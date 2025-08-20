from datetime import datetime

import attr
from .....private_eye import ParserOptions
from .....private_eye.heidelberg.data import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment_parser import HeidelbergStreamWrapper, segment_body_parser
from .....private_eye.utils.attrs import hex_repr
from .....private_eye.utils.oletime import from_oletime


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ExamInfo3A(SegmentBody):
    exam_timestamp: datetime


@segment_body_parser(types=[0x3A], targets=[ExamInfo3A])
def parser_3a(stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions) -> ExamInfo3A:
    # TODO RIPF-222 Investigate
    stream.read(6)
    exam_timestamp = from_oletime(stream.read_double())
    return ExamInfo3A(exam_timestamp=exam_timestamp)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ExamInfoA(SegmentBody):
    exam_timestamp: datetime


@segment_body_parser(types=[0xA], targets=[ExamInfoA])
def parser_a(stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions) -> ExamInfoA:
    # TODO RIPF-222 Investigate
    stream.read(6)
    exam_timestamp = from_oletime(stream.read_double())
    return ExamInfoA(exam_timestamp=exam_timestamp)
