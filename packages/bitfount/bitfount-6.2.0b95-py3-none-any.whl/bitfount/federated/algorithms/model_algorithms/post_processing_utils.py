"""Utilities for post-processing."""

from __future__ import annotations

import ast
from enum import Enum, unique
import inspect
import json
import logging
import re
from typing import Any, ClassVar, Optional, Type, TypeVar, Union

import pandas as pd

from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.processor import TransformationProcessor
from bitfount.types import PredictReturnType

logger = logging.getLogger(__name__)


#############################################################################
# Base classes and type definitions
#############################################################################


@unique
class PostprocessorType(str, Enum):
    """Types of built-in postprocessors."""

    RENAME = "rename"  # Rename DataFrame columns
    TRANSFORM = (
        "transform"  # Apply transformations from bitfount.transformations # noqa: E501
    )
    JSON_RESTRUCTURE = (
        "json_restructure"  # Restructure JSON data by moving fields between levels
    )
    STRING_TO_JSON = "string_to_json"  # Convert string columns to JSON objects
    JSON_KEY_RENAME = (
        "json_key_rename"  # Rename keys within JSON data stored in columns
    )
    COMPOUND = "compound"  # Apply multiple postprocessors in sequence


# Global registry for postprocessors
POSTPROCESSOR_REGISTRY: dict[PostprocessorType, Type] = {}

# TypeVar for the postprocessor class
T = TypeVar("T", bound="PostProcessor")


class PostProcessor:
    """Base class that all postprocessors inherit from."""

    _processor_type: ClassVar[Optional[PostprocessorType]] = None

    def __init_subclass__(cls, **kwargs: Any):
        """Automatically register subclasses when they are defined."""
        super().__init_subclass__(**kwargs)

        if not inspect.isabstract(cls):
            processor_type = getattr(cls, "_processor_type", None)
            if processor_type is not None:
                if processor_type in POSTPROCESSOR_REGISTRY:
                    logger.warning(
                        f"Postprocessor type {processor_type} already "
                        f"registered. Overwriting."
                    )
                logger.debug(f"Adding {cls.__name__}: {cls} to PostProcessor registry")
                POSTPROCESSOR_REGISTRY[processor_type] = cls

    def process(
        self, predictions: Union[PredictReturnType, pd.DataFrame]
    ) -> Union[PredictReturnType, pd.DataFrame, Any]:
        """Process the model predictions."""
        raise NotImplementedError("Subclasses must implement process()")


#############################################################################
# Factory functions
#############################################################################


def create_postprocessor(config: dict[str, Any]) -> Optional[PostProcessor]:
    """Create a postprocessor from a configuration dictionary.

    Args:
        config: Postprocessor configuration with 'type' and other parameters

    Returns:
        An instance of the requested postprocessor or None if there is an
            error when creating it.
    """
    if "type" not in config:
        logger.error("Postprocessor configuration must include 'type'")
        return None

    processor_type = config["type"]

    # Convert string to enum if needed
    if isinstance(processor_type, str):
        try:
            processor_type = PostprocessorType(processor_type.lower())
        except ValueError:
            logger.error(f"Unknown postprocessor type: {processor_type}")
            return None

    if processor_type not in POSTPROCESSOR_REGISTRY:
        logger.error(f"Unsupported postprocessor type: {processor_type}")
        return None

    processor_class = POSTPROCESSOR_REGISTRY[processor_type]

    # Create a copy of the config to modify
    config_copy = config.copy()
    # Remove 'type' to avoid passing it to constructor, this is not used
    config_copy.pop("type")

    try:
        processor: PostProcessor = processor_class(**config_copy)
        return processor
    except TypeError as e:
        logger.error(f"Failed to instantiate {processor_type} postprocessor: {e}")
        return None


