import logging
from typing import List

import attr
import numpy as np
from .....private_eye import ParserOptions
from .....private_eye.consts import RetinalLayer
from .....private_eye.heidelberg.data import Segment
from .....private_eye.heidelberg.parser.file_parser import SegmentBody
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr

logger = logging.getLogger(__name__)

_max_float32: np.single = np.finfo(np.float32).max

CONTOUR_MAP = {
    0: RetinalLayer.ILM,
    1: RetinalLayer.BM,
    2: RetinalLayer.RNFL,
    3: RetinalLayer.GCL,
    4: RetinalLayer.IPL,
    5: RetinalLayer.INL,
    6: RetinalLayer.OPL,
    8: RetinalLayer.ELM,
    14: RetinalLayer.E,
    15: RetinalLayer.OS,
    16: RetinalLayer.RPE,
}


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ContourSegment(SegmentBody):
    id: int
    layer_name: str
    data: np.ndarray = attr.ib(repr=False, eq=False)
    mystery_1: int
    mystery_2: int


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ContourSegmentOld(SegmentBody):
    size: int
    first_width: int
    second_width: int
    header_type: int
    data: List[int]
    mystery: int


@segment_body_parser(types=[0x2723], targets=[ContourSegment])
def contour(stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions) -> ContourSegment:
    mystery_1 = stream.read_int()
    contour_id = stream.read_int()
    layer_name = CONTOUR_MAP.get(contour_id, f"Unknown({contour_id})")
    mystery_2 = stream.read_int()
    width = stream.read_int()
    stream.skip(20)
    data = np.frombuffer(stream.read_bytes(width * 4), dtype=np.float32)
    data = np.where(data == _max_float32, np.NaN, data)
    return ContourSegment(contour_id, layer_name, data, mystery_1, mystery_2)


@segment_body_parser(types=[0x40002710, 0x40002711, 0x40002712], targets=[ContourSegmentOld])
def contour_old(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> ContourSegmentOld:
    # TODO RIPF-235 Work out the meaning of these types
    header_type = header.type - 0x40002710

    size = stream.read_int()
    # This could be a type, see e.g. the type parsing code in image.py
    mystery = stream.read_int()

    # These two widths are the same for all the OCTs which we've tested in which case the
    # data length is the width, but they differ for other scan types, e.g. some FA images,
    # see integration tests.  We don't know how to interpret this if they differ.
    width_1 = stream.read_int()
    width_2 = stream.read_int()

    if width_1 != width_2:
        logger.info("Contour widths don't match, not returning any contours")
        return ContourSegmentOld(size, width_1, width_2, header_type, [], mystery)

    data = stream.read_ints(width_2)
    return ContourSegmentOld(size, width_1, width_2, header_type, data, mystery)
