"""Operations done at batch time defined here."""

from __future__ import annotations

import inspect
from types import GenericAlias
from typing import Any, Protocol, Union, cast

import albumentations as A
import albumentations.augmentations as albumentations_augmentations
import albumentations.pytorch as albumentations_pytorch
import attr
from marshmallow import fields, post_load
from marshmallow_union import Union as M_Union
import numpy as np

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.types import DataSplit
from bitfount.transformations.base_transformation import _TransformationSchema
from bitfount.transformations.exceptions import TransformationParsingError
from bitfount.transformations.unary_operations import UnaryOperation
from bitfount.types import _JSONDict

#: Dictionary of available image transformations and their corresponding classes.
from bitfount.utils import delegates

IMAGE_TRANSFORMATIONS: dict[str, type[A.BasicTransform]] = {
    name: class_
    for name, class_ in vars(albumentations_augmentations).items()
    if inspect.isclass(class_)
    # types.GenericAlias instances (e.g. list[str]) are reported as classes by
    # inspect.isclass() but are not compatible with issubclass() against an
    # abstract class, so we need to exclude.
    # See: https://github.com/python/cpython/issues/101162
    # TODO: [Python 3.11] This issue is fixed in Python 3.11 so can remove
    and not isinstance(class_, GenericAlias)
    and issubclass(class_, A.BasicTransform)
    and not inspect.isabstract(class_)
}
if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    IMAGE_TRANSFORMATIONS.update(
        {
            name: class_
            for name, class_ in vars(albumentations_pytorch).items()
            if inspect.isclass(class_)
            # types.GenericAlias instances (e.g. list[str]) are reported as classes by
            # inspect.isclass() but are not compatible with issubclass() against an
            # abstract class, so we need to exclude.
            # See: https://github.com/python/cpython/issues/101162
            # TODO: [Python 3.11] This issue is fixed in Python 3.11 so can remove
            and not isinstance(class_, GenericAlias)
            and issubclass(class_, A.BasicTransform)
            and not inspect.isabstract(class_)
        }
    )


@delegates()
@attr.dataclass(kw_only=True)
class BatchTimeOperation(UnaryOperation):
    """Class just to denote that transformation will happen at batch time.

    All batch time operations must be unary operations.

    Args:
        step: Denotes whether transformations should be performed at training,
            validation or test time.

    """

    step: DataSplit


@delegates()
@attr.dataclass(kw_only=True)
class AlbumentationsImageTransformation(BatchTimeOperation):
    """Represents image transformations done on a single column at batch time.

    Args:
        transformations: list of transformations to be performed in order as one
            transformation.

    Raises:
        ValueError: If the `output` is set to False.
    """

    _registry_name = "albumentations"

    transformations: list[Union[str, dict[str, _JSONDict]]]

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if not self.output:
            raise ValueError("`output` cannot be False for a BatchTimeOperation")

    def _load_transformation(
        self, tfm: Union[str, dict[str, _JSONDict]]
    ) -> A.BasicTransform:
        """Loads and returns transformation in albumentations.

        Args:
            tfm: Albumentations transformation.

        Raises:
            TransformationParsingError: If the transformation name cannot be parsed
                properly.
            ValueError: If the transformation cannot be found.

        Returns:
            The transform loaded in albumentations.
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
        transformation = IMAGE_TRANSFORMATIONS.get(tfm_name)
        if transformation is None:
            raise ValueError(f"Transformation {tfm_name} could not be found.")

        return transformation(**tfm_args)

    def get_callable(self) -> _AlbumentationsAugmentation:
        """Returns callable which performs the transformations.

        Returns:
            The callable to perform transformations.
        """
        list_of_transformations: list[A.BasicTransform] = []
        for tfm in self.transformations:
            a_tfm = self._load_transformation(tfm)
            list_of_transformations.append(a_tfm)

        tfm_callable = A.Compose(list_of_transformations)
        return cast(_AlbumentationsAugmentation, tfm_callable)

    class _Schema(_TransformationSchema):
        """Marshmallow schema for ImageTransformation."""

        # From Transformation
        name = fields.String(default=None)
        output = fields.Boolean(default=True)
        # From UnaryOperation
        arg = fields.String(required=True)
        # From BatchTimeOperation
        step = fields.Method(
            serialize="_serialize_step", deserialize="_deserialize_step"
        )
        # From ImageTransformation
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
        def _serialize_step(transformation: AlbumentationsImageTransformation) -> str:
            """Serializes the step of the transformation from Enum to string."""
            return transformation.step.value

        @staticmethod
        def _deserialize_step(value: str) -> DataSplit:
            """Deserializes the step of the transformation from string to Enum."""
            return DataSplit(value)

        @post_load
        def make_transformation(
            self, data: _JSONDict, **_kwargs: Any
        ) -> AlbumentationsImageTransformation:
            """Creates the ImageTransformation object from the marshmallow data."""
            return AlbumentationsImageTransformation(**data)


class _AlbumentationsAugmentation(Protocol):
    """Protocol for the signature of an albumentations augmentation function."""

    def __call__(self, *, image: np.ndarray) -> dict[str, np.ndarray]:
        """Calls the function.

        `image` must be passed as a kwarg.
        """
        ...
