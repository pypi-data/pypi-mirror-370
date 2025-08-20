import logging
from datetime import date, datetime, time
from io import BytesIO
from typing import Dict, Optional, Type, cast

from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp
from PIL import Image
from ...private_eye import ImageParseException, SectionName
from ...private_eye.common.single_file_with_external_data_image_parser import (
    SectionParser,
    SingleFileWithExternalDataImageParser,
)
from ...private_eye.consts import ImageModality, Laterality, ModalityFlag
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
from ...private_eye.imagenet2000.imagenet2k_procedures import proc_to_modality
from ...private_eye.utils.binary import get_subint
from ...private_eye.utils.optional import map_optional

logger = logging.getLogger(__name__)


class PatientParser(SectionParser[PatientData]):
    def parse(self) -> PatientData:
        patient = self.external_data.patient
        return PatientData(
            patient_key=patient.ident,
            last_name=patient.last_name,
            first_name=patient.first_name,
            date_of_birth=map_optional(cast(Timestamp, patient.birth_date), lambda ts: ts.ToDatetime().date()),
            gender=patient.sex,
            # Imagenet2000 patient key is the same as the standard patient key
            source_id=patient.ident,
        )


class ExamParser(SectionParser[ExamData]):
    def parse(self) -> ExamData:
        image = self.external_data.image
        return ExamData(
            manufacturer="Topcon",
            scan_datetime=_image_datetime(image),
            scanner_model="Imagenet2000",
            scanner_serial_number=str(image.device),
            scanner_software_version=None,
            scanner_last_calibration_date=None,
            source_id=str(image.sn),
        )


class SeriesParser(SectionParser[SeriesData]):
    def parse(self) -> SeriesData:
        image = self.external_data.image
        modality = _image_modality(image, self.external_data.patient)

        if ModalityFlag.IS_ANTERIOR in modality.flags:
            anterior = True
            fixation = None
        elif ModalityFlag.IS_INTERIOR in modality.flags:
            anterior = False
            fixation = "Retina"
        else:
            anterior = None
            fixation = None

        return SeriesData(
            laterality=self._parse_laterality(),
            fixation=fixation,
            anterior=anterior,
            protocol=image.proc_name,
            # If we have a proof sheet, use its ID as a source ID. Otherwise, use the raw image ID
            source_id=str(_proof_sheet_sn_or_default(image, image.sn)),
        )

    def _parse_laterality(self) -> Laterality:
        mode = self.external_data.image.mode
        laterality_value = get_subint(mode, 16, 16)
        if laterality_value == 1:
            return Laterality.RIGHT
        elif laterality_value == 2:
            return Laterality.LEFT

        # The laterality is often not set, but the procedure type can give us a reasonable guess
        proc_name = self.external_data.image.proc_name.lower()
        if "left" in proc_name:
            return Laterality.LEFT
        elif "right" in proc_name:
            return Laterality.RIGHT

        # We need to return something, so return 'unknown'
        return Laterality.UNKNOWN


class ImagesParser(SectionParser[ImagesData]):
    def parse(self) -> ImagesData:
        if self.file.options.skip_image_data:
            return ImagesData(images=[])

        return ImagesData(images=[self._parse_image()])

    def _parse_image(self) -> ImageData:
        image = self.external_data.image
        width = get_subint(image.size, 0, 16)
        height = get_subint(image.size, 16, 16)
        size = Size2D(width, height)

        self.file.fs.seek(0)
        image_bytes = self.file.fs.read_data_or_skip()
        image_contents = PhotoImageData(
            colour_depth=8,
            capture_datetime=_image_datetime(image),
            # Imagenet2000 doesn't do anything weird with channels or bands, so we can just consume
            # the file directly. This means we can use PIL directly instead of using the tifffile module.
            image=image_bytes,
            image_output_params=[
                ImageOutputParams(
                    image_processing_options=image_processing_option, image_mode=None, image_transform_functions=[]
                )
                for image_processing_option in self.file.options.image_processing_options
            ],
            image_byte_format=ImageSourceDataType.IMAGENET2000,
        )

        return ImageData(
            modality=_image_modality(image, self.external_data.patient),
            group_id=_proof_sheet_sn_or_default(image, None),
            size=size,
            # There is no information about physical size anywhere, so sadly leave these blank
            dimensions_mm=None,
            resolutions_mm=None,
            field_of_view=image.angle if image.angle > 0 else None,
            contents=[image_contents],
            source_id=str(image.sn),
            is_montage=image.is_proof_sheet,
        )


class DebugParser(SectionParser[DebugData]):
    def parse(self) -> DebugData:
        return DebugData(
            dict(
                external_data=MessageToDict(self.external_data, preserving_proto_field_name=True),
            )
        )


class TopconImagenet2000Parser(SingleFileWithExternalDataImageParser[ExternalData.TopconImagenet2000]):
    image_types = ["tiff", "jpeg"]
    parsers: Dict[SectionName, Type[SectionParser]] = {
        SectionName.PATIENT: PatientParser,
        SectionName.EXAM: ExamParser,
        SectionName.SERIES: SeriesParser,
        SectionName.IMAGES: ImagesParser,
        SectionName.DEBUG: DebugParser,
    }

    def get_external_data(self) -> ExternalData.TopconImagenet2000:
        return self.external_data.topcon_imagenet2000


def _proof_sheet_sn_or_default(image: ExternalData.TopconImagenet2000.Image, default: Optional[int]) -> Optional[int]:
    return image.proof_sheet.sn if image.proof_sheet and image.proof_sheet.sn is not None else default


def _image_modality(
    image: ExternalData.TopconImagenet2000.Image, patient: ExternalData.TopconImagenet2000.Patient
) -> ImageModality:
    proc_name = image.proc_name
    # There are a surprisingly high number of cases of the procedure name matches the patient ID
    # In these cases we both have no idea of what the image is, and there are sometimes cases of identifiable data
    # We could simply ignore this case and simply fall through to the default,
    # but it may be useful to log this separately
    if proc_name == patient.ident:
        # This happens surprisingly frequently
        logger.info("Imagenet2000 image %s procedure is similar to patient key", image.sn)
        return ImageModality.UNKNOWN

    return proc_to_modality(proc_name)


def _image_datetime(image: ExternalData.TopconImagenet2000.Image) -> datetime:
    date_ = date.fromisoformat(image.proc_date)
    time_ = time.fromisoformat(image.proc_time)
    return datetime.combine(date_, time_)
