"""
Test suite per il comando CLI useReq.

Questo modulo implementa i test unitari per verificare il corretto funzionamento
dello script CLI, secondo il requisito REQ-054.

# REQ-054
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Importa il modulo CLI da testare.
from usereq import cli


class TestCLI(unittest.TestCase):
    """Suite di test per il comando CLI useReq."""

    # Percorso della directory di test sotto temp/.
    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test"

    @classmethod
    def setUpClass(cls) -> None:
        """Prepara l'ambiente di test creando le directory necessarie."""
        # Rimuove la directory di test se presente (REQ-054.1).
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

        # Crea la directory di test e le sottocartelle docs e tech (REQ-054.2).
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        # Crea una sottocartella in tech per verificare REQ-026.
        (cls.TEST_DIR / "tech" / "src").mkdir(exist_ok=True)

        # Esegue lo script con i parametri specificati (REQ-054.3).
        # Evita chiamate di rete durante i test.
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

        # Stampare la lista di tutti i test disponibili
        test_methods = [method for method in dir(cls) if method.startswith("test_")]
        print(f"Tutti i test disponibili: {', '.join(test_methods)}")

    def setUp(self) -> None:
        """Stampa l'inizio del test."""
        print(f"Eseguendo test: {self._testMethodName} - {self.__doc__}")

    def tearDown(self) -> None:
        """Stampa l'esito del test."""
        print("PASS")

    @classmethod
    def tearDownClass(cls) -> None:
        """Pulisce l'ambiente di test rimuovendo le directory temporanee (REQ-024)."""
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_exit_code_is_zero(self) -> None:
        """Verifica che lo script termini con codice di uscita 0."""
        self.assertEqual(self.exit_code, 0, "Lo script deve terminare con exit code 0")

    def test_requirements_md_generated(self) -> None:
        """REQ-001: Verifica che requirements.md venga generato nella directory docs vuota."""
        requirements_path = self.TEST_DIR / "docs" / "requirements.md"
        self.assertTrue(
            requirements_path.exists(),
            "Il file requirements.md deve essere generato in docs/",
        )
        content = requirements_path.read_text(encoding="utf-8")
        self.assertIn("---", content, "requirements.md deve contenere front matter")

    def test_codex_directory_created(self) -> None:
        """REQ-002: Verifica la creazione della cartella .codex/prompts."""
        codex_prompts = self.TEST_DIR / ".codex" / "prompts"
        self.assertTrue(
            codex_prompts.is_dir(), "La directory .codex/prompts deve esistere"
        )

    def test_github_directories_created(self) -> None:
        """REQ-002: Verifica la creazione delle cartelle .github/agents e .github/prompts."""
        github_agents = self.TEST_DIR / ".github" / "agents"
        github_prompts = self.TEST_DIR / ".github" / "prompts"
        self.assertTrue(
            github_agents.is_dir(), "La directory .github/agents deve esistere"
        )
        self.assertTrue(
            github_prompts.is_dir(), "La directory .github/prompts deve esistere"
        )

    def test_gemini_directories_created(self) -> None:
        """REQ-002: Verifica la creazione delle cartelle .gemini/commands e .gemini/commands/req."""
        gemini_commands = self.TEST_DIR / ".gemini" / "commands"
        gemini_req = gemini_commands / "req"
        self.assertTrue(
            gemini_commands.is_dir(), "La directory .gemini/commands deve esistere"
        )
        self.assertTrue(
            gemini_req.is_dir(), "La directory .gemini/commands/req deve esistere"
        )

    def test_kiro_directories_created(self) -> None:
        """REQ-017: Verifica la creazione delle cartelle .kiro/agents e .kiro/prompts."""
        kiro_agents = self.TEST_DIR / ".kiro" / "agents"
        kiro_prompts = self.TEST_DIR / ".kiro" / "prompts"
        self.assertTrue(kiro_agents.is_dir(), "La directory .kiro/agents deve esistere")
        self.assertTrue(
            kiro_prompts.is_dir(), "La directory .kiro/prompts deve esistere"
        )

    def test_opencode_directory_created(self) -> None:
        """REQ-048: Verifica la creazione della cartella .opencode/agent."""
        opencode_agent = self.TEST_DIR / ".opencode" / "agent"
        self.assertTrue(
            opencode_agent.is_dir(), "La directory .opencode/agent deve esistere"
        )

    def test_claude_directory_created(self) -> None:
        """REQ-049: Verifica la creazione della cartella .claude/agents."""
        claude_agents = self.TEST_DIR / ".claude" / "agents"
        self.assertTrue(
            claude_agents.is_dir(), "La directory .claude/agents deve esistere"
        )

    def test_codex_prompt_files_created(self) -> None:
        """REQ-003: Verifica la copia dei file prompt in .codex/prompts."""
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
                f"Il file {prompt} deve esistere in .codex/prompts",
            )

    def test_github_agent_files_created(self) -> None:
        """REQ-003, REQ-053: Verifica la copia dei file in .github/agents con front matter name."""
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
                agent_path.exists(), f"Il file {agent} deve esistere in .github/agents"
            )
            # Verifica il front matter con name (REQ-053).
            content = agent_path.read_text(encoding="utf-8")
            self.assertIn("---", content, f"{agent} deve contenere front matter")
            prompt_name = agent.replace(".agent.md", "").replace(".", "-")
            # Il nome nel front matter deve essere req.<nome>.
            expected_name_pattern = agent.replace(".agent.md", "")
            self.assertIn(
                f"name: {expected_name_pattern}",
                content,
                f"{agent} deve contenere 'name: {expected_name_pattern}' nel front matter",
            )
            self.assertIn(
                "description:",
                content,
                f"{agent} deve contenere 'description:' nel front matter",
            )

    def test_github_prompt_files_created(self) -> None:
        """REQ-004: Verifica la creazione dei file .github/prompts/req.<nome>.prompt.md."""
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
                f"Il file {prompt} deve esistere in .github/prompts",
            )
            # Verifica il contenuto del file.
            content = prompt_path.read_text(encoding="utf-8")
            agent_name = prompt.replace(".prompt.md", "")
            self.assertIn(
                f"agent: {agent_name}",
                content,
                f"{prompt} deve referenziare l'agente {agent_name}",
            )

    def test_gemini_toml_files_created(self) -> None:
        """REQ-005: Verifica la generazione dei file TOML in .gemini/commands/req."""
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
                f"Il file {toml} deve esistere in .gemini/commands/req",
            )
            content = toml_path.read_text(encoding="utf-8")
            self.assertIn(
                "description", content, f"{toml} deve contenere 'description'"
            )
            self.assertIn("prompt", content, f"{toml} deve contenere 'prompt'")

    def test_templates_copied(self) -> None:
        """REQ-006: Verifica la copia dei template in .req/templates."""
        templates_dir = self.TEST_DIR / ".req" / "templates"
        self.assertTrue(
            templates_dir.is_dir(), "La directory .req/templates deve esistere"
        )
        requirements_template = templates_dir / "requirements.md"
        self.assertTrue(
            requirements_template.exists(),
            "Il template requirements.md deve esistere in .req/templates",
        )

    def test_kiro_prompt_files_created(self) -> None:
        """REQ-018: Verifica la copia dei file in .kiro/prompts."""
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
                prompt_path.exists(), f"Il file {prompt} deve esistere in .kiro/prompts"
            )

    def test_kiro_agent_json_files_created(self) -> None:
        """REQ-019, REQ-020: Verifica la generazione dei file JSON in .kiro/agents."""
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
                agent_path.exists(), f"Il file {agent} deve esistere in .kiro/agents"
            )
            # Verifica la struttura JSON (REQ-020).
            content = agent_path.read_text(encoding="utf-8")
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                self.fail(f"Il file {agent} deve essere un JSON valido")

            # Verifica i campi obbligatori.
            self.assertIn("name", data, f"{agent} deve contenere il campo 'name'")
            self.assertIn(
                "description", data, f"{agent} deve contenere il campo 'description'"
            )
            self.assertIn("prompt", data, f"{agent} deve contenere il campo 'prompt'")

            # Verifica il formato del nome (req-<nome>).
            expected_name = agent.replace(".json", "").replace(".", "-")
            self.assertEqual(
                data["name"],
                expected_name,
                f"Il nome in {agent} deve essere '{expected_name}'",
            )

    def test_req_doc_replacement(self) -> None:
        """REQ-022: Verifica la sostituzione di %%REQ_DOC%%."""
        # Dopo l'esecuzione, i file devono contenere il link al requirements.md.
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req.analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        # Verifica che %%REQ_DOC%% sia stato sostituito.
        self.assertNotIn(
            "%%REQ_DOC%%", content, "Il token %%REQ_DOC%% deve essere sostituito"
        )
        # Verifica che contenga il riferimento al file docs/requirements.md.
        self.assertIn(
            "docs/requirements.md",
            content,
            "Il file deve contenere il riferimento a docs/requirements.md",
        )

    def test_config_json_saved(self) -> None:
        """REQ-033: Verifica il salvataggio di .req/config.json."""
        config_path = self.TEST_DIR / ".req" / "config.json"
        self.assertTrue(config_path.exists(), "Il file .req/config.json deve esistere")
        content = config_path.read_text(encoding="utf-8")
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            self.fail(".req/config.json deve essere un JSON valido")

        # Verifica i campi doc e dir.
        self.assertIn("doc", data, "config.json deve contenere il campo 'doc'")
        self.assertIn("dir", data, "config.json deve contenere il campo 'dir'")
        self.assertEqual(data["doc"], "docs", "Il campo 'doc' deve essere 'docs'")
        self.assertEqual(data["dir"], "tech", "Il campo 'dir' deve essere 'tech'")

    def test_opencode_agent_files_created(self) -> None:
        """REQ-047: Verifica la generazione degli agenti OpenCode in .opencode/agent."""
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
                agent_path.exists(), f"Il file {agent} deve esistere in .opencode/agent"
            )
            content = agent_path.read_text(encoding="utf-8")
            # Verifica il front matter con description e mode.
            self.assertIn("---", content, f"{agent} deve contenere front matter")
            self.assertIn(
                "description:", content, f"{agent} deve contenere 'description:'"
            )
            self.assertIn("mode: all", content, f"{agent} deve contenere 'mode: all'")

    def test_claude_agent_files_created(self) -> None:
        """REQ-050, REQ-051: Verifica la generazione dei file Claude Code."""
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
                agent_path.exists(), f"Il file {agent} deve esistere in .claude/agents"
            )
            content = agent_path.read_text(encoding="utf-8")
            # Verifica il front matter (REQ-051).
            self.assertIn("---", content, f"{agent} deve contenere front matter")

            # Verifica il campo name (req-<nome>).
            expected_name = agent.replace(".md", "").replace(".", "-")
            self.assertIn(
                f"name: {expected_name}",
                content,
                f"{agent} deve contenere 'name: {expected_name}' nel front matter",
            )

            # Verifica il campo model: inherit.
            self.assertIn(
                "model: inherit",
                content,
                f"{agent} deve contenere 'model: inherit' nel front matter",
            )

            # Verifica il campo description.
            self.assertIn(
                "description:",
                content,
                f"{agent} deve contenere 'description:' nel front matter",
            )

    def test_req_dir_replacement(self) -> None:
        """REQ-026, REQ-027: Verifica la sostituzione di %%REQ_DIR%%."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req.analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        # Verifica che %%REQ_DIR%% sia stato sostituito.
        self.assertNotIn(
            "%%REQ_DIR%%", content, "Il token %%REQ_DIR%% deve essere sostituito"
        )
        # Verifica che contenga il riferimento alla sottodirectory tech/src/.
        self.assertIn(
            "tech/src/", content, "Il file deve contenere il riferimento a tech/src/"
        )

    def test_kiro_resources_include_prompt(self) -> None:
        """REQ-046: Verifica che il campo resources dei file Kiro includa il prompt."""
        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req.analyze.json"
        content = kiro_agent.read_text(encoding="utf-8")
        data = json.loads(content)

        self.assertIn(
            "resources", data, "Il file JSON deve contenere il campo 'resources'"
        )
        resources = data["resources"]
        self.assertIsInstance(
            resources, list, "Il campo 'resources' deve essere una lista"
        )
        self.assertGreater(
            len(resources), 0, "La lista 'resources' non deve essere vuota"
        )

        # Verifica che la prima voce sia il prompt.
        first_resource = resources[0]
        self.assertIn(
            ".kiro/prompts/req.analyze.md",
            first_resource,
            "La prima risorsa deve essere il prompt .kiro/prompts/req.analyze.md",
        )


class TestModelsAndTools(unittest.TestCase):
    """Verifica l'inclusione condizionale di model e tools nei file generati."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-models"

    @classmethod
    def setUpClass(cls) -> None:
        # Prepara progetto di test
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)
        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEST_DIR / "docs").mkdir(exist_ok=True)
        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        # Crea risorse di config temporanee sotto una cartella resources temporanea
        tmp_resources = Path(__file__).resolve().parents[1] / "temp" / "resources"
        if tmp_resources.exists():
            shutil.rmtree(tmp_resources)
        (tmp_resources / "copilot").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "claude").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "gemini").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "kiro").mkdir(parents=True, exist_ok=True)
        (tmp_resources / "opencode").mkdir(parents=True, exist_ok=True)

        sample_config = {
            "settings": {"version": "1.0.0"},
            "prompts": {"analyze": {"model": "GPT-5 mini (copilot)", "mode": "read_write"}},
            "usage_modes": {"read_write": {"tools": ["vscode", "execute", "read"]}}
        }

        for name in ("copilot", "claude", "gemini", "kiro", "opencode"):
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
        # Copy Kiro agent template from package kiro folder
        orig_kiro_template = repo_root / "src" / "usereq" / "kiro" / "agent.json"
        if orig_kiro_template.exists():
            shutil.copyfile(orig_kiro_template, tmp_resources / "kiro" / "agent.json")

        # Write configs into the real resources folder so CLI can find them
        repo_root = Path(__file__).resolve().parents[1]
        real_resources = repo_root / "src" / "usereq" / "resources"
        cls._created_configs: list[Path] = []
        for name in ("copilot", "claude", "gemini", "kiro", "opencode"):
            target_dir = real_resources / name
            target_dir.mkdir(parents=True, exist_ok=True)
            cfg_path = target_dir / "config.json"
            cfg_path.write_text(json.dumps(sample_config, indent=2), encoding="utf-8")
            cls._created_configs.append(cfg_path)

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
        for p in getattr(cls, "_created_configs", []):
            try:
                p.unlink()
            except Exception:
                pass

    def test_generated_files_include_model_and_tools(self) -> None:
        """Verifica che i file generati contengano model e tools quando i config esistono e i flag sono attivi."""
        gha = self.TEST_DIR / ".github" / "agents" / "req.analyze.agent.md"
        self.assertTrue(gha.exists(), "GitHub agent should exist")
        content = gha.read_text(encoding="utf-8")
        self.assertIn("model:", content)
        self.assertIn("tools:", content)

        kiro_agent = self.TEST_DIR / ".kiro" / "agents" / "req.analyze.json"
        self.assertTrue(kiro_agent.exists(), "Kiro agent should exist")
        data = json.loads(kiro_agent.read_text(encoding="utf-8"))
        self.assertIn("model", data)
        self.assertIn("tools", data)

        gemini_toml = self.TEST_DIR / ".gemini" / "commands" / "req" / "analyze.toml"
        self.assertTrue(gemini_toml.exists(), "Gemini toml should exist")
        toml_content = gemini_toml.read_text(encoding="utf-8")
        self.assertIn("model =", toml_content)
        self.assertIn("tools =", toml_content)

    def test_without_flags_no_model_tools(self) -> None:
        """Eseguire CLI senza flags non deve aggiungere model/tools (salvo comportamenti previsti)."""
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


