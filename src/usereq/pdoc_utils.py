"""!
@file pdoc_utils.py
@brief Utilities for generating pdoc documentation.
@details Wraps pdoc execution to generate HTML documentation for the project modules.
@author GitHub Copilot
@version 0.0.70
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence


def _normalize_modules(modules: str | Iterable[str]) -> list[str]:
    """! @brief Returns a list of modules from either a string or an iterable.
    @param modules A single module name string or an iterable of strings.
    @return List of module names.
    """
    if isinstance(modules, str):
        return [modules]
    return list(modules)


def _run_pdoc(command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess:
    """! @brief Runs pdoc and captures output for error handling.
    @param command The command list to execute.
    @param env Environment variables dictionary.
    @param cwd Working directory path.
    @return CompletedProcess object containing execution results.
    @details Executes pdoc as a subprocess with captured output (stdout/stderr).
    """
    return subprocess.run(
        command,
        check=False,
        env=env,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def generate_pdoc_docs(
    output_dir: Path,
    modules: Sequence[str] | str = ("usereq",),
    *,
    all_submodules: bool = True,
) -> None:
    """! @brief Generates or updates pdoc documentation in the target output directory.
    @param output_dir Directory where HTML documentation will be written.
    @param modules Importable modules or packages to document.
    @param all_submodules When True, recurse into submodules even if not exported via __all__.
    @throws RuntimeError If pdoc generation fails.
    @details Sets up PYTHONPATH to include `src` and executes pdoc via `sys.executable`. Handles fallback if `--all-submodules` is not supported by the installed pdoc version.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]
    source_root = repo_root / "src"

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    paths = [str(source_root)]
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(paths)

    targets = _normalize_modules(modules)
    command: list[str] = [
        sys.executable,
        "-m",
        "pdoc",
    ]
    if all_submodules:
        command.append("--all-submodules")
    command.extend(
        [
            "--output-dir",
            str(output_dir),
        ]
    )
    command.extend(targets)

    result = _run_pdoc(command, env=env, cwd=repo_root)

    # Fallback for pdoc versions that do not support --all-submodules.
    if result.returncode != 0 and all_submodules:
        stderr = (result.stderr or "").lower()
        if "unrecognized arguments" in stderr and "--all-submodules" in stderr:
            command = [c for c in command if c != "--all-submodules"]
            result = _run_pdoc(command, env=env, cwd=repo_root)

    if result.returncode != 0:
        msg = result.stderr.strip() if result.stderr else ""
        raise RuntimeError(f"pdoc documentation generation failed: {msg}")
