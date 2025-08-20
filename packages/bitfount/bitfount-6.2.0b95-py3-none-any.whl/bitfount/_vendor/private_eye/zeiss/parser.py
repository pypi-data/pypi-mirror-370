import logging
from typing import cast

import pydicom
from ...private_eye import ParserOptions, ParserResults
from ...private_eye.common.image_parser import SingleFileImageParser
from ...private_eye.consts import InputFileHandle, SectionName
from ...private_eye.zeiss.metadata_builder import build_metadata
from pydicom import FileDataset

logger = logging.getLogger(__name__)

ZEISS_MANUFACTURER = "Carl Zeiss Meditec"


class ZeissParser(SingleFileImageParser):
    @classmethod
    def matches_file(cls, input_file: InputFileHandle, options: ParserOptions) -> bool:
        # We only check that the file is a DICOM as we need to read the whole file in to check that it is a Zeiss DICOM,
        # which would be rather an expensive operation.  However we do fail in read_sections if it is not a Zeiss DICOM.
        input_file.handle.seek(128)
        first_four_bytes = input_file.handle.read(4)
        logger.debug("First 4 bytes were %s", first_four_bytes)
        input_file.handle.seek(0)
        return first_four_bytes == b"DICM"

    def read_sections(self, *section_names: SectionName) -> ParserResults:
        self.input_file.handle.seek(0)
        file_dataset: FileDataset = pydicom.dcmread(self.input_file.handle)
        if file_dataset.Manufacturer != ZEISS_MANUFACTURER:
            raise ValueError(
                f"Given file is not a Zeiss DICOM.  Expected Manufacturer to be {ZEISS_MANUFACTURER} but "
                f"was {file_dataset.Manufacturer}"
            )
        logger.debug("Parsed DICOM dataset with pydicom")
        return cast(ParserResults, build_metadata(section_names, file_dataset, self.options))
