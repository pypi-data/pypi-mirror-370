import attr

from ...data import DirectoryHeader, Segment, SegmentBody


@attr.s(auto_attribs=True, frozen=True)
class SmallSegmentBody(SegmentBody):
    value: int


def parse_small_segment(header_segment: DirectoryHeader.Segment) -> Segment[SmallSegmentBody]:
    return Segment(
        header=Segment.Header(
            position=header_segment.position,
            size=header_segment.size,
            standard_metadata=header_segment.standard_metadata,
            type=header_segment.type,
        ),
        body=SmallSegmentBody(header_segment.start),
    )
