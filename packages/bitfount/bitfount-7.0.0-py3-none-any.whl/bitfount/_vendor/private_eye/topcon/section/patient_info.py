import array
from io import BytesIO
from typing import Optional

from ...data import PatientData
from ...exceptions import ImageParseException
from ..topcon_stream_wrapper import TopconStreamWrapper
from .base import FdaSection


class PatientInfoSection(FdaSection):
    """
    TODO RIPF-1591 There is a large amount of mystery data in here still.
    """

    def load(self) -> None:
        self.patient_key = self.fs.read_ascii(32)
        self.first_name = self.fs.read_topcon_string(32)
        self.last_name = self.fs.read_topcon_string(32)
        self.fs.skip(8)
        self.gender = _unmarshall_gender(self.fs.read_byte())
        self.date_of_birth = self.fs.read_date(can_return_none=True)
        self.fs.skip(40)
        self.unknown_date = self.fs.read_date(can_return_none=True)

    def to_patient_metadata(self) -> PatientData:
        return PatientData(
            patient_key=self.patient_key,
            first_name=self.first_name,
            last_name=self.last_name,
            date_of_birth=self.date_of_birth,
            gender=self.gender,
            source_id=self.patient_key,
        )


class PatientInfo03Section(PatientInfoSection):
    """
    Key extracted as follows:

    * Take two FDA files with known patient_key, first_name, last_name, etc.
    * Look at the binary diff of the patient info 03 section, differs in only a couple of places.  Suggests a
      modification which operates character by character.  However it's clearly not the same function operating on each
      character, like a rotation, so the next most obvious is XOR.
    * (Encrypted Bytes) XOR (Guessable Plaintext) = (Encryption Key).

    Since we couldn't guess the whole plaintext, we couldn't extract the whole key.  Also PatientInfo03 is shorter than
    PatientInfo02 so at some point they must diverge.
    """

    KEY = [
        # patient_key, 0x0 -> 0x20
        225,
        34,
        113,
        18,
        4,
        46,
        54,
        103,
        11,
        142,
        63,
        83,
        144,
        254,
        230,
        65,
        204,
        171,
        56,
        156,
        12,
        138,
        2,
        51,
        174,
        17,
        208,
        25,
        193,
        14,
        76,
        220,
        # first_name, 0x20 -> 0x40
        221,
        121,
        138,
        85,
        165,
        105,
        81,
        177,
        121,
        67,
        22,
        103,
        122,
        228,
        238,
        184,
        160,
        22,
        65,
        249,
        103,
        196,
        239,
        129,
        146,
        97,
        99,
        157,
        159,
        80,
        179,
        97,
        # last_name,  0x40 -> 0x60
        49,
        109,
        92,
        125,
        148,
        46,
        111,
        94,
        44,
        98,
        145,
        129,
        191,
        25,
        57,
        121,
        143,
        188,
        122,
        84,
        64,
        49,
        2,
        249,
        195,
        3,
        60,
        208,
        129,
        31,
        131,
        217,
        # Mystery, 0x60 -> 0x68, is usually zero
        45,
        60,
        187,
        22,
        14,
        34,
        163,
        141,
        # Gender
        60,
        # Date of birth (only date field), 0x6A -> 0x71
        162,
        164,
        58,
        209,
        28,
        126,
        #
        # Some more mystery x40
        234,
        89,
        17,
        194,
        10,
        138,
        93,
        165,
        160,
        116,
        67,
        118,
        209,
        203,
        216,
        189,
        196,
        148,
        142,
        249,
        119,
        154,
        111,
        205,
        115,
        48,
        23,
        149,
        56,
        78,
        183,
        75,
        209,
        171,
        72,
        102,
        196,
        210,
        250,
        149,
        #
        # # Date of first appointment???
        40,
        147,
        96,
        52,
        5,
        199,
    ]

    def load(self) -> None:
        encrypted_bytes = self.fs.read(len(PatientInfo03Section.KEY))
        plaintext = array.array("B", (b ^ k for b, k in zip(encrypted_bytes, PatientInfo03Section.KEY))).tobytes()
        self.fs: TopconStreamWrapper = TopconStreamWrapper(BytesIO(plaintext), self.options)
        super().load()


def _unmarshall_gender(gender: int) -> Optional[str]:
    """Values chosen to match http://dicomlookup.com/lookup.asp?sw=Ttable&q=C.7-1"""
    if gender == 1:
        return "M"
    if gender == 2:
        return "F"
    if gender == 3:
        # This is relatively rare, < 5% of all scans.
        # Appears in imagenet6 as a blank gender
        return None
    raise ImageParseException(f"Unknown gender: {gender}")
