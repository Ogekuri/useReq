#!/usr/bin/env python3
"""!
@file find_constructs.py
@brief Find and extract specific constructs from source files.
@details Filters source code constructs (CLASS, FUNCTION, etc.) by type tag and name regex pattern, generating markdown output with complete code extracts.
@author GitHub Copilot
@version 0.0.70
"""

import os
import re
import sys

from .doxygen_parser import format_doxygen_fields_as_markdown, parse_doxygen_comment
from .source_analyzer import SourceAnalyzer
from .compress import compress_source, detect_language


# ── Language-specific TAG support map ────────────────────────────────────────
LANGUAGE_TAGS = {
    "python": {"CLASS", "FUNCTION", "DECORATOR", "IMPORT", "VARIABLE"},
    "c": {"STRUCT", "UNION", "ENUM", "TYPEDEF", "MACRO", "FUNCTION", "IMPORT", "VARIABLE"},
    "cpp": {"CLASS", "STRUCT", "ENUM", "NAMESPACE", "FUNCTION", "MACRO", "IMPORT", "TYPE_ALIAS"},
    "rust": {"FUNCTION", "STRUCT", "ENUM", "TRAIT", "IMPL", "MODULE", "MACRO", "CONSTANT", "TYPE_ALIAS", "IMPORT", "DECORATOR"},
    "javascript": {"CLASS", "FUNCTION", "COMPONENT", "CONSTANT", "IMPORT", "MODULE"},
    "typescript": {"INTERFACE", "TYPE_ALIAS", "ENUM", "CLASS", "FUNCTION", "NAMESPACE", "MODULE", "IMPORT", "DECORATOR"},
    "java": {"CLASS", "INTERFACE", "ENUM", "FUNCTION", "IMPORT", "MODULE", "DECORATOR", "CONSTANT"},
    "go": {"FUNCTION", "METHOD", "STRUCT", "INTERFACE", "TYPE_ALIAS", "CONSTANT", "IMPORT", "MODULE"},
    "ruby": {"CLASS", "MODULE", "FUNCTION", "CONSTANT", "IMPORT", "DECORATOR"},
    "php": {"CLASS", "INTERFACE", "TRAIT", "FUNCTION", "NAMESPACE", "IMPORT", "CONSTANT"},
    "swift": {"CLASS", "STRUCT", "ENUM", "PROTOCOL", "EXTENSION", "FUNCTION", "IMPORT", "CONSTANT", "VARIABLE"},
    "kotlin": {"CLASS", "INTERFACE", "ENUM", "FUNCTION", "CONSTANT", "VARIABLE", "MODULE", "IMPORT", "DECORATOR"},
    "scala": {"CLASS", "TRAIT", "MODULE", "FUNCTION", "CONSTANT", "VARIABLE", "TYPE_ALIAS", "IMPORT"},
    "lua": {"FUNCTION", "VARIABLE"},
    "shell": {"FUNCTION", "VARIABLE", "IMPORT"},
    "perl": {"FUNCTION", "MODULE", "IMPORT", "CONSTANT"},
    "haskell": {"MODULE", "TYPE_ALIAS", "STRUCT", "CLASS", "FUNCTION", "IMPORT"},
    "zig": {"FUNCTION", "STRUCT", "ENUM", "UNION", "CONSTANT", "VARIABLE", "IMPORT"},
    "elixir": {"MODULE", "FUNCTION", "PROTOCOL", "IMPL", "STRUCT", "IMPORT"},
    "csharp": {"CLASS", "INTERFACE", "STRUCT", "ENUM", "NAMESPACE", "FUNCTION", "PROPERTY", "IMPORT", "DECORATOR", "CONSTANT"},
}


def format_available_tags() -> str:
    """! @brief Generate formatted list of available TAGs per language.
    @return Multi-line string listing each language with its supported TAGs.
    @details Iterates LANGUAGE_TAGS dictionary, formats each entry as "- Language: TAG1, TAG2, ..." with language capitalized and tags alphabetically sorted and comma-separated.
    """
    lines = []
    for lang in sorted(LANGUAGE_TAGS.keys()):
        tags = sorted(LANGUAGE_TAGS[lang])
        lang_display = lang.capitalize()
        tags_str = ", ".join(tags)
        lines.append(f"- {lang_display}: {tags_str}")
    return "\n".join(lines)


def parse_tag_filter(tag_string: str) -> set[str]:
    """! @brief Parse pipe-separated tag filter into a normalized set.
    @param tag_string Raw tag filter string (e.g., "CLASS|FUNCTION").
    @return Set of uppercase tag identifiers.
    @details Splits the input string by pipe character `|` and strips whitespace from each component.
    """
    return {tag.strip().upper() for tag in tag_string.split("|") if tag.strip()}


