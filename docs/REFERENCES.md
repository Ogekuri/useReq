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

# __init__.py | Python | 27L | 0 symbols | 9 imports | 3 comments
> Path: `/home/ogekuri/useReq/src/usereq/__init__.py`
> ! @file __init__.py @brief Initialization module for the `usereq` package. @details Exposes the package version, main entry point, and key submodules. Designed to be lightweight. ...

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
- L10: ! @brief Semantic version string of the package.
- L27: ! @brief List of public symbols exported by the package.


---

# __main__.py | Python | 17L | 0 symbols | 2 imports | 2 comments
> Path: `/home/ogekuri/useReq/src/usereq/__main__.py`
> ! @file __main__.py @brief Package entry point for execution as a module. @details Enables running the package via `python -m usereq`. Delegates execution to the CLI main function. ...

## Imports
```
from .cli import main
import sys
```

## Comments
- L13: ! @brief Entry point check. @details Executes `main()` and exits with the returned status code when run as a script.


---

# cli.py | Python | 2537L | 94 symbols | 23 imports | 149 comments
> Path: `/home/ogekuri/useReq/src/usereq/cli.py`
> ! @file cli.py @brief CLI entry point implementing the useReq initialization flow. @details Handles argument parsing, configuration management, and execution of useReq commands. ...

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

- var `REPO_ROOT = Path(__file__).resolve().parents[2]` (L24)
- var `RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"` (L27) — ! @brief The absolute path to the repository root.
- var `VERBOSE = False` (L30) — ! @brief The absolute path to the resources directory.
- var `DEBUG = False` (L33) — ! @brief Whether verbose output is enabled.
- var `REQUIREMENTS_TEMPLATE_NAME = "Requirements_Template.md"` (L36) — ! @brief Whether debug output is enabled.
### class `class ReqError(Exception)` : Exception (L40-54)
L37> ! @brief Name of the packaged requirements template file.
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L45-54) L41> ! @brief Dedicated exception for expected CLI errors. @details This exception is used to bubble u...
  L46-49> ! @brief Initialize an expected CLI failure payload. @param message Human-readable error message. @param code Process exit code bound to the failure category.

### fn `def log(msg: str) -> None` (L55-61)
L56-58> ! @brief Prints an informational message. @param msg The message string to print.

### fn `def dlog(msg: str) -> None` (L62-69)
L63-65> ! @brief Prints a debug message if debugging is active. @param msg The debug message string to print.

### fn `def vlog(msg: str) -> None` (L70-77)
L71-73> ! @brief Prints a verbose message if verbose mode is active. @param msg The verbose message string to print.

### fn `def _get_available_tags_help() -> str` `priv` (L78-89)
L79-82> ! @brief Generate available TAGs help text for argument parser. @return Formatted multi-line string listing TAGs by language. @details Imports format_available_tags from find_constructs module to generate dynamic TAG listing for CLI help display.
L85> `return format_available_tags()`
L87> `return "(tag list unavailable)"`

### fn `def build_parser() -> argparse.ArgumentParser` (L90-273)
L91-94> ! @brief Builds the CLI argument parser. @return Configured ArgumentParser instance. @details Defines all supported CLI arguments, flags, and help texts.
L271> `return parser`

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L274-281)
L275-278> ! @brief Parses command-line arguments into a namespace. @param argv List of arguments (defaults to sys.argv). @return Namespace containing parsed arguments.
L279> `return build_parser().parse_args(argv)`

### fn `def load_package_version() -> str` (L282-294)
L283-286> ! @brief Reads the package version from __init__.py. @return Version string extracted from the package. @throws ReqError If version cannot be determined.
L291> `raise ReqError("Error: unable to determine package version", 6)`
L292> `return match.group(1)`

### fn `def maybe_print_version(argv: list[str]) -> bool` (L295-305)
L296-299> ! @brief Handles --ver/--version by printing the version. @param argv Command line arguments to check. @return True if version was printed, False otherwise.
L302> `return True`
L303> `return False`

### fn `def run_upgrade() -> None` (L306-329)
L307-309> ! @brief Executes the upgrade using uv. @throws ReqError If upgrade fails.
L322> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L324> `raise ReqError(`

### fn `def run_uninstall() -> None` (L330-350)
L331-333> ! @brief Executes the uninstallation using uv. @throws ReqError If uninstall fails.
L343> `raise ReqError("Error: 'uv' command not found in PATH", 12) from exc`
L345> `raise ReqError(`

### fn `def normalize_release_tag(tag: str) -> str` (L351-361)
L352-355> ! @brief Normalizes the release tag by removing a 'v' prefix if present. @param tag The raw tag string. @return The normalized version string.
L359> `return value.strip()`

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L362-386)
L363-367> ! @brief Converts a version into a numeric tuple for comparison. @param version The version string to parse. @return Tuple of integers or None if parsing fails. @details Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
L371> `return None`
L382> `return None`
L384> `return tuple(numbers) if numbers else None`

### fn `def is_newer_version(current: str, latest: str) -> bool` (L387-403)
L388-392> ! @brief Returns True if latest is greater than current. @param current The current installed version string. @param latest The latest available version string. @return True if update is available, False otherwise.
L396> `return False`
L401> `return latest_norm > current_norm`

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L404-445)
L405-408> ! @brief Checks online for a new version and prints a warning. @param timeout_seconds Time to wait for the version check response. @details If the call fails or the response is invalid, it prints nothing and proceeds.
L427> `return`
L443> `return`

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L446-465)
L447-451> ! @brief Ensures the documentation directory exists under the project base. @param path The relative path to the documentation directory. @param project_base The project root path. @throws ReqError If path is invalid, absolute, or not a directory.
L456> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L458> `raise ReqError(`
L463> `raise ReqError("Error: --docs-dir must specify a directory, not a file", 5)`

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L466-485)
L467-471> ! @brief Ensures the test directory exists under the project base. @param path The relative path to the test directory. @param project_base The project root path. @throws ReqError If path is invalid, absolute, or not a directory.
L476> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L478> `raise ReqError(`
L483> `raise ReqError("Error: --tests-dir must specify a directory, not a file", 5)`

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L486-505)
L487-491> ! @brief Ensures the source directory exists under the project base. @param path The relative path to the source directory. @param project_base The project root path. @throws ReqError If path is invalid, absolute, or not a directory.
L496> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L498> `raise ReqError(`
L503> `raise ReqError("Error: --src-dir must specify a directory, not a file", 5)`

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L506-545)
L507-512> ! @brief Normalizes the path relative to the project root when possible. @param path_value The input path string. @param project_base The base path of the project. @return The normalized relative path string. @details Handles cases where the path includes the project directory name redundantly.
L514> `return ""`
L531> `return str(candidate.relative_to(project_base))`
L533> `return str(candidate)`
L536> `return str(resolved.relative_to(project_base))`
L542> `return trimmed`
L543> `return path_value`

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L546-559)
L547-551> ! @brief Resolves the absolute path starting from a normalized value. @param normalized The normalized relative path string. @param project_base The project root path. @return Absolute Path object or None if normalized is empty.
L553> `return None`
L556> `return candidate`
L557> `return (project_base / candidate).resolve(strict=False)`

### fn `def format_substituted_path(value: str) -> str` (L560-569)
L561-564> ! @brief Uniforms path separators for substitutions. @param value The path string to format. @return Path string with forward slashes.
L566> `return ""`
L567> `return value.replace(os.sep, "/")`

### fn `def compute_sub_path(` (L570-571)

### fn `def save_config(` (L590-595)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L617-657)
L618-622> ! @brief Loads parameters saved in .req/config.json. @param project_base The project root path. @return Dictionary containing configuration values. @throws ReqError If config file is missing or invalid.
L625> `raise ReqError(`
L632> `raise ReqError("Error: .req/config.json is not valid", 11) from exc`
L634> Fallback to legacy key names from pre-v0.59 config files.
L639> `raise ReqError("Error: missing or invalid 'guidelines-dir' field in .req/config.json", 11)`
L641> `raise ReqError("Error: missing or invalid 'docs-dir' field in .req/config.json", 11)`
L643> `raise ReqError("Error: missing or invalid 'tests-dir' field in .req/config.json", 11)`
L649> `raise ReqError("Error: missing or invalid 'src-dir' field in .req/config.json", 11)`
L650> `return {`

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L658-685)
L659-660> ! @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
L662> `return ""`
L674> If there are no files, use the directory itself.
L679> `return f"`{rel_str}`"`
L681> `return ""`
L683> `return ", ".join(files)`

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L686-714)
L687-689> ! @brief Generates a list of relative file paths (no formatting) for printing. @details Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
L691> `return []`
L703> If there are no files, use the directory itself.
L708> `return [rel_str]`
L710> `return []`
L712> `return items`

### fn `def upgrade_guidelines_templates(` (L715-716)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L748-759)
L749-750> ! @brief Normalizes the path token optionally preserving the trailing slash.
L752> `return ""`
L755> `return ""`
L757> `return f"{normalized}{suffix}"`

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L760-769)
L761-762> ! @brief Validates that the path is not absolute and raises an error otherwise.
L764> `raise ReqError(`

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L770-777)
L771-772> ! @brief Returns text with token replacements applied.
L775> `return text`

### fn `def write_text_file(dst: Path, text: str) -> None` (L778-784)
L779-780> ! @brief Writes text to disk, ensuring the destination folder exists.

### fn `def copy_with_replacements(` (L785-786)

### fn `def normalize_description(value: str) -> str` (L795-805)
L796-797> ! @brief Normalizes a description by removing superfluous quotes and escapes.
L803> `return trimmed.replace('\\"', '"')`

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L806-834)
L807-808> ! @brief Converts a Markdown prompt to TOML for Gemini.
L810> `raise ReqError(`
L817> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L835-844)
L836-837> ! @brief Extracts front matter and body from Markdown.
L840> `raise ReqError("No leading '---' block found at start of Markdown file.", 4)`
L841> Explicitly return two strings to satisfy type annotation.
L842> `return match.group(1), match.group(2)`

### fn `def extract_description(frontmatter: str) -> str` (L845-853)
L846-847> ! @brief Extracts the description from front matter.
L850> `raise ReqError("No 'description:' field found inside the leading block.", 5)`
L851> `return normalize_description(desc_match.group(1).strip())`

