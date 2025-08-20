"""Handler classes for Zeiss Ophthalmology dicoms."""

from enum import Enum
import logging
import math
import typing
from typing import Any, Dict, Final, List, Optional, Set, Tuple

# EXDCM files contain invalid null chars in certain tag strings (see _strip_null_chars)
# pydicom complains each time dcmread is called on an EXDCM file --> suppressing for now
import warnings

import cv2
import numpy as np
from pydicom import Dataset, Sequence
from pydicom.dataelem import DataElement
from pydicom.encaps import generate_pixel_data_frame
from pydicom.tag import BaseTag, Tag, TagType
import pydicom.uid
from pydicom.valuerep import VR

from bitfount.data.datasources.dicom_source import (
    DICOM_IMAGE_ATTRIBUTE,
    DICOM_LATERALITY_POSSIBLE_FIELDS,
)
from bitfount.data.exceptions import DataSourceError

warnings.filterwarnings("ignore", module="pydicom")

logger = logging.getLogger(__name__)


class ZeissDcmTags:
    """Tag values for relevant elements of Zeiss Dcm."""

    IMAGE = Tag((0x0407, 0x1005))
    FRAME = Tag((0x0407, 0x1006))
    PIXEL_SPACING_1 = Tag((0x0407, 0x100A))
    PIXEL_SPACING_2 = Tag((0x0407, 0x100B))
    PIXEL_SPACING_3 = Tag((0x0407, 0x100C))
    PIXEL_X = Tag((0x0407, 0x1001))
    PIXEL_Y = Tag((0x0407, 0x1002))
    NUM_FRAMES = Tag((0x0407, 0x1003))
    CZM_OCT_HIDEF = Tag((0x0407, 0x10A0))
    CZM_OCT_CUBE = Tag((0x0407, 0x10A1))
    CZM_OCT_MOTION = Tag((0x0407, 0x10A2))
    CZM_OCT_NOISE = Tag((0x0407, 0x10A3))
    CZM_OCT_FUNDUS = Tag((0x0407, 0x10A6))
    CZM_OCT_ENFACE = Tag((0x0407, 0x10A7))
    CZM_OCT_IRIS = Tag((0x0407, 0x10B5))
    PRIVATE_IMAGE_NAMES = Tag((0x2201, 0x1002))


class ImageName(str, Enum):
    """Image types string enum."""

    CzmOctHiDef = "CzmOctHiDef"
    CzmOctCube = "CzmOctCube"
    CzmOctMotion = "CzmOctMotion"
    CzmOctNoise = "CzmOctNoise"
    CzmOctFundus = "CzmOctFundus"
    CzmOctEnface = "CzmOctEnface"
    CzmOctIris = "CzmOctIris"


class ZeissDcmMisc:
    """Misc definitions required for reading Zeiss Dcm files."""

    RETINAL_SERIES_DESCRIPTIONS = ["Macular Cube 512x128", "Optic Disc Cube 200x200"]

    IMAGETAG_TO_IMAGENAME = {
        ZeissDcmTags.CZM_OCT_HIDEF: ImageName.CzmOctHiDef,
        ZeissDcmTags.CZM_OCT_CUBE: ImageName.CzmOctCube,
        ZeissDcmTags.CZM_OCT_MOTION: ImageName.CzmOctMotion,
        ZeissDcmTags.CZM_OCT_NOISE: ImageName.CzmOctNoise,
        ZeissDcmTags.CZM_OCT_FUNDUS: ImageName.CzmOctFundus,
        ZeissDcmTags.CZM_OCT_ENFACE: ImageName.CzmOctEnface,
        ZeissDcmTags.CZM_OCT_IRIS: ImageName.CzmOctIris,
    }


class ZeissExdcmTags(BaseTag):
    """Tag values for relevant elements of Zeiss ExDcm."""

    MANUFACTURER = Tag((0x0008, 0x0070))
    SPACING_BETWEEN_SLICES = Tag((0x0018, 0x0088))
    LATERALITY = Tag((0x0020, 0x0060))
    PHOTOMETRIC_INTERPRETATION = Tag((0x0028, 0x0004))
    NUMBER_OF_FRAMES = Tag((0x0028, 0x0008))
    ROWS = Tag((0x0028, 0x0010))
    COLUMNS = Tag((0x0028, 0x0011))
    SERIES_DESCRIPTION = Tag((0x0008, 0x0104))
    PIXEL_SPACING = Tag((0x0028, 0x0030))
    PATIENTS_BIRTH_DATE = Tag((0x0010, 0x0030))
    PATIENT_NAME = Tag((0x0010, 0x0010))
    PATIENTS_SEX = Tag((0x0010, 0x0040))
    ACQUISITION_DATE_TIME = Tag((0x0008, 0x002A))
    STUDY_DATE = Tag((0x0008, 0x0020))
    MANUFACTURERS_MODEL_NAME = Tag((0x0008, 0x1090))


