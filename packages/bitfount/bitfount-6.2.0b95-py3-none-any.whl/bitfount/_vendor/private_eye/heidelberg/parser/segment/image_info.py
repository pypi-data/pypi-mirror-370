import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import attr
from .....private_eye import ImageParseException
from .....private_eye.data import Laterality, ParserOptions, PointF, Size2D
from .....private_eye.exceptions import StreamLengthError
from .....private_eye.heidelberg.heidelberg_consts import BScanType
from .....private_eye.heidelberg.hr import get_series_type
from .....private_eye.heidelberg.parser.file_parser import Segment, SegmentBody
from .....private_eye.heidelberg.parser.segment.segment_utils import parse_laterality
from .....private_eye.heidelberg.parser.segment_parser import segment_body_parser
from .....private_eye.heidelberg.parser.stream_wrapper import HeidelbergStreamWrapper
from .....private_eye.utils.attrs import hex_repr
from .....private_eye.utils.maths import distance

logger = logging.getLogger(__name__)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class CustomOctSettingsSegment(SegmentBody):
    """
    This is not always present for OCT scans, so assume it stores settings overrides
    """

    oct_contrast: int  # This is the value of 'OCT Contrast' in brightness/contrast settings
    mystery_1: int
    mystery_2: int
    mystery_3: int
    mystery_4: int


