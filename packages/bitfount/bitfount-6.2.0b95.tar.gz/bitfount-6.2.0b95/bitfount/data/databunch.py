"""Classes concerning databunches."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from bitfount.data.datafactory import _DataFactory, _get_default_data_factory
from bitfount.data.datasplitters import DatasetSplitter, _InferenceSplitter
from bitfount.data.types import DataSplit, SemanticType
from bitfount.utils import _add_this_to_list

if TYPE_CHECKING:
    from bitfount.data.dataloaders import BitfountDataLoader
    from bitfount.data.datasets import _BaseBitfountDataset
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.data.datastructure import DataStructure
    from bitfount.data.schema import BitfountSchema

logger = logging.getLogger(__name__)


class BitfountDataBunch:
    """Wrapper for train, validation and test dataloaders.

    Provides methods to access dataloaders for training and evaluation. This is strictly
    a model concept and is not necessary for algorithms that do not have models.

    Args:
        data_structure: A `DataStructure` object.
        schema: A `TableSchema` object.
        datasource: A `BaseSource` object.
        data_factory: A `_DataFactory` instance for creating datasets and dataloaders.
            Defaults to None.
    """

    def __init__(
        self,
        data_structure: DataStructure,
        schema: BitfountSchema,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        data_factory: Optional[_DataFactory] = None,
        ignore_support_cols: bool = False,
    ):
        self.data_structure = data_structure
        self.schema = schema
        self.datasource = datasource
        self.data_factory = (
            data_factory if data_factory is not None else _get_default_data_factory()
        )

        self.data_splitter = data_splitter
        self.ignore_support_cols = ignore_support_cols

        # Column attributes
        self.target = self.data_structure.target
        # Placeholders for generated datasets
        self._train_ds: Optional[_BaseBitfountDataset] = None
        self._validation_ds: Optional[_BaseBitfountDataset] = None
        self._test_ds: Optional[_BaseBitfountDataset] = None

        # Check datastructure schema requirements
        schema_reqs = "partial"
        if isinstance(self.data_structure.schema_requirements, dict):
            # By this point the schema requirements are a dictionary,
            # but wrapping in if statement for type checker
            for key, values in self.data_structure.schema_requirements.items():
                if type(self.datasource).__name__ in values and key == "full":
                    schema_reqs = "full"

        if not schema.features:
            if schema_reqs == "partial":
                # Call datasource yield_data once to populate schema features
                next(self.datasource.yield_data())
            elif schema_reqs == "full":
                schema.generate_full_schema(self.datasource)
        self.data_structure.set_training_column_split_by_semantic_type(self.schema)
        self._disallow_text_features()

        # TODO: [BIT-1167] This probably needs to be removed once we have implemented
        # dataset transformations. Currently, this call does nothing.
        self.datasource = self.data_structure.apply_dataset_transformations(
            self.datasource
        )

        self.selected_cols_prefix = self.data_structure.selected_cols_prefix
        self.image_cols_prefix = self.data_structure.image_prefix

        self._load_data()
        self._create_datasets()

    def _load_data(self) -> None:
        """Loads the data from the datasource and applies dataset transformations."""
        kwargs: dict = {}
        if isinstance(self.data_structure.table, str):
            kwargs["table_name"] = self.data_structure.table

    def _disallow_text_features(self) -> None:
        """Removes columns with semantic type TEXT from the data structure."""
        disallowed_columns = []
        for col in self.data_structure.selected_cols:
            if col in self.schema.get_feature_names(SemanticType.TEXT):
                disallowed_columns.append(col)
                logger.warning(
                    f"DataStructure has selected the text column {col} "
                    f"which is not supported. Removing this from the selection."
                )
        self.data_structure.ignore_cols = _add_this_to_list(
            disallowed_columns, self.data_structure.ignore_cols
        )
        self.data_structure.selected_cols = [
            i for i in self.data_structure.selected_cols if i not in disallowed_columns
        ]

    def _data_to_dataset(
        self,
        data_split: DataSplit,
    ) -> _BaseBitfountDataset:
        """Converts pandas dataframe to relevant BitfountDataset."""
        return self.data_factory.create_dataset(
            datasource=self.datasource,
            data_splitter=self.data_splitter,
            target=self.target,
            schema=self.schema,
            selected_cols_semantic_types=self.data_structure.selected_cols_w_types,
            selected_cols=self.data_structure.selected_cols,
            selected_col_prefix=self.selected_cols_prefix,
            image_cols_prefix=self.image_cols_prefix,
            batch_transforms=self.data_structure.batch_transforms,
            data_split=data_split,
            auto_convert_grayscale_images=self.data_structure.auto_convert_grayscale_images,
            ignore_support_cols=self.ignore_support_cols,
            image_prefix_batch_transforms=self.data_structure.image_prefix_batch_transforms,
        )

    def _create_datasets(self) -> None:
        """Creates datasets for dataloaders.

        Sets `self._train_ds`, `self._validation_ds` and `self._test_ds`.
        """
        if isinstance(self.data_splitter, _InferenceSplitter):
            logger.info("Using only the test set of the dataset for inference.")
            # If the data_splitter is an inference splitter, it will not have
            # the train/validation/test splits, so we just create a single dataset.
            self._train_ds = None
            self._validation_ds = None
            self._test_ds = self._data_to_dataset(DataSplit.TEST)
        else:
            self._train_ds = self._data_to_dataset(DataSplit.TRAIN)
            self._validation_ds = self._data_to_dataset(DataSplit.VALIDATION)
            self._test_ds = self._data_to_dataset(DataSplit.TEST)

    def get_train_dataloader(
        self, batch_size: Optional[int] = None, **kwargs: Any
    ) -> Optional[BitfountDataLoader]:
        """Gets the relevant data loader for training data."""
        if self._train_ds is None:
            logging.warning(
                "No training data in the dataset. Training DataLoader is 'None'."
            )
            return None
        elif len(self._train_ds) == 0:
            # TODO: [BIT-6159] Revisit this length check
            logger.warning(
                "Training dataset appears to be empty, length is 0;"
                " returning `None` instead"
            )
            return None
        return self.data_factory.create_dataloader(
            self._train_ds, batch_size=batch_size, **kwargs
        )

    def get_validation_dataloader(
        self, batch_size: Optional[int] = None, **kwargs: Any
    ) -> Optional[BitfountDataLoader]:
        """Gets the relevant data loader for validation data."""
        if self._validation_ds is None:
            logging.warning(
                "No validation data in the dataset. Validation DataLoader is 'None'."
            )
            return None
        elif len(self._validation_ds) == 0:
            # TODO: [BIT-6159] Revisit this length check
            logger.warning(
                "Validation dataset appears to be empty, length is 0;"
                " returning `None` instead"
            )
            return None
        return self.data_factory.create_dataloader(
            self._validation_ds, batch_size=batch_size, **kwargs
        )

    def get_test_dataloader(
        self, batch_size: Optional[int] = None, **kwargs: Any
    ) -> Optional[BitfountDataLoader]:
        """Gets the relevant data loader for test data."""
        if self._test_ds is None:
            logging.warning("No test data in the dataset. Test DataLoader is `None`.")
            return None
        elif isinstance(self.data_splitter, _InferenceSplitter):
            # If it got here with this datasplitter it has
            # passed the initial worker data check, so the
            # test_ds should be non-empty.
            return self.data_factory.create_dataloader(
                self._test_ds, batch_size=batch_size, **kwargs
            )
        elif len(self._test_ds) == 0:
            # TODO: [BIT-6159] Revisit this length check
            logger.warning(
                "Test dataset appears to be empty, length is 0;"
                " returning `None` instead"
            )
            return None
        return self.data_factory.create_dataloader(
            self._test_ds, batch_size=batch_size, **kwargs
        )
