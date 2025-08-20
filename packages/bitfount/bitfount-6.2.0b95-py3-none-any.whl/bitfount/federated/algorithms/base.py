"""Base classes for all algorithms.

Each module in this package defines a single algorithm.

Attributes:
    registry: A read-only dictionary of algorithm factory names to their
              implementation classes.
"""

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Callable, Mapping
from functools import wraps
import inspect
import os
from types import FunctionType, MappingProxyType, new_class
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

from typing_extensions import ParamSpec

from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import (
    DataStructure,
    registry as datastructure_registry,
)
from bitfount.federated.exceptions import AlgorithmError
from bitfount.federated.helper import TaskContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.roles import _RolesMixIn
from bitfount.federated.types import AlgorithmType
from bitfount.hooks import BaseDecoratorMetaClass, HookType, get_hooks
from bitfount.types import T_FIELDS_DICT, T_NESTED_FIELDS, _BaseSerializableObjectMixIn

if TYPE_CHECKING:
    from bitfount.data.datasources.base_source import BaseSource

logger = _get_federated_logger(__name__)


class AlgorithmDecoratorMetaClass(BaseDecoratorMetaClass, type):
    """Decorates the `__init__`, `initialise` and `run` algorithm methods."""

    @staticmethod
    def decorator(f: Callable) -> Callable:
        """Hook and federated error decorators."""
        method_name = f.__name__
        if method_name == "__init__":

            @wraps(f)
            def init_wrapper(
                self: _BaseAlgorithm,
                *args: Any,
                **kwargs: Any,
            ) -> None:
                """Wraps __init__ method of algorithm.

                Calls relevant hooks before and after the algorithm is initialised.

                Args:
                    self: The algorithm instance.
                    hook_kwargs: Keyword arguments to pass to the hooks.
                    *args: Positional arguments to pass to the algorithm.
                    **kwargs: Keyword arguments to pass to the algorithm.
                """
                for hook in get_hooks(HookType.ALGORITHM):
                    hook.on_init_start(self)
                logger.debug(f"Calling method {method_name} from algorithm")
                f(self, *args, **kwargs)
                for hook in get_hooks(HookType.ALGORITHM):
                    hook.on_init_end(self)

            return init_wrapper

        elif method_name == "initialise":

            @wraps(f)
            def initialise_wrapper(
                self: _BaseAlgorithm,
                *args: Any,
                **kwargs: Any,
            ) -> Any:
                """Wraps initialise method of algorithm.

                For the Worker side wraps exceptions in an AlgorithmError
                and logs a federated error to the modeller.

                Args:
                    self: Algorithm instance.
                    *args: Positional arguments to pass to the initialise method.
                    **kwargs: Keyword arguments to pass to the initialise method.

                Returns:
                    Return value of the run method.
                """
                task_context: Optional[TaskContext] = None
                if isinstance(self, BaseModellerAlgorithm):
                    task_context = TaskContext.MODELLER
                elif isinstance(self, BaseWorkerAlgorithm):
                    task_context = TaskContext.WORKER

                try:
                    logger.debug(f"Calling method {method_name} from algorithm")
                    result = f(self, *args, **kwargs)
                    return result
                except Exception as e:
                    if task_context == TaskContext.WORKER:
                        # TODO: [BIT-1619] change to federated_exception
                        logger.federated_error(f"{type(e)}: {e}")
                        raise AlgorithmError(
                            f"Algorithm function {method_name} from "
                            f"{self.__class__.__module__} "
                            f"raised the following exception: {e}"
                        ) from e
                    else:
                        raise e

            return initialise_wrapper

        elif method_name == "run":

            @wraps(f)
            def run_wrapper(
                self: _BaseAlgorithm,
                *args: Any,
                **kwargs: Any,
            ) -> Any:
                """Wraps run method of algorithm.

                Calls hooks before and after the run method is called.

                For the Worker side wraps exceptions in an AlgorithmError
                and logs a federated error to the modeller.

                Args:
                    self: Algorithm instance.
                    *args: Positional arguments to pass to the run method.
                    **kwargs: Keyword arguments to pass to the run method.

                Returns:
                    Return value of the run method.
                """
                task_context: Optional[TaskContext] = None
                if isinstance(self, BaseModellerAlgorithm):
                    task_context = TaskContext.MODELLER
                elif isinstance(self, BaseWorkerAlgorithm):
                    task_context = TaskContext.WORKER

                hooks = get_hooks(HookType.ALGORITHM)
                for hook in hooks:
                    hook.on_run_start(self, task_context)

                try:
                    logger.debug(f"Calling method {method_name} from algorithm")
                    result = f(self, *args, **kwargs)
                    for hook in hooks:
                        hook.on_run_end(self, task_context)
                    return result
                except Exception as e:
                    if task_context == TaskContext.WORKER:
                        # TODO: [BIT-1619] change to federated_exception
                        logger.federated_error(f"{type(e)}: {e}")
                        raise AlgorithmError(
                            f"Algorithm function {method_name} from "
                            f"{self.__class__.__module__} "
                            f"raised the following exception: {e}"
                        ) from e
                    else:
                        raise e

            return run_wrapper

        # This is not expected to ever happen, but if it does, raise an error
        raise ValueError(f"Method {method_name} cannot be decorated.")

    @classmethod
    def do_decorate(cls, attr: str, value: Any) -> bool:
        """Checks if an object should be decorated.

        Only the __init__, initialise and run methods should be decorated.
        """
        return attr in ("__init__", "initialise", "run") and isinstance(
            value, FunctionType
        )


