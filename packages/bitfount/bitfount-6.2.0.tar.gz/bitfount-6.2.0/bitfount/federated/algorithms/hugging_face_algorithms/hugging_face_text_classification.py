"""Hugging Face Text Classification Algorithm."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Union, cast

from marshmallow import fields
import numpy as np
import pandas as pd

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.huggingface.dataloaders import (
    HuggingFaceBitfountDataLoader,
    HuggingFaceIterableBitfountDataLoader,
)
from bitfount.federated.algorithms.hugging_face_algorithms.base import _HFModellerSide

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, set_seed

from bitfount.data.datasources.base_source import BaseSource
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
from bitfount.types import T_FIELDS_DICT
from bitfount.utils import DEFAULT_SEED, delegates

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig


logger = _get_federated_logger(__name__)
_FunctionToApply = Literal["sigmoid", "softmax", "none"]


def sigmoid(_outputs: np.ndarray) -> torch.Tensor:
    """Sigmoid function for output postprocessing."""
    return torch.from_numpy(1.0 / (1.0 + np.exp(-_outputs)))


def softmax(_outputs: np.ndarray) -> torch.Tensor:
    """Softmax function for output postprocessing."""
    maxes = np.max(_outputs, axis=-1, keepdims=True)
    shifted_exp = np.exp(_outputs - maxes)
    return torch.from_numpy(shifted_exp / shifted_exp.sum(axis=-1, keepdims=True))


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the HuggingFaceTextClassificationInference algorithm."""

    def __init__(
        self,
        model_id: str,
        target_column_name: str,
        batch_size: int = 1,
        function_to_apply: Optional[_FunctionToApply] = None,
        seed: int = DEFAULT_SEED,
        top_k: int = 1,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.target_column_name = target_column_name
        self.target_col_with_semantic_type: Mapping[_SemanticTypeValue, list[str]] = {
            "text": [self.target_column_name]
        }
        self.batch_size = batch_size
        self.function_to_apply = function_to_apply
        self.seed = seed
        self.top_k = top_k

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the model and tokenizer."""
        # TODO: [BIT-3097] Resolve initialise without DP
        if pod_dp:
            logger.warning("The use of DP is not supported, ignoring set `pod_dp`.")
        self.initialise_data(datasource=datasource)
        data_factory, dataset = get_data_factory_dataset(
            datasource=datasource,
            data_splitter=data_splitter,
            data_split=DataSplit.TEST,
            selected_cols=[self.target_column_name],
            selected_cols_semantic_types=self.target_col_with_semantic_type,
            batch_transforms=[],
        )
        self.test_dataloader: Union[
            HuggingFaceBitfountDataLoader, HuggingFaceIterableBitfountDataLoader
        ] = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )
        set_seed(self.seed)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_id)
        if self.top_k > self.model.config.num_labels:
            logger.warning(
                f"The provided `top_k` ({self.top_k}) is higher than the number of "
                f"labels defined by the model ({self.model.config.num_labels}). "
                f"Setting `top_k` to {self.model.config.num_labels}."
            )
            self.top_k = self.model.config.num_labels

    def run(
        self, return_data_keys: bool = False, final_batch: bool = False
    ) -> Union[pd.DataFrame, list[list[dict[str, Union[str, float]]]], dict[str, Any]]:
        """Runs the pipeline to generate text."""
        dataframe_records = []
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
            # TODO: [BIT-3581] Check that this is as intended, as it was flagged by
            #       mypy as being an incompatible types
            if isinstance(input_[0], tuple):  # type: ignore[unreachable] # Reason: see above # noqa: E501
                input_ = [item[0] for item in input_]  # type: ignore[unreachable] # Reason: see above # noqa: E501
            input_ = self.tokenizer(input_, return_tensors="pt")
            with torch.no_grad():
                model_outputs = self.model(**input_)

            # Get and apply the right post-processing function
            if self.function_to_apply is None:
                if (
                    self.model.config.problem_type == "multi_label_classification"
                    or self.model.config.num_labels == 1
                ):
                    self.function_to_apply = "sigmoid"
                elif (
                    self.model.config.problem_type == "single_label_classification"
                    or self.model.config.num_labels > 1
                ):
                    self.function_to_apply = "softmax"
                elif (
                    hasattr(self.model.config, "function_to_apply")
                    and self.function_to_apply is None
                ):
                    self.function_to_apply = self.model.config.function_to_apply
                else:
                    self.function_to_apply = "none"

            # Extract the logits, convert to numpy and
            # apply the post-processing function
            outputs = model_outputs["logits"]
            outputs = outputs.numpy()
            if self.function_to_apply == "sigmoid":
                probabilities = sigmoid(outputs)
            elif self.function_to_apply == "softmax":
                probabilities = softmax(outputs)
            elif self.function_to_apply == "none":
                probabilities = outputs
            else:
                raise ValueError(
                    "Unrecognized `function_to_apply` "
                    f"argument: {self.function_to_apply}"
                )

            values, indices = torch.topk(probabilities, self.top_k)
            if indices.dim() >= 2:
                for idx, (pred_idx, val) in enumerate(zip(indices, values)):
                    labels = {
                        self.model.config.id2label[i.item()]: v.item()
                        for i, v in zip(pred_idx, val)
                    }
                    # If keys are provided and requested, add them to the dataframe
                    # as a new column.
                    if keys and return_data_keys:
                        labels[ORIGINAL_FILENAME_METADATA_COLUMN] = keys[idx]
                    dataframe_records.append(labels)
            else:
                labels = {
                    self.model.config.id2label[i.item()]: v.item()
                    for i, v in zip(indices, values)
                }

                # If keys are provided and requested, add them to the dataframe as a
                # new column.
                if keys and return_data_keys:
                    labels[ORIGINAL_FILENAME_METADATA_COLUMN] = keys[
                        0
                    ]  # as only one entry

                dataframe_records.append(labels)

        df = pd.DataFrame.from_records(dataframe_records)
        df = df.reindex(sorted(df.columns), axis=1)
        return df


@delegates()
class HuggingFaceTextClassificationInference(
    BaseNonModelAlgorithmFactory[_HFModellerSide, _WorkerSide]
):
    """Inference for pre-trained Hugging Face text classification models.

    Args:
        datastructure: The data structure to use for the algorithm.
        model_id: The model id to use for text classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        batch_size: The batch size for inference. Defaults to 1.
        function_to_apply: The function to apply to the model outputs in order
            to retrieve the scores. Accepts four different values: if this argument
            is not specified, then it will apply the following functions according
            to the number of labels - if the model has a single label, will apply
            the `sigmoid` function on the output; if the model has several labels,
            will apply the `softmax` function on the output. Possible values are:
            "sigmoid": Applies the sigmoid function on the output.
            "softmax": Applies the softmax function on the output.
            "none": Does not apply any function on the output. Default to None.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
        top_k: The number of top labels that will be returned by the pipeline.
            Defaults to 1.

    Attributes:
        model_id: The model id to use for text classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        batch_size: The batch size for inference. Defaults to 1.
        function_to_apply: The function to apply to the model outputs in order
            to retrieve the scores. Accepts four different values: if this argument
            is not specified, then it will apply the following functions according
            to the number of labels - if the model has a single label, will apply
            the `sigmoid` function on the output; if the model has several labels,
            will apply the `softmax` function on the output. Possible values are:
            "sigmoid": Applies the sigmoid function on the output.
            "softmax": Applies the softmax function on the output.
            "none": Does not apply any function on the output. Default to None.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
        top_k: The number of top labels that will be returned by the pipeline.
            Defaults to 1.
    """

    def __init__(
        self,
        datastructure: DataStructure,
        model_id: str,
        batch_size: int = 1,
        function_to_apply: Optional[_FunctionToApply] = None,
        seed: int = DEFAULT_SEED,
        top_k: int = 1,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.model_id = model_id
        self.batch_size = batch_size
        self.function_to_apply = function_to_apply
        self.seed = seed
        self.top_k = top_k

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "batch_size": fields.Int(required=False),
        "function_to_apply": fields.Str(required=False, allow_none=True),
        "seed": fields.Int(required=False, missing=DEFAULT_SEED),
        "top_k": fields.Int(required=False),
    }

    def modeller(self, **kwargs: Any) -> _HFModellerSide:
        """Returns the modeller side of the HuggingFaceTextClassificationInference algorithm."""  # noqa: E501
        return _HFModellerSide(task_name="text_classification", **kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the HuggingFaceTextClassificationInference algorithm."""  # noqa: E501
        return _WorkerSide(
            model_id=self.model_id,
            target_column_name=self.datastructure.selected_cols[0],
            batch_size=self.batch_size,
            function_to_apply=self.function_to_apply,
            seed=self.seed,
            top_k=self.top_k,
            **kwargs,
        )
