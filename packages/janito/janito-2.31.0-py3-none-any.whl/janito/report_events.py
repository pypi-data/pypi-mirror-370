import attr
from typing import Any, ClassVar, Optional, Dict
from enum import Enum
from janito.event_bus.event import Event


class ReportSubtype(Enum):
    ACTION_INFO = "action_info"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"
    STDOUT = "stdout"
    STDERR = "stderr"
    PROGRESS = "progress"


class ReportAction(Enum):
    READ = "READ"
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    EXECUTE = "EXECUTE"
    # Add more as needed


@attr.s(auto_attribs=True, kw_only=True)
class ReportEvent(Event):
    """
    Event for reporting status, errors, warnings, and output.
    Uses enums for subtype and action for type safety and clarity.
    """

    category: ClassVar[str] = "report"
    subtype: ReportSubtype
    message: str
    action: Optional[ReportAction] = None
    tool: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
