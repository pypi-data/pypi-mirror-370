from .base import FdaSection


class BinarySection(FdaSection):
    MULTIPLE = True

    def load(self) -> None:
        self.data = self.fs.read()
