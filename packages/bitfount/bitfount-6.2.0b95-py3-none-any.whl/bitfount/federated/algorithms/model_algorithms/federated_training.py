"""Algorithm to train a model remotely and return its parameters."""

from __future__ import annotations

from collections.abc import Mapping
import os
from typing import TYPE_CHECKING, Any, ClassVar, Optional

from bitfount import config
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithm,
    _BaseModelAlgorithmFactory,
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.authorisation_checkers import ModelURLs, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.hub.api import BitfountHub
from bitfount.models.base_models import MAIN_MODEL_REGISTRY
from bitfount.types import (
    T_NESTED_FIELDS,
    DistributedModelProtocol,
    _Residuals,
    _SerializedWeights,
    _Weights,
)
from bitfount.utils import delegates

if TYPE_CHECKING:
    from bitfount.types import _DistributedModelTypeOrReference

logger = _get_federated_logger(__name__)


class _BaseModelTrainingMixIn(_BaseModelAlgorithm):
    """Shared methods/attributes for both modeller and worker."""

    # This is set in the base model algorithm
    model: DistributedModelProtocol

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @property
    def epochs(self) -> Optional[int]:
        """Returns model epochs."""
        return self.model.epochs

    @property
    def steps(self) -> Optional[int]:
        """Returns model steps."""
        return self.model.steps

    def diff_params(self, old_params: _Weights) -> _Residuals:
        return self.model.diff_params(
            old_params=old_params, new_params=self.model.get_param_states()
        )

    def get_param_states(self) -> _Weights:
        """Returns the current parameters of the underlying model."""
        return self.model.get_param_states()

    def apply_update(self, update: _Weights) -> _Weights:
        """Applies a parameter update to the underlying model."""
        return self.model.apply_weight_updates([update])

    def serialize(self, filename: str) -> None:
        """Serializes and saves the model parameters."""
        self.model.serialize(filename)


class _ModellerSide(
    _BaseModelTrainingMixIn,
    _BaseModellerModelAlgorithm,
):
    """Modeller side of the FederatedModelTraining algorithm."""

    def __init__(
        self,
        *,
        model: DistributedModelProtocol,
        **kwargs: Any,
    ):
        super().__init__(model=model, **kwargs)

    def run(
        self,
        iteration: int = 0,
        update: Optional[_Weights] = None,
        validation_metrics: Optional[Mapping[str, float]] = None,
    ) -> _SerializedWeights:
        """Takes a weight update, applies it and returns the new model parameters."""
        if update is not None:
            self.apply_update(update)
        nn_params: _Weights = self.get_param_states()
        serialized_params = self.model.serialize_params(nn_params)
        if self.modeller_checkpointing:
            # Check if there are any previous checkpoints and remove them
            for fname in os.listdir(config.settings.paths.logs_dir):
                if fname.startswith(str(self.checkpoint_filename)):
                    os.remove(os.path.join(config.settings.paths.logs_dir, fname))
            self.serialize(
                filename=f"{config.settings.paths.logs_dir}/{self.checkpoint_filename}-iteration-{iteration}.pt"
            )

        if validation_metrics:
            for key, value in validation_metrics.items():
                self.model.log_(key, value, on_epoch=True, prog_bar=True, logger=True)
        return serialized_params


class _WorkerSide(
    _BaseModelTrainingMixIn,
    _BaseWorkerModelAlgorithm,
):
    """Worker side of the FederatedModelTraining algorithm."""

    def __init__(
        self,
        *,
        model: DistributedModelProtocol,
        **kwargs: Any,
    ):
        super().__init__(model=model, **kwargs)

    def run(
        self,
        model_params: _SerializedWeights,
        iterations: int,
    ) -> tuple[_Residuals, Optional[dict[str, str]]]:
        """Takes the model parameters, trains and returns the parameter update."""
        tensor_model_params = self.model.deserialize_params(model_params)
        self.model.update_params(tensor_model_params)

        # Train for one federated round - `iterations` many steps or epochs
        self.model.set_model_training_iterations(iterations)
        self.model.reset_trainer()
        validation_metrics: Optional[dict[str, str]] = self.model.fit(self.datasource)
        # Return the weight update and validation metrics
        return self.diff_params(old_params=tensor_model_params), validation_metrics

    def save_final_parameters(self, model_params: _SerializedWeights) -> None:
        """Saves the final global model parameters.

        :::note

        This method saves the final global model to a file called `model.pt`.

        :::

        Args:
            model_params: The final global model parameters.
        """
        self.update_params(model_params)
        # TODO: [BIT-1043]: pass filename for serialization
        self.model.serialize(config.settings.paths.output_dir / "model.pt")


@delegates()
class FederatedModelTraining(
    _BaseModelAlgorithmFactory[_ModellerSide, _WorkerSide],
):
    """Algorithm for training a model remotely and returning its updated parameters.

    This algorithm is designed to be compatible with the `FederatedAveraging` protocol.

    Args:
        model: The model to train on remote data.

    Attributes:
        model: The model to train on remote data.
        modeller_checkpointing: Whether to save the last checkpoint on the modeller
            side. Defaults to True.
        checkpoint_filename: The filename for the last checkpoint. Defaults to
            the task id and the last iteration number, i.e.,
            `{taskid}-iteration-{iteration_number}.pt`.
    """

    # The modeller_checkpoints and checkpoint filename don't need to be sent to
    # the worker, hence they don't need to be serialized.
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"model": MAIN_MODEL_REGISTRY}
    _inference_algorithm: bool = False

    def __init__(
        self,
        *,
        model: _DistributedModelTypeOrReference,
        modeller_checkpointing: bool = True,
        checkpoint_filename: Optional[str] = None,
        **kwargs: Any,
    ):
        self.modeller_checkpointing = modeller_checkpointing
        self.checkpoint_filename = checkpoint_filename
        super().__init__(model=model, **kwargs)

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the FederatedModelTraining algorithm."""
        model = self._get_model_from_reference_and_upload_weights(
            project_id=self.project_id
        )
        return _ModellerSide(
            model=model,
            modeller_checkpointing=self.modeller_checkpointing,
            checkpoint_filename=self.checkpoint_filename,
            **kwargs,
        )

    def worker(
        self,
        *,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns the worker side of the FederatedModelTraining algorithm.

        Args:
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
                May contain URLs for downloading models directly rather than from
                the hub.
            **kwargs: Additional keyword arguments to pass to the worker side.

        Returns:
            Worker side of the FederatedModelTraining algorithm.
        """
        model_urls: Optional[dict[str, ModelURLs]] = (
            context.model_urls if context else None
        )
        model = self._get_model_and_download_weights(
            hub=hub,
            project_id=self.project_id,
            auth_model_urls=model_urls,
        )
        return _WorkerSide(model=model, **kwargs)
