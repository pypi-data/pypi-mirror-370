import logging
from itertools import groupby, repeat
from typing import Any, Dict, List, Type

import attr
import numpy as np
from more_itertools import flatten
from PIL.Image import Image
from ....private_eye.data import DebugData
from tabulate import tabulate

from ...consts import SectionName
from ..data import DbFiles, HeidelbergFile, PatientExamSeries, Segment, SegmentBody, StandardMetadata
from ..parser import ContourSegment, ImageParseException, ImageThumbnail
from ..parser.segment.binary import BinarySegmentBody
from .abstract_data_builder import DataBuilder

logger = logging.getLogger(__name__)


class _DebugBuilder(DataBuilder[DebugData]):
    name = SectionName.DEBUG
    requires: List[Type[SegmentBody]] = []

    def build(self, pes: PatientExamSeries, db_files: DbFiles) -> DebugData:
        if db_files.is_for_e2e():
            metadata = {"e2e": _prettify(db_files.pdb)}
        else:
            metadata = {
                "pdb": _prettify(db_files.pdb),
                "edb": _prettify(db_files.edb),
                "sdb": _prettify(db_files.sdb),
            }

        metadata["segment_summary"] = _build_segment_summary(pes, db_files, False)
        metadata["restricted_segment_summary"] = _build_segment_summary(pes, db_files, True)

        if self.options.skip_image_data:
            debug_images: Dict[str, Image] = {}
        else:
            debug_images = _extract_debug_images(db_files)
        files = _extract_debug_files(db_files)
        files.update(_extract_debug_contours(db_files))
        return DebugData(metadata, images=debug_images, files=files)


def _prettify(heidelberg_file: HeidelbergFile) -> Any:
    as_dict = attr.asdict(heidelberg_file, recurse=False)

    def _prettify(d: Any) -> Any:
        if isinstance(d, dict):
            return {str(k): _prettify(v) for k, v in d.items() if k not in ["data"]}
        if isinstance(d, (list, set)):
            return [_prettify(e) for e in d]
        if hasattr(d, "__attrs_attrs__"):
            return _prettify(attr.asdict(d, recurse=False))
        if isinstance(d, Image):
            return "<Image Data>"
        if isinstance(d, np.ndarray):
            return "<Raw Data>"
        return d

    return _prettify(as_dict)


def _build_segment_summary(pes: PatientExamSeries, db_files: DbFiles, restricted: bool) -> str:
    def should_include_segment(standard_metadata: StandardMetadata) -> bool:
        if not restricted:
            return True
        return standard_metadata.pes == pes

    def hexify(val: Any) -> str:
        if isinstance(val, int):
            return f"{val} | 0x{val:x}"
        return str(val)

    if db_files.is_for_e2e():
        segments = zip(repeat("e2e"), flatten(db_files.pdb.segments.values()))
    else:
        segments = flatten(
            [
                zip(repeat("pdb"), flatten(db_files.pdb.segments.values())),
                zip(repeat("edb"), flatten(db_files.edb.segments.values())),
                zip(repeat("sdb"), flatten(db_files.sdb.segments.values())),
            ]
        )

    rows = [
        [
            hexify(val)
            for val in [
                file_name,
                segment.header.type,
                segment.header.standard_metadata.patient_id,
                segment.header.standard_metadata.exam_id,
                segment.header.standard_metadata.series_id,
                segment.header.standard_metadata.slice,
                segment.header.standard_metadata.ind,
                type(segment.body).__name__,
                segment.header.position,
                segment.header.size,
                segment.header.standard_metadata.mystery_1,
                segment.header.mystery_1,
                segment.header.mystery_2,
                segment.header.mystery_3,
            ]
        ]
        for file_name, segment in segments
        if should_include_segment(segment.header.standard_metadata)
    ]
    summary: str = tabulate(
        rows, headers=["file", "type", "p", "e", "s", "sl", "ind", "type", "pos", "size", "sm_m1", "m1", "m2", "m3"]
    )
    logger.debug(pes)
    logger.debug("Segment Summary (restricted: %s, rows: %s)\n%s", restricted, len(rows), summary)

    return summary


def _extract_debug_images(db_files: DbFiles) -> Dict[str, Image]:
    def name(ic: Segment[ImageThumbnail]) -> str:
        sm = ic.header.standard_metadata
        return "-".join([str(elem) for elem in ["debug", "ic", sm.series_id, sm.slice, sm.ind]])

    image_constituents: List[Segment[ImageThumbnail]] = db_files.edb.get_segments(ImageThumbnail)
    images = [(name(ic), ic.body.data) for ic in image_constituents]

    names = [image[0] for image in images]
    if len(set(names)) != len(names):
        raise ImageParseException(f"Found duplicate image constituents: {names}")

    return dict(images)


def _extract_debug_contours(db_files: DbFiles) -> Dict[str, bytes]:
    contours = db_files.get_segments(ContourSegment)

    def _filename(s: Segment, index: int) -> str:
        md = s.sm
        layer_id = s.body.layer_name or s.body.id
        return f"contour-{md.patient_id}-{md.exam_id}-{md.series_id}-{md.slice}-{md.ind}-{layer_id}-{index}.csv"

    def _ser(data: List[float]) -> bytes:
        return "\r\n".join(str(c) for c in data).encode("ascii")

    return dict((_filename(c, index), _ser(c.body.data)) for index, c in enumerate(contours))


def _extract_debug_files(db_files: DbFiles) -> Dict[str, bytes]:
    binary_segments = db_files.get_segments(BinarySegmentBody)

    def _file_name(header: Segment.Header, index: int) -> str:
        md = header.standard_metadata
        return f"0x{header.type:x}-{md.patient_id}-{md.exam_id}-{md.series_id}-{md.slice}-{md.ind}-{index}.dat"

    ret = {}
    for _, segments in groupby(
        binary_segments, lambda s: (s.header.type, s.sm.patient_id, s.sm.exam_id, s.sm.series_id, s.sm.slice, s.sm.ind)
    ):
        for index, segment in enumerate(segments):
            ret[_file_name(segment.header, index)] = segment.body.value

    return ret