class ZeissExdcmMisc:
    """Misc definitions required for reading Zeiss ExDcm files."""

    # Note: these are the image dimensions as stated in the EXDCM metadata
    # (NumberOfFrames, Rows, Columns)
    SHAPE_TO_MODALITY: Dict[str, Dict[Tuple[Optional[int], int, int], str]] = {
        "Macular Cube 512x128": {
            (2, 1024, 1024): ImageName.CzmOctHiDef,
            (None, 512, 1024): ImageName.CzmOctNoise,
            (None, 480, 640): ImageName.CzmOctIris,
            (128, 512, 1024): ImageName.CzmOctCube,
            (128, 1024, 512): ImageName.CzmOctCube,
            (None, 128, 512): ImageName.CzmOctEnface,
            (2, 512, 1024): ImageName.CzmOctMotion,
            (None, 512, 664): ImageName.CzmOctFundus,
        },
        "Optic Disc Cube 200x200":
        # CzmOctHiDef is not acquired in Optic Disc scan protocol
        {
            (None, 200, 1024): ImageName.CzmOctNoise,
            (None, 480, 640): ImageName.CzmOctIris,
            (200, 1024, 200): ImageName.CzmOctCube,
            (None, 200, 200): ImageName.CzmOctEnface,
            (2, 200, 1024): ImageName.CzmOctMotion,
            (None, 512, 664): ImageName.CzmOctFundus,
        },
    }

    MODEL_NAME_MAPPING = {"5000": "CIRRUS HD-OCT 5000", "6000": "CIRRUS HD-OCT 6000"}

    EXDCM_METADATA: Dict[str, Tuple[BaseTag, typing.Callable]] = {
        "Columns": (ZeissExdcmTags.COLUMNS, lambda x: int(x)),
        "Rows": (ZeissExdcmTags.ROWS, lambda x: int(x)),
        "Pixel Spacing Row": (
            ZeissExdcmTags.PIXEL_SPACING,
            lambda x: (float(x.strip("[]").split(",")[0]) if "," in x else None),
        ),
        "Pixel Spacing Column": (
            ZeissExdcmTags.PIXEL_SPACING,
            lambda x: (float(x.strip("[]").split(",")[1]) if "," in x else None),
        ),
        "Slice Thickness": (
            ZeissExdcmTags.SPACING_BETWEEN_SLICES,
            lambda x: float(x),
        ),
        "Number of Frames": (
            ZeissExdcmTags.NUMBER_OF_FRAMES,
            lambda x: int(x),
        ),
        "Patient's Birth Date": (ZeissExdcmTags.PATIENTS_BIRTH_DATE, lambda x: str(x)),
        "Patient's Sex": (ZeissExdcmTags.PATIENTS_SEX, lambda x: str(x)),
        "Patient's Name": (ZeissExdcmTags.PATIENT_NAME, lambda x: str(x)),
        "Scan Laterality": (ZeissExdcmTags.LATERALITY, lambda x: str(x)),
        "Acquisition DateTime": (
            ZeissExdcmTags.ACQUISITION_DATE_TIME,
            lambda x: str(x),
        ),
        "Study Date": (ZeissExdcmTags.STUDY_DATE, lambda x: str(x)),
        "Manufacturer": (ZeissExdcmTags.MANUFACTURER, lambda x: str(x)),
        "Manufacturer's Model Name": (
            ZeissExdcmTags.MANUFACTURERS_MODEL_NAME,
            lambda x: str(x),
        ),
        "Series Description": (ZeissExdcmTags.SERIES_DESCRIPTION, lambda x: str(x)),
        "Photometric Interpretation": (
            ZeissExdcmTags.PHOTOMETRIC_INTERPRETATION,
            lambda x: str(x),
        ),
    }


# See:
#   - https://pydicom.github.io/pydicom/stable/guides/element_value_types.html
#   - https://dicom.nema.org/medical/dicom/current/output/html/part05.html#table_6.2-1
_NUM_STR_VR: Final[set[str]] = {
    VR.DS,  # Decimal String
    VR.IS,  # Integer String
}

