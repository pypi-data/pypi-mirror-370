import math
import os

HALF_MANTISSA_SIZE = 10
HALF_MANTISSA_BIAS = 63
HALF_MANTISSA_SUBNORMAL_BIAS = HALF_MANTISSA_BIAS - 1
HALF_MANTISSA_SCALE = 1 << HALF_MANTISSA_SIZE


def ushort_to_unsigned_half(input_: int) -> float:
    """
    Convert a two-byte number into Heidelberg's own floating-point.
    It is unsigned with a 6-bit exponent and 10-bit mantissa and a bias of 63 (which forces all values to be <= 1)
    """
    exponent = input_ >> 10  # First 6 bits
    mantissa = input_ & 0x03FF  # Last 10 bits

    if exponent == 0:
        # The subnormal case
        return math.ldexp(float(mantissa) / HALF_MANTISSA_SCALE, -HALF_MANTISSA_SUBNORMAL_BIAS)
    if exponent == 63:
        # This signifies +/-infinity, which we treat as zero
        return 0.0

    normalised_mantissa = 1.0 + float(mantissa) / HALF_MANTISSA_SCALE
    return math.ldexp(normalised_mantissa, exponent - HALF_MANTISSA_BIAS)


def is_heidelberg_dob_fix_enabled() -> bool:
    """Check if the Heidelberg date fix is enabled."""
    # Allows the envvar to be anything along the lines of true, True, TRUE, 1,
    # "1", TrUe, t, T, etc.
    return (
        os.getenv("PRIVATE_EYE_HEIDELBERG_DATE_FIX", "False").lower()
        in ("true", "1", "t", "yes", "y")
    )
