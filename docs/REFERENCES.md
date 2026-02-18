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
        └── token_counter.py
```

# __init__.py | Python | 26L | 0 symbols | 8 imports | 3 comments
> Path: `/home/ogekuri/useReq/src/usereq/__init__.py`

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
> Path: `/home/ogekuri/useReq/src/usereq/__main__.py`

## Imports
```
from .cli import main
import sys
```


---

# cli.py | Python | 2774L | 96 symbols | 24 imports | 156 comments
> Path: `/home/ogekuri/useReq/src/usereq/cli.py`

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
import copy
from .token_counter import count_files_metrics, format_pack_summary
from .generate_markdown import generate_markdown
from .compress_files import compress_files
from .find_constructs import find_constructs_in_files
from .generate_markdown import generate_markdown
from .compress_files import compress_files
from .find_constructs import find_constructs_in_files
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
### class `class ReqError(Exception)` : Exception (L41-54)
- Brief: Dedicated exception for expected CLI errors. Initialize an expected CLI failure payload.
- Details: This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.
- Param: message Human-readable error message. code Process exit code bound to the failure category.
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L45-54)
  - Brief: Dedicated exception for expected CLI errors. Initialize an expected CLI failure payload.
  - Details: This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.
  - Param: message Human-readable error message. code Process exit code bound to the failure category.

### fn `def log(msg: str) -> None` (L55-61)
- Brief: Prints an informational message.
- Param: msg The message string to print.

### fn `def dlog(msg: str) -> None` (L62-69)
- Brief: Prints a debug message if debugging is active.
- Param: msg The debug message string to print.

### fn `def vlog(msg: str) -> None` (L70-77)
- Brief: Prints a verbose message if verbose mode is active.
- Param: msg The verbose message string to print.

### fn `def _get_available_tags_help() -> str` `priv` (L78-89)
- Brief: Generate available TAGs help text for argument parser.
- Details: Imports format_available_tags from find_constructs module to generate dynamic TAG listing for CLI help display.
- Return: Formatted multi-line string listing TAGs by language.

### fn `def build_parser() -> argparse.ArgumentParser` (L90-289)
- Brief: Builds the CLI argument parser.
- Details: Defines all supported CLI arguments, flags, and help texts. Includes provider flags (--enable-claude, --enable-codex, --enable-gemini, --enable-github, --enable-kiro, --enable-opencode) and artifact-type flags (--enable-prompts, --enable-agents, --enable-skills).
- Return: Configured ArgumentParser instance.

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L290-297)
- Brief: Parses command-line arguments into a namespace.
- Param: argv List of arguments (defaults to sys.argv).
- Return: Namespace containing parsed arguments.

### fn `def load_package_version() -> str` (L298-310)
- Brief: Reads the package version from __init__.py.
- Return: Version string extracted from the package.
- Throws: ReqError If version cannot be determined.

### fn `def maybe_print_version(argv: list[str]) -> bool` (L311-321)
- Brief: Handles --ver/--version by printing the version.
- Param: argv Command line arguments to check.
- Return: True if version was printed, False otherwise.

### fn `def run_upgrade() -> None` (L322-345)
- Brief: Executes the upgrade using uv.
- Throws: ReqError If upgrade fails.

### fn `def run_uninstall() -> None` (L346-366)
- Brief: Executes the uninstallation using uv.
- Throws: ReqError If uninstall fails.

### fn `def normalize_release_tag(tag: str) -> str` (L367-377)
- Brief: Normalizes the release tag by removing a 'v' prefix if present.
- Param: tag The raw tag string.
- Return: The normalized version string.

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L378-402)
- Brief: Converts a version into a numeric tuple for comparison.
- Details: Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
- Param: version The version string to parse.
- Return: Tuple of integers or None if parsing fails.

### fn `def is_newer_version(current: str, latest: str) -> bool` (L403-419)
- Brief: Returns True if latest is greater than current.
- Param: current The current installed version string. latest The latest available version string.
- Return: True if update is available, False otherwise.

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L420-461)
- Brief: Checks online for a new version and prints a warning.
- Details: If the call fails or the response is invalid, it prints nothing and proceeds.
- Param: timeout_seconds Time to wait for the version check response.

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L462-481)
- Brief: Ensures the documentation directory exists under the project base.
- Param: path The relative path to the documentation directory. project_base The project root path.
- Throws: ReqError If path is invalid, absolute, or not a directory.

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L482-501)
- Brief: Ensures the test directory exists under the project base.
- Param: path The relative path to the test directory. project_base The project root path.
- Throws: ReqError If path is invalid, absolute, or not a directory.

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L502-521)
- Brief: Ensures the source directory exists under the project base.
- Param: path The relative path to the source directory. project_base The project root path.
- Throws: ReqError If path is invalid, absolute, or not a directory.

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L522-561)
- Brief: Normalizes the path relative to the project root when possible.
- Details: Handles cases where the path includes the project directory name redundantly.
- Param: path_value The input path string. project_base The base path of the project.
- Return: The normalized relative path string.

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L562-575)
- Brief: Resolves the absolute path starting from a normalized value.
- Param: normalized The normalized relative path string. project_base The project root path.
- Return: Absolute Path object or None if normalized is empty.

### fn `def format_substituted_path(value: str) -> str` (L576-585)
- Brief: Uniforms path separators for substitutions.
- Param: value The path string to format.
- Return: Path string with forward slashes.

### fn `def compute_sub_path(` (L586-587)

### fn `def save_config(` (L606-611)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L633-673)
- Brief: Loads parameters saved in .req/config.json.
- Param: project_base The project root path.
- Return: Dictionary containing configuration values.
- Throws: ReqError If config file is missing or invalid.

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L674-701)
- Brief: Generates the markdown file list for %%GUIDELINES_FILES%% replacement.

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L702-730)
- Brief: Generates a list of relative file paths (no formatting) for printing.
- Details: Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.

### fn `def upgrade_guidelines_templates(` (L731-732)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L764-775)
- Brief: Normalizes the path token optionally preserving the trailing slash.

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L776-785)
- Brief: Validates that the path is not absolute and raises an error otherwise.

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L786-793)
- Brief: Returns text with token replacements applied.

### fn `def write_text_file(dst: Path, text: str) -> None` (L794-800)
- Brief: Writes text to disk, ensuring the destination folder exists.

### fn `def copy_with_replacements(` (L801-802)

### fn `def normalize_description(value: str) -> str` (L811-821)
- Brief: Normalizes a description by removing superfluous quotes and escapes.

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L822-850)
- Brief: Converts a Markdown prompt to TOML for Gemini.

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L851-860)
- Brief: Extracts front matter and body from Markdown.

### fn `def extract_description(frontmatter: str) -> str` (L861-869)
- Brief: Extracts the description from front matter.

### fn `def extract_argument_hint(frontmatter: str) -> str` (L870-878)
- Brief: Extracts the argument-hint from front matter, if present.

### fn `def extract_purpose_first_bullet(body: str) -> str` (L879-899)
- Brief: Returns the first bullet of the Purpose section.

### fn `def _extract_section_text(body: str, section_name: str) -> str` `priv` (L900-927)
- Brief: Extracts and collapses the text content of a named ## section.
- Details: Scans `body` line by line for a heading matching `## <section_name>` (case-insensitive). Collects all subsequent non-empty lines until the next `##`-level heading (or end of string). Strips each line, joins with a single space, and returns the collapsed single-line result.
- Param[in]: body str -- Full prompt body text (after front matter removal). section_name str -- Target section name without `##` prefix (case-insensitive match).
- Return: str -- Single-line collapsed text of the section; empty string if section absent or empty.

### fn `def extract_skill_description(frontmatter: str) -> str` (L928-946)
- Brief: Extracts the usage field from YAML front matter as a single YAML-safe line.
- Details: Parses the YAML front matter and returns the `usage` field value with all whitespace normalized to a single line. Returns an empty string if the field is absent.
- Param[in]: frontmatter str -- YAML front matter text (without the leading/trailing `---` delimiters).
- Return: str -- Single-line text of the usage field; empty string if absent.

### fn `def json_escape(value: str) -> str` (L947-952)
- Brief: Escapes a string for JSON without external delimiters.

### fn `def generate_kiro_resources(` (L953-956)

### fn `def render_kiro_agent(` (L976-985)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L1019-1027)
- Brief: Replaces tokens in the specified file.

### fn `def yaml_double_quote_escape(value: str) -> str` (L1028-1033)
- Brief: Minimal escape for a double-quoted string in YAML.

### fn `def list_docs_templates() -> list[Path]` (L1034-1049)
- Brief: Returns non-hidden files available in resources/docs.
- Return: Sorted list of file paths under resources/docs.
- Throws: ReqError If resources/docs does not exist or has no non-hidden files.

### fn `def find_requirements_template(docs_templates: list[Path]) -> Path` (L1050-1064)
- Brief: Returns the packaged Requirements template file.
- Param: docs_templates Runtime docs template file list from resources/docs.
- Return: Path to `Requirements_Template.md`.
- Throws: ReqError If `Requirements_Template.md` is not present.

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L1065-1099)
- Brief: Loads the Kiro template from centralized models configuration.

### fn `def strip_json_comments(text: str) -> str` (L1100-1120)
- Brief: Removes // and /* */ comments to allow JSONC parsing.

### fn `def load_settings(path: Path) -> dict[str, Any]` (L1121-1132)
- Brief: Loads JSON/JSONC settings, removing comments when necessary.

### fn `def load_centralized_models(` (L1133-1136)

### fn `def get_model_tools_for_prompt(` (L1180-1181)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1216-1233)
- Brief: Returns the raw value of `usage_modes[mode]['tools']` for the prompt.
- Details: Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1234-1241)
- Brief: Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1242-1252)
- Brief: Recursively merges dictionaries, prioritizing incoming values.

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1253-1261)
- Brief: Finds the VS Code settings template if available.

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1262-1272)
- Brief: Generates chat.promptFilesRecommendations from available prompts.

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1273-1282)
- Brief: Verifies that the path is under the project root.

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1283-1292)
- Brief: Saves a backup of VS Code settings if the file exists.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1293-1304)
- Brief: Restores VS Code settings from backup, if present.

