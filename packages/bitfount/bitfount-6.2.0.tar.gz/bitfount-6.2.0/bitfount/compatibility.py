"""Utilities for handling task compatibility with different SDK versions."""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Type

import desert
from marshmallow import ValidationError
import semver

from bitfount.config import get_compatible_yaml_versions_for_role
from bitfount.exceptions import BitfountVersionError

_logger = logging.getLogger(__name__)

# Try to import the changelog from __version__.py
# Define __changelog__ first to ensure it's always defined
__changelog__ = ""
try:
    from bitfount.__version__ import __changelog__
except ImportError:
    _logger.warning("__changelog__ not found in __version__.py")

if not __changelog__:
    _logger.warning("__changelog__ is empty")

__all__: list[str] = [
    "get_compatible_versions_for_modeller",
    "parse_semver",
    "extract_version_changes",
    "create_error_message",
    "check_task_compatibility",
    "validate_task_compatibility",
]


def get_compatible_versions_for_modeller() -> List[str]:
    """Get compatible versions for the modeller role.

    Returns:
        List of compatible versions
    """
    return get_compatible_yaml_versions_for_role("modeller")


def parse_semver(version: str) -> Optional[semver.VersionInfo]:
    """Parse a semantic version string.

    Args:
        version: The version string to parse

    Returns:
        Parsed VersionInfo object or None if parsing fails
    """
    try:
        return semver.VersionInfo.parse(version)
    except (ValueError, ImportError) as e:
        _logger.warning(f"Failed to parse version '{version}': {e}")
        return None


def extract_version_changes(
    from_version: str, to_version: str
) -> Tuple[List[str], bool]:
    """Extract changes between two versions from the __version__.py file.

    Args:
        from_version: The source version
        to_version: The target version

    Returns:
        Tuple of (list of change descriptions, is_complete_history):
            is_complete_history is False if the from_version is older
            than the oldest version in the changelog
    """
    try:
        if not __changelog__:
            return [], False

        # Extract all version blocks using regex
        version_blocks = re.findall(
            r"- (\d+\.\d+\.\d+):([\s\S]*?)(?=- \d+\.\d+\.\d+:|$)", __changelog__
        )

        if not version_blocks:
            _logger.warning("No version blocks found in changelog")
            return [], False

        # Convert to dictionary for easier lookup
        version_changes = {
            version: changes.strip() for version, changes in version_blocks
        }

        # Parse versions
        from_semver = parse_semver(from_version)
        to_semver = parse_semver(to_version)

        if not from_semver or not to_semver:
            return [], False

        # Get the oldest version in the changelog
        oldest_version = min(
            version_changes.keys(),
            key=lambda v: parse_semver(v) or semver.VersionInfo.parse("0.0.0"),
        )
        oldest_semver = parse_semver(oldest_version)

        if not oldest_semver:
            return [], False

        # Check if we have complete history
        is_complete_history = from_semver >= oldest_semver

        # If from_version is older than the oldest in changelog,
        # use the oldest as starting point
        effective_from_semver = from_semver if is_complete_history else oldest_semver

        # Collect changes for all versions between effective_from_version and to_version
        changes = []

        # Add a note if we don't have complete history
        if not is_complete_history:
            changes.append(
                f"Note: Your task version ({from_version}) is older "
                f"than the oldest version in the changelog ({oldest_version})."
            )
            changes.append(f"Showing changes from version {oldest_version} onwards.")
            changes.append("")

        # Sort versions in descending order (newest first)
        sorted_versions = sorted(
            version_changes.keys(),
            key=lambda v: parse_semver(v) or semver.VersionInfo.parse("0.0.0"),
            reverse=True,
        )

        for version_str in sorted_versions:
            version_semver = parse_semver(version_str)
            if not version_semver:
                continue

            # Include changes if version is newer than effective_from_version
            # and not newer than to_version
            if effective_from_semver < version_semver <= to_semver:
                # Extract bullet points from the changes text
                version_bullets = re.findall(
                    r"- ([^\n]+)", version_changes[version_str]
                )

                # Add version header
                changes.append(f"Version {version_str}:")

                # Add bullet points
                for bullet in version_bullets:
                    changes.append(f"  - {bullet.strip()}")

                # Add a blank line after each version
                changes.append("")

        return changes, is_complete_history
    except Exception as e:
        _logger.warning(f"Error extracting version changes: {e}", exc_info=True)
        return [], False


def create_error_message(
    message: str, validation_error: Optional[ValidationError] = None
) -> str:
    """Create an error message, logging the validation error if provided.

    Args:
        message: The main error message
        validation_error: Optional validation error to log

    Returns:
        The formatted error message
    """
    if validation_error:
        _logger.error(f"Original validation error: {str(validation_error)}")

    return message


