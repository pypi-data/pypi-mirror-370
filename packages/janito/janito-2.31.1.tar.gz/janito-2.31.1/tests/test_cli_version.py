import subprocess
import sys


def test_cli_version():
    # Try running the CLI with --version
    result = subprocess.run(
        [sys.executable, "-m", "janito.cli.main_cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Non-zero exit: {result.returncode}"
    assert (
        "Janito" in result.stdout or "Janito" in result.stderr
    ), "Version output missing 'Janito'"
