"""Algorithm to evaluate a model on remote data."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar, List, Optional, Union, cast

from marshmallow import fields
import numpy as np
import pandas as pd

from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithmFactory,
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.post_processing_utils import (
    create_postprocessors,
)
from bitfount.federated.authorisation_checkers import ModelURLs, ProtocolContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.transport.message_service import (
    ResourceConsumed,
    ResourceType,
)
from bitfount.hub.api import BitfountHub
from bitfount.types import PredictReturnType, _SerializedWeights
from bitfount.utils import delegates

if TYPE_CHECKING:
    from bitfount.types import (
        T_FIELDS_DICT,
        DistributedModelProtocol,
        _DistributedModelTypeOrReference,
    )

logger = _get_federated_logger(__name__)


class _ModellerSide(_BaseModellerModelAlgorithm):
    """Modeller side of the ModelInference algorithm."""

    def run(
        self, results: Mapping[str, Union[list[np.ndarray], pd.DataFrame]]
    ) -> dict[str, Union[list[np.ndarray], pd.DataFrame]]:
        """Simply returns predictions."""
        return dict(results)


class _WorkerSide(_BaseWorkerModelAlgorithm):
    """Worker side of the ModelInference algorithm."""

    def __init__(
        self,
        *,
        model: DistributedModelProtocol,
        class_outputs: Optional[list[str]] = None,
        maybe_bitfount_model_slug: Optional[str] = None,
        postprocessors: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        super().__init__(model=model, **kwargs)
        self.class_outputs = class_outputs
        self.maybe_bitfount_model_slug = maybe_bitfount_model_slug
        self.num_inferences_performed: Optional[int] = None
        self.postprocessors = (
            create_postprocessors(postprocessors) if postprocessors else []
        )

    def run(
        self,
        model_params: Optional[_SerializedWeights] = None,
        return_data_keys: bool = False,
        **kwargs: Any,
    ) -> Union[PredictReturnType, pd.DataFrame]:
        """Runs inference and returns results."""
        if model_params is not None:
            self.update_params(model_params)

        # mypy: as we are in the worker-side of the algorithm, we know that
        # _predict_local() will be the actual underlying call, and that that returns
        # PredictReturnType
        predict_output: PredictReturnType = cast(
            PredictReturnType, self.model.predict(self.datasource)
        )
        # Assuming that the prediction count equals the number of input records
        self.num_inferences_performed = len(predict_output.preds)

        # Process output with class_outputs if provided
        output = self._process_class_outputs(predict_output, return_data_keys)
        # Apply postprocessors in sequence
        if self.postprocessors:
            output = self.apply_postprocessors(output)
        return output

    def _process_class_outputs(
        self, predict_output: PredictReturnType, return_data_keys: bool
    ) -> Union[PredictReturnType, pd.DataFrame]:
        """Process the prediction output with class_outputs if provided."""
        # TODO: [BIT-3620] revisit outputs after this ticket is done.
        # At the moment, the pytorch built-in models return the
        # predictions based on the number of frames, which
        # should not be the case. I.e. a file that has 2 frames
        # will return a list of two values adding up to 1 as predictions,
        # whereas a file that has 3 frames returns a list of three values
        # adding up to 1. This is not the desired behaviour, and added
        # to do here as this algo might need updating after we handle that.
        if self.class_outputs:
            df: Optional[pd.DataFrame] = None

            if isinstance(predict_output.preds, pd.DataFrame):
                df = predict_output.preds

                if not set(self.class_outputs).issubset(df.columns):
                    logger.warning(
                        "Class outputs provided do not match"
                        " the model prediction output."
                        f" You provided a list of {len(self.class_outputs)}, and"
                        f" this differs from the output dataframe."
                        " Outputting predictions as-is."
                    )
            else:  # preds is list[np.ndarray]
                # If all the arrays have the same length, we can make a dataframe
                if all(
                    prediction.shape[0] == len(self.class_outputs)
                    for prediction in predict_output.preds
                ):
                    df = pd.DataFrame(
                        data=predict_output.preds, columns=self.class_outputs
                    )
                else:
                    logger.warning(
                        "Class outputs provided do not match"
                        " the model prediction output."
                        f" You provided a list of {len(self.class_outputs)}, and"
                        f" not all the model predictions are of the same shape."
                        " Outputting predictions as a list of numpy arrays."
                    )

            if df is not None:  # i.e. we've created a dataframe
                # If keys are provided and requested, add them to the dataframe as a
                # new column.
                if predict_output.keys is not None and return_data_keys:
                    df[ORIGINAL_FILENAME_METADATA_COLUMN] = predict_output.keys

                return df

        # We will fall back to this if either there aren't self.class_outputs OR if
        # we couldn't create a dataframe as requested above.
        if not return_data_keys:
            # If data keys have not been requested, null out their potential entry
            predict_output.keys = None

        return predict_output

    def get_resources_consumed(self) -> List[ResourceConsumed]:
        """Return resources consumed by this model inference execution.

        Only supports number of model inferences for private bitfount models.
        """
        resources_consumed: List[ResourceConsumed] = []

        if (
            self.num_inferences_performed is not None
            and self.maybe_bitfount_model_slug is not None
        ):
            resources_consumed.append(
                ResourceConsumed(
                    resource_type=ResourceType.MODEL_INFERENCE,
                    resource_identifier=self.maybe_bitfount_model_slug,
                    amount=self.num_inferences_performed,
                )
            )

        return resources_consumed

    def apply_postprocessors(self, predictions: Any) -> Any:
        """Apply a list of postprocessors to predictions in sequence.

        Args:
            predictions: Model predictions to process.
            postprocessors: List of postprocessor instances.

        Returns:
            Processed predictions
        """
        result = predictions
        for i, postprocessor in enumerate(self.postprocessors):
            try:
                result = postprocessor.process(result)
            except Exception as e:
                # Continue with current result rather than failing
                logger.error(f"Error in postprocessor {i + 1}: {e}")
        return result


@delegates()
class ModelInference(_BaseModelAlgorithmFactory[_ModellerSide, _WorkerSide]):
    """Algorithm for running inference on a model and returning the predictions.

    :::danger

    This algorithm could potentially return the data unfiltered so should only be used
    when the other party is trusted.

    :::

    Args:
        model: The model to infer on remote data.
        class_outputs: A list of strings corresponding to prediction outputs.
            If provided, the model will return a dataframe of results with the
            class outputs list elements as columns. Defaults to None.
        postprocessors: Post-processing configuration, which can be either a
            preset string or a list of postprocessor configuration dicts.

    Attributes:
        model: The model to infer on remote data.
        class_outputs: A list of strings corresponding to prediction outputs.
            If provided, the model will return a dataframe of results with the
            class outputs list elements as columns. Defaults to None.
        postprocessors: A list of postprocessor configuration dicts.
            Defaults to None.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "class_outputs": fields.List(fields.String(), allow_none=True),
        "postprocessors": fields.List(
            fields.Dict(
                keys=fields.String(),
            ),
            allow_none=True,
        ),
    }

    def __init__(
        self,
        *,
        model: _DistributedModelTypeOrReference,
        class_outputs: Optional[list[str]] = None,
        postprocessors: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        self.class_outputs = class_outputs
        self.postprocessors = postprocessors
        super().__init__(model=model, **kwargs)

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the ModelInference algorithm."""
        model = self._get_model_from_reference_and_upload_weights(
            project_id=self.project_id
        )
        return _ModellerSide(model=model, **kwargs)

    def worker(
        self,
        *,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Returns the worker side of the ModelInference algorithm.

        Args:
            hub: `BitfountHub` object to use for communication with the hub.
            context: Optional. Run-time protocol context details for running.
                May contain URLs for downloading models directly rather than from
                the hub.
            **kwargs: Additional keyword arguments to pass to the worker side.

        Returns:
            Worker side of the ModelInference algorithm.
        """
        model_urls: Optional[dict[str, ModelURLs]] = (
            context.model_urls if context else None
        )
        model_slug: Optional[str] = (
            self.model.model_id
            if isinstance(self.model, BitfountModelReference)
            else None
        )
        model = self._get_model_and_download_weights(
            hub=hub,
            project_id=self.project_id,
            auth_model_urls=model_urls,
        )
        return _WorkerSide(
            model=model,
            class_outputs=self.class_outputs,
            maybe_bitfount_model_slug=model_slug,
            postprocessors=self.postprocessors,
            **kwargs,
        )