### fn `def prune_empty_dirs(root: Path) -> None` (L1305-1318)
- Brief: Removes empty directories under the specified root.

### fn `def remove_generated_resources(project_base: Path) -> None` (L1319-1364)
- Brief: Removes resources generated by the tool in the project root.

### fn `def run_remove(args: Namespace) -> None` (L1365-1411)
- Brief: Handles the removal of generated resources.

### fn `def run(args: Namespace) -> None` (L1412-1611)
- Brief: Handles the main initialization flow.
- Details: Validates input arguments, normalizes paths, and orchestrates resource generation per provider and artifact type. Requires at least one provider flag and at least one of --enable-prompts, --enable-agents, --enable-skills.
- Param: args Parsed CLI namespace; must contain provider flags (enable_claude, enable_codex, enable_gemini, enable_github, enable_kiro, enable_opencode) and artifact-type flags (enable_prompts, enable_agents, enable_skills).

- var `VERBOSE = args.verbose` (L1418)
- Brief: Handles the main initialization flow.
- Details: Validates input arguments, normalizes paths, and orchestrates resource generation per provider and artifact type. Requires at least one provider flag and at least one of --enable-prompts, --enable-agents, --enable-skills.
- Param: args Parsed CLI namespace; must contain provider flags (enable_claude, enable_codex, enable_gemini, enable_github, enable_kiro, enable_opencode) and artifact-type flags (enable_prompts, enable_agents, enable_skills).
- var `DEBUG = args.debug` (L1419)
- var `PROMPT = prompt_path.stem` (L1784)
### fn `def _format_install_table(` `priv` (L2358-2360)

