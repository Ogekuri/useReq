"""Punto di ingresso CLI che implementa il flusso di inizializzazione di useReq."""

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

REPO_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"
VERBOSE = False
DEBUG = False


class ReqError(Exception):
    """Eccezione dedicata per errori previsti della CLI."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


def log(msg: str) -> None:
    """Stampa un messaggio informativo."""
    print(msg)


def dlog(msg: str) -> None:
    """Stampa un messaggio di debug se attivo."""
    if DEBUG:
        print("DEBUG:", msg)


def vlog(msg: str) -> None:
    """Stampa un messaggio verboso se attivo."""
    if VERBOSE:
        print(msg)


def build_parser() -> argparse.ArgumentParser:
    """Costruisce il parser degli argomenti CLI."""
    version = load_package_version()
    usage = (
        "req -c [-h] [--upgrade] [--uninstall] [--remove] [--update] (--base BASE | --here) "
        "--doc DOC --dir DIR [--verbose] [--debug] "
        f"({version})"
    )
    parser = argparse.ArgumentParser(
        description="Initialize a project with useReq resources.",
        prog="req",
        usage=usage,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--base", type=Path, help="Directory root of the project to update."
    )
    group.add_argument(
        "--here",
        action="store_true",
        help="Use current working directory as the project root.",
    )
    parser.add_argument(
        "--doc",
        help="Directory containing documentation files relative to the project root.",
    )
    parser.add_argument(
        "--dir", help="Technical directory relative to the project root."
    )
    parser.add_argument(
        "--upgrade", action="store_true", help="Upgrade the tool with uv."
    )
    parser.add_argument(
        "--uninstall", action="store_true", help="Uninstall the tool with uv."
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Re-run the command using .req/config.json.",
    )
    parser.add_argument(
        "--remove", action="store_true", help="Remove resources created by the tool."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show verbose progress messages."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Show debug logs for diagnostics."
    )
    return parser


def parse_args(argv: Optional[list[str]] = None) -> Namespace:
    return build_parser().parse_args(argv)


def load_package_version() -> str:
    """Legge la versione del pacchetto da __init__.py."""
    init_path = Path(__file__).resolve().parent / "__init__.py"
    text = init_path.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"\s*$', text, re.M)
    if not match:
        raise ReqError("Error: unable to determine package version", 6)
    return match.group(1)


def maybe_print_version(argv: list[str]) -> bool:
    """Gestisce --ver/--version stampando la versione."""
    if "--ver" in argv or "--version" in argv:
        print(load_package_version())
        return True
    return False


def run_upgrade() -> None:
    """Esegue l'aggiornamento con uv."""
    command = [
        "uv",
        "tool",
        "install",
        "usereq",
        "--force",
        "--from",
        "git+https://github.com/Ogekuri/useReq.git",
    ]
    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise ReqError("Error: 'uv' command not found in PATH", 12) from exc
    if result.returncode != 0:
        raise ReqError(
            f"Error: auto-upgrade failed (code {result.returncode})",
            result.returncode,
        )


def run_uninstall() -> None:
    """Esegue la disinstallazione con uv."""
    command = [
        "uv",
        "tool",
        "uninstall",
        "usereq",
    ]
    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise ReqError("Error: 'uv' command not found in PATH", 12) from exc
    if result.returncode != 0:
        raise ReqError(
            f"Error: uninstall failed (code {result.returncode})",
            result.returncode,
        )


def normalize_release_tag(tag: str) -> str:
    """Normalizza il tag di release rimuovendo un eventuale prefisso 'v'."""
    value = (tag or "").strip()
    if value.lower().startswith("v") and len(value) > 1:
        value = value[1:]
    return value.strip()


def parse_version_tuple(version: str) -> tuple[int, ...] | None:
    """Converte una versione in una tupla numerica per il confronto.

    Accetta versioni nel formato 'X.Y.Z' (con eventuali suffix non numerici che vengono ignorati).
    """

    cleaned = (version or "").strip()
    if not cleaned:
        return None

    parts = cleaned.split(".")
    numbers: list[int] = []
    for part in parts:
        match = re.match(r"^(\d+)", part)
        if not match:
            break
        try:
            numbers.append(int(match.group(1)))
        except ValueError:
            return None

    return tuple(numbers) if numbers else None


