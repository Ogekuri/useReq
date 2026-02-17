#!/usr/bin/env python3
"""!
@file source_analyzer.py
@brief Multi-language source code analyzer.
@details Inspired by tree-sitter, this module analyzes source files across multiple programming languages, extracting: - Definitions of functions, methods, classes, structs, enums, traits, interfaces, modules, components and other constructs - Comments (single-line and multi-line) in language-specific syntax - A structured listing of the entire file with line number prefixes
@author GitHub Copilot
@version 0.0.70
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

try:
    from .doxygen_parser import parse_doxygen_comment
except ImportError:
    from doxygen_parser import parse_doxygen_comment


class ElementType(Enum):
    """! @brief Element types recognized in source code.
    @details Enumeration of all supported syntactic constructs across languages.
    """
    FUNCTION = auto()
    METHOD = auto()
    CLASS = auto()
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    INTERFACE = auto()
    MODULE = auto()
    IMPL = auto()
    MACRO = auto()
    CONSTANT = auto()
    VARIABLE = auto()
    TYPE_ALIAS = auto()
    IMPORT = auto()
    DECORATOR = auto()
    COMMENT_SINGLE = auto()
    COMMENT_MULTI = auto()
    COMPONENT = auto()
    PROTOCOL = auto()
    EXTENSION = auto()
    UNION = auto()
    NAMESPACE = auto()
    PROPERTY = auto()
    SIGNAL = auto()
    TYPEDEF = auto()


@dataclass
class SourceElement:
    """! @brief Element found in source file.
    @details Data class representing a single extracted code construct with its metadata.
    """
    element_type: ElementType
    line_start: int
    line_end: int
    extract: str
    name: Optional[str] = None
    signature: Optional[str] = None
    visibility: Optional[str] = None
    parent_name: Optional[str] = None
    inherits: Optional[str] = None
    depth: int = 0
    body_comments: list = field(default_factory=list)
    exit_points: list = field(default_factory=list)
    doxygen_fields: dict = field(default_factory=dict)

    @property
    def type_label(self) -> str:
        """! @brief Return the normalized printable label for element_type.
        @return Stable uppercase label used in markdown rendering output.
        @details Maps internal ElementType enum to a string representation for reporting.
        """
        labels = {
            ElementType.FUNCTION: "FUNCTION",
            ElementType.METHOD: "METHOD",
            ElementType.CLASS: "CLASS",
            ElementType.STRUCT: "STRUCT",
            ElementType.ENUM: "ENUM",
            ElementType.TRAIT: "TRAIT",
            ElementType.INTERFACE: "INTERFACE",
            ElementType.MODULE: "MODULE",
            ElementType.IMPL: "IMPL",
            ElementType.MACRO: "MACRO",
            ElementType.CONSTANT: "CONSTANT",
            ElementType.VARIABLE: "VARIABLE",
            ElementType.TYPE_ALIAS: "TYPE_ALIAS",
            ElementType.IMPORT: "IMPORT",
            ElementType.DECORATOR: "DECORATOR",
            ElementType.COMMENT_SINGLE: "COMMENT",
            ElementType.COMMENT_MULTI: "COMMENT",
            ElementType.COMPONENT: "COMPONENT",
            ElementType.PROTOCOL: "PROTOCOL",
            ElementType.EXTENSION: "EXTENSION",
            ElementType.UNION: "UNION",
            ElementType.NAMESPACE: "NAMESPACE",
            ElementType.PROPERTY: "PROPERTY",
            ElementType.SIGNAL: "SIGNAL",
            ElementType.TYPEDEF: "TYPEDEF",
        }
        return labels.get(self.element_type, "UNKNOWN")


@dataclass
class LanguageSpec:
    """! @brief Language recognition pattern specification.
    @details Holds regex patterns and configuration for parsing a specific programming language.
    """
    name: str
    single_comment: Optional[str] = None
    multi_comment_start: Optional[str] = None
    multi_comment_end: Optional[str] = None
    string_delimiters: tuple = ("\"", "'")
    patterns: list = field(default_factory=list)


def build_language_specs() -> dict:
    """! @brief Build specifications for all supported languages.
    """
    specs = {}

    # ── Python ──────────────────────────────────────────────────────────
    specs["python"] = LanguageSpec(
        name="Python",
        single_comment="#",
        multi_comment_start='"""',
        multi_comment_end='"""',
        string_delimiters=("\"", "'", '"""', "'''"),
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*class\s+(\w+)\s*[\(:])")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:async\s+)?def\s+(\w+)\s*\()")),
            (ElementType.DECORATOR, re.compile(
                r"^(\s*@(\w[\w.]*)\s*)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*(?:from\s+\S+\s+)?import\s+(.+))")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*([A-Z][A-Z_0-9]+)\s*=\s*)")),
        ],
    )

    # ── C ───────────────────────────────────────────────────────────────
    specs["c"] = LanguageSpec(
        name="C",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.STRUCT, re.compile(
                r"^(\s*(?:typedef\s+)?struct\s+(\w+))")),
            (ElementType.UNION, re.compile(
                r"^(\s*(?:typedef\s+)?union\s+(\w+))")),
            (ElementType.ENUM, re.compile(
                r"^(\s*(?:typedef\s+)?enum\s+(\w+))")),
            (ElementType.TYPEDEF, re.compile(
                r"^(\s*typedef\s+.+?\s+(\w+)\s*;)")),
            (ElementType.MACRO, re.compile(
                r"^(\s*#\s*define\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:static\s+|inline\s+|extern\s+|const\s+)*"
                r"(?:(?:unsigned|signed|long|short|volatile|register)\s+)*"
                r"(?:void|int|char|float|double|long|short|unsigned|signed|"
                r"size_t|ssize_t|uint\d+_t|int\d+_t|bool|_Bool|FILE|"
                r"\w+_t|\w+)\s*\**\s+"
                r"(\w+)\s*\()")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*#\s*include\s+(.+))")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*(?:static\s+|extern\s+|const\s+)*"
                r"(?:const\s+)?(?:char|int|float|double|void|long|short|unsigned|signed|"
                r"size_t|bool|_Bool|\w+_t)\s*\**\s+"
                r"(\w+)\s*(?:=|;|\[))")),
        ],
    )

    # ── C++ ─────────────────────────────────────────────────────────────
    specs["cpp"] = LanguageSpec(
        name="C++",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:template\s*<[^>]*>\s*)?class\s+(\w+))")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*(?:template\s*<[^>]*>\s*)?struct\s+(\w+))")),
            (ElementType.ENUM, re.compile(
                r"^(\s*enum\s+(?:class\s+)?(\w+))")),
            (ElementType.NAMESPACE, re.compile(
                r"^(\s*namespace\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:static\s+|inline\s+|virtual\s+|explicit\s+|"
                r"constexpr\s+|consteval\s+|constinit\s+|extern\s+|const\s+)*"
                r"(?:auto|void|int|char|float|double|long|short|unsigned|signed|"
                r"bool|string|wstring|size_t|\w+(?:::\w+)*)\s*[&*]*\s*"
                r"(\w+(?:::\w+)*)\s*\()")),
            (ElementType.MACRO, re.compile(
                r"^(\s*#\s*define\s+(\w+))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*#\s*include\s+(.+))")),
            (ElementType.TYPE_ALIAS, re.compile(
                r"^(\s*(?:using|typedef)\s+(\w+))")),
        ],
    )

    # ── Rust ────────────────────────────────────────────────────────────
    specs["rust"] = LanguageSpec(
        name="Rust",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+\"C\"\s+)?fn\s+(\w+))")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?struct\s+(\w+))")),
            (ElementType.ENUM, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?enum\s+(\w+))")),
            (ElementType.TRAIT, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?(?:unsafe\s+)?trait\s+(\w+))")),
            (ElementType.IMPL, re.compile(
                r"^(\s*impl(?:<[^>]*>)?\s+(?:(\w+(?:<[^>]*>)?)\s+for\s+)?(\w+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?mod\s+(\w+))")),
            (ElementType.MACRO, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?macro_rules!\s+(\w+))")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?(?:const|static)\s+(\w+))")),
            (ElementType.TYPE_ALIAS, re.compile(
                r"^(\s*(?:pub(?:\(\w+\))?\s+)?type\s+(\w+))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*use\s+(.+?);)")),
            (ElementType.DECORATOR, re.compile(
                r"^(\s*#\[(\w[^\]]*)\])")),
        ],
    )

    # ── JavaScript ──────────────────────────────────────────────────────
    specs["javascript"] = LanguageSpec(
        name="JavaScript",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        string_delimiters=("\"", "'", "`"),
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:export\s+)?(?:default\s+)?class\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s+(\w+)\s*\()")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?"
                r"(?:function|\([^)]*\)\s*=>|[a-zA-Z_]\w*\s*=>))")),
            (ElementType.COMPONENT, re.compile(
                r"^(\s*(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+(\w+)\s*=\s*"
                r"(?:React\.)?(?:memo|forwardRef|lazy)\s*\()")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:export\s+)?const\s+([A-Z][A-Z_0-9]+)\s*=)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(.+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+(\w+)\s*=\s*"
                r"require\s*\()")),
        ],
    )

    # ── TypeScript ──────────────────────────────────────────────────────
    specs["typescript"] = LanguageSpec(
        name="TypeScript",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        string_delimiters=("\"", "'", "`"),
        patterns=[
            (ElementType.INTERFACE, re.compile(
                r"^(\s*(?:export\s+)?interface\s+(\w+))")),
            (ElementType.TYPE_ALIAS, re.compile(
                r"^(\s*(?:export\s+)?type\s+(\w+)\s*(?:<[^>]*>)?\s*=)")),
            (ElementType.ENUM, re.compile(
                r"^(\s*(?:export\s+)?(?:const\s+)?enum\s+(\w+))")),
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s+(\w+)\s*)")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*(?::\s*[^=]+)?\s*=\s*"
                r"(?:async\s+)?(?:function|\([^)]*\)\s*(?::\s*[^=]+)?\s*=>|"
                r"[a-zA-Z_]\w*\s*=>))")),
            (ElementType.NAMESPACE, re.compile(
                r"^(\s*(?:export\s+)?(?:declare\s+)?namespace\s+(\w+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*(?:export\s+)?(?:declare\s+)?module\s+(\w+))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(.+))")),
            (ElementType.DECORATOR, re.compile(
                r"^(\s*@(\w[\w.]*)\s*)")),
        ],
    )

    # ── Java ────────────────────────────────────────────────────────────
    specs["java"] = LanguageSpec(
        name="Java",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?"
                r"(?:final\s+)?(?:abstract\s+)?class\s+(\w+))")),
            (ElementType.INTERFACE, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+)?interface\s+(\w+))")),
            (ElementType.ENUM, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+)?enum\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?"
                r"(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?"
                r"(?:abstract\s+)?(?:<[^>]+>\s+)?"
                r"(?:void|int|char|float|double|long|short|byte|boolean|"
                r"String|Object|List|Map|Set|Optional|\w+(?:<[^>]*>)?)\s*(?:\[\])?\s+"
                r"(\w+)\s*\()")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(?:static\s+)?(.+?);)")),
            (ElementType.MODULE, re.compile(
                r"^(\s*package\s+(.+?);)")),
            (ElementType.DECORATOR, re.compile(
                r"^(\s*@(\w[\w.]*(?:\([^)]*\))?))")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+)?static\s+final\s+\w+\s+([A-Z_]\w*)\s*=)")),
        ],
    )

    # ── Go ──────────────────────────────────────────────────────────────
    specs["go"] = LanguageSpec(
        name="Go",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        string_delimiters=("\"", "`"),
        patterns=[
            (ElementType.FUNCTION, re.compile(
                r"^(\s*func\s+(\w+)\s*\()")),
            (ElementType.METHOD, re.compile(
                r"^(\s*func\s+\(\s*\w+\s+\*?\w+\s*\)\s+(\w+)\s*\()")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*type\s+(\w+)\s+struct\b)")),
            (ElementType.INTERFACE, re.compile(
                r"^(\s*type\s+(\w+)\s+interface\b)")),
            (ElementType.TYPE_ALIAS, re.compile(
                r"^(\s*type\s+(\w+)\s+(?!struct|interface)\w)")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:const|var)\s+(\w+))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(.+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*package\s+(\w+))")),
        ],
    )

    # ── Ruby ────────────────────────────────────────────────────────────
    specs["ruby"] = LanguageSpec(
        name="Ruby",
        single_comment="#",
        multi_comment_start="=begin",
        multi_comment_end="=end",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*class\s+(\w+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*module\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*def\s+(?:self\.)?(\w+[?!=]?))")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*([A-Z][A-Z_0-9]+)\s*=)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*require(?:_relative)?\s+(.+))")),
            (ElementType.DECORATOR, re.compile(
                r"^(\s*attr_(?:reader|writer|accessor)\s+(.+))")),
        ],
    )

    # ── PHP ─────────────────────────────────────────────────────────────
    specs["php"] = LanguageSpec(
        name="PHP",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:abstract\s+|final\s+)?class\s+(\w+))")),
            (ElementType.INTERFACE, re.compile(
                r"^(\s*interface\s+(\w+))")),
            (ElementType.TRAIT, re.compile(
                r"^(\s*trait\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?function\s+(\w+)\s*\()")),
            (ElementType.NAMESPACE, re.compile(
                r"^(\s*namespace\s+(.+?);)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*(?:use|require|require_once|include|include_once)\s+(.+?);)")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:const|define)\s*\(?\s*['\"]?(\w+))")),
        ],
    )

    # ── Swift ───────────────────────────────────────────────────────────
    specs["swift"] = LanguageSpec(
        name="Swift",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:public\s+|private\s+|internal\s+|open\s+|fileprivate\s+)?"
                r"(?:final\s+)?class\s+(\w+))")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*(?:public\s+|private\s+|internal\s+)?struct\s+(\w+))")),
            (ElementType.ENUM, re.compile(
                r"^(\s*(?:public\s+|private\s+|internal\s+)?enum\s+(\w+))")),
            (ElementType.PROTOCOL, re.compile(
                r"^(\s*(?:public\s+|private\s+|internal\s+)?protocol\s+(\w+))")),
            (ElementType.EXTENSION, re.compile(
                r"^(\s*(?:public\s+|private\s+|internal\s+)?extension\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:public\s+|private\s+|internal\s+|open\s+)?(?:static\s+|class\s+)?"
                r"(?:override\s+)?func\s+(\w+))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(\w+))")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:public\s+|private\s+)?(?:static\s+)?let\s+(\w+)\s*(?::|\s*=))")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*(?:public\s+|private\s+)?(?:static\s+)?var\s+(\w+)\s*(?::|\s*=))")),
        ],
    )

    # ── Kotlin ──────────────────────────────────────────────────────────
    specs["kotlin"] = LanguageSpec(
        name="Kotlin",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:open\s+|abstract\s+|sealed\s+|data\s+|inner\s+)*class\s+(\w+))")),
            (ElementType.INTERFACE, re.compile(
                r"^(\s*interface\s+(\w+))")),
            (ElementType.ENUM, re.compile(
                r"^(\s*enum\s+class\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:open\s+|override\s+)?"
                r"(?:suspend\s+)?fun\s+(?:<[^>]+>\s+)?(\w+)\s*\()")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:const\s+)?val\s+(\w+))")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*var\s+(\w+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*(?:object|companion\s+object)\s+(\w*))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(.+))")),
            (ElementType.DECORATOR, re.compile(
                r"^(\s*@(\w[\w.]*)\s*)")),
        ],
    )

    # ── Scala ───────────────────────────────────────────────────────────
    specs["scala"] = LanguageSpec(
        name="Scala",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:abstract\s+|sealed\s+|case\s+)?class\s+(\w+))")),
            (ElementType.TRAIT, re.compile(
                r"^(\s*trait\s+(\w+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*object\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:override\s+)?def\s+(\w+))")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*val\s+(\w+))")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*var\s+(\w+))")),
            (ElementType.TYPE_ALIAS, re.compile(
                r"^(\s*type\s+(\w+))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(.+))")),
        ],
    )

    # ── Lua ─────────────────────────────────────────────────────────────
    specs["lua"] = LanguageSpec(
        name="Lua",
        single_comment="--",
        multi_comment_start="--[[",
        multi_comment_end="]]",
        patterns=[
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:local\s+)?function\s+(\w[\w.:]*))\s*\(")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:local\s+)?(\w[\w.]*)\s*=\s*function\s*\()")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*local\s+(\w+)\s*=)")),
        ],
    )

    # ── Shell (Bash) ────────────────────────────────────────────────────
    specs["shell"] = LanguageSpec(
        name="Shell",
        single_comment="#",
        multi_comment_start=None,
        multi_comment_end=None,
        patterns=[
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:function\s+)?(\w+)\s*\(\s*\))")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*(?:export\s+|readonly\s+|declare\s+(?:-\w+\s+)*)?"
                r"([A-Z_][A-Z_0-9]*)\s*=)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*(?:source|\\.)\s+(.+))")),
        ],
    )
    specs["bash"] = specs["shell"]
    specs["sh"] = specs["shell"]
    specs["zsh"] = specs["shell"]

    # ── Perl ────────────────────────────────────────────────────────────
    specs["perl"] = LanguageSpec(
        name="Perl",
        single_comment="#",
        multi_comment_start="=pod",
        multi_comment_end="=cut",
        patterns=[
            (ElementType.FUNCTION, re.compile(
                r"^(\s*sub\s+(\w+))")),
            (ElementType.MODULE, re.compile(
                r"^(\s*package\s+(\w[\w:]*))")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:use\s+constant\s+(\w+)))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*(?:use|require)\s+(.+?);)")),
        ],
    )

    # ── Haskell ─────────────────────────────────────────────────────────
    specs["haskell"] = LanguageSpec(
        name="Haskell",
        single_comment="--",
        multi_comment_start="{-",
        multi_comment_end="-}",
        patterns=[
            (ElementType.MODULE, re.compile(
                r"^(\s*module\s+(\w[\w.]*))")),
            (ElementType.TYPE_ALIAS, re.compile(
                r"^(\s*type\s+(\w+))")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*data\s+(\w+))")),
            (ElementType.CLASS, re.compile(
                r"^(\s*class\s+(\w+))")),
            (ElementType.FUNCTION, re.compile(
                r"^(([a-z_]\w*)\s*::)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*import\s+(?:qualified\s+)?(.+))")),
        ],
    )

    # ── Zig ─────────────────────────────────────────────────────────────
    specs["zig"] = LanguageSpec(
        name="Zig",
        single_comment="//",
        multi_comment_start=None,
        multi_comment_end=None,
        patterns=[
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:pub\s+|export\s+)?fn\s+(\w+))")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*(?:pub\s+)?const\s+(\w+)\s*=\s*(?:extern\s+|packed\s+)?struct\b)")),
            (ElementType.ENUM, re.compile(
                r"^(\s*(?:pub\s+)?const\s+(\w+)\s*=\s*enum\b)")),
            (ElementType.UNION, re.compile(
                r"^(\s*(?:pub\s+)?const\s+(\w+)\s*=\s*(?:extern\s+|packed\s+)?union\b)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*const\s+(\w+)\s*=\s*@import\()")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:pub\s+)?const\s+(\w+)\s*(?::\s*[^=]+)?\s*=)")),
            (ElementType.VARIABLE, re.compile(
                r"^(\s*(?:pub\s+)?var\s+(\w+))")),
        ],
    )

    # ── Elixir ──────────────────────────────────────────────────────────
    specs["elixir"] = LanguageSpec(
        name="Elixir",
        single_comment="#",
        multi_comment_start=None,
        multi_comment_end=None,
        patterns=[
            (ElementType.MODULE, re.compile(
                r"^(\s*defmodule\s+(\w[\w.]*))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:def|defp|defmacro|defmacrop)\s+(\w+))")),
            (ElementType.PROTOCOL, re.compile(
                r"^(\s*defprotocol\s+(\w[\w.]*))")),
            (ElementType.IMPL, re.compile(
                r"^(\s*defimpl\s+(\w[\w.]*))")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*defstruct\s+(.+))")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*(?:import|alias|use|require)\s+(.+))")),
        ],
    )

    # ── C# ──────────────────────────────────────────────────────────────
    specs["csharp"] = LanguageSpec(
        name="C#",
        single_comment="//",
        multi_comment_start="/*",
        multi_comment_end="*/",
        patterns=[
            (ElementType.CLASS, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+)?"
                r"(?:sealed\s+|abstract\s+|partial\s+)?class\s+(\w+))")),
            (ElementType.INTERFACE, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+|internal\s+)?interface\s+(\w+))")),
            (ElementType.STRUCT, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+|internal\s+)?"
                r"(?:readonly\s+)?struct\s+(\w+))")),
            (ElementType.ENUM, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+|internal\s+)?enum\s+(\w+))")),
            (ElementType.NAMESPACE, re.compile(
                r"^(\s*namespace\s+(\w[\w.]*))")),
            (ElementType.FUNCTION, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+)?"
                r"(?:async\s+)?(?:virtual\s+|override\s+|abstract\s+)?"
                r"(?:void|int|char|float|double|long|short|byte|bool|decimal|"
                r"string|object|var|Task|IEnumerable|\w+(?:<[^>]*>)?)\s*(?:\[\])?\s+"
                r"(\w+)\s*\()")),
            (ElementType.PROPERTY, re.compile(
                r"^(\s*(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+)?"
                r"(?:virtual\s+|override\s+)?(?:required\s+)?"
                r"\w+(?:<[^>]*>)?\s+(\w+)\s*\{)")),
            (ElementType.IMPORT, re.compile(
                r"^(\s*using\s+(.+?);)")),
            (ElementType.DECORATOR, re.compile(
                r"^(\s*\[(\w[\w.]*(?:\([^)]*\))?)\])")),
            (ElementType.CONSTANT, re.compile(
                r"^(\s*(?:public\s+|private\s+)?const\s+\w+\s+(\w+)\s*=)")),
        ],
    )
    specs["cs"] = specs["csharp"]

    # Common aliases
    specs["js"] = specs["javascript"]
    specs["ts"] = specs["typescript"]
    specs["rs"] = specs["rust"]
    specs["py"] = specs["python"]
    specs["rb"] = specs["ruby"]
    specs["hs"] = specs["haskell"]
    specs["cc"] = specs["cpp"]
    specs["cxx"] = specs["cpp"]
    specs["h"] = specs["c"]
    specs["hpp"] = specs["cpp"]
    specs["kt"] = specs["kotlin"]
    specs["ex"] = specs["elixir"]
    specs["exs"] = specs["elixir"]
    specs["pl"] = specs["perl"]

    return specs


