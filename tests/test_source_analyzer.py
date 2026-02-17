"""Tests for the usereq.source_analyzer module.

Covers: SRC-001 through SRC-014.
Ported and adapted from the original parser test suite.
"""

import os
import tempfile
from collections import Counter

import pytest

from usereq.source_analyzer import (
    ElementType,
    LanguageSpec,
    SourceAnalyzer,
    SourceElement,
    build_language_specs,
    format_markdown,
)


# ── Extension to language mapping ─────────────────────────────────────────

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".c": "c",
    ".cpp": "cpp",
    ".rs": "rust",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".lua": "lua",
    ".sh": "shell",
    ".pl": "perl",
    ".hs": "haskell",
    ".zig": "zig",
    ".ex": "elixir",
    ".cs": "csharp",
}

ALL_LANGUAGES = sorted(EXTENSION_TO_LANGUAGE.values())

LANGUAGE_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "rs": "rust",
    "py": "python",
    "rb": "ruby",
    "hs": "haskell",
    "cc": "cpp",
    "cxx": "cpp",
    "h": "c",
    "hpp": "cpp",
    "kt": "kotlin",
    "ex": "elixir",
    "exs": "elixir",
    "pl": "perl",
    "cs": "csharp",
    "bash": "shell",
    "sh": "shell",
    "zsh": "shell",
}


# ── Expected counts per language (calibrated on actual fixtures) ──────────

EXPECTED_COUNTS = {
    "c": {
        ElementType.COMMENT_MULTI: 65,
        ElementType.COMMENT_SINGLE: 2,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 11,
        ElementType.IMPORT: 5,
        ElementType.MACRO: 6,
        ElementType.STRUCT: 6,
        ElementType.TYPEDEF: 5,
        ElementType.UNION: 5,
        ElementType.VARIABLE: 6,
    },
    "cpp": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 63,
        ElementType.COMMENT_SINGLE: 4,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 18,
        ElementType.IMPORT: 7,
        ElementType.MACRO: 5,
        ElementType.NAMESPACE: 5,
        ElementType.STRUCT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "csharp": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 12,
        ElementType.COMMENT_SINGLE: 161,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 18,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.NAMESPACE: 5,
        ElementType.PROPERTY: 6,
        ElementType.STRUCT: 5,
    },
    "elixir": {
        ElementType.COMMENT_SINGLE: 30,
        ElementType.FUNCTION: 35,
        ElementType.IMPL: 6,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 8,
        ElementType.PROTOCOL: 5,
        ElementType.STRUCT: 6,
    },
    "go": {
        ElementType.COMMENT_MULTI: 15,
        ElementType.COMMENT_SINGLE: 81,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 8,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.METHOD: 5,
        ElementType.MODULE: 5,
        ElementType.STRUCT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "haskell": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 2,
        ElementType.COMMENT_SINGLE: 67,
        ElementType.FUNCTION: 11,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
        ElementType.STRUCT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "java": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 58,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 6,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 23,
        ElementType.IMPORT: 7,
        ElementType.INTERFACE: 5,
        ElementType.MODULE: 5,
    },
    "javascript": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 60,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.COMPONENT: 5,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 14,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
    },
    "kotlin": {
        ElementType.CLASS: 9,
        ElementType.COMMENT_MULTI: 69,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 9,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 15,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.MODULE: 5,
        ElementType.VARIABLE: 5,
    },
    "lua": {
        ElementType.COMMENT_MULTI: 1,
        ElementType.COMMENT_SINGLE: 82,
        ElementType.FUNCTION: 16,
        ElementType.VARIABLE: 13,
    },
    "perl": {
        ElementType.COMMENT_MULTI: 3,
        ElementType.COMMENT_SINGLE: 68,
        ElementType.CONSTANT: 6,
        ElementType.FUNCTION: 14,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
    },
    "php": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 58,
        ElementType.COMMENT_SINGLE: 5,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 24,
        ElementType.IMPORT: 6,
        ElementType.INTERFACE: 5,
        ElementType.NAMESPACE: 5,
        ElementType.TRAIT: 5,
    },
    "python": {
        ElementType.CLASS: 7,
        ElementType.COMMENT_MULTI: 41,
        ElementType.COMMENT_SINGLE: 24,
        ElementType.DECORATOR: 9,
        ElementType.FUNCTION: 32,
        ElementType.IMPORT: 7,
        ElementType.VARIABLE: 6,
    },
    "ruby": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 2,
        ElementType.COMMENT_SINGLE: 107,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 5,
        ElementType.FUNCTION: 20,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
    },
    "rust": {
        ElementType.COMMENT_MULTI: 18,
        ElementType.COMMENT_SINGLE: 113,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 18,
        ElementType.IMPL: 7,
        ElementType.IMPORT: 5,
        ElementType.MACRO: 5,
        ElementType.MODULE: 5,
        ElementType.STRUCT: 5,
        ElementType.TRAIT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "scala": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 56,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 25,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
        ElementType.TRAIT: 5,
        ElementType.TYPE_ALIAS: 5,
        ElementType.VARIABLE: 5,
    },
    "shell": {
        ElementType.COMMENT_SINGLE: 64,
        ElementType.FUNCTION: 9,
        ElementType.IMPORT: 5,
        ElementType.VARIABLE: 11,
    },
    "swift": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 16,
        ElementType.COMMENT_SINGLE: 113,
        ElementType.CONSTANT: 7,
        ElementType.ENUM: 5,
        ElementType.EXTENSION: 5,
        ElementType.FUNCTION: 13,
        ElementType.IMPORT: 7,
        ElementType.PROTOCOL: 5,
        ElementType.STRUCT: 5,
        ElementType.VARIABLE: 16,
    },
    "typescript": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 74,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 9,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.MODULE: 5,
        ElementType.NAMESPACE: 5,
        ElementType.TYPE_ALIAS: 6,
    },
    "zig": {
        ElementType.COMMENT_SINGLE: 100,
        ElementType.CONSTANT: 11,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 13,
        ElementType.IMPORT: 7,
        ElementType.STRUCT: 5,
        ElementType.UNION: 5,
        ElementType.VARIABLE: 5,
    },
}