def is_newer_version(current: str, latest: str) -> bool:
    """Ritorna True se latest e' maggiore di current."""
    current_tuple = parse_version_tuple(current)
    latest_tuple = parse_version_tuple(latest)
    if not current_tuple or not latest_tuple:
        return False

    max_len = max(len(current_tuple), len(latest_tuple))
    current_norm = current_tuple + (0,) * (max_len - len(current_tuple))
    latest_norm = latest_tuple + (0,) * (max_len - len(latest_tuple))
    return latest_norm > current_norm


def maybe_notify_newer_version(timeout_seconds: float = 1.0) -> None:
    """Verifica online la presenza di una nuova versione e stampa un avviso.

    Se la chiamata fallisce o la risposta non e' valida, non stampa nulla e prosegue.
    """

    current_version = load_package_version()
    url = "https://api.github.com/repos/Ogekuri/useReq/releases/latest"

    try:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": f"usereq/{current_version}",
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
        payload = json.loads(body)
        tag = payload.get("tag_name")
        if not isinstance(tag, str) or not tag.strip():
            return

        latest_version = normalize_release_tag(tag)
        if is_newer_version(current_version, latest_version):
            print(
                "A new version of usereq is available: "
                f"current {current_version}, latest {latest_version}. "
                "To upgrade, run: req --upgrade"
            )
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        ValueError,
    ):
        return


def ensure_doc_directory(path: str, project_base: Path) -> None:
    # Prima normalizza il percorso usando la logica esistente.
    normalized = make_relative_if_contains_project(path, project_base)
    doc_path = project_base / normalized
    resolved = doc_path.resolve(strict=False)
    if not resolved.is_relative_to(project_base):
        raise ReqError("Error: --doc must be under the project base", 5)
    if not doc_path.exists():
        raise ReqError(
            f"Error: the --doc directory '{normalized}' does not exist under {project_base}",
            5,
        )
    if not doc_path.is_dir():
        raise ReqError(f"Error: --doc must specify a directory, not a file", 5)


def make_relative_if_contains_project(path_value: str, project_base: Path) -> str:
    """Normalizza il percorso rispetto alla root di progetto quando possibile."""
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
    """Risoluzione del percorso assoluto a partire da un valore normalizzato."""
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (project_base / candidate).resolve(strict=False)


def format_substituted_path(value: str) -> str:
    """Uniforma i separatori di percorso per le sostituzioni."""
    if not value:
        return ""
    return value.replace(os.sep, "/")


def compute_sub_path(
    normalized: str, absolute: Optional[Path], project_base: Path
) -> str:
    """Calcola il percorso relativo da usare nei token."""
    if not normalized:
        return ""
    if absolute:
        try:
            rel = absolute.relative_to(project_base)
            return format_substituted_path(str(rel))
        except ValueError:
            return format_substituted_path(normalized)
    return format_substituted_path(normalized)


def save_config(project_base: Path, doc_value: str, dir_value: str) -> None:
    """Salva i parametri normalizzati in .req/config.json."""
    config_path = project_base / ".req" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"doc": doc_value, "dir": dir_value}
    config_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def load_config(project_base: Path) -> dict[str, str]:
    """Carica i parametri salvati da .req/config.json."""
    config_path = project_base / ".req" / "config.json"
    if not config_path.is_file():
        raise ReqError(
            "Error: .req/config.json not found in the project root",
            11,
        )
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReqError("Error: .req/config.json is not valid", 11) from exc
    doc_value = payload.get("doc")
    dir_value = payload.get("dir")
    if not isinstance(doc_value, str) or not doc_value.strip():
        raise ReqError("Error: missing or invalid 'doc' field in .req/config.json", 11)
    if not isinstance(dir_value, str) or not dir_value.strip():
        raise ReqError("Error: missing or invalid 'dir' field in .req/config.json", 11)
    return {"doc": doc_value, "dir": dir_value}


def generate_doc_file_list(doc_dir: Path, project_base: Path) -> str:
    """Genera l'elenco markdown dei file per la sostituzione di %%REQ_DOC%%."""
    if not doc_dir.is_dir():
        return ""

    files = []
    for file_path in sorted(doc_dir.iterdir()):
        if file_path.is_file():
            try:
                rel_path = file_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/")
                files.append(f"[{rel_str}]({rel_str})")
            except ValueError:
                continue

    return ", ".join(files)


