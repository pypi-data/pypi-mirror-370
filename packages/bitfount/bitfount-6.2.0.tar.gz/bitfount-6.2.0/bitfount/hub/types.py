"""Types for hub-related code."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final, List, Literal, Optional, TypedDict, Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing_extensions import NotRequired

from bitfount.federated.monitoring.types import ProgressCounterDict
from bitfount.federated.types import SerializedProtocol
from bitfount.types import (
    _JSONDict,
    _S3PresignedPOSTFields,
    _S3PresignedPOSTURL,
    _S3PresignedURL,
)

# Hub/AM URLs
PRODUCTION_HUB_URL: Final[str] = "https://hub.bitfount.com"
PRODUCTION_AM_URL: Final[str] = "https://am.hub.bitfount.com"
_STAGING_HUB_URL: Final[str] = "https://hub.staging.bitfount.com"
_STAGING_AM_URL: Final[str] = "https://am.hub.staging.bitfount.com"
_DEV_HUB_URL: Final[str] = "http://localhost:3000"
_DEV_AM_URL: Final[str] = "http://localhost:3001"
_SANDBOX_HUB_URL: Final[str] = "https://hub.sandbox.bitfount.com"
_SANDBOX_AM_URL: Final[str] = "https://am.hub.sandbox.bitfount.com"
# IDP URLs
_PRODUCTION_IDP_URL: Final[str] = (
    "https://prod-bitfount.eu.auth0.com/"
    "samlp/8iCJ33Kp6hc9ofrXTzr5GLxMRHWrlzZO?SAMLRequest="
)
_STAGING_IDP_URL: Final[str] = (
    "https://dev-bitfount.eu.auth0.com/"
    "samlp/Wk4XZHDKfY8F3OYcKdagIHETt6JYwX08?SAMLRequest="
)
_DEV_IDP_URL: Final[str] = (
    "https://dev-bitfount.eu.auth0.com/"
    "samlp/MP8oao6gcJd4jARwzJiJlEiK59ZeLCt3?SAMLRequest="
)
_SANDBOX_IDP_URL: Final[str] = (
    "https://dev-bitfount.eu.auth0.com/"
    "samlp/Wk4XZHDKfY8F3OYcKdagIHETt6JYwX08?SAMLRequest="
)  # same as staging


# General JSONs
class _HubSuccessResponseJSON(TypedDict):
    """Generic hub success response JSON."""

    success: Literal[True]
    message: str


class _HubFailureResponseJSON(TypedDict):
    """Generic hub failure response JSON."""

    success: Literal[False]
    errorMessage: str


_HubResponseJSON = Union[_HubSuccessResponseJSON, _HubFailureResponseJSON]


# Hub-related JSON.
class _PodDetailsResponseJSON(TypedDict):
    """Response JSON from GET /api/pods/[userName]/[podName]."""

    podIdentifier: str
    podName: str
    podDisplayName: str
    podPublicKey: str
    accessManagerPublicKey: str
    description: str
    # dataSchema: str  # present but should not be used
    schemaStorageKey: str
    isOnline: bool
    providerUserName: str
    visibility: Literal["public", "private"]
    schemaDownloadUrl: _S3PresignedURL


class _MultiPodDetailsResponseJSON(TypedDict):
    """Response JSON from GET /api/pods."""

    podIdentifier: str
    name: str
    podDisplayName: str
    isOnline: bool
    podPublicKey: str
    accessManagerPublicKey: str
    description: str
    providerUserName: str
    podPagePath: str


class _PodRegistrationResponseJSON(TypedDict):
    """Response JSON from POST /api/pods."""

    success: bool
    alreadyExisted: bool
    message: str
    uploadUrl: _S3PresignedPOSTURL
    uploadFields: _S3PresignedPOSTFields


class _PodRegistrationFailureJSON(TypedDict):
    """Failure response JSON from POST /api/pods."""

    success: Literal[False]
    alreadyExisted: bool
    errorMessage: str


class _ModelDetailsResponseJSON(TypedDict):
    """Response JSON from GET /api/models when getting specific model."""

    modelDownloadUrl: _S3PresignedURL
    modelHash: str
    weightsDownloadUrl: NotRequired[_S3PresignedURL]
    modelVersion: int


class _ModelUploadResponseJSON(TypedDict):
    """Response JSON from POST /api/models."""

    # This is not a 1-to-1 mapping with the actual return types (i.e. some are
    # only returned on success, some only on failure), but is enough for our
    # use case.
    uploadUrl: _S3PresignedPOSTURL
    uploadFields: _S3PresignedPOSTFields
    success: bool
    alreadyExisted: bool
    version: int
    errorMessage: NotRequired[str]


class _MonitorPostJSON(TypedDict):
    """Form of the JSON object for sending to the task monitoring service."""

    taskId: str
    senderId: str
    recipientId: NotRequired[str]
    timestamp: str  # ISO 8601 format timestamp
    privacy: str  # one of monitoring.MonitorRecordPrivacy's values
    # one of _BitfountMessageType's names or monitoring.AdditionalMonitorMessageTypes
    type: str
    message: NotRequired[str]
    metadata: NotRequired[_JSONDict]
    progress: NotRequired[dict[str, ProgressCounterDict]]
    resourceUsage: NotRequired[dict[str, float]]


class _RegisterUserPublicKeyPOSTJSON(TypedDict):
    """Form of POST JSON for registering user public key.

    API: POST /api/[username]/keys

    The public key should be in OpenSSH format.
    """

    key: str  # should be in ssh format


class _PublicKeyJSON(TypedDict):
    """Public Key JSON from Hub.

    Keys will be returned in PEM format.
    """

    public_key: str
    id: str
    active: bool


class _ActivePublicKey(TypedDict):
    """Parsed public key with metadata from the hub."""

    public_key: RSAPublicKey
    id: str
    active: bool


class _UserRSAPublicKeysResponseJSON(TypedDict):
    """Response JSON from GET /api/{username}/keys.

    Keys will be returned in PEM format.
    """

    maximumOffset: int
    keys: list[_PublicKeyJSON]


class _CreatedResourceResponseJSON(TypedDict):
    """Response JSON for resource creation."""

    id: Union[str, int]


class _CreateProjectResponseJSON(TypedDict):
    """Response JSON for project creation."""

    projectId: str


class _ProjectJSON(TypedDict):
    """Project JSON from Hub."""

    id: str
    name: str
    role: str
    created_at: str
    updated_at: str
    status: Literal["PUBLISHED", "ARCHIVED"]
    isDemo: bool


class _GetProjectsPagedResponseJSON(TypedDict):
    """Response JSON from GET /api/pods/[userName]/[podName]."""

    totalProjects: int
    projects: list[_ProjectJSON]


# Access Manager-related JSON
class _AccessManagerKeyResponseJSON(TypedDict):
    """Response JSON from GET /api/access-manager-key."""

    accessManagerPublicKey: str


class _OIDCAccessCheckPostJSON(TypedDict):
    """Required keys for OIDC JSON POST /api/access."""

    podIdentifier: str
    modellerProtocolRequest: SerializedProtocol
    modellerName: str
    modellerToken: str
    identityProvider: Literal["OIDC"]
    projectId: NotRequired[Optional[str]]


class _SignatureBasedAccessCheckPostJSON(TypedDict):
    """Required keys for Signatured based JSON POST /api/access.

    NOTE: unsignedTask and taskSignature are byte-strings but will need to be b64
          encoded to allow them to be sent as JSON.
    """

    podIdentifier: str
    modellerName: str
    modellerProtocolRequest: SerializedProtocol
    unsignedTask: str  # b64 encoded byte-string
    taskSignature: str  # b64 encoded byte-string
    identityProvider: Literal["SIGNATURE"]
    projectId: NotRequired[Optional[str]]
    publicKeyId: NotRequired[Optional[str]]


class _AMAccessCheckResponseJSON(TypedDict):
    """Response JSON from Access Manager access check.

    Covers:
        - POST /api/access
    """

    code: Literal[
        # Common response types
        "ACCEPT",
        # /api/access response types
        "NO_ACCESS",
        "INVALID_PROOF_OF_IDENTITY",
        "UNAUTHORISED",
        "NO_PROOF_OF_IDENTITY",
    ]
    limits: Optional[List[_AMResourceUsageAndLimitJSON]]


# Auth0 related types
class _DeviceCodeRequestDict(TypedDict):
    """Data dictionary for POST request to /oauth/device/code.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow
    """

    audience: str
    scope: str
    client_id: str


class _DeviceCodeResponseJSON(TypedDict):
    """JSON response for POST /oauth/device/code.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow
    """

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class _DeviceAccessTokenRequestDict(TypedDict):
    """Data dictionary for device code POST request to /oauth/token.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow48
    """

    grant_type: Literal["urn:ietf:params:oauth:grant-type:device_code"]
    client_id: str
    device_code: str


class _DeviceAccessTokenResponseJSON(TypedDict):
    """Success JSON response for POST /oauth/token.

    For Device Authorization Flow.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow48
    """

    access_token: str
    id_token: str
    refresh_token: str
    scope: str
    expires_in: int
    token_type: Literal["Bearer"]


class _TokenRefreshRequestDict(TypedDict):
    """Data dictionary for token refresh POST request to /oauth/token.

    This is not the full potential params, but is enough for us.

    See: https://auth0.com/docs/api/authentication?http#refresh-token
    """

    grant_type: Literal["refresh_token"]
    client_id: str
    refresh_token: str


class _TokenRefreshResponseJSON(TypedDict):
    """Success JSON response for refresh token POST /oauth/token.

    See: https://auth0.com/docs/api/authentication?http#refresh-token

    Note that our response will include a new refresh token as we are using
    refresh token rotation.

    See: https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation
    """

    access_token: str
    id_token: str
    refresh_token: str  # see docstring
    scope: str
    expires_in: int
    token_type: Literal["Bearer"]


class _DeviceAccessTokenFailResponseJSON(TypedDict):
    """Fail JSON response for POST /oauth/token.

    For Device Authorization Flow.

    See: https://auth0.com/docs/api/authentication?http#device-authorization-flow48
    """

    error: str
    error_description: str


class _PKCEAccessTokenRequestDict(TypedDict):
    """Data dictionary for ACF with PKCE code POST request to /oauth/token.

    See: https://auth0.com/docs/api/authentication?http#authorization-code-flow-with-pkce45
    """  # noqa: E501

    grant_type: Literal["authorization_code"]
    client_id: str
    code: str
    code_verifier: str
    redirect_uri: str


class _PKCEAccessTokenResponseJSON(TypedDict):
    """Success JSON response for POST /oauth/token.

    For Authorization Code Flow with PKCE.

    See: https://auth0.com/docs/api/authentication?http#authorization-code-flow-with-pkce45
    """  # noqa: E501

    access_token: str
    refresh_token: str
    id_token: str
    token_type: Literal["Bearer"]
    expires_in: int


class _SimpleUsageJSON(TypedDict):
    """Base JSON return corresponding to model usage/limits.

    Corresponds to '#/components/schemas/SimpleUsage'.

    Returned as array from GET:/api/projects/[projectId]/limits
    """

    resourceType: Literal["MODEL_INFERENCE"]
    resourceName: str
    limit: NotRequired[Optional[int]]
    totalUsage: int


_ProjectLimitsJSON = list[_SimpleUsageJSON]
"""JSON return for project usage/limits.

