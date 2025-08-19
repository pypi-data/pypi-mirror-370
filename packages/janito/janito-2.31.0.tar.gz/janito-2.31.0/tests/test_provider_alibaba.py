import pytest
from janito.providers.registry import LLMProviderRegistry


def test_alibaba_provider_registered():
    provider_cls = LLMProviderRegistry.get("alibaba")
    assert provider_cls is not None, "Alibaba provider should be registered."
    provider = provider_cls()
    assert provider.name == "alibaba"
    assert provider.driver_config.base_url.startswith(
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
