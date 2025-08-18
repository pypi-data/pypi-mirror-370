from abc import ABC, abstractmethod
import importlib
from janito.llm.driver import LLMDriver


class LLMProvider(ABC):
    def create_driver(self):
        """
        Returns a new instance of the configured driver for this provider.
        Subclasses must implement this method.
        """
        raise NotImplementedError(
            "LLMProvider subclasses must implement create_driver()."
        )

    """
    Abstract base class for Large Language Model (LLM) providers.

    Provider Usage and Driver Communication Flow:
      1. Provider class is selected (e.g., OpenAIProvider).
      2. An instance of the provider is created. This instance is bound to a specific configuration (LLMDriverConfig) containing model, credentials, etc.
      3. All drivers created by that provider instance are associated with the bound config.
      4. To communicate with an LLM, call create_driver() on the provider instance, which yields a driver configured for the attached config. Every driver created via this method inherits the provider's configuration.

    Key: You do not create/configure a driver directly—always go through the provider to ensure correct configuration binding to the provider instance.

    Subclasses must implement the core interface for interacting with LLM APIs and define `provider_name` as a class attribute.
    """

    name: str = None  # Must be set on subclasses
    DEFAULT_MODEL: str = None  # Should be set by subclasses

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if (
            not hasattr(cls, "name")
            or not isinstance(getattr(cls, "name"), str)
            or not cls.name
        ):
            raise TypeError(
                f"Class {cls.__name__} must define a class attribute 'name' (non-empty str)"
            )
        if (
            not hasattr(cls, "DEFAULT_MODEL")
            or getattr(cls, "DEFAULT_MODEL", None) is None
        ):
            raise TypeError(
                f"Class {cls.__name__} must define a class attribute 'DEFAULT_MODEL' (non-empty str)"
            )

    def fill_missing_device_info(self, config):
        """
        Fill missing LLMDriverConfig fields (max_tokens, temperature, etc) from MODEL_SPECS for the chosen model.
        Mutates the config in place.
        """
        if not hasattr(self, "MODEL_SPECS"):
            return
        model_name = getattr(config, "model", None) or getattr(
            self, "DEFAULT_MODEL", None
        )
        model_info = self.MODEL_SPECS.get(model_name)
        if not model_info:
            return
        # Handle common fields from model_info
        spec_dict = (
            model_info.to_dict() if hasattr(model_info, "to_dict") else dict(model_info)
        )
        if (
            hasattr(config, "max_tokens")
            and getattr(config, "max_tokens", None) is None
        ):
            val = spec_dict.get("max_tokens") or spec_dict.get("max_response")
            if val is not None:
                try:
                    config.max_tokens = int(val)
                except Exception:
                    pass
        if (
            hasattr(config, "temperature")
            and getattr(config, "temperature", None) is None
        ):
            val = spec_dict.get("temperature")
            if val is None:
                val = spec_dict.get("default_temp")
            if val is not None:
                try:
                    config.temperature = float(val)
                except Exception:
                    pass

    @property
    @abstractmethod
    def driver(self) -> LLMDriver:
        pass

    def is_model_available(self, model_name):
        """
        Returns True if the given model is available for this provider.
        Default implementation checks MODEL_SPECS; override for dynamic providers.
        """
        if not hasattr(self, "MODEL_SPECS"):
            return False
        return model_name in self.MODEL_SPECS

    def get_model_info(self, model_name=None):
        """
        Return the info dict for a given model (driver, params, etc). If model_name is None, return all model info dicts.
        MODEL_SPECS must be dict[str, LLMModelInfo].
        """
        if not hasattr(self, "MODEL_SPECS"):
            raise NotImplementedError(
                "This provider does not have a MODEL_SPECS attribute."
            )
        if model_name is None:
            return {
                name: model_info.to_dict()
                for name, model_info in self.MODEL_SPECS.items()
            }
        if model_name in self.MODEL_SPECS:
            return self.MODEL_SPECS[model_name].to_dict()
        return None

    def _validate_model_specs(self):
        if not hasattr(self, "MODEL_SPECS"):
            raise NotImplementedError(
                "This provider does not have a MODEL_SPECS attribute."
            )

    def _get_model_name_from_config(self, config):
        return (config or {}).get("model_name", getattr(self, "DEFAULT_MODEL", None))

    def _get_model_spec_entry(self, model_name):
        spec = self.MODEL_SPECS.get(model_name, None)
        if spec is None:
            raise ValueError(f"Model '{model_name}' not found in MODEL_SPECS.")
        return spec

    def _get_driver_name_from_spec(self, spec):
        driver_name = None
        if hasattr(spec, "driver") and spec.driver:
            driver_name = spec.driver
        elif hasattr(spec, "other") and isinstance(spec.other, dict):
            driver_name = spec.other.get("driver", None)
        return driver_name

    def _resolve_driver_class(self, driver_name):
        if not driver_name:
            raise NotImplementedError(
                "No driver class found or specified for this MODEL_SPECS entry."
            )
        module_root = "janito.drivers"
        probable_path = None
        mapping = {
            "OpenAIResponsesModelDriver": "openai_responses.driver",
            "OpenAIModelDriver": "openai.driver",
            "AzureOpenAIModelDriver": "azure_openai.driver",
            "GoogleGenaiModelDriver": "google_genai.driver",
        }
        if driver_name in mapping:
            probable_path = mapping[driver_name]
            module_path = f"{module_root}.{probable_path}"
            mod = importlib.import_module(module_path)
            return getattr(mod, driver_name)
        # Attempt dynamic fallback based on convention
        if driver_name.endswith("ModelDriver"):
            base = driver_name[: -len("ModelDriver")]
            mod_name = base.replace("_", "").lower()
            module_path = f"{module_root}.{mod_name}.driver"
            try:
                mod = importlib.import_module(module_path)
                return getattr(mod, driver_name)
            except Exception:
                pass
        raise NotImplementedError(
            "No driver class found for driver_name: {}".format(driver_name)
        )

    def _validate_required_config(self, driver_class, config, driver_name):
        required = getattr(driver_class, "required_config", None)
        if required:
            missing = [
                k
                for k in required
                if not config or k not in config or config.get(k) in (None, "")
            ]
            if missing:
                raise ValueError(
                    f"Missing required config for {driver_name}: {', '.join(missing)}"
                )

    def create_agent(self, tools_adapter=None, agent_name: str = None, **kwargs):
        from janito.llm.agent import LLMAgent

        # Dynamically create driver if supported, else fallback to existing.
        driver = self.driver
        return LLMAgent(self, tools_adapter, agent_name=agent_name, **kwargs)
