"""Shims to allow compat between different PyTorch/Lightning versions."""

from __future__ import annotations

from collections.abc import Callable
import logging
import os
from typing import IO, Any, BinaryIO, Optional, Union

from packaging.version import Version, parse as version_parse
import pytorch_lightning
from pytorch_lightning.loggers import Logger as LightningLoggerBase  # noqa: F401
import torch
from torch.types import Storage
from typing_extensions import TypeAlias

# These are backported from torch.serialization.py v2.5.0+
FILE_LIKE: TypeAlias = Union[str, os.PathLike, BinaryIO, IO[bytes]]
MAP_LOCATION: TypeAlias = Optional[
    Union[Callable[[Storage, str], Storage], torch.device, str, dict[str, str]]
]

_TORCH_VERSION: Version = version_parse(torch.__version__)
_LIGHTNING_VERSION: Version = version_parse(pytorch_lightning.__version__)


_logger = logging.getLogger(__name__)


# This signature matches torch.load() from v1.13+
def torch_load(
    f: FILE_LIKE,
    map_location: MAP_LOCATION = None,
    pickle_module: Any = None,
    *,
    weights_only: bool = True,
    **pickle_load_args: Any,
) -> Any:
    """See torch.load() (>=1.13) for documentation."""
    if not weights_only:
        _logger.warning(
            f"The weights_only argument is currently {weights_only}."
            f" Ensure that what is being loaded in this `torch_load()` call"
            f" is from a trusted source."
        )
    return torch.load(  # nosec[pytorch_load] # See logging above; most pathways are weight_only=True enforced # noqa: E501
        f,
        map_location,
        pickle_module,
        weights_only=weights_only,
        **pickle_load_args,
    )
