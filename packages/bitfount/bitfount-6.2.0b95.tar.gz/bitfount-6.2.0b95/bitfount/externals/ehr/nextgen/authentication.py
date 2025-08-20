"""Authentication classes for NextGen interactions."""

from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlparse

import requests
from requests import Response

from bitfount.externals.ehr.nextgen.exceptions import NextGenQuotaExceeded
from bitfount.hub.api import SMARTOnFHIR
from bitfount.hub.types import SMARTOnFHIRAccessToken
from bitfount.utils.web_utils import _auto_retry_request

logger = logging.getLogger(__name__)


class NextGenAuthSession(requests.Session):
    """Session that uses bearer authentication and auto-retry for NextGen APIs.

    Differs from BearerAuthSession in that it contains functionality to auto-retrieve
    a new NextGen token from SMARTOnFHIR if the other is found to be expired.
    """

    def __init__(
        self,
        smart_on_fhir: SMARTOnFHIR,
    ):
        super().__init__()
        self.smart_on_fhir = smart_on_fhir
        self._token: Optional[SMARTOnFHIRAccessToken] = None

    @property
    def token(self) -> str:
        """Returns the current NextGen token or gets one if necessary."""
        if self._token is None:
            self._token = self.smart_on_fhir.get_access_token()
        return self._token.token

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

        # Try the request once
        resp = super().request(
            method, url, params=params, data=data, headers=headers, **kwargs
        )
        # If we get a 401 (which could indicate token expired), we'll get a new token
        # and retry; otherwise, just return the response
        if resp.status_code != 401:
            return self._check_for_quota_limits(resp)
        else:
            # Do some sanity checking; auth failures seem to have body
            # "invalid access token" so we should check this
            if (resp_body := resp.text) == "invalid access token":
                logger.warning(
                    "NextGen response was 401: invalid access token,"
                    " refreshing from SMART on FHIR..."
                )
            else:
                if len(resp_body) <= 40:
                    body_log_str = resp_body
                else:
                    body_log_str = f"{resp_body[:40]}... (truncated)"
                logger.warning(
                    f"NextGen response was 401, but body didn't indicate expired token."
                    f" Attempting to refresh token from SMART on FHIR anyway..."
                    f" Body was: {body_log_str}"
                )

            self._token = None  # Clear the old token to force a new one to be fetched
            headers["authorization"] = f"Bearer {self.token}"
            return self._check_for_quota_limits(
                super().request(
                    method, url, params=params, data=data, headers=headers, **kwargs
                )
            )

    @staticmethod
    def _check_for_quota_limits(resp: Response) -> Response:
        """Perform check for quota limits being exceeded.

        This limit is detailed at https://developer.nextgen.com/wiki/pages/999bfa5c-947d-43df-a9ed-591d6690884f/intro-to-api-dev-portal
        and applies across the _entirety_ of Bitfount applications.

        It is indicated by receiving "a 200 status code but an empty payload".
        """
        if resp.status_code == 200 and not resp.content:
            req = resp.request
            if (method := req.method) and (url := req.url):
                # Get something of the form GET:/path/to/api/endpoint
                parsed_url = urlparse(url)
                request_details = f"{method.upper()}:{parsed_url.path}"
            else:
                request_details = None

            err_msg = (
                "Received response indicating NextGen daily quota exceeded"
                " (200, empty payload)"
            )
            if request_details:
                err_msg += f" when performing {request_details}"
            raise NextGenQuotaExceeded(err_msg)
        return resp
