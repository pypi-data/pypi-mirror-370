"""Migration code for converting between PyTorchBitfountModels v1 and v2."""

from __future__ import annotations

from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Final, TypeVar, cast, overload

from typing_extensions import Self

from bitfount.models.bitfount_model import BitfountModel

if TYPE_CHECKING:
    # Only import the types here, do the main import further down
    from bitfount.backends.pytorch.models.bitfount_model import (
        PyTorchBitfountModel,
        PyTorchBitfountModelv2,
    )

# Tensor dtype type variable
T_DTYPE = TypeVar("T_DTYPE", covariant=True)

#####################################################
# ================ HERE BE DRAGONS ================ #
# Beyond here we start messing with metaclasses,    #
# dynamic class creation, etc. Be wary when making  #
# changes and ensure it's well tested as bugs       #
# related to this will be hard to track.            #
#####################################################
_METHODS_TO_REMOVE_IN_V2: Final = (
    "train_epoch_end",
    "validation_epoch_end",
    "test_epoch_end",
)


class _ConvertedBitfountModelMetaclass(ABCMeta):
    def mro(cls) -> list[type]:
        # DEV: We need to do the main import here to avoid circular import issues.
        #      By the nature of this function it will be called in places elsewhere
        #      in the codebase and reaches down into the pytorch packages, increasing
        #      the likelihood of circular imports massively.
        from bitfount.backends.pytorch.models.bitfount_model import (
            PyTorchBitfountModel,
        )

        # Remove PyTorchBitfountModel class from the mro so that methods from it are
        # not used/available to the converted class.
        orig_mro = super().mro()
        return [base for base in orig_mro if base is not PyTorchBitfountModel]

    def __getattribute__(cls, name: str) -> Any:
        # Explicitly remove disallowed methods from the derived class
        if name in _METHODS_TO_REMOVE_IN_V2:
            raise AttributeError(
                f"Method '{name}' is not available in"
                f" PyTorch Lightning v2 derived classes."
            )
        return super(_ConvertedBitfountModelMetaclass, cls).__getattribute__(name)

    def __repr__(cls) -> str:
        # Change repr string for class so that it contains information about the
        # converted class where possible
        # Original is of the form: <class '{module}.{qualname}'>
        converted_module_name = getattr(cls, "__converted_cls_module__", None)
        converted_qualname = getattr(cls, "__converted_cls_qualname__", None)
        if converted_module_name and converted_qualname:
            return (
                f"<class '{cls.__module__}.{cls.__qualname__}'"
                f" (converted from"
                f" '{converted_module_name}.{converted_qualname}'"
                f")>"
            )
        else:
            return super().__repr__()