### fn `def extract_argument_hint(frontmatter: str) -> str` (L854-862)
L855-856> ! @brief Extracts the argument-hint from front matter, if present.
L859> `return ""`
L860> `return normalize_description(match.group(1).strip())`

### fn `def extract_purpose_first_bullet(body: str) -> str` (L863-883)
L864-865> ! @brief Returns the first bullet of the Purpose section.
L873> `raise ReqError("Error: missing '## Purpose' section in prompt.", 7)`
L880> `return match.group(1).strip()`
L881> `raise ReqError("Error: no bullet found under the '## Purpose' section.", 7)`

### fn `def json_escape(value: str) -> str` (L884-889)
L885-886> ! @brief Escapes a string for JSON without external delimiters.
L887> `return json.dumps(value)[1:-1]`

### fn `def generate_kiro_resources(` (L890-893)

### fn `def render_kiro_agent(` (L913-922)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L956-964)
L957-958> ! @brief Replaces tokens in the specified file.

### fn `def yaml_double_quote_escape(value: str) -> str` (L965-970)
L966-967> ! @brief Minimal escape for a double-quoted string in YAML.
L968> `return value.replace("\\", "\\\\").replace('"', '\\"')`

### fn `def list_docs_templates() -> list[Path]` (L971-986)
L972-975> ! @brief Returns non-hidden files available in resources/docs. @return Sorted list of file paths under resources/docs. @throws ReqError If resources/docs does not exist or has no non-hidden files.
L978> `raise ReqError("Error: no docs templates directory found in resources", 9)`
L983> `raise ReqError("Error: no docs templates found in resources/docs", 9)`
L984> `return templates`

### fn `def find_requirements_template(docs_templates: list[Path]) -> Path` (L987-1001)
L988-992> ! @brief Returns the packaged Requirements template file. @param docs_templates Runtime docs template file list from resources/docs. @return Path to `Requirements_Template.md`. @throws ReqError If `Requirements_Template.md` is not present.
L995> `return template_path`
L996> `raise ReqError(`

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L1002-1036)
L1003-1004> ! @brief Loads the Kiro template from centralized models configuration.
L1007> Try models.json first (this function is called during generation, not with legacy flag check)
L1018> `return agent_template, kiro_cfg`
L1021> `return (`
L1031> `raise ReqError(`

### fn `def strip_json_comments(text: str) -> str` (L1037-1057)
L1038-1039> ! @brief Removes // and /* */ comments to allow JSONC parsing.
L1055> `return "\n".join(cleaned)`

### fn `def load_settings(path: Path) -> dict[str, Any]` (L1058-1069)
L1059-1060> ! @brief Loads JSON/JSONC settings, removing comments when necessary.
L1063> `return json.loads(raw)`
L1067> `return json.loads(cleaned)`

### fn `def load_centralized_models(` (L1070-1073)

### fn `def get_model_tools_for_prompt(` (L1117-1118)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1153-1170)
L1154-1156> ! @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt. @details Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
L1158> `return None`
L1167> `return mode_entry.get("tools")`
L1168> `return None`

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1171-1178)
L1172-1173> ! @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
L1176> `return f"[{quoted}]"`

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1179-1189)
L1180-1181> ! @brief Recursively merges dictionaries, prioritizing incoming values.
L1187> `return base`

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1190-1198)
L1191-1192> ! @brief Finds the VS Code settings template if available.
L1195> `return candidate`
L1196> `return None`

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1199-1209)
L1200-1201> ! @brief Generates chat.promptFilesRecommendations from available prompts.
L1204> `return recommendations`
L1207> `return recommendations`

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1210-1219)
L1211-1212> ! @brief Verifies that the path is under the project root.
L1214> `raise ReqError(`

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1220-1229)
L1221-1222> ! @brief Saves a backup of VS Code settings if the file exists.
L1224> Never create an absence marker. Backup only if the file exists.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1230-1241)
L1231-1232> ! @brief Restores VS Code settings from backup, if present.
L1239> Do not remove the target file if no backup exists: restore behavior disabled otherwise.

### fn `def prune_empty_dirs(root: Path) -> None` (L1242-1255)
L1239> Do not remove the target file if no backup exists: restore behavior disabled otherwise.
L1243-1244> ! @brief Removes empty directories under the specified root.
L1246> `return`

### fn `def remove_generated_resources(project_base: Path) -> None` (L1256-1296)
L1257-1258> ! @brief Removes resources generated by the tool in the project root.

### fn `def run_remove(args: Namespace) -> None` (L1297-1343)
L1298-1299> ! @brief Handles the removal of generated resources.
L1305> `raise ReqError(`
L1310> `raise ReqError(`
L1319> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1322> `raise ReqError(`
L1327> After validation and before any removal, check for a new version.
L1330> Do not perform any restore or removal of .vscode/settings.json during removal.

### fn `def run(args: Namespace) -> None` (L1344-1543)
L1345-1346> ! @brief Handles the main initialization flow.
L1351> Main flow: validates input, calculates paths, generates resources.
L1354> `return`
L1361> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L1370> `raise ReqError(`
L1375> `raise ReqError(`
L1399> `raise ReqError("Error: invalid docs configuration values", 11)`
L1401> `raise ReqError("Error: invalid tests configuration value", 11)`
L1407> `raise ReqError("Error: invalid src configuration values", 11)`
L1447> `raise ReqError("Error: --guidelines-dir must be under the project base", 8)`
L1449> `raise ReqError("Error: --docs-dir must be under the project base", 5)`
L1451> `raise ReqError("Error: --tests-dir must be under the project base", 5)`
L1454> `raise ReqError("Error: --src-dir must be under the project base", 5)`
L1479> `raise ReqError(`
L1486> Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
L1517> `raise ReqError(`
L1522> After validation and before any operation that modifies the filesystem, check for a new version.

- var `VERBOSE = args.verbose` (L1348) — ! @brief Handles the main initialization flow.
- var `DEBUG = args.debug` (L1349)
- var `PROMPT = prompt_path.stem` (L1691)
### fn `def _format_install_table(` `priv` (L2121-2123)
L2118> Build and print a simple installation report table describing which

### fn `def fmt(row: tuple[str, ...]) -> str` (L2144-2146)
L2145> `return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row))`

- var `EXCLUDED_DIRS = frozenset({` (L2164) — ── Excluded directories for --references and --compress ──────────────────
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2173) — ── Supported source file extensions ──────────────────────────────────────
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2181-2201)
L2178> File extensions considered during source directory scanning.
L2182-2184> ! @brief Recursively collect source files from the given directories. @details Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
L2191> Filter out excluded directories (modifies dirnames in-place)
L2199> `return collected`

### fn `def _build_ascii_tree(paths: list[str]) -> str` `priv` (L2202-2239)
L2203-2206> ! @brief Build a deterministic tree string from project-relative paths. @param paths Project-relative file paths. @return Rendered tree rooted at '.'.
L2237> `return "\n".join(lines)`

### fn `def _emit(` `priv` (L2224-2226)

### fn `def _format_files_structure_markdown(files: list[str], project_base: Path) -> str` `priv` (L2240-2250)
L2241-2245> ! @brief Format markdown section containing the scanned files tree. @param files Absolute file paths selected for --references processing. @param project_base Project root used to normalize relative paths. @return Markdown section with heading and fenced tree.
L2248> `return f"# Files Structure\n```\n{tree}\n```"`

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2251-2261)
L2252-2253> ! @brief Check if the parsed args contain a standalone file command.
L2254> `return bool(`

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2262-2272)
L2263-2264> ! @brief Check if the parsed args contain a project scan command.
L2265> `return bool(`

### fn `def run_files_tokens(files: list[str]) -> None` (L2273-2291)
L2274-2275> ! @brief Execute --files-tokens: count tokens for arbitrary files.
L2286> `raise ReqError("Error: no valid files provided.", 1)`

### fn `def run_files_references(files: list[str]) -> None` (L2292-2300)
L2293-2294> ! @brief Execute --files-references: generate markdown for arbitrary files.

### fn `def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None` (L2301-2315)
L2302-2305> ! @brief Execute --files-compress: compress arbitrary files. @param files List of source file paths to compress. @param enable_line_numbers If True, emits <n>: prefixes in compressed entries.

### fn `def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None` (L2316-2341)
L2317-2320> ! @brief Execute --files-find: find constructs in arbitrary files. @param args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...]. @param enable_line_numbers If True, emits <n>: prefixes in output.
L2324> `raise ReqError(`

