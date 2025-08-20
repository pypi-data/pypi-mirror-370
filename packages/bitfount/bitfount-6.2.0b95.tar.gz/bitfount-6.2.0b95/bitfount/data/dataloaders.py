"""Classes concerning data loading and dataloaders."""

from __future__ import annotations

from collections.abc import Iterator
import math
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from bitfount.data.datasets import _BaseBitfountDataset
    from bitfount.data.types import SingleOrMulti


class BitfountDataLoader:
    """A backend-agnostic data loader.

    Args:
        dataset: The dataset for the dataloader.
        batch_size: The batch size for the dataloader.
            Defaults to None.
    """

    def __init__(
        self,
        dataset: _BaseBitfountDataset,
        batch_size: Optional[int] = None,
        shuffle: bool = False,
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle

    def __len__(self) -> int:
        """Number of batches or number of elements if batch size is None."""
        if not self.batch_size:
            return len(self.dataset)
        return math.ceil(len(self.dataset) / self.batch_size)

    def __iter__(self) -> Iterator[list[SingleOrMulti[Any]]]:
        """This should be implemented to allow batch by batch loading.

        Currently, there are no backend-agnostic models that can operate on iterable
        datasets, so it has not been implemented.

        Returns:
            An iterator over batches of x and y numpy arrays.
        """
        raise NotImplementedError
