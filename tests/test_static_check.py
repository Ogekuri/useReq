"""!
@file test_static_check.py
@brief Unit tests for the static_check module (SRS-247).
@details Covers:
  - StaticCheckBase (Dummy) output format
  - StaticCheckPylance OK/FAIL branches (mocked subprocess)
  - StaticCheckRuff OK/FAIL branches (mocked subprocess)
  - StaticCheckCommand availability check and OK/FAIL branches (mocked subprocess)
  - Glob pattern resolution including ** recursive expansion (_resolve_files)
  - Direct-children-only directory resolution (_resolve_files)
  - Empty file-list warning behavior
  - CLI dispatcher (run_static_check)
@author useReq
@version 0.0.71
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
    StaticCheckBase,
    StaticCheckCommand,
    StaticCheckPylance,
    StaticCheckRuff,
    _resolve_files,
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


if __name__ == "__main__":
    unittest.main()
