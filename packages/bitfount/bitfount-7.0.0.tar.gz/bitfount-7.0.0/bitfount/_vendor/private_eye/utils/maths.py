from math import atan2, pi, sqrt
from typing import TypeVar

from ...private_eye.data import Point, PointF

TPoint = TypeVar("TPoint", Point, PointF)


def distance(a: TPoint, b: TPoint) -> float:
    dx = a.x - b.x
    dy = a.y - b.y

    return sqrt(dx * dx + dy * dy)


def angle_from_origin(point: TPoint, origin: TPoint) -> float:
    """
    Angle of the vector from origin -> point from the positive x-axis. The result is always between 0 and 2*PI
    """
    angle = atan2(point.y - origin.y, point.x - origin.x)
    if angle < 0:
        angle += 2 * pi
    return angle
