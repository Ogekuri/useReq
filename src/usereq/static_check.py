"""!
@file static_check.py
@brief Static code analysis dispatch module implementing Dummy/Pylance/Ruff/Command check classes.
@details Provides a class hierarchy for running static analysis tools against resolved file lists.
  Exposes `run_static_check(argv)` as the primary entry point called from cli.py.
  Class hierarchy: StaticCheckBase (Dummy) -> StaticCheckPylance, StaticCheckRuff, StaticCheckCommand.
  File resolution supports: explicit file paths, glob patterns (with full `**` recursive expansion),
  and direct-children-only directory traversal. No custom `--recursive` flag; recursive traversal
  is expressed via `**` glob syntax (e.g., `src/**/*.py`).
@author useReq
@version 0.0.71
"""

from __future__ import annotations

import glob
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .cli import ReqError


# ---------------------------------------------------------------------------
# File resolution helpers
# ---------------------------------------------------------------------------

def _resolve_files(inputs: Sequence[str]) -> List[str]:
    """!
    @brief Resolve a mixed list of paths, glob patterns, and directories into regular files.
    @param inputs Sequence of raw path strings (file, directory, or glob pattern).
    @return Sorted deduplicated list of resolved absolute file paths (regular files only).
    @details
      Resolution order per element:
      1. If the element contains a glob wildcard character (`*`, `?`, `[`) expand via
         `glob.glob(entry, recursive=True)`, enabling full `**` recursive expansion
         (e.g., `src/**/*.py` matches all `.py` files under `src/` at any depth).
      2. If the element is an existing directory, iterate direct children only (flat traversal).
      3. Otherwise treat as a literal file path; include if it is a regular file.
      Symlinks to regular files are included. Non-existent paths that do not match a glob produce
      a warning on stderr and are skipped.
    """
    resolved: dict[str, None] = {}  # ordered set via dict

    for entry in inputs:
        if any(c in entry for c in ("*", "?", "[")):
            # Glob pattern; recursive=True enables ** expansion (SRS-245)
            matches = glob.glob(entry, recursive=True)
            for m in sorted(matches):
                p = Path(m)
                if p.is_file():
                    resolved[str(p.resolve())] = None
        else:
            p = Path(entry)
            if p.is_dir():
                # Direct children only; recursive traversal is expressed via ** glob patterns
                for child in sorted(p.iterdir()):
                    if child.is_file():
                        resolved[str(child.resolve())] = None
            elif p.is_file():
                resolved[str(p.resolve())] = None
            else:
                print(
                    f"  Warning: skipping (not found or not a file): {entry}",
                    file=sys.stderr,
                )

    return list(resolved.keys())


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class StaticCheckBase:
    """!
    @brief Dummy static-check class; base of the static analysis class hierarchy.
    @details Iterates over resolved input files and emits a per-file header line plus `Result: OK`.
      Subclasses override `_check_file` to provide tool-specific logic.
      File resolution is delegated to `_resolve_files`.
    """

    #: Tool label used in the header line. Subclasses override this.
    LABEL: str = "Dummy"

    def __init__(
        self,
        inputs: Sequence[str],
        extra_args: Optional[Sequence[str]] = None,
    ) -> None:
        """!
        @brief Initialize the static checker with resolved inputs and options.
        @param inputs Raw path/pattern/directory entries from CLI.
        @param extra_args Additional CLI arguments forwarded to the external tool (may be None).
        @details Resolves `inputs` immediately into `self._files` via `_resolve_files`.
          Recursive traversal is expressed via `**` glob patterns in `inputs` (e.g., `src/**/*.py`);
          no separate recursive flag exists (SRS-240, SRS-245).
        """
        self._extra_args: List[str] = list(extra_args) if extra_args else []
        self._files = _resolve_files(inputs)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> int:
        """!
        @brief Execute the static check for all resolved files.
        @return Exit code: 0 if all files pass (or file list is empty), 1 if any file fails.
        @details
          If the resolved file list is empty a warning is printed to stderr and 0 is returned.
          For each file `_check_file` is called; the overall return code is the maximum of all
          per-file return codes (0 = all OK, 1 = at least one FAIL).
        """
        if not self._files:
            print(
                "  Warning: no files resolved for static check.",
                file=sys.stderr,
            )
            return 0

        overall = 0
        for filepath in self._files:
            rc = self._check_file(filepath)
            if rc != 0:
                overall = 1
        return overall

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _header_line(self, filepath: str) -> str:
        """!
        @brief Build the per-file header line for output.
        @param filepath Absolute path of the file being checked.
        @return Formatted header string including label, filename, and extra args.
        @details Format: `# Static-Check(<LABEL>): <filepath> [<extra_args>]`.
          When `extra_args` is empty the bracket section is omitted.
        """
        opts = f" [{' '.join(self._extra_args)}]" if self._extra_args else ""
        return f"# Static-Check({self.LABEL}): {filepath}{opts}"

    def _check_file(self, filepath: str) -> int:
        """!
        @brief Perform the static analysis for a single file.
        @param filepath Absolute path of the file to check.
        @return 0 on pass, non-zero on failure.
        @details Base implementation (Dummy): always prints the header and `Result: OK`.
          Subclasses override this method to invoke external tools.
        """
        print(self._header_line(filepath))
        print("Result: OK")
        return 0


