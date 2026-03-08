---
title: "useReq Requirements"
description: "Software Requirements Specification"
date: "2026-03-05"
version: 1.07
author: "Ogekuri"
scope:
  paths:
    - "**/*.py"
  excludes:
    - ".*/**"
visibility: "draft"
tags: ["markdown", "requirements", "srs"]
---

# useReq Requirements

## 1. Introduction
useReq is a text-based CLI that initializes and updates repository resources for multi-agent workflows and source-analysis commands.

### 1.1 Document Rules
- This document MUST be written and maintained in English.
- RFC 2119 keywords MUST be used exclusively: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.
- Each requirement MUST be atomic, single-sentence, and testable; target <= 35 words per requirement; split compound behavior into separate requirement IDs.
- Requirement bullets in requirements sections MUST start with a unique, stable requirement ID and MUST preserve all pre-existing ID values.
- Pre-existing requirement IDs MUST NOT be renumbered, renamed, or reused; newly created requirement IDs MUST be appended beyond the current highest ID.
- This document MUST NOT introduce requirements about source-code comment authoring style beyond already preserved requirements.

### 1.2 Project Scope
- Primary interface: CLI (`req`, `use-req`, `usereq`).
- Functional domains: project resource generation, configuration persistence, source analysis, token counting, compression, construct extraction, and Doxygen field extraction.
- Out-of-scope for this SRS rewrite: source-code modification.

### 1.3 Components and Dependencies
- Runtime: Python 3.11+.
- Core libraries: `argparse`, `pathlib`, `json`, `re`, `os`, `shutil`, `urllib`.
- Tokenization: `tiktoken` (`cl100k_base` default).
- Workflow automation: `.github/workflows/release-uvx.yml`.

### 1.4 Project Structure (evidence tree)
```text
.
├── docs/
│   ├── REQUIREMENTS.md
│   ├── REFERENCES.md
│   └── WORKFLOW.md
├── .github/workflows/
│   └── release-uvx.yml
├── src/usereq/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── source_analyzer.py
│   ├── generate_markdown.py
│   ├── compress.py
│   ├── compress_files.py
│   ├── find_constructs.py
│   ├── doxygen_parser.py
│   ├── token_counter.py
│   └── resources/
│       ├── common/
│       ├── docs/
│       ├── guidelines/
│       ├── prompts/
│       └── vscode/
└── tests/
    ├── fixtures/
    └── test_*.py
```

### 1.5 User Interface and Behavioral Overview
- Implemented UI is CLI-only; no GUI behavior is implemented.
- Output channels: stdout for normal payloads and stderr for warnings/errors/verbose status.
- Configuration persistence: `.req/config.json` and `.req/models.json`.

### 1.6 Performance Evidence
No explicit performance optimizations identified.

## 2. Project Requirements

### 2.1 Project Functions
- **SRS-001**: The implementation MUST preserve this behavior exactly: The command MUST initialize a project by creating or updating requirements documents, technical templates and root-based prompt resources.
- **SRS-002**: The implementation MUST preserve this behavior exactly: The command MUST accept exactly one of `--base` or `--here`; with `--base` it MUST use explicit `--guidelines-dir`, `--docs-dir`, `--tests-dir`, and `--src-dir` parameters, and with `--here` it MUST use only `guidelines-dir`, `docs-dir`, `tests-dir`, and `src-dir` values from `.req/config.json`, ignoring explicitly passed paths.
- **SRS-003**: The implementation MUST preserve this behavior exactly: The command MUST generate prompt resources for Codex, GitHub and Gemini by replacing path tokens with calculated relative values.
- **SRS-004**: The implementation MUST preserve this behavior exactly: The command MUST update local templates in `.req/docs` and integrate VS Code settings when available.
- **SRS-005**: The implementation MUST preserve this behavior exactly: The user interface MUST be a CLI text with optional error messages and progress logs.

### 2.2 Project Constraints
- **SRS-006**: The implementation MUST preserve this behavior exactly: The values of `--guidelines-dir`, `--docs-dir`, `--tests-dir`, and `--src-dir` MAY be absolute or relative paths when using `--base`. The routes MUST be normalized with respect to the root of the past project with `--base` verifying if present in the past routes with `--guidelines-dir`, `--docs-dir`, `--tests-dir`, and `--src-dir`. When using `--here`, explicit routes MUST be ignored and actual routes MUST be loaded by `.req/config.json`.
- **SRS-007**: The implementation MUST preserve this behavior exactly: The project requirements directory MUST coincide with the normalized `--docs-dir` path under the project root and MUST NOT be configured with a dedicated parameter.
- **SRS-008**: The implementation MUST preserve this behavior exactly: The route passed to `--guidelines-dir` and then normalized compared to `--base`, MUST exist as a real directory under the root of the project before copying the resources.
- **SRS-009**: The implementation MUST preserve this behavior exactly: The route passed to `--docs-dir` and then normalized compared to `--base`, MUST exist as a real directory under the root of the project before copying the resources.
- **SRS-010**: The implementation MUST preserve this behavior exactly: The route passed to `--tests-dir` and then normalized compared to `--base`, MUST exist as a real directory under the root of the project before copying the resources.
- **SRS-011**: The implementation MUST preserve this behavior exactly: The route passed to `--src-dir` and then normalized compared to `--base`, MUST exist as a real directory under the root of the project before copying the resources.
- **SRS-012**: The implementation MUST preserve this behavior exactly: Removal of pre-existing directories `.req` or `.req/docs` MUST only be allowed if such paths are under the root of the project.
- **SRS-013**: The implementation MUST preserve this behavior exactly: The command MUST fail if the specified project does not exist on the filesystem.

## 3. Requirements

### 3.1 Design and Implementation Constraints
- **SRS-014**: The implementation MUST preserve this behavior exactly: The calculation of the `%%GUIDELINES_FILES%%` token MUST be replaced with the list of directories found in the folder specified with `--guidelines-dir`. When expanded inline, the list MUST be formatted using inline code notation (backticks) for each element in the `dir1/`, `dir2/` form (with final slash).
- **SRS-015**: The implementation MUST preserve this behavior exactly: The source of the `Requirements_Template.md` template MUST be the `resources/docs` folder included in the package and the command MUST fail if the template is not available.
- **SRS-016**: The implementation MUST preserve this behavior exactly: Markdown prompt conversion to TOML MUST extract the `description` field from the front matter and save the prompt body in a multiline string.
- **SRS-017**: The implementation MUST preserve this behavior exactly: The combination of VS Code settings MUST support JSONC files by removing comments and MUST recurring objects with priority to the template values.
- **SRS-018**: The implementation MUST preserve this behavior exactly: `chat.promptFilesRecommendations` recommendations MUST be generated from the available Markdown prompts.
- **SRS-019**: The implementation MUST preserve this behavior exactly: The package entry point MUST expose `usereq.cli:main` via `use-req`, `req`, and `usereq`.
- **SRS-020**: The implementation MUST preserve this behavior exactly: Expected errors MUST be handled with no-zero exit code.
- **SRS-021**: The implementation MUST preserve this behavior exactly: The `load_cli_configs` function MUST be replaced with `load_centralized_models` which loads data from the `src/usereq/resources/common/models.json` file. When `legacy_mode` is active, it MUST load `models-legacy.json` if it exists, otherwise do fallback on `models.json`. The fallback MUST take place at full file level, not for individual entries. The return structure MUST remain compatible: a `cli_name -> config` dictionary where `config` contains the keys `prompts`, `usage_modes`, and optionally `agent_template`.
- **SRS-022**: The implementation MUST preserve this behavior exactly: The `generate_req_file_list` function MUST NOT be used by the prompt generation stream, and the `%%REQ_DIR%%` token MUST NOT be supported anymore.
- **SRS-023**: The implementation MUST preserve this behavior exactly: The `generate_dir_list` function MUST be renamed in `generate_guidelines_file_list`. The behavior MUST be aligned to `generate_req_file_list`: scan the specified directory (the one passed with `--guidelines-dir`) and return the list of files present in that directory (without recurring search of subfolders), ignoring the files starting with point (`.`). If the directory is empty or does not contain unhidden files, it MUST return the directory name itself as a fallback (preserving the original behavior only for the empty directory case).
- **SRS-024**: All declarations under `src/` MUST include Doxygen-style documentation blocks for modules, classes, structs, objects, functions, and methods.
- **SRS-025**: The documentation format MUST follow `src/usereq/resources/docs/Document_Source_Code_in_Doxygen_Style.md` with high semantic density for LLM-oriented source documentation.
- **SRS-026**: The implementation MUST preserve this behavior exactly: Documentation blocks MUST use standard language-specific docstring syntax (e.g., triple double quotes `"""` for Python) and include standard Doxygen tags (e.g., `@param`, `@return`, `@brief`) as specified in the guidelines.

