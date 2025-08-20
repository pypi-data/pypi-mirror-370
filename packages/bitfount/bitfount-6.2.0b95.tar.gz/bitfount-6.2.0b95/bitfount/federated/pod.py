"""Pods for responding to tasks."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Iterable, MutableSequence
from contextlib import AbstractContextManager, nullcontext
import os
import threading
from typing import Mapping, Optional, Tuple, Union, cast
import warnings

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from requests import HTTPError, RequestException

from bitfount import config
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
    FileSystemIterableSourceInferrable,
)
from bitfount.data.datasplitters import DatasetSplitter, SplitterDefinedInData
from bitfount.data.exceptions import DataSourceError
from bitfount.data.persistence.sqlite import SQLiteDataPersister
from bitfount.data.schema import BitfountSchema, SchemaGenerationFromYieldData
from bitfount.data.types import _ForceStypeValue, _SemanticTypeValue
from bitfount.externals.general.authentication import ExternallyManagedJWT
from bitfount.federated.aggregators.secure import _is_secure_share_task_request
from bitfount.federated.authorisation_checkers import (
    _IDENTITY_VERIFICATION_METHODS_MAP,
    IdentityVerificationMethod,
    _AuthorisationChecker,
    _OIDCAuthorisationCode,
    _OIDCDeviceCode,
    _SignatureBasedAuthorisation,
    check_identity_verification_method,
)
from bitfount.federated.exceptions import (
    BitfountTaskStartError,
    PodNameError,
    PodRegistrationError,
)
from bitfount.federated.helper import (
    POD_NAME_REGEX,
    _check_and_update_pod_ids,
    _create_and_connect_pod_mailbox,
)
from bitfount.federated.keys_setup import RSAKeyPair, _get_pod_keys
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.monitoring import task_monitor_context
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.pod_vitals import _PodVitals, _PodVitalsHandler
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.schema_management import (
    SchemaManagement,
    _register_dataset,
)
from bitfount.federated.task_requests import (
    _SignedEncryptedTaskRequest,
    _TaskRequest,
    _TaskRequestMessage,
)
from bitfount.federated.transport.base_transport import _run_func_and_listen_to_mailbox
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
)
from bitfount.federated.transport.opentelemetry import setup_opentelemetry_metrics
from bitfount.federated.transport.pod_transport import _PodMailbox
from bitfount.federated.transport.worker_transport import (
    _InterPodWorkerMailbox,
    _WorkerMailbox,
)
from bitfount.federated.types import (
    AggregatorType,
    DatasourceContainer,
    DatasourceContainerConfig,
    HubConfig,
    MinimalSchemaUploadConfig,
    SerializedAlgorithm,
    SerializedProtocol,
    _PodResponseType,
)
from bitfount.federated.utils import _StoppableThead
from bitfount.federated.worker import _Worker
from bitfount.hooks import HookType, get_hooks, on_pod_init_error, on_pod_startup_error
from bitfount.hub.api import BitfountAM, BitfountHub, PodPublicMetadata
from bitfount.hub.authentication_flow import _get_auth_environment
from bitfount.hub.authentication_handlers import _DEFAULT_USERNAME
from bitfount.hub.helper import (
    _create_access_manager,
    _create_bitfounthub,
    _get_pod_public_keys,
    get_pod_schema,
)
from bitfount.runners.config_schemas.common_schemas import SecretsUse
from bitfount.runners.config_schemas.hub_schemas import (
    APIKeys,
)
from bitfount.runners.config_schemas.pod_schemas import (
    PodDataConfig,
    PodDbConfig,
    PodDetailsConfig,
)
from bitfount.runners.utils import get_secrets_for_use
from bitfount.utils import _handle_fatal_error, is_notebook
from bitfount.utils.db_connector import ProjectDbConnector

logger = _get_federated_logger(__name__)


class Pod:
    """Makes data and computation available remotely and responds to tasks.

    The basic component of the Bitfount network is the `Pod` (Processor of Data). Pods
    are co-located with data, check users are authorized to do given operations on the
    data and then do any approved computation. Creating a `Pod` will register the pod
    with Bitfount Hub.

    ```python title="Example usage:"
    import bitfount as bf

    pod = bf.Pod(
        name="really_cool_data",
        data="/path/to/data",
    )
    pod.start()
    ```

    :::tip

    Once you start a `Pod`, you can just leave it running in the background. It will
    automatically respond to any tasks without any intervention required.

    :::

    Args:
        name: Name of the pod. This will appear on `Bitfount Hub` and `Bitfount AM`.
            This is also used for the name of the table in a single-table `BaseSource`.
        datasource: (Deprecated, use `datasources` instead) A concrete instance
            of the `BaseSource` object.
        datasources: The list of datasources to be associated and registered with
            this pod. Each will have their own data config and schema (although
            not necessarily present at this point).
        username: Username of the user who is registering the pod. Defaults to None.
        data_config: (Deprecated, use `datasources` instead) Configuration for the
            data. Defaults to None.
        schema: (Deprecated, use `datasources` instead) Schema for the data. This
            can be a `BitfountSchema` object or a Path to a serialized
            `BitfountSchema`. This will be generated automatically if not provided.
            Defaults to None.
        pod_details_config: (Deprecated, use `datasources` instead) Configuration for
            the pod details. Defaults to None.
        hub: Bitfount Hub to register the pod with. Defaults to None.
        message_service: Configuration for the message service. Defaults to None.
        access_manager: Access manager to use for checking access. Defaults to None.
        pod_keys: Keys for the pod. Defaults to None.
        approved_pods: list of other pod identifiers this pod is happy
            to share a training task with. Required if the protocol uses the
            `SecureAggregator` aggregator.
        differential_privacy: Differential privacy configuration for the pod.
            Defaults to None.
        pod_db: Whether the results should be stored in a database. Defaults to False.
            If argument is set to True, then a SQLite database will be created for the
            pod in order to enable results storage for protocols that return them.
            It also keeps track of the pod datapoints so any repeat task is ran
            only on new datapoints.
        update_schema: Whether the schema needs to be re-generated even if provided.
            Defaults to False.
        secrets: Secrets for authenticating with Bitfount services.
            If not provided then an interactive flow will trigger for authentication.

    Attributes:
        datasources: The set of datasources associated with this pod.
        name: Name of the pod.
        pod_identifier: Identifier of the pod.
        private_key: Private key of the pod.

    Raises:
        PodRegistrationError: If the pod could not be registered for any reason.
        DataSourceError: If the `BaseSource` for the provided datasource has
            not been initialised properly. This can be done by calling
            `super().__init__(**kwargs)` in the `__init__` of the DataSource.
    """

    @on_pod_init_error
    def __init__(
        self,
        name: str,
        datasource: Optional[BaseSource] = None,
        datasources: Optional[Iterable[DatasourceContainerConfig]] = None,
        username: Optional[str] = None,
        data_config: Optional[PodDataConfig] = None,
        schema: Optional[Union[str, os.PathLike, BitfountSchema]] = None,
        pod_details_config: Optional[PodDetailsConfig] = None,
        hub: Optional[BitfountHub] = None,
        message_service: Optional[MessageServiceConfig] = None,
        access_manager: Optional[BitfountAM] = None,
        pod_keys: Optional[RSAKeyPair] = None,
        approved_pods: Optional[list[str]] = None,
        differential_privacy: Optional[DPPodConfig] = None,
        pod_db: Union[bool, PodDbConfig] = False,
        update_schema: bool = False,
        secrets: Optional[
            APIKeys
            | ExternallyManagedJWT
            | dict[SecretsUse, APIKeys | ExternallyManagedJWT]
        ] = None,
    ):
        for hook in get_hooks(HookType.POD):
            hook.on_pod_init_start(self, pod_name=name, username=username)

        self._prefect_unavailable = False
        if not SchemaManagement.is_prefect_server_healthy():
            logger.warning(
                "Prefect server is not running. "
                "Schema generation tasks will not be able to run."
            )
            self._prefect_unavailable = True

        self.name = name

        self._pod_details_config = (
            pod_details_config
            if pod_details_config is not None
            else self._get_default_pod_details_config()
        )
        self.project_db_connector: Optional[ProjectDbConnector] = (
            ProjectDbConnector(pod_db.path)
            if isinstance(pod_db, PodDbConfig)
            else (ProjectDbConnector() if pod_db is True else None)
        )

        base_datasource_configs = self._process_datasource_args(
            datasources=datasources,
            datasource=datasource,
            pod_name=name,
            datasource_details=self._pod_details_config,
            data_config=data_config,
            schema=schema,
        )
        # Establish Bitfount Hub and access manager connection details
        for hook in get_hooks(HookType.POD):
            hook.on_pod_init_progress(self, "Establishing connection with Hub")

        self._hub = (
            hub
            if hub is not None
            else _create_bitfounthub(
                username=username, secrets=get_secrets_for_use(secrets, "bitfount")
            )
        )
        self._username = username
        self._secrets = secrets
        self._session = self._hub.session
        self._access_manager = (
            access_manager
            if access_manager is not None
            else _create_access_manager(self._session)
        )
        self._access_manager_public_key = self._access_manager.get_access_manager_key()
        self.pod_identifier = f"{self._session.username}/{self.name}"

        # Start processing dataset configurations
        for hook in get_hooks(HookType.POD):
            hook.on_pod_init_progress(
                self,
                "Processed configurations",
                base_datasource_names=list(ds.name for ds in base_datasource_configs),
            )

        # Check for the presence of any uninitialised datasources
        maybe_uninitialised_datasource = next(
            (
                dsc
                for dsc in base_datasource_configs
                if isinstance(dsc.datasource, BaseSource)  # TODO: [BIT-3358]
                and not dsc.datasource.is_initialised
            ),
            None,
        )
        if maybe_uninitialised_datasource is not None:
            raise DataSourceError(
                f"The {maybe_uninitialised_datasource} datasource provided has not "
                "initialised the BaseSource parent class. Please make sure "
                "that you call `super().__init__(**kwargs)` in your child method."
            )
        # Load schemas if necessary and save ready to use datasources
        self.base_datasources: dict[str, DatasourceContainer] = {
            ds.name: self._load_basesource_schema_if_necessary(ds, update_schema)
            for ds in base_datasource_configs
        }
        # Get RSA keys for pod
        self.private_key, self.pod_public_key = self._get_default_pod_keys(pod_keys)

        # Establish identifiers for datasets
        # and ensure these are added to the auto-approved "pods" list
        dataset_identifiers = [
            f"{self._session.username}/{ds_name}" for ds_name in self.datasources.keys()
        ]
        if approved_pods is None:
            approved_pods = []
        approved_pods = _check_and_update_pod_ids(
            [*approved_pods, *dataset_identifiers], self._hub
        )
        self.approved_pods = approved_pods

        self._pod_dp = differential_privacy
        self._pod_vitals = _PodVitals()
        # Connecting the pod to the message service must happen AFTER registering
        # it on the hub as the message service uses hub information to verify that
        # the relevant message queue is available.
        try:
            # For now, we register the datasources as logical pods
            for ds in self.datasources.values():
                public_metadata = self._get_public_metadata(ds, bool(self._pod_dp))
                hub_upload_config = MinimalSchemaUploadConfig(
                    public_metadata=public_metadata,
                    access_manager_public_key=self._access_manager_public_key,
                    pod_public_key=self.pod_public_key,
                )
                _register_dataset(hub_upload_config, self._hub)
        except PodRegistrationError as pre:
            _handle_fatal_error(pre, logger=logger)

        self._ms_config: Optional[MessageServiceConfig] = message_service
        self._mailbox: Optional[_PodMailbox] = None

        # Marker for when initialization is complete
        self._initialised: bool = False

        for hook in get_hooks(HookType.POD):
            hook.on_pod_init_end(self)

    @property
    def datasources(self) -> dict[str, DatasourceContainer]:
        """Dictionary of base datasources."""
        return {
            **self.base_datasources,
        }

    @property
    def name(self) -> str:
        """Pod name property."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Validate Pod's name matches POD_NAME_REGEX."""
        if _name := POD_NAME_REGEX.fullmatch(name):
            self._name = _name.string
        else:
            raise PodNameError(
                f"Invalid Pod name: {name}. "
                f"Pod names must match: {POD_NAME_REGEX.pattern}"
            )

    @property
    def datasource(self) -> Optional[DatasourceContainer]:
        """If there is only a single datasource, this is a shorthand for retrieving it.

        If there is more than one datasource (or no datasources) this will log a
        warning and return None.
        """
        if (num_datasources := len(self.datasources)) > 1:
            logger.warning(
                f"Pod has {num_datasources} datasources;"
                f" unable to extract with Pod.datasource property."
            )
            return None
        elif num_datasources < 1:
            logger.warning(
                "Pod has no datasources configured;"
                " unable to extract with Pod.datasource property."
            )
            return None

        # Otherwise we have exactly one datasource
        return list(self.datasources.values())[0]

    @property
    def datasources_needing_schema_generation(self) -> dict[str, DatasourceContainer]:
        """Dictionary of datasources that need schema generation.

        Filters out datasources with pre-defined schemas as they don't need
        schema generation through Prefect flows.
        """
        return {
            name: ds
            for name, ds in self.base_datasources.items()
            if not ds.datasource.has_predefined_schema
        }

    def _load_basesource_schema_if_necessary(
        self, ds: DatasourceContainerConfig, update_schema: bool = False
    ) -> DatasourceContainer:
        """Load schema for base datasources."""
        for hook in get_hooks(HookType.POD):
            hook.on_pod_init_progress(self, "Generating schema", ds.name)

        # Extract or generate data config
        if ds.data_config:
            data_config = ds.data_config
        else:
            data_config = PodDataConfig()
        if (
            data_config.data_split is not None
            and data_config.data_split.data_splitter == "predefined"
        ):
            # Special handling required for the splitter defined in
            # data with folder based structure
            data_splitter = DatasetSplitter.create(
                data_config.data_split.data_splitter, **data_config.data_split.args
            )
            if isinstance(ds.datasource, FileSystemIterableSourceInferrable):
                if (
                    isinstance(data_splitter, SplitterDefinedInData)
                    and data_splitter.infer_data_split_labels is True
                ):
                    # The folder structure may provide labels for the data split
                    # (i.e. train,test, validation), the class labels for the
                    # data, or both.
                    ds.datasource.infer_data_split_column_name = (
                        data_splitter.column_name
                    )
                    # We extract the split labels from the data splitter for
                    # SplitterDefinedInData
                    ds.datasource.datasplitter_labels = [
                        data_splitter.training_set_label,
                        data_splitter.validation_set_label,
                        data_splitter.test_set_label,
                    ]
                else:
                    ds.datasource.infer_data_split_column_name = False
                    ds.datasource.datasplitter_labels = None
        # Load existing schemas if needed
        schema: Optional[BitfountSchema] = None
        if ds.datasource.has_predefined_schema:
            # This is not the real schema, it's just a placeholder to avoid
            # the schema generation flow for hardcoded multitable schemas.
            # The real schema is retrieved and uploaded to the hub elsewhere in
            # the `__init__` method: `_get_public_metadata` calls `get_schema` on
            # the datasource if it has a predefined schema.
            schema = BitfountSchema(name=ds.name)

        elif ds.schema and not update_schema:
            if isinstance(ds.schema, BitfountSchema):
                schema = ds.schema
            else:
                schema = BitfountSchema.load_from_file(ds.schema)
        elif not update_schema:
            try:
                schema = get_pod_schema(
                    pod_identifier=ds.name,
                    hub=self._hub,
                )
            except Exception as ex:
                logger.debug(
                    "Failed to load schema from hub, attempting to generate new schema."
                )
                logger.debug(ex)

        schema = self._setup_schema(
            datasource_name=ds.name,
            datasource=ds.datasource,
            schema=schema,
            data_config=data_config,
            force_schema_update=update_schema,
        )
        return DatasourceContainer(
            name=ds.name,
            datasource=ds.datasource,
            datasource_details=ds.datasource_details
            or self._get_default_pod_details_config(ds.name),
            data_config=data_config,
            schema=schema,
        )

    @classmethod
    def _setup_schema(
        cls,
        datasource_name: str,
        datasource: BaseSource,
        data_config: PodDataConfig,
        schema: Optional[BitfountSchema] = None,
        force_schema_update: bool = False,
    ) -> BitfountSchema:
        """Generates dataset schema if requested or required.

        The schema will be generated if:
            - schema update was forced
            - auto-tidy is requested and datasource is not iterable
            - no schema is provided
            - schema is not populated
            - datasource name does not match the table name
            - force stypes do not have appropriate type

        Only the first batch of data is used to generate the schema in this method.
        """
        force_stypes, column_descriptions, description, ignore_cols = (
            _schema_config_migration(data_config, datasource_name)
        )
        schema_needs_regeneration = False
        if force_schema_update:
            logger.debug("Requested update of schema.")
            schema_needs_regeneration = True

        # Check schema and its attributes
        if schema is None:
            logger.debug("Schema is not provided.")
            schema_needs_regeneration = True
        else:
            if schema.name != datasource_name:
                logger.debug("Datasource name does not match schema table name.")
                schema_needs_regeneration = True

            # Check for force stypes
            if force_stypes != schema.force_stypes and force_stypes is not None:
                stype: _ForceStypeValue
                schema.force_stypes = force_stypes
                for stype, cols in force_stypes.items():
                    if stype == "image_prefix":
                        # If the stype is image_prefix,
                        # we continue in order to not re-generate
                        # the schema every time for file iterable datasets.
                        continue
                    elif stype not in schema.features.keys():
                        schema_needs_regeneration = True
                    else:
                        for col in cols:
                            if col not in schema.features[stype]:
                                schema_needs_regeneration = True

        if schema_needs_regeneration:
            schema = BitfountSchema(
                name=datasource_name,
                description=description,
                column_descriptions=cast(
                    Optional[Mapping[str, str]], column_descriptions
                ),
            )
            hook = SchemaGenerationFromYieldData(schema, ignore_cols, force_stypes)
            datasource.add_hook(hook)
            # Use required fields for initial schema if prefect server is healthy,
            # if not use partial schema (previous fast_load behaviour)
            if (
                datasource.required_fields is not None
                and len(datasource.required_fields) > 0
                and SchemaManagement.is_prefect_server_healthy()
            ):
                schema.initialize_dataless_schema(datasource.required_fields)
                if force_stypes is not None and "image_prefix" in force_stypes:
                    schema.image_prefix = force_stypes["image_prefix"]
                schema.schema_type = "empty"
            else:
                schema.generate_partial_schema(datasource=datasource)
        else:
            logger.info(f"Using user provided schema for datasource {datasource_name}.")

        if schema is None:
            raise ValueError("Schema should never be None at this point")
        return schema

    def _get_default_pod_details_config(
        self, name: Optional[str] = None
    ) -> PodDetailsConfig:
        """Get default pod details config."""
        return PodDetailsConfig(
            display_name=name or self.name, description=name or self.name
        )

    @classmethod
    def _get_public_metadata(
        cls,
        datasource_container: DatasourceContainer,
        pod_dp: bool,
        ds_add_number_of_records: bool = False,
    ) -> PodPublicMetadata:
        """Get PodPublicMetadata.

        Args:
            datasource_container: The container of the datasource to get the metadata
                for.
            pod_dp: Whether the pod has Differential Privacy enabled.
            ds_add_number_of_records: Whether the number of records for the
                datasource should be retrieved and included in the metadata.
        """
        schema = (
            datasource_container.datasource.get_schema()
            if datasource_container.datasource.has_predefined_schema
            else datasource_container.schema.to_json()
        )
        number_of_records = (
            cls._get_number_of_records(datasource_container.datasource, pod_dp)
            if ds_add_number_of_records
            else None
        )
        return PodPublicMetadata(
            datasource_container.name,
            datasource_container.datasource_details.display_name,
            datasource_container.datasource_details.description,
            schema,
            number_of_records=number_of_records,
        )

    def _get_default_pod_keys(
        self, pod_keys: Optional[RSAKeyPair]
    ) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Get default pod keys."""
        if pod_keys is None:
            user_storage_path = config.settings.paths.storage_path / _DEFAULT_USERNAME
            pod_directory = user_storage_path / "pods" / self.name
            pod_keys = _get_pod_keys(pod_directory)
        return pod_keys.private, pod_keys.public

    async def _initialise(self) -> None:
        """Initialises the pod.

        Sets any attributes that could not be created at creation time.
        """
        if not self._initialised:
            # `Optional` as may be set to `None` further down
            dataset_names: Optional[list[str]] = list(self.datasources.keys())
            # If there's only one dataset with the same name as the pod
            # then we register it as a plain old pod
            if (
                dataset_names is not None  # to assuage mypy
                and len(dataset_names) == 1
                and dataset_names[0] == self.name
            ):
                dataset_names = None

            # Create mailbox(es). Cannot be done in __init__ due to async nature.
            self._mailbox = await _create_and_connect_pod_mailbox(
                pod_name=self.name,
                session=self._session,
                ms_config=self._ms_config,
                dataset_names=dataset_names,
            )
            setup_opentelemetry_metrics(
                session=self._session,
            )

            # Set initialised state
            self._initialised = True
        else:
            logger.warning("Pod._initialise() called twice. This is not allowed.")

    def _secure_aggregation_other_workers_response(
        self, other_worker_names: MutableSequence[str]
    ) -> Optional[list[str]]:
        """Checks if secure aggregation can be performed with given other workers.

        Args:
            other_worker_names (list[str]): list of other worker names

        Returns:
            Optional[list[str]]:
                unapproved workers (if they exist in other_worker_names)
        """
        unapproved_pods = [
            worker for worker in other_worker_names if worker not in self.approved_pods
        ]
        logger.debug(
            f"Modeller requested aggregation with non-approved pods: {unapproved_pods}"
        )

        if unapproved_pods:
            logger.info(
                "Modeller requested aggregation with"
                " pods that this pod has not approved."
            )
            return unapproved_pods

        logger.debug("All pods requested by modeller for aggregation are approved.")
        return None

    def _check_for_unapproved_pods(
        self,
        pods_involved_in_task: Iterable[str],
        serialized_protocol: SerializedProtocol,
    ) -> Optional[list[str]]:
        """Returns the pods that we're not happy to work with.

        If secure aggregation has been requested then this will
        identify any pods that we've not approved.

        In any other case it returns None, as there's no concern
        around security with other pods.

        Args:
            pods_involved_in_task: A list of other pods that have been contacted by
                the modeller for this task.
            serialized_protocol: The decrypted serialized protocol portion of the task
                request.

        Returns:
            Either a list of unapproved pods or `None` if all are approved or if secure
            aggregation not in use.
        """
        unapproved_workers = None

        # Create mutable version of pods_involved_in_task
        other_pods: list[str] = list(pods_involved_in_task)

        # We don't need to check if we're approved to work with our self.
        try:
            other_pods.remove(self.pod_identifier)
        except ValueError:  # if not in list to remove
            pass

        aggregator = serialized_protocol.get("aggregator")
        if (
            aggregator
            and aggregator["class_name"] == AggregatorType.SecureAggregator.value
        ):
            logger.info(
                "Secure aggregation is in use, checking responses from other pods."
            )
            unapproved_workers = self._secure_aggregation_other_workers_response(
                other_pods
            )

        return unapproved_workers

    async def _new_task_request_handler(self, message: _BitfountMessage) -> None:
        """Called on new task request being received from message service."""
        logger.info(f"Training task request received from '{message.sender}'")
        try:
            await self._create_and_run_worker(message)
        except asyncio.TimeoutError:
            logger.info("Ready for next task...")
            return

    def _unpack_task_request(self, message: _BitfountMessage) -> _TaskRequest:
        """Unpack the task request message."""
        task_request_message = _TaskRequestMessage.deserialize(message.body)
        self._patch_task_request(task_request_message)
        auth_type = check_identity_verification_method(task_request_message.auth_type)
        authoriser_cls = _IDENTITY_VERIFICATION_METHODS_MAP[auth_type]
        return authoriser_cls.unpack_task_request(message.body, self.private_key)

    def _patch_task_request(self, task_request_message: _TaskRequestMessage) -> None:
        """Patch the task request message with default values."""
        if not hasattr(task_request_message, "project_id"):
            task_request_message.project_id = None
        if not hasattr(task_request_message, "run_on_new_data_only"):
            task_request_message.run_on_new_data_only = False
        if not hasattr(task_request_message, "batched_execution"):
            task_request_message.batched_execution = (
                config.settings.default_batched_execution
            )

    def _determine_target_data_identifiers(
        self, message: _BitfountMessage
    ) -> Tuple[str, Optional[str]]:
        """Determine the target data identifiers for the task request."""
        # This is the "pod identifier" for the logical pod representing the target
        # datasource, i.e. what the modeller will have addressed to hit this
        # datasource.
        # Will be of the form: "<pod_namespace/owner>/<datasource_name>"
        # If the requested datasource is `None` we default to assuming the
        # data_identifier is the same as the pod_identifier by passing `None`
        # through to the worker.
        datasource_name = self._extract_requested_datasource(message)
        if datasource_name:
            data_identifier = f"{self._session.username}/{datasource_name}"
            return data_identifier, data_identifier
        return self.pod_identifier, None

    def _is_compatible_datasource(
        self,
        task_request_message: _TaskRequestMessage,
        datasource_info: Tuple[
            str, BaseSource, BitfountSchema, Optional[DatasetSplitter], PodDataConfig
        ],
    ) -> bool:
        """Check if the datasource is compatible with the task request.

        Args:
            task_request_message: The task request message.
            datasource_info: Datasource information.

        Returns:
            bool: True if compatible, False otherwise.
        """
        datasource_name, datasource, *_ = datasource_info
        algorithms = task_request_message.serialized_protocol.get("algorithm")
        if algorithms is None:
            algorithms = []
        elif not isinstance(algorithms, list):
            algorithms = [algorithms]

        for algo in algorithms:
            datastructure = algo.get("datastructure") or algo.get("model", {}).get(
                "datastructure"
            )
            if not datastructure:
                continue

            compatible_ds = datastructure.get("compatible_datasources")
            if compatible_ds and type(datasource).__name__ in compatible_ds:
                return True  # Return early if compatibility is found
        return False

    def _create_worker_mailbox(
        self,
        message: _BitfountMessage,
        target_identifier: str,
        unapproved_workers: Optional[list[str]],
        task_request: _TaskRequest,
    ) -> _WorkerMailbox:
        """Create the worker mailbox."""
        # `_initialise` is always called before this method, so we can assume
        # that the mailbox is initialised. Reassuring mypy that this is True.
        assert isinstance(self._mailbox, _PodMailbox)  # nosec assert_used
        # If we are dealing with secure aggregation (and hence need inter-pod
        # communication) we create an appropriate mailbox as long as there are no
        # unapproved workers.
        # If there are, the task will be rejected, so we can just create a normal
        # mailbox (as don't need inter-pod communication to reject the task).
        # Similarly, if we're not using secure aggregation we just create a normal
        # mailbox as inter-pod communication won't be needed.
        if _is_secure_share_task_request(task_request) and not unapproved_workers:
            logger.debug("Creating mailbox with inter-pod support.")
            return _InterPodWorkerMailbox(
                pod_public_keys=_get_pod_public_keys(
                    [
                        pod
                        for pod in message.pod_mailbox_ids
                        if pod != target_identifier
                    ],
                    self._hub,
                ),
                private_key=self.private_key,
                pod_identifier=target_identifier,
                modeller_mailbox_id=message.sender_mailbox_id,
                modeller_name=message.sender,
                aes_encryption_key=task_request.aes_key,
                message_service=self._mailbox.message_service,
                pod_mailbox_ids=message.pod_mailbox_ids,
                task_id=message.task_id,
            )
        logger.debug("Creating modeller<->worker-only mailbox.")
        return _WorkerMailbox(
            pod_identifier=target_identifier,
            modeller_mailbox_id=message.sender_mailbox_id,
            modeller_name=message.sender,
            aes_encryption_key=task_request.aes_key,
            message_service=self._mailbox.message_service,
            pod_mailbox_ids=message.pod_mailbox_ids,
            task_id=message.task_id,
        )

    async def _get_latest_partial_schemas(self) -> None:
        """Get the latest partial schemas for all datasources."""
        for datasource_name, datasource_container in self.base_datasources.items():
            if datasource_container.schema.schema_type == "partial":
                try:
                    schema = get_pod_schema(
                        pod_identifier=datasource_name, hub=self._hub
                    )
                    datasource_container.schema = schema
                except Exception as ex:
                    logger.error(
                        f"Failed to load schema for datasource {datasource_name}: {ex}"
                    )

    async def _reject_incompatible_task(
        self,
        worker_mailbox: _WorkerMailbox,
        message: _BitfountMessage,
        target_identifier: str,
        datasource_info: Tuple[
            str, BaseSource, BitfountSchema, Optional[DatasetSplitter], PodDataConfig
        ],
    ) -> None:
        """Reject the task due to incompatible datasource.

        Args:
            worker_mailbox: The worker mailbox.
            message: The incoming message.
            target_identifier: The target identifier.
            datasource_info: Datasource information.
        """
        datasource_name, datasource, *_ = datasource_info
        logger.info(
            f"Task from '{message.sender}' rejected as the datasource "
            f"'{datasource_name}' is is not compatible with the task."
        )
        error = _PodResponseMessage(message.sender, target_identifier)
        error.add(_PodResponseType.INCOMPATIBLE_DATASOURCE)
        await worker_mailbox.reject_task(error.messages)

    def _initialize_worker(
        self,
        task_request_message: _TaskRequestMessage,
        task_request: _TaskRequest,
        datasource_info: Tuple[
            str, BaseSource, BitfountSchema, Optional[DatasetSplitter], PodDataConfig
        ],
        worker_mailbox: _WorkerMailbox,
        authorisation_checker: _AuthorisationChecker,
        data_identifier: Optional[str],
        sender: str,
        multi_pod_task: bool,
    ) -> _Worker:
        """Initialize the worker instance.

        Args:
            task_request_message: The task request message.
            task_request: The unpacked task request.
            datasource_info: Datasource information.
            worker_mailbox: The worker mailbox.
            authorisation_checker: Authorisation checker.
            data_identifier: Data identifier.
            sender: The sender's username.
            multi_pod_task: Whether the task is a multi-pod task.

        Returns:
            Any: The initialized worker instance.
        """
        datasource_name, datasource, schema, data_splitter, data_config = (
            datasource_info
        )

        # Schema requirements check
        schema_requirements = (
            self._extract_datastructure_requirements_from_task_request(
                task_request_message, type(datasource).__name__
            )
        )
        update_schema = False
        update_schema_level = schema_requirements
        schema_kwargs = {
            "force_stypes": data_config.force_stypes,
            "ignore_cols": data_config.ignore_cols,
        }
        if schema_requirements != schema.schema_type:
            if schema_requirements == "full":
                logger.info(
                    f"Task from '{sender}' requires full schema. "
                    f"Full schema will be generated for '{datasource_name}'."
                )
                update_schema = True
                update_schema_level = "full"

            elif schema_requirements == "partial" and schema.schema_type != "full":
                # This should cover cases where schema is partial or full
                # and the required schema level is `partial`.
                logger.info(
                    f"Task from '{sender}' requires partial schema. "
                    f"Partial schema will be generated for '{datasource_name}'."
                )
                update_schema = True
                update_schema_level = "partial"
            elif schema_requirements == "empty":
                pass  # No schema update required

        return _Worker(
            datasource=datasource,
            datasource_name=datasource_name,
            schema=schema,
            mailbox=worker_mailbox,
            bitfounthub=self._hub,
            authorisation=authorisation_checker,
            parent_pod_identifier=self.pod_identifier,
            data_identifier=data_identifier,
            serialized_protocol=task_request.serialized_protocol,
            data_splitter=data_splitter,
            pod_vitals=self._pod_vitals,
            pod_dp=self._pod_dp,
            project_db_connector=self.project_db_connector,
            project_id=task_request_message.project_id,
            run_on_new_data_only=task_request_message.run_on_new_data_only,
            batched_execution=task_request_message.batched_execution,
            multi_pod_task=multi_pod_task,
            update_schema=update_schema,
            update_schema_level=update_schema_level,
            schema_kwargs=schema_kwargs,
            test_run=task_request_message.test_run,
            force_rerun_failed_files=task_request_message.force_rerun_failed_files,
            secrets=self._secrets,
        )

    async def _run_worker_task(
        self,
        worker: _Worker,
        worker_mailbox: _WorkerMailbox,
        sender: str,
        project_id: Optional[str],
        protocol_name: str,
    ) -> None:
        """Run the worker task.

        Args:
            worker: The worker instance.
            worker_mailbox: The worker mailbox.
            sender: The sender's username.
            project_id: The project ID.
            protocol_name: The protocol name.
        """
        # Extract save_path from underlying algorithm if present
        # (most likely CSV algorithm) and pass it to the hook
        # so that other hooks have access to the directory where
        # the results should be saved.
        save_path = None
        algorithm = worker.serialized_protocol.get("algorithm", [])
        if not isinstance(algorithm, list):
            algorithm = [algorithm]

        for algo in algorithm:
            if isinstance(algo, dict) and "save_path" in algo:
                save_path = algo["save_path"]
                break

        # worker.run can't handle primary_results_path being in
        # the task protocol so need to remove it here
        primary_results_path = worker.serialized_protocol.pop(
            "primary_results_path", None
        )

        for hook in get_hooks(HookType.POD):
            hook.on_task_start(
                self,
                task_id=worker_mailbox.task_id,
                project_id=project_id,
                modeller_username=sender,
                protocol_name=protocol_name,
                save_path=save_path,
                primary_results_path=primary_results_path,
                dataset_name=worker.datasource_name,
            )
        try:
            await _run_func_and_listen_to_mailbox(worker.run(), worker_mailbox)
        except Exception as e:
            logger.exception(e)
            for hook in get_hooks(HookType.POD):
                hook.on_task_error(
                    self, e, task_id=worker_mailbox.task_id, project_id=project_id
                )
        finally:
            for hook in get_hooks(HookType.POD):
                hook.on_task_end(self, task_id=worker_mailbox.task_id)

    def _setup_task_monitor_context(
        self, worker_mailbox: _WorkerMailbox
    ) -> AbstractContextManager:
        """Set up task monitoring context manager.

        Args:
            worker_mailbox: The worker mailbox.

        Returns:
            AbstractContextManager: The task monitoring context.
        """
        if worker_mailbox.task_id:
            return task_monitor_context(
                hub=self._hub,
                task_id=worker_mailbox.task_id,
                sender_id=worker_mailbox.mailbox_id,
            )
        return nullcontext()

    def _finalize_worker_task(
        self,
        datasource_info: Tuple[
            str, BaseSource, BitfountSchema, Optional[DatasetSplitter], PodDataConfig
        ],
        task_succeeded: bool,
    ) -> None:
        """Finalize the worker task by updating the schema and cleanup.

        Args:
            datasource_info: The packed datasource information.
            task_succeeded: Whether the task succeeded or not.
        """
        datasource_name, datasource, schema, *_ = datasource_info
        datasource.is_task_running = False
        if datasource_container := self.base_datasources.get(datasource_name):
            if not datasource_container.datasource.has_predefined_schema:
                logger.debug(f"Updating schema for {datasource_name}")
                datasource_container.schema = schema
                self._register_schema(
                    datasource_container,
                    # Only want to include the records on a successful task run,
                    # as requires an iteration of the files for the datasource,
                    # something we want to avoid on a task failure so that we can return
                    # to a "Ready for next task" state as quickly as possible.
                    ds_add_number_of_records=task_succeeded,
                )

    async def _create_and_run_worker(self, message: _BitfountMessage) -> None:
        """Creates and runs a worker instance."""
        # `_initialise` is always called before this method, so we can assume
        # that the mailbox is initialised. Reassuring mypy that this is True.
        assert isinstance(self._mailbox, _PodMailbox)  # nosec assert_used

        # Unpack task details from received message
        logger.info("Unpacking task details from message...")
        task_request = self._unpack_task_request(message)

        task_request_message: _TaskRequestMessage = _TaskRequestMessage.deserialize(
            message.body
        )

        project_id = task_request_message.project_id
        key_id = task_request_message.key_id

        target_identifier, data_identifier = self._determine_target_data_identifiers(
            message
        )

        # If we are using secure aggregation we check for unapproved workers; if
        # we are not, `unapproved_workers` will be `None`.
        other_pods = [
            pod_id for pod_id in message.pod_mailbox_ids if pod_id != target_identifier
        ]
        unapproved_workers = self._check_for_unapproved_pods(
            other_pods, task_request.serialized_protocol
        )

        worker_mailbox = self._create_worker_mailbox(
            message, target_identifier, unapproved_workers, task_request
        )
        # TODO: [BIT-1045] Move the secure aggregation allowed check to the access
        #       manager once we support configuring or storing it there.
        if unapproved_workers:
            # There are pods we're explicitly not happy to work with (i.e. we're
            # using secure aggregation) we reject the task.
            logger.info(f"Task from '{message.sender}' rejected.")
            authorisation_errors = _PodResponseMessage(
                message.sender, target_identifier
            )
            authorisation_errors.add(
                _PodResponseType.NO_ACCESS,
                unapproved_workers,
            )
            await worker_mailbox.reject_task(authorisation_errors.messages)
            return

        # Suspend the schema generation process until the task is over
        if not self._prefect_unavailable:
            SchemaManagement.stop_prefect_flow()

        # Get latest schemas from the hub for partial schemas
        await self._get_latest_partial_schemas()
        logger.debug("Creating authorisation checker.")
        authorisation_checker = self._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=message.sender,
            worker_mailbox=worker_mailbox,
            # not sure of a better way to get the "logical" pod identifier
            target_pod_identifier=f"{message.recipient}/{message.recipient_mailbox_id}",
            project_id=project_id,
            key_id=key_id,
        )

        # Establish worker datasource and schema
        logger.debug("Creating worker.")
        worker_datasource_info = self._get_target_datasource(message)
        # Check if the datasource is compatible with the task request
        if not self._is_compatible_datasource(
            task_request_message, worker_datasource_info
        ):
            await self._reject_incompatible_task(
                worker_mailbox, message, target_identifier, worker_datasource_info
            )
            return

        worker = self._initialize_worker(
            task_request_message,
            task_request,
            worker_datasource_info,
            worker_mailbox,
            authorisation_checker,
            data_identifier,
            message.sender,
            bool(other_pods),
        )

        task_monitor_cm = self._setup_task_monitor_context(worker_mailbox)
        try:
            with task_monitor_cm:
                await self._run_worker_task(
                    worker,
                    worker_mailbox,
                    message.sender,
                    task_request_message.project_id,
                    task_request_message.serialized_protocol.get("class_name", ""),
                )
        except Exception as e:
            logger.exception("Exception whilst running task", exc_info=e)
            self._finalize_worker_task(worker_datasource_info, task_succeeded=False)
        else:
            self._finalize_worker_task(worker_datasource_info, task_succeeded=True)

        if not self._prefect_unavailable:
            hub_config = HubConfig(
                username=self._username,
                secrets=get_secrets_for_use(self._secrets, "bitfount"),
            )
            # Resume the schema generation flow if it was suspended
            SchemaManagement.start_prefect_flow(
                base_datasources=self.datasources_needing_schema_generation,
                hub_config=hub_config,
                pod_public_key=self.pod_public_key,
                _access_manager_public_key=self._access_manager_public_key,
            )

        logger.info("Ready for next task...")

    def _extract_datastructure_requirements_from_task_request(
        self, task_request_message: _TaskRequestMessage, datasource_type: str
    ) -> str:
        """Extract the schema requirements.

        Extract the schema requirements from the task request message,
        and datasource type. This returns the most complete schema requirement
        from all the algorithms in the task request message.

        Args:
            task_request_message: The task request message.
            datasource_type: The type of the datasource.

        Returns:
            The most complete schema requirement from the task request message.
        """
        # Define the priority order for schema requirements.
        priority_order = {"empty": 0, "partial": 1, "full": 2}

        # Default schema requirement is "none".
        most_complete_requirement = "empty"

        # Retrieve algorithms from the task request message.
        algorithms = task_request_message.serialized_protocol.get("algorithm")
        if algorithms is None:
            algorithms = []
        elif not isinstance(algorithms, list):
            algorithms = [algorithms]

        # Iterate through algorithms to find the most complete schema requirement.
        for algo in algorithms:
            datastructure = algo.get("datastructure") or algo.get("model", {}).get(
                "datastructure"
            )
            if not datastructure:
                continue

            schema_reqs = datastructure.get("schema_requirements")
            if schema_reqs:
                for key, values in schema_reqs.items():
                    if (
                        datasource_type in values
                        and priority_order[key]
                        > priority_order[most_complete_requirement]
                    ):
                        most_complete_requirement = key

                        # Break early if we find the highest priority "full".
                        if most_complete_requirement == "full":
                            return most_complete_requirement

        return most_complete_requirement

    def _register_schema(
        self,
        datasource_container: DatasourceContainer,
        ds_add_number_of_records: bool = False,
    ) -> None:
        """Updates the schema corresponding to the given datasource name.

        Args:
            datasource_container: The datasource container to update the schema for.
            ds_add_number_of_records: Whether to add the number of records to
                the schema.
        """
        logger.info(f"Updating schema for {datasource_container.name}")

        # Update the schema on the hub
        try:
            public_metadata = self._get_public_metadata(
                datasource_container,
                bool(self._pod_dp),
                ds_add_number_of_records=ds_add_number_of_records,
            )
            hub_upload_config = MinimalSchemaUploadConfig(
                public_metadata=public_metadata,
                pod_public_key=self.pod_public_key,
                access_manager_public_key=self._access_manager_public_key,
            )
            _register_dataset(hub_upload_config, self._hub)
        except PodRegistrationError as pre:
            _handle_fatal_error(pre, logger=logger)

        self.base_datasources[datasource_container.name] = datasource_container

    @staticmethod
    def _get_number_of_records(datasource: BaseSource, pod_dp: bool) -> Optional[int]:
        """Gets the number of records in the datasource.

        Args:
            datasource: The datasource to get the number of records for. The type of
                this argument matches the type of the datasource in
                `DatasourceContainerConfig`.
            pod_dp: Whether the pod has differential privacy enabled.

        Returns:
            The number of records in the datasource if it is a BaseSource and
            differential privacy is not enabled. Otherwise, returns None.
        """
        try:
            number_of_records = (
                len(datasource)
                if isinstance(datasource, BaseSource) and not pod_dp
                else None
            )
        except Exception:
            return None

        return number_of_records

    def _create_authorisation_checker(
        self,
        task_request_message: _TaskRequestMessage,
        sender: str,
        worker_mailbox: _WorkerMailbox,
        target_pod_identifier: str,
        project_id: Optional[str] = None,
        key_id: Optional[str] = None,
    ) -> _AuthorisationChecker:
        """Create appropriate Authorisation Checker.

        Determines checker to create based on supplied auth_type.

        Args:
            task_request_message: The full task request message.
            sender: The sender (i.e. modeller) of the request.
            worker_mailbox: Worker mailbox for communication with modeller.
            target_pod_identifier: The pod identifier of the target pod.
            project_id: Optional. The project ID associated with the task. Used
                to verify project-based access.
            key_id: Optional. The key ID associated with the task. Used to verify
                key-based access.

        Returns:
            An authorisation checker.
        """
        auth_type: IdentityVerificationMethod = check_identity_verification_method(
            task_request_message.auth_type
        )
        authorisation_checker_cls = _IDENTITY_VERIFICATION_METHODS_MAP[auth_type]

        task_request = authorisation_checker_cls.unpack_task_request(
            task_request_message, self.private_key
        )
        serialized_protocol = task_request.serialized_protocol
        # Remove schema to reduce latency when checking access with the Access Manager
        # since it is the largest task element.
        algorithm = serialized_protocol["algorithm"]
        if not isinstance(serialized_protocol["algorithm"], list):
            algorithm = [cast(SerializedAlgorithm, algorithm)]

        algorithm = cast(list[SerializedAlgorithm], algorithm)
        for algo in algorithm:
            try:
                algo["model"].pop("schema", None)
            except KeyError:
                pass

        pod_response_message = _PodResponseMessage(
            modeller_name=sender,
            pod_identifier=target_pod_identifier,
        )

        authorisation_checker: _AuthorisationChecker

        if auth_type == IdentityVerificationMethod.KEYS:
            # Public Key Signature authorisation
            packed_request: _SignedEncryptedTaskRequest = (
                authorisation_checker_cls.extract_from_task_request_message(
                    task_request_message
                )
            )

            authorisation_checker = _SignatureBasedAuthorisation(
                pod_response_message=pod_response_message,
                access_manager=self._access_manager,
                modeller_name=worker_mailbox.modeller_name,
                encrypted_task_request=packed_request.encrypted_request,
                signature=packed_request.signature,
                serialized_protocol=serialized_protocol,
                project_id=project_id,
                key_id=key_id,
            )
        elif auth_type == IdentityVerificationMethod.OIDC_ACF_PKCE:
            # OIDC Authorization Code Flow
            auth_env = _get_auth_environment()
            authorisation_checker = _OIDCAuthorisationCode(
                pod_response_message=pod_response_message,
                access_manager=self._access_manager,
                mailbox=worker_mailbox,
                serialized_protocol=serialized_protocol,
                project_id=project_id,
                _auth_domain=auth_env.auth_domain,
                _client_id=auth_env.client_id,
            )
        elif auth_type == IdentityVerificationMethod.OIDC_DEVICE_CODE:
            # OIDC Device Code flow
            auth_env = _get_auth_environment()
            authorisation_checker = _OIDCDeviceCode(
                pod_response_message=pod_response_message,
                access_manager=self._access_manager,
                mailbox=worker_mailbox,
                serialized_protocol=serialized_protocol,
                project_id=project_id,
                _auth_domain=auth_env.auth_domain,
                _client_id=auth_env.client_id,
            )
        else:
            # This should never happen as we have already checked the auth_type
            # is valid.
            raise ValueError(f"Unknown auth_type: {auth_type}")

        return authorisation_checker

    def _get_target_datasource(
        self, message: _BitfountMessage
    ) -> tuple[
        str, BaseSource, BitfountSchema, Optional[DatasetSplitter], PodDataConfig
    ]:
        """Extract the datasource config associated with datasource requested.

        Returns the datasource name, datasource and schema.
        """
        # Retrieve requested datasource details
        requested_datasource = self._extract_requested_datasource(message)
        if requested_datasource is None:
            target_datasource_container = None
        else:
            target_datasource_container = self.datasources.get(requested_datasource)

        # Check it is one that exists
        if target_datasource_container is None:
            logger.error(
                "Failed to start task addressed to recipient_mailbox_id="
                f"'{requested_datasource}'"
            )
            raise BitfountTaskStartError(
                "Failed to start task addressed to recipient_mailbox_id="
                f"'{requested_datasource}'"
            )
        # Get latest schema from hub
        if target_datasource_container.schema != "full":
            # Get the latest hub schema and use that one.
            try:
                target_datasource_container.schema = get_pod_schema(
                    pod_identifier=target_datasource_container.name, hub=self._hub
                )
            except Exception as ex:
                logger.debug("Failed to load schema from hub.")
                logger.debug(ex)
        # Get data split info
        data_split_config = target_datasource_container.data_config.data_split
        if data_split_config is not None:
            data_splitter = DatasetSplitter.create(
                data_split_config.data_splitter, **data_split_config.args
            )
        else:
            data_splitter = None
        return (
            target_datasource_container.name,
            target_datasource_container.datasource,
            target_datasource_container.schema,
            data_splitter,
            target_datasource_container.data_config,
        )

    def _extract_requested_datasource(self, message: _BitfountMessage) -> Optional[str]:
        """Extract the requested datasource from task request message.

        Returns `None` if the requested datasource cannot be found,
        otherwise the datasource name.
        """
        # The recipient_mailbox_id (i.e. the "pod name") on the received message will
        # actually be the dataset name as the datasets are viewed as logical pods.
        recipient_mailbox_id = message.recipient_mailbox_id
        if recipient_mailbox_id in self.datasources:
            logger.info(f"Requested datasource was {recipient_mailbox_id}")
            return recipient_mailbox_id
        else:
            logger.warning(
                f"Requested datasource was {recipient_mailbox_id}"
                f" but could not find this in datasources"
            )
            return None

    @staticmethod
    async def _repeat(
        stop_event: threading.Event, interval: int, func: Callable[..., Coroutine]
    ) -> None:
        """Run coroutine func every interval seconds.

        If func has not finished before *interval*, will run again
        immediately when the previous iteration finished.

        Args:
            stop_event: threading.Event to stop the loop
            interval: run interval in seconds
            func: function to call which returns a coroutine to await
        """
        while not stop_event.is_set():
            # Don't need to worry about gather tasks cancellation as func() (in
            # this case _pod_heartbeat()) is short running, so if one of the tasks
            # raises an exception the other won't be left running long.
            await asyncio.gather(func(), asyncio.sleep(interval))

    async def _pod_heartbeat(self) -> None:
        """Send a pod heartbeat to the hub."""
        try:
            self._hub.do_pod_heartbeat(
                list(self.datasources.keys()), self.pod_public_key
            )
        except HTTPError as ex:
            logger.warning(f"Failed to reach hub for status: {ex}")
        except RequestException as ex:
            logger.warning(f"Could not connect to hub for status: {ex}")

    def _run_pod_heartbeat_task(self, stop_event: threading.Event) -> None:
        """Makes 10-second interval pod heartbeats to the hub."""
        if is_notebook():
            # We need to create a new event loop here for jupyter
            # As it's run in a new thread and can't be patched by nest_asyncio
            asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.run(self._repeat(stop_event, 10, self._pod_heartbeat))

    def _get_pod_heartbeat_thread(self) -> _StoppableThead:
        """Returns pod heartbeat thread."""
        logger.info(f"Starting pod {self.name}...")
        thread_stop_event = threading.Event()
        pod_heartbeat = _StoppableThead(
            stop_event=thread_stop_event,
            target=self._run_pod_heartbeat_task,
            args=(thread_stop_event,),
            name="pod_heartbeat",
        )
        return pod_heartbeat

    def _run_pod_vitals_server(self) -> Optional[_PodVitalsHandler]:
        """Create _PodVitalsHandler and run _PodVitals webserver."""
        # Check that we have not initialized the Pod from a notebook
        if not is_notebook():
            # Setup pod vitals webserver
            logger.debug("Starting Pod Vitals interface...")
            vitals_handler = _PodVitalsHandler(
                self._pod_vitals,
                {ds_name: ds.schema for ds_name, ds in self.datasources.items()},
            )
            vitals_handler.start(thread_name="pod_vitals_interface", daemon=True)
            return vitals_handler
        else:
            return None

    async def start_async(self) -> None:
        """Starts a pod instance, listening for tasks.

        Whenever a task is received, a worker is created to handle it. Runs continuously
        and asynchronously orchestrates training whenever a task arrives i.e. multiple
        tasks can run concurrently.
        """
        for hook in get_hooks(HookType.POD):
            hook.on_pod_startup_start(self)
        # Do post-init initialization work
        await self._initialise()

        # `_initialise` has just been called which sets the mailbox so we can assume
        # that the mailbox is initialised. Reassuring mypy that this is True.
        assert isinstance(self._mailbox, _PodMailbox)  # nosec assert_used

        # Placeholders for elements that need shutdown
        pod_heartbeat: Optional[_StoppableThead] = None
        vitals_handler: Optional[_PodVitalsHandler] = None

        try:
            # Setup heartbeat to hub
            pod_heartbeat = self._get_pod_heartbeat_thread()
            pod_heartbeat.start()

            # Start pod vitals webserver
            vitals_handler = self._run_pod_vitals_server()

            # Attach handler for new tasks
            self._mailbox.register_handler(
                _BitfountMessageType.JOB_REQUEST,
                self._new_task_request_handler,
            )

            for hook in get_hooks(HookType.POD):
                hook.on_pod_startup_end(self)

            # Start pod listening for messages
            logger.info("Pod started... press Ctrl+C to stop")
            if not self._prefect_unavailable:
                logger.info("Starting schema generation in separate process")
                hub_config = HubConfig(
                    username=self._username,
                    secrets=get_secrets_for_use(self._secrets, "bitfount"),
                )
                SchemaManagement.start_prefect_flow(
                    base_datasources=self.datasources_needing_schema_generation,
                    hub_config=hub_config,
                    pod_public_key=self.pod_public_key,
                    _access_manager_public_key=self._access_manager_public_key,
                )
            # Mark as ready in the pod vitals, even if we're not using the handler
            self._pod_vitals.mark_pod_ready()

            await self._mailbox.listen_indefinitely()

        finally:
            for hook in get_hooks(HookType.POD):
                hook.on_pod_shutdown_start(self)

            logger.info(f"Pod {self.name} stopped.")

            # Shutdown pod heartbeat thread
            if pod_heartbeat:
                pod_heartbeat.stop()
                logger.debug(
                    f"Waiting up to "
                    f"{config.settings.pod_heartbeat_shutdown_timeout} seconds"
                    f" for pod heartbeat thread to stop"
                )
                pod_heartbeat.join(config.settings.pod_heartbeat_shutdown_timeout)
                if pod_heartbeat.stopped:
                    logger.debug("Shut down pod heartbeat thread")
                else:
                    logger.error("Unable to shut down pod heartbeat thread")
            if not self._prefect_unavailable:
                SchemaManagement.stop_prefect_flow()
            # Shutdown pod vitals webserver
            if vitals_handler:
                try:
                    logger.debug(
                        f"Waiting up to"
                        f" {config.settings.pod_vitals_handler_shutdown_timeout}"
                        f" seconds for pod vitals server thread to stop"
                    )
                    vitals_handler.stop(
                        config.settings.pod_vitals_handler_shutdown_timeout
                    )
                except Exception as e:
                    logger.warning(f"Error stopping pod vitals server: {str(e)}")
                else:
                    logger.debug("Shut down vitals handler thread")

            for hook in get_hooks(HookType.POD):
                hook.on_pod_shutdown_end(self)

    @on_pod_startup_error
    def start(self) -> None:
        """Starts a pod instance, listening for tasks.

        Whenever a task is received, a worker is created to handle it. Runs continuously
        and asynchronously orchestrates training whenever a task arrives i.e. multiple
        tasks can run concurrently.
        """
        asyncio.run(self.start_async())

    def _process_datasource_args(
        self,
        *,
        # New-format datasources
        datasources: Optional[Iterable[DatasourceContainerConfig]] = None,
        # Old-format datasource
        datasource: Optional[BaseSource] = None,
        # Old-format datasource: needed
        pod_name: Optional[str] = None,
        datasource_details: Optional[PodDetailsConfig] = None,
        # Old-format datasource: truly optional
        data_config: Optional[PodDataConfig] = None,
        schema: Optional[Union[str, os.PathLike, BitfountSchema]] = None,
    ) -> list[DatasourceContainerConfig]:
        """Load supplied datasources into expected format by datasource type.

        Handles deprecation and incompatible specifications.
        """
        # Can EITHER have `datasource` or `datasources`, not both
        if datasource and datasources:
            raise ValueError(
                "Only one of `datasource` and `datasources` can be specified."
            )

        # One of `datasource` and `datasources` MUST BE specified
        if not datasource and not datasources:
            raise ValueError("One of `datasource` and `datasources` must be specified.")

        # `data_config` and `schema` are ONLY compatible with `datasources`
        if (data_config or schema) and not datasource:
            raise ValueError(
                "If using `data_config` or `schema`, must supply `datasource`."
            )

        # Old-format datasource _needs_ the pod name and datasource details
        if datasource and not (pod_name and datasource_details):
            raise ValueError(
                "When supplying `datasource`,"
                " `pod_name` and `datasource_details` are required."
            )

        if datasources:
            # do data config migration
            for ds in datasources:
                if ds.data_config is not None:
                    force_stypes, column_descriptions, description, ignore_cols = (
                        _schema_config_migration(ds.data_config, ds.name)
                    )
                    ds.data_config.force_stypes = force_stypes
                    ds.data_config.column_descriptions = column_descriptions
                    ds.data_config.description = description
                    ds.data_config.ignore_cols = ignore_cols

            # Establish subclasses of BaseSource. We to this here even though
            # the `self.base_datasources` is an arg for the class as it is
            # set later in the class init
            base_datasources = {
                ds.name: ds
                for ds in datasources
                if isinstance(ds.datasource, BaseSource)
            }

            # Make sure that the data cache is correctly enabled based
            # on the environment variable
            if config.settings.enable_data_cache is True:
                logger.info(
                    "Enabling data cache for "
                    "datasources as per environment variable "
                    "`BITFOUNT_ENABLE_DATA_CACHE`."
                )
                for ds_name, ds in base_datasources.items():
                    if isinstance(ds.datasource, FileSystemIterableSource):
                        if ds.datasource.data_cache is None:
                            config.settings.paths.dataset_cache_dir.mkdir(
                                parents=True, exist_ok=True
                            )
                            data_persister_path = (
                                config.settings.paths.dataset_cache_dir
                                / f"{ds_name}_cache.sqlite"
                            ).resolve()
                            logger.info(
                                f'Creating/retrieving cache for dataset "{ds_name}"'
                                f" at {data_persister_path}"
                            )
                            ds.datasource.data_cache = SQLiteDataPersister(
                                data_persister_path
                            )

            return list(base_datasources.values())
        else:  # if datasource
            warnings.warn(
                "Single `datasource` specification will be replaced"
                " with `datasources` in future versions",
                DeprecationWarning,
                stacklevel=2,
            )

            # Logic above should capture the need for these to be not `None` if
            # using singular `datasource`, these are primarily to mass persuade
            # mypy that this is the case
            assert datasource is not None  # nosec assert_used
            assert pod_name is not None  # nosec assert_used
            assert datasource_details is not None  # nosec assert_used
            if data_config is not None:
                force_stypes, column_descriptions, description, ignore_cols = (
                    _schema_config_migration(data_config, pod_name)
                )
                data_config.force_stypes = force_stypes
                data_config.column_descriptions = column_descriptions
                data_config.description = description
                data_config.ignore_cols = ignore_cols
            # Create wrapper DataSourceContainer object around direct datasource
            # Uses pod name as datasource name.
            return [
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource=datasource,
                    datasource_details=datasource_details,
                    data_config=data_config,
                    schema=schema,
                )
            ]


def _schema_config_migration(
    data_config: PodDataConfig, datasource_name: str
) -> tuple[
    Optional[dict[Union[_ForceStypeValue, _SemanticTypeValue], list[str]]],
    Optional[Union[Mapping[str, Mapping[str, str]], Mapping[str, str]]],
    Optional[str],
    Optional[list[str]],
]:
    """Migrate schema configuration to new format."""
    force_stypes: Optional[dict[Union[_ForceStypeValue, _SemanticTypeValue], list[str]]]
    column_descriptions: Optional[Mapping[str, str]]
    description: Optional[str] = data_config.description
    ignore_cols: Optional[list[str]]
    if (
        data_config.force_stypes is not None
        and datasource_name in data_config.force_stypes.keys()
    ):
        force_stypes = cast(
            dict[Union[_ForceStypeValue, _SemanticTypeValue], list[str]],
            data_config.force_stypes[datasource_name],
        )
    else:
        force_stypes = cast(
            Optional[dict[Union[_ForceStypeValue, _SemanticTypeValue], list[str]]],
            data_config.force_stypes,
        )

    if (
        data_config.column_descriptions is not None
        and datasource_name in data_config.column_descriptions.keys()
    ):
        column_descriptions = cast(
            Mapping[str, str], data_config.column_descriptions[datasource_name]
        )
    else:
        column_descriptions = cast(
            Optional[Mapping[str, str]], data_config.column_descriptions
        )
    if (
        data_config.table_descriptions is not None
        and datasource_name in data_config.table_descriptions
        and description is not None
    ):
        description = data_config.table_descriptions[datasource_name]

    if (
        data_config.ignore_cols is not None
        and not isinstance(data_config.ignore_cols, list)
        and datasource_name in data_config.ignore_cols
    ):
        ignore_cols = data_config.ignore_cols[datasource_name]
    else:
        ignore_cols = cast(Optional[list[str]], data_config.ignore_cols)
    return force_stypes, column_descriptions, description, ignore_cols
