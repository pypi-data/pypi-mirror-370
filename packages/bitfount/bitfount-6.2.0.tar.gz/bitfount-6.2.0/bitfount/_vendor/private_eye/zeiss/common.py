from datetime import date, datetime, time
from typing import Any, Callable, Optional, TypeVar

from pydicom import Dataset

T = TypeVar("T")

DATE_FORMAT = "%Y%m%d"
TIME_FORMATS = ["%H%M%S.%f", "%H%M%S"]
DATETIME_FORMATS = [f"{DATE_FORMAT}{time_format}" for time_format in TIME_FORMATS]


def _parse_encoded_optional(parser: Callable[[str], Optional[T]]) -> Callable[[Optional[str]], Optional[T]]:
    def _parse(encoded: Optional[str]) -> Optional[T]:
        return parser(encoded) if encoded else None

    return _parse


@_parse_encoded_optional
def map_string_to_optional(value: str) -> Optional[str]:
    return value


@_parse_encoded_optional
def parse_optional_datetime(encoded_datetime: str) -> Optional[datetime]:
    for datetime_format in DATETIME_FORMATS:
        try:
            return datetime.strptime(encoded_datetime, datetime_format)
        except ValueError:
            pass
    raise ValueError(f"datetime {encoded_datetime} doesn't match any known datetime format")


@_parse_encoded_optional
def parse_optional_date(encoded_date: str) -> Optional[date]:
    return datetime.strptime(encoded_date, DATE_FORMAT).date()


@_parse_encoded_optional
def parse_optional_time(encoded_time: str) -> Optional[time]:
    for time_format in TIME_FORMATS:
        try:
            return datetime.strptime(encoded_time, time_format).time()
        except ValueError:
            pass
    raise ValueError(f"time {encoded_time} doesn't match any known datetime format")


def parse_separated_optional_datetimes(encoded_date: Optional[str], encoded_time: Optional[str]) -> Optional[datetime]:
    date_option = parse_optional_date(encoded_date)
    time_option = parse_optional_time(encoded_time)
    if date_option:
        return datetime.combine(date_option, time_option or time.min)
    return None


def ds_require(ds: Dataset, attr_name: str, expected: Any) -> None:
    actual = getattr(ds, attr_name)
    if actual != expected:
        raise ValueError(f"Unable to parse Zeiss image, {attr_name}={actual} but expected {expected}")
