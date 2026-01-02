"""Consente l'esecuzione dello strumento come modulo."""
from .cli import main
import sys


if __name__ == "__main__":
    sys.exit(main())
