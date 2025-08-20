"""Utility functions for HuggingFace data."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Optional, Union

from bitfount.data.huggingface.datafactory import _BaseHuggingFaceDataFactory
from bitfount.data.huggingface.datasets import (
    _IterableHuggingFaceDataset,
)

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.data.datasplitters import DatasetSplitter, DataSplit
    from bitfount.data.types import _SemanticTypeValue
    from bitfount.types import _JSONDict


def get_data_factory_dataset(
    datasource: BaseSource,
    data_split: DataSplit,
    selected_cols: list[str],
    selected_cols_semantic_types: Mapping[_SemanticTypeValue, list[str]],
    batch_transforms: Optional[list[dict[str, _JSONDict]]],
    data_splitter: Optional[DatasetSplitter] = None,
    labels2id: Optional[dict[str, int]] = None,
    target: Optional[Union[str, list[str]]] = None,
) -> tuple[_BaseHuggingFaceDataFactory, Union[_IterableHuggingFaceDataset]]:
    """Get the HuggingFace data factory and dataset for the given datasource."""
    data_factory = _BaseHuggingFaceDataFactory()
    dataset = data_factory.create_dataset(
        datasource=datasource,
        data_splitter=data_splitter,
        data_split=data_split,
        selected_cols=selected_cols,
        selected_cols_semantic_types=selected_cols_semantic_types,
        batch_transforms=batch_transforms,
        labels2id=labels2id,
        target=target,
    )
    return data_factory, dataset
