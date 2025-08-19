"""Exceptions for the MontyCloud Day2 SDK."""

from typing import Optional


class Day2Error(Exception):
    """Base exception class for MontyCloud Day2 SDK."""


class ClientError(Day2Error):
    """Raised when a client-side error occurs (4xx)."""

    def __init__(
        self, message: str, status_code: int, request_id: Optional[str] = None
    ):
        self.status_code = status_code
        self.request_id = request_id
        super().__init__(f"{message} (Status: {status_code}, RequestId: {request_id})")


class ServerError(Day2Error):
    """Raised when a server-side error occurs (5xx)."""

    def __init__(
        self, message: str, status_code: int, request_id: Optional[str] = None
    ):
        self.status_code = status_code
        self.request_id = request_id
        super().__init__(f"{message} (Status: {status_code}, RequestId: {request_id})")


class ValidationError(ClientError):
    """Raised when request validation fails."""


class ResourceNotFoundError(ClientError):
    """Raised when a requested resource is not found."""

    def __init__(
        self, message: str, status_code: int = 404, request_id: Optional[str] = None
    ):
        super().__init__(message, status_code, request_id)


class AuthenticationError(ClientError):
    """Raised when authentication fails."""


class TenantContextError(ClientError):
    """Raised when there's an issue with tenant context."""

    def __init__(
        self, message: str, status_code: int = 400, request_id: Optional[str] = None
    ):
        super().__init__(message, status_code, request_id)


class ProfileNotFoundError(Day2Error):
    """Raised when a specified profile is not found."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Profile '{profile_name}' not found")
