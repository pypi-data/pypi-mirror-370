"""Defines abstract models, mixins, and other common backend-agnostic classes.

Implementations of these abstract models should be located in `bitfount.models.models`
or in the `models` subpackage of a backend.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from dataclasses import dataclass
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Optional, TypeVar, Union

import desert
from marshmallow import fields
import numpy as np

from bitfount import config
from bitfount.data.databunch import BitfountDataBunch
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import (
    DataStructure,
    registry as datastructure_registry,
)
from bitfount.data.schema import BitfountSchema
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    EvaluateReturnType,
    PredictReturnType,
    UsedForConfigSchemas,
    _BaseSerializableObjectMixIn,
    _StrAnyDict,
)
from bitfount.utils import seed_all

if TYPE_CHECKING:
    from bitfount.federated.helper import TaskContext
    from bitfount.metrics import Metric


logger = logging.getLogger(__name__)

# Main Model registry that is used to collect all model classes.
# Used for serialization and deserialization of model classes.
# Includes both abstract and non-abstract classes.
MAIN_MODEL_REGISTRY: _StrAnyDict = {}


@dataclass
class LoggerConfig(UsedForConfigSchemas):
    """Configuration for the logger.

    The configured logger will log training events, metrics, model checkpoints, etc. to
    your chosen platform. If no logger configuration is provided, the default logger is
    a Tensorboard logger.

    Args:
        name: The name of the logger. Should be one of the loggers supported by the
            chosen backend
        save_dir: The directory to save the logs.
            Defaults to `config.settings.paths.logs_dir`
        params: A dictionary of keyword arguments to pass to the logger. Defaults to an
            empty dictionary
    """

    #: same as argument
    name: str
    #: same as argument
    save_dir: Optional[Path] = desert.field(
        fields.Function(
            deserialize=lambda path: path if path is None else Path(path).expanduser()
        ),
        default=config.settings.paths.logs_dir,
    )
    #: same as argument
    params: Optional[_StrAnyDict] = desert.field(
        fields.Dict(keys=fields.Str), default_factory=dict
    )


ModelType = TypeVar("ModelType", bound="_BaseModel")


class _BaseModelRegistryMixIn:
    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if cls.__name__ not in MAIN_MODEL_REGISTRY:
            MAIN_MODEL_REGISTRY[cls.__name__] = cls


class _BaseModel(
    _BaseModelRegistryMixIn, _BaseSerializableObjectMixIn, ABC, Generic[ModelType]
):
    """Abstract Base Model from which all other models must inherit.

    This class is designed to be at the very bottom of the inheritance hierarchy.
    The only reason it has a `super().__init__()` call is to call the parent classes of
    other classes defined in other libraries. It also takes kwargs so that we do not
    throw an error if there are unexpected keyword arguments. These unexpected keyword
    arguments will end up in this constructor where they will simply be ignored.

    Args:
        datastructure: `DataStructure` to be passed to the model when initialised
        schema: The `BitfountSchema` object associated with the datasource
            on which the model will be trained on.
        seed: Random number seed. Used for setting random seed for all libraries.
            Defaults to None.
        param_clipping: Arguments for clipping for BatchNorm parameters.
            Used for federated models with secure aggregation.
            It should contain the SecureShare variables and the
            number of workers in a dictionary,
            e.g. `{"prime_q":13, "precision": 10**3,"num_workers":2}`.
            Defaults to None.

    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "seed": fields.Integer(allow_none=True),
        "schema": fields.Nested(BitfountSchema._Schema),
        "param_clipping": fields.Dict(
            keys=fields.String(), values=fields.Integer(), allow_none=True
        ),
    }
    # TODO: [BIT-1623] BitfountSchema here temporarily as a nested field,
    #  should be removed following the RFC
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"datastructure": datastructure_registry}

    def __init__(
        self,
        datastructure: DataStructure,
        schema: BitfountSchema,
        seed: Optional[int] = None,
        param_clipping: Optional[dict[str, int]] = None,
        **kwargs: Any,
    ):
        self.class_name = f"bitfount.{type(self).__name__}"
        self._context: Optional[TaskContext] = None
        self.metrics: Optional[MutableMapping[str, Metric]] = None
        self._model: Optional[ModelType] = None
        self._initialised: bool = False
        self.seed = seed
        self.param_clipping = param_clipping
        seed_all(self.seed)
        self.datastructure = datastructure
        self.databunch: BitfountDataBunch
        self.schema = schema
        self._objective: str

        # Placeholders for dataloaders
        self.train_dl: Optional[BitfountDataLoader] = None
        self.validation_dl: Optional[BitfountDataLoader] = None
        self.test_dl: Optional[BitfountDataLoader] = None

        for unexpected_kwarg in kwargs:
            logger.warning(f"Ignoring unexpected keyword argument {unexpected_kwarg}")

        super().__init__()

    def _set_dataloaders(
        self,
        batch_size: Optional[int] = None,
    ) -> None:
        """Sets train, validation and test dataloaders.

        Args:
            batch_size: The batch size to use for the dataloaders. Defaults to None.
        """
        if self.databunch is None:
            raise ValueError(
                "_set_dataloaders() requires the databunch to be set "
                "before being called."
            )

        if batch_size is None and hasattr(self, "batch_size"):
            batch_size = self.batch_size

        self.train_dl = self.databunch.get_train_dataloader(batch_size)
        self.validation_dl = self.databunch.get_validation_dataloader(batch_size)
        self.test_dl = self.databunch.get_test_dataloader(batch_size)

    @abstractmethod
    def initialise_model(
        self,
        data: Optional[BaseSource] = None,
        data_splitter: Optional[DatasetSplitter] = None,
        context: Optional[TaskContext] = None,
    ) -> None:
        """Can be implemented to initialise model if necessary.

        This is automatically called by the `fit()` method if necessary.

        Args:
            data: The data used for model training.
            data_splitter: The `DatasetSplitter` object used to split the data.
            context: Indicates if the model is running as a modeller or worker. If None,
                there is no difference between modeller and worker. Defaults to None.
        """
        raise NotImplementedError

    @property
    def initialised(self) -> bool:
        """Returns True if the model has been initialised, otherwise False.

        I.e. whether the `initialise_model` method has been called.
        """
        return self._initialised

    @abstractmethod
    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Implement this method to serialise a model."""
        raise NotImplementedError

    @abstractmethod
    def deserialize(
        self, content: Union[str, os.PathLike, bytes], **kwargs: Any
    ) -> None:
        """Implement this method to deserialise a model."""
        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        test_dl: Optional[BitfountDataLoader] = None,
        pod_identifiers: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Union[
        EvaluateReturnType,
        dict[str, float],
    ]:
        """Implement this method to perform inference on the test set.

        Args:
            test_dl: Optional `BitfountDataLoader` object containing test data. If this
                is not provided, the test set from the `BaseSource` used to train the
                model should be used if present.
            pod_identifiers: A list of pod identifiers to use for remote evaluation.
            **kwargs: Additional keyword arguments.

        Returns:
            A tuple of numpy arrays containing the predicted and actual values.
        """
        raise NotImplementedError

    @abstractmethod
    def predict(
        self,
        data: Optional[BaseSource] = None,
        pod_identifiers: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Union[
        PredictReturnType,
        dict[str, list[np.ndarray]],
    ]:
        """This method runs inference on the test data, returns predictions.

        Args:
            data: `BaseSource` object containing the data to run prediction on.
                Predictions will be generated for the test subset (as defined
                by the `DataSetSplitter`).
            pod_identifiers: A list of pod identifiers to use for remote prediction.
            **kwargs: Additional keyword arguments.

        Returns:
            A numpy array containing the prediction values.
        """
        raise NotImplementedError

    @abstractmethod
    def fit(
        self,
        data: Optional[BaseSource] = None,
        metrics: Optional[dict[str, Metric]] = None,
        pod_identifiers: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Optional[dict[str, str]]:
        """Must be implemented to fit the model.

        Must call `initialise_model()` within the method if the model needs to be
        initialised.

        Args:
            data: The data used for local model training.
            metrics: A dictionary of metrics to use for validation.
            pod_identifiers: A list of pod identifiers to use for federated training.
            **kwargs: Additional keyword arguments.

        """
        raise NotImplementedError


class ClassifierMixIn(_BaseModelRegistryMixIn, _BaseSerializableObjectMixIn):
    """MixIn for classification problems.

    Classification models must have this class in their inheritance hierarchy.

    Args:
        multilabel: Whether the problem is a multi-label problem. i.e. each datapoint
            belongs to multiple classes
        param_clipping: Arguments for clipping for BatchNorm parameters.
            Used for federated models with secure aggregation.
            It should contain the SecureShare variables and the
            number of workers in a dictionary,
            e.g. `{"prime_q":13, "precision": 10**3,"num_workers":2}`


    Attributes:
        multilabel: Whether the problem is a multi-label problem
        n_classes: Number of classes in the problem
    """

    #: set in _BaseModel
    datastructure: DataStructure
    #: set in _BaseModel
    schema: BitfountSchema
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "multilabel": fields.Bool(),
        "n_classes": fields.Int(),
        "param_clipping": fields.Dict(
            keys=fields.String(), values=fields.Integer(), allow_none=True
        ),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"datastructure": datastructure_registry}

    def __init__(
        self,
        multilabel: bool = False,
        param_clipping: Optional[dict[str, int]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.multilabel = multilabel
        self.param_clipping = param_clipping
        self.n_classes: int
        if "n_classes" in kwargs:
            self.n_classes = int(kwargs["n_classes"])
        self._objective = "classification"

    def set_number_of_classes(self, schema: BitfountSchema) -> None:
        """Sets the target number of classes for the classifier.

        If the data is a multi-label problem, the number of classes is set to the number
        of target columns as specified in the `DataStructure`. Otherwise, the number of
        classes is set to the number of unique values in the target column as specified
        in the `BitfountSchema`. The value is stored in the `n_classes` attribute.
        """
        if self.datastructure.target is None and hasattr(self, "n_classes"):
            logger.warning(
                "No target specified in data. Using explicitly provided n_classes."
                "Note that only inference results will be valid, not training "
                "or evaluation for this model and dataset."
            )
        elif self.datastructure.target is not None:
            # If the model is distributed, then we need to get the table name that
            # the Modeller has specified for this particular Pod.
            self.n_classes = (
                len(self.datastructure.target)
                if self.multilabel
                else schema.get_categorical_feature_size(self.datastructure.target)
            )
        else:
            raise ValueError(
                "No target specified in data, and number of classes not specified "
                "explicitly. Not able to determine dimensions of head of model."
            )


class RegressorMixIn(_BaseModelRegistryMixIn, _BaseSerializableObjectMixIn):
    """MixIn for regression problems.

    Currently, just used for tagging purposes.
    """

    pass
