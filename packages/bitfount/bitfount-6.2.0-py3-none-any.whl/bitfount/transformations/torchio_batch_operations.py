"""TorchIO Operations done at batch time defined here."""

from __future__ import annotations

import inspect
from typing import Any, Protocol, Union, cast

import attr
from marshmallow import fields, post_load
from marshmallow_union import Union as M_Union
import numpy as np

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    import torchio as tio

from bitfount.data.types import DataSplit
from bitfount.transformations.base_transformation import _TransformationSchema
from bitfount.transformations.batch_operations import BatchTimeOperation
from bitfount.transformations.exceptions import TransformationParsingError
from bitfount.types import _JSONDict

#: Dictionary of available image transformations and their corresponding classes.
from bitfount.utils import delegates

# Initialise dictionary, required in case we aren't using the PyTorch engine
TORCHIO_IMAGE_TRANSFORMATIONS: dict[str, type[tio.transforms.Transform]] = {}
if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    TORCHIO_IMAGE_TRANSFORMATIONS.update(
        {
            name: class_
            for name, class_ in vars(tio.transforms).items()
            if inspect.isclass(class_)
            and not inspect.isabstract(class_)
            and ("augmentation" in str(class_) or "preprocessing" in str(class_))
        }
    )


@delegates()
@attr.dataclass(kw_only=True)
class TorchIOImageTransformation(BatchTimeOperation):
    """Represents torchio image transformations done on a single column at batch time.

    Args:
        transformations: list of torchio transformations to be performed in order as one
            transformation.

    Raises:
        ValueError: If the `output` is set to False.
    """

    _registry_name = "torchio"

    transformations: list[Union[str, dict[str, _JSONDict]]]

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if not self.output:
            raise ValueError("`output` cannot be False for a BatchTimeOperation")

    def _load_transformation(
        self, tfm: Union[str, dict[str, _JSONDict]]
    ) -> tio.transforms.Transform:
        """Loads and returns transformation in torchio.

        Args:
            tfm: Torchio transformation.

        Raises:
            TransformationParsingError: If the transformation name cannot be parsed
                properly.
            ValueError: If the transformation cannot be found.

        Returns:
            The transform loaded in torchio.
        """
        if isinstance(tfm, dict):
            tfm_keys = list(tfm.keys())
            if len(tfm_keys) > 1:
                raise TransformationParsingError(
                    f"Transformation has supplied multiple names: {tfm_keys}"
                )
            tfm_name = tfm_keys[0]
            tfm_args = tfm[tfm_name]
        else:
            tfm_name = tfm
            tfm_args = {}
        transformation = TORCHIO_IMAGE_TRANSFORMATIONS.get(tfm_name)
        if transformation is None:
            raise ValueError(f"Transformation {tfm_name} could not be found.")

        return transformation(**tfm_args)

    def get_callable(self) -> _TorchIOAugmentation:
        """Returns callable which performs the transformations.

        Returns:
            The callable to perform transformations.
        """
        list_of_transformations: list[tio.transforms.Transform] = []
        for tfm in self.transformations:
            a_tfm = self._load_transformation(tfm)
            list_of_transformations.append(a_tfm)

        tfm_callable = tio.Compose(list_of_transformations)
        return cast(_TorchIOAugmentation, tfm_callable)

    class _Schema(_TransformationSchema):
        """Marshmallow schema for TorchIOImageTransformation."""

        # From Transformation
        name = fields.String(default=None)
        output = fields.Boolean(default=True)
        # From UnaryOperation
        arg = fields.String(required=True)
        # From BatchTimeOperation
        step = fields.Method(
            serialize="_serialize_step", deserialize="_deserialize_step"
        )
        # From TorchIOImageTransformation
        transformations = fields.List(
            M_Union(
                [
                    fields.String(),
                    fields.Dict(
                        keys=fields.String(),
                        values=fields.Dict(keys=fields.String(), values=fields.Raw()),
                    ),
                ],
            ),
            required=True,
        )

        @staticmethod
        def _serialize_step(transformation: TorchIOImageTransformation) -> str:
            """Serializes the step of the transformation from Enum to string."""
            return transformation.step.value

        @staticmethod
        def _deserialize_step(value: str) -> DataSplit:
            """Deserializes the step of the transformation from string to Enum."""
            return DataSplit(value)

        @post_load
        def make_transformation(
            self, data: _JSONDict, **_kwargs: Any
        ) -> TorchIOImageTransformation:
            """Creates the ImageTransformation object from the marshmallow data."""
            return TorchIOImageTransformation(**data)


class _TorchIOAugmentation(Protocol):
    """Protocol for the signature of an torchio transformation function."""

    def __call__(self, data: np.ndarray) -> np.ndarray:
        """Calls the function."""
        ...
