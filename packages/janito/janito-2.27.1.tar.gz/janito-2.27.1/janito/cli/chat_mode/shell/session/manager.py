import os
import json
from datetime import datetime

# --- Session ID generation ---
_current_session_id = None


def generate_session_id():
    # Use seconds since start of year, encode as base36 for shortness
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    seconds = int((now - start_of_year).total_seconds())
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    n = seconds
    while n:
        n, r = divmod(n, 36)
        out = chars[r] + out
    return out or "0"


def reset_session_id():
    global _current_session_id
    _current_session_id = None


def get_session_id():
    global _current_session_id
    if _current_session_id is None:
        _current_session_id = generate_session_id()
    return _current_session_id


def set_role(role):
    """Set the current role."""
    # No longer needed: from janito.cli.runtime_config import RuntimeConfig
    rc = RuntimeConfig()
    rc.role = role
    rc.save()
