"""Contains PyTorch implementations of the BitfountModel paradigm."""

from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from collections.abc import MutableMapping, Sequence
from io import BytesIO
import logging
import os
import re
from typing import Any, ClassVar, Generic, Optional, Union, cast

from deprecated import deprecated
from marshmallow import fields
import numpy as np
import pandas as pd
import pytorch_lightning as pl
from pytorch_lightning.callbacks import Callback
from pytorch_lightning.callbacks.progress import TQDMProgressBar
from pytorch_lightning.loggers import TensorBoardLogger
import torch
from torch import nn as nn
from torch.optim.lr_scheduler import _LRScheduler
from torch.utils.data import DataLoader as PyTorchDataLoader

from bitfount import config
from bitfount.backends.pytorch.data.dataloaders import _BasePyTorchBitfountDataLoader
from bitfount.backends.pytorch.epoch_callbacks import EpochCallbacks
from bitfount.backends.pytorch.federated.mixins import _PyTorchDistributedModelMixIn
from bitfount.backends.pytorch.models.base_models import (
    _TEST_STEP_OUTPUT,
    _TEST_STEP_OUTPUT_GENERIC,
    _TRAIN_STEP_OUTPUT,
    _OptimizerType,
)
from bitfount.backends.pytorch.utils import (
    _TORCH_DTYPES,
    autodetect_gpu,
    enhanced_torch_load,
)
from bitfount.data.databunch import BitfountDataBunch
from bitfount.data.dataloaders import BitfountDataLoader
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.federated.helper import TaskContext
from bitfount.metrics import Metric
from bitfount.models.base_models import ClassifierMixIn
from bitfount.models.bitfount_model import BitfountModel
from bitfount.types import (
    T_DTYPE,
    T_FIELDS_DICT,
    EvaluateReturnType,
    PredictReturnType,
    _StrAnyDict,
)
from bitfount.utils import _merge_list_of_dicts, delegates
from bitfount.utils.logging_utils import filter_stderr

logger = logging.getLogger(__name__)


