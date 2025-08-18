from prompt_toolkit.styles import Style

chat_shell_style = Style.from_dict(
    {
        "prompt": "bg:#2323af #ffffff bold",
        "": "bg:#005fdd #ffffff",  # blue background for input area
        "bottom-toolbar": "fg:#2323af bg:yellow",
        "key-label": "bg:#ff9500 fg:#232323 bold",
        "provider": "fg:#117fbf",
        "model": "fg:#1f5fa9",
        "role": "fg:#e87c32 bold",
        "msg_count": "fg:#5454dd",
        "session_id": "fg:#704ab9",
        "tokens_total": "fg:#a022c7",
        "tokens_in": "fg:#00af5f",
        "tokens_out": "fg:#01814a",
        "max-tokens": "fg:#888888",
        "key-toggle-on": "bg:#ffd700 fg:#232323 bold",
        "key-toggle-off": "bg:#444444 fg:#ffffff bold",
        "cmd-label": "bg:#ff9500 fg:#232323 bold",
    }
)
