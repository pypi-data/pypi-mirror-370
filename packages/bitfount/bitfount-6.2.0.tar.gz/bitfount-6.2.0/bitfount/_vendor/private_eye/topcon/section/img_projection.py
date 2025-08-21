from ...data import Size2D
from .base import FdaSection


class ImgProjectionSection(FdaSection):
    EXCLUDED_FIELDS = ["image"]

    def load(self) -> None:
        self.size = Size2D(self.fs.read_int(), self.fs.read_int())
        self.colour_depth = self.fs.read_int()
        self.image_type = self.fs.read_byte()
        self.image_level = self.fs.read_short()
        self.reversibility = self.fs.read_byte()
        self.image = self.fs.read_data_or_skip(self.fs.read_int())
