# Files Structure
```
.
├── scripts
│   ├── pyright.sh
│   ├── req.sh
│   ├── ruff.sh
│   └── test-install.sh
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

# pyright.sh | Shell | 52L | 7 symbols | 2 imports | 14 comments
> Path: `scripts/pyright.sh`

## Imports
```
source "${VENVDIR}/bin/activate"
source "${VENVDIR}/bin/activate"
```

## Definitions

- var `FULL_PATH=$(readlink -f "$0")` (L9)
- var `SCRIPT_PATH=$(dirname "$FULL_PATH")` (L12)
- var `SCRIPT_NAME=$(basename "$FULL_PATH")` (L15)
- var `BASE_DIR=$(dirname "$SCRIPT_PATH")` (L18)
- var `VENVDIR="${BASE_DIR}/.venv"` (L27)
- var `REQUIREMENTS_FILE="${BASE_DIR}/requirements.txt"` (L28)
- var `PYTHONPATH="${BASE_DIR}/src:${PYTHONPATH}" \` (L51)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`FULL_PATH`|var||9||
|`SCRIPT_PATH`|var||12||
|`SCRIPT_NAME`|var||15||
|`BASE_DIR`|var||18||
|`VENVDIR`|var||27||
|`REQUIREMENTS_FILE`|var||28||
|`PYTHONPATH`|var||51||


---

# req.sh | Shell | 52L | 7 symbols | 2 imports | 14 comments
> Path: `scripts/req.sh`

## Imports
```
source "${VENVDIR}/bin/activate"
source "${VENVDIR}/bin/activate"
```

## Definitions

- var `FULL_PATH=$(readlink -f "$0")` (L9)
- var `SCRIPT_PATH=$(dirname "$FULL_PATH")` (L12)
- var `SCRIPT_NAME=$(basename "$FULL_PATH")` (L15)
- var `BASE_DIR=$(dirname "$SCRIPT_PATH")` (L18)
- var `VENVDIR="${BASE_DIR}/.venv"` (L27)
- var `REQUIREMENTS_FILE="${BASE_DIR}/requirements.txt"` (L28)
- var `PYTHONPATH="${BASE_DIR}/src:${PYTHONPATH}" \` (L51)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`FULL_PATH`|var||9||
|`SCRIPT_PATH`|var||12||
|`SCRIPT_NAME`|var||15||
|`BASE_DIR`|var||18||
|`VENVDIR`|var||27||
|`REQUIREMENTS_FILE`|var||28||
|`PYTHONPATH`|var||51||


---

# ruff.sh | Shell | 52L | 7 symbols | 2 imports | 14 comments
> Path: `scripts/ruff.sh`

## Imports
```
source "${VENVDIR}/bin/activate"
source "${VENVDIR}/bin/activate"
```

## Definitions

- var `FULL_PATH=$(readlink -f "$0")` (L9)
- var `SCRIPT_PATH=$(dirname "$FULL_PATH")` (L12)
- var `SCRIPT_NAME=$(basename "$FULL_PATH")` (L15)
- var `BASE_DIR=$(dirname "$SCRIPT_PATH")` (L18)
- var `VENVDIR="${BASE_DIR}/.venv"` (L27)
- var `REQUIREMENTS_FILE="${BASE_DIR}/requirements.txt"` (L28)
- var `PYTHONPATH="${BASE_DIR}/src:${PYTHONPATH}" \` (L51)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`FULL_PATH`|var||9||
|`SCRIPT_PATH`|var||12||
|`SCRIPT_NAME`|var||15||
|`BASE_DIR`|var||18||
|`VENVDIR`|var||27||
|`REQUIREMENTS_FILE`|var||28||
|`PYTHONPATH`|var||51||


---

# test-install.sh | Shell | 111L | 6 symbols | 0 imports | 17 comments
> Path: `scripts/test-install.sh`

## Definitions

- var `FULL_PATH=$(readlink -f "$0")` (L9)
- var `SCRIPT_PATH=$(dirname "$FULL_PATH")` (L12)
- var `SCRIPT_NAME=$(basename "$FULL_PATH")` (L15)
- var `BASE_DIR=$(dirname "$SCRIPT_PATH")` (L18)
- var `FOLDER_PATH="${1:-}"` (L26)
- var `FOLDER_PATH="$BASE_DIR/temp/test-install"` (L29)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`FULL_PATH`|var||9||
|`SCRIPT_PATH`|var||12||
|`SCRIPT_NAME`|var||15||
|`BASE_DIR`|var||18||
|`FOLDER_PATH`|var||26||
|`FOLDER_PATH`|var||29||


---

# __init__.py | Python | 26L | 0 symbols | 8 imports | 3 comments
> Path: `src/usereq/__init__.py`
- @brief Initialization module for the `usereq` package.
- @details Exposes the package version, main entry point, and key submodules. Designed to be lightweight.
@author GitHub Copilot
@version 0.0.70

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
- @brief Package entry point for execution as a module.
- @details Enables running the package via `python -m usereq`. Delegates execution to the CLI main function.
@author GitHub Copilot
@version 0.0.70

## Imports
```
from .cli import main
import sys
```


---

# cli.py | Python | 4969L | 151 symbols | 32 imports | 240 comments
> Path: `src/usereq/cli.py`
- @brief CLI entry point implementing the useReq initialization flow.
- @details Handles argument parsing, configuration management, and execution of useReq commands.
@author GitHub Copilot
@version 0.0.70

## Imports
```
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import os
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

- var `REPO_ROOT = Path(__file__).resolve().parents[2]` (L29)
- var `RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"` (L32)
- @brief The absolute path to the repository root."""
- var `VERBOSE = False` (L35)
- @brief The absolute path to the resources directory."""
- var `DEBUG = False` (L38)
- @brief Whether verbose output is enabled."""
- var `REQUIREMENTS_TEMPLATE_NAME = "Requirements_Template.md"` (L41)
- @brief Whether debug output is enabled."""
- var `PERSISTED_UPDATE_FLAG_KEYS = ("preserve-models",)` (L44)
- @brief Name of the packaged requirements template file."""
- var `VALID_PROVIDERS = frozenset({"codex", "claude", "gemini", "github", "kiro", "opencode"})` (L47)
- @brief Config keys persisted for install/update boolean flags (SRS-288)."""
- var `VALID_ARTIFACTS = frozenset({"prompts", "agents", "skills"})` (L50)
- @brief Valid provider names accepted by ``--provider`` specs (SRS-275)."""
- var `VALID_PROVIDER_OPTIONS = frozenset(` (L53)
- @brief Valid artifact type tokens accepted in ``--provider`` specs (SRS-275)."""
- var `INVALID_WT_NAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f\s]')` (L68)
- @brief Provider-to-directory mapping for worktree copy operations (SRS-325)."""
### fn `def parse_provider_spec(spec: str) -> tuple[str, set[str], set[str]]` (L72-123)
- @brief Regex matching characters invalid in both Linux and Windows directory names."""
- @brief Parse a single ``--provider`` SPEC string into its components.
- @details Splits on ``:``, validates each component against the known sets, and returns normalized lower-case values. Commas separate multiple artifacts and options within their respective fields.
- @param spec The raw SPEC string in format ``PROVIDER:ARTIFACTS[:OPTIONS]``.
- @return Tuple of (provider_name, artifacts_set, options_set).
- @throws ReqError If the SPEC contains unknown provider, artifact, or option tokens (SRS-278).
- @see SRS-275, SRS-276, SRS-278

### fn `def resolve_provider_configs(` (L124-125)

- var `ANSI_BRIGHT_RED = "\033[91m"` (L176)
- @brief Resolve per-provider configurations from ``--provider`` specs only.
- @details ``--provider`` specs are the sole mechanism for provider/artifact/option
configuration (SRS-275, SRS-276). All providers start disabled with all options
inactive; each spec enables its provider and activates listed artifacts and options.
- @param provider_specs List of raw ``--provider`` SPEC strings.
- @return Dict mapping each of the 6 provider names to a config dict with keys:
``enabled`` (bool), ``prompts`` (bool), ``agents`` (bool), ``skills`` (bool),
``enable-models`` (bool), ``enable-tools`` (bool), ``prompts-use-agents`` (bool),
``legacy`` (bool).
- @see SRS-275, SRS-276
- var `ANSI_BRIGHT_GREEN = "\033[92m"` (L179)
- @brief ANSI escape prefix for bright red terminal output."""
- var `ANSI_RESET = "\033[0m"` (L182)
- @brief ANSI escape prefix for bright green terminal output."""
- var `RELEASE_CHECK_TIMEOUT_SECONDS = 2.0` (L185)
- @brief ANSI escape sequence that resets terminal style."""
- var `RELEASE_CHECK_IDLE_DELAY_SECONDS = 300` (L188)
- @brief Hardcoded default timeout for startup release-check HTTP calls."""
- var `TOOL_PROGRAM_NAME = "usereq"` (L191)
- @brief Hardcoded startup release-check idle-delay in seconds."""
- var `RELEASE_CHECK_PROGRAM_NAME = TOOL_PROGRAM_NAME` (L194)
- @brief Hardcoded configurable tool identifier used by uv install/uninstall commands."""
- var `GITHUB_REPOSITORY_OWNER = "Ogekuri"` (L197)
- @brief Program identifier used in release-check idle-state filename."""
- var `GITHUB_REPOSITORY_NAME = "useReq"` (L200)
- @brief Hardcoded GitHub owner used by upgrade and release-check endpoints."""
- var `RELEASE_CHECK_IDLE_FILENAME_TEMPLATE = ".github_api_idle-time.{program_name}"` (L203)
- @brief Hardcoded GitHub repository used by upgrade and release-check endpoints."""
- var `GITHUB_RELEASES_LATEST_URL = (` (L206)
- @brief Filename template for release-check idle-state JSON in `$HOME`."""
- var `GITHUB_UPGRADE_SOURCE = (` (L212)
- @brief Hardcoded GitHub API endpoint for latest-release resolution."""
### class `class ReqError(Exception)` : Exception (L218-235)
- @brief Hardcoded git source used by uv self-upgrade command."""
- @brief Dedicated exception for expected CLI errors.
- @details This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L223-235)
  - @brief Dedicated exception for expected CLI errors.
  - @brief Initialize an expected CLI failure payload.
  - @details This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.
  - @details Implements the __init__ function behavior with deterministic control flow.
  - @param message Human-readable error message.
  - @param code Process exit code bound to the failure category.
  - @return {None} Function return value.

### fn `def log(msg: str) -> None` (L236-245)
- @brief Prints an informational message.
- @details Implements the log function behavior with deterministic control flow.
- @param msg The message string to print.
- @return {None} Function return value.

### fn `def dlog(msg: str) -> None` (L246-256)
- @brief Prints a debug message if debugging is active.
- @details Implements the dlog function behavior with deterministic control flow.
- @param msg The debug message string to print.
- @return {None} Function return value.

### fn `def vlog(msg: str) -> None` (L257-267)
- @brief Prints a verbose message if verbose mode is active.
- @details Implements the vlog function behavior with deterministic control flow.
- @param msg The verbose message string to print.
- @return {None} Function return value.

### fn `def _get_available_tags_help() -> str` `priv` (L268-280)
- @brief Generate available TAGs help text for argument parser.
- @details Imports format_available_tags from find_constructs module to generate dynamic TAG listing for CLI help display.
- @return Formatted multi-line string listing TAGs by language.

### fn `def build_parser() -> argparse.ArgumentParser` (L281-480)
- @brief Builds the CLI argument parser.
- @details Defines all supported CLI arguments, flags, and help texts. Provider enablement, artifact selection, and per-provider options are configured exclusively via the repeatable ``--provider SPEC`` argument (SRS-275, SRS-034).
- @return Configured ArgumentParser instance.

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L544-553)
- @brief Parses command-line arguments into a namespace.
- @details Implements the parse_args function behavior with deterministic control flow.
- @param argv List of arguments (defaults to sys.argv).
- @return Namespace containing parsed arguments.

### fn `def load_package_version() -> str` (L554-568)
- @brief Reads the package version from __init__.py.
- @details Implements the load_package_version function behavior with deterministic control flow.
- @return Version string extracted from the package.
- @throws ReqError If version cannot be determined.

### fn `def maybe_print_version(argv: list[str]) -> bool` (L569-581)
- @brief Handles --ver/--version by printing the version.
- @details Implements the maybe_print_version function behavior with deterministic control flow.
- @param argv Command line arguments to check.
- @return True if version was printed, False otherwise.

### fn `def run_upgrade() -> None` (L582-608)
- @brief Executes the upgrade using uv.
- @details Implements the run_upgrade function behavior with deterministic control flow.
- @return {None} Function return value.
- @throws ReqError If upgrade fails.

### fn `def run_uninstall() -> None` (L609-632)
- @brief Executes the uninstallation using uv.
- @details Implements the run_uninstall function behavior with deterministic control flow.
- @return {None} Function return value.
- @throws ReqError If uninstall fails.

### fn `def normalize_release_tag(tag: str) -> str` (L633-645)
- @brief Normalizes the release tag by removing a 'v' prefix if present.
- @details Implements the normalize_release_tag function behavior with deterministic control flow.
- @param tag The raw tag string.
- @return The normalized version string.

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L646-670)
- @brief Converts a version into a numeric tuple for comparison.
- @details Accepts versions in 'X.Y.Z' format (ignoring any non-numeric suffixes).
- @param version The version string to parse.
- @return Tuple of integers or None if parsing fails.

### fn `def is_newer_version(current: str, latest: str) -> bool` (L671-689)
- @brief Returns True if latest is greater than current.
- @details Implements the is_newer_version function behavior with deterministic control flow.
- @param current The current installed version string.
- @param latest The latest available version string.
- @return True if update is available, False otherwise.

### fn `def parse_github_owner_repository(remote_url: str) -> tuple[str, str] | None` (L690-716)
- @brief Extract GitHub owner/repository from a git remote URL.
- @details Supports SSH (`git@github.com:owner/repo.git`), HTTPS (`https://github.com/owner/repo.git`), and SSH-scheme (`ssh://git@github.com/owner/repo.git`) forms. Removes optional `.git` suffix.
- @param remote_url Remote URL string from `git remote -v`.
- @return Tuple `(owner, repository)` when URL targets github.com; otherwise None.

### fn `def read_git_remote_verbose(cwd: str | None = None) -> str` (L717-736)
- @brief Read git remote definitions using `git remote -v`.
- @details Executes `git remote -v` with deterministic stderr capture and text decoding. When `cwd` is omitted, the current process working directory is used.
- @param cwd Optional working directory override for git execution context.
- @return Raw stdout output generated by `git remote -v`.
- @throws subprocess.CalledProcessError If git returns a non-zero status.