### 3.2 CLI Interface and Lifecycle
- **SRS-027**: The no-argument invocation behavior MUST be treated as legacy intent; current true-state behavior prints parser help and returns success without an additional standalone version line (see `SRS-028`).
- **SRS-028**: The CLI with no arguments MUST print parser help and exit with code 0, and the current implementation does not append a standalone version line in this path.
- **SRS-029**: When `req` is invoked with `--ver` or `--version`, the command MUST print the version number, and a startup bright-green newer-version message MAY precede it when online release-check detects a newer release.
- **SRS-030**: The help usage string MUST include command `req`, version, and all available options including `--add-guidelines`, `--upgrade-guidelines`, `--files-tokens`, `--files-references`, `--files-compress`, `--files-find`, `--references`, `--compress`, `--find`, `--enable-line-numbers`, `--tokens`, `--preserve-models`, and `--provider` in `usage: req -c ...` format. The usage string MUST NOT include any removed legacy flags (`--enable-models`, `--enable-tools`, `--enable-claude`, `--enable-codex`, `--enable-gemini`, `--enable-github`, `--enable-kiro`, `--enable-opencode`, `--install-prompts`, `--install-agents`, `--install-skills`, `--prompts-use-agents`, `--legacy`). When `req` is invoked without parameters, the `--files-find` help text MUST include the dynamic list of available TAGs by language generated from `LANGUAGE_TAGS`. The `--find` help text MUST explicitly reference the list shown in `--files-find` to avoid duplication.
- **SRS-031**: The implementation MUST preserve this behavior exactly: All usage, help, information, verbose, and debug outputs emitted by the script MUST be in English.
- **SRS-032**: The implementation MUST preserve this behavior exactly: The command MUST require the `--docs-dir`, `--tests-dir`, and `--src-dir` parameters and verify that they indicate existing directories when `--base` is used; when `--here` is used, it MUST load these paths from `.req/config.json` and ignore any values passed with explicit parameters.
- **SRS-033**: The implementation MUST preserve this behavior exactly: The `--src-dir` parameter MUST be provided several times; each past directory MUST be normalized as other paths and MUST exist, otherwise the command MUST end with error.
- **SRS-034**: The CLI MUST accept the boolean flag `--preserve-models` and the repeatable `--provider SPEC` argument as the sole mechanism for provider enablement, artifact selection, and per-provider option configuration. The legacy global flags `--enable-claude`, `--enable-codex`, `--enable-gemini`, `--enable-github`, `--enable-kiro`, `--enable-opencode`, `--install-prompts`, `--install-agents`, `--install-skills`, `--enable-models`, `--enable-tools`, `--prompts-use-agents`, and `--legacy` MUST NOT be accepted by the argument parser. When `--preserve-models` is active in combination with `--update`, the CLI MUST preserve the existing `.req/models.json` file.
- **SRS-035**: During installation without `--update`, the CLI MUST require at least one `--provider` spec; otherwise it MUST print an English error and exit code 4. Each `--provider` spec implicitly enables the named provider and the listed artifact types.
- **SRS-036**: The installation summary table MUST include rows only for providers whose prompts were installed during the current invocation.
- **SRS-037**: The implementation MUST preserve this behavior exactly: The command MUST support the Boolean flags `--add-guidelines` and `--upgrade-guidelines` (default false). These flags activate the copy of the contents of the `src/usereq/resources/guidelines/` directory in the directory specified by `--guidelines-dir`. The copying operation MUST be performed before the call to `generate_guidelines_file_list`. If the source directory exists but does not contain unhidden files, the command MUST complete without error and consider the copy as a valid operation with zero copied files.
- **SRS-038**: The implementation MUST preserve this behavior exactly: When `--add-guidelines` is active, the command MUST copy all unhidden files present in `src/usereq/resources/guidelines/` in the target directory specified by `--guidelines-dir`, preserving existing files (without overwriting) if they have the same name.
- **SRS-039**: The implementation MUST preserve this behavior exactly: When `--upgrade-guidelines` is active, the command MUST copy all unhidden files present in `src/usereq/resources/guidelines/` in the target directory specified by `--guidelines-dir`, overwriting existing files if they have the same name.
- **SRS-040**: The implementation MUST preserve this behavior exactly: The `--add-guidelines` and `--upgrade-guidelines` flags are mutually exclusive: if both are provided at the same time, the command MUST end with error.
- **SRS-041**: The implementation MUST preserve this behavior exactly: The copy of technical templates MUST only occur when at least one of the two flags (`--add-guidelines` or `--upgrade-guidelines`) is active. If neither flag is provided, the copying operation MUST NOT be performed.
- **SRS-042**: `--uninstall` and `--upgrade` dispatch MUST execute before argparse parsing and before regular initialization flow; `--uninstall` has precedence when both flags are present in argv order handling.
- **SRS-043**: The `--upgrade` option MUST run `uv tool install usereq --force --from git+https://github.com/Ogekuri/useReq.git` and MUST fail on non-zero exit.
- **SRS-044**: The implementation MUST preserve this behavior exactly: The help string MUST include `--upgrade` as an option available.
- **SRS-045**: The `--uninstall` option MUST run `uv tool uninstall usereq` and MUST fail on non-zero exit.
- **SRS-046**: The implementation MUST preserve this behavior exactly: The help string MUST include `--uninstall` as an option available.
- **SRS-047**: The implementation MUST preserve this behavior exactly: After successful installation or update, the CLI MUST print a single English line reporting success and including the resolved project root path.
- **SRS-048**: The implementation MUST preserve this behavior exactly: Immediately after the successful message, the CLI MUST print a list of the discovered directories for replacing the `%%GUIDELINES_FILES%%` token, prefixed by `- `.
- **SRS-049**: Immediately after the file list, CLI MUST print a Unicode box-drawing installation summary table with bright-red border lines.
- **SRS-289**: The first installation summary table header cell MUST be `Provider` and MUST replace any previous `CLI` label.
- **SRS-290**: The `Prompts Installed` column MUST use a maximum display width of 50 characters and MUST wrap overflowing content onto subsequent lines.
- **SRS-291**: The `Modules Installed` column MUST render one line per active `--provider` artifact as `artifact` when no options are active, or `artifact:options` when options are active, where `artifact` is `prompts`, `agents`, or `skills`.
- **SRS-295**: In `Modules Installed` module-entry lines, `options` MUST preserve parsed token order from `--provider`; if no option is active, the line MUST be only `artifact` without `:options`.
- **SRS-296**: The `Modules Installed` column width MUST fit the longest rendered module-entry line in active rows and MUST NOT wrap module-entry lines.
- **SRS-050**: At program start, before any input-parameter parsing or validation, the command MUST use `https://api.github.com/repos/Ogekuri/useReq/releases/latest` as the release-check endpoint.
- **SRS-051**: The startup release-check MUST execute only when `$HOME/.github_api_idle-time.usereq` is missing or its stored `idle_until_timestamp` is expired; otherwise the command MUST skip remote version checks for that invocation.
- **SRS-052**: When a release-check is executed, it MUST use a hardcoded configurable timeout with default value `2` seconds; if remote version is greater than `__version__`, it MUST print a bright-green English message with installed and latest versions.
- **SRS-269**: If a release-check attempt fails, the command MUST print a bright-red English error message with an explicit failure reason (for example HTTP `403` rate-limit exceeded) and MUST NOT abort command execution.
- **SRS-270**: The idle-state file MUST be `$HOME/.github_api_idle-time.usereq` in JSON format and MUST contain keys `last_success_timestamp`, `last_success_human_readable_timestamp`, `idle_until_timestamp`, and `idle_until_human_readable_timestamp`.
- **SRS-271**: After each successful release-check HTTP/JSON flow, the command MUST write or update idle-state keys and MUST set `idle_until_timestamp` to `last_success_timestamp + 300`.
- **SRS-299**: Startup release-check gating MUST enforce fixed hardcoded `idle_delay_seconds=300` and MUST skip remote checks while `now < idle_until_timestamp`.
- **SRS-300**: On HTTP 429 with valid `Retry-After`, the command MUST set `idle_until_timestamp` to `max(current_idle_until_timestamp, now + max(300, retry_after_seconds))` and MUST persist all idle-state human-readable timestamps.
- **SRS-053**: The CLI MUST NOT create `requirements.md` under `--docs-dir`, including when `--docs-dir` is empty; the `Requirements_Template.md` template MUST be copied only into `.req/docs`.
- **SRS-054**: The repository MUST include `scripts/req.sh` as the development launcher wrapper for the CLI.
- **SRS-055**: The repository MUST keep `requirements.txt` as the canonical runtime/build dependency list containing all and only packages required to execute or build the application.
- **SRS-056**: `scripts/req.sh` MUST execute the CLI via `.venv/bin/python3` and MUST forward all user-provided CLI arguments unchanged.
- **SRS-264**: Dependency declarations in `pyproject.toml` or `setup.py` MUST match `requirements.txt` exactly and MUST include all and only packages required to execute or build the application.
- **SRS-057**: The current implementation MUST be treated as not providing a root-level `doxygen.sh` script for automated Doxygen generation.
- **SRS-058**: Any workflow that invokes `doxygen.sh` from repository root MUST fail fast because no such script path exists in the repository.
- **SRS-059**: Doxygen output generation to `doxygen/html`, `doxygen/pdf`, and `doxygen/markdown` MUST be treated as unsupported by committed automation scripts.
- **SRS-266**: The repository MUST include `scripts/ruff.sh`, which bootstraps `.venv` from `requirements.txt` when missing and then execs `.venv/bin/ruff` with passthrough arguments.
- **SRS-267**: The repository MUST include `scripts/pyright.sh`, which bootstraps `.venv` from `requirements.txt` when missing and then execs `.venv/bin/pyright` with passthrough arguments.
- **SRS-060**: The implementation MUST preserve this behavior exactly: The command MUST save the values of `--guidelines-dir`, `--docs-dir`, `--tests-dir`, and the list of `--src-dir` in `.req/config.json` as relative paths.
- **SRS-061**: The implementation MUST preserve this behavior exactly: The `.req/config.json` file MUST include `guidelines-dir`, `docs-dir`, `tests-dir`, and `src-dir` fields while preserving final slash; `src-dir` MUST be an array with a voice for each past directory.
- **SRS-062**: The implementation MUST preserve this behavior exactly: The command MUST support the `--update` option to rerun initialization using saved parameters.
- **SRS-063**: The implementation MUST preserve this behavior exactly: When `--update` is present, the command MUST verify the presence of `.req/config.json` and terminate with error if absent.
- **SRS-064**: With `--update`, the CLI MUST load paths, `--preserve-models` flag, and persisted `providers` array from `.req/config.json`, then apply only CLI-provided `--preserve-models` flag and `--provider` specs as overrides; if no provider spec is active after merging, it MUST raise a config-invalid error.
- **SRS-065**: The implementation MUST preserve this behavior exactly: The command MUST copy in `.req/docs` all files present in `src/usereq/resources/docs/`, dynamically generating the list of files to be copied, and MUST replace existing files.
- **SRS-066**: The command MUST copy the `.req/models.json` configuration file, replacing the pre-existing file if present, unless `--preserve-models` is active. When `--preserve-models` is NOT active: if the `legacy` option is NOT active for the provider being processed, it MUST copy `models.json` from package resources (`src/usereq/resources/common/models.json`); if `legacy` is active (via `--provider PROVIDER:...:legacy`) and `models-legacy.json` file is successfully loaded (i.e. when it exists), it MUST copy `models-legacy.json` from package resources (`src/usereq/resources/common/models-legacy.json`). This copy MUST take place after creating the `.req` directory and after saving `config.json`.
- **SRS-067**: The implementation MUST preserve this behavior exactly: If the VS Code template is available, create or update `.vscode/settings.json` by joining settings.
- **SRS-068**: The implementation MUST preserve this behavior exactly: Before modifying `.vscode/settings.json`, you MUST save the original state in backup under `.req/` (to restore with remove).
- **SRS-069**: The implementation MUST preserve this behavior exactly: The `.vscode/settings.json` update MUST only take place if there are semantic differences; if there are no, it MUST NOT rewrite or create backups.
- **SRS-070**: The implementation MUST preserve this behavior exactly: The `.req/settings.json.absent` file MUST never be generated.
- **SRS-071**: The implementation MUST preserve this behavior exactly: The command MUST NOT generate or replace the `%%REQ_DIR%%` and `%%REQ_PATH%%` tokens in the prompts.
- **SRS-072**: The implementation MUST preserve this behavior exactly: Prompt templates MUST be treated without parsing or rendering placeholders related to requirements (`%%REQ_*%%`).
- **SRS-073**: The implementation MUST preserve this behavior exactly: The script MUST relativize paths containing the path home project.
- **SRS-074**: The implementation MUST preserve this behavior exactly: The command MUST replace `%%GUIDELINES_FILES%%` with the list of subfolders in `--guidelines-dir` formatted as inline queues with final slash.
- **SRS-075**: The implementation MUST preserve this behavior exactly: If the `--guidelines-dir` directory is empty, use the directory itself for `%%GUIDELINES_FILES%%`.
- **SRS-076**: The implementation MUST preserve this behavior exactly: The directory list for `%%GUIDELINES_FILES%%` MUST use relative paths.
- **SRS-077**: The implementation MUST preserve this behavior exactly: The command MUST replace `%%GUIDELINES_PATH%%` with the past path with `--guidelines-dir`, which is normalized compared to the project root.
- **SRS-078**: The implementation MUST preserve this behavior exactly: The command MUST replace `%%DOC_PATH%%` with the past path with `--docs-dir`, which is normalized compared to the project root.
- **SRS-079**: The implementation MUST preserve this behavior exactly: The command MUST replace `%%TEST_PATH%%` with the past path with `--tests-dir`, normalized compared to the project root, formatted as inline code (backticks) and always adding a final slash even when the past value does not include it.
- **SRS-080**: The implementation MUST preserve this behavior exactly: The command MUST replace `%%SRC_PATHS%%` with the list of past directories with `--src-dir`, normalized compared to the project root, formatted as inline queues with final slash, and separated by `, `.
- **SRS-081**: The command MUST support per-provider `enable-models` and `enable-tools` options (via `--provider PROVIDER:ARTIFACTS:enable-models,enable-tools`) to include `model` and `tools` fields in generated files for that provider.
- **SRS-082**: When `enable-models` is active for a provider, include `model: <value>` if present in the provider's configuration from `models.json`.
- **SRS-083**: When `enable-tools` is active for a provider, include `tools` derived from `usage_modes` if present in the provider's configuration from `models.json`.
- **SRS-084**: The implementation MUST treat centralized model files as valid for `model`/`tools` extraction without requiring `settings.version` in `models.json` or `models-legacy.json`.
- **SRS-085**: The CLI MUST load prompt-generation configurations; with `--preserve-models` + `--update` and existing `.req/models.json`, it MUST load from `.req/models.json` and the per-provider `legacy` option MUST have no effect; otherwise it MUST load `src/usereq/resources/common/models.json` for `<cli>` `prompts` and `usage_modes`, and if the `legacy` option is active for a provider (via `--provider PROVIDER:...:legacy`) it MUST prefer `src/usereq/resources/common/models-legacy.json` when present (file-level fallback), else use `models.json`; `src/usereq/resources/<cli>/config.json` MUST NOT be used and MAY be removed; if `write.model` is defined, `readme` MUST use the same `model` and `mode` as `write`.
- **SRS-086**: The help string MUST include `--preserve-models` and `--provider` as available options; `--legacy` MUST NOT appear as a standalone flag.
- **SRS-275**: The CLI MUST accept a repeatable `--provider SPEC` argument as the sole mechanism for provider enablement, artifact selection, and per-provider option configuration. SPEC MUST follow the syntax `PROVIDER:ARTIFACTS[:OPTIONS]`; PROVIDER MUST be one of `codex`, `claude`, `gemini`, `github`, `kiro`, `opencode`; ARTIFACTS MUST be a comma-separated list from `{prompts, agents, skills}`; OPTIONS, when present, MUST be a comma-separated list from `{enable-models, enable-tools, prompts-use-agents, legacy}`.
- **SRS-276**: When one or more `--provider` specs are given, each spec MUST enable the named provider for the listed artifact types and activate listed options for that provider only; artifact types and options not listed in a spec MUST remain inactive for that provider.
- **SRS-277**: ~~REMOVED~~ (Legacy global flag merging with `--provider` specs is no longer supported; `--provider` is the sole configuration mechanism per SRS-275.)
- **SRS-278**: If a `--provider` SPEC contains an unknown PROVIDER name, unknown ARTIFACTS value, or unknown OPTIONS value, the CLI MUST print an English error message identifying the invalid token and exit with code 1.
- **SRS-279**: The CLI MUST persist all `--provider` specs as a JSON array under the `"providers"` key in `.req/config.json`; each element MUST be the raw SPEC string as provided on the command line.
- **SRS-280**: When `--update` loads `.req/config.json`, the CLI MUST restore persisted `"providers"` array entries; CLI-supplied `--provider` specs MUST replace (not merge with) persisted entries when at least one `--provider` flag is present on the command line.
- **SRS-281**: ~~REMOVED~~ (No global `--enable-models`/`--enable-tools` flags exist; `enable-models` and `enable-tools` are per-provider options in `--provider` specs only per SRS-275.)
- **SRS-282**: ~~REMOVED~~ (No global `--prompts-use-agents` flag exists; `prompts-use-agents` is a per-provider option in `--provider` specs only per SRS-275.)
- **SRS-283**: ~~REMOVED~~ (No global `--legacy` flag exists; `legacy` is a per-provider option in `--provider` specs only per SRS-275.)

