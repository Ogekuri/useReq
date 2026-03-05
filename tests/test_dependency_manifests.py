"""@brief Validate repository dependency manifest invariants.
@details Enforces alignment between requirements.txt and packaging metadata plus req.sh invocation semantics for .venv execution behavior.
@satisfies SRS-055
@satisfies SRS-056
@satisfies SRS-264
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REQ_SCRIPT_PATH = REPO_ROOT / "scripts" / "req.sh"
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
    assert "exec \"${VENVDIR}/bin/python3\"" in content
    assert 'raise SystemExit(main())' in content
    assert "\"$@\"" in content
    assert "REQ_HASH_FILE=" not in content
    assert "sha256sum" not in content
