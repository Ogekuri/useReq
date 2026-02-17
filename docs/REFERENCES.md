# Files Structure
```
.
└── src
    └── usereq
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── compress.py
        ├── compress_files.py
        ├── doxygen_parser.py
        ├── find_constructs.py
        ├── generate_markdown.py
        ├── pdoc_utils.py
        ├── source_analyzer.py
        └── token_counter.py
```

# __init__.py | Python | 27L | 0 symbols | 9 imports | 3 comments
> Path: `/home/ogekuri/useReq/src/usereq/__init__.py`

## Imports
```
from . import cli  # usereq.cli submodule
from . import pdoc_utils  # usereq.pdoc_utils submodule
from . import source_analyzer  # usereq.source_analyzer submodule
from . import token_counter  # usereq.token_counter submodule
from . import generate_markdown  # usereq.generate_markdown submodule
from . import compress  # usereq.compress submodule
from . import compress_files  # usereq.compress_files submodule
from . import find_constructs  # usereq.find_constructs submodule
from .cli import main  # re-export of CLI entry point
```


---

# __main__.py | Python | 17L | 0 symbols | 2 imports | 2 comments
> Path: `/home/ogekuri/useReq/src/usereq/__main__.py`

## Imports
```
from .cli import main
import sys
```


---

# cli.py | Python | 2537L | 94 symbols | 23 imports | 149 comments
> Path: `/home/ogekuri/useReq/src/usereq/cli.py`

## Imports
```
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import sys
import subprocess
import urllib.error
import urllib.request
from argparse import Namespace
from pathlib import Path
from typing import Any, Mapping, Optional
from .find_constructs import format_available_tags
import copy
from .token_counter import count_files_metrics, format_pack_summary
from .generate_markdown import generate_markdown
from .compress_files import compress_files
from .find_constructs import find_constructs_in_files
from .generate_markdown import generate_markdown
from .compress_files import compress_files
from .find_constructs import find_constructs_in_files
import traceback
```

## Definitions

- var `REPO_ROOT = Path(__file__).resolve().parents[2]` (L24)
- var `RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"` (L27)
- Brief: The absolute path to the repository root."""
- var `VERBOSE = False` (L30)
- Brief: The absolute path to the resources directory."""
- var `DEBUG = False` (L33)
- Brief: Whether verbose output is enabled."""
- var `REQUIREMENTS_TEMPLATE_NAME = "Requirements_Template.md"` (L36)
- Brief: Whether debug output is enabled."""
### class `class ReqError(Exception)` : Exception (L40-54)
- fn `def __init__(self, message: str, code: int = 1) -> None` `priv` (L45-54)
  - Brief: Dedicated exception for expected CLI errors.
  - Details: This exception is used to bubble up known error conditions that should be reported to the user without a stack trace.

### fn `def log(msg: str) -> None` (L55-61)

### fn `def dlog(msg: str) -> None` (L62-69)

### fn `def vlog(msg: str) -> None` (L70-77)

### fn `def _get_available_tags_help() -> str` `priv` (L78-89)

### fn `def build_parser() -> argparse.ArgumentParser` (L90-273)

### fn `def parse_args(argv: Optional[list[str]] = None) -> Namespace` (L274-281)

### fn `def load_package_version() -> str` (L282-294)

### fn `def maybe_print_version(argv: list[str]) -> bool` (L295-305)

### fn `def run_upgrade() -> None` (L306-329)

### fn `def run_uninstall() -> None` (L330-350)

### fn `def normalize_release_tag(tag: str) -> str` (L351-361)

### fn `def parse_version_tuple(version: str) -> tuple[int, ...] | None` (L362-386)

### fn `def is_newer_version(current: str, latest: str) -> bool` (L387-403)

### fn `def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None` (L404-445)

### fn `def ensure_doc_directory(path: str, project_base: Path) -> None` (L446-465)

### fn `def ensure_test_directory(path: str, project_base: Path) -> None` (L466-485)

### fn `def ensure_src_directory(path: str, project_base: Path) -> None` (L486-505)

### fn `def make_relative_if_contains_project(path_value: str, project_base: Path) -> str` (L506-545)

### fn `def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]` (L546-559)

### fn `def format_substituted_path(value: str) -> str` (L560-569)

### fn `def compute_sub_path(` (L570-571)

### fn `def save_config(` (L590-595)

### fn `def load_config(project_base: Path) -> dict[str, str | list[str]]` (L617-657)

### fn `def generate_guidelines_file_list(guidelines_dir: Path, project_base: Path) -> str` (L658-685)

### fn `def generate_guidelines_file_items(guidelines_dir: Path, project_base: Path) -> list[str]` (L686-714)

### fn `def upgrade_guidelines_templates(` (L715-716)

