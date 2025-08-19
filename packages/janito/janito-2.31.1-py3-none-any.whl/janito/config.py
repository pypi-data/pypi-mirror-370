# Shared Janito ConfigManager singleton
from janito.config_manager import ConfigManager

# Only one global instance! Used by CLI, provider_config, others:
# If you want to use a custom config, re-initialize this singleton with config_name or config_path before use.
config = ConfigManager(config_path=None)