def generate_dir_list(dir_path: Path, project_base: Path) -> str:
    """Genera l'elenco markdown delle directory per la sostituzione di %%REQ_DIR%%."""
    if not dir_path.is_dir():
        return ""

    subdirs = []
    for subdir_path in sorted(dir_path.iterdir()):
        if subdir_path.is_dir():
            try:
                rel_path = subdir_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/") + "/"
                subdirs.append(f"[{rel_str}]({rel_str})")
            except ValueError:
                continue

    # Se non ci sono sottodirectory, usa la directory stessa.
    if not subdirs:
        try:
            rel_path = dir_path.relative_to(project_base)
            rel_str = str(rel_path).replace(os.sep, "/") + "/"
            return f"[{rel_str}]({rel_str})"
        except ValueError:
            return ""

    return ", ".join(subdirs)


def make_relative_token(raw: str, keep_trailing: bool = False) -> str:
    """Normalizza il token di percorso preservando opzionalmente lo slash finale."""
    if not raw:
        return ""
    normalized = raw.replace("\\", "/").strip("/")
    if not normalized:
        return ""
    suffix = "/" if keep_trailing and raw.endswith("/") else ""
    return f"{normalized}{suffix}"


def ensure_relative(value: str, name: str, code: int) -> None:
    """Valida che il percorso non sia assoluto e segnala errore in caso contrario."""
    if Path(value).is_absolute():
        raise ReqError(
            f"Error: {name} must be a relative path under PROJECT_BASE",
            code,
        )
        raise ReqError(
            f"Error: {name} must be a relative path under PROJECT_BASE",
            code,
        )


def copy_with_replacements(
    src: Path, dst: Path, replacements: Mapping[str, str]
) -> None:
    """Copia un file sostituendo i token indicati con i relativi valori."""
    text = src.read_text(encoding="utf-8")
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")


def normalize_description(value: str) -> str:
    """Normalizza una descrizione rimuovendo virgolette superflue ed escape."""
    trimmed = value.strip()
    if len(trimmed) >= 2 and trimmed.startswith('"') and trimmed.endswith('"'):
        trimmed = trimmed[1:-1]
    if len(trimmed) >= 4 and trimmed.startswith('\\"') and trimmed.endswith('\\"'):
        trimmed = trimmed[2:-2]
    return trimmed.replace('\\"', '"')


def md_to_toml(md_path: Path, toml_path: Path, force: bool) -> None:
    """Converte un prompt Markdown in TOML per Gemini."""
    if toml_path.exists() and not force:
        raise ReqError(
            f"Destination TOML already exists (use --force to overwrite): {toml_path}",
            3,
        )
    content = md_path.read_text(encoding="utf-8")
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not match:
        raise ReqError("No leading '---' block found at start of Markdown file.", 4)
    frontmatter, rest = match.groups()
    desc = extract_description(frontmatter)
    desc_escaped = desc.replace("\\", "\\\\").replace('"', '\\"')
    rest_text = rest if rest.endswith("\n") else rest + "\n"
    toml_body = [
        f'description = "{desc_escaped}"',
        "",
        'prompt = """',
        rest_text,
        '"""',
        "",
    ]
    toml_path.parent.mkdir(parents=True, exist_ok=True)
    toml_path.write_text("\n".join(toml_body), encoding="utf-8")
    dlog(f"Wrote TOML to: {toml_path}")


def extract_frontmatter(content: str) -> tuple[str, str]:
    """Estrae front matter e corpo dal Markdown."""
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not match:
        raise ReqError("No leading '---' block found at start of Markdown file.", 4)
    # Explicitamente ritorniamo due stringhe per soddisfare l'annotazione di tipo.
    return match.group(1), match.group(2)


def extract_description(frontmatter: str) -> str:
    """Estrae la descrizione dal front matter."""
    desc_match = re.search(r"^description:\s*(.*)$", frontmatter, re.M)
    if not desc_match:
        raise ReqError("No 'description:' field found inside the leading block.", 5)
    return normalize_description(desc_match.group(1).strip())


def extract_purpose_first_bullet(body: str) -> str:
    """Ritorna il primo bullet della sezione Purpose."""
    lines = body.splitlines()
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == "## purpose":
            start_idx = idx + 1
            break
    if start_idx is None:
        raise ReqError("Error: missing '## Purpose' section in prompt.", 7)
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        match = re.match(r"^\s*-\s+(.*)$", line)
        if match:
            return match.group(1).strip()
    raise ReqError("Error: no bullet found under the '## Purpose' section.", 7)


def json_escape(value: str) -> str:
    """Esegue l'escape JSON di una stringa senza delimitatori esterni."""
    return json.dumps(value)[1:-1]


