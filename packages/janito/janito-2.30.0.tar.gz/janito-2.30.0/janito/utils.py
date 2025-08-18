import inspect


def kwargs_from_locals(*names):
    """
    Return a dict of {name: value} for each name from the caller's local scope.
    Usage:
        event = GenerationStarted(**kwargs_from_locals('driver_name', 'request_id', 'conversation_history'))
    """
    frame = inspect.currentframe().f_back
    return {name: frame.f_locals[name] for name in names}
