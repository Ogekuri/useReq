"""Package entry point for useReq automation.

This file exposes lightweight metadata and a convenient re-export of the `main` CLI entry point,
so callers can use `from usereq import main` without unintentionally importing
the full package behavior.
"""

__version__ = "0.0.54"
"""The current version of the package."""

from . import cli  # usereq.cli submodule
from . import pdoc_utils  # usereq.pdoc_utils submodule
from .cli import main  # re-export of CLI entry point

__all__ = ["__version__", "main", "cli", "pdoc_utils"]
