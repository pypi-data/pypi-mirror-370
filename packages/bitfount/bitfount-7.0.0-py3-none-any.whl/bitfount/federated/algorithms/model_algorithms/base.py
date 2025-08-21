"""Base classes for all model-based algorithms.

Attributes:
    registry: A read-only dictionary of model algorithm factory names to their
        implementation classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
import inspect
import os
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Optional, Union, cast

from requests.exceptions import HTTPError

from bitfount.backends.pytorch.models.bitfount_model_migration import (
    maybe_convert_bitfount_model_class_to_v2,
)
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.federated.algorithms.base import (
    BaseAlgorithmFactory,
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
    T_ModellerSide,
    T_WorkerSide,
    _BaseAlgorithm,
)
from bitfount.federated.authorisation_checkers import ModelURLs
from bitfount.federated.exceptions import DPNotAppliedError
from bitfount.federated.helper import TaskContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.models.base_models import MAIN_MODEL_REGISTRY
from bitfount.models.bitfount_model import BitfountModel
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    DistributedModelProtocol,
    _SerializedWeights,
)

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub
    from bitfount.types import _DistributedModelTypeOrReference


logger = _get_federated_logger(__name__)


class _BaseModelAlgorithm(Generic[T_DTYPE], _BaseAlgorithm, ABC):
    """Blueprint for either the modeller side or the worker side of ModelAlgorithm."""

    def __init__(
        self,
        *,
        model: DistributedModelProtocol[T_DTYPE],
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model = model
        self.pretrained_file = pretrained_file

    @property
    def tensor_precision(self) -> T_DTYPE:
        """Returns model tensor precision."""
        return cast(T_DTYPE, self.model.tensor_precision())


class _BaseModellerModelAlgorithm(_BaseModelAlgorithm, BaseModellerAlgorithm, ABC):
    """Modeller side of the algorithm."""

    def __init__(
        self,
        *,
        model: DistributedModelProtocol,
        modeller_checkpointing: bool = True,
        checkpoint_filename: Optional[str] = None,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ):
        super().__init__(model=model, pretrained_file=pretrained_file, **kwargs)
        self.modeller_checkpointing = modeller_checkpointing
        self.checkpoint_filename = checkpoint_filename

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm as required."""
        if not self.model.initialised:
            self.model.initialise_model(context=TaskContext.MODELLER)
        if not self.checkpoint_filename:
            self.checkpoint_filename = task_id
        # This needs to occur AFTER model initialization so the model is correctly
        # created. deserialize() may cause initialization but we can not rely on it
        # in this instance because we need to pass in context information.
        # This should be reviewed as part of [BIT-536].
        if self.pretrained_file is not None:
            logger.info(f"Deserializing model from {self.pretrained_file}.")
            self.model.deserialize(self.pretrained_file, **kwargs)


