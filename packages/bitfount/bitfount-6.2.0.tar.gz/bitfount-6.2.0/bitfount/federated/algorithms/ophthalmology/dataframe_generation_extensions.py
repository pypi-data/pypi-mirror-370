"""Additional functionality for DataFrame processing.

Provides functions that can be used for additional column generation.
"""

from __future__ import annotations

from collections.abc import Callable
from hashlib import md5
import re
from typing import Any, ParamSpec, Protocol, TypeVar, Union

from dateutil.parser import ParserError as DateUtilParserError
import pandas as pd
from pandas.errors import ParserError as PandasParserError
import text_unidecode

from bitfount.exceptions import BitfountError
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    _BITFOUNT_PATIENT_ID_KEY,
    DEFAULT_MAX_SUBFOVEAL_DISTANCE,
    DISTANCE_FROM_FOVEA_CENTRE_COL,
    DOB_COL,
    INTRARETINAL_CYSTOID_FLUID_COL,
    NAME_COL,
    SEROUS_RPE_DETACHMENT_COL,
    SUBFOVEAL_COL,
    SUBRETINAL_FLUID_COL,
)
from bitfount.federated.logging import _get_federated_logger

# Try to import the specific date parsing error from pandas, but if not possible,
# defer to the parent class of that exception
# mypy_reason: distinct paths through import
try:
    from pandas._libs.tslibs.parsing import DateParseError as PandasDateParseError
except ImportError:
    PandasDateParseError = ValueError  # type: ignore[misc,assignment]
    # Reason: see above

_logger = _get_federated_logger(f"bitfount.federated.algorithms.{__name__}")

P = ParamSpec("P")


class DataFrameExtensionFunction(Protocol[P]):
    """Callback protocol for DataFrame extension functions."""

    def __call__(
        self, df: pd.DataFrame, *args: P.args, **kwargs: P.kwargs
    ) -> pd.DataFrame:
        """Callback function structure."""
        ...


extensions: dict[str, DataFrameExtensionFunction] = {}

F = TypeVar("F", bound=DataFrameExtensionFunction)


def _register(
    register_name: str,
) -> Callable[[F], F]:
    """Decorate a function to register it as a DataFrame extension function.

    Args:
        register_name: The name to store the function against in the registry.
    """

    def _decorator(func: F) -> F:
        extensions[register_name] = func
        return func

    return _decorator


def id_safe_string(s: str) -> str:
    """Converts a string to a normalised version safe for use in IDs.

    In particular, converts accented/diacritic characters to their closest
    ASCII representation, ensures lowercase, and replaces any non-word
    characters with underscores.

    This allows us to map potentially different spellings (e.g. Francois
    John-Smith vs François John Smith) to the same string
    (francois_john_smith).
    """
    # First, ensure we are working in lower case.
    s = s.lower()

    # Next split and combine each "segment"
    # Here we split on any non-word characters (i.e. anything expect letters,
    # numbers, or underscore).
    s = "_".join(re.split(r"\W+", s))

    # Convert to a normalised unicode form, removing any combining characters
    # (e.g. accent modifiers, etc.).
    # This has the effect of converting things like 'ø' or 'é' to 'o' and 'e'
    # respectively.
    # `unidecode()` is relatively expensive, so we only do it if needed.
    if not s.isascii():
        s = text_unidecode.unidecode(s)

    return s


def safe_format_date(value: Any) -> Any:
    """Safely format a date string.

    Args:
        value: The input value, which can be a date string, integer, or NaN.

    Returns:
        Formatted date string or the original value as a string if formatting fails.
    """
    if pd.isnull(value):
        return pd.NA  # Handle null values
    try:
        # Attempt to parse and format the date
        formatted_date = pd.to_datetime(value).strftime("%Y-%m-%d")
        # The below is inferred by mypy as "Any",
        # so the whole functions return type is "Any"
        return formatted_date
    except (ValueError, pd.errors.OutOfBoundsDatetime):
        # If parsing fails, return the original value as a string
        return str(value)