def generate_kiro_resources(
    doc_dir: Path,
    project_base: Path,
    prompt_rel_path: str,
) -> str:
    """Genera l'array JSON delle risorse per l'agente Kiro."""
    resources = [f'    "file://{prompt_rel_path}"']
    if not doc_dir.is_dir():
        return "\n".join(resources)

    for file_path in sorted(doc_dir.iterdir()):
        if file_path.is_file():
            try:
                rel_path = file_path.relative_to(project_base)
                rel_str = str(rel_path).replace(os.sep, "/")
                resources.append(f'    "file://{rel_str}"')
            except ValueError:
                continue

    return ",\n".join(resources)


def render_kiro_agent(
    template: str,
    name: str,
    description: str,
    prompt: str,
    resources: str,
) -> str:
    """Rende il JSON dell'agente Kiro con i token sostituiti."""
    replacements = {
        "%%NAME%%": json_escape(name),
        "%%DESCRIPTION%%": json_escape(description),
        "%%PROMPT%%": json_escape(prompt),
        "%%RESOURCES%%": resources,
    }
    for token, replacement in replacements.items():
        template = template.replace(token, replacement)
    return template


def replace_tokens(path: Path, replacements: Mapping[str, str]) -> None:
    """Sostituisce i token nel file indicato."""
    text = path.read_text(encoding="utf-8")
    for token, replacement in replacements.items():
        text = text.replace(token, replacement)
    path.write_text(text, encoding="utf-8")


def yaml_double_quote_escape(value: str) -> str:
    """Esegue l'escape minimo per una stringa tra doppi apici in YAML."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def find_template_source() -> Path:
    """Restituisce la sorgente dei template o solleva errore."""
    candidate = RESOURCE_ROOT / "templates"
    if (candidate / "requirements.md").is_file():
        return candidate
    raise ReqError(
        "Error: no requirements.md template found in templates or usetemplates",
        9,
    )


def load_kiro_template() -> str:
    """Carica il template JSON per gli agenti Kiro."""
    candidate = RESOURCE_ROOT / "kiro" / "agent.json"
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    raise ReqError("Error: no Kiro template found in resources/kiro", 9)


def strip_json_comments(text: str) -> str:
    """Rimuove commenti // e /* */ per consentire il parsing di JSONC."""
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
    """Carica impostazioni JSON/JSONC, rimuovendo i commenti quando necessario."""
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = strip_json_comments(raw)
        dlog(f"Parsed {path} after removing comments")
        return json.loads(cleaned)


