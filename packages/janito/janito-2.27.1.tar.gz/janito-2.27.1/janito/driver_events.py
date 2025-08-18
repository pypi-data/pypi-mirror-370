import attr
from typing import Any, ClassVar
from enum import Enum
from janito.event_bus.event import Event


class RequestStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
    EMPTY_RESPONSE = "empty_response"
    TIMEOUT = "timeout"


@attr.s(auto_attribs=True, kw_only=True)
class DriverEvent(Event):
    """
    Base class for events related to a driver (e.g., LLM, API provider).
    Includes driver name and request ID for correlation.
    """

    category: ClassVar[str] = "driver"
    driver_name: str = None
    request_id: str = None


@attr.s(auto_attribs=True, kw_only=True)
class GenerationStarted(DriverEvent):
    conversation_history: Any = None


@attr.s(auto_attribs=True, kw_only=True)
class GenerationFinished(DriverEvent):
    total_turns: int = 0


@attr.s(auto_attribs=True, kw_only=True)
class RequestStarted(DriverEvent):
    payload: Any = None


@attr.s(auto_attribs=True, kw_only=True)
class RequestFinished(DriverEvent):
    """
    Used for all request completions: success, error, cancellation, empty response, or timeout.
    status should be a RequestStatus value.
    - For errors, fill error/exception/traceback fields.
    - For cancellations, fill reason field.
    - For empty response, fill error/details fields as appropriate.
    - For timeout, fill error/details fields as appropriate.
    """

    response: Any = None
    status: RequestStatus = (
        None  # RequestStatus.SUCCESS, ERROR, CANCELLED, EMPTY_RESPONSE, TIMEOUT
    )
    usage: dict = None
    finish_type: str = None  # 'success', 'error', 'cancelled', etc. (legacy)
    error: str = None
    exception: Exception = None
    traceback: str = None
    reason: str = None  # for cancellations or empty/timeout reasons
    details: dict = None  # for additional info (empty response, timeout, etc.)


@attr.s(auto_attribs=True, kw_only=True)
class ContentPartFound(DriverEvent):
    content_part: Any = None


@attr.s(auto_attribs=True, kw_only=True)
class ToolCallStarted(DriverEvent):
    tool_call_id: str = None
    name: str = None
    arguments: Any = None

    @property
    def tool_name(self):
        return self.name


@attr.s(auto_attribs=True, kw_only=True)
class ToolCallFinished(DriverEvent):
    tool_call_id: str = None
    name: str = None
    result: Any = None

    @property
    def tool_name(self):
        return self.name


@attr.s(auto_attribs=True, kw_only=True)
@attr.s(auto_attribs=True, kw_only=True)
class RateLimitRetry(DriverEvent):
    """Emitted by a driver when it encounters a provider rate-limit (HTTP 429) and
    decides to retry the request after a delay. This allows UIs or logging layers
    to give feedback to the user while the driver automatically waits.
    """

    attempt: int = 0  # Retry attempt number (starting at 1)
    retry_delay: float = 0  # Delay in seconds before the next attempt
    error: str = None  # The original error message
    details: dict = None  # Additional details extracted from the provider response


@attr.s(auto_attribs=True, kw_only=True)
class ResponseReceived(DriverEvent):
    parts: list = None
    tool_results: list = None  # each as dict or custom ToolResult dataclass
    timestamp: float = None  # UNIX epoch seconds, normalized
    metadata: dict = None
