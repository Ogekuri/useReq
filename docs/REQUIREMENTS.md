---
title: "useReq Requirements"
description: "Software Requirements Specification"
date: "2026-03-17"
version: 1.09
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
- Functional domains: project resource generation, configuration persistence, source analysis, token counting, compression, construct extraction, Doxygen field extraction, and git worktree management.
- Out-of-scope for this SRS rewrite: source-code modification.

### 1.3 Components and Dependencies
- Runtime: Python 3.11+.
- Core libraries: `argparse`, `pathlib`, `json`, `re`, `os`, `shutil`, `subprocess`, `urllib`.
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

### 2.2 Project Constraints

## 3. Requirements

### 3.1 Design and Implementation Constraints

### 3.2 CLI Interface and Lifecycle
- **SRS-034**: MUST implement the following behavior: The CLI MUST accept `--upgrade`, `--uninstall`, the boolean flag `--preserve-models`, and repeatable `--provider SPEC`; provider configuration MUST remain exclusive to `--provider SPEC`; listed legacy global flags MUST NOT be parsed; with `--update` + `--preserve-models`, `.req/models.json` MUST be preserved.
- **SRS-035**: MUST implement the following behavior: During installation without `--update`, the CLI MUST require at least one `--provider` spec; otherwise it MUST print an English error and exit code 4. Each `--provider` spec implicitly enables the named provider and the listed artifact types.
- **SRS-036**: MUST implement the following behavior: The installation summary table MUST include rows only for providers whose prompts were installed during the current invocation.
- **SRS-049**: MUST implement the following behavior: Immediately after the file list, CLI MUST print a Unicode box-drawing installation summary table with bright-red border lines.
- **SRS-290**: MUST implement the following behavior: The `Prompts Installed` column MUST use a maximum display width of 50 characters and MUST wrap overflowing content onto subsequent lines.
- **SRS-291**: MUST implement the following behavior: The `Modules Installed` column MUST render one line per active `--provider` artifact as `artifact` when no options are active, or `artifact:options` when options are active, where `artifact` is `prompts`, `agents`, or `skills`.
- **SRS-296**: MUST implement the following behavior: The `Modules Installed` column width MUST fit the longest rendered module-entry line in active rows and MUST NOT wrap module-entry lines.
- **SRS-055**: MUST implement the following behavior: The repository MUST keep `uv.lock` as the canonical committed dependency lockfile for execution, build, development, testing, and static analysis environments, and MUST NOT keep a root `requirements.txt` manifest.
- **SRS-056**: MUST implement the following behavior: `scripts/req.sh` MUST execute the CLI via `uv run python -m usereq.cli` from repository root, MUST forward all user-provided CLI arguments unchanged, and MUST rely on uv-managed runtime environments.
- **SRS-342**: MUST implement the following behavior: `README.md` MUST include a `Requirements` section stating that Astral `uv` tool is required for `scripts/req.sh` and recommended project CLI execution workflows.
- **SRS-264**: MUST implement the following behavior: Runtime dependency declarations in `pyproject.toml` `[project].dependencies` MUST be present in the locked package set defined by `uv.lock`; `[project].dependencies` MUST include `ruff` and `pyright`; `[build-system].requires` MAY be outside `uv.lock`.
- **SRS-064**: MUST implement the following behavior: With `--update`, the CLI MUST load paths, `--preserve-models` flag, and persisted `providers` array from `.req/config.json`, then apply only CLI-provided `--preserve-models` flag and `--provider` specs as overrides; if no provider spec is active after merging, it MUST raise a config-invalid error.
- **SRS-066**: MUST implement the following behavior: The command MUST copy the `.req/models.json` configuration file, replacing the pre-existing file if present, unless `--preserve-models` is active. When `--preserve-models` is NOT active: if the `legacy` option is NOT active for the provider being processed, it MUST copy `models.json` from package resources (`src/usereq/resources/common/models.json`); if `legacy` is active (via `--provider PROVIDER:...:legacy`) and `models-legacy.json` file is successfully loaded (i.e. when it exists), it MUST copy `models-legacy.json` from package resources (`src/usereq/resources/common/models-legacy.json`). This copy MUST take place after creating the `.req` directory and after saving `config.json`.
- **SRS-085**: MUST implement the following behavior: The CLI MUST load prompt-generation configurations; with `--preserve-models` + `--update` and existing `.req/models.json`, it MUST load from `.req/models.json` and the per-provider `legacy` option MUST have no effect; otherwise it MUST load `src/usereq/resources/common/models.json` for `<cli>` `prompts` and `usage_modes`, and if the `legacy` option is active for a provider (via `--provider PROVIDER:...:legacy`) it MUST prefer `src/usereq/resources/common/models-legacy.json` when present (file-level fallback), else use `models.json`; `src/usereq/resources/<cli>/config.json` MUST NOT be used and MAY be removed; if `write.model` is defined, `readme` MUST use the same `model` and `mode` as `write`.
- **SRS-275**: MUST implement the following behavior: The CLI MUST accept a repeatable `--provider SPEC` argument as the sole mechanism for provider enablement, artifact selection, and per-provider option configuration. SPEC MUST follow the syntax `PROVIDER:ARTIFACTS[:OPTIONS]`; PROVIDER MUST be one of `codex`, `claude`, `gemini`, `github`, `kiro`, `opencode`; ARTIFACTS MUST be a comma-separated list from `{prompts, agents, skills}`; OPTIONS, when present, MUST be a comma-separated list from `{enable-models, enable-tools, prompts-use-agents, legacy}`.
- **SRS-276**: MUST implement the following behavior: When one or more `--provider` specs are given, each spec MUST enable the named provider for the listed artifact types and activate listed options for that provider only; artifact types and options not listed in a spec MUST remain inactive for that provider.
- **SRS-278**: MUST implement the following behavior: If a `--provider` SPEC contains an unknown PROVIDER name, unknown ARTIFACTS value, or unknown OPTIONS value, the CLI MUST print an English error message identifying the invalid token and exit with code 1.
- **SRS-279**: MUST implement the following behavior: The CLI MUST persist all `--provider` specs as a JSON array under the `"providers"` key in `.req/config.json`; each element MUST be the raw SPEC string as provided on the command line.
- **SRS-280**: MUST implement the following behavior: When `--update` loads `.req/config.json`, the CLI MUST restore persisted `"providers"` array entries; CLI-supplied `--provider` specs MUST replace (not merge with) persisted entries when at least one `--provider` flag is present on the command line.
- **SRS-281**: MUST treat this requirement as a removed legacy behavior and keep it unsupported.
- **SRS-282**: MUST treat this requirement as a removed legacy behavior and keep it unsupported.
- **SRS-343**: MUST implement the following behavior: `--upgrade` MUST execute `uv tool install usereq --force --from git+https://github.com/Ogekuri/useReq.git` only on Linux; on non-Linux, it MUST NOT execute `uv` and MUST print the manual command.
- **SRS-344**: MUST implement the following behavior: `--uninstall` on Linux MUST execute `uv tool uninstall usereq` and MUST run release-check cache cleanup per SRS-346; on non-Linux, it MUST NOT execute `uv` and MUST print the manual command.
- **SRS-345**: MUST implement the following behavior: Startup release-check idle-state MUST persist at `~/.cache/usereq/check_version_idle-time.json`, and release-check persistence writes MUST create missing parent directories before file serialization.
- **SRS-346**: MUST implement the following behavior: On Linux, `--uninstall` MUST delete `~/.cache/usereq/check_version_idle-time.json` when present and MUST remove `~/.cache/usereq` only when the directory is empty.