### fn `def run_references(args: Namespace) -> None` (L2342-2355)
L2343-2344> ! @brief Execute --references: generate markdown for project source files.
L2350> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_compress_cmd(args: Namespace) -> None` (L2356-2373)
L2357-2359> ! @brief Execute --compress: compress project source files. @param args Parsed CLI arguments namespace.
L2365> `raise ReqError("Error: no source files found in configured directories.", 1)`

### fn `def run_find(args: Namespace) -> None` (L2374-2400)
L2375-2378> ! @brief Execute --find: find constructs in project source files. @param args Parsed CLI arguments namespace. @throws ReqError If no source files found or no constructs match criteria with available TAGs listing.
L2384> `raise ReqError("Error: no source files found in configured directories.", 1)`
L2386> args.find is a list [TAG, PATTERN]
L2398> `raise ReqError(str(e), 1)`

### fn `def run_tokens(args: Namespace) -> None` (L2401-2423)
L2402-2405> ! @brief Execute --tokens: count tokens for files directly in --docs-dir. @param args Parsed CLI arguments namespace. @details Requires --base/--here and --docs-dir, then delegates reporting to run_files_tokens.
L2413> `raise ReqError("Error: --tokens requires --docs-dir.", 1)`
L2420> `raise ReqError("Error: no files found in --docs-dir.", 1)`

### fn `def _resolve_project_base(args: Namespace) -> Path` `priv` (L2424-2444)
L2425-2429> ! @brief Resolve project base path for project-level commands. @param args Parsed CLI arguments namespace. @return Absolute path of project base. @throws ReqError If --base/--here is missing or the resolved path does not exist.
L2431> `raise ReqError(`
L2441> `raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)`
L2442> `return project_base`

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L2445-2471)
L2446-2447> ! @brief Resolve project base and src-dirs for --references/--compress.
L2454> Source dirs can come from args or from config
L2462> `raise ReqError(`
L2467> `raise ReqError("Error: no source directories configured.", 1)`
L2469> `return project_base, src_dirs`

### fn `def main(argv: Optional[list[str]] = None) -> int` (L2472-2537)
L2473-2475> ! @brief CLI entry point for console_scripts and `-m` execution. @details Returns an exit code (0 success, non-zero on error).
L2481> `return 0`
L2484> `return 0`
L2487> `return 0`
L2489> `return 0`
L2493> Standalone file commands (no --base/--here required)
L2509> `return 0`
L2510> Project scan commands (require --base/--here)
L2520> `return 0`
L2521> Standard init flow requires --base or --here
L2523> `raise ReqError(`
L2529> `return e.code`
L2530> Unexpected error
L2536> `return 1`
L2537> `return 0`

- var `VERBOSE = getattr(args, "verbose", False)` (L2491)
- var `DEBUG = getattr(args, "debug", False)` (L2492)
## Comments
- L46: ! @brief Initialize an expected CLI failure payload. @param message Human-readable error message. @param code Process exit code bound to the failur...
- L56: ! @brief Prints an informational message. @param msg The message string to print.
- L63: ! @brief Prints a debug message if debugging is active. @param msg The debug message string to print.
- L71: ! @brief Prints a verbose message if verbose mode is active. @param msg The verbose message string to print.
- L79: ! @brief Generate available TAGs help text for argument parser. @return Formatted multi-line string listing TAGs by language. @details Imports form...
- L91: ! @brief Builds the CLI argument parser. @return Configured ArgumentParser instance. @details Defines all supported CLI arguments, flags, and help ...
- L275: ! @brief Parses command-line arguments into a namespace. @param argv List of arguments (defaults to sys.argv). @return Namespace containing parsed ...
- L283: ! @brief Reads the package version from __init__.py. @return Version string extracted from the package. @throws ReqError If version cannot be deter...
- L296: ! @brief Handles --ver/--version by printing the version. @param argv Command line arguments to check. @return True if version was printed, False o...
- L307: ! @brief Executes the upgrade using uv. @throws ReqError If upgrade fails.
- L331: ! @brief Executes the uninstallation using uv. @throws ReqError If uninstall fails.
- L352: ! @brief Normalizes the release tag by removing a 'v' prefix if present. @param tag The raw tag string. @return The normalized version string.
- L363: ! @brief Converts a version into a numeric tuple for comparison. @param version The version string to parse. @return Tuple of integers or None if p...
- L388: ! @brief Returns True if latest is greater than current. @param current The current installed version string. @param latest The latest available ve...
- L405: ! @brief Checks online for a new version and prints a warning. @param timeout_seconds Time to wait for the version check response. @details If the ...
- L447: ! @brief Ensures the documentation directory exists under the project base. @param path The relative path to the documentation directory. @param pr...
- L467: ! @brief Ensures the test directory exists under the project base. @param path The relative path to the test directory. @param project_base The pro...
- L487: ! @brief Ensures the source directory exists under the project base. @param path The relative path to the source directory. @param project_base The...
- L507: ! @brief Normalizes the path relative to the project root when possible. @param path_value The input path string. @param project_base The base path...
- L547: ! @brief Resolves the absolute path starting from a normalized value. @param normalized The normalized relative path string. @param project_base Th...
- L561: ! @brief Uniforms path separators for substitutions. @param value The path string to format. @return Path string with forward slashes.
- L573: ! @brief Calculates the relative path to use in tokens. @param normalized The normalized relative path. @param absolute The absolute path object (c...
- L597: ! @brief Saves normalized parameters to .req/config.json. @param project_base The project root path. @param guidelines_dir_value Relative path to g...
- L618: ! @brief Loads parameters saved in .req/config.json. @param project_base The project root path. @return Dictionary containing configuration values....
- L634: Fallback to legacy key names from pre-v0.59 config files.
- L659: ! @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
- L674: If there are no files, use the directory itself.
- L687: ! @brief Generates a list of relative file paths (no formatting) for printing. @details Each entry is formatted as `guidelines/file.md` (forward sl...
- L703: If there are no files, use the directory itself.
- L718: ! @brief Copies guidelines templates from resources/guidelines/ to the target directory. @details Args: guidelines_dest: Target directory where tem...
- L749: ! @brief Normalizes the path token optionally preserving the trailing slash.
- L761: ! @brief Validates that the path is not absolute and raises an error otherwise.
- L771: ! @brief Returns text with token replacements applied.
- L779: ! @brief Writes text to disk, ensuring the destination folder exists.
- L788: ! @brief Copies a file substituting the indicated tokens with their values.
- L796: ! @brief Normalizes a description by removing superfluous quotes and escapes.
- L807: ! @brief Converts a Markdown prompt to TOML for Gemini.
- L836: ! @brief Extracts front matter and body from Markdown.
- L841: Explicitly return two strings to satisfy type annotation.
- L846: ! @brief Extracts the description from front matter.
- L855: ! @brief Extracts the argument-hint from front matter, if present.
- L864: ! @brief Returns the first bullet of the Purpose section.
- L885: ! @brief Escapes a string for JSON without external delimiters.
- L895: ! @brief Generates the resource list for the Kiro agent.
- L924: ! @brief Renders the Kiro agent JSON and populates main fields.
- L952: If parsing fails, return raw template to preserve previous behavior
- L957: ! @brief Replaces tokens in the specified file.
- L966: ! @brief Minimal escape for a double-quoted string in YAML.
- L972: ! @brief Returns non-hidden files available in resources/docs. @return Sorted list of file paths under resources/docs. @throws ReqError If resource...
- L988: ! @brief Returns the packaged Requirements template file. @param docs_templates Runtime docs template file list from resources/docs. @return Path t...
- L1003: ! @brief Loads the Kiro template from centralized models configuration.
- L1007: Try models.json first (this function is called during generation, not with legacy flag check)
- L1038: ! @brief Removes // and /* */ comments to allow JSONC parsing.
- L1059: ! @brief Loads JSON/JSONC settings, removing comments when necessary.
- L1075: ! @brief Loads centralized models configuration from common/models.json. @details Returns a map cli_name -> parsed_json or None if not present. Whe...
- L1081: Priority 1: preserve_models_path if provided and exists
- L1085: Priority 2: legacy mode
- L1092: Fallback: standard models.json
- L1099: Load the centralized configuration
- L1107: Extract individual CLI configs
- L1120: ! @brief Extracts model and tools for the prompt from the CLI config. @details Returns (model, tools) where each value can be None if not available.
- L1136-1137: Use the unified key name 'tools' across all CLI configs. | Accept either a list of strings or a CSV string in the config.json.
- L1145: Parse comma-separated string into list
- L1154: ! @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt. @details Can return a list of strings, a string, or None depending o...
- L1172: ! @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
- L1180: ! @brief Recursively merges dictionaries, prioritizing incoming values.
- L1191: ! @brief Finds the VS Code settings template if available.
- L1200: ! @brief Generates chat.promptFilesRecommendations from available prompts.
- L1211: ! @brief Verifies that the path is under the project root.
- L1221-1224: ! @brief Saves a backup of VS Code settings if the file exists. | Never create an absence marker. Backup only if the file exists.
- L1231: ! @brief Restores VS Code settings from backup, if present.
- L1243: ! @brief Removes empty directories under the specified root.
- L1257: ! @brief Removes resources generated by the tool in the project root.
- L1298: ! @brief Handles the removal of generated resources.
- L1327: After validation and before any removal, check for a new version.
- L1330: Do not perform any restore or removal of .vscode/settings.json during removal.
- L1351: Main flow: validates input, calculates paths, generates resources.
- L1486: Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
- L1522: After validation and before any operation that modifies the filesystem, check for a new version.
- L1552-1553: Copy models configuration to .req/models.json based on legacy mode (REQ-084) | Skip if --preserve-models is active
- L1578: Create requirements.md only if the --docs-dir folder is empty.
- L1587: Generate the file list for the %%GUIDELINES_FILES%% token.
- L1656: Load CLI configs only if requested to include model/tools
- L1667: Determine preserve_models_path (REQ-082)
- L1698: (Removed: bootstrap file inlining and YOLO stop/approval substitution)
- L1714: Precompute description and Claude metadata so provider blocks can reuse them safely.
- L1724: .codex/prompts
- L1733: .codex/skills/req/<prompt>/SKILL.md
- L1763: Gemini TOML
- L1801: .kiro/prompts
- L1811: .claude/agents
- L1837: .github/agents
- L1865: .github/prompts
- L1897: .kiro/agents
- L1927: .opencode/agent
- L1958: .opencode/command
- L2003: .claude/commands/req
- L2063: Load existing settings (if present) and those from the template.
- L2069: If checking/loading fails, consider it empty
- L2074: Merge without modifying original until sure.
- L2084: If final result is identical to existing, do not rewrite nor backup.
- L2089: If changes are expected, create backup only if file exists.
- L2092: Write final settings.
- L2100-2101: Final success notification: printed only when the command completed all | intended filesystem modifications without raising an exception.
- L2108-2109: Print the discovered directories used for token substitutions | as required by REQ-078: one item per line prefixed with '- '.
- L2125: ! @brief Format the installation summary table aligning header, prompts, and rows.
- L2169: Directories excluded from source scanning in --references and --compress.
- L2182: ! @brief Recursively collect source files from the given directories. @details Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
- L2191: Filter out excluded directories (modifies dirnames in-place)
- L2203: ! @brief Build a deterministic tree string from project-relative paths. @param paths Project-relative file paths. @return Rendered tree rooted at '.'.
- L2241: ! @brief Format markdown section containing the scanned files tree. @param files Absolute file paths selected for --references processing. @param p...
- L2252: ! @brief Check if the parsed args contain a standalone file command.
- L2263: ! @brief Check if the parsed args contain a project scan command.
- L2274: ! @brief Execute --files-tokens: count tokens for arbitrary files.
- L2293: ! @brief Execute --files-references: generate markdown for arbitrary files.
- L2302: ! @brief Execute --files-compress: compress arbitrary files. @param files List of source file paths to compress. @param enable_line_numbers If True...
- L2317: ! @brief Execute --files-find: find constructs in arbitrary files. @param args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...]. @param enable...
- L2343: ! @brief Execute --references: generate markdown for project source files.
- L2357: ! @brief Execute --compress: compress project source files. @param args Parsed CLI arguments namespace.
- L2375: ! @brief Execute --find: find constructs in project source files. @param args Parsed CLI arguments namespace. @throws ReqError If no source files f...
- L2386: args.find is a list [TAG, PATTERN]
- L2402: ! @brief Execute --tokens: count tokens for files directly in --docs-dir. @param args Parsed CLI arguments namespace. @details Requires --base/--he...
- L2425: ! @brief Resolve project base path for project-level commands. @param args Parsed CLI arguments namespace. @return Absolute path of project base. @...
- L2446: ! @brief Resolve project base and src-dirs for --references/--compress.
- L2454: Source dirs can come from args or from config
- L2473: ! @brief CLI entry point for console_scripts and `-m` execution. @details Returns an exit code (0 success, non-zero on error).
- L2493: Standalone file commands (no --base/--here required)
- L2510: Project scan commands (require --base/--here)
- L2521: Standard init flow requires --base or --here

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|24||
|`RESOURCE_ROOT`|var|pub|27||
|`VERBOSE`|var|pub|30||
|`DEBUG`|var|pub|33||
|`REQUIREMENTS_TEMPLATE_NAME`|var|pub|36||
|`ReqError`|class|pub|40-54|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|45-54|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|55-61|def log(msg: str) -> None|
|`dlog`|fn|pub|62-69|def dlog(msg: str) -> None|
|`vlog`|fn|pub|70-77|def vlog(msg: str) -> None|
|`_get_available_tags_help`|fn|priv|78-89|def _get_available_tags_help() -> str|
|`build_parser`|fn|pub|90-273|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|274-281|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|282-294|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|295-305|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|306-329|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|330-350|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|351-361|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|362-386|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|387-403|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|404-445|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|446-465|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|466-485|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|486-505|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|506-545|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|546-559|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|560-569|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|570-571|def compute_sub_path(|
|`save_config`|fn|pub|590-595|def save_config(|
|`load_config`|fn|pub|617-657|def load_config(project_base: Path) -> dict[str, str | li...|
|`generate_guidelines_file_list`|fn|pub|658-685|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|686-714|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`upgrade_guidelines_templates`|fn|pub|715-716|def upgrade_guidelines_templates(|
|`make_relative_token`|fn|pub|748-759|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|760-769|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|770-777|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|778-784|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|785-786|def copy_with_replacements(|
|`normalize_description`|fn|pub|795-805|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|806-834|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|835-844|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|845-853|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|854-862|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|863-883|def extract_purpose_first_bullet(body: str) -> str|
|`json_escape`|fn|pub|884-889|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|890-893|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|913-922|def render_kiro_agent(|
|`replace_tokens`|fn|pub|956-964|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|965-970|def yaml_double_quote_escape(value: str) -> str|
|`list_docs_templates`|fn|pub|971-986|def list_docs_templates() -> list[Path]|
|`find_requirements_template`|fn|pub|987-1001|def find_requirements_template(docs_templates: list[Path]...|
|`load_kiro_template`|fn|pub|1002-1036|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|1037-1057|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|1058-1069|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|1070-1073|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|1117-1118|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1153-1170|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1171-1178|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1179-1189|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1190-1198|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1199-1209|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1210-1219|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1220-1229|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1230-1241|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1242-1255|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1256-1296|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1297-1343|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1344-1543|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1348||
|`DEBUG`|var|pub|1349||
|`PROMPT`|var|pub|1691||
|`_format_install_table`|fn|priv|2121-2123|def _format_install_table(|
|`fmt`|fn|pub|2144-2146|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|2164||
|`SUPPORTED_EXTENSIONS`|var|pub|2173||
|`_collect_source_files`|fn|priv|2181-2201|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_build_ascii_tree`|fn|priv|2202-2239|def _build_ascii_tree(paths: list[str]) -> str|
|`_emit`|fn|priv|2224-2226|def _emit(|
|`_format_files_structure_markdown`|fn|priv|2240-2250|def _format_files_structure_markdown(files: list[str], pr...|
|`_is_standalone_command`|fn|priv|2251-2261|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2262-2272|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2273-2291|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2292-2300|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2301-2315|def run_files_compress(files: list[str], enable_line_numb...|
|`run_files_find`|fn|pub|2316-2341|def run_files_find(args_list: list[str], enable_line_numb...|
|`run_references`|fn|pub|2342-2355|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2356-2373|def run_compress_cmd(args: Namespace) -> None|
|`run_find`|fn|pub|2374-2400|def run_find(args: Namespace) -> None|
|`run_tokens`|fn|pub|2401-2423|def run_tokens(args: Namespace) -> None|
|`_resolve_project_base`|fn|priv|2424-2444|def _resolve_project_base(args: Namespace) -> Path|
|`_resolve_project_src_dirs`|fn|priv|2445-2471|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|2472-2537|def main(argv: Optional[list[str]] = None) -> int|
|`VERBOSE`|var|pub|2491||
|`DEBUG`|var|pub|2492||


---

# compress.py | Python | 386L | 11 symbols | 5 imports | 41 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress.py`
> ! @file compress.py @brief Source code compressor for LLM context optimization. @details Parses a source file and removes all comments (inline, single-line, multi-line), blank lines, trailing white...

## Imports
```
import os
import re
import sys
from .source_analyzer import build_language_specs
import argparse
```

## Definitions

- var `EXT_LANG_MAP = {` (L17) — Extension-to-language map (mirrors generate_markdown.py)
- var `INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}` (L29) — ! @brief Extension-to-language normalization map for compression input.
### fn `def _get_specs()` `priv` (L36-46)
L33> ! @brief Cached language specification dictionary initialized lazily.
L37-40> ! @brief Return cached language specifications, initializing once. @return Dictionary mapping normalized language keys to language specs. @details If cache is empty, calls `build_language_specs()` to populate it.
L44> `return _specs_cache`

### fn `def detect_language(filepath: str) -> str | None` (L47-56)
L48-52> ! @brief Detect language key from file extension. @param filepath Source file path. @return Normalized language key, or None when extension is unsupported. @details Uses `EXT_LANG_MAP` for lookup. Case-insensitive extension matching.
L54> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L57-98)
L58-64> ! @brief Check if position `pos` in `line` is inside a string literal. @param line The code line string. @param pos The character index to check. @param string_delimiters Tuple of string delimiter characters/sequences. @return True if `pos` is inside a string, False otherwise. @details iterates through the line handling escaped delimiters.
L71> Check for escaped delimiter (single-char only)
L73> Count consecutive backslashes
L96> `return in_string is not None`

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L99-142)
L101-107> ! @brief Remove trailing single-line comment from a code line. @param line The code line string. @param single_comment The single-line comment marker (e.g., "//", "#"). @param string_delimiters Tuple of string delimiters to respect. @return The line content before the comment starts. @details Respects string literals; does not remove comments inside strings.
L109> `return line`
L132> `return line[:i]`
L140> `return line`

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L143-154)
L144-147> ! @brief Check if a line is a standalone Python docstring (triple-quote only). @param line The code line string. @return True if the line appears to be a standalone triple-quoted string.
L151> `return True`
L152> `return False`

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L155-166)
L157-161> ! @brief Format compressed entries, optionally prefixing original line numbers. @param entries List of tuples (line_number, text). @param include_line_numbers Boolean flag to enable line prefixes. @return Formatted string.
L163> `return '\n'.join(text for _, text in entries)`
L164> `return '\n'.join(f"{lineno}: {text}" for lineno, text in entries)`

### fn `def compress_source(source: str, language: str,` (L167-334)
L169-176> ! @brief Compress source code by removing comments, blank lines, and extra whitespace. @param source The source code string. @param language Language identifier (e.g. "python", "javascript"). @param include_line_numbers If True (default), prefix each line with <n>: format. @return Compressed source code string. @throws ValueError If language is unsupported. @details Preserves indentation for indent-significant languages (Python, Haskell, Elixir).
L180> `raise ValueError(f"Unsupported language: {language}")`
L185> list of (original_line_number, text)
L192> Python: also handle ''' as multi-comment
L201> --- Handle multi-line comment continuation ---
L204> End of multi-line comment found
L208> Process remainder as a new line
L215-241> --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docstring: if python_docstring_delim in line: end_pos = line.index(python_docstring_delim) + 3 remainder = line[end_pos:] in_python_docstring = False python_docstring_delim = None if remainder.strip(): lines[i] = remainder continue i += 1 continue stripped = line.strip() Skip empty lines if not stripped: i += 1 continue --- Detect multi-line comment start --- if mc_start: For Python, triple-quotes can be strings or docstrings. We only strip standalone docstrings (line starts with triple-quote after optional whitespace). if is_python: for q in ('"""', "'''"):
L243> Single-line docstring: """...
L245> Check it's not a variable assignment like x = """...
L249> Standalone docstring or assigned — skip if standalone
L253> If code before and not assignment, keep line
L255> Multi-line docstring start
L266> Non-Python: check for multi-line comment start
L269> Check if inside a string
L272> Check for same-line close
L276> Single-line block comment: remove it
L283> Re-process this reconstructed line
L287> Multi-line comment starts here
L296> --- Full-line single-line comment ---
L298> Special: keep shebangs
L304> --- Remove inline comment ---
L308> --- Clean whitespace ---
L310> Keep leading whitespace, strip trailing
L316> Collapse internal multiple spaces (but not in strings)
L324> Remove trailing whitespace
L332> `return _format_result(result, include_line_numbers)`

### fn `def compress_file(filepath: str, language: str | None = None,` (L335-356)
L337-343> ! @brief Compress a source file by removing comments and extra whitespace. @param filepath Path to the source file. @param language Optional language override. Auto-detected if None. @param include_line_numbers If True (default), prefix each line with <n>: format. @return Compressed source code string. @throws ValueError If language cannot be detected.
L347> `raise ValueError(`
L354> `return compress_source(source, language, include_line_numbers)`

### fn `def main()` (L357-384)
L358-360> ! @brief Execute the standalone compression CLI. @details Parses command-line arguments and invokes `compress_file`, printing the result to stdout or errors to stderr.
L374> `sys.exit(1)`
L382> `sys.exit(1)`

## Comments
- L2: ! @file compress.py @brief Source code compressor for LLM context optimization. @details Parses a source file and removes all comments (inline, sin...
- L30: ! @brief Languages requiring indentation-preserving compression behavior.
- L37: ! @brief Return cached language specifications, initializing once. @return Dictionary mapping normalized language keys to language specs. @details ...
- L48: ! @brief Detect language key from file extension. @param filepath Source file path. @return Normalized language key, or None when extension is unsu...
- L58: ! @brief Check if position `pos` in `line` is inside a string literal. @param line The code line string. @param pos The character index to check. @...
- L71-73: Check for escaped delimiter (single-char only) | Count consecutive backslashes
- L101: ! @brief Remove trailing single-line comment from a code line. @param line The code line string. @param single_comment The single-line comment mark...
- L144: ! @brief Check if a line is a standalone Python docstring (triple-quote only). @param line The code line string. @return True if the line appears t...
- L157: ! @brief Format compressed entries, optionally prefixing original line numbers. @param entries List of tuples (line_number, text). @param include_l...
- L169: ! @brief Compress source code by removing comments, blank lines, and extra whitespace. @param source The source code string. @param language Langua...
- L192: Python: also handle ''' as multi-comment
- L201: --- Handle multi-line comment continuation ---
- L204: End of multi-line comment found
- L208: Process remainder as a new line
- L215-245: --- Python docstrings (""" / ''') used as standalone comments --- if is_python and in_python_docs... | Single-line docstring: """... | Check it's not a variable assignment like x = """...
- L249: Standalone docstring or assigned — skip if standalone
- L253-255: If code before and not assignment, keep line | Multi-line docstring start
- L266: Non-Python: check for multi-line comment start
- L269: Check if inside a string
- L272: Check for same-line close
- L276: Single-line block comment: remove it
- L283: Re-process this reconstructed line
- L287: Multi-line comment starts here
- L296-298: --- Full-line single-line comment --- | Special: keep shebangs
- L304: --- Remove inline comment ---
- L308-310: --- Clean whitespace --- | Keep leading whitespace, strip trailing
- L316: Collapse internal multiple spaces (but not in strings)
- L324: Remove trailing whitespace
- L337: ! @brief Compress a source file by removing comments and extra whitespace. @param filepath Path to the source file. @param language Optional langua...
- L358: ! @brief Execute the standalone compression CLI. @details Parses command-line arguments and invokes `compress_file`, printing the result to stdout ...

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
> ! @file compress_files.py @brief Compress and concatenate multiple source files. @details Uses the compress module to strip comments and whitespace from each input file, then concatenates results w...

## Imports
```
import os
import sys
from .compress import compress_file, detect_language
import argparse
```

## Definitions

### fn `def _extract_line_range(compressed_with_line_numbers: str) -> tuple[int, int]` `priv` (L16-33)
L17-21> ! @brief Extract source line interval from compressed output with <n>: prefixes. @param compressed_with_line_numbers Compressed payload generated with include_line_numbers=True. @return Tuple (line_start, line_end) derived from preserved <n>: prefixes; returns (0, 0) when no prefixed lines exist. @details Parses the first token of each line as an integer line number.
L29> `return 0, 0`
L31> `return line_numbers[0], line_numbers[-1]`

### fn `def compress_files(filepaths: list[str],` (L34-90)
L37-44> ! @brief Compress multiple source files and concatenate with identifying headers. @param filepaths List of source file paths. @param include_line_numbers If True (default), keep <n>: prefixes in code block lines. @param verbose If True, emits progress status messages on stderr. @return Concatenated compressed output string. @throws ValueError If no files could be processed. @details Each file is compressed and emitted as: header line `@@@ <path> | <lang>`, line-range metadata `- Lines: <start>-<end>`, and fenced code block delimited by triple backticks. Line range is derived from the already computed <n>: prefixes to preserve existing numbering logic. Files are separated by a blank line.
L82> `raise ValueError("No valid source files processed")`
L88> `return "\n\n".join(parts)`

### fn `def main()` (L91-111)
L92-94> ! @brief Execute the multi-file compression CLI command. @details Parses command-line arguments, calls `compress_files`, and prints output or errors.
L109> `sys.exit(1)`

## Comments
- L2: ! @file compress_files.py @brief Compress and concatenate multiple source files. @details Uses the compress module to strip comments and whitespace...
- L17: ! @brief Extract source line interval from compressed output with <n>: prefixes. @param compressed_with_line_numbers Compressed payload generated w...
- L37: ! @brief Compress multiple source files and concatenate with identifying headers. @param filepaths List of source file paths. @param include_line_n...
- L92: ! @brief Execute the multi-file compression CLI command. @details Parses command-line arguments, calls `compress_files`, and prints output or errors.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_extract_line_range`|fn|priv|16-33|def _extract_line_range(compressed_with_line_numbers: str...|
|`compress_files`|fn|pub|34-90|def compress_files(filepaths: list[str],|
|`main`|fn|pub|91-111|def main()|


---

# find_constructs.py | Python | 255L | 8 symbols | 7 imports | 14 comments
> Path: `/home/ogekuri/useReq/src/usereq/find_constructs.py`
> ! @file find_constructs.py @brief Find and extract specific constructs from source files. @details Filters source code constructs (CLASS, FUNCTION, etc.) by type tag and name regex pattern, generat...

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

- var `LANGUAGE_TAGS = {` (L20) — ── Language-specific TAG support map ────────────────────────────────────────
### fn `def format_available_tags() -> str` (L44-57)
L45-48> ! @brief Generate formatted list of available TAGs per language. @return Multi-line string listing each language with its supported TAGs. @details Iterates LANGUAGE_TAGS dictionary, formats each entry as "- Language: TAG1, TAG2, ..." with language capitalized and tags alphabetically sorted and comma-separated.
L55> `return "\n".join(lines)`

### fn `def parse_tag_filter(tag_string: str) -> set[str]` (L58-66)
L59-63> ! @brief Parse pipe-separated tag filter into a normalized set. @param tag_string Raw tag filter string (e.g., "CLASS|FUNCTION"). @return Set of uppercase tag identifiers. @details Splits the input string by pipe character `|` and strips whitespace from each component.
L64> `return {tag.strip().upper() for tag in tag_string.split("|") if tag.strip()}`

### fn `def language_supports_tags(lang: str, tag_set: set[str]) -> bool` (L67-77)
L68-73> ! @brief Check if the language supports at least one of the requested tags. @param lang Normalized language identifier. @param tag_set Set of requested TAG identifiers. @return True if intersection is non-empty, False otherwise. @details Lookups the language in `LANGUAGE_TAGS` and checks if any of `tag_set` exists in the supported tags.
L75> `return bool(supported & tag_set)`

### fn `def construct_matches(element, tag_set: set[str], pattern: str) -> bool` (L78-95)
L79-85> ! @brief Check if a source element matches tag filter and regex pattern. @param element SourceElement instance from analyzer. @param tag_set Set of requested TAG identifiers. @param pattern Regex pattern string to test against element name. @return True if element type is in tag_set and name matches pattern. @details Validates the element type and then applies the regex search on the element name.
L87> `return False`
L89> `return False`
L91> `return bool(re.search(pattern, element.name))`
L93> `return False`

### fn `def format_construct(element, source_lines: list[str], include_line_numbers: bool) -> str` (L96-124)
L97-103> ! @brief Format a single matched construct for markdown output with complete code extraction. @param element SourceElement instance containing line range indices. @param source_lines Complete source file content as list of lines. @param include_line_numbers If True, prefix code lines with <n>: format. @return Formatted markdown block for the construct with complete code from line_start to line_end. @details Extracts the complete construct code directly from source_lines using element.line_start and element.line_end indices.
L110> Extract COMPLETE code block from source file (not truncated extract)
L122> `return "\n".join(lines)`

### fn `def find_constructs_in_files(` (L125-130)

### fn `def main()` (L218-253)
L219-221> ! @brief Execute the construct finding CLI command. @details Parses arguments and calls find_constructs_in_files. Handles exceptions by printing errors to stderr.
L251> `sys.exit(1)`

## Comments
- L2: ! @file find_constructs.py @brief Find and extract specific constructs from source files. @details Filters source code constructs (CLASS, FUNCTION,...
- L45: ! @brief Generate formatted list of available TAGs per language. @return Multi-line string listing each language with its supported TAGs. @details ...
- L59: ! @brief Parse pipe-separated tag filter into a normalized set. @param tag_string Raw tag filter string (e.g., "CLASS|FUNCTION"). @return Set of up...
- L68: ! @brief Check if the language supports at least one of the requested tags. @param lang Normalized language identifier. @param tag_set Set of reque...
- L79: ! @brief Check if a source element matches tag filter and regex pattern. @param element SourceElement instance from analyzer. @param tag_set Set of...
- L97: ! @brief Format a single matched construct for markdown output with complete code extraction. @param element SourceElement instance containing line...
- L110: Extract COMPLETE code block from source file (not truncated extract)
- L132: ! @brief Find and extract constructs matching tag filter and regex pattern from multiple files. @param filepaths List of source file paths. @param ...
- L167: Check if language supports at least one requested tag
- L175: Read complete source file for full construct extraction
- L183: Filter elements matching tag and pattern
- L219: ! @brief Execute the construct finding CLI command. @details Parses arguments and calls find_constructs_in_files. Handles exceptions by printing er...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`LANGUAGE_TAGS`|var|pub|20||
|`format_available_tags`|fn|pub|44-57|def format_available_tags() -> str|
|`parse_tag_filter`|fn|pub|58-66|def parse_tag_filter(tag_string: str) -> set[str]|
|`language_supports_tags`|fn|pub|67-77|def language_supports_tags(lang: str, tag_set: set[str]) ...|
|`construct_matches`|fn|pub|78-95|def construct_matches(element, tag_set: set[str], pattern...|
|`format_construct`|fn|pub|96-124|def format_construct(element, source_lines: list[str], in...|
|`find_constructs_in_files`|fn|pub|125-130|def find_constructs_in_files(|
|`main`|fn|pub|218-253|def main()|


---

# generate_markdown.py | Python | 128L | 4 symbols | 3 imports | 7 comments
> Path: `/home/ogekuri/useReq/src/usereq/generate_markdown.py`
> ! @file generate_markdown.py @brief Generate concatenated markdown from arbitrary source files. @details Analyzes each input file with source_analyzer and produces a single markdown output concaten...

## Imports
```
import os
import sys
from .source_analyzer import SourceAnalyzer, format_markdown
```

## Definitions

- var `EXT_LANG_MAP = {` (L16) — Map file extensions to languages
### fn `def detect_language(filepath: str) -> str | None` (L43-52)
L40> ! @brief Extension-to-language normalization map for markdown generation.
L44-48> ! @brief Detect language from file extension. @param filepath Path to the source file. @return Language identifier string or None if unknown. @details Uses EXT_LANG_MAP for extension lookup (case-insensitive).
L50> `return EXT_LANG_MAP.get(ext.lower())`

### fn `def generate_markdown(filepaths: list[str], verbose: bool = False) -> str` (L53-109)
L54-60> ! @brief Analyze source files and return concatenated markdown. @param filepaths List of source file paths to analyze. @param verbose If True, emits progress status messages on stderr. @return Concatenated markdown string with all file analyses. @throws ValueError If no valid source files are found. @details Iterates through files, detecting language, analyzing constructs, and formatting output.
L101> `raise ValueError("No valid source files processed")`
L107> `return "\n\n---\n\n".join(md_parts)`

### fn `def main()` (L110-126)
L111-113> ! @brief Execute the standalone markdown generation CLI command. @details Expects file paths as command-line arguments. Prints generated markdown to stdout.
L117> `sys.exit(1)`
L124> `sys.exit(1)`

## Comments
- L2: ! @file generate_markdown.py @brief Generate concatenated markdown from arbitrary source files. @details Analyzes each input file with source_analy...
- L44: ! @brief Detect language from file extension. @param filepath Path to the source file. @return Language identifier string or None if unknown. @deta...
- L54: ! @brief Analyze source files and return concatenated markdown. @param filepaths List of source file paths to analyze. @param verbose If True, emit...
- L111: ! @brief Execute the standalone markdown generation CLI command. @details Expects file paths as command-line arguments. Prints generated markdown t...

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|16||
|`detect_language`|fn|pub|43-52|def detect_language(filepath: str) -> str | None|
|`generate_markdown`|fn|pub|53-109|def generate_markdown(filepaths: list[str], verbose: bool...|
|`main`|fn|pub|110-126|def main()|


---

# pdoc_utils.py | Python | 98L | 3 symbols | 6 imports | 5 comments
> Path: `/home/ogekuri/useReq/src/usereq/pdoc_utils.py`
> ! @file pdoc_utils.py @brief Utilities for generating pdoc documentation. @details Wraps pdoc execution to generate HTML documentation for the project modules. ...

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

### fn `def _normalize_modules(modules: str | Iterable[str]) -> list[str]` `priv` (L18-27)
L19-22> ! @brief Returns a list of modules from either a string or an iterable. @param modules A single module name string or an iterable of strings. @return List of module names.
L24> `return [modules]`
L25> `return list(modules)`

### fn `def _run_pdoc(command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess` `priv` (L28-45)
L29-35> ! @brief Runs pdoc and captures output for error handling. @param command The command list to execute. @param env Environment variables dictionary. @param cwd Working directory path. @return CompletedProcess object containing execution results. @details Executes pdoc as a subprocess with captured output (stdout/stderr).
L36> `return subprocess.run(`

### fn `def generate_pdoc_docs(` (L46-50)

## Comments
- L19: ! @brief Returns a list of modules from either a string or an iterable. @param modules A single module name string or an iterable of strings. @retu...
- L29: ! @brief Runs pdoc and captures output for error handling. @param command The command list to execute. @param env Environment variables dictionary....
- L52: ! @brief Generates or updates pdoc documentation in the target output directory. @param output_dir Directory where HTML documentation will be writt...
- L89: Fallback for pdoc versions that do not support --all-submodules.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_normalize_modules`|fn|priv|18-27|def _normalize_modules(modules: str | Iterable[str]) -> l...|
|`_run_pdoc`|fn|priv|28-45|def _run_pdoc(command: list[str], *, env: dict[str, str],...|
|`generate_pdoc_docs`|fn|pub|46-50|def generate_pdoc_docs(|


---

# source_analyzer.py | Python | 1957L | 56 symbols | 7 imports | 130 comments
> Path: `/home/ogekuri/useReq/src/usereq/source_analyzer.py`
> ! @file source_analyzer.py @brief Multi-language source code analyzer. @details Inspired by tree-sitter, this module analyzes source files across multiple programming languages, extracting: - Defin...

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

### class `class ElementType(Enum)` : Enum (L19-49)
- var `FUNCTION = auto()` (L23) L20> ! @brief Element types recognized in source code. @details Enumeration of all supported syntactic...
- var `METHOD = auto()` (L24)
- var `CLASS = auto()` (L25)
- var `STRUCT = auto()` (L26)
- var `ENUM = auto()` (L27)
- var `TRAIT = auto()` (L28)
- var `INTERFACE = auto()` (L29)
- var `MODULE = auto()` (L30)
- var `IMPL = auto()` (L31)
- var `MACRO = auto()` (L32)
- var `CONSTANT = auto()` (L33)
- var `VARIABLE = auto()` (L34)
- var `TYPE_ALIAS = auto()` (L35)
- var `IMPORT = auto()` (L36)
- var `DECORATOR = auto()` (L37)
- var `COMMENT_SINGLE = auto()` (L38)
- var `COMMENT_MULTI = auto()` (L39)
- var `COMPONENT = auto()` (L40)
- var `PROTOCOL = auto()` (L41)
- var `EXTENSION = auto()` (L42)
- var `UNION = auto()` (L43)
- var `NAMESPACE = auto()` (L44)
- var `PROPERTY = auto()` (L45)
- var `SIGNAL = auto()` (L46)
- var `TYPEDEF = auto()` (L47)

### class `class SourceElement` `@dataclass` (L51-103)
L52-54> ! @brief Element found in source file. @details Data class representing a single extracted code construct with its metadata.
- fn `def type_label(self) -> str` (L69-103)
  L70-73> ! @brief Return the normalized printable label for element_type. @return Stable uppercase label used in markdown rendering output. @details Maps internal ElementType enum to a string representation for reporting.
  L101> `return labels.get(self.element_type, "UNKNOWN")`

### class `class LanguageSpec` `@dataclass` (L105-116)
L106-108> ! @brief Language recognition pattern specification. @details Holds regex patterns and configuration for parsing a specific programming language.

### fn `def build_language_specs() -> dict` (L117-316)
L118-119> ! @brief Build specifications for all supported languages.
L122> ── Python ──────────────────────────────────────────────────────────
L143> ── C ───────────────────────────────────────────────────────────────
L177> ── C++ ─────────────────────────────────────────────────────────────
L207> ── Rust ────────────────────────────────────────────────────────────
L239> ── JavaScript ──────────────────────────────────────────────────────
L267> ── TypeScript ──────────────────────────────────────────────────────
L300> ── Java ────────────────────────────────────────────────────────────

### class `class SourceAnalyzer` (L670-869)
L846-851> ! @brief Check if position pos is inside a string literal. @param line The line of code. @param pos The column index. @param spec The LanguageSpec instance. @return True if pos is within a string.
- fn `def __init__(self)` `priv` (L675-678) L671> ! @brief Multi-language source file analyzer. @details Analyzes a source file identifying definit...
  L676> ! @brief Initialize analyzer state with language specifications.
- fn `def get_supported_languages(self) -> list` (L679-690) L676> ! @brief Initialize analyzer state with language specifications.
  L680-682> ! @brief Return list of supported languages (without aliases). @return Sorted list of unique language identifiers.
  L689> `return sorted(result)`
- fn `def analyze(self, filepath: str, language: str) -> list` (L691-844)
  L692-698> ! @brief Analyze a source file and return the list of SourceElement found. @param filepath Path to the source file. @param language Language identifier. @return List of SourceElement instances. @throws ValueError If language is not supported. @details Reads file content, detects single/multi-line comments, and matches regex patterns for definitions.
  L701> `raise ValueError(`
  L713> Multi-line comment state
  L721> ── Multi-line comment handling ──────────────────────────
  L738> ── Multi-line comment start ────────────────────────────
  L740> Special handling for Python docstrings and =begin/=pod blocks
  L744> Check not inside a string
  L746> Check if multi-line comment closes on same line
  L758> Python: """ ... """ sulla stessa riga
  L775> ── Single-line comment ───────────────────────────────────
  L779> If comment is the entire line (aside from whitespace)
  L790> Inline comment: add both element and comment
  L800> ── Language patterns ─────────────────────────────────────
  L813> Single-line types: don't search for block
  L830> Limit extract to max 5 lines for readability
  L843> `return elements`

### fn `def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool` `priv` (L845-878)
L846-851> ! @brief Check if position pos is inside a string literal. @param line The line of code. @param pos The column index. @param spec The LanguageSpec instance. @return True if pos is within a string.
L877> `return in_string`

### fn `def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]` `priv` (L879-916)
L880-884> ! @brief Find position of single-line comment, ignoring strings. @param line The line of code. @param spec The LanguageSpec instance. @return Column index of comment start, or None.
L886> `return None`
L903> `return i`
L915> `return None`

### fn `def _find_block_end(self, lines: list, start_idx: int,` `priv` (L917-995)
L919-926> ! @brief Find the end of a block (function, class, struct, etc.). @param lines List of all file lines. @param start_idx Index of the start line. @param language Language identifier. @param first_line Content of the start line. @return 1-based index of the end line. @details Returns the index (1-based) of the final line of the block. Limits search for performance.
L927> Per Python: basato sull'indentazione
L940> `return end`
L942> Per linguaggi con parentesi graffe
L959> `return end + 1`
L961> If no opening braces found, return just the first line
L963> `return start_idx + 1`
L964> `return end`
L966> Per Ruby/Elixir/Lua: basato su end keyword
L975> `return end + 1`
L977> `return start_idx + 1`
L979> Per Haskell: basato sull'indentazione
L992> `return end`
L994> `return start_idx + 1`

### fn `def enrich(self, elements: list, language: str,` (L998-1012)
L996> ── Enrichment methods for LLM-optimized output ───────────────────
L1000-1002> ! @brief Enrich elements with signatures, hierarchy, visibility, inheritance. @details Call after analyze() to add metadata for LLM-optimized markdown output. Modifies elements in-place and returns them. If filepath is provided, also extracts body comments and exit points.
L1011> `return elements`

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L1013-1038)
L1014-1016> ! @brief Extract clean identifiers from name fields. @details Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.
L1021> Try to re-extract the name from the element's extract line
L1022> using the original pattern (which has group 2 as the identifier)
L1030> Take highest non-None non-empty group
L1031> (group 2+ = identifier, group 1 = full match)

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1039-1054)
L1040-1041> ! @brief Extract clean signatures from element extracts.

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1055-1088)
L1056-1058> ! @brief Detect parent-child relationships between elements. @details Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1089-1101)
L1090-1091> ! @brief Extract visibility/access modifiers from elements.

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1102-1147)
L1104-1105> ! @brief Parse visibility modifier from a signature line.
L1108> `return "priv"`
L1110> `return "priv"`
L1111> `return "pub"`
L1114> `return "pub"`
L1116> `return "priv"`
L1118> `return "prot"`
L1120> `return "int"`
L1121> `return None`
L1124> `return "pub"`
L1125> `return "priv"`
L1128> `return "pub"`
L1129> `return "priv"`
L1132> `return "priv"`
L1134> `return "fpriv"`
L1136> `return "pub"`
L1137> `return None`
L1140> `return "pub"`
L1142> `return "priv"`
L1144> `return "prot"`
L1145> `return None`
L1146> `return None`

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1148-1159)
L1149-1150> ! @brief Extract inheritance/implementation info from class-like elements.

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1160-1189)
L1162-1163> ! @brief Parse inheritance info from a class/struct declaration line.
L1166> `return m.group(1).strip() if m else None`
L1175> `return ", ".join(parts) if parts else None`
L1179> `return m.group(1).strip() if m else None`
L1184> `return m.group(1).strip() if m else None`
L1187> `return m.group(1) if m else None`
L1188> `return None`

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1197-1320)
L1199-1201> ! @brief Extract comments and exit points from within function/class bodies. @details Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.
L1204> `return`
L1210> `return`
L1212> Only process definitions that span multiple lines
L1230> Scan the body (lines after the definition line)
L1231> 1-based, skip def line itself
L1245> Multi-line comment tracking within body
L1260> Check for multi-line comment start
L1265> Single-line multi-comment
L1289> Single-line comment (full line)
L1299> Standalone comment line in body
L1305> Inline comment after code
L1310> Exit points

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1322-1333)
L1323-1324> ! @brief Strip comment markers from a single line of comment text.
L1331> `return s`

### fn `def format_markdown(elements: list, filepath: str, language: str,` (L1334-1401)
L1336-1343> ! @brief Format structured analysis output as markdown. @param elements List of SourceElement objects. @param filepath Path to source file. @param language Language key. @param spec_name Human-readable language name. @param total_lines Total line count of the source file. @return Markdown formatted string representing the analysis.
L1351> ── Definitions table ──────────────────────────────────────────────
L1361> Sort by start line
L1369> Escape pipes in signature
L1375> ── Comments section ───────────────────────────────────────────────
L1385> Sort by start line
L1391> Take first line of content, max 80 chars
L1399> `return "\n".join(output_lines)`

### fn `def _md_loc(elem) -> str` `priv` (L1402-1409)
L1403-1404> ! @brief Format element location compactly for markdown.
L1406> `return f"L{elem.line_start}"`
L1407> `return f"L{elem.line_start}-{elem.line_end}"`

### fn `def _md_kind(elem) -> str` `priv` (L1410-1437)
L1411-1412> ! @brief Short kind label for markdown output.
L1435> `return mapping.get(elem.element_type, "unk")`

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1438-1460)
L1439-1441> ! @brief Extract clean text content from a comment element. @details Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.
L1446> Strip comment markers
L1451> Strip multi-line markers
L1458> `return text`

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1461-1477)
L1462-1463> ! @brief Extract clean text lines from a multi-line comment (preserving structure).
L1475> `return cleaned`

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1478-1538)
L1479-1481> ! @brief Build maps that associate comments with their adjacent definitions. @details Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)
L1484> Identify definition elements
L1492> Build adjacency map: comments preceding a definition (within 2 lines)
L1501> Extract file description from first comment(s), skip shebangs
L1506> Skip shebang lines and empty comments
L1514> Skip inline comments (name == "inline")
L1519> Check if this comment precedes a definition within 2 lines
L1526> Stop if we hit another element
L1531> Skip file-level description (already captured)
L1536> `return doc_for_def, standalone_comments, file_description`

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1539-1590)
L1541-1543> ! @brief Render body comments and exit points for a definition element. @details Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.
L1544> Build maps by line number
L1553> Collect all annotated line numbers
L1557> Skip if within an excluded range (child element)
L1571> Merge: show exit point code with comment as context
L1574> Strip inline comment from exit_text if it contains it

