import subprocess
import sys
import re


def test_cli_list_providers_includes_alibaba():
    result = subprocess.run(
        [sys.executable, "-m", "janito.cli.main_cli", "--list-providers"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Should mention alibaba in the output
    assert re.search(r"alibaba", result.stdout, re.IGNORECASE)
