from collections import defaultdict
from datetime import datetime
from bisect import insort
import itertools
import threading


class EventBus:
    """
    Generic event bus for publish/subscribe event-driven communication with handler priorities.
    Automatically injects a timestamp (event.timestamp) into each event when published.
    Handlers with lower priority numbers are called first (default priority=100).
    Thread-safe for concurrent subscribe, unsubscribe, and publish operations.
    """

    def __init__(self):
        # _subscribers[event_type] = list of (priority, seq, callback)
        self._subscribers = defaultdict(list)
        self._seq_counter = itertools.count()
        self._lock = threading.Lock()

    def subscribe(self, event_type, callback, priority=100):
        """Subscribe a callback to a specific event type with a given priority (lower is higher priority)."""
        with self._lock:
            seq = next(self._seq_counter)
            entry = (priority, seq, callback)
            callbacks = self._subscribers[event_type]
            # Prevent duplicate subscriptions of the same callback with the same priority
            if not any(
                cb == callback and prio == priority for prio, _, cb in callbacks
            ):
                insort(callbacks, entry)

    def unsubscribe(self, event_type, callback):
        """Unsubscribe a callback from a specific event type (all priorities)."""
        with self._lock:
            callbacks = self._subscribers[event_type]
            self._subscribers[event_type] = [
                entry for entry in callbacks if entry[2] != callback
            ]

    def publish(self, event):
        """
        Publish an event to all relevant subscribers in strict priority order.
        Thread-safe: handlers are called outside the lock to avoid deadlocks.
        """
        with self._lock:
            # Collect all matching handlers (priority, seq, callback) for this event
            matching_handlers = []
            for event_type, callbacks in self._subscribers.items():
                if isinstance(event, event_type):
                    matching_handlers.extend(callbacks)
            # Remove duplicates (same callback for same event)
            seen = set()
            unique_handlers = []
            for prio, seq, cb in matching_handlers:
                if cb not in seen:
                    unique_handlers.append((prio, seq, cb))
                    seen.add(cb)
            # Sort by priority, then sequence
            unique_handlers.sort()
        # Call handlers outside the lock to avoid deadlocks
        for priority, seq, callback in unique_handlers:
            callback(event)


# Singleton instance for global use
event_bus = EventBus()
