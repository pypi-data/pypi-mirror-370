"""HuggingFace TIMM fine-tuning Algorithm.

Borrowed with permission from https://github.com/huggingface/pytorch-image-models.
Copyright 2020 Ross Wightman (https://github.com/rwightman)
"""

from __future__ import annotations

import warnings
from contextlib import suppress
from dataclasses import asdict
from functools import partial
import gc
import logging
import os
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional, Union

import desert
from marshmallow import fields
from marshmallow.validate import OneOf

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.federated.algorithms.hugging_face_algorithms.base import _HFModellerSide
from bitfount.federated.authorisation_checkers import ProtocolContext

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    from timm import utils as timm_utils
    from timm.data import Mixup
    from timm.layers import convert_splitbn_model, convert_sync_batchnorm, set_fast_norm
    from timm.loss import (
        BinaryCrossEntropy,
        JsdCrossEntropy,
        LabelSmoothingCrossEntropy,
        SoftTargetCrossEntropy,
    )
    from timm.models import create_model, safe_model_name
    from timm.optim import create_optimizer_v2, optimizer_kwargs
    from timm.scheduler import create_scheduler_v2, scheduler_kwargs
    from timm.utils import ApexScaler, NativeScaler
    import torch
    import torch.nn as nn
    from torch.nn.parallel import DistributedDataParallel as NativeDDP

    try:
        from apex import amp
        from apex.parallel import (
            DistributedDataParallel as ApexDDP,
            convert_syncbn_model,
        )

        has_apex = True
    except ImportError:
        has_apex = False

    try:
        if torch.cuda.amp.autocast is not None:
            has_native_amp = True
    except AttributeError:
        has_native_amp = False

    has_compile = hasattr(torch, "compile")

import yaml