### 3.3 Provider Resource Generation
- **SRS-095**: MUST implement the following behavior: For each skill subdirectory of every enabled provider, the CLI MUST generate `SKILL.md` with YAML front matter containing: `name: req-<prompt_name>`; `description` populated by `extract_skill_description(prompt_frontmatter)` (see SRS-113) escaped for YAML double-quoted strings; `model` and `tools` fields populated using the provider-specific configuration from `models.json` or `models-legacy.json` according to the per-provider `legacy` option, subject to per-provider `enable-models` and `enable-tools` options; the prompt body with token substitutions applied.

- **SRS-263**: MUST implement the following behavior: The CLI MUST treat files under `src/usereq/resources/prompts` as read-only package inputs and MUST NOT create, modify, overwrite, rename, or delete files in that directory.

### 3.4 Removal and Cleanup

### 3.5 CI/CD Release Workflow
- **SRS-128**: MUST implement the following behavior: The workflow MUST build Python package (sdist and wheel) in `dist/`.
- **SRS-129**: MUST implement the following behavior: The workflow MUST create GitHub Release for the tag and load assets from `dist/`.
- **SRS-130**: MUST implement the following behavior: The workflow MUST generate artifact certifications for files in `dist/`.
- **SRS-268**: MUST implement the following behavior: The `.github/workflows/release-uvx.yml` workflow MUST define `workflow_dispatch` under `on` in addition to tag-push triggers so releases MAY be launched manually without altering automatic tag-trigger behavior.

