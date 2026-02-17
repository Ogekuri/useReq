"""Tests for the --files-tokens, --files-references, --files-compress,
--references, --compress, --enable-line-numbers, and --tokens CLI commands.

Covers: CMD-001 through CMD-017.
"""

import json
import os
import tempfile
import shutil
import re
from typing import Dict, List

import pytest

from usereq.cli import (
    main,
    EXCLUDED_DIRS,
    SUPPORTED_EXTENSIONS,
    _collect_source_files,
)
from pathlib import Path
from usereq.doxygen_parser import format_doxygen_fields_as_markdown
from usereq.doxygen_parser import parse_doxygen_comment
from usereq.find_constructs import LANGUAGE_TAGS
from usereq.generate_markdown import detect_language
from usereq.source_analyzer import ElementType, SourceAnalyzer


FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_FILES = sorted(FIXTURES_DIR.glob("fixture_*.*"))
DOXYGEN_TAG_LABELS_IN_ORDER = [
    "Brief",
    "Details",
    "Param",
    "Param[in]",
    "Param[out]",
    "Return",
    "Retval",
    "Exception",
    "Throws",
    "Warning",
    "Deprecated",
    "Note",
    "See",
    "Sa",
    "Pre",
    "Post",
]
DOXYGEN_TAG_TO_LABEL_IN_ORDER: list[tuple[str, str]] = [
    ("@brief", "Brief"),
    ("@details", "Details"),
    ("@param", "Param"),
    ("@param[in]", "Param[in]"),
    ("@param[out]", "Param[out]"),
    ("@return", "Return"),
    ("@retval", "Retval"),
    ("@exception", "Exception"),
    ("@throws", "Throws"),
    ("@warning", "Warning"),
    ("@deprecated", "Deprecated"),
    ("@note", "Note"),
    ("@see", "See"),
    ("@sa", "Sa"),
    ("@pre", "Pre"),
    ("@post", "Post"),
]
DOXYGEN_OUTPUT_LABEL_PATTERNS: Dict[str, re.Pattern[str]] = {
    label: re.compile(rf"(?m)^\s*-\s*{re.escape(label)}:")
    for _, label in DOXYGEN_TAG_TO_LABEL_IN_ORDER
}


def _count_source_doxygen_tags(filepath: Path) -> Dict[str, int]:
    """! @brief Count every parseable Doxygen tag occurrence emitted from source constructs."""
    language = detect_language(str(filepath))
    assert language is not None, f"Unsupported fixture extension: {filepath}"

    analyzer = SourceAnalyzer()
    elements = analyzer.analyze(str(filepath), language)
    analyzer.enrich(elements, language, str(filepath))

    counts = {tag: 0 for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER}
    skipped_types = {
        ElementType.COMMENT_SINGLE,
        ElementType.COMMENT_MULTI,
        ElementType.IMPORT,
        ElementType.DECORATOR,
    }
    for element in elements:
        if element.element_type in skipped_types:
            continue
        fields = getattr(element, "doxygen_fields", None) or {}
        for tag in counts:
            normalized_tag = tag[1:]
            if fields.get(normalized_tag):
                counts[tag] += 1

    return counts


def _count_output_doxygen_labels(output: str) -> Dict[str, int]:
    """! @brief Count every supported Doxygen output label occurrence in references output."""
    return {
        label: len(pattern.findall(output))
        for label, pattern in DOXYGEN_OUTPUT_LABEL_PATTERNS.items()
    }


def _assert_doxygen_reference_counts(
    source_counts: Dict[str, int],
    output_counts: Dict[str, int],
    context_id: str,
) -> None:
    """! @brief Assert 1:1 parity between source Doxygen tags and emitted reference labels."""
    for tag, label in DOXYGEN_TAG_TO_LABEL_IN_ORDER:
        assert output_counts[label] == source_counts[tag], (
            f"{context_id}: mismatch {tag} ({source_counts[tag]}) "
            f"vs {label}: ({output_counts[label]})"
        )

    source_total = sum(source_counts.values())
    output_total = sum(output_counts.values())
    assert output_total == source_total, (
        f"{context_id}: total mismatch source={source_total} output={output_total}"
    )


