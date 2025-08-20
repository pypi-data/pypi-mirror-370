import logging
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, Iterable, List, Type

from ....private_eye import ParserOptions
from ....private_eye.exceptions import ImageParseException
from ....private_eye.heidelberg.data import Segment, SegmentBody
from ....private_eye.heidelberg.parser.segment.binary import binary_parser
from ....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper

Parser = Callable[[HeidelbergStreamWrapper, Segment.Header, ParserOptions], Any]
_segment_body_parsers_by_type: Dict[int, Parser] = {}
_segment_types_by_target: DefaultDict[Type[SegmentBody], List[int]] = defaultdict(list)

logger = logging.getLogger(__name__)


def segment_body_parser(types: List[int], targets: Iterable[Type[SegmentBody]]) -> Callable[[Callable], None]:
    def decorator(func: Callable) -> None:
        for segment_type in types:
            if segment_type in _segment_body_parsers_by_type:
                raise ValueError("You can only register one parser for each segment type")
            _segment_body_parsers_by_type[segment_type] = func

        for target in targets:
            _segment_types_by_target[target].extend(types)

    return decorator


def parse_segment(fs: HeidelbergStreamWrapper, expected_type: int, parser_options: ParserOptions) -> Segment:
    header = fs.read_segment_header()
    start = fs.tell()

    if header.type != expected_type:
        raise ImageParseException("Segment header type doesn't match type from directory header")

    try:
        # The header itself is 0x3C bytes long
        segment_body_parser = _segment_body_parsers_by_type[header.type]
    except KeyError:
        logger.info("Segment type not recognised by any parsers: %X", header.type)
        segment_body_parser = binary_parser

    # Use a substream to ensure that we don't read past the end of a segment
    segment_body = segment_body_parser(fs.get_substream(header.size), header, parser_options)
    logger.debug("Parsed segment body: %s", segment_body)

    end = fs.tell()
    logger.debug("%s %s %s", start, end - start, header.size)
    if end - start != header.size:
        logger.debug(
            "Body parser %s (type: %s) read the wrong number of characters: %s, expected %s",
            segment_body_parser.__name__,
            header.type,
            end - start,
            header.size,
        )

    return Segment(header, segment_body)
