# __init__.py | Python | 25L | 0 symbols | 8 imports | 3 comments
> Path: `/home/ogekuri/useReq/src/usereq/__init__.py`
> Package entry point for useReq automation. This file exposes lightweight metadata and a convenient re-export of the `main` CLI entry point, so callers can use `from usereq import main` without unin...

## Imports
```
from . import cli  # usereq.cli submodule
from . import pdoc_utils  # usereq.pdoc_utils submodule
from . import source_analyzer  # usereq.source_analyzer submodule
from . import token_counter  # usereq.token_counter submodule
from . import generate_markdown  # usereq.generate_markdown submodule
from . import compress  # usereq.compress submodule
from . import compress_files  # usereq.compress_files submodule
from .cli import main  # re-export of CLI entry point
```

## Comments
- L9: The current version of the package.
- L25: ! @brief Public package exports for CLI entrypoint and utility submodules.


---

# __main__.py | Python | 7L | 0 symbols | 2 imports | 1 comments
> Path: `/home/ogekuri/useReq/src/usereq/__main__.py`
> Allows execution of the tool as a module.

## Imports
```
from .cli import main
import sys
```


---

# cli.py | Python | 2196L | 82 symbols | 20 imports | 140 comments
> Path: `/home/ogekuri/useReq/src/usereq/cli.py`
> CLI entry point implementing the useReq initialization flow.

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
from argparse import Namespace
from pathlib import Path
from typing import Any, Mapping, Optional
import copy
from .token_counter import count_files_metrics, format_pack_summary
from .generate_markdown import generate_markdown
from .compress_files import compress_files
from .generate_markdown import generate_markdown
from .compress_files import compress_files
import traceback
```

## Definitions

- var `REPO_ROOT = Path(__file__).resolve().parents[2]` (L18)
- var `RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"` (L21) — The absolute path to the repository root.
- var `VERBOSE = False` (L24) — The absolute path to the resources directory.
- var `DEBUG = False` (L27) — Whether verbose output is enabled.
### class `class ReqError(Exception)` : Exception (L31-43)
L28> Whether debug output is enabled.
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L34-43) L32> Dedicated exception for expected CLI errors.
  L35-38> ! @brief Initialize an expected CLI failure payload. @param message Human-readable error message. @param code Process exit code bound to the failure category.

### fn `def log(msg: str) -> None` (L44-48)
L45> Prints an informational message.

### fn `def dlog(msg: str) -> None` (L49-54)
L50> Prints a debug message if debugging is active.

### fn `def vlog(msg: str) -> None` (L55-60)
L56> Prints a verbose message if verbose mode is active.

### fn `def build_parser() -> argparse.ArgumentParser` (L61-218)
L62> Builds the CLI argument parser.
L216> `return parser`

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L219-223)
L220> Parses command-line arguments into a namespace.
L221> `return build_parser().parse_args(argv)`

### fn `def load_package_version() -> str` (L224-233)
L225> Reads the package version from __init__.py.
L230> `raise ReqError("Error: unable to determine package version", 6)`
L231> `return match.group(1)`

### fn `def maybe_print_version(argv: list[str]) -> bool` (L234-241)
L235> Handles --ver/--version by printing the version.
L238> `return True`
L239> `return False`

### fn `def run_upgrade() -> None` (L242-263)
L243> Executes the upgrade using uv.
L256> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L258> `raise ReqError(`

### fn `def run_uninstall() -> None` (L264-282)
L265> Executes the uninstallation using uv.
L275> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L277> `raise ReqError(`

### fn `def normalize_release_tag(tag: str) -> str` (L283-290)
L284> Normalizes the release tag by removing a 'v' prefix if present.
L288> `return value.strip()`

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L291-314)
L292-295> Converts a version into a numeric tuple for comparison. Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
L299> `return None`
L310> `return None`
L312> `return tuple(numbers) if numbers else None`

### fn `def is_newer_version(current: str, latest: str) -> bool` (L315-327)
L316> Returns True if latest is greater than current.
L320> `return False`
L325> `return latest_norm > current_norm`

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L328-369)
L329-332> Checks online for a new version and prints a warning. If the call fails or the response is invalid, it prints nothing and proceeds.
L351> `return`
L367> `return`

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L370-385)
L371> Ensures the documentation directory exists under the project base.
L376> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L378> `raise ReqError(`
L383> `raise ReqError("Error: --docs-dir must specify a directory, not a file", 5)`

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L386-401)
L387> Ensures the test directory exists under the project base.
L392> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L394> `raise ReqError(`
L399> `raise ReqError("Error: --tests-dir must specify a directory, not a file", 5)`

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L402-417)
L403> Ensures the source directory exists under the project base.
L408> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L410> `raise ReqError(`
L415> `raise ReqError("Error: --src-dir must specify a directory, not a file", 5)`

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L418-452)
L419> Normalizes the path relative to the project root when possible.
L421> `return ""`
L438> `return str(candidate.relative_to(project_base))`
L440> `return str(candidate)`
L443> `return str(resolved.relative_to(project_base))`
L449> `return trimmed`
L450> `return path_value`

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L453-462)
L454> Resolves the absolute path starting from a normalized value.
L456> `return None`
L459> `return candidate`
L460> `return (project_base / candidate).resolve(strict=False)`

### fn `def format_substituted_path(value: str) -> str` (L463-469)
L464> Uniforms path separators for substitutions.
L466> `return ""`
L467> `return value.replace(os.sep, "/")`

### fn `def compute_sub_path(` (L470-471)

### fn `def save_config(` (L485-490)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L506-542)
L507> Loads parameters saved in .req/config.json.
L510> `raise ReqError(`
L517> `raise ReqError("Error: .req/config.json is not valid", 11) from exc`
L519> Fallback to legacy key names from pre-v0.59 config files.
L524> `raise ReqError("Error: missing or invalid 'guidelines-dir' field in .req/config.json", 11)`
L526> `raise ReqError("Error: missing or invalid 'docs-dir' field in .req/config.json", 11)`
L528> `raise ReqError("Error: missing or invalid 'tests-dir' field in .req/config.json", 11)`
L534> `raise ReqError("Error: missing or invalid 'src-dir' field in .req/config.json", 11)`
L535> `return {`

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L543-569)
L544> Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
L546> `return ""`
L558> If there are no files, use the directory itself.
L563> `return f"`{rel_str}`"`
L565> `return ""`
L567> `return ", ".join(files)`

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L570-600)
L571-575> Generates a list of relative file paths (no formatting) for printing. Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
L577> `return []`
L589> If there are no files, use the directory itself.
L594> `return [rel_str]`
L596> `return []`
L598> `return items`

### fn `def copy_guidelines_templates(` (L601-602)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L640-650)
L641> Normalizes the path token optionally preserving the trailing slash.
L643> `return ""`
L646> `return ""`
L648> `return f"{normalized}{suffix}"`

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L651-659)
L652> Validates that the path is not absolute and raises an error otherwise.
L654> `raise ReqError(`

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L660-666)
L661> Returns text with token replacements applied.
L664> `return text`

### fn `def write_text_file(dst: Path, text: str) -> None` (L667-672)
L668> Writes text to disk, ensuring the destination folder exists.

### fn `def copy_with_replacements(` (L673-674)