class _BasePyTorchBitfountModel(
    _PyTorchDistributedModelMixIn[T_DTYPE],
    BitfountModel,
    pl.LightningModule,
    Generic[T_DTYPE],
):
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "epochs": fields.Integer(allow_none=True),
        "steps": fields.Integer(allow_none=True),
    }

    train_dl: _BasePyTorchBitfountDataLoader

    # Test attributes
    _test_preds: Optional[Union[list[np.ndarray], pd.DataFrame]]
    _test_targets: Optional[list[np.ndarray]]
    _test_keys: Optional[list[str]]

    def __init__(
        self,
        batch_size: int = 32,
        epochs: Optional[int] = None,
        steps: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        if (steps is None and epochs is None) or (
            isinstance(steps, int) and isinstance(epochs, int)
        ):
            raise ValueError("You must specify one (and only one) of steps or epochs.")

        # Set hyperparameters
        self.batch_size = batch_size
        self.epochs: Optional[int] = epochs
        self.steps: Optional[int] = steps

        # Set training attributes
        # Override self._model with your model
        self._model: Optional[nn.Module] = None
        self._pl_trainer: pl.Trainer = self.trainer_init()  # cannot be "self.trainer"
        self.preds: list[float] = []
        self.target: list[float] = []
        self.val_stats: list[dict[str, float]] = []
        self._trained_on_previous_batch: bool = False
        self._total_num_batches_trained: int = 0

    @staticmethod
    def _get_import_statements() -> list[str]:
        """Returns a list of import statements likely to be required for the model.

        Returns:
            A list of import statements.
        """
        return [
            "import os",
            "import torch",
            "from torch import nn as nn",
            "from torch.nn import functional as F",
            "from bitfount import *",
            "import bitfount",
        ]

    @abstractmethod
    def forward(self, x: Any) -> Any:
        """Forward method of the model - just like a regular `torch.nn.Module` class.

        :::tip

        This will depend on your model but could be as simple as:

        ```python
        return self._model(x)
        ```

        :::

        Args:
            x: Input to the model.

        Returns:
            Output of the model.
        """
        raise NotImplementedError

    @abstractmethod
    def configure_optimizers(
        self,
    ) -> Union[_OptimizerType, tuple[list[_OptimizerType], list[_LRScheduler]]]:
        """Configures the optimizer(s) and scheduler(s) for backpropagation.

        Returns:
            Either the optimizer of your choice or a tuple of optimizers and learning
            rate schedulers.
        """
        raise NotImplementedError

    @abstractmethod
    def create_model(self) -> nn.Module:
        """Creates and returns the underlying pytorch model.

        Returns:
            Underlying pytorch model. This is set to `self._model`.
        """
        raise NotImplementedError

    def tensor_precision(self) -> T_DTYPE:
        """Returns tensor dtype used by Pytorch Lightning Trainer.

        :::note

        Currently only 32-bit training is supported.

        :::

        Returns:
            Pytorch tensor dtype.
        """
        # TODO: [BIT-727] support non-32 bit training
        return cast(T_DTYPE, _TORCH_DTYPES[self._pl_trainer.precision])

    def initialise_model(
        self,
        data: Optional[BaseSource] = None,
        data_splitter: Optional[DatasetSplitter] = None,
        context: Optional[TaskContext] = None,
    ) -> None:
        """Any initialisation of models/dataloaders to be done here.

        Initialises the dataloaders and sets `self._model` to be the output from
        `self.create_model`. Any initialisation ahead of training,
        serialization or deserialization should be done here.

        Args:
            data: The datasource for model training. Defaults to None.
            data_splitter: The splitter to use for the data. Defaults to None.
            context: Indicates if the model is running as a modeller or worker.
                If None, there is no difference between modeller and worker.
        """
        self._context = context
        self._initialised = True
        if data is not None:
            self.databunch = BitfountDataBunch(
                data_structure=self.datastructure,
                schema=self.schema,
                datasource=data,
                data_splitter=data_splitter,
            )

            if self._context != TaskContext.MODELLER:
                self._set_dataloaders(self.batch_size)

        self.datastructure.set_training_input_size(self.schema)

        if hasattr(self, "_objective") and self._objective == "classification":
            # The casts here are to assuage mypy because it (incorrectly) asserts
            # that a subclass of both ClassifierMixIn and BitfountModel cannot exist.
            # We utilise a subclass of both in the tests to assure ourselves.
            if isinstance(cast(ClassifierMixIn, self), ClassifierMixIn):
                cast(ClassifierMixIn, self).set_number_of_classes(self.schema)
            else:
                raise TypeError(
                    "Training objective is classification but this model does not "
                    "inherit from ClassifierMixIn"
                )

        if self._model is None:
            self._model = self.create_model()

    def trainer_init(self) -> pl.Trainer:
        """Initialises the Lightning Trainer for this model.

        Documentation for pytorch-lightning trainer can be found here:
        https://pytorch-lightning.readthedocs.io/en/stable/common/trainer.html

        :::tip

        Override this method to choose your own `Trainer` arguments.

        :::

        Returns:
            The pytorch lightning trainer.
        """
        callbacks: list[Callback] = [
            TQDMProgressBar(refresh_rate=1),
            EpochCallbacks(),
        ]

        # torch emits warnings to stderr that are not relevant for us, so we need
        # to filter them out
        with filter_stderr(
            re.escape(
                "[W Context.cpp:70] Warning:"
                " torch.use_deterministic_algorithms is in beta"
            )
        ):
            gpu_kwargs = autodetect_gpu()
            trainer = pl.Trainer(
                max_epochs=self.epochs or -1,
                max_steps=self.steps or -1,
                # Setting deterministic to True ensures that the results are
                # reproducible but this comes at the cost of performance. Also, some
                # operations require setting the CUBLAS_WORKSPACE_CONFIG env var to
                # `:4096:8` or `:16:8` when using CUDA.
                deterministic=True,
                callbacks=callbacks,
                logger=TensorBoardLogger(save_dir=str(config.settings.paths.logs_dir)),
                default_root_dir=str(config.settings.paths.output_dir),
                **gpu_kwargs,
            )
            return trainer

    def train_dataloader(self) -> _BasePyTorchBitfountDataLoader:
        """Returns training dataloader."""
        # We override the dataloader return annotation as the LightningModule
        # expects a pytorch DataLoader, and we return out PyTorchBitfountDataLoader
        return self.train_dl

    def val_dataloader(self) -> _BasePyTorchBitfountDataLoader:
        """Returns validation dataloader."""
        # We override the dataloader return annotation as the LightningModule
        # expects a pytorch DataLoader, and we return out PyTorchBitfountDataLoader
        return cast(_BasePyTorchBitfountDataLoader, self.validation_dl)

    def test_dataloader(self) -> _BasePyTorchBitfountDataLoader:
        """Returns test dataloader."""
        # We override the dataloader return annotation as the LightningModule
        # expects a pytorch DataLoader, and we return out PyTorchBitfountDataLoader
        return cast(_BasePyTorchBitfountDataLoader, self.test_dl)

    def _expect_keys(
        self,
        dataloaders: Optional[
            BitfountDataLoader
            | PyTorchDataLoader
            | list[BitfountDataLoader]
            | list[PyTorchDataLoader]
        ],
    ) -> bool:
        """Should data keys be expected in entries from target dataloader.

        Args:
            dataloaders: A list of Pytorch/Bitfount dataloaders. This should be a
                single-element list, `Optional` and longer lists are provided only
                to enable compatibility with the PyTorch Lightning return types.

        Returns:
            bool: True if data keys are expected in entries, False otherwise.

        Raises:
            TypeError: If no dataloader is provided.
            TypeError: If the number of dataloaders provided is not 1.
        """
        if dataloaders is None:
            raise TypeError(
                "Expected list of PyTorch or Bitfount dataloaders; got `None`"
            )

        # If provided with a list/collection of dataloaders, extract
        if isinstance(dataloaders, Sequence):
            if len(dataloaders) != 1:
                raise TypeError(
                    f"Expected exactly one PyTorch or Bitfount dataloader;"
                    f" got {len(dataloaders)}"
                )

            dataloader = dataloaders[0]
        # Otherwise is a dataloader object directly, just use that
        else:
            dataloader = dataloaders

        return (
            isinstance(dataloader, _BasePyTorchBitfountDataLoader)
            and dataloader.expect_key_in_iter()
        )

    def serialize(self, filename: Union[str, os.PathLike]) -> None:
        """Serialize model to file with provided `filename`.

        Args:
            filename: Path to file to save serialized model.
        """
        if not self._initialised:
            logger.info("Model not yet initialised. Auto-initialising model.")
            self.initialise_model()
        # Model has been initialised, assuring mypy of this
        assert self._model is not None  # nosec assert_used
        torch.save(self._model.state_dict(), filename)

    def deserialize(
        self,
        content: Union[str, os.PathLike, bytes],
        weights_only: bool = True,
        **kwargs: Any,
    ) -> None:
        """Deserialize model.

        :::danger

        If `weights_only` is set to False, this should not be used on a model file that
        has been received across a trust boundary due to underlying use of `pickle` by
        `torch`.

        :::

        Args:
            content: Path to file containing serialized model.
            weights_only: If True, only load the weights of the model. If False, load
                the entire model. Defaults to True.
            **kwargs: Keyword arguments provided to `torch.load` under the hood.
        """
        kwargs.update({"weights_only": weights_only})
        if not self._initialised:
            logger.info("Model not yet initialised. Auto-initialising model.")
            self.initialise_model()
        # Model has been initialised, assuring mypy of this
        assert self._model is not None  # nosec assert_used
        load_contents = BytesIO(content) if isinstance(content, bytes) else content
        self._model.load_state_dict(enhanced_torch_load(load_contents, **kwargs))

    def skip_training_batch(self, batch_idx: int) -> bool:
        """Checks if the current batch from the training set should be skipped.

        This is a workaround for the fact that PyTorch Lightning starts the Dataloader
        iteration from the beginning every time `fit` is called. This means that if we
        are training in steps, we are always training on the same batches. So this
        method needs to be called at the beginning of every `training_step` to skip
        to the right batch index.

        Args:
            batch_idx: the index of the batch from `training_step`.

        Returns:
            True if the batch should be skipped, otherwise False.
        """
        # TODO: [BIT-1237] remove this code block and find a better way to do this that
        # doesn't involve loading every batch into memory until we get to the right one
        if self.steps:
            # If we have trained on the previous batch, we can avoid the checks because
            # it means we have already reached the target start batch.
            if not self._trained_on_previous_batch:
                if (self.steps != self._pl_trainer.max_steps) and (
                    batch_idx < (self._total_num_batches_trained % len(self.train_dl))
                ):
                    return True
                else:
                    self._trained_on_previous_batch = True

            # `_total_num_batches_trained` hasn't been incremented yet so we need to add
            # 1 here to get the correct batch number.
            if self._total_num_batches_trained + 1 == self._pl_trainer.max_steps:
                self._trained_on_previous_batch = False

        if not self._pl_trainer.sanity_checking:
            self._total_num_batches_trained += 1

        return False

    @staticmethod
    def _compute_metric_averages(outputs: list[_StrAnyDict]) -> dict[str, float]:
        """Compute the average metrics from a list of outputs."""
        # Stack up shared dict keys into lists of entries
        stacked_dict = defaultdict(list)
        for output in outputs:
            for k, v in output.items():
                stacked_dict[k].append(v)

        # Calculate the average value of each key and convert to float
        avgs = {}
        for k, v_list in stacked_dict.items():
            avgs[k] = float(torch.stack(v_list).mean().item())
        return avgs

    def _evaluate_local(
        self, test_dl: Optional[BitfountDataLoader] = None, **kwargs: Any
    ) -> EvaluateReturnType:
        """This method runs inference on the test dataloader.

        This is done by calling `self.test_step` under the hood. Customise this method
        as you please but it must return a list of predictions and a list of targets.

        Args:
            test_dl: Optional dataloader to run inference on which takes precedence over
                the dataloader returned by `self.test_dataloader`.
            **kwargs: Additional keyword arguments.

        Returns:
            A tuple of predictions and targets as numpy arrays.
        """
        # Reset test attributes to None
        self._reset_test_attrs()

        if test_dl is None:
            if isinstance(self.test_dl, _BasePyTorchBitfountDataLoader):
                test_dl = self.test_dl
            else:
                raise ValueError("No test data to evaluate the model on.")

        self._pl_trainer.test(model=self, dataloaders=cast(PyTorchDataLoader, test_dl))

        return EvaluateReturnType(
            preds=np.asarray(self._test_preds),
            targs=np.asarray(self._test_targets),
            keys=self._test_keys,
        )

    def _reset_test_attrs(self) -> None:
        """Resets test attributes to None."""
        self._test_preds = None
        self._test_targets = None
        self._test_keys = None

    def _predict_local(self, data: BaseSource, **kwargs: Any) -> PredictReturnType:
        """This method runs inference on the test data, returns predictions.

        This is done by calling `test_step` under the hood. Customise this method as you
        please but it must return a list of predictions and a list of targets. Note that
        as this is the prediction function, only the predictions are returned.

        :::tip

        Feel free to overwrite this method just so long as you return a numpy array to
        maintain compatability with the `ModelInference` algorithm - you are not limited
        to just returning predictions.

        :::

        Returns:
            A numpy array containing the prediction values.
        """
        if not hasattr(self, "test_dl") or not self.test_dl:
            raise ValueError("No dataloader found. Please initialise the model first.")

        if isinstance(self.test_dl, BitfountDataLoader):
            logger.info(
                f"Using test portion of dataset for inference - this has "
                f"{len(self.test_dl.dataset)} record(s)."
            )
        else:
            raise ValueError("No test data to infer in the provided datasource.")

        self._pl_trainer.test(
            model=self, dataloaders=cast(PyTorchDataLoader, self.test_dl)
        )

        if self._test_preds is not None:
            return PredictReturnType(preds=self._test_preds, keys=self._test_keys)

        raise ValueError("'self._test_preds' was not set by the model after inference.")

    def _fit_local(
        self,
        data: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        metrics: Optional[Union[str, list[str], MutableMapping[str, Metric]]] = None,
        **kwargs: Any,
    ) -> dict[str, str]:
        """Trains the model on local data.

        Returns:
            Validation metrics for the final epoch.
        """
        if not self._initialised:
            logger.info("Model not yet initialised. Auto-initialising model.")
            self.initialise_model(data, data_splitter=data_splitter)

        self._pl_trainer.fit(self)
        # Return the validation stats to be sent back
        return {k: ("%.4f" % v) for k, v in self.val_stats[-1].items()}


@deprecated(
    "PyTorchBitfountModel is deprecated and will be removed in a future version."
    " Please reimplement in PyTorchBitfountModelv2."
)
@delegates()
class PyTorchBitfountModel(_BasePyTorchBitfountModel[T_DTYPE]):
    """Blueprint for a pytorch custom model in the lightning v1 format.

    This class must be subclassed in its own module. A `Path` to the module containing
    the subclass can then be passed to `BitfountModelReference` and on to your
    `Algorithm` of choice which will send the model to Bitfount Hub.

    To get started, just implement the abstract methods in this class. For more advanced
    users feel free to override or overwrite any variables/methods in your subclass.

    Take a look at the pytorch-lightning documentation on how to properly create a
    `LightningModule`:

    https://pytorch-lightning.readthedocs.io/en/1.9.5/common/lightning_module.html

    :::caution

    Ensure you set `self.metrics` in the `__init__` method of your subclass to ensure
    they pertain appropriately to your model. If not, Bitfount will attempt to set
    these appropriately for you but there is no guarantee it will get it right.

    :::

    Args:
        batch_size: The batch size to use for training. Defaults to 32.
        epochs: The number of epochs to train for.
        steps: The number of steps to train for.
        **kwargs: Any additional arguments to pass to parent constructors.

    Attributes:
        batch_size: The batch size to use for training.
        epochs: The number of epochs to train for.
        steps: The number of steps to train for.
        preds: The predictions from the most recent test run.
        target: The targets from the most recent test run.
        val_stats: Metrics from the validation set during training.

    Raises:
        ValueError: If both `epochs` and `steps` are specified.
    """

    def __init__(
        self,
        batch_size: int = 32,
        epochs: Optional[int] = None,
        steps: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(batch_size=batch_size, epochs=epochs, steps=steps, **kwargs)

        # Test attributes
        self._test_preds = None
        self._test_targets = None
        self._test_keys = None

    @abstractmethod
    def training_step(self, batch: Any, batch_idx: int) -> _TRAIN_STEP_OUTPUT:
        """Training step.

        :::caution

        If iterations have been specified in terms of steps, the default behaviour of
        pytorch lightning is to train on the first _n_ steps of the dataloader every
        time `fit` is called. This default behaviour is not desirable and has been dealt
        with in the built-in Bitfount models but, until this bug gets fixed by the
        pytorch lightning team, this needs to be implemented by the user for custom
        models.

        :::

        :::tip

        Take a look at the `skip_training_batch` method for one way on how to deal with
        this. It can be used as follows:

        ```python
        if self.skip_training_batch(batch_idx):
            return None
        ```

        :::

        Args:
            batch: The batch to be trained on.
            batch_idx: The index of the batch to be trained on from the train
                dataloader.

        Returns:
            The loss from this batch as a `torch.Tensor`. Or a dictionary which includes
            the key `loss` and the loss as a `torch.Tensor`.
        """
        raise NotImplementedError

    @abstractmethod
    def validation_step(self, batch: Any, batch_idx: int) -> _StrAnyDict:
        """Validation step.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the validation
                dataloader.

        Returns:
            A dictionary of strings and values that should be averaged at the end of
            every epoch and logged e.g. `{"validation_loss": loss}`. These will be
            passed to the `validation_epoch_end` method.
        """
        raise NotImplementedError

    @abstractmethod
    def test_step(self, batch: Any, batch_idx: int) -> _TEST_STEP_OUTPUT:
        """Operates on a single batch of data from the test set.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the test
                dataloader.

        Returns:
            A dictionary of predictions and targets, with the dictionary
            keys being "predictions" and "targets" for each of them, respectively.
            These will be passed to the `test_epoch_end` method.
        """
        raise NotImplementedError

    def validation_epoch_end(self, outputs: list[_StrAnyDict]) -> None:
        """Called at the end of the validation epoch with all validation step outputs.

        Ensures that the average metrics from a validation epoch is stored. Logs results
        and also appends to `self.val_stats`.

        Args:
            outputs: list of outputs from each validation step.
        """
        # Override the pl.lightning method, as its outputs can be
        # list[Union[Tensor, _StrAnyDict]], whereas we force outputs to be a dict
        avgs = self._compute_metric_averages(outputs)
        self.val_stats.append(avgs)

        # Also log out these averaged metrics
        for k, v in avgs.items():
            self.log(f"avg_{k}", v)

    def test_epoch_end(
        self,
        outputs: list[_TEST_STEP_OUTPUT],
    ) -> None:
        """Aggregates the predictions and targets from the test set.

        :::caution

        If you are overwriting this method, ensure you set `self._test_preds` to
        maintain compatibility with `self._predict_local` unless you are overwriting
        both of them.

        :::

        Args:
            outputs: list of outputs from each test step.
        """
        # Override the pl.lightning method, as it requires a different type for outputs.

        # Merge outputs into singular lists rather than a list of dicts.
        # NOTE: This also _flattens_ the non-scalar outputs (such as `outputs` and
        # `targets`) such that a list (of len Z) MxN tensors becomes a list
        # (of len ZxM) (N,) tensors
        merged_outputs: dict[str, list[Union[torch.Tensor, str]]] = (
            _merge_list_of_dicts(cast(list[_TEST_STEP_OUTPUT_GENERIC], outputs))
        )

        self._test_preds = [
            i.cpu().numpy()
            for i in cast(list[torch.Tensor], merged_outputs["predictions"])
        ]
        self._test_targets = [
            i.cpu().numpy() for i in cast(list[torch.Tensor], merged_outputs["targets"])
        ]

        if self._expect_keys(self.trainer.test_dataloaders):
            self._test_keys = cast(list[str], merged_outputs["keys"])

            # If keys are expected, there should be the same number as the number of
            # predictions
            if (predictions_len := len(merged_outputs["predictions"])) != (
                keys_len := len(merged_outputs["keys"])
            ):
                raise ValueError(
                    f"Mismatch in number of predictions vs data keys;"
                    f" got {predictions_len} predictions and {keys_len} keys."
                )


@delegates()
class PyTorchBitfountModelv2(_BasePyTorchBitfountModel[T_DTYPE]):
    """Blueprint for a pytorch custom model in the lightning v2+ format.

    This class must be subclassed in its own module. A `Path` to the module containing
    the subclass can then be passed to `BitfountModelReference` and on to your
    `Algorithm` of choice which will send the model to Bitfount Hub.

    To get started, just implement the abstract methods in this class. For more advanced
    users feel free to override or overwrite any variables/methods in your subclass.

    Take a look at the pytorch-lightning documentation on how to properly create a
    `LightningModule`:

    https://pytorch-lightning.readthedocs.io/en/stable/common/lightning_module.html

    :::caution

    Ensure you set `self.metrics` in the `__init__` method of your subclass to ensure
    they pertain appropriately to your model. If not, Bitfount will attempt to set
    these appropriately for you but there is no guarantee it will get it right.

    :::

    Args:
        batch_size: The batch size to use for training. Defaults to 32.
        epochs: The number of epochs to train for.
        steps: The number of steps to train for.
        **kwargs: Any additional arguments to pass to parent constructors.

    Attributes:
        batch_size: The batch size to use for training.
        epochs: The number of epochs to train for.
        steps: The number of steps to train for.
        preds: The predictions from the most recent test run.
        target: The targets from the most recent test run.
        val_stats: Metrics from the validation set during training.

    Raises:
        ValueError: If both `epochs` and `steps` are specified.
    """

    def __init__(
        self,
        batch_size: int = 32,
        epochs: Optional[int] = None,
        steps: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(batch_size=batch_size, epochs=epochs, steps=steps, **kwargs)

        # Test attributes
        self._test_pred = None
        self._test_target = None
        self._test_keys = None

        # Step outputs for epoch end use
        self._pl_training_step_outputs: list[_TRAIN_STEP_OUTPUT] = []
        self._pl_validation_step_outputs: list[_StrAnyDict] = []
        self._pl_test_step_outputs: list[_TEST_STEP_OUTPUT] = []

    def training_step(self, batch: Any, batch_idx: int) -> _TRAIN_STEP_OUTPUT:
        """Training step.

        This is a wrapper around the _training_step() method which handles output
        storing.

        :::caution

        If iterations have been specified in terms of steps, the default behaviour of
        pytorch lightning is to train on the first _n_ steps of the dataloader every
        time `fit` is called. This default behaviour is not desirable and has been dealt
        with in the built-in Bitfount models but, until this bug gets fixed by the
        pytorch lightning team, this needs to be implemented by the user for custom
        models.

        :::

        :::tip

        Take a look at the `skip_training_batch` method for one way on how to deal with
        this. It can be used as follows:

        ```python
        if self.skip_training_batch(batch_idx):
            return None
        ```

        :::

        Args:
            batch: The batch to be trained on.
            batch_idx: The index of the batch to be trained on from the train
                dataloader.

        Returns:
            The loss from this batch as a `torch.Tensor`. Or a dictionary which includes
            the key `loss` and the loss as a `torch.Tensor`.
        """
        r = self._training_step(batch, batch_idx)
        self._pl_training_step_outputs.append(r)
        return r

    @abstractmethod
    def _training_step(self, batch: Any, batch_idx: int) -> _TRAIN_STEP_OUTPUT:
        """Actual training step method which performs the step action.

        :::caution

        If iterations have been specified in terms of steps, the default behaviour of
        pytorch lightning is to train on the first _n_ steps of the dataloader every
        time `fit` is called. This default behaviour is not desirable and has been dealt
        with in the built-in Bitfount models but, until this bug gets fixed by the
        pytorch lightning team, this needs to be implemented by the user for custom
        models.

        :::

        :::tip

        Take a look at the `skip_training_batch` method for one way on how to deal with
        this. It can be used as follows:

        ```python
        if self.skip_training_batch(batch_idx):
            return None
        ```

        :::

        Args:
            batch: The batch to be trained on.
            batch_idx: The index of the batch to be trained on from the train
                dataloader.

        Returns:
            The loss from this batch as a `torch.Tensor`. Or a dictionary which includes
            the key `loss` and the loss as a `torch.Tensor`.
        """
        raise NotImplementedError

    def on_train_epoch_end(self) -> None:
        """Called at the end of the training epoch.

        Default does nothing but clear training step outputs store.
        """
        # Pass through copy as we are about to clear the original
        self._train_epoch_end(self._pl_training_step_outputs.copy())
        self._pl_training_step_outputs.clear()

    def _train_epoch_end(self, outputs: list[_TRAIN_STEP_OUTPUT]) -> None:
        """Called at the end of the training epoch with all training step outputs.

        Default method does nothing.

        Args:
            outputs: list of outputs from each training step.
        """
        pass

    def validation_step(self, batch: Any, batch_idx: int) -> _StrAnyDict:
        """Validation step.

        This is a wrapper around the _validation_step() method which handles output
        storing.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the validation
                dataloader.

        Returns:
            A dictionary of strings and values that should be averaged at the end of
            every epoch and logged e.g. `{"validation_loss": loss}`. These will be
            passed to the `validation_epoch_end` method.
        """
        r = self._validation_step(batch, batch_idx)
        self._pl_validation_step_outputs.append(r)
        return r

    @abstractmethod
    def _validation_step(self, batch: Any, batch_idx: int) -> _StrAnyDict:
        """Actual validation step method which performs the step action.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the validation
                dataloader.

        Returns:
            A dictionary of strings and values that should be averaged at the end of
            every epoch and logged e.g. `{"validation_loss": loss}`. These will be
            passed to the `validation_epoch_end` method.
        """
        raise NotImplementedError

    def on_validation_epoch_end(self) -> None:
        """Called at the end of the validation epoch.

        Ensures that the average metrics from a validation epoch is stored. Logs
        results and also appends to `self.val_stats`.
        """
        # Pass through copy as we are about to clear the original
        self._validation_epoch_end(self._pl_validation_step_outputs.copy())
        self._pl_validation_step_outputs.clear()

    def _validation_epoch_end(self, outputs: list[_StrAnyDict]) -> None:
        """Called at the end of the validation epoch with all validation step outputs.

        Ensures that the average metrics from a validation epoch is stored. Logs
        results and also appends to `self.val_stats`.

        Args:
            outputs: list of outputs from each validation step.
        """
        # Override the pl.lightning method, as its outputs can be
        # list[Union[Tensor, _StrAnyDict]], whereas we force outputs to be a dict
        avgs = self._compute_metric_averages(outputs)
        self.val_stats.append(avgs)

        # Also log out these averaged metrics
        for k, v in avgs.items():
            self.log(f"avg_{k}", v)

    def test_step(self, batch: Any, batch_idx: int) -> _TEST_STEP_OUTPUT:
        """Operates on a single batch of data from the test set.

        This is a wrapper around the _test_step() method which handles output storing.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the test
                dataloader.

        Returns:
            A dictionary of predictions and targets, with the dictionary
            keys being "predictions" and "targets" for each of them, respectively.
            These will be passed to the `test_epoch_end` method.
        """
        r = self._test_step(batch, batch_idx)
        self._pl_test_step_outputs.append(r)

        return r

    @abstractmethod
    def _test_step(self, batch: Any, batch_idx: int) -> _TEST_STEP_OUTPUT:
        """Actual test step method which performs the step action.

        Operates on a single batch of data from the test set.

        Args:
            batch: The batch to be evaluated.
            batch_idx: The index of the batch to be evaluated from the test
                dataloader.

        Returns:
            A dictionary of predictions and targets, with the dictionary
            keys being "predictions" and "targets" for each of them, respectively.
            These will be passed to the `test_epoch_end` method.
        """
        raise NotImplementedError

    def on_test_epoch_end(self) -> None:
        """Called at the end of the test epoch.

        Aggregates the predictions and targets from the test set.

        :::caution

        If you are overwriting this method, ensure you set `self._test_preds` to
        maintain compatibility with `self._predict_local` unless you are overwriting
        both of them.

        :::
        """
        # Pass through copy as we are about to clear the original
        self._test_epoch_end(self._pl_test_step_outputs.copy())
        self._pl_test_step_outputs.clear()

    def _test_epoch_end(
        self,
        outputs: list[_TEST_STEP_OUTPUT],
    ) -> None:
        """Aggregates the predictions and targets from the test set.

        :::caution

        If you are overwriting this method, ensure you set `self._test_preds` to
        maintain compatibility with `self._predict_local` unless you are overwriting
        both of them.

        :::

        Args:
            outputs: list of outputs from each test step.
        """
        # Override the pl.lightning method, as it requires a different type for outputs.

        # Merge outputs into singular lists rather than a list of dicts.
        # NOTE: This also _flattens_ the non-scalar outputs (such as `outputs` and
        # `targets`) such that a list (of len Z) MxN tensors becomes a list
        # (of len ZxM) (N,) tensors
        merged_outputs: dict[str, list[Union[torch.Tensor, str]]] = (
            _merge_list_of_dicts(cast(list[_TEST_STEP_OUTPUT_GENERIC], outputs))
        )

        self._test_preds = [
            i.cpu().numpy()
            for i in cast(list[torch.Tensor], merged_outputs["predictions"])
        ]
        self._test_targets = [
            i.cpu().numpy() for i in cast(list[torch.Tensor], merged_outputs["targets"])
        ]

        if self._expect_keys(self.trainer.test_dataloaders):
            self._test_keys = cast(list[str], merged_outputs["keys"])

            # If keys are expected, there should be the same number as the number of
            # predictions
            if (predictions_len := len(merged_outputs["predictions"])) != (
                keys_len := len(merged_outputs["keys"])
            ):
                raise ValueError(
                    f"Mismatch in number of predictions vs data keys;"
                    f" got {predictions_len} predictions and {keys_len} keys."
                )
