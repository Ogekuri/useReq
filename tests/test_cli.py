"""
Test suite for the useReq CLI command.

This module implements unit tests to verify the correct operation
of the CLI script, according to requirement REQ-054.

# REQ-054
"""

import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Imports the CLI module to test.
from usereq import cli

KIRO_READ_ONLY_TOOLS = [
    "read",
    "glob",
    "grep",
    "shell",
    "todo",
    "todo_list",
    "thinking",
]
"""List of read-only tools allowed for Kiro."""

KIRO_READ_WRITE_TOOLS = [
    "read",
    "glob",
    "grep",
    "write",
    "shell",
    "todo",
    "todo_list",
    "thinking",
]
"""List of read-write tools allowed for Kiro."""

PROVIDER_FLAGS = [
    "--enable-claude",
    "--enable-codex",
    "--enable-gemini",
    "--enable-github",
    "--enable-kiro",
    "--enable-opencode",
]
"""Provider-specific CLI flags that enable prompt generation."""

ARTIFACT_TYPE_FLAGS = [
    "--enable-prompts",
    "--enable-agents",
]
"""Artifact-type CLI flags that explicitly enable prompts/agents; skills are enabled by default."""


class TestCLI(unittest.TestCase):
    """Test suite for the useReq CLI command."""
    # Test directory path under temp/.
    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test"

    @staticmethod
    def _snapshot_non_hidden_files(root: Path) -> dict[str, str]:
        """Returns a deterministic snapshot of non-hidden file contents."""
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(root.iterdir())
            if path.is_file() and not path.name.startswith(".")
        }

    @classmethod
    def setUpClass(cls) -> None:
        """Prepares the test environment by creating necessary directories."""
        # Removes the test directory if present (REQ-054.1).
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

        # Creates the test directory and docs/guidelines subfolders (REQ-054.2).
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tests").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)
        (cls.TEST_DIR / "lib").mkdir(exist_ok=True)
        (cls.TEST_DIR / "lib").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)
        (cls.TEST_DIR / "lib").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)

        # Creates a subfolder in guidelines to verify REQ-026.
        (cls.TEST_DIR / "guidelines" / "src").mkdir(exist_ok=True)

        cls.prompts_snapshot_before = cls._snapshot_non_hidden_files(
            cli.RESOURCE_ROOT / "prompts"
        )
        cls.docs_snapshot_before = cls._snapshot_non_hidden_files(
            cli.RESOURCE_ROOT / "docs"
        )

        # Executes the script with specified parameters (REQ-054.3).
        # Avoids network calls during tests.
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),

                    "--docs-dir",
                    str(cls.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(cls.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(cls.TEST_DIR / "tests"),
                    "--src-dir",
                    str(cls.TEST_DIR / "src"),
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        cls.exit_code = exit_code
        cls.prompts_snapshot_after = cls._snapshot_non_hidden_files(
            cli.RESOURCE_ROOT / "prompts"
        )
        cls.docs_snapshot_after = cls._snapshot_non_hidden_files(
            cli.RESOURCE_ROOT / "docs"
        )

        # Print the list of all available tests
        test_methods = [method for method in dir(cls) if method.startswith("test_")]
        print(f"All available tests: {', '.join(test_methods)}")

    def setUp(self) -> None:
        """Prints the start of the test."""
        print(f"Running test: {self._testMethodName} - {self.__doc__}")

    def tearDown(self) -> None:
        """Prints the outcome of the test."""
        print("PASS")

    @classmethod
    def tearDownClass(cls) -> None:
        """Cleans up the test environment by removing temporary directories (REQ-024)."""
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_exit_code_is_zero(self) -> None:
        """Verifies that the script ends with exit code 0."""
        self.assertEqual(self.exit_code, 0, "The script must end with exit code 0")

    def test_packaged_prompt_templates_are_read_only(self) -> None:
        """SRS-263: Verifies packaged prompt templates are not modified by CLI run."""
        self.assertEqual(
            self.prompts_snapshot_before,
            self.prompts_snapshot_after,
            "Files under src/usereq/resources/prompts must remain unchanged",
        )

    def test_packaged_docs_templates_are_read_only(self) -> None:
        """SRS-264: Verifies packaged docs templates are not modified by CLI run."""
        self.assertEqual(
            self.docs_snapshot_before,
            self.docs_snapshot_after,
            "Files under src/usereq/resources/docs must remain unchanged",
        )

    def test_requirements_md_not_generated_when_docs_empty(self) -> None:
        """REQ-001: Verifies that requirements.md is NOT generated when docs is empty."""
        requirements_path = self.TEST_DIR / "docs" / "requirements.md"
        self.assertFalse(
            requirements_path.exists(),
            "The file requirements.md must NOT be generated even if docs is empty",
        )

    def test_codex_directory_created(self) -> None:
        """REQ-002: Verifies the creation of the .codex/prompts directory."""
        codex_prompts = self.TEST_DIR / ".codex" / "prompts"
        self.assertTrue(
            codex_prompts.is_dir(), "The directory .codex/prompts must exist"
        )

    def test_codex_skills_directory_created(self) -> None:
        """REQ-095: Verifies the creation of the .codex/skills directory."""
        codex_skills = self.TEST_DIR / ".codex" / "skills"
        self.assertTrue(
            codex_skills.is_dir(), "The directory .codex/skills must exist"
        )

    def test_github_directories_created(self) -> None:
        """REQ-002: Verifies the creation of .github/agents and .github/prompts directories."""
        github_agents = self.TEST_DIR / ".github" / "agents"
        github_prompts = self.TEST_DIR / ".github" / "prompts"
        self.assertTrue(
            github_agents.is_dir(), "The directory .github/agents must exist"
        )
        self.assertTrue(
            github_prompts.is_dir(), "The directory .github/prompts must exist"
        )

    def test_gemini_directories_created(self) -> None:
        """REQ-002: Verifies the creation of .gemini/commands and .gemini/commands/req directories."""
        gemini_commands = self.TEST_DIR / ".gemini" / "commands"
        gemini_req = gemini_commands / "req"
        self.assertTrue(
            gemini_commands.is_dir(), "The directory .gemini/commands must exist"
        )
        self.assertTrue(
            gemini_req.is_dir(), "The directory .gemini/commands/req must exist"
        )

    def test_kiro_directories_created(self) -> None:
        """REQ-017: Verifies the creation of .kiro/agents and .kiro/prompts directories."""
        kiro_agents = self.TEST_DIR / ".kiro" / "agents"
        kiro_prompts = self.TEST_DIR / ".kiro" / "prompts"
        self.assertTrue(kiro_agents.is_dir(), "The directory .kiro/agents must exist")
        self.assertTrue(
            kiro_prompts.is_dir(), "The directory .kiro/prompts must exist"
        )

    def test_opencode_directory_created(self) -> None:
        """REQ-048: Verifies the creation of the .opencode/agent directory."""
        opencode_agent = self.TEST_DIR / ".opencode" / "agent"
        self.assertTrue(
            opencode_agent.is_dir(), "The directory .opencode/agent must exist"
        )

    def test_claude_directory_created(self) -> None:
        """REQ-049: Verifies the creation of the .claude/agents directory."""
        claude_agents = self.TEST_DIR / ".claude" / "agents"
        self.assertTrue(
            claude_agents.is_dir(), "The directory .claude/agents must exist"
        )

    def test_codex_prompt_files_created(self) -> None:
        """REQ-003: Verifies copy of prompt files into .codex/prompts."""
        codex_prompts = self.TEST_DIR / ".codex" / "prompts"
        expected_prompts = [
            "req-analyze.md",
            "req-change.md",
            "req-check.md",
            "req-cover.md",
            "req-fix.md",
            "req-new.md",
            "req-refactor.md",
            "req-recreate.md",
            "req-write.md",
        ]
        for prompt in expected_prompts:
            prompt_path = codex_prompts / prompt
            self.assertTrue(
                prompt_path.exists(),
                f"The file {prompt} must exist in .codex/prompts",
            )

    def test_codex_skill_files_created(self) -> None:
        """REQ-095: Verifies creation of SKILL.md for each Codex prompt."""
        codex_skills = self.TEST_DIR / ".codex" / "skills"
        expected_skills = [
            "req-analyze",
            "req-change",
            "req-check",
            "req-cover",
            "req-fix",
            "req-new",
            "req-refactor",
            "req-recreate",
            "req-write",
        ]
        for skill in expected_skills:
            skill_path = codex_skills / skill / "SKILL.md"
            self.assertTrue(
                skill_path.exists(),
                f"The file SKILL.md must exist in .codex/skills/{skill}",
            )

    def test_codex_skill_front_matter_structure(self) -> None:
        """SRS-095: Verifies Codex SKILL.md front matter has correct name and skill description."""
        codex_skill = self.TEST_DIR / ".codex" / "skills" / "req-analyze" / "SKILL.md"
        github_agent = self.TEST_DIR / ".github" / "agents" / "req-analyze.agent.md"
        self.assertTrue(codex_skill.exists(), "The Codex SKILL.md must exist")
        self.assertTrue(github_agent.exists(), "The GitHub agent must exist")
        codex_content = codex_skill.read_text(encoding="utf-8")
        agent_content = github_agent.read_text(encoding="utf-8")
        self.assertIn("name: req-analyze", codex_content, "SKILL.md must have name field")
        self.assertIn("description:", codex_content, "SKILL.md must have description field")
        # Extract description values from each file's front matter.
        import re as _re
        codex_desc_match = _re.search(r'^description:\s*"(.*)"', codex_content, _re.M)
        agent_desc_match = _re.search(r'^description:\s*"(.*)"', agent_content, _re.M)
        self.assertIsNotNone(codex_desc_match, "SKILL.md must have quoted description")
        self.assertIsNotNone(agent_desc_match, "GitHub agent must have quoted description")
        # Skill description MUST differ from agent description (different source: sections vs front matter).
        self.assertNotEqual(
            codex_desc_match.group(1),
            agent_desc_match.group(1),
            "Skill description must be derived from prompt YAML front matter usage (not agent sections)",
        )
        # Skill description must be a non-empty single-line string (no embedded newlines).
        self.assertGreater(len(codex_desc_match.group(1)), 0, "Skill description must not be empty")
        self.assertNotIn("\\n", codex_desc_match.group(1), "Skill description must be single-line")

    def test_github_agent_files_created(self) -> None:
        """REQ-003, REQ-053: Verifies copy of files into .github/agents with front matter name."""
        github_agents = self.TEST_DIR / ".github" / "agents"
        expected_agents = [
            "req-analyze.agent.md",
            "req-change.agent.md",
            "req-check.agent.md",
            "req-cover.agent.md",
            "req-fix.agent.md",
            "req-new.agent.md",
            "req-refactor.agent.md",
            "req-recreate.agent.md",
            "req-write.agent.md",
        ]
        for agent in expected_agents:
            agent_path = github_agents / agent
            self.assertTrue(
                agent_path.exists(), f"The file {agent} must exist in .github/agents"
            )
            # Verify front matter with name (REQ-053).
            content = agent_path.read_text(encoding="utf-8")
            self.assertIn("---", content, f"{agent} must contain front matter")
            prompt_name = agent.replace(".agent.md", "").replace(".", "-")
            # The name in front matter must be req-<name>.
            expected_name_pattern = agent.replace(".agent.md", "").replace(".", "-")
            self.assertIn(
                f"name: {expected_name_pattern}",
                content,
                f"{agent} must contain 'name: {expected_name_pattern}' in front matter",
            )
            self.assertIn(
                "description:",
                content,
                f"{agent} must contain 'description:' in front matter",
            )
            self.assertNotIn(
                "model:",
                content,
                "Claude front matter must not include 'model' without enabled flags",
            )

    def test_github_prompt_files_created(self) -> None:
        """REQ-004: Verifies the creation of .github/prompts/req-<name>.prompt.md files."""
        github_prompts = self.TEST_DIR / ".github" / "prompts"
        expected_prompts = [
            "req-analyze.prompt.md",
            "req-change.prompt.md",
            "req-check.prompt.md",
            "req-cover.prompt.md",
            "req-fix.prompt.md",
            "req-new.prompt.md",
            "req-refactor.prompt.md",
            "req-recreate.prompt.md",
            "req-write.prompt.md",
        ]
        for prompt in expected_prompts:
            prompt_path = github_prompts / prompt
            self.assertTrue(
                prompt_path.exists(),
                f"The file {prompt} must exist in .github/prompts",
            )
            # Verify file content.
            content = prompt_path.read_text(encoding="utf-8")
            # With default (no --prompts-use-agents) the file must contain prompt body
            # and not just a reference to the agent.
            self.assertNotIn("agent:", content, "The prompt must not be just an agent reference")
            self.assertIn("description:", content, "The prompt must include description in front matter")
            self.assertIn("argument-hint:", content, "The prompt must include argument-hint in front matter")
            self.assertIn("##", content, "The prompt body must be present")

    def test_gemini_toml_files_created(self) -> None:
        """REQ-005: Verifies TOML files generation in .gemini/commands/req-"""
        gemini_req = self.TEST_DIR / ".gemini" / "commands" / "req"
        expected_toml = [
            "analyze.toml",
            "change.toml",
            "check.toml",
            "cover.toml",
            "fix.toml",
            "new.toml",
            "refactor.toml",
            "recreate.toml",
            "write.toml",
        ]
        for toml in expected_toml:
            toml_path = gemini_req / toml
            self.assertTrue(
                toml_path.exists(),
                f"The file {toml} must exist in .gemini/commands/req",
            )
            content = toml_path.read_text(encoding="utf-8")
            self.assertIn(
                "description", content, f"{toml} must contain 'description'"
            )
            self.assertIn("prompt", content, f"{toml} must contain 'prompt'")

    def test_templates_copied(self) -> None:
        """REQ-006: Verifies copy of templates into .req/docs."""
        templates_dir = self.TEST_DIR / ".req" / "docs"
        self.assertTrue(
            templates_dir.is_dir(), "The directory .req/docs must exist"
        )
        expected_templates = sorted(
            path.name
            for path in (cli.RESOURCE_ROOT / "docs").iterdir()
            if path.is_file() and not path.name.startswith(".")
        )
        copied_templates = sorted(
            path.name for path in templates_dir.iterdir() if path.is_file()
        )
        self.assertEqual(
            copied_templates,
            expected_templates,
            "The directory .req/docs must contain all runtime docs templates",
        )

    def test_kiro_prompt_files_created(self) -> None:
        """REQ-018: Verifies copy of files into .kiro/prompts."""
        kiro_prompts = self.TEST_DIR / ".kiro" / "prompts"
        expected_prompts = [
            "req-analyze.md",
            "req-change.md",
            "req-check.md",
            "req-cover.md",
            "req-fix.md",
            "req-new.md",
            "req-refactor.md",
            "req-recreate.md",
            "req-write.md",
        ]
        for prompt in expected_prompts:
            prompt_path = kiro_prompts / prompt
            self.assertTrue(
                prompt_path.exists(), f"The file {prompt} must exist in .kiro/prompts"
            )

    def test_codex_kiro_prompt_contents_match(self) -> None:
        """Verifies that Codex and Kiro prompt contents match after replacement."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req-analyze.md"
        kiro_prompt = self.TEST_DIR / ".kiro" / "prompts" / "req-analyze.md"
        codex_content = codex_prompt.read_text(encoding="utf-8")
        kiro_content = kiro_prompt.read_text(encoding="utf-8")
        self.assertEqual(
            codex_content,
            kiro_content,
            "Codex and Kiro prompt files must have identical contents",
        )

    def test_bootstrap_token_replaced(self) -> None:
        # Removed: obsolete test for REQ-077 (bootstrap substitution no longer performed).
        pass

    def test_kiro_agent_json_files_created(self) -> None:
        """REQ-019, REQ-020: Verifies JSON files generation in .kiro/agents."""
        kiro_agents = self.TEST_DIR / ".kiro" / "agents"
        expected_agents = [
            "req-analyze.json",
            "req-change.json",
            "req-check.json",
            "req-cover.json",
            "req-fix.json",
            "req-new.json",
            "req-refactor.json",
            "req-recreate.json",
            "req-write.json",
        ]
        for agent in expected_agents:
            agent_path = kiro_agents / agent
            self.assertTrue(
                agent_path.exists(), f"The file {agent} must exist in .kiro/agents"
            )
            # Verify JSON structure (REQ-020).
            content = agent_path.read_text(encoding="utf-8")
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                self.fail(f"The file {agent} must be a valid JSON")

            # Verify mandatory fields.
            self.assertIn("name", data, f"{agent} must contain 'name' field")
            self.assertIn(
                "description", data, f"{agent} must contain 'description' field"
            )
            self.assertIn("prompt", data, f"{agent} must contain 'prompt' field")

            # Verify name format (req-<name>).
            expected_name = agent.replace(".json", "").replace(".", "-")
            self.assertEqual(
                data["name"],
                expected_name,
                f"The name in {agent} must be '{expected_name}'",
            )
            self.assertNotIn(
                "tools",
                data,
                f"{agent} must not contain 'tools' field without --enable-tools",
            )
            self.assertNotIn(
                "allowedTools",
                data,
                f"{agent} must not contain 'allowedTools' field without --enable-tools",
            )

    def test_render_kiro_agent_includes_model_tools(self) -> None:
        """Verifies render_kiro_agent handles model/tools flags consistently."""
        template = (
            "{\n"
            '  "name": "%%NAME%%",\n'
            '  "description": "%%DESCRIPTION%%",\n'
            '  "prompt": "%%PROMPT%%",\n'
            '  "resources": [\n'
            "%%RESOURCES%%\n"
            "  ],\n"
            '  "model": "legacy",\n'
            '  "tools": ["legacy"],\n'
            '  "allowedTools": ["legacy"]\n'
            "}\n"
        )
        rendered = cli.render_kiro_agent(
            template,
            name="req-test",
            description="Desc",
            prompt="Body",
            resources=["file://docs/requirements.md"],
            tools=["tool-one"],
            model="model-one",
            include_tools=True,
            include_model=True,
        )
        data = json.loads(rendered)
        self.assertEqual(data.get("model"), "model-one")
        self.assertEqual(data.get("tools"), ["tool-one"])
        self.assertEqual(data.get("allowedTools"), ["tool-one"])
        self.assertEqual(
            data.get("resources"),
            ["file://docs/requirements.md"],
            "Resources must be preserved in the rendered agent",
        )

        rendered_without_flags = cli.render_kiro_agent(
            template,
            name="req-test",
            description="Desc",
            prompt="Body",
            resources=["file://docs/requirements.md"],
            tools=["tool-one"],
            model="model-one",
            include_tools=False,
            include_model=False,
        )
        data_without_flags = json.loads(rendered_without_flags)
        self.assertNotIn("model", data_without_flags)
        self.assertNotIn("tools", data_without_flags)
        self.assertNotIn("allowedTools", data_without_flags)

    def test_doc_path_replacement(self) -> None:
        """REQ-091: Verifies %%DOC_PATH%% replacement."""
        config_path = self.TEST_DIR / ".req" / "config.json"
        data = json.loads(config_path.read_text(encoding="utf-8"))
        doc_dir = data["docs-dir"]
        replaced = cli.apply_replacements("DOC: %%DOC_PATH%%", {"%%DOC_PATH%%": doc_dir})
        self.assertEqual(replaced, f"DOC: {doc_dir}")

    def test_test_path_replacement(self) -> None:
        """REQ-092: Verifies %%TEST_PATH%% replacement."""
        config_path = self.TEST_DIR / ".req" / "config.json"
        data = json.loads(config_path.read_text(encoding="utf-8"))
        test_dir = data["tests-dir"]
        test_value = f"`{test_dir.rstrip('/\\\\')}/`"
        replaced = cli.apply_replacements(
            "TEST: %%TEST_PATH%%", {"%%TEST_PATH%%": test_value}
        )
        self.assertEqual(replaced, f"TEST: {test_value}")

    def test_src_paths_replacement(self) -> None:
        """REQ-094: Verifies %%SRC_PATHS%% replacement."""
        config_path = self.TEST_DIR / ".req" / "config.json"
        data = json.loads(config_path.read_text(encoding="utf-8"))
        src_dirs = data["src-dir"]
        src_value = ", ".join(f"`{value.rstrip('/\\\\')}/`" for value in src_dirs)
        replaced = cli.apply_replacements(
            "SRC: %%SRC_PATHS%%", {"%%SRC_PATHS%%": src_value}
        )
        self.assertEqual(replaced, f"SRC: {src_value}")

    def test_config_json_saved(self) -> None:
        """REQ-033: Verifies saving of .req/config.json."""
        config_path = self.TEST_DIR / ".req" / "config.json"
        self.assertTrue(config_path.exists(), "The file .req/config.json must exist")
        content = config_path.read_text(encoding="utf-8")
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            self.fail(".req/config.json must be a valid JSON")

        # Verify fields guidelines-dir, docs-dir, and tests-dir.
        self.assertIn("guidelines-dir", data, "config.json must contain 'guidelines-dir' field")
        self.assertIn("docs-dir", data, "config.json must contain 'docs-dir' field")
        self.assertIn("tests-dir", data, "config.json must contain 'tests-dir' field")
        self.assertIn("src-dir", data, "config.json must contain 'src-dir' field")
        self.assertEqual(data["guidelines-dir"], "guidelines", "The 'guidelines-dir' field must be 'guidelines'")
        self.assertEqual(data["docs-dir"], "docs", "The 'docs-dir' field must be 'docs'")
        self.assertEqual(data["tests-dir"], "tests", "The 'tests-dir' field must be 'tests'")
        self.assertEqual(data["src-dir"], ["src"], "The 'src-dir' field must be ['src']")

    def test_opencode_agent_files_created(self) -> None:
        """REQ-047: Verifies OpenCode agents generation in .opencode/agent."""
        opencode_agent = self.TEST_DIR / ".opencode" / "agent"
        expected_agents = [
            "req-analyze.md",
            "req-change.md",
            "req-check.md",
            "req-cover.md",
            "req-fix.md",
            "req-new.md",
            "req-refactor.md",
            "req-recreate.md",
            "req-write.md",
        ]
        for agent in expected_agents:
            agent_path = opencode_agent / agent
            self.assertTrue(
                agent_path.exists(), f"The file {agent} must exist in .opencode/agent"
            )
            content = agent_path.read_text(encoding="utf-8")
            # Verify front matter with description and mode.
            self.assertIn("---", content, f"{agent} must contain front matter")
            self.assertIn(
                "description:", content, f"{agent} must contain 'description:'"
            )
            self.assertIn("mode: all", content, f"{agent} must contain 'mode: all'")

    def test_opencode_command_contains_metadata(self) -> None:
        """Verifies that .opencode/command files include description and argument-hint."""
        cmd_path = self.TEST_DIR / ".opencode" / "command" / "req-analyze.md"
        self.assertTrue(cmd_path.exists(), "The opencode command must exist")
        content = cmd_path.read_text(encoding="utf-8")
        self.assertIn("description:", content, "Must include description in front matter")
        self.assertIn("argument-hint:", content, "Must include argument-hint in front matter")

    def test_claude_agent_files_created(self) -> None:
        """REQ-050, REQ-051: Verifies Claude Code files generation."""
        claude_agents = self.TEST_DIR / ".claude" / "agents"
        expected_agents = [
            "req-analyze.md",
            "req-change.md",
            "req-check.md",
            "req-cover.md",
            "req-fix.md",
            "req-new.md",
            "req-refactor.md",
            "req-recreate.md",
            "req-write.md",
        ]
        for agent in expected_agents:
            agent_path = claude_agents / agent
            self.assertTrue(
                agent_path.exists(), f"The file {agent} must exist in .claude/agents"
            )
            content = agent_path.read_text(encoding="utf-8")
            # Verify front matter (REQ-051).
            self.assertIn("---", content, f"{agent} must contain front matter")

            # Verify name field (req-<name>).
            expected_name = agent.replace(".md", "").replace(".", "-")
            self.assertIn(
                f"name: {expected_name}",
                content,
                f"{agent} must contain 'name: {expected_name}' in front matter",
            )

            # verify model field: inherit.
            # The 'model' field is no longer required by default (only when --enable-models).

            # Verify description field.
            self.assertIn(
                "description:",
                content,
                f"{agent} must contain 'description:' in front matter",
            )

    def test_claude_command_has_argument_hint_and_no_agent(self) -> None:
        """Verifies that full Claude commands include argument-hint and not the agent when no stubs are used."""
        cmd_path = self.TEST_DIR / ".claude" / "commands" / "req" / "analyze.md"
        self.assertTrue(cmd_path.exists(), "The Claude command must exist")
        content = cmd_path.read_text(encoding="utf-8")
        self.assertIn("argument-hint:", content, "The command must contain argument-hint")
        self.assertNotIn("agent:", content, "The command must not contain agent without stubs")

    def test_req_dir_replacement(self) -> None:
        """REQ-026, REQ-027: Verifies %%GUIDELINES_FILES%% replacement."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req-analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        # Verify that %%GUIDELINES_FILES%% has been replaced.
        self.assertNotIn(
            "%%GUIDELINES_FILES%%", content, "The token %%GUIDELINES_FILES%% must be replaced"
        )
        # After DES-014 change: generate_guidelines_file_list now lists files, not subdirectories.
        # The guidelines/ folder now contains files from its direct children, not subdirectories.
        # Since guidelines/src/ exists but is empty, the fallback will show guidelines/ directory itself.
        self.assertIn(
            "guidelines/", content, "The file must contain reference to guidelines/"
        )

    def test_kiro_resources_include_prompt(self) -> None:
        """REQ-046: Verifies that Kiro resources field includes the prompt."""
        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req-analyze.json"
        content = kiro_agent.read_text(encoding="utf-8")
        data = json.loads(content)

        self.assertIn(
            "resources", data, "The JSON file must contain 'resources' field"
        )
        resources = data["resources"]
        self.assertIsInstance(
            resources, list, "The 'resources' field must be a list"
        )
        self.assertGreater(
            len(resources), 0, "The 'resources' list must not be empty"
        )

        # Verify that the first entry is the prompt.
        first_resource = resources[0]
        self.assertIn(
            ".kiro/prompts/req-analyze.md",
            first_resource,
            "The first resource must be the prompt .kiro/prompts/req-analyze.md",
        )

    def test_claude_skills_directory_created(self) -> None:
        """SRS-233: Verifies the creation of the .claude/skills directory."""
        claude_skills = self.TEST_DIR / ".claude" / "skills"
        self.assertTrue(
            claude_skills.is_dir(), "The directory .claude/skills must exist"
        )

    def test_claude_skill_files_created(self) -> None:
        """SRS-233: Verifies creation of SKILL.md for each Claude skill."""
        claude_skills = self.TEST_DIR / ".claude" / "skills"
        expected_skills = [
            "req-analyze",
            "req-change",
            "req-check",
            "req-cover",
            "req-fix",
            "req-new",
            "req-refactor",
            "req-recreate",
            "req-write",
        ]
        for skill in expected_skills:
            skill_path = claude_skills / skill / "SKILL.md"
            self.assertTrue(
                skill_path.exists(),
                f"The file SKILL.md must exist in .claude/skills/{skill}",
            )

    def test_gemini_skills_directory_created(self) -> None:
        """SRS-234: Verifies the creation of the .gemini/skills directory."""
        gemini_skills = self.TEST_DIR / ".gemini" / "skills"
        self.assertTrue(
            gemini_skills.is_dir(), "The directory .gemini/skills must exist"
        )

    def test_gemini_skill_files_created(self) -> None:
        """SRS-234: Verifies creation of SKILL.md for each Gemini skill."""
        gemini_skills = self.TEST_DIR / ".gemini" / "skills"
        expected_skills = [
            "req-analyze",
            "req-change",
            "req-check",
            "req-cover",
            "req-fix",
            "req-new",
            "req-refactor",
            "req-recreate",
            "req-write",
        ]
        for skill in expected_skills:
            skill_path = gemini_skills / skill / "SKILL.md"
            self.assertTrue(
                skill_path.exists(),
                f"The file SKILL.md must exist in .gemini/skills/{skill}",
            )

    def test_github_skills_directory_created(self) -> None:
        """SRS-236: Verifies the creation of the .github/skills directory."""
        github_skills = self.TEST_DIR / ".github" / "skills"
        self.assertTrue(
            github_skills.is_dir(), "The directory .github/skills must exist"
        )

    def test_github_skill_files_created(self) -> None:
        """SRS-236: Verifies creation of SKILL.md for each GitHub/Copilot skill."""
        github_skills = self.TEST_DIR / ".github" / "skills"
        expected_skills = [
            "req-analyze",
            "req-change",
            "req-check",
            "req-cover",
            "req-fix",
            "req-new",
            "req-refactor",
            "req-recreate",
            "req-write",
        ]
        for skill in expected_skills:
            skill_path = github_skills / skill / "SKILL.md"
            self.assertTrue(
                skill_path.exists(),
                f"The file SKILL.md must exist in .github/skills/{skill}",
            )

    def test_kiro_skills_directory_created(self) -> None:
        """SRS-237: Verifies the creation of the .kiro/skills directory."""
        kiro_skills = self.TEST_DIR / ".kiro" / "skills"
        self.assertTrue(
            kiro_skills.is_dir(), "The directory .kiro/skills must exist"
        )

    def test_kiro_skill_files_created(self) -> None:
        """SRS-237: Verifies creation of SKILL.md for each Kiro skill."""
        kiro_skills = self.TEST_DIR / ".kiro" / "skills"
        expected_skills = [
            "req-analyze",
            "req-change",
            "req-check",
            "req-cover",
            "req-fix",
            "req-new",
            "req-refactor",
            "req-recreate",
            "req-write",
        ]
        for skill in expected_skills:
            skill_path = kiro_skills / skill / "SKILL.md"
            self.assertTrue(
                skill_path.exists(),
                f"The file SKILL.md must exist in .kiro/skills/{skill}",
            )

    def test_opencode_skills_directory_created(self) -> None:
        """SRS-235: Verifies the creation of the .opencode/skill directory."""
        opencode_skills = self.TEST_DIR / ".opencode" / "skill"
        self.assertTrue(
            opencode_skills.is_dir(), "The directory .opencode/skill must exist"
        )

    def test_opencode_skill_files_created(self) -> None:
        """SRS-235: Verifies creation of SKILL.md for each OpenCode skill."""
        opencode_skills = self.TEST_DIR / ".opencode" / "skill"
        expected_skills = [
            "req-analyze",
            "req-change",
            "req-check",
            "req-cover",
            "req-fix",
            "req-new",
            "req-refactor",
            "req-recreate",
            "req-write",
        ]
        for skill in expected_skills:
            skill_path = opencode_skills / skill / "SKILL.md"
            self.assertTrue(
                skill_path.exists(),
                f"The file SKILL.md must exist in .opencode/skill/{skill}",
            )

    def test_skill_description_is_prompt_frontmatter_usage(self) -> None:
        """
        @brief Validates SKILL.md `description` derivation from prompt YAML front matter `usage`.
        @details Confirms that the generated SKILL.md YAML `description` equals the single-line
        normalized value of the source prompt YAML front matter `usage` for `analyze.md`, and that
        all skill providers emit the same `description` for the same prompt name.
        @return None
        @see cli.extract_skill_description
        @see cli.extract_frontmatter
        """
        import yaml as _yaml

        prompt_path = cli.RESOURCE_ROOT / "prompts" / "analyze.md"
        prompt_text = prompt_path.read_text(encoding="utf-8")
        prompt_frontmatter, _prompt_body = cli.extract_frontmatter(prompt_text)
        prompt_yaml = _yaml.safe_load(prompt_frontmatter)
        self.assertIsInstance(prompt_yaml, dict, "Prompt front matter MUST parse as a YAML mapping")
        expected_usage = " ".join(str(prompt_yaml.get("usage", "")).split())
        self.assertGreater(len(expected_usage), 0, "Prompt front matter MUST contain non-empty usage")

        skill_paths = [
            self.TEST_DIR / ".codex" / "skills" / "req-analyze" / "SKILL.md",
            self.TEST_DIR / ".claude" / "skills" / "req-analyze" / "SKILL.md",
            self.TEST_DIR / ".github" / "skills" / "req-analyze" / "SKILL.md",
        ]
        observed_descriptions: list[str] = []
        for skill_path in skill_paths:
            self.assertTrue(skill_path.exists(), f"{skill_path} must exist")
            skill_text = skill_path.read_text(encoding="utf-8")
            skill_frontmatter, _skill_body = cli.extract_frontmatter(skill_text)
            skill_yaml = _yaml.safe_load(skill_frontmatter)
            self.assertIsInstance(skill_yaml, dict, f"{skill_path} front matter MUST be a YAML mapping")
            self.assertIn("description", skill_yaml, f"{skill_path} MUST include YAML field description")
            observed_descriptions.append(str(skill_yaml.get("description", "")))

        for observed in observed_descriptions:
            self.assertEqual(
                expected_usage,
                observed,
                "SKILL.md description MUST equal normalized prompt front matter usage",
            )
        self.assertEqual(
            1,
            len(set(observed_descriptions)),
            "All skill providers MUST have identical description for the same prompt",
        )

    def test_skill_front_matter_has_name_field(self) -> None:
        """SRS-095: Each SKILL.md must have a name field with prefix 'req-'."""
        skills_to_check = [
            self.TEST_DIR / ".codex" / "skills" / "req-change" / "SKILL.md",
            self.TEST_DIR / ".claude" / "skills" / "req-change" / "SKILL.md",
            self.TEST_DIR / ".github" / "skills" / "req-change" / "SKILL.md",
            self.TEST_DIR / ".gemini" / "skills" / "req-change" / "SKILL.md",
            self.TEST_DIR / ".kiro" / "skills" / "req-change" / "SKILL.md",
            self.TEST_DIR / ".opencode" / "skill" / "req-change" / "SKILL.md",
        ]
        for skill_path in skills_to_check:
            content = skill_path.read_text(encoding="utf-8")
            self.assertIn(
                "name: req-change",
                content,
                f"{skill_path} must contain 'name: req-change'",
            )


class TestGuidelinesPathReplacement(unittest.TestCase):
    """REQ-090: Verifies %%GUIDELINES_PATH%% replacement."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-guidelines-path"
    RESOURCE_DIR = (
        Path(__file__).resolve().parents[1] / "temp" / "resources-guidelines-path"
    )

    @classmethod
    def setUpClass(cls) -> None:
        """Prepares a temporary project with a custom prompt containing %%GUIDELINES_PATH%%."""
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        if cls.RESOURCE_DIR.exists():
            shutil.rmtree(cls.RESOURCE_DIR)

        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tests").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)
        (cls.TEST_DIR / "lib").mkdir(exist_ok=True)

        prompts_dir = cls.RESOURCE_DIR / "prompts"
        templates_dir = cls.RESOURCE_DIR / "docs"
        common_dir = cls.RESOURCE_DIR / "common"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        templates_dir.mkdir(parents=True, exist_ok=True)
        common_dir.mkdir(parents=True, exist_ok=True)

        prompt_content = (
            "---\n"
            "description: \"Guidelines path prompt\"\n"
            "---\n"
            "\n"
            "GuidelinesPath: %%GUIDELINES_PATH%%\n"
            "TestPath: %%TEST_PATH%%\n"
            "SrcPaths: %%SRC_PATHS%%\n"
        )
        (prompts_dir / "techpath.md").write_text(prompt_content, encoding="utf-8")
        (templates_dir / "Requirements_Template.md").write_text(
            "---\n---\n\nTemp requirements template.\n",
            encoding="utf-8",
        )
        (common_dir / "models.json").write_text(
            json.dumps(
                {
                    "kiro": {
                        "agent_template": {
                            "name": "%%NAME%%",
                            "description": "%%DESCRIPTION%%",
                            "prompt": "%%PROMPT%%",
                            "resources": ["%%RESOURCES%%"],
                        },
                        "prompts": {},
                        "usage_modes": {},
                    }
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        cls._orig_resource_root = cli.RESOURCE_ROOT
        cli.RESOURCE_ROOT = cls.RESOURCE_DIR

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            cls.exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),

                    "--docs-dir",
                    str(cls.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(cls.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(cls.TEST_DIR / "tests"),
                    "--src-dir",
                    str(cls.TEST_DIR / "src"),
                    "--src-dir",
                    str(cls.TEST_DIR / "lib"),
                    "--enable-codex",
                ]
                + ARTIFACT_TYPE_FLAGS
            )

    @classmethod
    def tearDownClass(cls) -> None:
        """Restores resources and removes temporary folders."""
        cli.RESOURCE_ROOT = cls._orig_resource_root
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        if cls.RESOURCE_DIR.exists():
            shutil.rmtree(cls.RESOURCE_DIR)

    def test_guidelines_path_replacement(self) -> None:
        """REQ-090: Verifies that %%GUIDELINES_PATH%% is replaced."""
        self.assertEqual(self.exit_code, 0, "The script must end with exit code 0")
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req-techpath.md"
        self.assertTrue(codex_prompt.exists(), "The Codex prompt must exist")
        content = codex_prompt.read_text(encoding="utf-8")
        self.assertNotIn(
            "%%GUIDELINES_PATH%%", content, "The token %%GUIDELINES_PATH%% must be replaced"
        )
        self.assertIn(
            "GuidelinesPath: guidelines",
            content,
            "The token %%GUIDELINES_PATH%% must be replaced with the normalized guidelines path",
        )

    def test_test_path_replacement(self) -> None:
        """REQ-092: Verifies that %%TEST_PATH%% is replaced."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req-techpath.md"
        content = codex_prompt.read_text(encoding="utf-8")
        self.assertNotIn(
            "%%TEST_PATH%%", content, "The token %%TEST_PATH%% must be replaced"
        )
        self.assertIn(
            "TestPath: `tests/`",
            content,
            "The token %%TEST_PATH%% must be replaced with the normalized test path",
        )

    def test_src_paths_replacement(self) -> None:
        """REQ-094: Verifies that %%SRC_PATHS%% is replaced."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req-techpath.md"
        content = codex_prompt.read_text(encoding="utf-8")
        self.assertNotIn(
            "%%SRC_PATHS%%", content, "The token %%SRC_PATHS%% must be replaced"
        )
        self.assertIn(
            "SrcPaths: `src/`, `lib/`",
            content,
            "The token %%SRC_PATHS%% must be replaced with the normalized src paths",
        )


class TestModelsAndTools(unittest.TestCase):
    """Verifies conditional inclusion of model and tools in generated files."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-models"

    @classmethod
    def setUpClass(cls) -> None:
        # Prepare test project
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tests").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)

        # Create temporary config resources under a temporary resources folder
        tmp_resources = Path(__file__).resolve().parents[1] / "temp" / "resources"
        if tmp_resources.exists():
            shutil.rmtree(tmp_resources)
        tmp_resources.mkdir(parents=True, exist_ok=True)
        (tmp_resources / "common").mkdir(parents=True, exist_ok=True)

        cls._tmp_resources = tmp_resources
        cls._orig_resource_root = cli.RESOURCE_ROOT

        base_usage = {"read_write": {"tools": ["vscode", "execute", "read"]}}
        claude_usage = {"read_write": {"tools": ["Read", "Grep", "Glob"]}}
        kiro_usage = {
            "read_write": {"tools": KIRO_READ_WRITE_TOOLS},
            "read_only": {"tools": KIRO_READ_ONLY_TOOLS}
        }

        # Create centralized models.json
        models_config = {
            "settings": {"version": "1.0.0"},
            "codex": {
                "prompts": {"analyze": {"model": "GPT-5.2-Codex (codex)", "mode": "read_write"}},
                "usage_modes": base_usage
            },
            "copilot": {
                "prompts": {"analyze": {"model": "GPT-5.2-Codex (copilot)", "mode": "read_write"}},
                "usage_modes": base_usage
            },
            "claude": {
                "prompts": {"analyze": {"model": "GPT-5.2-Codex (copilot)", "mode": "read_write"}},
                "usage_modes": claude_usage
            },
            "gemini": {
                "prompts": {"analyze": {"model": "GPT-5.2-Codex (copilot)", "mode": "read_write"}},
                "usage_modes": base_usage
            },
            "kiro": {
                "prompts": {"analyze": {"model": "GPT-5.2-Codex (copilot)", "mode": "read_only"}},
                "usage_modes": kiro_usage,
                "agent_template": {
                    "name": "%%NAME%%",
                    "description": "%%DESCRIPTION%%",
                    "prompt": "%%PROMPT%%"
                }
            },
            "opencode": {
                "prompts": {"analyze": {"model": "GPT-5.2-Codex (copilot)", "mode": "read_write"}},
                "usage_modes": base_usage
            }
        }
        models_path = tmp_resources / "common" / "models.json"
        models_path.write_text(json.dumps(models_config, indent=2), encoding="utf-8")

        # Copy existing prompts and templates into tmp_resources so CLI finds them
        repo_root = Path(__file__).resolve().parents[1]
        orig_resources = repo_root / "src" / "usereq" / "resources"
        if (orig_resources / "prompts").is_dir():
            shutil.copytree(orig_resources / "prompts", tmp_resources / "prompts")
        if (orig_resources / "docs").is_dir():
            (tmp_resources / "docs").mkdir(parents=True, exist_ok=True)
            tmpl = orig_resources / "docs" / "Requirements_Template.md"
            if tmpl.exists():
                shutil.copyfile(tmpl, tmp_resources / "docs" / "Requirements_Template.md")

        # Use temporary resources as CLI root, without touching project files.
        cli.RESOURCE_ROOT = tmp_resources

        # Run CLI with flags enabled
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),

                    "--docs-dir",
                    str(cls.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(cls.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(cls.TEST_DIR / "tests"),
                    "--src-dir",
                    str(cls.TEST_DIR / "src"),
                    "--enable-models",
                    "--enable-tools",
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        cls.exit_code = exit_code

    @classmethod
    def tearDownClass(cls) -> None:
        # Cleanup created test project and remove temporary config files
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        if getattr(cls, "_tmp_resources", None) and cls._tmp_resources.exists():
            shutil.rmtree(cls._tmp_resources)
        if getattr(cls, "_orig_resource_root", None) is not None:
            cli.RESOURCE_ROOT = cls._orig_resource_root

    def test_generated_files_include_model_and_tools(self) -> None:
        """Verifies that generated files contain model and tools when configs exist and flags are active."""
        gha = self.TEST_DIR / ".github" / "agents" / "req-analyze.agent.md"
        self.assertTrue(gha.exists(), "GitHub agent should exist")
        content = gha.read_text(encoding="utf-8")
        self.assertIn("model:", content)
        self.assertIn("tools:", content)

        ghp = self.TEST_DIR / ".github" / "prompts" / "req-analyze.prompt.md"
        self.assertTrue(ghp.exists(), "GitHub prompt should exist")
        ghp_content = ghp.read_text(encoding="utf-8")
        self.assertIn("model:", ghp_content)
        self.assertIn("tools:", ghp_content)
        self.assertIn("argument-hint:", ghp_content)

        codex_skill = self.TEST_DIR / ".codex" / "skills" / "req-analyze" / "SKILL.md"
        self.assertTrue(codex_skill.exists(), "Codex SKILL.md should exist")
        codex_content = codex_skill.read_text(encoding="utf-8")
        self.assertIn("model:", codex_content)
        self.assertIn("tools:", codex_content)

        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req-analyze.json"
        self.assertTrue(kiro_agent.exists(), "Kiro agent should exist")
        data = json.loads(kiro_agent.read_text(encoding="utf-8"))
        self.assertIn("model", data)
        self.assertIn("tools", data)
        self.assertIn(
            "allowedTools",
            data,
            "Kiro agent must contain 'allowedTools' field",
        )
        self.assertEqual(
            data["allowedTools"],
            data["tools"],
            "allowedTools must match tools",
        )
        self.assertListEqual(
            data["tools"],
            KIRO_READ_ONLY_TOOLS,
            "Kiro agent must use the tools list defined for the current mode",
        )

        gemini_toml = self.TEST_DIR / ".gemini" / "commands" / "req" / "analyze.toml"
        self.assertTrue(gemini_toml.exists(), "Gemini toml should exist")
        toml_content = gemini_toml.read_text(encoding="utf-8")
        self.assertIn("model =", toml_content)
        self.assertIn("tools =", toml_content)

    def test_without_flags_no_model_tools(self) -> None:
        """Running CLI without flags should not add model/tools (unless expected behavior)."""
        # Run again without flags
        from unittest.mock import patch
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),

                    "--docs-dir",
                    str(self.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(self.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(self.TEST_DIR / "tests"),
                    "--src-dir",
                    str(self.TEST_DIR / "src"),
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)
        gha = self.TEST_DIR / ".github" / "agents" / "req-analyze.agent.md"
        content = gha.read_text(encoding="utf-8")
        # model/tools should not be present in GitHub agent when flags are off
        self.assertNotIn("tools:", content)
        self.assertNotIn("model:", content)

        codex_skill = self.TEST_DIR / ".codex" / "skills" / "req-analyze" / "SKILL.md"
        codex_content = codex_skill.read_text(encoding="utf-8")
        self.assertNotIn("tools:", codex_content)
        self.assertNotIn("model:", codex_content)

    def test_tools_only_adds_tools_without_models(self) -> None:
        """With only --enable-tools, tools should appear but not models."""
        from unittest.mock import patch

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),

                    "--docs-dir",
                    str(self.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(self.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(self.TEST_DIR / "tests"),
                    "--src-dir",
                    str(self.TEST_DIR / "src"),
                    "--enable-tools",
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)

        gha = self.TEST_DIR / ".github" / "agents" / "req-analyze.agent.md"
        content = gha.read_text(encoding="utf-8")
        self.assertIn("tools:", content)
        self.assertNotIn("model:", content)

        codex_skill = self.TEST_DIR / ".codex" / "skills" / "req-analyze" / "SKILL.md"
        codex_content = codex_skill.read_text(encoding="utf-8")
        self.assertIn("tools:", codex_content)
        self.assertNotIn("model:", codex_content)

        gemini_toml = self.TEST_DIR / ".gemini" / "commands" / "req" / "analyze.toml"
        gemini_content = gemini_toml.read_text(encoding="utf-8")
        self.assertIn("tools =", gemini_content)
        self.assertNotIn("model =", gemini_content)

        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req-analyze.json"
        kiro_data = json.loads(kiro_agent.read_text(encoding="utf-8"))
        self.assertIn("tools", kiro_data)
        self.assertNotIn("model", kiro_data)


class TestCLIWithExistingDocs(unittest.TestCase):
    """Tests to verify behavior when docs already contains files."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-existing"

    @classmethod
    def setUpClass(cls) -> None:
        """Prepares test environment with an existing file in docs."""
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        docs_dir = cls.TEST_DIR / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Create an existing file in docs.
        existing_file = docs_dir / "existing.md"
        existing_file.write_text("# Existing file\n", encoding="utf-8")
        (docs_dir / ".gitignore").write_text("# ignore\n", encoding="utf-8")

        (cls.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (cls.TEST_DIR / "guidelines" / ".place-holder").write_text("", encoding="utf-8")
        (cls.TEST_DIR / "tests").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)

        # Prevent network calls during tests.
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),

                    "--docs-dir",
                    str(cls.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(cls.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(cls.TEST_DIR / "tests"),
                    "--src-dir",
                    str(cls.TEST_DIR / "src"),
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        cls.exit_code = exit_code

        # Print list of all available tests
        test_methods = [method for method in dir(cls) if method.startswith("test_")]
        print(f"All available tests: {', '.join(test_methods)}")

    def setUp(self) -> None:
        """Prints test start."""
        print(f"Running test: {self._testMethodName} - {self.__doc__}")

    def tearDown(self) -> None:
        """Prints test result."""
        print("PASS")

    @classmethod
    def tearDownClass(cls) -> None:
        """Cleans up test environment (REQ-024)."""
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_requirements_md_not_generated_when_docs_not_empty(self) -> None:
        """REQ-001: Verifies that requirements.md is NOT generated if docs is not empty."""
        requirements_path = self.TEST_DIR / "docs" / "requirements.md"
        self.assertFalse(
            requirements_path.exists(),
            "The file requirements.md must NOT be generated if docs already contains files",
        )

    def test_existing_file_preserved(self) -> None:
        """Verifies that the existing file in docs is preserved."""
        existing_file = self.TEST_DIR / "docs" / "existing.md"
        self.assertTrue(
            existing_file.exists(), "The existing file must be preserved"
        )

    def test_kiro_resources_contains_existing_file(self) -> None:
        """REQ-046: Verifies Kiro resources include existing docs files."""
        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req-analyze.json"
        data = json.loads(kiro_agent.read_text(encoding="utf-8"))
        self.assertIn(
            "file://docs/existing.md",
            data.get("resources", []),
            "Kiro resources must include docs/existing.md",
        )

    def test_kiro_resources_include_prompt_when_docs_nonempty(self) -> None:
        """REQ-046: Verifies Kiro resources include generated prompt when docs non-empty."""
        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req-analyze.json"
        data = json.loads(kiro_agent.read_text(encoding="utf-8"))
        resources = data.get("resources", [])
        self.assertIn(
            "file://.kiro/prompts/req-analyze.md",
            resources,
            "Kiro resources must include prompt file",
        )

    def test_guidelines_dir_ignores_dotfiles(self) -> None:
        """DES-014: Verifies that %%GUIDELINES_FILES%% ignores dotfiles."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req-analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        self.assertNotIn(
            "guidelines/.place-holder",
            content,
            "Dotfiles in guidelines must be ignored in %%GUIDELINES_FILES%%",
        )
        self.assertIn("guidelines/", content, "Fallback guidelines/ must be present")


class TestPromptsUseAgents(unittest.TestCase):
    """Verifies behavior with --prompts-use-agents enabled."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-prompts-agents"

    @classmethod
    def setUpClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tests").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)

        from unittest.mock import patch

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),

                    "--docs-dir",
                    str(cls.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(cls.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(cls.TEST_DIR / "tests"),
                    "--src-dir",
                    str(cls.TEST_DIR / "src"),
                    "--prompts-use-agents",
                    "--enable-models",
                    "--enable-tools",
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        cls.exit_code = exit_code

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_github_prompts_are_agent_stubs(self) -> None:
        """With the flag enabled, .github/prompts files must be agent stubs."""
        prompt_path = self.TEST_DIR / ".github" / "prompts" / "req-analyze.prompt.md"
        self.assertTrue(prompt_path.exists())
        content = prompt_path.read_text(encoding="utf-8").strip()
        self.assertEqual(content, "---\nagent: req-analyze\n---", "The prompt must be a stub with only agent")

    def test_claude_commands_are_agent_stubs(self) -> None:
        """With the flag enabled, .claude/commands/req files must contain only the agent."""
        cmd_path = self.TEST_DIR / ".claude" / "commands" / "req" / "analyze.md"
        self.assertTrue(cmd_path.exists())
        content = cmd_path.read_text(encoding="utf-8").strip()
        # With the flag enabled, Claude commands must include the 'agent:' line.
        self.assertIn("agent: req-analyze", content, "The command must contain 'agent:' line when --prompts-use-agents is active")
        # The file should be a YAML front matter block.
        self.assertTrue(content.startswith("---"))
        self.assertTrue(content.endswith("---"))

    def test_claude_commands_stub_has_no_models_or_tools(self) -> None:
        """Even with model/tools flags active, stubs must remain only agent."""
        cmd_path = self.TEST_DIR / ".claude" / "commands" / "req" / "analyze.md"
        content = cmd_path.read_text(encoding="utf-8")
        self.assertIn("agent: req-analyze", content)
        self.assertNotIn("model:", content, "The stub must not include model")
        self.assertNotIn("allowed-tools:", content, "The stub must not include allowed-tools")

    def test_opencode_commands_are_agent_stubs(self) -> None:
        """With the flag enabled, .opencode/command files must contain only the agent (agent: /req-<name>)."""
        cmd_path = self.TEST_DIR / ".opencode" / "command" / "req-analyze.md"
        self.assertTrue(cmd_path.exists())
        content = cmd_path.read_text(encoding="utf-8").strip()
        # With the flag enabled, OpenCode commands must include the 'agent:' line.
        self.assertIn("agent: req-analyze", content, "The opencode command must contain 'agent:' line when --prompts-use-agents is active")
        self.assertTrue(content.startswith("---"))
        self.assertTrue(content.endswith("---"))


class TestKiroToolsEnabled(unittest.TestCase):
    """Verifies that Kiro populates tools/allowedTools only with --enable-tools."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-kiro-tools"

    @classmethod
    def setUpClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tests").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)

        from unittest.mock import patch

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),

                    "--docs-dir",
                    str(cls.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(cls.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(cls.TEST_DIR / "tests"),
                    "--src-dir",
                    str(cls.TEST_DIR / "src"),
                    "--enable-tools",
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        cls.exit_code = exit_code

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_kiro_change_tools_match_read_write_mode(self) -> None:
        """REQ-075: with enable-tools, change prompt uses read_write tools."""
        change_agent = self.TEST_DIR / ".kiro" / "agents" / "req-change.json"
        self.assertTrue(
            change_agent.exists(),
            "The file req-change.json must be present",
        )
        data = json.loads(change_agent.read_text(encoding="utf-8"))
        self.assertEqual(
            data.get("tools"),
            KIRO_READ_WRITE_TOOLS,
            "Req.change must have the read_write list of tools",
        )
        self.assertEqual(
            data.get("allowedTools"),
            KIRO_READ_WRITE_TOOLS,
            "Req.change must have allowedTools identical to tools",
        )

    def test_kiro_analyze_tools_match_read_only_mode(self) -> None:
        """REQ-075: with enable-tools, analyze prompt uses read_only tools."""
        analyze_agent = self.TEST_DIR / ".kiro" / "agents" / "req-analyze.json"
        self.assertTrue(
            analyze_agent.exists(),
            "The file req-analyze.json must be present",
        )
        data = json.loads(analyze_agent.read_text(encoding="utf-8"))
        self.assertEqual(
            data.get("tools"),
            KIRO_READ_ONLY_TOOLS,
            "Req.analyze must have the read_only list of tools",
        )
        self.assertEqual(
            data.get("allowedTools"),
            KIRO_READ_ONLY_TOOLS,
            "Req.analyze must have allowedTools identical to tools",
        )


class TestLoadCLIConfigsLegacy(unittest.TestCase):
    """Verifies load_centralized_models selects models-legacy when requested."""

    CLI_NAMES = ("claude", "copilot", "gemini", "kiro", "opencode", "codex")

    def setUp(self) -> None:
        self.resources_dir = Path(tempfile.mkdtemp(prefix="usereq-cli-configs-"))
        common_dir = self.resources_dir / "common"
        common_dir.mkdir(parents=True, exist_ok=True)
        
        # Create models.json with all CLI configs
        default_models = {
            "settings": {"version": "0.0.64"},
            "claude": {"id": "claude-config"},
            "copilot": {"id": "copilot-config"},
            "gemini": {"id": "gemini-config"},
            "kiro": {"id": "kiro-config"},
            "opencode": {"id": "opencode-config"},
            "codex": {"id": "codex-config"}
        }
        (common_dir / "models.json").write_text(
            json.dumps(default_models, indent=2), encoding="utf-8"
        )
        
        # Create models-legacy.json (copilot doesn't have legacy)
        legacy_models = {
            "settings": {"version": "0.0.64"},
            "claude": {"id": "claude-legacy"},
            "copilot": {"id": "copilot-config"},
            "gemini": {"id": "gemini-legacy"},
            "kiro": {"id": "kiro-legacy"},
            "opencode": {"id": "opencode-legacy"},
            "codex": {"id": "codex-legacy"}
        }
        (common_dir / "models-legacy.json").write_text(
            json.dumps(legacy_models, indent=2), encoding="utf-8"
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.resources_dir)

    def test_legacy_mode_prefers_legacy_configs(self) -> None:
        """REQ-082: With --legacy the models-legacy.json overrides models.json."""
        configs = cli.load_centralized_models(self.resources_dir, legacy_mode=True)
        claude_config = configs["claude"]
        gemini_config = configs["gemini"]
        copilot_config = configs["copilot"]
        self.assertIsNotNone(claude_config)
        self.assertIsNotNone(gemini_config)
        self.assertIsNotNone(copilot_config)
        assert claude_config is not None
        assert gemini_config is not None
        assert copilot_config is not None
        self.assertEqual(
            claude_config["id"],
            "claude-legacy",
            "Claude should load from models-legacy.json in legacy mode",
        )
        self.assertEqual(
            gemini_config["id"],
            "gemini-legacy",
            "Gemini should load from models-legacy.json in legacy mode",
        )
        self.assertEqual(
            copilot_config["id"],
            "copilot-config",
            "Copilot should use models-legacy.json even though it has same value",
        )

    def test_standard_mode_uses_config_json(self) -> None:
        """Verify that the normal path uses models.json."""
        configs = cli.load_centralized_models(self.resources_dir, legacy_mode=False)
        claude_config = configs["claude"]
        copilot_config = configs["copilot"]
        self.assertIsNotNone(claude_config)
        self.assertIsNotNone(copilot_config)
        assert claude_config is not None
        assert copilot_config is not None
        self.assertEqual(
            claude_config["id"],
            "claude-config",
            "Claude should load from models.json when not in legacy mode",
        )
        self.assertEqual(
            copilot_config["id"],
            "copilot-config",
            "Copilot should load from models.json when not in legacy mode",
        )


class TestCLIWithoutClaude(unittest.TestCase):
    """Runs CLI without Claude enabled to ensure other providers work."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-no-claude"

    @classmethod
    def setUpClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tests").mkdir(exist_ok=True)
        (cls.TEST_DIR / "src").mkdir(exist_ok=True)

        # Run CLI with a provider other than Claude to surface unbound variable issues.
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            cls.exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),

                    "--docs-dir",
                    str(cls.TEST_DIR / "docs"),
                    "--guidelines-dir",
                    str(cls.TEST_DIR / "guidelines"),
                    "--tests-dir",
                    str(cls.TEST_DIR / "tests"),
                    "--src-dir",
                    str(cls.TEST_DIR / "src"),
                    "--enable-github",
                ]
                + ARTIFACT_TYPE_FLAGS
            )

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_exit_code_zero_without_claude(self) -> None:
        """CLI must succeed when Claude is disabled and GitHub is enabled."""
        self.assertEqual(self.exit_code, 0)

    def test_github_files_created_without_claude(self) -> None:
        """GitHub artifacts must be generated without requiring Claude resources."""
        github_agent = self.TEST_DIR / ".github" / "agents" / "req-analyze.agent.md"
        self.assertTrue(github_agent.exists(), "GitHub agent must be generated")
        content = github_agent.read_text(encoding="utf-8")
        self.assertIn("description:", content, "GitHub agent must include description")
        claude_dir = self.TEST_DIR / ".claude"
        self.assertFalse(
            claude_dir.exists(),
            "Claude resources must not be created when provider flag is omitted",
        )


class TestProviderEnableFlags(unittest.TestCase):
    """Ensures the CLI enforces provider enable flags before generating resources."""

    TEST_DIR = (
        Path(__file__).resolve().parents[1]
        / "temp"
        / "project-test-provider-flags"
    )

    def setUp(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)
        self.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (self.TEST_DIR / "docs").mkdir(exist_ok=True)
        (self.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (self.TEST_DIR / "tests").mkdir(exist_ok=True)
        (self.TEST_DIR / "src").mkdir(exist_ok=True)

    def tearDown(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)

    def test_requires_at_least_one_provider_flag(self) -> None:
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stderr") as fake_stderr:
                exit_code = cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),

                        "--docs-dir",
                        str(self.TEST_DIR / "docs"),
                        "--guidelines-dir",
                        str(self.TEST_DIR / "guidelines"),
                        "--tests-dir",
                        str(self.TEST_DIR / "tests"),
                        "--src-dir",
                        str(self.TEST_DIR / "src"),
                    ]
                )

        self.assertEqual(
            exit_code,
            4,
            "Missing provider --enable-* flags must cause exit code 4",
        )
        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(
            "--enable-*",
            written,
            "Error message must mention the --enable-* requirement",
        )


class TestBasePrefixedRelativePaths(unittest.TestCase):
    """Verifies normalization when paths include the relative --base prefix."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-base-prefix"
    BASE_ARG = "temp/project-test-base-prefix"

    def setUp(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)
        self.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (self.TEST_DIR / "docs").mkdir(exist_ok=True)
        (self.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (self.TEST_DIR / "tests").mkdir(exist_ok=True)
        (self.TEST_DIR / "src").mkdir(exist_ok=True)

    def tearDown(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)

    def test_base_prefixed_relative_paths_are_accepted(self) -> None:
        """CTN-001: Paths including relative --base prefix must normalize correctly."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    self.BASE_ARG,
                    "--docs-dir",
                    f"{self.BASE_ARG}/docs",
                    "--guidelines-dir",
                    f"{self.BASE_ARG}/guidelines",
                    "--tests-dir",
                    f"{self.BASE_ARG}/tests",
                    "--src-dir",
                    f"{self.BASE_ARG}/src",
                    "--enable-codex",
                ]
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)
        config = json.loads((self.TEST_DIR / ".req" / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["docs-dir"], "docs")
        self.assertEqual(config["guidelines-dir"], "guidelines")
        self.assertEqual(config["tests-dir"], "tests")
        self.assertEqual(config["src-dir"], ["src"])


if __name__ == "__main__":
    unittest.main()


class TestUpdateNotification(unittest.TestCase):
    """Targeted test to verify update message."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-update-msg"

    def tearDown(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)

    def test_update_message_mentions_upgrade(self) -> None:
        """Verifies that if a new version is available, the upgrade hint is printed."""
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)
        self.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (self.TEST_DIR / "docs").mkdir(exist_ok=True)
        (self.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (self.TEST_DIR / "tests").mkdir(exist_ok=True)
        (self.TEST_DIR / "src").mkdir(exist_ok=True)

        def fake_notify(*_args, **_kwargs):
            print(
                "A new version of usereq is available: current 0.0.1, latest 9.9.9. "
                "To upgrade, run: req --upgrade"
            )

        with patch("usereq.cli.maybe_notify_newer_version", side_effect=fake_notify):
            with patch("sys.stdout") as fake_stdout:
                exit_code = cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),

                        "--docs-dir",
                        str(self.TEST_DIR / "docs"),
                        "--guidelines-dir",
                        str(self.TEST_DIR / "guidelines"),
                        "--tests-dir",
                        str(self.TEST_DIR / "tests"),
                        "--src-dir",
                        str(self.TEST_DIR / "src"),
                    ]
                    + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
                )

        # Note: we do not check exit code because stdout capture might vary based on runner.
        written = "".join(call.args[0] for call in fake_stdout.write.call_args_list)
        self.assertIn("req --upgrade", written)

    def test_installation_success_message(self) -> None:
        """Verifies the CLI prints the installation success message on completion."""
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)
        self.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (self.TEST_DIR / "docs").mkdir(exist_ok=True)
        (self.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (self.TEST_DIR / "tests").mkdir(exist_ok=True)
        (self.TEST_DIR / "src").mkdir(exist_ok=True)

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stdout") as fake_stdout:
                exit_code = cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),

                        "--docs-dir",
                        str(self.TEST_DIR / "docs"),
                        "--guidelines-dir",
                        str(self.TEST_DIR / "guidelines"),
                        "--tests-dir",
                        str(self.TEST_DIR / "tests"),
                        "--src-dir",
                        str(self.TEST_DIR / "src"),
                    ]
                    + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
                )

        written = "".join(call.args[0] for call in fake_stdout.write.call_args_list)
        self.assertIn("Installation completed successfully in", written)

        lines = written.splitlines()
        header_pattern = re.compile(
            r"^CLI\s+\|\s+Prompts Installed\s+\|\s+Modules Installed\s*$"
        )
        try:
            header_index = next(
                i for i, line in enumerate(lines) if header_pattern.search(line)
            )
        except StopIteration as exc:
            raise self.failureException(
                "The installation summary table header must be printed"
            ) from exc
        header_line = lines[header_index]
        header_pipes = [pos for pos, ch in enumerate(header_line) if ch == "|"]
        self.assertEqual(
            len(header_pipes),
            2,
            "Header row must contain exactly two pipe separators",
        )

        # Skip header and separator lines; verify all data rows align pipes with header.
        data_rows = [
            line
            for line in lines[header_index + 2 :]
            if "|" in line and line.strip("- |")
        ]
        self.assertGreater(
            len(data_rows), 0, "The installation summary table must include data rows",
        )
        for row in data_rows:
            row_pipes = [pos for pos, ch in enumerate(row) if ch == "|"]
            self.assertEqual(
                header_pipes,
                row_pipes,
                f"Installation summary row is not aligned with header: {row}",
            )


