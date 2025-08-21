from .....private_eye.output_formatter.dicom.dicom_helpers import code_sequence
from .....private_eye.output_formatter.dicom.modules.common import DicomData, DicomModule
from pydicom import Dataset


class OcularRegionImaged(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # This allows 'B' to represent Both eyes, unlike General Series laterality
        ds.ImageLaterality = data.parser_result.series.laterality.value
        # http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4209.html
        if data.parser_result.series.anterior:
            ds.AnatomicRegionSequence = code_sequence("SCT", "28726007", "Cornea")
        else:
            ds.AnatomicRegionSequence = code_sequence("SCT", "5665001", "Retina")
