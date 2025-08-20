"""Contains the base classes for handling custom models."""

from __future__ import annotations

from abc import ABC, abstractmethod
import os
from typing import Any, Optional, Union

from bitfount.models.base_models import _BaseModel
from bitfount.utils import _get_object_source_code, delegates


# This class must implement `DistributedModelProtocol` but cannot inherit from it for
# two reasons:
# 1. Pytorch lightning does not like this for some reason and throws an error in the
# `PyTorchBitfountModel` subclass:
#   "AttributeError: cannot assign module before Module.__init__() call"
# 2. If this inherits from `DistributedModelProtocol`, mypy does not ensure that an
# implementation actually implements the protocol. As a result, we have to do an
# `isinstance` check which will always return `True` if the protocol is part of the
# hierarchy regardless of whether the implementation actually implements the protocol.
@delegates()
class BitfountModel(_BaseModel, ABC):
    """Base class for custom models which must implement `DistributedModelProtocol`.

    A base tagging class to highlight custom models which are designed to be uploaded to
    Bitfount Hub.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.class_name = type(self).__name__  # overrides _BaseModel attribute

    @staticmethod
    @abstractmethod
    def _get_import_statements() -> list[str]:
        """Returns a list of import statements likely to be required for the model.

        These are likely to be backend-specific so this method is left to be implemented
        by the subclass.

        Returns:
            A list of import statements.
        """
        raise NotImplementedError

    @classmethod
    def serialize_model_source_code(
        cls,
        filename: Union[str, os.PathLike],
        extra_imports: Optional[list[str]] = None,
    ) -> None:
        """Serializes the source code of the model to file.

        This is required so that the model source code can be uploaded to Bitfount Hub.

        Args:
            filename: The filename to save the source code to.
            extra_imports: A list of extra import statements to include in the source
                code.
        """
        source = _get_object_source_code(cls)
        all_imports = cls._get_import_statements()
        if extra_imports is not None:
            all_imports += extra_imports
        with open(filename, "w") as f:
            for import_ in all_imports:
                f.write(import_ + "\n")
            f.write(source)

        # Remove unused imports. It is recommended that `ruff` be used
        # to format the source code after `autoimport` is used.
        # Security warnings ignored because these are only run on the user's own machine
        os.system(  # nosec start_process_with_a_shell # Reason: See above
            f"autoimport {str(filename)} > /dev/null 2>&1"  # Suppress stdout and stderr
        )

        # Format the source code
        # Security warnings ignored because these are only run on the user's own machine
        os.system(  # nosec start_process_with_a_shell # Reason: See above
            f"ruff format {str(filename)} > /dev/null 2>&1"  # Suppress stdout and stderr  # noqa: E501
        )
