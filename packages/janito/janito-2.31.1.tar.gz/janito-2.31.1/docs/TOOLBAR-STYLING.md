# Styling the Prompt Toolkit Toolbar in Janito

This document describes how styles are defined and applied to key elements in the command-line interface (CLI) toolbar using [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/).

## How Toolbar Styling Works

- The toolbar lines (provider, model, role, key bindings, token usage, etc.) are generated in `janito/cli/chat_mode/toolbar.py`.
- The strings use special HTML-like tags (e.g., `<role>admin</role>`, `<key-label>F1</key-label>`) to mark segments for custom styling.
- `prompt_toolkit`'s `HTML` formatted text parser interprets tags that match style names defined in a dictionary in `janito/cli/chat_mode/prompt_style.py`.

## Defining Styles

All style rules are set in `janito/cli/chat_mode/prompt_style.py`, for example:

```python
chat_shell_style = Style.from_dict({
    'role': 'fg:#e87c32 bold',                # For <role>...</role>
    'provider': 'fg:#117fbf',                 # For <provider>...</provider>
    'key-label': 'bg:#ff9500 fg:#232323 bold',# For <key-label>...</key-label>
    ...
})
```

- The key in `Style.from_dict` must match the tag name used in toolbar line strings.
- Example: `<role>user</role>` will be rendered using the `'role'` style.

## Applying Styles in Toolbar Output

When building toolbar lines, use HTML-like tags named for your style, **not CSS style tags or attributes**:

**Correct:**
```python
f'Press <key-label>F1</key-label> for help | Role: <role>{role}</role>'
```

**Incorrect (won't work):**
```python
f'<style class="key-label">F1</style> | Role: <role>{role}</role>'
```

## Supported Tag Mapping

| Tag Used in Toolbar String       | Style Name in prompt_style.py         | Example Usage                  |
|----------------------------------|---------------------------------------|-------------------------------|
| `<role>...</role>`               | `'role'`                              | `<role>user</role>`           |
| `<provider>...</provider>`       | `'provider'`                          | `<provider>OpenAI</provider>`  |
| `<key-label>...</key-label>`     | `'key-label'`                         | `<key-label>F1</key-label>`    |
| `<msg_count>...</msg_count>`     | `'msg_count'`                         | `<msg_count>3</msg_count>`     |
| ...                              | ...                                   | ...                           |

## Adding or Changing a Style

1. **Define your style** in `prompt_style.py`, for example:
   ```python
   'custom': 'bg:#f7e01d fg:#222222'
   ```
2. **Mark up your toolbar string** with `<custom>...</custom>`.
3. **Result:** prompt_toolkit will apply your custom style to those segments.

## Example

If you want a new binding to stand out in blue:

```python
# In prompt_style.py:
'blue-label': 'bg:#2629d4 fg:#ffffff bold',

# In toolbar.py:
return f'... <blue-label>F5</blue-label>: Extra ...'
```

---

**Troubleshooting:**
- If your style is not applied, check that the tag name in your string exactly matches a key in the style `from_dict`.
- Do not use HTML `<span>`, `<style>`, or CSS classes; only tag names matching style dict keys work.

---

*See also: `prompt_toolkit.formatted_text.HTML` and [prompt_toolkit styling documentation](https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#styling-the-output)*