### fn `def fmt(row: tuple[str, ...]) -> str` (L2381-2383)

- var `EXCLUDED_DIRS = frozenset({` (L2401)
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2410)
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2418-2438)
- Brief: Recursively collect source files from the given directories.
- Details: Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.

### fn `def _build_ascii_tree(paths: list[str]) -> str` `priv` (L2439-2476)
- Brief: Build a deterministic tree string from project-relative paths.
- Param: paths Project-relative file paths.
- Return: Rendered tree rooted at '.'.

### fn `def _emit(` `priv` (L2461-2463)

### fn `def _format_files_structure_markdown(files: list[str], project_base: Path) -> str` `priv` (L2477-2487)
- Brief: Format markdown section containing the scanned files tree.
- Param: files Absolute file paths selected for --references processing. project_base Project root used to normalize relative paths.
- Return: Markdown section with heading and fenced tree.

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2488-2498)
- Brief: Check if the parsed args contain a standalone file command.

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2499-2509)
- Brief: Check if the parsed args contain a project scan command.

### fn `def run_files_tokens(files: list[str]) -> None` (L2510-2528)
- Brief: Execute --files-tokens: count tokens for arbitrary files.

### fn `def run_files_references(files: list[str]) -> None` (L2529-2537)
- Brief: Execute --files-references: generate markdown for arbitrary files.

