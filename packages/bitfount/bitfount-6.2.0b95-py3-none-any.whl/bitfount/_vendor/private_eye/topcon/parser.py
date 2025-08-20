import logging
from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    no_type_check,
)

import attr
import numpy as np
from ...private_eye import ParserOptions
from ...private_eye.consts import Fixation, ImageModality, InputFileHandle, SectionName
from ...private_eye.external.external_pb2 import ExternalData
from ...private_eye.topcon.utils.location_calculator import DimensionsCalculator
from ...private_eye.utils.maths import distance
from ...private_eye.utils.optional import get_attr_if_present

from ..common.image_parser import SingleFileImageParser
from ..data import (
    BScanImageData,
    BscanLocation,
    Circle,
    ContourData,
    ContourLine,
    DebugData,
    ExamData,
    ImageContent,
    ImageData,
    ImageOutputParams,
    ImagesData,
    ImageSourceDataType,
    Line,
    ParserResults,
    PatientData,
    PhotoImageData,
    SeriesData,
    SeriesResult,
    Size2D,
    Size3D,
    TImageData,
)
from ..exceptions import ImageParseException, StreamLengthError
from ..utils.binary import peek
from .section.alignment_info import AlignmentInfoSection
from .section.base import FdaSection
from .section.binary import BinarySection
from .section.bounding_box import RegistrationInfoSection, ScanRangeSection
from .section.capture_info import CaptureInfoSection
from .section.contour_info import ContourInfoSection
from .section.cornea import ResultCorneaCurve, ResultCorneaThickness
from .section.disc_segementation import DiscSegmentationSection
from .section.file_info import FileInfoSection
from .section.gla_littmann import GlaucomaLittmannSection
from .section.hardware_info import HardwareInfoSection
from .section.img_bscan import TOPCON_IMAGE_TRANSFORM, BScanImageSection, BScanParamSection
from .section.img_fundus import FundusImageSection, FundusParamSection
from .section.img_ir import InfraredImageSection, InfraredParamSection
from .section.img_mot_comp import ImgMotCompSection
from .section.img_projection import ImgProjectionSection
from .section.param_angiography import ParamAngiographySection
from .section.patient_info import PatientInfo03Section, PatientInfoSection
from .section.quality import FastQ2Section
from .section.ref_img_scan_section import RefImageScanSection
from .section.thumbnail import ThumbnailSection
from .section.unknown import UnknownSection
from .topcon_stream_wrapper import TopconStreamWrapper

logger = logging.getLogger(__name__)

# Note: Other FDA formats exist. This is fine for now though
FDA_HEADER = b"FOCT"

_section_map: Dict[str, Type[FdaSection]] = {
    "@FDA_FILE_INFO": FileInfoSection,
    "@HW_INFO_03": HardwareInfoSection,
    "@PATIENT_INFO_02": PatientInfoSection,
    "@PATIENT_INFO_03": PatientInfo03Section,
    "@CAPTURE_INFO_02": CaptureInfoSection,
    "@IMG_JPEG": BScanImageSection,
    "@PARAM_SCAN_04": BScanParamSection,
    "@IMG_TRC_02": InfraredImageSection,
    "@PARAM_TRC_02": InfraredParamSection,
    "@IMG_FUNDUS": FundusImageSection,
    "@PARAM_OBS_02": FundusParamSection,
    "@IMG_MOT_COMP_03": ImgMotCompSection,
    "@IMG_PROJECTION": ImgProjectionSection,
    "@REGIST_INFO": RegistrationInfoSection,
    "@EFFECTIVE_SCAN_RANGE": ScanRangeSection,
    "@THUMBNAIL": ThumbnailSection,
    "@CONTOUR_INFO": ContourInfoSection,
    "@CONTOUR_MASK_INFO": BinarySection,
    "@GLA_LITTMANN_01": GlaucomaLittmannSection,
    "@FAST_Q2_INFO": FastQ2Section,
    "@REF_IMG_SCAN": RefImageScanSection,
    "@ALIGN_INFO": AlignmentInfoSection,
    "@FDA_DISC_SEGMENTATION": DiscSegmentationSection,
    "@PARAM_ANGIOGRAPHY": ParamAngiographySection,
    "@RESULT_CORNEA_CURVE": ResultCorneaCurve,
    "@RESULT_CORNEA_THICKNESS": ResultCorneaThickness,
}


