#!/usr/bin/env python
"""Command-line interface for Beacon."""

import argparse
import sys

from .core.analyzer import GitAnalyzer
from .formatters.extended import ExtendedFormatter
from .formatters.json_format import JSONFormatter
from .formatters.standard import StandardFormatter

# Domain-specific date errors for clearer CLI messages
from .core.date_errors import DateParseError, DateRangeError


def main() -> None:
    """Main CLI entry point for Beacon - Your delivery compass for empowered product builders.

    Beacon provides comprehensive git repository analysis with support for single commit
    and date range analysis with flexible date formatting options.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Beacon - Your delivery compass for empowered product builders\n\n"
            "IMPORTANT: All dates and times are interpreted as UTC. Please convert local times to UTC.\n\n"
            "Examples:\n"
            "  # Analyze the latest commit\n"
            "  beaconled\n\n"
            "  # Analyze a specific commit\n"
            "  beaconled abc1234\n\n"
            "  # Analyze changes in the last week (UTC)\n"
            '  beaconled --since "1w"\n\n'
            "  # Analyze changes between specific dates (UTC)\n"
            '  beaconled --since "2025-01-01" --until "2025-01-31 23:59:59"\n\n'
            "  # Analyze changes with explicit UTC times\n"
            '  beaconled --since "2025-01-01 00:00:00" --until "2025-01-31 23:59:59"\n\n'
            "  # Output in JSON format\n"
            "  beaconled --format json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="beaconled 0.2.0",
        help="Show program's version number and exit",
    )
    parser.add_argument(
        "commit",
        nargs="?",
        default="HEAD",
        help="Commit hash to analyze (default: HEAD)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["standard", "extended", "json"],
        default="standard",
        help="Output format (default: standard)",
    )
    parser.add_argument(
        "--since",
        default=None,
        help=(
            "Start date for range analysis (interpreted as UTC).\n"
            "\n"
            "Relative formats (relative to current UTC time):\n"
            "  1d    - 1 day ago\n"
            "  2w    - 2 weeks ago\n"
            "  3m    - 3 months ago\n"
            "  1y    - 1 year ago\n"
            "\n"
            "Absolute formats (interpreted as UTC):\n"
            "  YYYY-MM-DD                  - Date only (midnight UTC)\n"
            "  YYYY-MM-DD HH:MM            - Date and time\n"
            "  YYYY-MM-DDTHH:MM:SS        - ISO 8601 format\n"
            "  YYYY-MM-DDTHH:MM:SS+00:00  - Explicit UTC timezone\n"
            "\n"
            "Note: All times must be in UTC. Convert local times to UTC before use.\n"
        ),
    )
    parser.add_argument(
        "--until",
        default=None,
        help=(
            "End date for range analysis (interpreted as UTC).\n"
            "\n"
            "Uses same formats as --since, plus:\n"
            "  now   - Current UTC time\n"
            "\n"
            "Note: All times must be in UTC. Convert local times to UTC before use.\n"
            "Default: now (current UTC time)"
        ),
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory)",
    )

    args = parser.parse_args()

    # If --since is not provided, but --until is, that's an error
    if not args.since and args.until:
        parser.error("--until cannot be used without --since")

    try:
        analyzer = GitAnalyzer(args.repo)
        output: str

        # If --since is provided, perform a range analysis
        if args.since:
            since = args.since
            until = args.until or "now"  # Default to "now" if not provided

            range_stats = analyzer.get_range_analytics(since, until)
            if args.format == "json":
                json_formatter = JSONFormatter()
                output = json_formatter.format_range_stats(range_stats)
            elif args.format == "extended":
                extended_formatter = ExtendedFormatter()
                output = extended_formatter.format_range_stats(range_stats)
            else:  # standard
                standard_formatter = StandardFormatter()
                output = standard_formatter.format_range_stats(range_stats)
        else:
            # For single commit analysis
            commit_stats = analyzer.get_commit_stats(args.commit)

            if args.format == "json":
                json_formatter = JSONFormatter()
                output = json_formatter.format_commit_stats(commit_stats)
            elif args.format == "extended":
                extended_formatter = ExtendedFormatter()
                output = extended_formatter.format_commit_stats(commit_stats)
            else:  # standard
                standard_formatter = StandardFormatter()
                output = standard_formatter.format_commit_stats(commit_stats)

        # Handle output with proper encoding
        try:
            print(output)
        except UnicodeEncodeError:
            # Fallback for systems with limited encoding support
            # Replace problematic characters with ASCII alternatives
            safe_output = output.encode("ascii", "replace").decode("ascii")
            print(safe_output)

    except DateParseError as e:
        # Preserve domain-specific parse error messaging expected by tests
        error_msg = str(e)
        if "timezone" in error_msg.lower():
            error_msg += (
                "\nNote: All dates must be in UTC. Please convert local times to UTC before use."
            )
        try:
            print(f"Error: {error_msg}", file=sys.stderr)
        except UnicodeEncodeError:
            safe_error = error_msg.encode("ascii", "replace").decode("ascii")
            print(f"Error: {safe_error}", file=sys.stderr)
        sys.exit(2)
    except DateRangeError as e:
        # Preserve date range validation messaging (tests assert substrings)
        error_msg = str(e)
        if "timezone" in error_msg.lower() or "range" in error_msg.lower():
            error_msg += "\nNote: All date ranges must be specified in UTC. "
            error_msg += "Please ensure both start and end times are in UTC."
        try:
            print(f"Error: {error_msg}", file=sys.stderr)
        except UnicodeEncodeError:
            safe_error = error_msg.encode("ascii", "replace").decode("ascii")
            print(f"Error: {safe_error}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        # Ensure error messages are also handled properly
        try:
            print(f"Error: {e}", file=sys.stderr)
        except UnicodeEncodeError:
            safe_error = str(e).encode("ascii", "replace").decode("ascii")
            print(f"Error: {safe_error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
