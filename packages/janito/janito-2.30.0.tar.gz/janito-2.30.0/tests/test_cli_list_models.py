import subprocess
import sys
import pytest


def test_cli_list_models_requires_provider():
    result = subprocess.run(
        [sys.executable, "-m", "janito.cli.main_cli", "--list-models"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert (
        "No provider selected" in result.stdout
        or "No provider selected" in result.stderr
        or "Provider must be specified" in result.stdout
        or "Provider must be specified" in result.stderr
    )


@pytest.mark.parametrize("provider", ["openai", "google", "anthropic"])
def test_cli_list_models_for_provider(provider):
    result = subprocess.run(
        [sys.executable, "-m", "janito.cli.main_cli", "--list-models", "-p", provider],
        capture_output=True,
        text=True,
    )
    # Accept either pretty table or fallback list
    assert result.returncode == 0
    assert (
        f"Supported models for provider '{provider}'" in result.stdout
        or f"Supported models for provider '{provider}'" in result.stderr
        or "Model Name" in result.stdout
        or "Model Name" in result.stderr
        or "- " in result.stdout  # fallback list
    )
