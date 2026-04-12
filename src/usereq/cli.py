"""!
@file cli.py
@brief CLI entry point implementing the useReq initialization flow.
@details Handles argument parsing, configuration management, and execution of useReq commands.
@author GitHub Copilot
@version 0.0.70
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import os
import platform
import re
import shutil
import sys
import subprocess
import textwrap
import time
import urllib.error
import urllib.request
import yaml
from argparse import Namespace
from pathlib import Path
from typing import Any, Mapping, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
"""! @brief The absolute path to the repository root."""

RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"
"""! @brief The absolute path to the resources directory."""

VERBOSE = False
"""! @brief Whether verbose output is enabled."""

DEBUG = False
"""! @brief Whether debug output is enabled."""

REQUIREMENTS_TEMPLATE_NAME = "Requirements_Template.md"
"""! @brief Name of the packaged requirements template file."""

PERSISTED_UPDATE_FLAG_KEYS = ("preserve-models",)
"""! @brief Config keys persisted for install/update boolean flags (SRS-288)."""

VALID_PROVIDERS = frozenset(
    {"codex", "claude", "gemini", "github", "kiro", "opencode", "pi"}
)
"""! @brief Valid provider names accepted by ``--provider`` specs (SRS-275, SRS-353, SRS-354)."""

VALID_ARTIFACTS = frozenset({"prompts", "agents", "skills"})
"""! @brief Valid artifact type tokens accepted in ``--provider`` specs (SRS-275)."""

VALID_PROVIDER_OPTIONS = frozenset(
    {"enable-models", "enable-tools", "prompts-use-agents", "legacy"}
)
"""! @brief Valid per-provider option tokens accepted in ``--provider`` specs (SRS-275)."""

PROVIDER_DIR_MAP: dict[str, list[str]] = {
    "claude": [".claude/commands", ".claude/agents", ".claude/skills"],
    "gemini": [".gemini/commands", ".gemini/skills"],
    "github": [".github/prompts", ".github/agents", ".github/skills"],
    "codex": [".codex/prompts", ".codex/skills"],
    "kiro": [".kiro/prompts", ".kiro/agents", ".kiro/skills"],
    "opencode": [".opencode/agent", ".opencode/command", ".opencode/skill"],
    "pi": [".pi/prompts", ".pi/skills"],
}
"""! @brief Provider-to-directory mapping for worktree copy operations (SRS-325, SRS-353, SRS-354)."""

INVALID_WT_NAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f\s]')
"""! @brief Regex matching characters invalid in both Linux and Windows directory names."""


def parse_provider_spec(spec: str) -> tuple[str, set[str], set[str]]:
    """!
    @brief Parse a single ``--provider`` SPEC string into its components.
    @param spec The raw SPEC string in format ``PROVIDER:ARTIFACTS[:OPTIONS]``.
    @return Tuple of (provider_name, artifacts_set, options_set).
    @throws ReqError If the SPEC contains unknown provider, artifact, or option tokens (SRS-278).
    @details Splits on ``:``, validates each component against the known sets,
    and returns normalized lower-case values.  Commas separate multiple
    artifacts and options within their respective fields.
    @see SRS-275, SRS-276, SRS-278
    """
    parts = spec.split(":")
    if len(parts) < 2 or len(parts) > 3:
        raise ReqError(
            f"Error: invalid --provider spec '{spec}': expected PROVIDER:ARTIFACTS[:OPTIONS]",
            1,
        )
    provider = parts[0].strip().lower()
    if provider not in VALID_PROVIDERS:
        raise ReqError(
            f"Error: unknown provider '{provider}' in --provider spec '{spec}'; "
            f"valid providers: {', '.join(sorted(VALID_PROVIDERS))}",
            1,
        )
    raw_artifacts = [a.strip().lower() for a in parts[1].split(",") if a.strip()]
    if not raw_artifacts:
        raise ReqError(
            f"Error: --provider spec '{spec}' must list at least one artifact type",
            1,
        )
    for artifact in raw_artifacts:
        if artifact not in VALID_ARTIFACTS:
            raise ReqError(
                f"Error: unknown artifact '{artifact}' in --provider spec '{spec}'; "
                f"valid artifacts: {', '.join(sorted(VALID_ARTIFACTS))}",
                1,
            )
    artifacts: set[str] = set(raw_artifacts)
    options: set[str] = set()
    if len(parts) == 3:
        raw_options = [o.strip().lower() for o in parts[2].split(",") if o.strip()]
        for option in raw_options:
            if option not in VALID_PROVIDER_OPTIONS:
                raise ReqError(
                    f"Error: unknown option '{option}' in --provider spec '{spec}'; "
                    f"valid options: {', '.join(sorted(VALID_PROVIDER_OPTIONS))}",
                    1,
                )
        options = set(raw_options)
    return provider, artifacts, options


def resolve_provider_configs(
    provider_specs: list[str],
) -> dict[str, dict[str, Any]]:
    """!
    @brief Resolve per-provider configurations from ``--provider`` specs only.
    @param provider_specs List of raw ``--provider`` SPEC strings.
    @return Dict mapping each supported provider name to a config dict with keys:
      ``enabled`` (bool), ``prompts`` (bool), ``agents`` (bool), ``skills`` (bool),
      ``enable-models`` (bool), ``enable-tools`` (bool), ``prompts-use-agents`` (bool),
      ``legacy`` (bool).
    @details ``--provider`` specs are the sole mechanism for provider/artifact/option
    configuration (SRS-275, SRS-276).  All providers start disabled with all options
    inactive; each spec enables its provider and activates listed artifacts and options.
    @see SRS-275, SRS-276
    """
    # Initialize all providers as disabled with inactive options.
    configs: dict[str, dict[str, Any]] = {}
    for prov in sorted(VALID_PROVIDERS):
        configs[prov] = {
            "enabled": False,
            "prompts": False,
            "agents": False,
            "skills": False,
            "enable-models": False,
            "enable-tools": False,
            "prompts-use-agents": False,
            "legacy": False,
        }

    # Apply --provider specs.
    for spec_str in provider_specs:
        provider, artifacts, options = parse_provider_spec(spec_str)
        cfg = configs[provider]
        cfg["enabled"] = True
        if "prompts" in artifacts:
            cfg["prompts"] = True
        if "agents" in artifacts:
            cfg["agents"] = True
        if "skills" in artifacts:
            cfg["skills"] = True
        if "enable-models" in options:
            cfg["enable-models"] = True
        if "enable-tools" in options:
            cfg["enable-tools"] = True
        if "prompts-use-agents" in options:
            cfg["prompts-use-agents"] = True
        if "legacy" in options:
            cfg["legacy"] = True

    return configs


ANSI_BRIGHT_RED = "\033[91m"
"""! @brief ANSI escape prefix for bright red terminal output."""

ANSI_BRIGHT_GREEN = "\033[92m"
"""! @brief ANSI escape prefix for bright green terminal output."""

ANSI_RESET = "\033[0m"
"""! @brief ANSI escape sequence that resets terminal style."""

RELEASE_CHECK_TIMEOUT_SECONDS = 2.0
"""! @brief Hardcoded default timeout for startup release-check HTTP calls."""

RELEASE_CHECK_IDLE_DELAY_SECONDS = 3600
"""! @brief Hardcoded startup release-check idle-delay in seconds."""

RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS = 86400
"""! @brief Hardcoded startup release-check idle-delay in seconds for API rate limiting."""

TOOL_PROGRAM_NAME = "usereq"
"""! @brief Hardcoded configurable tool identifier used by uv install/uninstall commands."""

RELEASE_CHECK_PROGRAM_NAME = TOOL_PROGRAM_NAME
"""! @brief Program identifier used in release-check idle-state cache directory."""

GITHUB_REPOSITORY_OWNER = "Ogekuri"
"""! @brief Hardcoded GitHub owner used by upgrade and release-check endpoints."""

GITHUB_REPOSITORY_NAME = "useReq"
"""! @brief Hardcoded GitHub repository used by upgrade and release-check endpoints."""

RELEASE_CHECK_IDLE_CACHE_ROOT_DIRNAME = ".cache"
"""! @brief Root cache directory name located under `$HOME`."""

RELEASE_CHECK_IDLE_FILENAME = "check_version_idle-time.json"
"""! @brief Canonical release-check idle-state JSON filename."""

GITHUB_RELEASES_LATEST_URL = (
    f"https://api.github.com/repos/{GITHUB_REPOSITORY_OWNER}/"
    f"{GITHUB_REPOSITORY_NAME}/releases/latest"
)
"""! @brief Hardcoded GitHub API endpoint for latest-release resolution."""

GITHUB_UPGRADE_SOURCE = (
    f"git+https://github.com/{GITHUB_REPOSITORY_OWNER}/{GITHUB_REPOSITORY_NAME}.git"
)
"""! @brief Hardcoded git source used by uv self-upgrade command."""

FORCE_ONLINE_RELEASE_CHECK = False
"""! @brief Startup-scoped override that bypasses release-check idle-state gating when enabled."""


class ReqError(Exception):
    """! @brief Dedicated exception for expected CLI errors.
    @details This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.
    """

    def __init__(self, message: str, code: int = 1) -> None:
        """!
        @brief Initialize an expected CLI failure payload.
                @param message Human-readable error message.
                @param code Process exit code bound to the failure category.
        @details Implements the __init__ function behavior with deterministic control flow.
        @return {None} Function return value.
        """
        super().__init__(message)
        self.message = message
        self.code = code


def log(msg: str) -> None:
    """!
    @brief Prints an informational message.
        @param msg The message string to print.
    @details Implements the log function behavior with deterministic control flow.
    @return {None} Function return value.
    """
    print(msg)


def dlog(msg: str) -> None:
    """!
    @brief Prints a debug message if debugging is active.
        @param msg The debug message string to print.
    @details Implements the dlog function behavior with deterministic control flow.
    @return {None} Function return value.
    """
    if DEBUG:
        print("DEBUG:", msg)


def vlog(msg: str) -> None:
    """!
    @brief Prints a verbose message if verbose mode is active.
        @param msg The verbose message string to print.
    @details Implements the vlog function behavior with deterministic control flow.
    @return {None} Function return value.
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
    @return Configured ArgumentParser instance.
    @details Defines all supported CLI arguments, flags, and help texts. Provider enablement,
    artifact selection, and per-provider options are configured exclusively via the repeatable
    ``--provider SPEC`` argument (SRS-275, SRS-034).
    """
    version = load_package_version()
    usage = (
        "req -c [-h] [--upgrade] [--uninstall] [--remove] [--update] (--base BASE | --here) "
        "--docs-dir DOCS_DIR --guidelines-dir GUIDELINES_DIR --tests-dir TESTS_DIR --src-dir SRC_DIR [--verbose] [--debug] "
        "[--provider PROVIDER:ARTIFACTS[:OPTIONS]] "
        "[--preserve-models] [--add-guidelines | --upgrade-guidelines] "
        "[--files-tokens FILE ...] [--files-references FILE ...] [--files-compress FILE ...] [--files-find TAG PATTERN FILE ...] "
        "[--references] [--compress] [--find TAG PATTERN] [--enable-line-numbers] [--tokens] "
        "[--test-static-check {dummy,pylance,ruff,command} [FILES...]] "
        "[--git-check] [--docs-check] [--git-wt-name] [--git-wt-create WT_NAME] [--git-wt-delete WT_NAME] [--git-path] [--get-base-path] "
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
        "--preserve-models",
        action="store_true",
        help="When set with --update, preserve existing .req/models.json.",
    )
    parser.add_argument(
        "--provider",
        action="append",
        metavar="SPEC",
        dest="provider_specs",
        help=(
            "Per-provider artifact and option configuration (repeatable). "
            "Format: PROVIDER:ARTIFACTS[:OPTIONS]. "
            "PROVIDER: codex|claude|gemini|github|kiro|opencode|pi. "
            "ARTIFACTS: comma-separated from {prompts,agents,skills}. "
            "OPTIONS: comma-separated from {enable-models,enable-tools,prompts-use-agents,legacy}."
        ),
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
        help="Generate LLM reference markdown for all source files in configured src-dir directories (here-only project scan; --here implied; --base forbidden).",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Generate compressed output for all source files in configured src-dir directories (here-only project scan; --here implied; --base forbidden).",
    )
    parser.add_argument(
        "--find",
        nargs=2,
        metavar=("TAG", "PATTERN"),
        help="Find and extract specific constructs from configured src-dir: --find TAG PATTERN (here-only project scan; --here implied; --base forbidden). For available tags, see --files-find help.",
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
        help="Count tokens/chars for REQUIREMENTS.md, WORKFLOW.md, and REFERENCES.md in configured docs-dir (here-only project scan; --here implied; --base forbidden).",
    )
    parser.add_argument(
        "--test-static-check",
        nargs=argparse.REMAINDER,
        metavar="ARG",
        dest="test_static_check",
        help=(
            "Run static analysis: --test-static-check <subcommand> [FILES...]. "
            "Subcommands: dummy, pylance, ruff, command <cmd>. "
            "[FILES] may be files, directories, or glob patterns including ** (standalone, no --base/--here required)."
        ),
    )
    parser.add_argument(
        "--enable-static-check",
        action="append",
        metavar="SPEC",
        dest="enable_static_check",
        default=None,
        help=(
            "Configure a static-check tool for a language during install/update. "
            "SPEC format: LANG=MODULE[,CMD[,PARAM...]]. "
            "MODULE: Dummy, Pylance, Ruff, Command (case-insensitive). "
            "LANG: Python, C, C++, C#, Rust, JavaScript, TypeScript, Java, Go, Ruby, "
            "PHP, Swift, Kotlin, Scala, Lua, Shell, Perl, Haskell, Zig, Elixir (case-insensitive). "
            "For Command, CMD is the binary and subsequent tokens are params saved in config.json; "
            "tokens containing commas must be wrapped in double quotes. "
            "Repeatable: multiple flags per language append multiple entries. "
            "Example: --enable-static-check Python=Pylance "
            "--enable-static-check C=Command,/usr/bin/cppcheck,--check-library"
        ),
    )
    parser.add_argument(
        "--files-static-check",
        nargs="+",
        metavar="FILE",
        dest="files_static_check",
        help=(
            "Run static analysis on explicit files using tools configured in .req/config.json. "
            "Detects language from file extension; skips files with no configured tool. "
            "Standalone (no --base/--here required; uses --here/--base if provided, else CWD). "
            "Example: --files-static-check src/main.c src/utils.py"
        ),
    )
    parser.add_argument(
        "--static-check",
        action="store_true",
        default=False,
        dest="static_check",
        help=(
            "Run static analysis on all source files in configured src-dir directories "
            "(here-only project scan; --here implied; --base forbidden). Uses the same file-collection logic as --references "
            "and --compress. Tools are loaded from the 'static-check' section of .req/config.json."
        ),
    )
    parser.add_argument(
        "--git-check",
        action="store_true",
        default=False,
        dest="git_check",
        help=(
            "Check git repository status: clean work tree and valid HEAD "
            "(here-only; --here implied; --base forbidden)."
        ),
    )
    parser.add_argument(
        "--docs-check",
        action="store_true",
        default=False,
        dest="docs_check",
        help=(
            "Check existence of REQUIREMENTS.md, WORKFLOW.md, and REFERENCES.md in docs-dir "
            "(here-only; --here implied; --base forbidden)."
        ),
    )
    parser.add_argument(
        "--git-wt-name",
        action="store_true",
        default=False,
        dest="git_wt_name",
        help=(
            "Print a standardized worktree name: useReq-<PROJECT>-<BRANCH>-<TIMESTAMP> "
            "(here-only; --here implied; --base forbidden)."
        ),
    )
    parser.add_argument(
        "--git-wt-create",
        metavar="WT_NAME",
        default=None,
        dest="git_wt_create",
        help=(
            "Create a git worktree and branch with the given name, copying .req and provider dirs "
            "(here-only; --here implied; --base forbidden)."
        ),
    )
    parser.add_argument(
        "--git-wt-delete",
        metavar="WT_NAME",
        default=None,
        dest="git_wt_delete",
        help=(
            "Remove a git worktree and branch by name "
            "(here-only; --here implied; --base forbidden)."
        ),
    )
    parser.add_argument(
        "--git-path",
        action="store_true",
        default=False,
        dest="git_path_cmd",
        help=(
            "Print configured git-path from .req/config.json "
            "(here-only; --here implied; --base forbidden)."
        ),
    )
    parser.add_argument(
        "--get-base-path",
        action="store_true",
        default=False,
        dest="get_base_path_cmd",
        help=(
            "Print configured base-path from .req/config.json "
            "(here-only; --here implied; --base forbidden)."
        ),
    )
    return parser


def parse_args(argv: Optional[list[str]] = None) -> Namespace:
    """!
    @brief Parses command-line arguments into a namespace.
        @param argv List of arguments (defaults to sys.argv).
        @return Namespace containing parsed arguments.
    @details Implements the parse_args function behavior with deterministic control flow.
    """
    return build_parser().parse_args(argv)


def load_package_version() -> str:
    """!
    @brief Reads the package version from __init__.py.
        @return Version string extracted from the package.
        @throws ReqError If version cannot be determined.
    @details Implements the load_package_version function behavior with deterministic control flow.
    """
    init_path = Path(__file__).resolve().parent / "__init__.py"
    text = init_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"\s*$', text, re.M)
    if not match:
        raise ReqError("Error: unable to determine package version", 6)
    return match.group(1)


def maybe_print_version(argv: list[str]) -> bool:
    """!
    @brief Handles --ver/--version by printing the version.
        @param argv Command line arguments to check.
        @return True if version was printed, False otherwise.
    @details Implements the maybe_print_version function behavior with deterministic control flow.
    """
    if "--ver" in argv or "--version" in argv:
        print(load_package_version())
        return True
    return False


def run_upgrade() -> None:
    """!
    @brief Executes the upgrade using uv.
        @throws ReqError If upgrade fails.
    @details Implements the run_upgrade function behavior with deterministic control flow.
    @return {None} Function return value.
    @satisfies SRS-343
    """
    command = [
        "uv",
        "tool",
        "install",
        TOOL_PROGRAM_NAME,
        "--force",
        "--from",
        GITHUB_UPGRADE_SOURCE,
    ]
    detected_system = platform.system() or "Unknown"
    if detected_system != "Linux":
        print(
            "Warning: --upgrade automatic execution is supported only on Linux "
            f"(detected: {detected_system}). Run manually: {' '.join(command)}"
        )
        return
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
    """!
    @brief Executes the uninstallation using uv.
        @throws ReqError If uninstall fails.
    @details Implements the run_uninstall function behavior with deterministic control flow.
    @return {None} Function return value.
    @satisfies SRS-344, SRS-346
    """
    command = [
        "uv",
        "tool",
        "uninstall",
        TOOL_PROGRAM_NAME,
    ]
    detected_system = platform.system() or "Unknown"
    if detected_system != "Linux":
        print(
            "Warning: --uninstall automatic execution is supported only on Linux "
            f"(detected: {detected_system}). Run manually: {' '.join(command)}"
        )
        return
    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise ReqError("Error: 'uv' command not found in PATH", 12) from exc
    if result.returncode != 0:
        raise ReqError(
            f"Error: uninstall failed (code {result.returncode})",
            result.returncode,
        )
    cleanup_release_check_idle_state_cache()


def normalize_release_tag(tag: str) -> str:
    """!
    @brief Normalizes the release tag by removing a 'v' prefix if present.
        @param tag The raw tag string.
        @return The normalized version string.
    @details Implements the normalize_release_tag function behavior with deterministic control flow.
    """
    value = (tag or "").strip()
    if value.lower().startswith("v") and len(value) > 1:
        value = value[1:]
    return value.strip()


def parse_version_tuple(version: str) -> tuple[int, ...] | None:
    """! @brief Converts a version into a numeric tuple for comparison.
    @param version The version string to parse.
    @return Tuple of integers or None if parsing fails.
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
    """!
    @brief Returns True if latest is greater than current.
        @param current The current installed version string.
        @param latest The latest available version string.
        @return True if update is available, False otherwise.
    @details Implements the is_newer_version function behavior with deterministic control flow.
    """
    current_tuple = parse_version_tuple(current)
    latest_tuple = parse_version_tuple(latest)
    if not current_tuple or not latest_tuple:
        return False

    max_len = max(len(current_tuple), len(latest_tuple))
    current_norm = current_tuple + (0,) * (max_len - len(current_tuple))
    latest_norm = latest_tuple + (0,) * (max_len - len(latest_tuple))
    return latest_norm > current_norm


