# __init__.py | Python | 24L | 0 symbols | 8 imports | 2 comments
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

# cli.py | Python | 2192L | 82 symbols | 20 imports | 139 comments
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
### class `class ReqError(Exception)` : Exception (L31-39)
L28> Whether debug output is enabled.
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L34-39) L32> Dedicated exception for expected CLI errors.

### fn `def log(msg: str) -> None` (L40-44)
L41> Prints an informational message.

### fn `def dlog(msg: str) -> None` (L45-50)
L46> Prints a debug message if debugging is active.

### fn `def vlog(msg: str) -> None` (L51-56)
L52> Prints a verbose message if verbose mode is active.

### fn `def build_parser() -> argparse.ArgumentParser` (L57-214)
L58> Builds the CLI argument parser.
L212> `return parser`

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L215-219)
L216> Parses command-line arguments into a namespace.
L217> `return build_parser().parse_args(argv)`

### fn `def load_package_version() -> str` (L220-229)
L221> Reads the package version from __init__.py.
L226> `raise ReqError("Error: unable to determine package version", 6)`
L227> `return match.group(1)`

### fn `def maybe_print_version(argv: list[str]) -> bool` (L230-237)
L231> Handles --ver/--version by printing the version.
L234> `return True`
L235> `return False`

### fn `def run_upgrade() -> None` (L238-259)
L239> Executes the upgrade using uv.
L252> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L254> `raise ReqError(`

### fn `def run_uninstall() -> None` (L260-278)
L261> Executes the uninstallation using uv.
L271> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L273> `raise ReqError(`

### fn `def normalize_release_tag(tag: str) -> str` (L279-286)
L280> Normalizes the release tag by removing a 'v' prefix if present.
L284> `return value.strip()`

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L287-310)
L288-291> Converts a version into a numeric tuple for comparison. Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
L295> `return None`
L306> `return None`
L308> `return tuple(numbers) if numbers else None`

### fn `def is_newer_version(current: str, latest: str) -> bool` (L311-323)
L312> Returns True if latest is greater than current.
L316> `return False`
L321> `return latest_norm > current_norm`

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L324-365)
L325-328> Checks online for a new version and prints a warning. If the call fails or the response is invalid, it prints nothing and proceeds.
L347> `return`
L363> `return`

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L366-381)
L367> Ensures the documentation directory exists under the project base.
L372> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L374> `raise ReqError(`
L379> `raise ReqError("Error: --docs-dir must specify a directory, not a file", 5)`

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L382-397)
L383> Ensures the test directory exists under the project base.
L388> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L390> `raise ReqError(`
L395> `raise ReqError("Error: --tests-dir must specify a directory, not a file", 5)`

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L398-413)
L399> Ensures the source directory exists under the project base.
L404> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L406> `raise ReqError(`
L411> `raise ReqError("Error: --src-dir must specify a directory, not a file", 5)`

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L414-448)
L415> Normalizes the path relative to the project root when possible.
L417> `return ""`
L434> `return str(candidate.relative_to(project_base))`
L436> `return str(candidate)`
L439> `return str(resolved.relative_to(project_base))`
L445> `return trimmed`
L446> `return path_value`

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L449-458)
L450> Resolves the absolute path starting from a normalized value.
L452> `return None`
L455> `return candidate`
L456> `return (project_base / candidate).resolve(strict=False)`

### fn `def format_substituted_path(value: str) -> str` (L459-465)
L460> Uniforms path separators for substitutions.
L462> `return ""`
L463> `return value.replace(os.sep, "/")`

### fn `def compute_sub_path(` (L466-467)

### fn `def save_config(` (L481-486)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L502-538)
L503> Loads parameters saved in .req/config.json.
L506> `raise ReqError(`
L513> `raise ReqError("Error: .req/config.json is not valid", 11) from exc`
L515> Fallback to legacy key names from pre-v0.59 config files.
L520> `raise ReqError("Error: missing or invalid 'guidelines-dir' field in .req/config.json", 11)`
L522> `raise ReqError("Error: missing or invalid 'docs-dir' field in .req/config.json", 11)`
L524> `raise ReqError("Error: missing or invalid 'tests-dir' field in .req/config.json", 11)`
L530> `raise ReqError("Error: missing or invalid 'src-dir' field in .req/config.json", 11)`
L531> `return {`

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L539-565)
L540> Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
L542> `return ""`
L554> If there are no files, use the directory itself.
L559> `return f"`{rel_str}`"`
L561> `return ""`
L563> `return ", ".join(files)`

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L566-596)
L567-571> Generates a list of relative file paths (no formatting) for printing. Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
L573> `return []`
L585> If there are no files, use the directory itself.
L590> `return [rel_str]`
L592> `return []`
L594> `return items`

### fn `def copy_guidelines_templates(` (L597-598)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L636-646)
L637> Normalizes the path token optionally preserving the trailing slash.
L639> `return ""`
L642> `return ""`
L644> `return f"{normalized}{suffix}"`

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L647-655)
L648> Validates that the path is not absolute and raises an error otherwise.
L650> `raise ReqError(`

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L656-662)
L657> Returns text with token replacements applied.
L660> `return text`

### fn `def write_text_file(dst: Path, text: str) -> None` (L663-668)
L664> Writes text to disk, ensuring the destination folder exists.

### fn `def copy_with_replacements(` (L669-670)