### fn `def format_markdown(elements: list, filepath: str, language: str,` (L1591-1790)
L1593-1595> ! @brief Format analysis as compact Markdown optimized for LLM agent consumption. @details Produces token-efficient output with: - File header with language, line count, element summary, and description - Imports in a code block - Hierarchical definitions with line-numbered doc comments - Body comments (L<N>> text) and exit points (L<N>> `return ...`) - Comments grouped with their relevant definitions - Standalone section/region comments preserved as context - Symbol index table for quick reference by line number
L1604> Build comment association maps
L1607> ── Header ────────────────────────────────────────────────────────
L1619> ── Imports ───────────────────────────────────────────────────────
L1632> ── Build decorator map: line -> decorator text ───────────────────
L1638> ── Definitions ───────────────────────────────────────────────────
L1678> Collect associated doc comments for this definition
L1701> For impl blocks, use the full first line as sig
L1709> Show associated doc comment with line number
L1719> Body annotations: comments and exit points
L1720> For containers with children, exclude annotations
L1721> that fall within a child's line range (including
L1722> doc comments that immediately precede the child)
L1727> Extend range to include preceding doc comment
L1736> Children with their doc comments and body annotations
L1758> Child body annotations (indented)
L1764> ── Standalone Comments (section/region markers, TODOs, notes) ────
L1767> Group consecutive comments (within 2 lines of each other)
L1786> Multi-line comment block: show as region

