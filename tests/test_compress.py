"""Tests for the usereq.compress and usereq.compress_files modules.

Covers: CMP-001 through CMP-012.
"""

import os
import tempfile

import pytest

from usereq.compress import compress_source, compress_file, detect_language
from usereq.compress_files import compress_files


class TestDetectLanguage:
    """CMP-006: Language detection from file extension."""

    def test_python(self):
        assert detect_language("test.py") == "python"

    def test_javascript(self):
        assert detect_language("test.js") == "javascript"

    def test_unknown(self):
        assert detect_language("test.txt") is None


class TestCompressSource:
    """CMP-001 through CMP-005: compress_source tests."""

    def test_removes_comments(self):
        """CMP-001: Comments must be removed."""
        source = "x = 1  # comment\ny = 2\n"
        result = compress_source(source, "python")
        assert "# comment" not in result
        assert "x = 1" in result

    def test_removes_blank_lines(self):
        """CMP-001: Blank lines must be removed."""
        source = "x = 1\n\n\ny = 2\n"
        result = compress_source(source, "python", include_line_numbers=False)
        lines = result.strip().split("\n")
        assert all(line.strip() for line in lines)

    def test_preserves_python_indentation(self):
        """CMP-002: Python indentation must be preserved."""
        source = "def f():\n    x = 1\n    return x\n"
        result = compress_source(source, "python", include_line_numbers=False)
        assert "    x = 1" in result or "    return x" in result

    def test_line_number_prefix(self):
        """CMP-003: Line numbers must use Lnn> format."""
        source = "x = 1\ny = 2\n"
        result = compress_source(source, "python", include_line_numbers=True)
        assert "L1>" in result

    def test_no_line_numbers(self):
        """CMP-003: Line numbers can be disabled."""
        source = "x = 1\n"
        result = compress_source(source, "python", include_line_numbers=False)
        assert "L1>" not in result

    def test_preserves_shebang(self):
        """CMP-004: Shebang lines must be preserved."""
        source = "#!/usr/bin/env python3\nx = 1\n"
        result = compress_source(source, "python", include_line_numbers=False)
        assert "#!/usr/bin/env python3" in result

    def test_comments_in_strings_preserved(self):
        """CMP-005: Comments inside strings must not be removed."""
        source = 'x = "has # inside"\n'
        result = compress_source(source, "python", include_line_numbers=False)
        assert "# inside" in result

    def test_multiline_comment_removal(self):
        """CMP-012: Multi-line comments must be removed."""
        source = '/* block comment */\nint x = 1;\n'
        result = compress_source(source, "c", include_line_numbers=False)
        assert "block comment" not in result
        assert "int x = 1;" in result

    def test_python_docstring_removal(self):
        """CMP-012: Python docstrings must be removed."""
        source = '"""This is a docstring."""\nx = 1\n'
        result = compress_source(source, "python", include_line_numbers=False)
        assert "docstring" not in result

    def test_unsupported_language_raises(self):
        """CMP-001: Unsupported language must raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported language"):
            compress_source("x = 1", "brainfuck")


class TestCompressFile:
    """CMP-006: compress_file tests."""

    def test_compress_python_file(self):
        """Must compress a Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("# comment\nx = 1\n")
            path = f.name
        try:
            result = compress_file(path)
            assert "x = 1" in result
        finally:
            os.unlink(path)

    def test_auto_detect_language(self):
        """Must auto-detect language from extension."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js",
                                         delete=False) as f:
            f.write("// comment\nvar x = 1;\n")
            path = f.name
        try:
            result = compress_file(path)
            assert "var x = 1;" in result
        finally:
            os.unlink(path)

    def test_unknown_extension_raises(self):
        """Must raise ValueError for unknown extension."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz",
                                         delete=False) as f:
            f.write("data")
            path = f.name
        try:
            with pytest.raises(ValueError, match="Cannot detect language"):
                compress_file(path)
        finally:
            os.unlink(path)


class TestCompressFiles:
    """CMP-007 through CMP-011: compress_files tests."""

    def test_header_format(self):
        """CMP-007: Each file must have @@@ header."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            result = compress_files([path])
            assert f"@@@ {path} | python" in result
        finally:
            os.unlink(path)

    def test_skip_nonexistent(self, capsys):
        """CMP-008: Non-existent files must be skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            valid_path = f.name
        try:
            result = compress_files(["/nonexistent.py", valid_path])
            captured = capsys.readouterr()
            assert "SKIP" not in captured.err
        finally:
            os.unlink(valid_path)

    def test_skip_unsupported(self, capsys):
        """CMP-009: Unsupported extensions must be skipped."""
        py_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                              delete=False)
        py_file.write("x = 1\n")
        py_file.close()
        txt_file = tempfile.NamedTemporaryFile(mode="w", suffix=".xyz",
                                               delete=False)
        txt_file.write("data")
        txt_file.close()
        try:
            result = compress_files([txt_file.name, py_file.name])
            captured = capsys.readouterr()
            assert "SKIP" not in captured.err
        finally:
            os.unlink(py_file.name)
            os.unlink(txt_file.name)

    def test_progress_messages_with_verbose(self, capsys):
        """CMP-008, CMP-009, CMP-011: Progress messages must require verbose."""
        py_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                              delete=False)
        py_file.write("x = 1\n")
        py_file.close()
        txt_file = tempfile.NamedTemporaryFile(mode="w", suffix=".xyz",
                                               delete=False)
        txt_file.write("data")
        txt_file.close()
        try:
            compress_files(["/nonexistent.py", txt_file.name, py_file.name], verbose=True)
            captured = capsys.readouterr()
            assert "SKIP" in captured.err
            assert "OK" in captured.err
            assert "Compressed:" in captured.err
        finally:
            os.unlink(py_file.name)
            os.unlink(txt_file.name)

    def test_no_valid_files_raises(self):
        """CMP-010: No valid files must raise ValueError."""
        with pytest.raises(ValueError, match="No valid source files"):
            compress_files(["/nonexistent.py"])

    def test_multiple_files(self):
        """CMP-007: Multiple files must be concatenated."""
        files = []
        try:
            for i in range(2):
                f = tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                                delete=False)
                f.write(f"x{i} = {i}\n")
                f.close()
                files.append(f.name)
            result = compress_files(files)
            assert result.count("@@@") == 2
        finally:
            for path in files:
                os.unlink(path)
