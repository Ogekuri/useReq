"""Test specifici per il riconoscimento dei commenti."""

import pytest

from tests.test_helpers import (
    ALL_LANGUAGES,
    fixture_path,
    filter_elements,
)
from usereq.source_analyzer import ElementType


# Linguaggi con supporto commenti multi-line
LANGUAGES_WITH_MULTILINE = [
    "python", "c", "cpp", "rust", "javascript", "typescript",
    "java", "go", "ruby", "php", "swift", "kotlin", "scala",
    "lua", "perl", "haskell", "csharp",
]

# Linguaggi SENZA commenti multi-line nativi
LANGUAGES_WITHOUT_MULTILINE = [
    "shell", "zig", "elixir",
]


class TestSingleLineComments:
    """Test per i commenti single-line."""

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_has_single_line_comment(self, language, analyzer, fixtures_dir):
        """Verifica che ogni fixture abbia almeno un commento single-line."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        singles = filter_elements(elements, ElementType.COMMENT_SINGLE)
        assert len(singles) > 0, \
            f"{language}: nessun commento single-line trovato"

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_single_line_comment_is_single_line(self, language, analyzer, fixtures_dir):
        """Verifica che i commenti single-line occupino una sola riga."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        singles = filter_elements(elements, ElementType.COMMENT_SINGLE)
        for elem in singles:
            assert elem.line_start == elem.line_end, (
                f"{language}: commento single-line su piu' righe: "
                f"L{elem.line_start}-L{elem.line_end}"
            )

    @pytest.mark.parametrize("language,prefix", [
        ("python", "#"),
        ("c", "//"),
        ("cpp", "//"),
        ("rust", "//"),
        ("javascript", "//"),
        ("typescript", "//"),
        ("java", "//"),
        ("go", "//"),
        ("ruby", "#"),
        ("php", "//"),
        ("swift", "//"),
        ("kotlin", "//"),
        ("scala", "//"),
        ("lua", "--"),
        ("shell", "#"),
        ("perl", "#"),
        ("haskell", "--"),
        ("zig", "//"),
        ("elixir", "#"),
        ("csharp", "//"),
    ])
    def test_comment_has_correct_prefix(self, language, prefix, analyzer, fixtures_dir):
        """Verifica che il commento usi il prefisso corretto del linguaggio."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        singles = filter_elements(elements, ElementType.COMMENT_SINGLE)
        # Almeno il primo commento (non-inline) deve iniziare col prefisso giusto
        non_inline = [e for e in singles if e.name != "inline"]
        assert len(non_inline) > 0
        assert non_inline[0].extract.strip().startswith(prefix), (
            f"{language}: commento non inizia con '{prefix}': "
            f"'{non_inline[0].extract.strip()[:30]}'"
        )


class TestMultiLineComments:
    """Test per i commenti multi-line."""

    @pytest.mark.parametrize("language", LANGUAGES_WITH_MULTILINE)
    def test_has_multiline_comment(self, language, analyzer, fixtures_dir):
        """Verifica che i linguaggi con multi-line abbiano almeno un commento multi-line."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        multis = filter_elements(elements, ElementType.COMMENT_MULTI)
        assert len(multis) > 0, \
            f"{language}: nessun commento multi-line trovato"

    @pytest.mark.parametrize("language", LANGUAGES_WITHOUT_MULTILINE)
    def test_no_multiline_comment(self, language, analyzer, fixtures_dir):
        """Verifica che i linguaggi senza multi-line non ne abbiano."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        multis = filter_elements(elements, ElementType.COMMENT_MULTI)
        assert len(multis) == 0, \
            f"{language}: trovati {len(multis)} commenti multi-line inattesi"

    @pytest.mark.parametrize("language", [
        lang for lang in LANGUAGES_WITH_MULTILINE
        if lang not in ("swift", "typescript")  # commento multi-line su 1 riga
    ])
    def test_multiline_spans_multiple_lines(self, language, analyzer, fixtures_dir):
        """Verifica che almeno un commento multi-line copra piu' righe."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        multis = filter_elements(elements, ElementType.COMMENT_MULTI)
        spanning = [e for e in multis if e.line_end > e.line_start]
        assert len(spanning) > 0, (
            f"{language}: nessun commento multi-line su piu' righe. "
            f"Multi trovati: {[(e.line_start, e.line_end) for e in multis]}"
        )


class TestCommentContent:
    """Test sul contenuto dei commenti."""

    @pytest.mark.parametrize("language", ALL_LANGUAGES)
    def test_first_comment_contains_text(self, language, analyzer, fixtures_dir):
        """Verifica che il primo commento contenga testo significativo."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        comments = [e for e in elements if e.element_type in (
            ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI)]
        assert len(comments) > 0
        # Il commento deve contenere piu' di soli delimitatori
        text = comments[0].extract.strip()
        assert len(text) > 2, f"{language}: commento troppo corto: '{text}'"

    @pytest.mark.parametrize("language,keyword", [
        ("python", "comment"),
        ("c", "comment"),
        ("javascript", "comment"),
        ("rust", "comment"),
        ("go", "comment"),
    ])
    def test_comment_extract_contains_keyword(self, language, keyword,
                                               analyzer, fixtures_dir):
        """Verifica che l'extract del commento contenga la parola chiave attesa."""
        path = fixture_path(fixtures_dir, language)
        elements = analyzer.analyze(path, language)
        comments = [e for e in elements if e.element_type in (
            ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI)]
        all_text = " ".join(e.extract.lower() for e in comments)
        assert keyword.lower() in all_text, (
            f"{language}: '{keyword}' non trovato nei commenti"
        )
