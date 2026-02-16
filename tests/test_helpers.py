"""Costanti e helper condivisi per la test suite di source_analyzer."""

import os
from collections import Counter

from usereq.source_analyzer import ElementType


# ── Mapping estensione -> linguaggio ──────────────────────────────────────
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".c": "c",
    ".cpp": "cpp",
    ".rs": "rust",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".lua": "lua",
    ".sh": "shell",
    ".pl": "perl",
    ".hs": "haskell",
    ".zig": "zig",
    ".ex": "elixir",
    ".cs": "csharp",
}

# ── Lista linguaggi canonici (senza alias) ────────────────────────────────
ALL_LANGUAGES = sorted(EXTENSION_TO_LANGUAGE.values())

# ── Alias noti ────────────────────────────────────────────────────────────
LANGUAGE_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "rs": "rust",
    "py": "python",
    "rb": "ruby",
    "hs": "haskell",
    "cc": "cpp",
    "cxx": "cpp",
    "h": "c",
    "hpp": "cpp",
    "kt": "kotlin",
    "ex": "elixir",
    "exs": "elixir",
    "pl": "perl",
    "cs": "csharp",
    "bash": "shell",
    "sh": "shell",
    "zsh": "shell",
}


# ── Conteggi attesi per tipo (calibrati sull'output reale) ────────────────
EXPECTED_COUNTS = {
    "python": {
        ElementType.CLASS: 7,
        ElementType.COMMENT_MULTI: 40,
        ElementType.COMMENT_SINGLE: 21,
        ElementType.DECORATOR: 9,
        ElementType.FUNCTION: 32,
        ElementType.IMPORT: 7,
        ElementType.VARIABLE: 3,
    },
    "c": {
        ElementType.COMMENT_MULTI: 64,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.ENUM: 1,
        ElementType.FUNCTION: 11,
        ElementType.IMPORT: 5,
        ElementType.MACRO: 6,
        ElementType.STRUCT: 3,
        ElementType.TYPEDEF: 2,
        ElementType.UNION: 1,
        ElementType.VARIABLE: 6,
    },
    "cpp": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 62,
        ElementType.COMMENT_SINGLE: 3,
        ElementType.ENUM: 1,
        ElementType.FUNCTION: 17,
        ElementType.IMPORT: 7,
        ElementType.MACRO: 2,
        ElementType.NAMESPACE: 2,
        ElementType.STRUCT: 1,
        ElementType.TYPE_ALIAS: 3,
    },
    "rust": {
        ElementType.COMMENT_MULTI: 17,
        ElementType.COMMENT_SINGLE: 113,
        ElementType.CONSTANT: 4,
        ElementType.DECORATOR: 2,
        ElementType.ENUM: 1,
        ElementType.FUNCTION: 18,
        ElementType.IMPL: 4,
        ElementType.IMPORT: 4,
        ElementType.MACRO: 2,
        ElementType.MODULE: 2,
        ElementType.STRUCT: 3,
        ElementType.TRAIT: 2,
        ElementType.TYPE_ALIAS: 3,
    },
    "javascript": {
        ElementType.CLASS: 2,
        ElementType.COMMENT_MULTI: 59,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.COMPONENT: 1,
        ElementType.CONSTANT: 2,
        ElementType.FUNCTION: 14,
        ElementType.IMPORT: 2,
        ElementType.MODULE: 1,
    },
    "typescript": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 73,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.DECORATOR: 1,
        ElementType.ENUM: 3,
        ElementType.FUNCTION: 9,
        ElementType.IMPORT: 2,
        ElementType.INTERFACE: 3,
        ElementType.MODULE: 1,
        ElementType.NAMESPACE: 1,
        ElementType.TYPE_ALIAS: 6,
    },
    "java": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 57,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 1,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 1,
        ElementType.FUNCTION: 23,
        ElementType.IMPORT: 7,
        ElementType.INTERFACE: 1,
        ElementType.MODULE: 1,
    },
    "go": {
        ElementType.COMMENT_MULTI: 14,
        ElementType.COMMENT_SINGLE: 81,
        ElementType.CONSTANT: 3,
        ElementType.FUNCTION: 8,
        ElementType.IMPORT: 1,
        ElementType.INTERFACE: 3,
        ElementType.METHOD: 3,
        ElementType.MODULE: 1,
        ElementType.STRUCT: 3,
        ElementType.TYPE_ALIAS: 2,
    },
    "ruby": {
        ElementType.CLASS: 3,
        ElementType.COMMENT_MULTI: 1,
        ElementType.COMMENT_SINGLE: 106,
        ElementType.CONSTANT: 2,
        ElementType.DECORATOR: 3,
        ElementType.FUNCTION: 20,
        ElementType.IMPORT: 3,
        ElementType.MODULE: 3,
    },
    "php": {
        ElementType.CLASS: 4,
        ElementType.COMMENT_MULTI: 57,
        ElementType.COMMENT_SINGLE: 5,
        ElementType.CONSTANT: 2,
        ElementType.FUNCTION: 24,
        ElementType.IMPORT: 6,
        ElementType.INTERFACE: 1,
        ElementType.NAMESPACE: 1,
        ElementType.TRAIT: 2,
    },
    "swift": {
        ElementType.CLASS: 3,
        ElementType.COMMENT_MULTI: 15,
        ElementType.COMMENT_SINGLE: 113,
        ElementType.CONSTANT: 7,
        ElementType.ENUM: 2,
        ElementType.EXTENSION: 2,
        ElementType.FUNCTION: 13,
        ElementType.IMPORT: 2,
        ElementType.PROTOCOL: 2,
        ElementType.STRUCT: 3,
        ElementType.VARIABLE: 16,
    },
    "kotlin": {
        ElementType.CLASS: 9,
        ElementType.COMMENT_MULTI: 68,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 9,
        ElementType.DECORATOR: 3,
        ElementType.ENUM: 1,
        ElementType.FUNCTION: 15,
        ElementType.IMPORT: 3,
        ElementType.INTERFACE: 1,
        ElementType.MODULE: 4,
        ElementType.VARIABLE: 2,
    },
    "scala": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 55,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 3,
        ElementType.FUNCTION: 25,
        ElementType.IMPORT: 3,
        ElementType.MODULE: 4,
        ElementType.TRAIT: 3,
        ElementType.TYPE_ALIAS: 2,
        ElementType.VARIABLE: 1,
    },
    "lua": {
        ElementType.COMMENT_MULTI: 1,
        ElementType.COMMENT_SINGLE: 82,
        ElementType.FUNCTION: 16,
        ElementType.VARIABLE: 13,
    },
    "shell": {
        ElementType.COMMENT_SINGLE: 63,
        ElementType.FUNCTION: 9,
        ElementType.IMPORT: 1,
        ElementType.VARIABLE: 11,
    },
    "perl": {
        ElementType.COMMENT_MULTI: 2,
        ElementType.COMMENT_SINGLE: 68,
        ElementType.FUNCTION: 14,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 1,
    },
    "haskell": {
        ElementType.CLASS: 2,
        ElementType.COMMENT_MULTI: 1,
        ElementType.COMMENT_SINGLE: 67,
        ElementType.FUNCTION: 11,
        ElementType.IMPORT: 4,
        ElementType.MODULE: 1,
        ElementType.STRUCT: 4,
        ElementType.TYPE_ALIAS: 3,
    },
    "zig": {
        ElementType.COMMENT_SINGLE: 99,
        ElementType.CONSTANT: 13,
        ElementType.ENUM: 2,
        ElementType.FUNCTION: 13,
        ElementType.STRUCT: 3,
        ElementType.UNION: 2,
        ElementType.VARIABLE: 3,
    },
    "elixir": {
        ElementType.COMMENT_SINGLE: 28,
        ElementType.FUNCTION: 27,
        ElementType.IMPL: 2,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 3,
        ElementType.PROTOCOL: 1,
        ElementType.STRUCT: 1,
    },
    "csharp": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 11,
        ElementType.COMMENT_SINGLE: 161,
        ElementType.CONSTANT: 1,
        ElementType.DECORATOR: 4,
        ElementType.ENUM: 1,
        ElementType.FUNCTION: 18,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 2,
        ElementType.NAMESPACE: 1,
        ElementType.PROPERTY: 6,
        ElementType.STRUCT: 1,
    },
}


