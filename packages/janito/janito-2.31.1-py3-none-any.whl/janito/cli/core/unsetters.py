from janito.config import config as global_config


def handle_unset(args):
    unset_arg = getattr(args, "unset", None)
    if not unset_arg:
        return False
    key = unset_arg.strip().replace("-", "_")
    if "." in key:
        # Provider or model-specific keys
        parts = key.split(".")
        if len(parts) == 2:
            provider, subkey = parts
            current_val = (
                global_config.file_config.get("providers", {})
                .get(provider, {})
                .get(subkey)
            )
            if current_val is not None:
                del global_config.file_config["providers"][provider][subkey]
                global_config.save()
                print(f"{key}={current_val} was removed.")
                return True
        elif len(parts) == 3:
            provider, model, subkey = parts
            model_conf = (
                global_config.file_config.get("providers", {})
                .get(provider, {})
                .get("models", {})
                .get(model, {})
            )
            current_val = model_conf.get(subkey)
            if current_val is not None:
                del global_config.file_config["providers"][provider]["models"][model][
                    subkey
                ]
                global_config.save()
                print(f"{key}={current_val} was removed.")
                return True
    else:
        current_val = global_config.file_config.get(key)
        if current_val is not None:
            del global_config.file_config[key]
            global_config.save()
            print(f"{key}={current_val} was removed.")
            return True
    if "=" in unset_arg:
        provided_key = unset_arg.split("=")[0].strip()
        print(
            f"Error: --unset expected a key, not key=value. Did you mean: --unset {provided_key}?"
        )
    else:
        print(f"Error: no value set for {key} (cannot remove)")
    return True