def create_postprocessors(
    postprocessor_configs: Optional[list[dict[str, Any]]] = None,
) -> list[PostProcessor]:
    """Create a list of postprocessors from configurations.

    Args:
        postprocessor_configs: Configuration for postprocessors, either:
            - None (returns an empty list)
            - A list of dicts, each with 'type' and other parameters

    Returns:
        List of PostProcessors.
    """
    if postprocessor_configs is None:
        return []
    # Create postprocessors from each config
    postprocessors = []
    for config in postprocessor_configs:
        if (
            config.get("type") == "compound"
            and config.get("name") in POSTPROCESSING_PRESETS
        ):
            preset_name = config.get("name")
            if isinstance(preset_name, str):
                # Use preset if available
                preset = POSTPROCESSING_PRESETS[preset_name]
                postprocessor = create_postprocessor(preset)
            else:
                postprocessor = None
                logger.warning("Preset name is not a string, skipping.")
        else:
            postprocessor = create_postprocessor(config)

        if postprocessor is not None:
            postprocessors.append(postprocessor)
    return postprocessors


#############################################################################
# Common utility methods for postprocessors
#############################################################################


def _parse_json(value: Any) -> Any:
    """Parse JSON data from various formats.

    Args:
        value: The value to parse.

    Returns:
        Parsed JSON object or original value if parsing fails.
    """
    if isinstance(value, str):
        try:
            # Try standard JSON parsing
            return json.loads(value)
        except json.JSONDecodeError:
            try:
                # Try parsing as Python literal (with single quotes)
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                logger.warning(
                    f"Failed to parse as JSON or Python literal: {value[:100]}..."
                )
                return value
    else:
        logger.warning("Value is not a string, returning as is.")
        # Already parsed or not a string
        return value


def _get_matching_columns(all_columns: list[str], patterns: list[str]) -> list[str]:
    """Get column names matching the given patterns.

    Args:
        all_columns: List of all column names.
        patterns: List of regex patterns to match.

    Returns:
        List of column names that match at least one pattern.
    """
    target_columns = []

    for pattern in patterns:
        try:
            regex = re.compile(pattern)
            matches = [col for col in all_columns if regex.search(col)]
            target_columns.extend(matches)
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")

    # Deduplicate columns
    return list(set(target_columns))


#############################################################################
# Postprocessor implementations
#############################################################################
class ColumnRenamerPostProcessor(PostProcessor):
    """Renames columns in a DataFrame."""

    _processor_type = PostprocessorType.RENAME

    def __init__(self, column_mapping: dict[str, str]):
        """Initialize the column renamer.

        Args:
            column_mapping: Mapping from old column names to new
                column names.
        """
        self.column_mapping = column_mapping

    def process(self, predictions: Any) -> Any:
        """Process the predictions by renaming columns.

        Args:
            predictions: The model output to process.

        Returns:
            Processed predictions with renamed columns.
        """
        if isinstance(predictions, pd.DataFrame):
            # For DataFrame, use the rename method
            return predictions.rename(columns=self.column_mapping)
        elif isinstance(predictions, PredictReturnType):
            # For PredictReturnType, check if preds is a DataFrame
            if isinstance(predictions.preds, pd.DataFrame):
                renamed_preds = predictions.preds.rename(columns=self.column_mapping)
                return PredictReturnType(preds=renamed_preds, keys=predictions.keys)
        # If format not supported or no renaming needed, return as is
        return predictions


class TransformationApplierPostProcessor(PostProcessor):
    """Applies transformations from the transformations module."""

    _processor_type = PostprocessorType.TRANSFORM

    def __init__(self, transformations: list[Transformation]):
        """Initialize the transformation applier.

        Args:
            transformations: List of transformations to apply.
        """
        self.transformations = transformations
        self.processor = TransformationProcessor(self.transformations)

    def process(self, predictions: Any) -> Any:
        """Process the predictions using the transformations.

        Args:
            predictions: Model output to process

        Returns:
            Processed predictions
        """
        if isinstance(predictions, pd.DataFrame):
            # Use TransformationProcessor for DataFrame
            return self.processor.transform(predictions)

        elif isinstance(predictions, PredictReturnType):
            # For PredictReturnType, check if preds is a DataFrame
            if isinstance(predictions.preds, pd.DataFrame):
                transformed_preds = self.processor.transform(predictions.preds)
                return PredictReturnType(preds=transformed_preds, keys=predictions.keys)
            else:
                logger.warning(
                    f"Transformations can only be applied to DataFrame predictions, "
                    f"got {type(predictions.preds)}. Returning unmodified."
                )
                return predictions
        else:
            logger.warning(
                f"Transformations can only be applied to DataFrame "
                f"or PredictReturnType, got {type(predictions)}. Returning unmodified."
            )
            return predictions


