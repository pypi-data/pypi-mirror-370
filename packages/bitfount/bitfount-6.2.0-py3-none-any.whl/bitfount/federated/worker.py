"""Workers for handling task running on pods."""

from __future__ import annotations

from collections.abc import Callable, Generator, Sequence
from contextlib import closing, contextmanager
import copy
from datetime import datetime
from functools import partial
import hashlib
import json
from sqlite3 import Connection
from typing import TYPE_CHECKING, Any, Optional, cast

import pandas as pd

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasplitters import (
    DatasetSplitter,
    PercentageSplitter,
    SplitterDefinedInData,
    _InferenceSplitter,
)
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.exceptions import BitfountError
from bitfount.externals.general.authentication import ExternallyManagedJWT
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithm,
    _BaseModelAlgorithmFactory,
)
from bitfount.federated.authorisation_checkers import (
    _AuthorisationChecker,
)
from bitfount.federated.exceptions import (
    NoDataError,
    PodSchemaMismatchError,
    TaskAbortError,
)
from bitfount.federated.helper import TaskContext
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.monitoring.monitor import task_config_update
from bitfount.federated.pod_db_utils import (
    get_failed_files_cache,
    map_task_to_hash_add_to_db,
    save_failed_files_to_project_db,
    save_processed_datapoint_to_project_db,
)
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseProtocolFactory,
    _BaseProtocol,
)
from bitfount.federated.protocols.model_protocols.federated_averaging import (
    FederatedAveraging,
)
from bitfount.federated.transport.message_service import Reason, _BitfountMessageType
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.federated.types import SerializedAlgorithm, SerializedProtocol
from bitfount.federated.utils import _PROTOCOLS
from bitfount.hooks import BaseProtocolHook, HookType, get_hooks
from bitfount.hub.api import BitfountHub
from bitfount.runners.utils import get_secrets_for_use
from bitfount.schemas.utils import bf_load
from bitfount.types import _JSONDict
from bitfount.utils.db_connector import ProjectDbConnector

if TYPE_CHECKING:
    from bitfount.runners.config_schemas import APIKeys
    from bitfount.runners.config_schemas.common_schemas import SecretsUse


logger = _get_federated_logger(__name__)


class SaveResultsToDatabase(BaseProtocolHook):
    """Hook to save protocol results to database."""

    def on_run_end(
        self, protocol: _BaseProtocol, context: TaskContext, *args: Any, **kwargs: Any
    ) -> None:
        """Runs after protocol run to save results to database."""
        if context == TaskContext.WORKER:
            worker: _Worker = kwargs["worker"]
            db_con_getter: Optional[Callable[[], Optional[Connection]]] = kwargs.get(
                "db_con"
            )

            # If we can potentially get a DB connection, the context manager should
            # ensure it is closed.
            @contextmanager
            def _potential_db_con_cm() -> Generator[Optional[Connection], None, None]:
                conn: Optional[Connection] = None
                try:
                    if db_con_getter is not None:
                        conn = db_con_getter()
                    yield conn
                finally:
                    if conn is not None:
                        conn.close()

            with _potential_db_con_cm() as db_con:
                if db_con is None:
                    logger.warning(
                        "Results cannot be saved to project database. "
                        "No project database connection found."
                    )
                elif not isinstance(worker.datasource, FileSystemIterableSource):
                    logger.warning(
                        "Results cannot be saved to project database. "
                        "Datasource is not a FileSystemIterableSource."
                    )
                else:
                    # We don't need any error handling here, as this is in a hook and
                    # so any errors will be caught elsewhere
                    save_processed_datapoint_to_project_db(
                        task_hash=cast(str, worker._task_hash),
                        datasource=worker.datasource,
                        project_db_con=db_con,
                    )


