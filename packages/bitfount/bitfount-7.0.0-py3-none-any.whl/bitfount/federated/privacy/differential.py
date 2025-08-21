"""Contains classes for marking differential privacy on models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import inspect
from types import MappingProxyType
from typing import Any, ClassVar, Literal, Optional, Union

import desert
import marshmallow
from marshmallow import fields
from marshmallow.validate import OneOf
from marshmallow_union import Union as M_Union

from bitfount.federated.exceptions import DPParameterError
from bitfount.federated.logging import _get_federated_logger
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    UsedForConfigSchemas,
    _BaseSerializableObjectMixIn,
    _StrAnyDict,
)

logger = _get_federated_logger(__name__)

_DEFAULT_ALPHAS: list[float] = [1 + x / 10.0 for x in range(1, 100)] + list(
    range(12, 64)
)
_DEFAULT_DELTA: float = 1e-6
_ALLOWED_LOSS_REDUCTIONS: tuple[str, str] = ("mean", "sum")

# The mutable underlying dict that holds the registry information
_registry: dict[str, type[_BaseDPConfig]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, type[_BaseDPConfig]] = MappingProxyType(_registry)

try:
    from opacus import PrivacyEngine
except ImportError:
    logger.debug("Opacus not installed, Differential Privacy will not be available.")


@dataclass
class _BaseDPConfig:
    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to registry")
            _registry[cls.__name__] = cls


@dataclass
class DPModellerConfig(UsedForConfigSchemas):
    """Modeller configuration options for Differential Privacy.

    :::info

    `epsilon` and `delta` are also set by the Pods involved in the task and
    take precedence over the values supplied here.

    :::

    Args:
        epsilon: The maximum epsilon value to use.
        max_grad_norm: The maximum gradient norm to use. Defaults to 1.0.
        noise_multiplier: The noise multiplier to control how much noise to add.
            Defaults to 0.4.
        alphas: The alphas to use. Defaults to floats from 1.1 to 63.0 (inclusive) with
            increments of 0.1 up to 11.0 followed by increments of 1.0 up to 63.0.
            Note that none of the alphas should be equal to 1.
        delta: The target delta to use. Defaults to 1e-6.
        loss_reduction: The loss reduction to use. Available options are "mean" and
            "sum". Defaults to "mean".
        auto_fix: Whether to automatically fix the model if it is not DP-compliant.
            Currently, this just converts all `BatchNorm` layers to `GroupNorm`.
            Defaults to True.

    Raises:
        ValueError: If loss_reduction is not one of "mean" or "sum".
    """

    # DP directly related options
    epsilon: float
    max_grad_norm: Union[float, list[float]] = 1.0
    noise_multiplier: float = 0.4
    alphas: list[float] = field(default_factory=lambda: _DEFAULT_ALPHAS)
    delta: float = _DEFAULT_DELTA
    loss_reduction: Literal["mean", "sum"] = desert.field(
        marshmallow.fields.String(validate=OneOf(_ALLOWED_LOSS_REDUCTIONS)),
        default="mean",
    )

    # Other options
    auto_fix: bool = True
    fields_dict: ClassVar[_StrAnyDict] = {
        "epsilon": fields.Float(),
        "max_grad_norm": M_Union([fields.Float(), fields.List(fields.Float())]),
        "noise_multiplier": fields.Float(),
        "alphas": fields.List(fields.Float()),
        "delta": fields.Float(),
        "loss_reduction": fields.String(),
        "auto_fix": fields.Bool(),
    }
    nested_fields: ClassVar[dict[str, _StrAnyDict]] = {}

    def __post_init__(self) -> None:
        # Validate loss_reduction
        if self.loss_reduction not in _ALLOWED_LOSS_REDUCTIONS:
            raise ValueError(
                f"loss_reduction must be one of {_ALLOWED_LOSS_REDUCTIONS}, "
                f'not "{self.loss_reduction}".'
            )
        if any(alpha == 1 for alpha in self.alphas):
            raise DPParameterError(
                "You are trying to run a DP-task with an alpha value of 1, "
                "which is not allowed. Please update your alpha values and "
                "try again."
            )


@dataclass
class DPPodConfig(_BaseDPConfig, UsedForConfigSchemas):
    """Pod configuration options for Differential Privacy.

    Primarily used as caps and bounds for what options may be set by the modeller.

    Args:
        epsilon: The maximum epsilon value to use.
        delta: The maximum target delta to use. Defaults to 1e-6.
    """

    epsilon: float
    delta: float = _DEFAULT_DELTA
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "epsilon": fields.Float(),
        "delta": fields.Float(default=_DEFAULT_DELTA),
    }


class _DifferentiallyPrivate(_BaseSerializableObjectMixIn):
    """Marks that the model supports differential privacy.

    This class itself does not handle the implementation details of DP (as that
    will differ on a per-model/per-library basis) but captures the configuration
    details for DP to enable implementing models to make use of it.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "_dp_config": fields.Nested(
            desert.schema(DPModellerConfig),
            allow_none=True,
            data_key="dp_config",
            dump_only=True,
        ),
        "dp_config": fields.Nested(
            desert.schema(DPModellerConfig),
            allow_none=True,
            data_key="dp_config",
            load_only=True,
        ),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(
        self,
        dp_config: Optional[Union[DPModellerConfig, Mapping[str, Any]]] = None,
        **kwargs: Any,
    ):
        """Stores the Differential Privacy configuration for this model.

        Args:
            dp_config: The Differential Privacy configuration to use. Can be either
                a `DPModellerConfig` instance or a string-keyed mapping.
            **kwargs: Other keyword arguments to be passed up the inheritance
                hierarchy.
        """
        self.class_name = type(self).__name__
        # Capture DP config options, converting if needed
        if not isinstance(dp_config, DPModellerConfig):
            dp_config = self._convert_to_dpconfig(dp_config)
        self._dp_config: Optional[DPModellerConfig] = dp_config
        self._dp_engine: Optional[PrivacyEngine] = None
        self._noise_multiplier: Optional[float] = None

        # Keeps track of whether privacy guarantee has been exceeded in the past.
        # This attribute has been mangled to avoid being used by subclasses because
        # a False value is not necessarily False and can be misleading. Should only be
        # used by the `_is_privacy_guarantee_exceeded` method.
        self.__privacy_guarantee_exceeded: bool = False

        if self._dp_config:
            logger.info(
                f"Model is differentially private with settings: {self._dp_config}"
            )
        else:
            logger.info("No differential privacy settings provided.")

        super().__init__(**kwargs)

    @staticmethod
    def _convert_to_dpconfig(
        dict_config: Optional[Mapping[str, Any]] = None,
    ) -> Optional[DPModellerConfig]:
        """Converts a dict-based configuration into a DPModellerConfig.

        If the configuration is None, will be returned as-is.
        """
        if dict_config:
            return DPModellerConfig(**dict_config)
        else:
            return None

    def apply_pod_dp(self, pod_dp_config: Optional[DPPodConfig]) -> None:
        """Applies pod-based DP caps and bounds to configuration options.

        Args:
            pod_dp_config: Pod-based configuration related to DP.
        """
        if self._dp_config:
            if not pod_dp_config:
                logger.info("No pod DP preferences, using modeller preferences.")
                return

            # Modify maximum epsilon budget based on pod cap
            if self._dp_config.epsilon > pod_dp_config.epsilon:
                logger.warning(
                    f"Requested DP max epsilon ({self._dp_config.epsilon}) exceeds "
                    f"maximum value allowed by pod. Using pod max of "
                    f"{pod_dp_config.epsilon}."
                )
                self._dp_config.epsilon = pod_dp_config.epsilon

            # Modify maximum target delta based on pod cap
            if self._dp_config.delta > pod_dp_config.delta:
                logger.warning(
                    f"Requested DP target delta ({self._dp_config.delta}) exceeds "
                    f"maximum value allowed by pod. Using pod max of "
                    f"{pod_dp_config.delta}."
                )
                self._dp_config.delta = pod_dp_config.delta

    def _is_privacy_guarantee_exceeded(self) -> bool:
        """Checks whether the privacy spent exceeds the allowed max.

        Returns: True if maximum privacy budget exceeded, False if not or if DP not
            being checked.

        Raises:
            ValueError: If DP engine created but no DP configuration could be found.
        """
        # If monitoring DP, perform checks
        if self._dp_engine:
            if not self._dp_config:
                raise ValueError(
                    "DP Engine created but no configuration could be found."
                )

            # Check if the guarantee has already been exceeded previously
            if self.__privacy_guarantee_exceeded:
                return True

            # Calculate current epsilon level
            epsilon = self._dp_engine.get_epsilon(self._dp_config.delta)

            # Check privacy constraints
            if epsilon >= self._dp_config.epsilon:
                logger.warning("Exceeded privacy guarantee.")
                logger.federated_warning(
                    "Reached differential privacy limit. Stopping training."
                )
                self.__privacy_guarantee_exceeded = True
                return True

        # If not exceeded or not being checked
        return False
