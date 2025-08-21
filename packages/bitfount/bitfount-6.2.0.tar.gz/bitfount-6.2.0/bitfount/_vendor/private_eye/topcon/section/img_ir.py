from typing import List, Optional

from ...data import ImageOutputParams, Size2D
from .base import FdaSection


class InfraredImageSection(FdaSection):
    EXCLUDED_FIELDS = ["images"]

    def load(self) -> None:
        self.size = Size2D(width=self.fs.read_int(), height=self.fs.read_int())
        self.colour_depth = self.fs.read_int()
        img_count = self.fs.read_int()
        self.fs.skip(1)
        self.images: List[Optional[bytes]] = []
        self.image_mode = "L"
        for _ in range(img_count):
            image = self.fs.read_data_or_skip(self.fs.read_int())
            self.images.append(image)
        self.image_output_params = [
            ImageOutputParams(
                image_processing_options=image_processing_option,
                image_mode=self.image_mode,
                image_transform_functions=[],
            )
            for image_processing_option in self.options.image_processing_options
        ]


class InfraredParamSection(FdaSection):
    def load(self) -> None:
        self.capture_mode = self.fs.read_byte()
        self.image_angle = self.fs.read_byte()
        self.observe_illuminate_level = self.fs.read_short()
