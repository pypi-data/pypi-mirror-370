# LLM Driver Required Config Pattern

Some LLM drivers (when implemented) may require additional configuration fields (beyond API key or model name) to operate correctly. The `required_config` class attribute is intended to enable each driver to declare these requirements explicitly, and for providers to validate config early. As of this writing, no LLM driver implementation is present in this directory; this document describes the intended pattern.

## How to Use

1. **Declare requirements in your driver:**
    
    ```python
    class AzureOpenAIModelDriver(OpenAIModelDriver):
        required_config = {"azure_endpoint"}  # The config dict must contain this key.
    ```

2. **Validation on driver instantiation:**
    
    Instantiation via `LLMProvider.get_driver_for_model` will check that all required fields are present in the passed config dict, and raise a `ValueError` if any are missing.

3. **Backwards compatible:**
   - If `required_config` is not present, no validation is performed.
   - Providers and code using drivers without required_config are unchanged.

## Example: Azure OpenAI

If a model spec for Azure OpenAI uses `AzureOpenAIModelDriver`, the following config is required:

```python
config = {
    "azure_endpoint": "https://example.openai.azure.com/"
}
```
Attempting to create the driver without this field will result in:

```
ValueError: Missing required config for AzureOpenAIModelDriver: azure_endpoint
```

## Extending to Other Drivers

Other drivers may declare their own required fields (e.g., project_id, base_url) by providing a `required_config` class attribute as a set or list of key names.

---

*This pattern promotes robust, explicitly validated configuration for LLM drivers.*