EXPECTED_NAMED = [
    ("python", ElementType.CLASS, "class MyClass:", 59),
    ("python", ElementType.FUNCTION, "def regular_function(", 276),
    ("python", ElementType.FUNCTION, "async def async_function(", 390),
    ("python", ElementType.IMPORT, "import os", 7),
    ("python", ElementType.VARIABLE, "MAX_RETRIES = ", 18),
    ("python", ElementType.DECORATOR, "dataclass", 25),
    ("c", ElementType.STRUCT, "struct Point", 59),
    ("c", ElementType.UNION, "union Data", 94),
    ("c", ElementType.ENUM, "enum Color", 106),
    ("c", ElementType.FUNCTION, "void greet(", 167),
    ("c", ElementType.FUNCTION, "int main(", 181),
    ("c", ElementType.MACRO, "#define MAX_SIZE", 19),
    ("c", ElementType.TYPEDEF, "typedef int my_int;", 48),
    ("rust", ElementType.STRUCT, "pub struct MyStruct", 20),
    ("rust", ElementType.ENUM, "pub enum MyEnum", 51),
    ("rust", ElementType.TRAIT, "pub trait MyTrait", 65),
    ("rust", ElementType.FUNCTION, "pub fn my_function", 240),
    ("rust", ElementType.FUNCTION, "pub async fn async_function", 254),
    ("rust", ElementType.MACRO, "macro_rules! hashmap", 196),
    ("rust", ElementType.MODULE, "pub mod my_module", 182),
    ("rust", ElementType.TYPE_ALIAS, "pub type MyAlias", 232),
    ("javascript", ElementType.CLASS, "class MyComponent", 20),
    ("javascript", ElementType.FUNCTION, "function greet(", 103),
    ("javascript", ElementType.FUNCTION, "async function fetchData(", 112),
    ("javascript", ElementType.FUNCTION, "const handler = (event) =>", 122),
    ("javascript", ElementType.COMPONENT, "const MyWrapped = React.memo(", 153),
    ("javascript", ElementType.MODULE, "const fs = require(", 297),
    ("go", ElementType.STRUCT, "type Server struct", 39),
    ("go", ElementType.INTERFACE, "type Handler interface", 67),
    ("go", ElementType.FUNCTION, "func main(", 107),
    ("go", ElementType.METHOD, "func (s *Server) Start(", 119),
    ("swift", ElementType.CLASS, "class Animal", 16),
    ("swift", ElementType.STRUCT, "struct Point", 85),
    ("swift", ElementType.ENUM, "enum Direction", 140),
    ("swift", ElementType.PROTOCOL, "protocol Drawable", 186),
    ("swift", ElementType.EXTENSION, "extension Animal", 226),
    ("elixir", ElementType.MODULE, "defmodule MyApp.Server", 10),
    ("elixir", ElementType.PROTOCOL, "defprotocol Printable", 187),
    ("elixir", ElementType.IMPL, "defimpl Printable", 204),
    ("haskell", ElementType.MODULE, "module MyModule", 11),
    ("haskell", ElementType.TYPE_ALIAS, "type Name", 30),
    ("haskell", ElementType.STRUCT, "data Person", 42),
    ("haskell", ElementType.CLASS, "class Printable", 72),
    ("csharp", ElementType.NAMESPACE, "namespace MyApp", 15),
    ("csharp", ElementType.CLASS, "public class Person", 53),
    ("csharp", ElementType.INTERFACE, "public interface IGreeter", 179),
    ("csharp", ElementType.STRUCT, "public readonly struct Point", 215),
    ("csharp", ElementType.ENUM, "public enum Color", 238),
]

