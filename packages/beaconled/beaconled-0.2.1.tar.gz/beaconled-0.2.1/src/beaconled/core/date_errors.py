"""Date-related exceptions for the Beacon Delivery Compass application.

This module contains exceptions specific to date parsing and validation.
"""

from datetime import datetime
from typing import Any

from beaconled.exceptions import ErrorCode, ValidationError


class DateError(ValidationError):
    """Base class for date-related errors."""

    DEFAULT_ERROR_CODE = ErrorCode.DATE_ERROR

    def __init__(
        self,
        message: str,
        error_code: ErrorCode | None = None,
        details: dict[str, Any] | None = None,
        field: str = "date",
    ) -> None:
        # Ensure details is a proper dictionary
        safe_details: dict[str, Any] = {}
        if details is not None:
            safe_details.update(details)
        safe_details["field"] = field

        super().__init__(
            message=message,
            field=field,
            error_code=error_code or self.DEFAULT_ERROR_CODE,
            details=safe_details,
        )


class DateParseError(DateError):
    """Raised when a date string cannot be parsed."""

    DEFAULT_ERROR_CODE = ErrorCode.DATE_PARSE_ERROR

    def __init__(
        self,
        date_str: str,
        message: str | None = None,
        format_hint: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.date_str = date_str
        self.format_hint = format_hint

        # Format the error message
        if message is None:
            message = f"Could not parse date: '{date_str}'"
            if format_hint:
                message += f"\nExpected format: {format_hint}"

        # Initialize details dictionary
        details: dict[str, Any] = {
            "date_string": date_str,
        }

        # Add format hint if provided
        if format_hint is not None:
            details["format_hint"] = format_hint

        # Add any additional details from kwargs (except 'details')
        for key, value in kwargs.items():
            if key != "details":
                details[key] = value

        super().__init__(
            message=message,
            error_code=self.DEFAULT_ERROR_CODE,
            details=details,
        )


class DateRangeError(DateError):
    """Raised when there's an error with a date range.

    Attributes:
        start_date: The start date of the invalid range
        end_date: The end date of the invalid range
    """

    DEFAULT_ERROR_CODE = ErrorCode.DATE_RANGE_ERROR

    def __init__(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        message: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date

        # Generate default message if not provided
        if message is None:
            if start_date and end_date:
                message = f"Invalid date range: {start_date} to {end_date}"
            else:
                message = "Invalid date range"

        # Initialize details dictionary
        details: dict[str, Any] = {}

        # Add start and end dates to details if provided using space format
        if start_date is not None:
            details["start_date"] = start_date.strftime("%Y-%m-%d %H:%M:%S%z")
        if end_date is not None:
            details["end_date"] = end_date.strftime("%Y-%m-%d %H:%M:%S%z")

        # Get any existing details from kwargs
        if "details" in kwargs and isinstance(kwargs["details"], dict):
            details.update(kwargs["details"])
            del kwargs["details"]

        # Extract error_code if provided
        error_code = kwargs.pop("error_code", self.DEFAULT_ERROR_CODE)

        # Add any additional kwargs to details (excluding special parameters)
        for key, value in kwargs.items():
            details[key] = value

        # Call the parent class (DateError) with the correct parameters
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
        )

    @classmethod
    def from_dates(
        cls,
        start_date: datetime,
        end_date: datetime,
        reason: str | None = None,
        **kwargs: object,
    ) -> "DateRangeError":
        """Create a DateRangeError from datetime objects with an optional reason."""
        message = f"Invalid date range: {start_date} to {end_date}"
        if reason:
            message += f" ({reason})"

        return cls(start_date=start_date, end_date=end_date, message=message, **kwargs)
