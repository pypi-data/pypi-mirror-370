"""General authentication classes for external service interactions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
import threading
from typing import Any, Callable, Optional

import requests
from requests import Response

from bitfount import config
from bitfount.config import _USER_AGENT_STRING
from bitfount.externals.general.exceptions import AuthenticationError
from bitfount.utils.web_utils import _auto_retry_request

_logger = logging.getLogger(__name__)


class BearerAuthSession(requests.Session):
    """Session implementation that uses bearer authentication and auto-retry.

    Has no notion of token expiration or (re)authentication, simply using the
    provided token as-is. If reauthentication is required,
    see `ExternallyManagedJWTSession`.
    """

    def __init__(
        self,
        bearer_token: str,
    ) -> None:
        """Initializes a BearerAuthSession with the provided bearer token."""
        super().__init__()
        self.token = bearer_token

    # We only wrap this method in _auto_retry_request as any calls to the others
    # (post, get, etc) will make use of this. Wrapping them all would result in
    # a double retry loop, but we can't _not_ wrap request as it is often used
    # directly.
    @_auto_retry_request
    def request(  # type: ignore[no-untyped-def] # Reason: This is simply overriding a method on the parent class # noqa: E501
        self, method, url, params=None, data=None, headers=None, **kwargs
    ) -> Response:
        """Performs an HTTP request.

        Overrides requests.session.request, appending our access token
        to the request headers or API keys if present.
        """
        # Create headers if they don't exist already
        if not headers:
            headers = {}

        headers["authorization"] = f"Bearer {self.token}"

        return super().request(
            method, url, params=params, data=data, headers=headers, **kwargs
        )


@dataclass
class JWT:
    """Thin container for JSON web token and its expiry."""

    jwt: str
    expires: datetime


@dataclass(kw_only=True)
class ExternallyManagedJWT:
    """Externally managed JWT."""

    jwt: Optional[str] = None
    expires: Optional[datetime] = None
    get_token: Callable[[], tuple[str, datetime]]


class GenericExternallyManagedJWTHandler:
    """Authenticates user via JWT from an external source.

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
        **kwargs: Any,
    ) -> None:
        """Creates a new instance of GenericExternallyManagedJWTHandler.

        Can be supplied an initial JWT and expiration time to use or ignore these and
        rely on the provided hook to get the first token.

        Args:
            jwt: Optional. Initial JWT token to use. If provided, `expires` must also
                be provided.
            expires: Optional. Initial expiration time to use. If provided, `jwt` must
                also be provided.
            get_token: Callable that returns a tuple of a JWT and its expiration time.
            **kwargs: Other kwargs to be passed to the superclass.
        """
        super().__init__(**kwargs)

        self._get_token: Callable[[], tuple[str, datetime]] = get_token

        # Need both or neither of JWT and expiration time
        if jwt is not None and expires is None:
            _logger.warning(
                "JWT must have an expiration time, none was supplied."
                " Will retrieve new JWT."
            )
            jwt = None
        if jwt is None and expires is not None:
            _logger.warning(
                "JWT provided, but expiration time not. Setting expiration to None."
            )
            expires = None

        self._jwt_container: Optional[JWT]
        if jwt is not None and expires is not None:
            self._jwt_container = JWT(jwt=jwt, expires=expires)
        else:
            self._jwt_container = None

    def authenticate(self) -> None:
        """Retrieves a token from the token source.

        Calls the hook provided on object creation to retrieve a new token.
        """
        if not self.authenticated:
            token, expires = self._get_token()
            self._jwt_container = JWT(jwt=token, expires=expires)

    @property
    def authenticated(self) -> bool:
        """Whether the token is still valid."""
        if self._jwt_container is None:
            return False
        else:
            # Check for expiration with a 1 minute buffer
            return (self._jwt_container.expires - timedelta(minutes=1)) > datetime.now(
                timezone.utc
            )

    @property
    def request_headers(self) -> dict:
        """Header for authenticated requests.

        Checking that the call is authenticated is the responsibility of the calling
        code.

        Raises:
            AuthenticationError: If the JWT is not present or is expired.
        """
        if not self.authenticated:
            raise AuthenticationError("JWT is not present or is expired.")
        else:
            if self._jwt_container is None:
                # We should not get here. The `self.authenticated` check above
                # ensures self._jwt_container is not None
                raise ValueError("JWT container should be set.")

            return {
                "authorization": f"Bearer {self._jwt_container.jwt}",
                "user-agent": _USER_AGENT_STRING,
            }

    def get_valid_token(self) -> str:
        """Get a valid token to use."""
        if not self.authenticated:
            self.authenticate()

        if self._jwt_container is None:
            # We should not get here.`self.authenticate()` above
            # ensures self._jwt_container is not None
            raise ValueError("JWT container should be set.")

        return self._jwt_container.jwt


class ExternallyManagedJWTSession(requests.Session):
    """Manages session-based interactions with authentication handled externally.

    Extends `requests.Session`, appending an access token to the
    authorization of any requests made if an access token is present

    When the token expires it will request a new token prior to
    sending the web request.
    """

    def __init__(
        self,
        authentication_handler: GenericExternallyManagedJWTHandler,
    ):
        super().__init__()

        self._reauthentication_lock = threading.Lock()

        self.authentication_handler = authentication_handler

    @property
    def request_headers(self) -> dict:
        """Returns metadata for authenticating external service.

        Handles (re)authentication against the external service if needed.
        """
        with self._reauthentication_lock:
            if not self.authenticated:
                self.authenticate()

            return self.authentication_handler.request_headers

    @property
    def authenticated(self) -> bool:
        """Returns true if we have an unexpired access token."""
        return self.authentication_handler.authenticated

    def authenticate(self) -> None:
        """Authenticates session to allow protected requests."""
        _logger.debug("Calling authenticate on authentication handler")
        self.authentication_handler.authenticate()

    # We only wrap this method in _auto_retry_request as any calls to the others
    # (post, get, etc) will make use of this. Wrapping them all would result in
    # a double retry loop, but we can't _not_ wrap request as it is often used
    # directly.
    @_auto_retry_request
    def request(  # type: ignore[no-untyped-def] # Reason: This is simply overriding a method on the parent class # noqa: E501
        self, method, url, params=None, data=None, headers=None, **kwargs
    ) -> Response:
        """Performs an HTTP request.

        Overrides requests.session.request, appending our access token
        to the request headers or API keys if present.
        """
        # Create headers if they don't exist already
        if not headers:
            headers = {}

        # [LOGGING-IMPROVEMENTS]
        if config.settings.logging.log_authentication_headers:
            _logger.debug(f"Adding authentication to request headers for {url}")

        headers.update(self.request_headers)

        return super().request(
            method, url, params=params, data=data, headers=headers, **kwargs
        )
