#!/usr/bin/env python3
"""!
@file test_doxygen_parser.py
@brief Unit tests for doxygen_parser module.
@details Validates Doxygen field extraction across all 16 supported tags with a deterministic matrix of 10 scenarios per tag (160 extraction tests), including delimiter cleanup, multiline handling, whitespace normalization, and markdown formatting behavior.
"""

from collections import Counter

import pytest
from usereq.doxygen_parser import (
    DOXYGEN_TAGS,
    _normalize_whitespace,
    _strip_comment_delimiters,
    format_doxygen_fields_as_markdown,
    parse_doxygen_comment,
)

SCENARIOS_PER_TAG = 10
TOTAL_REQUIRED_EXTRACTION_TESTS = len(DOXYGEN_TAGS) * SCENARIOS_PER_TAG


def _tag_slug(tag: str) -> str:
    """!
    @brief Convert a Doxygen tag key into a deterministic ASCII slug.
    @details Replaces square brackets used in directional tags with underscores to build stable pytest ids and payload labels.
    @param tag Doxygen normalized tag key (for example brief, param[in], param[out]).
    @return Lowercase slug usable in case identifiers.
    """
    return tag.replace('[', '_').replace(']', '').replace(' ', '_')


def _build_comment_scenarios(tag: str) -> list[tuple[str, str, str]]:
    """!
    @brief Build ten deterministic extraction scenarios for one Doxygen tag.
    @details Generates comments covering syntax variants and edge patterns: direct tag, extra spacing, multiline continuation, C-style block delimiters, C++/Python line comments, backslash syntax, whitespace collapse, blank-line preservation, and triple-quote wrappers with CRLF.
    @param tag Doxygen normalized tag key.
    @return Ordered list of tuples `(scenario_name, comment_text, expected_content)`.
    """
    slug = _tag_slug(tag)
    token = f"@{tag}"
    slash_token = f"\\{tag}"

    return [
        (
            "plain",
            f"{token} {slug} case01 plain extraction.",
            f"{slug} case01 plain extraction.",
        ),
        (
            "leading_spaces",
            f"   {token}    {slug} case02 spaced extraction.",
            f"{slug} case02 spaced extraction.",
        ),
        (
            "multiline",
            f"{token} {slug} case03 first line.\nsecond line continuation.",
            f"{slug} case03 first line.\nsecond line continuation.",
        ),
        (
            "c_block",
            f"/**\n * {token} {slug} case04 c-style block.\n */",
            f"{slug} case04 c-style block.",
        ),
        (
            "cpp_slash",
            f"/// {token} {slug} case05 slash marker.",
            f"{slug} case05 slash marker.",
        ),
        (
            "python_hash",
            f"# {token} {slug} case06 hash marker.",
            f"{slug} case06 hash marker.",
        ),
        (
            "backslash_syntax",
            f"{slash_token} {slug} case07 backslash syntax.",
            f"{slug} case07 backslash syntax.",
        ),
        (
            "collapsed_spaces",
            f"{token}  {slug}   case08   collapsed   spaces.",
            f"{slug} case08 collapsed spaces.",
        ),
        (
            "blank_line_preserved",
            f"{token} {slug} case09 first paragraph.\n\nsecond paragraph.",
            f"{slug} case09 first paragraph.\nsecond paragraph.",
        ),
        (
            "triple_quote_wrapper",
            f'"""\r\n{token} {slug} case10 triple quote wrapper.\r\n"""',
            f"{slug} case10 triple quote wrapper.",
        ),
    ]


def _build_doxygen_case_matrix() -> list[tuple[str, str, dict[str, list[str]], str]]:
    """!
    @brief Build the full extraction matrix for all supported Doxygen tags.
    @details Expands the ten-scenario template over `DOXYGEN_TAGS`; each case defines one generated comment and one deterministic expected parser output dictionary.
    @return Matrix entries in form `(tag, comment_text, expected_dict, case_id)`.
    """
    matrix: list[tuple[str, str, dict[str, list[str]], str]] = []

    for tag in DOXYGEN_TAGS:
        slug = _tag_slug(tag)
        for index, (scenario, comment_text, expected_content) in enumerate(_build_comment_scenarios(tag), start=1):
            matrix.append(
                (
                    tag,
                    comment_text,
                    {tag: [expected_content]},
                    f"{slug}_{index:02d}_{scenario}",
                )
            )

    return matrix


