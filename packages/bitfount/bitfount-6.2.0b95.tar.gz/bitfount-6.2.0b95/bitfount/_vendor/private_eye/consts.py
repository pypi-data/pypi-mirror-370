from enum import Enum, IntFlag, auto, unique
from pathlib import Path, PurePath
from typing import BinaryIO, List, Union, cast

import attr


@unique
class Laterality(str, Enum):
    """Type of scan laterality"""

    LEFT: str = "L"
    RIGHT: str = "R"

    # We see this in some Zeiss files which contain raw data pertaining to both eyes
    BINOCULAR: str = "B"
    UNKNOWN: str = "U"


@unique
class RetinalLayer(str, Enum):
    """Names of segmentations of the retinal layers"""

    ILM = "Inner Limiting Membrane"
    RNFL = "Retinal Nerve Fibre Layer"
    GCL = "Ganglion Cell Layer"
    IPL = "Inner Plexiform Layer"
    OPL = "Outer Plexiform Layer"
    E = "Ellipsoid"
    M_E = "Myoid/Ellipsoid"
    OS = "Outer Segment"
    RPE = "Retinal Pigment Epithelium"
    BM = "Bruch's Membrane"
    INL = "Inner Nuclear Layer"
    ELM = "External Limiting Membrane"


@unique
class CornealLayer(str, Enum):
    """Names of layers of the cornea"""

    EP = "Epithelium"
    END = "Endothelium"
    BOW = "Bowman's"


class ModalityFlag(IntFlag):
    NONE = 0
    IS_COLOUR = auto()
    IS_2D_IMAGE = auto()
    # We can use modalities to guess whether certain images are exterior/anterior
    IS_ANTERIOR = auto()
    IS_INTERIOR = auto()
    # Images which could contain sensitive data, e.g. face photos, or identifiable text
    POTENTIALLY_SENSITIVE = auto()


