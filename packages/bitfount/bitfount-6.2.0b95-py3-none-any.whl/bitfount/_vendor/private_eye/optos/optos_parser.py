import imghdr
import logging
from abc import ABC, abstractmethod
from enum import IntEnum, IntFlag
from functools import partial
from typing import Callable, Dict, Generic, List, Optional, Tuple, Type, cast, no_type_check

import attr
import numpy as np
from google.protobuf.json_format import MessageToDict
from ...private_eye import ParserOptions
from ...private_eye.common.file_stream_wrapper import FileStreamWrapper
from ...private_eye.common.image_parser import SingleFileImageParser
from ...private_eye.consts import ImageModality, InputFileHandle, Laterality, SectionName
from ...private_eye.data import (
    AbstractData,
    DebugData,
    ExamData,
    ImageData,
    ImageOutputParams,
    ImagesData,
    ImageSourceDataType,
    ParserResults,
    PatientData,
    PhotoImageData,
    SeriesData,
    SeriesResult,
    Size2D,
    TImageData,
)
from ...private_eye.exceptions import ImageParseException
from ...private_eye.external.external_pb2 import ExternalData
from ...private_eye.optos.get_tiff_image_size import get_tiff_dimensions
from ...private_eye.utils.binary import get_subint

logger = logging.getLogger(__name__)


class OptosEyeSteering(IntEnum):
    NONE = 0
    STEER_0 = 1
    STEER_45 = 2
    STEER_90 = 3
    STEER_135 = 4
    STEER_180 = 5
    STEER_225 = 6
    STEER_270 = 7
    STEER_315 = 8


class OptosImageContent(IntFlag):
    STANDARD = 0
    RED_PLANE = 1
    GREEN_PLANE = 2
    BLUE_PLANE = 4
    IR_PLANE = 8


@attr.s(auto_attribs=True, frozen=True)
class OptosImageType:
    base_type: int
    image_content: OptosImageContent
    is_fa_sequence: bool
    eye_steering: OptosEyeSteering

    @classmethod
    def from_int(cls, image_type: Optional[int]) -> "OptosImageType":
        if not image_type:
            raise ImageParseException("Image type not provided")
        base_type = get_subint(image_type, 0, 8)
        image_content_int = get_subint(image_type, 8, 4)
        is_fa_sequence = bool(get_subint(image_type, 12, 4))
        eye_steering_int = get_subint(image_type, 16, 4)

        try:
            image_content = OptosImageContent(image_content_int)
        except ValueError as e:
            raise ImageParseException(f"Unknown image content value: {image_content_int}") from e

        try:
            eye_steering = OptosEyeSteering(eye_steering_int)
        except ValueError as e:
            raise ImageParseException(f"Unknown image eye steering value: {eye_steering_int}") from e

        return OptosImageType(
            base_type=base_type,
            image_content=image_content,
            is_fa_sequence=is_fa_sequence,
            eye_steering=eye_steering,
        )

    @property
    def is_multicolour(self) -> bool:
        return self.base_type in (1, 2, 3, 8)

    @property
    def modality(self) -> ImageModality:
        if self.is_multicolour:
            raise NotImplementedError("Multicolour images are split into separate modalities")
        if self.base_type in (4, 6, 7):
            return ImageModality.FLUORESCEIN_ANGIOGRAPHY
        if self.base_type == 5:
            return ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY
        if self.base_type in (9, 10, 11, 12):
            return ImageModality.AUTOFLUORESCENCE_GREEN
        raise ImageParseException(f"Unknown image base type: {self.base_type}")

    @property
    def resolution(self) -> float:
        # Note: The image itself contains XResolution and YResolution tags.
        # However, these are set to a constant 150DPI, which is meaningless in our case

        # According to the Optos docs, These are all 'Zoom' types, which have a resolution of 0.0081mm/px
        # See RIPF-55 for more details
        if self.base_type in (3, 6, 10):
            return 0.0081
        if self.base_type in (7, 8):
            # There are no examples of these in the database, so cannot explicitly check now.
            logger.warning(
                "Image is of type %s, which is marked as 'Reduced' according to the spec. "
                "Please verify that the image resolution is correct",
                self.base_type,
            )
        return 0.0104


