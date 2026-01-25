---
title: "useReq Requirements"
description: "Software Requirements Specification"
date: "2026-01-25"
version: 0.42
author: "Ogekuri"
scope:
  paths:
    - "**/*.py"
    - "**/*.ipynb"
    - "**/*.c"
    - "**/*.h"
    - "**/*.cpp"
  excludes:
    - ".*/**"
visibility: "draft"
tags: ["markdown", "requirements", "useReq"]
---

# useReq Requirements
**Version**: 0.42
**Author**: Ogekuri
**Date**: 2026-01-25

## Table of Contents
<!-- TOC -->
- [useReq Requirements](#usereq-requirements)
  - [Table of Contents](#table-of-contents)
  - [Revision History](#revision-history)
  - [1. Introduction](#1-introduction)
    - [1.1 Document Rules](#11-document-rules)
    - [1.2 Project Scope](#12-project-scope)
    - [1.3 Components and Libraries Used](#13-components-and-libraries-used)
    - [1.4 Project Structure](#14-project-structure)
    - [1.5 Main Components and Relationships](#15-main-components-and-relationships)
    - [1.6 Optimizations and Performance](#16-optimizations-and-performance)
    - [1.7 Test Suite](#17-test-suite)
  - [2. Project Requirements](#2-project-requirements)
    - [2.1 Project Functions](#21-project-functions)
    - [2.2 Project Constraints](#22-project-constraints)
  - [3. Requirements](#3-requirements)
    - [3.1 Design and Implementation](#31-design-and-implementation)
    - [3.2 CLI Interface \& General Behavior](#32-cli-interface--general-behavior)
    - [3.3 Installation \& Updates](#33-installation--updates)
    - [3.4 Version Check](#34-version-check)
    - [3.5 Project Initialization \& Configuration](#35-project-initialization--configuration)
    - [3.6 Resource Generation - Common](#36-resource-generation---common)
    - [3.7 Resource Generation - Specific Tools](#37-resource-generation---specific-tools)
      - [3.7.1 GitHub \& Codex](#371-github--codex)
      - [3.7.2 Gemini](#372-gemini)
      - [3.7.3 Kiro](#373-kiro)
      - [3.7.4 OpenCode](#374-opencode)
      - [3.7.5 Claude](#375-claude)
    - [3.8 Removal](#38-removal)
    - [3.9 Development \& Testing](#39-development--testing)
    - [3.10 CI/CD Workflows](#310-cicd-workflows)
<!-- TOC -->

## Revision History
| Date | Version | Reason and Description of Change |
|------|---------|----------------------------------|
| 2025-12-31 | 0.0 | Creation of requirements draft. |
| 2026-01-01 | 0.1 | Added req.sh script to run in-development version with venv. |
| 2026-01-01 | 0.2 | Added version printing for invocations without arguments and with dedicated options. |
| 2026-01-01 | 0.3 | Added help printing with version for invocations without arguments and version-only printing for dedicated options. |
| 2026-01-01 | 0.4 | Added version and command in the help usage string. |
| 2026-01-01 | 0.5 | Updated Gemini command generation in dedicated subfolder. |
| 2026-01-01 | 0.6 | Added support for Kiro CLI resource generation. |
| 2026-01-01 | 0.7 | Modified --doc command to accept directories and generate file lists. |
| 2026-01-01 | 0.8 | Restored path relativization and test organization under temp/. |
| 2026-01-01 | 0.9 | Modified --dir command to process subfolders and generate directory lists. |
| 2026-01-01 | 0.10 | Updated Kiro prompt generation with full Markdown body. |
| 2026-01-01 | 0.11 | Added support for --upgrade option and updated usage. |
| 2026-01-01 | 0.12 | Added support for --uninstall option and updated usage. |
| 2026-01-01 | 0.13 | Added persistent configuration for --doc and --dir. |
| 2026-01-02 | 0.14 | Added support for --update option. |
| 2026-01-02 | 0.15 | Added support for --remove option and settings restoration. |
| 2026-01-02 | 0.16 | Added requirement for English language output. |
| 2026-01-02 | 0.17 | Added requirements for English language comments in source code. |
| 2026-01-02 | 0.18 | Added requirement for Kiro resource ordering. |
| 2026-01-09 | 0.19 | Added support for OpenCode resource generation. |
| 2026-01-10 | 0.20 | Added support for Claude Code CLI resource generation. |
| 2026-01-11 | 0.21 | Modified OpenCode support: removed opencode.json generation, added individual agent generation in .opencode/agent/ with "all" mode. |
| 2026-01-11 | 0.22 | Modified OpenCode agent generation in .opencode/agent/ from JSON to Markdown with front matter. |
| 2026-01-11 | 0.23 | Removed generation of .opencode/prompts folder. |
| 2026-01-11 | 0.24 | Added requirement REQ-040: generation of front matter `name` for agents in `.github/agents`. |
| 2026-01-11 | 0.25 | Removed `model: inherit` obligation for agents in `.github/agents` (REQ-040 updated). |
| 2026-01-11 | 0.27 | Added detailed output in unit tests to show test list, current execution, check, and result. |
| 2026-01-11 | 0.28 | Avoided generation of .req/settings.json.absent; --remove does not modify .vscode/settings.json; idempotent merge of VS Code settings. |
| 2026-01-11 | 0.29 | Clarified --remove behavior: the .req folder must be completely removed; removed obligation to restore VS Code settings during --remove. |
| 2026-01-11 | 0.30 | Added requirements and GitHub Actions workflow for build on v* tags and attestation generation for release. |
| 2026-01-11 | 0.31 | Added online check for new version availability (GitHub releases latest). |
| 2026-01-14 | 0.32 | Removed default `model: inherit` setting for Claude Code; added optional `model` and `tools` management based on flags and configuration file; updated requirements and tests. |
| 2026-01-14 | 0.33 | Forbidden any test writing outside of `temp/`; updated requirements and test suite. |
| 2026-01-14 | 0.34 | Corrected population of `resources` field in Kiro agents from `config.json` template maintaining original format. |
| 2026-01-14 | 0.35 | Updated Kiro requirement so that `tools` and `allowedTools` are populated with arrays declared in `usage_modes` for each prompt. |
| 2026-01-15 | 0.36 | Added front matter generation for Claude commands in `.claude/commands/req` with `agent`, `model` (optional), and `allowed-tools` (optional, CSV) fields. |
| 2026-01-23 | 0.39 | Removed `--parse-prompts` (REQ-075) from requirements; flag was redundant and removed from CLI. |
| 2026-01-24 | 0.40 | Relaxed commenting requirements (DES-009, DES-010); removed REQ-073 (--yolo); updated agent generation conditional on --prompts-use-agents (REQ-038, REQ-039, REQ-051, REQ-056); clarified Kiro vs GitHub content (REQ-043); removed fallback to default mode in Kiro (REQ-047). |
| 2026-01-24 | 0.41 | Removed REQ-077: removed runtime bootstrap substitution (`%%BOOTSTRAP%%`) from prompt processing and aligned tests by removing the corresponding test that validated this behavior. |
| 2026-01-25 | 0.42 | Added REQ-078: CLI prints a single-line success message including resolved installation path when installation/update completes successfully. |

## 1. Introduction
This document defines the software requirements for useReq, a CLI utility that initializes a project with templates, prompts, and agent resources, ensuring consistent relative paths with respect to the project root.

### 1.1 Document Rules
This document must always follow these rules:
- This document must be written in English.
- Requirements must be formatted as a bulleted list, using the verb "must" to indicate mandatory actions.
- Each identifier (**PRJ-001**, **PRJ-002**, **CTN-001**, **CTN-002**, **DES-001**, **DES-002**, **REQ-012**, **REQ-036**, …) must be unique.
- Each identifier must start with the prefix of its requirement group (PRJ-, CTN-, DES-, REQ-).
- Each requirement must be identifiable, verifiable, and testable.
- With each modification of the document, the version number and revision history must be updated by adding an entry to the bottom of the list.

### 1.2 Project Scope
The project scope is to provide a `use-req`/`req` command that, given a project, initializes requirement files, technical folders, and prompt resources for development tools, ensuring safe relative paths and a repeatable setup.

### 1.3 Components and Libraries Used
- Python 3.11+ as package runtime.
- Standard libraries (`argparse`, `json`, `pathlib`, `shutil`, `os`, `re`, `sys`) for CLI parsing, file management, and paths.
- `setuptools` and `wheel` for packaging and distribution.

### 1.4 Project Structure
```
.
├── CHANGELOG.md
├── LICENSE
├── README.md
├── TODO.md
├── docs
│   └── requirements.md
├── other-stuff
│   └── templates
│       ├── srs-template-bare.md
│       └── srs-template.md
├── pyproject.toml
└── src
    └── usereq
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── kiro
        │   └── agent.json
        └── resources
            ├── prompts
            │   ├── analyze.md
            │   ├── change.md
            │   ├── check.md
            │   ├── cover.md
            │   ├── fix.md
            │   ├── new.md
            │   ├── optimize.md
            │   └── write.md
            ├── templates
            │   └── requirements.md
            └── vscode
                └── settings.json
```

### 1.5 Main Components and Relationships
- `usereq.cli` contains the main command logic, argument parsing, and initialization flow.
- `usereq.__main__` exposes execution as a Python module and delegates to `usereq.cli.main`.
- `usereq.__init__` provides version metadata and a re-export of the `main` entry point.
- `resources/prompts`, `resources/templates`, and `resources/vscode` contain the source files that the command copies or integrates into the target project.

### 1.6 Optimizations and Performance
There are no explicit performance optimizations; the code is limited to linear processing of files and paths necessary for initialization.

### 1.7 Test Suite
No unit tests found in the repository.

## 2. Project Requirements
### 2.1 Project Functions
- **PRJ-001**: The command must initialize a project by creating or updating requirement documents, technical templates, and prompt resources based on the root indicated by the user.
- **PRJ-002**: The command must accept exactly one of the options `--base` or `--here` and parameters `--doc` and `--dir` to determine the project root and paths to manage.
- **PRJ-003**: The command must generate prompt resources for Codex, GitHub, and Gemini by replacing path tokens with calculated relative values.
- **PRJ-004**: The command must update local templates in `.req/templates` and integrate VS Code settings when available.
- **PRJ-005**: The user interface must be a textual CLI with error messages and optional progress logs.

### 2.2 Project Constraints
- **CTN-001**: The values of `--doc` and `--dir` can be absolute or relative paths. Paths must be normalized to paths relative to the project root passed with `--base` by checking if it is present in the paths passed with `--doc` and `--dir`.
- **CTN-002**: The path passed to `--doc` and then normalized with respect to `--base`, must exist as a real directory under the project root before resource copying.
- **CTN-003**: The path passed to `--dir` and then normalized with respect to `--base`, must exist as a real directory under the project root before resource copying.
- **CTN-004**: Removal of pre-existing `.req` or `.req/templates` directories must be allowed only if such paths are under the project root.
- **CTN-005**: The command must fail if the specified project does not exist on the filesystem.

## 3. Requirements
### 3.1 Design and Implementation
- **DES-001**: The calculation of tokens `%%REQ_DOC%%` and `%%REQ_DIR%%` must be replaced with the list of documents and directories found in the folders specified with `--doc` and `--dir`. When expanded inline, these lists must be formatted using inline code notation (backticks) for each item rather than markdown links. For documents use the form `file1`, `file2`, `file3`; for directories use the form `dir1/`, `dir2/` (note the trailing slash to indicate directories).
- **DES-002**: The source of the `requirements.md` template must be the `resources/templates` folder included in the package and the command must fail if the template is not available.
- **DES-003**: The conversion of Markdown prompts to TOML must extract the `description` field from the front matter and save the prompt body in a multiline string.
- **DES-004**: The merge of VS Code settings must support JSONC files by removing comments and must recursively merge objects with priority to template values.
- **DES-005**: The recommendations `chat.promptFilesRecommendations` must be generated starting from available Markdown prompts.
- **DES-006**: The package entry point must expose `usereq.cli:main` via `use-req`, `req`, and `usereq`.
- **DES-007**: Expected errors must be handled via a dedicated exception with non-zero exit code.
- **DES-008**: All comments in source codes must be written exclusively in English. Exceptions are made for source file header comments. For example, comments indicating versions and/or authors like "# VERSION:" or "# AUTHORS:" which maintain standard English formatting.
- **DES-009**: Every important part of the code (classes, complex functions, business logic, critical algorithms) should be commented where necessary, though explanatory comments may be minimal for self-evident business logic.
- **DES-010**: Every new functionality added should include explanatory comments where applicable; modification of existing code does not strictly require updating pre-existing comments if the logic remains clear.
- **DES-011**: The static strings used for the `%%WORKFLOW%%` token substitution must be stored as plain text files inside the package resources under `src/usereq/resources/common/` with the filenames `workflow_on.md` and `workflow_off.md`. At runtime the CLI must load these files and use their contents for the `%%WORKFLOW%%` substitution. If the files are not present or cannot be read, the CLI must fall back to sensible built-in default texts that preserve previous behavior.

### 3.2 CLI Interface & General Behavior
- **REQ-001**: When the `req` command is invoked without parameters, the output must include help and the version number defined in `src/usereq/__init__.py` (`__version__`).
- **REQ-002**: When the `req` command is invoked with the `--ver` or `--version` option, the output must contain only the version number defined in `src/usereq/__init__.py` (`__version__`).
- **REQ-003**: The help usage string must include the command `req` and the version `__version__` in the format `usage: req -c [-h] [--upgrade] [--uninstall] [--remove] [--update] (--base BASE | --here) --doc DOC --dir DIR [--verbose] [--debug] [--enable-models] [--enable-tools] (major.minor.patch)` with major.minor.patch from `__version__`.
- **REQ-004**: All usage, help, information, verbose, or debug outputs of the script must be in English.
- **REQ-005**: The command must verify that the `--doc` parameter indicates an existing directory, otherwise it must terminate with error.

### 3.3 Installation & Updates
- **REQ-006**: The `--upgrade` option must execute the command `uv tool install usereq --force --from git+https://github.com/Ogekuri/useReq.git` and terminate with error if the command fails.
- **REQ-007**: The help usage string must include the `--upgrade` parameter as an available option.
- **REQ-008**: The `--uninstall` option must execute the command `uv tool uninstall usereq` and terminate with error if the command fails.
- **REQ-009**: The help usage string must include the `--uninstall` parameter as an available option.

- **REQ-078**: After successful completion of an installation or an update operation (that is, when the command finishes all intended filesystem modifications without error and exits with status code 0), the CLI must print a single line in English informing the user that the installation completed successfully and include the resolved project root path used for the operation. The message format must be exactly:
  - "Installation completed successfully in <path>"
  - where `<path>` is the absolute path to the project root as resolved from the `--base` parameter or the absolute working directory when `--here` was used. This line must be printed only on successful completion and must not be emitted on error paths or when the command performs a dry-run or validation-only flow.

### 3.4 Version Check
- **REQ-010**: The command, after successfully validating inputs and before performing any operation modifying the filesystem, must verify online availability of a new version by performing an HTTP GET call to `https://api.github.com/repos/Ogekuri/useReq/releases/latest` with a 1-second timeout.
- **REQ-011**: If the call fails (timeout/network error/invalid response), the command must proceed without printing anything. If the call succeeds and the remote version (read from JSON `tag_name` field and normalized by removing any `v` prefix) is greater than `__version__`, the command must print a message in English indicating current version and available version and must indicate how to update using `req --upgrade`.

### 3.5 Project Initialization & Configuration
- **REQ-012**: If the directory indicated by `--doc` is empty, the command must generate a `requirements.md` file from the template.
- **REQ-013**: The project must include a `req.sh` script in the repository root to start the in-development version of the command.
- **REQ-014**: The `req.sh` script must be executable from any path, resolve its own directory, verify the presence of `.venv` in that directory and, if absent, create the venv and install packages from `requirements.txt` before execution.
- **REQ-015**: If `.venv` exists, the `req.sh` script must execute the command using the venv's Python without reinstalling packages, forwarding received arguments.
- **REQ-016**: The command must save values of `--doc` and `--dir` in `.req/config.json` after validation and normalization into paths relative to the project root, and before selecting files present in `--doc` and directories present in `--dir`.
- **REQ-017**: The `.req/config.json` file must include fields `doc` and `dir` with relative paths and preserve any trailing slash of `--dir` to allow bypassing `--doc` and `--dir` parameters.
- **REQ-018**: The command must support the `--update` option to re-execute initialization using parameters saved in `.req/config.json`.
- **REQ-019**: When `--update` is present, the command must verify the presence of `.req/config.json` in the project root and terminate with error if the file does not exist.
- **REQ-020**: When `--update` is present, the command must load fields `doc` and `dir` from `.req/config.json` and execute the flow as if `--doc` and `--dir` were passed manually, without rewriting `.req/config.json`.
- **REQ-021**: The command must copy templates into `.req/templates`, replacing any pre-existing templates.
- **REQ-022**: If the VS Code template is available, the command must create or update `.vscode/settings.json` merging settings with existing ones and adding recommendations for prompts.
- **REQ-023**: Before modifying `.vscode/settings.json`, the command must save the original state in a backup file under `.req/` to allow restoration with `--remove`.
- **REQ-024**: During installation or update of VS Code settings (`.vscode/settings.json`), the command must calculate the merge result and verify if the resulting content differs from currently present content; if there are no semantic differences, the command must not rewrite the file nor create backups. If changes are expected, the command must create a backup only if the target file already exists, then apply changes.
- **REQ-025**: The file `.req/settings.json.absent` must never be generated by the command.

### 3.6 Resource Generation - Common
- **REQ-026**: The command must examine all files contained in the `--doc` directory in alphabetical order and replace the string `%%REQ_DOC%%` with a list of files formatted using inline code (backticks), in the form `file1`, `file2`, `file3` separated by ", " (comma space). Each entry must be the path relative to the project root as calculated by the script.
- **REQ-027**: The list of files for `%%REQ_DOC%%` replacement must use relative paths calculated by the script, net of the absolute path and relative to the project home.
- **REQ-028**: The script must relativize paths that contain the project home path (e.g., temp/project_sample/docs/ becomes docs/).
- **REQ-029**: The command must examine all subfolders contained in the `--dir` directory in alphabetical order and replace the string `%%REQ_DIR%%` with a list of directories formatted using inline code (backticks), in the form `dir1/`, `dir2/`, `dir3/` separated by ", " (comma space). Each entry must be the path relative to the project root as calculated by the script. Directory entries must include a trailing slash to indicate directory semantics.
- **REQ-030**: If the directory indicated by `--dir` is empty, it must use the directory itself for `%%REQ_DIR%%` replacement.
- **REQ-031**: The list of directories for `%%REQ_DIR%%` replacement must use relative paths calculated by the script.
- **REQ-032**: The command must support options `--enable-models` and `--enable-tools` (optional) to include respectively fields `model` and `tools` in generated agent/prompt files when available.
- **REQ-033**: If `--enable-models` is present, for each generated prompt the command must search, within folders `src/usereq/resources/{claude,copilot,opencode,kiro,gemini}`, for `config.json` files and, if the file exists and contains an entry for the prompt, include `model: <value>` in the front matter or JSON/TOML of the generated agent.
- **REQ-034**: If `--enable-tools` is present, for each generated prompt the command must, if available in `config.json`, include the `tools` field derived from `usage_modes[mode]["tools"]` for the `mode` specified in the prompt entry. The `config.json` can specify `tools` as a list of strings or as a comma-separated string; the CLI must accept both forms. When generating files for OpenCode (`.opencode/agent` and `.opencode/command`), the CLI must preserve the original type defined in `config.json`: if the value is a string, it must be inserted into files as a string (without converting it to an array); if it is a list, it must be inserted as an array. For other targets (e.g., Gemini, Kiro, GitHub, Claude) existing behavior (normalization to list when required) remains unchanged.
- **REQ-035**: Inclusion of `model` and `tools` is conditional on the existence and validity of the `config.json` file for the relative CLI; in the absence of the corresponding key, no field will be added (no additional backward compatibility behaviors are expected).

 
- **REQ-076**: The CLI must accept a boolean flag `--enable-workflow` (default false). During prompt processing, the token `%%WORKFLOW%%` must be substituted with a static text. Substitution must occur at runtime only and must not modify any source templates on disk. This requirement must be backward compatible with existing CLI behavior when the flag is not provided.

 - **REQ-076**: The CLI must accept a boolean flag `--enable-workflow` (default false). When `--enable-workflow` is present, during prompt processing the token `%%WORKFLOW%%` must be substituted at runtime only with a static text loaded from package resources (`src/usereq/resources/common/workflow_on.md` when available, or a sensible built-in default otherwise). Substitution must never modify source template files on disk. When `--enable-workflow` is not present (default), the CLI must not generate any `workflow` prompt files or `workflow` agents for any provider; existing templates and resources on disk must remain unchanged. This behavior must be backward compatible with previous CLI behavior when the flag is omitted.

 - **REQ-079**: Provider configuration files under `src/usereq/resources/` may include an optional `workflow` prompt entry. For providers that define per-prompt `model` and `mode` values, a `workflow` entry, if present, should have `model` and `mode` values consistent with the provider's `create` prompt when that is the intended behavior. The CLI must treat `workflow` as a normal prompt only when `--enable-workflow` is active: in that case, generators should include the `workflow` prompt and, if `--enable-models` is set, include the `model` value for `workflow` from the provider configuration. If a provider configuration does not include a `workflow` entry, and `--enable-workflow` is active, generators that rely on provider `model` metadata must fall back to the `create` prompt's `model` and `mode` for `workflow` without modifying provider configuration files on disk. When `--enable-workflow` is not active, no `workflow` prompt generation or `model` injection for `workflow` must occur.
 

### 3.7 Resource Generation - Specific Tools
#### 3.7.1 GitHub & Codex
- **REQ-036**: The command must create folders `.codex/prompts`, `.github/agents`, `.github/prompts`, `.gemini/commands` and `.gemini/commands/req` under the project root.
- **REQ-037**: For each available Markdown prompt, the command must copy the file into `.codex/prompts` and `.github/agents` replacing `%%REQ_DOC%%`, `%%REQ_DIR%%` and `%%ARGS%%` with calculated values.
- **REQ-038**: For each available Markdown prompt, the command must create a file `.github/prompts/req.<name>.prompt.md`. This file must reference the agent `req.<name>` only if the `--prompts-use-agents` option is enabled; otherwise, it must contain the description and prompt body.
- **REQ-039**: The command must create the configuration `.github/prompts` with front matter referencing the agent in use only if the `--prompts-use-agents` option is enabled.
- **REQ-040**: For each available Markdown prompt, the command must generate a file `.github/agents/req.<name>.agent.md` with front matter including `name` set to `req-<name>`, preserving `description` from the source prompt.

#### 3.7.2 Gemini
- **REQ-041**: For each available Markdown prompt, the command must generate a TOML file in `.gemini/commands/req` with name `<name>.toml` (without `req.` prefix), converting the Markdown and replacing `%%REQ_DOC%%`, `%%REQ_DIR%%` and `%%ARGS%%` with appropriate values for Gemini.

#### 3.7.3 Kiro
- **REQ-042**: The command must create folders `.kiro/agents` and `.kiro/prompts` under the project root.
- **REQ-043**: For each available Markdown prompt, the command must copy the file into `.kiro/prompts` using the source front matter and prompt body with replacements. This content differs from `.github/agents` which uses a generated front matter.
- **REQ-044**: For each available Markdown prompt, the command must generate a JSON file in `.kiro/agents` with name `req.<name>.json` using the template contained in `src/usereq/resources/kiro/config.json` in the `agent_template` field. The `config.json` file must include a top-level `settings` object (e.g., {"version": "0.0.46", "default_mode": "read_only"}) and the `agent_template` field, which can be a JSON string or a JSON object, with tokens `%%NAME%%`, `%%DESCRIPTION%%`, `%%PROMPT%%` and optionally `%%RESOURCES%%`; the command must replace tokens and populate the agent's `resources` field with the generated array even when the template contains an empty array instead of the explicit token.
- **REQ-045**: In Kiro JSON files, fields `name`, `description`, and `prompt` must be populated respectively with `req-<name>`, the `description` from the prompt front matter, and the Markdown prompt body without the initial section between delimiters `---`, with double quotes `"` escaped.
- **REQ-046**: In Kiro JSON files, the `resources` field must be populated by the command regardless of how it is defined in the template, including as the first item the corresponding prompt file in `.kiro/prompts/req.<name>.md` and, following that, links to identified requirements.
- **REQ-047**: The command must populate the `tools` and `allowedTools` fields in `.kiro/agents/req.<name>.json` with arrays declared in `usage_modes[mode]["tools"]` of the Kiro configuration, using the `mode` of each prompt only if present. If the prompt mode is missing, no tools are set.

#### 3.7.4 OpenCode
- **REQ-048**: For each available Markdown prompt, the command must generate a Markdown file in `.opencode/agent` with name `req.<name>.md` with front matter containing `description` from the prompt front matter description and `mode` set to "all", followed by the prompt body with substitutions `%%REQ_DOC%%`, `%%REQ_DIR%%`, and `%%ARGS%%`.
- **REQ-049**: The command must create the folder `.opencode/agent` under the project root.
- **REQ-050**: The command must create the folder `.opencode/command` under the project root.
- **REQ-051**: For each available Markdown prompt, the command must generate a file in `.opencode/command` with name `req.<name>.md` including YAML front matter containing:
  - `agent:` valued with the name of the corresponding file in `.opencode/agent` (e.g., `req.analyze`) only if the `--prompts-use-agents` option is enabled,
  - optionally `model:` and `tools:` when tags `--enable-models` and/or `--enable-tools` are active and relative values are present in CLI `config.json`,
  - followed by a separator line and the prompt body with the same substitutions (`%%REQ_DOC%%`, `%%REQ_DIR%%`, `%%REQ_PATH%%`, `%%ARGS%%`) applied for `.kiro/prompts`.
When `--remove` is present, files generated in `.opencode/command` must be removed and empty directories under `.opencode` deleted.

#### 3.7.5 Claude
- **REQ-052**: The command must create the folder `.claude/agents` under the project root.
- **REQ-053**: For each available Markdown prompt, the command must generate a file `.claude/agents/req.<name>.md` applying the same token substitutions used for `.kiro/prompts`.
- **REQ-054**: In `.claude/agents/req.<name>.md` files, the initial front matter must include fields `name` and `description` valued from the source prompt. The `model` field must not be automatically added by the application: the `model` field can be included only if the `--enable-models` parameter is passed and the file `src/usereq/resources/claude/config.json` contains a valid entry for the corresponding prompt. Similarly, the `tools` field can be included only if the `--enable-tools` parameter is passed and `config.json` provides `usage_modes[mode]["tools"]` for the prompt's `mode`. In the absence of these flags or valid values in `config.json`, the `model` and `tools` fields must not be present in the generated files.
- **REQ-055**: The command must create the folder `.claude/commands` and its subfolder `.claude/commands/req` under the project root.
- **REQ-056**: For each available Markdown prompt, the command must generate a file in `.claude/commands/req` with name `<name>.md` including an initial YAML front matter containing:
  - `agent`: valued with the same `name` identifier present in `.claude/agents/req.<name>.md` (e.g., `req-<name>`) only if the `--prompts-use-agents` option is enabled.
  - optionally `model`: included only if the `--enable-models` option is passed and `src/usereq/resources/claude/config.json` contains a `model` entry for the corresponding prompt; the value must be copied as is from `config.json`.
  - optionally `allowed-tools`: included only if the `--enable-tools` option is passed and `config.json` provides `usage_modes[mode]["tools"]` for the prompt's `mode`; the field must be a CSV string in double quotes, formatted as `"Read, Grep, Glob"`.
  - Followed by a separator line `---` and then the Markdown prompt body with the same token substitutions (`%%REQ_DOC%%`, `%%REQ_DIR%%`, `%%REQ_PATH%%`, `%%ARGS%%`).

### 3.8 Removal
- **REQ-057**: The command must support the `--remove` option to remove resources created by installation in the project root indicated by `--base` or `--here`.
- **REQ-058**: When `--remove` is present, the command must mandatorily require `--base` or `--here` and must refuse usage of `--doc`, `--dir` or `--update`.
- **REQ-059**: When `--remove` is present, the command must verify the existence of `.req/config.json` in the project root and terminate with error if absent.
- **REQ-060**: When `--remove` is present, the command must not restore `.vscode/settings.json` from the original state using backups kept in `.req/` (the `.req/` directory will be removed when the --remove option is used).
- **REQ-061**: When `--remove` is present, the command must remove created resources: `.codex/prompts/req.*`, `.github/agents/req.*`, `.github/prompts/req.*`, `.gemini/commands/req/`, `.kiro/agents/req.*`, `.kiro/prompts/req.*`, `.req/templates/`, `.req/config.json` and the complete `.req/` folder (all files and subfolders must be deleted).
- **REQ-062**: After removal, the command must delete empty subfolders under `.gemini`, `.codex`, `.kiro`, and `.github` iterating from bottom to top.
- **REQ-063**: When `--remove` is present, the command must remove generated `.claude/agents/req.*` files and remove any empty directories under `.claude`, and generated `.opencode/agent/req.*` files.
- **REQ-064**: When `--remove` is present, the command must in no case modify or remove the file `.vscode/settings.json` present in the project root, even if it was previously created by useReq.
- **REQ-065**: When `--remove` is present, the command must remove files generated in `.claude/commands/req` and remove any empty directories under `.claude`.

### 3.9 Development & Testing
- **REQ-066**: Unit tests, if implemented, must be executed using exclusively the `temp/` folder (or `tests/temp/`) for any file or directory operation, and temporary folders must be deleted at the end of execution.
- **REQ-067**: The project must include a unit test suite (`tests/test_cli.py`) that verifies correct CLI script operation by performing the following operations: (1) create an empty test directory in `temp/project-test`, removing it if already present; (2) create subfolders `docs` and `tech`; (3) execute the script with parameters `--base temp/project-test`, `--doc temp/project-test/docs` and `--dir temp/project-test/tech`; (4) verify that the generated file and directory structure and relative contents comply with documented requirements. The test suite must exclusively use folders under `temp/` (or `tests/temp/`) for any file/directory creation, modification, or deletion and must not touch other repository paths. Furthermore, it must provide detailed output during execution, showing the list of all available tests, which test is currently running, what it will check (based on method description), and the test result (PASS or FAIL).
- **REQ-068**: Unit tests must not create, modify, or remove files or folders outside of the `temp/` (or `tests/temp/`) folder of the repository; every filesystem write operation must be confined to such temporary paths.

### 3.10 CI/CD Workflows
- **REQ-069**: The repository must include a GitHub Actions workflow under `.github/workflows/` that triggers on push of tags matching `v*`.
- **REQ-070**: The workflow must perform the build of Python package distributions (sdist and wheel) producing outputs under `dist/`.
- **REQ-071**: The workflow must create (or update) a GitHub Release for the tag and upload as asset all files produced in `dist/`.
- **REQ-072**: The workflow must generate artifact attestations (build provenance) for files in `dist/` using OIDC, so that attestations appear visible in the GitHub web interface for the release/asset.

