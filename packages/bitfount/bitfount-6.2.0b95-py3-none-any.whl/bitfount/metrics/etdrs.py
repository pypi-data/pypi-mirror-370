"""Metrics regarding OCTs.

Not currently used in the project but may be useful in the future.
"""

from __future__ import annotations

from typing import Optional, cast

import numpy as np

from bitfount.metrics.types import (
    Coordinates,
    Laterality,
    MaculaQuadrantRingValue,
    MaculaQuadrants,
    MaculaQuadrantValue,
    MaculaSubFields,
    MaculaSubFieldsValue,
    Quadrant,
    Zone,
)

ETDRS_FOVEA_DIAMETER = 1  # mm
ETDRS_INNER_DIAMETER = 3  # mm
ETDRS_OUTER_DIAMETER = 6  # mm


def get_point_distance_from_fovea(
    point_coordinates: Coordinates,
    fovea_coordinates: Coordinates,
    mm_per_pixel_x: float,
    mm_per_pixel_y: float,
) -> float:
    """Calculates and returns a point's distance from the fovea in mm."""
    mm_distance_x = (point_coordinates.X - fovea_coordinates.X) * mm_per_pixel_x
    mm_distance_y = (point_coordinates.Y - fovea_coordinates.Y) * mm_per_pixel_y

    # Uses pythagoras' theorem
    mm_distance = float(np.sqrt(mm_distance_x**2 + mm_distance_y**2))
    return mm_distance


def get_zone(distance_from_fovea: float) -> Optional[Zone]:
    """Returns the zone corresponding to how far a point is from the fovea.

    Returns None if the point is further than the outer diameter.
    """
    if distance_from_fovea <= (ETDRS_FOVEA_DIAMETER / 2):
        return Zone.FOVEA
    elif distance_from_fovea <= (ETDRS_INNER_DIAMETER / 2):
        return Zone.INNER
    elif distance_from_fovea <= (ETDRS_OUTER_DIAMETER / 2):
        return Zone.OUTER

    return None


def get_quadrant(
    point_coordinates: Coordinates,
    fovea_coordinates: Coordinates,
    laterality: Laterality,
) -> Quadrant:
    """Gets the quadrant that a point is in, in relation to the fovea.

    Args:
        point_coordinates: The coordinates of the point in question.
        fovea_coordinates: The coordinates of the fovea.
        laterality: Whether the image is of the left eye or the right eye. This
            has no impact on superior or inferior quadrants but determines whether
            a coordinate is in the nasal quadrant or the temporal quadrant.

    Returns:
        The quadrant the point would be in. This does not take into account the distance
        from the fovea and therefore the point may fall inside the fovea (which has no
        quadrants) or it may so far from the fovea that it does not fall into any of the
        macula subfields.

    Raises:
        ValueError: If the quadrant cannot be calculated due to an unexpected value in
            the inputs to the function.
    """
    # 100 here refers to the number of pixels away from the fovea. The value itself
    # does not matter as it is simply used to get two points on the two 45 degree
    # diagonal lines that are used to split the macula into quadrants
    upper_right_coordinate = Coordinates(
        fovea_coordinates.X + 100, fovea_coordinates.Y + 100
    )
    upper_left_coordinate = Coordinates(
        fovea_coordinates.X - 100, fovea_coordinates.Y + 100
    )
    lower_right_coordinate = Coordinates(
        fovea_coordinates.X + 100, fovea_coordinates.Y - 100
    )
    lower_left_coordinate = Coordinates(
        fovea_coordinates.X - 100, fovea_coordinates.Y - 100
    )

    above_right_diagonal = is_point_above_line(
        lower_left_coordinate, upper_right_coordinate, point_coordinates
    )
    above_left_diagonal = is_point_above_line(
        lower_right_coordinate, upper_left_coordinate, point_coordinates
    )

    if above_right_diagonal and above_left_diagonal:
        return Quadrant.SUPERIOR
    if not above_right_diagonal and not above_left_diagonal:
        return Quadrant.INFERIOR
    if laterality == Laterality.LEFT:
        return Quadrant.NASAL if above_right_diagonal else Quadrant.TEMPORAL
    if laterality == Laterality.RIGHT:
        return Quadrant.NASAL if above_left_diagonal else Quadrant.TEMPORAL
    raise ValueError(
        "Please check the co-ordinates and laterality match the expected types."
    )