class SaveFailedFilesToDatabase(BaseProtocolHook):
    """Hook to save failed files to database."""

    def on_resilience_end(
        self, protocol: _BaseProtocol, context: TaskContext, *args: Any, **kwargs: Any
    ) -> None:
        """Runs after protocol run to save failed files to database."""
        if context == TaskContext.WORKER:
            worker: _Worker = kwargs["worker"]
            db_con_getter: Optional[Callable[[], Optional[Connection]]] = kwargs.get(
                "db_con"
            )
            # Get batch config from kwargs if available
            batch_config = kwargs.get("batch_config")
            if not batch_config:
                return

            # Only save failed files if individual retry was enabled and we have results
            if not (
                config.settings.individual_file_retry_enabled
                and batch_config.individual_file_results
            ):
                logger.debug(
                    "Individual file retry not enabled or "
                    "no results - not saving failed files"
                )
                return

            # If we can potentially get a DB connection, the context manager should
            # ensure it is closed.
            @contextmanager
            def _potential_db_con_cm() -> Generator[Optional[Connection], None, None]:
                conn: Optional[Connection] = None
                try:
                    if db_con_getter is not None:
                        conn = db_con_getter()
                    yield conn
                finally:
                    if conn is not None:
                        conn.close()

            with _potential_db_con_cm() as db_con:
                if db_con is None:
                    logger.debug(
                        "Failed files cannot be saved to project database. "
                        "No project database connection found."
                    )
                elif not isinstance(worker.datasource, FileSystemIterableSource):
                    logger.debug(
                        "Failed files cannot be saved to project database. "
                        "Datasource is not a FileSystemIterableSource."
                    )
                else:
                    # Collect only files that failed individually
                    failed_files = {}
                    for (
                        file_path,
                        success,
                    ) in batch_config.individual_file_results.items():
                        if not success:  # File failed individually
                            error = batch_config.file_level_errors.get(
                                file_path, Exception("File failed individually")
                            )
                            failed_files[file_path] = error

                    if failed_files:
                        # We don't need any error handling here, as this is in a
                        # hook and so any errors will be caught elsewhere
                        save_failed_files_to_project_db(
                            project_db_con=db_con,
                            failed_files=failed_files,
                            task_hash=cast(str, worker._task_hash),
                            datasource=worker.datasource,
                        )
                        logger.info(
                            f"Saved {len(failed_files)} genuinely failed "
                            f"files to database."
                        )


