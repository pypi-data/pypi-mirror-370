"""Authentication source for Bitfount services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import cached_property
import json
from json import JSONDecodeError
import logging
from pathlib import Path
import time
from typing import Final, Optional, Union, cast
import webbrowser

import jwt
from requests import Response
from requests.exceptions import InvalidJSONError

from bitfount import config
from bitfount.config import _USER_AGENT_STRING
from bitfount.externals.general.authentication import GenericExternallyManagedJWTHandler
from bitfount.externals.general.exceptions import AuthenticationError
from bitfount.hub.exceptions import AuthenticatedUserError
from bitfount.hub.types import (
    _DeviceAccessTokenFailResponseJSON,
    _DeviceAccessTokenRequestDict,
    _DeviceAccessTokenResponseJSON,
    _DeviceCodeRequestDict,
    _DeviceCodeResponseJSON,
    _TokenRefreshRequestDict,
    _TokenRefreshResponseJSON,
)
from bitfount.utils import web_utils

logger = logging.getLogger(__name__)

_PRODUCTION_AUTH_DOMAIN: Final = "auth.bitfount.com"
_STAGING_AUTH_DOMAIN: Final = "auth.staging.bitfount.com"
_DEVELOPMENT_AUTH_DOMAIN: Final = "auth.sandbox.bitfount.com"
_SANDBOX_AUTH_DOMAIN: Final = "auth.sandbox.bitfount.com"

# TODO: [BIT-356] potentially remove these client ids from the codebase
# these are the 'Python CLI' auth0 application client ids
_PRODUCTION_CLIENT_ID: Final = "8iCJ33Kp6hc9ofrXTzr5GLxMRHWrlzZO"
_STAGING_CLIENT_ID: Final = "Wk4XZHDKfY8F3OYcKdagIHETt6JYwX08"
_DEVELOPMENT_CLIENT_ID: Final = "nPU5aIZIOYqqYhUNX84j9OjKpUOnqfRB"
_SANDBOX_CLIENT_ID: Final = "nPU5aIZIOYqqYhUNX84j9OjKpUOnqfRB"

_SCOPES: Final = "profile openid offline_access"
_HUB_API_IDENTIFIER: Final = (
    "https://hub.bitfount.com/api"  # this is the same for staging and production
)
_DEVICE_CODE_GRANT_TYPE: Final = "urn:ietf:params:oauth:grant-type:device_code"
_AUTHORIZATION_PENDING_ERROR: Final = "authorization_pending"
_SLOW_DOWN_ERROR: Final = "slow_down"

_DEFAULT_USERNAME: Final[str] = "_default"
_USERNAME_KEY: Final = "https://www.bitfount.com/username"


class AuthenticationHandler(ABC):
    """Abstract Authentication Handler for use with BitfountSessions."""

    def __init__(self, username: str):
        self.user_storage_path: Path = config.settings.paths.storage_path / username

    @property
    @abstractmethod
    def hub_request_headers(self) -> dict:
        """HTTP Request headers for authenticating with the Hub."""
        pass

    @property
    @abstractmethod
    def am_request_headers(self) -> dict:
        """HTTP Request headers for authenticating with the Access Manager."""
        pass

    @property
    @abstractmethod
    def message_service_request_metadata(self) -> list[tuple[str, str]]:
        """Metadata used to authenticate with the message service."""
        pass

    @abstractmethod
    def authenticate(self) -> None:
        """Retrieve a valid method for authentication if managed externally.

        If the authentication mechanism requires interaction with an external
        party, or the authentication expires, then this is the method that
        should be used to retrieve new authentication materials for
        communicating with Bitfount services.
        """
        pass

    @property
    @abstractmethod
    def authenticated(self) -> bool:
        """Whether the handler currently has valid authentication.

        Some authentication methods are valid from creation,
        others may need refreshing intermittently.
        """
        pass

    @property
    @abstractmethod
    def username(self) -> str:
        """Authenticated user's username."""
        pass


