"""Dealing with interactions with configuration and environment variables."""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache
from importlib import util
import logging
import os
from pathlib import Path
import platform
from typing import Any, Final, Literal, Optional, cast

import GPUtil
from pydantic import Field, computed_field, field_validator
from pydantic.json_schema import SkipJsonSchema
from pydantic_settings import BaseSettings, SettingsConfigDict

from bitfount.__version__ import (
    __modeller_yaml_versions__ as modeller_yaml_versions,
    __version__ as bf_version,
    __yaml_versions__ as legacy_yaml_versions,
)

__all__: list[str] = [
    "LOG_LEVELS_STR",
    # Backend engine
    "BITFOUNT_ENGINE",
    # GPU
    "get_gpu_metadata",
    # YAML versioning
    "_BITFOUNT_COMPATIBLE_YAML_VERSIONS",
    # Environment
    "_get_environment",
    # DP Support
    "DP_AVAILABLE",
    # Settings
    "refresh_configuration",
    "configuration_schema",
    "Settings",
]

from marshmallow import ValidationError

logger = logging.getLogger(__name__)

LOG_LEVELS_STR = Literal[
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
]

DEFAULT_SETTINGS_CONFIG = SettingsConfigDict(
    # Configuration is loaded if an environment variable is present
    # with the `BITFOUNT_` prefix
    env_prefix="BITFOUNT_",
    env_file=(".env.local"),
    # Avoids issues when loading caused by computed fields
    extra="ignore",
)


class PrivateSettings(BaseSettings):
    """Settings that we don't expect the user to interface with."""

    model_config = SettingsConfigDict(env_prefix="_BITFOUNT_")

    # A Bitfount child process is a process that is spawned by the main Bitfount process
    # to perform a specific task. This is used to determine if the current process is a
    # child process or not and therefore if certain actions should be taken or not.
    child_process: SkipJsonSchema[bool] = Field(default=False)


