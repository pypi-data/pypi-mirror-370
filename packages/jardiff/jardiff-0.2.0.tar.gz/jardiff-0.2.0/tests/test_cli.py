"""Basic tests for the jardiff CLI.

These tests verify that the command-line interface can be invoked via
``python -m jardiff`` and via the console script entry point, and that
the help and version outputs are produced without error.  They do not
attempt to exercise the diff logic itself, which would require
constructing sample JAR directories.
"""

from __future__ import annotations

import subprocess
import sys


def test_help_and_version(tmp_path) -> None:
    """Ensure the CLI responds to --help and --version."""
    # Use python -m jardiff to ensure module discovery works
    result_help = subprocess.run(
        [sys.executable, "-m", "jardiff", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result_help.returncode == 0
    out_lower = result_help.stdout.lower()
    assert "usage" in out_lower
    assert "examples" in out_lower

    result_version = subprocess.run(
        [sys.executable, "-m", "jardiff", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result_version.returncode == 0
    # Should contain 'jardiff' and a version number
    assert "jardiff" in result_version.stdout.lower()
    assert any(char.isdigit() for char in result_version.stdout)
