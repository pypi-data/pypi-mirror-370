"""

Based on the work by Paulo Scardine, found here https://github.com/scardine/image_size/blob/master/get_image_size.py

Adjusted to just our requirements:
 - Working on a byte object rather than a file.
 - Reading the values from the second page should more than one page exist.
"""

import struct
from typing import Tuple


class InvalidTiffFile(Exception):
    pass


_IFD_ENTRY_SIZE = 12
COUNT_SIZE = 2


def get_tiff_dimensions(data: bytes) -> Tuple[int, int]:
    width = height = -1
    # Standard TIFF, big- or little-endian
    # BigTIFF and other different but TIFF-like formats are not
    # supported currently
    byte_order = data[:2]
    if byte_order not in (b"MM", b"II"):
        raise InvalidTiffFile(f"Invalid byte order: {byte_order!r}")
    bo_char = ">" if byte_order == b"MM" else "<"
    # maps TIFF type id to size (in bytes)
    # and python format char for struct
    tiff_types = {
        1: (1, bo_char + "B"),  # BYTE
        2: (1, bo_char + "c"),  # ASCII
        3: (2, bo_char + "H"),  # SHORT
        4: (4, bo_char + "L"),  # LONG
        5: (8, bo_char + "LL"),  # RATIONAL
        6: (1, bo_char + "b"),  # SBYTE
        7: (1, bo_char + "c"),  # UNDEFINED
        8: (2, bo_char + "h"),  # SSHORT
        9: (4, bo_char + "l"),  # SLONG
        10: (8, bo_char + "ll"),  # SRATIONAL
        11: (4, bo_char + "f"),  # FLOAT
        12: (8, bo_char + "d"),  # DOUBLE
    }
    try:
        ifd_offset = struct.unpack(bo_char + "L", data[4:8])[0]

        ec = data[ifd_offset : ifd_offset + COUNT_SIZE]
        ifd_entry_count = struct.unpack(bo_char + "H", ec)[0]

        # Before continuing we want to check if the file has more than one page.
        # This can be done by checking the value of the offset for the first page.
        page_location_offset = ifd_offset + COUNT_SIZE + ifd_entry_count * _IFD_ENTRY_SIZE
        page_offset = struct.unpack(bo_char + "I", data[page_location_offset : page_location_offset + 4])[0]
        # Reset data to not include the initial 8 bytes.
        # If their are multiple pages we will use the width and height value from page 2.
        if page_offset != 0:
            data = data[page_offset:-1]
            ifd_entry_count = struct.unpack(bo_char + "H", data[0:2])[0]
        else:
            data = data[8:-1]
        for i in range(ifd_entry_count):
            entry_offset = COUNT_SIZE + i * _IFD_ENTRY_SIZE
            tag = data[entry_offset : entry_offset + 2]
            tag = struct.unpack(bo_char + "H", tag)[0]
            if tag in (256, 257):
                # if type indicates that value fits into 4 bytes, value
                # offset is not an offset but value itself
                type_bytes = data[entry_offset + 2 : entry_offset + 4]
                tiff_type = struct.unpack(bo_char + "H", type_bytes)[0]
                if tiff_type not in tiff_types:
                    raise InvalidTiffFile("Unknown TIFF field type:" + str(type))
                type_size = tiff_types[tiff_type][0]
                type_char = tiff_types[tiff_type][1]
                value_bytes = data[entry_offset + 8 : entry_offset + 8 + type_size]
                value = int(struct.unpack(type_char, value_bytes)[0])
                if tag == 256:
                    width = value
                else:
                    height = value
            if width > -1 and height > -1:
                return width, height
    except Exception as e:
        raise InvalidTiffFile(str(e)) from e
    raise InvalidTiffFile("File does not contain the file dimensions in the Tiff header")
