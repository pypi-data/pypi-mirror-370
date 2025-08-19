"""Date parsing and validation utilities for GitAnalyzer.

This module provides a compatibility layer for the new DateParser utility.
New code should import directly from ``beaconled.utils.date_utils`` instead.
"""

from datetime import datetime

from beaconled.utils.date_utils import DateUtils


class GitDateParser:
    """Legacy date parser for Git operations.

    This class is maintained for backward compatibility. New code should use
    the DateParser class from beaconled.utils.date_utils instead.
    """

    # Maintain the same patterns for compatibility
    RELATIVE_DATE_PATTERN = DateUtils.RELATIVE_DATE_PATTERN
    # These patterns don't exist on DateUtils, so we'll remove them for now

    @classmethod
    def parse_date(cls, date_str: str) -> datetime:
        """Parse a date string into a timezone-aware datetime in UTC.

        This is a compatibility wrapper around DateParser.parse_date().

        Args:
            date_str: The date string to parse.

        Returns:
            A timezone-aware datetime in UTC.

        Raises:
            DateParseError: If the date string cannot be parsed.
        """
        return DateUtils.parse_date(date_str)

    @classmethod
    def parse_git_date(cls, date_str: str) -> datetime:
        """Parse a git date string into a UTC datetime.

        This is a compatibility wrapper around DateParser.parse_git_date().

        Args:
            date_str: Date string from git log.

        Returns:
            A timezone-aware datetime in UTC.

        Raises:
            DateParseError: If the date string cannot be parsed.
        """
        return DateUtils.parse_git_date(date_str)

    @classmethod
    def validate_date_range(
        cls,
        start_date: datetime | str | None = None,
        end_date: datetime | str | None = None,
    ) -> tuple[datetime, datetime]:
        """Validate and normalize a date range, returning UTC datetimes.

        This is a compatibility wrapper around DateParser.validate_date_range().

        Args:
            start_date: Start date as string or datetime.
            end_date: End date as string or datetime.

        Returns:
            (start_date, end_date) as UTC datetimes.

        Raises:
            ValueError: If the range is invalid.
        """
        return DateUtils.validate_date_range(start_date, end_date)

    @classmethod
    def _parse_relative_date(cls, date_str: str) -> datetime:
        """Parse a relative date string (e.g., '1d', '2w', '3m', '1y').

        This is a compatibility wrapper around DateParser._parse_relative_date().
        """
        return DateUtils._parse_relative_date(date_str)

    @classmethod
    def _parse_iso_date(cls, date_str: str) -> datetime:
        """Parse an ISO date string (YYYY-MM-DD).

        This is a compatibility wrapper around DateParser._parse_iso_date().
        """
        return DateUtils._parse_iso_date(date_str)

    @classmethod
    def _parse_iso_datetime(cls, datetime_str: str) -> datetime:
        """Parse an ISO datetime string (YYYY-MM-DD HH:MM).

        This is a compatibility wrapper around DateParser._parse_iso_datetime().
        """
        return DateUtils._parse_iso_datetime(datetime_str)

    @classmethod
    def is_valid_commit_hash(cls, commit_hash: str) -> bool:
        """Validate a git commit hash or reference.

        This is a compatibility wrapper around DateParser.is_valid_commit_hash().

        Args:
            commit_hash: The commit hash or reference to validate.

        Returns:
            bool: True if the commit hash is valid, False otherwise.
        """
        return DateUtils.is_valid_commit_hash(commit_hash)
