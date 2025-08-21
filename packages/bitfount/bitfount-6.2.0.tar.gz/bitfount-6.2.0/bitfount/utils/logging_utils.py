"""Utilities for logging and warning messages functionality."""

from __future__ import annotations

from collections import Counter
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
import functools
import importlib
import logging
from pathlib import Path
import re
import sys
from typing import Any, Callable, Final, Optional, Type, TypeVar, Union
import warnings

from bitfount import config
from bitfount.config import (
    _PYTORCH_ENGINE,
    BITFOUNT_ENGINE,
)

logger = logging.getLogger(__name__)

# Timestamp when this module is read in. Guarantees that any file-loggers will refer
# to the same file.
_log_file_time: Final = datetime.now().strftime("%Y-%m-%d-%H%M%S")


@contextmanager
def filter_stderr(to_filter: Union[str, re.Pattern]) -> Generator[None, None, None]:
    """Filter stderr messages emitted within this context manager.

    Will remove any messages where the start matches the filter pattern whilst allowing
    any other messages to go through.

    Args:
        to_filter: Regex pattern to match the start of messages to be filtered.
    """
    # Compile regex pattern if not already done
    reg_to_filter: re.Pattern[str]
    if isinstance(to_filter, str):
        reg_to_filter = re.compile(to_filter)
    else:
        reg_to_filter = to_filter

    # Store previous stderr.write() method
    _stderr_write = sys.stderr.write

    def _write(s: str) -> int:
        """Override write() method of stderr."""
        if reg_to_filter.match(s):
            # Do nothing, write 0 bytes
            return 0
        else:
            return _stderr_write(s)

    # mypy_reason: mypy is overzealous with functions being assigned to instance
    #              methods as it cannot easily determine the type of the callable
    #              between bound and unbound. "type: ignore" is the recommended
    #              workaround.
    #              See: https://github.com/python/mypy/issues/2427
    try:
        sys.stderr.write = _write  # type: ignore[method-assign] # Reason: see comment
        yield
    finally:
        # Need to ensure that anything written to stderr during this time is flushed
        # out as otherwise may not be printed until the stderr.write is reset
        sys.stderr.flush()
        # Reset stderr.write() method
        sys.stderr.write = _stderr_write  # type: ignore[method-assign] # Reason: see comment # noqa: E501


def _configure_third_party_logger(
    module: str,
    logger_name: str,
    log_level: Union[int, str] = config.settings.log_level,
    propagate: bool = True,
    clear_handlers: bool = False,
    custom_handlers: Optional[list[logging.Handler]] = None,
) -> None:
    """Configure third party logger with specified log level."""

    # Import here to guarantee that the third party
    # logger is set up before we override it.
    try:
        importlib.import_module(module)
    except ImportError:
        return

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = propagate
    logger.handlers = [] if clear_handlers else logger.handlers

    if custom_handlers:
        for custom_handler in custom_handlers:
            logger.addHandler(custom_handler)


def _customise_third_party_loggers() -> None:
    """Customised third-party loggers setup.

    Sets third-party loggers levels as WARNING or LOG_LEVEL.
    Configures handlers, and propagation of loggers.
    """
    # Custom handlers
    bitfount_file_handler = _get_bitfount_log_file_handler()
    warning_handler = logging.StreamHandler(sys.stderr)
    # mypy_reason: Function sig is correct, see https://docs.python.org/3/library/logging.html#logging.Filter.filter # noqa: E501
    warning_handler.addFilter(is_not_pytorch_lightning_warning)  # type: ignore[arg-type] # Reason: see message # noqa: E501

    _configure_third_party_logger(
        module="pytorch_lightning",
        logger_name="pytorch_lightning",
        log_level=logging.WARNING,
        propagate=False,
        clear_handlers=True,
        custom_handlers=[bitfount_file_handler],
    )
    _configure_third_party_logger(
        module="httpcore",
        logger_name="httpcore",
        log_level=config.settings.log_level
        if config.settings.logging.log_httpxcore
        else logging.WARNING,
    )
    _configure_third_party_logger(
        module="httpx",
        logger_name="httpx",
        log_level=config.settings.log_level
        if config.settings.logging.log_httpx
        else logging.WARNING,
    )
    _configure_third_party_logger(
        module="matplotlib",
        logger_name="matplotlib",
        log_level=config.settings.log_level
        if config.settings.logging.log_matplotlib
        else logging.WARNING,
    )
    _configure_third_party_logger(
        module="urllib3.connectionpool",
        logger_name="urllib3.connectionpool",
        log_level=config.settings.log_level
        if config.settings.logging.log_urllib3
        else logging.WARNING,
    )
    _configure_third_party_logger(
        module="warnings",
        logger_name="py.warnings",
        log_level=config.settings.log_level,
        propagate=False,
        clear_handlers=False,
        custom_handlers=[warning_handler, bitfount_file_handler],
    )

    # Configure private-eye logger regardless of if it is an installed package or
    # the vendored entry
    _configure_third_party_logger(
        module="private_eye",
        logger_name="private_eye",
        log_level=config.settings.log_level
        if config.settings.logging.log_private_eye
        else logging.ERROR,
    )
    _configure_third_party_logger(
        module="bitfount._vendor.private_eye",
        logger_name="bitfount._vendor.private_eye",
        log_level=config.settings.log_level
        if config.settings.logging.log_private_eye
        else logging.ERROR,
    )