class SourceAnalyzer:
    """! @brief Multi-language source file analyzer.
    @details Analyzes a source file identifying definitions, comments and constructs for the specified language. Produces structured output with line numbers, inspired by tree-sitter tags functionality.
    """

    def __init__(self):
        """! @brief Initialize analyzer state with language specifications."""
        self.specs = build_language_specs()

    def get_supported_languages(self) -> list:
        """! @brief Return list of supported languages (without aliases).
        @return Sorted list of unique language identifiers.
        """
        seen = set()
        result = []
        for key, spec in self.specs.items():
            if id(spec) not in seen:
                seen.add(id(spec))
                result.append(key)
        return sorted(result)

    def analyze(self, filepath: str, language: str) -> list:
        """! @brief Analyze a source file and return the list of SourceElement found.
        @param filepath Path to the source file.
        @param language Language identifier.
        @return List of SourceElement instances.
        @throws ValueError If language is not supported.
        @details Reads file content, detects single/multi-line comments, and matches regex patterns for definitions.
        """
        language = language.lower().strip().lstrip(".")
        if language not in self.specs:
            raise ValueError(
                f"Language '{language}' not supported.\n"
                f"Supported languages: {', '.join(self.get_supported_languages())}"
            )

        spec = self.specs[language]

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        elements = []

        # Multi-line comment state
        in_multiline_comment = False
        multiline_comment_start_line = 0
        multiline_comment_lines = []

        for line_num, line in enumerate(lines, start=1):
            stripped = line.rstrip("\n\r")

            # ── Multi-line comment handling ──────────────────────────
            if in_multiline_comment:
                multiline_comment_lines.append(stripped)
                if spec.multi_comment_end and spec.multi_comment_end in stripped:
                    in_multiline_comment = False
                    mc_extract = multiline_comment_lines
                    if len(mc_extract) > 5:
                        mc_extract = mc_extract[:4] + ["    ..."]
                    elements.append(SourceElement(
                        element_type=ElementType.COMMENT_MULTI,
                        line_start=multiline_comment_start_line,
                        line_end=line_num,
                        extract="\n".join(mc_extract),
                    ))
                    multiline_comment_lines = []
                continue

            # ── Multi-line comment start ────────────────────────────
            if spec.multi_comment_start:
                # Special handling for Python docstrings and =begin/=pod blocks
                mc_start = spec.multi_comment_start
                if mc_start in stripped:
                    start_idx = stripped.index(mc_start)
                    # Check not inside a string
                    if not self._in_string_context(stripped, start_idx, spec):
                        # Check if multi-line comment closes on same line
                        after_start = stripped[start_idx + len(mc_start):]
                        if (spec.multi_comment_end
                                and spec.multi_comment_end in after_start
                                and mc_start != spec.multi_comment_end):
                            elements.append(SourceElement(
                                element_type=ElementType.COMMENT_MULTI,
                                line_start=line_num,
                                line_end=line_num,
                                extract=stripped,
                            ))
                            continue
                        # Python: """ ... """ sulla stessa riga
                        if mc_start == '"""' or mc_start == "'''":
                            rest = stripped[start_idx + 3:]
                            if mc_start in rest:
                                elements.append(SourceElement(
                                    element_type=ElementType.COMMENT_MULTI,
                                    line_start=line_num,
                                    line_end=line_num,
                                    extract=stripped,
                                ))
                                continue

                        in_multiline_comment = True
                        multiline_comment_start_line = line_num
                        multiline_comment_lines = [stripped]
                        continue

            # ── Single-line comment ───────────────────────────────────
            if spec.single_comment:
                comment_idx = self._find_comment(stripped, spec)
                if comment_idx is not None:
                    # If comment is the entire line (aside from whitespace)
                    before_comment = stripped[:comment_idx].strip()
                    if not before_comment:
                        elements.append(SourceElement(
                            element_type=ElementType.COMMENT_SINGLE,
                            line_start=line_num,
                            line_end=line_num,
                            extract=stripped,
                        ))
                        continue
                    else:
                        # Inline comment: add both element and comment
                        comment_text = stripped[comment_idx:]
                        elements.append(SourceElement(
                            element_type=ElementType.COMMENT_SINGLE,
                            line_start=line_num,
                            line_end=line_num,
                            extract=comment_text,
                            name="inline",
                        ))

            # ── Language patterns ─────────────────────────────────────
            if not stripped.strip():
                continue

            for elem_type, pattern in spec.patterns:
                match = pattern.match(stripped)
                if match:
                    name = None
                    if match.lastindex and match.lastindex >= 2:
                        name = match.group(2)
                    elif match.lastindex and match.lastindex >= 1:
                        name = match.group(1)

                    # Single-line types: don't search for block
                    single_line_types = (
                        ElementType.IMPORT, ElementType.CONSTANT,
                        ElementType.VARIABLE, ElementType.DECORATOR,
                        ElementType.MACRO, ElementType.TYPE_ALIAS,
                        ElementType.TYPEDEF, ElementType.PROPERTY,
                    )

                    if elem_type in single_line_types:
                        block_end = line_num
                    else:
                        block_end = self._find_block_end(
                            lines, line_num - 1, language, stripped)

                    extract_lines = [lines[i].rstrip("\n\r")
                                     for i in range(line_num - 1, block_end)]

                    # Limit extract to max 5 lines for readability
                    if len(extract_lines) > 5:
                        extract_lines = extract_lines[:4] + ["    ..."]

                    elements.append(SourceElement(
                        element_type=elem_type,
                        line_start=line_num,
                        line_end=block_end,
                        extract="\n".join(extract_lines),
                        name=name,
                    ))
                    break

        return elements

    def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool:
        """! @brief Check if position pos is inside a string literal.
        @param line The line of code.
        @param pos The column index.
        @param spec The LanguageSpec instance.
        @return True if pos is within a string.
        """
        in_string = False
        current_delim = None
        i = 0
        while i < pos:
            ch = line[i]
            if in_string:
                if ch == "\\" and i + 1 < len(line):
                    i += 2
                    continue
                if line[i:].startswith(current_delim):
                    in_string = False
                    i += len(current_delim)
                    continue
            else:
                for delim in sorted(spec.string_delimiters, key=len, reverse=True):
                    if line[i:].startswith(delim):
                        in_string = True
                        current_delim = delim
                        i += len(delim)
                        break
                else:
                    i += 1
                    continue
                continue
            i += 1
        return in_string

    def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]:
        """! @brief Find position of single-line comment, ignoring strings.
        @param line The line of code.
        @param spec The LanguageSpec instance.
        @return Column index of comment start, or None.
        """
        if not spec.single_comment:
            return None

        in_string = False
        current_delim = None
        i = 0
        while i < len(line):
            ch = line[i]
            if in_string:
                if ch == "\\" and i + 1 < len(line):
                    i += 2
                    continue
                if line[i:].startswith(current_delim):
                    in_string = False
                    i += len(current_delim)
                    continue
            else:
                if line[i:].startswith(spec.single_comment):
                    return i
                for delim in sorted(spec.string_delimiters, key=len, reverse=True):
                    if line[i:].startswith(delim):
                        in_string = True
                        current_delim = delim
                        i += len(delim)
                        break
                else:
                    i += 1
                    continue
                continue
            i += 1
        return None

    def _find_block_end(self, lines: list, start_idx: int,
                        language: str, first_line: str) -> int:
        """! @brief Find the end of a block (function, class, struct, etc.).
        @param lines List of all file lines.
        @param start_idx Index of the start line.
        @param language Language identifier.
        @param first_line Content of the start line.
        @return 1-based index of the end line.
        @details Returns the index (1-based) of the final line of the block. Limits search for performance.
        """
        # Per Python: basato sull'indentazione
        if language in ("python", "py"):
            indent = len(first_line) - len(first_line.lstrip())
            end = start_idx + 1
            while end < min(len(lines), start_idx + 200):
                line = lines[end].rstrip("\n\r")
                if line.strip() == "":
                    end += 1
                    continue
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= indent and line.strip():
                    break
                end += 1
            return end

        # Per linguaggi con parentesi graffe
        if language in ("c", "cpp", "cc", "cxx", "h", "hpp", "rust", "rs",
                        "javascript", "js", "typescript", "ts", "java",
                        "go", "csharp", "cs", "swift", "kotlin", "kt",
                        "php", "scala", "zig"):
            brace_count = 0
            found_open = False
            end = start_idx
            while end < min(len(lines), start_idx + 300):
                line = lines[end].rstrip("\n\r")
                for ch in line:
                    if ch == "{":
                        brace_count += 1
                        found_open = True
                    elif ch == "}":
                        brace_count -= 1
                if found_open and brace_count <= 0:
                    return end + 1
                end += 1
            # If no opening braces found, return just the first line
            if not found_open:
                return start_idx + 1
            return end

        # Per Ruby/Elixir/Lua: basato su end keyword
        if language in ("ruby", "rb", "elixir", "ex", "exs", "lua"):
            indent = len(first_line) - len(first_line.lstrip())
            end = start_idx + 1
            while end < min(len(lines), start_idx + 200):
                line = lines[end].rstrip("\n\r")
                if line.strip() == "end" or line.strip().startswith("end "):
                    line_indent = len(line) - len(line.lstrip())
                    if line_indent <= indent:
                        return end + 1
                end += 1
            return start_idx + 1

        # Per Haskell: basato sull'indentazione
        if language in ("haskell", "hs"):
            indent = len(first_line) - len(first_line.lstrip())
            end = start_idx + 1
            while end < min(len(lines), start_idx + 100):
                line = lines[end].rstrip("\n\r")
                if line.strip() == "":
                    end += 1
                    continue
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= indent:
                    break
                end += 1
            return end

        return start_idx + 1

    # ── Enrichment methods for LLM-optimized output ───────────────────

    def enrich(self, elements: list, language: str,
               filepath: str = None) -> list:
        """! @brief Enrich elements with signatures, hierarchy, visibility, inheritance.
        @details Call after analyze() to add metadata for LLM-optimized markdown output. Modifies elements in-place and returns them. If filepath is provided, also extracts body comments and exit points.
        """
        language = language.lower().strip().lstrip(".")
        self._clean_names(elements, language)
        self._extract_signatures(elements, language)
        self._detect_hierarchy(elements)
        self._extract_visibility(elements, language)
        self._extract_inheritance(elements, language)
        if filepath:
            self._extract_body_annotations(elements, language, filepath)
            self._extract_doxygen_fields(elements)
        return elements

    def _clean_names(self, elements: list, language: str):
        """! @brief Extract clean identifiers from name fields.
        @details Due to regex group nesting, name may contain the full match expression (e.g. 'class MyClass:' instead of 'MyClass'). This method extracts the actual identifier.
        """
        for elem in elements:
            if not elem.name:
                continue
            name = elem.name.strip()
            # Try to re-extract the name from the element's extract line
            # using the original pattern (which has group 2 as the identifier)
            spec = self.specs.get(language)
            if spec:
                first_line = elem.extract.split("\n")[0]
                for etype, pattern in spec.patterns:
                    if etype == elem.element_type:
                        m = pattern.match(first_line)
                        if m:
                            # Take highest non-None non-empty group
                            # (group 2+ = identifier, group 1 = full match)
                            for gi in range(len(m.groups()), 0, -1):
                                g = m.group(gi)
                                if g is not None and g.strip():
                                    elem.name = g.strip()
                                    break
                            break

    def _extract_signatures(self, elements: list, language: str):
        """! @brief Extract clean signatures from element extracts.
        """
        skip_types = (ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI,
                      ElementType.IMPORT, ElementType.DECORATOR)
        for elem in elements:
            if elem.element_type in skip_types:
                continue
            first_line = elem.extract.split("\n")[0].strip()
            sig = first_line
            for suffix in (" {", "{", ":", ";"):
                if sig.endswith(suffix) and not sig.endswith("::"):
                    sig = sig[:-len(suffix)].rstrip()
                    break
            elem.signature = sig

    def _detect_hierarchy(self, elements: list):
        """! @brief Detect parent-child relationships between elements.
        @details Containers (class, struct, module, etc.) remain at depth=0. Non-container elements inside containers get depth=1 and parent_name set.
        """
        container_types = (
            ElementType.CLASS, ElementType.STRUCT, ElementType.MODULE,
            ElementType.IMPL, ElementType.INTERFACE, ElementType.TRAIT,
            ElementType.NAMESPACE, ElementType.ENUM, ElementType.EXTENSION,
            ElementType.PROTOCOL)
        containers = [e for e in elements if e.element_type in container_types]
        skip_types = (ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI,
                      ElementType.IMPORT)
        for elem in elements:
            if elem.element_type in skip_types:
                continue
            if elem.element_type in container_types:
                continue
            best = None
            for c in containers:
                if c is elem:
                    continue
                if (c.line_start <= elem.line_start
                        and c.line_end >= elem.line_end):
                    if best is None:
                        best = c
                    elif c.line_start > best.line_start:
                        best = c
                    elif (c.line_start == best.line_start
                          and c.line_end < best.line_end):
                        best = c
            if best is not None:
                elem.parent_name = best.name
                elem.depth = 1

    def _extract_visibility(self, elements: list, language: str):
        """! @brief Extract visibility/access modifiers from elements.
        """
        for elem in elements:
            if elem.element_type in (ElementType.COMMENT_SINGLE,
                                      ElementType.COMMENT_MULTI,
                                      ElementType.IMPORT):
                continue
            sig = elem.extract.split("\n")[0].strip()
            vis = self._parse_visibility(sig, elem.name, language)
            if vis:
                elem.visibility = vis

    def _parse_visibility(self, sig: str, name: Optional[str],
                          language: str) -> Optional[str]:
        """! @brief Parse visibility modifier from a signature line.
        """
        if language in ("python", "py"):
            if name and name.startswith("__") and not name.endswith("__"):
                return "priv"
            if name and name.startswith("_"):
                return "priv"
            return "pub"
        if language in ("java", "csharp", "cs", "kotlin", "kt", "php"):
            if re.search(r'\bpublic\b', sig):
                return "pub"
            if re.search(r'\bprivate\b', sig):
                return "priv"
            if re.search(r'\bprotected\b', sig):
                return "prot"
            if re.search(r'\binternal\b', sig):
                return "int"
            return None
        if language in ("rust", "rs", "zig"):
            if re.match(r'\s*pub\b', sig):
                return "pub"
            return "priv"
        if language in ("go",):
            if name and name[0:1].isupper():
                return "pub"
            return "priv"
        if language in ("swift",):
            if re.search(r'\bprivate\b', sig):
                return "priv"
            if re.search(r'\bfileprivate\b', sig):
                return "fpriv"
            if re.search(r'\b(?:public|open)\b', sig):
                return "pub"
            return None
        if language in ("cpp", "cc", "cxx", "h", "hpp"):
            if re.search(r'\bpublic\b', sig):
                return "pub"
            if re.search(r'\bprivate\b', sig):
                return "priv"
            if re.search(r'\bprotected\b', sig):
                return "prot"
            return None
        return None

    def _extract_inheritance(self, elements: list, language: str):
        """! @brief Extract inheritance/implementation info from class-like elements.
        """
        for elem in elements:
            if elem.element_type not in (ElementType.CLASS, ElementType.STRUCT,
                                          ElementType.INTERFACE):
                continue
            first_line = elem.extract.split("\n")[0].strip()
            inh = self._parse_inheritance(first_line, language)
            if inh:
                elem.inherits = inh

    def _parse_inheritance(self, first_line: str,
                           language: str) -> Optional[str]:
        """! @brief Parse inheritance info from a class/struct declaration line.
        """
        if language in ("python", "py"):
            m = re.search(r'class\s+\w+\s*\(([^)]+)\)', first_line)
            return m.group(1).strip() if m else None
        if language in ("java", "typescript", "ts", "javascript", "js"):
            parts = []
            m = re.search(r'\bextends\s+([\w.<>, ]+)', first_line)
            if m:
                parts.append(m.group(1).strip())
            m = re.search(r'\bimplements\s+([\w.<>, ]+)', first_line)
            if m:
                parts.append(m.group(1).strip())
            return ", ".join(parts) if parts else None
        if language in ("cpp", "cc", "cxx", "hpp", "csharp", "cs", "swift"):
            m = re.search(
                r'(?:class|struct)\s+\w+\s*:\s*(.+?)(?:\s*\{|$)', first_line)
            return m.group(1).strip() if m else None
        if language in ("kotlin", "kt"):
            m = re.search(
                r'class\s+\w+\s*(?:\([^)]*\))?\s*:\s*(.+?)(?:\s*\{|$)',
                first_line)
            return m.group(1).strip() if m else None
        if language in ("ruby", "rb"):
            m = re.search(r'class\s+\w+\s*<\s*(\w+)', first_line)
            return m.group(1) if m else None
        return None

    # ── Exit point patterns per language family ──────────────────────

    _EXIT_PATTERNS_RETURN = re.compile(
        r'^\s*(return\b.*|yield\b.*|raise\b.*|throw\b.*|panic!\(.*)')
    _EXIT_PATTERNS_IMPLICIT = re.compile(
        r'^\s*(sys\.exit\(.*|os\._exit\(.*|exit\(.*|process\.exit\(.*)')

    def _extract_body_annotations(self, elements: list,
                                  language: str, filepath: str):
        """! @brief Extract comments and exit points from within function/class bodies.
        @details Reads the source file and scans each definition's line range for: - Single-line comments (# or // etc.) - Multi-line comments (docstrings, /* */ blocks) - Exit points (return, yield, raise, throw, panic!, sys.exit) Populates body_comments and exit_points on each element.
        """
        spec = self.specs.get(language)
        if not spec:
            return

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
        except (OSError, IOError):
            return

        # Only process definitions that span multiple lines
        single_line_types = (
            ElementType.IMPORT, ElementType.CONSTANT,
            ElementType.VARIABLE, ElementType.DECORATOR,
            ElementType.MACRO, ElementType.TYPE_ALIAS,
            ElementType.TYPEDEF, ElementType.PROPERTY,
            ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI,
        )

        for elem in elements:
            if elem.element_type in single_line_types:
                continue
            if elem.line_end <= elem.line_start:
                continue

            body_comments = []
            exit_points = []

            # Scan the body (lines after the definition line)
            body_start = elem.line_start  # 1-based, skip def line itself
            body_end = min(elem.line_end, len(all_lines))

            in_multi = False
            multi_start = 0
            multi_lines = []

            for line_idx in range(body_start, body_end):
                raw = all_lines[line_idx].rstrip("\n\r")
                stripped = raw.strip()

                if not stripped:
                    continue

                # Multi-line comment tracking within body
                if in_multi:
                    multi_lines.append(stripped)
                    if spec.multi_comment_end and spec.multi_comment_end in stripped:
                        in_multi = False
                        text = " ".join(
                            self._clean_comment_line(ln, spec)
                            for ln in multi_lines)
                        text = text.strip()
                        if text:
                            body_comments.append(
                                (multi_start, line_idx + 1, text))
                        multi_lines = []
                    continue

                # Check for multi-line comment start
                if spec.multi_comment_start and spec.multi_comment_start in stripped:
                    mc_start = spec.multi_comment_start
                    start_pos = stripped.index(mc_start)
                    if not self._in_string_context(stripped, start_pos, spec):
                        # Single-line multi-comment
                        if mc_start == '"""' or mc_start == "'''":
                            after = stripped[start_pos + 3:]
                            if mc_start in after:
                                text = self._clean_comment_line(
                                    stripped, spec)
                                if text:
                                    body_comments.append(
                                        (line_idx + 1, line_idx + 1, text))
                                continue
                        elif (spec.multi_comment_end
                              and spec.multi_comment_end in stripped[
                                  start_pos + len(mc_start):]):
                            text = self._clean_comment_line(stripped, spec)
                            if text:
                                body_comments.append(
                                    (line_idx + 1, line_idx + 1, text))
                            continue

                        in_multi = True
                        multi_start = line_idx + 1
                        multi_lines = [stripped]
                        continue

                # Single-line comment (full line)
                if spec.single_comment:
                    comment_pos = self._find_comment(stripped, spec)
                    if comment_pos is not None:
                        before = stripped[:comment_pos].strip()
                        comment_text = stripped[comment_pos:]
                        cleaned = self._clean_comment_line(
                            comment_text, spec)

                        if not before:
                            # Standalone comment line in body
                            if cleaned:
                                body_comments.append(
                                    (line_idx + 1, line_idx + 1, cleaned))
                            continue
                        else:
                            # Inline comment after code
                            if cleaned:
                                body_comments.append(
                                    (line_idx + 1, line_idx + 1, cleaned))

                # Exit points
                if self._EXIT_PATTERNS_RETURN.match(stripped):
                    exit_text = stripped.strip()
                    exit_points.append((line_idx + 1, exit_text))
                elif self._EXIT_PATTERNS_IMPLICIT.match(stripped):
                    exit_text = stripped.strip()
                    exit_points.append((line_idx + 1, exit_text))

            elem.body_comments = body_comments
            elem.exit_points = exit_points

    def _extract_doxygen_fields(self, elements: list):
        """! @brief Extract Doxygen tag fields from associated documentation comments.
        @details For each non-comment element, resolves the nearest associated documentation comment using language-agnostic adjacency rules: same-line postfix comment (`//!<`, `#!<`, `/**<`), nearest preceding standalone comment block within two lines, or nearest following postfix standalone comment within two lines. Parses the resolved comment via parse_doxygen_comment() and stores the extracted fields in element.doxygen_fields.
        """
        comment_elements = [e for e in elements if e.element_type in
                           (ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI)]

        for elem in elements:
            # Skip comments themselves
            if elem.element_type in (ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI):
                continue

            associated_comment = None

            same_line_postfix_candidates = [
                comment
                for comment in comment_elements
                if comment.line_start == elem.line_end
                and comment.name == "inline"
                and self._is_postfix_doxygen_comment(comment.extract)
            ]
            if same_line_postfix_candidates:
                associated_comment = min(
                    same_line_postfix_candidates,
                    key=lambda comment: comment.line_start,
                )

            if associated_comment is None:
                preceding_candidates = [
                    comment
                    for comment in comment_elements
                    if comment.name != "inline"
                    and comment.line_end < elem.line_start
                    and elem.line_start - comment.line_end <= 2
                ]
                if preceding_candidates:
                    associated_comment = max(
                        preceding_candidates,
                        key=lambda comment: (comment.line_end, comment.line_start),
                    )

            if associated_comment is None:
                following_postfix_candidates = [
                    comment
                    for comment in comment_elements
                    if comment.name != "inline"
                    and comment.line_start > elem.line_end
                    and comment.line_start - elem.line_end <= 2
                    and self._is_postfix_doxygen_comment(comment.extract)
                ]
                if following_postfix_candidates:
                    associated_comment = min(
                        following_postfix_candidates,
                        key=lambda comment: (comment.line_start, comment.line_end),
                    )

            if associated_comment:
                comment_text = associated_comment.extract
                elem.doxygen_fields = parse_doxygen_comment(comment_text)

    @staticmethod
    def _is_postfix_doxygen_comment(comment_text: str) -> bool:
        """! @brief Detect whether a comment uses postfix Doxygen association markers.
        @details Returns True for comment prefixes that explicitly bind documentation to a preceding construct, including variants like `#!<`, `//!<`, `///<`, `/*!<`, and `/**<`.
        @param comment_text Raw extracted comment text.
        @return True when the comment text starts with a supported postfix marker; otherwise False.
        """
        if not comment_text:
            return False
        return bool(re.match(r"^\s*(?:#|//+|--|/\*+|;+)!?<", comment_text))

    @staticmethod
    def _clean_comment_line(text: str, spec) -> str:
        """! @brief Strip comment markers from a single line of comment text.
        """
        s = text.strip()
        for prefix in ("///", "//!", "//", "#!", "##", "#", "--", ";;"):
            if s.startswith(prefix):
                s = s[len(prefix):].strip()
                break
        s = s.strip("/*\"'").strip()
        return s


