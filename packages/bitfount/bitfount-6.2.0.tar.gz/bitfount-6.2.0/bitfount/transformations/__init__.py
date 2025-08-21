"""Modules related to the transformations framework.

All transformations should be imported here so that they are automatically added to the
transformations registry.
"""

from __future__ import annotations

from bitfount.transformations.base_transformation import TRANSFORMATION_REGISTRY
from bitfount.transformations.batch_operations import (
    IMAGE_TRANSFORMATIONS,
    AlbumentationsImageTransformation,
)
from bitfount.transformations.binary_operations import (
    AdditionTransformation,
    ComparisonTransformation,
    DivisionTransformation,
    MultiplicationTransformation,
    SubtractionTransformation,
)
from bitfount.transformations.dataset_operations import (
    CleanDataTransformation,
    NormalizeDataTransformation,
)
from bitfount.transformations.exceptions import (
    IncorrectReferenceError,
    InvalidBatchTransformationError,
    MissingColumnReferenceError,
    NotColumnReferenceError,
    NotTransformationReferenceError,
    TransformationApplicationError,
    TransformationParsingError,
    TransformationProcessorError,
    TransformationRegistryError,
)
from bitfount.transformations.parser import TransformationsParser
from bitfount.transformations.processor import TransformationProcessor
from bitfount.transformations.torchio_batch_operations import (
    TORCHIO_IMAGE_TRANSFORMATIONS,
    TorchIOImageTransformation,
)
from bitfount.transformations.unary_operations import (
    InclusionTransformation,
    OneHotEncodingTransformation,
)

__all__: list[str] = [
    "AdditionTransformation",
    "AlbumentationsImageTransformation",
    "TorchIOImageTransformation",
    "CleanDataTransformation",
    "ComparisonTransformation",
    "DivisionTransformation",
    "IMAGE_TRANSFORMATIONS",
    "TORCHIO_IMAGE_TRANSFORMATIONS",
    "InclusionTransformation",
    "IncorrectReferenceError",
    "InvalidBatchTransformationError",
    "MissingColumnReferenceError",
    "MultiplicationTransformation",
    "NormalizeDataTransformation",
    "NotColumnReferenceError",
    "NotTransformationReferenceError",
    "OneHotEncodingTransformation",
    "SubtractionTransformation",
    "TransformationApplicationError",
    "TransformationsParser",
    "TransformationParsingError",
    "TransformationProcessor",
    "TransformationProcessorError",
    "TransformationRegistryError",
    "TRANSFORMATION_REGISTRY",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