def parse_github_owner_repository(remote_url: str) -> tuple[str, str] | None:
    """!
    @brief Extract GitHub owner/repository from a git remote URL.
        @param remote_url Remote URL string from `git remote -v`.
        @return Tuple `(owner, repository)` when URL targets github.com; otherwise None.
    @details Supports SSH (`git@github.com:owner/repo.git`), HTTPS (`https://github.com/owner/repo.git`), and SSH-scheme (`ssh://git@github.com/owner/repo.git`) forms. Removes optional `.git` suffix.
    """
    value = (remote_url or "").strip()
    if not value:
        return None

    patterns = (
        r"^git@github\.com:(?P<owner>[^/\s]+)/(?P<repository>[^/\s]+?)(?:\.git)?$",
        r"^https?://github\.com/(?P<owner>[^/\s]+)/(?P<repository>[^/\s]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/(?P<owner>[^/\s]+)/(?P<repository>[^/\s]+?)(?:\.git)?/?$",
    )
    for pattern in patterns:
        match = re.match(pattern, value)
        if not match:
            continue
        owner = match.group("owner").strip()
        repository = match.group("repository").strip()
        if owner and repository:
            return owner, repository
    return None


def read_git_remote_verbose(cwd: str | None = None) -> str:
    """!
    @brief Read git remote definitions using `git remote -v`.
        @param cwd Optional working directory override for git execution context.
        @return Raw stdout output generated by `git remote -v`.
        @throws subprocess.CalledProcessError If git returns a non-zero status.
    @details Executes `git remote -v` with deterministic stderr capture and text decoding. When `cwd` is omitted, the current process working directory is used.
    """
    command_kwargs: dict[str, Any] = {
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if cwd is not None:
        command_kwargs["cwd"] = cwd
    return subprocess.check_output(
        ["git", "remote", "-v"],
        **command_kwargs,
    )


def resolve_github_owner_repository_from_active_remotes() -> tuple[str, str]:
    """!
    @brief Resolve GitHub owner/repository from active repository remotes.
        @return Tuple `(owner, repository)` resolved from active remotes.
        @throws ValueError If no github.com remote URL can be parsed from `git remote -v`.
        @throws ReqError If git remote inspection cannot execute successfully.
    @details Reads `git remote -v`, prioritizes `origin` fetch URL, then other fetch remotes, then non-fetch entries, and returns the first parseable github.com owner/repository pair. If the first inspection fails outside the repository root context, retries once from `REPO_ROOT`.
    """
    try:
        output = read_git_remote_verbose()
    except subprocess.CalledProcessError as exc:
        try:
            current_directory = Path.cwd().resolve()
            repo_root_directory = REPO_ROOT.resolve()
        except OSError:
            current_directory = Path.cwd()
            repo_root_directory = REPO_ROOT
        if current_directory != repo_root_directory:
            try:
                output = read_git_remote_verbose(cwd=str(REPO_ROOT))
            except subprocess.CalledProcessError as repo_exc:
                raise ReqError(
                    "Error: unable to inspect git remotes for GitHub owner/repository",
                    1,
                ) from repo_exc
        else:
            raise ReqError(
                "Error: unable to inspect git remotes for GitHub owner/repository",
                1,
            ) from exc
    except FileNotFoundError as exc:
        raise ReqError(
            "Error: unable to inspect git remotes for GitHub owner/repository",
            1,
        ) from exc

    ranked_remotes: list[tuple[int, str]] = []
    fallback_remotes: list[str] = []
    for raw_line in output.splitlines():
        parts = raw_line.strip().split()
        if len(parts) < 3:
            continue
        remote_name, remote_url, remote_kind = parts[0], parts[1], parts[2]
        if remote_kind == "(fetch)":
            rank = 0 if remote_name == "origin" else 1
            ranked_remotes.append((rank, remote_url))
        else:
            fallback_remotes.append(remote_url)

    ranked_remotes.sort(key=lambda item: item[0])
    candidate_urls = [url for _, url in ranked_remotes] + fallback_remotes
    for candidate_url in candidate_urls:
        parsed = parse_github_owner_repository(candidate_url)
        if parsed:
            return parsed

    raise ValueError(
        "unable to resolve GitHub owner/repository from active git remotes"
    )


def resolve_latest_release_api_url() -> str:
    """!
    @brief Resolve latest-release GitHub API URL from hardcoded repository settings.
        @return Fully-qualified URL `https://api.github.com/repos/Ogekuri/useReq/releases/latest`.
    @details Returns the static endpoint derived from `GITHUB_REPOSITORY_OWNER` and `GITHUB_REPOSITORY_NAME`.
    """
    return GITHUB_RELEASES_LATEST_URL


def format_unix_timestamp_utc(timestamp_seconds: int) -> str:
    """!
    @brief Convert a Unix timestamp into a UTC human-readable string.
        @param timestamp_seconds Unix timestamp in seconds.
        @return UTC datetime string in ISO-like `YYYY-MM-DDTHH:MM:SSZ` format.
    @details Implements deterministic UTC conversion for release-check idle-state persistence.
    """
    return datetime.fromtimestamp(
        timestamp_seconds,
        tz=timezone.utc,
    ).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_release_check_idle_file_path(
    program_name: str = RELEASE_CHECK_PROGRAM_NAME,
) -> Path:
    """!
    @brief Resolve idle-state file path for startup release-check throttling.
        @param program_name Program identifier used as cache subdirectory under `$HOME/.cache`.
        @return Absolute path `$HOME/.cache/<program_name>/check_version_idle-time.json`.
    @details Builds the path using the effective home directory returned by `Path.home()`.
    @satisfies SRS-345
    """
    return (
        Path.home()
        / RELEASE_CHECK_IDLE_CACHE_ROOT_DIRNAME
        / program_name
        / RELEASE_CHECK_IDLE_FILENAME
    )


def cleanup_release_check_idle_state_cache(
    program_name: str = RELEASE_CHECK_PROGRAM_NAME,
) -> None:
    """!
    @brief Delete release-check idle-state file and remove empty cache directory.
        @param program_name Program identifier used as cache subdirectory under `$HOME/.cache`.
        @throws OSError If filesystem operations fail.
    @details Deletes `$HOME/.cache/<program_name>/check_version_idle-time.json` when present; removes `$HOME/.cache/<program_name>` only when it exists and has no remaining entries.
    @satisfies SRS-346
    """
    idle_state_file_path = get_release_check_idle_file_path(program_name=program_name)
    idle_state_cache_dir = idle_state_file_path.parent

    if idle_state_file_path.exists():
        idle_state_file_path.unlink()

    if (
        idle_state_cache_dir.exists()
        and idle_state_cache_dir.is_dir()
        and not any(idle_state_cache_dir.iterdir())
    ):
        idle_state_cache_dir.rmdir()


def read_release_check_idle_state(file_path: Path) -> dict[str, int | str] | None:
    """!
    @brief Read and validate release-check idle-state JSON.
        @param file_path Absolute idle-state JSON path under `$HOME`.
        @return Normalized idle-state dictionary or None when file does not exist.
        @throws OSError If file read fails.
        @throws json.JSONDecodeError If file content is not valid JSON.
        @throws ValueError If required keys are missing or value types are invalid.
    @details Validates required keys `last_success_timestamp`, `last_success_human_readable_timestamp`, `idle_until_timestamp`, and `idle_until_human_readable_timestamp`; timestamps are normalized to integers.
    """
    if not file_path.exists():
        return None

    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("idle-state JSON root must be an object")

    required_keys = (
        "last_success_timestamp",
        "last_success_human_readable_timestamp",
        "idle_until_timestamp",
        "idle_until_human_readable_timestamp",
    )
    for key in required_keys:
        if key not in payload:
            raise ValueError(f"idle-state JSON missing key '{key}'")

    last_success_timestamp = payload["last_success_timestamp"]
    idle_until_timestamp = payload["idle_until_timestamp"]
    last_success_human_readable_timestamp = payload[
        "last_success_human_readable_timestamp"
    ]
    idle_until_human_readable_timestamp = payload["idle_until_human_readable_timestamp"]

    if not isinstance(last_success_timestamp, (int, float)):
        raise ValueError("idle-state key 'last_success_timestamp' must be numeric")
    if not isinstance(idle_until_timestamp, (int, float)):
        raise ValueError("idle-state key 'idle_until_timestamp' must be numeric")
    if (
        not isinstance(last_success_human_readable_timestamp, str)
        or not last_success_human_readable_timestamp.strip()
    ):
        raise ValueError(
            "idle-state key 'last_success_human_readable_timestamp' must be a non-empty string"
        )
    if (
        not isinstance(idle_until_human_readable_timestamp, str)
        or not idle_until_human_readable_timestamp.strip()
    ):
        raise ValueError(
            "idle-state key 'idle_until_human_readable_timestamp' must be a non-empty string"
        )

    return {
        "last_success_timestamp": int(last_success_timestamp),
        "last_success_human_readable_timestamp": (
            last_success_human_readable_timestamp.strip()
        ),
        "idle_until_timestamp": int(idle_until_timestamp),
        "idle_until_human_readable_timestamp": (
            idle_until_human_readable_timestamp.strip()
        ),
    }


def should_execute_release_check(
    idle_state: Mapping[str, Any] | None,
    now_timestamp: int,
) -> bool:
    """!
    @brief Decide whether startup release-check should execute in current invocation.
        @param idle_state Parsed idle-state payload or None when unavailable.
        @param now_timestamp Current Unix timestamp in seconds.
        @return True when release-check must execute; False when still in idle window.
    @details Executes release-check when state is missing and skips only while the persisted `idle_until_timestamp` is greater than the current timestamp.
    @satisfies SRS-348
    """
    if idle_state is None:
        return True

    idle_until_timestamp = idle_state.get("idle_until_timestamp")
    if not isinstance(idle_until_timestamp, (int, float)):
        return True
    return now_timestamp >= int(idle_until_timestamp)


def parse_retry_after_seconds(
    retry_after_header: str | None,
    now_timestamp: int,
) -> int | None:
    """!
    @brief Parse an HTTP `Retry-After` header value into non-negative seconds.
        @param retry_after_header Raw `Retry-After` header value.
        @param now_timestamp Current Unix timestamp in seconds.
        @return Retry delay in seconds when parsing succeeds; otherwise None.
    @details Supports integer-second values and HTTP-date values; HTTP-date values are converted to a delta from `now_timestamp`.
    """
    if retry_after_header is None:
        return None

    raw_value = retry_after_header.strip()
    if not raw_value:
        return None

    if re.fullmatch(r"[0-9]+", raw_value):
        return max(0, int(raw_value))

    try:
        parsed_datetime = parsedate_to_datetime(raw_value)
    except (TypeError, ValueError):
        return None
    if parsed_datetime is None:
        return None
    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)
    return max(0, int(parsed_datetime.timestamp()) - now_timestamp)


def write_release_check_idle_state_payload(
    file_path: Path,
    last_success_timestamp: int,
    idle_until_timestamp: int,
) -> None:
    """!
    @brief Persist canonical release-check idle-state payload to disk.
        @param file_path Absolute idle-state JSON path.
        @param last_success_timestamp Unix timestamp of the last successful release-check.
        @param idle_until_timestamp Unix timestamp until startup release-check remains disabled.
        @throws OSError If file write fails.
    @details Serializes both numeric and UTC human-readable timestamps for the success instant and the idle-until instant.
    """
    payload = {
        "last_success_timestamp": last_success_timestamp,
        "last_success_human_readable_timestamp": format_unix_timestamp_utc(
            last_success_timestamp
        ),
        "idle_until_timestamp": idle_until_timestamp,
        "idle_until_human_readable_timestamp": format_unix_timestamp_utc(
            idle_until_timestamp
        ),
    }
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        f"{json.dumps(payload, indent=2, sort_keys=True)}\n",
        encoding="utf-8",
    )


def write_release_check_idle_state(
    file_path: Path,
    now_timestamp: int,
    idle_delay_seconds: int = RELEASE_CHECK_IDLE_DELAY_SECONDS,
) -> None:
    """!
    @brief Persist release-check idle-state after a successful remote check.
        @param file_path Absolute idle-state JSON path.
        @param now_timestamp Successful check timestamp in seconds.
        @param idle_delay_seconds Fixed idle-delay length in seconds.
        @throws OSError If file write fails.
    @details Computes `idle_until_timestamp = now_timestamp + idle_delay_seconds` and persists canonical idle-state keys.
    @satisfies SRS-349
    """
    idle_until_timestamp = now_timestamp + int(idle_delay_seconds)
    write_release_check_idle_state_payload(
        file_path=file_path,
        last_success_timestamp=now_timestamp,
        idle_until_timestamp=idle_until_timestamp,
    )


def write_failed_release_check_idle_state(
    file_path: Path,
    now_timestamp: int,
    idle_state: Mapping[str, Any] | None,
    idle_delay_seconds: int = RELEASE_CHECK_IDLE_DELAY_SECONDS,
) -> None:
    """!
    @brief Persist idle-state after a startup release-check failure.
        @param file_path Absolute idle-state JSON path.
        @param now_timestamp Current Unix timestamp in seconds.
        @param idle_state Existing parsed idle-state payload or None.
        @param idle_delay_seconds Fixed failure idle-delay length in seconds.
        @throws OSError If file write fails.
    @details Computes `idle_until_timestamp = now + idle_delay_seconds`, rewrites the canonical idle-state payload on every failure, and preserves the previous successful timestamp when available.
    @satisfies SRS-350, SRS-351
    """
    effective_idle_delay = max(0, int(idle_delay_seconds))
    idle_until_timestamp = now_timestamp + effective_idle_delay

    last_success_timestamp = now_timestamp
    if isinstance(idle_state, Mapping):
        current_last_success = idle_state.get("last_success_timestamp")
        if isinstance(current_last_success, (int, float)):
            last_success_timestamp = int(current_last_success)

    write_release_check_idle_state_payload(
        file_path=file_path,
        last_success_timestamp=last_success_timestamp,
        idle_until_timestamp=idle_until_timestamp,
    )


def persist_failed_release_check_idle_state(
    file_path: Path,
    now_timestamp: int,
    idle_state: Mapping[str, Any] | None,
    idle_delay_seconds: int = RELEASE_CHECK_IDLE_DELAY_SECONDS,
) -> None:
    """!
    @brief Persist failure idle-state and report write failures.
        @param file_path Absolute idle-state JSON path.
        @param now_timestamp Current Unix timestamp in seconds.
        @param idle_state Existing parsed idle-state payload or None.
        @param idle_delay_seconds Fixed failure idle-delay length in seconds.
        @return {None} Function return value.
    @details Delegates failure idle-state persistence to `write_failed_release_check_idle_state(...)`; converts `OSError` into the standard bright-red stderr diagnostic without swallowing the original release-check failure.
    @satisfies SRS-350, SRS-351
    """
    try:
        write_failed_release_check_idle_state(
            file_path=file_path,
            now_timestamp=now_timestamp,
            idle_state=idle_state,
            idle_delay_seconds=idle_delay_seconds,
        )
    except OSError as idle_state_error:
        print(
            f"{ANSI_BRIGHT_RED}Release-check error: idle-state write failure ({idle_state_error}){ANSI_RESET}",
            file=sys.stderr,
        )


