from dataclasses import dataclass, field
from typing import Optional
import threading
from janito.llm.driver_config import LLMDriverConfig
from janito.conversation_history import LLMConversationHistory


@dataclass
class DriverInput:
    config: LLMDriverConfig
    conversation_history: LLMConversationHistory
    cancel_event: Optional[threading.Event] = field(default=None)
