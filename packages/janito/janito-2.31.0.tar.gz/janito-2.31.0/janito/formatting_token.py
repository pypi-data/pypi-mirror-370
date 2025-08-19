"""
Token summary formatter for rich and pt markup.
- Used to display token/message counters after completions.
"""

from janito.perf_singleton import performance_collector

from rich.rule import Rule


def format_tokens(n, tag=None, use_rich=False):
    if n is None:
        return "?"
    if n < 1000:
        val = str(n)
    elif n < 1000000:
        val = f"{n/1000:.1f}k"
    else:
        val = f"{n/1000000:.1f}M"
    if tag:
        if use_rich:
            return f"[{tag}]{val}[/{tag}]"
        else:
            return f"<{tag}>{val}</{tag}>"
    return val


def format_token_message_summary(
    msg_count, usage, width=96, use_rich=False, elapsed=None
):
    """
    Returns a string (rich or pt markup) summarizing message count, last token usage, elapsed time, and tokens per second.
    """
    left = f" Messages: {'[' if use_rich else '<'}msg_count{']' if use_rich else '>'}{msg_count}{'[/msg_count]' if use_rich else '</msg_count>'}"
    tokens_part = ""
    if usage:
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")
        tokens_part = (
            f" | Tokens - Prompt: {format_tokens(prompt_tokens, 'tokens_in', use_rich)}, "
            f"Completion: {format_tokens(completion_tokens, 'tokens_out', use_rich)}, "
            f"Total: {format_tokens(total_tokens, 'tokens_total', use_rich)}"
        )
    elapsed_part = ""
    tps_part = ""
    if elapsed is not None and elapsed > 0:
        elapsed_part = f" | Elapsed: [cyan]{elapsed:.2f}s[/cyan]"
        if usage and total_tokens:
            tokens_per_second = total_tokens / elapsed
            tps_part = f" | TPS: {int(tokens_per_second)}"
    return f"{left}{tokens_part}{elapsed_part}{tps_part}"


def print_token_message_summary(
    console, msg_count=None, usage=None, width=96, elapsed=None
):
    """Prints the summary using rich markup, using defaults from perf_singleton if not given. Optionally includes elapsed time."""
    if usage is None:
        usage = performance_collector.get_last_request_usage()
    if msg_count is None:
        msg_count = performance_collector.get_total_turns() or 0
    line = format_token_message_summary(
        msg_count, usage, width, use_rich=True, elapsed=elapsed
    )
    if line.strip():
        console.print(Rule(line))
