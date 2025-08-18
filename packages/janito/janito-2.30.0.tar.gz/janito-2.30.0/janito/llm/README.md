# janito.llm Package

This directory contains generic, provider-agnostic classes and methods for working with Large Language Models (LLMs) in the `janito` framework. Its purpose is to provide base abstractions that can be extended by provider-specific implementations.

## Scope and Contents

- **driver.py**
  - Contains `LLMDriver`, an abstract base class defining the core methods for LLM drivers. Subclasses should implement provider/model-specific logic, while benefiting from consistent streaming and event interfaces.
- **provider.py**
  - Contains `LLMProvider`, an abstract base class for LLM API providers. This outlines the required interface for integrating new providers and retrieving model info or driver classes.

## Usage
- Extend these base classes when adding new drivers or providers.
- Do not include provider-specific logic here; only generic mechanisms, patterns, or utilities applicable to any LLM integration belong in this package.

## Example
```python
from janito.llm.driver import LLMDriver
from janito.llm.provider import LLMProvider
```

---
This README clarifies the intention of the `llm` package as the generic/static contract for LLM drivers and providers.