# Languages with multi-line comment support
LANGUAGES_WITH_MULTILINE = [
    "python", "c", "cpp", "rust", "javascript", "typescript",
    "java", "go", "ruby", "php", "swift", "kotlin", "scala",
    "lua", "perl", "haskell", "csharp",
]

LANGUAGES_WITHOUT_MULTILINE = [
    "shell", "zig", "elixir",
]


# ── Helpers ───────────────────────────────────────────────────────────────

def fixture_path(language):
    """Return fixture path for the given language."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    for ext, lang in EXTENSION_TO_LANGUAGE.items():
        if lang == language:
            return os.path.join(fixtures_dir, f"fixture_{language}{ext}")
    raise ValueError(f"No fixture for language: {language}")


def count_by_type(elements):
    """Count elements by type."""
    return dict(Counter(e.element_type for e in elements))


def filter_elements(elements, element_type=None, name=None):
    """Filter elements by type and/or name."""
    result = elements
    if element_type is not None:
        result = [e for e in result if e.element_type == element_type]
    if name is not None:
        result = [e for e in result if e.name == name]
    return result


def _format_counts(counts):
    """Format counts for readable diff output."""
    return ", ".join(
        f"{t.name}:{c}" for t, c in sorted(counts.items(), key=lambda x: x[0].name)
    )


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def analyzer():
    """Shared analyzer instance."""
    return SourceAnalyzer()


# ── Test Classes ──────────────────────────────────────────────────────────

class TestAnalyzerAllLanguages:
    """Parameterized tests for all 20 supported languages."""

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_fixture_exists(self, language):
        """SRC-014: Fixture must exist for every language."""
        path = fixture_path(language)
        assert os.path.isfile(path), f"Fixture missing: {path}"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_analyze_returns_elements(self, language, analyzer):
        """SRC-001: analyze() must return a non-empty list for each language."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        assert isinstance(elements, list)
        assert len(elements) > 0

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_elements_are_source_elements(self, language, analyzer):
        """SRC-003: Each element must be a SourceElement instance."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert isinstance(elem, SourceElement)

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_element_line_numbers_positive(self, language, analyzer):
        """SRC-003: line_start >= 1, line_end >= line_start."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert elem.line_start >= 1
            assert elem.line_end >= elem.line_start

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_element_extract_not_empty(self, language, analyzer):
        """SRC-003: Extract must not be empty."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert elem.extract

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_element_type_is_valid(self, language, analyzer):
        """SRC-002: element_type must be a valid ElementType."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert isinstance(elem.element_type, ElementType)

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_expected_counts(self, language, analyzer):
        """SRC-001: Expected element counts per type."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        actual = count_by_type(elements)
        expected = EXPECTED_COUNTS[language]
        assert actual == expected, (
            f"{language}: counts differ.\n"
            f"  Expected: {_format_counts(expected)}\n"
            f"  Got:      {_format_counts(actual)}"
        )

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_total_element_count(self, language, analyzer):
        """SRC-001: Total count must match sum of expected counts."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        expected_total = sum(EXPECTED_COUNTS[language].values())
        assert len(elements) == expected_total

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_has_comment(self, language, analyzer):
        """SRC-005: Each fixture must have at least one comment."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        comments = [e for e in elements if e.element_type in (
            ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI)]
        assert len(comments) > 0

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_type_label_not_unknown(self, language, analyzer):
        """SRC-002: type_label must never be UNKNOWN."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert elem.type_label != "UNKNOWN"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_elements_sorted_by_line(self, language, analyzer):
        """Elements must be sorted by line_start."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        for i in range(1, len(elements)):
            assert elements[i].line_start >= elements[i - 1].line_start

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_extract_max_lines(self, language, analyzer):
        """SRC-003: Extract must not exceed 5 lines."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            lines = elem.extract.split("\n")
            assert len(lines) <= 5


