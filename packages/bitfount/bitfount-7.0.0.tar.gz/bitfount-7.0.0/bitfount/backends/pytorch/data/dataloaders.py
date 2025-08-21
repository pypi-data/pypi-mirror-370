"""PyTorch-specific DataLoader implementations."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Sequence
import math
import random
import secrets
from typing import Any, Union, cast

import torch

from bitfount.backends.pytorch.data.datasets import (
    _PytorchFileIterableDataset,
    _PyTorchIterableDataset,
)
from bitfount.backends.pytorch.data.utils import (
    DEFAULT_BUFFER_SIZE,
    _convert_batch_to_tensor,
)
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasets import _IterableBitfountDataset
from bitfount.data.types import (
    SingleOrMulti,
    _DataBatch as _DataBatchNoKey,
    _DataBatchWithKey,
    _DataEntry as _DataEntryNoKey,
    _DataEntryWithKey,
    _ImageAndTabularEntry as _ImageAndTabularEntryNoKey,
    _ImageAndTabularEntryWithKey,
    _ImageEntry as _ImageEntryNoKey,
    _ImageEntryWithKey,
    _ImagesData,
    _Segmentation_ImageAndTabEntry as _Segmentation_ImageAndTabEntryNoKey,
    _Segmentation_ImageAndTabEntryWithKey,
    _Segmentation_ImageEntry as _Segmentation_ImageEntryNoKey,
    _Segmentation_ImageEntryWithKey,
    _SupportData,
    _TabularData,
)
from bitfount.utils import delegates

# These types are used to identify keyed data (i.e. those where there is an element
# that allows identifying where the data came from, such as filename), passing
# through the dataloaders from the dataset
_PTImageIterDataX = Union[
    # _ImageEntry or _Segmentation_ImageEntry, with support data
    tuple[_ImagesData, _SupportData],
    # _ImageEntry or _Segmentation_ImageEntry, no support data
    _ImagesData,
    # _ImageAndTabularEntry or _Segmentation_ImageAndTabEntry, with support data
    tuple[_TabularData, _ImagesData, _SupportData],
    # _ImageAndTabularEntry or _Segmentation_ImageAndTabEntry, no support data
    tuple[_TabularData, _ImagesData],
]

_PTImageIterDataEntryNoKey = Union[
    _ImageEntryNoKey,
    _ImageAndTabularEntryNoKey,
    _Segmentation_ImageEntryNoKey,
    _Segmentation_ImageAndTabEntryNoKey,
]
_PTImageIterDataBatchNoKey = list[_PTImageIterDataEntryNoKey]

_PTImageIterDataEntryWithKey = Union[
    _ImageEntryWithKey,
    _ImageAndTabularEntryWithKey,
    _Segmentation_ImageEntryWithKey,
    _Segmentation_ImageAndTabEntryWithKey,
]
_PTImageIterDataBatchWithKey = list[_PTImageIterDataEntryWithKey]


class _BasePyTorchBitfountDataLoader(BitfountDataLoader):
    """Base class for PyTorch-specific Bitfount DataLoaders.

    Args:
       dataset: An pytorch compatible dataset.
       batch_size: The batch size for the dataloader.
           Defaults to 1.
       shuffle: A boolean value indicating whether the values
           in the dataset should be shuffled. Defaults to False.

    Attributes:
       dataset: An pytorch compatible dataset.
       batch_size: The batch size for the dataloader.
           Defaults to 1.
       shuffle: A boolean value indicating whether the values
           in the dataset should be shuffled. Defaults to False.
    """

    def __init__(
        self,
        dataset: Union[_PyTorchIterableDataset],
        batch_size: int = 1,
        shuffle: bool = False,
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.secure_rng = False  # not used for non-iterable dataloader

    @property
    def buffer_size(self) -> int:
        """Number of elements to buffer.

        The size of the buffer is the greatest of the batch size and default buffer size
        unless the dataset is smaller than the default buffer in which case the dataset
        size is used. PyTorch already ensures that the batch size is not greater than
        the dataset size under the hood.
        """
        # Batch size is optional in the core hierarchy but in pytorch we ensure it is
        # set to 1 if not provided. Re-assuring mypy of this.
        assert self.batch_size is not None  # nosec assert_used
        return max(min(len(self.dataset), DEFAULT_BUFFER_SIZE), self.batch_size)

    def _data_entry_contains_multi_imgs(self) -> bool:
        """True iff the data entries will contain multiple images per entry.

        If there are multiple image_columns in the dataset, this means there are
        multiple images per row/data entry.
        """
        return len(self.dataset.image_columns) > 1

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

    def _image_iter(self) -> Iterator[list[SingleOrMulti[torch.Tensor]]]:
        """Iteration method that handles data with images in it.

        Handles shuffling, matching number of frames together, etc.
        """
        # [DEV]: A number of these methods could probably be combined with some
        # clever type handling. They have currently been left separate for ease.

        # If there are images, we need to handle missing frames
        if not self.shuffle:
            yield from self._unshuffled_image_iter()
        else:
            yield from self._shuffled_image_iter()

    def _unshuffled_image_iter(self) -> Iterator[list[SingleOrMulti[torch.Tensor]]]:
        """Image dataset iteration."""
        # [DEV]: A number of these methods could probably be combined with some
        # clever type handling. They have currently been left separate for ease.

        buffer: _PTImageIterDataBatchNoKey = []

        # If we are in this method, we know that self.dataset is a _PyTorchDataset
        # but NOT _PytorchFileIterableDataset and that we are working with images.
        # In any case, this will return a type of _PTImageIterDataEntryNoKey in
        # its iteration.
        sample: _PTImageIterDataEntryNoKey
        for sample in cast(Iterator[_PTImageIterDataEntryNoKey], self.dataset):
            # Get the number of elements for each sample
            # Can be either (tabular, images,  supplementary) or (images,
            # supplementary).
            # Note that all samples in the dataset will have the same number of
            # elements per sample.
            sample_x, num_x_elements_per_sample = (
                self._get_and_validate_image_iter_sample_x(sample)
            )

            # If batch is empty, add the sample to them
            if len(buffer) == 0:
                buffer.append(sample)
            else:
                # Otherwise get the last sample from the batch_buffer
                prev_sample_x: _PTImageIterDataX = buffer[-1][0]

                # Establish the number of frames for the current and previous sample
                if num_x_elements_per_sample == 3:  # (tabular, images, supplementary)
                    number_of_frames_current_sample = len(sample_x[1])
                    number_of_frames_previous_sample = len(prev_sample_x[1])
                else:  # num_x_elements_per_sample == 2 # (images, supplementary)
                    number_of_frames_current_sample = len(sample_x[0])
                    number_of_frames_previous_sample = len(prev_sample_x[0])

                # Check if the number of frames is the same for the current and
                # previous sample, as we need to handle them differently:
                #   - if same: just add to the existing buffer
                #   - if diff: yield the current buffer (so batch has samples that
                #       are all the same number of frames), start new buffer for
                #       this new number of frames
                if number_of_frames_current_sample == number_of_frames_previous_sample:
                    buffer.append(sample)

                    # If the batch is full, yield it and then clear it
                    if len(buffer) == self.batch_size:
                        yield self._convert_input_target(buffer)
                        buffer.clear()
                else:
                    # otherwise, yield the current batch_buffer and
                    # start a new one with the current sample
                    yield self._convert_input_target(buffer)
                    buffer = [sample]

        # If there are any elements left in the batch after the
        # last iteration, yield them
        if buffer:
            yield self._convert_input_target(buffer)

    def _shuffled_image_iter(self) -> Iterator[list[SingleOrMulti[torch.Tensor]]]:
        """Image dataset iteration, shuffled."""
        # [DEV]: A number of these methods could probably be combined with some
        # clever type handling. They have currently been left separate for ease.

        # If the dataset should be shuffled, we use a reservoir sampling method to
        # sample from a buffer of elements from the dataset. We also have to group
        # samples with the same shapes for images within a same batch.
        #
        # `buffer_per_num_frames` and `batch_per_num_frames` are thus both mappings:
        #   "number of frames" -> "list of samples with that number of frames"
        batch_per_num_frames: defaultdict[int, _PTImageIterDataBatchNoKey] = (
            defaultdict(list)
        )
        buffer_per_num_frames: defaultdict[int, _PTImageIterDataBatchNoKey] = (
            defaultdict(list)
        )

        # If we are in this method, we know that self.dataset is a _PyTorchDataset
        # but NOT _PytorchFileIterableDataset and that we are working with images.
        # In any case, this will return a type of _PTImageIterDataEntryNoKey in
        # its iteration.
        sample: _PTImageIterDataEntryNoKey
        for sample in cast(Iterator[_PTImageIterDataEntryNoKey], self.dataset):
            # Get the number of elements for each sample
            # Should be either (tabular, images, supplementary) or
            # (images, supplementary).
            # Note that all samples in the dataset will have the same number
            # of elements per sample.
            sample_x, num_x_elements_per_sample = (
                self._get_and_validate_image_iter_sample_x(sample)
            )

            # Establish the number of frames this sample represents
            if num_x_elements_per_sample == 3:  # (tabular, images, supplementary)
                number_of_frames = len(sample[0][1])
            else:  # num_x_elements_per_sample == 2 # (images, supplementary)
                number_of_frames = len(sample[0][0])

            # If the buffer is full, we can then create a batch
            if (
                len(buffer := buffer_per_num_frames[number_of_frames])
                == self.buffer_size
            ):
                # If the batch is of the appropriate size, yield and reset
                if len(batch_per_num_frames[number_of_frames]) == self.batch_size:
                    yield self._convert_input_target(
                        batch_per_num_frames[number_of_frames]
                    )
                    batch_per_num_frames[number_of_frames] = []

                # Take an element (at random) from the buffer and transfer it to the
                # batch. Replace the removed element in the buffer with the current
                # sample.
                idx = self._get_random_buffer_idx()
                batch_per_num_frames[number_of_frames].append(buffer[idx])
                buffer[idx] = sample
                buffer_per_num_frames[number_of_frames] = buffer
            # Otherwise, just add the sample to the buffer
            else:
                buffer_per_num_frames[number_of_frames].append(sample)

        # This is only reached once the dataset iterator has been exhausted. The
        # remainder of the buffer is shuffled and yielded until empty.
        for key in buffer_per_num_frames.keys():
            buffer = buffer_per_num_frames[key]
            random.shuffle(buffer)

            # Add elements from the buffer to the batch, yielding as we create full
            # batches
            batch: _PTImageIterDataBatchNoKey = batch_per_num_frames[key]
            while buffer:
                if len(batch) == self.batch_size:
                    yield self._convert_input_target(batch)
                    batch = []

                batch.append(buffer.pop())

            # If there are any elements left in the batch after the
            # dataset/buffer are empty, yield an incomplete batch.
            if len(batch) > 0:
                yield self._convert_input_target(batch)

    def _image_iter_with_key(
        self,
    ) -> Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]]:
        """Iteration method that handles data with images in it and data keys.

        Handles shuffling, matching number of frames together, etc. Ensures that the
        "keys" (i.e. the original file name for each image) is passed through.
        """
        # [DEV]: A number of these methods could probably be combined with some
        # clever type handling. They have currently been left separate for ease.

        # If there are images, we need to handle missing frames
        if not self.shuffle:
            yield from self._unshuffled_image_iter_with_key()
        else:
            yield from self._shuffled_image_iter_with_key()

    def _unshuffled_image_iter_with_key(
        self,
    ) -> Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]]:
        """Image dataset iteration, with data keys."""
        # [DEV]: A number of these methods could probably be combined with some
        # clever type handling. They have currently been left separate for ease.

        # Should be either (tabular, images, supplementary) or
        # (images, supplementary).
        # Note that all samples in the dataset will have the same number
        # of elements per sample.
        sample_x: _PTImageIterDataX
        num_x_elements_per_sample: int

        buffer: _PTImageIterDataBatchWithKey = []

        # If we are in this method, we know that self.dataset is either
        # _PytorchFileIterableDataset and that we are working with images.
        # In either case, this will return a type of _PTImageIterDataEntryWithKey
        # in its iteration.
        sample: _PTImageIterDataEntryWithKey
        for sample in cast(Iterator[_PTImageIterDataEntryWithKey], self.dataset):
            # Get the number of X elements for each sample.
            sample_x, num_x_elements_per_sample = (
                self._get_and_validate_image_iter_sample_x(sample)
            )

            # If batch is empty, add the sample to them
            if len(buffer) == 0:
                buffer.append(sample)
            else:
                # Otherwise get the last sample from the buffer
                prev_sample_x: _PTImageIterDataX = buffer[-1][0]

                # Establish the number of frames for the current and previous sample
                if num_x_elements_per_sample == 3:  # (tabular, images, supplementary)
                    number_of_frames_current_sample = len(sample_x[1])
                    number_of_frames_previous_sample = len(prev_sample_x[1])
                else:  # num_x_elements_per_sample == 2 # (images, supplementary)
                    number_of_frames_current_sample = len(sample_x[0])
                    number_of_frames_previous_sample = len(prev_sample_x[0])

                # Check if the number of frames is the same for the current and
                # previous sample, as we need to handle them differently:
                #   - if same: just add to the existing buffer
                #   - if diff: yield the current buffer (so batch has samples that
                #       are all the same number of frames), start new buffer for
                #       this new number of frames
                if number_of_frames_current_sample == number_of_frames_previous_sample:
                    buffer.append(sample)

                    # If the batch is full, yield it and then clear it
                    if len(buffer) == self.batch_size:
                        yield self._convert_input_target_key(buffer)
                        buffer.clear()
                else:
                    # otherwise, yield the current batch_buffer and
                    # start a new one with the current sample
                    yield self._convert_input_target_key(buffer)
                    buffer = [sample]

        # If there are any elements left in the batch after the
        # last iteration, yield them
        if buffer:
            yield self._convert_input_target_key(buffer)

    def _shuffled_image_iter_with_key(
        self,
    ) -> Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]]:
        """Image dataset iteration, shuffled, with data keys."""
        # [DEV]: A number of these methods could probably be combined with some
        # clever type handling. They have currently been left separate for ease.

        # Should be either (tabular, images, supplementary) or
        # (images, supplementary).
        # Note that all samples in the dataset will have the same number
        # of elements per sample.
        sample_x: _PTImageIterDataX
        num_x_elements_per_sample: int

        # If the dataset should be shuffled, we use a reservoir sampling method to
        # sample from a buffer of elements from the dataset. We also have to group
        # samples with the same shapes for images within a same batch.
        #
        # `buffer_per_num_frames` and `batch_per_num_frames` are thus both mappings:
        #   "number of frames" -> "list of samples with that number of frames"
        batch_per_num_frames: defaultdict[int, _DataBatchWithKey] = defaultdict(list)
        buffer_per_num_frames: defaultdict[int, _DataBatchWithKey] = defaultdict(list)

        # If we are in this method, we know that self.dataset is either
        # _PytorchFileIterableDataset and that we are working with images.
        # In either case, this will return a type of _PTImageIterDataEntryWithKey
        # in its iteration.
        sample: _PTImageIterDataEntryWithKey
        for sample in cast(Iterator[_PTImageIterDataEntryWithKey], self.dataset):
            # Get the number of X elements for each sample
            sample_x, num_x_elements_per_sample = (
                self._get_and_validate_image_iter_sample_x(sample)
            )

            # Establish the number of frames this sample represents
            if num_x_elements_per_sample == 3:  # (tabular, images, supplementary)
                num_frames = len(sample_x[1])
            else:  # num_x_elements_per_sample == 2 # (images, supplementary)
                num_frames = len(sample_x[0])

            # If the buffer is full, we can then create a batch
            if (
                len(curr_buffer := buffer_per_num_frames[num_frames])
                == self.buffer_size
            ):
                # If the batch is of the appropriate size, yield and reset
                if len(batch_per_num_frames[num_frames]) == self.batch_size:
                    yield self._convert_input_target_key(
                        batch_per_num_frames[num_frames]
                    )
                    batch_per_num_frames[num_frames] = []

                # Take an element (at random) from the buffer and transfer it to the
                # batch. Replace the removed element in the buffer with the current
                # sample.
                idx = self._get_random_buffer_idx()
                batch_per_num_frames[num_frames].append(curr_buffer[idx])
                curr_buffer[idx] = sample
                buffer_per_num_frames[num_frames] = curr_buffer
            # Otherwise, just add the sample to the buffer
            else:
                buffer_per_num_frames[num_frames].append(sample)

        # This is only reached once the dataset iterator has been exhausted. The
        # remainder of the buffer is shuffled and yielded until empty.
        for key in buffer_per_num_frames.keys():
            curr_buffer = buffer_per_num_frames[key]
            random.shuffle(curr_buffer)

            # Add elements from the buffer to the batch, yielding as we create full
            # batches
            batch: _DataBatchWithKey = batch_per_num_frames[key]
            while curr_buffer:
                if len(batch) == self.batch_size:
                    yield self._convert_input_target_key(batch)
                    batch = []

                batch.append(curr_buffer.pop())

            # If there are any elements left in the batch after the
            # dataset/buffer are empty, yield an incomplete batch.
            if len(batch) > 0:
                yield self._convert_input_target_key(batch)

    def _get_and_validate_image_iter_sample_x(
        self, sample: Union[_PTImageIterDataEntryWithKey, _PTImageIterDataEntryNoKey]
    ) -> tuple[_PTImageIterDataX, int]:
        """Extract the X elements from a sample and validate the form.

        Returns:
            A tuple of the X part of the sample, and the number of elements in
            this X sample.

        Raises:
            TypeError: if the sample X is not a tuple as expected.
            ValueError: if the number of elements in the sample X is not 2 or 3.
        """
        # DEV: These guard conditions match what was previously stated in comments
        #      but this may be incorrect, particularly with regards to segmentation
        #      datasets.

        # mypy: only these types are supported, so we can cast knowing that
        #       the check below will fail out otherwise
        sample_x: _PTImageIterDataX = cast(_PTImageIterDataX, sample[0])
        if not isinstance(sample_x, tuple):
            raise TypeError(
                f"Incorrect type for sample in iteration:"
                f" expected tuple"
                f" (`(tabular, images, supplementary)`"
                f" or `(images, supplementary)`),"
                f" got {type(sample_x)}"
            )

        num_x_elements_per_sample: int = len(sample_x)
        if num_x_elements_per_sample not in (2, 3):
            raise ValueError(
                f"Expected number of elements in sample X should be"
                f" 2 (`(images, supplementary)`),"
                f" or 3 (`(tabular, images, supplementary)`);"
                f" got {num_x_elements_per_sample}"
            )

        return sample_x, num_x_elements_per_sample

    def _convert_input_target(
        self,
        batch: Union[_DataBatchNoKey, _PTImageIterDataBatchNoKey],
    ) -> list[SingleOrMulti[torch.Tensor]]:
        """Convert batch into input and target."""
        # mypy: The types of the batch are technically subtypes of the root
        #   _DataBatch, but as _DataBatch is defined as a list, it is invariant to the
        #   contained type.
        return _convert_batch_to_tensor(cast(_DataBatchNoKey, batch), self.dataset)

    def _convert_input_target_key(
        self,
        batch: Union[_DataBatchWithKey, _PTImageIterDataBatchWithKey],
    ) -> list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]:
        """Convert batch into input, target, and key."""
        # Extract the keys and arrays separately, so we can
        # convert the arrays to tensors
        batch_: list = []
        keys: list[str] = []
        for entry in batch:
            batch_.append(entry[:-1])
            keys.append(entry[-1])
        input_, target_ = _convert_batch_to_tensor(batch_, self.dataset)
        return [input_, target_, keys]

    def expect_key_in_iter(self) -> bool:
        """Will there be a data key entry in the output from iteration?"""
        return isinstance(self.dataset, _PytorchFileIterableDataset)


@delegates()
class PyTorchIterableBitfountDataLoader(_BasePyTorchBitfountDataLoader):
    """Wraps a PyTorch DataLoader with bitfount functions.

    Args:
        dataset: An iterable dataset.
        secure_rng: A boolean value indicating whether to use a secure
            random number generator. Defaults to False.

    Attributes:
         secure_rng: A boolean value indicating whether to use a secure
            random number generator. Defaults to False.
    """

    def __init__(
        self, dataset: _IterableBitfountDataset, secure_rng: bool = False, **kwargs: Any
    ):
        # _PytorchIterableDataset is a wrapper around of
        # _IterableBitfountDataset so this cast is safe.
        dataset = cast(_PyTorchIterableDataset, dataset)
        super().__init__(dataset=dataset, **kwargs)
        self.secure_rng = secure_rng

    def __len__(self) -> int:
        """Number of batches or number of elements if batch size is None.

        Will also be the number of elements in the case where there are multiple (but
        a varying number of) images per data element, as in this case the batches are
        dynamically constructed to group entries with the same number of images.
        """
        if self._data_entry_contains_multi_imgs():
            # Return the dataset length since we might have uneven batches. In worst
            # case, we could even be in the case where we will have all batch sizes
            # equal to 1, which means we will have to go through the whole dataset.
            #
            # If there are fewer batches, we will reach a StopIteration.
            return len(self.dataset)
        else:
            # If there is only one image columns, then we can defer to default
            # handling. From the pytorch dataloader, the length of the dataloader
            # will be given by len(dataset)/batch_size, which is reconstructed here
            # as we have no underlying PyTorch dataloader.
            assert self.batch_size is not None  # nosec assert_used
            return math.ceil(len(self.dataset) / self.batch_size)

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

    def _with_key_iter(
        self,
    ) -> Iterator[list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]]]:
        """Iteration where the data provides an identification key."""
        # Batch size is optional in the core hierarchy but in pytorch we ensure it is
        # set to 1 if not provided. Re-assuring mypy of this.
        assert self.batch_size is not None  # nosec assert_used

        # Make mypy happy that our dataset is of the right type
        self.dataset = cast(_PytorchFileIterableDataset, self.dataset)
        # If there are images, defer to parent method
        if self._data_entry_contains_multi_imgs() and self.batch_size > 1:
            yield from self._image_iter_with_key()
        # Otherwise, handle it here
        else:
            batch: _DataBatchWithKey = []

            # If we are in this method, we know that self.dataset is
            # _PytorchFileIterableDataset and will return a type of _DataEntryWithKey in
            # its iteration
            sample: _DataEntryWithKey
            if self.shuffle:
                # If the dataset should be shuffled, we use a reservoir sampling method
                # to sample from a buffer of elements from the dataset.
                buffer: _DataBatchWithKey = []

                for sample in self.dataset:
                    if len(batch) == self.batch_size:
                        yield self._convert_input_target_key(batch)
                        batch = []

                    if len(buffer) == self.buffer_size:
                        idx = self._get_random_buffer_idx()
                        batch.append(buffer[idx])
                        buffer[idx] = sample
                    else:
                        buffer.append(sample)

                # This is only reached once the dataset iterator has been exhausted. The
                # remainder of the buffer is shuffled and yielded until empty.
                random.shuffle(buffer)
                while buffer:
                    if len(batch) == self.batch_size:
                        yield self._convert_input_target_key(batch)
                        batch = []

                    batch.append(buffer.pop())

            else:
                # If the dataset should not be shuffled, we simply
                # iterate over the dataset
                for sample in self.dataset:
                    if len(batch) == self.batch_size:
                        yield self._convert_input_target_key(batch)
                        batch = []

                    batch.append(sample)

            # If there are any elements left in the batch after the dataset/buffer are
            # empty, yield an incomplete batch.
            if batch:
                yield self._convert_input_target_key(batch)

    def _no_key_iter(self) -> Iterator[list[SingleOrMulti[torch.Tensor]]]:
        """Iteration of raw data, with no identification key."""
        # Batch size is optional in the core hierarchy but in pytorch we ensure it is
        # set to 1 if not provided. Re-assuring mypy of this.
        assert self.batch_size is not None  # nosec assert_used

        # If we are in this method then `self.dataset` is explicitly NOT
        # _PytorchFileIterableDataset
        self.dataset = cast(_PyTorchIterableDataset, self.dataset)

        if self._data_entry_contains_multi_imgs() and self.batch_size > 1:
            yield from self._image_iter()
        else:
            batch: _DataBatchNoKey = []

            if self.shuffle:
                # If the dataset should be shuffled, we use a reservoir sampling method
                # to sample from a buffer of elements from the dataset.
                buffer: _DataBatchNoKey = []
                for sample in self.dataset:
                    if len(batch) == self.batch_size:
                        yield self._convert_input_target(batch)
                        batch = []

                    if len(buffer) == self.buffer_size:
                        idx = self._get_random_buffer_idx()
                        batch.append(buffer[idx])
                        buffer[idx] = sample
                    else:
                        buffer.append(sample)

                # This is only reached once the dataset iterator has been exhausted. The
                # remainder of the buffer is shuffled and yielded until empty.
                random.shuffle(buffer)
                while buffer:
                    if len(batch) == self.batch_size:
                        yield self._convert_input_target(batch)
                        batch = []

                    batch.append(buffer.pop())

            else:
                # If the dataset should not be shuffled, we simply
                # iterate over the dataset
                for sample in cast(Iterator[_DataEntryNoKey], self.dataset):
                    if len(batch) == self.batch_size:
                        yield self._convert_input_target(batch)
                        batch = []

                    batch.append(sample)

            # If there are any elements left in the batch after the dataset/buffer are
            # empty, yield an incomplete batch.
            if batch:
                yield self._convert_input_target(batch)
