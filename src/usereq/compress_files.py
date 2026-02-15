#!/usr/bin/env python3
"""! @brief compress_files.py - Compress and concatenate multiple source files.
@details Uses the compress module to strip comments and whitespace from each input file, then concatenates results with a compact header per file for unique identification by an LLM agent. Usage (as module): from compress_files import compress_files output = compress_files(["main.py", "utils.js"]) Usage (CLI): python compress_files.py file1.py file2.js ... python compress_files.py file1.py file2.js ... > packed.txt
"""

import os
import sys

from .compress import compress_file, detect_language


def compress_files(filepaths: list[str],
                   include_line_numbers: bool = True) -> str:
    """! @brief Compress multiple source files and concatenate with identifying headers.
    @details Each file is compressed and prefixed with a header line: @@@ <path> | <lang> Files are separated by a blank line. Args: filepaths: List of source file paths. include_line_numbers: If True (default), prefix each line with Lnn> format. Returns: Concatenated compressed output string. Raises: ValueError: If no files could be processed.
    """
    parts = []
    ok_count = 0
    fail_count = 0

    for fpath in filepaths:
        if not os.path.isfile(fpath):
            print(f"  SKIP  {fpath} (not found)", file=sys.stderr)
            continue

        lang = detect_language(fpath)
        if not lang:
            print(f"  SKIP  {fpath} (unsupported extension)", file=sys.stderr)
            continue

        try:
            compressed = compress_file(fpath, lang, include_line_numbers)
            header = f"@@@ {fpath} | {lang}"
            parts.append(f"{header}\n{compressed}")
            ok_count += 1
            print(f"  OK    {fpath}", file=sys.stderr)
        except Exception as e:
            print(f"  FAIL  {fpath} ({e})", file=sys.stderr)
            fail_count += 1

    if not parts:
        raise ValueError("No valid source files processed")

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