# https://dicom.nema.org/medical/dicom/current/output/chtml/part17/chapter_U.html
_LATERALITY_CODE_MAP: Final[dict[str, str]] = {
    "OS": "L",
    "OD": "R",
    "OU": "B",
}

# The character that generally seems to indicate the end of the "valid" string and
# the start of the invalid Zeiss-specific suffix
_ZEISS_STRING_INVALID_DELIM: Final[str] = "\0"

_ZEISS_MANUFACTURER_PREFIX: Final[str] = "Carl Zeiss Meditec"

# Max size of pixel data allowed in a non-extended DICOM file
_MAX_BASIC_OFFSET_SIZE: Final[int] = 2**32 - 1


def czm_data_sanitization(dataset: Dataset, dataelement: DataElement) -> None:
    """Callback sanitization function for CZM DICOMs.

    Should be used with pydicom.Dataset.walk().

    Args:
        dataset: the dataset being used in the callback.
        dataelement: the individual DICOM element that is currently being inspected.
    """
    # DICOMs generated by Zeiss devices often contain non-standard data entries,
    # normally containing \x00 and other hex characters at the of the "normal" entry.
    # In order to ensure that these DICOMs are parsable/used properly, we need to
    # apply some "best-effort" sanitization to the fields.
    #
    # We only concern ourselves with fields with "str" values as these are what the
    # expected type is for fields that Zeiss has added the "\x00" characters to;
    # their additions force these fields to have string values, even if pydicom
    # should instead parse it to other types.
    #
    # The sanitization has a cascading structure where multiple sanitization rules
    # may be applied to the same fields; this is by design to allow the most general
    # fixes to be applied first, then more specific ones for different types.

    # Do not sanitize pixel spacing, this is handled later
    if dataelement.tag == ZeissExdcmTags.PIXEL_SPACING:
        return

    # Sanitization 1: General string fix
    # If something is already a string, we can try to extract the values directly. We
    # want to get the portion of the string before the first "illegal" character,
    # which always seems to be "\x00".
    if dataelement.VM > 1:
        new_multi_value = []
        for sub_elem in dataelement.value:
            if isinstance(dataelement.value, str):
                # This will append the original value if we've not been able to split it
                new_multi_value.append(sub_elem.split(_ZEISS_STRING_INVALID_DELIM)[0])
        try:
            dataelement.value = new_multi_value
        except ValueError:
            # Even post-sanitization, some elements will not accept list[str] as
            # their input. These are handled explicitly elsewhere.
            pass
    # If there's only a single element as the value, work on that directly
    elif isinstance(dataelement.value, str):
        try:
            dataelement.value = dataelement.value.split(_ZEISS_STRING_INVALID_DELIM)[0]
        except ValueError:
            # Even post-sanitization, some elements will not accept str as their
            # input. These are handled explicitly elsewhere.
            pass

    # Sanitization 2: Number string fixes, in particular multi-value number strings
    #                 (e.g. "5.0,6.0")
    # Decimal/Integer strings, particularly those of >1 multiplicity, may not have
    # been set/parsed correctly due to the sanitization issues, and so we may need to
    # reset these (pydicom will then handle the conversion to the correct storage type).
    if dataelement.VR in _NUM_STR_VR:
        if isinstance(dataelement.value, str):
            # The previous block may not have handled the sanitization (for instance if
            # the sanitized str could not be set on the value), so we attempt it again
            # here just in case.
            sanitized: str = dataelement.value.split(_ZEISS_STRING_INVALID_DELIM)[0]
            split_value: list[str] = [s.strip() for s in sanitized.split(",")]

            # Want to set list[str] only if more than one element
            if len(split_value) > 1:
                dataelement.value = split_value
            else:
                dataelement.value = split_value[0]

    # Sanitization 3: Person Name fixes
    # Elements that are identified as PN (Person Name) will already have been
    # partially parsed and stored as a PersonName instance. Due to this, they will
    # have been skipped in the first pass to fix "\x00" strings.
    if dataelement.VR == VR.PN:
        old_name: str = str(dataelement.value)
        # pydicom will handle the value-setter converting the string into a new
        # PersonName instance
        dataelement.value = old_name.split(_ZEISS_STRING_INVALID_DELIM)[0]

    # Sanitization 4: Laterality field mapping
    # Laterality-related fields in Zeiss often use OS, OD, and OU, instead of the
    # standard's form of L, R, or B, respectively. To ensure compatibility with the
    # standard/with DICOMs from other sources, we need to map these fields. See:
    # https://dicom.nema.org/medical/dicom/current/output/chtml/part17/chapter_U.html
    if dataelement.name in DICOM_LATERALITY_POSSIBLE_FIELDS:
        if isinstance(dataelement.value, str):
            try:
                dataelement.value = _LATERALITY_CODE_MAP[dataelement.value]
            except KeyError:
                # This means it wasn't a field we know how to map, so just ignore it
                pass