class StringToJSONPostProcessor(PostProcessor):
    """Converts string columns containing JSON data to actual JSON/dict objects."""

    _processor_type = PostprocessorType.STRING_TO_JSON

    def __init__(self, column_patterns: list[str]):
        """Initialize the string to JSON converter.

        Args:
            column_patterns: List of regex patterns matching column names to process
        """
        self.column_patterns = column_patterns

    def process(self, predictions: Any) -> Any:
        """Process predictions by converting string columns to JSON objects."""
        if isinstance(predictions, pd.DataFrame):
            # Find matching columns
            target_columns = _get_matching_columns(
                predictions.columns.tolist(), self.column_patterns
            )

            if not target_columns:
                logger.warning(f"No columns matched patterns: {self.column_patterns}")
                return predictions

            # Process each target column
            result = predictions.copy()

            for col in target_columns:
                # Apply string to JSON conversion to each cell in the column
                result[col] = result[col].apply(lambda value: _parse_json(value))

            return result

        elif isinstance(predictions, PredictReturnType):
            if isinstance(predictions.preds, pd.DataFrame):
                processed_preds = self.process(predictions.preds)
                return PredictReturnType(preds=processed_preds, keys=predictions.keys)
            elif isinstance(predictions.preds, list) and all(
                isinstance(item, str) for item in predictions.preds
            ):
                # Handle list of strings
                processed_preds = [_parse_json(item) for item in predictions.preds]
                return PredictReturnType(preds=processed_preds, keys=predictions.keys)

        # For any other format, return unmodified
        return predictions


class JSONFieldRestructuringPostProcessor(PostProcessor):
    """Restructures JSON data by moving fields between different levels.

    This is done for example to move fields from one json
    level to another as for example from
    `{"key1": {"key2": "value", "key3": "val"}}` to
    `{"key1": {"key2": "value"}, "key3": "val"}` and vice-versa.
    """

    _processor_type = PostprocessorType.JSON_RESTRUCTURE

    def __init__(
        self,
        column_patterns: list[str],
        field_mappings: list[dict[str, str]],
        keep_original: bool = False,
    ):
        """Initialize the JSON field restructurer.

        Args:
            column_patterns: List of regex patterns matching columns to process
            field_mappings: List of mappings, each with:
                - 'source_path': JSON path to extract (using dot notation,
                    e.g., 'key1.key2' or 'key2')
                - 'target_path': Path to place the value (dot notation,
                    e.g., ''key1.key2' or 'key2'')
            keep_original: Whether to keep the original fields
        """
        self.column_patterns = column_patterns
        self.field_mappings = field_mappings
        self.keep_original = keep_original

    def process(self, predictions: Any) -> Any:
        """Process predictions by restructuring JSON fields."""
        if isinstance(predictions, pd.DataFrame):
            # Find matching columns
            target_columns = _get_matching_columns(
                predictions.columns.tolist(), self.column_patterns
            )
            if not target_columns:
                logger.warning(f"No columns matched patterns: {self.column_patterns}")
                return predictions

            # Process each target column
            result = predictions.copy()

            for col in target_columns:
                # Apply restructuring to each row
                result[col] = result[col].apply(
                    lambda value: self._restructure_json(value)
                )

            return result

        elif isinstance(predictions, PredictReturnType):
            if isinstance(predictions.preds, pd.DataFrame):
                processed_preds = self.process(predictions.preds)
                return PredictReturnType(preds=processed_preds, keys=predictions.keys)

        # For any other format, return unmodified
        return predictions

    def _restructure_json(self, value: Any) -> Any:
        """Restructure JSON data according to the field mappings.

        Args:
            value: The JSON value to restructure

        Returns:
            Restructured JSON data
        """
        convert_back_to_list = False
        # Parse the JSON if needed
        data = _parse_json(value)

        # If it's a list, extract the first element
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
            convert_back_to_list = True

        # If it's not a dictionary, return as is
        if not isinstance(data, dict):
            return value

        result: Union[dict[str, Any], list[dict[str, Any]]]
        # Create a new dictionary to hold the result
        result = data.copy()

        for mapping in self.field_mappings:
            source_path = mapping.get("source_path", "")
            target_path = mapping.get("target_path", "")
            if not source_path or not target_path:
                logger.warning(
                    "Both source and target paths are required, skipping mapping"
                )
                continue

            try:
                # Extract the source value
                source_value = self._get_value_by_path(data, source_path)

                # If source value couldn't be found, continue
                if source_value is None:
                    continue

                # Set the value at the target path
                self._set_value_by_path(result, target_path, source_value)

                # Remove the original value if not keeping it
                if not self.keep_original and source_path != target_path:
                    self._remove_value_by_path(result, source_path)

            except (KeyError, IndexError, TypeError) as e:
                logger.error(
                    f"Error restructuring field '{source_path}' to '{target_path}': {e}"
                )

        if convert_back_to_list:
            # Convert back to list if it was originally a list
            result = [result]

        return result

    def _get_value_by_path(self, data: Any, path: str) -> Any:
        """Get a value from nested data using dot notation path."""
        if not path:
            return None

        parts = path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict):
                if part in current:
                    current = current.get(part)
                else:
                    return None
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                return None

        return current

    def _set_value_by_path(self, data: dict, path: str, value: Any) -> None:
        """Set a value in nested data using dot notation path."""
        if not path:
            return
        # Get the separate parts of the path
        parts = path.split(".")
        current = data

        # Go to the parent object, creating objects as needed
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]

        # Set the value in the parent object
        current[parts[-1]] = value

    def _remove_value_by_path(self, data: dict, path: str) -> None:
        """Remove a value from nested data using dot notation path."""
        if not path:
            return
        # Split the path into parts
        parts = path.split(".")

        if len(parts) == 1:
            # Top level key
            if parts[0] in data:
                del data[parts[0]]
            return

        # Navigate to the parent object
        current = data
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Path doesn't exist, nothing to remove
                return

        # Remove the key from the parent object
        if isinstance(current, dict) and parts[-1] in current:
            del current[parts[-1]]


