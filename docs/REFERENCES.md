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
        ├── generate_markdown.py
        ├── pdoc_utils.py
        ├── source_analyzer.py
        └── token_counter.py
```

# __init__.py | Python | 22L | 0 symbols | 8 imports | 3 comments
> Path: `/home/ogekuri/useReq/src/usereq/__init__.py`
> ! @brief Package entry point for useReq automation. @details This file exposes lightweight metadata and a convenient re-export of the `main` CLI entry point, so callers can use `from usereq import ...

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
- L6: The current version of the package.
- L22: ! @brief Public package exports for CLI entrypoint and utility submodules.


---

# __main__.py | Python | 8L | 0 symbols | 2 imports | 1 comments
> Path: `/home/ogekuri/useReq/src/usereq/__main__.py`
> ! @brief Allows execution of the tool as a module.

## Imports
```
from .cli import main
import sys
```


---

# cli.py | Python | 2340L | 87 symbols | 20 imports | 144 comments
> Path: `/home/ogekuri/useReq/src/usereq/cli.py`
> ! @brief CLI entry point implementing the useReq initialization flow.

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

- var `REPO_ROOT = Path(__file__).resolve().parents[2]` (L19)
- var `RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"` (L22) — The absolute path to the repository root.
- var `VERBOSE = False` (L25) — The absolute path to the resources directory.
- var `DEBUG = False` (L28) — Whether verbose output is enabled.
### class `class ReqError(Exception)` : Exception (L32-45)
L29> Whether debug output is enabled.
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L36-45) L33> ! @brief Dedicated exception for expected CLI errors.
  L37-40> ! @brief Initialize an expected CLI failure payload. @param message Human-readable error message. @param code Process exit code bound to the failure category.

### fn `def log(msg: str) -> None` (L46-51)
L47-48> ! @brief Prints an informational message.

### fn `def dlog(msg: str) -> None` (L52-58)
L53-54> ! @brief Prints a debug message if debugging is active.

### fn `def vlog(msg: str) -> None` (L59-65)
L60-61> ! @brief Prints a verbose message if verbose mode is active.

### fn `def build_parser() -> argparse.ArgumentParser` (L66-235)
L67-68> ! @brief Builds the CLI argument parser.
L233> `return parser`

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L236-241)
L237-238> ! @brief Parses command-line arguments into a namespace.
L239> `return build_parser().parse_args(argv)`

### fn `def load_package_version() -> str` (L242-252)
L243-244> ! @brief Reads the package version from __init__.py.
L249> `raise ReqError("Error: unable to determine package version", 6)`
L250> `return match.group(1)`

### fn `def maybe_print_version(argv: list[str]) -> bool` (L253-261)
L254-255> ! @brief Handles --ver/--version by printing the version.
L258> `return True`
L259> `return False`

### fn `def run_upgrade() -> None` (L262-284)
L263-264> ! @brief Executes the upgrade using uv.
L277> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L279> `raise ReqError(`

### fn `def run_uninstall() -> None` (L285-304)
L286-287> ! @brief Executes the uninstallation using uv.
L297> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L299> `raise ReqError(`

### fn `def normalize_release_tag(tag: str) -> str` (L305-313)
L306-307> ! @brief Normalizes the release tag by removing a 'v' prefix if present.
L311> `return value.strip()`

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L314-336)
L315-317> ! @brief Converts a version into a numeric tuple for comparison. @details Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
L321> `return None`
L332> `return None`
L334> `return tuple(numbers) if numbers else None`

### fn `def is_newer_version(current: str, latest: str) -> bool` (L337-350)
L338-339> ! @brief Returns True if latest is greater than current.
L343> `return False`
L348> `return latest_norm > current_norm`

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L351-391)
L352-354> ! @brief Checks online for a new version and prints a warning. @details If the call fails or the response is invalid, it prints nothing and proceeds.
L373> `return`
L389> `return`

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L392-408)
L393-394> ! @brief Ensures the documentation directory exists under the project base.
L399> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L401> `raise ReqError(`
L406> `raise ReqError("Error: --docs-dir must specify a directory, not a file", 5)`

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L409-425)
L410-411> ! @brief Ensures the test directory exists under the project base.
L416> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L418> `raise ReqError(`
L423> `raise ReqError("Error: --tests-dir must specify a directory, not a file", 5)`

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L426-442)
L427-428> ! @brief Ensures the source directory exists under the project base.
L433> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L435> `raise ReqError(`
L440> `raise ReqError("Error: --src-dir must specify a directory, not a file", 5)`

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L443-478)
L444-445> ! @brief Normalizes the path relative to the project root when possible.
L447> `return ""`
L464> `return str(candidate.relative_to(project_base))`
L466> `return str(candidate)`
L469> `return str(resolved.relative_to(project_base))`
L475> `return trimmed`
L476> `return path_value`

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L479-489)
L480-481> ! @brief Resolves the absolute path starting from a normalized value.
L483> `return None`
L486> `return candidate`
L487> `return (project_base / candidate).resolve(strict=False)`

### fn `def format_substituted_path(value: str) -> str` (L490-497)
L491-492> ! @brief Uniforms path separators for substitutions.
L494> `return ""`
L495> `return value.replace(os.sep, "/")`

### fn `def compute_sub_path(` (L498-499)

### fn `def save_config(` (L514-519)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L536-573)
L537-538> ! @brief Loads parameters saved in .req/config.json.
L541> `raise ReqError(`
L548> `raise ReqError("Error: .req/config.json is not valid", 11) from exc`
L550> Fallback to legacy key names from pre-v0.59 config files.
L555> `raise ReqError("Error: missing or invalid 'guidelines-dir' field in .req/config.json", 11)`
L557> `raise ReqError("Error: missing or invalid 'docs-dir' field in .req/config.json", 11)`
L559> `raise ReqError("Error: missing or invalid 'tests-dir' field in .req/config.json", 11)`
L565> `raise ReqError("Error: missing or invalid 'src-dir' field in .req/config.json", 11)`
L566> `return {`

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L574-601)
L575-576> ! @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
L578> `return ""`
L590> If there are no files, use the directory itself.
L595> `return f"`{rel_str}`"`
L597> `return ""`
L599> `return ", ".join(files)`

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L602-630)
L603-605> ! @brief Generates a list of relative file paths (no formatting) for printing. @details Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
L607> `return []`
L619> If there are no files, use the directory itself.
L624> `return [rel_str]`
L626> `return []`
L628> `return items`

### fn `def copy_guidelines_templates(` (L631-632)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L664-675)
L665-666> ! @brief Normalizes the path token optionally preserving the trailing slash.
L668> `return ""`
L671> `return ""`
L673> `return f"{normalized}{suffix}"`

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L676-685)
L677-678> ! @brief Validates that the path is not absolute and raises an error otherwise.
L680> `raise ReqError(`

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L686-693)
L687-688> ! @brief Returns text with token replacements applied.
L691> `return text`

### fn `def write_text_file(dst: Path, text: str) -> None` (L694-700)
L695-696> ! @brief Writes text to disk, ensuring the destination folder exists.

### fn `def copy_with_replacements(` (L701-702)

