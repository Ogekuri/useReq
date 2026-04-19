<div align="center">
  <table width="100%">
    <tr>
      <td align="center" style="padding: 20px; border: 2px solid #d73a49; background-color: #ffeef0; border-radius: 8px;">
        <h2 style="color: #d73a49; margin-top: 0;">⚠️ PROJECT MOVED TO PI-CLI ⚠️</h2>
        <p style="font-size: 16px; color: #24292e;">
          This project is no longer maintained here. The SRS-driven development workflow has been migrated and is now available as a <strong>dedicated extension for the pi CLI</strong>.
        </p>
        <p style="font-size: 16px; color: #24292e;">
          This move provides <strong>greater control over prompts</strong> and integration with the full suite of <a href="https://shittycodingagent.ai/">pi.dev</a> tools.
        </p>
        <hr style="border: 0; border-top: 1px solid #d73a49; margin: 20px 0;">
        <h3 style="color: #d73a49;">How to Install</h3>
        <p style="font-size: 15px; color: #24292e;">
          You can install the extension via <strong>NPM</strong> by following the instructions here:
        </p>
        <a href="https://www.npmjs.com/package/pi-usereq" style="text-decoration: none;">
          <img src="https://img.shields.io/badge/NPM-pi--usereq-red?style=for-the-badge&logo=npm" alt="NPM Package" />
        </a>
        <p style="margin-top: 15px;">
          <a href="https://www.npmjs.com/package/pi-usereq" style="color: #0366d6; font-weight: bold; text-decoration: underline;">
            View Installation Guide on NPM
          </a>
        </p>
      </td>
    </tr>
  </table>
</div>


# useReq/req (0.65.0)

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-GPL--3.0-491?style=flat-square" alt="License: GPL-3.0">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-6A7EC2?style=flat-square&logo=terminal&logoColor=white" alt="Platforms">
  <img src="https://img.shields.io/badge/docs-live-b31b1b" alt="Docs">
<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</p>

<p align="center">
<strong>The <u>req</u> script provides CLI prompts for requirements-driven software development.</strong><br>
The defined prompts are exposed through provider-specific prompt, skill, and agent surfaces across supported CLIs and Agents (for example <b>/req-<name></b>, <b>/req:<name></b>, <b>/skill:req-<name></b>, or <b>/req-<name>.prompt</b>).<br>
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
<p align="center">
<br>
🚧 <strong>DRAFT</strong>: 👾 Alpha Development 👾 - Work in Progress 🏗️ 🚧<br>
⚠️ <strong>IMPORTANT NOTICE</strong>: Created itself with <a href="https://github.com/Ogekuri/useReq"><strong>useReq/req</strong></a> 🤖✨ ⚠️<br>
<br>
<p>

## Requirements

- Astral `uv` tool is required to run `scripts/req.sh` and project CLI workflows.
- `uv.lock` is the canonical dependency lockfile for this repository; do not maintain a root `requirements.txt` file.
- Primary validated environment: `linux` (automatic `--upgrade` and `--uninstall` execution is Linux-only).
- Python 3.11+


