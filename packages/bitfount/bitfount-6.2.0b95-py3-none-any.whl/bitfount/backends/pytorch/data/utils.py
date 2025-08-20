"""PyTorch data utility functions to be found here."""

from __future__ import annotations

from collections.abc import Sequence
import logging
from typing import Any, Union

import numpy as np
import torch

from bitfount.data.types import SingleOrMulti, _DataBatch

DEFAULT_BUFFER_SIZE: int = 1000

logger = logging.getLogger(__name__)


def _index_tensor_handler(
    idx: Union[int, Sequence[int], torch.Tensor],
) -> Union[int, Sequence[int]]:
    """Converts pytorch tensors to integers or lists of integers for indexing."""
    if torch.is_tensor(idx):
        list_idx: list = idx.tolist()
        return list_idx
    else:
        return idx


def _convert_batch_to_tensor(
    batch: _DataBatch,
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
        tensor_list = []
        try:
            for j in range(len(list_of_x_elements)):
                tensor = torch.tensor(list_of_x_elements[j], dtype=torch.float32)
                tensor_list.append(tensor)
            x.append(torch.stack(tensor_list))
        # A value error is raised if list elements are of different shapes. This happens
        # for instance when not all images in the array have the same shapes.
        except ValueError:
            images_list = []
            for img_num in range(len(list_of_x_elements[0])):
                # Convert to float32 to avoid errors when converting to tensor.
                # This can happen if the numpy array is of type uint16 which
                # is not supported for torch.tensors. It should not have an
                # impact on the output as the tensor is converted to that dtype.
                # See below:
                # https://discuss.pytorch.org/t/doubt-with-torch-from-numpy-with-uint16-and-how-to-tensor-manage-these-kinds-of-images/86410 #noqa:E501
                stacked = torch.stack(
                    [
                        (
                            torch.tensor(batch_item[img_num], dtype=torch.float32)
                            if not batch_item[img_num].dtype == np.uint16
                            else torch.tensor(
                                batch_item[img_num].astype(np.float32),
                                dtype=torch.float32,
                            )
                        )
                        for batch_item in list_of_x_elements
                    ]
                )
                images_list.append(stacked)
            x.append(images_list)
        # A type error is raised if we try to convert a list of strings to tensor.
        # This happens in the case of algorithms requiring text input.
        except TypeError:
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
