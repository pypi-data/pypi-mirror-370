import numpy as np

from .base import FdaSection


class ResultCorneaCurve(FdaSection):
    def load(self) -> None:
        self.id = self.fs.read_ascii(20)
        self.width = self.fs.read_int()
        self.count = self.fs.read_int()
        self.version = self.fs.read_ascii(32)
        # TODO RIPF-1588 The actual data is a whole load of doubles. What does it mean?


class ResultCorneaThickness(FdaSection):

    EXCLUDED_FIELDS = ["data"]

    def load(self) -> None:
        self.version = self.fs.read_ascii(32)
        self.id = self.fs.read_ascii(20)
        self.width = self.fs.read_int()
        self.count = self.fs.read_int()
        self.data = np.empty((self.count, self.width), dtype=np.float64)
        for y in range(self.count):
            for x in range(self.width):
                self.data[y][x] = self.fs.read_double()
