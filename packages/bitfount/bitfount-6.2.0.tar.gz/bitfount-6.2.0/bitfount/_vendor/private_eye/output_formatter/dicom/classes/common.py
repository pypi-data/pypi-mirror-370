import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type

from PIL import Image
from .....private_eye.data import (
    BaseImageDataBytes,
    ImageContent,
    ImageData,
    ImageProcessingOptions,
    ImageSourceDataType,
    SeriesResult,
)
from .....private_eye.output_formatter.convert_to_pil_image import apply_transforms, decompress_image
from .....private_eye.output_formatter.dicom.dicom_helpers import generate_uid_from_source, static_uid
from .....private_eye.output_formatter.dicom.modules.common import DicomData, DicomModule
from .....private_eye.utils.image import get_pixel_depth
from .....private_eye.version import version
from pydicom import DataElement, Dataset, FileDataset
from pydicom.datadict import keyword_for_tag
from pydicom.dataset import FileMetaDataset
from pydicom.encaps import encapsulate
from pydicom.uid import JPEG2000, UID, JPEG2000Lossless, JPEGBaseline8Bit

logger = logging.getLogger(__name__)


class DicomClass(ABC):
    IMPLEMENTATION_CLASS = static_uid("3.1")

    MODULES: List[Type[DicomModule]] = NotImplemented

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.MODULES is NotImplemented or not cls.MODULES:
            raise NotImplementedError("MODULES must have at least one entry")

    def __init__(self, pepper: Optional[str], is_anonymised: bool, uid_entropy: Optional[List[Any]] = None):
        self.pepper = pepper
        self.is_anonymised = is_anonymised
        self.uid_entropy = uid_entropy or []
        self._module_instances = [module(self) for module in self.MODULES]

    def write_to_output(
        self, output_path_prefix: Path, parser_result: SeriesResult, image_data: ImageData
    ) -> Dict[ImageProcessingOptions, Path]:
        return {
            image_processing_options: self._process_single_image(output_path_prefix, image_data, dicom_input)
            for image_processing_options, dicom_input in self._generate_dicom_data(parser_result, image_data).items()
        }

    def _process_single_image(self, output_path_prefix: Path, image_data: ImageData, dicom_input: DicomData):
        logger.debug("Processing single image %s", image_data)
        output_path = output_path_prefix.with_name(
            f"{dicom_input.image_processing_options}{output_path_prefix.name}.dcm"
        )
        self._write_data_to_path(dicom_input, output_path)
        return output_path

    def generate_image_uid(self, parser_result: SeriesResult, image: ImageData) -> UID:
        """
        Take a list of values to provide a deterministic yet sufficiently unique UID.
        The list can be supplemented by externally-provided values, for example if Librarian needs to use 'site'
        as a distinguishing factor.

        Note: As the generation is done using a sha512 hash,, there is no way to reverse-engineer
        the underlying values. Hence, this is sufficiently de-identified.
        """
        source = self.uid_entropy + [image.source_id, image.modality]
        if parser_result.patient:
            source += [parser_result.patient.source_id, parser_result.patient.patient_key]
        if parser_result.exam:
            source += [parser_result.exam.source_id, parser_result.exam.scan_datetime, parser_result.exam]
        if parser_result.series:
            source += [parser_result.series.source_id, parser_result.series.protocol]
        return generate_uid_from_source(self.pepper, source)

    @abstractmethod
    def get_sop_class(self, data: DicomData) -> UID:
        raise NotImplementedError()

    def _write_data_to_path(self, data: DicomData, path: Path) -> None:
        datasets = []

        # Instead of dumping all attributes into a single dataset, have each module populate its own dataset
        # which we then merge into the final output. This way it shouldn't matter what order the modules are processed,
        # as we won't accidentally overwrite an explicit value with an empty value.
        # We tidy up the cross-module spec requirements at the end.
        for module in self._module_instances:
            module_ds = Dataset()
            module.populate_dataset(module_ds, data)
            datasets.append(module_ds)

        ds = self._create_output_dataset(path, datasets, data.uid)
        ds.fix_meta_info(enforce_standard=True)

        # Overwrite the pydicom-generated file meta UIDs
        ds.file_meta.ImplementationClassUID = self.IMPLEMENTATION_CLASS
        ds.file_meta.ImplementationVersionName = f"MEH_PE_{version}"
        ds.save_as(path, write_like_original=False)

    def _create_output_dataset(self, path: Path, datasets: List[Dataset], uid: UID) -> FileDataset:
        # In order for our private data elements to be typed we need to use explicit_VR.
        # The DICOM standard recommends defaulting to implicit VR.
        # Using a FileDataset will result in pydicom overiding any transfer syntax that uses Explicit VR
        # unless implicit_VR is set to False within the dataset.
        # For ease make all our DICOM use explicit_VR.
        output = FileDataset(path, {}, file_meta=FileMetaDataset(), is_implicit_VR=False)
        output.file_meta.TransferSyntaxUID = uid[0]
        for ds in datasets:
            for tag, value in ds.items():
                # Overwrite any existing blank values, don't overwrite otherwise
                if tag not in output or not output[tag].value:
                    output[tag] = value

        self._fix_attribute_conflicts(output)
        return output

    @staticmethod
    def _fix_attribute_conflicts(ds: Dataset):
        """
        Recursively walk over the dataset and remove attributes which conflict with other attributes
        according to the spec. This will find attributes within sub-datasets, sequences etc.
        """
        elements_to_remove = set()

        def _fixer(_: Dataset, data_element: DataElement) -> None:
            tag_name = keyword_for_tag(data_element.tag)
            # Spec for Laterality (0020, 0060):
            # Required if the body part examined is a paired structure and Image Laterality (0020,0062) or
            # Frame Laterality (0020,9072) or Measurement Laterality (0024,0113) are not present.
            if tag_name in ("FrameLaterality", "ImageLaterality", "MeasurementLaterality"):
                elements_to_remove.add("Laterality")

            # Spec for Pixel Aspect Ratio (0028,0034)
            # Required if the aspect ratio values do not have a ratio of 1:1 and the physical pixel spacing is not
            # specified by Pixel Spacing (0028,0030), or Imager Pixel Spacing (0018,1164) or Nominal Scanned Pixel
            # Spacing (0018,2010), either for the entire Image or per-frame in a Functional Group Macro
            if tag_name in ("ImagerPixelSpacing", "PixelSpacing", "NominalScannedPixelSpacing"):
                elements_to_remove.add("PixelAspectRatio")

        ds.walk(_fixer, recursive=True)

        for element in elements_to_remove:
            try:
                delattr(ds, element)
            except AttributeError:
                # This is fine, just means the conflicting attribute isn't there in the first place
                pass

    def _generate_dicom_data(
        self, parser_result: SeriesResult, image_data: ImageData
    ) -> Dict[ImageProcessingOptions, DicomData]:
        return {
            image_processing_options: DicomData(
                image_processing_options.identifier(), parser_result, image_data, bits_stored, pixel_data, uid
            )
            for image_processing_options, (bits_stored, pixel_data, uid) in self._get_bits_stored_and_pixel_data(
                image_data
            ).items()
        }

    def _get_bits_stored_and_pixel_data(
        self, image_data: ImageData
    ) -> Dict[ImageProcessingOptions, Tuple[int, bytes, UID]]:

        images = image_data.contents
        is_colour = image_data.is_colour
        depth_and_pixel_data = [self._get_depth_and_pixels_for_single_image(image, is_colour) for image in images]
        image_processing_options = depth_and_pixel_data[0].keys()
        output = {}

        for image_processing_option in image_processing_options:
            all_depths = [depth_and_pixels[image_processing_option][0] for depth_and_pixels in depth_and_pixel_data]
            output[image_processing_option] = (
                all_depths[0] // 3 if is_colour else all_depths[0],
                encapsulate(
                    [depth_and_pixels[image_processing_option][1] for depth_and_pixels in depth_and_pixel_data]
                ),
                [depth_and_pixels[image_processing_option][2] for depth_and_pixels in depth_and_pixel_data],
            )

        return output

    @staticmethod
    def _get_depth_and_pixels_for_single_image(
        image: ImageContent, is_colour: bool
    ) -> Dict[ImageProcessingOptions, Tuple[int, bytes, UID]]:
        if not isinstance(image, BaseImageDataBytes):
            raise ValueError(f"Unsupported image type: {type(image)}")

        images = {}
        transform_hash_to_image_processing_option = {}
        image_array = None

        for image_output_params in image.image_output_params:
            # We want some way to use transforms as the key to a dictionary based on the content.
            # Caching transforms will produce a reasonable improvement in processing speed.
            # Often files that will be parsed with multiple processing options contain multiple images.
            # Only one of these images will actually result in a different output, the others will be identical.
            # As such caching means we only process these images once rather than multiple times.
            transform_hash = hash(tuple(image_output_params.image_transform_functions))
            processing_options = image_output_params.image_processing_options

            if transform_hash in transform_hash_to_image_processing_option:
                images[processing_options] = images[transform_hash_to_image_processing_option[transform_hash]]

            elif (
                image_output_params.image_transform_functions == []
                and image_output_params.image_mode
                and (
                    image.image_byte_format == ImageSourceDataType.JPEG2000
                    or image.image_byte_format == ImageSourceDataType.JPEG
                )
            ):
                # Since we are unsure if the TOPCON JPEG2000 is lossless it makes sense to use the less strict
                # JPEG2000 UID. When we can be certain an image is lossless we will use the more strict UID.
                dicom_format = JPEGBaseline8Bit if image.image_byte_format == ImageSourceDataType.JPEG else JPEG2000
                images[processing_options] = (
                    get_pixel_depth(image_output_params.image_mode),
                    image.image,
                    dicom_format,
                )
                transform_hash_to_image_processing_option[transform_hash] = processing_options

            else:
                if image_array is None:
                    image_array = decompress_image(image)

                pil_image = Image.fromarray(
                    apply_transforms(image_array, image_output_params.image_transform_functions)
                )

                if pil_image.mode == "RGB" and not is_colour:
                    pil_image = pil_image.convert("L")
                # Convert to a standard interpretation. This should match PhotometricInterpretation
                elif pil_image.mode != "RGB" and is_colour:
                    pil_image = pil_image.convert("RGB")

                with io.BytesIO() as output:
                    pil_image.save(output, format="JPEG2000", irreversible=False)
                    output_bytes = output.getvalue()

                # PIL is always going to be more accurate than our prediction.
                # If we have PIL's image mode we will use it.
                images[processing_options] = (get_pixel_depth(pil_image.mode), output_bytes, JPEG2000Lossless)
                transform_hash_to_image_processing_option[transform_hash] = processing_options

        return images