class Settings(BaseSettings):
    """All configurable settings.

    Contains all of our configurable variables.
    Loads from `.env.local` or from environment variables.
    """

    model_config = DEFAULT_SETTINGS_CONFIG

    paths: SkipJsonSchema[PathSettings] = Field(default_factory=lambda: PathSettings())
    logging: SkipJsonSchema[LogSettings] = Field(default_factory=lambda: LogSettings())
    private: SkipJsonSchema[PrivateSettings] = Field(
        default_factory=lambda: PrivateSettings()
    )
    smart_on_fhir: SkipJsonSchema[SMARTOnFHIRSettings] = Field(
        default_factory=lambda: SMARTOnFHIRSettings()
    )

    log_level: LOG_LEVELS_STR = Field(
        default="INFO",
        title="Log Level",
        description="Increases or decreases the verbosity of logging.",
    )

    # Compatibility/Extras
    use_mps: bool = Field(default=False)
    proxy_support: SkipJsonSchema[bool] = Field(default=True)
    enable_data_cache: SkipJsonSchema[bool] = Field(default=True)
    pod_vitals_port: SkipJsonSchema[int] = Field(default=29209)

    default_torch_device: Optional[str] = Field(default=None)

    # Zeiss DICOM Settings
    allow_extra_zeiss_transfer_syntaxes: SkipJsonSchema[bool] = Field(
        default=False,
        description=(
            "Enables additional TransferSyntaxUIDs to be considered"
            " when decoding Zeiss DICOM images."
            " The set of supported TransferSyntaxUIDs with this option is:"
            " JPEG2000Lossless (1.2.840.10008.1.2.4.90)"
            " [the default when this option is not enabled],"
            " JPEGLossless (1.2.840.10008.1.2.4.57),"
            " JPEGLosslessSV1 (1.2.840.10008.1.2.4.70),"
            " JPEGLSLossless (1.2.840.10008.1.2.4.80),"
            " JPEGLSNearLossless (1.2.840.10008.1.2.4.81),"
            " and JPEG2000 (1.2.840.10008.1.2.4.91)."
        ),
    )

    # File-system interaction settings
    network_drive_robustness: SkipJsonSchema[bool] = Field(default=False)
    # Assuming a _DEFAULT_MAX_BACKOFF of 60 seconds each retry after the 6th will take 1
    # minute to complete. So this value means about 6 hours of retries.
    network_drive_robustness_retries: SkipJsonSchema[int] = Field(default=360, gt=0)

    # Web interaction settings
    web_max_retries: SkipJsonSchema[int] = Field(default=3, gt=0)

    # Message Service
    # The window in which handlers can be registered for them to be dispatched for a
    # given message.
    handler_register_grace_period: SkipJsonSchema[int] = Field(gt=0, default=30)
    online_check_soft_limit: SkipJsonSchema[int] = Field(gt=0, default=180)
    online_check_hard_limit: SkipJsonSchema[int] = Field(gt=0, default=180)
    message_service_retries: SkipJsonSchema[int] = Field(
        default=3,
        gt=0,
        description=(
            "Max retries for message service connections"
            " that should have standard retry behaviour."
        ),
    )
    # Assuming a _DEFAULT_MAX_BACKOFF of 60 seconds and a _DEFAULT_TIMEOUT of 20,
    # each retry after the 9th will take 1:20 minutes to complete.
    # So this value means about 6 hours of retries.
    message_service_many_retries: SkipJsonSchema[int] = Field(
        default=270,
        gt=0,
        description=(
            "Max retries for message service connections that should have"
            " large retry amounts (e.g. send and get)."
            " Default is equivalent to about 6 hours."
        ),
    )

    # Data environment variables
    # The maximum number of files that can be selected in a FileSystemIterableSource
    # after filtering. This is to prevent the user from selecting a directory with
    # too many files.
    max_number_of_datasource_files: SkipJsonSchema[int] = Field(default=500_000, gt=0)

    # The maximum number of files to load for `fast_load` in a FileSystemIterableSource
    fast_load_maximum_number_of_files_to_load: SkipJsonSchema[int] = Field(
        default=50, gt=0
    )

    # Task environment variables
    # For easier control of the batched execution in the app
    default_batched_execution: SkipJsonSchema[bool] = Field(default=False)

    # This is used by the pod to determine how many batches to split a task into
    # if the modeller has requested batched execution
    task_batch_size: SkipJsonSchema[int] = Field(default=16, gt=0)
    # This is used by the pod to determine the number of files part of a test run
    test_run_number_of_files: SkipJsonSchema[int] = Field(default=1, gt=0)
    # Whether to do background file counting or not
    background_file_counting: SkipJsonSchema[bool] = Field(default=True)

    # Batch resilience settings
    # Whether to enable batch resilience (continue processing when
    # individual batches fail)
    enable_batch_resilience: SkipJsonSchema[bool] = Field(default=True)
    # Maximum number of consecutive batch failures before aborting the task
    max_consecutive_batch_failures: SkipJsonSchema[int] = Field(default=5, gt=0)
    # Whether to retry failed batch files individually after batch processing
    individual_file_retry_enabled: SkipJsonSchema[bool] = Field(default=True)

    # Shutdown variables
    pod_heartbeat_shutdown_timeout: SkipJsonSchema[int] = Field(default=15, gt=0)
    pod_vitals_handler_shutdown_timeout: SkipJsonSchema[int] = Field(default=10, gt=0)

    # Prefect variables
    max_number_of_prefect_workers: SkipJsonSchema[int] = Field(default=3, gt=0)
    # TODO: [BIT-3597] Remove this feature flag
    # Should match the default of the app
    file_multiprocessing_enabled: bool = Field(default=False)

    # Validators
    @classmethod
    @field_validator("default_torch_device")
    def _validate_torch_device(cls, arg: Optional[str]) -> Optional[str]:
        """Check that the supplied torch device is one of the expected types."""
        if arg is None:
            return None
        if arg in ("cpu", "mps") or arg.startswith("cuda"):
            return arg
        else:
            raise ValidationError(
                "Invalid choice for default torch device, should be one of:"
                ' "cpu",'
                ' "mps",'
                ' "cuda",'
                ' or "cuda:<device_id>" (e.g. "cuda:1").'
            )


