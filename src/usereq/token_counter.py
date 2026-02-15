"""
token_counter.py - Token and character counting for generated output.

Uses tiktoken for accurate token counting compatible with
OpenAI/Claude models.
"""

import os

import tiktoken


class TokenCounter:
    """Count tokens using tiktoken encoding (cl100k_base by default)."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, content: str) -> int:
        """Count tokens in content string."""
        try:
            return len(self.encoding.encode(content, disallowed_special=()))
        except Exception:
            return 0

    @staticmethod
    def count_chars(content: str) -> int:
        """Count characters in content string."""
        return len(content)


def count_file_metrics(content: str,
                       encoding_name: str = "cl100k_base") -> dict:
    """Count tokens and chars for a content string.

    Returns dict with 'tokens' and 'chars' keys.
    """
    counter = TokenCounter(encoding_name)
    return {
        "tokens": counter.count_tokens(content),
        "chars": TokenCounter.count_chars(content),
    }


def count_files_metrics(file_paths: list,
                        encoding_name: str = "cl100k_base") -> list:
    """Count tokens and chars for a list of files.

    Returns a list of dicts with 'file', 'tokens', 'chars' keys.
    Errors are reported with tokens=0, chars=0, and an 'error' key.
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
    """Format a pack summary string from a list of file metrics.

    Args:
        results: list of dicts from count_files_metrics().

    Returns:
        Formatted summary string with per-file details and totals.
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
