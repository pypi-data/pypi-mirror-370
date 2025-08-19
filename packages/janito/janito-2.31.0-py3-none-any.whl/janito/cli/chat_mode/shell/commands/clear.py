from janito.cli.chat_mode.shell.commands.base import ShellCmdHandler
from janito.cli.console import shared_console


class ClearShellHandler(ShellCmdHandler):
    help_text = "Clear the terminal screen using Rich console."

    def run(self):
        shared_console.clear()
        # Optionally show a message after clearing
        # shared_console.print("[green]Screen cleared.[/green]")
        return None
