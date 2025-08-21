from abc import ABC, abstractmethod
from pathlib import PurePath
from typing import List, Union

from ...private_eye import ParserOptions
from ...private_eye.consts import InputFileHandle, SectionName
from ...private_eye.data import AbstractData, ParserResults
from ...private_eye.exceptions import ImageParseException
from ...private_eye.external.external_pb2 import ExternalData
from ...private_eye.utils.external import protobuf_proxy


class ImageParser(ABC):
    """The base class responsible for parsing a given image file. Subclasses of this class will be responsible for
    specific file formats, e.g. Topcon.
    """

    def __init__(self, input_files: List[InputFileHandle], options: ParserOptions, external_data: ExternalData) -> None:
        self.input_files = input_files
        self.options = options
        self.external_data = protobuf_proxy(external_data)

    @classmethod
    @abstractmethod
    def get_extra_files(cls, input_file: InputFileHandle, options: ParserOptions) -> List[PurePath]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def matches_file(cls, input_file: InputFileHandle, options: ParserOptions) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def read_sections(self, *section_names: SectionName) -> ParserResults:
        """Read one or more sections from the given file.

        The returned dictionary will contain a list of :class:`private_eye.SeriesResults`, which will
        have properties based on section names. (See also :class:`private_eye.SectionName`):

        ========================================    =====================================
        Section Name                                Associated data type
        ========================================    =====================================
        :attr:`private_eye.SectionName.PATIENT`     :class:`private_eye.PatientData`
        :attr:`private_eye.SectionName.EXAM`        :class:`private_eye.ExamData`
        :attr:`private_eye.SectionName.SERIES`      :class:`private_eye.SeriesData`
        :attr:`private_eye.SectionName.IMAGES`      :class:`private_eye.Images`
        :attr:`private_eye.SectionName.DEBUG`       :class:`private_eye.DebugData`
        ========================================    =====================================

        :param section_names: One or more sections from the :class:`private_eye.SectionName` enum
        :return: a :class:`private_eye.ParserResults` object with one data object per section
        """
        raise NotImplementedError()

    def read_all_sections(self) -> ParserResults:
        """
        Read all sections from the given file

        See :py:meth:`~private_eye.ImageParser.read_section` for more info.

        :return: a :class:`private_eye.ParserResults` object with one data object per section
        """
        all_sections = list(SectionName)
        return self.read_sections(*all_sections)

    def read_section(self, section_name: Union[SectionName, str]) -> List[AbstractData]:
        """Read a single section from the given file.

        :param: Name of the required section.
        :return: A data object corresponding to the given `section_name`.
        :raise: :exc:`ValueError` if the section is not found.
        """
        section_name = SectionName(section_name)
        parser_result = self.read_sections(section_name)
        return [result.get(section_name) for result in parser_result.results]


class SingleFileImageParser(ImageParser, ABC):
    input_file: InputFileHandle

    def __init__(self, input_files: List[InputFileHandle], options: ParserOptions, external_data: ExternalData) -> None:
        super().__init__(input_files, options, external_data)
        if len(input_files) != 1:
            raise ImageParseException(f"File parser only supports single files, got {input_files}")
        self.input_file = input_files[0]

    @classmethod
    def get_extra_files(cls, input_file: InputFileHandle, options: ParserOptions) -> List[PurePath]:
        # Since this is a single file image no additional files are needed so return empty list
        return []
