"""Date and time utilities for the BeaconLED project."""

import re
from datetime import datetime, timedelta, timezone
from typing import TypeVar

from beaconled.core.date_errors import DateParseError
from beaconled.exceptions import ValidationError

# Type variable for datetime-like objects
DateTimeLike = TypeVar("DateTimeLike", datetime, str)


class DateUtils:
    """Utility class for date and time operations."""

    # Constants
    YEAR_MIN = 1970
    YEAR_MAX = 2100
    RELATIVE_DATE_PATTERN = re.compile(r"^\d+[dwmy]$")
    COMMIT_HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{7,40}$")

    @classmethod
    def parse_date(cls, date_str: str) -> datetime:
        """Parse a date string into a timezone-aware datetime in UTC."""
        if not date_str or not isinstance(date_str, str):
            raise DateParseError(
                str(date_str) if date_str is not None else "None",
                "Date string cannot be None or empty",
            )

        # Store original for case-sensitive patterns
        original_date_str = date_str.strip()
        date_str = date_str.strip().lower()

        # Handle special 'now' value
        if date_str == "now":
            return datetime.now(timezone.utc)

        # Handle relative dates (e.g., '1d', '2w', '3m', '1y')
        if cls.RELATIVE_DATE_PATTERN.match(date_str):
            return cls._parse_relative_date(date_str)

        # Handle ISO date (YYYY-MM-DD)
        if re.match(r"^\d{4}-\d{2}-\d{2}$", original_date_str):
            dt = cls._parse_iso_date(original_date_str)
            return dt.replace(tzinfo=timezone.utc)

        # Handle ISO datetime (YYYY-MM-DD HH:MM)
        if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", original_date_str):
            dt = cls._parse_iso_datetime(original_date_str)
            return dt.replace(tzinfo=timezone.utc)

        # Handle ISO datetime with T separator (YYYY-MM-DDTHH:MM:SS)
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", original_date_str):
            dt = cls._parse_iso_datetime_t(original_date_str)
            return dt.replace(tzinfo=timezone.utc)

        # Handle git date format (Unix timestamp with optional offset)
        if re.match(r"^\d+\s*[+-]?\d{4}$", original_date_str) or re.match(
            r"^\d+$",
            original_date_str,
        ):
            return cls._parse_git_date(original_date_str)

        raise DateParseError(
            date_str,
            "Unsupported date format. Expected formats: 'now', '1d'/'2w'/'3m'/'1y', \
            'YYYY-MM-DD', or 'YYYY-MM-DD HH:MM'",
        )

    @classmethod
    def _parse_git_date(cls, date_str: str) -> datetime:
        """Parse a git log date string into a timezone-aware datetime in UTC."""
        try:
            parts = date_str.strip().split()
            if len(parts) == 2:
                # <unix_timestamp> <+/-HHMM>
                ts, offset = parts
                dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
                sign = 1 if offset[0] == "+" else -1
                hours = int(offset[1:3])
                minutes = int(offset[3:5])
                delta = timedelta(hours=sign * hours, minutes=sign * minutes)
                dt = dt - delta
                return dt.replace(tzinfo=timezone.utc)
            elif len(parts) == 1:
                # <unix_timestamp> only, assume UTC
                ts = parts[0]
                return datetime.fromtimestamp(int(ts), tz=timezone.utc)
            else:
                msg = "Unexpected git date format"
                raise ValueError(msg)
        except Exception as e:
            raise DateParseError(date_str, f"Failed to parse git date: {e!s}") from e

    @classmethod
    def validate_date_range(
        cls,
        start_date: datetime | str | None = None,
        end_date: datetime | str | None = None,
    ) -> tuple[datetime, datetime]:
        """Validate and normalize a date range, returning UTC datetimes."""
        # Parse string dates
        if start_date is not None and isinstance(start_date, str):
            start_date = cls.parse_date(start_date)
        if end_date is not None and isinstance(end_date, str):
            if end_date.lower() in ["now", "today", ""]:
                end_date = datetime.now(timezone.utc)
            else:
                end_date = cls.parse_date(end_date)

        # Set defaults
        if start_date is None:
            start_date = datetime.min.replace(tzinfo=timezone.utc)
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        # Ensure timezone-aware and UTC
        if not start_date.tzinfo:
            start_date = start_date.replace(tzinfo=timezone.utc)
        else:
            start_date = start_date.astimezone(timezone.utc)

        if not end_date.tzinfo:
            end_date = end_date.replace(tzinfo=timezone.utc)
        else:
            end_date = end_date.astimezone(timezone.utc)

        # Validate range
        if end_date < start_date:
            msg = f"Invalid date range: end date ({end_date}) is before start date ({start_date})"
            raise ValueError(
                msg,
            )

        # Always normalize end_date to end of day after validation
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start_date, end_date

    @classmethod
    def _parse_relative_date(cls, date_str: str) -> datetime:
        """Parse a relative date string (e.g., '1d', '2w', '3m', '1y')."""
        try:
            num = int(date_str[:-1])
            if num <= 0:
                msg = "Relative date value must be positive"
                raise ValueError(msg)

            unit = date_str[-1].lower()
            now = datetime.now(timezone.utc)

            # Map units to timedelta
            unit_map = {
                "d": ("day", "days", timedelta(days=1)),
                "w": ("week", "weeks", timedelta(weeks=1)),
                "m": ("month", "months", timedelta(weeks=4)),  # Approximate
                "y": ("year", "years", timedelta(weeks=52)),  # Approximate
            }

            if unit not in unit_map:
                valid_units = ", ".join(f"'{u}'" for u in unit_map.keys())
                msg = f"Invalid time unit '{unit}'. Valid units are: {valid_units}"
                raise ValueError(msg)

            _, _, delta = unit_map[unit]
            return now - (delta * num)

        except (ValueError, IndexError) as e:
            raise DateParseError(
                date_str,
                f"Could not parse date: Invalid relative date format: {e!s}. "
                "Expected format: <number><unit> where <unit> is one of: "
                "d (days), w (weeks), m (months), y (years)",
            ) from e

    @classmethod
    def _parse_iso_date(cls, date_str: str) -> datetime:
        """Parse an ISO date string (YYYY-MM-DD) and ensure it's timezone-aware."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if not (cls.YEAR_MIN <= dt.year <= cls.YEAR_MAX):
                msg = (
                    f"Year {dt.year} is outside the supported range ({cls.YEAR_MIN}-{cls.YEAR_MAX})"
                )
                raise ValidationError(
                    msg,
                    field="date",
                    value=date_str,
                )
            # Set time to start of day
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            return dt
        except ValueError as e:
            raise DateParseError(
                date_str,
                f"Could not parse date: {e!s}. Expected format: YYYY-MM-DD",
            ) from e

    @classmethod
    def _parse_iso_datetime(cls, datetime_str: str) -> datetime:
        """Parse an ISO datetime string (YYYY-MM-DD HH:MM) and ensure it's timezone-aware."""
        try:
            # Parse the datetime string with timezone
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

            # Validate year range
            if dt.year < cls.YEAR_MIN or dt.year > cls.YEAR_MAX:
                msg = (
                    f"Year {dt.year} is outside the supported range ({cls.YEAR_MIN}-{cls.YEAR_MAX})"
                )
                raise ValidationError(
                    msg,
                    field="datetime",
                    value=datetime_str,
                )
            return dt

        except ValueError as e:
            raise DateParseError(
                datetime_str,
                f"Could not parse datetime: Invalid format. Expected YYYY-MM-DD HH:MM: {e!s}",
            ) from e

    @classmethod
    def _parse_iso_datetime_t(cls, datetime_str: str) -> datetime:
        """Parse an ISO datetime string with T separator (YYYY-MM-DDTHH:MM:SS)."""
        try:
            # Parse the datetime string with T separator and timezone
            dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)

            # Validate year range
            if dt.year < cls.YEAR_MIN or dt.year > cls.YEAR_MAX:
                msg = (
                    f"Year {dt.year} is outside the supported range ({cls.YEAR_MIN}-{cls.YEAR_MAX})"
                )
                raise ValidationError(
                    msg,
                    field="datetime",
                    value=datetime_str,
                )
            return dt

        except ValueError as e:
            raise DateParseError(
                datetime_str,
                f"Could not parse datetime: Invalid format. Expected YYYY-MM-DDTHH:MM:SS: {e!s}",
            ) from e

    @classmethod
    def is_valid_commit_hash(cls, commit_hash: str) -> bool:
        """Validate a git commit hash or reference.

        Args:
            commit_hash: The commit hash to validate.

        Returns:
            bool: True if the commit hash is valid, False otherwise.
        """
        # Validate input type and content
        if not isinstance(commit_hash, str) or not commit_hash.strip():
            return False

        # Get the pattern safely
        pattern = getattr(cls, "COMMIT_HASH_PATTERN", None)
        if not pattern:
            return False

        # Perform the match with error handling
        try:
            return bool(pattern.match(commit_hash.strip()))
        except Exception:
            return False

    @classmethod
    def parse_git_date(cls, date_str: str) -> datetime:
        """Public method to parse git date format.

        This is a public wrapper around _parse_git_date for backward compatibility.
        """
        return cls._parse_git_date(date_str)