# ---------------------------------------------------------------------------
# Pylance (pyright) checker
# ---------------------------------------------------------------------------

class StaticCheckPylance(StaticCheckBase):
    """!
    @brief Pylance static-check class; runs pyright on each resolved file.
    @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke `pyright`
      as a subprocess and parse its exit code.
      Header label: `Pylance`.
      Evidence block is emitted on failure by concatenating stdout and stderr from pyright.
    @see StaticCheckBase
    """

    LABEL = "Pylance"

    def _check_file(self, filepath: str) -> int:
        """!
        @brief Run pyright on `filepath` and emit OK or FAIL with evidence.
        @param filepath Absolute path of the file to analyse with pyright.
        @return 0 when pyright exits 0, 1 otherwise.
        @details
          Invokes `pyright <filepath> [extra_args...]`.
          Captures combined stdout+stderr.
          On exit code 0 prints `Result: OK`.
          On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
        @exception ReqError Not raised; subprocess errors are surfaced as FAIL evidence.
        """
        print(self._header_line(filepath))
        cmd = ["pyright", filepath] + self._extra_args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            print("Result: FAIL")
            print("Evidence:")
            print("  pyright not found on PATH")
            return 1

        if result.returncode == 0:
            print("Result: OK")
            return 0
        else:
            print("Result: FAIL")
            print("Evidence:")
            evidence = (result.stdout or "") + (result.stderr or "")
            print(evidence.rstrip())
            return 1


# ---------------------------------------------------------------------------
# Ruff checker
# ---------------------------------------------------------------------------

class StaticCheckRuff(StaticCheckBase):
    """!
    @brief Ruff static-check class; runs `ruff check` on each resolved file.
    @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke `ruff check`
      as a subprocess and parse its exit code.
      Header label: `Ruff`.
      Evidence block is emitted on failure by concatenating stdout and stderr from ruff.
    @see StaticCheckBase
    """

    LABEL = "Ruff"

    def _check_file(self, filepath: str) -> int:
        """!
        @brief Run `ruff check` on `filepath` and emit OK or FAIL with evidence.
        @param filepath Absolute path of the file to analyse with ruff.
        @return 0 when ruff exits 0, 1 otherwise.
        @details
          Invokes `ruff check <filepath> [extra_args...]`.
          Captures combined stdout+stderr.
          On exit code 0 prints `Result: OK`.
          On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
        @exception ReqError Not raised; subprocess errors are surfaced as FAIL evidence.
        """
        print(self._header_line(filepath))
        cmd = ["ruff", "check", filepath] + self._extra_args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            print("Result: FAIL")
            print("Evidence:")
            print("  ruff not found on PATH")
            return 1

        if result.returncode == 0:
            print("Result: OK")
            return 0
        else:
            print("Result: FAIL")
            print("Evidence:")
            evidence = (result.stdout or "") + (result.stderr or "")
            print(evidence.rstrip())
            return 1


# ---------------------------------------------------------------------------
# Arbitrary external command checker
# ---------------------------------------------------------------------------