### 3.5.1 Package Distribution and Resource Inclusion
- **SRS-272**: MUST implement the following behavior: The `[tool.setuptools.package-data]` section in `pyproject.toml` MUST enumerate glob patterns for required operational resource subdirectories only: `resources/common/*.json`, `resources/prompts/*.md`, `resources/guidelines/*.md`, `resources/docs/*.md`, `resources/vscode/settings.json`.
- **SRS-273**: MUST implement the following behavior: The `[tool.setuptools.package-data]` section in `pyproject.toml` MUST NOT list glob patterns that reference non-existent directories under `src/usereq/resources/`.
- **SRS-274**: MUST implement the following behavior: The built distribution (sdist and wheel) MUST include all files under `src/usereq/resources/` that are required for program operation, ensuring congruent behavior between local development execution, `uv`-installed package execution, and `uvx` live execution.

### 3.6 Source Analysis Core
- **SRS-131**: MUST implement the following behavior: The `usereq.source_analyzer` module MUST support 20 programming languages: C (`.c`), C++ (`.cpp`), C# (`.cs`), Elixir (`.ex`), Go (`.go`), Haskell (`.hs`), Java (`.java`), JavaScript (`.js`, `.mjs`), Kotlin (`.kt`), Lua (`.lua`), Perl (`.pl`), PHP (`.php`), Python (`.py`), Ruby (`.rb`), Rust (`.rs`), Scala (`.scala`), Shell (`.sh`), Swift (`.swift`), TypeScript (`.ts`), and Zig (`.zig`).
- **SRS-133**: MUST implement the following behavior: Each recognized element MUST contain: element type, initial row, final row, source code extract (maximum 5 rows), optional name, optional signature, optional visibility, optional parent name, optional inheritance, hierarchical depth.
- **SRS-143**: MUST implement the following behavior: The `usereq.source_analyzer` module MUST extract the documentation comment blocks associated with each construct and store them in `SourceElement` for the Doxygen parsing downstream.

### 3.7 Token Counting

### 3.8 Reference Markdown Generation

### 3.9 Source Compression

### 3.10 Construct Extraction and Command Operations
- **SRS-177**: MUST implement the following behavior: The `--references` command MUST select candidate files from `git ls-files` output under `src-dir` values loaded from `.req/config.json`, then keep only supported extensions from SRS-131.
- **SRS-179**: MUST implement the following behavior: The `--compress` command MUST select candidate files from `git ls-files` output under `src-dir` values loaded from `.req/config.json`, then keep only supported extensions from SRS-131.
- **SRS-180**: MUST implement the following behavior: For `--references`, `--compress`, `--find`, and `--static-check`, `EXCLUDED_DIRS` MUST contain only directory names that are not already excluded by `.gitignore`.
- **SRS-181**: MUST implement the following behavior: Source-file selection for `--references` and `--compress` MUST be derived from `git ls-files` relative paths and MUST NOT rely on recursive filesystem walking.

### 3.11 Doxygen Parsing and Field Emission
- **SRS-213**: MUST implement the following behavior: The parser MUST recognize these Doxygen tags: @brief, @details, @param, @param[in], @param[out], @param[in,out], @return, @retval, @exception, @throws, @warning, @deprecated, @note, @see, @sa, @satisfies, @pre, @post.

## 4. Test Requirements

