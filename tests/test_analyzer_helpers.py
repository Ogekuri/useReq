"""Test per i metodi interni dell'analyzer."""

import os
import tempfile
import pytest

from usereq.source_analyzer import (
    SourceAnalyzer, ElementType, LanguageSpec, build_language_specs,
)


class TestInStringContext:
    """Test per _in_string_context()."""

    def setup_method(self):
        self.analyzer = SourceAnalyzer()
        self.py_spec = self.analyzer.specs["python"]
        self.c_spec = self.analyzer.specs["c"]

    def test_not_in_string(self):
        """Posizione fuori da stringa."""
        line = 'x = 5  # comment'
        assert not self.analyzer._in_string_context(line, 7, self.py_spec)

    def test_in_double_quoted_string(self):
        """Posizione dentro una stringa con doppi apici."""
        line = 'x = "hello # world"'
        # Il '#' alla posizione 14 e' dentro la stringa
        idx = line.index("#")
        assert self.analyzer._in_string_context(line, idx, self.py_spec)

    def test_in_single_quoted_string(self):
        """Posizione dentro una stringa con singoli apici."""
        line = "x = 'hello # world'"
        idx = line.index("#")
        assert self.analyzer._in_string_context(line, idx, self.py_spec)

    def test_after_string(self):
        """Posizione dopo la chiusura della stringa."""
        line = 'x = "hello"  # comment'
        idx = line.index("#")
        assert not self.analyzer._in_string_context(line, idx, self.py_spec)

    def test_escaped_quote(self):
        """Quote escaped non chiude la stringa."""
        line = r'x = "hello \" world"  # comment'
        idx = line.index("#")
        assert not self.analyzer._in_string_context(line, idx, self.py_spec)

    def test_c_double_slash_in_string(self):
        """// dentro una stringa C non e' un commento."""
        line = 'char *s = "http://example.com";'
        # La posizione del // dentro la stringa
        idx = line.index("//")
        assert self.analyzer._in_string_context(line, idx, self.c_spec)


class TestFindComment:
    """Test per _find_comment()."""

    def setup_method(self):
        self.analyzer = SourceAnalyzer()
        self.py_spec = self.analyzer.specs["python"]
        self.c_spec = self.analyzer.specs["c"]
        self.lua_spec = self.analyzer.specs["lua"]

    def test_find_hash_comment(self):
        """Trova commento # in Python."""
        idx = self.analyzer._find_comment("x = 5  # comment", self.py_spec)
        assert idx is not None
        assert idx == 7

    def test_no_comment(self):
        """Nessun commento nella riga."""
        idx = self.analyzer._find_comment("x = 5", self.py_spec)
        assert idx is None

    def test_hash_in_string(self):
        """# dentro una stringa non e' un commento."""
        idx = self.analyzer._find_comment('x = "has # inside"', self.py_spec)
        assert idx is None

    def test_double_slash_comment(self):
        """Trova commento // in C."""
        idx = self.analyzer._find_comment("int x = 5; // comment", self.c_spec)
        assert idx is not None

    def test_double_slash_in_string(self):
        """// dentro una stringa non e' un commento."""
        idx = self.analyzer._find_comment(
            'char *s = "http://example.com";', self.c_spec
        )
        assert idx is None

    def test_double_dash_comment(self):
        """Trova commento -- in Lua."""
        idx = self.analyzer._find_comment("x = 5 -- comment", self.lua_spec)
        assert idx is not None

    def test_comment_at_start(self):
        """Commento all'inizio della riga."""
        idx = self.analyzer._find_comment("# full line comment", self.py_spec)
        assert idx == 0

    def test_no_single_comment_spec(self):
        """Spec senza single_comment restituisce None."""
        spec = LanguageSpec(name="test", single_comment=None)
        idx = self.analyzer._find_comment("x = 5", spec)
        assert idx is None