def _collect_expected_doxygen_sequences(filepath: Path) -> list[list[str]]:
    """! @brief Build deterministic expected Doxygen markdown sequences for one source file."""
    language = detect_language(str(filepath))
    assert language is not None, f"Unsupported fixture extension: {filepath}"

    analyzer = SourceAnalyzer()
    elements = analyzer.analyze(str(filepath), language)
    analyzer.enrich(elements, language, str(filepath))

    sequences: list[list[str]] = []
    skipped_types = {
        ElementType.COMMENT_SINGLE,
        ElementType.COMMENT_MULTI,
        ElementType.IMPORT,
        ElementType.DECORATOR,
    }
    for element in elements:
        if element.element_type in skipped_types:
            continue
        if getattr(element, "doxygen_fields", None):
            sequence = format_doxygen_fields_as_markdown(element.doxygen_fields)
            if sequence:
                sequences.append(sequence)
    return sequences


def _assert_no_legacy_annotation_lines(output: str) -> None:
    """! @brief Assert output does not contain legacy `L<n>>` annotation traces."""
    assert re.search(r"(?m)^L\d+(?:-\d+)?>", output) is None


def _assert_doxygen_markdown_order(output: str) -> None:
    """! @brief Assert each contiguous Doxygen bullet block follows DOX-011 ordering."""
    label_order = {
        label: index for index, label in enumerate(DOXYGEN_TAG_LABELS_IN_ORDER)
    }
    in_block = False
    last_index = -1

    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and ":" in stripped:
            label = stripped[2:].split(":", 1)[0]
            if label in label_order:
                current_index = label_order[label]
                if not in_block:
                    in_block = True
                    last_index = current_index
                else:
                    assert current_index >= last_index
                    last_index = current_index
                continue
        in_block = False
        last_index = -1


