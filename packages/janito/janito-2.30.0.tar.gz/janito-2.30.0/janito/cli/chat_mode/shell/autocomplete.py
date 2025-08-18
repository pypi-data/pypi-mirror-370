from prompt_toolkit.completion import Completer, Completion
from janito.cli.chat_mode.shell.commands import get_shell_command_names


class ShellCommandCompleter(Completer):
    """
    Provides autocomplete suggestions for shell commands starting with '/'.
    Uses the COMMAND_HANDLERS registry for available commands.
    """

    def __init__(self):
        # Only commands starting with '/'
        self.commands = get_shell_command_names()

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/"):
            prefix = text[1:]
            for cmd in self.commands:
                if cmd[1:].startswith(prefix):
                    yield Completion(cmd, start_position=-(len(prefix) + 1))
