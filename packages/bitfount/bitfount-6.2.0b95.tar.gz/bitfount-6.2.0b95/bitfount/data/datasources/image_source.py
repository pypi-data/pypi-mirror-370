"""Module containing ImageSource class.

ImageSource class handles loading of JPG and PNG image data.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional, Union

import numpy as np
import pandas as pd
from PIL import Image

from bitfount.data.datasources.base_source import FileSystemIterableSourceInferrable
from bitfount.data.datasources.utils import (
    FileSystemFilter,
)
from bitfount.utils import delegates

logger = logging.getLogger(__name__)
IMAGE_FILE_EXTENSIONS: list[str] = [
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
]
IMAGE_ATTRIBUTE = "Pixel Data"


@delegates()
class ImageSource(FileSystemIterableSourceInferrable):
    """Data source for loading JPG and PNG image files.

    Args:
        path: The path to the directory containing the image files.
        file_extensions: The file extensions to look for.
          If None, populates with ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'].
        **kwargs: Keyword arguments passed to the parent base classes.
    """

    def __init__(
        self,
        path: Union[os.PathLike, str],
        file_extensions: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        if file_extensions is None:
            file_extensions = IMAGE_FILE_EXTENSIONS
        self.file_extenstions = file_extensions
        filter_: Optional[FileSystemFilter] = kwargs.pop("filter", None)
        if filter_ is None:
            filter_ = FileSystemFilter(file_extension=file_extensions)

        super().__init__(path=path, filter=filter_, **kwargs)
        self.image_columns = {IMAGE_ATTRIBUTE}

    def _process_file(
        self,
        filename: str,
        skip_non_tabular_data: bool = False,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Loads the image file specified by `filename`.

        Args:
            filename: The name of the file to process.
            skip_non_tabular_data: Whether we can avoid loading non-tabular data,
                e.g. image data (can be set to True when generating schemas).
            **kwargs: Additional keyword arguments.

        Returns:
            The processed image as a dictionary of keys and values within a list
            containing just that element.
        """
        try:
            data = self._process_image_file(
                filename, skip_non_tabular_data=skip_non_tabular_data
            )
        except Exception as e:
            logger.warning(f"Unexpected error when processing file {filename}: {e}.")
            data = None

        if not data:
            logger.warning(f"Skipping file {filename}.")
            self.skipped_files.add(filename)
            return []

        return [data]

    def _process_image_file(
        self,
        filename: str,
        skip_non_tabular_data: bool = False,
    ) -> Optional[dict[str, Any]]:
        """Read and process the image file.

        Args:
            filename: The filename of the file to be processed.
            skip_non_tabular_data: Don't load pixel data from file.

        Returns:
            The processed image data as a dictionary.
        """
        data: dict[str, Any] = {}

        # Add basic file metadata
        data["Filename"] = os.path.basename(filename)
        data["FileExtension"] = os.path.splitext(filename)[1].lower()

        if skip_non_tabular_data:
            data[IMAGE_ATTRIBUTE] = "<SKIPPED>"
            return data

        try:
            with Image.open(filename) as img:
                # Convert image to numpy array
                arr = np.array(img)

                # Add image metadata
                data["ImageWidth"] = img.width
                data["ImageHeight"] = img.height
                data["ImageMode"] = img.mode
                data["ImageFormat"] = img.format

                # Add the image data
                data[IMAGE_ATTRIBUTE] = arr

        except Exception as e:
            logger.warning(f"Error when reading image file {filename}: {e}")
            return None

        return data

    def _process_dataset(self, dataframe: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Process the dataset after loading.

        Args:
            dataframe: The dataframe to process.
            **kwargs: Additional keyword arguments.

        Returns:
            The processed dataframe.
        """
        return dataframe