def maybe_notify_newer_version(
    timeout_seconds: float = RELEASE_CHECK_TIMEOUT_SECONDS,
) -> None:
    """!
    @brief Executes idle-gated online version check and prints bright colored status messages.
        @param timeout_seconds Time to wait for the version check response.
        @details Reads idle-state from `$HOME/.cache/usereq/check_version_idle-time.json`, skips remote requests when idle window is active unless startup context enables `FORCE_ONLINE_RELEASE_CHECK`, resolves latest-release URL from hardcoded repository settings when due, compares versions, prints a bright-green update message only for newer versions, persists a 3600-second idle-delay after successful HTTP/JSON validation, prints bright-red diagnostics on every failure, rewrites idle-state JSON on every failure, uses an 86400-second idle-delay for `HTTPError`, `URLError`, and `TimeoutError`, and uses the default 3600-second idle-delay for other release-check failures.
    @return {None} Function return value.
    @satisfies SRS-345, SRS-348, SRS-349, SRS-350, SRS-351
    """

    current_version = load_package_version()
    idle_state_path = get_release_check_idle_file_path()
    now_timestamp = int(time.time())

    idle_state: Mapping[str, Any] | None = None
    try:
        idle_state = read_release_check_idle_state(idle_state_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(
            f"{ANSI_BRIGHT_RED}Release-check error: invalid idle-state ({exc}){ANSI_RESET}",
            file=sys.stderr,
        )
        persist_failed_release_check_idle_state(
            file_path=idle_state_path,
            now_timestamp=now_timestamp,
            idle_state=idle_state,
        )
    if not FORCE_ONLINE_RELEASE_CHECK and not should_execute_release_check(
        idle_state,
        now_timestamp,
    ):
        return

    try:
        url = resolve_latest_release_api_url()
    except (ReqError, ValueError) as exc:
        print(
            f"{ANSI_BRIGHT_RED}Release-check error: {exc}{ANSI_RESET}",
            file=sys.stderr,
        )
        persist_failed_release_check_idle_state(
            file_path=idle_state_path,
            now_timestamp=now_timestamp,
            idle_state=idle_state,
        )
        return

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
            print(
                (
                    f"{ANSI_BRIGHT_RED}Release-check error: invalid response payload "
                    "(missing 'tag_name')."
                    f"{ANSI_RESET}"
                ),
                file=sys.stderr,
            )
            persist_failed_release_check_idle_state(
                file_path=idle_state_path,
                now_timestamp=now_timestamp,
                idle_state=idle_state,
            )
            return

        latest_version = normalize_release_tag(tag)
        if is_newer_version(current_version, latest_version):
            print(
                (
                    f"{ANSI_BRIGHT_GREEN}New version available: "
                    f"installed {current_version}, latest {latest_version}."
                    f"{ANSI_RESET}"
                ),
                file=sys.stderr,
            )
        try:
            write_release_check_idle_state(idle_state_path, now_timestamp)
        except OSError as exc:
            print(
                f"{ANSI_BRIGHT_RED}Release-check error: idle-state write failure ({exc}){ANSI_RESET}",
                file=sys.stderr,
            )
    except urllib.error.HTTPError as exc:
        error_details = f"HTTP {exc.code}"
        raw_error_payload = exc.read().decode("utf-8", errors="replace")
        payload: Any = None
        try:
            payload = json.loads(raw_error_payload) if raw_error_payload else None
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            message = payload.get("message")
            if isinstance(message, str) and message.strip():
                error_details = f"{error_details}: {message.strip()}"
        persist_failed_release_check_idle_state(
            file_path=idle_state_path,
            now_timestamp=now_timestamp,
            idle_state=idle_state,
            idle_delay_seconds=RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS,
        )
        print(
            f"{ANSI_BRIGHT_RED}Release-check error: {error_details}{ANSI_RESET}",
            file=sys.stderr,
        )
        return
    except urllib.error.URLError as exc:
        print(
            f"{ANSI_BRIGHT_RED}Release-check error: network failure ({exc.reason}){ANSI_RESET}",
            file=sys.stderr,
        )
        persist_failed_release_check_idle_state(
            file_path=idle_state_path,
            now_timestamp=now_timestamp,
            idle_state=idle_state,
            idle_delay_seconds=RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS,
        )
        return
    except TimeoutError:
        print(
            f"{ANSI_BRIGHT_RED}Release-check error: timeout exceeded{ANSI_RESET}",
            file=sys.stderr,
        )
        persist_failed_release_check_idle_state(
            file_path=idle_state_path,
            now_timestamp=now_timestamp,
            idle_state=idle_state,
            idle_delay_seconds=RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS,
        )
        return
    except (json.JSONDecodeError, ValueError) as exc:
        print(
            f"{ANSI_BRIGHT_RED}Release-check error: invalid release payload ({exc}){ANSI_RESET}",
            file=sys.stderr,
        )
        persist_failed_release_check_idle_state(
            file_path=idle_state_path,
            now_timestamp=now_timestamp,
            idle_state=idle_state,
        )
        return


def ensure_doc_directory(path: str, project_base: Path) -> None:
    """!
    @brief Ensures the documentation directory exists under the project base.
        @param path The relative path to the documentation directory.
        @param project_base The project root path.
        @throws ReqError If path is invalid, absolute, or not a directory.
    @details Implements the ensure_doc_directory function behavior with deterministic control flow.
    @return {None} Function return value.
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
    """!
    @brief Ensures the test directory exists under the project base.
        @param path The relative path to the test directory.
        @param project_base The project root path.
        @throws ReqError If path is invalid, absolute, or not a directory.
    @details Implements the ensure_test_directory function behavior with deterministic control flow.
    @return {None} Function return value.
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
    """!
    @brief Ensures the source directory exists under the project base.
        @param path The relative path to the source directory.
        @param project_base The project root path.
        @throws ReqError If path is invalid, absolute, or not a directory.
    @details Implements the ensure_src_directory function behavior with deterministic control flow.
    @return {None} Function return value.
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
    @param path_value The input path string.
    @param project_base The base path of the project.
    @return The normalized relative path string.
    @details Handles cases where the path includes the project directory name redundantly.
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
                suffix_resolved = (project_base / suffix_candidate).resolve(
                    strict=False
                )
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
    """!
    @brief Resolves the absolute path starting from a normalized value.
        @param normalized The normalized relative path string.
        @param project_base The project root path.
        @return Absolute Path object or None if normalized is empty.
    @details Implements the resolve_absolute function behavior with deterministic control flow.
    """
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (project_base / candidate).resolve(strict=False)


def format_substituted_path(value: str) -> str:
    """!
    @brief Uniforms path separators for substitutions.
        @param value The path string to format.
        @return Path string with forward slashes.
    @details Implements the format_substituted_path function behavior with deterministic control flow.
    """
    if not value:
        return ""
    return value.replace(os.sep, "/")


def compute_sub_path(
    normalized: str, absolute: Optional[Path], project_base: Path
) -> str:
    """!
    @brief Calculates the relative path to use in tokens.
        @param normalized The normalized relative path.
        @param absolute The absolute path object (can be None).
        @param project_base The project root path.
        @return Relative path string formatted with forward slashes.
    @details Implements the compute_sub_path function behavior with deterministic control flow.
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


def resolve_git_root(target_path: Path) -> Path:
    """!
    @brief Resolve the git repository root for a given path.
    @param target_path Absolute path that must be inside a git repository.
    @return Absolute path to the git repository root.
    @throws ReqError If the path is not inside a git repository.
    @satisfies SRS-305, SRS-306
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=str(target_path),
            timeout=10,
        )
        if result.returncode != 0:
            raise ReqError(
                f"Error: '{target_path}' is not inside a git repository.",
                3,
            )
        return Path(result.stdout.strip()).resolve()
    except FileNotFoundError:
        raise ReqError("Error: git is not available on PATH.", 3)
    except subprocess.TimeoutExpired:
        raise ReqError("Error: git command timed out.", 3)


def is_inside_git_repo(target_path: Path) -> bool:
    """!
    @brief Check whether a given path is inside a git work tree.
    @param target_path Absolute path to check.
    @return True if inside a git work tree, False otherwise.
    @satisfies SRS-305
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=str(target_path),
            timeout=10,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def sanitize_branch_name(branch: str) -> str:
    """!
    @brief Replace characters incompatible with Linux or Windows paths in a branch name.
    @param branch Raw git branch name.
    @return Sanitized string with incompatible characters replaced by `-`.
    @satisfies SRS-319
    """
    return re.sub(r'[<>:"/\\|?*\x00-\x1f\s~^{}\[\]]', "-", branch)


def validate_wt_name(wt_name: str) -> bool:
    """!
    @brief Validate that a worktree/branch name contains only valid directory characters.
    @param wt_name Candidate worktree name.
    @return True if valid, False if invalid characters are present.
    @satisfies SRS-321
    """
    if not wt_name or wt_name in (".", ".."):
        return False
    return INVALID_WT_NAME_RE.search(wt_name) is None


def load_full_config(project_base: Path) -> dict:
    """!
    @brief Load ALL parameters from `.req/config.json` as a raw dictionary.
    @param project_base The project root path.
    @return Full dictionary of all config.json key-value pairs.
    @throws ReqError If config file is missing or invalid JSON.
    @satisfies SRS-310
    """
    config_path = project_base / ".req" / "config.json"
    if not config_path.is_file():
        raise ReqError(
            "Error: .req/config.json not found in the project root",
            11,
        )
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReqError("Error: .req/config.json is not valid", 11) from exc


def save_config(
    project_base: Path,
    guidelines_dir_value: str,
    doc_dir_value: str,
    test_dir_value: str,
    src_dir_values: list[str],
    static_check_config: Optional[dict] = None,
    persisted_flags: Optional[dict[str, bool]] = None,
    provider_specs: Optional[list[str]] = None,
    base_path_abs: Optional[str] = None,
    git_path_abs: Optional[str] = None,
) -> None:
    """!
    @brief Saves normalized parameters to .req/config.json.
    @param project_base The project root path.
    @param guidelines_dir_value Relative path to guidelines directory.
    @param doc_dir_value Relative path to docs directory.
    @param test_dir_value Relative path to tests directory.
    @param src_dir_values List of relative paths to source directories.
    @param static_check_config Optional dict of static-check config to persist under key
      `"static-check"`; omitted from JSON when None or empty.
    @param persisted_flags Optional dict with persisted boolean flags used by `--update`.
    @param provider_specs Optional list of raw ``--provider`` SPEC strings to persist
      under the `"providers"` key (SRS-279).
    @param base_path_abs Optional absolute path string for `"base-path"` (SRS-302).
    @param git_path_abs Optional absolute path string for `"git-path"` (SRS-306).
    @details Writes full config payload to `.req/config.json`. Includes `"base-path"` and
    `"git-path"` when provided (SRS-302, SRS-306).
    @return {None} Function return value.
    @satisfies SRS-302, SRS-306
    """
    config_path = project_base / ".req" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict = {
        "guidelines-dir": guidelines_dir_value,
        "docs-dir": doc_dir_value,
        "tests-dir": test_dir_value,
        "src-dir": src_dir_values,
    }
    if base_path_abs is not None:
        payload["base-path"] = base_path_abs
    if git_path_abs is not None:
        payload["git-path"] = git_path_abs
    if static_check_config:
        payload["static-check"] = static_check_config
    if provider_specs:
        payload["providers"] = provider_specs
    if persisted_flags:
        payload.update(persisted_flags)
    config_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def load_config(project_base: Path) -> dict[str, str | list[str]]:
    """!
    @brief Loads parameters saved in .req/config.json.
        @param project_base The project root path.
        @return Dictionary containing configuration values.
        @throws ReqError If config file is missing or invalid.
    @details Implements the load_config function behavior with deterministic control flow.
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
        raise ReqError(
            "Error: missing or invalid 'guidelines-dir' field in .req/config.json", 11
        )
    if not isinstance(doc_dir_value, str) or not doc_dir_value.strip():
        raise ReqError(
            "Error: missing or invalid 'docs-dir' field in .req/config.json", 11
        )
    if not isinstance(test_dir_value, str) or not test_dir_value.strip():
        raise ReqError(
            "Error: missing or invalid 'tests-dir' field in .req/config.json", 11
        )
    if (
        not isinstance(src_dir_value, list)
        or not src_dir_value
        or not all(isinstance(item, str) and item.strip() for item in src_dir_value)
    ):
        raise ReqError(
            "Error: missing or invalid 'src-dir' field in .req/config.json", 11
        )
    return {
        "guidelines-dir": guidelines_dir_value,
        "docs-dir": doc_dir_value,
        "tests-dir": test_dir_value,
        "src-dir": src_dir_value,
    }


def load_static_check_from_config(project_base: Path) -> dict:
    """!
    @brief Load the `"static-check"` section from `.req/config.json` without validation errors.
    @param project_base The project root path.
    @return Dict of static-check config (canonical-lang -> list[config-dict]); empty dict if absent or
      if config.json is missing/invalid.
    @details Reads config.json silently; returns `{}` on any read or parse error.
      Does NOT raise `ReqError`; caller decides whether absence is an error.
    @see SRS-252, SRS-253, SRS-256
    """
    config_path = project_base / ".req" / "config.json"
    if not config_path.is_file():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    sc = payload.get("static-check")
    if not isinstance(sc, dict):
        return {}
    normalized: dict = {}
    for lang, entries in sc.items():
        if (
            isinstance(lang, str)
            and isinstance(entries, list)
            and entries
            and all(isinstance(item, dict) for item in entries)
        ):
            normalized[lang] = entries
    return normalized


def _static_check_entry_identity(
    canonical_lang: str, entry: Mapping[str, Any]
) -> tuple[str, str, Optional[str], tuple[str, ...]]:
    """!
    @brief Build the canonical identity tuple for one static-check entry.
    @param canonical_lang Canonical language key that owns the entry.
    @param entry Static-check entry mapping loaded from config or parsed from CLI.
    @return Tuple ``(canonical_lang, module, cmd, params_tuple)``.
    @details Identity is defined strictly by language, module, cmd, and params.
      Unknown/additional keys in ``entry`` are ignored; ``params`` is normalized
      to a tuple preserving order, and non-list params are treated as empty.
    @satisfies SRS-301
    """
    module_raw = entry.get("module")
    cmd_raw = entry.get("cmd")
    params_raw = entry.get("params")
    module = module_raw if isinstance(module_raw, str) else ""
    cmd = cmd_raw if isinstance(cmd_raw, str) else None
    params: tuple[str, ...] = ()
    if isinstance(params_raw, list):
        params = tuple(item for item in params_raw if isinstance(item, str))
    return (canonical_lang, module, cmd, params)


def build_persisted_update_flags(args: Namespace) -> dict[str, bool]:
    """!
    @brief Build persistent update flags from parsed CLI arguments.
        @param args Parsed CLI namespace.
        @return Mapping of config key -> boolean value for install/update persistence.
    @details Only ``preserve-models`` is persisted as a boolean flag (SRS-288).
    Provider/artifact/option configuration is persisted via ``--provider`` specs under
    the ``providers`` key in ``config.json`` (SRS-279).
    """
    return {
        "preserve-models": bool(args.preserve_models),
    }


def load_persisted_update_flags(project_base: Path) -> dict[str, bool]:
    """!
    @brief Load persisted install/update boolean flags from `.req/config.json`.
        @param project_base The project root path.
        @return Mapping of persisted config key -> boolean value.
        @throws ReqError If config file is missing, invalid, or required flag fields are missing/invalid.
    @details Only ``preserve-models`` is loaded as a boolean flag (SRS-288).
    Provider/artifact activation is validated via the persisted ``providers`` array (SRS-280).
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
    flags: dict[str, bool] = {}
    for key in PERSISTED_UPDATE_FLAG_KEYS:
        value = payload.get(key)
        if not isinstance(value, bool):
            raise ReqError(
                f"Error: missing or invalid '{key}' field in .req/config.json", 11
            )
        flags[key] = value

    # Validate that persisted --provider specs provide adequate activation (SRS-280).
    persisted_providers = payload.get("providers", [])
    has_provider_specs = (
        isinstance(persisted_providers, list) and len(persisted_providers) > 0
    )

    if not has_provider_specs:
        raise ReqError(
            "Error: .req/config.json has an invalid provider/artifact update configuration",
            11,
        )
    return flags


def load_persisted_provider_specs(project_base: Path) -> list[str]:
    """!
    @brief Load persisted ``--provider`` SPEC strings from `.req/config.json`.
    @param project_base The project root path.
    @return List of raw SPEC strings; empty list if key is missing or config is unreadable.
    @details Reads the ``"providers"`` key from config.json (SRS-280). Returns ``[]``
    on any read or parse error rather than raising.
    @see SRS-279, SRS-280
    """
    config_path = project_base / ".req" / "config.json"
    if not config_path.is_file():
        return []
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    specs = payload.get("providers", [])
    if isinstance(specs, list) and all(isinstance(s, str) for s in specs):
        return specs
    return []


def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str:
    """!
    @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
    @details Implements the generate_guidelines_file_list function behavior with deterministic control flow.
    @param guidelines_dir Input parameter `guidelines_dir`.
    @param project_base Input parameter `project_base`.
    @return {str} Function return value.
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


def generate_guidelines_file_items(
    guidelines_dir: Path, project_base: Path
) -> list[str]:
    """!
    @brief Generates a list of relative file paths (no formatting) for printing.
        @details Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
    @param guidelines_dir Input parameter `guidelines_dir`.
    @param project_base Input parameter `project_base`.
    @return {list[str]} Function return value.
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


def upgrade_guidelines_templates(guidelines_dest: Path, overwrite: bool = False) -> int:
    """!
    @brief Copies guidelines templates from resources/guidelines/ to the target directory.
        @details Args: guidelines_dest: Target directory where templates will be copied overwrite: If True, overwrite existing files; if False, skip existing files Returns: Number of non-hidden files copied; returns 0 when the source directory is empty.
    @param guidelines_dest Input parameter `guidelines_dest`.
    @param overwrite Input parameter `overwrite`.
    @return {int} Function return value.
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
    """!
    @brief Normalizes the path token optionally preserving the trailing slash.
    @details Implements the make_relative_token function behavior with deterministic control flow.
    @param raw Input parameter `raw`.
    @param keep_trailing Input parameter `keep_trailing`.
    @return {str} Function return value.
    """
    if not raw:
        return ""
    normalized = raw.replace("\\", "/").strip("/")
    if not normalized:
        return ""
    suffix = "/" if keep_trailing and raw.endswith("/") else ""
    return f"{normalized}{suffix}"


def ensure_relative(value: str, name: str, code: int) -> None:
    """!
    @brief Validates that the path is not absolute and raises an error otherwise.
    @details Implements the ensure_relative function behavior with deterministic control flow.
    @param value Input parameter `value`.
    @param name Input parameter `name`.
    @param code Input parameter `code`.
    @return {None} Function return value.
    """
    if Path(value).is_absolute():
        raise ReqError(
            f"Error: {name} must be a relative path under PROJECT_BASE",
            code,
        )


def apply_replacements(text: str, replacements: Mapping[str, str]) -> str:
    """!
    @brief Returns text with token replacements applied.
    @details Implements the apply_replacements function behavior with deterministic control flow.
    @param text Input parameter `text`.
    @param replacements Input parameter `replacements`.
    @return {str} Function return value.
    """
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    return text


def write_text_file(dst: Path, text: str) -> None:
    """!
    @brief Writes text to disk, ensuring the destination folder exists.
    @details Implements the write_text_file function behavior with deterministic control flow.
    @param dst Input parameter `dst`.
    @param text Input parameter `text`.
    @return {None} Function return value.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def copy_with_replacements(
    src: Path, dst: Path, replacements: Mapping[str, str]
) -> None:
    """!
    @brief Copies a file substituting the indicated tokens with their values.
    @details Implements the copy_with_replacements function behavior with deterministic control flow.
    @param src Input parameter `src`.
    @param dst Input parameter `dst`.
    @param replacements Input parameter `replacements`.
    @return {None} Function return value.
    """
    text = src.read_text(encoding="utf-8")
    updated = apply_replacements(text, replacements)
    write_text_file(dst, updated)


def normalize_description(value: str) -> str:
    """!
    @brief Normalizes a description by removing superfluous quotes and escapes.
    @details Implements the normalize_description function behavior with deterministic control flow.
    @param value Input parameter `value`.
    @return {str} Function return value.
    """
    trimmed = value.strip()
    if len(trimmed) >= 2 and trimmed.startswith('"') and trimmed.endswith('"'):
        trimmed = trimmed[1:-1]
    if len(trimmed) >= 4 and trimmed.startswith('\\"') and trimmed.endswith('\\"'):
        trimmed = trimmed[2:-2]
    return trimmed.replace('\\"', '"')


def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None:
    """!
    @brief Converts a Markdown prompt to TOML for Gemini.
    @details Implements the md_to_toml function behavior with deterministic control flow.
    @param md_path Input parameter `md_path`.
    @param toml_path Input parameter `toml_path`.
    @param force Input parameter `force`.
    @return {None} Function return value.
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
    """!
    @brief Extracts front matter and body from Markdown.
    @details Implements the extract_frontmatter function behavior with deterministic control flow.
    @param content Input parameter `content`.
    @return {tuple[str, str]} Function return value.
    """
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not match:
        raise ReqError("No leading '---' block found at start of Markdown file.", 4)
    # Explicitly return two strings to satisfy type annotation.
    return match.group(1), match.group(2)


def extract_description(frontmatter: str) -> str:
    """!
    @brief Extracts the description from front matter.
    @details Implements the extract_description function behavior with deterministic control flow.
    @param frontmatter Input parameter `frontmatter`.
    @return {str} Function return value.
    """
    desc_match = re.search(r"^description:\s*(.*)$", frontmatter, re.M)
    if not desc_match:
        raise ReqError("No 'description:' field found inside the leading block.", 5)
    return normalize_description(desc_match.group(1).strip())


def extract_argument_hint(frontmatter: str) -> str:
    """!
    @brief Extracts the argument-hint from front matter, if present.
    @details Implements the extract_argument_hint function behavior with deterministic control flow.
    @param frontmatter Input parameter `frontmatter`.
    @return {str} Function return value.
    """
    match = re.search(r"^argument-hint:\s*(.*)$", frontmatter, re.M)
    if not match:
        return ""
    return normalize_description(match.group(1).strip())


def extract_purpose_first_bullet(body: str) -> str:
    """!
    @brief Returns the first bullet of the Purpose section.
    @details Implements the extract_purpose_first_bullet function behavior with deterministic control flow.
    @param body Input parameter `body`.
    @return {str} Function return value.
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


def _extract_section_text(body: str, section_name: str) -> str:
    """! @brief Extracts and collapses the text content of a named ## section.
    @details Scans `body` line by line for a heading matching `## <section_name>`
    (case-insensitive). Collects all subsequent non-empty lines until the next
    `##`-level heading (or end of string). Strips each line, joins with a single
    space, and returns the collapsed single-line result.
    @param[in] body str -- Full prompt body text (after front matter removal).
    @param[in] section_name str -- Target section name without `##` prefix (case-insensitive match).
    @return str -- Single-line collapsed text of the section; empty string if section absent or empty.
    """
    lines = body.splitlines()
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == f"## {section_name.lower()}":
            start_idx = idx + 1
            break
    if start_idx is None:
        return ""
    parts: list[str] = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped.startswith("##"):
            break
        if stripped:
            parts.append(" ".join(stripped.split()))
    return " ".join(parts)


def extract_skill_description(frontmatter: str) -> str:
    """! @brief Extracts the usage field from YAML front matter as a single YAML-safe line.
    @details Parses the YAML front matter and returns the `usage` field value with all
    whitespace normalized to a single line. Returns an empty string if the field is absent.
    @param[in] frontmatter str -- YAML front matter text (without the leading/trailing `---` delimiters).
    @return str -- Single-line text of the usage field; empty string if absent.
    """
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError:
        return ""
    if not isinstance(data, dict):
        return ""
    usage = data.get("usage", "")
    if not usage:
        return ""
    return " ".join(str(usage).split())


def json_escape(value: str) -> str:
    """!
    @brief Escapes a string for JSON without external delimiters.
    @details Implements the json_escape function behavior with deterministic control flow.
    @param value Input parameter `value`.
    @return {str} Function return value.
    """
    return json.dumps(value)[1:-1]


def generate_kiro_resources(
    req_dir: Path,
    project_base: Path,
    prompt_rel_path: str,
) -> list[str]:
    """!
    @brief Generates the resource list for the Kiro agent.
    @details Implements the generate_kiro_resources function behavior with deterministic control flow.
    @param req_dir Input parameter `req_dir`.
    @param project_base Input parameter `project_base`.
    @param prompt_rel_path Input parameter `prompt_rel_path`.
    @return {list[str]} Function return value.
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
    """!
    @brief Renders the Kiro agent JSON and populates main fields.
    @details Implements the render_kiro_agent function behavior with deterministic control flow.
    @param template Input parameter `template`.
    @param name Input parameter `name`.
    @param description Input parameter `description`.
    @param prompt Input parameter `prompt`.
    @param resources Input parameter `resources`.
    @param tools Input parameter `tools`.
    @param model Input parameter `model`.
    @param include_tools Input parameter `include_tools`.
    @param include_model Input parameter `include_model`.
    @return {str} Function return value.
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
    """!
    @brief Replaces tokens in the specified file.
    @details Implements the replace_tokens function behavior with deterministic control flow.
    @param path Input parameter `path`.
    @param replacements Input parameter `replacements`.
    @return {None} Function return value.
    """
    text = path.read_text(encoding="utf-8")
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    path.write_text(text, encoding="utf-8")


def yaml_double_quote_escape(value: str) -> str:
    """!
    @brief Minimal escape for a double-quoted string in YAML.
    @details Implements the yaml_double_quote_escape function behavior with deterministic control flow.
    @param value Input parameter `value`.
    @return {str} Function return value.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def list_docs_templates() -> list[Path]:
    """!
    @brief Returns non-hidden files available in resources/docs.
        @return Sorted list of file paths under resources/docs.
        @throws ReqError If resources/docs does not exist or has no non-hidden files.
    @details Implements the list_docs_templates function behavior with deterministic control flow.
    """
    candidate = RESOURCE_ROOT / "docs"
    if not candidate.is_dir():
        raise ReqError("Error: no docs templates directory found in resources", 9)
    templates = sorted(
        path
        for path in candidate.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )
    if not templates:
        raise ReqError("Error: no docs templates found in resources/docs", 9)
    return templates


def find_requirements_template(docs_templates: list[Path]) -> Path:
    """!
    @brief Returns the packaged Requirements template file.
        @param docs_templates Runtime docs template file list from resources/docs.
        @return Path to `Requirements_Template.md`.
        @throws ReqError If `Requirements_Template.md` is not present.
    @details Implements the find_requirements_template function behavior with deterministic control flow.
    """
    for template_path in docs_templates:
        if template_path.name == REQUIREMENTS_TEMPLATE_NAME:
            return template_path
    raise ReqError(
        f"Error: no {REQUIREMENTS_TEMPLATE_NAME} template found in docs",
        9,
    )


def load_kiro_template() -> tuple[str, dict[str, Any]]:
    """!
    @brief Loads the Kiro template from centralized models configuration.
    @details Implements the load_kiro_template function behavior with deterministic control flow.
    @return {tuple[str, dict[str, Any]]} Function return value.
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
                                    json.dumps(
                                        agent_template, indent=2, ensure_ascii=False
                                    ),
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
    """!
    @brief Removes // and /* */ comments to allow JSONC parsing.
    @details Implements the strip_json_comments function behavior with deterministic control flow.
    @param text Input parameter `text`.
    @return {str} Function return value.
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
    """!
    @brief Loads JSON/JSONC settings, removing comments when necessary.
    @details Implements the load_settings function behavior with deterministic control flow.
    @param path Input parameter `path`.
    @return {dict[str, Any]} Function return value.
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
    preserve_models_path: Optional[Path] = None,
) -> dict[str, dict[str, Any] | None]:
    """!
    @brief Loads centralized models configuration from common/models.json.
        @details Returns a map cli_name -> parsed_json or None if not present. When preserve_models_path is provided and exists, loads from that file, ignoring legacy_mode. Otherwise, when legacy_mode is True, attempts to load models-legacy.json first, falling back to models.json if not found.
    @param resource_root Input parameter `resource_root`.
    @param legacy_mode Input parameter `legacy_mode`.
    @param preserve_models_path Input parameter `preserve_models_path`.
    @return {dict[str, dict[str, Any] | None]} Function return value.
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
            return {
                name: None
                for name in (
                    "claude",
                    "copilot",
                    "opencode",
                    "kiro",
                    "gemini",
                    "codex",
                    "pi",
                )
            }

    # Load the centralized configuration
    try:
        all_models = load_settings(config_file)
        dlog(f"Loaded centralized models from: {config_file}")
    except Exception as exc:
        dlog(f"Failed loading centralized models from {config_file}: {exc}")
        return {
            name: None
            for name in (
                "claude",
                "copilot",
                "opencode",
                "kiro",
                "gemini",
                "codex",
                "pi",
            )
        }

    # Extract individual CLI configs
    result: dict[str, dict[str, Any] | None] = {}
    for name in ("claude", "copilot", "opencode", "kiro", "gemini", "codex", "pi"):
        result[name] = all_models.get(name) if isinstance(all_models, dict) else None
        if result[name]:
            dlog(f"Extracted config for {name}")

    return result


def get_model_tools_for_prompt(
    config: dict[str, Any] | None, prompt_name: str, source_name: Optional[str] = None
) -> tuple[Optional[str], Optional[list[str]]]:
    """!
    @brief Extracts model and tools for the prompt from the CLI config.
        @details Returns (model, tools) where each value can be None if not available.
    @param config Input parameter `config`.
    @param prompt_name Input parameter `prompt_name`.
    @param source_name Input parameter `source_name`.
    @return {tuple[Optional[str], Optional[list[str]]]} Function return value.
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
    """!
    @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt.
        @details Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
    @param config Input parameter `config`.
    @param prompt_name Input parameter `prompt_name`.
    @return {Any} Function return value.
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
    """!
    @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
    @details Implements the format_tools_inline_list function behavior with deterministic control flow.
    @param tools Input parameter `tools`.
    @return {str} Function return value.
    """
    safe = [t.replace("'", "\\'") for t in tools]
    quoted = ", ".join(f"'{s}'" for s in safe)
    return f"[{quoted}]"


def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """!
    @brief Recursively merges dictionaries, prioritizing incoming values.
    @details Implements the deep_merge_dict function behavior with deterministic control flow.
    @param base Input parameter `base`.
    @param incoming Input parameter `incoming`.
    @return {dict[str, Any]} Function return value.
    """
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge_dict(base[key], value)
        else:
            base[key] = value
    return base


def find_vscode_settings_source() -> Optional[Path]:
    """!
    @brief Finds the VS Code settings template if available.
    @details Implements the find_vscode_settings_source function behavior with deterministic control flow.
    @return {Optional[Path]} Function return value.
    """
    candidate = RESOURCE_ROOT / "vscode" / "settings.json"
    if candidate.is_file():
        return candidate
    return None


def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]:
    """!
    @brief Generates chat.promptFilesRecommendations from available prompts.
    @details Implements the build_prompt_recommendations function behavior with deterministic control flow.
    @param prompts_dir Input parameter `prompts_dir`.
    @return {dict[str, bool]} Function return value.
    """
    recommendations: dict[str, bool] = {}
    if not prompts_dir.is_dir():
        return recommendations
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        recommendations[f"req-{prompt_path.stem}"] = True
    return recommendations


def ensure_wrapped(target: Path, project_base: Path, code: int) -> None:
    """!
    @brief Verifies that the path is under the project root.
    @details Implements the ensure_wrapped function behavior with deterministic control flow.
    @param target Input parameter `target`.
    @param project_base Input parameter `project_base`.
    @param code Input parameter `code`.
    @return {None} Function return value.
    """
    if not target.resolve().is_relative_to(project_base):
        raise ReqError(
            f"Error: safe removal of {target} refused (not under PROJECT_BASE)",
            code,
        )


def save_vscode_backup(req_root: Path, settings_path: Path) -> None:
    """!
    @brief Saves a backup of VS Code settings if the file exists.
    @details Implements the save_vscode_backup function behavior with deterministic control flow.
    @param req_root Input parameter `req_root`.
    @param settings_path Input parameter `settings_path`.
    @return {None} Function return value.
    """
    backup_path = req_root / "settings.json.backup"
    # Never create an absence marker. Backup only if the file exists.
    if settings_path.exists():
        req_root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(settings_path, backup_path)


def restore_vscode_settings(project_base: Path) -> None:
    """!
    @brief Restores VS Code settings from backup, if present.
    @details Implements the restore_vscode_settings function behavior with deterministic control flow.
    @param project_base Input parameter `project_base`.
    @return {None} Function return value.
    """
    req_root = project_base / ".req"
    backup_path = req_root / "settings.json.backup"
    target_settings = project_base / ".vscode" / "settings.json"
    if backup_path.exists():
        target_settings.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(backup_path, target_settings)
    # Do not remove the target file if no backup exists: restore behavior disabled otherwise.


def prune_empty_dirs(root: Path) -> None:
    """!
    @brief Removes empty directories under the specified root.
    @details Implements the prune_empty_dirs function behavior with deterministic control flow.
    @param root Input parameter `root`.
    @return {None} Function return value.
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
    """!
    @brief Removes resources generated by the tool in the project root.
    @details Implements the remove_generated_resources function behavior with deterministic control flow.
    @param project_base Input parameter `project_base`.
    @return {None} Function return value.
    """
    remove_dirs = [
        project_base / ".gemini" / "commands" / "req",
        project_base / ".gemini" / "skills",
        project_base / ".claude" / "commands" / "req",
        project_base / ".claude" / "skills",
        project_base / ".codex" / "skills",
        project_base / ".github" / "skills",
        project_base / ".pi" / "skills",
        project_base / ".kiro" / "skills",
        project_base / ".opencode" / "skill",
        project_base / ".req" / "docs",
    ]
    remove_globs = [
        project_base / ".codex" / "prompts",
        project_base / ".github" / "agents",
        project_base / ".github" / "prompts",
        project_base / ".pi" / "prompts",
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
        for pattern in ("req-*", "req-*"):
            for path in folder.glob(pattern):
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
    """!
    @brief Handles the removal of generated resources.
    @details Implements the run_remove function behavior with deterministic control flow.
    @param args Input parameter `args`.
    @return {None} Function return value.
    """
    guidelines_dir = getattr(args, "guidelines_dir", None)
    doc_dir = getattr(args, "docs_dir", None)
    test_dir = getattr(args, "tests_dir", None)
    src_dir = getattr(args, "src_dir", None)
    if args.update:
        raise ReqError(
            "Error: --remove does not accept --update",
            4,
        )
    if (not getattr(args, "here", False)) and (
        guidelines_dir or doc_dir or test_dir or src_dir
    ):
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

    # Do not perform any restore or removal of .vscode/settings.json during removal.
    remove_generated_resources(project_base)
    for root_name in (
        ".gemini",
        ".codex",
        ".kiro",
        ".github",
        ".pi",
        ".vscode",
        ".opencode",
        ".claude",
    ):
        prune_empty_dirs(project_base / root_name)


def _validate_enable_static_check_command_executables(
    static_check_config: Mapping[str, list[dict[str, Any]]],
    *,
    enforce: bool,
) -> None:
    """!
        @brief Validate Command-module executables in `--enable-static-check` parsed entries.
        @param static_check_config Parsed static-check entries grouped by canonical language.
        @param enforce When false, skip validation and return immediately.
        @throws ReqError If a Command entry references a non-executable `cmd` on this system.
        @details
          Validation scope is limited to Command entries coming from CLI specs.
          Each Command `cmd` is resolved with `shutil.which`; on miss, raises `ReqError(code=1)`
          before any configuration persistence.
        @see SRS-250
    @return {None} Function return value.
    """
    if not enforce:
        return
    for entries in static_check_config.values():
        for entry in entries:
            if entry.get("module") != "Command":
                continue
            cmd_raw = entry.get("cmd")
            cmd = cmd_raw.strip() if isinstance(cmd_raw, str) else ""
            if not cmd or shutil.which(cmd) is None:
                raise ReqError(
                    f"Error: --enable-static-check Command cmd '{cmd or '<missing>'}' is not an executable program on this system.",
                    1,
                )


def run(args: Namespace) -> None:
    """!
    @brief Handles the main initialization flow.
        @details Validates input arguments, normalizes paths, and orchestrates resource generation per provider and artifact type. Requires at least one ``--provider`` spec (SRS-035). Deduplicates ``--enable-static-check`` entries (SRS-251, SRS-301).
        @param args Parsed CLI namespace; must contain ``provider_specs`` list and ``preserve_models`` boolean.
    @return {None} Function return value.
    @satisfies SRS-251, SRS-301
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

    # SRS-305: Verify project_base is inside a git repository during installation.
    if not is_inside_git_repo(project_base):
        raise ReqError(
            f"Error: '{project_base}' is not inside a git repository.",
            3,
        )
    # SRS-306: Determine git root.
    git_root = resolve_git_root(project_base)
    base_path_abs = str(project_base)
    git_path_abs = str(git_root)

    guidelines_dir = getattr(args, "guidelines_dir", None)
    doc_dir = getattr(args, "docs_dir", None)
    test_dir = getattr(args, "tests_dir", None)
    src_dir = getattr(args, "src_dir", None)
    use_here_config = bool(getattr(args, "here", False))

    if (
        args.update
        and (not use_here_config)
        and (guidelines_dir or doc_dir or test_dir or src_dir)
    ):
        raise ReqError(
            "Error: --update does not accept --guidelines-dir, --docs-dir, --tests-dir, or --src-dir",
            4,
        )
    if (
        (not use_here_config)
        and (not args.update)
        and (not guidelines_dir or not doc_dir or not test_dir or not src_dir)
    ):
        raise ReqError(
            "Error: --guidelines-dir, --docs-dir, --tests-dir, and --src-dir are required without --update",
            4,
        )

    if use_here_config or args.update:
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

    if args.update:
        persisted_flags = load_persisted_update_flags(project_base)
        args.preserve_models = (
            bool(args.preserve_models) or persisted_flags["preserve-models"]
        )

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

    normalized_guidelines = make_relative_if_contains_project(
        guidelines_dir_value, project_base
    )
    normalized_doc = make_relative_if_contains_project(doc_dir_value, project_base)
    normalized_test = make_relative_if_contains_project(test_dir_value, project_base)
    normalized_src_dirs: list[str] = []
    config_src_dirs: list[str] = []
    src_has_trailing_slashes: list[bool] = []
    guidelines_has_trailing_slash = guidelines_dir_value.endswith(
        "/"
    ) or guidelines_dir_value.endswith("\\")
    doc_has_trailing_slash = doc_dir_value.endswith("/") or doc_dir_value.endswith("\\")
    test_has_trailing_slash = test_dir_value.endswith("/") or test_dir_value.endswith(
        "\\"
    )
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
        config_src = (
            f"{normalized_src}/" if has_trailing and normalized_src else normalized_src
        )
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
    if args.add_guidelines or args.upgrade_guidelines:
        guidelines_src = RESOURCE_ROOT / "guidelines"
        if guidelines_src.is_dir():
            copied = upgrade_guidelines_templates(
                guidelines_dest, overwrite=args.upgrade_guidelines
            )
            if VERBOSE:
                log(f"OK: copied {copied} guidelines template(s) to {guidelines_dest}")
        else:
            if VERBOSE:
                log(
                    f"OK: no guidelines templates found at {guidelines_src}, skipping copy"
                )

    # Resolve --provider specs: load persisted specs on --update, replace with CLI specs (SRS-275, SRS-280).
    cli_provider_specs: list[str] = getattr(args, "provider_specs", None) or []
    persisted_provider_specs: list[str] = []
    if use_here_config or args.update:
        persisted_provider_specs = load_persisted_provider_specs(project_base)
    # CLI --provider replaces persisted specs when at least one is given (SRS-280).
    effective_provider_specs = (
        cli_provider_specs if cli_provider_specs else persisted_provider_specs
    )
    # Validate all specs (will raise ReqError on invalid tokens, SRS-278).
    for spec_str in effective_provider_specs:
        parse_provider_spec(spec_str)
    # Resolve per-provider configs (spec-driven only, SRS-275).
    provider_configs = resolve_provider_configs(effective_provider_specs)

    # Derive flat enable_* variables from per-provider configs (spec-driven only).
    enable_claude = provider_configs["claude"]["enabled"]
    enable_codex = provider_configs["codex"]["enabled"]
    enable_gemini = provider_configs["gemini"]["enabled"]
    enable_github = provider_configs["github"]["enabled"]
    enable_kiro = provider_configs["kiro"]["enabled"]
    enable_opencode = provider_configs["opencode"]["enabled"]
    enable_pi = provider_configs["pi"]["enabled"]

    # A provider's artifacts are enabled only via the per-provider spec.
    enable_prompts = any(pc["prompts"] for pc in provider_configs.values())
    enable_agents = any(pc["agents"] for pc in provider_configs.values())
    enable_skills = any(pc["skills"] for pc in provider_configs.values())

    if not any(
        (
            enable_claude,
            enable_codex,
            enable_gemini,
            enable_github,
            enable_kiro,
            enable_opencode,
            enable_pi,
        )
    ):
        if args.update:
            raise ReqError(
                "Error: .req/config.json has an invalid provider/artifact update configuration",
                11,
            )
        parser = build_parser()
        parser.print_help()
        raise ReqError(
            "Error: at least one --provider spec is required to generate prompts",
            4,
        )
    if not any((enable_prompts, enable_agents, enable_skills)):
        if args.update:
            raise ReqError(
                "Error: .req/config.json has an invalid provider/artifact update configuration",
                11,
            )
        parser = build_parser()
        parser.print_help()
        raise ReqError(
            "Error: at least one --provider spec with artifact types is required",
            4,
        )

    # Parse --enable-static-check specs and compute merged static-check config (SRS-248..SRS-252, SRS-301).
    new_static_check: dict = {}
    enable_static_check_specs = getattr(args, "enable_static_check", None) or []
    if enable_static_check_specs:
        from .static_check import parse_enable_static_check as _parse_sc

        for spec in enable_static_check_specs:
            canonical_lang, lang_cfg = _parse_sc(spec)
            # SRS-251: discard identity-duplicate entries within one invocation.
            identity = _static_check_entry_identity(canonical_lang, lang_cfg)
            existing = new_static_check.get(canonical_lang, [])
            has_duplicate = any(
                _static_check_entry_identity(canonical_lang, entry) == identity
                for entry in existing
            )
            if not has_duplicate:
                new_static_check.setdefault(canonical_lang, []).append(lang_cfg)
    _validate_enable_static_check_command_executables(
        new_static_check,
        enforce=(not args.update and not use_here_config),
    )

    # Compute merged static-check: existing config + new non-duplicate entries (SRS-252, SRS-301).
    # Preserve pre-existing static-check entries whenever config.json already exists and
    # the invocation includes at least one --enable-static-check spec.
    config_path = project_base / ".req" / "config.json"
    should_merge_existing = (
        use_here_config
        or args.update
        or (bool(enable_static_check_specs) and config_path.is_file())
    )
    if should_merge_existing:
        existing_sc = load_static_check_from_config(project_base)
        merged_static_check: dict = {k: list(v) for k, v in existing_sc.items()}
        for lang, entries in new_static_check.items():
            existing_for_lang = merged_static_check.get(lang, [])
            existing_identities = {
                _static_check_entry_identity(lang, entry)
                for entry in existing_for_lang
                if isinstance(entry, dict)
            }
            for entry in entries:
                # SRS-301: skip new entry if same (language, module, cmd, params) already exists.
                identity = _static_check_entry_identity(lang, entry)
                if identity not in existing_identities:
                    merged_static_check.setdefault(lang, []).append(entry)
                    existing_identities.add(identity)
    else:
        merged_static_check = new_static_check

    if not args.update:
        save_config(
            project_base,
            config_guidelines,
            config_doc,
            config_test,
            config_src_dirs,
            static_check_config=merged_static_check if merged_static_check else None,
            persisted_flags=build_persisted_update_flags(args),
            provider_specs=effective_provider_specs
            if effective_provider_specs
            else None,
            base_path_abs=base_path_abs,
            git_path_abs=git_path_abs,
        )
    else:
        # --update path: always re-save config.json to update base-path/git-path (SRS-303, SRS-307)
        # and merge static-check entries (SRS-252, SRS-301) and provider specs (SRS-279).
        existing_full_config = load_config(project_base)
        persisted_flags = load_persisted_update_flags(project_base)
        save_config(
            project_base,
            str(existing_full_config["guidelines-dir"]),
            str(existing_full_config["docs-dir"]),
            str(existing_full_config["tests-dir"]),
            list(existing_full_config["src-dir"]),  # type: ignore[arg-type]
            static_check_config=merged_static_check if merged_static_check else None,
            persisted_flags=persisted_flags,
            provider_specs=effective_provider_specs
            if effective_provider_specs
            else None,
            base_path_abs=base_path_abs,
            git_path_abs=git_path_abs,
        )

    sub_guidelines_dir = compute_sub_path(
        normalized_guidelines, abs_guidelines, project_base
    )
    sub_test_dir = format_substituted_path(normalized_test).rstrip("/\\")
    token_test_path = f"`{sub_test_dir}/`" if sub_test_dir else ""
    sub_src_paths: list[str] = []
    for normalized_src, abs_src in zip(normalized_src_dirs, abs_src_dirs):
        sub_src = compute_sub_path(normalized_src, abs_src, project_base).rstrip("/\\")
        if sub_src:
            sub_src_paths.append(f"`{sub_src}/`")
    token_src_paths = ", ".join(sub_src_paths)
    if (
        guidelines_has_trailing_slash
        and sub_guidelines_dir
        and not sub_guidelines_dir.endswith("/")
    ):
        sub_guidelines_dir += "/"
    token_guidelines_dir = make_relative_token(sub_guidelines_dir, keep_trailing=True)

    req_root = project_base / ".req"
    req_root.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(f"OK: ensured directory {req_root}")

    # Copy models configuration to .req/models.json based on per-provider legacy mode (SRS-066)
    # Skip if --preserve-models is active
    any_legacy = any(pc["legacy"] for pc in provider_configs.values() if pc["enabled"])
    if not args.preserve_models:
        models_target = req_root / "models.json"
        if any_legacy:
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
    find_requirements_template(docs_templates)

    # Generate the file list for the %%GUIDELINES_FILES%% token.
    guidelines_file_list = generate_guidelines_file_list(
        project_base / normalized_guidelines, project_base
    )

    dlog(f"project_base={project_base}")
    dlog(f"DOCS_DIR={normalized_doc}")
    dlog(f"GUIDELINES_DIR={normalized_guidelines}")
    dlog(f"TESTS_DIR={normalized_test}")
    dlog(f"SRC_DIRS={normalized_src_dirs}")
    dlog(f"GUIDELINES_FILE_LIST={guidelines_file_list}")
    dlog(f"SUB_GUIDELINES_DIR={sub_guidelines_dir}")
    dlog(f"TOKEN_GUIDELINES_DIR={token_guidelines_dir}")

    codex_skills_root = None
    claude_skills_root = None
    gemini_skills_root = None
    opencode_skills_root = None
    pi_skills_root = None
    github_skills_root = None
    kiro_skills_root = None
    target_folders: list[Path] = []
    # Use per-provider configs to determine which directories to create (SRS-276).
    pc_codex = provider_configs["codex"]
    pc_github = provider_configs["github"]
    pc_gemini = provider_configs["gemini"]
    pc_kiro = provider_configs["kiro"]
    pc_claude = provider_configs["claude"]
    pc_opencode = provider_configs["opencode"]
    pc_pi = provider_configs["pi"]
    if pc_codex["enabled"] and pc_codex["prompts"]:
        target_folders.append(project_base / ".codex" / "prompts")
    if pc_codex["enabled"] and pc_codex["skills"]:
        codex_skills_root = project_base / ".codex" / "skills"
        target_folders.append(codex_skills_root)
    if pc_github["enabled"] and pc_github["agents"]:
        target_folders.append(project_base / ".github" / "agents")
    if pc_github["enabled"] and pc_github["prompts"]:
        target_folders.append(project_base / ".github" / "prompts")
    if pc_github["enabled"] and pc_github["skills"]:
        github_skills_root = project_base / ".github" / "skills"
        target_folders.append(github_skills_root)
    if pc_gemini["enabled"] and pc_gemini["prompts"]:
        target_folders.extend(
            [
                project_base / ".gemini" / "commands",
                project_base / ".gemini" / "commands" / "req",
            ]
        )
    if pc_gemini["enabled"] and pc_gemini["skills"]:
        gemini_skills_root = project_base / ".gemini" / "skills"
        target_folders.append(gemini_skills_root)
    if pc_kiro["enabled"] and pc_kiro["agents"]:
        target_folders.append(project_base / ".kiro" / "agents")
    if pc_kiro["enabled"] and pc_kiro["prompts"]:
        target_folders.append(project_base / ".kiro" / "prompts")
    if pc_kiro["enabled"] and pc_kiro["skills"]:
        kiro_skills_root = project_base / ".kiro" / "skills"
        target_folders.append(kiro_skills_root)
    if pc_claude["enabled"] and pc_claude["agents"]:
        target_folders.append(project_base / ".claude" / "agents")
    if pc_claude["enabled"] and pc_claude["prompts"]:
        target_folders.extend(
            [
                project_base / ".claude" / "commands",
                project_base / ".claude" / "commands" / "req",
            ]
        )
    if pc_claude["enabled"] and pc_claude["skills"]:
        claude_skills_root = project_base / ".claude" / "skills"
        target_folders.append(claude_skills_root)
    if pc_opencode["enabled"] and pc_opencode["agents"]:
        target_folders.append(project_base / ".opencode" / "agent")
    if pc_opencode["enabled"] and pc_opencode["prompts"]:
        target_folders.append(project_base / ".opencode" / "command")
    if pc_opencode["enabled"] and pc_opencode["skills"]:
        opencode_skills_root = project_base / ".opencode" / "skill"
        target_folders.append(opencode_skills_root)
    if pc_pi["enabled"] and pc_pi["prompts"]:
        target_folders.append(project_base / ".pi" / "prompts")
    if pc_pi["enabled"] and pc_pi["skills"]:
        pi_skills_root = project_base / ".pi" / "skills"
        target_folders.append(pi_skills_root)
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
    # Load CLI configs only if ANY provider requests model/tools (SRS-281).
    configs: dict[str, dict[str, Any] | None] = {}
    # Global include_models/include_tools determine whether to load centralized models.
    # Per-provider overrides are applied later in the generation loop.
    include_models = any(
        pc["enable-models"] for pc in provider_configs.values() if pc["enabled"]
    )
    include_tools = any(
        pc["enable-tools"] for pc in provider_configs.values() if pc["enabled"]
    )
    if include_models or include_tools:
        # Determine preserve_models_path (REQ-082)
        preserve_models_path = None
        if args.preserve_models and args.update:
            candidate_path = project_base / ".req" / "models.json"
            if candidate_path.is_file():
                preserve_models_path = candidate_path

        configs = load_centralized_models(
            RESOURCE_ROOT,
            legacy_mode=any_legacy,
            preserve_models_path=preserve_models_path,
        )
    prompts_installed: dict[str, set[str]] = {
        "claude": set(),
        "codex": set(),
        "github": set(),
        "gemini": set(),
        "kiro": set(),
        "opencode": set(),
        "pi": set(),
    }
    modules_installed: dict[str, set[str]] = {
        key: set() for key in prompts_installed.keys()
    }
    prompt_sources: list[tuple[str, Path]] = [
        *[("prompts", path) for path in sorted(prompts_dir.glob("*.md"))],
    ]
    for source_kind, prompt_path in prompt_sources:
        is_prompt_source = source_kind == "prompts"
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
        skill_desc_yaml = yaml_double_quote_escape(
            extract_skill_description(frontmatter)
        )
        claude_model = None
        claude_tools = None
        if configs:
            claude_model, claude_tools = get_model_tools_for_prompt(
                configs.get("claude"), PROMPT, "claude"
            )

        if is_prompt_source and pc_codex["enabled"] and pc_codex["prompts"]:
            # .codex/prompts
            dst_codex_prompt = project_base / ".codex" / "prompts" / f"req-{PROMPT}.md"
            existed = dst_codex_prompt.exists()
            write_text_file(dst_codex_prompt, prompt_with_replacements)
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_codex_prompt}")
            prompts_installed["codex"].add(PROMPT)
            modules_installed["codex"].add("prompts")

        if pc_codex["enabled"] and pc_codex["skills"] and codex_skills_root is not None:
            # .codex/skills/req-<prompt>/SKILL.md
            codex_skill_dir = codex_skills_root / f"req-{PROMPT}"
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
                f'description: "{skill_desc_yaml}"',
            ]
            if pc_codex["enable-models"] and codex_model:
                codex_header_lines.append(f"model: {codex_model}")
            if pc_codex["enable-tools"] and codex_tools:
                codex_header_lines.append(
                    f"tools: {format_tools_inline_list(codex_tools)}"
                )
            codex_skill_text = (
                "\n".join(codex_header_lines) + "\n---\n\n" + prompt_body_replaced
            )
            if not codex_skill_text.endswith("\n"):
                codex_skill_text += "\n"
            write_text_file(codex_skill_dir / "SKILL.md", codex_skill_text)
            prompts_installed["codex"].add(PROMPT)
            modules_installed["codex"].add("skills")

        if is_prompt_source and pc_gemini["enabled"] and pc_gemini["prompts"]:
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
            if configs and (pc_gemini["enable-models"] or pc_gemini["enable-tools"]):
                gem_model, gem_tools = get_model_tools_for_prompt(
                    configs.get("gemini"), PROMPT, "gemini"
                )
                if gem_model or gem_tools:
                    content = dst_toml.read_text(encoding="utf-8")
                    parts = content.split("\n", 1)
                    if len(parts) == 2:
                        first, rest = parts
                        inject_lines: list[str] = []
                        if pc_gemini["enable-models"] and gem_model:
                            inject_lines.append(f'model = "{gem_model}"')
                        if pc_gemini["enable-tools"] and gem_tools:
                            inject_lines.append(
                                f"tools = {format_tools_inline_list(gem_tools)}"
                            )
                        if inject_lines:
                            content = (
                                first + "\n" + "\n".join(inject_lines) + "\n" + rest
                            )
                            dst_toml.write_text(content, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_toml}")
            prompts_installed["gemini"].add(PROMPT)
            modules_installed["gemini"].add("commands")

        if is_prompt_source and pc_kiro["enabled"] and pc_kiro["prompts"]:
            # .kiro/prompts
            dst_kiro_prompt = project_base / ".kiro" / "prompts" / f"req-{PROMPT}.md"
            existed = dst_kiro_prompt.exists()
            write_text_file(dst_kiro_prompt, prompt_with_replacements)
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_kiro_prompt}")
            prompts_installed["kiro"].add(PROMPT)
            modules_installed["kiro"].add("prompts")

        if is_prompt_source and pc_claude["enabled"] and pc_claude["agents"]:
            # .claude/agents
            dst_claude_agent = project_base / ".claude" / "agents" / f"req-{PROMPT}.md"
            existed = dst_claude_agent.exists()
            claude_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{desc_yaml}"',
            ]
            if pc_claude["enable-models"] and claude_model:
                claude_header_lines.append(f"model: {claude_model}")
            if pc_claude["enable-tools"] and claude_tools:
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
            prompts_installed["claude"].add(PROMPT)
            modules_installed["claude"].add("agents")

        if is_prompt_source and pc_github["enabled"] and pc_github["agents"]:
            # .github/agents
            dst_gh_agent = (
                project_base / ".github" / "agents" / f"req-{PROMPT}.agent.md"
            )
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
            if pc_github["enable-models"] and gh_model:
                gh_header_lines.append(f"model: {gh_model}")
            if pc_github["enable-tools"] and gh_tools:
                gh_header_lines.append(f"tools: {format_tools_inline_list(gh_tools)}")
            gh_text = "\n".join(gh_header_lines) + "\n---\n\n" + prompt_body_replaced
            dst_gh_agent.parent.mkdir(parents=True, exist_ok=True)
            if not gh_text.endswith("\n"):
                gh_text += "\n"
            dst_gh_agent.write_text(gh_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_gh_agent}")
            prompts_installed["github"].add(PROMPT)
            modules_installed["github"].add("agents")

        if is_prompt_source and pc_github["enabled"] and pc_github["prompts"]:
            # .github/prompts
            dst_gh_prompt = (
                project_base / ".github" / "prompts" / f"req-{PROMPT}.prompt.md"
            )
            existed = dst_gh_prompt.exists()
            if pc_github["prompts-use-agents"]:
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
                if pc_github["enable-models"] and gh_model:
                    gh_header_lines.append(f"model: {gh_model}")
                if pc_github["enable-tools"] and gh_tools:
                    gh_header_lines.append(
                        f"tools: {format_tools_inline_list(gh_tools)}"
                    )
                gh_header = "\n".join(gh_header_lines) + "\n---\n\n"
                gh_prompt_text = gh_header + prompt_body_replaced
            dst_gh_prompt.parent.mkdir(parents=True, exist_ok=True)
            dst_gh_prompt.write_text(gh_prompt_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_gh_prompt}")
            prompts_installed["github"].add(PROMPT)
            modules_installed["github"].add("prompts")

        if is_prompt_source and pc_pi["enabled"] and pc_pi["prompts"]:
            # .pi/prompts (GitHub-equivalent prompt procedure)
            dst_pi_prompt = project_base / ".pi" / "prompts" / f"req-{PROMPT}.prompt.md"
            existed = dst_pi_prompt.exists()
            if pc_pi["prompts-use-agents"]:
                pi_prompt_text = f"---\nagent: req-{PROMPT}\n---\n"
            else:
                pi_header_lines = [
                    "---",
                    f"description: {frontmatter.splitlines()[0].split(':', 1)[1].strip() if 'description:' in frontmatter else description}",
                ]
                if argument_hint:
                    pi_header_lines.append(f"argument-hint: {argument_hint}")
                pi_model = None
                pi_tools = None
                if configs:
                    pi_model, pi_tools = get_model_tools_for_prompt(
                        configs.get("pi"), PROMPT, "pi"
                    )
                if pc_pi["enable-models"] and pi_model:
                    pi_header_lines.append(f"model: {pi_model}")
                if pc_pi["enable-tools"] and pi_tools:
                    pi_header_lines.append(
                        f"tools: {format_tools_inline_list(pi_tools)}"
                    )
                pi_header = "\n".join(pi_header_lines) + "\n---\n\n"
                pi_prompt_text = pi_header + prompt_body_replaced
            dst_pi_prompt.parent.mkdir(parents=True, exist_ok=True)
            dst_pi_prompt.write_text(pi_prompt_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_pi_prompt}")
            prompts_installed["pi"].add(PROMPT)
            modules_installed["pi"].add("prompts")

        if is_prompt_source and pc_kiro["enabled"] and pc_kiro["agents"]:
            # .kiro/agents
            dst_kiro_agent = project_base / ".kiro" / "agents" / f"req-{PROMPT}.json"
            existed = dst_kiro_agent.exists()
            kiro_prompt_rel = f".kiro/prompts/req-{PROMPT}.md"
            kiro_resources = generate_kiro_resources(
                project_base / normalized_doc,
                project_base,
                kiro_prompt_rel,
            )
            kiro_model, kiro_tools = get_model_tools_for_prompt(
                kiro_config, PROMPT, "kiro"
            )
            kiro_tools_list = (
                list(kiro_tools)
                if pc_kiro["enable-tools"] and isinstance(kiro_tools, list)
                else None
            )
            agent_content = render_kiro_agent(
                kiro_template,
                name=f"req-{PROMPT}",
                description=description,
                prompt=prompt_body_replaced,
                resources=kiro_resources,
                tools=kiro_tools_list,
                model=kiro_model,
                include_tools=pc_kiro["enable-tools"],
                include_model=pc_kiro["enable-models"],
            )
            dst_kiro_agent.write_text(agent_content, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_kiro_agent}")
            prompts_installed["kiro"].add(PROMPT)
            modules_installed["kiro"].add("agents")

        if is_prompt_source and pc_opencode["enabled"] and pc_opencode["agents"]:
            # .opencode/agent
            dst_opencode_agent = (
                project_base / ".opencode" / "agent" / f"req-{PROMPT}.md"
            )
            existed = dst_opencode_agent.exists()
            opencode_header_lines = ["---", f'description: "{desc_yaml}"', "mode: all"]
            if configs:
                oc_model, _ = get_model_tools_for_prompt(
                    configs.get("opencode"), PROMPT, "opencode"
                )
                oc_tools_raw = get_raw_tools_for_prompt(configs.get("opencode"), PROMPT)
                if pc_opencode["enable-models"] and oc_model:
                    opencode_header_lines.append(f"model: {oc_model}")
                if pc_opencode["enable-tools"] and oc_tools_raw is not None:
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
            prompts_installed["opencode"].add(PROMPT)
            modules_installed["opencode"].add("agent")

        if is_prompt_source and pc_opencode["enabled"] and pc_opencode["prompts"]:
            # .opencode/command
            dst_opencode_command = (
                project_base / ".opencode" / "command" / f"req-{PROMPT}.md"
            )
            existed = dst_opencode_command.exists()
            if pc_opencode["prompts-use-agents"]:
                command_text = f"---\nagent: req-{PROMPT}\n---\n"
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
                    oc_tools_raw = get_raw_tools_for_prompt(
                        configs.get("opencode"), PROMPT
                    )
                    if pc_opencode["enable-models"] and oc_model:
                        command_header_lines.append(f"model: {oc_model}")
                    if pc_opencode["enable-tools"] and oc_tools_raw is not None:
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

        if is_prompt_source and pc_claude["enabled"] and pc_claude["prompts"]:
            # .claude/commands/req
            dst_claude_command = (
                project_base / ".claude" / "commands" / "req" / f"{PROMPT}.md"
            )
            existed = dst_claude_command.exists()
            if pc_claude["prompts-use-agents"]:
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
                if pc_claude["enable-models"] and claude_model:
                    command_header_lines.append(
                        f'model: "{yaml_double_quote_escape(str(claude_model))}"'
                    )
                if pc_claude["enable-tools"] and claude_tools:
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
            prompts_installed["claude"].add(PROMPT)
            modules_installed["claude"].add("commands")

        if (
            pc_claude["enabled"]
            and pc_claude["skills"]
            and claude_skills_root is not None
        ):
            # .claude/skills/req-<prompt>/SKILL.md
            claude_skill_dir = claude_skills_root / f"req-{PROMPT}"
            claude_skill_dir.mkdir(parents=True, exist_ok=True)
            claude_skill_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{skill_desc_yaml}"',
            ]
            if pc_claude["enable-models"] and claude_model:
                claude_skill_header_lines.append(f"model: {claude_model}")
            if pc_claude["enable-tools"] and claude_tools:
                claude_skill_header_lines.append(
                    f"tools: {format_tools_inline_list(claude_tools)}"
                )
            claude_skill_text = (
                "\n".join(claude_skill_header_lines)
                + "\n---\n\n"
                + prompt_body_replaced
            )
            if not claude_skill_text.endswith("\n"):
                claude_skill_text += "\n"
            write_text_file(claude_skill_dir / "SKILL.md", claude_skill_text)
            prompts_installed["claude"].add(PROMPT)
            modules_installed["claude"].add("skills")

        if (
            pc_gemini["enabled"]
            and pc_gemini["skills"]
            and gemini_skills_root is not None
        ):
            # .gemini/skills/req-<prompt>/SKILL.md
            gemini_skill_dir = gemini_skills_root / f"req-{PROMPT}"
            gemini_skill_dir.mkdir(parents=True, exist_ok=True)
            gemini_skill_model = None
            gemini_skill_tools = None
            if configs:
                gemini_skill_model, gemini_skill_tools = get_model_tools_for_prompt(
                    configs.get("gemini"), PROMPT, "gemini"
                )
            gemini_skill_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{skill_desc_yaml}"',
            ]
            if pc_gemini["enable-models"] and gemini_skill_model:
                gemini_skill_header_lines.append(f"model: {gemini_skill_model}")
            if pc_gemini["enable-tools"] and gemini_skill_tools:
                gemini_skill_header_lines.append(
                    f"tools: {format_tools_inline_list(gemini_skill_tools)}"
                )
            gemini_skill_text = (
                "\n".join(gemini_skill_header_lines)
                + "\n---\n\n"
                + prompt_body_replaced
            )
            if not gemini_skill_text.endswith("\n"):
                gemini_skill_text += "\n"
            write_text_file(gemini_skill_dir / "SKILL.md", gemini_skill_text)
            prompts_installed["gemini"].add(PROMPT)
            modules_installed["gemini"].add("skills")

        if (
            pc_github["enabled"]
            and pc_github["skills"]
            and github_skills_root is not None
        ):
            # .github/skills/req-<prompt>/SKILL.md
            github_skill_dir = github_skills_root / f"req-{PROMPT}"
            github_skill_dir.mkdir(parents=True, exist_ok=True)
            github_skill_model = None
            github_skill_tools = None
            if configs:
                github_skill_model, github_skill_tools = get_model_tools_for_prompt(
                    configs.get("copilot"), PROMPT, "copilot"
                )
            github_skill_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{skill_desc_yaml}"',
            ]
            if pc_github["enable-models"] and github_skill_model:
                github_skill_header_lines.append(f"model: {github_skill_model}")
            if pc_github["enable-tools"] and github_skill_tools:
                github_skill_header_lines.append(
                    f"tools: {format_tools_inline_list(github_skill_tools)}"
                )
            github_skill_text = (
                "\n".join(github_skill_header_lines)
                + "\n---\n\n"
                + prompt_body_replaced
            )
            if not github_skill_text.endswith("\n"):
                github_skill_text += "\n"
            write_text_file(github_skill_dir / "SKILL.md", github_skill_text)
            prompts_installed["github"].add(PROMPT)
            modules_installed["github"].add("skills")

        if pc_pi["enabled"] and pc_pi["skills"] and pi_skills_root is not None:
            # .pi/skills/req-<prompt>/SKILL.md (GitHub-equivalent skill procedure)
            pi_skill_dir = pi_skills_root / f"req-{PROMPT}"
            pi_skill_dir.mkdir(parents=True, exist_ok=True)
            pi_skill_model = None
            pi_skill_tools = None
            if configs:
                pi_skill_model, pi_skill_tools = get_model_tools_for_prompt(
                    configs.get("pi"), PROMPT, "pi"
                )
            pi_skill_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{skill_desc_yaml}"',
            ]
            if pc_pi["enable-models"] and pi_skill_model:
                pi_skill_header_lines.append(f"model: {pi_skill_model}")
            if pc_pi["enable-tools"] and pi_skill_tools:
                pi_skill_header_lines.append(
                    f"tools: {format_tools_inline_list(pi_skill_tools)}"
                )
            pi_skill_text = (
                "\n".join(pi_skill_header_lines) + "\n---\n\n" + prompt_body_replaced
            )
            if not pi_skill_text.endswith("\n"):
                pi_skill_text += "\n"
            write_text_file(pi_skill_dir / "SKILL.md", pi_skill_text)
            prompts_installed["pi"].add(PROMPT)
            modules_installed["pi"].add("skills")

        if pc_kiro["enabled"] and pc_kiro["skills"] and kiro_skills_root is not None:
            # .kiro/skills/req-<prompt>/SKILL.md
            kiro_skill_dir = kiro_skills_root / f"req-{PROMPT}"
            kiro_skill_dir.mkdir(parents=True, exist_ok=True)
            kiro_skill_model, kiro_skill_tools = get_model_tools_for_prompt(
                kiro_config, PROMPT, "kiro"
            )
            kiro_skill_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{skill_desc_yaml}"',
            ]
            if pc_kiro["enable-models"] and kiro_skill_model:
                kiro_skill_header_lines.append(f"model: {kiro_skill_model}")
            if (
                pc_kiro["enable-tools"]
                and isinstance(kiro_skill_tools, list)
                and kiro_skill_tools
            ):
                kiro_skill_header_lines.append(
                    f"tools: {format_tools_inline_list(kiro_skill_tools)}"
                )
            kiro_skill_text = (
                "\n".join(kiro_skill_header_lines) + "\n---\n\n" + prompt_body_replaced
            )
            if not kiro_skill_text.endswith("\n"):
                kiro_skill_text += "\n"
            write_text_file(kiro_skill_dir / "SKILL.md", kiro_skill_text)
            prompts_installed["kiro"].add(PROMPT)
            modules_installed["kiro"].add("skills")

        if (
            pc_opencode["enabled"]
            and pc_opencode["skills"]
            and opencode_skills_root is not None
        ):
            # .opencode/skill/req-<prompt>/SKILL.md
            opencode_skill_dir = opencode_skills_root / f"req-{PROMPT}"
            opencode_skill_dir.mkdir(parents=True, exist_ok=True)
            opencode_skill_header_lines = [
                "---",
                f"name: req-{PROMPT}",
                f'description: "{skill_desc_yaml}"',
            ]
            if configs:
                oc_skill_model, _ = get_model_tools_for_prompt(
                    configs.get("opencode"), PROMPT, "opencode"
                )
                oc_skill_tools_raw = get_raw_tools_for_prompt(
                    configs.get("opencode"), PROMPT
                )
                if pc_opencode["enable-models"] and oc_skill_model:
                    opencode_skill_header_lines.append(f"model: {oc_skill_model}")
                if pc_opencode["enable-tools"] and oc_skill_tools_raw is not None:
                    if isinstance(oc_skill_tools_raw, list):
                        opencode_skill_header_lines.append(
                            f"tools: {format_tools_inline_list(oc_skill_tools_raw)}"
                        )
                    elif isinstance(oc_skill_tools_raw, str):
                        opencode_skill_header_lines.append(
                            f'tools: "{yaml_double_quote_escape(oc_skill_tools_raw)}"'
                        )
            opencode_skill_text = (
                "\n".join(opencode_skill_header_lines)
                + "\n---\n\n"
                + prompt_body_replaced
            )
            if not opencode_skill_text.endswith("\n"):
                opencode_skill_text += "\n"
            write_text_file(opencode_skill_dir / "SKILL.md", opencode_skill_text)
            prompts_installed["opencode"].add(PROMPT)
            modules_installed["opencode"].add("skills")

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
    guidelines_items = generate_guidelines_file_items(
        project_base / normalized_guidelines, project_base
    )

    if guidelines_items:
        for entry in guidelines_items:
            print(f"- {entry}")
    else:
        print("The folder %%GUIDELINES_FILES%% does not contain any files")

    # Build and print installation report table with provider artifact/options details.
    def _format_install_table(
        modules_map: dict[str, list[str]],
        prompts_map: dict[str, set[str]],
    ) -> list[str]:
        """!
        @brief Format the Unicode installation summary table.
        @details Builds a deterministic box-drawing table with columns: Provider, Prompts Installed, Modules Installed.
        Prompts Installed is wrapped to a maximum width of 50 characters. Modules Installed renders one non-wrapped
        line per active artifact as `artifact` when no options are active, or `artifact:options` when options exist.
        Borders are emitted with Unicode line-drawing characters and bright-red ANSI styling.
        @note Complexity: O(C * (P log P + M)) where C is provider count, P is prompts per provider, M is module-entry lines per provider.
        @note Side effects: None (pure formatting).
        @param modules_map {dict[str, list[str]]} Mapping: provider name -> module-entry lines in `artifact` or `artifact:options` format.
        @param prompts_map {dict[str, set[str]]} Mapping: provider name -> installed prompt identifiers (union across artifact types).
        @return {list[str]} Fully formatted table lines (including separators) ready for printing.
        """
        columns = ("Provider", "Prompts Installed", "Modules Installed")
        rows: list[tuple[str, str, str]] = []
        for provider_name in sorted(prompts_map.keys()):
            prompts = sorted(prompts_map.get(provider_name, ()))
            if not prompts:
                continue
            prompts_text = ", ".join(prompts) if prompts else "-"
            module_lines = modules_map.get(provider_name, [])
            modules_text = "\n".join(module_lines) if module_lines else "-"
            rows.append((provider_name, prompts_text, modules_text))

        if not rows:
            rows = [("-", "-", "-")]

        provider_width = max(len(columns[0]), max(len(row[0]) for row in rows))
        prompt_cells = [columns[1], *[row[1] for row in rows]]
        prompt_width = min(50, max(len(cell) for cell in prompt_cells))
        modules_width = len(columns[2])
        for row in rows:
            modules_width = max(
                modules_width, max(len(line) for line in row[2].splitlines() or [""])
            )

        def _wrap_cell(value: str, width: int, allow_wrap: bool) -> list[str]:
            """! @brief Normalize one table cell to printable lines.
            @details Preserves explicit newline-separated segments. When wrapping is enabled, wraps each segment to the target width; otherwise keeps each segment as-is.
            @param value {str} Cell text payload.
            @param width {int} Maximum cell width.
            @param allow_wrap {bool} Whether to apply line wrapping.
            @return {list[str]} Normalized printable lines for the cell.
            """
            raw_lines = value.splitlines() or [""]
            lines: list[str] = []
            for raw_line in raw_lines:
                if allow_wrap:
                    wrapped = textwrap.wrap(
                        raw_line,
                        width=width,
                        break_long_words=True,
                        break_on_hyphens=False,
                    )
                    lines.extend(wrapped if wrapped else [""])
                else:
                    lines.append(raw_line)
            return lines if lines else [""]

        def _render_row(provider: str, prompts: str, modules: str) -> list[str]:
            """!
            @brief Render one logical table row into one or more physical lines.
            @details Applies per-cell wrapping and left alignment, then expands the row height to the maximum wrapped cell line count.
            @param provider {str} Provider cell text.
            @param prompts {str} Prompts Installed cell text.
            @param modules {str} Modules Installed cell text.
            @return {list[str]} Physical row lines encoded with box-drawing separators.
            """
            provider_lines = _wrap_cell(provider, provider_width, allow_wrap=False)
            prompt_lines = _wrap_cell(prompts, prompt_width, allow_wrap=True)
            module_lines = _wrap_cell(modules, modules_width, allow_wrap=False)
            row_height = max(len(provider_lines), len(prompt_lines), len(module_lines))
            lines: list[str] = []
            for idx in range(row_height):
                provider_part = (
                    provider_lines[idx] if idx < len(provider_lines) else ""
                ).ljust(provider_width)
                prompt_part = (
                    prompt_lines[idx] if idx < len(prompt_lines) else ""
                ).ljust(prompt_width)
                module_part = (
                    module_lines[idx] if idx < len(module_lines) else ""
                ).ljust(modules_width)
                lines.append(f"│ {provider_part} │ {prompt_part} │ {module_part} │")
            return lines

        top = f"┌{'─' * (provider_width + 2)}┬{'─' * (prompt_width + 2)}┬{'─' * (modules_width + 2)}┐"
        middle = f"├{'─' * (provider_width + 2)}┼{'─' * (prompt_width + 2)}┼{'─' * (modules_width + 2)}┤"
        bottom = f"└{'─' * (provider_width + 2)}┴{'─' * (prompt_width + 2)}┴{'─' * (modules_width + 2)}┘"

        lines: list[str] = [top]
        lines.extend(_render_row(*columns))
        lines.append(middle)
        for index, row in enumerate(rows):
            lines.extend(_render_row(*row))
            if index != len(rows) - 1:
                lines.append(middle)
        lines.append(bottom)
        return lines

    def _build_provider_modules_map(provider_specs: list[str]) -> dict[str, list[str]]:
        """!
        @brief Build provider-to-module-entry mapping for installation table rendering.
        @details Parses raw `--provider` specifications preserving token order, then emits one module-entry line per active artifact as `artifact` or `artifact:options`.
        @param provider_specs {list[str]} Raw `--provider` SPEC values after update-merging logic.
        @return {dict[str, list[str]]} Mapping from provider to ordered module-entry lines.
        """
        artifacts_ordered: dict[str, list[str]] = {
            provider_name: [] for provider_name in sorted(VALID_PROVIDERS)
        }
        options_ordered: dict[str, list[str]] = {
            provider_name: [] for provider_name in sorted(VALID_PROVIDERS)
        }
        for raw_spec in provider_specs:
            parts = raw_spec.split(":")
            if len(parts) < 2:
                continue
            provider_name = parts[0].strip().lower()
            if provider_name not in VALID_PROVIDERS:
                continue
            for artifact in [
                v.strip().lower() for v in parts[1].split(",") if v.strip()
            ]:
                if (
                    artifact in VALID_ARTIFACTS
                    and artifact not in artifacts_ordered[provider_name]
                ):
                    artifacts_ordered[provider_name].append(artifact)
            if len(parts) == 3:
                for option in [
                    v.strip().lower() for v in parts[2].split(",") if v.strip()
                ]:
                    if (
                        option in VALID_PROVIDER_OPTIONS
                        and option not in options_ordered[provider_name]
                    ):
                        options_ordered[provider_name].append(option)
        modules_map: dict[str, list[str]] = {}
        for provider_name in sorted(VALID_PROVIDERS):
            options = options_ordered[provider_name]
            if options:
                options_text = ",".join(options)
                modules_map[provider_name] = [
                    f"{artifact}:{options_text}"
                    for artifact in artifacts_ordered[provider_name]
                ]
            else:
                modules_map[provider_name] = list(artifacts_ordered[provider_name])
        return modules_map

    def _colorize_table_border(line: str) -> str:
        """!
        @brief Colorize box-drawing border glyphs with bright-red ANSI style.
        @details Applies color to border characters while preserving cell payload text color.
        @param line {str} One already-rendered table line.
        @return {str} Line with border glyphs wrapped in ANSI bright-red and reset sequences.
        """
        border_chars = frozenset("┌┬┐├┼┤└┴┘─│")
        return "".join(
            f"{ANSI_BRIGHT_RED}{char}{ANSI_RESET}" if char in border_chars else char
            for char in line
        )

    table_lines = _format_install_table(
        _build_provider_modules_map(effective_provider_specs), prompts_installed
    )
    for table_line in table_lines:
        print(_colorize_table_border(table_line))


# ── Excluded directories for project-scan file selection ──────────────────

EXCLUDED_DIRS: frozenset[str] = frozenset()
"""Directories additionally excluded from project scan after `.gitignore` filtering."""

# ── Supported source file extensions ──────────────────────────────────────

SUPPORTED_EXTENSIONS = frozenset(
    {
        ".c",
        ".cpp",
        ".cs",
        ".ex",
        ".go",
        ".hs",
        ".java",
        ".js",
        ".mjs",
        ".kt",
        ".lua",
        ".pl",
        ".php",
        ".py",
        ".rb",
        ".rs",
        ".scala",
        ".sh",
        ".swift",
        ".ts",
        ".zig",
    }
)
"""File extensions considered during source directory scanning."""


def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]:
    """!
    @brief Collect source files from git-indexed project paths.
        @details Uses `git ls-files --cached --others --exclude-standard` in project root, filters by src-dir prefixes, applies EXCLUDED_DIRS filtering, and keeps only SUPPORTED_EXTENSIONS files.
    @param src_dirs Input parameter `src_dirs`.
    @param project_base Input parameter `project_base`.
    @return {list[str]} Function return value.
    """
    cmd = [
        "git",
        "-C",
        str(project_base),
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
    ]
    try:
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError:
        raise ReqError(
            "Error: failed to collect source files with `git ls-files` in project root.",
            1,
        )

    normalized_src_dirs: list[str] = []
    for src_dir in src_dirs:
        normalized = make_relative_if_contains_project(src_dir, project_base)
        normalized = Path(normalized).as_posix().strip("/")
        normalized_src_dirs.append(normalized)

    collected: set[str] = set()
    for rel_path in output.splitlines():
        rel_posix = Path(rel_path.strip()).as_posix()
        if rel_posix.startswith("./"):
            rel_posix = rel_posix[2:]
        if not rel_posix:
            continue
        if not any(
            src_dir in {"", "."}
            or rel_posix == src_dir
            or rel_posix.startswith(f"{src_dir}/")
            for src_dir in normalized_src_dirs
        ):
            continue
        rel_obj = Path(rel_posix)
        if any(part in EXCLUDED_DIRS for part in rel_obj.parts[:-1]):
            continue
        if rel_obj.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        collected.add(str((project_base / rel_obj).resolve()))
    return sorted(collected)


def _build_ascii_tree(paths: list[str]) -> str:
    """!
    @brief Build a deterministic tree string from project-relative paths.
        @param paths Project-relative file paths.
        @return Rendered tree rooted at '.'.
    @details Implements the _build_ascii_tree function behavior with deterministic control flow.
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
        """! @brief Emit one subtree in deterministic ASCII-tree order.
        @details Traverses child entries sorted lexicographically, appends connector glyphs (`├──`, `└──`) to `lines`, and recursively emits nested directories while preserving tree indentation state in `prefix`.
        @param branch {dict[str, dict[str, Any] | None]} Current subtree mapping where `None` denotes file leaf and `dict` denotes directory node.
        @param prefix {str} Prefix containing indentation and vertical-branch markers for current depth.
        @return {None} This helper mutates closure variable `lines` with formatted rows.
        """
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
    """!
    @brief Format markdown section containing the scanned files tree.
        @param files Absolute file paths selected for --references processing.
        @param project_base Project root used to normalize relative paths.
        @return Markdown section with heading and fenced tree.
    @details Implements the _format_files_structure_markdown function behavior with deterministic control flow.
    """
    rel_paths = [
        Path(path).resolve().relative_to(project_base).as_posix() for path in files
    ]
    tree = _build_ascii_tree(rel_paths)
    return f"# Files Structure\n```\n{tree}\n```"


def _is_standalone_command(args: Namespace) -> bool:
    """!
    @brief Check if the parsed args contain a standalone file command.
    @param args Parsed CLI namespace.
    @return True when any file-scope standalone flag is present.
    @details Standalone commands require no `--base`/`--here`: `--files-tokens`,
      `--files-references`, `--files-compress`, `--files-find`, `--test-static-check`,
      and `--files-static-check`. SRS-253 adds `--files-static-check` to this group.
    """
    return bool(
        getattr(args, "files_tokens", None)
        or getattr(args, "files_references", None)
        or getattr(args, "files_compress", None)
        or getattr(args, "files_find", None)
        or (getattr(args, "test_static_check", None) is not None)
        or getattr(args, "files_static_check", None)
    )


def _is_project_scan_command(args: Namespace) -> bool:
    """!
    @brief Check if the parsed args contain a project-scan command.
    @param args Parsed CLI namespace.
    @return True when any project-scan flag is present.
    @details Project-scan commands: `--references`, `--compress`, `--tokens`, `--find`,
      `--static-check`, `--git-check`, `--docs-check`, `--git-wt-name`, `--git-wt-create`,
      `--git-wt-delete`, `--git-path`, and `--get-base-path`.
    """
    return bool(
        getattr(args, "references", False)
        or getattr(args, "compress", False)
        or getattr(args, "tokens", False)
        or getattr(args, "find", None)
        or getattr(args, "static_check", False)
        or getattr(args, "git_check", False)
        or getattr(args, "docs_check", False)
        or getattr(args, "git_wt_name", False)
        or getattr(args, "git_wt_create", None)
        or getattr(args, "git_wt_delete", None)
        or getattr(args, "git_path_cmd", False)
        or getattr(args, "get_base_path_cmd", False)
    )


def _is_here_only_project_scan_command(args: Namespace) -> bool:
    """!
    @brief Check if args request a project-scan command restricted to `--here` mode.
    @param args Parsed CLI namespace.
    @return True when command requires implicit `--here` and rejects `--base`.
    @details Includes `--references`, `--compress`, `--tokens`, `--find`, `--static-check`,
      `--git-check`, `--docs-check`, `--git-wt-name`, `--git-wt-create`, `--git-wt-delete`,
      `--git-path`, and `--get-base-path`.
    @satisfies SRS-311, SRS-313, SRS-318, SRS-320, SRS-326, SRS-333
    """
    return bool(
        getattr(args, "references", False)
        or getattr(args, "compress", False)
        or getattr(args, "tokens", False)
        or getattr(args, "find", None)
        or getattr(args, "static_check", False)
        or getattr(args, "git_check", False)
        or getattr(args, "docs_check", False)
        or getattr(args, "git_wt_name", False)
        or getattr(args, "git_wt_create", None)
        or getattr(args, "git_wt_delete", None)
        or getattr(args, "git_path_cmd", False)
        or getattr(args, "get_base_path_cmd", False)
    )


def run_git_check(args: Namespace) -> None:
    """!
    @brief Execute --git-check: verify clean git status and valid HEAD.
    @param args Parsed CLI namespace.
    @return {None} Function return value.
    @throws ReqError On git status unclear or config load failure.
    @satisfies SRS-311, SRS-312
    """
    project_base = _resolve_project_base(args)
    full_cfg = load_full_config(project_base)
    git_path = full_cfg.get("git-path")
    if not git_path or not Path(git_path).is_dir():
        raise ReqError("Error: git-path not configured or does not exist.", 11)
    cmd = (
        "git rev-parse --is-inside-work-tree "
        "&& ! git status --porcelain | grep -q . "
        "&& { git symbolic-ref -q HEAD || git rev-parse --verify HEAD ; }"
    )
    try:
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
            cwd=git_path,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        raise ReqError("ERROR: Git status unclear!", 1)
    if result.returncode != 0:
        raise ReqError("ERROR: Git status unclear!", 1)


def run_docs_check(args: Namespace) -> None:
    """!
    @brief Execute --docs-check: verify existence of REQUIREMENTS.md, WORKFLOW.md, REFERENCES.md.
    @param args Parsed CLI namespace.
    @return {None} Function return value.
    @throws ReqError If any required doc file is missing.
    @satisfies SRS-313, SRS-314, SRS-315, SRS-316, SRS-317
    """
    project_base = _resolve_project_base(args)
    full_cfg = load_full_config(project_base)
    base_path = full_cfg.get("base-path", str(project_base))
    docs_dir = full_cfg.get("docs-dir", "docs")
    if isinstance(docs_dir, str):
        docs_dir = docs_dir.rstrip("/\\")
    doc_path = Path(base_path) / docs_dir
    for filename, prompt_cmd in [
        ("REQUIREMENTS.md", "/req-write"),
        ("WORKFLOW.md", "/req-workflow"),
        ("REFERENCES.md", "/req-references"),
    ]:
        full_path = doc_path / filename
        if not full_path.is_file():
            msg = (
                f"ERROR: File {doc_path}/{filename} does not exist, "
                f"generate it with the {prompt_cmd} prompt!"
            )
            print(msg)
            raise ReqError(msg, 1)


def run_git_wt_name(args: Namespace) -> None:
    """!
    @brief Execute --git-wt-name: print standardized worktree name.
    @param args Parsed CLI namespace.
    @return {None} Function return value.
    @satisfies SRS-318, SRS-319
    """
    project_base = _resolve_project_base(args)
    full_cfg = load_full_config(project_base)
    git_path = full_cfg.get("git-path")
    if not git_path or not Path(git_path).is_dir():
        raise ReqError("Error: git-path not configured or does not exist.", 11)
    project_name = Path(git_path).name
    try:
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=git_path,
            timeout=10,
        )
        branch = branch_result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        branch = "unknown"
    sanitized_branch = sanitize_branch_name(branch)
    execution_id = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"useReq-{project_name}-{sanitized_branch}-{execution_id}")


