import os
from datetime import date
from typing import Optional

import attr
from .....private_eye import ParserOptions
from .....private_eye.exceptions import ImageParseException
from .....private_eye.heidelberg.heidelberg_utils import is_heidelberg_dob_fix_enabled
from .....private_eye.heidelberg.parser.file_parser import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr
from .....private_eye.utils.optional import map_optional


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class PatientSegment(SegmentBody):
    given_name: str
    surname: str
    title: Optional[str]
    birthdate: date
    sex: Optional[str]
    patient_key: Optional[str]
    physician: Optional[int]
    ancestry: Optional[int]


@segment_body_parser(types=[0x9], targets=[PatientSegment])
def patient_info(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> PatientSegment:
    given_name: str = stream.read_mandatory_ascii(31)
    surname: str = stream.read_mandatory_ascii(51)

    title: Optional[str]
    birthdate: date
    if is_heidelberg_dob_fix_enabled():
        title = stream.read_optional_ascii(11)
        birthdate = stream.read_datetime()
    else:
        title = stream.read_optional_ascii(15)
        birthdate = stream.read_datetime()

    sex: Optional[str] = map_optional(stream.read_optional_byte(), chr)
    patient_key: Optional[str] = stream.read_optional_ascii(21)

    physician: Optional[int] = stream.read_optional_int()  # As mapped by the HRPhysician table
    ancestry: Optional[int] = stream.read_optional_int()  # As mapped by the HRAncestry table

    if sex not in ["M", "F", None]:
        raise ImageParseException(f"Unknown patient sex: {sex}")

    return PatientSegment(given_name, surname, title, birthdate, sex, patient_key, physician, ancestry)