class TestFindBlockEnd:
    """Test per _find_block_end()."""

    def setup_method(self):
        self.analyzer = SourceAnalyzer()

    def test_python_block_by_indentation(self):
        """Python: blocco determinato dall'indentazione."""
        lines = [
            "def f():\n",
            "    x = 1\n",
            "    return x\n",
            "\n",
            "y = 2\n",
        ]
        end = self.analyzer._find_block_end(lines, 0, "python", "def f():")
        # Deve includere le righe indentate ma fermarsi prima di y = 2
        assert end <= 4

    def test_c_block_by_braces(self):
        """C: blocco determinato dalle parentesi graffe."""
        lines = [
            "void f() {\n",
            "    int x = 1;\n",
            "}\n",
            "\n",
        ]
        end = self.analyzer._find_block_end(lines, 0, "c", "void f() {")
        assert end == 3  # Riga con }

    def test_c_no_braces(self):
        """C: senza parentesi graffe restituisce solo la prima riga."""
        lines = [
            "void f();\n",
            "int x = 5;\n",
        ]
        end = self.analyzer._find_block_end(lines, 0, "c", "void f();")
        assert end == 1

    def test_ruby_block_by_end_keyword(self):
        """Ruby: blocco terminato dalla keyword 'end'."""
        lines = [
            "def hello\n",
            "  puts 'hi'\n",
            "end\n",
        ]
        end = self.analyzer._find_block_end(lines, 0, "ruby", "def hello")
        assert end == 3

    def test_haskell_block_by_indentation(self):
        """Haskell: blocco determinato dall'indentazione."""
        lines = [
            "greet :: String -> String\n",
            "greet name = \"Hello \" ++ name\n",
            "\n",
            "other = 42\n",
        ]
        end = self.analyzer._find_block_end(lines, 0, "haskell",
                                             "greet :: String -> String")
        assert end <= 2

    def test_nested_braces(self):
        """Parentesi graffe annidate devono essere gestite."""
        lines = [
            "void f() {\n",
            "    if (x) {\n",
            "        y();\n",
            "    }\n",
            "}\n",
        ]
        end = self.analyzer._find_block_end(lines, 0, "c", "void f() {")
        assert end == 5

    def test_unknown_language_returns_first_line(self):
        """Linguaggio sconosciuto nella _find_block_end restituisce prima riga."""
        lines = ["something\n", "else\n"]
        end = self.analyzer._find_block_end(lines, 0, "unknown_lang", "something")
        assert end == 1


class TestBuildLanguageSpecs:
    """Test per build_language_specs()."""

    def test_returns_dict(self):
        """Deve restituire un dizionario."""
        specs = build_language_specs()
        assert isinstance(specs, dict)

    def test_all_core_languages_present(self):
        """Tutti i linguaggi principali devono essere presenti."""
        specs = build_language_specs()
        core = [
            "python", "c", "cpp", "rust", "javascript", "typescript",
            "java", "go", "ruby", "php", "swift", "kotlin", "scala",
            "lua", "shell", "perl", "haskell", "zig", "elixir", "csharp",
        ]
        for lang in core:
            assert lang in specs, f"Linguaggio '{lang}' mancante"

    def test_aliases_point_to_same_spec(self):
        """Gli alias devono puntare alla stessa specifica."""
        specs = build_language_specs()
        assert specs["js"] is specs["javascript"]
        assert specs["ts"] is specs["typescript"]
        assert specs["rs"] is specs["rust"]
        assert specs["py"] is specs["python"]
        assert specs["rb"] is specs["ruby"]
        assert specs["hs"] is specs["haskell"]
        assert specs["cs"] is specs["csharp"]
        assert specs["kt"] is specs["kotlin"]
        assert specs["ex"] is specs["elixir"]
        assert specs["sh"] is specs["shell"]
        assert specs["bash"] is specs["shell"]

    def test_each_spec_has_patterns(self):
        """Ogni specifica deve avere almeno un pattern."""
        specs = build_language_specs()
        seen = set()
        for key, spec in specs.items():
            if id(spec) in seen:
                continue
            seen.add(id(spec))
            assert len(spec.patterns) > 0, \
                f"Linguaggio '{key}' senza pattern"

    def test_each_spec_has_single_comment(self):
        """Ogni specifica deve avere un delimitatore per commento single-line."""
        specs = build_language_specs()
        seen = set()
        for key, spec in specs.items():
            if id(spec) in seen:
                continue
            seen.add(id(spec))
            assert spec.single_comment is not None, \
                f"Linguaggio '{key}' senza single_comment"

    def test_spec_name_not_empty(self):
        """Ogni specifica deve avere un nome non vuoto."""
        specs = build_language_specs()
        seen = set()
        for key, spec in specs.items():
            if id(spec) in seen:
                continue
            seen.add(id(spec))
            assert spec.name, f"Linguaggio '{key}' con nome vuoto"
