import logging
from typing import Dict, List, Optional, Tuple, Union

from ...private_eye import DebugData, ParserOptions
from ...private_eye.zeiss.visual_fields.raw_sfa_parser import ZEISS_RAW_SFA_TAG, parse_zeiss_raw_sfa_element
from pydicom import DataElement, Dataset, FileDataset, Sequence
from pydicom._dicom_dict import DicomDictionary

# This is really very useful when working on the format, as you can see all the info in one place, but we don't want to
# expose it as it makes the outputted JSON harder to consume.
PRETTY_PRINT_ALL_INFO = False

# Elements which shouldn't be included in the JSON output, usually because they are too large and will be exposed as raw
# files instead.
BINARY_DATA_TAGS = [
    # Pixel Data
    0x7FE00010,
    # Mystery Zeiss data
    0x04071006,
    # Encapsulated Document (seen in the PDF types)
    0x00420011,
]


DICOM_ELEMENT_LOG_TRUNCATION_LENGTH = 1024

logger = logging.getLogger(__name__)


def _pretty_print_tag(inner_elem: DataElement) -> str:
    assert isinstance(inner_elem, DataElement)
    # DicomDictionary is (VR, VM, Name, Retired, Keyword)

    # mypy needs some help
    element_description: Optional[Tuple[str, str, str, str, str]]
    element_name: Optional[str]
    element_type: Optional[str]

    try:
        element_description = DicomDictionary[inner_elem.tag]
    except KeyError:
        element_description = None

    if element_description:
        element_name = element_description[2]
        element_type = element_description[0]
    else:
        element_name = None
        element_type = None

    if PRETTY_PRINT_ALL_INFO:
        element_name = element_name or "?"
        element_type = element_type or "?"
        pretty_tag = f"{hex(inner_elem.tag)} {element_name} {element_type}"
    else:
        if element_name:
            pretty_tag = element_name
        else:
            pretty_tag = hex(inner_elem.tag)

    return pretty_tag


def build_debug_metadata(ds: FileDataset, options: ParserOptions) -> DebugData:
    files: Dict[str, bytes] = {}
    logger.debug("Converting dataset: %s", str(ds)[0:DICOM_ELEMENT_LOG_TRUNCATION_LENGTH])

    def _convert_dicom_dataset(ds: Dataset, breadcrumb: List[str]) -> Dict[str, Union[Dict, List, str]]:
        logger.debug(
            "Converting dataset %s, breadcrumb: %s", str(ds)[0:DICOM_ELEMENT_LOG_TRUNCATION_LENGTH], breadcrumb
        )
        assert isinstance(ds, Dataset), type(ds)
        return {
            _pretty_print_tag(inner_elem): _convert_dicom_elem(
                inner_elem, breadcrumb=breadcrumb + [hex(inner_elem.tag)]
            )
            for inner_elem in ds
        }

    def _convert_dicom_elem(elem: DataElement, breadcrumb: List[str]) -> Union[Dict, List, str]:
        logger.debug("Converting elem %s, breadcrumb: %s", str(elem)[0:DICOM_ELEMENT_LOG_TRUNCATION_LENGTH], breadcrumb)
        assert isinstance(elem, DataElement), f"{type(elem)} {elem}"
        if isinstance(elem.value, Sequence):
            return [
                _convert_dicom_dataset(elem, breadcrumb=breadcrumb + [str(idx)]) for idx, elem in enumerate(elem.value)
            ]
        if elem.tag in BINARY_DATA_TAGS:
            filename = "-".join(breadcrumb)
            files[filename] = elem.value
            return f"(private-eye) Binary Data, written out as {filename}"
        if elem.tag == ZEISS_RAW_SFA_TAG:
            return parse_zeiss_raw_sfa_element(elem.value, options)
        return str(elem.value)

    dataset_as_dict: Dict = _convert_dicom_dataset(ds, breadcrumb=[])
    dataset_as_dict["FileMeta"] = _convert_dicom_dataset(ds.file_meta, breadcrumb=[])
    return DebugData(metadata=dataset_as_dict, images=None, files=files)