def _worktree_path_exists_exact(git_path: Path, target_path: Path) -> bool:
    """!
    @brief Check whether a git worktree exists at the exact target path.
    @param git_path Absolute git root path used as command cwd.
    @param target_path Absolute worktree path expected for WT_NAME.
    @return {bool} True only when target_path is listed as an exact worktree path.
    @throws ReqError On git command execution errors.
    @details Parses `git worktree list --porcelain` output by `worktree <path>` records and performs exact path comparison to prevent partial-name or substring matches.
    """
    try:
        wt_list = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(git_path),
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        raise ReqError("Error: unable to query git worktree list.", 3)
    if wt_list.returncode != 0:
        raise ReqError("Error: unable to query git worktree list.", 3)
    target_norm = str(target_path.resolve())
    for line in wt_list.stdout.splitlines():
        if line.startswith("worktree "):
            listed_path = line[len("worktree ") :].strip()
            if Path(listed_path).resolve() == Path(target_norm):
                return True
    return False


def _rollback_worktree_create(git_path: Path, wt_path: Path, wt_name: str) -> None:
    """!
    @brief Roll back worktree and branch created by --git-wt-create on post-create failure.
    @param git_path Absolute git root path used as command cwd.
    @param wt_path Absolute worktree path to remove.
    @param wt_name Exact branch name to delete.
    @return {None} Function return value.
    @throws ReqError If rollback cannot remove the exact target worktree and branch.
    @details Uses `git worktree remove <path> --force` and `git branch -D <name>` to restore a clean git state when post-create copy/chdir operations fail.
    """
    try:
        remove_result = subprocess.run(
            ["git", "worktree", "remove", str(wt_path), "--force"],
            capture_output=True,
            text=True,
            cwd=str(git_path),
            timeout=30,
        )
        branch_result = subprocess.run(
            ["git", "branch", "-D", wt_name],
            capture_output=True,
            text=True,
            cwd=str(git_path),
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        raise ReqError(
            f"ERROR: Rollback failed for worktree or branch {wt_name}.",
            1,
        )
    if remove_result.returncode != 0 or branch_result.returncode != 0:
        raise ReqError(
            f"ERROR: Rollback failed for worktree or branch {wt_name}.",
            1,
        )


def run_git_wt_create(args: Namespace) -> None:
    """!
    @brief Execute --git-wt-create: create a git worktree and copy .req/provider dirs.
    @param args Parsed CLI namespace.
    @return {None} Function return value.
    @throws ReqError On invalid name, git command failure, or config errors.
    @satisfies SRS-320, SRS-321, SRS-322, SRS-323, SRS-324, SRS-325, SRS-331, SRS-335
    """
    wt_name: str = args.git_wt_create
    if not validate_wt_name(wt_name):
        msg = f"ERROR: Invalid worktree/branch name: {wt_name}."
        print(msg)
        raise ReqError(msg, 1)
    project_base = _resolve_project_base(args)
    full_cfg = load_full_config(project_base)
    git_path_str = full_cfg.get("git-path")
    base_path_str = full_cfg.get("base-path", str(project_base))
    if not git_path_str:
        raise ReqError("Error: git-path not configured or does not exist.", 11)
    git_path = Path(git_path_str)
    if not git_path.is_absolute():
        git_path = project_base / git_path
    if not git_path.is_dir():
        raise ReqError("Error: git-path not configured or does not exist.", 11)
    git_path = git_path.resolve()

    base_path = Path(base_path_str)
    if not base_path.is_absolute():
        base_path = project_base / base_path
    base_path = base_path.resolve()
    parent_path = git_path.parent
    # SRS-309: base-dir = relative path from git-path to base-path.
    try:
        base_dir = base_path.relative_to(git_path)
    except ValueError:
        base_dir = Path(".")
    # SRS-322: create worktree + branch.
    wt_dest = parent_path / wt_name
    try:
        result = subprocess.run(
            ["git", "worktree", "add", str(wt_dest), "-b", wt_name],
            capture_output=True,
            text=True,
            cwd=str(git_path),
            timeout=30,
        )
        if result.returncode != 0:
            raise ReqError(
                f"Error: git worktree add failed: {result.stderr.strip()}", 1
            )
    except FileNotFoundError:
        raise ReqError("Error: git is not available on PATH.", 3)
    except subprocess.TimeoutExpired:
        raise ReqError("Error: git worktree add timed out.", 3)
    wt_base_dir = wt_dest / base_dir
    try:
        # SRS-323: copy .req if not present in new worktree.
        wt_req = wt_base_dir / ".req"
        src_req = base_path / ".req"
        if src_req.is_dir() and not wt_req.is_dir():
            shutil.copytree(str(src_req), str(wt_req))
        # SRS-324, SRS-325: copy active provider directories.
        providers_specs = full_cfg.get("providers", [])
        active_providers: set[str] = set()
        if isinstance(providers_specs, list):
            for spec in providers_specs:
                if isinstance(spec, str) and ":" in spec:
                    active_providers.add(spec.split(":")[0].lower())
        for provider, dirs in PROVIDER_DIR_MAP.items():
            if provider not in active_providers:
                continue
            for rel_dir in dirs:
                src_dir = base_path / rel_dir
                dst_dir = wt_base_dir / rel_dir
                if src_dir.is_dir() and not dst_dir.is_dir():
                    shutil.copytree(str(src_dir), str(dst_dir))
        # SRS-335: copy .venv from base-path first, then git-path, preserving path from git-path.
        src_venv: Optional[Path] = None
        base_venv = base_path / ".venv"
        git_venv = git_path / ".venv"
        rel_venv = Path(".venv")
        if base_venv.is_dir():
            src_venv = base_venv
            rel_venv = base_dir / ".venv"
        elif git_venv.is_dir():
            src_venv = git_venv
            rel_venv = Path(".venv")
        if src_venv is not None:
            dst_venv = wt_dest / rel_venv
            if not dst_venv.is_dir():
                dst_venv.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(str(src_venv), str(dst_venv))
    except (OSError, ReqError):
        _rollback_worktree_create(git_path, wt_dest, wt_name)
        raise ReqError(
            f"ERROR: Unable to finalize worktree creation for {wt_name}.",
            1,
        )


def run_git_wt_delete(args: Namespace) -> None:
    """!
    @brief Execute --git-wt-delete: remove a git worktree and branch by name.
    @param args Parsed CLI namespace.
    @return {None} Function return value.
    @throws ReqError On invalid name or git removal failure.
    @satisfies SRS-326, SRS-327, SRS-328, SRS-332
    """
    wt_name: str = args.git_wt_delete
    project_base = _resolve_project_base(args)
    full_cfg = load_full_config(project_base)
    git_path_str = full_cfg.get("git-path")
    if not git_path_str or not Path(git_path_str).is_dir():
        raise ReqError("Error: git-path not configured or does not exist.", 11)
    git_path = Path(git_path_str)
    parent_path = git_path.parent
    # SRS-327: validate branch or worktree exists.
    branch_exists = False
    try:
        br = subprocess.run(
            ["git", "show-ref", "--verify", f"refs/heads/{wt_name}"],
            capture_output=True,
            text=True,
            cwd=str(git_path),
            timeout=10,
        )
        if br.returncode == 0:
            branch_exists = True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    wt_path = parent_path / wt_name
    try:
        wt_exists = _worktree_path_exists_exact(git_path, wt_path)
    except ReqError:
        wt_exists = False
    if not branch_exists and not wt_exists:
        msg = f"ERROR: Invalid worktree or branch name: {wt_name}."
        print(msg)
        raise ReqError(msg, 1)
    # SRS-328: remove worktree and branch.
    error_occurred = False
    base_path_str = full_cfg.get("base-path", str(project_base))
    base_path = Path(base_path_str)
    if not base_path.is_dir():
        raise ReqError("Error: base-path not configured or does not exist.", 11)
    os.chdir(base_path)
    if wt_exists:
        try:
            r1 = subprocess.run(
                ["git", "worktree", "remove", str(wt_path), "--force"],
                capture_output=True,
                text=True,
                cwd=str(base_path),
                timeout=30,
            )
            if r1.returncode != 0:
                error_occurred = True
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            error_occurred = True
    if branch_exists:
        try:
            r2 = subprocess.run(
                ["git", "branch", "-D", wt_name],
                capture_output=True,
                text=True,
                cwd=str(base_path),
                timeout=10,
            )
            if r2.returncode != 0:
                error_occurred = True
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            error_occurred = True
    if error_occurred:
        msg = f"ERROR: Unable to remove worktree or branch {wt_name}."
        print(msg)
        raise ReqError(msg, 1)


def run_git_path(args: Namespace) -> None:
    """!
    @brief Execute --git-path: print configured git-path from `.req/config.json`.
    @param args Parsed CLI namespace.
    @return {None} Function return value.
    @throws ReqError If `.req/config.json` is not present.
    @satisfies SRS-333, SRS-334
    """
    project_base = _resolve_project_base(args)
    full_cfg = load_full_config(project_base)
    print(str(full_cfg.get("git-path", "")))


def run_get_base_path(args: Namespace) -> None:
    """!
    @brief Execute --get-base-path: print configured base-path from `.req/config.json`.
    @param args Parsed CLI namespace.
    @return {None} Function return value.
    @throws ReqError If `.req/config.json` is not present.
    @satisfies SRS-333, SRS-347
    """
    project_base = _resolve_project_base(args)
    full_cfg = load_full_config(project_base)
    print(str(full_cfg.get("base-path", "")))


def run_files_tokens(files: list[str]) -> None:
    """!
    @brief Execute --files-tokens: count tokens for arbitrary files.
    @details Implements the run_files_tokens function behavior with deterministic control flow.
    @param files Input parameter `files`.
    @return {None} Function return value.
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
    """!
    @brief Execute --files-references: generate markdown for arbitrary files.
    @details Implements the run_files_references function behavior with deterministic control flow.
    @param files Input parameter `files`.
    @return {None} Function return value.
    """
    from .generate_markdown import generate_markdown

    md = generate_markdown(
        files,
        verbose=VERBOSE,
        output_base=Path.cwd().resolve(),
    )
    print(md)


def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None:
    """!
    @brief Execute --files-compress: compress arbitrary files.
        @param files List of source file paths to compress.
        @param enable_line_numbers If True, emits <n>: prefixes in compressed entries.
        @details Renders output header paths relative to current working directory.
    @return {None} Function return value.
    """
    from .compress_files import compress_files

    output = compress_files(
        files,
        include_line_numbers=enable_line_numbers,
        verbose=VERBOSE,
        output_base=Path.cwd().resolve(),
    )
    print(output)


def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None:
    """!
    @brief Execute --files-find: find constructs in arbitrary files.
        @param args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...].
        @param enable_line_numbers If True, emits <n>: prefixes in output.
    @details Implements the run_files_find function behavior with deterministic control flow.
    @return {None} Function return value.
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
    """!
    @brief Execute --references: generate markdown for project source files.
    @details Implements the run_references function behavior with deterministic control flow.
    @param args Input parameter `args`.
    @return {None} Function return value.
    """
    from .generate_markdown import generate_markdown

    project_base, src_dirs = _resolve_project_src_dirs(args)
    files = _collect_source_files(src_dirs, project_base)
    if not files:
        raise ReqError("Error: no source files found in configured directories.", 1)
    md = generate_markdown(files, verbose=VERBOSE, output_base=project_base)
    files_structure = _format_files_structure_markdown(files, project_base)
    print(f"{files_structure}\n\n{md}")


