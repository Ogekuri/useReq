"""!@file
@brief Provide module execution entrypoint.
@details Delegates process execution to ``tomarkdown.cli.main`` when invoked
with ``python -m tomarkdown``.
"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
