import logging
from datetime import date
from typing import Any, Callable, Dict, Tuple

from ...private_eye.common.file_stream_wrapper import FileStreamWrapper

logger = logging.getLogger(__name__)


class SectionTerminateException(Exception):
    pass


def _read_and_pass_trailing_zeroes(minimum: int) -> Callable[[FileStreamWrapper], str]:
    def parser(_fs: FileStreamWrapper) -> str:
        ret = _fs.read_ascii(minimum)
        next_byte = _fs.read_byte()
        while next_byte == 0:
            next_byte = _fs.read_byte()
        _fs.seek(-1, 1)
        return ret

    return parser


def _read_section_with_length_header() -> Callable[[FileStreamWrapper], bytes]:
    def parser(_fs: FileStreamWrapper) -> bytes:
        length = _fs.read_short()
        ret = _fs.read(length)
        return ret

    return parser


def _read_date() -> Callable[[FileStreamWrapper], date]:
    def parser(_fs: FileStreamWrapper) -> date:
        day = int(_fs.read_ascii(2))
        month = int(_fs.read_ascii(2))
        year = int(_fs.read_ascii(4))
        _fs.read(20)  # we don't know what this means but it comes after the date. Possibly a time encoding.
        return date(year, month, day)

    return parser


def _read_supplementary_sequence(
    sequence_length: int,
) -> Callable[[FileStreamWrapper], Dict[Tuple[int, int], Tuple[int, int]]]:
    def read_supplementary_test_point_sequence(fs: FileStreamWrapper) -> Dict[Tuple[int, int], Tuple[int, int]]:
        def read_supplementary_test_point() -> Tuple[Tuple[int, int], Tuple[int, int]]:
            x_coord = fs.read_byte_signed()
            y_coord = fs.read_byte_signed()
            byte1 = fs.read_byte()
            byte2 = fs.read_byte()
            return (x_coord, y_coord), (byte1, byte2)

        return dict(read_supplementary_test_point() for _ in range(sequence_length))

    return read_supplementary_test_point_sequence


def _terminate() -> Callable[[FileStreamWrapper], None]:
    def terminate(_fs: FileStreamWrapper) -> None:
        raise SectionTerminateException

    return terminate


def _read_long_header(header_start: str) -> Callable[[FileStreamWrapper], Dict[str, Any]]:
    def read_long_header(fs: FileStreamWrapper) -> Dict[str, Any]:
        long_read_methods = {
            "DNAM": _read_and_pass_trailing_zeroes(64),
            "DID1": _read_and_pass_trailing_zeroes(64),
            "DID2": _read_and_pass_trailing_zeroes(64),
            "DISS": _read_and_pass_trailing_zeroes(64),
            "DGEN": _read_and_pass_trailing_zeroes(16),
            "DACC": _read_and_pass_trailing_zeroes(16),
            "DORD": _read_and_pass_trailing_zeroes(64),
            "StID": _read_and_pass_trailing_zeroes(64),
            "SeID": _read_and_pass_trailing_zeroes(64),
            "STAT": lambda x: {"stat_1": x.read_ascii(17), "stat_2": x.read_ascii(17), "stat_3": x.read_ascii(17)},
        }

        full_header = header_start + fs.read_ascii(2)

        return {"full_header": full_header, "value": long_read_methods[full_header](fs)}

    return read_long_header


def _read_metadata_field(fs: FileStreamWrapper, sequence_length: int) -> Tuple[str, Any]:
    read_methods = {
        "SN": _read_and_pass_trailing_zeroes(28),
        "DP": _read_and_pass_trailing_zeroes(1),
        "MS": _read_and_pass_trailing_zeroes(2),
        "GZ": _read_section_with_length_header(),
        "DC": _read_and_pass_trailing_zeroes(15),
        "PC": _read_and_pass_trailing_zeroes(15),
        "AD": _read_and_pass_trailing_zeroes(1),
        "CM": _read_and_pass_trailing_zeroes(81),
        "CD": _read_and_pass_trailing_zeroes(2),
        "IP": _read_and_pass_trailing_zeroes(1),
        "SV": _read_and_pass_trailing_zeroes(12),
        "FX": _read_and_pass_trailing_zeroes(15),
        "RD": _read_date(),
        "PF": _read_and_pass_trailing_zeroes(64),
        "WO": lambda x: x.read_int(),
        "WI": lambda x: x.read_int(),
        "DN": _read_long_header("DN"),
        "DI": _read_long_header("DI"),
        "DG": _read_long_header("DG"),
        "DA": _read_long_header("DA"),
        "DO": _read_long_header("DO"),
        "St": _read_long_header("St"),
        "Se": _read_long_header("Se"),
        "ST": _read_long_header("ST"),
        "SD": _read_supplementary_sequence(sequence_length),
        # The 'GN' subsection comes at the end of this section in all RAW OPV files tested so far. It sometimes
        # contains eight bytes of illegible data.
        "GN": _terminate(),
    }

    friendly_header_names = {
        "SN": "Scanner Serial Number",
        "SV": "Software Version",
        "RD": "Date",
        "DNAM": "Patient Name",
        "DID1": "Patient ID 1",
        "DID2": "Patient ID 2",
        "DISS": "Patient ID Issuer",
        "DGEN": "Sex",
        "StID": "Study Instance ID",
        "SeID": "Series Instance ID",
    }

    field_header = fs.read_ascii(2)
    field_value = read_methods[field_header](fs)

    if isinstance(field_value, Dict) and "full_header" in field_value:
        field_header = field_value["full_header"]
        field_value = field_value["value"]

    field_header = friendly_header_names.get(field_header, field_header)

    return field_header, field_value


def read_metadata(fs: FileStreamWrapper, sequence_length: int) -> Dict[str, Any]:
    metadata = {}
    # this field typically appears after a byte of 229, 235 or 247, but in one observed file that byte is 0
    if fs.read_byte() in [229, 235, 247, 0]:
        metadata["mystery_7"] = fs.read(54)
    else:
        fs.seek(-1, 1)

    try:
        while True:
            try:
                key, value = _read_metadata_field(fs, sequence_length)

                metadata[key] = value
            except SectionTerminateException:
                break
    except Exception:  # pylint: disable=broad-except
        # we don't use the metadata anywhere, so errors shouldn't stop export of the important data
        logger.warning("Error parsing metadata, returning empty metadata.", exc_info=True)

    return metadata
