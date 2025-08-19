"""Beacon Delivery Compass - Analyze git repository statistics."""

from .core.analyzer import GitAnalyzer
from .core.date_errors import DateParseError, DateRangeError
from .core.models import CommitStats, RangeStats
from .exceptions import (
    BeaconError,
    CommitError,
    ConfigurationError,
    InvalidRepositoryError,
    RepositoryError,
    ValidationError,
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "BeaconError",
    "CommitError",
    "CommitStats",
    "ConfigurationError",
    "DateParseError",
    "DateRangeError",
    "GitAnalyzer",
    "InvalidRepositoryError",
    "RangeStats",
    "RepositoryError",
    "ValidationError",
]