def run_compress_cmd(args: Namespace) -> None:
    """!
    @brief Execute --compress: compress project source files.
        @param args Parsed CLI arguments namespace.
    @details Implements the run_compress_cmd function behavior with deterministic control flow.
    @return {None} Function return value.
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
        output_base=project_base,
    )
    print(output)


def run_find(args: Namespace) -> None:
    """!
    @brief Execute --find: find constructs in project source files.
        @param args Parsed CLI arguments namespace.
        @throws ReqError If no source files found or no constructs match criteria with available TAGs listing.
    @details Implements the run_find function behavior with deterministic control flow.
    @return {None} Function return value.
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
    """! @brief Execute --tokens on the canonical documentation files in --docs-dir.
    @param args Parsed CLI arguments namespace.
    @return None.
    @exception ReqError Raised when no canonical documentation file exists in configured docs-dir.
    @details Uses docs-dir from .req/config.json in here-only mode, ignores explicit --docs-dir,
      selects only REQUIREMENTS.md/WORKFLOW.md/REFERENCES.md as direct regular files in fixed order,
      and delegates summary rendering to run_files_tokens.
    """
    project_base = _resolve_project_base(args)
    config = load_config(project_base)
    docs_dir_value = config["docs-dir"]
    ensure_doc_directory(str(docs_dir_value), project_base)
    normalized_docs_dir = make_relative_if_contains_project(
        str(docs_dir_value), project_base
    )
    docs_dir = project_base / normalized_docs_dir
    canonical_names = ("REQUIREMENTS.md", "WORKFLOW.md", "REFERENCES.md")
    files = [
        str(candidate_path)
        for candidate_path in (docs_dir / name for name in canonical_names)
        if candidate_path.is_file()
    ]
    if not files:
        raise ReqError("Error: no canonical docs files found in --docs-dir.", 1)
    run_files_tokens(files)


