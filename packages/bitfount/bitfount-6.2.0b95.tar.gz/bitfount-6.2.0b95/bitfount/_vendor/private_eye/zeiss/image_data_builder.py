import logging
from functools import partial
from typing import Callable, Dict, List, Optional, Tuple, cast

import numpy as np
from more_itertools import one, only
from PIL import Image
from ...private_eye import ImageData, ImagesData, ParserOptions, PhotoImageData, Size2D
from ...private_eye.consts import ImageModality
from ...private_eye.data import ImageOutputParams, ImageProcessingOptions, ImageSourceDataType
from ...private_eye.zeiss.common import ds_require
from pydicom import Dataset, FileDataset
from pydicom._storage_sopclass_uids import (
    EncapsulatedPDFStorage,
    MultiFrameTrueColorSecondaryCaptureImageStorage,
    OphthalmicPhotography8BitImageStorage,
    OphthalmicTomographyImageStorage,
    OphthalmicVisualFieldStaticPerimetryMeasurementsStorage,
    RawDataStorage,
)
from pydicom.uid import JPEG2000, UID

logger = logging.getLogger(__name__)


def _opthalmic_photography_8_bit(ds: Dataset, options: ParserOptions) -> ImageData:
    ds_require(ds, "PixelRepresentation", 0)  # Unsigned integer
    ds_require(ds, "BitsAllocated", 8)
    ds_require(ds, "BitsStored", 8)
    ds_require(ds, "HighBit", 7)

    def _extract_fixation_points_protocol_name() -> Optional[str]:
        def is_protocol_name(acquisition_context_elem: Dataset) -> bool:
            concept_name_code_seq = getattr(acquisition_context_elem, "ConceptNameCodeSequence")
            return cast(bool, concept_name_code_seq and one(concept_name_code_seq).CodeValue == "Protocol Name")

        if hasattr(ds, "AcquisitionContextSequence"):
            protocol_name_element = only(filter(is_protocol_name, ds.AcquisitionContextSequence), default=None)
            if protocol_name_element:
                return cast(str, one(protocol_name_element.ConceptCodeSequence).CodeValue)

        return None

    if ds.file_meta.TransferSyntaxUID == JPEG2000:
        # This would normally require GDCM, but we can make do with Pillow if we
        # bodge it.  If we ever want to use these images then we should compare the GDCM
        # and pillow outputs to check if this is acceptable.
        # https://pydicom.github.io/pydicom/stable/image_data_handlers.html
        # e.g. \\mehforum\DICO-Store1\2015\10\12\1.2.276.0.75.2.2.42.50123534057.20151012145518101.6104578630.1.dcm
        # which is a "Maculuar Cube Scan" which produces a single grayscale jpeg2000 image.
        logger.warning(
            "Unable to properly parse JPEG2000 images.  "
            "Forcing Pillow to parse anyway, this may give strange results!"
        )
        from pydicom.pixel_data_handlers.pillow_handler import PillowSupportedTransferSyntaxes

        PillowSupportedTransferSyntaxes.append(JPEG2000)

    height = ds.Rows
    width = ds.Columns

    if int(ds.NumberOfFrames) > 1:
        logger.warning("Unable to parse Zeiss images with NumberOfFrames>1")
        # TODO RIPF-239
        # e.g. \\mehforum\DICO-Store1\2019\1\11\1.2.276.0.75.2.2.30.2.3.190111094038933.50126565286.1000005.dcm
        # Image above was taken with a "Humphrey Field Analyzer 3"
        # numpy becomes unhappy when trying to read out the pixel data.
        # In this image, array arrives with size 26760000 which is 3 times too big - should be (223,200,200).

        image_data = ImageData(
            modality=ImageModality.UNKNOWN,
            group_id=None,
            size=None,
            dimensions_mm=None,
            resolutions_mm=None,
            source_id=str(ds.SOPInstanceUID),
            contents=[],
            field_of_view=None,
        )
    else:
        ds_require(ds, "NumberOfFrames", 1)

        if options.skip_image_data:
            image = None
            image_output_params: List[ImageOutputParams] = [
                ImageOutputParams(
                    image_processing_options=image_processing_option, image_mode=None, image_transform_functions=[]
                )
                for image_processing_option in options.image_processing_options
            ]
            image_mode = None
        else:
            image, transform, image_mode = _get_image(ds)
            base_transforms = [transform] if transform else []

            def _should_censor_annotations(ds: Dataset, processing_option: ImageProcessingOptions) -> bool:
                return ds.BurnedInAnnotation == "YES" and not processing_option.zeiss_no_censor_annotations

            image_output_params = [
                ImageOutputParams(
                    image_processing_options=image_processing_option,
                    image_mode=image_mode,
                    image_transform_functions=base_transforms
                    + ([_censor_date] if _should_censor_annotations(ds, image_processing_option) else []),
                )
                for image_processing_option in options.image_processing_options
            ]

        modality = _get_image_modality(ds)

        image_data = ImageData(
            modality=modality,
            group_id=None,
            size=Size2D(width, height),
            # TODO RIPF-239 Look for this
            dimensions_mm=None,
            resolutions_mm=None,
            contents=[
                PhotoImageData(
                    colour_depth=ds.BitsAllocated,
                    image=image,
                    capture_datetime=None,
                    image_output_params=image_output_params,
                    extras={
                        "file_transfer_syntax": ds.file_meta.TransferSyntaxUID,
                        "photometric_interpretation": ds.PhotometricInterpretation,
                        "pixel_representation": ds.PixelRepresentation,
                        "samples_per_pixel": ds.SamplesPerPixel,
                    },
                    image_byte_format=ImageSourceDataType.DICOM,
                    width=width,
                    height=height,
                )
            ],
            source_id=str(ds.SOPInstanceUID),
            extras={"fixation_points_protocol_name": _extract_fixation_points_protocol_name()},
            field_of_view=None,
        )

    return image_data


