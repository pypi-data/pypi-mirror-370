from janito.config import config

CONFIG_OPTIONS = {
    "api_key": "API key for OpenAI-compatible service (required)",  # pragma: allowlist secret
    "trust": "Trust mode: suppress all console output (bool, default: False)",
    "model": "Model name to use (e.g., 'gpt-4.1', 'gpt-4o', 'gpt-4-turbo', 'o3-mini', 'o4-mini', 'gemini-2.5-flash')",
    "base_url": "API base URL (OpenAI-compatible endpoint)",
    "azure_deployment_name": "Azure OpenAI deployment name (for Azure endpoints)",
    "role": "Role description for the Agent Profile (e.g., 'software engineer')",
    "temperature": "Sampling temperature (float, e.g., 0.0 - 2.0)",
    "max_tokens": "Maximum tokens for model response (int)",
    "template": "Template context dictionary for Agent Profile prompt rendering (nested)",
    "profile": "Agent Profile name (only 'base' is supported)",
}
