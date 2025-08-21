import struct
import warnings
from typing import Generic, List, NoReturn, Optional, TypeVar, cast
from uuid import UUID

import numpy as np

from ..data import ParserOptions, PointF
from ..exceptions import ImageParseException, StreamLengthError
from .substream import StreamBase, SubStream

TWrapperType = TypeVar("TWrapperType", bound="FileStreamWrapper")


# TODO RIPF-301 Tidy this up and look into overwriting io.BufferedReader
class FileStreamWrapper(Generic[TWrapperType]):
    def __init__(self, fs: StreamBase, options: ParserOptions) -> None:
        self._fs = fs
        self._options = options

    def read(self, length: int = -1) -> bytes:
        return self._fs.read(length)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._fs.seek(offset, whence)

    def skip(self, length: int) -> int:
        return self._fs.seek(length, 1)

    def pos(self) -> int:
        warnings.warn("""Use 'tell' instead to match python IO""", category=DeprecationWarning, stacklevel=2)
        return self._fs.tell()

    def tell(self) -> int:
        return self._fs.tell()

    def read_ascii(self, length: int) -> str:
        return self.read_string(length, "ascii")

    def read_string(self, length: int, encoding: str) -> str:
        return self.read(length).decode(encoding, errors=self._options.on_string_decode_error).split("\0")[0]

    def read_null_terminated_string(self, encoding: str) -> str:
        raw_string = bytearray()
        while True:
            next_byte = self.read_byte()
            if next_byte == 0:
                break
            raw_string.append(next_byte)
        return raw_string.decode(encoding, errors=self._options.on_string_decode_error)

    def read_short(self) -> int:
        return self._unpack_int("<H", 2)

    def read_short_signed(self) -> int:
        return self._unpack_int("<h", 2)

    def read_int(self) -> int:
        return self._unpack_int("<I", 4)

    def read_int_signed(self) -> int:
        return self._unpack_int("<i", 4)

    def read_ints(self, num: int) -> List[int]:
        if num == 0:
            return []
        return list(struct.unpack(f"<{num}I", self._read_at_least(4 * num)))

    def read_byte(self) -> int:
        return ord(self._read_at_least(1))

    def read_byte_list(self, length: int) -> List[int]:
        return [self.read_byte() for _ in range(length)]

    def read_byte_signed(self) -> int:
        return self._unpack_int("<b", 1)

    def read_bytes(self, num: int) -> bytes:
        return self._fs.read(num)

    def read_double(self) -> float:
        return self._unpack_float("<d", 8)

    def read_float(self) -> float:
        return self._unpack_float("<f", 4)

    def read_float_list(self, length: int) -> List[float]:
        return [self.read_float() for _ in range(length)]

    def read_short_float(self) -> np.float16:
        raw_bytes = self.read_bytes(2)
        return cast(np.float16, np.frombuffer(raw_bytes, dtype=np.float16)[0])

    def read_point_f(self) -> PointF:
        return PointF(self.read_float(), self.read_float())

    def read_uuid(self) -> UUID:
        return UUID(bytes=self.read_bytes(16))

    def read_data(self, length: int = -1) -> bytes:
        return self.read(length)

    def read_data_list(self, size: int) -> List[bytes]:
        ret = []
        for _ in range(size):
            ret.append(self.read_data(self.read_int()))
        return ret

    def read_data_or_skip(self, length: int = -1) -> Optional[bytes]:
        if self._options.skip_image_data:
            if length != -1:
                self.skip(length)
            return None
        return self.read_data(length)

    def expect_int(self, expected_int: int) -> None:
        ret = self.read_int()
        if ret != expected_int:
            self._fail(f"Expected {expected_int} but got {ret}")

    def expect_short(self, expected_short: int) -> None:
        ret = self.read_short()
        if ret != expected_short:
            self._fail(f"Expected {expected_short} but got {ret}")

    def expect_bytes(self, expected_bytes: List[int]) -> None:
        ret = [self.read_byte() for i in expected_bytes]
        if ret != expected_bytes:
            self._fail(f"Expected {expected_bytes} but got {ret}")

    def expect_float(self, expected_float: float) -> None:
        ret = self.read_float()
        if ret != expected_float:
            self._fail(f"Expected {expected_float} but got {ret}")

    def expect_ascii_string(self, expected_ascii_string: str) -> None:
        ret = self.read_ascii(len(expected_ascii_string))
        if ret != expected_ascii_string:
            self._fail(f"Expected {expected_ascii_string} but got {ret}")

    def expect_null_bytes(self, length: int) -> None:
        ret = self.read_bytes(length)
        if any(b != 0 for b in ret):
            self._fail(f"Expected null bytes but got {ret!r}")

    def get_substream(self, length: int, offset: Optional[int] = None, invisible: bool = False) -> TWrapperType:
        if offset is None:
            offset = self.tell()
        substream = SubStream(self._fs, offset, length, invisible)
        # Note: we assume that all subclasses of this class have the same constructor
        return cast(TWrapperType, self.__class__(substream, self._options))

    def _fail(self, message: str) -> NoReturn:
        position = self.tell()
        raise ImageParseException(f"[{position} | 0x{position:x}] {message}")

    def _unpack_int(self, sig: str, length: int) -> int:
        return cast(int, struct.unpack(sig, self._read_at_least(length))[0])

    def _unpack_float(self, sig: str, length: int) -> float:
        return cast(float, struct.unpack(sig, self._read_at_least(length))[0])

    def _read_at_least(self, min_length: int) -> bytes:
        data = self._fs.read(min_length)
        actual_length = len(data)
        if actual_length < min_length:
            raise StreamLengthError(f"At least {min_length} bytes required; {actual_length} bytes read.")
        return data