### 3.3 Provider Resource Generation
- **SRS-087**: The resource generation described in the specific sections MUST only perform when the corresponding provider is targeted by a `--provider` spec.
- **SRS-089**: The CLI MUST create provider artifact directories only when the corresponding provider is targeted by a `--provider` spec with the corresponding artifact type: `.codex/prompts` when codex has `prompts`; `.codex/skills` when codex has `skills`; `.github/agents` when github has `agents`; `.github/prompts` when github has `prompts`; `.github/skills` when github has `skills`; `.gemini/commands` and `.gemini/commands/req` when gemini has `prompts`; `.gemini/skills` when gemini has `skills`; `.kiro/agents` when kiro has `agents`; `.kiro/prompts` when kiro has `prompts`; `.kiro/skills` when kiro has `skills`; `.claude/agents` when claude has `agents`; `.claude/commands` and `.claude/commands/req` when claude has `prompts`; `.claude/skills` when claude has `skills`; `.opencode/agent` when opencode has `agents`; `.opencode/command` when opencode has `prompts`; `.opencode/skill` when opencode has `skills`.
- **SRS-090**: For each Markdown prompt, the CLI MUST copy to `.codex/prompts/req-<name>.md` with token substitutions when codex is targeted with `prompts` artifact.
- **SRS-091**: For each Markdown prompt, the CLI MUST create `.github/prompts/req-<name>.prompt.md` when github is targeted with `prompts` artifact.
- **SRS-092**: The `.github/prompts` front matter MUST reference the agent (only `agent: req-<name>`) when `prompts-use-agents` option is active for the GitHub provider (via `--provider github:...:prompts-use-agents`); otherwise the full prompt body with metadata MUST be emitted.
- **SRS-093**: For each Markdown prompt, the CLI MUST generate `.github/agents/req-<name>.agent.md` with front matter including `name` when github is targeted with `agents` artifact.
- **SRS-094**: For each enabled provider with `skills` artifact active, the CLI MUST create a `skills` directory under the provider root (or `skill` for OpenCode) and, for each Markdown prompt, the subdirectory `<skills_root>/req-<prompt_name>`: `.codex/skills/req-<prompt_name>` for codex; `.github/skills/req-<prompt_name>` for github; `.gemini/skills/req-<prompt_name>` for gemini; `.kiro/skills/req-<prompt_name>` for kiro; `.claude/skills/req-<prompt_name>` for claude; `.opencode/skill/req-<prompt_name>` for opencode.
- **SRS-095**: For each skill subdirectory of every enabled provider, the CLI MUST generate `SKILL.md` with YAML front matter containing: `name: req-<prompt_name>`; `description` populated by `extract_skill_description(prompt_frontmatter)` (see SRS-113) escaped for YAML double-quoted strings; `model` and `tools` fields populated using the provider-specific configuration from `models.json` or `models-legacy.json` according to the per-provider `legacy` option, subject to per-provider `enable-models` and `enable-tools` options; the prompt body with token substitutions applied.
- **SRS-096**: The CLI MUST create `.gemini/commands` and `.gemini/commands/req` when gemini is targeted with `prompts` artifact.
- **SRS-097**: For each Markdown prompt, the CLI MUST generate a TOML file in `.gemini/commands/req` by converting Markdown and applying token substitutions when gemini is targeted with `prompts` artifact.
- **SRS-098**: The CLI MUST create `.kiro/agents` when kiro is targeted with `agents` artifact; MUST create `.kiro/prompts` when kiro is targeted with `prompts` artifact.
- **SRS-099**: For each Markdown prompt, the CLI MUST copy to `.kiro/prompts/req-<name>.md` preserving front matter when kiro is targeted with `prompts` artifact.
- **SRS-100**: For each Markdown prompt, the CLI MUST generate `.kiro/agents/req-<name>.json` using the agent template from `models.json` when kiro is targeted with `agents` artifact.
- **SRS-101**: The implementation MUST preserve this behavior exactly: In file Kiro JSON, popolare campi `name`, `description`, `prompt` (body escaped).
- **SRS-102**: The implementation MUST preserve this behavior exactly: In Kiro JSON file, popular `resources` field with relative file prompt and requirements.
- **SRS-103**: The implementation MUST preserve this behavior exactly: Popolare `tools` e `allowedTools` in `.kiro/agents` basandosi su `config.json` e mode prompt.
- **SRS-104**: The CLI MUST create `.opencode/agent` when opencode is targeted with `agents` artifact; MUST create `.opencode/command` when opencode is targeted with `prompts` artifact.
- **SRS-105**: For each Markdown prompt, the CLI MUST generate `.opencode/agent/req-<name>.md` with front matter and `mode: all` when opencode is targeted with `agents` artifact.
- **SRS-106**: For each Markdown prompt, the CLI MUST generate `.opencode/command/req-<name>.md`; when `prompts-use-agents` option is active for the OpenCode provider (via `--provider opencode:...:prompts-use-agents`), the front matter MUST reference `agent: req-<name>`.
- **SRS-107**: The CLI MUST create `.claude/agents` when claude is targeted with `agents` artifact.
- **SRS-108**: For each Markdown prompt, the CLI MUST generate `.claude/agents/req-<name>.md` with token substitutions when claude is targeted with `agents` artifact.
- **SRS-109**: In `.claude/agents`, the front matter MUST include `name` and `description`; `model`/`tools` MUST be included only if per-provider `enable-models`/`enable-tools` options are active and the value is configured. This applies when claude is targeted with `agents` artifact.
- **SRS-110**: The CLI MUST create `.claude/commands/req` when claude is targeted with `prompts` artifact.
- **SRS-111**: For each Markdown prompt, the CLI MUST generate a file in `.claude/commands/req` with front matter (agent ref if `prompts-use-agents` option is active for the Claude provider via `--provider claude:...:prompts-use-agents`, optional model/tools/allowed-tools) when claude is targeted with `prompts` artifact.

