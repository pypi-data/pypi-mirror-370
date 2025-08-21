"""Data factory classes.

Factory design patterns for producing datasets and dataloaders.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Optional, Union

from bitfount.config import _BASIC_ENGINE, _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasets import (
    _BaseBitfountDataset,
    _BitfountDataset,
    _FileSystemIterableBitfountDataset,
)
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.exceptions import BitfountEngineError
from bitfount.types import _JSONDict

if TYPE_CHECKING:
    from bitfount.data.datasplitters import DatasetSplitter
    from bitfount.data.schema import BitfountSchema
    from bitfount.data.types import DataSplit, _SemanticTypeValue


class _DataFactory(ABC):
    """A factory for producing dataset and dataloader instances."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: B027
        pass

    @abstractmethod
    def create_dataloader(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> BitfountDataLoader:
        """Creates a dataloader as specified by this factory.

        Args:
            dataset: The dataset that should be loaded.
            batch_size: The batch size that the dataloader should output.
            **kwargs: Keyword arguments to be passed to the underlying function if
                relevant.

        Returns:
            A BitfountDataLoader instance.
        """
        raise NotImplementedError

    @abstractmethod
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
    ) -> _BaseBitfountDataset:
        """Creates a dataset for prediction tasks.

        Args:
            datasource: The data to wrap in a dataset.
            data_splitter: The data splitter to use, as specified by the Modeller.
            data_split: Which data split of the datasource to use and the step for which
                batch transformations should be applied.
            schema: The schema of the datasource.
            selected_cols: The columns selected by the data structure.
            selected_cols_semantic_types: A mapping of semantic types and column names.
            selected_col_prefix: The prefix to use for selected columns.
            image_cols_prefix: The prefix to use for image columns.
            target: The dependent variable name.
            batch_transforms: A mapping of column names to transformations to
                be applied at batch time. E.g:
                [{
                    "image":
                        {"albumentations":
                            {"step": "test",
                            "output": "true",
                            "ToTensorV2"
                            }
                        }
                }]
            auto_convert_grayscale_images: Whether or not to automatically convert
                grayscale images to RGB. Defaults to True.
            image_prefix_batch_transforms: A list of  batch transform to apply to the
                columns defined by the image prefix. E.g.:
                [
                    {"albumentations":
                        {"step": "test",  "output": "true", "ToTensorV2"}},
                    {"albumentations":
                        {"step": "test", "output": "true", "Normalize"}
                    ]
            **kwargs: Any
        """
        raise NotImplementedError


class _BasicDataFactory(_DataFactory):
    """A basic DataFactory implementation using core dataset and dataloaders."""

    def create_dataloader(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> BitfountDataLoader:
        """See base class."""
        return BitfountDataLoader(dataset, batch_size)

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
    ) -> _BaseBitfountDataset:
        """See base class."""
        if schema is None:
            raise ValueError(
                "The schema must be provided to create a Bitfount dataset."
            )
        if isinstance(datasource, FileSystemIterableSource):
            return _FileSystemIterableBitfountDataset(
                datasource=datasource,
                schema=schema,
                data_splitter=data_splitter,
                data_split=data_split,
                target=target,
                selected_cols=selected_cols,
                selected_cols_semantic_types=selected_cols_semantic_types,
                selected_col_prefix=selected_col_prefix,
                image_cols_prefix=image_cols_prefix,
                batch_transforms=batch_transforms,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                image_prefix_batch_transforms=image_prefix_batch_transforms,
                **kwargs,
            )

        else:
            return _BitfountDataset(
                datasource=datasource,
                schema=schema,
                data_splitter=data_splitter,
                data_split=data_split,
                target=target,
                selected_cols=selected_cols,
                selected_cols_semantic_types=selected_cols_semantic_types,
                selected_col_prefix=selected_col_prefix,
                image_cols_prefix=image_cols_prefix,
                batch_transforms=batch_transforms,
                auto_convert_grayscale_images=auto_convert_grayscale_images,
                image_prefix_batch_transforms=image_prefix_batch_transforms,
                **kwargs,
            )


def _get_default_data_factory(*args: Any, **kwargs: Any) -> _DataFactory:
    """Create a DataFactory instance as specified by the backend engine.

    Args:
        *args: positional arguments, passed to the DataFactory constructor.
        **kwargs: keyword arguments, passed to the DataFactory constructor.

    Returns:
        The created DataFactory instance.

    Raises:
        BitfountEngineError: if there is an import issue in loading the backend.
    """
    if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
        try:
            from bitfount.backends.pytorch.data.datafactory import _PyTorchDataFactory

            return _PyTorchDataFactory(*args, **kwargs)
        except ImportError as e:
            raise BitfountEngineError(
                "An error was encountered trying to load the pytorch engine; "
                "check pytorch is installed."
            ) from e
    elif BITFOUNT_ENGINE == _BASIC_ENGINE:
        return _BasicDataFactory(*args, **kwargs)
    else:
        raise BitfountEngineError(f"Unable to load engine {BITFOUNT_ENGINE}.")
