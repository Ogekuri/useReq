"""! @brief CLI entry point implementing the useReq initialization flow.
"""

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

REPO_ROOT = Path(__file__).resolve().parents[2]
"""The absolute path to the repository root."""

RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"
"""The absolute path to the resources directory."""

VERBOSE = False
"""Whether verbose output is enabled."""

DEBUG = False
"""Whether debug output is enabled."""

REQUIREMENTS_TEMPLATE_NAME = "Requirements_Template.md"
"""Name of the packaged requirements template file."""


class ReqError(Exception):
    """! @brief Dedicated exception for expected CLI errors.
    """

    def __init__(self, message: str, code: int = 1) -> None:
        """! @brief Initialize an expected CLI failure payload.
        @param message Human-readable error message.
        @param code Process exit code bound to the failure category.
        """
        super().__init__(message)
        self.message = message
        self.code = code


def log(msg: str) -> None:
    """! @brief Prints an informational message.
    """
    print(msg)


def dlog(msg: str) -> None:
    """! @brief Prints a debug message if debugging is active.
    """
    if DEBUG:
        print("DEBUG:", msg)


def vlog(msg: str) -> None:
    """! @brief Prints a verbose message if verbose mode is active.
    """
    if VERBOSE:
        print(msg)


def _get_available_tags_help() -> str:
    """! @brief Generate available TAGs help text for argument parser.
    @return Formatted multi-line string listing TAGs by language.
    @details Imports format_available_tags from find_constructs module to generate dynamic TAG listing for CLI help display.
    """
    try:
        from .find_constructs import format_available_tags
        return format_available_tags()
    except ImportError:
        return "(tag list unavailable)"


def build_parser() -> argparse.ArgumentParser:
    """! @brief Builds the CLI argument parser.
    """
    version = load_package_version()
    usage = (
        "req -c [-h] [--upgrade] [--uninstall] [--remove] [--update] (--base BASE | --here) "
        "--docs-dir DOCS_DIR --guidelines-dir GUIDELINES_DIR --tests-dir TESTS_DIR --src-dir SRC_DIR [--verbose] [--debug] [--enable-models] [--enable-tools] "
        "[--enable-claude] [--enable-codex] [--enable-gemini] [--enable-github] "
        "[--enable-kiro] [--enable-opencode] [--prompts-use-agents] "
        "[--legacy] [--preserve-models] [--add-guidelines | --upgrade-guidelines] "
        "[--files-tokens FILE ...] [--files-references FILE ...] [--files-compress FILE ...] [--files-find TAG PATTERN FILE ...] "
        "[--references] [--compress] [--find TAG PATTERN] [--enable-line-numbers] [--tokens] "
        f"({version})"
    )
    parser = argparse.ArgumentParser(
        description="Initialize a project with useReq resources.",
        prog="req",
        usage=usage,
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--base", type=Path, help="Directory root of the project to update."
    )
    group.add_argument(
        "--here",
        action="store_true",
        help="Use current working directory as the project root.",
    )
    parser.add_argument(
        "--docs-dir", help="Documentation directory relative to the project root."
    )
    parser.add_argument(
        "--guidelines-dir", help="Technical directory relative to the project root."
    )
    parser.add_argument(
        "--tests-dir", help="Test directory relative to the project root."
    )
    parser.add_argument(
        "--src-dir",
        action="append",
        help="Source directory relative to the project root (repeatable).",
    )
    parser.add_argument(
        "--upgrade", action="store_true", help="Upgrade the tool with uv."
    )
    parser.add_argument(
        "--uninstall", action="store_true", help="Uninstall the tool with uv."
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Re-run the command using .req/config.json.",
    )
    parser.add_argument(
        "--remove", action="store_true", help="Remove resources created by the tool."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show verbose progress messages."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Show debug logs for diagnostics."
    )
    parser.add_argument(
        "--enable-models",
        action="store_true",
        help="Include 'model' in generated prompts/agents when available from CLI configs.",
    )
    parser.add_argument(
        "--enable-tools",
        action="store_true",
        help="Include 'tools' in generated prompts/agents when available from CLI configs.",
    )
    parser.add_argument(
        "--enable-claude",
        action="store_true",
        help="Enable generation of Claude prompts and agents for this run.",
    )
    parser.add_argument(
        "--enable-codex",
        action="store_true",
        help="Enable generation of Codex prompts for this run.",
    )
    parser.add_argument(
        "--enable-gemini",
        action="store_true",
        help="Enable generation of Gemini prompts for this run.",
    )
    parser.add_argument(
        "--enable-github",
        action="store_true",
        help="Enable generation of GitHub prompts and agents for this run.",
    )
    parser.add_argument(
        "--enable-kiro",
        action="store_true",
        help="Enable generation of Kiro prompts and agents for this run.",
    )
    parser.add_argument(
        "--enable-opencode",
        action="store_true",
        help="Enable generation of OpenCode prompts and agents for this run.",
    )
    parser.add_argument(
        "--prompts-use-agents",
        action="store_true",
        help="When set, generate .github and .claude prompt files as agent-only references (agent: req-<name>).",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="When set, enable legacy mode using config-legacy.json files for prompt configuration.",
    )
    parser.add_argument(
        "--preserve-models",
        action="store_true",
        help="When set with --update, preserve existing .req/models.json and bypass --legacy mode.",
    )
    guidelines_group = parser.add_mutually_exclusive_group()
    guidelines_group.add_argument(
        "--add-guidelines",
        action="store_true",
        help="Copy guidelines templates from resources/guidelines/ to --guidelines-dir without overwriting existing files.",
    )
    guidelines_group.add_argument(
        "--upgrade-guidelines",
        action="store_true",
        help="Copy guidelines templates from resources/guidelines/ to --guidelines-dir, overwriting existing files.",
    )
    parser.add_argument(
        "--files-tokens",
        nargs="+",
        metavar="FILE",
        help="Count tokens and chars for the given files (standalone, no --base/--here required).",
    )
    parser.add_argument(
        "--files-references",
        nargs="+",
        metavar="FILE",
        help="Generate LLM reference markdown for the given files (standalone, no --base/--here required).",
    )
    parser.add_argument(
        "--files-compress",
        nargs="+",
        metavar="FILE",
        help="Generate compressed output for the given files (standalone, no --base/--here required).",
    )
    parser.add_argument(
        "--files-find",
        nargs="+",
        metavar="ARG",
        help=f"Find and extract specific constructs: --files-find TAG PATTERN FILE ... (standalone, no --base/--here required). Available tags:\n{_get_available_tags_help()}",
    )
    parser.add_argument(
        "--references",
        action="store_true",
        help="Generate LLM reference markdown for all source files in configured --src-dir directories (requires --base/--here).",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Generate compressed output for all source files in configured --src-dir directories (requires --base/--here).",
    )
    parser.add_argument(
        "--find",
        nargs=2,
        metavar=("TAG", "PATTERN"),
        help="Find and extract specific constructs from configured --src-dir: --find TAG PATTERN (requires --base/--here). For available tags, see --files-find help.",
    )
    parser.add_argument(
        "--enable-line-numbers",
        action="store_true",
        default=False,
        help="Enable line number prefixes (<n>:) in output for --files-compress, --compress, --files-find, and --find (disabled by default).",
    )
    parser.add_argument(
        "--tokens",
        action="store_true",
        help="Count tokens/chars for files directly under --docs-dir (requires --base/--here and --docs-dir).",
    )
    return parser


def parse_args(argv: Optional[list[str]] = None) -> Namespace:
    """! @brief Parses command-line arguments into a namespace.
    """
    return build_parser().parse_args(argv)


def load_package_version() -> str:
    """! @brief Reads the package version from __init__.py.
    """
    init_path = Path(__file__).resolve().parent / "__init__.py"
    text = init_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"\s*$', text, re.M)
    if not match:
        raise ReqError("Error: unable to determine package version", 6)
    return match.group(1)


def maybe_print_version(argv: list[str]) -> bool:
    """! @brief Handles --ver/--version by printing the version.
    """
    if "--ver" in argv or "--version" in argv:
        print(load_package_version())
        return True
    return False


def run_upgrade() -> None:
    """! @brief Executes the upgrade using uv.
    """
    command = [
        "uv",
        "tool",
        "install",
        "usereq",
        "--force",
        "--from",
        "git+https://github.com/Ogekuri/useReq.git",
    ]
    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise ReqError("Error: 'uv' command not found in PATH", 12) from exc
    if result.returncode != 0:
        raise ReqError(
            f"Error: auto-upgrade failed (code {result.returncode})",
            result.returncode,
        )


def run_uninstall() -> None:
    """! @brief Executes the uninstallation using uv.
    """
    command = [
        "uv",
        "tool",
        "uninstall",
        "usereq",
    ]
    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise ReqError("Error: 'uv' command not found in PATH", 12) from exc
    if result.returncode != 0:
        raise ReqError(
            f"Error: uninstall failed (code {result.returncode})",
            result.returncode,
        )


def normalize_release_tag(tag: str) -> str:
    """! @brief Normalizes the release tag by removing a 'v' prefix if present.
    """
    value = (tag or "").strip()
    if value.lower().startswith("v") and len(value) > 1:
        value = value[1:]
    return value.strip()


def parse_version_tuple(version: str) -> tuple[int, ...] | None:
    """! @brief Converts a version into a numeric tuple for comparison.
    @details Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
    """

    cleaned = (version or "").strip()
    if not cleaned:
        return None

    parts = cleaned.split(".")
    numbers: list[int] = []
    for part in parts:
        match = re.match(r"^(\d+)", part)
        if not match:
            break
        try:
            numbers.append(int(match.group(1)))
        except ValueError:
            return None

    return tuple(numbers) if numbers else None


def is_newer_version(current: str, latest: str) -> bool:
    """! @brief Returns True if latest is greater than current.
    """
    current_tuple = parse_version_tuple(current)
    latest_tuple = parse_version_tuple(latest)
    if not current_tuple or not latest_tuple:
        return False

    max_len = max(len(current_tuple), len(latest_tuple))
    current_norm = current_tuple + (0,) * (max_len - len(current_tuple))
    latest_norm = latest_tuple + (0,) * (max_len - len(latest_tuple))
    return latest_norm > current_norm


