from ...consts import Laterality
from ...exceptions import ImageParseException
from .base import FdaSection


class CaptureInfoSection(FdaSection):
    def load(self) -> None:
        eye_byte = self.fs.read_byte()
        if eye_byte == 0:
            self.eye = Laterality.RIGHT
        elif eye_byte == 1:
            self.eye = Laterality.LEFT
        else:
            raise ImageParseException(f"Unknown eye flag: {eye_byte}")
        self.capture_mode = self.fs.read_byte()
        self.session_id = self.fs.read_int()
        self.label = self.fs.read_ascii(100)
        self.scan_datetime = self.fs.read_datetime()
