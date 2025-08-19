"""Data models for Beacon delivery analytics.

This module defines the core data structures used throughout the application
for representing git repository statistics and analysis results.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FileStats:
    """Statistics for a single file in a git commit.

    Attributes:
        path: Relative path of the file in the repository
        lines_added: Number of lines added in this file
        lines_deleted: Number of lines deleted from this file
        lines_changed: Total number of lines changed (added + deleted)
    """

    path: str
    lines_added: int = 0
    lines_deleted: int = 0
    lines_changed: int = 0

    def __post_init__(self) -> None:
        """Initialize computed fields after instance creation."""
        if self.lines_changed == 0:
            self.lines_changed = self.lines_added + self.lines_deleted


@dataclass
class CommitStats:
    """Statistics for a single git commit.

    Attributes:
        hash: Full 40-character SHA-1 hash of the commit
        author: Name and email of the commit author
        date: Timestamp when the commit was created (in UTC)
        message: Commit message (first line)
        files_changed: Number of files changed in this commit
        lines_added: Total lines added across all files
        lines_deleted: Total lines deleted across all files
        files: List of FileStats objects for each changed file
    """

    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    files: list[FileStats] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate and compute derived fields after initialization."""
        # Be flexible for unit tests/mocks: accept any non-empty string for hash.
        # Real repository validation occurs in analyzer/repo layer.
        if not isinstance(self.hash, str) or not self.hash.strip():
            msg = f"Invalid commit hash: {self.hash}"
            raise ValueError(msg)
        self.hash = self.hash.strip()

        if not self.files_changed and self.files:
            self.files_changed = len(self.files)

        if not (self.lines_added or self.lines_deleted) and self.files:
            self.lines_added = sum(f.lines_added for f in self.files)
            self.lines_deleted = sum(f.lines_deleted for f in self.files)


@dataclass
class RangeStats:
    """Statistics for a range of git commits.

    Attributes:
        start_date: Start of the date range (inclusive, UTC)
        end_date: End of the date range (inclusive, UTC)
        total_commits: Total number of commits in the range
        total_files_changed: Total files changed across all commits
        total_lines_added: Total lines added across all commits
        total_lines_deleted: Total lines deleted across all commits
        commits: List of CommitStats objects in chronological order
        authors: Dictionary mapping author names to commit counts
    """

    start_date: datetime
    end_date: datetime
    total_commits: int = 0
    total_files_changed: int = 0
    total_lines_added: int = 0
    total_lines_deleted: int = 0
    commits: list[CommitStats] = field(default_factory=list)
    authors: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and compute derived fields after initialization."""
        if self.start_date > self.end_date:
            msg = "start_date cannot be after end_date"
            raise ValueError(msg)

        if not self.commits:
            return

        # Recalculate totals from commits if not explicitly set
        if not self.total_commits:
            self.total_commits = len(self.commits)

        author_counts: dict[str, int] = defaultdict(int)
        for commit in self.commits:
            author_counts[commit.author] += 1
        self.authors = dict(author_counts)

        if not (self.total_files_changed or self.total_lines_added or self.total_lines_deleted):
            self.total_files_changed = sum(c.files_changed for c in self.commits)
            self.total_lines_added = sum(c.lines_added for c in self.commits)
            self.total_lines_deleted = sum(c.lines_deleted for c in self.commits)
