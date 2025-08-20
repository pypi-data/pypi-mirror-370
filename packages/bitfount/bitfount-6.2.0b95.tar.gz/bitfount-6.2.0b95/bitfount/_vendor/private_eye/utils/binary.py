from contextlib import contextmanager
from typing import BinaryIO, Iterator, cast


def get_subint(source: int, start_index: int, length: int) -> int:
    """
    Given a source integer, returns an integer represented by a given subset of bits
    :param source: Source integer
    :param start_index: Starting index, where 0 is the least significant bit
    :param length: Number of bits
    """
    mask = (2**length) - 1
    return cast(int, (source >> start_index) & mask)


@contextmanager
def peek(source: BinaryIO, length: int) -> Iterator[bytes]:
    """
    Read bytes from the stream and return to the original position at the end of the context scope
    :param source: bytes stream
    :param length: number of bytes to read
    :return: data read from the stream
    """
    current = source.tell()
    yield source.read(length)
    source.seek(current)
