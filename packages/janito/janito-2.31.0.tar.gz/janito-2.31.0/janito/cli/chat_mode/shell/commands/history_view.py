from janito.cli.console import shared_console
from janito.cli.chat_mode.shell.commands.base import ShellCmdHandler
import json

TRIM_LENGTH = 200  # Max chars to show for args or outputs before trimming


def trim_value(val, trim_length=TRIM_LENGTH):
    s = (
        json.dumps(val, ensure_ascii=False)
        if isinstance(val, (dict, list))
        else str(val)
    )
    if len(s) > trim_length:
        return s[:trim_length] + "... [trimmed]"
    return s


class ViewShellHandler(ShellCmdHandler):
    help_text = "Print the current LLM conversation history"

    def run(self):
        if not hasattr(self.shell_state, "agent") or self.shell_state.agent is None:
            shared_console.print("[red]No agent found in shell state.[/red]")
            return
        conversation_history = self.shell_state.agent.conversation_history
        messages = conversation_history.get_history()
        if not messages:
            shared_console.print("[yellow]Conversation history is empty.[/yellow]")
            return
        for i, msg in enumerate(messages, 1):
            self._print_message(i, msg)

    def _print_message(self, i, msg):
        role = msg.get("role", "?")
        content = msg.get("content", "")
        metadata = msg.get("metadata")
        is_tool_result = (
            role == "function"
            and isinstance(metadata, dict)
            and metadata.get("is_tool_result")
        )
        is_tool_call = (
            role == "tool_call"
            or (
                isinstance(metadata, dict)
                and (
                    metadata.get("type") == "tool_call" or metadata.get("is_tool_call")
                )
            )
        ) and not is_tool_result
        if is_tool_call:
            self._print_tool_call(i, metadata, content)
        elif is_tool_result:
            self._print_tool_result(i, content)
        else:
            self._print_regular_message(i, role, content, metadata)

    def _print_tool_call(self, i, metadata, content):
        func_name = None
        args = None
        if isinstance(metadata, dict):
            tool_call = metadata.get("tool_call")
            if tool_call and isinstance(tool_call, dict):
                func_name = (
                    tool_call.get("function") or tool_call.get("name") or "<unknown>"
                )
                args = tool_call.get("arguments") or tool_call.get("args") or {}
            else:
                func_name = metadata.get("name") or "<unknown>"
                args = metadata.get("arguments") or metadata.get("args") or content
        else:
            func_name = "<unknown>"
            args = content
        trimmed_args = trim_value(args)
        shared_console.print(
            f"[bold]{i}. TOOL_CALL:[/bold] {func_name}({trimmed_args})"
        )

    def _print_tool_result(self, i, content):
        trimmed_output = trim_value(content)
        if "\n" in trimmed_output:
            shared_console.print(f"[bold]{i}. TOOL_RESULT:[/bold]")
            for line in trimmed_output.splitlines():
                shared_console.print(line)
        else:
            shared_console.print(f"[bold]{i}. TOOL_RESULT:[/bold] {trimmed_output}")

    def _print_regular_message(self, i, role, content, metadata):
        trimmed_content = trim_value(content)
        shared_console.print(f"[bold]{i}. {role}:[/bold] {trimmed_content}")
        if metadata:
            shared_console.print(f"   [cyan]metadata:[/cyan] {metadata}")
