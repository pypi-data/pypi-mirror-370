from rich.console import Console
from pathlib import Path
import os


def handle_list_config(args=None):
    console = Console()
    home = Path.home()
    default_config = home / ".janito" / "config.json"
    custom_dir = home / ".janito" / "configs"
    console.print("[bold green]Janito configuration files:[/bold green]")
    if default_config.exists():
        console.print(f"[bold yellow]Default config:[/bold yellow] {default_config}")
    else:
        console.print(
            f"[bold yellow]Default config:[/bold yellow] {default_config} [red](not found)"
        )
    if custom_dir.exists() and custom_dir.is_dir():
        files = sorted(
            f for f in custom_dir.iterdir() if f.is_file() and f.suffix == ".json"
        )
        if files:
            console.print("[bold yellow]Custom configs:[/bold yellow]")
            for f in files:
                console.print(f"  - {f}")
        else:
            console.print("[bold yellow]Custom configs:[/bold yellow] (none found)")
    else:
        console.print(
            f"[bold yellow]Custom configs:[/bold yellow] {custom_dir} [red](directory not found)"
        )
