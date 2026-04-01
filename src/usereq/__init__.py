"""!
@file __init__.py
@brief Initialization module for the `usereq` package.
@details Exposes package metadata and lazily-resolved CLI entrypoints while avoiding eager
import of `usereq.cli` during package initialization.
@author GitHub Copilot
@version 0.0.70
"""

from __future__ import annotations

import importlib
from . import compress  # usereq.compress submodule
from . import compress_files  # usereq.compress_files submodule
from . import find_constructs  # usereq.find_constructs submodule
from . import generate_markdown  # usereq.generate_markdown submodule
from . import source_analyzer  # usereq.source_analyzer submodule
from . import token_counter  # usereq.token_counter submodule
from typing import Any

__version__ = "0.54.0"
"""! @brief Semantic version string of the package."""


def main(argv: list[str] | None = None) -> int:
    """!
    @brief Execute the package CLI entrypoint without eager module import side effects.
    @details Lazily imports `usereq.cli.main` on call to avoid pre-loading `usereq.cli`
    during package initialization, preventing runpy module-execution RuntimeWarning for
    `python -m usereq.cli`.
    @param argv {list[str] | None} Optional CLI arguments list forwarded to `usereq.cli.main`.
    @return {int} CLI process exit code produced by `usereq.cli.main`.
    @satisfies SRS-056
    """

    from .cli import main as cli_main

    return cli_main(argv)


def __getattr__(name: str) -> Any:
    """!
    @brief Lazily resolve deferred public package attributes.
    @details Resolves `cli` on first access to preserve backward-compatible attribute
    access (`usereq.cli`) while keeping package initialization free from eager CLI import.
    @param name {str} Requested attribute name.
    @return {Any} Resolved attribute object.
    @throws {AttributeError} Raised when the attribute is not a supported deferred symbol.
    @satisfies SRS-056
    """

    if name == "cli":
        return importlib.import_module(f"{__name__}.cli")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__", "main", "cli",
    "source_analyzer", "token_counter", "generate_markdown",
    "compress", "compress_files", "find_constructs",
]
"""! @brief List of public symbols exported by the package."""
