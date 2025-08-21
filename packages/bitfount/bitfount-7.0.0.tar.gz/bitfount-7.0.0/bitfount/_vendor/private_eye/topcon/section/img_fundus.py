from typing import Tuple

import numpy as np

from ...data import ImageOutputParams, ImageTransform, Size2D
from ...exceptions import ImageParseException
from .base import FdaSection


class FundusImageSection(FdaSection):
    EXCLUDED_FIELDS = ["image"]

    def load(self) -> None:
        self.size = Size2D(width=self.fs.read_int(), height=self.fs.read_int())
        self.colour_depth = self.fs.read_int()
        self.slices = self.fs.read_int()
        self.image_type = self.fs.read_byte()
        self.image_level = self.fs.read_short()
        self.reversibility = self.fs.read_byte()
        if self.colour_depth == 24:
            self.image_mode = "RGB"
        elif self.colour_depth == 8:
            self.image_mode = "L"
        else:
            raise ValueError(f"{self.colour_depth} is not 8 or 24")

        self.image_output_params = [
            ImageOutputParams(
                image_processing_options=image_processing_option,
                image_mode=self.image_mode,
                image_transform_functions=[_get_handle_RGB()],
            )
            for image_processing_option in self.options.image_processing_options
        ]

        if self.slices != 1:
            raise ImageParseException("Unable to parse ImgFundusSection with multiple slices")

        image = self.fs.read_data_or_skip(self.fs.read_int())

        self.image = image


def _split_image(image_array: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    return image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]


def _get_handle_RGB() -> ImageTransform:
    def _handle_RGB(image_array: np.ndarray) -> np.ndarray:
        # Bizarrely, red and blue channels are swapped for RGB images
        # Not all images are RGB - e.g. \mehimagenet6\Archive2\Folder_5788\1160860.fda
        try:
            _, _, channels = image_array.shape
            if channels >= 3:
                (r, g, b) = _split_image(image_array)
                image_array = np.stack([b, g, r], axis=2)
            return image_array
        except np.AxisError:
            return image_array

    return _handle_RGB


class FundusParamSection(FdaSection):
    def load(self) -> None:
        self.acquire_mode = self.fs.read_byte()
        self.image_angle = self.fs.read_byte()
        self.acquire_lighting_level = self.fs.read_int_signed()
        self.camera_type = self.fs.read_ascii(12)
        self.image_quality_mode = self.fs.read_ascii(24)
        # This is only present on newer Topcon images.  If we ever want
        # this data we could read these only if we are on a new enough
        # version
        # self.saturation = self.fs.read_byte()
        # self.edge_enhancement = self.fs.read_byte()
        # self.tone = self.fs.read_byte()
        # self.colour_space = self.fs.read_byte()
        # self.colour_shade = self.fs.read_byte()
        # self.lightness = self.fs.read_byte()
        # self.whitebalance_mode = self.fs.read_ascii(24)
        # self.colour_temperature = self.fs.read_byte()
        # self.shutter_speed = self.fs.read_byte()
        # self.iso_sensitivity = self.fs.read_ascii(12)
        # self.acquire_lighting_level_2 = self.fs.read_int_signed()
