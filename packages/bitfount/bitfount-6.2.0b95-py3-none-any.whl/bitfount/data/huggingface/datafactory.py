"""HuggingFace-specific implementation of the DataFactory provider."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, Union

from bitfount.data.datafactory import _DataFactory
from bitfount.data.datasets import _BaseBitfountDataset
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.huggingface.dataloaders import (
    HuggingFaceIterableBitfountDataLoader,
)
from bitfount.data.huggingface.datasets import (
    _FileIterableHuggingFaceDataset,
    _IterableHuggingFaceDataset,
)
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import DataSplit, _SemanticTypeValue
from bitfount.types import _JSONDict


class _BaseHuggingFaceDataFactory(_DataFactory):
    """A HuggingFace-specific implementation of the DataFactory provider."""

    def create_dataloader(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> HuggingFaceIterableBitfountDataLoader:
        """See base class."""
        kwargs["batch_size"] = batch_size

        # torch is part of our main requirements, and if using
        # a torch model for any of the hugging face tasks, will need to be installed.
        if isinstance(dataset, _IterableHuggingFaceDataset):
            return HuggingFaceIterableBitfountDataLoader(dataset, **kwargs)
        raise TypeError(
            "The _HuggingFaceDataFactory class only supports "
            "subclasses of HuggingFace Dataset for creating a DataLoader."
        )

    def create_dataset(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter],
        data_split: DataSplit,
        selected_cols: list[str],
        selected_cols_semantic_types: Mapping[_SemanticTypeValue, list[str]],
        selected_col_prefix: Optional[str] = None,
        image_cols_prefix: Optional[str] = None,
        schema: Optional[BitfountSchema] = None,
        target: Optional[Union[str, list[str]]] = None,
        batch_transforms: Optional[list[dict[str, _JSONDict]]] = None,
        auto_convert_grayscale_images: bool = True,
        image_prefix_batch_transforms: Optional[list[dict[str, _JSONDict]]] = None,
        **kwargs: Any,
    ) -> Union[_IterableHuggingFaceDataset, _FileIterableHuggingFaceDataset]:
        """See base class."""
        if isinstance(datasource, FileSystemIterableSource):
            return _FileIterableHuggingFaceDataset(
                datasource=datasource,
                data_splitter=data_splitter,
                data_split=data_split,
                target=target,
                selected_cols=selected_cols,
                selected_cols_semantic_types=selected_cols_semantic_types,
                batch_transforms=batch_transforms,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                image_prefix_batch_transforms=image_prefix_batch_transforms,
                **kwargs,
            )
        else:
            return _IterableHuggingFaceDataset(
                datasource=datasource,
                data_splitter=data_splitter,
                data_split=data_split,
                target=target,
                selected_cols=selected_cols,
                selected_cols_semantic_types=selected_cols_semantic_types,
                batch_transforms=batch_transforms,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                image_prefix_batch_transforms=image_prefix_batch_transforms,
                **kwargs,
            )
