"""PyTorch implementations of the federated learning mixin classes."""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping, Sequence
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, Optional, cast

import pytorch_lightning as pl
import torch

from bitfount.backends.pytorch.federated.shim import PyTorchBackendTensorShim
from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from bitfount.federated.mixins import _DistributedModelMixIn
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.shim import _load_default_tensor_shim
from bitfount.models.bitfount_model import BitfountModel
from bitfount.types import (
    T_DTYPE,
    DistributedModelProtocol,
    _Residuals,
    _SerializedWeights,
    _TensorLike,
    _Weights,
)

if TYPE_CHECKING:
    from bitfount.data.dataloaders import BitfountDataLoader
    from bitfount.hub.api import BitfountHub
    from bitfount.types import _DistributedModelTypeOrReference

logger = logging.getLogger(__name__)


class _PyTorchDistributedModelMixIn(
    _DistributedModelMixIn[T_DTYPE], ABC, Generic[T_DTYPE]
):
    """PyTorch implementation of the DistributedModelMixIn."""

    epochs: Optional[int]
    steps: Optional[int]
    train_dl: Optional[BitfountDataLoader]
    _pl_trainer: pl.Trainer
    _total_num_batches_trained: int

    def get_param_states(self) -> dict[str, _TensorLike]:
        """See base class.

        Wrapping the state dictionary with `dict` ensures we return a `dict` rather than
        an `OrderedDict`.
        """
        aux = dict(self._model.state_dict())  # type: ignore[attr-defined] # Reason: _model is initialised in subclass # noqa: E501

        return self._get_torch_adapter_states(aux)

    def _get_torch_tensor_states(
        self, adapted_params: Mapping[str, _TensorLike]
    ) -> dict[str, torch.Tensor]:
        """Get the tensors out of our adapter."""
        tensor_dict: dict[str, torch.Tensor] = {}
        for k, v in adapted_params.items():
            if isinstance(v, _AdaptorForPyTorchTensor):
                tensor_dict[k] = v.torchtensor
        return tensor_dict

    def _get_torch_adapter_states(
        self, torch_tensor_params: Mapping[str, torch.Tensor]
    ) -> dict[str, _TensorLike]:
        """Put tensors in our torch.Tensor adapter."""
        return {k: _AdaptorForPyTorchTensor(v) for k, v in torch_tensor_params.items()}

    def apply_weight_updates(self, weight_updates: Sequence[_Weights]) -> _Weights:
        """See base class."""
        params_to_update_adapted = self.get_param_states()
        params_to_update = self._get_torch_tensor_states(params_to_update_adapted)
        tensor_weight_updates = [
            self._get_torch_tensor_states(params) for params in weight_updates
        ]
        weight = 1 / len(weight_updates)
        for name in tensor_weight_updates[0]:
            params_to_update[name].data.copy_(
                params_to_update[name]
                + torch.stack(
                    [weight * params[name].data for params in tensor_weight_updates],
                    dim=0,
                ).sum(dim=0)
            )
        adapted_params: _Weights = self._get_torch_adapter_states(params_to_update)
        return adapted_params

    def update_params(self, new_model_params: _Weights) -> None:
        """See base class."""
        current_params_adapted = self.get_param_states()
        current_params = self._get_torch_tensor_states(current_params_adapted)
        new_model_params_torch = self._get_torch_tensor_states(new_model_params)
        for name in new_model_params_torch:
            current_params[name].data.copy_(new_model_params_torch[name].data)

    def deserialize_params(self, serialized_weights: _SerializedWeights) -> _Weights:
        """Convert serialized model params to tensors."""
        backend_tensor_shim = cast(
            PyTorchBackendTensorShim, _load_default_tensor_shim()
        )

        weights = {
            name: backend_tensor_shim.to_tensor(param)
            for name, param in serialized_weights.items()
        }

        return weights

    def serialize_params(self, weights: _Weights) -> _SerializedWeights:
        """Serialize model params."""
        backend_tensor_shim = cast(
            PyTorchBackendTensorShim, _load_default_tensor_shim()
        )

        serialized_weights = {
            name: backend_tensor_shim.to_list(param) for name, param in weights.items()
        }

        return serialized_weights

    @staticmethod
    def diff_params(
        old_params: _Weights,
        new_params: _Weights,
    ) -> _Residuals:
        """See base class."""
        old_params_torch: dict[str, torch.Tensor] = {}
        for k, v in old_params.items():
            if isinstance(v, _AdaptorForPyTorchTensor):
                old_params_torch[k] = v.torchtensor
        new_params_torch: dict[str, torch.Tensor] = {}
        for k, v in new_params.items():
            if isinstance(v, _AdaptorForPyTorchTensor):
                new_params_torch[k] = v.torchtensor
        for name in new_params:
            old_params_torch[name].data.copy_(
                new_params_torch[name].data - old_params_torch[name].data
            )
        old_params_adapted: _Residuals = {
            k: _AdaptorForPyTorchTensor(v) for k, v in old_params_torch.items()
        }
        return old_params_adapted

    def set_model_training_iterations(self, iterations: int) -> None:
        """See base class."""
        if self.epochs:
            self.epochs = iterations
            if hasattr(self, "_pl_trainer"):
                self._pl_trainer.fit_loop.max_epochs = iterations
        else:
            self.steps = iterations
            if hasattr(self, "_pl_trainer"):
                self._pl_trainer.fit_loop.epoch_loop.max_steps = iterations

    def reset_trainer(self) -> None:
        """See base class."""
        # `trainer_init()` comes from `PyTorchBitfountModel{,v2}`
        # This is a standard pattern for MixIn classes.
        self._pl_trainer: pl.Trainer = self.trainer_init()  # type: ignore[attr-defined] # Reason: see above. # noqa: E501

        # The `max_epochs` attribute on the trainer does not need to be reset for
        # epochs. This behaviour is only for steps. See pytorch-lightning issue #11425
        if self.steps and self.train_dl:
            # `max_steps` must be set to however number of steps we want to train
            # greater than the number of batches already trained
            self._pl_trainer.fit_loop.epoch_loop.max_steps = self.steps + (
                self._total_num_batches_trained % len(self.train_dl)
            )

    def tensor_precision(self) -> T_DTYPE:
        """Returns torch default dtype.

        This is `torch.float32` by default unless changed. This method should be
        overridden in the subclass if the model supports non-32-bit model tensors.
        """
        return cast(T_DTYPE, torch.get_default_dtype())

    def log_(self, name: str, value: Any, **kwargs: Any) -> Any:
        """Simple wrapper around the pytorch lightning `log` method."""
        # Method is present on `PyTorchBitfountModel{,v2}` inherited from `pl.LightningModule`. # noqa: E501
        self.log(name, value, **kwargs)  # type: ignore[attr-defined] # Reason: see above. # noqa: E501

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
        if isinstance(self, BitfountModel):
            # If the model is a custom model, we need to save the source code to a file
            # and create a BitfountModelReference to pass to the algorithm.
            filename = f"{type(self).__name__}.py"
            self.serialize_model_source_code(
                filename=filename, extra_imports=extra_imports
            )
            logger.info(
                f"Custom model source code saved to file: {filename}. "
                f"Version '{kwargs.get('model_version') or 'latest'}'"
            )
            if hasattr(self, "batch_size"):
                kwargs["batch_size"] = self.batch_size
            ref = BitfountModelReference(
                model_ref=Path(filename),
                model_version=kwargs.get("model_version"),
                datastructure=kwargs.get("datastructure") or self.datastructure,
                schema=kwargs.get("schema") or self.schema,
                hub=hub,
                hyperparameters={
                    "epochs": self.epochs,
                    "steps": self.steps,
                    **kwargs,
                },
                model_description=kwargs.get("model_description", ""),
            )
            logger.debug("Ensuring model reference matches model on Hub")
            # We need to make sure the model exists on the hub and is up to date
            # prior to sending the model reference to the pod
            # otherwise the pod will pull an old model version
            ref.upload_model_and_weights()
            return ref
        return cast(DistributedModelProtocol, self)