- **SRS-112**: Provider artifact-type activation MUST be specified exclusively via the ARTIFACTS component of `--provider` specs. During normal installation (non-upgrade/remove/help), at least one `--provider` spec MUST be present; if none is provided, the CLI MUST print an English error message and exit with exit code 4. The artifact types apply per provider independently: if a provider does not produce a given artifact type (e.g., Gemini produces only prompts, not agents), the corresponding artifact has no visible effect for that provider.
- **SRS-113**: The CLI MUST implement `extract_skill_description(frontmatter: str) -> str` that: (1) parses `frontmatter` as YAML (the prompt front matter without the leading/trailing `---` delimiters); (2) extracts the scalar field `usage` from the parsed YAML mapping; (3) normalizes `usage` by converting it to a string, splitting on all whitespace, and joining with a single ASCII space to form a single line; (4) returns the resulting string. If the YAML cannot be parsed, the parsed document is not a mapping, or the `usage` field is missing/empty, the function MUST return the empty string. The function MUST NOT derive the skill description from prompt-body sections (e.g., `## Purpose`, `## Scope`, `## Usage`).
- **SRS-114**: For each Markdown prompt, the CLI MUST generate `.claude/skills/req-<prompt_name>/SKILL.md` with YAML front matter (`name`, `description` from SRS-113, optional `model`/`tools`) and prompt body with token substitutions, using the `claude` configuration from `models.json`, when claude is targeted with `skills` artifact.
- **SRS-115**: For each Markdown prompt, the CLI MUST generate `.gemini/skills/req-<prompt_name>/SKILL.md` with YAML front matter (`name`, `description` from SRS-113, optional `model`/`tools`) and prompt body with token substitutions, using the `gemini` configuration from `models.json`, when gemini is targeted with `skills` artifact.
- **SRS-116**: For each Markdown prompt, the CLI MUST generate `.opencode/skill/req-<prompt_name>/SKILL.md` with YAML front matter (`name`, `description` from SRS-113, optional `model`/`tools`) and prompt body with token substitutions, using the `opencode` configuration from `models.json`, when opencode is targeted with `skills` artifact.
- **SRS-117**: For each Markdown prompt, the CLI MUST generate `.github/skills/req-<prompt_name>/SKILL.md` with YAML front matter (`name`, `description` from SRS-113, optional `model`/`tools`) and prompt body with token substitutions, using the `copilot` configuration from `models.json`, when github is targeted with `skills` artifact.
- **SRS-118**: For each Markdown prompt, the CLI MUST generate `.kiro/skills/req-<prompt_name>/SKILL.md` with YAML front matter (`name`, `description` from SRS-113, optional `model`/`tools`) and prompt body with token substitutions, using the `kiro` configuration from `models.json`, when kiro is targeted with `skills` artifact.
- **SRS-238**: For skill artifact generation, the CLI MUST process Markdown files only from `src/usereq/resources/prompts`, while prompt and agent artifacts MUST be generated only from `src/usereq/resources/prompts`.
- **SRS-263**: The CLI MUST treat files under `src/usereq/resources/prompts` as read-only package inputs and MUST NOT create, modify, overwrite, rename, or delete files in that directory.
- **SRS-265**: The CLI MUST treat files under `src/usereq/resources/docs` as read-only package templates and MUST NOT create, modify, overwrite, rename, or delete files in that directory.

### 3.4 Removal and Cleanup
- **SRS-119**: The implementation MUST preserve this behavior exactly: The command MUST support the `--remove` option to remove created resources.
- **SRS-120**: The implementation MUST preserve this behavior exactly: With `--remove`, mandatory `--base` or `--here` and refuse `--guidelines-dir`, `--update`.
- **SRS-121**: The implementation MUST preserve this behavior exactly: With `--remove`, verify `.req/config.json` existence.
- **SRS-122**: The implementation MUST preserve this behavior exactly: With `--remove`, do NOT restore `.vscode/settings.json` from backups.
- **SRS-123**: The implementation MUST preserve this behavior exactly: With `--remove`, remove created resources: `.codex`, `.github`, `.gemini`, `.kiro`, `.req`, etc.
- **SRS-124**: The implementation MUST preserve this behavior exactly: After removal, delete blank subfolders in folder providers.
- **SRS-125**: The implementation MUST preserve this behavior exactly: With `--remove`, remove generated files in `.claude` and `.opencode` and delete blank directories.
- **SRS-126**: The implementation MUST preserve this behavior exactly: With `--remove`, never change existing `.vscode/settings.json`.

