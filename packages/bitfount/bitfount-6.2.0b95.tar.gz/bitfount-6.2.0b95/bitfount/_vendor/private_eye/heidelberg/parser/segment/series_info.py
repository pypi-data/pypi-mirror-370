from typing import Optional

import attr
from .....private_eye import ParserOptions
from .....private_eye.consts import Laterality
from .....private_eye.heidelberg.hr import HrExamType, get_exam_struct, get_exam_type, get_series_type
from .....private_eye.heidelberg.parser.file_parser import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment.segment_utils import parse_laterality
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class SeriesInfoSegment(SegmentBody):
    series_type: Optional[str]
    exam_type_1: Optional[HrExamType]
    exam_type_2: Optional[HrExamType]
    number_of_pictures: int
    laterality: Laterality
    exam_structure: Optional[str]
    group_id: int
    archive_disk: int
    archive_start_number: int


# We don't yet know what the exact difference between 0xB and 0x3B is, except that some images have one type and others
# have the other.
@segment_body_parser(types=[0xB, 0x3B], targets=[SeriesInfoSegment])
def parse_series_info(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> SeriesInfoSegment:
    return SeriesInfoSegment(
        series_type=get_series_type(stream.read_int()),
        exam_type_1=get_exam_type(stream.read_int()),
        exam_type_2=get_exam_type(stream.read_int()),
        number_of_pictures=stream.read_short(),
        laterality=parse_laterality(stream.read_ascii(1)),
        exam_structure=get_exam_struct(stream.read_int()),
        group_id=stream.read_int_signed(),
        archive_disk=stream.read_short(),
        archive_start_number=stream.read_short_signed(),
    )
