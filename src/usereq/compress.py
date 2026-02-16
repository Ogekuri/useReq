#!/usr/bin/env python3
"""! @brief compress.py - Source code compressor for LLM context optimization.
@details Parses a source file and removes all comments (inline, single-line, multi-line), blank lines, trailing whitespace, and redundant spacing while preserving language semantics (e.g. Python indentation). Leverages LanguageSpec from source_analyzer to correctly identify comment syntax for each supported language. Usage (as module): from compress import compress_source, compress_file compressed = compress_source(code, "python") compressed = compress_file("main.py") Usage (CLI): python compress.py file.py python compress.py --lang rust file.rs
"""

import os
import re
import sys

from .source_analyzer import build_language_specs

# Extension-to-language map (mirrors generate_markdown.py)
EXT_LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".rs": "rust", ".go": "go", ".c": "c", ".cpp": "cpp",
    ".h": "c", ".hpp": "cpp", ".java": "java", ".rb": "ruby",
    ".php": "php", ".swift": "swift", ".kt": "kotlin",
    ".scala": "scala", ".lua": "lua", ".sh": "shell",
    ".pl": "perl", ".hs": "haskell", ".zig": "zig",
    ".ex": "elixir", ".cs": "csharp",
}
"""! @brief Extension-to-language normalization map for compression input."""

# Languages where indentation is semantically significant
INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}
"""! @brief Languages requiring indentation-preserving compression behavior."""

_specs_cache = None
"""! @brief Cached language specification dictionary initialized lazily."""


def _get_specs():
    """! @brief Return cached language specifications, initializing once.
    @return Dictionary mapping normalized language keys to language specs.
    """
    global _specs_cache
    if _specs_cache is None:
        _specs_cache = build_language_specs()
    return _specs_cache


def detect_language(filepath: str) -> str | None:
    """! @brief Detect language key from file extension.
    @param filepath Source file path.
    @return Normalized language key, or None when extension is unsupported.
    """
    _, ext = os.path.splitext(filepath)
    return EXT_LANG_MAP.get(ext.lower())


def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool:
    """! @brief Check if position `pos` in `line` is inside a string literal.
    """
    in_string = None
    i = 0
    sorted_delims = sorted(string_delimiters, key=len, reverse=True)
    while i < pos:
        if in_string is not None:
            if line[i:].startswith(in_string):
                # Check for escaped delimiter (single-char only)
                if len(in_string) == 1 and i > 0 and line[i - 1] == '\\':
                    # Count consecutive backslashes
                    bs = 0
                    j = i - 1
                    while j >= 0 and line[j] == '\\':
                        bs += 1
                        j -= 1
                    if bs % 2 == 1:
                        i += 1
                        continue
                i += len(in_string)
                in_string = None
                continue
            i += 1
        else:
            matched = False
            for delim in sorted_delims:
                if line[i:].startswith(delim):
                    in_string = delim
                    i += len(delim)
                    matched = True
                    break
            if not matched:
                i += 1
    return in_string is not None


def _remove_inline_comment(line: str, single_comment: str,
                           string_delimiters: tuple) -> str:
    """! @brief Remove trailing single-line comment from a code line.
    """
    if not single_comment:
        return line
    sc_len = len(single_comment)
    i = 0
    sorted_delims = sorted(string_delimiters, key=len, reverse=True)
    in_string = None
    while i < len(line):
        if in_string is not None:
            if line[i:].startswith(in_string):
                if len(in_string) == 1 and i > 0 and line[i - 1] == '\\':
                    bs = 0
                    j = i - 1
                    while j >= 0 and line[j] == '\\':
                        bs += 1
                        j -= 1
                    if bs % 2 == 1:
                        i += 1
                        continue
                i += len(in_string)
                in_string = None
                continue
            i += 1
        else:
            if line[i:i + sc_len] == single_comment:
                return line[:i]
            for delim in sorted_delims:
                if line[i:].startswith(delim):
                    in_string = delim
                    i += len(delim)
                    break
            else:
                i += 1
    return line


def _is_python_docstring_line(line: str) -> bool:
    """! @brief Check if a line is a standalone Python docstring (triple-quote only).
    """
    stripped = line.strip()
    for q in ('"""', "'''"):
        if stripped.startswith(q) and stripped.endswith(q) and len(stripped) >= 6:
            return True
    return False


def _format_result(entries: list[tuple[int, str]],
                   include_line_numbers: bool) -> str:
    """! @brief Format compressed entries, optionally prefixing original line numbers.
    """
    if not include_line_numbers:
        return '\n'.join(text for _, text in entries)
    return '\n'.join(f"{lineno}: {text}" for lineno, text in entries)


