"""!
@file __init__.py
@brief Initialization module for the `usereq` package.
@details Exposes the package version, main entry point, and key submodules. Designed to be lightweight.
@author GitHub Copilot
@version 0.0.70
"""

from . import cli  # usereq.cli submodule
from . import source_analyzer  # usereq.source_analyzer submodule
from . import token_counter  # usereq.token_counter submodule
from . import generate_markdown  # usereq.generate_markdown submodule
from . import compress  # usereq.compress submodule
from . import compress_files  # usereq.compress_files submodule
from . import find_constructs  # usereq.find_constructs submodule
from .cli import main  # re-export of CLI entry point

__version__ = "0.0.72"
"""! @brief Semantic version string of the package."""

__all__ = [
    "__version__", "main", "cli",
    "source_analyzer", "token_counter", "generate_markdown",
    "compress", "compress_files", "find_constructs",
]
"""! @brief List of public symbols exported by the package."""
