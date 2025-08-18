from typing import Type, Dict, Any
from janito.llm.driver_config import LLMDriverConfig


def build_llm_driver_config(
    config: Dict[str, Any], driver_class: Type
) -> LLMDriverConfig:
    """
    Build an LLMDriverConfig instance for the given driver class based on its declared driver_fields.
    Only fills fields missing from given config; does not overwrite fields already provided.
    Any config fields not in driver_fields or LLMDriverConfig fields go into .extra.
    """
    driver_fields = getattr(driver_class, "driver_fields", None)
    if driver_fields is None:
        driver_fields = set(LLMDriverConfig.__dataclass_fields__.keys()) - {
            "model",
            "extra",
        }
    base_info = {}
    extra = {}
    for k, v in (config or {}).items():
        if k in driver_fields and k in LLMDriverConfig.__dataclass_fields__:
            base_info[k] = v
        else:
            extra[k] = v
    # Only set missing fields, do NOT overwrite those from CLI/user
    for field in driver_fields:
        if field not in base_info and field in LLMDriverConfig.__dataclass_fields__:
            base_info[field] = (
                None  # Optional: replace None with provider/driver default if wanted
            )
    return LLMDriverConfig(
        model=config.get("model") or config.get("model_name"), extra=extra, **base_info
    )
