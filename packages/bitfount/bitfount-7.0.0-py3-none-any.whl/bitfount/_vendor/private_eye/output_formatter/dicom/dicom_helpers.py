from datetime import date, datetime
from typing import Any, Callable, List, Optional, TypeVar, Union

from ....private_eye.data import Number, Size3D
from ....private_eye.utils.optional import map_optional
from pydicom import Dataset, Sequence
from pydicom.uid import UID, generate_uid

_T = TypeVar("_T")

DATE_FORMAT = "%Y%m%d"
TIME_FORMAT = "%H%M%S"
DATETIME_FORMAT = f"{DATE_FORMAT}{TIME_FORMAT}"

DEFAULT_DATE = "18000101"
DEFAULT_TIME = "000000"
DEFAULT_DATETIME = f"{DEFAULT_DATE}{DEFAULT_TIME}"

# While all images should have physical resolutions, we don't have this information for some formats (e.g. Heidelberg)
# Until we do, provide a placeholder in order to satisfy the spec
DEFAULT_RESOLUTIONS_MM = Size3D(depth=0.001, height=0.001, width=0.001)

# Similarly to how DCMTK (the library used by the topcon) seems to work, we've invented an OID base for our own use.
_OID_BASE = "1.2.826.1.82422202918."


def format_date(d: Union[datetime, date]) -> str:
    return d.strftime(DATE_FORMAT)


def format_datetime(d: Union[datetime, date]) -> str:
    return d.strftime(DATETIME_FORMAT)


def format_time(d: Union[datetime, date]) -> str:
    return d.strftime(TIME_FORMAT)


def map_optional_to_string(value: Optional[_T], func: Callable[[_T], str] = str) -> str:
    """
    like map_optional, but if not present then returns an empty string.  This is useful because a lot of DICOM fields
    are required to be present, but if the value is unknown should be set to an empty string.
    """
    return map_optional(value, func) or ""


def render_name(first_name: Optional[str], last_name: Optional[str]) -> Optional[str]:
    if first_name is None and last_name is None:
        return None
    return map_optional_to_string(first_name) + "^" + map_optional_to_string(last_name)


def crop_number(number: Number) -> str:
    """
    DICOM digits represented as strings (type DS) cannot be longer than 16 characters
    """
    val = str(number)
    return val[:16]


def as_sequence(ds: Dataset) -> Sequence:
    return Sequence([ds])


def code_dataset(scheme: str, value: str, meaning: str) -> Dataset:
    ds = Dataset()
    ds.CodeValue = value
    ds.CodingSchemeDesignator = scheme
    ds.CodeMeaning = meaning
    return ds


def code_sequence(scheme: str, value: str, meaning: str) -> Sequence:
    return as_sequence(code_dataset(scheme, value, meaning))


def static_uid(suffix: str) -> UID:
    return UID(_OID_BASE + suffix)


def generate_uid_from_source(pepper: Optional[str], source: List[Any]) -> UID:
    return generate_uid(_OID_BASE, _generate_entropy_source(pepper, *source))


def _generate_entropy_source(*args: Any) -> Optional[List[str]]:
    # If the list of args is empty, replace it with None to generate a random UID
    return [str(a) for a in args if a] or None


def generate_bool_coded_string(boolean: bool) -> str:
    return "TRUE" if boolean else "FALSE"
