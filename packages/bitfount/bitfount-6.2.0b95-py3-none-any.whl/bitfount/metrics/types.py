"""Types regarding OCT metrics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal, TypedDict


@dataclass
class Coordinates:
    """Dataclass representing X and Y coordinates."""

    X: float
    Y: float


class Zone(Enum):
    """Represents the zone component of the ETDRS sub-field.

    This is determined by the absolute distance of a point from the centre of the
    macula.
    """

    FOVEA = "fovea"
    INNER = "inner"
    OUTER = "outer"


class Quadrant(Enum):
    """Represents the quadrant component of the ETDRS sub-field.

    This is determined by the angle of a point from the centre of the macula.
    """

    SUPERIOR = "superior"
    INFERIOR = "inferior"
    NASAL = "nasal"
    TEMPORAL = "temporal"


class Laterality(Enum):
    """Represents the laterality of the image."""

    LEFT = "L"
    RIGHT = "R"


class MaculaQuadrants(TypedDict):
    """TypedDict representing the quadrants in the inner/outer ETDRS zones."""

    superior: float
    inferior: float
    nasal: float
    temporal: float


class MaculaSubFields(TypedDict):
    """TypedDict representing the 9 ETDRS subfields."""

    fovea: float
    inner: MaculaQuadrants
    outer: MaculaQuadrants


# Macula zones that are split into quadrants
MaculaQuadrantRingValue = Literal["inner", "outer"]
# All Macula zones
MaculaSubFieldsValue = Literal["fovea", MaculaQuadrantRingValue]
# All quadrants
MaculaQuadrantValue = Literal["superior", "inferior", "nasal", "temporal"]