class JSONKeyRenamerPostProcessor(PostProcessor):
    """Renames keys within JSON data stored in columns."""

    _processor_type = PostprocessorType.JSON_KEY_RENAME

    def __init__(
        self,
        column_patterns: list[str],
        key_mappings: list[dict[str, str]],
        recursive: bool = True,
    ):
        """Initialize the JSON key renamer.

        Args:
            column_patterns: List of regex patterns matching columns to process
            key_mappings: List of mappings, each with:
                - 'source_key': Original key name
                - 'target_key': New key name
            recursive: Whether to rename keys recursively throughout nested objects
        """
        self.column_patterns = column_patterns
        self.key_mappings = key_mappings
        self.recursive = recursive

    def process(self, predictions: Any) -> Any:
        """Process predictions by renaming JSON keys."""
        if isinstance(predictions, pd.DataFrame):
            # Find matching columns
            target_columns = _get_matching_columns(
                predictions.columns.tolist(), self.column_patterns
            )

            if not target_columns:
                logger.warning(f"No columns matched patterns: {self.column_patterns}")
                return predictions

            # Process each target column
            result = predictions.copy()

            for col in target_columns:
                # Apply key renaming to each row
                result[col] = result[col].apply(
                    lambda value: self._rename_json_keys(value)
                )

            return result

        elif isinstance(predictions, PredictReturnType):
            if isinstance(predictions.preds, pd.DataFrame):
                processed_preds = self.process(predictions.preds)
                return PredictReturnType(preds=processed_preds, keys=predictions.keys)
            elif isinstance(predictions.preds, list):
                # Process each item in the list
                processed_preds = [
                    self._rename_json_keys(item) for item in predictions.preds
                ]
                return PredictReturnType(preds=processed_preds, keys=predictions.keys)

        # For any other format, return unmodified
        return predictions

    def _rename_json_keys(self, value: Any) -> Any:
        """Rename keys in JSON data according to the key mappings.

        Args:
            value: The JSON value to process

        Returns:
            JSON data with renamed keys
        """
        convert_back_to_list = False
        # Parse the JSON if needed
        data = _parse_json(value)

        # If it's a list, extract the first element
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
            convert_back_to_list = True

        # If it's not a dictionary, return as is
        if not isinstance(data, dict):
            return value
        result: Union[dict[str, Any], list[dict[str, Any]]]
        # Create a new dictionary with renamed keys
        result = self._rename_dict_keys(data)

        if convert_back_to_list:
            # Convert back to list if it was originally a list
            result = [result]

        return result

    def _rename_dict_keys(self, data: dict[str, Any]) -> dict[str, Any]:
        """Rename keys in a dictionary according to the key mappings.

        Args:
            data: Dictionary to process

        Returns:
            Dictionary with renamed keys
        """
        # Create a new dictionary to hold the result
        result: dict[str, Any] = {}

        # Process each key in the original dict
        for key, value in data.items():
            # Check if this key should be renamed
            new_key = key
            for mapping in self.key_mappings:
                source_key = mapping.get("source_key", "")
                target_key = mapping.get("target_key", "")

                if not source_key or not target_key:
                    logger.warning(
                        "Both source and target keys are required, skipping mapping"
                    )
                    continue

                if key == source_key:
                    new_key = target_key
                    break

            # Process nested structures if recursive is enabled
            if self.recursive and isinstance(value, dict):
                result[new_key] = self._rename_dict_keys(value)
            elif (
                self.recursive
                and isinstance(value, list)
                and all(isinstance(item, dict) for item in value)
            ):
                result[new_key] = [self._rename_dict_keys(item) for item in value]
            else:
                result[new_key] = value

        return result


