"""
Spec found at http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.41.3.html
"""
import logging

from .....private_eye.output_formatter.dicom.classes.common import DicomClass
from .....private_eye.output_formatter.dicom.modules.common import (
    DicomData,
    GeneralSeries,
    GeneralStudy,
    MultiFrameAndCine,
    Patient,
    SOPCommon,
    Synchronisation,
)
from .....private_eye.output_formatter.dicom.modules.equipment import GeneralEquipment
from .....private_eye.output_formatter.dicom.modules.eye import OcularRegionImaged
from .....private_eye.output_formatter.dicom.modules.image import EnhancedContrast, GeneralImage, ImagePixel
from .....private_eye.output_formatter.dicom.modules.photo import (
    OphthalmicPhotographicAcquisitionParameters,
    OphthalmicPhotographicParameters,
    OphthalmicPhotographyImage,
    OphthalmicPhotographySeries,
)
from pydicom.uid import UID, OphthalmicPhotography8BitImageStorage, OphthalmicPhotography16BitImageStorage

logger = logging.getLogger(__name__)


class OphthalmicPhotographyClass(DicomClass):
    """
    This class supports both 8-bit and 16-bit SOPs, as they have the same modules
    """

    MODULES = [
        SOPCommon,
        Patient,
        GeneralStudy,
        GeneralSeries,
        GeneralEquipment,
        GeneralImage,
        Synchronisation,
        # Required iff agent used.
        # see http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4200.html
        EnhancedContrast,
        MultiFrameAndCine,
        OcularRegionImaged,
        OphthalmicPhotographyImage,
        OphthalmicPhotographySeries,
        OphthalmicPhotographicAcquisitionParameters,
        OphthalmicPhotographicParameters,
        ImagePixel,
    ]

    def get_sop_class(self, data: DicomData) -> UID:
        if data.bits_stored == 16:
            return OphthalmicPhotography16BitImageStorage
        elif data.bits_stored in (1, 8):
            return OphthalmicPhotography8BitImageStorage
        else:
            raise ValueError(f"Unsupported BitsStored: {data.bits_stored}")