def _md_loc(elem) -> str:
    """! @brief Format element location compactly for markdown.
    """
    if elem.line_start == elem.line_end:
        return f"L{elem.line_start}"
    return f"L{elem.line_start}-{elem.line_end}"


def _md_kind(elem) -> str:
    """! @brief Short kind label for markdown output.
    """
    mapping = {
        ElementType.FUNCTION: "fn",
        ElementType.METHOD: "method",
        ElementType.CLASS: "class",
        ElementType.STRUCT: "struct",
        ElementType.ENUM: "enum",
        ElementType.TRAIT: "trait",
        ElementType.INTERFACE: "iface",
        ElementType.MODULE: "mod",
        ElementType.IMPL: "impl",
        ElementType.MACRO: "macro",
        ElementType.CONSTANT: "const",
        ElementType.VARIABLE: "var",
        ElementType.TYPE_ALIAS: "type",
        ElementType.COMPONENT: "comp",
        ElementType.PROPERTY: "prop",
        ElementType.DECORATOR: "dec",
        ElementType.TYPEDEF: "typedef",
        ElementType.EXTENSION: "ext",
        ElementType.PROTOCOL: "proto",
        ElementType.NAMESPACE: "ns",
    }
    return mapping.get(elem.element_type, "unk")


def _extract_comment_text(comment_elem, max_length: int = 0) -> str:
    """! @brief Extract clean text content from a comment element.
    @details Args: comment_elem: SourceElement with comment content max_length: if >0, truncate to this length. 0 = no truncation.
    """
    lines = comment_elem.extract.split("\n")
    cleaned = []
    for ln in lines:
        s = ln.strip()
        # Strip comment markers
        for prefix in ("///", "//!", "//", "#!", "##", "#", "--", ";;"):
            if s.startswith(prefix):
                s = s[len(prefix):].strip()
                break
        # Strip multi-line markers
        s = s.strip("/*\"'").strip()
        if s and not s.startswith("=begin") and not s.startswith("=end"):
            cleaned.append(s)
    text = " ".join(cleaned) if cleaned else ""
    if max_length > 0 and len(text) > max_length:
        text = text[:max_length - 3] + "..."
    return text


