🚧 **DRAFT:** Preliminary Version 📝 - Work in Progress 🏗️ 🚧

⚠️ **IMPORTANT NOTICE**: Created with **[useReq](https://github.com/Ogekuri/useReq)** 🤖✨ ⚠️

# useReq/req (0.0.70)

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-GPL--3.0-491?style=flat-square" alt="License: GPL-3.0">
  <img src="https://img.shields.io/badge/platform-Linux-6A7EC2?style=flat-square&logo=terminal&logoColor=white" alt="Platforms">
  <img src="https://img.shields.io/badge/docs-live-b31b1b" alt="Docs">
<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</p>

<p align="center">
<strong>The <u>req</u> script provides CLI prompts for requirements-driven software development.</strong><br>
The defined prompts are exposed as <b>req.<name></b> commands within various CLIs and Agents.<br>
This allows them to be run both as a Python package (installed as <b>req</b>, <b>usereq</b>, or <b>use-req</b>) and directly using <b>uvx</b>.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> |
  <a href="#feature-highlights">Feature Highlights</a> |
  <a href="#prompts-and-agents">Prompts and Agents</a> |
  <a href="#default-workflow">Default Workflow</a> |
  <a href="#supported-clis-agents-and-extensions">Supported CLIs, Agents, and Extensions</a> |
  <a href="#known-issues">Known Issues</a> |
  <a href="#legacy-mode">Legacy Mode</a>
</p>


## Feature Highlights
- Drives development through requirement changes.
- Keeps development under control.
- Creates a common interface for different CLIs and Agents.
- Creates **Software Requirements Specification** [*SRS*] files for existing projects.
- Manages *SRS* files in different languages.
- Lightweight customization.


## Prompts and Agents
  | Prompt | Description |
  | --- | --- |
  | `analyze` | Produce an analysis report |
  | `change` | Update the requirements and implement the corresponding changes |
  | `check` | Run the requirements check |
  | `cover` | Implement changes to cover new requirements |
  | `create` | Write a *SRS* draft using the project's source code |
  | `fix` | Fix a defect without changing the requirements |
  | `implement` | Implement source code from scratch from requirements |
  | `new` | Implement a new requirement and the corresponding source code changes |
  | `recreate` | Reorganize, update, and renumber the *SRS* |
  | `refactor` | Perform optimizations without changing the requirements |
  | `references` | Write a `REFERENCES.md` using the project's source code |
  | `write` | Produce a *SRS* draft based on the User Request description |
  | `workflow` | Write a `WORKFLOW.md` using the project's source code |


## Default Workflow

Click to zoom flowchart image.

[![Flowchart](https://raw.githubusercontent.com/Ogekuri/useReq/refs/heads/master/images/flowchart-bw.svg)](https://raw.githubusercontent.com/Ogekuri/useReq/refs/heads/master/images/flowchart-bw.svg)


## Quick Start

### Prerequisites

- Use supported environments: `linux`
- Python 3.11+
- Install the `uv` tool from: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)


### Run useReq/req with uvx
```bash
uvx --from git+https://github.com/Ogekuri/useReq.git req \
  --base myproject/ \
  --docs-dir myproject/docs/ \
  --guidelines-dir myproject/guidelines_docs/ \
  --tests-dir myproject/tests/ \
  --src-dir myproject/src/ \
  --enable-codex \
  --verbose --debug
```

### Install/Uninstall useReq/req with uv

#### Install
```bash
uv tool install usereq --force --from git+https://github.com/Ogekuri/useReq.git
```

#### Uninstall
```bash
uv tool uninstall usereq
```

### Usage
- Run `req` to create/re-create useReq resources in your project repository (depending on enabled providers and artifact types). This can include: `.codex`, `.claude`, `.github`, `.gemini`, `.kiro`, `.opencode`, `.req`, and `.vscode`.
  - You can run `req` from any directory:
    - Use `--base <project-folder>` to target a specific project.
    - Use `--here` to target the current directory and load paths from `.req/config.json` (requires `.req/config.json`).
    - If you run it from inside the project directory, you can omit both and it will use the current working directory as the project base (but you must still provide `--guidelines-dir`, `--docs-dir`, `--tests-dir`, and `--src-dir` unless you use `--update`).
  - `--docs-dir` is the requirements documentation directory; if it is empty, `REQUIREMENTS.md` is generated from the packaged template.
  - `--guidelines-dir` must be an existing directory under the project base, and can include user's guidelines files.
  - `--src-dir` is repeatable and can be provided multiple times to include multiple source directories.
  - Select CLI to install with:
    * `--enable-claude`       Enable generation of Claude prompts and agents for this run.
    * `--enable-codex`        Enable generation of Codex prompts for this run.
    * `--enable-gemini`       Enable generation of Gemini prompts for this run.
    * `--enable-github`       Enable generation of GitHub prompts and agents for this run.
    * `--enable-kiro`         Enable generation of Kiro prompts and agents for this run.
    * `--enable-opencode`     Enable generation of OpenCode prompts and agents for this run.
- Artifact types:
  - Skills are generated by default (disable with `--disable-skills`).
  - Prompts/commands are generated only when `--enable-prompts` is set.
  - Agents are generated only when `--enable-agents` is set.
- You need to run `req` again if you add or remove requirement-related files in the documentation directory or any files in the `guidelines/` directory.
- Option `--prompts-use-agents` generates prompt files as **agent-only references** (adds an `agent:` front matter field) where supported (GitHub prompts, Claude commands, and OpenCode commands).
- Add `--verbose` and `--debug` to get detailed and diagnostic output.
- Add `--update` to update an existing installation.
  - Add `--preserve-models` to use and preserve `.req/models.json` during installation.
- Add `--legacy` to enable the *legacy mode* support (see below).
- Add `--enable-models` and `--enable-tools` to include `model:` and `tools:` fields when available from centralized models configuration.
- Add `--add-guidelines` to copy packaged guideline templates into `--guidelines-dir` without overwriting existing files.
- Add `--upgrade-guidelines` to copy packaged guideline templates into `--guidelines-dir` and overwrite existing files.
- Add `--ver` / `--version` to print the installed package version and exit.
- Add `--remove` to remove resources generated by useReq from the target project (requires `.req/config.json`; removes `.req/` and generated provider artifacts).
- Add `--upgrade` to self-upgrade useReq via `uv`.
- Add `--uninstall` to uninstall useReq via `uv`.

### Embedded Utility

- Count tokens and chars for the given files (standalone, no --base/--here required).
  `--files-tokens FILE [FILE ...]`

- Generate LLM reference markdown for the given files (standalone, no --base/--here required).
  `--files-references FILE [FILE ...]`

- Generate compressed output for the given files (standalone, no --base/--here required).                        
  `--files-compress FILE [FILE ...]`

- Find and extract specific constructs from the given files (standalone, no --base/--here required).
  `--files-find TAG PATTERN FILE [FILE ...]`

- Count tokens and chars for files directly under the configured docs directory (requires --base/--here).
  `--tokens`

- Generate LLM reference markdown for all source files in configured --src-dir directories (requires --base/--here).
  `--references`

- Generate compressed output for all source files in configured --src-dir directories (requires --base/--here).  
  `--compress`

- Find and extract specific constructs from all source files in configured --src-dir directories (requires --base/--here).
  `--find TAG PATTERN`


- Add `--enable-line-numbers` to include `<n>:` prefixes in `--files-compress`, `--compress`, `--files-find`, and `--find` output.

#### Suported <TAG> in `--find` commands

- **Python**: CLASS, FUNCTION, DECORATOR, IMPORT, VARIABLE
- **C**: STRUCT, UNION, ENUM, TYPEDEF, MACRO, FUNCTION, IMPORT, VARIABLE
- **C++**: CLASS, STRUCT, ENUM, NAMESPACE, FUNCTION, MACRO, IMPORT, TYPE_ALIAS
- **C#**: CLASS, INTERFACE, STRUCT, ENUM, NAMESPACE, FUNCTION, PROPERTY, IMPORT, DECORATOR, CONSTANT
- **Rust**: FUNCTION, STRUCT, ENUM, TRAIT, IMPL, MODULE, MACRO, CONSTANT, TYPE_ALIAS, IMPORT, DECORATOR
- **JavaScript**: CLASS, FUNCTION, COMPONENT, CONSTANT, IMPORT, MODULE
- **TypeScript**: INTERFACE, TYPE_ALIAS, ENUM, CLASS, FUNCTION, NAMESPACE, MODULE, IMPORT, DECORATOR
- **Java**: CLASS, INTERFACE, ENUM, FUNCTION, IMPORT, MODULE, DECORATOR, CONSTANT
- **Go**: FUNCTION, METHOD, STRUCT, INTERFACE, TYPE_ALIAS, CONSTANT, IMPORT, MODULE
- **Ruby**: CLASS, MODULE, FUNCTION, CONSTANT, IMPORT, DECORATOR
- **PHP**: CLASS, INTERFACE, TRAIT, FUNCTION, NAMESPACE, IMPORT, CONSTANT
- **Swift**: CLASS, STRUCT, ENUM, PROTOCOL, EXTENSION, FUNCTION, IMPORT, CONSTANT, VARIABLE
- **Kotlin**: CLASS, INTERFACE, ENUM, FUNCTION, CONSTANT, VARIABLE, MODULE, IMPORT, DECORATOR
- **Scala**: CLASS, TRAIT, MODULE, FUNCTION, CONSTANT, VARIABLE, TYPE_ALIAS, IMPORT
- **Lua**: FUNCTION, VARIABLE
- **Shell**: FUNCTION, VARIABLE, IMPORT
- **Perl**: FUNCTION, MODULE, IMPORT, CONSTANT
- **Haskell**: MODULE, TYPE_ALIAS, STRUCT, CLASS, FUNCTION, IMPORT
- **Zig**: FUNCTION, STRUCT, ENUM, UNION, CONSTANT, VARIABLE, IMPORT
- **Elixir**: MODULE, FUNCTION, PROTOCOL, IMPL, STRUCT, IMPORT

## Supported CLIs, Agents, and Extensions

### High-Level Assessment

- 🌟 **GitHub Copilot** 🌟 - Many models available
- 👍 **OpenCode** 👍 - Many models available. Does not support `tools:` on agents/prompts.
- ⚖️ **Claude Code** ⚖️ - Only supports Claude/Anthropic models.
- 🆗 **OpenAI Codex** 🆗 - Only supports OpenAI models. Does not support agents. Does not support `model:` and `tools:` on prompts.
- 👎 **Kiro CLI** 👎 - Only supports Claude/Anthropic models. Does not support `$ARGUMENTS` on prompts.
- ☢️ **Gemini Code Assist** ☢️ - Only supports Google models. Does not support agents or prompts in the VS Code extension. Does not support agents, `model:`, and `tools:`.


### useReq/req Support

- ✅ OpenAI Codex (set environment variable **CODEX_HOME** to project's home)
- ✅ Claude Code
- ✅ GitHub Copilot
- ✅ OpenCode
- ✔️ Gemini Code Assist
- ✔️ Kiro CLI

| ✅ supported | ✔️ partially supported | ❌ issues | ⛔ not supported |


### useReq/req Support Details

#### OpenAI Codex
- ✅ OpenAI Codex CLI Prompt [`/prompts:req.create italian`]
  * set environment variable **CODEX_HOME** to project's home before run codex CLI
- ✅ OpenAI Codex Extension for Visual Studio Code [`/prompts:req.create italian`]
  * set environment variable **CODEX_HOME** to project's home before run VS Code

#### Claude Code
- ✅ Claude Code CLI Prompt [`/req:create italian`]
- ✅ Claude Code CLI Agent [`@agent-req-create italian`]
- ✅ Claude Extension for Visual Studio Code [`@agent-req-create italian`] (does not **highlight** agent commands like the CLI)

#### GitHub Copilot
- ✅ GitHub Copilot CLI Prompt [`/agent ➡️ req-create ➡️ italian ↩️`]
  * Use `--legacy` to not add `model:` on agents.
  * Slash command not supported 
  * Defect #980 [Model from agent.md isn't recognized #980](https://github.com/github/copilot-cli/issues/980)
  * Feature #618 → [Feature Request: Support custom slash commands from .github/prompts directory #618](https://github.com/github/copilot-cli/issues/618)
- ✔️ GitHub Copilot Agent Chat in Visual Studio Code [`gui; select agent ➡️ req.create; italian ↩️`]
  * **Starts a new chat** for every prompt.

#### OpenCode
- ✅ OpenCode CLI Prompt [`/req.create italian`]
- ✔️ OpenCode CLI Agent [`<TAB> ➡️ Req.Create ➡️ italian ↩️`]
  * **Starts a new session** (`/new`) for every prompt.

#### Gemini Code Assist
- ✅ Gemini CLI [`/req:create italian`]
- ⛔ Gemini Code Assist Extension for Visual Studio Code [`???`]
  * Prompts/Agents not supported by the VS Code extension

#### Kiro
- ❌ Kiro CLI Prompt [`'@req.create italian'`] (does not work as expected)
  - Prompt parameters (`$ARGUMENTS`) are not evaluated by the Kiro CLI.
  - *no arguments supported for file-based prompts* → [Manage prompts](https://kiro.dev/docs/cli/chat/manage-prompts/)
  - Defect #4141 → [Saved prompt with arguments only works when entire message is quoted in CLI (Spec Kit + Kiro CLI 1.21.0) #4141](https://github.com/kirodotdev/Kiro/issues/4141)
- ✔️ Kiro CLI Agent [`/agent swap; select agent ➡️ req.create; italian ↩️`] (does not work as expected)
  * **Clears the context** (`/clear`) for every prompt.


## Known Issues

- **Grok Code Fast 1** does not respect the TODO list and does not wait for approval
  * Defect #3180 → [Bug: Grok Code Fast 1 not update to do list correctly #3180](https://github.com/Kilo-Org/kilocode/issues/3180)


## Enable model and tools on prompts/agents

The `--enable-tools` switch includes a `tools:` specification on prompts according to read/write needs.

The `--enable-models` switch includes a `model:` specification on prompts according to the tables below.

### Models Specs

  | Model | Context Length | Reasoning [1] |
  | --- | --- | --- |
  | Grok Code Fast 0 | 256K | |
  | Claude Haiku 4.5 | 200K | |
  | Claude Sonnet 4.5 | 1M | | [2]
  | Claude Opus 4.5 | 200K | *Yes* |
  | Gemini 3 Flash (Preview) | 1,05M | |
  | Gemini 3 Pro (Preview) | 1,05M | Yes |
  | GPT-4.1 | 1,05M | **No** |
  | GPT-5 mini | 400K | Yes |
  | GPT-5.1 | 400K | Yes |
  | GPT-5.1-Codex-Mini (Preview) |  400K | |
  | GPT-5.1-Codex | 400K | |
  | GPT-5.1-Codex-Max | 400K | |
  | GPT-5.2 | 400K | *Yes* | 
  | GPT-5.2-Codex | 400K | *Yes* | 

  [1] *Reasoning availability according to openrouter.ai*
  [2] *Claude Sonnet 4.5 supports a 1M token context window when using the context-1m-2025-08-07 beta header. Long context pricing applies to requests exceeding 200K tokens.*

### GitHub Copilot

#### Available Models and Costs

  | Model | Cost |
  | --- | --- |
  | Grok Code Fast 0 | **0x** |
  | Claude Haiku 4.5 | 0.33x |
  | Claude Sonnet 4.5 | 1x |
  | *Claude Opus 4.5* | *3x* |
  | Gemini 3 Flash (Preview) | 0.33x |
  | Gemini 3 Pro (Preview) | 1x |
  | GPT-5 mini | **0x** |
  | GPT-5.1 | 1x |
  | GPT-5.1-Codex-Mini (Preview) | 0.33x |
  | GPT-5.1-Codex | 1x |
  | GPT-5.1-Codex-Max | 1x |
  | GPT-5.2 | 1x |
  | GPT-5.2-Codex | 1x |

#### Configured Models

  | Prompt | Model |
  | --- | --- |
  | `analyze` | Gemini 3 Flash (Preview) (copilot) |
  | `change` | GPT-5.2-Codex (copilot) |
  | `check` | Gemini 3 Pro (Preview) (copilot) |
  | `cover` | GPT-5.1-Codex-Max  (copilot) |
  | `create` | Gemini 3 Pro (Preview) (copilot) |
  | `fix` | GPT-5.1-Codex-Max (copilot) |
  | `new` | GPT-5.2-Codex (copilot) |
  | `recreate` | Gemini 3 Pro (Preview) (copilot) |
  | `refactor` | GPT-5.2-Codex (copilot) |
  | `write` | Gemini 3 Pro (Preview) (copilot) |

### Claude Code

#### Available Models and Costs

  | Model | Cost |
  | --- | --- |
  | Claude Haiku 4.5 | **low** |
  | Claude Sonnet 4.5 | mid |
  | *Claude Opus 4.5* | *high* |

#### Long Context Pricing

When using Claude Sonnet 4 or Sonnet 4.5 with the 1M token context window enabled, requests that exceed 200K input tokens are automatically charged at premium long context rates. [3]

```bash
# Example of using a full model name with the [1m] suffix
/model anthropic.claude-sonnet-4-5-20250929-v1:0[1m]
```

[3] *The 1M token context window is currently in beta for organizations in usage tier 4 and organizations with custom rate limits. The 1M token context window is only available for Claude Sonnet 4 and Sonnet 4.5.*

#### Configured Models

  | Prompt | Model |
  | --- | --- |
  | `analyze` | claude-haiku-4-5 |
  | `change` | claude-sonnet-4-5 |
  | `check` | claude-sonnet-4-5 |
  | `cover` | claude-opus-4-5 |
  | `create` | claude-sonnet-4-5 |
  | `fix` | claude-opus-4-5 |
  | `new` | claude-sonnet-4-5 |
  | `recreate` | claude-sonnet-4-5 |
  | `refactor` | claude-opus-4-5 |
  | `write` | claude-sonnet-4-5 |

### Kiro CLI

#### Available Models and Costs

  | Model | Cost |
  | --- | --- |
  | Claude Sonnet 4.5 | 1.3x credit |
  | Claude Sonnet 4 | 1.3x credit |
  | Claude Haiku 4.5 | 0.4x credit |
  | Claude Opus 4.5 | 2.2x credit |


#### Configured Models

  | Prompt | Model |
  | --- | --- |
  | `analyze` | claude-haiku-4.5 |
  | `change` | claude-sonnet-4.5 |
  | `check` | claude-sonnet-4.5 |
  | `cover` | claude-opus-4.5 |
  | `create` | claude-sonnet-4.5 |
  | `fix` | claude-opus-4.5 |
  | `new` | claude-sonnet-4.5 |
  | `recreate` | claude-sonnet-4.5 |
  | `refactor` | claude-opus-4.5 |
  | `write` | claude-sonnet-4.5 |

### OpenCode CLI

Models depend on the user's provider; useReq config uses the GitHub provider.
OpenCode CLI does not support "tools:" on agents/prompts.

#### Available GitHub Models

- github-copilot/claude-haiku-4.5
- github-copilot/claude-opus-4.5
- github-copilot/claude-opus-41
- github-copilot/claude-sonnet-4
- github-copilot/claude-sonnet-4.5
- github-copilot/gemini-3-flash-preview
- github-copilot/gpt-5-mini
- github-copilot/gpt-5.1
- github-copilot/gpt-5.1-codex
- github-copilot/gpt-5.1-codex-max
- github-copilot/gpt-5.2
- github-copilot/gpt-5.2-codex

##### Not Working GitHub Models

- github-copilot/gemini-2.5-pro
- github-copilot/gemini-3-pro-preview
- github-copilot/gpt-5.1-codex-mini

##### Not Tested GitHub Models

- github-copilot/gpt-4.1
- github-copilot/gpt-4o
- github-copilot/gpt-5
- github-copilot/gpt-5-codex
- github-copilot/grok-code-fast-1
- github-copilot/oswe-vscode-prime

#### Configured Models

  | Prompt | Model |
  | --- | --- |
  | `analyze` | github-copilot/gemini-3-flash-preview |
  | `change` | github-copilot/gpt-5-mini |
  | `check` | github-copilot/gemini-3-flash-preview |
  | `cover` | github-copilot/gpt-5.1-codex-max |
  | `create` | github-copilot/gpt-5.1 |
  | `fix` | github-copilot/gpt-5.1-codex-max |
  | `new` | github-copilot/gpt-5-mini |
  | `recreate` | github-copilot/gpt-5.1 |
  | `refactor` | github-copilot/gpt-5.2-codex |
  | `write` | github-copilot/gpt-5.1 |


### Gemini CLI

Gemini CLI does not support "model:" or "tools:" on prompts.


### OpenAI Codex CLI

OpenAI Codex CLI does not support "model:" or "tools:" on prompts.


## Note on GIT usage

This section describes the Git behavior when executing the commands provided by the scripts.

- Required state before execution:
  - Execute commands from a working branch (not in detached HEAD).
  - Preferably, the working tree should be clean: avoid unintended changes in the repository before starting the scripts.
  - Save all files and verify that you are in the correct project directory.

- What the scripts do to the repository:
  - The scripts may modify, create, or remove files in the working tree (files on disk).
  - They do not modify Git history (HEAD), branches, or tags automatically.
  - The index (staging area) and history remain unchanged until the user manually performs staging/commit operations.

- How to commit (recommended practice):
  - Review changes generated by the scripts before including them in a commit.
  - Manually add files to commit using `git add <file...>`.
  - Execute the commit with a structured message, for example:
    `git commit -m "change(<COMPONENT>): <SHORT-DESCRIPTION> [<DATE>]"`.
  - Staging and commit operations are under the user's control; the scripts do not perform automatic commits or update Git references.

- Practical warnings:
  - Do not use destructive commands (e.g., `git reset --hard`, `git clean -fd`) to "clean" the repository without verifying the impact.
  - If you prefer to isolate changes, execute commands in a branch or a copy of the repository.

## Legacy Mode

The *Legacy Mode* can be enabled with `--legacy`.

### GitHub Copilot

In *Legacy Mode* the unsupported `model:` is not added to agents.
See: Defect #980 [Model from agent.md isn't recognized #980](https://github.com/github/copilot-cli/issues/980)
