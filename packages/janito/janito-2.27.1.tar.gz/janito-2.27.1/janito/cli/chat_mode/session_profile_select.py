import os
from pathlib import Path
import questionary
from questionary import Style
import os
from pathlib import Path
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import HTML
from .prompt_style import chat_shell_style


"""
Profile selection logic for Janito Chat CLI using questionary.
"""


def _handle_raw_model_session_no_tools():
    return {
        "profile": "model_conversation_without_tools_or_context",
        "profile_system_prompt": None,
        "no_tools_mode": True,
    }  # Raw Model Session (no tools, no context)


def _handle_using_role():
    role_name = questionary.text("Enter the role name:").ask()
    return f"role:{role_name}"


def _get_toolbar(mode):
    if mode["multiline"]:
        return HTML(
            "<b>Multiline mode (Esc+Enter to submit). Type /single to switch.</b>"
        )
    else:
        return HTML(
            "<b>Single-line mode (Enter to submit). Type /multi for multiline.</b>"
        )


def _handle_custom_system_prompt():
    print(
        "\n[Custom System Prompt]\nPlease enter the message that will be used as the model system prompt. This will define how the AI behaves for this session.\nYou can use /multi for multiline mode, and /single to return to single-line mode.\n"
    )
    mode = {"multiline": False}
    bindings = KeyBindings()

    @bindings.add("c-r")
    def _(event):
        pass

    @bindings.add("f12")
    def _(event):
        buf = event.app.current_buffer
        buf.text = "Do It"
        buf.validate_and_handle()

    session = PromptSession(
        multiline=False,
        key_bindings=bindings,
        editing_mode=EditingMode.EMACS,
        bottom_toolbar=lambda: _get_toolbar(mode),
        style=chat_shell_style,
    )
    prompt_icon = HTML("<inputline>📝 </inputline>")
    while True:
        try:
            response = session.prompt(prompt_icon)
        except KeyboardInterrupt:
            print("[Custom System Prompt] Exited by the user.")
            import sys

            sys.exit(0)
        if not mode["multiline"] and response.strip() == "/multi":
            mode["multiline"] = True
            session.multiline = True
            continue
        elif mode["multiline"] and response.strip() == "/single":
            mode["multiline"] = False
            session.multiline = False
            continue
        else:
            sanitized = response.strip()
            try:
                sanitized.encode("utf-8")
            except UnicodeEncodeError:
                sanitized = sanitized.encode("utf-8", errors="replace").decode("utf-8")
            return {"profile": None, "profile_system_prompt": sanitized}


def _load_user_profiles():
    user_profiles_dir = Path.home() / ".janito" / "profiles"
    profiles = {}
    if user_profiles_dir.exists() and user_profiles_dir.is_dir():
        for profile_file in user_profiles_dir.glob("*"):
            if profile_file.is_file():
                try:
                    with open(profile_file, "r", encoding="utf-8") as f:
                        profiles[profile_file.stem] = f.read().strip()
                except Exception:
                    # Ignore unreadable files
                    pass
    return profiles


def select_profile():
    user_profiles = _load_user_profiles()
    choices = [
        "Developer with Python Tools",
        "Developer",
        "Market Analyst",
        "Custom system prompt...",
        "Raw Model Session (no tools, no context)",
    ]
    # Add user profiles to choices
    if user_profiles:
        choices.extend(user_profiles.keys())

    custom_style = Style(
        [
            ("highlighted", "bg:#00aaff #ffffff"),  # background for item under cursor
            ("question", "fg:#00aaff bold"),
        ]
    )
    answer = questionary.select(
        "Select a profile to use:", choices=choices, default=None, style=custom_style
    ).ask()

    if not answer:
        import sys

        sys.exit(0)

    if answer == "Raw Model Session (no tools, no context)":
        return _handle_raw_model_session_no_tools()
    elif answer == "Custom system prompt...":
        return _handle_custom_system_prompt()
    elif answer in user_profiles:
        # Return the content of the user profile as a custom system prompt
        return {"profile": None, "profile_system_prompt": user_profiles[answer]}
    elif answer == "Developer":
        # Return the content of the built-in Developer profile prompt
        from pathlib import Path
        from jinja2 import Template
        from janito.agent.setup_agent import _prepare_template_context

        # Get the absolute path relative to the current script location
        current_dir = Path(__file__).parent
        template_path = current_dir / "../../agent/templates/profiles/system_prompt_template_developer.txt.j2"
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        context = _prepare_template_context("developer", "Developer", None)
        prompt = template.render(**context)
        return {"profile": "Developer", "profile_system_prompt": prompt}
    elif answer == "Market Analyst":
        # Return the content of the built-in Market Analyst profile prompt
        from pathlib import Path
        from jinja2 import Template
        from janito.agent.setup_agent import _prepare_template_context

        # Get the absolute path relative to the current script location
        current_dir = Path(__file__).parent
        template_path = current_dir / "../../agent/templates/profiles/system_prompt_template_market_analyst.txt.j2"
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        context = _prepare_template_context("market_analyst", "Market Analyst", None)
        prompt = template.render(**context)
        return {"profile": "Market Analyst", "profile_system_prompt": prompt}
    return answer