def _extract_comment_lines(comment_elem) -> list:
    """! @brief Extract clean text lines from a multi-line comment (preserving structure).
    """
    lines = comment_elem.extract.split("\n")
    cleaned = []
    for ln in lines:
        s = ln.strip()
        for prefix in ("///", "//!", "//", "#!", "##", "#", "--", ";;"):
            if s.startswith(prefix):
                s = s[len(prefix):].strip()
                break
        s = s.strip("/*\"'").strip()
        if s and not s.startswith("=begin") and not s.startswith("=end"):
            cleaned.append(s)
    return cleaned


def _build_comment_maps(elements: list) -> tuple:
    """! @brief Build maps that associate comments with their adjacent definitions.
    @details Returns: - doc_for_def: dict mapping def line_start -> list of comment texts (comments immediately preceding a definition) - standalone_comments: list of comment elements not attached to defs - file_description: text from the first comment block (file-level docs)
    """
    all_sorted = sorted(elements, key=lambda e: e.line_start)

    # Identify definition elements
    def_types = set(ElementType) - {
        ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI,
        ElementType.IMPORT, ElementType.DECORATOR}
    def_starts = {e.line_start for e in elements if e.element_type in def_types}
    import_starts = {e.line_start for e in elements
                     if e.element_type == ElementType.IMPORT}

    # Build adjacency map: comments preceding a definition (within 2 lines)
    doc_for_def = {}
    standalone_comments = []
    file_description = ""

    comments = [e for e in all_sorted
                if e.element_type in (ElementType.COMMENT_SINGLE,
                                      ElementType.COMMENT_MULTI)]

    # Extract file description from first comment(s), skip shebangs
    for first_c in comments:
        if first_c.line_start > 10:
            break
        text = _extract_comment_text(first_c)
        # Skip shebang lines and empty comments
        if text and not text.startswith("/usr/") and not text.startswith("usr/"):
            file_description = text
            if len(file_description) > 200:
                file_description = file_description[:197] + "..."
            break

    for c in comments:
        # Skip inline comments (name == "inline")
        if c.name == "inline":
            continue

        attached = False
        # Check if this comment precedes a definition within 2 lines
        for gap in range(1, 4):
            target_line = c.line_end + gap
            if target_line in def_starts:
                doc_for_def.setdefault(target_line, []).append(c)
                attached = True
                break
            # Stop if we hit another element
            if target_line in import_starts:
                break

        if not attached and c != comments[0]:
            # Skip file-level description (already captured)
            standalone_comments.append(c)
        elif not attached and c == comments[0] and not file_description:
            standalone_comments.append(c)

    return doc_for_def, standalone_comments, file_description


