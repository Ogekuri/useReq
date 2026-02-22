## @file __init__.py
# @brief Expose package-level metadata and public CLI entrypoint symbols.
# @details Defines stable module exports for downstream imports and runtime version checks.

## @brief Store semantic version string for package metadata.
# @details Used by CLI usage/version output and by release automation checks.
__version__ = "0.4.0"

from .core import main  # noqa: F401

## @brief Enumerate public symbols exported by package root.
# @details Constrains wildcard-import surface to the version constant and CLI main callable.
__all__ = ["__version__", "main"]