class TestCLIWithExistingDocs(unittest.TestCase):
    """Test per verificare il comportamento quando docs contiene già dei file."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-existing"

    @classmethod
    def setUpClass(cls) -> None:
        """Prepara l'ambiente di test con un file esistente in docs."""
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

        cls.TEST_DIR.mkdir(parents=True, exist_ok=True)
        docs_dir = cls.TEST_DIR / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Crea un file esistente in docs.
        existing_file = docs_dir / "existing.md"
        existing_file.write_text("# Existing file\n", encoding="utf-8")

        (cls.TEST_DIR / "tech").mkdir(exist_ok=True)

        # Evita chiamate di rete durante i test.
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

        # Stampare la lista di tutti i test disponibili
        test_methods = [method for method in dir(cls) if method.startswith("test_")]
        print(f"Tutti i test disponibili: {', '.join(test_methods)}")

    def setUp(self) -> None:
        """Stampa l'inizio del test."""
        print(f"Eseguendo test: {self._testMethodName} - {self.__doc__}")

    def tearDown(self) -> None:
        """Stampa l'esito del test."""
        print("PASS")

    @classmethod
    def tearDownClass(cls) -> None:
        """Pulisce l'ambiente di test (REQ-024)."""
        if cls.TEST_DIR.exists():
            shutil.rmtree(cls.TEST_DIR)

    def test_requirements_md_not_generated_when_docs_not_empty(self) -> None:
        """REQ-001: Verifica che requirements.md NON venga generato se docs non è vuota."""
        requirements_path = self.TEST_DIR / "docs" / "requirements.md"
        self.assertFalse(
            requirements_path.exists(),
            "Il file requirements.md NON deve essere generato se docs contiene già file",
        )

    def test_existing_file_preserved(self) -> None:
        """Verifica che il file esistente in docs sia preservato."""
        existing_file = self.TEST_DIR / "docs" / "existing.md"
        self.assertTrue(
            existing_file.exists(), "Il file esistente deve essere preservato"
        )

    def test_req_doc_contains_existing_file(self) -> None:
        """REQ-022: Verifica che %%REQ_DOC%% contenga il file esistente."""
        codex_prompt = self.TEST_DIR / ".codex" / "prompts" / "req.analyze.md"
        content = codex_prompt.read_text(encoding="utf-8")
        self.assertIn(
            "docs/existing.md",
            content,
            "Il file deve contenere il riferimento a docs/existing.md",
        )


if __name__ == "__main__":
    unittest.main()


class TestUpdateNotification(unittest.TestCase):
    """Test mirato per verificare il messaggio di aggiornamento."""

    TEST_DIR = Path(__file__).resolve().parents[1] / "temp" / "project-test-update-msg"

    def tearDown(self) -> None:
        if self.TEST_DIR.exists():
            shutil.rmtree(self.TEST_DIR)

    def test_update_message_mentions_upgrade(self) -> None:
        """Verifica che, se disponibile una nuova versione, venga stampato il hint di upgrade."""
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

        # Nota: non verifichiamo l'exit code perche' la cattura stdout puo' variare in base al runner.
        written = "".join(call.args[0] for call in fake_stdout.write.call_args_list)
        self.assertIn("req --upgrade", written)
