"""
The constants here are pulled out of the Heidelberg Access database
"""
from enum import Enum, unique
from typing import Dict, Optional, cast

from more_itertools import one


def _assert_no_zero_keys(source: dict) -> dict:
    if any(k == 0 for k in source.keys()):
        raise ValueError("No zero-valued keys allowed")
    return source


_exam_structs = _assert_no_zero_keys(
    {
        1: "Retina",
        2: "Macula",
        3: "ONH",
        6: "Cornea",
        10: "Sclera",
        11: "Chamber Angle",
        12: "Papillomacular Bundle",
        13: "Anterior Segment",
        14: "Peripapillary Retina",
    }
)


@unique
class HrExamType(Enum):
    """
    The description values and IDs are straight from the HR database
    """

    FLUORESCEIN_ANGIOGRAPHY = (2, "Fluorescein Angiography")
    INDOCYANINE_GREEN_ANGIOGRAPHY = (3, "ICG Angiography")
    COLOUR_PHOTO = (4, "Color Photo")
    RED_FREE = (5, "Red Free")
    INFRARED = (6, "Infra-Red")
    TOMOGRAPHY = (7, "Tomography")
    BLUE_AUTOFLUORESCENCE = (10, "Blue Autofluorescence (488 nm)")
    BLACK_WHITE_PHOTO = (11, "Black & White Photo")
    THICKNESS = (16, "Thickness")
    AF_488_NM = (17, "488 nm")
    AF_514_NM = (18, "514 nm")
    OCT = (23, "OCT")
    CORNEA_MICROSCOPY = (24, "Cornea Microscopy")
    MPOD = (27, "MP Optical Density")
    MPOD_RESULT = (28, "MP Optical Density Result")
    FIXATION = (29, "Fixation Measurement")
    FDF = (30, "FDF")
    IR_XP = (33, "Infra-Red (cross polarized)")
    RED_FREE_XP = (34, "Red Free (cross polarized)")
    IR_BLUE_XP = (35, "IR & Blue (cross polarized)")
    IR_AUTOFLUORESCENCE = (36, "IR Autofluorescence (790 nm)")
    CFP = (37, "CFP")
    VIOLET_BLUE = (38, "Violet blue")
    MULTICOLOR = (39, "MultiColor")
    RGB = (40, "RGB")
    RED = (41, "Red")
    GREEN_REFLECTANCE = (42, "Green Reflectance")
    BLUE_REFLECTANCE = (43, "Blue Reflectance")
    GREEN_AUTOFLUORESCENCE = (44, "Green Autofluorescence (518 nm)")
    QUANTITATIVE_AUTOFLUORESCENCE_488NM = (47, "Quantitative Autofluorescence (488 nm)")
    BLUE_REFLECTANCE_XP = (48, "Blue Reflectance (cross polarized)")
    SAP = (76, "SAP")

    description: str

    def __new__(cls, hr_id: int, description: str) -> "HrExamType":
        # This is the canonical way of overriding handling of the enum value.
        # See https://docs.python.org/3/library/enum.html#using-a-custom-new
        ret = object.__new__(cls)
        ret._value_ = hr_id
        ret.description = description
        return cast("HrExamType", ret)

    def __str__(self) -> str:
        return self.description

    @classmethod
    def get_by_id(cls, hr_id: int) -> "HrExamType":
        return one((t for t in HrExamType if t.value == hr_id), too_short=KeyError())


_series_types = _assert_no_zero_keys(
    {
        101: "Unconverted DOS Images",
        102: "Images",
        103: "Time Sequence",
        104: "Z-Scan",
        107: "W-Scan",
        108: "TAU-Map",
        204: "Result",
        205: "Signal Width",
        206: "Progression",
        214: "Topography",
        401: "Section",
        403: "Volume",
        501: "24-2",
        701: "OCT B-Scan",
        702: "OCT Volume ",
        703: "OCT ART Volume",
        704: "OCT Star Scan",
        705: "OCT Scan Template",
        706: "OCT Movie",
        707: "OCT Radial+Circles",
        751: "OCTA B-Scan",
        752: "OCTA Volume ",
        753: "OCTA ART Volume",
        754: "OCTA Star Scan",
        755: "OCTA Scan Template",
        756: "OCTA Movie",
        757: "OCTA Radial+Circles",
        801: "AS OCT B-Scan",
        802: "AS OCT Volume",
        803: "AS OCT ART Volume",
        804: "AS OCT Star Scan",
        806: "AS OCT Movie",
        901: "WFO OCT B-Scan",
        902: "WFO OCT Volume",
        903: "WFO OCT ART Volume",
        904: "WFO OCT Star Scan",
        906: "WFO OCT Movie",
    }
)


def _get_value_or_null(source: Dict[int, str], key: int) -> Optional[str]:
    if key == 0:
        return None
    return source[key]


def get_exam_struct(key: int) -> Optional[str]:
    return _get_value_or_null(_exam_structs, key)


def get_exam_type(key: int) -> Optional[HrExamType]:
    try:
        return HrExamType.get_by_id(key)
    except KeyError:
        return None


def get_series_type(key: int) -> Optional[str]:
    return _get_value_or_null(_series_types, key)
