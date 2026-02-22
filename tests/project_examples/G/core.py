#!/usr/bin/env python3
## @file core.py
# @brief Core command dispatch and git-alias runtime orchestration.
# @details Provides command routing, repository diagnostics, changelog/version workflows, and process wrappers.

import argparse
import importlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

pathspec = importlib.import_module("pathspec")

## @brief Constant `CONFIG_FILENAME` used by CLI runtime paths and policies.

CONFIG_FILENAME = ".g.conf"

## @brief Constant `GITHUB_LATEST_RELEASE_API` used by CLI runtime paths and policies.

GITHUB_LATEST_RELEASE_API = "https://api.github.com/repos/Ogekuri/G/releases/latest"

## @brief Constant `VERSION_CHECK_CACHE_FILE` used by CLI runtime paths and policies.
VERSION_CHECK_CACHE_FILE = Path(tempfile.gettempdir()) / ".g_version_check_cache.json"
## @brief Constant `VERSION_CHECK_TTL_HOURS` used by CLI runtime paths and policies.

VERSION_CHECK_TTL_HOURS = 6

## @brief Constant `DEFAULT_VER_RULES` used by CLI runtime paths and policies.

DEFAULT_VER_RULES = [
    ("README.md", r'\s*"(\d+\.\d+\.\d+)"\s*'),
    ("src/**/*.py", r'__version__\s*=\s*["\']?(\d+\.\d+\.\d+)["\']?'),
    ("pyproject.toml", r'\bversion\s*=\s*"(\d+\.\d+\.\d+)"'),
]
## @brief Constant `VERSION_CLEANUP_REGEXES` used by CLI runtime paths and policies.

VERSION_CLEANUP_REGEXES = [
    r"(^|/)\.git(/|$)",
    r"(^|/)\.vscode(/|$)",
    r"(^|/)tmp(/|$)",
    r"(^|/)temp(/|$)",
    r"(^|/)\.cache(/|$)",
    r"(^|/)\.pytest_cache(/|$)",
    r"(^|/)node_modules/\.cache(/|$)",
]
## @brief Constant `VERSION_CLEANUP_PATTERNS` used by CLI runtime paths and policies.

VERSION_CLEANUP_PATTERNS = [re.compile(pattern) for pattern in VERSION_CLEANUP_REGEXES]

## @brief Constant `DEFAULT_CONFIG` used by CLI runtime paths and policies.

DEFAULT_CONFIG = {
    "master": "master",
    "develop": "develop",
    "work": "work",
    "editor": "edit",
    "default_module": "core",
    "ver_rules": [
        {"pattern": "README.md", "regex": r'\s*\((\d+\.\d+\.\d+)\)\n'},
        {"pattern": "src/**/*.py", "regex": r'__version__\s*=\s*["\']?(\d+\.\d+\.\d+)["\']?'},
        {"pattern": "pyproject.toml", "regex": r'\bversion\s*=\s*"(\d+\.\d+\.\d+)"'},
    ],
}

## @brief Constant `CONFIG` used by CLI runtime paths and policies.

CONFIG = DEFAULT_CONFIG.copy()
## @brief Constant `BRANCH_KEYS` used by CLI runtime paths and policies.

BRANCH_KEYS = ("master", "develop", "work")
## @brief Constant `MANAGEMENT_HELP` used by CLI runtime paths and policies.

MANAGEMENT_HELP = [
    ("--write-config", "Generate the .g.conf file in the repository root with default values."),
    ("--upgrade", "Reinstall git-alias via uv tool install."),
    ("--remove", "Uninstall git-alias using uv tool uninstall."),
    ("--ver", "Print the CLI version."),
    ("--version", "Print the CLI version."),
    ("--help", "Print the full help screen or the help text of a specific alias."),
]


## @brief Execute `get_config_value` runtime logic for Git-Alias CLI.
# @details Executes `get_config_value` using deterministic CLI control-flow and explicit error propagation.
# @param name Input parameter consumed by `get_config_value`.
# @return Result emitted by `get_config_value` according to command contract.
def get_config_value(name):
    return CONFIG.get(name, DEFAULT_CONFIG[name])


## @brief Execute `get_branch` runtime logic for Git-Alias CLI.
# @details Executes `get_branch` using deterministic CLI control-flow and explicit error propagation.
# @param name Input parameter consumed by `get_branch`.
# @return Result emitted by `get_branch` according to command contract.
def get_branch(name):
    if name not in BRANCH_KEYS:
        raise KeyError(f"Unknown branch key {name}")
    return get_config_value(name)


## @brief Execute `get_editor` runtime logic for Git-Alias CLI.
# @details Executes `get_editor` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `get_editor` according to command contract.
def get_editor():
    return get_config_value("editor")


## @brief Execute `_load_config_rules` runtime logic for Git-Alias CLI.
# @details Executes `_load_config_rules` using deterministic CLI control-flow and explicit error propagation.
# @param key Input parameter consumed by `_load_config_rules`.
# @param fallback Input parameter consumed by `_load_config_rules`.
# @return Result emitted by `_load_config_rules` according to command contract.
def _load_config_rules(key, fallback):
    raw_value = CONFIG.get(key, DEFAULT_CONFIG[key])
    if not isinstance(raw_value, list):
        print(f"Ignoring non-list value for {key}", file=sys.stderr)
        return list(fallback)
    rules = []
    for entry in raw_value:
        pattern = regex = None
        if isinstance(entry, dict):
            pattern = entry.get("pattern") or entry.get("glob")
            regex = entry.get("regex")
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            pattern, regex = entry[0], entry[1]
        if isinstance(pattern, str):
            pattern = pattern.strip()
        else:
            pattern = None
        if isinstance(regex, str):
            regex = regex.strip()
        else:
            regex = None
        if pattern and regex:
            rules.append((pattern, regex))
    return rules if rules else list(fallback)


## @brief Execute `get_version_rules` runtime logic for Git-Alias CLI.
# @details Executes `get_version_rules` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `get_version_rules` according to command contract.
def get_version_rules():
    return _load_config_rules("ver_rules", DEFAULT_VER_RULES)


## @brief Execute `get_cli_version` runtime logic for Git-Alias CLI.
# @details Executes `get_cli_version` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `get_cli_version` according to command contract.
def get_cli_version():
    init_path = Path(__file__).resolve().with_name("__init__.py")
    try:
        content = init_path.read_text(encoding="utf-8")
    except OSError:
        return "unknown"
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    return "unknown"


## @brief Execute `_normalize_semver_text` runtime logic for Git-Alias CLI.
# @details Executes `_normalize_semver_text` using deterministic CLI control-flow and explicit error propagation.
# @param text Input parameter consumed by `_normalize_semver_text`.
# @return Result emitted by `_normalize_semver_text` according to command contract.
def _normalize_semver_text(text: str) -> str:
    value = (text or "").strip()
    if value.lower().startswith("v"):
        value = value[1:]
    return value


