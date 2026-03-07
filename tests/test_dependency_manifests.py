"""@brief Validate repository dependency manifest invariants.
@details Enforces alignment between requirements.txt and packaging metadata plus req.sh invocation semantics for .venv execution behavior. Includes package-data coverage validation for resource subdirectories.
@satisfies SRS-055
@satisfies SRS-056
@satisfies SRS-264
@satisfies SRS-272
@satisfies SRS-273
@satisfies SRS-274
"""

from __future__ import annotations

import fnmatch
import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REQ_SCRIPT_PATH = REPO_ROOT / "scripts" / "req.sh"
RESOURCES_DIR = REPO_ROOT / "src" / "usereq" / "resources"
RUNTIME_BUILD_PACKAGES = {"build", "setuptools", "wheel", "tiktoken", "pyyaml"}


def _normalize_requirement_name(requirement: str) -> str:
    """@brief Extract canonical package name token from requirement entry.
    @details Uses a deterministic regex to capture the leading PEP 508 package token and normalizes underscores to hyphens.
    @param requirement {str} Raw requirement/specifier entry from requirements.txt or pyproject lists.
    @return {str} Normalized package name in lowercase.
    @throws {ValueError} Raised when the entry cannot be parsed into a package token.
    """

    match = re.match(r"^\s*([A-Za-z0-9_.-]+)", requirement)
    if match is None:
        raise ValueError(f"Cannot parse requirement entry: {requirement!r}")
    return match.group(1).replace("_", "-").lower()


def _read_requirements_packages() -> set[str]:
    """@brief Parse requirements.txt into normalized package set.
    @details Drops blank/comment lines and normalizes each requirement token for set-level equality checks against pyproject dependency declarations.
    @return {set[str]} Distinct normalized package names declared in requirements.txt.
    """

    lines = REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines()
    return {
        _normalize_requirement_name(line)
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_requirements_contains_only_runtime_build_packages() -> None:
    """@brief Assert requirements.txt matches allowed runtime/build dependency set.
    @details Prevents drift to test/lint-only packages and enforces exact package set required for application execution and build operations.
    @return {None} No return value.
    """

    assert _read_requirements_packages() == RUNTIME_BUILD_PACKAGES


def test_pyproject_dependencies_are_aligned_with_requirements() -> None:
    """@brief Verify pyproject dependency declarations mirror requirements.txt.
    @details Compares requirements.txt package names with union(build-system.requires, project.dependencies) after normalization to enforce exact manifest alignment.
    @return {None} No return value.
    """

    pyproject_data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    build_requires = pyproject_data["build-system"]["requires"]
    project_dependencies = pyproject_data["project"]["dependencies"]
    pyproject_packages = {
        _normalize_requirement_name(entry)
        for entry in [*build_requires, *project_dependencies]
    }
    assert pyproject_packages == _read_requirements_packages()


def test_req_sh_executes_cli_with_venv_python() -> None:
    """@brief Validate req.sh executes CLI through .venv Python without hash-refresh logic.
    @details Confirms req.sh forwards CLI arguments unchanged to the .venv Python entrypoint and does not contain requirements-hash synchronization behavior.
    @return {None} No return value.
    """

    content = REQ_SCRIPT_PATH.read_text(encoding="utf-8")
    assert 'exec "${VENVDIR}/bin/python3"' in content
    assert "raise SystemExit(main())" in content
    assert '"$@"' in content
    assert "REQ_HASH_FILE=" not in content
    assert "sha256sum" not in content


def _get_package_data_patterns() -> list[str]:
    """@brief Extract package-data glob patterns from pyproject.toml for usereq.
    @details Reads [tool.setuptools.package-data].usereq and returns the declared patterns list.
    @return {list[str]} List of glob pattern strings declared as package data.
    """

    pyproject_data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return pyproject_data["tool"]["setuptools"]["package-data"]["usereq"]


def _get_existing_resource_subdirs() -> set[str]:
    """@brief Enumerate actual resource subdirectories under src/usereq/resources/.
    @details Scans the filesystem for immediate child directories, excluding hidden directories (starting with dot).
    @return {set[str]} Set of subdirectory names present under resources/.
    """

    return {
        entry.name
        for entry in RESOURCES_DIR.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    }


def test_package_data_covers_all_resource_subdirectories() -> None:
    """@brief Assert package-data patterns reference every existing resource subdirectory.
    @details Extracts directory prefixes from each package-data glob pattern and verifies that every actual
    subdirectory under src/usereq/resources/ has at least one corresponding pattern. Prevents resource
    directories from being silently excluded from built distributions.
    @return {None} No return value.
    @satisfies SRS-272, SRS-274
    """

    patterns = _get_package_data_patterns()
    covered_dirs: set[str] = set()
    for pattern in patterns:
        parts = pattern.split("/")
        if len(parts) >= 2 and parts[0] == "resources":
            covered_dirs.add(parts[1])

    existing_dirs = _get_existing_resource_subdirs()
    missing = existing_dirs - covered_dirs
    assert not missing, (
        f"Resource subdirectories not covered by package-data: {sorted(missing)}. "
        f"Existing: {sorted(existing_dirs)}, Covered: {sorted(covered_dirs)}"
    )


def test_package_data_patterns_reference_existing_directories() -> None:
    """@brief Assert package-data patterns do not reference non-existent resource directories.
    @details Validates that every directory prefix extracted from package-data glob patterns corresponds
    to an actual directory under src/usereq/resources/. Prevents build warnings from stale patterns.
    @return {None} No return value.
    @satisfies SRS-273
    """

    patterns = _get_package_data_patterns()
    existing_dirs = _get_existing_resource_subdirs()
    referenced_dirs: set[str] = set()
    for pattern in patterns:
        parts = pattern.split("/")
        if len(parts) >= 2 and parts[0] == "resources":
            referenced_dirs.add(parts[1])

    nonexistent = referenced_dirs - existing_dirs
    assert not nonexistent, (
        f"Package-data references non-existent resource directories: {sorted(nonexistent)}. "
        f"Existing: {sorted(existing_dirs)}"
    )


def test_package_data_matches_actual_resource_files() -> None:
    """@brief Assert every non-hidden file under resources/ is matched by at least one package-data pattern.
    @details Iterates all regular files under src/usereq/resources/ (excluding hidden files) and verifies
    each file's relative path matches at least one declared pattern in package-data. Ensures no operational
    resource file is silently excluded from the distribution.
    @return {None} No return value.
    @satisfies SRS-274
    """

    patterns = _get_package_data_patterns()
    all_resource_files: list[Path] = []
    for child in RESOURCES_DIR.rglob("*"):
        if child.is_file() and not any(
            p.startswith(".") for p in child.relative_to(RESOURCES_DIR).parts
        ):
            all_resource_files.append(child)

    assert all_resource_files, "No resource files found under src/usereq/resources/"

    unmatched: list[str] = []
    for resource_file in all_resource_files:
        rel_path = str(resource_file.relative_to(RESOURCES_DIR.parent))
        matched = any(fnmatch.fnmatch(rel_path, pat) for pat in patterns)
        if not matched:
            unmatched.append(rel_path)

    assert not unmatched, (
        f"Resource files not matched by any package-data pattern: {sorted(unmatched)}"
    )
