"""CLI entry point implementing the useReq initialization flow."""

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


class ReqError(Exception):
    """Dedicated exception for expected CLI errors."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


def log(msg: str) -> None:
    """Prints an informational message."""
    print(msg)


def dlog(msg: str) -> None:
    """Prints a debug message if debugging is active."""
    if DEBUG:
        print("DEBUG:", msg)


def vlog(msg: str) -> None:
    """Prints a verbose message if verbose mode is active."""
    if VERBOSE:
        print(msg)


def build_parser() -> argparse.ArgumentParser:
    """Builds the CLI argument parser."""
    version = load_package_version()
    usage = (
        "req -c [-h] [--upgrade] [--uninstall] [--remove] [--update] (--base BASE | --here) "
        "--doc DOC --dir DIR [--verbose] [--debug] [--enable-models] [--enable-tools] "
        f"({version})"
    )
    parser = argparse.ArgumentParser(
        description="Initialize a project with useReq resources.",
        prog="req",
        usage=usage,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--base", type=Path, help="Directory root of the project to update."
    )
    group.add_argument(
        "--here",
        action="store_true",
        help="Use current working directory as the project root.",
    )
    parser.add_argument(
        "--doc",
        help="Directory containing documentation files relative to the project root.",
    )
    parser.add_argument(
        "--dir", help="Technical directory relative to the project root."
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
        "--prompts-use-agents",
        action="store_true",
        help="When set, generate .github and .claude prompt files as agent-only references (agent: req-<name>).",
    )
    parser.add_argument(
        "--enable-workflow",
        action="store_true",
        help="When set, substitute %%WORKFLOW%% with the workflow update instruction in generated prompts.",
    )
    return parser


def parse_args(argv: Optional[list[str]] = None) -> Namespace:
    """Parses command-line arguments into a namespace."""
    return build_parser().parse_args(argv)


def load_package_version() -> str:
    """Reads the package version from __init__.py."""
    init_path = Path(__file__).resolve().parent / "__init__.py"
    text = init_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"\s*$', text, re.M)
    if not match:
        raise ReqError("Error: unable to determine package version", 6)
    return match.group(1)


def maybe_print_version(argv: list[str]) -> bool:
    """Handles --ver/--version by printing the version."""
    if "--ver" in argv or "--version" in argv:
        print(load_package_version())
        return True
    return False


def run_upgrade() -> None:
    """Executes the upgrade using uv."""
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
    """Executes the uninstallation using uv."""
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
    """Normalizes the release tag by removing a 'v' prefix if present."""
    value = (tag or "").strip()
    if value.lower().startswith("v") and len(value) > 1:
        value = value[1:]
    return value.strip()


def parse_version_tuple(version: str) -> tuple[int, ...] | None:
    """Converts a version into a numeric tuple for comparison.

    Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
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
    """Returns True if latest is greater than current."""
    current_tuple = parse_version_tuple(current)
    latest_tuple = parse_version_tuple(latest)
    if not current_tuple or not latest_tuple:
        return False

    max_len = max(len(current_tuple), len(latest_tuple))
    current_norm = current_tuple + (0,) * (max_len - len(current_tuple))
    latest_norm = latest_tuple + (0,) * (max_len - len(latest_tuple))
    return latest_norm > current_norm


