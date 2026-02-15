#!/usr/bin/env python3
"""
generate_markdown.py - Generate concatenated markdown from arbitrary source files.

Analyzes each input file with source_analyzer and produces a single markdown
output concatenating all results. Prints pack summary to stderr.

Usage (as module):
    from generate_markdown import generate_markdown
    md = generate_markdown(["file1.py", "file2.js"])

Usage (CLI):
    python generate_markdown.py file1.py file2.js ...
    python generate_markdown.py file1.py file2.js ... > output.md
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
    """Detect language from file extension."""
    _, ext = os.path.splitext(filepath)
    return EXT_LANG_MAP.get(ext.lower())


def generate_markdown(filepaths: list[str]) -> str:
    """Analyze source files and return concatenated markdown.

    Args:
        filepaths: List of source file paths to analyze.

    Returns:
        Concatenated markdown string with all file analyses.

    Raises:
        ValueError: If no valid source files are found.
    """
    analyzer = SourceAnalyzer()
    md_parts = []
    ok_count = 0
    fail_count = 0

    for fpath in filepaths:
        if not os.path.isfile(fpath):
            print(f"  SKIP  {fpath} (file not found)", file=sys.stderr)
            continue

        lang = detect_language(fpath)
        if not lang:
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
                elements, fpath, lang_key, spec.name, total_lines)

            md_parts.append(md_output)
            ok_count += 1
            print(f"  OK    {fpath}", file=sys.stderr)

        except Exception as e:
            print(f"  FAIL  {fpath} ({e})", file=sys.stderr)
            fail_count += 1

    if not md_parts:
        raise ValueError("No valid source files processed")

    print(f"\n  Processed: {ok_count} ok, {fail_count} failed",
          file=sys.stderr)

    return "\n\n---\n\n".join(md_parts)


def main():
    """! @brief Execute the standalone markdown generation CLI command."""
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
