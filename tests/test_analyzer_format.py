"""Test per format_output() e type_label."""

import os
import pytest

from tests.test_helpers import ALL_LANGUAGES, fixture_path
from usereq.source_analyzer import (
    SourceAnalyzer, ElementType, SourceElement, format_output,
)


class TestFormatOutput:
    """Test per la funzione format_output()."""

    def test_contains_filepath(self, analyzer, fixtures_dir):
        """L'output deve contenere il percorso del file."""
        path = fixture_path(fixtures_dir, "python")
        elements = analyzer.analyze(path, "python")
        output = format_output(elements, path, "python", "Python")
        assert path in output

    def test_contains_language_name(self, analyzer, fixtures_dir):
        """L'output deve contenere il nome del linguaggio."""
        path = fixture_path(fixtures_dir, "rust")
        elements = analyzer.analyze(path, "rust")
        output = format_output(elements, path, "rust", "Rust")
        assert "Rust" in output
        assert "rust" in output

    def test_contains_element_count(self, analyzer, fixtures_dir):
        """Output should contain element count."""
        path = fixture_path(fixtures_dir, "python")
        elements = analyzer.analyze(path, "python")
        output = format_output(elements, path, "python", "Python")
        assert f"Elements found: {len(elements)}" in output

    def test_has_definitions_section(self, analyzer, fixtures_dir):
        """Output should contain a DEFINITIONS section."""
        path = fixture_path(fixtures_dir, "python")
        elements = analyzer.analyze(path, "python")
        output = format_output(elements, path, "python", "Python")
        assert "DEFINITIONS" in output

    def test_has_comments_section(self, analyzer, fixtures_dir):
        """Output should contain a COMMENTS section."""
        path = fixture_path(fixtures_dir, "python")
        elements = analyzer.analyze(path, "python")
        output = format_output(elements, path, "python", "Python")
        assert "COMMENTS" in output

    def test_has_structured_list(self, analyzer, fixtures_dir):
        """Output should contain COMPLETE STRUCTURED LISTING."""
        path = fixture_path(fixtures_dir, "python")
        elements = analyzer.analyze(path, "python")
        output = format_output(elements, path, "python", "Python")
        assert "COMPLETE STRUCTURED LISTING" in output

    def test_has_separators(self, analyzer, fixtures_dir):
        """L'output deve contenere separatori (righe di '=')."""
        path = fixture_path(fixtures_dir, "python")
        elements = analyzer.analyze(path, "python")
        output = format_output(elements, path, "python", "Python")
        assert "=" * 78 in output

    def test_empty_elements_no_definitions(self):
        """With empty list there should be no DEFINITIONS section."""
        output = format_output([], "test.py", "python", "Python")
        assert "DEFINITIONS" not in output
        assert "no elements found" in output

    def test_non_consecutive_separated(self, analyzer, fixtures_dir):
        """Elementi non consecutivi devono essere separati da riga vuota."""
        path = fixture_path(fixtures_dir, "python")
        elements = analyzer.analyze(path, "python")
        output = format_output(elements, path, "python", "Python")
        lines = output.split("\n")
        # Cerca almeno una riga vuota tra sezioni
        has_blank = any(line == "" for line in lines)
        assert has_blank, "Nessuna riga vuota di separazione trovata"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_format_output_all_languages(self, language, analyzer, fixtures_dir):
        """format_output() deve funzionare per tutti i linguaggi senza errori."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        spec = analyzer.specs[language]
        output = format_output(elements, path, language, spec.name)
        assert isinstance(output, str)
        assert len(output) > 0


class TestTypeLabelProperty:
    """Test per la proprieta' type_label di SourceElement."""

    @pytest.mark.parametrize("elem_type,expected_label", [
        (ElementType.FUNCTION, "FUNCTION"),
        (ElementType.METHOD, "METHOD"),
        (ElementType.CLASS, "CLASS"),
        (ElementType.STRUCT, "STRUCT"),
        (ElementType.ENUM, "ENUM"),
        (ElementType.TRAIT, "TRAIT"),
        (ElementType.INTERFACE, "INTERFACE"),
        (ElementType.MODULE, "MODULE"),
        (ElementType.IMPL, "IMPL"),
        (ElementType.MACRO, "MACRO"),
        (ElementType.CONSTANT, "CONSTANT"),
        (ElementType.VARIABLE, "VARIABLE"),
        (ElementType.TYPE_ALIAS, "TYPE_ALIAS"),
        (ElementType.IMPORT, "IMPORT"),
        (ElementType.DECORATOR, "DECORATOR"),
        (ElementType.COMMENT_SINGLE, "COMMENT"),
        (ElementType.COMMENT_MULTI, "COMMENT"),
        (ElementType.COMPONENT, "COMPONENT"),
        (ElementType.PROTOCOL, "PROTOCOL"),
        (ElementType.EXTENSION, "EXTENSION"),
        (ElementType.UNION, "UNION"),
        (ElementType.NAMESPACE, "NAMESPACE"),
        (ElementType.PROPERTY, "PROPERTY"),
        (ElementType.SIGNAL, "SIGNAL"),
        (ElementType.TYPEDEF, "TYPEDEF"),
    ])
    def test_type_label(self, elem_type, expected_label):
        """Verifica la label per ogni ElementType."""
        elem = SourceElement(
            element_type=elem_type,
            line_start=1,
            line_end=1,
            extract="test",
        )
        assert elem.type_label == expected_label

    def test_comment_types_have_same_label(self):
        """COMMENT_SINGLE e COMMENT_MULTI devono avere label 'COMMENT'."""
        e1 = SourceElement(ElementType.COMMENT_SINGLE, 1, 1, "//")
        e2 = SourceElement(ElementType.COMMENT_MULTI, 1, 3, "/* */")
        assert e1.type_label == "COMMENT"
        assert e2.type_label == "COMMENT"
        assert e1.type_label == e2.type_label


class TestLineLocationFormat:
    """Test per il formato della posizione (L1 vs L1-L5)."""

    def test_single_line_format(self):
        """Elemento su una riga deve mostrare Lx, non Lx-Lx."""
        elem = SourceElement(ElementType.FUNCTION, 5, 5, "def f():")
        # Verifica nel format_output
        output = format_output([elem], "test.py", "python", "Python")
        assert "L5" in output
        # Non deve avere L5-L5
        assert "L5-L5" not in output

    def test_multi_line_format(self):
        """Elemento su piu' righe deve mostrare Lx-Ly."""
        elem = SourceElement(ElementType.FUNCTION, 5, 10, "def f():\n    pass")
        output = format_output([elem], "test.py", "python", "Python")
        assert "L5-L10" in output

    def test_inline_comment_tagged(self):
        """Commento inline deve essere taggato con [inline]."""
        elem = SourceElement(
            ElementType.COMMENT_SINGLE, 5, 5, "# inline",
            name="inline"
        )
        output = format_output([elem], "test.py", "python", "Python")
        assert "[inline]" in output


class TestExtractTruncation:
    """Test per la troncatura dell'extract."""

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_extract_max_lines(self, language, analyzer, fixtures_dir):
        """L'extract non deve superare 5 righe (o 4 + '...')."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            lines = elem.extract.split("\n")
            assert len(lines) <= 5, (
                f"{language}: extract di {len(lines)} righe per "
                f"{elem.element_type.name} '{elem.name}' "
                f"L{elem.line_start}-L{elem.line_end}"
            )