def _render_body_annotations(out: list, elem, indent: str = "",
                             exclude_ranges: list = None):
    """! @brief Render body comments and exit points for a definition element.
    @details Merges body_comments and exit_points in line-number order, outputting each as L<N>> text. When both a comment and exit point exist on the same line, merges them as: L<N>> `return` — comment text. Skips annotations within exclude_ranges.
    """
    # Build maps by line number
    comment_map = {}
    for (start, end, text) in getattr(elem, 'body_comments', []):
        comment_map[start] = (start, end, text)

    exit_map = {}
    for (line_num, text) in getattr(elem, 'exit_points', []):
        exit_map[line_num] = text

    # Collect all annotated line numbers
    all_lines = sorted(set(comment_map.keys()) | set(exit_map.keys()))

    for line_num in all_lines:
        # Skip if within an excluded range (child element)
        if exclude_ranges:
            in_child = False
            for cstart, cend in exclude_ranges:
                if cstart <= line_num <= cend:
                    in_child = True
                    break
            if in_child:
                continue

        has_comment = line_num in comment_map
        has_exit = line_num in exit_map

        if has_comment and has_exit:
            # Merge: show exit point code with comment as context
            exit_text = exit_map[line_num]
            comment_text = comment_map[line_num][2]
            # Strip inline comment from exit_text if it contains it
            exit_clean = exit_text
            if '#' in exit_clean:
                exit_clean = exit_clean[:exit_clean.index('#')].strip()
            elif '//' in exit_clean:
                exit_clean = exit_clean[:exit_clean.index('//')].strip()
            out.append(f"{indent}L{line_num}> `{exit_clean}` — {comment_text}")
        elif has_exit:
            out.append(f"{indent}L{line_num}> `{exit_map[line_num]}`")
        elif has_comment:
            start, end, text = comment_map[line_num]
            if start == end:
                out.append(f"{indent}L{start}> {text}")
            else:
                out.append(f"{indent}L{start}-{end}> {text}")


