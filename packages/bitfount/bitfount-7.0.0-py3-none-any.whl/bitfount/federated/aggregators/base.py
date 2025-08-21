"""Base Aggregator classes.

Attributes:
    registry: A read-only dictionary of aggregator factory names to their implementation
        classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, Mapping as _RunTimeCheckableMapping
from enum import Enum, auto
import inspect
from types import MappingProxyType
from typing import Any, ClassVar, Generic, Optional, Union, overload

import numpy as np
import pandas as pd

from bitfount.federated.exceptions import AggregatorError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.roles import _RolesMixIn
from bitfount.federated.shim import _load_default_tensor_shim
from bitfount.federated.types import AggregatorType
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _SerializedWeights,
    _Weights,
)

logger = _get_federated_logger(__name__)


class AggregationType(Enum):
    """Supported types for the aggregator."""

    TENSOR_DICT = auto()
    PANDAS_DATAFRAME = auto()
    NUMPY_ARRAY = auto()

    UNSUPPORTED = auto()


class _BaseAggregator(ABC):
    """Base Aggregator from which all other aggregators must inherit."""

    def __init__(self, **kwargs: Any):
        self._tensor_shim = _load_default_tensor_shim()
        # Dictionary of non numeric columns to values
        self.non_numeric_columns: dict[str, np.ndarray] = {}

    @staticmethod
    def _get_type(obj: Iterable[Any]) -> AggregationType:
        """Determine the type of the supplied objects from the workers.

        :::note

        This is used to determine whether the object is a tensor, pandas dataframe or
        numpy array.

        :::
        """
        obj_iter = iter(obj)
        first = next(obj_iter)
        obj_type = type(first)

        # Check that these are the same in all others
        for other in obj_iter:
            if obj_type is not type(other):
                raise AggregatorError(
                    f"Algorithm outputs are not consistent between workers: "
                    f"all types should match {obj_type}"
                )

        if obj_type == np.ndarray:
            logger.debug("Numpy array detected for aggregation.")
            return AggregationType.NUMPY_ARRAY
        elif obj_type == pd.DataFrame:
            logger.debug("Pandas dataframe detected for aggregation.")
            return AggregationType.PANDAS_DATAFRAME
        elif isinstance(first, _RunTimeCheckableMapping):
            logger.debug("Tensor-like object detected for aggregation.")
            return AggregationType.TENSOR_DICT

        return AggregationType.UNSUPPORTED

    def _set_non_numeric_columns(
        self, algorithm_outputs: Iterable[pd.DataFrame]
    ) -> None:
        """Extracts the non-numeric columns for an iterable of DataFrames.

        Raises:
            AggregatorError: If the non-numeric columns are not the same for all
                dataframes.
        """
        for output in algorithm_outputs:
            output_dict: dict[str, np.ndarray] = {
                col: output[col].to_numpy() for col in output.columns
            }
            for col, values in output_dict.items():
                if (
                    col in self.non_numeric_columns
                    and (self.non_numeric_columns[col] != values).any()
                ):
                    raise AggregatorError(
                        f"Non-numeric columns must be the same. "
                        f"Column {col} has different values between workers."
                    )
                elif not np.issubdtype(values.dtype, np.number):
                    self.non_numeric_columns[col] = values


class _BaseModellerAggregator(_BaseAggregator, Generic[T_DTYPE], ABC):
    """Base modeller-side aggregator."""

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, _SerializedWeights],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> _Weights:
        """Averages tensor dictionaries and returns the average."""
        ...

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, pd.DataFrame],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Averages pandas dataframes and returns the average."""
        ...

    @overload
    def run(
        self,
        algorithm_outputs: Mapping[str, np.ndarray],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """Averages numpy arrays and returns the average."""
        ...

    @abstractmethod
    def run(
        self,
        algorithm_outputs: Union[
            Mapping[str, _SerializedWeights],
            Mapping[str, np.ndarray],
            Mapping[str, pd.DataFrame],
        ],
        tensor_dtype: Optional[T_DTYPE] = None,
        **kwargs: Any,
    ) -> Union[_Weights, pd.DataFrame, np.ndarray]:
        """Averages algorithm outputs and returns the average."""


class _BaseWorkerAggregator(_BaseAggregator, ABC):
    """Base worker-side aggregator."""

    @overload
    async def run(
        self, algorithm_output: _Weights, **kwargs: Any
    ) -> _SerializedWeights:
        """Converts tensors to list of floats and returns them."""
        ...

    @overload
    async def run(self, algorithm_output: np.ndarray, **kwargs: Any) -> np.ndarray:
        """Doesn't do anything - leaves the type as it is."""
        ...

    @overload
    async def run(self, algorithm_output: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Doesn't do anything - leaves the type as it is."""
        ...

    @abstractmethod
    async def run(
        self, algorithm_output: Union[_Weights, np.ndarray, pd.DataFrame], **kwargs: Any
    ) -> Union[_SerializedWeights, np.ndarray, pd.DataFrame]:
        """Runs the worker-side aggregator."""


# The mutable underlying dict that holds the registry information
_registry: dict[str, type[_BaseAggregatorFactory]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, type[_BaseAggregatorFactory]] = MappingProxyType(_registry)


class _AggregatorWorkerFactory(ABC):
    """Defines the base worker() factory method for aggregation."""

    @abstractmethod
    def worker(self, **kwargs: Any) -> _BaseWorkerAggregator:
        """Return worker side of the Aggregator."""
        pass


class _BaseAggregatorFactory(ABC, _BaseSerializableObjectMixIn, _RolesMixIn):
    """Base aggregator factory from which all others should inherit.

    Attributes:
        class_names: The name of the aggregator class.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(self, **kwargs: Any) -> None:
        self.class_name = AggregatorType[type(self).__name__].value

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to Aggregator registry")
            _registry[cls.__name__] = cls
        else:
            # Add abstract classes to the registry (so they can be correctly used for
            # serialization field inheritance) but ensure they are stored differently
            # so they cannot be accidentally looked up by name
            abstract_cls_name = f"Abstract::{cls.__name__}"
            logger.debug(
                f"Adding abstract class {cls.__name__}: {cls} to Aggregator registry"
                f" as {abstract_cls_name}"
            )
            _registry[abstract_cls_name] = cls

    @abstractmethod
    def modeller(self, **kwargs: Any) -> _BaseModellerAggregator:
        """Return modeller side of the Aggregator."""
        raise NotImplementedError