## Feature Highlights
- **Drives development through requirement changes**.
- Keeps development under control.
- Usable as skills, or agents, or prompts.
- Creates a common interface for different vendor CLIs and Agents.
- Creates **Software Requirements Specification** [*SRS*] file, optimized for LLM Agents, for new or existing projects.
- Keeps source code documentation updated and optimized for LLM Agents reasoning.
- Engineered for uninterrupted linear progression.
- Use **git worktree** to parallelize tasks (only on clean git repositories)
- Provide **source-code analysis tool**, that supports different programming languages: Python, C, C++, C#, Rust, JavaScript, TypeScript, Java, Go, Ruby, PHP, Swift, Kotlin, Scala, Lua, Shell, Perl, Haskell, Zig, Elixir.
- Support **static-code analysis** with Pylance, Ruff or customizable Command-Line commands.
- Support customizable guidelines.
- Supports [Conventional Commit Standards](https://www.conventionalcommits.org/en/v1.0.0/) and is compatible with [release-changelog-builder-action](https://github.com/mikepenz/release-changelog-builder-action).
- Compatible with [G/Git-Alias CLI](https://github.com/Ogekuri/G).
- You will no longer need to read the codebase.


## Prompts and Agents
  | Prompt | Description |
  | --- | --- |
  | `write` | Produce a *SRS* draft based on the User Request description |
  | `create` | Write a *Software Requirements Specification* using the project's source code |
  | `recreate` | Reorganize and update the *Software Requirements Specification* based on source code analysis (preserve requirement IDs) |
  | `renumber` | Deterministically renumber requirement IDs in the *Software Requirements Specification* without changing requirement text or order |
  | `analyze` | Produce an analysis report |
  | `change` | Update the requirements and implement the corresponding changes |
  | `check` | Run the requirements check |
  | `cover` | Implement minimal changes to cover uncovered existing requirements |
  | `fix` | Fix a defect without changing the requirements |
  | `implement` | Implement source code from requirements (from scratch) |
  | `new` | Implement a new requirement and the corresponding source code changes |
  | `refactor` | Perform a refactor without changing the requirements |
  | `readme` | Write `README.md` from user-visible implementation evidence |
  | `references` | Write a `REFERENCES.md` using the project's source code |
  | `workflow` | Write a `WORKFLOW.md` using the project's source code |
  | `flowchart` | Write a `FLOWCHART.md` using the project's source code |


## Default Workflow

Click to zoom flowchart image.

[![Flowchart](https://raw.githubusercontent.com/Ogekuri/useReq/refs/heads/master/images/flowchart-bw.svg)](https://raw.githubusercontent.com/Ogekuri/useReq/refs/heads/master/images/flowchart-bw.svg)


## Quick Start

### Prerequisites

- Supported environment: `linux`
- Python 3.11+
- Install the `uv` tool from: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)


### Project's Tree

Here the typical project's tree, except for `.req` directory you can configurare the other directories according your project layout:

```text
.
├── .req/
│   └── useReq/req files
├── docs/
│   ├── FLOWCHART.md
│   ├── REQUIREMENTS.md
│   ├── REFERENCES.md
│   └── WORKFLOW.md
├── guidelines/
│   └── User's guidelines
├── src/
│   └── Source code
└── tests/
    └── Unit tests suite
```

### Run useReq/req with uvx
```bash
uvx --from git+https://github.com/Ogekuri/useReq.git req \
  --base myproject/ \
  --provider pi:prompts
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

### Quick Install

1. Install on a project in path `project_path` (missing directories are created automatically on fresh install):
- Typical Install:
```
req \
--base "project_path" \
--docs-dir "docs/" \
--guidelines-dir "guidelines/" \
--src-dir "src/" \
--tests-dir "tests/" \
--upgrade-guidelines \
--provider pi:prompts \
--provider claude:prompts \
--provider codex:skills \
--provider gemini:prompts \
--provider github:skills \
--provider kiro:agents \
--provider opencode:prompts \
--enable-static-check C=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c11 \
--enable-static-check C=Command,clang-format,--dry-run,--Werror \
--enable-static-check C++=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c++20 \
--enable-static-check C++=Command,clang-format,--dry-run,--Werror \
--enable-static-check Python=Pylance \
--enable-static-check Python=Ruff
```
2. Use `/req-write` or `/req-create` to create requirements
3. Use `/req-implement` to implement source-code from requirements, or `/req-cover` to cover new requirements (documentation).
4. Use `/req-workflow`, `/req-flowchart`, and/or `/req-references` to update project's documentation.
5. Start to use `/req-change`, `/req-new`, and `/req-fix`.

### Usage
- Run `req` to create or recreate useReq resources in your project repository (depending on enabled providers and artifact types). This can include: `.codex`, `.claude`, `.github`, `.gemini`, `.kiro`, `.opencode`, `.pi`, `.req`, and `.vscode`.
  - You can run `req` from any directory:
    - Use `--base <project-folder>` to target a specific project directory (recommended for first installation).
    - Use `--here` to target the current working directory.
    - For initialization, you cannot omit both `--base` and `--here`.
    - `--here` and `--update` load directory settings from `.req/config.json`, so first installation requires `--base`.
  - Directory flags for initialization:
    - `--docs-dir`, `--guidelines-dir`, `--tests-dir`, and `--src-dir` must resolve under the project base.
    - On fresh installation (`--base` without `--update`), omitted values default to `req/docs`, `req/guidelines/`, `tests/`, and `src/`.
    - On fresh installation, missing configured directories are created automatically.
    - `--src-dir` is repeatable and can be provided multiple times to include multiple source directories.
  - If `REQUIREMENTS.md` is missing in the configured docs directory, it is generated from the packaged template.
  - Use one or more `--provider SPEC` parameters (at least one is required) to configure provider activation, artifact types, and options:
    - `SPEC` format: `PROVIDER:ARTIFACT_ITEM[,ARTIFACT_ITEM...][:PROVIDER_OPTIONS]`
    - `PROVIDER`: `pi`, `codex`, `claude`, `gemini`, `github`, `kiro`, or `opencode`.
    - `ARTIFACT_ITEM`: `ARTIFACT` or `ARTIFACT+ARTIFACT_OPTIONS`.
    - `ARTIFACT`: one of `{prompts, agents, skills}`.
    - `ARTIFACT_OPTIONS`: `enable-models` and/or `enable-tools`, joined with `+`, and scoped only to that artifact item.
    - `PROVIDER_OPTIONS`: (optional) comma-separated list from `{prompts-use-agents, legacy}`.
    - Example: `--provider pi:prompts+enable-tools,skills+enable-models`
    - Migration note: `enable-models` and `enable-tools` are no longer valid in the trailing `:PROVIDER_OPTIONS` segment; attach them directly to each artifact item with `+`.
  - Artifact types (specified within the `--provider` spec):
    - `skills` artifact generates skill resources for the provider.
    - `prompts` artifact generates prompts/commands resources for the provider.
    - `agents` artifact generates agent resources for the provider.
    - Provider `pi` currently generates `.pi/prompts/req-<name>.prompt.md` and `.pi/skills/req-<name>/SKILL.md`.
  - `--enable-static-check SPEC` Enable static check configuration for a language (repeatable). SPEC format: `LANG=MODULE[,CMD[,PARAM...]]`.
      - Supported `MODULE` values: `Dummy`, `Pylance`, `Ruff`, `Command` (case-insensitive).
      - Entries are merged into `.req/config.json` without replacing existing ones: existing entries are preserved, identity-duplicates are ignored, and only new non-duplicate entries are appended per language.
- You need to run `req` again if you add or remove requirement-related files in the documentation directory or any files in the `guidelines/` directory.
- Provider-scoped option `prompts-use-agents` (in the optional `:PROVIDER_OPTIONS` segment) generates prompt files as **agent-only references** (adds an `agent:` front matter field) where supported (GitHub prompts, Claude commands, and OpenCode commands).
- Add `--verbose` and `--debug` to get detailed and diagnostic output.
- Add `--update` to update an existing installation (requires an existing `.req/config.json` under the project base).
  - Add `--preserve-models` to use and preserve `.req/models.json` during installation.
  - With `--update`, passing one or more `--provider` specs replaces persisted provider specs; without `--provider`, persisted specs are reused.
- Provider-scoped option `legacy` (in the optional `:PROVIDER_OPTIONS` segment) enables the *legacy mode* support (see below).
- Artifact-local options `enable-models` and `enable-tools` (set on each `ARTIFACT_ITEM` with `+`) include `model:` and `tools:` fields for that artifact when available from centralized models configuration.
- Add `--add-guidelines` to copy packaged guideline templates into `--guidelines-dir` without overwriting existing files.
- Add `--upgrade-guidelines` to copy packaged guideline templates into `--guidelines-dir` and overwrite existing files.
- Add `-h` / `--help` to print command help and exit.
- Add `--ver` / `--version` to print the installed package version and exit.
- Add `--remove` to remove resources generated by useReq from the target project (requires `--base` or `--here` and an existing `.req/config.json`; removes `.req/` and generated provider artifacts).
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

- Run static analysis on the given files using tools configured in `.req/config.json` (standalone, no --base/--here required).
  `--files-static-check FILE [FILE ...]`

- Count tokens and chars for canonical docs files in configured `docs-dir` (`REQUIREMENTS.md`, `WORKFLOW.md`, `REFERENCES.md`; here-only project scan: `--here` is implied when omitted, `--base` is not allowed, and explicit `--docs-dir` is ignored).
  `--tokens`

- Generate LLM reference markdown for source files selected by `git ls-files --cached --others --exclude-standard` under configured `src-dir` directories (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--references`

- Generate compressed output for source files selected by `git ls-files --cached --others --exclude-standard` under configured `src-dir` directories (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).  
  `--compress`

- Find and extract specific constructs from source files selected by `git ls-files --cached --others --exclude-standard` under configured `src-dir` directories (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--find TAG PATTERN`

- Run static analysis on source files selected by `git ls-files --cached --others --exclude-standard` under configured `src-dir` directories (plus configured `tests-dir`, excluding `fixtures/`) using tools configured in `.req/config.json` (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--static-check`

- Check repository integrity for the configured git path: clean working tree and valid HEAD (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--git-check`

- Check canonical docs presence in configured `docs-dir`: `REQUIREMENTS.md`, `WORKFLOW.md`, `REFERENCES.md` (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--docs-check`

- Create an isolated git worktree and branch with the provided name; also copies `.req/`, active provider directories, and `.venv` (when present) into the new worktree context (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--git-wt-create WT_NAME`

- Remove the git worktree and branch identified by name (force-removes the target worktree and deletes the branch; here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--git-wt-delete WT_NAME`

- Print the configured `git-path` value from `.req/config.json`; if `.req/config.json` is missing, the command fails with `Error: .req/config.json not found in the project root` (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--git-path`

- Print the configured `base-path` value from `.req/config.json`; if `.req/config.json` is missing, the command fails with `Error: .req/config.json not found in the project root` (here-only project scan: `--here` is implied when omitted, `--base` is not allowed).
  `--get-base-path`


- Add `--enable-line-numbers` to include `<n>:` prefixes in `--files-compress`, `--compress`, `--files-find`, and `--find` output.

- Test static check configuration and execution (standalone).
  `--test-static-check {dummy,pylance,ruff,command} [FILES...]`

#### Supported <TAG> in `--find` commands

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

- 🌟 **pi.dev CLI** 🌟 - Supports project-local prompt templates and Agent Skills from `.pi/prompts/` and `.pi/skills/`.
- 🌟 **GitHub Copilot** 🌟 - Many models available.
- 👍 **OpenCode** 👍 - Many models available. Does not support `tools:` on agents/prompts.
- ⚖️ **Claude Code** ⚖️ - Only supports Claude/Anthropic models.
- 🆗 **OpenAI Codex** 🆗 - Only supports OpenAI models. Does not support agents, `model:`, or `tools:` on prompts.
- 👎 **Kiro CLI** 👎 - Only supports Claude/Anthropic models. Does not support `$ARGUMENTS` on prompts.
- ☢️ **Gemini Code Assist** ☢️ - Only supports Google models. VS Code extension does not support agents or prompts.


### useReq/req Support
- ✅ pi.dev CLI
- ✅ OpenAI Codex
  - set environment variable **CODEX_HOME** to project's home before running the codex CLI
- ✅ Claude Code
- ✅ GitHub Copilot
- ✅ OpenCode
- ✔️ Gemini Code Assist
- ✔️ Kiro CLI

| ✅ supported | ✔️ partially supported | ❌ issues | ⛔ not supported |

#### Skills Details
- ✅ pi.dev CLI: [`/skill:req-create`]
  - useReq generates `.pi/skills/req-create/SKILL.md`.
  - pi discovers project skills from `.pi/skills/` and registers them as `/skill:name` commands.
  - Arguments after the command are appended to the skill content as `User: <args>`.
- ✅ OpenAI Codex: [`$req-create`]
- ✅ Claude Code: [`/req-create`]
- ✅ GitHub Copilot: [`/req-create`]
- ✅ OpenCode: [`/req-create`]
- ✅ Gemini: [`$req-create`]
- ❌ Kiro: Does not work as expected

#### CLI Prompt Details
- ✅ pi.dev CLI: [`/req-create.prompt`]
  - useReq generates `.pi/prompts/req-create.prompt.md`.
  - pi prompt templates use the filename without `.md` as the command name, so the generated `.prompt` suffix remains part of the slash command.
  - Prompt arguments are supported by pi prompt templates (`$1`, `$2`, `$@`, `$ARGUMENTS`).
- ✅ OpenAI Codex: [`/prompts:/req-create`]
- ✅ Claude Code: [`/req:create`]
- ✅ GitHub Copilot: [`/agent ➡️ req-create ↩️`]
  - Use provider-scoped `legacy` to not add `model:` on agents.
  - Slash command not supported.
  - Defect #980 [Model from agent.md isn't recognized #980](https://github.com/github/copilot-cli/issues/980)
  - Feature #618 → [Feature Request: Support custom slash commands from .github/prompts directory #618](https://github.com/github/copilot-cli/issues/618)
- ✅ OpenCode: [`/req-create`]
- ✅ Gemini: [`/req:create`]
- ❌ Kiro: [`'@/req-create'`]
  - Does not work as expected
  - Prompt parameters (`$ARGUMENTS`) are not evaluated by the Kiro CLI.
  - *no arguments supported for file-based prompts* → [Manage prompts](https://kiro.dev/docs/cli/chat/manage-prompts/)
  - Defect #4141 → [Saved prompt with arguments only works when entire message is quoted in CLI (Spec Kit + Kiro CLI 1.21.0) #4141](https://github.com/kirodotdev/Kiro/issues/4141)

#### CLI Agents Details
- ❌ pi.dev CLI
  - useReq does not generate `.pi/agents`; provider `pi` currently emits `.pi/prompts` and `.pi/skills` only.
- ❌ OpenAI Codex
- ✅ Claude Code: [`@agent-req-create`]
- ❌ GitHub Copilot
- ✔️ OpenCode: [`<TAB> ➡️ Req.Create ↩️`]
  - **Starts a new session** (`/new`) for every prompt.
- ✔️ Kiro: [`/agent swap; select agent ➡️ /req-create; ↩️`]
  - Does not work as expected
  - **Clears the context** (`/clear`) for every prompt.

#### Visual Studio Code Extension Details
- ❌ pi.dev CLI
  - useReq integrates pi through `.pi/` project resources; it does not generate a separate Visual Studio Code extension surface for provider `pi`.
- ✅ OpenAI Codex Extension for Visual Studio Code
  - Skills: [`/ ➡️ Req.Create ↩️`]
  - Prompts: [`/prompts:/req-create`]
  - set environment variable **CODEX_HOME** to project's home before running VS Code
- ✅ Claude Extension for Visual Studio Code
  - Skills: [`/req-create`]
  - Prompts: [`@agent-req-create`] (does not **highlight** agent like the CLI)
- ✔️ GitHub Copilot Agent Chat in Visual Studio Code
  - Agents: [`gui; select agent ➡️ /req-create; ↩️`]
  - **Starts a new chat** for every prompt.
- ✔️ OpenCode in Visual Studio Code
  - Supported with a windowed CLI
- ✔️ Gemini Code Assist Extension for Visual Studio Code
  - Skills: [`$req-create`] (does not **highlight** skills like the CLI)
  - Prompts/Agents not supported by the VS Code extension
- ❌ Kiro in VS Code is not supported


## Known Issues

- **Grok Code Fast 1** does not respect the TODO list and does not wait for user approval.
  * Defect #3180 → [Bug: Grok Code Fast 1 not update to do list correctly #3180](https://github.com/Kilo-Org/kilocode/issues/3180)


## Enable model and tools on prompts/agents

`enable-tools` and `enable-models` are artifact-local `--provider` options. Attach them directly to each artifact item with `+`, for example `claude:prompts+enable-models+enable-tools` or `github:prompts+enable-models,skills+enable-tools`.

The `enable-tools` option adds a `tools:` specification when the selected artifact/provider combination has a matching `usage_modes` entry in `src/usereq/resources/common/models.json`.

The `enable-models` option adds a `model:` specification using the mappings from `src/usereq/resources/common/models.json`.

The prompt-name mappings below are also reused for generated skill artifacts when the provider supports `skills`.

### pi.dev CLI

#### Tool Sets

- `read_only`: `read`, `bash`, `grep`, `find`, `ls`
- `read_write`: `read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`

#### Configured Models

| Prompts | Model | Mode |
| --- | --- | --- |
| `analyze`, `check` | `Gemini 3.1 Pro (Preview) (copilot)` | `read_only` |
| `create`, `readme`, `recreate`, `write` | `Gemini 3.1 Pro (Preview) (copilot)` | `read_write` |
| `change`, `cover`, `fix`, `flowchart`, `implement`, `new`, `refactor`, `renumber`, `workflow` | `GPT-5.3-Codex (copilot)` | `read_write` |

### GitHub Copilot

#### Tool Sets

- `read_only`: `vscode`, `execute`, `read`, `search`, `ms-python.python/getPythonEnvironmentInfo`, `ms-python.python/getPythonExecutableCommand`, `ms-python.python/installPythonPackage`, `ms-python.python/configurePythonEnvironment`, `todo`
- `read_write`: `vscode`, `execute`, `read`, `edit`, `search`, `ms-python.python/getPythonEnvironmentInfo`, `ms-python.python/getPythonExecutableCommand`, `ms-python.python/installPythonPackage`, `ms-python.python/configurePythonEnvironment`, `todo`

#### Configured Models

| Prompts | Model | Mode |
| --- | --- | --- |
| `analyze`, `check` | `Gemini 3.1 Pro (Preview) (copilot)` | `read_only` |
| `create`, `readme`, `recreate`, `write` | `Gemini 3.1 Pro (Preview) (copilot)` | `read_write` |
| `change`, `cover`, `fix`, `flowchart`, `implement`, `new`, `refactor`, `renumber`, `workflow` | `GPT-5.3-Codex (copilot)` | `read_write` |

### Claude Code

#### Tool Sets

- `read_only`: `Read`, `Grep`, `Glob`, `ReadFile`, `Pytest`
- `read_write`: `Read`, `Grep`, `Glob`, `ReadFile`, `Edit`, `WriteFile`, `DeleteFile`, `Pytest`

#### Configured Models

| Prompts | Model | Mode |
| --- | --- | --- |
| `analyze`, `check` | `haiku` | `read_only` |
| `create`, `flowchart`, `readme`, `recreate`, `workflow`, `write` | `haiku` | `read_write` |
| `change`, `new` | `sonnet` | `read_write` |
| `cover`, `fix`, `implement`, `refactor`, `renumber` | `opus` | `read_write` |

### Kiro CLI

#### Tool Sets

- `read_only`: `read`, `glob`, `grep`, `shell`, `todo`, `todo_list`, `thinking`
- `read_write`: `read`, `glob`, `grep`, `write`, `shell`, `todo`, `todo_list`, `thinking`

#### Configured Models

| Prompts | Model | Mode |
| --- | --- | --- |
| `analyze`, `check` | `claude-haiku-4.5` | `read_only` |
| `create`, `flowchart`, `readme`, `recreate`, `workflow`, `write` | `claude-haiku-4.5` | `read_write` |
| `change`, `cover`, `fix`, `implement`, `new`, `refactor`, `renumber` | `claude-sonnet-4.5` | `read_write` |

### OpenCode CLI

Models depend on the user's provider; the bundled configuration uses GitHub-hosted model identifiers.

`src/usereq/resources/common/models.json` defines prompt models for OpenCode, but it does not define `usage_modes` for the `opencode` provider, so artifact items using `+enable-tools` currently have no centralized `tools:` value to inject.

#### Configured Models

| Prompts | Model | Mode |
| --- | --- | --- |
| `analyze`, `check` | `github-copilot/gemini-3.1-pro-preview` | `read_only` |
| `create`, `readme`, `recreate`, `write` | `github-copilot/gemini-3.1-pro-preview` | `read_write` |
| `change`, `cover`, `fix`, `flowchart`, `implement`, `new`, `refactor`, `renumber`, `workflow` | `github-copilot/claude-opus-4.6` | `read_write` |

### OpenAI Codex CLI

#### Tool Sets

- `read_only`: `read`, `glob`, `grep`, `shell`, `todo`, `todo_list`, `thinking`
- `read_write`: `read`, `glob`, `grep`, `write`, `shell`, `todo`, `todo_list`, `thinking`

#### Configured Models

| Prompts | Model | Mode |
| --- | --- | --- |
| `analyze`, `check` | `gpt-5.3-codex` | `read_only` |
| `create`, `readme`, `recreate`, `write` | `gpt-5.2` | `read_write` |
| `change`, `cover`, `fix`, `flowchart`, `implement`, `new`, `refactor`, `renumber`, `workflow` | `gpt-5.3-codex` | `read_write` |

### Gemini CLI

`src/usereq/resources/common/models.json` currently defines no centralized prompt-model map or tool sets for the `gemini` provider, so artifact items using `+enable-models` or `+enable-tools` have no bundled values to inject for Gemini artifacts.


## Note on Git usage

This section describes the Git behavior when executing the commands provided by the scripts.

- Required state before execution:
  - Execute commands from a working branch (not in detached HEAD).
  - Preferably, the working tree should be clean: avoid unintended changes in the repository before starting the scripts.
  - Save all files and verify that you are in the correct project directory.
  - **IMPORTANT:** `useReq/req` uses the `.req/` directory (including `.req/config.json`). Keep `.req/` tracked in the Git repository (do not ignore it), so `git worktree` checkouts include the same configuration; otherwise commands that depend on project configuration can fail.

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

The *Legacy Mode* is enabled per provider via `--provider SPEC` options.

Use `legacy` in the optional `:PROVIDER_OPTIONS` segment of `PROVIDER:ARTIFACT_ITEM[,ARTIFACT_ITEM...][:PROVIDER_OPTIONS]`, for example:

```bash
req --provider github:agents:legacy
```

Standalone `--legacy` is not a supported CLI flag.

### GitHub Copilot

In *Legacy Mode* the unsupported `model:` is not added to agents.
See: Defect #980 [Model from agent.md isn't recognized #980](https://github.com/github/copilot-cli/issues/980)
