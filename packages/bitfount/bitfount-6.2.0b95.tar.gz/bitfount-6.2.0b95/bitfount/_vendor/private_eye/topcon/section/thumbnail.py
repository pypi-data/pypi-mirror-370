from typing import List

from PIL.Image import Image
from ....private_eye.exceptions import ImageParseException, StreamLengthError

from .base import FdaSection


class ThumbnailSection(FdaSection):
    EXCLUDED_FIELDS = ["thumbnails"]

    def load(self) -> None:
        self.thumbnails: List[Image] = []
        while True:
            try:
                thumbnail = self.fs.read_data_or_skip(self.fs.read_int())
            except (StreamLengthError, ImageParseException):
                break
            self.thumbnails.append(thumbnail)