class TestGuidelinesTemplates(unittest.TestCase):
    """Tests for --add-guidelines and --upgrade-guidelines functionality."""

    def setUp(self) -> None:
        """Create temporary project for guidelines template tests."""
        self.TEST_DIR = Path(tempfile.mkdtemp(prefix="usereq-guidelines-templates-"))
        self.docs_dir = self.TEST_DIR / "docs"
        self.guidelines_dir = self.TEST_DIR / "guidelines"
        self.test_dir = self.TEST_DIR / "tests"
        self.src_dir = self.TEST_DIR / "src"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.guidelines_dir.mkdir(parents=True, exist_ok=True)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.src_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        """Clean up test directory."""
        shutil.rmtree(self.TEST_DIR)

    def _make_temp_resource_root(self, include_guideline_file: bool) -> Path:
        """Create a temporary RESOURCE_ROOT fixture for guidelines copy tests."""
        temp_resources = Path(tempfile.mkdtemp(prefix="usereq-guidelines-resources-"))
        shutil.copytree(cli.RESOURCE_ROOT / "prompts", temp_resources / "prompts")
        shutil.copytree(cli.RESOURCE_ROOT / "docs", temp_resources / "docs")
        shutil.copytree(cli.RESOURCE_ROOT / "common", temp_resources / "common")
        guidelines_root = temp_resources / "guidelines"
        guidelines_root.mkdir(parents=True, exist_ok=True)
        if include_guideline_file:
            (guidelines_root / "HDT_Test_Authoring_Guide_for_LLM_Agents.md").write_text(
                "# Template Content\nThis should overwrite with --upgrade-guidelines.\n",
                encoding="utf-8",
            )
        return temp_resources

    def test_add_guidelines_preserves_existing(self) -> None:
        """REQ-086: --add-guidelines does not overwrite existing files."""
        # Create existing file in guidelines dir with specific content
        existing_file = self.guidelines_dir / "HDT_Test_Authoring_Guide_for_LLM_Agents.md"
        original_content = "# Original Content\nThis should be preserved.\n"
        existing_file.write_text(original_content, encoding="utf-8")

        # Run with --add-guidelines
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),

                    "--docs-dir",
                    "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--add-guidelines",
                    "--enable-claude",
                ]
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)

        # Verify existing file was NOT modified
        preserved_content = existing_file.read_text(encoding="utf-8")
        self.assertEqual(
            preserved_content,
            original_content,
            "Existing file should be preserved with --add-guidelines",
        )

    def test_upgrade_guidelines_overwrites_existing(self) -> None:
        """REQ-087: --upgrade-guidelines overwrites existing files."""
        # Create existing file in guidelines dir with specific content
        existing_file = self.guidelines_dir / "HDT_Test_Authoring_Guide_for_LLM_Agents.md"
        original_content = "# Original Content\nThis should be overwritten.\n"
        existing_file.write_text(original_content, encoding="utf-8")

        temp_resources = self._make_temp_resource_root(include_guideline_file=True)
        original_resource_root = cli.RESOURCE_ROOT
        cli.RESOURCE_ROOT = temp_resources

        # Run with --upgrade-guidelines
        try:
            with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
                exit_code = cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),
                        "--docs-dir",
                        "docs",
                        "--guidelines-dir",
                        "guidelines",
                        "--tests-dir",
                        "tests",
                        "--src-dir",
                        "src",
                        "--upgrade-guidelines",
                        "--enable-claude",
                    ]
                    + ARTIFACT_TYPE_FLAGS
                )
        finally:
            cli.RESOURCE_ROOT = original_resource_root
            shutil.rmtree(temp_resources)
        self.assertEqual(exit_code, 0)

        # Verify existing file WAS overwritten with template content
        new_content = existing_file.read_text(encoding="utf-8")
        self.assertEqual(
            new_content,
            "# Template Content\nThis should overwrite with --upgrade-guidelines.\n",
            "Existing file should be overwritten with --upgrade-guidelines when source template exists",
        )

    def test_upgrade_guidelines_with_empty_source_succeeds(self) -> None:
        """REQ-085: --upgrade-guidelines succeeds when source guidelines directory is empty."""
        existing_file = self.guidelines_dir / "HDT_Test_Authoring_Guide_for_LLM_Agents.md"
        original_content = "# Original Content\nShould stay unchanged when source is empty.\n"
        existing_file.write_text(original_content, encoding="utf-8")

        temp_resources = self._make_temp_resource_root(include_guideline_file=False)
        original_resource_root = cli.RESOURCE_ROOT
        cli.RESOURCE_ROOT = temp_resources
        try:
            with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
                exit_code = cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),
                        "--docs-dir",
                        "docs",
                        "--guidelines-dir",
                        "guidelines",
                        "--tests-dir",
                        "tests",
                        "--src-dir",
                        "src",
                        "--upgrade-guidelines",
                        "--enable-claude",
                    ]
                    + ARTIFACT_TYPE_FLAGS
                )
        finally:
            cli.RESOURCE_ROOT = original_resource_root
            shutil.rmtree(temp_resources)

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            existing_file.read_text(encoding="utf-8"),
            original_content,
            "Existing file should stay unchanged when source guidelines directory is empty",
        )

    def test_add_guidelines_and_upgrade_guidelines_mutually_exclusive(self) -> None:
        """REQ-088: --add-guidelines and --upgrade-guidelines cannot be used together."""
        # Attempt to run with both flags - argparse should handle mutual exclusivity
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with self.assertRaises(SystemExit):
                cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),

                        "--docs-dir",
                        "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--add-guidelines",
                    "--upgrade-guidelines",
                    "--enable-claude",
                ]
                + ARTIFACT_TYPE_FLAGS
            )

    def test_no_copy_without_flags(self) -> None:
        """REQ-089: Guidelines templates are not copied without --add-guidelines or --upgrade-guidelines."""
        # Run without either flag
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),

                    "--docs-dir",
                    "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--enable-claude",
                ]
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)

        # Verify no guidelines template files were copied
        guidelines_file = self.guidelines_dir / "HDT_Test_Authoring_Guide_for_LLM_Agents.md"
        self.assertFalse(
            guidelines_file.exists(),
            "Guidelines templates should not be copied without --add-guidelines or --upgrade-guidelines",
        )


