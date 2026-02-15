"""Tests for the usereq.generate_markdown module.

Covers: MKD-001 through MKD-007.
"""

import os
import tempfile

import pytest

from usereq.generate_markdown import detect_language, generate_markdown


class TestDetectLanguage:
    """MKD-002: Language detection from file extension."""

    def test_python_extension(self):
        assert detect_language("test.py") == "python"

    def test_javascript_extension(self):
        assert detect_language("test.js") == "javascript"

    def test_unknown_extension(self):
        assert detect_language("test.txt") is None

    def test_case_insensitive(self):
        assert detect_language("test.PY") == "python"


class TestGenerateMarkdown:
    """MKD-001, MKD-003 through MKD-007: generate_markdown tests."""

    def test_generates_markdown_from_python(self):
        """MKD-001: Must produce markdown from a Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("def hello():\n    return 'world'\n")
            path = f.name
        try:
            md = generate_markdown([path])
            assert isinstance(md, str)
            assert len(md) > 0
        finally:
            os.unlink(path)

    def test_skip_nonexistent_file(self, capsys):
        """MKD-003: Non-existent files must be skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            valid_path = f.name
        try:
            md = generate_markdown(["/nonexistent/file.py", valid_path])
            assert isinstance(md, str)
            captured = capsys.readouterr()
            assert "SKIP" in captured.err
        finally:
            os.unlink(valid_path)

    def test_skip_unsupported_extension(self, capsys):
        """MKD-004: Unsupported extensions must be skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            valid_path = f.name
        unsup = tempfile.NamedTemporaryFile(mode="w", suffix=".xyz",
                                            delete=False)
        unsup.write("data")
        unsup.close()
        try:
            md = generate_markdown([unsup.name, valid_path])
            captured = capsys.readouterr()
            assert "SKIP" in captured.err
        finally:
            os.unlink(valid_path)
            os.unlink(unsup.name)

    def test_no_valid_files_raises(self):
        """MKD-005: No valid files must raise ValueError."""
        with pytest.raises(ValueError, match="No valid source files"):
            generate_markdown(["/nonexistent/file.py"])

    def test_separator_between_files(self):
        """MKD-006: Multiple files separated by ---."""
        files = []
        try:
            for i in range(2):
                f = tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                                delete=False)
                f.write(f"def func{i}():\n    pass\n")
                f.close()
                files.append(f.name)
            md = generate_markdown(files)
            assert "---" in md
        finally:
            for path in files:
                os.unlink(path)