def _customise_third_party_warnings() -> None:
    """Customised third-party warnings setup."""
    # Pytorch:
    # Filter out warnings related to IterableDataset (as not an issue for us
    # as we guarantee only one worker); should only be processed once, not
    # per-batch.
    warnings.filterwarnings(
        action="once",
        message=r"Your `IterableDataset` has `__len__` defined.",
        category=UserWarning,
        module="pytorch_lightning.utilities",
    )


def _configure_logging() -> None:
    """Configure logging and third-party loggers to adhere to Bitfount style."""
    # [LOGGING-IMPROVEMENTS]
    # Set up logging to capture any `warnings` module issues raised.
    logging.captureWarnings(True)
    _customise_third_party_warnings()
    _customise_third_party_loggers()
    # Finally, set up the main `bitfount` logger to output to stream
    setup_loggers([logging.getLogger("bitfount")])


def _get_bitfount_console_handler(
    log_level: Union[int, str] = config.settings.log_level,
) -> logging.StreamHandler:
    """Return a console handler pre-configured for Bitfount style."""
    console_handler = logging.StreamHandler(sys.stdout)
    console_log_formatter = logging.Formatter(
        config.settings.logging.log_format,
        datefmt=config.settings.logging.log_date_format,
    )
    console_handler.setFormatter(console_log_formatter)
    console_handler.setLevel(log_level)
    return console_handler


def _get_bitfount_log_file_handler(
    log_file_subdir_name: Optional[str] = None, log_file_name: Optional[str] = None
) -> logging.FileHandler:
    """Get a FileHandler pre-configured for Bitfount style.

    Will create the log file in setting.logs_dir unless log_file_subdir_name is
    specified in which case it will be created in that subdirectory within
    setting.logs_dir.

    Log-level will be DEBUG.
    """
    logfile_dir = _get_bitfount_logdir(log_file_subdir_name)
    log_file_name = log_file_name or _log_file_time

    # Set file logging configuration
    file_handler = logging.FileHandler(f"{logfile_dir}/{log_file_name}.log")
    file_log_formatter = logging.Formatter(config.settings.logging.file_log_format)
    file_handler.setFormatter(file_log_formatter)
    file_handler.setLevel(logging.DEBUG)

    return file_handler


def _get_bitfount_logdir(subdir_name: Optional[str] = None) -> Path:
    """Get the directory that Bitfount logs should be written to.

    This will be config.settings.paths.logs_dir
    unless subdir_name is specified in which case
    it will be that subdirectory within config.settings.paths.logs_dir.
    """
    # Establish log directory and create it if it doesn't exist
    parent_logfile_dir = config.settings.paths.logs_dir

    if subdir_name:
        logfile_dir = parent_logfile_dir / subdir_name
    else:
        logfile_dir = parent_logfile_dir

    logfile_dir.mkdir(parents=True, exist_ok=True)
    return logfile_dir