class PathSettings(BaseSettings):
    """Settings related to storage paths, etc."""

    model_config = DEFAULT_SETTINGS_CONFIG

    # The default path structure looks like this:
    # .                                   (output_dir)
    # ├── bitfount_logs                   (logs_dir)
    # └── ~/.bitfount/                    (storage_path)
    #     ├── plugins/                    (plugin_path)
    #     │   └── federated               (federated_plugin_path)
    #     ├── cache                       (cache_dir)
    #     │   └── datasets                (dataset_cache_dir)
    #     └── known_workers.yml           (key_store)
    storage_path: SkipJsonSchema[Path] = Field(
        default=(Path.home() / ".bitfount").expanduser()
    )

    # These fields are just used to drive our computed fields below
    # Overriding one of the root paths (storage_path, plugin_path, cache_dir)
    # Will affect all child paths, unless those paths are also overridden
    # These can't be prefixed with an `_` as Fields cannot be private in pydantic
    raw_plugin_path: SkipJsonSchema[Optional[Path]] = Field(
        default=None, alias="bitfount_plugin_path", exclude=True, repr=False
    )
    raw_federated_plugin_path: SkipJsonSchema[Optional[Path]] = Field(
        default=None, alias="bitfount_federated_plugin_path", exclude=True, repr=False
    )
    raw_key_store: SkipJsonSchema[Optional[Path]] = Field(
        default=None, alias="bitfount_key_store", exclude=True, repr=False
    )
    raw_cache_dir: SkipJsonSchema[Optional[Path]] = Field(
        default=None, alias="bitfount_cache_dir", exclude=True, repr=False
    )
    raw_dataset_cache_dir: SkipJsonSchema[Optional[Path]] = Field(
        default=None, alias="bitfount_dataset_cache_dir", exclude=True, repr=False
    )

    # These fields are standalone, they don't depend on other paths
    # So won't be recomputed if other paths change
    logs_dir: SkipJsonSchema[Path] = Field(default=Path("bitfount_logs"))
    output_dir: SkipJsonSchema[Path] = Field(default=Path("."))
    proxy_cert_dir: SkipJsonSchema[Optional[Path]] = Field(default=None)

    @computed_field  # type: ignore[prop-decorator] # reason: this is required by pydantic
    @property
    def plugin_path(self) -> Path:
        """Plugins storage."""
        return (
            self.raw_plugin_path.expanduser()
            if self.raw_plugin_path
            else self.storage_path / "_plugins"
        )

    @computed_field  # type: ignore[prop-decorator] # reason: this is required by pydantic
    @property
    def federated_plugin_path(self) -> Path:
        """Federated-subfolder of plugins."""
        return (
            self.raw_federated_plugin_path.expanduser()
            if self.raw_federated_plugin_path
            else self.plugin_path / "federated"
        )

    @computed_field  # type: ignore[prop-decorator] # reason: this is required by pydantic
    @property
    def key_store(self) -> Path:
        """Known workers keystore."""
        return (
            self.raw_key_store.expanduser()
            if self.raw_key_store
            else self.storage_path / "known_workers.yml"
        )

    @computed_field  # type: ignore[prop-decorator] # reason: this is required by pydantic
    @property
    def cache_dir(self) -> Path:
        """Cache(s) location."""
        return (
            self.raw_cache_dir.expanduser()
            if self.raw_cache_dir
            else self.storage_path / "cache"
        )

    @computed_field  # type: ignore[prop-decorator] # reason: this is required by pydantic
    @property
    def dataset_cache_dir(self) -> Path:
        """Dataset cache(s) location."""
        return (
            self.raw_dataset_cache_dir.expanduser()
            if self.raw_dataset_cache_dir
            else self.cache_dir / "datasets"
        )


class LogSettings(BaseSettings):
    """Settings related to log configuration."""

    model_config = DEFAULT_SETTINGS_CONFIG

    _DEFAULT_LOG_FORMAT: Final[str] = (
        "%(asctime)s:"
        " %(processName)s.%(threadName)s:"
        " %(levelname)s"
        " %(name)s:%(filename)s:%(lineno)d"
        " %(message)s"
    )
    _DEFAULT_LOG_DATE_FORMAT: Final[str] = "%H:%M:%S"

    auto_configure_logging: SkipJsonSchema[bool] = Field(default=True)
    log_format: SkipJsonSchema[str] = Field(default=_DEFAULT_LOG_FORMAT)
    log_date_format: SkipJsonSchema[str] = Field(default=_DEFAULT_LOG_DATE_FORMAT)
    file_log_format: SkipJsonSchema[str] = Field(default=_DEFAULT_LOG_FORMAT)

    limit_logs: SkipJsonSchema[bool] = Field(default=False)
    log_to_file: SkipJsonSchema[bool] = Field(default=True)

    tb_limit: SkipJsonSchema[int] = Field(default=3)
    multithreading_debug: SkipJsonSchema[bool] = Field(default=False)
    data_cache_debug: SkipJsonSchema[bool] = Field(default=False)
    data_cache_sql_debug: SkipJsonSchema[bool] = Field(default=False)

    # [LOGGING-IMPROVEMENTS]
    log_authentication_headers: SkipJsonSchema[bool] = Field(default=False)

    log_dicom_fixes: SkipJsonSchema[bool] = Field(default=False)
    log_hooks: SkipJsonSchema[bool] = Field(default=False)
    log_message_service: SkipJsonSchema[bool] = Field(default=False)
    log_pod_heartbeat: SkipJsonSchema[bool] = Field(default=False)
    log_transformation_apply: SkipJsonSchema[bool] = Field(default=False)
    log_web_utils: SkipJsonSchema[bool] = Field(default=False)

    # Third-party
    log_httpxcore: SkipJsonSchema[bool] = Field(default=False)
    log_httpx: SkipJsonSchema[bool] = Field(default=False)
    log_matplotlib: SkipJsonSchema[bool] = Field(default=False)
    log_private_eye: SkipJsonSchema[bool] = Field(default=False)
    log_private_eye_fixes: SkipJsonSchema[bool] = Field(default=False)
    log_urllib3: SkipJsonSchema[bool] = Field(default=False)

    log_fully: SkipJsonSchema[bool] = Field(default=False)

    def model_post_init(self, *args: Any) -> None:
        """Additional post-init log setup."""
        if self.log_fully:
            self.log_authentication_headers = True
            self.log_dicom_fixes = True
            self.log_hooks = True
            self.log_message_service = True
            self.log_pod_heartbeat = True
            self.log_transformation_apply = True
            self.log_web_utils = True

            self.log_httpxcore = True
            self.log_httpx = True
            self.log_matplotlib = True
            self.log_private_eye = True
            self.log_urllib3 = True


