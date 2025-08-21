from typing import Optional, Type, cast

import numpy as np

from ...consts import CornealLayer, RetinalLayer
from ...exceptions import ImageParseException
from .base import FdaSection

CONTOUR_MAP = {
    "MULTILAYERS_1": RetinalLayer.ILM,
    "MULTILAYERS_2": RetinalLayer.RNFL,
    "MULTILAYERS_3": RetinalLayer.GCL,
    "MULTILAYERS_4": RetinalLayer.IPL,
    "MULTILAYERS_5": RetinalLayer.M_E,
    "MULTILAYERS_6": RetinalLayer.RPE,
    "MULTILAYERS_7": RetinalLayer.BM,
    "MULTILAYERS_8": RetinalLayer.INL,
    "MULTILAYERS_9": RetinalLayer.ELM,
    "RETINA_1": RetinalLayer.ILM,
    "RETINA_2": RetinalLayer.M_E,
    "RETINA_3": RetinalLayer.RPE,
    "RETINA_4": RetinalLayer.BM,
    "CORNEA_1": CornealLayer.EP,
    "CORNEA_2": CornealLayer.END,
    "CORNEA_3": CornealLayer.BOW,
}


class ContourInfoSection(FdaSection):
    EXCLUDED_FIELDS = ["data"]
    MULTIPLE = True

    def load(self) -> None:
        self.id = self.fs.read_ascii(20)
        self.label = CONTOUR_MAP.get(self.id, f"Unknown({self.id})")
        self.type = self.fs.read_short()
        self.width = self.fs.read_int()
        self.count = self.fs.read_int()
        self.data = self._parse_contour_data()
        self.mystery1 = self.fs.read_ascii(32)

        # Older FDA files only have one mystery string, so check whether we've hit the end
        self.mystery2: Optional[str] = None
        try:
            self.mystery2 = self.fs.read_ascii(32)
        except ValueError:
            pass

    def _parse_contour_data(self) -> np.ndarray:
        length = self.fs.read_int()

        dtype: Type[np.number]
        if self.type == 0:
            dtype = np.int16
        elif self.type == 256:
            dtype = np.float64
        else:
            raise ImageParseException(f"Unknown contour type: {self.type}")

        size = np.dtype(dtype).itemsize
        if size * self.count * self.width != length:
            raise ImageParseException(
                f"Contour dimensions ({self.width}x{self.count}x{size}) " f"do not match data length ({length})"
            )

        data = np.frombuffer(self.fs.read_bytes(length), dtype=dtype)
        return cast(np.ndarray, data.reshape((self.count, self.width)))
