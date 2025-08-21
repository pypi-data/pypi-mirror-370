import logging
from datetime import datetime, timedelta
from typing import List, Optional

import attr
from ....private_eye.consts import SectionName
from ....private_eye.data import ExamData
from ....private_eye.heidelberg.data import DbFiles, PatientExamSeries, Segment
from ....private_eye.heidelberg.metadata_builder.abstract_data_builder import DataBuilder
from ....private_eye.heidelberg.parser import DeviceSegment, ImageInfo05Segment, ImageParseException
from ....private_eye.utils.optional import get_optional

logger = logging.getLogger(__name__)


class _ExamDataBuilder(DataBuilder[ExamData]):
    name = SectionName.EXAM
    requires = [DeviceSegment, ImageInfo05Segment]

    def build(self, pes: PatientExamSeries, db_files: DbFiles) -> ExamData:
        model_name: Optional[str] = None
        try:
            device_segment: Segment[DeviceSegment] = db_files.edb.get_last_segment_for_pes(
                DeviceSegment, attr.evolve(pes, series_id=None)
            )
            model_name = device_segment.body.camera_model

        except KeyError:
            # TODO RIPF-1589 This data could be queried from the database instead of setting it to null
            logger.warning("No device data is contained inside this file.")

        image_info_segments: List[Segment[ImageInfo05Segment]] = db_files.edb.get_segments_for_pes(
            ImageInfo05Segment, pes
        )
        capture_datetime = _get_scan_datetime(image_info_segments)

        return ExamData(
            scan_datetime=capture_datetime,
            manufacturer="Heidelberg",
            scanner_model=model_name,
            scanner_software_version=None,
            scanner_serial_number=None,
            scanner_last_calibration_date=None,
            source_id=str(get_optional(pes.exam_id)),
        )


def _get_scan_datetime(image_info_segments: List[Segment[ImageInfo05Segment]]) -> datetime:
    """We assume that the capture datetimes are all pretty close to either other and just return the earliest.   If
    they aren't close then fail.
    """
    capture_datetimes = sorted([iis.body.capture_datetime for iis in image_info_segments])
    if capture_datetimes[-1] - capture_datetimes[0] > timedelta(minutes=15):
        raise ImageParseException("Capture datetimes differ by over 15 minutes")
    capture_datetime = capture_datetimes[0]
    return capture_datetime
