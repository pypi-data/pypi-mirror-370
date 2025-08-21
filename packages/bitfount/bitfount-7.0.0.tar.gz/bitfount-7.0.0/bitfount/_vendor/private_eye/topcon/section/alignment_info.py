from .base import FdaSection


class AlignmentInfoSection(FdaSection):
    def load(self) -> None:
        self.alignment_type = self.fs.read_byte()
        self.data_type = self.fs.read_byte()
        self.width = self.fs.read_int()

        self.unknown_data = self.fs.read_data(self.fs.read_int())

        self.keyframe_position_start = self.fs.read_int()
        self.keyframe_position_end = self.fs.read_int()
        self.upper_oct_border = self.fs.read_int()
        self.lower_oct_border = self.fs.read_int()
        self.alignment_version = self.fs.read_ascii(32)
