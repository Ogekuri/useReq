"""!
@file test_static_check.py
@brief Unit tests for the static_check module (SRS-247, SRS-262).
@details Covers:
  - StaticCheckBase (Dummy) output format
  - StaticCheckPylance OK/FAIL branches (mocked subprocess)
  - StaticCheckRuff OK/FAIL branches (mocked subprocess)
  - StaticCheckCommand availability check and OK/FAIL branches (mocked subprocess)
  - Glob pattern resolution including ** recursive expansion (_resolve_files)
  - Direct-children-only directory resolution (_resolve_files)
  - Empty file-list warning behavior
  - CLI dispatcher (run_static_check)
  - parse_enable_static_check happy/error cases (SRS-262)
  - dispatch_static_check_for_file per module (SRS-262)
  - --files-static-check CLI dispatch (SRS-262)
  - --static-check project-scan dispatch (SRS-262)
  - --enable-static-check config persistence (SRS-262)
  - Language name case-insensitivity (SRS-262)
@author useReq
@version 0.0.72
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from usereq.static_check import (
    STATIC_CHECK_EXT_TO_LANG,
    STATIC_CHECK_LANG_CANONICAL,
    StaticCheckBase,
    StaticCheckCommand,
    StaticCheckPylance,
    StaticCheckRuff,
    _resolve_files,
    dispatch_static_check_for_file,
    parse_enable_static_check,
    run_static_check,
)
from usereq.cli import ReqError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TEMP_BASE = Path(__file__).resolve().parents[1] / "temp" / "test_static_check"


def _make_temp_file(directory: Path, name: str = "sample.py", content: str = "x = 1\n") -> Path:
    """Create a temporary file under directory and return its path."""
    directory.mkdir(parents=True, exist_ok=True)
    p = directory / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _resolve_files tests
# ---------------------------------------------------------------------------

class TestResolveFiles(unittest.TestCase):
    """Tests for the _resolve_files helper."""

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "resolve"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_single_file(self) -> None:
        """Explicit file path resolves to a single entry."""
        f = _make_temp_file(self.tmp, "a.py")
        result = _resolve_files([str(f)])
        self.assertEqual(result, [str(f.resolve())])

    def test_glob_pattern(self) -> None:
        """Glob pattern expands to matching files."""
        _make_temp_file(self.tmp, "b1.py")
        _make_temp_file(self.tmp, "b2.py")
        _make_temp_file(self.tmp, "c.txt")
        pattern = str(self.tmp / "*.py")
        result = _resolve_files([pattern])
        basenames = sorted(Path(p).name for p in result)
        self.assertIn("b1.py", basenames)
        self.assertIn("b2.py", basenames)
        self.assertNotIn("c.txt", basenames)

    def test_glob_double_star_recursive(self) -> None:
        """** glob pattern recursively expands into subdirectories (SRS-245)."""
        subdir = self.tmp / "pkg"
        subdir.mkdir()
        _make_temp_file(self.tmp, "top.py")
        _make_temp_file(subdir, "nested.py")
        pattern = str(self.tmp / "**" / "*.py")
        result = _resolve_files([pattern])
        names = [Path(p).name for p in result]
        self.assertIn("top.py", names)
        self.assertIn("nested.py", names)

    def test_directory_direct_children_only(self) -> None:
        """Bare directory entry lists only direct children (SRS-245)."""
        subdir = self.tmp / "sub"
        subdir.mkdir()
        _make_temp_file(self.tmp, "top.py")
        _make_temp_file(subdir, "nested.py")
        result = _resolve_files([str(self.tmp)])
        names = [Path(p).name for p in result]
        self.assertIn("top.py", names)
        self.assertNotIn("nested.py", names)

    def test_nonexistent_path_warns_and_skips(self) -> None:
        """Non-existent path emits a warning to stderr and is skipped."""
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            result = _resolve_files(["/no/such/path/file.py"])
        self.assertEqual(result, [])
        self.assertIn("Warning", mock_err.getvalue())

    def test_deduplication(self) -> None:
        """Duplicate entries are resolved to a single occurrence."""
        f = _make_temp_file(self.tmp, "dup.py")
        result = _resolve_files([str(f), str(f)])
        self.assertEqual(len(result), 1)

    def test_empty_inputs(self) -> None:
        """Empty inputs list returns empty result."""
        result = _resolve_files([])
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# StaticCheckBase (Dummy)
# ---------------------------------------------------------------------------

class TestStaticCheckBase(unittest.TestCase):
    """Tests for StaticCheckBase (Dummy) behavior."""

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "dummy"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_output_format_single_file(self) -> None:
        """Dummy emits correct header and Result: OK for a single file."""
        f = _make_temp_file(self.tmp, "check.py")
        with patch("builtins.print") as mock_print:
            checker = StaticCheckBase(inputs=[str(f)])
            rc = checker.run()
        self.assertEqual(rc, 0)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertTrue(any("Static-Check(Dummy)" in s and str(f.resolve()) in s for s in calls))
        self.assertIn("Result: OK", calls)

    def test_output_format_with_extra_args(self) -> None:
        """Header line includes extra_args when provided."""
        f = _make_temp_file(self.tmp, "with_opts.py")
        with patch("builtins.print") as mock_print:
            checker = StaticCheckBase(inputs=[str(f)], extra_args=["--strict"])
            checker.run()
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        header = next(s for s in calls if "Static-Check(Dummy)" in s)
        self.assertIn("--strict", header)

    def test_multiple_files_all_ok(self) -> None:
        """Dummy emits OK for each file in the list."""
        files = [_make_temp_file(self.tmp, f"f{i}.py") for i in range(3)]
        with patch("builtins.print") as mock_print:
            checker = StaticCheckBase(inputs=[str(f) for f in files])
            rc = checker.run()
        self.assertEqual(rc, 0)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        ok_count = calls.count("Result: OK")
        self.assertEqual(ok_count, 3)

    def test_empty_file_list_warns(self) -> None:
        """Empty resolved file list emits a warning to stderr and returns 0."""
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            checker = StaticCheckBase(inputs=[])
            rc = checker.run()
        self.assertEqual(rc, 0)
        self.assertIn("Warning", mock_err.getvalue())

    def test_no_recursive_attribute(self) -> None:
        """StaticCheckBase has no _recursive attribute (SRS-240)."""
        checker = StaticCheckBase(inputs=[])
        self.assertFalse(hasattr(checker, "_recursive"))

    def test_label_is_dummy(self) -> None:
        """LABEL of StaticCheckBase is 'Dummy'."""
        self.assertEqual(StaticCheckBase.LABEL, "Dummy")


# ---------------------------------------------------------------------------
# StaticCheckPylance
# ---------------------------------------------------------------------------

class TestStaticCheckPylance(unittest.TestCase):
    """Tests for StaticCheckPylance OK/FAIL branches with mocked subprocess."""

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "pylance"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def _make_completed(self, returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
        m = MagicMock()
        m.returncode = returncode
        m.stdout = stdout
        m.stderr = stderr
        return m

    def test_label_is_pylance(self) -> None:
        """LABEL of StaticCheckPylance is 'Pylance'."""
        self.assertEqual(StaticCheckPylance.LABEL, "Pylance")

    def test_ok_branch(self) -> None:
        """Pylance OK branch: prints header and Result: OK."""
        f = _make_temp_file(self.tmp, "ok.py")
        with patch("subprocess.run", return_value=self._make_completed(0)):
            with patch("builtins.print") as mock_print:
                checker = StaticCheckPylance(inputs=[str(f)])
                rc = checker.run()
        self.assertEqual(rc, 0)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertTrue(any("Static-Check(Pylance)" in s for s in calls))
        self.assertIn("Result: OK", calls)

    def test_fail_branch(self) -> None:
        """Pylance FAIL branch: prints header, Result: FAIL, Evidence:, and output."""
        f = _make_temp_file(self.tmp, "fail.py")
        evidence = "error: some type error"
        with patch("subprocess.run", return_value=self._make_completed(1, stdout=evidence)):
            with patch("builtins.print") as mock_print:
                checker = StaticCheckPylance(inputs=[str(f)])
                rc = checker.run()
        self.assertEqual(rc, 1)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertIn("Result: FAIL", calls)
        self.assertIn("Evidence:", calls)
        self.assertTrue(any(evidence in s for s in calls))

    def test_pyright_not_found(self) -> None:
        """When pyright is not on PATH, emits FAIL with evidence."""
        f = _make_temp_file(self.tmp, "nobin.py")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with patch("builtins.print") as mock_print:
                checker = StaticCheckPylance(inputs=[str(f)])
                rc = checker.run()
        self.assertEqual(rc, 1)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertIn("Result: FAIL", calls)

    def test_fail_uses_stderr_when_stdout_empty(self) -> None:
        """FAIL evidence includes stderr when stdout is empty."""
        f = _make_temp_file(self.tmp, "stderr_fail.py")
        evidence = "type error on line 1"
        with patch("subprocess.run", return_value=self._make_completed(1, stdout="", stderr=evidence)):
            with patch("builtins.print") as mock_print:
                checker = StaticCheckPylance(inputs=[str(f)])
                rc = checker.run()
        self.assertEqual(rc, 1)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertTrue(any(evidence in s for s in calls))

    def test_multiple_files_mixed_results(self) -> None:
        """Overall rc is 1 when at least one file fails."""
        f1 = _make_temp_file(self.tmp, "ok.py")
        f2 = _make_temp_file(self.tmp, "fail.py")
        results = [self._make_completed(0), self._make_completed(1, stdout="err")]
        with patch("subprocess.run", side_effect=results):
            with patch("builtins.print"):
                checker = StaticCheckPylance(inputs=[str(f1), str(f2)])
                rc = checker.run()
        self.assertEqual(rc, 1)


# ---------------------------------------------------------------------------
# StaticCheckRuff
# ---------------------------------------------------------------------------

class TestStaticCheckRuff(unittest.TestCase):
    """Tests for StaticCheckRuff OK/FAIL branches with mocked subprocess."""

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "ruff"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def _make_completed(self, returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
        m = MagicMock()
        m.returncode = returncode
        m.stdout = stdout
        m.stderr = stderr
        return m

    def test_label_is_ruff(self) -> None:
        """LABEL of StaticCheckRuff is 'Ruff'."""
        self.assertEqual(StaticCheckRuff.LABEL, "Ruff")

    def test_ok_branch(self) -> None:
        """Ruff OK branch: prints header and Result: OK."""
        f = _make_temp_file(self.tmp, "ok.py")
        with patch("subprocess.run", return_value=self._make_completed(0)):
            with patch("builtins.print") as mock_print:
                checker = StaticCheckRuff(inputs=[str(f)])
                rc = checker.run()
        self.assertEqual(rc, 0)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertTrue(any("Static-Check(Ruff)" in s for s in calls))
        self.assertIn("Result: OK", calls)

    def test_fail_branch(self) -> None:
        """Ruff FAIL branch: prints header, Result: FAIL, Evidence:, and output."""
        f = _make_temp_file(self.tmp, "fail.py")
        evidence = "E501 line too long"
        with patch("subprocess.run", return_value=self._make_completed(1, stdout=evidence)):
            with patch("builtins.print") as mock_print:
                checker = StaticCheckRuff(inputs=[str(f)])
                rc = checker.run()
        self.assertEqual(rc, 1)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertIn("Result: FAIL", calls)
        self.assertIn("Evidence:", calls)
        self.assertTrue(any(evidence in s for s in calls))

    def test_ruff_not_found(self) -> None:
        """When ruff is not on PATH, emits FAIL with evidence."""
        f = _make_temp_file(self.tmp, "nobin.py")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with patch("builtins.print") as mock_print:
                checker = StaticCheckRuff(inputs=[str(f)])
                rc = checker.run()
        self.assertEqual(rc, 1)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertIn("Result: FAIL", calls)

    def test_invokes_ruff_check(self) -> None:
        """Ruff invocation uses 'ruff check' as the command prefix."""
        f = _make_temp_file(self.tmp, "cmd_check.py")
        with patch("subprocess.run", return_value=self._make_completed(0)) as mock_run:
            checker = StaticCheckRuff(inputs=[str(f)])
            with patch("builtins.print"):
                checker.run()
        cmd_used = mock_run.call_args[0][0]
        self.assertEqual(cmd_used[0], "ruff")
        self.assertEqual(cmd_used[1], "check")

    def test_multiple_files_all_ok(self) -> None:
        """All files OK returns rc 0."""
        files = [_make_temp_file(self.tmp, f"r{i}.py") for i in range(2)]
        with patch("subprocess.run", return_value=self._make_completed(0)):
            with patch("builtins.print"):
                checker = StaticCheckRuff(inputs=[str(f) for f in files])
                rc = checker.run()
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# StaticCheckCommand
# ---------------------------------------------------------------------------

class TestStaticCheckCommand(unittest.TestCase):
    """Tests for StaticCheckCommand availability check and OK/FAIL branches."""

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "command"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def _make_completed(self, returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
        m = MagicMock()
        m.returncode = returncode
        m.stdout = stdout
        m.stderr = stderr
        return m

    def test_cmd_not_found_raises_req_error(self) -> None:
        """Constructor raises ReqError when cmd is not on PATH."""
        with patch("shutil.which", return_value=None):
            with self.assertRaises(ReqError) as ctx:
                StaticCheckCommand(cmd="nonexistent_tool_xyz", inputs=[])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("nonexistent_tool_xyz", ctx.exception.message)

    def test_label_includes_cmd_name(self) -> None:
        """LABEL is set to 'Command[<cmd>]' after successful init."""
        with patch("shutil.which", return_value="/usr/bin/mytool"):
            checker = StaticCheckCommand(cmd="mytool", inputs=[])
        self.assertEqual(checker.LABEL, "Command[mytool]")

    def test_ok_branch(self) -> None:
        """Command OK branch: prints header and Result: OK."""
        f = _make_temp_file(self.tmp, "ok.py")
        with patch("shutil.which", return_value="/usr/bin/mytool"):
            with patch("subprocess.run", return_value=self._make_completed(0)):
                with patch("builtins.print") as mock_print:
                    checker = StaticCheckCommand(cmd="mytool", inputs=[str(f)])
                    rc = checker.run()
        self.assertEqual(rc, 0)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertTrue(any("Static-Check(Command[mytool])" in s for s in calls))
        self.assertIn("Result: OK", calls)

    def test_fail_branch(self) -> None:
        """Command FAIL branch: prints Result: FAIL and Evidence."""
        f = _make_temp_file(self.tmp, "fail.py")
        evidence = "found issue in file"
        with patch("shutil.which", return_value="/usr/bin/mytool"):
            with patch("subprocess.run", return_value=self._make_completed(1, stdout=evidence)):
                with patch("builtins.print") as mock_print:
                    checker = StaticCheckCommand(cmd="mytool", inputs=[str(f)])
                    rc = checker.run()
        self.assertEqual(rc, 1)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertIn("Result: FAIL", calls)
        self.assertIn("Evidence:", calls)
        self.assertTrue(any(evidence in s for s in calls))

    def test_command_not_on_path_at_runtime(self) -> None:
        """FileNotFoundError at subprocess.run emits FAIL evidence."""
        f = _make_temp_file(self.tmp, "runtime_fail.py")
        with patch("shutil.which", return_value="/usr/bin/gone"):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                with patch("builtins.print") as mock_print:
                    checker = StaticCheckCommand(cmd="gone", inputs=[str(f)])
                    rc = checker.run()
        self.assertEqual(rc, 1)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        self.assertIn("Result: FAIL", calls)

    def test_invokes_cmd_with_filepath(self) -> None:
        """Subprocess call includes the cmd name and filepath."""
        f = _make_temp_file(self.tmp, "invoke_check.py")
        with patch("shutil.which", return_value="/usr/bin/mytool"):
            with patch("subprocess.run", return_value=self._make_completed(0)) as mock_run:
                checker = StaticCheckCommand(cmd="mytool", inputs=[str(f)])
                with patch("builtins.print"):
                    checker.run()
        cmd_used = mock_run.call_args[0][0]
        self.assertEqual(cmd_used[0], "mytool")
        self.assertIn(str(f.resolve()), cmd_used)

    def test_extra_args_forwarded(self) -> None:
        """extra_args are forwarded to the subprocess call."""
        f = _make_temp_file(self.tmp, "extra.py")
        with patch("shutil.which", return_value="/usr/bin/mytool"):
            with patch("subprocess.run", return_value=self._make_completed(0)) as mock_run:
                checker = StaticCheckCommand(cmd="mytool", inputs=[str(f)], extra_args=["--flag"])
                with patch("builtins.print"):
                    checker.run()
        cmd_used = mock_run.call_args[0][0]
        self.assertIn("--flag", cmd_used)


# ---------------------------------------------------------------------------
# run_static_check dispatcher
# ---------------------------------------------------------------------------

class TestRunStaticCheck(unittest.TestCase):
    """Tests for the run_static_check CLI dispatcher."""

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "dispatcher"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_no_subcommand_raises_req_error(self) -> None:
        """Empty argv raises ReqError."""
        with self.assertRaises(ReqError):
            run_static_check([])

    def test_unknown_subcommand_raises_req_error(self) -> None:
        """Unknown subcommand raises ReqError."""
        with self.assertRaises(ReqError):
            run_static_check(["unknown_sub"])

    def test_dummy_subcommand_dispatches_correctly(self) -> None:
        """'dummy' subcommand creates StaticCheckBase and calls run()."""
        f = _make_temp_file(self.tmp, "d.py")
        with patch("builtins.print"):
            rc = run_static_check(["dummy", str(f)])
        self.assertEqual(rc, 0)

    def test_pylance_subcommand_dispatches_correctly(self) -> None:
        """'pylance' subcommand creates StaticCheckPylance and calls run()."""
        f = _make_temp_file(self.tmp, "p.py")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            with patch("builtins.print"):
                rc = run_static_check(["pylance", str(f)])
        self.assertEqual(rc, 0)

    def test_ruff_subcommand_dispatches_correctly(self) -> None:
        """'ruff' subcommand creates StaticCheckRuff and calls run()."""
        f = _make_temp_file(self.tmp, "r.py")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            with patch("builtins.print"):
                rc = run_static_check(["ruff", str(f)])
        self.assertEqual(rc, 0)

    def test_command_subcommand_missing_cmd_raises_req_error(self) -> None:
        """'command' without <cmd> raises ReqError."""
        with self.assertRaises(ReqError):
            run_static_check(["command"])

    def test_command_subcommand_dispatches_correctly(self) -> None:
        """'command <cmd>' with available tool dispatches StaticCheckCommand."""
        f = _make_temp_file(self.tmp, "c.py")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch("shutil.which", return_value="/usr/bin/mytool"):
            with patch("subprocess.run", return_value=mock_result):
                with patch("builtins.print"):
                    rc = run_static_check(["command", "mytool", str(f)])
        self.assertEqual(rc, 0)

    def test_double_star_glob_resolves_recursively(self) -> None:
        """** glob pattern in FILES resolves nested files recursively (SRS-245)."""
        subdir = self.tmp / "pkg"
        subdir.mkdir()
        _make_temp_file(self.tmp, "top.py")
        _make_temp_file(subdir, "nested.py")
        pattern = str(self.tmp / "**" / "*.py")
        with patch("builtins.print") as mock_print:
            rc = run_static_check(["dummy", pattern])
        self.assertEqual(rc, 0)
        calls = [str(c.args[0]) for c in mock_print.call_args_list]
        headers = [s for s in calls if "Static-Check(Dummy)" in s]
        # Header format: "# Static-Check(Dummy): <filepath>"
        names_in_headers = [Path(h.split(": ", 1)[1].split(" ")[0]).name for h in headers]
        self.assertIn("top.py", names_in_headers)
        self.assertIn("nested.py", names_in_headers)

    def test_empty_resolved_files_returns_zero(self) -> None:
        """When no files resolve, returns 0 (warning behavior is covered by TestStaticCheckBase)."""
        # Empty file list: no FILES arg; the warning is printed to stderr but the exit code is 0.
        with patch("builtins.print"):
            rc = run_static_check(["dummy"])
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# Integration: CLI main() wires --test-static-check
# ---------------------------------------------------------------------------

class TestCLIIntegrationStaticCheck(unittest.TestCase):
    """Integration tests: ensure cli.main() dispatches --test-static-check."""

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "cli_integration"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_main_dispatches_dummy(self) -> None:
        """cli.main(['--test-static-check', 'dummy', <file>]) returns 0."""
        from usereq import cli
        f = _make_temp_file(self.tmp, "main_dummy.py")
        with patch("builtins.print"):
            rc = cli.main(["--test-static-check", "dummy", str(f)])
        self.assertEqual(rc, 0)

    def test_main_dispatches_unknown_subcommand(self) -> None:
        """cli.main(['--test-static-check', 'badcmd']) returns non-zero."""
        from usereq import cli
        with patch("builtins.print"):
            with patch("sys.stderr", new_callable=StringIO):
                rc = cli.main(["--test-static-check", "badcmd"])
        self.assertNotEqual(rc, 0)

    def test_main_static_check_is_standalone(self) -> None:
        """--test-static-check does not require --base or --here."""
        from usereq import cli
        f = _make_temp_file(self.tmp, "standalone.py")
        with patch("builtins.print"):
            rc = cli.main(["--test-static-check", "dummy", str(f)])
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# parse_enable_static_check tests (SRS-260, SRS-262)
# ---------------------------------------------------------------------------

class TestParseEnableStaticCheck(unittest.TestCase):
    """!
    @brief Tests for parse_enable_static_check (SRS-260, SRS-262).
    @details Covers happy paths for all four modules, error cases (missing =,
      unknown lang, unknown module, missing cmd), and case-insensitivity.
    """

    def test_pylance_module_happy(self) -> None:
        """Python=Pylance produces canonical lang and module-only config."""
        lang, cfg = parse_enable_static_check("Python=Pylance")
        self.assertEqual(lang, "Python")
        self.assertEqual(cfg, {"module": "Pylance"})

    def test_ruff_module_happy(self) -> None:
        """Python=Ruff produces Ruff module config without extra keys."""
        lang, cfg = parse_enable_static_check("Python=Ruff")
        self.assertEqual(lang, "Python")
        self.assertEqual(cfg, {"module": "Ruff"})

    def test_dummy_module_happy(self) -> None:
        """C=Dummy produces Dummy module config."""
        lang, cfg = parse_enable_static_check("C=Dummy")
        self.assertEqual(lang, "C")
        self.assertEqual(cfg, {"module": "Dummy"})

    def test_command_module_with_cmd_and_params(self) -> None:
        """C=Command,/usr/bin/cppcheck,--check-library produces cmd and params."""
        lang, cfg = parse_enable_static_check("C=Command,/usr/bin/cppcheck,--check-library")
        self.assertEqual(lang, "C")
        self.assertEqual(cfg["module"], "Command")
        self.assertEqual(cfg["cmd"], "/usr/bin/cppcheck")
        self.assertEqual(cfg["params"], ["--check-library"])

    def test_command_module_with_cmd_only(self) -> None:
        """c++=Command,cppcheck produces cmd without params key."""
        lang, cfg = parse_enable_static_check("c++=Command,cppcheck")
        self.assertEqual(lang, "C++")
        self.assertEqual(cfg["module"], "Command")
        self.assertEqual(cfg["cmd"], "cppcheck")
        self.assertNotIn("params", cfg)

    def test_command_module_multiple_params(self) -> None:
        """Multiple params after cmd are stored as list."""
        lang, cfg = parse_enable_static_check("C=Command,cppcheck,--a,--b,--c flag")
        self.assertEqual(cfg["params"], ["--a", "--b", "--c flag"])

    def test_lang_case_insensitive(self) -> None:
        """Language name matching is case-insensitive (SRS-249)."""
        for raw in ("python", "PYTHON", "Python", "PyThOn"):
            lang, _ = parse_enable_static_check(f"{raw}=Dummy")
            self.assertEqual(lang, "Python")

    def test_module_case_insensitive(self) -> None:
        """Module name matching is case-insensitive (SRS-250)."""
        for raw in ("pylance", "PYLANCE", "Pylance"):
            _, cfg = parse_enable_static_check(f"Python={raw}")
            self.assertEqual(cfg["module"], "Pylance")

    def test_lang_alias_cpp(self) -> None:
        """'cpp' alias resolves to canonical 'C++' (SRS-258)."""
        lang, _ = parse_enable_static_check("cpp=Dummy")
        self.assertEqual(lang, "C++")

    def test_lang_alias_csharp(self) -> None:
        """'csharp' alias resolves to canonical 'C#' (SRS-258)."""
        lang, _ = parse_enable_static_check("csharp=Dummy")
        self.assertEqual(lang, "C#")

    def test_lang_alias_js(self) -> None:
        """'js' alias resolves to canonical 'JavaScript' (SRS-258)."""
        lang, _ = parse_enable_static_check("js=Dummy")
        self.assertEqual(lang, "JavaScript")

    def test_lang_alias_ts(self) -> None:
        """'ts' alias resolves to canonical 'TypeScript' (SRS-258)."""
        lang, _ = parse_enable_static_check("ts=Dummy")
        self.assertEqual(lang, "TypeScript")

    def test_lang_alias_sh(self) -> None:
        """'sh' alias resolves to canonical 'Shell' (SRS-258)."""
        lang, _ = parse_enable_static_check("sh=Dummy")
        self.assertEqual(lang, "Shell")

    def test_missing_equals_raises_req_error(self) -> None:
        """Missing '=' separator raises ReqError with code 1."""
        with self.assertRaises(ReqError) as ctx:
            parse_enable_static_check("PythonPylance")
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("=", ctx.exception.message)

    def test_unknown_language_raises_req_error(self) -> None:
        """Unknown language raises ReqError with code 1."""
        with self.assertRaises(ReqError) as ctx:
            parse_enable_static_check("UnknownLang=Dummy")
        self.assertEqual(ctx.exception.code, 1)

    def test_unknown_module_raises_req_error(self) -> None:
        """Unknown module raises ReqError with code 1."""
        with self.assertRaises(ReqError) as ctx:
            parse_enable_static_check("Python=UnknownModule")
        self.assertEqual(ctx.exception.code, 1)

    def test_command_without_cmd_raises_req_error(self) -> None:
        """Command module without cmd argument raises ReqError."""
        with self.assertRaises(ReqError) as ctx:
            parse_enable_static_check("C=Command")
        self.assertEqual(ctx.exception.code, 1)

    def test_all_20_languages_recognized(self) -> None:
        """All 20 canonical languages from SRS-249 are recognized."""
        canonical_langs = {
            "Python", "C", "C++", "C#", "Rust", "JavaScript", "TypeScript",
            "Java", "Go", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Lua",
            "Shell", "Perl", "Haskell", "Zig", "Elixir",
        }
        recognized = set(STATIC_CHECK_LANG_CANONICAL.values())
        self.assertEqual(recognized, canonical_langs)

    def test_pylance_with_no_params_omits_params_key(self) -> None:
        """Non-Command module with no extra tokens omits 'params' key."""
        _, cfg = parse_enable_static_check("Python=Pylance")
        self.assertNotIn("params", cfg)


# ---------------------------------------------------------------------------
# STATIC_CHECK_EXT_TO_LANG tests (SRS-259, SRS-262)
# ---------------------------------------------------------------------------

class TestStaticCheckExtToLang(unittest.TestCase):
    """!
    @brief Tests for STATIC_CHECK_EXT_TO_LANG mapping (SRS-259, SRS-262).
    @details Verifies extension-to-language mapping for all 20 SRS-131 languages.
    """

    def test_py_maps_to_python(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".py"), "Python")

    def test_c_maps_to_c(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".c"), "C")

    def test_cpp_maps_to_cpp(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".cpp"), "C++")

    def test_cs_maps_to_csharp(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".cs"), "C#")

    def test_rs_maps_to_rust(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".rs"), "Rust")

    def test_js_maps_to_javascript(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".js"), "JavaScript")

    def test_ts_maps_to_typescript(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".ts"), "TypeScript")

    def test_java_maps_to_java(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".java"), "Java")

    def test_go_maps_to_go(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".go"), "Go")

    def test_rb_maps_to_ruby(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".rb"), "Ruby")

    def test_ex_maps_to_elixir(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".ex"), "Elixir")

    def test_sh_maps_to_shell(self) -> None:
        self.assertEqual(STATIC_CHECK_EXT_TO_LANG.get(".sh"), "Shell")

    def test_unknown_ext_returns_none(self) -> None:
        self.assertIsNone(STATIC_CHECK_EXT_TO_LANG.get(".xyz"))

    def test_covers_20_languages(self) -> None:
        """Exactly 20 extensions are mapped (one per language from SRS-131)."""
        self.assertEqual(len(STATIC_CHECK_EXT_TO_LANG), 20)


# ---------------------------------------------------------------------------
# dispatch_static_check_for_file tests (SRS-261, SRS-262)
# ---------------------------------------------------------------------------

class TestDispatchStaticCheckForFile(unittest.TestCase):
    """!
    @brief Tests for dispatch_static_check_for_file (SRS-261, SRS-262).
    @details Covers dispatch to each module type with mocked subprocess/which,
      unknown module error, and Command missing-cmd error.
    """

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "dispatch_single"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def _make_proc_result(self, rc: int, stdout: str = "") -> MagicMock:
        m = MagicMock()
        m.returncode = rc
        m.stdout = stdout
        m.stderr = ""
        return m

    def test_dispatch_dummy_module_ok(self) -> None:
        """Dummy module dispatches to StaticCheckBase; returns 0."""
        f = _make_temp_file(self.tmp, "a.py")
        cfg = {"module": "Dummy"}
        with patch("builtins.print"):
            rc = dispatch_static_check_for_file(str(f), cfg)
        self.assertEqual(rc, 0)

    def test_dispatch_pylance_module_ok(self) -> None:
        """Pylance module dispatches to StaticCheckPylance; returns 0 on success."""
        f = _make_temp_file(self.tmp, "b.py")
        cfg = {"module": "Pylance"}
        with patch("subprocess.run", return_value=self._make_proc_result(0)):
            with patch("builtins.print"):
                rc = dispatch_static_check_for_file(str(f), cfg)
        self.assertEqual(rc, 0)

    def test_dispatch_pylance_module_fail(self) -> None:
        """Pylance module returns 1 when pyright exits non-zero."""
        f = _make_temp_file(self.tmp, "b2.py")
        cfg = {"module": "Pylance"}
        with patch("subprocess.run", return_value=self._make_proc_result(1, "type error")):
            with patch("builtins.print"):
                rc = dispatch_static_check_for_file(str(f), cfg)
        self.assertEqual(rc, 1)

    def test_dispatch_ruff_module_ok(self) -> None:
        """Ruff module dispatches to StaticCheckRuff; returns 0 on success."""
        f = _make_temp_file(self.tmp, "c.py")
        cfg = {"module": "Ruff"}
        with patch("subprocess.run", return_value=self._make_proc_result(0)):
            with patch("builtins.print"):
                rc = dispatch_static_check_for_file(str(f), cfg)
        self.assertEqual(rc, 0)

    def test_dispatch_command_module_ok(self) -> None:
        """Command module dispatches to StaticCheckCommand; returns 0 on success."""
        f = _make_temp_file(self.tmp, "d.c")
        cfg = {"module": "Command", "cmd": "cppcheck"}
        with patch("shutil.which", return_value="/usr/bin/cppcheck"):
            with patch("subprocess.run", return_value=self._make_proc_result(0)):
                with patch("builtins.print"):
                    rc = dispatch_static_check_for_file(str(f), cfg)
        self.assertEqual(rc, 0)

    def test_dispatch_command_with_params(self) -> None:
        """Command module forwards params to subprocess."""
        f = _make_temp_file(self.tmp, "e.c")
        cfg = {"module": "Command", "cmd": "cppcheck", "params": ["--enable=all"]}
        with patch("shutil.which", return_value="/usr/bin/cppcheck"):
            with patch("subprocess.run", return_value=self._make_proc_result(0)) as mock_run:
                with patch("builtins.print"):
                    dispatch_static_check_for_file(str(f), cfg)
        cmd_args = mock_run.call_args[0][0]
        self.assertIn("--enable=all", cmd_args)

    def test_dispatch_command_missing_cmd_raises(self) -> None:
        """Command module without 'cmd' key raises ReqError."""
        f = _make_temp_file(self.tmp, "f.c")
        cfg = {"module": "Command"}
        with self.assertRaises(ReqError):
            dispatch_static_check_for_file(str(f), cfg)

    def test_dispatch_unknown_module_raises(self) -> None:
        """Unknown module name raises ReqError."""
        f = _make_temp_file(self.tmp, "g.py")
        cfg = {"module": "UnknownModule"}
        with self.assertRaises(ReqError):
            dispatch_static_check_for_file(str(f), cfg)

    def test_dispatch_module_case_insensitive(self) -> None:
        """Module dispatch is case-insensitive (dummy -> StaticCheckBase)."""
        f = _make_temp_file(self.tmp, "h.py")
        cfg = {"module": "dummy"}
        with patch("builtins.print"):
            rc = dispatch_static_check_for_file(str(f), cfg)
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# --files-static-check CLI dispatch tests (SRS-253, SRS-254, SRS-255, SRS-262)
# ---------------------------------------------------------------------------

class TestFilesStaticCheckCLI(unittest.TestCase):
    """!
    @brief Tests for --files-static-check CLI command (SRS-253, SRS-254, SRS-255, SRS-262).
    @details Covers: files with known/unknown extensions, missing config.json,
      dispatch per extension language, exit code propagation.
    """

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "files_sc_cli"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)
        self.req_dir = self.tmp / ".req"
        self.req_dir.mkdir()

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def _write_config(self, sc_config: dict) -> None:
        """Write .req/config.json with base fields and given static-check section."""
        import json
        payload = {
            "guidelines-dir": "guidelines",
            "docs-dir": "docs",
            "tests-dir": "tests",
            "src-dir": ["src"],
            "static-check": sc_config,
        }
        (self.req_dir / "config.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_files_static_check_dummy_language(self) -> None:
        """--files-static-check dispatches Dummy for .py file when configured."""
        from usereq import cli
        f = _make_temp_file(self.tmp, "main.py")
        self._write_config({"Python": {"module": "Dummy"}})
        with patch("builtins.print"):
            rc = cli.main(["--base", str(self.tmp), "--files-static-check", str(f)])
        self.assertEqual(rc, 0)

    def test_files_static_check_unknown_extension_skipped(self) -> None:
        """--files-static-check skips files with unrecognized extension."""
        from usereq import cli
        self._write_config({"Python": {"module": "Dummy"}})
        f = _make_temp_file(self.tmp, "file.unknown_ext")
        with patch("builtins.print"):
            with patch("sys.stderr", new_callable=StringIO):
                rc = cli.main(["--base", str(self.tmp), "--files-static-check", str(f)])
        self.assertEqual(rc, 0)

    def test_files_static_check_no_config_warns_and_returns_zero(self) -> None:
        """Without config.json, --files-static-check warns to stderr and returns 0."""
        from usereq import cli
        import shutil as _shutil
        _shutil.rmtree(str(self.req_dir))
        f = _make_temp_file(self.tmp, "main.py")
        # Do NOT mock builtins.print here: the warning is emitted via print(..., file=sys.stderr).
        # Patching builtins.print would swallow it before it reaches the patched sys.stderr.
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = cli.main(["--base", str(self.tmp), "--files-static-check", str(f)])
        self.assertEqual(rc, 0)
        self.assertIn("Warning", mock_err.getvalue())

    def test_files_static_check_lang_not_in_config_skipped(self) -> None:
        """File whose language is not configured in static-check config is skipped."""
        from usereq import cli
        self._write_config({"Python": {"module": "Dummy"}})
        # .c file, but only Python is configured
        f = _make_temp_file(self.tmp, "prog.c", "int main(){return 0;}\n")
        with patch("builtins.print"):
            rc = cli.main(["--base", str(self.tmp), "--files-static-check", str(f)])
        self.assertEqual(rc, 0)

    def test_files_static_check_fail_propagates_exit_code(self) -> None:
        """--files-static-check returns 1 when at least one file fails."""
        from usereq import cli
        self._write_config({"Python": {"module": "Pylance"}})
        f = _make_temp_file(self.tmp, "bad.py")
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "type error"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            with patch("builtins.print"):
                rc = cli.main(["--base", str(self.tmp), "--files-static-check", str(f)])
        self.assertEqual(rc, 1)

    def test_files_static_check_multiple_files_mixed(self) -> None:
        """Mixed pass/fail across files: overall exit code 1."""
        from usereq import cli
        self._write_config({"Python": {"module": "Pylance"}})
        f1 = _make_temp_file(self.tmp, "ok.py")
        f2 = _make_temp_file(self.tmp, "fail.py")
        results = [MagicMock(returncode=0, stdout="", stderr=""),
                   MagicMock(returncode=1, stdout="err", stderr="")]
        with patch("subprocess.run", side_effect=results):
            with patch("builtins.print"):
                rc = cli.main(["--base", str(self.tmp), "--files-static-check", str(f1), str(f2)])
        self.assertEqual(rc, 1)


# ---------------------------------------------------------------------------
# --static-check project-scan dispatch tests (SRS-256, SRS-257, SRS-262)
# ---------------------------------------------------------------------------

class TestStaticCheckProjectScan(unittest.TestCase):
    """!
    @brief Tests for --static-check project-scan command (SRS-256, SRS-257, SRS-262).
    @details Covers: file collection from src-dir, language dispatch, skip when not configured,
      exit code propagation, missing config behavior.
    """

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "project_sc"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)
        (self.tmp / ".req").mkdir()
        (self.tmp / "src").mkdir()

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def _write_config(self, sc_config: dict) -> None:
        import json
        payload = {
            "guidelines-dir": "guidelines",
            "docs-dir": "docs",
            "tests-dir": "tests",
            "src-dir": ["src"],
        }
        if sc_config:
            payload["static-check"] = sc_config
        (self.tmp / ".req" / "config.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_static_check_dummy_on_project_files(self) -> None:
        """--static-check runs Dummy on .py files in src-dir."""
        from usereq import cli
        _make_temp_file(self.tmp / "src", "main.py")
        self._write_config({"Python": {"module": "Dummy"}})
        with patch("builtins.print"):
            rc = cli.main(["--base", str(self.tmp), "--static-check"])
        self.assertEqual(rc, 0)

    def test_static_check_skips_unconfigured_language(self) -> None:
        """--static-check skips files whose language has no configured tool."""
        from usereq import cli
        _make_temp_file(self.tmp / "src", "main.c", "int main(){return 0;}\n")
        # Only Python configured, but file is C
        self._write_config({"Python": {"module": "Dummy"}})
        with patch("builtins.print") as mock_print:
            rc = cli.main(["--base", str(self.tmp), "--static-check"])
        # rc=0 because no files were actually checked (all skipped)
        self.assertEqual(rc, 0)
        calls = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
        # No "Static-Check" output because the .c file was skipped
        self.assertFalse(any("Static-Check" in s for s in calls))

    def test_static_check_fail_propagates_exit_code(self) -> None:
        """--static-check returns 1 when at least one file fails."""
        from usereq import cli
        _make_temp_file(self.tmp / "src", "bad.py")
        self._write_config({"Python": {"module": "Pylance"}})
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "type error"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            with patch("builtins.print"):
                rc = cli.main(["--base", str(self.tmp), "--static-check"])
        self.assertEqual(rc, 1)

    def test_static_check_no_source_files_raises(self) -> None:
        """--static-check raises ReqError when no source files found."""
        from usereq import cli
        # src dir exists but is empty
        self._write_config({})
        with patch("sys.stderr", new_callable=StringIO):
            with patch("builtins.print"):
                rc = cli.main(["--base", str(self.tmp), "--static-check"])
        self.assertNotEqual(rc, 0)

    def test_static_check_requires_base_or_here(self) -> None:
        """--static-check without --base/--here returns non-zero."""
        from usereq import cli
        with patch("sys.stderr", new_callable=StringIO):
            with patch("builtins.print"):
                rc = cli.main(["--static-check"])
        self.assertNotEqual(rc, 0)

    def test_static_check_uses_cwd_as_project_base_with_here(self) -> None:
        """--static-check with --here uses CWD as project base."""
        from usereq import cli
        import os
        _make_temp_file(self.tmp / "src", "ok.py")
        self._write_config({"Python": {"module": "Dummy"}})
        old_cwd = os.getcwd()
        try:
            os.chdir(str(self.tmp))
            with patch("builtins.print"):
                rc = cli.main(["--here", "--static-check"])
        finally:
            os.chdir(old_cwd)
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# --enable-static-check config persistence tests (SRS-248, SRS-252, SRS-262)
# ---------------------------------------------------------------------------

class TestEnableStaticCheckConfigPersistence(unittest.TestCase):
    """!
    @brief Tests for --enable-static-check config persistence (SRS-248, SRS-252, SRS-262).
    @details Verifies that static-check config is correctly written to config.json via
      `save_config()` and that multiple specs merge correctly (last-wins per language, SRS-251).
      Uses direct API calls to `save_config` and `load_static_check_from_config` to avoid
      invoking the full installation flow (which requires provider flags and resource files).
    """

    def setUp(self) -> None:
        self.tmp = TEMP_BASE / "enable_sc_config"
        if self.tmp.exists():
            shutil.rmtree(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)
        (self.tmp / ".req").mkdir()

    def tearDown(self) -> None:
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_enable_static_check_saved_to_config_json(self) -> None:
        """save_config with static_check_config persists Pylance config for Python."""
        from usereq.cli import save_config, load_static_check_from_config
        sc = {"Python": {"module": "Pylance"}}
        save_config(self.tmp, "guidelines", "docs", "tests", ["src"], static_check_config=sc)
        result = load_static_check_from_config(self.tmp)
        self.assertIn("Python", result)
        self.assertEqual(result["Python"]["module"], "Pylance")

    def test_enable_static_check_command_saves_cmd_and_params(self) -> None:
        """save_config persists Command module with cmd and params for C."""
        from usereq.cli import save_config, load_static_check_from_config
        sc = {"C": {"module": "Command", "cmd": "cppcheck", "params": ["--check-library"]}}
        save_config(self.tmp, "guidelines", "docs", "tests", ["src"], static_check_config=sc)
        result = load_static_check_from_config(self.tmp)
        self.assertIn("C", result)
        self.assertEqual(result["C"]["module"], "Command")
        self.assertEqual(result["C"]["cmd"], "cppcheck")
        self.assertEqual(result["C"]["params"], ["--check-library"])

    def test_enable_static_check_multiple_langs(self) -> None:
        """save_config with multiple languages persists all entries."""
        from usereq.cli import save_config, load_static_check_from_config
        sc = {
            "Python": {"module": "Pylance"},
            "C": {"module": "Dummy"},
        }
        save_config(self.tmp, "guidelines", "docs", "tests", ["src"], static_check_config=sc)
        result = load_static_check_from_config(self.tmp)
        self.assertIn("Python", result)
        self.assertIn("C", result)

    def test_enable_static_check_last_wins_same_lang(self) -> None:
        """Collecting multiple specs with same language: last-wins before save (SRS-251)."""
        from usereq.cli import save_config, load_static_check_from_config
        from usereq.static_check import parse_enable_static_check
        # Simulate collecting multiple --enable-static-check specs for the same language.
        specs = ["Python=Dummy", "Python=Ruff"]
        merged: dict = {}
        for spec in specs:
            lang, cfg = parse_enable_static_check(spec)
            merged[lang] = cfg  # last wins
        save_config(self.tmp, "guidelines", "docs", "tests", ["src"], static_check_config=merged)
        result = load_static_check_from_config(self.tmp)
        self.assertEqual(result["Python"]["module"], "Ruff")

    def test_enable_static_check_unknown_lang_raises_req_error(self) -> None:
        """parse_enable_static_check with unknown language raises ReqError (SRS-249)."""
        from usereq.static_check import parse_enable_static_check
        with self.assertRaises(ReqError) as ctx:
            parse_enable_static_check("CobolLanguage=Dummy")
        self.assertEqual(ctx.exception.code, 1)

    def test_no_static_check_config_omitted_from_json(self) -> None:
        """save_config without static_check_config omits 'static-check' key from JSON."""
        import json
        from usereq.cli import save_config
        save_config(self.tmp, "guidelines", "docs", "tests", ["src"])
        payload = json.loads((self.tmp / ".req" / "config.json").read_text())
        self.assertNotIn("static-check", payload)

    def test_load_static_check_returns_empty_when_key_absent(self) -> None:
        """load_static_check_from_config returns {} when 'static-check' key is absent."""
        import json
        from usereq.cli import save_config, load_static_check_from_config
        save_config(self.tmp, "guidelines", "docs", "tests", ["src"])
        result = load_static_check_from_config(self.tmp)
        self.assertEqual(result, {})

    def test_load_static_check_returns_empty_when_no_config_file(self) -> None:
        """load_static_check_from_config returns {} when config.json is absent (SRS-254)."""
        from usereq.cli import load_static_check_from_config
        # No config.json written in setUp for this test
        result = load_static_check_from_config(self.tmp)
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
