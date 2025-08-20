from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterable, List, Optional, Sequence, Set, Type, no_type_check

from ....private_eye import ImageParser
from ....private_eye.consts import SectionName
from ....private_eye.data import TImageData
from ....private_eye.external.external_pb2 import ExternalData
from ....private_eye.heidelberg.data import DbFiles, PatientExamSeries, SegmentBody

if TYPE_CHECKING:
    from ....private_eye.heidelberg.heidelberg_parser import HeidelbergParser


class DataBuilder(Generic[TImageData], ABC):
    _required_segments_map: Dict[SectionName, List[Type[SegmentBody]]] = {}
    _class_map: Dict[SectionName, Type["DataBuilder"]] = {}

    # noinspection PyTypeChecker
    @no_type_check  # We need so many casts here that it's not worth the type checking.
    def __init_subclass__(cls, *args: Any, **kwargs: Dict[str, Any]) -> None:
        # We don't want to add the abstract base class to the _class_map.
        if cls.__name__ == DataBuilder.__name__:
            return

        assert isinstance(cls.name, SectionName), (
            "AbstractDataBuilder names must be of type SectionName, " f"not {cls.name}"
        )
        assert isinstance(cls.requires, list), (
            "AbstractDataBuilder requires must be of type list, " f"not {cls.requires}"
        )
        DataBuilder._class_map[cls.name] = cls
        DataBuilder._required_segments_map[cls.name] = cls.requires

    def __init__(self, parser: ImageParser):
        self.options = parser.options
        self.external_data: Optional[ExternalData.Heidelberg] = parser.external_data.heidelberg

    @property
    @abstractmethod
    def name(self) -> SectionName:
        raise NotImplementedError()

    @property
    @abstractmethod
    def requires(self) -> Sequence[Type[SegmentBody]]:
        raise NotImplementedError()

    @abstractmethod
    def build(self, pes: PatientExamSeries, db_files: DbFiles) -> TImageData:
        raise NotImplementedError()

    @classmethod
    def get_required_segment_types(cls, section_names: Iterable[SectionName]) -> Set[Type[SegmentBody]]:
        ret: Set[Type[SegmentBody]] = set()
        for name in section_names:
            required_types = cls._required_segments_map.get(name)
            if required_types:
                ret.update(required_types)
        return ret

    @classmethod
    def get_builder(cls, parser: ImageParser, section_name: SectionName) -> Optional["DataBuilder"]:
        mapped_class: Optional[Type["DataBuilder"]] = cls._class_map.get(section_name)
        if mapped_class:
            return mapped_class(parser)
        return None
