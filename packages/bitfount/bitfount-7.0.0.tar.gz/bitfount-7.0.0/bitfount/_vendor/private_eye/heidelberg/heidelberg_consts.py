from enum import Enum, unique

# This is a static value that is defined in a Heidelberg manual and roughly matches some of the values we've seen
# noqa: E501  See
# https://www.heidelbergengineering.com/media/e-learning/Totara/Dateien/pdf-tutorials/210111-001_SPECTRALIS%20OCTA%20-%20Principles%20and%20Clinical%20Applications_EN.pdf
# TODO RIPF-496: This is incorrect for some images - it must be present *somewhere* in the eye data
#  e.g. reena/3356599.sdb contains images marked as 9.9mm in Heyex, while this values gives 8.8mm.
INTERIOR_DEGREES_TO_MM = 4.4 / 15


# This also comes from a Heidelberg manual, and is specified as approximate
# noqa: E501  See
# https://www.heidelbergengineering.com/media/e-learning/Totara/Dateien/pdf-tutorials/93450-001_SPECTRALIS-ASM_How-to-acquire-perfect-image_EN.pdf
ANTERIOR_DEGREES_TO_MM = 16.0 / 30


@unique
class BScanType(int, Enum):
    LINE: int = 1
    CIRCLE: int = 2