# ── Elementi specifici attesi (lingua, tipo, nome, line_start) ────────────
EXPECTED_NAMED = [
    # Python
    ("python", ElementType.CLASS, "class MyClass:", 59),
    ("python", ElementType.FUNCTION, "def regular_function(", 276),
    ("python", ElementType.FUNCTION, "async def async_function(", 390),
    ("python", ElementType.IMPORT, "import os", 7),
    ("python", ElementType.VARIABLE, "MAX_RETRIES = ", 18),
    ("python", ElementType.DECORATOR, "dataclass", 25),
    # C
    ("c", ElementType.STRUCT, "struct Point", 59),
    ("c", ElementType.UNION, "union Data", 94),
    ("c", ElementType.ENUM, "enum Color", 106),
    ("c", ElementType.FUNCTION, "void greet(", 167),
    ("c", ElementType.FUNCTION, "int main(", 181),
    ("c", ElementType.MACRO, "#define MAX_SIZE", 19),
    ("c", ElementType.TYPEDEF, "typedef int my_int;", 48),
    # Rust
    ("rust", ElementType.STRUCT, "pub struct MyStruct", 20),
    ("rust", ElementType.ENUM, "pub enum MyEnum", 51),
    ("rust", ElementType.TRAIT, "pub trait MyTrait", 65),
    ("rust", ElementType.FUNCTION, "pub fn my_function", 240),
    ("rust", ElementType.FUNCTION, "pub async fn async_function", 254),
    ("rust", ElementType.MACRO, "macro_rules! hashmap", 196),
    ("rust", ElementType.MODULE, "pub mod my_module", 182),
    ("rust", ElementType.TYPE_ALIAS, "pub type MyAlias", 232),
    # JavaScript
    ("javascript", ElementType.CLASS, "class MyComponent", 20),
    ("javascript", ElementType.FUNCTION, "function greet(", 103),
    ("javascript", ElementType.FUNCTION, "async function fetchData(", 112),
    ("javascript", ElementType.FUNCTION, "const handler = (event) =>", 122),
    ("javascript", ElementType.COMPONENT, "const MyWrapped = React.memo(", 153),
    ("javascript", ElementType.MODULE, "const fs = require(", 297),
    # Go
    ("go", ElementType.STRUCT, "type Server struct", 39),
    ("go", ElementType.INTERFACE, "type Handler interface", 67),
    ("go", ElementType.FUNCTION, "func main(", 107),
    ("go", ElementType.METHOD, "func (s *Server) Start(", 119),
    # Swift
    ("swift", ElementType.CLASS, "class Animal", 16),
    ("swift", ElementType.STRUCT, "struct Point", 85),
    ("swift", ElementType.ENUM, "enum Direction", 140),
    ("swift", ElementType.PROTOCOL, "protocol Drawable", 186),
    ("swift", ElementType.EXTENSION, "extension Animal", 226),
    # Elixir
    ("elixir", ElementType.MODULE, "defmodule MyApp.Server", 10),
    ("elixir", ElementType.PROTOCOL, "defprotocol Printable", 187),
    ("elixir", ElementType.IMPL, "defimpl Printable", 204),
    # Haskell
    ("haskell", ElementType.MODULE, "module MyModule", 11),
    ("haskell", ElementType.TYPE_ALIAS, "type Name", 30),
    ("haskell", ElementType.STRUCT, "data Person", 42),
    ("haskell", ElementType.CLASS, "class Printable", 72),
    # C#
    ("csharp", ElementType.NAMESPACE, "namespace MyApp", 15),
    ("csharp", ElementType.CLASS, "public class Person", 53),
    ("csharp", ElementType.INTERFACE, "public interface IGreeter", 179),
    ("csharp", ElementType.STRUCT, "public readonly struct Point", 215),
    ("csharp", ElementType.ENUM, "public enum Color", 238),
]


# ── Helper functions ──────────────────────────────────────────────────────

def fixture_path(fixtures_dir, language):
    """Restituisce il percorso del file fixture per il linguaggio dato."""
    for ext, lang in EXTENSION_TO_LANGUAGE.items():
        if lang == language:
            return os.path.join(fixtures_dir, f"fixture_{language}{ext}")
    raise ValueError(f"Nessuna fixture per il linguaggio: {language}")


def language_from_extension(filepath):
    """Determina il linguaggio dall'estensione del file."""
    _, ext = os.path.splitext(filepath)
    return EXTENSION_TO_LANGUAGE.get(ext)


def filter_elements(elements, element_type=None, name=None):
    """Filtra elementi per tipo e/o nome."""
    result = elements
    if element_type is not None:
        result = [e for e in result if e.element_type == element_type]
    if name is not None:
        result = [e for e in result if e.name == name]
    return result


def count_by_type(elements):
    """Conta gli elementi per tipo."""
    return dict(Counter(e.element_type for e in elements))