def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None:
    """Checks online for a new version and prints a warning.

    If the call fails or the response is invalid, it prints nothing and proceeds.
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
    """Ensures the documentation directory exists under the project base."""
    # First normalize the path using existing logic.
    normalized = make_relative_if_contains_project(path, project_base)
    doc_path = project_base / normalized
    resolved = doc_path.resolve(strict=False)
    if not resolved.is_relative_to(project_base):
        raise ReqError("Error: --doc must be under the project base", 5)
    if not doc_path.exists():
        raise ReqError(
            f"Error: the --doc directory '{normalized}' does not exist under {project_base}",
            5,
        )
    if not doc_path.is_dir():
        raise ReqError(f"Error: --doc must specify a directory, not a file", 5)


def make_relative_if_contains_project(path_value: str, project_base: Path) -> str:
    """Normalizes the path relative to the project root when possible."""
    if not path_value:
        return ""
    candidate = Path(path_value)
    if not candidate.is_absolute():
        parts = candidate.parts
        if parts and parts[0] == project_base.name and len(parts) > 1:
            candidate = Path(*parts[1:])
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
    """Resolves the absolute path starting from a normalized value."""
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (project_base / candidate).resolve(strict=False)


def format_substituted_path(value: str) -> str:
    """Uniforms path separators for substitutions."""
    if not value:
        return ""
    return value.replace(os.sep, "/")


def compute_sub_path(
    normalized: str, absolute: Optional[Path], project_base: Path
) -> str:
    """Calculates the relative path to use in tokens."""
    if not normalized:
        return ""
    if absolute:
        try:
            rel = absolute.relative_to(project_base)
            return format_substituted_path(str(rel))
        except ValueError:
            return format_substituted_path(normalized)
    return format_substituted_path(normalized)


def save_config(project_base: Path, doc_value: str, dir_value: str) -> None:
    """Saves normalized parameters to .req/config.json."""
    config_path = project_base / ".req" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"doc": doc_value, "dir": dir_value}
    config_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def load_config(project_base: Path) -> dict[str, str]:
    """Loads parameters saved in .req/config.json."""
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
    doc_value = payload.get("doc")
    dir_value = payload.get("dir")
    if not isinstance(doc_value, str) or not doc_value.strip():
        raise ReqError("Error: missing or invalid 'doc' field in .req/config.json", 11)
    if not isinstance(dir_value, str) or not dir_value.strip():
        raise ReqError("Error: missing or invalid 'dir' field in .req/config.json", 11)
    return {"doc": doc_value, "dir": dir_value}


def generate_doc_file_list(doc_dir: Path, project_base: Path) -> str:
    """Generates the markdown file list for %%REQ_DOC%% replacement."""
    if not doc_dir.is_dir():
        return ""

    files = []
    for file_path in sorted(doc_dir.iterdir()):
        if file_path.is_file():
            try:
                rel_path = file_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/")
                files.append(f"`{rel_str}`")
            except ValueError:
                continue

    return ", ".join(files)


def generate_dir_list(dir_path: Path, project_base: Path) -> str:
    """Generates the markdown directory list for %%REQ_DIR%% replacement."""
    if not dir_path.is_dir():
        return ""

    subdirs = []
    for subdir_path in sorted(dir_path.iterdir()):
        if subdir_path.is_dir():
            try:
                rel_path = subdir_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/") + "/"
                subdirs.append(f"`{rel_str}`")
            except ValueError:
                continue

    # If there are no subdirectories, use the directory itself.
    if not subdirs:
        try:
            rel_path = dir_path.relative_to(project_base)
            rel_str = str(rel_path).replace(os.sep, "/") + "/"
            return f"`{rel_str}`"
        except ValueError:
            return ""

    return ", ".join(subdirs)


def make_relative_token(raw: str, keep_trailing: bool = False) -> str:
    """Normalizes the path token optionally preserving the trailing slash."""
    if not raw:
        return ""
    normalized = raw.replace("\\", "/").strip("/")
    if not normalized:
        return ""
    suffix = "/" if keep_trailing and raw.endswith("/") else ""
    return f"{normalized}{suffix}"


def ensure_relative(value: str, name: str, code: int) -> None:
    """Validates that the path is not absolute and raises an error otherwise."""
    if Path(value).is_absolute():
        raise ReqError(
            f"Error: {name} must be a relative path under PROJECT_BASE",
            code,
        )


def apply_replacements(text: str, replacements: Mapping[str, str]) -> str:
    """Returns text with token replacements applied."""
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    return text


def write_text_file(dst: Path, text: str) -> None:
    """Writes text to disk, ensuring the destination folder exists."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def copy_with_replacements(
    src: Path, dst: Path, replacements: Mapping[str, str]
) -> None:
    """Copies a file substituting the indicated tokens with their values."""
    text = src.read_text(encoding="utf-8")
    updated = apply_replacements(text, replacements)
    write_text_file(dst, updated)


