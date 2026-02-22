"""
@file __main__.py
@brief HtmlDownloader package entry module.
@details Exposes package-level symbols used by CLI entrypoints and version reporting.
@module_symbols functions=0 classes=0 variables=0
"""
from .cli import main
import sys


if __name__ == "__main__":
    sys.exit(main())
