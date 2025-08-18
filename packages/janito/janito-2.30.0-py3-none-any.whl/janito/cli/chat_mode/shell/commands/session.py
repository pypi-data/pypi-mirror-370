from janito.cli.console import shared_console

from janito.cli.chat_mode.shell.commands.base import ShellCmdHandler
from janito.cli.console import shared_console


class HistoryShellHandler(ShellCmdHandler):
    help_text = "Show input history for this session"

    def run(self):
        if self.shell_state and hasattr(self.shell_state, "mem_history"):
            input_history = list(self.shell_state.mem_history.get_strings())
        else:
            input_history = []
        args = self.after_cmd_line.strip().split()
        if not args:
            start = max(0, len(input_history) - 5)
            end = len(input_history)
        elif len(args) == 1:
            count = int(args[0])
            start = max(0, len(input_history) - count)
            end = len(input_history)
        elif len(args) >= 2:
            start = int(args[0])
            end = int(args[1]) + 1
        else:
            start = 0
            end = len(input_history)
        shared_console.print(
            f"[bold cyan]Showing input history {start} to {end - 1} (total {len(input_history)}):[/bold cyan]"
        )
        for idx, line in enumerate(input_history[start:end], start=start):
            shared_console.print(f"{idx}: {line}")
            if isinstance(line, dict):
                role = line.get("role", "unknown")
                content = line.get("content", "")
            else:
                role = "user"
                content = line
            shared_console.print(f"[bold]{idx} [{role}]:[/bold] {content}")