def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None:
    """! @brief Checks online for a new version and prints a warning.
    @details If the call fails or the response is invalid, it prints nothing and proceeds.
    """

    current_version = load_package_version()
    url = "https://api.github.com/repos/Ogekuri/useReq/releases/latest"

    try:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": f"usereq/{current_version}",
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
        payload = json.loads(body)
        tag = payload.get("tag_name")
        if not isinstance(tag, str) or not tag.strip():
            return

        latest_version = normalize_release_tag(tag)
        if is_newer_version(current_version, latest_version):
            print(
                "A new version of usereq is available: "
                f"current {current_version}, latest {latest_version}. "
                "To upgrade, run: req --upgrade"
            )
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        ValueError,
    ):
        return


def ensure_doc_directory(path: str, project_base: Path) -> None:
    """! @brief Ensures the documentation directory exists under the project base.
    """
    normalized = make_relative_if_contains_project(path, project_base)
    doc_path = project_base / normalized
    resolved = doc_path.resolve(strict=False)
    if not resolved.is_relative_to(project_base):
        raise ReqError("Error: --docs-dir must be under the project base", 5)
    if not doc_path.exists():
        raise ReqError(
            f"Error: the --docs-dir directory '{normalized}' does not exist under {project_base}",
            5,
        )
    if not doc_path.is_dir():
        raise ReqError("Error: --docs-dir must specify a directory, not a file", 5)


def ensure_test_directory(path: str, project_base: Path) -> None:
    """! @brief Ensures the test directory exists under the project base.
    """
    normalized = make_relative_if_contains_project(path, project_base)
    test_path = project_base / normalized
    resolved = test_path.resolve(strict=False)
    if not resolved.is_relative_to(project_base):
        raise ReqError("Error: --tests-dir must be under the project base", 5)
    if not test_path.exists():
        raise ReqError(
            f"Error: the --tests-dir directory '{normalized}' does not exist under {project_base}",
            5,
        )
    if not test_path.is_dir():
        raise ReqError("Error: --tests-dir must specify a directory, not a file", 5)


def ensure_src_directory(path: str, project_base: Path) -> None:
    """! @brief Ensures the source directory exists under the project base.
    """
    normalized = make_relative_if_contains_project(path, project_base)
    src_path = project_base / normalized
    resolved = src_path.resolve(strict=False)
    if not resolved.is_relative_to(project_base):
        raise ReqError("Error: --src-dir must be under the project base", 5)
    if not src_path.exists():
        raise ReqError(
            f"Error: the --src-dir directory '{normalized}' does not exist under {project_base}",
            5,
        )
    if not src_path.is_dir():
        raise ReqError("Error: --src-dir must specify a directory, not a file", 5)


def make_relative_if_contains_project(path_value: str, project_base: Path) -> str:
    """! @brief Normalizes the path relative to the project root when possible.
    """
    if not path_value:
        return ""
    candidate = Path(path_value)
    if not candidate.is_absolute():
        parts = candidate.parts
        if parts and parts[0] == project_base.name and len(parts) > 1:
            candidate = Path(*parts[1:])
        elif project_base.name in parts:
            project_name_index = max(
                idx for idx, part in enumerate(parts) if part == project_base.name
            )
            if project_name_index + 1 < len(parts):
                suffix_candidate = Path(*parts[project_name_index + 1 :])
                suffix_resolved = (project_base / suffix_candidate).resolve(strict=False)
                if suffix_resolved.exists():
                    candidate = suffix_candidate
    if candidate.is_absolute():
        try:
            return str(candidate.relative_to(project_base))
        except ValueError:
            return str(candidate)
    resolved = (project_base / candidate).resolve(strict=False)
    try:
        return str(resolved.relative_to(project_base))
    except ValueError:
        pass
    base_str = str(project_base)
    if path_value.startswith(base_str):
        trimmed = path_value[len(base_str) :].lstrip("/\\")
        return trimmed
    return path_value


def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]:
    """! @brief Resolves the absolute path starting from a normalized value.
    """
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (project_base / candidate).resolve(strict=False)


def format_substituted_path(value: str) -> str:
    """! @brief Uniforms path separators for substitutions.
    """
    if not value:
        return ""
    return value.replace(os.sep, "/")


def compute_sub_path(
    normalized: str, absolute: Optional[Path], project_base: Path
) -> str:
    """! @brief Calculates the relative path to use in tokens.
    """
    if not normalized:
        return ""
    if absolute:
        try:
            rel = absolute.relative_to(project_base)
            return format_substituted_path(str(rel))
        except ValueError:
            return format_substituted_path(normalized)
    return format_substituted_path(normalized)


def save_config(
    project_base: Path,
    guidelines_dir_value: str,
    doc_dir_value: str,
    test_dir_value: str,
    src_dir_values: list[str],
) -> None:
    """! @brief Saves normalized parameters to .req/config.json.
    """
    config_path = project_base / ".req" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "guidelines-dir": guidelines_dir_value,
        "docs-dir": doc_dir_value,
        "tests-dir": test_dir_value,
        "src-dir": src_dir_values,
    }
    config_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def load_config(project_base: Path) -> dict[str, str | list[str]]:
    """! @brief Loads parameters saved in .req/config.json.
    """
    config_path = project_base / ".req" / "config.json"
    if not config_path.is_file():
        raise ReqError(
            "Error: .req/config.json not found in the project root",
            11,
        )
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReqError("Error: .req/config.json is not valid", 11) from exc
    guidelines_dir_value = payload.get("guidelines-dir")
    # Fallback to legacy key names from pre-v0.59 config files.
    doc_dir_value = payload.get("docs-dir") or payload.get("doc-dir")
    test_dir_value = payload.get("tests-dir") or payload.get("test-dir")
    src_dir_value = payload.get("src-dir")
    if not isinstance(guidelines_dir_value, str) or not guidelines_dir_value.strip():
        raise ReqError("Error: missing or invalid 'guidelines-dir' field in .req/config.json", 11)
    if not isinstance(doc_dir_value, str) or not doc_dir_value.strip():
        raise ReqError("Error: missing or invalid 'docs-dir' field in .req/config.json", 11)
    if not isinstance(test_dir_value, str) or not test_dir_value.strip():
        raise ReqError("Error: missing or invalid 'tests-dir' field in .req/config.json", 11)
    if (
        not isinstance(src_dir_value, list)
        or not src_dir_value
        or not all(isinstance(item, str) and item.strip() for item in src_dir_value)
    ):
        raise ReqError("Error: missing or invalid 'src-dir' field in .req/config.json", 11)
    return {
        "guidelines-dir": guidelines_dir_value,
        "docs-dir": doc_dir_value,
        "tests-dir": test_dir_value,
        "src-dir": src_dir_value,
    }


def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str:
    """! @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
    """
    if not guidelines_dir.is_dir():
        return ""

    files = []
    for file_path in sorted(guidelines_dir.iterdir()):
        if file_path.is_file() and not file_path.name.startswith("."):
            try:
                rel_path = file_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/")
                files.append(f"`{rel_str}`")
            except ValueError:
                continue

    # If there are no files, use the directory itself.
    if not files:
        try:
            rel_path = guidelines_dir.relative_to(project_base)
            rel_str = str(rel_path).replace(os.sep, "/") + "/"
            return f"`{rel_str}`"
        except ValueError:
            return ""

    return ", ".join(files)


def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]:
    """! @brief Generates a list of relative file paths (no formatting) for printing.
    @details Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
    """
    if not guidelines_dir.is_dir():
        return []

    items: list[str] = []
    for file_path in sorted(guidelines_dir.iterdir()):
        if file_path.is_file() and not file_path.name.startswith("."):
            try:
                rel_path = file_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/")
                items.append(rel_str)
            except ValueError:
                continue

    # If there are no files, use the directory itself.
    if not items:
        try:
            rel_path = guidelines_dir.relative_to(project_base)
            rel_str = str(rel_path).replace(os.sep, "/") + "/"
            return [rel_str]
        except ValueError:
            return []

    return items


def copy_guidelines_templates(
    guidelines_dest: Path, overwrite: bool = False
) -> int:
    """! @brief Copies guidelines templates from resources/guidelines/ to the target directory.
    @details Args: guidelines_dest: Target directory where templates will be copied overwrite: If True, overwrite existing files; if False, skip existing files Returns: Number of non-hidden files copied; returns 0 when the source directory is empty.
    """
    guidelines_src = RESOURCE_ROOT / "guidelines"
    if not guidelines_src.is_dir():
        vlog(f"Guidelines templates directory not found at {guidelines_src}, skipping")
        return 0

    if not guidelines_dest.is_dir():
        raise ReqError(
            f"Error: target guidelines directory '{guidelines_dest}' does not exist",
            8,
        )

    copied_count = 0
    for src_file in sorted(guidelines_src.iterdir()):
        if src_file.is_file() and not src_file.name.startswith("."):
            dst_file = guidelines_dest / src_file.name
            existed = dst_file.exists()
            if existed and not overwrite:
                vlog(f"SKIPPED (already exists): {dst_file}")
                continue
            shutil.copyfile(src_file, dst_file)
            copied_count += 1
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_file}")

    return copied_count


def make_relative_token(raw: str, keep_trailing: bool = False) -> str:
    """! @brief Normalizes the path token optionally preserving the trailing slash.
    """
    if not raw:
        return ""
    normalized = raw.replace("\\", "/").strip("/")
    if not normalized:
        return ""
    suffix = "/" if keep_trailing and raw.endswith("/") else ""
    return f"{normalized}{suffix}"


def ensure_relative(value: str, name: str, code: int) -> None:
    """! @brief Validates that the path is not absolute and raises an error otherwise.
    """
    if Path(value).is_absolute():
        raise ReqError(
            f"Error: {name} must be a relative path under PROJECT_BASE",
            code,
        )