def convert_bitfount_model_class_to_v2(
    old_bitfount_model_cls: type[PyTorchBitfountModel[T_DTYPE]],
) -> type[PyTorchBitfountModelv2[T_DTYPE]]:
    """Convert a PyTorchBitfountModel class to a PyTorchBitfountModelv2 class.

    Moves methods around to make them match with the new form, deletes others and
    reconstitutes the class with PyTorchBitfountModelv2 as one of its parent classes
    instead of PyTorchBitfountModel.

    Args:
        old_bitfount_model_cls: The class (not instance) of the old form model.

    Returns:
        A "Converted" class which is the original class converted to be a subclass of
        PyTorchBitfountModelv2 instead.
    """
    # DEV: We need to do the main import here to avoid circular import issues. By the
    #      nature of this function it will be called in places elsewhere in the
    #      codebase and reaches down into the pytorch packages, increasing the
    #      likelihood of circular imports massively.
    from bitfount.backends.pytorch.models.bitfount_model import (
        PyTorchBitfountModel,
        PyTorchBitfountModelv2,
    )

    # Old methods to move
    # The following we move so that they are wrapped with storage calls. There will
    # still be methods with the same name on the final class:
    # - training_step() -> _training_step()
    # - validation_step() -> _validation_step()
    # - test_step() -> _test_step()
    #
    # The following are moved because they are no longer supported in
    # v2 Lightning and so original methods must also be deleted:
    # - train_epoch_end() -> _train_epoch_end()
    # - validation_epoch_end() -> _validation_epoch_end()
    # - test_epoch_end() -> _test_epoch_end()
    class Converted(
        old_bitfount_model_cls,  # type: ignore[valid-type,misc] # Reason: It's valid
        PyTorchBitfountModelv2[T_DTYPE],
        metaclass=_ConvertedBitfountModelMetaclass,
    ):
        # Converted class metadata fields
        __converted_cls_module__ = old_bitfount_model_cls.__module__
        __converted_cls_name__ = old_bitfount_model_cls.__name__
        __converted_cls_qualname__ = old_bitfount_model_cls.__qualname__

        # Methods to move (but not delete)
        # The old names will then be overridden with the PyTorchBitfountModelv2
        # versions.
        _training_step = old_bitfount_model_cls.training_step
        training_step = PyTorchBitfountModelv2.training_step
        _validation_step = old_bitfount_model_cls.validation_step
        validation_step = PyTorchBitfountModelv2.validation_step
        _test_step = old_bitfount_model_cls.test_step
        test_step = PyTorchBitfountModelv2.test_step

        # Methods to move (and will be "deleted" by limiting __getattribute__ check)
        # Only set if these are actually overridden in old_bitfount_model_cls,
        # otherwise we can use the default implementation (this is the != function
        # comparisons).
        if callable(getattr(old_bitfount_model_cls, "train_epoch_end", None)):
            _train_epoch_end = old_bitfount_model_cls.train_epoch_end  # type: ignore[attr-defined] # Reason: getattr() check above # noqa: E501
        if (
            old_bitfount_model_cls.validation_epoch_end
            != PyTorchBitfountModel.validation_epoch_end
        ):
            _validation_epoch_end = old_bitfount_model_cls.validation_epoch_end
        if old_bitfount_model_cls.test_epoch_end != PyTorchBitfountModel.test_epoch_end:
            _test_epoch_end = old_bitfount_model_cls.test_epoch_end

        def __new__(cls, *args: Any, **kwargs: Any) -> Self:
            return cast(Self, super().__new__(cls))

        def __getattribute__(self, name: str) -> Any:
            # Explicitly remove disallowed methods from the derived instance
            if name in _METHODS_TO_REMOVE_IN_V2:
                raise AttributeError(
                    f"Method '{name}' is not available in"
                    f" PyTorch Lightning v2 derived class instances."
                )
            return super().__getattribute__(name)

        def __repr__(self) -> str:
            # Change repr string for class instance so that it contains information
            # about the converted class where possible
            # Original is of the form:
            # <{module}.{qualname} object at {hex(id(instance))>
            cls = type(self)
            return (
                f"<"
                f"{cls.__module__}.{cls.__qualname__}"
                f" (converted from"
                f" {cls.__converted_cls_module__}.{cls.__converted_cls_qualname__}"
                f")"
                f" object at {hex(id(self))}"
                f">"
            )

    # Remove PyTorchBitfountModel from bases if present
    Converted.__bases__ = tuple(
        base for base in Converted.__bases__ if base is not PyTorchBitfountModel
    )

    # DEV: Known Limitations
    # Due to how ABCMeta performs issubclass() and isinstance() checks (basically by
    # checking, recursively, if a class is a subclass or a subclass of a subclass of
    # the abstract class), this converted class will still, "incorrectly",
    # pass issubclass(Converted, PyTorchBifountModel) and a similar isinstance check.
    return Converted


@overload
def maybe_convert_bitfount_model_class_to_v2(
    model_cls: type[PyTorchBitfountModel[T_DTYPE]],
) -> type[PyTorchBitfountModelv2[T_DTYPE]]: ...


@overload
def maybe_convert_bitfount_model_class_to_v2(
    model_cls: type[BitfountModel],
) -> type[BitfountModel]: ...


def maybe_convert_bitfount_model_class_to_v2(
    model_cls: type[BitfountModel] | type[PyTorchBitfountModel[T_DTYPE]],
) -> type[BitfountModel] | type[PyTorchBitfountModelv2[T_DTYPE]]:
    """If model_cls is a PyTorchBitfountModel, convert to PyTorchBitfountModelv2."""
    # DEV: We need to do the main import here to avoid circular import issues. By the
    #      nature of this function it will be called in places elsewhere in the
    #      codebase and reaches down into the pytorch packages, increasing the
    #      likelihood of circular imports massively.
    from bitfount.backends.pytorch.models.bitfount_model import (
        PyTorchBitfountModel,
    )

    if issubclass(model_cls, PyTorchBitfountModel) and not hasattr(
        model_cls, "__converted_cls_name__"
    ):
        return convert_bitfount_model_class_to_v2(model_cls)
    else:
        return model_cls