def run_files_static_check_cmd(files: list[str], args: Namespace) -> int:
    """!
    @brief Execute `--files-static-check`: run static analysis on an explicit file list.
    @param files List of raw file paths supplied by the user.
    @param args Parsed CLI namespace; `--here`/`--base` are used to locate config.json.
    @return Exit code: 0 if all checked files pass (or none are checked), 1 if any fail.
    @details
      Project-base resolution order:
      1. `--base PATH` -> use PATH.
      2. `--here` -> use CWD.
      3. Fallback -> use CWD.
      If `.req/config.json` is not found at the resolved project base, emits a warning to
      stderr and returns 0 (SRS-254).
      For each file:
      - Resolves absolute path; skips with warning if not a regular file.
      - Detects language via `STATIC_CHECK_EXT_TO_LANG` keyed on the lowercase extension.
      - Looks up language in the `"static-check"` config section; skips silently if absent.
      - Executes each configured language entry sequentially via
        `dispatch_static_check_for_file(filepath, lang_config, fail_only=True, project_base=...)`.
      - For `Command` module entries, execution order is `<cmd> [params...] <filename>`.
      Dispatch context provides project root for checker runtime execution.
      All checks execute with `fail_only=True`: passing checks produce no stdout output (SRS-253).
      Overall exit code: max of all per-file codes (0=all pass, 1=any fail). (SRS-253, SRS-255)
    @see SRS-253, SRS-254, SRS-255, SRS-341
    """
    from .static_check import STATIC_CHECK_EXT_TO_LANG, dispatch_static_check_for_file

    # Resolve project base for config.json lookup
    base_arg = getattr(args, "base", None)
    here_arg = getattr(args, "here", False)
    if base_arg:
        project_base: Path = Path(base_arg).resolve()
    elif here_arg:
        project_base = Path.cwd().resolve()
    else:
        project_base = Path.cwd().resolve()

    sc_config = load_static_check_from_config(project_base)
    if not sc_config:
        config_path = project_base / ".req" / "config.json"
        if not config_path.is_file():
            print(
                "  Warning: .req/config.json not found; no static-check tools configured.",
                file=sys.stderr,
            )
            return 0

    overall = 0
    for raw_path in files:
        p = Path(raw_path)
        if not p.is_file():
            print(
                f"  Warning: skipping (not found or not a file): {raw_path}",
                file=sys.stderr,
            )
            continue
        filepath = str(p.resolve())
        ext = p.suffix.lower()
        lang = STATIC_CHECK_EXT_TO_LANG.get(ext)
        if not lang:
            vlog(f"Skipping {raw_path}: no language mapping for extension '{ext}'")
            continue
        lang_configs = sc_config.get(lang)
        if not lang_configs:
            vlog(f"Skipping {raw_path}: no static-check config for language '{lang}'")
            continue
        for lang_config in lang_configs:
            rc = dispatch_static_check_for_file(
                filepath,
                lang_config,
                fail_only=True,
                project_base=project_base,
            )
            if rc != 0:
                overall = 1
    return overall


