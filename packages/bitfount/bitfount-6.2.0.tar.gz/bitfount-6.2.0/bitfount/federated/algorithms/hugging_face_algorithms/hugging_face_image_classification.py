"""Hugging Face Image Classification Algorithm."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import gc
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union, cast
import warnings

from marshmallow import fields
import pandas as pd

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.huggingface.dataloaders import (
    HuggingFaceBitfountDataLoader,
    HuggingFaceIterableBitfountDataLoader,
)
from bitfount.federated.algorithms.hugging_face_algorithms.utils import (
    get_device_for_model,
)
from bitfount.federated.authorisation_checkers import ProtocolContext

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    import torch
    from transformers import (
        AutoImageProcessor,
        AutoModelForImageClassification,
        set_seed,
    )

from bitfount.data.huggingface.utils import get_data_factory_dataset
from bitfount.data.types import (
    DataSplit,
    SingleOrMulti,
    _SemanticTypeValue,
)
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    FinalStepAlgorithm,
)
from bitfount.federated.algorithms.hugging_face_algorithms.base import _HFModellerSide
from bitfount.federated.logging import _get_federated_logger
from bitfount.utils import DEFAULT_SEED, delegates

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.federated.privacy.differential import DPPodConfig
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger(__name__)


class _WorkerSide(BaseWorkerAlgorithm, FinalStepAlgorithm):
    """Worker side of the HuggingFaceImageClassificationInference algorithm."""

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        apply_softmax_to_predictions: bool = True,
        batch_size: int = 1,
        seed: int = DEFAULT_SEED,
        top_k: int = 5,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.batch_size = batch_size
        self.top_k = top_k
        self.seed = seed
        self.image_column_name = image_column_name
        self.image_col_with_semantic_type: Mapping[_SemanticTypeValue, list[str]] = {
            "image": [self.image_column_name]
        }
        self.apply_softmax_to_predictions = apply_softmax_to_predictions
        self.device = get_device_for_model()

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
            selected_cols=[self.image_column_name],
            selected_cols_semantic_types=self.image_col_with_semantic_type,
            batch_transforms=[],
        )
        self.test_dataloader: Union[
            HuggingFaceBitfountDataLoader, HuggingFaceIterableBitfountDataLoader
        ] = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )
        set_seed(self.seed)
        self.image_processor = AutoImageProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForImageClassification.from_pretrained(self.model_id)
        self.model.to(self.device)
        # Update top_k if it is higher than the number of labels defined by the model
        if self.top_k > self.model.config.num_labels:
            logger.warning(
                f"The provided `top_k` ({self.top_k}) is higher than the number of "
                f"labels defined by the model ({self.model.config.num_labels}). "
                f"Setting `top_k` to {self.model.config.num_labels}."
            )
            self.top_k = self.model.config.num_labels

    def run(
        self, return_data_keys: bool = False, final_batch: bool = False
    ) -> pd.DataFrame:
        """Runs inference on the given image classification HuggingFace model.

        Args:
            return_data_keys: Whether to return data keys
            final_batch: Whether this is the final batch of the algo run. Deprecated.
        """
        if final_batch:
            warnings.warn(
                "final_batch parameter is deprecated and will be removed in a "
                "future release. Memory cleanup logic moved to run_final_step() "
                "method.",
                DeprecationWarning,
                stacklevel=2,
            )
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

            input_ = self.image_processor(images=batch[0], return_tensors="pt")
            input_ = input_.to(self.device)

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

            with torch.no_grad():
                outputs = self.model(**input_)
            del input_

            if self.apply_softmax_to_predictions:
                # Apply the same softmax as it is in the HF ImageClassificationPipeline
                probabilities = outputs.logits.softmax(-1)[0]
            else:
                probabilities = outputs.logits
            del outputs

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            values, indices = probabilities.topk(self.top_k)
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
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        df = pd.DataFrame.from_records(dataframe_records)
        df = df.reindex(sorted(df.columns), axis=1)
        return df

    async def run_final_step(
        self, context: Optional[ProtocolContext] = None, **kwargs: Any
    ) -> Any:
        """Final model cleanup step."""
        if hasattr(self, "model"):
            del self.model
        # Additional cleanup for final step
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


@delegates()
class HuggingFaceImageClassificationInference(
    BaseNonModelAlgorithmFactory[_HFModellerSide, _WorkerSide]
):
    """Inference for pre-trained Hugging Face image classification models.

    Args:
        datastructure: The datastructure to use for the algorithm.
        model_id: The model id to use for image classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        batch_size: The batch size for inference. Defaults to 1.
        top_k: The number of top labels that will be returned by the pipeline.
            If the provided number is higher than the number of labels available
            in the model configuration, it will default to the number of labels.
            Defaults to 5.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.

    Attributes:
        model_id: The model id to use for image classification inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        batch_size: The batch size for inference. Defaults to 1.
        top_k: The number of top labels that will be returned by the pipeline.
            If the provided number is higher than the number of labels available
            in the model configuration, it will default to the number of labels.
            Defaults to 5.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
    """

    def __init__(
        self,
        datastructure: DataStructure,
        model_id: str,
        seed: int = DEFAULT_SEED,
        apply_softmax_to_predictions: bool = True,
        batch_size: int = 1,
        top_k: int = 5,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.model_id = model_id
        self.batch_size = batch_size
        self.top_k = top_k
        self.seed = seed
        self.apply_softmax_to_predictions = apply_softmax_to_predictions

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "batch_size": fields.Int(required=False),
        "top_k": fields.Int(required=False),
        "seed": fields.Int(required=False, missing=DEFAULT_SEED),
        "apply_softmax_to_predictions": fields.Bool(required=False),
    }

    def modeller(self, **kwargs: Any) -> _HFModellerSide:
        """Returns the modeller side of the HuggingFaceImageClassificationInference algorithm."""  # noqa: E501
        return _HFModellerSide(task_name="image_classification", **kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the HuggingFaceImageClassification algorithm."""
        return _WorkerSide(
            model_id=self.model_id,
            image_column_name=self.datastructure.selected_cols[0],
            top_k=self.top_k,
            apply_softmax_to_predictions=self.apply_softmax_to_predictions,
            batch_size=self.batch_size,
            seed=self.seed,
            **kwargs,
        )
