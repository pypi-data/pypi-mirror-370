"""Utility functions for interacting with ophthalmology datasources."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final, Union

SLO_ORIGINAL_FILENAME_METADATA_COLUMN: Final[str] = "_slo_original_filename"


class NoParserForFileExtension(KeyError):
    """Indicates no parser was specified for a file extension."""

    pass


def make_path_absolute(
    file_path: Union[str, os.PathLike], parent_folder: Union[str, os.PathLike]
) -> Path:
    """Makes a relative file path absolute with respect to a parent folder.

    Does not change an already absolute file path.
    """
    file_path = Path(file_path)
    parent_folder = Path(parent_folder)
    return (
        file_path if file_path.is_absolute() else parent_folder / file_path
    ).resolve()


def make_path_relative(
    file_path: Union[str, os.PathLike], parent_folder: Union[str, os.PathLike]
) -> Path:
    """Makes an absolute file path relative with respect to a parent folder.

    Does not change an already relative file path.
    """
    file_path = Path(file_path)
    parent_folder = Path(parent_folder)
    return (
        file_path
        if not file_path.is_absolute()
        else file_path.relative_to(parent_folder)
    )
