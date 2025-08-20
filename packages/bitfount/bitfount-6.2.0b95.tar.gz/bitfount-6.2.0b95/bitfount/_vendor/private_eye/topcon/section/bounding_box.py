from typing import Any, Optional, Union

import attr

from ...data import Point
from .base import FdaSection


@attr.s(auto_attribs=True, frozen=True, repr=False)
class BoundingBox:
    min: Point
    max: Point


@attr.s(auto_attribs=True, frozen=True, repr=False)
class BoundingCircle:
    centre: Point
    radius: int


BoundingShape = Union[BoundingBox, BoundingCircle]


class BoundingShapeSection(FdaSection):
    """
    The section contains bounding shapes, either defined as boxes or circles
    The distinction is the last number: if zero, it is a circle; otherwise, it is a box.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.trc_shape: Optional[BoundingShape] = None
        self.fundus_shape: Optional[BoundingShape] = None

    def _read_bounding_shape(self) -> BoundingShape:
        values = (
            self.fs.read_int(),
            self.fs.read_int(),
            self.fs.read_int(),
            self.fs.read_int(),
        )

        if values[3] == 0:
            return BoundingCircle(Point(values[0], values[1]), values[2])
        return BoundingBox(Point(values[0], values[1]), Point(values[2], values[3]))


class RegistrationInfoSection(BoundingShapeSection):
    def load(self) -> None:
        self.registration_method = self.fs.read_byte()
        self.offset_x = self.fs.read_int()
        self.offset_y = self.fs.read_int()
        self.fundus_shape = self._read_bounding_shape()
        self.registration_version = self.fs.read_ascii(32)
        self.trc_shape = self._read_bounding_shape()

        # After this point we have the following information:
        # * Disc grid centre coords (manual/auto)
        # * Macula grid centre coords (manual/auto)
        # * Vertical scan bounding boxes
        # * 'affine' variables.
        #
        # Given that it's not  obvious which are which, especially since not all files have all of these,
        # we shall ignore these for now.


class ScanRangeSection(BoundingShapeSection):
    def load(self) -> None:
        self.fundus_shape = self._read_bounding_shape()
        self.trc_shape = self._read_bounding_shape()