@_register(_BITFOUNT_PATIENT_ID_KEY)
def generate_bitfount_patient_id(
    df: pd.DataFrame, name_col: str = NAME_COL, dob_col: str = DOB_COL
) -> pd.DataFrame:
    """Adds a BitfountPatientID column to the provided DataFrame.

    This mutates the input dataframe with the new column.

    The generated IDs are the hash of the concatenated string of a
    Bitfount-specific key, full name, and date of birth.
    """
    try:
        # In order to get a consistent string representation of the dates,
        # still maintaining nulls, we have to do this conversion via
        # `.apply()` as using just `.to_datetime()` and `astype(str)`
        # converts nulls to "NaT" strings.
        # See: https://github.com/pandas-dev/pandas/issues/31708
        dobs: pd.Series[str] = df[dob_col].apply(safe_format_date)

        # As above, need to use `apply()` to ensure that nulls are respected
        name_ids: pd.Series[str] = df[name_col].apply(
            lambda x: id_safe_string(x) if pd.notnull(x) else pd.NA
        )

    except KeyError as ke:
        raise DataFrameExtensionError(
            f"Unable to add BitfountPatientID column, missing base columns: {ke}"
        ) from ke

    except (DateUtilParserError, PandasDateParseError, PandasParserError) as dpe:
        # The error message may contain data information, so we want to
        # ensure this info is only logged locally, not potentially
        # propagated back to the modeller as part of the exception message.
        _logger.error(
            f"Parsing error whilst processing date of birth column, {dob_col}: {dpe}"
        )
        raise DataFrameExtensionError(
            f"Parsing error whilst processing date of birth column, {dob_col}."
            f" See Bitfount logs for details."
        ) from dpe

    # Concatenate the separate elements together, prepended with our key.
    # This concatenation respects null entries.
    patient_ids: pd.Series[str] = _BITFOUNT_PATIENT_ID_KEY + name_ids + dobs

    # Calculate the hash value of the generated key to ensure the IDs are
    # obfuscated.
    # We use md5 here, which is cryptographically broken but fine for our
    # use-case as it is not being used for security.
    # SHA-256 is ~20% slower than md5 which, for the scale of entries we are
    # considering, is a noticeable difference for no additional benefit.
    patient_ids = patient_ids.apply(
        lambda x: (
            md5(x.encode(), usedforsecurity=False).hexdigest()  # nosec[blacklist] md5 is not being used in a security context # noqa: E501
            if pd.notnull(x)
            else pd.NA
        )
    )

    # Add the new Bitfount patient ID column
    # This mutates the input dataframe, so returning it is slightly redundant
    # but we do so to ensure compatibility with other extensions.
    df[_BITFOUNT_PATIENT_ID_KEY] = patient_ids
    return df


class DataFrameExtensionError(BitfountError):
    """Indicates an error whilst trying to apply an extension function."""

    pass


def generate_subfoveal_indicator(
    df: pd.DataFrame,
    distance_from_fovea_col: str = DISTANCE_FROM_FOVEA_CENTRE_COL,
    max_distance: float = DEFAULT_MAX_SUBFOVEAL_DISTANCE,
) -> pd.DataFrame:
    """Adds a 'Subfoveal?' column to the provided DataFrame.

    This mutates the input dataframe with the new column.

    The column will contain 'Y' if the distance from fovea is less than the
    specified maximum distance, 'N' if it's greater, and 'Fovea not detected' if
    the distance value is not available.

    Args:
        df: The DataFrame to add the column to.
        distance_from_fovea_col: The name of the column containing the distance
            from fovea. Defaults to DISTANCE_FROM_FOVEA_CENTRE_COL.
        max_distance: The maximum distance to consider as subfoveal. Defaults
            to 0.0.

    Returns:
        The modified DataFrame with the new column.

    Raises:
        DataFrameExtensionError: If the distance from fovea column is not
            available in the DataFrame.
    """
    # Check if we have the distance from fovea column
    has_fovea_distance = distance_from_fovea_col in df.columns

    if not has_fovea_distance:
        raise DataFrameExtensionError(
            f"Unable to add {SUBFOVEAL_COL} column, missing distance column: "
            f"{distance_from_fovea_col}"
        )

    # Initialize the subfoveal column with 'N'
    df[SUBFOVEAL_COL] = "N"

    # Create mask for valid (non-NA) fovea distance values
    fovea_valid_mask = df[distance_from_fovea_col].notna()

    # Mark as subfoveal if fovea distance is less than or equal to max_distance
    fovea_subfoveal_mask = fovea_valid_mask & (
        df[distance_from_fovea_col] <= max_distance
    )
    df.loc[fovea_subfoveal_mask, SUBFOVEAL_COL] = "Y"

    # Set 'Fovea not detected' for rows where fovea distance is NA
    fovea_na_mask = ~fovea_valid_mask
    df.loc[fovea_na_mask, SUBFOVEAL_COL] = "Fovea not detected"

    return df


