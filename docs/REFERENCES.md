# Files Structure
```
.
└── src
    └── usereq
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── compress.py
        ├── compress_files.py
        ├── doxygen_parser.py
        ├── find_constructs.py
        ├── generate_markdown.py
        ├── source_analyzer.py
        ├── static_check.py
        └── token_counter.py
```

# __init__.py | Python | 26L | 0 symbols | 8 imports | 3 comments
> Path: `src/usereq/__init__.py`

## Imports
```
from . import cli  # usereq.cli submodule
from . import source_analyzer  # usereq.source_analyzer submodule
from . import token_counter  # usereq.token_counter submodule
from . import generate_markdown  # usereq.generate_markdown submodule
from . import compress  # usereq.compress submodule
from . import compress_files  # usereq.compress_files submodule
from . import find_constructs  # usereq.find_constructs submodule
from .cli import main  # re-export of CLI entry point
```


---

# __main__.py | Python | 17L | 0 symbols | 2 imports | 2 comments
> Path: `src/usereq/__main__.py`

## Imports
```
from .cli import main
import sys
```


---

# cli.py | Python | 3175L | 102 symbols | 28 imports | 166 comments
> Path: `src/usereq/cli.py`

## Imports
```
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import sys
import subprocess
import urllib.error
import urllib.request
import yaml
from argparse import Namespace
from pathlib import Path
from typing import Any, Mapping, Optional
from .find_constructs import format_available_tags
from .static_check import parse_enable_static_check as _parse_sc
import copy
from .token_counter import count_files_metrics, format_pack_summary
from .generate_markdown import generate_markdown
from .compress_files import compress_files
from .find_constructs import find_constructs_in_files
from .generate_markdown import generate_markdown
from .compress_files import compress_files
from .find_constructs import find_constructs_in_files
from .static_check import STATIC_CHECK_EXT_TO_LANG, dispatch_static_check_for_file
from .static_check import STATIC_CHECK_EXT_TO_LANG, dispatch_static_check_for_file
from .static_check import run_static_check
import traceback
```

## Definitions

