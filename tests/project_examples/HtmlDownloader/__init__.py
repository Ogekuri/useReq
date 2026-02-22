"""
@file __init__.py
@brief HtmlDownloader package entry module.
@details Exposes package-level symbols used by CLI entrypoints and version reporting.
@module_symbols functions=0 classes=0 variables=1
@variables __all__
"""

from .version import __version__

from .cli import main

#: @var __all__ @brief Module-level variable `__all__`.
__all__ = ["__version__", "main"]