def run_project_static_check_cmd(args: Namespace) -> int:
    """!
    @brief Execute `--static-check`: run static analysis on project source and test files.
    @param args Parsed CLI namespace; here-only project scan (`--here` implied; `--base` rejected).
    @return Exit code: 0 if all checked files pass (or none are checked), 1 if any fail.
    @details
      Collects files from configured `src-dir` directories and the `tests-dir` directory
      (SRS-256, SRS-336), applies `EXCLUDED_DIRS` filtering and `SUPPORTED_EXTENSIONS` matching.
      If `tests-dir` is missing or invalid in `.req/config.json`, test directory inclusion is
      skipped silently without error (SRS-336).
      Files under `<tests-dir>/fixtures/` are excluded from static-check selection because they
      are fixture corpus inputs for parser/static-check tests and can intentionally contain
      diagnostics unrelated to project code quality gates.
      For each collected file:
      - Detects language via `STATIC_CHECK_EXT_TO_LANG` keyed on lowercase extension.
      - Looks up language in the `"static-check"` section of `.req/config.json`.
      - Skips silently when no tool is configured for the file's language.
      - Executes each configured language entry sequentially via
        `dispatch_static_check_for_file(filepath, lang_config, fail_only=True, project_base=...)`.
      - For `Command` module entries, execution order is `<cmd> [params...] <filename>`.
      Dispatch context provides project root for checker runtime execution.
      All checks execute with `fail_only=True`: passing checks produce no stdout output (SRS-256).
      Overall exit code: max of all per-file codes (0=all pass, 1=any fail). (SRS-256, SRS-257)
    @throws ReqError If no source files are found.
    @see SRS-256, SRS-257, SRS-336, SRS-341
    """
    from .static_check import STATIC_CHECK_EXT_TO_LANG, dispatch_static_check_for_file

    project_base, src_dirs = _resolve_project_src_dirs(args)
    sc_config = load_static_check_from_config(project_base)
    selection_dirs = list(src_dirs)
    tests_dir_rel: Optional[str] = None

    # SRS-336: append tests-dir to file selection; skip silently if missing/invalid
    try:
        full_cfg = load_full_config(project_base)
        tests_dir_val = full_cfg.get("tests-dir") or full_cfg.get("test-dir")
        if isinstance(tests_dir_val, str) and tests_dir_val.strip():
            selection_dirs.append(tests_dir_val)
            tests_dir_rel = (
                Path(make_relative_if_contains_project(tests_dir_val, project_base))
                .as_posix()
                .strip("/")
            )
    except ReqError:
        pass

    files = _collect_source_files(selection_dirs, project_base)
    fixture_roots: list[str] = ["tests/fixtures"]
    if tests_dir_rel is not None:
        configured_root = (
            "fixtures" if tests_dir_rel in {"", "."} else f"{tests_dir_rel}/fixtures"
        )
        if configured_root not in fixture_roots:
            fixture_roots.append(configured_root)
    filtered_files: list[str] = []
    for filepath in files:
        try:
            rel_posix = (
                Path(filepath).resolve().relative_to(project_base.resolve()).as_posix()
            )
        except ValueError:
            filtered_files.append(filepath)
            continue
        should_skip = False
        for fixture_root in fixture_roots:
            fixture_prefix = f"{fixture_root}/"
            if rel_posix == fixture_root or rel_posix.startswith(fixture_prefix):
                should_skip = True
                break
        if should_skip:
            continue
        filtered_files.append(filepath)
    files = filtered_files
    if not files:
        raise ReqError("Error: no source files found in configured directories.", 1)

    overall = 0
    for filepath in files:
        ext = Path(filepath).suffix.lower()
        lang = STATIC_CHECK_EXT_TO_LANG.get(ext)
        if not lang:
            vlog(f"Skipping {filepath}: no language mapping for extension '{ext}'")
            continue
        lang_configs = sc_config.get(lang)
        if not lang_configs:
            vlog(f"Skipping {filepath}: no static-check config for language '{lang}'")
            continue
        for lang_config in lang_configs:
            rc = dispatch_static_check_for_file(
                filepath,
                lang_config,
                fail_only=True,
                project_base=project_base,
            )
            if rc != 0:
                overall = 1
    return overall