## @brief Execute `check_for_newer_version` runtime logic for Git-Alias CLI.
# @details Executes `check_for_newer_version` using deterministic CLI control-flow and explicit error propagation.
# @param timeout_seconds Input parameter consumed by `check_for_newer_version`.
# @return Result emitted by `check_for_newer_version` according to command contract.
def check_for_newer_version(timeout_seconds: float = 1.0) -> None:
    current = _parse_semver_tuple(get_cli_version())
    if current is None:
        return
    
    # @details Reuse non-expired cache payload before any online request.
    cache_valid = False
    if VERSION_CHECK_CACHE_FILE.exists():
        try:
            with open(VERSION_CHECK_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            expires_str = cache_data.get('expires', '')
            if expires_str:
                expires = datetime.fromisoformat(expires_str)
                if datetime.now() < expires:
                    # @details Emit upgrade warning when cached latest version is newer.
                    cached_latest = cache_data.get('latest_version', '')
                    latest = _parse_semver_tuple(cached_latest)
                    if latest and latest > current:
                        current_text = "{}.{}.{}".format(*current)
                        print(
                            f"New version available (current: {current_text}, latest: {cached_latest}). "
                            f"Upgrade with: g --upgrade",
                            file=sys.stderr,
                        )
                    cache_valid = True
        except Exception:
            # @details Ignore cache read failures because version checks are non-blocking.
            pass
    
    if cache_valid:
        # @details Skip network request when cache entry is valid.
        return
    
    # @details Execute online release lookup when cache is absent or expired.
    request = Request(
        GITHUB_LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "git-alias",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload_bytes = response.read()
    except Exception:
        return
    try:
        payload_text = payload_bytes.decode("utf-8") if isinstance(payload_bytes, (bytes, bytearray)) else str(payload_bytes)
        data = json.loads(payload_text)
    except Exception:
        return
    if not isinstance(data, dict):
        return
    tag = data.get("tag_name") or ""
    latest_text = _normalize_semver_text(str(tag))
    latest = _parse_semver_tuple(latest_text)
    if latest is None:
        return
    
    # @details Persist fresh release-check payload with TTL metadata.
    try:
        cache_data = {
            "last_check": datetime.now().isoformat(),
            "current_version": "{}.{}.{}".format(*current),
            "latest_version": latest_text,
            "expires": (datetime.now() + timedelta(hours=VERSION_CHECK_TTL_HOURS)).isoformat()
        }
        with open(VERSION_CHECK_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception:
        # @details Ignore cache write failures because command execution must continue.
        pass
    
    # @details Emit upgrade hint when fetched latest version is newer than current.
    if latest > current:
        current_text = "{}.{}.{}".format(*current)
        print(
            f"New version available (current: {current_text}, latest: {latest_text}). "
            f"Upgrade with: g --upgrade",
            file=sys.stderr,
        )


## @brief Execute `get_git_root` runtime logic for Git-Alias CLI.
# @details Executes `get_git_root` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `get_git_root` according to command contract.
def get_git_root():
    try:
        result = _run_checked(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        location = result.stdout.strip()
        if location:
            return Path(location)
    except CommandExecutionError:
        pass
    return Path.cwd()


## @brief Execute `get_config_path` runtime logic for Git-Alias CLI.
# @details Executes `get_config_path` using deterministic CLI control-flow and explicit error propagation.
# @param root Input parameter consumed by `get_config_path`.
# @return Result emitted by `get_config_path` according to command contract.
def get_config_path(root=None):
    base = Path(root) if root is not None else get_git_root()
    return base / CONFIG_FILENAME


## @brief Execute `load_cli_config` runtime logic for Git-Alias CLI.
# @details Executes `load_cli_config` using deterministic CLI control-flow and explicit error propagation.
# @param root Input parameter consumed by `load_cli_config`.
# @return Result emitted by `load_cli_config` according to command contract.
def load_cli_config(root=None):
    CONFIG.update(DEFAULT_CONFIG)
    config_path = get_config_path(root)
    if not config_path.exists():
        return config_path
    try:
        raw_text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Unable to read {config_path}: {exc}", file=sys.stderr)
        return config_path
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        print(f"Unable to parse {config_path} as JSON: {exc}", file=sys.stderr)
        return config_path
    if not isinstance(data, dict):
        print(f"Ignoring {config_path}: expected a JSON object.", file=sys.stderr)
        return config_path
    for key in DEFAULT_CONFIG:
        if key not in data:
            continue
        value = data[key]
        if key == "ver_rules":
            if isinstance(value, list):
                CONFIG[key] = value
            else:
                print(f"Ignoring {key}: expected a JSON array.", file=sys.stderr)
            continue
        if isinstance(value, str) and value.strip():
            CONFIG[key] = value
        else:
            print(f"Ignoring {key}: expected a non-empty string.", file=sys.stderr)
    return config_path


## @brief Execute `write_default_config` runtime logic for Git-Alias CLI.
# @details Executes `write_default_config` using deterministic CLI control-flow and explicit error propagation.
# @param root Input parameter consumed by `write_default_config`.
# @return Result emitted by `write_default_config` according to command contract.
def write_default_config(root=None):
    config_path = get_config_path(root)
    payload = json.dumps(DEFAULT_CONFIG, indent=2)
    config_path.write_text(payload + "\n", encoding="utf-8")
    print(f"Configuration written to {config_path}")
    return config_path


## @brief Execute `_editor_base_command` runtime logic for Git-Alias CLI.
# @details Executes `_editor_base_command` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_editor_base_command` according to command contract.
def _editor_base_command():
    raw_value = get_editor() or DEFAULT_CONFIG["editor"]
    try:
        parts = shlex.split(raw_value)
    except ValueError as exc:
        print(
            f"Ignoring invalid editor command '{raw_value}': {exc}. Falling back to '{DEFAULT_CONFIG['editor']}'",
            file=sys.stderr,
        )
        parts = [DEFAULT_CONFIG["editor"]]
    if not parts:
        parts = [DEFAULT_CONFIG["editor"]]
    return parts


## @brief Execute `run_editor_command` runtime logic for Git-Alias CLI.
# @details Executes `run_editor_command` using deterministic CLI control-flow and explicit error propagation.
# @param args Input parameter consumed by `run_editor_command`.
# @return Result emitted by `run_editor_command` according to command contract.
def run_editor_command(args):
    return run_command(_editor_base_command() + list(args))

## @brief Constant `HELP_TEXTS` used by CLI runtime paths and policies.

HELP_TEXTS = {
    "aa": "Add all file changes/added to stage area for commit.",
    "ar": "Archive the configured master branch as zip file. Use tag as filename.",
    "bd": "Delete a local branch: git bd '<branch>'.",
    "br": "Create a new branch.",
    "backup": "Merge configured work into develop and push develop to origin (shared release preflight checks).",
    "chver": "Change the project version to the provided semantic version.",
    "changelog": "Generate CHANGELOG.md grouped by minor releases. Options: --include-patch, --force-write, --print-only, --disable-history.",
    "ck": "Check differences.",
    "cm": "Standard commit with staging/worktree validation: git cm '<message>'.",
    "co": "Checkout a specific branch: git co '<branch>'.",
    "d": "Run a directory difftool between two refs. Syntax: git d <ref_a> <ref_b>.",
    "dcc": "Run a directory difftool between HEAD~1 and HEAD.",
    "dccc": "Run a directory difftool between HEAD~2 and HEAD.",
    "de": "Print last tagged commit details.",
    "di": "Discard current changes on file: git di '<filename>'",
    "dime": "Discard merge changes in favor of their files.",
    "diyou": "Discard merge changes in favor of your files.",
    "dwc": "Run a directory difftool between working tree and HEAD.",
    "dwcc": "Run a directory difftool between working tree and HEAD~1.",
    "ed": "Edit a file. Syntax: git ed <filename>.",
    "fe": "Fetch new data of current branch from origin.",
    "feall": "Fetch new data from origin for all branch.",
    "gp": "Open git commits graph (Git K).",
    "gr": "Open git tags graph (Git K).",
    "lb": "Print all branches.",
    "lg": "Print commit history.",
    "lh": "Print last commit details.",
    "ll": "Print latest full commit hash.",
    "lm": "Print all merges.",
    "lt": "Print tags with containing branches.",
    "major": "Release a new major version from the work branch. Options: --include-patch.",
    "minor": "Release a new minor version from the work branch. Options: --include-patch.",
    "new": "Conventional commit new(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "implement": "Conventional commit implement(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "refactor": "Conventional commit refactor(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "fix": "Conventional commit fix(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "change": "Conventional commit change(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "docs": "Conventional commit docs(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "style": "Conventional commit style(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "revert": "Conventional commit revert(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "misc": "Conventional commit misc(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "cover": "Conventional commit cover(<module>): <description>. Input: '<module>: <description>' or '<description>' (uses default_module).",
    "me": "Merge",
    "pl": "Pull (fetch + merge FETCH_HEAD) from origin on current branch.",
    "pt": "Push all new tags to origin.",
    "pu": "Push current branch to origin (add upstream (tracking) reference for pull).",
    "patch": "Release a new patch version from the work branch. Options: --include-patch.",
    "ra": "Remove all staged files and return them to the working tree (inverse of aa).",
    "rf": "Print changes on HEAD reference.",
    "rmloc": "Remove changed files from the working tree.",
    "rmstg": "Remove staged files from index tree.",
    "rmtg": "Remove a tag on current branch and from origin.",
    "rmunt": "Remove untracked files from the working tree.",
    "rs": "Reset current branch to HEAD (--hard).",
    "rshrd": "Hard reset alias (--hard).",
    "rskep": "Keep reset alias (--keep).",
    "rsmix": "Mixed reset alias (--mixed).",
    "rsmrg": "Merge reset alias (--merge).",
    "rssft": "Soft reset alias (--soft).",
    "st": "Print current GIT status.",
    "tg": "Create a new annotate tag. Syntax: git tg <description> <tag>.",
    "unstg": "Un-stage a file from commit: git unstg '<filename>'. Unstage all files with: git unstg *.",
    "wip": "Commit work in progress with an automatic message and the same checks as cm.",
    "ver": "Verify version consistency across configured files. Options: --verbose, --debug.",
    "str": "Display all unique remotes and show detailed status for each.",
}

## @brief Constant `RESET_HELP` used by CLI runtime paths and policies.

RESET_HELP = """

 Reset commands help screen

 default mode = '--mixed'

 working - working tree
 index   - staging area ready to commit
 HEAD    - latest commit
 target  - example: origin/master

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  A       B     C    D     --soft   A       B     D
                           --mixed  A       D     D
                           --hard   D       D     D
                           --merge  (disallowed)
                           --keep   (disallowed)

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  A       B     C    C     --soft   A       B     C
                           --mixed  A       C     C
                           --hard   C       C     C
                           --merge  (disallowed)
                           --keep   A       C     C

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  B       B     C    D     --soft   B       B     D
                           --mixed  B       D     D
                           --hard   D       D     D
                           --merge  D       D     D
                           --keep   (disallowed)

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  B       B     C    C     --soft   B       B     C
                           --mixed  B       C     C
                           --hard   C       C     C
                           --merge  C       C     C
                           --keep   B       C     C

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  B       C     C    D     --soft   B       C     D
                           --mixed  B       D     D
                           --hard   D       D     D
                           --merge  (disallowed)
                           --keep   (disallowed)

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  B       C     C    C     --soft   B       C     C
                           --mixed  B       C     C
                           --hard   C       C     C
                           --merge  B       C     C
                           --keep   B       C     C

 The following tables show what happens when there are unmerged entries:
 X means any state and U means an unmerged index.

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  X       U     A    B     --soft   (disallowed)
                           --mixed  X       B     B
                           --hard   B       B     B
                           --merge  B       B     B
                           --keep   (disallowed)

 working index HEAD target         working index HEAD
 ----------------------------------------------------
  X       U     A    A     --soft   (disallowed)
                           --mixed  X       A     A
                           --hard   A       A     A
                           --merge  A       A     A
                           --keep   (disallowed)

"""

## @brief Constant `RESET_HELP_COMMANDS` used by CLI runtime paths and policies.

RESET_HELP_COMMANDS = {"rs", "rshrd", "rskep", "rsmix", "rsmrg", "rssft"}


## @brief Execute `_to_args` runtime logic for Git-Alias CLI.
# @details Executes `_to_args` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `_to_args`.
# @return Result emitted by `_to_args` according to command contract.
def _to_args(extra):
    return list(extra) if extra else []


## @brief Class `CommandExecutionError` models a typed runtime container/error boundary.
class CommandExecutionError(RuntimeError):
    ## @brief Execute `__init__` runtime logic for Git-Alias CLI.
    # @param self Input parameter consumed by `__init__`.
    # @param exc Input parameter consumed by `__init__`.
    # @return Result emitted by `__init__` according to command contract.
    def __init__(self, exc: subprocess.CalledProcessError):
        self.cmd = exc.cmd
        self.returncode = exc.returncode
        self.stdout = exc.stdout
        self.stderr = exc.stderr
        message = self._format_message()
        super().__init__(message)

    ## @brief Execute `_format_message` runtime logic for Git-Alias CLI.
    # @param self Input parameter consumed by `_format_message`.
    # @return Result emitted by `_format_message` according to command contract.
    def _format_message(self) -> str:
        text = self._decode_stream(self.stderr).strip()
        if text:
            return text
        cmd_display = ""
        if isinstance(self.cmd, (list, tuple)):
            cmd_display = " ".join(str(part) for part in self.cmd)
        elif self.cmd:
            cmd_display = str(self.cmd)
        return f"Command '{cmd_display}' failed with exit code {self.returncode}"

    @staticmethod
    ## @brief Execute `_decode_stream` runtime logic for Git-Alias CLI.
    # @param data Input parameter consumed by `_decode_stream`.
    # @return Result emitted by `_decode_stream` according to command contract.
    def _decode_stream(data) -> str:
        if data is None:
            return ""
        if isinstance(data, bytes):
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return data.decode("utf-8", errors="replace")
        return str(data)


## @brief Execute `_run_checked` runtime logic for Git-Alias CLI.
# @details Executes `_run_checked` using deterministic CLI control-flow and explicit error propagation.
# @param *popenargs Input parameter consumed by `_run_checked`.
# @param **kwargs Input parameter consumed by `_run_checked`.
# @return Result emitted by `_run_checked` according to command contract.
def _run_checked(*popenargs, **kwargs):
    kwargs.setdefault("check", True)
    try:
        return subprocess.run(*popenargs, **kwargs)
    except subprocess.CalledProcessError as exc:
        raise CommandExecutionError(exc) from None


## @brief Class `VersionDetectionError` models a typed runtime container/error boundary.
class VersionDetectionError(RuntimeError):
    pass


## @brief Class `ReleaseError` models a typed runtime container/error boundary.
class ReleaseError(RuntimeError):
    pass


## @brief Execute `run_git_cmd` runtime logic for Git-Alias CLI.
# @details Executes `run_git_cmd` using deterministic CLI control-flow and explicit error propagation.
# @param base_args Input parameter consumed by `run_git_cmd`.
# @param extra Input parameter consumed by `run_git_cmd`.
# @param cwd Input parameter consumed by `run_git_cmd`.
# @param **kwargs Input parameter consumed by `run_git_cmd`.
# @return Result emitted by `run_git_cmd` according to command contract.
def run_git_cmd(base_args, extra=None, cwd=None, **kwargs):
    full = ["git"] + list(base_args) + _to_args(extra)
    return _run_checked(full, cwd=cwd, **kwargs)


## @brief Execute `capture_git_output` runtime logic for Git-Alias CLI.
# @details Executes `capture_git_output` using deterministic CLI control-flow and explicit error propagation.
# @param base_args Input parameter consumed by `capture_git_output`.
# @param cwd Input parameter consumed by `capture_git_output`.
# @return Result emitted by `capture_git_output` according to command contract.
def capture_git_output(base_args, cwd=None):
    result = _run_checked(["git"] + list(base_args), cwd=cwd, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()


## @brief Execute `run_command` runtime logic for Git-Alias CLI.
# @details Executes `run_command` using deterministic CLI control-flow and explicit error propagation.
# @param cmd Input parameter consumed by `run_command`.
# @param cwd Input parameter consumed by `run_command`.
# @return Result emitted by `run_command` according to command contract.
def run_command(cmd, cwd=None):
    return _run_checked(cmd, cwd=cwd)


## @brief Execute `run_git_text` runtime logic for Git-Alias CLI.
# @details Executes `run_git_text` using deterministic CLI control-flow and explicit error propagation.
# @param args Input parameter consumed by `run_git_text`.
# @param cwd Input parameter consumed by `run_git_text`.
# @param check Input parameter consumed by `run_git_text`.
# @return Result emitted by `run_git_text` according to command contract.
def run_git_text(args, cwd=None, check=True):
    try:
        proc = _run_checked(
            ["git", *args],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )
    except CommandExecutionError as exc:
        message = CommandExecutionError._decode_stream(exc.stderr).strip()
        if not message:
            message = f"git {' '.join(args)} failed"
        raise RuntimeError(message) from None
    return proc.stdout.strip()


## @brief Execute `run_shell` runtime logic for Git-Alias CLI.
# @details Executes `run_shell` using deterministic CLI control-flow and explicit error propagation.
# @param command Input parameter consumed by `run_shell`.
# @param cwd Input parameter consumed by `run_shell`.
# @return Result emitted by `run_shell` according to command contract.
def run_shell(command, cwd=None):
    return _run_checked(command, shell=True, cwd=cwd)


## @brief Execute `_git_status_lines` runtime logic for Git-Alias CLI.
# @details Executes `_git_status_lines` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_git_status_lines` according to command contract.
def _git_status_lines():
    proc = _run_checked(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return proc.stdout.splitlines()


## @brief Execute `has_unstaged_changes` runtime logic for Git-Alias CLI.
# @details Executes `has_unstaged_changes` using deterministic CLI control-flow and explicit error propagation.
# @param status_lines Input parameter consumed by `has_unstaged_changes`.
# @return Result emitted by `has_unstaged_changes` according to command contract.
def has_unstaged_changes(status_lines=None):
    lines = status_lines if status_lines is not None else _git_status_lines()
    for line in lines:
        if not line:
            continue
        if line.startswith("??"):
            return True
        if len(line) > 1 and line[1] != " ":
            return True
    return False


## @brief Execute `has_staged_changes` runtime logic for Git-Alias CLI.
# @details Executes `has_staged_changes` using deterministic CLI control-flow and explicit error propagation.
# @param status_lines Input parameter consumed by `has_staged_changes`.
# @return Result emitted by `has_staged_changes` according to command contract.
def has_staged_changes(status_lines=None):
    lines = status_lines if status_lines is not None else _git_status_lines()
    for line in lines:
        if not line or line.startswith("??"):
            continue
        if line[0] != " ":
            return True
    return False


## @brief Constant `_REMOTE_REFS_UPDATED` used by CLI runtime paths and policies.

_REMOTE_REFS_UPDATED = False
## @brief Constant `WIP_MESSAGE_RE` used by CLI runtime paths and policies.

WIP_MESSAGE_RE = re.compile(r"^wip: work in progress\.$")


## @brief Execute `_refresh_remote_refs` runtime logic for Git-Alias CLI.
# @details Executes `_refresh_remote_refs` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_refresh_remote_refs` according to command contract.
def _refresh_remote_refs():
    global _REMOTE_REFS_UPDATED
    if _REMOTE_REFS_UPDATED:
        return
    try:
        run_git_cmd(["remote", "-v", "update"])
    except CommandExecutionError as exc:
        print(f"Unable to update remote references: {exc}", file=sys.stderr)
        return
    _REMOTE_REFS_UPDATED = True


## @brief Execute `_branch_remote_divergence` runtime logic for Git-Alias CLI.
# @details Executes `_branch_remote_divergence` using deterministic CLI control-flow and explicit error propagation.
# @param branch_key Input parameter consumed by `_branch_remote_divergence`.
# @param remote Input parameter consumed by `_branch_remote_divergence`.
# @return Result emitted by `_branch_remote_divergence` according to command contract.
def _branch_remote_divergence(branch_key, remote="origin"):
    _refresh_remote_refs()
    branch = get_branch(branch_key)
    upstream = f"{remote}/{branch}"
    try:
        counts = run_git_text(["rev-list", "--left-right", "--count", f"{branch}...{upstream}"])
    except RuntimeError:
        return (0, 0)
    parts = counts.strip().split()
    if len(parts) < 2:
        return (0, 0)
    try:
        local_ahead = int(parts[0])
        remote_ahead = int(parts[1])
    except ValueError:
        return (0, 0)
    return (local_ahead, remote_ahead)


## @brief Execute `has_remote_branch_updates` runtime logic for Git-Alias CLI.
# @details Executes `has_remote_branch_updates` using deterministic CLI control-flow and explicit error propagation.
# @param branch_key Input parameter consumed by `has_remote_branch_updates`.
# @param remote Input parameter consumed by `has_remote_branch_updates`.
# @return Result emitted by `has_remote_branch_updates` according to command contract.
def has_remote_branch_updates(branch_key, remote="origin"):
    _, remote_ahead = _branch_remote_divergence(branch_key, remote=remote)
    return remote_ahead > 0


## @brief Execute `has_remote_develop_updates` runtime logic for Git-Alias CLI.
# @details Executes `has_remote_develop_updates` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `has_remote_develop_updates` according to command contract.
def has_remote_develop_updates():
    return has_remote_branch_updates("develop")


## @brief Execute `has_remote_master_updates` runtime logic for Git-Alias CLI.
# @details Executes `has_remote_master_updates` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `has_remote_master_updates` according to command contract.
def has_remote_master_updates():
    return has_remote_branch_updates("master")


## @brief Execute `_head_commit_message` runtime logic for Git-Alias CLI.
# @details Executes `_head_commit_message` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_head_commit_message` according to command contract.
def _head_commit_message():
    try:
        return run_git_text(["log", "-1", "--pretty=%s"]).strip()
    except RuntimeError:
        return ""


## @brief Execute `_head_commit_hash` runtime logic for Git-Alias CLI.
# @details Executes `_head_commit_hash` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_head_commit_hash` according to command contract.
def _head_commit_hash():
    try:
        return run_git_text(["rev-parse", "HEAD"]).strip()
    except RuntimeError:
        return ""


## @brief Execute `_commit_exists_in_branch` runtime logic for Git-Alias CLI.
# @details Executes `_commit_exists_in_branch` using deterministic CLI control-flow and explicit error propagation.
# @param commit_hash Input parameter consumed by `_commit_exists_in_branch`.
# @param branch_name Input parameter consumed by `_commit_exists_in_branch`.
# @return Result emitted by `_commit_exists_in_branch` according to command contract.
def _commit_exists_in_branch(commit_hash, branch_name):
    if not commit_hash or not branch_name:
        return False
    proc = _run_checked(
        ["git", "merge-base", "--is-ancestor", commit_hash, branch_name],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode == 0


## @brief Execute `_should_amend_existing_commit` runtime logic for Git-Alias CLI.
# @details Executes `_should_amend_existing_commit` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_should_amend_existing_commit` according to command contract.
def _should_amend_existing_commit():
    message = _head_commit_message()
    if not (message and WIP_MESSAGE_RE.match(message)):
        return (False, "HEAD is not a WIP commit.")
    commit_hash = _head_commit_hash()
    if not commit_hash:
        return (False, "Unable to determine the HEAD commit hash.")
    develop_branch = get_branch("develop")
    master_branch = get_branch("master")
    if _commit_exists_in_branch(commit_hash, develop_branch):
        return (False, f"The last WIP commit is already contained in {develop_branch}.")
    if _commit_exists_in_branch(commit_hash, master_branch):
        return (False, f"The last WIP commit is already contained in {master_branch}.")
    return (True, "HEAD WIP commit is still pending locally.")


## @brief Execute `is_inside_git_repo` runtime logic for Git-Alias CLI.
# @details Executes `is_inside_git_repo` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `is_inside_git_repo` according to command contract.
def is_inside_git_repo():
    try:
        output = run_git_text(["rev-parse", "--is-inside-work-tree"])
    except RuntimeError:
        return False
    return output.strip().lower() == "true"


@dataclass
## @brief Class `TagInfo` models a typed runtime container/error boundary.
# @details Encapsulates tag identity, tag date, and resolved Git object identifier for changelog assembly.

class TagInfo:
    ## @brief Store raw tag name including `v` prefix when present.
    name: str
    ## @brief Store ISO date string used for changelog section headers.
    iso_date: str
    ## @brief Store object hash associated with the tag reference.
    object_name: str


## @brief Constant `DELIM` used by CLI runtime paths and policies.

DELIM = "\x1f"
## @brief Constant `RECORD` used by CLI runtime paths and policies.

RECORD = "\x1e"
## @brief Constant `_CONVENTIONAL_RE` used by CLI runtime paths and policies.

_CONVENTIONAL_RE = re.compile(
    r"^(?P<type>new|fix|change|implement|refactor|docs|style|revert|misc|cover)"
    r"(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s+(?P<desc>.+)$",
    re.IGNORECASE,
)
## @brief Constant `_MODULE_PREFIX_RE` used by CLI runtime paths and policies.

_MODULE_PREFIX_RE = re.compile(r"^(?P<module>[A-Za-z0-9_]+):\s*(?P<body>.*)$")
## @brief Constant `_SEMVER_TAG_RE` used by CLI runtime paths and policies.

_SEMVER_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
## @brief Constant `SEMVER_RE` used by CLI runtime paths and policies.

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
## @brief Constant `SECTION_EMOJI` used by CLI runtime paths and policies.

SECTION_EMOJI = {
    "Features": "⛰️",
    "Implementations": "🏗️",
    "Bug Fixes": "🐛",
    "Changes": "🚜",
    "Refactor": "✨",
    "Documentation": "📚",
    "Styling": "🎨",
    "Miscellaneous Tasks": "⚙️",
    "Revert": "◀️",
    "Cover Requirements": "🎯",
}

## @brief Execute `_tag_semver_tuple` runtime logic for Git-Alias CLI.
# @details Executes `_tag_semver_tuple` using deterministic CLI control-flow and explicit error propagation.
# @param tag_name Input parameter consumed by `_tag_semver_tuple`.
# @return Result emitted by `_tag_semver_tuple` according to command contract.
def _tag_semver_tuple(tag_name: str) -> Optional[Tuple[int, int, int]]:
    return _parse_semver_tuple(tag_name.lstrip("v"))


## @brief Execute `_latest_supported_tag_name` runtime logic for Git-Alias CLI.
# @details Executes `_latest_supported_tag_name` using deterministic CLI control-flow and explicit error propagation.
# @param tags Input parameter consumed by `_latest_supported_tag_name`.
# @return Result emitted by `_latest_supported_tag_name` according to command contract.
def _latest_supported_tag_name(tags: List[TagInfo]) -> Optional[str]:
    return tags[-1].name if tags else None


## @brief Predicate: tag is a minor release.
# @details Returns `True` when `tag_name` is a semver tag where `patch==0` AND `(major>=1 OR minor>=1)`,
#          i.e. version `>=0.1.0` with no patch component.
#          Patch releases (`patch>0`) and pre-0.1.0 tags (`0.0.x`) return `False`.
# @param tag_name Semver tag string, optionally prefixed with `v` (e.g. `v0.1.0`, `0.2.0`).
# @return `True` iff tag represents a minor release; `False` otherwise.
# @satisfies REQ-018, REQ-040
def _is_minor_release_tag(tag_name: str) -> bool:
    parts = _tag_semver_tuple(tag_name)
    if parts is None:
        return False
    major, minor, patch = parts
    return patch == 0 and (major >= 1 or minor >= 1)


## @brief Locate the chronologically latest patch tag after a given minor release.
# @details Scans `all_tags` (sorted chronologically, ascending) for tags that are NOT minor releases
#          and appear after `last_minor` in the list.  When `last_minor` is `None`, scans all tags.
#          Returns the last qualifying `TagInfo` (most recent), or `None` if no patch exists.
# @param all_tags  Full list of `TagInfo` sorted by date ascending (from `list_tags_sorted_by_date`).
# @param last_minor The last minor-release `TagInfo` to anchor the search; `None` means no minor exists.
# @return Most recent `TagInfo` that is not a minor release and appears after `last_minor`, or `None`.
# @satisfies REQ-040
def _latest_patch_tag_after(all_tags: List[TagInfo], last_minor: Optional[TagInfo]) -> Optional[TagInfo]:
    if last_minor is None:
        candidates = all_tags
    else:
        idx = next((i for i, t in enumerate(all_tags) if t.name == last_minor.name), None)
        candidates = all_tags[idx + 1:] if idx is not None else []
    patch_tags = [t for t in candidates if not _is_minor_release_tag(t.name)]
    return patch_tags[-1] if patch_tags else None


## @brief Execute `list_tags_sorted_by_date` runtime logic for Git-Alias CLI.
# @details Executes `list_tags_sorted_by_date` using deterministic CLI control-flow and explicit error propagation.
# @param repo_root Input parameter consumed by `list_tags_sorted_by_date`.
# @param merged_ref Input parameter consumed by `list_tags_sorted_by_date`.
# @return Result emitted by `list_tags_sorted_by_date` according to command contract.
def list_tags_sorted_by_date(repo_root: Path, merged_ref: Optional[str] = None) -> List[TagInfo]:
    fmt = f"%(refname:strip=2){DELIM}%(creatordate:short){DELIM}%(objectname)"
    args = ["for-each-ref", "--sort=creatordate", f"--format={fmt}"]
    if merged_ref:
        args.extend(["--merged", merged_ref])
    args.append("refs/tags")
    output = run_git_text(args, cwd=repo_root, check=False)
    if not output:
        return []
    tags: List[TagInfo] = []
    for line in output.splitlines():
        parts = line.split(DELIM)
        if len(parts) != 3:
            continue
        name, date_s, obj = parts
        if not _SEMVER_TAG_RE.match(name):
            continue
        tags.append(TagInfo(name=name, iso_date=date_s or "unknown-date", object_name=obj))
    return tags


## @brief Execute `git_log_subjects` runtime logic for Git-Alias CLI.
# @details Executes `git_log_subjects` using deterministic CLI control-flow and explicit error propagation.
# @param repo_root Input parameter consumed by `git_log_subjects`.
# @param rev_range Input parameter consumed by `git_log_subjects`.
# @return Result emitted by `git_log_subjects` according to command contract.
def git_log_subjects(repo_root: Path, rev_range: str) -> List[str]:
    fmt = f"%s{RECORD}"
    out = run_git_text(
        ["log", "--no-merges", f"--pretty=format:{fmt}", rev_range],
        cwd=repo_root,
        check=False,
    )
    if not out:
        return []
    return [x.strip() for x in out.split(RECORD) if x.strip()]


## @brief Execute `categorize_commit` runtime logic for Git-Alias CLI.
# @details Parses a conventional commit subject line and maps it to a changelog section and formatted entry line.
# Entry line format: `- <description> *(<scope>)*` when scope is present; `- <description>` otherwise.
# @param subject Conventional commit subject string (e.g. `type(scope): description`).
# @return Tuple `(section, line)`: `section` is the changelog section name or `None` if type is unmapped or ignored; `line` is the formatted entry string or `""` when section is `None`.
def categorize_commit(subject: str) -> Tuple[Optional[str], str]:
    match = _CONVENTIONAL_RE.match(subject.strip())
    if not match:
        return (None, "")
    ctype = match.group("type").lower()
    scope = match.group("scope")
    desc = match.group("desc").strip()
    scope_text = f" *({scope})*" if scope else ""
    line = f"- {desc}{scope_text}"
    mapping = {
        "new": "Features",
        "implement": "Implementations",
        "fix": "Bug Fixes",
        "change": "Changes",
        "cover": "Cover Requirements",
        "refactor": "Refactor",
        "docs": "Documentation",
        "style": "Styling",
        "revert": "Revert",
        "misc": "Miscellaneous Tasks",
    }
    section = mapping.get(ctype)
    return (section, line) if section else (None, "")


## @brief Execute `_extract_release_version` runtime logic for Git-Alias CLI.
# @details Executes `_extract_release_version` using deterministic CLI control-flow and explicit error propagation.
# @param subject Input parameter consumed by `_extract_release_version`.
# @return Result emitted by `_extract_release_version` according to command contract.
def _extract_release_version(subject: str) -> Optional[str]:
    match = re.match(
        r"\s*(?:release version:\s+|release:\s+release version\s+)(\d+\.\d+\.\d+)\s*$",
        subject,
        re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1)


## @brief Execute `_is_release_marker_commit` runtime logic for Git-Alias CLI.
# @details Executes `_is_release_marker_commit` using deterministic CLI control-flow and explicit error propagation.
# @param subject Input parameter consumed by `_is_release_marker_commit`.
# @return Result emitted by `_is_release_marker_commit` according to command contract.
def _is_release_marker_commit(subject: str) -> bool:
    return _extract_release_version(subject) is not None


## @brief Execute `generate_section_for_range` runtime logic for Git-Alias CLI.
# @details Executes `generate_section_for_range` using deterministic CLI control-flow and explicit error propagation.
# @param repo_root Input parameter consumed by `generate_section_for_range`.
# @param title Input parameter consumed by `generate_section_for_range`.
# @param date_s Input parameter consumed by `generate_section_for_range`.
# @param rev_range Input parameter consumed by `generate_section_for_range`.
# @param expected_version Input parameter consumed by `generate_section_for_range`.
# @return Result emitted by `generate_section_for_range` according to command contract.
def generate_section_for_range(repo_root: Path, title: str, date_s: str, rev_range: str, expected_version: Optional[str] = None) -> Optional[str]:
    subjects = git_log_subjects(repo_root, rev_range)
    buckets: Dict[str, List[str]] = defaultdict(list)
    for subj in subjects:
        if _is_release_marker_commit(subj):
            continue
        release_version = _extract_release_version(subj)
        if expected_version and release_version and release_version != expected_version:
            continue
        section, line = categorize_commit(subj)
        if section and line:
            buckets[section].append(line)
    if not any(buckets.values()):
        return None
    lines: List[str] = []
    lines.append(f"## {title} - {date_s}")
    order = [
        "Features",
        "Implementations",
        "Bug Fixes",
        "Changes",
        "Cover Requirements",
        "Refactor",
        "Documentation",
        "Styling",
        "Miscellaneous Tasks",
        "Revert",
    ]
    for sec in order:
        entries = buckets.get(sec, [])
        if entries:
            emoji = SECTION_EMOJI.get(sec, "")
            header = f"### {emoji}  {sec}".rstrip()
            lines.append(header)
            lines.extend(entries)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


## @brief Resolve the git remote name configured for a given branch.
# @details Queries `git config branch.<branch_name>.remote` via a local git command.
#          Returns `origin` as fallback when the config key is absent or the command fails.
#          No network operations are performed.
# @param branch_name Local branch name whose configured remote is requested (e.g. `"master"`).
# @param repo_root Absolute path used as CWD for the git config query.
# @return Remote name string; never empty (falls back to `"origin"`).
# @satisfies REQ-046
def _get_remote_name_for_branch(branch_name: str, repo_root: Path) -> str:
    remote = run_git_text(
        ["config", "--get", f"branch.{branch_name}.remote"],
        cwd=repo_root,
        check=False,
    ).strip()
    return remote if remote else "origin"


## @brief Resolve the normalized HTTPS base URL from the master branch's configured remote.
# @details Parses both SSH (`git@<host>:<owner>/<repo>[.git]`) and HTTPS
#          (`https://<host>/<owner>/<repo>[.git]`) formats and extracts `<owner>` and `<repo>`
#          through deterministic string parsing.
# @param remote_url Raw git remote URL string.
# @return Tuple `(owner, repo)` when parsing succeeds; otherwise `None`.
def _extract_owner_repo(remote_url: str) -> Optional[Tuple[str, str]]:
    value = (remote_url or "").strip()
    if not value:
        return None
    if value.startswith("git@"):
        if ":" not in value:
            return None
        path_part = value.split(":", 1)[1]
    else:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return None
        path_part = parsed.path.lstrip("/")
    path_part = path_part.rstrip("/")
    if path_part.endswith(".git"):
        path_part = path_part[:-4]
    parts = [segment for segment in path_part.split("/") if segment]
    if len(parts) != 2:
        return None
    owner, repo = parts
    if not owner or not repo:
        return None
    return owner, repo


## @brief Resolve normalized GitHub URL base from the master-branch configured remote.
# @details Determines remote name using `_get_remote_name_for_branch` with the configured
#          master branch, then executes local `git remote get-url <remote>` command.
#          If command execution fails or URL parsing fails, returns `None`.
#          On success, always emits `https://github.com/<owner>/<repo>` for changelog templates.
#          No network operation is performed; all data is derived from local git metadata.
# @param repo_root Absolute path to the repository root used as CWD for all git commands.
# @return Normalized HTTPS base URL string (no trailing `.git`), or `None` on failure.
# @satisfies REQ-043, REQ-046
def _canonical_origin_base(repo_root: Path) -> Optional[str]:
    master_branch = get_branch("master")
    remote = _get_remote_name_for_branch(master_branch, repo_root)
    try:
        url = run_git_text(["remote", "get-url", remote], cwd=repo_root, check=True).strip()
    except RuntimeError:
        return None
    owner_repo = _extract_owner_repo(url)
    if owner_repo is None:
        return None
    owner, repo = owner_repo
    return f"https://github.com/{owner}/{repo}"


## @brief Execute `get_origin_compare_url` runtime logic for Git-Alias CLI.
# @details Executes `get_origin_compare_url` using deterministic CLI control-flow and explicit error propagation.
# @param base_url Input parameter consumed by `get_origin_compare_url`.
# @param prev_tag Input parameter consumed by `get_origin_compare_url`.
# @param tag Input parameter consumed by `get_origin_compare_url`.
# @return Result emitted by `get_origin_compare_url` according to command contract.
def get_origin_compare_url(base_url: Optional[str], prev_tag: Optional[str], tag: str) -> Optional[str]:
    if not base_url:
        return None
    if prev_tag:
        return f"{base_url}/compare/{prev_tag}..{tag}"
    return f"{base_url}/releases/tag/{tag}"


## @brief Execute `get_release_page_url` runtime logic for Git-Alias CLI.
# @details Executes `get_release_page_url` using deterministic CLI control-flow and explicit error propagation.
# @param base_url Input parameter consumed by `get_release_page_url`.
# @param tag Input parameter consumed by `get_release_page_url`.
# @return Result emitted by `get_release_page_url` according to command contract.
def get_release_page_url(base_url: Optional[str], tag: str) -> Optional[str]:
    if not base_url:
        return None
    return f"{base_url}/releases/tag/{tag}"


## @brief Execute `build_history_section` runtime logic for Git-Alias CLI.
# @details Executes `build_history_section` using deterministic CLI control-flow and explicit error propagation.
# @param repo_root Input parameter consumed by `build_history_section`.
# @param tags Input parameter consumed by `build_history_section`.
# @param include_unreleased Input parameter consumed by `build_history_section`.
# @param include_unreleased_link Input parameter consumed by `build_history_section`.
# @return Result emitted by `build_history_section` according to command contract.
def build_history_section(
    repo_root: Path,
    tags: List[TagInfo],
    include_unreleased: bool,
    include_unreleased_link: bool = True,
) -> Optional[str]:
    base = _canonical_origin_base(repo_root)
    if not base:
        return None
    lines = ["# History"]
    visible_tags = tags
    if visible_tags:
        lines.append("")
        for tag in visible_tags:
            release_url = get_release_page_url(base, tag.name)
            if release_url:
                lines.append(f"- \\[{tag.name.lstrip('v')}\\]: {release_url}")
        lines.append("")
    prev: Optional[str] = None
    for tag in visible_tags:
        compare = get_origin_compare_url(base, prev, tag.name)
        if compare:
            lines.append(f"[{tag.name.lstrip('v')}]: {compare}")
        prev = tag.name
    if include_unreleased and include_unreleased_link:
        baseline = _latest_supported_tag_name(tags)
        if baseline:
            compare = get_origin_compare_url(base, baseline, "HEAD")
            if compare:
                lines.append(f"[unreleased]: {compare}")
    return "\n".join(lines).rstrip() + "\n"


## @brief Generate the full CHANGELOG.md document from repository tags and commits.
# @details Groups commits by minor release (semver where `patch=0` AND version `>=0.1.0`).
#          By default only minor releases appear; the document body is empty when none exist.
#          With `include_patch=True`, prepends the latest patch release after the last minor
#          (or the latest patch overall when no minor exists) including all commits in that range.
#          Releases are ordered reverse-chronologically in the output.
#          `# History` contains only the version tags present in the changelog body:
#          minor tags when `include_patch=False`; minor tags plus the latest patch when
#          `include_patch=True`. Diff links in `# History` use the same ranges as the
#          corresponding changelog sections. History generation can be disabled by flag.
# @param repo_root Absolute path to the repository root used as CWD for all git commands.
# @param include_patch When `True`, prepend the latest patch release section to the document.
# @param disable_history When `True`, omit `# History` section from output.
# @return Complete `CHANGELOG.md` string content, terminated with a newline.
# @satisfies REQ-018, REQ-040, REQ-041, REQ-043, REQ-068, REQ-069, REQ-070
def generate_changelog_document(repo_root: Path, include_patch: bool, disable_history: bool = False) -> str:
    all_tags = list_tags_sorted_by_date(repo_root)
    origin_base = _canonical_origin_base(repo_root)
    lines: List[str] = ["# Changelog", ""]
    release_sections: List[str] = []
    minor_tags = [t for t in all_tags if _is_minor_release_tag(t.name)]
    last_minor: Optional[TagInfo] = minor_tags[-1] if minor_tags else None
    latest_patch: Optional[TagInfo] = None
    if include_patch:
        latest_patch = _latest_patch_tag_after(all_tags, last_minor)
        if latest_patch:
            rev_range = (
                f"{last_minor.name}..{latest_patch.name}" if last_minor else latest_patch.name
            )
            display = latest_patch.name.lstrip("v")
            compare_url = get_origin_compare_url(
                origin_base, last_minor.name if last_minor else None, latest_patch.name
            )
            title = f"[{display}]({compare_url})" if compare_url else display
            section = generate_section_for_range(
                repo_root,
                title,
                latest_patch.iso_date,
                rev_range,
                expected_version=display,
            )
            if section:
                lines.append(section)
    prev_included: Optional[str] = None
    for tag in minor_tags:
        rev_range = tag.name if prev_included is None else f"{prev_included}..{tag.name}"
        display = tag.name.lstrip("v")
        compare_url = get_origin_compare_url(origin_base, prev_included, tag.name)
        title = f"[{display}]({compare_url})" if compare_url else display
        section = generate_section_for_range(
            repo_root,
            title,
            tag.iso_date,
            rev_range,
            expected_version=display,
        )
        if section:
            release_sections.append(section)
        prev_included = tag.name
    if release_sections:
        lines.extend(reversed(release_sections))
    if not disable_history:
        history_tags: List[TagInfo] = list(minor_tags)
        if latest_patch is not None:
            history_tags = history_tags + [latest_patch]
        history = build_history_section(
            repo_root,
            history_tags,
            False,
            include_unreleased_link=False,
        )
        if history:
            lines.append("")
            lines.append(history)
    return "\n".join(lines).rstrip() + "\n"


## @brief Execute `_collect_version_files` runtime logic for Git-Alias CLI.
# @details Executes `_collect_version_files` using deterministic CLI control-flow and explicit error propagation.
# @param root Input parameter consumed by `_collect_version_files`.
# @param pattern Input parameter consumed by `_collect_version_files`.
# @return Result emitted by `_collect_version_files` according to command contract.
## @brief Store resolved per-rule context for version discovery and matching.
# @details Encapsulates immutable artifacts required across detect/update/verify phases:
#          compiled regex, resolved file list, and pre-rendered relative-path map for stable debug output.
# @note Complexity: O(1) storage per field; aggregate complexity scales with matched file count per rule.
@dataclass(frozen=True)
class VersionRuleContext:
    pattern: str
    expression: str
    compiled_regex: re.Pattern
    files: List[Path]
    relative_map: Dict[Path, str]


## @brief Normalize a `ver_rules` pattern to the internal pathspec matching form.
# @details Converts separators to POSIX style, strips leading `./`, and anchors patterns containing `/`
#          to repository root by prefixing `/` when missing, preserving REQ-017 semantics.
# @param pattern Input pattern string from configuration.
# @return Normalized pathspec-compatible pattern string; empty string when input is blank.
def _normalize_version_rule_pattern(pattern: str) -> str:
    trimmed = (pattern or "").strip()
    if not trimmed:
        return ""
    normalized_pattern = trimmed.replace("\\", "/")
    if normalized_pattern.startswith("./"):
        normalized_pattern = normalized_pattern[2:]
    if "/" in normalized_pattern and not normalized_pattern.startswith("/"):
        normalized_pattern = f"/{normalized_pattern}"
    return normalized_pattern


## @brief Build a deduplicated repository file inventory for version rule evaluation.
# @details Executes a single `rglob("*")` traversal from repository root, filters to files only,
#          applies hardcoded exclusion regexes, normalizes relative paths, and deduplicates by resolved path.
# @param root Repository root path used as traversal anchor.
# @return List of tuples `(absolute_path, normalized_relative_path)` used by downstream matchers.
def _build_version_file_inventory(root: Path) -> List[Tuple[Path, str]]:
    inventory: List[Tuple[Path, str]] = []
    seen = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if _is_version_path_excluded(relative):
            continue
        normalized_relative = (relative or "").replace("\\", "/").strip()
        if not normalized_relative:
            continue
        if normalized_relative.startswith("./"):
            normalized_relative = normalized_relative[2:]
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        inventory.append((path, normalized_relative))
    return inventory


## @brief Execute `_collect_version_files` runtime logic for Git-Alias CLI.
# @details Executes `_collect_version_files` using deterministic CLI control-flow and explicit error propagation.
#          Uses precomputed inventory when provided to avoid repeated repository traversals.
# @param root Input parameter consumed by `_collect_version_files`.
# @param pattern Input parameter consumed by `_collect_version_files`.
# @param inventory Optional precomputed `(path, normalized_relative_path)` list.
# @return Result emitted by `_collect_version_files` according to command contract.
def _collect_version_files(root, pattern, *, inventory=None):
    files = []
    normalized_pattern = _normalize_version_rule_pattern(pattern)
    if not normalized_pattern:
        return files
    # @details Apply pathspec matcher to preserve configured GitIgnore-like semantics.
    spec = pathspec.PathSpec.from_lines("gitignore", [normalized_pattern])
    candidates = inventory if inventory is not None else _build_version_file_inventory(root)
    for path, normalized_relative in candidates:
        matches = spec.match_file(normalized_relative)
        if not matches and normalized_pattern.startswith("/") and not normalized_relative.startswith("/"):
            matches = spec.match_file(f"/{normalized_relative}")
        if matches:
            files.append(path)

    return files


## @brief Execute `_is_version_path_excluded` runtime logic for Git-Alias CLI.
# @details Executes `_is_version_path_excluded` using deterministic CLI control-flow and explicit error propagation.
# @param relative_path Input parameter consumed by `_is_version_path_excluded`.
# @return Result emitted by `_is_version_path_excluded` according to command contract.
def _is_version_path_excluded(relative_path: str) -> bool:
    return any(regex.search(relative_path) for regex in VERSION_CLEANUP_PATTERNS)


## @brief Execute `_iter_versions_in_text` runtime logic for Git-Alias CLI.
# @details Executes `_iter_versions_in_text` using deterministic CLI control-flow and explicit error propagation.
# @param text Input parameter consumed by `_iter_versions_in_text`.
# @param compiled_regexes Input parameter consumed by `_iter_versions_in_text`.
# @return Result emitted by `_iter_versions_in_text` according to command contract.
def _iter_versions_in_text(text, compiled_regexes):
    for regex in compiled_regexes:
        for match in regex.finditer(text):
            if match.groups():
                for group in match.groups():
                    if group:
                        yield group
                        break
            else:
                yield match.group(0)


## @brief Read and cache UTF-8 text content for a version-managed file.
# @details Loads file content with UTF-8 decoding; falls back to `errors="ignore"` on decode failures.
#          Emits deterministic stderr diagnostics on I/O failure and returns `None` for caller-managed skip logic.
# @param file_path Absolute path of the file to read.
# @param text_cache Optional mutable cache keyed by `Path` to avoid duplicate reads across phases.
# @return File text payload or `None` when file cannot be read.
def _read_version_file_text(file_path: Path, text_cache: Optional[Dict[Path, str]] = None) -> Optional[str]:
    if text_cache is not None and file_path in text_cache:
        return text_cache[file_path]
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        print(f"Unable to read {file_path}: {exc}", file=sys.stderr)
        return None
    if text_cache is not None:
        text_cache[file_path] = text
    return text


## @brief Build reusable per-rule contexts for canonical version evaluation workflows.
# @details Resolves matched files and compiled regex for each `(pattern, regex)` rule exactly once.
#          Preserves error contracts for unmatched patterns and invalid regex declarations.
# @param root Repository root path used for relative-path rendering.
# @param rules Sequence of `(pattern, regex)` tuples.
# @param inventory Optional precomputed inventory to avoid repeated filesystem traversal.
# @return Ordered list of `VersionRuleContext` objects aligned to input rule order.
# @throws VersionDetectionError when a rule matches no files or contains an invalid regex.
def _prepare_version_rule_contexts(
    root: Path, rules, *, inventory: Optional[List[Tuple[Path, str]]] = None
) -> List[VersionRuleContext]:
    contexts: List[VersionRuleContext] = []
    for pattern, expression in rules:
        files = _collect_version_files(root, pattern, inventory=inventory)
        relative_map: Dict[Path, str] = {}
        for file_path in files:
            try:
                relative_map[file_path] = file_path.relative_to(root).as_posix()
            except ValueError:
                relative_map[file_path] = str(file_path)
        if not files:
            raise VersionDetectionError(
                f"No files matched the version rule pattern '{pattern}'."
            )
        try:
            compiled = re.compile(expression)
        except re.error as exc:
            raise VersionDetectionError(
                f"Invalid regex '{expression}' for pattern '{pattern}': {exc}"
            )
        contexts.append(
            VersionRuleContext(
                pattern=pattern,
                expression=expression,
                compiled_regex=compiled,
                files=files,
                relative_map=relative_map,
            )
        )
    return contexts


## @brief Execute `_determine_canonical_version` runtime logic for Git-Alias CLI.
# @details Executes `_determine_canonical_version` using deterministic CLI control-flow and explicit error propagation.
# @param root Input parameter consumed by `_determine_canonical_version`.
# @param rules Input parameter consumed by `_determine_canonical_version`.
# @param verbose Input parameter consumed by `_determine_canonical_version`.
# @param debug Input parameter consumed by `_determine_canonical_version`.
# @param contexts Optional precomputed `VersionRuleContext` list for reuse across phases.
# @param text_cache Optional mutable cache keyed by file path to avoid duplicate reads.
# @return Result emitted by `_determine_canonical_version` according to command contract.
def _determine_canonical_version(
    root: Path,
    rules,
    *,
    verbose: bool = False,
    debug: bool = False,
    contexts: Optional[List[VersionRuleContext]] = None,
    text_cache: Optional[Dict[Path, str]] = None,
):
    active_contexts = contexts if contexts is not None else _prepare_version_rule_contexts(root, rules)
    canonical = None
    canonical_file = None
    for context in active_contexts:
        if debug:
            print(f"Pattern '{context.pattern}' matched files:")
            if context.files:
                for file_path in context.files:
                    print(f"  {context.relative_map[file_path]}")
            else:
                print("  (none)")
        matched_in_rule = False
        for file_path in context.files:
            text = _read_version_file_text(file_path, text_cache=text_cache)
            if text is None:
                continue
            versions = list(_iter_versions_in_text(text, [context.compiled_regex]))
            if verbose:
                match_state = "yes" if versions else "no"
                print(f"Regex match for {context.relative_map[file_path]}: {match_state}.")
            if versions:
                matched_in_rule = True
            for version in versions:
                if canonical is None:
                    canonical = version
                    canonical_file = file_path
                elif version != canonical:
                    raise VersionDetectionError(
                        f"Version mismatch between {canonical_file} ({canonical}) and {file_path} ({version})"
                    )
        if not matched_in_rule:
            raise VersionDetectionError(
                f"No version matches found for rule pattern '{context.pattern}' with regex '{context.expression}'."
            )
    if canonical is None:
        raise VersionDetectionError("No version string matched the configured rule list.")
    return canonical


## @brief Execute `_parse_semver_tuple` runtime logic for Git-Alias CLI.
# @details Executes `_parse_semver_tuple` using deterministic CLI control-flow and explicit error propagation.
# @param text Input parameter consumed by `_parse_semver_tuple`.
# @return Result emitted by `_parse_semver_tuple` according to command contract.
def _parse_semver_tuple(text: str) -> Optional[Tuple[int, int, int]]:
    match = SEMVER_RE.match((text or "").strip())
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


## @brief Execute `_replace_versions_in_text` runtime logic for Git-Alias CLI.
# @details Executes `_replace_versions_in_text` using deterministic CLI control-flow and explicit error propagation.
# @param text Input parameter consumed by `_replace_versions_in_text`.
# @param compiled_regex Input parameter consumed by `_replace_versions_in_text`.
# @param replacement Input parameter consumed by `_replace_versions_in_text`.
# @return Result emitted by `_replace_versions_in_text` according to command contract.
def _replace_versions_in_text(text, compiled_regex, replacement):
    last_index = 0
    pieces = []
    count = 0
    for match in compiled_regex.finditer(text):
        span = match.span(1) if match.groups() else match.span(0)
        pieces.append(text[last_index:span[0]])
        pieces.append(replacement)
        last_index = span[1]
        count += 1
    if count == 0:
        return text, 0
    pieces.append(text[last_index:])
    return "".join(pieces), count


## @brief Execute `_current_branch_name` runtime logic for Git-Alias CLI.
# @details Executes `_current_branch_name` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_current_branch_name` according to command contract.
def _current_branch_name():
    proc = _run_checked(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    branch = proc.stdout.strip()
    if not branch or branch == "HEAD":
        raise ReleaseError("Release commands require an active branch head.")
    return branch


## @brief Execute `_ref_exists` runtime logic for Git-Alias CLI.
# @details Executes `_ref_exists` using deterministic CLI control-flow and explicit error propagation.
# @param ref_name Input parameter consumed by `_ref_exists`.
# @return Result emitted by `_ref_exists` according to command contract.
def _ref_exists(ref_name):
    proc = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", ref_name],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


## @brief Execute `_local_branch_exists` runtime logic for Git-Alias CLI.
# @details Executes `_local_branch_exists` using deterministic CLI control-flow and explicit error propagation.
# @param branch_name Input parameter consumed by `_local_branch_exists`.
# @return Result emitted by `_local_branch_exists` according to command contract.
def _local_branch_exists(branch_name):
    return _ref_exists(f"refs/heads/{branch_name}")


## @brief Execute `_remote_branch_exists` runtime logic for Git-Alias CLI.
# @details Executes `_remote_branch_exists` using deterministic CLI control-flow and explicit error propagation.
# @param branch_name Input parameter consumed by `_remote_branch_exists`.
# @return Result emitted by `_remote_branch_exists` according to command contract.
def _remote_branch_exists(branch_name):
    return _ref_exists(f"refs/remotes/origin/{branch_name}")


## @brief Execute `_ensure_release_prerequisites` runtime logic for Git-Alias CLI.
# @details Executes `_ensure_release_prerequisites` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `_ensure_release_prerequisites` according to command contract.
def _ensure_release_prerequisites():
    master_branch = get_branch("master")
    develop_branch = get_branch("develop")
    work_branch = get_branch("work")
    missing_local = [name for name in (master_branch, develop_branch, work_branch) if not _local_branch_exists(name)]
    if missing_local:
        joined = ", ".join(missing_local)
        raise ReleaseError(f"Unable to run release command: missing local branches {joined}.")
    _refresh_remote_refs()
    missing_remote = [name for name in (master_branch, develop_branch) if not _remote_branch_exists(name)]
    if missing_remote:
        joined = ", ".join(missing_remote)
        raise ReleaseError(f"Unable to run release command: missing remote branches {joined}.")
    if has_remote_branch_updates("master"):
        raise ReleaseError(f"Remote branch {master_branch} has pending updates. Please pull them first.")
    if has_remote_branch_updates("develop"):
        raise ReleaseError(f"Remote branch {develop_branch} has pending updates. Please pull them first.")
    current_branch = _current_branch_name()
    if current_branch != work_branch:
        raise ReleaseError(f"Release commands must be executed from the {work_branch} branch (current: {current_branch}).")
    status = _git_status_lines()
    if has_unstaged_changes(status):
        raise ReleaseError("Working tree changes detected. Clean or stage them before running a release.")
    if has_staged_changes(status):
        raise ReleaseError("Staging area is not empty. Complete or reset pending commits before running a release.")
    return {"master": master_branch, "develop": develop_branch, "work": work_branch}


## @brief Execute `_bump_semver_version` runtime logic for Git-Alias CLI.
# @details Executes `_bump_semver_version` using deterministic CLI control-flow and explicit error propagation.
# @param current_version Input parameter consumed by `_bump_semver_version`.
# @param level Input parameter consumed by `_bump_semver_version`.
# @return Result emitted by `_bump_semver_version` according to command contract.
def _bump_semver_version(current_version, level):
    parts = _parse_semver_tuple(current_version)
    if parts is None:
        raise ReleaseError(f"The current version '{current_version}' is not a valid semantic version.")
    major, minor, patch = parts
    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "patch":
        patch += 1
    else:
        raise ReleaseError(f"Unsupported release level '{level}'.")
    return f"{major}.{minor}.{patch}"


## @brief Execute `_run_release_step` runtime logic for Git-Alias CLI.
# @details Executes `_run_release_step` using deterministic CLI control-flow and explicit error propagation.
# @param level Input parameter consumed by `_run_release_step`.
# @param step_name Input parameter consumed by `_run_release_step`.
# @param action Input parameter consumed by `_run_release_step`.
# @return Result emitted by `_run_release_step` according to command contract.
def _run_release_step(level, step_name, action):
    label = f"[release:{level}]"
    try:
        result = action()
        print(f"\n--- {label} Step '{step_name}' completed successfully. ---")
        return result
    except ReleaseError:
        raise
    except VersionDetectionError:
        raise
    except CommandExecutionError as exc:
        err_text = CommandExecutionError._decode_stream(exc.stderr).strip()
        message = err_text if err_text else str(exc)
        raise ReleaseError(f"\n--- {label} Step '{step_name}' failed: {message} ---") from None
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        raise ReleaseError(f"\n--- {label} Step '{step_name}' failed: command exited with status {code} ---") from None
    except Exception as exc:
        raise ReleaseError(f"\n--- {label} Step '{step_name}' failed: {exc} ---") from None


## @brief Execute `_create_release_commit_for_flow` runtime logic for Git-Alias CLI.
# @details Executes release-flow first-commit creation with WIP amend semantics reused from `_execute_commit`.
# @param target_version Input parameter consumed by `_create_release_commit_for_flow`.
# @return Result emitted by `_create_release_commit_for_flow` according to command contract.
def _create_release_commit_for_flow(target_version):
    _ensure_commit_ready("release")
    message = f"release: Release version {target_version}"
    return _execute_commit(message, "release")


## @brief Execute `_push_branch_with_tags` runtime logic for Git-Alias CLI.
# @details Pushes the specified local branch to `origin` using an explicit branch refspec and
#          includes `--tags` in the same push command.
# @param branch_name Local branch name resolved from configured release branches.
# @return Result emitted by `run_git_cmd` according to command contract.
def _push_branch_with_tags(branch_name):
    branch_ref = f"refs/heads/{branch_name}:refs/heads/{branch_name}"
    return run_git_cmd(["push", "origin", branch_ref, "--tags"])


## @brief Execute `_execute_release_flow` runtime logic for Git-Alias CLI.
# @details Orchestrates the full release pipeline for `major`, `minor`, and `patch` levels.
#          Branch integration is level-dependent (REQ-045):
#          - `patch`: merges `work` into `develop` and pushes `develop` only; skips `master`.
#          - `major`/`minor`: merges `work` into `develop`, pushes `develop` with tags, then merges
#            `develop` into `master` and pushes `master`.
#          Changelog flags always include `--force-write`; `patch` auto-adds `--include-patch`.
#          A temporary local `v<target>` tag is created on `work` only to generate changelog and
#          deleted immediately after changelog generation. The definitive `v<target>` tag is then
#          created on `develop` (`patch`) or `master` (`major`/`minor`) immediately before push
#          with `--tags`.
# @param level Release level string: `"major"`, `"minor"`, or `"patch"`.
# @param changelog_args Optional list of extra changelog flags forwarded alongside `--force-write`.
# @return None; raises `ReleaseError` or `VersionDetectionError` on failure.
# @satisfies REQ-026, REQ-045
def _execute_release_flow(level, changelog_args=None):
    branches = _ensure_release_prerequisites()
    rules = get_version_rules()
    if not rules:
        raise ReleaseError("No version rules configured. Cannot compute the next version.")
    root = get_git_root()
    current_version = _determine_canonical_version(root, rules)
    target_version = _bump_semver_version(current_version, level)
    release_message = f"release: Release version {target_version}"
    release_tag = f"v{target_version}"
    changelog_flags = ["--force-write"]
    if level == "patch" and "--include-patch" not in changelog_flags:
        changelog_flags.append("--include-patch")
    if changelog_args:
        for arg in changelog_args:
            if arg not in changelog_flags:
                changelog_flags.append(arg)

    print()
    _run_release_step(level, "update versions", lambda: cmd_chver([target_version]))
    _run_release_step(level, "stage files", lambda: run_git_cmd(["add", "--all"]))
    _run_release_step(level, "create release commit", lambda: _create_release_commit_for_flow(target_version))
    _run_release_step(level, "create temporary changelog tag", lambda: cmd_tg([release_message, release_tag]))
    _run_release_step(level, "regenerate changelog", lambda: cmd_changelog(changelog_flags))
    _run_release_step(level, "delete temporary changelog tag", lambda: run_git_cmd(["tag", "--delete", release_tag]))
    _run_release_step(level, "stage changelog", lambda: run_git_cmd(["add", "CHANGELOG.md"]))
    _run_release_step(level, "amend release commit", lambda: run_git_cmd(["commit", "--amend", "--no-edit"]))

    work_branch = branches["work"]
    develop_branch = branches["develop"]
    master_branch = branches["master"]

    _run_release_step(level, "checkout develop", lambda: cmd_co([develop_branch]))
    _run_release_step(level, "merge work into develop", lambda: cmd_me([work_branch]))
    if level == "patch":
        _run_release_step(level, "tag release on develop", lambda: cmd_tg([release_message, release_tag]))
        _run_release_step(level, "push develop with tags", lambda: _push_branch_with_tags(develop_branch))
    else:
        _run_release_step(level, "push develop with tags", lambda: _push_branch_with_tags(develop_branch))
        _run_release_step(level, "checkout master", lambda: cmd_co([master_branch]))
        _run_release_step(level, "merge develop into master", lambda: cmd_me([develop_branch]))
        _run_release_step(level, "tag release on master", lambda: cmd_tg([release_message, release_tag]))
        _run_release_step(level, "push master with tags", lambda: _push_branch_with_tags(master_branch))
    _run_release_step(level, "return to work", lambda: cmd_co([work_branch]))
    _run_release_step(level, "show release details", lambda: cmd_de([]))
    print(f"Release {target_version} completed successfully.")


## @brief Execute `_execute_backup_flow` runtime logic for Git-Alias CLI.
# @details Executes the `backup` workflow by reusing the release preflight checks, then
#          fast-forward merges configured `work` into configured `develop`, pushes `develop`
#          to its configured remote tracking branch, checks out back to `work`, and prints
#          an explicit success confirmation.
# @return None; raises `ReleaseError` on preflight or workflow failure.
# @satisfies REQ-047, REQ-048, REQ-049
def _execute_backup_flow():
    branches = _ensure_release_prerequisites()
    work_branch = branches["work"]
    develop_branch = branches["develop"]

    level = "backup"
    print()
    _run_release_step(level, "checkout develop", lambda: cmd_co([develop_branch]))
    _run_release_step(level, "merge work into develop", lambda: cmd_me([work_branch]))
    _run_release_step(level, "push develop", lambda: run_git_cmd(["push", "origin", develop_branch]))
    _run_release_step(level, "return to work", lambda: cmd_co([work_branch]))
    print(
        f"Backup completed successfully: all local '{work_branch}' changes were merged and pushed to remote '{develop_branch}'."
    )


## @brief Execute `_run_release_command` runtime logic for Git-Alias CLI.
# @details Executes `_run_release_command` using deterministic CLI control-flow and explicit error propagation.
# @param level Input parameter consumed by `_run_release_command`.
# @param changelog_args Input parameter consumed by `_run_release_command`.
# @return Result emitted by `_run_release_command` according to command contract.
def _run_release_command(level, changelog_args=None):
    try:
        _execute_release_flow(level, changelog_args=changelog_args)
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except VersionDetectionError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except CommandExecutionError as exc:
        err_text = CommandExecutionError._decode_stream(exc.stderr).strip()
        if err_text:
            print(err_text, file=sys.stderr)
        sys.exit(exc.returncode or 1)


## @brief Execute `_run_backup_command` runtime logic for Git-Alias CLI.
# @details Runs the `backup` workflow with the same error propagation strategy used by release commands.
# @return None; exits with status 1 on `ReleaseError`.
# @satisfies REQ-047, REQ-048, REQ-049
def _run_backup_command():
    try:
        _execute_backup_flow()
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


## @brief Execute `_run_reset_with_help` runtime logic for Git-Alias CLI.
# @details Executes `_run_reset_with_help` using deterministic CLI control-flow and explicit error propagation.
# @param base_args Input parameter consumed by `_run_reset_with_help`.
# @param extra Input parameter consumed by `_run_reset_with_help`.
# @return Result emitted by `_run_reset_with_help` according to command contract.
def _run_reset_with_help(base_args, extra):
    args = _to_args(extra)
    if "--help" in args:
        print(RESET_HELP.strip("\n"))
        return
    return run_git_cmd(base_args, args)


## @brief Execute `_reject_extra_arguments` runtime logic for Git-Alias CLI.
# @details Executes `_reject_extra_arguments` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `_reject_extra_arguments`.
# @param alias Input parameter consumed by `_reject_extra_arguments`.
# @return Result emitted by `_reject_extra_arguments` according to command contract.
def _reject_extra_arguments(extra, alias):
    args = _to_args(extra)
    if args:
        print(f"git {alias} does not accept positional arguments.", file=sys.stderr)
        sys.exit(1)


## @brief Execute `_parse_release_flags` runtime logic for Git-Alias CLI.
# @details Executes `_parse_release_flags` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `_parse_release_flags`.
# @param alias Input parameter consumed by `_parse_release_flags`.
# @return Result emitted by `_parse_release_flags` according to command contract.
def _parse_release_flags(extra, alias):
    args = _to_args(extra)
    if not args:
        return []
    allowed = {"--include-patch"}
    unknown = [arg for arg in args if arg not in allowed]
    if unknown:
        joined = ", ".join(unknown)
        print(f"git {alias} accepts only --include-patch (got {joined}).", file=sys.stderr)
        sys.exit(1)
    deduped = []
    seen = set()
    for arg in args:
        if arg not in seen:
            deduped.append(arg)
            seen.add(arg)
    return deduped


## @brief Execute `_prepare_commit_message` runtime logic for Git-Alias CLI.
# @details Executes `_prepare_commit_message` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `_prepare_commit_message`.
# @param alias Input parameter consumed by `_prepare_commit_message`.
# @return Result emitted by `_prepare_commit_message` according to command contract.
def _prepare_commit_message(extra, alias):
    args = _to_args(extra)
    if not args:
        print(f"git {alias} requires a message after the command.", file=sys.stderr)
        sys.exit(1)
    if args[0] == "--help":
        print_command_help(alias)
        sys.exit(0)
    return " ".join(args)


## @brief Execute `_build_conventional_message` runtime logic for Git-Alias CLI.
# @details Executes `_build_conventional_message` using deterministic CLI control-flow and explicit error propagation.
# @param kind Input parameter consumed by `_build_conventional_message`.
# @param extra Input parameter consumed by `_build_conventional_message`.
# @param alias Input parameter consumed by `_build_conventional_message`.
# @return Result emitted by `_build_conventional_message` according to command contract.
def _build_conventional_message(kind: str, extra, alias: str) -> str:
    text = _prepare_commit_message(extra, alias).strip()
    match = _MODULE_PREFIX_RE.match(text)
    if match:
        scope = match.group("module")
        body = match.group("body").strip()
    else:
        scope = get_config_value("default_module")
        body = text
    if not body:
        print(f"git {alias} requires text after the '<module>:' prefix to complete the message.", file=sys.stderr)
        sys.exit(1)
    return f"{kind}({scope}): {body}"


## @brief Execute `_run_conventional_commit` runtime logic for Git-Alias CLI.
# @details Executes `_run_conventional_commit` using deterministic CLI control-flow and explicit error propagation.
# @param kind Input parameter consumed by `_run_conventional_commit`.
# @param alias Input parameter consumed by `_run_conventional_commit`.
# @param extra Input parameter consumed by `_run_conventional_commit`.
# @return Result emitted by `_run_conventional_commit` according to command contract.
def _run_conventional_commit(kind: str, alias: str, extra):
    message = _build_conventional_message(kind, extra, alias)
    _ensure_commit_ready(alias)
    return _execute_commit(message, alias)


## @brief Execute `_execute_commit` runtime logic for Git-Alias CLI.
# @details Executes `_execute_commit` using deterministic CLI control-flow and explicit error propagation.
# @param message Input parameter consumed by `_execute_commit`.
# @param alias Input parameter consumed by `_execute_commit`.
# @param allow_amend Input parameter consumed by `_execute_commit`.
# @return Result emitted by `_execute_commit` according to command contract.
def _execute_commit(message, alias, allow_amend=True):
    if allow_amend:
        amend, reason = _should_amend_existing_commit()
    else:
        amend = False
        reason = "Amend is disabled for this alias."
    if amend:
        print(f"Updating the existing WIP commit (--amend). Reason: {reason}")
    else:
        print(f"Creating a new commit. Reason: {reason}")
    base = ["commit"]
    if amend:
        base.append("--amend")
    base.extend(["-F", "-"])
    try:
        return run_git_cmd(base, input=message, text=True)
    except CommandExecutionError as exc:
        status_lines = _git_status_lines()
        if has_unstaged_changes(status_lines):
            print(
                f"Unable to run git {alias}: unstaged changes are still present.",
                file=sys.stderr,
            )
            sys.exit(exc.returncode or 1)
        if not has_staged_changes(status_lines):
            print(f"Unable to run git {alias}: the staging area is empty.", file=sys.stderr)
            sys.exit(exc.returncode or 1)
        raise


## @brief Execute `upgrade_self` runtime logic for Git-Alias CLI.
# @details Executes `upgrade_self` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `upgrade_self` according to command contract.
def upgrade_self():
    _run_checked(
        [
            "uv",
            "tool",
            "install",
            "git-alias",
            "--force",
            "--from",
            "git+https://github.com/Ogekuri/G.git",
        ]
    )


## @brief Execute `remove_self` runtime logic for Git-Alias CLI.
# @details Executes `remove_self` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `remove_self` according to command contract.
def remove_self():
    _run_checked(["uv", "tool", "uninstall", "git-alias"])


## @brief Execute `cmd_aa` runtime logic for Git-Alias CLI.
# @details Executes `cmd_aa` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_aa`.
# @return Result emitted by `cmd_aa` according to command contract.
def cmd_aa(extra):
    status_lines = _git_status_lines()
    if not has_unstaged_changes(status_lines):
        print("No changes are available to add to the staging area.", file=sys.stderr)
        sys.exit(1)
    return run_git_cmd(["add", "--all"], extra)


## @brief Execute `cmd_ra` runtime logic for Git-Alias CLI.
# @details Executes `cmd_ra` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_ra`.
# @return Result emitted by `cmd_ra` according to command contract.
def cmd_ra(extra):
    if extra:
        args = _to_args(extra)
        if args == ["--help"]:
            print_command_help("ra")
            return
        print("git ra does not accept positional arguments.", file=sys.stderr)
        sys.exit(1)
    work_branch = get_branch("work")
    try:
        current_branch = _current_branch_name()
    except ReleaseError:
        print("git ra requires an active branch head.", file=sys.stderr)
        sys.exit(1)
    if current_branch != work_branch:
        print(
            f"git ra must be executed from the {work_branch} branch (current: {current_branch}).",
            file=sys.stderr,
        )
        sys.exit(1)
    _ensure_commit_ready("ra")
    return run_git_cmd(["reset", "--mixed"], [])


## @brief Execute `cmd_ar` runtime logic for Git-Alias CLI.
# @details Executes `cmd_ar` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_ar`.
# @return Result emitted by `cmd_ar` according to command contract.
def cmd_ar(extra):
    args = _to_args(extra)
    master_branch = get_branch("master")
    tag = capture_git_output(["describe", master_branch])
    filename = f"{tag}.tar.gz"
    archive_cmd = ["git", "archive", master_branch, "--prefix=/"] + args
    with subprocess.Popen(archive_cmd, stdout=subprocess.PIPE) as archive_proc:
        with open(filename, "wb") as output_io:
            gzip_proc = _run_checked(["gzip"], stdin=archive_proc.stdout, stdout=output_io)
        if archive_proc.stdout is not None:
            archive_proc.stdout.close()
        archive_proc.wait()
    return gzip_proc


## @brief Execute `cmd_br` runtime logic for Git-Alias CLI.
# @details Executes `cmd_br` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_br`.
# @return Result emitted by `cmd_br` according to command contract.
def cmd_br(extra):
    return run_git_cmd(["branch"], extra)


## @brief Execute `cmd_bd` runtime logic for Git-Alias CLI.
# @details Executes `cmd_bd` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_bd`.
# @return Result emitted by `cmd_bd` according to command contract.
def cmd_bd(extra):
    return run_git_cmd(["branch", "-d"], extra)


## @brief Execute `cmd_ck` runtime logic for Git-Alias CLI.
# @details Executes `cmd_ck` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_ck`.
# @return Result emitted by `cmd_ck` according to command contract.
def cmd_ck(extra):
    return run_git_cmd(["diff", "--check"], extra)


## @brief Execute `_ensure_commit_ready` runtime logic for Git-Alias CLI.
# @details Executes `_ensure_commit_ready` using deterministic CLI control-flow and explicit error propagation.
# @param alias Input parameter consumed by `_ensure_commit_ready`.
# @return Result emitted by `_ensure_commit_ready` according to command contract.
def _ensure_commit_ready(alias):
    status_lines = _git_status_lines()
    if has_unstaged_changes(status_lines):
        print(
            f"Unable to run git {alias}: unstaged changes are still present.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not has_staged_changes(status_lines):
        print(f"Unable to run git {alias}: the staging area is empty.", file=sys.stderr)
        sys.exit(1)
    return True


## @brief Execute `cmd_cm` runtime logic for Git-Alias CLI.
# @details Executes `cmd_cm` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_cm`.
# @return Result emitted by `cmd_cm` according to command contract.
def cmd_cm(extra):
    message = _prepare_commit_message(extra, "cm")
    _ensure_commit_ready("cm")
    return _execute_commit(message, "cm")


## @brief Execute `cmd_wip` runtime logic for Git-Alias CLI.
# @details Executes `cmd_wip` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_wip`.
# @return Result emitted by `cmd_wip` according to command contract.
def cmd_wip(extra):
    if extra:
        args = _to_args(extra)
        if args == ["--help"]:
            print_command_help("wip")
            return
        print("git wip does not accept positional arguments.", file=sys.stderr)
        sys.exit(1)
    _ensure_commit_ready("wip")
    message = "wip: work in progress."
    return _execute_commit(message, "wip")


## @brief Execute `cmd_release` runtime logic for Git-Alias CLI.
# @details Executes `cmd_release` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_release`.
# @return Result emitted by `cmd_release` according to command contract.
def cmd_release(extra):
    args = _to_args(extra)
    if args:
        if args == ["--help"]:
            print_command_help("release")
            return
        print("git release does not accept positional arguments.", file=sys.stderr)
        sys.exit(1)
    _ensure_commit_ready("release")
    rules = get_version_rules()
    if not rules:
        print("No version rules configured.", file=sys.stderr)
        sys.exit(1)
    root = get_git_root()
    try:
        version = _determine_canonical_version(root, rules)
    except VersionDetectionError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    message = f"release: Release version {version}"
    return _execute_commit(message, "release")


## @brief Execute `cmd_new` runtime logic for Git-Alias CLI.
# @details Executes `cmd_new` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_new`.
# @return Result emitted by `cmd_new` according to command contract.
def cmd_new(extra):
    return _run_conventional_commit("new", "new", extra)


## @brief Execute `cmd_refactor` runtime logic for Git-Alias CLI.
# @details Executes `cmd_refactor` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_refactor`.
# @return Result emitted by `cmd_refactor` according to command contract.
def cmd_refactor(extra):
    return _run_conventional_commit("refactor", "refactor", extra)


## @brief Execute `cmd_fix` runtime logic for Git-Alias CLI.
# @details Executes `cmd_fix` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_fix`.
# @return Result emitted by `cmd_fix` according to command contract.
def cmd_fix(extra):
    return _run_conventional_commit("fix", "fix", extra)


## @brief Execute `cmd_change` runtime logic for Git-Alias CLI.
# @details Executes `cmd_change` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_change`.
# @return Result emitted by `cmd_change` according to command contract.
def cmd_change(extra):
    return _run_conventional_commit("change", "change", extra)


## @brief Execute `cmd_implement` runtime logic for Git-Alias CLI.
# @details Executes `cmd_implement` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_implement`.
# @return Result emitted by `cmd_implement` according to command contract.
def cmd_implement(extra):
    return _run_conventional_commit("implement", "implement", extra)


## @brief Execute `cmd_docs` runtime logic for Git-Alias CLI.
# @details Executes `cmd_docs` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_docs`.
# @return Result emitted by `cmd_docs` according to command contract.
def cmd_docs(extra):
    return _run_conventional_commit("docs", "docs", extra)


## @brief Execute `cmd_style` runtime logic for Git-Alias CLI.
# @details Executes `cmd_style` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_style`.
# @return Result emitted by `cmd_style` according to command contract.
def cmd_style(extra):
    return _run_conventional_commit("style", "style", extra)


## @brief Execute `cmd_revert` runtime logic for Git-Alias CLI.
# @details Executes `cmd_revert` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_revert`.
# @return Result emitted by `cmd_revert` according to command contract.
def cmd_revert(extra):
    return _run_conventional_commit("revert", "revert", extra)


## @brief Execute `cmd_misc` runtime logic for Git-Alias CLI.
# @details Executes `cmd_misc` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_misc`.
# @return Result emitted by `cmd_misc` according to command contract.
def cmd_misc(extra):
    return _run_conventional_commit("misc", "misc", extra)


## @brief Execute `cmd_cover` runtime logic for Git-Alias CLI.
# @details Executes `cmd_cover` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_cover`.
# @return Result emitted by `cmd_cover` according to command contract.
def cmd_cover(extra):
    return _run_conventional_commit("cover", "cover", extra)


## @brief Execute `cmd_co` runtime logic for Git-Alias CLI.
# @details Executes `cmd_co` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_co`.
# @return Result emitted by `cmd_co` according to command contract.
def cmd_co(extra):
    return run_git_cmd(["checkout"], extra)


## @brief Execute `cmd_d` runtime logic for Git-Alias CLI.
# @details Executes `cmd_d` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_d`.
# @return Result emitted by `cmd_d` according to command contract.
def cmd_d(extra):
    args = _to_args(extra)
    if len(args) != 2:
        print("git d requires exactly two refs: git d <ref_a> <ref_b>", file=sys.stderr)
        sys.exit(1)
    return run_git_cmd(["difftool", "-d", args[0], args[1]])


## @brief Execute `cmd_dcc` runtime logic for Git-Alias CLI.
# @details Executes `cmd_dcc` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_dcc`.
# @return Result emitted by `cmd_dcc` according to command contract.
def cmd_dcc(extra):
    return run_git_cmd(["difftool", "-d", "HEAD~1", "HEAD"], extra)


## @brief Execute `cmd_dccc` runtime logic for Git-Alias CLI.
# @details Executes `cmd_dccc` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_dccc`.
# @return Result emitted by `cmd_dccc` according to command contract.
def cmd_dccc(extra):
    return run_git_cmd(["difftool", "-d", "HEAD~2", "HEAD"], extra)


## @brief Execute `cmd_de` runtime logic for Git-Alias CLI.
# @details Executes `cmd_de` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_de`.
# @return Result emitted by `cmd_de` according to command contract.
def cmd_de(extra):
    return run_git_cmd(["describe"], extra)


## @brief Execute `cmd_di` runtime logic for Git-Alias CLI.
# @details Executes `cmd_di` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_di`.
# @return Result emitted by `cmd_di` according to command contract.
def cmd_di(extra):
    return run_git_cmd(["checkout", "--"], extra)


## @brief Execute `cmd_diyou` runtime logic for Git-Alias CLI.
# @details Executes `cmd_diyou` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_diyou`.
# @return Result emitted by `cmd_diyou` according to command contract.
def cmd_diyou(extra):
    return run_git_cmd(["checkout", "--ours", "--"], extra)


## @brief Execute `cmd_dime` runtime logic for Git-Alias CLI.
# @details Executes `cmd_dime` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_dime`.
# @return Result emitted by `cmd_dime` according to command contract.
def cmd_dime(extra):
    return run_git_cmd(["checkout", "--theirs", "--"], extra)


## @brief Execute `cmd_dwc` runtime logic for Git-Alias CLI.
# @details Executes `cmd_dwc` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_dwc`.
# @return Result emitted by `cmd_dwc` according to command contract.
def cmd_dwc(extra):
    return run_git_cmd(["difftool", "-d", "HEAD"], extra)


## @brief Execute `cmd_dwcc` runtime logic for Git-Alias CLI.
# @details Executes `cmd_dwcc` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_dwcc`.
# @return Result emitted by `cmd_dwcc` according to command contract.
def cmd_dwcc(extra):
    return run_git_cmd(["difftool", "-d", "HEAD~1"], extra)


## @brief Execute `cmd_ed` runtime logic for Git-Alias CLI.
# @details Executes `cmd_ed` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_ed`.
# @return Result emitted by `cmd_ed` according to command contract.
def cmd_ed(extra):
    paths = _to_args(extra)
    if not paths:
        print("git ed requires at least one file path", file=sys.stderr)
        sys.exit(1)
    for path in paths:
        expanded = os.path.expanduser(path)
        run_editor_command([expanded])


## @brief Execute `cmd_fe` runtime logic for Git-Alias CLI.
# @details Executes `cmd_fe` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_fe`.
# @return Result emitted by `cmd_fe` according to command contract.
def cmd_fe(extra):
    return run_git_cmd(["fetch"], extra)


## @brief Execute `cmd_feall` runtime logic for Git-Alias CLI.
# @details Executes `cmd_feall` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_feall`.
# @return Result emitted by `cmd_feall` according to command contract.
def cmd_feall(extra):
    return cmd_fe(["--all", "--tags", "--prune"] + _to_args(extra))


## @brief Execute `cmd_gp` runtime logic for Git-Alias CLI.
# @details Executes `cmd_gp` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_gp`.
# @return Result emitted by `cmd_gp` according to command contract.
def cmd_gp(extra):
    return run_command(["gitk", "--all"] + _to_args(extra))


## @brief Execute `cmd_gr` runtime logic for Git-Alias CLI.
# @details Executes `cmd_gr` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_gr`.
# @return Result emitted by `cmd_gr` according to command contract.
def cmd_gr(extra):
    return run_command(["gitk", "--simplify-by-decoration", "--all"] + _to_args(extra))


## @brief Execute `cmd_str` runtime logic for Git-Alias CLI.
# @details Executes `cmd_str` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_str`.
# @return Result emitted by `cmd_str` according to command contract.
def cmd_str(extra):
    # @details Query git remotes with transport metadata.
    result = run_git_text(["remote", "-v"])
    lines = result.strip().split("\n")
    
    # @details Deduplicate remote names from `git remote -v` rows.
    remotes = set()
    for line in lines:
        if line.strip():
            parts = line.split()
            if parts:
                remote_name = parts[0]
                remotes.add(remote_name)
    
    # @details Print normalized remote name inventory.
    print("Remotes found:")
    for remote in sorted(remotes):
        print(f"  {remote}")
    print()
    
    # @details Print detailed status for each unique remote.
    for remote in sorted(remotes):
        print(f"--- Status for '{remote}' ---")
        try:
            run_git_cmd(["remote", "show", remote])
        except CommandExecutionError:
            print(f"Error showing status for '{remote}'", file=sys.stderr)
            raise


## @brief Execute `cmd_lb` runtime logic for Git-Alias CLI.
# @details Executes `cmd_lb` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_lb`.
# @return Result emitted by `cmd_lb` according to command contract.
def cmd_lb(extra):
    return run_git_cmd(["branch", "-v", "-a"], extra)


## @brief Execute `cmd_lg` runtime logic for Git-Alias CLI.
# @details Executes `cmd_lg` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_lg`.
# @return Result emitted by `cmd_lg` according to command contract.
def cmd_lg(extra):
    return run_git_cmd(
        [
            "log",
            "--graph",
            "--abbrev-commit",
            "--decorate",
            "--format=format:%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(bold yellow)%d%C(reset)",
            "--all",
        ],
        extra,
    )


## @brief Execute `cmd_lh` runtime logic for Git-Alias CLI.
# @details Executes `cmd_lh` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_lh`.
# @return Result emitted by `cmd_lh` according to command contract.
def cmd_lh(extra):
    return run_git_cmd(["log", "-1", "HEAD"], extra)


## @brief Execute `cmd_ll` runtime logic for Git-Alias CLI.
# @details Executes `cmd_ll` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_ll`.
# @return Result emitted by `cmd_ll` according to command contract.
def cmd_ll(extra):
    return run_git_cmd(
        [
            "log",
            "--graph",
            "--decorate",
            "--format=format:%C(bold blue)%H%C(reset) - %C(bold cyan)%aD%C(reset) %C(bold green)(%ar)%C(reset)%C(bold yellow)%d%C(reset)%n %C(white)%s%C(reset) %C(dim white)- %an%C(reset)",
            "--all",
        ],
        extra,
    )


## @brief Execute `cmd_lm` runtime logic for Git-Alias CLI.
# @details Executes `cmd_lm` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_lm`.
# @return Result emitted by `cmd_lm` according to command contract.
def cmd_lm(extra):
    return run_git_cmd(["log", "--merges"], extra)


## @brief Execute `cmd_lt` runtime logic for Git-Alias CLI.
# @details Enumerates tags via `git tag -l`, resolves containing refs via `git branch -a --contains <tag>`,
#          trims branch markers/prefixes from git output, and prints deterministic `<tag>: <branch_1>, <branch_2>, ...` lines.
# @param extra Input parameter consumed by `cmd_lt`.
# @return Result emitted by `cmd_lt` according to command contract.
def cmd_lt(extra):
    tags_text = capture_git_output(["tag", "-l", *_to_args(extra)])
    tags = [tag.strip() for tag in tags_text.splitlines() if tag.strip()]
    for tag in tags:
        branches_text = capture_git_output(["branch", "-a", "--contains", tag])
        branches = []
        for branch_line in branches_text.splitlines():
            branch = branch_line.strip()
            if not branch:
                continue
            if branch.startswith("*"):
                branch = branch.lstrip("*").strip()
            if branch.startswith("remotes/"):
                branch = branch[len("remotes/") :]
            if " -> " in branch:
                continue
            branches.append(branch)
        print(f"{tag}: {', '.join(branches)}" if branches else f"{tag}:")


## @brief Execute `cmd_me` runtime logic for Git-Alias CLI.
# @details Executes `cmd_me` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_me`.
# @return Result emitted by `cmd_me` according to command contract.
def cmd_me(extra):
    return run_git_cmd(["merge", "--ff-only"], extra)


## @brief Execute `cmd_pl` runtime logic for Git-Alias CLI.
# @details Executes `cmd_pl` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_pl`.
# @return Result emitted by `cmd_pl` according to command contract.
def cmd_pl(extra):
    return run_git_cmd(["pull", "--ff-only"], extra)


## @brief Execute `cmd_pt` runtime logic for Git-Alias CLI.
# @details Executes `cmd_pt` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_pt`.
# @return Result emitted by `cmd_pt` according to command contract.
def cmd_pt(extra):
    return run_git_cmd(["push", "--tags"], extra)


## @brief Execute `cmd_pu` runtime logic for Git-Alias CLI.
# @details Executes `cmd_pu` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_pu`.
# @return Result emitted by `cmd_pu` according to command contract.
def cmd_pu(extra):
    return run_git_cmd(["push", "-u"], extra)


## @brief Execute `cmd_rf` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rf` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rf`.
# @return Result emitted by `cmd_rf` according to command contract.
def cmd_rf(extra):
    return run_git_cmd(["reflog"], extra)


## @brief Execute `cmd_rmtg` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rmtg` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rmtg`.
# @return Result emitted by `cmd_rmtg` according to command contract.
def cmd_rmtg(extra):
    args = _to_args(extra)
    if not args:
        print("usage: git rmtg \"<tag>\"", file=sys.stderr)
        sys.exit(1)
    tag = args[0]
    tail = args[1:]
    run_git_cmd(["tag", "--delete", tag])
    return run_git_cmd(["push", "--delete", "origin", tag], tail)


## @brief Execute `cmd_rmloc` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rmloc` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rmloc`.
# @return Result emitted by `cmd_rmloc` according to command contract.
def cmd_rmloc(extra):
    return run_git_cmd(["reset", "--hard", "--"], extra)


## @brief Execute `cmd_rmstg` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rmstg` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rmstg`.
# @return Result emitted by `cmd_rmstg` according to command contract.
def cmd_rmstg(extra):
    return run_git_cmd(["rm", "--cached", "--"], extra)


## @brief Execute `cmd_rmunt` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rmunt` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rmunt`.
# @return Result emitted by `cmd_rmunt` according to command contract.
def cmd_rmunt(extra):
    return run_git_cmd(["clean", "-d", "-f", "--"], extra)


## @brief Execute `cmd_rs` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rs` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rs`.
# @return Result emitted by `cmd_rs` according to command contract.
def cmd_rs(extra):
    return _run_reset_with_help(["reset", "--hard", "HEAD"], extra)


## @brief Execute `cmd_rssft` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rssft` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rssft`.
# @return Result emitted by `cmd_rssft` according to command contract.
def cmd_rssft(extra):
    return _run_reset_with_help(["reset", "--soft", "--"], extra)


## @brief Execute `cmd_rsmix` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rsmix` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rsmix`.
# @return Result emitted by `cmd_rsmix` according to command contract.
def cmd_rsmix(extra):
    return _run_reset_with_help(["reset", "--mixed", "--"], extra)


## @brief Execute `cmd_rshrd` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rshrd` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rshrd`.
# @return Result emitted by `cmd_rshrd` according to command contract.
def cmd_rshrd(extra):
    return _run_reset_with_help(["reset", "--hard", "--"], extra)


## @brief Execute `cmd_rsmrg` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rsmrg` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rsmrg`.
# @return Result emitted by `cmd_rsmrg` according to command contract.
def cmd_rsmrg(extra):
    return _run_reset_with_help(["reset", "--merge", "--"], extra)


## @brief Execute `cmd_rskep` runtime logic for Git-Alias CLI.
# @details Executes `cmd_rskep` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_rskep`.
# @return Result emitted by `cmd_rskep` according to command contract.
def cmd_rskep(extra):
    return _run_reset_with_help(["reset", "--keep", "--"], extra)


## @brief Execute `cmd_st` runtime logic for Git-Alias CLI.
# @details Executes `cmd_st` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_st`.
# @return Result emitted by `cmd_st` according to command contract.
def cmd_st(extra):
    return run_git_cmd(["status"], extra)


## @brief Execute `cmd_tg` runtime logic for Git-Alias CLI.
# @details Executes `cmd_tg` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_tg`.
# @return Result emitted by `cmd_tg` according to command contract.
def cmd_tg(extra):
    return run_git_cmd(["tag", "-a", "-m"], extra)


## @brief Execute `cmd_unstg` runtime logic for Git-Alias CLI.
# @details Executes `cmd_unstg` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_unstg`.
# @return Result emitted by `cmd_unstg` according to command contract.
def cmd_unstg(extra):
    return run_git_cmd(["reset", "--mixed", "--"], extra)


## @brief Execute `cmd_ver` runtime logic for Git-Alias CLI.
# @details Executes `cmd_ver` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_ver`.
# @return Result emitted by `cmd_ver` according to command contract.
def cmd_ver(extra):
    args = _to_args(extra)
    verbose = "--verbose" in args
    debug = "--debug" in args
    if debug:
        verbose = True
    root = get_git_root()
    rules = get_version_rules()
    if not rules:
        print("No version rules configured.", file=sys.stderr)
        sys.exit(1)
    try:
        inventory = _build_version_file_inventory(root)
        contexts = _prepare_version_rule_contexts(root, rules, inventory=inventory)
        canonical = _determine_canonical_version(
            root,
            rules,
            verbose=verbose,
            debug=debug,
            contexts=contexts,
        )
    except VersionDetectionError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(canonical)


## @brief Execute `cmd_chver` runtime logic for Git-Alias CLI.
# @details Executes `cmd_chver` using deterministic CLI control-flow and explicit error propagation.
# @param extra Input parameter consumed by `cmd_chver`.
# @return Result emitted by `cmd_chver` according to command contract.
def cmd_chver(extra):
    args = _to_args(extra)
    if len(args) != 1:
        print("usage: git chver <major.minor.patch>", file=sys.stderr)
        sys.exit(1)
    requested = args[0].strip()
    target_tuple = _parse_semver_tuple(requested)
    if not target_tuple:
        print("Please provide the version in the format <major>.<minor>.<patch> (e.g. 1.2.3).", file=sys.stderr)
        sys.exit(1)
    root = get_git_root()
    rules = get_version_rules()
    if not rules:
        print("No version rules configured.", file=sys.stderr)
        sys.exit(1)
    text_cache: Dict[Path, str] = {}
    try:
        inventory = _build_version_file_inventory(root)
        contexts = _prepare_version_rule_contexts(root, rules, inventory=inventory)
        current = _determine_canonical_version(
            root,
            rules,
            contexts=contexts,
            text_cache=text_cache,
        )
    except VersionDetectionError as exc:
        print(f"Unable to determine the current version: {exc}", file=sys.stderr)
        sys.exit(1)
    current_tuple = _parse_semver_tuple(current)
    if current_tuple is None:
        print(f"The current version '{current}' is not a valid semantic version.", file=sys.stderr)
        sys.exit(1)
    if requested == current:
        print(f"The project version is already {current}.")
        return
    action = "Upgrade" if target_tuple > current_tuple else "Downgrade"
    replacements = 0
    for context in contexts:
        for file_path in context.files:
            text = _read_version_file_text(file_path, text_cache=text_cache)
            if text is None:
                continue
            new_text, count = _replace_versions_in_text(text, context.compiled_regex, requested)
            if count:
                try:
                    file_path.write_text(new_text, encoding="utf-8")
                except OSError as exc:
                    print(f"Unable to write {file_path}: {exc}", file=sys.stderr)
                    sys.exit(1)
                text_cache[file_path] = new_text
                replacements += count
    if replacements == 0:
        print("No version entries were updated. Ensure ver_rules match the desired files.", file=sys.stderr)
        sys.exit(1)
    try:
        confirmed = _determine_canonical_version(
            root,
            rules,
            contexts=contexts,
            text_cache=text_cache,
        )
    except VersionDetectionError as exc:
        print(f"Fatal error after updating versions: {exc}", file=sys.stderr)
        sys.exit(1)
    if confirmed != requested:
        print(
            f"Fatal error: the updated files report version {confirmed} instead of {requested}.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"{action} completed: version is now {confirmed}.")


## @brief CLI entry-point for the `major` release subcommand.
# @details Increments the major semver index (resets minor and patch to 0), merges and pushes
#          to both configured `develop` and `master` branches, regenerates changelog via a
#          temporary local tag on `work`, and creates the definitive release tag on `master`
#          immediately before pushing `master` with `--tags`.
# @param extra Iterable of CLI argument strings; accepted flag: `--include-patch`.
# @return None; delegates to `_run_release_command("major", ...)`.
# @satisfies REQ-026, REQ-045
def cmd_major(extra):
    changelog_args = _parse_release_flags(extra, "major")
    _run_release_command("major", changelog_args=changelog_args)


## @brief CLI entry-point for the `minor` release subcommand.
# @details Increments the minor semver index (resets patch to 0), merges and pushes to both
#          configured `develop` and `master` branches, regenerates changelog via a temporary local
#          tag on `work`, and creates the definitive release tag on `master` immediately before
#          pushing `master` with `--tags`.
# @param extra Iterable of CLI argument strings; accepted flag: `--include-patch`.
# @return None; delegates to `_run_release_command("minor", ...)`.
# @satisfies REQ-026, REQ-045
def cmd_minor(extra):
    changelog_args = _parse_release_flags(extra, "minor")
    _run_release_command("minor", changelog_args=changelog_args)


## @brief CLI entry-point for the `patch` release subcommand.
# @details Increments the patch semver index, merges and pushes to configured `develop` only
#          (MUST NOT merge or push to `master`), regenerates changelog via a temporary local tag
#          on `work`, and creates the definitive release tag on `develop` immediately before
#          pushing `develop` with `--tags`; `--include-patch` is auto-included.
# @param extra Iterable of CLI argument strings; accepted flag: `--include-patch`.
# @return None; delegates to `_run_release_command("patch", ...)`.
# @satisfies REQ-026, REQ-045
def cmd_patch(extra):
    changelog_args = _parse_release_flags(extra, "patch")
    _run_release_command("patch", changelog_args=changelog_args)


## @brief CLI entry-point for the `backup` workflow subcommand.
# @details Runs the same preflight checks used by `major`/`minor`/`patch`, then integrates the
#          configured `work` branch into the configured `develop` branch and pushes `develop`
#          to its remote tracking branch before returning to `work`.
# @param extra Iterable of CLI argument strings; accepted token: `--help` only.
# @return None; delegates to `_run_backup_command()`.
# @satisfies REQ-047, REQ-048, REQ-049
def cmd_backup(extra):
    args = _to_args(extra)
    if args == ["--help"]:
        print_command_help("backup")
        return
    if args:
        print("git backup does not accept positional arguments.", file=sys.stderr)
        sys.exit(1)
    _run_backup_command()


## @brief CLI entry-point for the `changelog` subcommand.
# @details Parses flags, delegates to `generate_changelog_document`, and writes or prints the result.
#          Accepted flags: `--include-patch`, `--force-write`, `--print-only`,
#          `--disable-history`, `--help`.
#          Exits with status 2 on argument errors or when not inside a git repository.
#          Exits with status 1 when `CHANGELOG.md` already exists and `--force-write` was not supplied.
# @param extra Iterable of CLI argument strings following the `changelog` subcommand token.
# @return None; side-effects: writes `CHANGELOG.md` to disk or prints to stdout.
# @satisfies REQ-018, REQ-040, REQ-041, REQ-043
def cmd_changelog(extra):
    parser = argparse.ArgumentParser(prog="g changelog", add_help=False)
    parser.add_argument("--force-write", dest="force_write", action="store_true")
    parser.add_argument("--include-patch", dest="include_patch", action="store_true")
    parser.add_argument("--print-only", action="store_true")
    parser.add_argument("--disable-history", dest="disable_history", action="store_true")
    parser.add_argument("--help", action="store_true")
    try:
        args = parser.parse_args(list(extra))
    except SystemExit:
        print("Invalid arguments for g changelog.", file=sys.stderr)
        sys.exit(2)
    if args.help:
        print_command_help("changelog")
        return
    if not is_inside_git_repo():
        print("Error: run g changelog inside a Git repository.", file=sys.stderr)
        sys.exit(2)
    repo_root = get_git_root()
    content = generate_changelog_document(repo_root, args.include_patch, args.disable_history)
    if args.print_only:
        print(content, end="")
        return
    destination = Path(repo_root) / "CHANGELOG.md"
    if destination.exists() and not args.force_write:
        print(
            "CHANGELOG.md already exists. Use --force-write to overwrite it or --print-only to show the new content.",
            file=sys.stderr,
        )
        sys.exit(1)
    destination.write_text(content, encoding="utf-8")
    print(f"\nGenerated file: {destination}")

## @brief Constant `COMMANDS` used by CLI runtime paths and policies.

COMMANDS = {
    "aa": cmd_aa,
    "ar": cmd_ar,
    "backup": cmd_backup,
    "bd": cmd_bd,
    "br": cmd_br,
    "chver": cmd_chver,
    "changelog": cmd_changelog,
    "change": cmd_change,
    "implement": cmd_implement,
    "ck": cmd_ck,
    "cm": cmd_cm,
    "co": cmd_co,
    "d": cmd_d,
    "dcc": cmd_dcc,
    "dccc": cmd_dccc,
    "de": cmd_de,
    "di": cmd_di,
    "dime": cmd_dime,
    "diyou": cmd_diyou,
    "docs": cmd_docs,
    "dwc": cmd_dwc,
    "dwcc": cmd_dwcc,
    "ed": cmd_ed,
    "fix": cmd_fix,
    "fe": cmd_fe,
    "feall": cmd_feall,
    "gp": cmd_gp,
    "gr": cmd_gr,
    "lb": cmd_lb,
    "lg": cmd_lg,
    "lh": cmd_lh,
    "ll": cmd_ll,
    "lm": cmd_lm,
    "lt": cmd_lt,
    "major": cmd_major,
    "misc": cmd_misc,
    "me": cmd_me,
    "minor": cmd_minor,
    "new": cmd_new,
    "cover": cmd_cover,
    "str": cmd_str,
    "refactor": cmd_refactor,
    "patch": cmd_patch,
    "ra": cmd_ra,
    "pl": cmd_pl,
    "pt": cmd_pt,
    "pu": cmd_pu,
    "revert": cmd_revert,
    "rf": cmd_rf,
    "rmloc": cmd_rmloc,
    "rmstg": cmd_rmstg,
    "rmtg": cmd_rmtg,
    "rmunt": cmd_rmunt,
    "rs": cmd_rs,
    "rshrd": cmd_rshrd,
    "rskep": cmd_rskep,
    "rsmix": cmd_rsmix,
    "rsmrg": cmd_rsmrg,
    "rssft": cmd_rssft,
    "st": cmd_st,
    "tg": cmd_tg,
    "unstg": cmd_unstg,
    "wip": cmd_wip,
    "ver": cmd_ver,
    "style": cmd_style,
}

## @brief Execute `print_command_help` runtime logic for Git-Alias CLI.
# @details Executes `print_command_help` using deterministic CLI control-flow and explicit error propagation.
# @param name Input parameter consumed by `print_command_help`.
# @param width Input parameter consumed by `print_command_help`.
# @return Result emitted by `print_command_help` according to command contract.
def print_command_help(name, width=None):
    description = HELP_TEXTS.get(name, "No help text is available for this command.")
    if width is None:
        print(f"{name} - {description}")
    else:
        print(f"{name.ljust(width)} - {description}")

## @brief Execute `print_all_help` runtime logic for Git-Alias CLI.
# @details Executes `print_all_help` using deterministic CLI control-flow and explicit error propagation.
# @return Result emitted by `print_all_help` according to command contract.
def print_all_help():
    print(f"Usage: g <command> [options] ({get_cli_version()})")
    print()
    print("Management Commands:")
    for flag, description in MANAGEMENT_HELP:
        print(f"  {flag} - {description}")
    print()
    print("Configuration Parameters:")
    for key in DEFAULT_CONFIG:
        value = CONFIG.get(key, DEFAULT_CONFIG[key])
        if key == "ver_rules":
            print("  ver_rules:")
            if isinstance(value, list):
                entries = value
            else:
                entries = []
            for entry in entries:
                pattern = ""
                regex = ""
                if isinstance(entry, dict):
                    pattern = entry.get("pattern") or entry.get("glob") or ""
                    regex = entry.get("regex") or ""
                elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                    pattern, regex = entry[0], entry[1]
                print(f"    - pattern={pattern} regex={regex}")
        else:
            print(f"  {key} = {value}")
    print()
    print("Commands:")
    help_width = max(len(name) for name in HELP_TEXTS)
    for name in sorted(COMMANDS.keys()):
        print("  ", end="")
        print_command_help(name, width=help_width)


## @brief Execute `main` runtime logic for Git-Alias CLI.
# @details Executes `main` using deterministic CLI control-flow and explicit error propagation.
# @param argv Input parameter consumed by `main`.
# @param check_updates Input parameter consumed by `main`.
# @return Result emitted by `main` according to command contract.
def main(argv=None, *, check_updates: bool = True):
    args = list(argv) if argv is not None else sys.argv[1:]
    git_root = get_git_root()
    load_cli_config(git_root)
    if not args:
        print("Please provide a command or --help", file=sys.stderr)
        print_all_help()
        sys.exit(1)
    if args[0] == "--help" and len(args) > 1 and args[1] not in COMMANDS:
        print(f"Unknown command: {args[1]}", file=sys.stderr)
        sys.exit(1)
    if check_updates:
        check_for_newer_version(timeout_seconds=1.0)
    if args[0] in ("--ver", "--version"):
        print(get_cli_version())
        return
    if args[0] == "--write-config":
        write_default_config(git_root)
        return
    if args[0] == "--upgrade":
        upgrade_self()
        return
    if args[0] == "--remove":
        remove_self()
        return
    if args[0] == "--help":
        if len(args) == 1:
            print_all_help()
            return
        name = args[1]
        if name in COMMANDS:
            print_command_help(name)
        return
    name = args[0]
    extras = args[1:]
    try:
        if name not in COMMANDS:
            run_git_cmd([name], extras)
            return
        if "--help" in extras:
            if name in RESET_HELP_COMMANDS:
                COMMANDS[name](extras)
            else:
                print_command_help(name)
            return
        COMMANDS[name](extras)
    except CommandExecutionError as exc:
        err_text = CommandExecutionError._decode_stream(exc.stderr).strip()
        if err_text:
            print(err_text, file=sys.stderr)
        sys.exit(exc.returncode or 1)
