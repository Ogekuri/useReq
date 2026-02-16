#!/usr/bin/env python3
"""! @brief Unit tests for find_constructs module.
@details Tests construct extraction, tag filtering, pattern matching, and output formatting for the find_constructs module.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from usereq.find_constructs import (
    LANGUAGE_TAGS,
    construct_matches,
    find_constructs_in_files,
    format_available_tags,
    format_construct,
    language_supports_tags,
    parse_tag_filter,
)
from usereq.source_analyzer import ElementType, SourceElement


def test_parse_tag_filter():
    """! @brief Test tag filter parsing."""
    assert parse_tag_filter("CLASS") == {"CLASS"}
    assert parse_tag_filter("CLASS|FUNCTION") == {"CLASS", "FUNCTION"}
    assert parse_tag_filter("class|function") == {"CLASS", "FUNCTION"}
    assert parse_tag_filter("  CLASS  |  FUNCTION  ") == {"CLASS", "FUNCTION"}
    assert parse_tag_filter("") == set()


def test_language_supports_tags():
    """! @brief Test language tag support checking."""
    assert language_supports_tags("python", {"CLASS", "FUNCTION"})
    assert language_supports_tags("python", {"CLASS"})
    assert not language_supports_tags("python", {"STRUCT"})
    assert language_supports_tags("c", {"STRUCT", "FUNCTION"})
    assert not language_supports_tags("python", {"NONEXISTENT"})


def test_construct_matches():
    """! @brief Test construct matching logic."""
    elem = SourceElement(
        element_type=ElementType.FUNCTION,
        line_start=1,
        line_end=5,
        extract="def test_foo(): pass",
        name="test_foo",
    )

    assert construct_matches(elem, {"FUNCTION"}, "test_.*")
    assert construct_matches(elem, {"FUNCTION", "CLASS"}, "test_.*")
    assert not construct_matches(elem, {"CLASS"}, "test_.*")
    assert not construct_matches(elem, {"FUNCTION"}, "^bar$")

    # Test without name
    elem_no_name = SourceElement(
        element_type=ElementType.COMMENT_SINGLE,
        line_start=1,
        line_end=1,
        extract="# comment",
    )
    assert not construct_matches(elem_no_name, {"COMMENT"}, ".*")


def test_format_construct_with_line_numbers():
    """! @brief Test construct formatting with line numbers."""
    elem = SourceElement(
        element_type=ElementType.FUNCTION,
        line_start=10,
        line_end=12,
        extract="def foo():\n    return 42",
        name="foo",
        signature="def foo()",
    )

    output = format_construct(elem, include_line_numbers=True)
    assert "### FUNCTION: `foo`" in output
    assert "Signature: `def foo()`" in output
    assert "Lines: 10-12" in output
    assert "L10>" in output
    assert "L11>" in output


def test_format_construct_without_line_numbers():
    """! @brief Test construct formatting without line numbers."""
    elem = SourceElement(
        element_type=ElementType.CLASS,
        line_start=1,
        line_end=3,
        extract="class Bar:\n    pass",
        name="Bar",
    )

    output = format_construct(elem, include_line_numbers=False)
    assert "### CLASS: `Bar`" in output
    assert "Lines: 1-3" in output
    assert "L1>" not in output
    assert "class Bar:" in output


def test_find_constructs_basic(tmp_path):
    """! @brief Test basic construct finding functionality."""
    # Create a test Python file
    test_file = tmp_path / "test.py"
    test_file.write_text(
        """def test_foo():
    return 1

def test_bar():
    return 2

def other_func():
    return 3

class TestClass:
    pass
"""
    )

    # Find all test_ functions
    output = find_constructs_in_files(
        [str(test_file)], "FUNCTION", "test_.*", include_line_numbers=True
    )

    assert "test_foo" in output
    assert "test_bar" in output
    assert "other_func" not in output
    assert "TestClass" not in output


def test_find_constructs_multiple_tags(tmp_path):
    """! @brief Test finding with multiple tags."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        """class MyClass:
    pass

def my_function():
    pass