def _merge_doxygen_fields(
    base_fields: Dict[str, List[str]],
    extra_fields: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """! @brief Merge Doxygen fields preserving insertion order inside each tag."""
    for tag, values in extra_fields.items():
        if tag not in base_fields:
            base_fields[tag] = []
        base_fields[tag].extend(values)
    return base_fields


def _collect_expected_find_constructs(
    filepath: Path,
    tag_filter: str,
    pattern: str,
) -> list[dict]:
    """! @brief Build deterministic expected find-construct payload from static analysis."""
    language = detect_language(str(filepath))
    assert language is not None, f"Unsupported fixture extension: {filepath}"

    analyzer = SourceAnalyzer()
    elements = analyzer.analyze(str(filepath), language)
    analyzer.enrich(elements, language, str(filepath))

    tag_set = {tag.strip().upper() for tag in tag_filter.split("|") if tag.strip()}
    expected = []
    for element in elements:
        if not element.name:
            continue
        if element.type_label not in tag_set:
            continue
        if not re.search(pattern, element.name):
            continue

        aggregate_fields: Dict[str, List[str]] = {}
        if getattr(element, "doxygen_fields", None):
            _merge_doxygen_fields(aggregate_fields, element.doxygen_fields)
        for body_comment in getattr(element, "body_comments", []):
            if not isinstance(body_comment, tuple) or len(body_comment) < 3:
                continue
            parsed = parse_doxygen_comment(body_comment[2])
            if parsed:
                _merge_doxygen_fields(aggregate_fields, parsed)

        expected.append(
            {
                "type_label": element.type_label,
                "name": element.name,
                "line_start": element.line_start,
                "line_end": element.line_end,
                "doxygen_lines": format_doxygen_fields_as_markdown(aggregate_fields),
            }
        )

    return expected


def _extract_construct_blocks(output: str) -> list[dict]:
    """! @brief Parse all construct blocks from find-command markdown output."""
    blocks: list[dict] = []
    pattern = re.compile(
        r"### ([A-Z_]+): `([^`]+)`\n(.*?)(?=\n### [A-Z_]+: `|\Z)",
        re.S,
    )
    for match in pattern.finditer(output):
        type_label = match.group(1)
        name = match.group(2)
        block = match.group(0)
        body = match.group(3)
        lines_match = re.search(r"- Lines: (\d+)-(\d+)", body)
        if lines_match is None:
            continue
        blocks.append(
            {
                "type_label": type_label,
                "name": name,
                "line_start": int(lines_match.group(1)),
                "line_end": int(lines_match.group(2)),
                "block": block,
            }
        )
    return blocks


def _extract_construct_block(
    output: str,
    type_label: str,
    name: str,
    line_start: int,
    line_end: int,
) -> str:
    """! @brief Extract one construct markdown block by type, name, and line range."""
    for parsed in _extract_construct_blocks(output):
        if (
            parsed["type_label"] == type_label
            and parsed["name"] == name
            and parsed["line_start"] == line_start
            and parsed["line_end"] == line_end
        ):
            return parsed["block"]

    escaped_type = re.escape(type_label)
    escaped_name = re.escape(name)
    raise AssertionError(
        "Missing construct block for "
        f"{escaped_type}:{escaped_name}:{line_start}-{line_end}"
    )


def _assert_find_construct_doxygen_block(
    output: str,
    expected_construct: dict,
) -> None:
    """! @brief Assert one find-construct block emits expected Doxygen section semantics."""
    block = _extract_construct_block(
        output,
        expected_construct["type_label"],
        expected_construct["name"],
        expected_construct["line_start"],
        expected_construct["line_end"],
    )
    expected_lines = expected_construct["doxygen_lines"]

    lines_idx = block.find("- Lines:")
    code_idx = block.find("```")
    assert lines_idx != -1
    assert code_idx != -1
    assert lines_idx < code_idx

    if expected_lines:
        cursor = lines_idx
        for line in expected_lines:
            idx = block.find(line, cursor + 1)
            assert idx != -1, (
                f"Missing expected Doxygen line '{line}' "
                f"for {expected_construct['type_label']}:{expected_construct['name']}"
            )
            assert idx < code_idx
            cursor = idx
    else:
        doxygen_prefixes = [f"- {label}:" for label in DOXYGEN_TAG_LABELS_IN_ORDER]
        metadata_section = block[lines_idx:code_idx]
        for prefix in doxygen_prefixes:
            assert prefix not in metadata_section


def _build_language_tag_filter(filepath: Path) -> str:
    """! @brief Build full language-specific tag filter string for find commands."""
    language = detect_language(str(filepath))
    assert language is not None, f"Unsupported fixture extension: {filepath}"
    tags = sorted(LANGUAGE_TAGS[language])
    assert tags, f"No tag definition for language '{language}'"
    return "|".join(tags)


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
            assert captured.err == ""
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

    def test_files_references_verbose_outputs_progress(self, capsys):
        """CMD-029: Progress messages must be printed only with --verbose."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            rc = main(["--verbose", "--files-references", path])
            assert rc == 0
            captured = capsys.readouterr()
            assert "OK" in captured.err
            assert "Processed:" in captured.err
        finally:
            os.unlink(path)

    @pytest.mark.parametrize(
        "fixture_file",
        FIXTURE_FILES,
        ids=lambda path: path.name,
    )
    def test_files_references_extracts_doxygen_fields_for_each_fixture(
        self,
        fixture_file,
        capsys,
    ):
        """DOX-014: Every fixture must preserve total Doxygen field count in output."""
        source_counts = _count_source_doxygen_tags(fixture_file)

        rc = main(["--files-references", str(fixture_file)])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        assert output
        output_counts = _count_output_doxygen_labels(output)
        _assert_doxygen_reference_counts(
            source_counts=source_counts,
            output_counts=output_counts,
            context_id=f"--files-references::{fixture_file.name}",
        )

        _assert_no_legacy_annotation_lines(output)
        _assert_doxygen_markdown_order(output)

    def test_files_references_without_doxygen_outputs_only_construct_reference(
        self,
        capsys,
        tmp_path,
    ):
        """DOX-009: Constructs without Doxygen comments must not emit Doxygen bullets."""
        source_file = tmp_path / "plain.py"
        source_file.write_text(
            "def plain_function(value):\n    return value\n",
            encoding="utf-8",
        )

        rc = main(["--files-references", str(source_file)])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        assert "plain_function" in output
        for label in DOXYGEN_TAG_LABELS_IN_ORDER:
            assert f"- {label}:" not in output
        _assert_no_legacy_annotation_lines(output)


class TestFilesCompressCommand:
    """CMD-006, CMD-007, CMD-017: --files-compress tests."""

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
            assert captured.err == ""
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

    def test_files_compress_no_line_numbers_by_default(self, capsys):
        """CMD-017: Must suppress <n>: prefixes by default."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            rc = main(["--files-compress", path])
            assert rc == 0
            captured = capsys.readouterr()
            assert "1: x = 1" not in captured.out
            assert "x = 1" in captured.out
        finally:
            os.unlink(path)

    def test_files_compress_enable_line_numbers(self, capsys):
        """CMD-017: Must include <n>: prefixes when flag is present."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            rc = main(["--files-compress", path, "--enable-line-numbers"])
            assert rc == 0
            captured = capsys.readouterr()
            assert "1: x = 1" in captured.out
            assert "x = 1" in captured.out
        finally:
            os.unlink(path)

    def test_files_compress_verbose_outputs_progress(self, capsys):
        """CMD-029: Progress messages must be printed only with --verbose."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            rc = main(["--verbose", "--files-compress", path])
            assert rc == 0
            captured = capsys.readouterr()
            assert "OK" in captured.err
            assert "Compressed:" in captured.err
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
    """CMD-008, CMD-009, CMD-014, CMD-015: --references tests."""

    def test_requires_base_or_here(self, capsys):
        """CMD-008: Must error without --base or --here."""
        rc = main(["--references"])
        assert rc != 0
        captured = capsys.readouterr()
        assert "--base" in captured.err or "require" in captured.err.lower()

    def test_references_with_here(self, capsys, tmp_path, monkeypatch):
        """CMD-009: With --here must load src-dir from config and ignore --src-dir."""
        src = tmp_path / "cfg_lib"
        src.mkdir()
        (src / "main.py").write_text("def hello():\n    pass\n")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/", "tests-dir": "tests/", "src-dir": ["cfg_lib"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--references", "--src-dir", "mylib"])
        assert rc == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "cfg_lib/main.py" in captured.out

    def test_references_prepends_files_structure(self, capsys, tmp_path, monkeypatch):
        """CMD-015: Must prepend a fenced markdown tree of scanned source files."""
        src = tmp_path / "cfg_src"
        nested = src / "pkg"
        nested.mkdir(parents=True)
        (nested / "main.py").write_text("def hello():\n    return 1\n")
        (nested / "skip.txt").write_text("ignore\n")
        excluded = src / "__pycache__"
        excluded.mkdir()
        (excluded / "cached.py").write_text("x = 1\n")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/", "tests-dir": "tests/", "src-dir": ["cfg_src"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--references", "--src-dir", "src"])
        assert rc == 0
        captured = capsys.readouterr()
        assert captured.out.startswith("# Files Structure\n```")
        assert "\n```\n\n# " in captured.out
        assert "cfg_src/pkg/main.py" in captured.out
        assert "skip.txt" not in captured.out
        assert "__pycache__/cached.py" not in captured.out

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

    def test_references_from_legacy_config_keys(self, capsys, tmp_path,
                                                monkeypatch):
        """CMD-014: Must load src-dir from config.json with legacy keys."""
        src = tmp_path / "lib"
        src.mkdir()
        (src / "code.py").write_text("x = 42\n")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "doc-dir": "docs/",
                  "test-dir": "tests/", "src-dir": ["lib"]}
        (req_dir / "config.json").write_text(json.dumps(config))
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--references"])
        assert rc == 0

    @pytest.mark.parametrize(
        "fixture_file",
        FIXTURE_FILES,
        ids=lambda path: path.name,
    )
    def test_references_extracts_doxygen_fields_from_fixture_project(
        self,
        fixture_file: Path,
        capsys,
        tmp_path,
        monkeypatch,
    ):
        """DOX-015: --references must preserve total Doxygen field count for each fixture."""
        src = tmp_path / "src"
        src.mkdir()

        copied_fixture = src / fixture_file.name
        shutil.copy(fixture_file, copied_fixture)

        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {
            "guidelines-dir": "docs/",
            "docs-dir": "docs/",
            "tests-dir": "tests/",
            "src-dir": ["src"],
        }
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")

        source_counts = _count_source_doxygen_tags(copied_fixture)

        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--references"])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        assert output.startswith("# Files Structure\n```")
        assert fixture_file.name in output
        output_counts = _count_output_doxygen_labels(output)
        _assert_doxygen_reference_counts(
            source_counts=source_counts,
            output_counts=output_counts,
            context_id=f"--references::{fixture_file.name}",
        )

        _assert_no_legacy_annotation_lines(output)
        _assert_doxygen_markdown_order(output)


