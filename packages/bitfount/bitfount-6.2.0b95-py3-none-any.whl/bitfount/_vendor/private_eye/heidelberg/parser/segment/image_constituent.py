from io import BytesIO
from typing import Optional

import attr
from PIL import Image
from .....private_eye import ParserOptions
from .....private_eye.heidelberg.data import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ImageThumbnail(SegmentBody):
    type: int
    mystery_1: int
    mystery_2: int
    data: Optional[Image.Image]


@segment_body_parser(types=[0x2], targets=[ImageThumbnail])
def parse_image_constituent(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> ImageThumbnail:
    # int length
    # int type eg. 01010202 (like TYPE_FUNDUS)
    # ?
    # ?
    # JFIF / JPEG
    length = stream.read_int()
    image_type = stream.read_int()
    mystery_1 = stream.read_int()
    mystery_2 = stream.read_int()
    img_length = length - 16
    if parser_options.skip_image_data:
        stream.skip(img_length)
        data = None
    else:
        image_bytes = stream.read(img_length)
        data = Image.open(BytesIO(image_bytes))

    return ImageThumbnail(image_type, mystery_1, mystery_2, data)