### fn `def main()` (L1838-1955)
L1839> ! @brief Execute the standalone source analyzer CLI command.
L1904> `sys.exit(0)`
L1910> `sys.exit(1)`
L1913> `sys.exit(1)`
L1915> Optional filtering

## Comments
- L2: ! @file source_analyzer.py @brief Multi-language source code analyzer. @details Inspired by tree-sitter, this module analyzes source files across m...
- L52: ! @brief Element found in source file. @details Data class representing a single extracted code construct with its metadata.
- L70: ! @brief Return the normalized printable label for element_type. @return Stable uppercase label used in markdown rendering output. @details Maps in...
- L106: ! @brief Language recognition pattern specification. @details Holds regex patterns and configuration for parsing a specific programming language.
- L118: ! @brief Build specifications for all supported languages.
- L122: ── Python ──────────────────────────────────────────────────────────
- L143: ── C ───────────────────────────────────────────────────────────────
- L177: ── C++ ─────────────────────────────────────────────────────────────
- L207: ── Rust ────────────────────────────────────────────────────────────
- L239: ── JavaScript ──────────────────────────────────────────────────────
- L267: ── TypeScript ──────────────────────────────────────────────────────
- L300: ── Java ────────────────────────────────────────────────────────────
- L332: ── Go ──────────────────────────────────────────────────────────────
- L359: ── Ruby ────────────────────────────────────────────────────────────
- L381: ── PHP ─────────────────────────────────────────────────────────────
- L405: ── Swift ───────────────────────────────────────────────────────────
- L435: ── Kotlin ──────────────────────────────────────────────────────────
- L464: ── Scala ───────────────────────────────────────────────────────────
- L490: ── Lua ─────────────────────────────────────────────────────────────
- L506: ── Shell (Bash) ────────────────────────────────────────────────────
- L526: ── Perl ────────────────────────────────────────────────────────────
- L544: ── Haskell ─────────────────────────────────────────────────────────
- L566: ── Zig ─────────────────────────────────────────────────────────────
- L590: ── Elixir ──────────────────────────────────────────────────────────
- L612: ── C# ──────────────────────────────────────────────────────────────
- L651: Common aliases
- L680: ! @brief Return list of supported languages (without aliases). @return Sorted list of unique language identifiers.
- L692: ! @brief Analyze a source file and return the list of SourceElement found. @param filepath Path to the source file. @param language Language identi...
- L713: Multi-line comment state
- L721: ── Multi-line comment handling ──────────────────────────
- L738-740: ── Multi-line comment start ──────────────────────────── | Special handling for Python docstrings and =begin/=pod blocks
- L744-746: Check not inside a string | Check if multi-line comment closes on same line
- L758: Python: """ ... """ sulla stessa riga
- L775: ── Single-line comment ───────────────────────────────────
- L779: If comment is the entire line (aside from whitespace)
- L790: Inline comment: add both element and comment
- L800: ── Language patterns ─────────────────────────────────────
- L813: Single-line types: don't search for block
- L830: Limit extract to max 5 lines for readability
- L846: ! @brief Check if position pos is inside a string literal. @param line The line of code. @param pos The column index. @param spec The LanguageSpec ...
- L880: ! @brief Find position of single-line comment, ignoring strings. @param line The line of code. @param spec The LanguageSpec instance. @return Colum...
- L919-927: ! @brief Find the end of a block (function, class, struct, etc.). @param lines List of all file l... | Per Python: basato sull'indentazione
- L942: Per linguaggi con parentesi graffe
- L961: If no opening braces found, return just the first line
- L966: Per Ruby/Elixir/Lua: basato su end keyword
- L979: Per Haskell: basato sull'indentazione
- L1000: ! @brief Enrich elements with signatures, hierarchy, visibility, inheritance. @details Call after analyze() to add metadata for LLM-optimized markd...
- L1014: ! @brief Extract clean identifiers from name fields. @details Due to regex group nesting, name may contain the full match expression (e.g. 'class M...
- L1021-1022: Try to re-extract the name from the element's extract line | using the original pattern (which has group 2 as the identifier)
- L1030-1031: Take highest non-None non-empty group | (group 2+ = identifier, group 1 = full match)
- L1040: ! @brief Extract clean signatures from element extracts.
- L1056: ! @brief Detect parent-child relationships between elements. @details Containers (class, struct, module, etc.) remain at depth=0. Non-container ele...
- L1090: ! @brief Extract visibility/access modifiers from elements.
- L1104: ! @brief Parse visibility modifier from a signature line.
- L1149: ! @brief Extract inheritance/implementation info from class-like elements.
- L1162: ! @brief Parse inheritance info from a class/struct declaration line.
- L1190: ── Exit point patterns per language family ──────────────────────
- L1199: ! @brief Extract comments and exit points from within function/class bodies. @details Reads the source file and scans each definition's line range ...
- L1212: Only process definitions that span multiple lines
- L1230: Scan the body (lines after the definition line)
- L1245: Multi-line comment tracking within body
- L1260: Check for multi-line comment start
- L1265: Single-line multi-comment
- L1289: Single-line comment (full line)
- L1299: Standalone comment line in body
- L1305: Inline comment after code
- L1310: Exit points
- L1323: ! @brief Strip comment markers from a single line of comment text.
- L1336: ! @brief Format structured analysis output as markdown. @param elements List of SourceElement objects. @param filepath Path to source file. @param ...
- L1351: ── Definitions table ──────────────────────────────────────────────
- L1361: Sort by start line
- L1369: Escape pipes in signature
- L1375: ── Comments section ───────────────────────────────────────────────
- L1385: Sort by start line
- L1391: Take first line of content, max 80 chars
- L1403: ! @brief Format element location compactly for markdown.
- L1411: ! @brief Short kind label for markdown output.
- L1439: ! @brief Extract clean text content from a comment element. @details Args: comment_elem: SourceElement with comment content max_length: if >0, trun...
- L1446: Strip comment markers
- L1451: Strip multi-line markers
- L1462: ! @brief Extract clean text lines from a multi-line comment (preserving structure).
- L1479: ! @brief Build maps that associate comments with their adjacent definitions. @details Returns: - doc_for_def: dict mapping def line_start -> list o...
- L1484: Identify definition elements
- L1492: Build adjacency map: comments preceding a definition (within 2 lines)
- L1501: Extract file description from first comment(s), skip shebangs
- L1506: Skip shebang lines and empty comments
- L1514: Skip inline comments (name == "inline")
- L1519: Check if this comment precedes a definition within 2 lines
- L1526: Stop if we hit another element
- L1531: Skip file-level description (already captured)
- L1541-1544: ! @brief Render body comments and exit points for a definition element. @details Merges body_comm... | Build maps by line number
- L1553: Collect all annotated line numbers
- L1557: Skip if within an excluded range (child element)
- L1571: Merge: show exit point code with comment as context
- L1574: Strip inline comment from exit_text if it contains it
- L1593: ! @brief Format analysis as compact Markdown optimized for LLM agent consumption. @details Produces token-efficient output with: - File header with...
- L1604: Build comment association maps
- L1607: ── Header ────────────────────────────────────────────────────────
- L1619: ── Imports ───────────────────────────────────────────────────────
- L1632: ── Build decorator map: line -> decorator text ───────────────────
- L1638: ── Definitions ───────────────────────────────────────────────────
- L1678: Collect associated doc comments for this definition
- L1701: For impl blocks, use the full first line as sig
- L1709: Show associated doc comment with line number
- L1719-1722: Body annotations: comments and exit points | For containers with children, exclude annotations | that fall within a child's line range (including | doc comments that immediately precede the child)
- L1727: Extend range to include preceding doc comment
- L1736: Children with their doc comments and body annotations
- L1758: Child body annotations (indented)
- L1764: ── Standalone Comments (section/region markers, TODOs, notes) ────
- L1767: Group consecutive comments (within 2 lines of each other)
- L1786: Multi-line comment block: show as region
- L1799: ── Symbol Index ──────────────────────────────────────────────────
- L1819-1820: Only show sig for functions/methods/classes (not vars/consts | which already show full content in Definitions section)
- L1839: ! @brief Execute the standalone source analyzer CLI command.
- L1915: Optional filtering

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ElementType`|class|pub|19-49|class ElementType(Enum)|
|`ElementType.FUNCTION`|var|pub|23||
|`ElementType.METHOD`|var|pub|24||
|`ElementType.CLASS`|var|pub|25||
|`ElementType.STRUCT`|var|pub|26||
|`ElementType.ENUM`|var|pub|27||
|`ElementType.TRAIT`|var|pub|28||
|`ElementType.INTERFACE`|var|pub|29||
|`ElementType.MODULE`|var|pub|30||
|`ElementType.IMPL`|var|pub|31||
|`ElementType.MACRO`|var|pub|32||
|`ElementType.CONSTANT`|var|pub|33||
|`ElementType.VARIABLE`|var|pub|34||
|`ElementType.TYPE_ALIAS`|var|pub|35||
|`ElementType.IMPORT`|var|pub|36||
|`ElementType.DECORATOR`|var|pub|37||
|`ElementType.COMMENT_SINGLE`|var|pub|38||
|`ElementType.COMMENT_MULTI`|var|pub|39||
|`ElementType.COMPONENT`|var|pub|40||
|`ElementType.PROTOCOL`|var|pub|41||
|`ElementType.EXTENSION`|var|pub|42||
|`ElementType.UNION`|var|pub|43||
|`ElementType.NAMESPACE`|var|pub|44||
|`ElementType.PROPERTY`|var|pub|45||
|`ElementType.SIGNAL`|var|pub|46||
|`ElementType.TYPEDEF`|var|pub|47||
|`SourceElement`|class|pub|51-103|class SourceElement|
|`SourceElement.type_label`|fn|pub|69-103|def type_label(self) -> str|
|`LanguageSpec`|class|pub|105-116|class LanguageSpec|
|`build_language_specs`|fn|pub|117-316|def build_language_specs() -> dict|
|`SourceAnalyzer`|class|pub|670-869|class SourceAnalyzer|
|`SourceAnalyzer.__init__`|fn|priv|675-678|def __init__(self)|
|`SourceAnalyzer.get_supported_languages`|fn|pub|679-690|def get_supported_languages(self) -> list|
|`SourceAnalyzer.analyze`|fn|pub|691-844|def analyze(self, filepath: str, language: str) -> list|
|`_in_string_context`|fn|priv|845-878|def _in_string_context(self, line: str, pos: int, spec: L...|
|`_find_comment`|fn|priv|879-916|def _find_comment(self, line: str, spec: LanguageSpec) ->...|
|`_find_block_end`|fn|priv|917-995|def _find_block_end(self, lines: list, start_idx: int,|
|`enrich`|fn|pub|998-1012|def enrich(self, elements: list, language: str,|
|`_clean_names`|fn|priv|1013-1038|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1039-1054|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1055-1088|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1089-1101|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1102-1147|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1148-1159|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1160-1189|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1197-1320|def _extract_body_annotations(self, elements: list,|
|`_clean_comment_line`|fn|priv|1322-1333|def _clean_comment_line(text: str, spec) -> str|
|`format_markdown`|fn|pub|1334-1401|def format_markdown(elements: list, filepath: str, langua...|
|`_md_loc`|fn|priv|1402-1409|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1410-1437|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1438-1460|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1461-1477|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1478-1538|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1539-1590|def _render_body_annotations(out: list, elem, indent: str...|
|`format_markdown`|fn|pub|1591-1790|def format_markdown(elements: list, filepath: str, langua...|
|`main`|fn|pub|1838-1955|def main()|


---

# token_counter.py | Python | 116L | 7 symbols | 2 imports | 8 comments
> Path: `/home/ogekuri/useReq/src/usereq/token_counter.py`
> ! @file token_counter.py @brief Token and character counting for generated output. @details Uses tiktoken for accurate token counting compatible with OpenAI/Claude models. ...

## Imports
```
import os
import tiktoken
```

## Definitions

### class `class TokenCounter` (L14-44)
- fn `def __init__(self, encoding_name: str = "cl100k_base")` `priv` (L19-24) L15> ! @brief Count tokens using tiktoken encoding (cl100k_base by default). @details Wrapper around t...
  L20-22> ! @brief Initialize token counter with a specific tiktoken encoding. @param encoding_name Name of tiktoken encoding used for tokenization.
- fn `def count_tokens(self, content: str) -> int` (L25-35) L20> ! @brief Initialize token counter with a specific tiktoken encoding. @param encoding_name Name of...
  L26-30> ! @brief Count tokens in content string. @param content The text content to tokenize. @return Integer count of tokens. @details Uses `disallowed_special=()` to allow special tokens in input without raising errors. Returns 0 on failure.
  L32> `return len(self.encoding.encode(content, disallowed_special=()))`
  L34> `return 0`
- fn `def count_chars(content: str) -> int` (L37-44)
  L38-41> ! @brief Count characters in content string. @param content The text string. @return Integer count of characters.
  L42> `return len(content)`

### fn `def count_file_metrics(content: str,` (L45-58)
L47-51> ! @brief Count tokens and chars for a content string. @param content The text content to measure. @param encoding_name The tiktoken encoding name (default: "cl100k_base"). @return Dictionary with keys 'tokens' (int) and 'chars' (int).
L53> `return {`

### fn `def count_files_metrics(file_paths: list,` (L59-87)
L61-66> ! @brief Count tokens and chars for a list of files. @param file_paths List of file paths to process. @param encoding_name The tiktoken encoding name. @return List of dictionaries, each containing 'file', 'tokens', 'chars', and optionally 'error'. @details Iterates through files, reading content and counting metrics. Gracefully handles read errors.
L85> `return results`

### fn `def format_pack_summary(results: list) -> str` (L88-116)
L89-93> ! @brief Format a pack summary string from a list of file metrics. @param results List of metrics dictionaries from count_files_metrics(). @return Formatted summary string with per-file details and totals. @details Generates a human-readable report including icons, per-file stats, and aggregate totals.
L116> `return "\n".join(lines)`

## Comments
- L26: ! @brief Count tokens in content string. @param content The text content to tokenize. @return Integer count of tokens. @details Uses `disallowed_sp...
- L38: ! @brief Count characters in content string. @param content The text string. @return Integer count of characters.
- L47: ! @brief Count tokens and chars for a content string. @param content The text content to measure. @param encoding_name The tiktoken encoding name (...
- L61: ! @brief Count tokens and chars for a list of files. @param file_paths List of file paths to process. @param encoding_name The tiktoken encoding na...
- L89: ! @brief Format a pack summary string from a list of file metrics. @param results List of metrics dictionaries from count_files_metrics(). @return ...

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

