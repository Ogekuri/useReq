"""Tests for the --files-tokens, --files-references, --files-compress,
--references, --compress, --enable-line-numbers, and --tokens CLI commands.

Covers: CMD-001 through CMD-017.
"""

import contextlib
import io
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
    "Satisfies",
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
    ("@satisfies", "Satisfies"),
    ("@pre", "Pre"),
    ("@post", "Post"),
]
DOXYGEN_OUTPUT_LABEL_PATTERNS: Dict[str, re.Pattern[str]] = {
    label: re.compile(rf"(?m)^\s*-\s*{re.escape(label)}:")
    for _, label in DOXYGEN_TAG_TO_LABEL_IN_ORDER
}
DOXYGEN_SOURCE_TAG_PATTERNS: Dict[str, re.Pattern[str]] = {
    "@brief": re.compile(r"(?<!\w)@brief\b"),
    "@details": re.compile(r"(?<!\w)@details\b"),
    "@param": re.compile(r"(?<!\w)@param(?!\s*\[)\b"),
    "@param[in]": re.compile(r"(?<!\w)@param\s*\[\s*in\s*\]"),
    "@param[out]": re.compile(r"(?<!\w)@param\s*\[\s*out\s*\]"),
    "@return": re.compile(r"(?<!\w)@return\b"),
    "@retval": re.compile(r"(?<!\w)@retval\b"),
    "@exception": re.compile(r"(?<!\w)@exception\b"),
    "@throws": re.compile(r"(?<!\w)@throws\b"),
    "@warning": re.compile(r"(?<!\w)@warning\b"),
    "@deprecated": re.compile(r"(?<!\w)@deprecated\b"),
    "@note": re.compile(r"(?<!\w)@note\b"),
    "@see": re.compile(r"(?<!\w)@see\b"),
    "@sa": re.compile(r"(?<!\w)@sa\b"),
    "@satisfies": re.compile(r"(?<!\w)@satisfies\b"),
    "@pre": re.compile(r"(?<!\w)@pre\b"),
    "@post": re.compile(r"(?<!\w)@post\b"),
}
DOXYGEN_SOURCE_MULTILINE_ENTRY_PATTERN = re.compile(
    r"(?is)(?:@|\\)(?P<tag>brief|details|param\s*\[\s*in\s*\]|"
    r"param\s*\[\s*out\s*\]|param|return|retval|exception|throws|"
    r"warning|deprecated|note|see|sa|satisfies|pre|post)(?=\s|$)"
    r"(?P<body>.*?)(?=(?:\n[^\n]*(?:@|\\)(?:brief|details|param\s*\[\s*in\s*\]|"
    r"param\s*\[\s*out\s*\]|param|return|retval|exception|throws|"
    r"warning|deprecated|note|see|sa|satisfies|pre|post)(?=\s|$))|\Z)"
)
PROJECT_EXAMPLES_DIR = Path(__file__).parent / "project_examples"
CMD_MAJOR_SAMPLE_SOURCE = """## @brief CLI entry-point for the `major` release subcommand.
# @details Increments the major semver index (resets minor and patch to 0), merges and pushes
# to both configured `develop` and `master` branches, regenerates changelog via a
# temporary local tag on `work`, and creates the definitive release tag on `master`
# immediately before pushing `master` with `--tags`.
# @param extra Iterable of CLI argument strings; accepted flag: `--include-patch`.
# @return None; delegates to `_run_release_command("major", ...)`.
# @satisfies REQ-026, REQ-045
def cmd_major(extra):
    changelog_args = _parse_release_flags(extra, "major")
    _run_release_command("major", changelog_args=changelog_args)
"""


