from typing import Optional, Set, Tuple

import attr
from .....private_eye import ParserOptions
from .....private_eye.exceptions import ImageParseException
from .....private_eye.heidelberg.data import Segment, SegmentBody, StandardMetadata
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class PatientInfo1FSegment(SegmentBody):
    pass


@segment_body_parser(types=[0x1F], targets=[PatientInfo1FSegment])
def parse_1f(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> PatientInfo1FSegment:
    """
    Only seen this in the pdb file and almost always containing nothing but null bytes.  Once seen a single
    letter U in the middle of a sea of null bytes.
    """
    return PatientInfo1FSegment()


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class PatientInfo2332Segment(SegmentBody):
    mystery: Optional[int]
    location: str
    first_records: Set[StandardMetadata] = attr.ib(default=None, eq=False)  # Not yet using this data, so don't compare.
    second_records: Set[Tuple[Optional[int], StandardMetadata]] = attr.ib(
        default=None, eq=False
    )  # Not yet using this data, so don't compare.


@segment_body_parser(types=[0x2332], targets=[PatientInfo2332Segment])
def parse_2332(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> PatientInfo2332Segment:
    """
    Only seen this in the PDB file, I can't decode most of the header, but did manage to decode what looks like a huge
    chunk of StandardMetadata entries.  I don't have a use for them yet though.
    """
    mystery = stream.read_optional_int()

    location = stream.read_string(0x8, "utf-16-le")

    # I've not been able to decode any of this, or the initial integer
    stream.skip(0xF8)

    # These lists of records are basically the standard metadata
    number_of_records = stream.read_int()
    first_records = []
    for _ in range(number_of_records):
        patient_id = stream.read_int()
        exam_id = stream.read_optional_int()
        series_id = stream.read_optional_int()
        slice_id = stream.read_optional_int()
        ind = stream.read_short()

        first_records.append(StandardMetadata(patient_id, exam_id, series_id, slice_id, ind))

    second_records = []
    for _ in range(number_of_records):
        record_mystery = stream.read_optional_int()
        patient_id = stream.read_int()
        exam_id = stream.read_optional_int()
        series_id = stream.read_optional_int()
        slice_id = stream.read_optional_int()
        ind = stream.read_short()

        second_records.append((record_mystery, StandardMetadata(patient_id, exam_id, series_id, slice_id, ind)))

    first_records_as_set = set(first_records)
    if len(first_records) != len(first_records_as_set):
        raise ImageParseException("PatientInfo2332Segment contains duplicate records in first record batch")

    second_records_as_set = set(second_records)
    if len(second_records) != len(second_records_as_set):
        raise ImageParseException("PatientInfo2332Segment contains duplicate records in second record batch")

    return PatientInfo2332Segment(mystery, location, first_records_as_set, second_records_as_set)
