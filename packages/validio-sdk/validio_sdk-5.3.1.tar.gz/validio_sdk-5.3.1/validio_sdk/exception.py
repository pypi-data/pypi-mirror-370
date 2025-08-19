"""Exceptions used throughout the system."""

import os
from typing import Any

from aiohttp.client_exceptions import ClientConnectorError
from gql.transport.exceptions import TransportQueryError, TransportServerError


class ValidioError(Exception):
    """Base exception used for every exception thrown by Validio."""

    def __init__(self, *args: Any):
        """Construct the exception."""
        super().__init__(*args)


class ValidioTimeoutError(ValidioError):
    """Validio specific timeout error."""

    def __init__(self, method: str | None = None, timeout: int | float | None = None):
        """Construct the exception."""
        message = "Request timed out"

        if timeout is not None:
            maybe_method = f"{method} " if method is not None else ""
            message += (
                f": {maybe_method}did not respond within"
                f" {timeout}s or server canceled the request"
            )

        super().__init__(message)


class ValidioBugError(ValidioError):
    """Same as `ValidioError` but marked for bugs to be reported."""

    def __init__(self, *args: Any):
        """Construct the exception."""
        super().__init__(*args)

    def __str__(self) -> str:
        """String representation for the exception."""
        s = f"{super().__str__()}\n"
        s += "This is a bug, please report to support@validio.io"

        return s


class ConfigNotFoundError(ValidioError):
    """Exception when no configuration is found."""

    def __init__(
        self, endpoint_env: str, access_key_env: str, secret_access_key_env: str
    ) -> None:
        """Construct the exception."""
        super().__init__(
            "No configuration file found. Run 'validio config init' to create one or"
            f" set the environment variables '{endpoint_env}',"
            f" '{access_key_env}' and '{secret_access_key_env}'"
        )


class ConfigInvalidError(ValidioError):
    """Exception when the configuration file is invalid."""

    def __init__(self) -> None:
        """Construct the exception."""
        super().__init__("Configuration file is invalid.")


class UnauthorizedError(ValidioError):
    """Exception thrown when unauthorized request is made."""

    def __init__(self, access_key_env: str, secret_access_key_env: str) -> None:
        """Construct the exception."""
        super().__init__(
            "🛑 Unauthorized!\n"
            "Make sure you have proper credentials and run 'validio config init' to"
            f" add them or use '{access_key_env}' and"
            f" '{secret_access_key_env}'"
        )


class ForbiddenError(ValidioError):
    """Exception throw when doing forbidden request.

    This happens when trying to access API methods not allowed, e.g. adding
    resources to a namespace the API key is not part of.
    """

    def __init__(self) -> None:
        """Construct the exception."""
        super().__init__(
            "Forbidden request.\n"
            "Make sure the API key used has the right role and access to the "
            "given namespace."
        )


class ValidioConnectionError(ValidioError):
    """Exception thrown when connection to Validio backend fails."""

    def __init__(self, endpoint_env: str, e: Exception) -> None:
        """Construct the exception."""
        super().__init__(
            f"🛑 Failed to connect to server: {e!s}\n"
            "Check your network environment, run 'validio config init' to set a proper"
            f" server endpoint or use '{endpoint_env}'"
        )


def _show_trace() -> bool:
    return os.environ.get("VALIDIO_SHOW_TRACE") is not None


def _parse_error(
    e: ClientConnectorError | TransportQueryError | TransportServerError | TimeoutError,
    endpoint_env: str,
    access_key_env: str,
    secret_access_key_env: str,
    timeout: int | float | None = None,
) -> None:
    if _show_trace():
        raise e

    if isinstance(e, ClientConnectorError):
        raise ValidioConnectionError(endpoint_env, e)

    if isinstance(e, TransportQueryError):
        if not e.errors:
            raise e

        error_details = e.errors[0]
        extension_code = error_details.get("extensions", {}).get("code")

        if error_details.get("message", "").endswith("request timeout."):
            raise ValidioTimeoutError(timeout=timeout)

        match extension_code:
            case "INVALID_API_KEY":
                raise UnauthorizedError(access_key_env, secret_access_key_env)
            case "FORBIDDEN":
                raise ForbiddenError
            case _:
                raise e

    elif isinstance(e, TransportServerError):
        raise ValidioError(f"🛑 Server error: {e}")

    elif isinstance(e, TimeoutError):
        raise ValidioTimeoutError(timeout=timeout)

    else:
        raise e
