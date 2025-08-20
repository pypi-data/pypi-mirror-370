import logging
from typing import Optional

from ....private_eye.consts import SectionName
from ....private_eye.data import SeriesData
from ....private_eye.heidelberg.data import DbFiles, PatientExamSeries, Segment
from ....private_eye.heidelberg.metadata_builder.abstract_data_builder import DataBuilder
from ....private_eye.heidelberg.parser import SeriesInfoSegment
from ....private_eye.utils.optional import get_optional

logger = logging.getLogger(__name__)


class _SeriesDataBuilder(DataBuilder[SeriesData]):
    name = SectionName.SERIES
    requires = [SeriesInfoSegment]

    def build(self, pes: PatientExamSeries, db_files: DbFiles) -> SeriesData:
        series_info: Segment[SeriesInfoSegment] = db_files.edb.get_last_segment_for_pes(SeriesInfoSegment, pes)
        laterality = series_info.body.laterality
        fixation = series_info.body.exam_structure
        series_type = series_info.body.series_type

        return SeriesData(
            laterality=laterality,
            fixation=fixation,
            anterior=self._anterior_from_series_type_and_fixation(series_type, fixation),
            protocol=series_type,
            source_id=str(get_optional(pes.series_id)),
        )

    @staticmethod
    def _anterior_from_series_type_and_fixation(series_type: Optional[str], fixation: Optional[str]) -> bool:
        return (
            series_type in ("Pachymetry", "Topography")
            or (series_type is not None and series_type.startswith("AS"))
            or fixation in ("Cornea", "Anterior Segment", "Chamber Angle")
        )
