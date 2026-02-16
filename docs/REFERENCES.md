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
        ├── find_constructs.py
        ├── generate_markdown.py
        ├── pdoc_utils.py
        ├── source_analyzer.py
        └── token_counter.py
```

# __init__.py | Python | 23L | 0 symbols | 9 imports | 3 comments
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
from . import find_constructs  # usereq.find_constructs submodule
from .cli import main  # re-export of CLI entry point
```

## Comments
- L6: The current version of the package.
- L23: ! @brief Public package exports for CLI entrypoint and utility submodules.


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

# cli.py | Python | 2454L | 92 symbols | 23 imports | 147 comments
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

### fn `def _get_available_tags_help() -> str` `priv` (L66-77)
L67-70> ! @brief Generate available TAGs help text for argument parser. @return Formatted multi-line string listing TAGs by language. @details Imports format_available_tags from find_constructs module to generate dynamic TAG listing for CLI help display.
L73> `return format_available_tags()`
L75> `return "(tag list unavailable)"`

### fn `def build_parser() -> argparse.ArgumentParser` (L78-259)
L79-80> ! @brief Builds the CLI argument parser.
L257> `return parser`

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L260-265)
L261-262> ! @brief Parses command-line arguments into a namespace.
L263> `return build_parser().parse_args(argv)`

### fn `def load_package_version() -> str` (L266-276)
L267-268> ! @brief Reads the package version from __init__.py.
L273> `raise ReqError("Error: unable to determine package version", 6)`
L274> `return match.group(1)`

### fn `def maybe_print_version(argv: list[str]) -> bool` (L277-285)
L278-279> ! @brief Handles --ver/--version by printing the version.
L282> `return True`
L283> `return False`

### fn `def run_upgrade() -> None` (L286-308)
L287-288> ! @brief Executes the upgrade using uv.
L301> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L303> `raise ReqError(`

### fn `def run_uninstall() -> None` (L309-328)
L310-311> ! @brief Executes the uninstallation using uv.
L321> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L323> `raise ReqError(`

### fn `def normalize_release_tag(tag: str) -> str` (L329-337)
L330-331> ! @brief Normalizes the release tag by removing a 'v' prefix if present.
L335> `return value.strip()`

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L338-360)
L339-341> ! @brief Converts a version into a numeric tuple for comparison. @details Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
L345> `return None`
L356> `return None`
L358> `return tuple(numbers) if numbers else None`

### fn `def is_newer_version(current: str, latest: str) -> bool` (L361-374)
L362-363> ! @brief Returns True if latest is greater than current.
L367> `return False`
L372> `return latest_norm > current_norm`

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L375-415)
L376-378> ! @brief Checks online for a new version and prints a warning. @details If the call fails or the response is invalid, it prints nothing and proceeds.
L397> `return`
L413> `return`

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L416-432)
L417-418> ! @brief Ensures the documentation directory exists under the project base.
L423> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L425> `raise ReqError(`
L430> `raise ReqError("Error: --docs-dir must specify a directory, not a file", 5)`

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L433-449)
L434-435> ! @brief Ensures the test directory exists under the project base.
L440> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L442> `raise ReqError(`
L447> `raise ReqError("Error: --tests-dir must specify a directory, not a file", 5)`

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L450-466)
L451-452> ! @brief Ensures the source directory exists under the project base.
L457> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L459> `raise ReqError(`
L464> `raise ReqError("Error: --src-dir must specify a directory, not a file", 5)`

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L467-502)
L468-469> ! @brief Normalizes the path relative to the project root when possible.
L471> `return ""`
L488> `return str(candidate.relative_to(project_base))`
L490> `return str(candidate)`
L493> `return str(resolved.relative_to(project_base))`
L499> `return trimmed`
L500> `return path_value`

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L503-513)
L504-505> ! @brief Resolves the absolute path starting from a normalized value.
L507> `return None`
L510> `return candidate`
L511> `return (project_base / candidate).resolve(strict=False)`

### fn `def format_substituted_path(value: str) -> str` (L514-521)
L515-516> ! @brief Uniforms path separators for substitutions.
L518> `return ""`
L519> `return value.replace(os.sep, "/")`

### fn `def compute_sub_path(` (L522-523)

### fn `def save_config(` (L538-543)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L560-597)
L561-562> ! @brief Loads parameters saved in .req/config.json.
L565> `raise ReqError(`
L572> `raise ReqError("Error: .req/config.json is not valid", 11) from exc`
L574> Fallback to legacy key names from pre-v0.59 config files.
L579> `raise ReqError("Error: missing or invalid 'guidelines-dir' field in .req/config.json", 11)`
L581> `raise ReqError("Error: missing or invalid 'docs-dir' field in .req/config.json", 11)`
L583> `raise ReqError("Error: missing or invalid 'tests-dir' field in .req/config.json", 11)`
L589> `raise ReqError("Error: missing or invalid 'src-dir' field in .req/config.json", 11)`
L590> `return {`

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L598-625)
L599-600> ! @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
L602> `return ""`
L614> If there are no files, use the directory itself.
L619> `return f"`{rel_str}`"`
L621> `return ""`
L623> `return ", ".join(files)`

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L626-654)
L627-629> ! @brief Generates a list of relative file paths (no formatting) for printing. @details Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
L631> `return []`
L643> If there are no files, use the directory itself.
L648> `return [rel_str]`
L650> `return []`
L652> `return items`