### fn `def resolve_github_owner_repository_from_active_remotes() -> tuple[str, str]` (L737-797)
- @brief Resolve GitHub owner/repository from active repository remotes.
- @details Reads `git remote -v`, prioritizes `origin` fetch URL, then other fetch remotes, then non-fetch entries, and returns the first parseable github.com owner/repository pair. If the first inspection fails outside the repository root context, retries once from `REPO_ROOT`.
- @return Tuple `(owner, repository)` resolved from active remotes.
- @throws ValueError If no github.com remote URL can be parsed from `git remote -v`.
- @throws ReqError If git remote inspection cannot execute successfully.

### fn `def resolve_latest_release_api_url() -> str` (L798-806)
- @brief Resolve latest-release GitHub API URL from hardcoded repository settings.
- @details Returns the static endpoint derived from `GITHUB_REPOSITORY_OWNER` and `GITHUB_REPOSITORY_NAME`.
- @return Fully-qualified URL `https://api.github.com/repos/Ogekuri/useReq/releases/latest`.

### fn `def format_unix_timestamp_utc(timestamp_seconds: int) -> str` (L807-819)
- @brief Convert a Unix timestamp into a UTC human-readable string.
- @details Implements deterministic UTC conversion for release-check idle-state persistence.
- @param timestamp_seconds Unix timestamp in seconds.
- @return UTC datetime string in ISO-like `YYYY-MM-DDTHH:MM:SSZ` format.

### fn `def get_release_check_idle_file_path(` (L820-821)

### fn `def read_release_check_idle_state(file_path: Path) -> dict[str, int | str] | None` (L833-897)
- @brief Resolve idle-state file path for startup release-check throttling.
- @brief Read and validate release-check idle-state JSON.
- @details Builds the path using the effective home directory returned by `Path.home()`.
- @details Validates required keys `last_success_timestamp`, `last_success_human_readable_timestamp`, `idle_until_timestamp`, and `idle_until_human_readable_timestamp`; timestamps are normalized to integers.
- @param program_name Program identifier appended to the filename suffix.
- @param file_path Absolute idle-state JSON path under `$HOME`.
- @return Absolute path `$HOME/.github_api_idle-time.<program_name>`.
- @return Normalized idle-state dictionary or None when file does not exist.
- @throws OSError If file read fails.
- @throws json.JSONDecodeError If file content is not valid JSON.
- @throws ValueError If required keys are missing or value types are invalid.

### fn `def should_execute_release_check(` (L898-900)

### fn `def parse_retry_after_seconds(` (L918-920)
- @brief Decide whether startup release-check should execute in current invocation.
- @details Executes release-check when state is missing and skips only while the persisted `idle_until_timestamp` is greater than the current timestamp.
- @param idle_state Parsed idle-state payload or None when unavailable.
- @param now_timestamp Current Unix timestamp in seconds.
- @return True when release-check must execute; False when still in idle window.

### fn `def write_release_check_idle_state_payload(` (L950-953)
- @brief Parse an HTTP `Retry-After` header value into non-negative seconds.
- @details Supports integer-second values and HTTP-date values; HTTP-date values are converted to a delta from `now_timestamp`.
- @param retry_after_header Raw `Retry-After` header value.
- @param now_timestamp Current Unix timestamp in seconds.
- @return Retry delay in seconds when parsing succeeds; otherwise None.

### fn `def write_release_check_idle_state(` (L979-982)
- @brief Persist canonical release-check idle-state payload to disk.
- @details Serializes both numeric and UTC human-readable timestamps for the success instant and the idle-until instant.
- @param file_path Absolute idle-state JSON path.
- @param last_success_timestamp Unix timestamp of the last successful release-check.
- @param idle_until_timestamp Unix timestamp until startup release-check remains disabled.
- @throws OSError If file write fails.

### fn `def write_rate_limited_release_check_idle_state(` (L1000-1005)
- @brief Persist release-check idle-state after a successful remote check.
- @details Computes `idle_until_timestamp = now_timestamp + idle_delay_seconds` and persists canonical idle-state keys.
- @param file_path Absolute idle-state JSON path.
- @param now_timestamp Successful check timestamp in seconds.
- @param idle_delay_seconds Fixed idle-delay length in seconds.
- @throws OSError If file write fails.

### fn `def maybe_notify_newer_version(` (L1039-1040)
- @brief Persist idle-state when GitHub responds with HTTP 429 rate limiting.
- @details Computes `candidate_idle_until = now + max(idle_delay_seconds, retry_after_seconds)` and preserves the maximum against any existing `idle_until_timestamp` to avoid shortening prior 429 backoff windows.
- @param file_path Absolute idle-state JSON path.
- @param now_timestamp Current Unix timestamp in seconds.
- @param retry_after_seconds Parsed `Retry-After` delay in seconds.
- @param idle_state Existing parsed idle-state payload or None.
- @param idle_delay_seconds Fixed idle-delay length in seconds.
- @throws OSError If file write fails.

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L1171-1193)
- @brief Executes idle-gated online version check and prints bright colored status messages.
- @brief Ensures the documentation directory exists under the project base.
- @details Reads idle-state from `$HOME/.github_api_idle-time.usereq`, skips remote requests when idle window is active, resolves latest-release URL from hardcoded repository settings when due, compares versions, prints bright-green update message, prints bright-red diagnostics on failure, writes idle-state after successful HTTP/JSON validation, and updates idle-state on HTTP 429 using `Retry-After`.
- @details Implements the ensure_doc_directory function behavior with deterministic control flow.
- @param timeout_seconds Time to wait for the version check response.
- @param path The relative path to the documentation directory.
- @param project_base The project root path.
- @return {None} Function return value.
- @return {None} Function return value.
- @throws ReqError If path is invalid, absolute, or not a directory.

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L1194-1216)
- @brief Ensures the test directory exists under the project base.
- @details Implements the ensure_test_directory function behavior with deterministic control flow.
- @param path The relative path to the test directory.
- @param project_base The project root path.
- @return {None} Function return value.
- @throws ReqError If path is invalid, absolute, or not a directory.

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L1217-1239)
- @brief Ensures the source directory exists under the project base.
- @details Implements the ensure_src_directory function behavior with deterministic control flow.
- @param path The relative path to the source directory.
- @param project_base The project root path.
- @return {None} Function return value.
- @throws ReqError If path is invalid, absolute, or not a directory.

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L1240-1281)
- @brief Normalizes the path relative to the project root when possible.
- @details Handles cases where the path includes the project directory name redundantly.
- @param path_value The input path string.
- @param project_base The base path of the project.
- @return The normalized relative path string.

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L1282-1297)
- @brief Resolves the absolute path starting from a normalized value.
- @details Implements the resolve_absolute function behavior with deterministic control flow.
- @param normalized The normalized relative path string.
- @param project_base The project root path.
- @return Absolute Path object or None if normalized is empty.

### fn `def format_substituted_path(value: str) -> str` (L1298-1309)
- @brief Uniforms path separators for substitutions.
- @details Implements the format_substituted_path function behavior with deterministic control flow.
- @param value The path string to format.
- @return Path string with forward slashes.

### fn `def compute_sub_path(` (L1310-1311)

### fn `def resolve_git_root(target_path: Path) -> Path` (L1332-1359)
- @brief Calculates the relative path to use in tokens.
- @brief Resolve the git repository root for a given path.
- @details Implements the compute_sub_path function behavior with deterministic control flow.
- @param normalized The normalized relative path.
- @param absolute The absolute path object (can be None).
- @param project_base The project root path.
- @param target_path Absolute path that must be inside a git repository.
- @return Relative path string formatted with forward slashes.
- @return Absolute path to the git repository root.
- @throws ReqError If the path is not inside a git repository.
- @satisfies SRS-305, SRS-306

### fn `def is_inside_git_repo(target_path: Path) -> bool` (L1360-1379)
- @brief Check whether a given path is inside a git work tree.
- @param target_path Absolute path to check.
- @return True if inside a git work tree, False otherwise.
- @satisfies SRS-305

### fn `def sanitize_branch_name(branch: str) -> str` (L1380-1389)
- @brief Replace characters incompatible with Linux or Windows paths in a branch name.
- @param branch Raw git branch name.
- @return Sanitized string with incompatible characters replaced by `-`.
- @satisfies SRS-319

### fn `def validate_wt_name(wt_name: str) -> bool` (L1390-1401)
- @brief Validate that a worktree/branch name contains only valid directory characters.
- @param wt_name Candidate worktree name.
- @return True if valid, False if invalid characters are present.
- @satisfies SRS-321

### fn `def load_full_config(project_base: Path) -> dict` (L1402-1421)
- @brief Load ALL parameters from `.req/config.json` as a raw dictionary.
- @param project_base The project root path.
- @return Full dictionary of all config.json key-value pairs.
- @throws ReqError If config file is missing or invalid JSON.
- @satisfies SRS-310

### fn `def save_config(` (L1422-1432)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L1476-1526)
- @brief Saves normalized parameters to .req/config.json.
- @brief Loads parameters saved in .req/config.json.
- @details Writes full config payload to `.req/config.json`. Includes `"base-path"` and
`"git-path"` when provided (SRS-302, SRS-306).
- @details Implements the load_config function behavior with deterministic control flow.
- @param project_base The project root path.
- @param guidelines_dir_value Relative path to guidelines directory.
- @param doc_dir_value Relative path to docs directory.
- @param test_dir_value Relative path to tests directory.
- @param src_dir_values List of relative paths to source directories.
- @param static_check_config Optional dict of static-check config to persist under key
`"static-check"`; omitted from JSON when None or empty.
- @param persisted_flags Optional dict with persisted boolean flags used by `--update`.
- @param provider_specs Optional list of raw ``--provider`` SPEC strings to persist
under the `"providers"` key (SRS-279).
- @param base_path_abs Optional absolute path string for `"base-path"` (SRS-302).
- @param git_path_abs Optional absolute path string for `"git-path"` (SRS-306).
- @param project_base The project root path.
- @return {None} Function return value.
- @return Dictionary containing configuration values.
- @throws ReqError If config file is missing or invalid.
- @satisfies SRS-302, SRS-306

### fn `def load_static_check_from_config(project_base: Path) -> dict` (L1527-1558)
- @brief Load the `"static-check"` section from `.req/config.json` without validation errors.
- @details Reads config.json silently; returns `{}` on any read or parse error. Does NOT raise `ReqError`; caller decides whether absence is an error.
- @param project_base The project root path.
- @return Dict of static-check config (canonical-lang -> list[config-dict]); empty dict if absent or if config.json is missing/invalid.
- @see SRS-252, SRS-253, SRS-256

### fn `def _static_check_entry_identity(` `priv` (L1559-1560)

### fn `def build_persisted_update_flags(args: Namespace) -> dict[str, bool]` (L1583-1596)
- @brief Build the canonical identity tuple for one static-check entry.
- @brief Build persistent update flags from parsed CLI arguments.
- @details Identity is defined strictly by language, module, cmd, and params.
Unknown/additional keys in ``entry`` are ignored; ``params`` is normalized
to a tuple preserving order, and non-list params are treated as empty.
- @details Only ``preserve-models`` is persisted as a boolean flag (SRS-288). Provider/artifact/option configuration is persisted via ``--provider`` specs under the ``providers`` key in ``config.json`` (SRS-279).
- @param canonical_lang Canonical language key that owns the entry.
- @param entry Static-check entry mapping loaded from config or parsed from CLI.
- @param args Parsed CLI namespace.
- @return Tuple ``(canonical_lang, module, cmd, params_tuple)``.
- @return Mapping of config key -> boolean value for install/update persistence.
- @satisfies SRS-301

### fn `def load_persisted_update_flags(project_base: Path) -> dict[str, bool]` (L1597-1638)
- @brief Load persisted install/update boolean flags from `.req/config.json`.
- @details Only ``preserve-models`` is loaded as a boolean flag (SRS-288). Provider/artifact activation is validated via the persisted ``providers`` array (SRS-280).
- @param project_base The project root path.
- @return Mapping of persisted config key -> boolean value.
- @throws ReqError If config file is missing, invalid, or required flag fields are missing/invalid.

### fn `def load_persisted_provider_specs(project_base: Path) -> list[str]` (L1639-1660)
- @brief Load persisted ``--provider`` SPEC strings from `.req/config.json`.
- @details Reads the ``"providers"`` key from config.json (SRS-280). Returns ``[]`` on any read or parse error rather than raising.
- @param project_base The project root path.
- @return List of raw SPEC strings; empty list if key is missing or config is unreadable.
- @see SRS-279, SRS-280

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L1661-1693)
- @brief Generates the markdown file list for %%GUIDELINES_FILES%% replacement.
- @details Implements the generate_guidelines_file_list function behavior with deterministic control flow.
- @param guidelines_dir Input parameter `guidelines_dir`.
- @param project_base Input parameter `project_base`.
- @return {str} Function return value.

### fn `def generate_guidelines_file_items(` (L1694-1695)

### fn `def upgrade_guidelines_templates(guidelines_dest: Path, overwrite: bool = False) -> int` (L1729-1763)
- @brief Generates a list of relative file paths (no formatting) for printing.
- @brief Copies guidelines templates from resources/guidelines/ to the target directory.
- @details Each entry is formatted as `guidelines/file.md` (forward slashes). If there are no files, returns the directory itself with a trailing slash.
- @details Args: guidelines_dest: Target directory where templates will be copied overwrite: If True, overwrite existing files; if False, skip existing files Returns: Number of non-hidden files copied; returns 0 when the source directory is empty.
- @param guidelines_dir Input parameter `guidelines_dir`.
- @param project_base Input parameter `project_base`.
- @param guidelines_dest Input parameter `guidelines_dest`.
- @param overwrite Input parameter `overwrite`.
- @return {list[str]} Function return value.
- @return {int} Function return value.

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L1764-1780)
- @brief Normalizes the path token optionally preserving the trailing slash.
- @details Implements the make_relative_token function behavior with deterministic control flow.
- @param raw Input parameter `raw`.
- @param keep_trailing Input parameter `keep_trailing`.
- @return {str} Function return value.

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L1781-1796)
- @brief Validates that the path is not absolute and raises an error otherwise.
- @details Implements the ensure_relative function behavior with deterministic control flow.
- @param value Input parameter `value`.
- @param name Input parameter `name`.
- @param code Input parameter `code`.
- @return {None} Function return value.

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L1797-1809)
- @brief Returns text with token replacements applied.
- @details Implements the apply_replacements function behavior with deterministic control flow.
- @param text Input parameter `text`.
- @param replacements Input parameter `replacements`.
- @return {str} Function return value.