def language_supports_tags(lang: str, tag_set: set[str]) -> bool:
    """! @brief Check if the language supports at least one of the requested tags.
    @param lang Normalized language identifier.
    @param tag_set Set of requested TAG identifiers.
    @return True if intersection is non-empty, False otherwise.
    @details Lookups the language in `LANGUAGE_TAGS` and checks if any of `tag_set` exists in the supported tags.
    """
    supported = LANGUAGE_TAGS.get(lang, set())
    return bool(supported & tag_set)


def construct_matches(element, tag_set: set[str], pattern: str) -> bool:
    """! @brief Check if a source element matches tag filter and regex pattern.
    @param element SourceElement instance from analyzer.
    @param tag_set Set of requested TAG identifiers.
    @param pattern Regex pattern string to test against element name.
    @return True if element type is in tag_set and name matches pattern.
    @details Validates the element type and then applies the regex search on the element name.
    """
    if element.type_label not in tag_set:
        return False
    if not element.name:
        return False
    try:
        return bool(re.search(pattern, element.name))
    except re.error:
        return False


def _merge_doxygen_fields(
    base_fields: dict[str, list[str]],
    extra_fields: dict[str, list[str]],
) -> dict[str, list[str]]:
    """! @brief Merge Doxygen fields preserving per-tag content order.
    @details Appends extra field values to base field lists for matching tags and initializes missing tags. Mutates and returns base_fields.
    @param base_fields Canonical field dictionary to update.
    @param extra_fields Additional parsed fields to append.
    @return Updated base_fields dictionary.
    """
    for tag, values in extra_fields.items():
        if tag not in base_fields:
            base_fields[tag] = []
        base_fields[tag].extend(values)
    return base_fields


def _extract_construct_doxygen_fields(element) -> dict[str, list[str]]:
    """! @brief Build aggregate Doxygen fields for one construct.
    @details Aggregates fields from two sources: pre-associated element.doxygen_fields and all comment snippets extracted from element.body_comments. Each comment snippet is parsed with parse_doxygen_comment() and merged in discovery order.
    @param element SourceElement instance potentially enriched with doxygen_fields and body_comments.
    @return Dictionary tag->list preserving tag content insertion order.
    """
    aggregate: dict[str, list[str]] = {}

    if hasattr(element, "doxygen_fields") and element.doxygen_fields:
        _merge_doxygen_fields(aggregate, element.doxygen_fields)

    body_comments = getattr(element, "body_comments", [])
    for body_comment in body_comments:
        if not isinstance(body_comment, tuple) or len(body_comment) < 3:
            continue
        comment_text = body_comment[2]
        parsed_fields = parse_doxygen_comment(comment_text)
        if parsed_fields:
            _merge_doxygen_fields(aggregate, parsed_fields)

    return aggregate


def _strip_construct_comments(
    code_lines: list[str],
    language: str,
    line_start: int,
    include_line_numbers: bool,
) -> str:
    """! @brief Remove comments from extracted construct code while preserving source line mapping.
    @param code_lines Raw construct code lines sliced by SourceElement line range.
    @param language Normalized language key used by the compression parser.
    @param line_start Absolute start line number of the construct in the original file.
    @param include_line_numbers If True, emit `<n>:` prefixes with absolute source line numbers.
    @return Comment-stripped construct code string.
    @details Delegates comment stripping to `compress_source()` to remove inline, single-line, and multi-line comments while preserving string literals. When line numbers are enabled, remaps local compressed line indices back to absolute file line numbers using `line_start`.
    """
    raw_source = "".join(code_lines)
    stripped_with_local_numbers = compress_source(
        raw_source,
        language,
        include_line_numbers=True,
    )
    stripped_lines = stripped_with_local_numbers.splitlines()

    if not include_line_numbers:
        return "\n".join(
            line.split(": ", 1)[1] if ": " in line else line
            for line in stripped_lines
        )

    remapped_lines: list[str] = []
    for line in stripped_lines:
        match = re.match(r"^(\d+):\s(.*)$", line)
        if not match:
            remapped_lines.append(line)
            continue
        local_line = int(match.group(1))
        absolute_line = line_start + local_line - 1
        remapped_lines.append(f"{absolute_line}: {match.group(2)}")
    return "\n".join(remapped_lines)