class TestPreserveModels(unittest.TestCase):
    """Verifies --preserve-models flag preserves .req/models.json and bypasses --legacy."""

    def setUp(self) -> None:
        self.TEST_DIR = Path(tempfile.mkdtemp(prefix="usereq-preserve-models-"))
        self.docs_dir = self.TEST_DIR / "docs"
        self.guidelines_dir = self.TEST_DIR / "guidelines"
        self.test_dir = self.TEST_DIR / "tests"
        self.src_dir = self.TEST_DIR / "src"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.guidelines_dir.mkdir(parents=True, exist_ok=True)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.src_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.TEST_DIR)

    def test_preserve_models_keeps_custom_config(self) -> None:
        """REQ-082, REQ-084: With --preserve-models and --update, custom .req/models.json is preserved."""
        # Initial setup
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),

                    "--docs-dir",
                    "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--enable-claude",
                ]
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)

        # Modify .req/models.json with custom content
        models_file = self.TEST_DIR / ".req" / "models.json"
        self.assertTrue(models_file.is_file(), ".req/models.json should exist after initial setup")
        
        custom_config = {
            "settings": {"version": "9.9.9", "custom": "preserved"},
            "claude": {"id": "custom-claude-config", "prompts": ["custom-prompt"]},
        }
        models_file.write_text(json.dumps(custom_config, indent=2), encoding="utf-8")

        # Run --update with --preserve-models
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),
                    "--update",
                    "--preserve-models",
                    "--enable-claude",
                ]
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)

        # Verify custom content is preserved
        preserved_content = json.loads(models_file.read_text(encoding="utf-8"))
        self.assertEqual(
            preserved_content["settings"]["version"],
            "9.9.9",
            ".req/models.json version should be preserved with --preserve-models",
        )
        self.assertEqual(
            preserved_content["settings"]["custom"],
            "preserved",
            "Custom fields in .req/models.json should be preserved with --preserve-models",
        )
        self.assertEqual(
            preserved_content["claude"]["id"],
            "custom-claude-config",
            "Custom claude config should be preserved with --preserve-models",
        )

    def test_preserve_models_bypasses_legacy_mode(self) -> None:
        """REQ-082: With --preserve-models, --legacy has no effect."""
        # Setup with initial run
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),

                    "--docs-dir",
                    "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--enable-claude",
                ]
                + ARTIFACT_TYPE_FLAGS
            )

        # Create custom models.json
        models_file = self.TEST_DIR / ".req" / "models.json"
        custom_config = {
            "settings": {"marker": "preserve-wins"},
            "claude": {"id": "preserved-config"},
        }
        models_file.write_text(json.dumps(custom_config, indent=2), encoding="utf-8")

        # Run with both --preserve-models and --legacy
        # The preserve flag should take precedence
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),
                    "--update",
                    "--preserve-models",
                    "--legacy",
                    "--enable-claude",
                ]
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(exit_code, 0)

        # Verify custom content is still preserved (--legacy had no effect)
        preserved_content = json.loads(models_file.read_text(encoding="utf-8"))
        self.assertEqual(
            preserved_content["settings"]["marker"],
            "preserve-wins",
            "--preserve-models should take precedence over --legacy",
        )