def _aggregate_reference_doxygen_fields(element) -> Dict[str, List[str]]:
    """! @brief Aggregate Doxygen fields for references output from associated and body comments.
    @param element SourceAnalyzer element potentially containing doxygen_fields and body_comments.
    @return Deterministic tag->values mapping preserving discovery order.
    @details Merges `element.doxygen_fields` and parsed Doxygen tags from each body-comment tuple.
    """
    aggregate: Dict[str, List[str]] = {}

    direct_fields = getattr(element, "doxygen_fields", None) or {}
    for tag, values in direct_fields.items():
        if tag not in aggregate:
            aggregate[tag] = []
        aggregate[tag].extend(values)

    for body_comment in getattr(element, "body_comments", []):
        if not isinstance(body_comment, tuple) or len(body_comment) < 3:
            continue
        parsed = parse_doxygen_comment(body_comment[2])
        for tag, values in parsed.items():
            if tag not in aggregate:
                aggregate[tag] = []
            aggregate[tag].extend(values)

    return aggregate


def _collect_reference_rendered_elements(filepath: Path) -> list:
    """! @brief Collect constructs that are rendered by references markdown definitions section.
    @param filepath Source file analyzed by references flow.
    @return Ordered list of elements rendered as top-level definitions plus mapped children.
    @details Mirrors `format_markdown()` selection strategy: skip comments/imports/decorators,
    include all depth-0 definitions, then append child elements mapped by parent_name and span.
    """
    language = detect_language(str(filepath))
    assert language is not None, f"Unsupported fixture extension: {filepath}"

    analyzer = SourceAnalyzer()
    elements = analyzer.analyze(str(filepath), language)
    analyzer.enrich(elements, language, str(filepath))

    skipped_types = {
        ElementType.COMMENT_SINGLE,
        ElementType.COMMENT_MULTI,
        ElementType.IMPORT,
        ElementType.DECORATOR,
    }
    definitions = sorted(
        [e for e in elements if e.element_type not in skipped_types],
        key=lambda e: e.line_start,
    )
    top_level = [e for e in definitions if getattr(e, "depth", 0) == 0]

    children_map: Dict[int, List] = {}
    for element in definitions:
        if getattr(element, "depth", 0) <= 0 or not getattr(element, "parent_name", None):
            continue
        for top in top_level:
            if (
                top.name == element.parent_name
                and top.line_start <= element.line_start
                and top.line_end >= element.line_end
            ):
                children_map.setdefault(id(top), []).append(element)
                break

    ordered_elements = []
    for top in top_level:
        ordered_elements.append(top)
        ordered_elements.extend(
            sorted(children_map.get(id(top), []), key=lambda e: e.line_start)
        )
    return ordered_elements


def _count_source_doxygen_tags(filepath: Path) -> Dict[str, int]:
    """! @brief Count every parseable Doxygen tag occurrence emitted from source constructs."""
    counts = {tag: 0 for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER}
    for element in _collect_reference_rendered_elements(filepath):
        fields = _aggregate_reference_doxygen_fields(element)
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


def _run_cli_capture(args: list[str]) -> tuple[int, str, str]:
    """! @brief Run CLI main() capturing stdout/stderr as plain strings."""
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(
        stderr_buffer
    ):
        rc = main(args)
    return rc, stdout_buffer.getvalue(), stderr_buffer.getvalue()


def _collect_project_examples_source_files() -> list[Path]:
    """! @brief Collect the full list of parser-compatible source files under tests/project_examples."""
    files = []
    for path in PROJECT_EXAMPLES_DIR.rglob("*"):
        if path.is_file() and detect_language(str(path)) is not None:
            files.append(path)
    return sorted(files)


def _init_zero_tag_counts() -> Dict[str, int]:
    """! @brief Initialize zeroed counters for all supported source Doxygen tags."""
    return {tag: 0 for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER}