def setup_loggers(
    loggers: list[logging.Logger],
    log_file_dir_name: Optional[str] = None,
    log_level: Union[int, str] = config.settings.log_level,
    clear_existing_handlers: bool = True,
    clear_existing_filters: bool = True,
) -> list[logging.Logger]:
    """Set up supplied loggers with stdout and file handlers.

    Creates a logfile in 'logs' directory with the current date and time and outputs all
    logs at the "DEBUG" level. Also outputs logs to stdout at the "INFO" level. A common
    scenario is to attach handlers only to the root logger, and to let propagation take
    care of the rest.

    Args:
        loggers: The logger(s) to set up
        log_file_dir_name: Creates a subdirectory inside config.settings.paths.logs_dir
            if provided. Defaults to None.
        log_level: The log level to apply to the console logs
        clear_existing_handlers: If True, clear existing handlers for each logger
        clear_existing_filters: If True, clear existing filters for each logger

    Returns:
        A list of updated logger(s).
    """
    handlers: list[logging.Handler] = []

    # If logging to file is enabled, create appropriate FileHandler
    if config.settings.logging.log_to_file:
        file_handler = _get_bitfount_log_file_handler(log_file_dir_name)
        handlers.append(file_handler)

    # Set console logging configuration
    console_handler = _get_bitfount_console_handler(log_level)
    handlers.append(console_handler)

    # Cannot use `logger` as iter-variable as shadows outer name.
    for i_logger in loggers:
        # Clear any existing handler/filter configuration
        if clear_existing_handlers:
            i_logger.handlers = []
        if clear_existing_filters:
            i_logger.filters = []

        # Set base level to DEBUG and ensure messages are not duplicated
        i_logger.setLevel(logging.DEBUG)
        i_logger.propagate = False

        # Add handlers to loggers
        for handler in handlers:
            i_logger.addHandler(handler)

    return loggers


# PyTorch-related utilities
def is_not_pytorch_lightning_warning(record: logging.LogRecord) -> int:
    """Returns 0 if is a warning generated by PyTorch Lightning, 1 otherwise."""
    msg: str = record.getMessage()

    # warnings generates a log message of form "<file_path>:<line_no> ..." so should
    # be able to only filter on lightning mentions in file path.
    file_path: str = msg.split(":", maxsplit=1)[0]
    if "pytorch_lightning" in file_path:
        return 0  # i.e. should not be logged
    else:
        return 1  # i.e. should be logged


def log_pytorch_env_info_if_available() -> None:
    """Log PyTorch environment info if PyTorch is available."""
    if BITFOUNT_ENGINE == _PYTORCH_ENGINE:
        from torch.utils.collect_env import get_pretty_env_info

        logger.debug(get_pretty_env_info())


SAMPLE_LOGGING_INTERVAL: Final = 1000


class SampleFilter(logging.Filter):
    """A logging filter that tracks counts for logs and only logs at intervals.

    Useful for very frequent logs where we only care about logging "samples" of the
    logs, at some specific interval, for example, whilst iterating through a list of
    files.
    """

    def __init__(
        self, interval: int = SAMPLE_LOGGING_INTERVAL, *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        # Counter of (pathname, lineno) to counts of logs
        self._sample_counter: Counter[tuple[str, int]] = Counter()
        self.interval = interval

    def filter(self, record: logging.LogRecord) -> bool:
        """Returns True if the record should be logged, False otherwise."""
        # If sampling is not enabled for this log record, then we will always log
        if not (hasattr(record, "sample") and record.sample is True):
            return True

        # Otherwise, keep track of the count, only logging if the count is at the
        # specified interval or is the first time this has been logged
        log_record_key = (record.pathname, record.lineno)
        self._sample_counter[log_record_key] += 1
        if (
            self._sample_counter[log_record_key] == 1
            or self._sample_counter[log_record_key] % self.interval == 0
        ):
            return True
        else:
            return False


_T = TypeVar("_T")


def deprecated_class_name(cls: Type[_T]) -> Callable[..., _T]:
    """Class decorator to log a DeprecationWarning for deprecated class names.

    Used for cases where we have:
    ```
    class NewClassName:
        ...

    @deprecated_class_name
    class OldClassName(NewClassName):
        pass
    ```
    """

    @functools.wraps(cls)
    def _class_wrapper(*args: Any, **kwargs: Any) -> _T:
        # Wraps "cls" (in actuality wraps the __init__ method)

        # Find the name of the parent class, or use "new class name" as a fallback
        try:
            parent_name = f"{cls.mro()[1].__name__}()"
        except Exception:
            parent_name = "new class name"

        # stacklevel=2 means that the _calling_ code of __init__ is where the
        # deprecation is logged
        warnings.warn(
            f"Using class name {cls.__name__} is deprecated"
            f" and will be removed in a future release."
            f" Please use {parent_name} instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        return cls(*args, **kwargs)

    return _class_wrapper
