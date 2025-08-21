"""PyTorch implementations of the datafactory module contents."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from bitfount.backends.pytorch.data.dataloaders import (
    PyTorchIterableBitfountDataLoader,
    _BasePyTorchBitfountDataLoader,
)
from bitfount.backends.pytorch.data.datasets import (
    _PytorchFileIterableDataset,
    _PyTorchIterableDataset,
)
from bitfount.data.datafactory import _DataFactory
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.types import _JSONDict

if TYPE_CHECKING:
    from bitfount.data.datasets import _BaseBitfountDataset
    from bitfount.data.datasplitters import DatasetSplitter
    from bitfount.data.schema import BitfountSchema
    from bitfount.data.types import DataSplit, _SemanticTypeValue

_logger = logging.getLogger(__name__)


class _PyTorchDataFactory(_DataFactory):
    """A PyTorch-specific implementation of the DataFactory provider."""

    def create_dataloader(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> _BasePyTorchBitfountDataLoader:
        """See base class."""
        if isinstance(dataset, (_PyTorchIterableDataset, _PytorchFileIterableDataset)):
            _logger.debug("Creating PyTorchIterableBitfountDataLoader")
            return PyTorchIterableBitfountDataLoader(
                dataset=dataset, batch_size=batch_size, **kwargs
            )
        raise TypeError(
            "The _PyTorchDataFactory class only supports "
            "subclasses of PyTorch Dataset for creating a DataLoader."
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
    ) -> Union[_PyTorchIterableDataset, _PytorchFileIterableDataset]:
        """See base class."""
        if schema is None:
            raise ValueError("The schema must be provided to create a PyTorch dataset.")
        if isinstance(datasource, FileSystemIterableSource):
            _logger.debug(
                f"Datasource is a {FileSystemIterableSource.__name__},"
                f" creating a {_PytorchFileIterableDataset.__name__} dataset."
            )
            return _PytorchFileIterableDataset(
                schema=schema,
                selected_cols_semantic_types=selected_cols_semantic_types,
                data_splitter=data_splitter,
                datasource=datasource,
                target=target,
                selected_cols=selected_cols,
                selected_col_prefix=selected_col_prefix,
                image_cols_prefix=image_cols_prefix,
                batch_transforms=batch_transforms,
                data_split=data_split,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                image_prefix_batch_transforms=image_prefix_batch_transforms,
                **kwargs,
            )
        else:
            logging.debug(
                f"Datasource is iterable,"
                f" creating a {_PyTorchIterableDataset.__name__} dataset."
            )
            return _PyTorchIterableDataset(
                schema=schema,
                selected_cols_semantic_types=selected_cols_semantic_types,
                data_splitter=data_splitter,
                datasource=datasource,
                target=target,
                selected_cols=selected_cols,
                selected_col_prefix=selected_col_prefix,
                image_cols_prefix=image_cols_prefix,
                batch_transforms=batch_transforms,
                data_split=data_split,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                image_prefix_batch_transforms=image_prefix_batch_transforms,
                **kwargs,
            )