# The metaclass for the BaseAlgorithm must also have all the same classes in its own
# inheritance chain so we need to create a thin wrapper around it.
AbstractAlgorithmDecoratorMetaClass = new_class(
    "AbstractAlgorithmDecoratorMetaClass",
    (ABCMeta, AlgorithmDecoratorMetaClass),
    {},
)

_P = ParamSpec("_P")
_R = TypeVar("_R")


class _BaseAlgorithm(ABC, metaclass=AbstractAlgorithmDecoratorMetaClass):  # type: ignore[misc] # Reason: see above # noqa: E501
    """Blueprint for either the modeller side or the worker side of BaseAlgorithm."""

    def __init__(self, **kwargs: Any):
        super().__init__()
        self.class_name = module_registry.get(self.__class__.__module__, "")

    @abstractmethod
    def run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Runs the algorithm."""
        ...


class BaseModellerAlgorithm(_BaseAlgorithm, ABC):
    """Modeller side of the algorithm."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @abstractmethod
    def initialise(self, task_id: Optional[str], **kwargs: Any) -> None:
        """Initialise the algorithm."""
        raise NotImplementedError


class NoResultsModellerAlgorithm(BaseModellerAlgorithm):
    """Modeller side of any algorithm that does not return any results.

    Args:
        log_message: A message to log when the algorithm is
            run on the modeller side.
        save_path: The path the worker results should be saved to. This might be
            checked by the modeller if both modeller and worker are running on the
            same machine.
        **kwargs: Additional keyword arguments.
    """

    def __init__(
        self,
        log_message: Optional[str] = None,
        save_path: Optional[Union[os.PathLike, str]] = None,
        **kwargs: Any,
    ) -> None:
        self.log_message = log_message
        self.save_path = save_path
        super().__init__(**kwargs)

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Nothing to initialise here."""

    def run(self, results: Mapping[str, Any]) -> None:
        """Modeller side just logs the log message."""
        if self.log_message:
            logger.info(self.log_message)


class ResultsOnlyModellerAlgorithm(BaseModellerAlgorithm):
    """Modeller side of any algorithm that only returns results."""

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Nothing to initialise here."""

    def run(self, results: Mapping[str, Any]) -> dict[str, Any]:
        """Modeller side just returns the results as a dictionary."""
        return dict(results)


