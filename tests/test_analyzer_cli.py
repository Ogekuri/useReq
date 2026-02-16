"""Test per l'interfaccia CLI di source_analyzer.py."""

import os
import subprocess
import sys
import pytest


ANALYZER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "src", "usereq", "source_analyzer.py"
)


def run_analyzer(*args, expect_success=True):
    """Esegue source_analyzer.py come subprocess e restituisce il risultato."""
    cmd = [sys.executable, ANALYZER_PATH] + list(args)
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30
    )
    if expect_success:
        assert result.returncode == 0, (
            f"Comando fallito (rc={result.returncode}):\n"
            f"  cmd: {' '.join(cmd)}\n"
            f"  stderr: {result.stderr}"
        )
    return result


class TestCLIHelp:
    """Test per --help."""

    def test_help_exit_code(self):
        """--help deve uscire con codice 0."""
        result = run_analyzer("--help")
        assert result.returncode == 0

    def test_help_contains_usage(self):
        """--help deve mostrare informazioni di uso."""
        result = run_analyzer("--help")
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout

    def test_help_lists_languages(self):
        """--help deve menzionare alcuni linguaggi."""
        result = run_analyzer("--help")
        output = result.stdout.lower()
        assert "python" in output
        assert "rust" in output


class TestCLIBasicUsage:
    """Test per l'uso base della CLI."""

    def test_analyze_python_fixture(self, fixtures_dir):
        """Analisi di una fixture Python deve produrre output."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python")
        assert len(result.stdout) > 0
        assert "FUNCTION" in result.stdout or "CLASS" in result.stdout

    def test_analyze_c_fixture(self, fixtures_dir):
        """Analisi di una fixture C."""
        path = os.path.join(fixtures_dir, "fixture_c.c")
        result = run_analyzer(path, "c")
        assert "FUNCTION" in result.stdout
        assert "STRUCT" in result.stdout

    def test_analyze_rust_fixture(self, fixtures_dir):
        """Analisi di una fixture Rust."""
        path = os.path.join(fixtures_dir, "fixture_rust.rs")
        result = run_analyzer(path, "rust")
        assert "FUNCTION" in result.stdout
        assert "STRUCT" in result.stdout


class TestCLIFlags:
    """Test per i flag opzionali."""

    def test_quiet_mode(self, fixtures_dir):
        """Il flag -q deve produrre output semplificato."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python", "-q")
        # In quiet mode non ci deve essere l'intestazione con "==="
        assert "======" not in result.stdout
        # Ma deve contenere output
        assert len(result.stdout.strip()) > 0

    def test_definitions_only(self, fixtures_dir):
        """The -d flag should show only definitions."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python", "-d")
        assert "DEFINITIONS" in result.stdout or "FUNCTION" in result.stdout
        # No separate comments section
        lines = result.stdout.split("\n")
        comment_section = [l for l in lines if "COMMENTS (" in l]
        assert len(comment_section) == 0

    def test_comments_only(self, fixtures_dir):
        """The -c flag should show only comments."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python", "-c")
        assert "COMMENT" in result.stdout
        # No definitions section
        lines = result.stdout.split("\n")
        def_section = [l for l in lines if "DEFINITIONS (" in l]
        assert len(def_section) == 0


class TestCLIErrors:
    """Test per gli errori CLI."""

    def test_missing_arguments(self):
        """Senza argomenti deve fallire."""
        result = run_analyzer(expect_success=False)
        assert result.returncode != 0

    def test_nonexistent_file(self):
        """Nonexistent file should fail with code 1."""
        result = run_analyzer("/nonexistent/file.py", "python",
                              expect_success=False)
        assert result.returncode == 1
        assert "Error" in result.stderr or "error" in result.stderr.lower()

    def test_unsupported_language(self, fixtures_dir):
        """Unsupported language should fail with code 1."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "fortran", expect_success=False)
        assert result.returncode == 1
        assert "not supported" in result.stderr


class TestCLIOutputFormat:
    """Test per il formato dell'output CLI."""

    def test_output_has_header(self, fixtures_dir):
        """L'output deve contenere un'intestazione con separatore."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python")
        assert "=====" in result.stdout

    def test_output_has_language_info(self, fixtures_dir):
        """L'output deve indicare il linguaggio."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python")
        assert "Python" in result.stdout or "python" in result.stdout

    def test_output_has_element_count(self, fixtures_dir):
        """Output should contain element count."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python")
        assert "Elements found:" in result.stdout

    def test_output_has_line_numbers(self, fixtures_dir):
        """L'output deve contenere numeri di riga (Lxx)."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python")
        assert "L1" in result.stdout or "L2" in result.stdout

    def test_quiet_output_has_line_numbers(self, fixtures_dir):
        """Anche in modalita' quiet deve avere numeri di riga."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        result = run_analyzer(path, "python", "-q")
        # Deve avere il formato "  N | [TYPE]"
        import re
        assert re.search(r"\d+\s*\|\s*\[", result.stdout), \
            "Output quiet senza numeri di riga"
