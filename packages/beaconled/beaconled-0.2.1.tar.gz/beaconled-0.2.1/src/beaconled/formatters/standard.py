"""Standard output formatter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from colorama import Fore, Style

from .base_formatter import BaseFormatter

if TYPE_CHECKING:
    # Only import for typing to avoid runtime import cycles
    from beaconled.core.models import CommitStats, RangeStats


class StandardFormatter(BaseFormatter):
    """Standard text formatter for Beacon delivery analytics output.

    Provides basic formatting of commit and range statistics with color coding.
    """

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as standard text."""
        net_change_str = self._format_net_change(
            stats.lines_added,
            stats.lines_deleted,
        )
        output = [
            f"{Fore.CYAN}Commit:{Style.RESET_ALL} {stats.hash[:8]}",
            f"{Fore.CYAN}Author:{Style.RESET_ALL} {stats.author}",
            f"{Fore.CYAN}Date:{Style.RESET_ALL} {self._format_date(stats.date)}",
            f"{Fore.CYAN}Message:{Style.RESET_ALL} {stats.message}",
            "",
            f"{Fore.YELLOW}Files changed:{Style.RESET_ALL} {stats.files_changed}",
            f"{Fore.GREEN}Lines added:{Style.RESET_ALL} {stats.lines_added}",
            f"{Fore.RED}Lines deleted:{Style.RESET_ALL} {stats.lines_deleted}",
            f"{Fore.YELLOW}Net change:{Style.RESET_ALL} {net_change_str}",
        ]

        if stats.files:
            output.extend(
                [
                    "",
                    f"{Fore.MAGENTA}File changes:{Style.RESET_ALL}",
                    *[self._format_file_stats(f) for f in stats.files],
                ],
            )

        return "\n".join(output)

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as standard text."""
        range_net_change = self._format_net_change(
            stats.total_lines_added,
            stats.total_lines_deleted,
        )
        output = [
            f"{Fore.CYAN}Range Analysis:{Style.RESET_ALL} "
            f"{self._format_date(stats.start_date).split()[0]} to "
            f"{self._format_date(stats.end_date).split()[0]}",
            "",
            f"{Fore.YELLOW}Total commits:{Style.RESET_ALL} {stats.total_commits}",
            (f"{Fore.YELLOW}Total files changed:{Style.RESET_ALL} {stats.total_files_changed}"),
            (f"{Fore.GREEN}Total lines added:{Style.RESET_ALL} {stats.total_lines_added}"),
            (f"{Fore.RED}Total lines deleted:{Style.RESET_ALL} {stats.total_lines_deleted}"),
            f"{Fore.YELLOW}Net change:{Style.RESET_ALL} {range_net_change}",
        ]

        if stats.authors:
            output.extend(
                [
                    "",
                    f"{Fore.MAGENTA}Contributors:{Style.RESET_ALL}",
                    *[
                        self._format_author_stats(a, c)
                        for a, c in sorted(
                            stats.authors.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                    ],
                ],
            )

        return "\n".join(output)