@_register(SUBFOVEAL_COL)
def generate_subfoveal_indicator_extension(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for generating the subfoveal indicator column.

    Note that this is a wrapper function since extensions do not support
    parameters yet. Once they do, we can remove this wrapper function.
    """
    return generate_subfoveal_indicator(df)


def extract_json_value(
    df: pd.DataFrame,
    json_column: str,
    key: str,
    new_column_name: str,
) -> pd.DataFrame:
    """Extracts a specific value from a JSON string or dictionary column.

    Args:
        df: The DataFrame to process.
        json_column: The name of the column containing JSON strings or
            dictionaries.
        key: The key to extract from the JSON or dictionary.
        new_column_name: The name for the new column containing the extracted
            values.

    Returns:
        The DataFrame with the new column added.
    """
    # Create a copy of the dataframe to avoid modifying the original
    df = df.copy()

    # Check if the json_column exists in the dataframe
    if json_column not in df.columns:
        _logger.warning(f"Column '{json_column}' not found in dataframe")
        df[new_column_name] = f"'{json_column}' not found"
        return df

    # Log the data type of the column
    column_dtype = df[json_column].dtype
    sample_value = df[json_column].iloc[0] if len(df) > 0 else None
    sample_type = type(sample_value).__name__ if sample_value is not None else "None"

    _logger.info(
        f"Column '{json_column}' has dtype: {column_dtype}, "
        f"first value type: {sample_type}"
    )

    # Function to extract the value for a specific key from a JSON string or dictionary
    def extract_value(value: Union[dict, str, None, Any]) -> Any:
        # Handle None values
        if value is None:
            return pd.NA

        # Handle dictionary objects directly
        if isinstance(value, dict):
            return value.get(key, pd.NA)

        # Handle string values
        if isinstance(value, str):
            # Check for empty or NA strings
            if not value or pd.isna(value):
                return pd.NA

            # Try to parse as JSON
            try:
                import json

                data = json.loads(value.replace("'", '"'))
                return data.get(key, pd.NA)
            except json.JSONDecodeError:
                _logger.warning(f"Failed to parse JSON string: {value[:50]}...")
                return pd.NA

        # If we get here, it's an unexpected type
        _logger.warning(f"Unexpected type in {json_column}: {type(value).__name__}")
        return pd.NA

    # Apply the extraction function to the JSON column
    df[new_column_name] = df[json_column].apply(extract_value)

    return df


# Register extensions for each segmentation area
@_register("hypertransmission")
def extract_hypertransmission(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting hypertransmission area."""
    _logger.info(
        f"Running hypertransmission extension. Available columns: {df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_areas",
        key="hypertransmission",
        new_column_name="Hypertransmission",
    )


@_register("rpe_disruption")
def extract_rpe_disruption(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting RPE disruption area."""
    _logger.info(
        f"Running rpe_disruption extension. Available columns: {df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_areas",
        key="rpe_disruption",
        new_column_name="RPE disruption",
    )


@_register("is_os_disruption")
def extract_is_os_disruption(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting IS/OS disruption area."""
    _logger.info(
        f"Running is_os_disruption extension. Available columns: {df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_areas",
        key="is_os_disruption",
        new_column_name="IS/OS disruption",
    )


@_register("rpe_atrophy")
def extract_rpe_atrophy(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting RPE atrophy area."""
    _logger.info(
        f"Running rpe_atrophy extension. Available columns: {df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_areas",
        key="rpe_atrophy",
        new_column_name="RPE atrophy",
    )


@_register("neurosensory_retina_atrophy")
def extract_neurosensory_retina_atrophy(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting neurosensory retina atrophy area."""
    _logger.info(
        f"Running neurosensory_retina_atrophy extension. Available columns: "
        f"{df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_areas",
        key="neurosensory_retina_atrophy",
        new_column_name="Neurosensory retina atrophy",
    )


@_register("serous_rpe_detachment")
def extract_serous_rpe_detachment(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting serous rpe detachment volume."""
    _logger.info(
        f"Running serous_rpe_detachment extension. Available columns: "
        f"{df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_volumes",
        key="serous_rpe_detachment",
        new_column_name=SEROUS_RPE_DETACHMENT_COL,
    )


@_register("intraretinal_cystoid_fluid")
def extract_intraretinal_cystoid_fluid(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting intraretinal cystoid fluid volume."""
    _logger.info(
        f"Running intraretinal_cystoid_fluid extension. Available columns: "
        f"{df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_volumes",
        key="intraretinal_cystoid_fluid",
        new_column_name=INTRARETINAL_CYSTOID_FLUID_COL,
    )


@_register("subretinal_fluid")
def extract_subretinal_fluid(df: pd.DataFrame) -> pd.DataFrame:
    """Extension function for extracting subretinal fluid volume."""
    _logger.info(
        f"Running subretinal_fluid extension. Available columns: {df.columns.tolist()}"
    )
    return extract_json_value(
        df,
        json_column="segmentation_volumes",
        key="subretinal_fluid",
        new_column_name=SUBRETINAL_FLUID_COL,
    )
