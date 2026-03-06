"""Unit tests for online update-check dispatch in CLI command flows."""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from usereq import cli


class TestOnlineUpdateCheck(unittest.TestCase):
    """Verifies that command execution triggers online update checks."""

    def test_files_references_triggers_online_update_check(self) -> None:
        """Standalone command --files-references must invoke release-check once."""
        fixture = Path(__file__).resolve().parent / "fixtures" / "fixture_python.py"

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True) as notify_mock:
            with patch("sys.stdout"):
                exit_code = cli.main(["--files-references", str(fixture)])

        self.assertEqual(exit_code, 0)
        notify_mock.assert_called_once_with(timeout_seconds=1.0)

    def test_version_triggers_online_update_check(self) -> None:
        """Version-only command must still execute startup release-check."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True) as notify_mock:
            with patch("sys.stdout"):
                exit_code = cli.main(["--version"])

        self.assertEqual(exit_code, 0)
        notify_mock.assert_called_once_with(timeout_seconds=1.0)

    def test_update_check_runs_before_argument_parsing(self) -> None:
        """Release-check must run before parse_args is executed."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True) as notify_mock:
            with patch("usereq.cli.parse_args", side_effect=RuntimeError("parse failure")):
                with patch("sys.stdout"), patch("sys.stderr"):
                    exit_code = cli.main(["--files-references", "missing.py"])

        self.assertEqual(exit_code, 1)
        notify_mock.assert_called_once_with(timeout_seconds=1.0)

    def test_newer_version_warning_is_bright_red(self) -> None:
        """Remote-newer detection must print a bright-red warning payload."""
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"tag_name": "v9.9.9"}).encode("utf-8")
        urlopen_cm = MagicMock()
        urlopen_cm.__enter__.return_value = response_mock
        urlopen_cm.__exit__.return_value = None

        with patch("usereq.cli.load_package_version", return_value="0.0.1"):
            with patch("usereq.cli.urllib.request.urlopen", return_value=urlopen_cm):
                with patch("sys.stderr") as fake_stderr:
                    cli.maybe_notify_newer_version(timeout_seconds=1.0)

        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(cli.ANSI_BRIGHT_RED, written)
        self.assertIn("current 0.0.1, latest 9.9.9.", written)
        self.assertIn(cli.ANSI_RESET, written)
