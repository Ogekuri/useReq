#!/usr/bin/env python3
"""!
@file doxygen_parser.py
@brief Doxygen comment parser for extracting structured documentation fields.
@details Parses Doxygen-formatted documentation comments and extracts recognized tags (@brief, @param, @return, etc.) into structured dictionaries for downstream LLM-optimized markdown rendering.
@author GitHub Copilot
@version 0.0.70
"""

import re
from typing import Dict, List


# Supported Doxygen tags in extraction order
DOXYGEN_TAGS = [
    'brief',
    'details',
    'param',
    'param[in]',
    'param[out]',
    'return',
    'retval',
    'exception',
    'throws',
    'warning',
    'deprecated',
    'note',
    'see',
    'sa',
    'satisfies',
    'pre',
    'post',
]

_NON_PARAM_TAGS = [tag for tag in DOXYGEN_TAGS if tag not in {'param', 'param[in]', 'param[out]'}]
"""! @brief Supported non-param Doxygen tags used to build the parser pattern."""

_NON_PARAM_TAG_ALTERNATION = "|".join(
    re.escape(tag) for tag in sorted(_NON_PARAM_TAGS, key=len, reverse=True)
)
"""! @brief Regex alternation for non-param tags ordered by descending length."""

DOXYGEN_TAG_PATTERN = re.compile(
    r'[@\\]'
    rf'(?:(param)(\[[^\]]+\])?|({_NON_PARAM_TAG_ALTERNATION}))'
)
"""! @brief Compiled regex that matches supported @tag / \\tag tokens."""


def parse_doxygen_comment(comment_text: str) -> Dict[str, List[str]]:
    """!
    @brief Extract Doxygen fields from a documentation comment block.
    @details Parses both @tag and \\tag syntax. Each tag's content extends until the next tag or end of comment. Multiple occurrences of the same tag accumulate in the returned list. Whitespace is normalized.
    @param comment_text Raw comment string potentially containing Doxygen tags.
    @return Dictionary mapping normalized tag names to lists of extracted content strings.
    @note Returns empty dict if no Doxygen tags are found.
    @see DOXYGEN_TAGS for recognized tag list.
    """
    if not comment_text or not comment_text.strip():
        return {}

    result: Dict[str, List[str]] = {}

    # Normalize line endings and strip comment delimiters
    text = comment_text.replace('\r\n', '\n').replace('\r', '\n')
    text = _strip_comment_delimiters(text)

    matches = list(DOXYGEN_TAG_PATTERN.finditer(text))

    if not matches:
        return {}

    for i, match in enumerate(matches):
        param_tag = match.group(1)
        direction = match.group(2) if match.group(2) else ''
        non_param_tag = match.group(3)

        # Normalize tag key: param[in], param[out], param (no direction)
        if param_tag:
            normalized_tag = f'param{direction}' if direction else 'param'
        else:
            normalized_tag = non_param_tag

        # Extract content from end of tag to start of next tag (or end of text)
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        content = text[start_pos:end_pos].strip()
        content = _normalize_whitespace(content)

        if content:
            if normalized_tag not in result:
                result[normalized_tag] = []
            result[normalized_tag].append(content)

    return result


def _strip_comment_delimiters(text: str) -> str:
    """!
    @brief Remove common comment delimiters from text block.
    @details Strips leading/trailing /**, */, //, #, triple quotes, and intermediate * column markers. Preserves content while removing comment syntax artifacts.
    @param text Raw comment block possibly containing comment delimiters.
    @return Cleaned text with delimiters removed.
    """
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Remove common comment starters/enders
        if stripped in ('/**', '/*', '*/', '"""', "'''", '/*!', '///', '//!'):
            continue

        # Remove leading comment markers: //, #, *, etc.
        stripped = re.sub(r'^[/*#]+\s*', '', stripped)
        stripped = re.sub(r'^\*\s*', '', stripped)  # leading * from multi-line C-style
        stripped = re.sub(r'^///?!?\s*', '', stripped)  # // or /// or //!
        stripped = re.sub(r'^#+\s*', '', stripped)  # Python #

        if stripped:
            cleaned_lines.append(stripped)

    return '\n'.join(cleaned_lines)


def _normalize_whitespace(text: str) -> str:
    """!
    @brief Normalize internal whitespace in extracted tag content.
    @details Collapses multiple spaces to single space, preserves single newlines, removes redundant blank lines.
    @param text Tag content with potentially irregular whitespace.
    @return Whitespace-normalized content.
    """
    # Collapse multiple spaces to single space
    text = re.sub(r' +', ' ', text)
    # Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    # Remove consecutive blank lines
    normalized_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                normalized_lines.append(line)
            prev_blank = True
        else:
            normalized_lines.append(line)
            prev_blank = False

    return '\n'.join(normalized_lines).strip()


def format_doxygen_fields_as_markdown(doxygen_fields: Dict[str, List[str]]) -> List[str]:
    """!
    @brief Format extracted Doxygen fields as Markdown bulleted list.
    @details Emits fields in fixed order (DOXYGEN_TAGS), capitalizes tag, omits @ prefix, appends ':'. Skips tags not present in input. Each tag's content items are concatenated.
    @param doxygen_fields Dictionary of tag -> content list from parse_doxygen_comment().
    @return List of Markdown lines (each starting with '- ').
    @note Output order matches DOXYGEN_TAGS sequence.
    """
    lines = []
    for tag in DOXYGEN_TAGS:
        if tag in doxygen_fields:
            # Capitalize first letter, append colon
            label = tag.capitalize() + ':'
            # Join multiple content entries with space
            content = ' '.join(doxygen_fields[tag])
            lines.append(f'- {label} {content}')
    return lines