def normalize_description(value: str) -> str:
    """Normalizes a description by removing superfluous quotes and escapes."""
    trimmed = value.strip()
    if len(trimmed) >= 2 and trimmed.startswith('"') and trimmed.endswith('"'):
        trimmed = trimmed[1:-1]
    if len(trimmed) >= 4 and trimmed.startswith('\\"') and trimmed.endswith('\\"'):
        trimmed = trimmed[2:-2]
    return trimmed.replace('\\"', '"')


def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None:
    """Converts a Markdown prompt to TOML for Gemini."""
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
    """Extracts front matter and body from Markdown."""
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not match:
        raise ReqError("No leading '---' block found at start of Markdown file.", 4)
    # Explicitly return two strings to satisfy type annotation.
    return match.group(1), match.group(2)


def extract_description(frontmatter: str) -> str:
    """Extracts the description from front matter."""
    desc_match = re.search(r"^description:\s*(.*)$", frontmatter, re.M)
    if not desc_match:
        raise ReqError("No 'description:' field found inside the leading block.", 5)
    return normalize_description(desc_match.group(1).strip())


def extract_argument_hint(frontmatter: str) -> str:
    """Extracts the argument-hint from front matter, if present."""
    match = re.search(r"^argument-hint:\s*(.*)$", frontmatter, re.M)
    if not match:
        return ""
    return normalize_description(match.group(1).strip())


def extract_purpose_first_bullet(body: str) -> str:
    """Returns the first bullet of the Purpose section."""
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
    """Escapes a string for JSON without external delimiters."""
    return json.dumps(value)[1:-1]


def generate_kiro_resources(
    doc_dir: Path,
    project_base: Path,
    prompt_rel_path: str,
) -> list[str]:
    """Generates the resource list for the Kiro agent."""
    resources = [f"file://{prompt_rel_path}"]
    if not doc_dir.is_dir():
        return resources

    for file_path in sorted(doc_dir.iterdir()):
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
    """Renders the Kiro agent JSON and populates main fields."""
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
    """Replaces tokens in the specified file."""
    text = path.read_text(encoding="utf-8")
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    path.write_text(text, encoding="utf-8")


def yaml_double_quote_escape(value: str) -> str:
    """Minimal escape for a double-quoted string in YAML."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def find_template_source() -> Path:
    """Returns the template source or raises an error."""
    candidate = RESOURCE_ROOT / "templates"
    if (candidate / "requirements.md").is_file():
        return candidate
    raise ReqError(
        "Error: no requirements.md template found in templates or usetemplates",
        9,
    )


def load_kiro_template() -> tuple[str, dict[str, Any]]:
    """Loads the Kiro template and configuration needed for agents."""
    roots = [RESOURCE_ROOT]
    builtin_root = Path(__file__).resolve().parent / "resources"
    if builtin_root != RESOURCE_ROOT:
        roots.append(builtin_root)

    for root in roots:
        candidate = root / "kiro" / "config.json"
        if candidate.is_file():
            try:
                cfg = load_settings(candidate)
            except Exception as exc:
                dlog(f"Failed parsing kiro/config.json at {candidate}: {exc}")
                cfg = {}
            agent_template = (
                cfg.get("agent_template") if isinstance(cfg, dict) else None
            )
            if isinstance(agent_template, str) and agent_template.strip():
                return agent_template, cfg
            if isinstance(agent_template, dict):
                try:
                    return (
                        json.dumps(agent_template, indent=2, ensure_ascii=False),
                        cfg,
                    )
                except Exception:
                    pass

    raise ReqError(
        "Error: no Kiro config with 'agent_template' found in resources/kiro",
        9,
    )


def strip_json_comments(text: str) -> str:
    """Removes // and /* */ comments to allow JSONC parsing."""
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
    """Loads JSON/JSONC settings, removing comments when necessary."""
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = strip_json_comments(raw)
        dlog(f"Parsed {path} after removing comments")
        return json.loads(cleaned)


def load_cli_configs(resource_root: Path) -> dict[str, dict[str, Any] | None]:
    """Loads config.json files for supported CLIs if present.

    Returns a map cli_name -> parsed_json or None if not present.
    """
    result: dict[str, dict[str, Any] | None] = {}
    for name in ("claude", "copilot", "opencode", "kiro", "gemini"):
        candidate = resource_root / name / "config.json"
        if candidate.is_file():
            try:
                result[name] = load_settings(candidate)
            except Exception:
                dlog(f"Failed loading config for {name}: {candidate}")
                result[name] = None
        else:
            result[name] = None
    return result


