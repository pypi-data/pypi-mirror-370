from decimal import Decimal

from .....private_eye.consts import ImageModality
from .....private_eye.output_formatter.dicom.dicom_helpers import (
    DEFAULT_RESOLUTIONS_MM,
    as_sequence,
    code_dataset,
    code_sequence,
)
from .....private_eye.output_formatter.dicom.modules.common import DicomData, DicomModule
from pydicom import Dataset, Sequence


class GeneralImage(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # See http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.html#sect_C.7.6.1.1.1
        # This value is fixed according to both Topcon and Zeiss conformance statements
        # TODO RIPF-430: Verify this is also correct for Heidelberg
        ds.PatientOrientation = ["L", "F"]
        ds.AcquisitionNumber = 0


class ImagePixel(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        image_size = data.image.size

        ds.Rows = image_size.height
        ds.Columns = image_size.width

        if data.image.is_colour:
            samples = 3
            interpretation = "RGB"
        else:
            samples = 1
            interpretation = "MONOCHROME2"
        ds.BitsAllocated = data.bits_stored
        ds.BitsStored = data.bits_stored
        ds.HighBit = data.bits_stored - 1
        ds.SamplesPerPixel = samples
        ds.PhotometricInterpretation = interpretation
        ds.PixelRepresentation = 0  # Unsigned integers

        if samples > 1:
            # For RGB images, this means the order of the pixel values encoded shall be R1, G1, B1, R2, G2, B2, …, etc.
            ds.PlanarConfiguration = 0

        image_resolutions_mm = data.image.resolutions_mm or DEFAULT_RESOLUTIONS_MM
        pixel_size_x = Decimal(image_resolutions_mm.width)
        pixel_size_y = Decimal(image_resolutions_mm.height)
        ratio = pixel_size_x / pixel_size_y
        ds.PixelAspectRatio = list(ratio.as_integer_ratio())

        ds.PixelData = data.pixel_data
        ds.HorizontalFieldOfView = data.image.field_of_view


class EnhancedContrast(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        if data.image.modality == ImageModality.FLUORESCEIN_ANGIOGRAPHY:
            ds.ContrastBolusAgentSequence = self._contrast_agent_sequence("350086004", "Fluorescein")
        elif data.image.modality == ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY:
            ds.ContrastBolusAgentSequence = self._contrast_agent_sequence("7292004", "Indocyanine green")

    @staticmethod
    def _contrast_agent_sequence(value: str, meaning: str) -> Sequence:
        base_ds = code_dataset("SCT", value, meaning)
        base_ds.ContrastBolusAgentNumber = 1
        # Required by the spec but can be empty
        base_ds.ContrastBolusVolume = ""
        base_ds.ContrastBolusIngredientConcentration = ""
        base_ds.ContrastBolusIngredientCodeSequence = Sequence()
        # According to the Zeiss DICOM conformance statement, both FA and ICGA dyes are injected intravenously
        base_ds.ContrastBolusAdministrationRouteSequence = code_sequence("SCT", "47625008", "Intravenous route")
        return as_sequence(base_ds)