def compress_source(source: str, language: str,
                    include_line_numbers: bool = True) -> str:
    """! @brief Compress source code by removing comments, blank lines, and extra whitespace.
    @details Preserves indentation for indent-significant languages (Python, Haskell, Elixir). Args: source: The source code string. language: Language identifier (e.g. "python", "javascript"). include_line_numbers: If True (default), prefix each line with <n>: format. Returns: Compressed source code string.
    """
    specs = _get_specs()
    lang_key = language.lower().strip().lstrip(".")
    if lang_key not in specs:
        raise ValueError(f"Unsupported language: {language}")

    spec = specs[lang_key]
    preserve_indent = lang_key in INDENT_SIGNIFICANT
    lines = source.split('\n')
    result = []        # list of (original_line_number, text)

    in_multi_comment = False
    mc_end = spec.multi_comment_end
    mc_start = spec.multi_comment_start
    string_delims = spec.string_delimiters

    # Python: also handle ''' as multi-comment
    is_python = lang_key == "python"
    in_python_docstring = False
    python_docstring_delim = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- Handle multi-line comment continuation ---
        if in_multi_comment:
            if mc_end and mc_end in line:
                # End of multi-line comment found
                end_pos = line.index(mc_end) + len(mc_end)
                remainder = line[end_pos:]
                in_multi_comment = False
                # Process remainder as a new line
                if remainder.strip():
                    lines[i] = remainder
                    continue
            i += 1
            continue

        # --- Python docstrings (""" / ''') used as standalone comments ---
        if is_python and in_python_docstring:
            if python_docstring_delim in line:
                end_pos = line.index(python_docstring_delim) + 3
                remainder = line[end_pos:]
                in_python_docstring = False
                python_docstring_delim = None
                if remainder.strip():
                    lines[i] = remainder
                    continue
            i += 1
            continue

        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # --- Detect multi-line comment start ---
        if mc_start:
            # For Python, triple-quotes can be strings or docstrings.
            # We only strip standalone docstrings (line starts with triple-quote
            # after optional whitespace).
            if is_python:
                for q in ('"""', "'''"):
                    if stripped.startswith(q):
                        # Single-line docstring: """..."""
                        if stripped.count(q) >= 2 and stripped.endswith(q) and len(stripped) > 3:
                            # Check it's not a variable assignment like x = """..."""
                            leading = line[:len(line) - len(line.lstrip())]
                            code_before = line[:line.index(q)].strip()
                            if not code_before or code_before.endswith('='):
                                # Standalone docstring or assigned — skip if standalone
                                if not code_before:
                                    line = None
                                    break
                            # If code before and not assignment, keep line
                        elif stripped.startswith(q) and stripped.count(q) == 1:
                            # Multi-line docstring start
                            code_before = line[:line.index(q)].strip()
                            if not code_before:
                                in_python_docstring = True
                                python_docstring_delim = q
                                line = None
                                break
                if line is None:
                    i += 1
                    continue
            else:
                # Non-Python: check for multi-line comment start
                mc_pos = stripped.find(mc_start)
                if mc_pos != -1:
                    # Check if inside a string
                    full_pos = line.find(mc_start)
                    if not _is_in_string(line, full_pos, string_delims):
                        # Check for same-line close
                        after_start = line[full_pos + len(mc_start):]
                        close_pos = after_start.find(mc_end) if mc_end else -1
                        if close_pos != -1 and mc_start != mc_end:
                            # Single-line block comment: remove it
                            before = line[:full_pos]
                            after = after_start[close_pos + len(mc_end):]
                            line = before + after
                            if not line.strip():
                                i += 1
                                continue
                            # Re-process this reconstructed line
                            lines[i] = line
                            continue
                        else:
                            # Multi-line comment starts here
                            before = line[:full_pos]
                            in_multi_comment = True
                            if before.strip():
                                line = before
                            else:
                                i += 1
                                continue

        # --- Full-line single-line comment ---
        if spec.single_comment and stripped.startswith(spec.single_comment):
            # Special: keep shebangs
            if stripped.startswith('#!') and i == 0:
                result.append((i + 1, stripped))
            i += 1
            continue

        # --- Remove inline comment ---
        if spec.single_comment:
            line = _remove_inline_comment(line, spec.single_comment, string_delims)

        # --- Clean whitespace ---
        if preserve_indent:
            # Keep leading whitespace, strip trailing
            leading = line[:len(line) - len(line.lstrip())]
            content = line.strip()
            if not content:
                i += 1
                continue
            # Collapse internal multiple spaces (but not in strings)
            line = leading + content
        else:
            line = line.strip()
            if not line:
                i += 1
                continue

        # Remove trailing whitespace
        line = line.rstrip()

        if line:
            result.append((i + 1, line))

        i += 1

    return _format_result(result, include_line_numbers)


def compress_file(filepath: str, language: str | None = None,
                  include_line_numbers: bool = True) -> str:
    """! @brief Compress a source file by removing comments and extra whitespace.
    @details Args: filepath: Path to the source file. language: Optional language override. Auto-detected if None. include_line_numbers: If True (default), prefix each line with <n>: format. Returns: Compressed source code string.
    """
    if language is None:
        language = detect_language(filepath)
        if language is None:
            raise ValueError(
                f"Cannot detect language for '{filepath}'. "
                "Use --lang to specify explicitly.")

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        source = f.read()

    return compress_source(source, language, include_line_numbers)


def main():
    """! @brief Execute the standalone compression CLI."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Compress source code for LLM context optimization.")
    parser.add_argument("file", help="Source file to compress.")
    parser.add_argument("--lang", default=None,
                        help="Language override (auto-detected from extension).")
    parser.add_argument("--enable-line-numbers", action="store_true",
                        default=False,
                        help="Enable line number prefixes (<n>:) in output.")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        compressed = compress_file(args.file, args.lang,
                                   args.enable_line_numbers)
        print(compressed)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
