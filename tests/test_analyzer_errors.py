"""Test per la gestione degli errori e casi limite."""

import os
import tempfile
import pytest

from usereq.source_analyzer import SourceAnalyzer, ElementType


class TestUnsupportedLanguage:
    """Test per linguaggi non supportati."""

    def test_raises_value_error(self, analyzer):
        """Unknown language should raise ValueError."""
        with pytest.raises(ValueError, match="not supported"):
            analyzer.analyze("dummy.txt", "brainfuck")

    def test_error_message_contains_language(self, analyzer):
        """Il messaggio di errore deve contenere il nome del linguaggio."""
        with pytest.raises(ValueError, match="xyz"):
            analyzer.analyze("dummy.txt", "xyz")

    def test_error_message_lists_supported(self, analyzer):
        """Il messaggio di errore deve elencare i linguaggi supportati."""
        try:
            analyzer.analyze("dummy.txt", "unknown")
        except ValueError as e:
            msg = str(e)
            assert "python" in msg
            assert "rust" in msg
            assert "javascript" in msg


class TestFileNotFound:
    """Test per file inesistenti."""

    def test_raises_file_not_found(self, analyzer):
        """File inesistente deve lanciare FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze("/nonexistent/path/file.py", "python")

    def test_raises_for_directory(self, analyzer):
        """Una directory non e' un file valido."""
        with pytest.raises((FileNotFoundError, IsADirectoryError)):
            analyzer.analyze("/tmp", "python")


class TestEmptyFile:
    """Test per file vuoti."""

    def test_empty_file_returns_empty(self, analyzer, temp_output_dir):
        """Un file vuoto deve restituire una lista vuota."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                          delete=False, dir=temp_output_dir) as f:
            f.write("")
            path = f.name
        try:
            elements = analyzer.analyze(path, "python")
            assert elements == []
        finally:
            os.unlink(path)

    def test_whitespace_only_file(self, analyzer, temp_output_dir):
        """Un file con solo spazi bianchi deve restituire lista vuota."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                          delete=False, dir=temp_output_dir) as f:
            f.write("   \n\n  \n")
            path = f.name
        try:
            elements = analyzer.analyze(path, "python")
            assert elements == []
        finally:
            os.unlink(path)


class TestLanguageNormalization:
    """Test per la normalizzazione del parametro linguaggio."""

    def test_uppercase(self, analyzer, fixtures_dir):
        """Il linguaggio in maiuscolo deve funzionare."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        elements = analyzer.analyze(path, "PYTHON")
        assert len(elements) > 0

    def test_mixed_case(self, analyzer, fixtures_dir):
        """Il linguaggio con case misto deve funzionare."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        elements = analyzer.analyze(path, "Python")
        assert len(elements) > 0

    def test_with_leading_dot(self, analyzer, fixtures_dir):
        """Il linguaggio con punto iniziale deve funzionare (es: .py)."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        elements = analyzer.analyze(path, ".py")
        assert len(elements) > 0

    def test_with_spaces(self, analyzer, fixtures_dir):
        """Il linguaggio con spazi intorno deve funzionare."""
        path = os.path.join(fixtures_dir, "fixture_python.py")
        elements = analyzer.analyze(path, "  python  ")
        assert len(elements) > 0

    def test_dot_and_upper(self, analyzer, fixtures_dir):
        """Combinazione punto + maiuscolo deve funzionare."""
        path = os.path.join(fixtures_dir, "fixture_rust.rs")
        elements = analyzer.analyze(path, ".RS")
        assert len(elements) > 0


class TestSupportedLanguages:
    """Test per get_supported_languages()."""

    def test_returns_list(self, analyzer):
        """get_supported_languages() deve restituire una lista."""
        langs = analyzer.get_supported_languages()
        assert isinstance(langs, list)

    def test_contains_all_core_languages(self, analyzer):
        """Deve contenere tutti i 20 linguaggi principali."""
        langs = analyzer.get_supported_languages()
        core = [
            "python", "c", "cpp", "rust", "javascript", "typescript",
            "java", "go", "ruby", "php", "swift", "kotlin", "scala",
            "lua", "shell", "perl", "haskell", "zig", "elixir", "csharp",
        ]
        for lang in core:
            assert lang in langs, f"Linguaggio '{lang}' mancante"

    def test_no_aliases_in_list(self, analyzer):
        """La lista non deve contenere alias come 'js', 'ts', ecc."""
        langs = analyzer.get_supported_languages()
        # Gli alias non dovrebbero apparire come linguaggi separati
        # (hanno lo stesso id(spec))
        aliases = ["js", "ts", "rs", "py", "rb", "hs", "cc", "cxx",
                   "h", "hpp", "kt", "ex", "exs", "pl", "cs"]
        for alias in aliases:
            assert alias not in langs, f"Alias '{alias}' nella lista"

    def test_sorted(self, analyzer):
        """La lista deve essere ordinata."""
        langs = analyzer.get_supported_languages()
        assert langs == sorted(langs)


class TestSingleLineFile:
    """Test per file con una sola riga."""

    def test_single_comment_line(self, analyzer, temp_output_dir):
        """Un file con solo un commento deve trovare un commento."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                          delete=False, dir=temp_output_dir) as f:
            f.write("# Just a comment\n")
            path = f.name
        try:
            elements = analyzer.analyze(path, "python")
            assert len(elements) == 1
            assert elements[0].element_type == ElementType.COMMENT_SINGLE
        finally:
            os.unlink(path)

    def test_single_function_line(self, analyzer, temp_output_dir):
        """Un file con solo una definizione di funzione."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c",
                                          delete=False, dir=temp_output_dir) as f:
            f.write("void hello() {}\n")
            path = f.name
        try:
            elements = analyzer.analyze(path, "c")
            funcs = [e for e in elements if e.element_type == ElementType.FUNCTION]
            assert len(funcs) == 1
            assert "hello" in funcs[0].name
        finally:
            os.unlink(path)