def _convert_to_rgb(pixel_data: np.ndarray, photometric_interpretation: str) -> np.ndarray:
    if photometric_interpretation == "RGB":
        return pixel_data
    if photometric_interpretation in ("YBR_FULL", "YBR_FULL_422"):
        # Convert to a PIL image to use PIL's efficient C implementation of the colour space conversion
        # The naive implementation in pydicom eats RAM for high resolution images
        pil_image = Image.fromarray(pixel_data, mode="YCbCr")
        return np.array(pil_image.convert("RGB"))
    raise ValueError(f"Conversion from {photometric_interpretation} to RGB is not supported")


def _get_image(ds: Dataset) -> Tuple[bytes, Optional[Callable], str]:
    samples_per_pixel = ds.SamplesPerPixel
    photometric_interpretation = ds.PhotometricInterpretation

    if samples_per_pixel == 3:
        convert = partial(_convert_to_rgb, photometric_interpretation=photometric_interpretation)
        return ds.PixelData, convert, "RGB"

    if samples_per_pixel == 1:
        if photometric_interpretation == "MONOCHROME1":
            # Greyscale image where the minimum value is treated as white
            # To parse this, we invert the image
            logger.warning("Verify the result to ensure we are treating MONOCHROME1 correctly.")

            def _convert(image_arr: np.ndarray) -> np.ndarray:
                return cast(np.ndarray, 255 - image_arr)

            return ds.PixelData, _convert, "L"
        if photometric_interpretation == "MONOCHROME2":
            # Greyscale image where the minimum value is treated as black
            return ds.PixelData, None, "L"
        if photometric_interpretation == "PALETTE COLOR":
            raise NotImplementedError("Palette colour interpretation not yet supported")
        raise ValueError(
            f"Invalid photometric interpretation for images with sample size 1: {photometric_interpretation}"
        )
    raise ValueError(f"Unable to handle SamplesPerPixel={ds.SamplesPerPixel}")


def _get_image_modality(ds: Dataset) -> ImageModality:
    samples_per_pixel = ds.SamplesPerPixel
    if samples_per_pixel == 3:
        return ImageModality.COLOUR_PHOTO
    if samples_per_pixel == 1:
        # TODO RIPF-1575: Replace this with a proper value
        return ImageModality.UNKNOWN
    raise ValueError(f"Unable to handle SamplesPerPixel={ds.SamplesPerPixel}")


def _opthalmic_tomography(ds: Dataset, options: ParserOptions) -> ImageData:
    ds_require(ds, "Modality", "OPT")

    # TODO RIPF-1575 Try extracting this, don't forget the burned in annotation
    return ImageData(
        modality=ImageModality.OCT,
        group_id=None,
        size=None,
        dimensions_mm=None,
        resolutions_mm=None,
        contents=[],
        source_id=str(ds.SOPInstanceUID),
        field_of_view=None,
    )


def _encapsulated_pdf_storage(ds: Dataset, options: ParserOptions) -> ImageData:
    # The PDF is stored at tag 0x00420011 and should be straightforward to extract should we ever need it.
    return ImageData(
        modality=ImageModality.ENCAPSULATED_PDF,
        group_id=None,
        size=None,
        dimensions_mm=None,
        resolutions_mm=None,
        source_id=str(ds.SOPInstanceUID),
        contents=[],
        field_of_view=None,
    )