def format_markdown(
    elements: list,
    filepath: str,
    language: str,
    spec_name: str,
    total_lines: int,
    include_legacy_annotations: bool = True,
) -> str:
    """! @brief Format analysis as compact Markdown optimized for LLM agent consumption.
    @details Produces token-efficient output with: - File header with language, line count, element summary, and optional file description - Imports in a code block - Hierarchical definitions enriched with ordered Doxygen field bullets when available - Optional legacy comment/exit traces when include_legacy_annotations is enabled - Symbol index table for quick reference by line number.
    @param elements Parsed and optionally enriched SourceElement list.
    @param filepath Absolute or relative source file path.
    @param language Normalized source language key.
    @param spec_name Display language name from LanguageSpec.
    @param total_lines Total source file line count.
    @param include_legacy_annotations Enable legacy L<n>> comment/exit traces and standalone comments section.
    @return Markdown payload for one analyzed file.
    """
    out = []
    fname = os.path.basename(filepath)

    skip_types = (ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI,
                  ElementType.IMPORT, ElementType.DECORATOR)
    n_defs = sum(1 for e in elements if e.element_type not in skip_types)
    n_imports = sum(1 for e in elements if e.element_type == ElementType.IMPORT)

    # Build comment association maps
    doc_for_def, standalone_comments, file_desc = _build_comment_maps(elements)
    if not include_legacy_annotations:
        standalone_comments = []
        file_desc = ""

    try:
        from .doxygen_parser import format_doxygen_fields_as_markdown
    except ImportError:
        from doxygen_parser import format_doxygen_fields_as_markdown

    # ── Header ────────────────────────────────────────────────────────
    n_comments = sum(1 for e in elements
                     if e.element_type in (ElementType.COMMENT_SINGLE,
                                           ElementType.COMMENT_MULTI)
                     and e.name != "inline")
    out.append(f"# {fname} | {spec_name} | {total_lines}L | "
               f"{n_defs} symbols | {n_imports} imports | {n_comments} comments")
    out.append(f"> Path: `{filepath}`")
    if file_desc:
        out.append(f"> {file_desc}")
    out.append("")

    # ── Imports ───────────────────────────────────────────────────────
    imports = sorted(
        [e for e in elements if e.element_type == ElementType.IMPORT],
        key=lambda e: e.line_start)
    if imports:
        out.append("## Imports")
        out.append("```")
        for imp in imports:
            first = imp.extract.split("\n")[0].strip()
            out.append(first)
        out.append("```")
        out.append("")

    # ── Build decorator map: line -> decorator text ───────────────────
    dec_map = {}
    for e in elements:
        if e.element_type == ElementType.DECORATOR:
            dec_map[e.line_start] = e.extract.split("\n")[0].strip()

    # ── Definitions ───────────────────────────────────────────────────
    defs = sorted(
        [e for e in elements if e.element_type not in skip_types],
        key=lambda e: e.line_start)

    top_level = [e for e in defs if e.depth == 0]
    children_map = {}
    for e in defs:
        if e.depth > 0 and e.parent_name:
            for top in top_level:
                if (top.name == e.parent_name
                        and top.line_start <= e.line_start
                        and top.line_end >= e.line_end):
                    children_map.setdefault(id(top), []).append(e)
                    break

    inline_types = (ElementType.CONSTANT, ElementType.VARIABLE,
                    ElementType.TYPE_ALIAS, ElementType.TYPEDEF,
                    ElementType.MACRO, ElementType.PROPERTY)

    if top_level:
        out.append("## Definitions")
        out.append("")

        i = 0
        while i < len(top_level):
            elem = top_level[i]
            kind = _md_kind(elem)
            sig = elem.signature or elem.name or ""
            loc = _md_loc(elem)
            inherit_str = f" : {elem.inherits}" if elem.inherits else ""
            vis_str = ""
            if elem.visibility and elem.visibility not in ("pub", "public"):
                vis_str = f" `{elem.visibility}`"

            dec_str = ""
            dec_line = elem.line_start - 1
            if dec_line in dec_map:
                dec_str = f" `{dec_map[dec_line]}`"

            # Collect associated doc comments for this definition
            # Prefer Doxygen fields if present (DOX-009).
            def_docs = doc_for_def.get(elem.line_start, [])
            doc_text = ""
            doc_lines_list = []
            doc_line_num = 0
            doxygen_markdown = []

            if hasattr(elem, 'doxygen_fields') and elem.doxygen_fields:
                doxygen_markdown = format_doxygen_fields_as_markdown(elem.doxygen_fields)
                # Use brief as inline doc_text if available
                if 'brief' in elem.doxygen_fields:
                    doc_text = elem.doxygen_fields['brief'][0]
                    if len(doc_text) > 150:
                        doc_text = doc_text[:147] + "..."
            elif include_legacy_annotations and def_docs:
                doc_lines_list = _extract_comment_lines(def_docs[0])
                doc_text = " ".join(doc_lines_list) if doc_lines_list else ""
                doc_line_num = def_docs[0].line_start
                if len(doc_text) > 150:
                    doc_text = doc_text[:147] + "..."

            is_single_line = (elem.line_start == elem.line_end)
            is_inline = (elem.element_type in inline_types or is_single_line)

            if is_inline:
                first_line = elem.extract.split("\n")[0].strip()
                line = f"- {kind} `{first_line}`{vis_str} (L{elem.line_start})"
                if include_legacy_annotations and doc_text:
                    line += f" — {doc_text}"
                out.append(line)
                if doxygen_markdown:
                    out.extend(doxygen_markdown)
                i += 1
            else:
                # For impl blocks, use the full first line as sig
                if elem.element_type == ElementType.IMPL:
                    first_line = elem.extract.split("\n")[0].strip()
                    sig = first_line.rstrip(" {")

                out.append(f"### {kind} `{sig}`{inherit_str}{vis_str}"
                           f"{dec_str} ({loc})")

                # Show Doxygen fields if present, else raw comment (DOX-009)
                if doxygen_markdown:
                    out.extend(doxygen_markdown)
                elif include_legacy_annotations and doc_lines_list and len(doc_lines_list) > 1:
                    for idx, dline in enumerate(doc_lines_list[:5]):
                        ln = doc_line_num + idx
                        out.append(f"L{ln}> {dline}")
                    if len(doc_lines_list) > 5:
                        out.append(f"L{doc_line_num + 5}> ...")
                elif include_legacy_annotations and doc_text and doc_line_num:
                    out.append(f"L{doc_line_num}> {doc_text}")

                # Body annotations: comments and exit points
                # For containers with children, exclude annotations
                # that fall within a child's line range (including
                # doc comments that immediately precede the child)
                kids = children_map.get(id(elem), [])
                if include_legacy_annotations:
                    child_ranges = []
                    for c in kids:
                        range_start = c.line_start
                        # Extend range to include preceding doc comment
                        c_docs = doc_for_def.get(c.line_start, [])
                        if c_docs:
                            range_start = min(range_start,
                                              c_docs[0].line_start)
                        child_ranges.append((range_start, c.line_end))
                    _render_body_annotations(out, elem,
                                             exclude_ranges=child_ranges)

                # Children with their doc comments and body annotations
                if kids:
                    for child in sorted(kids, key=lambda e: e.line_start):
                        child_sig = child.signature or child.name or ""
                        child_loc = _md_loc(child)
                        child_kind = _md_kind(child)
                        child_vis = ""
                        if (child.visibility
                                and child.visibility not in ("pub", "public")):
                            child_vis = f" `{child.visibility}`"
                        child_doc = ""
                        child_doc_ln = ""
                        child_doxygen_markdown = []
                        if hasattr(child, 'doxygen_fields') and child.doxygen_fields:
                            child_doxygen_markdown = format_doxygen_fields_as_markdown(
                                child.doxygen_fields
                            )
                        elif include_legacy_annotations:
                            child_docs = doc_for_def.get(child.line_start, [])
                            if child_docs:
                                child_doc_text = _extract_comment_text(
                                    child_docs[0], max_length=100)
                                if child_doc_text:
                                    child_doc_ln = f" L{child_docs[0].line_start}>"
                                    child_doc = f" {child_doc_text}"
                        out.append(f"- {child_kind} `{child_sig}`"
                                   f"{child_vis} ({child_loc})"
                                   f"{child_doc_ln}{child_doc}")
                        if child_doxygen_markdown:
                            out.extend(f"  {line}" for line in child_doxygen_markdown)
                        # Child body annotations (indented)
                        if include_legacy_annotations:
                            _render_body_annotations(out, child, indent="  ")

                out.append("")
                i += 1

    # ── Standalone Comments (section/region markers, TODOs, notes) ────
    if include_legacy_annotations and standalone_comments:
        out.append("## Comments")
        # Group consecutive comments (within 2 lines of each other)
        groups = []
        current_group = [standalone_comments[0]]
        for c in standalone_comments[1:]:
            prev = current_group[-1]
            if c.line_start <= prev.line_end + 2:
                current_group.append(c)
            else:
                groups.append(current_group)
                current_group = [c]
        groups.append(current_group)

        for group in groups:
            if len(group) == 1:
                c = group[0]
                text = _extract_comment_text(c, max_length=150)
                if text:
                    out.append(f"- L{c.line_start}: {text}")
            else:
                # Multi-line comment block: show as region
                start_line = group[0].line_start
                end_line = group[-1].line_end
                texts = []
                for c in group:
                    t = _extract_comment_text(c, max_length=100)
                    if t:
                        texts.append(t)
                if texts:
                    out.append(f"- L{start_line}-{end_line}: "
                               + " | ".join(texts))
        out.append("")

    # ── Symbol Index ──────────────────────────────────────────────────
    indexable = sorted(
        [e for e in elements if e.element_type not in (
            ElementType.COMMENT_SINGLE, ElementType.COMMENT_MULTI,
            ElementType.IMPORT, ElementType.DECORATOR)],
        key=lambda e: e.line_start)

    if indexable:
        out.append("## Symbol Index")
        out.append("|Symbol|Kind|Vis|Lines|Sig|")
        out.append("|---|---|---|---|---|")
        for elem in indexable:
            name = elem.name or "?"
            if elem.parent_name:
                name = f"{elem.parent_name}.{name}"
            kind = _md_kind(elem)
            vis = elem.visibility or ""
            loc = (f"{elem.line_start}"
                   if elem.line_start == elem.line_end
                   else f"{elem.line_start}-{elem.line_end}")
            # Only show sig for functions/methods/classes (not vars/consts
            # which already show full content in Definitions section)
            sig = ""
            if (elem.element_type in (
                    ElementType.FUNCTION, ElementType.METHOD,
                    ElementType.CLASS, ElementType.STRUCT,
                    ElementType.TRAIT, ElementType.INTERFACE,
                    ElementType.IMPL, ElementType.ENUM)
                    and elem.signature
                    and elem.signature != elem.name):
                sig = elem.signature
                if len(sig) > 60:
                    sig = sig[:57] + "..."
            out.append(f"|`{name}`|{kind}|{vis}|{loc}|{sig}|")
        out.append("")

    return "\n".join(out)