class CZMError(DataSourceError):
    """Errors related to processing of Zeiss DICOMs."""

    pass


class ZeissCirrusBase:
    """Base class for extracting image data from the Zeiss CIRRUS.

    Attributes:
        ds (Dataset): pydicom dataset object of the Zeiss .dcm/.EX.DCM file
        Following read_data():
            self.metadata (dict)

    """

    def __init__(self, ds: Dataset, desired_image_type: str = "CzmOctCube"):
        if ds.file_meta:
            ds.file_meta.walk(czm_data_sanitization)
        ds.walk(czm_data_sanitization)
        self.ds = ds
        self.desired_image_type = desired_image_type
        self.image_types: Set[str] = set()
        self.manufacturer: Optional[str] = None
        self.metadata: Dict[str, Any] = dict()
        self.final_image: Optional[np.ndarray] = None

    def _metadata_preprocess(self) -> None:
        """Method to extract metadata and prepare image data."""
        raise NotImplementedError

    def _unscramble_images(self) -> None:
        """Unscramble the obfuscated Zeiss image data."""
        raise NotImplementedError

    def _transform_images(
        self, arr_list: List[np.ndarray], image_name: str
    ) -> Optional[np.ndarray]:
        """Apply transforms to make images look similar to the Zeiss FORUM viewer.

        Rotations/flips only, no changes to brightness/contrast etc.
        """
        rotated_image_names = [
            ImageName.CzmOctFundus,
            ImageName.CzmOctNoise,
            ImageName.CzmOctCube,
            ImageName.CzmOctHiDef,
            ImageName.CzmOctMotion,
        ]
        if arr_list[0] is not None:
            if image_name in rotated_image_names:
                self._invert_metadata_rows_columns()

            if len(arr_list) == 1:
                transformed_arr = arr_list[0]

                if image_name == ImageName.CzmOctFundus:
                    # Transformation to make retinal fundus image similar
                    # to FORUM viewer:
                    # 1) 90 degrees clockwise rotation
                    transformed_arr = np.rot90(transformed_arr, k=3)

                # This code is commented out because we currently do not
                # have examples of these files in our test suite, but may be useful
                # in the future
                # Code written by Dom, Mar 2025

                # elif image_name == ImageName.CzmOctIris:
                #     # Not visible in FORUM, but can still correctly orient iris photo:
                #     # 1) horizontal flip [AAA|BBB] -> [BBB|AAA]
                #     transformed_arr = np.flip(transformed_arr, axis=1)
                # elif image_name == ImageName.CzmOctEnface:
                #     # Enface does not require any rotation/flip, but we
                #     # expand to a square for visualising
                #     max_dim = max(transformed_arr.shape)
                #     transformed_arr = cv2.resize(
                #         transformed_arr,
                #         (max_dim, max_dim),
                #         interpolation=cv2.INTER_NEAREST,
                #     )
                #     self.metadata["Rows"] = max_dim
                #     self.metadata["Columns"] = max_dim
                # elif image_name == ImageName.CzmOctNoise:
                #     # Not visible in FORUM, but can still correctly
                #     orient to match OCT:
                #     # 1) 90 degree clockwise rotation
                #     transformed_arr = np.rot90(transformed_arr, k=3)
                transformed_arr = transformed_arr.astype(np.uint8)

                # All 2D images are greyscale, so only one channel needed
                transformed_arr = transformed_arr[:, :, 0]
                # unscrambled_frame = Image.fromarray(unscrambled_frame, 'L')
                # For PrivateEye, we want np.ndarrays as output

                # Add a dimension to the single 2d frame, to match
                # shape of 3d image
                return np.expand_dims(transformed_arr, axis=0)

            elif len(arr_list) > 1:
                transformed_volume = np.array(arr_list, dtype=np.uint8)
                if image_name == ImageName.CzmOctCube:
                    # Transformations to make retinal OCT similar to FORUM viewer:
                    # 1) rotate 90 deg CW 2) horizontal flip 3) reverse order of bscans
                    transformed_volume = np.rot90(transformed_volume, axes=(1, 2), k=3)
                    transformed_volume = np.flip(transformed_volume, axis=2)
                    transformed_volume = np.flip(transformed_volume, axis=0)

                # This code is commented out because we currently do not
                # have examples of these files in our test suite, but may be useful
                # in the future
                # Code written by Dom, Mar 2025
                # elif image_name == ImageName.CzmOctHiDef:
                #     #Transformations to make retinal hidef OCT similar to FORUM viewer
                #     # 1) rotate 90 deg CW, 2) horizontal flip ONLY in slice 0
                #     transformed_volume = np.rot90(transformed_volume,axes=(1, 2),k=3)
                #     transformed_volume[0] = np.flip(transformed_volume[0], axis=1)
                # elif image_name == ImageName.CzmOctMotion:
                #     # Not visible in FORUM but can still correctly orient to match OCT
                #     # (Assume same as CzmOctHiDef)
                #     # 1)90 degree clockwise rotation 2)horizontal flip ONLY in slice 0
                #     transformed_volume = np.rot90(transformed_volume, axes=(1, 2),k=3)
                #     transformed_volume[0] = np.flip(transformed_volume[0], axis=1)

                return transformed_volume
        return None

    def _invert_metadata_rows_columns(self) -> None:
        """Swap rows and columns value due to rotation of image."""
        rows, cols = self.metadata.get("Rows"), self.metadata.get("Columns")
        self.metadata["Rows"], self.metadata["Columns"] = (
            cols,
            rows,
        )

    def _unscramble_frame(self, original_frame: bytes) -> bytearray:
        """Return an unscrambled image frame.

        Thanks to https://github.com/scaramallion
        for the code, as detailed in https://github.com/pydicom/pydicom/discussions/1618.

        Args:
        original_frame (bytes): The scrambled CZM JPEG 2000 data frame as found in
          the DICOM dataset.

        Returns:
        bytearray: The unscrambled JPEG 2000 data.
        """
        # Fix the 0x5A XORing
        frame = bytearray(original_frame)
        for ii in range(0, len(frame), 7):
            frame[ii] = frame[ii] ^ 0x5A

        # Offset to the start of the JP2 header - empirically determined
        jp2_offset = math.floor(len(frame) / 5 * 3)

        # Double check that our empirically determined jp2_offset is correct
        offset = frame.find(b"\x00\x00\x00\x0c")
        if offset == -1:
            raise CZMError("No JP2 header found in the scrambled pixel data")

        if offset != jp2_offset:
            jp2_offset = offset

        d = bytearray()
        d.extend(frame[jp2_offset : jp2_offset + 253])
        d.extend(frame[993:1016])
        d.extend(frame[276:763])
        d.extend(frame[23:276])
        d.extend(frame[1016:jp2_offset])
        d.extend(frame[:23])
        d.extend(frame[763:993])
        d.extend(frame[jp2_offset + 253 :])

        if len(d) != len(frame):
            raise CZMError("Unscrambled frame is not of the same length")
        else:
            return d

    def _add_image_to_metadata(self) -> None:
        """Add image data frame-by-frame to metadata dictionary."""
        if self.final_image is None:
            raise CZMError("No final image found")

        number_frames = self.metadata["Number of Frames"]
        if number_frames != self.final_image.shape[0]:
            raise CZMError(
                f"Number of Frames ({number_frames}) does not "
                f"match pixel data (shape: {self.final_image.shape})"
            )

        for frame_number, frame_arr in enumerate(self.final_image):
            self.metadata[f"{DICOM_IMAGE_ATTRIBUTE} {frame_number}"] = frame_arr

    @property
    def image_is_valid(self) -> bool:
        """Image is valid if image type in dicom matches the intended type."""
        return self.desired_image_type in self.image_types

    def get_data(self, stop_before_pixels: bool = False) -> Optional[dict]:
        """Return the pixel data of the OCT Cube scan.

        If there are multiple OCT Cube scans in the file, the one with the most
        number of frames is returned.
        If there are no OCT Cube images, return None

        """
        if self.manufacturer != "Carl Zeiss Meditec":
            logger.warning(
                f"Not a Zeiss dicom, manufacturer is {self.manufacturer}. Skipping."
            )
            return None

        self._metadata_preprocess()

        log_image_types = ", ".join(self.image_types)

        if self.image_is_valid:
            if not stop_before_pixels:
                self._unscramble_images()
                self._add_image_to_metadata()

            # Log other types of images present in the Dicom
            if len(self.image_types) > 1:
                logger.info(f"Dicom Image contains types {log_image_types}.")

            return self.metadata

        logger.info(
            f"Dicom Image is of type {log_image_types}, "
            f"not {self.desired_image_type}. Skipping."
        )
        return None


