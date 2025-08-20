"""Hook infrastructure for Bitfount."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from enum import Enum
from functools import partial, wraps
import logging
from types import FunctionType, MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Protocol,
    Union,
    cast,
    overload,
    runtime_checkable,
)

import pandas as pd

from bitfount import config
from bitfount.exceptions import HookError
from bitfount.types import _JSONDict

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import FileSystemIterableSource
    from bitfount.federated.algorithms.base import _BaseAlgorithm
    from bitfount.federated.helper import TaskContext
    from bitfount.federated.pod import Pod
    from bitfount.federated.protocols.base import _BaseProtocol

__all__: list[str] = [
    "BaseAlgorithmHook",
    "BasePodHook",
    "HookType",
    "get_hooks",
]

logger = logging.getLogger(__name__)

_HOOK_DECORATED_ATTRIBUTE = "_decorate"


##################
# HOOK PROTOCOLS #
##################
# These classes define the python protocols that can be used for creating custom
# hook implementations. They define various hooks that can be overridden in the
# subclass to be called at various points in the pod/modeller/algorithm/protocol
# flow.
#
# Basic concrete classes are provided later in this file.
#
# A registry is also defined that will allow retrieval of all hooks of a given type
# (e.g. all pod hook classes).
class HookType(Enum):
    """Enum for hook types."""

    POD = "POD"
    MODELLER = "MODELLER"
    ALGORITHM = "ALGORITHM"
    PROTOCOL = "PROTOCOL"
    DATASOURCE = "DATASOURCE"


@runtime_checkable
class HookProtocol(Protocol):
    """Base Protocol for hooks used just for type annotation."""

    hook_name: str

    @property
    def type(self) -> HookType:
        """Return the hook type."""
        ...

    @property
    def registered(self) -> bool:
        """Return whether the hook is registered."""
        ...

    def register(self) -> None:
        """Register the hook.

        Adds hook to the registry against the hook type.
        """
        ...

    def deregister(self) -> None:
        """Deregister the hook.

        Removes hook from the registry against the hook type.
        """
        ...


@runtime_checkable
class PodHookProtocol(HookProtocol, Protocol):
    """Protocol for Pod hooks."""

    def on_pod_init_start(
        self,
        pod: Pod,
        pod_name: str,
        username: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the very start of pod initialisation."""
        ...

    def on_pod_init_progress(
        self,
        pod: Pod,
        message: str,
        datasource_name: Optional[str] = None,
        base_datasource_names: Optional[list[str]] = None,
        pod_db_enabled: Optional[bool] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at key points of pod initialisation."""
        ...

    def on_pod_init_end(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the end of pod initialisation."""
        ...

    def on_pod_init_error(
        self, pod: Pod, exception: BaseException, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook if an uncaught exception is raised during pod initialisation."""
        ...

    def on_pod_startup_start(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very start of pod startup."""
        ...

    def on_pod_task_data_check(
        self, task_id: Optional[str], *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at start of a job request to check that the pod has data."""
        ...

    def on_pod_startup_error(
        self, pod: Pod, exception: BaseException, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook if an uncaught exception is raised during pod startup."""
        ...

    def on_pod_startup_end(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the end of pod startup."""
        ...

    def on_task_start(
        self,
        pod: Pod,
        task_id: Optional[str],
        project_id: Optional[str],
        modeller_username: str,
        protocol_name: str,
        save_path: Optional[str] = None,
        primary_results_path: Optional[str] = None,
        dataset_name: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when a new task is received at the start."""
        ...

    def on_task_progress(
        self,
        task_id: Optional[str],
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at key points of the task."""
        ...

    def on_task_error(
        self,
        pod: Pod,
        exception: BaseException,
        task_id: Optional[str],
        project_id: Optional[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when there is an exception in a task."""
        ...

    def on_task_end(
        self, pod: Pod, task_id: Optional[str], *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook when a new task is received at the end."""
        ...

    def on_pod_shutdown_start(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very start of pod shutdown."""
        ...

    def on_pod_shutdown_end(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very end of pod shutdown."""
        ...

    def on_files_partition(
        self,
        datasource: FileSystemIterableSource,
        total_num_files: Optional[int],
        batch_size: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when we partition files to be processed."""
        ...

    def on_file_process_start(
        self,
        datasource: FileSystemIterableSource,
        file_num: int,
        total_num_files: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when a file starts to be processed."""
        ...

    def on_file_process_end(
        self,
        datasource: FileSystemIterableSource,
        file_num: int,
        total_num_files: Optional[int],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when a file processing ends."""
        ...

    def on_file_filter_progress(
        self, total_files: int, total_skipped: int, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook when filtering files to track progress."""
        ...

    def on_batches_complete(
        self,
        task_id: Optional[str],
        modeller_username: str,
        total_batches: int,
        total_files: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when all batches are processed but before resilience starts."""
        ...

    def on_resilience_start(
        self,
        task_id: Optional[str],
        modeller_username: str,
        total_failed_files: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when individual file retry phase begins."""
        ...

    def on_resilience_progress(
        self,
        task_id: Optional[str],
        modeller_username: str,
        current_file: int,
        total_files: int,
        file_name: str,
        success: bool,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook for each individual file retry attempt."""
        ...

    def on_resilience_complete(
        self,
        task_id: Optional[str],
        modeller_username: str,
        total_attempted: int,
        total_succeeded: int,
        total_failed: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when individual file retry phase is complete."""
        ...


@runtime_checkable
class ModellerHookProtocol(HookProtocol, Protocol):
    """Protocol for Modeller hooks."""

    def on_task_request(
        self,
        pod_identifiers: Iterable[str],
        project_id: Optional[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run just before modeller sends task request message."""
        ...

    def on_task_response(
        self,
        accepted_pod_identifiers: list[str],
        task_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run when modeller receives all task response messages."""
        ...

    def on_log_message(
        self,
        message: _JSONDict,
        task_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run when modeller receives a log message from the pod."""
        ...


@runtime_checkable
class AlgorithmHookProtocol(HookProtocol, Protocol):
    """Protocol for Algorithm hooks."""

    def on_init_start(
        self, algorithm: _BaseAlgorithm, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the very start of algorithm initialisation."""
        ...

    def on_init_end(self, algorithm: _BaseAlgorithm, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very end of algorithm initialisation."""
        ...

    def on_run_start(
        self,
        algorithm: _BaseAlgorithm,
        context: Optional[TaskContext],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the very start of algorithm run."""
        ...

    def on_run_end(
        self,
        algorithm: _BaseAlgorithm,
        context: Optional[TaskContext],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the very end of algorithm run."""
        ...

    def on_train_epoch_start(
        self,
        current_epoch: int,
        min_epochs: Optional[int],
        max_epochs: Optional[int],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the start of an epoch testing.

        Only applicable for training algorithms.
        """
        ...

    def on_train_epoch_end(
        self,
        current_epoch: int,
        min_epochs: Optional[int],
        max_epochs: Optional[int],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the end of an epoch testing.

        Only applicable for training algorithms.
        """
        ...


@runtime_checkable
class ProtocolHookProtocol(HookProtocol, Protocol):
    """Protocol for Protocol hooks."""

    def on_init_start(self, protocol: _BaseProtocol, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very start of protocol initialisation."""
        ...

    def on_init_end(self, protocol: _BaseProtocol, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very end of protocol initialisation."""
        ...

    def on_run_start(
        self, protocol: _BaseProtocol, context: TaskContext, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the very start of protocol run."""
        ...

    def on_run_end(
        self, protocol: _BaseProtocol, context: TaskContext, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the very end of protocol run."""
        ...

    def on_resilience_end(
        self, protocol: _BaseProtocol, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the end of protocol resilience."""
        ...


@runtime_checkable
class DatasourceHookProtocol(HookProtocol, Protocol):
    """Protocol for Protocol hooks."""

    def on_datasource_yield_data(
        self, data: pd.DataFrame, *args: Any, **kwrags: Any
    ) -> None:
        """Run the hook when the datasource yields data."""
        ...


# mypy_reason: mypy is overzealous when using type[X] that the class represented must
# be _instantiable_, as that is the most common use case. Here we are only using it
# for subclass checking purposes, so we can ignore the issues.
#
# See: https://github.com/python/mypy/issues/4717
HOOK_TYPE_TO_PROTOCOL_MAPPING: dict[HookType, type[HookProtocol]] = {
    HookType.POD: PodHookProtocol,  # type: ignore[type-abstract] # Reason: see above
    HookType.MODELLER: ModellerHookProtocol,  # type: ignore[type-abstract] # Reason: see above # noqa: E501
    HookType.ALGORITHM: AlgorithmHookProtocol,  # type: ignore[type-abstract] # Reason: see above # noqa: E501
    HookType.PROTOCOL: ProtocolHookProtocol,  # type: ignore[type-abstract] # Reason: see above # noqa: E501
    HookType.DATASOURCE: DatasourceHookProtocol,  # type: ignore[type-abstract] # Reason: see above # noqa: E501
}

# The mutable underlying dict that holds the registry information
_registry: dict[HookType, list[HookProtocol]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[HookType, list[HookProtocol]] = MappingProxyType(_registry)


@overload
def get_hooks(type: Literal[HookType.POD]) -> list[PodHookProtocol]: ...


@overload
def get_hooks(type: Literal[HookType.MODELLER]) -> list[ModellerHookProtocol]: ...


@overload
def get_hooks(type: Literal[HookType.ALGORITHM]) -> list[AlgorithmHookProtocol]: ...


@overload
def get_hooks(type: Literal[HookType.PROTOCOL]) -> list[ProtocolHookProtocol]: ...


@overload
def get_hooks(type: Literal[HookType.DATASOURCE]) -> list[DatasourceHookProtocol]: ...


def get_hooks(
    type: HookType,
) -> Union[
    list[AlgorithmHookProtocol],
    list[PodHookProtocol],
    list[ProtocolHookProtocol],
    list[ModellerHookProtocol],
    list[DatasourceHookProtocol],
]:
    """Get all registered hooks of a particular type.

    Args:
        type: The type of hook to get.

    Returns:
        A list of hooks of the provided type.

    Raises:
        ValueError: If the provided type is not a valid hook type.
    """
    hooks = registry.get(type, [])
    if type == HookType.POD:
        return cast(list[PodHookProtocol], hooks)
    elif type == HookType.MODELLER:
        return cast(list[ModellerHookProtocol], hooks)
    elif type == HookType.ALGORITHM:
        return cast(list[AlgorithmHookProtocol], hooks)
    elif type == HookType.PROTOCOL:
        return cast(list[ProtocolHookProtocol], hooks)
    elif type == HookType.DATASOURCE:
        return cast(list[DatasourceHookProtocol], hooks)

    raise ValueError(f"Unknown hook type {type}")


################
# HOOK CLASSES #
################
# The following are concrete implementations of the various hook protocols defined
# above.
#
# They make use of a custom metaclass to decorate all hook methods such that errors
# within them will be captured appropriately, as errors in hooks should not propagate
# outside of the hook.
def ignore_decorator(f: Callable) -> Callable:
    """Decorator to exclude methods from autodecoration."""
    setattr(f, _HOOK_DECORATED_ATTRIBUTE, False)
    return f


class BaseDecoratorMetaClass(type):
    """Base Metaclass for auto-decorating specific methods of a class."""

    @classmethod
    @abstractmethod
    def do_decorate(cls, attr: str, value: Any) -> bool:
        """Checks if an object should be decorated."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def decorator(f: Callable) -> Callable:
        """Returns the decorator to use."""
        raise NotImplementedError

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, Any],
    ) -> type:
        """Creates a new class with specific methods decorated.

        The methods to decorate are determined by the `do_decorate` method. The class
        must not be abstract.
        """
        # Only decorate if the class is not a subclass of ABC i.e. not abstract
        if ABC not in bases:
            for attr, value in dct.items():
                if cls.do_decorate(attr, value):
                    setattr(value, _HOOK_DECORATED_ATTRIBUTE, True)
                    dct[attr] = cls.decorator(value)
        return super().__new__(cls, name, bases, dct)

    def __setattr__(self, attr: str, value: Any) -> None:
        if self.do_decorate(attr, value):
            value = self.decorator(value)
        super().__setattr__(attr, value)


class HookDecoratorMetaClass(BaseDecoratorMetaClass, type):
    """Decorate all instance methods (unless excluded) with the same decorator."""

    @staticmethod
    def decorator(f: Callable) -> Callable:
        """Hook decorator which logs before and after the hook it decorates.

        The decorator also catches any exceptions in the hook so that a hook can never
        be the cause of an error.
        """

        @wraps(f)
        def wrapper(self: BaseHook, *args: Any, **kwargs: Any) -> Any:
            """Wraps provided function and prints before and after."""
            # [LOGGING-IMPROVEMENTS]
            if config.settings.logging.log_hooks:
                logger.debug(f"Calling hook {f.__name__} from {self.hook_name}")
            try:
                return_val = f(self, *args, **kwargs)
            # NotImplementedError is re-raised as this is unrelated to the behaviour
            # of the hook and is re-caught elsewhere if necessary
            except NotImplementedError:
                raise
            except Exception as e:
                logger.error(f"Exception in hook {f.__name__} from {self.hook_name}")
                logger.exception(e)
            else:
                # [LOGGING-IMPROVEMENTS]
                if config.settings.logging.log_hooks:
                    logger.debug(f"Called hook {f.__name__} from {self.hook_name}")
                return return_val

        return wrapper

    @classmethod
    def do_decorate(cls, attr: str, value: Any) -> bool:
        """Checks if an object should be decorated.

        Private methods beginning with an underscore are not decorated.
        """
        return (
            "__" not in attr
            and not attr.startswith("_")
            and isinstance(value, FunctionType)
            and getattr(value, _HOOK_DECORATED_ATTRIBUTE, True)
        )


class BaseHook(metaclass=HookDecoratorMetaClass):
    """Base hook class."""

    def __init__(self) -> None:
        """Initialise the hook."""
        self.hook_name = type(self).__name__

    @property
    @abstractmethod
    def type(self) -> HookType:
        """Return the hook type."""
        raise NotImplementedError

    @property
    def registered(self) -> bool:
        """Return whether the hook is registered."""
        return self.hook_name in [h.hook_name for h in _registry.get(self.type, [])]

    @ignore_decorator
    def register(self) -> None:
        """Register the hook.

        Adds hook to the registry against the hook type.
        """
        if not isinstance(self, HOOK_TYPE_TO_PROTOCOL_MAPPING[self.type]):
            raise HookError("Hook does not implement the specified protocol")

        if self.registered:
            logger.info(f"{self.hook_name} hook already registered")
            return

        logger.debug(f"Adding {self.hook_name} to Hooks registry")
        existing_hooks = _registry.get(self.type, [])
        existing_hooks.append(self)
        _registry[self.type] = existing_hooks
        logger.info(f"Added {self.hook_name} to Hooks registry")

    @ignore_decorator
    def deregister(self) -> None:
        """Deregister the hook if registered."""
        if self.registered:
            logger.debug(f"Deregistering hook: {self.hook_name}")
            if self in _registry.get(self.type, []):
                _registry[self.type].remove(self)
        else:
            logger.warning(f"Hook {self.hook_name} is not registered.")


class BasePodHook(BaseHook):
    """Base pod hook class."""

    @property
    def type(self) -> HookType:
        """Return the hook type."""
        return HookType.POD

    def on_pod_init_start(
        self,
        pod: Pod,
        pod_name: str,
        username: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the very start of pod initialisation."""
        pass

    def on_pod_init_progress(
        self,
        pod: Pod,
        message: str,
        datasource_name: Optional[str] = None,
        base_datasource_names: Optional[list[str]] = None,
        pod_db_enabled: Optional[bool] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at key points of pod initialisation."""
        pass

    def on_pod_init_end(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the end of pod initialisation."""
        pass

    def on_pod_init_error(
        self, pod: Pod, exception: Exception, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook if an uncaught exception is raised during pod initialisation.

        Raises:
            NotImplementedError: If the hook is not implemented. This is to ensure that
                underlying exceptions are not swallowed if the hook is not implemented.
                This error is caught further up the chain and the underlying exception
                is raised instead.
        """
        raise NotImplementedError()

    def on_pod_startup_start(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very start of pod startup."""
        pass

    def on_pod_startup_error(
        self, pod: Pod, exception: Exception, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook if an uncaught exception is raised during pod startup.

        Raises:
            NotImplementedError: If the hook is not implemented. This is to ensure that
                underlying exceptions are not swallowed if the hook is not implemented.
                This error is caught further up the chain and the underlying exception
                is raised instead.
        """
        raise NotImplementedError()

    def on_pod_startup_end(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the end of pod startup."""
        pass

    def on_task_start(
        self,
        pod: Pod,
        task_id: Optional[str],
        project_id: Optional[str],
        modeller_username: str,
        protocol_name: str,
        save_path: Optional[str] = None,
        primary_results_path: Optional[str] = None,
        dataset_name: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when a new task is received at the start."""
        pass

    def on_pod_task_data_check(
        self, task_id: Optional[str], message: str, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at start of a job request to check that the pod has data."""
        pass

    def on_task_progress(
        self,
        task_id: Optional[str],
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at key points of the task."""
        pass

    def on_task_error(
        self,
        pod: Pod,
        exception: BaseException,
        task_id: Optional[str],
        project_id: Optional[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when there is an exception in a task."""
        pass

    def on_task_abort(
        self,
        pod: Pod,
        message: str,
        task_id: Optional[str],
        project_id: Optional[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when there is an exception in a task."""
        pass

    def on_task_end(
        self, pod: Pod, task_id: Optional[str], *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook when a new task is received at the end."""
        pass

    def on_pod_shutdown_start(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very start of pod shutdown."""
        pass

    def on_pod_shutdown_end(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very end of pod shutdown."""
        pass

    def on_files_partition(
        self,
        datasource: FileSystemIterableSource,
        total_num_files: Optional[int],
        batch_size: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when we partition files to be processed."""
        pass

    def on_file_process_start(
        self,
        datasource: FileSystemIterableSource,
        file_num: int,
        total_num_files: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when a file starts to be processed."""
        pass

    def on_file_process_end(
        self,
        datasource: FileSystemIterableSource,
        file_num: int,
        total_num_files: Optional[int],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when a file processing ends."""
        pass

    def on_file_filter_progress(
        self, total_files: int, total_skipped: int, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook when filtering files to track progress."""
        pass

    def on_batches_complete(
        self,
        task_id: Optional[str],
        modeller_username: str,
        total_batches: int,
        total_files: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when all batches are processed but before resilience starts."""
        pass

    def on_resilience_start(
        self,
        task_id: Optional[str],
        modeller_username: str,
        total_failed_files: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when individual file retry phase begins."""
        pass

    def on_resilience_progress(
        self,
        task_id: Optional[str],
        modeller_username: str,
        current_file: int,
        total_files: int,
        file_name: str,
        success: bool,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook for each individual file retry attempt."""
        pass

    def on_resilience_complete(
        self,
        task_id: Optional[str],
        modeller_username: str,
        total_attempted: int,
        total_succeeded: int,
        total_failed: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook when individual file retry phase is complete."""
        pass


class BaseModellerHook(BaseHook):
    """Base algorithm hook class."""

    @property
    def type(self) -> HookType:
        """Return the hook type."""
        return HookType.MODELLER

    def on_task_request(
        self,
        pod_identifiers: Iterable[str],
        project_id: Optional[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run just before modeller sends task request message."""
        pass

    def on_task_response(
        self,
        accepted_pod_identifiers: list[str],
        task_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run when modeller receives all task response messages."""
        pass

    def on_log_message(
        self,
        message: _JSONDict,
        task_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run when modeller receives a log message from the pod."""
        pass


class BaseAlgorithmHook(BaseHook):
    """Base algorithm hook class."""

    @property
    def type(self) -> HookType:
        """Return the hook type."""
        return HookType.ALGORITHM

    def on_init_start(
        self, algorithm: _BaseAlgorithm, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the very start of algorithm initialisation."""
        pass

    def on_init_end(self, algorithm: _BaseAlgorithm, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very end of algorithm initialisation."""
        pass

    def on_run_start(
        self,
        algorithm: _BaseAlgorithm,
        context: Optional[TaskContext],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the very start of algorithm run."""
        pass

    def on_run_end(
        self,
        algorithm: _BaseAlgorithm,
        context: Optional[TaskContext],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the very end of algorithm run."""
        pass

    def on_train_epoch_start(
        self,
        current_epoch: int,
        min_epochs: Optional[int],
        max_epochs: Optional[int],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the start of an epoch testing.

        Only applicable for training algorithms.
        """
        pass

    def on_train_epoch_end(
        self,
        current_epoch: int,
        min_epochs: Optional[int],
        max_epochs: Optional[int],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Run the hook at the end of an epoch testing.

        Only applicable for training algorithms.
        """
        pass


class BaseProtocolHook(BaseHook):
    """Base protocol hook class."""

    @property
    def type(self) -> HookType:
        """Return the hook type."""
        return HookType.PROTOCOL

    def on_init_start(self, protocol: _BaseProtocol, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very start of protocol initialisation."""
        pass

    def on_init_end(self, protocol: _BaseProtocol, *args: Any, **kwargs: Any) -> None:
        """Run the hook at the very end of protocol initialisation."""
        pass

    def on_run_start(
        self, protocol: _BaseProtocol, context: TaskContext, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the very start of protocol run."""
        pass

    def on_run_end(
        self, protocol: _BaseProtocol, context: TaskContext, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the very end of protocol run."""
        pass

    def on_resilience_end(
        self, protocol: _BaseProtocol, context: TaskContext, *args: Any, **kwargs: Any
    ) -> None:
        """Run the hook at the very end of resilience run."""
        pass


class DataSourceHook(BaseHook):
    """Base datasource hook class."""

    @property
    def type(self) -> HookType:
        """Return the hook type."""
        return HookType.DATASOURCE

    def on_datasource_get_data(
        self, data: pd.DataFrame, *args: Any, **kwrags: Any
    ) -> None:
        """Run the hook when the datasource gets data."""
        pass

    def on_datasource_yield_data(
        self, data: pd.DataFrame, *args: Any, **kwrags: Any
    ) -> None:
        """Run the hook when the datasource yields data."""
        pass


######################
# POD ERROR HANDLING #
######################
# The following are wrappers for various pod methods that will wrap the target method
# with exception handling that will capture any exceptions in the underlying method
# and then call any hooks of the specified type in that error handling block.
def _on_pod_error(hook_name: str, f: Callable) -> Callable:
    """Pod method decorator which catches exceptions in the method.

    If an exception is caught, all registered pod hooks with the provided `hook_name`
    are called.

    Args:
        hook_name: The name of the hook to call if an exception is caught.
        f: The method to decorate.
    """

    @wraps(f)
    def pod_method_wrapper(self: Pod, *args: Any, **kwargs: Any) -> Any:
        """Wraps provided function and calls the relevant hook if there is an exception.

        Re-raises the exception if there are no hooks registered.
        """
        try:
            return_val = f(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in pod {f.__name__}")
            hooks: list[PodHookProtocol] = get_hooks(HookType.POD)
            # Re-raise the exception if there are no hooks registered
            if not hooks:
                raise
            # Otherwise log the exception and call the hooks
            logger.exception(e)
            for hook in hooks:
                try:
                    getattr(hook, hook_name)(self, e)  # Passing pod instance to hook
                except NotImplementedError:
                    # If Pod hooks are registered but do not have the hook, log
                    # a warning
                    logger.warning(
                        f"{hook.hook_name} has not implemented hook {hook_name}"
                    )
                except Exception as e:
                    # Any other exception, log it but then carry on
                    logger.error(
                        f"Error whilst processing hook {hook_name}"
                        f" in {hook.hook_name}: {e}"
                    )
                    logger.debug(e, exc_info=True)

        else:
            return return_val

    return pod_method_wrapper


#: Decorator to be used on Pod.__init__ method.
on_pod_init_error: Callable[[Callable], Callable] = partial(
    _on_pod_error, "on_pod_init_error"
)

#: Decorator to be used on Pod.start method.
on_pod_startup_error: Callable[[Callable], Callable] = partial(
    _on_pod_error, "on_pod_startup_error"
)
