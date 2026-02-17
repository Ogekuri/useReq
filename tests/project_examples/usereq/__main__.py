"""!
@file __main__.py
@brief Package entry point for execution as a module.
@details Enables running the package via `python -m usereq`. Delegates execution to the CLI main function.
@author GitHub Copilot
@version 0.0.70
"""
from .cli import main
import sys


if __name__ == "__main__":
    """!
    @brief Entry point check.
    @details Executes `main()` and exits with the returned status code when run as a script.
    """
    sys.exit(main())
