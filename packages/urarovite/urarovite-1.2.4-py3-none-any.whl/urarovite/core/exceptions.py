"""Custom exceptions for the Urarovite validation library."""

from typing import Any


class ValidationError(Exception):
    """Base exception for validation errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class AuthenticationError(ValidationError):
    """Raised when Google Sheets authentication fails."""

    pass


class SheetAccessError(ValidationError):
    """Raised when unable to access or read from Google Sheets."""

    pass
