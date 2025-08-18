import inspect
from .bus import event_bus


class EventHandlerBase:
    """
    Base class for event handler classes.
    Automatically subscribes methods named on_<EventClassName> to the event bus for the corresponding event type.
    Pass one or more event modules (e.g., janito.report_events, janito.driver_events) to the constructor.
    Raises an error if a handler method does not match any known event class.
    """

    def __init__(self, *event_modules):
        unknown_event_methods = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("on_"):
                event_class_name = name[3:]
                event_class = None
                for module in event_modules:
                    event_class = getattr(module, event_class_name, None)
                    if event_class:
                        break
                if event_class:
                    event_bus.subscribe(event_class, method)
                else:
                    unknown_event_methods.append(name)
        if unknown_event_methods:
            raise ValueError(
                f"Unknown event handler methods found: {unknown_event_methods}. "
                f"No matching event class found in provided event modules."
            )
