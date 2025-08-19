from janito.cli.chat_mode.shell.commands.base import ShellCmdHandler
from janito.cli.console import shared_console
from janito.cli.config import config

from janito.cli.cli_commands.show_config import resolve_effective_model


class ModelShellHandler(ShellCmdHandler):
    help_text = "Change or show the current LLM model (usage: /model [MODEL_NAME])"

    def run(self):
        model_name = self.after_cmd_line.strip()
        if not model_name:
            # Show effective model
            provider = config.get("provider")
            effective_model = resolve_effective_model(provider) if provider else None
            if effective_model:
                shared_console.print(
                    f"[bold green]Current effective model:[/bold green] {effective_model}"
                )
            else:
                shared_console.print(
                    "[bold yellow]No model is currently set.[/bold yellow]"
                )
            return
        # Set new model (global override)
        config.runtime_set("model", model_name)
        # Update agent's model in shell_state if possible
        agent = getattr(self.shell_state, "agent", None)
        if agent is not None and hasattr(
            agent, "reset_driver_config_to_model_defaults"
        ):
            agent.reset_driver_config_to_model_defaults(model_name)
        shared_console.print(
            f"[bold green]Model and config reset to defaults for:[/bold green] {model_name}"
        )