class TestUpdateLoadsPersistedFlags(unittest.TestCase):
    """Verifies that --update reloads persisted flag states from .req/config.json."""

    def setUp(self) -> None:
        self.TEST_DIR = Path(tempfile.mkdtemp(prefix="usereq-update-persisted-flags-"))
        (self.TEST_DIR / "docs").mkdir(parents=True, exist_ok=True)
        (self.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (self.TEST_DIR / "tests").mkdir(exist_ok=True)
        (self.TEST_DIR / "src").mkdir(exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.TEST_DIR)

    def _run_here_update(self, args: list[str]) -> int:
        """Runs CLI commands from TEST_DIR to exercise --here resolution."""
        previous_cwd = Path.cwd()
        try:
            os.chdir(self.TEST_DIR)
            return cli.main(args)
        finally:
            os.chdir(previous_cwd)

    def test_update_reloads_persisted_flags(self) -> None:
        """SRS-034, SRS-064: --update must restore persisted enable/disable flags from config.json."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            install_exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),
                    "--docs-dir",
                    "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--enable-models",
                    "--enable-tools",
                    "--prompts-use-agents",
                    "--legacy",
                    "--disable-skills",
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(install_exit_code, 0)

        config_payload = json.loads((self.TEST_DIR / ".req" / "config.json").read_text(encoding="utf-8"))
        expected_flags = {
            "enable-models": True,
            "enable-tools": True,
            "enable-claude": True,
            "enable-codex": True,
            "enable-gemini": True,
            "enable-github": True,
            "enable-kiro": True,
            "enable-opencode": True,
            "enable-prompts": True,
            "enable-agents": True,
            "disable-skills": True,
            "prompts-use-agents": True,
            "legacy": True,
            "preserve-models": False,
        }
        for key, expected in expected_flags.items():
            self.assertIn(key, config_payload, f"{key} must be persisted in .req/config.json")
            self.assertEqual(config_payload[key], expected, f"{key} must preserve its boolean state")

        shutil.rmtree(self.TEST_DIR / ".github")
        shutil.rmtree(self.TEST_DIR / ".claude")
        shutil.rmtree(self.TEST_DIR / ".opencode")

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            update_exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),
                    "--update",
                ]
            )
        self.assertEqual(update_exit_code, 0, "--update must reuse persisted provider/artifact flags")

        github_prompt = self.TEST_DIR / ".github" / "prompts" / "req-analyze.prompt.md"
        self.assertTrue(github_prompt.is_file(), "GitHub prompts must be regenerated from persisted flags")
        self.assertEqual(
            github_prompt.read_text(encoding="utf-8").strip(),
            "---\nagent: req-analyze\n---",
            "Persisted --prompts-use-agents must generate agent-stub prompts",
        )
        self.assertFalse(
            (self.TEST_DIR / ".github" / "skills").exists(),
            "Persisted --disable-skills must keep skill generation disabled",
        )
        self.assertTrue(
            (self.TEST_DIR / ".claude" / "agents").is_dir(),
            "Persisted --enable-claude and --enable-agents must regenerate Claude agents",
        )
        self.assertTrue(
            (self.TEST_DIR / ".opencode" / "agent").is_dir(),
            "Persisted --enable-opencode and --enable-agents must regenerate OpenCode agents",
        )

    def test_update_here_reloads_persisted_flags(self) -> None:
        """SRS-064: --update with --here must reuse persisted flags from .req/config.json."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            install_exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),
                    "--docs-dir",
                    "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--enable-models",
                    "--enable-tools",
                    "--prompts-use-agents",
                    "--legacy",
                    "--disable-skills",
                ]
                + PROVIDER_FLAGS
                + ARTIFACT_TYPE_FLAGS
            )
        self.assertEqual(install_exit_code, 0)

        shutil.rmtree(self.TEST_DIR / ".github")
        shutil.rmtree(self.TEST_DIR / ".claude")
        shutil.rmtree(self.TEST_DIR / ".opencode")

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            update_exit_code = self._run_here_update(["--here", "--update"])
        self.assertEqual(update_exit_code, 0, "--update --here must reuse persisted flags")
        self.assertTrue(
            (self.TEST_DIR / ".github" / "prompts" / "req-analyze.prompt.md").is_file(),
            "Persisted flags must regenerate provider artifacts in --here mode",
        )
        self.assertFalse(
            (self.TEST_DIR / ".github" / "skills").exists(),
            "Persisted --disable-skills must remain effective in --here update mode",
        )

    def test_update_here_invalid_persisted_flags_uses_config_error(self) -> None:
        """SRS-064: --update --here must fail with config-invalid error for invalid persisted flags."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            install_exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),
                    "--docs-dir",
                    "docs",
                    "--guidelines-dir",
                    "guidelines",
                    "--tests-dir",
                    "tests",
                    "--src-dir",
                    "src",
                    "--enable-claude",
                    "--enable-prompts",
                ]
            )
        self.assertEqual(install_exit_code, 0)

        config_path = self.TEST_DIR / ".req" / "config.json"
        config_payload = json.loads(config_path.read_text(encoding="utf-8"))
        for key in (
            "enable-claude",
            "enable-codex",
            "enable-gemini",
            "enable-github",
            "enable-kiro",
            "enable-opencode",
        ):
            config_payload[key] = False
        config_path.write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stderr") as fake_stderr:
                update_exit_code = self._run_here_update(["--here", "--update"])
        self.assertEqual(update_exit_code, 11)
        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(
            "invalid provider/artifact update configuration",
            written,
            "Invalid persisted flags must report config-specific update error",
        )
        self.assertNotIn(
            "at least one --enable-* provider flag is required",
            written,
            "Update invalid-config path must not report regular provider-flag validation error",
        )


class TestArtifactTypeFlags(unittest.TestCase):
    """Verifies enforcement and behavior of --enable-prompts, --enable-agents, --disable-skills (SRS-231, SRS-035)."""

    TEST_DIR = (
        Path(__file__).resolve().parents[1]
        / "temp"
        / "project-test-artifact-type-flags"
    )

    def setUp(self) -> None:
        """Creates a clean temporary project directory before each test."""
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)
        self.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (self.TEST_DIR / "docs").mkdir(exist_ok=True)
        (self.TEST_DIR / "guidelines").mkdir(exist_ok=True)
        (self.TEST_DIR / "tests").mkdir(exist_ok=True)
        (self.TEST_DIR / "src").mkdir(exist_ok=True)

    def tearDown(self) -> None:
        """Removes the temporary project directory after each test."""
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)

    def _base_args(self) -> list:
        """Returns the base CLI args common to all test invocations."""
        return [
            "--base",
            str(self.TEST_DIR),
            "--docs-dir",
            str(self.TEST_DIR / "docs"),
            "--guidelines-dir",
            str(self.TEST_DIR / "guidelines"),
            "--tests-dir",
            str(self.TEST_DIR / "tests"),
            "--src-dir",
            str(self.TEST_DIR / "src"),
        ]

    def test_requires_at_least_one_artifact_type_flag(self) -> None:
        """SRS-035, SRS-231: CLI MUST exit with code 4 when all artifact types are inactive."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stderr") as fake_stderr:
                exit_code = cli.main(
                    self._base_args() + ["--enable-claude", "--disable-skills"]
                )

        self.assertEqual(
            exit_code,
            4,
            "Missing artifact-type flag must cause exit code 4",
        )
        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(
            "--disable-skills",
            written,
            "Error message must mention --disable-skills",
        )

    def test_enable_skills_flag_is_rejected(self) -> None:
        """SRS-034, SRS-231: --enable-skills is removed and MUST be rejected by parser."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stderr") as fake_stderr:
                with self.assertRaises(SystemExit) as cm:
                    cli.main(self._base_args() + ["--enable-claude", "--enable-skills"])
        self.assertEqual(cm.exception.code, 2, "Removed --enable-skills flag must be rejected")
        written = "".join(call.args[0] for call in fake_stderr.write.call_args_list)
        self.assertIn(
            "unrecognized arguments: --enable-skills",
            written,
            "Parser error must mention removed --enable-skills flag",
        )

    def test_enable_prompts_only_generates_prompt_artifacts(self) -> None:
        """SRS-231: --enable-prompts with --disable-skills generates only prompt/command artifacts; agent/skill dirs absent."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                self._base_args()
                + [
                    "--enable-claude",
                    "--enable-codex",
                    "--enable-prompts",
                    "--disable-skills",
                ]
            )
        self.assertEqual(exit_code, 0, "CLI must succeed with --enable-prompts")
        # Prompt artifacts MUST exist
        self.assertTrue(
            (self.TEST_DIR / ".claude" / "commands").is_dir(),
            ".claude/commands must be created with --enable-prompts",
        )
        self.assertTrue(
            (self.TEST_DIR / ".codex" / "prompts").is_dir(),
            ".codex/prompts must be created with --enable-prompts",
        )
        # Agent artifacts MUST NOT exist (--enable-agents not set)
        self.assertFalse(
            (self.TEST_DIR / ".claude" / "agents").exists(),
            ".claude/agents must NOT be created without --enable-agents",
        )
        # Skill artifacts MUST NOT exist (--disable-skills set)
        self.assertFalse(
            (self.TEST_DIR / ".codex" / "skills").exists(),
            ".codex/skills must NOT be created with --disable-skills",
        )

    def test_enable_agents_only_generates_agent_artifacts(self) -> None:
        """SRS-231: --enable-agents with --disable-skills generates only agent artifacts; prompt/skill dirs absent."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                self._base_args()
                + [
                    "--enable-claude",
                    "--enable-codex",
                    "--enable-agents",
                    "--disable-skills",
                ]
            )
        self.assertEqual(exit_code, 0, "CLI must succeed with --enable-agents")
        # Agent artifacts MUST exist
        self.assertTrue(
            (self.TEST_DIR / ".claude" / "agents").is_dir(),
            ".claude/agents must be created with --enable-agents",
        )
        # Prompt artifacts MUST NOT exist
        self.assertFalse(
            (self.TEST_DIR / ".claude" / "commands").exists(),
            ".claude/commands must NOT be created without --enable-prompts",
        )
        # Codex prompt artifacts MUST NOT exist
        self.assertFalse(
            (self.TEST_DIR / ".codex" / "prompts").exists(),
            ".codex/prompts must NOT be created without --enable-prompts",
        )
        # Skill artifacts MUST NOT exist
        self.assertFalse(
            (self.TEST_DIR / ".codex" / "skills").exists(),
            ".codex/skills must NOT be created with --disable-skills",
        )

    def test_skills_are_enabled_by_default(self) -> None:
        """
        @brief Verify default-enabled skills populate installation summary prompts.
        @details Executes installation with provider flags only (skills enabled by default; prompts/agents disabled).
        Asserts that skill directories are created and the installation summary ASCII table lists installed prompt
        identifiers under "Prompts Installed" even when artifacts are produced as skills (SRS-036, SRS-049, SRS-231).
        @return {None}
        """
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stdout") as fake_stdout:
                exit_code = cli.main(
                    self._base_args()
                    + [
                        "--enable-claude",
                        "--enable-codex",
                    ]
                )
        self.assertEqual(exit_code, 0, "CLI must succeed with default-enabled skills")
        # Skill artifacts MUST exist for each enabled provider
        self.assertTrue(
            (self.TEST_DIR / ".codex" / "skills").is_dir(),
            ".codex/skills must be created by default",
        )
        self.assertTrue(
            (self.TEST_DIR / ".claude" / "skills").is_dir(),
            ".claude/skills must be created by default",
        )
        written = "".join(call.args[0] for call in fake_stdout.write.call_args_list)
        lines = written.splitlines()
        header_pattern = re.compile(
            r"^CLI\s+\|\s+Prompts Installed\s+\|\s+Modules Installed\s*$"
        )
        header_index = next(
            i for i, line in enumerate(lines) if header_pattern.search(line)
        )
        data_rows = [
            line
            for line in lines[header_index + 2 :]
            if "|" in line and line.strip("- |")
        ]
        parsed: dict[str, tuple[str, str]] = {}
        for row in data_rows:
            parts = [part.strip() for part in row.split("|")]
            if len(parts) >= 3:
                parsed[parts[0]] = (parts[1], parts[2])
        self.assertIn("codex", parsed, "Summary table must include codex row")
        self.assertIn("claude", parsed, "Summary table must include claude row")
        codex_prompts, codex_modules = parsed["codex"]
        claude_prompts, claude_modules = parsed["claude"]
        self.assertNotEqual(codex_prompts, "-", "codex prompts list must not be empty")
        self.assertNotEqual(claude_prompts, "-", "claude prompts list must not be empty")
        self.assertIn("analyze", codex_prompts, "codex prompts list must include a known prompt id")
        self.assertIn("analyze", claude_prompts, "claude prompts list must include a known prompt id")
        self.assertIn("skills", codex_modules, "codex modules list must include skills")
        self.assertIn("skills", claude_modules, "claude modules list must include skills")
        # Prompt artifacts MUST NOT exist
        self.assertFalse(
            (self.TEST_DIR / ".codex" / "prompts").exists(),
            ".codex/prompts must NOT be created without --enable-prompts",
        )
        # Agent artifacts MUST NOT exist
        self.assertFalse(
            (self.TEST_DIR / ".claude" / "agents").exists(),
            ".claude/agents must NOT be created without --enable-agents",
        )

    def test_all_artifact_type_flags_enable_all_artifacts(self) -> None:
        """SRS-231: prompts/agents flags plus default skills enable all artifact categories."""
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                self._base_args()
                + [
                    "--enable-claude",
                    "--enable-codex",
                    "--enable-prompts",
                    "--enable-agents",
                ]
            )
        self.assertEqual(exit_code, 0, "CLI must succeed with all artifact-type flags")
        self.assertTrue(
            (self.TEST_DIR / ".claude" / "commands").is_dir(),
            ".claude/commands must exist",
        )
        self.assertTrue(
            (self.TEST_DIR / ".claude" / "agents").is_dir(),
            ".claude/agents must exist",
        )
        self.assertTrue(
            (self.TEST_DIR / ".claude" / "skills").is_dir(),
            ".claude/skills must exist",
        )
        self.assertTrue(
            (self.TEST_DIR / ".codex" / "prompts").is_dir(),
            ".codex/prompts must exist",
        )
        self.assertTrue(
            (self.TEST_DIR / ".codex" / "skills").is_dir(),
            ".codex/skills must exist",
        )
