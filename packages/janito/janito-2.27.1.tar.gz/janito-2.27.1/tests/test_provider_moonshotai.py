import pytest
from janito.providers.registry import LLMProviderRegistry


def test_moonshotai_provider_registered():
    provider_cls = LLMProviderRegistry.get("moonshotai")
    assert provider_cls is not None, "MoonshotAI provider should be registered."
    provider = provider_cls()
    assert provider.name == "moonshotai"
    assert provider.driver_config.base_url.startswith("https://api.moonshot.ai")
