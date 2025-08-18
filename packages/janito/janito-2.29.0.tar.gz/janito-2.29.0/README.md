# Janito, control you context

[![PyPI version](https://badge.fury.io/py/janito.svg)](https://badge.fury.io/py/janito)

Janito is a command-line interface (CLI) tool for managing and interacting with Large Language Model (LLM) providers. It enables you to configure API keys, select providers and models, and submit prompts to various LLMs from your terminal. Janito is designed for extensibility, supporting multiple providers and a wide range of tools for automation and productivity.

## Features

- 🔑 Manage API keys and provider configurations
- 🤖 Interact with multiple LLM providers (OpenAI, Google Gemini, DeepSeek, and more)
- 🛠️ List and use a variety of registered tools
- 📝 Submit prompts and receive responses directly from the CLI
- 📋 List available models for each provider
- 🧩 Extensible architecture for adding new providers and tools
- 🎛️ Rich terminal output and event logging

### Advanced and Architectural Features

- ⚡ **Event-driven architecture**: Modular, decoupled system using a custom EventBus for extensibility and integration.
- 🧑‍💻 **Tool registry & dynamic tool execution**: Register new tools easily, execute them by name or call from automation pipelines.
- 🤖 **LLM Agent automation**: Supports agent-like workflows with the ability to chain tools or make decisions during LLM conversations.
- 🏗️ **Extensible provider management**: Add, configure, or switch between LLM providers and their models on the fly.
- 🧰 **Rich tool ecosystem**: Includes file operations, local/remote script and command execution, text processing, and internet access (fetching URLs), all reusable by LLM or user.
- 📝 **Comprehensive event & history reporting**: Detailed logs of prompts, events, tool usage, and responses for traceability and audit.
- 🖥️ **Enhanced terminal UI**: Colorful, informative real-time outputs and logs to improve productivity and insight during LLM usage.

## Installation

Janito is a Python package. Since this is a development version, you can install it directly from GitHub:

```bash
pip install git+git@github.com:ikignosis/janito.git
```

### First launch and quick setup

Janito integrates with external LLM providers (list below), and most of them require a subscription to get an API_KEY.

> [!NOTE]
> Today, on June the 26th 2025, Google has a free tier subscription for its Gemini-2.5-flash and Gemini-2.5-pro models. Despite the limitation of the models and of the rate limit of the free tier, they can be used for testing janito. The API_KEY for Gemini is available [here](https://aistudio.google.com/app/apikey).

> [!NOTE]
> [Here](https://github.com/cheahjs/free-llm-api-resources/blob/main/README.md) a list of various services that provide free access or credits towards API-based LLM usage. Note that not all of them are supported by Janito, yet.

For a quick usage you can:

1. once you get the API_KEY from your favourite LLM provider, setup the API_KEY in Janito

```bash
janito --set-api-key API_KEY -p PROVIDER
```

2. then run janito from command line with the specific LLM provider of your choice

```bash
janito -p PROVIDER "Hello, who are you? How can you help me in my tasks?"
```

3. or you can run janito in interactive mode without the trailing argument

```bash
janito -p PROVIDER
```

4. if you want to setup a specific provider for any further interactions you can use:

```bash
janito -set provider=PROVIDER
```

> [!WARNING]
> Currently the supported providers are: `openai`, `google`, `anthropic`, `azure_openai`. You can get more details with `janito --list-providers`.

5. for more advanced setup, continue reading.


## Usage

After installation, use the `janito` command in your terminal with the syntax: `janito [options] [prompt]`

Janito supports both general-purpose and specialized assistance through the use of **profiles**. Profiles allow you to select a specific system prompt template and behavior for the agent, enabling workflows tailored to different roles or tasks (e.g., developer, writer, data analyst), or to use Janito as a generic AI assistant.

### Profiles: General-Purpose and Specialized Assistance

- By default, Janito acts as a general-purpose assistant.
- You can select a specialized profile using the `--profile` option:
  ```bash
  janito --profile developer "Refactor this code for better readability."
  janito --profile writer "Draft a blog post about AI in healthcare."
  ```
- Profiles change the system prompt and agent behavior to suit the selected role or workflow.
- To see available profiles or customize them, refer to the documentation or the `agent/templates/profiles/` directory.

> **Tip:** Use `--profile` for targeted workflows, or omit it for a general-purpose assistant.

Janito has configuration options, like `--set api-key API_KEY` and `--set provider=PROVIDER`, that create durable configurations and single shoot options, like `-p PROVIDER` and `-m MODEL`, that are active for the single run of the command or session.

### Basic Commands

- **Set API Key for a Provider (requires -p PROVIDER)**
  ```bash
  janito --set-api-key API_KEY -p PROVIDER
  ```
  > **Note:** The `-p PROVIDER` argument is required when setting an API key. For example:
  > ```bash
  > janito --set-api-key sk-xxxxxxx -p openai
  > ```

- **Set the Provider (durable)**
  ```bash
  janito --set provider=provider_name
  ```

- **List Supported Providers**
  ```bash
  janito --list-providers
  ```

- **List Registered Tools**
  ```bash
  janito --list-tools
  ```

- **List Models for a Provider**
  ```bash
  janito -p PROVIDER --list-models
  ```

- **Submit a Prompt**
  ```bash
  janito "What is the capital of France?"
  ```

- **Start Interactive Chat Shell**
  ```bash
  janito
  ```

### Advanced Options

- **Enable Execution Tools (Code/Shell Execution)**
  
  By default, **all tool privileges (read, write, execute)** are disabled for safety. This means Janito starts with no permissions to run tools that read, write, or execute code/shell commands unless you explicitly enable them.

- To enable **read** tools (e.g., file reading, searching): add `-r` or `--read`
- To enable **write** tools (e.g., file editing): add `-w` or `--write`
- To enable **execution** tools (code/shell execution): add `-x` or `--exec`

You can combine these flags as needed. For example, to enable both read and write tools:

```bash
janito -r -w "Read and update this file: ..."
```

To enable all permissions (read, write, execute):

```bash
# Using individual flags
janito -r -w -x "Run this code: print('Hello, world!')"

# Using the convenient /rwx prefix (single-shot mode)
janito /rwx "Run this code: print('Hello, world!')"
```

#### One-Shot Mode
For quick tasks without entering interactive mode, provide your prompt directly:

```bash
# Basic one-shot
janito "What are the key classes in this project?"

# One-shot with all permissions enabled
janito /rwx "Create a Python script and run it"

# One-shot with specific permissions
janito -r -w "Read this file and create a summary"
```

> **Warning:** Enabling execution tools allows running arbitrary code or shell commands. Only use `--exec` if you trust your prompt and environment.

- **Set a System Prompt**
  ```bash
  janito -s path/to/system_prompt.txt "Your prompt here"
  ```

- **Select Model and Provider Temporarily**
  ```bash
  janito -p openai -m gpt-3.5-turbo "Your prompt here"
  janito -p google -m gemini-2.5-flash "Your prompt here"
  ```



- **Enable Event Logging**
  ```bash
  janito -e "Your prompt here"
  ```

## 🌟 CLI Options Reference

### Core CLI Options
| Option                  | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `--version`            | Show program version                                                        |
| `--list-tools`         | List all registered tools                                                   |
| `--list-providers`     | List all supported LLM providers                                            |
| `-l`, `--list-models`  | List models for current/selected provider                                   |
| `--set-api-key`        | Set API key for a provider. **Requires** `-p PROVIDER` to specify the provider. |
| `--set provider=name`  | Set the current LLM provider (e.g., `janito --set provider=openai`)         |
| `--set PROVIDER.model=MODEL` or `--set model=MODEL` | Set the default model for the current/selected provider, or globally. (e.g., `janito --set openai.model=gpt-3.5-turbo`) |
| `-s`, `--system`       | Set a system prompt (e.g., `janito -s path/to/system_prompt.txt "Your prompt here"`) |

| `-p`, `--provider`     | Select LLM provider (overrides config) (e.g., `janito -p openai "Your prompt here"`) |
| `-m`, `--model`        | Select model for the provider (e.g., `janito -m gpt-3.5-turbo "Your prompt here"`) |
| `-v`, `--verbose`      | Print extra information before answering                                    |
| `-R`, `--raw`          | Print raw JSON response from API                                            |
| `-e`, `--event-log`    | Log events to console as they occur                                         |
| `prompt`        | Prompt to submit for the non interactive mode (e.g. `janito "What is the capital of France?"`) |

### 🧩 Extended Chat Mode Commands
Once inside the interactive chat mode, you can use these slash commands:

#### 📲 Basic Interaction
| Command           | Description                                  |
|-------------------|----------------------------------------------|
| `/exit` or `exit` | Exit chat mode                               |
| `/help`           | Show available commands                      |
| `/multi`          | Activate multiline input mode                |
| `/clear`          | Clear the terminal screen                    |
| `/history`        | Show input history                           |
| `/view`           | Print current conversation history           |
| `/track`          | Show tool usage history                      |

#### 💬 Conversation Management
| Command             | Description                                  |
|---------------------|----------------------------------------------|
| `/restart`          | Start a new conversation (reset context)   |
| `/prompt`           | Show the current system prompt               |
| `/role <description>` | Change the system role                     |
| `/lang [code]`      | Change interface language (e.g., `/lang en`) |

#### 🛠️ Tool & Provider Interaction
| Command              | Description                                  |
|----------------------|----------------------------------------------|
| `/tools`             | List available tools                         |
| `/-status`           | Show status of server                       |
| `/-logs`             | Show last lines of logs                     |
| `/write [on\|off]`   | Enable or disable write tool permissions   |
| `/read [on\|off]`    | Enable or disable read tool permissions    |
| `/execute [on\|off]` | Enable or disable execute tool permissions |


#### 📊 Output Control
| Command             | Description                                  |
|---------------------|----------------------------------------------|
| `/verbose`          | Show current verbose mode status             |
| `/verbose [on\|off]` | Set verbose mode                             |

## Extending Janito

Janito is built to be extensible. You can add new LLM providers or tools by implementing new modules in the `janito/providers` or `janito/tools` directories, respectively. See the source code and developer documentation for more details.

## Supported Providers

- OpenAI
- OpenAI over Azure
- Google Gemini
- DeepSeek
- Anthropic

See [docs/supported-providers-models.md](docs/supported-providers-models.md) for more details.

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` (if available) or open an issue to get started.

---

## Developer Documentation

For developer-specific setup, versioning, and contribution guidelines, see [README-dev.md](./README-dev.md).

## License

This project is licensed under the terms of the MIT license.

For more information, see the documentation in the `docs/` directory or run `janito --help`.

---

# Support


## 📖 Detailed Documentation

Full and up-to-date documentation is available at: https://ikignosis.github.io/janito/

---


## FAQ: Setting API Keys

- [Multiple API_KEY setup](#faq-multiple-api-key)
- [Use a specific model](#faq-use-specific-model)
- [Fetch the available LLM providers](#faq-fetch-providers)
- [Fetch the available models](#faq-fetch-models)


<a id="faq-multiple-api-key"></a>
### Multiple API_KEY setup

To set an API key for a provider, you **must** specify both the API key and the provider name:

```bash
janito --set-api-key YOUR_API_KEY -p PROVIDER_NAME
```

You can have an API_KEY for each LLM provider 

```bash
janito --set-api-key API_KEY_1 -p PROVIDER_1
janito --set-api-key API_KEY_2 -p PROVIDER_2
```

Then you can easily use one provider or the other without changing the API_KEY

```bash
janito -p PROVIDER_1 "What provider do you use?"
janito -p PROVIDER_2 "What provider do you use?"
```

If you omit the `-p PROVIDER_NAME` argument, Janito will show an error and not set the key.

<a id="faq-use-specific-model"></a>
### Use a specific model

To use a specific model, you can use the `-m` option in the following way:

```bash
janito -m gpt-4.1-nano -p openai "What model do you use?"
```

Or you can use the durable `--set` option: 

```bash
janito --set provider=openai 
janito --set model=gpt-4.1-nano
janito "What model do you use?"
```

<a id="faq-fetch-providers"></a>
### Fetch the available LLM providers

You can list all the LLM providers available using:

```bash
janito --list-providers
```

<a id="faq-fetch-models"></a>
### Fetch the available models

Each LLM provider has its own models, the best way to check what are the available models is using the following commands:

```bash
janito -p openai --list-models
janito -p google --list-models
janito -p azure_openai --list-models
janito -p anthropic --list-models
janito -p deepseek --list-models
```


## Ask Me Anything

<div align="center">
  <a href="git@github.com:ikignosis/janito.git" title="Ask Me Anything">
    <img width="250" src="docs/imgs/ama.png" alt="Ask Me Anything">
  </a>
</div

When the FAQ are not enough, you can contact the contributors of the project by direct questions

<p align="center">
  <kbd><a href="../../issues/new?labels=question">Ask a question</a></kbd> <kbd><a href="../../issues?q=is%3Aissue+is%3Aclosed+label%3Aquestion">Read questions</a></kbd>
</p>

#### Guidelines

- :mag: Ensure your question hasn't already been answered.
- :memo: Use a succinct title and description.
- :bug: Bugs & feature requests should be opened on the relevant issue tracker.
- :signal_strength: Support questions are better asked on Stack Overflow.
- :blush: Be nice, civil and polite.
- :heart_eyes: If you include at least one emoji in your question, the feedback will probably come faster.
- [Read more AMAs](https://github.com/sindresorhus/amas)
- [What's an AMA?](https://en.wikipedia.org/wiki/R/IAmA)
