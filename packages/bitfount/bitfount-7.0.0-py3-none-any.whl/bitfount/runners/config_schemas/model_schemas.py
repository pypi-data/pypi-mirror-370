"""Config YAML specification classes related to models and model references."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Optional, Union

import desert
from marshmallow import ValidationError, fields

from bitfount.federated.privacy.differential import DPModellerConfig
from bitfount.models.base_models import LoggerConfig
from bitfount.runners.config_schemas.common_schemas import ModelReference
from bitfount.types import _JSONDict

_logger = logging.getLogger(__name__)


@dataclass
class ModelStructureConfig:
    """Configuration for the ModelStructure."""

    name: str
    arguments: _JSONDict = desert.field(
        fields.Dict(keys=fields.Str), default_factory=dict
    )


@dataclass
class BitfountModelReferenceConfig:
    """Configuration for BitfountModelReference."""

    model_ref: Union[Path, str] = desert.field(ModelReference())
    model_version: Optional[int] = None
    username: Optional[str] = None
    weights: Optional[str] = None


@dataclass
class ModelConfig:
    """Configuration for the model."""

    # For existing models
    name: Optional[str] = None
    structure: Optional[ModelStructureConfig] = None

    # For custom models
    bitfount_model: Optional[BitfountModelReferenceConfig] = None

    # Other
    hyperparameters: _JSONDict = desert.field(
        fields.Dict(keys=fields.Str), default_factory=dict
    )
    logger_config: Optional[LoggerConfig] = None
    dp_config: Optional[DPModellerConfig] = None

    def __post_init__(self) -> None:
        # Validate either name or bitfount_model reference provided
        self._name_or_bitfount_model()

    def _name_or_bitfount_model(self) -> None:
        """Ensures that both `name` and `bitfount_model` can't be set.

        Raises:
            ValidationError: if both `name` and `bitfount_model` are set
        """
        if self.name:
            raise ValidationError(
                "Model name support has been removed. Must specify a bitfount model."
            )
        if not self.bitfount_model:
            raise ValidationError("No model specified. Must specify a bitfount_model.")