def main():
    """! @brief Execute the standalone source analyzer CLI command."""
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a source file and extract definitions, comments "
            "and code structure. Inspired by tree-sitter."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Supported languages:\n"
            "  python, c, cpp, rust, javascript, typescript, java, go,\n"
            "  ruby, php, swift, kotlin, scala, lua, shell, perl,\n"
            "  haskell, zig, elixir, csharp\n"
            "\n"
            "Common aliases: py, js, ts, rs, rb, cs, sh, bash, kt, hs,\n"
            "                cc, cxx, h, hpp, ex, exs, pl, zsh\n"
            "\n"
            "Examples:\n"
            "  %(prog)s main.py python\n"
            "  %(prog)s server.js javascript\n"
            "  %(prog)s lib.rs rust\n"
            "  %(prog)s main.c c\n"
        ),
    )
    parser.add_argument(
        "file",
        help="Path to source file to analyze",
    )
    parser.add_argument(
        "language",
        help="File format/language (e.g.: python, c, rust, javascript)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Show only structured listing, without headers",
    )
    parser.add_argument(
        "-d", "--definitions-only",
        action="store_true",
        help="Show only definitions (without comments)",
    )
    parser.add_argument(
        "-c", "--comments-only",
        action="store_true",
        help="Show only comments",
    )
    parser.add_argument(
        "-m", "--markdown",
        action="store_true",
        help="Output in compact Markdown format optimized for LLM agent context",
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="Show supported languages and exit",
    )

    args = parser.parse_args()
    analyzer = SourceAnalyzer()

    if args.list_languages:
        print("Supported languages:")
        for lang in analyzer.get_supported_languages():
            spec = analyzer.specs[lang]
            print(f"  {lang:<14} ({spec.name})")
        sys.exit(0)

    try:
        elements = analyzer.analyze(args.file, args.language)
    except FileNotFoundError:
        print(f"Error: file '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Optional filtering
    if args.definitions_only:
        elements = [e for e in elements
                     if e.element_type not in (ElementType.COMMENT_SINGLE,
                                               ElementType.COMMENT_MULTI)]
    elif args.comments_only:
        elements = [e for e in elements
                     if e.element_type in (ElementType.COMMENT_SINGLE,
                                           ElementType.COMMENT_MULTI)]

    lang_key = args.language.lower().strip().lstrip(".")
    spec = analyzer.specs[lang_key]

    if args.definitions_only:
        elements = [e for e in elements
                    if e.element_type not in (ElementType.COMMENT_SINGLE,
                                              ElementType.COMMENT_MULTI)]
    if args.comments_only:
        elements = [e for e in elements
                    if e.element_type in (ElementType.COMMENT_SINGLE,
                                          ElementType.COMMENT_MULTI)]

    if args.markdown or not args.quiet:
        with open(args.file, "r", encoding="utf-8", errors="replace") as f:
            total_lines = sum(1 for _ in f)
        analyzer.enrich(elements, lang_key, filepath=args.file)
        output = format_markdown(
            elements, args.file, lang_key, spec.name, total_lines)
        print(output)
    elif args.quiet:
        sorted_elements = sorted(elements, key=lambda e: e.line_start)
        prev_line_end = None
        for elem in sorted_elements:
            if prev_line_end is not None and elem.line_start > prev_line_end + 1:
                print()
            name_str = f" {elem.name}" if elem.name and elem.name != "inline" else ""
            location = (f"L{elem.line_start}"
                        if elem.line_start == elem.line_end
                        else f"L{elem.line_start}-L{elem.line_end}")
            print(f"{elem.line_start:>6} | [{elem.type_label}]{name_str} {location}")
            first_line = elem.extract.split("\n")[0]
            if len(first_line) > 72:
                first_line = first_line[:69] + "..."
            print(f"       | {first_line}")
            prev_line_end = elem.line_end


if __name__ == "__main__":
    main()