def apply_replacements(text: str, replacements: Mapping[str, str]) -> str:
    """! @brief Returns text with token replacements applied.
    """
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    return text


def write_text_file(dst: Path, text: str) -> None:
    """! @brief Writes text to disk, ensuring the destination folder exists.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def copy_with_replacements(
    src: Path, dst: Path, replacements: Mapping[str, str]
) -> None:
    """! @brief Copies a file substituting the indicated tokens with their values.
    """
    text = src.read_text(encoding="utf-8")
    updated = apply_replacements(text, replacements)
    write_text_file(dst, updated)


def normalize_description(value: str) -> str:
    """! @brief Normalizes a description by removing superfluous quotes and escapes.
    """
    trimmed = value.strip()
    if len(trimmed) >= 2 and trimmed.startswith('"') and trimmed.endswith('"'):
        trimmed = trimmed[1:-1]
    if len(trimmed) >= 4 and trimmed.startswith('\\"') and trimmed.endswith('\\"'):
        trimmed = trimmed[2:-2]
    return trimmed.replace('\\"', '"')


def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None:
    """! @brief Converts a Markdown prompt to TOML for Gemini.
    """
    if toml_path.exists() and not force:
        raise ReqError(
            f"Destination TOML already exists (use --force to overwrite): {toml_path}",
            3,
        )
    content = md_path.read_text(encoding="utf-8")
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not match:
        raise ReqError("No leading '---' block found at start of Markdown file.", 4)
    frontmatter, rest = match.groups()
    desc = extract_description(frontmatter)
    desc_escaped = desc.replace("\\", "\\\\").replace('"', '\\"')
    rest_text = rest if rest.endswith("\n") else rest + "\n"
    toml_body = [
        f'description = "{desc_escaped}"',
        "",
        'prompt = """',
        rest_text,
        '"""',
        "",
    ]
    toml_path.parent.mkdir(parents=True, exist_ok=True)
    toml_path.write_text("\n".join(toml_body), encoding="utf-8")
    dlog(f"Wrote TOML to: {toml_path}")


def extract_frontmatter(content: str) -> tuple[str, str]:
    """! @brief Extracts front matter and body from Markdown.
    """
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not match:
        raise ReqError("No leading '---' block found at start of Markdown file.", 4)
    # Explicitly return two strings to satisfy type annotation.
    return match.group(1), match.group(2)


def extract_description(frontmatter: str) -> str:
    """! @brief Extracts the description from front matter.
    """
    desc_match = re.search(r"^description:\s*(.*)$", frontmatter, re.M)
    if not desc_match:
        raise ReqError("No 'description:' field found inside the leading block.", 5)
    return normalize_description(desc_match.group(1).strip())


def extract_argument_hint(frontmatter: str) -> str:
    """! @brief Extracts the argument-hint from front matter, if present.
    """
    match = re.search(r"^argument-hint:\s*(.*)$", frontmatter, re.M)
    if not match:
        return ""
    return normalize_description(match.group(1).strip())


def extract_purpose_first_bullet(body: str) -> str:
    """! @brief Returns the first bullet of the Purpose section.
    """
    lines = body.splitlines()
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == "## purpose":
            start_idx = idx + 1
            break
    if start_idx is None:
        raise ReqError("Error: missing '## Purpose' section in prompt.", 7)
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        match = re.match(r"^\s*-\s+(.*)$", line)
        if match:
            return match.group(1).strip()
    raise ReqError("Error: no bullet found under the '## Purpose' section.", 7)


def json_escape(value: str) -> str:
    """! @brief Escapes a string for JSON without external delimiters.
    """
    return json.dumps(value)[1:-1]


def generate_kiro_resources(
    req_dir: Path,
    project_base: Path,
    prompt_rel_path: str,
) -> list[str]:
    """! @brief Generates the resource list for the Kiro agent.
    """
    resources = [f"file://{prompt_rel_path}"]
    if not req_dir.is_dir():
        return resources

    for file_path in sorted(req_dir.iterdir()):
        if file_path.is_file():
            try:
                rel_path = file_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/")
                resources.append(f"file://{rel_str}")
            except ValueError:
                continue

    return resources


def render_kiro_agent(
    template: str,
    name: str,
    description: str,
    prompt: str,
    resources: list[str],
    tools: list[str] | None = None,
    model: Optional[str] = None,
    include_tools: bool = False,
    include_model: bool = False,
) -> str:
    """! @brief Renders the Kiro agent JSON and populates main fields.
    """
    replacements = {
        "%%NAME%%": json_escape(name),
        "%%DESCRIPTION%%": json_escape(description),
        "%%PROMPT%%": json_escape(prompt),
    }
    if "%%RESOURCES%%" in template:
        resources_block = ",\n".join(f'    "{json_escape(item)}"' for item in resources)
        replacements["%%RESOURCES%%"] = resources_block
    for token, replacement in replacements.items():
        template = template.replace(token, replacement)
    try:
        parsed = json.loads(template)
        parsed["resources"] = resources
        if include_model and model is not None:
            parsed["model"] = model
        else:
            parsed.pop("model", None)
        if include_tools:
            parsed_tools = tools if isinstance(tools, list) else []
            parsed["tools"] = parsed_tools
            parsed["allowedTools"] = parsed_tools
        else:
            parsed.pop("tools", None)
            parsed.pop("allowedTools", None)
        return json.dumps(parsed, indent=2, ensure_ascii=False) + "\n"
    except Exception:
        # If parsing fails, return raw template to preserve previous behavior
        return template


def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None:
    """! @brief Replaces tokens in the specified file.
    """
    text = path.read_text(encoding="utf-8")
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    path.write_text(text, encoding="utf-8")


