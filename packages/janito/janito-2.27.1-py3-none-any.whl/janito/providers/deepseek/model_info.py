MODEL_SPECS = {
    "deepseek-chat": {
        "description": "DeepSeek Chat Model (OpenAI-compatible)",
        "context_window": 8192,
        "max_tokens": 4096,
        "family": "deepseek",
        "default": True,
    },
    "deepseek-reasoner": {
        "description": "DeepSeek Reasoner Model (OpenAI-compatible)",
        "context_window": 8192,
        "max_tokens": 4096,
        "family": "deepseek",
        "default": False,
    },
}
