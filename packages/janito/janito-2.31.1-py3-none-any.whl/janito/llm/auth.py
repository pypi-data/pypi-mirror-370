"""
LLMAuthManager: Handles authentication credentials for LLM providers, persisted in ~/.janito/auth.json or a custom path.
"""

import os
import json
from typing import Dict, Optional


class LLMAuthManager:
    """
    Manages authentication tokens, API keys, or credentials for LLM providers.
    Persists credentials in ~/.janito/auth.json or a custom path.
    """

    def __init__(self, auth_file: Optional[str] = None):
        if auth_file is not None:
            self._auth_file = os.path.expanduser(auth_file)
        else:
            self._auth_file = os.path.expanduser("~/.janito/auth.json")
        self._credentials: Dict[str, str] = {}
        self._load_credentials()

    def _load_credentials(self):
        if os.path.exists(self._auth_file):
            try:
                with open(self._auth_file, "r") as f:
                    self._credentials = json.load(f)
            except Exception:
                self._credentials = {}
        else:
            self._credentials = {}

    def _save_credentials(self):
        os.makedirs(os.path.dirname(self._auth_file), exist_ok=True)
        with open(self._auth_file, "w") as f:
            json.dump(self._credentials, f, indent=2)
            f.write("\n")

    def set_credentials(self, provider_name: str, credentials: str) -> None:
        """
        Store credentials for a given provider and persist to disk. Raises ValueError if provider is unknown.
        """
        from janito.providers.registry import LLMProviderRegistry

        if provider_name not in LLMProviderRegistry.list_providers():
            raise ValueError(f"Unknown provider: {provider_name}")
        self._credentials[provider_name] = credentials
        self._save_credentials()

    def get_credentials(self, provider_name: str) -> Optional[str]:
        """
        Retrieve credentials for a given provider.
        """
        return self._credentials.get(provider_name)

    def remove_credentials(self, provider_name: str) -> None:
        """
        Remove credentials for a given provider and update disk.
        """
        if provider_name in self._credentials:
            del self._credentials[provider_name]
            self._save_credentials()
