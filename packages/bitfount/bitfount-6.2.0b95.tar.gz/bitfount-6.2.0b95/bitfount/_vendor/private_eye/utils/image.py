from PIL import Image

from ..data import Number
from ..exceptions import ImageParseException

PILLOW_MODE_TO_DEPTH = {
    "1": 1,
    "L": 8,
    "P": 8,
    "RGB": 24,
    "RGBA": 32,
    "CMYK": 32,
    "YCbCr": 24,
    "I": 32,
    "F": 32,
    "I;16": 16,
}


def get_pixel_depth(mode: str) -> int:
    return PILLOW_MODE_TO_DEPTH[mode]


def validate_image(image: Image, expected_width: Number, expected_height: Number, expected_depth: int) -> None:
    img_height_diff_exp_height = image.height != expected_height
    img_width_diff_exp_width = image.width != expected_width
    img_depth_diff_exp_depth = get_pixel_depth(image) != expected_depth

    if img_height_diff_exp_height or img_width_diff_exp_width or img_depth_diff_exp_depth:
        raise ImageParseException(
            "Image metadata didn't match FDA metadata: "
            f"{image.height}, {image.width}, {image.mode} / "
            f"{expected_height}, {expected_width}, {expected_depth}"
        )
