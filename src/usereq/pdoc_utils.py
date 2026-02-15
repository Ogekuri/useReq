"""! @brief Utilities for generating pdoc documentation.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence


def _normalize_modules(modules: str | Iterable[str]) -> list[str]:
    """! @brief Returns a list of modules from either a string or an iterable.
    """
    if isinstance(modules, str):
        return [modules]
    return list(modules)


def _run_pdoc(command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess:
    """! @brief Runs pdoc and captures output for error handling.
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
    @details Args: output_dir: Directory where HTML documentation will be written. modules: Importable modules or packages to document. all_submodules: When True, recurse into submodules even if not exported via __all__.
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