### fn `def write_text_file(dst: Path, text: str) -> None` (L1810-1821)
- @brief Writes text to disk, ensuring the destination folder exists.
- @details Implements the write_text_file function behavior with deterministic control flow.
- @param dst Input parameter `dst`.
- @param text Input parameter `text`.
- @return {None} Function return value.

### fn `def copy_with_replacements(` (L1822-1823)

### fn `def normalize_description(value: str) -> str` (L1838-1852)
- @brief Copies a file substituting the indicated tokens with their values.
- @brief Normalizes a description by removing superfluous quotes and escapes.
- @details Implements the copy_with_replacements function behavior with deterministic control flow.
- @details Implements the normalize_description function behavior with deterministic control flow.
- @param src Input parameter `src`.
- @param dst Input parameter `dst`.
- @param replacements Input parameter `replacements`.
- @param value Input parameter `value`.
- @return {None} Function return value.
- @return {str} Function return value.

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L1853-1887)
- @brief Converts a Markdown prompt to TOML for Gemini.
- @details Implements the md_to_toml function behavior with deterministic control flow.
- @param md_path Input parameter `md_path`.
- @param toml_path Input parameter `toml_path`.
- @param force Input parameter `force`.
- @return {None} Function return value.

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L1888-1901)
- @brief Extracts front matter and body from Markdown.
- @details Implements the extract_frontmatter function behavior with deterministic control flow.
- @param content Input parameter `content`.
- @return {tuple[str, str]} Function return value.

### fn `def extract_description(frontmatter: str) -> str` (L1902-1914)
- @brief Extracts the description from front matter.
- @details Implements the extract_description function behavior with deterministic control flow.
- @param frontmatter Input parameter `frontmatter`.
- @return {str} Function return value.

### fn `def extract_argument_hint(frontmatter: str) -> str` (L1915-1927)
- @brief Extracts the argument-hint from front matter, if present.
- @details Implements the extract_argument_hint function behavior with deterministic control flow.
- @param frontmatter Input parameter `frontmatter`.
- @return {str} Function return value.

### fn `def extract_purpose_first_bullet(body: str) -> str` (L1928-1952)
- @brief Returns the first bullet of the Purpose section.
- @details Implements the extract_purpose_first_bullet function behavior with deterministic control flow.
- @param body Input parameter `body`.
- @return {str} Function return value.

### fn `def _extract_section_text(body: str, section_name: str) -> str` `priv` (L1953-1980)
- @brief Extracts and collapses the text content of a named ## section.
- @details Scans `body` line by line for a heading matching `## <section_name>` (case-insensitive). Collects all subsequent non-empty lines until the next `##`-level heading (or end of string). Strips each line, joins with a single space, and returns the collapsed single-line result.
- @param[in] body str -- Full prompt body text (after front matter removal).
- @param[in] section_name str -- Target section name without `##` prefix (case-insensitive match).
- @return str -- Single-line collapsed text of the section; empty string if section absent or empty.

### fn `def extract_skill_description(frontmatter: str) -> str` (L1981-1999)
- @brief Extracts the usage field from YAML front matter as a single YAML-safe line.
- @details Parses the YAML front matter and returns the `usage` field value with all whitespace normalized to a single line. Returns an empty string if the field is absent.
- @param[in] frontmatter str -- YAML front matter text (without the leading/trailing `---` delimiters).
- @return str -- Single-line text of the usage field; empty string if absent.

### fn `def json_escape(value: str) -> str` (L2000-2009)
- @brief Escapes a string for JSON without external delimiters.
- @details Implements the json_escape function behavior with deterministic control flow.
- @param value Input parameter `value`.
- @return {str} Function return value.

### fn `def generate_kiro_resources(` (L2010-2013)

### fn `def render_kiro_agent(` (L2039-2048)
- @brief Generates the resource list for the Kiro agent.
- @details Implements the generate_kiro_resources function behavior with deterministic control flow.
- @param req_dir Input parameter `req_dir`.
- @param project_base Input parameter `project_base`.
- @param prompt_rel_path Input parameter `prompt_rel_path`.
- @return {list[str]} Function return value.

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L2094-2107)
- @brief Renders the Kiro agent JSON and populates main fields.
- @brief Replaces tokens in the specified file.
- @details Implements the render_kiro_agent function behavior with deterministic control flow.
- @details Implements the replace_tokens function behavior with deterministic control flow.
- @param template Input parameter `template`.
- @param name Input parameter `name`.
- @param description Input parameter `description`.
- @param prompt Input parameter `prompt`.
- @param resources Input parameter `resources`.
- @param tools Input parameter `tools`.
- @param model Input parameter `model`.
- @param include_tools Input parameter `include_tools`.
- @param include_model Input parameter `include_model`.
- @param path Input parameter `path`.
- @param replacements Input parameter `replacements`.
- @return {str} Function return value.
- @return {None} Function return value.

### fn `def yaml_double_quote_escape(value: str) -> str` (L2108-2117)
- @brief Minimal escape for a double-quoted string in YAML.
- @details Implements the yaml_double_quote_escape function behavior with deterministic control flow.
- @param value Input parameter `value`.
- @return {str} Function return value.

### fn `def list_docs_templates() -> list[Path]` (L2118-2137)
- @brief Returns non-hidden files available in resources/docs.
- @details Implements the list_docs_templates function behavior with deterministic control flow.
- @return Sorted list of file paths under resources/docs.
- @throws ReqError If resources/docs does not exist or has no non-hidden files.

### fn `def find_requirements_template(docs_templates: list[Path]) -> Path` (L2138-2154)
- @brief Returns the packaged Requirements template file.
- @details Implements the find_requirements_template function behavior with deterministic control flow.
- @param docs_templates Runtime docs template file list from resources/docs.
- @return Path to `Requirements_Template.md`.
- @throws ReqError If `Requirements_Template.md` is not present.

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L2155-2194)
- @brief Loads the Kiro template from centralized models configuration.
- @details Implements the load_kiro_template function behavior with deterministic control flow.
- @return {tuple[str, dict[str, Any]]} Function return value.

### fn `def strip_json_comments(text: str) -> str` (L2195-2219)
- @brief Removes // and /* */ comments to allow JSONC parsing.
- @details Implements the strip_json_comments function behavior with deterministic control flow.
- @param text Input parameter `text`.
- @return {str} Function return value.

### fn `def load_settings(path: Path) -> dict[str, Any]` (L2220-2235)
- @brief Loads JSON/JSONC settings, removing comments when necessary.
- @details Implements the load_settings function behavior with deterministic control flow.
- @param path Input parameter `path`.
- @return {dict[str, Any]} Function return value.

### fn `def load_centralized_models(` (L2236-2239)

### fn `def get_model_tools_for_prompt(` (L2294-2295)
- @brief Loads centralized models configuration from common/models.json.
- @details Returns a map cli_name -> parsed_json or None if not present. When preserve_models_path is provided and exists, loads from that file, ignoring legacy_mode. Otherwise, when legacy_mode is True, attempts to load models-legacy.json first, falling back to models.json if not found.
- @param resource_root Input parameter `resource_root`.
- @param legacy_mode Input parameter `legacy_mode`.
- @param preserve_models_path Input parameter `preserve_models_path`.
- @return {dict[str, dict[str, Any] | None]} Function return value.

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L2335-2356)
- @brief Extracts model and tools for the prompt from the CLI config.
- @brief Returns the raw value of `usage_modes[mode]['tools']` for the prompt.
- @details Returns (model, tools) where each value can be None if not available.
- @details Can return a list of strings, a string, or None depending on how it is defined in `config.json`. Does not perform CSV parsing: returns the value exactly as present in the configuration file.
- @param config Input parameter `config`.
- @param prompt_name Input parameter `prompt_name`.
- @param source_name Input parameter `source_name`.
- @param config Input parameter `config`.
- @param prompt_name Input parameter `prompt_name`.
- @return {tuple[Optional[str], Optional[list[str]]]} Function return value.
- @return {Any} Function return value.

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L2357-2368)
- @brief Formats the tools list as inline YAML/TOML/MD: ['a', 'b'].
- @details Implements the format_tools_inline_list function behavior with deterministic control flow.
- @param tools Input parameter `tools`.
- @return {str} Function return value.

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L2369-2384)
- @brief Recursively merges dictionaries, prioritizing incoming values.
- @details Implements the deep_merge_dict function behavior with deterministic control flow.
- @param base Input parameter `base`.
- @param incoming Input parameter `incoming`.
- @return {dict[str, Any]} Function return value.

### fn `def find_vscode_settings_source() -> Optional[Path]` (L2385-2396)
- @brief Finds the VS Code settings template if available.
- @details Implements the find_vscode_settings_source function behavior with deterministic control flow.
- @return {Optional[Path]} Function return value.

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L2397-2411)
- @brief Generates chat.promptFilesRecommendations from available prompts.
- @details Implements the build_prompt_recommendations function behavior with deterministic control flow.
- @param prompts_dir Input parameter `prompts_dir`.
- @return {dict[str, bool]} Function return value.

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L2412-2427)
- @brief Verifies that the path is under the project root.
- @details Implements the ensure_wrapped function behavior with deterministic control flow.
- @param target Input parameter `target`.
- @param project_base Input parameter `project_base`.
- @param code Input parameter `code`.
- @return {None} Function return value.

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L2428-2442)
- @brief Saves a backup of VS Code settings if the file exists.
- @details Implements the save_vscode_backup function behavior with deterministic control flow.
- @param req_root Input parameter `req_root`.
- @param settings_path Input parameter `settings_path`.
- @return {None} Function return value.

### fn `def restore_vscode_settings(project_base: Path) -> None` (L2443-2458)
- @brief Restores VS Code settings from backup, if present.
- @details Implements the restore_vscode_settings function behavior with deterministic control flow.
- @param project_base Input parameter `project_base`.
- @return {None} Function return value.

### fn `def prune_empty_dirs(root: Path) -> None` (L2459-2476)
- @brief Removes empty directories under the specified root.
- @details Implements the prune_empty_dirs function behavior with deterministic control flow.
- @param root Input parameter `root`.
- @return {None} Function return value.

### fn `def remove_generated_resources(project_base: Path) -> None` (L2477-2527)
- @brief Removes resources generated by the tool in the project root.
- @details Implements the remove_generated_resources function behavior with deterministic control flow.
- @param project_base Input parameter `project_base`.
- @return {None} Function return value.

### fn `def run_remove(args: Namespace) -> None` (L2528-2577)
- @brief Handles the removal of generated resources.
- @details Implements the run_remove function behavior with deterministic control flow.
- @param args Input parameter `args`.
- @return {None} Function return value.

### fn `def _validate_enable_static_check_command_executables(` `priv` (L2578-2581)

### fn `def run(args: Namespace) -> None` (L2610-2809)
- @brief Validate Command-module executables in `--enable-static-check` parsed entries.
- @brief Handles the main initialization flow.
- @details Validation scope is limited to Command entries coming from CLI specs.
Each Command `cmd` is resolved with `shutil.which`; on miss, raises `ReqError(code=1)`
before any configuration persistence.
- @details Validates input arguments, normalizes paths, and orchestrates resource generation per provider and artifact type. Requires at least one ``--provider`` spec (SRS-035). Deduplicates ``--enable-static-check`` entries (SRS-251, SRS-301).
- @param static_check_config Parsed static-check entries grouped by canonical language.
- @param enforce When false, skip validation and return immediately.
- @param args Parsed CLI namespace; must contain ``provider_specs`` list and ``preserve_models`` boolean.
- @return {None} Function return value.
- @return {None} Function return value.
- @throws ReqError If a Command entry references a non-executable `cmd` on this system.
- @see SRS-250
- @satisfies SRS-251, SRS-301

- var `VERBOSE = args.verbose` (L2619)
- @brief Handles the main initialization flow.
- @details Validates input arguments, normalizes paths, and orchestrates resource generation per provider and artifact type. Requires at least one ``--provider`` spec (SRS-035). Deduplicates ``--enable-static-check`` entries (SRS-251, SRS-301).
- @param args Parsed CLI namespace; must contain ``provider_specs`` list and ``preserve_models`` boolean.
- @return {None} Function return value.
- @satisfies SRS-251, SRS-301
- var `DEBUG = args.debug` (L2620)
- var `PROMPT = prompt_path.stem` (L3125)
### fn `def _format_install_table(` `priv` (L3753-3755)

### fn `def _wrap_cell(value: str, width: int, allow_wrap: bool) -> list[str]` `priv` (L3792-3814)
- @brief Format the Unicode installation summary table.
- @brief Normalize one table cell to printable lines.
- @details Builds a deterministic box-drawing table with columns: Provider, Prompts Installed, Modules Installed.
Prompts Installed is wrapped to a maximum width of 50 characters. Modules Installed renders one non-wrapped
line per active artifact as `artifact` when no options are active, or `artifact:options` when options exist.
Borders are emitted with Unicode line-drawing characters and bright-red ANSI styling.
- @details Preserves explicit newline-separated segments. When wrapping is enabled, wraps each segment to the target width; otherwise keeps each segment as-is.
- @param modules_map {dict[str, list[str]]} Mapping: provider name -> module-entry lines in `artifact` or `artifact:options` format.
- @param prompts_map {dict[str, set[str]]} Mapping: provider name -> installed prompt identifiers (union across artifact types).
- @param value {str} Cell text payload.
- @param width {int} Maximum cell width.
- @param allow_wrap {bool} Whether to apply line wrapping.
- @return {list[str]} Fully formatted table lines (including separators) ready for printing.
- @return {list[str]} Normalized printable lines for the cell.
- @note Complexity: O(C * (P log P + M)) where C is provider count, P is prompts per provider, M is module-entry lines per provider.
- @note Side effects: None (pure formatting).

### fn `def _render_row(provider: str, prompts: str, modules: str) -> list[str]` `priv` (L3815-3843)
- @brief Render one logical table row into one or more physical lines.
- @details Applies per-cell wrapping and left alignment, then expands the row height to the maximum wrapped cell line count.
- @param provider {str} Provider cell text.
- @param prompts {str} Prompts Installed cell text.
- @param modules {str} Modules Installed cell text.
- @return {list[str]} Physical row lines encoded with box-drawing separators.

