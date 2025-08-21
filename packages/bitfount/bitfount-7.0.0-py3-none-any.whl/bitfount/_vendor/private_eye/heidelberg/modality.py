import logging

from ...private_eye import ImageParseException
from ...private_eye.consts import ImageModality
from ...private_eye.heidelberg.hr import HrExamType

logger = logging.getLogger(__name__)

_exam_type_to_modality_map = {
    HrExamType.FLUORESCEIN_ANGIOGRAPHY: ImageModality.FLUORESCEIN_ANGIOGRAPHY,
    HrExamType.INDOCYANINE_GREEN_ANGIOGRAPHY: ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY,
    HrExamType.COLOUR_PHOTO: ImageModality.COLOUR_PHOTO,
    HrExamType.RED_FREE: ImageModality.RED_FREE,
    HrExamType.INFRARED: ImageModality.SLO_INFRARED,
    HrExamType.TOMOGRAPHY: ImageModality.HR_TOMOGRAPHY,
    HrExamType.BLUE_AUTOFLUORESCENCE: ImageModality.AUTOFLUORESCENCE_BLUE,
    HrExamType.THICKNESS: ImageModality.THICKNESS,
    HrExamType.AF_488_NM: ImageModality.AUTOFLUORESCENCE_BLUE,
    HrExamType.AF_514_NM: ImageModality.AUTOFLUORESCENCE_GREEN,
    HrExamType.OCT: ImageModality.OCT,
    HrExamType.CORNEA_MICROSCOPY: ImageModality.CORNEA_MICROSCOPY,
    HrExamType.MPOD: ImageModality.MPOD,
    HrExamType.MPOD_RESULT: ImageModality.MPOD_RESULT,
    HrExamType.FDF: ImageModality.FDF,
    HrExamType.IR_XP: ImageModality.SLO_INFRARED_CROSS_POLARIZED,
    HrExamType.RED_FREE_XP: ImageModality.RED_FREE_CROSS_POLARIZED,
    HrExamType.IR_AUTOFLUORESCENCE: ImageModality.AUTOFLUORESCENCE_IR,
    HrExamType.CFP: ImageModality.COLOUR_PHOTO,
    HrExamType.RGB: ImageModality.COLOUR_PHOTO,
    HrExamType.GREEN_REFLECTANCE: ImageModality.REFLECTANCE_GREEN,
    HrExamType.BLUE_REFLECTANCE: ImageModality.REFLECTANCE_GREEN,
    HrExamType.GREEN_AUTOFLUORESCENCE: ImageModality.AUTOFLUORESCENCE_GREEN,
    HrExamType.QUANTITATIVE_AUTOFLUORESCENCE_488NM: ImageModality.AUTOFLUORESCENCE_BLUE,
    HrExamType.BLUE_REFLECTANCE_XP: ImageModality.REFLECTANCE_BLUE_CROSS_POLARIZED,
    HrExamType.SAP: ImageModality.SAP,
}

# For multicolour images these types correspond to the three colour channels. It is unknown if this extends to others.
_multicolour_type_to_modality = {
    0x4000271A: ImageModality.REFLECTANCE_GREEN,
    0x4000271B: ImageModality.REFLECTANCE_BLUE,
    0x40000000: ImageModality.REFLECTANCE_IR,
}


def get_modality_from_exam_type(exam_type: HrExamType, segment_type: int) -> ImageModality:
    """
    Get the Private Eye modality from a combination of exam type and segment type.
    In cases where we don't know the exact return value we throw an error - this logic has
    been worked out in combination with MEH and UHB researchers, and we don't want to
    export any ambiguous data at this point.

    Not all HR exam types will have a matching modality - we've explicitly excluded these
    as there are no examples in any HR database we've looked at, so we don't want to guess
    at the data structure

    One special case is Multicolour. Heyex stores these as three separate images with
    the same exam type but different segment types. We have decided to export these as
    separate images with separate modalities, and leave it up to end users to combine
    the channels as they see fit.

    See RIPF-508 for background of the logic.
    """
    if exam_type == HrExamType.MULTICOLOR:
        try:
            return _multicolour_type_to_modality[segment_type]
        except KeyError as error:
            raise ImageParseException(f"Unknown multicolour segment type: {segment_type}") from error
    try:
        return _exam_type_to_modality_map[exam_type]
    except KeyError as error:
        # We raise an exception instead of warning, as we don't know what to do with the given image modality
        # and will need to examine it in detail before allowing it into the database
        raise ImageParseException(f"Unknown Heidelberg exam type: {exam_type}") from error
