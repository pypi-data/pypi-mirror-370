from typing import Optional

import attr
from .....private_eye import ParserOptions

from ....consts import Laterality
from ....utils.attrs import hex_repr
from ...data import Segment, SegmentBody
from ...parser.segment_parser import HeidelbergStreamWrapper, segment_body_parser
from .segment_utils import parse_laterality


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class EyeDataSegment(SegmentBody):
    laterality: Laterality
    c_curve: Optional[float]
    refraction: Optional[float]
    cylinder: Optional[float]
    axis: Optional[float]
    pupil_size: Optional[float]
    iop: Optional[float]
    v_field_mean: Optional[float]
    v_field_var: Optional[float]
    # 0 - None, 1 - Glasses, 2 - Hard Contact Lenses, 3 - Soft contact lenses
    corrective_lens: Optional[int]


@segment_body_parser(types=[0x7], targets=[EyeDataSegment])
def parse_eye_data(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> EyeDataSegment:
    return EyeDataSegment(
        laterality=parse_laterality(stream.read_ascii(1)),
        iop=stream.read_double(),
        refraction=stream.read_double(),
        c_curve=stream.read_double(),
        v_field_mean=stream.read_double(),
        v_field_var=stream.read_double(),
        cylinder=stream.read_double(),
        axis=stream.read_double(),
        corrective_lens=stream.read_short(),
        pupil_size=stream.read_double(),
    )