### fn `def normalize_description(value: str) -> str` (L682-691)
L683> Normalizes a description by removing superfluous quotes and escapes.
L689> `return trimmed.replace('\\"', '"')`

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L692-719)
L693> Converts a Markdown prompt to TOML for Gemini.
L695> `raise ReqError(`
L702> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L720-728)
L721> Extracts front matter and body from Markdown.
L724> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`
L725> Explicitly return two strings to satisfy type annotation.
L726> `return match.group(1), match.group(2)`

### fn `def extract_description(frontmatter: str) -> str` (L729-736)
L730> Extracts the description from front matter.
L733> `raise ReqError("No 'description:' field found inside the leading block.", 5)`
L734> `return normalize_description(desc_match.group(1).strip())`

### fn `def extract_argument_hint(frontmatter: str) -> str` (L737-744)
L738> Extracts the argument-hint from front matter, if present.
L741> `return ""`
L742> `return normalize_description(match.group(1).strip())`

### fn `def extract_purpose_first_bullet(body: str) -> str` (L745-764)
L746> Returns the first bullet of the Purpose section.
L754> `raise ReqError("Error: missing '## Purpose' section in prompt.", 7)`
L761> `return match.group(1).strip()`
L762> `raise ReqError("Error: no bullet found under the '## Purpose' section.", 7)`

### fn `def json_escape(value: str) -> str` (L765-769)
L766> Escapes a string for JSON without external delimiters.
L767> `return json.dumps(value)[1:-1]`

### fn `def generate_kiro_resources(` (L770-773)

### fn `def render_kiro_agent(` (L792-801)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L834-841)
L835> Replaces tokens in the specified file.

### fn `def yaml_double_quote_escape(value: str) -> str` (L842-846)
L843> Minimal escape for a double-quoted string in YAML.
L844> `return value.replace("\\", "\\\\").replace('"', '\\"')`

### fn `def find_template_source() -> Path` (L847-857)
L848> Returns the template source or raises an error.
L851> `return candidate`
L852> `raise ReqError(`

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L858-891)
L859> Loads the Kiro template from centralized models configuration.
L862> Try models.json first (this function is called during generation, not with legacy flag check)
L873> `return agent_template, kiro_cfg`
L876> `return (`
L886> `raise ReqError(`

### fn `def strip_json_comments(text: str) -> str` (L892-911)
L893> Removes // and /* */ comments to allow JSONC parsing.
L909> `return "\n".join(cleaned)`

### fn `def load_settings(path: Path) -> dict[str, Any]` (L912-922)
L913> Loads JSON/JSONC settings, removing comments when necessary.
L916> `return json.loads(raw)`
L920> `return json.loads(cleaned)`

### fn `def load_centralized_models(` (L923-926)

### fn `def get_model_tools_for_prompt(` (L974-975)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1011-1031)
L1012-1017> Returns the raw value of `usage_modes[mode]['tools']` for the prompt. Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
L1019> `return None`
L1028> `return mode_entry.get("tools")`
L1029> `return None`

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1032-1038)
L1033> Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
L1036> `return f"[{quoted}]"`

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1039-1048)
L1040> Recursively merges dictionaries, prioritizing incoming values.
L1046> `return base`

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1049-1056)
L1050> Finds the VS Code settings template if available.
L1053> `return candidate`
L1054> `return None`

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1057-1066)
L1058> Generates chat.promptFilesRecommendations from available prompts.
L1061> `return recommendations`
L1064> `return recommendations`

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1067-1075)
L1068> Verifies that the path is under the project root.
L1070> `raise ReqError(`

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1076-1084)
L1077> Saves a backup of VS Code settings if the file exists.
L1079> Never create an absence marker. Backup only if the file exists.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1085-1095)
L1086> Restores VS Code settings from backup, if present.
L1093> Do not remove the target file if no backup exists: restore behavior disabled otherwise.

### fn `def prune_empty_dirs(root: Path) -> None` (L1096-1108)
L1093> Do not remove the target file if no backup exists: restore behavior disabled otherwise.
L1097> Removes empty directories under the specified root.
L1099> `return`

### fn `def remove_generated_resources(project_base: Path) -> None` (L1109-1148)
L1110> Removes resources generated by the tool in the project root.

### fn `def run_remove(args: Namespace) -> None` (L1149-1189)
L1150> Handles the removal of generated resources.
L1156> `raise ReqError(`
L1165> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1168> `raise ReqError(`
L1173> After validation and before any removal, check for a new version.
L1176> Do not perform any restore or removal of .vscode/settings.json during removal.

### fn `def run(args: Namespace) -> None` (L1190-1389)
L1191> Handles the main initialization flow.
L1196> Main flow: validates input, calculates paths, generates resources.
L1199> `return`
L1206> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1214> `raise ReqError(`
L1219> `raise ReqError(`
L1237> `raise ReqError("Error: invalid docs configuration values", 11)`
L1239> `raise ReqError("Error: invalid tests configuration value", 11)`
L1245> `raise ReqError("Error: invalid src configuration values", 11)`
L1285> `raise ReqError("Error: --guidelines-dir must be under the project base", 8)`
L1287> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L1289> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L1292> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L1317> `raise ReqError(`
L1324> Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
L1353> `raise ReqError(`
L1358> After validation and before any operation that modifies the filesystem, check for a new version.
L1388> Copy models configuration to .req/models.json based on legacy mode (REQ-084)
L1389> Skip if --preserve-models is active

- var `VERBOSE = args.verbose` (L1193) — Handles the main initialization flow.
- var `DEBUG = args.debug` (L1194)
- var `PROMPT = prompt_path.stem` (L1527)
### fn `def _format_install_table(` `priv` (L1955-1957)
L1952> Build and print a simple installation report table describing which

### fn `def fmt(row: tuple[str, ...]) -> str` (L1977-1979)
L1978> `return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row))`

- var `EXCLUDED_DIRS = frozenset({` (L1997) — ── Excluded directories for --references and --compress ──────────────────
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2006) — ── Supported source file extensions ──────────────────────────────────────
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2014-2035)
L2011> File extensions considered during source directory scanning.
L2015-2018> Recursively collect source files from the given directories. Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
L2025> Filter out excluded directories (modifies dirnames in-place)
L2033> `return collected`

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2036-2044)
L2037> Check if the parsed args contain a standalone file command.
L2038> `return bool(`

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2045-2052)
L2046> Check if the parsed args contain a project scan command.
L2047> `return bool(`

### fn `def run_files_tokens(files: list[str]) -> None` (L2053-2070)
L2054> Execute --files-tokens: count tokens for arbitrary files.
L2065> `raise ReqError("Error: no valid files provided.", 1)`

### fn `def run_files_references(files: list[str]) -> None` (L2071-2078)
L2072> Execute --files-references: generate markdown for arbitrary files.

### fn `def run_files_compress(files: list[str]) -> None` (L2079-2086)
L2080> Execute --files-compress: compress arbitrary files.

### fn `def run_references(args: Namespace) -> None` (L2087-2098)
L2088> Execute --references: generate markdown for project source files.
L2094> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_compress_cmd(args: Namespace) -> None` (L2099-2110)
L2100> Execute --compress: compress project source files.
L2106> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L2111-2144)
L2112> Resolve project base and src-dirs for --references/--compress.
L2114> `raise ReqError(`
L2124> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L2126> Source dirs can come from args or from config
L2129> Try to load from config
L2135> `raise ReqError(`
L2140> `raise ReqError("Error: no source directories configured.", 1)`
L2142> `return project_base, src_dirs`

### fn `def main(argv: Optional[list[str]] = None) -> int` (L2145-2196)
L2146-2149> CLI entry point for console_scripts and `-m` execution. Returns an exit code (0 success, non-zero on error).
L2154> `return 0`
L2157> `return 0`
L2160> `return 0`
L2162> `return 0`
L2164> Standalone file commands (no --base/--here required)
L2172> `return 0`
L2173> Project scan commands (require --base/--here)
L2179> `return 0`
L2180> Standard init flow requires --base or --here
L2182> `raise ReqError(`
L2188> `return e.code`
L2189> Unexpected error
L2195> `return 1`
L2196> `return 0`

## Comments
- L35: ! @brief Initialize an expected CLI failure payload. @param message Human-readable error message. @param code Process exit code bound to the failur...
- L45: Prints an informational message.
- L50: Prints a debug message if debugging is active.
- L56: Prints a verbose message if verbose mode is active.
- L62: Builds the CLI argument parser.
- L220: Parses command-line arguments into a namespace.
- L225: Reads the package version from __init__.py.
- L235: Handles --ver/--version by printing the version.
- L243: Executes the upgrade using uv.
- L265: Executes the uninstallation using uv.
- L284: Normalizes the release tag by removing a 'v' prefix if present.
- L292: Converts a version into a numeric tuple for comparison. Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
- L316: Returns True if latest is greater than current.
- L329: Checks online for a new version and prints a warning. If the call fails or the response is invalid, it prints nothing and proceeds.
- L371: Ensures the documentation directory exists under the project base.
- L387: Ensures the test directory exists under the project base.
- L403: Ensures the source directory exists under the project base.
- L419: Normalizes the path relative to the project root when possible.
- L454: Resolves the absolute path starting from a normalized value.
- L464: Uniforms path separators for substitutions.
- L473: Calculates the relative path to use in tokens.
- L492: Saves normalized parameters to .req/config.json.
- L507: Loads parameters saved in .req/config.json.
- L519: Fallback to legacy key names from pre-v0.59 config files.
- L544: Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
- L558: If there are no files, use the directory itself.
- L571: Generates a list of relative file paths (no formatting) for printing. Each entry is formatted as `guidelines/file.md` (forward slashes). If there a...
- L589: If there are no files, use the directory itself.
- L604: Copies guidelines templates from resources/guidelines/ to the target directory. Args: guidelines_dest: Target directory where templates will be cop...
- L641: Normalizes the path token optionally preserving the trailing slash.
- L652: Validates that the path is not absolute and raises an error otherwise.
- L661: Returns text with token replacements applied.
- L668: Writes text to disk, ensuring the destination folder exists.
- L676: Copies a file substituting the indicated tokens with their values.
- L683: Normalizes a description by removing superfluous quotes and escapes.
- L693: Converts a Markdown prompt to TOML for Gemini.
- L721: Extracts front matter and body from Markdown.
- L725: Explicitly return two strings to satisfy type annotation.
- L730: Extracts the description from front matter.
- L738: Extracts the argument-hint from front matter, if present.
- L746: Returns the first bullet of the Purpose section.
- L766: Escapes a string for JSON without external delimiters.
- L775: Generates the resource list for the Kiro agent.
- L803: Renders the Kiro agent JSON and populates main fields.
- L830: If parsing fails, return raw template to preserve previous behavior
- L835: Replaces tokens in the specified file.
- L843: Minimal escape for a double-quoted string in YAML.
- L848: Returns the template source or raises an error.
- L859: Loads the Kiro template from centralized models configuration.
- L862: Try models.json first (this function is called during generation, not with legacy flag check)
- L893: Removes // and /* */ comments to allow JSONC parsing.
- L913: Loads JSON/JSONC settings, removing comments when necessary.
- L928: Loads centralized models configuration from common/models.json. Returns a map cli_name -> parsed_json or None if not present. When preserve_models_...
- L938: Priority 1: preserve_models_path if provided and exists
- L942: Priority 2: legacy mode
- L949: Fallback: standard models.json
- L956: Load the centralized configuration
- L964: Extract individual CLI configs
- L977: Extracts model and tools for the prompt from the CLI config. Returns (model, tools) where each value can be None if not available.
- L994-995: Use the unified key name 'tools' across all CLI configs. | Accept either a list of strings or a CSV string in the config.json.
- L1003: Parse comma-separated string into list
- L1012: Returns the raw value of `usage_modes[mode]['tools']` for the prompt. Can return a list of strings, a string, or None depending on how it is define...
- L1033: Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
- L1040: Recursively merges dictionaries, prioritizing incoming values.
- L1050: Finds the VS Code settings template if available.
- L1058: Generates chat.promptFilesRecommendations from available prompts.
- L1068: Verifies that the path is under the project root.
- L1077-1079: Saves a backup of VS Code settings if the file exists. | Never create an absence marker. Backup only if the file exists.
- L1086: Restores VS Code settings from backup, if present.
- L1097: Removes empty directories under the specified root.
- L1110: Removes resources generated by the tool in the project root.
- L1150: Handles the removal of generated resources.
- L1173: After validation and before any removal, check for a new version.
- L1176: Do not perform any restore or removal of .vscode/settings.json during removal.
- L1196: Main flow: validates input, calculates paths, generates resources.
- L1324: Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
- L1358: After validation and before any operation that modifies the filesystem, check for a new version.
- L1388-1389: Copy models configuration to .req/models.json based on legacy mode (REQ-084) | Skip if --preserve-models is active
- L1413: Create requirements.md only if the --docs-dir folder is empty.
- L1423: Generate the file list for the %%GUIDELINES_FILES%% token.
- L1492: Load CLI configs only if requested to include model/tools
- L1503: Determine preserve_models_path (REQ-082)
- L1534: (Removed: bootstrap file inlining and YOLO stop/approval substitution)
- L1550: Precompute description and Claude metadata so provider blocks can reuse them safely.
- L1560: .codex/prompts
- L1569: .codex/skills/req/<prompt>/SKILL.md
- L1599: Gemini TOML
- L1637: .kiro/prompts
- L1647: .claude/agents
- L1673: .github/agents
- L1701: .github/prompts
- L1733: .kiro/agents
- L1763: .opencode/agent
- L1794: .opencode/command
- L1839: .claude/commands/req
- L1897: Load existing settings (if present) and those from the template.
- L1903: If checking/loading fails, consider it empty
- L1908: Merge without modifying original until sure.
- L1918: If final result is identical to existing, do not rewrite nor backup.
- L1923: If changes are expected, create backup only if file exists.
- L1926: Write final settings.
- L1934-1935: Final success notification: printed only when the command completed all | intended filesystem modifications without raising an exception.
- L1942-1943: Print the discovered directories used for token substitutions | as required by REQ-078: one item per line prefixed with '- '.
- L1959: Format the installation summary table aligning header, prompts, and rows.
- L2002: Directories excluded from source scanning in --references and --compress.
- L2015: Recursively collect source files from the given directories. Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
- L2025: Filter out excluded directories (modifies dirnames in-place)
- L2037: Check if the parsed args contain a standalone file command.
- L2046: Check if the parsed args contain a project scan command.
- L2054: Execute --files-tokens: count tokens for arbitrary files.
- L2072: Execute --files-references: generate markdown for arbitrary files.
- L2080: Execute --files-compress: compress arbitrary files.
- L2088: Execute --references: generate markdown for project source files.
- L2100: Execute --compress: compress project source files.
- L2112: Resolve project base and src-dirs for --references/--compress.
- L2126: Source dirs can come from args or from config
- L2129: Try to load from config
- L2146: CLI entry point for console_scripts and `-m` execution. Returns an exit code (0 success, non-zero on error).
- L2164: Standalone file commands (no --base/--here required)
- L2173: Project scan commands (require --base/--here)
- L2180: Standard init flow requires --base or --here

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|18||
|`RESOURCE_ROOT`|var|pub|21||
|`VERBOSE`|var|pub|24||
|`DEBUG`|var|pub|27||
|`ReqError`|class|pub|31-43|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|34-43|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|44-48|def log(msg: str) -> None|
|`dlog`|fn|pub|49-54|def dlog(msg: str) -> None|
|`vlog`|fn|pub|55-60|def vlog(msg: str) -> None|
|`build_parser`|fn|pub|61-218|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|219-223|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|224-233|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|234-241|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|242-263|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|264-282|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|283-290|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|291-314|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|315-327|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|328-369|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|370-385|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|386-401|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|402-417|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|418-452|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|453-462|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|463-469|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|470-471|def compute_sub_path(|
|`save_config`|fn|pub|485-490|def save_config(|
|`load_config`|fn|pub|506-542|def load_config(project_base: Path) -> dict[str, str | li...|
|`generate_guidelines_file_list`|fn|pub|543-569|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|570-600|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`copy_guidelines_templates`|fn|pub|601-602|def copy_guidelines_templates(|
|`make_relative_token`|fn|pub|640-650|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|651-659|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|660-666|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|667-672|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|673-674|def copy_with_replacements(|
|`normalize_description`|fn|pub|682-691|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|692-719|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|720-728|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|729-736|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|737-744|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|745-764|def extract_purpose_first_bullet(body: str) -> str|
|`json_escape`|fn|pub|765-769|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|770-773|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|792-801|def render_kiro_agent(|
|`replace_tokens`|fn|pub|834-841|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|842-846|def yaml_double_quote_escape(value: str) -> str|
|`find_template_source`|fn|pub|847-857|def find_template_source() -> Path|
|`load_kiro_template`|fn|pub|858-891|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|892-911|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|912-922|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|923-926|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|974-975|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1011-1031|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1032-1038|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1039-1048|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1049-1056|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1057-1066|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1067-1075|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1076-1084|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1085-1095|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1096-1108|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1109-1148|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1149-1189|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1190-1389|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1193||
|`DEBUG`|var|pub|1194||
|`PROMPT`|var|pub|1527||
|`_format_install_table`|fn|priv|1955-1957|def _format_install_table(|
|`fmt`|fn|pub|1977-1979|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|1997||
|`SUPPORTED_EXTENSIONS`|var|pub|2006||
|`_collect_source_files`|fn|priv|2014-2035|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_is_standalone_command`|fn|priv|2036-2044|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2045-2052|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2053-2070|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2071-2078|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2079-2086|def run_files_compress(files: list[str]) -> None|
|`run_references`|fn|pub|2087-2098|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2099-2110|def run_compress_cmd(args: Namespace) -> None|
|`_resolve_project_src_dirs`|fn|priv|2111-2144|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|2145-2196|def main(argv: Optional[list[str]] = None) -> int|


---

# compress.py | Python | 382L | 11 symbols | 5 imports | 41 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress.py`
> compress.py - Source code compressor for LLM context optimization. Parses a source file and removes all comments (inline, single-line, ...

## Imports
```
import os
import re
import sys
from .source_analyzer import build_language_specs
import argparse
```

## Definitions

- var `EXT_LANG_MAP = {` (L29) — Extension-to-language map (mirrors generate_markdown.py)
- var `INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}` (L41) — ! @brief Extension-to-language normalization map for compression input.
### fn `def _get_specs()` `priv` (L48-57)
L45> ! @brief Cached language specification dictionary initialized lazily.
L49-51> ! @brief Return cached language specifications, initializing once. @return Dictionary mapping normalized language keys to language specs.
L55> `return _specs_cache`

### fn `def detect_language(filepath: str) -> str | None` (L58-66)
L59-62> ! @brief Detect language key from file extension. @param filepath Source file path. @return Normalized language key, or None when extension is unsupported.
L64> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L67-102)
L68> Check if position `pos` in `line` is inside a string literal.
L75> Check for escaped delimiter (single-char only)
L77> Count consecutive backslashes
L100> `return in_string is not None`

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L103-140)
L105> Remove trailing single-line comment from a code line.
L107> `return line`
L130> `return line[:i]`
L138> `return line`

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L141-149)
L142> Check if a line is a standalone Python docstring (triple-quote only).
L146> `return True`
L147> `return False`

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L150-157)
L152> Format compressed entries, optionally prefixing original line numbers.
L154> `return '\n'.join(text for _, text in entries)`
L155> `return '\n'.join(f"L{lineno}> {text}" for lineno, text in entries)`

### fn `def compress_source(source: str, language: str,` (L158-329)
L160-171> Compress source code by removing comments, blank lines, and extra whitespace. Preserves indentation for indent-significant languages (Python, Haskell, Elixir). Args: source: The source code string. language: Language identifier (e.g. "python", "javascript"). include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Compressed source code string.
L175> `raise ValueError(f"Unsupported language: {language}")`
L180> list of (original_line_number, text)
L187> Python: also handle ''' as multi-comment
L196> --- Handle multi-line comment continuation ---
L199> End of multi-line comment found
L203> Process remainder as a new line
L210-236> --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docstring: if python_docstring_delim in line: end_pos = line.index(python_docstring_delim) + 3 remainder = line[end_pos:] in_python_docstring = False python_docstring_delim = None if remainder.strip(): lines[i] = remainder continue i += 1 continue stripped = line.strip() Skip empty lines if not stripped: i += 1 continue --- Detect multi-line comment start --- if mc_start: For Python, triple-quotes can be strings or docstrings. We only strip standalone docstrings (line starts with triple-quote after optional whitespace). if is_python: for q in ('"""', "'''"):
L238> Single-line docstring: """...
L240> Check it's not a variable assignment like x = """...
L244> Standalone docstring or assigned — skip if standalone
L248> If code before and not assignment, keep line
L250> Multi-line docstring start
L261> Non-Python: check for multi-line comment start
L264> Check if inside a string
L267> Check for same-line close
L271> Single-line block comment: remove it
L278> Re-process this reconstructed line
L282> Multi-line comment starts here
L291> --- Full-line single-line comment ---
L293> Special: keep shebangs
L299> --- Remove inline comment ---
L303> --- Clean whitespace ---
L305> Keep leading whitespace, strip trailing
L311> Collapse internal multiple spaces (but not in strings)
L319> Remove trailing whitespace
L327> `return _format_result(result, include_line_numbers)`

### fn `def compress_file(filepath: str, language: str | None = None,` (L330-354)
L332-341> Compress a source file by removing comments and extra whitespace. Args: filepath: Path to the source file. language: Optional language override. Auto-detected if None. include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Compressed source code string.
L345> `raise ValueError(`
L352> `return compress_source(source, language, include_line_numbers)`

### fn `def main()` (L355-380)
L356> ! @brief Execute the standalone compression CLI.
L370> `sys.exit(1)`
L378> `sys.exit(1)`

## Comments
- L2: compress.py - Source code compressor for LLM context optimization. Parses a source file and removes all comments (inline, single-line, ...
- L42: ! @brief Languages requiring indentation-preserving compression behavior.
- L49: ! @brief Return cached language specifications, initializing once. @return Dictionary mapping normalized language keys to language specs.
- L59: ! @brief Detect language key from file extension. @param filepath Source file path. @return Normalized language key, or None when extension is unsu...
- L68: Check if position `pos` in `line` is inside a string literal.
- L75-77: Check for escaped delimiter (single-char only) | Count consecutive backslashes
- L105: Remove trailing single-line comment from a code line.
- L142: Check if a line is a standalone Python docstring (triple-quote only).
- L152: Format compressed entries, optionally prefixing original line numbers.
- L160: Compress source code by removing comments, blank lines, and extra whitespace. Preserves indentation for indent-significant languages (Python, Haske...
- L187: Python: also handle ''' as multi-comment
- L196: --- Handle multi-line comment continuation ---
- L199: End of multi-line comment found
- L203: Process remainder as a new line
- L210-240: --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docs... | Single-line docstring: """... | Check it's not a variable assignment like x = """...
- L244: Standalone docstring or assigned — skip if standalone
- L248-250: If code before and not assignment, keep line | Multi-line docstring start
- L261: Non-Python: check for multi-line comment start
- L264: Check if inside a string
- L267: Check for same-line close
- L271: Single-line block comment: remove it
- L278: Re-process this reconstructed line
- L282: Multi-line comment starts here
- L291-293: --- Full-line single-line comment --- | Special: keep shebangs
- L299: --- Remove inline comment ---
- L303-305: --- Clean whitespace --- | Keep leading whitespace, strip trailing
- L311: Collapse internal multiple spaces (but not in strings)
- L319: Remove trailing whitespace
- L332: Compress a source file by removing comments and extra whitespace. Args: filepath: Path to the source file. ...
- L356: ! @brief Execute the standalone compression CLI.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|29||
|`INDENT_SIGNIFICANT`|var|pub|41||
|`_get_specs`|fn|priv|48-57|def _get_specs()|
|`detect_language`|fn|pub|58-66|def detect_language(filepath: str) -> str | None|
|`_is_in_string`|fn|priv|67-102|def _is_in_string(line: str, pos: int, string_delimiters:...|
|`_remove_inline_comment`|fn|priv|103-140|def _remove_inline_comment(line: str, single_comment: str,|
|`_is_python_docstring_line`|fn|priv|141-149|def _is_python_docstring_line(line: str) -> bool|
|`_format_result`|fn|priv|150-157|def _format_result(entries: list[tuple[int, str]],|
|`compress_source`|fn|pub|158-329|def compress_source(source: str, language: str,|
|`compress_file`|fn|pub|330-354|def compress_file(filepath: str, language: str | None = N...|
|`main`|fn|pub|355-380|def main()|


---

# compress_files.py | Python | 95L | 2 symbols | 4 imports | 4 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress_files.py`
> compress_files.py - Compress and concatenate multiple source files. Uses the compress module to strip comments and whitespace from each input ...

## Imports
```
import os
import sys
from .compress import compress_file, detect_language
import argparse
```

## Definitions

### fn `def compress_files(filepaths: list[str],` (L24-74)
L26-41> Compress multiple source files and concatenate with identifying headers. Each file is compressed and prefixed with a header line: @@@ <path> | <lang> Files are separated by a blank line. Args: filepaths: List of source file paths. include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Concatenated compressed output string. Raises: ValueError: If no files could be processed.
L67> `raise ValueError("No valid source files processed")`
L72> `return "\n\n".join(parts)`

### fn `def main()` (L75-93)
L76> ! @brief Execute the multi-file compression CLI command.
L91> `sys.exit(1)`

## Comments
- L2: compress_files.py - Compress and concatenate multiple source files. Uses the compress module to strip comments and whitespace from each input ...
- L26: Compress multiple source files and concatenate with identifying headers. Each file is compressed and prefixed with a header line: @@@ <path> | <lan...
- L76: ! @brief Execute the multi-file compression CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`compress_files`|fn|pub|24-74|def compress_files(filepaths: list[str],|
|`main`|fn|pub|75-93|def main()|


---

# generate_markdown.py | Python | 128L | 4 symbols | 3 imports | 7 comments
> Path: `/home/ogekuri/useReq/src/usereq/generate_markdown.py`
> generate_markdown.py - Generate concatenated markdown from arbitrary source files. Analyzes each input file with source_analyzer and produces a single markdown ...

## Imports
```
import os
import sys
from .source_analyzer import SourceAnalyzer, format_markdown
```

## Definitions

- var `EXT_LANG_MAP = {` (L23) — Map file extensions to languages
### fn `def detect_language(filepath: str) -> str | None` (L50-55)
L47> ! @brief Extension-to-language normalization map for markdown generation.
L51> Detect language from file extension.
L53> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def generate_markdown(filepaths: list[str]) -> str` (L56-111)
L57-67> Analyze source files and return concatenated markdown. Args: filepaths: List of source file paths to analyze. Returns: Concatenated markdown string with all file analyses. Raises: ValueError: If no valid source files are found.
L104> `raise ValueError("No valid source files processed")`
L109> `return "\n\n---\n\n".join(md_parts)`

### fn `def main()` (L112-126)
L113> ! @brief Execute the standalone markdown generation CLI command.
L117> `sys.exit(1)`
L124> `sys.exit(1)`

## Comments
- L2: generate_markdown.py - Generate concatenated markdown from arbitrary source files. Analyzes each input file with source_analyzer and produces a sin...
- L51: Detect language from file extension.
- L57: Analyze source files and return concatenated markdown. Args: filepaths: List of source file paths to analyze. ...
- L113: ! @brief Execute the standalone markdown generation CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|23||
|`detect_language`|fn|pub|50-55|def detect_language(filepath: str) -> str | None|
|`generate_markdown`|fn|pub|56-111|def generate_markdown(filepaths: list[str]) -> str|
|`main`|fn|pub|112-126|def main()|


---

# pdoc_utils.py | Python | 83L | 3 symbols | 6 imports | 5 comments
> Path: `/home/ogekuri/useReq/src/usereq/pdoc_utils.py`
> Utilities for generating pdoc documentation.

## Imports
```
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence
```

## Definitions

### fn `def _normalize_modules(modules: str | Iterable[str]) -> list[str]` `priv` (L12-18)
L13> Returns a list of modules from either a string or an iterable.
L15> `return [modules]`
L16> `return list(modules)`

### fn `def _run_pdoc(command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess` `priv` (L19-30)
L20> Runs pdoc and captures output for error handling.
L21> `return subprocess.run(`

### fn `def generate_pdoc_docs(` (L31-35)

## Comments
- L13: Returns a list of modules from either a string or an iterable.
- L20: Runs pdoc and captures output for error handling.
- L37: Generates or updates pdoc documentation in the target output directory. Args: output_dir: Directory where HTML documentation will be written. ...
- L74: Fallback for pdoc versions that do not support --all-submodules.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_normalize_modules`|fn|priv|12-18|def _normalize_modules(modules: str | Iterable[str]) -> l...|
|`_run_pdoc`|fn|priv|19-30|def _run_pdoc(command: list[str], *, env: dict[str, str],...|
|`generate_pdoc_docs`|fn|pub|31-35|def generate_pdoc_docs(|


---

# source_analyzer.py | Python | 2020L | 56 symbols | 7 imports | 130 comments
> Path: `/home/ogekuri/useReq/src/usereq/source_analyzer.py`
> source_analyzer.py - Multi-language source code analyzer. Inspired by tree-sitter, this module analyzes source files across multiple ...

## Imports
```
import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
```

## Definitions

### class `class ElementType(Enum)` : Enum (L29-57)
- var `FUNCTION = auto()` (L31) L30> Element types recognized in source code.
- var `METHOD = auto()` (L32)
- var `CLASS = auto()` (L33)
- var `STRUCT = auto()` (L34)
- var `ENUM = auto()` (L35)
- var `TRAIT = auto()` (L36)
- var `INTERFACE = auto()` (L37)
- var `MODULE = auto()` (L38)
- var `IMPL = auto()` (L39)
- var `MACRO = auto()` (L40)
- var `CONSTANT = auto()` (L41)
- var `VARIABLE = auto()` (L42)
- var `TYPE_ALIAS = auto()` (L43)
- var `IMPORT = auto()` (L44)
- var `DECORATOR = auto()` (L45)
- var `COMMENT_SINGLE = auto()` (L46)
- var `COMMENT_MULTI = auto()` (L47)
- var `COMPONENT = auto()` (L48)
- var `PROTOCOL = auto()` (L49)
- var `EXTENSION = auto()` (L50)
- var `UNION = auto()` (L51)
- var `NAMESPACE = auto()` (L52)
- var `PROPERTY = auto()` (L53)
- var `SIGNAL = auto()` (L54)
- var `TYPEDEF = auto()` (L55)

### class `class SourceElement` `@dataclass` (L59-108)
L60> Element found in source file.
- fn `def type_label(self) -> str` (L75-108)
  L76-78> ! @brief Return the normalized printable label for element_type. @return Stable uppercase label used in markdown rendering output.
  L106> `return labels.get(self.element_type, "UNKNOWN")`

### class `class LanguageSpec` `@dataclass` (L110-119)
L111> Language recognition pattern specification.

### fn `def build_language_specs() -> dict` (L120-319)
L121> Build specifications for all supported languages.
L124> ── Python ──────────────────────────────────────────────────────────
L145> ── C ───────────────────────────────────────────────────────────────
L179> ── C++ ─────────────────────────────────────────────────────────────
L209> ── Rust ────────────────────────────────────────────────────────────
L241> ── JavaScript ──────────────────────────────────────────────────────
L269> ── TypeScript ──────────────────────────────────────────────────────
L302> ── Java ────────────────────────────────────────────────────────────

### class `class SourceAnalyzer` (L672-871)
- fn `def __init__(self)` `priv` (L680-683) L673> Multi-language source file analyzer. Analyzes a source file identifying definitions, comments and...
  L681> ! @brief Initialize analyzer state with language specifications.
- fn `def get_supported_languages(self) -> list` (L684-693) L681> ! @brief Initialize analyzer state with language specifications.
  L685> Return list of supported languages (without aliases).
  L692> `return sorted(result)`
- fn `def analyze(self, filepath: str, language: str) -> list` (L694-841)
  L695> Analyze a source file and return the list of SourceElement found.
  L698> `raise ValueError(`
  L710> Multi-line comment state
  L718> ── Multi-line comment handling ──────────────────────────
  L735> ── Multi-line comment start ────────────────────────────
  L737> Special handling for Python docstrings and =begin/=pod blocks
  L741> Check not inside a string
  L743> Check if multi-line comment closes on same line
  L755> Python: """ ... """ sulla stessa riga
  L772> ── Single-line comment ───────────────────────────────────
  L776> If comment is the entire line (aside from whitespace)
  L787> Inline comment: add both element and comment
  L797> ── Language patterns ─────────────────────────────────────
  L810> Single-line types: don't search for block
  L827> Limit extract to max 5 lines for readability
  L840> `return elements`
- fn `def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool` `priv` (L842-870)
  L843> Check if position pos is inside a string literal.
  L869> `return in_string`

### fn `def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]` `priv` (L871-904)
L872> Find position of single-line comment, ignoring strings.
L874> `return None`
L891> `return i`
L903> `return None`

### fn `def _find_block_end(self, lines: list, start_idx: int,` `priv` (L905-980)
L907-911> Find the end of a block (function, class, struct, etc.). Returns the index (1-based) of the final line of the block. Limits search for performance.
L912> Per Python: basato sull'indentazione
L925> `return end`
L927> Per linguaggi con parentesi graffe
L944> `return end + 1`
L946> If no opening braces found, return just the first line
L948> `return start_idx + 1`
L949> `return end`
L951> Per Ruby/Elixir/Lua: basato su end keyword
L960> `return end + 1`
L962> `return start_idx + 1`
L964> Per Haskell: basato sull'indentazione
L977> `return end`
L979> `return start_idx + 1`

### fn `def enrich(self, elements: list, language: str,` (L983-1000)
L981> ── Enrichment methods for LLM-optimized output ───────────────────
L985-990> Enrich elements with signatures, hierarchy, visibility, inheritance. Call after analyze() to add metadata for LLM-optimized markdown output. Modifies elements in-place and returns them. If filepath is provided, also extracts body comments and exit points.
L999> `return elements`

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L1001-1029)
L1002-1007> Extract clean identifiers from name fields. Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.
L1012> Try to re-extract the name from the element's extract line
L1013> using the original pattern (which has group 2 as the identifier)
L1021> Take highest non-None non-empty group
L1022> (group 2+ = identifier, group 1 = full match)

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1030-1044)
L1031> Extract clean signatures from element extracts.

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1045-1080)
L1046-1050> Detect parent-child relationships between elements. Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1081-1092)
L1082> Extract visibility/access modifiers from elements.

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1093-1137)
L1095> Parse visibility modifier from a signature line.
L1098> `return "priv"`
L1100> `return "priv"`
L1101> `return "pub"`
L1104> `return "pub"`
L1106> `return "priv"`
L1108> `return "prot"`
L1110> `return "int"`
L1111> `return None`
L1114> `return "pub"`
L1115> `return "priv"`
L1118> `return "pub"`
L1119> `return "priv"`
L1122> `return "priv"`
L1124> `return "fpriv"`
L1126> `return "pub"`
L1127> `return None`
L1130> `return "pub"`
L1132> `return "priv"`
L1134> `return "prot"`
L1135> `return None`
L1136> `return None`

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1138-1148)
L1139> Extract inheritance/implementation info from class-like elements.

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1149-1177)
L1151> Parse inheritance info from a class/struct declaration line.
L1154> `return m.group(1).strip() if m else None`
L1163> `return ", ".join(parts) if parts else None`
L1167> `return m.group(1).strip() if m else None`
L1172> `return m.group(1).strip() if m else None`
L1175> `return m.group(1) if m else None`
L1176> `return None`

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1185-1314)
L1187-1195> Extract comments and exit points from within function/class bodies. Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.
L1198> `return`
L1204> `return`
L1206> Only process definitions that span multiple lines
L1224> Scan the body (lines after the definition line)
L1225> 1-based, skip def line itself
L1239> Multi-line comment tracking within body
L1254> Check for multi-line comment start
L1259> Single-line multi-comment
L1283> Single-line comment (full line)
L1293> Standalone comment line in body
L1299> Inline comment after code
L1304> Exit points

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1316-1326)
L1317> Strip comment markers from a single line of comment text.
L1324> `return s`

### fn `def format_output(elements: list, filepath: str, language: str,` (L1327-1446)
L1329> Format structured analysis output.
L1339> ── Definitions section ────────────────────────────────────────────
L1363> Prefix with line number
L1373> ── Comments section ───────────────────────────────────────────────
L1406> ── Complete structured listing ────────────────────────────────────
L1413> Sort by start line
L1431> Show first line of extract
L1444> `return "\n".join(output_lines)`

### fn `def _md_loc(elem) -> str` `priv` (L1447-1453)
L1448> Format element location compactly for markdown.
L1450> `return f"L{elem.line_start}"`
L1451> `return f"L{elem.line_start}-{elem.line_end}"`

### fn `def _md_kind(elem) -> str` `priv` (L1454-1481)
L1455> Short kind label for markdown output.
L1479> `return mapping.get(elem.element_type, "?")`

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1482-1507)
L1483-1488> Extract clean text content from a comment element. Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.
L1493> Strip comment markers
L1498> Strip multi-line markers
L1505> `return text`

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1508-1523)
L1509> Extract clean text lines from a multi-line comment (preserving structure).
L1521> `return cleaned`

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1524-1589)
L1525-1532> Build maps that associate comments with their adjacent definitions. Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)
L1535> Identify definition elements
L1543> Build adjacency map: comments preceding a definition (within 2 lines)
L1552> Extract file description from first comment(s), skip shebangs
L1557> Skip shebang lines and empty comments
L1565> Skip inline comments (name == "inline")
L1570> Check if this comment precedes a definition within 2 lines
L1577> Stop if we hit another element
L1582> Skip file-level description (already captured)
L1587> `return doc_for_def, standalone_comments, file_description`

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1590-1645)
L1592-1598> Render body comments and exit points for a definition element. Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.
L1599> Build maps by line number
L1608> Collect all annotated line numbers
L1612> Skip if within an excluded range (child element)
L1626> Merge: show exit point code with comment as context
L1629> Strip inline comment from exit_text if it contains it

### fn `def format_markdown(elements: list, filepath: str, language: str,` (L1646-1845)
L1648-1658> Format analysis as compact Markdown optimized for LLM agent consumption. Produces token-efficient output with: - File header with language, line count, element summary, and description - Imports in a code block - Hierarchical definitions with line-numbered doc comments - Body comments (L<N>> text) and exit points (L<N>> `return ...`) - Comments grouped with their relevant definitions - Standalone section/region comments preserved as context - Symbol index table for quick reference by line number
L1667> Build comment association maps
L1670> ── Header ────────────────────────────────────────────────────────
L1682> ── Imports ───────────────────────────────────────────────────────
L1695> ── Build decorator map: line -> decorator text ───────────────────
L1701> ── Definitions ───────────────────────────────────────────────────
L1741> Collect associated doc comments for this definition
L1764> For impl blocks, use the full first line as sig
L1772> Show associated doc comment with line number
L1782> Body annotations: comments and exit points
L1783> For containers with children, exclude annotations
L1784> that fall within a child's line range (including
L1785> doc comments that immediately precede the child)
L1790> Extend range to include preceding doc comment
L1799> Children with their doc comments and body annotations
L1821> Child body annotations (indented)
L1827> ── Standalone Comments (section/region markers, TODOs, notes) ────
L1830> Group consecutive comments (within 2 lines of each other)

### fn `def main()` (L1901-2018)
L1902> ! @brief Execute the standalone source analyzer CLI command.
L1967> `sys.exit(0)`
L1973> `sys.exit(1)`
L1976> `sys.exit(1)`
L1978> Optional filtering

## Comments
- L2: source_analyzer.py - Multi-language source code analyzer. Inspired by tree-sitter, this module analyzes source files across multiple ...
- L60: Element found in source file.
- L76: ! @brief Return the normalized printable label for element_type. @return Stable uppercase label used in markdown rendering output.
- L111: Language recognition pattern specification.
- L121: Build specifications for all supported languages.
- L124: ── Python ──────────────────────────────────────────────────────────
- L145: ── C ───────────────────────────────────────────────────────────────
- L179: ── C++ ─────────────────────────────────────────────────────────────
- L209: ── Rust ────────────────────────────────────────────────────────────
- L241: ── JavaScript ──────────────────────────────────────────────────────
- L269: ── TypeScript ──────────────────────────────────────────────────────
- L302: ── Java ────────────────────────────────────────────────────────────
- L334: ── Go ──────────────────────────────────────────────────────────────
- L361: ── Ruby ────────────────────────────────────────────────────────────
- L383: ── PHP ─────────────────────────────────────────────────────────────
- L407: ── Swift ───────────────────────────────────────────────────────────
- L437: ── Kotlin ──────────────────────────────────────────────────────────
- L466: ── Scala ───────────────────────────────────────────────────────────
- L492: ── Lua ─────────────────────────────────────────────────────────────
- L508: ── Shell (Bash) ────────────────────────────────────────────────────
- L528: ── Perl ────────────────────────────────────────────────────────────
- L546: ── Haskell ─────────────────────────────────────────────────────────
- L568: ── Zig ─────────────────────────────────────────────────────────────
- L592: ── Elixir ──────────────────────────────────────────────────────────
- L614: ── C# ──────────────────────────────────────────────────────────────
- L653: Common aliases
- L685: Return list of supported languages (without aliases).
- L695: Analyze a source file and return the list of SourceElement found.
- L710: Multi-line comment state
- L718: ── Multi-line comment handling ──────────────────────────
- L735-737: ── Multi-line comment start ──────────────────────────── | Special handling for Python docstrings and =begin/=pod blocks
- L741-743: Check not inside a string | Check if multi-line comment closes on same line
- L755: Python: """ ... """ sulla stessa riga
- L772: ── Single-line comment ───────────────────────────────────
- L776: If comment is the entire line (aside from whitespace)
- L787: Inline comment: add both element and comment
- L797: ── Language patterns ─────────────────────────────────────
- L810: Single-line types: don't search for block
- L827: Limit extract to max 5 lines for readability
- L843: Check if position pos is inside a string literal.
- L872: Find position of single-line comment, ignoring strings.
- L907-912: Find the end of a block (function, class, struct, etc.). Returns the index (1-based) of the final... | Per Python: basato sull'indentazione
- L927: Per linguaggi con parentesi graffe
- L946: If no opening braces found, return just the first line
- L951: Per Ruby/Elixir/Lua: basato su end keyword
- L964: Per Haskell: basato sull'indentazione
- L985: Enrich elements with signatures, hierarchy, visibility, inheritance. Call after analyze() to add metadata for LLM-optimized markdown output. Modifi...
- L1002: Extract clean identifiers from name fields. Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead o...
- L1012-1013: Try to re-extract the name from the element's extract line | using the original pattern (which has group 2 as the identifier)
- L1021-1022: Take highest non-None non-empty group | (group 2+ = identifier, group 1 = full match)
- L1031: Extract clean signatures from element extracts.
- L1046: Detect parent-child relationships between elements. Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside conta...
- L1082: Extract visibility/access modifiers from elements.
- L1095: Parse visibility modifier from a signature line.
- L1139: Extract inheritance/implementation info from class-like elements.
- L1151: Parse inheritance info from a class/struct declaration line.
- L1178: ── Exit point patterns per language family ──────────────────────
- L1187: Extract comments and exit points from within function/class bodies. Reads the source file and scans each definition's line range for: - Single-line...
- L1206: Only process definitions that span multiple lines
- L1224: Scan the body (lines after the definition line)
- L1239: Multi-line comment tracking within body
- L1254: Check for multi-line comment start
- L1259: Single-line multi-comment
- L1283: Single-line comment (full line)
- L1293: Standalone comment line in body
- L1299: Inline comment after code
- L1304: Exit points
- L1317: Strip comment markers from a single line of comment text.
- L1329: Format structured analysis output.
- L1339: ── Definitions section ────────────────────────────────────────────
- L1363: Prefix with line number
- L1373: ── Comments section ───────────────────────────────────────────────
- L1406: ── Complete structured listing ────────────────────────────────────
- L1413: Sort by start line
- L1431: Show first line of extract
- L1448: Format element location compactly for markdown.
- L1455: Short kind label for markdown output.
- L1483: Extract clean text content from a comment element. Args: comment_elem: SourceElement with comment content ...
- L1493: Strip comment markers
- L1498: Strip multi-line markers
- L1509: Extract clean text lines from a multi-line comment (preserving structure).
- L1525: Build maps that associate comments with their adjacent definitions. Returns: - doc_for_def: dict mapping def line_start -> list of comment texts ...
- L1535: Identify definition elements
- L1543: Build adjacency map: comments preceding a definition (within 2 lines)
- L1552: Extract file description from first comment(s), skip shebangs
- L1557: Skip shebang lines and empty comments
- L1565: Skip inline comments (name == "inline")
- L1570: Check if this comment precedes a definition within 2 lines
- L1577: Stop if we hit another element
- L1582: Skip file-level description (already captured)
- L1592-1599: Render body comments and exit points for a definition element. Merges body_comments and exit_poin... | Build maps by line number
- L1608: Collect all annotated line numbers
- L1612: Skip if within an excluded range (child element)
- L1626: Merge: show exit point code with comment as context
- L1629: Strip inline comment from exit_text if it contains it
- L1648: Format analysis as compact Markdown optimized for LLM agent consumption. Produces token-efficient output with: - File header with language, line co...
- L1667: Build comment association maps
- L1670: ── Header ────────────────────────────────────────────────────────
- L1682: ── Imports ───────────────────────────────────────────────────────
- L1695: ── Build decorator map: line -> decorator text ───────────────────
- L1701: ── Definitions ───────────────────────────────────────────────────
- L1741: Collect associated doc comments for this definition
- L1764: For impl blocks, use the full first line as sig
- L1772: Show associated doc comment with line number
- L1782-1785: Body annotations: comments and exit points | For containers with children, exclude annotations | that fall within a child's line range (including | doc comments that immediately precede the child)
- L1790: Extend range to include preceding doc comment
- L1799: Children with their doc comments and body annotations
- L1821: Child body annotations (indented)
- L1827: ── Standalone Comments (section/region markers, TODOs, notes) ────
- L1830: Group consecutive comments (within 2 lines of each other)
- L1849: Multi-line comment block: show as region
- L1862: ── Symbol Index ──────────────────────────────────────────────────
- L1882-1883: Only show sig for functions/methods/classes (not vars/consts | which already show full content in Definitions section)
- L1902: ! @brief Execute the standalone source analyzer CLI command.
- L1978: Optional filtering

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ElementType`|class|pub|29-57|class ElementType(Enum)|
|`ElementType.FUNCTION`|var|pub|31||
|`ElementType.METHOD`|var|pub|32||
|`ElementType.CLASS`|var|pub|33||
|`ElementType.STRUCT`|var|pub|34||
|`ElementType.ENUM`|var|pub|35||
|`ElementType.TRAIT`|var|pub|36||
|`ElementType.INTERFACE`|var|pub|37||
|`ElementType.MODULE`|var|pub|38||
|`ElementType.IMPL`|var|pub|39||
|`ElementType.MACRO`|var|pub|40||
|`ElementType.CONSTANT`|var|pub|41||
|`ElementType.VARIABLE`|var|pub|42||
|`ElementType.TYPE_ALIAS`|var|pub|43||
|`ElementType.IMPORT`|var|pub|44||
|`ElementType.DECORATOR`|var|pub|45||
|`ElementType.COMMENT_SINGLE`|var|pub|46||
|`ElementType.COMMENT_MULTI`|var|pub|47||
|`ElementType.COMPONENT`|var|pub|48||
|`ElementType.PROTOCOL`|var|pub|49||
|`ElementType.EXTENSION`|var|pub|50||
|`ElementType.UNION`|var|pub|51||
|`ElementType.NAMESPACE`|var|pub|52||
|`ElementType.PROPERTY`|var|pub|53||
|`ElementType.SIGNAL`|var|pub|54||
|`ElementType.TYPEDEF`|var|pub|55||
|`SourceElement`|class|pub|59-108|class SourceElement|
|`SourceElement.type_label`|fn|pub|75-108|def type_label(self) -> str|
|`LanguageSpec`|class|pub|110-119|class LanguageSpec|
|`build_language_specs`|fn|pub|120-319|def build_language_specs() -> dict|
|`SourceAnalyzer`|class|pub|672-871|class SourceAnalyzer|
|`SourceAnalyzer.__init__`|fn|priv|680-683|def __init__(self)|
|`SourceAnalyzer.get_supported_languages`|fn|pub|684-693|def get_supported_languages(self) -> list|
|`SourceAnalyzer.analyze`|fn|pub|694-841|def analyze(self, filepath: str, language: str) -> list|
|`SourceAnalyzer._in_string_context`|fn|priv|842-870|def _in_string_context(self, line: str, pos: int, spec: L...|
|`_find_comment`|fn|priv|871-904|def _find_comment(self, line: str, spec: LanguageSpec) ->...|
|`_find_block_end`|fn|priv|905-980|def _find_block_end(self, lines: list, start_idx: int,|
|`enrich`|fn|pub|983-1000|def enrich(self, elements: list, language: str,|
|`_clean_names`|fn|priv|1001-1029|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1030-1044|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1045-1080|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1081-1092|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1093-1137|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1138-1148|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1149-1177|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1185-1314|def _extract_body_annotations(self, elements: list,|
|`_clean_comment_line`|fn|priv|1316-1326|def _clean_comment_line(text: str, spec) -> str|
|`format_output`|fn|pub|1327-1446|def format_output(elements: list, filepath: str, language...|
|`_md_loc`|fn|priv|1447-1453|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1454-1481|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1482-1507|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1508-1523|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1524-1589|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1590-1645|def _render_body_annotations(out: list, elem, indent: str...|
|`format_markdown`|fn|pub|1646-1845|def format_markdown(elements: list, filepath: str, langua...|
|`main`|fn|pub|1901-2018|def main()|


---

# token_counter.py | Python | 107L | 7 symbols | 2 imports | 8 comments
> Path: `/home/ogekuri/useReq/src/usereq/token_counter.py`
> token_counter.py - Token and character counting for generated output. Uses tiktoken for accurate token counting compatible with ...

## Imports
```
import os
import tiktoken
```

## Definitions

### class `class TokenCounter` (L13-34)
- fn `def __init__(self, encoding_name: str = "cl100k_base")` `priv` (L16-21) L14> Count tokens using tiktoken encoding (cl100k_base by default).
  L17-19> ! @brief Initialize token counter with a specific tiktoken encoding. @param encoding_name Name of tiktoken encoding used for tokenization.
- fn `def count_tokens(self, content: str) -> int` (L22-28) L17> ! @brief Initialize token counter with a specific tiktoken encoding. @param encoding_name Name of...
  L23> Count tokens in content string.
  L25> `return len(self.encoding.encode(content, disallowed_special=()))`
  L27> `return 0`
- fn `def count_chars(content: str) -> int` (L30-34)
  L31> Count characters in content string.
  L32> `return len(content)`

### fn `def count_file_metrics(content: str,` (L35-47)
L37-40> Count tokens and chars for a content string. Returns dict with 'tokens' and 'chars' keys.
L42> `return {`

### fn `def count_files_metrics(file_paths: list,` (L48-75)
L50-54> Count tokens and chars for a list of files. Returns a list of dicts with 'file', 'tokens', 'chars' keys. Errors are reported with tokens=0, chars=0, and an 'error' key.
L73> `return results`

### fn `def format_pack_summary(results: list) -> str` (L76-107)
L77-84> Format a pack summary string from a list of file metrics. Args: results: list of dicts from count_files_metrics(). Returns: Formatted summary string with per-file details and totals.
L107> `return "\n".join(lines)`

## Comments
- L23: Count tokens in content string.
- L31: Count characters in content string.
- L37: Count tokens and chars for a content string. Returns dict with 'tokens' and 'chars' keys.
- L50: Count tokens and chars for a list of files. Returns a list of dicts with 'file', 'tokens', 'chars' keys. Errors are reported with tokens=0, chars=0...
- L77: Format a pack summary string from a list of file metrics. Args: results: list of dicts from count_files_metrics(). ...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`TokenCounter`|class|pub|13-34|class TokenCounter|
|`TokenCounter.__init__`|fn|priv|16-21|def __init__(self, encoding_name: str = "cl100k_base")|
|`TokenCounter.count_tokens`|fn|pub|22-28|def count_tokens(self, content: str) -> int|
|`TokenCounter.count_chars`|fn|pub|30-34|def count_chars(content: str) -> int|
|`count_file_metrics`|fn|pub|35-47|def count_file_metrics(content: str,|
|`count_files_metrics`|fn|pub|48-75|def count_files_metrics(file_paths: list,|
|`format_pack_summary`|fn|pub|76-107|def format_pack_summary(results: list) -> str|