def format_construct(
    element,
    source_lines: list[str],
    include_line_numbers: bool,
    language: str = "python",
) -> str:
    """! @brief Format a single matched construct for markdown output with complete code extraction.
    @param element SourceElement instance containing line range indices.
    @param source_lines Complete source file content as list of lines.
    @param include_line_numbers If True, prefix code lines with <n>: format.
    @param language Normalized source language key used for comment stripping.
    @return Formatted markdown block for the construct with complete code from line_start to line_end.
    @details Extracts construct code directly from source_lines using element.line_start and element.line_end indices, removes inline/single-line/multi-line comments from the extracted block, and inserts Doxygen metadata before the code fence when available.
    """
    lines = []
    lines.append(f"### {element.type_label}: `{element.name}`")
    if element.signature:
        lines.append(f"> Signature: `{element.signature}`")
    lines.append(f"> Lines: {element.line_start}-{element.line_end}")

    # Insert Doxygen fields if present (DOX-010, DOX-011)
    doxygen_fields = _extract_construct_doxygen_fields(element)
    if doxygen_fields:
        dox_lines = format_doxygen_fields_as_markdown(doxygen_fields)
        lines.extend(dox_lines)

    # Extract COMPLETE code block from source file and strip comments
    code_lines = source_lines[element.line_start - 1:element.line_end]
    formatted = _strip_construct_comments(
        code_lines=code_lines,
        language=language,
        line_start=element.line_start,
        include_line_numbers=include_line_numbers,
    )

    lines.append("```")
    lines.append(formatted)
    lines.append("```")

    return "\n".join(lines)


def find_constructs_in_files(
    filepaths: list[str],
    tag_filter: str,
    pattern: str,
    include_line_numbers: bool = True,
    verbose: bool = False,
) -> str:
    """! @brief Find and extract constructs matching tag filter and regex pattern from multiple files.
    @param filepaths List of source file paths.
    @param tag_filter Pipe-separated TAG identifiers (e.g., "CLASS|FUNCTION").
    @param pattern Regex pattern for construct name matching.
    @param include_line_numbers If True (default), prefix code lines with <n>: format.
    @param verbose If True, emits progress status messages on stderr.
    @return Concatenated markdown output string.
    @throws ValueError If no files could be processed or no constructs found.
    @details Analyzes each file with SourceAnalyzer, filters elements by tag and name pattern, formats results as markdown with file headers.
    """
    tag_set = parse_tag_filter(tag_filter)
    if not tag_set:
        available = format_available_tags()
        raise ValueError(f"No valid tags specified in tag filter.\n\nAvailable tags by language:\n{available}")

    parts = []
    ok_count = 0
    skip_count = 0
    fail_count = 0
    total_matches = 0

    for fpath in filepaths:
        if not os.path.isfile(fpath):
            if verbose:
                print(f"  SKIP  {fpath} (not found)", file=sys.stderr)
            skip_count += 1
            continue

        lang = detect_language(fpath)
        if not lang:
            if verbose:
                print(f"  SKIP  {fpath} (unsupported extension)", file=sys.stderr)
            skip_count += 1
            continue

        # Check if language supports at least one requested tag
        if not language_supports_tags(lang, tag_set):
            if verbose:
                print(f"  SKIP  {fpath} (language {lang} does not support any requested tags)", file=sys.stderr)
            skip_count += 1
            continue

        try:
            # Read complete source file for full construct extraction
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                source_lines = f.readlines()

            analyzer = SourceAnalyzer()
            elements = analyzer.analyze(fpath, lang)
            analyzer.enrich(elements, lang, fpath)

            # Filter elements matching tag and pattern
            matches = [el for el in elements if construct_matches(el, tag_set, pattern)]

            if matches:
                header = f"@@@ {fpath} | {lang}"
                constructs_md = "\n\n".join(
                    format_construct(
                        el,
                        source_lines,
                        include_line_numbers,
                        language=lang,
                    )
                    for el in matches
                )
                parts.append(f"{header}\n\n{constructs_md}")
                total_matches += len(matches)
                ok_count += 1
                if verbose:
                    print(f"  OK    {fpath} ({len(matches)} matches)", file=sys.stderr)
            else:
                if verbose:
                    print(f"  SKIP  {fpath} (no matches)", file=sys.stderr)
                skip_count += 1

        except Exception as e:
            if verbose:
                print(f"  FAIL  {fpath} ({e})", file=sys.stderr)
            fail_count += 1

    if not parts:
        available = format_available_tags()
        raise ValueError(f"No constructs found matching the specified criteria.\n\nAvailable tags by language:\n{available}")

    if verbose:
        print(
            f"\n  Found: {total_matches} constructs in {ok_count} files "
            f"({skip_count} skipped, {fail_count} failed)",
            file=sys.stderr,
        )

    return "\n\n".join(parts)


def main():
    """! @brief Execute the construct finding CLI command.
    @details Parses arguments and calls find_constructs_in_files. Handles exceptions by printing errors to stderr.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Find and extract specific constructs from source files."
    )
    parser.add_argument(
        "tag",
        help="Pipe-separated construct types (e.g., CLASS|FUNCTION).",
    )
    parser.add_argument(
        "pattern",
        help="Regex pattern for construct name matching.",
    )
    parser.add_argument("files", nargs="+", help="Source files to search.")
    parser.add_argument(
        "--enable-line-numbers",
        action="store_true",
        default=False,
        help="Enable line number prefixes (<n>:) in output.",
    )
    args = parser.parse_args()

    try:
        output = find_constructs_in_files(
            args.files, args.tag, args.pattern, args.enable_line_numbers
        )
        print(output)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
