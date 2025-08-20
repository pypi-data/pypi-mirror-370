from typing import List, Optional

from ....private_eye.data import Size2D

from ...exceptions import ImageParseException
from .base import FdaSection


class RefImageScanSection(FdaSection):
    def load(self) -> None:
        self.size = Size2D(self.fs.read_int(), self.fs.read_int())
        self.colour_depth = self.fs.read_int()
        self.slice_count = self.fs.read_int()
        self.fs.skip(1)
        data_length = self.fs.read_int()
        bytes_per_pixel = int(self.colour_depth / 8)
        if data_length != self.slice_count * self.size.width * self.size.height * bytes_per_pixel:
            raise ImageParseException("Invalid length of REF_IMG_SCAN section!")
        self.images: List[Optional[bytes]] = []
        for _ in range(self.slice_count):
            data_length = int(self.size.height * self.size.width * bytes_per_pixel)
            if self.options.skip_image_data:
                self.fs.skip(data_length)
                data = None
            else:
                data = self.fs.read(data_length)
            self.images.append(data)
