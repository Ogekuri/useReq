#!/usr/bin/env python3
"""! @brief compress_files.py - Compress and concatenate multiple source files.
@details Uses the compress module to strip comments and whitespace from each input file, then concatenates results with a compact header per file for unique identification by an LLM agent. Usage (as module): from compress_files import compress_files output = compress_files(["main.py", "utils.js"]) Usage (CLI): python compress_files.py file1.py file2.js ... python compress_files.py file1.py file2.js ... > packed.txt
"""

import os
import sys

from .compress import compress_file, detect_language


def _extract_line_range(compressed_with_line_numbers: str) -> tuple[int, int]:
    """! @brief Extract source line interval from compressed output with Lnn> prefixes.
    @param compressed_with_line_numbers Compressed payload generated with include_line_numbers=True.
    @return Tuple (line_start, line_end) derived from preserved Lnn> prefixes; returns (0, 0) when no prefixed lines exist.
    """
    line_numbers: list[int] = []
    for line in compressed_with_line_numbers.splitlines():
        if line.startswith("L") and ">" in line:
            marker = line[1:line.find(">")]
            if marker.isdigit():
                line_numbers.append(int(marker))

    if not line_numbers:
        return 0, 0

    return line_numbers[0], line_numbers[-1]


def compress_files(filepaths: list[str],
                   include_line_numbers: bool = True,
                   verbose: bool = False) -> str:
    """! @brief Compress multiple source files and concatenate with identifying headers.
    @details Each file is compressed and emitted as: header line `@@@ <path> | <lang>`, line-range metadata `- Lines: <start>-<end>`, and fenced code block delimited by triple backticks. Line range is derived from the already computed Lnn> prefixes to preserve existing numbering logic. Files are separated by a blank line. Args: filepaths: List of source file paths. include_line_numbers: If True (default), keep Lnn> prefixes in code block lines. verbose: If True, emits progress status messages on stderr. Returns: Concatenated compressed output string. Raises: ValueError: If no files could be processed.
    """
    parts = []
    ok_count = 0
    fail_count = 0

    for fpath in filepaths:
        if not os.path.isfile(fpath):
            if verbose:
                print(f"  SKIP  {fpath} (not found)", file=sys.stderr)
            continue

        lang = detect_language(fpath)
        if not lang:
            if verbose:
                print(f"  SKIP  {fpath} (unsupported extension)", file=sys.stderr)
            continue

        try:
            compressed_with_line_numbers = compress_file(fpath, lang, True)
            line_start, line_end = _extract_line_range(compressed_with_line_numbers)
            compressed = (
                compressed_with_line_numbers
                if include_line_numbers
                else compress_file(fpath, lang, False)
            )
            header = f"@@@ {fpath} | {lang}"
            parts.append(
                f"{header}\n- Lines: {line_start}-{line_end}\n```\n{compressed}\n```"
            )
            ok_count += 1
            if verbose:
                print(f"  OK    {fpath}", file=sys.stderr)
        except Exception as e:
            if verbose:
                print(f"  FAIL  {fpath} ({e})", file=sys.stderr)
            fail_count += 1

    if not parts:
        raise ValueError("No valid source files processed")

    if verbose:
        print(f"\n  Compressed: {ok_count} ok, {fail_count} failed",
              file=sys.stderr)

    return "\n\n".join(parts)


def main():
    """! @brief Execute the multi-file compression CLI command."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Compress and concatenate source files for LLM context.")
    parser.add_argument("files", nargs="+", help="Source files to compress.")
    parser.add_argument("--disable-line-numbers", action="store_true",
                        default=False,
                        help="Disable line number prefixes (Lnn>) in output.")
    args = parser.parse_args()

    try:
        output = compress_files(args.files, not args.disable_line_numbers)
        print(output)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
