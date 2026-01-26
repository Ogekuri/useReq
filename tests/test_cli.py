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
from usereq.pdoc_utils import generate_pdoc_docs

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


class TestCLI(unittest.TestCase):
    """Test suite for the useReq CLI command."""
    # Test directory path under temp/.
    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test"

    @classmethod
    def setUpClass(cls) -> None:
        """Prepares the test environment by creating necessary directories."""
        # Removes the test directory if present (REQ-054.1).
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

        # Creates the test directory and docs/tech subfolders (REQ-054.2).
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        # Creates a subfolder in tech to verify REQ-026.
        (cls.TEST_DIR / "tech" / "src").mkdir(exist_ok=True)

        # Executes the script with specified parameters (REQ-054.3).
        # Avoids network calls during tests.
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),
                    "--doc",
                    str(cls.TEST_DIR / "docs"),
                    "--dir",
                    str(cls.TEST_DIR / "tech"),
                ]
            )
        cls.exit_code = exit_code

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

    def test_requirements_md_generated(self) -> None:
        """REQ-001: Verifies that requirements.md is generated in the empty docs directory."""
        requirements_path = self.TEST_DIR / "docs" / "requirements.md"
        self.assertTrue(
            requirements_path.exists(),
            "The file requirements.md must be generated in docs/",
        )
        content = requirements_path.read_text(encoding="utf-8")
        self.assertIn("---", content, "requirements.md must contain front matter")

    def test_codex_directory_created(self) -> None:
        """REQ-002: Verifies the creation of the .codex/prompts directory."""
        codex_prompts = self.TEST_DIR / ".codex" / "prompts"
        self.assertTrue(
            codex_prompts.is_dir(), "The directory .codex/prompts must exist"
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
            "req.analyze.md",
            "req.change.md",
            "req.check.md",
            "req.cover.md",
            "req.fix.md",
            "req.new.md",
            "req.optimize.md",
            "req.write.md",
        ]
        for prompt in expected_prompts:
            prompt_path = codex_prompts / prompt
            self.assertTrue(
                prompt_path.exists(),
                f"The file {prompt} must exist in .codex/prompts",
            )

    def test_github_agent_files_created(self) -> None:
        """REQ-003, REQ-053: Verifies copy of files into .github/agents with front matter name."""
        github_agents = self.TEST_DIR / ".github" / "agents"
        expected_agents = [
            "req.analyze.agent.md",
            "req.change.agent.md",
            "req.check.agent.md",
            "req.cover.agent.md",
            "req.fix.agent.md",
            "req.new.agent.md",
            "req.optimize.agent.md",
            "req.write.agent.md",
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
        """REQ-004: Verifies the creation of .github/prompts/req.<name>.prompt.md files."""
        github_prompts = self.TEST_DIR / ".github" / "prompts"
        expected_prompts = [
            "req.analyze.prompt.md",
            "req.change.prompt.md",
            "req.check.prompt.md",
            "req.cover.prompt.md",
            "req.fix.prompt.md",
            "req.new.prompt.md",
            "req.optimize.prompt.md",
            "req.write.prompt.md",
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
        """REQ-005: Verifies TOML files generation in .gemini/commands/req."""
        gemini_req = self.TEST_DIR / ".gemini" / "commands" / "req"
        expected_toml = [
            "analyze.toml",
            "change.toml",
            "check.toml",
            "cover.toml",
            "fix.toml",
            "new.toml",
            "optimize.toml",
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
        """REQ-006: Verifies copy of templates into .req/templates."""
        templates_dir = self.TEST_DIR / ".req" / "templates"
        self.assertTrue(
            templates_dir.is_dir(), "The directory .req/templates must exist"
        )
        requirements_template = templates_dir / "requirements.md"
        self.assertTrue(
            requirements_template.exists(),
            "The template requirements.md must exist in .req/templates",
        )

    def test_kiro_prompt_files_created(self) -> None:
        """REQ-018: Verifies copy of files into .kiro/prompts."""
        kiro_prompts = self.TEST_DIR / ".kiro" / "prompts"
        expected_prompts = [
            "req.analyze.md",
            "req.change.md",
            "req.check.md",
            "req.cover.md",
            "req.fix.md",
            "req.new.md",
            "req.optimize.md",
            "req.write.md",
        ]
        for prompt in expected_prompts:
            prompt_path = kiro_prompts / prompt
            self.assertTrue(
                prompt_path.exists(), f"The file {prompt} must exist in .kiro/prompts"
            )

    def test_codex_kiro_prompt_contents_match(self) -> None:
        """Verifies that Codex and Kiro prompt contents match after replacement."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req.analyze.md"
        kiro_prompt = self.TEST_DIR / ".kiro" / "prompts" / "req.analyze.md"
        codex_content = codex_prompt.read_text(encoding="utf-8")
        kiro_content = kiro_prompt.read_text(encoding="utf-8")
        self.assertEqual(
            codex_content,
            kiro_content,
            "Codex and Kiro prompt files must have identical contents",
        )

    def test_terminate_token_replaced_by_default(self) -> None:
        """REQ-076: Verifies no 'workflow' prompt files are generated by default."""
        # When --enable-workflow is not provided, no files for the 'workflow'
        # prompt must be created in generated locations.
        codex_workflow = self.TEST_DIR / ".codex" / "prompts" / "req.workflow.md"
        gh_agent = self.TEST_DIR / ".github" / "agents" / "req.workflow.agent.md"
        kiro_prompt = self.TEST_DIR / ".kiro" / "prompts" / "req.workflow.md"
        claude_agent = self.TEST_DIR / ".claude" / "agents" / "req.workflow.md"

        self.assertFalse(codex_workflow.exists(), "No .codex workflow prompt must be generated by default")
        self.assertFalse(gh_agent.exists(), "No .github workflow agent must be generated by default")
        self.assertFalse(kiro_prompt.exists(), "No .kiro workflow prompt must be generated by default")
        self.assertFalse(claude_agent.exists(), "No .claude workflow agent must be generated by default")

    def test_bootstrap_token_replaced(self) -> None:
        # Removed: obsolete test for REQ-077 (bootstrap substitution no longer performed).
        pass

    def test_kiro_agent_json_files_created(self) -> None:
        """REQ-019, REQ-020: Verifies JSON files generation in .kiro/agents."""
        kiro_agents = self.TEST_DIR / ".kiro" / "agents"
        expected_agents = [
            "req.analyze.json",
            "req.change.json",
            "req.check.json",
            "req.cover.json",
            "req.fix.json",
            "req.new.json",
            "req.optimize.json",
            "req.write.json",
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

    def test_req_doc_replacement(self) -> None:
        """REQ-022: Verifies %%REQ_DOC%% replacement."""
        # After execution, files must contain link to requirements.md.
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req.analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        # Verify that %%REQ_DOC%% has been replaced.
        self.assertNotIn(
            "%%REQ_DOC%%", content, "The token %%REQ_DOC%% must be replaced"
        )
        # Verify that it contains reference to docs/requirements.md.
        self.assertIn(
            "docs/requirements.md",
            content,
            "The file must contain reference to docs/requirements.md",
        )

    def test_config_json_saved(self) -> None:
        """REQ-033: Verifies saving of .req/config.json."""
        config_path = self.TEST_DIR / ".req" / "config.json"
        self.assertTrue(config_path.exists(), "The file .req/config.json must exist")
        content = config_path.read_text(encoding="utf-8")
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            self.fail(".req/config.json must be a valid JSON")

        # Verify fields doc and dir.
        self.assertIn("doc", data, "config.json must contain 'doc' field")
        self.assertIn("dir", data, "config.json must contain 'dir' field")
        self.assertEqual(data["doc"], "docs", "The 'doc' field must be 'docs'")
        self.assertEqual(data["dir"], "tech", "The 'dir' field must be 'tech'")

    def test_opencode_agent_files_created(self) -> None:
        """REQ-047: Verifies OpenCode agents generation in .opencode/agent."""
        opencode_agent = self.TEST_DIR / ".opencode" / "agent"
        expected_agents = [
            "req.analyze.md",
            "req.change.md",
            "req.check.md",
            "req.cover.md",
            "req.fix.md",
            "req.new.md",
            "req.optimize.md",
            "req.write.md",
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

    def test_pdoc_documentation_generated(self) -> None:
        """REQ-081: Verifies pdoc documentation is generated in the pdoc/ folder."""
        output_dir = self.TEST_DIR / "pdoc"
        generate_pdoc_docs(output_dir)
        self.assertTrue(output_dir.exists(), "The pdoc/ directory must be created")
        html_files = list(output_dir.glob("*.html"))
        self.assertTrue(html_files, "The pdoc/ directory must contain HTML files")

    def test_opencode_command_contains_metadata(self) -> None:
        """Verifies that .opencode/command files include description and argument-hint."""
        cmd_path = self.TEST_DIR / ".opencode" / "command" / "req.analyze.md"
        self.assertTrue(cmd_path.exists(), "The opencode command must exist")
        content = cmd_path.read_text(encoding="utf-8")
        self.assertIn("description:", content, "Must include description in front matter")
        self.assertIn("argument-hint:", content, "Must include argument-hint in front matter")

    def test_claude_agent_files_created(self) -> None:
        """REQ-050, REQ-051: Verifies Claude Code files generation."""
        claude_agents = self.TEST_DIR / ".claude" / "agents"
        expected_agents = [
            "req.analyze.md",
            "req.change.md",
            "req.check.md",
            "req.cover.md",
            "req.fix.md",
            "req.new.md",
            "req.optimize.md",
            "req.write.md",
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
        """REQ-026, REQ-027: Verifies %%REQ_DIR%% replacement."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req.analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        # Verify that %%REQ_DIR%% has been replaced.
        self.assertNotIn(
            "%%REQ_DIR%%", content, "The token %%REQ_DIR%% must be replaced"
        )
        # Verify that it contains reference to subdirectory tech/src/.
        self.assertIn(
            "tech/src/", content, "The file must contain reference to tech/src/"
        )

    def test_kiro_resources_include_prompt(self) -> None:
        """REQ-046: Verifies that Kiro resources field includes the prompt."""
        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req.analyze.json"
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
            ".kiro/prompts/req.analyze.md",
            first_resource,
            "The first resource must be the prompt .kiro/prompts/req.analyze.md",
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
        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        # Create temporary config resources under a temporary resources folder
        tmp_resources = Path(__file__).resolve().parents[1] / "temp" / "resources"
        if tmp_resources.exists():
            shutil.rmtree(tmp_resources)
        (tmp_resources / "copilot").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "claude").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "gemini").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "kiro").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "opencode").mkdir(parents=True, exist_ok=True)

        cls._tmp_resources = tmp_resources
        cls._orig_resource_root = cli.RESOURCE_ROOT

        base_usage = {"read_write": {"tools": ["vscode", "execute", "read"]}}
        claude_usage = {"read_write": {"tools": ["Read", "Grep", "Glob"]}}

        for name in ("copilot", "claude", "gemini", "kiro", "opencode"):
            sample_config = {
                "settings": {"version": "1.0.0"},
                "prompts": {"analyze": {"model": "GPT-5.1-Codex-Mini (copilot)", "mode": "read_write"}},
            }
            if name == "claude":
                sample_config["usage_modes"] = claude_usage
            else:
                sample_config["usage_modes"] = base_usage
            cfg_path = tmp_resources / name / "config.json"
            cfg_path.write_text(json.dumps(sample_config, indent=2), encoding="utf-8")

        # Copy existing prompts and templates into tmp_resources so CLI finds them
        repo_root = Path(__file__).resolve().parents[1]
        orig_resources = repo_root / "src" / "usereq" / "resources"
        if (orig_resources / "prompts").is_dir():
            shutil.copytree(orig_resources / "prompts", tmp_resources / "prompts")
        if (orig_resources / "templates").is_dir():
            (tmp_resources / "templates").mkdir(parents=True, exist_ok=True)
            tmpl = orig_resources / "templates" / "requirements.md"
            if tmpl.exists():
                shutil.copyfile(tmpl, tmp_resources / "templates" / "requirements.md")

        # Use temporary resources as CLI root, without touching project files.
        cli.RESOURCE_ROOT = tmp_resources

        # Run CLI with flags enabled
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),
                    "--doc",
                    str(cls.TEST_DIR / "docs"),
                    "--dir",
                    str(cls.TEST_DIR / "tech"),
                    "--enable-models",
                    "--enable-tools",
                ]
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
        gha = self.TEST_DIR / ".github" / "agents" / "req.analyze.agent.md"
        self.assertTrue(gha.exists(), "GitHub agent should exist")
        content = gha.read_text(encoding="utf-8")
        self.assertIn("model:", content)
        self.assertIn("tools:", content)

        ghp = self.TEST_DIR / ".github" / "prompts" / "req.analyze.prompt.md"
        self.assertTrue(ghp.exists(), "GitHub prompt should exist")
        ghp_content = ghp.read_text(encoding="utf-8")
        self.assertIn("model:", ghp_content)
        self.assertIn("tools:", ghp_content)
        self.assertIn("argument-hint:", ghp_content)

        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req.analyze.json"
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
                    "--doc",
                    str(self.TEST_DIR / "docs"),
                    "--dir",
                    str(self.TEST_DIR / "tech"),
                ]
            )
        self.assertEqual(exit_code, 0)
        gha = self.TEST_DIR / ".github" / "agents" / "req.analyze.agent.md"
        content = gha.read_text(encoding="utf-8")
        # model/tools should not be present in GitHub agent when flags are off
        self.assertNotIn("tools:", content)
        self.assertNotIn("model:", content)

    def test_tools_only_adds_tools_without_models(self) -> None:
        """With only --enable-tools, tools should appear but not models."""
        from unittest.mock import patch

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(self.TEST_DIR),
                    "--doc",
                    str(self.TEST_DIR / "docs"),
                    "--dir",
                    str(self.TEST_DIR / "tech"),
                    "--enable-tools",
                ]
            )
        self.assertEqual(exit_code, 0)

        gha = self.TEST_DIR / ".github" / "agents" / "req.analyze.agent.md"
        content = gha.read_text(encoding="utf-8")
        self.assertIn("tools:", content)
        self.assertNotIn("model:", content)

        gemini_toml = self.TEST_DIR / ".gemini" / "commands" / "req" / "analyze.toml"
        gemini_content = gemini_toml.read_text(encoding="utf-8")
        self.assertIn("tools =", gemini_content)
        self.assertNotIn("model =", gemini_content)

        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req.analyze.json"
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

        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        # Prevent network calls during tests.
        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),
                    "--doc",
                    str(cls.TEST_DIR / "docs"),
                    "--dir",
                    str(cls.TEST_DIR / "tech"),
                ]
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

    def test_req_doc_contains_existing_file(self) -> None:
        """REQ-022: Verifies that %%REQ_DOC%% contains the existing file."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req.analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        self.assertIn(
            "docs/existing.md",
            content,
            "The file must contain reference to docs/existing.md",
        )


class TestPromptsUseAgents(unittest.TestCase):
    """Verifies behavior with --prompts-use-agents enabled."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-prompts-agents"

    @classmethod
    def setUpClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        from unittest.mock import patch

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),
                    "--doc",
                    str(cls.TEST_DIR / "docs"),
                    "--dir",
                    str(cls.TEST_DIR / "tech"),
                    "--prompts-use-agents",
                    "--enable-models",
                    "--enable-tools",
                ]
            )
        cls.exit_code = exit_code

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_github_prompts_are_agent_stubs(self) -> None:
        """With the flag enabled, .github/prompts files must be agent stubs."""
        prompt_path = self.TEST_DIR / ".github" / "prompts" / "req.analyze.prompt.md"
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
        """With the flag enabled, .opencode/command files must contain only the agent (agent: req.<name>)."""
        cmd_path = self.TEST_DIR / ".opencode" / "command" / "req.analyze.md"
        self.assertTrue(cmd_path.exists())
        content = cmd_path.read_text(encoding="utf-8").strip()
        # With the flag enabled, OpenCode commands must include the 'agent:' line.
        self.assertIn("agent: req.analyze", content, "The opencode command must contain 'agent:' line when --prompts-use-agents is active")
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
        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        from unittest.mock import patch

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            exit_code = cli.main(
                [
                    "--base",
                    str(cls.TEST_DIR),
                    "--doc",
                    str(cls.TEST_DIR / "docs"),
                    "--dir",
                    str(cls.TEST_DIR / "tech"),
                    "--enable-tools",
                ]
            )
        cls.exit_code = exit_code

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_kiro_change_tools_match_read_write_mode(self) -> None:
        """REQ-075: with enable-tools, change prompt uses read_write tools."""
        change_agent = self.TEST_DIR / ".kiro" / "agents" / "req.change.json"
        self.assertTrue(
            change_agent.exists(),
            "The file req.change.json must be present",
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
        analyze_agent = self.TEST_DIR / ".kiro" / "agents" / "req.analyze.json"
        self.assertTrue(
            analyze_agent.exists(),
            "The file req.analyze.json must be present",
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
        (self.TEST_DIR / "tech").mkdir(exist_ok=True)

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
                        "--doc",
                        str(self.TEST_DIR / "docs"),
                        "--dir",
                        str(self.TEST_DIR / "tech"),
                    ]
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
        (self.TEST_DIR / "tech").mkdir(exist_ok=True)

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stdout") as fake_stdout:
                exit_code = cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),
                        "--doc",
                        str(self.TEST_DIR / "docs"),
                        "--dir",
                        str(self.TEST_DIR / "tech"),
                    ]
                )

        written = "".join(call.args[0] for call in fake_stdout.write.call_args_list)
        self.assertIn("Installation completed successfully in", written)

        lines = written.splitlines()
        header_pattern = re.compile(
            r"^CLI\s+\|\s+Modules Installed\s+\|\s+Workflow Installed\s*$"
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
            len(header_pipes), 2, "Header row must contain exactly two pipe separators",
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

    def test_workflow_summary_marks_yes(self) -> None:
        """The summary table must mark workflow as installed when the flag is enabled."""
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)
        self.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (self.TEST_DIR / "docs").mkdir(exist_ok=True)
        (self.TEST_DIR / "tech").mkdir(exist_ok=True)

        with patch("usereq.cli.maybe_notify_newer_version", autospec=True):
            with patch("sys.stdout") as fake_stdout:
                exit_code = cli.main(
                    [
                        "--base",
                        str(self.TEST_DIR),
                        "--doc",
                        "docs",
                        "--dir",
                        "tech",
                        "--enable-workflow",
                    ]
                )

        self.assertEqual(exit_code, 0)

        written = "".join(call.args[0] for call in fake_stdout.write.call_args_list)
        lines = written.splitlines()
        header_pattern = re.compile(
            r"^CLI\s+\|\s+Modules Installed\s+\|\s+Workflow Installed\s*$"
        )
        try:
            header_index = next(
                i for i, line in enumerate(lines) if header_pattern.search(line)
            )
        except StopIteration as exc:
            raise self.failureException(
                "The installation summary table header must be printed"
            ) from exc

        data_rows = [
            line
            for line in lines[header_index + 2 :]
            if "|" in line and line.strip("- |")
        ]
        self.assertGreater(
            len(data_rows), 0, "The summary table must contain data rows",
        )

        for row in data_rows:
            parts = [col.strip() for col in row.split("|")]
            self.assertGreaterEqual(
                len(parts), 3, f"Row must contain three columns: {row}"
            )
            self.assertEqual(
                parts[2],
                "Yes",
                "Workflow Installed column must be 'Yes' when --enable-workflow is provided",
            )
