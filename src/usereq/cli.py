"""Command-line entry point that implements the useReq initialization workflow."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any, Mapping, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"
VERBOSE = False
DEBUG = False


class ReqError(Exception):
    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


def log(msg: str) -> None:
    print(msg)


def dlog(msg: str) -> None:
    if DEBUG:
        print("DEBUG:", msg)


def vlog(msg: str) -> None:
    if VERBOSE:
        print(msg)


def parse_args(argv: Optional[list[str]] = None) -> Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a project with useReq resources."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--base", type=Path, help="Directory root of the project to update.")
    group.add_argument("--here", action="store_true", help="Use current working directory as the project root.")
    parser.add_argument("--doc", required=True, help="Markdown requirements document relative to the project root.")
    parser.add_argument("--dir", required=True, help="Technical directory relative to the project root.")
    parser.add_argument("--verbose", action="store_true", help="Show verbose progress messages.")
    parser.add_argument("--debug", action="store_true", help="Show debug logs for diagnostics.")
    return parser.parse_args(argv)


def ensure_md_file(path: str) -> None:
    if not path.lower().endswith(".md"):
        raise ReqError("Errore: --doc richiede un file che termini con .md", 5)


def make_relative_if_contains_project(path_value: str, project_base: Path) -> str:
    if not path_value:
        return ""
    candidate = Path(path_value)
    if not candidate.is_absolute():
        parts = candidate.parts
        if parts and parts[0] == project_base.name and len(parts) > 1:
            candidate = Path(*parts[1:])
    if candidate.is_absolute():
        try:
            return str(candidate.relative_to(project_base))
        except ValueError:
            return str(candidate)
    resolved = (project_base / candidate).resolve(strict=False)
    try:
        return str(resolved.relative_to(project_base))
    except ValueError:
        pass
    base_str = str(project_base)
    if path_value.startswith(base_str):
        trimmed = path_value[len(base_str) :].lstrip("/\\")
        return trimmed
    return path_value


def resolve_absolute(normalized: str, project_base: Path) -> Optional[Path]:
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (project_base / candidate).resolve(strict=False)


def format_substituted_path(value: str) -> str:
    if not value:
        return ""
    return value.replace(os.sep, "/")


def compute_sub_path(normalized: str, absolute: Optional[Path], project_base: Path) -> str:
    if not normalized:
        return ""
    if absolute:
        try:
            rel = absolute.relative_to(project_base)
            return format_substituted_path(str(rel))
        except ValueError:
            return format_substituted_path(normalized)
    return format_substituted_path(normalized)


def make_relative_token(raw: str, keep_trailing: bool = False) -> str:
    if not raw:
        return ""
    normalized = raw.replace("\\", "/").strip("/")
    if not normalized:
        return ""
    suffix = "/" if keep_trailing and raw.endswith("/") else ""
    return f"{normalized}{suffix}"


def ensure_relative(value: str, name: str, code: int) -> None:
    if Path(value).is_absolute():
        raise ReqError(
            f"Errore: {name} deve essere un percorso relativo rispetto a PROJECT_BASE",
            code,
        )


def copy_with_replacements(src: Path, dst: Path, replacements: Mapping[str, str]) -> None:
    text = src.read_text(encoding="utf-8")
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None:
    if toml_path.exists() and not force:
        raise ReqError(
            f"Destination TOML already exists (use --force to overwrite): {toml_path}", 3
        )
    content = md_path.read_text(encoding="utf-8")
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not match:
        raise ReqError("No leading '---' block found at start of Markdown file.", 4)
    frontmatter, rest = match.groups()
    desc_match = re.search(r"^description:\s*(.*)$", frontmatter, re.M)
    if not desc_match:
        raise ReqError("No 'description:' field found inside the leading block.", 5)
    desc = desc_match.group(1).strip()
    desc_escaped = desc.replace("\\", "\\\\").replace('"', '\\"')
    rest_text = rest if rest.endswith("\n") else rest + "\n"
    toml_body = [f'description = "{desc_escaped}"', "", 'prompt = """', rest_text, '"""', ""]
    toml_path.parent.mkdir(parents=True, exist_ok=True)
    toml_path.write_text("\n".join(toml_body), encoding="utf-8")
    dlog(f"Wrote TOML to: {toml_path}")


def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    path.write_text(text, encoding="utf-8")


def find_template_source() -> Path:
    candidate = RESOURCE_ROOT / "templates"
    if (candidate / "requirements.md").is_file():
        return candidate
    raise ReqError(
        "Errore: nessun template requirements.md trovato in templates o usetemplates",
        9,
    )


def strip_json_comments(text: str) -> str:
    """Remove leading // and /* */ comment lines so JSONC files can be parsed."""
    cleaned: list[str] = []
    in_block = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if in_block:
            if "*/" in stripped:
                in_block = False
            continue
        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_block = True
            continue
        if stripped.startswith("//"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def load_settings(path: Path) -> dict[str, Any]:
    """Load JSON/JSONC settings, stripping comments when necessary."""
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = strip_json_comments(raw)
        dlog(f"Parsed {path} after removing comments")
        return json.loads(cleaned)


def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge dicts, letting incoming values override base."""
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge_dict(base[key], value)  # type: ignore[arg-type]
        else:
            base[key] = value
    return base


def find_vscode_settings_source() -> Optional[Path]:
    candidate = RESOURCE_ROOT / "vscode" / "settings.json"
    if candidate.is_file():
        return candidate
    return None


def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]:
    """Produce chat.promptFilesRecommendations from available prompt files."""
    recommendations: dict[str, bool] = {}
    if not prompts_dir.is_dir():
        return recommendations
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        recommendations[f"req.{prompt_path.stem}"] = True
    return recommendations


def ensure_wrapped(target: Path, project_base: Path, code: int) -> None:
    if not target.resolve().is_relative_to(project_base):
        raise ReqError(
            f"Errore: rimozione sicura di {target} rifiutata (non sotto PROJECT_BASE)",
            code,
        )


def run(args: Namespace) -> None:
    global VERBOSE, DEBUG
    VERBOSE = args.verbose
    DEBUG = args.debug

    if args.base:
        project_base = args.base.resolve()
    else:
        project_base = Path.cwd().resolve()
    if not project_base.exists():
        raise ReqError(f"Errore: PROJECT_BASE '{project_base}' non esiste", 2)

    ensure_md_file(args.doc)

    normalized_doc = make_relative_if_contains_project(args.doc, project_base)
    normalized_dir = make_relative_if_contains_project(args.dir, project_base)
    dir_has_trailing_slash = args.dir.endswith("/") or args.dir.endswith("\\")

    ensure_relative(normalized_doc, "REQ_DOC", 4)
    ensure_relative(normalized_dir, "REQ_DIR", 5)

    abs_doc = resolve_absolute(normalized_doc, project_base)
    abs_dir = resolve_absolute(normalized_dir, project_base)

    sub_req_doc = compute_sub_path(normalized_doc, abs_doc, project_base)
    sub_tech_dir = compute_sub_path(normalized_dir, abs_dir, project_base)
    if dir_has_trailing_slash and sub_tech_dir and not sub_tech_dir.endswith("/"):
        sub_tech_dir += "/"
    token_req_doc = make_relative_token(sub_req_doc)
    token_req_dir = make_relative_token(sub_tech_dir, keep_trailing=True)

    dlog(f"project_base={project_base}")
    dlog(f"REQ_DOC={normalized_doc}")
    dlog(f"REQ_DIR={normalized_dir}")
    dlog(f"SUB_REQ_DOC={sub_req_doc}")
    dlog(f"SUB_TECH_DIR={sub_tech_dir}")
    dlog(f"TOKEN_REQ_DOC={token_req_doc}")
    dlog(f"TOKEN_REQ_DIR={token_req_dir}")

    tech_dest = project_base / normalized_dir
    if not tech_dest.is_dir():
        raise ReqError(
            f"Errore: la directory REQ_DIR '{normalized_dir}' non esiste sotto {project_base}",
            8,
        )
    if VERBOSE:
        log(f"OK: directory tecnica trovata {tech_dest}")

    req_root = project_base / ".req"
    if req_root.exists():
        ensure_wrapped(req_root, project_base, 10)
        shutil.rmtree(req_root)
    req_root.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(f"OK: assicurata directory {req_root}")

    templates_src = find_template_source()
    doc_target = project_base / normalized_doc
    if not doc_target.exists():
        src_file = templates_src / "requirements.md"
        doc_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_file, doc_target)
        if VERBOSE:
            log(
                f"Creato {doc_target} — modificare il file con i requisiti del progetto. (sorgente: {src_file})"
            )

    for folder in (
        project_base / ".codex" / "prompts",
        project_base / ".github" / "agents",
        project_base / ".github" / "prompts",
        project_base / ".gemini" / "commands",
    ):
        folder.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(f"OK: create/assicurate cartelle .codex, .github, .gemini sotto {project_base}")

    prompts_dir = REPO_ROOT / "prompts"
    if not prompts_dir.is_dir():
        prompts_dir = RESOURCE_ROOT / "prompts"
    if prompts_dir.is_dir():
        for prompt_path in sorted(prompts_dir.glob("*.md")):
            PROMPT = prompt_path.stem
            vlog(f"Processo prompt: {PROMPT}")
            dst_codex = project_base / ".codex" / "prompts" / f"req.{PROMPT}.md"
            existed = dst_codex.exists()
            copy_with_replacements(
                prompt_path,
                dst_codex,
                {
                    "%%REQ_DOC%%": token_req_doc,
                    "%%REQ_DIR%%": token_req_dir,
                    "%%ARGS%%": "$ARGUMENTS",
                },
            )
            if VERBOSE:
                log(f"{ 'SOVRASCRITTO' if existed else 'COPIATO' }: {dst_codex}")

            dst_agent = project_base / ".github" / "agents" / f"req.{PROMPT}.agent.md"
            existed = dst_agent.exists()
            copy_with_replacements(
                prompt_path,
                dst_agent,
                {
                    "%%REQ_DOC%%": token_req_doc,
                    "%%REQ_DIR%%": token_req_dir,
                    "%%ARGS%%": "$ARGUMENTS",
                },
            )
            if VERBOSE:
                log(f"{ 'SOVRASCRITTO' if existed else 'COPIATO' }: {dst_agent}")

            dst_prompt = project_base / ".github" / "prompts" / f"req.{PROMPT}.prompt.md"
            existed = dst_prompt.exists()
            dst_prompt.write_text(f"---\nagent: req.{PROMPT}\n---\n", encoding="utf-8")
            if VERBOSE:
                log(f"{ 'SOVRASCRITTO' if existed else 'COPIATO' }: {dst_prompt}")

            dst_toml = project_base / ".gemini" / "commands" / f"req.{PROMPT}.toml"
            existed = dst_toml.exists()
            md_to_toml(prompt_path, dst_toml, force=existed)
            replace_tokens(
                dst_toml,
                {
                    "%%REQ_DOC%%": token_req_doc,
                    "%%REQ_DIR%%": token_req_dir,
                    "%%ARGS%%": "{{args}}",
                },
            )
            if VERBOSE:
                log(f"{ 'SOVRASCRITTO' if existed else 'COPIATO' }: {dst_toml}")

    templates_target = req_root / "templates"
    if templates_target.exists():
        ensure_wrapped(templates_target, project_base, 10)
        shutil.rmtree(templates_target)
    shutil.copytree(templates_src, templates_target)
    if VERBOSE:
        log(
            f"OK: ricreati {templates_target} da {templates_src} (contenuto precedente cancellato)"
        )

    vscode_settings_src = find_vscode_settings_source()
    if vscode_settings_src:
        vscode_dir = project_base / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)
        target_settings = vscode_dir / "settings.json"
        merged_settings: dict[str, Any] = {}
        if target_settings.exists():
            merged_settings = load_settings(target_settings)
        src_settings = load_settings(vscode_settings_src)
        merged_settings = deep_merge_dict(merged_settings, src_settings)
        prompt_recs = build_prompt_recommendations(prompts_dir)
        if prompt_recs:
            merged_settings["chat.promptFilesRecommendations"] = prompt_recs
        target_settings.write_text(json.dumps(merged_settings, indent=2, ensure_ascii=False), encoding="utf-8")
        if VERBOSE:
            log(f"OK: integrato settings.json in {target_settings}")


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point suitable for console_scripts and `-m` execution.

    Returns an exit code (0 success, non-zero on error).
    """
    try:
        args = parse_args(argv)
        run(args)
    except ReqError as e:
        print(e.message, file=sys.stderr)
        return e.code
    except Exception as e:  # unexpected
        print(f"Unexpected error: {e}", file=sys.stderr)
        if DEBUG:
            import traceback

            traceback.print_exc()
        return 1
    return 0

