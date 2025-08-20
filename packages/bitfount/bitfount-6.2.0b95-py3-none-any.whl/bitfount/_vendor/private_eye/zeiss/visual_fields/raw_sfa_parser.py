import io
import logging
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any, Dict, Generator, List, Optional, Tuple, cast
from xml.etree.ElementTree import Element

import attr
from ....private_eye import ParserOptions
from ....private_eye.common.file_stream_wrapper import FileStreamWrapper
from ....private_eye.data import VisualFieldData, VisualFieldReliabilityIndex, VisualFieldStorageType, VisualFieldTestPoint
from ....private_eye.utils.optional import map_optional
from ....private_eye.zeiss.raw_sfa_metadata_parser import read_metadata
from pydicom.dataset import FileDataset

logger = logging.getLogger(__name__)

ZEISS_RAW_SFA_TAG = 0x3011008


@attr.s(auto_attribs=True)
class RawSfaVisualFieldTestPoint:
    x_coord: int
    y_coord: int
    stimulus_results: str
    sensitivity: int
    retest_stimulus_seen: Optional[str]
    retest_sensitivity: Optional[int]
    supplementary_byte_1: Optional[int]
    supplementary_byte_2: Optional[int]
    mystery_byte: int


def parse_zeiss_raw_sfa(ds: FileDataset, options: ParserOptions) -> VisualFieldData:
    parsed_data = parse_zeiss_raw_sfa_element(ds[ZEISS_RAW_SFA_TAG].value, options)

    header_data = parsed_data["Header"]

    fixation_losses = VisualFieldReliabilityIndex(
        numerator=header_data["Fixation Loss Num."], denominator=header_data["Fixation Loss Den."]
    )
    false_positives = VisualFieldReliabilityIndex(
        numerator=header_data["False POS Rate Num."], denominator=header_data["False POS Rate Den."]
    )
    false_negatives = VisualFieldReliabilityIndex(
        numerator=header_data["False NEG Rate Num."], denominator=header_data["False NEG Rate Den."]
    )

    return VisualFieldData(
        storage_type=VisualFieldStorageType.RAW,
        modality="Static",  # SFA is static by definition
        # TODO:RIPF-656 Try to populate this field
        strategy="",
        source_id=str(ds.SOPInstanceUID),
        left_eye_patient_clinical_information=None,
        right_eye_patient_clinical_information=None,
        glaucoma_hemifield_test=None,
        test_duration=0,
        fixation_monitors=[],
        stimulus_size=None,
        stimulus_colour=None,
        background_luminance=None,
        foveal_sensitivity=None,
        # the interpretation of this RAW field is uncertain but appears closely related to the
        # 'performed protocol code sequence' field in the OPV files
        protocol=header_data["Test Pattern?"],
        fixation_loss=fixation_losses,
        false_positive_errors=false_positives,
        false_negative_errors=false_negatives,
        # we believe the aggregate values below are calculated, but the results of naive calculations are off and
        # the exact weighted formulae Zeiss use are currently unknown
        visual_field_index=None,
        mean_deviation=None,
        mean_deviation_significance=None,
        pattern_standard_deviation=None,
        pattern_standard_deviation_significance=None,
        visual_field_data=[
            _build_vf_data_from_raw_sfa_dataset(p) for p in parsed_data["Visual Field Test Point Sequence"]
        ],
    )


def parse_zeiss_raw_sfa_element(xml_data: bytes, options: ParserOptions) -> Dict[str, Any]:
    byte_data = _extract_byte_data(xml_data)
    parsed_data = _parse_byte_data(byte_data, options)

    return parsed_data


