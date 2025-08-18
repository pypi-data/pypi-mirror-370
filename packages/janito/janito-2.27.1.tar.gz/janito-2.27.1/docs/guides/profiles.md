# Using Profiles in Janito

Janito supports both general-purpose and specialized workflows through the use of **profiles**. Profiles allow you to tailor the assistant's behavior, system prompt, and capabilities for different roles or tasks, such as software development, writing, data analysis, or any custom workflow you define.

## What is a Profile?

A **profile** in Janito is a named configuration that determines the system prompt and context for the agent. By selecting a profile, you can:
- Switch between general-purpose and specialized assistance
- Load a role-specific system prompt template
- Enable context, tools, or behaviors suited to a particular workflow (e.g., "developer", "writer", "analyst")

## Why Use Profiles?

- **General-purpose assistant:** Omit the `--profile` option to use Janito as a flexible, all-purpose AI assistant.
- **Specialized workflows:** Use `--profile <name>` to activate a profile designed for a specific role or domain, improving relevance and productivity.
- **Custom roles:** Create your own profiles by adding prompt templates in the `janito/agent/templates/profiles/` directory.

## How to Use Profiles

### Selecting a Profile

You can select a profile at launch using the `--profile` option:

```sh
janito --profile developer "Refactor this code for better readability."
janito --profile writer "Draft a blog post about AI in healthcare."
```

If you omit `--profile`, Janito uses the default (general-purpose) behavior.

### Listing and Customizing Profiles

- To see available profiles, check the `janito/agent/templates/profiles/` directory or refer to the documentation.
- Each profile corresponds to a Jinja2 template file named `system_prompt_template_<profile>.txt.j2`.
- You can create new profiles by adding new template files in this directory.

### Interactive Profile Selection

In interactive chat mode, you can select or switch profiles using the `/profile` command:

```sh
/profile
```

This will show the current and available profiles, and may prompt you to select one interactively.

## Example: Creating a Custom Profile

1. Create a new file in `janito/agent/templates/profiles/` named `system_prompt_template_dataanalyst.txt.j2`:

```
You are a data analyst. Answer questions with a focus on data-driven reasoning and clear explanations.
```

2. Launch Janito with your new profile:

```sh
janito --profile dataanalyst "Analyze this sales dataset and summarize key trends."
```

## Profile Precedence and System Prompt

- If you specify both `--profile` and `--system`, the explicit system prompt may override the profile template.
- Profiles are the recommended way to manage reusable, role-specific system prompts.

## Best Practices

- Use profiles for repeatable workflows or when you want consistent behavior for a given role.
- Keep your profile templates concise and focused on the desired behavior or domain.
- Review and update your profiles as your needs evolve.

## Further Reading

- [Prompt Design Style: Condition Before Action](prompting/README.md)
- [Terminal Shell Guide](terminal-shell.md)
- [CLI Options Reference](../reference/cli-options.md)

---

_Profiles make Janito adaptable for both general and specialized tasks. Leverage them to get the most out of your AI assistant!_