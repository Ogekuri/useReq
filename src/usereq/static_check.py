"""!
@file static_check.py
@brief Static code analysis dispatch module implementing Dummy/Pylance/Ruff/Command check classes.
@details Provides a class hierarchy for running static analysis tools against resolved file lists.
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
# Language configuration constants (SRS-258, SRS-259)
# ---------------------------------------------------------------------------

STATIC_CHECK_LANG_CANONICAL: dict[str, str] = {
    "python": "Python",
    "c": "C",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "rust": "Rust",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "java": "Java",
    "go": "Go",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "lua": "Lua",
    "shell": "Shell",
    "sh": "Shell",
    "perl": "Perl",
    "haskell": "Haskell",
    "zig": "Zig",
    "elixir": "Elixir",
}
"""!
@brief Maps lowercase language identifiers (including aliases) to canonical language names.
@details Covers all 20 languages from SRS-249 plus common aliases (cpp, csharp, js, ts, sh).
  Canonical names: Python, C, C++, C#, Rust, JavaScript, TypeScript, Java, Go, Ruby,
  PHP, Swift, Kotlin, Scala, Lua, Shell, Perl, Haskell, Zig, Elixir.
  Lookup MUST be performed on `value.strip().lower()` of the user-supplied language token.
@see SRS-258, SRS-249
"""

STATIC_CHECK_EXT_TO_LANG: dict[str, str] = {
    ".py": "Python",
    ".c": "C",
    ".cpp": "C++",
    ".cs": "C#",
    ".rs": "Rust",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".lua": "Lua",
    ".sh": "Shell",
    ".pl": "Perl",
    ".hs": "Haskell",
    ".zig": "Zig",
    ".ex": "Elixir",
}
"""!
@brief Maps file extensions (lowercase, dot-prefixed) to canonical language names.
@details Uses the same 20-language extension set as SRS-131 (one primary extension per language).
  Lookup MUST be performed on `Path(filepath).suffix.lower()`.