class _Worker:
    """Client worker which runs a protocol locally.

    Args:
        datasource: BaseSource object.
        datasource_name: Name of the datasource.
        schema: BitfountSchema object corresponding to the datasource. This is just
            used to validate the protocol.
        mailbox: Relevant mailbox.
        bitfounthub: BitfountHub object.
        authorisation: AuthorisationChecker object.
        parent_pod_identifier: Identifier of the pod the Worker is running in.
        serialized_protocol: SerializedProtocol dictionary that the Pod has received
            from the Modeller.
        pod_vitals: PodVitals object. Defaults to None.
        pod_dp: DPPodConfig object. Defaults to None.
        project_db_connector: Optional ProjectDbConnector object. Defaults to None.
        project_id: The project id. Defaults to None.
        run_on_new_data_only: Whether to run on the whole dataset or only on
            new data. Defaults to False.
        data_identifier: The logical pod/datasource identifier for the task the
            worker has been created for. May differ from the pod identifier for
            pods with multiple datasources. Defaults to the parent_pod_identifier
            if not otherwise provided.
        batched_execution: Whether to run the protocol in batched mode. Defaults to
            False.
        multi_pod_task: Whether the task is a multi-pod task. Defaults to False.
        schema_kwargs: Optional dictionary of schema generation kwargs. Defaults to
            None.
        update_schema: Whether to update the schema. Defaults to False.
        update_schema_level: The level of schema update to perform. Defaults to "empty".
        test_run: Whether the task is a test run. Defaults to False.
        force_rerun_failed_files: If True, forces a rerun on files that
            the task previously failed on. If False, the task will skip
            files that have previously failed. Note: This option can only be
            enabled if both enable_batch_resilience and
            individual_file_retry_enabled are True. Defaults to True.
    """

    def __init__(
        self,
        datasource: BaseSource,
        datasource_name: str,
        schema: BitfountSchema,
        mailbox: _WorkerMailbox,
        bitfounthub: BitfountHub,
        authorisation: _AuthorisationChecker,
        parent_pod_identifier: str,
        serialized_protocol: SerializedProtocol,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_vitals: Optional[_PodVitals] = None,
        pod_dp: Optional[DPPodConfig] = None,
        project_db_connector: Optional[ProjectDbConnector] = None,
        project_id: Optional[str] = None,
        run_on_new_data_only: bool = False,
        data_identifier: Optional[str] = None,
        batched_execution: Optional[bool] = None,
        multi_pod_task: bool = False,
        schema_kwargs: Optional[dict[str, Any]] = None,
        update_schema: bool = False,
        update_schema_level: str = "empty",
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
        secrets: Optional[
            APIKeys
            | ExternallyManagedJWT
            | dict[SecretsUse, APIKeys | ExternallyManagedJWT]
        ] = None,
        **_kwargs: Any,
    ):
        self.datasource = datasource
        self.datasource_name = datasource_name
        self.mailbox = mailbox
        self.hub = bitfounthub
        self.authorisation = authorisation
        self.parent_pod_identifier = parent_pod_identifier
        self.serialized_protocol = serialized_protocol
        self.pod_vitals = pod_vitals
        self._pod_dp = pod_dp
        self.project_id = project_id
        self.multi_pod_task = multi_pod_task
        self._project_db_connector = (
            project_db_connector if project_id is not None else None
        )
        self.run_on_new_data_only = (
            run_on_new_data_only
            if self._project_db_connector is not None
            and isinstance(self.datasource, FileSystemIterableSource)
            else False
        )
        self.force_rerun_failed_files = force_rerun_failed_files
        # Schema and schema generation attributes
        self.schema = schema
        self.schema_kwargs = schema_kwargs
        self.update_schema = update_schema
        self.update_schema_level = update_schema_level

        # The logical pod/datasource identifier that is actually being used by
        # this worker. For multidatasource pods, this will be different than the
        # pod identifier of the physical pod that the worker is running on
        # (parent_pod_identifier).
        # Will still be of the form: <pod_namespace>/<datasource_name>
        self._data_identifier = (
            data_identifier if data_identifier else self.parent_pod_identifier
        )
        # Compute task hash on ordered json dictionary
        # excluding the schema part of the model.
        self._task_hash = self._compute_task_hash()

        self.batched_execution = (
            batched_execution
            if batched_execution is not None
            else config.settings.default_batched_execution
        )
        self.test_run = test_run

        self._secrets = secrets

        # Keep track of the original data splitter for the datasource
        self._orig_data_splitter = data_splitter

        # Set up the results saving hook. This is idempotent so it's safe to
        # call it multiple times for different tasks
        if self._project_db_connector is not None:
            SaveResultsToDatabase().register()
            if (
                config.settings.enable_batch_resilience
                and config.settings.individual_file_retry_enabled
            ):
                SaveFailedFilesToDatabase().register()

        # Clear the file_names cache on the FileSystemIterableSource
        self._clear_datasource_file_names_cache()

    def check_if_data_exists(self) -> None:
        """Check if data exists in the datasource."""
        # Check that data is not empty
        empty_data = False
        if self.schema.number_of_records == 0 and self.update_schema_level != "empty":
            empty_data = True
        # For dataless schemas, try to yield data to confirm
        # there is at least one datapoint.
        elif self.schema.number_of_records == 0 and self.update_schema_level == "empty":
            try:
                data = next(self.datasource.yield_data(partition_size=1))
                if data.empty:
                    empty_data = True
            except StopIteration:
                empty_data = True
        if empty_data:
            raise NoDataError("""Dataset is empty. Aborting task.""")

    def check_and_update_schema_if_necessary(self) -> None:
        """Check if schema needs to be updated and update it if necessary."""
        # Check if new files have been added to the datasource
        # and update the schema if necessary
        if self.update_schema_level == "full":
            self._check_for_new_files()
        if self.update_schema:
            if self.update_schema_level == "full":
                # Apply test subset for "full" schema generation during test runs
                if self.test_run and isinstance(
                    self.datasource, FileSystemIterableSource
                ):
                    num_files = int(
                        getattr(config.settings, "test_run_number_of_files", 1)
                    )
                    # Get first N files by iterating without loading all into memory
                    subset = []
                    for filename in self.datasource.selected_file_names_iter():
                        subset.append(filename)
                        if len(subset) >= num_files:
                            break
                    self.datasource.selected_file_names_override = subset
                if self.schema_kwargs:
                    force_stypes = self.schema_kwargs.get("force_stypes", None)
                    ignore_cols = self.schema_kwargs.get("ignore_cols", None)
                    self.schema.generate_full_schema(
                        datasource=self.datasource,
                        force_stypes=force_stypes,
                        ignore_cols=ignore_cols,
                    )
                else:
                    self.schema.generate_full_schema(datasource=self.datasource)
            elif self.update_schema_level == "partial":
                self.schema.generate_partial_schema(datasource=self.datasource)

    def _check_for_new_files(self) -> None:
        """Check for new files in the FileSystemIterableSource.

        This is only relevant if the schema is set to full. If the schema is set
        to empty, we don't need to check for new files.
        """
        if isinstance(self.datasource, FileSystemIterableSource):
            # Check if the cached file list is the same as the current file list
            if self.datasource.has_uncached_files():
                # if the two file lists are different,
                # then force schema (and cache) update
                self.update_schema = True
                logger.info(
                    "New files detected, updating schema and cache before "
                    "continuing task with `full` schema requirement."
                )

    async def run(self) -> None:
        """Runs the specified protocol on the worker."""
        # Send task to Monitor service. This is done regardless of whether the task
        # is accepted. This method is being run in a task monitor context manager so
        # no need to set the task monitor prior to sending.
        self._update_task_config()
        # Check authorisation with access manager
        auth_check_result = await self.authorisation.check_authorisation()
        pod_response_message = auth_check_result.pod_response_message
        # Check if there are messages in the pod response instance; this only happens
        # if the task is rejected.
        if pod_response_message.messages:
            # Reject task, as there were errors
            await self.mailbox.reject_task(
                pod_response_message.messages,
            )
            return
        # Accept task and inform modeller
        logger.info("Task accepted, informing modeller.")
        await self.mailbox.accept_task()

        # Set the is_task_running flag on the datasource to True
        self.datasource.is_task_running = True
        if not self.datasource.has_predefined_schema:
            # Update schema based on the schema requirements of the task
            self.check_and_update_schema_if_necessary()
            try:
                for hook in get_hooks(HookType.POD):
                    hook.on_pod_task_data_check(
                        task_id=self.mailbox.task_id,
                        message="Checking if data exists in the dataset",
                    )

                self.check_if_data_exists()
            except NoDataError as e:
                msg = "No data found in the datasource. Aborting task."
                logger.info(msg)
                self.mailbox.abort = (msg, Reason.NO_DATA)
                await self.mailbox.send_task_abort_message(msg, Reason.NO_DATA)
                self._cleanup_after_task()
                raise e

        # Update hub instance if BitfountModelReference
        algorithm = self.serialized_protocol["algorithm"]
        if not isinstance(self.serialized_protocol["algorithm"], list):
            algorithm = [cast(SerializedAlgorithm, algorithm)]

        algorithm = cast(list[SerializedAlgorithm], algorithm)
        for algo in algorithm:
            if model := algo.get("model"):
                if model["class_name"] == "BitfountModelReference":
                    logger.debug("Patching model reference hub.")
                    model["hub"] = self.hub

        # Deserialize protocol only after task has been accepted just to be safe
        protocol: BaseProtocolFactory = cast(
            BaseProtocolFactory,
            bf_load(cast(_JSONDict, self.serialized_protocol), _PROTOCOLS),
        )
        # Load data according to model datastructure if one exists.
        # For multi-algorithm protocols, we assume that all algorithm models have the
        # same datastructure.
        datastructure: Optional[DataStructure] = None
        algorithm_ = protocol.algorithm
        if not isinstance(algorithm_, Sequence):
            algorithm_ = [algorithm_]

        algorithm_ = cast(list[BaseCompatibleAlgoFactory], algorithm_)

        # Find and update datastructure with the appropriate pod identifiers
        for algo_ in algorithm_:
            if isinstance(algo_, _BaseModelAlgorithmFactory):
                datastructure = algo_.model.datastructure
                break
        # Find and update schema with the appropriate on
        for algo_ in algorithm_:
            if isinstance(algo_, _BaseModelAlgorithmFactory):
                algo_.model.schema = self.schema
        if any(algo._inference_algorithm is False for algo in algorithm_):
            # If any non-inference algorithms are present,
            # then it's not an inference task.
            inference_task = False
        else:
            inference_task = True

        data_splitter = self._resolve_data_splitter(
            datastructure, self._orig_data_splitter, inference_task
        )
        processed_files: Optional[dict[str, datetime]] = None
        failed_files_cache: Optional[dict[str, dict[str, str]]] = None
        if (optional_con := self._get_project_db_con_if_allowed(protocol)) is not None:
            with closing(optional_con) as project_db_con:
                try:
                    cur = project_db_con.cursor()
                    columns_and_types = (
                        self.datasource.get_project_db_sqlite_create_table_query()
                    )
                    # Drop the old version of the table if it exists.
                    cur.execute(f"DROP TABLE IF EXISTS '{self._task_hash}'")
                    # Create the new version of the table if it doesn't exist already.
                    cur.execute(
                        f"""CREATE TABLE IF NOT EXISTS "{self._task_hash}-v2" ({columns_and_types})"""  # noqa: E501
                    )
                    # Create failed files table
                    failed_columns_and_types = (
                        self.datasource.get_project_db_sqlite_create_table_query()
                    )  # noqa: E501
                    cur.execute(
                        f"""CREATE TABLE IF NOT EXISTS "{self._task_hash}-failed-v1" ({failed_columns_and_types})"""  # noqa: E501
                    )
                    project_db_con.commit()
                except Exception as e:
                    logger.error(
                        f"Encountered error whilst creating task hash table in database: {e}"  # noqa: E501
                    )
                    logger.debug(e, exc_info=True)

                try:
                    # task_hash is set if pod_db is true, so
                    # it's safe to cast
                    map_task_to_hash_add_to_db(
                        self.serialized_protocol,
                        cast(str, self._task_hash),
                        project_db_con,
                    )
                except Exception as e:
                    logger.error(
                        f"Encountered error whilst initializing worker task"
                        f" hash in database: {e}"
                    )
                    logger.debug(e, exc_info=True)

                if (
                    self.run_on_new_data_only
                    and inference_task
                    and isinstance(self.datasource, FileSystemIterableSource)
                ):
                    processed_files = self._get_processed_files_cache(project_db_con)
                    failed_files_cache = self._get_failed_files_cache(project_db_con)

        # Project ID needs to be set on the model algorithms before `worker` is called
        # so that the algorithm has the right permissions to download the model from the
        # Hub.
        for algo_ in algorithm_:
            if isinstance(algo_, _BaseModelAlgorithmFactory):
                algo_.project_id = self.project_id

        # Check that the protocol context is for Worker, if supplied
        if (
            task_context := auth_check_result.protocol_context.task_context
            != TaskContext.WORKER
        ):
            if task_context is not None:
                logger.warning(
                    f"Protocol context for Worker run contained {task_context=};"
                    f" correcting to TaskContext.WORKER."
                )
            auth_check_result.protocol_context.task_context = TaskContext.WORKER

        # Calling the `worker` method on the protocol also calls the `worker` method on
        # underlying objects such as the algorithm and aggregator. The algorithm
        # `worker` method will also download the model from the Hub if it is a
        # `BitfountModelReference`
        worker_protocol = protocol.worker(
            mailbox=self.mailbox,
            hub=self.hub,
            context=auth_check_result.protocol_context,
        )

        # If the algorithm is a model algorithm, then we need to pass the pod
        # identifier to the model so that it can extract the relevant information
        # from the datastructure the Modeller has sent. This must be done after
        # the worker protocol has been created, so that any model references
        # have been converted to models.
        for worker_algo in worker_protocol.algorithms:
            if isinstance(worker_algo, _BaseModelAlgorithm):
                worker_algo.model.set_datastructure_identifier(self._data_identifier)

        for hook in get_hooks(HookType.POD):
            hook.on_task_progress(
                task_id=self.mailbox.task_id,
                message="Setting up protocol and algorithms",
            )

        # See if we have EHR secrets to pass in
        ehr_secrets: Optional[ExternallyManagedJWT] = None
        try:
            ehr_secrets_tmp = get_secrets_for_use(self._secrets, "ehr")
        except BitfountError:
            # EHR secrets are not present
            pass
        else:
            # Only ExternallyManagedJWT is currently supported for EHR secrets
            if ehr_secrets_tmp is None or isinstance(
                ehr_secrets_tmp, ExternallyManagedJWT
            ):
                ehr_secrets = ehr_secrets_tmp
            else:
                raise TypeError(
                    f"EHR secrets must be an ExternallyManagedJWT or None."
                    f" Got: {type(ehr_secrets_tmp)}"
                )

        try:
            # Initialise the worker protocol
            worker_protocol.initialise(
                datasource=self.datasource,
                data_splitter=data_splitter,
                pod_dp=self._pod_dp,
                pod_identifier=self.mailbox.pod_identifier,
                project_id=self.project_id,
                ehr_secrets=ehr_secrets,
                parent_pod_identifier=self.parent_pod_identifier,
            )
            # Run the worker protocol
            await worker_protocol.run(
                pod_vitals=self.pod_vitals,
                batched_execution=self.batched_execution,
                context=auth_check_result.protocol_context,
                processed_files_cache=processed_files,
                failed_files_cache=failed_files_cache,
                hook_kwargs={
                    "worker": self,
                    # TODO: [NO_TICKET: Casual thoughts] Should this instead be
                    #       a method for the hook to retrieve its own connection?
                    #       Otherwise connection could be very long-lived.
                    # Hook is responsible for closing DB connection
                    "db_con": partial(self._get_project_db_con_if_allowed, protocol),
                },
                test_run=self.test_run,
            )
        except TaskAbortError as tae:
            if not tae.message_already_sent:
                logger.error(
                    "Exception encountered during task execution. Aborting task."
                )
                await self.mailbox.send_task_abort_message(
                    str(tae),
                    tae.reason if tae.reason is not None else Reason.WORKER_ERROR,
                )
                tae.message_already_sent = True
                raise tae
            else:
                logger.error(
                    f"Exception encountered during task execution,"
                    f" message already sent."
                    f" Exception was: {str(tae)}"
                )
        except Exception as e:
            logger.error("Exception encountered during task execution. Aborting task.")
            await self.mailbox.send_task_abort_message(str(e), Reason.WORKER_ERROR)
            raise e
        else:
            await self.mailbox.get_task_complete_update()
        finally:
            logger.info("Task complete.")
            self._cleanup_after_task()

    def _compute_task_hash(self) -> Optional[str]:
        """Computes a hash of the serialized protocol.

        This function makes a deep copy of the serialized protocol,
        removes the 'schema' part from each 'model' in the 'algorithms' list,
        and then computes the hash. The original serialized protocol is not modified.
        Additionally:
            - The 'dataset_name' field is added to the task parameters, containing the
              value of `self.datasource_name`.
            - The 'parent_pod' field is added to the task parameters, containing the
              value of `self.parent_pod_identifier` in the format
              `<username>/<parent pod name>`.
            - The 'data_identifier' field is added to the task parameters, containing
              the value of `self._data_identifier` in the format
              <pod_namespace>/<datasource_name>.

        Returns:
            Optional[str]: The computed hash, or None if the
                project database connector is None.
        """
        protocol_copy = copy.deepcopy(self.serialized_protocol)
        # Ensure the schema of any models is removed
        # before computing the hash.
        algorithms = protocol_copy.get("algorithm", [])

        if isinstance(algorithms, list):
            for algorithm in algorithms:
                model = algorithm.get("model", {})
                if model:
                    model.pop("schema", None)
        task_params = {
            "protocol": protocol_copy,
            "parent_pod": self.parent_pod_identifier,  # in the format <username>/<parent pod name> # noqa: E501
            "data_identifier": self._data_identifier,  # in the format <pod_namespace>/<datasource_name> # noqa: E501
            "datasource_name": self.datasource_name,  # string
        }
        # Compute the hash
        return (
            hashlib.sha256(
                json.dumps(task_params, sort_keys=True).encode("utf-8")
            ).hexdigest()
            if self._project_db_connector is not None
            else None
        )

    def _clear_datasource_file_names_cache(self) -> None:
        """Clears the file_names cache on the FileSystemIterableSource.

        The datasource makes use of `functools.cached_property` to cache the
        file_names property. We want this to be refreshed on every new task so
        that the datasource can pick up any new files that have been added to the
        filesystem since the last task.
        """
        if isinstance(self.datasource, FileSystemIterableSource):
            self.datasource.clear_file_names_cache()

    def _update_task_config(self) -> None:
        """Send task config update to monitor service.

        Also checks that the schema in the task config matches the schema of the
        pod (if there is only a single pod in the task) and raises a
        PodSchemaMismatchError if it doesn't.
        """
        # remove schema from task_config to limit request body size
        task_config = copy.deepcopy(self.serialized_protocol)
        algorithm = task_config["algorithm"]
        algorithms = algorithm if isinstance(algorithm, list) else [algorithm]
        datasource_type = type(self.datasource).__name__
        for algorithm in algorithms:
            if "model" in algorithm.keys():
                model = algorithm["model"]
                datastructure = algorithm.get("datastructure") or algorithm.get(
                    "model", {}
                ).get("datastructure")
                if not datastructure:
                    continue
                # Extract the schema requirements from the datastructure
                # for the given datasource type
                schema_reqs = next(
                    (
                        key
                        for key, value in datastructure.get(
                            "schema_requirements", {}
                        ).items()
                        if datasource_type in value
                    ),
                    None,
                )
                if "schema" in model and model["schema"] is not None:
                    if schema_reqs and schema_reqs != "empty":
                        if (
                            schema_reqs == "full"
                            and not self.multi_pod_task
                            and BitfountSchema.load(model["schema"]) != self.schema
                        ):
                            raise PodSchemaMismatchError(
                                f"Schema mismatch between pod and task in model "
                                f"{model['class_name']}. "
                            )
                    del model["schema"]

        task_config_update(dict(task_config))

    def _cleanup_after_task(self) -> None:
        """Clean-up after running a task on file iterable source."""
        if (
            isinstance(self.datasource, FileSystemIterableSource)
            and self.run_on_new_data_only
        ):
            # Clean up the new_file_names_only_set after task completion
            self.datasource.new_file_names_only_set = None
            # Clean up selected_file_names_override after task completion
            self.datasource.selected_file_names_override = []

        self.mailbox.delete_all_handlers(_BitfountMessageType.LOG_MESSAGE)

    def _get_project_db_con_if_allowed(
        self, protocol: BaseProtocolFactory
    ) -> Optional[Connection]:
        """Retrieves a project DB conn if the various requirements are met."""
        # Can't connect to DB without these details
        if (
            self._project_db_connector is None
            or self.project_id is None
            or not self.datasource.supports_project_db
        ):
            return None

        # For FederatedAveraging, we return a dictionary of
        # validation metrics, which is incompatible with the database.
        if isinstance(protocol, FederatedAveraging):
            return None

        return self._project_db_connector.get_project_db_connection(self.project_id)

    def _get_processed_files_cache(
        self, project_db_con: Connection
    ) -> dict[str, datetime]:
        """Gets processed files info from db for filtering during batched execution.

        Returns:
            Dictionary mapping filename -> last_modified_datetime for processed files
        """

        logger.debug("Loading processed files info from database")
        try:
            run_records = pd.read_sql(
                f'SELECT * FROM "{self._task_hash}-v2"',  # nosec hardcoded_sql_expressions # noqa: E501
                project_db_con,
            )

            if run_records.empty:
                logger.debug("No processed files found in database")
                return {}

            columns = self.datasource.get_project_db_sqlite_columns()
            run_records_dict = dict(
                zip(run_records[columns[0]], run_records[columns[1]])
            )

            # Convert to datetime objects for comparison
            processed_files = {}
            for filename, last_modified_str in run_records_dict.items():
                processed_files[filename] = datetime.fromisoformat(last_modified_str)

            logger.debug(f"Loaded {len(processed_files)} processed files from database")
            return processed_files

        except Exception as e:
            logger.warning(
                f"Error loading processed files: {e}. Treating all files as new."
            )
            return {}

    def _get_failed_files_cache(
        self, project_db_con: Connection
    ) -> Optional[dict[str, dict[str, str]]]:
        """Retrieves failed files cache from database.

        Returns:
            Dictionary mapping filename -> failure info for previously failed files.
            Returns empty dict if force_rerun_failed_files is True.

        """
        # If force rerun is enabled, return empty cache (don't skip any files)
        if self.force_rerun_failed_files:
            logger.debug("Force rerun enabled, returning empty failed files cache")
            return None
        if not isinstance(self.datasource, FileSystemIterableSource):
            logger.debug(
                "Failed files cannot be loaded from project database. "
                "Datasource is not a FileSystemIterableSource."
            )
            return None
        logger.debug("Loading failed files info from database")
        return get_failed_files_cache(
            project_db_con, cast(str, self._task_hash), self.datasource
        )

    def _save_failed_files_to_db(
        self, project_db_con: Connection, failed_files: dict[str, Exception]
    ) -> None:
        """Saves failed files to the project database."""
        if isinstance(self.datasource, FileSystemIterableSource):
            save_failed_files_to_project_db(
                project_db_con,
                failed_files,
                cast(str, self._task_hash),
                self.datasource,
            )

    def _resolve_data_splitter(
        self,
        datastructure: Optional[DataStructure] = None,
        dataset_data_splitter: Optional[DatasetSplitter] = None,
        inference_task: bool = False,
    ) -> DatasetSplitter:
        """Resolves the data splitter.

        The data splitter is resolved in the following order:
            1. If the task is an inference task, the data splitter
                is set to _InferenceSplitter.
            2. Data config for the dataset data_splitter if specified
            3. Provided data_splitter if specified (from datastructure)
            4. PercentageSplitter (default)

        Returns:
            The appropriate data splitter to use.
        """
        data_splitter: DatasetSplitter
        if inference_task:
            if isinstance(dataset_data_splitter, SplitterDefinedInData):
                data_splitter = dataset_data_splitter
            else:
                # If we are running an inference only the datasplit
                # will always be 100% in test.
                data_splitter = _InferenceSplitter()
        else:
            if dataset_data_splitter is not None:
                if datastructure is not None and hasattr(
                    datastructure, "data_splitter"
                ):
                    logger.warning(
                        "Ignoring provided data splitter as the BaseSource "
                        "already has one."
                    )
                data_splitter = dataset_data_splitter
            else:
                if (
                    datastructure is not None
                    and hasattr(datastructure, "data_splitter")
                    and datastructure.data_splitter is not None
                ):
                    logger.info("Using data splitter from datastructure.")
                    data_splitter = datastructure.data_splitter
                else:
                    logger.warning(
                        "No data splitter provided. Using default PercentageSplitter."
                    )
                    data_splitter = PercentageSplitter()
        return data_splitter
