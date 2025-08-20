"""HuggingFace compatible dataloaders."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
import logging
import math
import random
import secrets
from typing import Any, Union, cast

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    import torch
    from torch.utils.data import DataLoader as PyTorchDataLoader

from bitfount.backends.pytorch import DEFAULT_BUFFER_SIZE
from bitfount.backends.pytorch.data.utils import _convert_batch_to_tensor
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasets import _IterableBitfountDataset
from bitfount.data.huggingface.datasets import (
    _FileIterableHuggingFaceDataset,
    _IterableHuggingFaceDataset,
)
from bitfount.data.types import (
    SingleOrMulti,
    _DataBatch,
    _DataBatchAllowingText,
    _DataBatchAllowingTextWithKey,
    _DataEntryAllowingTextWithKey,
    _HFSegmentation_ImageTextEntry,
    _HFSegmentation_ImageTextEntryWithKey,
)
from bitfount.utils import delegates

_logger = logging.getLogger(__name__)


class _BaseHuggingFaceBitfountDataLoader(BitfountDataLoader):
    """Base class for HuggingFace-specific Bitfount DataLoaders.

    Args:
       dataset: An huggingface compatible dataset.
       batch_size: The batch size for the dataloader.
           Defaults to 1.
       shuffle: A boolean value indicating whether the values
           in the dataset should be shuffled. Defaults to False.

    Attributes:
       dataset: An huggingface compatible dataset.
       batch_size: The batch size for the dataloader.
           Defaults to 1.
       shuffle: A boolean value indicating whether the values
           in the dataset should be shuffled. Defaults to False.
    """

    def __init__(
        self,
        dataset: _IterableHuggingFaceDataset,
        batch_size: int = 1,
        shuffle: bool = False,
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle


@delegates()
class HuggingFaceBitfountDataLoader(_BaseHuggingFaceBitfountDataLoader):
    """Wraps a PyTorch DataLoader with bitfount functions.

    Args:
       dataset: An pytorch compatible dataset.
    """

    def __init__(
        self,
        dataset: _IterableHuggingFaceDataset,
        batch_size: int = 1,
        shuffle: bool = False,
        **kwargs: Any,
    ):
        self.dataset = dataset
        super().__init__(dataset=dataset, batch_size=batch_size, shuffle=shuffle)
        self.dataloader = self._get_pytorch_dataloader()

    def _get_pytorch_dataloader(self, **kwargs: Any) -> PyTorchDataLoader:
        """Return a PyTorch DataLoader for `self.dataset`.

        Keyword arguments are passed to PyTorch's DataLoader constructor and take
        precedence over the values set in the constructor.
        """
        return PyTorchDataLoader(
            dataset=kwargs.pop("dataset", self.dataset),
            batch_size=kwargs.pop("batch_size", self.batch_size),
            shuffle=kwargs.pop("shuffle", self.shuffle),
            **kwargs,
        )

    def __len__(self) -> int:
        """Number of batches or number of elements if batch size is None."""
        return len(self.dataloader)

    def __iter__(
        self,
    ) -> Union[
        Iterator[list[SingleOrMulti[torch.Tensor]]],
        Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]],
    ]:
        """Wrapper around the default PyTorch DataLoader iterator.

        The only difference is that the elements of each batch are wrapped in a list.
        """
        if self.expect_key_in_iter():
            return self._with_key_iter()
        else:
            return self._no_key_iter()

    def _with_key_iter(
        self,
    ) -> Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]]:
        for batch in self.dataloader:
            yield [x for x in batch]

    def _no_key_iter(self) -> Iterator[list[SingleOrMulti[torch.Tensor]]]:
        for batch in self.dataloader:
            yield [x for x in batch]

    def expect_key_in_iter(self) -> bool:
        """Will there be a data key entry in the output from iteration?"""
        return isinstance(self.dataset, _FileIterableHuggingFaceDataset)


@delegates()
class HuggingFaceIterableBitfountDataLoader(BitfountDataLoader):
    """Wraps a PyTorch DataLoader with bitfount functions.

    Args:
       dataset: An HuggingFace compatible dataset.
    """

    dataset: _IterableHuggingFaceDataset

    def __init__(
        self,
        dataset: _IterableBitfountDataset,
        batch_size: int = 1,
        shuffle: bool = False,
        secure_rng: bool = False,
        **kwargs: Any,
    ):
        # _PytorchIterableDataset is a wrapper around of
        # _IterableBitfountDataset so this cast is safe.
        dataset = cast(_IterableHuggingFaceDataset, dataset)
        super().__init__(dataset=dataset, batch_size=batch_size, shuffle=shuffle)
        self.secure_rng = secure_rng
        self.batch_size = batch_size
        self.shuffle = shuffle

    @property
    def buffer_size(self) -> int:
        """Number of elements to buffer.

        The size of the buffer is the greater of the batch size and default buffer size
        unless the dataset is smaller than the default buffer in which case the dataset
        size is used. PyTorch already ensures that the batch size is not greater than
        the dataset size under the hood.
        """
        # Batch size is optional in the core hierarchy but in pytorch we ensure it is
        # set to 1 if not provided. Re-assuring mypy of this.
        assert self.batch_size is not None  # nosec assert_used
        return max(min(len(self.dataset), DEFAULT_BUFFER_SIZE), self.batch_size)

    def __len__(self) -> int:
        """Number of batches in the dataset."""
        assert self.batch_size is not None  # nosec assert_used
        return math.ceil(len(self.dataset) / self.batch_size)

    @staticmethod
    def convert_input_target(
        batch: _DataBatchAllowingText,
    ) -> list[SingleOrMulti[torch.Tensor]]:
        """Convert the input and target to match the hugging face expected inputs_."""
        # TODO: [BIT-3851] tidy this up properly
        if len(batch[0]) == 3:
            # TODO: [BIT-3851] is this broken anyway? It only returns the first
            #       entry in the batch?

            #  This only happens for the image segmentation case where we
            #  return images, text and target
            input_aux, text_aux, target_aux = cast(
                _HFSegmentation_ImageTextEntry, batch[0]
            )
            text_ = cast(torch.Tensor, text_aux)
            batch_ = input_aux, target_aux
            input_, target_ = _convert_batch_to_tensor([batch_])
            if isinstance(input_, list):
                # Try to combine the input_ tensors into a single tensor, but if that
                # doesn't work, leave it as a list
                try:
                    input_ = torch.stack(input_)
                except RuntimeError as re:
                    _logger.warning(re)
                else:
                    input_ = torch.swapaxes(input_, 0, 1)
            return [input_, text_, target_]
        else:
            input_, target_ = _convert_batch_to_tensor(cast(_DataBatch, batch))
            if isinstance(input_, list):
                # Try to combine the input_ tensors into a single tensor, but if that
                # doesn't work, leave it as a list
                try:
                    input_ = torch.stack(input_)
                except RuntimeError as re:
                    _logger.warning(re)
                except TypeError:
                    _logger.debug(
                        """TypeError in convert_input_target,
                        most likely a text element in the batch"""
                    )
                else:
                    input_ = torch.swapaxes(input_, 0, 1)
            return [input_, target_]

    @staticmethod
    def convert_input_target_key(
        batch: _DataBatchAllowingTextWithKey,
    ) -> list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]:
        """Convert the input and target to match the hugging face expected inputs_.

        Ensures that the data key is also passed through to the output.
        """
        # TODO: [BIT-3851] tidy this up properly
        if len(batch[0]) == 4:
            # TODO: [BIT-3851] is this broken anyway? It only returns the first
            #       entry in the batch?

            # This only happens for the image segmentation case
            # where we return images, text, target, and key
            input_aux, text_aux, target_aux, key = cast(
                _HFSegmentation_ImageTextEntryWithKey, batch[0]
            )
            text_ = cast(torch.Tensor, text_aux)
            input_, target_ = _convert_batch_to_tensor([(input_aux, target_aux)])
            if isinstance(input_, list):
                # Try to combine the input_ tensors into a single tensor, but if that
                # doesn't work, leave it as a list
                try:
                    input_ = torch.stack(input_)
                except RuntimeError as re:
                    _logger.warning(re)
                else:
                    input_ = torch.swapaxes(input_, 0, 1)
            return [input_, text_, target_, key]
        else:
            # Batch is a list of "data entries", where the last element of each
            # entry will be the key; need to extract those into an independent
            # list so that we can then pair it up again later
            batch_: list = []
            keys: list[str] = []
            for entry in batch:
                batch_.append(entry[:-1])
                keys.append(entry[-1])

            input_, target_ = _convert_batch_to_tensor(cast(_DataBatch, batch_))
            if isinstance(input_, list):
                # Try to combine the input_ tensors into a single tensor, but if that
                # doesn't work, leave it as a list
                try:
                    input_ = torch.stack(input_)
                except RuntimeError as re:
                    _logger.warning(re)
                except TypeError:
                    _logger.debug(
                        """TypeError in convert_input_target_key,
                        most likely a text element in the batch"""
                    )
                else:
                    input_ = torch.swapaxes(input_, 0, 1)
            return [input_, target_, keys]

    def __iter__(
        self,
    ) -> Union[
        Iterator[list[SingleOrMulti[torch.Tensor]]],
        Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]],
    ]:
        """Yields a batch of data when iterated.

        We use a custom iterator with different behaviour depending on whether the
        dataset should be shuffled or not. Each batch is explicitly converted to torch
        tensors prior to yielding as this is not done automatically by pytorch.
        """
        if self.expect_key_in_iter():
            return self._with_key_iter()
        else:
            return self._no_key_iter()

    def _get_random_buffer_idx(self) -> int:
        """Return a random index inside a buffer."""
        if self.secure_rng:
            idx = secrets.randbelow(self.buffer_size)
        else:
            # Ignoring security warning here because RNG does not need
            # to be cryptographically secure if it is turned off by
            # the user.
            idx = random.randint(0, self.buffer_size - 1)  # nosec B311 # "random" usage
        return idx

    def _with_key_iter(
        self,
    ) -> Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]]:
        batch: _DataBatchAllowingTextWithKey = []

        # If we are in this method, we know that self.dataset is
        # _FileIterableHuggingFaceDataset and will return a type of
        # _DataEntryAllowingTextWithKey in its iteration
        sample: _DataEntryAllowingTextWithKey
        if self.shuffle:
            # If the dataset should be shuffled, we use a reservoir sampling method
            # to sample from a buffer of elements from the dataset.
            buffer_: _DataBatchAllowingTextWithKey = []
            for sample in cast(Iterator[_DataEntryAllowingTextWithKey], self.dataset):
                if len(batch) == self.batch_size:
                    yield self.convert_input_target_key(batch)
                    batch = []

                if len(buffer_) == self.buffer_size:
                    idx = self._get_random_buffer_idx()
                    batch.append(buffer_[idx])
                    buffer_[idx] = sample
                else:
                    buffer_.append(sample)

            # This is only reached once the dataset iterator has been exhausted. The
            # remainder of the buffer is shuffled and yielded until empty.
            random.shuffle(buffer_)
            while buffer_:
                if len(batch) == self.batch_size:
                    yield self.convert_input_target_key(batch)
                    batch = []

                batch.append(buffer_.pop())
        else:
            # If the dataset should not be shuffled, we simply iterate over the dataset
            for sample in cast(Iterator[_DataEntryAllowingTextWithKey], self.dataset):
                if len(batch) == self.batch_size:
                    yield self.convert_input_target_key(batch)
                    batch = []

                batch.append(sample)

        # If there are any elements left in the batch after the dataset/buffer are
        # empty, yield an incomplete batch.
        if batch:
            yield self.convert_input_target_key(batch)

    def _no_key_iter(self) -> Iterator[list[SingleOrMulti[torch.Tensor]]]:
        batch: _DataBatchAllowingText = []

        if self.shuffle:
            # If the dataset should be shuffled, we use a reservoir sampling method
            # to sample from a buffer of elements from the dataset.
            buffer_: _DataBatchAllowingText = []
            for sample in self.dataset:
                if len(batch) == self.batch_size:
                    yield self.convert_input_target(batch)
                    batch = []

                if len(buffer_) == self.buffer_size:
                    idx = self._get_random_buffer_idx()
                    batch.append(buffer_[idx])
                    buffer_[idx] = sample
                else:
                    buffer_.append(sample)

            # This is only reached once the dataset iterator has been exhausted. The
            # remainder of the buffer is shuffled and yielded until empty.
            random.shuffle(buffer_)
            while buffer_:
                if len(batch) == self.batch_size:
                    yield self.convert_input_target(batch)
                    batch = []

                batch.append(buffer_.pop())
        else:
            # If the dataset should not be shuffled, we simply iterate over the dataset
            for sample in self.dataset:
                if len(batch) == self.batch_size:
                    yield self.convert_input_target(batch)
                    batch = []

                batch.append(sample)

        # If there are any elements left in the batch after the dataset/buffer are
        # empty, yield an incomplete batch.
        if batch:
            yield self.convert_input_target(batch)

    def expect_key_in_iter(self) -> bool:
        """Will there be a data key entry in the output from iteration?"""
        return isinstance(self.dataset, _FileIterableHuggingFaceDataset)
