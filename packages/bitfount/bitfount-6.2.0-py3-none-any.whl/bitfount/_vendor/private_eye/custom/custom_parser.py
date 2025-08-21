import logging
from typing import Any, Dict, Type, cast

from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
from ...private_eye.common.single_file_with_external_data_image_parser import (
    SectionParser,
    SingleFileWithExternalDataImageParser,
)
from ...private_eye.consts import ImageModality, Laterality, SectionName
from ...private_eye.custom.get_jpeg_header_information import get_jpeg_header_data
from ...private_eye.data import (
    DebugData,
    ExamData,
    ImageData,
    ImageOutputParams,
    ImagesData,
    ImageSourceDataType,
    PatientData,
    PhotoImageData,
    SeriesData,
    Size2D,
)
from ...private_eye.external.external_pb2 import ExternalData
from ...private_eye.utils.optional import map_optional

logger = logging.getLogger(__name__)


JFIF_COMPONENT_NUMBER_TO_IMAGE_MODE = {1: "L", 3: "YCbCr", 4: "CMYK"}


class PatientParser(SectionParser[PatientData]):
    def parse(self) -> PatientData:
        data = self.external_data
        return PatientData(
            patient_key=data.patient_key,
            last_name=data.last_name,
            first_name=data.first_name,
            gender=self._parse_gender(),
            date_of_birth=map_optional(cast(Timestamp, data.date_of_birth), lambda ts: ts.ToDatetime().date()),
            source_id=data.patient_key,
        )

    def _parse_gender(self) -> str:
        gender_value = self.external_data.gender
        if not gender_value or gender_value in ["M", "F", "U"]:
            return gender_value
        else:
            raise ValueError(f"Unknown gender: {gender_value}")


class ExamParser(SectionParser[ExamData]):
    def parse(self) -> ExamData:
        data = self.external_data
        return ExamData(
            manufacturer=data.manufacturer,
            scan_datetime=data.scan_datetime.ToDatetime(),
            scanner_model=data.scanner_model,
            scanner_serial_number=data.scanner_serial_number,
            scanner_software_version=data.scanner_software_version,
            scanner_last_calibration_date=None,
            source_id=data.source_exam_id or data.source_series_id or data.source_image_id,
        )


class SeriesParser(SectionParser[SeriesData]):
    def parse(self) -> SeriesData:
        data = self.external_data
        return SeriesData(
            laterality=self._parse_laterality(),
            fixation=data.fixation,
            anterior=data.anterior,
            protocol=data.protocol,
            source_id=data.source_series_id or data.source_image_id,
        )

    def _parse_laterality(self) -> Laterality:
        laterality_value = self.external_data.laterality
        if laterality_value == "L":
            return Laterality.LEFT
        elif laterality_value == "R":
            return Laterality.RIGHT
        elif laterality_value == "B":
            return Laterality.BOTH
        elif laterality_value == "U":
            return Laterality.UNKNOWN
        else:
            raise ValueError(f"Unknown laterality: {laterality_value}")


class ImagesParser(SectionParser[ImagesData]):
    def parse(self) -> ImagesData:
        return ImagesData(images=[self._parse_image()])

    def _parse_image(self) -> ImageData:
        data = self.external_data

        self.file.fs.seek(0)
        image_bytes = self.file.fs.read_data_or_skip()

        jpeg_header_data = get_jpeg_header_data(image_bytes)

        try:
            image_mode = JFIF_COMPONENT_NUMBER_TO_IMAGE_MODE[jpeg_header_data.number_of_components]
        except KeyError:
            image_mode = None

        image_contents = PhotoImageData(
            colour_depth=jpeg_header_data.bits_per_sample,
            capture_datetime=data.capture_datetime.ToDatetime()
            if data.capture_datetime
            else data.scan_datetime.ToDatetime(),
            image=image_bytes,
            image_byte_format=ImageSourceDataType.JPEG,
            image_output_params=[
                ImageOutputParams(
                    image_processing_options=image_processing_options,
                    image_mode=image_mode,
                    image_transform_functions=[],
                )
                for image_processing_options in self.file.options.image_processing_options
            ],
        )

        return ImageData(
            modality=self._parse_modality(),
            group_id=None,
            size=Size2D(jpeg_header_data.width, jpeg_header_data.height),
            dimensions_mm=None,
            resolutions_mm=None,
            field_of_view=data.field_of_view,
            contents=[image_contents],
            source_id=data.source_image_id,
        )

    def _parse_modality(self) -> ImageModality:
        modality_value = self.external_data.modality.lower()

        # Try to match a modality by case insensitive comparison against both code and description
        for image_modality in ImageModality:
            if modality_value in [image_modality.code.lower(), image_modality.value.lower()]:
                return image_modality
        raise ValueError(f"Unknown modality: {modality_value}")


class DebugParser(SectionParser[DebugData]):
    def parse(self) -> DebugData:
        return DebugData(dict(external_data=MessageToDict(self.external_data, preserving_proto_field_name=True)))


class CustomParser(SingleFileWithExternalDataImageParser[ExternalData.Custom]):
    image_types = ["jpeg"]
    parsers: Dict[SectionName, Type[SectionParser[Any]]] = {
        SectionName.PATIENT: PatientParser,
        SectionName.EXAM: ExamParser,
        SectionName.SERIES: SeriesParser,
        SectionName.IMAGES: ImagesParser,
        SectionName.DEBUG: DebugParser,
    }

    def get_external_data(self) -> ExternalData.Custom:
        return self.external_data.custom