def _get_section_class(section_id: str) -> Type[FdaSection]:
    try:
        return _section_map[section_id]
    except KeyError:
        return UnknownSection


TFdaSection = TypeVar("TFdaSection", bound=FdaSection)


class _FdaSectionList(list):
    def get_sections(self, section_cls: Type[TFdaSection]) -> List[TFdaSection]:
        return list(filter(lambda s: isinstance(s, (section_cls,)), self))

    def get_section(self, section_cls: Type[TFdaSection]) -> TFdaSection:
        try:
            return self.get_sections(section_cls)[0]
        except IndexError as error:
            raise KeyError(f"Missing segment: {section_cls.__name__}") from error

    def get_optional_section(self, section_cls: Type[TFdaSection]) -> Optional[TFdaSection]:
        try:
            return self.get_sections(section_cls)[0]
        except IndexError:
            return None


class FdaSectionParser(Generic[TImageData], ABC):
    _required_sections_map: Dict[SectionName, List[Type[FdaSection]]] = {}
    _class_map: Dict[SectionName, Type["FdaSectionParser"]] = {}

    # noinspection PyTypeChecker
    @no_type_check  # We need so many casts that it's not worth the type checking.
    def __init_subclass__(cls, *args: Any, **kwargs: Dict[str, Any]) -> None:
        # We don't want to add the abstract base class to _class_map and _required_sections_map
        if cls.__name__ == FdaSectionParser.__name__:
            return

        assert isinstance(cls.name, SectionName), (
            "FdaSectionParser names must be of type SectionName, " f"not {cls.name}"
        )
        assert isinstance(cls.required_sections, list), (
            "FdaSectionParser required_sections must be of type" f" list, not {cls.required_sections}"
        )

        FdaSectionParser._class_map[cls.name] = cls
        FdaSectionParser._required_sections_map[cls.name] = cls.required_sections

    def __init__(self, file: "TopconParser") -> None:
        self.file = file

    @property
    @abstractmethod
    def required_sections(self) -> Sequence[Type[FdaSection]]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def name(self) -> SectionName:
        raise NotImplementedError()

    @abstractmethod
    def parse(self, sections: _FdaSectionList) -> TImageData:
        raise NotImplementedError()

    @classmethod
    def get_required_section_types(cls, section_names: Iterable[SectionName]) -> Set[Type[FdaSection]]:
        ret: Set[Type[FdaSection]] = set()
        for name in section_names:
            required_types = cls._required_sections_map.get(name)
            if required_types:
                ret.update(required_types)
        return ret

    @classmethod
    def get_parser(cls, section_name: SectionName, file: "TopconParser") -> Optional["FdaSectionParser"]:
        clazz = cls._class_map.get(section_name)

        if not clazz:
            return None

        return clazz(file)


class PatientParser(FdaSectionParser[PatientData]):
    required_sections = [PatientInfoSection]
    name = SectionName.PATIENT

    def parse(self, sections: _FdaSectionList) -> PatientData:
        patient_section = sections.get_section(PatientInfoSection)
        return patient_section.to_patient_metadata()


class SeriesParser(FdaSectionParser[SeriesData]):
    required_sections = [CaptureInfoSection, BScanParamSection, BScanImageSection]
    name = SectionName.SERIES

    def parse(self, sections: _FdaSectionList) -> SeriesData:
        scan_section = sections.get_section(CaptureInfoSection)
        bscan_param_section = sections.get_optional_section(BScanParamSection)
        bscan_image_section = sections.get_optional_section(BScanImageSection)
        fixation = get_attr_if_present(bscan_param_section, "visual_fixation")

        return SeriesData(
            laterality=scan_section.eye,
            fixation=fixation,
            anterior=fixation == Fixation.EXTERNAL,
            protocol=get_attr_if_present(bscan_image_section, "scan_mode"),
            source_id=self.file.series_id,
        )