Contains information for each model associated with the project task.

Returned from GET:/api/projects/[projectId]/limits
"""


class _ProjectMemberUsageJSON(_SimpleUsageJSON):
    """JSON for specific project+user+model usage/limits.

    Corresponds to '#/components/schemas/ProjectMemberUsage'.
    """

    granteeUsername: str
    role: str


class _ProjectModelLimitsJSON(TypedDict):
    """JSON return for project+model usage/limits.

    Corresponds to '#/components/schemas/Limits'.

    Returned from GET:/api/projects/[projectId]/limits/models/[...resourceIdentifier]
    """

    default: NotRequired[Optional[int]]
    totalGrantees: int
    usage: list[_ProjectMemberUsageJSON]


class _AMResourceUsageAndLimitJSON(_SimpleUsageJSON):
    """Contains the user's limit and usage data for a resource.

    Corresponds to '#/components/schemas/ResourcesWithLimitsForUser'

    Type is returned as part of the access manager check access response.
    """

    modelDownloadUrl: NotRequired[Optional[str]]
    weightsDownloadUrl: NotRequired[Optional[str]]


#####################################
# SMART on FHIR JSON Objects: Start #
#####################################
class _PairingBaseJSON(TypedDict):
    """Shared JSON elements for pairings from SMART on FHIR /api/pairings."""

    id: str  # uuid
    ownerUsername: str
    createdAt: str  # datetime
    updatedAt: str  # datetime
    expiresAt: str  # datetime
    clientPublicKey: NotRequired[Optional[str]]
    clientIpAddress: NotRequired[Optional[str]]


class _InitialisedPairingJSON(_PairingBaseJSON):
    """Initialised pairings JSON elements from SMART on FHIR /api/pairings."""

    state: Literal["initialised"]
    pairingCode: str


class _PairedPairingJSON(_PairingBaseJSON):
    """Paired pairings JSON elements from SMART on FHIR /api/pairings."""

    state: Literal["paired"]
    resourceServer: str  # "http://localhost:4013/v/r3/fhir"
    remoteUser: NotRequired[  # A string that identifies the user in the resourceServer # noqa: E501
        Optional[str]
    ]


class _NextGenContext(TypedDict):
    """NextGen context dict entry for SMART on FHIR session return."""

    enterpriseId: NotRequired[Optional[str]]
    practiceId: NotRequired[Optional[str]]
    locationId: NotRequired[Optional[str]]
    providerId: NotRequired[Optional[str]]


class _SMARTOnFHIRSessionContextDict(TypedDict):
    """Context dict for SMART on FHIR session return."""

    nextgen: NotRequired[Optional[_NextGenContext]]


class _SMARTOnFHIRSessionJSON(TypedDict):
    """JSON response for SMART on FHIR /api/pairings/session."""

    type: Literal["confidentialClient"]
    accessToken: str
    context: NotRequired[Optional[_SMARTOnFHIRSessionContextDict]]


@dataclass
class SMARTOnFHIRAccessToken:
    """Wrapper for access token and metadata from NextGen."""

    token: str
    valid_until: Optional[datetime] = None
    context: Optional[_NextGenContext] = None


###################################
# SMART on FHIR JSON Objects: End #
###################################
