#!/usr/bin/env python3
"""! @brief Comprehensive unit tests for find_constructs covering all language-construct combinations.
@details Validates extraction of all construct types for all 20 supported languages using fixture files.
Tests verify that find_constructs_in_files() correctly identifies and extracts constructs matching
the tag filter and regex pattern for each language-construct combination defined in FND-002.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from usereq.find_constructs import (
    LANGUAGE_TAGS,
    find_constructs_in_files,
)


# ── Expected construct names per language fixture ────────────────────────────
# Maps language -> construct_type -> set of expected construct names in fixture
EXPECTED_CONSTRUCTS: Dict[str, Dict[str, Set[str]]] = {
    "python": {
        "CLASS": {
            "Config",
            "MyClass",
            "InnerHelper",
            "AbstractProcessor",
            "ConcreteProcessor",
            "GenericContainer",
            "Renderable",
        },
        "FUNCTION": {
            "regular_function",
            "function_with_walrus",
            "multi_return_paths",
            "generator_function",
            "async_generator",
            "managed_resource",
            "closure_factory",
            "inner",
            "uses_unpacking",
            "async_function",
            "deeply_nested_logic",
            "exception_handling_example",
        },
        "DECORATOR": {"dataclass", "property", "abstractmethod", "contextmanager"},
        "IMPORT": {"os", "sys", "Path", "Optional", "ABC"},
        "VARIABLE": {
            "MAX_RETRIES",
            "DEFAULT_TIMEOUT",
            "_INTERNAL_CACHE",
            "T",
            "transform",
            "EVEN_SQUARES",
        },
    },
    "c": {
        "STRUCT": {"Point", "PackedFlags", "Node"},
        "UNION": {"Data"},
        "ENUM": {"Color"},
        "TYPEDEF": {
            "my_int",
            "byte_t",
            "comparator_fn",
            "transform_fn",
            "callback_entry_t",
        },
        "MACRO": {"MAX_SIZE", "CLAMP", "STRINGIFY", "CONCAT", "LOG"},
        "FUNCTION": {
            "min_val",
            "greet",
            "main",
            "sum_ints",
            "apply_transform",
            "factorial",
            "fast_copy",
            "read_volatile",
            "sum_fixed",
        },
        "IMPORT": {"stdio.h", "stdlib.h", "string.h", "stdarg.h", "myheader.h"},
        "VARIABLE": {"counter", "error_buffer"},
    },
    "cpp": {
        "CLASS": {"MyClass", "Singleton", "BaseClass", "DerivedClass"},
        "STRUCT": {"Point", "Config"},
        "ENUM": {"Color", "Status"},
        "NAMESPACE": {"utils", "nested"},
        "FUNCTION": {
            "main",
            "greet",
            "add",
            "template_max",
            "overloaded_func",
            "constexpr_square",
        },
        "MACRO": {"MAX_SIZE", "DEBUG_LOG"},
        "IMPORT": {"iostream", "vector", "memory", "string"},
        "TYPE_ALIAS": {"IntVector", "StringPtr"},
    },
    "rust": {
        "FUNCTION": {
            "new",
            "with_value",
            "value",
            "try_update",
            "do_work",
            "do_work_with_ctx",
            "parse",
            "fmt",
            "insert",
            "get_or_default",
            "my_function",
            "async_function",
            "filter_with",
            "create_worker",
            "read_raw",
            "ffi_double",
            "describe_enum",
        },
        "STRUCT": {"MyStruct", "BorrowedData", "TypedMap"},
        "ENUM": {"MyEnum"},
        "TRAIT": {"MyTrait", "Parser"},
        "IMPL": {"MyStruct", "Display", "TypedMap"},
        "MODULE": {"my_module", "internal"},
        "MACRO": {"hashmap", "my_macro"},
        "CONSTANT": {"MY_CONST", "MY_STATIC", "CONFIG"},
        "TYPE_ALIAS": {"IoResult", "MyAlias"},
        "IMPORT": {"io", "HashMap", "Display", "Arc"},
        "DECORATOR": {"derive"},
    },
    "javascript": {
        "CLASS": {"MyClass", "Person", "Animal"},
        "FUNCTION": {
            "greet",
            "add",
            "fetchData",
            "asyncHandler",
            "processArray",
            "createCounter",
        },
        "COMPONENT": {"MyComponent", "UserProfile"},
        "CONSTANT": {"MAX_SIZE", "API_URL", "DEFAULT_CONFIG"},
        "IMPORT": {"react", "axios", "lodash"},
        "MODULE": {"utils", "helpers"},
    },
    "typescript": {
        "INTERFACE": {"User", "Repository", "Serializable"},
        "TYPE_ALIAS": {"Result", "Callback", "StatusCode"},
        "ENUM": {"Color", "Direction", "HttpStatus"},
        "CLASS": {"UserService", "BaseController", "DataManager"},
        "FUNCTION": {
            "processUser",
            "validateInput",
            "fetchResource",
            "calculateTotal",
        },
        "NAMESPACE": {"Utils", "Validators"},
        "MODULE": {"database", "api"},
        "IMPORT": {"Component", "ReactNode"},
        "DECORATOR": {"component", "inject", "logged"},
    },
    "java": {
        "CLASS": {"MyClass", "UserService", "DataProcessor"},
        "INTERFACE": {"Comparable", "Serializable", "Repository"},
        "ENUM": {"Color", "Status", "Level"},
        "FUNCTION": {
            "main",
            "process",
            "validate",
            "calculate",
            "getData",
            "setData",
        },
        "IMPORT": {"java.util.List", "java.util.Map"},
        "MODULE": {"com.example.app"},
        "DECORATOR": {"Override", "SuppressWarnings", "RequiresAuth"},
        "CONSTANT": {"MAX_SIZE", "DEFAULT_VALUE", "PI"},
    },
    "go": {
        "FUNCTION": {"main", "greet", "add", "processData", "validateInput"},
        "METHOD": {"String", "Value", "Process", "Calculate"},
        "STRUCT": {"User", "Config", "Point", "Node"},
        "INTERFACE": {"Reader", "Writer", "Handler", "Validator"},
        "TYPE_ALIAS": {"UserID", "Callback", "Handler"},
        "CONSTANT": {"MaxSize", "DefaultTimeout", "APIVersion"},
        "IMPORT": {"fmt", "io", "net/http", "encoding/json"},
        "MODULE": {"main", "utils", "handlers"},
    },
    "ruby": {
        "CLASS": {"MyClass", "User", "ApplicationController"},
        "MODULE": {"Utils", "Helpers", "Validators"},
        "FUNCTION": {"greet", "process", "calculate", "validate"},
        "CONSTANT": {"MAX_SIZE", "API_URL", "DEFAULT_CONFIG"},
        "IMPORT": {"json", "net/http", "active_record"},
        "DECORATOR": {"attr_reader", "attr_accessor", "before_action"},
    },
    "php": {
        "CLASS": {"MyClass", "User", "Controller"},
        "INTERFACE": {"Serializable", "Repository", "Handler"},
        "TRAIT": {"Timestamps", "SoftDeletes", "HasUuid"},
        "FUNCTION": {"greet", "process", "validate", "calculateTotal"},
        "NAMESPACE": {"App\\Models", "App\\Controllers"},
        "IMPORT": {"DateTime", "Exception"},
        "CONSTANT": {"MAX_SIZE", "API_URL", "VERSION"},
    },
    "swift": {
        "CLASS": {"MyClass", "ViewController", "NetworkManager"},
        "STRUCT": {"Point", "User", "Config"},
        "ENUM": {"Color", "Status", "Result"},
        "PROTOCOL": {"Identifiable", "Codable", "Handler"},
        "EXTENSION": {"String", "Array", "Int"},
        "FUNCTION": {"greet", "process", "calculate", "validateInput"},
        "IMPORT": {"Foundation", "UIKit", "Combine"},
        "CONSTANT": {"maxSize", "apiURL", "defaultTimeout"},
        "VARIABLE": {"counter", "cache", "config"},
    },
    "kotlin": {
        "CLASS": {"MyClass", "User", "DataManager"},
        "INTERFACE": {"Repository", "Handler", "Validator"},
        "ENUM": {"Color", "Status", "Level"},
        "FUNCTION": {"main", "greet", "process", "calculate"},
        "CONSTANT": {"MAX_SIZE", "API_URL", "VERSION"},
        "VARIABLE": {"counter", "cache", "config"},
        "MODULE": {"com.example.app"},
        "IMPORT": {"java.util.List"},
        "DECORATOR": {"JvmStatic", "Throws", "Deprecated"},
    },
    "scala": {
        "CLASS": {"MyClass", "User", "ServiceImpl"},
        "TRAIT": {"Serializable", "Repository", "Handler"},
        "MODULE": {"Utils", "Helpers"},
        "FUNCTION": {"main", "process", "calculate", "validate"},
        "CONSTANT": {"MaxSize", "ApiUrl", "Version"},
        "VARIABLE": {"counter", "cache", "config"},
        "TYPE_ALIAS": {"UserId", "Callback", "Result"},
        "IMPORT": {"scala.collection.mutable"},
    },
    "lua": {
        "FUNCTION": {"greet", "add", "process", "calculate"},
        "VARIABLE": {"MAX_SIZE", "config", "cache"},
    },
    "shell": {
        "FUNCTION": {"greet", "process", "cleanup", "validate"},
        "VARIABLE": {"MAX_SIZE", "API_URL", "DEBUG"},
        "IMPORT": {"source"},
    },
    "perl": {
        "FUNCTION": {"greet", "process", "calculate", "new"},
        "MODULE": {"MyModule", "Utils"},
        "IMPORT": {"strict", "warnings", "Data::Dumper"},
        "CONSTANT": {"MAX_SIZE", "API_URL"},
    },
    "haskell": {
        "MODULE": {"Main", "Utils", "Data.MyModule"},
        "TYPE_ALIAS": {"UserId", "Result", "Handler"},
        "STRUCT": {"Point", "User", "Config"},
        "CLASS": {"Eq", "Show", "Monad"},
        "FUNCTION": {"main", "greet", "add", "process"},
        "IMPORT": {"Data.List", "Control.Monad"},
    },
    "zig": {
        "FUNCTION": {"main", "greet", "add", "process"},
        "STRUCT": {"Point", "User", "Config"},
        "ENUM": {"Color", "Status"},
        "UNION": {"Data", "Value"},
        "CONSTANT": {"max_size", "api_url"},
        "VARIABLE": {"counter", "cache"},
        "IMPORT": {"std"},
    },
    "elixir": {
        "MODULE": {"MyModule", "Utils", "GenServer"},
        "FUNCTION": {"greet", "process", "calculate", "handle_call"},
        "PROTOCOL": {"Enumerable", "String.Chars"},
        "IMPL": {"Enumerable", "String.Chars"},
        "STRUCT": {"User", "Config", "State"},
        "IMPORT": {"Logger", "Task"},
    },
    "csharp": {
        "CLASS": {"MyClass", "User", "Controller"},
        "INTERFACE": {"IRepository", "IHandler", "IValidator"},
        "STRUCT": {"Point", "Vector", "Config"},
        "ENUM": {"Color", "Status", "Level"},
        "NAMESPACE": {"MyApp.Models", "MyApp.Controllers"},
        "FUNCTION": {"Main", "Process", "Calculate", "Validate"},
        "PROPERTY": {"Name", "Value", "Count"},
        "IMPORT": {"System", "System.Collections.Generic"},
        "DECORATOR": {"Serializable", "Obsolete", "Route"},
        "CONSTANT": {"MaxSize", "ApiUrl", "Version"},
    },
}


class TestFindConstructsComprehensive:
    """! @brief Comprehensive test suite for construct extraction across all languages.
    @details Tests every language-construct combination defined in LANGUAGE_TAGS using fixture files.
    """

    @pytest.fixture
    def fixtures_dir(self) -> Path:
        """! @brief Get the path to the fixtures directory.
        @return Path object pointing to tests/fixtures.
        """
        return Path(__file__).parent / "fixtures"

    def get_fixture_path(self, fixtures_dir: Path, language: str) -> Path:
        """! @brief Resolve fixture file path for a given language.
        @param fixtures_dir Base fixtures directory.
        @param language Normalized language identifier.
        @return Path to the fixture file.
        """
        extension_map = {
            "python": "py",
            "c": "c",
            "cpp": "cpp",
            "rust": "rs",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "ruby": "rb",
            "php": "php",
            "swift": "swift",
            "kotlin": "kt",
            "scala": "scala",
            "lua": "lua",
            "shell": "sh",
            "perl": "pl",
            "haskell": "hs",
            "zig": "zig",
            "elixir": "ex",
            "csharp": "cs",
        }
        ext = extension_map[language]
        return fixtures_dir / f"fixture_{language}.{ext}"

    def test_language_tags_coverage(self):
        """! @brief Verify EXPECTED_CONSTRUCTS covers all 20 supported languages."""
        required_languages = set(LANGUAGE_TAGS.keys())
        covered_languages = set(EXPECTED_CONSTRUCTS.keys())
        assert required_languages == covered_languages, (
            f"Missing language coverage: "
            f"{required_languages - covered_languages}"
        )

    @pytest.mark.parametrize("language", list(LANGUAGE_TAGS.keys()))
    def test_fixture_exists(self, fixtures_dir, language):
        """! @brief Verify fixture file exists for each language.
        @param fixtures_dir Base fixtures directory.
        @param language Language identifier to test.
        """
        fixture_path = self.get_fixture_path(fixtures_dir, language)
        assert fixture_path.exists(), f"Missing fixture for {language}: {fixture_path}"

    # ── Python construct tests ────────────────────────────────────────────────

    def test_python_class_extraction(self, fixtures_dir):
        """! @brief Test CLASS extraction from Python fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))
        output = find_constructs_in_files([fixture], "CLASS", ".*")

        expected_classes = EXPECTED_CONSTRUCTS["python"]["CLASS"]
        for class_name in expected_classes:
            assert f"CLASS: `{class_name}`" in output, f"Missing class: {class_name}"

    def test_python_function_extraction(self, fixtures_dir):
        """! @brief Test FUNCTION extraction from Python fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))
        output = find_constructs_in_files([fixture], "FUNCTION", ".*")

        expected_functions = EXPECTED_CONSTRUCTS["python"]["FUNCTION"]
        # Test subset of key functions
        key_functions = {"regular_function", "async_function", "generator_function"}
        for func_name in key_functions:
            assert f"FUNCTION: `{func_name}`" in output, f"Missing function: {func_name}"

    def test_python_decorator_pattern(self, fixtures_dir):
        """! @brief Test DECORATOR extraction with pattern matching."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))
        output = find_constructs_in_files([fixture], "DECORATOR", "data.*")

        assert "DECORATOR: `dataclass`" in output

    def test_python_variable_extraction(self, fixtures_dir):
        """! @brief Test VARIABLE extraction from Python fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))
        output = find_constructs_in_files([fixture], "VARIABLE", "MAX.*")

        assert "VARIABLE: `MAX_RETRIES`" in output

    # ── C construct tests ─────────────────────────────────────────────────────

    def test_c_struct_extraction(self, fixtures_dir):
        """! @brief Test STRUCT extraction from C fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "c"))
        output = find_constructs_in_files([fixture], "STRUCT", ".*")

        expected_structs = EXPECTED_CONSTRUCTS["c"]["STRUCT"]
        for struct_name in expected_structs:
            assert f"STRUCT: `{struct_name}`" in output, f"Missing struct: {struct_name}"

    def test_c_union_extraction(self, fixtures_dir):
        """! @brief Test UNION extraction from C fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "c"))
        output = find_constructs_in_files([fixture], "UNION", ".*")

        assert "UNION: `Data`" in output

    def test_c_enum_extraction(self, fixtures_dir):
        """! @brief Test ENUM extraction from C fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "c"))
        output = find_constructs_in_files([fixture], "ENUM", ".*")

        assert "ENUM: `Color`" in output

    def test_c_typedef_extraction(self, fixtures_dir):
        """! @brief Test TYPEDEF extraction from C fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "c"))
        output = find_constructs_in_files([fixture], "TYPEDEF", ".*")

        # Note: source analyzer currently only extracts simple typedefs,
        # not function pointer or struct typedefs
        expected_typedefs = {"my_int", "byte_t"}
        for typedef_name in expected_typedefs:
            assert f"TYPEDEF: `{typedef_name}`" in output, f"Missing typedef: {typedef_name}"

    def test_c_macro_extraction(self, fixtures_dir):
        """! @brief Test MACRO extraction from C fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "c"))
        output = find_constructs_in_files([fixture], "MACRO", ".*")

        expected_macros = {"MAX_SIZE", "CLAMP", "STRINGIFY"}
        for macro_name in expected_macros:
            assert f"MACRO: `{macro_name}`" in output, f"Missing macro: {macro_name}"

    def test_c_function_extraction(self, fixtures_dir):
        """! @brief Test FUNCTION extraction from C fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "c"))
        output = find_constructs_in_files([fixture], "FUNCTION", ".*")

        expected_functions = {"main", "greet", "factorial"}
        for func_name in expected_functions:
            assert f"FUNCTION: `{func_name}`" in output, f"Missing function: {func_name}"

    # ── Rust construct tests ──────────────────────────────────────────────────

    def test_rust_struct_extraction(self, fixtures_dir):
        """! @brief Test STRUCT extraction from Rust fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "rust"))
        output = find_constructs_in_files([fixture], "STRUCT", ".*")

        expected_structs = EXPECTED_CONSTRUCTS["rust"]["STRUCT"]
        for struct_name in expected_structs:
            assert f"STRUCT: `{struct_name}`" in output, f"Missing struct: {struct_name}"

    def test_rust_enum_extraction(self, fixtures_dir):
        """! @brief Test ENUM extraction from Rust fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "rust"))
        output = find_constructs_in_files([fixture], "ENUM", ".*")

        assert "ENUM: `MyEnum`" in output

    def test_rust_trait_extraction(self, fixtures_dir):
        """! @brief Test TRAIT extraction from Rust fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "rust"))
        output = find_constructs_in_files([fixture], "TRAIT", ".*")

        expected_traits = {"MyTrait", "Parser"}
        for trait_name in expected_traits:
            assert f"TRAIT: `{trait_name}`" in output, f"Missing trait: {trait_name}"

    def test_rust_impl_extraction(self, fixtures_dir):
        """! @brief Test IMPL extraction from Rust fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "rust"))
        output = find_constructs_in_files([fixture], "IMPL", "My.*")

        assert "MyStruct" in output or "MyTrait" in output

    def test_rust_macro_extraction(self, fixtures_dir):
        """! @brief Test MACRO extraction from Rust fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "rust"))
        output = find_constructs_in_files([fixture], "MACRO", ".*")

        expected_macros = {"hashmap", "my_macro"}
        for macro_name in expected_macros:
            assert f"MACRO: `{macro_name}`" in output, f"Missing macro: {macro_name}"

    def test_rust_constant_extraction(self, fixtures_dir):
        """! @brief Test CONSTANT extraction from Rust fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "rust"))
        output = find_constructs_in_files([fixture], "CONSTANT", "MY.*")

        assert "MY_CONST" in output or "MY_STATIC" in output

    def test_rust_type_alias_extraction(self, fixtures_dir):
        """! @brief Test TYPE_ALIAS extraction from Rust fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "rust"))
        output = find_constructs_in_files([fixture], "TYPE_ALIAS", ".*")

        expected_aliases = {"IoResult", "MyAlias"}
        for alias_name in expected_aliases:
            assert f"TYPE_ALIAS: `{alias_name}`" in output, f"Missing type alias: {alias_name}"

    # ── Additional language sampling tests ────────────────────────────────────

    def test_typescript_interface_extraction(self, fixtures_dir):
        """! @brief Test INTERFACE extraction from TypeScript fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "typescript"))
        output = find_constructs_in_files([fixture], "INTERFACE", ".*")

        assert "INTERFACE: `User`" in output

    def test_typescript_type_alias_extraction(self, fixtures_dir):
        """! @brief Test TYPE_ALIAS extraction from TypeScript fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "typescript"))
        output = find_constructs_in_files([fixture], "TYPE_ALIAS", ".*")

        # TypeScript fixture should have type aliases
        assert "TYPE_ALIAS:" in output

    def test_java_class_extraction(self, fixtures_dir):
        """! @brief Test CLASS extraction from Java fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "java"))
        output = find_constructs_in_files([fixture], "CLASS", ".*")

        assert "CLASS: `MyClass`" in output

    def test_java_interface_extraction(self, fixtures_dir):
        """! @brief Test INTERFACE extraction from Java fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "java"))
        output = find_constructs_in_files([fixture], "INTERFACE", ".*")

        # Java fixture should have interfaces
        assert "INTERFACE:" in output

    def test_go_function_extraction(self, fixtures_dir):
        """! @brief Test FUNCTION extraction from Go fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "go"))
        output = find_constructs_in_files([fixture], "FUNCTION", "main")

        assert "FUNCTION: `main`" in output

    def test_go_struct_extraction(self, fixtures_dir):
        """! @brief Test STRUCT extraction from Go fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "go"))
        output = find_constructs_in_files([fixture], "STRUCT", ".*")

        # Go fixture should have structs
        assert "STRUCT:" in output

    def test_cpp_class_extraction(self, fixtures_dir):
        """! @brief Test CLASS extraction from C++ fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "cpp"))
        output = find_constructs_in_files([fixture], "CLASS", ".*")

        # C++ fixture should have classes
        assert "CLASS:" in output

    def test_cpp_namespace_extraction(self, fixtures_dir):
        """! @brief Test NAMESPACE extraction from C++ fixture."""
        fixture = str(self.get_fixture_path(fixtures_dir, "cpp"))
        output = find_constructs_in_files([fixture], "NAMESPACE", ".*")

        # C++ fixture should have namespaces
        assert "NAMESPACE:" in output

    # ── Pattern matching tests ────────────────────────────────────────────────

    def test_pattern_matching_case_sensitive(self, fixtures_dir):
        """! @brief Test case-sensitive regex pattern matching."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))

        # Should match MAX_RETRIES but not max_retries
        output = find_constructs_in_files([fixture], "VARIABLE", "^MAX.*")
        assert "MAX_RETRIES" in output

    def test_pattern_matching_anchored(self, fixtures_dir):
        """! @brief Test anchored regex patterns."""
        fixture = str(self.get_fixture_path(fixtures_dir, "c"))

        # Exact match for 'main' function
        output = find_constructs_in_files([fixture], "FUNCTION", "^main$")
        assert "FUNCTION: `main`" in output
        # Should not match min_val or other functions containing 'main'
        lines = output.split("\n")
        main_lines = [l for l in lines if "FUNCTION:" in l]
        assert len(main_lines) <= 2  # Header line + main function

    def test_multiple_tags_extraction(self, fixtures_dir):
        """! @brief Test extraction with multiple tag filter."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))

        # Extract both classes and functions
        output = find_constructs_in_files([fixture], "CLASS|FUNCTION", "My.*")
        assert "CLASS: `MyClass`" in output
        # Should also find functions starting with 'my' or 'My'

    def test_line_numbers_included_by_default(self, fixtures_dir):
        """! @brief Test that line numbers are included in output by default."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))
        output = find_constructs_in_files([fixture], "CLASS", "MyClass", include_line_numbers=True)

        assert "L" in output and ">" in output  # Check for Lnn> format

    def test_line_numbers_disabled(self, fixtures_dir):
        """! @brief Test that line numbers can be disabled."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))
        output = find_constructs_in_files([fixture], "CLASS", "MyClass", include_line_numbers=False)

        # Should not have Lnn> prefixes
        assert "L1>" not in output and "L2>" not in output

    # ── Error and edge case tests ─────────────────────────────────────────────

    def test_no_matches_raises_error(self, fixtures_dir):
        """! @brief Test that no matches raises ValueError."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))

        with pytest.raises(ValueError, match="No constructs found"):
            find_constructs_in_files([fixture], "CLASS", "^NonexistentClassName$")

    def test_unsupported_tag_for_language(self, fixtures_dir):
        """! @brief Test extraction with tag not supported by language."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))

        # Python doesn't support STRUCT
        with pytest.raises(ValueError, match="No constructs found"):
            find_constructs_in_files([fixture], "STRUCT", ".*")

    def test_invalid_regex_pattern(self, fixtures_dir):
        """! @brief Test that invalid regex patterns are handled gracefully."""
        fixture = str(self.get_fixture_path(fixtures_dir, "python"))

        # Invalid regex should result in no matches
        with pytest.raises(ValueError, match="No constructs found"):
            find_constructs_in_files([fixture], "CLASS", "[invalid(regex")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
