"""Utility functions for interacting with pandas."""

from __future__ import annotations

from collections.abc import Callable, Collection, Generator, Iterable
from datetime import date, datetime
from functools import partial
import io
import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from cryptography.fernet import Fernet
import pandas as pd
from pandas import RangeIndex

from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    _BITFOUNT_PATIENT_ID_KEY,
    _BITFOUNT_PATIENT_ID_RENAMED,
    DOB_COL,
    NAME_COL,
)
from bitfount.utils.fs_utils import safe_write_to_file

if TYPE_CHECKING:
    from pandas.core.series import TimestampSeries

_CSV_READ_CHUNKSIZE = 100

_logger = logging.getLogger(__name__)


def conditional_dataframe_yielder(
    dfs: Iterable[pd.DataFrame],
    condition: Callable[[pd.DataFrame], pd.DataFrame],
    reset_index: bool = True,
) -> Generator[pd.DataFrame, None, None]:
    """Create a generator that conditionally yields rows from a set of dataframes.

    This replicates the standard `.loc` conditional indexing that can be used on
    a whole dataframe in a manner that can be applied to an iterable of dataframes
    such as is returned when chunking a CSV file.

    Args:
        dfs: An iterable of dataframes to conditionally yield rows from.
        condition: A callable that takes in a dataframe, applied a condition, and
            returns the edited/filtered dataframe.
        reset_index: Whether the index of the yielded dataframes should be reset.
            If True, a standard integer index is used that is consistent between
            the yielded dataframes (e.g. if yielded dataframe 10 ends with index
            42, yielded dataframe 11 will start with index 43).

    Yields:
        Dataframes from the iterable with rows included/excluded based on the
        condition. Empty dataframes, post-condition, are skipped.
    """
    curr_idx = 0
    for i, df in enumerate(dfs):
        tmp_df = condition(df)

        if tmp_df.empty:
            _logger.debug(
                f"Empty dataframe from applying {condition=} to dataframe {i}"
                f" of dataframe iterable;"
                f" skipping..."
            )
            continue
        else:
            new_rows = len(tmp_df)
            next_idx = curr_idx + new_rows

            if reset_index:
                _logger.debug(f"{curr_idx=}, {new_rows=}")
                idx = RangeIndex(curr_idx, next_idx)
                tmp_df = tmp_df.set_index(idx)

            yield tmp_df

            curr_idx = next_idx


def dataframe_iterable_join(
    joiners: Iterable[pd.DataFrame],
    joinee: pd.DataFrame,
    reset_joiners_index: bool = False,
) -> Generator[pd.DataFrame, None, None]:
    """Performs a dataframe join against a collection of dataframes.

    This replicates the standard `.join()` method that can be used on a whole
    dataframe in a manner that can be applied to an iterable of dataframes such
    as is returned when chunking a CSV file.

    This is equivalent to:
    ```
    joiner.join(joinee)
    ```

    Args:
        joiners: The collection of dataframes that should be joined against the joinee.
        joinee: The single dataframe that the others should be joined against.
        reset_joiners_index: Whether the index of the joiners dataframes should
            be reset as they are processed. If True, a standard integer index is
            used that is consistent between the yielded dataframes (e.g. if yielded
            dataframe 10 ends with index 42, yielded dataframe 11 will start with
            index 43).

    Yields:
        Dataframes from the iterable joined against the joineee. Empty dataframes
        are skipped.
    """
    curr_joiner_idx = 0
    for i, joiner in enumerate(joiners):
        if reset_joiners_index:
            new_joiner_rows = len(joiner)
            next_joiner_idx = curr_joiner_idx + new_joiner_rows

            idx = RangeIndex(curr_joiner_idx, next_joiner_idx)
            joiner = joiner.set_index(idx)

            curr_joiner_idx = next_joiner_idx

        joined: pd.DataFrame = joiner.join(joinee)

        if joined.empty:
            _logger.debug(
                f"Empty dataframe from joining joinee dataframe to dataframe {i}"
                f" of dataframe iterable;"
                f" skipping..."
            )
            continue
        else:
            yield joined


