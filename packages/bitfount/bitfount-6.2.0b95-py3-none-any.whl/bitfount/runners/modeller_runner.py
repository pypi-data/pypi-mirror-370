"""Utility functions for running modellers from configs."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
import logging
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union, cast

import yaml

from bitfount import config
from bitfount.compatibility import validate_task_compatibility
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import BaseAlgorithmFactory
from bitfount.federated.algorithms.hugging_face_algorithms.timm_fine_tuning import (
    TIMMFineTuning,
)
from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.exceptions import AggregatorError, DPNotAppliedError
from bitfount.federated.helper import (
    _check_and_update_pod_ids,
    _create_aggregator,
    _create_message_service,
)
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.modeller import _Modeller
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.types import AlgorithmType, ProtocolType
from bitfount.federated.utils import _ALGORITHMS, _PROTOCOLS
from bitfount.hub.helper import _create_bitfounthub, get_pod_schema
from bitfount.models.base_models import _BaseModel
from bitfount.runners.config_schemas.algorithm_schemas import (
    AlgorithmConfig,
    ModelAlgorithmConfig,
)
from bitfount.runners.config_schemas.modeller_schemas import ModellerConfig, TaskConfig
from bitfount.runners.exceptions import PlugInAlgorithmError, PlugInProtocolError
from bitfount.runners.utils import dataclass_to_kwargs, get_secrets_for_use
from bitfount.types import DistributedModelProtocol

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

DEFAULT_MODEL_OUT: Path = config.settings.paths.output_dir / "output-model.pt"

logger = logging.getLogger(__name__)


def setup_modeller_from_config_file(
    path_to_config_yaml: Union[str, PathLike],
) -> tuple[_Modeller, list[str], Optional[str], bool, bool, bool, bool]:
    """Creates a modeller from a YAML config file.

    Args:
        path_to_config_yaml: the path to the config file

    Returns:
        A tuple of the created Modeller and the list of pod identifiers to run

    Raises:
        BitfountVersionError: If the task configuration is incompatible with
            the current SDK
    """
    path_to_config_yaml = Path(path_to_config_yaml)

    with open(path_to_config_yaml) as f:
        config_yaml = yaml.safe_load(f)
    # Check task compatibility and get parsed config
    context = {"config_path": path_to_config_yaml}
    config = validate_task_compatibility(config_yaml, ModellerConfig, context)
    # If we get here, the task is compatible with our schema
    return setup_modeller_from_config(config)


def setup_modeller_from_config(
    modeller_config: ModellerConfig,
) -> tuple[_Modeller, list[str], Optional[str], bool, bool, bool, bool]:
    """Creates a modeller from a loaded config mapping.

    Args:
        modeller_config: The modeller configuration.

    Returns:
        6-tuple of:
        - the created Modeller
        - the list of pod identifiers to run the task against
        - the project_id (if within a project)
        - the run_on_new_data_only boolean flag
        - the batched_execution boolean flag
        - the test_run boolean flag
    """
    # Load config details
    transformation_file = modeller_config.task.transformation_file
    if transformation_file is not None and not transformation_file.exists():
        raise FileNotFoundError("Transformation file specified but doesn't exist")

    bitfount_hub = _create_bitfounthub(
        username=modeller_config.modeller.username,
        url=modeller_config.hub.url,
        secrets=get_secrets_for_use(modeller_config.secrets, "bitfount"),
    )
    if modeller_config.batched_execution is None:
        batched_execution = config.settings.default_batched_execution
    else:
        batched_execution = modeller_config.batched_execution

    # We assume that if the user has not included a username in
    # a pod identifier that it is their own pod
    pod_identifiers: list[str] = _check_and_update_pod_ids(
        modeller_config.pods.identifiers, bitfount_hub
    )

    modeller = setup_modeller(
        pod_identifiers=pod_identifiers,
        task_details=modeller_config.task,
        bitfount_hub=bitfount_hub,
        ms_config=modeller_config.message_service,
        identity_verification_method=modeller_config.modeller.identity_verification_method,
        private_key_file=modeller_config.modeller.private_key_file,
        idp_url=modeller_config.modeller._identity_provider_url,
        project_id=modeller_config.project_id,
    )
    return (
        modeller,
        pod_identifiers,
        modeller_config.project_id,
        modeller_config.run_on_new_data_only,
        batched_execution,
        modeller_config.test_run,
        modeller_config.force_rerun_failed_files,
    )


def setup_modeller(
    pod_identifiers: list[str],
    task_details: TaskConfig,
    bitfount_hub: BitfountHub,
    ms_config: MessageServiceConfig,
    identity_verification_method: Union[
        str, IdentityVerificationMethod
    ] = IdentityVerificationMethod.DEFAULT,
    private_key_file: Optional[Path] = None,
    idp_url: Optional[str] = None,
    project_id: Optional[str] = None,
) -> _Modeller:
    """Creates a modeller.

    Args:
        pod_identifiers: The pod identifiers of the pods to be used in the task.
        task_details: The task details as a TaskConfig instance.
        bitfount_hub: The BitfountHub instance.
        ms_config: The message service settings as a MessageServiceConfig instance.
        identity_verification_method: The identity verification method to use.
        private_key_file: The path to the private key used by this modeller.
        idp_url: URL of the modeller's identity provider.
        project_id: The project ID the task belongs to.

    Returns:
        The created Modeller.
    """
    # Check validity of pod names
    if not pod_identifiers:
        raise ValueError("Must provide at least one `pod_identifier`")
    pod_identifiers = _check_and_update_pod_ids(pod_identifiers, bitfount_hub)
    try:
        # Check that the schemas of the given pods match
        # TODO: [BIT-1098] Manage pods with different schemas
        schema = get_pod_schema(
            pod_identifiers[0], hub=bitfount_hub, project_id=project_id
        )
        for pod_id in pod_identifiers[1:]:
            aux_schema = get_pod_schema(pod_id, hub=bitfount_hub, project_id=project_id)
            # We need to check that the schemas have the same contents
            if aux_schema != schema:
                raise ValueError(
                    "Pod schemas must match in order to be able to train on them."
                )
    except Exception as e:
        logger.warning(f"Error getting or validating pod schema: {e}")
        schema = None
    # Load algorithm from components
    if not isinstance(task_algorithm := task_details.algorithm, list):
        task_algorithm = [cast(AlgorithmConfig, task_details.algorithm)]

    algorithm = []
    models = []

    # Create data structure
    data_config = task_details.data_structure
    if not data_config.select.include and not data_config.select.exclude:
        # If no columns are specified, we include all columns
        data_config.select.exclude = []
    data_structure = DataStructure.create_datastructure(
        select=data_config.select,
        transform=data_config.transform,
        assign=data_config.assign,
        data_split=data_config.data_split,
        schema=schema,
        schema_requirements=data_config.schema_requirements,
        compatible_datasources=data_config.compatible_datasources,
    )
    for algo in task_algorithm:
        model: Optional[Union[_BaseModel, BitfountModelReference]] = None

        if issubclass(type(algo), ModelAlgorithmConfig) and algo.model:
            if not data_config:
                raise ValueError(
                    "If a model is provided, a data structure must be provided too."
                )

            # Create model
            model_details = algo.model

            if model_details.name:  # i.e. built-in model
                raise ValueError(
                    "Model name no longer supported. Must specify a bitfount model."
                )
            elif model_details.bitfount_model:  # i.e. custom model
                # Custom DP models not currently supported
                if model_details.dp_config:
                    raise DPNotAppliedError(
                        "Custom models cannot currently be used with"
                        " Differential Privacy."
                    )

                # We set the hyperparameters of the BitfountModelReference
                # using those from the config; allows the config format
                # to avoid duplicate hyperparameter fields.
                model = BitfountModelReference(
                    username=model_details.bitfount_model.username,
                    model_ref=model_details.bitfount_model.model_ref,
                    model_version=model_details.bitfount_model.model_version,
                    datastructure=data_structure,
                    schema=schema,
                    hyperparameters=model_details.hyperparameters,
                    hub=bitfount_hub,
                    weights=model_details.bitfount_model.weights,
                )
                model.upload_model_and_weights(project_id)
                # We call get_model here to upload it to the hub earlier in the code,
                # to help us mitigate a race condition between the pod and the modeller,
                # where the pod is trying to get the model from the hub when it has
                # not finished uploading. This has been observed in the app run case.
            else:
                raise TypeError(
                    "Unrecognised model type: should be a built-in model "
                    "or a BitfountModelReference."
                )
            models.append(model)

        # Determine algorithm class
        algorithm_cls: type[BaseAlgorithmFactory]
        try:
            # First we see if it is a built-in algorithm class
            # All built-ins start with "bitfount." so prepend if we don't have it
            algo_name_in_config = algo.name
            algo_name_to_use = algo_name_in_config
            if not algo_name_to_use.startswith("bitfount."):
                algo_name_to_use = f"bitfount.{algo_name_to_use}"

            algorithm_cls = _ALGORITHMS[AlgorithmType(algo_name_to_use).name]

            # If the algorithm was found as a built-in, but only because we
            # prepended, log a warning
            if not algo_name_in_config.startswith("bitfount."):
                logger.warning(
                    f"Algorithm {algo_name_in_config} was found"
                    f" as built-in bitfount.{algo_name_in_config};"
                    f" references to this should explicitly include"
                    f' the "bitfount." prefix.'
                )
        except ValueError:
            # If algo.name is not in AlgorithmType then we see if it is a plugin
            logger.debug(
                f"Could not find {algo.name} in built-in algorithm classes."
                f" Trying to load as plugin..."
            )
            try:
                algorithm_cls = _ALGORITHMS[algo.name]
            except KeyError as e:
                raise PlugInAlgorithmError(
                    "The specified algorithm was not found as a plugin"
                    " and is not a built-in algorithm."
                ) from e

        # Construct algorithm kwargs as needed
        additional_algo_kwargs: dict[str, Any] = dict()
        if model:
            # If we are working with a model then we must be working with
            # a model algorithm so can treat it as such
            additional_algo_kwargs.update(
                {
                    "model": model,
                    "pretrained_file": algo.pretrained_file,
                    "project_id": project_id,
                }
            )
        # Schema and datastructure already exist separately so they are not part of the
        # algorithm arguments config and must be added separately
        elif algorithm_cls == TIMMFineTuning:
            additional_algo_kwargs.update(schema=schema, datastructure=data_structure)
        # All non-model algorithms need to be passed the datastructure
        else:
            additional_algo_kwargs.update(datastructure=data_structure)

        # Build and append algorithm instance
        algo_kwargs = {}
        if isinstance(algo.arguments, dict):
            algo_kwargs.update(algo.arguments)
        elif algo.arguments is not None:
            # If `.arguments` is not a dict it's likely a nested dataclass all
            # of its own
            algo_kwargs.update(dataclass_to_kwargs(algo.arguments))

        algorithm.append(algorithm_cls(**algo_kwargs, **additional_algo_kwargs))

    # Set protocol kwargs
    protocol_kwargs = {}
    if isinstance(task_details.protocol.arguments, dict):
        protocol_kwargs.update(task_details.protocol.arguments)
    else:
        # If `.arguments` is not a dict it's likely a nested dataclass all
        # of its own
        protocol_kwargs.update(dataclass_to_kwargs(task_details.protocol.arguments))

    # Set aggregation options
    if task_details.aggregator is not None:
        if len(models) > 0:
            for model in models:
                if not isinstance(
                    model, (DistributedModelProtocol, BitfountModelReference)
                ):
                    raise TypeError(
                        "Aggregation is only compatible with models implementing "
                        "DistributedModelProtocol or BitfountModelReference instances."
                    )

        # We check early, whilst both are in scope, to ensure that, if weightings
        # have been supplied, weightings for all pods have been supplied.
        if task_details.aggregator.weights is not None:
            if (weight_pods := set(task_details.aggregator.weights.keys())) != (
                requested_pods := set(pod_identifiers)
            ):
                raise AggregatorError(
                    f"Pods in task and aggregation weightings do not match: "
                    f"{requested_pods} != {weight_pods}"
                )

        aggregator = _create_aggregator(
            secure_aggregation=task_details.aggregator.secure,
            weights=task_details.aggregator.weights,
        )
        protocol_kwargs.update({"aggregator": aggregator})

    # Load protocol from components
    try:
        # All built-ins start with "bitfount." so prepend if we don't have it
        protocol_name_in_config = task_details.protocol.name
        protocol_name_to_use = protocol_name_in_config
        if not protocol_name_to_use.startswith("bitfount."):
            protocol_name_to_use = f"bitfount.{protocol_name_to_use}"

        protocol = _PROTOCOLS[ProtocolType(protocol_name_to_use).name](
            algorithm=algorithm if len(algorithm) > 1 else algorithm[0],
            primary_results_path=task_details.primary_results_path,
            **protocol_kwargs,
        )

        # If the protocol was found as a built-in, but only because we prepended,
        # log a warning
        if not protocol_name_in_config.startswith("bitfount."):
            logger.warning(
                f"Protocol {protocol_name_in_config} was found"
                f" as built-in bitfount.{protocol_name_in_config};"
                f" references to this should explicitly include"
                f' the "bitfount." prefix.'
            )
    except ValueError:
        # Check if the protocol is a plugin
        try:
            protocol = _PROTOCOLS[task_details.protocol.name](
                algorithm=algorithm if len(algorithm) > 1 else algorithm[0],
                primary_results_path=task_details.primary_results_path,
                **protocol_kwargs,
            )
        # Raise custom error if protocol not found.
        except KeyError as e:
            raise PlugInProtocolError(
                "The specified plugin protocol was not found."
            ) from e

    # Create Modeller
    message_service = _create_message_service(
        session=bitfount_hub.session,
        ms_config=ms_config,
    )
    modeller = _Modeller(
        protocol=protocol,
        message_service=message_service,
        bitfounthub=bitfount_hub,
        identity_verification_method=identity_verification_method,
        private_key=private_key_file,
        idp_url=idp_url,
    )

    return modeller


async def run_modeller_async(
    modeller: _Modeller,
    pod_identifiers: Iterable[str],
    require_all_pods: bool = False,
    model_out: Optional[Path] = DEFAULT_MODEL_OUT,
    project_id: Optional[str] = None,
    run_on_new_data_only: bool = False,
    batched_execution: Optional[bool] = None,
    test_run: bool = False,
    force_rerun_failed_files: bool = True,
) -> Optional[Any]:
    """Runs the modeller.

    Run the modeller, submitting tasks to the pods and waiting for the results.

    Args:
        modeller: The Modeller instance being used to manage the task.
        pod_identifiers: The group of pod identifiers to run the task against.
        require_all_pods: Require all pod identifiers specified to accept the task
            request to complete task execution.
        model_out: The path to save the model out to. Defaults to "./output-model.pt".
        project_id: The project ID the task belongs to.
        run_on_new_data_only: Whether to run the task on new datapoints only.
            Defaults to False.
        batched_execution: Whether to run the task in batched mode. Defaults to False.
        test_run: Whether to run the modeller in test mode. False if `batched_execution`
            is False. Defaults to False.
        force_rerun_failed_files: If True, forces a rerun on files that
            the task previously failed on. If False, the task will skip
            files that have previously failed. Note: This option can only be
            enabled if both enable_batch_resilience and individual_file_retry_enabled
            are True. Defaults to True.

    Raises:
        PodResponseError: If require_all_pods is true and at least one pod
            identifier specified rejects or fails to respond to a task request.
    """
    # Start task running
    if batched_execution is None:
        batched_execution = config.settings.default_batched_execution
    result = await modeller.run_async(
        pod_identifiers,
        require_all_pods=require_all_pods,
        project_id=project_id,
        run_on_new_data_only=run_on_new_data_only,
        batched_execution=batched_execution,
        test_run=test_run,
        force_rerun_failed_files=force_rerun_failed_files,
    )

    if model_out:
        logger.debug(f"Saving model out to {model_out}")
        modeller._serialize(model_out)

    if result is False:
        return None

    return result


def run_modeller(
    modeller: _Modeller,
    pod_identifiers: Iterable[str],
    require_all_pods: bool = False,
    model_out: Optional[Path] = DEFAULT_MODEL_OUT,
    project_id: Optional[str] = None,
    run_on_new_data_only: bool = False,
    batched_execution: Optional[bool] = None,
    test_run: bool = False,
    force_rerun_failed_files: bool = True,
) -> Optional[Any]:
    """Runs the modeller.

    Run the modeller, submitting tasks to the pods and waiting for the results.

    Args:
        modeller: The Modeller instance being used to manage the task.
        pod_identifiers: The group of pod identifiers to run the task against.
        require_all_pods: Require all pod identifiers specified to accept the task
            request to complete task execution.
        model_out: The path to save the model out to. Defaults to "./output-model.pt".
        project_id: Project ID the task belongs to. Defaults to None.
        run_on_new_data_only: Whether to run the task on new datapoints only.
            Defaults to False.
        batched_execution:  Whether to run the task in batched mode. Defaults to False.
        test_run: Whether to run the modeller in test mode. False if `batched_execution`
            is False. Defaults to False.
        force_rerun_failed_files: If True, forces a rerun on files that
            the task previously failed on. If False, the task will skip
            files that have previously failed. Note: This option can only be
            enabled if both enable_batch_resilience and individual_file_retry_enabled
            are True. Defaults to True.

    Raises:
        PodResponseError: If require_all_pods is true and at least one pod
            identifier specified rejects or fails to respond to a task request.
    """
    pod_identifiers = _check_and_update_pod_ids(pod_identifiers, modeller._hub)
    if batched_execution is None:
        batched_execution = config.settings.default_batched_execution
    return asyncio.run(
        run_modeller_async(
            modeller,
            pod_identifiers,
            require_all_pods,
            model_out,
            project_id,
            run_on_new_data_only,
            batched_execution,
            test_run,
            force_rerun_failed_files,
        )
    )
