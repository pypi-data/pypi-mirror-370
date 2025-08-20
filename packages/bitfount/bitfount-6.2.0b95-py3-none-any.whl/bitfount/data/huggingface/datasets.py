"""Hugging Face Datasets."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
import logging
from typing import Any, Optional, Union, cast

import numpy as np
import pandas as pd

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter, _InferenceSplitter

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    import torch

from bitfount.data.datasets import (
    _BaseBitfountDataset,
    _FileSystemIterableBitfountDataset,
    _IterableBitfountDataset,
)
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.types import (
    _DataEntryAllowingText,
    _DataEntryAllowingTextWithKey,
    _HFSegmentation_ImageTextEntry,
    _ImagesData,
    _TabularData,
    _TextData,
)

_logger = logging.getLogger(__name__)


class _BaseHuggingFaceDataset(_BaseBitfountDataset):
    """Hugging Face Dataset."""

    def __init__(
        self, labels2id: Optional[Mapping[str, int]] = None, **kwargs: Any
    ) -> None:
        self.labels2id = labels2id
        super().__init__(**kwargs)

    def _set_text_values(self, data: pd.DataFrame) -> None:
        """Sets `self.text`."""
        self.text = data.loc[
            :, self.selected_cols_semantic_types.get("text", [])
        ].values.tolist()

    def __len__(self) -> int:
        """Returns the length of the dataset."""
        data_splitter: DatasetSplitter
        if self.data_splitter is None:
            _logger.warning(
                "No datasplitter was specified during dataset creation."
                " Defaulting to InferenceSplitter."
            )
            data_splitter = _InferenceSplitter()
        else:
            data_splitter = self.data_splitter

        data = self.get_dataset_split(
            split=self.data_split, data_splitter=data_splitter
        )
        self._reformat_data(data)
        return len(self.x_var[0])

    def _reformat_data(self, data: pd.DataFrame) -> None:
        """Reformats the data to be compatible with the Dataset class."""
        self._set_batch_transformation_processors()
        self.data = data.reset_index(drop=True)
        if self.labels2id is not None:
            # Encode categorical labels to integers in the data
            self.data = self.data.replace(self.labels2id)

        X, Y = self._get_xy(self.data)

        if self.image_columns:
            self._set_image_values(X)

        self._set_tabular_values(X)
        self._set_text_values(X)

        # Package tabular, image and text columns together under the x_var attribute
        self.x_var = (self.tabular, self.image, self.text)

        self._set_target_values(Y)

    def __getitem__(
        self, idx: Union[int, Sequence[int], torch.Tensor]
    ) -> _DataEntryAllowingText:
        if torch.is_tensor(idx):
            list_idx: list = idx.tolist()
            return self._getitem(list_idx)
        else:
            return self._getitem(idx)

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntryAllowingText:
        """Returns the item referenced by index `idx` in the data."""
        image: _ImagesData
        tab: _TabularData
        text: _TextData
        target: Union[np.ndarray, tuple[np.ndarray, ...]]

        # Get target
        if len(self.y_var) == 0:
            # Set the target, if the dataset has no supervision,
            # choose set the default value to be 0.
            target = np.array(0)
        elif (
            "image" in self.selected_cols_semantic_types
            and self.target in self.selected_cols_semantic_types["image"]
        ):
            # Check if the target is an image and load it.
            target = self._load_images(idx, what_to_load="target")
        else:
            target = self.y_var[idx]

        # If the Dataset contains both tabular and image data
        if self.image.size and self.tabular.size:
            tab = self.tabular[idx]
            image = self._load_images(idx)

            # _ImageAndTabularEntry[no support data] or
            # _Segmentation_ImageAndTabEntry[no support data]
            return (tab, image), target

        # If the Dataset contains only tabular data
        elif self.tabular.size:
            tab = self.tabular[idx]

            # _TabularEntry[no support data]
            return tab, target

        # If the Dataset contains image and text data
        # Used for Hugging Face image segmentation algorithm
        elif self.image.size and np.array(self.text).size:
            image = self._load_images(idx)
            text = self.text[idx]

            # _HFSegmentation_ImageTextEntry
            return cast(_HFSegmentation_ImageTextEntry, (image, text, target))

        # If the Dataset contains only image data
        elif self.image.size:
            image = self._load_images(idx)
            # _ImageEntry[no support data] or
            # _Segmentation_ImageEntry[no support data]
            return image, target

        # All cases remaining cases require text data only need the text (for now)
        else:
            text = self.text[idx]

            # _TextEntry
            return text, target


class _IterableHuggingFaceDataset(_BaseHuggingFaceDataset, _IterableBitfountDataset):
    """Iterable HuggingFace Dataset.

    The main difference between this and other datasets
    is that it does not require a schema and does not
    include the support columns.
    """

    datasource: BaseSource

    def __iter__(self) -> Iterator[_DataEntryAllowingText]:
        """Iterates over the dataset."""
        for data_partition in self.yield_dataset_split(
            split=self.data_split, data_splitter=self.data_splitter
        ):
            self._reformat_data(data_partition)

            for idx in range(len(self.data)):
                yield self._getitem(idx)

    def __len__(self) -> int:
        # _BaseHuggingFaceDataset should take priority in MRO _except_ for __len__ as
        # the method implemented in _IterableBitfountDataset is better suited for the
        # iterable use-case (i.e. doesn't rely on a data split finder that requires
        # data to be loaded)
        return _IterableBitfountDataset.__len__(self)


class _FileIterableHuggingFaceDataset(
    _IterableHuggingFaceDataset, _FileSystemIterableBitfountDataset
):
    """File Iterable HuggingFace Dataset."""

    data_keys: list[str]

    datasource: FileSystemIterableSource

    def __iter__(self) -> Iterator[_DataEntryAllowingTextWithKey]:  # type: ignore[override] # Reason: [BIT-3851] temp fix for supporting data key passthrough # noqa: E501
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
        self.data_keys = cast(
            np.ndarray, data.loc[:, ORIGINAL_FILENAME_METADATA_COLUMN].values
        ).tolist()

    def __getitem__(  # type: ignore[override] # Reason: [BIT-3851] temp fix for supporting data key passthrough # noqa: E501
        self, idx: Union[int, Sequence[int], torch.Tensor]
    ) -> _DataEntryAllowingTextWithKey:
        # Super method relies on calls to _getitem(), etc, which we have changed in
        # this class; this means we can constrain the return type even though we are
        # calling the super method
        return cast(_DataEntryAllowingTextWithKey, super().__getitem__(idx))

    def _getitem(self, idx: Union[int, Sequence[int]]) -> _DataEntryAllowingTextWithKey:  # type: ignore[override] # Reason: [BIT-3851] temp fix for supporting data key passthrough # noqa: E501
        d: _DataEntryAllowingText = super()._getitem(idx)
        if isinstance(idx, int):
            data_key = self.data_keys[idx]
        else:
            # TODO: [BIT-3851] support multi-index
            raise TypeError(f"idx of type ({type(idx)}) is not supported")

        # mypy: lack of support for tuple unpacking means we need to manually cast this
        new_d: _DataEntryAllowingTextWithKey = cast(
            _DataEntryAllowingTextWithKey, (*d, data_key)
        )
        return new_d