def _count_source_doxygen_tags_with_regex(filepath: Path) -> Dict[str, int]:
    """! @brief Count source Doxygen tag occurrences in one file using multiline regex."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    counts = _init_zero_tag_counts()
    for match in DOXYGEN_SOURCE_MULTILINE_ENTRY_PATTERN.finditer(text):
        normalized_tag = f"@{re.sub(r'\\s+', '', match.group('tag').lower())}"
        if normalized_tag in counts:
            counts[normalized_tag] += 1
    return counts


def _labels_to_tags_counts(label_counts: Dict[str, int]) -> Dict[str, int]:
    """! @brief Convert output-label counts (Brief:, Param:, ...) to source-tag keys (@brief, @param, ...)."""
    return {
        tag: int(label_counts.get(label, 0))
        for tag, label in DOXYGEN_TAG_TO_LABEL_IN_ORDER
    }


def _merge_tag_counts(base: Dict[str, int], extra: Dict[str, int]) -> Dict[str, int]:
    """! @brief Merge field counters by summation."""
    for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER:
        base[tag] += int(extra.get(tag, 0))
    return base


def _sum_tag_counts(tag_counts: Dict[str, int]) -> int:
    """! @brief Return total occurrences across all supported Doxygen tags."""
    return sum(int(tag_counts[tag]) for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER)


def _format_tag_counts_line(tag_counts: Dict[str, int]) -> str:
    """! @brief Serialize all field counters in fixed deterministic order."""
    return ", ".join(
        f"{tag}={int(tag_counts[tag])}" for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER
    )


def _print_file_tag_counts(phase: str, filepath: Path, tag_counts: Dict[str, int]) -> None:
    """! @brief Print one per-file Doxygen field report line for debugging and auditability."""
    print(
        f"[{phase}] {filepath.as_posix()} | "
        f"fields={_sum_tag_counts(tag_counts)} | {_format_tag_counts_line(tag_counts)}"
    )


def _print_directory_tag_counts(phase: str, tag_counts: Dict[str, int]) -> None:
    """! @brief Print one full-directory Doxygen field report line for debugging and auditability."""
    print(
        f"[{phase}] DIRECTORY_TOTAL | "
        f"fields={_sum_tag_counts(tag_counts)} | {_format_tag_counts_line(tag_counts)}"
    )


def _assert_tag_counts_match(
    expected: Dict[str, int],
    actual: Dict[str, int],
    context_id: str,
) -> None:
    """! @brief Assert exact parity for every tag and total with context-rich mismatch traces."""
    for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER:
        assert int(actual[tag]) == int(expected[tag]), (
            f"{context_id}: mismatch field={tag} expected={int(expected[tag])} "
            f"actual={int(actual[tag])}"
        )
    assert _sum_tag_counts(actual) == _sum_tag_counts(expected), (
        f"{context_id}: mismatch total expected={_sum_tag_counts(expected)} "
        f"actual={_sum_tag_counts(actual)}"
    )


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
    sequences: list[list[str]] = []
    for element in _collect_reference_rendered_elements(filepath):
        aggregate_fields = _aggregate_reference_doxygen_fields(element)
        if not aggregate_fields:
            continue
        sequence = format_doxygen_fields_as_markdown(aggregate_fields)
        if sequence:
            sequences.append(sequence)
    return sequences


def _assert_no_legacy_annotation_lines(output: str) -> None:
    """! @brief Assert output does not contain legacy `L<n>>` annotation traces."""
    assert re.search(r"(?m)^L\d+(?:-\d+)?>", output) is None


def _assert_reference_doxygen_sequences(
    output: str,
    expected_sequences: list[list[str]],
    context_id: str,
) -> None:
    """! @brief Assert references output emits expected Doxygen lines in deterministic order.
    @param output Full markdown payload from --files-references or --references.
    @param expected_sequences Ordered list of expected per-construct Doxygen bullet sequences.
    @param context_id Context marker for assertion diagnostics.
    """
    cursor = -1
    for sequence in expected_sequences:
        for expected_line in sequence:
            idx = output.find(expected_line, cursor + 1)
            assert idx != -1, (
                f"{context_id}: missing expected Doxygen line '{expected_line}'"
            )
            cursor = idx


def _extract_reference_definition_block(output: str, header: str) -> str:
    """! @brief Extract one references definition block starting from a specific heading."""
    start = output.find(header)
    assert start != -1, f"Missing references block header: {header}"

    next_header = output.find("\n### ", start + len(header))
    symbol_index = output.find("\n## Symbol Index", start + len(header))
    end_candidates = [idx for idx in (next_header, symbol_index) if idx != -1]
    end = min(end_candidates) if end_candidates else len(output)
    return output[start:end]


def _extract_reference_definition_block_by_signature(
    output: str,
    signature: str,
) -> str:
    """! @brief Extract one references definition block by function signature text."""
    signature_pattern = re.escape(signature.rstrip(":"))
    match = re.search(
        rf"^### fn `def {signature_pattern}:?`.*?(?=^### |\n## Symbol Index|\Z)",
        output,
        flags=re.M | re.S,
    )
    assert match is not None, f"Missing references block for signature: {signature}"
    return match.group(0)


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


def _build_fixture_specific_pattern(filepath: Path, tag_filter: str) -> str:
    """! @brief Build fixture-specific regex matching every analyzable construct name."""
    all_constructs = _collect_expected_find_constructs(filepath, tag_filter, ".*")
    escaped_names = sorted({re.escape(item["name"]) for item in all_constructs})
    assert escaped_names, f"No analyzable constructs for {filepath.name}"
    return rf"^(?:{'|'.join(escaped_names)})$"


def _count_find_source_doxygen_tags(expected_constructs: list[dict]) -> Dict[str, int]:
    """! @brief Count source Doxygen tags across expected find-construct payload."""
    label_to_tag = {label: tag for tag, label in DOXYGEN_TAG_TO_LABEL_IN_ORDER}
    counts = {tag: 0 for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER}
    for expected in expected_constructs:
        for line in expected["doxygen_lines"]:
            match = re.match(r"^\s*-\s*([^:]+):", line)
            if not match:
                continue
            tag = label_to_tag.get(match.group(1))
            if tag is not None:
                counts[tag] += 1
    return counts


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


def _extract_construct_block_by_name(output: str, type_label: str, name: str) -> str:
    """! @brief Extract one construct markdown block by type and name."""
    for parsed in _extract_construct_blocks(output):
        if parsed["type_label"] == type_label and parsed["name"] == name:
            return parsed["block"]
    raise AssertionError(f"Missing construct block for {type_label}:{name}")


def _assert_cmd_major_doxygen_fields(block: str, context_id: str) -> None:
    """! @brief Assert cmd_major block contains all expected Doxygen fields with key payload fragments."""
    required_lines = [
        "- Brief: CLI entry-point for the `major` release subcommand.",
        "- Param: extra Iterable of CLI argument strings; accepted flag: `--include-patch`.",
        "- Return: None; delegates to `_run_release_command(\"major\", ...)`.",
        "- Satisfies: REQ-026, REQ-045",
    ]
    for line in required_lines:
        assert line in block, f"{context_id}: missing line {line}"

    assert "- Details:" in block, f"{context_id}: missing Details label"
    assert (
        "Increments the major semver index (resets minor and patch to 0), merges and pushes"
        in block
    ), f"{context_id}: missing details leading fragment"
    assert (
        "immediately before pushing `master` with `--tags`." in block
    ), f"{context_id}: missing details trailing fragment"

    ordered_labels = ["- Brief:", "- Details:", "- Param:", "- Return:", "- Satisfies:"]
    previous_idx = -1
    for label in ordered_labels:
        current_idx = block.find(label)
        assert current_idx != -1, f"{context_id}: missing ordered label {label}"
        assert current_idx > previous_idx, f"{context_id}: wrong label order at {label}"
        previous_idx = current_idx


def _write_cmd_major_sample(filepath: Path) -> None:
    """! @brief Write the cmd_major Python sample with Doxygen comments to the target file."""
    filepath.write_text(CMD_MAJOR_SAMPLE_SOURCE, encoding="utf-8")


def _assert_find_construct_listing_matches_expected(
    output: str,
    expected_constructs: list[dict],
    context_id: str,
) -> None:
    """! @brief Assert output construct listing matches expected fixture constructs 1:1."""
    actual_constructs = _extract_construct_blocks(output)
    expected_keys = {
        (
            item["type_label"],
            item["name"],
            int(item["line_start"]),
            int(item["line_end"]),
        )
        for item in expected_constructs
    }
    actual_keys = {
        (
            item["type_label"],
            item["name"],
            int(item["line_start"]),
            int(item["line_end"]),
        )
        for item in actual_constructs
    }
    assert actual_keys == expected_keys, (
        f"{context_id}: construct set mismatch "
        f"missing={sorted(expected_keys - actual_keys)} "
        f"extra={sorted(actual_keys - expected_keys)}"
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
            expected_path = Path(
                os.path.relpath(Path(path).resolve(), Path.cwd().resolve())
            ).as_posix()
            assert len(captured.out) > 0
            assert f"> Path: `{expected_path}`" in captured.out
            assert f"> Path: `{path}`" not in captured.out
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
        _assert_reference_doxygen_sequences(
            output=output,
            expected_sequences=_collect_expected_doxygen_sequences(fixture_file),
            context_id=f"--files-references::{fixture_file.name}",
        )

        _assert_no_legacy_annotation_lines(output)
        _assert_doxygen_markdown_order(output)

    def test_files_references_cli_log_emits_brief_and_param(self, capsys):
        """DOX-014: --files-references must emit semantic Doxygen field content for `log()`."""
        cli_file = Path(__file__).resolve().parents[1] / "src" / "usereq" / "cli.py"
        rc = main(["--files-references", str(cli_file)])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        block = _extract_reference_definition_block(
            output=output,
            header="### fn `def log(msg: str) -> None` (L73-79)",
        )
        assert "- Brief: Prints an informational message." in block
        assert "- Param: msg The message string to print." in block

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

    def test_files_references_cmd_major_extracts_all_expected_doxygen_fields(
        self,
        capsys,
        tmp_path,
    ):
        """DOX-014: --files-references must extract brief/details/param/return/satisfies for cmd_major sample."""
        source_file = tmp_path / "cmd_major_sample.py"
        _write_cmd_major_sample(source_file)

        rc = main(["--files-references", str(source_file)])
        assert rc == 0
        captured = capsys.readouterr()
        block = _extract_reference_definition_block_by_signature(
            captured.out,
            "cmd_major(extra):",
        )
        _assert_cmd_major_doxygen_fields(
            block,
            context_id="--files-references::cmd_major",
        )


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
            expected_path = Path(
                os.path.relpath(Path(path).resolve(), Path.cwd().resolve())
            ).as_posix()
            assert "@@@" in captured.out
            assert f"@@@ {expected_path} | python" in captured.out
            assert f"@@@ {path} | python" not in captured.out
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
        assert str(tmp_path) not in captured.out

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
        _assert_reference_doxygen_sequences(
            output=output,
            expected_sequences=_collect_expected_doxygen_sequences(copied_fixture),
            context_id=f"--references::{fixture_file.name}",
        )

        _assert_no_legacy_annotation_lines(output)
        _assert_doxygen_markdown_order(output)

    def test_references_cli_log_emits_brief_and_param(
        self,
        capsys,
        tmp_path,
        monkeypatch,
    ):
        """DOX-015: --references must emit semantic Doxygen field content for `log()`."""
        src = tmp_path / "src"
        src.mkdir()
        cli_source = Path(__file__).resolve().parents[1] / "src" / "usereq" / "cli.py"
        copied_cli = src / "cli.py"
        shutil.copy(cli_source, copied_cli)

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
        rc = main(["--here", "--references"])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        block = _extract_reference_definition_block(
            output=output,
            header="### fn `def log(msg: str) -> None` (L73-79)",
        )
        assert "- Brief: Prints an informational message." in block
        assert "- Param: msg The message string to print." in block

    def test_references_cmd_major_extracts_all_expected_doxygen_fields(
        self,
        capsys,
        tmp_path,
        monkeypatch,
    ):
        """DOX-015: --references must extract brief/details/param/return/satisfies for cmd_major sample."""
        src = tmp_path / "src"
        src.mkdir()
        source_file = src / "cmd_major_sample.py"
        _write_cmd_major_sample(source_file)

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
        rc = main(["--here", "--references"])
        assert rc == 0
        captured = capsys.readouterr()
        block = _extract_reference_definition_block_by_signature(
            captured.out,
            "cmd_major(extra):",
        )
        _assert_cmd_major_doxygen_fields(
            block,
            context_id="--references::cmd_major",
        )


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
        assert str(tmp_path) not in captured.out
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
        pattern = _build_fixture_specific_pattern(fixture_file, tag_filter)
        expected_constructs = _collect_expected_find_constructs(
            fixture_file,
            tag_filter,
            pattern,
        )
        assert expected_constructs, f"No expected constructs for {fixture_file.name}"
        source_counts = _count_find_source_doxygen_tags(expected_constructs)

        rc = main(["--files-find", tag_filter, pattern, str(fixture_file)])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        assert output
        _assert_find_construct_listing_matches_expected(
            output=output,
            expected_constructs=expected_constructs,
            context_id=f"--files-find::{fixture_file.name}",
        )
        _assert_doxygen_reference_counts(
            source_counts=source_counts,
            output_counts=_count_output_doxygen_labels(output),
            context_id=f"--files-find::{fixture_file.name}",
        )
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

    def test_files_find_strips_comments_from_code_and_keeps_doxygen_header(
        self,
        capsys,
        tmp_path,
    ):
        """FND-005/FND-006/DOX-010: --files-find strips code comments while keeping Doxygen metadata."""
        source_file = tmp_path / "sample.c"
        source_file.write_text(
            "/** @brief Increment value */\n"
            "int inc(int value) {\n"
            "    // single-line comment\n"
            "    int out = value + 1; /* inline block */\n"
            "    return out;\n"
            "}\n",
            encoding="utf-8",
        )

        rc = main(["--files-find", "FUNCTION", "^inc$", str(source_file)])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out
        assert "- Brief: Increment value" in output

        block = _extract_construct_block(output, "FUNCTION", "inc", 2, 6)
        code_start = block.find("```")
        code_end = block.rfind("```")
        assert code_start != -1 and code_end > code_start
        code_payload = block[code_start:code_end]
        assert "//" not in code_payload
        assert "/*" not in code_payload
        assert "single-line comment" not in code_payload
        assert "inline block" not in code_payload

    def test_files_find_cmd_major_extracts_all_expected_doxygen_fields(
        self,
        capsys,
        tmp_path,
    ):
        """DOX-016: --files-find must extract brief/details/param/return/satisfies for cmd_major sample."""
        source_file = tmp_path / "cmd_major_sample.py"
        _write_cmd_major_sample(source_file)

        rc = main(["--files-find", "FUNCTION", "^cmd_major$", str(source_file)])
        assert rc == 0
        captured = capsys.readouterr()
        block = _extract_construct_block_by_name(captured.out, "FUNCTION", "cmd_major")
        _assert_cmd_major_doxygen_fields(
            block,
            context_id="--files-find::cmd_major",
        )

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
        pattern = _build_fixture_specific_pattern(copied_fixture, tag_filter)
        expected_constructs = _collect_expected_find_constructs(
            copied_fixture,
            tag_filter,
            pattern,
        )
        assert expected_constructs, f"No expected constructs for {fixture_file.name}"
        source_counts = _count_find_source_doxygen_tags(expected_constructs)

        monkeypatch.chdir(tmp_path)
        rc = main(["--here", "--find", tag_filter, pattern])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out

        assert output
        _assert_find_construct_listing_matches_expected(
            output=output,
            expected_constructs=expected_constructs,
            context_id=f"--find::{fixture_file.name}",
        )
        _assert_doxygen_reference_counts(
            source_counts=source_counts,
            output_counts=_count_output_doxygen_labels(output),
            context_id=f"--find::{fixture_file.name}",
        )
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

    def test_find_strips_comments_from_code_and_keeps_doxygen_header(
        self,
        capsys,
        tmp_path,
        monkeypatch,
    ):
        """FND-005/FND-006/DOX-010: --find strips code comments while keeping Doxygen metadata."""
        src = tmp_path / "src"
        src.mkdir()
        source_file = src / "sample.c"
        source_file.write_text(
            "/** @brief Increment value */\n"
            "int inc(int value) {\n"
            "    // single-line comment\n"
            "    int out = value + 1; /* inline block */\n"
            "    return out;\n"
            "}\n",
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
        rc = main(["--here", "--find", "FUNCTION", "^inc$"])
        assert rc == 0
        captured = capsys.readouterr()
        output = captured.out
        assert "- Brief: Increment value" in output

        block = _extract_construct_block(output, "FUNCTION", "inc", 2, 6)
        code_start = block.find("```")
        code_end = block.rfind("```")
        assert code_start != -1 and code_end > code_start
        code_payload = block[code_start:code_end]
        assert "//" not in code_payload
        assert "/*" not in code_payload
        assert "single-line comment" not in code_payload
        assert "inline block" not in code_payload

    def test_find_cmd_major_extracts_all_expected_doxygen_fields(
        self,
        capsys,
        tmp_path,
        monkeypatch,
    ):
        """DOX-017: --find must extract brief/details/param/return/satisfies for cmd_major sample."""
        src = tmp_path / "src"
        src.mkdir()
        source_file = src / "cmd_major_sample.py"
        _write_cmd_major_sample(source_file)

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
        rc = main(["--here", "--find", "FUNCTION", "^cmd_major$"])
        assert rc == 0
        captured = capsys.readouterr()
        block = _extract_construct_block_by_name(captured.out, "FUNCTION", "cmd_major")
        _assert_cmd_major_doxygen_fields(
            block,
            context_id="--find::cmd_major",
        )


class TestProjectExamplesDoxygenOccurrences:
    """DOX-018: Directory-wide Doxygen parity checks split by command semantics."""

    def test_project_examples_doxygen_occurrence_parity_two_phase_flow(self):
        """DOX-018: Validate phase-specific parity for --files-references and --files-find."""
        files = _collect_project_examples_source_files()
        assert files, "No parser-compatible source files found in tests/project_examples"

        print("[FILE-LIST] Complete parser-compatible source files:")
        for index, filepath in enumerate(files, start=1):
            print(f"[FILE-LIST] {index:02d}. {filepath.as_posix()}")

        phase1_baseline_by_file: Dict[Path, Dict[str, int]] = {}
        phase1_baseline_directory = _init_zero_tag_counts()

        for filepath in files:
            baseline_counts = _count_source_doxygen_tags(filepath)
            phase1_baseline_by_file[filepath] = baseline_counts
            _merge_tag_counts(phase1_baseline_directory, baseline_counts)
            _print_file_tag_counts("PHASE1-BASELINE", filepath, baseline_counts)

        _print_directory_tag_counts("PHASE1-BASELINE", phase1_baseline_directory)

        phase1_directory = _init_zero_tag_counts()
        for filepath in files:
            rc, stdout, _ = _run_cli_capture(["--files-references", str(filepath)])
            assert rc == 0, f"phase1::{filepath.as_posix()}: --files-references failed"

            phase1_counts = _labels_to_tags_counts(_count_output_doxygen_labels(stdout))
            _merge_tag_counts(phase1_directory, phase1_counts)
            _print_file_tag_counts("PHASE1", filepath, phase1_counts)

            _assert_tag_counts_match(
                expected=phase1_baseline_by_file[filepath],
                actual=phase1_counts,
                context_id=f"phase1::{filepath.as_posix()}",
            )

        _print_directory_tag_counts("PHASE1", phase1_directory)
        _assert_tag_counts_match(
            expected=phase1_baseline_directory,
            actual=phase1_directory,
            context_id="phase1::directory",
        )

        phase2_expected_directory = _init_zero_tag_counts()
        phase2_directory = _init_zero_tag_counts()
        for filepath in files:
            tag_filter = _build_language_tag_filter(filepath)
            constructs = _collect_expected_find_constructs(
                filepath=filepath,
                tag_filter=tag_filter,
                pattern=".*",
            )
            print(
                f"[PHASE2] {filepath.as_posix()} | "
                f"extractable_constructs={len(constructs)}"
            )

            phase2_expected_counts = _count_find_source_doxygen_tags(constructs)
            _merge_tag_counts(phase2_expected_directory, phase2_expected_counts)
            _print_file_tag_counts("PHASE2-BASELINE", filepath, phase2_expected_counts)

            phase2_file_counts = _init_zero_tag_counts()
            for construct in constructs:
                pattern = rf"^{re.escape(str(construct['name']))}$"
                rc, stdout, _ = _run_cli_capture(
                    [
                        "--files-find",
                        str(construct["type_label"]),
                        pattern,
                        str(filepath),
                    ]
                )
                assert rc == 0, (
                    f"phase2::{filepath.as_posix()}: --files-find failed "
                    f"for {construct['type_label']}:{construct['name']}"
                )

                block = _extract_construct_block(
                    output=stdout,
                    type_label=str(construct["type_label"]),
                    name=str(construct["name"]),
                    line_start=int(construct["line_start"]),
                    line_end=int(construct["line_end"]),
                )
                construct_counts = _labels_to_tags_counts(
                    _count_output_doxygen_labels(block)
                )
                _merge_tag_counts(phase2_file_counts, construct_counts)

                print(
                    f"[PHASE2-CONSTRUCT] {filepath.name} | "
                    f"{construct['type_label']}:{construct['name']} "
                    f"{construct['line_start']}-{construct['line_end']} | "
                    f"fields={_sum_tag_counts(construct_counts)}"
                )

            _merge_tag_counts(phase2_directory, phase2_file_counts)
            _print_file_tag_counts("PHASE2", filepath, phase2_file_counts)
            _assert_tag_counts_match(
                expected=phase2_expected_counts,
                actual=phase2_file_counts,
                context_id=f"phase2::{filepath.as_posix()}",
            )

        _print_directory_tag_counts("PHASE2-BASELINE", phase2_expected_directory)
        _print_directory_tag_counts("PHASE2", phase2_directory)
        _assert_tag_counts_match(
            expected=phase2_expected_directory,
            actual=phase2_directory,
            context_id="phase2::directory",
        )

    @pytest.mark.parametrize(
        "filepath",
        _collect_project_examples_source_files(),
        ids=lambda path: path.as_posix(),
    )
    def test_project_examples_files_references_regex_multiline_per_file_counts(
        self,
        filepath: Path,
    ):
        """DOX-018: Per-file multiline-regex tag discovery must align with --files-references effective count parity."""
        regex_counts = _count_source_doxygen_tags_with_regex(filepath)
        expected_counts = _count_source_doxygen_tags(filepath)
        for tag, _ in DOXYGEN_TAG_TO_LABEL_IN_ORDER:
            if int(expected_counts[tag]) > 0:
                assert int(regex_counts[tag]) > 0, (
                    f"--files-references::{filepath.as_posix()}: "
                    f"regex extraction did not discover effective tag {tag}"
                )

        rc, stdout, _ = _run_cli_capture(["--files-references", str(filepath)])
        assert rc == 0, f"--files-references failed for {filepath.as_posix()}"
        output_tag_counts = _labels_to_tags_counts(_count_output_doxygen_labels(stdout))
        _assert_tag_counts_match(
            expected=expected_counts,
            actual=output_tag_counts,
            context_id=f"--files-references-regex::{filepath.as_posix()}",
        )


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