def _build_vf_data_from_raw_sfa_dataset(point: RawSfaVisualFieldTestPoint) -> VisualFieldTestPoint:
    return VisualFieldTestPoint(
        x_coord=float(point.x_coord),
        y_coord=float(point.y_coord),
        stimulus_results=point.stimulus_results,
        sensitivity=float(point.sensitivity),
        retest_stimulus_seen=point.retest_stimulus_seen,
        retest_sensitivity=map_optional(point.retest_sensitivity, float),
        normals=None,  # Currently normals cannot be read from RAW data
    )


def _extract_byte_data(xml_data: bytes) -> bytes:
    xml_string = xml_data.decode("UTF-8")
    data = xml_string.replace("\n", "").replace("\r", "").replace("\t", "").replace("\x04", "").replace("\x00", "")
    root = ET.fromstring(data)
    dataset_elem = root.find("{http://www.meditec.zeiss.com/czm-xml/Message}DataSet")
    if not dataset_elem:
        raise ValueError("Failed to parse XML: expected 'DataSet' element not present")
    binary_data = cast(Element, dataset_elem).find(
        "{http://www.meditec.zeiss.com/czm-xml/ExtendedInformationObject/HfaVisualFieldBinary}hfa_II_serial_binhex"
    )
    if not dataset_elem:
        raise ValueError("Failed to parse XML: expected 'hfa_II_serial_binhex' element not present")

    byte_data = bytes.fromhex(str(cast(Element, binary_data).text))
    return byte_data


def _parse_byte_data(byte_data: bytes, options: ParserOptions) -> Dict[str, Any]:
    fs: FileStreamWrapper = FileStreamWrapper(io.BytesIO(byte_data), options)
    header = _read_header(fs)
    sequence = _read_test_point_sequence(fs)

    if header["Sequence Length"] != len(sequence):
        logger.warning("Sequence actual length does not match stated length.")

    metadata = read_metadata(fs, len(sequence))

    if "SD" in metadata:
        _append_supplementary_sequence_data(sequence, metadata.pop("SD"))
    return {"Header": header, "Visual Field Test Point Sequence": sequence, "Metadata": metadata}


def _append_supplementary_sequence_data(
    sequence: List[RawSfaVisualFieldTestPoint], supplementary_sequence: Dict[Tuple[int, int], Tuple[int, int]]
) -> None:
    for point in sequence:
        x = point.x_coord
        y = point.y_coord
        supp_data = supplementary_sequence[(x, y)]
        point.supplementary_byte_1 = supp_data[0]
        point.supplementary_byte_2 = supp_data[1]


def _read_header(fs: FileStreamWrapper) -> Dict[str, Any]:
    maybe_format = fs.read_bytes(8)
    patient_id = fs.read_null_terminated_string("ascii")
    day = int(fs.read_ascii(2))
    month = int(fs.read_ascii(2))
    year = int(fs.read_ascii(4))
    _date = date(year, month, day)
    fs.read(1)
    mystery2 = fs.read_bytes(20)
    patient_name = fs.read_ascii(24)
    patient_key = fs.read_ascii(12)
    test_pattern = fs.read_ascii(16)
    mystery3 = fs.read_bytes(21)
    sph_lens_pow = fs.read_ascii(6)
    cyl_lens_pow = fs.read_ascii(6)
    cyl_axis = fs.read_ascii(3)
    mystery4 = fs.read_bytes(22)
    false_neg_den = fs.read_short()
    false_neg_num = fs.read_short()
    false_pos_den = fs.read_short()
    false_pos_num = fs.read_short()
    mystery4a = fs.read_bytes(2)
    sequence_length = fs.read_short()
    fix_loss_num = fs.read_short()
    fix_loss_den = fs.read_short()
    mystery5 = fs.read_bytes(38)
    foveal_sensitivity = fs.read_byte()
    mystery6 = fs.read_bytes(9)

    return {
        "Format (possibly)": maybe_format,
        "Patient Id": patient_id,
        "Date": _date,
        "Mystery 2": mystery2,
        "Patient Name": patient_name,
        "Patient Key": patient_key,
        "Test Pattern?": test_pattern,
        "Mystery 3": mystery3,
        "Spherical Lens Power": sph_lens_pow,
        "Cylinder Lens Power": cyl_lens_pow,
        "Cylinder Axis": cyl_axis,
        "Mystery 4": mystery4,
        "False NEG Rate Den.": false_neg_den,
        "False NEG Rate Num.": false_neg_num,
        "False POS Rate Den.": false_pos_den,
        "False POS Rate Num.": false_pos_num,
        "Mystery 4a": mystery4a,
        "Sequence Length": sequence_length,
        "Fixation Loss Num.": fix_loss_num,
        "Fixation Loss Den.": fix_loss_den,
        "Mystery 5": mystery5,
        "Foveal Sensitivity": foveal_sensitivity,
        "Mystery 6": mystery6,
    }