def check_task_compatibility(
    task_data: Dict[str, Any],
    config_class: Type,
    context: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[Any], Optional[str]]:
    """Check if a task is compatible with the current SDK version.

    Args:
        task_data: The task data to check
        config_class: The dataclass to use for validation
        context: Optional context to pass to the schema

    Returns:
        Tuple of (is_compatible, parsed_task, error_message)
    """
    # Step 1: Try to parse with current schema
    try:
        # Create schema from dataclass using desert
        schema = desert.schema(config_class)

        # Set context if provided
        if context:
            schema.context.update(context)

        # Load data
        parsed_task = schema.load(task_data)
        # Additional validation for ModellerConfig
        # Import here to avoid circular imports
        from bitfount.runners.config_schemas.algorithm_schemas import (
            GenericAlgorithmConfig,
        )
        from bitfount.runners.config_schemas.modeller_schemas import ModellerConfig
        from bitfount.runners.config_schemas.protocol_schemas import (
            GenericProtocolConfig,
        )

        # Needs some extra handling for new protocols and algorithms.
        # Since they won't be recognized by the schema, they will be
        # parsed as GenericProtocolConfig and GenericAlgorithmConfig
        # respectively. We need to check for these and raise an error
        # if found, since we won't be able to run tasks with these configs.
        if isinstance(parsed_task, ModellerConfig):
            if isinstance(parsed_task.task.protocol, GenericProtocolConfig):
                raise ValidationError(
                    "GenericProtocolConfig is not supported for modeller tasks."
                )
            if any(
                isinstance(algo, GenericAlgorithmConfig)
                for algo in parsed_task.task.algorithms
            ):
                raise ValidationError(
                    "GenericAlgorithmConfig is not supported for modeller tasks."
                )
        # If we get here, the task is compatible with our schema
        # Check if the version is in the list of compatible versions
        task_version = task_data.get("version")
        if task_version:
            compatible_versions = get_compatible_versions_for_modeller()
            if task_version not in compatible_versions:
                # Task version is not in the list of compatible versions,
                # but the schema is compatible. Log a warning but allow
                # it to proceed
                _logger.warning(
                    f"Task version {task_version} is not in the list "
                    f"of compatible versions {compatible_versions}, "
                    f"but the schema is compatible. Proceeding anyway."
                )

        return True, parsed_task, None
    except ValidationError as e:
        # Step 2: Parsing failed, check version compatibility
        task_version = task_data.get("version")
        if not task_version:
            return (
                False,
                None,
                create_error_message(
                    f"Task yaml failed validation and is missing version field: {str(e)}",  # noqa: E501
                    e,
                ),
            )

        # Get the SDK's expected YAML versions
        compatible_versions = get_compatible_versions_for_modeller()

        if not compatible_versions:
            return (
                False,
                None,
                create_error_message(
                    "No compatible YAML versions found for the current SDK. "
                    "This may indicate a configuration issue.",
                    e,
                ),
            )

        # Format the list of compatible versions for display
        versions_display = ", ".join(compatible_versions)

        # Compare versions
        task_semver = parse_semver(task_version)
        if not task_semver:
            return (
                False,
                None,
                create_error_message(
                    f"Failed to parse version '{task_version}' as semantic version. "
                    f"Compatible versions are: {versions_display}.",
                    e,
                ),
            )

        # Check against all compatible versions
        compatible_found = False
        for compatible_version in compatible_versions:
            compatible_semver = parse_semver(compatible_version)
            if not compatible_semver:
                continue

            if task_semver == compatible_semver:
                compatible_found = True
                break

        if compatible_found:
            # Version is compatible but parsing still failed - this
            # is a schema validation error
            return (
                False,
                None,
                create_error_message(
                    f"Task has a compatible version ({task_version})"
                    " but failed schema validation. This may indicate an "
                    f"invalid task configuration: {str(e)}",
                    e,
                ),
            )

        # If we get here, the version is not compatible
        # Find the latest compatible version
        latest_compatible = compatible_versions[0]
        latest_compatible_semver = parse_semver(latest_compatible)

        if not latest_compatible_semver:
            return (
                False,
                None,
                create_error_message(
                    f"Failed to parse latest compatible version '{latest_compatible}'. "
                    f"This may indicate a configuration issue.",
                    e,
                ),
            )

        if task_semver < latest_compatible_semver:
            # Task version is older than what SDK expects
            # Extract changes between versions
            changes, is_complete_history = extract_version_changes(
                task_version, latest_compatible
            )
            changes_text = (
                "\n".join(changes)
                if changes
                else "No detailed change information available."
            )

            return (
                False,
                None,
                create_error_message(
                    f"Task YAML version ({task_version}) is older than "
                    f"what the SDK expects. Please update your task configuration "
                    f"to a compatible version: {versions_display}.\n\n"
                    f"Changes since version {task_version}:\n{changes_text}",
                    e,
                ),
            )
        else:  # task_semver > latest_compatible_semver
            # Task version is newer than what SDK supports
            return (
                False,
                None,
                create_error_message(
                    f"Task YAML version ({task_version}) is newer "
                    "than what the SDK supports. Please update your SDK "
                    "to the latest version or use a task with a compatible "
                    f"version: {versions_display}.",
                    e,
                ),
            )


def validate_task_compatibility(
    task_data: Dict[str, Any],
    config_class: Type,
    context: Optional[Dict[str, Any]] = None,
) -> Any:
    """Validate task compatibility and return parsed task or raise informative error.

    Args:
        task_data: The task data to validate
        config_class: The dataclass to use for validation
        context: Optional context to pass to the schema

    Returns:
        The parsed task if compatible

    Raises:
        BitfountVersionError: If task is incompatible with detailed message
    """
    is_compatible, parsed_task, error_message = check_task_compatibility(
        task_data, config_class, context
    )
    if not is_compatible:
        raise BitfountVersionError(error_message)

    return parsed_task
