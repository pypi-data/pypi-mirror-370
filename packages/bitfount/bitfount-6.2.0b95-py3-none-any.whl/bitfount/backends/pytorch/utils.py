"""Contains PyTorch specific utility methods."""

from __future__ import annotations

from functools import lru_cache
import logging
from typing import Any

import torch

from bitfount import config
from bitfount.backends.pytorch._torch_shims import FILE_LIKE, MAP_LOCATION, torch_load
from bitfount.config import (
    get_cuda_metadata_pytorch,
    has_cuda,
    has_mps,
)
from bitfount.types import _StrAnyDict

logger = logging.getLogger(__name__)

# The keys in this dictionary match the return type of `pl.Trainer.precision`
# _PRECISION_INPUT_STR = Literal[
#     "transformer-engine",
#     "transformer-engine-float16",
#     "16-true",
#     "16-mixed",
#     "bf16-true",
#     "bf16-mixed",
#     "32-true",
#     "64-true",
# ]
_TORCH_DTYPES: dict[str, torch.dtype] = {
    # bf16
    "bf16": torch.bfloat16,
    "bf16-true": torch.bfloat16,
    "bf16-mixed": torch.bfloat16,
    # 16
    "16": torch.float16,
    "16-true": torch.float16,
    "16-mixed": torch.float16,
    # 32
    "32": torch.float32,
    "32-true": torch.float32,
    # 64
    "64": torch.float64,
    "64-true": torch.float64,
}


@lru_cache(maxsize=1)
def autodetect_gpu() -> _StrAnyDict:
    """Detects and returns GPU accelerator and device count.

    Returns:
        A dictionary with the keys 'accelerator' and 'devices' which should be passed
        to the PyTorchLightning Trainer.
    """
    if has_mps():
        return {"accelerator": "mps", "devices": 1}

    else:
        # Run on GPU if available
        gpu_0_name, gpus = get_cuda_metadata_pytorch()
        if gpu_0_name is not None and gpus > 0:
            # Reduce to 1 GPU if multiple detected
            # TODO: [BIT-492] Add multi-GPU support.
            if gpus > 1:
                logger.warning(
                    f"Bitfount model currently only supports one GPU. "
                    f"Will use GPU 0 ({gpu_0_name})."
                )
                gpus = 1
            return {"accelerator": "gpu", "devices": 1}

    return {"accelerator": "cpu", "devices": "auto"}


# This signature matches torch.load() from v1.13+
def enhanced_torch_load(
    f: FILE_LIKE,
    map_location: MAP_LOCATION = None,
    pickle_module: Any = None,
    *,
    weights_only: bool = True,
    **pickle_load_args: Any,
) -> Any:
    """Call `torch.load()` with sensible parameters.

    See the docs of `torch.load()` for more information.
    """
    # If not explicitly specified, and we have a default device set, use that
    if not map_location and (default_device := config.settings.default_torch_device):
        logger.debug(f'Setting torch.load() device to "{default_device}"')
        map_location = default_device

    try:
        # First try just loading as requested
        return torch_load(
            f,
            map_location,
            pickle_module,
            weights_only=weights_only,
            **pickle_load_args,
        )
    except Exception as e:
        # we use a broad exception clause here because there are myriad exceptions
        # that could be thrown in torch.load() or the chosen "pickle_module"; easier
        # to capture them, log them, then try the next option
        warning_msg = "Error whilst trying to load model"
        if map_location:
            warning_msg += f" with map_location={map_location}"
        warning_msg += f': "{str(e)}"'
        logger.warning(warning_msg)

        # See what alternative devices we have available to map the model to
        potential_devices = ["cpu"]
        if has_mps():
            potential_devices.append("mps")
        if has_cuda():
            # Append the default/current CUDA device
            potential_devices.append("cuda")

        # Want them in reverse order to prioritise GPU over CPU
        potential_devices.reverse()
        for device in potential_devices:
            # Kept as warning as this whole flow is WARNING
            logger.warning(f"Trying to load model on {device} device...")
            try:
                # If f is not a file path, but a stream of some description, then
                # we'll need to reset it
                try:
                    f.seek(0)  # type: ignore[union-attr] # Reason: failure captured
                    logger.debug(
                        "Reset model stream to position 0 to retry torch.load()"
                    )
                except AttributeError:
                    pass

                loaded = torch_load(
                    f,
                    device,
                    pickle_module,
                    weights_only=weights_only,
                    **pickle_load_args,
                )
            except Exception as e2:
                logger.warning(f'Error loading model on {device} device: "{str(e2)}"')
                continue
            else:
                # Kept as warning as this whole flow is WARNING
                logger.warning(f"Successfully loaded model on {device} device")
                return loaded
        else:
            raise RuntimeError(
                f"Unable to load model as requested,"
                f" or on any of these alternative devices:"
                f" {', '.join(potential_devices)}"
            ) from e