def yaml_double_quote_escape(value: str) -> str:
    """! @brief Minimal escape for a double-quoted string in YAML.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def list_docs_templates() -> list[Path]:
    """! @brief Returns non-hidden files available in resources/docs.
    @return Sorted list of file paths under resources/docs.
    @throws ReqError If resources/docs does not exist or has no non-hidden files.
    """
    candidate = RESOURCE_ROOT / "docs"
    if not candidate.is_dir():
        raise ReqError("Error: no docs templates directory found in resources", 9)
    templates = sorted(
        path for path in candidate.iterdir() if path.is_file() and not path.name.startswith(".")
    )
    if not templates:
        raise ReqError("Error: no docs templates found in resources/docs", 9)
    return templates


def find_requirements_template(docs_templates: list[Path]) -> Path:
    """! @brief Returns the packaged Requirements template file.
    @param docs_templates Runtime docs template file list from resources/docs.
    @return Path to `Requirements_Template.md`.
    @throws ReqError If `Requirements_Template.md` is not present.
    """
    for template_path in docs_templates:
        if template_path.name == REQUIREMENTS_TEMPLATE_NAME:
            return template_path
    raise ReqError(
        f"Error: no {REQUIREMENTS_TEMPLATE_NAME} template found in docs",
        9,
    )


def load_kiro_template() -> tuple[str, dict[str, Any]]:
    """! @brief Loads the Kiro template from centralized models configuration.
    """
    common_dir = RESOURCE_ROOT / "common"
    
    # Try models.json first (this function is called during generation, not with legacy flag check)
    for config_name in ["models.json", "models-legacy.json"]:
        config_file = common_dir / config_name
        if config_file.is_file():
            try:
                all_models = load_settings(config_file)
                if isinstance(all_models, dict):
                    kiro_cfg = all_models.get("kiro")
                    if isinstance(kiro_cfg, dict):
                        agent_template = kiro_cfg.get("agent_template")
                        if isinstance(agent_template, str) and agent_template.strip():
                            return agent_template, kiro_cfg
                        if isinstance(agent_template, dict):
                            try:
                                return (
                                    json.dumps(agent_template, indent=2, ensure_ascii=False),
                                    kiro_cfg,
                                )
                            except Exception:
                                pass
            except Exception as exc:
                dlog(f"Failed parsing {config_file}: {exc}")
                continue
    
    raise ReqError(
        "Error: no Kiro config with 'agent_template' found in centralized models",
        9,
    )


def strip_json_comments(text: str) -> str:
    """! @brief Removes // and /* */ comments to allow JSONC parsing.
    """
    cleaned: list[str] = []
    in_block = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if in_block:
            if "*/" in stripped:
                in_block = False
            continue
        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_block = True
            continue
        if stripped.startswith("//"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def load_settings(path: Path) -> dict[str, Any]:
    """! @brief Loads JSON/JSONC settings, removing comments when necessary.
    """
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = strip_json_comments(raw)
        dlog(f"Parsed {path} after removing comments")
        return json.loads(cleaned)


def load_centralized_models(
    resource_root: Path, 
    legacy_mode: bool = False, 
    preserve_models_path: Optional[Path] = None
) -> dict[str, dict[str, Any] | None]:
    """! @brief Loads centralized models configuration from common/models.json.
    @details Returns a map cli_name -> parsed_json or None if not present. When preserve_models_path is provided and exists, loads from that file, ignoring legacy_mode. Otherwise, when legacy_mode is True, attempts to load models-legacy.json first, falling back to models.json if not found.
    """
    common_dir = resource_root / "common"
    config_file = None
    
    # Priority 1: preserve_models_path if provided and exists
    if preserve_models_path and preserve_models_path.is_file():
        config_file = preserve_models_path
        dlog(f"Using preserved models config: {preserve_models_path}")
    # Priority 2: legacy mode
    elif legacy_mode:
        legacy_candidate = common_dir / "models-legacy.json"
        if legacy_candidate.is_file():
            config_file = legacy_candidate
            dlog(f"Using legacy models config: {legacy_candidate}")
    
    # Fallback: standard models.json
    if config_file is None:
        config_file = common_dir / "models.json"
        if not config_file.is_file():
            dlog(f"Models config not found: {config_file}")
            return {name: None for name in ("claude", "copilot", "opencode", "kiro", "gemini", "codex")}
    
    # Load the centralized configuration
    try:
        all_models = load_settings(config_file)
        dlog(f"Loaded centralized models from: {config_file}")
    except Exception as exc:
        dlog(f"Failed loading centralized models from {config_file}: {exc}")
        return {name: None for name in ("claude", "copilot", "opencode", "kiro", "gemini", "codex")}
    
    # Extract individual CLI configs
    result: dict[str, dict[str, Any] | None] = {}
    for name in ("claude", "copilot", "opencode", "kiro", "gemini", "codex"):
        result[name] = all_models.get(name) if isinstance(all_models, dict) else None
        if result[name]:
            dlog(f"Extracted config for {name}")
    
    return result


def get_model_tools_for_prompt(
    config: dict[str, Any] | None, prompt_name: str, source_name: Optional[str] = None
) -> tuple[Optional[str], Optional[list[str]]]:
    """! @brief Extracts model and tools for the prompt from the CLI config.
    @details Returns (model, tools) where each value can be None if not available.
    """
    if not config:
        return None, None
    prompts = config.get("prompts") or {}
    entry = prompts.get(prompt_name) if isinstance(prompts, dict) else None
    model = None
    tools: Optional[list[str]] = None
    if isinstance(entry, dict):
        model = entry.get("model")
        mode = entry.get("mode")
        if mode:
            usage = config.get("usage_modes") or {}
            mode_entry = usage.get(mode) if isinstance(usage, dict) else None
            if isinstance(mode_entry, dict):
                # Use the unified key name 'tools' across all CLI configs.
                # Accept either a list of strings or a CSV string in the config.json.
                key_name = "tools"
                raw = mode_entry.get(key_name)
                if raw is None:
                    tools = None
                elif isinstance(raw, list):
                    tools = [str(t) for t in raw]
                elif isinstance(raw, str):
                    # Parse comma-separated string into list
                    items = [p.strip() for p in raw.split(",") if p.strip()]
                    tools = items if items else None
                else:
                    tools = None
    return model, tools


def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any:
    """! @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt.
    @details Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
    """
    if not config:
        return None
    prompts = config.get("prompts") or {}
    entry = prompts.get(prompt_name) if isinstance(prompts, dict) else None
    if isinstance(entry, dict):
        mode = entry.get("mode")
        if mode:
            usage = config.get("usage_modes") or {}
            mode_entry = usage.get(mode) if isinstance(usage, dict) else None
            if isinstance(mode_entry, dict):
                return mode_entry.get("tools")
    return None


def format_tools_inline_list(tools: list[str]) -> str:
    """! @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
    """
    safe = [t.replace("'", "\\'") for t in tools]
    quoted = ", ".join(f"'{s}'" for s in safe)
    return f"[{quoted}]"


def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """! @brief Recursively merges dictionaries, prioritizing incoming values.
    """
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge_dict(base[key], value)
        else:
            base[key] = value
    return base


def find_vscode_settings_source() -> Optional[Path]:
    """! @brief Finds the VS Code settings template if available.
    """
    candidate = RESOURCE_ROOT / "vscode" / "settings.json"
    if candidate.is_file():
        return candidate
    return None


def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]:
    """! @brief Generates chat.promptFilesRecommendations from available prompts.
    """
    recommendations: dict[str, bool] = {}
    if not prompts_dir.is_dir():
        return recommendations
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        recommendations[f"req.{prompt_path.stem}"] = True
    return recommendations


def ensure_wrapped(target: Path, project_base: Path, code: int) -> None:
    """! @brief Verifies that the path is under the project root.
    """
    if not target.resolve().is_relative_to(project_base):
        raise ReqError(
            f"Error: safe removal of {target} refused (not under PROJECT_BASE)",
            code,
        )


def save_vscode_backup(req_root: Path, settings_path: Path) -> None:
    """! @brief Saves a backup of VS Code settings if the file exists.
    """
    backup_path = req_root / "settings.json.backup"
    # Never create an absence marker. Backup only if the file exists.
    if settings_path.exists():
        req_root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(settings_path, backup_path)


def restore_vscode_settings(project_base: Path) -> None:
    """! @brief Restores VS Code settings from backup, if present.
    """
    req_root = project_base / ".req"
    backup_path = req_root / "settings.json.backup"
    target_settings = project_base / ".vscode" / "settings.json"
    if backup_path.exists():
        target_settings.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(backup_path, target_settings)
    # Do not remove the target file if no backup exists: restore behavior disabled otherwise.


def prune_empty_dirs(root: Path) -> None:
    """! @brief Removes empty directories under the specified root.
    """
    if not root.is_dir():
        return
    for current, _dirs, _files in os.walk(root, topdown=False):
        current_path = Path(current)
        try:
            if not any(current_path.iterdir()):
                current_path.rmdir()
        except OSError:
            continue


def remove_generated_resources(project_base: Path) -> None:
    """! @brief Removes resources generated by the tool in the project root.
    """
    remove_dirs = [
        project_base / ".gemini" / "commands" / "req",
        project_base / ".claude" / "commands" / "req",
        project_base / ".codex" / "skills" / "req",
        project_base / ".req" / "docs",
    ]
    remove_globs = [
        project_base / ".codex" / "prompts",
        project_base / ".github" / "agents",
        project_base / ".github" / "prompts",
        project_base / ".kiro" / "agents",
        project_base / ".kiro" / "prompts",
        project_base / ".claude" / "agents",
        project_base / ".claude" / "commands",
        project_base / ".opencode" / "agent",
        project_base / ".opencode" / "command",
    ]
    for target in remove_dirs:
        if target.exists():
            ensure_wrapped(target, project_base, 10)
            shutil.rmtree(target)
    for folder in remove_globs:
        if not folder.is_dir():
            continue
        ensure_wrapped(folder, project_base, 10)
        for path in folder.glob("req.*"):
            if path.is_file():
                path.unlink()
    config_path = project_base / ".req" / "config.json"
    if config_path.exists():
        ensure_wrapped(config_path, project_base, 10)
        config_path.unlink()
    req_root = project_base / ".req"
    if req_root.exists():
        ensure_wrapped(req_root, project_base, 10)
        shutil.rmtree(req_root)


def run_remove(args: Namespace) -> None:
    """! @brief Handles the removal of generated resources.
    """
    guidelines_dir = getattr(args, 'guidelines_dir', None)
    doc_dir = getattr(args, 'docs_dir', None)
    test_dir = getattr(args, 'tests_dir', None)
    src_dir = getattr(args, 'src_dir', None)
    if args.update:
        raise ReqError(
            "Error: --remove does not accept --update",
            4,
        )
    if (not getattr(args, "here", False)) and (guidelines_dir or doc_dir or test_dir or src_dir):
        raise ReqError(
            "Error: --remove does not accept --guidelines-dir, --docs-dir, --tests-dir, or --src-dir without --here",
            4,
        )
    if args.base:
        project_base = args.base.resolve()
    else:
        project_base = Path.cwd().resolve()
    if not project_base.exists():
        raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)
    config_path = project_base / ".req" / "config.json"
    if not config_path.is_file():
        raise ReqError(
            "Error: .req/config.json not found in the project root",
            11,
        )

    # After validation and before any removal, check for a new version.
    maybe_notify_newer_version(timeout_seconds=1.0)

    # Do not perform any restore or removal of .vscode/settings.json during removal.
    remove_generated_resources(project_base)
    for root_name in (
        ".gemini",
        ".codex",
        ".kiro",
        ".github",
        ".vscode",
        ".opencode",
        ".claude",
    ):
        prune_empty_dirs(project_base / root_name)


def run(args: Namespace) -> None:
    """! @brief Handles the main initialization flow.
    """
    global VERBOSE, DEBUG
    VERBOSE = args.verbose
    DEBUG = args.debug

    # Main flow: validates input, calculates paths, generates resources.
    if args.remove:
        run_remove(args)
        return

    if args.base:
        project_base = args.base.resolve()
    else:
        project_base = Path.cwd().resolve()
    if not project_base.exists():
        raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)

    guidelines_dir = getattr(args, 'guidelines_dir', None)
    doc_dir = getattr(args, 'docs_dir', None)
    test_dir = getattr(args, 'tests_dir', None)
    src_dir = getattr(args, 'src_dir', None)
    use_here_config = bool(getattr(args, "here", False))

    if args.update and (not use_here_config) and (guidelines_dir or doc_dir or test_dir or src_dir):
        raise ReqError(
            "Error: --update does not accept --guidelines-dir, --docs-dir, --tests-dir, or --src-dir",
            4,
        )
    if (not use_here_config) and (not args.update) and (not guidelines_dir or not doc_dir or not test_dir or not src_dir):
        raise ReqError(
            "Error: --guidelines-dir, --docs-dir, --tests-dir, and --src-dir are required without --update",
            4,
        )

    if use_here_config:
        config = load_config(project_base)
        guidelines_dir_value = config["guidelines-dir"]
        doc_dir_value = config["docs-dir"]
        test_dir_value = config["tests-dir"]
        src_dir_values = config["src-dir"]
    elif args.update:
        config = load_config(project_base)
        guidelines_dir_value = config["guidelines-dir"]
        doc_dir_value = config["docs-dir"]
        test_dir_value = config["tests-dir"]
        src_dir_values = config["src-dir"]
    else:
        guidelines_dir_value = guidelines_dir
        doc_dir_value = doc_dir
        test_dir_value = test_dir
        src_dir_values = src_dir

    if not isinstance(guidelines_dir_value, str) or not isinstance(doc_dir_value, str):
        raise ReqError("Error: invalid docs configuration values", 11)
    if not isinstance(test_dir_value, str):
        raise ReqError("Error: invalid tests configuration value", 11)
    if (
        not isinstance(src_dir_values, list)
        or not src_dir_values
        or not all(isinstance(value, str) for value in src_dir_values)
    ):
        raise ReqError("Error: invalid src configuration values", 11)

    ensure_doc_directory(doc_dir_value, project_base)
    ensure_test_directory(test_dir_value, project_base)
    for src_dir_value in src_dir_values:
        ensure_src_directory(src_dir_value, project_base)

    normalized_guidelines = make_relative_if_contains_project(guidelines_dir_value, project_base)
    normalized_doc = make_relative_if_contains_project(doc_dir_value, project_base)
    normalized_test = make_relative_if_contains_project(test_dir_value, project_base)
    normalized_src_dirs: list[str] = []
    config_src_dirs: list[str] = []
    src_has_trailing_slashes: list[bool] = []
    guidelines_has_trailing_slash = guidelines_dir_value.endswith("/") or guidelines_dir_value.endswith("\\")
    doc_has_trailing_slash = doc_dir_value.endswith("/") or doc_dir_value.endswith("\\")
    test_has_trailing_slash = test_dir_value.endswith("/") or test_dir_value.endswith("\\")
    normalized_guidelines = normalized_guidelines.rstrip("/\\")
    normalized_doc = normalized_doc.rstrip("/\\")
    normalized_test = normalized_test.rstrip("/\\")
    for src_dir_value in src_dir_values:
        has_trailing = src_dir_value.endswith("/") or src_dir_value.endswith("\\")
        normalized_src = make_relative_if_contains_project(src_dir_value, project_base)
        normalized_src = normalized_src.rstrip("/\\")
        normalized_src_dirs.append(normalized_src)
        src_has_trailing_slashes.append(has_trailing)

    ensure_relative(normalized_guidelines, "GUIDELINES_DIR", 5)
    ensure_relative(normalized_doc, "DOCS_DIR", 4)
    ensure_relative(normalized_test, "TESTS_DIR", 4)
    for normalized_src in normalized_src_dirs:
        ensure_relative(normalized_src, "SRC_DIR", 4)

    abs_guidelines = resolve_absolute(normalized_guidelines, project_base)
    abs_doc = resolve_absolute(normalized_doc, project_base)
    abs_test = resolve_absolute(normalized_test, project_base)
    abs_src_dirs = [
        resolve_absolute(normalized_src, project_base)
        for normalized_src in normalized_src_dirs
    ]
    if abs_guidelines and not abs_guidelines.resolve().is_relative_to(project_base):
        raise ReqError("Error: --guidelines-dir must be under the project base", 8)
    if abs_doc and not abs_doc.resolve().is_relative_to(project_base):
        raise ReqError("Error: --docs-dir must be under the project base", 5)
    if abs_test and not abs_test.resolve().is_relative_to(project_base):
        raise ReqError("Error: --tests-dir must be under the project base", 5)
    for abs_src in abs_src_dirs:
        if abs_src and not abs_src.resolve().is_relative_to(project_base):
            raise ReqError("Error: --src-dir must be under the project base", 5)

    config_guidelines = (
        f"{normalized_guidelines}/"
        if guidelines_has_trailing_slash and normalized_guidelines
        else normalized_guidelines
    )
    config_doc = (
        f"{normalized_doc}/"
        if doc_has_trailing_slash and normalized_doc
        else normalized_doc
    )
    config_test = (
        f"{normalized_test}/"
        if test_has_trailing_slash and normalized_test
        else normalized_test
    )
    for normalized_src, has_trailing in zip(
        normalized_src_dirs, src_has_trailing_slashes
    ):
        config_src = f"{normalized_src}/" if has_trailing and normalized_src else normalized_src
        config_src_dirs.append(config_src)

    guidelines_dest = project_base / normalized_guidelines
    if not guidelines_dest.is_dir():
        raise ReqError(
            f"Error: GUIDELINES_DIR directory '{normalized_guidelines}' does not exist under {project_base}",
            8,
        )
    if VERBOSE:
        log(f"OK: technical directory found {guidelines_dest}")

    # Copy guidelines templates if requested (REQ-085, REQ-086, REQ-087, REQ-089)
    if args.add_guidelines or args.copy_guidelines:
        guidelines_src = RESOURCE_ROOT / "guidelines"
        if guidelines_src.is_dir():
            copied = copy_guidelines_templates(guidelines_dest, overwrite=args.copy_guidelines)
            if VERBOSE:
                log(f"OK: copied {copied} guidelines template(s) to {guidelines_dest}")
        else:
            if VERBOSE:
                log(f"OK: no guidelines templates found at {guidelines_src}, skipping copy")

    enable_claude = args.enable_claude
    enable_codex = args.enable_codex
    enable_gemini = args.enable_gemini
    enable_github = args.enable_github
    enable_kiro = args.enable_kiro
    enable_opencode = args.enable_opencode
    if not any(
        (
            enable_claude,
            enable_codex,
            enable_gemini,
            enable_github,
            enable_kiro,
            enable_opencode,
        )
    ):
        parser = build_parser()
        parser.print_help()
        raise ReqError(
            "Error: at least one --enable-* flag is required to generate prompts",
            4,
        )

    # After validation and before any operation that modifies the filesystem, check for a new version.
    maybe_notify_newer_version(timeout_seconds=1.0)

    if not args.update:
        save_config(
            project_base,
            config_guidelines,
            config_doc,
            config_test,
            config_src_dirs,
        )

    sub_guidelines_dir = compute_sub_path(normalized_guidelines, abs_guidelines, project_base)
    sub_test_dir = format_substituted_path(normalized_test).rstrip("/\\")
    token_test_path = f"`{sub_test_dir}/`" if sub_test_dir else ""
    sub_src_paths: list[str] = []
    for normalized_src, abs_src in zip(normalized_src_dirs, abs_src_dirs):
        sub_src = compute_sub_path(normalized_src, abs_src, project_base).rstrip("/\\")
        if sub_src:
            sub_src_paths.append(f"`{sub_src}/`")
    token_src_paths = ", ".join(sub_src_paths)
    if guidelines_has_trailing_slash and sub_guidelines_dir and not sub_guidelines_dir.endswith("/"):
        sub_guidelines_dir += "/"
    token_guidelines_dir = make_relative_token(sub_guidelines_dir, keep_trailing=True)

    req_root = project_base / ".req"
    req_root.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(f"OK: ensured directory {req_root}")

    # Copy models configuration to .req/models.json based on legacy mode (REQ-084)
    # Skip if --preserve-models is active
    if not args.preserve_models:
        models_target = req_root / "models.json"
        if args.legacy:
            legacy_candidate = RESOURCE_ROOT / "common" / "models-legacy.json"
            if legacy_candidate.is_file():
                models_src = legacy_candidate
            else:
                models_src = RESOURCE_ROOT / "common" / "models.json"
        else:
            models_src = RESOURCE_ROOT / "common" / "models.json"
        
        if models_src.is_file():
            shutil.copyfile(models_src, models_target)
            if VERBOSE:
                log(f"OK: copied {models_src} to {models_target}")
    else:
        if VERBOSE:
            log("OK: preserved existing .req/models.json (--preserve-models active)")

    docs_templates = list_docs_templates()
    requirements_template = find_requirements_template(docs_templates)
    req_dir_path = project_base / normalized_doc
    req_dir_empty = not any(req_dir_path.iterdir())
    req_target = project_base / normalized_doc / "requirements.md"
    # Create requirements.md only if the --docs-dir folder is empty.
    if req_dir_empty:
        req_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(requirements_template, req_target)
        if VERBOSE:
            log(
                f"Created {req_target} — update the file with the project requirements. (source: {requirements_template})"
            )

    # Generate the file list for the %%GUIDELINES_FILES%% token.
    guidelines_file_list = generate_guidelines_file_list(project_base / normalized_guidelines, project_base)

    dlog(f"project_base={project_base}")
    dlog(f"DOCS_DIR={normalized_doc}")
    dlog(f"GUIDELINES_DIR={normalized_guidelines}")
    dlog(f"TESTS_DIR={normalized_test}")
    dlog(f"SRC_DIRS={normalized_src_dirs}")
    dlog(f"GUIDELINES_FILE_LIST={guidelines_file_list}")
    dlog(f"SUB_GUIDELINES_DIR={sub_guidelines_dir}")
    dlog(f"TOKEN_GUIDELINES_DIR={token_guidelines_dir}")

    codex_skills_root = None
    target_folders: list[Path] = []
    if enable_codex:
        target_folders.append(project_base / ".codex" / "prompts")
        codex_skills_root = project_base / ".codex" / "skills" / "req"
        target_folders.append(codex_skills_root)
    if enable_github:
        target_folders.extend(
            [
                project_base / ".github" / "agents",
                project_base / ".github" / "prompts",
            ]
        )
    if enable_gemini:
        target_folders.extend(
            [
                project_base / ".gemini" / "commands",
                project_base / ".gemini" / "commands" / "req",
            ]
        )
    if enable_kiro:
        target_folders.extend(
            [
                project_base / ".kiro" / "agents",
                project_base / ".kiro" / "prompts",
            ]
        )
    if enable_claude:
        target_folders.extend(
            [
                project_base / ".claude" / "agents",
                project_base / ".claude" / "commands",
                project_base / ".claude" / "commands" / "req",
            ]
        )
    if enable_opencode:
        target_folders.extend(
            [
                project_base / ".opencode" / "agent",
                project_base / ".opencode" / "command",
            ]
        )
    for folder in target_folders:
        folder.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(
            "OK: ensured provider folders for the requested target CLIs under "
            f"{project_base}"
        )

    prompts_dir = RESOURCE_ROOT / "prompts"
    if not prompts_dir.is_dir():
        raise ReqError(
            f"Error: prompts directory not found at {prompts_dir} (RESOURCE_ROOT/prompts required)",
            9,
        )
    kiro_template, kiro_config = load_kiro_template()
    # Load CLI configs only if requested to include model/tools
    configs: dict[str, dict[str, Any] | None] = {}
    try:
        include_models = args.enable_models
        include_tools = args.enable_tools
        prompts_use_agents = args.prompts_use_agents
    except Exception:
        include_models = False
        include_tools = False
        prompts_use_agents = False
    if include_models or include_tools:
        # Determine preserve_models_path (REQ-082)
        preserve_models_path = None
        if args.preserve_models and args.update:
            candidate_path = project_base / ".req" / "models.json"
            if candidate_path.is_file():
                preserve_models_path = candidate_path
        
        configs = load_centralized_models(
            RESOURCE_ROOT, 
            legacy_mode=args.legacy,
            preserve_models_path=preserve_models_path
        )
    prompts_installed: dict[str, set[str]] = {
        "claude": set(),
        "codex": set(),
        "github": set(),
        "gemini": set(),
        "kiro": set(),
        "opencode": set(),
    }
    modules_installed: dict[str, set[str]] = {
        key: set() for key in prompts_installed.keys()
    }
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        PROMPT = prompt_path.stem
        content = prompt_path.read_text(encoding="utf-8")
        frontmatter, prompt_body = extract_frontmatter(content)
        description = extract_description(frontmatter)
        argument_hint = extract_argument_hint(frontmatter)
        prompt_body = prompt_body if prompt_body.endswith("\n") else prompt_body + "\n"

        # (Removed: bootstrap file inlining and YOLO stop/approval substitution)

        base_replacements = {
            "%%GUIDELINES_FILES%%": guidelines_file_list,
            "%%GUIDELINES_PATH%%": normalized_guidelines,
            "%%DOC_PATH%%": normalized_doc,
            "%%TEST_PATH%%": token_test_path,
            "%%SRC_PATHS%%": token_src_paths,
        }
        prompt_replacements = {
            **base_replacements,
            "%%ARGS%%": "$ARGUMENTS",
        }
        prompt_with_replacements = apply_replacements(content, prompt_replacements)
        prompt_body_replaced = apply_replacements(prompt_body, prompt_replacements)

        # Precompute description and Claude metadata so provider blocks can reuse them safely.
        desc_yaml = yaml_double_quote_escape(description)
        claude_model = None
        claude_tools = None
        if configs:
            claude_model, claude_tools = get_model_tools_for_prompt(
                configs.get("claude"), PROMPT, "claude"
            )

        if enable_codex:
            # .codex/prompts
            dst_codex_prompt = project_base / ".codex" / "prompts" / f"req.{PROMPT}.md"
            existed = dst_codex_prompt.exists()
            write_text_file(dst_codex_prompt, prompt_with_replacements)
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_codex_prompt}")
            prompts_installed["codex"].add(PROMPT)
            modules_installed["codex"].add("prompts")

            # .codex/skills/req/<prompt>/SKILL.md
            if codex_skills_root is not None:
                codex_skill_dir = codex_skills_root / PROMPT
                codex_skill_dir.mkdir(parents=True, exist_ok=True)
                codex_model = None
                codex_tools = None
                if configs:
                    codex_model, codex_tools = get_model_tools_for_prompt(
                        configs.get("codex"), PROMPT, "codex"
                    )
                codex_header_lines = [
                    "---",
                    f"name: req-{PROMPT}",
                    f'description: "{desc_yaml}"',
                ]
                if include_models and codex_model:
                    codex_header_lines.append(f"model: {codex_model}")
                if include_tools and codex_tools:
                    codex_header_lines.append(
                        f"tools: {format_tools_inline_list(codex_tools)}"
                    )
                codex_skill_text = (
                    "\n".join(codex_header_lines) + "\n---\n\n" + prompt_body_replaced
                )
                if not codex_skill_text.endswith("\n"):
                    codex_skill_text += "\n"
                write_text_file(codex_skill_dir / "SKILL.md", codex_skill_text)
                modules_installed["codex"].add("skills")

        if enable_gemini:
            # Gemini TOML
            dst_toml = project_base / ".gemini" / "commands" / "req" / f"{PROMPT}.toml"
            existed = dst_toml.exists()
            md_to_toml(prompt_path, dst_toml, force=existed)
            toml_replacements = {
                "%%GUIDELINES_FILES%%": guidelines_file_list,
                "%%GUIDELINES_PATH%%": normalized_guidelines,
                "%%DOC_PATH%%": normalized_doc,
                "%%TEST_PATH%%": token_test_path,
                "%%SRC_PATHS%%": token_src_paths,
                "%%ARGS%%": "{{args}}",
            }
            replace_tokens(dst_toml, toml_replacements)
            if configs and (include_models or include_tools):
                gem_model, gem_tools = get_model_tools_for_prompt(
                    configs.get("gemini"), PROMPT, "gemini"
                )
                if gem_model or gem_tools:
                    content = dst_toml.read_text(encoding="utf-8")
                    parts = content.split("\n", 1)
                    if len(parts) == 2:
                        first, rest = parts
                        inject_lines: list[str] = []
                        if include_models and gem_model:
                            inject_lines.append(f'model = "{gem_model}"')
                        if include_tools and gem_tools:
                            inject_lines.append(
                                f"tools = {format_tools_inline_list(gem_tools)}"
                            )
                        if inject_lines:
                            content = first + "\n" + "\n".join(inject_lines) + "\n" + rest
                            dst_toml.write_text(content, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_toml}")
            prompts_installed["gemini"].add(PROMPT)
            modules_installed["gemini"].add("commands")

        if enable_kiro:
            # .kiro/prompts
            dst_kiro_prompt = project_base / ".kiro" / "prompts" / f"req.{PROMPT}.md"
            existed = dst_kiro_prompt.exists()
            write_text_file(dst_kiro_prompt, prompt_with_replacements)
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_kiro_prompt}")
            prompts_installed["kiro"].add(PROMPT)
            modules_installed["kiro"].add("prompts")

        if enable_claude:
            # .claude/agents
            dst_claude_agent = project_base / ".claude" / "agents" / f"req.{PROMPT}.md"
            existed = dst_claude_agent.exists()
            claude_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{desc_yaml}"',
            ]
            if include_models and claude_model:
                claude_header_lines.append(f"model: {claude_model}")
            if include_tools and claude_tools:
                claude_header_lines.append(
                    f"tools: {format_tools_inline_list(claude_tools)}"
                )
            claude_text = (
                "\n".join(claude_header_lines) + "\n---\n\n" + prompt_body_replaced
            )
            dst_claude_agent.parent.mkdir(parents=True, exist_ok=True)
            if not claude_text.endswith("\n"):
                claude_text += "\n"
            dst_claude_agent.write_text(claude_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_claude_agent}")
            modules_installed["claude"].add("agents")

        if enable_github:
            # .github/agents
            dst_gh_agent = project_base / ".github" / "agents" / f"req.{PROMPT}.agent.md"
            existed = dst_gh_agent.exists()
            gh_model = None
            gh_tools = None
            if configs:
                gh_model, gh_tools = get_model_tools_for_prompt(
                    configs.get("copilot"), PROMPT, "copilot"
                )
            gh_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{desc_yaml}"',
            ]
            if include_models and gh_model:
                gh_header_lines.append(f"model: {gh_model}")
            if include_tools and gh_tools:
                gh_header_lines.append(f"tools: {format_tools_inline_list(gh_tools)}")
            gh_text = "\n".join(gh_header_lines) + "\n---\n\n" + prompt_body_replaced
            dst_gh_agent.parent.mkdir(parents=True, exist_ok=True)
            if not gh_text.endswith("\n"):
                gh_text += "\n"
            dst_gh_agent.write_text(gh_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_gh_agent}")
            modules_installed["github"].add("agents")

        if enable_github:
            # .github/prompts
            dst_gh_prompt = project_base / ".github" / "prompts" / f"req.{PROMPT}.prompt.md"
            existed = dst_gh_prompt.exists()
            if prompts_use_agents:
                gh_prompt_text = f"---\nagent: req-{PROMPT}\n---\n"
            else:
                gh_header_lines = [
                    "---",
                    f"description: {frontmatter.splitlines()[0].split(':', 1)[1].strip() if 'description:' in frontmatter else description}",
                ]
                if argument_hint:
                    gh_header_lines.append(f"argument-hint: {argument_hint}")
                gh_model = None
                gh_tools = None
                if configs:
                    gh_model, gh_tools = get_model_tools_for_prompt(
                        configs.get("copilot"), PROMPT, "copilot"
                    )
                if include_models and gh_model:
                    gh_header_lines.append(f"model: {gh_model}")
                if include_tools and gh_tools:
                    gh_header_lines.append(f"tools: {format_tools_inline_list(gh_tools)}")
                gh_header = "\n".join(gh_header_lines) + "\n---\n\n"
                gh_prompt_text = gh_header + prompt_body_replaced
            dst_gh_prompt.parent.mkdir(parents=True, exist_ok=True)
            dst_gh_prompt.write_text(gh_prompt_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_gh_prompt}")
            prompts_installed["github"].add(PROMPT)
            modules_installed["github"].add("prompts")

        if enable_kiro:
            # .kiro/agents
            dst_kiro_agent = project_base / ".kiro" / "agents" / f"req.{PROMPT}.json"
            existed = dst_kiro_agent.exists()
            kiro_prompt_rel = f".kiro/prompts/req.{PROMPT}.md"
            kiro_resources = generate_kiro_resources(
                project_base / normalized_doc,
                project_base,
                kiro_prompt_rel,
            )
            kiro_model, kiro_tools = get_model_tools_for_prompt(kiro_config, PROMPT, "kiro")
            kiro_tools_list = (
                list(kiro_tools) if include_tools and isinstance(kiro_tools, list) else None
            )
            agent_content = render_kiro_agent(
                kiro_template,
                name=f"req-{PROMPT}",
                description=description,
                prompt=prompt_body_replaced,
                resources=kiro_resources,
                tools=kiro_tools_list,
                model=kiro_model,
                include_tools=include_tools,
                include_model=include_models,
            )
            dst_kiro_agent.write_text(agent_content, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_kiro_agent}")
            modules_installed["kiro"].add("agents")

        if enable_opencode:
            # .opencode/agent
            dst_opencode_agent = project_base / ".opencode" / "agent" / f"req.{PROMPT}.md"
            existed = dst_opencode_agent.exists()
            opencode_header_lines = ["---", f'description: "{desc_yaml}"', "mode: all"]
            if configs:
                oc_model, _ = get_model_tools_for_prompt(
                    configs.get("opencode"), PROMPT, "opencode"
                )
                oc_tools_raw = get_raw_tools_for_prompt(configs.get("opencode"), PROMPT)
                if include_models and oc_model:
                    opencode_header_lines.append(f"model: {oc_model}")
                if include_tools and oc_tools_raw is not None:
                    if isinstance(oc_tools_raw, list):
                        opencode_header_lines.append(
                            f"tools: {format_tools_inline_list(oc_tools_raw)}"
                        )
                    elif isinstance(oc_tools_raw, str):
                        opencode_header_lines.append(
                            f'tools: "{yaml_double_quote_escape(oc_tools_raw)}"'
                        )
            opencode_text = (
                "\n".join(opencode_header_lines) + "\n---\n\n" + prompt_body_replaced
            )
            dst_opencode_agent.parent.mkdir(parents=True, exist_ok=True)
            if not opencode_text.endswith("\n"):
                opencode_text += "\n"
            dst_opencode_agent.write_text(opencode_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_opencode_agent}")
            modules_installed["opencode"].add("agent")

            # .opencode/command
            dst_opencode_command = (
                project_base / ".opencode" / "command" / f"req.{PROMPT}.md"
            )
            existed = dst_opencode_command.exists()
            if prompts_use_agents:
                command_text = f"---\nagent: req.{PROMPT}\n---\n"
            else:
                command_header_lines = [
                    "---",
                    f'description: "{desc_yaml}"',
                ]
                if argument_hint:
                    command_header_lines.append(
                        f'argument-hint: "{yaml_double_quote_escape(argument_hint)}"'
                    )
                if configs:
                    oc_model, _ = get_model_tools_for_prompt(
                        configs.get("opencode"), PROMPT, "opencode"
                    )
                    oc_tools_raw = get_raw_tools_for_prompt(configs.get("opencode"), PROMPT)
                    if include_models and oc_model:
                        command_header_lines.append(f"model: {oc_model}")
                    if include_tools and oc_tools_raw is not None:
                        if isinstance(oc_tools_raw, list):
                            command_header_lines.append(
                                f"tools: {format_tools_inline_list(oc_tools_raw)}"
                            )
                        elif isinstance(oc_tools_raw, str):
                            command_header_lines.append(
                                f'tools: "{yaml_double_quote_escape(oc_tools_raw)}"'
                            )
                command_text = (
                    "\n".join(command_header_lines) + "\n---\n\n" + prompt_body_replaced
                )
            dst_opencode_command.parent.mkdir(parents=True, exist_ok=True)
            if not command_text.endswith("\n"):
                command_text += "\n"
            dst_opencode_command.write_text(command_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_opencode_command}")
            prompts_installed["opencode"].add(PROMPT)
            modules_installed["opencode"].add("command")

        if enable_claude:
            # .claude/commands/req
            dst_claude_command = (
                project_base / ".claude" / "commands" / "req" / f"{PROMPT}.md"
            )
            existed = dst_claude_command.exists()
            if prompts_use_agents:
                command_header_lines = ["---", f"agent: req-{PROMPT}"]
                claude_command_text = "\n".join(command_header_lines) + "\n---\n"
            else:
                command_header_lines = ["---"]
                if description:
                    command_header_lines.append(f'description: "{desc_yaml}"')
                if argument_hint:
                    command_header_lines.append(
                        f'argument-hint: "{yaml_double_quote_escape(argument_hint)}"'
                    )
                if include_models and claude_model:
                    command_header_lines.append(
                        f'model: "{yaml_double_quote_escape(str(claude_model))}"'
                    )
                if include_tools and claude_tools:
                    try:
                        allowed_csv = ", ".join(str(t) for t in claude_tools)
                    except Exception:
                        allowed_csv = str(claude_tools)
                    command_header_lines.append(
                        f'allowed-tools: "{yaml_double_quote_escape(allowed_csv)}"'
                    )
                claude_command_text = (
                    "\n".join(command_header_lines)
                    + "\n---\n\n"
                    + prompt_body_replaced
                )
            dst_claude_command.parent.mkdir(parents=True, exist_ok=True)
            if not claude_command_text.endswith("\n"):
                claude_command_text += "\n"
            dst_claude_command.write_text(claude_command_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_claude_command}")
            prompts_installed["claude"].add(PROMPT)
            modules_installed["claude"].add("commands")

    templates_target = req_root / "docs"
    if templates_target.exists():
        ensure_wrapped(templates_target, project_base, 10)
        shutil.rmtree(templates_target)
    templates_target.mkdir(parents=True, exist_ok=True)
    for template_file in docs_templates:
        shutil.copyfile(template_file, templates_target / template_file.name)
    if VERBOSE:
        log(
            f"OK: recreated {templates_target} from resources/docs ({len(docs_templates)} files)"
        )

    vscode_settings_src = find_vscode_settings_source()
    if vscode_settings_src:
        vscode_dir = project_base / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)
        target_settings = vscode_dir / "settings.json"

        # Load existing settings (if present) and those from the template.
        existing_settings: dict[str, Any] = {}
        if target_settings.exists():
            try:
                existing_settings = load_settings(target_settings)
            except Exception:
                # If checking/loading fails, consider it empty
                existing_settings = {}

        src_settings = load_settings(vscode_settings_src)

        # Merge without modifying original until sure.
        import copy

        final_settings = copy.deepcopy(existing_settings)
        final_settings = deep_merge_dict(final_settings, src_settings)

        prompt_recs = build_prompt_recommendations(prompts_dir)
        if prompt_recs:
            final_settings["chat.promptFilesRecommendations"] = prompt_recs

        # If final result is identical to existing, do not rewrite nor backup.
        if existing_settings == final_settings:
            if VERBOSE:
                log(f"OK: settings.json already up-to-date in {target_settings}")
        else:
            # If changes are expected, create backup only if file exists.
            if target_settings.exists():
                save_vscode_backup(req_root, target_settings)
            # Write final settings.
            target_settings.write_text(
                json.dumps(final_settings, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            if VERBOSE:
                log(f"OK: merged settings.json in {target_settings}")

    # Final success notification: printed only when the command completed all
    # intended filesystem modifications without raising an exception.
    try:
        resolved_base = str(project_base.resolve())
    except Exception:
        resolved_base = str(project_base)
    print(f"Installation completed successfully in {resolved_base}")

    # Print the discovered directories used for token substitutions
    # as required by REQ-078: one item per line prefixed with '- '.
    guidelines_items = generate_guidelines_file_items(project_base / normalized_guidelines, project_base)

    if guidelines_items:
        for entry in guidelines_items:
            print(f"- {entry}")
    else:
        print("The folder %%GUIDELINES_FILES%% does not contain any files")

    # Build and print a simple installation report table describing which
    # modules were installed for each CLI target. The table is printed in
    # plain ASCII with a header row matching the requirement.
    def _format_install_table(
        installed_map: dict[str, set[str]],
        prompts_map: dict[str, set[str]],
    ) -> tuple[str, str, list[str]]:
        """! @brief Format the installation summary table aligning header, prompts, and rows.
        """

        columns = ("CLI", "Prompts Installed", "Modules Installed")
        widths = [len(value) for value in columns]
        rows: list[tuple[str, str, str]] = []

        for cli_name in sorted(installed_map.keys()):
            modules = installed_map[cli_name]
            prompts = sorted(prompts_map.get(cli_name, ()))
            if not modules and not prompts:
                continue
            prompts_text = ", ".join(prompts) if prompts else "-"
            mods_text = ", ".join(sorted(modules)) if modules else "-"
            widths[0] = max(widths[0], len(cli_name))
            widths[1] = max(widths[1], len(prompts_text))
            widths[2] = max(widths[2], len(mods_text))
            rows.append((cli_name, prompts_text, mods_text))

        def fmt(row: tuple[str, ...]) -> str:
            return " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row))

        header = fmt(columns)
        separator = " | ".join("-" * max(3, widths[idx]) for idx in range(len(columns)))
        if not rows:
            return header, separator, [fmt(("-", "-", "-"))]
        return header, separator, [fmt(r) for r in rows]

    header, separator, rows = _format_install_table(
        modules_installed, prompts_installed
    )
    print(header)
    print(separator)
    for line in rows:
        print(line)


# ── Excluded directories for --references and --compress ──────────────────

EXCLUDED_DIRS = frozenset({
    ".git", ".vscode", "tmp", "temp", ".cache", ".pytest_cache",
    "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".tox", ".mypy_cache", ".ruff_cache",
})
"""Directories excluded from source scanning in --references and --compress."""

# ── Supported source file extensions ──────────────────────────────────────

SUPPORTED_EXTENSIONS = frozenset({
    ".c", ".cpp", ".cs", ".ex", ".go", ".hs", ".java", ".js",
    ".kt", ".lua", ".pl", ".php", ".py", ".rb", ".rs", ".scala",
    ".sh", ".swift", ".ts", ".zig",
})
"""File extensions considered during source directory scanning."""


def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]:
    """! @brief Recursively collect source files from the given directories.
    @details Applies EXCLUDED_DIRS filtering and SUPPORTED_EXTENSIONS matching.
    """
    collected = []
    for src_dir in src_dirs:
        base_path = project_base / src_dir
        if not base_path.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(str(base_path)):
            # Filter out excluded directories (modifies dirnames in-place)
            dirnames[:] = [
                d for d in dirnames if d not in EXCLUDED_DIRS
            ]
            for fname in sorted(filenames):
                _, ext = os.path.splitext(fname)
                if ext.lower() in SUPPORTED_EXTENSIONS:
                    collected.append(os.path.join(dirpath, fname))
    return collected


def _build_ascii_tree(paths: list[str]) -> str:
    """! @brief Build a deterministic tree string from project-relative paths.
    @param paths Project-relative file paths.
    @return Rendered tree rooted at '.'.
    """
    tree: dict[str, dict[str, Any] | None] = {}
    for rel_path in sorted(paths):
        node = tree
        parts = Path(rel_path).parts
        for index, part in enumerate(parts):
            is_leaf = index == len(parts) - 1
            if is_leaf:
                node.setdefault(part, None)
            else:
                child = node.setdefault(part, {})
                if child is None:
                    child = {}
                    node[part] = child
                node = child

    lines = ["."]

    def _emit(
        branch: dict[str, dict[str, Any] | None],
        prefix: str = "",
    ) -> None:
        entries = sorted(branch.items(), key=lambda item: item[0])
        for idx, (name, child) in enumerate(entries):
            last = idx == len(entries) - 1
            connector = "└── " if last else "├── "
            lines.append(f"{prefix}{connector}{name}")
            if isinstance(child, dict) and child:
                _emit(child, prefix + ("    " if last else "│   "))

    _emit(tree)
    return "\n".join(lines)


def _format_files_structure_markdown(files: list[str], project_base: Path) -> str:
    """! @brief Format markdown section containing the scanned files tree.
    @param files Absolute file paths selected for --references processing.
    @param project_base Project root used to normalize relative paths.
    @return Markdown section with heading and fenced tree.
    """
    rel_paths = [Path(path).resolve().relative_to(project_base).as_posix() for path in files]
    tree = _build_ascii_tree(rel_paths)
    return f"# Files Structure\n```\n{tree}\n```"


def _is_standalone_command(args: Namespace) -> bool:
    """! @brief Check if the parsed args contain a standalone file command.
    """
    return bool(
        getattr(args, "files_tokens", None)
        or getattr(args, "files_references", None)
        or getattr(args, "files_compress", None)
        or getattr(args, "files_find", None)
    )


def _is_project_scan_command(args: Namespace) -> bool:
    """! @brief Check if the parsed args contain a project scan command.
    """
    return bool(
        getattr(args, "references", False)
        or getattr(args, "compress", False)
        or getattr(args, "tokens", False)
        or getattr(args, "find", None)
    )


def run_files_tokens(files: list[str]) -> None:
    """! @brief Execute --files-tokens: count tokens for arbitrary files.
    """
    from .token_counter import count_files_metrics, format_pack_summary

    valid_files = []
    for f in files:
        if not os.path.isfile(f):
            print(f"  Warning: skipping (not found): {f}", file=sys.stderr)
        else:
            valid_files.append(f)

    if not valid_files:
        raise ReqError("Error: no valid files provided.", 1)

    results = count_files_metrics(valid_files)
    print(format_pack_summary(results))


def run_files_references(files: list[str]) -> None:
    """! @brief Execute --files-references: generate markdown for arbitrary files.
    """
    from .generate_markdown import generate_markdown

    md = generate_markdown(files, verbose=VERBOSE)
    print(md)


def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None:
    """! @brief Execute --files-compress: compress arbitrary files.
    @param files List of source file paths to compress.
    @param enable_line_numbers If True, emits <n>: prefixes in compressed entries.
    """
    from .compress_files import compress_files

    output = compress_files(
        files,
        include_line_numbers=enable_line_numbers,
        verbose=VERBOSE,
    )
    print(output)


def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None:
    """! @brief Execute --files-find: find constructs in arbitrary files.
    @param args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...].
    @param enable_line_numbers If True, emits <n>: prefixes in output.
    """
    from .find_constructs import find_constructs_in_files

    if len(args_list) < 3:
        raise ReqError(
            "Error: --files-find requires at least TAG, PATTERN, and one FILE.", 1
        )

    tag_filter = args_list[0]
    pattern = args_list[1]
    files = args_list[2:]

    output = find_constructs_in_files(
        files,
        tag_filter,
        pattern,
        include_line_numbers=enable_line_numbers,
        verbose=VERBOSE,
    )
    print(output)


def run_references(args: Namespace) -> None:
    """! @brief Execute --references: generate markdown for project source files.
    """
    from .generate_markdown import generate_markdown

    project_base, src_dirs = _resolve_project_src_dirs(args)
    files = _collect_source_files(src_dirs, project_base)
    if not files:
        raise ReqError("Error: no source files found in configured directories.", 1)
    md = generate_markdown(files, verbose=VERBOSE)
    files_structure = _format_files_structure_markdown(files, project_base)
    print(f"{files_structure}\n\n{md}")


def run_compress_cmd(args: Namespace) -> None:
    """! @brief Execute --compress: compress project source files.
    @param args Parsed CLI arguments namespace.
    """
    from .compress_files import compress_files

    project_base, src_dirs = _resolve_project_src_dirs(args)
    files = _collect_source_files(src_dirs, project_base)
    if not files:
        raise ReqError("Error: no source files found in configured directories.", 1)
    output = compress_files(
        files,
        include_line_numbers=getattr(args, "enable_line_numbers", False),
        verbose=VERBOSE,
    )
    print(output)


def run_find(args: Namespace) -> None:
    """! @brief Execute --find: find constructs in project source files.
    @param args Parsed CLI arguments namespace.
    @throws ReqError If no source files found or no constructs match criteria with available TAGs listing.
    """
    from .find_constructs import find_constructs_in_files

    project_base, src_dirs = _resolve_project_src_dirs(args)
    files = _collect_source_files(src_dirs, project_base)
    if not files:
        raise ReqError("Error: no source files found in configured directories.", 1)

    # args.find is a list [TAG, PATTERN]
    tag_filter, pattern = args.find
    try:
        output = find_constructs_in_files(
            files,
            tag_filter,
            pattern,
            include_line_numbers=getattr(args, "enable_line_numbers", False),
            verbose=VERBOSE,
        )
        print(output)
    except ValueError as e:
        raise ReqError(str(e), 1)


def run_tokens(args: Namespace) -> None:
    """! @brief Execute --tokens: count tokens for files directly in --docs-dir.
    @param args Parsed CLI arguments namespace.
    @details Requires --base/--here and --docs-dir, then delegates reporting to run_files_tokens.
    """
    project_base = _resolve_project_base(args)
    if getattr(args, "here", False):
        config = load_config(project_base)
        docs_dir_value = config["docs-dir"]
    else:
        docs_dir_arg = getattr(args, "docs_dir", None)
        if not docs_dir_arg:
            raise ReqError("Error: --tokens requires --docs-dir.", 1)
        docs_dir_value = str(docs_dir_arg)
    ensure_doc_directory(str(docs_dir_value), project_base)
    normalized_docs_dir = make_relative_if_contains_project(str(docs_dir_value), project_base)
    docs_dir = project_base / normalized_docs_dir
    files = sorted(str(path) for path in docs_dir.iterdir() if path.is_file())
    if not files:
        raise ReqError("Error: no files found in --docs-dir.", 1)
    run_files_tokens(files)


def _resolve_project_base(args: Namespace) -> Path:
    """! @brief Resolve project base path for project-level commands.
    @param args Parsed CLI arguments namespace.
    @return Absolute path of project base.
    @throws ReqError If --base/--here is missing or the resolved path does not exist.
    """
    if not getattr(args, "base", None) and not getattr(args, "here", False):
        raise ReqError(
            "Error: --references, --compress, and --tokens require --base or --here.", 1
        )

    if args.base:
        project_base = args.base.resolve()
    else:
        project_base = Path.cwd().resolve()

    if not project_base.exists():
        raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)
    return project_base


def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]:
    """! @brief Resolve project base and src-dirs for --references/--compress.
    """
    project_base = _resolve_project_base(args)

    if getattr(args, "here", False):
        config = load_config(project_base)
        src_dirs = config.get("src-dir", [])
    else:
        # Source dirs can come from args or from config
        src_dirs = getattr(args, "src_dir", None)
        if not src_dirs:
            config_path = project_base / ".req" / "config.json"
            if config_path.is_file():
                config = load_config(project_base)
                src_dirs = config.get("src-dir", [])
            else:
                raise ReqError(
                    "Error: --src-dir is required or .req/config.json must exist.", 1
                )

    if not src_dirs:
        raise ReqError("Error: no source directories configured.", 1)

    return project_base, src_dirs


def main(argv: Optional[list[str]] = None) -> int:
    """! @brief CLI entry point for console_scripts and `-m` execution.
    @details Returns an exit code (0 success, non-zero on error).
    """
    try:
        global VERBOSE, DEBUG
        argv_list = sys.argv[1:] if argv is None else argv
        if not argv_list:
            build_parser().print_help()
            return 0
        if "--uninstall" in argv_list:
            run_uninstall()
            return 0
        if "--upgrade" in argv_list:
            run_upgrade()
            return 0
        if maybe_print_version(argv_list):
            return 0
        args = parse_args(argv_list)
        VERBOSE = getattr(args, "verbose", False)
        DEBUG = getattr(args, "debug", False)
        # Standalone file commands (no --base/--here required)
        if _is_standalone_command(args):
            if getattr(args, "files_tokens", None):
                run_files_tokens(args.files_tokens)
            elif getattr(args, "files_references", None):
                run_files_references(args.files_references)
            elif getattr(args, "files_compress", None):
                run_files_compress(
                    args.files_compress,
                    enable_line_numbers=getattr(args, "enable_line_numbers", False),
                )
            elif getattr(args, "files_find", None):
                run_files_find(
                    args.files_find,
                    enable_line_numbers=getattr(args, "enable_line_numbers", False),
                )
            return 0
        # Project scan commands (require --base/--here)
        if _is_project_scan_command(args):
            if getattr(args, "references", False):
                run_references(args)
            elif getattr(args, "compress", False):
                run_compress_cmd(args)
            elif getattr(args, "tokens", False):
                run_tokens(args)
            elif getattr(args, "find", None):
                run_find(args)
            return 0
        # Standard init flow requires --base or --here
        if not getattr(args, "base", None) and not getattr(args, "here", False):
            raise ReqError(
                "Error: --base or --here is required for initialization.", 1
            )
        run(args)
    except ReqError as e:
        print(e.message, file=sys.stderr)
        return e.code
    except Exception as e:  # Unexpected error
        print(f"Unexpected error: {e}", file=sys.stderr)
        if DEBUG:
            import traceback

            traceback.print_exc()
        return 1
    return 0
