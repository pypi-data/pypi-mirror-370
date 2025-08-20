import math
from datetime import datetime, timedelta

# Description from https://docs.microsoft.com/en-us/dotnet/api/system.datetime.tooadate?view=netframework-4.8
# An OLE Automation date is implemented as a floating-point number whose integral component is the number of days
# before or after midnight, 30 December 1899, and whose fractional component represents the time on that day divided
# by 24. For example, midnight, 31 December 1899 is represented by 1.0; 6 A.M., 1 January 1900 is represented by
# 2.25; midnight, 29 December 1899 is represented by -1.0; and 6 A.M., 29 December 1899 is represented by -1.25.

OLE_TIME_ZERO = datetime(1899, 12, 30)
SECONDS_PER_DAY = 86400


def from_oletime(value: float) -> datetime:
    frac_part, int_part = math.modf(value)
    if int_part < 0:
        frac_part = -frac_part
    return OLE_TIME_ZERO + timedelta(days=int_part, seconds=frac_part * SECONDS_PER_DAY)


def to_oletime(value: datetime) -> float:
    delta = value - OLE_TIME_ZERO
    if delta >= timedelta(0, 0):
        return float(delta.days) + (float(delta.seconds) / SECONDS_PER_DAY)
    return float(delta.days) - (float(delta.seconds) / SECONDS_PER_DAY)