def append_dataframe_to_csv(
    csv_file: Union[str, os.PathLike], df: pd.DataFrame
) -> Path:
    """Append or write a dataframe to a CSV file.

    Handles appending a dataframe to an already existing CSV file that may contain
    differing columns.

    Additionally, handles safe writing to file, where a new file will be created if
    the desired one is inaccessible for some reason.

    Args:
        csv_file: The CSV file path to append/write to.
        df: The dataframe to append.

    Returns:
        The actual path the CSV was written to, which may differ from the requested
        one if that file was inaccessible.
    """
    csv_path: Path = Path(csv_file)

    # Append to existing
    if csv_path.exists():
        # Get existing CSV details. We only care about the columns, so don't need to
        # retrieve any rows.
        existing_df = pd.read_csv(csv_path, nrows=0, index_col=False)

        existing_columns = existing_df.columns
        df_columns = df.columns

        # See if the dataframe to append matches the dataframes that have already
        # been written to CSV
        if list(existing_columns) != list(df_columns):
            # As we may be manipulating the ordering/columns now, we need to make a
            # copy of the dataframe to work on
            df = df.copy()

            # There are four potential options for why the column lists may differ:
            # - Same elements, different order
            #   - Handled by column-reindexing the new dataframe to match
            # - existing_df has columns not in df
            #   - Handled by column-reindexing the new dataframe to match (NaN values
            #     in missing columns)
            # - df has columns not in existing_df
            #   - Handled by taking the union of the columns indexes and
            #     column-reindexing the new dataframe.
            #   - The new columns will be appended to the column index and so the
            #     existing CSV needs to be rewritten with this new index.
            # - existing_df has columns not in df AND df has columns not in existing_df
            #   - Handled by taking the union of the columns indexes and
            #     column-reindexing the new dataframe.
            #   - The new columns will be appended to the column index and so the
            #     existing CSV needs to be rewritten with this new index.
            #
            # We can take the index union in any case as it won't impact the first
            # two options.
            combined_index = existing_columns.union(df_columns)

            # Determine if we need to rewrite the existing CSV with additional columns
            new_cols = set(df_columns) - set(existing_columns)
            if new_cols:
                new_cols_str = ", ".join(sorted(new_cols))
                _logger.debug(
                    f"Appending dataframe to CSV requires"
                    f" new columns to be added to CSV: {new_cols_str}"
                )
                csv_path = rewrite_csv_with_new_columns(csv_path, combined_index)

            df = df.reindex(combined_index, axis="columns")

        _, csv_path = safe_write_to_file(
            partial(df.to_csv, mode="a", header=False, index=False, na_rep="N/A"),
            csv_path,
        )

    # Write new if non-existent
    else:
        _, csv_path = safe_write_to_file(
            partial(df.to_csv, mode="w", header=True, index=False, na_rep="N/A"),
            csv_path,
        )

    return csv_path


