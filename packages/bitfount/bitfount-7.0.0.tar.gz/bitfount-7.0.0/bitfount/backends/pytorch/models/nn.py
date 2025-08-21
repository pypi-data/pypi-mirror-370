"""Neural Network classes and helper functions for PyTorch."""

from __future__ import annotations

import logging
from typing import Any, cast

import torch.nn as nn
import torchvision.models as tv_models

logger = logging.getLogger(__name__)

TORCHVISION_CLASSIFICATION_MODELS = {
    name: func
    for name, func in vars(tv_models).items()
    if callable(func) and not isinstance(func, type)
}


def _get_torchvision_classification_model(
    model_name: str, pretrained: bool, num_classes: int, **kwargs: Any
) -> nn.Module:
    """Returns a pre-existing torchvision model.

    This function returns the torchvision classification model corresponding to
    `model_name`. Importantly, it resizes the final layer to make it appropriate
    for the task. Since this is different for every model, this must be hard-coded

    Adapted from pytorch docs/tutorials
    """
    # Convert model name for consistency
    model_name = model_name.lower()

    if "resnet" in model_name:
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
    elif ("alexnet" in model_name) or ("vgg" in model_name):
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        num_ftrs = model.classifier[6].in_features
        model.classifier[6] = nn.Linear(num_ftrs, num_classes)
    elif "squeezenet" in model_name:
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        model.classifier[1] = nn.Conv2d(
            512, num_classes, kernel_size=(1, 1), stride=(1, 1)
        )
        model.num_classes = num_classes
    elif "densenet" in model_name:
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Linear(num_ftrs, num_classes)
    elif model_name in TORCHVISION_CLASSIFICATION_MODELS:
        raise ValueError("Model reshaping not implemented yet. Choose another model.")
    else:
        raise ValueError("Model name not recognised")

    return cast(nn.Module, model)
