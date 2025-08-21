"""Hugging Face Perplexity Algorithm.

Reference:
https://huggingface.co/docs/transformers/perplexity#example-calculating-perplexity-with-gpt2-in-transformers
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Optional, Sequence, Union, cast

from marshmallow import fields
import pandas as pd

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.huggingface.utils import get_data_factory_dataset
from bitfount.data.types import DataSplit, SingleOrMulti

if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
)
from bitfount.federated.algorithms.hugging_face_algorithms.base import _HFModellerSide
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.utils import DEFAULT_SEED, delegates

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource
    from bitfount.data.huggingface.dataloaders import (
        HuggingFaceBitfountDataLoader,
        HuggingFaceIterableBitfountDataLoader,
    )
    from bitfount.types import T_FIELDS_DICT

DEFAULT_STRIDE = 512


logger = _get_federated_logger(__name__)


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the HuggingFacePerplexityEvaluation algorithm."""

    def __init__(
        self,
        model_id: str,
        text_column_name: str,
        stride: int,
        seed: int,
        batch_size: int = 1,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.text_column_name = text_column_name
        self.stride = stride
        self.seed = seed
        self.batch_size = batch_size

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
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)
        data_factory, dataset = get_data_factory_dataset(
            datasource=datasource,
            data_splitter=data_splitter,
            data_split=DataSplit.TEST,
            selected_cols=[self.text_column_name],
            selected_cols_semantic_types={"text": [self.text_column_name]},
            batch_transforms=[],
        )
        self.test_dataloader: Union[
            HuggingFaceBitfountDataLoader, HuggingFaceIterableBitfountDataLoader
        ] = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )
        set_seed(self.seed)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, trust_remote_code=True
        )

    def run(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        """Runs the pipeline to compute perplexities.

        The function calculates perplexity for each prompt in the
        provided data source. Perplexity is the average exponentiated
        loss obtained from the model. To handle fixed-length causal language
        models with a maximum context, we utilize a sliding window strategy.
        This strategy breaks the sequence into subsequences with a sliding
        context window, preventing poor approximation of the fully-factorized
        perplexity. This approach ensures that the model has sufficient
        context when making each prediction, leading to more accurate results.
        """
        # TODO: [BIT-3851] Make use `return_data_keys` for FileIterableDatasources
        # This should also ensure that the input_ and the keys are properly split.
        perplexities = []
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
            # TODO: [BIT-3581] Check that this is as intended, as it was flagged by
            #       mypy as being an incompatible types
            if isinstance(input_[0], tuple):  # type: ignore[unreachable] # Reason: see above # noqa: E501
                input_ = [item[0] for item in input_]  # type: ignore[unreachable] # Reason: see above # noqa: E501
            encodings = self.tokenizer(input_, return_tensors="pt")
            # model's maximum context size (tokens)
            max_length = self.model.config.n_positions
            # The number of tokens as context when calculating conditional likelihood
            # of any one token (see DEFAULT_STRIDE)
            stride = self.stride
            seq_len = encodings.input_ids.size(1)

            nlls = []
            prev_end_loc = 0
            # Sliding window strategy
            for begin_loc in range(0, seq_len, stride):
                end_loc = min(begin_loc + max_length, seq_len)
                trg_len = end_loc - prev_end_loc
                input_ids = encodings.input_ids[:, begin_loc:end_loc]
                target_ids = input_ids.clone()
                # Avoid token overlap from influencing loss
                # by setting to -100.
                target_ids[:, :-trg_len] = -100

                with torch.no_grad():
                    outputs = self.model(input_ids, labels=target_ids)
                    # Loss = trg_len - 1 (internal shift of labels to the left by 1)
                    neg_log_likelihood = outputs.loss

                nlls.append(neg_log_likelihood)

                prev_end_loc = end_loc
                if end_loc == seq_len:
                    break

            ppl = torch.exp(torch.stack(nlls).mean()).item()
            perplexities.append(ppl)

        return pd.DataFrame({"results": perplexities})


@delegates()
class HuggingFacePerplexityEvaluation(
    BaseNonModelAlgorithmFactory[_HFModellerSide, _WorkerSide]
):
    """Hugging Face Perplexity Algorithm.

    Args:
        datastructure: The data structure to use for the algorithm.
        model_id: The model id to use for evaluating its perplexity.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts models with a causal language
            modeling head.
        stride: Sets the stride of the algorithm. Defaults to 512.
        seed: Sets the seed of the algorithm. For reproducible behaviour
            it defaults to 42.

    Attributes:
        model_id: The model id to use for evaluation.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts models with a causal language
            modeling head.
        text_column_name: The single column to query against. Should contain
            text for generation.
        stride: Sets the stride of the algorithm. Defaults to 512.
        seed: Sets the seed of the algorithm. For reproducible behaviour
            it defaults to 42.
    """

    def __init__(
        self,
        datastructure: DataStructure,
        model_id: str,
        stride: int = DEFAULT_STRIDE,
        seed: int = DEFAULT_SEED,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.model_id = model_id
        self.stride = stride
        self.seed = seed

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "stride": fields.Int(required=False, missing=DEFAULT_STRIDE),
        "seed": fields.Int(required=False, missing=DEFAULT_SEED),
    }

    def modeller(self, **kwargs: Any) -> _HFModellerSide:
        """Returns the modeller side of the HuggingFacePerplexityEvaluation algorithm."""  # noqa: E501
        return _HFModellerSide(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the HuggingFacePerplexityEvaluation algorithm."""  # noqa: E501
        return _WorkerSide(
            model_id=self.model_id,
            text_column_name=self.datastructure.selected_cols[0],
            stride=self.stride,
            seed=self.seed,
            **kwargs,
        )
