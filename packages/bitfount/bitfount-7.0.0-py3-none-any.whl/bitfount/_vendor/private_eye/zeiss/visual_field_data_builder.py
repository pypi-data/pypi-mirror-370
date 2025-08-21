from typing import Callable, Dict, Optional

from ...private_eye import ParserOptions
from ...private_eye.data import VisualFieldData
from ...private_eye.zeiss.common import ds_require
from ...private_eye.zeiss.visual_fields.encapsulated_pdf_parser import parse_zeiss_encapsulated_pdf
from ...private_eye.zeiss.visual_fields.opv_parser import parse_opv_data
from ...private_eye.zeiss.visual_fields.raw_sfa_parser import parse_zeiss_raw_sfa
from pydicom import FileDataset
from pydicom._storage_sopclass_uids import (
    EncapsulatedPDFStorage,
    OphthalmicVisualFieldStaticPerimetryMeasurementsStorage,
    RawDataStorage,
)
from pydicom.uid import UID

vf_parsers: Dict[UID, Callable[[FileDataset, ParserOptions], VisualFieldData]] = {
    EncapsulatedPDFStorage: parse_zeiss_encapsulated_pdf,
    RawDataStorage: parse_zeiss_raw_sfa,
    OphthalmicVisualFieldStaticPerimetryMeasurementsStorage: parse_opv_data,
}


def build_visual_field_metadata(ds: FileDataset, options: ParserOptions) -> Optional[VisualFieldData]:
    ds_require(ds.file_meta, "MediaStorageSOPClassUID", ds.SOPClassUID)

    if ds.get("Modality") == "OPV":
        if parser := vf_parsers.get(ds.SOPClassUID):
            return parser(ds, options)

    return None
