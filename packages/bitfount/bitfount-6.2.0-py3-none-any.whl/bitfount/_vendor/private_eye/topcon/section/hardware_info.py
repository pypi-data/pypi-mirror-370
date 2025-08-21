from .base import FdaSection


class HardwareInfoSection(FdaSection):
    def load(self) -> None:
        self.manufacturer_model = self.fs.read_ascii(16)
        self.serial_number = self.fs.read_ascii(48)
        self.software_version = self.fs.read_ascii(16)
        self.last_calibration_date = self.fs.read_datetime(True)
