from .base import FdaSection


class FileInfoSection(FdaSection):
    def load(self) -> None:
        self.major = self.fs.read_int()
        self.minor = self.fs.read_int()
        self.build = self.fs.read_ascii(32)
