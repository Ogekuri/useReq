#!/usr/bin/env python3
"""!
@file compress_files.py
@brief Compress and concatenate multiple source files.
@details Uses the compress module to strip comments and whitespace from each input file, then concatenates results with a compact header per file for unique identification by an LLM agent.
@author GitHub Copilot
@version 0.0.70
"""

import os
import sys
from pathlib import Path

from .compress import compress_file, detect_language


def _extract_line_range(compressed_with_line_numbers: str) -> tuple[int, int]:
    """! @brief Extract source line interval from compressed output with <n>: prefixes.
    @param compressed_with_line_numbers Compressed payload generated with include_line_numbers=True.
    @return Tuple (line_start, line_end) derived from preserved <n>: prefixes; returns (0, 0) when no prefixed lines exist.
    @details Parses the first token of each line as an integer line number.
    """
    line_numbers: list[int] = []
    for line in compressed_with_line_numbers.splitlines():
        marker, sep, _ = line.partition(":")
        if sep and marker.isdigit():
            line_numbers.append(int(marker))

    if not line_numbers:
        return 0, 0

    return line_numbers[0], line_numbers[-1]


def _format_output_path(filepath: str, output_base: Path | None) -> str:
    """! @brief Build the header-visible path for one compressed source file.
    @param filepath Absolute or relative source file path.
    @param output_base Project-home base used to relativize output paths.
    @return Original filepath when output_base is None; otherwise POSIX relative path from output_base.
    """
    if output_base is None:
        return filepath
    absolute_path = Path(filepath).resolve()
    return Path(os.path.relpath(absolute_path, output_base)).as_posix()


def compress_files(filepaths: list[str],
                   include_line_numbers: bool = True,
                   verbose: bool = False,
                   output_base: Path | None = None) -> str:
    """! @brief Compress multiple source files and concatenate with identifying headers.
    @param filepaths List of source file paths.
    @param include_line_numbers If True (default), keep <n>: prefixes in code block lines.
    @param verbose If True, emits progress status messages on stderr.
    @param output_base Project-home base used to render header paths as relative paths.
    @return Concatenated compressed output string.
    @throws ValueError If no files could be processed.
    @details Each file is compressed and emitted as: header line `@@@ <path> | <lang>`, line-range metadata `> Lines: <start>-<end>`, and fenced code block delimited by triple backticks. Line range is derived from the already computed <n>: prefixes to preserve existing numbering logic. Files are separated by a blank line.
    """
    parts = []
    ok_count = 0
    fail_count = 0
    resolved_output_base = output_base.resolve() if output_base is not None else None

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
            output_path = _format_output_path(fpath, resolved_output_base)
            header = f"@@@ {output_path} | {lang}"
            parts.append(
                f"{header}\n> Lines: {line_start}-{line_end}\n```\n{compressed}\n```"
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
    """! @brief Execute the multi-file compression CLI command.
    @details Parses command-line arguments, calls `compress_files`, and prints output or errors.
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="Compress and concatenate source files for LLM context.")
    parser.add_argument("files", nargs="+", help="Source files to compress.")
    parser.add_argument("--enable-line-numbers", action="store_true",
                        default=False,
                        help="Enable line number prefixes (<n>:) in output.")
    args = parser.parse_args()

    try:
        output = compress_files(args.files, args.enable_line_numbers)
        print(output)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
