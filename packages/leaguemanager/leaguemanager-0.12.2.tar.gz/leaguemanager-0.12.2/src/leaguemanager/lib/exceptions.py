from http import HTTPStatus
from typing import Any


class LeagueManagerException(Exception):
    """Base exception class for League Manager errors."""

    detail: str

    def __init__(self, *args: Any, detail: str = "") -> None:
        str_args = [str(arg) for arg in args if arg]
        if not detail:
            if str_args:
                detail, *str_args = str_args
            elif hasattr(self, "detail"):
                detail = self.detail
        self.detail = detail
        super().__init__(*str_args)

    def __repr__(self) -> str:
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__

    def __str__(self) -> str:
        return " ".join((*self.args, self.detail)).strip()


class PermissionDenied(LeagueManagerException, ValueError):
    """Exception raised for permission denied errors."""


class ApplicationClientError(LeagueManagerException):
    """Exception raised for application client errors."""


class HTTPException(LeagueManagerException):
    """Base exception for HTTP error responses.

    These exceptions carry information to construct an HTTP response.
    """

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    """Exception status code."""
    detail: str
    """Exception details or message."""
    headers: dict[str, str] | None
    """Headers to attach to the response."""
    extra: dict[str, Any] | list[Any] | None
    """An extra mapping to attach to the exception."""

    def __init__(
        self,
        *args: Any,
        detail: str = "",
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        extra: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        """Initialize ``HTTPException``.

        Set ``detail`` and ``args`` if not provided.

        Args:
            *args: if ``detail`` kwarg not provided, first arg should be error detail.
            detail: Exception details or message. Will default to args[0] if not provided.
            status_code: Exception HTTP status code.
            headers: Headers to set on the response.
            extra: An extra mapping to attach to the exception.
        """
        super().__init__(*args, detail=detail)
        self.status_code = status_code or self.status_code
        self.extra = extra
        self.headers = headers
        if not self.detail:
            self.detail = HTTPStatus(self.status_code).phrase
        self.args = (f"{self.status_code}: {self.detail}", *self.args)

    def __repr__(self) -> str:
        return f"{self.status_code} - {self.__class__.__name__} - {self.detail}"

    def __str__(self) -> str:
        return " ".join(self.args).strip()
