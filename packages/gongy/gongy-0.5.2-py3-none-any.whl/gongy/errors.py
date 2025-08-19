"""Exceptions."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "AccessDeniedError",
    "CallIDNotFoundError",
    "GongError",
    "MalformedRequestError",
    "NoCallsFoundError",
    "NotFoundError",
    "RequestLimitExceededError",
    "UnexpectedError",
)

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:  # pragma: no cover
    from typing import ClassVar

    from gongy.models import RequestID


class GongErrorInfo(TypedDict, total=False):
    """TypedDict for Gong error information."""

    requestId: RequestID
    errors: list[str]


class GongError(Exception):
    """Base class for all Gong errors."""

    status: ClassVar[int]

    def __init__(
        self,
        message: str | None = None,
        request_id: RequestID | None = None,
        errors: list[str] | None = None,
    ) -> None:
        """Initialize Gong error."""
        super().__init__(message)
        self.request_id = request_id
        self.errors = errors

    def __repr__(self) -> str:
        """Return a string representation of the error."""
        return (
            f"{self.__class__.__name__}(message={self.args[0]!r}, "
            f"request_id={self.request_id!r}, errors={self.errors!r})"
        )


class MalformedRequestError(GongError):
    """Exception raised for malformed requests.

    Code: 400
    """

    status = 400


class AccessDeniedError(GongError):
    """Exception raised for access denied errors.

    Code: 401
    """

    status = 401


class NotFoundError(GongError):
    """Exception raised for not found errors.

    Code: 404
    """

    status = 404


class NoCallsFoundError(NotFoundError):
    """Exception raised when no calls are found.

    Code: 404
    """

    status = 404


class CallIDNotFoundError(NotFoundError):
    """Exception raised when a call ID is not found.

    Code: 404
    """

    status = 404


class RequestLimitExceededError(GongError):
    """Exception raised when the request limit is exceeded.

    Code: 429
    """

    status = 429


class UnexpectedError(GongError):
    """Exception raised for unexpected errors.

    Code: 500
    """

    status = 500
