"""Tests for the --files-tokens, --files-references, --files-compress,
--references, and --compress CLI commands.

Covers: CMD-001 through CMD-014.
"""

import json
import os
import tempfile
import shutil

import pytest

from usereq.cli import (
    main,
    EXCLUDED_DIRS,
    SUPPORTED_EXTENSIONS,
    _collect_source_files,
)
from pathlib import Path


class TestFilesTokensCommand:
    """CMD-001 through CMD-003: --files-tokens tests."""

    def test_files_tokens_basic(self, capsys):
        """CMD-001: Must output token/char summary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("def hello():\n    return 'world'\n")
            path = f.name
        try:
            rc = main(["--files-tokens", path])
            assert rc == 0
            captured = capsys.readouterr()
            assert "Pack Summary" in captured.out
            assert "tokens" in captured.out
        finally:
            os.unlink(path)

    def test_files_tokens_no_base_required(self, capsys):
        """CMD-002: Must work without --base or --here."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            rc = main(["--files-tokens", path])
            assert rc == 0
        finally:
            os.unlink(path)

    def test_files_tokens_skip_missing(self, capsys):
        """CMD-003: Must skip non-existent files with warning."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            valid_path = f.name
        try:
            rc = main(["--files-tokens", "/nonexistent.py", valid_path])
            assert rc == 0
            captured = capsys.readouterr()
            assert "skipping" in captured.err.lower() or "Warning" in captured.err
        finally:
            os.unlink(valid_path)

    def test_files_tokens_all_missing_errors(self, capsys):
        """CMD-003: All missing files must error."""
        rc = main(["--files-tokens", "/nonexistent1.py", "/nonexistent2.py"])
        assert rc != 0


class TestFilesReferencesCommand:
    """CMD-004, CMD-005: --files-references tests."""

    def test_files_references_basic(self, capsys):
        """CMD-004: Must output markdown."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("class Foo:\n    pass\n")
            path = f.name
        try:
            rc = main(["--files-references", path])
            assert rc == 0
            captured = capsys.readouterr()
            assert len(captured.out) > 0
        finally:
            os.unlink(path)

    def test_files_references_no_base_required(self, capsys):
        """CMD-005: Must work without --base or --here."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            rc = main(["--files-references", path])
            assert rc == 0
        finally:
            os.unlink(path)


class TestFilesCompressCommand:
    """CMD-006, CMD-007: --files-compress tests."""

    def test_files_compress_basic(self, capsys):
        """CMD-006: Must output compressed content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("# comment\nx = 1\n")
            path = f.name
        try:
            rc = main(["--files-compress", path])
            assert rc == 0
            captured = capsys.readouterr()
            assert "@@@" in captured.out
        finally:
            os.unlink(path)

    def test_files_compress_no_base_required(self, capsys):
        """CMD-007: Must work without --base or --here."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            rc = main(["--files-compress", path])
            assert rc == 0
        finally:
            os.unlink(path)


class TestCollectSourceFiles:
    """CMD-012, CMD-013: Source file collection with exclusions."""

    def test_collects_supported_extensions(self, tmp_path):
        """CMD-012: Must collect files with supported extensions."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("x = 1\n")
        (src / "main.js").write_text("var x = 1;\n")
        (src / "readme.txt").write_text("not source\n")
        files = _collect_source_files(["src"], tmp_path)
        assert len(files) == 2
        extensions = {os.path.splitext(f)[1] for f in files}
        assert ".py" in extensions
        assert ".js" in extensions
        assert ".txt" not in extensions

    def test_excludes_dirs(self, tmp_path):
        """CMD-012: Must exclude directories in EXCLUDED_DIRS."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("x = 1\n")
        cache = src / "__pycache__"
        cache.mkdir()
        (cache / "cached.py").write_text("cached\n")
        git = src / ".git"
        git.mkdir()
        (git / "something.py").write_text("git file\n")
        files = _collect_source_files(["src"], tmp_path)
        assert len(files) == 1
        assert all("__pycache__" not in f for f in files)
        assert all(".git" not in f for f in files)

    def test_recursive_scan(self, tmp_path):
        """CMD-013: Must scan recursively."""
        src = tmp_path / "src"
        sub = src / "sub"
        sub.mkdir(parents=True)
        (src / "main.py").write_text("x = 1\n")
        (sub / "helper.py").write_text("y = 2\n")
        files = _collect_source_files(["src"], tmp_path)
        assert len(files) == 2


class TestReferencesCommand:
    """CMD-008, CMD-009, CMD-014: --references tests."""

    def test_requires_base_or_here(self, capsys):
        """CMD-008: Must error without --base or --here."""
        rc = main(["--references"])
        assert rc != 0
        captured = capsys.readouterr()
        assert "--base" in captured.err or "require" in captured.err.lower()

    def test_references_with_here(self, capsys, tmp_path, monkeypatch):
        """CMD-009: Must generate markdown from configured src-dir."""
        src = tmp_path / "mylib"
        src.mkdir()
        (src / "main.py").write_text("def hello():\n    pass\n")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--references", "--src-dir", "mylib"])
        assert rc == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_references_from_config(self, capsys, tmp_path, monkeypatch):
        """CMD-014: Must load src-dir from config.json."""
        src = tmp_path / "lib"
        src.mkdir()
        (src / "code.py").write_text("x = 42\n")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/",
                  "tests-dir": "tests/", "src-dir": ["lib"]}
        (req_dir / "config.json").write_text(json.dumps(config))
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--references"])
        assert rc == 0


class TestCompressCommand:
    """CMD-010, CMD-011: --compress tests."""

    def test_requires_base_or_here(self, capsys):
        """CMD-010: Must error without --base or --here."""
        rc = main(["--compress"])
        assert rc != 0

    def test_compress_with_here(self, capsys, tmp_path, monkeypatch):
        """CMD-011: Must generate compressed output from configured src-dir."""
        src = tmp_path / "mylib"
        src.mkdir()
        (src / "main.py").write_text("# comment\nx = 1\n")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--compress", "--src-dir", "mylib"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "@@@" in captured.out


class TestSupportedExtensions:
    """CMD-012: Verify supported extensions constant."""

    def test_all_20_extensions_present(self):
        """All 20 language extensions must be in SUPPORTED_EXTENSIONS."""
        expected = {
            ".c", ".cpp", ".cs", ".ex", ".go", ".hs", ".java", ".js",
            ".kt", ".lua", ".pl", ".php", ".py", ".rb", ".rs", ".scala",
            ".sh", ".swift", ".ts", ".zig",
        }
        assert expected == SUPPORTED_EXTENSIONS


class TestExcludedDirs:
    """CMD-012: Verify excluded directories constant."""

    def test_common_exclusions_present(self):
        """Common excluded directories must be in EXCLUDED_DIRS."""
        assert ".git" in EXCLUDED_DIRS
        assert ".vscode" in EXCLUDED_DIRS
        assert "tmp" in EXCLUDED_DIRS
        assert "temp" in EXCLUDED_DIRS
        assert ".cache" in EXCLUDED_DIRS
        assert ".pytest_cache" in EXCLUDED_DIRS
        assert "node_modules" in EXCLUDED_DIRS
        assert "__pycache__" in EXCLUDED_DIRS
