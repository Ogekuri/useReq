#!/usr/bin/env python3
"""!
@file test_doxygen_parser.py
@brief Unit tests for doxygen_parser module.
@details Tests extraction of all 14 supported Doxygen tags from comment blocks. Validates multi-line content handling, direction modifiers for @param, and whitespace normalization.
"""

import pytest
from usereq.doxygen_parser import (
    parse_doxygen_comment,
    format_doxygen_fields_as_markdown,
    _strip_comment_delimiters,
    _normalize_whitespace,
)


class TestParseDoxygenComment:
    """! @brief Test suite for parse_doxygen_comment() function."""

    def test_brief_single_line(self):
        """! @brief Extract single-line @brief tag."""
        comment = """
        @brief This is a brief description.
        """
        result = parse_doxygen_comment(comment)
        assert 'brief' in result
        assert result['brief'][0] == 'This is a brief description.'

    def test_brief_multiline(self):
        """! @brief Extract multi-line @brief content."""
        comment = """
        @brief This is a brief description
        that spans multiple lines.
        """
        result = parse_doxygen_comment(comment)
        assert 'brief' in result
        assert 'multiple lines' in result['brief'][0]

    def test_details_extraction(self):
        """! @brief Extract @details tag content."""
        comment = """
        @details Detailed explanation of the function
        with multiple sentences.
        """
        result = parse_doxygen_comment(comment)
        assert 'details' in result
        assert 'Detailed explanation' in result['details'][0]

    def test_param_no_direction(self):
        """! @brief Extract @param without direction modifier."""
        comment = """
        @param count The number of items to process.
        """
        result = parse_doxygen_comment(comment)
        assert 'param' in result
        assert 'count' in result['param'][0]

    def test_param_in_direction(self):
        """! @brief Extract @param[in] with input direction."""
        comment = """
        @param[in] value Input value for computation.
        """
        result = parse_doxygen_comment(comment)
        assert 'param[in]' in result
        assert 'value' in result['param[in]'][0]

    def test_param_out_direction(self):
        """! @brief Extract @param[out] with output direction."""
        comment = """
        @param[out] buffer Output buffer to fill.
        """
        result = parse_doxygen_comment(comment)
        assert 'param[out]' in result
        assert 'buffer' in result['param[out]'][0]

    def test_return_tag(self):
        """! @brief Extract @return tag content."""
        comment = """
        @return The computed result value.
        """
        result = parse_doxygen_comment(comment)
        assert 'return' in result
        assert 'computed result' in result['return'][0]

    def test_retval_tag(self):
        """! @brief Extract @retval tag content."""
        comment = """
        @retval 0 Success
        @retval -1 Failure
        """
        result = parse_doxygen_comment(comment)
        assert 'retval' in result
        assert len(result['retval']) == 2
        assert '0 Success' in result['retval'][0]

    def test_exception_tag(self):
        """! @brief Extract @exception tag content."""
        comment = """
        @exception ValueError If input is invalid.
        """
        result = parse_doxygen_comment(comment)
        assert 'exception' in result
        assert 'ValueError' in result['exception'][0]

    def test_throws_tag(self):
        """! @brief Extract @throws tag content."""
        comment = """
        @throws RuntimeError If operation fails.
        """
        result = parse_doxygen_comment(comment)
        assert 'throws' in result
        assert 'RuntimeError' in result['throws'][0]

    def test_warning_tag(self):
        """! @brief Extract @warning tag content."""
        comment = """
        @warning This function is not thread-safe.
        """
        result = parse_doxygen_comment(comment)
        assert 'warning' in result
        assert 'thread-safe' in result['warning'][0]

    def test_deprecated_tag(self):
        """! @brief Extract @deprecated tag content."""
        comment = """
        @deprecated Use new_function() instead.
        """
        result = parse_doxygen_comment(comment)
        assert 'deprecated' in result
        assert 'new_function' in result['deprecated'][0]

    def test_note_tag(self):
        """! @brief Extract @note tag content."""
        comment = """
        @note This is an important note.
        """
        result = parse_doxygen_comment(comment)
        assert 'note' in result
        assert 'important note' in result['note'][0]

    def test_see_tag(self):
        """! @brief Extract @see tag content."""
        comment = """
        @see related_function()
        """
        result = parse_doxygen_comment(comment)
        assert 'see' in result
        assert 'related_function' in result['see'][0]

    def test_sa_tag(self):
        """! @brief Extract @sa tag content."""
        comment = """
        @sa other_module
        """
        result = parse_doxygen_comment(comment)
        assert 'sa' in result
        assert 'other_module' in result['sa'][0]

    def test_pre_tag(self):
        """! @brief Extract @pre tag content."""
        comment = """
        @pre Input must be non-null.
        """
        result = parse_doxygen_comment(comment)
        assert 'pre' in result
        assert 'non-null' in result['pre'][0]

    def test_post_tag(self):
        """! @brief Extract @post tag content."""
        comment = """
        @post Output buffer is filled.
        """
        result = parse_doxygen_comment(comment)
        assert 'post' in result
        assert 'filled' in result['post'][0]

    def test_backslash_syntax(self):
        """! @brief Support \\tag backslash syntax."""
        comment = r"""
        \brief Alternative syntax test.
        """
        result = parse_doxygen_comment(comment)
        assert 'brief' in result
        assert 'Alternative syntax' in result['brief'][0]

    def test_multiple_tags(self):
        """! @brief Extract multiple different tags from one comment."""
        comment = """
        @brief Short description.
        @details Longer detailed description.
        @param x First parameter.
        @return Result value.
        """
        result = parse_doxygen_comment(comment)
        assert 'brief' in result
        assert 'details' in result
        assert 'param' in result
        assert 'return' in result

    def test_empty_comment(self):
        """! @brief Return empty dict for empty comment."""
        result = parse_doxygen_comment("")
        assert result == {}

    def test_no_doxygen_tags(self):
        """! @brief Return empty dict when no Doxygen tags present."""
        comment = """
        This is a regular comment without any Doxygen tags.
        """
        result = parse_doxygen_comment(comment)
        assert result == {}


