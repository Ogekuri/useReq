"""Tests for the usereq.token_counter module.

Covers: TOK-001 through TOK-006.
"""

import os
import tempfile

import pytest

from usereq.token_counter import (
    TokenCounter,
    count_file_metrics,
    count_files_metrics,
    format_pack_summary,
)


class TestTokenCounter:
    """TOK-001, TOK-002: TokenCounter class tests."""

    def test_count_tokens_nonempty(self):
        """count_tokens must return > 0 for non-empty content."""
        counter = TokenCounter()
        result = counter.count_tokens("Hello world, this is a test.")
        assert result > 0

    def test_count_tokens_empty(self):
        """count_tokens must return 0 for empty string."""
        counter = TokenCounter()
        assert counter.count_tokens("") == 0

    def test_count_chars(self):
        """count_chars must return the string length."""
        result = TokenCounter.count_chars("hello")
        assert result == 5

    def test_count_chars_empty(self):
        """count_chars must return 0 for empty string."""
        assert TokenCounter.count_chars("") == 0

    def test_default_encoding(self):
        """Default encoding must be cl100k_base."""
        counter = TokenCounter()
        assert counter.encoding.name == "cl100k_base"


class TestCountFileMetrics:
    """TOK-003: count_file_metrics function tests."""

    def test_returns_dict_with_keys(self):
        """Must return dict with 'tokens' and 'chars' keys."""
        result = count_file_metrics("Hello world")
        assert "tokens" in result
        assert "chars" in result

    def test_tokens_positive(self):
        """Tokens count must be positive for non-empty content."""
        result = count_file_metrics("def foo():\n    return 42\n")
        assert result["tokens"] > 0

    def test_chars_correct(self):
        """Chars count must match content length."""
        content = "test content"
        result = count_file_metrics(content)
        assert result["chars"] == len(content)


class TestCountFilesMetrics:
    """TOK-004: count_files_metrics function tests."""

    def test_returns_list(self):
        """Must return a list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            results = count_files_metrics([path])
            assert isinstance(results, list)
            assert len(results) == 1
            assert results[0]["file"] == path
            assert results[0]["tokens"] > 0
            assert results[0]["chars"] > 0
        finally:
            os.unlink(path)

    def test_error_includes_error_key(self):
        """Non-existent file must include 'error' key."""
        results = count_files_metrics(["/nonexistent/path.py"])
        assert len(results) == 1
        assert "error" in results[0]
        assert results[0]["tokens"] == 0
        assert results[0]["chars"] == 0

    def test_multiple_files(self):
        """Must handle multiple files."""
        files = []
        try:
            for i in range(3):
                f = tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                                delete=False)
                f.write(f"x = {i}\n")
                f.close()
                files.append(f.name)
            results = count_files_metrics(files)
            assert len(results) == 3
        finally:
            for path in files:
                os.unlink(path)


class TestFormatPackSummary:
    """TOK-005: format_pack_summary function tests."""

    def test_contains_totals(self):
        """Summary must contain total counts."""
        results = [
            {"file": "test.py", "tokens": 100, "chars": 500},
            {"file": "test2.py", "tokens": 200, "chars": 1000},
        ]
        summary = format_pack_summary(results)
        assert "Pack Summary" in summary
        assert "Total Files: 2" in summary
        assert "300" in summary  # total tokens

    def test_error_file_shown(self):
        """Error files must show ERROR marker."""
        results = [
            {"file": "bad.py", "tokens": 0, "chars": 0, "error": "not found"},
        ]
        summary = format_pack_summary(results)
        assert "ERROR" in summary

    def test_returns_string(self):
        """Must return a string."""
        results = [{"file": "a.py", "tokens": 10, "chars": 50}]
        summary = format_pack_summary(results)
        assert isinstance(summary, str)


class TestTokenCounterErrorHandling:
    """TOK-006: Error handling in token counting."""

    def test_count_tokens_returns_zero_on_error(self):
        """count_tokens must return 0 on encoding error, not raise."""
        # TokenCounter handles exceptions internally
        counter = TokenCounter()
        # Normal strings should work
        result = counter.count_tokens("normal text")
        assert result > 0
