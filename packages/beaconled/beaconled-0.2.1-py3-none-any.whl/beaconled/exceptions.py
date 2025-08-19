"""Custom exceptions for the Beacon Delivery Compass application.

This module defines custom exceptions with error codes for better programmatic
handling. Each exception includes a unique error code and a human-readable
message.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, TypedDict


class ErrorDetail(TypedDict, total=False):
    """Type for error details dictionary."""

    message: str
    code: str
    details: dict[str, Any]


class ErrorCode(str, Enum):
    """Standard error codes for the application."""

    UNKNOWN = "unknown_error"
    VALIDATION = "validation_error"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    UNAUTHORIZED = "unauthorized"
    CONFLICT = "conflict"
    BAD_REQUEST = "bad_request"
    TIMEOUT = "timeout"
    NETWORK = "network_error"
    CONFIGURATION = "configuration_error"
    NOT_IMPLEMENTED = "not_implemented"
    INTERNAL = "internal_error"
    GIT_ERROR = "git_error"
    INVALID_DATE = "invalid_date"
    INVALID_TIMEZONE = "invalid_timezone"
    INVALID_COMMIT = "invalid_commit"
    INVALID_REPOSITORY = "invalid_repository"
    REPOSITORY_NOT_FOUND = "repository_not_found"
    COMMIT_NOT_FOUND = "commit_not_found"
    BRANCH_NOT_FOUND = "branch_not_found"
    TAG_NOT_FOUND = "tag_not_found"
    ANALYZER_ERROR = "analyzer_error"
    FORMATTER_ERROR = "formatter_error"
    INTEGRATION_ERROR = "integration_error"
    DATE_ERROR = "date_error"
    DATE_PARSE_ERROR = "date_parse_error"
    DATE_RANGE_ERROR = "date_range_error"


class BeaconError(Exception):
    """Base exception class for all application-specific exceptions.

    Attributes:
        error_code: A unique error code from the ErrorCode enum
        message: Human-readable error message
        details: Additional error details (optional)
    """

    DEFAULT_ERROR_CODE = ErrorCode.UNKNOWN

    def __init__(
        self,
        message: str,
        error_code: ErrorCode | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.error_code = error_code or self.DEFAULT_ERROR_CODE
        self.details = details.copy() if details else {}
        super().__init__(message)


class ConfigurationError(BeaconError):
    """Raised when there is a configuration error."""

    DEFAULT_ERROR_CODE = ErrorCode.CONFIGURATION


class ValidationError(BeaconError):
    """Raised when input validation fails.

    Attributes:
        message: Explanation of the validation error
        field: The field that failed validation (optional)
        value: The value that caused the validation to fail (optional)
        error_code: Specific error code (defaults to VALIDATION)
    """

    DEFAULT_ERROR_CODE = ErrorCode.VALIDATION

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: object | None = None,
        error_code: ErrorCode | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        self.value = value
        details = details or {}
        if field is not None:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(
            message=message,
            error_code=error_code or self.DEFAULT_ERROR_CODE,
            details=details,
        )


class RepositoryError(BeaconError):
    """Base class for repository-related errors."""

    DEFAULT_ERROR_CODE = ErrorCode.INVALID_REPOSITORY


class InvalidRepositoryError(RepositoryError):
    """Raised when the repository path is invalid or not a git repository."""

    DEFAULT_ERROR_CODE = ErrorCode.INVALID_REPOSITORY

    def __init__(
        self,
        repo_path: str,
        reason: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.repo_path = repo_path
        self.reason = reason
        message = f"Invalid repository: {repo_path}"
        if reason:
            message += f" ({reason})"

        details = kwargs.pop("details", {})
        details["repo_path"] = repo_path
        if reason:
            details["reason"] = reason

        super().__init__(message=message, details=details, **kwargs)


class CommitError(BeaconError):
    """Base class for commit-related errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INVALID_COMMIT,
        commit_hash: str | None = None,
        commit_ref: str | None = None,
        details: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        # Initialize a new dictionary to avoid modifying the input
        safe_details: dict[str, Any] = {}

        # Copy details if provided
        if details is not None:
            safe_details.update(details)

        # Add any additional details from kwargs (except special parameters)
        special_params = {"details", "error_code", "commit_hash", "commit_ref"}
        for key, value in kwargs.items():
            if key not in special_params and not key.startswith("_"):
                safe_details[key] = value

        # Add commit hash to details if provided
        if commit_hash is not None:
            safe_details["commit_hash"] = commit_hash

        # Add commit ref to details if provided
        if commit_ref is not None:
            safe_details["commit_ref"] = commit_ref

        # Call parent with properly typed arguments
        super().__init__(
            message=message,
            error_code=error_code,
            details=safe_details,
        )
        self.commit_hash = commit_hash

    @classmethod
    def with_reason(
        cls,
        commit_ref: str,
        reason: str | None = None,
        **kwargs: Any,
    ) -> CommitError:
        """Create a CommitError with a reason.

        Args:
            commit_ref: The commit reference that caused the error
            reason: Optional reason for the error
            **kwargs: Additional arguments to pass to the exception

        Returns:
            A configured CommitError instance
        """
        message = f"Error with commit {commit_ref}"
        if reason:
            message += f": {reason}"

        details: dict[str, Any] = {}
        details["commit_ref"] = commit_ref
        if reason:
            details["reason"] = reason

        # Filter out any 'details' from kwargs to avoid duplication
        kwargs_without_details = {k: v for k, v in kwargs.items() if k != "details"}
        details.update(kwargs_without_details)

        return cls(message=message, details=details)