### fn `def _build_provider_modules_map(provider_specs: list[str]) -> dict[str, list[str]]` `priv` (L3864-3903)
- @brief Build provider-to-module-entry mapping for installation table rendering.
- @details Parses raw `--provider` specifications preserving token order, then emits one module-entry line per active artifact as `artifact` or `artifact:options`.
- @param provider_specs {list[str]} Raw `--provider` SPEC values after update-merging logic.
- @return {dict[str, list[str]]} Mapping from provider to ordered module-entry lines.

### fn `def _colorize_table_border(line: str) -> str` `priv` (L3904-3916)
- @brief Colorize box-drawing border glyphs with bright-red ANSI style.
- @details Applies color to border characters while preserving cell payload text color.
- @param line {str} One already-rendered table line.
- @return {str} Line with border glyphs wrapped in ANSI bright-red and reset sequences.

- var `SUPPORTED_EXTENSIONS = frozenset(` (L3931)
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L3959-4016)
- @brief Collect source files from git-indexed project paths.
- @details Uses `git ls-files --cached --others --exclude-standard` in project root, filters by src-dir prefixes, applies EXCLUDED_DIRS filtering, and keeps only SUPPORTED_EXTENSIONS files.
- @param src_dirs Input parameter `src_dirs`.
- @param project_base Input parameter `project_base`.
- @return {list[str]} Function return value.

### fn `def _build_ascii_tree(paths: list[str]) -> str` `priv` (L4017-4062)
- @brief Build a deterministic tree string from project-relative paths.
- @details Implements the _build_ascii_tree function behavior with deterministic control flow.
- @param paths Project-relative file paths.
- @return Rendered tree rooted at '.'.

### fn `def _emit(` `priv` (L4041-4043)
- @brief Build a deterministic tree string from project-relative paths.
- @details Implements the _build_ascii_tree function behavior with deterministic control flow.
- @param paths Project-relative file paths.
- @return Rendered tree rooted at '.'.

### fn `def _format_files_structure_markdown(files: list[str], project_base: Path) -> str` `priv` (L4063-4077)
- @brief Format markdown section containing the scanned files tree.
- @details Implements the _format_files_structure_markdown function behavior with deterministic control flow.
- @param files Absolute file paths selected for --references processing.
- @param project_base Project root used to normalize relative paths.
- @return Markdown section with heading and fenced tree.

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L4078-4096)
- @brief Check if the parsed args contain a standalone file command.
- @details Standalone commands require no `--base`/`--here`: `--files-tokens`, `--files-references`, `--files-compress`, `--files-find`, `--test-static-check`, and `--files-static-check`. SRS-253 adds `--files-static-check` to this group.
- @param args Parsed CLI namespace.
- @return True when any file-scope standalone flag is present.

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L4097-4120)
- @brief Check if the parsed args contain a project-scan command.
- @details Project-scan commands: `--references`, `--compress`, `--tokens`, `--find`, `--static-check`, `--git-check`, `--docs-check`, `--git-wt-name`, `--git-wt-create`, `--git-wt-delete`, and `--git-wt-exit`.
- @param args Parsed CLI namespace.
- @return True when any project-scan flag is present.

### fn `def _is_here_only_project_scan_command(args: Namespace) -> bool` `priv` (L4121-4145)
- @brief Check if args request a project-scan command restricted to `--here` mode.
- @details Includes `--references`, `--compress`, `--tokens`, `--find`, `--static-check`, `--git-check`, `--docs-check`, `--git-wt-name`, `--git-wt-create`, `--git-wt-delete`, and `--git-wt-exit`.
- @param args Parsed CLI namespace.
- @return True when command requires implicit `--here` and rejects `--base`.
- @satisfies SRS-311, SRS-313, SRS-318, SRS-320, SRS-326, SRS-333

### fn `def run_git_check(args: Namespace) -> None` (L4146-4177)
- @brief Execute --git-check: verify clean git status and valid HEAD.
- @param args Parsed CLI namespace.
- @return {None} Function return value.
- @throws ReqError On git status unclear or config load failure.
- @satisfies SRS-311, SRS-312

### fn `def run_docs_check(args: Namespace) -> None` (L4178-4207)
- @brief Execute --docs-check: verify existence of REQUIREMENTS.md, WORKFLOW.md, REFERENCES.md.
- @param args Parsed CLI namespace.
- @return {None} Function return value.
- @throws ReqError If any required doc file is missing.
- @satisfies SRS-313, SRS-314, SRS-315, SRS-316, SRS-317

### fn `def run_git_wt_name(args: Namespace) -> None` (L4208-4236)
- @brief Execute --git-wt-name: print standardized worktree name.
- @param args Parsed CLI namespace.
- @return {None} Function return value.
- @satisfies SRS-318, SRS-319

### fn `def _worktree_path_exists_exact(git_path: Path, target_path: Path) -> bool` `priv` (L4237-4266)
- @brief Check whether a git worktree exists at the exact target path.
- @details Parses `git worktree list --porcelain` output by `worktree <path>` records and performs exact path comparison to prevent partial-name or substring matches.
- @param git_path Absolute git root path used as command cwd.
- @param target_path Absolute worktree path expected for WT_NAME.
- @return {bool} True only when target_path is listed as an exact worktree path.
- @throws ReqError On git command execution errors.

### fn `def _rollback_worktree_create(git_path: Path, wt_path: Path, wt_name: str) -> None` `priv` (L4267-4303)
- @brief Roll back worktree and branch created by --git-wt-create on post-create failure.
- @details Uses `git worktree remove <path> --force` and `git branch -D <name>` to restore a clean git state when post-create copy/chdir operations fail.
- @param git_path Absolute git root path used as command cwd.
- @param wt_path Absolute worktree path to remove.
- @param wt_name Exact branch name to delete.
- @return {None} Function return value.
- @throws ReqError If rollback cannot remove the exact target worktree and branch.

### fn `def run_git_wt_create(args: Namespace) -> None` (L4304-4395)
- @brief Execute --git-wt-create: create a git worktree and copy .req/provider dirs.
- @param args Parsed CLI namespace.
- @return {None} Function return value.
- @throws ReqError On invalid name, git command failure, or config errors.
- @satisfies SRS-320, SRS-321, SRS-322, SRS-323, SRS-324, SRS-325, SRS-331, SRS-335

### fn `def run_git_wt_delete(args: Namespace) -> None` (L4396-4473)
- @brief Execute --git-wt-delete: remove a git worktree and branch by name.
- @param args Parsed CLI namespace.
- @return {None} Function return value.
- @throws ReqError On invalid name or git removal failure.
- @satisfies SRS-326, SRS-327, SRS-328, SRS-332

### fn `def run_git_wt_exit(args: Namespace) -> None` (L4474-4490)
- @brief Execute --git-wt-exit: change current directory to configured base-path.
- @param args Parsed CLI namespace.
- @return {None} Function return value.
- @throws ReqError On missing or invalid base-path configuration.
- @satisfies SRS-333, SRS-334

### fn `def run_files_tokens(files: list[str]) -> None` (L4491-4513)
- @brief Execute --files-tokens: count tokens for arbitrary files.
- @details Implements the run_files_tokens function behavior with deterministic control flow.
- @param files Input parameter `files`.
- @return {None} Function return value.

### fn `def run_files_references(files: list[str]) -> None` (L4514-4530)
- @brief Execute --files-references: generate markdown for arbitrary files.
- @details Implements the run_files_references function behavior with deterministic control flow.
- @param files Input parameter `files`.
- @return {None} Function return value.

### fn `def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None` (L4531-4549)
- @brief Execute --files-compress: compress arbitrary files.
- @details Renders output header paths relative to current working directory.
- @param files List of source file paths to compress.
- @param enable_line_numbers If True, emits <n>: prefixes in compressed entries.
- @return {None} Function return value.

### fn `def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None` (L4550-4578)
- @brief Execute --files-find: find constructs in arbitrary files.
- @details Implements the run_files_find function behavior with deterministic control flow.
- @param args_list Combined list: [TAG, PATTERN, FILE1, FILE2, ...].
- @param enable_line_numbers If True, emits <n>: prefixes in output.
- @return {None} Function return value.

### fn `def run_references(args: Namespace) -> None` (L4579-4596)
- @brief Execute --references: generate markdown for project source files.
- @details Implements the run_references function behavior with deterministic control flow.
- @param args Input parameter `args`.
- @return {None} Function return value.

### fn `def run_compress_cmd(args: Namespace) -> None` (L4597-4618)
- @brief Execute --compress: compress project source files.
- @details Implements the run_compress_cmd function behavior with deterministic control flow.
- @param args Parsed CLI arguments namespace.
- @return {None} Function return value.

### fn `def run_find(args: Namespace) -> None` (L4619-4648)
- @brief Execute --find: find constructs in project source files.
- @details Implements the run_find function behavior with deterministic control flow.
- @param args Parsed CLI arguments namespace.
- @return {None} Function return value.
- @throws ReqError If no source files found or no constructs match criteria with available TAGs listing.

### fn `def run_tokens(args: Namespace) -> None` (L4649-4676)
- @brief Execute --tokens on the canonical documentation files in --docs-dir.
- @details Uses docs-dir from .req/config.json in here-only mode, ignores explicit --docs-dir, selects only REQUIREMENTS.md/WORKFLOW.md/REFERENCES.md as direct regular files in fixed order, and delegates summary rendering to run_files_tokens.
- @param args Parsed CLI arguments namespace.
- @return None.
- @exception ReqError Raised when no canonical documentation file exists in configured docs-dir.

### fn `def run_files_static_check_cmd(files: list[str], args: Namespace) -> int` (L4677-4747)
- @brief Execute `--files-static-check`: run static analysis on an explicit file list.
- @details Project-base resolution order: 1. `--base PATH` -> use PATH. 2. `--here` -> use CWD. 3. Fallback -> use CWD. If `.req/config.json` is not found at the resolved project base, emits a warning to stderr and returns 0 (SRS-254). For each file: - Resolves absolute path; skips with warning if not a regular file. - Detects language via `STATIC_CHECK_EXT_TO_LANG` keyed on the lowercase extension. - Looks up language in the `"static-check"` config section; skips silently if absent. - Executes each configured language entry sequentially via `dispatch_static_check_for_file(filepath, lang_config)`. - For `Command` module entries, execution order is `<cmd> [params...] <filename>`. Overall exit code: max of all per-file codes (0=all pass, 1=any fail). (SRS-253, SRS-255)
- @param files List of raw file paths supplied by the user.
- @param args Parsed CLI namespace; `--here`/`--base` are used to locate config.json.
- @return Exit code: 0 if all checked files pass (or none are checked), 1 if any fail.
- @see SRS-253, SRS-254, SRS-255

### fn `def run_project_static_check_cmd(args: Namespace) -> int` (L4748-4794)
- @brief Execute `--static-check`: run static analysis on all project source files.
- @details Uses the same file-collection logic as `--references` and `--compress` (SRS-177, SRS-179, SRS-180, SRS-181): collects files from configured `src-dir` directories, applies `EXCLUDED_DIRS` filtering and `SUPPORTED_EXTENSIONS` matching. For each collected file: - Detects language via `STATIC_CHECK_EXT_TO_LANG` keyed on lowercase extension. - Looks up language in the `"static-check"` section of `.req/config.json`. - Skips silently when no tool is configured for the file's language. - Executes each configured language entry sequentially via `dispatch_static_check_for_file(filepath, lang_config)`. - For `Command` module entries, execution order is `<cmd> [params...] <filename>`. Overall exit code: max of all per-file codes (0=all pass, 1=any fail). (SRS-256, SRS-257)
- @param args Parsed CLI namespace; here-only project scan (`--here` implied; `--base` rejected).
- @return Exit code: 0 if all checked files pass (or none are checked), 1 if any fail.
- @throws ReqError If no source files are found.
- @see SRS-256, SRS-257

### fn `def _resolve_project_base(args: Namespace) -> Path` `priv` (L4795-4815)
- @brief Resolve project base path for project-level commands.
- @details Implements the _resolve_project_base function behavior with deterministic control flow.
- @param args Parsed CLI arguments namespace.
- @return Absolute path of project base.
- @throws ReqError If --base/--here is missing or the resolved path does not exist.

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L4816-4868)
- @brief Resolve project base and src-dirs for project source commands.
- @details Implements the _resolve_project_src_dirs function behavior with deterministic control flow.
- @param args Input parameter `args`.
- @return {tuple[Path, list[str]]} Function return value.

### fn `def main(argv: Optional[list[str]] = None) -> int` (L4869-4969)
- @brief CLI entry point for console_scripts and `-m` execution.
- @details Returns an exit code (0 success, non-zero on error).
- @param argv Input parameter `argv`.
- @return {int} Function return value.

