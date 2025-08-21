"""MixIn classes for compatible models with the federated algorithms."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, MutableMapping, Sequence
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, Optional, Union, cast

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
import numpy as np
import pandas as pd

from bitfount import config
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.federated.aggregators.base import _BaseAggregatorFactory
from bitfount.federated.algorithms.model_algorithms.evaluate import ModelEvaluation
from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
)
from bitfount.federated.algorithms.model_algorithms.inference import ModelInference
from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.helper import (
    _check_and_update_pod_ids,
    _create_aggregator,
    _create_message_service,
    _get_idp_url,
)
from bitfount.federated.modeller import _Modeller
from bitfount.federated.protocols.model_protocols.federated_averaging import (
    FederatedAveraging,
)
from bitfount.federated.protocols.results_only import (
    ResultsOnly,
    _ResultsOnlyCompatibleNonModelAlgoFactory,
)
from bitfount.federated.transport.message_service import _MessageService
from bitfount.hub.helper import _create_bitfounthub

if TYPE_CHECKING:
    from bitfount.data.datastructure import DataStructure
    from bitfount.federated.transport.config import MessageServiceConfig
    from bitfount.hub.api import BitfountHub
    from bitfount.metrics import Metric
    from bitfount.types import (
        EvaluateReturnType,
        PredictReturnType,
        _DistributedModelTypeOrReference,
        _Residuals,
        _SerializedWeights,
        _Weights,
    )

from bitfount.federated.logging import _get_federated_logger
from bitfount.types import T_DTYPE

logger = _get_federated_logger(__name__)


class _DistributedModelMixIn(ABC, Generic[T_DTYPE]):
    """A mixin for models used in federated mechanisms.

    An abstract base mixin for models that are compatible with the following
    distributed learning protocols:
        - FederatedAveraging
    """

    datastructure: DataStructure
    # Set on the BaseModel
    epochs: Optional[int] = None
    steps: Optional[int] = None
    # Used to identify the relevant section of the datastructure that applies to
    # the pod/logical pod/datasource that this model is being run against (if any)
    _datastructure_identifier: Optional[str] = None

    @abstractmethod
    def get_param_states(self) -> _Weights:
        """Gets the current states of the trainable parameters of the model.

        Returns:
            A dict of param names to tensors
        """
        raise NotImplementedError

    @abstractmethod
    def apply_weight_updates(self, weight_updates: Sequence[_Residuals]) -> _Weights:
        """Applies weight updates to the weights of this model.

        Apply a sequence of parameter weight updates (mappings of parameter name
        to a tensor describing the weight update) to the parameters of this model.
        Used by Modeller to apply updates received from Workers.

        Args:
            weight_updates (Sequence[_Residuals]): The sequence
                of weight updates

        Returns:
            The updated parameters as a dict of name to tensor.
        """
        raise NotImplementedError

    @abstractmethod
    def update_params(self, new_model_params: _Weights) -> None:
        """Updates the current model parameters to the ones provided.

        Used by Worker to update new parameters received from Modeller.

        Args:
            new_model_params (WeightMapping): The new model parameters
                to update to as a mapping of parameter names to tensors.
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize_params(self, serialized_weights: _SerializedWeights) -> _Weights:
        """Converts serialized model parameters to tensors.

        Used by Worker to convert serialized parameters received from Modeller.

        Args:
            serialized_weights (_SerializedWeights): The model parameters
                to deserialize.
        """
        raise NotImplementedError

    @abstractmethod
    def serialize_params(self, weights: _Weights) -> _SerializedWeights:
        """Serializes model parameters.

        Used by Modeller to serialize model parameters to send to the Worker.

        Args:
            weights (_Weights): The model parameters
                to serialize.
        """
        raise NotImplementedError

    @abstractmethod
    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Serialize model to file with provided `filename`.

        Args:
           filename: Path to file to save serialized model.
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize(
        self, content: Union[str, os.PathLike, bytes], **kwargs: Any
    ) -> None:
        """Deserialize model.

        Args:
            content: Byte stream or path to file containing serialized model.
            kwargs: Additional keyword arguments for deserialization methods.
        """
        raise NotImplementedError

    @abstractmethod
    def diff_params(self, old_params: _Weights, new_params: _Weights) -> _Residuals:
        """Calculates the difference between two sets of model parameters."""
        raise NotImplementedError

    @abstractmethod
    def set_model_training_iterations(self, iterations: int) -> None:
        """Sets model steps or epochs to the appropriate number between updates."""
        raise NotImplementedError

    @abstractmethod
    def reset_trainer(self) -> None:
        """Resets the trainer to its initial state.

        :::note

        Importantly, calling this method in between `fit` calls allows the caller to
        repeatedly refit the model continuing from the batch after the one that was last
        fit. This only applies to step-wise training.

        :::
        """
        raise NotImplementedError

    @abstractmethod
    def log_(self, name: str, value: Any, **kwargs: Any) -> Any:
        """Logs a metric with a particular value to the user's configured model loggers.

        Args:
            name: The name of the metric to log
            value: The value of the metric to log
            **kwargs: Additional keyword arguments to pass to the logger
        """
        raise NotImplementedError

    @abstractmethod
    def tensor_precision(self) -> T_DTYPE:
        """Gets the floating point precision used by model tensors.

        Typically this will be 32 bits.
        """
        raise NotImplementedError

    @abstractmethod
    def _fit_local(
        self,
        data: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        metrics: Optional[MutableMapping[str, Metric]] = None,
        **kwargs: Any,
    ) -> dict[str, str]:
        """Fits model locally using data from `datasource`.

        Should be implemented in the final model class that subclasses
        DistributedModelMixIn.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_model(
        self,
        extra_imports: Optional[list[str]] = None,
        hub: Optional[BitfountHub] = None,
        **kwargs: Any,
    ) -> _DistributedModelTypeOrReference:
        """Gets the model to be used in distributed training.

        This method is used by the Modeller to get the model to be used in
        distributed training.

        Args:
            extra_imports: A list of extra imports to add to the model file if the model
                is a custom model.
            hub: A BitfountHub instance to be passed to `BitfountModelReference`.
                Optional.
            **kwargs: Additional keyword arguments to pass to the
                `BitfountModelReference` constructor as hyperparameters.

        Returns:
            Either a `BitfountModelReference` object if the model is a custom model, or
            the model itself if it is a built-in model.
        """
        raise NotImplementedError

    def set_datastructure_identifier(self, datastructure_identifier: str) -> None:
        """Sets the datastructure identifier for the model.

        This is used to identify which elements of the datastructure are referring
        to the current runner and is normally the pod identifier (for single
        datasource pods) or the "logical pod" identifier for pods with multiple
        datasources that have registered as different pods.

        This must be called on the Pod/Worker side in Distributed training because it
        is needed for the model to be able to extract the relevant information from the
        datastructure sent by the Modeller.

        Args:
            datastructure_identifier: The datastructure identifier for the model.
        """
        self._datastructure_identifier = datastructure_identifier

    def _fit_federated(
        self,
        pod_identifiers: list[str],
        username: Optional[str] = None,
        aggregator: Optional[_BaseAggregatorFactory] = None,
        steps_between_parameter_updates: Optional[int] = None,
        epochs_between_parameter_updates: Optional[int] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        secure_aggregation: bool = False,
        auto_eval: bool = True,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: E501
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
        model_out: Optional[Union[Path, str]] = None,
        require_all_pods: bool = False,
        extra_imports: Optional[list[str]] = None,
        modeller_checkpointing: bool = True,
        checkpoint_filename: Optional[str] = None,
        project_id: Optional[str] = None,
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        **kwargs: Any,
    ) -> Optional[dict[str, str]]:
        """Fits model federated-ly."""
        if not bitfounthub:
            bitfounthub = _create_bitfounthub(username=username)
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        if run_on_new_data_only:
            logger.warning(
                "Running on new data only is only supported for predict method. "
                "Resuming task on the entire datasource."
            )
            run_on_new_data_only = False
        if batched_execution:
            logger.warning(
                "Batched execution is only supported for prediction and evaluation. "
                "Resuming task without batched execution."
            )
            batched_execution = False

        model = self._get_model(extra_imports=extra_imports, hub=bitfounthub, **kwargs)
        algorithm = FederatedModelTraining(
            model=model,
            pretrained_file=pretrained_file,
            modeller_checkpointing=modeller_checkpointing,
            checkpoint_filename=checkpoint_filename,
            project_id=project_id,
        )

        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)
        if (
            len(pod_identifiers) > 1
            and hasattr(self.datastructure, "table")
            and isinstance(self.datastructure.table, str)
        ):
            raise ValueError(
                "You are attempting to train on multiple pods, but the "
                "provided DataStructure table name is a string. "
                "Please make sure that the `table` argument to the "
                "`DataStructure` is a mapping of Pod names to table names. "
            )
        if not message_service:
            message_service = _create_message_service(bitfounthub.session, ms_config)

        if not aggregator:
            aggregator = _create_aggregator(secure_aggregation=secure_aggregation)

        if not idp_url:
            idp_url = _get_idp_url()

        # TODO: [BIT-1098] Manage pods with different schemas
        protocol = FederatedAveraging(
            algorithm=algorithm,
            aggregator=aggregator,
            steps_between_parameter_updates=steps_between_parameter_updates,
            epochs_between_parameter_updates=epochs_between_parameter_updates,
            auto_eval=auto_eval,
        )

        modeller = _Modeller(
            protocol=protocol,
            message_service=message_service,
            bitfounthub=bitfounthub,
            pod_public_key_paths=pod_public_key_paths,
            identity_verification_method=identity_verification_method,
            private_key=private_key_or_file,
            idp_url=idp_url,
        )
        # Run task
        result = modeller.run(
            pod_identifiers,
            require_all_pods=require_all_pods,
            model_out=model_out,
            run_on_new_data_only=run_on_new_data_only,
            batched_execution=batched_execution,
            project_id=project_id,
        )

        if result is False:
            return None
        else:
            return result

    def fit(
        self,
        data: Optional[BaseSource] = None,
        metrics: Optional[dict[str, Metric]] = None,
        pod_identifiers: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Optional[dict[str, str]]:
        """Fits model either locally or federated-ly.

        `pod_identifiers` must be provided for federated training.

        :::caution

        For remote training, this method does not use the existing parameters of the
        model unless they are serialized and provided using the `pretrained_file`
        keyword argument.

        :::

        Args:
            data: Datasource for training. Defaults to None.
            metrics: Metrics to calculate for validation. Defaults to None.
            pod_identifiers: list of pod identifiers. If this is provided, the model
                will be trained in a federated manner. Defaults to None.
            **kwargs: Optional keyword arguments passed to the federated fit method.
                Any unrecognized keyword arguments will be interpreted as
                custom model hyperparameters.

        Returns:
            A dictionary of metrics and their values. Optional.

        Raises:
            ValueError: If neither `pod_identifiers` are provided for federated training
                nor `data` is provided for local training.
        """
        if pod_identifiers is not None:
            logger.info(f"Training federated with pods: {', '.join(pod_identifiers)}.")
            return self._fit_federated(pod_identifiers=pod_identifiers, **kwargs)
        elif data is not None:
            logger.info("Training locally using provided datasource.")
            return self._fit_local(data=data, metrics=metrics)

        raise ValueError(
            "Please provide either pod identifiers or a datasource for model training."
        )

    def evaluate(
        self,
        test_dl: Optional[BitfountDataLoader] = None,
        pod_identifiers: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Union[
        EvaluateReturnType,
        dict[str, float],
    ]:
        """Evaluates model either locally or federated-ly.

        `pod_identifiers` must be provided for federated evaluation.

        :::caution

        For remote evaluation, this method does not use the existing parameters of the
        model unless they are serialized and provided using the `pretrained_file`
        keyword argument.

        :::

        Args:
            test_dl: Optional dataloader to run inference on which takes precedence over
                the dataloader returned by `self.test_dataloader`.
            pod_identifiers: list of pod identifiers. If this is provided, the model
                will be evaluated in a federated manner. Defaults to None.
            **kwargs: Optional keyword arguments passed to the federated evaluate
                method.

        Returns:
            Either:
                - A tuple of numpy arrays containing the predicted and actual values if
                evaluated locally.
                - A dictionary of metrics if evaluated remotely.
        """
        if pod_identifiers is not None:
            logger.info(f"Evaluating model on pods: {', '.join(pod_identifiers)}.")
            return self._evaluate_federated(pod_identifiers=pod_identifiers, **kwargs)

        logger.info("Evaluating model locally")
        return self._evaluate_local(test_dl=test_dl)

    def _evaluate_local(
        self, test_dl: Optional[BitfountDataLoader] = None, **kwargs: Any
    ) -> EvaluateReturnType:
        """This method runs inference on the test dataloader.

        Args:
            test_dl: Optional dataloader to run inference on which takes precedence over
                the dataloader returned by `self.test_dataloader`.
            **kwargs: Additional keyword arguments to pass to the evaluate method.

        Returns:
            A tuple of predictions and targets as numpy arrays.
        """
        raise NotImplementedError

    def _evaluate_federated(
        self,
        pod_identifiers: list[str],
        username: Optional[str] = None,
        aggregator: Optional[_BaseAggregatorFactory] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        secure_aggregation: bool = False,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: E501
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
        model_out: Optional[Union[Path, str]] = None,
        require_all_pods: bool = False,
        extra_imports: Optional[list[str]] = None,
        project_id: Optional[str] = None,
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        **kwargs: Any,
    ) -> dict[str, float]:
        """Evaluates model remotely on all the specified pods separately.

        Returns:
            A dictionary of metrics.
        """
        if not bitfounthub:
            bitfounthub = _create_bitfounthub(username=username)
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        if run_on_new_data_only:
            logger.warning(
                "Running on new data only is only supported for predict method. "
                "Resuming task on the entire datasource."
            )
            run_on_new_data_only = False
        if len(pod_identifiers) > 1 and batched_execution:
            logger.warning(
                "Batched execution is only supported for single pod evaluation. "
                "Resuming task without batched execution."
            )
            batched_execution = False
        model = self._get_model(extra_imports=extra_imports, hub=bitfounthub, **kwargs)
        algorithm = ModelEvaluation(
            model=model, pretrained_file=pretrained_file, project_id=project_id
        )

        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)
        if (
            len(pod_identifiers) > 1
            and hasattr(self.datastructure, "table")
            and isinstance(self.datastructure.table, str)
        ):
            raise ValueError(
                "You are attempting to evaluate on multiple pods, but the "
                "provided DataStructure table name is a string. "
                "Please make sure that the `table` argument to the "
                "`DataStructure` is a mapping of Pod names to table names. "
            )
        if not message_service:
            message_service = _create_message_service(bitfounthub.session, ms_config)

        if not idp_url:
            idp_url = _get_idp_url()

        protocol = ResultsOnly(
            algorithm=algorithm,
            aggregator=aggregator,
            secure_aggregation=secure_aggregation,
        )

        modeller = _Modeller(
            protocol=protocol,
            message_service=message_service,
            bitfounthub=bitfounthub,
            pod_public_key_paths=pod_public_key_paths,
            identity_verification_method=identity_verification_method,
            private_key=private_key_or_file,
            idp_url=idp_url,
        )

        metrics = modeller.run(
            pod_identifiers,
            require_all_pods=require_all_pods,
            model_out=model_out,
            project_id=project_id,
            batched_execution=batched_execution,
            run_on_new_data_only=run_on_new_data_only,
        )
        return cast(dict[str, float], metrics)

    def predict(
        self,
        data: Optional[BaseSource] = None,
        pod_identifiers: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Union[
        PredictReturnType,
        dict[str, list[np.ndarray]],
    ]:
        """Infers model either locally or federated-ly.

        `pod_identifiers` must be provided for federated inference.

        :::caution

        For remote inference, this method does not use the existing parameters of the
        model unless they are serialized and provided using the `pretrained_file`
        keyword argument.

        :::

        Args:
            data: Optional datasource to run inference on if training locally. Defaults
                to None.
            pod_identifiers: list of pod identifiers. If this is provided, the model
                will be inferred in a federated manner. Defaults to None.
            **kwargs: Optional keyword arguments passed to the federated predict
                method.

        Returns:
            Either:
                - A numpy array containing the predicted values if
                inferred locally.
                - A dictionary of numpy arrays if inferred remotely.
        """
        # Prediction only happens on one epoch, and not dependent
        # on the number of steps. To ensure that the tasks are
        # mapped to the same task hash in the database, we modify
        # the hyperparmeters here, since it does not
        if self.epochs:
            self.epochs = 1
        else:
            self.steps = 1
        if data and pod_identifiers:
            raise ValueError(
                "Only one of 'data' and 'pod_identifiers' can be provided. "
                "Received both."
            )
        elif pod_identifiers:
            logger.info(f"Inferring model on pods: {', '.join(pod_identifiers)}.")
            return self._predict_federated(pod_identifiers=pod_identifiers, **kwargs)
        elif data:
            logger.info("Inferring model locally")
            return self._predict_local(data)

        raise ValueError(
            "One of 'data' or 'pod_identifiers' must be provided. Received neither."
        )

    def _predict_local(self, data: BaseSource, **kwargs: Any) -> PredictReturnType:
        """This method runs inference on the datasource.

        Args:
            data: DataSource to run inference on.
            **kwargs: Additional keyword arguments to pass to the predict method.

        Returns:
            Predictions (or whatever the model outputs) as a numpy array.
        """
        raise NotImplementedError

    def _predict_federated(
        self,
        pod_identifiers: list[str],
        username: Optional[str] = None,
        aggregator: Optional[_BaseAggregatorFactory] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        secure_aggregation: bool = False,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: E501
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
        model_out: Optional[Union[Path, str]] = None,
        require_all_pods: bool = False,
        extra_imports: Optional[list[str]] = None,
        project_id: Optional[str] = None,
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        **kwargs: Any,
    ) -> dict[str, list[np.ndarray]]:
        """Infers the model remotely on all the specified pods separately.

        Returns:
            A dictionary of predictions.
        """
        if not bitfounthub:
            bitfounthub = _create_bitfounthub(username=username)
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        if len(pod_identifiers) > 1 and batched_execution:
            logger.warning(
                "Batched execution is only supported for single pod prediction. "
                "Resuming task without batched execution."
            )
            batched_execution = False

        model = self._get_model(extra_imports=extra_imports, hub=bitfounthub, **kwargs)
        algorithm = ModelInference(
            model=model, pretrained_file=pretrained_file, project_id=project_id
        )

        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)
        if (
            len(pod_identifiers) > 1
            and hasattr(self.datastructure, "table")
            and isinstance(self.datastructure.table, str)
        ):
            raise ValueError(
                "You are attempting to infer on multiple pods, but the "
                "provided DataStructure table name is a string. "
                "Please make sure that the `table` argument to the "
                "`DataStructure` is a mapping of Pod names to table names. "
            )
        if not message_service:
            message_service = _create_message_service(bitfounthub.session, ms_config)

        if not idp_url:
            idp_url = _get_idp_url()

        protocol = ResultsOnly(
            algorithm=algorithm,
            aggregator=aggregator,
            secure_aggregation=secure_aggregation,
        )

        modeller = _Modeller(
            protocol=protocol,
            message_service=message_service,
            bitfounthub=bitfounthub,
            pod_public_key_paths=pod_public_key_paths,
            identity_verification_method=identity_verification_method,
            private_key=private_key_or_file,
            idp_url=idp_url,
        )

        predictions = modeller.run(
            pod_identifiers,
            require_all_pods=require_all_pods,
            model_out=model_out,
            project_id=project_id,
            run_on_new_data_only=run_on_new_data_only,
            batched_execution=batched_execution,
        )
        return cast(dict[str, list[np.ndarray]], predictions)


class _ModellessAlgorithmMixIn(ABC):
    """A mixin for SQL Algorithms.

    An abstract base mixin for SQL algorithms that are compatible with the
    ResultsOnly protocol.
    """

    def execute(
        self,
        pod_identifiers: list[str],
        username: Optional[str] = None,
        bitfounthub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: E501
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
        require_all_pods: bool = False,
        aggregator: Optional[_BaseAggregatorFactory] = None,
        project_id: Optional[str] = None,
    ) -> list[pd.DataFrame]:
        """Execute ResultsOnly compatible algorithm.

        Syntactic sugar to allow the modeller to call `.execute(...)` on
        ResultsOnly compatible algorithms.
        """
        if not bitfounthub:
            bitfounthub = _create_bitfounthub(username=username)

        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfounthub)

        if not message_service:
            message_service = _create_message_service(bitfounthub.session, ms_config)

        if not idp_url:
            idp_url = _get_idp_url()

        protocol = ResultsOnly(
            algorithm=cast(_ResultsOnlyCompatibleNonModelAlgoFactory, self),
            aggregator=aggregator,
        )
        modeller = _Modeller(
            protocol=protocol,
            message_service=message_service,
            bitfounthub=bitfounthub,
            pod_public_key_paths=pod_public_key_paths,
            identity_verification_method=identity_verification_method,
            private_key=private_key_or_file,
            idp_url=idp_url,
        )

        result = cast(
            list[pd.DataFrame],
            modeller.run(
                pod_identifiers=pod_identifiers,
                require_all_pods=require_all_pods,
                project_id=project_id,
            ),
        )
        return result