MY_CONSTANT = 42
"""
    )

    # Find classes and functions with "my" prefix
    output = find_constructs_in_files(
        [str(test_file)], "CLASS|FUNCTION", "(?i)my.*", include_line_numbers=False
    )

    assert "MyClass" in output
    assert "my_function" in output
    assert "MY_CONSTANT" not in output


def test_find_constructs_skip_unsupported_language(tmp_path):
    """! @brief Test skipping files with unsupported language/tags."""
    # Create a Python file
    py_file = tmp_path / "test.py"
    py_file.write_text("def foo(): pass")

    # Try to find STRUCT (not supported in Python)
    with pytest.raises(ValueError, match="No constructs found"):
        find_constructs_in_files([str(py_file)], "STRUCT", ".*")


def test_find_constructs_no_matches(tmp_path):
    """! @brief Test error when no constructs match."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass")

    # Pattern that won't match
    with pytest.raises(ValueError, match="No constructs found"):
        find_constructs_in_files([str(test_file)], "FUNCTION", "^nonexistent$")


def test_find_constructs_skip_missing_file():
    """! @brief Test that missing files are skipped."""
    with pytest.raises(ValueError, match="No constructs found"):
        find_constructs_in_files(["/nonexistent/file.py"], "FUNCTION", ".*")


def test_find_constructs_disable_line_numbers(tmp_path):
    """! @brief Test line number prefix disabling."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo():\n    pass")

    output_with = find_constructs_in_files(
        [str(test_file)], "FUNCTION", "foo", include_line_numbers=True
    )
    output_without = find_constructs_in_files(
        [str(test_file)], "FUNCTION", "foo", include_line_numbers=False
    )

    assert "L1>" in output_with
    assert "L1>" not in output_without


def test_find_constructs_no_progress_without_verbose(tmp_path, capsys):
    """! @brief Test that progress messages are suppressed by default."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo():\n    pass")
    find_constructs_in_files([str(test_file)], "FUNCTION", "foo")
    captured = capsys.readouterr()
    assert captured.err == ""


def test_find_constructs_progress_with_verbose(tmp_path, capsys):
    """! @brief Test that progress messages are shown in verbose mode."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo():\n    pass")
    find_constructs_in_files([str(test_file)], "FUNCTION", "foo", verbose=True)
    captured = capsys.readouterr()
    assert "OK" in captured.err
    assert "Found:" in captured.err


def test_language_tags_completeness():
    """! @brief Test that all required languages have tag definitions."""
    required_languages = [
        "python",
        "c",
        "cpp",
        "rust",
        "javascript",
        "typescript",
        "java",
        "go",
        "ruby",
        "php",
        "swift",
        "kotlin",
        "scala",
        "lua",
        "shell",
        "perl",
        "haskell",
        "zig",
        "elixir",
        "csharp",
    ]

    for lang in required_languages:
        assert lang in LANGUAGE_TAGS, f"Missing tag definition for {lang}"
        assert len(LANGUAGE_TAGS[lang]) > 0, f"Empty tag set for {lang}"


def test_format_available_tags():
    """! @brief Test format_available_tags function generates correct output."""
    output = format_available_tags()

    # Check output is non-empty
    assert output, "format_available_tags should return non-empty string"

    # Check it contains all required languages
    required_languages = [
        "C", "Cpp", "Csharp", "Elixir", "Go", "Haskell", "Java",
        "Javascript", "Kotlin", "Lua", "Perl", "Php", "Python",
        "Ruby", "Rust", "Scala", "Shell", "Swift", "Typescript", "Zig"
    ]
    for lang in required_languages:
        assert lang in output, f"format_available_tags should include {lang}"

    # Check format: each line should start with "- " and contain ": "
    lines = output.split("\n")
    assert len(lines) == len(LANGUAGE_TAGS), "Should have one line per language"
    for line in lines:
        assert line.startswith("- "), f"Line should start with '- ': {line}"
        assert ": " in line, f"Line should contain ': ': {line}"

    # Check tags are comma-separated
    for line in lines:
        if ":" in line:
            tags_part = line.split(": ", 1)[1]
            if "," in tags_part:
                assert ", " in tags_part, f"Tags should be comma-space separated: {line}"


def test_find_constructs_error_shows_available_tags(tmp_path):
    """! @brief Test that error messages include available tags listing."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass")

    # Test with invalid tag filter (empty)
    try:
        find_constructs_in_files([str(test_file)], "", ".*")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        error_msg = str(e)
        assert "Available tags by language:" in error_msg
        assert "Python:" in error_msg or "- Python:" in error_msg
        assert "CLASS" in error_msg or "FUNCTION" in error_msg

    # Test with no matches
    try:
        find_constructs_in_files([str(test_file)], "FUNCTION", "^nonexistent_pattern$")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        error_msg = str(e)
        assert "Available tags by language:" in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
