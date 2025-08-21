import logging
from typing import List, Optional, cast

import attr
import numpy as np

from ...consts import Fixation
from ...data import ImageOutputParams, ImageTransform, Size2D, TopconImageTransforms
from ...exceptions import ExceptionSwallowedByNativeLibraryError, ImageParseException
from ..consts import ScanMode
from .base import FdaSection

EXPECTED_DEPTH = 8
TOPCON_IMAGE_TRANSFORM = TopconImageTransforms(lower=54, higher=191)

logger = logging.getLogger(__name__)


class BScanImageSection(FdaSection):
    EXCLUDED_FIELDS = ["images"]

    def load(self) -> None:
        self.scan_mode = _parse_scan_mode(self.fs.read_byte())
        self.brightness_min = self.fs.read_int()
        self.brightness_max = self.fs.read_int()
        self.size = Size2D(self.fs.read_int(), self.fs.read_int())
        self.slice_count = self.fs.read_int()
        self.image_type = self.fs.read_byte()
        self.image_level = self.fs.read_short()
        self.reversibility = self.fs.read_byte()
        self.images: List[Optional[bytes]] = []
        self.pixel_mode: str = "L"

        self.image_output_params = [
            ImageOutputParams(
                image_processing_options=image_processing_option,
                image_mode="L",
                image_transform_functions=[] if image_processing_option.topcon_no_clip_bscan else [_get_clip_bscan()],
            )
            for image_processing_option in self.options.image_processing_options
        ]

        if self.scan_mode != ScanMode.NONE:
            for _ in range(self.slice_count):
                image = self.fs.read_data_or_skip(self.fs.read_int())
                self.images.append(image)


class BScanParamSection(FdaSection):
    @attr.s(auto_attribs=True, frozen=True)
    class SizingInfo:
        width_dimension_mm: float
        depth_dimension_mm: float
        height_resolution_um: float

    def load(self) -> None:
        self.magic = self.fs.read_byte()

        if self.magic != 0x03:
            raise ImageParseException("Unexpected magic value in BScanParamSection")

        self.mystery1 = self.fs.read_byte()
        self.mystery2 = self.fs.read_byte()

        self.visual_fixation = _parse_fixation(self.fs.read_byte())

        self.ref_mirror_position = self.fs.read_int()
        self.polarizing = self.fs.read_int()
        self.sizing_info = BScanParamSection.SizingInfo(
            # This is the order in which the dimensions are stored in the image.
            # The height is the resolution (i.e. the distance between scans, not the dimension).
            # Marc Wilson from Google has checked these interpretations too.
            width_dimension_mm=self.fs.read_double(),
            depth_dimension_mm=self.fs.read_double(),
            height_resolution_um=self.fs.read_double(),
        )
        self.display_comp_secondary = self.fs.read_double()
        self.display_comp_cubic = self.fs.read_double()
        self.ref_mirror_basis = self.fs.read_byte()
        self.calib_data = self.fs.read_byte()

        # TODO RIPF-195 The rest of these do not appear for all types of images, so ignore them until we need them

        # self.averaging_modes = self.fs.read_byte()
        # self.image_quality_mode = self.fs.read_byte()
        # self.scan_rotate_direction = self.fs.read_byte()
        # self.tracking = self.fs.read_byte()
        # self.area_enhance_mode = self.fs.read_byte()

        # self.scan_protocol = self.fs.read_short()
        # self.z_lock_pos = self.fs.read_short()
        # self.image_count = self.fs.read_int()
        # self.averaging_try = self.fs.read_short()
        # self.supplement = self.fs.read_short_signed()  # TODO RIPF-195 Is this a boolean?
        # self.supplement_result = self.fs.read_short()


def _parse_fixation(encoded_fixation: int) -> Optional[Fixation]:
    # There should be a cornea setting as well, according to mehimagenet6, but we have no sample images.
    try:
        return {
            0x00: Fixation.CENTER,
            0x01: Fixation.DISK,
            0x02: Fixation.MACULAR,
            0x03: Fixation.WIDE,
            0x0F: Fixation.EXTERNAL,
        }[encoded_fixation]
    except KeyError:
        return None


def _parse_scan_mode(encoded_scan_mode: int) -> Optional[ScanMode]:
    """
    Initially borrowed from https://bitbucket.org/uocte/uocte/wiki/Topcon%20File%20Format

    0x00 a line scan
    0x01 a circular scan (called Circle in mehimagenet6)
    0x02 a rectangular volume scan (called 3D scan in mehimagenet6)
    0x03 a cylindrical volume scan
    0x06 - called 3d scan vertical in mehimagenet6
    0x07 a 7 line scan (horitontal or vertical)
    0x0b two 5 line scans put into one 10 slice volume (called 5LineCross in mehimagenet6)
    """
    try:
        return {
            0x00: ScanMode.LINE,
            0x01: ScanMode.CIRCLE,
            0x02: ScanMode.RECTANGULAR_VOLUME,
            0x03: ScanMode.CYLINDRICAL_VOLUME,
            0x06: ScanMode.VERTICAL,
            0x07: ScanMode.SEVEN_LINE,
            0x0B: ScanMode.DOUBLE_FIVE_LINE,
        }[encoded_scan_mode]
    except KeyError:
        logger.warning("Unknown topcon scan mode %s", hex(encoded_scan_mode))
        return None


def _get_clip_bscan() -> ImageTransform:
    def _clip_bscan(image_array: np.ndarray) -> np.ndarray:
        """
        This clipping is based off an equivalent clipping which is performed by Topcon's fds2dcm.exe when exporting to
        DICOM.  It is not an exact match of the Topcon behaviour, though it is close.
        """

        # noinspection PyTypeChecker
        _detect_swallowed_exception(image_array)
        normalised_pixels = ((image_array.astype(np.int32) - TOPCON_IMAGE_TRANSFORM.lower) * 255) / (
            TOPCON_IMAGE_TRANSFORM.higher - TOPCON_IMAGE_TRANSFORM.lower
        )
        clipped_pixels = np.minimum(255, np.maximum(0, normalised_pixels)).astype(np.uint8)

        return cast(np.ndarray, clipped_pixels)

    return _clip_bscan


def _detect_swallowed_exception(pixels: np.ndarray) -> None:
    # We've seen quite a few exceptions in the wild which look like:
    # TypeError: int() argument must be a string, a bytes-like object or a number, not 'Jpeg2KImageFile'
    # which are thrown as soon as the pixels array is used.  On closer inspection, the pixels array has the wrong type (
    # object, not uint8).  This can be triggered manually by pressing Ctrl-C halfway through a parse.
    #
    # I’m pretty sure that what is going on is that an exception is being asynchronously raised inside the parsing
    # thread - a KeyboardInterrupt when we press Ctrl-C, likely a SoftTimeLimitExceeded in the librarian - but it isn’t
    # being raised properly because the thread is in a native library (numpy)
    if pixels.dtype == object:
        raise ExceptionSwallowedByNativeLibraryError()