class OptosSectionParser(Generic[TImageData], ABC):
    def __init__(self, file: "OptosParser") -> None:
        self.file = file
        self.external_data = file.external_data.optos

    @abstractmethod
    def parse(self) -> Optional[TImageData]:
        raise NotImplementedError()


class OptosDebugDataParser(OptosSectionParser[DebugData]):
    def parse(self) -> DebugData:
        return DebugData(
            dict(
                image_type=attr.asdict(OptosImageType.from_int(self.external_data.image_type)),
                external_data=MessageToDict(self.external_data, preserving_proto_field_name=True),
            )
        )


class OptosPatientDataParser(OptosSectionParser[PatientData]):
    def parse(self) -> PatientData:
        first_name, last_name = self._parse_name()
        return PatientData(
            patient_key=self.external_data.patient_refcodes,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=self.external_data.patient_dob.ToDatetime().date(),
            gender=self.external_data.patient_gender,
            source_id=self.external_data.patient_id,
        )

    def _parse_name(self) -> Tuple[str, str]:
        name = self.external_data.patient_name
        if not name:
            raise ImageParseException("Patient name not provided")
        # Optos names are stored as  'Last^First^Middle^Title^'
        name_parts = name.split("^")
        last_name = name_parts[0]
        first_name = name_parts[1]
        middle_name = name_parts[2]

        # All Optos patients we have seen have at least a first and last name
        return f"{first_name} {middle_name}" if middle_name else first_name, last_name


class OptosExamDataParser(OptosSectionParser[ExamData]):
    def parse(self) -> ExamData:
        return ExamData(
            # Start time matches the capture date of first images, so use that.
            scan_datetime=self.external_data.session_start_time.ToDatetime(),
            manufacturer="Optos",
            # The initial assumption about all Optos models having the same name was incorrect, so leave this as blank
            scanner_model=None,
            scanner_serial_number=self.external_data.session_instrument_id,
            scanner_software_version=None,
            scanner_last_calibration_date=None,
            source_id=self.external_data.session_id,
        )


class OptosSeriesDataParser(OptosSectionParser[SeriesData]):
    def parse(self) -> SeriesData:
        return SeriesData(
            laterality=self._parse_laterality(),
            fixation="Retina",
            anterior=False,
            protocol=self._parse_protocol(),
            # There are no series for Optos, so make each id unique
            source_id=self.external_data.image_id,
        )

    def _parse_laterality(self) -> Laterality:
        eye = self.external_data.image_eye
        if eye == 1:
            return Laterality.LEFT
        if eye == 2:
            return Laterality.RIGHT
        raise ValueError(f"Unknown laterality: {eye}")

    def _parse_protocol(self) -> Optional[str]:
        base_type = get_subint(self.external_data.image_type, 0, 8)

        # Types 9-12 are AF. 10 is definitely zoom, but we don't know if any are plus or reduced, so we leave it blank.
        if base_type in (3, 6, 10):
            return "Zoom"
        if base_type in (2, 6):
            return "Plus"
        if base_type in (7, 8):
            return "Reduced"
        return None