class TestCompressCommand:
    """CMD-010, CMD-011, CMD-017: --compress tests."""

    def test_requires_base_or_here(self, capsys):
        """CMD-010: Must error without --base or --here."""
        rc = main(["--compress"])
        assert rc != 0

    def test_compress_with_here(self, capsys, tmp_path, monkeypatch):
        """CMD-011: With --here must load src-dir from config and ignore --src-dir."""
        src = tmp_path / "cfg_mylib"
        src.mkdir()
        (src / "main.py").write_text("# comment\nx = 1\n\ny = 2\n")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/", "tests-dir": "tests/", "src-dir": ["cfg_mylib"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--compress", "--src-dir", "mylib"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "@@@" in captured.out
        assert "cfg_mylib/main.py" in captured.out
        assert "- Lines: 2-4" in captured.out
        assert "```" in captured.out

    def test_compress_no_line_numbers_by_default(self, capsys, tmp_path, monkeypatch):
        """CMD-017: Must suppress <n>: prefixes by default."""
        src = tmp_path / "cfg_mylib"
        src.mkdir()
        (src / "main.py").write_text("x = 1\n")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/", "tests-dir": "tests/", "src-dir": ["cfg_mylib"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--compress", "--src-dir", "mylib"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "1: x = 1" not in captured.out
        assert "x = 1" in captured.out
        assert "- Lines: 1-1" in captured.out
        assert "```" in captured.out

    def test_compress_enable_line_numbers(self, capsys, tmp_path, monkeypatch):
        """CMD-017: Must include <n>: prefixes when flag is present."""
        src = tmp_path / "cfg_mylib"
        src.mkdir()
        (src / "main.py").write_text("x = 1\n")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/", "tests-dir": "tests/", "src-dir": ["cfg_mylib"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--compress", "--src-dir", "mylib", "--enable-line-numbers"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "1: x = 1" in captured.out
        assert "x = 1" in captured.out
        assert "- Lines: 1-1" in captured.out
        assert "```" in captured.out


