"""!
@file token_counter.py
@brief Token and character counting for generated output.
@details Uses tiktoken for accurate token counting compatible with OpenAI/Claude models.
@author GitHub Copilot
@version 0.0.70
"""

import os

import tiktoken


class TokenCounter:
    """! @brief Count tokens using tiktoken encoding (cl100k_base by default).
    @details Wrapper around tiktoken encoding to simplify token counting operations.
    """

    def __init__(self, encoding_name: str = "cl100k_base"):
        """! @brief Initialize token counter with a specific tiktoken encoding.
        @param encoding_name Name of tiktoken encoding used for tokenization.
        """
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, content: str) -> int:
        """! @brief Count tokens in content string.
        @param content The text content to tokenize.
        @return Integer count of tokens.
        @details Uses `disallowed_special=()` to allow special tokens in input without raising errors. Returns 0 on failure.
        """
        try:
            return len(self.encoding.encode(content, disallowed_special=()))
        except Exception:
            return 0

    @staticmethod
    def count_chars(content: str) -> int:
        """! @brief Count characters in content string.
        @param content The text string.
        @return Integer count of characters.
        """
        return len(content)


def count_file_metrics(content: str,
                       encoding_name: str = "cl100k_base") -> dict:
    """! @brief Count tokens and chars for a content string.
    @param content The text content to measure.
    @param encoding_name The tiktoken encoding name (default: "cl100k_base").
    @return Dictionary with keys 'tokens' (int) and 'chars' (int).
    """
    counter = TokenCounter(encoding_name)
    return {
        "tokens": counter.count_tokens(content),
        "chars": TokenCounter.count_chars(content),
    }


def count_files_metrics(file_paths: list,
                        encoding_name: str = "cl100k_base") -> list:
    """! @brief Count tokens and chars for a list of files.
    @param file_paths List of file paths to process.
    @param encoding_name The tiktoken encoding name.
    @return List of dictionaries, each containing 'file', 'tokens', 'chars', and optionally 'error'.
    @details Iterates through files, reading content and counting metrics. Gracefully handles read errors.
    """
    counter = TokenCounter(encoding_name)
    results = []
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            results.append({
                "file": path,
                "tokens": counter.count_tokens(content),
                "chars": counter.count_chars(content),
            })
        except Exception as e:
            results.append({
                "file": path,
                "tokens": 0,
                "chars": 0,
                "error": str(e),
            })
    return results


def format_pack_summary(results: list) -> str:
    """! @brief Format a pack summary string from a list of file metrics.
    @param results List of metrics dictionaries from count_files_metrics().
    @return Formatted summary string with per-file details and totals.
    @details Generates a human-readable report including icons, per-file stats, and aggregate totals.
    """
    lines = []
    total_tokens = 0
    total_chars = 0
    total_files = len(results)

    for r in results:
        fname = os.path.basename(r["file"])
        tokens = r["tokens"]
        chars = r["chars"]
        total_tokens += tokens
        total_chars += chars
        if "error" in r:
            lines.append(f"  ❌ {fname}: ERROR - {r['error']}")
        else:
            lines.append(f"  📄 {fname}: {tokens:,} tokens, {chars:,} chars")

    lines.append("")
    lines.append("📊 Pack Summary:")
    lines.append("────────────────")
    lines.append(f"  Total Files: {total_files} files")
    lines.append(f" Total Tokens: {total_tokens:,} tokens")
    lines.append(f"  Total Chars: {total_chars:,} chars")
    return "\n".join(lines)
