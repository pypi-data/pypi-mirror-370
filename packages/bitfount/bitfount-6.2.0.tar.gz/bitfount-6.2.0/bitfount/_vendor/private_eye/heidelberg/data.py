from abc import ABC
from typing import Any, DefaultDict, Generic, List, Optional, Type, TypeVar, cast, no_type_check

import attr
from more_itertools import one

from ..utils.attrs import hex_repr


class SegmentBody(ABC):
    pass


SegmentBodyT = TypeVar("SegmentBodyT", bound=SegmentBody)


@attr.s(auto_attribs=True, frozen=True, repr=False, eq=False, hash=True)
class PatientExamSeries:
    patient_id: Optional[int]
    exam_id: Optional[int]
    series_id: Optional[int]

    def __repr__(self) -> str:
        return f"PES(p={self.patient_id}, e={self.exam_id}, s={self.series_id})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatientExamSeries):
            return False
        return (
            self._equal_or_none(self.patient_id, other.patient_id)
            and self._equal_or_none(self.exam_id, other.exam_id)
            and self._equal_or_none(self.series_id, other.series_id)
        )

    @staticmethod
    def _equal_or_none(id1: Optional[int], id2: Optional[int]) -> bool:
        return id1 is None or id2 is None or id1 == id2

    def is_series(self) -> bool:
        return self.patient_id is not None and self.exam_id is not None and self.series_id is not None


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class StandardMetadata:
    patient_id: Optional[int]
    exam_id: Optional[int]
    series_id: Optional[int]
    slice: Optional[int]
    ind: Optional[int]
    pes: PatientExamSeries = attr.ib(init=False, repr=False, eq=False, hash=False)
    mystery_1: Optional[int] = attr.ib(default=None, eq=False)

    @property
    def is_empty(self) -> bool:
        return all(getattr(self, a) is None for a in ["patient_id", "exam_id", "series_id", "slice", "ind"])

    @pes.default
    def _init_pes(self) -> PatientExamSeries:
        return PatientExamSeries(self.patient_id, self.exam_id, self.series_id)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class NodeReference:
    num_entries: int
    current: int
    previous: int
    mystery: Optional[int] = attr.ib(default=None, eq=False)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class Segment(Generic[SegmentBodyT]):
    @hex_repr
    @attr.s(auto_attribs=True)
    class Header:
        position: int
        size: int
        standard_metadata: StandardMetadata
        type: int
        mystery_1: Optional[int] = attr.ib(default=None, eq=False)
        mystery_2: Optional[int] = attr.ib(default=None, eq=False)
        mystery_3: Optional[int] = attr.ib(default=None, eq=False)

    header: Header
    body: SegmentBodyT

    @property
    def sm(self) -> StandardMetadata:
        return self.header.standard_metadata


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class DirectoryHeader:
    @hex_repr
    @attr.s(auto_attribs=True, frozen=True)
    class Segment:
        position: int
        start: int
        size: int
        standard_metadata: StandardMetadata
        type: int
        mystery_1: Optional[int] = attr.ib(default=None, eq=False)
        mystery_2: Optional[int] = attr.ib(default=None, eq=False)

        @property
        def is_empty(self) -> bool:
            return self.start == 0 and self.size == 0 and self.type == 0 and self.standard_metadata.is_empty

    node_reference: NodeReference
    segments: List[Segment]


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class HeidelbergFile:
    standard_metadata: StandardMetadata
    node_reference: NodeReference
    # Really, we want segments above to have the type  DefaultDict[Type[SegmentBodyT], List[Segment[SegmentBodyT]]]
    # but this isn't supported, so we have to bodge it with Any
    segments: DefaultDict[Type[SegmentBody], Any]

    @no_type_check
    def get_single_segment(self, segment_type: Type[SegmentBody]) -> Segment:
        return one(self.segments.get(segment_type, []))

    @no_type_check
    def get_segments(self, segment_type: Type[SegmentBody]) -> List[Segment]:
        return self.segments.get(segment_type, [])

    def get_segments_for_pes(
        self, segment_type: Type[SegmentBody], pes: PatientExamSeries, allow_empty: bool = False
    ) -> List[Segment]:
        segments = self.get_segments(segment_type)
        if not segments and not allow_empty:
            raise KeyError(f"No segments of type {segment_type.__name__} found.")
        return [s for s in segments if s.sm.pes == pes]

    def get_last_segment_for_pes(self, segment_type: Type[SegmentBody], pes: PatientExamSeries) -> Segment:
        """
        Heidelberg stores old versions of segments in order, so the newest one is the last one.
        """
        segments = self.get_segments_for_pes(segment_type, pes)
        if not segments:
            raise KeyError(f"No segments of type {segment_type.__name__} and {pes} found.")
        return segments[-1]


@attr.s(auto_attribs=True)
class DbFiles:
    pdb: HeidelbergFile
    edb: HeidelbergFile
    sdb: HeidelbergFile

    def get_segments(self, segment_type: Type[SegmentBody]) -> List[Segment]:
        pdb_segments = self.pdb.get_segments(segment_type)
        edb_segments = self.edb.get_segments(segment_type)
        sdb_segments = self.sdb.get_segments(segment_type)

        return cast(List[Segment], pdb_segments + edb_segments + sdb_segments)

    @staticmethod
    def is_for_e2e() -> bool:
        return False


class DbFilesForE2E(DbFiles):
    e2e: HeidelbergFile

    def __init__(self, e2e: HeidelbergFile):
        self.e2e = e2e
        self.pdb = e2e
        self.edb = e2e
        self.sdb = e2e

    def get_segments(self, segment_type: Type[SegmentBody]) -> List[Segment]:
        return cast(List[Segment], self.e2e.get_segments(segment_type))

    @staticmethod
    def is_for_e2e() -> bool:
        return True