class APIKeysHandler(AuthenticationHandler):
    """Authenticate a user with API Keys."""

    def __init__(self, api_key_id: str, api_key: str, username: str):
        super().__init__(username)
        self._api_key_id = api_key_id
        self._api_key = api_key
        self._username = username
        # We do not send the Access manager portion of the key
        # to the hub or the message service
        self._core_api_key_id = self._api_key_id.split(":")[0]
        self._core_api_key = self._api_key.split(":")[0]

        if self._username == _DEFAULT_USERNAME:
            # username must be explicitly set in __init__ to use API keys
            raise AuthenticatedUserError("Must specify a username when using API Keys.")

    @cached_property
    def hub_request_headers(self) -> dict:
        """Header for authenticating with hub."""
        return {
            "x-api-key-id": self._core_api_key_id,
            "x-api-key": self._core_api_key,
            "user-agent": _USER_AGENT_STRING,
        }

    @cached_property
    def am_request_headers(self) -> dict:
        """Header for authenticating with access manager."""
        # If the URL is an AM URL, the entire API key is used because the AM
        # also calls the Hub under the hood and therefore needs both portions
        return {
            "x-api-key-id": self._api_key_id,
            "x-api-key": self._api_key,
            "user-agent": _USER_AGENT_STRING,
        }

    @property
    def message_service_request_metadata(self) -> list[tuple[str, str]]:
        """Metadata for authenticating with message service."""
        return [
            ("x-api-key-id", self._core_api_key_id),
            ("x-api-key", self._core_api_key),
        ]

    def authenticate(self) -> None:
        """Authenticates the user.

        We're using API keys here which are valid from creation.
        They do not require any additional interaction from the user here.
        """
        logger.debug("Using API keys, no need to authenticate.")

    @property
    def authenticated(self) -> bool:
        """Checks the user is authenticated.

        This class is using API keys which
        cannot be checked in a meaningful way locally.
        """
        logger.debug("Using API keys, assuming they are valid.")
        return True

    @property
    def username(self) -> str:
        """Authenticated user's username.

        In the case of API keys we have relied on the user providing this.
        If it's incorrect then their API calls will fail,
        but we can't meaningfully check this locally.
        """
        return self._username


class ExternallyManagedJWTHandler(
    GenericExternallyManagedJWTHandler,
    AuthenticationHandler,
):
    """Authenticates user via JWT from an external source.

    This can provide a JWT to the `BitfountSession` that is managed
    by another application.

    The Bitfount library hands responsibility for management of the
    token to the external source.

    Whenever a new token is needed it makes a call to the `get_token`
    hook which provides one.
    """

    def __init__(
        self,
        jwt: Optional[str],
        expires: Optional[datetime],
        get_token: Callable[[], tuple[str, datetime]],
        username: str,
    ):
        super().__init__(
            jwt=jwt, expires=expires, get_token=get_token, username=username
        )
        self._username = username

        if self._username == _DEFAULT_USERNAME:
            # username must be explicitly set in __init__ to use OAuth Application
            raise AuthenticatedUserError(
                "Must specify a username when using OAuth Application."
            )

    @property
    def hub_request_headers(self) -> dict:
        """Header for authenticating with hub.

        Checking that the call is authenticated is the responsibility of the calling
        code.
        """
        return self.request_headers

    @property
    def am_request_headers(self) -> dict:
        """Header for authenticating with access manager.

        Checking that the call is authenticated is the responsibility of the calling
        code.
        """
        return self.request_headers

    @property
    def message_service_request_metadata(self) -> list[tuple[str, str]]:
        """Metadata for authenticating with message service.

        Checking that the call is authenticated is the responsibility of the calling
        code.
        """
        if not self.authenticated:
            raise AuthenticationError("JWT is not present or is expired.")
        else:
            # This is just to make mypy happy; the `self.authenticated` check above
            # ensures self._jwt_container is not None
            assert self._jwt_container is not None, "JWT container should be set."  # nosec[assert_used] # Reason: See comment # noqa: E501
            return [("token", self._jwt_container.jwt)]

    @property
    def username(self) -> str:
        """Username of authenticated user."""
        return self._username


