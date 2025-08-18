from janito.cli.console import shared_console
from janito.cli.chat_mode.shell.commands.base import ShellCmdHandler
from janito.platform_discovery import PlatformDiscovery
import subprocess
import sys


class BangShellHandler(ShellCmdHandler):
    help_text = "!<cmd>: Run a shell command in the underlying shell (PowerShell or Bash). Usage: !ls -al or !Get-Process. Use ! with no command to launch an interactive shell."

    def run(self):
        if not self.shell_state:
            shared_console.print("[red]Shell state unavailable.[/red]")
            return
        cmd = (self.after_cmd_line or "").strip()
        if not cmd:
            pd = PlatformDiscovery()
            if pd.is_windows():
                shared_console.print(
                    "[yellow]Launching interactive PowerShell. Type 'exit' to return.[/yellow]"
                )
                subprocess.run(["powershell.exe"], check=False)
            else:
                shared_console.print(
                    "[yellow]Launching interactive Bash shell. Type 'exit' to return.[/yellow]"
                )
                subprocess.run(["bash"], check=False)
            return
        pd = PlatformDiscovery()
        if pd.is_windows():
            shared_console.print(f"[cyan]Running in PowerShell:[/cyan] {cmd}")
            completed = subprocess.run(
                ["powershell.exe", "-Command", cmd], capture_output=True, text=True
            )
        else:
            shared_console.print(f"[cyan]Running in Bash:[/cyan] {cmd}")
            completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = completed.stdout
        error = completed.stderr
        if output:
            shared_console.print(output)
        if error:
            shared_console.print(f"[red]{error}[/red]")
