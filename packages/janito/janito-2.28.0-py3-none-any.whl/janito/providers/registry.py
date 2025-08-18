from typing import Type, Dict
from janito.llm.provider import LLMProvider


class LLMProviderRegistry:
    """
    Registry for LLM provider classes.
    """

    _providers: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type[LLMProvider]):
        if name in cls._providers:
            raise ValueError(f"Provider '{name}' is already registered.")
        cls._providers[name] = provider_cls

    @classmethod
    def get(cls, name: str) -> Type[LLMProvider]:
        if name not in cls._providers:
            return None
        return cls._providers[name]

    @classmethod
    def list_providers(cls):
        return list(cls._providers.keys())
