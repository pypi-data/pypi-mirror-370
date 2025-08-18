"""
Utility functions for janito CLI (shared).
"""


def format_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}m"
    elif n >= 1_000:
        return f"{n/1_000:.2f}k"
    else:
        return str(n)


def format_generation_time(generation_time_ms):
    minutes = int(generation_time_ms // 60000)
    seconds = int((generation_time_ms % 60000) // 1000)
    milliseconds = int(generation_time_ms % 1000)
    formatted_time = ""
    if minutes > 0:
        formatted_time += f"{minutes}m "
    if seconds > 0:
        formatted_time += f"{seconds}s "
    formatted_time += f"[{int(generation_time_ms)} ms]"
    return formatted_time
