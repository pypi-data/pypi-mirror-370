"""Test utilities for the Beacon Delivery Compass test suite."""

import os
import subprocess
import sys


def get_beaconled_cmd() -> list[str]:
    """
    Get the appropriate beaconled command for testing.

    Returns:
        List of command parts to execute beaconled.
    """
    # Try to find the system-installed beaconled first
    if sys.platform == "win32":
        # On Windows, try the Scripts directory
        venv_path = os.path.join(os.getcwd(), ".venv", "Scripts", "beaconled.exe")
    else:
        # On Unix-like systems, try the bin directory
        venv_path = os.path.join(os.getcwd(), ".venv", "bin", "beaconled")

    # Check if the virtual environment binary exists
    if os.path.exists(venv_path):
        return [venv_path]

    # Fall back to system-installed beaconled
    return ["beaconled"]


def run_beaconled(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Run beaconled with the given arguments.

    Args:
        args: List of command line arguments to pass to beaconled
        **kwargs: Additional arguments to pass to subprocess.run()

    Returns:
        CompletedProcess object with the result of the command execution.
    """
    cmd = get_beaconled_cmd() + args
    return subprocess.run(cmd, **kwargs)