class TestExpectedNamedElements:
    """Verify specific named elements at expected positions."""

    @pytest.mark.parametrize(
        "language,elem_type,name,line_start",
        EXPECTED_NAMED,
        ids=[f"{lang}-{etype.name}-{name}"
             for lang, etype, name, _ in EXPECTED_NAMED],
    )
    def test_named_element(self, language, elem_type, name, line_start, analyzer):
        """SRC-002: Verify specific named element at expected line."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        typed = filter_elements(elements, element_type=elem_type)
        matches = [e for e in typed if e.name and name in e.name]
        assert len(matches) > 0, (
            f"{language}: {elem_type.name} containing '{name}' not found"
        )
        line_matches = [e for e in matches if e.line_start == line_start]
        assert len(line_matches) > 0, (
            f"{language}: {elem_type.name} '{name}' not found at line {line_start}"
        )


class TestLanguageAliases:
    """SRC-006: Aliases must produce identical results."""

    @pytest.mark.parametrize("alias,canonical", list(LANGUAGE_ALIASES.items()))
    def test_alias_same_results(self, alias, canonical, analyzer):
        """Alias must produce the same elements as canonical language."""
        path = fixture_path(canonical)
        elements_canonical = analyzer.analyze(path, canonical)
        elements_alias = analyzer.analyze(path, alias)
        assert len(elements_canonical) == len(elements_alias)
        for e1, e2 in zip(elements_canonical, elements_alias):
            assert e1.element_type == e2.element_type
            assert e1.line_start == e2.line_start
            assert e1.name == e2.name


class TestComments:
    """SRC-005: Comment recognition tests."""

    @pytest.mark.parametrize("language,prefix", [
        ("python", "#"), ("c", "//"), ("cpp", "//"), ("rust", "//"),
        ("javascript", "//"), ("typescript", "//"), ("java", "//"),
        ("go", "//"), ("ruby", "#"), ("php", "//"), ("swift", "//"),
        ("kotlin", "//"), ("scala", "//"), ("lua", "--"), ("shell", "#"),
        ("perl", "#"), ("haskell", "--"), ("zig", "//"), ("elixir", "#"),
        ("csharp", "//"),
    ])
    def test_comment_has_correct_prefix(self, language, prefix, analyzer):
        """SRC-005: Comments must use the correct prefix."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        singles = filter_elements(elements, ElementType.COMMENT_SINGLE)
        non_inline = [e for e in singles if e.name != "inline"]
        assert len(non_inline) > 0
        assert non_inline[0].extract.strip().startswith(prefix)

    @pytest.mark.parametrize("language", LANGUAGES_WITH_MULTILINE)
    def test_has_multiline_comment(self, language, analyzer):
        """SRC-005: Languages with multi-line support must have multi-line comments."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        multis = filter_elements(elements, ElementType.COMMENT_MULTI)
        assert len(multis) > 0

    @pytest.mark.parametrize("language", LANGUAGES_WITHOUT_MULTILINE)
    def test_no_multiline_comment(self, language, analyzer):
        """SRC-005: Languages without multi-line support must have none."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        multis = filter_elements(elements, ElementType.COMMENT_MULTI)
        assert len(multis) == 0