@unique
class ImageModality(Enum):
    COLOUR_PHOTO = ("CP", "Colour Photo", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_COLOUR)
    INFRARED_PHOTO = ("IRP", "Infrared Photo", ModalityFlag.IS_2D_IMAGE)

    # Scanning laser ophthalmoscopy.
    SLO_RED = ("SLO_R", "SLO - Red", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    SLO_GREEN = ("SLO_G", "SLO - Green", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    SLO_BLUE = ("SLO_B", "SLO - Blue", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    SLO_INFRARED = ("SLO_IR", "SLO - Infrared", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    SLO_INFRARED_CROSS_POLARIZED = (
        "SLO_IR_XP",
        "SLO - Infrared (cross-polarized)",
        ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR,
    )

    FLUORESCEIN_ANGIOGRAPHY = ("FA", "FA", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    INDOCYANINE_GREEN_ANGIOGRAPHY = ("ICGA", "ICGA", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    RED_FREE = ("RF", "Red-free", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    RED_FREE_CROSS_POLARIZED = (
        "RF_XP",
        "Red-free (cross-polarized)",
        ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR,
    )

    AUTOFLUORESCENCE_BLUE = ("AF_B", "AF - Blue", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    AUTOFLUORESCENCE_GREEN = ("AF_G", "AF - Green", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)
    AUTOFLUORESCENCE_IR = ("AF_IR", "AF - Infrared", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)

    REFLECTANCE_RED = ("REF_R", "Reflectance - Red", ModalityFlag.IS_2D_IMAGE)
    REFLECTANCE_GREEN = ("REF_G", "Reflectance - Green", ModalityFlag.IS_2D_IMAGE)
    REFLECTANCE_BLUE = ("REF_B", "Reflectance - Blue", ModalityFlag.IS_2D_IMAGE)
    REFLECTANCE_BLUE_CROSS_POLARIZED = ("REF_B_XP", "Reflectance - Blue (cross-polarized)", ModalityFlag.IS_2D_IMAGE)
    REFLECTANCE_IR = ("REF_IR", "Reflectance - Infrared", ModalityFlag.IS_2D_IMAGE)

    OCT = ("OCT", "OCT")

    CORNEA_MICROSCOPY = ("CM", "Cornea Microscopy")
    MPOD = ("MPOD", "MP Optical Density")

    HR_TOMOGRAPHY = ("HRT", "HR Tomography")

    SLIT_LAMP = ("SLIT", "Slit Lamp", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_ANTERIOR)
    RED = ("RED", "Red", ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_INTERIOR)

    FACE_PHOTO = (
        "FACE",
        "Face photo",
        ModalityFlag.IS_2D_IMAGE | ModalityFlag.IS_ANTERIOR | ModalityFlag.POTENTIALLY_SENSITIVE,
    )

    # VF-related modalities
    FDF = ("FDF", "Flicker Defined Form Perimetry")
    SAP = ("SAP", "Standard Automated Perimetry")

    # Values which are not real images or may contain sensitive data.
    # Librarian will want to ignore these
    MPOD_RESULT = ("MPODR", "MP Optical Density Result")
    THICKNESS = ("T", "Thickness")
    CELL_ANALYSIS = ("CELL", "Cell Analysis")
    ENCAPSULATED_PDF = ("PDF", "PDF", ModalityFlag.POTENTIALLY_SENSITIVE)

    # Mark this as 'sensitive' as we just don't know what data could be in here
    UNKNOWN = ("U", "Unknown", ModalityFlag.POTENTIALLY_SENSITIVE)

    flags: ModalityFlag
    code: str

    def __new__(cls, code: str, description: str, flags: ModalityFlag = ModalityFlag.NONE) -> "ImageModality":
        # This is the canonical way of overriding handling of the enum value.
        # See https://docs.python.org/3/library/enum.html#using-a-custom-new
        obj = object.__new__(cls)
        # Use the long-form as the value as it is likely to be more useful than the short-hand code
        obj._value_ = description
        obj.code = code
        obj.flags = flags
        return cast("ImageModality", obj)

    def __str__(self) -> str:
        return cast(str, self.value)

    @property
    def is_colour(self) -> bool:
        return ModalityFlag.IS_COLOUR in self.flags

    @property
    def is_2d_image(self) -> bool:
        return ModalityFlag.IS_2D_IMAGE in self.flags

    @property
    def potentially_sensitive(self) -> bool:
        return ModalityFlag.POTENTIALLY_SENSITIVE in self.flags


@unique
class Fixation(str, Enum):
    """Type of fixation of a scan"""

    CENTER: str = "Center"
    DISK: str = "Disk"
    MACULAR: str = "Macular"
    WIDE: str = "Wide"
    EXTERNAL: str = "External"


@unique
class SectionName(Enum):
    """Enumeration representing the different sections which can be returned"""

    # Patient information. Corresponds to the :class:`PatientData` class.
    PATIENT: str = "patient"

    # Exam information. Corresponds to the :class:`ExamData` class.
    EXAM: str = "exam"

    # Series information. Corresponds to the :class:`SeriesData` class.
    SERIES: str = "series"

    # Images and associated data. Corresponds to the :class:`ImagesData` class.
    IMAGES: str = "images"

    # Visual field information. Corresponds to the :class:`VisualFieldData` class.
    VISUAL_FIELD: str = "visual_field"

    # Debug information about the image. Corresponds to the :class:`DebugData` class.
    DEBUG: str = "debug"


class RequiresFiles(Exception):
    def __init__(self, files: List[PurePath]) -> None:
        self.files = files
        super().__init__(f"Missing {', '.join(path.name for path in files)}")


class NoImageData(Exception):
    pass


@attr.s(auto_attribs=True, frozen=True)
class InputFile:
    """
    input_files: The path to the image file on disk.
    original_filepath: The original file path, if the file being passed in is a temporary copy or similar.  This
    is useful for file parsers like Optos which process the filepath itself.
    """

    file_path: Path
    original_filepath: PurePath

    @classmethod
    def local_file(cls, file_path: Union[Path, str]) -> "InputFile":
        if isinstance(file_path, str):
            file_path = Path(file_path)
        return cls(file_path, file_path)


@attr.s(auto_attribs=True, frozen=True)
class InputFileHandle:
    file_path: Path
    original_filepath: PurePath
    handle: BinaryIO


@unique
class EntireFileOutputFormat(Enum):
    H5_GOOGLE_OCT: str = "h5_google_oct"
    H5_GOOGLE_FA: str = "h5_google_fa"
    H5_GOOGLE_ICGA: str = "h5_google_icga"
    METADATA_JSON: str = "metadata_json"
    METADATA_CONSOLE: str = "metadata_console"
    RAW_FILES: str = "raw_files"
    DEBUG_IMAGES: str = "debug_images"
    NONE: str = "no_output"


@unique
class IndividualImageOutputFormat(Enum):
    DICOM: str = "dicom"
    H5: str = "h5"
    RAW_IMAGES: str = "raw_images"


OutputFormat = Union[EntireFileOutputFormat, IndividualImageOutputFormat]
