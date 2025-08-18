"""Vardef client exceptions."""

import json
from functools import wraps
from http import HTTPStatus
from types import MappingProxyType

import urllib3
from pytz import UnknownTimeZoneError
from ruamel.yaml.error import YAMLError

from dapla_metadata.variable_definitions._generated.vardef_client.exceptions import (
    OpenApiException,
)
from dapla_metadata.variable_definitions._generated.vardef_client.exceptions import (
    UnauthorizedException,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions._utils._client import VardefClient
from dapla_metadata.variable_definitions._utils.constants import (
    PUBLISHING_BLOCKED_ERROR_MESSAGE,
)
from dapla_metadata.variable_definitions._utils.constants import VARDEF_PROD_URL

# Use MappingProxyType so the dict is immutable
STATUS_EXPLANATIONS: MappingProxyType[HTTPStatus | None, str] = MappingProxyType(
    {
        HTTPStatus.BAD_REQUEST: "There was a problem with the supplied data. Please review the data you supplied based on the details below.",
        HTTPStatus.UNAUTHORIZED: "There is a problem with your token, it may have expired. Try logging out, logging in and trying again.",
        HTTPStatus.FORBIDDEN: "Forbidden. You don't have access to this, possibly because your team is not an owner of this variable definition.",
        HTTPStatus.NOT_FOUND: "The variable definition was not found, check that the `short_name` or `id` is correct and that the variable exists.",
        HTTPStatus.METHOD_NOT_ALLOWED: "That won't work here. The status of your variable definition likely doesn't allow for this to happen.",
        HTTPStatus.CONFLICT: "There was a conflict with existing data. Please change your data and try again.",
        None: "",
    },
)


class VardefClientError(Exception):
    """Custom exception to represent errors encountered in the Vardef client.

    This exception extracts and formats error details from a JSON response body
    provided by the Vardef API, enabling more descriptive error messages.
    If the response body cannot be parsed as JSON or lacks expected keys,
    default values are used to provide meaningful feedback.
    """

    def __init__(self, response_body: str) -> None:
        """Initialize the exception with a JSON-formatted response body.

        Args:
            response_body (str): The JSON string containing error details
                                from the Vardef API response.

        Attributes:
            status (str): The status code from the response, or "Unknown status"
                        if not available or the response is invalid.
            detail (str || list): A detailed error message from the response, or
                        "No detail provided" if not provided. If "Constraint violation"
                        detail contains 'field' and 'message'.
            response_body (str): The raw response body string, stored for
                                debugging purposes.
        """
        self.status: int | None = None
        self.detail: str = ""
        try:
            data = json.loads(response_body)
            self.status = data.get("status")
            if data.get("title") == "Constraint Violation":
                violations = data.get("violations", [])
                self.detail = "\n" + "\n".join(
                    f"{violation.get('field', 'Unknown field')}: {violation.get('message', 'No message provided')}"
                    for violation in violations
                )
            else:
                self.detail = data.get("detail")

            if self.detail:
                self.detail = f"\nDetail: {self.detail}"
            self.response_body = response_body
        except (json.JSONDecodeError, TypeError):
            self.detail = "Could not decode error response from API"

        super().__init__(
            f"{self._get_status_explanation(self.status)}{self.detail if self.detail else ''}",
        )

    @staticmethod
    def _get_status_explanation(status: int | None) -> str:
        return (
            ""
            if not status
            else (STATUS_EXPLANATIONS.get(HTTPStatus(status)) or f"Status {status}:")
        )


def vardef_exception_handler(method):  # noqa: ANN201, ANN001
    """Decorator for handling exceptions in Vardef."""

    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):  # noqa: ANN001, ANN002, ANN003
        try:
            return method(self, *method_args, **method_kwargs)
        except urllib3.exceptions.HTTPError as e:
            # Catch all urllib3 exceptions by catching the base class.
            # These exceptions typically arise from lower level network problems.
            raise VardefClientError(
                json.dumps(
                    {
                        "status": None,
                        "title": "Network problems",
                        "detail": f"""There was a network problem when sending the request to the server. Try again shortly.
Original exception:
{getattr(e, "message", repr(e))}""",
                    },
                ),
            ) from e
        except UnauthorizedException as e:
            raise VardefClientError(
                json.dumps(
                    {
                        "status": e.status,
                        "title": "Unauthorized",
                        "detail": "Unauthorized",
                    },
                ),
            ) from e
        except OpenApiException as e:
            raise VardefClientError(e.body) from e

    return _impl


