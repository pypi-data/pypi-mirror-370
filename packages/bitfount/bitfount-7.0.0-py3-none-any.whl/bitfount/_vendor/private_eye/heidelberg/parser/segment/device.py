import attr
from .....private_eye import ParserOptions
from .....private_eye.heidelberg.parser.file_parser import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class DeviceSegment(SegmentBody):
    camera_model: str
    mystery0: str
    mystery1: int
    mystery2: int


@segment_body_parser(types=[0xD], targets=[DeviceSegment])
def device(stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions) -> DeviceSegment:
    """
    You can see the Camera Model field in the Heidelberg Explorer, when looking at the detailed information of a single
    image.

    For mystery0 I've seen OCT and HRA
    """
    mystery0 = stream.read_utf16_le(0x40)
    camera_model = stream.read_utf16_le(0x80)
    mystery1 = stream.read_int()
    mystery2 = stream.read_int()

    return DeviceSegment(camera_model, mystery0, mystery1, mystery2)
