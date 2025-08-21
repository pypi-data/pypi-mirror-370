import attr
from .....private_eye import ParserOptions

from ...data import Segment, SegmentBody
from ..stream_wrapper import HeidelbergStreamWrapper


@attr.s(auto_attribs=True, frozen=True)
class BinarySegmentBody(SegmentBody):
    value: bytes = attr.ib(repr=False)


def binary_parser(
    fs: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> BinarySegmentBody:
    return BinarySegmentBody(fs.read(header.size))