### fn `def normalize_description(value: str) -> str` (L711-721)
L712-713> ! @brief Normalizes a description by removing superfluous quotes and escapes.
L719> `return trimmed.replace('\\"', '"')`

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L722-750)
L723-724> ! @brief Converts a Markdown prompt to TOML for Gemini.
L726> `raise ReqError(`
L733> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L751-760)
L752-753> ! @brief Extracts front matter and body from Markdown.
L756> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`
L757> Explicitly return two strings to satisfy type annotation.
L758> `return match.group(1), match.group(2)`

### fn `def extract_description(frontmatter: str) -> str` (L761-769)
L762-763> ! @brief Extracts the description from front matter.
L766> `raise ReqError("No 'description:' field found inside the leading block.", 5)`
L767> `return normalize_description(desc_match.group(1).strip())`

### fn `def extract_argument_hint(frontmatter: str) -> str` (L770-778)
L771-772> ! @brief Extracts the argument-hint from front matter, if present.
L775> `return ""`
L776> `return normalize_description(match.group(1).strip())`

### fn `def extract_purpose_first_bullet(body: str) -> str` (L779-799)
L780-781> ! @brief Returns the first bullet of the Purpose section.
L789> `raise ReqError("Error: missing '## Purpose' section in prompt.", 7)`
L796> `return match.group(1).strip()`
L797> `raise ReqError("Error: no bullet found under the '## Purpose' section.", 7)`

### fn `def json_escape(value: str) -> str` (L800-805)
L801-802> ! @brief Escapes a string for JSON without external delimiters.
L803> `return json.dumps(value)[1:-1]`

### fn `def generate_kiro_resources(` (L806-809)

### fn `def render_kiro_agent(` (L829-838)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L872-880)
L873-874> ! @brief Replaces tokens in the specified file.

### fn `def yaml_double_quote_escape(value: str) -> str` (L881-886)
L882-883> ! @brief Minimal escape for a double-quoted string in YAML.
L884> `return value.replace("\\", "\\\\").replace('"', '\\"')`

### fn `def find_template_source() -> Path` (L887-898)
L888-889> ! @brief Returns the template source or raises an error.
L892> `return candidate`
L893> `raise ReqError(`

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L899-933)
L900-901> ! @brief Loads the Kiro template from centralized models configuration.
L904> Try models.json first (this function is called during generation, not with legacy flag check)
L915> `return agent_template, kiro_cfg`
L918> `return (`
L928> `raise ReqError(`

### fn `def strip_json_comments(text: str) -> str` (L934-954)
L935-936> ! @brief Removes // and /* */ comments to allow JSONC parsing.
L952> `return "\n".join(cleaned)`

### fn `def load_settings(path: Path) -> dict[str, Any]` (L955-966)
L956-957> ! @brief Loads JSON/JSONC settings, removing comments when necessary.
L960> `return json.loads(raw)`
L964> `return json.loads(cleaned)`

### fn `def load_centralized_models(` (L967-970)

### fn `def get_model_tools_for_prompt(` (L1014-1015)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1050-1067)
L1051-1053> ! @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt. @details Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
L1055> `return None`
L1064> `return mode_entry.get("tools")`
L1065> `return None`

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1068-1075)
L1069-1070> ! @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
L1073> `return f"[{quoted}]"`

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1076-1086)
L1077-1078> ! @brief Recursively merges dictionaries, prioritizing incoming values.
L1084> `return base`

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1087-1095)
L1088-1089> ! @brief Finds the VS Code settings template if available.
L1092> `return candidate`
L1093> `return None`

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1096-1106)
L1097-1098> ! @brief Generates chat.promptFilesRecommendations from available prompts.
L1101> `return recommendations`
L1104> `return recommendations`

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1107-1116)
L1108-1109> ! @brief Verifies that the path is under the project root.
L1111> `raise ReqError(`

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1117-1126)
L1118-1119> ! @brief Saves a backup of VS Code settings if the file exists.
L1121> Never create an absence marker. Backup only if the file exists.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1127-1138)
L1128-1129> ! @brief Restores VS Code settings from backup, if present.
L1136> Do not remove the target file if no backup exists: restore behavior disabled otherwise.

### fn `def prune_empty_dirs(root: Path) -> None` (L1139-1152)
L1136> Do not remove the target file if no backup exists: restore behavior disabled otherwise.
L1140-1141> ! @brief Removes empty directories under the specified root.
L1143> `return`

### fn `def remove_generated_resources(project_base: Path) -> None` (L1153-1193)
L1154-1155> ! @brief Removes resources generated by the tool in the project root.

### fn `def run_remove(args: Namespace) -> None` (L1194-1235)
L1195-1196> ! @brief Handles the removal of generated resources.
L1202> `raise ReqError(`
L1211> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1214> `raise ReqError(`
L1219> After validation and before any removal, check for a new version.
L1222> Do not perform any restore or removal of .vscode/settings.json during removal.

### fn `def run(args: Namespace) -> None` (L1236-1435)
L1237-1238> ! @brief Handles the main initialization flow.
L1243> Main flow: validates input, calculates paths, generates resources.
L1246> `return`
L1253> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1261> `raise ReqError(`
L1266> `raise ReqError(`
L1284> `raise ReqError("Error: invalid docs configuration values", 11)`
L1286> `raise ReqError("Error: invalid tests configuration value", 11)`
L1292> `raise ReqError("Error: invalid src configuration values", 11)`
L1332> `raise ReqError("Error: --guidelines-dir must be under the project base", 8)`
L1334> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L1336> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L1339> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L1364> `raise ReqError(`
L1371> Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
L1400> `raise ReqError(`
L1405> After validation and before any operation that modifies the filesystem, check for a new version.
L1435> Copy models configuration to .req/models.json based on legacy mode (REQ-084)

- var `VERBOSE = args.verbose` (L1240) — ! @brief Handles the main initialization flow.
- var `DEBUG = args.debug` (L1241)
- var `PROMPT = prompt_path.stem` (L1574)
### fn `def _format_install_table(` `priv` (L2002-2004)
L1999> Build and print a simple installation report table describing which

### fn `def fmt(row: tuple[str, ...]) -> str` (L2025-2027)
L2026> `return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row))`

- var `EXCLUDED_DIRS = frozenset({` (L2045) — ── Excluded directories for --references and --compress ──────────────────
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2054) — ── Supported source file extensions ──────────────────────────────────────
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2062-2082)
L2059> File extensions considered during source directory scanning.
L2063-2065> ! @brief Recursively collect source files from the given directories. @details Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
L2072> Filter out excluded directories (modifies dirnames in-place)
L2080> `return collected`

### fn `def _build_ascii_tree(paths: list[str]) -> str` `priv` (L2083-2120)
L2084-2087> ! @brief Build a deterministic tree string from project-relative paths. @param paths Project-relative file paths. @return Rendered tree rooted at '.'.
L2118> `return "\n".join(lines)`

### fn `def _emit(` `priv` (L2105-2107)

### fn `def _format_files_structure_markdown(files: list[str], project_base: Path) -> str` `priv` (L2121-2131)
L2122-2126> ! @brief Format markdown section containing the scanned files tree. @param files Absolute file paths selected for --references processing. @param project_base Project root used to normalize relative paths. @return Markdown section with heading and fenced tree.
L2129> `return f"# Files Structure\n```\n{tree}\n```"`

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2132-2141)
L2133-2134> ! @brief Check if the parsed args contain a standalone file command.
L2135> `return bool(`

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2142-2151)
L2143-2144> ! @brief Check if the parsed args contain a project scan command.
L2145> `return bool(`

### fn `def run_files_tokens(files: list[str]) -> None` (L2152-2170)
L2153-2154> ! @brief Execute --files-tokens: count tokens for arbitrary files.
L2165> `raise ReqError("Error: no valid files provided.", 1)`

### fn `def run_files_references(files: list[str]) -> None` (L2171-2179)
L2172-2173> ! @brief Execute --files-references: generate markdown for arbitrary files.

### fn `def run_files_compress(files: list[str], disable_line_numbers: bool = False) -> None` (L2180-2190)
L2181-2184> ! @brief Execute --files-compress: compress arbitrary files. @param files List of source file paths to compress. @param disable_line_numbers If True, suppresses Lnn> prefixes in compressed entries.

### fn `def run_references(args: Namespace) -> None` (L2191-2204)
L2192-2193> ! @brief Execute --references: generate markdown for project source files.
L2199> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_compress_cmd(args: Namespace) -> None` (L2205-2221)
L2206-2208> ! @brief Execute --compress: compress project source files. @param args Parsed CLI arguments namespace.
L2214> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_tokens(args: Namespace) -> None` (L2222-2239)
L2223-2226> ! @brief Execute --tokens: count tokens for files directly in --docs-dir. @param args Parsed CLI arguments namespace. @details Requires --base/--here and --docs-dir, then delegates reporting to run_files_tokens.
L2230> `raise ReqError("Error: --tokens requires --docs-dir.", 1)`
L2236> `raise ReqError("Error: no files found in --docs-dir.", 1)`

### fn `def _resolve_project_base(args: Namespace) -> Path` `priv` (L2240-2260)
L2241-2245> ! @brief Resolve project base path for project-level commands. @param args Parsed CLI arguments namespace. @return Absolute path of project base. @throws ReqError If --base/--here is missing or the resolved path does not exist.
L2247> `raise ReqError(`
L2257> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L2258> `return project_base`

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L2261-2284)
L2262-2263> ! @brief Resolve project base and src-dirs for --references/--compress.
L2266> Source dirs can come from args or from config
L2269> Try to load from config
L2275> `raise ReqError(`
L2280> `raise ReqError("Error: no source directories configured.", 1)`
L2282> `return project_base, src_dirs`

### fn `def main(argv: Optional[list[str]] = None) -> int` (L2285-2340)
L2286-2288> ! @brief CLI entry point for console_scripts and `-m` execution. @details Returns an exit code (0 success, non-zero on error).
L2293> `return 0`
L2296> `return 0`
L2299> `return 0`
L2301> `return 0`
L2303> Standalone file commands (no --base/--here required)
L2314> `return 0`
L2315> Project scan commands (require --base/--here)
L2323> `return 0`
L2324> Standard init flow requires --base or --here
L2326> `raise ReqError(`
L2332> `return e.code`
L2333> Unexpected error
L2339> `return 1`
L2340> `return 0`

## Comments
- L37: ! @brief Initialize an expected CLI failure payload. @param message Human-readable error message. @param code Process exit code bound to the failur...
- L47: ! @brief Prints an informational message.
- L53: ! @brief Prints a debug message if debugging is active.
- L60: ! @brief Prints a verbose message if verbose mode is active.
- L67: ! @brief Builds the CLI argument parser.
- L237: ! @brief Parses command-line arguments into a namespace.
- L243: ! @brief Reads the package version from __init__.py.
- L254: ! @brief Handles --ver/--version by printing the version.
- L263: ! @brief Executes the upgrade using uv.
- L286: ! @brief Executes the uninstallation using uv.
- L306: ! @brief Normalizes the release tag by removing a 'v' prefix if present.
- L315: ! @brief Converts a version into a numeric tuple for comparison. @details Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
- L338: ! @brief Returns True if latest is greater than current.
- L352: ! @brief Checks online for a new version and prints a warning. @details If the call fails or the response is invalid, it prints nothing and proceeds.
- L393: ! @brief Ensures the documentation directory exists under the project base.
- L410: ! @brief Ensures the test directory exists under the project base.
- L427: ! @brief Ensures the source directory exists under the project base.
- L444: ! @brief Normalizes the path relative to the project root when possible.
- L480: ! @brief Resolves the absolute path starting from a normalized value.
- L491: ! @brief Uniforms path separators for substitutions.
- L501: ! @brief Calculates the relative path to use in tokens.
- L521: ! @brief Saves normalized parameters to .req/config.json.
- L537: ! @brief Loads parameters saved in .req/config.json.
- L550: Fallback to legacy key names from pre-v0.59 config files.
- L575: ! @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
- L590: If there are no files, use the directory itself.
- L603: ! @brief Generates a list of relative file paths (no formatting) for printing. @details Each entry is formatted as `guidelines/file.md` (forward sl...
- L619: If there are no files, use the directory itself.
- L634: ! @brief Copies guidelines templates from resources/guidelines/ to the target directory. @details Args: guidelines_dest: Target directory where tem...
- L665: ! @brief Normalizes the path token optionally preserving the trailing slash.
- L677: ! @brief Validates that the path is not absolute and raises an error otherwise.
- L687: ! @brief Returns text with token replacements applied.
- L695: ! @brief Writes text to disk, ensuring the destination folder exists.
- L704: ! @brief Copies a file substituting the indicated tokens with their values.
- L712: ! @brief Normalizes a description by removing superfluous quotes and escapes.
- L723: ! @brief Converts a Markdown prompt to TOML for Gemini.
- L752: ! @brief Extracts front matter and body from Markdown.
- L757: Explicitly return two strings to satisfy type annotation.
- L762: ! @brief Extracts the description from front matter.
- L771: ! @brief Extracts the argument-hint from front matter, if present.
- L780: ! @brief Returns the first bullet of the Purpose section.
- L801: ! @brief Escapes a string for JSON without external delimiters.
- L811: ! @brief Generates the resource list for the Kiro agent.
- L840: ! @brief Renders the Kiro agent JSON and populates main fields.
- L868: If parsing fails, return raw template to preserve previous behavior
- L873: ! @brief Replaces tokens in the specified file.
- L882: ! @brief Minimal escape for a double-quoted string in YAML.
- L888: ! @brief Returns the template source or raises an error.
- L900: ! @brief Loads the Kiro template from centralized models configuration.
- L904: Try models.json first (this function is called during generation, not with legacy flag check)
- L935: ! @brief Removes // and /* */ comments to allow JSONC parsing.
- L956: ! @brief Loads JSON/JSONC settings, removing comments when necessary.
- L972: ! @brief Loads centralized models configuration from common/models.json. @details Returns a map cli_name -> parsed_json or None if not present. Whe...
- L978: Priority 1: preserve_models_path if provided and exists
- L982: Priority 2: legacy mode
- L989: Fallback: standard models.json
- L996: Load the centralized configuration
- L1004: Extract individual CLI configs
- L1017: ! @brief Extracts model and tools for the prompt from the CLI config. @details Returns (model, tools) where each value can be None if not available.
- L1033-1034: Use the unified key name 'tools' across all CLI configs. | Accept either a list of strings or a CSV string in the config.json.
- L1042: Parse comma-separated string into list
- L1051: ! @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt. @details Can return a list of strings, a string, or None depending o...
- L1069: ! @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
- L1077: ! @brief Recursively merges dictionaries, prioritizing incoming values.
- L1088: ! @brief Finds the VS Code settings template if available.
- L1097: ! @brief Generates chat.promptFilesRecommendations from available prompts.
- L1108: ! @brief Verifies that the path is under the project root.
- L1118-1121: ! @brief Saves a backup of VS Code settings if the file exists. | Never create an absence marker. Backup only if the file exists.
- L1128: ! @brief Restores VS Code settings from backup, if present.
- L1140: ! @brief Removes empty directories under the specified root.
- L1154: ! @brief Removes resources generated by the tool in the project root.
- L1195: ! @brief Handles the removal of generated resources.
- L1219: After validation and before any removal, check for a new version.
- L1222: Do not perform any restore or removal of .vscode/settings.json during removal.
- L1243: Main flow: validates input, calculates paths, generates resources.
- L1371: Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
- L1405: After validation and before any operation that modifies the filesystem, check for a new version.
- L1435-1436: Copy models configuration to .req/models.json based on legacy mode (REQ-084) | Skip if --preserve-models is active
- L1460: Create requirements.md only if the --docs-dir folder is empty.
- L1470: Generate the file list for the %%GUIDELINES_FILES%% token.
- L1539: Load CLI configs only if requested to include model/tools
- L1550: Determine preserve_models_path (REQ-082)
- L1581: (Removed: bootstrap file inlining and YOLO stop/approval substitution)
- L1597: Precompute description and Claude metadata so provider blocks can reuse them safely.
- L1607: .codex/prompts
- L1616: .codex/skills/req/<prompt>/SKILL.md
- L1646: Gemini TOML
- L1684: .kiro/prompts
- L1694: .claude/agents
- L1720: .github/agents
- L1748: .github/prompts
- L1780: .kiro/agents
- L1810: .opencode/agent
- L1841: .opencode/command
- L1886: .claude/commands/req
- L1944: Load existing settings (if present) and those from the template.
- L1950: If checking/loading fails, consider it empty
- L1955: Merge without modifying original until sure.
- L1965: If final result is identical to existing, do not rewrite nor backup.
- L1970: If changes are expected, create backup only if file exists.
- L1973: Write final settings.
- L1981-1982: Final success notification: printed only when the command completed all | intended filesystem modifications without raising an exception.
- L1989-1990: Print the discovered directories used for token substitutions | as required by REQ-078: one item per line prefixed with '- '.
- L2006: ! @brief Format the installation summary table aligning header, prompts, and rows.
- L2050: Directories excluded from source scanning in --references and --compress.
- L2063: ! @brief Recursively collect source files from the given directories. @details Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
- L2072: Filter out excluded directories (modifies dirnames in-place)
- L2084: ! @brief Build a deterministic tree string from project-relative paths. @param paths Project-relative file paths. @return Rendered tree rooted at '.'.
- L2122: ! @brief Format markdown section containing the scanned files tree. @param files Absolute file paths selected for --references processing. @param p...
- L2133: ! @brief Check if the parsed args contain a standalone file command.
- L2143: ! @brief Check if the parsed args contain a project scan command.
- L2153: ! @brief Execute --files-tokens: count tokens for arbitrary files.
- L2172: ! @brief Execute --files-references: generate markdown for arbitrary files.
- L2181: ! @brief Execute --files-compress: compress arbitrary files. @param files List of source file paths to compress. @param disable_line_numbers If Tru...
- L2192: ! @brief Execute --references: generate markdown for project source files.
- L2206: ! @brief Execute --compress: compress project source files. @param args Parsed CLI arguments namespace.
- L2223: ! @brief Execute --tokens: count tokens for files directly in --docs-dir. @param args Parsed CLI arguments namespace. @details Requires --base/--he...
- L2241: ! @brief Resolve project base path for project-level commands. @param args Parsed CLI arguments namespace. @return Absolute path of project base. @...
- L2262: ! @brief Resolve project base and src-dirs for --references/--compress.
- L2266: Source dirs can come from args or from config
- L2269: Try to load from config
- L2286: ! @brief CLI entry point for console_scripts and `-m` execution. @details Returns an exit code (0 success, non-zero on error).
- L2303: Standalone file commands (no --base/--here required)
- L2315: Project scan commands (require --base/--here)
- L2324: Standard init flow requires --base or --here

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|19||
|`RESOURCE_ROOT`|var|pub|22||
|`VERBOSE`|var|pub|25||
|`DEBUG`|var|pub|28||
|`ReqError`|class|pub|32-45|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|36-45|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|46-51|def log(msg: str) -> None|
|`dlog`|fn|pub|52-58|def dlog(msg: str) -> None|
|`vlog`|fn|pub|59-65|def vlog(msg: str) -> None|
|`build_parser`|fn|pub|66-235|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|236-241|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|242-252|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|253-261|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|262-284|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|285-304|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|305-313|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|314-336|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|337-350|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|351-391|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|392-408|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|409-425|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|426-442|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|443-478|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|479-489|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|490-497|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|498-499|def compute_sub_path(|
|`save_config`|fn|pub|514-519|def save_config(|
|`load_config`|fn|pub|536-573|def load_config(project_base: Path) -> dict[str, str | li...|
|`generate_guidelines_file_list`|fn|pub|574-601|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|602-630|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`copy_guidelines_templates`|fn|pub|631-632|def copy_guidelines_templates(|
|`make_relative_token`|fn|pub|664-675|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|676-685|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|686-693|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|694-700|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|701-702|def copy_with_replacements(|
|`normalize_description`|fn|pub|711-721|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|722-750|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|751-760|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|761-769|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|770-778|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|779-799|def extract_purpose_first_bullet(body: str) -> str|
|`json_escape`|fn|pub|800-805|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|806-809|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|829-838|def render_kiro_agent(|
|`replace_tokens`|fn|pub|872-880|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|881-886|def yaml_double_quote_escape(value: str) -> str|
|`find_template_source`|fn|pub|887-898|def find_template_source() -> Path|
|`load_kiro_template`|fn|pub|899-933|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|934-954|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|955-966|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|967-970|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|1014-1015|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1050-1067|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1068-1075|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1076-1086|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1087-1095|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1096-1106|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1107-1116|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1117-1126|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1127-1138|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1139-1152|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1153-1193|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1194-1235|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1236-1435|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1240||
|`DEBUG`|var|pub|1241||
|`PROMPT`|var|pub|1574||
|`_format_install_table`|fn|priv|2002-2004|def _format_install_table(|
|`fmt`|fn|pub|2025-2027|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|2045||
|`SUPPORTED_EXTENSIONS`|var|pub|2054||
|`_collect_source_files`|fn|priv|2062-2082|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_build_ascii_tree`|fn|priv|2083-2120|def _build_ascii_tree(paths: list[str]) -> str|
|`_emit`|fn|priv|2105-2107|def _emit(|
|`_format_files_structure_markdown`|fn|priv|2121-2131|def _format_files_structure_markdown(files: list[str], pr...|
|`_is_standalone_command`|fn|priv|2132-2141|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2142-2151|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2152-2170|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2171-2179|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2180-2190|def run_files_compress(files: list[str], disable_line_num...|
|`run_references`|fn|pub|2191-2204|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2205-2221|def run_compress_cmd(args: Namespace) -> None|
|`run_tokens`|fn|pub|2222-2239|def run_tokens(args: Namespace) -> None|
|`_resolve_project_base`|fn|priv|2240-2260|def _resolve_project_base(args: Namespace) -> Path|
|`_resolve_project_src_dirs`|fn|priv|2261-2284|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|2285-2340|def main(argv: Optional[list[str]] = None) -> int|


---

# compress.py | Python | 354L | 11 symbols | 5 imports | 41 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress.py`
> ! @brief compress.py - Source code compressor for LLM context optimization. @details Parses a source file and removes all comments (inline, single-line, multi-line), blank lines, trailing whitespac...

## Imports
```
import os
import re
import sys
from .source_analyzer import build_language_specs
import argparse
```

## Definitions

- var `EXT_LANG_MAP = {` (L13) — Extension-to-language map (mirrors generate_markdown.py)
- var `INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}` (L25) — ! @brief Extension-to-language normalization map for compression input.
### fn `def _get_specs()` `priv` (L32-41)
L29> ! @brief Cached language specification dictionary initialized lazily.
L33-35> ! @brief Return cached language specifications, initializing once. @return Dictionary mapping normalized language keys to language specs.
L39> `return _specs_cache`

### fn `def detect_language(filepath: str) -> str | None` (L42-50)
L43-46> ! @brief Detect language key from file extension. @param filepath Source file path. @return Normalized language key, or None when extension is unsupported.
L48> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L51-87)
L52-53> ! @brief Check if position `pos` in `line` is inside a string literal.
L60> Check for escaped delimiter (single-char only)
L62> Count consecutive backslashes
L85> `return in_string is not None`

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L88-126)
L90-91> ! @brief Remove trailing single-line comment from a code line.
L93> `return line`
L116> `return line[:i]`
L124> `return line`

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L127-136)
L128-129> ! @brief Check if a line is a standalone Python docstring (triple-quote only).
L133> `return True`
L134> `return False`

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L137-145)
L139-140> ! @brief Format compressed entries, optionally prefixing original line numbers.
L142> `return '\n'.join(text for _, text in entries)`
L143> `return '\n'.join(f"L{lineno}> {text}" for lineno, text in entries)`

### fn `def compress_source(source: str, language: str,` (L146-308)
L148-150> ! @brief Compress source code by removing comments, blank lines, and extra whitespace. @details Preserves indentation for indent-significant languages (Python, Haskell, Elixir). Args: source: The source code string. language: Language identifier (e.g. "python", "javascript"). include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Compressed source code string.
L154> `raise ValueError(f"Unsupported language: {language}")`
L159> list of (original_line_number, text)
L166> Python: also handle ''' as multi-comment
L175> --- Handle multi-line comment continuation ---
L178> End of multi-line comment found
L182> Process remainder as a new line
L189-215> --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docstring: if python_docstring_delim in line: end_pos = line.index(python_docstring_delim) + 3 remainder = line[end_pos:] in_python_docstring = False python_docstring_delim = None if remainder.strip(): lines[i] = remainder continue i += 1 continue stripped = line.strip() Skip empty lines if not stripped: i += 1 continue --- Detect multi-line comment start --- if mc_start: For Python, triple-quotes can be strings or docstrings. We only strip standalone docstrings (line starts with triple-quote after optional whitespace). if is_python: for q in ('"""', "'''"):
L217> Single-line docstring: """...
L219> Check it's not a variable assignment like x = """...
L223> Standalone docstring or assigned — skip if standalone
L227> If code before and not assignment, keep line
L229> Multi-line docstring start
L240> Non-Python: check for multi-line comment start
L243> Check if inside a string
L246> Check for same-line close
L250> Single-line block comment: remove it
L257> Re-process this reconstructed line
L261> Multi-line comment starts here
L270> --- Full-line single-line comment ---
L272> Special: keep shebangs
L278> --- Remove inline comment ---
L282> --- Clean whitespace ---
L284> Keep leading whitespace, strip trailing
L290> Collapse internal multiple spaces (but not in strings)
L298> Remove trailing whitespace
L306> `return _format_result(result, include_line_numbers)`

### fn `def compress_file(filepath: str, language: str | None = None,` (L309-326)
L311-313> ! @brief Compress a source file by removing comments and extra whitespace. @details Args: filepath: Path to the source file. language: Optional language override. Auto-detected if None. include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Compressed source code string.
L317> `raise ValueError(`
L324> `return compress_source(source, language, include_line_numbers)`

### fn `def main()` (L327-352)
L328> ! @brief Execute the standalone compression CLI.
L342> `sys.exit(1)`
L350> `sys.exit(1)`

## Comments
- L2: ! @brief compress.py - Source code compressor for LLM context optimization. @details Parses a source file and removes all comments (inline, single-...
- L26: ! @brief Languages requiring indentation-preserving compression behavior.
- L33: ! @brief Return cached language specifications, initializing once. @return Dictionary mapping normalized language keys to language specs.
- L43: ! @brief Detect language key from file extension. @param filepath Source file path. @return Normalized language key, or None when extension is unsu...
- L52: ! @brief Check if position `pos` in `line` is inside a string literal.
- L60-62: Check for escaped delimiter (single-char only) | Count consecutive backslashes
- L90: ! @brief Remove trailing single-line comment from a code line.
- L128: ! @brief Check if a line is a standalone Python docstring (triple-quote only).
- L139: ! @brief Format compressed entries, optionally prefixing original line numbers.
- L148: ! @brief Compress source code by removing comments, blank lines, and extra whitespace. @details Preserves indentation for indent-significant langua...
- L166: Python: also handle ''' as multi-comment
- L175: --- Handle multi-line comment continuation ---
- L178: End of multi-line comment found
- L182: Process remainder as a new line
- L189-219: --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docs... | Single-line docstring: """... | Check it's not a variable assignment like x = """...
- L223: Standalone docstring or assigned — skip if standalone
- L227-229: If code before and not assignment, keep line | Multi-line docstring start
- L240: Non-Python: check for multi-line comment start
- L243: Check if inside a string
- L246: Check for same-line close
- L250: Single-line block comment: remove it
- L257: Re-process this reconstructed line
- L261: Multi-line comment starts here
- L270-272: --- Full-line single-line comment --- | Special: keep shebangs
- L278: --- Remove inline comment ---
- L282-284: --- Clean whitespace --- | Keep leading whitespace, strip trailing
- L290: Collapse internal multiple spaces (but not in strings)
- L298: Remove trailing whitespace
- L311: ! @brief Compress a source file by removing comments and extra whitespace. @details Args: filepath: Path to the source file. language: Optional lan...
- L328: ! @brief Execute the standalone compression CLI.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|13||
|`INDENT_SIGNIFICANT`|var|pub|25||
|`_get_specs`|fn|priv|32-41|def _get_specs()|
|`detect_language`|fn|pub|42-50|def detect_language(filepath: str) -> str | None|
|`_is_in_string`|fn|priv|51-87|def _is_in_string(line: str, pos: int, string_delimiters:...|
|`_remove_inline_comment`|fn|priv|88-126|def _remove_inline_comment(line: str, single_comment: str,|
|`_is_python_docstring_line`|fn|priv|127-136|def _is_python_docstring_line(line: str) -> bool|
|`_format_result`|fn|priv|137-145|def _format_result(entries: list[tuple[int, str]],|
|`compress_source`|fn|pub|146-308|def compress_source(source: str, language: str,|
|`compress_file`|fn|pub|309-326|def compress_file(filepath: str, language: str | None = N...|
|`main`|fn|pub|327-352|def main()|


---

# compress_files.py | Python | 70L | 2 symbols | 4 imports | 4 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress_files.py`
> ! @brief compress_files.py - Compress and concatenate multiple source files. @details Uses the compress module to strip comments and whitespace from each input file, then concatenates results with ...

## Imports
```
import os
import sys
from .compress import compress_file, detect_language
import argparse
```

## Definitions

### fn `def compress_files(filepaths: list[str],` (L12-49)
L14-16> ! @brief Compress multiple source files and concatenate with identifying headers. @details Each file is compressed and prefixed with a header line: @@@ <path> | <lang> Files are separated by a blank line. Args: filepaths: List of source file paths. include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Concatenated compressed output string. Raises: ValueError: If no files could be processed.
L42> `raise ValueError("No valid source files processed")`
L47> `return "\n\n".join(parts)`

### fn `def main()` (L50-68)
L51> ! @brief Execute the multi-file compression CLI command.
L66> `sys.exit(1)`

## Comments
- L2: ! @brief compress_files.py - Compress and concatenate multiple source files. @details Uses the compress module to strip comments and whitespace fro...
- L14: ! @brief Compress multiple source files and concatenate with identifying headers. @details Each file is compressed and prefixed with a header line:...
- L51: ! @brief Execute the multi-file compression CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`compress_files`|fn|pub|12-49|def compress_files(filepaths: list[str],|
|`main`|fn|pub|50-68|def main()|


---

# generate_markdown.py | Python | 110L | 4 symbols | 3 imports | 7 comments
> Path: `/home/ogekuri/useReq/src/usereq/generate_markdown.py`
> ! @brief generate_markdown.py - Generate concatenated markdown from arbitrary source files. @details Analyzes each input file with source_analyzer and produces a single markdown output concatenatin...

## Imports
```
import os
import sys
from .source_analyzer import SourceAnalyzer, format_markdown
```

## Definitions

- var `EXT_LANG_MAP = {` (L12) — Map file extensions to languages
### fn `def detect_language(filepath: str) -> str | None` (L39-45)
L36> ! @brief Extension-to-language normalization map for markdown generation.
L40-41> ! @brief Detect language from file extension.
L43> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def generate_markdown(filepaths: list[str]) -> str` (L46-93)
L47-49> ! @brief Analyze source files and return concatenated markdown. @details Args: filepaths: List of source file paths to analyze. Returns: Concatenated markdown string with all file analyses. Raises: ValueError: If no valid source files are found.
L86> `raise ValueError("No valid source files processed")`
L91> `return "\n\n---\n\n".join(md_parts)`

### fn `def main()` (L94-108)
L95> ! @brief Execute the standalone markdown generation CLI command.
L99> `sys.exit(1)`
L106> `sys.exit(1)`

## Comments
- L2: ! @brief generate_markdown.py - Generate concatenated markdown from arbitrary source files. @details Analyzes each input file with source_analyzer ...
- L40: ! @brief Detect language from file extension.
- L47: ! @brief Analyze source files and return concatenated markdown. @details Args: filepaths: List of source file paths to analyze. Returns: Concatenat...
- L95: ! @brief Execute the standalone markdown generation CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|12||
|`detect_language`|fn|pub|39-45|def detect_language(filepath: str) -> str | None|
|`generate_markdown`|fn|pub|46-93|def generate_markdown(filepaths: list[str]) -> str|
|`main`|fn|pub|94-108|def main()|


---

# pdoc_utils.py | Python | 82L | 3 symbols | 6 imports | 5 comments
> Path: `/home/ogekuri/useReq/src/usereq/pdoc_utils.py`
> ! @brief Utilities for generating pdoc documentation.

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

### fn `def _normalize_modules(modules: str | Iterable[str]) -> list[str]` `priv` (L13-20)
L14-15> ! @brief Returns a list of modules from either a string or an iterable.
L17> `return [modules]`
L18> `return list(modules)`

### fn `def _run_pdoc(command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess` `priv` (L21-33)
L22-23> ! @brief Runs pdoc and captures output for error handling.
L24> `return subprocess.run(`

### fn `def generate_pdoc_docs(` (L34-38)

## Comments
- L14: ! @brief Returns a list of modules from either a string or an iterable.
- L22: ! @brief Runs pdoc and captures output for error handling.
- L40: ! @brief Generates or updates pdoc documentation in the target output directory. @details Args: output_dir: Directory where HTML documentation will...
- L73: Fallback for pdoc versions that do not support --all-submodules.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_normalize_modules`|fn|priv|13-20|def _normalize_modules(modules: str | Iterable[str]) -> l...|
|`_run_pdoc`|fn|priv|21-33|def _run_pdoc(command: list[str], *, env: dict[str, str],...|
|`generate_pdoc_docs`|fn|pub|34-38|def generate_pdoc_docs(|


---

# source_analyzer.py | Python | 1985L | 56 symbols | 7 imports | 130 comments
> Path: `/home/ogekuri/useReq/src/usereq/source_analyzer.py`
> ! @brief source_analyzer.py - Multi-language source code analyzer. @details Inspired by tree-sitter, this module analyzes source files across multiple programming languages, extracting: - Definitio...

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

### class `class ElementType(Enum)` : Enum (L15-44)
- var `FUNCTION = auto()` (L18) L16> ! @brief Element types recognized in source code.
- var `METHOD = auto()` (L19)
- var `CLASS = auto()` (L20)
- var `STRUCT = auto()` (L21)
- var `ENUM = auto()` (L22)
- var `TRAIT = auto()` (L23)
- var `INTERFACE = auto()` (L24)
- var `MODULE = auto()` (L25)
- var `IMPL = auto()` (L26)
- var `MACRO = auto()` (L27)
- var `CONSTANT = auto()` (L28)
- var `VARIABLE = auto()` (L29)
- var `TYPE_ALIAS = auto()` (L30)
- var `IMPORT = auto()` (L31)
- var `DECORATOR = auto()` (L32)
- var `COMMENT_SINGLE = auto()` (L33)
- var `COMMENT_MULTI = auto()` (L34)
- var `COMPONENT = auto()` (L35)
- var `PROTOCOL = auto()` (L36)
- var `EXTENSION = auto()` (L37)
- var `UNION = auto()` (L38)
- var `NAMESPACE = auto()` (L39)
- var `PROPERTY = auto()` (L40)
- var `SIGNAL = auto()` (L41)
- var `TYPEDEF = auto()` (L42)

### class `class SourceElement` `@dataclass` (L46-96)
L47-48> ! @brief Element found in source file.
- fn `def type_label(self) -> str` (L63-96)
  L64-66> ! @brief Return the normalized printable label for element_type. @return Stable uppercase label used in markdown rendering output.
  L94> `return labels.get(self.element_type, "UNKNOWN")`

### class `class LanguageSpec` `@dataclass` (L98-108)
L99-100> ! @brief Language recognition pattern specification.

### fn `def build_language_specs() -> dict` (L109-308)
L110-111> ! @brief Build specifications for all supported languages.
L114> ── Python ──────────────────────────────────────────────────────────
L135> ── C ───────────────────────────────────────────────────────────────
L169> ── C++ ─────────────────────────────────────────────────────────────
L199> ── Rust ────────────────────────────────────────────────────────────
L231> ── JavaScript ──────────────────────────────────────────────────────
L259> ── TypeScript ──────────────────────────────────────────────────────
L292> ── Java ────────────────────────────────────────────────────────────

### class `class SourceAnalyzer` (L662-861)
- fn `def __init__(self)` `priv` (L667-670) L663> ! @brief Multi-language source file analyzer. @details Analyzes a source file identifying definit...
  L668> ! @brief Initialize analyzer state with language specifications.
- fn `def get_supported_languages(self) -> list` (L671-681) L668> ! @brief Initialize analyzer state with language specifications.
  L672-673> ! @brief Return list of supported languages (without aliases).
  L680> `return sorted(result)`
- fn `def analyze(self, filepath: str, language: str) -> list` (L682-830)
  L683-684> ! @brief Analyze a source file and return the list of SourceElement found.
  L687> `raise ValueError(`
  L699> Multi-line comment state
  L707> ── Multi-line comment handling ──────────────────────────
  L724> ── Multi-line comment start ────────────────────────────
  L726> Special handling for Python docstrings and =begin/=pod blocks
  L730> Check not inside a string
  L732> Check if multi-line comment closes on same line
  L744> Python: """ ... """ sulla stessa riga
  L761> ── Single-line comment ───────────────────────────────────
  L765> If comment is the entire line (aside from whitespace)
  L776> Inline comment: add both element and comment
  L786> ── Language patterns ─────────────────────────────────────
  L799> Single-line types: don't search for block
  L816> Limit extract to max 5 lines for readability
  L829> `return elements`
- fn `def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool` `priv` (L831-860)
  L832-833> ! @brief Check if position pos is inside a string literal.
  L859> `return in_string`

### fn `def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]` `priv` (L861-895)
L862-863> ! @brief Find position of single-line comment, ignoring strings.
L865> `return None`
L882> `return i`
L894> `return None`

### fn `def _find_block_end(self, lines: list, start_idx: int,` `priv` (L896-969)
L898-900> ! @brief Find the end of a block (function, class, struct, etc.). @details Returns the index (1-based) of the final line of the block. Limits search for performance.
L901> Per Python: basato sull'indentazione
L914> `return end`
L916> Per linguaggi con parentesi graffe
L933> `return end + 1`
L935> If no opening braces found, return just the first line
L937> `return start_idx + 1`
L938> `return end`
L940> Per Ruby/Elixir/Lua: basato su end keyword
L949> `return end + 1`
L951> `return start_idx + 1`
L953> Per Haskell: basato sull'indentazione
L966> `return end`
L968> `return start_idx + 1`

### fn `def enrich(self, elements: list, language: str,` (L972-986)
L970> ── Enrichment methods for LLM-optimized output ───────────────────
L974-976> ! @brief Enrich elements with signatures, hierarchy, visibility, inheritance. @details Call after analyze() to add metadata for LLM-optimized markdown output. Modifies elements in-place and returns them. If filepath is provided, also extracts body comments and exit points.
L985> `return elements`

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L987-1012)
L988-990> ! @brief Extract clean identifiers from name fields. @details Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.
L995> Try to re-extract the name from the element's extract line
L996> using the original pattern (which has group 2 as the identifier)
L1004> Take highest non-None non-empty group
L1005> (group 2+ = identifier, group 1 = full match)

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1013-1028)
L1014-1015> ! @brief Extract clean signatures from element extracts.

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1029-1062)
L1030-1032> ! @brief Detect parent-child relationships between elements. @details Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1063-1075)
L1064-1065> ! @brief Extract visibility/access modifiers from elements.

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1076-1121)
L1078-1079> ! @brief Parse visibility modifier from a signature line.
L1082> `return "priv"`
L1084> `return "priv"`
L1085> `return "pub"`
L1088> `return "pub"`
L1090> `return "priv"`
L1092> `return "prot"`
L1094> `return "int"`
L1095> `return None`
L1098> `return "pub"`
L1099> `return "priv"`
L1102> `return "pub"`
L1103> `return "priv"`
L1106> `return "priv"`
L1108> `return "fpriv"`
L1110> `return "pub"`
L1111> `return None`
L1114> `return "pub"`
L1116> `return "priv"`
L1118> `return "prot"`
L1119> `return None`
L1120> `return None`

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1122-1133)
L1123-1124> ! @brief Extract inheritance/implementation info from class-like elements.

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1134-1163)
L1136-1137> ! @brief Parse inheritance info from a class/struct declaration line.
L1140> `return m.group(1).strip() if m else None`
L1149> `return ", ".join(parts) if parts else None`
L1153> `return m.group(1).strip() if m else None`
L1158> `return m.group(1).strip() if m else None`
L1161> `return m.group(1) if m else None`
L1162> `return None`

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1171-1294)
L1173-1175> ! @brief Extract comments and exit points from within function/class bodies. @details Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.
L1178> `return`
L1184> `return`
L1186> Only process definitions that span multiple lines
L1204> Scan the body (lines after the definition line)
L1205> 1-based, skip def line itself
L1219> Multi-line comment tracking within body
L1234> Check for multi-line comment start
L1239> Single-line multi-comment
L1263> Single-line comment (full line)
L1273> Standalone comment line in body
L1279> Inline comment after code
L1284> Exit points

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1296-1307)
L1297-1298> ! @brief Strip comment markers from a single line of comment text.
L1305> `return s`

### fn `def format_output(elements: list, filepath: str, language: str,` (L1308-1428)
L1310-1311> ! @brief Format structured analysis output.
L1321> ── Definitions section ────────────────────────────────────────────
L1345> Prefix with line number
L1355> ── Comments section ───────────────────────────────────────────────
L1388> ── Complete structured listing ────────────────────────────────────
L1395> Sort by start line
L1413> Show first line of extract
L1426> `return "\n".join(output_lines)`

### fn `def _md_loc(elem) -> str` `priv` (L1429-1436)
L1430-1431> ! @brief Format element location compactly for markdown.
L1433> `return f"L{elem.line_start}"`
L1434> `return f"L{elem.line_start}-{elem.line_end}"`

### fn `def _md_kind(elem) -> str` `priv` (L1437-1465)
L1438-1439> ! @brief Short kind label for markdown output.
L1463> `return mapping.get(elem.element_type, "?")`

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1466-1488)
L1467-1469> ! @brief Extract clean text content from a comment element. @details Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.
L1474> Strip comment markers
L1479> Strip multi-line markers
L1486> `return text`

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1489-1505)
L1490-1491> ! @brief Extract clean text lines from a multi-line comment (preserving structure).
L1503> `return cleaned`

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1506-1566)
L1507-1509> ! @brief Build maps that associate comments with their adjacent definitions. @details Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)
L1512> Identify definition elements
L1520> Build adjacency map: comments preceding a definition (within 2 lines)
L1529> Extract file description from first comment(s), skip shebangs
L1534> Skip shebang lines and empty comments
L1542> Skip inline comments (name == "inline")
L1547> Check if this comment precedes a definition within 2 lines
L1554> Stop if we hit another element
L1559> Skip file-level description (already captured)
L1564> `return doc_for_def, standalone_comments, file_description`

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1567-1618)
L1569-1571> ! @brief Render body comments and exit points for a definition element. @details Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.
L1572> Build maps by line number
L1581> Collect all annotated line numbers
L1585> Skip if within an excluded range (child element)
L1599> Merge: show exit point code with comment as context
L1602> Strip inline comment from exit_text if it contains it

### fn `def format_markdown(elements: list, filepath: str, language: str,` (L1619-1818)
L1621-1623> ! @brief Format analysis as compact Markdown optimized for LLM agent consumption. @details Produces token-efficient output with: - File header with language, line count, element summary, and description - Imports in a code block - Hierarchical definitions with line-numbered doc comments - Body comments (L<N>> text) and exit points (L<N>> `return ...`) - Comments grouped with their relevant definitions - Standalone section/region comments preserved as context - Symbol index table for quick reference by line number
L1632> Build comment association maps
L1635> ── Header ────────────────────────────────────────────────────────
L1647> ── Imports ───────────────────────────────────────────────────────
L1660> ── Build decorator map: line -> decorator text ───────────────────
L1666> ── Definitions ───────────────────────────────────────────────────
L1706> Collect associated doc comments for this definition
L1729> For impl blocks, use the full first line as sig
L1737> Show associated doc comment with line number
L1747> Body annotations: comments and exit points
L1748> For containers with children, exclude annotations
L1749> that fall within a child's line range (including
L1750> doc comments that immediately precede the child)
L1755> Extend range to include preceding doc comment
L1764> Children with their doc comments and body annotations
L1786> Child body annotations (indented)
L1792> ── Standalone Comments (section/region markers, TODOs, notes) ────
L1795> Group consecutive comments (within 2 lines of each other)
L1814> Multi-line comment block: show as region

### fn `def main()` (L1866-1983)
L1867> ! @brief Execute the standalone source analyzer CLI command.
L1932> `sys.exit(0)`
L1938> `sys.exit(1)`
L1941> `sys.exit(1)`
L1943> Optional filtering

## Comments
- L2: ! @brief source_analyzer.py - Multi-language source code analyzer. @details Inspired by tree-sitter, this module analyzes source files across multi...
- L47: ! @brief Element found in source file.
- L64: ! @brief Return the normalized printable label for element_type. @return Stable uppercase label used in markdown rendering output.
- L99: ! @brief Language recognition pattern specification.
- L110: ! @brief Build specifications for all supported languages.
- L114: ── Python ──────────────────────────────────────────────────────────
- L135: ── C ───────────────────────────────────────────────────────────────
- L169: ── C++ ─────────────────────────────────────────────────────────────
- L199: ── Rust ────────────────────────────────────────────────────────────
- L231: ── JavaScript ──────────────────────────────────────────────────────
- L259: ── TypeScript ──────────────────────────────────────────────────────
- L292: ── Java ────────────────────────────────────────────────────────────
- L324: ── Go ──────────────────────────────────────────────────────────────
- L351: ── Ruby ────────────────────────────────────────────────────────────
- L373: ── PHP ─────────────────────────────────────────────────────────────
- L397: ── Swift ───────────────────────────────────────────────────────────
- L427: ── Kotlin ──────────────────────────────────────────────────────────
- L456: ── Scala ───────────────────────────────────────────────────────────
- L482: ── Lua ─────────────────────────────────────────────────────────────
- L498: ── Shell (Bash) ────────────────────────────────────────────────────
- L518: ── Perl ────────────────────────────────────────────────────────────
- L536: ── Haskell ─────────────────────────────────────────────────────────
- L558: ── Zig ─────────────────────────────────────────────────────────────
- L582: ── Elixir ──────────────────────────────────────────────────────────
- L604: ── C# ──────────────────────────────────────────────────────────────
- L643: Common aliases
- L672: ! @brief Return list of supported languages (without aliases).
- L683: ! @brief Analyze a source file and return the list of SourceElement found.
- L699: Multi-line comment state
- L707: ── Multi-line comment handling ──────────────────────────
- L724-726: ── Multi-line comment start ──────────────────────────── | Special handling for Python docstrings and =begin/=pod blocks
- L730-732: Check not inside a string | Check if multi-line comment closes on same line
- L744: Python: """ ... """ sulla stessa riga
- L761: ── Single-line comment ───────────────────────────────────
- L765: If comment is the entire line (aside from whitespace)
- L776: Inline comment: add both element and comment
- L786: ── Language patterns ─────────────────────────────────────
- L799: Single-line types: don't search for block
- L816: Limit extract to max 5 lines for readability
- L832: ! @brief Check if position pos is inside a string literal.
- L862: ! @brief Find position of single-line comment, ignoring strings.
- L898-901: ! @brief Find the end of a block (function, class, struct, etc.). @details Returns the index (1-b... | Per Python: basato sull'indentazione
- L916: Per linguaggi con parentesi graffe
- L935: If no opening braces found, return just the first line
- L940: Per Ruby/Elixir/Lua: basato su end keyword
- L953: Per Haskell: basato sull'indentazione
- L974: ! @brief Enrich elements with signatures, hierarchy, visibility, inheritance. @details Call after analyze() to add metadata for LLM-optimized markd...
- L988: ! @brief Extract clean identifiers from name fields. @details Due to regex group nesting, name may contain the full match expression (e.g. 'class M...
- L995-996: Try to re-extract the name from the element's extract line | using the original pattern (which has group 2 as the identifier)
- L1004-1005: Take highest non-None non-empty group | (group 2+ = identifier, group 1 = full match)
- L1014: ! @brief Extract clean signatures from element extracts.
- L1030: ! @brief Detect parent-child relationships between elements. @details Containers (class, struct, module, etc.) remain at depth=0. Non-container ele...
- L1064: ! @brief Extract visibility/access modifiers from elements.
- L1078: ! @brief Parse visibility modifier from a signature line.
- L1123: ! @brief Extract inheritance/implementation info from class-like elements.
- L1136: ! @brief Parse inheritance info from a class/struct declaration line.
- L1164: ── Exit point patterns per language family ──────────────────────
- L1173: ! @brief Extract comments and exit points from within function/class bodies. @details Reads the source file and scans each definition's line range ...
- L1186: Only process definitions that span multiple lines
- L1204: Scan the body (lines after the definition line)
- L1219: Multi-line comment tracking within body
- L1234: Check for multi-line comment start
- L1239: Single-line multi-comment
- L1263: Single-line comment (full line)
- L1273: Standalone comment line in body
- L1279: Inline comment after code
- L1284: Exit points
- L1297: ! @brief Strip comment markers from a single line of comment text.
- L1310: ! @brief Format structured analysis output.
- L1321: ── Definitions section ────────────────────────────────────────────
- L1345: Prefix with line number
- L1355: ── Comments section ───────────────────────────────────────────────
- L1388: ── Complete structured listing ────────────────────────────────────
- L1395: Sort by start line
- L1413: Show first line of extract
- L1430: ! @brief Format element location compactly for markdown.
- L1438: ! @brief Short kind label for markdown output.
- L1467: ! @brief Extract clean text content from a comment element. @details Args: comment_elem: SourceElement with comment content max_length: if >0, trun...
- L1474: Strip comment markers
- L1479: Strip multi-line markers
- L1490: ! @brief Extract clean text lines from a multi-line comment (preserving structure).
- L1507: ! @brief Build maps that associate comments with their adjacent definitions. @details Returns: - doc_for_def: dict mapping def line_start -> list o...
- L1512: Identify definition elements
- L1520: Build adjacency map: comments preceding a definition (within 2 lines)
- L1529: Extract file description from first comment(s), skip shebangs
- L1534: Skip shebang lines and empty comments
- L1542: Skip inline comments (name == "inline")
- L1547: Check if this comment precedes a definition within 2 lines
- L1554: Stop if we hit another element
- L1559: Skip file-level description (already captured)
- L1569-1572: ! @brief Render body comments and exit points for a definition element. @details Merges body_comm... | Build maps by line number
- L1581: Collect all annotated line numbers
- L1585: Skip if within an excluded range (child element)
- L1599: Merge: show exit point code with comment as context
- L1602: Strip inline comment from exit_text if it contains it
- L1621: ! @brief Format analysis as compact Markdown optimized for LLM agent consumption. @details Produces token-efficient output with: - File header with...
- L1632: Build comment association maps
- L1635: ── Header ────────────────────────────────────────────────────────
- L1647: ── Imports ───────────────────────────────────────────────────────
- L1660: ── Build decorator map: line -> decorator text ───────────────────
- L1666: ── Definitions ───────────────────────────────────────────────────
- L1706: Collect associated doc comments for this definition
- L1729: For impl blocks, use the full first line as sig
- L1737: Show associated doc comment with line number
- L1747-1750: Body annotations: comments and exit points | For containers with children, exclude annotations | that fall within a child's line range (including | doc comments that immediately precede the child)
- L1755: Extend range to include preceding doc comment
- L1764: Children with their doc comments and body annotations
- L1786: Child body annotations (indented)
- L1792: ── Standalone Comments (section/region markers, TODOs, notes) ────
- L1795: Group consecutive comments (within 2 lines of each other)
- L1814: Multi-line comment block: show as region
- L1827: ── Symbol Index ──────────────────────────────────────────────────
- L1847-1848: Only show sig for functions/methods/classes (not vars/consts | which already show full content in Definitions section)
- L1867: ! @brief Execute the standalone source analyzer CLI command.
- L1943: Optional filtering

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ElementType`|class|pub|15-44|class ElementType(Enum)|
|`ElementType.FUNCTION`|var|pub|18||
|`ElementType.METHOD`|var|pub|19||
|`ElementType.CLASS`|var|pub|20||
|`ElementType.STRUCT`|var|pub|21||
|`ElementType.ENUM`|var|pub|22||
|`ElementType.TRAIT`|var|pub|23||
|`ElementType.INTERFACE`|var|pub|24||
|`ElementType.MODULE`|var|pub|25||
|`ElementType.IMPL`|var|pub|26||
|`ElementType.MACRO`|var|pub|27||
|`ElementType.CONSTANT`|var|pub|28||
|`ElementType.VARIABLE`|var|pub|29||
|`ElementType.TYPE_ALIAS`|var|pub|30||
|`ElementType.IMPORT`|var|pub|31||
|`ElementType.DECORATOR`|var|pub|32||
|`ElementType.COMMENT_SINGLE`|var|pub|33||
|`ElementType.COMMENT_MULTI`|var|pub|34||
|`ElementType.COMPONENT`|var|pub|35||
|`ElementType.PROTOCOL`|var|pub|36||
|`ElementType.EXTENSION`|var|pub|37||
|`ElementType.UNION`|var|pub|38||
|`ElementType.NAMESPACE`|var|pub|39||
|`ElementType.PROPERTY`|var|pub|40||
|`ElementType.SIGNAL`|var|pub|41||
|`ElementType.TYPEDEF`|var|pub|42||
|`SourceElement`|class|pub|46-96|class SourceElement|
|`SourceElement.type_label`|fn|pub|63-96|def type_label(self) -> str|
|`LanguageSpec`|class|pub|98-108|class LanguageSpec|
|`build_language_specs`|fn|pub|109-308|def build_language_specs() -> dict|
|`SourceAnalyzer`|class|pub|662-861|class SourceAnalyzer|
|`SourceAnalyzer.__init__`|fn|priv|667-670|def __init__(self)|
|`SourceAnalyzer.get_supported_languages`|fn|pub|671-681|def get_supported_languages(self) -> list|
|`SourceAnalyzer.analyze`|fn|pub|682-830|def analyze(self, filepath: str, language: str) -> list|
|`SourceAnalyzer._in_string_context`|fn|priv|831-860|def _in_string_context(self, line: str, pos: int, spec: L...|
|`_find_comment`|fn|priv|861-895|def _find_comment(self, line: str, spec: LanguageSpec) ->...|
|`_find_block_end`|fn|priv|896-969|def _find_block_end(self, lines: list, start_idx: int,|
|`enrich`|fn|pub|972-986|def enrich(self, elements: list, language: str,|
|`_clean_names`|fn|priv|987-1012|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1013-1028|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1029-1062|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1063-1075|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1076-1121|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1122-1133|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1134-1163|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1171-1294|def _extract_body_annotations(self, elements: list,|
|`_clean_comment_line`|fn|priv|1296-1307|def _clean_comment_line(text: str, spec) -> str|
|`format_output`|fn|pub|1308-1428|def format_output(elements: list, filepath: str, language...|
|`_md_loc`|fn|priv|1429-1436|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1437-1465|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1466-1488|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1489-1505|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1506-1566|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1567-1618|def _render_body_annotations(out: list, elem, indent: str...|
|`format_markdown`|fn|pub|1619-1818|def format_markdown(elements: list, filepath: str, langua...|
|`main`|fn|pub|1866-1983|def main()|


---

# token_counter.py | Python | 99L | 7 symbols | 2 imports | 8 comments
> Path: `/home/ogekuri/useReq/src/usereq/token_counter.py`
> ! @brief token_counter.py - Token and character counting for generated output. @details Uses tiktoken for accurate token counting compatible with OpenAI/Claude models.

## Imports
```
import os
import tiktoken
```

## Definitions

### class `class TokenCounter` (L10-34)
- fn `def __init__(self, encoding_name: str = "cl100k_base")` `priv` (L14-19) L11> ! @brief Count tokens using tiktoken encoding (cl100k_base by default).
  L15-17> ! @brief Initialize token counter with a specific tiktoken encoding. @param encoding_name Name of tiktoken encoding used for tokenization.
- fn `def count_tokens(self, content: str) -> int` (L20-27) L15> ! @brief Initialize token counter with a specific tiktoken encoding. @param encoding_name Name of...
  L21-22> ! @brief Count tokens in content string.
  L24> `return len(self.encoding.encode(content, disallowed_special=()))`
  L26> `return 0`
- fn `def count_chars(content: str) -> int` (L29-34)
  L30-31> ! @brief Count characters in content string.
  L32> `return len(content)`

### fn `def count_file_metrics(content: str,` (L35-46)
L37-39> ! @brief Count tokens and chars for a content string. @details Returns dict with 'tokens' and 'chars' keys.
L41> `return {`

### fn `def count_files_metrics(file_paths: list,` (L47-72)
L49-51> ! @brief Count tokens and chars for a list of files. @details Returns a list of dicts with 'file', 'tokens', 'chars' keys. Errors are reported with tokens=0, chars=0, and an 'error' key.
L70> `return results`

### fn `def format_pack_summary(results: list) -> str` (L73-99)
L74-76> ! @brief Format a pack summary string from a list of file metrics. @details Args: results: list of dicts from count_files_metrics(). Returns: Formatted summary string with per-file details and totals.
L99> `return "\n".join(lines)`

## Comments
- L21: ! @brief Count tokens in content string.
- L30: ! @brief Count characters in content string.
- L37: ! @brief Count tokens and chars for a content string. @details Returns dict with 'tokens' and 'chars' keys.
- L49: ! @brief Count tokens and chars for a list of files. @details Returns a list of dicts with 'file', 'tokens', 'chars' keys. Errors are reported with...
- L74: ! @brief Format a pack summary string from a list of file metrics. @details Args: results: list of dicts from count_files_metrics(). Returns: Forma...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`TokenCounter`|class|pub|10-34|class TokenCounter|
|`TokenCounter.__init__`|fn|priv|14-19|def __init__(self, encoding_name: str = "cl100k_base")|
|`TokenCounter.count_tokens`|fn|pub|20-27|def count_tokens(self, content: str) -> int|
|`TokenCounter.count_chars`|fn|pub|29-34|def count_chars(content: str) -> int|
|`count_file_metrics`|fn|pub|35-46|def count_file_metrics(content: str,|
|`count_files_metrics`|fn|pub|47-72|def count_files_metrics(file_paths: list,|
|`format_pack_summary`|fn|pub|73-99|def format_pack_summary(results: list) -> str|

