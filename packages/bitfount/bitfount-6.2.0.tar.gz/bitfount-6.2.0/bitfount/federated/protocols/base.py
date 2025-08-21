"""Pod communication protocols.

These classes take an algorithm and are responsible for organising the communication
between Pods and Modeller.

Attributes:
    registry: A read-only dictionary of protocol factory names to their
        implementation classes.

Current message flow between the workers with 2 batches
 and modeller for streaming batched execution:

    1. Workers send `NUM_BATCHES`=-1 to Modeller.
    2. Workers send `CURRENT_BATCH_ID`=1 to Modeller.
    3. Modeller states it's processing batch 1, Worker send a `TASK_START` to Modeller.
    4. Modeller waits for all Pods to be ready.
    5. Modeller sends `TASK_START` to Worker.
    6. Workers run batch 1.
    7. Workers send `EVALUATION_RESULTS` to Modeller.
    8. Workers send `CURRENT_BATCH_ID`=2 to Modeller.
    9. Workers run batch 2 (final), Modeller states it's processing batch 2.
    10. Workers send `EVALUATION_RESULTS` to Modeller.
    11. Workers send `BATCHES_COMPLETE("BATCHES_ONLY")` to Modeller.
    12. Worker runs resilience phase [if enabled]
    13. Workers send BATCHES_COMPLETE("TASK_COMPLETE") to Modeller,
        modeller exits streaming loop.
    14. Modeller sends `TASK_COMPLETE` to Workers.

Batched execution is currently only supported for single worker cases, but for
future reference, in the case where multiple workers are expected to execute
the current task, the modeller will choose to display to the user the current
batch id corresponding to the slowest user.
"""

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
import asyncio
from collections.abc import Callable, Collection, Mapping, Sequence
from datetime import datetime
from functools import wraps
import inspect
import os
from pathlib import Path
import types
from types import FunctionType, MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    NamedTuple,
    NoReturn,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from marshmallow import fields

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasplitters import (
    DatasetSplitter,
    PercentageSplitter,
    SplitterDefinedInData,
)
from bitfount.data.types import DataSplit
from bitfount.externals.general.authentication import ExternallyManagedJWT
import bitfount.federated.algorithms.base as algorithms
from bitfount.federated.algorithms.base import (
    FinalStepAlgorithm,
    InitialSetupAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithmFactory,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    _WorkerSide as ModelInferenceWorkerSideAlgorithm,
)
from bitfount.federated.authorisation_checkers import (
    IdentityVerificationMethod,
    InferenceLimits,
    ProtocolContext,
)
from bitfount.federated.background_file_counter import (
    get_background_file_count,
    start_background_file_counting,
    stop_background_file_counting,
)
from bitfount.federated.exceptions import (
    AlgorithmError,
    BitfountTaskStartError,
    NoDataError,
    NoNewDataError,
    ProtocolError,
    TaskAbortError,
)
from bitfount.federated.helper import (
    TaskContext,
    _check_and_update_pod_ids,
    _create_message_service,
    _get_idp_url,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.modeller import _Modeller
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.protocols.resilience import ResilienceHandler
from bitfount.federated.protocols.types import (
    BATCH_ID_RETRY_DELAY,
    MAXIMUM_RETRIES,
    MAXIMUM_SLEEP_TIME,
    BatchConfig,
    ProtocolState,
    TerminationReason,
)
from bitfount.federated.roles import _RolesMixIn
from bitfount.federated.transport.base_transport import _BaseMailbox
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.transport.message_service import (
    ResourceConsumed,
    ResourceType,
    _MessageService,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.types import Reason
from bitfount.federated.transport.utils import compute_backoff
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.federated.types import ProtocolType, SerializedProtocol
from bitfount.hooks import (
    _HOOK_DECORATED_ATTRIBUTE,
    BaseDecoratorMetaClass,
    HookType,
    get_hooks,
)
from bitfount.hub.helper import _default_bitfounthub
from bitfount.schemas.utils import bf_dump
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _StrAnyDict,
)

if TYPE_CHECKING:
    from bitfount.federated.pod_vitals import _PodVitals
    from bitfount.hub.api import BitfountHub
    from bitfount.hub.authentication_flow import BitfountSession


logger = _get_federated_logger(__name__)


class ProtocolDecoratorMetaClass(BaseDecoratorMetaClass, type):
    """Decorates the `__init__` and `run` protocol methods."""

    @staticmethod
    def decorator(f: Callable) -> Callable:
        """Hook decorator which logs before and after the hook it decorates."""
        method_name = f.__name__
        if method_name == "__init__":

            @wraps(f)
            def init_wrapper(
                self: _BaseProtocol,
                hook_kwargs: Optional[_StrAnyDict] = None,
                *args: Any,
                **kwargs: Any,
            ) -> None:
                """Wraps __init__ method of protocol.

                Calls relevant hooks before and after the protocol is initialised.

                Args:
                    self: The protocol instance.
                    hook_kwargs: Keyword arguments to pass to the hooks.
                    *args: Positional arguments to pass to the protocol.
                    **kwargs: Keyword arguments to pass to the protocol.
                """
                hook_kwargs = hook_kwargs or {}
                for hook in get_hooks(HookType.PROTOCOL):
                    hook.on_init_start(self, **hook_kwargs)
                logger.debug(f"Calling method {method_name} from protocol")
                f(self, *args, **kwargs)
                for hook in get_hooks(HookType.PROTOCOL):
                    hook.on_init_end(self, **hook_kwargs)

            return init_wrapper

        elif method_name == "run":

            @wraps(f)
            async def run_wrapper(
                self: _BaseProtocol,
                *,
                context: Optional[ProtocolContext] = None,
                batched_execution: Optional[bool] = None,
                hook_kwargs: Optional[_StrAnyDict] = None,
                processed_files_cache: Optional[dict[str, datetime]] = None,
                failed_files_cache: Optional[dict[str, dict[str, str]]] = None,
                test_run: bool = False,
                **kwargs: Any,
            ) -> Union[Any, list[Any]]:
                """Wraps run method of protocol.

                Calls hooks before and after the run method is called and also
                orchestrates batched execution if set to True.

                Args:
                   self: Protocol instance.
                   context: Context in which the protocol is being run. Only required
                       if batched_execution is True.
                   batched_execution: Whether to run the protocol in batched mode.
                   hook_kwargs: Keyword arguments to pass to the hooks.
                   processed_files_cache: Optional. A dictionary of processed file
                        names for the current task mapped to their last modified
                        dates. Defaults to None.
                   failed_files_cache: Optional. Dictionary of previously failed files
                        for the current task. Defaults to None
                   test_run: Whether this is a test run. Defaults to False.
                   **kwargs: Keyword arguments to pass to the run method.

                Returns:
                   Return value of the run method. Or a list of return values if
                   batched_execution is True.

                Raises:
                   BitfountTaskStartError: If batched_execution is True but the
                       datasource does not support batched execution.
                   AlgorithmError: This is caught and re-raised.
                   ProtocolError: Any error that is raised in the protocol run that
                       is not an AlgorithmError is raised as a ProtocolError.
                """
                executor = ProtocolExecution(
                    protocol=self,
                    run_method=f,
                    context=context,
                    batched_execution=batched_execution,
                    processed_files_cache=processed_files_cache,
                    failed_files_cache=failed_files_cache,
                    test_run=test_run,
                    hook_kwargs=hook_kwargs,
                    **kwargs,
                )

                return await executor.execute()

            return run_wrapper

        raise ValueError(f"Method {method_name} cannot be decorated.")

    @classmethod
    def do_decorate(cls, attr: str, value: Any) -> bool:
        """Checks if an object should be decorated.

        Only the __init__ and run methods should be decorated.
        """
        return (
            attr in ("__init__", "run")
            and isinstance(value, FunctionType)
            and getattr(value, _HOOK_DECORATED_ATTRIBUTE, True)
        )


MB = TypeVar("MB", bound=_BaseMailbox)

# The metaclass for the BaseProtocol must also have all the same classes in its own
# inheritance chain so we need to create a thin wrapper around it.
AbstractProtocolDecoratorMetaClass = types.new_class(
    "AbstractProtocolDecoratorMetaClass",
    (Generic[MB], ABCMeta, ProtocolDecoratorMetaClass),
    {},
)


class ProtocolExecution:
    """Handles protocol execution with proper context management.

    Args:
        protocol: The protocol instance to run.
        run_method: The method to execute on the protocol.
        context: Optional. The context in which the protocol is being run.
        batched_execution: Whether to run the protocol in batched mode.
        hook_kwargs: Optional. Keyword arguments to pass to the hooks.
        processed_files_cache: Optional. A dictionary of processed files
            with their last modified dates. Defaults to None.
        failed_files_cache: Optional. A dictionary of previously failed
            files for the current task run. Defaults to None.
        test_run: Whether this is a test run. Defaults to False.
        **kwargs: Additional keyword arguments for the run method.
    """

    def __init__(
        self,
        protocol: _BaseProtocol,
        run_method: Callable,
        context: Optional[ProtocolContext],
        batched_execution: Optional[bool],
        hook_kwargs: Optional[_StrAnyDict],
        processed_files_cache: Optional[dict[str, datetime]] = None,
        failed_files_cache: Optional[dict[str, dict[str, str]]] = None,
        test_run: bool = False,
        **kwargs: Any,
    ):
        self.protocol = protocol
        self.run_method = run_method
        self.context = context
        self.task_context = context.task_context if context else None
        self.batched_execution = (
            config.settings.default_batched_execution
            if batched_execution is None
            else batched_execution
        )
        self.processed_files_cache = processed_files_cache
        self.failed_files_cache = failed_files_cache or {}
        self.test_run = test_run
        self.background_file_counting = (
            config.settings.background_file_counting if not test_run else False
        )

        # Check for context when batched execution is enabled
        if self.batched_execution and not context:
            raise BitfountTaskStartError(
                "Context must be provided for batched execution."
            )

        self.hook_kwargs = hook_kwargs or {}
        self.hook_kwargs["context"] = self.task_context
        self.kwargs = kwargs

    async def execute(self) -> Union[Any, list[Any]]:
        """Main execution entry point."""
        try:
            if self.task_context == TaskContext.WORKER:
                return await self._execute_worker()
            elif self.task_context == TaskContext.MODELLER:
                return await self._execute_modeller()
            else:
                return await self._run_single()
        except BitfountTaskStartError:
            raise
        except NoNewDataError:
            logger.error(
                "No new data available for the task. "
                "Please check the datasource and try again."
            )
            raise
        except Exception as e:
            logger.exception(e)
            raise

    async def _execute_worker(self) -> Union[Any, list[Any]]:
        """Handles worker-side execution."""
        protocol = cast(BaseWorkerProtocol, self.protocol)
        datasource = self._validate_worker_datasource(protocol)
        batch_config: Optional[BatchConfig] = None
        try:
            if not isinstance(datasource, FileSystemIterableSource):
                logger.warning(
                    "Batched execution not compatible with non-iterable sources. "
                    "Running in non-batched mode."
                )
                self.batched_execution = False

            # Apply any initial setup needed
            if isinstance(protocol, InitialSetupProtocol):
                if isinstance(datasource, FileSystemIterableSource):
                    self._perform_initial_setup(datasource, protocol)
                else:
                    logger.warning(
                        f"Protocol contains initial setup steps"
                        f" but the selected datasource type,"
                        f" {type(datasource).__name__},"
                        f" is not supported for this."
                    )

            if not self.batched_execution:
                if self.test_run:
                    self.test_run = False
                    logger.warning("Test run is not supported in non-batched mode.")
                # Inform modeller we're running in non-batched mode
                await protocol.mailbox.send_num_batches_message(1)
                return await self._run_single()

            batch_config = self._setup_worker_batches(
                protocol=protocol, datasource=datasource
            )

            if (
                isinstance(datasource, FileSystemIterableSource)
                and self.background_file_counting is not False
            ):
                start_background_file_counting(datasource)
                logger.info(
                    "Started background file counting with batch count updates..."
                )

            # Signal batches coming in by streaming by sending -1 as num_batches
            await protocol.mailbox.send_num_batches_message(-1)
            return await self._run_worker_batches(protocol, batch_config)

        except NoNewDataError:
            raise
        finally:
            # Stop background counting when done
            if (
                isinstance(datasource, FileSystemIterableSource)
                and self.background_file_counting is not False
            ):
                stop_background_file_counting(datasource)
            self._restore_worker_datasource(
                datasource=datasource, batch_config=batch_config
            )

    async def _execute_modeller(self) -> Union[Any, list[Any]]:
        """Handles modeller-side execution."""
        mailbox = cast(_ModellerMailbox, self.protocol.mailbox)
        # Always wait for batch information from worker at the
        # start of the task
        num_batches = await mailbox.get_num_batches_message()
        logger.debug(f"Modeller received num_batches: {num_batches}")
        if not self.batched_execution or num_batches == 1:
            logger.debug("Modeller: Running in non-batched mode")
            result = await self._run_single()
        elif num_batches == -1:
            logger.debug("Modeller: Running in streaming mode")
            # In streaming mode, we don't know the number of batches upfront.
            # We will run batches until the worker signals completion.
            result = await self._run_modeller_streaming_batches()
        else:
            logger.error(
                "Modeller and worker are incompatible. "
                "Please ensure that they are both running the same bitfount version."
            )
            raise BitfountTaskStartError(
                "Modeller and worker are incompatible. "
                "Please ensure that they are both running the same bitfount version."
            )
        return result

    async def _run_single(self) -> Any:
        """Executes a single non-batched run."""
        await self._ensure_parties_ready()

        if self.task_context == TaskContext.WORKER:
            self._load_new_data_for_single_batch()

        for hook in get_hooks(HookType.PROTOCOL):
            hook.on_run_start(self.protocol, **self.hook_kwargs)

        try:
            protocol_state = ProtocolState()
            protocol_state.execute_final_step = True
            protocol_state.termination_reason = TerminationReason.SINGLE_BATCH
            return_val = await self._execute_run(
                final_batch=False, protocol_state=protocol_state
            )

            final_result = await self._execute_final_steps(
                cast(BaseWorkerProtocol, self.protocol), protocol_state=protocol_state
            )
            self.hook_kwargs["results"] = final_result

            for hook in get_hooks(HookType.PROTOCOL):
                hook.on_run_end(self.protocol, **self.hook_kwargs)

            return return_val
        except (AlgorithmError, TaskAbortError):
            raise
        except Exception as e:
            raise ProtocolError(
                f"Protocol {self.protocol.__class__.__name__} "
                f"raised the following exception: {e}"
            ) from e

    def _perform_initial_setup(
        self,
        datasource: FileSystemIterableSource,
        protocol: BaseWorkerProtocol,
    ) -> None:
        """Perform initial setup methods if the protocol needs them."""
        # If there is initial setup that needs to occur prior to batching (filtering,
        # grouping, etc.) then perform this first.
        # This will set selected_file_names_override if needed.
        if isinstance(protocol, InitialSetupProtocol):
            logger.info("Running protocol initial setup before batching.")
            protocol.run_initial_setup()

            if len(datasource.selected_file_names_override) == 0:
                # If initial setup is run and selected_file_names_override is empty
                # then we have no data to work with.
                raise NoDataError("Dataset is empty. Aborting task.")

            logger.info("Protocol initial setup complete.")

    async def _execute_final_steps(
        self, protocol: BaseWorkerProtocol, protocol_state: ProtocolState
    ) -> Any:
        """Execute final steps at protocol level."""
        result = None
        # Only execute protocol-level final reduce step
        # The protocol itself manages its algorithms
        if isinstance(protocol, FinalStepProtocol):
            logger.info("Executing protocol final step")
            result = await protocol.run_final_step(
                self.context, **(protocol_state.reduce_step_kwargs or {})
            )
        else:
            logger.debug(
                "Protocol does not implement FinalStepProtocol - no final step"
            )

        return result

    def _load_new_data_for_single_batch(self) -> None:
        """Loads new data only for a single batch run."""
        if self.processed_files_cache is not None:
            run_records_filenames = list(self.processed_files_cache)
            if (
                not hasattr(self.protocol, "datasource")
                or not self.protocol.datasource
                or not hasattr(self.protocol, "data_splitter")
            ):
                raise BitfountTaskStartError(
                    "Protocol has not been initialised with a datasource."
                )

            if isinstance(self.protocol.data_splitter, SplitterDefinedInData):
                datasource_file_names = self.protocol.data_splitter.get_filenames(
                    self.protocol.datasource, split=DataSplit.TEST
                )
            else:
                # This filenames iteration is fine here as it
                # is used only for non-batched execution.
                datasource_file_names = list(self.protocol.datasource.file_names_iter())
            new_records = [
                # [non_iterable_file_names]
                i
                for i in datasource_file_names
                if str(i) not in run_records_filenames
            ]
            for run_record in run_records_filenames:
                # Check if the file is still present in the datasource
                # [non_iterable_file_names]
                if run_record in datasource_file_names:
                    original_last_modified = self.processed_files_cache[run_record]
                    new_last_modified = datetime.fromtimestamp(
                        os.path.getmtime(run_record)
                    )
                    # Check if the file has been modified since the last run
                    if new_last_modified > original_last_modified:
                        logger.debug(
                            f"File {run_record} has been modified since last run. "
                            f"Adding to new records."
                        )
                        new_records.append(run_record)
            new_records_set = set(new_records)
            if len(new_records) == 0:
                msg = "No new data available. Aborting task."
                logger.info(msg)
                raise NoNewDataError(msg)
            if len(new_records_set) != len(new_records):
                logger.warning(
                    "There are duplicate filenames in the new records. "
                    "These have been removed but this may indicate an issue."
                )

            logger.info(
                f"Found {len(new_records_set)} new record(s) to run the task on."
            )
            # We explicitly only set the file names that are new, ignoring any other
            # data in new_records
            self.protocol.datasource.new_file_names_only_set = new_records_set

    def _validate_worker_datasource(self, protocol: BaseWorkerProtocol) -> BaseSource:
        """Validates and returns the worker datasource.

        Args:
            protocol: The worker protocol instance.

        Raises:
            BitfountTaskStartError: If the protocol has not been initialised with a
                datasource or if the datasource is not a FileSystemIterableSource.

        Returns:
           The datasource to use for the worker.
        """
        try:
            datasource = protocol.datasource
        except Exception as e:
            raise BitfountTaskStartError(
                "Protocol has not been initialised with a datasource."
            ) from e
        return datasource

    def _get_data_splitter(self, protocol: BaseWorkerProtocol) -> DatasetSplitter:
        """Gets the data splitter, using default if none set.

        Args:
            protocol: The worker protocol instance.

        Returns:
            The data splitter to use for the protocol.
        """
        try:
            data_splitter = (
                protocol.data_splitter
                if protocol.data_splitter is not None
                else PercentageSplitter(iterative_splitting=True)
            )
        except Exception:
            logger.warning(
                "Protocol has not been initialised with "
                "a data splitter. Using default PercentageSplitter."
            )
            data_splitter = PercentageSplitter(iterative_splitting=True)
        return data_splitter

    def _setup_worker_batches(
        self,
        datasource: BaseSource,
        protocol: BaseWorkerProtocol,
    ) -> BatchConfig:
        """Sets up batch configuration for worker execution.

        Args:
            datasource: The worker datasource to use.
            protocol: The worker protocol instance.

        Returns:
            The batch configuration for the worker.
        """
        if not isinstance(datasource, FileSystemIterableSource):
            raise BitfountTaskStartError(
                "Batched execution is not supported for non-filesystem "
                "iterable sources."
            )

        # Get the data splitter, don't retrieve all files upfront
        data_splitter = self._get_data_splitter(protocol)
        if self.test_run:
            batch_size = config.settings.test_run_number_of_files
        else:
            batch_size = config.settings.task_batch_size

        return BatchConfig(
            batch_size=batch_size,
            data_splitter=data_splitter,
            datasource=datasource,
            original_file_names_override=datasource.selected_file_names_override.copy(),
        )

    def _prepare_worker_batch(
        self,
        batch_config: BatchConfig,
        protocol: BaseWorkerProtocol,
    ) -> bool:
        """Prepares the worker datasource for the current batch.

        Args:
            batch_config: The batch configuration for the worker.
            protocol: The worker protocol instance.

        Returns:
            True if the batch was prepared successfully, False if no more batches
        """
        # If this was already marked as the final batch, don't try to prepare more
        if batch_config.is_final_batch:
            return False

        # Collect files for this batch using the iterator
        current_batch_files: list[str] = []
        try:
            while len(current_batch_files) < batch_config.batch_size:
                filename = next(batch_config.current_files_iterator)
                batch_config.total_files_checked += 1

                # Filter for new data if cache is not None
                if self.processed_files_cache is not None:
                    if self._is_file_new_from_cache(filename):
                        batch_config.has_new_files = (
                            True  # Mark that we found new files
                        )
                        current_batch_files.append(filename)
                    # If not new, skip this file (don't add to current_batch_files)
                else:
                    current_batch_files.append(filename)
        except StopIteration:
            if not current_batch_files:
                # This can happen if there are no files in the test set
                return False
            else:
                # This is the final batch with fewer files than batch_size
                batch_config.is_final_batch = True

        # If we collected a full batch, check if there are more files
        if (
            len(current_batch_files) == batch_config.batch_size
            and not batch_config.is_final_batch
        ):
            try:
                batch_config.current_files_iterator.peek()
            except StopIteration:
                batch_config.is_final_batch = True

        # Store the current batch files
        batch_config.current_batch_files = current_batch_files

        # Update datasource with current batch of files
        datasource = cast(FileSystemIterableSource, protocol.datasource)
        datasource.selected_file_names_override = current_batch_files
        # Reinitialize algorithms with updated datasource
        data_splitter = self._get_data_splitter(protocol)
        for algo in protocol.algorithms:
            algo.initialise_data(datasource=datasource, data_splitter=data_splitter)

        # Increment the batch counter
        batch_config.current_batch += 1

        return True

    def _restore_worker_datasource(
        self,
        datasource: BaseSource,
        batch_config: Optional[BatchConfig] = None,
    ) -> None:
        """Restores the worker datasource to its original state.

        Args:
            datasource: The worker datasource to restore.
            batch_config: Optional. The batch configuration used for the run.
        """
        if (
            isinstance(datasource, FileSystemIterableSource)
            and batch_config is not None
        ):
            datasource.selected_file_names_override = (
                batch_config.original_file_names_override or []
            )

    async def _run_worker_batches(
        self, protocol: BaseWorkerProtocol, batch_config: BatchConfig
    ) -> list[Any]:
        """Executes all batches for worker context.

        Args:
            protocol: The worker protocol instance.
            batch_config: The batch configuration for the worker.
        """
        return_values = []
        is_last_batch = False
        total_count = None
        datasource = cast(FileSystemIterableSource, protocol.datasource)
        # Initialize batch context
        protocol_state = ProtocolState()
        # Create resilience handler
        resilience_handler = ResilienceHandler(
            protocol=protocol,
            hook_kwargs=self.hook_kwargs,
            execute_run_func=self._execute_run,
        )
        try:
            # Check if we have any new files when run_on_new_data_only is enabled
            if self.processed_files_cache is not None:
                batch_config.has_new_files = False  # Track if any new files are found
            # Process batches in streaming mode until there are no more batches or
            # until flag to execute final step is received
            while not is_last_batch and not protocol_state.execute_final_step:
                batch_prepared = self._prepare_worker_batch(
                    batch_config=batch_config,
                    protocol=protocol,
                )
                # If run_on_new_data_only is enabled and no new files found, abort
                if (
                    self.processed_files_cache is not None
                    and not batch_config.has_new_files
                ):
                    msg = "No new data found after checking files. Aborting task."
                    logger.info(msg)
                    await protocol.mailbox.send_task_abort_message(
                        "No new data available. Aborting task.", Reason.NO_NEW_DATA
                    )
                    raise NoNewDataError(msg)
                if not batch_prepared:
                    break

                # Get current batch number
                batch_num = (
                    batch_config.current_batch - 1
                )  # -1 because we already incremented

                # Send the current batch ID to the modeller
                await protocol.mailbox.send_current_batch_id_message(batch_num)
                if self.test_run:
                    is_last_batch = True  # In test run, we only run one batch
                else:
                    # Check if this is the final batch
                    is_last_batch = batch_config.is_final_batch

                total_count = get_background_file_count(datasource)
                estimated_batches = None

                if total_count is not None:
                    estimated_batches = (
                        total_count + batch_config.batch_size - 1
                    ) // batch_config.batch_size
                    logger.info(f"Estimated total batches: {estimated_batches}")
                    if not batch_config._sent_batch_count_update:
                        await protocol.mailbox.send_num_batches_message(
                            estimated_batches
                        )
                        batch_config._sent_batch_count_update = True
                # Run the batch with resilience handling
                try:
                    return_val = await self._run_batch(
                        batch_num=batch_num,
                        is_final=False,
                        total_batches=estimated_batches,
                        protocol_state=protocol_state,
                    )
                    # Success - reset consecutive failures and track success
                    batch_config.consecutive_failures = 0
                    batch_config.successful_batches.append(batch_num)
                    return_values.append(return_val)
                except TaskAbortError as abort_error:
                    if (
                        hasattr(abort_error, "reason")
                        and abort_error.reason == Reason.LIMITS_EXCEEDED
                    ):
                        logger.error(
                            f"Task aborted due to limits exceeded: {abort_error}"
                        )
                        raise  # Always abort for limits exceeded
                    else:
                        await resilience_handler.handle_batch_failure(
                            abort_error, batch_num, batch_config
                        )
                except (ProtocolError, AlgorithmError, Exception) as e:
                    await resilience_handler.handle_batch_failure(
                        e, batch_num, batch_config
                    )
            await protocol.mailbox.send_batches_complete_message("BATCHES_ONLY")

            for hook in get_hooks(HookType.POD):
                hook.on_batches_complete(
                    task_id=getattr(protocol.mailbox, "task_id", None),
                    modeller_username=getattr(protocol.mailbox, "modeller_name", ""),
                    total_batches=len(return_values),
                    total_files=batch_config.total_files_checked,
                )
            await resilience_handler.handle_batch_resilience_and_reporting(batch_config)

            # After the main run, execute final reduce step.
            logger.info("Starting final reduce phase if it exists")
            await self._execute_final_steps(protocol, protocol_state)

            # Signal to the modeller that all batches are complete including resilience
            await protocol.mailbox.send_batches_complete_message("TASK_COMPLETE")

            if total_count is not None:
                logger.info(
                    f"Task completed: processed {len(return_values)} batches "
                    f"with {total_count} total files"
                )

            return return_values
        except NoNewDataError:
            # When NoNewDataError occurs, we've already sent the task abort message
            # Don't execute any completion logic, just re-raise
            logger.debug("NoNewDataError occurred, skipping completion logic")
            raise

    async def _run_modeller_streaming_batches(self) -> list[Any]:
        """Executes modeller-side batches in streaming mode."""
        return_values = []
        mailbox = cast(_ModellerMailbox, self.protocol.mailbox)

        # Process regular batches until all workers have finished batches
        while (
            not mailbox.all_workers_batch_complete
            and not mailbox.batches_complete_received
            and not mailbox.abort
        ):
            try:
                # Get the current batch ID from any worker
                batch_num = await mailbox.get_current_batch_id_message()

                if batch_num == -1:
                    logger.debug("Worker signaled completion with batch_num = -1")
                    continue  # Other workers might still be sending batch IDs

                if batch_num is None:
                    raise ValueError("No current batch ID messages received.")

                # Get total batches for centralized logging
                total_batches = mailbox._current_total_batches

                # Run the batch
                return_val = await self._run_batch(
                    batch_num=batch_num,
                    is_final=False,
                    total_batches=total_batches,
                )
                return_values.append(return_val)

            except Exception as e:
                logger.debug(f"Error getting batch ID: {e}")
                # If no more batch IDs available, check completion states
                if (
                    getattr(mailbox, "all_workers_batch_complete", False)
                    or mailbox.batches_complete_received
                    or mailbox.abort
                ):
                    break
                else:
                    # Wait a bit and try again
                    await asyncio.sleep(BATCH_ID_RETRY_DELAY)
                    continue
        # Check if task was aborted and raise the error
        if mailbox.abort:
            error_message, reason = mailbox.abort
            raise TaskAbortError(error_message, reason)
        # Handle resilience phase - continue until all workers complete
        if mailbox.any_worker_in_resilience and not mailbox.batches_complete_received:
            logger.info("Entering resilience phase...")
            resilience_results = await self._handle_resilience_phase()
            return_values.extend(resilience_results)

        logger.info(f"Completed {len(return_values)} batches total")
        return return_values

    async def _handle_resilience_phase(self) -> list[Any]:
        """Handle evaluation results during the resilience phase.

        Continues processing evaluation results from workers in resilience
        until all workers send BATCHES_COMPLETE("TASK_COMPLETE").
        """
        resilience_results = []
        mailbox = cast(_ModellerMailbox, self.protocol.mailbox)

        logger.info(
            f"Resilience phase: {len(mailbox.workers_in_resilience)} "
            f"workers in resilience"
        )

        # Continue processing while any worker is in resilience
        while (
            mailbox.any_worker_in_resilience
            and not mailbox.batches_complete_received
            and not mailbox.abort
        ):
            try:
                # Run protocol to receive evaluation results from resilience processing
                return_val = await self._execute_run(final_batch=False)

                if return_val is not None:
                    resilience_results.append(return_val)
                    logger.debug("Processed resilience results from worker recovery")

            except Exception as e:
                logger.debug(f"Error during resilience phase: {e}")
                await asyncio.sleep(0.1)  # Small delay
                continue
        # Check if task was aborted during resilience
        if mailbox.abort:
            error_message, reason = mailbox.abort
            raise TaskAbortError(error_message, reason)
        logger.info(
            f"Resilience phase complete. Processed "
            f"{len(resilience_results)} additional results."
        )
        return resilience_results

    async def _ensure_parties_ready(self) -> None:
        """Ensures all parties are ready before proceeding."""
        retry_count = 0
        await self.protocol.mailbox.send_task_start_message()

        if self.task_context == TaskContext.WORKER:
            mailbox = cast(_WorkerMailbox, self.protocol.mailbox)
            while not mailbox.modeller_ready:
                retry_count += 1
                if retry_count >= MAXIMUM_RETRIES:
                    raise BitfountTaskStartError(
                        "Timed out while waiting for modeller to be ready"
                    )
                await asyncio.sleep(
                    compute_backoff(retry_count, max_backoff=MAXIMUM_SLEEP_TIME)
                )
                logger.info("Waiting for modeller to be ready...")
            logger.info("Modeller is ready. Starting task...")

        elif self.task_context == TaskContext.MODELLER:
            modeller_mailbox = cast(_ModellerMailbox, self.protocol.mailbox)
            while not modeller_mailbox.pods_ready and modeller_mailbox.abort is None:
                retry_count += 1
                await asyncio.sleep(
                    compute_backoff(retry_count, max_backoff=MAXIMUM_SLEEP_TIME)
                )
                logger.info("Waiting for pod(s) to be ready...")
            if modeller_mailbox.abort is not None:
                error_message, reason = modeller_mailbox.abort
                logger.error(error_message)
                raise TaskAbortError(error_message, reason)
            logger.info("Pod(s) are ready. Starting task...")

    async def _run_batch(
        self,
        batch_num: int,
        is_final: bool = False,
        total_batches: Optional[int] = None,
        protocol_state: Optional[ProtocolState] = None,
    ) -> Any:
        """Executes a single batch with proper hook handling.

        Args:
            batch_num: Current batch number (0-indexed)
            is_final: Whether this is the final batch
            total_batches: Total number of batches (if known)
            protocol_state: The current protocol state object
        """
        # Centralized batch logging with progress information
        if total_batches is not None:
            logger.info(f"Running batch {batch_num + 1} out of {total_batches}")
        elif self.background_file_counting:
            logger.info(f"Running batch {batch_num + 1} (total count pending...)")
        else:
            logger.info(f"Running batch {batch_num + 1} (total batches unknown)")
        hook_kwargs = self.hook_kwargs.copy()
        hook_kwargs.update(
            {
                "batch_num": batch_num,
                "total_batches": total_batches,
                "protocol_state": protocol_state,
            }
        )

        for hook in get_hooks(HookType.PROTOCOL):
            hook.on_run_start(self.protocol, **hook_kwargs)

        if batch_num == 0:
            await self._ensure_parties_ready()

        return_val = await self._execute_run(
            batch_num=batch_num, final_batch=is_final, protocol_state=protocol_state
        )
        hook_kwargs["results"] = return_val
        for hook in get_hooks(HookType.PROTOCOL):
            hook.on_run_end(self.protocol, **hook_kwargs)

        return return_val

    async def _execute_run(
        self,
        batch_num: Optional[int] = None,
        final_batch: bool = False,
        protocol_state: Optional[ProtocolState] = None,
    ) -> Any:
        """Executes the actual run method with error handling."""
        try:
            return await self.run_method(
                self.protocol,
                context=self.context,
                batch_num=batch_num,
                final_batch=final_batch,
                protocol_state=protocol_state,
                **self.kwargs,
            )
        except (AlgorithmError, TaskAbortError):
            raise
        except Exception as e:
            raise ProtocolError(
                f"Protocol {self.protocol.__class__.__name__} "
                f"raised the following exception: {e}"
            ) from e

    def _is_file_new_from_cache(
        self,
        filename: str,
    ) -> bool:
        """Check if a file is new using the cached processed files info.

        Args:
            filename: The filename to check

        Returns:
            True if the file is new or has been modified, False otherwise
        """
        if self.processed_files_cache is not None:
            if filename not in self.processed_files_cache:
                # File hasn't been processed before
                # But check if it previously failed
                if self._is_file_previously_failed(filename):
                    # File previously failed - skip it
                    return False
                # File hasn't been processed before
                return True

            try:
                # Check if file has been modified since last processing
                stored_last_modified = self.processed_files_cache[filename]
                current_last_modified = datetime.fromtimestamp(
                    os.path.getmtime(filename)
                )

                if current_last_modified > stored_last_modified:
                    logger.debug(
                        f"File {filename} has been modified since last run. "
                        f"Including in batch."
                    )
                    return True

                return False

            except Exception:
                # If there's any error checking file modification time,
                # include the file to be safe
                logger.warning(
                    f"Error checking modification time for {filename}. Treating as new."
                )
                if self._is_file_previously_failed(filename):
                    return False
                return True
        else:
            # No processed files cache - check failed files cache
            if self._is_file_previously_failed(filename):
                return False

            # We should not end up in this branch if the protocol is set up correctly,
            # but **if** we do, log error and treat all files as new.
            logger.error(
                "No processed files cache provided. Treating all files as new."
            )
            return True

    def _is_file_previously_failed(self, filename: str) -> bool:
        """Check if a file has previously failed.

        Args:
            filename: The filename to check

        Returns:
            True if the file previously failed and should be skipped
        """
        if not self.failed_files_cache:
            return False

        if filename not in self.failed_files_cache:
            return False

        # Check if file has been modified since it failed
        try:
            failure_info = self.failed_files_cache[filename]
            if failure_info.get("last_modified"):
                failed_last_modified = datetime.fromisoformat(
                    failure_info["last_modified"]
                )
                current_last_modified = datetime.fromtimestamp(
                    os.path.getmtime(filename)
                )

                if current_last_modified > failed_last_modified:
                    logger.debug(
                        f"File {filename} has been modified since it last failed. "
                        f"Including in processing."
                    )
                    return False
        except Exception as e:
            logger.warning(
                f"Error checking failed file modification time for {filename}: {e}"
            )
        return True


T_AlgoType = TypeVar("T_AlgoType")


# Mypy doesn't yet support metaclasses with generics
class _BaseProtocol(
    Generic[MB, T_AlgoType],
    ABC,
    metaclass=AbstractProtocolDecoratorMetaClass,  # type: ignore[misc] # Reason: see above # noqa: E501
):
    """Blueprint for modeller side or the worker side of BaseProtocolFactory."""

    def __init__(
        self,
        *,
        algorithm: Union[
            T_AlgoType,
            Sequence[T_AlgoType],
        ],
        mailbox: MB,
        **kwargs: Any,
    ):
        self.algorithm = algorithm
        self.mailbox = mailbox
        self.class_name = module_registry.get(self.__class__.__module__, "")

        super().__init__(**kwargs)

    @property
    def algorithms(
        self,
    ) -> list[T_AlgoType]:
        """Returns the algorithms in the protocol."""
        if isinstance(self.algorithm, Sequence):
            return list(self.algorithm)
        return [self.algorithm]


class BaseCompatibleModellerAlgorithm(Protocol):
    """Protocol defining base modeller-side algorithm compatibility."""

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm."""
        pass


class BaseModellerProtocol(
    _BaseProtocol[_ModellerMailbox, BaseCompatibleModellerAlgorithm], ABC
):
    """Modeller side of the protocol.

    Calls the modeller side of the algorithm.
    """

    def __init__(
        self,
        *,
        algorithm: Union[
            BaseCompatibleModellerAlgorithm, Sequence[BaseCompatibleModellerAlgorithm]
        ],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    def initialise(
        self,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the component algorithms."""
        for algo in self.algorithms:
            algo.initialise(
                task_id=task_id,
                **kwargs,
            )

    @abstractmethod
    async def run(
        self, *, context: Optional[ProtocolContext] = None, **kwargs: Any
    ) -> Any:
        """Runs Modeller side of the protocol.

        Args:
            context: Optional. Run-time context for the protocol.
            **kwargs: Additional keyword arguments.
        """
        pass


class BaseCompatibleWorkerAlgorithm(Protocol):
    """Protocol defining base worker-side algorithm compatibility."""

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the algorithm."""
        pass

    def initialise_data(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> None:
        """Initialises the data for the algorithm."""
        pass


class BaseWorkerProtocol(
    _BaseProtocol[_WorkerMailbox, BaseCompatibleWorkerAlgorithm], ABC
):
    """Worker side of the protocol.

    Calls the worker side of the algorithm.
    """

    datasource: BaseSource
    mailbox: _WorkerMailbox
    project_id: Optional[str]

    def __init__(
        self,
        *,
        algorithm: Union[
            BaseCompatibleWorkerAlgorithm, Sequence[BaseCompatibleWorkerAlgorithm]
        ],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        project_id: Optional[str] = None,
        ehr_secrets: Optional[ExternallyManagedJWT] = None,
        parent_pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialises the component algorithms."""
        self.datasource = datasource
        self.data_splitter = data_splitter
        self.project_id = project_id
        self.parent_pod_identifier = parent_pod_identifier
        for algo in self.algorithms:
            algo.initialise(
                datasource=datasource,
                data_splitter=data_splitter,
                pod_dp=pod_dp,
                pod_identifier=pod_identifier,
                task_id=self.mailbox.task_id,
                ehr_secrets=ehr_secrets,
                **kwargs,
            )

    @abstractmethod
    async def run(
        self,
        *,
        pod_vitals: Optional[_PodVitals] = None,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> Any:
        """Runs the worker-side of the algorithm.

        Args:
            pod_vitals: Optional. Pod vitals instance for recording run-time details
                from the protocol run.
            context: Optional. Run-time context for the protocol.
            **kwargs: Additional keyword arguments.
        """
        pass


# The mutable underlying dict that holds the registry information
_registry: dict[str, type[BaseProtocolFactory]] = {}
# The read-only version of the registry that is allowed to be imported
registry: Mapping[str, type[BaseProtocolFactory]] = MappingProxyType(_registry)

# The mutable underlying dict that holds the mapping of module name to class name
_module_registry: dict[str, str] = {}
# The read-only version of the module registry that is allowed to be imported
module_registry: Mapping[str, str] = MappingProxyType(_module_registry)

T_WorkerSide = TypeVar(
    "T_WorkerSide", bound=BaseCompatibleWorkerAlgorithm, covariant=True
)


class _BaseCompatibleAlgoFactoryCommon(Protocol[T_WorkerSide]):
    """Protocol defining common base algorithm factory compatibility."""

    class_name: str
    _inference_algorithm: bool = True
    fields_dict: ClassVar[T_FIELDS_DICT] = {}
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}


class BaseCompatibleAlgoFactoryWorkerStandard(
    _BaseCompatibleAlgoFactoryCommon[T_WorkerSide], Protocol[T_WorkerSide]
):
    """Protocol defining base algorithm factory compatibility.

    For the case where the worker() call has no explicit requirements.
    """

    def worker(self, **kwargs: Any) -> T_WorkerSide:
        """Worker-side of the algorithm."""
        ...


class BaseCompatibleAlgoFactoryWorkerHubNeeded(
    _BaseCompatibleAlgoFactoryCommon[T_WorkerSide], Protocol[T_WorkerSide]
):
    """Protocol defining base algorithm factory compatibility.

    For the case where the worker() call explicitly needs a hub instance.
    """

    def worker(self, *, hub: BitfountHub, **kwargs: Any) -> T_WorkerSide:
        """Worker-side of the algorithm."""
        ...


BaseCompatibleAlgoFactory = (
    BaseCompatibleAlgoFactoryWorkerStandard | BaseCompatibleAlgoFactoryWorkerHubNeeded
)


class BaseProtocolFactory(ABC, _RolesMixIn, _BaseSerializableObjectMixIn):
    """Base Protocol from which all other protocols must inherit."""

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "primary_results_path": fields.Str(allow_none=True)
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {"algorithm": algorithms.registry}

    def __init__(
        self,
        *,
        algorithm: Union[
            BaseCompatibleAlgoFactory, Sequence[BaseCompatibleAlgoFactory]
        ],
        primary_results_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        try:
            self.class_name = ProtocolType[type(self).__name__].value
        except KeyError:
            # Check if the protocol is a plug-in
            self.class_name = type(self).__name__

        super().__init__(**kwargs)
        self.algorithm = algorithm

        self.primary_results_path = primary_results_path

        for algo in self.algorithms:
            self._validate_algorithm(algo)

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to Protocol registry")
            _registry[cls.__name__] = cls
            _module_registry[cls.__module__] = cls.__name__
        else:
            # Add abstract classes to the registry (so they can be correctly used for
            # serialization field inheritance) but ensure they are stored differently
            # so they cannot be accidentally looked up by name
            abstract_cls_name = f"Abstract::{cls.__name__}"
            logger.debug(
                f"Adding abstract class {cls.__name__}: {cls} to Protocol registry"
                f" as {abstract_cls_name}"
            )
            _registry[abstract_cls_name] = cls

    @property
    def algorithms(self) -> list[BaseCompatibleAlgoFactory]:
        """Returns the algorithms in the protocol."""
        if isinstance(self.algorithm, Sequence):
            return list(self.algorithm)
        return [self.algorithm]

    @classmethod
    @abstractmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Checks that `algorithm` is compatible with the protocol.

        Raises TypeError if `algorithm` is not compatible with the protocol.
        """
        pass

    @abstractmethod
    def modeller(
        self, mailbox: _ModellerMailbox, **kwargs: Any
    ) -> BaseModellerProtocol:
        """Creates an instance of the modeller-side for this protocol."""
        raise NotImplementedError

    @abstractmethod
    def worker(
        self,
        mailbox: _WorkerMailbox,
        hub: BitfountHub,
        context: Optional[ProtocolContext] = None,
        **kwargs: Any,
    ) -> BaseWorkerProtocol:
        """Creates an instance of the worker-side for this protocol."""
        raise NotImplementedError

    def dump(self) -> SerializedProtocol:
        """Returns the JSON-serializable representation of the protocol."""
        return cast(SerializedProtocol, bf_dump(self))

    def run(
        self,
        pod_identifiers: Collection[str],
        session: Optional[BitfountSession] = None,
        username: Optional[str] = None,
        hub: Optional[BitfountHub] = None,
        ms_config: Optional[MessageServiceConfig] = None,
        message_service: Optional[_MessageService] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        identity_verification_method: IdentityVerificationMethod = IdentityVerificationMethod.DEFAULT,  # noqa: E501
        private_key_or_file: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
        require_all_pods: bool = False,
        run_on_new_data_only: bool = False,
        model_out: Optional[Union[Path, str]] = None,
        project_id: Optional[str] = None,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> Optional[Any]:
        """Sets up a local Modeller instance and runs the protocol.

        Args:
            pod_identifiers: The BitfountHub pod identifiers to run against.
            session: Optional. Session to use for authenticated requests.
                 Created if needed.
            username: Username to run as. Defaults to logged in user.
            hub: BitfountHub instance. Default: hub.bitfount.com.
            ms_config: Message service config. Default: messaging.bitfount.com.
            message_service: Message service instance, created from ms_config if not
                provided. Defaults to "messaging.bitfount.com".
            pod_public_key_paths: Public keys of pods to be checked against.
            identity_verification_method: The identity verification method to use.
            private_key_or_file: Private key (to be removed).
            idp_url: The IDP URL.
            require_all_pods: If true raise PodResponseError if at least one pod
                identifier specified rejects or fails to respond to a task request.
            run_on_new_data_only: Whether to run the task on new datapoints only.
                Defaults to False.
            model_out: The path to save the model to.
            project_id: The project ID to run the task under.
            batched_execution: Whether to run the task in batched mode. Defaults to
                False.
            test_run: If True, runs the task in test mode, on a limited number of
                datapoints. Defaults to False.
            force_rerun_failed_files: If True, forces a rerun on files that
                the task previously failed on. If False, the task will skip
                files that have previously failed. Note: This option can only be
                enabled if both enable_batch_resilience and
                individual_file_retry_enabled are True. Defaults to True.

        Returns:
            Results of the protocol.

        Raises:
            PodResponseError: If require_all_pods is true and at least one pod
                identifier specified rejects or fails to respond to a task request.
            ValueError: If attempting to train on multiple pods, and the
                `DataStructure` table name is given as a string.
        """
        hub = _default_bitfounthub(hub=hub, username=username)
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        if len(pod_identifiers) > 1 and batched_execution:
            logger.warning(
                "Batched execution is only supported for single pod tasks. "
                "Resuming task without batched execution."
            )
            batched_execution = False

        for algo in self.algorithms:
            if (
                isinstance(algo, _BaseModelAlgorithmFactory)
                and algo.model.datastructure is not None
            ):
                if (
                    len(pod_identifiers) > 1
                    and hasattr(algo.model.datastructure, "table")
                    and isinstance(algo.model.datastructure.table, str)
                ):
                    raise ValueError(
                        "You are attempting to train on multiple pods, and the "
                        "provided the DataStructure table name is a string. "
                        "Please make sure that the `table` argument to the "
                        "`DataStructure` is a mapping of Pod names to table names. "
                    )
                pod_identifiers = _check_and_update_pod_ids(pod_identifiers, hub)

        if not session:
            session = hub.session
        if not idp_url:
            idp_url = _get_idp_url()
        if not message_service:
            message_service = _create_message_service(
                session=session,
                ms_config=ms_config,
            )

        modeller = _Modeller(
            protocol=self,
            message_service=message_service,
            bitfounthub=hub,
            pod_public_key_paths=pod_public_key_paths,
            identity_verification_method=identity_verification_method,
            private_key=private_key_or_file,
            idp_url=idp_url,
        )

        name = type(self).__name__

        logger.info(f"Starting {name} Task...")

        result = modeller.run(
            pod_identifiers,
            require_all_pods=require_all_pods,
            project_id=project_id,
            model_out=model_out,
            run_on_new_data_only=run_on_new_data_only,
            batched_execution=batched_execution,
            test_run=test_run,
            force_rerun_failed_files=force_rerun_failed_files,
        )
        logger.info(f"Completed {name} Task.")
        return result


LimitsExceededInfo = NamedTuple(
    "LimitsExceededInfo", [("overrun", int), ("allowed", int)]
)


class ModelInferenceProtocolMixin:
    """Mixin class for protocols that may contain one or more model inference steps.

    These protocols will have to respect any model inference usage limits that are
    associated with the model(s) in use.
    """

    @staticmethod
    def check_usage_limits(
        limits: dict[str, InferenceLimits],
        inference_algorithm: ModelInferenceWorkerSideAlgorithm,
    ) -> Optional[LimitsExceededInfo]:
        """Check if the most recent inference run has exceeded the usage limits.

        Updates the total usage count associated with model in question, regardless
        of if the limits are exceeded or not.

        Args:
            limits: The inference usage limits as a mapping of model_id to usage
                limits.
            inference_algorithm: The inference algorithm instance that has just been
                run.

        Returns:
            If limits were not exceeded, returns None. Otherwise, returns a container
            with `.overrun` and `.allowed` attributes which indicate the number of
            predictions usage was exceeded by and the number of predictions actually
            allowed to be used respectively.
            e.g. for an initial total_usage of 10, a limit of 20, and an inference
            run that used 14 more inferences, will return `(4, 10)`. If limits are
            not exceeded, will return `None`.
        """
        # Extract model associated with inference algorithm, failing fast if no
        # model_id is found.
        model_id: Optional[str] = inference_algorithm.maybe_bitfount_model_slug
        if model_id is None:
            logger.debug(
                f"Inference algorithm {inference_algorithm} has no associated model ID."
            )
            return None

        # Find the usage limits associated with the model in question, failing fast
        # if no usage limits are found for that model.
        model_limits: InferenceLimits
        try:
            model_limits = limits[model_id]
        except KeyError:
            logger.debug(f"No limits specified for model {model_id}")
            return None

        # Calculate the new usages associated with the model in question and update
        # the total_usage counts in the limits.
        resources_consumed_for_model: list[ResourceConsumed] = [
            rc
            for rc in inference_algorithm.get_resources_consumed()
            if rc.resource_identifier == model_id
            and rc.resource_type == ResourceType.MODEL_INFERENCE
        ]

        if len(resources_consumed_for_model) > 1:
            raise ValueError(
                f"Multiple model inference resources consumed found for {model_id};"
                f" only one is supported."
            )

        new_usage: int = int(sum(rc.amount for rc in resources_consumed_for_model))
        model_limits.total_usage = model_limits.total_usage + new_usage

        # Check if we have exceeded the usage limits and return this information.
        if model_limits.total_usage >= model_limits.limit:
            if model_limits.total_usage > model_limits.limit:
                logger.warning(
                    f"Model usage limits exceeded for model {model_id};"
                    f" usage limit is {model_limits.limit},"
                    f" have performed {model_limits.total_usage} inferences."
                )
            else:  # model_limits.total_usage == model_limits.limits
                logger.warning(
                    f"Model usage limits reached for model {model_id};"
                    f" usage limit is {model_limits.limit},"
                    f" have performed {model_limits.total_usage} inferences."
                )
            overrun: int = model_limits.total_usage - model_limits.limit
            allowed: int = new_usage - overrun
            return LimitsExceededInfo(overrun, allowed)
        else:
            return None

    @staticmethod
    def apply_actual_usage_to_resources_consumed(
        inference_algorithm: ModelInferenceWorkerSideAlgorithm,
        limits_exceeded_info: LimitsExceededInfo | None,
    ) -> list[ResourceConsumed]:
        """Generate a resources consumed list from an algorithm that respects limits.

        Given information on the actual number of inferences that were allowed/used,
        updates resources consumed entries from the given algorithm to reflect this
        limit.

        If limits were not exceeded, just returns the resources consumed information
        unchanged.

        Args:
            inference_algorithm: The inference algorithm used for the inferences.
            limits_exceeded_info: If not None, contains information on the actual
                number of inferences that were allowed/used.

        Returns:
            The list of resources consumed, as generated by the algorithm, with model
            inference resources consumed entries modified to reflect the actually
            used inferences. If limits were not exceeded, returns the list of
            resources consumed, unchanged.
        """
        # Extract model associated with inference algorithm, failing fast if no
        # model_id is found.
        model_id: Optional[str] = inference_algorithm.maybe_bitfount_model_slug
        if model_id is None:
            logger.debug(
                f"Inference algorithm {inference_algorithm} has no associated model ID."
            )
            return []

        resources_consumed: list[ResourceConsumed] = (
            inference_algorithm.get_resources_consumed()
        )

        # If limits weren't exceeded, return the list of resources consumed unchanged
        if limits_exceeded_info is None:
            return resources_consumed

        # Check that there is max 1 model inference related to this model,
        # as otherwise we don't know which one to apply the cap to
        matching_rc_indices: list[int] = [
            i
            for i, rc in enumerate(resources_consumed)
            if rc.resource_identifier == model_id
            and rc.resource_type == ResourceType.MODEL_INFERENCE
        ]
        if len(matching_rc_indices) > 1:
            raise ValueError(
                f"Multiple model inference resource usages found for model {model_id};"
                f" unable to apply actual usage caused by exceeding limits."
            )

        # Otherwise, apply the actual usage (i.e. that reduced because we can only
        # use part of the prediction) to the resource in question
        resources_consumed[matching_rc_indices[0]].amount = limits_exceeded_info.allowed
        return resources_consumed

    @staticmethod
    async def handle_limits_exceeded(
        exceeded_inference_algo: ModelInferenceWorkerSideAlgorithm,
        limits_exceeded_info: LimitsExceededInfo,
        limits_info: dict[str, InferenceLimits],
        mailbox: _WorkerMailbox,
    ) -> NoReturn:
        """Handles when usage limits are exceeded within the protocol.

        In particular, sends a TASK_ABORT message from Worker->Modeller, letting them
        know that they limits are exceeded, and raises a TaskAbortError to do the
        same within the Worker side.
        """
        # model_id SHOULD NOT be None as the only way we can look-up/calculate usage
        # limits is if the model slug is present on the inference algorithm
        model_id: Optional[str] = exceeded_inference_algo.maybe_bitfount_model_slug
        error_msg: str = "Model inference usage limits reached for model"
        if model_id is not None:
            error_msg += f" {model_id}."

            # If limits have been exceeded then that means the total number of
            # predictions done in this task is dictated by the usage limit and the
            # initial usage reported
            try:
                model_limits_info = limits_info[model_id]
                total_predictions_this_run: int = (
                    model_limits_info.limit - model_limits_info.initial_total_usage
                )

                error_msg += (
                    f" {total_predictions_this_run} predictions were successfully run."
                )
            except KeyError:
                logger.warning(
                    f"Could not find limits info for model {model_id}"
                    f" when resolving total usage in run."
                )
        else:
            error_msg += "."

        error_msg += (
            f" In last batch {limits_exceeded_info.overrun}"
            f" predictions were over the limit."
        )

        # Handle task abort in Modeller (Pod sends message)
        await mailbox.send_task_abort_message(error_msg, Reason.LIMITS_EXCEEDED)

        # Handle task abort in Worker (exception handling)
        raise TaskAbortError(
            error_msg, Reason.LIMITS_EXCEEDED, message_already_sent=True
        )

    def _signal_final_step_for_limits_exceeded(
        self,
        protocol_state: Optional[ProtocolState] = None,
    ) -> None:
        """Signal final step if limits exceeded."""
        if protocol_state is not None:
            protocol_state.execute_final_step = True
            protocol_state.termination_reason = TerminationReason.LIMITS_EXCEEDED


T_FinalStepAlgo = TypeVar("T_FinalStepAlgo", bound=FinalStepAlgorithm)


class FinalStepProtocol(Generic[T_FinalStepAlgo]):
    """Tagging class for protocols that contain a final step.

    These protocols will have a number of steps that can be operated batch-wise (batch
    steps) followed by step(s) to be executed at the end.

    Type Args:
        T_FinalStepAlgo: Type of the setup algorithm, must implement
            FinalStepAlgorithm
    """

    @property
    def algorithms(
        self,
    ) -> (
        # FinalStepProtocol supports working on either the worker or modeller side
        # of the protocol, same as InitialSetupProtocol for compatibility
        list[BaseCompatibleModellerAlgorithm] | list[BaseCompatibleWorkerAlgorithm]
    ):
        """Get the algorithms for this protocol."""
        raise NotImplementedError(
            "Protocols using FinalStepProtocol must implement the algorithms property"
        )

    async def run_final_step(
        self, context: Optional[ProtocolContext] = None, **kwargs: Any
    ) -> Any:
        """Execute the final reduce step."""
        logger.info("Starting final reduce step for the protocol")

        # Find and execute final reduce step for applicable algorithms
        for algo in self.algorithms:
            if isinstance(algo, FinalStepAlgorithm):
                algo.run_final_step(context=context, **kwargs)
        return None


class FinalStepReduceProtocol(FinalStepProtocol):
    """Tagging class for protocols that contain a final "reduce" step.

    These protocols will have a number of steps that can be operated batch-wise (batch
    steps) followed by step(s) at the end that cannot be executed batch-wise but
    instead require access to the outputs from all batch steps (reduce step(s)).
    """

    pass


T_InitialSetupAlgo = TypeVar("T_InitialSetupAlgo", bound=InitialSetupAlgorithm)


class InitialSetupProtocol(Generic[T_InitialSetupAlgo]):
    """Tagging class for protocols that contain an initial setup step.

    These protocols will have an initial step that must be executed before any batching,
    followed by steps that can be operated batch-wise.

    Type Args:
        T_InitialSetupAlgo: Type of the setup algorithm, must implement
            InitialSetupAlgorithm
    """

    @property
    def algorithms(
        self,
    ) -> (
        # InitialSetupProtocol supports working on either the worker or modeller side
        # of the protocol
        list[BaseCompatibleModellerAlgorithm] | list[BaseCompatibleWorkerAlgorithm]
    ):
        """Get the algorithms for this protocol."""
        raise NotImplementedError(
            "Protocols using InitialSetupProtocol must implement the "
            "algorithms property"
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Verify first algorithm implements InitialSetupAlgorithm
        if not isinstance(self.algorithms[0], InitialSetupAlgorithm):
            raise TypeError(
                f"First algorithm must implement InitialSetupAlgorithm, "
                f"got {type(self.algorithms[0])} instead"
            )

    def run_initial_setup(self, **kwargs: Any) -> None:
        """Run the initial setup phase."""
        first_algo = self.algorithms[0]
        if not isinstance(first_algo, InitialSetupAlgorithm):
            raise TypeError(
                f"First algorithm must implement InitialSetupAlgorithm, "
                f"got {type(first_algo)} instead"
            )
        first_algo.setup_run(**kwargs)
