"""! @brief Package entry point for useReq automation.
@details This file exposes lightweight metadata and a convenient re-export of the `main` CLI entry point, so callers can use `from usereq import main` without unintentionally importing the full package behavior.
"""

__version__ = "0.0.69"
"""The current version of the package."""

from . import cli  # usereq.cli submodule
from . import pdoc_utils  # usereq.pdoc_utils submodule
from . import source_analyzer  # usereq.source_analyzer submodule
from . import token_counter  # usereq.token_counter submodule
from . import generate_markdown  # usereq.generate_markdown submodule
from . import compress  # usereq.compress submodule
from . import compress_files  # usereq.compress_files submodule
from . import find_constructs  # usereq.find_constructs submodule
from .cli import main  # re-export of CLI entry point

__all__ = [
    "__version__", "main", "cli", "pdoc_utils",
    "source_analyzer", "token_counter", "generate_markdown",
    "compress", "compress_files", "find_constructs",
]
"""! @brief Public package exports for CLI entrypoint and utility submodules."""
