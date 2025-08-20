import attr
from .....private_eye import ParserOptions
from .....private_eye.heidelberg.data import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr

_types = {0x34: "patient", 0x35: "exam", 0x36: "series"}


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class UIDSegment(SegmentBody):
    type: str
    uid: str


@segment_body_parser(types=[0x34, 0x35, 0x36], targets=[UIDSegment])
def parse_uid_segment(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> UIDSegment:
    """
    Only seen this in the pdb file.  Contains something which looks like an OID assigned to Heidelberg, but with a
    curious prefix.  Eg.

    LOC13092244.1.3.6.1.4.1.33437.10.7.832020.13131124719.32655.7
    | Prefix   | Heidelberg-assigned OID

    The patient type appears in the Access DB, in the HRPatientUIDs table which matches these UIDs to the Patient ID.
    """
    id_type = _types[header.type]
    return UIDSegment(id_type, stream.read_ascii(header.size))