class SMARTOnFHIRSettings(BaseSettings):
    """Settings for SMART On FHIR interaction."""

    smart_on_fhir_url: SkipJsonSchema[Optional[str]] = Field(default=None)
    smart_on_fhir_resource_server_url: SkipJsonSchema[Optional[str]] = Field(
        default=None
    )
    smart_on_fhir_api_timeout: SkipJsonSchema[int] = Field(default=30, gt=0)


settings = Settings()


def configuration_schema() -> dict[str, Any]:
    """Generate a JSON schema for visible configuration."""
    return settings.model_json_schema()


def refresh_configuration() -> None:
    """Hot-reloads configuration values.

    Lets us refresh settings at runtime
    Avoiding having to restart everything to load in environment variables
    https://docs.pydantic.dev/latest/concepts/pydantic_settings/#in-place-reloading
    """
    settings.__init__()  # type: ignore[misc] # reason: Documented approach from pydantic


# Logging/Error Handling
LogLevel = Literal[
    50,  # logging.CRITICAL
    40,  # logging.ERROR
    30,  # logging.WARNING
    20,  # logging.INFO
    10,  # logging.DEBUG
]

##############################################
# End of Public Config/Environment Variables #
##############################################

########################################
# Private Config/Environment Variables #
########################################
_BITFOUNT_CLI_MODE: bool = False
_PRODUCTION_ENVIRONMENT: Final[str] = "production"
_STAGING_ENVIRONMENT: Final[str] = "staging"
_DEVELOPMENT_ENVIRONMENT: Final[str] = "dev"
_SANDBOX_ENVIRONMENT: Final[str] = "sandbox"
_ENVIRONMENT_CANDIDATES: tuple[str, ...] = (
    _PRODUCTION_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _DEVELOPMENT_ENVIRONMENT,
    _SANDBOX_ENVIRONMENT,
)


# Role types for YAML version selection
RoleType = Literal["pod", "modeller"]


def _get_plugin_yaml_versions(role: Optional[RoleType] = None) -> Optional[list[str]]:
    """Get yaml versions from plugins directory if available.

    Args:
        role: Optional role to get specific versions for ("pod" or "modeller")

    Returns:
        List of yaml versions if plugins are used, None otherwise
    """
    if not hasattr(settings, "paths") or not hasattr(settings.paths, "plugin_path"):
        return None

    plugin_path = settings.paths.plugin_path
    version_file = os.path.join(plugin_path, "__version__.py")

    if not os.path.exists(version_file):
        return None

    try:
        spec = util.spec_from_file_location("__version__", version_file)
        if spec is None or spec.loader is None:
            return None

        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # If a specific role is requested, try to get role-specific versions first
        if role is not None:
            if role == "modeller" and hasattr(mod, "__modeller_yaml_versions__"):
                return cast(list[str], mod.__modeller_yaml_versions__)
            # If role-specific versions aren't available, fall back to legacy versions
            elif hasattr(mod, "__yaml_versions__"):
                return cast(list[str], mod.__yaml_versions__)
        # If no specific role is requested, just get the legacy versions
        elif hasattr(mod, "__yaml_versions__"):
            return cast(list[str], mod.__yaml_versions__)

        return None
    except Exception as e:
        logger.warning(f"Error loading plugin version: {e}")
        return None


