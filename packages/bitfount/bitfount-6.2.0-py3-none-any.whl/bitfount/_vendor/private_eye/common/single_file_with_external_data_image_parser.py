import imghdr
import logging
from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, Type

from ...private_eye import ImageParseException, ParserOptions, ParserResults, SectionName, SeriesResult
from ...private_eye.common.file_stream_wrapper import FileStreamWrapper
from ...private_eye.common.image_parser import SingleFileImageParser
from ...private_eye.consts import InputFileHandle
from ...private_eye.data import AbstractData, TExternalData, TImageData
from ...private_eye.external.external_pb2 import ExternalData

logger = logging.getLogger(__name__)


class SingleFileWithExternalDataImageParser(SingleFileImageParser, ABC, Generic[TExternalData]):
    parsers: Dict[SectionName, Type["SectionParser[AbstractData]"]]
    image_types: List[str]
    fs: FileStreamWrapper

    def __init__(self, input_files: List[InputFileHandle], options: ParserOptions, external_data: ExternalData) -> None:
        super().__init__(input_files, options, external_data)
        if not self.get_external_data():
            raise ImageParseException("External data is required to parse Imagenet2000 files")
        self.fs = FileStreamWrapper(self.input_file.handle, options)
        logger.debug("Extracting Imagenet2000 metadata from %s", self.input_file)

    @abstractmethod
    def get_external_data(self) -> TExternalData:
        raise NotImplementedError()

    @classmethod
    def matches_file(cls, input_file: InputFileHandle, options: ParserOptions) -> bool:
        img_type = imghdr.what(input_file.handle)
        return img_type in cls.image_types

    def read_sections(self, *section_names: SectionName) -> ParserResults:
        def parse(section_name: SectionName) -> Optional[AbstractData]:
            parser = self.parsers.get(section_name)

            if not parser:
                return None

            return parser(self).parse()

        result = SeriesResult(
            **{section_name.value: parse(section_name) for section_name in section_names}  # type: ignore
        )
        return ParserResults([result])


class SectionParser(Generic[TImageData], ABC):
    def __init__(self, file: SingleFileWithExternalDataImageParser) -> None:
        self.file = file
        self.external_data = file.get_external_data()

    @abstractmethod
    def parse(self) -> TImageData:
        raise NotImplementedError