### 3.5 CI/CD Release Workflow
- **SRS-127**: The implementation MUST preserve this behavior exactly: The repository MUST include GitHub Actions workflow that clicks on `v*` tag push.
- **SRS-128**: The implementation MUST preserve this behavior exactly: The workflow MUST build Python package (sdist and wheel) in `dist/`.
- **SRS-129**: The implementation MUST preserve this behavior exactly: The workflow MUST create GitHub Release for the tag and load assets from `dist/`.
- **SRS-130**: The implementation MUST preserve this behavior exactly: The workflow MUST generate artifact certifications for files in `dist/`.
- **SRS-268**: The `.github/workflows/release-uvx.yml` workflow MUST define `workflow_dispatch` under `on` in addition to tag-push triggers so releases MAY be launched manually without altering automatic tag-trigger behavior.

### 3.5.1 Package Distribution and Resource Inclusion
- **SRS-272**: The `[tool.setuptools.package-data]` section in `pyproject.toml` MUST enumerate glob patterns for every resource subdirectory present under `src/usereq/resources/`, including `resources/common/*.json`.
- **SRS-273**: The `[tool.setuptools.package-data]` section in `pyproject.toml` MUST NOT list glob patterns that reference non-existent directories under `src/usereq/resources/`.
- **SRS-274**: The built distribution (sdist and wheel) MUST include all files under `src/usereq/resources/` that are required for program operation, ensuring congruent behavior between local development execution, `uv`-installed package execution, and `uvx` live execution.

### 3.6 Source Analysis Core
- **SRS-131**: The implementation MUST preserve this behavior exactly: The `usereq.source_analyzer` module MUST support 20 programming languages: C (`.c`), C++ (`.cpp`), C# (`.cs`), Elixir (`.ex`), Go (`.go`), Haskell (`.hs`), Java (`.java`), JavaScript (`.js`, `.mjs`), Kotlin (`.kt`), Lua (`.lua`), Perl (`.pl`), PHP (`.php`), Python (`.py`), Ruby (`.rb`), Rust (`.rs`), Scala (`.scala`), Shell (`.sh`), Swift (`.swift`), TypeScript (`.ts`), and Zig (`.zig`).
- **SRS-132**: The implementation MUST preserve this behavior exactly: For each language, the module MUST recognize and classify the following types of elements:
- **SRS-133**: The implementation MUST preserve this behavior exactly: Each recognized element MUST contain: element type, initial row, final row, source code extract (maximum 5 rows), optional name, optional signature, optional visibility, optional parent name, optional inheritance, hierarchical depth.
- **SRS-134**: The implementation MUST preserve this behavior exactly: The language parameter MUST be normalized: it MUST accept uppercases, lowercases, mixed houses, starting point and spaces.
- **SRS-135**: The implementation MUST preserve this behavior exactly: For each language, the module MUST recognize single-line comments with the appropriate delimiter and multi-rigue comments with the specific opening and closing delimiters of the language.
- **SRS-136**: The implementation MUST preserve this behavior exactly: The module MUST support language aliases (e.g., `js` for `javascript`, `ts` for `typescript`, `rs` for `rust`, `py` for `python`, `rb` for `ruby`, `hs` for `haskell`, `cs` for `csharp`, `kt` for `kotlin`, `ex` for `elixir`, `sh`/`bash`/`zsh` for `shell`, `cc`/`cxx` for `cpp`, `h` for `c`, `hpp` for `cpp`, `pl` for `perl`, `exs` for `elixir`) and aliases MUST produce identical results to the canonical language.
- **SRS-137**: The implementation MUST preserve this behavior exactly: The module MUST manage the hierarchy of elements: the container elements (class, struct, module, etc.) MUST remain at depth 0, the contained elements MUST have depth 1 and the set `parent_name` field.
- **SRS-138**: The implementation MUST preserve this behavior exactly: The `enrich()` method MUST enrich the elements with clean signatures, hierarchy, visibility, inheritance, internal comments and exit points.
- **SRS-139**: The implementation MUST preserve this behavior exactly: The `format_markdown()` function MUST produce a compact Markdown output optimized for the LLM context, structured with: header file (name, language, lines), table `Definitions` (symbol, type, line, signature), table `Symbol Index` ( navigable index), and optional sections for comments and comments.
- **SRS-140**: The implementation MUST preserve this behavior exactly: The module MUST correctly manage: empty files (reestablish empty list), files with only spaces (reestablish empty list), unsupported languages (lead `ValueError`), files not found (lead `FileNotFoundError`).
- **SRS-141**: The implementation MUST preserve this behavior exactly: The search for the end of the blocks MUST use specific strategies for the language family: indentation for Python and Haskell, clumsy brackets for C/C++/Rust/JavaScript/TypeScript/Java/Go/C#/Swift/Kotlin/PHP/Scala/Zig, keyword `end` for Ruby/Elixir/Lua.
- **SRS-142**: The implementation MUST preserve this behavior exactly: Comments within literal strings MUST NOT be recognized as comments.
- **SRS-143**: The implementation MUST preserve this behavior exactly: The `usereq.source_analyzer` module MUST extract the documentation comment blocks associated with each construct and store them in `SourceElement` for the Doxygen parsing downstream.

### 3.7 Token Counting
- **SRS-144**: The implementation MUST preserve this behavior exactly: The `usereq.token_counter` module MUST count tokens using the `tiktoken` encoding with `cl100k_base` encoding as default.
- **SRS-145**: The implementation MUST preserve this behavior exactly: The `TokenCounter` class MUST expose `count_tokens(content)` and `count_chars(content)` methods.
- **SRS-146**: The implementation MUST preserve this behavior exactly: The `count_file_metrics(content, encoding_name)` function MUST return a dictionary with `tokens` and `chars` keys.
- **SRS-147**: The implementation MUST preserve this behavior exactly: The `count_files_metrics(file_paths, encoding_name)` function MUST return a list of dictionaries with `file`, `tokens`, `chars` keys and optionally `error` in case of read error.
- **SRS-148**: The implementation MUST preserve this behavior exactly: The `format_pack_summary(results)` function MUST format a summary with details for files and totals, using the file name, token count, character count, and a Pack Summary section with totals.
- **SRS-149**: The implementation MUST preserve this behavior exactly: In case of token count error (except in encoding), the count MUST return 0 without propagating the exception.

### 3.8 Reference Markdown Generation
- **SRS-150**: The implementation MUST preserve this behavior exactly: The `usereq.generate_markdown` module MUST analyze source files using `usereq.source_analyzer` and produce a chained markdown output.
- **SRS-151**: The implementation MUST preserve this behavior exactly: The module MUST determine the language from the file extension using the supported file extension-language map.
- **SRS-152**: The implementation MUST preserve this behavior exactly: The files not found MUST be ignored; the SKIP message on stderr MUST be printed only when the verbose mode is active.
- **SRS-153**: The implementation MUST preserve this behavior exactly: Unsupported file extensions MUST be ignored; the SKIP message on stderr MUST only be printed when the verbose mode is active.
- **SRS-154**: The implementation MUST preserve this behavior exactly: If no valid file is processed, a `ValueError` exception MUST be launched.
- **SRS-155**: The implementation MUST preserve this behavior exactly: Markdown analysis results MUST be chained with `\n\n---\n\n` separator.
- **SRS-156**: The implementation MUST preserve this behavior exactly: The processing status (OK/FAIL and counting) MUST be printed on stderr only when the verbose mode is active. The markdown output for each construct MUST include only the reference of the construct and the extracted Doxygen fields (if present), formatted as the Markdown bet list; it MUST NOT include legacy lines of comments/exit points in the `L<n>>` format.

### 3.9 Source Compression
- **SRS-157**: The implementation MUST preserve this behavior exactly: The `usereq.compress` module MUST compress the source code by removing comments (inline, single-line, multi-rigue), empty lines, final spaces and redundant spacing, preserving the semantic of the language.
- **SRS-158**: The implementation MUST preserve this behavior exactly: For languages with significant indentation (Python, Haskell, Elixir), indentation MUST be preserved during compression.
- **SRS-159**: The implementation MUST preserve this behavior exactly: The output format MUST support prefixes with row number in the `<n>: <testo>` format, enabled by default and disabled with the `include_line_numbers=False` option.
- **SRS-160**: The implementation MUST preserve this behavior exactly: Shebang lines (`#!`) at the first row of the file MUST be preserved.
- **SRS-161**: The implementation MUST preserve this behavior exactly: Comments within literal strings MUST NOT be removed.
- **SRS-162**: The implementation MUST preserve this behavior exactly: The module MUST automatically determine the language from the file extension, with the possibility of manual override.
- **SRS-163**: The `usereq.compress_files` module MUST emit, per file, header `@@@ <path> | <language>`, metadata line `> Lines: <line_start>-<line_end>`, and compressed content inside a fenced Markdown code block.
- **SRS-164**: The implementation MUST preserve this behavior exactly: The files not found MUST be ignored; the SKIP message on stderr MUST be printed only when the verbose mode is active.
- **SRS-165**: The implementation MUST preserve this behavior exactly: Unsupported file extensions MUST be ignored; the SKIP message on stderr MUST only be printed when the verbose mode is active.
- **SRS-166**: The implementation MUST preserve this behavior exactly: If no valid file is processed, a `ValueError` exception MUST be launched.
- **SRS-167**: The implementation MUST preserve this behavior exactly: The processing status (OK/FAIL and counting) MUST be printed on stderr only when the verbose mode is active.
- **SRS-168**: The implementation MUST preserve this behavior exactly: Multi-line comment blocks (including Python docstrings with `"""` and `'''`) MUST be removed during compression.

