"""!@file
@brief Expose public package entrypoints for tomarkdown.
@details Re-exports version and CLI main callable for consumers importing
`tomarkdown` as a library entrypoint.
"""

from .version import __version__
from .core import main

#: @brief Declare public symbols exported by ``from tomarkdown import *``.
__all__ = ["__version__", "main"]
