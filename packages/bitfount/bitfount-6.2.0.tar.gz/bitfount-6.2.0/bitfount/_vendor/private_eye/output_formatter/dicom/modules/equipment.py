from .....private_eye.output_formatter.dicom.dicom_helpers import map_optional_to_string
from .....private_eye.output_formatter.dicom.modules.common import DicomData, DicomModule
from pydicom import Dataset


class GeneralEquipment(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        exam = data.parser_result.exam
        ds.Manufacturer = exam.manufacturer
        ds.ManufacturerModelName = exam.scanner_model
        if not self.parent.is_anonymised:
            ds.DeviceSerialNumber = map_optional_to_string(exam.scanner_serial_number)


class EnhancedGeneralEquipment(DicomModule):
    """
    This is a subset of General Equipment, but with stricter requirements
    """

    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        exam = data.parser_result.exam
        ds.ManufacturerModelName = exam.scanner_model or "Unknown"
        if self.parent.is_anonymised:
            ds.DeviceSerialNumber = "0"
            ds.SoftwareVersions = ["0"]
        else:
            ds.DeviceSerialNumber = exam.scanner_serial_number or "Unknown"
            ds.SoftwareVersions = [exam.scanner_software_version or "Unknown"]
