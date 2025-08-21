import logging

from .....private_eye.output_formatter.dicom.classes.common import DicomClass
from .....private_eye.output_formatter.dicom.modules.common import (
    DicomData,
    FrameOfReference,
    GeneralSeries,
    GeneralStudy,
    Patient,
    SOPCommon,
    Synchronisation,
)
from .....private_eye.output_formatter.dicom.modules.equipment import EnhancedGeneralEquipment, GeneralEquipment
from .....private_eye.output_formatter.dicom.modules.eye import OcularRegionImaged
from .....private_eye.output_formatter.dicom.modules.image import EnhancedContrast, ImagePixel
from .....private_eye.output_formatter.dicom.modules.oct import (
    AcquisitionContext,
    MultiFrameDimension,
    MultiFrameFunctionalGroups,
    OphthalmicTomographyAcquisitionParameters,
    OphthalmicTomographyImage,
    OphthalmicTomographyParameters,
    OphthalmicTomographySeries,
)
from pydicom.uid import UID, OphthalmicTomographyImageStorage

logger = logging.getLogger(__name__)


class OphthalmicTomographyImageClass(DicomClass):
    MODULES = [
        SOPCommon,
        Patient,
        GeneralStudy,
        GeneralSeries,
        GeneralEquipment,
        EnhancedGeneralEquipment,
        FrameOfReference,
        Synchronisation,
        EnhancedContrast,
        MultiFrameFunctionalGroups,
        MultiFrameDimension,
        AcquisitionContext,
        OphthalmicTomographySeries,
        OphthalmicTomographyImage,
        OphthalmicTomographyAcquisitionParameters,
        OphthalmicTomographyParameters,
        OcularRegionImaged,
        ImagePixel,
    ]

    def get_sop_class(self, data: DicomData) -> UID:
        return OphthalmicTomographyImageStorage