- var `REPO_ROOT = Path(__file__).resolve().parents[2]` (L25)
- var `RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"` (L28)
- Brief: The absolute path to the repository root."""
- var `VERBOSE = False` (L31)
- Brief: The absolute path to the resources directory."""
- var `DEBUG = False` (L34)
- Brief: Whether verbose output is enabled."""
- var `REQUIREMENTS_TEMPLATE_NAME = "Requirements_Template.md"` (L37)
- Brief: Whether debug output is enabled."""
- var `PERSISTED_UPDATE_FLAG_KEYS = (` (L40)
- Brief: Name of the packaged requirements template file."""
### class `class ReqError(Exception)` : Exception (L59-72)
- Brief: Dedicated exception for expected CLI errors. Initialize an expected CLI failure payload.
- Details: This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.
- Param: message Human-readable error message. code Process exit code bound to the failure category.
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L63-72)
  - Brief: Dedicated exception for expected CLI errors. Initialize an expected CLI failure payload.
  - Details: This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.
  - Param: message Human-readable error message. code Process exit code bound to the failure category.

### fn `def log(msg: str) -> None` (L73-79)
- Brief: Prints an informational message.
- Param: msg The message string to print.

### fn `def dlog(msg: str) -> None` (L80-87)
- Brief: Prints a debug message if debugging is active.
- Param: msg The debug message string to print.

### fn `def vlog(msg: str) -> None` (L88-95)
- Brief: Prints a verbose message if verbose mode is active.
- Param: msg The verbose message string to print.

### fn `def _get_available_tags_help() -> str` `priv` (L96-107)
- Brief: Generate available TAGs help text for argument parser.
- Details: Imports format_available_tags from find_constructs module to generate dynamic TAG listing for CLI help display.
- Return: Formatted multi-line string listing TAGs by language.

### fn `def build_parser() -> argparse.ArgumentParser` (L108-307)
- Brief: Builds the CLI argument parser.
- Details: Defines all supported CLI arguments, flags, and help texts. Includes provider flags (--enable-claude, --enable-codex, --enable-gemini, --enable-github, --enable-kiro, --enable-opencode) and artifact-type flags (--enable-prompts, --enable-agents, --disable-skills).
- Return: Configured ArgumentParser instance.

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L364-371)
- Brief: Parses command-line arguments into a namespace.
- Param: argv List of arguments (defaults to sys.argv).
- Return: Namespace containing parsed arguments.

### fn `def load_package_version() -> str` (L372-384)
- Brief: Reads the package version from __init__.py.
- Return: Version string extracted from the package.
- Throws: ReqError If version cannot be determined.

### fn `def maybe_print_version(argv: list[str]) -> bool` (L385-395)
- Brief: Handles --ver/--version by printing the version.
- Param: argv Command line arguments to check.
- Return: True if version was printed, False otherwise.

### fn `def run_upgrade() -> None` (L396-419)
- Brief: Executes the upgrade using uv.
- Throws: ReqError If upgrade fails.

### fn `def run_uninstall() -> None` (L420-440)
- Brief: Executes the uninstallation using uv.
- Throws: ReqError If uninstall fails.

### fn `def normalize_release_tag(tag: str) -> str` (L441-451)
- Brief: Normalizes the release tag by removing a 'v' prefix if present.
- Param: tag The raw tag string.
- Return: The normalized version string.

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L452-476)
- Brief: Converts a version into a numeric tuple for comparison.
- Details: Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
- Param: version The version string to parse.
- Return: Tuple of integers or None if parsing fails.

### fn `def is_newer_version(current: str, latest: str) -> bool` (L477-493)
- Brief: Returns True if latest is greater than current.
- Param: current The current installed version string. latest The latest available version string.
- Return: True if update is available, False otherwise.

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L494-535)
- Brief: Checks online for a new version and prints a warning.
- Details: If the call fails or the response is invalid, it prints nothing and proceeds.
- Param: timeout_seconds Time to wait for the version check response.

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L536-555)
- Brief: Ensures the documentation directory exists under the project base.
- Param: path The relative path to the documentation directory. project_base The project root path.
- Throws: ReqError If path is invalid, absolute, or not a directory.

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L556-575)
- Brief: Ensures the test directory exists under the project base.
- Param: path The relative path to the test directory. project_base The project root path.
- Throws: ReqError If path is invalid, absolute, or not a directory.

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L576-595)
- Brief: Ensures the source directory exists under the project base.
- Param: path The relative path to the source directory. project_base The project root path.
- Throws: ReqError If path is invalid, absolute, or not a directory.

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L596-635)
- Brief: Normalizes the path relative to the project root when possible.
- Details: Handles cases where the path includes the project directory name redundantly.
- Param: path_value The input path string. project_base The base path of the project.
- Return: The normalized relative path string.

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L636-649)
- Brief: Resolves the absolute path starting from a normalized value.
- Param: normalized The normalized relative path string. project_base The project root path.
- Return: Absolute Path object or None if normalized is empty.

### fn `def format_substituted_path(value: str) -> str` (L650-659)
- Brief: Uniforms path separators for substitutions.
- Param: value The path string to format.
- Return: Path string with forward slashes.

### fn `def compute_sub_path(` (L660-661)

### fn `def save_config(` (L680-687)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L718-758)
- Brief: Loads parameters saved in .req/config.json.
- Param: project_base The project root path.
- Return: Dictionary containing configuration values.
- Throws: ReqError If config file is missing or invalid.

### fn `def load_static_check_from_config(project_base: Path) -> dict` (L759-790)
- Brief: Load the `"static-check"` section from `.req/config.json` without validation errors.
- Details: Reads config.json silently; returns `{}` on any read or parse error. Does NOT raise `ReqError`; caller decides whether absence is an error.
- Param: project_base The project root path.
- Return: Dict of static-check config (canonical-lang -> list[config-dict]); empty dict if absent or if config.json is missing/invalid.
- See: SRS-252, SRS-253, SRS-256

### fn `def build_persisted_update_flags(args: Namespace) -> dict[str, bool]` (L791-813)
- Brief: Build persistent update flags from parsed CLI arguments.
- Param: args Parsed CLI namespace.
- Return: Mapping of config key -> boolean value for install/update persistence.

### fn `def load_persisted_update_flags(project_base: Path) -> dict[str, bool]` (L814-838)
- Brief: Load persisted install/update boolean flags from `.req/config.json`.
- Param: project_base The project root path.
- Return: Mapping of persisted config key -> boolean value.
- Throws: ReqError If config file is missing, invalid, or required flag fields are missing/invalid.

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L839-866)
- Brief: Generates the markdown file list for %%GUIDELINES_FILES%% replacement.

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L867-895)
- Brief: Generates a list of relative file paths (no formatting) for printing.
- Details: Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.

### fn `def upgrade_guidelines_templates(` (L896-897)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L929-940)
- Brief: Normalizes the path token optionally preserving the trailing slash.

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L941-950)
- Brief: Validates that the path is not absolute and raises an error otherwise.

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L951-958)
- Brief: Returns text with token replacements applied.

### fn `def write_text_file(dst: Path, text: str) -> None` (L959-965)
- Brief: Writes text to disk, ensuring the destination folder exists.

### fn `def copy_with_replacements(` (L966-967)

### fn `def normalize_description(value: str) -> str` (L976-986)
- Brief: Normalizes a description by removing superfluous quotes and escapes.

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L987-1015)
- Brief: Converts a Markdown prompt to TOML for Gemini.

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L1016-1025)
- Brief: Extracts front matter and body from Markdown.

### fn `def extract_description(frontmatter: str) -> str` (L1026-1034)
- Brief: Extracts the description from front matter.

### fn `def extract_argument_hint(frontmatter: str) -> str` (L1035-1043)
- Brief: Extracts the argument-hint from front matter, if present.

### fn `def extract_purpose_first_bullet(body: str) -> str` (L1044-1064)
- Brief: Returns the first bullet of the Purpose section.

### fn `def _extract_section_text(body: str, section_name: str) -> str` `priv` (L1065-1092)
- Brief: Extracts and collapses the text content of a named ## section.
- Details: Scans `body` line by line for a heading matching `## <section_name>` (case-insensitive). Collects all subsequent non-empty lines until the next `##`-level heading (or end of string). Strips each line, joins with a single space, and returns the collapsed single-line result.
- Param[in]: body str -- Full prompt body text (after front matter removal). section_name str -- Target section name without `##` prefix (case-insensitive match).
- Return: str -- Single-line collapsed text of the section; empty string if section absent or empty.

### fn `def extract_skill_description(frontmatter: str) -> str` (L1093-1111)
- Brief: Extracts the usage field from YAML front matter as a single YAML-safe line.
- Details: Parses the YAML front matter and returns the `usage` field value with all whitespace normalized to a single line. Returns an empty string if the field is absent.
- Param[in]: frontmatter str -- YAML front matter text (without the leading/trailing `---` delimiters).
- Return: str -- Single-line text of the usage field; empty string if absent.

### fn `def json_escape(value: str) -> str` (L1112-1117)
- Brief: Escapes a string for JSON without external delimiters.

### fn `def generate_kiro_resources(` (L1118-1121)

### fn `def render_kiro_agent(` (L1141-1150)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L1184-1192)
- Brief: Replaces tokens in the specified file.

### fn `def yaml_double_quote_escape(value: str) -> str` (L1193-1198)
- Brief: Minimal escape for a double-quoted string in YAML.

### fn `def list_docs_templates() -> list[Path]` (L1199-1214)
- Brief: Returns non-hidden files available in resources/docs.
- Return: Sorted list of file paths under resources/docs.
- Throws: ReqError If resources/docs does not exist or has no non-hidden files.

### fn `def find_requirements_template(docs_templates: list[Path]) -> Path` (L1215-1229)
- Brief: Returns the packaged Requirements template file.
- Param: docs_templates Runtime docs template file list from resources/docs.
- Return: Path to `Requirements_Template.md`.
- Throws: ReqError If `Requirements_Template.md` is not present.

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L1230-1264)
- Brief: Loads the Kiro template from centralized models configuration.

### fn `def strip_json_comments(text: str) -> str` (L1265-1285)
- Brief: Removes // and /* */ comments to allow JSONC parsing.

### fn `def load_settings(path: Path) -> dict[str, Any]` (L1286-1297)
- Brief: Loads JSON/JSONC settings, removing comments when necessary.

### fn `def load_centralized_models(` (L1298-1301)

### fn `def get_model_tools_for_prompt(` (L1345-1346)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1381-1398)
- Brief: Returns the raw value of `usage_modes[mode]['tools']` for the prompt.
- Details: Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1399-1406)
- Brief: Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1407-1417)
- Brief: Recursively merges dictionaries, prioritizing incoming values.

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1418-1426)
- Brief: Finds the VS Code settings template if available.

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1427-1437)
- Brief: Generates chat.promptFilesRecommendations from available prompts.

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1438-1447)
- Brief: Verifies that the path is under the project root.

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1448-1457)
- Brief: Saves a backup of VS Code settings if the file exists.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1458-1469)
- Brief: Restores VS Code settings from backup, if present.

### fn `def prune_empty_dirs(root: Path) -> None` (L1470-1483)
- Brief: Removes empty directories under the specified root.

### fn `def remove_generated_resources(project_base: Path) -> None` (L1484-1529)
- Brief: Removes resources generated by the tool in the project root.

### fn `def run_remove(args: Namespace) -> None` (L1530-1576)
- Brief: Handles the removal of generated resources.

### fn `def run(args: Namespace) -> None` (L1577-1776)
- Brief: Handles the main initialization flow.
- Details: Validates input arguments, normalizes paths, and orchestrates resource generation per provider and artifact type. Requires at least one provider flag and at least one active artifact type among prompts, agents, and skills (skills are active unless --disable-skills is provided).
- Param: args Parsed CLI namespace; must contain provider flags (enable_claude, enable_codex, enable_gemini, enable_github, enable_kiro, enable_opencode) and artifact-type controls (enable_prompts, enable_agents, enable_skills where enable_skills is toggled by --disable-skills).

- var `VERBOSE = args.verbose` (L1583)
- Brief: Handles the main initialization flow.
- Details: Validates input arguments, normalizes paths, and orchestrates resource generation per provider and artifact type. Requires at least one provider flag and at least one active artifact type among prompts, agents, and skills (skills are active unless --disable-skills is provided).
- Param: args Parsed CLI namespace; must contain provider flags (enable_claude, enable_codex, enable_gemini, enable_github, enable_kiro, enable_opencode) and artifact-type controls (enable_prompts, enable_agents, enable_skills where enable_skills is toggled by --disable-skills).
- var `DEBUG = args.debug` (L1584)
- var `PROMPT = prompt_path.stem` (L2001)
### fn `def _format_install_table(` `priv` (L2585-2587)

### fn `def fmt(row: tuple[str, ...]) -> str` (L2618-2620)

- var `EXCLUDED_DIRS = frozenset({` (L2638)
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2647)
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2655-2675)
- Brief: Recursively collect source files from the given directories.
- Details: Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.

### fn `def _build_ascii_tree(paths: list[str]) -> str` `priv` (L2676-2713)
- Brief: Build a deterministic tree string from project-relative paths.
- Param: paths Project-relative file paths.
- Return: Rendered tree rooted at '.'.

### fn `def _emit(` `priv` (L2698-2700)

### fn `def _format_files_structure_markdown(files: list[str], project_base: Path) -> str` `priv` (L2714-2724)
- Brief: Format markdown section containing the scanned files tree.
- Param: files Absolute file paths selected for --references processing. project_base Project root used to normalize relative paths.
- Return: Markdown section with heading and fenced tree.

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2725-2743)
- Brief: Check if the parsed args contain a standalone file command.
- Details: Standalone commands require no `--base`/`--here`: `--files-tokens`, `--files-references`, `--files-compress`, `--files-find`, `--test-static-check`, and `--files-static-check`. SRS-253 adds `--files-static-check` to this group.
- Param: args Parsed CLI namespace.
- Return: True when any file-scope standalone flag is present.

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2744-2760)
- Brief: Check if the parsed args contain a project-scan command.
- Details: Project-scan commands: `--references`, `--compress`, `--tokens`, `--find`, and `--static-check`. SRS-257 adds `--static-check` to this group.
- Param: args Parsed CLI namespace.
- Return: True when any project-scan flag is present (requires `--base`/`--here`).

### fn `def run_files_tokens(files: list[str]) -> None` (L2761-2779)
- Brief: Execute --files-tokens: count tokens for arbitrary files.

### fn `def run_files_references(files: list[str]) -> None` (L2780-2792)
- Brief: Execute --files-references: generate markdown for arbitrary files.

### fn `def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None` (L2793-2809)
- Brief: Execute --files-compress: compress arbitrary files.
- Details: Renders output header paths relative to current working directory.
- Param: files List of source file paths to compress. enable_line_numbers If True, emits <n>: prefixes in compressed entries.

### fn `def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None` (L2810-2835)
- Brief: Execute --files-find: find constructs in arbitrary files.
- Param: args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...]. enable_line_numbers If True, emits <n>: prefixes in output.

### fn `def run_references(args: Namespace) -> None` (L2836-2849)
- Brief: Execute --references: generate markdown for project source files.

### fn `def run_compress_cmd(args: Namespace) -> None` (L2850-2868)
- Brief: Execute --compress: compress project source files.
- Param: args Parsed CLI arguments namespace.

### fn `def run_find(args: Namespace) -> None` (L2869-2895)
- Brief: Execute --find: find constructs in project source files.
- Param: args Parsed CLI arguments namespace.
- Throws: ReqError If no source files found or no constructs match criteria with available TAGs listing.

### fn `def run_tokens(args: Namespace) -> None` (L2896-2918)
- Brief: Execute --tokens: count tokens for files directly in --docs-dir.
- Details: Requires --base/--here and --docs-dir, then delegates reporting to run_files_tokens.
- Param: args Parsed CLI arguments namespace.

### fn `def run_files_static_check_cmd(files: list[str], args: Namespace) -> int` (L2919-2985)
- Brief: Execute `--files-static-check`: run static analysis on an explicit file list.
- Details: Project-base resolution order: 1. `--base PATH` -> use PATH. 2. `--here` -> use CWD. 3. Fallback -> use CWD. If `.req/config.json` is not found at the resolved project base, emits a warning to stderr and returns 0 (SRS-254). For each file: - Resolves absolute path; skips with warning if not a regular file. - Detects language via `STATIC_CHECK_EXT_TO_LANG` keyed on the lowercase extension. - Looks up language in the `"static-check"` config section; skips silently if absent. - Executes each configured language entry sequentially via `dispatch_static_check_for_file(filepath, lang_config)`. Overall exit code: max of all per-file codes (0=all pass, 1=any fail). (SRS-253, SRS-255)
- Param: files List of raw file paths supplied by the user. args Parsed CLI namespace; `--here`/`--base` are used to locate config.json.
- Return: Exit code: 0 if all checked files pass (or none are checked), 1 if any fail.
- See: SRS-253, SRS-254, SRS-255

### fn `def run_project_static_check_cmd(args: Namespace) -> int` (L2986-3031)
- Brief: Execute `--static-check`: run static analysis on all project source files.
- Details: Uses the same file-collection logic as `--references` and `--compress` (SRS-177, SRS-179, SRS-180, SRS-181): collects files from configured `src-dir` directories, applies `EXCLUDED_DIRS` filtering and `SUPPORTED_EXTENSIONS` matching. For each collected file: - Detects language via `STATIC_CHECK_EXT_TO_LANG` keyed on lowercase extension. - Looks up language in the `"static-check"` section of `.req/config.json`. - Skips silently when no tool is configured for the file's language. - Executes each configured language entry sequentially via `dispatch_static_check_for_file(filepath, lang_config)`. Overall exit code: max of all per-file codes (0=all pass, 1=any fail). (SRS-256, SRS-257)
- Param: args Parsed CLI namespace; `--base`/`--here` required.
- Return: Exit code: 0 if all checked files pass (or none are checked), 1 if any fail.
- Throws: ReqError If `--base`/`--here` is missing or no source files are found.
- See: SRS-256, SRS-257

### fn `def _resolve_project_base(args: Namespace) -> Path` `priv` (L3032-3052)
- Brief: Resolve project base path for project-level commands.
- Param: args Parsed CLI arguments namespace.
- Return: Absolute path of project base.
- Throws: ReqError If --base/--here is missing or the resolved path does not exist.

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L3053-3099)
- Brief: Resolve project base and src-dirs for --references/--compress.

### fn `def main(argv: Optional[list[str]] = None) -> int` (L3100-3175)
- Brief: CLI entry point for console_scripts and `-m` execution.
- Details: Returns an exit code (0 success, non-zero on error).

- var `VERBOSE = getattr(args, "verbose", False)` (L3119)
- var `DEBUG = getattr(args, "debug", False)` (L3120)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|25||
|`RESOURCE_ROOT`|var|pub|28||
|`VERBOSE`|var|pub|31||
|`DEBUG`|var|pub|34||
|`REQUIREMENTS_TEMPLATE_NAME`|var|pub|37||
|`PERSISTED_UPDATE_FLAG_KEYS`|var|pub|40||
|`ReqError`|class|pub|59-72|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|63-72|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|73-79|def log(msg: str) -> None|
|`dlog`|fn|pub|80-87|def dlog(msg: str) -> None|
|`vlog`|fn|pub|88-95|def vlog(msg: str) -> None|
|`_get_available_tags_help`|fn|priv|96-107|def _get_available_tags_help() -> str|
|`build_parser`|fn|pub|108-307|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|364-371|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|372-384|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|385-395|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|396-419|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|420-440|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|441-451|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|452-476|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|477-493|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|494-535|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|536-555|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|556-575|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|576-595|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|596-635|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|636-649|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|650-659|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|660-661|def compute_sub_path(|
|`save_config`|fn|pub|680-687|def save_config(|
|`load_config`|fn|pub|718-758|def load_config(project_base: Path) -> dict[str, str | li...|
|`load_static_check_from_config`|fn|pub|759-790|def load_static_check_from_config(project_base: Path) -> ...|
|`build_persisted_update_flags`|fn|pub|791-813|def build_persisted_update_flags(args: Namespace) -> dict...|
|`load_persisted_update_flags`|fn|pub|814-838|def load_persisted_update_flags(project_base: Path) -> di...|
|`generate_guidelines_file_list`|fn|pub|839-866|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|867-895|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`upgrade_guidelines_templates`|fn|pub|896-897|def upgrade_guidelines_templates(|
|`make_relative_token`|fn|pub|929-940|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|941-950|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|951-958|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|959-965|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|966-967|def copy_with_replacements(|
|`normalize_description`|fn|pub|976-986|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|987-1015|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|1016-1025|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|1026-1034|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|1035-1043|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|1044-1064|def extract_purpose_first_bullet(body: str) -> str|
|`_extract_section_text`|fn|priv|1065-1092|def _extract_section_text(body: str, section_name: str) -...|
|`extract_skill_description`|fn|pub|1093-1111|def extract_skill_description(frontmatter: str) -> str|
|`json_escape`|fn|pub|1112-1117|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|1118-1121|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|1141-1150|def render_kiro_agent(|
|`replace_tokens`|fn|pub|1184-1192|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|1193-1198|def yaml_double_quote_escape(value: str) -> str|
|`list_docs_templates`|fn|pub|1199-1214|def list_docs_templates() -> list[Path]|
|`find_requirements_template`|fn|pub|1215-1229|def find_requirements_template(docs_templates: list[Path]...|
|`load_kiro_template`|fn|pub|1230-1264|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|1265-1285|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|1286-1297|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|1298-1301|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|1345-1346|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1381-1398|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1399-1406|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1407-1417|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1418-1426|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1427-1437|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1438-1447|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1448-1457|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1458-1469|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1470-1483|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1484-1529|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1530-1576|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1577-1776|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1583||
|`DEBUG`|var|pub|1584||
|`PROMPT`|var|pub|2001||
|`_format_install_table`|fn|priv|2585-2587|def _format_install_table(|
|`fmt`|fn|pub|2618-2620|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|2638||
|`SUPPORTED_EXTENSIONS`|var|pub|2647||
|`_collect_source_files`|fn|priv|2655-2675|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_build_ascii_tree`|fn|priv|2676-2713|def _build_ascii_tree(paths: list[str]) -> str|
|`_emit`|fn|priv|2698-2700|def _emit(|
|`_format_files_structure_markdown`|fn|priv|2714-2724|def _format_files_structure_markdown(files: list[str], pr...|
|`_is_standalone_command`|fn|priv|2725-2743|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2744-2760|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2761-2779|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2780-2792|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2793-2809|def run_files_compress(files: list[str], enable_line_numb...|
|`run_files_find`|fn|pub|2810-2835|def run_files_find(args_list: list[str], enable_line_numb...|
|`run_references`|fn|pub|2836-2849|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2850-2868|def run_compress_cmd(args: Namespace) -> None|
|`run_find`|fn|pub|2869-2895|def run_find(args: Namespace) -> None|
|`run_tokens`|fn|pub|2896-2918|def run_tokens(args: Namespace) -> None|
|`run_files_static_check_cmd`|fn|pub|2919-2985|def run_files_static_check_cmd(files: list[str], args: Na...|
|`run_project_static_check_cmd`|fn|pub|2986-3031|def run_project_static_check_cmd(args: Namespace) -> int|
|`_resolve_project_base`|fn|priv|3032-3052|def _resolve_project_base(args: Namespace) -> Path|
|`_resolve_project_src_dirs`|fn|priv|3053-3099|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|3100-3175|def main(argv: Optional[list[str]] = None) -> int|
|`VERBOSE`|var|pub|3119||
|`DEBUG`|var|pub|3120||


---

# compress.py | Python | 385L | 11 symbols | 4 imports | 41 comments
> Path: `src/usereq/compress.py`

## Imports
```
import os
import sys
from .source_analyzer import build_language_specs
import argparse
```

## Definitions

- var `EXT_LANG_MAP = {` (L16)
- var `INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}` (L28)
### fn `def _get_specs()` `priv` (L35-45)
- Brief: Return cached language specifications, initializing once.
- Details: If cache is empty, calls `build_language_specs()` to populate it.
- Return: Dictionary mapping normalized language keys to language specs.

### fn `def detect_language(filepath: str) -> str | None` (L46-55)
- Brief: Detect language key from file extension.
- Details: Uses `EXT_LANG_MAP` for lookup. Case-insensitive extension matching.
- Param: filepath Source file path.
- Return: Normalized language key, or None when extension is unsupported.

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L56-97)
- Brief: Check if position `pos` in `line` is inside a string literal.
- Details: iterates through the line handling escaped delimiters.
- Param: line The code line string. pos The character index to check. string_delimiters Tuple of string delimiter characters/sequences.
- Return: True if `pos` is inside a string, False otherwise.

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L98-141)
- Brief: Remove trailing single-line comment from a code line.
- Details: Respects string literals; does not remove comments inside strings.
- Param: line The code line string. single_comment The single-line comment marker (e.g., "//", "#"). string_delimiters Tuple of string delimiters to respect.
- Return: The line content before the comment starts.

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L142-153)
- Brief: Check if a line is a standalone Python docstring (triple-quote only).
- Param: line The code line string.
- Return: True if the line appears to be a standalone triple-quoted string.

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L154-165)
- Brief: Format compressed entries, optionally prefixing original line numbers.
- Param: entries List of tuples (line_number, text). include_line_numbers Boolean flag to enable line prefixes.
- Return: Formatted string.

### fn `def compress_source(source: str, language: str,` (L166-333)
- Brief: Compress source code by removing comments, blank lines, and extra whitespace.
- Details: Preserves indentation for indent-significant languages (Python, Haskell, Elixir).
- Param: source The source code string. language Language identifier (e.g. "python", "javascript"). include_line_numbers If True (default), prefix each line with <n>: format.
- Return: Compressed source code string.
- Throws: ValueError If language is unsupported.

### fn `def compress_file(filepath: str, language: str | None = None,` (L334-355)
- Brief: Compress a source file by removing comments and extra whitespace.
- Param: filepath Path to the source file. language Optional language override. Auto-detected if None. include_line_numbers If True (default), prefix each line with <n>: format.
- Return: Compressed source code string.
- Throws: ValueError If language cannot be detected.

### fn `def main()` (L356-383)
- Brief: Execute the standalone compression CLI.
- Details: Parses command-line arguments and invokes `compress_file`, printing the result to stdout or errors to stderr.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|16||
|`INDENT_SIGNIFICANT`|var|pub|28||
|`_get_specs`|fn|priv|35-45|def _get_specs()|
|`detect_language`|fn|pub|46-55|def detect_language(filepath: str) -> str | None|
|`_is_in_string`|fn|priv|56-97|def _is_in_string(line: str, pos: int, string_delimiters:...|
|`_remove_inline_comment`|fn|priv|98-141|def _remove_inline_comment(line: str, single_comment: str,|
|`_is_python_docstring_line`|fn|priv|142-153|def _is_python_docstring_line(line: str) -> bool|
|`_format_result`|fn|priv|154-165|def _format_result(entries: list[tuple[int, str]],|
|`compress_source`|fn|pub|166-333|def compress_source(source: str, language: str,|
|`compress_file`|fn|pub|334-355|def compress_file(filepath: str, language: str | None = N...|
|`main`|fn|pub|356-383|def main()|


---

# compress_files.py | Python | 130L | 4 symbols | 5 imports | 6 comments
> Path: `src/usereq/compress_files.py`

## Imports
```
import os
import sys
from pathlib import Path
from .compress import compress_file, detect_language
import argparse
```

## Definitions

### fn `def _extract_line_range(compressed_with_line_numbers: str) -> tuple[int, int]` `priv` (L17-34)
- Brief: Extract source line interval from compressed output with <n>: prefixes.
- Details: Parses the first token of each line as an integer line number.
- Param: compressed_with_line_numbers Compressed payload generated with include_line_numbers=True.
- Return: Tuple (line_start, line_end) derived from preserved <n>: prefixes; returns (0, 0) when no prefixed lines exist.

### fn `def _format_output_path(filepath: str, output_base: Path | None) -> str` `priv` (L35-46)
- Brief: Build the header-visible path for one compressed source file.
- Param: filepath Absolute or relative source file path. output_base Project-home base used to relativize output paths.
- Return: Original filepath when output_base is None; otherwise POSIX relative path from output_base.

### fn `def compress_files(filepaths: list[str],` (L47-107)
- Brief: Compress multiple source files and concatenate with identifying headers.
- Details: Each file is compressed and emitted as: header line `@@@ <path> | <lang>`, line-range metadata `- Lines: <start>-<end>`, and fenced code block delimited by triple backticks. Line range is derived from the already computed <n>: prefixes to preserve existing numbering logic. Files are separated by a blank line.
- Param: filepaths List of source file paths. include_line_numbers If True (default), keep <n>: prefixes in code block lines. verbose If True, emits progress status messages on stderr. output_base Project-home base used to render header paths as relative paths.
- Return: Concatenated compressed output string.
- Throws: ValueError If no files could be processed.

### fn `def main()` (L108-128)
- Brief: Execute the multi-file compression CLI command.
- Details: Parses command-line arguments, calls `compress_files`, and prints output or errors.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_extract_line_range`|fn|priv|17-34|def _extract_line_range(compressed_with_line_numbers: str...|
|`_format_output_path`|fn|priv|35-46|def _format_output_path(filepath: str, output_base: Path ...|
|`compress_files`|fn|pub|47-107|def compress_files(filepaths: list[str],|
|`main`|fn|pub|108-128|def main()|


---

# doxygen_parser.py | Python | 163L | 5 symbols | 2 imports | 19 comments
> Path: `src/usereq/doxygen_parser.py`

## Imports
```
import re
from typing import Dict, List
```

## Definitions

- var `DOXYGEN_TAGS = [` (L15)
### fn `def parse_doxygen_comment(comment_text: str) -> Dict[str, List[str]]` (L35-91)
- Brief: Extract Doxygen fields from a documentation comment block.
- Details: Parses both @tag and \\tag syntax. Each tag's content extends until the next tag or end of comment. Multiple occurrences of the same tag accumulate in the returned list. Whitespace is normalized.
- Param: comment_text Raw comment string potentially containing Doxygen tags.
- Return: Dictionary mapping normalized tag names to lists of extracted content strings.
- Note: Returns empty dict if no Doxygen tags are found.
- See: DOXYGEN_TAGS for recognized tag list.

### fn `def _strip_comment_delimiters(text: str) -> str` `priv` (L92-120)
- Brief: Remove common comment delimiters from text block.
- Details: Strips leading/trailing /**, */, //, #, triple quotes, and intermediate * column markers. Preserves content while removing comment syntax artifacts.
- Param: text Raw comment block possibly containing comment delimiters.
- Return: Cleaned text with delimiters removed.

### fn `def _normalize_whitespace(text: str) -> str` `priv` (L121-146)
- Brief: Normalize internal whitespace in extracted tag content.
- Details: Collapses multiple spaces to single space, preserves single newlines, removes redundant blank lines.
- Param: text Tag content with potentially irregular whitespace.
- Return: Whitespace-normalized content.

### fn `def format_doxygen_fields_as_markdown(doxygen_fields: Dict[str, List[str]]) -> List[str]` (L147-163)
- Brief: Format extracted Doxygen fields as Markdown bulleted list.
- Details: Emits fields in fixed order (DOXYGEN_TAGS), capitalizes tag, omits @ prefix, appends ':'. Skips tags not present in input. Each tag's content items are concatenated.
- Param: doxygen_fields Dictionary of tag -> content list from parse_doxygen_comment().
- Return: List of Markdown lines (each starting with '- ').
- Note: Output order matches DOXYGEN_TAGS sequence.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`DOXYGEN_TAGS`|var|pub|15||
|`parse_doxygen_comment`|fn|pub|35-91|def parse_doxygen_comment(comment_text: str) -> Dict[str,...|
|`_strip_comment_delimiters`|fn|priv|92-120|def _strip_comment_delimiters(text: str) -> str|
|`_normalize_whitespace`|fn|priv|121-146|def _normalize_whitespace(text: str) -> str|
|`format_doxygen_fields_as_markdown`|fn|pub|147-163|def format_doxygen_fields_as_markdown(doxygen_fields: Dic...|


---

# find_constructs.py | Python | 356L | 11 symbols | 7 imports | 18 comments
> Path: `src/usereq/find_constructs.py`

## Imports
```
import os
import re
import sys
from .doxygen_parser import format_doxygen_fields_as_markdown, parse_doxygen_comment
from .source_analyzer import SourceAnalyzer
from .compress import compress_source, detect_language
import argparse
```

## Definitions

- var `LANGUAGE_TAGS = {` (L20)
### fn `def format_available_tags() -> str` (L44-57)
- Brief: Generate formatted list of available TAGs per language.
- Details: Iterates LANGUAGE_TAGS dictionary, formats each entry as "- Language: TAG1, TAG2, ..." with language capitalized and tags alphabetically sorted and comma-separated.
- Return: Multi-line string listing each language with its supported TAGs.

### fn `def parse_tag_filter(tag_string: str) -> set[str]` (L58-66)
- Brief: Parse pipe-separated tag filter into a normalized set.
- Details: Splits the input string by pipe character `|` and strips whitespace from each component.
- Param: tag_string Raw tag filter string (e.g., "CLASS|FUNCTION").
- Return: Set of uppercase tag identifiers.

### fn `def language_supports_tags(lang: str, tag_set: set[str]) -> bool` (L67-77)
- Brief: Check if the language supports at least one of the requested tags.
- Details: Lookups the language in `LANGUAGE_TAGS` and checks if any of `tag_set` exists in the supported tags.
- Param: lang Normalized language identifier. tag_set Set of requested TAG identifiers.
- Return: True if intersection is non-empty, False otherwise.

### fn `def construct_matches(element, tag_set: set[str], pattern: str) -> bool` (L78-95)
- Brief: Check if a source element matches tag filter and regex pattern.
- Details: Validates the element type and then applies the regex search on the element name.
- Param: element SourceElement instance from analyzer. tag_set Set of requested TAG identifiers. pattern Regex pattern string to test against element name.
- Return: True if element type is in tag_set and name matches pattern.

### fn `def _merge_doxygen_fields(` `priv` (L96-98)

### fn `def _extract_construct_doxygen_fields(element) -> dict[str, list[str]]` `priv` (L113-135)
- Brief: Build aggregate Doxygen fields for one construct.
- Details: Aggregates fields from two sources: pre-associated element.doxygen_fields and all comment snippets extracted from element.body_comments. Each comment snippet is parsed with parse_doxygen_comment() and merged in discovery order.
- Param: element SourceElement instance potentially enriched with doxygen_fields and body_comments.
- Return: Dictionary tag->list preserving tag content insertion order.

### fn `def _strip_construct_comments(` `priv` (L136-140)

### fn `def format_construct(` (L176-180)

### fn `def find_constructs_in_files(` (L218-223)

### fn `def main()` (L319-354)
- Brief: Execute the construct finding CLI command.
- Details: Parses arguments and calls find_constructs_in_files. Handles exceptions by printing errors to stderr.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`LANGUAGE_TAGS`|var|pub|20||
|`format_available_tags`|fn|pub|44-57|def format_available_tags() -> str|
|`parse_tag_filter`|fn|pub|58-66|def parse_tag_filter(tag_string: str) -> set[str]|
|`language_supports_tags`|fn|pub|67-77|def language_supports_tags(lang: str, tag_set: set[str]) ...|
|`construct_matches`|fn|pub|78-95|def construct_matches(element, tag_set: set[str], pattern...|
|`_merge_doxygen_fields`|fn|priv|96-98|def _merge_doxygen_fields(|
|`_extract_construct_doxygen_fields`|fn|priv|113-135|def _extract_construct_doxygen_fields(element) -> dict[st...|
|`_strip_construct_comments`|fn|priv|136-140|def _strip_construct_comments(|
|`format_construct`|fn|pub|176-180|def format_construct(|
|`find_constructs_in_files`|fn|pub|218-223|def find_constructs_in_files(|
|`main`|fn|pub|319-354|def main()|


---

# generate_markdown.py | Python | 153L | 5 symbols | 4 imports | 8 comments
> Path: `src/usereq/generate_markdown.py`

## Imports
```
import os
import sys
from pathlib import Path
from .source_analyzer import SourceAnalyzer, format_markdown
```

## Definitions

- var `EXT_LANG_MAP = {` (L17)
### fn `def detect_language(filepath: str) -> str | None` (L44-53)
- Brief: Detect language from file extension.
- Details: Uses EXT_LANG_MAP for extension lookup (case-insensitive).
- Param: filepath Path to the source file.
- Return: Language identifier string or None if unknown.

### fn `def _format_output_path(filepath: str, output_base: Path | None) -> str` `priv` (L54-65)
- Brief: Build the markdown-visible path for one source file.
- Param: filepath Absolute or relative source file path. output_base Project-home base used to relativize output paths.
- Return: Original filepath when output_base is None; otherwise POSIX relative path from output_base.

### fn `def generate_markdown(` (L66-69)

### fn `def main()` (L135-151)
- Brief: Execute the standalone markdown generation CLI command.
- Details: Expects file paths as command-line arguments. Prints generated markdown to stdout.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|17||
|`detect_language`|fn|pub|44-53|def detect_language(filepath: str) -> str | None|
|`_format_output_path`|fn|priv|54-65|def _format_output_path(filepath: str, output_base: Path ...|
|`generate_markdown`|fn|pub|66-69|def generate_markdown(|
|`main`|fn|pub|135-151|def main()|


---

# source_analyzer.py | Python | 2060L | 59 symbols | 11 imports | 130 comments
> Path: `src/usereq/source_analyzer.py`

## Imports
```
import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from .doxygen_parser import parse_doxygen_comment
from usereq.doxygen_parser import parse_doxygen_comment
from .doxygen_parser import format_doxygen_fields_as_markdown
from usereq.doxygen_parser import format_doxygen_fields_as_markdown
```

## Definitions

### class `class ElementType(Enum)` : Enum (L24-54)
- Brief: Element types recognized in source code.
- Details: Enumeration of all supported syntactic constructs across languages.
- var `FUNCTION = auto()` (L28)
  - Brief: Element types recognized in source code.
  - Details: Enumeration of all supported syntactic constructs across languages.
- var `METHOD = auto()` (L29)
  - Brief: Element types recognized in source code.
  - Details: Enumeration of all supported syntactic constructs across languages.
- var `CLASS = auto()` (L30)
- var `STRUCT = auto()` (L31)
- var `ENUM = auto()` (L32)
- var `TRAIT = auto()` (L33)
- var `INTERFACE = auto()` (L34)
- var `MODULE = auto()` (L35)
- var `IMPL = auto()` (L36)
- var `MACRO = auto()` (L37)
- var `CONSTANT = auto()` (L38)
- var `VARIABLE = auto()` (L39)
- var `TYPE_ALIAS = auto()` (L40)
- var `IMPORT = auto()` (L41)
- var `DECORATOR = auto()` (L42)
- var `COMMENT_SINGLE = auto()` (L43)
- var `COMMENT_MULTI = auto()` (L44)
- var `COMPONENT = auto()` (L45)
- var `PROTOCOL = auto()` (L46)
- var `EXTENSION = auto()` (L47)
- var `UNION = auto()` (L48)
- var `NAMESPACE = auto()` (L49)
- var `PROPERTY = auto()` (L50)
- var `SIGNAL = auto()` (L51)
- var `TYPEDEF = auto()` (L52)

### class `class SourceElement` `@dataclass` (L56-109)
- Brief: Element found in source file. Return the normalized printable label for element_type.
- Details: Data class representing a single extracted code construct with its metadata. Maps internal ElementType enum to a string representation for reporting.
- Return: Stable uppercase label used in markdown rendering output.
- fn `def type_label(self) -> str` (L75-109)
  - Brief: Return the normalized printable label for element_type.
  - Details: Maps internal ElementType enum to a string representation for reporting.
  - Return: Stable uppercase label used in markdown rendering output.

### class `class LanguageSpec` `@dataclass` (L111-122)
- Brief: Language recognition pattern specification.
- Details: Holds regex patterns and configuration for parsing a specific programming language.

### fn `def build_language_specs() -> dict` (L123-322)
- Brief: Build specifications for all supported languages.

### class `class SourceAnalyzer` (L676-875)
- Brief: Multi-language source file analyzer. Initialize analyzer state with language specifications. Return list of supported languages (without aliases). Analyze a source file and return the list of SourceElement found. Check if position pos is inside a string literal.
- Details: Analyzes a source file identifying definitions, comments and constructs for the specified language. Produces structured output with line numbers, inspired by tree-sitter tags functionality. Reads file content, detects single/multi-line comments, and matches regex patterns for definitions.
- Param: filepath Path to the source file. language Language identifier. line The line of code. pos The column index. spec The LanguageSpec instance.
- Return: Sorted list of unique language identifiers. List of SourceElement instances. True if pos is within a string.
- Throws: ValueError If language is not supported.
- fn `def __init__(self)` `priv` (L681-684)
  - Brief: Multi-language source file analyzer. Initialize analyzer state with language specifications.
  - Details: Analyzes a source file identifying definitions, comments and constructs for the specified language. Produces structured output with line numbers, inspired by tree-sitter tags functionality.
- fn `def get_supported_languages(self) -> list` (L685-696)
  - Brief: Return list of supported languages (without aliases).
  - Return: Sorted list of unique language identifiers.
- fn `def analyze(self, filepath: str, language: str) -> list` (L697-850)
  - Brief: Analyze a source file and return the list of SourceElement found.
  - Details: Reads file content, detects single/multi-line comments, and matches regex patterns for definitions.
  - Param: filepath Path to the source file. language Language identifier.
  - Return: List of SourceElement instances.
  - Throws: ValueError If language is not supported.

### fn `def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool` `priv` (L851-884)
- Brief: Check if position pos is inside a string literal.
- Param: line The line of code. pos The column index. spec The LanguageSpec instance.
- Return: True if pos is within a string.

### fn `def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]` `priv` (L885-922)
- Brief: Find position of single-line comment, ignoring strings.
- Param: line The line of code. spec The LanguageSpec instance.
- Return: Column index of comment start, or None.

### fn `def _find_block_end(self, lines: list, start_idx: int,` `priv` (L923-1001)
- Brief: Find the end of a block (function, class, struct, etc.).
- Details: Returns the index (1-based) of the final line of the block. Limits search for performance.
- Param: lines List of all file lines. start_idx Index of the start line. language Language identifier. first_line Content of the start line.
- Return: 1-based index of the end line.

### fn `def enrich(self, elements: list, language: str,` (L1004-1019)
- Brief: Enrich elements with signatures, hierarchy, visibility, inheritance.
- Details: Call after analyze() to add metadata for LLM-optimized markdown output. Modifies elements in-place and returns them. If filepath is provided, also extracts body comments and exit points.

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L1020-1044)
- Brief: Extract clean identifiers from name fields.
- Details: Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1045-1060)
- Brief: Extract clean signatures from element extracts.

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1061-1094)
- Brief: Detect parent-child relationships between elements.
- Details: Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1095-1107)
- Brief: Extract visibility/access modifiers from elements.

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1108-1153)
- Brief: Parse visibility modifier from a signature line.

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1154-1165)
- Brief: Extract inheritance/implementation info from class-like elements.

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1166-1195)
- Brief: Parse inheritance info from a class/struct declaration line.

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1203-1326)
- Brief: Extract comments and exit points from within function/class bodies.
- Details: Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.

### fn `def _extract_doxygen_fields(self, elements: list)` `priv` (L1327-1386)
- Brief: Extract Doxygen tag fields from associated documentation comments.
- Details: For each non-comment element, resolves the nearest associated documentation comment using language-agnostic adjacency rules: same-line postfix comment (`//!<`, `#!<`, `/**<`), nearest preceding standalone comment block within two lines, or nearest following postfix standalone comment within two lines. Parses the resolved comment via parse_doxygen_comment() and stores the extracted fields in element.doxygen_fields.

### fn `def _is_postfix_doxygen_comment(comment_text: str) -> bool` `priv` `@staticmethod` (L1388-1397)
- Brief: Detect whether a comment uses postfix Doxygen association markers.
- Details: Returns True for comment prefixes that explicitly bind documentation to a preceding construct, including variants like `#!<`, `//!<`, `///<`, `/*!<`, and `/**<`.
- Param: comment_text Raw extracted comment text.
- Return: True when the comment text starts with a supported postfix marker; otherwise False.

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1399-1410)
- Brief: Strip comment markers from a single line of comment text.

### fn `def _md_loc(elem) -> str` `priv` (L1411-1418)
- Brief: Format element location compactly for markdown.

### fn `def _md_kind(elem) -> str` `priv` (L1419-1446)
- Brief: Short kind label for markdown output.

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1447-1469)
- Brief: Extract clean text content from a comment element.
- Details: Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1470-1486)
- Brief: Extract clean text lines from a multi-line comment (preserving structure).

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1487-1547)
- Brief: Build maps that associate comments with their adjacent definitions.
- Details: Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1548-1599)
- Brief: Render body comments and exit points for a definition element.
- Details: Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.

### fn `def _merge_doxygen_fields(` `priv` (L1600-1602)

### fn `def _collect_element_doxygen_fields(elem) -> dict[str, list[str]]` `priv` (L1616-1637)
- Brief: Aggregate construct Doxygen fields from associated and body comments.
- Details: Parses each body-comment tuple with parse_doxygen_comment() and merges results after pre-associated fields so references output can represent both association styles.
- Param: elem SourceElement containing optional `doxygen_fields` and `body_comments`.
- Return: Dictionary of normalized Doxygen tags to ordered value lists.

### fn `def format_markdown(` (L1638-1644)

### fn `def main()` (L1935-2058)
- Brief: Execute the standalone source analyzer CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ElementType`|class|pub|24-54|class ElementType(Enum)|
|`ElementType.FUNCTION`|var|pub|28||
|`ElementType.METHOD`|var|pub|29||
|`ElementType.CLASS`|var|pub|30||
|`ElementType.STRUCT`|var|pub|31||
|`ElementType.ENUM`|var|pub|32||
|`ElementType.TRAIT`|var|pub|33||
|`ElementType.INTERFACE`|var|pub|34||
|`ElementType.MODULE`|var|pub|35||
|`ElementType.IMPL`|var|pub|36||
|`ElementType.MACRO`|var|pub|37||
|`ElementType.CONSTANT`|var|pub|38||
|`ElementType.VARIABLE`|var|pub|39||
|`ElementType.TYPE_ALIAS`|var|pub|40||
|`ElementType.IMPORT`|var|pub|41||
|`ElementType.DECORATOR`|var|pub|42||
|`ElementType.COMMENT_SINGLE`|var|pub|43||
|`ElementType.COMMENT_MULTI`|var|pub|44||
|`ElementType.COMPONENT`|var|pub|45||
|`ElementType.PROTOCOL`|var|pub|46||
|`ElementType.EXTENSION`|var|pub|47||
|`ElementType.UNION`|var|pub|48||
|`ElementType.NAMESPACE`|var|pub|49||
|`ElementType.PROPERTY`|var|pub|50||
|`ElementType.SIGNAL`|var|pub|51||
|`ElementType.TYPEDEF`|var|pub|52||
|`SourceElement`|class|pub|56-109|class SourceElement|
|`SourceElement.type_label`|fn|pub|75-109|def type_label(self) -> str|
|`LanguageSpec`|class|pub|111-122|class LanguageSpec|
|`build_language_specs`|fn|pub|123-322|def build_language_specs() -> dict|
|`SourceAnalyzer`|class|pub|676-875|class SourceAnalyzer|
|`SourceAnalyzer.__init__`|fn|priv|681-684|def __init__(self)|
|`SourceAnalyzer.get_supported_languages`|fn|pub|685-696|def get_supported_languages(self) -> list|
|`SourceAnalyzer.analyze`|fn|pub|697-850|def analyze(self, filepath: str, language: str) -> list|
|`_in_string_context`|fn|priv|851-884|def _in_string_context(self, line: str, pos: int, spec: L...|
|`_find_comment`|fn|priv|885-922|def _find_comment(self, line: str, spec: LanguageSpec) ->...|
|`_find_block_end`|fn|priv|923-1001|def _find_block_end(self, lines: list, start_idx: int,|
|`enrich`|fn|pub|1004-1019|def enrich(self, elements: list, language: str,|
|`_clean_names`|fn|priv|1020-1044|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1045-1060|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1061-1094|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1095-1107|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1108-1153|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1154-1165|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1166-1195|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1203-1326|def _extract_body_annotations(self, elements: list,|
|`_extract_doxygen_fields`|fn|priv|1327-1386|def _extract_doxygen_fields(self, elements: list)|
|`_is_postfix_doxygen_comment`|fn|priv|1388-1397|def _is_postfix_doxygen_comment(comment_text: str) -> bool|
|`_clean_comment_line`|fn|priv|1399-1410|def _clean_comment_line(text: str, spec) -> str|
|`_md_loc`|fn|priv|1411-1418|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1419-1446|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1447-1469|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1470-1486|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1487-1547|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1548-1599|def _render_body_annotations(out: list, elem, indent: str...|
|`_merge_doxygen_fields`|fn|priv|1600-1602|def _merge_doxygen_fields(|
|`_collect_element_doxygen_fields`|fn|priv|1616-1637|def _collect_element_doxygen_fields(elem) -> dict[str, li...|
|`format_markdown`|fn|pub|1638-1644|def format_markdown(|
|`main`|fn|pub|1935-2058|def main()|


---

# static_check.py | Python | 663L | 20 symbols | 8 imports | 58 comments
> Path: `src/usereq/static_check.py`

## Imports
```
from __future__ import annotations
import glob
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence
from .cli import ReqError
```

## Definitions

### fn `def _split_csv_like_tokens(spec_rhs: str) -> list[str]` `priv` (L111-145)
- Brief: Split a comma-separated SPEC right-hand side with quote-aware token boundaries.
- Details: - Supported quote delimiters: single quote `'` and double quote `"`. - Commas split tokens only when parser is outside a quoted segment. - Quote delimiters are not included in output tokens. - Leading and trailing whitespace for each token is stripped.
- Param: spec_rhs Text after `LANG=` in `--enable-static-check`.
- Return: Token list where commas inside `'...'` or `"..."` do not split tokens.
- See: SRS-260, SRS-250

### fn `def parse_enable_static_check(spec: str) -> tuple[str, dict]` (L146-222)
- Brief: Parse a single `--enable-static-check` SPEC string into a (lang, config_dict) pair.
- Details: Parse steps: 1. Split on the first `=`; left side is LANG token, right side is `MODULE[,...]`. 2. Normalize LANG via `STATIC_CHECK_LANG_CANONICAL` (case-insensitive). 3. Parse right side as comma-separated tokens; first token is MODULE (case-insensitive, validated against `_CANONICAL_MODULES`). 4. For Command: next token is `cmd` (mandatory); all subsequent tokens are `params`. 5. For all other modules: all tokens after MODULE are `params`. 6. `params` key is omitted when the list is empty. 7. `cmd` key is omitted for non-Command modules. 8. Surrounding quote delimiters (`'` or `"`) are stripped from parsed tokens. Note: PARAM values containing `,` must be wrapped with `'` or `"` in SPEC.
- Param: spec Raw SPEC string in the format `LANG=MODULE[,CMD[,PARAM...]]`.
- Return: Tuple `(canonical_lang, config_dict)` where `config_dict` contains `"module"` and optionally `"cmd"` (Command only) and `"params"` (non-empty list only).
- Throws: ReqError If `=` separator is absent, language is unknown, or module is unknown.
- See: SRS-260, SRS-248, SRS-249, SRS-250

### fn `def dispatch_static_check_for_file(filepath: str, lang_config: dict) -> int` (L227-272)
- Brief: Dispatch static-check for a single file based on a language config dict.
- Details: Module dispatch table: - `"Dummy"` (case-insensitive) -> `StaticCheckBase` - `"Pylance"` -> `StaticCheckPylance` - `"Ruff"` -> `StaticCheckRuff` - `"Command"` -> `StaticCheckCommand` (requires `"cmd"` key) Instantiates the checker with `inputs=[filepath]` and `extra_args=params`. Delegates actual check to `checker.run()`.
- Param: filepath Absolute path of the file to analyse. lang_config Dict with keys `"module"` (str), optional `"cmd"` (str, Command only), optional `"params"` (list[str]).
- Return: Exit code: 0 on pass, 1 on fail.
- Throws: ReqError If module is unknown, or Command module is missing `"cmd"`.
- See: SRS-261, SRS-253, SRS-256

### fn `def _resolve_files(inputs: Sequence[str]) -> List[str]` `priv` (L277-319)
- Brief: Resolve a mixed list of paths, glob patterns, and directories into regular files.
- Details: Resolution order per element: 1. If the element contains a glob wildcard character (`*`, `?`, `[`) expand via `glob.glob(entry, recursive=True)`, enabling full `**` recursive expansion (e.g., `src/**/*.py` matches all `.py` files under `src/` at any depth). 2. If the element is an existing directory, iterate direct children only (flat traversal). 3. Otherwise treat as a literal file path; include if it is a regular file. Symlinks to regular files are included. Non-existent paths that do not match a glob produce a warning on stderr and are skipped.
- Param: inputs Sequence of raw path strings (file, directory, or glob pattern).
- Return: Sorted deduplicated list of resolved absolute file paths (regular files only).

### class `class StaticCheckBase` (L324-414)
- Brief: Dummy static-check class; base of the static analysis class hierarchy. Initialize the static checker with resolved inputs and options. Execute the static check for all resolved files. Build the per-file header line for output. Perform the static analysis for a single file. Emit one markdown output line.
- Details: Iterates over resolved input files and emits a per-file header line plus `Result: OK`. Subclasses override `_check_file` to provide tool-specific logic. File resolution is delegated to `_resolve_files`. Resolves `inputs` immediately into `self._files` via `_resolve_files`. Recursive traversal is expressed via `**` glob patterns in `inputs` (e.g., `src/**/*.py`); no separate recursive flag exists (SRS-240, SRS-245). If the resolved file list is empty a warning is printed to stderr and 0 is returned. For each file `_check_file` is called; the overall return code is the maximum of all per-file return codes (0 = all OK, 1 = at least one FAIL). Format: `# Static-Check(<LABEL>): <filepath> [<extra_args>]`. When `extra_args` is empty the bracket section is omitted. Base implementation (Dummy): always prints the header and `Result: OK`. Subclasses override this method to invoke external tools. Emits `line` followed by a newline.
- Param: inputs Raw path/pattern/directory entries from CLI. extra_args Additional CLI arguments forwarded to the external tool (may be None). filepath Absolute path of the file being checked. filepath Absolute path of the file to check. line Line content to emit on stdout.
- Return: Exit code: 0 if all files pass (or file list is empty), 1 if any file fails. Formatted header string including label, filename, and extra args. 0 on pass, non-zero on failure.
- fn `def __init__(` `priv` (L335-338)
- fn `def run(self) -> int` (L355-378)
  - Brief: Execute the static check for all resolved files.
  - Details: If the resolved file list is empty a warning is printed to stderr and 0 is returned. For each file `_check_file` is called; the overall return code is the maximum of all per-file return codes (0 = all OK, 1 = at least one FAIL).
  - Return: Exit code: 0 if all files pass (or file list is empty), 1 if any file fails.
- fn `def _header_line(self, filepath: str) -> str` `priv` (L383-393)
  - Brief: Build the per-file header line for output.
  - Details: Format: `# Static-Check(<LABEL>): <filepath> [<extra_args>]`. When `extra_args` is empty the bracket section is omitted.
  - Param: filepath Absolute path of the file being checked.
  - Return: Formatted header string including label, filename, and extra args.
- fn `def _check_file(self, filepath: str) -> int` `priv` (L394-405)
  - Brief: Perform the static analysis for a single file.
  - Details: Base implementation (Dummy): always prints the header and `Result: OK`. Subclasses override this method to invoke external tools.
  - Param: filepath Absolute path of the file to check.
  - Return: 0 on pass, non-zero on failure.
- fn `def _emit_line(self, line: str) -> None` `priv` (L406-414)
  - Brief: Emit one markdown output line.
  - Details: Emits `line` followed by a newline.
  - Param: line Line content to emit on stdout.

### class `class StaticCheckPylance(StaticCheckBase)` : StaticCheckBase (L419-467)
- Brief: Pylance static-check class; runs pyright on each resolved file. Run pyright on `filepath` and emit OK or FAIL with evidence.
- Details: Derived from `StaticCheckBase`; overrides `_check_file` to invoke `pyright` as a subprocess and parse its exit code. Header label: `Pylance`. Evidence block is emitted on failure by concatenating stdout and stderr from pyright. Invokes `pyright <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
- Param: filepath Absolute path of the file to analyse with pyright.
- Return: 0 when pyright exits 0, 1 otherwise.
- Exception: ReqError Not raised; subprocess errors are surfaced as FAIL evidence.
- See: StaticCheckBase
- var `LABEL = "Pylance"` (L429)
  - Brief: Pylance static-check class; runs pyright on each resolved file.
  - Details: Derived from `StaticCheckBase`; overrides `_check_file` to invoke `pyright`
as a subprocess and parse its exit code.
...
- fn `def _check_file(self, filepath: str) -> int` `priv` (L431-467)
  - Brief: Run pyright on `filepath` and emit OK or FAIL with evidence.
  - Details: Invokes `pyright <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
  - Param: filepath Absolute path of the file to analyse with pyright.
  - Return: 0 when pyright exits 0, 1 otherwise.
  - Exception: ReqError Not raised; subprocess errors are surfaced as FAIL evidence.

### class `class StaticCheckRuff(StaticCheckBase)` : StaticCheckBase (L472-520)
- Brief: Ruff static-check class; runs `ruff check` on each resolved file. Run `ruff check` on `filepath` and emit OK or FAIL with evidence.
- Details: Derived from `StaticCheckBase`; overrides `_check_file` to invoke `ruff check` as a subprocess and parse its exit code. Header label: `Ruff`. Evidence block is emitted on failure by concatenating stdout and stderr from ruff. Invokes `ruff check <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
- Param: filepath Absolute path of the file to analyse with ruff.
- Return: 0 when ruff exits 0, 1 otherwise.
- Exception: ReqError Not raised; subprocess errors are surfaced as FAIL evidence.
- See: StaticCheckBase
- var `LABEL = "Ruff"` (L482)
  - Brief: Ruff static-check class; runs `ruff check` on each resolved file.
  - Details: Derived from `StaticCheckBase`; overrides `_check_file` to invoke `ruff check`
as a subprocess and parse its exit code.
...
- fn `def _check_file(self, filepath: str) -> int` `priv` (L484-520)
  - Brief: Run `ruff check` on `filepath` and emit OK or FAIL with evidence.
  - Details: Invokes `ruff check <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
  - Param: filepath Absolute path of the file to analyse with ruff.
  - Return: 0 when ruff exits 0, 1 otherwise.
  - Exception: ReqError Not raised; subprocess errors are surfaced as FAIL evidence.

### class `class StaticCheckCommand(StaticCheckBase)` : StaticCheckBase (L525-594)
- Brief: Command static-check class; runs an arbitrary external command on each resolved file. Initialize the command checker and verify tool availability. Run the external command on `filepath` and emit OK or FAIL with evidence.
- Details: Derived from `StaticCheckBase`; overrides `_check_file` to invoke the user-supplied `cmd` as a subprocess. Header label: `Command[<cmd>]`. Before processing files the constructor verifies that `cmd` is available on PATH via `shutil.which`; raises `ReqError(code=1)` if the command is not found. Calls `shutil.which(cmd)` before delegating to the parent constructor. Sets `LABEL` dynamically to `Command[<cmd>]`. Invokes `<cmd> <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
- Param: cmd External command name (must be available on PATH). inputs Raw path/pattern/directory entries from CLI. extra_args Additional CLI arguments forwarded to the external command. filepath Absolute path of the file to analyse.
- Return: 0 when the command exits 0, 1 otherwise.
- Throws: ReqError If `cmd` is not found on PATH (exit code 1).
- See: StaticCheckBase
- fn `def __init__(` `priv` (L536-540)
  - Brief: Command static-check class; runs an arbitrary external command on each resolved file.
  - Details: Derived from `StaticCheckBase`; overrides `_check_file` to invoke the user-supplied
`cmd` as a subprocess.
...
- fn `def _check_file(self, filepath: str) -> int` `priv` (L559-594)
  - Brief: Run the external command on `filepath` and emit OK or FAIL with evidence.
  - Details: Invokes `<cmd> <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
  - Param: filepath Absolute path of the file to analyse.
  - Return: 0 when the command exits 0, 1 otherwise.

### fn `def run_static_check(argv: Sequence[str]) -> int` (L599-663)
- Brief: Parse `--test-static-check` sub-argv and dispatch to the appropriate checker class.
- Details: Expected argument format: - `dummy [FILES...]` - `pylance [FILES...]` - `ruff [FILES...]` - `command <cmd> [FILES...]` No custom `--recursive` flag is parsed; recursive traversal is expressed via `**` glob patterns in `[FILES]` (e.g., `src/**/*.py`). For `command`, the first token after `command` is treated as `<cmd>`. All remaining tokens (after subcommand and optional cmd) are treated as FILES. Dispatches to: - `dummy` -> `StaticCheckBase` - `pylance` -> `StaticCheckPylance` - `ruff` -> `StaticCheckRuff` - `command` -> `StaticCheckCommand`
- Param: argv Remaining argument tokens after `--test-static-check` (i.e. [subcommand, ...]).
- Return: Process exit code from the selected checker's `run()` method.
- Throws: ReqError If subcommand is missing, unknown, or `command` subcommand is missing `cmd`.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_split_csv_like_tokens`|fn|priv|111-145|def _split_csv_like_tokens(spec_rhs: str) -> list[str]|
|`parse_enable_static_check`|fn|pub|146-222|def parse_enable_static_check(spec: str) -> tuple[str, dict]|
|`dispatch_static_check_for_file`|fn|pub|227-272|def dispatch_static_check_for_file(filepath: str, lang_co...|
|`_resolve_files`|fn|priv|277-319|def _resolve_files(inputs: Sequence[str]) -> List[str]|
|`StaticCheckBase`|class|pub|324-414|class StaticCheckBase|
|`StaticCheckBase.__init__`|fn|priv|335-338|def __init__(|
|`StaticCheckBase.run`|fn|pub|355-378|def run(self) -> int|
|`StaticCheckBase._header_line`|fn|priv|383-393|def _header_line(self, filepath: str) -> str|
|`StaticCheckBase._check_file`|fn|priv|394-405|def _check_file(self, filepath: str) -> int|
|`StaticCheckBase._emit_line`|fn|priv|406-414|def _emit_line(self, line: str) -> None|
|`StaticCheckPylance`|class|pub|419-467|class StaticCheckPylance(StaticCheckBase)|
|`StaticCheckPylance.LABEL`|var|pub|429||
|`StaticCheckPylance._check_file`|fn|priv|431-467|def _check_file(self, filepath: str) -> int|
|`StaticCheckRuff`|class|pub|472-520|class StaticCheckRuff(StaticCheckBase)|
|`StaticCheckRuff.LABEL`|var|pub|482||
|`StaticCheckRuff._check_file`|fn|priv|484-520|def _check_file(self, filepath: str) -> int|
|`StaticCheckCommand`|class|pub|525-594|class StaticCheckCommand(StaticCheckBase)|
|`StaticCheckCommand.__init__`|fn|priv|536-540|def __init__(|
|`StaticCheckCommand._check_file`|fn|priv|559-594|def _check_file(self, filepath: str) -> int|
|`run_static_check`|fn|pub|599-663|def run_static_check(argv: Sequence[str]) -> int|


---

# token_counter.py | Python | 116L | 7 symbols | 2 imports | 8 comments
> Path: `src/usereq/token_counter.py`

## Imports
```
import os
import tiktoken
```

## Definitions

### class `class TokenCounter` (L14-44)
- Brief: Count tokens using tiktoken encoding (cl100k_base by default). Initialize token counter with a specific tiktoken encoding. Count tokens in content string. Count characters in content string.
- Details: Wrapper around tiktoken encoding to simplify token counting operations. Uses `disallowed_special=()` to allow special tokens in input without raising errors. Returns 0 on failure.
- Param: encoding_name Name of tiktoken encoding used for tokenization. content The text content to tokenize. content The text string.
- Return: Integer count of tokens. Integer count of characters.
- fn `def __init__(self, encoding_name: str = "cl100k_base")` `priv` (L19-24)
  - Brief: Count tokens using tiktoken encoding (cl100k_base by default). Initialize token counter with a specific tiktoken encoding.
  - Details: Wrapper around tiktoken encoding to simplify token counting operations.
  - Param: encoding_name Name of tiktoken encoding used for tokenization.
- fn `def count_tokens(self, content: str) -> int` (L25-35)
  - Brief: Count tokens in content string.
  - Details: Uses `disallowed_special=()` to allow special tokens in input without raising errors. Returns 0 on failure.
  - Param: content The text content to tokenize.
  - Return: Integer count of tokens.
- fn `def count_chars(content: str) -> int` (L37-44)
  - Brief: Count characters in content string.
  - Param: content The text string.
  - Return: Integer count of characters.

### fn `def count_file_metrics(content: str,` (L45-58)
- Brief: Count tokens and chars for a content string.
- Param: content The text content to measure. encoding_name The tiktoken encoding name (default: "cl100k_base").
- Return: Dictionary with keys 'tokens' (int) and 'chars' (int).

### fn `def count_files_metrics(file_paths: list,` (L59-87)
- Brief: Count tokens and chars for a list of files.
- Details: Iterates through files, reading content and counting metrics. Gracefully handles read errors.
- Param: file_paths List of file paths to process. encoding_name The tiktoken encoding name.
- Return: List of dictionaries, each containing 'file', 'tokens', 'chars', and optionally 'error'.

### fn `def format_pack_summary(results: list) -> str` (L88-116)
- Brief: Format a pack summary string from a list of file metrics.
- Details: Generates a human-readable report including icons, per-file stats, and aggregate totals.
- Param: results List of metrics dictionaries from count_files_metrics().
- Return: Formatted summary string with per-file details and totals.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`TokenCounter`|class|pub|14-44|class TokenCounter|
|`TokenCounter.__init__`|fn|priv|19-24|def __init__(self, encoding_name: str = "cl100k_base")|
|`TokenCounter.count_tokens`|fn|pub|25-35|def count_tokens(self, content: str) -> int|
|`TokenCounter.count_chars`|fn|pub|37-44|def count_chars(content: str) -> int|
|`count_file_metrics`|fn|pub|45-58|def count_file_metrics(content: str,|
|`count_files_metrics`|fn|pub|59-87|def count_files_metrics(file_paths: list,|
|`format_pack_summary`|fn|pub|88-116|def format_pack_summary(results: list) -> str|

