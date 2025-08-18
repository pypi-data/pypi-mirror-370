"""
CLI Command: Validate and set the model provider selection
"""

from janito.cli.config import config

_provider_instance = None


def get_provider_instance():
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = setup_provider()
    return _provider_instance


def handle_model_selection(args):
    if getattr(args, "model", None):
        provider_instance = get_provider_instance()
        provider_name = getattr(provider_instance, "name", None)
        if not provider_name:
            print(
                "Error: Provider must be specified with --provider or set as default before selecting a model."
            )
            import sys

            sys.exit(1)
        if not validate_model_for_provider(provider_name, args.model):
            sys.exit(1)
        config.runtime_set("model", args.model)


def validate_model_for_provider(provider_name, model_name):
    try:
        provider_instance = get_provider_instance()
        info_dict = provider_instance.get_model_info()
        available_names = [
            m["name"] for m in info_dict.values() if isinstance(m, dict) and "name" in m
        ]
        if model_name in available_names:
            return True
        else:
            print(
                f"Error: Model '{model_name}' is not available for provider '{provider_name}'."
            )
            print(f"Available models: {', '.join(available_names)}")
            return False
    except Exception as e:
        print(f"Error validating model for provider '{provider_name}': {e}")
        return False
