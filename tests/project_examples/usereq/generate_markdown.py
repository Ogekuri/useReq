#!/usr/bin/env python3
"""!
@file generate_markdown.py
@brief Generate concatenated markdown from arbitrary source files.
@details Analyzes each input file with source_analyzer and produces a single markdown output concatenating all results. Prints pack summary to stderr.
@author GitHub Copilot
@version 0.0.70
"""

import os
import sys

from .source_analyzer import SourceAnalyzer, format_markdown

# Map file extensions to languages
EXT_LANG_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".java": "java",
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
"""! @brief Extension-to-language normalization map for markdown generation."""


def detect_language(filepath: str) -> str | None:
    """! @brief Detect language from file extension.
    @param filepath Path to the source file.
    @return Language identifier string or None if unknown.
    @details Uses EXT_LANG_MAP for extension lookup (case-insensitive).
    """
    _, ext = os.path.splitext(filepath)
    return EXT_LANG_MAP.get(ext.lower())


def generate_markdown(filepaths: list[str], verbose: bool = False) -> str:
    """! @brief Analyze source files and return concatenated markdown.
    @param filepaths List of source file paths to analyze.
    @param verbose If True, emits progress status messages on stderr.
    @return Concatenated markdown string with all file analyses.
    @throws ValueError If no valid source files are found.
    @details Iterates through files, detecting language, analyzing constructs, and formatting output. Disables legacy comment/exit annotation traces in rendered markdown, emitting only construct references plus Doxygen field bullets when available.
    """
    analyzer = SourceAnalyzer()
    md_parts = []
    ok_count = 0
    fail_count = 0

    for fpath in filepaths:
        if not os.path.isfile(fpath):
            if verbose:
                print(f"  SKIP  {fpath} (file not found)", file=sys.stderr)
            continue

        lang = detect_language(fpath)
        if not lang:
            if verbose:
                print(f"  SKIP  {fpath} (unsupported extension)", file=sys.stderr)
            continue

        try:
            elements = analyzer.analyze(fpath, lang)
            lang_key = lang.lower().strip().lstrip(".")
            spec = analyzer.specs[lang_key]
            analyzer.enrich(elements, lang_key, filepath=fpath)

            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                total_lines = sum(1 for _ in f)

            md_output = format_markdown(
                elements,
                fpath,
                lang_key,
                spec.name,
                total_lines,
                include_legacy_annotations=False,
            )

            md_parts.append(md_output)
            ok_count += 1
            if verbose:
                print(f"  OK    {fpath}", file=sys.stderr)

        except Exception as e:
            if verbose:
                print(f"  FAIL  {fpath} ({e})", file=sys.stderr)
            fail_count += 1

    if not md_parts:
        raise ValueError("No valid source files processed")

    if verbose:
        print(f"\n  Processed: {ok_count} ok, {fail_count} failed",
              file=sys.stderr)

    return "\n\n---\n\n".join(md_parts)


def main():
    """! @brief Execute the standalone markdown generation CLI command.
    @details Expects file paths as command-line arguments. Prints generated markdown to stdout.
    """
    if len(sys.argv) < 2:
        print("Usage: python generate_markdown.py file1 [file2 ...]",
              file=sys.stderr)
        sys.exit(1)

    try:
        md = generate_markdown(sys.argv[1:])
        print(md)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
