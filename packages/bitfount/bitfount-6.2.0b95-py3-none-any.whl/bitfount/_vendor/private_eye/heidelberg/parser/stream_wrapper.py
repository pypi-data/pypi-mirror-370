import logging
import struct
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from jdcal import jd2gcal

from ....private_eye.heidelberg.heidelberg_utils import (
    is_heidelberg_dob_fix_enabled, ushort_to_unsigned_half,
)

from ...common.file_stream_wrapper import FileStreamWrapper
from ..data import DirectoryHeader, NodeReference, Segment, StandardMetadata

EXPECTED_VERSION = 0x64

NULL_FLOAT = struct.unpack("<f", b"\xFF\xFF\x7F\x7F")[0]
NULL_BYTE = 0xFF
NULL_SHORT = 0xFFFF
NULL_INT = 0xFFFFFFFF
NULL_ASCII = ""


logger = logging.getLogger(__name__)


class HeidelbergStreamWrapper(FileStreamWrapper["HeidelbergStreamWrapper"]):
    def read_version(self, version: int) -> None:
        parsed_version = self.read_int()
        if parsed_version != version:
            self._fail(f"Unexpected version: {parsed_version:x}")

    def read_null_int(self) -> None:
        i = self.read_int()
        if i != 0:
            self._fail(f"Unexpected non-null int: {i:x}")

    def read_null_short(self) -> None:
        i = self.read_short()
        if i != 0:
            self._fail(f"Unexpected non-null short: {i:x}")

    def read_null_byte(self) -> None:
        i = self.read_byte()
        if i != 0:
            self._fail(f"Unexpected non-null byte: {i:x}")

    def read_magic_header(self, expected_magic_string: str) -> None:
        magic = self.read_ascii(12)

        if magic != expected_magic_string:
            self._fail(f"Incorrect magic string: {magic}")

    def read_optional_int(self) -> Optional[int]:
        ret = self.read_int()
        return ret if ret != NULL_INT else None

    def read_optional_short(self) -> Optional[int]:
        ret = super().read_short()
        return ret if ret != NULL_SHORT else None

    def read_optional_float(self) -> Optional[float]:
        ret = super().read_float()
        return ret if ret != NULL_FLOAT else None

    def read_optional_byte(self) -> Optional[int]:
        ret = super().read_byte()
        return ret if ret != NULL_BYTE else None

    def read_optional_ascii(self, length: int) -> Optional[str]:
        ret = self.read_ascii(length)
        return ret if ret != NULL_ASCII else None

    def read_mandatory_ascii(self, length: int) -> str:
        ret = self.read_ascii(length)
        if ret == NULL_ASCII:
            raise ValueError("Read null string where mandatory string expected")
        return ret

    def read_datetime(self) -> date:
        if is_heidelberg_dob_fix_enabled():
            serial = self.read_double()
            return date(1899, 12, 30) + timedelta(days=serial)
        else:
            gcal = jd2gcal((float(self.read_int()) / 64) - 14558805, 0)
            return date(gcal[0], gcal[1], gcal[2])

    def read_utf16_le(self, length: int) -> str:
        return self.read_string(length, "utf-16-le")

    def read_var_utf16_le(self) -> str:
        char = self.read(2)
        buffer: List[str] = []
        while char != b"\0\0":
            buffer.append(char.decode("utf-16-le", errors=self._options.on_string_decode_error))
            char = self.read(2)
        return "".join(buffer)

    def read_unsigned_half(self) -> float:
        return ushort_to_unsigned_half(self.read_short())

    def warn_if_unexpected(self, expected_bytes: bytes, header: Segment.Header) -> bytes:
        length = len(expected_bytes)
        val = self.read(length)
        if val != expected_bytes:
            logger.warning(
                "Expected 0x%s but got 0x%s at offset 0x%02x of type 0x%02x",
                expected_bytes.hex(),
                val.hex(),
                self.tell() - length,
                header.type,
            )
        return val

    def read_msft_filetime(self) -> datetime:
        filetime = struct.unpack("<Q", self.read_bytes(8))[0]
        epoch_as_filetime = 116444736_000_000_000  # January 1, 1970 as MS file time
        hundreds_of_nanoseconds = 10_000_000
        return datetime.utcfromtimestamp((filetime - epoch_as_filetime) / hundreds_of_nanoseconds)

    def read_file_header(self) -> StandardMetadata:
        self.read_magic_header("CMDb")
        self.read_version(EXPECTED_VERSION)

        return self.read_standard_metadata()

    def read_main_header(self) -> Tuple[StandardMetadata, NodeReference]:
        self.read_magic_header("MDbMDir")
        self.read_version(EXPECTED_VERSION)
        standard_metadata = self.read_standard_metadata()
        node_reference = self.read_node_reference()

        return standard_metadata, node_reference

    def read_directory_header(self) -> Tuple[StandardMetadata, DirectoryHeader]:
        self.read_magic_header("MDbDir")
        self.read_version(EXPECTED_VERSION)
        standard_metadata = self.read_standard_metadata()
        node_reference = self.read_node_reference()
        segments = [self.read_directory_entry() for _ in range(node_reference.num_entries)]

        return standard_metadata, DirectoryHeader(node_reference, [s for s in segments if not s.is_empty])

    def read_node_reference(self) -> NodeReference:
        num_entries = self.read_int()
        current = self.read_int()
        previous = self.read_int()
        mystery = self.read_optional_int()

        return NodeReference(num_entries=num_entries, current=current, previous=previous, mystery=mystery)

    def read_standard_metadata(self) -> StandardMetadata:
        patient = self.read_optional_int()
        study = self.read_optional_int()
        series = self.read_optional_int()
        slice_id = self.read_optional_int()
        ind = self.read_optional_short()
        mystery_1 = self.read_short()

        return StandardMetadata(patient, study, series, slice_id, ind, mystery_1)

    def read_directory_entry(self) -> DirectoryHeader.Segment:
        position = self.read_int()  # This is the chunks own position in the file
        start = self.read_int()
        size = self.read_int()
        mystery_1 = self.read_int()
        standard_metadata = self.read_standard_metadata()
        segment_type = self.read_int()
        mystery_2 = self.read_int()  # This appears to be some sort of global offset

        return DirectoryHeader.Segment(
            position=position,
            start=start,
            size=size,
            standard_metadata=standard_metadata,
            mystery_1=mystery_1,
            type=segment_type,
            mystery_2=mystery_2,
        )

    def read_segment_header(self) -> Segment.Header:
        """0x3C bytes long"""
        self.read_magic_header("MDbData")
        mystery_1 = self.read_optional_int()
        mystery_2 = self.read_optional_int()
        position = self.read_int()
        size = self.read_int()
        self.read_null_int()
        standard_metadata = self.read_standard_metadata()
        segment_type = self.read_int()
        mystery_3 = self.read_optional_int()

        return Segment.Header(position, size, standard_metadata, segment_type, mystery_1, mystery_2, mystery_3)