def is_point_above_line(a: Coordinates, b: Coordinates, c: Coordinates) -> bool:
    """Returns True if point c is above line formed from points a and b.

    Args:
        a: A point on a line.
        b: Another point on the same line as point a.
        c: A set of coordinates whcih can be anywhere in relation to the line formed
            by points a and b.

    Returns:
        True if point c would lie above the line formed by a and b, otherwise False. The
        line can be thought to be extrapolated if point c falls outside the length of
        the line.
    """
    # Calculates cross product
    return ((b.X - a.X) * (c.Y - a.Y) - (b.Y - a.Y) * (c.X - a.X)) > 0


def is_pixel_ga(pixel: np.ndarray) -> bool:
    """Returns whether a given pixel from an en-face image is GA based on the colour."""
    # If the 4th element in the array is not 255
    return True if pixel[3] != 255 else False


def get_num_pixels_ga(img_array: np.ndarray) -> int:
    """Returns the number of pixels in the image which demonstrate GA."""
    return len([pixel for line in img_array for pixel in line if is_pixel_ga(pixel)])


def compute_subfields(
    img_array: np.ndarray,
    laterality: Laterality,
    slo_num_pixels_width: int,
    slo_num_pixels_height: int,
    slo_dimension_mm_width: float,
    slo_dimension_mm_height: float,
    fovea_coordinates: Optional[Coordinates] = None,
) -> MaculaSubFields:
    """Compute GA affected area of macula ETDRS subfields.

    Args:
        img_array: Image as a square 2D numpy array.
        laterality: The laterality of the image (left or right).
        slo_num_pixels_width: Number of pixels in the width of the image array.
        slo_num_pixels_height: Number of pixels in the height of the image array.
        slo_dimension_mm_width: Width in mm of the image array.
        slo_dimension_mm_height: Height in mm of the image array.
        fovea_coordinates: The coordinates corresponding to the fovea. If not
            provided, the fovea will be assumed to be in the centre of the image.

    Returns:
        A nested dictionary of ETDRS subfields contained affected areas in mm^2.
    """
    slo_area_pixels = slo_num_pixels_width * slo_num_pixels_height
    slo_area_mm = slo_dimension_mm_width * slo_dimension_mm_height  # mm
    slo_mm_per_pixel_x = slo_dimension_mm_width / slo_num_pixels_width
    slo_mm_per_pixel_y = slo_dimension_mm_height / slo_num_pixels_height

    etdrs_subfields = MaculaSubFields(
        fovea=0,
        inner=MaculaQuadrants(superior=0, inferior=0, nasal=0, temporal=0),
        outer=MaculaQuadrants(superior=0, inferior=0, nasal=0, temporal=0),
    )

    # This is used as a proxy for the fovea if fovea coordinates are not provided
    if not fovea_coordinates:
        fovea_coordinates = Coordinates(
            (slo_num_pixels_width + 1) / 2,
            (slo_num_pixels_height + 1) / 2,
        )

    for x in range(slo_num_pixels_width):
        for y in range(slo_num_pixels_height):
            distance = get_point_distance_from_fovea(
                Coordinates(x, y),
                fovea_coordinates,
                slo_mm_per_pixel_x,
                slo_mm_per_pixel_y,
            )
            zone = get_zone(distance)
            ga = is_pixel_ga(img_array[x][y])
            if zone == Zone.FOVEA and ga:
                zone_value = cast(MaculaSubFieldsValue, zone.value)
                etdrs_subfields[zone_value] = cast(int, etdrs_subfields[zone_value]) + 1
            elif not ga or not zone:
                continue
            else:
                quadrant = get_quadrant(
                    Coordinates(x, y), fovea_coordinates, laterality
                )
                zone_value = cast(MaculaQuadrantRingValue, zone.value)
                etdrs_subfields[zone_value][quadrant.value] = (
                    cast(int, etdrs_subfields[zone_value][quadrant.value]) + 1
                )

    for k, v in etdrs_subfields.items():
        k = cast(MaculaSubFieldsValue, k)
        if not isinstance(v, dict):
            v = cast(int, v)
            etdrs_subfields[k] = (v / slo_area_pixels) * slo_area_mm
        else:
            v = cast(MaculaQuadrants, v)
            for k_, v_ in v.items():
                k = cast(MaculaQuadrantRingValue, k)
                k_ = cast(MaculaQuadrantValue, k_)
                v_ = cast(int, v_)
                etdrs_subfields[k][k_] = (v_ / slo_area_pixels) * slo_area_mm
    return etdrs_subfields