### fn `def make_relative_token(raw: str, keep_trailing: bool = False) -> str` (L748-759)

### fn `def ensure_relative(value: str, name: str, code: int) -> None` (L760-769)

### fn `def apply_replacements(text: str, replacements: Mapping[str, str]) -> str` (L770-777)

### fn `def write_text_file(dst: Path, text: str) -> None` (L778-784)

### fn `def copy_with_replacements(` (L785-786)

### fn `def normalize_description(value: str) -> str` (L795-805)

### fn `def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None` (L806-834)

### fn `def extract_frontmatter(content: str) -> tuple[str, str]` (L835-844)

### fn `def extract_description(frontmatter: str) -> str` (L845-853)

### fn `def extract_argument_hint(frontmatter: str) -> str` (L854-862)

### fn `def extract_purpose_first_bullet(body: str) -> str` (L863-883)

### fn `def json_escape(value: str) -> str` (L884-889)

### fn `def generate_kiro_resources(` (L890-893)

### fn `def render_kiro_agent(` (L913-922)

### fn `def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None` (L956-964)

### fn `def yaml_double_quote_escape(value: str) -> str` (L965-970)

### fn `def list_docs_templates() -> list[Path]` (L971-986)

### fn `def find_requirements_template(docs_templates: list[Path]) -> Path` (L987-1001)

### fn `def load_kiro_template() -> tuple[str, dict[str, Any]]` (L1002-1036)

### fn `def strip_json_comments(text: str) -> str` (L1037-1057)

### fn `def load_settings(path: Path) -> dict[str, Any]` (L1058-1069)

### fn `def load_centralized_models(` (L1070-1073)

### fn `def get_model_tools_for_prompt(` (L1117-1118)

### fn `def get_raw_tools_for_prompt(config: dict[str, Any] | None, prompt_name: str) -> Any` (L1153-1170)

### fn `def format_tools_inline_list(tools: list[str]) -> str` (L1171-1178)

### fn `def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]` (L1179-1189)

### fn `def find_vscode_settings_source() -> Optional[Path]` (L1190-1198)

### fn `def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]` (L1199-1209)

### fn `def ensure_wrapped(target: Path, project_base: Path, code: int) -> None` (L1210-1219)

### fn `def save_vscode_backup(req_root: Path, settings_path: Path) -> None` (L1220-1229)

### fn `def restore_vscode_settings(project_base: Path) -> None` (L1230-1241)

### fn `def prune_empty_dirs(root: Path) -> None` (L1242-1255)

### fn `def remove_generated_resources(project_base: Path) -> None` (L1256-1296)

### fn `def run_remove(args: Namespace) -> None` (L1297-1343)

### fn `def run(args: Namespace) -> None` (L1344-1543)

- var `VERBOSE = args.verbose` (L1348)
- Brief: Handles the main initialization flow.
- var `DEBUG = args.debug` (L1349)
- var `PROMPT = prompt_path.stem` (L1691)
### fn `def _format_install_table(` `priv` (L2121-2123)

### fn `def fmt(row: tuple[str, ...]) -> str` (L2144-2146)

- var `EXCLUDED_DIRS = frozenset({` (L2164)
- var `SUPPORTED_EXTENSIONS = frozenset({` (L2173)
### fn `def _collect_source_files(src_dirs: list[str], project_base: Path) -> list[str]` `priv` (L2181-2201)

### fn `def _build_ascii_tree(paths: list[str]) -> str` `priv` (L2202-2239)

### fn `def _emit(` `priv` (L2224-2226)

### fn `def _format_files_structure_markdown(files: list[str], project_base: Path) -> str` `priv` (L2240-2250)

### fn `def _is_standalone_command(args: Namespace) -> bool` `priv` (L2251-2261)

### fn `def _is_project_scan_command(args: Namespace) -> bool` `priv` (L2262-2272)

### fn `def run_files_tokens(files: list[str]) -> None` (L2273-2291)

### fn `def run_files_references(files: list[str]) -> None` (L2292-2300)

### fn `def run_files_compress(files: list[str], enable_line_numbers: bool = False) -> None` (L2301-2315)

### fn `def run_files_find(args_list: list[str], enable_line_numbers: bool = False) -> None` (L2316-2341)

### fn `def run_references(args: Namespace) -> None` (L2342-2355)

### fn `def run_compress_cmd(args: Namespace) -> None` (L2356-2373)

### fn `def run_find(args: Namespace) -> None` (L2374-2400)

### fn `def run_tokens(args: Namespace) -> None` (L2401-2423)

### fn `def _resolve_project_base(args: Namespace) -> Path` `priv` (L2424-2444)

### fn `def _resolve_project_src_dirs(args: Namespace) -> tuple[Path, list[str]]` `priv` (L2445-2471)

