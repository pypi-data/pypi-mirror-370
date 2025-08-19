"""Base formatter with shared functionality for all formatters."""

from datetime import datetime

import colorama
from colorama import Fore, Style

from beaconled.core.models import CommitStats, FileStats, RangeStats

# Initialize colorama for cross-platform color support
colorama.init()


class BaseFormatter:
    """Base formatter providing common formatting functionality."""

    def _format_date(self, dt: datetime) -> str:
        """Format a datetime object consistently across formatters."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _format_file_stats(self, file_stat: FileStats) -> str:
        """Format a single file's statistics."""
        return (
            f"  {file_stat.path}: "
            f"{Fore.GREEN}+{file_stat.lines_added}{Style.RESET_ALL} "
            f"{Fore.RED}-{file_stat.lines_deleted}{Style.RESET_ALL}"
        )

    def _format_author_stats(self, author: str, count: int) -> str:
        """Format author statistics line."""
        return f"  {author}: {count} commit{'s' if count != 1 else ''}"

    def _format_net_change(self, added: int, deleted: int) -> str:
        """Format net change with appropriate color coding."""
        net_change = added - deleted
        net_color = Fore.GREEN if net_change >= 0 else Fore.RED
        return f"{net_color}{net_change}{Style.RESET_ALL}"

    def _get_file_type_breakdown(
        self,
        files: list[FileStats],
    ) -> dict[str, dict[str, int]]:
        """Group file statistics by file extension."""
        file_types: dict[str, dict[str, int]] = {}
        for file_stat in files:
            ext = file_stat.path.split(".")[-1] if "." in file_stat.path else "no-ext"
            if ext not in file_types:
                file_types[ext] = {"count": 0, "added": 0, "deleted": 0}
            file_types[ext]["count"] += 1
            file_types[ext]["added"] += file_stat.lines_added
            file_types[ext]["deleted"] += file_stat.lines_deleted
        return file_types

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics. Must be implemented by subclasses."""
        raise NotImplementedError

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics. Must be implemented by subclasses."""
        raise NotImplementedError
