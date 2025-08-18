"""
Main entry point for the Janito Chat CLI.
Handles the interactive chat loop and session startup.
"""

from rich.console import Console
from prompt_toolkit.formatted_text import HTML
from janito.cli.chat_mode.session import ChatSession


def main(args=None):
    console = Console()
    console.clear()
    from janito.version import __version__

    session = ChatSession(console, args=args)
    session.run()


if __name__ == "__main__":
    main()