@see SRS-259, SRS-131
"""

#: Canonical module names (lowercase -> display form).
_CANONICAL_MODULES: dict[str, str] = {
    "dummy": "Dummy",
    "pylance": "Pylance",
    "ruff": "Ruff",
    "command": "Command",
}


# ---------------------------------------------------------------------------
# Configuration parsing helpers (SRS-260)
# ---------------------------------------------------------------------------

def _split_csv_like_tokens(spec_rhs: str) -> list[str]:
    """!
    @brief Split a comma-separated SPEC right-hand side with quote-aware token boundaries.
    @param spec_rhs Text after `LANG=` in `--enable-static-check`.
    @return Token list where commas inside `'...'` or `"..."` do not split tokens.
    @details
      - Supported quote delimiters: single quote `'` and double quote `"`.
      - Commas split tokens only when parser is outside a quoted segment.
      - Quote delimiters are not included in output tokens.
      - Leading and trailing whitespace for each token is stripped.
    @see SRS-260, SRS-250
    """
    tokens: list[str] = []
    current: list[str] = []
    active_quote: str | None = None

    for ch in spec_rhs:
        if active_quote is None:
            if ch in ("'", '"'):
                active_quote = ch
            elif ch == ",":
                tokens.append("".join(current).strip())
                current = []
            else:
                current.append(ch)
        else:
            if ch == active_quote:
                active_quote = None
            else:
                current.append(ch)

    tokens.append("".join(current).strip())
    return tokens


def parse_enable_static_check(spec: str) -> tuple[str, dict]:
    """!
    @brief Parse a single `--enable-static-check` SPEC string into a (lang, config_dict) pair.
    @param spec Raw SPEC string in the format `LANG=MODULE[,CMD[,PARAM...]]`.
    @return Tuple `(canonical_lang, config_dict)` where `config_dict` contains `"module"` and
      optionally `"cmd"` (Command only) and `"params"` (non-empty list only).
    @throws ReqError If `=` separator is absent, language is unknown, or module is unknown.
    @details
      Parse steps:
      1. Split on the first `=`; left side is LANG token, right side is `MODULE[,...]`.
      2. Normalize LANG via `STATIC_CHECK_LANG_CANONICAL` (case-insensitive).
      3. Parse right side as comma-separated tokens; first token is MODULE
         (case-insensitive, validated against `_CANONICAL_MODULES`).
      4. For Command: next token is `cmd` (mandatory); all subsequent tokens are `params`.
      5. For all other modules: all tokens after MODULE are `params`.
      6. `params` key is omitted when the list is empty.
      7. `cmd` key is omitted for non-Command modules.
      8. Surrounding quote delimiters (`'` or `"`) are stripped from parsed tokens.
      Note: PARAM values containing `,` must be wrapped with `'` or `"` in SPEC.
    @see SRS-260, SRS-248, SRS-249, SRS-250
    """
    if "=" not in spec:
        raise ReqError(
            "Error: --enable-static-check requires format LANG=MODULE[,CMD[,PARAM...]]; "
            "missing '=' separator.",
            1,
        )
    lang_raw, rest = spec.split("=", 1)
    lang_key = lang_raw.strip().lower()
    if lang_key not in STATIC_CHECK_LANG_CANONICAL:
        valid = ", ".join(sorted({v for v in STATIC_CHECK_LANG_CANONICAL.values()}, key=str.lower))
        raise ReqError(
            f"Error: unknown language '{lang_raw.strip()}' in --enable-static-check. "
            f"Valid language names (case-insensitive): {valid}",
            1,
        )
    canonical_lang = STATIC_CHECK_LANG_CANONICAL[lang_key]

    parts = _split_csv_like_tokens(rest)
    if not parts or not parts[0].strip():
        raise ReqError(
            "Error: --enable-static-check requires MODULE after '='. "
            "Valid modules (case-insensitive): Dummy, Pylance, Ruff, Command",
            1,
        )

    module_raw = parts[0].strip()
    module_key = module_raw.lower()
    if module_key not in _CANONICAL_MODULES:
        raise ReqError(
            f"Error: unknown module '{module_raw}' in --enable-static-check. "
            "Valid modules (case-insensitive): Dummy, Pylance, Ruff, Command",
            1,
        )
    module = _CANONICAL_MODULES[module_key]
    remaining = [p.strip() for p in parts[1:]]

    config: dict = {"module": module}
    if module == "Command":
        if not remaining or not remaining[0]:
            raise ReqError(
                "Error: Command module requires a cmd argument in --enable-static-check. "
                "Format: LANG=Command,CMD[,PARAM...]",
                1,
            )
        config["cmd"] = remaining[0]
        params = [p for p in remaining[1:] if p]
        if params:
            config["params"] = params
    else:
        params = [p for p in remaining if p]
        if params:
            config["params"] = params

    return canonical_lang, config


# ---------------------------------------------------------------------------
# Per-file dispatch helper (SRS-261)
# ---------------------------------------------------------------------------

def dispatch_static_check_for_file(filepath: str, lang_config: dict) -> int:
    """!
    @brief Dispatch static-check for a single file based on a language config dict.
    @param filepath Absolute path of the file to analyse.
    @param lang_config Dict with keys `"module"` (str), optional `"cmd"` (str, Command only),
      optional `"params"` (list[str]).
    @return Exit code: 0 on pass, 1 on fail.
    @throws ReqError If module is unknown, or Command module is missing `"cmd"`.
    @details
      Module dispatch table:
      - `"Dummy"` (case-insensitive) -> `StaticCheckBase`
      - `"Pylance"` -> `StaticCheckPylance`
      - `"Ruff"` -> `StaticCheckRuff`
      - `"Command"` -> `StaticCheckCommand` (requires `"cmd"` key)
      Instantiates the checker with `inputs=[filepath]` and `extra_args=params`.
      Delegates actual check to `checker.run()`.
    @see SRS-261, SRS-253, SRS-256
    """
    module = lang_config.get("module", "")
    params: List[str] = lang_config.get("params", [])
    cmd: Optional[str] = lang_config.get("cmd")

    module_key = module.lower()
    checker: StaticCheckBase
    if module_key == "dummy":
        checker = StaticCheckBase(inputs=[filepath], extra_args=params)
    elif module_key == "pylance":
        checker = StaticCheckPylance(inputs=[filepath], extra_args=params)
    elif module_key == "ruff":
        checker = StaticCheckRuff(inputs=[filepath], extra_args=params)
    elif module_key == "command":
        if not cmd:
            raise ReqError(
                f"Error: Command module requires 'cmd' in static-check config for '{filepath}'.",
                1,
            )
        checker = StaticCheckCommand(cmd=cmd, inputs=[filepath], extra_args=params)
    else:
        raise ReqError(
            f"Error: unknown static-check module '{module}'. "
            "Valid modules: Dummy, Pylance, Ruff, Command",
            1,
        )
    return checker.run()


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
        self._has_emitted_output = False

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
        self._emit_line(self._header_line(filepath))
        self._emit_line("Result: OK")
        return 0

    def _emit_line(self, line: str) -> None:
        """!
        @brief Emit one markdown output line without appending trailing blank lines.
        @param line Line content to emit on stdout.
        @details Adds a single newline separator only between emitted lines and omits a trailing
          blank line at stream end.
        """
        if self._has_emitted_output:
            print("\n", end="")
        print(line, end="")
        self._has_emitted_output = True


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
        self._emit_line(self._header_line(filepath))
        cmd = ["pyright", filepath] + self._extra_args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            self._emit_line("Result: FAIL")
            self._emit_line("Evidence:")
            self._emit_line("  pyright not found on PATH")
            return 1

        if result.returncode == 0:
            self._emit_line("Result: OK")
            return 0
        else:
            self._emit_line("Result: FAIL")
            self._emit_line("Evidence:")
            evidence = (result.stdout or "") + (result.stderr or "")
            self._emit_line(evidence.rstrip())
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
        self._emit_line(self._header_line(filepath))
        cmd = ["ruff", "check", filepath] + self._extra_args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            self._emit_line("Result: FAIL")
            self._emit_line("Evidence:")
            self._emit_line("  ruff not found on PATH")
            return 1

        if result.returncode == 0:
            self._emit_line("Result: OK")
            return 0
        else:
            self._emit_line("Result: FAIL")
            self._emit_line("Evidence:")
            evidence = (result.stdout or "") + (result.stderr or "")
            self._emit_line(evidence.rstrip())
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
        self._emit_line(self._header_line(filepath))
        cmd = [self._cmd, filepath] + self._extra_args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            self._emit_line("Result: FAIL")
            self._emit_line("Evidence:")
            self._emit_line(f"  command '{self._cmd}' not found on PATH")
            return 1

        if result.returncode == 0:
            self._emit_line("Result: OK")
            return 0
        else:
            self._emit_line("Result: FAIL")
            self._emit_line("Evidence:")
            evidence = (result.stdout or "") + (result.stderr or "")
            self._emit_line(evidence.rstrip())
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
