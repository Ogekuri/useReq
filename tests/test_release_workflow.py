"""Tests for GitHub release workflow trigger configuration."""

import re
import unittest
from pathlib import Path


class TestReleaseWorkflowTriggers(unittest.TestCase):
    """Validates release workflow trigger declarations."""

    def test_release_workflow_supports_manual_dispatch(self) -> None:
        """Release workflow must declare workflow_dispatch under on."""
        workflow_path = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "release-uvx.yml"
        )
        content = workflow_path.read_text(encoding="utf-8")
        on_block = re.search(
            r"^on:\n(?P<body>(?:^[ \t].*\n?)*)",
            content,
            flags=re.MULTILINE,
        )
        self.assertIsNotNone(on_block, "Workflow must define an 'on' block")
        self.assertIn(
            "workflow_dispatch:",
            on_block.group("body"),
            "Release workflow must allow manual dispatch",
        )
        self.assertRegex(
            on_block.group("body"),
            r"push:\n[ \t]+tags:\n[ \t]+- 'v\[0-9\]\+\.\[0-9\]\+\.\[0-9\]\+'",
            "Release workflow must retain tag push trigger",
        )
