from pathlib import PurePath
from typing import Iterable, List, Optional, Set, Type, cast

from more_itertools import flatten, one
from ...private_eye.common.image_parser import ImageParser
from ...private_eye.consts import InputFileHandle, SectionName
from ...private_eye.data import ParserOptions, ParserResults, SeriesResult, TImageData
from ...private_eye.external.external_pb2 import ExternalData
from ...private_eye.heidelberg.data import DbFilesForE2E, HeidelbergFile, PatientExamSeries, SegmentBody
from ...private_eye.heidelberg.metadata_builder.abstract_data_builder import DataBuilder
from ...private_eye.heidelberg.parser import HeidelbergStreamWrapper
from ...private_eye.heidelberg.parser.file_parser import parse
from ...private_eye.heidelberg.validator import validate
from ...private_eye.utils.binary import peek


class HeidelbergE2EParser(ImageParser):
    e2e: HeidelbergStreamWrapper

    def __init__(self, input_files: List[InputFileHandle], options: ParserOptions, external_data: ExternalData):
        super().__init__(input_files, options, external_data)
        input_file = one(self.input_files)

        self.e2e = HeidelbergStreamWrapper(input_file.handle, self.options)

    @classmethod
    def get_extra_files(cls, input_file: InputFileHandle, options: ParserOptions) -> List[PurePath]:
        # No additional files are required for E2E files.
        return []

    @classmethod
    def matches_file(cls, input_file: InputFileHandle, options: ParserOptions) -> bool:
        with peek(input_file.handle, 4) as binary_data:
            return binary_data == b"CMDb" and input_file.file_path.suffix.lower() == ".e2e"

    def read_sections(self, *section_names: SectionName) -> ParserResults:
        self._reset_e2e_pointer()
        required_segments = self._calculate_required_segments(section_names)
        parsed_files = parse(self.e2e, self.options, required_segments=required_segments)

        parsed_results = []
        for parsed_file in parsed_files:
            db_files = DbFilesForE2E(parsed_file)
            validate(db_files)
            pes = self._get_pes(parsed_file)
            result = self._build_result(db_files, pes, section_names)
            parsed_results.append(result)

        return ParserResults(parsed_results, is_e2e=True)

    def _reset_e2e_pointer(self) -> None:
        self.e2e.seek(0)

    def _calculate_required_segments(self, section_names: Iterable[SectionName]) -> Optional[Set[Type[SegmentBody]]]:
        if self.options.full_parse:
            return None
        return DataBuilder.get_required_segment_types(section_names)

    @staticmethod
    def _get_pes(series: HeidelbergFile) -> PatientExamSeries:
        # Get 'most filled in' PES, throwing error if there are others which are not the same or weaker.
        all_segments = flatten(series.get_segments(segment_type) for segment_type in series.segments)

        def _count_nones(pes: PatientExamSeries) -> int:
            return [pes.patient_id, pes.exam_id, pes.series_id].count(None)

        sorted_segments = sorted(all_segments, key=lambda segment: _count_nones(segment.sm.pes))

        if len(sorted_segments) == 0:
            raise ValueError("No segments were found.")

        pes = sorted_segments[0].sm.pes

        if not all(segment.sm.pes == pes for segment in all_segments):
            raise ValueError("Other series segments found.")

        return cast(PatientExamSeries, pes)

    def _build_result(
        self, db_files: DbFilesForE2E, pes: PatientExamSeries, sections: Iterable[SectionName]
    ) -> SeriesResult:
        parser_inputs = {section.value: self._build_section(db_files, pes, section) for section in sections}
        return SeriesResult(**parser_inputs)

    def _build_section(
        self, db_files: DbFilesForE2E, pes: PatientExamSeries, section_name: SectionName
    ) -> Optional[TImageData]:
        builder = DataBuilder.get_builder(self, section_name)
        if builder is None:
            return None

        result = builder.build(pes, db_files)
        return cast(TImageData, result)