class CommitNotFoundError(CommitError):
    """Raised when a commit cannot be found in the repository."""

    DEFAULT_ERROR_CODE = ErrorCode.COMMIT_NOT_FOUND

    def __init__(
        self,
        commit_ref: str,
        repo_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        message = f"Commit not found: {commit_ref}"
        details: dict[str, Any] = {}

        # Get any existing details from kwargs
        if "details" in kwargs and isinstance(kwargs["details"], dict):
            details.update(kwargs["details"])
            del kwargs["details"]

        # Add commit reference to details
        details["commit_ref"] = commit_ref

        # Add repo path to details if provided
        if repo_path is not None:
            details["repo_path"] = repo_path
            message += f" in repository {repo_path}"

        # Extract specific parameters for the parent class
        error_code = kwargs.pop("error_code", self.DEFAULT_ERROR_CODE)
        commit_hash = kwargs.pop("commit_hash", None)

        # Call parent with properly typed arguments
        super().__init__(
            message=message,
            error_code=error_code,
            commit_hash=commit_hash,
            commit_ref=commit_ref,
            details=details,
        )


class CommitParseError(CommitError):
    """Raised when there's an error parsing commit data."""

    DEFAULT_ERROR_CODE = ErrorCode.INVALID_COMMIT

    def __init__(
        self,
        commit_ref: str,
        parse_error: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        message = f"Failed to parse commit: {commit_ref}"

        # Initialize a new dictionary for details
        details: dict[str, Any] = {}

        # Get any existing details from kwargs
        if "details" in kwargs and isinstance(kwargs["details"], dict):
            details.update(kwargs["details"])
            del kwargs["details"]

        # Add commit reference to details
        details["commit_ref"] = commit_ref

        # Add parse error details if available
        if parse_error is not None:
            details["parse_error"] = str(parse_error)
            message += f" - {parse_error!s}"

        # Extract specific parameters for the parent class
        error_code = kwargs.pop("error_code", self.DEFAULT_ERROR_CODE)
        commit_hash = kwargs.pop("commit_hash", None)

        # Call parent with properly typed arguments
        super().__init__(
            message=message,
            error_code=error_code,
            commit_hash=commit_hash,
            commit_ref=commit_ref,
            details=details,
        )


# DateRangeError has been moved to core.date_errors module