### fn `def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None` (L2538-2552)
- Brief: Execute --files-compress: compress arbitrary files.
- Param: files List of source file paths to compress. enable_line_numbers If True, emits <n>: prefixes in compressed entries.

### fn `def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None` (L2553-2578)
- Brief: Execute --files-find: find constructs in arbitrary files.
- Param: args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...]. enable_line_numbers If True, emits <n>: prefixes in output.

### fn `def run_references(args: Namespace) -> None` (L2579-2592)
- Brief: Execute --references: generate markdown for project source files.

### fn `def run_compress_cmd(args: Namespace) -> None` (L2593-2610)
- Brief: Execute --compress: compress project source files.
- Param: args Parsed CLI arguments namespace.

### fn `def run_find(args: Namespace) -> None` (L2611-2637)
- Brief: Execute --find: find constructs in project source files.
- Param: args Parsed CLI arguments namespace.
- Throws: ReqError If no source files found or no constructs match criteria with available TAGs listing.

### fn `def run_tokens(args: Namespace) -> None` (L2638-2660)
- Brief: Execute --tokens: count tokens for files directly in --docs-dir.
- Details: Requires --base/--here and --docs-dir, then delegates reporting to run_files_tokens.
- Param: args Parsed CLI arguments namespace.

### fn `def _resolve_project_base(args: Namespace) -> Path` `priv` (L2661-2681)
- Brief: Resolve project base path for project-level commands.
- Param: args Parsed CLI arguments namespace.
- Return: Absolute path of project base.
- Throws: ReqError If --base/--here is missing or the resolved path does not exist.

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L2682-2708)
- Brief: Resolve project base and src-dirs for --references/--compress.

### fn `def main(argv: Optional[list[str]] = None) -> int` (L2709-2774)
- Brief: CLI entry point for console_scripts and `-m` execution.
- Details: Returns an exit code (0 success, non-zero on error).