def get_compatible_yaml_versions_for_role(role: RoleType) -> list[str]:
    """Get the compatible YAML versions for a specific role.

    Args:
        role: Either "pod" or "modeller"

    Returns:
        List of compatible YAML versions for the specified role,
        including legacy versions
    """
    # Check if custom plugin versions exist first for this role
    plugin_versions = _get_plugin_yaml_versions(role)
    if plugin_versions is not None:
        # For plugins, we return only what they define
        return plugin_versions

    # For built-in versions, combine role-specific with
    # legacy for backward compatibility
    combined_versions = []

    # Add role-specific versions
    if role == "modeller":
        combined_versions.extend(modeller_yaml_versions)
    elif role == "pod":
        # For the pod, we use the legacy versions
        combined_versions.extend(legacy_yaml_versions)
    else:
        raise ValueError(f"Unknown role: {role}")

    # Add legacy versions that aren't already included
    for version in legacy_yaml_versions:
        if version not in combined_versions:
            combined_versions.append(version)

    return combined_versions


def _get_compatible_yaml_versions() -> Optional[list[str]]:
    """Get the compatible yaml versions.

    If plugins are used, they need to contain the compatible
    version in the plugins directory in a __version__.py file.
    Else we use the version defined in __version__.py

    Note: This function maintains backward compatibility with legacy code.
    New code should use get_compatible_yaml_versions_for_role() instead.
    """
    return _get_plugin_yaml_versions()


plugin_versions = _get_compatible_yaml_versions()
_BITFOUNT_COMPATIBLE_YAML_VERSIONS: list[str] = (
    plugin_versions if plugin_versions is not None else legacy_yaml_versions
)


@lru_cache(maxsize=1)
def _get_environment() -> str:
    """Returns bitfount environment to be used from BITFOUNT_ENVIRONMENT variable.

    The result is cached to avoid multiple warning messages. This means that changes to
    the `BITFOUNT_ENVIRONMENT` environment variable will not be detected whilst the
    library is running.

    Returns:
        str: PRODUCTION_ENVIRONMENT, STAGING_ENVIRONMENT, DEVELOPMENT_ENVIRONMENT or
            SANDBOX_ENVIRONMENT

    """

    BITFOUNT_ENVIRONMENT = os.getenv("BITFOUNT_ENVIRONMENT", _PRODUCTION_ENVIRONMENT)
    if BITFOUNT_ENVIRONMENT == "":
        #   It can happen that the environment variable is set to an empty string,
        #   we default to the prod environment in this case.
        BITFOUNT_ENVIRONMENT = _PRODUCTION_ENVIRONMENT

    if BITFOUNT_ENVIRONMENT not in _ENVIRONMENT_CANDIDATES:
        raise ValueError(
            f"The environment specified by the environment variable "
            f"BITFOUNT_ENVIRONMENT ({BITFOUNT_ENVIRONMENT}) is not in the supported "
            f"list of environments ({_ENVIRONMENT_CANDIDATES})"
        )
    if BITFOUNT_ENVIRONMENT == _STAGING_ENVIRONMENT:
        logger.warning(
            "Using the staging environment. "
            + "This will only work for Bitfount employees."
        )
    if BITFOUNT_ENVIRONMENT == _DEVELOPMENT_ENVIRONMENT:
        logger.warning(
            "Using the development environment. "
            + "This will only work if you have all Bitfount services running locally."
        )
    if BITFOUNT_ENVIRONMENT == _SANDBOX_ENVIRONMENT:
        logger.warning(
            "Using the sandbox environment. "
            + "This will only work for Bitfount employees."
        )
    return BITFOUNT_ENVIRONMENT


###############################################
# End of Private Config/Environment Variables #
###############################################

##################
# Backend Engine #
##################
_PYTORCH_ENGINE: Final[str] = "pytorch"
_BASIC_ENGINE: Final[str] = "basic"
_ENGINE_CANDIDATES: tuple[str, ...] = (
    _BASIC_ENGINE,
    _PYTORCH_ENGINE,
)