def rewrite_csv_with_new_columns(
    csv_file: Union[str, os.PathLike], new_column_index: pd.Index
) -> Path:
    """Rewrite an existing dataframe CSV with a new set of columns.

    This is of use when new columns need to be added to the CSV file. The function
    will read, chunked, the original CSV, change the column index and write it out to
    a new file. At the end of writing the new file, it will replace the original CSV.

    Additionally, handles safe writing to file, where a new file will be created if
    the desired one is inaccessible for some reason.

    Args:
        csv_file: The CSV file to rewrite.
        new_column_index: A pandas Index representing the new set of columns to use.

    Returns:
        The actual path the CSV was written to, which may differ from the requested
        one if that file was inaccessible.
    """
    _logger.debug(f"Rewriting CSV file {csv_file} with new column index")
    csv_path: Path = Path(csv_file)

    with TemporaryDirectory() as tmp_dir:
        new_csv = Path(tmp_dir) / "new.csv"

        for i, chunk in enumerate(
            pd.read_csv(csv_path, index_col=False, chunksize=_CSV_READ_CHUNKSIZE)
        ):
            new_chunk = chunk.reindex(new_column_index, axis="columns")

            # NOTE: don't need safe_write_to_file here as this is a temporary file
            #       away from the user
            if i == 0:  # i.e. this is the first thing being written to the new file
                new_chunk.to_csv(
                    new_csv, mode="w", header=True, index=False, na_rep="N/A"
                )
            else:
                new_chunk.to_csv(
                    new_csv, mode="a", header=False, index=False, na_rep="N/A"
                )

        # Rename original CSV file
        # We don't just delete/override it here so that we have a fallback file if
        # needed
        old_csv_path: Optional[Path] = None
        try:
            old_csv_path = csv_path.rename(csv_path.with_suffix(".csv.old"))
        except Exception as e:
            _logger.warning(f"Unable to backup original CSV file {csv_path}: {e}")

        # Move new CSV file into place
        new_csv, _ = safe_write_to_file(new_csv.rename, csv_path)

        # Delete old file
        if old_csv_path is not None:
            try:
                old_csv_path.unlink()
            except Exception as e:
                _logger.warning(
                    f"Error whilst trying to delete"
                    f" temporary CSV file {old_csv_path}: {e}"
                )

        return new_csv


def calculate_age(
    dob: pd.Timestamp | datetime | date,
    comparison_date: Optional[pd.Timestamp | datetime | date] = None,
) -> int:
    """Given a date of birth, calculate age at a target date.

    If no target date is supplied, use today.

    Args:
        dob: Date of birth (should be pandas Timestamp or python
            datetime/date).
        comparison_date: The date to calculate age at. Defaults to today.

    Returns:
        The age at the target date.
    """
    if comparison_date is None:
        comparison_date = pd.to_datetime("now", utc=True)

    return (
        comparison_date.year
        - dob.year
        - ((comparison_date.month, comparison_date.day) < (dob.month, dob.day))
    )


def calculate_ages(
    dobs: pd.Series[pd.Timestamp | datetime | date] | TimestampSeries,
    comparison_date: Optional[pd.Timestamp | datetime | date] = None,
) -> pd.Series[int]:
    """Given a series of date of births, calculate ages at a target date.

    If no target date is supplied, use today.

    Args:
        dobs: Series of date of births (should be pandas Timestamps or python
            datetimes/dates).
        comparison_date: The date to calculate age at. Defaults to today.

    Returns:
        A series of the ages at the target date.
    """
    if comparison_date is None:
        comparison_date = pd.to_datetime("now", utc=True)

    return dobs.apply(calculate_age, args=(comparison_date,))


def find_column_name(
    dataframe_or_columns: pd.DataFrame | pd.Index | Collection[str],
    potential_names: Collection[str],
) -> Optional[str]:
    """Find the actual column name used, given a set of potential column names.

    Args:
        dataframe_or_columns: The dataframe to match column names against or the
            column names as an Index or list of column names.
        potential_names: The collection of potential column names.

    Returns:
        The found matching column name or None if no matching column name was found.
    """
    present_columns: set[str]
    if isinstance(dataframe_or_columns, pd.DataFrame):
        present_columns = set(str(i) for i in dataframe_or_columns.columns)
    else:
        present_columns = set(str(i) for i in dataframe_or_columns)

    return next((col for col in potential_names if col in present_columns), None)


# Potential common variations on target column name
BITFOUNT_ID_COLUMNS = [
    _BITFOUNT_PATIENT_ID_KEY,  # From ophth_algo_types.py
    _BITFOUNT_PATIENT_ID_RENAMED,  # From ophth_algo_types.py
    "BitfountPatientID",
    "bitfount_patient_id",
    "Bitfount patient ID",
]


