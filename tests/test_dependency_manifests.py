"""@brief Validate repository dependency manifest invariants.
@details Enforces alignment between uv.lock and packaging metadata plus req.sh invocation semantics for uv-based execution behavior. Includes package-data coverage validation for resource subdirectories.
@satisfies SRS-055
@satisfies SRS-056
@satisfies SRS-342
@satisfies SRS-264
@satisfies SRS-272
@satisfies SRS-273
@satisfies SRS-274
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
UV_LOCK_PATH = REPO_ROOT / "uv.lock"
GITIGNORE_PATH = REPO_ROOT / ".gitignore"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REQ_SCRIPT_PATH = REPO_ROOT / "scripts" / "req.sh"
README_PATH = REPO_ROOT / "README.md"
RESOURCES_DIR = REPO_ROOT / "src" / "usereq" / "resources"
REQUIRED_OPERATIONAL_RESOURCE_SUBDIRS = {
    "common",
    "prompts",
    "guidelines",
    "docs",
    "vscode",
}


def _normalize_requirement_name(requirement: str) -> str:
    """@brief Extract canonical package name token from requirement entry.
    @details Uses a deterministic regex to capture the leading PEP 508 package token and normalizes underscores to hyphens.
    @param requirement {str} Raw requirement/specifier entry from pyproject lists or uv.lock package names.
    @return {str} Normalized package name in lowercase.
    @throws {ValueError} Raised when the entry cannot be parsed into a package token.
    """

    match = re.match(r"^\s*([A-Za-z0-9_.-]+)", requirement)
    if match is None:
        raise ValueError(f"Cannot parse requirement entry: {requirement!r}")
    return match.group(1).replace("_", "-").lower()


def _read_uv_lock_packages() -> set[str]:
    """@brief Parse uv.lock into a normalized package-name set.
    @details Reads the lockfile TOML and collects every `[[package]].name` token
    after deterministic normalization for set-level checks against pyproject declarations.
    @return {set[str]} Distinct normalized package names declared in uv.lock.
    """

    lock_data = tomllib.loads(UV_LOCK_PATH.read_text(encoding="utf-8"))
    package_entries = lock_data.get("package", [])
    assert isinstance(package_entries, list), "uv.lock must define a [[package]] list"
    package_names = {
        _normalize_requirement_name(entry["name"])
        for entry in package_entries
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    assert package_names, "uv.lock must define at least one package name"
    return package_names


def test_repository_uses_uv_lock_and_omits_requirements_txt() -> None:
    """@brief Assert repository dependency-manifest policy uses uv.lock only.
    @details Ensures uv.lock exists as canonical lockfile and root requirements.txt
    is absent from tracked project files.
    @return {None} No return value.
    @satisfies SRS-055
    """

    assert UV_LOCK_PATH.exists(), "uv.lock must exist at repository root"
    assert not REQUIREMENTS_PATH.exists(), "requirements.txt must not exist at repository root"


def test_gitignore_unignores_uv_lock_and_not_requirements_txt() -> None:
    """@brief Assert .gitignore tracks uv.lock and no longer unignores requirements.txt.
    @details Validates root .gitignore contains `!uv.lock` and excludes obsolete
    `!requirements.txt` unignore rule to keep lockfile tracking policy deterministic.
    @return {None} No return value.
    @satisfies SRS-055
    """

    content = GITIGNORE_PATH.read_text(encoding="utf-8")
    assert "!uv.lock" in content, ".gitignore must include !uv.lock unignore rule"
    assert (
        "!requirements.txt" not in content
    ), ".gitignore must not include !requirements.txt unignore rule"


def test_pyproject_dependencies_are_present_in_uv_lock() -> None:
    """@brief Verify pyproject dependency declarations are present in uv.lock.
    @details Compares project.dependencies after normalization against uv.lock
    package names. Runtime declarations MUST be represented by locked packages.
    Build-system requirements are validated independently of lock membership.
    @return {None} No return value.
    @satisfies SRS-264
    """

    pyproject_data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    project_dependencies = pyproject_data["project"]["dependencies"]
    pyproject_packages = {
        _normalize_requirement_name(entry)
        for entry in project_dependencies
    }
    uv_lock_packages = _read_uv_lock_packages()
    assert pyproject_packages <= uv_lock_packages, (
        f"pyproject.toml declares packages not represented in uv.lock: "
        f"{sorted(pyproject_packages - uv_lock_packages)}"
    )


def test_pyproject_dependencies_include_ruff_and_pyright() -> None:
    """@brief Verify pyproject.toml project.dependencies includes ruff and pyright.
    @details Ensures static-analysis tools are declared as runtime dependencies
    so they are installed with the package, enabling internal module-based invocation
    via sys.executable without requiring external PATH availability.
    @return {None} No return value.
    @satisfies SRS-338, SRS-340
    """

    pyproject_data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    project_dependencies = pyproject_data["project"]["dependencies"]
    normalized_deps = {
        _normalize_requirement_name(entry)
        for entry in project_dependencies
    }
    required_static_tools = {"ruff", "pyright"}
    missing = required_static_tools - normalized_deps
    assert not missing, (
        f"pyproject.toml [project].dependencies missing static-analysis tools: "
        f"{sorted(missing)}. Required: {sorted(required_static_tools)}"
    )


def test_req_sh_executes_cli_with_uv_run() -> None:
    """@brief Validate req.sh executes CLI through uv-managed runtime without virtualenv bootstrap.
    @details Confirms req.sh forwards CLI arguments unchanged through `uv run`,
    executes `python -m usereq.cli`, and does not create or activate `.venv` manually.
    @return {None} No return value.
    """

    content = REQ_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "exec uv run" in content
    assert "python -m usereq.cli" in content
    assert '"$@"' in content
    assert "virtualenv" not in content
    assert "pip install -r" not in content
    assert "/bin/activate" not in content
    assert "${VENVDIR}/bin/python3" not in content
    assert "REQ_HASH_FILE=" not in content
    assert "sha256sum" not in content


def test_req_sh_preserves_invocation_cwd_for_here_commands(tmp_path: Path) -> None:
    """@brief Verify req.sh does not force CLI here-mode commands to repository root.
    @details Executes req.sh from an isolated directory without `.req/config.json`
    and calls `--git-check`; expected behavior is failure in caller context with
    missing-config diagnostic from here-only command execution.
    @param tmp_path {Path} Pytest-provided isolated temporary directory.
    @return {None} No return value.
    @satisfies SRS-056
    @satisfies SRS-311
    """

    target_cwd = tmp_path / "external-project"
    target_cwd.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(REQ_SCRIPT_PATH), "--git-check"],
        cwd=target_cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert ".req/config.json not found in the project root" in result.stderr


def test_python_module_cli_entrypoint_emits_no_runpy_runtimewarning() -> None:
    """@brief Verify module-mode CLI execution does not emit runpy pre-import warning.
    @details Executes `python -m usereq.cli --ver` under repository PYTHONPATH and
    asserts stderr does not contain the known runpy RuntimeWarning emitted when
    `usereq.cli` is imported by package initialization before module execution.
    @return {None} No return value.
    @satisfies SRS-056
    """

    existing_pythonpath = os.environ.get("PYTHONPATH")
    composed_pythonpath = str(REPO_ROOT / "src")
    if existing_pythonpath:
        composed_pythonpath = f"{composed_pythonpath}:{existing_pythonpath}"
    env = {**os.environ, "PYTHONPATH": composed_pythonpath}
    result = subprocess.run(
        [sys.executable, "-m", "usereq.cli", "--ver"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "RuntimeWarning" not in result.stderr, result.stderr
    assert "usereq.cli" not in result.stderr, result.stderr


def test_python_module_cli_executes_main_for_ver_flag() -> None:
    """@brief Verify `python -m usereq.cli` executes CLI main for version requests.
    @details Executes module mode with `--ver` and asserts version text is printed
    on stdout, proving module execution invokes `main()` rather than importing only.
    @return {None} No return value.
    @satisfies SRS-056
    """

    existing_pythonpath = os.environ.get("PYTHONPATH")
    composed_pythonpath = str(REPO_ROOT / "src")
    if existing_pythonpath:
        composed_pythonpath = f"{composed_pythonpath}:{existing_pythonpath}"
    env = {**os.environ, "PYTHONPATH": composed_pythonpath}
    result = subprocess.run(
        [sys.executable, "-m", "usereq.cli", "--ver"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "Expected version output on stdout for --ver"


def test_readme_includes_requirements_section_with_uv_tool() -> None:
    """@brief Validate README declares Astral uv tool requirement in a dedicated Requirements section.
    @details Confirms README includes the `## Requirements` heading and explicitly states Astral `uv` tool is required.
    @return {None} No return value.
    @satisfies SRS-342
    """

    content = README_PATH.read_text(encoding="utf-8")
    assert "## Requirements" in content
    assert "Astral `uv` tool is required" in content


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


def test_package_data_covers_required_operational_resource_subdirectories() -> None:
    """@brief Assert package-data patterns reference required operational resource subdirectories.
    @details Extracts directory prefixes from package-data glob patterns and verifies coverage of the fixed
    operational subdirectory set required for runtime behavior and packaging.
    @return {None} No return value.
    @satisfies SRS-272, SRS-274
    """

    patterns = _get_package_data_patterns()
    covered_dirs: set[str] = set()
    for pattern in patterns:
        parts = pattern.split("/")
        if len(parts) >= 2 and parts[0] == "resources":
            covered_dirs.add(parts[1])

    missing = REQUIRED_OPERATIONAL_RESOURCE_SUBDIRS - covered_dirs
    assert not missing, (
        "Required operational resource subdirectories not covered by package-data: "
        f"{sorted(missing)}. Required: {sorted(REQUIRED_OPERATIONAL_RESOURCE_SUBDIRS)}, "
        f"Covered: {sorted(covered_dirs)}"
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


def test_pyproject_does_not_define_unsupported_uv_forms_section() -> None:
    """@brief Ensure pyproject.toml does not declare unsupported uv settings keys.
    @details Guards req.sh uv-managed execution from settings-discovery warnings by
    forbidding the deprecated `[tool.uv.forms.*]` subtree in pyproject metadata.
    @return {None} No return value.
    @satisfies SRS-056
    """

    pyproject_data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    uv_settings = pyproject_data.get("tool", {}).get("uv", {})
    assert "forms" not in uv_settings, (
        "pyproject.toml MUST NOT define [tool.uv.forms.*] because current uv "
        "settings schema rejects `forms` and emits runtime warnings."
    )