### 3.10 Construct Extraction and Command Operations
- **SRS-169**: The implementation MUST preserve this behavior exactly: The `--files-tokens` command MUST accept a list of files as a parameter and calculate the token count and characters for each file, printing a summary with details for files and totals on stdout.
- **SRS-170**: The implementation MUST preserve this behavior exactly: The `--files-tokens` command MUST operate independently of `--base`, `--here` and useReq configuration. `--base` and `--here` parameters MUST NOT be required.
- **SRS-171**: The implementation MUST preserve this behavior exactly: The `--files-tokens` command MUST ignore the files not found with a warning on stderr and end with error if no valid file is provided.
- **SRS-172**: The implementation MUST preserve this behavior exactly: The `--files-references` command MUST accept an arbitrary list of files and created structured reference markdown for LLM context on stdout; for each construct it MUST issue the construct and extracted Doxygen fields (when present) in the format defined by SRS-219 and SRS-221. The `> Path: \` line file...\` MUST be related to the project home (current working directory) and MUST NOT be absolute.
- **SRS-173**: The implementation MUST preserve this behavior exactly: The `--files-references` command MUST operate independently of `--base`, `--here` and useReq configuration. `--base` and `--here` parameters MUST NOT be required.
- **SRS-174**: The implementation MUST preserve this behavior exactly: The `--files-compress` command MUST accept an arbitrary list of files and generate a compressed output for the LLM context, printing it on stdout.
- **SRS-175**: The implementation MUST preserve this behavior exactly: The `--files-compress` command MUST operate independently of `--base`, `--here` and useReq configuration. `--base` and `--here` parameters MUST NOT be required.
- **SRS-176**: The `--references` command MUST operate in `--here` mode only; if neither `--here` nor `--base` is provided it MUST imply `--here`, and if `--base` is provided it MUST fail.
- **SRS-177**: The `--references` command MUST select candidate files from `git ls-files` output under `src-dir` values loaded from `.req/config.json`, then keep only supported extensions from SRS-131.
- **SRS-178**: The `--compress` command MUST operate in `--here` mode only; if neither `--here` nor `--base` is provided it MUST imply `--here`, and if `--base` is provided it MUST fail.
- **SRS-179**: The `--compress` command MUST select candidate files from `git ls-files` output under `src-dir` values loaded from `.req/config.json`, then keep only supported extensions from SRS-131.
- **SRS-180**: For `--references`, `--compress`, `--find`, and `--static-check`, `EXCLUDED_DIRS` MUST contain only directory names that are not already excluded by `.gitignore`.
- **SRS-181**: Source-file selection for `--references` and `--compress` MUST be derived from `git ls-files` relative paths and MUST NOT rely on recursive filesystem walking.
- **SRS-182**: When `--update` is used with `--references` or `--compress`, `src-dir` values MUST be loaded from `.req/config.json` before applying `git ls-files` filtering.
- **SRS-183**: The `--references` command MUST prepend `# Files Structure` using only files selected after `git ls-files`, `src-dir`, supported-extension filtering (SRS-131), and `EXCLUDED_DIRS` filtering (SRS-180).
- **SRS-184**: The `--tokens` command MUST run in implicit `--here`, MUST reject `--base`, MUST load `docs-dir` from `.req/config.json` ignoring explicit `--docs-dir`, and MUST invoke `--files-tokens` only for `REQUIREMENTS.md`, `WORKFLOW.md`, and `REFERENCES.md`.
- **SRS-185**: The implementation MUST preserve this behavior exactly: `--files-compress` and `--compress` commands MUST accept the optional `--enable-line-numbers` flag; when the flag is absent the compressed output MUST NOT include `<numero>:` prefixes, when the flag is present the prefixes MUST be included.
- **SRS-186**: The implementation MUST preserve this behavior exactly: The `usereq.find_constructs` module MUST extract specific constructs from source files by filtering by element type (`TAG`) and element name by regex pattern (`REGEXP`).
- **SRS-187**: The implementation MUST preserve this behavior exactly: The `<TAG>` parameter MUST accept one or more element type identifiers separated by the `|` character.
- **SRS-188**: The implementation MUST preserve this behavior exactly: The `<REGEXP>` parameter MUST be a regular Python expression (`re` module) applied to the name of the extracted construct. The match MUST be case-sensitive and tested with `re.search()`.
- **SRS-189**: The implementation MUST preserve this behavior exactly: If a source file does not support any of the tags specified in `<TAG>` for its language, the file MUST be jumped; the SKIP message on stderr MUST be printed only when the verbose mode is active.
- **SRS-190**: The implementation MUST preserve this behavior exactly: The `find_constructs_in_files()` function MUST analyze each file with `SourceAnalyzer.analyze()` and `SourceAnalyzer.enrich()`, filter elements by tag and regex, use construct-associated comments processed in `SourceAnalyzer.enrich()` to populate `doxygen_fields`, read the full content of each filtered construct from source files using `line_start` and `line_end`, normalize code blocks by removing inline/single-line/multi-line comments without altering string literals or construct semantics, and format output in markdown.
- **SRS-191**: The implementation MUST preserve this behavior exactly: Markdown output format MUST include, for each file, a `@@@ <path> | <language>` header, followed by found constructs with type, name, signature (if present), start line, end line, extracted Doxygen fields as a Markdown bullet list (if present), and the construct code block extracted from `line_start` and `line_end` indexes.
- **SRS-192**: The implementation MUST preserve this behavior exactly: The code extracted for each construct MUST include prefixes with row number in the `<n>: <testo>` format by default. Prefixes MUST be disabled with the `include_line_numbers=False` option.
- **SRS-193**: The implementation MUST preserve this behavior exactly: The processing status (OK/SKIP/FAIL and counting) MUST be printed on stderr only when the verbose mode is active.
- **SRS-194**: The implementation MUST preserve this behavior exactly: If no valid file is processed or no construct is found, a `ValueError` exception MUST be launched.
- **SRS-195**: The implementation MUST preserve this behavior exactly: The files not found MUST be ignored; the SKIP message on stderr MUST be printed only when the verbose mode is active.
- **SRS-196**: The implementation MUST preserve this behavior exactly: Unsupported file extensions MUST be ignored; the SKIP message on stderr MUST only be printed when the verbose mode is active.
- **SRS-197**: The implementation MUST preserve this behavior exactly: The `usereq.find_constructs` module MUST provide a `format_available_tags()` function that generates the formatted list of TAGs available for language, dynamically iterating on the `LANGUAGE_TAGS` map. The output format MUST be multi-rigue with each language on a separate row in the format: `- <Linguaggio>: TAG1, TAG2, TAG3, ...` (language with first capital letter, TAG separated by comma+space, sorted alphabetically).
- **SRS-198**: The implementation MUST preserve this behavior exactly: The `--files-find` command MUST accept two mandatory parameters `<TAG>` and `<REGEXP>`, followed by an arbitrary list of files: `--files-find <TAG> <REGEXP> <FILE1> <FILE2> ...`. If `<TAG>` does not contain valid identifiers or is not supported by any processed language, the command MUST print an error message that includes the complete list of TAGs available by language, dynamically generated using the `LANGUAGE_TAGS` defined in `find_constructs.py`.
- **SRS-199**: Invalid regex input for construct extraction MUST be treated as a non-match condition, resulting in the generic 'no constructs found' error rather than a regex syntax exception.
- **SRS-200**: The implementation MUST preserve this behavior exactly: The `--files-find` command MUST operate independently of `--base`, `--here` and useReq configuration. `--base` and `--here` parameters MUST NOT be required.
- **SRS-201**: The implementation MUST preserve this behavior exactly: The `--files-find` command MUST extract and print on stdout all constructs that: belong to the types specified in `<TAG>` (separated by `|`), have the name that runs the match with `<REGEXP>`, are present in the specified files.
- **SRS-202**: The implementation MUST preserve this behavior exactly: The `--files-find` command MUST accept the optional `--enable-line-numbers` flag; when the flag is absent the output MUST NOT include `<numero>:` prefixes, when the flag is present the prefixes MUST be included.
- **SRS-203**: The `--find` command MUST operate in `--here` mode only; if neither `--here` nor `--base` is provided it MUST imply `--here`, and if `--base` is provided it MUST fail.
- **SRS-204**: The implementation MUST preserve this behavior exactly: The `--find` command MUST accept two mandatory parameters `<TAG>` and `<REGEXP>`: `--find <TAG> <REGEXP>`. If `<TAG>` does not contain valid identifiers or is not supported by any processed language, the command MUST print an error message that includes the complete list of TAGs available by language, dynamically generated using the `LANGUAGE_TAGS` defined in `find_constructs.py`.
- **SRS-205**: The `--find` command MUST select candidate files from `git ls-files` output under `src-dir` values loaded from `.req/config.json`, then keep only supported extensions from SRS-131.
- **SRS-206**: During `--find` candidate-file selection, paths containing any `EXCLUDED_DIRS` segment from SRS-180 MUST be excluded.
- **SRS-207**: Source-file selection for `--find` MUST be derived from `git ls-files` relative paths and MUST NOT rely on recursive filesystem walking.
- **SRS-208**: When `--update` is used with `--find`, `src-dir` values MUST be loaded from `.req/config.json` before applying `git ls-files` filtering.
- **SRS-209**: The implementation MUST preserve this behavior exactly: The `--find` command MUST accept the optional `--enable-line-numbers` flag; when the flag is absent the output MUST NOT include `<numero>:` prefixes, when the flag is present the prefixes MUST be included.
- **SRS-210**: The implementation MUST preserve this behavior exactly: The `--files-references`, `--references`, `--files-compress`, `--compress`, `--files-find` and `--find` controls MUST print state outputs (OK/SKIP/FAIL and re-epilogue) only when the `--verbose` flag is present; without `--verbose` MUST NOT be such outputs.
- **SRS-211**: The `--files-compress` and `--compress` commands MUST print, per processed file, header `@@@ <path> | <language>`, metadata line `> Lines: <line_start>-<line_end>`, and fenced code block; paths MUST be project-relative only.

