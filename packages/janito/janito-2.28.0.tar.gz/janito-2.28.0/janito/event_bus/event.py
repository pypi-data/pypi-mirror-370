import attr
from typing import ClassVar
from datetime import datetime, timezone


@attr.s(auto_attribs=True, kw_only=True)
class Event:
    """
    Base class for all events in the system.
    Represents a generic event with a category.
    Automatically sets a timestamp at creation.
    """

    category: ClassVar[str] = "generic"
    timestamp: datetime = attr.ib(factory=lambda: datetime.now(timezone.utc))