def _raw_data_storage(ds: FileDataset, options: ParserOptions) -> Optional[ImageData]:
    # If this is a VF file then the raw data contains no images - instead it's the raw output from the HFA machine
    if ds.get("Modality") == "OPV":
        return None

    # This type seems to be used by Zeiss for their own obfuscated raw data - in Zeiss Forum Viewer the datatype appears
    # as RAW and it is clearly obfuscated.
    #
    # Other people have attempted to parse this and failed:
    # https://www.reddit.com/r/dicom/comments/46elm7/can_a_company_claim_it_is_dicom_compatible_but/
    #
    # If you XOR every 7th byte of one of the binary data blobs then exactly one JPEG 2000 header will appear partway
    # through the file.  At the end of the every file is a the JPEG 2000 end of file marker.  This suggests to me that
    # the JPEG file has been rearranged somehow, but I could not determine how.
    # https://github.com/plroit/Skyreach/wiki/Introduction-to-JPEG2000-Structure-and-Layout
    # https://www.ece.uvic.ca/~frodo/publications/jpeg2000.pdf

    return ImageData(
        modality=ImageModality.UNKNOWN,
        source_id=str(ds.SOPInstanceUID),
        contents=[],
        group_id=None,
        size=None,
        dimensions_mm=None,
        resolutions_mm=None,
        field_of_view=None,
    )


def _multiframe_true_colour_secondary_capture_image_storage(ds: Dataset, options: ParserOptions) -> ImageData:
    # From the spec:
    # The Multi-frame True Color Secondary Capture (SC) Image Information Object Definition (IOD) specifies True
    # Color images that are converted from a non-DICOM format to a modality independent DICOM format.
    # This IOD is typically used for screen captured or synthetic images where true color is used, but may also be
    # appropriate for scanned color documents.
    #
    # Zeiss seems to only use this for Tomography.
    ds_require(ds, "Modality", "OPT")
    height = ds.Rows
    width = ds.Columns

    image = ds.PixelData if options.skip_image_data else None

    if ds.BurnedInAnnotation == "YES":
        logger.warning("Image has burned-in date annotation")

    return ImageData(
        modality=ImageModality.OCT,
        group_id=None,
        size=Size2D(width, height),
        dimensions_mm=None,
        resolutions_mm=None,
        contents=[
            PhotoImageData(
                colour_depth=ds.BitsAllocated,
                image=image,
                capture_datetime=None,
                image_output_params=[
                    ImageOutputParams(
                        image_processing_options=image_processing_option, image_mode="L", image_transform_functions=[]
                    )
                    for image_processing_option in options.image_processing_options
                ],
                extras={
                    "file_transfer_syntax": ds.file_meta.TransferSyntaxUID,
                    "photometric_interpretation": ds.PhotometricInterpretation,
                    "pixel_representation": ds.PixelRepresentation,
                    "samples_per_pixel": ds.SamplesPerPixel,
                },
                image_byte_format=ImageSourceDataType.DICOM,
                width=width,
                height=height,
            )
        ],
        source_id=str(ds.SOPInstanceUID),
        field_of_view=None,
    )


def _unknown(ds: Dataset, options: ParserOptions) -> ImageData:
    logger.warning("Unknown SOPClassUID: %s", ds.SOPClassUID)
    return ImageData(
        modality=ImageModality.UNKNOWN,
        source_id=str(ds.SOPInstanceUID),
        contents=[],
        group_id=None,
        size=None,
        dimensions_mm=None,
        resolutions_mm=None,
        field_of_view=None,
    )


_image_metadata_builders: Dict[UID, Optional[Callable[[FileDataset, ParserOptions], Optional[ImageData]]]] = {
    OphthalmicPhotography8BitImageStorage: _opthalmic_photography_8_bit,
    OphthalmicTomographyImageStorage: _opthalmic_tomography,
    RawDataStorage: _raw_data_storage,
    EncapsulatedPDFStorage: _encapsulated_pdf_storage,
    MultiFrameTrueColorSecondaryCaptureImageStorage: _multiframe_true_colour_secondary_capture_image_storage,
    OphthalmicVisualFieldStaticPerimetryMeasurementsStorage: None,
}


def build_images_metadata(ds: FileDataset, options: ParserOptions) -> ImagesData:
    ds_require(ds.file_meta, "MediaStorageSOPClassUID", ds.SOPClassUID)

    try:
        builder = _image_metadata_builders[ds.SOPClassUID]
    except KeyError:
        builder = _unknown

    if not builder:
        return ImagesData(images=[])

    image_data = builder(ds, options)

    if not image_data:
        return ImagesData(images=[])

    # TODO RIPF-239 Reduce the amount of data put into extras once we've worked out a good classification.
    image_data.extras["SOPClassUID"] = ds.SOPClassUID
    image_data.extras["ImageType"] = [str(elem) for elem in ds.get("ImageType", [])]
    image_data.extras["ProtocolName"] = ds.get("ProtocolName")
    image_data.extras["SeriesDescription"] = ds.get("SeriesDescription")
    image_data.extras["PositionReferenceIndicator"] = ds.get("PositionReferenceIndicator")

    return ImagesData(images=[image_data])


def _censor_date(image: np.ndarray) -> np.ndarray:
    logger.debug("Removing burned in annotation")
    # Some images have a date added directly to the bottom left of the image. Anonymisation requires we remove this.
    censor_width = 250
    censor_height = 100
    censor_block = np.zeros(censor_width * censor_height * 3).reshape(censor_height, censor_width, 3)
    height = image.shape[0]
    image[height - censor_height : height, 0:censor_width] = censor_block

    return image