# Set BITFOUNT_ENGINE, defaulting to PYTORCH_ENGINE or BASIC_ENGINE
# Start with BASIC_ENGINE as default
BITFOUNT_ENGINE: str = _BASIC_ENGINE
try:
    # Use the type specified by envvar if present
    BITFOUNT_ENGINE = os.environ["BITFOUNT_ENGINE"]
    # Check that the engine option is a valid one
    if BITFOUNT_ENGINE not in _ENGINE_CANDIDATES:
        raise ValueError(
            f"The backend engine specified by the environment variable "
            f"BITFOUNT_ENGINE ({BITFOUNT_ENGINE}) is not in the supported list of "
            f"backends ({_ENGINE_CANDIDATES})"
        )
except KeyError:
    # Don't import pytorch if in a child process
    if not settings.private.child_process:
        # Otherwise, if PyTorch is installed use PYTORCH_ENGINE
        try:
            import torch

            BITFOUNT_ENGINE = _PYTORCH_ENGINE
        except ImportError:
            pass
    else:
        logger.warning("Not importing PyTorch in a child process.")

#########################
# End of Backend Engine #
#########################

##############
# DP Support #
##############
DP_AVAILABLE: bool
try:
    import opacus  # noqa: F401

    # TODO: [BIT-4640] Re-enable PrivateSQLQuery
    import snsql  # noqa: F401

    DP_AVAILABLE = True
except ImportError:
    logger.debug("Differential Privacy requirements not installed.")
    DP_AVAILABLE = False
#####################
# End of DP Support #
#####################


#############################
# GPU information retrieval #
#############################
def _get_gpu_metadata_gputil() -> tuple[Optional[str], int]:
    """Returns gpu metadata from GPUtil.

    Uses the name of the first GPU thereby assuming that there is only 1 type of GPU
    attached to the machine.

    Returns:
        tuple[Optional[str], int]: name of gpu and how many there are
    """
    gpus = GPUtil.getGPUs()
    if gpus:
        return gpus[0].name, len(gpus)
    # nvidia-smi installed, but no GPU available
    return None, 0


def get_cuda_metadata_pytorch() -> tuple[Optional[str], int]:
    """Return gpu metadata from pytorch.

    Returns:
        tuple[Optional[str], int]: name of gpu and how many there are
    """
    try:
        if torch.cuda.is_available():
            gpus: int = torch.cuda.device_count()
            if gpus > 0:
                gpu_0_name: str = torch.cuda.get_device_name(0)
                logger.info(f"CUDA support detected. GPU ({gpu_0_name}) will be used.")
                return gpu_0_name, gpus
            else:
                logger.debug("CUDA is available to PyTorch but there are no GPUs")
        else:
            logger.debug("CUDA is not available to PyTorch")
    except Exception as ex:
        logger.info(f"CUDA is not available to PyTorch: {ex}")

    return None, 0


_GPU_COUNT_FUNCTION_LOOKUP: dict[str, Callable[..., tuple[Optional[str], int]]] = {
    _BASIC_ENGINE: _get_gpu_metadata_gputil,
    _PYTORCH_ENGINE: get_cuda_metadata_pytorch,
}


def get_gpu_metadata() -> tuple[Optional[str], int]:
    """Retrieve details about GPUs if available.

    Uses tools available in the appropriate backend,
    to find GPUs that are usable by the backend.

    Returns: a tuple of GPU name and count.
    """
    # noinspection PyBroadException
    try:
        return _GPU_COUNT_FUNCTION_LOOKUP[BITFOUNT_ENGINE]()
    except Exception as ex:
        # Broad exception handling here as libraries may throw various exceptions
        # But if anything is raised we can assume we don't have GPU access
        logger.warning(f"Encountered exception whilst gathering GPU information: {ex}")
        logger.warning("No GPU info will be used.")
        return None, 0


def has_mps() -> bool:
    """Detect if MPS is available and torch can use it."""
    mps = False
    try:
        # Older PyTorch versions don't have this attribute so need to catch
        if torch.backends.mps.is_available() and platform.processor() in (
            "arm",
            "arm64",
        ):
            if settings.use_mps:
                mps = True
                logger.info("MPS is available to PyTorch.")
            else:
                logger.debug("MPS support detected, but has been switched off.")
    except AttributeError:
        logger.info("Pytorch version does not support MPS.")
    return mps


def has_cuda() -> bool:
    """Detect if CUDA is available and torch can use it."""
    cuda_device_name, _ = get_cuda_metadata_pytorch()
    return cuda_device_name is not None


####################################
# End of GPU information retrieval #
####################################


# User-Agent string for requests
_USER_AGENT_STRING: Final = f"Bitfount SDK {bf_version}"