### fn `def copy_guidelines_templates(` (L655-656)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L688-699)
L689-690> ! @brief Normalizes the path token optionally preserving the trailing slash.
L692> `return ""`
L695> `return ""`
L697> `return f"{normalized}{suffix}"`

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L700-709)
L701-702> ! @brief Validates that the path is not absolute and raises an error otherwise.
L704> `raise ReqError(`

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L710-717)
L711-712> ! @brief Returns text with token replacements applied.
L715> `return text`

### fn `def write_text_file(dst: Path, text: str) -> None` (L718-724)
L719-720> ! @brief Writes text to disk, ensuring the destination folder exists.

### fn `def copy_with_replacements(` (L725-726)

### fn `def normalize_description(value: str) -> str` (L735-745)
L736-737> ! @brief Normalizes a description by removing superfluous quotes and escapes.
L743> `return trimmed.replace('\\"', '"')`

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L746-774)
L747-748> ! @brief Converts a Markdown prompt to TOML for Gemini.
L750> `raise ReqError(`
L757> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L775-784)
L776-777> ! @brief Extracts front matter and body from Markdown.
L780> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`
L781> Explicitly return two strings to satisfy type annotation.
L782> `return match.group(1), match.group(2)`

### fn `def extract_description(frontmatter: str) -> str` (L785-793)
L786-787> ! @brief Extracts the description from front matter.
L790> `raise ReqError("No 'description:' field found inside the leading block.", 5)`
L791> `return normalize_description(desc_match.group(1).strip())`

### fn `def extract_argument_hint(frontmatter: str) -> str` (L794-802)
L795-796> ! @brief Extracts the argument-hint from front matter, if present.
L799> `return ""`
L800> `return normalize_description(match.group(1).strip())`

### fn `def extract_purpose_first_bullet(body: str) -> str` (L803-823)
L804-805> ! @brief Returns the first bullet of the Purpose section.
L813> `raise ReqError("Error: missing '## Purpose' section in prompt.", 7)`
L820> `return match.group(1).strip()`
L821> `raise ReqError("Error: no bullet found under the '## Purpose' section.", 7)`

### fn `def json_escape(value: str) -> str` (L824-829)
L825-826> ! @brief Escapes a string for JSON without external delimiters.
L827> `return json.dumps(value)[1:-1]`

### fn `def generate_kiro_resources(` (L830-833)

### fn `def render_kiro_agent(` (L853-862)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L896-904)
L897-898> ! @brief Replaces tokens in the specified file.

### fn `def yaml_double_quote_escape(value: str) -> str` (L905-910)
L906-907> ! @brief Minimal escape for a double-quoted string in YAML.
L908> `return value.replace("\\", "\\\\").replace('"', '\\"')`

### fn `def find_template_source() -> Path` (L911-922)
L912-913> ! @brief Returns the template source or raises an error.
L916> `return candidate`
L917> `raise ReqError(`

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L923-957)
L924-925> ! @brief Loads the Kiro template from centralized models configuration.
L928> Try models.json first (this function is called during generation, not with legacy flag check)
L939> `return agent_template, kiro_cfg`
L942> `return (`
L952> `raise ReqError(`

### fn `def strip_json_comments(text: str) -> str` (L958-978)
L959-960> ! @brief Removes // and /* */ comments to allow JSONC parsing.
L976> `return "\n".join(cleaned)`

### fn `def load_settings(path: Path) -> dict[str, Any]` (L979-990)
L980-981> ! @brief Loads JSON/JSONC settings, removing comments when necessary.
L984> `return json.loads(raw)`
L988> `return json.loads(cleaned)`

### fn `def load_centralized_models(` (L991-994)

### fn `def get_model_tools_for_prompt(` (L1038-1039)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1074-1091)
L1075-1077> ! @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt. @details Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
L1079> `return None`
L1088> `return mode_entry.get("tools")`
L1089> `return None`

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1092-1099)
L1093-1094> ! @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
L1097> `return f"[{quoted}]"`

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1100-1110)
L1101-1102> ! @brief Recursively merges dictionaries, prioritizing incoming values.
L1108> `return base`

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1111-1119)
L1112-1113> ! @brief Finds the VS Code settings template if available.
L1116> `return candidate`
L1117> `return None`

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1120-1130)
L1121-1122> ! @brief Generates chat.promptFilesRecommendations from available prompts.
L1125> `return recommendations`
L1128> `return recommendations`

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1131-1140)
L1132-1133> ! @brief Verifies that the path is under the project root.
L1135> `raise ReqError(`

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1141-1150)
L1142-1143> ! @brief Saves a backup of VS Code settings if the file exists.
L1145> Never create an absence marker. Backup only if the file exists.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1151-1162)
L1152-1153> ! @brief Restores VS Code settings from backup, if present.
L1160> Do not remove the target file if no backup exists: restore behavior disabled otherwise.

### fn `def prune_empty_dirs(root: Path) -> None` (L1163-1176)
L1160> Do not remove the target file if no backup exists: restore behavior disabled otherwise.
L1164-1165> ! @brief Removes empty directories under the specified root.
L1167> `return`

### fn `def remove_generated_resources(project_base: Path) -> None` (L1177-1217)
L1178-1179> ! @brief Removes resources generated by the tool in the project root.

### fn `def run_remove(args: Namespace) -> None` (L1218-1264)
L1219-1220> ! @brief Handles the removal of generated resources.
L1226> `raise ReqError(`
L1231> `raise ReqError(`
L1240> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1243> `raise ReqError(`
L1248> After validation and before any removal, check for a new version.
L1251> Do not perform any restore or removal of .vscode/settings.json during removal.

### fn `def run(args: Namespace) -> None` (L1265-1464)
L1266-1267> ! @brief Handles the main initialization flow.
L1272> Main flow: validates input, calculates paths, generates resources.
L1275> `return`
L1282> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1291> `raise ReqError(`
L1296> `raise ReqError(`
L1320> `raise ReqError("Error: invalid docs configuration values", 11)`
L1322> `raise ReqError("Error: invalid tests configuration value", 11)`
L1328> `raise ReqError("Error: invalid src configuration values", 11)`
L1368> `raise ReqError("Error: --guidelines-dir must be under the project base", 8)`
L1370> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L1372> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L1375> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L1400> `raise ReqError(`
L1407> Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
L1436> `raise ReqError(`
L1441> After validation and before any operation that modifies the filesystem, check for a new version.

- var `VERBOSE = args.verbose` (L1269) — ! @brief Handles the main initialization flow.
- var `DEBUG = args.debug` (L1270)
- var `PROMPT = prompt_path.stem` (L1610)
### fn `def _format_install_table(` `priv` (L2038-2040)
L2035> Build and print a simple installation report table describing which

### fn `def fmt(row: tuple[str, ...]) -> str` (L2061-2063)
L2062> `return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row))`

- var `EXCLUDED_DIRS = frozenset({` (L2081) — ── Excluded directories for --references and --compress ──────────────────
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2090) — ── Supported source file extensions ──────────────────────────────────────
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2098-2118)
L2095> File extensions considered during source directory scanning.
L2099-2101> ! @brief Recursively collect source files from the given directories. @details Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
L2108> Filter out excluded directories (modifies dirnames in-place)
L2116> `return collected`

### fn `def _build_ascii_tree(paths: list[str]) -> str` `priv` (L2119-2156)
L2120-2123> ! @brief Build a deterministic tree string from project-relative paths. @param paths Project-relative file paths. @return Rendered tree rooted at '.'.
L2154> `return "\n".join(lines)`

### fn `def _emit(` `priv` (L2141-2143)

### fn `def _format_files_structure_markdown(files: list[str], project_base: Path) -> str` `priv` (L2157-2167)
L2158-2162> ! @brief Format markdown section containing the scanned files tree. @param files Absolute file paths selected for --references processing. @param project_base Project root used to normalize relative paths. @return Markdown section with heading and fenced tree.
L2165> `return f"# Files Structure\n```\n{tree}\n```"`

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2168-2178)
L2169-2170> ! @brief Check if the parsed args contain a standalone file command.
L2171> `return bool(`

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2179-2189)
L2180-2181> ! @brief Check if the parsed args contain a project scan command.
L2182> `return bool(`

### fn `def run_files_tokens(files: list[str]) -> None` (L2190-2208)
L2191-2192> ! @brief Execute --files-tokens: count tokens for arbitrary files.
L2203> `raise ReqError("Error: no valid files provided.", 1)`

### fn `def run_files_references(files: list[str]) -> None` (L2209-2217)
L2210-2211> ! @brief Execute --files-references: generate markdown for arbitrary files.

### fn `def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None` (L2218-2232)
L2219-2222> ! @brief Execute --files-compress: compress arbitrary files. @param files List of source file paths to compress. @param enable_line_numbers If True, emits Lnn> prefixes in compressed entries.

### fn `def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None` (L2233-2258)
L2234-2237> ! @brief Execute --files-find: find constructs in arbitrary files. @param args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...]. @param enable_line_numbers If True, emits Lnn> prefixes in output.
L2241> `raise ReqError(`

### fn `def run_references(args: Namespace) -> None` (L2259-2272)
L2260-2261> ! @brief Execute --references: generate markdown for project source files.
L2267> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_compress_cmd(args: Namespace) -> None` (L2273-2290)
L2274-2276> ! @brief Execute --compress: compress project source files. @param args Parsed CLI arguments namespace.
L2282> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_find(args: Namespace) -> None` (L2291-2317)
L2292-2295> ! @brief Execute --find: find constructs in project source files. @param args Parsed CLI arguments namespace. @throws ReqError If no source files found or no constructs match criteria with available TAGs listing.
L2301> `raise ReqError("Error: no source files found in configured directories.", 1)`
L2303> args.find is a list [TAG, PATTERN]
L2315> `raise ReqError(str(e), 1)`

### fn `def run_tokens(args: Namespace) -> None` (L2318-2340)
L2319-2322> ! @brief Execute --tokens: count tokens for files directly in --docs-dir. @param args Parsed CLI arguments namespace. @details Requires --base/--here and --docs-dir, then delegates reporting to run_files_tokens.
L2330> `raise ReqError("Error: --tokens requires --docs-dir.", 1)`
L2337> `raise ReqError("Error: no files found in --docs-dir.", 1)`

### fn `def _resolve_project_base(args: Namespace) -> Path` `priv` (L2341-2361)
L2342-2346> ! @brief Resolve project base path for project-level commands. @param args Parsed CLI arguments namespace. @return Absolute path of project base. @throws ReqError If --base/--here is missing or the resolved path does not exist.
L2348> `raise ReqError(`
L2358> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L2359> `return project_base`

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L2362-2388)
L2363-2364> ! @brief Resolve project base and src-dirs for --references/--compress.
L2371> Source dirs can come from args or from config
L2379> `raise ReqError(`
L2384> `raise ReqError("Error: no source directories configured.", 1)`
L2386> `return project_base, src_dirs`

### fn `def main(argv: Optional[list[str]] = None) -> int` (L2389-2454)
L2390-2392> ! @brief CLI entry point for console_scripts and `-m` execution. @details Returns an exit code (0 success, non-zero on error).
L2398> `return 0`
L2401> `return 0`
L2404> `return 0`
L2406> `return 0`
L2410> Standalone file commands (no --base/--here required)
L2426> `return 0`
L2427> Project scan commands (require --base/--here)
L2437> `return 0`
L2438> Standard init flow requires --base or --here
L2440> `raise ReqError(`
L2446> `return e.code`
L2447> Unexpected error
L2453> `return 1`
L2454> `return 0`

- var `VERBOSE = getattr(args, "verbose", False)` (L2408)
- var `DEBUG = getattr(args, "debug", False)` (L2409)
## Comments
- L37: ! @brief Initialize an expected CLI failure payload. @param message Human-readable error message. @param code Process exit code bound to the failur...
- L47: ! @brief Prints an informational message.
- L53: ! @brief Prints a debug message if debugging is active.
- L60: ! @brief Prints a verbose message if verbose mode is active.
- L67: ! @brief Generate available TAGs help text for argument parser. @return Formatted multi-line string listing TAGs by language. @details Imports form...
- L79: ! @brief Builds the CLI argument parser.
- L261: ! @brief Parses command-line arguments into a namespace.
- L267: ! @brief Reads the package version from __init__.py.
- L278: ! @brief Handles --ver/--version by printing the version.
- L287: ! @brief Executes the upgrade using uv.
- L310: ! @brief Executes the uninstallation using uv.
- L330: ! @brief Normalizes the release tag by removing a 'v' prefix if present.
- L339: ! @brief Converts a version into a numeric tuple for comparison. @details Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
- L362: ! @brief Returns True if latest is greater than current.
- L376: ! @brief Checks online for a new version and prints a warning. @details If the call fails or the response is invalid, it prints nothing and proceeds.
- L417: ! @brief Ensures the documentation directory exists under the project base.
- L434: ! @brief Ensures the test directory exists under the project base.
- L451: ! @brief Ensures the source directory exists under the project base.
- L468: ! @brief Normalizes the path relative to the project root when possible.
- L504: ! @brief Resolves the absolute path starting from a normalized value.
- L515: ! @brief Uniforms path separators for substitutions.
- L525: ! @brief Calculates the relative path to use in tokens.
- L545: ! @brief Saves normalized parameters to .req/config.json.
- L561: ! @brief Loads parameters saved in .req/config.json.
- L574: Fallback to legacy key names from pre-v0.59 config files.
- L599: ! @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
- L614: If there are no files, use the directory itself.
- L627: ! @brief Generates a list of relative file paths (no formatting) for printing. @details Each entry is formatted as `guidelines/file.md` (forward sl...
- L643: If there are no files, use the directory itself.
- L658: ! @brief Copies guidelines templates from resources/guidelines/ to the target directory. @details Args: guidelines_dest: Target directory where tem...
- L689: ! @brief Normalizes the path token optionally preserving the trailing slash.
- L701: ! @brief Validates that the path is not absolute and raises an error otherwise.
- L711: ! @brief Returns text with token replacements applied.
- L719: ! @brief Writes text to disk, ensuring the destination folder exists.
- L728: ! @brief Copies a file substituting the indicated tokens with their values.
- L736: ! @brief Normalizes a description by removing superfluous quotes and escapes.
- L747: ! @brief Converts a Markdown prompt to TOML for Gemini.
- L776: ! @brief Extracts front matter and body from Markdown.
- L781: Explicitly return two strings to satisfy type annotation.
- L786: ! @brief Extracts the description from front matter.
- L795: ! @brief Extracts the argument-hint from front matter, if present.
- L804: ! @brief Returns the first bullet of the Purpose section.
- L825: ! @brief Escapes a string for JSON without external delimiters.
- L835: ! @brief Generates the resource list for the Kiro agent.
- L864: ! @brief Renders the Kiro agent JSON and populates main fields.
- L892: If parsing fails, return raw template to preserve previous behavior
- L897: ! @brief Replaces tokens in the specified file.
- L906: ! @brief Minimal escape for a double-quoted string in YAML.
- L912: ! @brief Returns the template source or raises an error.
- L924: ! @brief Loads the Kiro template from centralized models configuration.
- L928: Try models.json first (this function is called during generation, not with legacy flag check)
- L959: ! @brief Removes // and /* */ comments to allow JSONC parsing.
- L980: ! @brief Loads JSON/JSONC settings, removing comments when necessary.
- L996: ! @brief Loads centralized models configuration from common/models.json. @details Returns a map cli_name -> parsed_json or None if not present. Whe...
- L1002: Priority 1: preserve_models_path if provided and exists
- L1006: Priority 2: legacy mode
- L1013: Fallback: standard models.json
- L1020: Load the centralized configuration
- L1028: Extract individual CLI configs
- L1041: ! @brief Extracts model and tools for the prompt from the CLI config. @details Returns (model, tools) where each value can be None if not available.
- L1057-1058: Use the unified key name 'tools' across all CLI configs. | Accept either a list of strings or a CSV string in the config.json.
- L1066: Parse comma-separated string into list
- L1075: ! @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt. @details Can return a list of strings, a string, or None depending o...
- L1093: ! @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
- L1101: ! @brief Recursively merges dictionaries, prioritizing incoming values.
- L1112: ! @brief Finds the VS Code settings template if available.
- L1121: ! @brief Generates chat.promptFilesRecommendations from available prompts.
- L1132: ! @brief Verifies that the path is under the project root.
- L1142-1145: ! @brief Saves a backup of VS Code settings if the file exists. | Never create an absence marker. Backup only if the file exists.
- L1152: ! @brief Restores VS Code settings from backup, if present.
- L1164: ! @brief Removes empty directories under the specified root.
- L1178: ! @brief Removes resources generated by the tool in the project root.
- L1219: ! @brief Handles the removal of generated resources.
- L1248: After validation and before any removal, check for a new version.
- L1251: Do not perform any restore or removal of .vscode/settings.json during removal.
- L1272: Main flow: validates input, calculates paths, generates resources.
- L1407: Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
- L1441: After validation and before any operation that modifies the filesystem, check for a new version.
- L1471-1472: Copy models configuration to .req/models.json based on legacy mode (REQ-084) | Skip if --preserve-models is active
- L1496: Create requirements.md only if the --docs-dir folder is empty.
- L1506: Generate the file list for the %%GUIDELINES_FILES%% token.
- L1575: Load CLI configs only if requested to include model/tools
- L1586: Determine preserve_models_path (REQ-082)
- L1617: (Removed: bootstrap file inlining and YOLO stop/approval substitution)
- L1633: Precompute description and Claude metadata so provider blocks can reuse them safely.
- L1643: .codex/prompts
- L1652: .codex/skills/req/<prompt>/SKILL.md
- L1682: Gemini TOML
- L1720: .kiro/prompts
- L1730: .claude/agents
- L1756: .github/agents
- L1784: .github/prompts
- L1816: .kiro/agents
- L1846: .opencode/agent
- L1877: .opencode/command
- L1922: .claude/commands/req
- L1980: Load existing settings (if present) and those from the template.
- L1986: If checking/loading fails, consider it empty
- L1991: Merge without modifying original until sure.
- L2001: If final result is identical to existing, do not rewrite nor backup.
- L2006: If changes are expected, create backup only if file exists.
- L2009: Write final settings.
- L2017-2018: Final success notification: printed only when the command completed all | intended filesystem modifications without raising an exception.
- L2025-2026: Print the discovered directories used for token substitutions | as required by REQ-078: one item per line prefixed with '- '.
- L2042: ! @brief Format the installation summary table aligning header, prompts, and rows.
- L2086: Directories excluded from source scanning in --references and --compress.
- L2099: ! @brief Recursively collect source files from the given directories. @details Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
- L2108: Filter out excluded directories (modifies dirnames in-place)
- L2120: ! @brief Build a deterministic tree string from project-relative paths. @param paths Project-relative file paths. @return Rendered tree rooted at '.'.
- L2158: ! @brief Format markdown section containing the scanned files tree. @param files Absolute file paths selected for --references processing. @param p...
- L2169: ! @brief Check if the parsed args contain a standalone file command.
- L2180: ! @brief Check if the parsed args contain a project scan command.
- L2191: ! @brief Execute --files-tokens: count tokens for arbitrary files.
- L2210: ! @brief Execute --files-references: generate markdown for arbitrary files.
- L2219: ! @brief Execute --files-compress: compress arbitrary files. @param files List of source file paths to compress. @param enable_line_numbers If True...
- L2234: ! @brief Execute --files-find: find constructs in arbitrary files. @param args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...]. @param enable...
- L2260: ! @brief Execute --references: generate markdown for project source files.
- L2274: ! @brief Execute --compress: compress project source files. @param args Parsed CLI arguments namespace.
- L2292: ! @brief Execute --find: find constructs in project source files. @param args Parsed CLI arguments namespace. @throws ReqError If no source files f...
- L2303: args.find is a list [TAG, PATTERN]
- L2319: ! @brief Execute --tokens: count tokens for files directly in --docs-dir. @param args Parsed CLI arguments namespace. @details Requires --base/--he...
- L2342: ! @brief Resolve project base path for project-level commands. @param args Parsed CLI arguments namespace. @return Absolute path of project base. @...
- L2363: ! @brief Resolve project base and src-dirs for --references/--compress.
- L2371: Source dirs can come from args or from config
- L2390: ! @brief CLI entry point for console_scripts and `-m` execution. @details Returns an exit code (0 success, non-zero on error).
- L2410: Standalone file commands (no --base/--here required)
- L2427: Project scan commands (require --base/--here)
- L2438: Standard init flow requires --base or --here

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
|`_get_available_tags_help`|fn|priv|66-77|def _get_available_tags_help() -> str|
|`build_parser`|fn|pub|78-259|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|260-265|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|266-276|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|277-285|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|286-308|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|309-328|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|329-337|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|338-360|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|361-374|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|375-415|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|416-432|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|433-449|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|450-466|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|467-502|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|503-513|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|514-521|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|522-523|def compute_sub_path(|
|`save_config`|fn|pub|538-543|def save_config(|
|`load_config`|fn|pub|560-597|def load_config(project_base: Path) -> dict[str, str | li...|
|`generate_guidelines_file_list`|fn|pub|598-625|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|626-654|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`copy_guidelines_templates`|fn|pub|655-656|def copy_guidelines_templates(|
|`make_relative_token`|fn|pub|688-699|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|700-709|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|710-717|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|718-724|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|725-726|def copy_with_replacements(|
|`normalize_description`|fn|pub|735-745|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|746-774|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|775-784|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|785-793|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|794-802|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|803-823|def extract_purpose_first_bullet(body: str) -> str|
|`json_escape`|fn|pub|824-829|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|830-833|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|853-862|def render_kiro_agent(|
|`replace_tokens`|fn|pub|896-904|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|905-910|def yaml_double_quote_escape(value: str) -> str|
|`find_template_source`|fn|pub|911-922|def find_template_source() -> Path|
|`load_kiro_template`|fn|pub|923-957|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|958-978|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|979-990|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|991-994|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|1038-1039|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1074-1091|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1092-1099|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1100-1110|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1111-1119|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1120-1130|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1131-1140|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1141-1150|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1151-1162|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1163-1176|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1177-1217|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1218-1264|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1265-1464|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1269||
|`DEBUG`|var|pub|1270||
|`PROMPT`|var|pub|1610||
|`_format_install_table`|fn|priv|2038-2040|def _format_install_table(|
|`fmt`|fn|pub|2061-2063|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|2081||
|`SUPPORTED_EXTENSIONS`|var|pub|2090||
|`_collect_source_files`|fn|priv|2098-2118|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_build_ascii_tree`|fn|priv|2119-2156|def _build_ascii_tree(paths: list[str]) -> str|
|`_emit`|fn|priv|2141-2143|def _emit(|
|`_format_files_structure_markdown`|fn|priv|2157-2167|def _format_files_structure_markdown(files: list[str], pr...|
|`_is_standalone_command`|fn|priv|2168-2178|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2179-2189|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2190-2208|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2209-2217|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2218-2232|def run_files_compress(files: list[str], enable_line_numb...|
|`run_files_find`|fn|pub|2233-2258|def run_files_find(args_list: list[str], enable_line_numb...|
|`run_references`|fn|pub|2259-2272|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2273-2290|def run_compress_cmd(args: Namespace) -> None|
|`run_find`|fn|pub|2291-2317|def run_find(args: Namespace) -> None|
|`run_tokens`|fn|pub|2318-2340|def run_tokens(args: Namespace) -> None|
|`_resolve_project_base`|fn|priv|2341-2361|def _resolve_project_base(args: Namespace) -> Path|
|`_resolve_project_src_dirs`|fn|priv|2362-2388|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|2389-2454|def main(argv: Optional[list[str]] = None) -> int|
|`VERBOSE`|var|pub|2408||
|`DEBUG`|var|pub|2409||


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

# compress_files.py | Python | 102L | 3 symbols | 4 imports | 5 comments
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

### fn `def _extract_line_range(compressed_with_line_numbers: str) -> tuple[int, int]` `priv` (L12-29)
L13-16> ! @brief Extract source line interval from compressed output with Lnn> prefixes. @param compressed_with_line_numbers Compressed payload generated with include_line_numbers=True. @return Tuple (line_start, line_end) derived from preserved Lnn> prefixes; returns (0, 0) when no prefixed lines exist.
L25> `return 0, 0`
L27> `return line_numbers[0], line_numbers[-1]`

### fn `def compress_files(filepaths: list[str],` (L30-81)
L33-35> ! @brief Compress multiple source files and concatenate with identifying headers. @details Each file is compressed and emitted as: header line `@@@ <path> | <lang>`, line-range metadata `- Lines: <start>-<end>`, and fenced code block delimited by triple backticks. Line range is derived from the already computed Lnn> prefixes to preserve existing numbering logic. Files are separated by a blank line. Args: filepaths: List of source file paths. include_line_numbers: If True (default), keep Lnn> prefixes in code block lines. verbose: If True, emits progress status messages on stderr. Returns: Concatenated compressed output string. Raises: ValueError: If no files could be processed.
L73> `raise ValueError("No valid source files processed")`
L79> `return "\n\n".join(parts)`

### fn `def main()` (L82-100)
L83> ! @brief Execute the multi-file compression CLI command.
L98> `sys.exit(1)`

## Comments
- L2: ! @brief compress_files.py - Compress and concatenate multiple source files. @details Uses the compress module to strip comments and whitespace fro...
- L13: ! @brief Extract source line interval from compressed output with Lnn> prefixes. @param compressed_with_line_numbers Compressed payload generated w...
- L33: ! @brief Compress multiple source files and concatenate with identifying headers. @details Each file is compressed and emitted as: header line `@@@...
- L83: ! @brief Execute the multi-file compression CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_extract_line_range`|fn|priv|12-29|def _extract_line_range(compressed_with_line_numbers: str...|
|`compress_files`|fn|pub|30-81|def compress_files(filepaths: list[str],|
|`main`|fn|pub|82-100|def main()|


---

# find_constructs.py | Python | 239L | 8 symbols | 7 imports | 14 comments
> Path: `/home/ogekuri/useReq/src/usereq/find_constructs.py`
> ! @brief find_constructs.py - Find and extract specific constructs from source files. @details Filters source code constructs (CLASS, FUNCTION, etc.) by type tag and name regex pattern, generating ...

## Imports
```
import os
import re
import sys
from pathlib import Path
from .source_analyzer import SourceAnalyzer
from .compress import detect_language
import argparse
```

## Definitions

- var `LANGUAGE_TAGS = {` (L16) — ── Language-specific TAG support map ────────────────────────────────────────
### fn `def format_available_tags() -> str` (L40-53)
L41-44> ! @brief Generate formatted list of available TAGs per language. @return Multi-line string listing each language with its supported TAGs. @details Iterates LANGUAGE_TAGS dictionary, formats each entry as "- Language: TAG1, TAG2, ..." with language capitalized and tags alphabetically sorted and comma-separated.
L51> `return "\n".join(lines)`

### fn `def parse_tag_filter(tag_string: str) -> set[str]` (L54-61)
L55-58> ! @brief Parse pipe-separated tag filter into a normalized set. @param tag_string Raw tag filter string (e.g., "CLASS|FUNCTION"). @return Set of uppercase tag identifiers.
L59> `return {tag.strip().upper() for tag in tag_string.split("|") if tag.strip()}`

### fn `def language_supports_tags(lang: str, tag_set: set[str]) -> bool` (L62-71)
L63-67> ! @brief Check if the language supports at least one of the requested tags. @param lang Normalized language identifier. @param tag_set Set of requested TAG identifiers. @return True if intersection is non-empty, False otherwise.
L69> `return bool(supported & tag_set)`

### fn `def construct_matches(element, tag_set: set[str], pattern: str) -> bool` (L72-88)
L73-78> ! @brief Check if a source element matches tag filter and regex pattern. @param element SourceElement instance from analyzer. @param tag_set Set of requested TAG identifiers. @param pattern Regex pattern string to test against element name. @return True if element type is in tag_set and name matches pattern.
L80> `return False`
L82> `return False`
L84> `return bool(re.search(pattern, element.name))`
L86> `return False`

### fn `def format_construct(element, source_lines: list[str], include_line_numbers: bool) -> str` (L89-117)
L90-96> ! @brief Format a single matched construct for markdown output with complete code extraction. @param element SourceElement instance containing line range indices. @param source_lines Complete source file content as list of lines. @param include_line_numbers If True, prefix code lines with Lnn> format. @return Formatted markdown block for the construct with complete code from line_start to line_end. @details Extracts the complete construct code directly from source_lines using element.line_start and element.line_end indices, replacing the truncated element.extract field to ensure full construct visibility without snippet limitations or ellipsis truncation.
L103> Extract COMPLETE code block from source file (not truncated extract)
L115> `return "\n".join(lines)`

### fn `def find_constructs_in_files(` (L118-123)

### fn `def main()` (L204-237)
L205> ! @brief Execute the construct finding CLI command.
L235> `sys.exit(1)`

## Comments
- L2: ! @brief find_constructs.py - Find and extract specific constructs from source files. @details Filters source code constructs (CLASS, FUNCTION, etc...
- L41: ! @brief Generate formatted list of available TAGs per language. @return Multi-line string listing each language with its supported TAGs. @details ...
- L55: ! @brief Parse pipe-separated tag filter into a normalized set. @param tag_string Raw tag filter string (e.g., "CLASS|FUNCTION"). @return Set of up...
- L63: ! @brief Check if the language supports at least one of the requested tags. @param lang Normalized language identifier. @param tag_set Set of reque...
- L73: ! @brief Check if a source element matches tag filter and regex pattern. @param element SourceElement instance from analyzer. @param tag_set Set of...
- L90: ! @brief Format a single matched construct for markdown output with complete code extraction. @param element SourceElement instance containing line...
- L103: Extract COMPLETE code block from source file (not truncated extract)
- L125: ! @brief Find and extract constructs matching tag filter and regex pattern from multiple files. @details Analyzes each file with SourceAnalyzer, fi...
- L153: Check if language supports at least one requested tag
- L161: Read complete source file for full construct extraction
- L169: Filter elements matching tag and pattern
- L205: ! @brief Execute the construct finding CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`LANGUAGE_TAGS`|var|pub|16||
|`format_available_tags`|fn|pub|40-53|def format_available_tags() -> str|
|`parse_tag_filter`|fn|pub|54-61|def parse_tag_filter(tag_string: str) -> set[str]|
|`language_supports_tags`|fn|pub|62-71|def language_supports_tags(lang: str, tag_set: set[str]) ...|
|`construct_matches`|fn|pub|72-88|def construct_matches(element, tag_set: set[str], pattern...|
|`format_construct`|fn|pub|89-117|def format_construct(element, source_lines: list[str], in...|
|`find_constructs_in_files`|fn|pub|118-123|def find_constructs_in_files(|
|`main`|fn|pub|204-237|def main()|


---

# generate_markdown.py | Python | 115L | 4 symbols | 3 imports | 7 comments
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

### fn `def generate_markdown(filepaths: list[str], verbose: bool = False) -> str` (L46-98)
L47-49> ! @brief Analyze source files and return concatenated markdown. @details Args: filepaths: List of source file paths to analyze. verbose: If True, emits progress status messages on stderr. Returns: Concatenated markdown string with all file analyses. Raises: ValueError: If no valid source files are found.
L90> `raise ValueError("No valid source files processed")`
L96> `return "\n\n---\n\n".join(md_parts)`

### fn `def main()` (L99-113)
L100> ! @brief Execute the standalone markdown generation CLI command.
L104> `sys.exit(1)`
L111> `sys.exit(1)`

## Comments
- L2: ! @brief generate_markdown.py - Generate concatenated markdown from arbitrary source files. @details Analyzes each input file with source_analyzer ...
- L40: ! @brief Detect language from file extension.
- L47: ! @brief Analyze source files and return concatenated markdown. @details Args: filepaths: List of source file paths to analyze. verbose: If True, e...
- L100: ! @brief Execute the standalone markdown generation CLI command.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|12||
|`detect_language`|fn|pub|39-45|def detect_language(filepath: str) -> str | None|
|`generate_markdown`|fn|pub|46-98|def generate_markdown(filepaths: list[str], verbose: bool...|
|`main`|fn|pub|99-113|def main()|


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

