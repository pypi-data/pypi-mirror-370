import array
import io
import mmap
from typing import BinaryIO, Union


class SubStream(io.RawIOBase):
    """
    Wrapper around a RawIOBase-like object which acts like a sub-stream
    with its own internal position.

    Note: any seeking and reading actions will affect the base IO object
    """

    def __init__(self, fs: "StreamBase", start: int, length: int, invisible: bool = False) -> None:
        super().__init__()
        self.fs = fs
        self.start = start
        self.length = length
        self.pos = 0
        self._invisible = invisible

    def seek(self, offset: int, origin: int = io.SEEK_SET) -> int:
        if origin == io.SEEK_SET:
            self.pos = offset
            if not self._invisible:
                self.fs.seek(self.start + self.pos)
        elif origin == io.SEEK_CUR:
            self.pos += offset
            if not self._invisible:
                self.fs.seek(offset, io.SEEK_CUR)
        elif origin == io.SEEK_END:
            self.pos = self.length - offset
            if not self._invisible:
                self.fs.seek(self.start + self.pos)
        else:
            raise ValueError(f"Unexpected origin: {origin}")
        return self.pos

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def read(self, size: int = -1) -> bytes:
        base_offset = self.fs.tell()
        # If the underlying stream has moved on, ensure we bring it back to its expected place
        if base_offset != self.start + self.pos:
            self.fs.seek(self.start + self.pos)
        remaining = self.length - self.pos
        size = remaining if size is None or size < 0 or size > remaining else size
        ret = self.fs.read(size)
        self.pos += len(ret)
        if self._invisible:
            # Return the stream to its original position after the read
            self.fs.seek(base_offset)
        return ret

    def readall(self) -> bytes:
        return self.read()

    def readinto(self, b: Union[bytearray, memoryview, array.array, mmap.mmap]) -> int:
        remaining = self.length - self.pos
        to_read = remaining if len(b) > remaining else len(b)
        b[:to_read] = self.read(to_read)  # type: ignore
        return to_read

    def readable(self) -> bool:
        return True


StreamBase = Union[BinaryIO, SubStream]