class TestFormatDoxygenFieldsAsMarkdown:
    """! @brief Test suite for format_doxygen_fields_as_markdown()."""

    def test_format_brief(self):
        """! @brief Format brief field as markdown."""
        fields = {'brief': ['Short description.']}
        lines = format_doxygen_fields_as_markdown(fields)
        assert len(lines) == 1
        assert lines[0] == '- Brief: Short description.'

    def test_format_multiple_fields(self):
        """! @brief Format multiple fields preserving tag order."""
        fields = {
            'return': ['Result value.'],
            'brief': ['Function summary.'],
            'param': ['x Input value.'],
        }
        lines = format_doxygen_fields_as_markdown(fields)
        # Should be in DOXYGEN_TAGS order: brief, param, return
        assert lines[0].startswith('- Brief:')
        assert lines[1].startswith('- Param:')
        assert lines[2].startswith('- Return:')

    def test_capitalize_tag_labels(self):
        """! @brief Capitalize tag labels correctly."""
        fields = {'see': ['other_func()'], 'sa': ['module']}
        lines = format_doxygen_fields_as_markdown(fields)
        assert '- See:' in lines[0]
        assert '- Sa:' in lines[1]

    def test_skip_missing_tags(self):
        """! @brief Omit tags not present in input."""
        fields = {'brief': ['Summary.']}
        lines = format_doxygen_fields_as_markdown(fields)
        assert len(lines) == 1
        # Should not include empty entries for other tags


class TestStripCommentDelimiters:
    """! @brief Test suite for _strip_comment_delimiters()."""

    def test_strip_c_style_delimiters(self):
        """! @brief Remove C-style comment delimiters."""
        text = "/** \n * Content \n */"
        result = _strip_comment_delimiters(text)
        assert '/**' not in result
        assert '*/' not in result
        assert 'Content' in result

    def test_strip_python_hash(self):
        """! @brief Remove Python # comment markers."""
        text = "# Comment line 1\n# Comment line 2"
        result = _strip_comment_delimiters(text)
        assert result == "Comment line 1\nComment line 2"


class TestNormalizeWhitespace:
    """! @brief Test suite for _normalize_whitespace()."""

    def test_collapse_multiple_spaces(self):
        """! @brief Collapse multiple spaces to single space."""
        text = "word1    word2"
        result = _normalize_whitespace(text)
        assert result == "word1 word2"

    def test_remove_trailing_whitespace(self):
        """! @brief Strip trailing whitespace from lines."""
        text = "line1  \nline2  "
        result = _normalize_whitespace(text)
        assert result == "line1\nline2"