def find_bitfount_id_column(df: pd.DataFrame) -> Optional[str]:
    """Find the actual column name for bitfount id in the DataFrame.

    Args:
        df: DataFrame to search for bitfount id column

    Returns:
        The actual column name if found, None otherwise
    """
    return find_column_name(df, BITFOUNT_ID_COLUMNS)


# Potential common variations on target column name
DOB_COLUMNS = [
    DOB_COL,  # From ophth_algo_types.py
    "Patient's Birth Date",  # DICOM standard
    "Patient's DOB",  # DICOM renamed
    "PatientBirthDate",  # DICOM variation
    "dob",
    "DOB",
    "date_of_birth",
    "Date of birth",
    "Date of Birth",
    "Date Of Birth",
    "birth_date",
    "birthdate",
    "BirthDate",
    "birth_dt",
    "birthdt",
    "PatientDOB",
    "patient_dob",
    "patient_birth_date",
]


def find_dob_column(df: pd.DataFrame) -> Optional[str]:
    """Find the actual column name for date of birth in the DataFrame.

    Args:
        df: DataFrame to search for dob column

    Returns:
        The actual column name if found, None otherwise
    """
    return find_column_name(df, DOB_COLUMNS)


# Potential common variations on target column name
FULL_NAME_COLUMNS = [
    NAME_COL,  # From ophth_algo_types.py
    "Patient's Name",  # DICOM standard
    "Patient's name",  # DICOM renamed
    "PatientName",  # DICOM variation
    "name",
    "full_name",
    "fullname",
    "FullName",
    "patient_name",
    "patient_full_name",
    "PatientFullName",
    "complete_name",
    "CompleteName",
    "display_name",
    "DisplayName",
]


def find_full_name_column(df: pd.DataFrame) -> Optional[str]:
    """Find the actual column name for full name in the DataFrame.

    Args:
        df: DataFrame to search for name column

    Returns:
        The actual column name if found, None otherwise
    """
    return find_column_name(df, FULL_NAME_COLUMNS)


# Potential common variations on target column name
GIVEN_NAME_COLUMNS = [
    "given",  # FHIR format
    "given_name",
    "givenname",
    "Given Name",
    "first name",
    "first_name",
    "firstname",  # Common variation
    "First Name",
    "FirstName",
    "first",
    "fname",
    "f_name",
    "patient_first_name",
    "PatientFirstName",
    "patient_given_name",
]


def find_given_name_column(df: pd.DataFrame) -> Optional[str]:
    """Find the actual column name for given/first name in the DataFrame.

    Args:
        df: DataFrame to search for given name column

    Returns:
        The actual column name if found, None otherwise
    """
    return find_column_name(df, GIVEN_NAME_COLUMNS)


# Potential common variations on target column name
FAMILY_NAME_COLUMNS = [
    "family",  # FHIR format
    "family_name",
    "familyname",
    "Family Name",
    "lastname",  # Common variation
    "last_name",
    "Last Name",
    "LastName",
    "surname",
    "Surname",
    "last",
    "lname",
    "l_name",
    "patient_last_name",
    "PatientLastName",
    "patient_family_name",
]


def find_family_name_column(df: pd.DataFrame) -> Optional[str]:
    """Find the actual column name for family/last name in the DataFrame.

    Args:
        df: DataFrame to search for family name column

    Returns:
        The actual column name if found, None otherwise
    """
    return find_column_name(df, FAMILY_NAME_COLUMNS)


