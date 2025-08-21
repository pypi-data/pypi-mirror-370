import struct
from datetime import date, datetime
from typing import Optional

from ..common.file_stream_wrapper import FileStreamWrapper


class TopconStreamWrapper(FileStreamWrapper["TopconStreamWrapper"]):
    def read_topcon_string(self, length: int) -> str:
        return self.read_string(length, self._options.topcon_encoding)

    def read_datetime(self, can_return_none: bool = False) -> Optional[datetime]:
        try:
            return parse_datetime(self._read_at_least(12))
        except ValueError:
            if can_return_none:
                return None
            raise

    def read_date(self, can_return_none: bool = False) -> Optional[date]:
        try:
            return parse_date(self._read_at_least(6))
        except ValueError:
            if can_return_none:
                return None
            raise


def parse_datetime(as_bytes: bytes) -> datetime:
    # FDA Datetimes are stored as YYMMddHHmmss
    parts = struct.unpack("<6H", as_bytes)
    return datetime(*parts)


def parse_date(as_bytes: bytes) -> date:
    parts = struct.unpack("<3H", as_bytes)
    return date(*parts)
