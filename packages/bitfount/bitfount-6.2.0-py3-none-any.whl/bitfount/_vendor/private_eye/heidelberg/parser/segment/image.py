import logging
from typing import Optional, Union, cast

import attr
from .....private_eye import ParserOptions
from .....private_eye.heidelberg.data import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr

# the type is a 4-byte number of which the second byte indicates fundus image or tomogram.
TYPE_FUNDUS = 0x01
TYPE_TOMOGRAM = 0x20

logger = logging.getLogger(__name__)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class PhotoImageSegment(SegmentBody):
    size: int
    type: int
    width: int
    height: int
    data: Optional[bytes]
    pixel_count: Optional[int] = attr.ib(default=None, eq=False)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class BScanImageSegment(SegmentBody):
    size: int
    type: int
    width: int
    height: int
    data: Optional[bytes]
    pixel_count: Optional[int] = attr.ib(default=None, eq=False)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class UnknownImageSegment(SegmentBody):
    size: int
    type: Optional[int]
    width: int
    height: int
    pixel_count: Optional[int] = attr.ib(default=None, eq=False)


@segment_body_parser(
    types=[0x40000000, 0x4000271A, 0x4000271B],
    targets=[PhotoImageSegment, BScanImageSegment, UnknownImageSegment],
)
def parse(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> Union[PhotoImageSegment, BScanImageSegment, UnknownImageSegment]:
    size = stream.read_int()  # Size of this segment including this int

    # the first byte of this appears to indicate whether the image is visible in the Eye Explorer
    # the second byte indicates image type, with fundus (0x01) and tomogram (0x20) identified so far
    # the third and fourth bytes are always 0x0201, meaning unknown
    img_type = stream.read_optional_int()
    pixel_count = stream.read_optional_int()
    height = stream.read_int()
    width = stream.read_int()

    if img_type is not None and img_type & 0xFFFF != 0x0201:
        logger.warning("Unexpected magic number in img_type: %s", hex(img_type))
        return UnknownImageSegment(size, img_type, width, height, pixel_count)

    def _match_type(segment_type: Optional[int], target_type: int) -> bool:
        return segment_type is not None and ((segment_type >> 16) & 0xFF) == target_type

    if _match_type(img_type, TYPE_FUNDUS):
        bytes_to_read = width * height
        if size != bytes_to_read + 20:
            logger.warning("Unexpected image size: %s for image with dimensions %sx%s", size, width, height)
            return UnknownImageSegment(size, img_type, width, height, pixel_count)
        image_bytes = stream.read_data_or_skip(bytes_to_read)
        return PhotoImageSegment(
            size,
            cast(int, img_type),
            width,
            height,
            image_bytes,
            pixel_count,
        )

    if _match_type(img_type, TYPE_TOMOGRAM):
        bytes_to_read = width * height * 2
        if size != bytes_to_read + 20:
            logger.warning("Unexpected image size: %s for image with dimensions %sx%s", size, width, height)
            return UnknownImageSegment(size, img_type, width, height, pixel_count)

        image_bytes = stream.read_data_or_skip(bytes_to_read)
        return BScanImageSegment(
            size=size, type=cast(int, img_type), width=width, height=height, data=image_bytes, pixel_count=pixel_count
        )

    logger.warning("Unable to parse image.  Type: 0x%X  ind: %x", img_type, header.standard_metadata.ind)
    return UnknownImageSegment(size, img_type, width, height, pixel_count)
