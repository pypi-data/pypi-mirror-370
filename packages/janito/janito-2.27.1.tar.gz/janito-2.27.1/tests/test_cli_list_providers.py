import subprocess
import sys
import re


def test_cli_list_providers_runs_and_prints_table():
    result = subprocess.run(
        [sys.executable, "-m", "janito.cli.main_cli", "--list-providers"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Should print a table header or at least some provider names
    assert (
        "Supported LLM Providers" in result.stdout
        or "Provider" in result.stdout
        or "openai" in result.stdout.lower()  # fallback: at least one known provider
    )
    # Should not error
    assert "error" not in result.stdout.lower()
    assert "traceback" not in result.stdout.lower()
    # Optionally, check for at least one provider row (e.g., openai, deepseek, azure)
    assert re.search(r"openai", result.stdout, re.IGNORECASE)
    assert re.search(r"deepseek", result.stdout, re.IGNORECASE)
    assert re.search(r"azure", result.stdout, re.IGNORECASE)