### fn `def normalize_description(value: str) -> str` (L678-687)
L679> Normalizes a description by removing superfluous quotes and escapes.
L685> `return trimmed.replace('\\"', '"')`

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L688-715)
L689> Converts a Markdown prompt to TOML for Gemini.
L691> `raise ReqError(`
L698> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L716-724)
L717> Extracts front matter and body from Markdown.
L720> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`
L721> Explicitly return two strings to satisfy type annotation.
L722> `return match.group(1), match.group(2)`

### fn `def extract_description(frontmatter: str) -> str` (L725-732)
L726> Extracts the description from front matter.
L729> `raise ReqError("No 'description:' field found inside the leading block.", 5)`
L730> `return normalize_description(desc_match.group(1).strip())`

### fn `def extract_argument_hint(frontmatter: str) -> str` (L733-740)
L734> Extracts the argument-hint from front matter, if present.
L737> `return ""`
L738> `return normalize_description(match.group(1).strip())`

### fn `def extract_purpose_first_bullet(body: str) -> str` (L741-760)
L742> Returns the first bullet of the Purpose section.
L750> `raise ReqError("Error: missing '## Purpose' section in prompt.", 7)`
L757> `return match.group(1).strip()`
L758> `raise ReqError("Error: no bullet found under the '## Purpose' section.", 7)`

### fn `def json_escape(value: str) -> str` (L761-765)
L762> Escapes a string for JSON without external delimiters.
L763> `return json.dumps(value)[1:-1]`

### fn `def generate_kiro_resources(` (L766-769)

### fn `def render_kiro_agent(` (L788-797)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L830-837)
L831> Replaces tokens in the specified file.

### fn `def yaml_double_quote_escape(value: str) -> str` (L838-842)
L839> Minimal escape for a double-quoted string in YAML.
L840> `return value.replace("\\", "\\\\").replace('"', '\\"')`

### fn `def find_template_source() -> Path` (L843-853)
L844> Returns the template source or raises an error.
L847> `return candidate`
L848> `raise ReqError(`

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L854-887)
L855> Loads the Kiro template from centralized models configuration.
L858> Try models.json first (this function is called during generation, not with legacy flag check)
L869> `return agent_template, kiro_cfg`
L872> `return (`
L882> `raise ReqError(`

### fn `def strip_json_comments(text: str) -> str` (L888-907)
L889> Removes // and /* */ comments to allow JSONC parsing.
L905> `return "\n".join(cleaned)`

### fn `def load_settings(path: Path) -> dict[str, Any]` (L908-918)
L909> Loads JSON/JSONC settings, removing comments when necessary.
L912> `return json.loads(raw)`
L916> `return json.loads(cleaned)`

### fn `def load_centralized_models(` (L919-922)

### fn `def get_model_tools_for_prompt(` (L970-971)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1007-1027)
L1008-1013> Returns the raw value of `usage_modes[mode]['tools']` for the prompt. Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
L1015> `return None`
L1024> `return mode_entry.get("tools")`
L1025> `return None`

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1028-1034)
L1029> Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
L1032> `return f"[{quoted}]"`

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1035-1044)
L1036> Recursively merges dictionaries, prioritizing incoming values.
L1042> `return base`

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1045-1052)
L1046> Finds the VS Code settings template if available.
L1049> `return candidate`
L1050> `return None`

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1053-1062)
L1054> Generates chat.promptFilesRecommendations from available prompts.
L1057> `return recommendations`
L1060> `return recommendations`

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1063-1071)
L1064> Verifies that the path is under the project root.
L1066> `raise ReqError(`

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1072-1080)
L1073> Saves a backup of VS Code settings if the file exists.
L1075> Never create an absence marker. Backup only if the file exists.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1081-1091)
L1082> Restores VS Code settings from backup, if present.
L1089> Do not remove the target file if no backup exists: restore behavior disabled otherwise.

### fn `def prune_empty_dirs(root: Path) -> None` (L1092-1104)
L1089> Do not remove the target file if no backup exists: restore behavior disabled otherwise.
L1093> Removes empty directories under the specified root.
L1095> `return`

### fn `def remove_generated_resources(project_base: Path) -> None` (L1105-1144)
L1106> Removes resources generated by the tool in the project root.

### fn `def run_remove(args: Namespace) -> None` (L1145-1185)
L1146> Handles the removal of generated resources.
L1152> `raise ReqError(`
L1161> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1164> `raise ReqError(`
L1169> After validation and before any removal, check for a new version.
L1172> Do not perform any restore or removal of .vscode/settings.json during removal.

### fn `def run(args: Namespace) -> None` (L1186-1385)
L1187> Handles the main initialization flow.
L1192> Main flow: validates input, calculates paths, generates resources.
L1195> `return`
L1202> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1210> `raise ReqError(`
L1215> `raise ReqError(`
L1233> `raise ReqError("Error: invalid docs configuration values", 11)`
L1235> `raise ReqError("Error: invalid tests configuration value", 11)`
L1241> `raise ReqError("Error: invalid src configuration values", 11)`
L1281> `raise ReqError("Error: --guidelines-dir must be under the project base", 8)`
L1283> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L1285> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L1288> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L1313> `raise ReqError(`
L1320> Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
L1349> `raise ReqError(`
L1354> After validation and before any operation that modifies the filesystem, check for a new version.
L1384> Copy models configuration to .req/models.json based on legacy mode (REQ-084)
L1385> Skip if --preserve-models is active

- var `VERBOSE = args.verbose` (L1189) — Handles the main initialization flow.
- var `DEBUG = args.debug` (L1190)
- var `PROMPT = prompt_path.stem` (L1523)
### fn `def _format_install_table(` `priv` (L1951-1953)
L1948> Build and print a simple installation report table describing which

### fn `def fmt(row: tuple[str, ...]) -> str` (L1973-1975)
L1974> `return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row))`

- var `EXCLUDED_DIRS = frozenset({` (L1993) — ── Excluded directories for --references and --compress ──────────────────
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2002) — ── Supported source file extensions ──────────────────────────────────────
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2010-2031)
L2007> File extensions considered during source directory scanning.
L2011-2014> Recursively collect source files from the given directories. Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
L2021> Filter out excluded directories (modifies dirnames in-place)
L2029> `return collected`

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2032-2040)
L2033> Check if the parsed args contain a standalone file command.
L2034> `return bool(`

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2041-2048)
L2042> Check if the parsed args contain a project scan command.
L2043> `return bool(`

### fn `def run_files_tokens(files: list[str]) -> None` (L2049-2066)
L2050> Execute --files-tokens: count tokens for arbitrary files.
L2061> `raise ReqError("Error: no valid files provided.", 1)`

### fn `def run_files_references(files: list[str]) -> None` (L2067-2074)
L2068> Execute --files-references: generate markdown for arbitrary files.

### fn `def run_files_compress(files: list[str]) -> None` (L2075-2082)
L2076> Execute --files-compress: compress arbitrary files.

### fn `def run_references(args: Namespace) -> None` (L2083-2094)
L2084> Execute --references: generate markdown for project source files.
L2090> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_compress_cmd(args: Namespace) -> None` (L2095-2106)
L2096> Execute --compress: compress project source files.
L2102> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L2107-2140)
L2108> Resolve project base and src-dirs for --references/--compress.
L2110> `raise ReqError(`
L2120> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L2122> Source dirs can come from args or from config
L2125> Try to load from config
L2131> `raise ReqError(`
L2136> `raise ReqError("Error: no source directories configured.", 1)`
L2138> `return project_base, src_dirs`

### fn `def main(argv: Optional[list[str]] = None) -> int` (L2141-2192)
L2142-2145> CLI entry point for console_scripts and `-m` execution. Returns an exit code (0 success, non-zero on error).
L2150> `return 0`
L2153> `return 0`
L2156> `return 0`
L2158> `return 0`
L2160> Standalone file commands (no --base/--here required)
L2168> `return 0`
L2169> Project scan commands (require --base/--here)
L2175> `return 0`
L2176> Standard init flow requires --base or --here
L2178> `raise ReqError(`
L2184> `return e.code`
L2185> Unexpected error
L2191> `return 1`
L2192> `return 0`

## Comments
- L41: Prints an informational message.
- L46: Prints a debug message if debugging is active.
- L52: Prints a verbose message if verbose mode is active.
- L58: Builds the CLI argument parser.
- L216: Parses command-line arguments into a namespace.
- L221: Reads the package version from __init__.py.
- L231: Handles --ver/--version by printing the version.
- L239: Executes the upgrade using uv.
- L261: Executes the uninstallation using uv.
- L280: Normalizes the release tag by removing a 'v' prefix if present.
- L288: Converts a version into a numeric tuple for comparison. Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
- L312: Returns True if latest is greater than current.
- L325: Checks online for a new version and prints a warning. If the call fails or the response is invalid, it prints nothing and proceeds.
- L367: Ensures the documentation directory exists under the project base.
- L383: Ensures the test directory exists under the project base.
- L399: Ensures the source directory exists under the project base.
- L415: Normalizes the path relative to the project root when possible.
- L450: Resolves the absolute path starting from a normalized value.
- L460: Uniforms path separators for substitutions.
- L469: Calculates the relative path to use in tokens.
- L488: Saves normalized parameters to .req/config.json.
- L503: Loads parameters saved in .req/config.json.
- L515: Fallback to legacy key names from pre-v0.59 config files.
- L540: Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
- L554: If there are no files, use the directory itself.
- L567: Generates a list of relative file paths (no formatting) for printing. Each entry is formatted as `guidelines/file.md` (forward slashes). If there a...
- L585: If there are no files, use the directory itself.
- L600: Copies guidelines templates from resources/guidelines/ to the target directory. Args: guidelines_dest: Target directory where templates will be cop...
- L637: Normalizes the path token optionally preserving the trailing slash.
- L648: Validates that the path is not absolute and raises an error otherwise.
- L657: Returns text with token replacements applied.
- L664: Writes text to disk, ensuring the destination folder exists.
- L672: Copies a file substituting the indicated tokens with their values.
- L679: Normalizes a description by removing superfluous quotes and escapes.
- L689: Converts a Markdown prompt to TOML for Gemini.
- L717: Extracts front matter and body from Markdown.
- L721: Explicitly return two strings to satisfy type annotation.
- L726: Extracts the description from front matter.
- L734: Extracts the argument-hint from front matter, if present.
- L742: Returns the first bullet of the Purpose section.
- L762: Escapes a string for JSON without external delimiters.
- L771: Generates the resource list for the Kiro agent.
- L799: Renders the Kiro agent JSON and populates main fields.
- L826: If parsing fails, return raw template to preserve previous behavior
- L831: Replaces tokens in the specified file.
- L839: Minimal escape for a double-quoted string in YAML.
- L844: Returns the template source or raises an error.
- L855: Loads the Kiro template from centralized models configuration.
- L858: Try models.json first (this function is called during generation, not with legacy flag check)
- L889: Removes // and /* */ comments to allow JSONC parsing.
- L909: Loads JSON/JSONC settings, removing comments when necessary.
- L924: Loads centralized models configuration from common/models.json. Returns a map cli_name -> parsed_json or None if not present. When preserve_models_...
- L934: Priority 1: preserve_models_path if provided and exists
- L938: Priority 2: legacy mode
- L945: Fallback: standard models.json
- L952: Load the centralized configuration
- L960: Extract individual CLI configs
- L973: Extracts model and tools for the prompt from the CLI config. Returns (model, tools) where each value can be None if not available.
- L990-991: Use the unified key name 'tools' across all CLI configs. | Accept either a list of strings or a CSV string in the config.json.
- L999: Parse comma-separated string into list
- L1008: Returns the raw value of `usage_modes[mode]['tools']` for the prompt. Can return a list of strings, a string, or None depending on how it is define...
- L1029: Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
- L1036: Recursively merges dictionaries, prioritizing incoming values.
- L1046: Finds the VS Code settings template if available.
- L1054: Generates chat.promptFilesRecommendations from available prompts.
- L1064: Verifies that the path is under the project root.
- L1073-1075: Saves a backup of VS Code settings if the file exists. | Never create an absence marker. Backup only if the file exists.
- L1082: Restores VS Code settings from backup, if present.
- L1093: Removes empty directories under the specified root.
- L1106: Removes resources generated by the tool in the project root.
- L1146: Handles the removal of generated resources.
- L1169: After validation and before any removal, check for a new version.
- L1172: Do not perform any restore or removal of .vscode/settings.json during removal.
- L1192: Main flow: validates input, calculates paths, generates resources.
- L1320: Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
- L1354: After validation and before any operation that modifies the filesystem, check for a new version.
- L1384-1385: Copy models configuration to .req/models.json based on legacy mode (REQ-084) | Skip if --preserve-models is active
- L1409: Create requirements.md only if the --docs-dir folder is empty.
- L1419: Generate the file list for the %%GUIDELINES_FILES%% token.
- L1488: Load CLI configs only if requested to include model/tools
- L1499: Determine preserve_models_path (REQ-082)
- L1530: (Removed: bootstrap file inlining and YOLO stop/approval substitution)
- L1546: Precompute description and Claude metadata so provider blocks can reuse them safely.
- L1556: .codex/prompts
- L1565: .codex/skills/req/<prompt>/SKILL.md
- L1595: Gemini TOML
- L1633: .kiro/prompts
- L1643: .claude/agents
- L1669: .github/agents
- L1697: .github/prompts
- L1729: .kiro/agents
- L1759: .opencode/agent
- L1790: .opencode/command
- L1835: .claude/commands/req
- L1893: Load existing settings (if present) and those from the template.
- L1899: If checking/loading fails, consider it empty
- L1904: Merge without modifying original until sure.
- L1914: If final result is identical to existing, do not rewrite nor backup.
- L1919: If changes are expected, create backup only if file exists.
- L1922: Write final settings.
- L1930-1931: Final success notification: printed only when the command completed all | intended filesystem modifications without raising an exception.
- L1938-1939: Print the discovered directories used for token substitutions | as required by REQ-078: one item per line prefixed with '- '.
- L1955: Format the installation summary table aligning header, prompts, and rows.
- L1998: Directories excluded from source scanning in --references and --compress.
- L2011: Recursively collect source files from the given directories. Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
- L2021: Filter out excluded directories (modifies dirnames in-place)
- L2033: Check if the parsed args contain a standalone file command.
- L2042: Check if the parsed args contain a project scan command.
- L2050: Execute --files-tokens: count tokens for arbitrary files.
- L2068: Execute --files-references: generate markdown for arbitrary files.
- L2076: Execute --files-compress: compress arbitrary files.
- L2084: Execute --references: generate markdown for project source files.
- L2096: Execute --compress: compress project source files.
- L2108: Resolve project base and src-dirs for --references/--compress.
- L2122: Source dirs can come from args or from config
- L2125: Try to load from config
- L2142: CLI entry point for console_scripts and `-m` execution. Returns an exit code (0 success, non-zero on error).
- L2160: Standalone file commands (no --base/--here required)
- L2169: Project scan commands (require --base/--here)
- L2176: Standard init flow requires --base or --here

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|18||
|`RESOURCE_ROOT`|var|pub|21||
|`VERBOSE`|var|pub|24||
|`DEBUG`|var|pub|27||
|`ReqError`|class|pub|31-39|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|34-39|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|40-44|def log(msg: str) -> None|
|`dlog`|fn|pub|45-50|def dlog(msg: str) -> None|
|`vlog`|fn|pub|51-56|def vlog(msg: str) -> None|
|`build_parser`|fn|pub|57-214|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|215-219|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|220-229|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|230-237|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|238-259|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|260-278|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|279-286|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|287-310|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|311-323|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|324-365|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|366-381|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|382-397|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|398-413|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|414-448|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|449-458|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|459-465|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|466-467|def compute_sub_path(|
|`save_config`|fn|pub|481-486|def save_config(|
|`load_config`|fn|pub|502-538|def load_config(project_base: Path) -> dict[str, str | li...|
|`generate_guidelines_file_list`|fn|pub|539-565|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|566-596|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`copy_guidelines_templates`|fn|pub|597-598|def copy_guidelines_templates(|
|`make_relative_token`|fn|pub|636-646|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|647-655|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|656-662|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|663-668|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|669-670|def copy_with_replacements(|
|`normalize_description`|fn|pub|678-687|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|688-715|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|716-724|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|725-732|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|733-740|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|741-760|def extract_purpose_first_bullet(body: str) -> str|
|`json_escape`|fn|pub|761-765|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|766-769|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|788-797|def render_kiro_agent(|
|`replace_tokens`|fn|pub|830-837|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|838-842|def yaml_double_quote_escape(value: str) -> str|
|`find_template_source`|fn|pub|843-853|def find_template_source() -> Path|
|`load_kiro_template`|fn|pub|854-887|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|888-907|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|908-918|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|919-922|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|970-971|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1007-1027|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1028-1034|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1035-1044|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1045-1052|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1053-1062|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1063-1071|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1072-1080|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1081-1091|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1092-1104|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1105-1144|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1145-1185|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1186-1385|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1189||
|`DEBUG`|var|pub|1190||
|`PROMPT`|var|pub|1523||
|`_format_install_table`|fn|priv|1951-1953|def _format_install_table(|
|`fmt`|fn|pub|1973-1975|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|1993||
|`SUPPORTED_EXTENSIONS`|var|pub|2002||
|`_collect_source_files`|fn|priv|2010-2031|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_is_standalone_command`|fn|priv|2032-2040|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2041-2048|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2049-2066|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2067-2074|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2075-2082|def run_files_compress(files: list[str]) -> None|
|`run_references`|fn|pub|2083-2094|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2095-2106|def run_compress_cmd(args: Namespace) -> None|
|`_resolve_project_src_dirs`|fn|priv|2107-2140|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|2141-2192|def main(argv: Optional[list[str]] = None) -> int|


---

# compress.py | Python | 371L | 11 symbols | 5 imports | 35 comments
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
- var `INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}` (L40) — Languages where indentation is semantically significant
### fn `def _get_specs()` `priv` (L45-51)
L49> `return _specs_cache`

### fn `def detect_language(filepath: str) -> str | None` (L52-56)
L54> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L57-92)
L58> Check if position `pos` in `line` is inside a string literal.
L65> Check for escaped delimiter (single-char only)
L67> Count consecutive backslashes
L90> `return in_string is not None`

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L93-130)
L95> Remove trailing single-line comment from a code line.
L97> `return line`
L120> `return line[:i]`
L128> `return line`

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L131-139)
L132> Check if a line is a standalone Python docstring (triple-quote only).
L136> `return True`
L137> `return False`

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L140-147)
L142> Format compressed entries, optionally prefixing original line numbers.
L144> `return '\n'.join(text for _, text in entries)`
L145> `return '\n'.join(f"L{lineno}> {text}" for lineno, text in entries)`

### fn `def compress_source(source: str, language: str,` (L148-319)
L150-161> Compress source code by removing comments, blank lines, and extra whitespace. Preserves indentation for indent-significant languages (Python, Haskell, Elixir). Args: source: The source code string. language: Language identifier (e.g. "python", "javascript"). include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Compressed source code string.
L165> `raise ValueError(f"Unsupported language: {language}")`
L170> list of (original_line_number, text)
L177> Python: also handle ''' as multi-comment
L186> --- Handle multi-line comment continuation ---
L189> End of multi-line comment found
L193> Process remainder as a new line
L200-226> --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docstring: if python_docstring_delim in line: end_pos = line.index(python_docstring_delim) + 3 remainder = line[end_pos:] in_python_docstring = False python_docstring_delim = None if remainder.strip(): lines[i] = remainder continue i += 1 continue stripped = line.strip() Skip empty lines if not stripped: i += 1 continue --- Detect multi-line comment start --- if mc_start: For Python, triple-quotes can be strings or docstrings. We only strip standalone docstrings (line starts with triple-quote after optional whitespace). if is_python: for q in ('"""', "'''"):
L228> Single-line docstring: """...
L230> Check it's not a variable assignment like x = """...
L234> Standalone docstring or assigned — skip if standalone
L238> If code before and not assignment, keep line
L240> Multi-line docstring start
L251> Non-Python: check for multi-line comment start
L254> Check if inside a string
L257> Check for same-line close
L261> Single-line block comment: remove it
L268> Re-process this reconstructed line
L272> Multi-line comment starts here
L281> --- Full-line single-line comment ---
L283> Special: keep shebangs
L289> --- Remove inline comment ---
L293> --- Clean whitespace ---
L295> Keep leading whitespace, strip trailing
L301> Collapse internal multiple spaces (but not in strings)
L309> Remove trailing whitespace
L317> `return _format_result(result, include_line_numbers)`

### fn `def compress_file(filepath: str, language: str | None = None,` (L320-344)
L322-331> Compress a source file by removing comments and extra whitespace. Args: filepath: Path to the source file. language: Optional language override. Auto-detected if None. include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Compressed source code string.
L335> `raise ValueError(`
L342> `return compress_source(source, language, include_line_numbers)`

### fn `def main()` (L345-369)
L359> `sys.exit(1)`
L367> `sys.exit(1)`

## Comments
- L2: compress.py - Source code compressor for LLM context optimization. Parses a source file and removes all comments (inline, single-line, ...
- L58: Check if position `pos` in `line` is inside a string literal.
- L65-67: Check for escaped delimiter (single-char only) | Count consecutive backslashes
- L95: Remove trailing single-line comment from a code line.
- L132: Check if a line is a standalone Python docstring (triple-quote only).
- L142: Format compressed entries, optionally prefixing original line numbers.
- L150: Compress source code by removing comments, blank lines, and extra whitespace. Preserves indentation for indent-significant languages (Python, Haske...
- L177: Python: also handle ''' as multi-comment
- L186: --- Handle multi-line comment continuation ---
- L189: End of multi-line comment found
- L193: Process remainder as a new line
- L200-230: --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docs... | Single-line docstring: """... | Check it's not a variable assignment like x = """...
- L234: Standalone docstring or assigned — skip if standalone
- L238-240: If code before and not assignment, keep line | Multi-line docstring start
- L251: Non-Python: check for multi-line comment start
- L254: Check if inside a string
- L257: Check for same-line close
- L261: Single-line block comment: remove it
- L268: Re-process this reconstructed line
- L272: Multi-line comment starts here
- L281-283: --- Full-line single-line comment --- | Special: keep shebangs
- L289: --- Remove inline comment ---
- L293-295: --- Clean whitespace --- | Keep leading whitespace, strip trailing
- L301: Collapse internal multiple spaces (but not in strings)
- L309: Remove trailing whitespace
- L322: Compress a source file by removing comments and extra whitespace. Args: filepath: Path to the source file. ...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|29||
|`INDENT_SIGNIFICANT`|var|pub|40||
|`_get_specs`|fn|priv|45-51|def _get_specs()|
|`detect_language`|fn|pub|52-56|def detect_language(filepath: str) -> str | None|
|`_is_in_string`|fn|priv|57-92|def _is_in_string(line: str, pos: int, string_delimiters:...|
|`_remove_inline_comment`|fn|priv|93-130|def _remove_inline_comment(line: str, single_comment: str,|
|`_is_python_docstring_line`|fn|priv|131-139|def _is_python_docstring_line(line: str) -> bool|
|`_format_result`|fn|priv|140-147|def _format_result(entries: list[tuple[int, str]],|
|`compress_source`|fn|pub|148-319|def compress_source(source: str, language: str,|
|`compress_file`|fn|pub|320-344|def compress_file(filepath: str, language: str | None = N...|
|`main`|fn|pub|345-369|def main()|


---

# compress_files.py | Python | 94L | 2 symbols | 4 imports | 3 comments
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

### fn `def main()` (L75-92)
L90> `sys.exit(1)`

## Comments
- L2: compress_files.py - Compress and concatenate multiple source files. Uses the compress module to strip comments and whitespace from each input ...
- L26: Compress multiple source files and concatenate with identifying headers. Each file is compressed and prefixed with a header line: @@@ <path> | <lan...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`compress_files`|fn|pub|24-74|def compress_files(filepaths: list[str],|
|`main`|fn|pub|75-92|def main()|


---

# generate_markdown.py | Python | 126L | 4 symbols | 3 imports | 5 comments
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
### fn `def detect_language(filepath: str) -> str | None` (L49-54)
L50> Detect language from file extension.
L52> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def generate_markdown(filepaths: list[str]) -> str` (L55-110)
L56-66> Analyze source files and return concatenated markdown. Args: filepaths: List of source file paths to analyze. Returns: Concatenated markdown string with all file analyses. Raises: ValueError: If no valid source files are found.
L103> `raise ValueError("No valid source files processed")`
L108> `return "\n\n---\n\n".join(md_parts)`

### fn `def main()` (L111-124)
L115> `sys.exit(1)`
L122> `sys.exit(1)`

## Comments
- L2: generate_markdown.py - Generate concatenated markdown from arbitrary source files. Analyzes each input file with source_analyzer and produces a sin...
- L50: Detect language from file extension.
- L56: Analyze source files and return concatenated markdown. Args: filepaths: List of source file paths to analyze. ...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|23||
|`detect_language`|fn|pub|49-54|def detect_language(filepath: str) -> str | None|
|`generate_markdown`|fn|pub|55-110|def generate_markdown(filepaths: list[str]) -> str|
|`main`|fn|pub|111-124|def main()|


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

# source_analyzer.py | Python | 2015L | 56 symbols | 7 imports | 127 comments
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

### class `class SourceElement` `@dataclass` (L59-105)
L60> Element found in source file.
- fn `def type_label(self) -> str` (L75-105)
  L103> `return labels.get(self.element_type, "UNKNOWN")`

### class `class LanguageSpec` `@dataclass` (L107-116)
L108> Language recognition pattern specification.

### fn `def build_language_specs() -> dict` (L117-316)
L118> Build specifications for all supported languages.
L121> ── Python ──────────────────────────────────────────────────────────
L142> ── C ───────────────────────────────────────────────────────────────
L176> ── C++ ─────────────────────────────────────────────────────────────
L206> ── Rust ────────────────────────────────────────────────────────────
L238> ── JavaScript ──────────────────────────────────────────────────────
L266> ── TypeScript ──────────────────────────────────────────────────────
L299> ── Java ────────────────────────────────────────────────────────────

### class `class SourceAnalyzer` (L669-868)
L868> Find position of single-line comment, ignoring strings.
- fn `def __init__(self)` `priv` (L677-679) L670> Multi-language source file analyzer. Analyzes a source file identifying definitions, comments and...
- fn `def get_supported_languages(self) -> list` (L680-689)
  L681> Return list of supported languages (without aliases).
  L688> `return sorted(result)`
- fn `def analyze(self, filepath: str, language: str) -> list` (L690-837)
  L691> Analyze a source file and return the list of SourceElement found.
  L694> `raise ValueError(`
  L706> Multi-line comment state
  L714> ── Multi-line comment handling ──────────────────────────
  L731> ── Multi-line comment start ────────────────────────────
  L733> Special handling for Python docstrings and =begin/=pod blocks
  L737> Check not inside a string
  L739> Check if multi-line comment closes on same line
  L751> Python: """ ... """ sulla stessa riga
  L768> ── Single-line comment ───────────────────────────────────
  L772> If comment is the entire line (aside from whitespace)
  L783> Inline comment: add both element and comment
  L793> ── Language patterns ─────────────────────────────────────
  L806> Single-line types: don't search for block
  L823> Limit extract to max 5 lines for readability
  L836> `return elements`
- fn `def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool` `priv` (L838-866)
  L839> Check if position pos is inside a string literal.
  L865> `return in_string`

### fn `def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]` `priv` (L867-900)
L868> Find position of single-line comment, ignoring strings.
L870> `return None`
L887> `return i`
L899> `return None`

### fn `def _find_block_end(self, lines: list, start_idx: int,` `priv` (L901-976)
L903-907> Find the end of a block (function, class, struct, etc.). Returns the index (1-based) of the final line of the block. Limits search for performance.
L908> Per Python: basato sull'indentazione
L921> `return end`
L923> Per linguaggi con parentesi graffe
L940> `return end + 1`
L942> If no opening braces found, return just the first line
L944> `return start_idx + 1`
L945> `return end`
L947> Per Ruby/Elixir/Lua: basato su end keyword
L956> `return end + 1`
L958> `return start_idx + 1`
L960> Per Haskell: basato sull'indentazione
L973> `return end`
L975> `return start_idx + 1`

### fn `def enrich(self, elements: list, language: str,` (L979-996)
L977> ── Enrichment methods for LLM-optimized output ───────────────────
L981-986> Enrich elements with signatures, hierarchy, visibility, inheritance. Call after analyze() to add metadata for LLM-optimized markdown output. Modifies elements in-place and returns them. If filepath is provided, also extracts body comments and exit points.
L995> `return elements`

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L997-1025)
L998-1003> Extract clean identifiers from name fields. Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.
L1008> Try to re-extract the name from the element's extract line
L1009> using the original pattern (which has group 2 as the identifier)
L1017> Take highest non-None non-empty group
L1018> (group 2+ = identifier, group 1 = full match)

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1026-1040)
L1027> Extract clean signatures from element extracts.

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1041-1076)
L1042-1046> Detect parent-child relationships between elements. Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1077-1088)
L1078> Extract visibility/access modifiers from elements.

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1089-1133)
L1091> Parse visibility modifier from a signature line.
L1094> `return "priv"`
L1096> `return "priv"`
L1097> `return "pub"`
L1100> `return "pub"`
L1102> `return "priv"`
L1104> `return "prot"`
L1106> `return "int"`
L1107> `return None`
L1110> `return "pub"`
L1111> `return "priv"`
L1114> `return "pub"`
L1115> `return "priv"`
L1118> `return "priv"`
L1120> `return "fpriv"`
L1122> `return "pub"`
L1123> `return None`
L1126> `return "pub"`
L1128> `return "priv"`
L1130> `return "prot"`
L1131> `return None`
L1132> `return None`

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1134-1144)
L1135> Extract inheritance/implementation info from class-like elements.

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1145-1173)
L1147> Parse inheritance info from a class/struct declaration line.
L1150> `return m.group(1).strip() if m else None`
L1159> `return ", ".join(parts) if parts else None`
L1163> `return m.group(1).strip() if m else None`
L1168> `return m.group(1).strip() if m else None`
L1171> `return m.group(1) if m else None`
L1172> `return None`

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1181-1310)
L1183-1191> Extract comments and exit points from within function/class bodies. Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.
L1194> `return`
L1200> `return`
L1202> Only process definitions that span multiple lines
L1220> Scan the body (lines after the definition line)
L1221> 1-based, skip def line itself
L1235> Multi-line comment tracking within body
L1250> Check for multi-line comment start
L1255> Single-line multi-comment
L1279> Single-line comment (full line)
L1289> Standalone comment line in body
L1295> Inline comment after code
L1300> Exit points

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1312-1322)
L1313> Strip comment markers from a single line of comment text.
L1320> `return s`

### fn `def format_output(elements: list, filepath: str, language: str,` (L1323-1442)
L1325> Format structured analysis output.
L1335> ── Definitions section ────────────────────────────────────────────
L1359> Prefix with line number
L1369> ── Comments section ───────────────────────────────────────────────
L1402> ── Complete structured listing ────────────────────────────────────
L1409> Sort by start line
L1427> Show first line of extract
L1440> `return "\n".join(output_lines)`

### fn `def _md_loc(elem) -> str` `priv` (L1443-1449)
L1444> Format element location compactly for markdown.
L1446> `return f"L{elem.line_start}"`
L1447> `return f"L{elem.line_start}-{elem.line_end}"`

### fn `def _md_kind(elem) -> str` `priv` (L1450-1477)
L1451> Short kind label for markdown output.
L1475> `return mapping.get(elem.element_type, "?")`

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1478-1503)
L1479-1484> Extract clean text content from a comment element. Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.
L1489> Strip comment markers
L1494> Strip multi-line markers
L1501> `return text`

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1504-1519)
L1505> Extract clean text lines from a multi-line comment (preserving structure).
L1517> `return cleaned`

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1520-1585)
L1521-1528> Build maps that associate comments with their adjacent definitions. Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)
L1531> Identify definition elements
L1539> Build adjacency map: comments preceding a definition (within 2 lines)
L1548> Extract file description from first comment(s), skip shebangs
L1553> Skip shebang lines and empty comments
L1561> Skip inline comments (name == "inline")
L1566> Check if this comment precedes a definition within 2 lines
L1573> Stop if we hit another element
L1578> Skip file-level description (already captured)
L1583> `return doc_for_def, standalone_comments, file_description`

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1586-1641)
L1588-1594> Render body comments and exit points for a definition element. Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.
L1595> Build maps by line number
L1604> Collect all annotated line numbers
L1608> Skip if within an excluded range (child element)
L1622> Merge: show exit point code with comment as context
L1625> Strip inline comment from exit_text if it contains it

### fn `def format_markdown(elements: list, filepath: str, language: str,` (L1642-1841)
L1644-1654> Format analysis as compact Markdown optimized for LLM agent consumption. Produces token-efficient output with: - File header with language, line count, element summary, and description - Imports in a code block - Hierarchical definitions with line-numbered doc comments - Body comments (L<N>> text) and exit points (L<N>> `return ...`) - Comments grouped with their relevant definitions - Standalone section/region comments preserved as context - Symbol index table for quick reference by line number
L1663> Build comment association maps
L1666> ── Header ────────────────────────────────────────────────────────
L1678> ── Imports ───────────────────────────────────────────────────────
L1691> ── Build decorator map: line -> decorator text ───────────────────
L1697> ── Definitions ───────────────────────────────────────────────────
L1737> Collect associated doc comments for this definition
L1760> For impl blocks, use the full first line as sig
L1768> Show associated doc comment with line number
L1778> Body annotations: comments and exit points
L1779> For containers with children, exclude annotations
L1780> that fall within a child's line range (including
L1781> doc comments that immediately precede the child)
L1786> Extend range to include preceding doc comment
L1795> Children with their doc comments and body annotations
L1817> Child body annotations (indented)
L1823> ── Standalone Comments (section/region markers, TODOs, notes) ────
L1826> Group consecutive comments (within 2 lines of each other)

### fn `def main()` (L1897-2013)
L1962> `sys.exit(0)`
L1968> `sys.exit(1)`
L1971> `sys.exit(1)`
L1973> Optional filtering

## Comments
- L2: source_analyzer.py - Multi-language source code analyzer. Inspired by tree-sitter, this module analyzes source files across multiple ...
- L60: Element found in source file.
- L108: Language recognition pattern specification.
- L118: Build specifications for all supported languages.
- L121: ── Python ──────────────────────────────────────────────────────────
- L142: ── C ───────────────────────────────────────────────────────────────
- L176: ── C++ ─────────────────────────────────────────────────────────────
- L206: ── Rust ────────────────────────────────────────────────────────────
- L238: ── JavaScript ──────────────────────────────────────────────────────
- L266: ── TypeScript ──────────────────────────────────────────────────────
- L299: ── Java ────────────────────────────────────────────────────────────
- L331: ── Go ──────────────────────────────────────────────────────────────
- L358: ── Ruby ────────────────────────────────────────────────────────────
- L380: ── PHP ─────────────────────────────────────────────────────────────
- L404: ── Swift ───────────────────────────────────────────────────────────
- L434: ── Kotlin ──────────────────────────────────────────────────────────
- L463: ── Scala ───────────────────────────────────────────────────────────
- L489: ── Lua ─────────────────────────────────────────────────────────────
- L505: ── Shell (Bash) ────────────────────────────────────────────────────
- L525: ── Perl ────────────────────────────────────────────────────────────
- L543: ── Haskell ─────────────────────────────────────────────────────────
- L565: ── Zig ─────────────────────────────────────────────────────────────
- L589: ── Elixir ──────────────────────────────────────────────────────────
- L611: ── C# ──────────────────────────────────────────────────────────────
- L650: Common aliases
- L681: Return list of supported languages (without aliases).
- L691: Analyze a source file and return the list of SourceElement found.
- L706: Multi-line comment state
- L714: ── Multi-line comment handling ──────────────────────────
- L731-733: ── Multi-line comment start ──────────────────────────── | Special handling for Python docstrings and =begin/=pod blocks
- L737-739: Check not inside a string | Check if multi-line comment closes on same line
- L751: Python: """ ... """ sulla stessa riga
- L768: ── Single-line comment ───────────────────────────────────
- L772: If comment is the entire line (aside from whitespace)
- L783: Inline comment: add both element and comment
- L793: ── Language patterns ─────────────────────────────────────
- L806: Single-line types: don't search for block
- L823: Limit extract to max 5 lines for readability
- L839: Check if position pos is inside a string literal.
- L868: Find position of single-line comment, ignoring strings.
- L903-908: Find the end of a block (function, class, struct, etc.). Returns the index (1-based) of the final... | Per Python: basato sull'indentazione
- L923: Per linguaggi con parentesi graffe
- L942: If no opening braces found, return just the first line
- L947: Per Ruby/Elixir/Lua: basato su end keyword
- L960: Per Haskell: basato sull'indentazione
- L981: Enrich elements with signatures, hierarchy, visibility, inheritance. Call after analyze() to add metadata for LLM-optimized markdown output. Modifi...
- L998: Extract clean identifiers from name fields. Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead o...
- L1008-1009: Try to re-extract the name from the element's extract line | using the original pattern (which has group 2 as the identifier)
- L1017-1018: Take highest non-None non-empty group | (group 2+ = identifier, group 1 = full match)
- L1027: Extract clean signatures from element extracts.
- L1042: Detect parent-child relationships between elements. Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside conta...
- L1078: Extract visibility/access modifiers from elements.
- L1091: Parse visibility modifier from a signature line.
- L1135: Extract inheritance/implementation info from class-like elements.
- L1147: Parse inheritance info from a class/struct declaration line.
- L1174: ── Exit point patterns per language family ──────────────────────
- L1183: Extract comments and exit points from within function/class bodies. Reads the source file and scans each definition's line range for: - Single-line...
- L1202: Only process definitions that span multiple lines
- L1220: Scan the body (lines after the definition line)
- L1235: Multi-line comment tracking within body
- L1250: Check for multi-line comment start
- L1255: Single-line multi-comment
- L1279: Single-line comment (full line)
- L1289: Standalone comment line in body
- L1295: Inline comment after code
- L1300: Exit points
- L1313: Strip comment markers from a single line of comment text.
- L1325: Format structured analysis output.
- L1335: ── Definitions section ────────────────────────────────────────────
- L1359: Prefix with line number
- L1369: ── Comments section ───────────────────────────────────────────────
- L1402: ── Complete structured listing ────────────────────────────────────
- L1409: Sort by start line
- L1427: Show first line of extract
- L1444: Format element location compactly for markdown.
- L1451: Short kind label for markdown output.
- L1479: Extract clean text content from a comment element. Args: comment_elem: SourceElement with comment content ...
- L1489: Strip comment markers
- L1494: Strip multi-line markers
- L1505: Extract clean text lines from a multi-line comment (preserving structure).
- L1521: Build maps that associate comments with their adjacent definitions. Returns: - doc_for_def: dict mapping def line_start -> list of comment texts ...
- L1531: Identify definition elements
- L1539: Build adjacency map: comments preceding a definition (within 2 lines)
- L1548: Extract file description from first comment(s), skip shebangs
- L1553: Skip shebang lines and empty comments
- L1561: Skip inline comments (name == "inline")
- L1566: Check if this comment precedes a definition within 2 lines
- L1573: Stop if we hit another element
- L1578: Skip file-level description (already captured)
- L1588-1595: Render body comments and exit points for a definition element. Merges body_comments and exit_poin... | Build maps by line number
- L1604: Collect all annotated line numbers
- L1608: Skip if within an excluded range (child element)
- L1622: Merge: show exit point code with comment as context
- L1625: Strip inline comment from exit_text if it contains it
- L1644: Format analysis as compact Markdown optimized for LLM agent consumption. Produces token-efficient output with: - File header with language, line co...
- L1663: Build comment association maps
- L1666: ── Header ────────────────────────────────────────────────────────
- L1678: ── Imports ───────────────────────────────────────────────────────
- L1691: ── Build decorator map: line -> decorator text ───────────────────
- L1697: ── Definitions ───────────────────────────────────────────────────
- L1737: Collect associated doc comments for this definition
- L1760: For impl blocks, use the full first line as sig
- L1768: Show associated doc comment with line number
- L1778-1781: Body annotations: comments and exit points | For containers with children, exclude annotations | that fall within a child's line range (including | doc comments that immediately precede the child)
- L1786: Extend range to include preceding doc comment
- L1795: Children with their doc comments and body annotations
- L1817: Child body annotations (indented)
- L1823: ── Standalone Comments (section/region markers, TODOs, notes) ────
- L1826: Group consecutive comments (within 2 lines of each other)
- L1845: Multi-line comment block: show as region
- L1858: ── Symbol Index ──────────────────────────────────────────────────
- L1878-1879: Only show sig for functions/methods/classes (not vars/consts | which already show full content in Definitions section)
- L1973: Optional filtering

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
|`SourceElement`|class|pub|59-105|class SourceElement|
|`SourceElement.type_label`|fn|pub|75-105|def type_label(self) -> str|
|`LanguageSpec`|class|pub|107-116|class LanguageSpec|
|`build_language_specs`|fn|pub|117-316|def build_language_specs() -> dict|
|`SourceAnalyzer`|class|pub|669-868|class SourceAnalyzer|
|`SourceAnalyzer.__init__`|fn|priv|677-679|def __init__(self)|
|`SourceAnalyzer.get_supported_languages`|fn|pub|680-689|def get_supported_languages(self) -> list|
|`SourceAnalyzer.analyze`|fn|pub|690-837|def analyze(self, filepath: str, language: str) -> list|
|`SourceAnalyzer._in_string_context`|fn|priv|838-866|def _in_string_context(self, line: str, pos: int, spec: L...|
|`_find_comment`|fn|priv|867-900|def _find_comment(self, line: str, spec: LanguageSpec) ->...|
|`_find_block_end`|fn|priv|901-976|def _find_block_end(self, lines: list, start_idx: int,|
|`enrich`|fn|pub|979-996|def enrich(self, elements: list, language: str,|
|`_clean_names`|fn|priv|997-1025|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1026-1040|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1041-1076|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1077-1088|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1089-1133|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1134-1144|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1145-1173|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1181-1310|def _extract_body_annotations(self, elements: list,|
|`_clean_comment_line`|fn|priv|1312-1322|def _clean_comment_line(text: str, spec) -> str|
|`format_output`|fn|pub|1323-1442|def format_output(elements: list, filepath: str, language...|
|`_md_loc`|fn|priv|1443-1449|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1450-1477|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1478-1503|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1504-1519|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1520-1585|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1586-1641|def _render_body_annotations(out: list, elem, indent: str...|
|`format_markdown`|fn|pub|1642-1841|def format_markdown(elements: list, filepath: str, langua...|
|`main`|fn|pub|1897-2013|def main()|


---

# token_counter.py | Python | 104L | 7 symbols | 2 imports | 7 comments
> Path: `/home/ogekuri/useReq/src/usereq/token_counter.py`
> token_counter.py - Token and character counting for generated output. Uses tiktoken for accurate token counting compatible with ...

## Imports
```
import os
import tiktoken
```

## Definitions

### class `class TokenCounter` (L13-31)
- fn `def __init__(self, encoding_name: str = "cl100k_base")` `priv` (L16-18) L14> Count tokens using tiktoken encoding (cl100k_base by default).
- fn `def count_tokens(self, content: str) -> int` (L19-25)
  L20> Count tokens in content string.
  L22> `return len(self.encoding.encode(content, disallowed_special=()))`
  L24> `return 0`
- fn `def count_chars(content: str) -> int` (L27-31)
  L28> Count characters in content string.
  L29> `return len(content)`

### fn `def count_file_metrics(content: str,` (L32-44)
L34-37> Count tokens and chars for a content string. Returns dict with 'tokens' and 'chars' keys.
L39> `return {`

### fn `def count_files_metrics(file_paths: list,` (L45-72)
L47-51> Count tokens and chars for a list of files. Returns a list of dicts with 'file', 'tokens', 'chars' keys. Errors are reported with tokens=0, chars=0, and an 'error' key.
L70> `return results`

### fn `def format_pack_summary(results: list) -> str` (L73-104)
L74-81> Format a pack summary string from a list of file metrics. Args: results: list of dicts from count_files_metrics(). Returns: Formatted summary string with per-file details and totals.
L104> `return "\n".join(lines)`

## Comments
- L20: Count tokens in content string.
- L28: Count characters in content string.
- L34: Count tokens and chars for a content string. Returns dict with 'tokens' and 'chars' keys.
- L47: Count tokens and chars for a list of files. Returns a list of dicts with 'file', 'tokens', 'chars' keys. Errors are reported with tokens=0, chars=0...
- L74: Format a pack summary string from a list of file metrics. Args: results: list of dicts from count_files_metrics(). ...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`TokenCounter`|class|pub|13-31|class TokenCounter|
|`TokenCounter.__init__`|fn|priv|16-18|def __init__(self, encoding_name: str = "cl100k_base")|
|`TokenCounter.count_tokens`|fn|pub|19-25|def count_tokens(self, content: str) -> int|
|`TokenCounter.count_chars`|fn|pub|27-31|def count_chars(content: str) -> int|
|`count_file_metrics`|fn|pub|32-44|def count_file_metrics(content: str,|
|`count_files_metrics`|fn|pub|45-72|def count_files_metrics(file_paths: list,|
|`format_pack_summary`|fn|pub|73-104|def format_pack_summary(results: list) -> str|