### fn `def main(argv: Optional[list[str]] = None) -> int` (L2472-2537)

- var `VERBOSE = getattr(args, "verbose", False)` (L2491)
- var `DEBUG = getattr(args, "debug", False)` (L2492)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REPO_ROOT`|var|pub|24||
|`RESOURCE_ROOT`|var|pub|27||
|`VERBOSE`|var|pub|30||
|`DEBUG`|var|pub|33||
|`REQUIREMENTS_TEMPLATE_NAME`|var|pub|36||
|`ReqError`|class|pub|40-54|class ReqError(Exception)|
|`ReqError.__init__`|fn|priv|45-54|def __init__(self, message: str, code: int = 1) -> None|
|`log`|fn|pub|55-61|def log(msg: str) -> None|
|`dlog`|fn|pub|62-69|def dlog(msg: str) -> None|
|`vlog`|fn|pub|70-77|def vlog(msg: str) -> None|
|`_get_available_tags_help`|fn|priv|78-89|def _get_available_tags_help() -> str|
|`build_parser`|fn|pub|90-273|def build_parser() -> argparse.ArgumentParser|
|`parse_args`|fn|pub|274-281|def parse_args(argv: Optional[list[str]] = None) -> Names...|
|`load_package_version`|fn|pub|282-294|def load_package_version() -> str|
|`maybe_print_version`|fn|pub|295-305|def maybe_print_version(argv: list[str]) -> bool|
|`run_upgrade`|fn|pub|306-329|def run_upgrade() -> None|
|`run_uninstall`|fn|pub|330-350|def run_uninstall() -> None|
|`normalize_release_tag`|fn|pub|351-361|def normalize_release_tag(tag: str) -> str|
|`parse_version_tuple`|fn|pub|362-386|def parse_version_tuple(version: str) -> tuple[int, ...] ...|
|`is_newer_version`|fn|pub|387-403|def is_newer_version(current: str, latest: str) -> bool|
|`maybe_notify_newer_version`|fn|pub|404-445|def maybe_notify_newer_version(timeout_seconds: float = 1...|
|`ensure_doc_directory`|fn|pub|446-465|def ensure_doc_directory(path: str, project_base: Path) -...|
|`ensure_test_directory`|fn|pub|466-485|def ensure_test_directory(path: str, project_base: Path) ...|
|`ensure_src_directory`|fn|pub|486-505|def ensure_src_directory(path: str, project_base: Path) -...|
|`make_relative_if_contains_project`|fn|pub|506-545|def make_relative_if_contains_project(path_value: str, pr...|
|`resolve_absolute`|fn|pub|546-559|def resolve_absolute(normalized: str, project_base: Path)...|
|`format_substituted_path`|fn|pub|560-569|def format_substituted_path(value: str) -> str|
|`compute_sub_path`|fn|pub|570-571|def compute_sub_path(|
|`save_config`|fn|pub|590-595|def save_config(|
|`load_config`|fn|pub|617-657|def load_config(project_base: Path) -> dict[str, str | li...|
|`generate_guidelines_file_list`|fn|pub|658-685|def generate_guidelines_file_list(guidelines_dir: Path, p...|
|`generate_guidelines_file_items`|fn|pub|686-714|def generate_guidelines_file_items(guidelines_dir: Path, ...|
|`upgrade_guidelines_templates`|fn|pub|715-716|def upgrade_guidelines_templates(|
|`make_relative_token`|fn|pub|748-759|def make_relative_token(raw: str, keep_trailing: bool = F...|
|`ensure_relative`|fn|pub|760-769|def ensure_relative(value: str, name: str, code: int) -> ...|
|`apply_replacements`|fn|pub|770-777|def apply_replacements(text: str, replacements: Mapping[s...|
|`write_text_file`|fn|pub|778-784|def write_text_file(dst: Path, text: str) -> None|
|`copy_with_replacements`|fn|pub|785-786|def copy_with_replacements(|
|`normalize_description`|fn|pub|795-805|def normalize_description(value: str) -> str|
|`md_to_toml`|fn|pub|806-834|def md_to_toml(md_path: Path, toml_path: Path, force: boo...|
|`extract_frontmatter`|fn|pub|835-844|def extract_frontmatter(content: str) -> tuple[str, str]|
|`extract_description`|fn|pub|845-853|def extract_description(frontmatter: str) -> str|
|`extract_argument_hint`|fn|pub|854-862|def extract_argument_hint(frontmatter: str) -> str|
|`extract_purpose_first_bullet`|fn|pub|863-883|def extract_purpose_first_bullet(body: str) -> str|
|`json_escape`|fn|pub|884-889|def json_escape(value: str) -> str|
|`generate_kiro_resources`|fn|pub|890-893|def generate_kiro_resources(|
|`render_kiro_agent`|fn|pub|913-922|def render_kiro_agent(|
|`replace_tokens`|fn|pub|956-964|def replace_tokens(path: Path, replacements: Mapping[str,...|
|`yaml_double_quote_escape`|fn|pub|965-970|def yaml_double_quote_escape(value: str) -> str|
|`list_docs_templates`|fn|pub|971-986|def list_docs_templates() -> list[Path]|
|`find_requirements_template`|fn|pub|987-1001|def find_requirements_template(docs_templates: list[Path]...|
|`load_kiro_template`|fn|pub|1002-1036|def load_kiro_template() -> tuple[str, dict[str, Any]]|
|`strip_json_comments`|fn|pub|1037-1057|def strip_json_comments(text: str) -> str|
|`load_settings`|fn|pub|1058-1069|def load_settings(path: Path) -> dict[str, Any]|
|`load_centralized_models`|fn|pub|1070-1073|def load_centralized_models(|
|`get_model_tools_for_prompt`|fn|pub|1117-1118|def get_model_tools_for_prompt(|
|`get_raw_tools_for_prompt`|fn|pub|1153-1170|def get_raw_tools_for_prompt(config: dict[str, Any] | Non...|
|`format_tools_inline_list`|fn|pub|1171-1178|def format_tools_inline_list(tools: list[str]) -> str|
|`deep_merge_dict`|fn|pub|1179-1189|def deep_merge_dict(base: dict[str, Any], incoming: dict[...|
|`find_vscode_settings_source`|fn|pub|1190-1198|def find_vscode_settings_source() -> Optional[Path]|
|`build_prompt_recommendations`|fn|pub|1199-1209|def build_prompt_recommendations(prompts_dir: Path) -> di...|
|`ensure_wrapped`|fn|pub|1210-1219|def ensure_wrapped(target: Path, project_base: Path, code...|
|`save_vscode_backup`|fn|pub|1220-1229|def save_vscode_backup(req_root: Path, settings_path: Pat...|
|`restore_vscode_settings`|fn|pub|1230-1241|def restore_vscode_settings(project_base: Path) -> None|
|`prune_empty_dirs`|fn|pub|1242-1255|def prune_empty_dirs(root: Path) -> None|
|`remove_generated_resources`|fn|pub|1256-1296|def remove_generated_resources(project_base: Path) -> None|
|`run_remove`|fn|pub|1297-1343|def run_remove(args: Namespace) -> None|
|`run`|fn|pub|1344-1543|def run(args: Namespace) -> None|
|`VERBOSE`|var|pub|1348||
|`DEBUG`|var|pub|1349||
|`PROMPT`|var|pub|1691||
|`_format_install_table`|fn|priv|2121-2123|def _format_install_table(|
|`fmt`|fn|pub|2144-2146|def fmt(row: tuple[str, ...]) -> str|
|`EXCLUDED_DIRS`|var|pub|2164||
|`SUPPORTED_EXTENSIONS`|var|pub|2173||
|`_collect_source_files`|fn|priv|2181-2201|def _collect_source_files(src_dirs: list[str], project_ba...|
|`_build_ascii_tree`|fn|priv|2202-2239|def _build_ascii_tree(paths: list[str]) -> str|
|`_emit`|fn|priv|2224-2226|def _emit(|
|`_format_files_structure_markdown`|fn|priv|2240-2250|def _format_files_structure_markdown(files: list[str], pr...|
|`_is_standalone_command`|fn|priv|2251-2261|def _is_standalone_command(args: Namespace) -> bool|
|`_is_project_scan_command`|fn|priv|2262-2272|def _is_project_scan_command(args: Namespace) -> bool|
|`run_files_tokens`|fn|pub|2273-2291|def run_files_tokens(files: list[str]) -> None|
|`run_files_references`|fn|pub|2292-2300|def run_files_references(files: list[str]) -> None|
|`run_files_compress`|fn|pub|2301-2315|def run_files_compress(files: list[str], enable_line_numb...|
|`run_files_find`|fn|pub|2316-2341|def run_files_find(args_list: list[str], enable_line_numb...|
|`run_references`|fn|pub|2342-2355|def run_references(args: Namespace) -> None|
|`run_compress_cmd`|fn|pub|2356-2373|def run_compress_cmd(args: Namespace) -> None|
|`run_find`|fn|pub|2374-2400|def run_find(args: Namespace) -> None|
|`run_tokens`|fn|pub|2401-2423|def run_tokens(args: Namespace) -> None|
|`_resolve_project_base`|fn|priv|2424-2444|def _resolve_project_base(args: Namespace) -> Path|
|`_resolve_project_src_dirs`|fn|priv|2445-2471|def _resolve_project_src_dirs(args: Namespace) -> tuple[P...|
|`main`|fn|pub|2472-2537|def main(argv: Optional[list[str]] = None) -> int|
|`VERBOSE`|var|pub|2491||
|`DEBUG`|var|pub|2492||


---

# compress.py | Python | 386L | 11 symbols | 5 imports | 41 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress.py`