### 3.11 Doxygen Parsing and Field Emission
- **SRS-212**: The implementation MUST preserve this behavior exactly: The `usereq.doxygen_parser` module MUST extract Doxygen fields from documentation comments following the standard Doxygen syntax for all supported languages.
- **SRS-213**: The implementation MUST preserve this behavior exactly: The parser MUST recognize these Doxygen tags: @brief, @details, @param, @param[in], @param[out], @param[in,out], @return, @retval, @exception, @throws, @warning, @deprecated, @note, @see, @sa, @satisfies, @pre, @post.
- **SRS-214**: The implementation MUST preserve this behavior exactly: The `parse_doxygen_comment(comment_text: str) -> Dict[str, List[str]]` function MUST return a dictionary where keys are the normalized Doxygen tags and values are lists of extracted content.
- **SRS-215**: The implementation MUST preserve this behavior exactly: The parser MUST support both `@tag` and `\tag` syntax for standard Doxygen compatibility.
- **SRS-216**: The implementation MUST preserve this behavior exactly: For `@param` tags, the parser MUST distinguish `@param`, `@param[in]`, `@param[out]`, and `@param[in,out]` while preserving directionality.
- **SRS-217**: The implementation MUST preserve this behavior exactly: The content of each tag MUST extend to the next Doxygen tag or at the end of the comment, with normalization of the spaces.
- **SRS-218**: The implementation MUST preserve this behavior exactly: The `usereq.source_analyzer` module MUST invoke `parse_doxygen_comment()` on constructive comments and popularize a new `doxygen_fields` field in `SourceElement`.
- **SRS-219**: MUST format Doxygen fields for `--files-references` and `--references` as Markdown bullets using original Doxygen tags (`@tag`) exactly, without human-readable label conversion and without `:` suffix.
- **SRS-220**: The `--files-find` and `--find` outputs MUST emit metadata lines as `> Signature: ...` (when available) and `> Lines: ...`; extracted Doxygen bullets MUST appear after `> Lines: ...` and before code blocks, preserving original `@tag` names without `:` suffix.
- **SRS-221**: The implementation MUST preserve this behavior exactly: Doxygen fields MUST be emitted in fixed order: @brief, @details, @param, @param[in], @param[out], @param[in,out], @return, @retval, @exception, @throws, @warning, @deprecated, @note, @see, @sa, @satisfies, @pre, @post, omitting missing tags.

## 4. Test Requirements

### 4.1 Test and Verification Requirements
- **SRS-222**: The implementation MUST preserve this behavior exactly: Unit test MUST only use the `temp/` folder (or `temp/tests/`).
- **SRS-223**: The implementation MUST preserve this behavior exactly: The project MUST include `tests/test_cli.py` suites that check CLI operations in temporary folder.
- **SRS-224**: The implementation MUST preserve this behavior exactly: Test unit MUST NOT create/modify files outside `temp/`.
- **SRS-225**: The implementation MUST preserve this behavior exactly: The project MUST include `tests/test_analyzer_core.py`, `tests/test_analyzer_comments.py`, `tests/test_analyzer_format.py`, `tests/test_analyzer_errors.py`, `tests/test_analyzer_helpers.py`, and `tests/test_analyzer_cli.py` testing modules.
- **SRS-226**: The implementation MUST preserve this behavior exactly: `source_analyzer` tests requiring language fixtures MUST use files in `tests/fixtures/` named `fixture_<language>.<extension>`.
- **SRS-227**: The implementation MUST preserve this behavior exactly: `source_analyzer` module tests that create temporary files MUST set the output directory under `temp/` of the repository.
- **SRS-228**: The implementation MUST preserve this behavior exactly: The project MUST include the `tests/test_find_constructs_comprehensive.py` test module that tests the COMPLETA extraction (without truncating or limited snippet) of specific constructs through `find_constructs_in_files()` for all language-construct combinations defined in SRS-187 and for the quantitative/heterogeneity constraints defined in SRS-230, using the fixtures present in `tests/fixtures/`, validating that the TAG at least 5 distinct drawings with regex pattern anchored on different construct names.
- **SRS-229**: The implementation MUST preserve this behavior exactly: Test fixtures for all 20 languages MUST be present in `tests/fixtures/` using the `fixture_<language>.<extension>` format.
- **SRS-230**: The implementation MUST preserve this behavior exactly: Each fixture in `tests/fixtures/fixture_<language>.<extension>` MUST include at least 5 distinct constructs for each required TAG of the language defined in SRS-187; constructs MUST include heterogeneous comments with at least one occurrence in `pre-line`, `inline`, and `multi-line` modes where the language syntax allows it, while remaining valid and parsable for the target language.
- **SRS-231**: Every file in `tests/fixtures/` MUST include one file-level Doxygen block with `@file`, `@brief`, and `@details`, and MUST retain at least five construct-level blocks with `@brief`, `@details`, `@param`, and `@return`.
- **SRS-232**: The implementation MUST preserve this behavior exactly: The project MUST includes `tests/test_doxygen_parser.py` with at least 180 units tests, derived from at least 10 cases for each of the 18 Doxygen tags supported in SRS-213; each test MUST use a generated synthetic comment and deterministic expected extraction output.
- **SRS-233**: The implementation MUST preserve this behavior exactly: The project MUST include `tests/fixtures/`-based Doxygen tests that, for each fixture file, extract all the constructions present compatible with SRS-187, validate the Doxygen fields expected for each construct, and verify that the comment association→built is correct for both pre-built comments and post-built comments when allowed by the language syntax.
- **SRS-234**: MUST verify in `tests/test_files_commands.py` that `--files-references` outputs Doxygen field bullets with original tags from SRS-213 (`@brief` ... `@post`) and never emits converted labels like `Brief:`.
- **SRS-235**: MUST verify in `tests/test_files_commands.py` that `--references` outputs Doxygen field bullets with original tags from SRS-213 (`@brief` ... `@post`) and never emits converted labels like `Brief:`.
- **SRS-236**: MUST verify command-level `--files-find` outputs Doxygen field bullets using original tags from SRS-213 (`@brief` ... `@post`) with SRS-220 placement and SRS-221 order, never converted labels.
- **SRS-237**: MUST verify command-level `--find` outputs Doxygen field bullets using original tags from SRS-213 (`@brief` ... `@post`) with SRS-220 placement, SRS-221 order, and no converted labels.
- **SRS-284**: The project MUST include unit tests in `tests/test_cli.py` verifying that `--provider PROVIDER:ARTIFACTS[:OPTIONS]` parsing accepts valid specs and rejects unknown providers, unknown artifacts, and unknown options with exit code 1.
- **SRS-285**: The project MUST include unit tests in `tests/test_cli.py` verifying that multiple `--provider` specs correctly enable distinct per-provider artifact types and per-provider options independently.
- **SRS-286**: The project MUST include unit tests in `tests/test_cli.py` verifying that `--provider` specs are persisted to and restored from `.req/config.json` under the `"providers"` key during `--update` round-trips.
- **SRS-287**: The project MUST include unit tests in `tests/test_cli.py` verifying that per-provider `enable-models`, `enable-tools`, `prompts-use-agents`, and `legacy` options from `--provider` specs are applied independently to each targeted provider.
- **SRS-288**: The `.req/config.json` file MUST persist only the `"providers"` JSON array (raw SPEC strings) and the `"preserve-models"` boolean for update round-trips; the 13 legacy boolean keys (`enable-models`, `enable-tools`, `enable-claude`, `enable-codex`, `enable-gemini`, `enable-github`, `enable-kiro`, `enable-opencode`, `install-prompts`, `install-agents`, `install-skills`, `prompts-use-agents`, `legacy`) MUST NOT be written to or required from `config.json`.
- **SRS-292**: The project MUST include unit tests in `tests/test_cli.py` verifying that the installation summary table uses `Provider` as the first header and Unicode box-drawing borders with bright-red line color.
- **SRS-293**: The project MUST include unit tests in `tests/test_cli.py` verifying that `Prompts Installed` content wraps with a maximum display width of 50 characters.
- **SRS-294**: The project MUST include unit tests in `tests/test_cli.py` verifying that `Modules Installed` renders one module-entry line per active provider artifact from `--provider` using `artifact` without options or `artifact:options` when options exist.
- **SRS-297**: The project MUST include unit tests in `tests/test_cli.py` verifying that `Modules Installed` preserves parsed option token order in each `artifact:options` line and emits only `artifact` when options are absent.
- **SRS-298**: The project MUST include unit tests in `tests/test_cli.py` verifying that `Modules Installed` does not wrap module-entry lines and widths include the longest rendered module-entry line.

