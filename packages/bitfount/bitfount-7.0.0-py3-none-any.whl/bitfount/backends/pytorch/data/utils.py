"""PyTorch data utility functions to be found here."""

from __future__ import annotations

import logging
from typing import Any, Union

import numpy as np
import torch

from bitfount.data.datasets import _BaseBitfountDataset
from bitfount.data.types import SingleOrMulti, _DataBatch

DEFAULT_BUFFER_SIZE: int = 1000

logger = logging.getLogger(__name__)


def _to_chw(arr: Union[np.ndarray, torch.Tensor]) -> torch.Tensor:
    """Convert an image array to a PyTorch tensor in channels-first format.

    Returns:
        A tensor in the Channels, Height, Width (CHW) format.
    """
    t = arr if isinstance(arr, torch.Tensor) else torch.tensor(arr)
    t = t.to(torch.float32)

    if t.ndim == 2:
        # (H, W) -> (1, H, W)
        return t.unsqueeze(0)

    if t.ndim == 3:
        # If channels-last, move to channels-first
        if t.shape[-1] in (1, 3, 4):
            t = t.permute(2, 0, 1)  # (C, H, W)
        # Otherwise assume already (C, H, W)
        return t

    raise ValueError(f"Unexpected image shape: {tuple(t.shape)}")


def _stack_images_as_list_BCHW(list_of_x_elements: list[Any]) -> list[torch.Tensor]:
    """Stack images from a list of elements into a list of tensors in BCHW format.

    Returns:
        A list of tensors, in the Batch, Channels, Height, Width format.
    """
    # Validate input - ensure we have samples to process
    if len(list_of_x_elements) == 0:
        raise ValueError("The list of elements is empty. Cannot stack images.")
    # Analyze the first sample to understand the frame structure
    # This tells us how many frames we need to process
    first_frames, num_frames, _ = _iter_frames(list_of_x_elements[0])
    images_list: list[torch.Tensor] = []
    # Process each frame position
    for frame_idx in range(num_frames):
        batch_frames: list[torch.Tensor] = []
        for sample in list_of_x_elements:
            frames, _, is_seq = _iter_frames(sample)
            # Handle variable-length sequences
            # If this sample has fewer frames than frame_idx, skip it
            if is_seq and frame_idx >= len(frames):
                continue
            # Determine which frame to use from this sample
            # For sequences: use frame at frame_idx
            # For single images: always use index 0
            idx = frame_idx if is_seq else 0
            frame = frames[idx]
            # Convert uint16 to float32 for PyTorch compatibility
            if isinstance(frame, np.ndarray) and frame.dtype == np.uint16:
                frame = frame.astype(np.float32)
            # Convert frame to CHW format and add to batch collection
            # _to_chw ensures consistent (Channels, Height, Width) format
            batch_frames.append(_to_chw(frame))
        images_list.append(torch.stack(batch_frames, dim=0))  # (B,C,H,W)

    return images_list


def _convert_batch_to_tensor(
    batch: _DataBatch,
    dataset: _BaseBitfountDataset | None = None,
) -> list[SingleOrMulti[torch.Tensor]]:
    """Converts a batch of data containing numpy arrays to torch tensors.

    Data must be explicitly converted to torch tensors since the PyTorch DataLoader
    which does this automatically is not being used.
    """
    x: list[Any] = []
    num_x_elements_per_batch = len(
        batch[0][0]
    )  # Subset of [tabular, images, supplementary]

    for i in range(num_x_elements_per_batch):
        list_of_x_elements = [sample[0][i] for sample in batch]

        # If this element is images, always use image path (single or multi-frame)
        if dataset is not None and hasattr(dataset, "image_columns"):
            has_tabular = (
                hasattr(dataset, "tabular")
                and getattr(dataset, "tabular", np.array([])).size > 0
            )
            has_images = len(dataset.image_columns) > 0
            is_image_elem = (has_tabular and has_images and i == 1) or (
                has_images and not has_tabular and i == 0
            )
            if is_image_elem:
                x.append(_stack_images_as_list_BCHW(list_of_x_elements))
                continue

        # Non-image (tabular/text) handling
        tensor_list = []
        try:
            for j in range(len(list_of_x_elements)):
                tensor = torch.tensor(list_of_x_elements[j], dtype=torch.float32)
                tensor_list.append(tensor)
            x.append(torch.stack(tensor_list))
        except ValueError:
            # A value error is raised if list elements are of different shapes.
            # This happens for instance when not all images in
            # the array have the same shapes.
            x.append(_stack_images_as_list_BCHW(list_of_x_elements))
        except TypeError:
            # A type error is raised if we try to convert a list of strings to tensor.
            # This happens in the case of algorithms requiring text input.
            x += list_of_x_elements
    try:
        y = torch.from_numpy(np.array([b[1] for b in batch]))
    except TypeError as e:
        logger.error(
            "It seems like the labels specified do not accurately match the "
            "actual labels in the data."
        )
        raise e
    return [x, y]


def _is_invalid_frame(x: Any) -> bool:
    """Check if the frame is invalid."""
    match x:
        case None:
            return True
        case float() if np.isnan(x):
            return True
        case list() | tuple() if len(x) == 0:
            return True
        case np.ndarray() if x.size == 0:
            return True
        case torch.Tensor() if x.numel() == 0:
            return True
        case str():
            return True
    return False


def _iter_frames(sample: Any) -> tuple[list[Any], int, bool]:
    """Iterate over frames in a sample.

    Returns a tuple of:
        - List of frames (valid frames only)
        - Number of valid frames
        - Whether the sample contains multiple frames
          (True if list/tuple, False if single frame)
    """
    # tuple/list of frames (filter invalid)
    if isinstance(sample, (list, tuple)):
        frames = [f for f in sample if not _is_invalid_frame(f)]
        return frames, len(frames), True
    # numpy object array holding frames (filter invalid)
    if isinstance(sample, np.ndarray) and sample.dtype == object:
        frames = [f for f in sample.tolist() if not _is_invalid_frame(f)]
        return frames, len(frames), True
    # single frame (ndarray/tensor)
    return [sample], 1, False
