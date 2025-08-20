"""Utility functions for the runner modules."""

from __future__ import annotations

import dataclasses
import logging
from typing import TYPE_CHECKING, Any, Optional, TypeVar

from packaging import version

from bitfount.__version__ import __version__ as bf_version
from bitfount.exceptions import BitfountError
from bitfount.utils.logging_utils import setup_loggers

if TYPE_CHECKING:
    from bitfount.externals.general.authentication import ExternallyManagedJWT
    from bitfount.runners.config_schemas import APIKeys
    from bitfount.runners.config_schemas.common_schemas import SecretsUse

__all__ = ["setup_loggers"]

_logger = logging.getLogger(__name__)


def is_version_compatible_major_minor(
    yaml_versions: list[str], version_to_check: str, task_or_dataset: str
) -> tuple[bool, str]:
    """Check version compatibility based on major and minor versions.

    Check is based on a `any` type check to see if at least one
    of the yaml versions is compatible with the current one.

    Args:
        yaml_versions: The list of compatible yaml versions.
        version_to_check: The version to check for compatibility.
        task_or_dataset: Whether the check is done in the context
            of a task or a dataset.

    Returns:
        A tuple containing a bool indicating compatibility, together with a message.
    """
    parsed_version_to_check = version.parse(version_to_check)
    needs_update = False
    parsed_versions = [version.parse(v) for v in yaml_versions]
    highest_version = max(parsed_versions)
    lowest_version = min(parsed_versions)
    if any(
        [
            parsed_version_to_check.major == v.major
            and parsed_version_to_check.minor == v.minor
            for v in parsed_versions
        ]
    ):
        message = (
            f"Your version ({version_to_check}) is compatible "
            f"with at least one version."
        )
        needs_update = True
    elif (
        parsed_version_to_check.major <= lowest_version.major
        and parsed_version_to_check.minor < lowest_version.minor
    ):
        message = (
            f"The {task_or_dataset} specification you are using "
            "is an old version that is not compatible with the "
            "new version of Bitfount you are running. "
            f"Please fix your {task_or_dataset} specifications. "
            f"Current Bitfount version is {bf_version}, which supports "
            f"yaml versions {yaml_versions}, but {task_or_dataset} YAML "
            f"version is {version_to_check}."
        )

    elif (
        parsed_version_to_check.major >= highest_version.major
        and parsed_version_to_check.minor > highest_version.minor
    ):
        message = (
            f"The {task_or_dataset} specification you are using is a new version "
            "that is not compatible with the old version of "
            "Bitfount you are running. Please update Bitfount. "
            f"Current Bitfount version is {bf_version}, which supports "
            f"yaml versions {yaml_versions}, but {task_or_dataset} YAML "
            f"version is {version_to_check}."
        )

    else:
        message = (
            f"The {task_or_dataset} specification you are using is a version "
            "that is not compatible with the current version of "
            "Bitfount you are running. "
            f"Current Bitfount version is {bf_version}, which supports "
            f"yaml versions {yaml_versions}, but {task_or_dataset} YAML "
            f"version is {version_to_check}."
        )
    return needs_update, message


def is_version_compatible_all(
    yaml_versions: list[str], version_to_check: str, task_or_dataset: str
) -> tuple[bool, str]:
    """Check version compatibility for versions.

    Args:
        yaml_versions: The list of compatible yaml versions.
        version_to_check: The version to check for compatibility.
        task_or_dataset: Whether the check is done in the context
            of a task or a dataset.

    Returns:
        A tuple containing a bool indicating compatibility, together with a message.
    """
    parsed_version_to_check = version.parse(version_to_check)
    needs_update = False
    parsed_versions = [version.parse(v) for v in yaml_versions]

    if any([parsed_version_to_check == v for v in parsed_versions]):
        message = (
            f"Your version ({version_to_check}) is compatible "
            f"with at least one version."
        )
        needs_update = True
    elif all([parsed_version_to_check < v for v in parsed_versions]):
        message = (
            f"The {task_or_dataset} specification you are using "
            "is an old version that is not compatible with the "
            "new version of Bitfount you are running. "
            f"Please fix your {task_or_dataset} specifications. "
            f"Current Bitfount version is {bf_version}, which supports "
            f"yaml versions {yaml_versions},  but {task_or_dataset} YAML "
            f"version is {version_to_check}."
        )
    elif all([parsed_version_to_check > v for v in parsed_versions]):
        message = (
            f"The {task_or_dataset} specification you are using is a new version "
            "that is not compatible with the old version of "
            "Bitfount you are running. Please update Bitfount. "
            f"Current Bitfount version is {bf_version}, which supports "
            f"yaml versions {yaml_versions}, but {task_or_dataset} YAML "
            f"version is {version_to_check}."
        )
    else:
        message = (
            f"The {task_or_dataset} specification you are using is a version "
            "that is not compatible with the current version of "
            "Bitfount you are running. "
            f"Current Bitfount version is {bf_version}, which supports "
            f"yaml versions {yaml_versions}, but {task_or_dataset} YAML "
            f"version is {version_to_check}."
        )
    return needs_update, message