## Imports
```
import os
import re
import sys
from .source_analyzer import build_language_specs
import argparse
```

## Definitions

- var `EXT_LANG_MAP = {` (L17)
- var `INDENT_SIGNIFICANT = {"python", "haskell", "elixir"}` (L29)
### fn `def _get_specs()` `priv` (L36-46)

### fn `def detect_language(filepath: str) -> str | None` (L47-56)

### fn `def _is_in_string(line: str, pos: int, string_delimiters: tuple) -> bool` `priv` (L57-98)

### fn `def _remove_inline_comment(line: str, single_comment: str,` `priv` (L99-142)

### fn `def _is_python_docstring_line(line: str) -> bool` `priv` (L143-154)

### fn `def _format_result(entries: list[tuple[int, str]],` `priv` (L155-166)

### fn `def compress_source(source: str, language: str,` (L167-334)

### fn `def compress_file(filepath: str, language: str | None = None,` (L335-356)

### fn `def main()` (L357-384)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|17||
|`INDENT_SIGNIFICANT`|var|pub|29||
|`_get_specs`|fn|priv|36-46|def _get_specs()|
|`detect_language`|fn|pub|47-56|def detect_language(filepath: str) -> str | None|
|`_is_in_string`|fn|priv|57-98|def _is_in_string(line: str, pos: int, string_delimiters:...|
|`_remove_inline_comment`|fn|priv|99-142|def _remove_inline_comment(line: str, single_comment: str,|
|`_is_python_docstring_line`|fn|priv|143-154|def _is_python_docstring_line(line: str) -> bool|
|`_format_result`|fn|priv|155-166|def _format_result(entries: list[tuple[int, str]],|
|`compress_source`|fn|pub|167-334|def compress_source(source: str, language: str,|
|`compress_file`|fn|pub|335-356|def compress_file(filepath: str, language: str | None = N...|
|`main`|fn|pub|357-384|def main()|


---

# compress_files.py | Python | 113L | 3 symbols | 4 imports | 5 comments
> Path: `/home/ogekuri/useReq/src/usereq/compress_files.py`

## Imports
```
import os
import sys
from .compress import compress_file, detect_language
import argparse
```

## Definitions

### fn `def _extract_line_range(compressed_with_line_numbers: str) -> tuple[int, int]` `priv` (L16-33)

### fn `def compress_files(filepaths: list[str],` (L34-90)

### fn `def main()` (L91-111)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_extract_line_range`|fn|priv|16-33|def _extract_line_range(compressed_with_line_numbers: str...|
|`compress_files`|fn|pub|34-90|def compress_files(filepaths: list[str],|
|`main`|fn|pub|91-111|def main()|


---

# doxygen_parser.py | Python | 163L | 5 symbols | 2 imports | 19 comments
> Path: `/home/ogekuri/useReq/src/usereq/doxygen_parser.py`

## Imports
```
import re
from typing import Dict, List
```

## Definitions

- var `DOXYGEN_TAGS = [` (L15)
### fn `def parse_doxygen_comment(comment_text: str) -> Dict[str, List[str]]` (L35-91)

### fn `def _strip_comment_delimiters(text: str) -> str` `priv` (L92-120)

### fn `def _normalize_whitespace(text: str) -> str` `priv` (L121-146)

### fn `def format_doxygen_fields_as_markdown(doxygen_fields: Dict[str, List[str]]) -> List[str]` (L147-163)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`DOXYGEN_TAGS`|var|pub|15||
|`parse_doxygen_comment`|fn|pub|35-91|def parse_doxygen_comment(comment_text: str) -> Dict[str,...|
|`_strip_comment_delimiters`|fn|priv|92-120|def _strip_comment_delimiters(text: str) -> str|
|`_normalize_whitespace`|fn|priv|121-146|def _normalize_whitespace(text: str) -> str|
|`format_doxygen_fields_as_markdown`|fn|pub|147-163|def format_doxygen_fields_as_markdown(doxygen_fields: Dic...|


---

# find_constructs.py | Python | 262L | 8 symbols | 8 imports | 15 comments
> Path: `/home/ogekuri/useReq/src/usereq/find_constructs.py`

## Imports
```
import os
import re
import sys
from pathlib import Path
from .source_analyzer import SourceAnalyzer
from .compress import detect_language
from .doxygen_parser import format_doxygen_fields_as_markdown
import argparse
```

## Definitions

- var `LANGUAGE_TAGS = {` (L20)
### fn `def format_available_tags() -> str` (L44-57)

### fn `def parse_tag_filter(tag_string: str) -> set[str]` (L58-66)

### fn `def language_supports_tags(lang: str, tag_set: set[str]) -> bool` (L67-77)

### fn `def construct_matches(element, tag_set: set[str], pattern: str) -> bool` (L78-95)

### fn `def format_construct(element, source_lines: list[str], include_line_numbers: bool) -> str` (L96-131)

### fn `def find_constructs_in_files(` (L132-137)

### fn `def main()` (L225-260)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`LANGUAGE_TAGS`|var|pub|20||
|`format_available_tags`|fn|pub|44-57|def format_available_tags() -> str|
|`parse_tag_filter`|fn|pub|58-66|def parse_tag_filter(tag_string: str) -> set[str]|
|`language_supports_tags`|fn|pub|67-77|def language_supports_tags(lang: str, tag_set: set[str]) ...|
|`construct_matches`|fn|pub|78-95|def construct_matches(element, tag_set: set[str], pattern...|
|`format_construct`|fn|pub|96-131|def format_construct(element, source_lines: list[str], in...|
|`find_constructs_in_files`|fn|pub|132-137|def find_constructs_in_files(|
|`main`|fn|pub|225-260|def main()|


---

# generate_markdown.py | Python | 134L | 4 symbols | 3 imports | 7 comments
> Path: `/home/ogekuri/useReq/src/usereq/generate_markdown.py`

## Imports
```
import os
import sys
from .source_analyzer import SourceAnalyzer, format_markdown
```

## Definitions

- var `EXT_LANG_MAP = {` (L16)
### fn `def detect_language(filepath: str) -> str | None` (L43-52)

### fn `def generate_markdown(filepaths: list[str], verbose: bool = False) -> str` (L53-115)

### fn `def main()` (L116-132)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_LANG_MAP`|var|pub|16||
|`detect_language`|fn|pub|43-52|def detect_language(filepath: str) -> str | None|
|`generate_markdown`|fn|pub|53-115|def generate_markdown(filepaths: list[str], verbose: bool...|
|`main`|fn|pub|116-132|def main()|


---

# pdoc_utils.py | Python | 98L | 3 symbols | 6 imports | 5 comments
> Path: `/home/ogekuri/useReq/src/usereq/pdoc_utils.py`

## Imports
```
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence
```

## Definitions

### fn `def _normalize_modules(modules: str | Iterable[str]) -> list[str]` `priv` (L18-27)

### fn `def _run_pdoc(command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess` `priv` (L28-45)

### fn `def generate_pdoc_docs(` (L46-50)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_normalize_modules`|fn|priv|18-27|def _normalize_modules(modules: str | Iterable[str]) -> l...|
|`_run_pdoc`|fn|priv|28-45|def _run_pdoc(command: list[str], *, env: dict[str, str],...|
|`generate_pdoc_docs`|fn|pub|46-50|def generate_pdoc_docs(|


---

# source_analyzer.py | Python | 2018L | 57 symbols | 11 imports | 128 comments
> Path: `/home/ogekuri/useReq/src/usereq/source_analyzer.py`

## Imports
```
import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from .doxygen_parser import parse_doxygen_comment
from doxygen_parser import parse_doxygen_comment
from .doxygen_parser import format_doxygen_fields_as_markdown
from doxygen_parser import format_doxygen_fields_as_markdown
```

## Definitions

### class `class ElementType(Enum)` : Enum (L24-54)
- var `FUNCTION = auto()` (L28)
  - Brief: Element types recognized in source code.
  - Details: Enumeration of all supported syntactic constructs across languages.
- var `METHOD = auto()` (L29)
  - Brief: Element types recognized in source code.
  - Details: Enumeration of all supported syntactic constructs across languages.
- var `CLASS = auto()` (L30)
- var `STRUCT = auto()` (L31)
- var `ENUM = auto()` (L32)
- var `TRAIT = auto()` (L33)
- var `INTERFACE = auto()` (L34)
- var `MODULE = auto()` (L35)
- var `IMPL = auto()` (L36)
- var `MACRO = auto()` (L37)
- var `CONSTANT = auto()` (L38)
- var `VARIABLE = auto()` (L39)
- var `TYPE_ALIAS = auto()` (L40)
- var `IMPORT = auto()` (L41)
- var `DECORATOR = auto()` (L42)
- var `COMMENT_SINGLE = auto()` (L43)
- var `COMMENT_MULTI = auto()` (L44)
- var `COMPONENT = auto()` (L45)
- var `PROTOCOL = auto()` (L46)
- var `EXTENSION = auto()` (L47)
- var `UNION = auto()` (L48)
- var `NAMESPACE = auto()` (L49)
- var `PROPERTY = auto()` (L50)
- var `SIGNAL = auto()` (L51)
- var `TYPEDEF = auto()` (L52)

### class `class SourceElement` `@dataclass` (L56-109)
- fn `def type_label(self) -> str` (L75-109)

### class `class LanguageSpec` `@dataclass` (L111-122)

### fn `def build_language_specs() -> dict` (L123-322)

### class `class SourceAnalyzer` (L676-875)
- fn `def __init__(self)` `priv` (L681-684)
  - Brief: Multi-language source file analyzer.
  - Details: Analyzes a source file identifying definitions, comments and constructs for the specified language. Produces structured output with line numbers, inspired by tree-sitter tags functionality.
- fn `def get_supported_languages(self) -> list` (L685-696)
- fn `def analyze(self, filepath: str, language: str) -> list` (L697-850)

### fn `def _in_string_context(self, line: str, pos: int, spec: LanguageSpec) -> bool` `priv` (L851-884)

### fn `def _find_comment(self, line: str, spec: LanguageSpec) -> Optional[int]` `priv` (L885-922)

### fn `def _find_block_end(self, lines: list, start_idx: int,` `priv` (L923-1001)

### fn `def enrich(self, elements: list, language: str,` (L1004-1019)

### fn `def _clean_names(self, elements: list, language: str)` `priv` (L1020-1045)

### fn `def _extract_signatures(self, elements: list, language: str)` `priv` (L1046-1061)

### fn `def _detect_hierarchy(self, elements: list)` `priv` (L1062-1095)

### fn `def _extract_visibility(self, elements: list, language: str)` `priv` (L1096-1108)

### fn `def _parse_visibility(self, sig: str, name: Optional[str],` `priv` (L1109-1154)

### fn `def _extract_inheritance(self, elements: list, language: str)` `priv` (L1155-1166)

### fn `def _parse_inheritance(self, first_line: str,` `priv` (L1167-1196)

### fn `def _extract_body_annotations(self, elements: list,` `priv` (L1204-1327)

### fn `def _extract_doxygen_fields(self, elements: list)` `priv` (L1328-1387)

### fn `def _is_postfix_doxygen_comment(comment_text: str) -> bool` `priv` `@staticmethod` (L1389-1398)

### fn `def _clean_comment_line(text: str, spec) -> str` `priv` `@staticmethod` (L1400-1411)

### fn `def _md_loc(elem) -> str` `priv` (L1412-1419)

### fn `def _md_kind(elem) -> str` `priv` (L1420-1447)

### fn `def _extract_comment_text(comment_elem, max_length: int = 0) -> str` `priv` (L1448-1470)

### fn `def _extract_comment_lines(comment_elem) -> list` `priv` (L1471-1487)

### fn `def _build_comment_maps(elements: list) -> tuple` `priv` (L1488-1548)

### fn `def _render_body_annotations(out: list, elem, indent: str = "",` `priv` (L1549-1600)

### fn `def format_markdown(` (L1601-1607)

### fn `def main()` (L1893-2016)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ElementType`|class|pub|24-54|class ElementType(Enum)|
|`ElementType.FUNCTION`|var|pub|28||
|`ElementType.METHOD`|var|pub|29||
|`ElementType.CLASS`|var|pub|30||
|`ElementType.STRUCT`|var|pub|31||
|`ElementType.ENUM`|var|pub|32||
|`ElementType.TRAIT`|var|pub|33||
|`ElementType.INTERFACE`|var|pub|34||
|`ElementType.MODULE`|var|pub|35||
|`ElementType.IMPL`|var|pub|36||
|`ElementType.MACRO`|var|pub|37||
|`ElementType.CONSTANT`|var|pub|38||
|`ElementType.VARIABLE`|var|pub|39||
|`ElementType.TYPE_ALIAS`|var|pub|40||
|`ElementType.IMPORT`|var|pub|41||
|`ElementType.DECORATOR`|var|pub|42||
|`ElementType.COMMENT_SINGLE`|var|pub|43||
|`ElementType.COMMENT_MULTI`|var|pub|44||
|`ElementType.COMPONENT`|var|pub|45||
|`ElementType.PROTOCOL`|var|pub|46||
|`ElementType.EXTENSION`|var|pub|47||
|`ElementType.UNION`|var|pub|48||
|`ElementType.NAMESPACE`|var|pub|49||
|`ElementType.PROPERTY`|var|pub|50||
|`ElementType.SIGNAL`|var|pub|51||
|`ElementType.TYPEDEF`|var|pub|52||
|`SourceElement`|class|pub|56-109|class SourceElement|
|`SourceElement.type_label`|fn|pub|75-109|def type_label(self) -> str|
|`LanguageSpec`|class|pub|111-122|class LanguageSpec|
|`build_language_specs`|fn|pub|123-322|def build_language_specs() -> dict|
|`SourceAnalyzer`|class|pub|676-875|class SourceAnalyzer|
|`SourceAnalyzer.__init__`|fn|priv|681-684|def __init__(self)|
|`SourceAnalyzer.get_supported_languages`|fn|pub|685-696|def get_supported_languages(self) -> list|
|`SourceAnalyzer.analyze`|fn|pub|697-850|def analyze(self, filepath: str, language: str) -> list|
|`_in_string_context`|fn|priv|851-884|def _in_string_context(self, line: str, pos: int, spec: L...|
|`_find_comment`|fn|priv|885-922|def _find_comment(self, line: str, spec: LanguageSpec) ->...|
|`_find_block_end`|fn|priv|923-1001|def _find_block_end(self, lines: list, start_idx: int,|
|`enrich`|fn|pub|1004-1019|def enrich(self, elements: list, language: str,|
|`_clean_names`|fn|priv|1020-1045|def _clean_names(self, elements: list, language: str)|
|`_extract_signatures`|fn|priv|1046-1061|def _extract_signatures(self, elements: list, language: str)|
|`_detect_hierarchy`|fn|priv|1062-1095|def _detect_hierarchy(self, elements: list)|
|`_extract_visibility`|fn|priv|1096-1108|def _extract_visibility(self, elements: list, language: str)|
|`_parse_visibility`|fn|priv|1109-1154|def _parse_visibility(self, sig: str, name: Optional[str],|
|`_extract_inheritance`|fn|priv|1155-1166|def _extract_inheritance(self, elements: list, language: ...|
|`_parse_inheritance`|fn|priv|1167-1196|def _parse_inheritance(self, first_line: str,|
|`_extract_body_annotations`|fn|priv|1204-1327|def _extract_body_annotations(self, elements: list,|
|`_extract_doxygen_fields`|fn|priv|1328-1387|def _extract_doxygen_fields(self, elements: list)|
|`_is_postfix_doxygen_comment`|fn|priv|1389-1398|def _is_postfix_doxygen_comment(comment_text: str) -> bool|
|`_clean_comment_line`|fn|priv|1400-1411|def _clean_comment_line(text: str, spec) -> str|
|`_md_loc`|fn|priv|1412-1419|def _md_loc(elem) -> str|
|`_md_kind`|fn|priv|1420-1447|def _md_kind(elem) -> str|
|`_extract_comment_text`|fn|priv|1448-1470|def _extract_comment_text(comment_elem, max_length: int =...|
|`_extract_comment_lines`|fn|priv|1471-1487|def _extract_comment_lines(comment_elem) -> list|
|`_build_comment_maps`|fn|priv|1488-1548|def _build_comment_maps(elements: list) -> tuple|
|`_render_body_annotations`|fn|priv|1549-1600|def _render_body_annotations(out: list, elem, indent: str...|
|`format_markdown`|fn|pub|1601-1607|def format_markdown(|
|`main`|fn|pub|1893-2016|def main()|


---

# token_counter.py | Python | 116L | 7 symbols | 2 imports | 8 comments
> Path: `/home/ogekuri/useReq/src/usereq/token_counter.py`

## Imports
```
import os
import tiktoken
```

## Definitions

### class `class TokenCounter` (L14-44)
- fn `def __init__(self, encoding_name: str = "cl100k_base")` `priv` (L19-24)
  - Brief: Count tokens using tiktoken encoding (cl100k_base by default).
  - Details: Wrapper around tiktoken encoding to simplify token counting operations.
- fn `def count_tokens(self, content: str) -> int` (L25-35)
- fn `def count_chars(content: str) -> int` (L37-44)

### fn `def count_file_metrics(content: str,` (L45-58)

### fn `def count_files_metrics(file_paths: list,` (L59-87)

### fn `def format_pack_summary(results: list) -> str` (L88-116)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`TokenCounter`|class|pub|14-44|class TokenCounter|
|`TokenCounter.__init__`|fn|priv|19-24|def __init__(self, encoding_name: str = "cl100k_base")|
|`TokenCounter.count_tokens`|fn|pub|25-35|def count_tokens(self, content: str) -> int|
|`TokenCounter.count_chars`|fn|pub|37-44|def count_chars(content: str) -> int|
|`count_file_metrics`|fn|pub|45-58|def count_file_metrics(content: str,|
|`count_files_metrics`|fn|pub|59-87|def count_files_metrics(file_paths: list,|
|`format_pack_summary`|fn|pub|88-116|def format_pack_summary(results: list) -> str|