### 4.1 Test and Verification Requirements
- **SRS-231**: MUST implement the following behavior: Every file in `tests/fixtures/` MUST include one file-level Doxygen block with `@file`, `@brief`, and `@details`, and MUST retain at least five construct-level blocks with `@brief`, `@details`, `@param`, and `@return`.
- **SRS-233**: MUST implement the following behavior: The project MUST include `tests/fixtures/`-based Doxygen tests that, for each fixture file, extract all the constructions present compatible with SRS-187, validate the Doxygen fields expected for each construct, and verify that the comment association→built is correct for both pre-built comments and post-built comments when allowed by the language syntax.
- **SRS-234**: MUST verify in `tests/test_files_commands.py` that `--files-references` outputs Doxygen field bullets with original tags from SRS-213 (`@brief` ... `@post`) and never emits converted labels like `Brief:`.
- **SRS-235**: MUST verify in `tests/test_files_commands.py` that `--references` outputs Doxygen field bullets with original tags from SRS-213 (`@brief` ... `@post`) and never emits converted labels like `Brief:`.
- **SRS-236**: MUST verify command-level `--files-find` outputs Doxygen field bullets using original tags from SRS-213 (`@brief` ... `@post`) with SRS-220 placement and SRS-221 order, never converted labels.
- **SRS-237**: MUST verify command-level `--find` outputs Doxygen field bullets using original tags from SRS-213 (`@brief` ... `@post`) with SRS-220 placement, SRS-221 order, and no converted labels.
- **SRS-284**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that `--provider PROVIDER:ARTIFACTS[:OPTIONS]` parsing accepts valid specs and rejects unknown providers, unknown artifacts, and unknown options with exit code 1.
- **SRS-285**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that multiple `--provider` specs correctly enable distinct per-provider artifact types and per-provider options independently.
- **SRS-286**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that `--provider` specs are persisted to and restored from `.req/config.json` under the `"providers"` key during `--update` round-trips.
- **SRS-287**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that per-provider `enable-models`, `enable-tools`, `prompts-use-agents`, and `legacy` options from `--provider` specs are applied independently to each targeted provider.
- **SRS-288**: MUST implement the following behavior: The `.req/config.json` file MUST persist only the `"providers"` JSON array (raw SPEC strings) and the `"preserve-models"` boolean for update round-trips; the 13 legacy boolean keys (`enable-models`, `enable-tools`, `enable-claude`, `enable-codex`, `enable-gemini`, `enable-github`, `enable-kiro`, `enable-opencode`, `install-prompts`, `install-agents`, `install-skills`, `prompts-use-agents`, `legacy`) MUST NOT be written to or required from `config.json`.
- **SRS-293**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that `Prompts Installed` content wraps with a maximum display width of 50 characters.
- **SRS-294**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that `Modules Installed` renders one module-entry line per active provider artifact from `--provider` using `artifact` without options or `artifact:options` when options exist.
- **SRS-297**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that `Modules Installed` preserves parsed option token order in each `artifact:options` line and emits only `artifact` when options are absent.
- **SRS-298**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that `Modules Installed` does not wrap module-entry lines and widths include the longest rendered module-entry line.

## 5. Static Code Analysis Requirements

### 5.1 Static Analysis Feature Overview
- **SRS-240**: MUST implement the following behavior: The `--test-static-check` flag MUST accept an optional list of `[FILES]...` arguments following the subcommand name and optional subcommand-specific options. Each element of `[FILES]` MAY be: a path to a directory (direct children only), a glob pattern (e.g., `path/**/*.py`) with full `**` recursive expansion support, or a specific file path. No custom `--recursive` flag is defined; recursive traversal is expressed via `**` glob syntax.
- **SRS-241**: MUST implement the following behavior: The implementation MUST provide a `StaticCheckBase` (Dummy) class in `src/usereq/static_check.py` that iterates over resolved input files; when `fail_only` mode is inactive, MUST emit `# Static-Check(Dummy): <filename> [OPTIONS]`, emit `Result: OK`, and append exactly one trailing blank line after each per-file block; when `fail_only` mode is active, a passing file MUST produce no output.
- **SRS-242**: MUST implement the following behavior: The implementation MUST provide a `StaticCheckPylance` class derived from `StaticCheckBase` that invokes `pyright` per resolved file via `[sys.executable, '-m', 'pyright', '--pythonpath', sys.executable, <extra_path_args>, <filepath>, <extra_args>...]` subprocess using the active runtime interpreter; when `fail_only` mode is inactive, MUST emit `# Static-Check(Pylance): <filename> [OPTIONS]`, emit `Result: OK` or `Result: FAIL\nEvidence:\n<output>`, and append exactly one trailing blank line after each per-file block; when `fail_only` mode is active, a passing file MUST produce no output and a failing file MUST emit header, `Result: FAIL\nEvidence:\n<output>`, and one trailing blank line.
- **SRS-243**: MUST implement the following behavior: The implementation MUST provide a `StaticCheckRuff` class derived from `StaticCheckBase` that invokes `ruff check` per resolved file via `[sys.executable, '-m', 'ruff', 'check', <filepath>, <extra_args>...]` subprocess using the active runtime interpreter; when `fail_only` mode is inactive, MUST emit `# Static-Check(Ruff): <filename> [OPTIONS]`, emit `Result: OK` or `Result: FAIL\nEvidence:\n<output>`, and append exactly one trailing blank line after each per-file block; when `fail_only` mode is active, a passing file MUST produce no output and a failing file MUST emit header, `Result: FAIL\nEvidence:\n<output>`, and one trailing blank line.
- **SRS-244**: MUST implement the following behavior: The implementation MUST provide a `StaticCheckCommand` class derived from `StaticCheckBase` that requires `command <cmd>`, validates `cmd` on PATH (`shutil.which`), invokes external tools as `<cmd> [params...] <filename>`; when `fail_only` mode is inactive, MUST emit `# Static-Check(Command[<cmd>]): <filename> [OPTIONS]`, emit pass/fail output, and append exactly one trailing blank line after each per-file block; when `fail_only` mode is active, a passing file MUST produce no output and a failing file MUST emit header, `Result: FAIL\nEvidence:\n<output>`, and one trailing blank line.
- **SRS-245**: MUST implement the following behavior: All static-check classes MUST resolve `[FILES]` input using glob expansion (with `**` recursive support always enabled) for patterns, and direct-children-only traversal for bare directory entries, collecting only regular files. If the resolved file list is empty, the command MUST print a warning to stderr and exit with code 0.