class DeviceCodeFlowHandler(AuthenticationHandler):
    """Manages token retrieval and refresh for interactions with Bitfount.

    Extends `requests.Session`, appending an access token to the
    authorization of any requests made if an access token is present

    When the token expires it will request a new token prior to
    sending the web request.

    Attributes:
        access_token_expires_at: The time at which the access token expires.
        device_code: The device code returned by the Bitfount API.
        device_code_arrival_time: The time at which the device code was issued.
        id_token: The ID token returned by the Bitfount API.
        refresh_token: The refresh token returned by the Bitfount API.
        token_file: The path to the file where the token is stored.
        token_request_interval: The time between token requests.
    """

    def __init__(
        self,
        auth_domain: str = _PRODUCTION_AUTH_DOMAIN,
        client_id: str = _PRODUCTION_CLIENT_ID,
        scopes: str = _SCOPES,
        audience: str = _HUB_API_IDENTIFIER,
        username: str = _DEFAULT_USERNAME,
    ):
        super().__init__(username)
        self._access_token: Optional[str] = None
        self._auth_domain = auth_domain
        self._client_id = client_id
        self._scopes: str = scopes
        self._audience: str = audience
        self._device_code_endpoint: str = (
            f"https://{self._auth_domain}/oauth/device/code"
        )
        self._token_endpoint: str = f"https://{self._auth_domain}/oauth/token"
        self._username = username

        self.access_token_expires_at: Optional[datetime] = None
        self.device_code: Optional[str] = None
        self.device_code_arrival_time: Optional[datetime] = None
        self.device_code_expires_in: Optional[int] = None
        self.id_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_file: Path = self.user_storage_path / ".token"
        self.token_request_interval: Optional[int] = None

    @property
    def hub_request_headers(self) -> dict:
        """Header for authenticating with hub."""
        return {
            "authorization": f"Bearer {self._access_token}",
            "user-agent": _USER_AGENT_STRING,
        }

    @property
    def am_request_headers(self) -> dict:
        """Header for authenticating with access manager."""
        return {
            "authorization": f"Bearer {self._access_token}",
            "user-agent": _USER_AGENT_STRING,
        }

    @property
    def message_service_request_metadata(self) -> list[tuple[str, str]]:
        """Metadata for authenticating with message service."""
        return [("token", cast(str, self._access_token))]

    def authenticate(self) -> None:
        """Authenticates user to allow protected requests.

        Prompts the user to login/authenticate and stores the tokens to use them
        in future requests.

        Raises:
            AssertionError: If user storage path corresponds to a different username
                from the BitfountSession.
            ConnectionError: If a token cannot be retrieved.
        """
        self._load_token_from_file(self.token_file)

        # Refresh the loaded token if it has expired
        refreshed = False
        if self.access_token_expires_at and not self.authenticated:
            refreshed = self._refresh_access_token()

        # Force user to go through login flow if we didn't refresh the token
        # Or if we haven't loaded an authenticated token
        if not self.authenticated and not refreshed:
            user_code, verification_uri = self._fetch_device_code()
            self._do_verification(user_code, verification_uri)
            self._exchange_device_code_for_token()

        # Verify that user storage path corresponds to username before saving the token
        self._verify_user_storage_path()

        # Ensure directory path exists
        self.user_storage_path.mkdir(parents=True, exist_ok=True)
        self._save_token_to_file(self.token_file)
        logger.info(f'Logged into Bitfount as "{self.username}"')

    @property
    def authenticated(self) -> bool:
        """Whether the access token is valid.

        Returns: True if the token is valid
        """
        # Either both attributes will be present or neither will be
        if self._access_token and self.access_token_expires_at:
            # If the token expires in the next 10 minutes, refresh
            return (
                self.access_token_expires_at - timedelta(minutes=10)
            ) > datetime.now(timezone.utc)
        else:
            return False

    @property
    def username(self) -> str:
        """Username of the authenticated user."""
        username_from_id_token = self._get_username_from_id_token()
        if self._username != _DEFAULT_USERNAME:
            if self._username != username_from_id_token:
                raise AuthenticatedUserError(
                    f"DeviceCodeFlowHandler object was created for {self._username} but"
                    f" authentication was done against {username_from_id_token}"
                )
            return self._username
        return username_from_id_token

    def _refresh_access_token(self) -> bool:
        """Attempts to refresh the access token.

        Returns: True if the token was refreshed, false otherwise
        """
        token_response = self._send_token_request(refresh=True)

        if token_response.status_code == 200:
            token_response_json: _TokenRefreshResponseJSON = token_response.json()
            self._access_token = token_response_json["access_token"]
            self.refresh_token = token_response_json["refresh_token"]
            self.id_token = token_response_json["id_token"]
            self.access_token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=token_response_json["expires_in"]
            )
            return True
        logger.warning(
            f"Failed to refresh access token, response was: {token_response.text}"
        )
        return False

    def _send_token_request(self, refresh: bool = False) -> Response:
        """Sends a request to the Auth Server token endpoint to get a new token."""
        if refresh:
            # See: https://auth0.com/docs/api/authentication?http#refresh-token
            # If refreshing, must have refresh_token. Reassure mypy.
            assert self.refresh_token is not None  # nosec assert_used
            refresh_request_data: _TokenRefreshRequestDict = {
                "client_id": self._client_id,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            }
            return web_utils.post(self._token_endpoint, data=refresh_request_data)
        else:
            # See: https://auth0.com/docs/api/authentication?http#device-authorization-flow48  # noqa: E501
            # device_code must already be set by the time we are calling this.
            # Reassure mypy.
            assert self.device_code is not None  # nosec assert_used
            request_data: _DeviceAccessTokenRequestDict = {
                "client_id": self._client_id,
                "grant_type": _DEVICE_CODE_GRANT_TYPE,
                "device_code": self.device_code,
            }
            return web_utils.post(self._token_endpoint, data=request_data)

    def _save_token_to_file(self, token_file: Path) -> None:
        """Saves authentication token to file.

        Saves all fields that are necessary to reproduce this object to a file.
        """
        # This will be set by the time this is called. Reassure mypy.
        assert self.access_token_expires_at is not None  # nosec assert_used
        json.dump(
            {
                "access_token": self._access_token,
                "refresh_token": self.refresh_token,
                "id_token": self.id_token,
                "access_token_expires_at": self.access_token_expires_at.timestamp(),
                "auth_domain": self._auth_domain,
                "client_id": self._client_id,
                "scopes": self._scopes,
                "audience": self._audience,
            },
            token_file.open("w"),
        )

    def _load_token_from_file(self, token_file: Path) -> None:
        """Loads authentication token from file.

        Attempts to load the data needed for authentication, when loaded it updates
        the fields on the instance.

        If the data is found but the metadata differs then it will not update
        the fields.

        If no data, or no file is found it will just return without error.
        """
        if token_file.exists():
            try:
                with token_file.open() as tf:
                    serialized_tokens = json.load(tf)
            except (JSONDecodeError, IOError) as e:
                logger.warning(
                    f"Unable to read existing token file ({str(token_file)}),"
                    f" will require new login: {e}"
                )
                return

            auth_domain = serialized_tokens["auth_domain"]
            client_id = serialized_tokens["client_id"]
            scopes = serialized_tokens["scopes"]
            audience = serialized_tokens["audience"]

            if (
                self._auth_domain != auth_domain
                or self._client_id != client_id
                or self._scopes != scopes
                or self._audience != audience
            ):
                print(
                    "Stored tokens are no longer valid, "
                    "fresh authentication is necessary"
                )
                return

            self._access_token = serialized_tokens["access_token"]
            self.refresh_token = serialized_tokens["refresh_token"]
            self.id_token = serialized_tokens["id_token"]
            self.access_token_expires_at = datetime.fromtimestamp(
                serialized_tokens["access_token_expires_at"], tz=timezone.utc
            )

    def _fetch_device_code(self) -> tuple[str, str]:
        """Fetches device code."""
        # See: https://auth0.com/docs/api/authentication?http#device-authorization-flow
        request_data: _DeviceCodeRequestDict = {
            "client_id": self._client_id,
            "scope": self._scopes,
            "audience": self._audience,
        }
        device_code_response: Response = web_utils.post(
            self._device_code_endpoint,
            data=request_data,
        )
        device_code_response.raise_for_status()

        response_json: _DeviceCodeResponseJSON = device_code_response.json()
        verification_uri: str = response_json["verification_uri_complete"]
        user_code: str = response_json["user_code"]

        self.device_code = response_json["device_code"]
        self.token_request_interval = response_json["interval"]
        self.device_code_expires_in = response_json["expires_in"]

        # This doesn't need to be exact, network latency affects this anyway
        self.device_code_arrival_time = datetime.now(timezone.utc)

        return user_code, verification_uri

    def _do_verification(self, user_code: str, verification_uri: str) -> None:
        """Opens web browser for verification."""
        print(f"Your confirmation code is: {user_code}")
        time.sleep(1)  # Give the user a second to see the code before opening browser
        webbrowser.open(verification_uri)
        print(
            "A browser window has been opened, please log in to confirm your identity."
        )
        print("If no browser window has opened, then please visit the following URL:")
        print(verification_uri)

    def _exchange_device_code_for_token(self) -> None:
        """Exchanges device code for token."""
        token_response: Optional[
            Union[_DeviceAccessTokenResponseJSON, _DeviceAccessTokenFailResponseJSON]
        ] = None

        # This method should only be called after a call to _fetch_device_code
        # so these will be set. Asserts to reassure mypy.
        assert self.device_code_arrival_time is not None  # nosec assert_used
        assert self.device_code_expires_in is not None  # nosec assert_used
        assert self.token_request_interval is not None  # nosec assert_used

        interval = self.token_request_interval

        while not self._device_code_expired(
            self.device_code_arrival_time, self.device_code_expires_in
        ):
            response: Response = self._send_token_request()

            # Break out of loop as we have our tokens!
            if (status_code := response.status_code) == 200:
                try:
                    token_response = cast(
                        _DeviceAccessTokenResponseJSON, response.json()
                    )
                except InvalidJSONError:
                    logger.error(
                        f"Received 200 status response, but JSON is invalid: "
                        f'"{response.text}"'
                    )
                    pass
                # Break because we have token or because we're unable to decode it
                break

            # Treat it as an expected "failure" response until we know otherwise;
            # status code could be any 4XX value, so we instead just check for the
            # right format and error values.
            try:
                token_response = cast(
                    _DeviceAccessTokenFailResponseJSON, response.json()
                )
            except InvalidJSONError:
                logger.error(
                    f"Received {status_code} status response, but JSON is invalid: "
                    f'"{response.text}"'
                )
                break

            # Break out of loop unless the flow is still in progress
            if (error := token_response.get("error")) not in (
                _AUTHORIZATION_PENDING_ERROR,
                _SLOW_DOWN_ERROR,
            ):
                # Not a retry-able response; fail out
                error_msg = (
                    f"An unexpected error occurred: status code: {status_code}; "
                    f'"{response.text}"'
                )
                logger.error(error_msg)
                print(error_msg)
                break
            elif error == _SLOW_DOWN_ERROR:
                # Somehow polling too fast (though should be using the interval
                # they specified); increase interval
                logger.warning(
                    f"Polling too quickly; increasing interval from {interval} "
                    f"to {interval + 1} seconds"
                )
                interval += 1
            else:  # error == _AUTHORIZATION_PENDING_ERROR
                # Fine and expected, just keep trying
                pass

            print(
                f"Awaiting authentication in browser. "
                f"Will check again in {interval} seconds."
            )
            time.sleep(interval)

        if token_response and "access_token" in token_response:
            # Have our response now
            token_response = cast(_DeviceAccessTokenResponseJSON, token_response)
            self._access_token = token_response["access_token"]
            self.refresh_token = token_response["refresh_token"]
            self.id_token = token_response["id_token"]
            self.access_token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=token_response["expires_in"],
            )
        else:
            raise ConnectionError(
                "Failed to retrieve a device code from the authentication server"
            )

    @staticmethod
    def _device_code_expired(arrival_time: datetime, expires_in_seconds: int) -> bool:
        """Checks if authorization code has expired.

        Checks if too much time has passed between the device code
        being issued by the Auth Server and the user approving access
        using that device code.
        """
        return datetime.now(timezone.utc) >= arrival_time + timedelta(
            seconds=expires_in_seconds
        )

    def _get_username_from_id_token(self) -> str:
        """Extracts the Bitfount username from the token.

        Note: This function performs no verification of the id_token signature
        and should only be used in situations where the username in the token
        is not used to make decisions. As this is not backend code (i.e.
        anyone can edit this) we aren't very concerned about the fact it is
        not verified.
        """
        if self.id_token is None:
            raise AuthenticatedUserError(
                "User not authenticated yet, call authenticate() before accessing"
                " the ID token"
            )

        # Decode the ID token without verification
        id_token_decode: dict[str, str] = jwt.decode(
            self.id_token, options={"verify_signature": False}
        )
        return id_token_decode[_USERNAME_KEY]

    def _verify_user_storage_path(self) -> None:
        """Verifies that user storage path corresponds to username.

        Raises:
            AssertionError: if user storage path corresponds to a different username
                from the BitfountSession.
        """
        # User storage should either be for the default username or the
        # authenticated user
        if not str(self.user_storage_path).endswith((_DEFAULT_USERNAME, self.username)):
            provided_user = self.user_storage_path.stem
            raise AuthenticatedUserError(
                f"BitfountSession connected to {self.username}. "
                f"This does not match the provided user storage path: {provided_user}"
            )
