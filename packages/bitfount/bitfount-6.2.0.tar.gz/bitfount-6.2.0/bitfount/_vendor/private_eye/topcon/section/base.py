from abc import ABC, abstractmethod
from typing import Any, Dict, List

import attr
from ....private_eye import ParserOptions

from ...topcon.topcon_stream_wrapper import TopconStreamWrapper


class FdaSection(ABC):
    """
    A slice of an FDA file with its own stream object
    """

    fs: TopconStreamWrapper
    section_id: str
    options: ParserOptions

    # List of fields to exclude from debug dump
    EXCLUDED_FIELDS: List[str] = []

    # Whether this section can appear in a FDA file multiple times
    MULTIPLE = False

    def __init__(self, fs: TopconStreamWrapper, section_id: str, options: ParserOptions) -> None:
        """
        Create the section
        :param fs: a BaseIO-like object for this section.
        :param section_id: The ID of the section in the FDA file. Does not have to be unique
        :param options: Parsing options
        """
        self.fs = fs
        self.section_id = section_id
        self.options = options

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError()

    def debug_data(self) -> Dict[str, Any]:
        excluded_names = set(self.EXCLUDED_FIELDS + ["fs", "options"])
        ret = {}
        for attr_name, value in self.__dict__.items():
            if not attr_name.startswith("_") and attr_name not in excluded_names:
                ret[attr_name] = attr.asdict(value) if hasattr(value, "__attrs_attrs__") else value
        return ret

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.section_id})"
