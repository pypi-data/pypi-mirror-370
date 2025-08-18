"""Stub implementation of EventLogger for the CLI event logging system."""


class EventLogger:
    def __init__(self, debug=False):
        self.debug = debug

    def subscribe(self, event_name, callback):
        if self.debug:
            pass  # Add debug subscribe output if needed
        # No real subscription logic

    def submit(self, event_name, payload=None):
        if self.debug:
            pass  # Add debug submit output if needed
        # No real submission logic


def setup_event_logger(args):
    debug = getattr(args, "event_debug", False)
    event_logger = EventLogger(debug=debug)
    print("[EventLog] Event logger is now active (stub implementation)")
    return event_logger


def setup_event_logger_if_needed(args):
    if getattr(args, "event_log", False):
        print("[EventLog] Setting up event logger with system bus...")
        event_logger = setup_event_logger(args)
        from janito.event_bus import event_bus

        def event_logger_handler(event):
            from janito.cli.console import shared_console
            from rich.pretty import Pretty
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            shared_console.print(
                f"[EventLog] [dim]{timestamp}[/] [bold green]{event.__class__.__name__}[/] | [cyan]{getattr(event, 'category', '')}[/]"
            )
            shared_console.print(Pretty(event, expand_all=True))
            shared_console.file.flush()

        from janito.event_bus.event import Event

        event_bus.subscribe(Event, event_logger_handler)


def inject_debug_event_bus_if_needed(args):
    if getattr(args, "event_debug", False):
        from janito.event_bus import event_bus

        orig_publish = event_bus.publish

        def debug_publish(event):
            # You can enrich here if needed
            return orig_publish(event)

        event_bus.publish = debug_publish