- var `VERBOSE = getattr(args, "verbose", False)` (L2728)
- var `DEBUG = getattr(args, "debug", False)` (L2729)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|25||
|`RESOURCE_ROOT`|var|pub|28||
|`VERBOSE`|var|pub|31||
|`DEBUG`|var|pub|34||
|`REQUIREMENTS_TEMPLATE_NAME`|var|pub|37||
|`ReqError`|class|pub|41-54|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|45-54|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|55-61|def log(msg: str) -> None|
|`dlog`|fn|pub|62-69|def dlog(msg: str) -> None|
|`vlog`|fn|pub|70-77|def vlog(msg: str) -> None|
|`_get_available_tags_help`|fn|priv|78-89|def _get_available_tags_help() -> str|
|`build_parser`|fn|pub|90-289|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|290-297|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|298-310|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|311-321|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|322-345|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|346-366|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|367-377|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|378-402|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|403-419|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|420-461|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|462-481|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|482-501|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|502-521|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|522-561|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|562-575|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|576-585|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|586-587|def compute_sub_path(|
|`save_config`|fn|pub|606-611|def save_config(|
|`load_config`|fn|pub|633-673|def load_config(project_base: Path) -> dict[str, str | li...|
|`generate_guidelines_file_list`|fn|pub|674-701|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|702-730|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`upgrade_guidelines_templates`|fn|pub|731-732|def upgrade_guidelines_templates(|
|`make_relative_token`|fn|pub|764-775|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|776-785|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|786-793|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|794-800|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|801-802|def copy_with_replacements(|
|`normalize_description`|fn|pub|811-821|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|822-850|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|851-860|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|861-869|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|870-878|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|879-899|def extract_purpose_first_bullet(body: str) -> str|
|`_extract_section_text`|fn|priv|900-927|def _extract_section_text(body: str, section_name: str) -...|
|`extract_skill_description`|fn|pub|928-946|def extract_skill_description(frontmatter: str) -> str|
|`json_escape`|fn|pub|947-952|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|953-956|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|976-985|def render_kiro_agent(|
|`replace_tokens`|fn|pub|1019-1027|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|1028-1033|def yaml_double_quote_escape(value: str) -> str|
|`list_docs_templates`|fn|pub|1034-1049|def list_docs_templates() -> list[Path]|
|`find_requirements_template`|fn|pub|1050-1064|def find_requirements_template(docs_templates: list[Path]...|
|`load_kiro_template`|fn|pub|1065-1099|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|1100-1120|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|1121-1132|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|1133-1136|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|1180-1181|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1216-1233|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1234-1241|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1242-1252|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1253-1261|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1262-1272|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1273-1282|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1283-1292|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1293-1304|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1305-1318|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1319-1364|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1365-1411|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1412-1611|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1418||
|`DEBUG`|var|pub|1419||
|`PROMPT`|var|pub|1784||
|`_format_install_table`|fn|priv|2358-2360|def _format_install_table(|
|`fmt`|fn|pub|2381-2383|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|2401||
|`SUPPORTED_EXTENSIONS`|var|pub|2410||
|`_collect_source_files`|fn|priv|2418-2438|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_build_ascii_tree`|fn|priv|2439-2476|def _build_ascii_tree(paths: list[str]) -> str|
|`_emit`|fn|priv|2461-2463|def _emit(|
|`_format_files_structure_markdown`|fn|priv|2477-2487|def _format_files_structure_markdown(files: list[str], pr...|
|`_is_standalone_command`|fn|priv|2488-2498|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2499-2509|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2510-2528|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2529-2537|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2538-2552|def run_files_compress(files: list[str], enable_line_numb...|
|`run_files_find`|fn|pub|2553-2578|def run_files_find(args_list: list[str], enable_line_numb...|
|`run_references`|fn|pub|2579-2592|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2593-2610|def run_compress_cmd(args: Namespace) -> None|
|`run_find`|fn|pub|2611-2637|def run_find(args: Namespace) -> None|
|`run_tokens`|fn|pub|2638-2660|def run_tokens(args: Namespace) -> None|
|`_resolve_project_base`|fn|priv|2661-2681|def _resolve_project_base(args: Namespace) -> Path|
|`_resolve_project_src_dirs`|fn|priv|2682-2708|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|2709-2774|def main(argv: Optional[list[str]] = None) -> int|
|`VERBOSE`|var|pub|2728||
|`DEBUG`|var|pub|2729||


---

# compress.py | Python | 386L | 11 symbols | 5 imports | 41 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress.py`

## Imports
```
import os
import re
import sys
from .source_analyzer import build_language_specs
import argparse
```

## Definitions

- var `EXT_LANG_MAP = {` (L17)
- var `INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}` (L29)
### fn `def _get_specs()` `priv` (L36-46)
- Brief: Return cached language specifications, initializing once.
- Details: If cache is empty, calls `build_language_specs()` to populate it.
- Return: Dictionary mapping normalized language keys to language specs.

### fn `def detect_language(filepath: str) -> str | None` (L47-56)
- Brief: Detect language key from file extension.
- Details: Uses `EXT_LANG_MAP` for lookup. Case-insensitive extension matching.
- Param: filepath Source file path.
- Return: Normalized language key, or None when extension is unsupported.

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L57-98)
- Brief: Check if position `pos` in `line` is inside a string literal.
- Details: iterates through the line handling escaped delimiters.
- Param: line The code line string. pos The character index to check. string_delimiters Tuple of string delimiter characters/sequences.
- Return: True if `pos` is inside a string, False otherwise.

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L99-142)
- Brief: Remove trailing single-line comment from a code line.
- Details: Respects string literals; does not remove comments inside strings.
- Param: line The code line string. single_comment The single-line comment marker (e.g., "//", "#"). string_delimiters Tuple of string delimiters to respect.
- Return: The line content before the comment starts.

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L143-154)
- Brief: Check if a line is a standalone Python docstring (triple-quote only).
- Param: line The code line string.
- Return: True if the line appears to be a standalone triple-quoted string.

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L155-166)
- Brief: Format compressed entries, optionally prefixing original line numbers.
- Param: entries List of tuples (line_number, text). include_line_numbers Boolean flag to enable line prefixes.
- Return: Formatted string.

### fn `def compress_source(source: str, language: str,` (L167-334)
- Brief: Compress source code by removing comments, blank lines, and extra whitespace.
- Details: Preserves indentation for indent-significant languages (Python, Haskell, Elixir).
- Param: source The source code string. language Language identifier (e.g. "python", "javascript"). include_line_numbers If True (default), prefix each line with <n>: format.
- Return: Compressed source code string.
- Throws: ValueError If language is unsupported.

### fn `def compress_file(filepath: str, language: str | None = None,` (L335-356)
- Brief: Compress a source file by removing comments and extra whitespace.
- Param: filepath Path to the source file. language Optional language override. Auto-detected if None. include_line_numbers If True (default), prefix each line with <n>: format.
- Return: Compressed source code string.
- Throws: ValueError If language cannot be detected.

### fn `def main()` (L357-384)
- Brief: Execute the standalone compression CLI.
- Details: Parses command-line arguments and invokes `compress_file`, printing the result to stdout or errors to stderr.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|17||
|`INDENT_SIGNIFICANT`|var|pub|29||
|`_get_specs`|fn|priv|36-46|def _get_specs()|
|`detect_language`|fn|pub|47-56|def detect_language(filepath: str) -> str | None|
|`_is_in_string`|fn|priv|57-98|def _is_in_string(line: str, pos: int, string_delimiters:...|
|`_remove_inline_comment`|fn|priv|99-142|def _remove_inline_comment(line: str, single_comment: str,|
|`_is_python_docstring_line`|fn|priv|143-154|def _is_python_docstring_line(line: str) -> bool|
|`_format_result`|fn|priv|155-166|def _format_result(entries: list[tuple[int, str]],|
|`compress_source`|fn|pub|167-334|def compress_source(source: str, language: str,|
|`compress_file`|fn|pub|335-356|def compress_file(filepath: str, language: str | None = N...|
|`main`|fn|pub|357-384|def main()|


---

# compress_files.py | Python | 113L | 3 symbols | 4 imports | 5 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress_files.py`

## Imports
```
import os
import sys
from .compress import compress_file, detect_language
import argparse
```

## Definitions

### fn `def _extract_line_range(compressed_with_line_numbers: str) -> tuple[int, int]` `priv` (L16-33)
- Brief: Extract source line interval from compressed output with <n>: prefixes.
- Details: Parses the first token of each line as an integer line number.
- Param: compressed_with_line_numbers Compressed payload generated with include_line_numbers=True.
- Return: Tuple (line_start, line_end) derived from preserved <n>: prefixes; returns (0, 0) when no prefixed lines exist.

### fn `def compress_files(filepaths: list[str],` (L34-90)
- Brief: Compress multiple source files and concatenate with identifying headers.
- Details: Each file is compressed and emitted as: header line `@@@ <path> | <lang>`, line-range metadata `- Lines: <start>-<end>`, and fenced code block delimited by triple backticks. Line range is derived from the already computed <n>: prefixes to preserve existing numbering logic. Files are separated by a blank line.
- Param: filepaths List of source file paths. include_line_numbers If True (default), keep <n>: prefixes in code block lines. verbose If True, emits progress status messages on stderr.
- Return: Concatenated compressed output string.
- Throws: ValueError If no files could be processed.

### fn `def main()` (L91-111)
- Brief: Execute the multi-file compression CLI command.
- Details: Parses command-line arguments, calls `compress_files`, and prints output or errors.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_extract_line_range`|fn|priv|16-33|def _extract_line_range(compressed_with_line_numbers: str...|
|`compress_files`|fn|pub|34-90|def compress_files(filepaths: list[str],|
|`main`|fn|pub|91-111|def main()|


---

# doxygen_parser.py | Python | 163L | 5 symbols | 2 imports | 19 comments
> Path: `/home/ogekuri/useReq/src/usereq/doxygen_parser.py`

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

# find_constructs.py | Python | 357L | 11 symbols | 8 imports | 18 comments
> Path: `/home/ogekuri/useReq/src/usereq/find_constructs.py`

## Imports
```
import os
import re
import sys
from pathlib import Path
from .doxygen_parser import format_doxygen_fields_as_markdown, parse_doxygen_comment
from .source_analyzer import SourceAnalyzer
from .compress import compress_source, detect_language
import argparse
```

## Definitions

- var `LANGUAGE_TAGS = {` (L21)
### fn `def format_available_tags() -> str` (L45-58)
- Brief: Generate formatted list of available TAGs per language.
- Details: Iterates LANGUAGE_TAGS dictionary, formats each entry as "- Language: TAG1, TAG2, ..." with language capitalized and tags alphabetically sorted and comma-separated.
- Return: Multi-line string listing each language with its supported TAGs.

### fn `def parse_tag_filter(tag_string: str) -> set[str]` (L59-67)
- Brief: Parse pipe-separated tag filter into a normalized set.
- Details: Splits the input string by pipe character `|` and strips whitespace from each component.
- Param: tag_string Raw tag filter string (e.g., "CLASS|FUNCTION").
- Return: Set of uppercase tag identifiers.

### fn `def language_supports_tags(lang: str, tag_set: set[str]) -> bool` (L68-78)
- Brief: Check if the language supports at least one of the requested tags.
- Details: Lookups the language in `LANGUAGE_TAGS` and checks if any of `tag_set` exists in the supported tags.
- Param: lang Normalized language identifier. tag_set Set of requested TAG identifiers.
- Return: True if intersection is non-empty, False otherwise.

### fn `def construct_matches(element, tag_set: set[str], pattern: str) -> bool` (L79-96)
- Brief: Check if a source element matches tag filter and regex pattern.
- Details: Validates the element type and then applies the regex search on the element name.
- Param: element SourceElement instance from analyzer. tag_set Set of requested TAG identifiers. pattern Regex pattern string to test against element name.
- Return: True if element type is in tag_set and name matches pattern.

### fn `def _merge_doxygen_fields(` `priv` (L97-99)

### fn `def _extract_construct_doxygen_fields(element) -> dict[str, list[str]]` `priv` (L114-136)
- Brief: Build aggregate Doxygen fields for one construct.
- Details: Aggregates fields from two sources: pre-associated element.doxygen_fields and all comment snippets extracted from element.body_comments. Each comment snippet is parsed with parse_doxygen_comment() and merged in discovery order.
- Param: element SourceElement instance potentially enriched with doxygen_fields and body_comments.
- Return: Dictionary tag->list preserving tag content insertion order.

### fn `def _strip_construct_comments(` `priv` (L137-141)

### fn `def format_construct(` (L177-181)

### fn `def find_constructs_in_files(` (L219-224)

### fn `def main()` (L320-355)
- Brief: Execute the construct finding CLI command.
- Details: Parses arguments and calls find_constructs_in_files. Handles exceptions by printing errors to stderr.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`LANGUAGE_TAGS`|var|pub|21||
|`format_available_tags`|fn|pub|45-58|def format_available_tags() -> str|
|`parse_tag_filter`|fn|pub|59-67|def parse_tag_filter(tag_string: str) -> set[str]|
|`language_supports_tags`|fn|pub|68-78|def language_supports_tags(lang: str, tag_set: set[str]) ...|
|`construct_matches`|fn|pub|79-96|def construct_matches(element, tag_set: set[str], pattern...|
|`_merge_doxygen_fields`|fn|priv|97-99|def _merge_doxygen_fields(|
|`_extract_construct_doxygen_fields`|fn|priv|114-136|def _extract_construct_doxygen_fields(element) -> dict[st...|
|`_strip_construct_comments`|fn|priv|137-141|def _strip_construct_comments(|
|`format_construct`|fn|pub|177-181|def format_construct(|
|`find_constructs_in_files`|fn|pub|219-224|def find_constructs_in_files(|
|`main`|fn|pub|320-355|def main()|


---

# generate_markdown.py | Python | 134L | 4 symbols | 3 imports | 7 comments
> Path: `/home/ogekuri/useReq/src/usereq/generate_markdown.py`

## Imports
```
import os
import sys
from .source_analyzer import SourceAnalyzer, format_markdown
```

## Definitions

- var `EXT_LANG_MAP = {` (L16)
### fn `def detect_language(filepath: str) -> str | None` (L43-52)
- Brief: Detect language from file extension.
- Details: Uses EXT_LANG_MAP for extension lookup (case-insensitive).
- Param: filepath Path to the source file.
- Return: Language identifier string or None if unknown.

### fn `def generate_markdown(filepaths: list[str], verbose: bool = False) -> str` (L53-115)
- Brief: Analyze source files and return concatenated markdown.
- Details: Iterates through files, detecting language, analyzing constructs, and formatting output. Disables legacy comment/exit annotation traces in rendered markdown, emitting only construct references plus Doxygen field bullets when available.
- Param: filepaths List of source file paths to analyze. verbose If True, emits progress status messages on stderr.
- Return: Concatenated markdown string with all file analyses.
- Throws: ValueError If no valid source files are found.

### fn `def main()` (L116-132)
- Brief: Execute the standalone markdown generation CLI command.
- Details: Expects file paths as command-line arguments. Prints generated markdown to stdout.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|16||
|`detect_language`|fn|pub|43-52|def detect_language(filepath: str) -> str | None|
|`generate_markdown`|fn|pub|53-115|def generate_markdown(filepaths: list[str], verbose: bool...|
|`main`|fn|pub|116-132|def main()|


---

# source_analyzer.py | Python | 2061L | 59 symbols | 11 imports | 130 comments
> Path: `/home/ogekuri/useReq/src/usereq/source_analyzer.py`

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
from doxygen_parser import parse_doxygen_comment
from .doxygen_parser import format_doxygen_fields_as_markdown
from doxygen_parser import format_doxygen_fields_as_markdown
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

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L1020-1045)
- Brief: Extract clean identifiers from name fields.
- Details: Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1046-1061)
- Brief: Extract clean signatures from element extracts.

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1062-1095)
- Brief: Detect parent-child relationships between elements.
- Details: Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1096-1108)
- Brief: Extract visibility/access modifiers from elements.

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1109-1154)
- Brief: Parse visibility modifier from a signature line.

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1155-1166)
- Brief: Extract inheritance/implementation info from class-like elements.

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1167-1196)
- Brief: Parse inheritance info from a class/struct declaration line.

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1204-1327)
- Brief: Extract comments and exit points from within function/class bodies.
- Details: Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.

### fn `def _extract_doxygen_fields(self, elements: list)` `priv` (L1328-1387)
- Brief: Extract Doxygen tag fields from associated documentation comments.
- Details: For each non-comment element, resolves the nearest associated documentation comment using language-agnostic adjacency rules: same-line postfix comment (`//!<`, `#!<`, `/**<`), nearest preceding standalone comment block within two lines, or nearest following postfix standalone comment within two lines. Parses the resolved comment via parse_doxygen_comment() and stores the extracted fields in element.doxygen_fields.

### fn `def _is_postfix_doxygen_comment(comment_text: str) -> bool` `priv` `@staticmethod` (L1389-1398)
- Brief: Detect whether a comment uses postfix Doxygen association markers.
- Details: Returns True for comment prefixes that explicitly bind documentation to a preceding construct, including variants like `#!<`, `//!<`, `///<`, `/*!<`, and `/**<`.
- Param: comment_text Raw extracted comment text.
- Return: True when the comment text starts with a supported postfix marker; otherwise False.

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1400-1411)
- Brief: Strip comment markers from a single line of comment text.

### fn `def _md_loc(elem) -> str` `priv` (L1412-1419)
- Brief: Format element location compactly for markdown.

### fn `def _md_kind(elem) -> str` `priv` (L1420-1447)
- Brief: Short kind label for markdown output.

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1448-1470)
- Brief: Extract clean text content from a comment element.
- Details: Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1471-1487)
- Brief: Extract clean text lines from a multi-line comment (preserving structure).

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1488-1548)
- Brief: Build maps that associate comments with their adjacent definitions.
- Details: Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1549-1600)
- Brief: Render body comments and exit points for a definition element.
- Details: Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.

### fn `def _merge_doxygen_fields(` `priv` (L1601-1603)

### fn `def _collect_element_doxygen_fields(elem) -> dict[str, list[str]]` `priv` (L1617-1638)
- Brief: Aggregate construct Doxygen fields from associated and body comments.
- Details: Parses each body-comment tuple with parse_doxygen_comment() and merges results after pre-associated fields so references output can represent both association styles.
- Param: elem SourceElement containing optional `doxygen_fields` and `body_comments`.
- Return: Dictionary of normalized Doxygen tags to ordered value lists.

### fn `def format_markdown(` (L1639-1645)

### fn `def main()` (L1936-2059)
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
|`_clean_names`|fn|priv|1020-1045|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1046-1061|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1062-1095|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1096-1108|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1109-1154|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1155-1166|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1167-1196|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1204-1327|def _extract_body_annotations(self, elements: list,|
|`_extract_doxygen_fields`|fn|priv|1328-1387|def _extract_doxygen_fields(self, elements: list)|
|`_is_postfix_doxygen_comment`|fn|priv|1389-1398|def _is_postfix_doxygen_comment(comment_text: str) -> bool|
|`_clean_comment_line`|fn|priv|1400-1411|def _clean_comment_line(text: str, spec) -> str|
|`_md_loc`|fn|priv|1412-1419|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1420-1447|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1448-1470|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1471-1487|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1488-1548|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1549-1600|def _render_body_annotations(out: list, elem, indent: str...|
|`_merge_doxygen_fields`|fn|priv|1601-1603|def _merge_doxygen_fields(|
|`_collect_element_doxygen_fields`|fn|priv|1617-1638|def _collect_element_doxygen_fields(elem) -> dict[str, li...|
|`format_markdown`|fn|pub|1639-1645|def format_markdown(|
|`main`|fn|pub|1936-2059|def main()|


---

# token_counter.py | Python | 116L | 7 symbols | 2 imports | 8 comments
> Path: `/home/ogekuri/useReq/src/usereq/token_counter.py`

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