def _resolve_project_base(args: Namespace) -> Path:
    """!
    @brief Resolve project base path for project-level commands.
        @param args Parsed CLI arguments namespace.
        @return Absolute path of project base.
        @throws ReqError If --base/--here is missing or the resolved path does not exist.
    @details Implements the _resolve_project_base function behavior with deterministic control flow.
    """
    if not getattr(args, "base", None) and not getattr(args, "here", False):
        raise ReqError("Error: --base or --here is required for this command.", 1)

    if args.base:
        project_base = args.base.resolve()
    else:
        project_base = Path.cwd().resolve()

    if not project_base.exists():
        raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)
    return project_base


def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]:
    """!
    @brief Resolve project base and src-dirs for project source commands.
    @details Implements the _resolve_project_src_dirs function behavior with deterministic control flow.
    @param args Input parameter `args`.
    @return {tuple[Path, list[str]]} Function return value.
    """
    project_base = _resolve_project_base(args)

    src_dirs: list[str]
    if getattr(args, "here", False):
        config = load_config(project_base)
        raw_src_dirs = config.get("src-dir", [])
        if not isinstance(raw_src_dirs, list) or not all(
            isinstance(item, str) for item in raw_src_dirs
        ):
            raise ReqError(
                "Error: missing or invalid 'src-dir' field in .req/config.json", 11
            )
        src_dirs = raw_src_dirs
    else:
        # Source dirs can come from args or from config
        src_dirs_arg = getattr(args, "src_dir", None)
        if src_dirs_arg:
            if not isinstance(src_dirs_arg, list) or not all(
                isinstance(item, str) for item in src_dirs_arg
            ):
                raise ReqError("Error: invalid --src-dir value.", 1)
            src_dirs = src_dirs_arg
        else:
            config_path = project_base / ".req" / "config.json"
            if config_path.is_file():
                config = load_config(project_base)
                raw_src_dirs = config.get("src-dir", [])
                if not isinstance(raw_src_dirs, list) or not all(
                    isinstance(item, str) for item in raw_src_dirs
                ):
                    raise ReqError(
                        "Error: missing or invalid 'src-dir' field in .req/config.json",
                        11,
                    )
                src_dirs = raw_src_dirs
            else:
                raise ReqError(
                    "Error: --src-dir is required or .req/config.json must exist.", 1
                )

    if not src_dirs:
        raise ReqError("Error: no source directories configured.", 1)

    return project_base, src_dirs


def main(argv: Optional[list[str]] = None) -> int:
    """!
    @brief CLI entry point for console_scripts and `-m` execution.
        @details Returns an exit code (0 success, non-zero on error).
    @param argv Input parameter `argv`.
    @return {int} Function return value.
    """
    try:
        global VERBOSE, DEBUG
        argv_list = sys.argv[1:] if argv is None else argv
        force_online_release_check = "--ver" in argv_list or "--version" in argv_list
        # Run release-check at startup before argument parsing/validation.
        global FORCE_ONLINE_RELEASE_CHECK
        previous_force_online_release_check = FORCE_ONLINE_RELEASE_CHECK
        FORCE_ONLINE_RELEASE_CHECK = force_online_release_check
        try:
            maybe_notify_newer_version(timeout_seconds=RELEASE_CHECK_TIMEOUT_SECONDS)
        finally:
            FORCE_ONLINE_RELEASE_CHECK = previous_force_online_release_check
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
        if _is_here_only_project_scan_command(args):
            if getattr(args, "base", None):
                raise ReqError(
                    "Error: --references, --compress, --tokens, --find, --static-check, "
                    "--git-check, --docs-check, --git-wt-name, --git-wt-create, and "
                    "--git-wt-delete, --git-path, and --get-base-path do not allow --base; use --here.",
                    1,
                )
            args.here = True
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
            elif getattr(args, "test_static_check", None) is not None:
                from .static_check import run_static_check

                rc = run_static_check(args.test_static_check)
                return rc
            elif getattr(args, "files_static_check", None):
                rc = run_files_static_check_cmd(args.files_static_check, args)
                return rc
            return 0
        # Project scan commands
        if _is_project_scan_command(args):
            if getattr(args, "references", False):
                run_references(args)
            elif getattr(args, "compress", False):
                run_compress_cmd(args)
            elif getattr(args, "tokens", False):
                run_tokens(args)
            elif getattr(args, "find", None):
                run_find(args)
            elif getattr(args, "static_check", False):
                rc = run_project_static_check_cmd(args)
                return rc
            elif getattr(args, "git_check", False):
                run_git_check(args)
            elif getattr(args, "docs_check", False):
                run_docs_check(args)
            elif getattr(args, "git_wt_name", False):
                run_git_wt_name(args)
            elif getattr(args, "git_wt_create", None):
                run_git_wt_create(args)
            elif getattr(args, "git_wt_delete", None):
                run_git_wt_delete(args)
            elif getattr(args, "git_path_cmd", False):
                run_git_path(args)
            elif getattr(args, "get_base_path_cmd", False):
                run_get_base_path(args)
            return 0
        # Standard init flow requires --base or --here
        if not getattr(args, "base", None) and not getattr(args, "here", False):
            raise ReqError("Error: --base or --here is required for initialization.", 1)
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


if __name__ == "__main__":
    raise SystemExit(main())