- var `VERBOSE = getattr(args, "verbose", False)` (L4893)
- @brief CLI entry point for console_scripts and `-m` execution.
- @details Returns an exit code (0 success, non-zero on error).
- @param argv Input parameter `argv`.
- @return {int} Function return value.
- var `DEBUG = getattr(args, "debug", False)` (L4894)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|29||
|`RESOURCE_ROOT`|var|pub|32||
|`VERBOSE`|var|pub|35||
|`DEBUG`|var|pub|38||
|`REQUIREMENTS_TEMPLATE_NAME`|var|pub|41||
|`PERSISTED_UPDATE_FLAG_KEYS`|var|pub|44||
|`VALID_PROVIDERS`|var|pub|47||
|`VALID_ARTIFACTS`|var|pub|50||
|`VALID_PROVIDER_OPTIONS`|var|pub|53||
|`INVALID_WT_NAME_RE`|var|pub|68||
|`parse_provider_spec`|fn|pub|72-123|def parse_provider_spec(spec: str) -> tuple[str, set[str]...|
|`resolve_provider_configs`|fn|pub|124-125|def resolve_provider_configs(|
|`ANSI_BRIGHT_RED`|var|pub|176||
|`ANSI_BRIGHT_GREEN`|var|pub|179||
|`ANSI_RESET`|var|pub|182||
|`RELEASE_CHECK_TIMEOUT_SECONDS`|var|pub|185||
|`RELEASE_CHECK_IDLE_DELAY_SECONDS`|var|pub|188||
|`TOOL_PROGRAM_NAME`|var|pub|191||
|`RELEASE_CHECK_PROGRAM_NAME`|var|pub|194||
|`GITHUB_REPOSITORY_OWNER`|var|pub|197||
|`GITHUB_REPOSITORY_NAME`|var|pub|200||
|`RELEASE_CHECK_IDLE_FILENAME_TEMPLATE`|var|pub|203||
|`GITHUB_RELEASES_LATEST_URL`|var|pub|206||
|`GITHUB_UPGRADE_SOURCE`|var|pub|212||
|`ReqError`|class|pub|218-235|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|223-235|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|236-245|def log(msg: str) -> None|
|`dlog`|fn|pub|246-256|def dlog(msg: str) -> None|
|`vlog`|fn|pub|257-267|def vlog(msg: str) -> None|
|`_get_available_tags_help`|fn|priv|268-280|def _get_available_tags_help() -> str|
|`build_parser`|fn|pub|281-480|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|544-553|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|554-568|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|569-581|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|582-608|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|609-632|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|633-645|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|646-670|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|671-689|def is_newer_version(current: str, latest: str) -> bool|
|`parse_github_owner_repository`|fn|pub|690-716|def parse_github_owner_repository(remote_url: str) -> tup...|
|`read_git_remote_verbose`|fn|pub|717-736|def read_git_remote_verbose(cwd: str | None = None) -> str|
|`resolve_github_owner_repository_from_active_remotes`|fn|pub|737-797|def resolve_github_owner_repository_from_active_remotes()...|
|`resolve_latest_release_api_url`|fn|pub|798-806|def resolve_latest_release_api_url() -> str|
|`format_unix_timestamp_utc`|fn|pub|807-819|def format_unix_timestamp_utc(timestamp_seconds: int) -> str|
|`get_release_check_idle_file_path`|fn|pub|820-821|def get_release_check_idle_file_path(|
|`read_release_check_idle_state`|fn|pub|833-897|def read_release_check_idle_state(file_path: Path) -> dic...|
|`should_execute_release_check`|fn|pub|898-900|def should_execute_release_check(|
|`parse_retry_after_seconds`|fn|pub|918-920|def parse_retry_after_seconds(|
|`write_release_check_idle_state_payload`|fn|pub|950-953|def write_release_check_idle_state_payload(|
|`write_release_check_idle_state`|fn|pub|979-982|def write_release_check_idle_state(|
|`write_rate_limited_release_check_idle_state`|fn|pub|1000-1005|def write_rate_limited_release_check_idle_state(|
|`maybe_notify_newer_version`|fn|pub|1039-1040|def maybe_notify_newer_version(|
|`ensure_doc_directory`|fn|pub|1171-1193|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|1194-1216|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|1217-1239|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|1240-1281|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|1282-1297|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|1298-1309|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|1310-1311|def compute_sub_path(|
|`resolve_git_root`|fn|pub|1332-1359|def resolve_git_root(target_path: Path) -> Path|
|`is_inside_git_repo`|fn|pub|1360-1379|def is_inside_git_repo(target_path: Path) -> bool|
|`sanitize_branch_name`|fn|pub|1380-1389|def sanitize_branch_name(branch: str) -> str|
|`validate_wt_name`|fn|pub|1390-1401|def validate_wt_name(wt_name: str) -> bool|
|`load_full_config`|fn|pub|1402-1421|def load_full_config(project_base: Path) -> dict|
|`save_config`|fn|pub|1422-1432|def save_config(|
|`load_config`|fn|pub|1476-1526|def load_config(project_base: Path) -> dict[str, str | li...|
|`load_static_check_from_config`|fn|pub|1527-1558|def load_static_check_from_config(project_base: Path) -> ...|
|`_static_check_entry_identity`|fn|priv|1559-1560|def _static_check_entry_identity(|
|`build_persisted_update_flags`|fn|pub|1583-1596|def build_persisted_update_flags(args: Namespace) -> dict...|
|`load_persisted_update_flags`|fn|pub|1597-1638|def load_persisted_update_flags(project_base: Path) -> di...|
|`load_persisted_provider_specs`|fn|pub|1639-1660|def load_persisted_provider_specs(project_base: Path) -> ...|
|`generate_guidelines_file_list`|fn|pub|1661-1693|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|1694-1695|def generate_guidelines_file_items(|
|`upgrade_guidelines_templates`|fn|pub|1729-1763|def upgrade_guidelines_templates(guidelines_dest: Path, o...|
|`make_relative_token`|fn|pub|1764-1780|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|1781-1796|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|1797-1809|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|1810-1821|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|1822-1823|def copy_with_replacements(|
|`normalize_description`|fn|pub|1838-1852|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|1853-1887|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|1888-1901|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|1902-1914|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|1915-1927|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|1928-1952|def extract_purpose_first_bullet(body: str) -> str|
|`_extract_section_text`|fn|priv|1953-1980|def _extract_section_text(body: str, section_name: str) -...|
|`extract_skill_description`|fn|pub|1981-1999|def extract_skill_description(frontmatter: str) -> str|
|`json_escape`|fn|pub|2000-2009|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|2010-2013|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|2039-2048|def render_kiro_agent(|
|`replace_tokens`|fn|pub|2094-2107|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|2108-2117|def yaml_double_quote_escape(value: str) -> str|
|`list_docs_templates`|fn|pub|2118-2137|def list_docs_templates() -> list[Path]|
|`find_requirements_template`|fn|pub|2138-2154|def find_requirements_template(docs_templates: list[Path]...|
|`load_kiro_template`|fn|pub|2155-2194|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|2195-2219|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|2220-2235|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|2236-2239|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|2294-2295|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|2335-2356|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|2357-2368|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|2369-2384|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|2385-2396|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|2397-2411|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|2412-2427|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|2428-2442|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|2443-2458|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|2459-2476|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|2477-2527|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|2528-2577|def run_remove(args: Namespace) -> None|
|`_validate_enable_static_check_command_executables`|fn|priv|2578-2581|def _validate_enable_static_check_command_executables(|
|`run`|fn|pub|2610-2809|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|2619||
|`DEBUG`|var|pub|2620||
|`PROMPT`|var|pub|3125||
|`_format_install_table`|fn|priv|3753-3755|def _format_install_table(|
|`_wrap_cell`|fn|priv|3792-3814|def _wrap_cell(value: str, width: int, allow_wrap: bool) ...|
|`_render_row`|fn|priv|3815-3843|def _render_row(provider: str, prompts: str, modules: str...|
|`_build_provider_modules_map`|fn|priv|3864-3903|def _build_provider_modules_map(provider_specs: list[str]...|
|`_colorize_table_border`|fn|priv|3904-3916|def _colorize_table_border(line: str) -> str|
|`SUPPORTED_EXTENSIONS`|var|pub|3931||
|`_collect_source_files`|fn|priv|3959-4016|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_build_ascii_tree`|fn|priv|4017-4062|def _build_ascii_tree(paths: list[str]) -> str|
|`_emit`|fn|priv|4041-4043|def _emit(|
|`_format_files_structure_markdown`|fn|priv|4063-4077|def _format_files_structure_markdown(files: list[str], pr...|
|`_is_standalone_command`|fn|priv|4078-4096|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|4097-4120|def _is_project_scan_command(args: Namespace) -> bool|
|`_is_here_only_project_scan_command`|fn|priv|4121-4145|def _is_here_only_project_scan_command(args: Namespace) -...|
|`run_git_check`|fn|pub|4146-4177|def run_git_check(args: Namespace) -> None|
|`run_docs_check`|fn|pub|4178-4207|def run_docs_check(args: Namespace) -> None|
|`run_git_wt_name`|fn|pub|4208-4236|def run_git_wt_name(args: Namespace) -> None|
|`_worktree_path_exists_exact`|fn|priv|4237-4266|def _worktree_path_exists_exact(git_path: Path, target_pa...|
|`_rollback_worktree_create`|fn|priv|4267-4303|def _rollback_worktree_create(git_path: Path, wt_path: Pa...|
|`run_git_wt_create`|fn|pub|4304-4395|def run_git_wt_create(args: Namespace) -> None|
|`run_git_wt_delete`|fn|pub|4396-4473|def run_git_wt_delete(args: Namespace) -> None|
|`run_git_wt_exit`|fn|pub|4474-4490|def run_git_wt_exit(args: Namespace) -> None|
|`run_files_tokens`|fn|pub|4491-4513|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|4514-4530|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|4531-4549|def run_files_compress(files: list[str], enable_line_numb...|
|`run_files_find`|fn|pub|4550-4578|def run_files_find(args_list: list[str], enable_line_numb...|
|`run_references`|fn|pub|4579-4596|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|4597-4618|def run_compress_cmd(args: Namespace) -> None|
|`run_find`|fn|pub|4619-4648|def run_find(args: Namespace) -> None|
|`run_tokens`|fn|pub|4649-4676|def run_tokens(args: Namespace) -> None|
|`run_files_static_check_cmd`|fn|pub|4677-4747|def run_files_static_check_cmd(files: list[str], args: Na...|
|`run_project_static_check_cmd`|fn|pub|4748-4794|def run_project_static_check_cmd(args: Namespace) -> int|
|`_resolve_project_base`|fn|priv|4795-4815|def _resolve_project_base(args: Namespace) -> Path|
|`_resolve_project_src_dirs`|fn|priv|4816-4868|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|4869-4969|def main(argv: Optional[list[str]] = None) -> int|
|`VERBOSE`|var|pub|4893||
|`DEBUG`|var|pub|4894||


---

# compress.py | Python | 393L | 11 symbols | 4 imports | 41 comments
> Path: `src/usereq/compress.py`
- @brief Source code compressor for LLM context optimization.
- @details Parses a source file and removes all comments (inline, single-line, multi-line), blank lines, trailing whitespace, and redundant spacing while preserving language semantics (e.g. Python indentation). Leverages LanguageSpec from source_analyzer to correctly identify comment syntax for each supported language.
@author GitHub Copilot
@version 0.0.70

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
- @brief Cached language specification dictionary initialized lazily."""
- @brief Return cached language specifications, initializing once.
- @details If cache is empty, calls `build_language_specs()` to populate it.
- @return Dictionary mapping normalized language keys to language specs.

### fn `def detect_language(filepath: str) -> str | None` (L46-55)
- @brief Detect language key from file extension.
- @details Uses `EXT_LANG_MAP` for lookup. Case-insensitive extension matching.
- @param filepath Source file path.
- @return Normalized language key, or None when extension is unsupported.

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L56-97)
- @brief Check if position `pos` in `line` is inside a string literal.
- @details iterates through the line handling escaped delimiters.
- @param line The code line string.
- @param pos The character index to check.
- @param string_delimiters Tuple of string delimiter characters/sequences.
- @return True if `pos` is inside a string, False otherwise.

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L98-141)
- @brief Remove trailing single-line comment from a code line.
- @details Respects string literals; does not remove comments inside strings.
- @param line The code line string.
- @param single_comment The single-line comment marker (e.g., "//", "#").
- @param string_delimiters Tuple of string delimiters to respect.
- @return The line content before the comment starts.

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L142-155)
- @brief Check if a line is a standalone Python docstring (triple-quote only).
- @details Implements the _is_python_docstring_line function behavior with deterministic control flow.
- @param line The code line string.
- @return True if the line appears to be a standalone triple-quoted string.

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L156-169)
- @brief Format compressed entries, optionally prefixing original line numbers.
- @details Implements the _format_result function behavior with deterministic control flow.
- @param entries List of tuples (line_number, text).
- @param include_line_numbers Boolean flag to enable line prefixes.
- @return Formatted string.

### fn `def compress_source(source: str, language: str,` (L170-337)
- @brief Compress source code by removing comments, blank lines, and extra whitespace.
- @details Preserves indentation for indent-significant languages (Python, Haskell, Elixir).
- @param source The source code string.
- @param language Language identifier (e.g. "python", "javascript").
- @param include_line_numbers If True (default), prefix each line with <n>: format.
- @return Compressed source code string.
- @throws ValueError If language is unsupported.

### fn `def compress_file(filepath: str, language: str | None = None,` (L338-361)
- @brief Compress a source file by removing comments and extra whitespace.
- @details Implements the compress_file function behavior with deterministic control flow.
- @param filepath Path to the source file.
- @param language Optional language override. Auto-detected if None.
- @param include_line_numbers If True (default), prefix each line with <n>: format.
- @return Compressed source code string.
- @throws ValueError If language cannot be detected.

### fn `def main()` (L362-391)
- @brief Execute the standalone compression CLI.
- @details Parses command-line arguments and invokes `compress_file`, printing the result to stdout or errors to stderr.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|16||
|`INDENT_SIGNIFICANT`|var|pub|28||
|`_get_specs`|fn|priv|35-45|def _get_specs()|
|`detect_language`|fn|pub|46-55|def detect_language(filepath: str) -> str | None|
|`_is_in_string`|fn|priv|56-97|def _is_in_string(line: str, pos: int, string_delimiters:...|
|`_remove_inline_comment`|fn|priv|98-141|def _remove_inline_comment(line: str, single_comment: str,|
|`_is_python_docstring_line`|fn|priv|142-155|def _is_python_docstring_line(line: str) -> bool|
|`_format_result`|fn|priv|156-169|def _format_result(entries: list[tuple[int, str]],|
|`compress_source`|fn|pub|170-337|def compress_source(source: str, language: str,|
|`compress_file`|fn|pub|338-361|def compress_file(filepath: str, language: str | None = N...|
|`main`|fn|pub|362-391|def main()|


---

# compress_files.py | Python | 134L | 4 symbols | 5 imports | 6 comments
> Path: `src/usereq/compress_files.py`
- @brief Compress and concatenate multiple source files.
- @details Uses the compress module to strip comments and whitespace from each input file, then concatenates results with a compact header per file for unique identification by an LLM agent.
@author GitHub Copilot
@version 0.0.70

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
- @brief Extract source line interval from compressed output with <n>: prefixes.
- @details Parses the first token of each line as an integer line number.
- @param compressed_with_line_numbers Compressed payload generated with include_line_numbers=True.
- @return Tuple (line_start, line_end) derived from preserved <n>: prefixes; returns (0, 0) when no prefixed lines exist.

### fn `def _format_output_path(filepath: str, output_base: Path | None) -> str` `priv` (L35-48)
- @brief Build the header-visible path for one compressed source file.
- @details Implements the _format_output_path function behavior with deterministic control flow.
- @param filepath Absolute or relative source file path.
- @param output_base Project-home base used to relativize output paths.
- @return Original filepath when output_base is None; otherwise POSIX relative path from output_base.

### fn `def compress_files(filepaths: list[str],` (L49-109)

### fn `def main()` (L110-132)
- @brief Execute the multi-file compression CLI command.
- @details Parses command-line arguments, calls `compress_files`, and prints output or errors.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_extract_line_range`|fn|priv|17-34|def _extract_line_range(compressed_with_line_numbers: str...|
|`_format_output_path`|fn|priv|35-48|def _format_output_path(filepath: str, output_base: Path ...|
|`compress_files`|fn|pub|49-109|def compress_files(filepaths: list[str],|
|`main`|fn|pub|110-132|def main()|


---

# doxygen_parser.py | Python | 172L | 6 symbols | 2 imports | 19 comments
> Path: `src/usereq/doxygen_parser.py`
- @brief Doxygen comment parser for extracting structured documentation fields.
- @brief ,
- @details Parses Doxygen-formatted documentation comments and extracts recognized tags (
- @param ,
- @return , etc.) into structured dictionaries for downstream LLM-optimized markdown rendering.
@author GitHub Copilot
@version 0.0.70

## Imports
```
import re
from typing import Dict, List
```

## Definitions

- var `DOXYGEN_TAGS = [` (L15)
- var `DOXYGEN_TAG_PATTERN = re.compile(` (L44)
- @brief Regex alternation for non-param tags ordered by descending length."""
### fn `def parse_doxygen_comment(comment_text: str) -> Dict[str, List[str]]` (L51-99)
- @brief Compiled regex that matches supported @tag / \\tag tokens."""
- @brief Extract Doxygen fields from a documentation comment block.
- @details Parses both @tag and \\tag syntax. Each tag's content extends until the next tag or end of comment. Multiple occurrences of the same tag accumulate in the returned list. Whitespace is normalized.
- @param comment_text Raw comment string potentially containing Doxygen tags.
- @return Dictionary mapping normalized tag names to lists of extracted content strings.
- @note Returns empty dict if no Doxygen tags are found.
- @see DOXYGEN_TAGS for recognized tag list.

### fn `def _strip_comment_delimiters(text: str) -> str` `priv` (L100-128)
- @brief Remove common comment delimiters from text block.
- @details Strips leading/trailing /**, */, //, #, triple quotes, and intermediate * column markers. Preserves content while removing comment syntax artifacts.
- @param text Raw comment block possibly containing comment delimiters.
- @return Cleaned text with delimiters removed.

### fn `def _normalize_whitespace(text: str) -> str` `priv` (L129-154)
- @brief Normalize internal whitespace in extracted tag content.
- @details Collapses multiple spaces to single space, preserves single newlines, removes redundant blank lines.
- @param text Tag content with potentially irregular whitespace.
- @return Whitespace-normalized content.

### fn `def format_doxygen_fields_as_markdown(doxygen_fields: Dict[str, List[str]]) -> List[str]` (L155-172)
- @brief Format extracted Doxygen fields as Markdown bulleted list.
- @details Emits fields in fixed order (DOXYGEN_TAGS) preserving original Doxygen tag tokens with `@` prefix and no `:` suffix. Skips tags not present in input. Each extracted field occurrence is emitted as an independent markdown bullet.
- @param doxygen_fields Dictionary of tag -> content list from parse_doxygen_comment().
- @return List of Markdown lines (each starting with '- ').
- @note Output order matches DOXYGEN_TAGS sequence.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`DOXYGEN_TAGS`|var|pub|15||
|`DOXYGEN_TAG_PATTERN`|var|pub|44||
|`parse_doxygen_comment`|fn|pub|51-99|def parse_doxygen_comment(comment_text: str) -> Dict[str,...|
|`_strip_comment_delimiters`|fn|priv|100-128|def _strip_comment_delimiters(text: str) -> str|
|`_normalize_whitespace`|fn|priv|129-154|def _normalize_whitespace(text: str) -> str|
|`format_doxygen_fields_as_markdown`|fn|pub|155-172|def format_doxygen_fields_as_markdown(doxygen_fields: Dic...|


---

# find_constructs.py | Python | 394L | 12 symbols | 7 imports | 19 comments
> Path: `src/usereq/find_constructs.py`
- @brief Find and extract specific constructs from source files.
- @details Filters source code constructs (CLASS, FUNCTION, etc.) by type tag and name regex pattern, generating markdown output with complete code extracts.
@author GitHub Copilot
@version 0.0.70

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
- @brief Generate formatted list of available TAGs per language.
- @details Iterates LANGUAGE_TAGS dictionary, formats each entry as "- Language: TAG1, TAG2, ..." with language capitalized and tags alphabetically sorted and comma-separated.
- @return Multi-line string listing each language with its supported TAGs.

### fn `def parse_tag_filter(tag_string: str) -> set[str]` (L58-66)
- @brief Parse pipe-separated tag filter into a normalized set.
- @details Splits the input string by pipe character `|` and strips whitespace from each component.
- @param tag_string Raw tag filter string (e.g., "CLASS|FUNCTION").
- @return Set of uppercase tag identifiers.

### fn `def language_supports_tags(lang: str, tag_set: set[str]) -> bool` (L67-77)
- @brief Check if the language supports at least one of the requested tags.
- @details Lookups the language in `LANGUAGE_TAGS` and checks if any of `tag_set` exists in the supported tags.
- @param lang Normalized language identifier.
- @param tag_set Set of requested TAG identifiers.
- @return True if intersection is non-empty, False otherwise.

### fn `def construct_matches(element, tag_set: set[str], pattern: str) -> bool` (L78-95)
- @brief Check if a source element matches tag filter and regex pattern.
- @details Validates the element type and then applies the regex search on the element name.
- @param element SourceElement instance from analyzer.
- @param tag_set Set of requested TAG identifiers.
- @param pattern Regex pattern string to test against element name.
- @return True if element type is in tag_set and name matches pattern.

### fn `def _merge_doxygen_fields(` `priv` (L96-98)

### fn `def _extract_construct_doxygen_fields(element) -> dict[str, list[str]]` `priv` (L113-136)
- @brief Merge Doxygen fields preserving per-tag content order.
- @brief Build aggregate Doxygen fields for one construct.
- @details Appends extra field values to base field lists for matching tags and initializes missing tags. Mutates and returns base_fields.
- @details Uses canonical `element.doxygen_fields` from `SourceAnalyzer.enrich()` and merges only body comments located at construct start (first 3 lines) to retain docstring-style Doxygen blocks while preventing internal-body duplication.
- @param base_fields Canonical field dictionary to update.
- @param extra_fields Additional parsed fields to append.
- @param element SourceElement instance potentially enriched with doxygen_fields and body_comments.
- @return Updated base_fields dictionary.
- @return Dictionary tag->list preserving tag content insertion order.

### fn `def _extract_file_level_doxygen_fields(elements: list) -> dict[str, list[str]]` `priv` (L137-161)
- @brief Extract file-level Doxygen fields from the first comment containing `@file`.
- @details Scans non-inline comment elements in source order and parses the first block containing `@file` or `\\file` markers.
- @param elements SourceAnalyzer output for one source file.
- @return Parsed Doxygen fields from the file-level comment; empty dictionary if absent.

### fn `def _strip_construct_comments(` `priv` (L162-166)

### fn `def format_construct(` (L202-206)
- @brief Remove comments from extracted construct code while preserving source line mapping.
- @details Delegates comment stripping to `compress_source()` to remove inline, single-line, and multi-line comments while preserving string literals. When line numbers are enabled, remaps local compressed line indices back to absolute file line numbers using `line_start`.
- @param code_lines Raw construct code lines sliced by SourceElement line range.
- @param language Normalized language key used by the compression parser.
- @param line_start Absolute start line number of the construct in the original file.
- @param include_line_numbers If True, emit `<n>:` prefixes with absolute source line numbers.
- @return Comment-stripped construct code string.

### fn `def find_constructs_in_files(` (L244-249)
- @brief Format a single matched construct for markdown output with complete code extraction.
- @details Extracts construct code directly from source_lines using element.line_start and element.line_end indices, removes inline/single-line/multi-line comments from the extracted block, and inserts Doxygen metadata before the code fence when available.
- @param element SourceElement instance containing line range indices.
- @param source_lines Complete source file content as list of lines.
- @param include_line_numbers If True, prefix code lines with <n>: format.
- @param language Normalized source language key used for comment stripping.
- @return Formatted markdown block for the construct with complete code from line_start to line_end.

### fn `def main()` (L355-392)
- @brief Find and extract constructs matching tag filter and regex pattern from multiple files.
- @brief Execute the construct finding CLI command.
- @details Analyzes each file with SourceAnalyzer, filters elements by tag and name pattern, formats results as markdown with file headers.
- @details Parses arguments and calls find_constructs_in_files. Handles exceptions by printing errors to stderr.
- @param filepaths List of source file paths.
- @param tag_filter Pipe-separated TAG identifiers (e.g., "CLASS|FUNCTION").
- @param pattern Regex pattern for construct name matching.
- @param include_line_numbers If True (default), prefix code lines with <n>: format.
- @param verbose If True, emits progress status messages on stderr.
- @return Concatenated markdown output string.
- @return {None} Function return value.
- @throws ValueError If no files could be processed or no constructs found.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`LANGUAGE_TAGS`|var|pub|20||
|`format_available_tags`|fn|pub|44-57|def format_available_tags() -> str|
|`parse_tag_filter`|fn|pub|58-66|def parse_tag_filter(tag_string: str) -> set[str]|
|`language_supports_tags`|fn|pub|67-77|def language_supports_tags(lang: str, tag_set: set[str]) ...|
|`construct_matches`|fn|pub|78-95|def construct_matches(element, tag_set: set[str], pattern...|
|`_merge_doxygen_fields`|fn|priv|96-98|def _merge_doxygen_fields(|
|`_extract_construct_doxygen_fields`|fn|priv|113-136|def _extract_construct_doxygen_fields(element) -> dict[st...|
|`_extract_file_level_doxygen_fields`|fn|priv|137-161|def _extract_file_level_doxygen_fields(elements: list) ->...|
|`_strip_construct_comments`|fn|priv|162-166|def _strip_construct_comments(|
|`format_construct`|fn|pub|202-206|def format_construct(|
|`find_constructs_in_files`|fn|pub|244-249|def find_constructs_in_files(|
|`main`|fn|pub|355-392|def main()|


---

# generate_markdown.py | Python | 158L | 5 symbols | 4 imports | 8 comments
> Path: `src/usereq/generate_markdown.py`
- @brief Generate concatenated markdown from arbitrary source files.
- @details Analyzes each input file with source_analyzer and produces a single markdown output concatenating all results. Prints pack summary to stderr.
@author GitHub Copilot
@version 0.0.70

## Imports
```
import os
import sys
from pathlib import Path
from .source_analyzer import SourceAnalyzer, format_markdown
```

## Definitions

- var `EXT_LANG_MAP = {` (L17)
### fn `def detect_language(filepath: str) -> str | None` (L45-54)
- @brief Extension-to-language normalization map for markdown generation."""
- @brief Detect language from file extension.
- @details Uses EXT_LANG_MAP for extension lookup (case-insensitive).
- @param filepath Path to the source file.
- @return Language identifier string or None if unknown.

### fn `def _format_output_path(filepath: str, output_base: Path | None) -> str` `priv` (L55-68)
- @brief Build the markdown-visible path for one source file.
- @details Implements the _format_output_path function behavior with deterministic control flow.
- @param filepath Absolute or relative source file path.
- @param output_base Project-home base used to relativize output paths.
- @return Original filepath when output_base is None; otherwise POSIX relative path from output_base.

### fn `def generate_markdown(` (L69-72)

### fn `def main()` (L138-156)
- @brief Analyze source files and return concatenated markdown.
- @brief Execute the standalone markdown generation CLI command.
- @details Iterates through files, detecting language, analyzing constructs, and formatting output. Disables legacy comment/exit annotation traces in rendered markdown, emitting only construct references plus Doxygen field bullets when available.
- @details Expects file paths as command-line arguments. Prints generated markdown to stdout.
- @param filepaths List of source file paths to analyze.
- @param verbose If True, emits progress status messages on stderr.
- @param output_base Project-home base used to render file paths in markdown as relative paths.
- @return Concatenated markdown string with all file analyses.
- @return {None} Function return value.
- @throws ValueError If no valid source files are found.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|17||
|`detect_language`|fn|pub|45-54|def detect_language(filepath: str) -> str | None|
|`_format_output_path`|fn|priv|55-68|def _format_output_path(filepath: str, output_base: Path ...|
|`generate_markdown`|fn|pub|69-72|def generate_markdown(|
|`main`|fn|pub|138-156|def main()|


---

# source_analyzer.py | Python | 2280L | 62 symbols | 11 imports | 135 comments
> Path: `src/usereq/source_analyzer.py`
- @brief Multi-language source code analyzer.
- @details Inspired by tree-sitter, this module analyzes source files across multiple programming languages, extracting: - Definitions of functions, methods, classes, structs, enums, traits, interfaces, modules, components and other constructs - Comments (single-line and multi-line) in language-specific syntax - A structured listing of the entire file with line number prefixes
@author GitHub Copilot
@version 0.0.70

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
- @brief Element types recognized in source code.
- @details Enumeration of all supported syntactic constructs across languages.
- var `FUNCTION = auto()` (L28)
  - @brief Element types recognized in source code.
  - @details Enumeration of all supported syntactic constructs across languages.
- var `METHOD = auto()` (L29)
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

### class `class SourceElement` `@dataclass` (L56-116)
- @brief Element found in source file.
- @details Data class representing a single extracted code construct with its metadata.
- fn `def type_label(self) -> str` (L82-116)
  - @brief Return the normalized printable label for element_type.
  - @details Maps internal ElementType enum to a string representation for reporting.
  - @return Stable uppercase label used in markdown rendering output.

### class `class LanguageSpec` `@dataclass` (L118-129)
- @brief Language recognition pattern specification.
- @details Holds regex patterns and configuration for parsing a specific programming language.

### fn `def build_language_specs() -> dict` (L130-329)
- @brief Build specifications for all supported languages.
- @details Implements the build_language_specs function behavior with deterministic control flow.
- @return {dict} Function return value.

### class `class SourceAnalyzer` (L686-885)
- @brief Multi-language source file analyzer.
- @details Analyzes a source file identifying definitions, comments and constructs for the specified language. Produces structured output with line numbers, inspired by tree-sitter tags functionality.
- fn `def __init__(self)` `priv` (L691-698)
  - @brief Multi-language source file analyzer.
  - @brief Initialize analyzer state with language specifications.
  - @details Analyzes a source file identifying definitions, comments and constructs for the specified language. Produces structured output with line numbers, inspired by tree-sitter tags functionality.
  - @details Implements the __init__ function behavior with deterministic control flow.
  - @return {None} Function return value.
- fn `def get_supported_languages(self) -> list` (L699-712)
  - @brief Return list of supported languages (without aliases).
  - @details Implements the get_supported_languages function behavior with deterministic control flow.
  - @return Sorted list of unique language identifiers.
- fn `def analyze(self, filepath: str, language: str) -> list` (L713-868)
  - @brief Analyze a source file and return the list of SourceElement found.
  - @details Reads file content, detects single/multi-line comments, and matches regex patterns for definitions.
  - @param filepath Path to the source file.
  - @param language Language identifier.
  - @return List of SourceElement instances.
  - @throws ValueError If language is not supported.

### fn `def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool` `priv` (L869-904)
- @brief Check if position pos is inside a string literal.
- @details Implements the _in_string_context function behavior with deterministic control flow.
- @param line The line of code.
- @param pos The column index.
- @param spec The LanguageSpec instance.
- @return True if pos is within a string.

### fn `def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]` `priv` (L905-944)
- @brief Find position of single-line comment, ignoring strings.
- @details Implements the _find_comment function behavior with deterministic control flow.
- @param line The line of code.
- @param spec The LanguageSpec instance.
- @return Column index of comment start, or None.

### fn `def _find_block_end(self, lines: list, start_idx: int,` `priv` (L945-1023)
- @brief Find the end of a block (function, class, struct, etc.).
- @details Returns the index (1-based) of the final line of the block. Limits search for performance.
- @param lines List of all file lines.
- @param start_idx Index of the start line.
- @param language Language identifier.
- @param first_line Content of the start line.
- @return 1-based index of the end line.

### fn `def enrich(self, elements: list, language: str,` (L1026-1046)
- @brief Enrich elements with signatures, hierarchy, visibility, inheritance.
- @details Call after analyze() to add metadata for LLM-optimized markdown output. Modifies elements in-place and returns them. If filepath is provided, also extracts body comments and exit points.
- @param elements Input parameter `elements`.
- @param language Input parameter `language`.
- @param filepath Input parameter `filepath`.
- @return {list} Function return value.

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L1047-1075)
- @brief Extract clean identifiers from name fields.
- @details Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.
- @param elements Input parameter `elements`.
- @param language Input parameter `language`.
- @return {None} Function return value.

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1076-1096)
- @brief Extract clean signatures from element extracts.
- @details Implements the _extract_signatures function behavior with deterministic control flow.
- @param elements Input parameter `elements`.
- @param language Input parameter `language`.
- @return {None} Function return value.

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1097-1133)
- @brief Detect parent-child relationships between elements.
- @details Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.
- @param elements Input parameter `elements`.
- @return {None} Function return value.

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1134-1151)
- @brief Extract visibility/access modifiers from elements.
- @details Implements the _extract_visibility function behavior with deterministic control flow.
- @param elements Input parameter `elements`.
- @param language Input parameter `language`.
- @return {None} Function return value.

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1152-1203)
- @brief Parse visibility modifier from a signature line.
- @details Implements the _parse_visibility function behavior with deterministic control flow.
- @param sig Input parameter `sig`.
- @param name Input parameter `name`.
- @param language Input parameter `language`.
- @return {Optional[str]} Function return value.

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1204-1220)
- @brief Extract inheritance/implementation info from class-like elements.
- @details Implements the _extract_inheritance function behavior with deterministic control flow.
- @param elements Input parameter `elements`.
- @param language Input parameter `language`.
- @return {None} Function return value.

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1221-1255)
- @brief Parse inheritance info from a class/struct declaration line.
- @details Implements the _parse_inheritance function behavior with deterministic control flow.
- @param first_line Input parameter `first_line`.
- @param language Input parameter `language`.
- @return {Optional[str]} Function return value.

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1263-1391)
- @brief Extract comments and exit points from within function/class bodies.
- @details Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.
- @param elements Input parameter `elements`.
- @param language Input parameter `language`.
- @param filepath Input parameter `filepath`.
- @return {None} Function return value.

### fn `def _extract_doxygen_fields(self, elements: list)` `priv` (L1392-1540)
- @brief Extract Doxygen tag fields from associated documentation comments.
- @details For each non-comment element, resolves the nearest associated documentation comment using language-agnostic adjacency rules: same-line postfix comment (`//!<`, `#!<`, `/**<`), nearest preceding standalone comment block within two lines, or nearest following postfix standalone comment within two lines. When the nearest preceding match is a standalone comment, contiguous preceding standalone comments are merged into one logical block before parsing so multi-line tag sets split across `#`/`//` lines are preserved. Parsed fields are stored in element.doxygen_fields.
- @param elements Input parameter `elements`.
- @return {None} Function return value.

### fn `def _is_file_level_comment(comment) -> bool` `priv` (L1413-1423)
- @brief Extract Doxygen tag fields from associated documentation comments.
- @brief Detect whether a comment block is file-scoped Doxygen metadata.
- @details For each non-comment element, resolves the nearest associated documentation comment using language-agnostic adjacency rules: same-line postfix comment (`//!<`, `#!<`, `/**<`), nearest preceding standalone comment block within two lines, or nearest following postfix standalone comment within two lines. When the nearest preceding match is a standalone comment, contiguous preceding standalone comments are merged into one logical block before parsing so multi-line tag sets split across `#`/`//` lines are preserved. Parsed fields are stored in element.doxygen_fields.
- @details Resolves canonical text from `comment_source` or fallback `extract` and checks for a standalone `@file` or `\\file` tag token; empty comment payloads are treated as non file-level.
- @param elements Input parameter `elements`.
- @param comment {SourceElement} Candidate comment element.
- @return {None} Function return value.
- @return {bool} True when the comment declares file-level metadata and must not be bound to a symbol.

### fn `def _has_blocking_element(comment) -> bool` `priv` (L1447-1468)
- @brief Validate that no non-comment construct exists between comment and target symbol.
- @details Evaluates direct-span and overlap-span blockers in `non_comment_elements`; returns True when any unrelated construct occupies the interval between `comment.line_end` and `elem.line_start`.
- @param comment {SourceElement} Candidate preceding comment element.
- @return {bool} True when association must be rejected due to an intervening non-comment element.

### fn `def _is_postfix_doxygen_comment(comment_text: str) -> bool` `priv` `@staticmethod` (L1542-1551)
- @brief Detect whether a comment uses postfix Doxygen association markers.
- @details Returns True for comment prefixes that explicitly bind documentation to a preceding construct, including variants like `#!<`, `//!<`, `///<`, `/*!<`, and `/**<`.
- @param comment_text Raw extracted comment text.
- @return True when the comment text starts with a supported postfix marker; otherwise False.

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1553-1569)
- @brief Strip comment markers from a single line of comment text.
- @details Implements the _clean_comment_line function behavior with deterministic control flow.
- @param text Input parameter `text`.
- @param spec Input parameter `spec`.
- @return {str} Function return value.

### fn `def _md_loc(elem) -> str` `priv` (L1570-1581)
- @brief Format element location compactly for markdown.
- @details Implements the _md_loc function behavior with deterministic control flow.
- @param elem Input parameter `elem`.
- @return {str} Function return value.

### fn `def _md_kind(elem) -> str` `priv` (L1582-1613)
- @brief Short kind label for markdown output.
- @details Implements the _md_kind function behavior with deterministic control flow.
- @param elem Input parameter `elem`.
- @return {str} Function return value.

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1614-1640)
- @brief Extract clean text content from a comment element.
- @details Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.
- @param comment_elem Input parameter `comment_elem`.
- @param max_length Input parameter `max_length`.
- @return {str} Function return value.

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1641-1661)
- @brief Extract clean text lines from a multi-line comment (preserving structure).
- @details Implements the _extract_comment_lines function behavior with deterministic control flow.
- @param comment_elem Input parameter `comment_elem`.
- @return {list} Function return value.

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1662-1725)
- @brief Build maps that associate comments with their adjacent definitions.
- @details Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)
- @param elements Input parameter `elements`.
- @return {tuple} Function return value.

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1726-1783)
- @brief Render body comments and exit points for a definition element.
- @details Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.
- @param out Input parameter `out`.
- @param elem Input parameter `elem`.
- @param indent Input parameter `indent`.
- @param exclude_ranges Input parameter `exclude_ranges`.
- @return {None} Function return value.

### fn `def _merge_doxygen_fields(` `priv` (L1784-1786)

### fn `def _collect_element_doxygen_fields(elem) -> dict[str, list[str]]` `priv` (L1802-1825)
- @brief Merge Doxygen field dictionaries preserving per-tag value order.
- @brief Aggregate construct Doxygen fields from associated and body comments.
- @details Implements the _merge_doxygen_fields function behavior with deterministic control flow.
- @details Uses canonical `elem.doxygen_fields` from `SourceAnalyzer.enrich()` and merges only body comments located at construct start (first 3 lines) to retain docstring-style Doxygen blocks while avoiding internal-body duplication.
- @param base_fields Destination dictionary mutated in place.
- @param extra_fields Source dictionary containing additional tag values.
- @param elem SourceElement containing optional `doxygen_fields` and `body_comments`.
- @return Updated destination dictionary.
- @return Dictionary of normalized Doxygen tags to ordered value lists.

### fn `def _collect_file_level_doxygen_fields(elements: list) -> dict[str, list[str]]` `priv` (L1826-1850)
- @brief Extract file-level Doxygen fields from the first `@file` documentation block.
- @details Scans non-inline comment elements in source order and selects the first comment containing `@file` or `\\file`, then parses the full comment text through `parse_doxygen_comment()`.
- @param elements Parsed SourceElement list for one source file.
- @return Parsed Doxygen fields from the file-level documentation block; empty dictionary if not found.

### fn `def format_markdown(` (L1851-1857)

### fn `def main()` (L2151-2278)
- @brief Execute the standalone source analyzer CLI command.
- @details Implements the main function behavior with deterministic control flow.
- @return {None} Function return value.

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
|`SourceElement`|class|pub|56-116|class SourceElement|
|`SourceElement.type_label`|fn|pub|82-116|def type_label(self) -> str|
|`LanguageSpec`|class|pub|118-129|class LanguageSpec|
|`build_language_specs`|fn|pub|130-329|def build_language_specs() -> dict|
|`SourceAnalyzer`|class|pub|686-885|class SourceAnalyzer|
|`SourceAnalyzer.__init__`|fn|priv|691-698|def __init__(self)|
|`SourceAnalyzer.get_supported_languages`|fn|pub|699-712|def get_supported_languages(self) -> list|
|`SourceAnalyzer.analyze`|fn|pub|713-868|def analyze(self, filepath: str, language: str) -> list|
|`_in_string_context`|fn|priv|869-904|def _in_string_context(self, line: str, pos: int, spec: L...|
|`_find_comment`|fn|priv|905-944|def _find_comment(self, line: str, spec: LanguageSpec) ->...|
|`_find_block_end`|fn|priv|945-1023|def _find_block_end(self, lines: list, start_idx: int,|
|`enrich`|fn|pub|1026-1046|def enrich(self, elements: list, language: str,|
|`_clean_names`|fn|priv|1047-1075|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1076-1096|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1097-1133|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1134-1151|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1152-1203|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1204-1220|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1221-1255|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1263-1391|def _extract_body_annotations(self, elements: list,|
|`_extract_doxygen_fields`|fn|priv|1392-1540|def _extract_doxygen_fields(self, elements: list)|
|`_is_file_level_comment`|fn|priv|1413-1423|def _is_file_level_comment(comment) -> bool|
|`_has_blocking_element`|fn|priv|1447-1468|def _has_blocking_element(comment) -> bool|
|`_is_postfix_doxygen_comment`|fn|priv|1542-1551|def _is_postfix_doxygen_comment(comment_text: str) -> bool|
|`_clean_comment_line`|fn|priv|1553-1569|def _clean_comment_line(text: str, spec) -> str|
|`_md_loc`|fn|priv|1570-1581|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1582-1613|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1614-1640|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1641-1661|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1662-1725|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1726-1783|def _render_body_annotations(out: list, elem, indent: str...|
|`_merge_doxygen_fields`|fn|priv|1784-1786|def _merge_doxygen_fields(|
|`_collect_element_doxygen_fields`|fn|priv|1802-1825|def _collect_element_doxygen_fields(elem) -> dict[str, li...|
|`_collect_file_level_doxygen_fields`|fn|priv|1826-1850|def _collect_file_level_doxygen_fields(elements: list) ->...|
|`format_markdown`|fn|pub|1851-1857|def format_markdown(|
|`main`|fn|pub|2151-2278|def main()|


---

# static_check.py | Python | 668L | 20 symbols | 8 imports | 58 comments
> Path: `src/usereq/static_check.py`
- @brief Static code analysis dispatch module implementing Dummy/Pylance/Ruff/Command check classes.
- @details Provides a class hierarchy for running static analysis tools against resolved file lists.
Exposes `run_static_check(argv)` as the primary entry point for `--test-static-check` called
from cli.py. Also exposes `parse_enable_static_check`, `dispatch_static_check_for_file`,
`STATIC_CHECK_LANG_CANONICAL`, and `STATIC_CHECK_EXT_TO_LANG` for `--enable-static-check`,
`--files-static-check`, and `--static-check` command support.
Class hierarchy: StaticCheckBase (Dummy) -> StaticCheckPylance, StaticCheckRuff, StaticCheckCommand.
File resolution supports: explicit file paths, glob patterns (with full `**` recursive expansion),
and direct-children-only directory traversal. No custom `--recursive` flag; recursive traversal
is expressed via `**` glob syntax (e.g., `src/**/*.py`).
@author useReq
@version 0.0.72

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

### fn `def _split_csv_like_tokens(spec_rhs: str) -> list[str]` `priv` (L112-146)
- @brief Split a comma-separated SPEC right-hand side with quote-aware token boundaries.
- @details - Supported quote delimiters: single quote `'` and double quote `"`. - Commas split tokens only when parser is outside a quoted segment. - Quote delimiters are not included in output tokens. - Leading and trailing whitespace for each token is stripped.
- @param spec_rhs Text after `LANG=` in `--enable-static-check`.
- @return Token list where commas inside `'...'` or `"..."` do not split tokens.
- @see SRS-260, SRS-250

### fn `def parse_enable_static_check(spec: str) -> tuple[str, dict]` (L147-223)
- @brief Parse a single `--enable-static-check` SPEC string into a (lang, config_dict) pair.
- @details Parse steps: 1. Split on the first `=`; left side is LANG token, right side is `MODULE[,...]`. 2. Normalize LANG via `STATIC_CHECK_LANG_CANONICAL` (case-insensitive). 3. Parse right side as comma-separated tokens; first token is MODULE (case-insensitive, validated against `_CANONICAL_MODULES`). 4. For Command: next token is `cmd` (mandatory); all subsequent tokens are `params`. 5. For all other modules: all tokens after MODULE are `params`. 6. `params` key is omitted when the list is empty. 7. `cmd` key is omitted for non-Command modules. 8. Surrounding quote delimiters (`'` or `"`) are stripped from parsed tokens. Note: PARAM values containing `,` must be wrapped with `'` or `"` in SPEC.
- @param spec Raw SPEC string in the format `LANG=MODULE[,CMD[,PARAM...]]`.
- @return Tuple `(canonical_lang, config_dict)` where `config_dict` contains `"module"` and optionally `"cmd"` (Command only) and `"params"` (non-empty list only).
- @throws ReqError If `=` separator is absent, language is unknown, or module is unknown.
- @see SRS-260, SRS-248, SRS-249, SRS-250

### fn `def dispatch_static_check_for_file(filepath: str, lang_config: dict) -> int` (L228-273)
- @brief Dispatch static-check for a single file based on a language config dict.
- @details Module dispatch table: - `"Dummy"` (case-insensitive) -> `StaticCheckBase` - `"Pylance"` -> `StaticCheckPylance` - `"Ruff"` -> `StaticCheckRuff` - `"Command"` -> `StaticCheckCommand` (requires `"cmd"` key) Instantiates the checker with `inputs=[filepath]` and `extra_args=params`. Delegates actual check to `checker.run()`.
- @param filepath Absolute path of the file to analyse.
- @param lang_config Dict with keys `"module"` (str), optional `"cmd"` (str, Command only), optional `"params"` (list[str]).
- @return Exit code: 0 on pass, 1 on fail.
- @throws ReqError If module is unknown, or Command module is missing `"cmd"`.
- @see SRS-261, SRS-253, SRS-256

### fn `def _resolve_files(inputs: Sequence[str]) -> List[str]` `priv` (L278-320)
- @brief Resolve a mixed list of paths, glob patterns, and directories into regular files.
- @details Resolution order per element: 1. If the element contains a glob wildcard character (`*`, `?`, `[`) expand via `glob.glob(entry, recursive=True)`, enabling full `**` recursive expansion (e.g., `src/**/*.py` matches all `.py` files under `src/` at any depth). 2. If the element is an existing directory, iterate direct children only (flat traversal). 3. Otherwise treat as a literal file path; include if it is a regular file. Symlinks to regular files are included. Non-existent paths that do not match a glob produce a warning on stderr and are skipped.
- @param inputs Sequence of raw path strings (file, directory, or glob pattern).
- @return Sorted deduplicated list of resolved absolute file paths (regular files only).

### class `class StaticCheckBase` (L325-417)
- @brief Dummy static-check class; base of the static analysis class hierarchy.
- @details Iterates over resolved input files and emits a per-file header line plus `Result: OK`. Subclasses override `_check_file` to provide tool-specific logic. File resolution is delegated to `_resolve_files`.
- fn `def __init__(` `priv` (L336-339)
  - @brief Dummy static-check class; base of the static analysis class hierarchy.
  - @details Iterates over resolved input files and emits a per-file header line plus `Result: OK`.
Subclasses override `_check_file` to provide tool-specific logic.
File resolution is delegated to `_resolve_files`.
- fn `def run(self) -> int` (L357-380)
  - @brief Execute the static check for all resolved files.
  - @details If the resolved file list is empty a warning is printed to stderr and 0 is returned. For each file `_check_file` is called; the overall return code is the maximum of all per-file return codes (0 = all OK, 1 = at least one FAIL).
  - @return Exit code: 0 if all files pass (or file list is empty), 1 if any file fails.
- fn `def _header_line(self, filepath: str) -> str` `priv` (L385-395)
  - @brief Build the per-file header line for output.
  - @details Format: `# Static-Check(<LABEL>): <filepath> [<extra_args>]`. When `extra_args` is empty the bracket section is omitted.
  - @param filepath Absolute path of the file being checked.
  - @return Formatted header string including label, filename, and extra args.
- fn `def _check_file(self, filepath: str) -> int` `priv` (L396-407)
  - @brief Perform the static analysis for a single file.
  - @details Base implementation (Dummy): always prints the header and `Result: OK`. Subclasses override this method to invoke external tools.
  - @param filepath Absolute path of the file to check.
  - @return 0 on pass, non-zero on failure.
- fn `def _emit_line(self, line: str) -> None` `priv` (L408-417)
  - @brief Emit one markdown output line.
  - @details Emits `line` followed by a newline.
  - @param line Line content to emit on stdout.
  - @return {None} Function return value.

### class `class StaticCheckPylance(StaticCheckBase)` : StaticCheckBase (L422-470)
- @brief Pylance static-check class; runs pyright on each resolved file.
- @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke `pyright` as a subprocess and parse its exit code. Header label: `Pylance`. Evidence block is emitted on failure by concatenating stdout and stderr from pyright.
- @see StaticCheckBase
- var `LABEL = "Pylance"` (L432)
  - @brief Pylance static-check class; runs pyright on each resolved file.
  - @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke `pyright`
as a subprocess and parse its exit code.
Header label: `Pylance`.
Evidence block is emitted on failure by concatenating stdout and stderr from pyright.
  - @see StaticCheckBase
- fn `def _check_file(self, filepath: str) -> int` `priv` (L434-470)
  - @brief Run pyright on `filepath` and emit OK or FAIL with evidence.
  - @details Invokes `pyright <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
  - @param filepath Absolute path of the file to analyse with pyright.
  - @return 0 when pyright exits 0, 1 otherwise.
  - @exception ReqError Not raised; subprocess errors are surfaced as FAIL evidence.

### class `class StaticCheckRuff(StaticCheckBase)` : StaticCheckBase (L475-523)
- @brief Ruff static-check class; runs `ruff check` on each resolved file.
- @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke `ruff check` as a subprocess and parse its exit code. Header label: `Ruff`. Evidence block is emitted on failure by concatenating stdout and stderr from ruff.
- @see StaticCheckBase
- var `LABEL = "Ruff"` (L485)
  - @brief Ruff static-check class; runs `ruff check` on each resolved file.
  - @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke `ruff check`
as a subprocess and parse its exit code.
Header label: `Ruff`.
Evidence block is emitted on failure by concatenating stdout and stderr from ruff.
  - @see StaticCheckBase
- fn `def _check_file(self, filepath: str) -> int` `priv` (L487-523)
  - @brief Run `ruff check` on `filepath` and emit OK or FAIL with evidence.
  - @details Invokes `ruff check <filepath> [extra_args...]`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
  - @param filepath Absolute path of the file to analyse with ruff.
  - @return 0 when ruff exits 0, 1 otherwise.
  - @exception ReqError Not raised; subprocess errors are surfaced as FAIL evidence.

### class `class StaticCheckCommand(StaticCheckBase)` : StaticCheckBase (L528-599)
- @brief Command static-check class; runs an arbitrary external command on each resolved file.
- @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke the user-supplied `cmd` as a subprocess. Header label: `Command[<cmd>]`. Before processing files the constructor verifies that `cmd` is available on PATH via `shutil.which`; raises `ReqError(code=1)` if the command is not found.
- @see StaticCheckBase
- fn `def __init__(` `priv` (L539-543)
  - @brief Command static-check class; runs an arbitrary external command on each resolved file.
  - @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke the user-supplied
`cmd` as a subprocess.
Header label: `Command[<cmd>]`.
Before processing files the constructor verifies that `cmd` is available on PATH via
`shutil.which`; raises `ReqError(code=1)` if the command is not found.
  - @see StaticCheckBase
- fn `def _check_file(self, filepath: str) -> int` `priv` (L563-599)
  - @brief Initialize the command checker and verify tool availability.
  - @brief Run the external command on `filepath` and emit OK or FAIL with evidence.
  - @details Calls `shutil.which(cmd)` before delegating to the parent constructor.
Sets `LABEL` dynamically to `Command[<cmd>]`.
  - @details Invokes `<cmd> [extra_args...] <filepath>`. Captures combined stdout+stderr. On exit code 0 prints `Result: OK`. On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
  - @param cmd External command name (must be available on PATH).
  - @param inputs Raw path/pattern/directory entries from CLI.
  - @param extra_args Additional CLI arguments forwarded to the external command.
  - @param filepath Absolute path of the file to analyse.
  - @return {None} Function return value.
  - @return 0 when the command exits 0, 1 otherwise.
  - @throws ReqError If `cmd` is not found on PATH (exit code 1).
  - @satisfies SRS-244, SRS-253, SRS-256

### fn `def run_static_check(argv: Sequence[str]) -> int` (L604-668)
- @brief Parse `--test-static-check` sub-argv and dispatch to the appropriate checker class.
- @details Expected argument format: - `dummy [FILES...]` - `pylance [FILES...]` - `ruff [FILES...]` - `command <cmd> [FILES...]` No custom `--recursive` flag is parsed; recursive traversal is expressed via `**` glob patterns in `[FILES]` (e.g., `src/**/*.py`). For `command`, the first token after `command` is treated as `<cmd>`. All remaining tokens (after subcommand and optional cmd) are treated as FILES. Dispatches to: - `dummy` -> `StaticCheckBase` - `pylance` -> `StaticCheckPylance` - `ruff` -> `StaticCheckRuff` - `command` -> `StaticCheckCommand`
- @param argv Remaining argument tokens after `--test-static-check` (i.e. [subcommand, ...]).
- @return Process exit code from the selected checker's `run()` method.
- @throws ReqError If subcommand is missing, unknown, or `command` subcommand is missing `cmd`.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_split_csv_like_tokens`|fn|priv|112-146|def _split_csv_like_tokens(spec_rhs: str) -> list[str]|
|`parse_enable_static_check`|fn|pub|147-223|def parse_enable_static_check(spec: str) -> tuple[str, dict]|
|`dispatch_static_check_for_file`|fn|pub|228-273|def dispatch_static_check_for_file(filepath: str, lang_co...|
|`_resolve_files`|fn|priv|278-320|def _resolve_files(inputs: Sequence[str]) -> List[str]|
|`StaticCheckBase`|class|pub|325-417|class StaticCheckBase|
|`StaticCheckBase.__init__`|fn|priv|336-339|def __init__(|
|`StaticCheckBase.run`|fn|pub|357-380|def run(self) -> int|
|`StaticCheckBase._header_line`|fn|priv|385-395|def _header_line(self, filepath: str) -> str|
|`StaticCheckBase._check_file`|fn|priv|396-407|def _check_file(self, filepath: str) -> int|
|`StaticCheckBase._emit_line`|fn|priv|408-417|def _emit_line(self, line: str) -> None|
|`StaticCheckPylance`|class|pub|422-470|class StaticCheckPylance(StaticCheckBase)|
|`StaticCheckPylance.LABEL`|var|pub|432||
|`StaticCheckPylance._check_file`|fn|priv|434-470|def _check_file(self, filepath: str) -> int|
|`StaticCheckRuff`|class|pub|475-523|class StaticCheckRuff(StaticCheckBase)|
|`StaticCheckRuff.LABEL`|var|pub|485||
|`StaticCheckRuff._check_file`|fn|priv|487-523|def _check_file(self, filepath: str) -> int|
|`StaticCheckCommand`|class|pub|528-599|class StaticCheckCommand(StaticCheckBase)|
|`StaticCheckCommand.__init__`|fn|priv|539-543|def __init__(|
|`StaticCheckCommand._check_file`|fn|priv|563-599|def _check_file(self, filepath: str) -> int|
|`run_static_check`|fn|pub|604-668|def run_static_check(argv: Sequence[str]) -> int|


---

# token_counter.py | Python | 123L | 7 symbols | 2 imports | 8 comments
> Path: `src/usereq/token_counter.py`
- @brief Token and character counting for generated output.
- @details Uses tiktoken for accurate token counting compatible with OpenAI/Claude models.
@author GitHub Copilot
@version 0.0.70

## Imports
```
import os
import tiktoken  # pyright: ignore[reportMissingImports]
```

## Definitions

### class `class TokenCounter` (L14-49)
- @brief Count tokens using tiktoken encoding (cl100k_base by default).
- @details Wrapper around tiktoken encoding to simplify token counting operations.
- fn `def __init__(self, encoding_name: str = "cl100k_base")` `priv` (L19-27)
  - @brief Count tokens using tiktoken encoding (cl100k_base by default).
  - @brief Initialize token counter with a specific tiktoken encoding.
  - @details Wrapper around tiktoken encoding to simplify token counting operations.
  - @details Implements the __init__ function behavior with deterministic control flow.
  - @param encoding_name Name of tiktoken encoding used for tokenization.
  - @return {None} Function return value.
- fn `def count_tokens(self, content: str) -> int` (L28-38)
  - @brief Count tokens in content string.
  - @details Uses `disallowed_special=()` to allow special tokens in input without raising errors. Returns 0 on failure.
  - @param content The text content to tokenize.
  - @return Integer count of tokens.
- fn `def count_chars(content: str) -> int` (L40-49)
  - @brief Count characters in content string.
  - @details Implements the count_chars function behavior with deterministic control flow.
  - @param content The text string.
  - @return Integer count of characters.

### fn `def count_file_metrics(content: str,` (L50-65)
- @brief Count tokens and chars for a content string.
- @details Implements the count_file_metrics function behavior with deterministic control flow.
- @param content The text content to measure.
- @param encoding_name The tiktoken encoding name (default: "cl100k_base").
- @return Dictionary with keys 'tokens' (int) and 'chars' (int).

### fn `def count_files_metrics(file_paths: list,` (L66-94)
- @brief Count tokens and chars for a list of files.
- @details Iterates through files, reading content and counting metrics. Gracefully handles read errors.
- @param file_paths List of file paths to process.
- @param encoding_name The tiktoken encoding name.
- @return List of dictionaries, each containing 'file', 'tokens', 'chars', and optionally 'error'.

### fn `def format_pack_summary(results: list) -> str` (L95-123)
- @brief Format a pack summary string from a list of file metrics.
- @details Generates a human-readable report including icons, per-file stats, and aggregate totals.
- @param results List of metrics dictionaries from count_files_metrics().
- @return Formatted summary string with per-file details and totals.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`TokenCounter`|class|pub|14-49|class TokenCounter|
|`TokenCounter.__init__`|fn|priv|19-27|def __init__(self, encoding_name: str = "cl100k_base")|
|`TokenCounter.count_tokens`|fn|pub|28-38|def count_tokens(self, content: str) -> int|
|`TokenCounter.count_chars`|fn|pub|40-49|def count_chars(content: str) -> int|
|`count_file_metrics`|fn|pub|50-65|def count_file_metrics(content: str,|
|`count_files_metrics`|fn|pub|66-94|def count_files_metrics(file_paths: list,|
|`format_pack_summary`|fn|pub|95-123|def format_pack_summary(results: list) -> str|

