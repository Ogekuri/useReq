"""Test parametrizzati per tutti i 20 linguaggi supportati."""

import os
import pytest
from collections import Counter

from tests.test_helpers import (
    ALL_LANGUAGES,
    EXPECTED_COUNTS,
    EXPECTED_NAMED,
    EXTENSION_TO_LANGUAGE,
    LANGUAGE_ALIASES,
    fixture_path,
    filter_elements,
    count_by_type,
)
from usereq.source_analyzer import SourceAnalyzer, ElementType, SourceElement


class TestAnalyzerAllLanguages:
    """Test parametrizzati per verificare l'analisi di ogni linguaggio."""

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_fixture_exists(self, language, fixtures_dir):
        """Verifica che la fixture esista per ogni linguaggio."""
        path = fixture_path(fixtures_dir, language)
        assert os.path.isfile(path), f"Fixture mancante: {path}"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_analyze_returns_elements(self, language, analyzer, fixtures_dir):
        """Verifica che analyze() restituisca una lista non vuota."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        assert isinstance(elements, list)
        assert len(elements) > 0, f"Nessun elemento trovato per {language}"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_elements_are_source_elements(self, language, analyzer, fixtures_dir):
        """Verifica che ogni elemento sia un'istanza di SourceElement."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert isinstance(elem, SourceElement), \
                f"Elemento non valido per {language}: {elem}"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_element_line_numbers_positive(self, language, analyzer, fixtures_dir):
        """Verifica che line_start e line_end siano positivi e coerenti."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert elem.line_start >= 1, \
                f"{language}: line_start < 1: {elem}"
            assert elem.line_end >= elem.line_start, \
                f"{language}: line_end < line_start: {elem}"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_element_extract_not_empty(self, language, analyzer, fixtures_dir):
        """Verifica che l'extract non sia vuoto."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert elem.extract, f"{language}: extract vuoto: {elem}"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_element_type_is_valid(self, language, analyzer, fixtures_dir):
        """Verifica che element_type sia un valore valido di ElementType."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert isinstance(elem.element_type, ElementType), \
                f"{language}: tipo non valido: {elem.element_type}"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_expected_counts(self, language, analyzer, fixtures_dir):
        """Verifica i conteggi esatti per tipo di elemento."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        actual = count_by_type(elements)
        expected = EXPECTED_COUNTS[language]
        assert actual == expected, (
            f"{language}: conteggi diversi.\n"
            f"  Atteso:  {_format_counts(expected)}\n"
            f"  Trovato: {_format_counts(actual)}"
        )

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_total_element_count(self, language, analyzer, fixtures_dir):
        """Verifica il conteggio totale degli elementi."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        expected_total = sum(EXPECTED_COUNTS[language].values())
        assert len(elements) == expected_total, (
            f"{language}: totale elementi {len(elements)} != atteso {expected_total}"
        )

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_has_comment(self, language, analyzer, fixtures_dir):
        """Verifica che ogni fixture contenga almeno un commento."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        comments = [e for e in elements if e.element_type in (
            ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI)]
        assert len(comments) > 0, \
            f"{language}: nessun commento trovato"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_type_label_not_unknown(self, language, analyzer, fixtures_dir):
        """Verifica che type_label non sia mai UNKNOWN."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        for elem in elements:
            assert elem.type_label != "UNKNOWN", \
                f"{language}: type_label UNKNOWN per {elem.element_type}"


class TestExpectedNamedElements:
    """Verifica elementi specifici per nome e posizione."""

    @pytest.mark.parametrize(
        "language,elem_type,name,line_start",
        EXPECTED_NAMED,
        ids=[f"{lang}-{etype.name}-{name}"
             for lang, etype, name, _ in EXPECTED_NAMED],
    )
    def test_named_element(self, language, elem_type, name, line_start,
                           analyzer, fixtures_dir):
        """Verifica la presenza di un elemento specifico con nome e linea.

        Il campo name dell'analyzer contiene il match completo del regex
        (es. 'class MyClass:'), quindi usiamo substring matching per
        verificare che il nome atteso sia contenuto nel match.
        """
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        typed = filter_elements(elements, element_type=elem_type)
        # Substring match: il nome atteso deve essere contenuto nel name
        matches = [e for e in typed if e.name and name in e.name]
        assert len(matches) > 0, (
            f"{language}: elemento {elem_type.name} contenente '{name}' non trovato.\n"
            f"Elementi di tipo {elem_type.name}: "
            f"{[(e.name, e.line_start) for e in typed]}"
        )
        line_matches = [e for e in matches if e.line_start == line_start]
        assert len(line_matches) > 0, (
            f"{language}: {elem_type.name} con '{name}' non trovato alla riga {line_start}.\n"
            f"Trovato alle righe: {[e.line_start for e in matches]}"
        )


class TestLanguageAliases:
    """Verifica che gli alias producano gli stessi risultati."""

    @pytest.mark.parametrize("alias,canonical", list(LANGUAGE_ALIASES.items()))
    def test_alias_same_results(self, alias, canonical, analyzer, fixtures_dir):
        """Verifica che un alias produca gli stessi risultati del linguaggio canonico."""
        path = fixture_path(fixtures_dir, canonical)
        elements_canonical = analyzer.analyze(path, canonical)
        elements_alias = analyzer.analyze(path, alias)
        assert len(elements_canonical) == len(elements_alias), (
            f"Alias '{alias}' -> '{canonical}': conteggio diverso "
            f"({len(elements_alias)} vs {len(elements_canonical)})"
        )
        for e1, e2 in zip(elements_canonical, elements_alias):
            assert e1.element_type == e2.element_type
            assert e1.line_start == e2.line_start
            assert e1.name == e2.name


class TestExtensionMapping:
    """Verifica il mapping estensione -> linguaggio."""

    @pytest.mark.parametrize("ext,language", list(EXTENSION_TO_LANGUAGE.items()))
    def test_extension_to_language(self, ext, language, analyzer, fixtures_dir):
        """Verifica che il mapping estensione->linguaggio sia coerente."""
        path = fixture_path(fixtures_dir, language)
        assert os.path.isfile(path)
        # Verifica che l'estensione del file corrisponda
        _, file_ext = os.path.splitext(path)
        assert file_ext == ext, f"Estensione {file_ext} != {ext} per {language}"


class TestElementsSorted:
    """Verifica che gli elementi siano ordinati per linea."""

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_elements_sorted_by_line(self, language, analyzer, fixtures_dir):
        """Verifica che gli elementi siano in ordine crescente di line_start."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        for i in range(1, len(elements)):
            assert elements[i].line_start >= elements[i - 1].line_start, (
                f"{language}: elementi non ordinati alla posizione {i}: "
                f"L{elements[i - 1].line_start} > L{elements[i].line_start}"
            )


def _format_counts(counts):
    """Helper per formattare i conteggi in modo leggibile."""
    return ", ".join(
        f"{t.name}:{c}" for t, c in sorted(counts.items(), key=lambda x: x[0].name)
    )
