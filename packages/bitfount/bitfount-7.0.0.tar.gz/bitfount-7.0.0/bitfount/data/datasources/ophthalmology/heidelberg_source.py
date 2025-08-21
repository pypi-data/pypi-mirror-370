"""Data source for loading ophthalmology files using private-eye."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
import logging
import os
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Optional,
    TypedDict,
    Union,
    cast,
    get_type_hints,
)

import pandas as pd

from bitfount.data.datasources.ophthalmology.ophth_ds_types import (
    ProcessedDataRequiredTypes,
)
from bitfount.data.datasources.ophthalmology.ophth_ds_utils import (
    make_path_absolute,
    make_path_relative,
)
from bitfount.data.datasources.ophthalmology.ophthalmology_base_source import (
    IMAGE_COLUMN_PREFIX,
)
from bitfount.data.datasources.ophthalmology.private_eye_base_source import (
    PrivateEyeParser,
    _PrivateEyeSource,
)
from bitfount.data.datasources.utils import (
    ORIGINAL_FILENAME_METADATA_COLUMN,
    FileSystemFilter,
)
from bitfount.data.exceptions import DataSourceError
from bitfount.types import UsedForConfigSchemas
from bitfount.utils import delegates

if TYPE_CHECKING:
    from typing_extensions import NotRequired

logger = logging.getLogger(__name__)

HEIDELBERG_FILE_EXTENSION: Final[str] = ".sdb"
HEIDELBERG_REQUIRED_FIELDS = get_type_hints(ProcessedDataRequiredTypes)


@dataclass
class HeidelbergCSVColumns(UsedForConfigSchemas):
    """Arguments for ophthalmology columns in the csv.

    Args:
        heidelberg_files_col: The name of the column that points to Heidelberg
            files in the CSV file. Defaults to 'heidelberg_file'. These files
            should all be in the `.sdb` format.
    """

    heidelberg_files_col: str = "heidelberg_file"


class _HeidelbergCSVColumnsTD(TypedDict):
    """Typed dict form of HeidelbergCSVColumns dataclass."""

    heidelberg_files_col: NotRequired[str]


@delegates()
class HeidelbergSource(_PrivateEyeSource):
    """Data source for loading Heidelberg files.

    Args:
        path: The path to the directory containing the Heidelberg files or to a
            CSV file that includes Heidelberg files as one of its columns. If a CSV
            file is provided, the file extensions specified in `file_extension` will
            be ignored. If a CSV file is provided, the `heidelberg_csv_columns`
            argument should also be provided.
        parsers: The private eye parsers to use for the different file extensions.
            Only needs to be supplied if file_extension filter is non-default. Can
            either be a single parser to use for all file extensions or a mapping of
            file extensions to parser type. Defaults to appropriate parser(s) for the
            default file extension(s).
        heidelberg_csv_columns: If `path` is a CSV file, this contains information
            about the specific columns that contain the path information for the
            Heidelberg files. If not provided, it is assumed that the CSV file
            contains a column named 'heidelberg_file' that contains the paths to
            the Heidelberg files. Defaults to None.
        **kwargs: Keyword arguments passed to the parent base classes.
    """

    def __init__(
        self,
        path: Union[os.PathLike, str],
        parsers: Optional[
            Union[PrivateEyeParser, Mapping[str, PrivateEyeParser]]
        ] = None,
        heidelberg_csv_columns: Optional[
            Union[HeidelbergCSVColumns, _HeidelbergCSVColumnsTD]
        ] = None,
        required_fields: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        # Create default parsers if not provided
        # (can't be in args as mutable type)
        if parsers is None:
            parsers = {
                ".sdb": PrivateEyeParser.HEIDELBERG,
            }
        elif isinstance(parsers, Mapping) and ".e2e" in parsers:
            logger.warning(
                "Support for '.e2e' file parser type is deprecated and has "
                "been removed. Only the '.sdb' file parser is currently supported."
            )
        # Parse CSV if path is a CSV file
        # If a csv file has been provided, we load the files named in the csv file.
        # The file names, if relative, are assumed relative to the _CSV_. To enable
        # this, we then set path to path.parent.
        self._csv_df: Optional[pd.DataFrame] = None
        if Path(path).suffix == ".csv":
            csv_path = Path(path).resolve()  # ensures absolute path
            self._csv_df = pd.read_csv(csv_path)
            path = csv_path.parent

        # Parse Heidelberg CSV options
        # Parse heidelberg_csv_columns if provided or else use the default column names
        self._heidelberg_csv_columns: Optional[HeidelbergCSVColumns] = None
        if self._csv_df is None and heidelberg_csv_columns is not None:
            logger.warning(
                f"CSV columns info was specified but target was not a CSV file"
                f" ({str(path)}); ignoring CSV columns info.)"
            )
        elif heidelberg_csv_columns is not None:  # self._csv_df is not None
            if isinstance(heidelberg_csv_columns, HeidelbergCSVColumns):
                self._heidelberg_csv_columns = heidelberg_csv_columns
            else:  # is typed dict
                self._heidelberg_csv_columns = HeidelbergCSVColumns(
                    **heidelberg_csv_columns
                )
        elif self._csv_df is not None and heidelberg_csv_columns is None:
            logger.warning(
                "CSV file provided but no column info specified. Using default columns."
            )
            self._heidelberg_csv_columns = HeidelbergCSVColumns()

        filter_: Optional[FileSystemFilter] = kwargs.pop("filter", None)
        if filter_ is not None:
            file_extension = filter_.file_extension or []
            if ".e2e" in file_extension:
                logger.warning(
                    "Support for '.e2e' file extension is deprecated and has "
                    "been removed. Only '.sdb' files are supported."
                )
                filter_.file_extension = [HEIDELBERG_FILE_EXTENSION]
            elif file_extension != [".sdb"]:
                logger.warning(
                    "HeidelbergSource only supports '.sdb' files. Ignoring "
                    f"file_extension={file_extension}."
                )
                filter_.file_extension = [HEIDELBERG_FILE_EXTENSION]
        else:
            filter_ = FileSystemFilter(file_extension=HEIDELBERG_FILE_EXTENSION)

        super().__init__(
            private_eye_parser=parsers,
            path=path,
            filter=filter_,
            **kwargs,
        )
        if required_fields is None:
            required_fields = HEIDELBERG_REQUIRED_FIELDS
        self.required_fields = required_fields
        self.image_fields = IMAGE_COLUMN_PREFIX

    def _get_file_names_from_csv(self) -> list[str]:
        """Returns a list of file names in the CSV file for the specified modality.

        These file paths will be absolute paths, regardless of their origin.

        Returns:
            The list of file names.
        """
        file_names: list[str] = []
        # If using a CSV file we want to extract the files from the target column
        # in the CSV
        if self._csv_df is not None:
            # If self._csv_df is not None then self._heidelberg_csv_columns will
            # also not be None
            self._heidelberg_csv_columns = cast(
                HeidelbergCSVColumns, self._heidelberg_csv_columns
            )

            file_names_raw: list[str] = list(
                self._csv_df[self._heidelberg_csv_columns.heidelberg_files_col]
            )
            file_names_paths = [
                make_path_absolute(Path(i), self.path) for i in file_names_raw
            ]
            file_names = [str(i) for i in file_names_paths]

        return file_names

    @cached_property
    def _file_names(self) -> list[str]:
        """Returns a list of file names in the directory that match the DOB args.

        These file paths will be absolute paths, regardless of their origin.
        """
        if self._csv_df is not None:
            file_names = self._get_file_names_from_csv()
        else:
            file_names = super()._file_names

        return file_names

    def _add_metadata_to_data(
        self, data: dict[str, Any], filename: str
    ) -> dict[str, Any]:
        """Adds metadata to the data.

        Args:
            data: The data to add metadata to.
            filename: The filename of the file to be processed.

        Returns:
            The data with metadata added.
        """
        data[ORIGINAL_FILENAME_METADATA_COLUMN] = filename
        modify_time = os.path.getmtime(filename)
        data["_last_modified"] = datetime.fromtimestamp(modify_time).isoformat()
        # Generate additional string which is unique for each row
        if (
            ("laterality" in data)
            and ("protocol" in data)
            and ("_series_index" in data)
        ):
            data["_hash_modifier"] = (
                data["protocol"]
                + " "
                + data["laterality"]
                + " "
                + str(data["_series_index"])
            )
        # Track the first two directory levels so that we can easily
        # process the possible labels later on as needed
        relative_filepath = Path(filename).relative_to(self.path).parts
        if len(relative_filepath) > 1:
            data[self._first_directory_in_path] = relative_filepath[0]
        if len(relative_filepath) > 2:
            data[self._second_directory_in_path] = relative_filepath[1]

        return data

    def _post_process_file(
        self, data: dict[str, Any], filename_path: Path
    ) -> dict[str, Any]:
        """Apply any post-processing to the data found in _process_file.

        If using in Heidelberg CSV mode this will involve matching the extracted
        data with the data from the CSV.
        """
        if self._csv_df is not None and data is not None:
            if self._heidelberg_csv_columns is None:
                raise DataSourceError(
                    "Heidelberg CSV is specified"
                    " but CSV columns info has not been instantiated."
                    " This should have occurred during HeidelbergSource initialization."
                )
            for _row_idx, row in self._csv_df.iterrows():
                # Don't know if the file path in the CSV is relative or absolute
                # and can't guarantee that `filename` is either. So check both
                # relative and absolute forms.
                row_filename_path: str = cast(
                    str, row[self._heidelberg_csv_columns.heidelberg_files_col]
                )
                if (
                    make_path_absolute(row_filename_path, self.path)
                    == make_path_absolute(filename_path, self.path)
                ) or (
                    make_path_relative(row_filename_path, self.path)
                    == make_path_relative(filename_path, self.path)
                ):
                    data.update({str(k): v for k, v in row.to_dict().items()})
                    break
            else:
                raise (
                    DataSourceError("No rows in the csv map to the same image file.")
                )

        return data