class ZeissCirrusDcm(ZeissCirrusBase):
    """Class for extracting OCT pixel data from the Zeiss CIRRUS .dcm file format."""

    def __init__(self, ds: Dataset, desired_image_type: str = "CzmOctCube"):
        super().__init__(ds, desired_image_type)
        self.manufacturer = self.ds.get("Manufacturer")
        self.image_data_element: Optional[DataElement] = None

    def get_data(self, stop_before_pixels: bool = False) -> Optional[dict]:
        """Performs checks on data before reading data."""
        # Require RawDataStorage to avoid Encapsulated PDF Storage etc.
        if (sop_class_uid := self.ds.get("SOPClassUID")) != pydicom.uid.RawDataStorage:
            logger.info(
                f"DCM does not have RawDataStorage SOP Class UID, has {sop_class_uid}."
                f" Skipping."
            )
            return None
        # Check SeriesDescription for Macular/Optic Disc Cube
        series_description = self.ds.get("SeriesDescription", "None")
        if not any(
            opt in series_description for opt in ("Macular Cube", "Optic Disc Cube")
        ):
            logger.info(
                f"DCM is not a macular or optic disc-centered OCT scan,"
                f" was {series_description}."
                f" Skipping."
            )
            return None

        return super().get_data()

    def _find_image_data_element(
        self,
        dataset: Dataset,
        tag_to_find: TagType = ZeissDcmTags.IMAGE,
        parent: Optional[DataElement] = None,
        latest_image_name: Optional[str] = None,
    ) -> None:
        """Recursively search for the required Zeiss .dcm image data element.

        Stores the parent data element for the wanted image type
        in self.image_data_element.
        """
        for data_element in dataset:
            if data_element.tag == tag_to_find:
                if isinstance(latest_image_name, str):
                    self.image_types.add(latest_image_name)
                if latest_image_name == self.desired_image_type:
                    # If this tag is one we are searching for, add the parent data
                    # element (if any) to the list
                    # We want the parent because it contains relevant metadata
                    if parent:
                        self.image_data_element = parent[0]
                    else:
                        self.image_data_element = data_element[0]

            x = ZeissDcmMisc.IMAGETAG_TO_IMAGENAME.get(data_element.tag)
            if x is not None:
                latest_image_name = x

            if hasattr(data_element, "value") and isinstance(
                data_element.value, Sequence
            ):
                for item in data_element.value:
                    # Recursively search within the nested dataset
                    self._find_image_data_element(
                        item,
                        tag_to_find,
                        parent=data_element,
                        latest_image_name=latest_image_name,
                    )

    def _unscramble_images(self) -> None:
        """Unscramble each image type."""
        data_element = self.image_data_element
        if data_element is None:
            raise ValueError("No data element found for .dcm file")

        pixel_data = data_element[ZeissDcmTags.IMAGE]
        image = self._process_pixel_data(pixel_data)
        if image is not None and all(arr is not None for arr in image):
            self.final_image = self._transform_images(image, self.desired_image_type)

    def _metadata_preprocess(self) -> None:
        """Reads metadata for each imaging modality in .dcm file."""

        self._find_image_data_element(self.ds)

        if self.image_data_element is None:
            return

        data_element = self.image_data_element

        pixels_x = int(data_element[ZeissDcmTags.PIXEL_X].value)
        pixels_y = int(data_element[ZeissDcmTags.PIXEL_Y].value)
        number_of_frames = int(data_element[ZeissDcmTags.NUM_FRAMES].value)
        pixel_spacing = [
            float(data_element[ZeissDcmTags.PIXEL_SPACING_2].value),
            float(data_element[ZeissDcmTags.PIXEL_SPACING_1].value),
        ]
        slice_thickness = float(data_element[ZeissDcmTags.PIXEL_SPACING_3].value)

        # floats/ints
        self.metadata["Columns"] = pixels_y
        self.metadata["Rows"] = pixels_x
        self.metadata["Pixel Spacing Row"] = pixel_spacing[0]
        self.metadata["Pixel Spacing Column"] = pixel_spacing[1]
        self.metadata["Slice Thickness"] = slice_thickness
        self.metadata["Number of Frames"] = number_of_frames

        # strings
        self.metadata["Patient's Birth Date"] = self.ds.get("PatientBirthDate")
        self.metadata["Patient's Sex"] = self.ds.get("PatientSex")
        self.metadata["Patient's Name"] = self._sanitize_name(
            str(self.ds.get("PatientName"))
        )
        self.metadata["Scan Laterality"] = self.ds.get("Laterality")
        self.metadata["Acquisition DateTime"] = self.ds.get("AcquisitionDateTime")
        self.metadata["Study Date"] = self.ds.get("StudyDate")
        self.metadata["Manufacturer"] = self.ds.get("Manufacturer")
        self.metadata["Manufacturer's Model Name"] = self.ds.get(
            "ManufacturerModelName"
        )
        self.metadata["Series Description"] = self.ds.get("SeriesDescription")
        self.metadata["Photometric Interpretation"] = self.ds.get(
            "PhotometricInterpretation"
        )
        self.metadata["Modality"] = self.desired_image_type

    def _sanitize_name(self, name: str) -> str:
        """Remove '^' characters from person's name."""
        return name.replace("^", " ")

    def _process_pixel_data(
        self, data_element: DataElement
    ) -> Optional[List[np.ndarray]]:
        """Process 2D and 3D image data elements."""
        num_frames = len(data_element.value)
        if num_frames == 1:
            scrambled_frame = data_element[0][ZeissDcmTags.FRAME]
            unscrambled_bytes = self._unscramble_frame(scrambled_frame)
            if unscrambled_bytes:
                unscrambled_frame = cv2.imdecode(
                    np.frombuffer(unscrambled_bytes, np.uint8), flags=1
                )
                return [unscrambled_frame]
            else:
                raise CZMError("Unable to unscramble single frame")
        else:  # volume/multiframe image
            unscrambled_volume = []
            for frame in data_element:  # type: ignore[attr-defined]  # reason: complains not iterable but it is # noqa: E501
                scrambled_frame = frame[ZeissDcmTags.FRAME]
                unscrambled_bytes = self._unscramble_frame(scrambled_frame)
                if unscrambled_bytes:
                    unscrambled_frame = cv2.imdecode(
                        np.frombuffer(unscrambled_bytes, np.uint8), flags=1
                    )
                    unscrambled_volume.append(unscrambled_frame)
                else:
                    raise CZMError("Unable to unscramble frame in multiframe image")

            return unscrambled_volume


