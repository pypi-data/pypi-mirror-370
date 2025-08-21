import logging
from typing import Callable, Dict, Iterable, Optional, no_type_check

from ...private_eye import (
    AbstractData,
    ExamData,
    Laterality,
    ParserOptions,
    ParserResults,
    PatientData,
    SectionName,
    SeriesData,
    SeriesResult,
)
from ...private_eye.zeiss.common import parse_optional_date, parse_separated_optional_datetimes
from ...private_eye.zeiss.debug_data_builder import build_debug_metadata
from ...private_eye.zeiss.image_data_builder import build_images_metadata
from ...private_eye.zeiss.visual_field_data_builder import build_visual_field_metadata
from pydicom import FileDataset

logger = logging.getLogger(__name__)


@no_type_check
def build_metadata(
    section_names: Iterable[SectionName], file_dataset: FileDataset, options: ParserOptions
) -> ParserResults:
    parser_input = {
        section_name.value: _metadata_builders[section_name](file_dataset, options) for section_name in section_names
    }
    parser_result = SeriesResult(**parser_input)
    return ParserResults([parser_result])


def _build_patient_metadata(ds: FileDataset, options: ParserOptions) -> PatientData:
    return PatientData(
        patient_key=ds.PatientID,
        first_name=ds.PatientName.given_name,
        last_name=ds.PatientName.family_name,
        date_of_birth=parse_optional_date(ds.PatientBirthDate),
        gender=ds.PatientSex,
        source_id=ds.PatientID,
    )


def _build_exam_metadata(ds: FileDataset, options: ParserOptions) -> ExamData:
    return ExamData(
        scan_datetime=parse_separated_optional_datetimes(ds.get("StudyDate"), ds.get("StudyTime")),
        manufacturer=ds.Manufacturer,
        source_id=ds.StudyInstanceUID,
        scanner_model=ds.ManufacturerModelName,
        scanner_serial_number=ds.get("DeviceSerialNumber"),
        scanner_software_version=",".join(ds.get("SoftwareVersions", [])),
        scanner_last_calibration_date=parse_separated_optional_datetimes(
            ds.get("DateOfLastCalibration"), ds.get("TimeOfLastCalibration")
        ),
    )


def _build_series_metadata(ds: FileDataset, options: ParserOptions) -> SeriesData:
    # Between ProtocolName and SeriesDescription we hope to come up with something sensible
    series_type = ds.get("SeriesDescription")
    if not series_type:
        series_type = ds.get("ProtocolName")

    laterality_str = ds.get("ImageLaterality") or ds.get("Laterality")
    if laterality_str:
        laterality = Laterality(laterality_str)
    else:
        # TODO RIPF-239 Some Zeiss images do not have a laterality, need to check if this means they refer to both
        # eyes
        # e.g. \\mehforum\DICO-Store1\2015\1\10\1.2.276.0.75.2.5.80.25.3.180810011126887.128189930951.1792217172.dcm
        laterality = Laterality.UNKNOWN

    return SeriesData(
        laterality=laterality,
        # TODO RIPF-239 This is not obvious for Zeiss.  For Fundus images the AnatomicRegionSequence is just Eye,
        #  probably because the exact fixation changes inside the series.  Fixation could be moved to image to
        #  overcome this.
        fixation=None,
        anterior=False,
        protocol=series_type,
        source_id=ds.SeriesInstanceUID,
    )


_metadata_builders: Dict[SectionName, Callable[[FileDataset, ParserOptions], Optional[AbstractData]]] = {
    SectionName.PATIENT: _build_patient_metadata,
    SectionName.EXAM: _build_exam_metadata,
    SectionName.SERIES: _build_series_metadata,
    SectionName.IMAGES: build_images_metadata,
    SectionName.VISUAL_FIELD: build_visual_field_metadata,
    SectionName.DEBUG: build_debug_metadata,
}
