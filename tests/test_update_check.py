"""Unit tests for online update-check dispatch in CLI command flows."""

import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_version_does_not_trigger_online_update_check(self) -> None:
        """Version-only command must print version without running release-check."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True) as notify_mock:
            with patch("sys.stdout"):
                exit_code = cli.main(["--version"])

        self.assertEqual(exit_code, 0)
        notify_mock.assert_not_called()