class OptosImagesDataParser(OptosSectionParser[ImagesData]):
    def parse(self) -> Optional[ImagesData]:
        if self.file.options.skip_image_data:
            return None
        image_bytes = self.file.fs.read()

        image_type = OptosImageType.from_int(self.external_data.image_type)
        images: List[ImageData] = []
        columns, rows = get_tiff_dimensions(image_bytes)
        size = Size2D(columns, rows)
        depth = 8

        def append_new_image(
            modality: ImageModality, channel: Optional[int], check: Callable[[np.ndarray], None]
        ) -> None:
            images.append(
                self._build_image(
                    modality,
                    image_type.resolution,
                    size,
                    depth,
                    image_bytes,
                    [
                        ImageOutputParams(
                            image_processing_options=image_processing_option,
                            image_mode="L",
                            image_transform_functions=[
                                partial(
                                    self._get_image_array, image_channel_number=channel, check_image_dimensions=check
                                )
                            ],
                        )
                        for image_processing_option in self.file.options.image_processing_options
                    ],
                )
            )

        if image_type.is_multicolour:
            # Green is channel 0
            append_new_image(ImageModality.SLO_GREEN, 0, self._check_multicolour_image)
            # Red is channel 1
            append_new_image(ImageModality.SLO_RED, 1, self._check_multicolour_image)
        else:
            # Monochrome has no channels
            append_new_image(image_type.modality, None, self._check_monochrome_image)
        return ImagesData(images=images)

    @staticmethod
    def _get_image_array(
        image_array: np.ndarray,
        image_channel_number: Optional[int],
        check_image_dimensions: Callable[[np.ndarray], None],
    ) -> np.ndarray:
        check_image_dimensions(image_array)
        if image_channel_number is not None:
            return cast(np.ndarray, image_array[image_channel_number])
        return image_array

    @staticmethod
    def _check_monochrome_image(image_array: np.ndarray) -> None:
        if len(image_array.shape) != 2:
            raise ImageParseException(
                f"Expected monochrome image data to contain 2 dimensions, got {len(image_array.shape)}"
            )

    @staticmethod
    def _check_multicolour_image(image_array: np.ndarray) -> None:
        if len(image_array.shape) != 3:
            raise ImageParseException(
                f"Expected colour image data to contain 3 dimensions, got {len(image_array.shape)}"
            )
        channel_count, _, _ = image_array.shape
        if channel_count != 2:
            raise ImageParseException(f"Expected 2 colour channels a colour composite image, got {channel_count}")

    def _build_image(
        self,
        modality: ImageModality,
        resolution: float,
        size: Size2D,
        depth: int,
        image_data: bytes,
        image_output_params: List[ImageOutputParams],
    ) -> ImageData:
        dimensions_mm = size * resolution
        resolutions_mm = Size2D(resolution, resolution)

        image_contents = PhotoImageData(
            colour_depth=depth,
            image=image_data,
            capture_datetime=self.external_data.image_captured.ToDatetime(),
            image_output_params=image_output_params,
            image_byte_format=ImageSourceDataType.TIFF,
        )
        return ImageData(
            modality=modality,
            group_id=None,
            size=size,
            dimensions_mm=dimensions_mm,
            resolutions_mm=resolutions_mm,
            contents=[image_contents],
            source_id=f"{self.external_data.image_id}-{modality.code}",
            field_of_view=None,
        )


class OptosParser(SingleFileImageParser):
    parsers: Dict[SectionName, Type[OptosSectionParser]] = {
        SectionName.PATIENT: OptosPatientDataParser,
        SectionName.EXAM: OptosExamDataParser,
        SectionName.SERIES: OptosSeriesDataParser,
        SectionName.IMAGES: OptosImagesDataParser,
        SectionName.DEBUG: OptosDebugDataParser,
    }

    fs: FileStreamWrapper

    def __init__(self, input_files: List[InputFileHandle], options: ParserOptions, external_data: ExternalData) -> None:
        super().__init__(input_files, options, external_data)
        # Protobuf defaults are empty instances instead of None
        if not self.external_data.optos:
            raise ImageParseException("Optos external data is required to parse Optos files")
        self.fs = FileStreamWrapper(self.input_file.handle, options)
        logger.debug("Extracting Optos metadata from %s", self.input_file)

    @classmethod
    def matches_file(cls, input_file: InputFileHandle, options: ParserOptions) -> bool:
        img_type = imghdr.what(input_file.handle)
        return img_type == "tiff"

    def read_sections(self, *section_names: SectionName) -> ParserResults:
        @no_type_check
        def parse(section_name: SectionName) -> Optional[AbstractData]:
            parser = self.parsers.get(section_name)
            if not parser:
                return None
            return parser(self).parse()

        result = SeriesResult(**{section_name.value: parse(section_name) for section_name in section_names})
        return ParserResults([result])