def _read_test_point_sequence(fs: FileStreamWrapper) -> List[RawSfaVisualFieldTestPoint]:
    def extract_stimulus_result(byte: int) -> bool:
        return (byte & 0b10000000) >> 7 == 1

    def extract_sensitivity(byte: int) -> int:
        return byte & 0b00111111

    def _test_point_iterator() -> Generator[RawSfaVisualFieldTestPoint, None, None]:
        quartile = 1
        while True:
            first_byte = fs.read_byte_signed()
            # The quartiles of the sequence are terminated with extra 0x9c (-100 signed integer) bytes
            # The lowest x-coordinate in real data is -21, so a value of -100 reliably identifies this
            if first_byte == -100:
                quartile += 1
                if quartile == 5:  # When we hit the 5th quartile we are out of the sequence
                    return
                continue

            x_coord = first_byte
            y_coord = fs.read_byte_signed()
            result_byte = fs.read_byte()

            # bit 1 is a boolean flag for seen/not seen. bit 2 is 1 iff i = 0, 14, 27, 41, meaning unknown
            # bits 3 to 8 are the sensitivity value encoded in 6-bit binary
            sensitivity = extract_sensitivity(result_byte)
            stimulus_result = extract_stimulus_result(result_byte)

            retest_byte_1 = fs.read_byte()
            retest_sensitivity = extract_sensitivity(retest_byte_1)

            retest_byte_2 = fs.read_byte()
            retest_result = extract_stimulus_result(retest_byte_2)

            # this byte is typically 0b11000000, but is different in some files and should be investigated:
            # DICO-Store1\2018\8\7\1.2.276.0.75.2.2.30.2.3.180807182507188.50126938103.1000017.dcm
            # DICO-Store1\2018\9\6\1.2.276.0.75.2.2.30.2.3.180906153841053.50126938239.1000020.dcm
            # DICO-Store1\2018\8\4\1.2.276.0.75.2.2.30.2.3.180804135537415.50128415040.1000002.dcm
            # DICO-Store1\2012\9\18\1.2.276.0.75.2.2.30.2.3.20120918093741.740.19674.dcm
            # DICO-Store1\2019\5\31\1.2.276.0.75.2.2.30.2.3.190531145205368.50126938103.1000011.dcm
            # and others
            mystery_byte = fs.read_byte()

            point_output = RawSfaVisualFieldTestPoint(
                x_coord=x_coord,
                y_coord=y_coord,
                stimulus_results="SEEN" if stimulus_result else "NOT SEEN",
                sensitivity=sensitivity,
                # the following four None values are populated later depending on the contents of the file
                retest_stimulus_seen=None,
                retest_sensitivity=None,
                supplementary_byte_1=None,
                supplementary_byte_2=None,
                mystery_byte=mystery_byte,
            )

            # this is a (hopefully) temporary means to detect if retest information exists.
            if retest_sensitivity != 0b111111:
                point_output.retest_stimulus_seen = "SEEN" if retest_result else "NOT SEEN"
                point_output.retest_sensitivity = retest_sensitivity

            yield point_output

    return list(_test_point_iterator())