class VariableNotFoundError(Exception):
    """Custom exception for when a variable is not found.

    Attributes:
        message (str): Message describing the error.
    """

    def __init__(self, message: str) -> None:
        """Initialize the VariableNotFoundError.

        Args:
            message (str): Description of the error.
        """
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Return the string representation of the exception."""
        return f" {self.message}"


class VardefFileError(Exception):
    """Custom exception for catching errors related to variable definition file handling.

    Attributes:
        message (str): Message describing the error.
    """

    def __init__(self, message: str, *args) -> None:  # noqa: ANN002
        """Accepting the message and any additional arguments."""
        super().__init__(message, *args)
        self.message = message
        self.args = args

    def __str__(self) -> str:
        """Returning a custom string representation of the exception."""
        return f"VardefFileError: {self.message}"


def vardef_file_error_handler(method):  # noqa: ANN201, ANN001
    """Decorator for handling exceptions when generating yaml files for variable definitions."""

    @wraps(method)
    def _impl(*method_args, **method_kwargs):  # noqa: ANN002, ANN003
        try:
            return method(
                *method_args,
                **method_kwargs,
            )
        except FileExistsError as e:
            msg = f"File already exists and can not be saved: {method_kwargs.get('file_path', 'unknown file path')}"
            raise VardefFileError(msg) from e
        except PermissionError as e:
            msg = f"Permission denied for file path when accessing the file. Original error: {e!s}"
            raise VardefFileError(msg) from e
        except UnknownTimeZoneError as e:
            msg = f"Timezone is unknown: {method_kwargs.get('time_zone', 'unknown')}"
            raise VardefFileError(msg) from e
        except YAMLError as e:
            msg = f"Invalid yaml. Please fix the formatting in your yaml file.\nOriginal error:\n{e!s}"
            raise VardefFileError(msg) from e
        except EOFError as e:
            msg = "Unexpected end of file"
            raise VardefFileError(msg) from e
        except NotADirectoryError as e:
            msg = f"Path is not a directory: {method_kwargs.get('file_path', 'unknown file path')}. Original error: {e!s}"
            raise VardefFileError(msg) from e

    return _impl


class PublishingBlockedError(RuntimeError):
    """Exception raised when publishing variable definitions is blocked in the production environment."""

    default_message = PUBLISHING_BLOCKED_ERROR_MESSAGE

    def __str__(self) -> str:
        """Return the default publishing blocked error message."""
        return self.default_message


def publishing_blocked_error_handler(method):  # noqa: ANN201, ANN001
    """Decorator that blocks publishing variable definitions in production.

    - If the environment is production:
        - If `variable_status` is present in the arguments and set to `PUBLISHED_INTERNAL` or `PUBLISHED_EXTERNAL`,
        publishing is blocked by raising a `PublishingBlockedError`.
        - If `variable_status` is set to `DRAFT`, the method is allowed to proceed.
        - If no arguments are provided, all publishing attempts are blocked.
    """

    @wraps(method)
    def _impl(*method_args, **method_kwargs):  # noqa: ANN002, ANN003
        try:
            client = VardefClient()
            host = client.get_config().host
        except VardefClientError as e:
            msg = f"Failed to get VardefClient config: {e}"
            raise RuntimeError(msg) from e

        if host == VARDEF_PROD_URL:
            if len(method_args) > 1:
                status = method_args[1].variable_status
                if status == VariableStatus.DRAFT:
                    return method(
                        *method_args,
                        **method_kwargs,
                    )
                if status in (
                    VariableStatus.PUBLISHED_INTERNAL,
                    VariableStatus.PUBLISHED_EXTERNAL,
                ):
                    raise PublishingBlockedError
            raise PublishingBlockedError
        return method(
            *method_args,
            **method_kwargs,
        )

    return _impl
