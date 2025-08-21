import logging
import math
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

import numpy as np
from ....private_eye.data import BscanLocation, Circle, Line, PointF, Size2D, Size3D
from ....private_eye.topcon.consts import ScanMode
from ....private_eye.topcon.section.bounding_box import BoundingBox, BoundingCircle, BoundingShape
from ....private_eye.topcon.section.img_bscan import BScanParamSection
from ....private_eye.utils.typings import get_type_args

logger = logging.getLogger(__name__)

TShape = TypeVar("TShape", BoundingBox, BoundingCircle)


class DimensionsCalculator(Generic[TShape], ABC):
    _class_map: Dict[ScanMode, Type["DimensionsCalculator"]] = dict()

    SCAN_MODE: ScanMode = NotImplemented

    def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:
        if cls.__name__ != "DimensionsCalculator" and cls.SCAN_MODE is NotImplemented:
            raise NotImplementedError("SCAN_MODE must be set")

        cls._class_map[cls.SCAN_MODE] = cls
        super().__init_subclass__(**kwargs)

    def locations(
        self,
        bounding_box: Optional[BoundingShape],
        image_count: int,
        sizing_info: Optional[BScanParamSection.SizingInfo],
    ) -> List[BscanLocation]:
        required_class = get_type_args(self.__class__)[0]
        if not isinstance(bounding_box, required_class):
            raise ValueError(f"Expected {required_class.__name__} boundary for {self.SCAN_MODE}")
        if not bounding_box:
            return []
        return self._calculate_positions(bounding_box, image_count, sizing_info)

    def bscan_dimensions(
        self, sizing_info: Optional[BScanParamSection.SizingInfo], bscan_size: Size2D, number_of_slices: int
    ) -> Tuple[Optional[Size3D], Optional[Size3D]]:
        if not sizing_info:
            return None, None

        width = self._get_physical_width(sizing_info)
        resolutions = Size3D(
            # Physical depth is the distance in mm between B-scans.
            depth=0 if number_of_slices == 1 else sizing_info.depth_dimension_mm / (number_of_slices - 1),
            # Physical width is the width in mm of a single b-scan pixel
            width=width / bscan_size.width,
            # Height is already the width of a pixel, but in um not mm
            height=sizing_info.height_resolution_um / 1000,
        )
        dimensions = Size3D(
            # Already the size in mm
            depth=sizing_info.depth_dimension_mm,
            # Already the size in mm
            width=width,
            # Need to multiply by the number of pixels
            height=resolutions.height * bscan_size.height,
        )
        return dimensions, resolutions

    def _get_physical_width(self, sizing_info: Optional[BScanParamSection.SizingInfo]) -> float:
        return sizing_info.width_dimension_mm

    @abstractmethod
    def _calculate_positions(
        self, bounding_shape: TShape, image_count: int, sizing_info: Optional[BScanParamSection.SizingInfo]
    ) -> List[BscanLocation]:
        raise NotImplementedError()

    @classmethod
    def get(cls, scan_mode: ScanMode) -> Optional["DimensionsCalculator"]:
        try:
            ret_cls = cls._class_map[scan_mode]
        except KeyError:
            # TODO RIPF-433: Implement appropriate subclasses and throw an error instead
            logger.warning(f"Dimension calculation for {scan_mode} not supported")
            return None
        else:
            return ret_cls()


class RectangularVolumeDimensionsCalculator(DimensionsCalculator[BoundingBox]):
    """
    Calculate appropriate y-values by performing a linear spacing between smallest and largest y-values
    We assume that the bounding box is always level and images are arranged horizontally
    """

    SCAN_MODE = ScanMode.RECTANGULAR_VOLUME

    def _calculate_positions(
        self, bounding_shape: BoundingBox, image_count: int, _: Optional[BScanParamSection.SizingInfo]
    ) -> List[BscanLocation]:
        start_x = float(bounding_shape.min.x)
        end_x = float(bounding_shape.max.x)
        y_values = np.linspace(bounding_shape.min.y, bounding_shape.max.y, image_count, endpoint=True, dtype=float)
        return [Line(PointF(start_x, y), PointF(end_x, y)) for y in y_values]


class VerticalVolumeDimensionsCalculator(DimensionsCalculator[BoundingBox]):
    """
    Calculate appropriate x-values by performing a linear spacing between smallest and largest x-values
    We assume that the bounding box is always level and images are arranged vertically
    """

    SCAN_MODE = ScanMode.VERTICAL

    def _calculate_positions(
        self, bounding_shape: BoundingBox, image_count: int, _: Optional[BScanParamSection.SizingInfo]
    ) -> List[BscanLocation]:
        start_y = float(bounding_shape.min.y)
        end_y = float(bounding_shape.max.y)
        x_values = np.linspace(bounding_shape.min.x, bounding_shape.max.x, image_count, endpoint=True, dtype=float)
        return [Line(PointF(x, start_y), PointF(x, end_y)) for x in x_values]