class ImagesParser(FdaSectionParser[ImagesData]):
    required_sections = [
        FundusImageSection,
        InfraredImageSection,
        RegistrationInfoSection,
        BScanImageSection,
        BScanParamSection,
        ContourInfoSection,
        FastQ2Section,
    ]
    name = SectionName.IMAGES

    def parse(self, sections: _FdaSectionList) -> ImagesData:

        fundus_section = sections.get_optional_section(FundusImageSection)
        infrared_section = sections.get_optional_section(InfraredImageSection)
        registration_info_section = sections.get_optional_section(RegistrationInfoSection)
        bscan_image_section = sections.get_optional_section(BScanImageSection)
        bscan_param_section = sections.get_optional_section(BScanParamSection)
        contours_sections = sections.get_sections(ContourInfoSection)
        quality_section = sections.get_optional_section(FastQ2Section)

        processing_flags = (
            {
                image_processing_option.identifier(): {
                    "topcon_processing_flags": {"clipping": not image_processing_option.topcon_no_clip_bscan}
                }
                for image_processing_option in bscan_image_section.options.image_processing_options
            }
            if bscan_image_section
            else {}
        )

        bscan_images: List[ImageData] = []
        bscan_dimensions: Optional[Size3D] = None
        bscan_resolutions: Optional[Size3D] = None
        first_fundus_bscan_location: Optional[BscanLocation] = None
        first_trc_bscan_location: Optional[BscanLocation] = None
        if bscan_image_section is not None:
            image_count = bscan_image_section.slice_count
            photo_locations: List[List[BscanLocation]] = []

            quality = quality_section.q_mean if quality_section else None
            bscan_sizing_info = getattr(bscan_param_section, "sizing_info", None)
            bscan_size = bscan_image_section.size

            calculator = DimensionsCalculator.get(bscan_image_section.scan_mode)
            if calculator:
                bscan_dimensions, bscan_resolutions = calculator.bscan_dimensions(
                    bscan_sizing_info, bscan_size, len(bscan_image_section.images)
                )
                if registration_info_section:
                    if fundus_section is not None:
                        fundus_locations = calculator.locations(
                            registration_info_section.fundus_shape, image_count, bscan_sizing_info
                        )
                        if fundus_locations:
                            first_fundus_bscan_location = fundus_locations[0]
                        photo_locations.append(fundus_locations)
                    if infrared_section is not None:
                        trc_locations = calculator.locations(
                            registration_info_section.trc_shape, image_count, bscan_sizing_info
                        )
                        if trc_locations:
                            first_trc_bscan_location = trc_locations[0]
                        photo_locations.append(
                            calculator.locations(registration_info_section.trc_shape, image_count, bscan_sizing_info)
                        )

            bscan_image_data: List[ImageContent] = list(
                BScanImageData(
                    quality=quality,
                    image=bscan_image,
                    photo_locations=[pl[index] for pl in photo_locations],
                    capture_datetime=None,
                    art_average=None,
                    image_transform_metadata={
                        image_processing_option.identifier(): TOPCON_IMAGE_TRANSFORM
                        for image_processing_option in bscan_image_section.options.image_processing_options
                    },
                    image_output_params=[
                        attr.evolve(
                            bscan_processing_option_data,
                            contour=ContourData(
                                bscan_index=index,
                                contour_layers=[
                                    ContourLine(layer_name=section.label, data=section.data[index])
                                    for section in contours_sections
                                ],
                            ),
                        )
                        for bscan_processing_option_data in bscan_image_section.image_output_params
                    ],
                    image_byte_format=ImageSourceDataType.JPEG2000,
                )
                for index, bscan_image in enumerate(bscan_image_section.images)
            )

            bscan_images.append(
                ImageData(
                    modality=ImageModality.OCT,
                    group_id=None,
                    size=bscan_size,
                    dimensions_mm=bscan_dimensions,
                    resolutions_mm=bscan_resolutions,
                    contents=bscan_image_data,
                    # In topcon, there is only one image of each type per series, so it's safe to use type as source ID
                    source_id="OCT",
                    # Topcon files seem to always have the image angle set to 0. It's probably actually 45 degrees as
                    # per the specification in this brochure -
                    # http://www.topconmedical.com/literature/3DOCT-2000_Series.pdf, but might vary between machines
                    field_of_view=None,
                    extras=processing_flags,
                )
            )

        photo_images: List[ImageData] = []
        if fundus_section is not None:
            photo_images.append(
                self._create_photo_image_data(
                    bscan_dimensions=bscan_dimensions,
                    bscan_location=first_fundus_bscan_location,
                    section=fundus_section,
                    image=fundus_section.image,
                    modality=ImageModality.COLOUR_PHOTO,
                    image_output_params=fundus_section.image_output_params,
                )
            )
        if infrared_section is not None:
            photo_images.append(
                self._create_photo_image_data(
                    bscan_dimensions=bscan_dimensions,
                    bscan_location=first_trc_bscan_location,
                    section=infrared_section,
                    image=infrared_section.images[-1],
                    modality=ImageModality.INFRARED_PHOTO,
                    image_output_params=infrared_section.image_output_params,
                )
            )

        return ImagesData(images=photo_images + bscan_images)

    def _create_photo_image_data(
        self,
        bscan_dimensions: Optional[Size3D],
        bscan_location: Optional[BscanLocation],
        section: Union[FundusImageSection, InfraredImageSection],
        image: Optional[bytes],
        modality: ImageModality,
        image_output_params: List[ImageOutputParams],
    ) -> ImageData:
        photo_dimensions, photo_resolutions = self._calculate_dimensions(
            bscan_dimensions=bscan_dimensions, bscan_location=bscan_location, image_section=section
        )

        photo_image_data = PhotoImageData(
            colour_depth=section.colour_depth,
            image=image,
            capture_datetime=None,
            image_output_params=image_output_params,
            image_byte_format=ImageSourceDataType.JPEG2000,
        )
        return ImageData(
            modality=modality,
            group_id=None,
            size=section.size,
            dimensions_mm=photo_dimensions,
            resolutions_mm=photo_resolutions,
            contents=[photo_image_data],
            source_id=modality.code,
            # Topcon files seem to always have the image angle set to 0. It's probably actually 45 degrees as
            # per the specification in this brochure -
            # http://www.topconmedical.com/literature/3DOCT-2000_Series.pdf, but might vary between machines
            field_of_view=None,
        )

    def _calculate_dimensions(
        self,
        bscan_dimensions: Optional[Size3D],
        bscan_location: Optional[BscanLocation],
        image_section: Union[FundusImageSection, InfraredImageSection],
    ) -> Tuple[Optional[Size2D], Optional[Size2D]]:
        photo_dimensions: Optional[Size2D] = None
        photo_resolutions: Optional[Size2D] = None
        if bscan_dimensions and bscan_location:
            photo_dimensions, photo_resolutions = self._calculate_fundus_dimension_and_resolution(
                bscan_dimensions, bscan_location, image_section.size
            )
        return photo_dimensions, photo_resolutions

    @staticmethod
    def _calculate_fundus_dimension_and_resolution(
        bscan_dimensions: Size3D, bscan_location: BscanLocation, image_size: Size2D
    ) -> Tuple[Size2D, Size2D]:
        """
        Topcon fundus images empirically have the same resolution in the x and y dimensions.
        We shall abuse this fact to work out the fundus dimensions using the b-scan X-resolution alone
        """
        if isinstance(bscan_location, Line):
            start = bscan_location.start
            end = bscan_location.end
            bscan_length_on_fundus = distance(start, end)
        elif isinstance(bscan_location, Circle):
            bscan_length_on_fundus = bscan_location.radius * 2 * np.pi
        else:
            raise ValueError(f"Unknown location type: {bscan_location.__class__}")

        resolution_x = bscan_dimensions.width / bscan_length_on_fundus if bscan_length_on_fundus != 0 else 0

        resolution = Size2D(width=resolution_x, height=resolution_x)
        dimension = Size2D(width=image_size.width * resolution.width, height=image_size.height * resolution.height)
        return dimension, resolution


