"""PyTorch implementations for Bitfount Dataset classes."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
import logging
from typing import Union, cast

from natsort import natsorted
import numpy as np
import pandas as pd
import torch
from torch.utils.data import IterableDataset as PTIterableDataset

from bitfount.data.datasets import (
    _BaseBitfountDataset,
    _FileSystemIterableBitfountDataset,
    _IterableBitfountDataset,
)
from bitfount.data.datasources.base_source import FileSystemIterableSource
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.types import (
    _DataEntry,
    _DataEntryWithKey,
    _ImagesData,
    _SupportData,
    _TabularData,
)

_logger = logging.getLogger(__name__)


class BasePyTorchDataset(_BaseBitfountDataset):
    """Base class for representing a Pytorch dataset."""

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntry:
        """Returns the item referenced by index `idx` in the data."""
        image: _ImagesData
        tab: _TabularData
        sup: _SupportData

        target: Union[np.ndarray, tuple[np.ndarray, ...]]
        if self.schema is not None:
            # Schema is None for HuggingFace datasets which is
            # handled separately, so we can cast.
            if len(self.y_var) == 0:
                # Set the target, if the dataset has no supervision,
                # choose set the default value to be 0.
                target = np.array(0)
            elif (
                "image" in self.schema.features
                and self.target in self.schema.features["image"]
            ):
                # Check if the target is an image and load it.
                target = self._load_images(idx, what_to_load="target")
            else:
                target = self.y_var[idx]

            # If the Dataset contains both tabular and image data
            if self.image.size and self.tabular.size:
                tab = self.tabular[idx]
                sup = self.support_cols[idx]
                image = self._load_images(idx)
                if self.ignore_support_cols:
                    # _ImageAndTabularEntry[no support data] or
                    # _Segmentation_ImageAndTabEntry[no support data]
                    return (
                        tab,
                        image,
                    ), target

                # _ImageAndTabularEntry[support data] or
                # _Segmentation_ImageAndTabEntry[support data]
                return (tab, image, sup), target

            # If the Dataset contains only tabular data
            elif self.tabular.size:
                tab = self.tabular[idx]
                sup = self.support_cols[idx]
                if self.ignore_support_cols:
                    # _TabularEntry[no support data]
                    return tab, target

                # _TabularEntry[support data]
                return (tab, sup), target

            # If the Dataset contains only image data
            else:
                sup = self.support_cols[idx]
                image = self._load_images(idx)
                if self.ignore_support_cols:
                    # _ImageEntry[no support data] or
                    # _Segmentation_ImageEntry[no support data]
                    return image, target

                # _ImageEntry[support data] or
                # _Segmentation_ImageEntry[support data]
                return (image, sup), target
        else:
            raise TypeError(
                "Dataset initialised without a schema. "
                "The only datasets that support this are the Huggingface algorithms, "
                "so make sure to use the correct datafactory for the dataset."
            )


class _PyTorchIterableDataset(
    _IterableBitfountDataset, BasePyTorchDataset, PTIterableDataset
):
    """See base class."""

    def __iter__(self) -> Iterator[_DataEntry]:
        """Iterates over the dataset."""
        for data_partition in self.yield_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        ):
            self._reformat_data(data_partition)

            for idx in range(len(self.data)):
                yield self._getitem(idx)


class _PytorchFileIterableDataset(
    _FileSystemIterableBitfountDataset, _PyTorchIterableDataset, PTIterableDataset
):
    """See base class.

    This class specifically has support for keyed-data entries to be returned,
    i.e. data elements will be associated with the filename that they came from.
    """

    data_keys: list[str]

    datasource: FileSystemIterableSource

    def __iter__(self) -> Iterator[_DataEntryWithKey]:  # type: ignore[override] # Reason: [BIT-3851] temp fix for supporting data key passthrough # noqa: E501
        """Iterates over the dataset."""
        for data_partition_idx, data_partition in enumerate(
            self.yield_dataset_split(
                split=self.data_split, data_splitter=self.data_splitter
            )
        ):
            try:
                self._reformat_data(data_partition)
            except Exception as reformat_exception:
                _logger.error(
                    f"Error whilst attempting to reformat"
                    f" data partition {data_partition_idx};"
                    f" skipping partition: {reformat_exception}"
                )
                continue

            try:
                for idx in range(len(self.data)):
                    try:
                        yield self._getitem(idx)
                    except Exception as yield_exception:
                        # See if we can get the data key, as that would be most useful
                        try:
                            data_key = self.data_keys[idx]
                            _logger.warning(
                                f"Error whilst iterating"
                                f" data partition {data_partition_idx};"
                                f" encountered error for index {idx} ({data_key}):"
                                f" {yield_exception}"
                            )
                        except Exception:
                            _logger.warning(
                                f"Error whilst iterating"
                                f" data partition {data_partition_idx};"
                                f" encountered error for index {idx}: {yield_exception}"
                            )

            except Exception as for_loop_exception:
                _logger.error(
                    f"Error whilst iterating through"
                    f" data partition {data_partition_idx};"
                    f" skipping remainder of partition: {for_loop_exception}"
                )
                continue

    def _reformat_data(self, data: pd.DataFrame) -> None:
        super()._reformat_data(data)

        # Also extract the key for the data (currently filename)
        self.data_keys = cast(
            np.ndarray, data.loc[:, ORIGINAL_FILENAME_METADATA_COLUMN].values
        ).tolist()

    def _set_image_values(self, data: pd.DataFrame) -> None:
        """Sets `self.image`."""
        # Reset the image attr
        self.image = np.array([])
        for col in natsorted(self.image_columns):
            if col in data.columns:
                x_img = np.expand_dims(
                    cast(np.ndarray, data.loc[:, col].values), axis=1
                )
                # If there are multiple images, we start concatenating `self.image`
                # with each next image
                self.image = (
                    x_img
                    if self.image.size == 0
                    else np.concatenate((self.image, x_img), axis=1)
                )

    def __getitem__(
        self, idx: Union[int, Sequence[int], torch.Tensor]
    ) -> _DataEntryWithKey:
        # Super method relies on calls to _getitem(), etc, which we have changed in
        # this class; this means we can constrain the return type even though we are
        # calling the super method
        return cast(_DataEntryWithKey, super().__getitem__(idx))

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntryWithKey:  # type: ignore[override] # Reason: [BIT-3851] temp fix for supporting data key passthrough # noqa: E501
        d: _DataEntry = super()._getitem(idx)
        if isinstance(idx, int):
            data_key = self.data_keys[idx]
        else:
            # TODO: [BIT-3851] support multi-index
            raise TypeError(f"idx of type ({type(idx)}) is not supported")

        # Combine main data with the appropriate key
        # mypy: lack of support for tuple unpacking means we need to manually cast this
        new_d: _DataEntryWithKey = cast(_DataEntryWithKey, (*d, data_key))
        return new_d
