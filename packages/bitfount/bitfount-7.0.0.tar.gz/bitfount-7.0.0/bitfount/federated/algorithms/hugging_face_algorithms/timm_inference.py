"""Hugging Face TIMM inference Algorithm.

Adapted from: https://github.com/huggingface/api-inference-community/
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import gc
import os
from typing import Any, ClassVar, Optional, Union, cast

from marshmallow import fields
import pandas as pd

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.federated.algorithms.hugging_face_algorithms.base import _HFModellerSide
from bitfount.federated.algorithms.hugging_face_algorithms.utils import (
    get_device_for_model,
)

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    import timm
    from timm.data import (
        CustomDatasetInfo,
        ImageNetInfo,
        create_transform,
        infer_imagenet_subset,
        resolve_model_data_config,
    )
    import torch

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datastructure import DEFAULT_IMAGE_TRANSFORMATIONS, DataStructure
from bitfount.data.huggingface.utils import get_data_factory_dataset
from bitfount.data.types import (
    DataSplit,
    SingleOrMulti,
    _SemanticTypeValue,
)
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.types import T_FIELDS_DICT, _JSONDict
from bitfount.utils import delegates

logger = _get_federated_logger(__name__)


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the TIMMInference algorithm."""

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        checkpoint_path: Optional[Union[os.PathLike, str]],
        batch_size: int = 1,
        batch_transformations: Optional[list[dict[str, _JSONDict]]] = None,
        num_classes: Optional[int] = None,
        class_outputs: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = f"hf_hub:{model_id}"
        self.image_column_name = image_column_name
        self.checkpoint_path = checkpoint_path
        self.num_classes = num_classes
        self.class_outputs = class_outputs
        self.image_col_with_semantic_type: Mapping[_SemanticTypeValue, list[str]] = {
            "image": [self.image_column_name]
        }
        self.batch_transformations: list[dict[str, _JSONDict]]
        if batch_transformations is not None:
            self.batch_transformations = batch_transformations
        else:
            self.batch_transformations = [
                {
                    "albumentations": {
                        "arg": self.image_column_name,
                        "output": True,
                        "transformations": DEFAULT_IMAGE_TRANSFORMATIONS,
                        "step": "test",
                    }
                }
            ]
        # By this point self.batch_transformations is guaranteed to be set
        self.batch_size = batch_size

        # Prepopulate num_classes when not provided to match the class_outputs.
        if self.class_outputs is not None and self.num_classes is None:
            self.num_classes = len(self.class_outputs)
        self.device = get_device_for_model()

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Primarily initialises the model with the checkpoint file.

        Also initialises the transformations.
        """
        # TODO: [BIT-3097] Resolve initialise without DP
        if pod_dp:
            logger.warning("The use of DP is not supported, ignoring set `pod_dp`.")

        self.initialise_data(datasource=datasource, data_splitter=data_splitter)

        if self.checkpoint_path:
            # If checkpoint and model don't have matching num_classes
            # the below will fail with a RuntimeError.
            self.model = timm.create_model(
                self.model_id,
                num_classes=self.num_classes,
                checkpoint_path=self.checkpoint_path,
            )
        else:
            # num_classes and other config should come from config.json
            self.model = timm.create_model(
                self.model_id,
                pretrained=True,
            )
        self.model.to(self.device)
        data_factory, dataset = get_data_factory_dataset(
            datasource=datasource,
            data_split=DataSplit.TEST,
            data_splitter=data_splitter,
            selected_cols=[self.image_column_name],
            selected_cols_semantic_types=self.image_col_with_semantic_type,
            batch_transforms=self.batch_transformations,
        )
        self.test_dataloader = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )
        self.transform = create_transform(
            **resolve_model_data_config(self.model, use_test_size=True)
        )
        self.model.eval()

        dataset_info = None
        label_names = self.model.pretrained_cfg.get("label_names", None)
        label_descriptions = self.model.pretrained_cfg.get("label_descriptions", None)

        if label_names is None:
            # If no labels added to config, check if these are provided
            # explicitly as class outputs
            if self.class_outputs is not None:
                label_names = self.class_outputs
            else:
                # If no labels in config/provided explicitly, use imagenet labeller
                imagenet_subset = infer_imagenet_subset(self.model)
                if imagenet_subset:
                    dataset_info = ImageNetInfo(imagenet_subset)
                elif self.model.num_classes is not None:
                    # Otherwise use num_classes as fallback for label names
                    label_names = [f"LABEL_{i}" for i in range(self.model.num_classes)]
                else:
                    # Label fallback failed, raise exception.
                    raise ValueError(
                        "Unable to infer labels for the model. ",
                        "Please ensure that either `class_outputs` or ",
                        "`num_classes` is set.",
                    )

        if dataset_info is None:
            dataset_info = CustomDatasetInfo(
                label_names=label_names,
                label_descriptions=label_descriptions,
            )

        self.dataset_info = dataset_info

    def run(
        self, return_data_keys: bool = False, final_batch: bool = False
    ) -> pd.DataFrame:
        """Runs the inference on the images in the datasource.

        Returns:
            A dataframe with the predictions where each row is an image and each column
            is a class.
        """
        dataframe_records = []
        gc.collect()
        for _batch_idx, batch in enumerate(self.test_dataloader):
            batch = cast(
                Union[
                    list[SingleOrMulti[torch.Tensor]],
                    list[Union[SingleOrMulti[torch.Tensor], Sequence[str]]],
                ],
                batch,
            )

            input_: SingleOrMulti[torch.Tensor] = cast(
                SingleOrMulti[torch.Tensor], batch[0]
            )

            keys: Optional[list[str]]
            if self.test_dataloader.expect_key_in_iter():
                # If key is in iteration, the last element in the batch will be the
                # data keys
                keys_: SingleOrMulti[str] = cast(SingleOrMulti[str], batch[-1])
                if isinstance(keys_, str):
                    keys = [keys_]
                else:
                    keys = list(keys_)
            else:
                keys = None

            # Run the input through the model to get the output probabilities
            input_ = input_.to(self.device)  # type: ignore[union-attr] # reason: this should be a tensor by the time it is returned here # noqa: E501
            with torch.no_grad():
                out = self.model(input_)
                del input_
            probabilities = out.squeeze(0).softmax(dim=0)
            del out

            # Use topk to get the probabilities in order, and which output class
            # index they are associated with; i.e. find the mapping of output class
            # -> probability
            values, indices = torch.topk(probabilities, self.model.num_classes)

            # If the batch contained multiple inputs in one go, we need to add each
            # as a separate row to the dataframe
            if indices.dim() >= 2:
                for idx, val in zip(indices, values):
                    labels = {
                        self.dataset_info.index_to_description(
                            i, detailed=True
                        ): v.item()
                        for i, v in zip(idx, val)
                    }

                    # If keys are provided and requested, add them to the dataframe
                    # as a new column.
                    if keys and return_data_keys:
                        labels[ORIGINAL_FILENAME_METADATA_COLUMN] = keys[idx]

                    dataframe_records.append(labels)
            # Otherwise, the probabilities are only for a single input, so just add
            # that directly
            else:
                labels = {
                    self.dataset_info.index_to_description(i, detailed=True): v.item()
                    for i, v in zip(indices, values)
                }

                # If keys are provided and requested, add them to the dataframe as a
                # new column.
                if keys and return_data_keys:
                    labels[ORIGINAL_FILENAME_METADATA_COLUMN] = keys[
                        0
                    ]  # as only one entry

                dataframe_records.append(labels)

            # Free up memory between inference batches
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        # Free up memory at the end of all batches
        # del self.model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        df = pd.DataFrame.from_records(dataframe_records)
        df = df.reindex(sorted(df.columns), axis=1)
        return df


@delegates()
class TIMMInference(BaseNonModelAlgorithmFactory[_HFModellerSide, _WorkerSide]):
    """HuggingFace TIMM Inference Algorithm.

    Args:
        datastructure: The data structure to use for the algorithm.
        model_id: The model id to use from the Hugging Face Hub.
        num_classes: The number of classes in the model.
            Defaults to None.
        batch_transformations: A list of dictionaries containing the
            batch transformations. Defaults to None.
        checkpoint_path: The path to a checkpoint file local to the Pod.
            Defaults to None.
        class_outputs: A list of explict class outputs to use as labels.
            Defaults to None.

    Attributes:
        model_id: The model id to use from the Hugging Face Hub.
        num_classes: The number of classes in the model.
            Defaults to None.
        checkpoint_path: The path to a checkpoint file local to the Pod.
            Defaults to None.
        class_outputs: A list of explict class outputs to use as labels.
            Defaults to None.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.String(required=True),
        "num_classes": fields.Integer(required=False, allow_none=True),
        "batch_transformations": fields.List(fields.Dict(), allow_none=True),
        "batch_size": fields.Integer(required=False, allow_none=True),
        "checkpoint_path": fields.String(required=False, allow_none=True),
        "class_outputs": fields.List(fields.String(), allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        model_id: str,
        num_classes: Optional[int] = None,
        # batch_transformations: Optional[list[Union[str, _JSONDict]]] = None,
        batch_size: int = 1,
        checkpoint_path: Optional[Union[os.PathLike, str]] = None,
        class_outputs: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.model_id = model_id
        self.num_classes = num_classes
        self.checkpoint_path = checkpoint_path
        self.class_outputs = class_outputs
        self.batch_size = batch_size

        if self.num_classes is None and self.class_outputs is None:
            raise ValueError(
                "Either `num_classes` or `class_outputs` must be provided "
                "for `TIMMInference` initialisation. Currently, both are missing."
            )
        elif self.num_classes is not None and self.class_outputs is not None:
            # Ensure both represent the same number of classes.
            if self.num_classes != len(self.class_outputs):
                raise ValueError(
                    "The `num_classes` and the length of `class_outputs` ",
                    "must be the same. ",
                    f"Currently, `num_classes` is {self.num_classes} and ",
                    f"`class_outputs` has {len(self.class_outputs)} elements.",
                )

    def modeller(self, **kwargs: Any) -> _HFModellerSide:
        """Returns the modeller side of the TIMMInference algorithm."""
        return _HFModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the TIMMInference algorithm."""
        return _WorkerSide(
            model_id=self.model_id,
            image_column_name=self.datastructure.selected_cols[0],
            num_classes=self.num_classes,
            batch_transformations=self.datastructure.batch_transforms,
            batch_size=self.batch_size,
            checkpoint_path=self.checkpoint_path,
            class_outputs=self.class_outputs,
            **kwargs,
        )
