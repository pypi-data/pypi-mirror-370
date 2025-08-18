class ShellCmdHandler:
    help_text = ""

    def __init__(self, after_cmd_line=None, shell_state=None):
        self.after_cmd_line = after_cmd_line
        self.shell_state = shell_state

    def run(self):
        raise NotImplementedError("Subclasses must implement run()")
