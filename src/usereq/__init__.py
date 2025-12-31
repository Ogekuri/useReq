"""Package entry point for the useReq automation.

This file exposes light-weight package metadata and a convenience
re-export of the CLI entry `main` so callers can do
`from usereq import main` without importing the heavier package
behaviour unintentionally.
"""

__version__ = "0.0.3"

from .cli import main  # re-export the CLI entry point

__all__ = ["__version__", "main"]
