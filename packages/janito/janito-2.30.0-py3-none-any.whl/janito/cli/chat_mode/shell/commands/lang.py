from janito.cli.config import config
import janito.i18n as i18n


from janito.cli.config import config
import janito.i18n as i18n
from janito.cli.console import shared_console
from janito.cli.chat_mode.shell.commands.base import ShellCmdHandler


class LangShellHandler(ShellCmdHandler):
    help_text = "Change the interface language (e.g., /lang en)"

    def run(self):
        lang_code = self.after_cmd_line.strip()
        if not lang_code:
            shared_console.print(
                "[bold yellow]Uso: /lang [código_idioma] (ex: pt, en, es)[/bold yellow]"
            )
            return
        config.runtime_set("lang", lang_code)
        i18n.set_locale(lang_code)
        shared_console.print(
            f"[bold green]Idioma alterado para:[/bold green] [cyan]{lang_code}[/cyan]"
        )