class _BaseWorkerModelAlgorithm(_BaseModelAlgorithm, BaseWorkerAlgorithm, ABC):
    """Worker side of the algorithm."""

    def __init__(self, *, model: DistributedModelProtocol, **kwargs: Any):
        super().__init__(model=model, **kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm as required."""
        # Apply pod DP settings if needed. Needs to occur before model
        # initialization so the right DP settings are applied during initialization.
        self._apply_pod_dp(pod_dp)
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def initialise_data(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> None:
        """Initialises the data for the algorithm.

        Args:
            datasource: The datasource to initialise the data from.
            data_splitter: The data splitter to use for splitting the data.
        """
        self.datasource = datasource
        self.data_splitter = data_splitter
        self.model.initialise_model(
            data=self.datasource,
            data_splitter=self.data_splitter,
            context=TaskContext.WORKER,
        )

    def update_params(self, params: _SerializedWeights) -> None:
        """Updates model parameters."""
        model_params = self.model.deserialize_params(params)
        self.model.update_params(model_params)

    def _apply_pod_dp(self, pod_dp: Optional[DPPodConfig]) -> None:
        """Applies pod-level Differential Privacy constraints if supported.

        The model must inherit from `DifferentiallyPrivate` for DP to be supported.

        Args:
            pod_dp: The pod DP constraints to apply or None if no constraints.
        """
        try:
            # only applied if model supports DP so can ignore attr-defined
            self.model.apply_pod_dp(pod_dp)  # type: ignore[attr-defined]  # Reason: caught by try-except  # noqa: E501
        except AttributeError as ae:
            # If the apply failed, but we weren't trying to apply anything, then no
            # problem. Otherwise, need to raise an error, as this has not been
            # correctly applied and the user may expect it to have been.
            if pod_dp is not None:
                logger.error(
                    "Unable to apply pod DP to model, model does not support DP."
                )
                raise DPNotAppliedError(
                    "Unable to apply pod DP to model, model does not support DP."
                ) from ae


# The mutable underlying dict that holds the registry information
_registry: dict[str, type[_BaseModelAlgorithmFactory]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, type[_BaseModelAlgorithmFactory]] = MappingProxyType(_registry)


class _BaseModelAlgorithmFactory(
    BaseAlgorithmFactory[T_ModellerSide, T_WorkerSide], ABC
):
    """Base factory for algorithms involving an underlying model.

    Args:
        model: The model for the federated algorithm.
        pretrained_file: A file path or a string containing a
            pre-trained model. Defaults to None.

    Attributes:
        model: The model for the federated algorithm.
        pretrained_file: A file path or a string containing a
            pre-trained model. Defaults to None.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"model": MAIN_MODEL_REGISTRY}

    def __init__(
        self,
        *,
        model: _DistributedModelTypeOrReference,
        pretrained_file: Optional[Union[str, os.PathLike]] = None,
        project_id: Optional[str] = None,
        **kwargs: Any,
    ):
        # TODO: [NO_TICKET: Consideration only] Consider if project_id is required
        #       on the algorithm or if it should be something inherent on the
        #       model_reference (which is all it's currently used for).
        super().__init__(**kwargs)
        self.model = model
        self.pretrained_file = pretrained_file
        self.project_id = project_id

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        super().__init_subclass__(*args, **kwargs)
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to Model Algorithm registry")
            _registry[cls.__name__] = cls

    @abstractmethod
    def modeller(self, **kwargs: Any) -> T_ModellerSide:
        """Modeller-side of the algorithm."""
        ...

    @abstractmethod
    def worker(self, *, hub: BitfountHub, **kwargs: Any) -> T_WorkerSide:
        """Worker-side of the algorithm."""
        ...

    def _get_model_and_download_weights(
        self,
        hub: Optional[BitfountHub] = None,
        project_id: Optional[str] = None,
        auth_model_urls: Optional[dict[str, ModelURLs]] = None,
    ) -> DistributedModelProtocol:
        """Retrieve model code and weights if necessary, instantiate a model instance.

        If `self.model` is a BitfountModelReference, retrieves the model and weights
        via the hub. If authorised model URLs for that model are provided via
        auth_models_urls, uses those URLs to retrieve the model and weights instead.

        If `self.model` is not a BitfountModelReference, just returns `self.model`.

        If the loaded model class is a v1 PyTorchBitfount model it is automatically
        converted to v2.

        Args:
            hub: BitfountHub instance to use for the model retrieval if needed.
                If not provided, uses the hub instance referenced by the
                BitfountModelReference instance.
            project_id: The project ID that this task is associated with, which
                dictates the project that model access is checked against when
                retrieving from a BitfountModelReference.
            auth_model_urls: If provided and retrieving from a BitfountModelReference,
                download URLs for a model reference from here will be used in
                preference to retrieving URLs from the hub.
                Used in cases where the model permissioning is associated with a
                user that is NOT the currently running user (e.g. when using a
                Modeller's usage quota but running on a worker).

        Returns:
              An instantiated model instance for the requested model. If the loaded
              model class is a v1 PyTorchBitfount model it is automatically converted
              to v2.
        """
        # TODO: [BIT-890] perhaps move this logic one level higher so that the algorithm
        # factory always takes a DistributedModelProtocol
        if isinstance(self.model, BitfountModelReference):
            if hub is not None:
                self.model.hub = hub

            model_id: str = self.model.model_id
            weights_bytes: Optional[bytes] = None
            # Defaults to using the hub.
            # If auth_model_urls are provided, will use those URLs instead.
            # If links expire, will fall back to using the hub.
            use_hub: bool = True
            if auth_model_urls and model_id in auth_model_urls:
                logger.info(
                    f"Retrieving model code for model {model_id}"
                    f" from quotas-provided URL"
                )
                use_hub = False
                model_urls: ModelURLs = auth_model_urls[model_id]
                # TODO: [BIT-4857] Remove model hash retrieval from here
                model_hash = self.model.hub._get_model_hash(
                    self.model.username,
                    self.model.model_name,
                    self.model.model_version,
                    project_id,
                )

                try:
                    model_cls: Optional[type[BitfountModel]] = (
                        self.model.hub.get_model_from_url(
                            model_urls.model_download_url, model_hash
                        )
                    )
                except HTTPError as e:
                    # We want to only use the hub as a fallback on 403
                    if e.response.status_code == 403:
                        logger.error(
                            f"Error retrieving model from download URL: {e}."
                            f" Attempting to retrieve model from hub."
                        )
                        use_hub = True
                    else:
                        raise e

                if model_urls.model_weights_url:
                    logger.info(
                        f"Retrieving model weights for model {model_id}"
                        f" from quotas-provided URL"
                    )
                    try:
                        weights_bytes = self.model.hub.get_weights_from_url(
                            model_urls.model_weights_url
                        )
                    except HTTPError as e:
                        # We want to only use the hub as a fallback on 403
                        if e.response.status_code == 403:
                            logger.error(
                                f"Error retrieving model from download URL: {e}."
                                f" Attempting to retrieve model from hub."
                            )
                            use_hub = True
                        else:
                            raise e

            if use_hub:
                logger.info(f"Retrieving model code for model {model_id} from hub")
                model_cls = self.model.get_model_from_hub(project_id=project_id)
                # TODO: [BIT-3019] Getting the weights here should not be called on both
                # modeller and worker sides
                if self.model.model_version:
                    logger.info(
                        f"Retrieving model weights for model {model_id} from hub"
                    )
                    weights_bytes = self.model.get_weights(project_id=project_id)

            # Check that the model has been retrieved correctly
            if not model_cls:
                raise ValueError(
                    "Unable to retrieve model from download URL,"
                    " check logs for details."
                )

            # [PyTorchBitfountModelv2] Conversion point
            model_cls = maybe_convert_bitfount_model_class_to_v2(model_cls)

            model = model_cls(
                datastructure=self.model.datastructure,
                schema=self.model.schema,
                **self.model.hyperparameters,
            )

            # If there is a weights file associated with the model then
            # initialise the model with these weights
            if weights_bytes is not None:
                logger.info("Applying weights..")
                model.deserialize(weights_bytes)

            self.model = cast(DistributedModelProtocol, model)
            return self.model
        else:
            return self.model

    def _get_model_from_reference_and_upload_weights(
        self, hub: Optional[BitfountHub] = None, project_id: Optional[str] = None
    ) -> DistributedModelProtocol:
        """Returns underlying model if BitfountModelReference.

        If not, just returns self.model.

        If the model referenced was a v1 PyTorchBitfountModel it is automatically
        converted to v2.
        """
        # TODO: [BIT-890] perhaps move this logic one level higher so that the algorithm
        # factory always takes a DistributedModelProtocol
        if isinstance(self.model, BitfountModelReference):
            if hub is not None:
                self.model.hub = hub
            model_cls = self.model.upload_model_and_weights(project_id=project_id)

            # [PyTorchBitfountModelv2] Conversion point
            model_cls = maybe_convert_bitfount_model_class_to_v2(model_cls)

            model = model_cls(
                datastructure=self.model.datastructure,
                schema=self.model.schema,
                **self.model.hyperparameters,
            )
            self.model = cast(DistributedModelProtocol, model)
            return self.model
        else:
            return self.model