def to_encrypted_csv(
    df: pd.DataFrame,
    path: Union[str, os.PathLike],
    encryption_key: str,
    suffix: str = ".crypt",
    **kwargs: Any,
) -> Path:
    """Write DataFrame to an encrypted CSV file.

    Args:
        df: The DataFrame to write.
        path: The file path to write to.
        encryption_key: The encryption key to use for encrypting the CSV data.
        suffix: The suffix to add/replace if not already present. Defaults to ".crypt".
        **kwargs: Additional arguments passed to pandas.DataFrame.to_csv.

    Returns:
        The actual path the encrypted CSV was written to.
    """
    # Convert to Path object for easier manipulation
    file_path = Path(path)

    # Ensure the file has the encryption suffix
    if file_path.suffix != suffix:
        file_path = file_path.with_suffix(suffix)

    # Create Fernet cipher
    fernet = Fernet(encryption_key)

    # Write DataFrame to BytesIO buffer
    buffer = io.BytesIO()
    # Ensure consistent line endings across platforms for encryption
    if "lineterminator" not in kwargs:
        kwargs["lineterminator"] = "\n"
    df.to_csv(buffer, **kwargs)
    buffer.seek(0)

    # Encrypt the CSV data
    encrypted_data = fernet.encrypt(buffer.read())

    # Write encrypted data to file
    with open(file_path, "wb") as f:
        f.write(encrypted_data)

    return file_path


def read_encrypted_csv(
    path: Union[str, os.PathLike],
    encryption_key: str,
    suffix: str = ".crypt",
    **kwargs: Any,
) -> pd.DataFrame:
    """Read DataFrame from an encrypted CSV file.

    Args:
        path: The file path to read from.
        encryption_key: The encryption key to use for decrypting the CSV data.
        suffix: The suffix to add if not already present. Defaults to ".crypt".
        **kwargs: Additional arguments passed to pandas.read_csv.

    Returns:
        The DataFrame read from the encrypted CSV file.
    """
    # Convert to Path object for easier manipulation
    file_path = Path(path)

    # Ensure the file has the encryption suffix
    if file_path.suffix != suffix:
        file_path = file_path.with_suffix(suffix)

    # Create Fernet cipher
    fernet = Fernet(encryption_key)

    # Read encrypted data from file
    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    # Decrypt the data
    decrypted_data = fernet.decrypt(encrypted_data)

    # Read DataFrame from decrypted CSV data
    try:
        return cast(pd.DataFrame, pd.read_csv(io.BytesIO(decrypted_data), **kwargs))
    except pd.errors.EmptyDataError:
        # Handle empty DataFrames that have no columns to parse
        return pd.DataFrame()


def append_encrypted_dataframe_to_csv(
    csv_file: Union[str, os.PathLike],
    df: pd.DataFrame,
    encryption_key: str,
    suffix: str = ".crypt",
) -> Path:
    """Append a dataframe to an encrypted CSV file.

    Similar to append_dataframe_to_csv but works with encrypted files.

    Args:
        csv_file: The encrypted CSV file path to append/write to.
        df: The dataframe to append.
        encryption_key: The encryption key to use.
        suffix: The suffix for encrypted files. Defaults to ".crypt".

    Returns:
        The actual path the CSV was written to.
    """
    file_path = Path(csv_file)

    # Ensure the file has the encryption suffix
    if file_path.suffix != suffix:
        file_path = file_path.with_suffix(suffix)

    # If file exists, read existing data and append
    if file_path.exists():
        try:
            # Read existing encrypted CSV
            existing_df = read_encrypted_csv(file_path, encryption_key)

            # Handle column differences similar to append_dataframe_to_csv
            existing_columns = existing_df.columns
            df_columns = df.columns

            if list(existing_columns) != list(df_columns):
                df = df.copy()
                combined_index = existing_columns.union(df_columns)

                # Reindex both dataframes to have the same columns
                existing_df = existing_df.reindex(combined_index, axis="columns")
                df = df.reindex(combined_index, axis="columns")

            # Combine the dataframes
            combined_df = pd.concat([existing_df, df], ignore_index=True)

        except Exception as e:
            _logger.warning(f"Error reading existing encrypted CSV {file_path}: {e}")
            # If we can't read the existing file, just write the new data
            combined_df = df
    else:
        combined_df = df

    # Write the combined data as encrypted CSV
    return to_encrypted_csv(
        combined_df, file_path, encryption_key, suffix, index=False, na_rep="N/A"
    )
