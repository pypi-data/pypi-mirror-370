import json
from typing import List, Dict, Optional


class LLMConversationHistory:
    """
    Stores the conversation history between user and LLM (assistant/system).
    Each message is a dict with keys: 'role', 'content', and optional 'metadata'.
    """

    def __init__(self):
        self._history: List[Dict] = []

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        message = {"role": role, "content": content}
        if metadata:
            message["metadata"] = metadata
        self._history.append(message)

    def get_history(self) -> List[Dict]:
        return list(self._history)

    def clear(self):
        self._history.clear()

    def export_json(self) -> str:
        return json.dumps(self._history, indent=2)

    def import_json(self, json_str: str):
        self._history = json.loads(json_str)
