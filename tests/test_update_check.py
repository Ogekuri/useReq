"""Unit tests for online update-check dispatch in CLI command flows."""

import io
import http.client
import json
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

    def test_version_forces_online_check_even_with_active_idle_state(self) -> None:
        """Version-only command must force online release-check despite idle-state gating."""
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
            response_mock = MagicMock()
            response_mock.read.return_value = json.dumps({"tag_name": "v0.0.1"}).encode(
                "utf-8"
            )
            urlopen_cm = MagicMock()
            urlopen_cm.__enter__.return_value = response_mock
            urlopen_cm.__exit__.return_value = None

            with patch("usereq.cli.time.time", return_value=now_timestamp):
                with patch(
                    "usereq.cli.get_release_check_idle_file_path",
                    return_value=idle_path,
                ):
                    with patch(
                        "usereq.cli.urllib.request.urlopen",
                        return_value=urlopen_cm,
                    ) as urlopen_mock:
                        with patch("sys.stdout"):
                            exit_code = cli.main(["--version"])

        self.assertEqual(exit_code, 0)
        urlopen_mock.assert_called_once()

    def test_release_api_url_is_hardcoded(self) -> None:
        """Release-check URL must resolve to the hardcoded repository endpoint."""
        resolved_url = cli.resolve_latest_release_api_url()
        self.assertEqual(
            resolved_url,
            "https://api.github.com/repos/Ogekuri/useReq/releases/latest",
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

    def test_release_check_http_403_rate_limit_sets_extended_idle_delay(self) -> None:
        """403 API rate-limit failures must print diagnostics and persist one-hour idle delay."""
        now_timestamp = 1700000000
        http_error = urllib.error.HTTPError(
            url="https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest",
            code=403,
            msg="Forbidden",
            hdrs=http.client.HTTPMessage(),
            fp=io.BytesIO(b'{"message":"API rate limit exceeded"}'),
        )

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
                                side_effect=http_error,
                            ):
                                with patch("sys.stderr") as fake_stderr:
                                    cli.maybe_notify_newer_version(timeout_seconds=2.0)
            payload = json.loads(idle_path.read_text(encoding="utf-8"))

        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(cli.ANSI_BRIGHT_RED, written)
        self.assertIn("HTTP 403", written)
        self.assertIn("API rate limit exceeded", written)
        self.assertIn(cli.ANSI_RESET, written)
        self.assertEqual(
            payload["idle_until_timestamp"],
            now_timestamp + cli.RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS,
        )

    def test_release_check_uses_hardcoded_url(self) -> None:
        """Release-check request must target the hardcoded GitHub endpoint URL."""
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
                            cli.maybe_notify_newer_version(timeout_seconds=2.0)

        urlopen_call = urlopen_mock.call_args
        request_object = urlopen_call.args[0]
        self.assertEqual(
            request_object.full_url,
            "https://api.github.com/repos/Ogekuri/useReq/releases/latest",
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

    def test_release_check_idle_delay_default_is_300_seconds(self) -> None:
        """Default release-check idle-delay constant must match five minutes."""
        self.assertEqual(cli.RELEASE_CHECK_IDLE_DELAY_SECONDS, 300)

    def test_release_check_rate_limit_idle_delay_is_3600_seconds(self) -> None:
        """Rate-limited release-check idle-delay constant must match one hour."""
        self.assertEqual(cli.RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS, 3600)

    def test_release_check_idle_file_path_uses_home_cache_directory(self) -> None:
        """Idle-state path must be anchored under ~/.cache/usereq."""
        fake_home = Path("/tmp/fake-home")
        with patch("usereq.cli.Path.home", return_value=fake_home):
            resolved_path = cli.get_release_check_idle_file_path()
        self.assertEqual(
            resolved_path,
            fake_home / ".cache" / "usereq" / "check_version_idle-time.json",
        )

    def test_write_release_check_idle_state_creates_parent_directories(self) -> None:
        """Idle-state writer must create missing parent cache directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = (
                Path(temp_dir)
                / ".cache"
                / "usereq"
                / "check_version_idle-time.json"
            )
            cli.write_release_check_idle_state(
                file_path=idle_path,
                now_timestamp=1700000000,
            )
            self.assertTrue(idle_path.exists())

    def test_release_check_executes_when_idle_until_expired(self) -> None:
        """Expired idle-until timestamp must allow a new remote release-check."""
        response_mock = MagicMock()
        response_mock.read.return_value = json.dumps({"tag_name": "v0.0.1"}).encode("utf-8")
        urlopen_cm = MagicMock()
        urlopen_cm.__enter__.return_value = response_mock
        urlopen_cm.__exit__.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = Path(temp_dir) / "idle.json"
            now_timestamp = 1700000000
            idle_state = {
                "last_success_timestamp": now_timestamp - 30,
                "last_success_human_readable_timestamp": "2023-11-14T22:13:10Z",
                "idle_until_timestamp": now_timestamp - 1,
                "idle_until_human_readable_timestamp": "2023-11-14T22:13:19Z",
            }
            idle_path.write_text(json.dumps(idle_state), encoding="utf-8")

            with patch("usereq.cli.load_package_version", return_value="0.0.1"):
                with patch("usereq.cli.time.time", return_value=now_timestamp):
                    with patch(
                        "usereq.cli.get_release_check_idle_file_path",
                        return_value=idle_path,
                    ):
                        with patch(
                            "usereq.cli.urllib.request.urlopen",
                            return_value=urlopen_cm,
                        ) as urlopen_mock:
                            cli.maybe_notify_newer_version(timeout_seconds=2.0)

        urlopen_mock.assert_called_once()

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
            now_timestamp + cli.RELEASE_CHECK_IDLE_DELAY_SECONDS,
        )
        self.assertEqual(
            payload["idle_until_human_readable_timestamp"],
            cli.format_unix_timestamp_utc(
                now_timestamp + cli.RELEASE_CHECK_IDLE_DELAY_SECONDS
            ),
        )

    def test_release_check_http_429_sets_extended_idle_delay_when_retry_after_is_higher(
        self,
    ) -> None:
        """HTTP 429 handling must ignore shorter policy differences and persist one-hour backoff."""
        now_timestamp = 1700000000
        hdrs_429 = http.client.HTTPMessage()
        hdrs_429["Retry-After"] = "900"
        http_error = urllib.error.HTTPError(
            url="https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest",
            code=429,
            msg="Too Many Requests",
            hdrs=hdrs_429,
            fp=io.BytesIO(b'{"message":"rate limit exceeded"}'),
        )

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
                                side_effect=http_error,
                            ):
                                cli.maybe_notify_newer_version(timeout_seconds=2.0)

            payload = json.loads(idle_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["last_success_timestamp"], now_timestamp)
        self.assertEqual(
            payload["idle_until_timestamp"],
            now_timestamp + cli.RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS,
        )

    def test_release_check_http_429_sets_extended_idle_delay_when_retry_after_is_lower(
        self,
    ) -> None:
        """HTTP 429 handling must persist one-hour backoff even with short Retry-After values."""
        now_timestamp = 1700000000
        hdrs_429_short = http.client.HTTPMessage()
        hdrs_429_short["Retry-After"] = "60"
        http_error = urllib.error.HTTPError(
            url="https://api.github.com/repos/ExampleOrg/ExampleRepo/releases/latest",
            code=429,
            msg="Too Many Requests",
            hdrs=hdrs_429_short,
            fp=io.BytesIO(b'{"message":"rate limit exceeded"}'),
        )

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
                                side_effect=http_error,
                            ):
                                cli.maybe_notify_newer_version(timeout_seconds=2.0)

            payload = json.loads(idle_path.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["idle_until_timestamp"],
            now_timestamp + cli.RELEASE_CHECK_RATE_LIMIT_IDLE_DELAY_SECONDS,
        )

    def test_rate_limited_idle_state_keeps_larger_existing_idle_until(self) -> None:
        """Rate-limit idle-state writer must preserve larger pre-existing idle-until timestamp."""
        now_timestamp = 1700000000
        idle_state = {
            "last_success_timestamp": now_timestamp - 7200,
            "last_success_human_readable_timestamp": "2023-11-14T20:13:20Z",
            "idle_until_timestamp": now_timestamp + 5400,
            "idle_until_human_readable_timestamp": "2023-11-14T23:43:20Z",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            idle_path = Path(temp_dir) / "idle.json"
            cli.write_rate_limited_release_check_idle_state(
                file_path=idle_path,
                now_timestamp=now_timestamp,
                idle_state=idle_state,
            )
            payload = json.loads(idle_path.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["last_success_timestamp"],
            idle_state["last_success_timestamp"],
        )
        self.assertEqual(
            payload["idle_until_timestamp"],
            idle_state["idle_until_timestamp"],
        )

    def test_upgrade_command_uses_hardcoded_owner_repository(self) -> None:
        """Upgrade command must use hardcoded owner/repository uv source URL."""
        result_mock = MagicMock(returncode=0)

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
                "git+https://github.com/Ogekuri/useReq.git",
            ],
            check=False,
        )

    def test_upgrade_command_fails_on_nonzero_exit(self) -> None:
        """Upgrade command must raise ReqError when uv exits with non-zero status."""
        result_mock = MagicMock(returncode=7)
        with patch("usereq.cli.subprocess.run", return_value=result_mock):
            with self.assertRaises(cli.ReqError) as context:
                cli.run_upgrade()
        self.assertIn("auto-upgrade failed", context.exception.message)
        self.assertEqual(context.exception.code, 7)

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
