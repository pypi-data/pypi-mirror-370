import logging

from .....private_eye import ImageModality
from .....private_eye.output_formatter.dicom.dicom_helpers import (
    DEFAULT_DATE,
    DEFAULT_DATETIME,
    DEFAULT_RESOLUTIONS_MM,
    DEFAULT_TIME,
    code_sequence,
    crop_number,
    format_date,
    format_datetime,
    format_time,
)
from .....private_eye.output_formatter.dicom.modules.common import DicomData, DicomModule
from .....private_eye.utils.optional import convert_or_default, map_optional
from pydicom import Dataset, Sequence

logger = logging.getLogger(__name__)


class OphthalmicPhotographySeries(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # The required fields for this are already fulfilled by GeneralSeries.
        # Not sure why this module exists, but we include it to match the DICOM spec.
        pass


class OphthalmicPhotographyImage(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        if self.parent.is_anonymised:
            # This is required for OphthalmicPhotographyImage, so make up a value
            ds.InstanceNumber = 0
        else:
            ds.InstanceNumber = convert_or_default(data.image.source_id, int, 0)

        # https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.17.2.html
        # A 'montage' is an image constructed out of several individual images, and is always of 'derived' type
        # (Indeed, a montage is the only valid use case for the derived type)
        #
        # The only example in supported image systems is a proof sheet from Imagenet2000
        if data.image.is_montage:
            ds.ImageType = ["DERIVED", "PRIMARY", "MONTAGE"]

            # Required when ImageType is 'DERIVED', but may be empty.
            # Note: this contradicts the requirements for the same attribute as part of the General Reference module
            # which states that at least one value must be within this sequence. However:
            # * We have nothing to insert into this sequence
            # * The General Reference is marked as 'U'
            # Hence, we shall prioritise the definition from THIS module and leave it empty.
            ds.SourceImageSequence = Sequence()

        else:
            ds.ImageType = ["ORIGINAL", "PRIMARY"]

        if self.parent.is_anonymised:
            ds.ContentDate = DEFAULT_DATE
            ds.ContentTime = DEFAULT_TIME
            ds.AcquisitionDateTime = DEFAULT_DATETIME
        else:
            scan_datetime = data.parser_result.exam.scan_datetime
            ds.ContentDate = map_optional(scan_datetime, format_date)
            ds.ContentTime = map_optional(scan_datetime, format_time)
            ds.AcquisitionDateTime = map_optional(scan_datetime, format_datetime)

        ds.BurnedInAnnotation = "NO"

        if data.image.is_colour:
            # Note: If two-colour, then use RGB with the missing channel zeroed out.
            ds.SamplesPerPixel = 3
            ds.PhotometricInterpretation = "RGB"
            # Only required if samples per pixel > 1
            ds.PlanarConfiguration = 0
        else:
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"
            # Only required if Monochrome
            ds.PresentationLUTShape = "IDENTITY"
        ds.PixelRepresentation = 0

        image_resolutions_mm = data.image.resolutions_mm or DEFAULT_RESOLUTIONS_MM
        # Pixel spacing = (distance between rows, distance between cols). Hence, (height resolution, width resolution)
        ds.PixelSpacing = [
            crop_number(image_resolutions_mm.height),
            crop_number(image_resolutions_mm.width),
        ]

        ds.LossyImageCompression = "00"


class OphthalmicPhotographicAcquisitionParameters(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        ds.RefractiveStateSequence = Sequence()
        ds.PatientEyeMovementCommanded = ""
        ds.HorizontalFieldOfView = ""
        ds.EmmetropicMagnification = ""
        ds.IntraOcularPressure = ""
        ds.PupilDilated = ""


class OphthalmicPhotographicParameters(DicomModule):
    def populate_dataset(self, ds: Dataset, data: DicomData) -> None:
        # http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4202.html
        if data.parser_result.series.anterior:
            ds.AcquisitionDeviceTypeCodeSequence = code_sequence("SCT", "409903006", "External Camera")
        elif data.image.modality in (
            ImageModality.SLO_RED,
            ImageModality.SLO_GREEN,
            ImageModality.SLO_BLUE,
            ImageModality.SLO_INFRARED,
            ImageModality.SLO_INFRARED_CROSS_POLARIZED,
            ImageModality.AUTOFLUORESCENCE_BLUE,
            ImageModality.AUTOFLUORESCENCE_GREEN,
            ImageModality.AUTOFLUORESCENCE_IR,
            ImageModality.FLUORESCEIN_ANGIOGRAPHY,
            ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY,
            ImageModality.RED_FREE,
            ImageModality.RED_FREE_CROSS_POLARIZED,
        ):
            ds.AcquisitionDeviceTypeCodeSequence = code_sequence("SCT", "392001008", "Scanning Laser Ophthalmoscope")
        else:
            ds.AcquisitionDeviceTypeCodeSequence = code_sequence("SCT", "409898007", "Fundus Camera")

        ds.IlluminationTypeCodeSequence = Sequence()
        ds.ImagePathFilterTypeStackCodeSequence = Sequence()
        ds.LensesCodeSequence = Sequence()
        ds.LightPathFilterTypeStackCodeSequence = Sequence()
        ds.DetectorType = ""
