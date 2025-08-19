#!/usr/bin/env python3
"""Test script to verify disabled tools functionality."""

import tempfile
import os
import subprocess
import sys
from pathlib import Path


import pytest


def test_disabled_tools_cli():
    """Test the --set disabled_tools=... CLI functionality."""
    print("Testing disabled tools CLI functionality...")

    # Test 1: Set disabled tools
    print("\n1. Testing --set disabled_tools=...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "janito",
            "--set",
            "disabled_tools=create_file,read_files",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Failed to set disabled tools: {result.stderr}"
    print("✓ Successfully set disabled tools")

    # Test 2: Show config to verify disabled tools and config file path
    print("\n2. Testing --show-config shows disabled tools and config file path")
    result = subprocess.run(
        [sys.executable, "-m", "janito", "--show-config"],
        capture_output=True,
        text=True,
    )

    assert (
        "Config file:" in result.stdout
    ), "Config file path not shown in config output"
    assert "Disabled tools:" in result.stdout, "Disabled tools not shown in config"
    assert (
        "create_file" in result.stdout and "read_files" in result.stdout
    ), "Expected disabled tools not found in config"
    print("✓ Disabled tools and config file path correctly shown in config")

    # Test 3: List tools should exclude disabled ones
    print("\n3. Testing --list-tools excludes disabled tools")
    result = subprocess.run(
        [sys.executable, "-m", "janito", "--list-tools"], capture_output=True, text=True
    )

    assert (
        "create_file" not in result.stdout and "read_files" not in result.stdout
    ), "Disabled tools still appear in --list-tools"
    print("✓ Disabled tools correctly excluded from --list-tools")

    # Test 4: Clear disabled tools
    print("\n4. Testing clearing disabled tools")
    result = subprocess.run(
        [sys.executable, "-m", "janito", "--set", "disabled_tools="],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Failed to clear disabled tools: {result.stderr}"
    print("✓ Successfully cleared disabled tools")

    # Test 5: Verify tools are available again
    print("\n5. Testing tools are available after clearing")
    result = subprocess.run(
        [sys.executable, "-m", "janito", "--list-tools"], capture_output=True, text=True
    )

    assert (
        "create_file" in result.stdout and "read_files" in result.stdout
    ), "Tools not restored after clearing disabled list"
    print("✓ Tools correctly restored after clearing disabled list")


if __name__ == "__main__":
    success = test_disabled_tools_cli()
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
