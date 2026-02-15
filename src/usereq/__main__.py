"""! @brief Allows execution of the tool as a module.
"""
from .cli import main
import sys


if __name__ == "__main__":
    sys.exit(main())
