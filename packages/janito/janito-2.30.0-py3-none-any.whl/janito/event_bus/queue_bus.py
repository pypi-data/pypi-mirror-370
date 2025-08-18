import threading
import queue


class QueueEventBusSentinel:
    """
    Special event to signal the end of event publishing for QueueEventBus.
    """

    pass


class QueueEventBus:
    """
    Event bus using a single queue for event delivery, preserving event order.
    API-compatible with EventBus for publish/subscribe, but all events go into one queue.
    Thread-safe for concurrent publish operations.
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._lock = threading.Lock()

    def subscribe(self, event_type=None, event_queue=None, priority=100):
        """
        No-op for compatibility. Returns the single event queue.
        """
        return self._queue

    def unsubscribe(self, event_type=None, event_queue=None):
        """
        No-op for compatibility.
        """
        pass

    def publish(self, event):
        """
        Publish an event to the single queue.
        """
        with self._lock:
            self._queue.put(event)

    def get_queue(self):
        """
        Return the single event queue for consumers.
        """
        return self._queue

    def fetch_event(self, block=True, timeout=None):
        """
        Fetch the next event from the queue. Blocks by default.
        Returns None if a QueueEventBusSentinel is encountered.
        """
        event = self._queue.get(block=block, timeout=timeout)
        if isinstance(event, QueueEventBusSentinel):
            return None
        return event
