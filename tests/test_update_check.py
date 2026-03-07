"""Unit tests for online update-check dispatch in CLI command flows."""

import io
import json
import subprocess
import tempfile
import urllib.error
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
        notify_mock.assert_called_once_with(timeout_seconds=2.0)

    def test_version_triggers_online_update_check(self) -> None:
        """Version-only command must still execute startup release-check."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True) as notify_mock:
            with patch("sys.stdout"):
                exit_code = cli.main(["--version"])

        self.assertEqual(exit_code, 0)
        notify_mock.assert_called_once_with(timeout_seconds=2.0)

    def test_update_check_runs_before_argument_parsing(self) -> None:
        """Release-check must run before parse_args is executed."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True) as notify_mock:
            with patch("usereq.cli.parse_args", side_effect=RuntimeError("parse failure")):
                with patch("sys.stdout"), patch("sys.stderr"):
                    exit_code = cli.main(["--files-references", "missing.py"])

        self.assertEqual(exit_code, 1)
        notify_mock.assert_called_once_with(timeout_seconds=2.0)

    def test_release_api_url_is_resolved_from_git_remote(self) -> None:
        """Git remotes must resolve to GitHub latest-release endpoint."""
        remote_output = (
            "origin\tgit@github.com:ExampleOrg/ExampleRepo.git (fetch)\n"
            "origin\tgit@github.com:ExampleOrg/ExampleRepo.git (push)\n"
        )
        with patch("usereq.cli.subprocess.check_output", return_value=remote_output):
            resolved_url = cli.resolve_latest_release_api_url()
        self.assertEqual(
            resolved_url,
            "https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest",
        )

    def test_newer_version_warning_is_bright_green(self) -> None:
        """Remote-newer detection must print a bright-green availability payload."""
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"tag_name": "v9.9.9"}).encode("utf-8")
        urlopen_cm = MagicMock()
        urlopen_cm.__enter__.return_value = response_mock
        urlopen_cm.__exit__.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = Path(temp_dir) / "idle.json"
            with patch("usereq.cli.load_package_version", return_value="0.0.1"):
                with patch("usereq.cli.time.time", return_value=1700000000):
                    with patch(
                        "usereq.cli.get_release_check_idle_file_path",
                        return_value=idle_path,
                    ):
                        with patch(
                            "usereq.cli.resolve_latest_release_api_url",
                            return_value=(
                                "https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest"
                            ),
                        ):
                            with patch(
                                "usereq.cli.urllib.request.urlopen",
                                return_value=urlopen_cm,
                            ):
                                with patch("sys.stderr") as fake_stderr:
                                    cli.maybe_notify_newer_version(timeout_seconds=2.0)

        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(cli.ANSI_BRIGHT_GREEN, written)
        self.assertIn("installed 0.0.1, latest 9.9.9.", written)
        self.assertIn(cli.ANSI_RESET, written)

    def test_release_check_http_403_prints_bright_red_error(self) -> None:
        """HTTP errors must print bright-red diagnostics without aborting execution."""
        http_error = urllib.error.HTTPError(
            url="https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"message":"API rate limit exceeded"}'),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = Path(temp_dir) / "idle.json"
            with patch("usereq.cli.load_package_version", return_value="0.0.1"):
                with patch("usereq.cli.time.time", return_value=1700000000):
                    with patch(
                        "usereq.cli.get_release_check_idle_file_path",
                        return_value=idle_path,
                    ):
                        with patch(
                            "usereq.cli.resolve_latest_release_api_url",
                            return_value=(
                                "https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest"
                            ),
                        ):
                            with patch(
                                "usereq.cli.urllib.request.urlopen",
                                side_effect=http_error,
                            ):
                                with patch("sys.stderr") as fake_stderr:
                                    cli.maybe_notify_newer_version(timeout_seconds=2.0)

        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(cli.ANSI_BRIGHT_RED, written)
        self.assertIn("HTTP 403", written)
        self.assertIn("API rate limit exceeded", written)
        self.assertIn(cli.ANSI_RESET, written)

    def test_release_check_uses_remote_resolved_url(self) -> None:
        """Release-check request must target URL built from git remote mapping."""
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"tag_name": "v0.0.1"}).encode("utf-8")
        urlopen_cm = MagicMock()
        urlopen_cm.__enter__.return_value = response_mock
        urlopen_cm.__exit__.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = Path(temp_dir) / "idle.json"
            with patch("usereq.cli.load_package_version", return_value="0.0.1"):
                with patch("usereq.cli.time.time", return_value=1700000000):
                    with patch(
                        "usereq.cli.get_release_check_idle_file_path",
                        return_value=idle_path,
                    ):
                        with patch(
                            "usereq.cli.urllib.request.urlopen",
                            return_value=urlopen_cm,
                        ) as urlopen_mock:
                            with patch(
                                "usereq.cli.subprocess.check_output",
                            ) as check_output_mock:
                                check_output_mock.return_value = (
                                    "origin\thttps://github.com/ExampleOrg/ExampleRepo.git (fetch)\n"
                                )
                                cli.maybe_notify_newer_version(timeout_seconds=2.0)

        urlopen_call = urlopen_mock.call_args
        request_object = urlopen_call.args[0]
        self.assertEqual(
            request_object.full_url,
            "https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest",
        )

    def test_release_check_skips_network_when_idle_window_active(self) -> None:
        """Active idle-until state must skip remote HTTP calls."""
        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = Path(temp_dir) / "idle.json"
            now_timestamp = 1700000000
            idle_state = {
                "last_success_timestamp": now_timestamp - 10,
                "last_success_human_readable_timestamp": "2023-11-14T22:13:10Z",
                "idle_until_timestamp": now_timestamp + 3600,
                "idle_until_human_readable_timestamp": "2023-11-15T00:13:20Z",
            }
            idle_path.write_text(json.dumps(idle_state), encoding="utf-8")

            with patch("usereq.cli.load_package_version", return_value="0.0.1"):
                with patch("usereq.cli.time.time", return_value=now_timestamp):
                    with patch(
                        "usereq.cli.get_release_check_idle_file_path",
                        return_value=idle_path,
                    ):
                        with patch("usereq.cli.urllib.request.urlopen") as urlopen_mock:
                            cli.maybe_notify_newer_version(timeout_seconds=2.0)

        urlopen_mock.assert_not_called()

    def test_release_check_idle_window_default_is_300_seconds(self) -> None:
        """Default idle window constant must match five-minute cadence."""
        self.assertEqual(cli.RELEASE_CHECK_IDLE_WINDOW_SECONDS, 300)

    def test_successful_release_check_writes_idle_state_file(self) -> None:
        """Successful release check must persist timestamps and human-readable fields."""
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"tag_name": "v0.0.1"}).encode("utf-8")
        urlopen_cm = MagicMock()
        urlopen_cm.__enter__.return_value = response_mock
        urlopen_cm.__exit__.return_value = None
        now_timestamp = 1700000000

        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = Path(temp_dir) / "idle.json"
            with patch("usereq.cli.load_package_version", return_value="0.0.1"):
                with patch("usereq.cli.time.time", return_value=now_timestamp):
                    with patch(
                        "usereq.cli.get_release_check_idle_file_path",
                        return_value=idle_path,
                    ):
                        with patch(
                            "usereq.cli.resolve_latest_release_api_url",
                            return_value=(
                                "https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest"
                            ),
                        ):
                            with patch(
                                "usereq.cli.urllib.request.urlopen",
                                return_value=urlopen_cm,
                            ):
                                cli.maybe_notify_newer_version(timeout_seconds=2.0)

            payload = json.loads(idle_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["last_success_timestamp"], now_timestamp)
        self.assertEqual(
            payload["last_success_human_readable_timestamp"],
            cli.format_unix_timestamp_utc(now_timestamp),
        )
        self.assertEqual(
            payload["idle_until_timestamp"],
            now_timestamp + cli.RELEASE_CHECK_IDLE_WINDOW_SECONDS,
        )
        self.assertEqual(
            payload["idle_until_human_readable_timestamp"],
            cli.format_unix_timestamp_utc(
                now_timestamp + cli.RELEASE_CHECK_IDLE_WINDOW_SECONDS
            ),
        )

    def test_upgrade_command_uses_remote_owner_repository(self) -> None:
        """Upgrade command must use git remote owner/repository in uv source URL."""
        remote_output = "origin\tgit@github.com:ExampleOrg/ExampleRepo.git (fetch)\n"
        result_mock = MagicMock(returncode=0)

        with patch("usereq.cli.subprocess.check_output", return_value=remote_output):
            with patch("usereq.cli.subprocess.run", return_value=result_mock) as run_mock:
                cli.run_upgrade()

        run_mock.assert_called_once_with(
            [
                "uv",
                "tool",
                "install",
                cli.TOOL_PROGRAM_NAME,
                "--force",
                "--from",
                "git+https://github.com/ExampleOrg/ExampleRepo.git",
            ],
            check=False,
        )

    def test_upgrade_command_errors_when_remote_is_not_github(self) -> None:
        """Upgrade command must fail when GitHub owner/repository cannot be resolved."""
        remote_output = "origin\thttps://example.com/org/repo.git (fetch)\n"
        with patch("usereq.cli.subprocess.check_output", return_value=remote_output):
            with self.assertRaises(cli.ReqError) as context:
                cli.run_upgrade()
        self.assertIn(
            "unable to resolve upgrade source from git remotes",
            context.exception.message,
        )

    def test_upgrade_command_retries_remote_inspection_in_repo_root(self) -> None:
        """Upgrade command must retry git remotes from repository root on first failure."""
        remote_output = "origin\tgit@github.com:ExampleOrg/ExampleRepo.git (fetch)\n"
        result_mock = MagicMock(returncode=0)

        with patch(
            "usereq.cli.subprocess.check_output",
            side_effect=[
                subprocess.CalledProcessError(
                    returncode=128,
                    cmd=["git", "remote", "-v"],
                    stderr="fatal: not a git repository",
                ),
                remote_output,
            ],
        ) as check_output_mock:
            with patch("usereq.cli.Path.cwd", return_value=Path("/tmp/non-repo-cwd")):
                with patch("usereq.cli.subprocess.run", return_value=result_mock) as run_mock:
                    cli.run_upgrade()

        self.assertEqual(check_output_mock.call_count, 2)
        first_call_kwargs = check_output_mock.call_args_list[0].kwargs
        second_call_kwargs = check_output_mock.call_args_list[1].kwargs
        self.assertNotIn("cwd", first_call_kwargs)
        self.assertEqual(second_call_kwargs.get("cwd"), str(cli.REPO_ROOT))
        run_mock.assert_called_once_with(
            [
                "uv",
                "tool",
                "install",
                cli.TOOL_PROGRAM_NAME,
                "--force",
                "--from",
                "git+https://github.com/ExampleOrg/ExampleRepo.git",
            ],
            check=False,
        )

    def test_uninstall_command_uses_tool_program_name(self) -> None:
        """Uninstall command must target configured tool program name."""
        result_mock = MagicMock(returncode=0)
        with patch("usereq.cli.subprocess.run", return_value=result_mock) as run_mock:
            cli.run_uninstall()

        run_mock.assert_called_once_with(
            [
                "uv",
                "tool",
                "uninstall",
                cli.TOOL_PROGRAM_NAME,
            ],
            check=False,
        )