DOXYGEN_CASE_MATRIX = _build_doxygen_case_matrix()
DOXYGEN_CASE_PARAMS = [
    pytest.param(comment_text, expected, id=case_id)
    for _, comment_text, expected, case_id in DOXYGEN_CASE_MATRIX
]


class TestParseDoxygenComment:
    """! @brief Test suite for parse_doxygen_comment() field extraction."""

    def test_doxygen_case_matrix_cardinality(self):
        """! @brief Enforce 10 generated extraction scenarios for each supported Doxygen tag."""
        counts = Counter(tag for tag, _, _, _ in DOXYGEN_CASE_MATRIX)

        assert len(DOXYGEN_CASE_MATRIX) == TOTAL_REQUIRED_EXTRACTION_TESTS
        for tag in DOXYGEN_TAGS:
            assert counts[tag] == SCENARIOS_PER_TAG

    @pytest.mark.parametrize(("comment", "expected"), DOXYGEN_CASE_PARAMS)
    def test_parse_doxygen_comment_generated_matrix(self, comment, expected):
        """! @brief Validate parser output against deterministic expected dictionary for each generated comment scenario."""
        assert parse_doxygen_comment(comment) == expected

    def test_multiple_tags(self):
        """! @brief Extract multiple tags from one comment block preserving independent keys."""
        comment = """
        @brief Short description.
        @details Longer detailed description.
        @param x First parameter.
        @return Result value.
        """

        result = parse_doxygen_comment(comment)
        assert result["brief"] == ["Short description."]
        assert result["details"] == ["Longer detailed description."]
        assert result["param"] == ["x First parameter."]
        assert result["return"] == ["Result value."]

    def test_empty_comment(self):
        """! @brief Return empty dictionary when comment text is empty."""
        assert parse_doxygen_comment("") == {}

    def test_no_doxygen_tags(self):
        """! @brief Return empty dictionary when comment contains no recognized Doxygen tags."""
        comment = "This is a regular comment without any Doxygen tags."
        assert parse_doxygen_comment(comment) == {}


class TestFormatDoxygenFieldsAsMarkdown:
    """! @brief Test suite for format_doxygen_fields_as_markdown()."""

    def test_format_brief(self):
        """! @brief Format a single brief field as markdown bullet."""
        fields = {"brief": ["Short description."]}
        lines = format_doxygen_fields_as_markdown(fields)
        assert lines == ["- Brief: Short description."]

    def test_format_multiple_fields(self):
        """! @brief Format multiple fields preserving DOXYGEN_TAGS ordering."""
        fields = {
            "return": ["Result value."],
            "brief": ["Function summary."],
            "param": ["x Input value."],
        }

        lines = format_doxygen_fields_as_markdown(fields)
        assert lines[0].startswith("- Brief:")
        assert lines[1].startswith("- Param:")
        assert lines[2].startswith("- Return:")

    def test_capitalize_tag_labels(self):
        """! @brief Capitalize markdown labels for short tags such as see/sa."""
        fields = {"see": ["other_func()"], "sa": ["module"]}
        lines = format_doxygen_fields_as_markdown(fields)

        assert "- See:" in lines[0]
        assert "- Sa:" in lines[1]

    def test_skip_missing_tags(self):
        """! @brief Omit markdown entries for tags not present in the parsed field dictionary."""
        fields = {"brief": ["Summary."]}
        lines = format_doxygen_fields_as_markdown(fields)
        assert len(lines) == 1


class TestStripCommentDelimiters:
    """! @brief Test suite for _strip_comment_delimiters()."""

    def test_strip_c_style_delimiters(self):
        """! @brief Remove C-style opening/closing delimiters and preserve payload content."""
        text = "/** \n * Content \n */"
        result = _strip_comment_delimiters(text)

        assert "/**" not in result
        assert "*/" not in result
        assert "Content" in result

    def test_strip_python_hash(self):
        """! @brief Remove Python hash markers across multiline comment blocks."""
        text = "# Comment line 1\n# Comment line 2"
        result = _strip_comment_delimiters(text)
        assert result == "Comment line 1\nComment line 2"


class TestNormalizeWhitespace:
    """! @brief Test suite for _normalize_whitespace()."""

    def test_collapse_multiple_spaces(self):
        """! @brief Collapse repeated spaces to single spaces in one line."""
        text = "word1    word2"
        result = _normalize_whitespace(text)
        assert result == "word1 word2"

    def test_remove_trailing_whitespace(self):
        """! @brief Strip trailing whitespace while preserving newline separators."""
        text = "line1  \nline2  "
        result = _normalize_whitespace(text)
        assert result == "line1\nline2"
