"""Utilities/patches for working with non-standard SSL configurations.

Adds the ability to work with trusted root CAs that are stored in the system
truststore.

:::note

In order for some of these patches to work properly, they must be made BEFORE
imports of requests, urllib3, etc., happen.

:::
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import platform
import ssl
import subprocess  # nosec B404 # import-subprocess # subprocess usage is acceptable/necessary here  # noqa: E501
import tempfile
from typing import Union

from bitfount import config

_logger = logging.getLogger(__name__)

_HTTP_PROXY_ENVVAR = "HTTP_PROXY"
_HTTPS_PROXY_ENVVAR = "HTTPS_PROXY"
_ALL_PROXY_ENVVAR = "ALL_PROXY"
_GRPC_PROXY_ENVVAR = "grpc_proxy"


def _get_clean_url(url: str) -> str:
    """Attempts to return a cleaned URL with the password redacted.

    If the URL is not in a format that can be parsed (or is not even a URL) then
    the original string will be returned.
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        replaced = parsed._replace(
            netloc="{}:{}@{}:{}".format(
                parsed.username, "**REDACTED**", parsed.hostname, parsed.port
            )
        )
        return replaced.geturl()
    except Exception:
        return url


def _set_envvars_case_insensitive(*envvars: str, value: str) -> None:
    """Sets a list of case-insensitive envvars to a value.

    Will set both the upper-case and lower-case versions of the environment
    variables to `value`.
    """
    for i in envvars:
        os.environ[i.upper()] = value
        os.environ[i.lower()] = value
        _logger.debug(
            f"ENVIRONMENT: {i.upper()} and {i.lower()} envvars set to "
            f"{_get_clean_url(value)}"
        )


def _set_proxies() -> None:
    """Sets the appropriate proxies using already supplied proxy information.

    Will use system proxies or environment variables to automatically set the
    following proxies (if not provided):
        - HTTP_PROXY
        - HTTPS_PROXY
        - grpc_proxy

    If HTTP_PROXY is not provided, will default to HTTPS_PROXY.

    If HTTPS_PROXY is not provided, will default to HTTP_PROXY.

    If grpc_proxy is not provided, will default to HTTPS_PROXY and then HTTP_PROXY.

    ALL_PROXY will override any other provided proxy information.
    """
    import urllib.request

    proxies = urllib.request.getproxies()

    if all_proxy := proxies.get("all"):
        _logger.debug(f"{_ALL_PROXY_ENVVAR} provided; setting all proxies to this")
        _set_envvars_case_insensitive(
            _HTTP_PROXY_ENVVAR,
            _HTTPS_PROXY_ENVVAR,
            _ALL_PROXY_ENVVAR,
            _GRPC_PROXY_ENVVAR,
            value=all_proxy,
        )
        return

    http_proxy = proxies.get("http")
    https_proxy = proxies.get("https")
    grpc_proxy = proxies.get("grpc")

    # If HTTP proxy is provided, use that, otherwise try to use the HTTPS proxy
    # if provided
    if http_proxy:
        _set_envvars_case_insensitive(_HTTP_PROXY_ENVVAR, value=http_proxy)
    elif https_proxy:
        _logger.debug("No HTTP proxy provided; setting HTTP proxy to HTTPS proxy")
        _set_envvars_case_insensitive(_HTTP_PROXY_ENVVAR, value=https_proxy)
    else:
        _logger.warning("Unable to determine HTTP proxy")

    # If HTTPS proxy is provided, use that, otherwise try to use the HTTP proxy
    # if provided
    if https_proxy:
        _set_envvars_case_insensitive(_HTTPS_PROXY_ENVVAR, value=https_proxy)
    elif http_proxy:
        _logger.debug("No HTTPS proxy provided; setting HTTPS proxy to HTTP proxy")
        _set_envvars_case_insensitive(_HTTPS_PROXY_ENVVAR, value=http_proxy)
    else:
        _logger.warning("Unable to determine HTTPS proxy")

    # If gRPC proxy is provided, use that, otherwise try to use the HTTPS proxy
    # or HTTP proxy in order
    if grpc_proxy:
        _set_envvars_case_insensitive(_GRPC_PROXY_ENVVAR, value=grpc_proxy)
    elif https_proxy:
        _logger.debug("No gRPC proxy provided; setting gRPC proxy to HTTPS proxy")
        _set_envvars_case_insensitive(_GRPC_PROXY_ENVVAR, value=https_proxy)
    elif http_proxy:
        _logger.debug("No gRPC proxy provided; setting gRPC proxy to HTTP proxy")
        _set_envvars_case_insensitive(_GRPC_PROXY_ENVVAR, value=http_proxy)
    else:
        _logger.warning("Unable to determine gRPC proxy")