class StaticCheckCommand(StaticCheckBase):
    """!
    @brief Command static-check class; runs an arbitrary external command on each resolved file.
    @details Derived from `StaticCheckBase`; overrides `_check_file` to invoke the user-supplied
      `cmd` as a subprocess.
      Header label: `Command[<cmd>]`.
      Before processing files the constructor verifies that `cmd` is available on PATH via
      `shutil.which`; raises `ReqError(code=1)` if the command is not found.
    @see StaticCheckBase
    """

    def __init__(
        self,
        cmd: str,
        inputs: Sequence[str],
        extra_args: Optional[Sequence[str]] = None,
    ) -> None:
        """!
        @brief Initialize the command checker and verify tool availability.
        @param cmd External command name (must be available on PATH).
        @param inputs Raw path/pattern/directory entries from CLI.
        @param extra_args Additional CLI arguments forwarded to the external command.
        @throws ReqError If `cmd` is not found on PATH (exit code 1).
        @details Calls `shutil.which(cmd)` before delegating to the parent constructor.
          Sets `LABEL` dynamically to `Command[<cmd>]`.
        """
        if not shutil.which(cmd):
            raise ReqError(
                f"Error: external command '{cmd}' not found on PATH.", 1
            )
        self._cmd = cmd
        self.LABEL = f"Command[{cmd}]"
        super().__init__(inputs=inputs, extra_args=extra_args)

    def _check_file(self, filepath: str) -> int:
        """!
        @brief Run the external command on `filepath` and emit OK or FAIL with evidence.
        @param filepath Absolute path of the file to analyse.
        @return 0 when the command exits 0, 1 otherwise.
        @details
          Invokes `<cmd> <filepath> [extra_args...]`.
          Captures combined stdout+stderr.
          On exit code 0 prints `Result: OK`.
          On non-zero exit code prints `Result: FAIL`, `Evidence:`, and the captured output.
        """
        print(self._header_line(filepath))
        cmd = [self._cmd, filepath] + self._extra_args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            print("Result: FAIL")
            print("Evidence:")
            print(f"  command '{self._cmd}' not found on PATH")
            return 1

        if result.returncode == 0:
            print("Result: OK")
            return 0
        else:
            print("Result: FAIL")
            print("Evidence:")
            evidence = (result.stdout or "") + (result.stderr or "")
            print(evidence.rstrip())
            return 1


# ---------------------------------------------------------------------------
# CLI dispatcher
# ---------------------------------------------------------------------------

def run_static_check(argv: Sequence[str]) -> int:
    """!
    @brief Parse `--test-static-check` sub-argv and dispatch to the appropriate checker class.
    @param argv Remaining argument tokens after `--test-static-check` (i.e. [subcommand, ...]).
    @return Process exit code from the selected checker's `run()` method.
    @throws ReqError If subcommand is missing, unknown, or `command` subcommand is missing `cmd`.
    @details
      Expected argument format:
      - `dummy [FILES...]`
      - `pylance [FILES...]`
      - `ruff [FILES...]`
      - `command <cmd> [FILES...]`

      No custom `--recursive` flag is parsed; recursive traversal is expressed via `**` glob
      patterns in `[FILES]` (e.g., `src/**/*.py`).
      For `command`, the first token after `command` is treated as `<cmd>`.
      All remaining tokens (after subcommand and optional cmd) are treated as FILES.

      Dispatches to:
      - `dummy`   -> `StaticCheckBase`
      - `pylance` -> `StaticCheckPylance`
      - `ruff`    -> `StaticCheckRuff`
      - `command` -> `StaticCheckCommand`
    """
    tokens = list(argv)
    if not tokens:
        raise ReqError(
            "Error: --test-static-check requires a subcommand: dummy, pylance, ruff, command.",
            1,
        )

    subcommand = tokens.pop(0)
    remaining = tokens

    if subcommand == "dummy":
        checker: StaticCheckBase = StaticCheckBase(
            inputs=remaining,
        )
    elif subcommand == "pylance":
        checker = StaticCheckPylance(
            inputs=remaining,
        )
    elif subcommand == "ruff":
        checker = StaticCheckRuff(
            inputs=remaining,
        )
    elif subcommand == "command":
        if not remaining:
            raise ReqError(
                "Error: --test-static-check command requires a <cmd> argument.", 1
            )
        cmd = remaining[0]
        remaining = remaining[1:]
        checker = StaticCheckCommand(
            cmd=cmd,
            inputs=remaining,
        )
    else:
        raise ReqError(
            f"Error: unknown --test-static-check subcommand '{subcommand}'. "
            "Valid subcommands: dummy, pylance, ruff, command.",
            1,
        )

    return checker.run()
