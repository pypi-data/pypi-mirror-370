"""

Based on the work by Paulo Scardine, found here https://github.com/scardine/image_size/blob/master/get_image_size.py

Adjusted to just our requirements,namely working on a byte object rather than a file.

"""
import struct
from typing import Tuple

import attr


@attr.s(auto_attribs=True, frozen=True, slots=True)
class JPEGHeaderData:
    bits_per_sample: int
    width: int
    height: int
    number_of_components: int


class InvalidJPEGFile(Exception):
    pass


def get_jpeg_header_data(image: bytes) -> JPEGHeaderData:
    """Returns the bits per a sample, width, height and number of components from JPEG header"""
    bits_per_sample = width = height = number_of_components = -1
    # Check that the file is a JPEG file based on the first 2 bytes
    if image[0:2] != b"\xff\xd8":
        raise InvalidJPEGFile("File dose not have JPEG file identifier as first 2 bytes")
    # Search for the correct part of the header file.
    # The size of the sections of the header file will not be consistent so need to handle this properly.
    current_location = 2
    while image[current_location] and image[current_location] != 0xDA:
        # All JPEG sections start with the byte 0xFF
        while image[current_location] != 0xFF:
            current_location += 1
        while image[current_location] == 0xFF:
            current_location += 1
        # The SOFx header section contains the dimensions of the JPEG file.
        # This header starts with a byte with values between 0xC0 and 0xC3 inclusive.

        if image[current_location] >= 0xC0 and image[current_location] <= 0xC3:
            # The bits per a sample will be 2 bytes later than the header start byte and is 1 byte long.
            # The height will be straight after and is 2 bytes long.
            # The width is the 2 bytes directly after the height
            # The number of components is the single byte after the width.

            bits_per_sample, height, width, number_of_components = struct.unpack(
                ">BHHB", image[current_location + 3 : current_location + 9]
            )

            break
        else:
            # Each header contains the length of the section after the section identifier and length values.
            # This is 2 bytes long.
            current_location += struct.unpack(">H", image[current_location + 1 : current_location + 3])[0] + 1
    # Only error on the dimensions. Should the other values be incorrect we will catch them at more appropriate times.
    # Unless we can use other methods to work out the value.
    if width == -1 or height == -1:
        raise InvalidJPEGFile("File header does not contain the file dimensions in the JPEG header")
    return JPEGHeaderData(bits_per_sample, width, height, number_of_components)
