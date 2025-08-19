from janito.cli.config import config


def handle_verbose(shell_state=None, **kwargs):
    args = kwargs.get("args", [])
    verbose = config.get("verbose") or False
    if not args:
        status = "ON" if verbose else "OFF"
        console.print(
            f"[bold green]/verbose:[/bold green] Verbose mode is currently [bold]{status}[/bold]."
        )
        return
    arg = args[0].lower()
    if arg == "on":
        config.runtime_set("verbose", True)
        console.print(
            "[bold green]/verbose:[/bold green] Verbose mode is now [bold]ON[/bold]."
        )
    elif arg == "off":
        config.runtime_set("verbose", False)
        console.print(
            "[bold green]/verbose:[/bold green] Verbose mode is now [bold]OFF[/bold]."
        )
    else:
        console.print("[bold red]Usage:[/bold red] /verbose [on|off]")


handle_verbose.help_text = "Show or set verbose mode for this session"
