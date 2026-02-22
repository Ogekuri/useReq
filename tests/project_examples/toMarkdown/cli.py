"""!@file
@brief Provide executable CLI wrapper.
@details Exposes a thin entry module delegating to ``tomarkdown.core.main``.
"""

from __future__ import annotations

from .core import main


if __name__ == "__main__":
    raise SystemExit(main())