class ExamParser(FdaSectionParser[ExamData]):
    required_sections = [HardwareInfoSection, CaptureInfoSection]
    name = SectionName.EXAM

    def parse(self, sections: _FdaSectionList) -> ExamData:
        hardware_section = sections.get_section(HardwareInfoSection)
        scan_section = sections.get_section(CaptureInfoSection)

        return ExamData(
            scan_datetime=scan_section.scan_datetime,
            manufacturer="Topcon",
            scanner_model=hardware_section.manufacturer_model,
            scanner_serial_number=hardware_section.serial_number,
            scanner_software_version=hardware_section.software_version,
            scanner_last_calibration_date=hardware_section.last_calibration_date,
            # We make the assumption that every exam has one series, and re-use the ID
            source_id=self.file.series_id,
        )


class DebugParser(FdaSectionParser[DebugData]):
    required_sections: List[Type[FdaSection]] = []
    name = SectionName.DEBUG

    def parse(self, sections: _FdaSectionList) -> DebugData:
        section_data = [s.debug_data() for s in sections]
        return DebugData(
            {
                "major_version": self.file.major_version,
                "minor_version": self.file.minor_version,
                "sections": section_data,
            }
        )


class TopconParser(SingleFileImageParser):
    def __init__(self, input_files: List[InputFileHandle], options: ParserOptions, external_data: ExternalData) -> None:
        super().__init__(input_files, options, external_data)
        self.fs = TopconStreamWrapper(self.input_file.handle, options)

        self.series_id = self._parse_series_id()
        self._verify_header()
        self._verify_fixation()
        self.major_version: int = self.fs.read_int()
        self.minor_version: int = self.fs.read_int()
        self._data_start: int = self.fs.tell()

    @classmethod
    def matches_file(cls, input_file: InputFileHandle, options: ParserOptions) -> bool:
        with peek(input_file.handle, len(FDA_HEADER)) as data:
            return data == FDA_HEADER

    def read_sections(self, *section_names: SectionName) -> ParserResults:
        fda_sections = self._parse_fda_sections(section_names)
        parsers = [FdaSectionParser.get_parser(name, self) for name in section_names]

        parser_input = {
            name.value: parser.parse(fda_sections) if parser else None for name, parser in zip(section_names, parsers)
        }
        parser_result = SeriesResult(**parser_input)
        return ParserResults([parser_result])

    def _parse_series_id(self) -> str:
        """
        Use the original file name as a substitute for the series/exam ID
        """
        return self.input_file.original_filepath.stem

    def _parse_fda_sections(self, section_names: Tuple[SectionName, ...]) -> _FdaSectionList:
        sections = _FdaSectionList()
        remaining_section_types = FdaSectionParser.get_required_section_types(section_names)
        if not remaining_section_types:
            return sections

        def _parse_section_type(type_to_parse: Type[FdaSection]) -> bool:
            if self.options.full_parse:
                return True
            # Can't do a simply 'type in remaining_types' as we can have subclasses, e.g. patient info
            for remaining_type in remaining_section_types:
                if issubclass(type_to_parse, remaining_type):
                    return True
            return False

        def _remove_section_type(type_to_remove: Type[FdaSection]) -> None:
            # Again, .remove() doesn't work as we have subclasses
            for remaining_type in list(remaining_section_types):
                if issubclass(type_to_remove, remaining_type):
                    remaining_section_types.remove(remaining_type)
                    return
            raise KeyError()

        self.fs.seek(self._data_start)
        section_header_length = self.fs.read_byte()
        while section_header_length != 0:
            section_id = self.fs.read_ascii(section_header_length)
            section_length = self.fs.read_int()
            section_cls = _get_section_class(section_id)

            if not _parse_section_type(section_cls):
                self.fs.skip(section_length)
            else:
                if not section_cls.MULTIPLE and not self.options.full_parse:
                    _remove_section_type(section_cls)
                section_stream = self.fs.get_substream(section_length)
                section = section_cls(section_stream, section_id, self.options)

                section.load()
                sections.append(section)

                if not self.options.full_parse and len(remaining_section_types) == 0:
                    # We've loaded all the data we want, so bail out
                    break

                remaining = section_length - section_stream.tell()
                if remaining > 0:
                    self.fs.seek(remaining, 1)
                    logger.debug("Skipping %d bytes to end of section %d", remaining, section_id)

            # Read next section length if available. A value of 0 indicates end of file.
            try:
                section_header_length = self.fs.read_byte()
            except StreamLengthError:
                break

        return sections

    def _verify_fixation(self) -> None:
        mode = self.fs.read_ascii(3)
        if mode not in ("FDA", "FAA"):
            raise ImageParseException(f"Unknown file fixation option: {mode}")

    def _verify_header(self) -> None:
        given = self.fs.read(len(FDA_HEADER))
        if given != FDA_HEADER:
            raise ImageParseException(f"Given file is not a Topcon file (saw header {given!r})")