from bitfount import config
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datastructure import DEFAULT_IMAGE_TRANSFORMATIONS, DataStructure
from bitfount.data.huggingface.utils import get_data_factory_dataset
from bitfount.data.types import DataSplit
from bitfount.federated.algorithms.base import BaseNonModelAlgorithmFactory, BaseWorkerAlgorithm
from bitfount.federated.algorithms.hugging_face_algorithms.utils import (
    TIMMTrainingConfig,
    train_one_epoch,
    validate,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.hooks import HookType, get_hooks
from bitfount.runners.utils import setup_loggers
from bitfount.types import T_FIELDS_DICT, _JSONDict
from bitfount.utils import delegates
from bitfount.utils.fs_utils import safe_write_to_file

logger = _get_federated_logger(__name__)

# Enable logging for timm checkpoint saver
timm_logger = logging.getLogger("timm.utils.checkpoint_saver")
setup_loggers([timm_logger])
_TimmBatchTransformationStep = Literal["train", "validation"]


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the TIMMFineTuning algorithm."""

    num_labels: Optional[int] = None

    def __init__(
        self,
        model_id: str,
        args: TIMMTrainingConfig,
        return_weights: bool,
        save_path: Union[str, os.PathLike],
        batch_transformations: Optional[list[dict[str, _JSONDict]]]=None,
        image_column_name: Optional[str] = None,
        target_column_name: Optional[str] = None,
        labels: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = f"hf_hub:{model_id}"
        self.args = args
        self.return_weights = return_weights
        self.save_path = save_path
        self.args.model = self.model_id
        self.image_column_name = image_column_name
        self.target_column_name = target_column_name
        if labels:
            self.labels2id = {
                self.target_column_name: {label: i for i, label in enumerate(labels)}
            }
            self.num_labels = len(labels)
        else:
            self.labels2id = None

        if batch_transformations is not None:
            self.batch_transformations = batch_transformations
        else:
            self.batch_transformations = [
                {
                    "albumentations": {
                        "arg": self.image_column_name,
                        "output": True,
                        "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                        "step": "train",
                    }
                },

                {
                    "albumentations": {
                        "arg": self.image_column_name,
                        "output": True,
                        "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                        "step": "validation",
                    }
                }
            ]




    def initialise_data(self, datasource: BaseSource, data_splitter: Optional[DatasetSplitter]=None) -> None:
        """Initialises the algorithm with data.

        Primarily sets the `train_dataloader`, `eval_dataloader` and `lr_scheduler` attributes
        to be used by the main `run` method (amongst others).
        """
        # Overwrite datasource partition_size to match the batch size of the model.
        datasource.partition_size = self.args.batch_size
        self.semantic_types = {
            "image": [self.image_column_name],
            "categorical": [self.target_column_name],
        }
        train_data_factory, train_dataset = get_data_factory_dataset(
            datasource=datasource,
            data_splitter=data_splitter,
            data_split=DataSplit.TRAIN,
            selected_cols=[self.image_column_name, self.target_column_name],
            selected_cols_semantic_types=self.semantic_types,
            batch_transforms=self.batch_transformations,
            target=self.target_column_name,
            labels2id=self.labels2id,
        )
        self.train_dataloader = train_data_factory.create_dataloader(
            train_dataset,
            batch_size=self.args.batch_size,
        )
        val_data_factory, val_dataset = get_data_factory_dataset(
            datasource=datasource,
            data_splitter=data_splitter,
            data_split=DataSplit.VALIDATION,
            selected_cols=[self.image_column_name, self.target_column_name],
            selected_cols_semantic_types=self.semantic_types,
            batch_transforms=self.batch_transformations,
            target=self.target_column_name,
            labels2id=self.labels2id,
        )
        self.eval_dataloader = val_data_factory.create_dataloader(
            val_dataset,
            batch_size=self.args.validation_batch_size or self.args.batch_size,
        )
        # Setup learning rate schedule and starting epoch
        updates_per_epoch = (
            len(self.train_dataloader) + self.args.grad_accum_steps - 1
        ) // self.args.grad_accum_steps
        self.lr_scheduler, num_epochs = create_scheduler_v2(
            self.optimizer,
            **scheduler_kwargs(self.args),
            updates_per_epoch=updates_per_epoch,
        )
        if hasattr(self, "start_epoch") and hasattr(self, "num_epochs"):
            # Run on all batches apart from the first if batched execution is enabled
            self.start_epoch += num_epochs
            self.num_epochs += num_epochs
        else:
            # Only run on the first batch if batched execution is enabled
            self.start_epoch = 0
            self.num_epochs = num_epochs

        if self.args.start_epoch is not None:
            # a specified start_epoch will always override the resume epoch
            self.start_epoch = self.args.start_epoch
        if self.lr_scheduler is not None and self.start_epoch > 0:
            if self.args.sched_on_updates:
                self.lr_scheduler.step_update(self.start_epoch * updates_per_epoch)
            else:
                self.lr_scheduler.step(self.start_epoch)
        if timm_utils.is_primary(self.args):
            if self.lr_scheduler:
                logger.info(
                    f'Scheduled epochs: {self.num_epochs}. LR stepped per {"epoch" if self.lr_scheduler.t_in_epochs else "update"}.'
                )
            else:
                logger.info(f"Scheduled epochs: {self.num_epochs}. LR is constant.")

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Primarily initialises the model and optimizer."""

        if task_id is not None:
            self.save_path = Path(self.save_path / f"{task_id}")
            self.save_path.mkdir(parents=True, exist_ok=True)

        # TODO: [BIT-3097] Resolve initialise without DP
        if pod_dp:
            logger.warning("The use of DP is not supported, ignoring set `pod_dp`.")

        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.benchmark = True

        self.device = timm_utils.init_distributed_device(self.args)
        if self.args.distributed:
            logger.info(
                "Training in distributed mode with multiple processes, 1 device per process."
                f"Process {self.args.rank}, total {self.args.world_size}, device {self.args.device}."
            )
        else:
            logger.info(
                f"Training with a single process on 1 device ({self.args.device})."
            )
        assert self.args.rank >= 0  # nosec[assert_used]

        # resolve AMP arguments based on PyTorch / Apex availability
        use_amp = None
        amp_dtype = torch.float16
        if self.args.amp:
            if self.args.amp_impl == "apex":
                assert (
                    has_apex
                ), "AMP impl specified as APEX but APEX is not installed."  # nosec[assert_used]
                use_amp = "apex"
                assert self.args.amp_dtype == "float16"  # nosec[assert_used]
            else:
                assert (  # nosec[assert_used]
                    has_native_amp
                ), "Please update PyTorch to a version with native AMP (or use APEX)."
                use_amp = "native"
                assert self.args.amp_dtype in (
                    "float16",
                    "bfloat16",
                )  # nosec[assert_used]
            if self.args.amp_dtype == "bfloat16":
                amp_dtype = torch.bfloat16

        timm_utils.random_seed(self.args.seed, self.args.rank)

        if self.args.fuser:
            timm_utils.set_jit_fuser(self.args.fuser)
        if self.args.fast_norm:
            set_fast_norm()

        in_chans = 3
        if self.args.in_chans is not None:
            in_chans = self.args.in_chans
        elif self.args.input_size is not None:
            in_chans = self.args.input_size[0]

        # Default num_classes to the number of labels
        if (
            self.args.num_classes is None
            and self.num_labels is not None
            and self.num_labels > 0
        ):
            self.args.num_classes = self.num_labels
        logger.info(
            f'{"Using" if self.args.pretrained else "Not using"} pre-trained model weights'
        )
        self.model = create_model(
            self.model_id,
            pretrained=self.args.pretrained,
            in_chans=in_chans,
            num_classes=self.args.num_classes,
            drop_rate=self.args.drop,
            drop_path_rate=self.args.drop_path,
            drop_block_rate=self.args.drop_block,
            global_pool=self.args.gp,
            bn_momentum=self.args.bn_momentum,
            bn_eps=self.args.bn_eps,
            scriptable=self.args.torchscript,
            checkpoint_path=self.args.initial_checkpoint,
            **self.args.model_kwargs,
        )
        if self.args.head_init_scale is not None:
            with torch.no_grad():
                self.model.get_classifier().weight.mul_(self.args.head_init_scale)
                self.model.get_classifier().bias.mul_(self.args.head_init_scale)
        if self.args.head_init_bias is not None:
            nn.init.constant_(
                self.model.get_classifier().bias, self.args.head_init_bias
            )

        if self.args.num_classes is None:
            assert hasattr(  # nosec[assert_used]
                self.model, "num_classes"
            ), "Model must have `num_classes` attr if not set on cmd line/config."
            self.args.num_classes = self.model.num_classes

        if self.args.grad_checkpointing:
            self.model.set_grad_checkpointing(enable=True)

        if timm_utils.is_primary(self.args):
            logger.info(
                f"Model {safe_model_name(self.model_id)} created, param count:{sum([m.numel() for m in self.model.parameters()])}"
            )

        # Setup augmentation batch splits for contrastive loss or split bn
        num_aug_splits = 0
        if self.args.aug_splits > 0:
            assert (
                self.args.aug_splits > 1
            ), "A split of 1 makes no sense"  # nosec[assert_used]
            num_aug_splits = self.args.aug_splits

        # enable split bn (separate bn stats per batch-portion)
        if self.args.split_bn:
            assert num_aug_splits > 1 or self.args.resplit  # nosec[assert_used]
            self.model = convert_splitbn_model(self.model, max(num_aug_splits, 2))

        # move model to GPU, enable channels last layout if set
        self.model.to(device=self.device)
        if self.args.channels_last:
            self.model.to(memory_format=torch.channels_last)

        # Setup synchronized BatchNorm for distributed training
        if self.args.distributed and self.args.sync_bn:
            self.args.dist_bn = ""  # disable dist_bn when sync BN active
            assert not self.args.split_bn  # nosec[assert_used]
            if has_apex and use_amp == "apex":
                # Apex SyncBN used with Apex AMP
                # WARNING this won't currently work with models using BatchNormAct2d
                self.model = convert_syncbn_model(self.model)
            else:
                self.model = convert_sync_batchnorm(self.model)
            if timm_utils.is_primary(self.args):
                logger.info(
                    "Converted model to use Synchronized BatchNorm. WARNING: You may have issues if using "
                    "zero initialized BN layers (enabled by default for ResNets) while sync-bn enabled."
                )

        if self.args.torchscript:
            assert not self.args.torchcompile  # nosec[assert_used]
            assert (
                use_amp != "apex"
            ), "Cannot use APEX AMP with torchscripted model"  # nosec[assert_used]
            assert (  # nosec[assert_used]
                not self.args.sync_bn
            ), "Cannot use SyncBatchNorm with torchscripted model"
            self.model = torch.jit.script(self.model)

        if not self.args.lr:
            global_batch_size = (
                self.args.batch_size * self.args.world_size * self.args.grad_accum_steps
            )
            batch_ratio = global_batch_size / self.args.lr_base_size
            if not self.args.lr_base_scale:
                on = self.args.opt.lower()
                self.args.lr_base_scale = (
                    "sqrt" if any([o in on for o in ("ada", "lamb")]) else "linear"
                )
            if self.args.lr_base_scale == "sqrt":
                batch_ratio = batch_ratio**0.5
            self.args.lr = self.args.lr_base * batch_ratio
            if timm_utils.is_primary(self.args):
                logger.info(
                    f"Learning rate ({self.args.lr}) calculated from base learning rate ({self.args.lr_base}) "
                    f"and effective global batch size ({global_batch_size}) with {self.args.lr_base_scale} scaling."
                )

        self.optimizer = create_optimizer_v2(
            self.model,
            **optimizer_kwargs(cfg=self.args),
            **self.args.opt_kwargs,
        )

        # Setup automatic mixed-precision (AMP) loss scaling and op casting
        self.amp_autocast = suppress  # do nothing
        self.loss_scaler = None
        if use_amp == "apex":
            assert self.device.type == "cuda"  # nosec[assert_used]
            self.model, self.optimizer = amp.initialize(
                self.model, self.optimizer, opt_level="O1"
            )
            self.loss_scaler = ApexScaler()
            if timm_utils.is_primary(self.args):
                logger.info("Using NVIDIA APEX AMP. Training in mixed precision.")
        elif use_amp == "native":
            try:
                self.amp_autocast = partial(
                    torch.autocast, device_type=self.device.type, dtype=amp_dtype
                )
            except (AttributeError, TypeError):
                # fallback to CUDA only AMP for PyTorch < 1.10
                assert self.device.type == "cuda"  # nosec[assert_used]
                self.amp_autocast = torch.cuda.amp.autocast
            if self.device.type == "cuda" and amp_dtype == torch.float16:
                # loss scaler only used for float16 (half) dtype, bfloat16 does not need it
                self.loss_scaler = NativeScaler()
            if timm_utils.is_primary(self.args):
                logger.info("Using native Torch AMP. Training in mixed precision.")
        else:
            if timm_utils.is_primary(self.args):
                logger.info("AMP not enabled. Training in float32.")

        # Setup exponential moving average of model weights, SWA could be used here too
        self.model_ema = None
        if self.args.model_ema:
            # Important to create EMA model after cuda(), DP wrapper, and AMP but before DDP wrapper
            self.model_ema = timm_utils.ModelEmaV2(
                self.model,
                decay=self.args.model_ema_decay,
                device="cpu" if self.args.model_ema_force_cpu else None,
            )

        # Setup distributed training
        if self.args.distributed:
            if has_apex and use_amp == "apex":
                # Apex DDP preferred unless native amp is activated
                if timm_utils.is_primary(self.args):
                    logger.info("Using NVIDIA APEX DistributedDataParallel.")
                self.model = ApexDDP(self.model, delay_allreduce=True)
            else:
                if timm_utils.is_primary(self.args):
                    logger.info("Using native Torch DistributedDataParallel.")
                self.model = NativeDDP(
                    self.model,
                    device_ids=[self.device],
                    broadcast_buffers=not self.args.no_ddp_bb,
                )
            # NOTE: EMA model does not need to be wrapped by DDP

        if self.args.torchcompile:
            # torch compile should be done after DDP
            assert (  # nosec[assert_used]
                has_compile
            ), "A version of torch w/ torch.compile() is required for --compile, possibly a nightly."
            self.model = torch.compile(self.model, backend=self.args.torchcompile)

        # Setup mixup / cutmix
        self.mixup_fn = None
        mixup_active = (
            self.args.mixup > 0
            or self.args.cutmix > 0.0
            or self.args.cutmix_minmax is not None
        )
        if mixup_active:
            mixup_args = dict(
                mixup_alpha=self.args.mixup,
                cutmix_alpha=self.args.cutmix,
                cutmix_minmax=self.args.cutmix_minmax,
                prob=self.args.mixup_prob,
                switch_prob=self.args.mixup_switch_prob,
                mode=self.args.mixup_mode,
                label_smoothing=self.args.smoothing,
                num_classes=self.args.num_classes,
            )
            if self.args.prefetcher:
                assert (  # nosec[assert_used]
                    not num_aug_splits
                )  # collate conflict (need to support deinterleaving in collate mixup)
            else:
                self.mixup_fn = Mixup(**mixup_args)

        # Setup loss function
        if self.args.jsd_loss:
            assert (
                num_aug_splits > 1
            )  # nosec[assert_used] # JSD only valid with aug splits set
            train_loss_fn = JsdCrossEntropy(
                num_splits=num_aug_splits, smoothing=self.args.smoothing
            )
        elif mixup_active:
            # smoothing is handled with mixup target transform which outputs sparse, soft targets
            if self.args.bce_loss:
                train_loss_fn = BinaryCrossEntropy(
                    target_threshold=self.args.bce_target_thresh
                )
            else:
                train_loss_fn = SoftTargetCrossEntropy()
        elif self.args.smoothing:
            if self.args.bce_loss:
                train_loss_fn = BinaryCrossEntropy(
                    smoothing=self.args.smoothing,
                    target_threshold=self.args.bce_target_thresh,
                )
            else:
                train_loss_fn = LabelSmoothingCrossEntropy(
                    smoothing=self.args.smoothing
                )
        else:
            train_loss_fn = nn.CrossEntropyLoss()
        self.train_loss_fn = train_loss_fn.to(device=self.device)
        self.validate_loss_fn = nn.CrossEntropyLoss().to(device=self.device)

        # Setup checkpoint saver and eval metric tracking
        self.saver = None
        if timm_utils.is_primary(self.args):
            decreasing = True if self.args.eval_metric == "loss" else False
            logger.info(f"Creating checkpoint saver at directory '{self.save_path}'")
            # Need to check if checkpoint exists and update prefix if it does as it
            # will use an error otherwise. If the checkpoint path exists, it will
            # always have epoch 0
            checkpoint_path = os.path.join(self.save_path, "checkpoint-0.pth.tar")
            if os.path.exists(checkpoint_path):
                checkpoint_prefix = "checkpoint_"
                i = 0
                while os.path.exists(
                    self.save_path / f"{checkpoint_prefix}{i}-0.pth.tar"
                ):
                    i += 1
                checkpoint_prefix = f"{checkpoint_prefix}{i}"
            else:
                checkpoint_prefix = "checkpoint"
            self.saver = timm_utils.CheckpointSaver(
                model=self.model,
                optimizer=self.optimizer,
                args=self.args,
                model_ema=self.model_ema,
                amp_scaler=self.loss_scaler,
                checkpoint_prefix=checkpoint_prefix,
                checkpoint_dir=self.save_path,
                recovery_dir=self.save_path,
                decreasing=decreasing,
                max_history=self.args.checkpoint_hist,
            )
            with open(os.path.join(self.save_path, "self.args.yaml"), "w") as f:
                yaml.dump(asdict(self.args), f, default_flow_style=False)

        # Initialise data (set dataloaders, and learning rate scheduler)
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

    def run(
        self,
        final_batch: bool = False,
    ) -> float:
        """Runs the main training and validation loop.

         Args:
            final_batch: Whether this is the final batch of the algo run. Deprecated.
        Returns:
            The model state dictionary if `return_weights` is True, else the value of
            the best metric.
        """
        if final_batch:
            warnings.warn(
                "final_batch parameter is deprecated and will be removed in a future release."
                " Memory cleanup logic moved to run_final_step() method.",
                DeprecationWarning,
                stacklevel=2,
            )
        gc.collect()
        best_metric = None
        best_epoch = None
        total_epochs = self.num_epochs - self.start_epoch
        for epoch in range(self.start_epoch, self.num_epochs):
            # call on_train_epoch_start hook
            for hook in get_hooks(HookType.ALGORITHM):
                hook.on_train_epoch_start(epoch, total_epochs, total_epochs)

            train_metrics = train_one_epoch(
                epoch,
                self.model,
                self.train_dataloader,
                self.optimizer,
                self.train_loss_fn,
                self.args,
                lr_scheduler=self.lr_scheduler,
                saver=self.saver,
                output_dir=self.save_path,
                amp_autocast=self.amp_autocast,
                loss_scaler=self.loss_scaler,
                model_ema=self.model_ema,
                mixup_fn=self.mixup_fn,
                device=self.device,
            )

            # call on_train_epoch_end hook
            for hook in get_hooks(HookType.ALGORITHM):
                hook.on_train_epoch_end(epoch, total_epochs, total_epochs)

            if self.args.distributed and self.args.dist_bn in ("broadcast", "reduce"):
                if timm_utils.is_primary(self.args):
                    logger.info("Distributing BatchNorm running means and vars")
                timm_utils.distribute_bn(
                    self.model, self.args.world_size, self.args.dist_bn == "reduce"
                )

            eval_metrics = validate(
                self.model,
                self.eval_dataloader,
                self.validate_loss_fn,
                self.args,
                device=self.device,
                amp_autocast=self.amp_autocast,
            )
            if self.model_ema is not None and not self.args.model_ema_force_cpu:
                if self.args.distributed and self.args.dist_bn in (
                    "broadcast",
                    "reduce",
                ):
                    timm_utils.distribute_bn(
                        self.model_ema,
                        self.args.world_size,
                        self.args.dist_bn == "reduce",
                    )

                ema_eval_metrics = validate(
                    self.model_ema.module,
                    self.eval_dataloader,
                    self.validate_loss_fn,
                    self.args,
                    amp_autocast=self.amp_autocast,
                    device=self.device,
                    log_suffix=" (EMA)",
                )
                eval_metrics = ema_eval_metrics

            lrs = [param_group["lr"] for param_group in self.optimizer.param_groups]
            safe_write_to_file(
                lambda x: timm_utils.update_summary(
                    epoch,
                    train_metrics,
                    eval_metrics,
                    filename=x,
                    lr=sum(lrs) / len(lrs),
                    write_header=best_metric is None,
                ),
                Path(self.save_path) / "summary.csv",
            )

            if self.saver is not None:
                # save proper checkpoint with eval metric
                save_metric = eval_metrics[self.args.eval_metric]
                best_metric, best_epoch = self.saver.save_checkpoint(
                    epoch, metric=save_metric
                )
            if self.lr_scheduler is not None:
                # step LR for next epoch
                self.lr_scheduler.step(epoch + 1, eval_metrics[self.args.eval_metric])
        if best_metric is not None:
            logger.info(
                "*** Best metric: {0} (epoch {1})".format(best_metric, best_epoch)
            )

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if self.return_weights:
            # TODO: [BIT-3286] Introduce protocol
            # return self.model.state_dict()
            logger.warning(
                "Return of fine tuned model weights is not yet supported. "
                + "Fine tuned model will be saved locally instead."
            )

        else:
            logger.federated_info("Model saved successfully.")
            return best_metric

    async def run_final_step(
        self,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any
    ) -> Any:
        """Final model cleanup step."""
        if getattr(self, 'model', None) is not None:
            del self.model
        if getattr(self, 'model_ema', None) is not None:
            del self.model_ema
        # Final cleanup
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

@delegates()
class TIMMFineTuning(BaseNonModelAlgorithmFactory[_HFModellerSide, _WorkerSide]):
    """HuggingFace TIMM Fine Tuning Algorithm.

    Args:
        datastructure: The datastructure relating to the dataset to be trained on. Defaults to None.
        model_id: The Hugging Face model ID.
        labels: The labels of the target column. Defaults to None.
        batch_transformations: The batch transformations to be applied to the batches.
            Can be a list of strings or a list of dictionaries, which will be applied
            to both training and validation, or a dictionary with keys "train" and
            "validation" mapped to a list of strings or a list of dictionaries,
            specifying the batch transformations to be applied at each individual step.
            They are only applied if `datastructure` is not passed.
            Defaults to apply DEFAULT_IMAGE_TRANSFORMATIONS to both training and validation.
        args: The training configuration.
        return_weights: Whether to return the weights of the model.
        save_path: The path to save the model to.
        **kwargs: Additional keyword arguments passed to the Worker side.

    Note:
        Either `schema` and `datastructure` must be passed or
        `image_column_name`,`target_column_name` and `labels`
        must be passed to this algorithm.

    """

    _inference_algorithm: bool = False

    def __init__(
        self,
        datastructure: DataStructure,
        model_id: str,
        labels: Optional[list[str]] = None,
        args: Optional[TIMMTrainingConfig] = None,
        return_weights: bool = False,
        save_path: Optional[Union[str, os.PathLike]] = None,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.model_id = model_id
        self.args = args or TIMMTrainingConfig()
        self.return_weights = return_weights
        self.save_path: Path = (
            config.settings.paths.output_dir if save_path is None else Path(save_path)
        )
        self.labels = labels
        # If we ever support multiple frames this needs to be looked
        # at so we ensure we support transforms via image_prefix.
        self.batch_transformations = self.datastructure.batch_transforms

        logger.debug(f"Arguments being used for fine-tuning {self.args}.")

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "args": fields.Nested(desert.schema_class(TIMMTrainingConfig), allow_none=True),
        "labels": fields.List(fields.Str(), allow_none=True),
        "return_weights": fields.Bool(required=False, default=False),
        "save_path": fields.Str(required=False, default=None),
    }

    def modeller(self, **kwargs: Any) -> _HFModellerSide:
        """Returns the modeller side of the TIMMFineTuning algorithm."""
        return _HFModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the TIMMFineTuning algorithm."""
        return _WorkerSide(
            model_id=self.model_id,
            image_column_name=self.datastructure.selected_cols[0],
            target_column_name=self.datastructure.target if isinstance(self.datastructure.target, str) else self.datastructure.target[0],
            labels=self.labels,
            batch_transformations=self.batch_transformations,
            args=self.args,
            return_weights=self.return_weights,
            save_path=self.save_path,
            **kwargs,
        )
