from .base import FdaSection


class FastQ2Section(FdaSection):
    def load(self) -> None:
        self.abs_min = self.fs.read_float()
        self.nf = self.fs.read_float()
        self.max = self.fs.read_float()
        self.abs_max = self.fs.read_float()
        self.q_mean = self.fs.read_float()
        self.z_mean = self.fs.read_float()
        self.version_info = self.fs.read_ascii(32)