class TestErrors:
    """SRC-011: Error handling tests."""

    def test_unsupported_language_raises(self, analyzer):
        """Unsupported language must raise ValueError."""
        with pytest.raises(ValueError, match="not supported"):
            analyzer.analyze("dummy.txt", "brainfuck")

    def test_file_not_found_raises(self, analyzer):
        """Missing file must raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze("/nonexistent/path/file.py", "python")

    def test_empty_file_returns_empty(self, analyzer):
        """Empty file must return empty list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("")
            path = f.name
        try:
            elements = analyzer.analyze(path, "python")
            assert elements == []
        finally:
            os.unlink(path)

    def test_whitespace_only_file(self, analyzer):
        """Whitespace-only file must return empty list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("   \n\n  \n")
            path = f.name
        try:
            elements = analyzer.analyze(path, "python")
            assert elements == []
        finally:
            os.unlink(path)


class TestLanguageNormalization:
    """SRC-004: Language parameter normalization."""

    def test_uppercase(self, analyzer):
        """Uppercase language must work."""
        path = fixture_path("python")
        elements = analyzer.analyze(path, "PYTHON")
        assert len(elements) > 0

    def test_mixed_case(self, analyzer):
        """Mixed case language must work."""
        path = fixture_path("python")
        elements = analyzer.analyze(path, "Python")
        assert len(elements) > 0

    def test_with_leading_dot(self, analyzer):
        """Language with leading dot must work."""
        path = fixture_path("python")
        elements = analyzer.analyze(path, ".py")
        assert len(elements) > 0

    def test_with_spaces(self, analyzer):
        """Language with surrounding spaces must work."""
        path = fixture_path("python")
        elements = analyzer.analyze(path, "  python  ")
        assert len(elements) > 0


class TestBuildLanguageSpecs:
    """SRC-001, SRC-006: Language spec construction tests."""

    def test_returns_dict(self):
        """Must return a dictionary."""
        specs = build_language_specs()
        assert isinstance(specs, dict)

    def test_all_core_languages_present(self):
        """All 20 core languages must be present."""
        specs = build_language_specs()
        for lang in ALL_LANGUAGES:
            assert lang in specs

    def test_aliases_point_to_same_spec(self):
        """Aliases must reference the same spec object."""
        specs = build_language_specs()
        assert specs["js"] is specs["javascript"]
        assert specs["ts"] is specs["typescript"]
        assert specs["rs"] is specs["rust"]
        assert specs["py"] is specs["python"]
        assert specs["rb"] is specs["ruby"]
        assert specs["hs"] is specs["haskell"]
        assert specs["cs"] is specs["csharp"]

    def test_each_spec_has_patterns(self):
        """Each spec must have at least one pattern."""
        specs = build_language_specs()
        seen = set()
        for key, spec in specs.items():
            if id(spec) in seen:
                continue
            seen.add(id(spec))
            assert len(spec.patterns) > 0

    def test_each_spec_has_single_comment(self):
        """Each spec must have a single-line comment delimiter."""
        specs = build_language_specs()
        seen = set()
        for key, spec in specs.items():
            if id(spec) in seen:
                continue
            seen.add(id(spec))
            assert spec.single_comment is not None


class TestFormatMarkdown:
    """SRC-010: format_markdown() tests."""

    def test_contains_filepath(self, analyzer):
        """Output must contain the file path."""
        path = fixture_path("python")
        elements = analyzer.analyze(path, "python")
        output = format_markdown(elements, path, "python", "Python", 100)
        assert path in output

    def test_contains_definitions_section(self, analyzer):
        """Output must contain Definitions section."""
        path = fixture_path("python")
        elements = analyzer.analyze(path, "python")
        output = format_markdown(elements, path, "python", "Python", 100)
        assert "## Definitions" in output

    def test_empty_elements_no_definitions(self):
        """Empty list should not have Definitions."""
        output = format_markdown([], "test.py", "python", "Python", 100)
        assert "## Definitions" not in output
        assert "# test.py | Python | 100L | 0 symbols | 0 imports | 0 comments" in output

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_format_markdown_all_languages(self, language, analyzer):
        """format_markdown() must work for all languages."""
        path = fixture_path(language)
        elements = analyzer.analyze(path, language)
        spec = analyzer.specs[language]
        analyzer.enrich(elements, language, filepath=path)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            total_lines = sum(1 for _ in f)
        md = format_markdown(elements, path, language, spec.name, total_lines)
        assert isinstance(md, str)
        assert len(md) > 0
        assert "## Definitions" in md or "## Comments" in md or "# File:" in md


class TestInternalHelpers:
    """SRC-013: String context and comment detection tests."""

    def setup_method(self):
        self.analyzer = SourceAnalyzer()
        self.py_spec = self.analyzer.specs["python"]
        self.c_spec = self.analyzer.specs["c"]

    def test_not_in_string(self):
        """Position outside string."""
        line = 'x = 5  # comment'
        assert not self.analyzer._in_string_context(line, 7, self.py_spec)

    def test_in_double_quoted_string(self):
        """Position inside double-quoted string."""
        line = 'x = "hello # world"'
        idx = line.index("#")
        assert self.analyzer._in_string_context(line, idx, self.py_spec)

    def test_hash_in_string_not_comment(self):
        """# inside string must not be a comment."""
        idx = self.analyzer._find_comment('x = "has # inside"', self.py_spec)
        assert idx is None

    def test_find_hash_comment(self):
        """Must find # comment in Python."""
        idx = self.analyzer._find_comment("x = 5  # comment", self.py_spec)
        assert idx is not None
        assert idx == 7


class TestTypeLabelProperty:
    """SRC-002: type_label property tests."""

    @pytest.mark.parametrize("elem_type,expected_label", [
        (ElementType.FUNCTION, "FUNCTION"),
        (ElementType.METHOD, "METHOD"),
        (ElementType.CLASS, "CLASS"),
        (ElementType.STRUCT, "STRUCT"),
        (ElementType.ENUM, "ENUM"),
        (ElementType.COMMENT_SINGLE, "COMMENT"),
        (ElementType.COMMENT_MULTI, "COMMENT"),
    ])
    def test_type_label(self, elem_type, expected_label):
        """Verify label for each ElementType."""
        elem = SourceElement(
            element_type=elem_type, line_start=1, line_end=1, extract="test",
        )
        assert elem.type_label == expected_label
