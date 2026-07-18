"""Custom exception definitions for the application domain."""

from __future__ import annotations


class AppError(Exception):
    """Base exception for application-level failures."""


class ConfigurationError(AppError):
    """Raised when required runtime configuration is invalid."""


class PersistenceError(AppError):
    """Raised when database interaction fails."""


class UploadError(AppError):
    """Raised when an uploaded file is invalid or cannot be stored."""


class ParsingError(AppError):
    """Raised when an uploaded template cannot be parsed into normalized resources."""
