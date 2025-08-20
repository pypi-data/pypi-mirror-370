"""Hugging Face Image Segmentation Algorithm."""

from __future__ import annotations

from collections.abc import Mapping
import gc
import os
from pathlib import Path
import typing
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, Union
import warnings

import cv2
from marshmallow import fields
from marshmallow.validate import OneOf
import numpy as np
import pandas as pd
import PIL

from bitfount.config import _PYTORCH_ENGINE, BITFOUNT_ENGINE
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
    from transformers import AutoImageProcessor, AutoModelForImageSegmentation, set_seed

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import ORIGINAL_FILENAME_METADATA_COLUMN
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
from bitfount.types import T_FIELDS_DICT
from bitfount.utils import DEFAULT_SEED, delegates

if TYPE_CHECKING:
    from bitfount.federated.privacy.differential import DPPodConfig

logger = _get_federated_logger(__name__)

_Subtask = Literal["semantic", "instance", "panoptic"]


class _WorkerSide(BaseWorkerAlgorithm, FinalStepAlgorithm):
    """Worker side of the HuggingFaceImageSegmentationInference algorithm."""

    def __init__(
        self,
        model_id: str,
        image_column_name: str,
        alpha: float = 0.3,
        batch_size: int = 1,
        dataframe_output: bool = False,
        mask_threshold: float = 0.5,
        overlap_mask_area_threshold: float = 0.5,
        save_path: Union[str, os.PathLike] = config.settings.paths.output_dir,
        seed: int = DEFAULT_SEED,
        subtask: Optional[_Subtask] = None,
        threshold: float = 0.9,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.image_column_name = image_column_name
        self.batch_size = batch_size
        self.subtask = subtask
        self.threshold = threshold
        self.mask_threshold = mask_threshold
        self.overlap_mask_area_threshold = overlap_mask_area_threshold
        self.seed = seed
        self.save_path = Path(save_path)
        self.alpha = alpha
        self.dataframe_output = dataframe_output
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
        # Add the filename column to the selected columns as text,
        # so we can use it for saving images with masks
        if isinstance(self.datasource, FileSystemIterableSource):
            selected_cols = [self.image_column_name, ORIGINAL_FILENAME_METADATA_COLUMN]
            selected_cols_semantic_types: Mapping[_SemanticTypeValue, list[str]] = {
                "image": [self.image_column_name],
                "text": [ORIGINAL_FILENAME_METADATA_COLUMN],
            }
        else:
            selected_cols = [self.image_column_name]
            selected_cols_semantic_types = {
                "image": [self.image_column_name],
                "text": [self.image_column_name],
            }
        data_factory, dataset = get_data_factory_dataset(
            datasource=datasource,
            data_splitter=data_splitter,
            data_split=DataSplit.TEST,
            selected_cols=selected_cols,
            selected_cols_semantic_types=selected_cols_semantic_types,
            batch_transforms=[],
        )
        self.test_dataloader: Union[
            HuggingFaceBitfountDataLoader, HuggingFaceIterableBitfountDataLoader
        ] = data_factory.create_dataloader(
            dataset, batch_size=self.batch_size, **kwargs
        )
        set_seed(self.seed)
        self.image_processor = AutoImageProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForImageSegmentation.from_pretrained(self.model_id)
        self.model.to(self.device)

    @staticmethod
    def _draw_masks_on_original_image(
        image: torch.Tensor, masks_generated: list[Any], alpha: float = 0.3
    ) -> tuple[Any, list[dict[str, Any]]]:
        """Draw the segmentation masks on the original image.

        Args:
            image: The path to the original image.
            masks_generated: The list with predictions returned
                by the huggingface model.
            alpha: The weight of the first image. Defaults to 0.3.

        """
        # Convert to RGB to account for pngs which add the extra alpha layer
        img = PIL.Image.fromarray(image.numpy().astype(np.uint8)).convert("RGB")
        orig_image = np.array(img).reshape(img.size[0], img.size[1], 3).copy()
        masked_image = orig_image.copy()
        for i in range(len(masks_generated)):
            reshape_mask = (
                np.array(masks_generated[i]).reshape(img.size[0], img.size[1]).copy()
            )
            masked_image = np.where(
                np.repeat(
                    np.array(reshape_mask).astype(int)[:, :, np.newaxis],
                    3,
                    axis=2,
                ),
                np.random.choice(range(256), size=3),
                masked_image,
            )

            masked_image = masked_image.astype(np.uint8)
        return (
            cv2.addWeighted(orig_image, alpha, masked_image, 1 - alpha, 0),
            masks_generated,
        )

    def run(
        self, return_data_keys: bool = False, final_batch: bool = False
    ) -> Union[
        pd.DataFrame, dict[str, tuple[str, str]], dict[str, tuple[str, str, str]]
    ]:
        """Runs inference on the given image segmentation HuggingFace model.

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
        gc.collect()

        final_img_path_list = []
        final_prediction_list = []
        keys_list: list[str] = []

        orig_images_storage_locations: list[str] = []

        # Load subtask from the image processor, there are specific post-processing
        # functions for each subtask. There are 2 different ways of applying the
        # post-processing on for when the subtask is panoptic or instance and one
        # for when the subtask is semantic or none.
        fn = None
        if self.subtask in {"panoptic", None} and hasattr(
            self.image_processor, "post_process_panoptic_segmentation"
        ):
            fn = self.image_processor.post_process_panoptic_segmentation
        elif self.subtask in {"instance", None} and hasattr(
            self.image_processor, "post_process_instance_segmentation"
        ):
            fn = self.image_processor.post_process_instance_segmentation

        for _batch_idx, batch in enumerate(self.test_dataloader):
            batch = typing.cast(
                Union[
                    list[SingleOrMulti[torch.Tensor]],
                    list[Union[SingleOrMulti[torch.Tensor], typing.Sequence[str]]],
                ],
                batch,
            )

            images: SingleOrMulti[torch.Tensor] = typing.cast(
                SingleOrMulti[torch.Tensor], batch[0]
            )
            images_storage_location: SingleOrMulti[torch.Tensor] = typing.cast(
                SingleOrMulti[torch.Tensor], batch[1]
            )

            keys: Optional[list[str]]
            if self.test_dataloader.expect_key_in_iter():
                # If key is in iteration, the last element in the batch will be the
                # data keys
                keys_: SingleOrMulti[str] = typing.cast(SingleOrMulti[str], batch[-1])
                if isinstance(keys_, str):
                    keys = [keys_]
                else:
                    keys = list(keys_)
            else:
                keys = None

            # TODO: [BIT-3581] Check that this is as intended, as it was flagged by
            #       mypy as being an incompatible types
            if isinstance(images_storage_location[0], tuple):  # type: ignore[unreachable] # Reason: see above # noqa: E501
                # Extract the image filename to a list
                images_storage_location = [item for item in images_storage_location[0]]  # type: ignore[unreachable] # Reason: see above # noqa: E501

            for index in range(self.batch_size):
                # Process the images one by one
                image = images[index]
                image_storage_location: str = typing.cast(
                    str, images_storage_location[index]
                )
                orig_images_storage_locations.append(image_storage_location)

                # Get the shape of the image
                target_size = [(image.shape[0], image.shape[1])]

                # Image pre-processing
                model_input = self.image_processor(images=[image], return_tensors="pt")
                model_input = model_input.to(self.device)

                with torch.no_grad():
                    model_outputs = self.model(**model_input)
                del model_input

                model_outputs["target_size"] = target_size
                masks = []
                annotation = []
                # Image post-processing
                if fn is not None:
                    # Apply the post-processing function from above.
                    outputs = fn(
                        model_outputs,
                        threshold=self.threshold,
                        mask_threshold=self.mask_threshold,
                        overlap_mask_area_threshold=self.overlap_mask_area_threshold,
                        target_sizes=model_outputs["target_size"],
                    )[0]

                    # Get all segments and their masks and labels from the outputs
                    segmentation = outputs["segmentation"]
                    for segment in outputs["segments_info"]:
                        mask = (segmentation == segment["id"]) * 255
                        masks.append(mask)
                        label = self.model.config.id2label[segment["label_id"]]
                        score = segment["score"]
                        annotation.append({"score": score, "label": label})
                elif self.subtask in {"semantic", None} and hasattr(
                    self.image_processor, "post_process_semantic_segmentation"
                ):
                    # If there is no post-processing function for the subtask,
                    # use the semantic segmentation post-processing function,
                    # the same way it is done by hugging face
                    outputs = self.image_processor.post_process_semantic_segmentation(
                        model_outputs, target_sizes=model_outputs["target_size"]
                    )[0]

                    # Get all segments and their masks and labels from the outputs
                    segmentation = outputs.numpy()
                    labels = np.unique(segmentation)
                    for label in labels:
                        mask = (segmentation == label) * 255
                        masks.append(mask)
                        label = self.model.config.id2label[label]
                        annotation.append({"score": None, "label": label})

                del model_outputs
                del outputs
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                # Finally for each image draw the masks on the original image
                # and save it
                if len(masks) > 0:
                    seg_image, _ = self._draw_masks_on_original_image(
                        image, masks, self.alpha
                    )
                    filename = (
                        image_storage_location.split("/")[-1].split(".")[0]
                        + "-with-mask.png"
                    )
                    img_filename = self.save_path / filename
                    # cv2.imwrite expects a string as filename
                    cv2.imwrite(str(img_filename), seg_image)
                    final_img_path_list.append(str(img_filename))
                    # We convert the annotation to a string so that it can
                    # be saved in the dataframe since we do not know how
                    # many masks there are
                    final_prediction_list.append(str(annotation))
                else:
                    # Or if no masks were found, add a field
                    # in the results "no mask found"
                    final_img_path_list.append("no mask found")
                    final_prediction_list.append("no mask found")

                # Append key either way
                if keys:
                    keys_list.append(keys[index])
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        if self.dataframe_output:
            out_df = pd.DataFrame(
                {
                    "predictions": [str(item) for item in final_prediction_list],
                    "image_with_mask_path": final_img_path_list,
                }
            )

            # If keys are provided and requested, add them to the dataframe as a
            # new column.
            if keys_list and return_data_keys:
                out_df[ORIGINAL_FILENAME_METADATA_COLUMN] = keys_list

            return out_df
        else:
            # If keys are provided and requested, add them to the dict output.
            if keys_list and return_data_keys:
                return {
                    orig_images_storage_locations[i]: (mask_path, mask_labels, key)
                    for i, (mask_path, mask_labels, key) in enumerate(
                        zip(final_img_path_list, final_prediction_list, keys_list)
                    )
                }
            else:
                return {
                    orig_images_storage_locations[i]: (mask_path, mask_labels)
                    for i, (mask_path, mask_labels) in enumerate(
                        zip(final_img_path_list, final_prediction_list)
                    )
                }

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
class HuggingFaceImageSegmentationInference(
    BaseNonModelAlgorithmFactory[_HFModellerSide, _WorkerSide]
):
    """Inference for pre-trained Hugging Face image segmentation models.

    Perform segmentation (detect masks & classes) in the image(s) passed as inputs.

    Args:
        datastructure: The data structure to use for the algorithm.
        model_id: The model id to use for image segmentation inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        batch_size: The batch size for inference. Defaults to 1.
        subtask: Segmentation task to be performed, choose [`semantic`,
            `instance` and `panoptic`] depending on model capabilities.
            If not set, the pipeline will attempt to resolve in the
            following order: `panoptic`, `instance`, `semantic`.
        threshold: Probability threshold to filter out predicted masks.
            Defaults to 0.9.
        mask_threshold: Threshold to use when turning the predicted
            masks into binary values. Defaults to 0.5.
        overlap_mask_area_threshold: Mask overlap threshold to eliminate
            small, disconnected segments. Defaults to 0.5.
        alpha: the alpha for the mask overlay.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
        save_path: The folder path where the images with masks drawn
            on them should be saved. Defaults to the current working directory.
        dataframe_output: Whether to output the prediction results in a
            dataframe format. Defaults to `False`.

    Attributes:
        model_id: The model id to use for image segmentation inference.
            The model id is of a pretrained model hosted inside a model
            repo on huggingface.co. Accepts resnet models.
        batch_size: The batch size for inference. Defaults to 1.
        subtask: Segmentation task to be performed, choose [`semantic`,
            `instance` and `panoptic`] depending on model capabilities.
            If not set, the pipeline will attempt to resolve in the
            following order: `panoptic`, `instance`, `semantic`.
        threshold: Probability threshold to filter out predicted masks.
            Defaults to 0.9.
        mask_threshold: Threshold to use when turning the predicted
            masks into binary values. Defaults to 0.5.
        overlap_mask_area_threshold: Mask overlap threshold to eliminate
            small, disconnected segments. Defaults to 0.5.
        alpha: the alpha for the mask overlay.
        seed: Sets the seed of the algorithm. For reproducible behavior
            it defaults to 42.
        save_path: The folder path where the images with masks drawn
            on them should be saved. Defaults to the current working directory.
        dataframe_output: Whether to output the prediction results in a
            dataframe format. Defaults to `False`.
    """

    def __init__(
        self,
        datastructure: DataStructure,
        model_id: str,
        alpha: float = 0.3,
        batch_size: int = 1,
        dataframe_output: bool = False,
        mask_threshold: float = 0.5,
        overlap_mask_area_threshold: float = 0.5,
        save_path: Union[str, os.PathLike] = config.settings.paths.output_dir,
        seed: int = DEFAULT_SEED,
        subtask: Optional[_Subtask] = None,
        threshold: float = 0.9,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.model_id = model_id
        self.batch_size = batch_size
        self.subtask = subtask
        self.threshold = threshold
        self.mask_threshold = mask_threshold
        self.overlap_mask_area_threshold = overlap_mask_area_threshold
        self.seed = seed
        self.alpha = alpha
        self.save_path = save_path
        self.dataframe_output = dataframe_output

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "model_id": fields.Str(required=True),
        "batch_size": fields.Int(required=False),
        "subtask": fields.String(
            validate=OneOf(typing.get_args(_Subtask)), allow_none=True
        ),
        "threshold": fields.Float(required=False),
        "mask_threshold": fields.Float(required=False),
        "overlap_mask_area_threshold": fields.Float(required=False),
        "seed": fields.Int(required=False, missing=DEFAULT_SEED),
        "save_path": fields.Str(
            required=False, missing=config.settings.paths.output_dir
        ),
        "alpha": fields.Float(required=False),
        "dataframe_output": fields.Bool(required=False, missing=False),
    }

    def modeller(self, **kwargs: Any) -> _HFModellerSide:
        """Returns the modeller side of the HuggingFaceImageSegmentationInference algorithm."""  # noqa: E501
        return _HFModellerSide(task_name="mask_labels", **kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the HuggingFaceImageSegmentationInference algorithm."""  # noqa: E501
        return _WorkerSide(
            model_id=self.model_id,
            image_column_name=self.datastructure.selected_cols[0],
            batch_size=self.batch_size,
            subtask=self.subtask,
            threshold=self.threshold,
            mask_threshold=self.mask_threshold,
            overlap_mask_area_threshold=self.overlap_mask_area_threshold,
            save_path=self.save_path,
            alpha=self.alpha,
            seed=self.seed,
            dataframe_output=self.dataframe_output,
            **kwargs,
        )