## 5. Static Code Analysis Requirements

### 5.1 Static Analysis Feature Overview
- **SRS-239**: The CLI MUST support a new flag `--test-static-check` that accepts a subcommand name (`dummy`, `pylance`, `ruff`, `command`) and dispatches static-code-analysis logic accordingly. The flag MUST operate as a standalone command (no `--base`/`--here` required).
- **SRS-240**: The `--test-static-check` flag MUST accept an optional list of `[FILES]...` arguments following the subcommand name and optional subcommand-specific options. Each element of `[FILES]` MAY be: a path to a directory (direct children only), a glob pattern (e.g., `path/**/*.py`) with full `**` recursive expansion support, or a specific file path. No custom `--recursive` flag is defined; recursive traversal is expressed via `**` glob syntax.
- **SRS-241**: The implementation MUST provide a `StaticCheckBase` (Dummy) class in `src/usereq/static_check.py` that iterates over resolved input files, emits `# Static-Check(Dummy): <filename> [OPTIONS]`, emits `Result: OK`, and appends exactly one trailing blank line after each per-file markdown block.
- **SRS-242**: The implementation MUST provide a `StaticCheckPylance` class derived from `StaticCheckBase` that invokes `pyright` per resolved file, emits `# Static-Check(Pylance): <filename> [OPTIONS]`, emits `Result: OK` or `Result: FAIL\nEvidence:\n<output>`, and appends exactly one trailing blank line after each per-file markdown block.
- **SRS-243**: The implementation MUST provide a `StaticCheckRuff` class derived from `StaticCheckBase` that invokes `ruff check` per resolved file, emits `# Static-Check(Ruff): <filename> [OPTIONS]`, emits `Result: OK` or `Result: FAIL\nEvidence:\n<output>`, and appends exactly one trailing blank line after each per-file markdown block.
- **SRS-244**: The implementation MUST provide a `StaticCheckCommand` class derived from `StaticCheckBase` that requires `command <cmd>`, validates `cmd` on PATH (`shutil.which`), emits `# Static-Check(Command[<cmd>]): <filename> [OPTIONS]`, emits pass/fail output, and appends exactly one trailing blank line after each per-file markdown block.
- **SRS-245**: All static-check classes MUST resolve `[FILES]` input using glob expansion (with `**` recursive support always enabled) for patterns, and direct-children-only traversal for bare directory entries, collecting only regular files. If the resolved file list is empty, the command MUST print a warning to stderr and exit with code 0.
- **SRS-246**: The `--test-static-check` dispatcher MUST be integrated into `cli.py` as a standalone command dispatched before the standard init flow.

### 5.2 Static Analysis Test Requirements
- **SRS-247**: The project MUST include `tests/test_static_check.py` with unit tests for: `StaticCheckBase` (Dummy) output format with one trailing blank separator line per file block; `StaticCheckPylance` OK/FAIL branches with mocked subprocess; `StaticCheckRuff` OK/FAIL branches with mocked subprocess; `StaticCheckCommand` availability check and OK/FAIL branches with mocked subprocess; glob pattern resolution including `**` recursive expansion; direct-children-only directory resolution; empty-file-list warning behavior.

### 5.3 Static Analysis Configuration Requirements
- **SRS-248**: The CLI MUST support repeatable `--enable-static-check SPEC` (`LANG=MODULE[,CMD[,PARAM...]]`), and each SPEC occurrence MUST append one static-check entry under the canonical language key in `.req/config.json` key `"static-check"`.
- **SRS-249**: `--enable-static-check` MUST accept language names case-insensitively; the 20 valid canonical language names are: Python, C, C++, C#, Rust, JavaScript, TypeScript, Java, Go, Ruby, PHP, Swift, Kotlin, Scala, Lua, Shell, Perl, Haskell, Zig, Elixir; any unknown language name MUST produce a `ReqError` with exit code 1.
- **SRS-250**: `--enable-static-check` MUST accept a module name (case-insensitive) as the first comma-separated token after `=`: Dummy, Pylance, Ruff, or Command; for Command the second comma-separated token is the mandatory `cmd` binary; during non-`--update` initialization that does not load config values, Command `cmd` MUST resolve to an executable program (`shutil.which`) or the command MUST fail with `ReqError` exit code 1 before any configuration is persisted; all subsequent comma-separated tokens are `params` stored as a JSON array, commas inside single-quoted or double-quoted tokens MUST NOT split parameters, and surrounding single or double quotes on each token MUST be stripped before persistence; unknown module names MUST produce a `ReqError` with exit code 1.
- **SRS-251**: When `--enable-static-check` is specified multiple times, entries MUST be preserved in insertion order per canonical language; an entry structurally identical (`module`, `cmd`, and `params` fields all equal) to an already-accumulated entry for the same canonical language MUST be silently discarded.
- **SRS-301**: When `--enable-static-check` is invoked against an existing `.req/config.json` (via `--update` or `--here`), the command MUST load and preserve all pre-existing `"static-check"` entries without removal; for each new CLI-specified entry, if a structurally identical entry (same `module`, `cmd`, and `params`) already exists for that canonical language in the loaded config, the new entry MUST be discarded; otherwise it MUST be appended.
- **SRS-252**: When `--enable-static-check` is used during installation or update, `.req/config.json` key `"static-check"` MUST be a JSON object keyed by canonical language name, and each language value MUST be a non-empty JSON array of entry objects with required `"module"` and optional `"cmd"`/`"params"` fields.

### 5.4 Static Analysis Execution Commands
- **SRS-253**: The CLI MUST support `--files-static-check FILE [FILE ...]` as a standalone command (no `--base`/`--here` required); for each FILE it MUST resolve absolute path, detect language, load the language array from `"static-check"`, and execute all configured entries sequentially; files with no language or no configured entries MUST be skipped.
- **SRS-254**: When `--files-static-check` cannot locate `.req/config.json` (no `--here`, no `--base`, and no `.req/config.json` exists in CWD), the command MUST print a warning to stderr and exit with code 0 without checking any files.
- **SRS-255**: The `--files-static-check` command exit code MUST be 0 when all checked files pass (or no files are checked), and 1 when at least one file fails static analysis.
- **SRS-256**: The CLI MUST support `--static-check` as a `--here`-only project-scan command with implicit `--here`, `--base` rejection, and file selection from `git ls-files` under configured `src-dir` values plus SRS-131/SRS-180 filtering.
- **SRS-257**: The `--static-check` command exit code MUST be 0 when all checked files pass (or no files are checked), and 1 when at least one file fails static analysis; it MUST remain dispatched via `_is_project_scan_command`.
### 5.5 Static Analysis Dispatch Implementation Requirements
- **SRS-258**: The implementation MUST provide a `STATIC_CHECK_LANG_CANONICAL` dict in `src/usereq/static_check.py` mapping lowercase language identifiers (including common aliases: `cpp` for C++, `csharp` for C#, `js` for JavaScript, `ts` for TypeScript, `sh` for Shell) to canonical language names from SRS-249.
- **SRS-259**: The implementation MUST provide a `STATIC_CHECK_EXT_TO_LANG` dict in `src/usereq/static_check.py` mapping file extensions to canonical language names, using the same 20-language extension set as SRS-131.
- **SRS-260**: The implementation MUST provide a `parse_enable_static_check(spec: str) -> tuple[str, dict]` function in `src/usereq/static_check.py` that: splits on the first `=`, validates the language (case-insensitive) and module (case-insensitive), tokenizes the right side as a comma-separated list to extract MODULE, optional `cmd` (for Command), and `params`, treats commas inside single-quoted or double-quoted tokens as literal characters, strips surrounding single or double quotes from each token, and returns `(canonical_lang, config_dict)`.
- **SRS-261**: The implementation MUST provide a `dispatch_static_check_for_file(filepath: str, lang_config: dict) -> int` function in `src/usereq/static_check.py` that: reads `module`, `cmd`, and `params` from `lang_config`; instantiates the appropriate checker class (`StaticCheckBase`, `StaticCheckPylance`, `StaticCheckRuff`, or `StaticCheckCommand`); and calls `run()` on a single-element file list.

### 5.6 Static Analysis Configuration and Dispatch Test Requirements
- **SRS-262**: The project MUST include unit tests in `tests/test_static_check.py` for parser/dispatcher behavior plus multi-entry language arrays, including repeated `Command` entries for one language and sequential execution checks for `--files-static-check` and `--static-check`.