class TestTokensCommand:
    """CMD-016: --tokens tests."""

    def test_tokens_requires_base_or_here(self, capsys):
        """CMD-016: Must error without --base or --here."""
        rc = main(["--tokens", "--docs-dir", "docs"])
        assert rc != 0
        captured = capsys.readouterr()
        assert "--base" in captured.err or "--here" in captured.err

    def test_tokens_requires_docs_dir(self, tmp_path):
        """CMD-016: Must error when --docs-dir is missing."""
        rc = main(["--base", str(tmp_path), "--tokens"])
        assert rc != 0

    def test_tokens_counts_docs_files(self, capsys, tmp_path, monkeypatch):
        """CMD-016: With --here must use docs-dir from config and ignore --docs-dir."""
        docs = tmp_path / "cfg_docs"
        docs.mkdir()
        (docs / "a.md").write_text("# A\n", encoding="utf-8")
        (docs / "b.txt").write_text("hello\nworld\n", encoding="utf-8")
        nested = docs / "nested"
        nested.mkdir()
        (nested / "skip.md").write_text("# ignored\n", encoding="utf-8")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "cfg_docs", "tests-dir": "tests/", "src-dir": ["src"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--tokens", "--docs-dir", "docs"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Pack Summary" in captured.out
        assert "a.md" in captured.out
        assert "b.txt" in captured.out
        assert "skip.md" not in captured.out


class TestFindCommandVerbose:
    """CMD-029: Verbose-gated progress output for --files-find and --find."""

    def test_files_find_default_suppresses_progress(self, capsys, tmp_path):
        src = tmp_path / "a.py"
        src.write_text("def foo():\n    return 1\n", encoding="utf-8")
        rc = main(["--files-find", "FUNCTION", "foo", str(src)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "foo" in captured.out
        assert "1: def foo():" not in captured.out
        assert captured.err == ""

    def test_files_find_verbose_outputs_progress(self, capsys, tmp_path):
        src = tmp_path / "a.py"
        src.write_text("def foo():\n    return 1\n", encoding="utf-8")
        rc = main(["--verbose", "--files-find", "FUNCTION", "foo", str(src)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "OK" in captured.err
        assert "Found:" in captured.err

    def test_files_find_enable_line_numbers(self, capsys, tmp_path):
        src = tmp_path / "a.py"
        src.write_text("def foo():\n    return 1\n", encoding="utf-8")
        rc = main(["--files-find", "FUNCTION", "foo", str(src), "--enable-line-numbers"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "1: def foo():" in captured.out

    def test_find_verbose_outputs_progress(self, capsys, tmp_path, monkeypatch):
        src_dir = tmp_path / "cfg_src"
        src_dir.mkdir()
        (src_dir / "a.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/", "tests-dir": "tests/", "src-dir": ["cfg_src"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--verbose", "--here", "--find", "FUNCTION", "foo", "--src-dir", "src"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "OK" in captured.err
        assert "Found:" in captured.err
        assert "1: def foo():" not in captured.out

    def test_find_enable_line_numbers(self, capsys, tmp_path, monkeypatch):
        src_dir = tmp_path / "cfg_src"
        src_dir.mkdir()
        (src_dir / "a.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {"guidelines-dir": "docs/", "docs-dir": "docs/", "tests-dir": "tests/", "src-dir": ["cfg_src"]}
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--find", "FUNCTION", "foo", "--src-dir", "src", "--enable-line-numbers"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "1: def foo():" in captured.out


class TestFindCommandsDoxygen:
    """DOX-016, DOX-017: Doxygen extraction for --files-find and --find."""

    @pytest.mark.parametrize(
        "fixture_file",
        FIXTURE_FILES,
        ids=lambda path: path.name,
    )
    def test_files_find_extracts_doxygen_fields_for_each_fixture(
        self,
        fixture_file: Path,
        capsys,
    ):
        """DOX-016: --files-find equivalent flow must emit expected Doxygen fields for each fixture."""
        tag_filter = _build_language_tag_filter(fixture_file)
        expected_constructs = _collect_expected_find_constructs(
            fixture_file,
            tag_filter,
            ".*",
        )
        assert expected_constructs, f"No expected constructs for {fixture_file.name}"

        rc = main(["--files-find", tag_filter, ".*", str(fixture_file)])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        assert output
        for expected_construct in expected_constructs:
            _assert_find_construct_doxygen_block(output, expected_construct)
        _assert_doxygen_markdown_order(output)

    def test_files_find_without_doxygen_outputs_only_construct_reference(
        self,
        capsys,
        tmp_path,
    ):
        """DOX-010: --files-find must omit Doxygen bullets when no Doxygen comment exists."""
        source_file = tmp_path / "plain.py"
        source_file.write_text(
            "def plain_function(value):\n    return value\n",
            encoding="utf-8",
        )

        rc = main(["--files-find", "FUNCTION", "plain_function", str(source_file)])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out
        assert "FUNCTION: `plain_function`" in output

        block = _extract_construct_block(output, "FUNCTION", "plain_function", 1, 2)
        lines_idx = block.find("- Lines:")
        code_idx = block.find("```")
        assert lines_idx != -1 and code_idx != -1 and lines_idx < code_idx
        metadata_section = block[lines_idx:code_idx]
        for label in DOXYGEN_TAG_LABELS_IN_ORDER:
            assert f"- {label}:" not in metadata_section

    @pytest.mark.parametrize(
        "fixture_file",
        FIXTURE_FILES,
        ids=lambda path: path.name,
    )
    def test_find_extracts_doxygen_fields_for_each_fixture(
        self,
        fixture_file: Path,
        capsys,
        tmp_path,
        monkeypatch,
    ):
        """DOX-017: --find must emit expected Doxygen fields for fixture-backed project scans."""
        src = tmp_path / "src"
        src.mkdir()
        copied_fixture = src / fixture_file.name
        shutil.copy(fixture_file, copied_fixture)

        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {
            "guidelines-dir": "docs/",
            "docs-dir": "docs/",
            "tests-dir": "tests/",
            "src-dir": ["src"],
        }
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")

        tag_filter = _build_language_tag_filter(copied_fixture)
        expected_constructs = _collect_expected_find_constructs(
            copied_fixture,
            tag_filter,
            ".*",
        )
        assert expected_constructs, f"No expected constructs for {fixture_file.name}"

        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--find", tag_filter, ".*"])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        assert output
        for expected_construct in expected_constructs:
            _assert_find_construct_doxygen_block(output, expected_construct)
        _assert_doxygen_markdown_order(output)

    def test_find_without_doxygen_outputs_only_construct_reference(
        self,
        capsys,
        tmp_path,
        monkeypatch,
    ):
        """DOX-010: --find must omit Doxygen bullets when constructs have no Doxygen comments."""
        src = tmp_path / "src"
        src.mkdir()
        source_file = src / "plain.py"
        source_file.write_text(
            "def plain_function(value):\n    return value\n",
            encoding="utf-8",
        )

        req_dir = tmp_path / ".req"
        req_dir.mkdir()
        config = {
            "guidelines-dir": "docs/",
            "docs-dir": "docs/",
            "tests-dir": "tests/",
            "src-dir": ["src"],
        }
        (req_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")

        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--find", "FUNCTION", "plain_function"])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out
        assert "FUNCTION: `plain_function`" in output

        block = _extract_construct_block(output, "FUNCTION", "plain_function", 1, 2)
        lines_idx = block.find("- Lines:")
        code_idx = block.find("```")
        assert lines_idx != -1 and code_idx != -1 and lines_idx < code_idx
        metadata_section = block[lines_idx:code_idx]
        for label in DOXYGEN_TAG_LABELS_IN_ORDER:
            assert f"- {label}:" not in metadata_section


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
