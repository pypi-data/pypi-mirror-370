"""Pytorch Lightning Callbacks to trigger Bitfount Epoch Hooks."""

from __future__ import annotations

import pytorch_lightning as pl
from pytorch_lightning.callbacks import Callback

from bitfount.hooks import HookType, get_hooks


class EpochCallbacks(Callback):
    """Pytorch Lightning Callbacks to trigger Bitfount Epoch Hooks."""

    def on_train_epoch_start(
        self, trainer: pl.Trainer, pl_module: pl.LightningModule
    ) -> None:
        """Called when the train epoch begins."""
        for hook in get_hooks(HookType.ALGORITHM):
            hook.on_train_epoch_start(
                trainer.current_epoch, trainer.min_epochs, trainer.max_epochs
            )

    def on_train_epoch_end(
        self, trainer: pl.Trainer, pl_module: pl.LightningModule
    ) -> None:
        """Called when the train epoch ends."""
        for hook in get_hooks(HookType.ALGORITHM):
            hook.on_train_epoch_end(
                trainer.current_epoch, trainer.min_epochs, trainer.max_epochs
            )
