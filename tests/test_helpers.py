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
    "c": {
        ElementType.COMMENT_MULTI: 72,
        ElementType.COMMENT_SINGLE: 2,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 16,
        ElementType.IMPORT: 5,
        ElementType.MACRO: 6,
        ElementType.STRUCT: 6,
        ElementType.TYPEDEF: 5,
        ElementType.UNION: 5,
        ElementType.VARIABLE: 6,
    },
    "cpp": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 70,
        ElementType.COMMENT_SINGLE: 4,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 23,
        ElementType.IMPORT: 7,
        ElementType.MACRO: 5,
        ElementType.NAMESPACE: 5,
        ElementType.STRUCT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "csharp": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 12,
        ElementType.COMMENT_SINGLE: 188,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 23,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.NAMESPACE: 5,
        ElementType.PROPERTY: 6,
        ElementType.STRUCT: 5,
    },
    "elixir": {
        ElementType.COMMENT_SINGLE: 57,
        ElementType.FUNCTION: 40,
        ElementType.IMPL: 6,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 9,
        ElementType.PROTOCOL: 5,
        ElementType.STRUCT: 6,
    },
    "go": {
        ElementType.COMMENT_MULTI: 15,
        ElementType.COMMENT_SINGLE: 111,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 13,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.METHOD: 5,
        ElementType.MODULE: 5,
        ElementType.STRUCT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "haskell": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 2,
        ElementType.COMMENT_SINGLE: 94,
        ElementType.FUNCTION: 16,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
        ElementType.STRUCT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "java": {
        ElementType.CLASS: 7,
        ElementType.COMMENT_MULTI: 65,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 6,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 28,
        ElementType.IMPORT: 7,
        ElementType.INTERFACE: 5,
        ElementType.MODULE: 5,
    },
    "javascript": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 60,
        ElementType.COMMENT_SINGLE: 28,
        ElementType.COMPONENT: 5,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 19,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
    },
    "kotlin": {
        ElementType.CLASS: 9,
        ElementType.COMMENT_MULTI: 76,
        ElementType.COMMENT_SINGLE: 1,
        ElementType.CONSTANT: 9,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 20,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.MODULE: 5,
        ElementType.VARIABLE: 5,
    },
    "lua": {
        ElementType.COMMENT_MULTI: 1,
        ElementType.COMMENT_SINGLE: 109,
        ElementType.FUNCTION: 21,
        ElementType.VARIABLE: 13,
    },
    "perl": {
        ElementType.COMMENT_MULTI: 3,
        ElementType.COMMENT_SINGLE: 95,
        ElementType.CONSTANT: 6,
        ElementType.FUNCTION: 19,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
    },
    "php": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 65,
        ElementType.COMMENT_SINGLE: 5,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 29,
        ElementType.IMPORT: 6,
        ElementType.INTERFACE: 5,
        ElementType.NAMESPACE: 5,
        ElementType.TRAIT: 5,
    },
    "python": {
        ElementType.CLASS: 7,
        ElementType.COMMENT_MULTI: 41,
        ElementType.COMMENT_SINGLE: 58,
        ElementType.DECORATOR: 9,
        ElementType.FUNCTION: 37,
        ElementType.IMPORT: 7,
        ElementType.VARIABLE: 6,
    },
    "ruby": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 2,
        ElementType.COMMENT_SINGLE: 134,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 5,
        ElementType.FUNCTION: 25,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 5,
    },
    "rust": {
        ElementType.COMMENT_MULTI: 19,
        ElementType.COMMENT_SINGLE: 139,
        ElementType.CONSTANT: 5,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 23,
        ElementType.IMPL: 7,
        ElementType.IMPORT: 5,
        ElementType.MACRO: 5,
        ElementType.MODULE: 5,
        ElementType.STRUCT: 5,
        ElementType.TRAIT: 5,
        ElementType.TYPE_ALIAS: 5,
    },
    "scala": {
        ElementType.CLASS: 6,
        ElementType.COMMENT_MULTI: 62,
        ElementType.COMMENT_SINGLE: 2,
        ElementType.CONSTANT: 5,
        ElementType.FUNCTION: 30,
        ElementType.IMPORT: 5,
        ElementType.MODULE: 6,
        ElementType.TRAIT: 5,
        ElementType.TYPE_ALIAS: 5,
        ElementType.VARIABLE: 5,
    },
    "shell": {
        ElementType.COMMENT_SINGLE: 91,
        ElementType.FUNCTION: 14,
        ElementType.IMPORT: 5,
        ElementType.VARIABLE: 11,
    },
    "swift": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 16,
        ElementType.COMMENT_SINGLE: 140,
        ElementType.CONSTANT: 7,
        ElementType.ENUM: 5,
        ElementType.EXTENSION: 5,
        ElementType.FUNCTION: 18,
        ElementType.IMPORT: 7,
        ElementType.PROTOCOL: 5,
        ElementType.STRUCT: 5,
        ElementType.VARIABLE: 16,
    },
    "typescript": {
        ElementType.CLASS: 5,
        ElementType.COMMENT_MULTI: 74,
        ElementType.COMMENT_SINGLE: 28,
        ElementType.DECORATOR: 5,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 14,
        ElementType.IMPORT: 5,
        ElementType.INTERFACE: 5,
        ElementType.MODULE: 5,
        ElementType.NAMESPACE: 5,
        ElementType.TYPE_ALIAS: 6,
    },
    "zig": {
        ElementType.COMMENT_SINGLE: 127,
        ElementType.CONSTANT: 11,
        ElementType.ENUM: 5,
        ElementType.FUNCTION: 18,
        ElementType.IMPORT: 7,
        ElementType.STRUCT: 5,
        ElementType.UNION: 5,
        ElementType.VARIABLE: 5,
    },
}


# ── Elementi specifici attesi (lingua, tipo, nome, line_start) ────────────
EXPECTED_NAMED = [
    # Python
    ("python", ElementType.CLASS, "class MyClass:", 61),
    ("python", ElementType.FUNCTION, "def regular_function(", 286),
    ("python", ElementType.FUNCTION, "async def async_function(", 400),
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
    ("go", ElementType.STRUCT, "type Server struct", 43),
    ("go", ElementType.INTERFACE, "type Handler interface", 71),
    ("go", ElementType.FUNCTION, "func main(", 111),
    ("go", ElementType.METHOD, "func (s *Server) Start(", 123),
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