@segment_body_parser(types=[0x2717], targets=[CustomOctSettingsSegment])
def parse_oct_settings(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> CustomOctSettingsSegment:
    mystery_1 = stream.read_int()  # Maybe the colour table type?
    oct_contrast = stream.read_int()
    mystery_2 = stream.read_int()
    mystery_3 = stream.read_short()
    mystery_4 = stream.read_short()

    return CustomOctSettingsSegment(
        oct_contrast=oct_contrast, mystery_1=mystery_1, mystery_2=mystery_2, mystery_3=mystery_3, mystery_4=mystery_4
    )


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ImageInfo03Segment(SegmentBody):
    series_type: Optional[str]
    laterality: Laterality
    name: str


@segment_body_parser(types=[0x3], targets=[ImageInfo03Segment])
def parse03(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> ImageInfo03Segment:
    series_type = get_series_type(stream.read_int())
    laterality = parse_laterality(stream.read_utf16_le(2))
    stream.skip(2)
    name = stream.read_var_utf16_le()

    # TODO RIPF-222 Investigate
    # 1 ?  - Could be HRExamStructs 1 - Retina???
    # 30deg (UTF16) - ??  Scan Angle??
    # 20 00 - ????
    # ART - ??
    # 1
    # 107
    # 17
    # 0 0
    # 250 - Distance between b scans over 2??
    #
    return ImageInfo03Segment(series_type, laterality, name)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ImageInfo05Segment(SegmentBody):
    capture_datetime: datetime
    ir_image_size_x: int
    ir_image_size_y: int
    scan_angle: int
    laterality: Laterality
    mystery_1: int = attr.ib(default=None, eq=False)
    mystery_2: int = attr.ib(default=None, eq=False)
    mystery_3: int = attr.ib(default=None, eq=False)
    mystery_4: bytes = attr.ib(default=None, eq=False)


@segment_body_parser(types=[0x5], targets=[ImageInfo05Segment])
def parse05(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> ImageInfo05Segment:
    """
    You can see the capture datetime field in the Heidelberg Explorer, when looking at the detailed information of a
    single image.
    """
    mystery_1 = stream.read_short()
    laterality = parse_laterality(stream.read_utf16_le(2))
    capture_datetime = stream.read_msft_filetime()
    ir_image_size_x = stream.read_short()  # These shorts could be reversed - only seen square images
    ir_image_size_y = stream.read_short()
    stream.expect_int(0)
    stream.expect_int(0)
    scan_angle = stream.read_short()
    mystery_2 = stream.read_int()
    mystery_3 = stream.read_byte()

    # This is null in all of our test images, but small amounts of data is present in the wild.
    mystery_4 = stream.read_bytes(0x1C)

    return ImageInfo05Segment(
        capture_datetime,
        ir_image_size_x,
        ir_image_size_y,
        scan_angle,
        laterality,
        mystery_1,
        mystery_2,
        mystery_3,
        mystery_4,
    )


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class FundusImageInfoSegment(SegmentBody):
    fixation_target: int
    mysteries: List[int]

    timestamp: int
    grey_value_offset: float
    grey_value_offset_std_dev: Optional[float]
    grey_value_offset_2: float
    adc_gain_factor_1: float
    adc_gain_factor_2: float
    target_size: Size2D
    sensitivity: int
    total_sensitivity: int

    analog_gain: float
    analog_offset: float

    camera_model_code: str
    camera_serial_no: int
    power_supply_serial_no: int
    touch_panel_serial_no: int
    hra_camera_fw_version: List[int]
    power_supply_fw_version: List[int]
    touch_panel_fw_version: List[int]
    acquisition_software_version: List[int]

    timezone_1: str
    timezone_1_offset: int
    timezone_2: str
    timezone_2_offset: int

    scanner_shift: int
    scanner_shift_range: int

    z_module_position: int
    z_module_controller_busy: int
    z_module_refractive_power: float
    z_module_series_state: int
    z_module_switches: int

    last_measured_horizontal_scan_angle: float
    last_measured_horizontal_scan_offset: float
    last_measured_horizontal_scan_age: int
    horizontal_scan_angle_regulator_value: Optional[float]
    last_measured_vertical_scan_angle: float
    last_measured_vertical_scan_offset: float
    last_measured_vertical_scan_age: float

    mystery_1: float


@segment_body_parser(types=[0x27], targets=[FundusImageInfoSegment])
def parser27(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> FundusImageInfoSegment:
    mysteries = []
    stream.read_short()  # 12, 16
    fixation_target = stream.read_short_signed()

    target_size = Size2D(
        stream.read_short(),
        stream.read_short(),
    )
    sensitivity = stream.read_short()

    mysteries.append(stream.read_short())  # 7, 8
    stream.expect_int(0)

    mysteries.append(stream.read_short())  # 3, 7
    mysteries.append(stream.read_short())  # 9 or 16
    mysteries.append(stream.read_short())  # 10, 30 or 50
    mysteries.append(stream.read_int())  # 1
    mysteries.append(stream.read_int())  # 1
    mysteries.append(stream.read_short())  # 1

    # Offset 0x20

    stream.expect_short(0)
    mysteries.append(stream.read_short())  # 0, 8000, 9333
    stream.expect_short(0)
    mysteries.append(stream.read_short())  # 10000
    stream.expect_short(0)
    mysteries.append(stream.read_short())  # 100
    stream.expect_short(0)

    stream.read_short()  # -1
    stream.read_short()  # -1
    stream.read_short()  # -1
    stream.read_short()  # -1

    mysteries.append(stream.read_short())  # 3, 13
    stream.expect_short(0)
    stream.expect_short(1)
    stream.expect_null_bytes(4)

    # Offset 0x40

    stream.expect_null_bytes(6)

    mystery_1 = stream.read_float()  # Usually 1
    grey_value_offset = stream.read_float()

    stream.expect_null_bytes(8)

    stream.read_short()  # 0 or 1
    stream.read_short()  # 0 or 1
    stream.read_short()  # 0
    stream.read_short()  # 1
    stream.read_short()  # 0

    # Offset 0x60
    # This doesn't seem to be a Unix timestamp and is shown as a hex value in Heyex
    timestamp = stream.read_int()
    stream.read_int()  # 0, 1 or 10

    camera_serial_no = stream.read_int()
    power_supply_serial_no = stream.read_int()
    touch_panel_serial_no = stream.read_int()

    total_sensitivity = stream.read_int()
    analog_gain = stream.read_float()  # dB
    analog_offset = stream.read_float()  # V

    # Offset 0x80
    hra_camera_fw_version = stream.read_byte_list(4)
    power_supply_fw_version = stream.read_byte_list(4)
    touch_panel_fw_version = stream.read_byte_list(4)
    acquisition_software_version = stream.read_byte_list(4)

    stream.read_int()  # 3
    stream.read_int()  # 1, 2

    stream.read_byte_list(2)  # Have seen 1,2 and 1, 3
    stream.read_int()  # 0 or 8

    stream.read_byte()  # 0
    scanner_shift = stream.read_byte()

    # Offset 0xA0
    scanner_shift_range = stream.read_byte()
    stream.read_byte()  # 2

    stream.read_int()  # 0
    # The Z-module values are guesses based on position in the data, as their values are mostly 0
    z_module_position = stream.read_int()
    z_module_controller_busy = stream.read_int()
    z_module_refractive_power = stream.read_float()
    z_module_series_state = stream.read_int()
    z_module_switches = stream.read_short()

    timezone_1 = stream.read_utf16_le(64)  # Usually 'GMT Standard Time'
    stream.skip(16)  # I suspect this is to do with the start/end dates, but not sure
    timezone_1_offset = stream.read_int_signed()  # 0 for GMT

    timezone_2 = stream.read_utf16_le(64)  # Usually 'GMT Daylight Time'
    stream.skip(16)  # See above
    timezone_2_offset = stream.read_int_signed()  # -60 for BST

    # Offset 0x160

    last_measured_horizontal_scan_angle = stream.read_float()
    last_measured_horizontal_scan_offset = stream.read_float()
    last_measured_horizontal_scan_age = stream.read_int()  # ms
    last_measured_vertical_scan_angle = stream.read_float()
    last_measured_vertical_scan_offset = stream.read_float()
    last_measured_vertical_scan_age = stream.read_int()  # ms

    mysteries.append(stream.read_int())  # 1, 9, 50, 59
    stream.expect_null_bytes(4)

    # Offset 0x180
    stream.expect_null_bytes(16)
    stream.expect_bytes([255] * 16)

    # Offset 0x1A0
    camera_model_code = stream.read_ascii(20)
    grey_value_offset_2 = stream.read_float()

    # These are guessed from position in the list of data
    adc_gain_factor_1 = stream.read_float()
    adc_gain_factor_2 = stream.read_float()

    # Offset 0x1C0
    stream.read_byte()  # 0 or 1

    # At this point some segments end

    try:
        stream.read_int()  # 0
        grey_value_offset_std_dev: Optional[float] = stream.read_float()
        stream.read_double()  # 7.7
        horizontal_scan_angle_regulator_value: Optional[float] = stream.read_float()
        stream.read_float()  # 1.0
    except StreamLengthError:
        grey_value_offset_std_dev = None
        horizontal_scan_angle_regulator_value = None

    return FundusImageInfoSegment(
        timestamp=timestamp,
        grey_value_offset=grey_value_offset,
        grey_value_offset_std_dev=grey_value_offset_std_dev,
        grey_value_offset_2=grey_value_offset_2,
        adc_gain_factor_1=adc_gain_factor_1,
        adc_gain_factor_2=adc_gain_factor_2,
        fixation_target=fixation_target,
        target_size=target_size,
        sensitivity=sensitivity,
        total_sensitivity=total_sensitivity,
        mysteries=mysteries,
        analog_gain=analog_gain,
        analog_offset=analog_offset,
        camera_model_code=camera_model_code,
        camera_serial_no=camera_serial_no,
        power_supply_serial_no=power_supply_serial_no,
        touch_panel_serial_no=touch_panel_serial_no,
        hra_camera_fw_version=hra_camera_fw_version,
        power_supply_fw_version=power_supply_fw_version,
        touch_panel_fw_version=touch_panel_fw_version,
        acquisition_software_version=acquisition_software_version,
        timezone_1=timezone_1,
        timezone_1_offset=timezone_1_offset,
        timezone_2=timezone_2,
        timezone_2_offset=timezone_2_offset,
        scanner_shift=scanner_shift,
        scanner_shift_range=scanner_shift_range,
        z_module_position=z_module_position,
        z_module_controller_busy=z_module_controller_busy,
        z_module_refractive_power=z_module_refractive_power,
        z_module_series_state=z_module_series_state,
        z_module_switches=z_module_switches,
        last_measured_horizontal_scan_angle=last_measured_horizontal_scan_angle,
        last_measured_horizontal_scan_offset=last_measured_horizontal_scan_offset,
        last_measured_horizontal_scan_age=last_measured_horizontal_scan_age,
        horizontal_scan_angle_regulator_value=horizontal_scan_angle_regulator_value,
        last_measured_vertical_scan_angle=last_measured_vertical_scan_angle,
        last_measured_vertical_scan_offset=last_measured_vertical_scan_offset,
        last_measured_vertical_scan_age=last_measured_vertical_scan_age,
        mystery_1=mystery_1,
    )


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ImageInfo28Segment(SegmentBody):
    pass


@segment_body_parser(types=[0x28], targets=[ImageInfo28Segment])
def parser28(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> ImageInfo28Segment:
    # TODO RIPF-222 Investigate
    return ImageInfo28Segment()


@hex_repr
@attr.s(auto_attribs=True)
class BScanImageInfoSegment(SegmentBody):
    mystery_1: int
    mystery_2: int
    mystery_3: float
    mystery_4: float
    size: Size2D
    # Note: for cylindrical scans the line_start == line_end.
    # These are relative to the fundus image
    line_start: PointF
    line_end: PointF
    centre_pos: PointF
    scan_angle: float
    intensity_scaling: float

    scaling_z: float

    scan_type: BScanType
    scan_datetime: datetime
    art_average: int

    oct_controller_fw_version: List[int]
    oct_camera_fw_version: List[int]
    oct_camera_fpga_version: List[int]

    quality: float

    data_exponent: float
    noise_background: int
    noise_background_std_dev: float
    frame_rate_hz: float
    first_valid_a_scan: int
    valid_a_scans: int
    scan_pattern_size: int
    scan_pattern_index: int

    spectrometer_lower_wavelength_limit_um: float
    spectrometer_upper_wavelength_limit_um: float

    fft_window_type: int
    fft_window_asymmetry: float
    fft_window_width: float

    camera_eye_distance_um: float

    board_serial_number: int
    eeprom_version: int
    board_revision: str
    twa_carrier_eeprom_version: int
    twa_carrier_board_revision: List[int]
    twa_carrier_board_serial_number: int
    twa_sensor_eeprom_version: int
    # A 4-part version number, each part being 1 byte
    twa_sensor_board_revision: List[int]
    twa_sensor_board_serial_number: int

    hra_to_oct_transform: List[float]
    circle_scan_nasal_start: int
    circle_scan_transform: List[float]
    scan_position_within_tolerance: int
    frame_error_state: int

    zero_reference_mean_value: float
    reference_spectrum: List[float]
    reference_spectrum_max_value: float
    background_noise_power: List[float]

    scan_guid: Optional[UUID]


@segment_body_parser(types=[0x2714], targets=[BScanImageInfoSegment])
def parser_bscan_image_info(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> BScanImageInfoSegment:
    mystery_1 = stream.read_int()
    height = stream.read_int()
    width = stream.read_int()
    # Note: for cylindrical scans the line_start == line_end.
    # These are measured in degrees, oddly enough. It does make calculating the scan angle fairly simple though...
    line_start = stream.read_point_f()
    line_end = stream.read_point_f()

    stream.expect_int(0)

    # Offset: 0x20
    intensity_scaling = stream.read_float()

    scaling_z = stream.read_float()  # In mm/pixel. This constant per machine
    data_exponent = stream.read_float()
    noise_background = stream.read_int()
    noise_background_std_dev = stream.read_float()
    frame_rate_hz = stream.read_float()
    first_valid_a_scan = stream.read_int()
    valid_a_scans = stream.read_int()

    # Offset: 0x40

    scan_pattern_size = stream.read_int()  # Note: this is sometime 0
    scan_pattern_index = stream.read_int()
    scan_type_raw = stream.read_int()  # Not sure if this is right

    centre_pos = stream.read_point_f()
    mystery_2 = stream.read_int()
    scan_datetime = stream.read_msft_filetime()

    # Offset 0x60

    stream.warn_if_unexpected(b"\0" * 4, header)
    spectrometer_lower_wavelength_limit_um = stream.read_float()
    spectrometer_upper_wavelength_limit_um = stream.read_float()

    # The first FFT params are guesses based on order of extended OCT info
    fft_window_type = stream.read_int()
    fft_window_asymmetry = stream.read_float()
    fft_window_width = stream.read_float()

    art_average = stream.read_int()

    oct_controller_fw_version = stream.read_byte_list(4)

    # Offset: 0x80

    oct_camera_fw_version = stream.read_byte_list(4)
    oct_camera_fpga_version = stream.read_byte_list(4)

    camera_eye_distance_um = stream.read_double()  # This can be negative
    # Have seen 0, 1210, 1200 and 2500.0 in the wild.
    # When it was 1210, 'Eye Length' was marked as 'Unknown (1210)'. However, I have no idea how these numbers
    # affect anything else yet.
    mystery_3 = stream.read_double()
    mystery_4 = stream.read_float()  # Doesn't appear in normal or extended properties
    quality = stream.read_float()

    # Offset: 0xA0

    board_serial_number = stream.read_int()
    eeprom_version = stream.read_int()
    board_revision = stream.read_ascii(10)
    twa_carrier_eeprom_version = stream.read_int()
    twa_carrier_board_revision = stream.read_byte_list(4)
    twa_carrier_board_serial_number = stream.read_int()
    stream.skip(1)

    # Offset: 0xBF
    twa_sensor_eeprom_version = stream.read_int()
    twa_sensor_board_revision = stream.read_byte_list(4)
    twa_sensor_board_serial_number = stream.read_int()
    stream.skip(1)

    hra_to_oct_transform = stream.read_float_list(6)

    # Offset: 0xE4
    circle_scan_nasal_start = stream.read_int()
    circle_scan_transform = stream.read_float_list(6)

    # Offset: 0x100
    scan_position_within_tolerance = stream.read_int()
    frame_error_state = stream.read_int()

    zero_reference_mean_value = stream.read_float()
    reference_spectrum = stream.read_float_list(8)

    # Offset 0x12C
    reference_spectrum_max_value = stream.read_float()
    background_noise_power = stream.read_float_list(8)

    # Offset 0x150
    stream.warn_if_unexpected(b"\0" * 4, header)
    stream.skip(4)
    try:
        scan_guid: Optional[UUID] = stream.read_uuid()
    except ValueError:
        # Not all files have this at the end
        scan_guid = None

    # Calculated values

    # As distances are measured in degrees, the angle can be found with a bit of pythagoras
    if scan_type_raw == 1:  # Line
        scan_angle = distance(line_start, line_end)
        scan_type = BScanType.LINE
    elif scan_type_raw == 2:  # Circle
        scan_angle = distance(line_start, centre_pos) * 2
        scan_type = BScanType.CIRCLE
    else:
        # Use 'Line' as the default type, so we can still parse the file
        scan_angle = distance(line_start, line_end)
        scan_type = BScanType.LINE
        logger.warning("Unknown bscan type: %d", scan_type_raw)

    return BScanImageInfoSegment(
        mystery_1=mystery_1,
        mystery_2=mystery_2,
        mystery_3=mystery_3,
        mystery_4=mystery_4,
        size=Size2D(width, height),
        line_start=line_start,
        line_end=line_end,
        scan_angle=scan_angle,
        intensity_scaling=intensity_scaling,
        scaling_z=scaling_z,
        scan_datetime=scan_datetime,
        data_exponent=data_exponent,
        noise_background=noise_background,
        noise_background_std_dev=noise_background_std_dev,
        frame_rate_hz=frame_rate_hz,
        first_valid_a_scan=first_valid_a_scan,
        valid_a_scans=valid_a_scans,
        scan_pattern_size=scan_pattern_size,
        scan_pattern_index=scan_pattern_index,
        scan_type=scan_type,
        centre_pos=centre_pos,
        spectrometer_lower_wavelength_limit_um=spectrometer_lower_wavelength_limit_um,
        spectrometer_upper_wavelength_limit_um=spectrometer_upper_wavelength_limit_um,
        fft_window_type=fft_window_type,
        fft_window_asymmetry=fft_window_asymmetry,
        fft_window_width=fft_window_width,
        art_average=art_average,
        oct_controller_fw_version=oct_controller_fw_version,
        oct_camera_fw_version=oct_camera_fw_version,
        oct_camera_fpga_version=oct_camera_fpga_version,
        camera_eye_distance_um=camera_eye_distance_um,
        quality=quality,
        board_serial_number=board_serial_number,
        eeprom_version=eeprom_version,
        board_revision=board_revision,
        twa_carrier_eeprom_version=twa_carrier_eeprom_version,
        twa_carrier_board_revision=twa_carrier_board_revision,
        twa_carrier_board_serial_number=twa_carrier_board_serial_number,
        twa_sensor_eeprom_version=twa_sensor_eeprom_version,
        twa_sensor_board_revision=twa_sensor_board_revision,
        twa_sensor_board_serial_number=twa_sensor_board_serial_number,
        hra_to_oct_transform=hra_to_oct_transform,
        circle_scan_nasal_start=circle_scan_nasal_start,
        circle_scan_transform=circle_scan_transform,
        scan_position_within_tolerance=scan_position_within_tolerance,
        frame_error_state=frame_error_state,
        zero_reference_mean_value=zero_reference_mean_value,
        reference_spectrum=reference_spectrum,
        reference_spectrum_max_value=reference_spectrum_max_value,
        background_noise_power=background_noise_power,
        scan_guid=scan_guid,
    )


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class ImageInfo2718Segment(SegmentBody):
    pass


@segment_body_parser(types=[0x2718], targets=[ImageInfo2718Segment])
def parser2718(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> ImageInfo2718Segment:
    # TODO RIPF-222 Investigate
    return ImageInfo2718Segment()


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class BScanImageInfo271ASegment(SegmentBody):
    mystery_1: int
    mystery_2: float
    count: int
    mystery_list: List[float]


@segment_body_parser(types=[0x271A], targets=[BScanImageInfo271ASegment])
def parser_271a(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> BScanImageInfo271ASegment:
    mystery_1 = stream.read_int()
    stream.expect_null_bytes(4)
    mystery_2 = stream.read_float()  # This seems to be 1 most of the time
    count = stream.read_int()
    mystery_list = [stream.read_float() for _ in range(count)]

    # There is a fat load of zeroes from here till the end of the segment
    pos = stream.tell() - header.position
    stream.expect_null_bytes(header.size - pos)

    return BScanImageInfo271ASegment(mystery_1, mystery_2, count, mystery_list)


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class BScanRegistrationSegment(SegmentBody):
    mystery_1: int
    scale_x: float
    dx: float
    dy: float
    shear_y_angle: float
    values_1: List[float]
    values_2: List[float]


@segment_body_parser(types=[0x271C], targets=[BScanRegistrationSegment])
def parser271c(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> BScanRegistrationSegment:
    """
    Most of the float parameters are constant 1 or 0, with the exception of those at indices 0, 2, 6, 8, 12, 14, 18, 20
    The following relationships can also exist:
    parameters[2] + parameters[14] = 0
    parameters[6] + parameters[18] = 0
    parameters[8] + parameters[20] ~ 0  - within an error margin of 0.15
    In some cases the values of the second half are all 1 and 0, regardless of what is in the first half

    An initial investigation reveals that we can create an affine transformation that matches
    the boundaries of the registered images in Heyex:
     1. The registered image sheared in the y-direction by an angle of parameters[6]. The transformation origin
        is located at the x-centre of the image for this transform, so the true transform is:
           * Translate the image by (-width/2, Y)
           * Scale
           * Shear
           * Translate back by (width/2, Y)
        As we only shear in the y-direction, the Y-translation is irrelevant, so we leave it as 0
     2. the registered image is translated by (parameters[2], parameters[8])
    """
    mystery_1 = stream.read_int()  # Scan pattern index?

    # First 12 values
    values_1: List[float] = [stream.read_float() for _ in range(12)]
    # Name the values we care about. We keep the full list of values as it's simpler to see the values
    # and compare to values_2 when they are the same size
    scale_x = values_1[0]
    dx = values_1[2]
    shear_y_angle = values_1[6]
    dy = values_1[8]

    # If this breaks, it means we need to update the registration logic with new parameters. The file which breaks
    # this should be added to the integration tests.
    # None represents values which can be variable - we show this explicitly in the 'expected' array
    expected = [None, 0.0, None, 0.0, 0.0, 0.0, None, 1.0, None, 0.0, 0.0, 0.0]
    for index, vals in enumerate(zip(expected, values_1)):
        expected_val, actual_val = vals
        if expected_val is not None and expected_val != actual_val:
            raise ImageParseException(
                f"Unexpected BScanRegistrationSegment value at index {index}: "
                f"expected {expected_val}; got {actual_val}"
            )

    # The next 12 might represent the inverse transform, given the relationships defined above.
    # However, the values are not always set.
    values_2: List[float] = [stream.read_float() for _ in range(12)]

    return BScanRegistrationSegment(
        mystery_1=mystery_1,
        scale_x=scale_x,
        dx=dx,
        dy=dy,
        shear_y_angle=shear_y_angle,
        values_1=values_1,
        values_2=values_2,
    )


@hex_repr
@attr.s(auto_attribs=True, frozen=True)
class BScanImagePositionsSegment(SegmentBody):
    scan_angle: int
    series_type: Optional[str]
    count: int
    positions: List["BScanPosition"]

    @hex_repr
    @attr.s(auto_attribs=True, frozen=True)
    class BScanPosition:
        """
        This corresponds to where a bscan is relative to the fundus image.
        If the type is cylindrical, the circle coords will be set.
        If the type is a line, the line coords will be set.

        All distances are measures in FOV degrees relative to fundus centre.
        X increases from left to right
        Y increases from top to bottom
        """

        type: int
        circle_centre_pos: PointF
        circle_centre_radius: float
        line_start: PointF
        line_end: PointF
        mystery_2: float
        mystery_3: float
        mystery_4: int


@segment_body_parser(types=[0x271D], targets=[BScanImagePositionsSegment])
def parser_bscan_positions(
    stream: HeidelbergStreamWrapper, header: Segment.Header, parser_options: ParserOptions
) -> BScanImagePositionsSegment:
    stream.expect_int(2)
    scan_angle = stream.read_int()  # Note: This can be zero for  cylindrical scans
    series_type = get_series_type(stream.read_int())

    count = stream.read_int()
    positions: List[BScanImagePositionsSegment.BScanPosition] = []
    for _ in range(count):
        subsection_type = stream.read_int()  # ???

        # Note: These are all in degrees
        circle_centre_pos = stream.read_point_f()
        circle_centre_radius = stream.read_float()

        stream.skip(8)
        mystery_2 = stream.read_float()
        stream.expect_null_bytes(12)
        mystery_3 = stream.read_float()
        stream.expect_null_bytes(4)

        line_start = stream.read_point_f()
        line_end = stream.read_point_f()

        stream.skip(16)
        mystery_4 = stream.read_int()
        positions.append(
            BScanImagePositionsSegment.BScanPosition(
                type=subsection_type,
                circle_centre_pos=circle_centre_pos,
                circle_centre_radius=circle_centre_radius,
                line_start=line_start,
                line_end=line_end,
                mystery_2=mystery_2,
                mystery_3=mystery_3,
                mystery_4=mystery_4,
            )
        )

    stream.expect_null_bytes(84)
    stream.skip(12)

    return BScanImagePositionsSegment(scan_angle, series_type, count, positions)