def get_model_tools_for_prompt(
    config: dict[str, Any] | None, prompt_name: str, source_name: Optional[str] = None
) -> tuple[Optional[str], Optional[list[str]]]:
    """Extracts model and tools for the prompt from the CLI config.

    Returns (model, tools) where each value can be None if not available.
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
    """Returns the raw value of `usage_modes[mode]['tools']` for the prompt.

    Can return a list of strings, a string, or None depending on how it is
    defined in `config.json`. Does not perform CSV parsing: returns the value
    exactly as present in the configuration file.
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
    """Formats the tools list as inline YAML/TOML/MD: ['a', 'b']."""
    safe = [t.replace("'", "\\'") for t in tools]
    quoted = ", ".join(f"'{s}'" for s in safe)
    return f"[{quoted}]"


def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Recursively merges dictionaries, prioritizing incoming values."""
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge_dict(base[key], value)
        else:
            base[key] = value
    return base


def find_vscode_settings_source() -> Optional[Path]:
    """Finds the VS Code settings template if available."""
    candidate = RESOURCE_ROOT / "vscode" / "settings.json"
    if candidate.is_file():
        return candidate
    return None


def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]:
    """Generates chat.promptFilesRecommendations from available prompts."""
    recommendations: dict[str, bool] = {}
    if not prompts_dir.is_dir():
        return recommendations
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        recommendations[f"req.{prompt_path.stem}"] = True
    return recommendations


def ensure_wrapped(target: Path, project_base: Path, code: int) -> None:
    """Verifies that the path is under the project root."""
    if not target.resolve().is_relative_to(project_base):
        raise ReqError(
            f"Error: safe removal of {target} refused (not under PROJECT_BASE)",
            code,
        )


def save_vscode_backup(req_root: Path, settings_path: Path) -> None:
    """Saves a backup of VS Code settings if the file exists."""
    backup_path = req_root / "settings.json.backup"
    # Never create an absence marker. Backup only if the file exists.
    if settings_path.exists():
        req_root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(settings_path, backup_path)


def restore_vscode_settings(project_base: Path) -> None:
    """Restores VS Code settings from backup, if present."""
    req_root = project_base / ".req"
    backup_path = req_root / "settings.json.backup"
    target_settings = project_base / ".vscode" / "settings.json"
    if backup_path.exists():
        target_settings.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(backup_path, target_settings)
    # Do not remove the target file if no backup exists: restore behavior disabled otherwise.


def prune_empty_dirs(root: Path) -> None:
    """Removes empty directories under the specified root."""
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
    """Removes resources generated by the tool in the project root."""
    remove_dirs = [
        project_base / ".gemini" / "commands" / "req",
        project_base / ".claude" / "commands" / "req",
        project_base / ".req" / "templates",
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
    """Handles the removal of generated resources."""
    if args.doc or args.dir or args.update:
        raise ReqError("Error: --remove does not accept --doc, --dir, or --update", 4)
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
    """Handles the main initialization flow."""
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

    if args.update and (args.doc or args.dir):
        raise ReqError("Error: --update does not accept --doc or --dir", 4)
    if not args.update and (not args.doc or not args.dir):
        raise ReqError("Error: --doc and --dir are required without --update", 4)

    if args.update:
        config = load_config(project_base)
        doc_value = config["doc"]
        dir_value = config["dir"]
    else:
        doc_value = args.doc
        dir_value = args.dir

    ensure_doc_directory(doc_value, project_base)

    normalized_doc = make_relative_if_contains_project(doc_value, project_base)
    normalized_dir = make_relative_if_contains_project(dir_value, project_base)
    doc_has_trailing_slash = doc_value.endswith("/") or doc_value.endswith("\\")
    dir_has_trailing_slash = dir_value.endswith("/") or dir_value.endswith("\\")
    normalized_doc = normalized_doc.rstrip("/\\")
    normalized_dir = normalized_dir.rstrip("/\\")

    ensure_relative(normalized_doc, "REQ_DOC", 4)
    ensure_relative(normalized_dir, "REQ_DIR", 5)

    abs_doc = resolve_absolute(normalized_doc, project_base)
    abs_dir = resolve_absolute(normalized_dir, project_base)
    if abs_doc and not abs_doc.resolve().is_relative_to(project_base):
        raise ReqError("Error: --doc must be under the project base", 5)
    if abs_dir and not abs_dir.resolve().is_relative_to(project_base):
        raise ReqError("Error: --dir must be under the project base", 8)

    config_doc = (
        f"{normalized_doc}/"
        if doc_has_trailing_slash and normalized_doc
        else normalized_doc
    )
    config_dir = (
        f"{normalized_dir}/"
        if dir_has_trailing_slash and normalized_dir
        else normalized_dir
    )

    tech_dest = project_base / normalized_dir
    if not tech_dest.is_dir():
        raise ReqError(
            f"Error: REQ_DIR directory '{normalized_dir}' does not exist under {project_base}",
            8,
        )
    if VERBOSE:
        log(f"OK: technical directory found {tech_dest}")

    # After validation and before any operation that modifies the filesystem, check for a new version.
    maybe_notify_newer_version(timeout_seconds=1.0)

    if not args.update:
        save_config(project_base, config_doc, config_dir)

    sub_req_doc = compute_sub_path(normalized_doc, abs_doc, project_base)
    sub_tech_dir = compute_sub_path(normalized_dir, abs_dir, project_base)
    if dir_has_trailing_slash and sub_tech_dir and not sub_tech_dir.endswith("/"):
        sub_tech_dir += "/"
    token_req_doc = make_relative_token(sub_req_doc)
    token_req_dir = make_relative_token(sub_tech_dir, keep_trailing=True)

    req_root = project_base / ".req"
    req_root.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(f"OK: ensured directory {req_root}")

    templates_src = find_template_source()
    doc_dir_path = project_base / normalized_doc
    doc_dir_empty = not any(doc_dir_path.iterdir())
    doc_target = project_base / normalized_doc / "requirements.md"
    # Create requirements.md only if the --doc folder is empty.
    if doc_dir_empty:
        src_file = templates_src / "requirements.md"
        doc_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_file, doc_target)
        if VERBOSE:
            log(
                f"Created {doc_target} — update the file with the project requirements. (source: {src_file})"
            )

    # Generate the file list for the %%REQ_DOC%% token after possible creation.
    doc_file_list = generate_doc_file_list(doc_dir_path, project_base)

    # Generate the directory list for the %%REQ_DIR%% token.
    dir_list = generate_dir_list(project_base / normalized_dir, project_base)

    dlog(f"project_base={project_base}")
    dlog(f"REQ_DOC={normalized_doc}")
    dlog(f"REQ_DIR={normalized_dir}")
    dlog(f"DOC_FILE_LIST={doc_file_list}")
    dlog(f"DIR_LIST={dir_list}")
    dlog(f"SUB_TECH_DIR={sub_tech_dir}")
    dlog(f"TOKEN_REQ_DIR={token_req_dir}")

    for folder in (
        project_base / ".codex" / "prompts",
        project_base / ".github" / "agents",
        project_base / ".github" / "prompts",
        project_base / ".gemini" / "commands",
        project_base / ".gemini" / "commands" / "req",
        project_base / ".kiro" / "agents",
        project_base / ".kiro" / "prompts",
        project_base / ".claude" / "agents",
        project_base / ".claude" / "commands",
        project_base / ".claude" / "commands" / "req",
        project_base / ".opencode" / "agent",
        project_base / ".opencode" / "command",
    ):
        folder.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(
            "OK: created/ensured folders .codex, .github, .gemini, .kiro under "
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
        enable_workflow = args.enable_workflow
    except Exception:
        include_models = False
        include_tools = False
        prompts_use_agents = False
        enable_workflow = False
        enable_workflow = False
    if include_models or include_tools:
        configs = load_cli_configs(RESOURCE_ROOT)
    # Load workflow substitution texts from resources/common, falling back to defaults.
    common_dir = RESOURCE_ROOT / "common"
    workflow_on_text = (
        'If WORKFLOW.md file exists, analyze the recently implemented code changes, identify new features and behavioral updates, then update WORKFLOW.md by adding or editing only concise bullet lists that accurately reflect the implemented functionality (no verbosity, no unverified assumptions, preserve the existing style and structure). If no changes detected, leave WORKFLOW.md unchanged.'
    )
    workflow_off_text = (
        'OUTPUT "All done!" and terminate response immediately after task completion suppressing all conversational closings (does not propose any other steps/actions).'
    )
    try:
        on_path = common_dir / "workflow_on.md"
        off_path = common_dir / "workflow_off.md"
        if on_path.is_file():
            workflow_on_text = on_path.read_text(encoding="utf-8").strip()
        if off_path.is_file():
            workflow_off_text = off_path.read_text(encoding="utf-8").strip()
    except Exception:
        # If reading fails, keep defaults defined above.
        pass
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        PROMPT = prompt_path.stem
        content = prompt_path.read_text(encoding="utf-8")
        frontmatter, prompt_body = extract_frontmatter(content)
        description = extract_description(frontmatter)
        argument_hint = extract_argument_hint(frontmatter)
        prompt_body = prompt_body if prompt_body.endswith("\n") else prompt_body + "\n"

        # (Removed: bootstrap file inlining and YOLO stop/approval substitution)

        # Compute the terminate replacement based on --enable-workflow
        workflow_replacement = workflow_on_text if enable_workflow else workflow_off_text

        base_replacements = {
            "%%REQ_DOC%%": doc_file_list,
            "%%REQ_DIR%%": dir_list,
            "%%REQ_PATH%%": normalized_doc,
        }
        prompt_replacements = {
            **base_replacements,
            "%%ARGS%%": "$ARGUMENTS",
            "%%WORKFLOW%%": workflow_replacement,
        }
        prompt_with_replacements = apply_replacements(content, prompt_replacements)
        prompt_body_replaced = apply_replacements(prompt_body, prompt_replacements)

        # .codex/prompts
        dst_codex_prompt = project_base / ".codex" / "prompts" / f"req.{PROMPT}.md"
        existed = dst_codex_prompt.exists()
        write_text_file(dst_codex_prompt, prompt_with_replacements)
        if VERBOSE:
            log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_codex_prompt}")

        # Gemini TOML
        dst_toml = project_base / ".gemini" / "commands" / "req" / f"{PROMPT}.toml"
        existed = dst_toml.exists()
        md_to_toml(prompt_path, dst_toml, force=existed)
        toml_replacements = {
            "%%REQ_DOC%%": doc_file_list,
            "%%REQ_DIR%%": dir_list,
            "%%REQ_PATH%%": normalized_doc,
            "%%ARGS%%": "{{args}}",
            "%%WORKFLOW%%": workflow_replacement,
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

        # .kiro/prompts
        dst_kiro_prompt = project_base / ".kiro" / "prompts" / f"req.{PROMPT}.md"
        existed = dst_kiro_prompt.exists()
        write_text_file(dst_kiro_prompt, prompt_with_replacements)
        if VERBOSE:
            log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_kiro_prompt}")

        # .claude/agents
        dst_claude_agent = project_base / ".claude" / "agents" / f"req.{PROMPT}.md"
        existed = dst_claude_agent.exists()
        desc_yaml = yaml_double_quote_escape(description)
        claude_model = None
        claude_tools = None
        if configs:
            claude_model, claude_tools = get_model_tools_for_prompt(
                configs.get("claude"), PROMPT, "claude"
            )
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
                "\n".join(command_header_lines) + "\n---\n\n" + prompt_body_replaced
            )
        dst_claude_command.parent.mkdir(parents=True, exist_ok=True)
        if not claude_command_text.endswith("\n"):
            claude_command_text += "\n"
        dst_claude_command.write_text(claude_command_text, encoding="utf-8")
        if VERBOSE:
            log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_claude_command}")

    templates_target = req_root / "templates"
    if templates_target.exists():
        ensure_wrapped(templates_target, project_base, 10)
        shutil.rmtree(templates_target)
    shutil.copytree(templates_src, templates_target)
    if VERBOSE:
        log(
            f"OK: recreated {templates_target} from {templates_src} (previous contents removed)"
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


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point for console_scripts and `-m` execution.

    Returns an exit code (0 success, non-zero on error).
    """
    try:
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
