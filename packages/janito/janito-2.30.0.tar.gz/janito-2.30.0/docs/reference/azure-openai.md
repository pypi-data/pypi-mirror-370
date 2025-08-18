# Using Azure OpenAI with Janito

Janito supports models hosted on Azure OpenAI in addition to OpenAI-compatible endpoints.

## Configuration Steps

1. **Set your Azure OpenAI endpoint:**
   Set the `base_url` to your Azure OpenAI endpoint, for example:
   ```
   https://YOUR-RESOURCE-NAME.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT-NAME
   ```

2. **Set your Azure API key:**
   Use `--set-api-key` or add it to your config file:
   ```bash
   janito --set-api-key YOUR_AZURE_OPENAI_KEY
   ```

3. **(Optional) Set API version:**
   If you need a specific API version, set `azure_openai_api_version` (default: `2023-05-15`).
   ```bash
   janito --set azure_openai_api_version=2023-05-15
   ```

## Example Configuration

Here is an example of the relevant configuration keys:

```txt
api_key = "YOUR_AZURE_OPENAI_KEY"
base_url = "https://YOUR-RESOURCE-NAME.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT-NAME"
azure_openai_api_version = "2023-05-15"  # Optional
```

## Notes
- You can use either local or global config for these settings.
- For more information, see the main README and release notes.