class CompoundPostProcessor(PostProcessor):
    """Applies multiple postprocessors in sequence."""

    _processor_type = PostprocessorType.COMPOUND

    def __init__(
        self,
        postprocessing_sequence: list[dict[str, Any]],
        name: Optional[str] = None,
    ):
        """Initialize the compound postprocessor.

        Args:
            postprocessing_sequence: List of postprocessor configurations
                to apply in a sequence
            name: Name as a string for the for this transformation
                pipeline. Default to None.
        """
        self.postprocessing_sequence = postprocessing_sequence
        self.name = name or "CompoundTransformation"

        # Create all the postprocessors
        self.processors = []
        for config in self.postprocessing_sequence:
            try:
                processor = create_postprocessor(config)
                if processor is not None:
                    self.processors.append(processor)
            except Exception as e:
                logger.error(f"Failed to create postprocessor: {e}")
                continue

    def process(self, predictions: Any) -> Any:
        """Apply all postprocessors in sequence."""
        logger.debug(f"Processing with CompoundPostProcessor: {self.name}")
        logger.debug(f"Input type: {type(predictions)}")

        result = predictions
        # Apply each postprocessor in sequence
        for i, processor in enumerate(self.processors):
            if processor is not None:
                processor_name = processor.__class__.__name__
                try:
                    logger.debug(
                        f"Applying processor {i + 1}/{len(self.processors)}:"
                        f" {processor_name}"
                    )

                    result = processor.process(result)
                    logger.debug(
                        f"After processor {i + 1}: {processor_name}, "
                        f"result type: {type(result)}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error in processor {i + 1}: {e}. "
                        f"Skipping processor {processor_name}."
                    )
                    continue
        return result


#############################################################################
# Compound Postprocessor Presets
#############################################################################


PATHOLOGY_TO_SEGMENTATION_TRANSFORMATION = {
    "type": "compound",
    "name": "pathology_to_segmentation",
    "postprocessing_sequence": [
        {
            "type": "string_to_json",
            "column_patterns": [r"Pixel_Data_\d+_prediction"],
        },
        {
            "type": "json_restructure",
            "column_patterns": [r"Pixel_Data_\d+_prediction"],
            "field_mappings": [
                {"source_path": "metadata", "target_path": "mask.metadata"},
                {
                    "source_path": "classes.choroidal_neovascularization",
                    "target_path": "choroidal_neovascularization",
                },
            ],
        },
        {
            "type": "json_key_rename",
            "column_patterns": [r"Pixel_Data_\d+_prediction"],
            "key_mappings": [
                {
                    "source_key": "choroidal_neovascularization",
                    "target_key": "cnv_probability",
                }
            ],
            "recursive": True,
        },
    ],
}


# Global registry for transformation presets
POSTPROCESSING_PRESETS: dict[str, Any] = {
    "pathology_to_segmentation": PATHOLOGY_TO_SEGMENTATION_TRANSFORMATION,
}