### 5.2 Static Analysis Test Requirements
- **SRS-247**: MUST implement the following behavior: The project MUST include `tests/test_static_check.py` with unit tests for: `StaticCheckBase` (Dummy) output format with one trailing blank separator line per file block; `StaticCheckPylance` and `StaticCheckRuff` OK/FAIL branches with mocked subprocess; pyright command composition including `--pythonpath sys.executable` and excluding `--extra-path`; absence of `.venv` interpreter probing; `StaticCheckCommand` availability check and OK/FAIL branches with mocked subprocess; glob pattern resolution including `**` recursive expansion; direct-children-only directory resolution; empty-file-list warning behavior; `fail_only` mode suppressing all output on pass for each checker class.

### 5.3 Static Analysis Configuration Requirements
- **SRS-248**: MUST implement the following behavior: The CLI MUST support repeatable `--enable-static-check SPEC` (`LANG=MODULE[,CMD[,PARAM...]]`), and each SPEC occurrence MUST append one static-check entry under the canonical language key in `.req/config.json` key `"static-check"`.
- **SRS-249**: MUST implement the following behavior: `--enable-static-check` MUST accept language names case-insensitively; the 20 valid canonical language names are: Python, C, C++, C#, Rust, JavaScript, TypeScript, Java, Go, Ruby, PHP, Swift, Kotlin, Scala, Lua, Shell, Perl, Haskell, Zig, Elixir; any unknown language name MUST produce a `ReqError` with exit code 1.
- **SRS-250**: MUST implement the following behavior: `--enable-static-check` MUST accept a module name (case-insensitive) as the first comma-separated token after `=`: Dummy, Pylance, Ruff, or Command; for Command the second comma-separated token is the mandatory `cmd` binary; during non-`--update` initialization that does not load config values, Command `cmd` MUST resolve to an executable program (`shutil.which`) or the command MUST fail with `ReqError` exit code 1 before any configuration is persisted; all subsequent comma-separated tokens are `params` stored as a JSON array, commas inside single-quoted or double-quoted tokens MUST NOT split parameters, and surrounding single or double quotes on each token MUST be stripped before persistence; unknown module names MUST produce a `ReqError` with exit code 1.
- **SRS-251**: MUST implement the following behavior: When `--enable-static-check` is specified multiple times, entries MUST be preserved in insertion order per canonical language; an entry structurally identical (`module`, `cmd`, and `params` fields all equal) to an already-accumulated entry for the same canonical language MUST be silently discarded.
- **SRS-301**: MUST implement the following behavior: When `--enable-static-check` is invoked against an existing `.req/config.json` (via `--update` or `--here`), the command MUST load and preserve all pre-existing `"static-check"` entries without removal; for each new CLI-specified entry, presence MUST be decided by exact tuple match `(canonical language, module, cmd, params)` in the loaded config; if present discard, otherwise append.
- **SRS-252**: MUST implement the following behavior: When `--enable-static-check` is used during installation or update, `.req/config.json` key `"static-check"` MUST be a JSON object keyed by canonical language name, and each language value MUST be a non-empty JSON array of entry objects with required `"module"` and optional `"cmd"`/`"params"` fields.