class SevenLineDimensionsCalculator(DimensionsCalculator[BoundingBox]):
    """
    Calculate appropriate x and y values by performing linear spacing between the limits of the bounding box.
    We currently only suppport bounding box's orientated along a major axis.
    """

    SCAN_MODE = ScanMode.SEVEN_LINE

    def _calculate_positions(
        self, bounding_shape: BoundingBox, image_count: int, sizing_info: Optional[BScanParamSection.SizingInfo]
    ) -> List[BscanLocation]:
        if not sizing_info:
            raise ValueError("Sizing info required to calculate positions for Seven Line scan mode.")
        start_x = bounding_shape.min.x
        end_x = bounding_shape.max.x
        start_y = bounding_shape.min.y
        end_y = bounding_shape.max.y
        difference_in_x = end_x - start_x
        difference_in_y = end_y - start_y

        if difference_in_x and difference_in_y:
            logger.warning("Scan not taken along a major axis. This is untested functionality.")

        scan_angle = math.pi / 2 - math.atan2(difference_in_y, difference_in_x)
        scan_length = np.linalg.norm((difference_in_x, difference_in_y))

        half_scan_width = (scan_length / sizing_info.width_dimension_mm) * sizing_info.depth_dimension_mm * 3.0

        # We round to reduce visual noise from floating point errors when looking at this data.
        left_x = round(start_x - half_scan_width * math.cos(scan_angle), 10)
        right_x = round(start_x + half_scan_width * math.cos(scan_angle), 10)

        top_y = round(start_y - half_scan_width * math.sin(scan_angle), 10)
        bottom_y = round(start_y + half_scan_width * math.sin(scan_angle), 10)

        x_values = np.linspace(left_x, right_x, image_count, endpoint=True, dtype=float)
        y_values = np.linspace(top_y, bottom_y, image_count, endpoint=True, dtype=float)

        return [
            Line(PointF(x, y), PointF(x + difference_in_x, y + difference_in_y)) for x, y in zip(x_values, y_values)
        ]


class LineDimensionsCalculator(DimensionsCalculator[BoundingBox]):
    """
    This is simply a line from the start coordinates to the end coordinates of the given bounding box
    """

    SCAN_MODE = ScanMode.LINE

    def _calculate_positions(
        self, bounding_shape: BoundingBox, image_count: int, _: Optional[BScanParamSection.SizingInfo]
    ) -> List[BscanLocation]:
        start = bounding_shape.min.to_tuple()
        end = bounding_shape.max.to_tuple()
        return [Line(PointF(*start), PointF(*end))]


class CircleDimensionsCalculator(DimensionsCalculator[BoundingCircle]):
    """
    A single b-scan in the shape of a circle.
    """

    SCAN_MODE = ScanMode.CIRCLE

    def _calculate_positions(
        self, bounding_shape: BoundingCircle, image_count: int, _: Optional[BScanParamSection.SizingInfo]
    ) -> List[BscanLocation]:
        centre = bounding_shape.centre.to_tuple()
        return [Circle(PointF(*centre), float(bounding_shape.radius), 0.0)]

    def _get_physical_width(self, sizing_info: Optional[BScanParamSection.SizingInfo]) -> float:
        """
        The physical width returned is actually the radius, so we need to adjust calculations accordingly
        """
        return sizing_info.width_dimension_mm * np.pi * 2


class CylindricalVolumeDimensionsCalculator(DimensionsCalculator[BoundingCircle]):
    """
    Cylindrical volume b-scans are taken radially at even angular intervals
    The first image is always along the x-axis, starting from 3 o'clock and ending at 9 o'clock.
    """

    SCAN_MODE = ScanMode.CYLINDRICAL_VOLUME

    def _calculate_positions(
        self, bounding_shape: BoundingCircle, image_count: int, _: Optional[BScanParamSection.SizingInfo]
    ) -> List[BscanLocation]:
        radius = bounding_shape.radius
        centre_x = bounding_shape.centre.x
        centre_y = bounding_shape.centre.y

        ret = []
        # Split 180 degrees into image_count sections, excluding 180 itself.
        for th in np.linspace(0, np.pi, image_count, endpoint=False, dtype=float):
            cos_th = radius * np.cos(th)
            sin_th = radius * np.sin(th)
            start = PointF(centre_x + cos_th, centre_y + sin_th)
            end = PointF(centre_x - cos_th, centre_y - sin_th)
            ret.append(Line(start, end))
        return ret