class BaseWorkerAlgorithm(_BaseAlgorithm, ABC):
    """Worker side of the algorithm."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _apply_pod_dp(self, pod_dp: Optional[DPPodConfig]) -> None:
        """Applies pod-level Differential Privacy constraints.

        Subclasses should override this method if DP is supported.

        Args:
            pod_dp: The pod DP constraints to apply or None if no constraints.
        """
        pass

    @abstractmethod
    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm.

        This method is only called once regardless of the number of batches in the task.

        :::note

        This method must call the `initialise_data` method.

        :::

        """
        raise NotImplementedError

    def initialise_data(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> None:
        """Initialises the algorithm with data.

        This method will be called once per task batch. It is expected that algorithms
        will override this method to initialise their data in the required way.

        :::note

        This is called by the `initialise` method and should not be called directly by
        the algorithm or protocol.

        :::
        """
        self.datasource = datasource
        self.data_splitter = data_splitter


# The mutable underlying dict that holds the registry information
_registry: dict[str, type[BaseAlgorithmFactory]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, type[BaseAlgorithmFactory]] = MappingProxyType(_registry)

# The mutable underlying dict that holds the mapping of module name to class name
_module_registry: dict[str, str] = {}
# The read-only version of the module registry that is allowed to be imported
module_registry: Mapping[str, str] = MappingProxyType(_module_registry)

T_ModellerSide = TypeVar("T_ModellerSide", bound=BaseModellerAlgorithm)
T_WorkerSide = TypeVar("T_WorkerSide", bound=BaseWorkerAlgorithm)


class BaseAlgorithmFactory(
    ABC,
    _RolesMixIn,
    _BaseSerializableObjectMixIn,
    Generic[T_ModellerSide, T_WorkerSide],
):
    """Base algorithm factory from which all other algorithms must inherit.

    Attributes:
       class_name: The name of the algorithm class.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}
    _inference_algorithm = True

    def __init__(self, **kwargs: Any):
        try:
            self.class_name = AlgorithmType[type(self).__name__].value
        except KeyError:
            # Check if the algorithm is a plug-in
            self.class_name = type(self).__name__
        super().__init__(**kwargs)

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to Algorithm registry")
            _registry[cls.__name__] = cls
            _module_registry[cls.__module__] = cls.__name__
        else:
            # Add abstract classes to the registry (so they can be correctly used for
            # serialization field inheritance) but ensure they are stored differently
            # so they cannot be accidentally looked up by name
            abstract_cls_name = f"Abstract::{cls.__name__}"
            logger.debug(
                f"Adding abstract class {cls.__name__}: {cls} to Algorithm registry"
                f" as {abstract_cls_name}"
            )
            _registry[abstract_cls_name] = cls

    modeller: Callable[..., T_ModellerSide]
    worker: Callable[..., T_WorkerSide]


# This is only a temporary class to be used until the `BaseAlgorithmFactory` is
# updated to include the `datastructure` field. Currently only models take a
# `datastructure` field, but this will be updated in the future to include all
# algorithms as part of a broader refactoring of models.
class BaseNonModelAlgorithmFactory(
    BaseAlgorithmFactory[T_ModellerSide, T_WorkerSide], ABC
):
    """Base factory for algorithms not involving an underlying model.

    Args:
        datastructure: The data structure to use for the algorithm.
        **kwargs: Additional keyword arguments.

    Attributes:
        datastructure: The data structure to use for the algorithm.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"datastructure": datastructure_registry}

    def __init__(
        self,
        *,
        datastructure: DataStructure,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.datastructure = datastructure

    @abstractmethod
    def modeller(self, **kwargs: Any) -> T_ModellerSide:
        """Modeller-side of the algorithm."""
        ...

    @abstractmethod
    def worker(self, **kwargs: Any) -> T_WorkerSide:
        """Worker-side of the algorithm."""
        ...


@runtime_checkable
class InitialSetupAlgorithm(Protocol):
    """Protocol defining the interface for algorithms that perform initial setup.

    Any algorithm used with InitialSetupProtocol must implement this interface.
    """

    def setup_run(self, **kwargs: Any) -> None:
        """Run setup operations before batching begins.

        This method will be called by protocols tagged with InitialSetupProtocol
        before any batching occurs.
        """
        ...


class BaseInitialSetupAlgorithm(BaseWorkerAlgorithm, ABC):
    """Base class for algorithms that perform initial setup.

    Provides a common base implementation for algorithms that need to run
    setup operations before batching begins.
    """

    @abstractmethod
    def setup_run(self, **kwargs: Any) -> None:
        """Run setup operations before batching begins.

        This method will be called by protocols tagged with InitialSetupProtocol
        before any batching occurs.
        """
        pass


class FinalStepAlgorithm:
    """Tagging interface for algorithms that contain a final "reduce" step.

    These algorithms have steps that can be operated batch-wise (normal run())
    followed by step(s) at the end that cannot be executed batch-wise but
    instead require access to outputs from all batch steps (reduce step(s)).
    """

    @abstractmethod
    def run_final_step(self, **kwargs: Any) -> Any:
        """Execute the final step without datasource access.

        This method is called after all batch processing is complete and
        should not access the datasource directly.

        Args:
            **kwargs: Additional context like accumulated results, task_id, etc.

        Returns:
            Final processed results
        """
        ...