### 5.4 Static Analysis Execution Commands
- **SRS-253**: MUST implement the following behavior: The CLI MUST support `--files-static-check FILE [FILE ...]` as a standalone command (no `--base`/`--here` required); for each FILE it MUST resolve absolute path, detect language, load the language array from `"static-check"`, and execute all configured entries sequentially with `fail_only` mode active and dispatch context containing resolved project base; for `Command` entries it MUST invoke tools as `<cmd> [params...] <filename>`; files with no language or no configured entries MUST be skipped; passing checks MUST produce no stdout output.
- **SRS-254**: MUST implement the following behavior: When `--files-static-check` cannot locate `.req/config.json` (no `--here`, no `--base`, and no `.req/config.json` exists in CWD), the command MUST print a warning to stderr and exit with code 0 without checking any files.
- **SRS-255**: MUST implement the following behavior: The `--files-static-check` command exit code MUST be 0 when all checked files pass (or no files are checked), and 1 when at least one file fails static analysis.
- **SRS-256**: MUST implement the following behavior: The CLI MUST support `--static-check` as a `--here`-only project-scan command with implicit `--here`, `--base` rejection, and file selection from `git ls-files` under configured `src-dir` values and the `tests-dir` value plus SRS-131/SRS-180 filtering; all checks MUST execute with `fail_only` mode active and dispatch context containing resolved project base; for `Command` entries it MUST invoke tools as `<cmd> [params...] <filename>`; passing checks MUST produce no stdout output.
- **SRS-257**: MUST implement the following behavior: The `--static-check` command exit code MUST be 0 when all checked files pass (or no files are checked), and 1 when at least one file fails static analysis; it MUST remain dispatched via `_is_project_scan_command`.
- **SRS-336**: MUST implement the following behavior: The `--static-check` command MUST load the `tests-dir` value from `.req/config.json` and append it to the `src-dir` list for file selection; if `tests-dir` is missing or invalid the command MUST skip test directory inclusion without error.
### 5.5 Static Analysis Dispatch Implementation Requirements
- **SRS-258**: MUST implement the following behavior: The implementation MUST provide a `STATIC_CHECK_LANG_CANONICAL` dict in `src/usereq/static_check.py` mapping lowercase language identifiers (including common aliases: `cpp` for C++, `csharp` for C#, `js` for JavaScript, `ts` for TypeScript, `sh` for Shell) to canonical language names from SRS-249.
- **SRS-259**: MUST implement the following behavior: The implementation MUST provide a `STATIC_CHECK_EXT_TO_LANG` dict in `src/usereq/static_check.py` mapping file extensions to canonical language names, using the same 20-language extension set as SRS-131.
- **SRS-260**: MUST implement the following behavior: The implementation MUST provide a `parse_enable_static_check(spec: str) -> tuple[str, dict]` function in `src/usereq/static_check.py` that: splits on the first `=`, validates the language (case-insensitive) and module (case-insensitive), tokenizes the right side as a comma-separated list to extract MODULE, optional `cmd` (for Command), and `params`, treats commas inside single-quoted or double-quoted tokens as literal characters, strips surrounding single or double quotes from each token, and returns `(canonical_lang, config_dict)`.
- **SRS-261**: MUST implement the following behavior: The implementation MUST provide a `dispatch_static_check_for_file(filepath: str, lang_config: dict, *, fail_only: bool = False, project_base: Optional[Path] = None) -> int` function in `src/usereq/static_check.py` that: reads `module`, `cmd`, and `params` from `lang_config`; instantiates the appropriate checker class (`StaticCheckBase`, `StaticCheckPylance`, `StaticCheckRuff`, or `StaticCheckCommand`) passing `fail_only`; forwards `project_base` to `StaticCheckPylance`; and calls `run()` on a single-element file list.

### 5.6 Static Analysis Configuration and Dispatch Test Requirements
- **SRS-262**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_static_check.py` for parser/dispatcher behavior plus multi-entry language arrays, including repeated `Command` entries for one language and sequential execution checks for `--files-static-check` and `--static-check`.
- **SRS-337**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_static_check.py` verifying that `--static-check` includes files from both `src-dir` and `tests-dir` directories in its file selection.
- **SRS-338**: MUST implement the following behavior: `pyproject.toml` `[project].dependencies` MUST include `ruff` and `pyright` as runtime dependencies so that static-analysis tools are distributed and installed with the package.
- **SRS-339**: MUST implement the following behavior: `StaticCheckPylance` and `StaticCheckRuff` MUST invoke their respective tools via `[sys.executable, '-m', '<tool_module>', ...]` subprocess commands using the current process interpreter (uv tool/uvx runtime when executed via uv), MUST NOT require external PATH resolution, and MUST NOT require project `.venv` discovery.
- **SRS-341**: MUST implement the following behavior: `StaticCheckPylance` MUST NOT pass any `--extra-path` argument to pyright and MUST invoke pyright using only the fixed interpreter/module command form and target filepath.
- **SRS-340**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_dependency_manifests.py` verifying that `ruff` and `pyright` are declared in `pyproject.toml` `[project].dependencies`.

## 6. Git Integration and Worktree Management Requirements

### 6.1 Configuration Path Persistence
- **SRS-302**: MUST implement the following behavior: During installation (`--base` without `--update`), the CLI MUST resolve the `--base` path to an absolute filesystem path and persist it as `"base-path"` in `.req/config.json`.
- **SRS-303**: MUST implement the following behavior: During `--update`, if the current absolute project path differs from the `"base-path"` value in `.req/config.json`, the CLI MUST update `"base-path"` to the current absolute path.
- **SRS-305**: MUST implement the following behavior: During installation (`--base`), the CLI MUST verify that the resolved `--base` path is inside a git repository by executing `git rev-parse --is-inside-work-tree` in the resolved path; if not inside a git repository, the CLI MUST terminate with a non-zero exit code and an English error message.
- **SRS-306**: MUST implement the following behavior: During installation, after verifying git repository membership, the CLI MUST determine the git repository root via `git rev-parse --show-toplevel` and persist it as `"git-path"` in `.req/config.json`.
- **SRS-307**: MUST implement the following behavior: During `--update`, if the current git repository root differs from the `"git-path"` value in `.req/config.json`, the CLI MUST update `"git-path"` to the current value.
- **SRS-309**: MUST implement the following behavior: The variable `"base-dir"` MUST be derived dynamically at runtime as the relative path from `"git-path"` to `"base-path"` and MUST NOT be persisted in `.req/config.json`.
- **SRS-310**: MUST implement the following behavior: When `.req/config.json` is loaded for `--here` or `--base` on an existing project, ALL key-value parameters in the configuration file MUST be loaded and available to CLI command functions.

### 6.2 Git Check Command
- **SRS-311**: MUST implement the following behavior: The CLI MUST support `--git-check` as a `--here`-only command that MUST reject `--base`; `--here` MUST be implied if not explicitly provided.
- **SRS-312**: MUST implement the following behavior: The `--git-check` command MUST execute `git rev-parse --is-inside-work-tree && ! git status --porcelain | grep -q . && { git symbolic-ref -q HEAD || git rev-parse --verify HEAD ; }` in the `"git-path"` directory, MUST print no output on success, and on non-zero exit MUST print `ERROR: Git status unclear!\n` to stdout and exit with non-zero code.

### 6.3 Docs Check Command
- **SRS-313**: MUST implement the following behavior: The CLI MUST support `--docs-check` as a `--here`-only command that MUST reject `--base`; `--here` MUST be implied if not explicitly provided.
- **SRS-314**: MUST implement the following behavior: The `--docs-check` command MUST construct `DOC_PATH` as `"base-path"/"docs-dir"` using values from `.req/config.json` and verify existence of `REQUIREMENTS.md`, `WORKFLOW.md`, and `REFERENCES.md` in sequential order.
- **SRS-315**: MUST implement the following behavior: If `DOC_PATH/REQUIREMENTS.md` does not exist, `--docs-check` MUST print `ERROR: File <DOC_PATH>/REQUIREMENTS.md does not exist, generate it with the /req-write prompt!\n` to stdout and exit with non-zero code.
- **SRS-316**: MUST implement the following behavior: If `DOC_PATH/WORKFLOW.md` does not exist, `--docs-check` MUST print `ERROR: File <DOC_PATH>/WORKFLOW.md does not exist, generate it with the /req-workflow prompt!\n` to stdout and exit with non-zero code.
- **SRS-317**: MUST implement the following behavior: If `DOC_PATH/REFERENCES.md` does not exist, `--docs-check` MUST print `ERROR: File <DOC_PATH>/REFERENCES.md does not exist, generate it with the /req-references prompt!\n` to stdout and exit with non-zero code.

### 6.4 Git Worktree Name Command
- **SRS-318**: MUST implement the following behavior: The CLI MUST support `--git-wt-name` as a `--here`-only command that MUST reject `--base`; `--here` MUST be implied if not explicitly provided.
- **SRS-319**: MUST implement the following behavior: The `--git-wt-name` command MUST print exactly `useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>` where `<PROJECT_NAME>` is the basename of `"git-path"`, `<ORIGINAL_BRANCH>` is the current git branch name with characters incompatible with Linux or Windows paths replaced by `-`, and `<EXECUTION_ID>` is the current timestamp formatted as `YYYYMMDDHHmmss`.

### 6.5 Git Worktree Create Command
- **SRS-320**: MUST implement the following behavior: The CLI MUST support `--git-wt-create WT_NAME` as a `--here`-only command that MUST reject `--base`; `--here` MUST be implied if not explicitly provided; `WT_NAME` is mandatory.
- **SRS-321**: MUST implement the following behavior: The `--git-wt-create` command MUST validate that `WT_NAME` contains only characters compatible with both Linux and Windows directory names; if invalid, it MUST print `ERROR: Invalid worktree/branch name: <WT_NAME>.\n` and exit with non-zero code.
- **SRS-322**: MUST implement the following behavior: The `--git-wt-create` command MUST execute `git worktree add "<parent-path>/<WT_NAME>" -b <WT_NAME>` from within the `"git-path"` directory.
- **SRS-323**: MUST implement the following behavior: After worktree creation, `--git-wt-create` MUST copy `"base-path"/.req` with all subdirectories to `"<parent-path>/<WT_NAME>/<base-dir>"` if `.req` is not already present in the destination.
- **SRS-324**: MUST implement the following behavior: After worktree creation, `--git-wt-create` MUST copy active provider directories from `"base-path"` to `"<parent-path>/<WT_NAME>/<base-dir>"`, only for providers configured in `"providers"` whose source directories exist on the filesystem.
- **SRS-325**: MUST implement the following behavior: The provider-to-directory mapping for `--git-wt-create` MUST be: claude -> `.claude/commands`, `.claude/agents`, `.claude/skills`; gemini -> `.gemini/commands`, `.gemini/skills`; github -> `.github/prompts`, `.github/agents`, `.github/skills`; codex -> `.codex/prompts`, `.codex/skills`; kiro -> `.kiro/prompts`, `.kiro/agents`, `.kiro/skills`; opencode -> `.opencode/agent`, `.opencode/command`, `.opencode/skill`.
- **SRS-331**: MUST implement the following behavior: The `--git-wt-create` command MUST change the current directory to `"<parent-path>/<WT_NAME>"` only as the final successful operation and MUST exit with code 0; if post-create operations fail, it MUST rollback created worktree and branch and MUST NOT change current directory.
- **SRS-335**: MUST implement the following behavior: Before the final directory change, `--git-wt-create` MUST check for a `.venv` directory in `"base-path"` first, then `"git-path"`; when found and destination is absent, it MUST copy `.venv` preserving its relative path from `"git-path"`.

### 6.6 Git Worktree Delete Command
- **SRS-326**: MUST implement the following behavior: The CLI MUST support `--git-wt-delete WT_NAME` as a `--here`-only command that MUST reject `--base`; `--here` MUST be implied if not explicitly provided; `WT_NAME` is mandatory.
- **SRS-327**: MUST implement the following behavior: The `--git-wt-delete` command MUST validate only exact targets for `WT_NAME`: branch ref `refs/heads/<WT_NAME>` and worktree path `"<parent-path>/<WT_NAME>"`; substring or partial-name matches MUST NOT be accepted.
- **SRS-328**: MUST implement the following behavior: The `--git-wt-delete` command MUST change current directory to `"base-path"` before deletion, then force-remove only exact target worktree and exact target branch using git commands, remaining robust when target worktree contains pending/uncommitted changes.
- **SRS-332**: MUST implement the following behavior: The `--git-wt-delete` command MUST NOT execute explicit file-system deletions of worktree content paths (for example `.req`, `.claude`, `.codex`), and MUST rely only on `git worktree remove` and `git branch -D`.

### 6.7 Git Worktree Exit Command
- **SRS-333**: MUST implement the following behavior: The CLI MUST support `--git-wt-exit` as a `--here`-only command that MUST reject `--base`; `--here` MUST be implied if not explicitly provided.
- **SRS-334**: MUST implement the following behavior: The `--git-wt-exit` command MUST change the current directory to `"base-path"` and MUST terminate successfully when the path change succeeds.

### 6.8 Git Integration Test Requirements
- **SRS-329**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying that `"base-path"` and `"git-path"` are persisted to `.req/config.json` during installation and updated during `--update` when paths change.
- **SRS-330**: MUST implement the following behavior: The project MUST include unit tests in `tests/test_cli.py` verifying the `--git-check`, `--docs-check`, `--git-wt-name`, `--git-wt-create` (including `.venv` copy behavior), `--git-wt-delete`, and `--git-wt-exit` commands behave per their respective requirements.