def _get_root_CAs_macos() -> str:
    """Loads root CAs from macOS truststores.

    Assumes any custom CAs will be in the "System" or "SystemRootCertificates"
    keychains.

    Returns:
        The set of trusted root CAs as a single string containing multiple
        PEM-formatted keys.
    """
    # NOTE: Have to use macOS's "security" command to interact with the keychains
    #       and export the certificates to the desired PEM bundle format.
    _logger.debug("Retrieving CA certificates from System keychain")
    system_ca_certs = subprocess.run(  # nosec start_process_with_partial_path, subprocess_without_shell_equals_true # no untrusted input, partial path for `security` is fine # noqa: E501
        [
            "security",
            "export",
            "-t",
            "certs",
            "-f",
            "pemseq",
            "-k",
            "/Library/Keychains/System.keychain",
        ],
        capture_output=True,
        check=True,
        encoding="utf-8",
    ).stdout

    _logger.debug("Retrieving CA certificates from SystemRoots keychain")
    system_roots_ca_certs = subprocess.run(  # nosec start_process_with_partial_path, subprocess_without_shell_equals_true # no untrusted input, partial path for `security` is fine # noqa: E501
        [
            "security",
            "export",
            "-t",
            "certs",
            "-f",
            "pemseq",
            "-k",
            "/System/Library/Keychains/SystemRootCertificates.keychain",
        ],
        capture_output=True,
        check=True,
        encoding="utf-8",
    ).stdout

    if not system_ca_certs:
        system_ca_certs = ""
    if not system_roots_ca_certs:
        system_roots_ca_certs = ""

    return system_ca_certs + system_roots_ca_certs


def _get_root_CAs_non_mac() -> str:
    """Loads root CAs for non-macOS platforms.

    Makes use of the Python ssl module's native support for pulling in CAs from the
    platform's truststores, if appropriate. This is primarily important on Windows.

    Returns:
        The set of trusted root CAs as a single string containing multiple
        PEM-formatted keys.
    """
    _logger.debug(
        "Loading default certs for platform;"
        " on Windows this will include any certificates in the truststore"
    )
    c = ssl.create_default_context()
    c.load_default_certs()
    der_certs = c.get_ca_certs(binary_form=True)
    pem_certs = [ssl.DER_cert_to_PEM_cert(i) for i in der_certs]
    return "".join(pem_certs)


def _create_pem_bundle(pems: str) -> Path:
    """Writes out the PEM-formatted CAs to a bundle.

    Writes to a TMP_DIR file, unless config.settings.paths.proxy_cert_dir is set.

    :::note

    As this is needed throughout we don't delete the tempfile created but
    instead rely on the OS's inherent removal of tempfiles.

    :::

    Returns:
        The path to the PEM-formatted bundle of root CAs on the filesystem.
    """
    cert_dir: Path
    if config.settings.paths.proxy_cert_dir:
        cert_dir = config.settings.paths.proxy_cert_dir
        cert_dir.mkdir(parents=True, exist_ok=True)
    else:
        cert_dir = Path(tempfile.mkdtemp())

    cert_file = (cert_dir / "caRootCerts.pem").absolute()

    _logger.debug(f"Combining all trusted root CAs into bundle at {str(cert_file)}")
    with open(cert_file, "w") as f:
        f.write(pems)

    return cert_file


def _set_certificates(cert_file: Union[str, Path]) -> None:
    """Sets the appropriate envvars to use the custom certificate file."""
    if "REQUESTS_CA_BUNDLE" not in os.environ:
        os.environ["REQUESTS_CA_BUNDLE"] = str(cert_file)
    if "CURL_CA_BUNDLE" not in os.environ:
        os.environ["CURL_CA_BUNDLE"] = str(cert_file)
    if "SSL_CERT_FILE" not in os.environ:
        os.environ["SSL_CERT_FILE"] = str(cert_file)
    if "GRPC_DEFAULT_SSL_ROOTS_FILE_PATH" not in os.environ:
        os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = str(cert_file)

    _logger.debug(f"ENVIRONMENT: REQUESTS_CA_BUNDLE={os.environ['REQUESTS_CA_BUNDLE']}")
    _logger.debug(f"ENVIRONMENT: CURL_CA_BUNDLE={os.environ['CURL_CA_BUNDLE']}")
    _logger.debug(f"ENVIRONMENT: SSL_CERT_FILE={os.environ['SSL_CERT_FILE']}")
    _logger.debug(
        f"ENVIRONMENT: GRPC_DEFAULT_SSL_ROOTS_FILE_PATH="
        f"{os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH']}"
    )


def inject_ssl_proxy_support() -> None:
    """Injects support for HTTPS proxy connections with custom SSL certificates.

    Proxies that handle HTTPS connections will normally require the proxy's root
    CA to be added as a trusted CA so that it can handle the wrapping/unwrapping
    of SSL connections.

    This function utilises the system truststores to add this support into Python's
    various HTTP(S) connection capabilities so that Bitfount can be used transparently
    from behind a corporate proxy.

    :::note

    The proxy details must still be provided to Python in some cases where
    it can't automatically detect the proxy from the system. The HTTP_PROXY
    and HTTPS_PROXY environment variables can be used to supply the details
    to the Python process.

    :::
    """
    _logger.debug("Injecting custom root CA support to enable HTTPS proxies")
    if system := platform.system() == "Darwin":
        pem_certs = _get_root_CAs_macos()
    elif system != "":
        pem_certs = _get_root_CAs_non_mac()
    else:
        raise ValueError("Could not determine platform")

    _cert_file = _create_pem_bundle(pem_certs)
    _set_certificates(_cert_file)

    # Need to set proxies after CA creation/setting as needs to import urllib.request
    _logger.debug("Setting proxy support")
    _set_proxies()