def dataclass_to_kwargs(dc: Any) -> dict[str, Any]:
    """Converts a dataclass, shallowly, into kwarg-ready form."""
    if not dataclasses.is_dataclass(dc):
        raise TypeError("Only dataclasses are supported for conversion to kwargs")
    # from details here: https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict # noqa: E501
    return dict(
        (field.name, getattr(dc, field.name)) for field in dataclasses.fields(dc)
    )


_T = TypeVar("_T")


def get_concrete_config_subclasses(cls: type[_T]) -> tuple[type[_T], ...]:
    """Get all the concrete subclasses of a config class."""
    # We want to find subclasses that are actually meant to be used (i.e. not
    # marked as "intermediate") as well as those that should be tried if nothing
    # else works (i.e. marked as "fallback").
    #
    # The fallback options should be put at the end of the subclass list so
    # that they are the last thing that desert/marshmallow will try to deserialize
    # as.
    concrete_subclasses = []
    fallback_subclasses = []
    queue = list(cls.__subclasses__())  # prime queue with initial subclasses
    while queue:
        current_cls = queue.pop()
        queue.extend(current_cls.__subclasses__())

        # Intermediate/fallback classes with have the cls._config_type attribute,
        # others won't
        config_type: Optional[str] = getattr(
            current_cls, f"_{current_cls.__name__}__config_type", None
        )
        if config_type != "intermediate":
            if config_type == "fallback":
                _logger.debug(
                    f"Discovered fallback subclass for {cls.__name__}:"
                    f" {current_cls.__name__}"
                )
                fallback_subclasses.append(current_cls)
            else:
                _logger.debug(
                    f"Discovered implementation subclass for {cls.__name__}:"
                    f" {current_cls.__name__}"
                )
                concrete_subclasses.append(current_cls)
        else:
            _logger.debug(
                f"Discovered intermediate subclass for {cls.__name__}:"
                f" {current_cls.__name__}"
            )
    return tuple(concrete_subclasses + fallback_subclasses)


def get_secrets_for_use(
    secrets: Optional[
        APIKeys
        | ExternallyManagedJWT
        | dict[SecretsUse, APIKeys | ExternallyManagedJWT]
    ],
    use: SecretsUse = "bitfount",
) -> Optional[APIKeys | ExternallyManagedJWT]:
    """Retrieve the secrets for the specified use.

    Args:
        secrets: The secrets configuration.
        use: The type of secrets to retrieve (e.g. 'bitfount', 'ehr'). Default is
            'bitfount'.

    Returns:
        The secrets, as supplied, for the specified use.

    Raises:
        BitfountError: If the use is not one of the supported secrets types or
            there is only one secret and the use is not 'bitfount'.
    """
    if not isinstance(secrets, dict):
        if use == "bitfount":
            return secrets
        else:
            err_msg = (
                f"Secrets configuration does not contain secrets"
                f' for accessing "{use}";'
                f" it contains only a single set of secrets,"
                f" for authenticating with Bitfount services"
            )
            _logger.error(err_msg)
            raise BitfountError(err_msg)
    else:
        try:
            return secrets[use]
        except KeyError as e:
            err_msg = (
                f'Secrets configuration does not contain secrets for accessing "{use}"'
            )
            _logger.error(err_msg)
            raise BitfountError(err_msg) from e