class ZeissCirrusExdcm(ZeissCirrusBase):
    """Class for extracting data from Zeiss's .EX.DCM file format."""

    def __init__(self, ds: Dataset, desired_image_type: str = "CzmOctCube"):
        super().__init__(ds, desired_image_type)

        self.manufacturer = self._strip_null_chars(str(self.ds.get("Manufacturer")))

    def _unscramble_images(self) -> None:
        """Unscramble PixelData from .EX.DCM file."""
        num_frames = self.metadata.get("Number of Frames")
        if num_frames and num_frames > 1:
            frames = generate_pixel_data_frame(self.ds.PixelData, num_frames)
            unscrambled_frame_list: List[np.ndarray] = []
            for _idx, scrambled_frame in enumerate(frames):
                # try decoding without unscrambling
                unscrambled_frame: Optional[np.ndarray] = cv2.imdecode(
                    np.frombuffer(scrambled_frame, np.uint8), flags=1
                )
                if unscrambled_frame is None:
                    unscrambled_bytes = self._unscramble_frame(scrambled_frame)
                    if unscrambled_bytes:
                        unscrambled_frame = cv2.imdecode(
                            np.frombuffer(unscrambled_bytes, np.uint8), flags=1
                        )
                    else:
                        raise CZMError(f"Unable to unscramble frame number {_idx}")
                unscrambled_frame_list.append(unscrambled_frame)
        else:
            # 2D
            unscrambled_bytes = self._unscramble_frame(self.ds.PixelData)
            if unscrambled_bytes:
                unscrambled_frame = cv2.imdecode(
                    np.frombuffer(unscrambled_bytes, np.uint8), flags=1
                )
                unscrambled_frame_list = [unscrambled_frame]
            else:
                raise CZMError("Unable to unscramble single frame")

        self.final_image = self._transform_images(
            unscrambled_frame_list, self.desired_image_type
        )

    def _metadata_preprocess(self) -> None:
        """Reads metadata from EX.DCM file."""
        if "PixelData" not in self.ds:
            logger.info("This EX.DCM file is not an image file")
            return

        for tag_name, (
            tag_to_search,
            transformation_func,
        ) in ZeissExdcmMisc.EXDCM_METADATA.items():
            value_list = self._retrieve_nested_dicom_values(
                self.ds, tag_to_search
            )  # If not found, returns empty list
            if value_list:
                if tag_name == "Series Description":
                    value_list = [self._strip_null_chars(str(v)) for v in value_list]
                    self.metadata["Series Description"] = (
                        self._process_series_description(value_list)
                    )
                else:
                    if len(value_list) == 1:
                        value = value_list[0]  # single value
                        value = self._strip_null_chars(str(value))
                        self.metadata[tag_name] = transformation_func(value)
                    else:
                        self.metadata[tag_name] = value_list
            else:
                self.metadata[tag_name] = None

        # Set other metadata fields
        self.manufacturer = self.metadata["Manufacturer"]

        model_name = self.metadata["Manufacturer's Model Name"]
        self.metadata["Manufacturer's Model Name"] = (
            ZeissExdcmMisc.MODEL_NAME_MAPPING.get(model_name, model_name)
        )

        # Set metadata shape and number of frames
        metadata_shape = (
            self.metadata.get("Number of Frames"),
            self.metadata.get("Rows"),
            self.metadata.get("Columns"),
        )

        if metadata_shape == (None, None, None):
            raise ValueError("EXDCM has insufficient row/column metadata.")

        if self.metadata.get("Number of Frames") is None:
            self.metadata["Number of Frames"] = 1

        metadata_shape = typing.cast(tuple[int, int, int], metadata_shape)

        series_description = self.metadata.get("Series Description")
        if series_description:
            image_name = ZeissExdcmMisc.SHAPE_TO_MODALITY[series_description].get(
                metadata_shape
            )
        else:
            image_name = None
            # Can't find a SeriesDescription, so try Macular Cube and Optic Disc
            for _, shape_to_mod in ZeissExdcmMisc.SHAPE_TO_MODALITY.items():
                image_name = shape_to_mod.get(metadata_shape)
                if image_name is not None:
                    break
        if image_name is None:
            raise ValueError(
                "EXDCM has no SeriesDescription - can't find the corresponding "
                f"image type. Shape = {metadata_shape}."
            )

        if isinstance(image_name, str):
            self.image_types.add(image_name)

        self.metadata["Modality"] = self.desired_image_type

    def _strip_null_chars(self, input_string: str) -> str:
        """Removes null byte data suffix."""
        byte_idx = input_string.find("\x00")
        if byte_idx != -1:
            return input_string[:byte_idx]
        else:
            return input_string

    def _retrieve_nested_dicom_values(
        self, ds: Dataset, tag_to_search: TagType
    ) -> List[str]:
        """Recursively search EXDCM for nested Tag.

        Necessary for finding SeriesDescription value(s).
        """
        values = []
        if tag_to_search in ds:
            values.append(ds[tag_to_search].value)
        for data_element in ds:
            if hasattr(data_element, "value") and isinstance(
                data_element.value, Sequence
            ):
                for item in data_element.value:
                    values.extend(
                        self._retrieve_nested_dicom_values(item, tag_to_search)
                    )

        return values

    def _process_series_description(self, series_desc: list) -> str:
        """Get designated series_description from list of values in the dicom."""
        valid_series_desc = [
            i for i in series_desc if i in ZeissDcmMisc.RETINAL_SERIES_DESCRIPTIONS
        ]
        if len(valid_series_desc) == 1 and isinstance(valid_series_desc[0], str):
            return valid_series_desc[0]
        else:
            return ""

    @staticmethod
    def get_scan_laterality(ds: pydicom.FileDataset) -> Optional[str]:
        """Get Scan Laterality from .EX.DCM file FileDataset.

        This method is specifically for use in DicomOpthSource's
        _get_file_properties, where the file is accessed quickly to retrieve
        specific values to be cached.
        """
        if ds.get(ZeissExdcmTags.LATERALITY):
            raw_value = ds.get(ZeissExdcmTags.LATERALITY).value

        if isinstance(raw_value, str) and raw_value in ("L", "R"):
            return raw_value
        elif isinstance(raw_value, str):
            return _LATERALITY_CODE_MAP.get(
                raw_value.split(_ZEISS_STRING_INVALID_DELIM)[0]
            )

        return None
