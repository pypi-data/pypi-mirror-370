"""Modeller for dispatching tasks."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, cast

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from bitfount import config
from bitfount.encryption.encryption import _RSAEncryption
from bitfount.federated.aggregators.secure import SecureAggregator
from bitfount.federated.authorisation_checkers import (
    _IDENTITY_VERIFICATION_METHODS_MAP,
    IdentityVerificationMethod,
    ProtocolContext,
    _SignatureBasedAuthorisation,
    check_identity_verification_method,
)
from bitfount.federated.exceptions import PodResponseError
from bitfount.federated.helper import (
    TaskContext,
    _check_and_update_pod_ids,
    _create_message_service,
)
from bitfount.federated.keys_setup import (
    RSAKeyPair,
    _get_key_id,
    _get_modeller_keys,
    _store_key_id,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.monitoring import task_monitor_context
from bitfount.federated.transport.base_transport import _run_func_and_listen_to_mailbox
from bitfount.federated.transport.identity_verification.oidc import (
    _OIDCAuthFlowChallengeHandler,
    _OIDCDeviceCodeHandler,
)
from bitfount.federated.transport.identity_verification.types import (
    _HasWebServer,
    _ResponseHandler,
)
from bitfount.federated.transport.message_service import (
    _BitfountMessageType,
    _MessageService,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.types import _TaskRequestMessageGenerator
from bitfount.hooks import HookType, get_hooks
from bitfount.hub.api import BitfountHub
from bitfount.hub.authentication_flow import _get_auth_environment
from bitfount.hub.exceptions import PodDoesNotExistError
from bitfount.hub.helper import _default_bitfounthub, _get_pod_public_keys

if TYPE_CHECKING:
    from bitfount.federated.protocols.base import BaseProtocolFactory


logger = _get_federated_logger(__name__)


@dataclass
class _RegisteredRSAPrivateKey:
    private_key: RSAPrivateKey
    key_id: str


class _Modeller:
    """Dispatches tasks to pods and runs the modeller side of the provided protocol.

    ```python title="Example usage:"
    import bitfount as bf

    modeller=bf.Modeller(
        protocol=bf.FederatedAveraging(...),
    )
    modeller.run(pod_identifiers=["bitfount/example-pod-1", "bitfount/example-pod-2"])
    ```

    Args:
        protocol: The protocol to use for the task.
        message_service: The message service to use for communication with pods.
            Defaults to None, in which case a new message service will be created.
        bitfounthub: Hub instance for Bitfount Hub communication. Defaults to None,
            in which case a new `BitfountHub` instance will be created.
        pod_public_key_paths: Optional. Mapping of pod identifiers to public
            key files for existing pod public keys. Expired or non-existent
            keys will be downloaded from the Hub.
        identity_verification_method: The identity verification method to use.
            Defaults to OIDC_DEVICE_CODE.
        private_key: This modeller's private key either as an `RSAPrivateKey`
            instance or a path to a private key file. If a non-key-based identity
            verification method is used, this is ignored. Defaults to None.
        idp_url: URL of identity provider, used for Identity Verification.

    Attributes:
        protocol: The protocol to use for the task.

    Raises:
        ValueError: If key-based identity verification is selected but no
            private key is provided.
    """

    def __init__(
        self,
        protocol: BaseProtocolFactory,
        message_service: Optional[_MessageService] = None,
        bitfounthub: Optional[BitfountHub] = None,
        pod_public_key_paths: Optional[Mapping[str, Path]] = None,
        identity_verification_method: Union[
            str, IdentityVerificationMethod
        ] = IdentityVerificationMethod.DEFAULT,
        private_key: Optional[Union[RSAPrivateKey, Path]] = None,
        idp_url: Optional[str] = None,
    ):
        self.protocol = protocol
        self._hub = _default_bitfounthub(hub=bitfounthub)
        self._message_service = (
            message_service
            if message_service is not None
            else _create_message_service(session=self._hub.session)
        )
        self._pod_public_key_paths: Mapping[str, Path] = pod_public_key_paths or dict()

        self._identity_verification_method: IdentityVerificationMethod = (
            check_identity_verification_method(identity_verification_method)
        )

        self._key_details = _Modeller._process_private_key(
            private_key, self._identity_verification_method, self._hub
        )

    @staticmethod
    def _is_public_key_registered(
        username: str, public_key: RSAPublicKey, hub: BitfountHub
    ) -> Optional[str]:
        key_id = None
        try:
            key_id = _get_key_id(_Modeller._get_modeller_key_storage_path(username))
        except IOError:
            logger.debug(
                "Key present, but no key ID file found. "
                "Will re-register key with the hub"
            )

        if key_id:
            # Validate against registered public key or register if not already present
            logger.debug(
                f"Checking hub for registered modeller public key"
                f" for modeller {username} with ID {key_id}"
            )
            key_with_metadata = hub.check_public_key_registered_and_active(key_id)
            if key_with_metadata:
                if _RSAEncryption.public_keys_equal(
                    public_key, key_with_metadata["public_key"]
                ):
                    logger.debug(
                        f"Public key already registered for modeller {username}"
                    )
                    return key_id
                else:
                    logger.debug(
                        f"Key provided doesn't match "
                        f"the one stored on the hub with ID {key_id}"
                    )
            else:
                logger.debug("Key provided, but it's not registered on the hub")
        return None

    @staticmethod
    def _process_private_key(
        private_key: Optional[Union[RSAPrivateKey, Path]],
        identity_verification_method: IdentityVerificationMethod,
        hub: BitfountHub,
    ) -> Optional[_RegisteredRSAPrivateKey]:
        # NOTE: This method is static to avoid the risk of it being called during
        #       _Modeller initialisation before the identity_verification_method
        #       or hub attributes have been set.
        # Fail out fast if not using key-based authorisation
        if identity_verification_method != IdentityVerificationMethod.KEYS:
            if private_key:
                logger.warning(
                    f"Private key provided but identity verification method "
                    f'"{identity_verification_method.value}" was chosen. '
                    f"Private key will be ignored."
                )
            return None

        username = hub.username

        if isinstance(private_key, Path):
            # Load private key file if needed
            logger.debug(
                f"Loading private key for modeller {username} from {str(private_key)}"
            )
            private_key = _RSAEncryption.load_private_key(private_key)
            public_key = private_key.public_key()
            # If we loaded it from a file, it may already be registered
            maybe_key_id = _Modeller._is_public_key_registered(
                username, public_key, hub
            )
            if maybe_key_id:
                logger.info(f"Modeller '{username}' using key with ID: {maybe_key_id}")
                return _RegisteredRSAPrivateKey(private_key, maybe_key_id)

        elif private_key is None:
            # Generate/load stored keys
            logger.info(
                f"No keys provided for modeller {username}; loading/generating keys"
            )
            key_pair = _Modeller._get_modeller_keys(username)
            private_key = key_pair.private
            public_key = key_pair.public

            # If the key was loaded it might already be registered
            maybe_key_id = _Modeller._is_public_key_registered(
                username, public_key, hub
            )
            if maybe_key_id:
                logger.info(f"Modeller '{username}' using key with ID: {maybe_key_id}")
                return _RegisteredRSAPrivateKey(private_key, maybe_key_id)
        elif isinstance(private_key, RSAPrivateKey):
            # Just use private key as is
            # We can't feasibly check this is registered without iterating
            # through them all, so we're going to register it
            public_key = private_key.public_key()
        else:
            # Must be invalid type
            raise TypeError(
                f"Error processing private key; expected a Path, RSAPrivateKey"
                f" or None, got {type(private_key)}"
            )

        # Register new public key
        logger.info(f"Registering public key for modeller {username}")
        key_id = str(hub.register_user_public_key(public_key))
        _store_key_id(
            _Modeller._get_modeller_key_storage_path(username),
            key_id,
        )

        logger.info(f"Modeller '{username}' using key with ID: {key_id}")

        return _RegisteredRSAPrivateKey(private_key, key_id)

    @staticmethod
    def _get_modeller_key_storage_path(username: str) -> Path:
        """Get the appropriate storage directory for the modeller keys."""
        # NOTE: We explicitly construct the storage path (rather than relying on
        #       the user_storage_path from the hub/session) to guarantee that the
        #       key storage location is explicitly linked to the username and avoids
        #       using `_default`.
        return Path(config.settings.paths.storage_path / username / "modeller" / "keys")

    @staticmethod
    def _get_modeller_keys(username: str) -> RSAKeyPair:
        """Load existing modeller keys or generate new ones.

        Args:
            username: The user to generate/load the keys for.

        Returns:
            The loaded/generated keys.
        """
        key_storage_path = _Modeller._get_modeller_key_storage_path(username)
        keys = _get_modeller_keys(key_storage_path)
        return keys

    async def _send_task_requests(
        self,
        pod_identifiers: Iterable[str],
        project_id: Optional[str],
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> _ModellerMailbox:
        """Sends task requests to pods.

        Args:
            pod_identifiers: The group of pods to run the task with.
            project_id: Project Id the task belongs to.
            run_on_new_data_only: Whether to run the task on new datapoints only.
                Defaults to False.
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
            The created ModellerMailbox for the task.
        """
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        # Load pod public keys
        loaded_pod_public_keys: dict[str, RSAPublicKey] = _get_pod_public_keys(
            pod_identifiers=pod_identifiers,
            hub=self._hub,
            pod_public_key_paths=self._pod_public_key_paths,
            project_id=project_id,
        )

        task_request_msg_gen = self._get_task_request_msg_gen()

        # Send task requests to chosen pods. We haven't attached a handler for the
        # responses yet but this is handled below. There is no issue due to the
        # fact that the listening task hasn't been started yet, and the inherent
        # handler backoff.
        for hook in get_hooks(HookType.MODELLER):
            hook.on_task_request(pod_identifiers=pod_identifiers, project_id=project_id)

        modeller_mailbox: _ModellerMailbox = await _ModellerMailbox.send_task_requests(
            serialized_protocol=self.protocol.dump(),
            pod_public_keys=loaded_pod_public_keys,
            task_request_msg_gen=task_request_msg_gen,
            message_service=self._message_service,
            project_id=project_id,
            run_on_new_data_only=run_on_new_data_only,
            batched_execution=batched_execution,
            test_run=test_run,
            force_rerun_failed_files=force_rerun_failed_files,
        )

        return modeller_mailbox

    def _get_task_request_msg_gen(self) -> _TaskRequestMessageGenerator:
        """Construct correct TaskRequestMessageGenerator object for the auth type."""
        authorization_checker_cls = _IDENTITY_VERIFICATION_METHODS_MAP[
            self._identity_verification_method
        ]

        if (
            self._identity_verification_method == IdentityVerificationMethod.KEYS
            and self._key_details is not None
        ):
            authorization_checker_cls = cast(
                type[_SignatureBasedAuthorisation], authorization_checker_cls
            )
            assert isinstance(self._key_details.private_key, RSAPrivateKey)  # nosec assert_used
            return authorization_checker_cls.create_task_request_message_generator(
                self._key_details.private_key, self._key_details.key_id
            )
        else:
            return authorization_checker_cls.create_task_request_message_generator()

    async def _modeller_run(
        self,
        modeller_mailbox: _ModellerMailbox,
        pod_identifiers: Iterable[str],
        require_all_pods: bool = False,
        response_handler: Optional[_ResponseHandler] = None,
        batched_execution: Optional[bool] = None,
    ) -> Union[Literal[False], Optional[Any]]:
        """Waits for pod responses and handles any who don't respond in time.

        Runs the modeller side of the protocol if some pods accepted the task.
        """
        # If additional response handling is specified, we call the handler
        if response_handler:
            await response_handler.handle(modeller_mailbox)
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        # Process job accept/reject
        await modeller_mailbox.process_task_request_responses()
        for hook in get_hooks(HookType.MODELLER):
            hook.on_task_response(
                accepted_pod_identifiers=list(
                    modeller_mailbox.accepted_worker_mailboxes.keys()
                ),
                task_id=modeller_mailbox.task_id,
            )

        # Fail-fast if no pods accepted the task request.
        if not modeller_mailbox.accepted_worker_mailboxes:
            logger.error(
                "No workers with which to train. "
                "Please ensure you have sent task requests at least some of "
                "which have been accepted."
            )
            return False

        # Otherwise run the protocol
        unaccepted_worker_ids = set(pod_identifiers).difference(
            set(modeller_mailbox.accepted_worker_mailboxes)
        )
        if unaccepted_worker_ids:
            unaccepted_worker_msg = (
                f"Pods {', '.join(unaccepted_worker_ids)} "
                "rejected task request or failed to respond. "
            )
            if require_all_pods:
                raise PodResponseError(
                    unaccepted_worker_msg
                    + "Task requires all pods accept the task request."
                )
            else:
                logger.warning(
                    unaccepted_worker_msg + "Continuing task without these pods ..."
                )

        return await self._run_modeller_protocol(modeller_mailbox, batched_execution)

    async def _run_modeller_protocol(
        self,
        modeller_mailbox: _ModellerMailbox,
        batched_execution: Optional[bool] = None,
    ) -> Optional[Any]:
        """Runs the modeller-side of the protocol."""
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        modeller_protocol = self.protocol.modeller(mailbox=modeller_mailbox)

        # Initialise the modeller side of the protocol
        modeller_protocol.initialise(
            task_id=modeller_mailbox.task_id,
        )

        # Run the modeller side of the protocol
        result = await modeller_protocol.run(
            batched_execution=batched_execution,
            context=ProtocolContext(task_context=TaskContext.MODELLER),
        )
        # Send task complete message
        await modeller_mailbox.send_task_complete_message()
        return result

    async def run_async(
        self,
        pod_identifiers: Iterable[str],
        require_all_pods: bool,
        project_id: Optional[str] = None,
        run_on_new_data_only: bool = False,
        batched_execution: Optional[bool] = None,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> Union[Literal[False], Optional[Any]]:
        """Runs the modeller's task with a set of pods.

        Will send a task request before commencing the task itself and only pods that
        accept the task request will be used.

        Args:
            pod_identifiers: The identifiers for the pods to run the task on.
            require_all_pods: Only run task if all pods are online.
            project_id: Project Id the task belongs to. Defaults to None.
            run_on_new_data_only: Whether to run the task on new datapoints only.
                Defaults to False.
            batched_execution: Whether to run the task in batched mode. Defaults to
                False.
            test_run: If True, runs the task in test mode, on a limited number of
                datapoints. False if batched execution is False. Defaults to False.
            force_rerun_failed_files: If True, forces a rerun on files that
                the task previously failed on. If False, the task will skip
                files that have previously failed. Note: This option can only be
                enabled if both enable_batch_resilience and
                individual_file_retry_enabled are True. Defaults to True.

        Returns:
            Whatever the protocol's return value is.

        Raises:
            PodResponseError: If require_all_pods is True and at least one
                pod_identifier rejects or fails to respond to the task request.
        """
        if batched_execution is None:
            batched_execution = config.settings.default_batched_execution
        try:
            # We do this early to give any handler components time to spin up
            response_handler = self._get_response_handler()

            logger.info("Sending task requests...")
            modeller_mailbox: _ModellerMailbox = await self._send_task_requests(
                pod_identifiers,
                project_id,
                run_on_new_data_only,
                batched_execution,
                test_run,
                force_rerun_failed_files,
            )

            with task_monitor_context(
                hub=self._hub,
                task_id=modeller_mailbox.task_id,
                sender_id=modeller_mailbox.mailbox_id,
            ):
                run_result: Union[
                    Literal[False], Optional[Any]
                ] = await _run_func_and_listen_to_mailbox(
                    self._modeller_run(
                        modeller_mailbox=modeller_mailbox,
                        pod_identifiers=pod_identifiers,
                        require_all_pods=require_all_pods,
                        response_handler=response_handler,
                        batched_execution=batched_execution,
                    ),
                    modeller_mailbox,
                )
                modeller_mailbox.delete_all_handlers(_BitfountMessageType.LOG_MESSAGE)
                return run_result
        except PodDoesNotExistError as e:
            logger.exception(e)
            logger.error("Aborted task request.")
            return False

        finally:
            # Stop any response handler web servers that may be running still
            try:
                # noinspection PyUnboundLocalVariable
                await cast(_HasWebServer, response_handler).stop_server()
            except NameError:
                logger.warning("Tried to shutdown non-existent response handler")
            except AttributeError:
                # Didn't have a stop_server() method
                pass

    def _get_response_handler(self) -> Optional[_ResponseHandler]:
        """Construct a response handler for additional task messages if required.

        This may spin-up web servers if the response handler requires it. It is
        the responsibility of the handler to shut these down when no longer needed.
        """
        response_handler: Optional[_ResponseHandler] = None

        # OIDC_ACF_PKCE
        if (
            self._identity_verification_method
            == IdentityVerificationMethod.OIDC_ACF_PKCE
        ):
            auth_env = _get_auth_environment()
            logger.debug(
                f"Setting up OIDC Authorization Code Flow challenge listener against "
                f"{auth_env.name} authorization environment."
            )
            response_handler = _OIDCAuthFlowChallengeHandler(
                auth_domain=auth_env.auth_domain
            )

        # OIDC_DEVICE_CODE
        elif (
            self._identity_verification_method
            == IdentityVerificationMethod.OIDC_DEVICE_CODE
        ):
            auth_env = _get_auth_environment()
            response_handler = _OIDCDeviceCodeHandler(auth_domain=auth_env.auth_domain)

        # Start web server if needed
        # cast()s are needed to allow mypy to infer this as reachable
        if isinstance(cast(_HasWebServer, response_handler), _HasWebServer):
            # Start response handler web server in background as it takes some time
            cast(_HasWebServer, response_handler).start_server()

        return response_handler

    def _serialize(self, model_out: Union[str, os.PathLike]) -> None:
        """Save any models to file.

        Save any algorithms which have models to the filename specified. If there is
        more than one algorithm with a model, the model name will be be appended with a
        number, starting from 1.

        Args:
            model_out: The path to save the model out to.
        """
        model_algorithms = [i for i in self.protocol.algorithms if hasattr(i, "model")]

        for i, algo in enumerate(model_algorithms, start=1):
            model_out = (
                f"{str(model_out)}_{i}" if len(model_algorithms) > 1 else str(model_out)
            )
            try:
                algo.model.serialize(model_out)
                logger.info(f'Model saved successfully to "{model_out}"')
            except Exception as e:
                logger.exception(e)

    def run(
        self,
        pod_identifiers: Iterable[str],
        require_all_pods: bool = False,
        model_out: Optional[Union[Path, str]] = None,
        project_id: Optional[str] = None,
        run_on_new_data_only: bool = False,
        batched_execution: bool = False,
        test_run: bool = False,
        force_rerun_failed_files: bool = True,
    ) -> Union[Literal[False], Optional[Any]]:
        """Runs the modeller's task with a set of pods.

        Will send a task request before commencing the task itself and only pods
        that accept the task request will be used.

        Args:
            pod_identifiers: The identifiers for the pods to run the task on.
            require_all_pods: Only run task if all pods are online.
            model_out: If specified, path to save the model out to.
            project_id: Project_id the task belongs to.
            run_on_new_data_only: Whether to run the task on new datapoints only.
                Defaults to False.
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
            Whatever the protocol's return value is.

        Raises:
            PodResponseError: If require_all_pods is True and at least one
                pod_identifier rejects or fails to respond to the task request.
        """
        pod_identifiers = _check_and_update_pod_ids(pod_identifiers, self._hub)

        # We need to pass the `SecureShare` parameters to the
        # model when SecureAggregation is in use.
        # First we check the protocol's model and aggregators.
        # if steps_between_parameter_updates is 1, then we do
        # the clipping at the 'SecureShare' level.
        if (
            hasattr(self.protocol, "aggregator")
            and isinstance(self.protocol.aggregator, SecureAggregator)
        ) and (
            hasattr(self.protocol, "steps_between_parameter_updates")
            and self.protocol.steps_between_parameter_updates != 1
        ):
            if any(hasattr(algo, "model") for algo in self.protocol.algorithms):
                logger.warning(
                    "SecureAggregation in use. We recommend normalization "
                    "of continuous features prior to training."
                )

            # Show warning to user if using custom models that
            # they might have to implement clipping in their custom model.
            if any(
                hasattr(algo, "model")
                and isinstance(algo.model, BitfountModelReference)
                for algo in self.protocol.algorithms
            ):
                logger.warning(
                    "You are using a custom model with Secure Aggregation."
                    "We recommend clipping the model parameters."
                )

            # Pass the `SecureShare` parameters to the model for clipping
            for algo in self.protocol.algorithms:
                if hasattr(algo, "model"):
                    algo.model.param_clipping = {
                        "prime_q": self.protocol.aggregator._secure_share.prime_q,
                        "precision": self.protocol.aggregator._secure_share.precision,
                        "num_workers": len(pod_identifiers),
                    }
        result = asyncio.run(
            self.run_async(
                pod_identifiers,
                require_all_pods,
                project_id,
                run_on_new_data_only,
                batched_execution,
                test_run,
                force_rerun_failed_files,
            )
        )
        if model_out and result is not False:
            self._serialize(model_out)
        return result