def deep_merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Unisce dizionari in modo ricorsivo, dando priorita ai valori in ingresso."""
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge_dict(base[key], value)
        else:
            base[key] = value
    return base


def find_vscode_settings_source() -> Optional[Path]:
    candidate = RESOURCE_ROOT / "vscode" / "settings.json"
    if candidate.is_file():
        return candidate
    return None


def build_prompt_recommendations(prompts_dir: Path) -> dict[str, bool]:
    """Genera chat.promptFilesRecommendations dai prompt disponibili."""
    recommendations: dict[str, bool] = {}
    if not prompts_dir.is_dir():
        return recommendations
    for prompt_path in sorted(prompts_dir.glob("*.md")):
        recommendations[f"req.{prompt_path.stem}"] = True
    return recommendations


def ensure_wrapped(target: Path, project_base: Path, code: int) -> None:
    """Verifica che il percorso sia sotto la root di progetto."""
    if not target.resolve().is_relative_to(project_base):
        raise ReqError(
            f"Error: safe removal of {target} refused (not under PROJECT_BASE)",
            code,
        )


def save_vscode_backup(req_root: Path, settings_path: Path) -> None:
    """Salva un backup delle impostazioni VS Code se il file esiste."""
    backup_path = req_root / "settings.json.backup"
    # Non creare mai un marker di assenza. Creiamo il backup solo se il file esiste.
    if settings_path.exists():
        req_root.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(settings_path, backup_path)


def restore_vscode_settings(project_base: Path) -> None:
    """Ripristina le impostazioni VS Code dal backup, se presente."""
    req_root = project_base / ".req"
    backup_path = req_root / "settings.json.backup"
    target_settings = project_base / ".vscode" / "settings.json"
    if backup_path.exists():
        target_settings.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(backup_path, target_settings)
    # Non rimuovere il file target se non esiste backup: comportamento di ripristino disabilitato altrimenti.


def prune_empty_dirs(root: Path) -> None:
    """Rimuove le directory vuote sotto la radice indicata."""
    if not root.is_dir():
        return
    for current, _dirs, _files in os.walk(root, topdown=False):
        current_path = Path(current)
        try:
            if not any(current_path.iterdir()):
                current_path.rmdir()
        except OSError:
            continue


def remove_generated_resources(project_base: Path) -> None:
    """Rimuove risorse generate dallo strumento nella root di progetto."""
    remove_dirs = [
        project_base / ".gemini" / "commands" / "req",
        project_base / ".claude" / "commands" / "req",
        project_base / ".req" / "templates",
    ]
    remove_globs = [
        project_base / ".codex" / "prompts",
        project_base / ".github" / "agents",
        project_base / ".github" / "prompts",
        project_base / ".kiro" / "agents",
        project_base / ".kiro" / "prompts",
        project_base / ".claude" / "agents",
        project_base / ".claude" / "commands",
        project_base / ".opencode" / "agent",
        project_base / ".opencode" / "command",
    ]
    for target in remove_dirs:
        if target.exists():
            ensure_wrapped(target, project_base, 10)
            shutil.rmtree(target)
    for folder in remove_globs:
        if not folder.is_dir():
            continue
        ensure_wrapped(folder, project_base, 10)
        for path in folder.glob("req.*"):
            if path.is_file():
                path.unlink()
    config_path = project_base / ".req" / "config.json"
    if config_path.exists():
        ensure_wrapped(config_path, project_base, 10)
        config_path.unlink()
    req_root = project_base / ".req"
    if req_root.exists():
        ensure_wrapped(req_root, project_base, 10)
        shutil.rmtree(req_root)


def run_remove(args: Namespace) -> None:
    """Gestisce la rimozione delle risorse generate."""
    if args.doc or args.dir or args.update:
        raise ReqError("Error: --remove does not accept --doc, --dir, or --update", 4)
    if args.base:
        project_base = args.base.resolve()
    else:
        project_base = Path.cwd().resolve()
    if not project_base.exists():
        raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)
    config_path = project_base / ".req" / "config.json"
    if not config_path.is_file():
        raise ReqError(
            "Error: .req/config.json not found in the project root",
            11,
        )

    # Dopo la validazione e prima di qualsiasi rimozione, controlla se esiste una nuova versione.
    maybe_notify_newer_version(timeout_seconds=1.0)

    # Non eseguire alcun ripristino o rimozione di .vscode/settings.json durante la rimozione.
    remove_generated_resources(project_base)
    for root_name in (
        ".gemini",
        ".codex",
        ".kiro",
        ".github",
        ".vscode",
        ".opencode",
        ".claude",
    ):
        prune_empty_dirs(project_base / root_name)


def run(args: Namespace) -> None:
    """Gestisce il flusso principale di inizializzazione."""
    global VERBOSE, DEBUG
    VERBOSE = args.verbose
    DEBUG = args.debug

    # Flusso principale: valida input, calcola percorsi, genera risorse.
    if args.remove:
        run_remove(args)
        return

    if args.base:
        project_base = args.base.resolve()
    else:
        project_base = Path.cwd().resolve()
    if not project_base.exists():
        raise ReqError(f"Error: PROJECT_BASE '{project_base}' does not exist", 2)

    if args.update and (args.doc or args.dir):
        raise ReqError("Error: --update does not accept --doc or --dir", 4)
    if not args.update and (not args.doc or not args.dir):
        raise ReqError("Error: --doc and --dir are required without --update", 4)

    if args.update:
        config = load_config(project_base)
        doc_value = config["doc"]
        dir_value = config["dir"]
    else:
        doc_value = args.doc
        dir_value = args.dir

    ensure_doc_directory(doc_value, project_base)

    normalized_doc = make_relative_if_contains_project(doc_value, project_base)
    normalized_dir = make_relative_if_contains_project(dir_value, project_base)
    doc_has_trailing_slash = doc_value.endswith("/") or doc_value.endswith("\\")
    dir_has_trailing_slash = dir_value.endswith("/") or dir_value.endswith("\\")
    normalized_doc = normalized_doc.rstrip("/\\")
    normalized_dir = normalized_dir.rstrip("/\\")

    ensure_relative(normalized_doc, "REQ_DOC", 4)
    ensure_relative(normalized_dir, "REQ_DIR", 5)

    abs_doc = resolve_absolute(normalized_doc, project_base)
    abs_dir = resolve_absolute(normalized_dir, project_base)
    if abs_doc and not abs_doc.resolve().is_relative_to(project_base):
        raise ReqError("Error: --doc must be under the project base", 5)
    if abs_dir and not abs_dir.resolve().is_relative_to(project_base):
        raise ReqError("Error: --dir must be under the project base", 8)

    config_doc = (
        f"{normalized_doc}/"
        if doc_has_trailing_slash and normalized_doc
        else normalized_doc
    )
    config_dir = (
        f"{normalized_dir}/"
        if dir_has_trailing_slash and normalized_dir
        else normalized_dir
    )

    tech_dest = project_base / normalized_dir
    if not tech_dest.is_dir():
        raise ReqError(
            f"Error: REQ_DIR directory '{normalized_dir}' does not exist under {project_base}",
            8,
        )
    if VERBOSE:
        log(f"OK: technical directory found {tech_dest}")

    # Dopo la validazione e prima di qualsiasi operazione che modifichi il filesystem, controlla se esiste una nuova versione.
    maybe_notify_newer_version(timeout_seconds=1.0)

    if not args.update:
        save_config(project_base, config_doc, config_dir)

    sub_req_doc = compute_sub_path(normalized_doc, abs_doc, project_base)
    sub_tech_dir = compute_sub_path(normalized_dir, abs_dir, project_base)
    if dir_has_trailing_slash and sub_tech_dir and not sub_tech_dir.endswith("/"):
        sub_tech_dir += "/"
    token_req_doc = make_relative_token(sub_req_doc)
    token_req_dir = make_relative_token(sub_tech_dir, keep_trailing=True)

    req_root = project_base / ".req"
    req_root.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(f"OK: ensured directory {req_root}")

    templates_src = find_template_source()
    doc_dir_path = project_base / normalized_doc
    doc_dir_empty = not any(doc_dir_path.iterdir())
    doc_target = project_base / normalized_doc / "requirements.md"
    # Crea requirements.md solo se la cartella --doc e' vuota.
    if doc_dir_empty:
        src_file = templates_src / "requirements.md"
        doc_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_file, doc_target)
        if VERBOSE:
            log(
                f"Created {doc_target} — update the file with the project requirements. (source: {src_file})"
            )

    # Genera l'elenco file per il token %%REQ_DOC%% dopo l'eventuale creazione.
    doc_file_list = generate_doc_file_list(doc_dir_path, project_base)

    # Genera l'elenco directory per il token %%REQ_DIR%%.
    dir_list = generate_dir_list(project_base / normalized_dir, project_base)

    dlog(f"project_base={project_base}")
    dlog(f"REQ_DOC={normalized_doc}")
    dlog(f"REQ_DIR={normalized_dir}")
    dlog(f"DOC_FILE_LIST={doc_file_list}")
    dlog(f"DIR_LIST={dir_list}")
    dlog(f"SUB_TECH_DIR={sub_tech_dir}")
    dlog(f"TOKEN_REQ_DIR={token_req_dir}")

    for folder in (
        project_base / ".codex" / "prompts",
        project_base / ".github" / "agents",
        project_base / ".github" / "prompts",
        project_base / ".gemini" / "commands",
        project_base / ".gemini" / "commands" / "req",
        project_base / ".kiro" / "agents",
        project_base / ".kiro" / "prompts",
        project_base / ".claude" / "agents",
        project_base / ".claude" / "commands",
        project_base / ".claude" / "commands" / "req",
        project_base / ".opencode" / "agent",
        project_base / ".opencode" / "command",
    ):
        folder.mkdir(parents=True, exist_ok=True)
    if VERBOSE:
        log(
            "OK: created/ensured folders .codex, .github, .gemini, .kiro under "
            f"{project_base}"
        )

    prompts_dir = REPO_ROOT / "prompts"
    if not prompts_dir.is_dir():
        prompts_dir = RESOURCE_ROOT / "prompts"
    kiro_template = load_kiro_template()
    if prompts_dir.is_dir():
        for prompt_path in sorted(prompts_dir.glob("*.md")):
            PROMPT = prompt_path.stem
            vlog(f"Processing prompt: {PROMPT}")
            prompt_content = prompt_path.read_text(encoding="utf-8")
            frontmatter, body = extract_frontmatter(prompt_content)
            description = extract_description(frontmatter)
            prompt_body = body
            dst_codex = project_base / ".codex" / "prompts" / f"req.{PROMPT}.md"
            existed = dst_codex.exists()
            copy_with_replacements(
                prompt_path,
                dst_codex,
                {
                    "%%REQ_DOC%%": doc_file_list,
                    "%%REQ_DIR%%": dir_list,
                    "%%REQ_PATH%%": normalized_doc,
                    "%%ARGS%%": "$ARGUMENTS",
                },
            )
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_codex}")

            dst_agent = project_base / ".github" / "agents" / f"req.{PROMPT}.agent.md"
            existed = dst_agent.exists()
            desc_yaml = yaml_double_quote_escape(description)
            github_header = (
                f'---\nname: req.{PROMPT}\ndescription: "{desc_yaml}"\n---\n\n'
            )
            github_text = github_header + prompt_body
            for token, replacement in {
                "%%REQ_DOC%%": doc_file_list,
                "%%REQ_DIR%%": dir_list,
                "%%REQ_PATH%%": normalized_doc,
                "%%ARGS%%": "$ARGUMENTS",
            }.items():
                github_text = github_text.replace(token, replacement)
            dst_agent.parent.mkdir(parents=True, exist_ok=True)
            if not github_text.endswith("\n"):
                github_text += "\n"
            dst_agent.write_text(github_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_agent}")

            dst_prompt = (
                project_base / ".github" / "prompts" / f"req.{PROMPT}.prompt.md"
            )
            existed = dst_prompt.exists()
            dst_prompt.write_text(f"---\nagent: req.{PROMPT}\n---\n", encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_prompt}")

            dst_toml = project_base / ".gemini" / "commands" / "req" / f"{PROMPT}.toml"
            existed = dst_toml.exists()
            md_to_toml(prompt_path, dst_toml, force=existed)
            replace_tokens(
                dst_toml,
                {
                    "%%REQ_DOC%%": doc_file_list,
                    "%%REQ_DIR%%": dir_list,
                    "%%REQ_PATH%%": normalized_doc,
                    "%%ARGS%%": "{{args}}",
                },
            )
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_toml}")

            dst_kiro_prompt = project_base / ".kiro" / "prompts" / f"req.{PROMPT}.md"
            existed = dst_kiro_prompt.exists()
            copy_with_replacements(
                prompt_path,
                dst_kiro_prompt,
                {
                    "%%REQ_DOC%%": doc_file_list,
                    "%%REQ_DIR%%": dir_list,
                    "%%REQ_PATH%%": normalized_doc,
                    "%%ARGS%%": "$ARGUMENTS",
                },
            )
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_kiro_prompt}")

            dst_claude_agent = project_base / ".claude" / "agents" / f"req.{PROMPT}.md"
            existed = dst_claude_agent.exists()
            desc_yaml = yaml_double_quote_escape(description)
            claude_header = (
                "---\n"
                f"name: req-{PROMPT}\n"
                f'description: "{desc_yaml}"\n'
                "model: inherit\n"
                "---\n\n"
            )
            claude_text = claude_header + prompt_body
            for token, replacement in {
                "%%REQ_DOC%%": doc_file_list,
                "%%REQ_DIR%%": dir_list,
                "%%REQ_PATH%%": normalized_doc,
                "%%ARGS%%": "$ARGUMENTS",
            }.items():
                claude_text = claude_text.replace(token, replacement)
            dst_claude_agent.parent.mkdir(parents=True, exist_ok=True)
            if not claude_text.endswith("\n"):
                claude_text += "\n"
            dst_claude_agent.write_text(claude_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_claude_agent}")

            dst_kiro_agent = project_base / ".kiro" / "agents" / f"req.{PROMPT}.json"
            existed = dst_kiro_agent.exists()
            kiro_prompt_rel = f".kiro/prompts/req.{PROMPT}.md"
            kiro_resources = generate_kiro_resources(
                project_base / normalized_doc,
                project_base,
                kiro_prompt_rel,
            )
            agent_content = render_kiro_agent(
                kiro_template,
                name=f"req-{PROMPT}",
                description=description,
                prompt=prompt_body,
                resources=kiro_resources,
            )
            dst_kiro_agent.write_text(agent_content, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_kiro_agent}")

            dst_opencode_agent = (
                project_base / ".opencode" / "agent" / f"req.{PROMPT}.md"
            )
            existed = dst_opencode_agent.exists()
            desc_yaml = yaml_double_quote_escape(description)
            opencode_header = f'---\ndescription: "{desc_yaml}"\nmode: all\n---\n\n'
            opencode_text = opencode_header + prompt_body
            for token, replacement in {
                "%%REQ_DOC%%": doc_file_list,
                "%%REQ_DIR%%": dir_list,
                "%%REQ_PATH%%": normalized_doc,
                "%%ARGS%%": "$ARGUMENTS",
            }.items():
                opencode_text = opencode_text.replace(token, replacement)
            dst_opencode_agent.parent.mkdir(parents=True, exist_ok=True)
            if not opencode_text.endswith("\n"):
                opencode_text += "\n"
            dst_opencode_agent.write_text(opencode_text, encoding="utf-8")
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_opencode_agent}")

            # Also copy prompt into .opencode/command as plain markdown with same substitutions
            dst_opencode_command = (
                project_base / ".opencode" / "command" / f"req.{PROMPT}.md"
            )
            existed = dst_opencode_command.exists()
            copy_with_replacements(
                prompt_path,
                dst_opencode_command,
                {
                    "%%REQ_DOC%%": doc_file_list,
                    "%%REQ_DIR%%": dir_list,
                    "%%REQ_PATH%%": normalized_doc,
                    "%%ARGS%%": "$ARGUMENTS",
                },
            )
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_opencode_command}")

            # Also copy prompt into .claude/commands/req mirroring .codex/prompts behavior
            dst_claude_command = (
                project_base / ".claude" / "commands" / "req" / f"{PROMPT}.md"
            )
            existed = dst_claude_command.exists()
            copy_with_replacements(
                prompt_path,
                dst_claude_command,
                {
                    "%%REQ_DOC%%": doc_file_list,
                    "%%REQ_DIR%%": dir_list,
                    "%%REQ_PATH%%": normalized_doc,
                    "%%ARGS%%": "$ARGUMENTS",
                },
            )
            if VERBOSE:
                log(f"{'OVERWROTE' if existed else 'COPIED'}: {dst_claude_command}")

    templates_target = req_root / "templates"
    if templates_target.exists():
        ensure_wrapped(templates_target, project_base, 10)
        shutil.rmtree(templates_target)
    shutil.copytree(templates_src, templates_target)
    if VERBOSE:
        log(
            f"OK: recreated {templates_target} from {templates_src} (previous contents removed)"
        )

    vscode_settings_src = find_vscode_settings_source()
    if vscode_settings_src:
        vscode_dir = project_base / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)
        target_settings = vscode_dir / "settings.json"

        # Carichiamo le impostazioni esistenti (se presenti) e quelle del template.
        existing_settings: dict[str, Any] = {}
        if target_settings.exists():
            try:
                existing_settings = load_settings(target_settings)
            except Exception:
                # Se non siamo in grado di caricare le impostazioni esistenti, consideriamo il file come non presente
                existing_settings = {}

        src_settings = load_settings(vscode_settings_src)

        # Calcoliamo il merge semantico senza modificare l'originale finché non siamo sicuri.
        import copy

        final_settings = copy.deepcopy(existing_settings)
        final_settings = deep_merge_dict(final_settings, src_settings)

        prompt_recs = build_prompt_recommendations(prompts_dir)
        if prompt_recs:
            final_settings["chat.promptFilesRecommendations"] = prompt_recs

        # Se il risultato finale è identico a quanto già presente, non riscriviamo il file né creiamo backup.
        if existing_settings == final_settings:
            if VERBOSE:
                log(f"OK: settings.json already up-to-date in {target_settings}")
        else:
            # Se sono previste modifiche, creiamo backup solo se il file esiste.
            if target_settings.exists():
                save_vscode_backup(req_root, target_settings)
            # Scriviamo le impostazioni finali sul file target.
            target_settings.write_text(
                json.dumps(final_settings, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            if VERBOSE:
                log(f"OK: merged settings.json in {target_settings}")


def main(argv: Optional[list[str]] = None) -> int:
    """Punto di ingresso CLI per console_scripts e per esecuzione con `-m`.

    Restituisce un codice di uscita (0 successo, non zero in caso di errore).
    """
    try:
        argv_list = sys.argv[1:] if argv is None else argv
        if not argv_list:
            build_parser().print_help()
            return 0
        if "--uninstall" in argv_list:
            run_uninstall()
            return 0
        if "--upgrade" in argv_list:
            run_upgrade()
            return 0
        if maybe_print_version(argv_list):
            return 0
        args = parse_args(argv_list)
        run(args)
    except ReqError as e:
        print(e.message, file=sys.stderr)
        return e.code
    except Exception as e:  # errore inatteso
        print(f"Unexpected error: {e}", file=sys.stderr)
        if DEBUG:
            import traceback

            traceback.print_exc()
        return 1
    return 0
