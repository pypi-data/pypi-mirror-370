import logging
from collections import defaultdict
from pathlib import PurePath
from typing import Iterable, List, Optional, Set, Type, cast

from more_itertools import one
from ...private_eye import ParserOptions
from ...private_eye.common.image_parser import ImageParser
from ...private_eye.consts import InputFileHandle, NoImageData, RequiresFiles, SectionName
from ...private_eye.data import ParserResults, SeriesResult, TImageData
from ...private_eye.exceptions import ImageParseException
from ...private_eye.external.external_pb2 import ExternalData
from ...private_eye.heidelberg.data import (
    DbFiles,
    HeidelbergFile,
    NodeReference,
    PatientExamSeries,
    SegmentBody,
    StandardMetadata,
)
from ...private_eye.heidelberg.metadata_builder.abstract_data_builder import DataBuilder
from ...private_eye.heidelberg.parser.file_parser import parse
from ...private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from ...private_eye.heidelberg.validator import validate
from ...private_eye.utils.binary import peek

logger = logging.getLogger(__name__)


class HeidelbergParser(ImageParser):
    stream_wrapper = HeidelbergStreamWrapper

    pdb: Optional[HeidelbergStreamWrapper]
    edb: HeidelbergStreamWrapper
    sdb: HeidelbergStreamWrapper
    sdb_header: StandardMetadata

    def __init__(self, input_files: List[InputFileHandle], options: ParserOptions, external_data: ExternalData) -> None:
        """
        If we have a matching sdb, edb, and pdb, then succeed otherwise fail with a useful error.
        """
        super().__init__(input_files, options, external_data)

        sdb_file = one(
            self._filter_by_extension(".sdb"),
            too_short=NoImageData("Only heidelberg .sdb files contain image data"),
            too_long=ImageParseException("Parsing multiple heidelberg scan files is not currently supported"),
        )
        self.sdb = self.stream_wrapper(sdb_file.handle, options)
        self.sdb_header = self.sdb.read_file_header()

        suggested_files = []
        edbs = self._filter_by_extension(".edb")
        pdbs = self._filter_by_extension(".pdb")

        try:
            edb_file = one(edbs, too_long=ImageParseException("Multiple exam files provided"))
        except ValueError:
            suggested_files.append(self._get_suggested_path(sdb_file, self.sdb_header.exam_id, "edb"))
        else:
            self.edb = self.stream_wrapper(edb_file.handle, options)

        if options.heidelberg_skip_pdb or self.external_data.heidelberg:
            # Prefer using external data to the pdb; the date of birth is more reliable
            self.pdb = None
        else:
            try:
                pdb_file = one(pdbs, too_long=ImageParseException("Multiple patient files provided"))
                self.pdb = self.stream_wrapper(pdb_file.handle, options)
            except ValueError:
                suggested_files.append(self._get_suggested_path(sdb_file, self.sdb_header.patient_id, "pdb"))

        if suggested_files:
            raise RequiresFiles(files=suggested_files)

    @classmethod
    def get_extra_files(cls, sdb_file: InputFileHandle, options: ParserOptions) -> List[PurePath]:
        ancillary_files: List[PurePath] = []
        if not sdb_file.original_filepath.name.endswith(".sdb"):
            raise ValueError(f"File is not of type '.sdb': {sdb_file.original_filepath}")
        sdb_file.handle.seek(0)
        if not cls.matches_file(sdb_file, options):
            raise ValueError(f"File is invalid: {sdb_file.original_filepath}")

        sdb = cls.stream_wrapper(sdb_file.handle, options)
        sdb_header = sdb.read_file_header()
        ancillary_files.append(cls._get_suggested_path(sdb_file, sdb_header.exam_id, "edb"))
        ancillary_files.append(cls._get_suggested_path(sdb_file, sdb_header.patient_id, "pdb"))
        return ancillary_files

    @classmethod
    def matches_file(cls, input_file: InputFileHandle, options: ParserOptions) -> bool:
        """Check that the file is a heidelberg file."""
        # If we don't need the file, we don't care about its contents
        if options.heidelberg_skip_pdb and input_file.file_path.suffix.lower() == ".pdb":
            return True
        with peek(input_file.handle, 4) as data:
            return data == b"CMDb"

    def read_sections(self, *section_names: SectionName) -> ParserResults:
        required_segments = self._calculate_required_segments(section_names)

        db_files = self._parse_heidelberg_files(required_segments)
        validate(db_files)

        result = self._build_metadata(db_files, section_names)
        return ParserResults([result])

    def _build_metadata(self, db_files: DbFiles, sections: Iterable[SectionName]) -> SeriesResult:
        pes = db_files.sdb.standard_metadata.pes
        if pes.patient_id is None:
            raise ImageParseException("Expected patient ID in SDB metadata")

        results = {section.value: self._build_section(db_files, pes, section) for section in sections}
        return SeriesResult(**results)  # type: ignore

    def _build_section(self, db_files: DbFiles, pes: PatientExamSeries, section: SectionName) -> Optional[TImageData]:
        builder = DataBuilder.get_builder(self, section)

        if not builder:
            return None

        return cast(TImageData, builder.build(pes, db_files))

    def _calculate_required_segments(self, section_names: Iterable[SectionName]) -> Optional[Set[Type[SegmentBody]]]:
        required_segments: Optional[Set[Type[SegmentBody]]]
        if self.options.full_parse:
            required_segments = None
        else:
            required_segments = DataBuilder.get_required_segment_types(section_names)
        logger.debug("required_segments: %s", required_segments)
        return required_segments

    def _parse_heidelberg_files(self, required_segments: Optional[Set[Type[SegmentBody]]]) -> DbFiles:
        logger.debug("Parsing sdb file")
        self.sdb.seek(0x24)
        sdb = one(
            parse(
                self.sdb,
                parser_options=self.options,
                file_header_metadata=self.sdb_header,
                required_segments=required_segments,
                required_pes=self.sdb_header.pes,
            )
        )

        if self.pdb:
            logger.debug("Parsing pdb file")
            self.pdb.seek(0)
            pdb = one(
                parse(
                    self.pdb,
                    parser_options=self.options,
                    required_segments=required_segments,
                    required_pes=self.sdb_header.pes,
                )
            )
        else:
            logger.debug("Skipping parse of pdb file")
            pdb = HeidelbergFile(
                StandardMetadata(self.sdb_header.patient_id, None, None, None, None),
                NodeReference(0, 0, 0),
                defaultdict(lambda: None),
            )

        logger.debug("Parsing edb file")
        self.edb.seek(0)
        edb = one(
            parse(
                self.edb,
                parser_options=self.options,
                required_segments=required_segments,
                required_pes=self.sdb_header.pes,
            )
        )

        return DbFiles(pdb, edb, sdb)

    def _filter_by_extension(self, extension: str) -> List[InputFileHandle]:
        return [f for f in self.input_files if f.original_filepath.suffix.lower() == extension]

    @staticmethod
    def _get_suggested_path(sdb_file: InputFileHandle, section_id: Optional[int], extension: str) -> PurePath:
        parent_folder = sdb_file.original_filepath.parent
        return parent_folder / f"{str(section_id).rjust(8, '0')}.{extension}"