def compute_subfields_oct(
    img_array: np.ndarray,
    laterality: Laterality,
    oct_width_mm: float,  # (e.g 8.8/512)
    oct_depth_mm: float,  # (e.g. 5.9/49)
    oct_num_pixels_width: int,
    oct_num_pixels_height: int,
    fovea_coordinates: Optional[Coordinates] = None,
) -> MaculaSubFields:
    """Compute GA affected area of macula ETDRS subfields.

    Args:
        img_array: Image as a square 2D numpy array.
        laterality: The laterality of the image (left or right).
        oct_width_mm: Width in mm of the image array.
        oct_depth_mm: Height in mm of the image array.
        oct_num_pixels_width: Number of pixels in the width of the image array.
        oct_num_pixels_height: Number of pixels in the height of the image array.
        fovea_coordinates: The coordinates corresponding to the fovea. If not
            provided, the fovea will be assumed to be in the centre of the image.

    Returns:
        A nested dictionary of ETDRS subfields contained affected areas in mm^2.
    """
    oct_mm_per_pixel_x = oct_width_mm / oct_num_pixels_width
    oct_mm_per_pixel_y = oct_depth_mm / oct_num_pixels_height
    oct_area_mm = oct_width_mm * oct_depth_mm
    oct_area_pixels = oct_num_pixels_width * oct_num_pixels_height

    etdrs_subfields = MaculaSubFields(
        fovea=0,
        inner=MaculaQuadrants(superior=0, inferior=0, nasal=0, temporal=0),
        outer=MaculaQuadrants(superior=0, inferior=0, nasal=0, temporal=0),
    )

    # This is used as a proxy for the fovea if fovea coordinates are not provided
    if not fovea_coordinates:
        fovea_coordinates = Coordinates(
            (oct_num_pixels_width + 1) / 2,
            (oct_num_pixels_height + 1) / 2,
        )

    for x in range(oct_num_pixels_width):
        for y in range(oct_num_pixels_height):
            distance = get_point_distance_from_fovea(
                Coordinates(x, y),
                fovea_coordinates,
                oct_mm_per_pixel_x,
                oct_mm_per_pixel_y,
            )
            zone = get_zone(distance)
            ga = is_pixel_ga(img_array[x][y])
            if zone == Zone.FOVEA and ga:
                zone_value = cast(MaculaSubFieldsValue, zone.value)
                etdrs_subfields[zone_value] = cast(int, etdrs_subfields[zone_value]) + 1
            elif not ga or not zone:
                continue
            else:
                quadrant = get_quadrant(
                    Coordinates(x, y), fovea_coordinates, laterality
                )
                zone_value = cast(MaculaQuadrantRingValue, zone.value)
                etdrs_subfields[zone_value][quadrant.value] = (
                    cast(int, etdrs_subfields[zone_value][quadrant.value]) + 1
                )

    for k, v in etdrs_subfields.items():
        k = cast(MaculaSubFieldsValue, k)
        if not isinstance(v, dict):
            v = cast(int, v)
            etdrs_subfields[k] = (v / oct_area_pixels) * oct_area_mm
        else:
            v = cast(MaculaQuadrants, v)
            for k_, v_ in v.items():
                k = cast(MaculaQuadrantRingValue, k)
                k_ = cast(MaculaQuadrantValue, k_)
                v_ = cast(int, v_)
                etdrs_subfields[k][k_] = (v_ / oct_area_pixels) * oct_area_mm
    return etdrs_subfields
