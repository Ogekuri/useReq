"""!@file
@brief Implement tomarkdown CLI orchestration and processing pipelines.
@details Provides argument parsing, PDF/HTML processing, post-processing
normalization, optional Pix2Tex/Gemini enrichment, and output artifact
management. Complexity is dominated by document parsing and image-processing
phases delegated to external libraries.
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Union, cast

import pymupdf  # type: ignore[reportMissingImports]

from tomarkdown.latex import validate_latex_formula

os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")
warnings.filterwarnings(
    "ignore",
    message=r".*Pydantic serializer warnings:.*",
    category=UserWarning,
)

#: @brief Module-level logger used across all processing phases.
LOG = logging.getLogger("tomarkdown")
#: @brief Millimeter-to-point conversion factor used for PDF crop margins.
MM_TO_PT = 72.0 / 25.4
VECTOR_SKIP_Y_RATIO = 0.15
MIN_VECTOR_SIZE_PT = 100.0
MAX_SEPARATOR_WIDTH_RATIO = 0.8
MIN_VECTOR_PATHS = 3
CLUSTER_X_TOLERANCE = 10.0
CLUSTER_Y_TOLERANCE = 10.0
VECTOR_PADDING = 8.0
EXIT_INVALID_ARGS = 6
EXIT_OUTPUT_DIR = 7
EXIT_OPENCV_MISSING = 8
EXIT_POSTPROC_ARTIFACT = 9
EXIT_POSTPROC_DEP = 10
GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"
TEST_MODE_ENV = "TOMARKDOWN_TEST_MODE"
TEST_PIX2TEX_FORMULA_ENV = "TOMARKDOWN_TEST_PIX2TEX_FORMULA"
TEST_GEMINI_IMAGE_ENV = "TOMARKDOWN_TEST_GEMINI_IMAGE_ANNOTATION"
TEST_GEMINI_EQUATION_ENV = "TOMARKDOWN_TEST_GEMINI_EQUATION_ANNOTATION"
TEST_PIX2TEX_DEFAULT_FORMULA = r"\int_{0}^{1} x^2 \, dx = \frac{1}{3}"
TEST_GEMINI_IMAGE_DEFAULT = "Test image annotation generated during automated test execution."
TEST_GEMINI_EQUATION_DEFAULT = (
    "Test equation annotation generated during automated test execution.\n\n"
    "Representative LaTeX: $$ {formula} $$"
)
GITHUB_LATEST_RELEASE_URL = "https://api.github.com/repos/Ogekuri/toMarkdown/releases/latest"
UPDATE_CHECK_TIMEOUT_SECONDS = 1.0
PROMPT_EQUATION_DEFAULT = (
    """
You are annotating an image for Retrieval-Augmented Generation (RAG).
Goal: detailed, faithful description optimized for retrieval, clearly grounded explanation.

Return ENGLISH Markdown optimized for RAG with the following sections (keep headings exactly):

## Overview
One sentence describing what the image contains (e.g., "A single equation", "A system of equations with a diagram", etc.).

## Mathematical transcription
- Transcribe ALL mathematical expressions visible (even if multiple).
- Preserve symbols, subscripts/superscripts, Greek letters, limits, summations, matrices, piecewise definitions.
- If something is unreadable, write: [UNREADABLE] and do NOT guess.

## LaTeX (MathJax)
Provide the equation(s) as MathJax-ready LaTeX in Markdown:
- Use one or more display blocks:
  $$ ... $$
- If multiple equations, use separate $$ blocks, in reading order.
- Do NOT add extra equations not present in the image.

## Definitions / Variables (only if explicitly present)
List variable meanings ONLY if they are written in the image. Otherwise write "Not specified."

## Notes on layout (only if useful)
Mention important spatial structure: aligned equations, braces, arrows, numbered steps, boxed results, etc.

## Ambiguities / Unclear parts
Bullet list of any uncertain characters/symbols and where they appear.
"""
)
PROMPT_NON_EQUATION_DEFAULT = (
    """
You are annotating an image for Retrieval-Augmented Generation (RAG).
Goal: detailed, faithful description optimized for retrieval, clearly grounded explanation.

Return ENGLISH Markdown optimized for RAG with the following sections (keep headings exactly):

## Overview
One sentence describing the image type (photo, diagram, chart, UI screenshot, table, flowchart, etc.).

## Visible text (verbatim)
Transcribe all readable text exactly as shown (line breaks if meaningful).
If text is unreadable, write: [UNREADABLE] and do NOT guess.

## Entities and layout
Describe the layout and key elements (objects, labels, axes, boxes, arrows, regions, legend, callouts).
Including all details useful to understand mathematical graphs, processes flows, flow charts, temporal diagrams, mind maps and graphs behaviors.
If there are flows/process steps, describe them in order.

## Tables (if any)
Recreate any table as Markdown table, preserving headers and cell values.
If a cell is unreadable, use [UNREADABLE].

## Quantities / Data (if any)
List numeric values, units, ranges, axis ticks, categories exactly as visible.

## Ambiguities / Unclear parts
Bullet list of any uncertain text/labels and where they appear.
"""
)
PROMPT_UNCERTAIN_DEFAULT = (
    """
You are annotating an image for Retrieval-Augmented Generation (RAG).
Goal: detailed, faithful description optimized for retrieval, clearly grounded explanation.

First decide whether the image contains a mathematical equation/expression that should be transcribed as LaTeX.
Then produce ENGLISH Markdown optimized for RAG in ONE of the two formats below.

### If the image contains mathematical equation(s):
Use EXACTLY these sections:

## Overview
One sentence describing the content.

## Classification
Equation: YES (confidence 0-100)

## Mathematical transcription
Transcribe ALL mathematical expressions visible. Do NOT guess unreadable parts; use [UNREADABLE].

## LaTeX (MathJax)
Provide ONLY the equation(s) that appear in the image as display blocks:
$$ ... $$
Use multiple blocks if needed, in reading order.

## Non-math context (if present)
Briefly describe any accompanying diagram/text/table that changes how the equation is read (e.g., variable definitions, constraints, figure references).

## Ambiguities / Unclear parts
List uncertain symbols/text and location.

### If the image does NOT contain equations:
Use EXACTLY these sections:

## Overview
One sentence describing the content.

## Classification
Equation: NO (confidence 0-100)

## Visible text (verbatim)
Transcribe all readable text exactly; use [UNREADABLE] when needed.

## Entities and layout
Describe the layout, objects, labels, arrows/flows, charts, and tables.
Including all details useful to understand mathematical graphs, processes flows, flow charts, temporal diagrams, mind maps and graphs behaviors.
If there are flows/process steps, describe them in order.

## Tables (if any)
Recreate as Markdown table.

## Ambiguities / Unclear parts
List uncertain parts and location.

Important rules:
- Do NOT invent equations or text.
- If unsure, choose the most likely classification but reflect uncertainty via confidence and Ambiguities.
"""
)
DEFAULT_PROMPTS = {
    "prompt_equation": PROMPT_EQUATION_DEFAULT.strip(),
    "prompt_non_equation": PROMPT_NON_EQUATION_DEFAULT.strip(),
    "prompt_uncertain": PROMPT_UNCERTAIN_DEFAULT.strip(),
}

TABLE_PLACEHOLDER_PREFIX = "TOMARKDOWN_TABLE_PLACEHOLDER_"


def _env_flag_enabled(value: Optional[str]) -> bool:
    """Interpreta una variabile di ambiente come flag booleano abilitato."""

    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "off", "no"}


def is_test_mode() -> bool:
    """Rileva la modalità di test tramite variabili d'ambiente o esecuzione pytest."""

    for key in (TEST_MODE_ENV, "PDF2TREE_TEST_MODE", "HTML2TREE_TEST_MODE"):
        env_flag = os.environ.get(key)
        if env_flag is not None:
            return _env_flag_enabled(env_flag)
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))


def _get_test_pix2tex_formula() -> str:
    """Restituisce la formula LaTeX fittizia per la modalità di test Pix2Tex."""

    for key in (TEST_PIX2TEX_FORMULA_ENV, "PDF2TREE_TEST_PIX2TEX_FORMULA", "HTML2TREE_TEST_PIX2TEX_FORMULA"):
        override = os.environ.get(key)
        if override is not None and override.strip():
            return override.strip()
    return TEST_PIX2TEX_DEFAULT_FORMULA


def _get_test_annotation_text(is_equation: bool, equation_text: Optional[str]) -> str:
    """Genera testo di annotazione deterministico in modalità test per immagini o equazioni."""

    if is_equation:
        for key in (TEST_GEMINI_EQUATION_ENV, "PDF2TREE_TEST_GEMINI_EQUATION_ANNOTATION", "HTML2TREE_TEST_GEMINI_EQUATION_ANNOTATION"):
            override = os.environ.get(key)
            if override is not None and override.strip():
                return override.strip()
        formula = equation_text or _get_test_pix2tex_formula() or TEST_PIX2TEX_DEFAULT_FORMULA
        return TEST_GEMINI_EQUATION_DEFAULT.format(formula=formula)
    for key in (TEST_GEMINI_IMAGE_ENV, "PDF2TREE_TEST_GEMINI_IMAGE_ANNOTATION", "HTML2TREE_TEST_GEMINI_IMAGE_ANNOTATION"):
        override = os.environ.get(key)
        if override is not None and override.strip():
            return override.strip()
    return TEST_GEMINI_IMAGE_DEFAULT


def _write_prompts_file(path: Path) -> None:
    """Scrive su disco i prompt di default creando le cartelle genitore."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(DEFAULT_PROMPTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_prompts_file(path: Path) -> Dict[str, str]:
    """Carica e valida un file JSON di prompt che deve contenere le tre chiavi richieste."""
    try:
        data_raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Unable to read prompts file {path}: {exc}") from exc

    prompts: Dict[str, str] = {}
    for key in ("prompt_equation", "prompt_non_equation", "prompt_uncertain"):
        value = data_raw.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Prompts file {path} missing non-empty key: {key}")
        prompts[key] = value.strip()
    return prompts


def select_annotation_prompt(is_equation: bool, pix2tex_executed: bool, config: "PostProcessingConfig") -> str:
    """Seleziona il prompt in base al tipo di immagine e all'esito dell'esecuzione Pix2Tex."""
    if pix2tex_executed:
        return config.prompt_equation if is_equation else config.prompt_non_equation
    return config.prompt_uncertain


def _resolve_log_level(verbose: bool, debug: bool) -> int:
    """Determina il livello di log partendo dai flag verbose/debug."""

    return logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)


def _configure_tomarkdown_logger(level: int) -> None:
    """Imposta il logger tomarkdown conservando handler e formato anche se cambia il root logger."""
    LOG.setLevel(level)
    LOG.propagate = False
    if not LOG.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        handler.setLevel(level)
        LOG.addHandler(handler)
    else:
        for handler in LOG.handlers:
            handler.setLevel(level)
            if handler.formatter is None:
                handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))


@dataclass
class PostProcessingConfig:
    """@brief Store runtime configuration for post-processing phases.
    @details Encapsulates CLI-derived feature flags and thresholds used by
    cleanup, TOC insertion, inline table expansion, Pix2Tex, and Gemini
    annotation stages.
    """

    equation_min_len: int
    verbose: bool
    debug: bool
    gemini_api_key: Optional[str]
    gemini_model: str
    gemini_module: str
    gemini_api_emulation: bool
    test_mode: bool
    disable_remove_small_images: bool
    disable_cleanup: bool
    add_toc: bool
    enable_inline_tables: bool
    enable_pictex: bool
    enable_gemini: bool
    enable_gemini_over_pixtex: bool
    min_size_x: int
    min_size_y: int
    prompt_equation: str
    prompt_non_equation: str
    prompt_uncertain: str
    skip_toc_validation: bool = False


def progress_label(prefix: str, current: int, total: int) -> str:
    """Restituisce un'etichetta di avanzamento leggibile (contatore e percentuale se nota)."""
    if total > 0:
        percent = (current / total) * 100.0
        return f"{prefix} [{current}/{total}] ({percent:.1f}%)"
    return f"{prefix} [{current}]"


def _progress_bar_line(current: int, total: int, width: int = 24) -> str:
    """Costruisce una barra di avanzamento ASCII per aggiornamenti in modalità verbose."""

    if total <= 0:
        return "[?]"
    clamped = max(0, min(current, total))
    filled = int((clamped / total) * width)
    filled = min(filled, width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def _log_verbose_progress(prefix: str, current: int, total: int, detail: Optional[str] = None) -> None:
    """Emette una riga di avanzamento con barra visiva solo in modalità verbose."""

    bar = _progress_bar_line(current, total)
    counter = f"[{current}/{total}]" if total > 0 else f"[{current}]"
    if total > 0:
        msg = f"{prefix} {bar} {counter} ({(current / total) * 100.0:.1f}%)"
    else:
        msg = f"{prefix} {bar} {counter}"
    if detail:
        msg = f"{msg} | {detail}"
    LOG.info(msg)


def setup_logging(verbose: bool, debug: bool) -> None:
    """Configura livello e formato del logging in base ai flag della CLI."""
    level = _resolve_log_level(verbose, debug)
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    _configure_tomarkdown_logger(level)


def _format_flag(value: bool) -> str:
    """Converte un booleano in etichetta ON/OFF."""

    return "ON" if value else "OFF"


def print_parameter_summary(
    *,
    args: argparse.Namespace,
    post_config: PostProcessingConfig,
    mode: str,
    source_path: Optional[Path],
    from_dir: Optional[Path],
    out_dir: Path,
    form_xobject_enabled: bool = False,
    vector_images_enabled: bool = False,
) -> None:
    """Stampa un riepilogo deterministico dei parametri CLI validati."""

    mode_desc = "conversion + post-processing"

    header_mm = 0.0 if getattr(args, "header", None) is None else float(args.header)
    footer_mm = 0.0 if getattr(args, "footer", None) is None else float(args.footer)
    start_page = getattr(args, "start_page", None) or 1
    page_count = getattr(args, "n_pages", None) or "ALL"

    pix2tex_active = bool(post_config.enable_pictex)
    remove_small_active = not post_config.disable_remove_small_images
    cleanup_active = not post_config.disable_cleanup
    toc_active = bool(post_config.add_toc)
    md_tables_active = bool(post_config.enable_inline_tables)
    gemini_active = bool(post_config.enable_gemini)
    gemini_over_pixtex_active = bool(post_config.enable_gemini_over_pixtex)
    gemini_key_present = bool(post_config.gemini_api_key)
    gemini_emulation_active = bool(post_config.gemini_api_emulation)

    mode_upper = mode.upper()
    source_pdf = str(source_path) if source_path is not None else "(not provided)"
    source_dir = str(from_dir) if from_dir is not None else "(not provided)"
    lines = [
        "Parameter summary:",
        f"  - Mode: {mode_upper} ({mode_desc})",
        f"  - Source PDF: {source_pdf}" if mode_upper == "PDF" else f"  - Source Dir: {source_dir}",
        f"  - Output directory: {out_dir}",
        f"  - Header/Footer crop (mm): {header_mm} / {footer_mm}" if mode_upper == "PDF" else "  - Header/Footer crop (mm): N/A",
        f"  - Page range: start={start_page}, count={page_count}" if mode_upper == "PDF" else "  - Page range: N/A",
        f"  - Verbose: {_format_flag(bool(args.verbose))}",
        f"  - Debug: {_format_flag(bool(args.debug))}",
        f"  - Form XObject: {_format_flag(form_xobject_enabled)}" if mode_upper == "PDF" else "  - Form XObject: N/A",
        f"  - Vector extraction: {_format_flag(vector_images_enabled)}" if mode_upper == "PDF" else "  - Vector extraction: N/A",
        f"  - Remove small images: {_format_flag(remove_small_active)} (min {post_config.min_size_x}x{post_config.min_size_y}px)",
        f"  - Cleanup: {_format_flag(cleanup_active)}",
        f"  - Add Markdown TOC: {_format_flag(toc_active)}",
        f"  - Inline tables: {_format_flag(md_tables_active)}",
        f"  - Pix2Tex: {_format_flag(pix2tex_active)} (threshold {post_config.equation_min_len})",
        f"  - Gemini annotation: {_format_flag(gemini_active)}",
        f"  - Gemini over Pix2Tex: {_format_flag(gemini_over_pixtex_active)}",
        f"  - Gemini API key: {_format_flag(gemini_key_present)}",
        f"  - Gemini emulation: {_format_flag(gemini_emulation_active)}",
        f"  - Gemini module/model: {post_config.gemini_module} / {post_config.gemini_model}",
    ]

    print("\n".join(lines))


def program_version() -> str:
    """Restituisce la versione del pacchetto, oppure 'unknown' se non disponibile."""
    try:
        from tomarkdown import __version__ as pkg_version  # type: ignore
    except Exception:
        pkg_version = "unknown"
    return str(pkg_version)


def _extract_numeric_version(text: str) -> Optional[str]:
    """Estrae una versione numerica tipo X.Y.Z da una stringa (es. tag GitHub `v0.0.7`)."""

    if not text:
        return None
    match = re.search(r"\d+(?:\.\d+)+", text.strip())
    if not match:
        return None
    return match.group(0)


def _version_tuple(version: str) -> Optional[Tuple[int, ...]]:
    """Converte una stringa versione numerica in tupla di interi per confronto."""

    normalized = _extract_numeric_version(version)
    if not normalized:
        return None
    try:
        parts = tuple(int(p) for p in normalized.split("."))
    except Exception:
        return None
    return parts


def _is_version_greater(candidate: str, current: str) -> bool:
    """Confronta due versioni numeriche; ritorna True se candidate > current."""

    cand_t = _version_tuple(candidate)
    curr_t = _version_tuple(current)
    if not cand_t or not curr_t:
        return False

    max_len = max(len(cand_t), len(curr_t))
    cand_padded = cand_t + (0,) * (max_len - len(cand_t))
    curr_padded = curr_t + (0,) * (max_len - len(curr_t))
    return cand_padded > curr_padded


def _fetch_latest_release_version(*, timeout_seconds: float) -> Optional[str]:
    """Interroga GitHub Releases per ottenere la versione latest; ritorna None su errore."""

    req = urllib.request.Request(
        GITHUB_LATEST_RELEASE_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "tomarkdown",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read()
    except Exception:
        return None

    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        return None

    tag = payload.get("tag_name") if isinstance(payload, dict) else None
    if not isinstance(tag, str) or not tag.strip():
        return None

    return _extract_numeric_version(tag.strip())


def maybe_print_new_version_notice(*, program_name: str = "tomarkdown") -> None:
    """Stampa un avviso se è disponibile una nuova versione; ignora errori e procede."""

    # CORE-DES-086: in modalità test non eseguire richieste di rete.
    if is_test_mode():
        return

    current = program_version()
    if not current or current == "unknown":
        return

    latest = _fetch_latest_release_version(timeout_seconds=UPDATE_CHECK_TIMEOUT_SECONDS)
    if not latest:
        return

    if not _is_version_greater(latest, current):
        return

    print(
        f"A new version of {program_name} is available: current {current}, latest {latest}. "
        f"To upgrade, run: {program_name} --upgrade"
    )


def run_self_upgrade(*, package_name: str = "tomarkdown") -> int:
    """Esegue l'upgrade del pacchetto tramite pip e ritorna un exit code."""

    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
    try:
        result = subprocess.run(cmd)
    except Exception as exc:
        print(f"Upgrade failed: {exc}")
        return 1
    return int(result.returncode)


def run_self_uninstall(*, package_name: str = "tomarkdown") -> int:
    """Disinstalla il pacchetto tramite pip e ritorna un exit code."""

    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package_name]
    try:
        result = subprocess.run(cmd)
    except Exception as exc:
        print(f"Uninstall failed: {exc}")
        return 1
    return int(result.returncode)


def print_program_banner(name: str = "tomarkdown") -> None:
    """Stampa il banner del programma con nome e versione."""
    print(f"*** {name} ({program_version()}) ***")


def start_phase(description: str) -> None:
    """Stampa il separatore che precede una fase di elaborazione."""
    print(f"\n--- {description} ---")


def end_phase() -> None:
    """Stampa il marcatore di completamento di una fase di elaborazione."""
    print("done.")


def slugify_filename(name: str) -> str:
    """Normalizza un nome file in uno slug sicuro per il filesystem."""
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name or "document"


def safe_write_text(path: Path, text: str) -> None:
    """Scrive testo su disco creando le cartelle necessarie e normalizzando le newline."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _json_default(obj: Any) -> Any:
    """Fallback JSON serializer for debug artifacts."""

    rect_types = (pymupdf.Rect,)
    irect_type = getattr(pymupdf, "IRect", None)
    if irect_type is not None:
        rect_types = rect_types + (irect_type,)
    if isinstance(obj, rect_types):
        return [float(obj.x0), float(obj.y0), float(obj.x1), float(obj.y1)]
    if isinstance(obj, Path):
        return obj.as_posix()
    return str(obj)


def write_table_json(path: Path, rows: List[List[str]]) -> None:
    """Scrive righe tabella in JSON creando la gerarchia di cartelle se mancante."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(rows, ensure_ascii=False, indent=2)
    path.write_text(payload + "\n", encoding="utf-8", newline="\n")


def unique_target(path: Path) -> Path:
    """Restituisce un percorso libero aggiungendo suffissi incrementali se il file esiste."""

    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    i = 1
    while True:
        candidate = path.with_name(f"{stem}__{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def normalize_path_for_md(p: str) -> str:
    """Normalizza un percorso per l'uso nei link Markdown."""

    p = p.replace("\\", "/")
    if p.startswith("file://"):
        p = p[len("file://") :]
    return p


def _pymupdf4llm_safe_dir(path: Path) -> Path:
    """Calcola una directory compatibile con pymupdf4llm senza rinominare la root di output."""

    resolved = path.expanduser().resolve()
    sanitized = resolved.as_posix()
    sanitized = (
        sanitized.replace("(", "-")
        .replace(")", "-")
        .replace("[", "-")
        .replace("]", "-")
        .replace(" ", "_")
        .replace(chr(0x2010), "-")
        .replace(chr(0x2011), "-")
        .replace(chr(0x2012), "-")
        .replace(chr(0x2013), "-")
        .replace(chr(0x2014), "-")
        .replace(chr(0x2015), "-")
        .replace(chr(0x2212), "-")
    )
    if sanitized == resolved.as_posix():
        return path
    safe_root = Path("/tmp/tomarkdown_safe")
    return safe_root / sanitized.lstrip("/")


def relative_to_output(path: Path, out_dir: Path) -> str:
    """Calcola un percorso relativo alla cartella di output, con fallback al nome file."""

    try:
        return str(path.resolve().relative_to(out_dir.resolve()))
    except Exception:
        return path.name


def _sanitize_printable_filename(name: str) -> str:
    """Normalizza i nomi file sostituendo spazi o caratteri non stampabili con '_' e forzando le minuscole."""

    if not name:
        return "image"
    cleaned: List[str] = []
    for ch in name:
        if ch == " ":
            cleaned.append("_")
        elif ch.isprintable():
            cleaned.append(ch)
        else:
            cleaned.append("_")
    sanitized = "".join(cleaned).lower()
    if not sanitized or not sanitized.strip("._"):
        return "image"
    return sanitized


_MARKDOWN_LINK_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!])")


def _unescape_markdown_link_target(url: str) -> str:
    """@brief Remove markdown escaping from a parsed link target."""

    return _MARKDOWN_LINK_ESCAPE_RE.sub(r"\1", url or "")


def _split_markdown_link(content: str) -> Tuple[str, Optional[str]]:
    """Separa l'URL e il titolo opzionale contenuti nei link Markdown."""

    content = (content or "").strip()
    match = re.search(r"\s+(\".*?\"|'.*?')$", content, re.DOTALL)
    if match:
        title = match.group(1)
        url = content[: match.start()].strip()
        return _unescape_markdown_link_target(url), title
    return _unescape_markdown_link_target(content), None


def delete_empty_folders(out_dir: Path, verbose: bool = False) -> None:
    """Elimina le cartelle images/tables se vuote salvo override via env."""

    if _env_flag_enabled(
        os.environ.get("TOMARKDOWN_PRESERVE_EMPTY_ASSET_TABLE_DIRS")
        or os.environ.get("PDF2TREE_PRESERVE_EMPTY_ASSET_TABLE_DIRS")
        or os.environ.get("HTML2TREE_PRESERVE_EMPTY_ASSET_TABLE_DIRS")
    ):
        if verbose:
            LOG.info("Preserving empty asset directories due to preserve-empty env flag")
        return
    for folder in ("images", "tables"):
        target = out_dir / folder
        if not target.exists() or not target.is_dir():
            continue
        try:
            next(target.iterdir())
            continue
        except StopIteration:
            pass
        try:
            target.rmdir()
            if verbose:
                LOG.info("Removed empty directory: %s", target)
        except Exception as exc:
            LOG.warning("Unable to remove empty directory %s: %s", target, exc)


def has_opencv() -> bool:
    """Verifica se OpenCV è importabile nell'ambiente corrente."""

    try:
        import cv2  # noqa: F401  # type: ignore[reportMissingImports]

        return True
    except Exception:
        return False


@dataclass
class TocNode:
    """@brief Represent a node in hierarchical TOC structures.
    @details Stores title, level, optional page/anchor metadata, and children.
    Used by TOC parsing, filtering, validation, and markdown generation stages.
    """

    title: str
    page: Optional[int]
    level: int
    anchor: Optional[str]
    children: List["TocNode"]


HeadingEntry = Tuple[int, str, Optional[Any]]


@dataclass
class TocValidationResult:
    """@brief Capture normalized TOC validation outcome.
    @details Stores pass/fail flag, normalized source/document title lists,
    mismatch tuples, aggregate counts, and root cause category.
    """

    ok: bool
    pdf_titles: List[str]
    md_titles: List[str]
    mismatches: List[Tuple[int, str, str]]
    pdf_count: int
    md_count: int
    reason: str


@dataclass
class HtmlTable:
    """@brief Store extracted HTML table payload and artifact metadata.
    @details Carries placeholder identity, generated filenames, markdown table
    rendering, and structured cell rows for file export.
    """

    index: int
    placeholder: str
    stem: str
    md: str
    rows: List[List[str]]


def build_toc_tree(toc_list: List[List[Any]]) -> TocNode:
    """Costruisce l'albero nidificato della TOC preservando la gerarchia."""
    root = TocNode(title="root", page=None, level=0, anchor=None, children=[])
    stack: List[TocNode] = [root]

    for entry in toc_list or []:
        if len(entry) < 2:
            continue
        level_raw, title_raw = entry[0], entry[1]
        try:
            level = int(level_raw)
        except Exception:
            continue
        title = str(title_raw).strip()
        if not title:
            continue
        page_no: Optional[int] = None
        anchor: Optional[str] = None
        if len(entry) >= 3:
            try:
                page_no = int(entry[2]) if entry[2] is not None else None
            except Exception:
                page_no = None
        if len(entry) >= 4:
            anchor = str(entry[3]).strip() if entry[3] else None

        node = TocNode(title=title, page=page_no, level=level, anchor=anchor, children=[])

        while stack and level <= stack[-1].level:
            stack.pop()
        parent = stack[-1] if stack else root
        parent.children.append(node)
        stack.append(node)

    return root


def serialize_toc_tree(node: TocNode) -> List[Dict[str, Any]]:
    """Serializza l'albero TOC in una lista di dizionari ricorsiva."""

    serialized: List[Dict[str, Any]] = []
    for child in node.children:
        entry: Dict[str, Any] = {
            "title": child.title,
            "children": serialize_toc_tree(child),
        }
        if child.page is not None:
            entry["pdf_source_page"] = child.page
        if child.anchor:
            entry["anchor"] = child.anchor
        serialized.append(entry)
    return serialized


def find_context_for_page(root: TocNode, page_no: Optional[int]) -> List[str]:
    """Individua il percorso di titoli che meglio corrisponde al numero di pagina."""
    if page_no is None:
        return []

    best_path: List[TocNode] = []
    best_page = -1
    fallback_path: List[TocNode] = []
    fallback_page: Optional[int] = None

    def dfs(node: TocNode, ancestors: List[TocNode]) -> None:
        nonlocal best_path, best_page, fallback_path, fallback_page
        current_path = ancestors + ([node] if node.level > 0 else [])
        if node.level > 0:
            if node.page is not None:
                if fallback_page is None or node.page < fallback_page:
                    fallback_page = node.page
                    fallback_path = current_path
                if node.page <= page_no:
                    if node.page > best_page:
                        best_page = node.page
                        best_path = current_path
        for child in node.children:
            dfs(child, current_path)

    dfs(root, [])
    if best_path:
        return [n.title for n in best_path]
    return [n.title for n in fallback_path]


def find_context(
    toc_path: Optional[Path],
    toc_root: Optional[TocNode],
    asset_names: Iterable[str],
    fallback_page: Optional[int],
) -> Tuple[List[str], str]:
    """Trova il contesto di un asset usando la TOC Markdown disponibile e in fallback la TOC del PDF."""

    names = {n for n in asset_names if n}
    if toc_path and toc_path.exists() and names:
        try:
            lines = toc_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            lines = []

        heading_re = re.compile(r"^(?P<indent>\s*)-\s*\[(?P<title>[^\]]+)\]\([^)]*\)")
        stack: List[str] = []
        found: Optional[List[str]] = None

        for raw in lines:
            if not raw.strip():
                continue
            h_match = heading_re.match(raw)
            if h_match:
                indent = h_match.group("indent")
                level = int(len(indent) / 2) + 1
                title = h_match.group("title").strip()

                while len(stack) >= level:
                    stack.pop()
                while len(stack) < level - 1:
                    stack.append("")
                stack.append(title)
                continue

            if any(name in raw for name in names):
                found = [item for item in stack if item]
                break

        if found is not None:
            context_path = list(found)
            context_str = " > ".join(context_path)
            return context_path, context_str

    context_titles = (
        find_context_for_page(toc_root or build_toc_tree([]), fallback_page)
        if fallback_page is not None
        else []
    )
    context_str = " > ".join(context_titles)
    return context_titles, context_str


def build_context_metadata(context_titles: List[str]) -> Tuple[str, List[str]]:
    """Costruisce `context` e `context_path` usando solo i titoli TOC trovati."""

    context_path = list(context_titles)
    context_str = " > ".join(context_path)
    return context_str, context_path


PAGE_IN_NAME_RE = re.compile(r"-([0-9]{3,4})-")


def guess_page_from_filename(name: str) -> Optional[int]:
    """Prova a dedurre il numero di pagina da un nome file."""

    match = PAGE_IN_NAME_RE.search(name)
    if match:
        try:
            return int(match.group(1))
        except Exception:
            return None
    alt = re.search(r"page[_-]?([0-9]{3,4})", name, re.IGNORECASE)
    if alt:
        try:
            return int(alt.group(1))
        except Exception:
            return None
    return None


IMG_LINK_RE = re.compile(r"(!\\?\[[^\]]*\\?\]\()([^\)]+)(\))")
MULTILINE_IMG_RE = re.compile(r"!\\?\[[^\]]*\\?\]\((?:.|\n)*?\)", re.MULTILINE)
DIRECT_IMG_LINK_RE = re.compile(r"(\[[^\]]+\]\()([^\)]+)(\))(?=\s*$)", re.MULTILINE)


def _rewrite_image_links(md_text: str, mapping: Dict[str, str]) -> str:
    """Riscrive i link immagine nel Markdown applicando una mappa (supporta basename o full path)."""

    if not md_text or not mapping:
        return md_text

    def _rewrite_target(content: str) -> Optional[str]:
        url, suffix = _split_markdown_link(content)
        raw = url.strip().strip('"').strip("'")
        url_norm = normalize_path_for_md(raw)
        fragment = ""
        query = ""
        base = url_norm
        if "#" in base:
            base, frag = base.split("#", 1)
            fragment = f"#{frag}"
        if "?" in base:
            base, qry = base.split("?", 1)
            query = f"?{qry}"

        # Prova prima con il percorso completo normalizzato
        renamed = mapping.get(base)
        if not renamed:
            # Fallback al basename per compatibilità
            base_path = Path(base)
            renamed = mapping.get(base_path.name)
            if renamed:
                # Se il mapping è basename->basename, ricostruisci il percorso completo
                new_base = str(base_path.with_name(renamed)) if base_path.name != base else renamed
            else:
                return None
        else:
            # Il mapping ha restituito un percorso completo
            new_base = renamed

        new_url = f"{new_base}{query}{fragment}"
        if content.strip().startswith("<"):
            new_url = f"<{new_url}>"
        if suffix:
            new_url = f"{new_url} {suffix}"
        return new_url

    def repl(match: re.Match) -> str:
        before, content, after = match.group(1), match.group(2), match.group(3)
        new_url = _rewrite_target(content)
        if not new_url:
            return match.group(0)
        return f"{before}{new_url}{after}"

    def repl_direct(match: re.Match) -> str:
        before, content, after = match.group(1), match.group(2), match.group(3)
        new_url = _rewrite_target(content)
        if not new_url:
            return match.group(0)
        label = before[1:-2]
        # Strip trailing backslash from label (escaped bracket handling)
        label_clean = label.rstrip("\\")
        if label_clean.strip() == content.strip():
            before = f"[{new_url}]("
        return f"{before}{new_url}{after}"

    updated = IMG_LINK_RE.sub(repl, md_text)
    updated = DIRECT_IMG_LINK_RE.sub(repl_direct, updated)
    return updated


def extract_image_basenames_from_markdown(md: str) -> Set[str]:
    """Estrae i basename dei file immagine presenti nei link Markdown."""

    out: Set[str] = set()
    for match in IMG_LINK_RE.finditer(md or ""):
        url_part, _ = _split_markdown_link(match.group(2))
        url = normalize_path_for_md(url_part)
        url = url.split("?", 1)[0].split("#", 1)[0]
        base = url.split("/")[-1].strip()
        if base:
            out.add(base)
    return out


def extract_image_paths_from_markdown(md: str) -> List[str]:
    """Estrae i percorsi normalizzati delle immagini dai link Markdown."""

    paths: List[str] = []
    for match in IMG_LINK_RE.finditer(md or ""):
        url_part, _ = _split_markdown_link(match.group(2))
        raw = url_part.strip().strip("\"").strip("'")
        if not raw:
            continue
        if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("mailto:") or raw.startswith("//"):
            continue
        url = normalize_path_for_md(raw)
        url = url.split("?", 1)[0].split("#", 1)[0]
        if url:
            paths.append(url)
    return paths


def extract_equation_basenames_from_markdown(md: str) -> Set[str]:
    """Estrae i basename delle immagini marcate come equazioni nel Markdown."""

    bases: Set[str] = set()
    for line in (md or "").splitlines():
        match = EQUATION_BLOCK_START_RE.match(line.strip())
        if match:
            base = match.group(1).strip()
            if base:
                bases.add(base)
    return bases


def extract_image_basenames_in_order(md: str) -> List[str]:
    """Restituisce i basename delle immagini nell'ordine in cui compaiono nel Markdown."""

    ordered: List[str] = []
    for match in IMG_LINK_RE.finditer(md or ""):
        url_part, _ = _split_markdown_link(match.group(2))
        url = normalize_path_for_md(url_part)
        url = url.split("?", 1)[0].split("#", 1)[0]
        base = url.split("/")[-1].strip()
        if base:
            ordered.append(base)
    return ordered


def rewrite_image_links_to_images_subdir(md: str, subdir: str = "images") -> str:
    """Forza tutti i link immagine a puntare a images/<basename>."""

    def repl(match: re.Match) -> str:
        before, url, after = match.group(1), match.group(2), match.group(3)
        url_clean = normalize_path_for_md(url.strip().strip('"').strip("'"))
        url_clean = url_clean.split("?", 1)[0].split("#", 1)[0]
        base = url_clean.split("/")[-1]
        return f"{before}{subdir}/{base}{after}"

    return IMG_LINK_RE.sub(repl, md)


def rewrite_image_links_to_assets_subdir(md: str, subdir: str = "images") -> str:
    """Riscrive i link immagine puntandoli a assets/images dove possibile."""

    def repl(match: re.Match) -> str:
        before, content, after = match.group(1), match.group(2), match.group(3)
        url, title = _split_markdown_link(content)
        url_clean = normalize_path_for_md(url)
        url_clean = url_clean.split("?", 1)[0].split("#", 1)[0]
        if "/assets/" in f"/{url_clean}":
            idx = f"/{url_clean}".rfind("/assets/")
            rel = f"/{url_clean}"[idx + len("/assets/") :]
        elif "/images/" in f"/{url_clean}":
            idx = f"/{url_clean}".rfind("/images/")
            rel = f"/{url_clean}"[idx + len("/images/") :]
        elif url_clean.startswith("assets/"):
            rel = url_clean[len("assets/") :]
        elif url_clean.startswith("images/"):
            rel = url_clean[len("images/") :]
        else:
            rel = url_clean.split("/")[-1]
        rel = rel.lstrip("/")
        new_url = f"{subdir}/{rel}"
        if title:
            return f"{before}{new_url} {title}{after}"
        return f"{before}{new_url}{after}"

    return IMG_LINK_RE.sub(repl, md)


def sanitize_image_links(md: str) -> str:
    """Normalizza i link immagine multi-linea generati da markdownify."""

    def fix_match(match: re.Match) -> str:
        raw = match.group(0)
        return re.sub(r"\\s+", " ", raw)

    return MULTILINE_IMG_RE.sub(fix_match, md)


def _strip_heading_inline_formatting(text: str) -> str:
    """Rimuove formattazione inline Markdown mantenendo il testo semplice."""

    current = re.sub(r"\\([`*_])", r"\1", text or "").strip()
    while current:
        updated = current
        if len(updated) >= 2 and updated.startswith("`") and updated.endswith("`"):
            updated = updated[1:-1].strip()
        elif ((updated.startswith("**") and updated.endswith("**"))
              or (updated.startswith("__") and updated.endswith("__"))):
            updated = updated[2:-2].strip()
        elif ((updated.startswith("*") and updated.endswith("*"))
              or (updated.startswith("_") and updated.endswith("_"))):
            updated = updated[1:-1].strip()
        if updated == current:
            break
        current = updated
    return current


def _normalize_markdown_heading_text(md_text: str) -> str:
    """Normalizza i titoli heading a testo semplice rimuovendo formattazione inline."""

    lines = md_text.splitlines()
    fenced_lines = _get_fenced_line_mask(lines)
    heading_re = re.compile(r"^(?P<prefix>\s*#{1,}\s+)(?P<title>.+?)\s*$")
    for idx, line in enumerate(lines):
        if idx in fenced_lines:
            continue
        match = heading_re.match(line)
        if not match:
            continue
        title_plain = _strip_heading_inline_formatting(match.group("title"))
        lines[idx] = f"{match.group('prefix')}{title_plain}"
    result = "\n".join(lines)
    if md_text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


_MARKDOWN_DECORATION_RE = re.compile(r"[`*_]+")
_CODE_FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
_DASH_FENCE_RE = re.compile(r"^[ \t]{0,3}(-{3,})\s*$")


def _strip_markdown_decoration(text: str) -> str:
    """@brief Remove inline markdown decoration markers from text."""

    return _MARKDOWN_DECORATION_RE.sub("", text or "")


def _update_fence_stack(stack: List[Tuple[str, int]], line: str) -> bool:
    """@brief Update fenced-block parser state for the current line."""

    code_match = _CODE_FENCE_RE.match(line)
    if code_match:
        seq = code_match.group(1)
        ch = seq[0]
        length = len(seq)
        if stack and stack[-1][0] == ch and length >= stack[-1][1]:
            stack.pop()
        else:
            stack.append((ch, length))
        return True

    dash_match = _DASH_FENCE_RE.match(line)
    if dash_match:
        seq = dash_match.group(1)
        length = len(seq)
        if stack:
            if stack[-1][0] != "-":
                return False
            if length >= stack[-1][1]:
                stack.pop()
                return True
            return False
        stack.append(("-", length))
        return True

    return False


def _split_markdown_by_fences(md_text: str) -> List[Tuple[bool, str]]:
    """@brief Split markdown into alternating fenced and unfenced segments."""

    if not md_text:
        return [(False, md_text)]

    segments: List[Tuple[bool, str]] = []
    current: List[str] = []
    fence_stack: List[Tuple[str, int]] = []
    in_fence = False

    for line in md_text.splitlines(keepends=True):
        line_no_nl = line.rstrip("\n")
        is_fence = _update_fence_stack(fence_stack, line_no_nl)
        if is_fence:
            if in_fence:
                current.append(line)
                segments.append((True, "".join(current)))
                current = []
                in_fence = False
            else:
                if current:
                    segments.append((False, "".join(current)))
                    current = []
                current.append(line)
                in_fence = True
            continue
        current.append(line)

    if current:
        segments.append((in_fence, "".join(current)))

    return segments


def _apply_outside_fences(md_text: str, fn: Callable[[str], str]) -> str:
    """@brief Apply a transform only on unfenced markdown segments."""

    if not md_text:
        return md_text
    segments = _split_markdown_by_fences(md_text)
    return "".join(segment if is_fenced else fn(segment) for is_fenced, segment in segments)


def _get_fenced_line_mask(lines: List[str]) -> Set[int]:
    """@brief Compute line indexes covered by active markdown fences."""

    fence_stack: List[Tuple[str, int]] = []
    fenced: Set[int] = set()
    for idx, line in enumerate(lines):
        if _update_fence_stack(fence_stack, line):
            fenced.add(idx)
            continue
        if fence_stack:
            fenced.add(idx)
    return fenced


def _escape_unbalanced_underscores(text: str) -> str:
    """@brief Escape unbalanced boundary underscores while preserving balanced ones."""

    if "_" not in text:
        return text

    def repl(match: re.Match) -> str:
        token = match.group(0)
        if "_" not in token:
            return token
        if set(token) == {"_"}:
            return token
        leading = len(token) - len(token.lstrip("_"))
        trailing = len(token) - len(token.rstrip("_"))
        if leading > 1 or trailing > 1:
            return token
        core = token[leading : len(token) - trailing]
        if not core:
            return token
        if leading and trailing:
            return token
        escaped = []
        if leading:
            escaped.append("\\_" * leading)
        escaped.append(core)
        if trailing:
            escaped.append("\\_" * trailing)
        return "".join(escaped)

    return re.sub(r"(?<!\\)[A-Za-z0-9_\[\]\(\)\-\.\:\\]+", repl, text)


def _normalize_underscore_escapes(text: str) -> str:
    """@brief Normalize underscore escaping according to markdown-safe rules."""

    if "\\_" not in text and "_" not in text:
        return text
    unescaped = text.replace("\\_", "_")
    return _escape_unbalanced_underscores(unescaped)


def _normalize_markdown_underscores(md_text: str) -> str:
    """@brief Normalize underscore escaping outside fenced/code regions."""

    if "\\_" not in md_text and "_" not in md_text:
        return md_text

    def _normalize_segment(segment: str) -> str:
        lines: List[str] = []
        for line in segment.splitlines():
            if "`" not in line:
                lines.append(_normalize_underscore_escapes(line))
                continue

            parts = line.split("`")
            for idx in range(0, len(parts), 2):
                parts[idx] = _normalize_underscore_escapes(parts[idx])
            lines.append("`".join(parts))

        result = "\n".join(lines)
        if segment.endswith("\n") and not result.endswith("\n"):
            result += "\n"
        return result

    return _apply_outside_fences(md_text, _normalize_segment)


def _normalize_table_cell_text(text: str) -> str:
    """@brief Normalize whitespace/newline escapes in table cell text."""

    cleaned = text.replace("\\n", " ")
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _split_markdown_table_row(line: str) -> List[str]:
    """@brief Split a markdown pipe row preserving escaped separators."""

    stripped = (line or "").strip()
    if not stripped:
        return []

    cells: List[str] = []
    buf: List[str] = []
    escape = False
    for ch in stripped:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\":
            escape = True
            buf.append(ch)
            continue
        if ch == "|":
            cells.append("".join(buf))
            buf = []
            continue
        buf.append(ch)

    cells.append("".join(buf))
    if stripped.startswith("|") and cells:
        cells = cells[1:]
    if stripped.endswith("|") and cells:
        cells = cells[:-1]

    return [cell.strip() for cell in cells]


def _is_markdown_table_separator(line: str) -> bool:
    """@brief Detect markdown table separator rows."""

    return bool(re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$", line or ""))


def _parse_markdown_table_rows(md_text: str) -> List[List[str]]:
    """Estrae le righe di una tabella Markdown con pipe, ignorando la riga di separazione."""

    rows: List[List[str]] = []
    in_table = False
    for line in (md_text or "").splitlines():
        if "|" not in (line or ""):
            if in_table:
                break
            continue

        in_table = True
        if _is_markdown_table_separator(line):
            continue
        cells = _split_markdown_table_row(line)
        if not cells:
            continue
        cleaned = [cell.replace("\\|", "|") for cell in cells]
        rows.append(cleaned)

    return rows


def _sanitize_table_cell(text: str) -> str:
    """@brief Escape markdown-sensitive characters in table cell output."""

    cleaned = _normalize_table_cell_text(text)
    specials = "\\\\`*{}[]()#+-.!|"
    escaped: List[str] = []
    for ch in cleaned:
        escaped.append(f"\\\\{ch}" if ch in specials else ch)
    return _normalize_underscore_escapes("".join(escaped))


def html_table_to_markdown(table) -> Tuple[str, List[List[str]]]:
    """@brief Convert one HTML table node to markdown text and structured rows."""

    rows: List[List[str]] = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        row_text = [_normalize_table_cell_text(cell.get_text(" ", strip=True)) for cell in cells]
        rows.append(row_text)

    if not rows:
        return "", []

    max_cols = max(len(r) for r in rows)
    padded = [r + [""] * (max_cols - len(r)) for r in rows]
    header = padded[0]
    body = padded[1:]

    md_lines = [
        "| " + " | ".join(_sanitize_table_cell(c) for c in header) + " |",
        "| " + " | ".join(["---"] * max_cols) + " |",
    ]
    for row in body:
        md_lines.append("| " + " | ".join(_sanitize_table_cell(c) for c in row) + " |")

    return "\n".join(md_lines), padded


def extract_tables_from_html(soup) -> List[HtmlTable]:
    """@brief Extract HTML tables, replace with placeholders, and build table models."""

    tables = soup.find_all("table")
    outputs: List[HtmlTable] = []
    used_stems: Set[str] = set()

    for idx, table in enumerate(tables, start=1):
        table_id = table.get("id") or f"table-{idx:03d}"
        base_stem = slugify_filename(str(table_id))
        stem = base_stem
        suffix = 1
        while stem in used_stems:
            stem = f"{base_stem}__{suffix}"
            suffix += 1
        used_stems.add(stem)

        md, rows = html_table_to_markdown(table)
        placeholder = f"{TABLE_PLACEHOLDER_PREFIX}{idx:03d}"
        placeholder_tag = soup.new_tag("p")
        placeholder_tag.string = placeholder
        table.replace_with(placeholder_tag)

        outputs.append(HtmlTable(index=idx, placeholder=placeholder, stem=stem, md=md, rows=rows))

    return outputs


def replace_table_placeholders(md_text: str, tables: List[HtmlTable]) -> str:
    """
    Sostituisce i placeholder delle tabelle HTML con i marker e link ai file.
    Non inserisce mai il contenuto inline (DES-029, REQ-019).
    """
    if not tables:
        return md_text

    def _placeholder_pattern(placeholder: str) -> re.Pattern[str]:
        parts: List[str] = []
        for ch in placeholder:
            if ch == "_":
                parts.append(r"\\?_")
            else:
                parts.append(re.escape(ch))
        return re.compile("".join(parts))

    patterns: List[Tuple[re.Pattern[str], HtmlTable]] = [
        (_placeholder_pattern(table.placeholder), table) for table in tables
    ]

    lines = md_text.splitlines()
    output: List[str] = []

    for line in lines:
        stripped = line.strip()
        matched_table: Optional[HtmlTable] = None
        for pattern, table in patterns:
            if pattern.search(stripped):
                matched_table = table
                break

        if matched_table is None:
            output.append(line)
            continue

        # Always insert only links, never inline content (DES-029, REQ-019)
        output.append("")
        output.append("<!-- Start of table -->")
        output.append("")
        output.append(f"[Markdown](tables/{matched_table.stem}.md)")
        output.append("")
        output.append(f"[JSON](tables/{matched_table.stem}.json)")
        output.append("")
        output.append("<!-- End of table -->")
        output.append("")

    result = "\n".join(output)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def export_html_tables_files(tables_dir: Path, tables: List[HtmlTable]) -> List[List[Path]]:
    """@brief Persist extracted HTML table markdown/json files to disk."""

    tables_dir.mkdir(parents=True, exist_ok=True)
    exported: List[List[Path]] = []
    for table in tables:
        files: List[Path] = []
        if table.md.strip():
            path_md = tables_dir / f"{table.stem}.md"
            safe_write_text(path_md, table.md.strip() + "\n")
            files.append(path_md)
        if table.rows:
            path_json = tables_dir / f"{table.stem}.json"
            write_table_json(path_json, table.rows)
            files.append(path_json)
        if files:
            exported.append(files)
    return exported


def yaml_front_matter(metadata: dict, source_path: Path, page_count: int) -> str:
    """Crea il front matter YAML con i metadati del PDF."""

    def clean(value: Any) -> str:
        text = str(value).replace("\n", " ").strip()
        text = text.replace('"', "'")
        return text

    title = clean(metadata.get("title", "")) if metadata else ""
    author = clean(metadata.get("author", "")) if metadata else ""
    subject = clean(metadata.get("subject", "")) if metadata else ""
    creator = clean(metadata.get("creator", "")) if metadata else ""

    lines = [
        "---",
        f'source_file: "{clean(source_path.name)}"',
        f"page_count: {page_count}",
    ]
    if title:
        lines.append(f'title: "{title}"')
    if author:
        lines.append(f'author: "{author}"')
    if subject:
        lines.append(f'subject: "{subject}"')
    if creator:
        lines.append(f'creator: "{creator}"')
    lines.append("---\n")
    return "\n".join(lines)


def build_toc_markdown(toc: Union[List[List[Any]], str]) -> str:
    """Genera la sezione Markdown della TOC con marker e link markdown."""

    if not toc:
        return ""

    if isinstance(toc, str):
        content = toc.strip("\n")
        if not content:
            return ""
        toc_lines = content.splitlines()
    else:
        toc_lines = []
        for level, title, page_no in toc:
            indent = "  " * max(0, int(level) - 1)
            safe_title = str(title).strip()
            anchor = _slugify_markdown_heading(safe_title)
            toc_lines.append(f"{indent}- [{safe_title}](#{anchor})")

    lines: List[str] = [
        "<!-- start of toc -->",
        "",
        "** TOC **",
        *toc_lines,
        "",
        "<!-- end of toc -->",
    ]
    return "\n".join(lines)


def build_document_toc_content(
    toc: List[HeadingEntry],
    *,
    page_start: Optional[int] = None,
    page_end: Optional[int] = None,
) -> str:
    """Genera il contenuto testuale della TOC basandosi sulla TOC PDF filtrata.

    Il filtraggio garantisce che la TOC in memoria contenga ESCLUSIVAMENTE gli heading
    delle pagine processate secondo i parametri --start-page e --n-pages.
    Heading al di fuori del range vengono esclusi dalla TOC generata.
    """

    if not toc:
        return ""

    lines: List[str] = []
    for entry in toc:
        if len(entry) < 2:
            continue
        try:
            level = int(entry[0])
        except Exception:
            level = 1
        title = str(entry[1]).strip()
        if not title:
            continue
        page_no: Optional[int] = None
        if len(entry) >= 3 and entry[2] is not None:
            try:
                page_no = int(entry[2])
            except Exception:
                page_no = None
        if page_start is not None and page_end is not None:
            if page_no is None or not (page_start <= page_no <= page_end):
                continue
        indent = "  " * max(0, level - 1)
        anchor = _slugify_markdown_heading(title)
        lines.append(f"{indent}- [{title}](#{anchor})")

    content = "\n".join(lines).strip()
    return f"{content}\n" if content else ""


def looks_like_markdown_table(text: str) -> bool:
    """Verifica se un testo assomiglia a una tabella Markdown."""

    if "|" not in (text or ""):
        return False
    if re.search(r"^\s*\|?.+\|.+\|?\s*$", text or "", flags=re.MULTILINE) and re.search(
        r"^\s*\|?\s*:?-{2,}:?\s*\|", text or "", flags=re.MULTILINE
    ):
        return True
    return False


def extract_tables_fallback(doc: Any, page_index: int) -> List[Tuple[str, List[List[str]]]]:
    """Esegue l'estrazione di tabelle via fallback PyMuPDF se disponibile."""

    page = doc[page_index]
    try:
        tables = page.find_tables()
    except Exception as exc:  # pragma: no cover - dipende dal supporto PyMuPDF
        LOG.debug("find_tables failed on page %d: %s", page_index + 1, exc)
        return []

    results: List[Tuple[str, List[List[str]]]] = []
    for table in getattr(tables, "tables", []) or []:
        md = ""
        rows: List[List[str]] = []

        try:
            if hasattr(table, "to_markdown"):
                md = table.to_markdown() or ""
        except Exception as exc:
            LOG.debug("Table.to_markdown failed page %d: %s", page_index + 1, exc)

        try:
            raw = table.extract()
            if isinstance(raw, list):
                rows = [[_normalize_table_cell_text("" if cell is None else str(cell)) for cell in row] for row in raw]
        except Exception as exc:
            LOG.debug("Table.extract failed page %d: %s", page_index + 1, exc)

        if md.strip() and looks_like_markdown_table(md):
            parsed_rows = _parse_markdown_table_rows(md)
            if parsed_rows:
                rows = parsed_rows

        if md.strip() or rows:
            results.append((md, rows))
    return results


def export_tables_files(tables_dir: Path, page_no: int, tables: List[Tuple[str, List[List[str]]]]) -> List[List[Path]]:
    """Esporta le tabelle estratte in Markdown e JSON restituendo i percorsi creati."""

    tables_dir.mkdir(parents=True, exist_ok=True)
    exported: List[List[Path]] = []
    for t_idx, (table_md, table_rows) in enumerate(tables, start=1):
        stem = f"page-{page_no:03d}-table-{t_idx:02d}"
        files: List[Path] = []
        if table_md.strip():
            path_md = tables_dir / f"{stem}.md"
            safe_write_text(path_md, table_md.strip() + "\n")
            files.append(path_md)
        if table_rows:
            path_json = tables_dir / f"{stem}.json"
            write_table_json(path_json, table_rows)
            files.append(path_json)
        if files:
            exported.append(files)
    return exported


def format_table_references(exported: List[List[Path]], out_dir: Path) -> List[str]:
    """Crea i riferimenti Markdown per ogni tabella esportata, restituendo blocchi separati."""

    blocks: List[str] = []
    for files in exported:
        rel_md: Optional[str] = None
        rel_json: Optional[str] = None
        for path in files:
            rel = relative_to_output(path, out_dir)
            if path.suffix.lower() == ".md":
                rel_md = rel
            elif path.suffix.lower() == ".json":
                rel_json = rel

        lines: List[str] = ["", "<!-- Start of table -->", ""]
        if rel_md:
            lines.append(f"[Markdown]({rel_md})")
            lines.append("")
        if rel_json:
            lines.append(f"[JSON]({rel_json})")
            lines.append("")
        lines.append("<!-- End of table -->")
        lines.append("")

        blocks.append("\n".join(lines) + "\n")

    return blocks


IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mat_mul(A: Tuple[float, float, float, float, float, float], B: Tuple[float, float, float, float, float, float]) -> Tuple[float, float, float, float, float, float]:
    """Esegue la moltiplicazione di due matrici di trasformazione 2D affine."""

    a, b, c, d, e, f = A
    a2, b2, c2, d2, e2, f2 = B
    return (
        a * a2 + b * c2,
        a * b2 + b * d2,
        c * a2 + d * c2,
        c * b2 + d * d2,
        e * a2 + f * c2 + e2,
        e * b2 + f * d2 + f2,
    )


def apply_mat(M: Tuple[float, float, float, float, float, float], x: float, y: float) -> Tuple[float, float]:
    """Applica una trasformazione affine 2D a un punto."""

    a, b, c, d, e, f = M
    return (a * x + c * y + e, b * x + d * y + f)


def parse_content_tokens(stream_bytes: bytes) -> List[bytes]:
    """Tokenizza lo stream di contenuto PDF in nomi e numeri utili all'analisi."""

    return re.findall(rb"/[A-Za-z0-9_.]+|[-+]?\d*\.?\d+|[A-Za-z]+", stream_bytes)


@dataclass
class FormPlacement:
    """@brief Represent one detected Form XObject placement.
    @details Captures object name, xref identifier, geometric bounds, applied
    transformation matrix, mapped PyMuPDF rectangle, and occurrence order.
    """

    name: str
    xref: int
    bbox: Tuple[float, float, float, float]
    ctm: Tuple[float, float, float, float, float, float]
    rect_mupdf: pymupdf.Rect
    order: int


def get_xobject_subtype_and_bbox(doc: pymupdf.Document, xref: int) -> Tuple[Optional[str], Optional[Tuple[float, float, float, float]]]:
    """Recupera subtype e bounding box di uno XObject a partire dal suo xref."""

    source = doc.xref_object(xref) or ""
    subtype_match = re.search(r"/Subtype\s*/([A-Za-z0-9]+)", source)
    subtype = subtype_match.group(1) if subtype_match else None
    bbox_match = re.search(r"/BBox\s*\[\s*([0-9.\-]+)\s+([0-9.\-]+)\s+([0-9.\-]+)\s+([0-9.\-]+)\s*\]", source)
    bbox = None
    if bbox_match:
        bbox = (
            float(bbox_match.group(1)),
            float(bbox_match.group(2)),
            float(bbox_match.group(3)),
            float(bbox_match.group(4)),
        )
    return subtype, bbox


def find_form_placements_on_page(doc: pymupdf.Document, page: pymupdf.Page, page_no: int, debug: bool = False) -> List[FormPlacement]:
    """Parse page content stream to locate Form XObject placements with approximate bounding boxes."""
    xobjs = page.get_xobjects() or []
    by_name: Dict[str, int] = {}
    for entry in xobjs:
        xref = int(entry[0])
        name = str(entry[1])
        by_name[name] = xref
    if not by_name:
        return []

    try:
        mediabox = getattr(page, "mediabox", None)
        base_height = float(mediabox.height) if mediabox else float(page.rect.height)
    except Exception:
        base_height = float(page.rect.height)

    cropbox = getattr(page, "cropbox", None)
    crop_x0 = float(getattr(cropbox, "x0", 0.0) if cropbox else 0.0)
    crop_y0 = float(getattr(cropbox, "y0", 0.0) if cropbox else 0.0)
    top_ref = float(base_height - crop_y0)
    crop_height = float(getattr(cropbox, "height", 0.0) if cropbox else 0.0)
    if crop_height <= 0.0:
        crop_height = float(base_height)

    stream_all = b""
    for content_xref in page.get_contents() or []:
        try:
            part = doc.xref_stream(content_xref)
            if part:
                stream_all += part + b"\n"
        except Exception:
            pass

    tokens = parse_content_tokens(stream_all)

    placements: List[FormPlacement] = []
    ctm = IDENT
    stack: List[Tuple[float, float, float, float, float, float]] = []
    last_nums: List[float] = []
    last_name: Optional[str] = None
    order = 0

    meta_cache: Dict[int, Tuple[Optional[str], Optional[Tuple[float, float, float, float]]]] = {}

    for tok in tokens:
        if re.fullmatch(rb"[-+]?\d*\.?\d+", tok):
            last_nums.append(float(tok))
            continue

        if tok == b"q":
            stack.append(ctm)
            last_nums.clear()
            last_name = None
            continue

        if tok == b"Q":
            ctm = stack.pop() if stack else IDENT
            last_nums.clear()
            last_name = None
            continue

        if tok == b"cm":
            if len(last_nums) >= 6:
                a, b, c, d, e, f = last_nums[-6:]
                M = (a, b, c, d, e, f)
                ctm = mat_mul(M, ctm)
            last_nums.clear()
            last_name = None
            continue

        if tok.startswith(b"/"):
            last_name = tok[1:].decode("utf-8", errors="ignore")
            last_nums.clear()
            continue

        if tok == b"Do":
            if last_name and last_name in by_name:
                xref = by_name[last_name]
                if xref not in meta_cache:
                    meta_cache[xref] = get_xobject_subtype_and_bbox(doc, xref)
                subtype, bbox = meta_cache[xref]
                if subtype == "Form" and bbox is not None:
                    x0, y0, x1, y1 = bbox
                    corners = [
                        apply_mat(ctm, x0, y0),
                        apply_mat(ctm, x1, y0),
                        apply_mat(ctm, x0, y1),
                        apply_mat(ctm, x1, y1),
                    ]
                    xs = [pt[0] - crop_x0 for pt in corners]
                    ys = [pt[1] - crop_y0 for pt in corners]

                    top = top_ref if top_ref > 0 else crop_height if crop_height > 0 else page.rect.height
                    rect_mupdf = pymupdf.Rect(min(xs), top - max(ys), max(xs), top - min(ys))

                    placements.append(
                        FormPlacement(
                            name=last_name,
                            xref=xref,
                            bbox=bbox,
                            ctm=ctm,
                            rect_mupdf=rect_mupdf,
                            order=order,
                        )
                    )
                    order += 1

            last_name = None
            last_nums.clear()
            continue

        last_nums.clear()

    filtered: List[FormPlacement] = []
    for placement in placements:
        rect = placement.rect_mupdf
        if rect.is_empty:
            continue
        if rect.width < 20 or rect.height < 20:
            continue
        rect_clipped = rect & page.rect
        if rect_clipped.is_empty:
            continue
        placement.rect_mupdf = rect_clipped
        filtered.append(placement)

    if debug and filtered:
        LOG.debug("Page %d: found %d Form placements: %s", page_no, len(filtered), [p.name for p in filtered])

    return filtered


def render_and_save_form_images(
    page: pymupdf.Page,
    placements: List[FormPlacement],
    images_dir: Path,
    pdf_filename_prefix: str,
    page_no: int,
    dpi: int = 150,
) -> List[Tuple[FormPlacement, str]]:
    """Rasterizza e salva i Form XObject individuati restituendo i nomi file creati."""

    images_dir.mkdir(parents=True, exist_ok=True)
    out: List[Tuple[FormPlacement, str]] = []
    for idx, placement in enumerate(sorted(placements, key=lambda p: p.order), start=1):
        fname = f"{pdf_filename_prefix}-{page_no:04d}-form-{idx:02d}.png"
        target = unique_target(images_dir / fname)
        pix = page.get_pixmap(clip=placement.rect_mupdf, dpi=dpi, alpha=False)
        pix.save(str(target))
        out.append((placement, target.name))
    return out


def find_vector_regions(page: pymupdf.Page, debug: bool = False) -> List[pymupdf.Rect]:
    """Individua regioni candidate di disegni vettoriali da rasterizzare come immagini."""
    page_number = getattr(page, "number", None)
    page_display = int(page_number) + 1 if isinstance(page_number, int) else -1
    try:
        drawings = page.get_drawings()
    except Exception as exc:  # pragma: no cover - dipende dalla versione di PyMuPDF
        LOG.debug("get_drawings failed on page %d: %s", page_display, exc)
        return []

    if not drawings:
        return []

    page_rect = page.rect
    width = float(page_rect.width)
    height = float(page_rect.height)
    skip_top = float(page_rect.y0) + height * VECTOR_SKIP_Y_RATIO
    skip_bottom = float(page_rect.y1) - height * VECTOR_SKIP_Y_RATIO

    filtered = []
    for d in drawings:
        rect = d.get("rect")
        if rect is None or rect.is_empty:
            continue
        if rect.width < MIN_VECTOR_SIZE_PT or rect.height < MIN_VECTOR_SIZE_PT:
            continue
        if rect.y1 < skip_top or rect.y0 > skip_bottom:
            continue
        if rect.width > width * 0.9 and rect.height > height * 0.9:
            continue
        if rect.width > width * MAX_SEPARATOR_WIDTH_RATIO and rect.height < 20:
            continue
        filtered.append(d)

    if not filtered:
        return []

    try:
        clusters = page.cluster_drawings(
            drawings=filtered, x_tolerance=CLUSTER_X_TOLERANCE, y_tolerance=CLUSTER_Y_TOLERANCE
        )
    except AttributeError:
        LOG.debug("cluster_drawings not available on page %d", page_display)
        clusters = []
    except Exception as exc:
        LOG.debug("cluster_drawings failed on page %d: %s", page_display, exc)
        clusters = []

    if not clusters and len(filtered) >= MIN_VECTOR_PATHS:
        rects = [d.get("rect") for d in filtered if d.get("rect")]
        if rects:
            try:
                union = rects[0]
                for r in rects[1:]:
                    union = union | r
                clusters = [union]
            except Exception:
                clusters = []

    regions: List[pymupdf.Rect] = []
    for rect in clusters:
        if rect.width < MIN_VECTOR_SIZE_PT or rect.height < MIN_VECTOR_SIZE_PT:
            continue
        count = 0
        for d in filtered:
            d_rect = d.get("rect")
            if d_rect and d_rect.intersects(rect):
                count += 1
        if count < MIN_VECTOR_PATHS:
            continue
        padded = pymupdf.Rect(rect)
        padded.x0 = max(page_rect.x0, padded.x0 - VECTOR_PADDING)
        padded.y0 = max(page_rect.y0, padded.y0 - VECTOR_PADDING)
        padded.x1 = min(page_rect.x1, padded.x1 + VECTOR_PADDING)
        padded.y1 = min(page_rect.y1, padded.y1 + VECTOR_PADDING)
        clipped = padded & page_rect
        if clipped.is_empty:
            continue
        regions.append(clipped)

    regions.sort(key=lambda r: r.width * r.height, reverse=True)
    if debug and regions:
        LOG.debug("Page %d: vector regions %s", page_display, regions)
    return regions


def render_vector_regions(
    doc: pymupdf.Document,
    doc_page_index: int,
    regions: List[pymupdf.Rect],
    images_dir: Path,
    pdf_filename_prefix: str,
    pdf_page_no: int,
    dpi: int = 200,
) -> List[str]:
    """Rasterizza le regioni vettoriali trovate e salva le immagini risultanti."""

    if not regions:
        return []
    images_dir.mkdir(parents=True, exist_ok=True)
    out: List[str] = []
    try:
        page = doc[doc_page_index]
    except Exception as exc:  # pragma: no cover - dipende dall'integrità del PDF
        LOG.debug("Page %d access failed: %s", pdf_page_no, exc)
        return []

    for idx, rect in enumerate(regions, start=1):
        fname = f"{pdf_filename_prefix}-{pdf_page_no:04d}-vector-{idx:02d}.png"
        target = unique_target(images_dir / fname)
        try:
            pix = page.get_pixmap(clip=rect, dpi=dpi, alpha=False)
            pix.save(str(target))
            out.append(target.name)
        except Exception as exc:
            LOG.debug("Vector render failed page %d idx %d: %s", pdf_page_no, idx, exc)
            continue
    return out


CAPTION_RE = re.compile(r"(?m)^(Figura\s+\d+(\.\d+)?\s*:.*)$")
PJM_PLACEHOLDER_RE = re.compile(r"\*\*==>\s*picture\s*\[[^\]]+\]\s*intentionally\s*omitted\s*<==\*\*", re.IGNORECASE)
ANNOTATION_LINE_RE = re.compile(r"^>\s*\[annotation:([^\]]+)\]:", re.IGNORECASE)
_BR_TAG_RE = r"(?:<br\s*/?>\s*)?"
EQUATION_BLOCK_START_RE = re.compile(
    rf"^<!--\s*Start of equation:\s*(.+?)\s*-->\s*{_BR_TAG_RE}$",
    re.IGNORECASE,
)
EQUATION_BLOCK_END_RE = re.compile(
    rf"^<!--\s*End of equation:\s*(.+?)\s*-->\s*{_BR_TAG_RE}$",
    re.IGNORECASE,
)
ANNOTATION_BLOCK_START_RE = re.compile(
    rf"^<!--\s*Start of annotation:\s*(.+?)\s*-->\s*{_BR_TAG_RE}$",
    re.IGNORECASE,
)
ANNOTATION_BLOCK_END_RE = re.compile(
    rf"^<!--\s*End of annotation:\s*(.+?)\s*-->\s*{_BR_TAG_RE}$",
    re.IGNORECASE,
)
PAGE_END_MARKER_RE = re.compile(r"(?m)^\s*<!--\s*end of page\.page_number=\d+\s*-->\s*$\n?")
PAGE_START_MARKER_CAPTURE_RE = re.compile(r"^\s*<!--\s*start of page\.page_number=(\d+)\s*-->\s*$", re.IGNORECASE)
PAGE_END_MARKER_CAPTURE_RE = re.compile(r"^\s*<!--\s*end of page\.page_number=(\d+)\s*-->\s*$", re.IGNORECASE)


def inject_images_into_page_markdown(page_text: str, rel_image_paths: List[str]) -> Tuple[str, str]:
    """
    Inserisce le immagini nel Markdown della pagina preservando eventuali marker alfabetici.
    Strategia:
      0) sostituisce in ordine i placeholder PyMuPDF "**==> picture [...] intentionally omitted <==**"
      1) se esistono linee con singole lettere (es. "A"/"B"), mantiene la lettera e inserisce l'immagine dopo
      2) altrimenti inserisce le immagini prima delle didascalie "Figura ..."
      3) in mancanza, appende le immagini al termine del contenuto
    """

    lines = (page_text or "").splitlines()
    out_lines: List[str] = []
    img_index = 0

    def consume_placeholder(md: str) -> Tuple[str, int]:
        """Sostituisce progressivamente i placeholder PyMuPDF con le immagini disponibili."""

        nonlocal img_index
        replaced = 0
        parts = []
        last = 0
        for match in PJM_PLACEHOLDER_RE.finditer(md):
            parts.append(md[last:match.start()])
            if img_index < len(rel_image_paths):
                parts.append(f"![]({rel_image_paths[img_index]})")
                img_index += 1
            replaced += 1  # removes the placeholder even when not replaced by an image
            last = match.end()
        parts.append(md[last:])
        return "".join(parts), replaced

    text, replaced = consume_placeholder("\n".join(lines))
    if replaced:
        lines = text.splitlines()
    else:
        text = "\n".join(lines)

    for line in lines:
        if img_index < len(rel_image_paths) and re.fullmatch(r"\s*[A-Z]\s*", line or ""):
            out_lines.append(line)
            out_lines.append("")
            out_lines.append(f"![]({rel_image_paths[img_index]})")
            out_lines.append("")
            img_index += 1
        else:
            out_lines.append(line)

    text = "\n".join(out_lines)

    if img_index == len(rel_image_paths):
        return text, "inserted_after_single_letter_lines" if replaced == 0 else "placeholders_and_letters"

    captions = list(CAPTION_RE.finditer(text))
    if captions:
        pieces: List[str] = []
        last = 0
        cap_idx = 0
        while img_index < len(rel_image_paths) and cap_idx < len(captions):
            match = captions[cap_idx]
            pieces.append(text[last:match.start()])
            pieces.append(f"![]({rel_image_paths[img_index]})\n")
            img_index += 1
            last = match.start()
            cap_idx += 1
        pieces.append(text[last:])
        txt2 = "".join(pieces)
        if img_index == len(rel_image_paths):
            return txt2, "inserted_before_captions"

        txt2 = txt2.rstrip() + "\n" + "\n".join(f"![]({p})" for p in rel_image_paths[img_index:]) + "\n"
        return txt2, "captions_then_append"

    txt3 = text.rstrip() + "\n" + "\n".join(f"![]({p})" for p in rel_image_paths[img_index:]) + "\n"
    return txt3, "appended_end"


def iter_search_dirs(pdf_path: Path, out_dir: Path, extra_dirs: Optional[Iterable[Path]] = None) -> List[Path]:
    """Restituisce i percorsi da ispezionare per spostare file generati dal PDF."""

    dirs = [pdf_path.parent.resolve(), Path.cwd().resolve(), out_dir.resolve()]
    if extra_dirs:
        for extra in extra_dirs:
            if extra is not None:
                dirs.append(Path(extra).resolve())
    seen = set()
    uniq: List[Path] = []
    for directory in dirs:
        if directory not in seen:
            seen.add(directory)
            uniq.append(directory)
    return uniq


def move_files_by_name(names: Iterable[str], search_dirs: List[Path], dest_dir: Path, verbose: bool = False) -> int:
    """Sposta file noti da più cartelle verso la destinazione garantendo nomi univoci."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    for name in names:
        found: Optional[Path] = None
        for directory in search_dirs:
            candidate = directory / name
            if candidate.exists() and candidate.is_file():
                found = candidate
                break
        if not found:
            continue
        if found.resolve().parent == dest_dir.resolve():
            continue
        target = unique_target(dest_dir / found.name)
        try:
            shutil.move(str(found), str(target))
            moved += 1
            if verbose:
                LOG.info("Moved image: %s -> %s", found, target)
        except Exception as exc:
            LOG.debug("Unable to move %s -> %s (%s)", found, target, exc)
    return moved


def collect_probable_generated_images(pdf_path: Path, fmt: str, search_dirs: List[Path]) -> Set[str]:
    """
    Raccoglie i PNG plausibili generati da pymupdf4llm anche se non linkati (es. pdf_sample.pdf-0003-10.png).
    I render dei Form XObject creati direttamente in images/ sono volutamente esclusi.
    """
    prefixes = [pdf_path.name, pdf_path.stem]
    pattern = re.compile(
        rf"^({'|'.join(re.escape(p) for p in prefixes)})-\d{{4}}-\d+\.{re.escape(fmt)}$",
        re.IGNORECASE,
    )

    names: Set[str] = set()
    for directory in search_dirs:
        for path in directory.glob(f"*.{fmt}"):
            if path.is_file() and pattern.match(path.name):
                names.add(path.name)
    return names


def mm_to_points(value_mm: float) -> float:
    """Converte millimetri in punti tipografici."""

    return float(value_mm) * MM_TO_PT


def apply_vertical_crop_margins(
    doc: pymupdf.Document, header_mm: Optional[float], footer_mm: Optional[float], debug: bool = False, verbose: bool = False
) -> None:
    """Applica il crop verticale in base ai margini header/footer mantenendo l'area valida."""
    header_mm_val = 0.0 if header_mm is None else header_mm
    footer_mm_val = 0.0 if footer_mm is None else footer_mm

    if header_mm_val <= 0 and footer_mm_val <= 0:
        return

    header_pts = mm_to_points(max(0.0, header_mm_val))
    footer_pts = mm_to_points(max(0.0, footer_mm_val))

    for page in doc:
        rect = page.rect
        page_no = int(getattr(page, "number", -1))
        max_removable = max(rect.height - 1.0, 0.0)
        total_requested = header_pts + footer_pts
        if total_requested > max_removable and total_requested > 0:
            scale = max_removable / total_requested
            top_adj = header_pts * scale
            bottom_adj = footer_pts * scale
        else:
            top_adj = header_pts
            bottom_adj = footer_pts
        new_rect = pymupdf.Rect(rect.x0, rect.y0 + top_adj, rect.x1, rect.y1 - bottom_adj)
        page.set_cropbox(new_rect)
        if debug or verbose:
            LOG.log(
                logging.DEBUG if debug else logging.INFO,
                "Applied vertical crop on page %d: top %.2f pt (%.2f mm) bottom %.2f pt (%.2f mm) -> rect %s",
                page_no + 1,
                top_adj,
                top_adj / MM_TO_PT,
                bottom_adj,
                bottom_adj / MM_TO_PT,
                new_rect,
            )


def embed_equations_in_markdown(md_text: str, formulas_by_base: Dict[str, str]) -> str:
    """Inserisce le formule LaTeX dopo il link diretto dell'immagine nella sezione dedicata."""
    if not formulas_by_base:
        return md_text

    lines = (md_text or "").splitlines()
    output: List[str] = []
    inserted: Set[str] = set()
    in_image_block = False
    skip_next_blank = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if skip_next_blank and not stripped:
            skip_next_blank = False
            i += 1
            continue
        skip_next_blank = False

        start_match = EQUATION_BLOCK_START_RE.match(stripped)
        if start_match:
            block_base = start_match.group(1).strip()
            if block_base in formulas_by_base:
                inserted.add(block_base)
                i += 1
                while i < len(lines):
                    if EQUATION_BLOCK_END_RE.match(lines[i].strip()):
                        i += 1
                        break
                    i += 1
                continue
            output.append(line)
            i += 1
            while i < len(lines):
                output.append(lines[i])
                if EQUATION_BLOCK_END_RE.match(lines[i].strip()):
                    i += 1
                    break
                i += 1
            continue

        if stripped == "<!-- Start of image -->":
            in_image_block = True
            output.append(line)
            i += 1
            continue

        if stripped == "<!-- End of image -->":
            in_image_block = False
            output.append(line)
            i += 1
            continue

        if not in_image_block:
            matches = list(IMG_LINK_RE.finditer(line))
            if matches:
                formula_match = None
                formula_base = ""
                for match in matches:
                    url_part, _ = _split_markdown_link(match.group(2))
                    url = normalize_path_for_md(url_part)
                    base = url.split("/")[-1]
                    if base in formulas_by_base and base not in inserted:
                        formula_match = match
                        formula_base = base
                        break

                if formula_match:
                    before = line[: formula_match.start()]
                    after = line[formula_match.end() :]
                    if before.strip():
                        output.append(before.rstrip())

                    if output and re.match(r"^\s*\$\$.*\$\$\s*$", output[-1]):
                        output.pop()

                    if output and output[-1].strip():
                        output.append("")

                    start_line = f"<!-- Start of equation: {formula_base} -->\n\n"
                    output.append(start_line)
                    output.append(f"$${formulas_by_base[formula_base]}$$")
                    output.append(f"\n<!-- End of equation: {formula_base} -->\n")
                    if output and output[-1].strip():
                        output.append("")
                    output.append(formula_match.group(0))
                    if after.strip():
                        output.append(after.lstrip())
                    inserted.add(formula_base)
                    i += 1
                    continue

        output.append(line)
        if in_image_block:
            matches = list(DIRECT_IMG_LINK_RE.finditer(line))
            for match in matches:
                url_part = match.group(2)
                url = normalize_path_for_md(url_part)
                base = url.split("/")[-1]
                if base not in formulas_by_base or base in inserted:
                    continue
                if output and output[-1].strip():
                    output.append("")
                start_line = f"<!-- Start of equation: {base} -->\n\n"
                output.append(start_line)
                output.append(f"$${formulas_by_base[base]}$$")
                output.append(f"\n<!-- End of equation: {base} -->\n")
                output.append("")
                inserted.add(base)
                if i + 1 < len(lines) and not lines[i + 1].strip():
                    skip_next_blank = True
        i += 1

    return "\n".join(output)


def embed_annotations_in_markdown(md_text: str, annotations: Dict[str, str]) -> str:
    """Inserisce i blocchi di annotazione dopo il link diretto o dopo l'equazione se presente."""
    if not annotations:
        return md_text

    lines = (md_text or "").splitlines()
    output: List[str] = []
    equation_bases = {match.group(1).strip() for match in EQUATION_BLOCK_START_RE.finditer(md_text or "")}
    inserted: Set[str] = set()
    in_image_block = False
    skip_next_blank = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if skip_next_blank and not stripped:
            skip_next_blank = False
            i += 1
            continue
        skip_next_blank = False

        if stripped == "<!-- Start of image -->":
            in_image_block = True
            output.append(line)
            i += 1
            continue

        if stripped == "<!-- End of image -->":
            in_image_block = False
            output.append(line)
            i += 1
            continue

        ann_old = ANNOTATION_LINE_RE.match(stripped)
        if ann_old:
            base_existing = ann_old.group(1)
            if base_existing in annotations:
                i += 1
                while i < len(lines) and lines[i].startswith(">"):
                    i += 1
                continue
            output.append(line)
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                output.append(lines[i])
                i += 1
            continue

        ann_start = ANNOTATION_BLOCK_START_RE.match(stripped)
        if ann_start:
            base_block = ann_start.group(1).strip()
            if base_block in annotations:
                i += 1
                while i < len(lines):
                    if ANNOTATION_BLOCK_END_RE.match(lines[i].strip()):
                        i += 1
                        break
                    i += 1
                continue
            output.append(line)
            i += 1
            while i < len(lines):
                output.append(lines[i])
                if ANNOTATION_BLOCK_END_RE.match(lines[i].strip()):
                    i += 1
                    break
                i += 1
            continue

        eq_start = EQUATION_BLOCK_START_RE.match(stripped)
        if eq_start:
            base = eq_start.group(1).strip()
            output.append(line)
            i += 1
            while i < len(lines):
                output.append(lines[i])
                if EQUATION_BLOCK_END_RE.match(lines[i].strip()):
                    i += 1
                    break
                i += 1
            if base in annotations and base not in inserted:
                text = annotations[base].strip()
                if text:
                    if output and output[-1].strip():
                        output.append("")
                    start_line = f"<!-- Start of annotation: {base} -->\n\n"
                    output.append(start_line)
                    ann_lines = text.splitlines() or [text]
                    for extra in ann_lines:
                        output.append(extra.strip())
                    output.append(f"\n<!-- End of annotation: {base} -->\n")
                    output.append("")
                    inserted.add(base)
                    if i < len(lines) and not lines[i].strip():
                        skip_next_blank = True
            continue

        output.append(line)
        if in_image_block:
            matches = list(DIRECT_IMG_LINK_RE.finditer(line))
            for match in matches:
                url_part = match.group(2)
                url = normalize_path_for_md(url_part)
                base = url.split("/")[-1]
                if base not in annotations or base in inserted or base in equation_bases:
                    continue
                text = annotations[base].strip()
                if not text:
                    continue
                if output and output[-1].strip():
                    output.append("")
                start_line = f"<!-- Start of annotation: {base} -->\n\n"
                output.append(start_line)
                ann_lines = text.splitlines() or [text]
                for extra in ann_lines:
                    output.append(extra.strip())
                output.append(f"\n<!-- End of annotation: {base} -->\n")
                output.append("")
                inserted.add(base)
                if i + 1 < len(lines) and not lines[i + 1].strip():
                    skip_next_blank = True
        else:
            matches = list(IMG_LINK_RE.finditer(line))
            for match in matches:
                url_part, _ = _split_markdown_link(match.group(2))
                url = normalize_path_for_md(url_part)
                base = url.split("/")[-1]
                if base not in annotations or base in inserted or base in equation_bases:
                    continue
                text = annotations[base].strip()
                if not text:
                    continue
                if output and output[-1].strip():
                    output.append("")
                start_line = f"<!-- Start of annotation: {base} -->\n\n"
                output.append(start_line)
                ann_lines = text.splitlines() or [text]
                for extra in ann_lines:
                    output.append(extra.strip())
                output.append(f"\n<!-- End of annotation: {base} -->\n")
                output.append("")
                inserted.add(base)
                if i + 1 < len(lines) and not lines[i + 1].strip():
                    skip_next_blank = True
        i += 1

    return "\n".join(output)


def _strip_image_links_from_line(line: str, basenames: Set[str]) -> Tuple[str, bool]:
    """Rimuove i link a immagini specifiche da una singola riga Markdown."""

    if not basenames:
        return line, False
    result_parts: List[str] = []
    last_index = 0
    removed = False
    for match in IMG_LINK_RE.finditer(line):
        result_parts.append(line[last_index : match.start()])
        url_part, _ = _split_markdown_link(match.group(2))
        url = normalize_path_for_md(url_part)
        url = url.split("?", 1)[0].split("#", 1)[0]
        base = url.split("/")[-1]
        if base in basenames:
            removed = True
        else:
            result_parts.append(match.group(0))
        last_index = match.end()
    if not removed:
        # Check for direct image links [path](path) added by normalize_image_links
        for match in DIRECT_IMG_LINK_RE.finditer(line):
            url_part = match.group(2)
            url = normalize_path_for_md(url_part)
            url = url.split("?", 1)[0].split("#", 1)[0]
            base = url.split("/")[-1]
            if base in basenames:
                # Remove the direct link
                return "", True
        return line, False
    result_parts.append(line[last_index:])
    new_line = "".join(result_parts)
    if not new_line.strip():
        return "", True
    return new_line, True


def strip_image_references_from_markdown(md_text: str, basenames: Set[str]) -> str:
    """Rimuove link immagine e blocchi Pix2Tex/annotazioni per i basename indicati."""
    if not basenames:
        return md_text

    lines = md_text.splitlines()
    output: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for image marker start
        if stripped == "<!-- Start of image -->":
            # Look ahead to find the image basename
            block_lines = [line]
            j = i + 1
            image_basename = None
            while j < len(lines):
                block_lines.append(lines[j])
                if lines[j].strip() == "<!-- End of image -->":
                    # Check if any line in the block contains a matching basename
                    for block_line in block_lines:
                        for match in IMG_LINK_RE.finditer(block_line):
                            url_part, _ = _split_markdown_link(match.group(2))
                            url = normalize_path_for_md(url_part)
                            url = url.split("?", 1)[0].split("#", 1)[0]
                            base = url.split("/")[-1]
                            if base in basenames:
                                image_basename = base
                                break
                        if image_basename:
                            break
                    
                    if image_basename:
                        # Skip entire image block
                        i = j + 1
                        # Skip trailing empty lines
                        while i < len(lines) and not lines[i].strip():
                            i += 1
                    else:
                        # Keep the block
                        output.extend(block_lines)
                        i = j + 1
                    break
                j += 1
            else:
                # No end marker found, keep the line
                output.append(line)
                i += 1
            continue

        eq_start = EQUATION_BLOCK_START_RE.match(stripped)
        if eq_start and eq_start.group(1).strip() in basenames:
            i += 1
            while i < len(lines):
                if EQUATION_BLOCK_END_RE.match(lines[i].strip()):
                    i += 1
                    break
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            continue

        ann_start = ANNOTATION_BLOCK_START_RE.match(stripped)
        if ann_start and ann_start.group(1).strip() in basenames:
            i += 1
            while i < len(lines):
                if ANNOTATION_BLOCK_END_RE.match(lines[i].strip()):
                    i += 1
                    break
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            continue

        new_line, removed = _strip_image_links_from_line(line, basenames)
        if removed and not new_line.strip():
            if output and not output[-1].strip():
                pass
            else:
                output.append("")
        else:
            output.append(new_line)
        i += 1

    cleaned = "\n".join(output)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def remove_small_images_phase(
    md_text: str,
    out_dir: Path,
    config: PostProcessingConfig,
) -> str:
    """Filtra le immagini troppo piccole dal Markdown e rimuove i file dal filesystem."""
    try:
        from PIL import Image  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"Pillow not available: {exc}") from exc

    image_paths_raw = extract_image_paths_from_markdown(md_text)
    if not image_paths_raw:
        return md_text

    seen_paths: Set[str] = set()
    image_paths: List[str] = []
    for path in image_paths_raw:
        if path not in seen_paths:
            seen_paths.add(path)
            image_paths.append(path)

    removed_basenames: Set[str] = set()
    min_width = max(1, int(config.min_size_x))
    min_height = max(1, int(config.min_size_y))
    total = len(image_paths)

    for index, rel_path in enumerate(image_paths, start=1):
        rel_file = normalize_path_for_md(str(rel_path))
        path = out_dir / rel_file
        base_name = Path(rel_file).name
        width: Optional[int] = None
        height: Optional[int] = None
        if path.exists():
            try:
                with Image.open(path) as img:
                    width, height = img.size
            except Exception as exc:
                if config.debug:
                    LOG.debug("remove-small-images unable to read %s: %s", path, exc)
        else:
            if config.debug:
                LOG.debug("remove-small-images missing file: %s", path)

        should_remove = bool(width is not None and height is not None and width < min_width and height < min_height)
        if config.verbose:
            size_label = f"{width}x{height}px" if width is not None and height is not None else "unknown size"
            status = "REMOVE" if should_remove else "KEEP"
            _log_verbose_progress(
                "remove-small-images",
                index,
                total,
                detail=f"{rel_file} -> {status} ({size_label})",
            )

        if should_remove:
            removed_basenames.add(base_name)
            try:
                path.unlink()
                if config.debug:
                    LOG.debug("remove-small-images removed file: %s", path)
            except FileNotFoundError:
                if config.debug:
                    LOG.debug("remove-small-images missing file for removal: %s", path)
            continue
    if not removed_basenames:
        return md_text

    cleaned_md = strip_image_references_from_markdown(md_text, removed_basenames)
    return cleaned_md


def rename_images_phase(
    *,
    md_text: str,
    out_dir: Path,
    config: PostProcessingConfig,
) -> str:
    """Rinomina le immagini con caratteri non stampabili o spazi e aggiorna i riferimenti."""

    images_dir = out_dir / "images"
    if not images_dir.exists() or not images_dir.is_dir():
        return md_text

    mapping: Dict[str, str] = {}
    # Scandire ricorsivamente usando rglob
    for path in sorted((p for p in images_dir.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        sanitized = _sanitize_printable_filename(path.name)
        if sanitized == path.name:
            continue
        target = unique_target(path.with_name(sanitized))
        # Percorsi normalizzati completi
        old_rel = normalize_path_for_md(relative_to_output(path, out_dir))
        new_rel = normalize_path_for_md(relative_to_output(target, out_dir))
        try:
            path.rename(target)
            mapping[old_rel] = new_rel
            if config.verbose:
                LOG.info("Renamed image: %s -> %s", old_rel, new_rel)
        except Exception as exc:
            LOG.error("Unable to rename image %s: %s", path, exc)
            if config.debug:
                LOG.debug("Rename failure details for %s", path, exc_info=exc)
            continue

    if not mapping:
        return md_text

    updated_md = _rewrite_image_links(md_text, mapping)
    return updated_md


def fix_missing_links(
    *,
    md_text: str,
    out_dir: Path,
    config: PostProcessingConfig,
) -> str:
    """Identifica i link mancanti e li marca nel Markdown."""

    if "[LINK]" in md_text:
        md_text = md_text.replace("[LINK]", "MISSING_LINK")

    link_re = re.compile(r"(?P<prefix>\[)(?P<label>[^\]]+)(\])\((?P<target>[^)]+)\)")
    img_re = re.compile(r"!\\?\[(?P<alt>[^\]]*)\\?\]\((?P<target>[^)]+)\)")

    def is_external(t: str) -> bool:
        t = t.strip()
        return t.startswith("http://") or t.startswith("https://") or t.startswith("mailto:") or t.startswith("//")

    def _process_pattern(text: str, pattern: re.Pattern, is_image: bool) -> str:
        out: List[str] = []
        last = 0
        for m in pattern.finditer(text):
            out.append(text[last : m.start()])
            target = m.group("target").strip()
            target_url, _ = _split_markdown_link(target)
            if target_url.startswith("#") or is_external(target_url):
                out.append(m.group(0))
            else:
                if target_url.startswith("file://"):
                    tgt_path = target_url[len("file://") :]
                else:
                    tgt_path = target_url

                try:
                    norm = normalize_path_for_md(tgt_path)
                except Exception:
                    norm = tgt_path

                candidate = out_dir / norm
                try:
                    exists = candidate.exists()
                except OSError:
                    exists = False
                if exists:
                    out.append(m.group(0))
                else:
                    out.append("MISSING_LINK")

            last = m.end()
        out.append(text[last:])
        return "".join(out)

    md_text = _process_pattern(md_text, img_re, is_image=True)
    md_text = _process_pattern(md_text, link_re, is_image=False)

    return md_text


def normalize_markdown_lists(md_text: str) -> str:
    r"""Normalizza le liste rimuovendo righe vuote tra elementi consecutivi."""

    if not md_text:
        return md_text

    def _normalize_lists(segment: str) -> str:
        list_item_re = r"^[\t ]*(?:[-*+]|\d+[.)])[\t ]+(.*?)\s*$"
        pattern = re.compile(rf"(?m)({list_item_re})\n(?:[ \t]*\n)+(?={list_item_re})")

        new_text = pattern.sub(r"\1\n", segment)
        while True:
            updated = pattern.sub(r"\1\n", new_text)
            if updated == new_text:
                break
            new_text = updated

        return new_text

    return _apply_outside_fences(md_text, _normalize_lists)


def cleanup_markdown(md_text: str, pdf_headings: Optional[List[HeadingEntry]] = None) -> str:
    """Pulisce il Markdown rimuovendo i marker di pagina senza modificare gli heading (DES-060, REQ-040)."""

    if not md_text:
        return md_text

    # DES-060: Do not degrade headings in post-processing
    base_text = md_text

    cleaned_lines: List[str] = []
    fence_stack: List[Tuple[str, int]] = []
    for raw in base_text.splitlines():
        stripped = raw.strip()

        if _update_fence_stack(fence_stack, raw):
            cleaned_lines.append(raw.rstrip())
            continue
        if fence_stack:
            cleaned_lines.append(raw)
            continue

        if raw.startswith("    ") or raw.startswith("\t"):
            cleaned_lines.append(raw.rstrip("\n"))
            continue

        if PAGE_START_MARKER_CAPTURE_RE.match(stripped) or PAGE_END_MARKER_CAPTURE_RE.match(stripped):
            continue

        line = raw.rstrip()
        line = re.sub(r"(?<=\S) {2,}", " ", line)
        cleaned_lines.append(line)

    intermediate = "\n".join(cleaned_lines)
    lines = intermediate.splitlines()
    result_lines: List[str] = []
    fence_stack = []
    prev_blank = False
    for line in lines:
        if _update_fence_stack(fence_stack, line):
            result_lines.append(line)
            prev_blank = False
            continue
        if fence_stack:
            result_lines.append(line)
            continue

        is_blank = not line.strip()
        if is_blank:
            if prev_blank:
                continue
            result_lines.append("")
            prev_blank = True
        else:
            result_lines.append(line)
            prev_blank = False

    result = "\n".join(result_lines)
    if base_text.endswith("\n") and not result.endswith("\n"):
        result += "\n"

    try:
        result = normalize_markdown_format(result)
    except Exception as exc:
        LOG.warning("normalize_markdown_format failed: %s", exc)

    return result


def check_fenced_code_balanced(md_text: str) -> bool:
    """Verifica che i blocchi di codice recintati siano bilanciati nel Markdown."""

    try:
        from markdown_it import MarkdownIt  # type: ignore
    except Exception:
        MarkdownIt = None  # type: ignore

    if MarkdownIt is not None:
        try:
            md = MarkdownIt()
            md.parse(md_text)
        except Exception:
            pass

    fence_re = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
    stack: List[Tuple[str, int]] = []
    for line in md_text.splitlines():
        match = fence_re.match(line)
        if not match:
            continue
        seq = match.group(1)
        ch = seq[0]
        length = len(seq)
        if not stack:
            stack.append((ch, length))
            continue
        top_ch, top_len = stack[-1]
        if ch == top_ch and length >= top_len:
            stack.pop()
        else:
            stack.append((ch, length))

    return len(stack) == 0


def _slugify_markdown_heading(title: str) -> str:
    """Genera uno slug Markdown da un titolo per collegamenti interni."""

    slug = unicodedata.normalize("NFKD", title or "").lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug or "section"


def _normalize_ref_label(label: str) -> str:
    """Normalizza label Markdown rimuovendo anchor Pandoc e spazi multipli."""
    cleaned = re.sub(r"\s*\{#[^\}]*\}\s*$", "", label).strip()
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def _remove_heading_references(md_text: str, anchors: Set[str]) -> str:
    """Rimuove anchor reference dalle intestazioni Markdown non presenti in anchors."""
    if not md_text:
        return md_text

    heading_re = re.compile(r"^(?P<indent>\s*)(?P<hashes>#{1,})\s+(?P<content>.+?)\s*$")
    anchor_re = re.compile(r"\s*\{#([^\}]+)\}\s*$")

    def _remove_in_segment(segment: str) -> str:
        lines = segment.splitlines()
        output: List[str] = []

        for line in lines:
            match = heading_re.match(line)
            if not match:
                output.append(line)
                continue

            indent = match.group("indent")
            hashes = match.group("hashes")
            content = match.group("content")

            anchor_match = anchor_re.search(content)
            if not anchor_match:
                output.append(line)
                continue

            anchor_id = anchor_match.group(1)
            if anchor_id in anchors:
                output.append(line)
                continue

            cleaned_content = anchor_re.sub("", content).strip()
            output.append(f"{indent}{hashes} {cleaned_content}")

        result = "\n".join(output)
        if segment.endswith("\n") and not result.endswith("\n"):
            result += "\n"
        return result

    return _apply_outside_fences(md_text, _remove_in_segment)


def _remove_heading_links(md_text: str, anchors: Set[str]) -> str:
    """Rimuove riferimenti a heading rimossi da link inline, HTML e definizioni."""
    if not anchors:
        return md_text

    ref_def_re = re.compile(
        r"^\s*\[(?P<ref>[^\]]+)\]:\s*#(?P<anchor>[^)\s]+)(?:\s+(\"[^\"]*\"|'[^']*'))?\s*$"
    )
    inline_link_re = re.compile(
        r"(?<!!)\[(?P<label>[^\]]+)\]\(\s*#(?P<anchor>[^)\s]+)(?:\s+(\"[^\"]*\"|'[^']*'))?\s*\)"
    )
    html_link_re = re.compile(
        r"<a\s+[^>]*href\s*=\s*(?P<quote>[\"'])#(?P<anchor>[^\"'\s]+)(?P=quote)[^>]*>(?P<label>.*?)</a>",
        re.IGNORECASE,
    )
    ref_link_re = re.compile(r"(?<!!)\[(?P<label>[^\]]+)\]\[(?P<ref>[^\]]*)\]")

    removed_refs: Set[str] = set()
    output: List[str] = []
    fence_stack: List[Tuple[str, int]] = []

    for line in md_text.splitlines():
        if _update_fence_stack(fence_stack, line):
            output.append(line)
            continue
        if fence_stack:
            output.append(line)
            continue
        match = ref_def_re.match(line)
        if match:
            anchor = match.group("anchor")
            if anchor in anchors:
                removed_refs.add(_normalize_ref_label(match.group("ref")))
                continue
        output.append(line)

    def _replace_inline_links(text: str) -> str:
        def _inline_repl(m: re.Match) -> str:
            if m.group("anchor") in anchors:
                return m.group("label")
            return m.group(0)

        def _html_repl(m: re.Match) -> str:
            if m.group("anchor") in anchors:
                return m.group("label")
            return m.group(0)

        def _ref_repl(m: re.Match) -> str:
            ref = m.group("ref") or m.group("label")
            if _normalize_ref_label(ref) in removed_refs:
                return m.group("label")
            return m.group(0)

        text = inline_link_re.sub(_inline_repl, text)
        text = html_link_re.sub(_html_repl, text)
        if removed_refs:
            text = ref_link_re.sub(_ref_repl, text)
        return text

    updated_lines: List[str] = []
    fence_stack = []
    for line in output:
        if _update_fence_stack(fence_stack, line):
            updated_lines.append(line)
            continue
        if fence_stack:
            updated_lines.append(line)
            continue
        updated_lines.append(_replace_inline_links(line))

    result = "\n".join(updated_lines)
    if md_text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def _scan_markdown_for_toc_entries(md_text: str) -> List[Tuple[str, int, str, str]]:
    """Analizza il Markdown e restituisce la sequenza delle voci TOC e dei riferimenti."""

    lines = md_text.splitlines()
    fenced_lines = _get_fenced_line_mask(lines)
    toc_sequence: List[Tuple[str, int, str, str]] = []
    heading_re = re.compile(r"^(#{1,})\s+(.+?)\s*$")
    image_re = re.compile(r"!\\?\[[^\]]*\\?\]\(\s*images/[^)]+\)")
    table_re = re.compile(r"\(\s*tables/[^)]+\)")

    for idx, raw in enumerate(lines):
        if idx in fenced_lines:
            continue
        line = raw.rstrip()
        heading = heading_re.match(line)
        if heading:
            level = len(heading.group(1))
            title_raw = heading.group(2).strip()
            page_note = ""
            match = re.search(r"\(pag\.\s*([^)]+)\)", title_raw)
            if match:
                page_note = match.group(1).strip()
                title_raw = title_raw.replace(match.group(0), "").strip()
            title_display = _strip_markdown_decoration(title_raw).strip()
            title_clean = _strip_markdown_decoration(title_raw).strip()
            title_clean = re.sub(r"^\d+(?:\.\d+)*\s+", "", title_clean).strip()
            if not title_display:
                continue
            toc_sequence.append(("heading", level, title_display, page_note))
            continue
        if image_re.search(line):
            toc_sequence.append(("raw", 0, line.strip(), ""))
            continue
        if table_re.search(line):
            toc_sequence.append(("raw", 0, line.strip(), ""))
            continue

    return toc_sequence


def normalize_markdown_headings(md_text: str, toc_headings: List[HeadingEntry]) -> str:
    """Normalizza intestazioni e TOC nel Markdown in base ai titoli presenti nella TOC del PDF."""

    # Extract valid anchors from toc_headings
    valid_anchors: Set[str] = set()
    for item in toc_headings:
        if len(item) >= 4 and item[3]:
            valid_anchors.add(str(item[3]))
        elif len(item) >= 3 and isinstance(item[2], str) and item[2]:
            valid_anchors.add(str(item[2]))

    # Apply anchor cleanup
    md_text = _remove_heading_references(md_text, valid_anchors)

    lines = md_text.splitlines()
    fenced_lines = _get_fenced_line_mask(lines)
    toc_list_start = None
    for idx, raw in enumerate(lines):
        if idx in fenced_lines:
            continue
        if raw.strip() == "** TOC **":
            toc_list_start = idx + 1
            break

    toc_page_entries: List[Tuple[str, int]] = []
    toc_page_re = re.compile(r"^(?P<indent>\s*)-\s+(?P<title>.+?)\s+\(pag\.\s*(?P<page>\d+)\s*\)\s*$")
    if toc_list_start is not None:
        for idx in range(toc_list_start, len(lines)):
            if idx in fenced_lines:
                continue
            stripped = lines[idx].strip()
            if PAGE_START_MARKER_CAPTURE_RE.match(stripped):
                break
            if not stripped:
                continue
            match = toc_page_re.match(lines[idx])
            if not match:
                continue
            title = match.group("title").strip()
            page_no = int(match.group("page"))
            toc_page_entries.append((title, page_no))

    normalized_toc: List[HeadingEntry] = []
    toc_page_index = 0
    for entry in toc_headings:
        if len(entry) < 2:
            continue
        level = int(entry[0])
        title = str(entry[1])
        page: Optional[int] = None
        if len(entry) >= 3:
            page_val = entry[2]
            if page_val is not None:
                try:
                    page = int(page_val)
                except Exception:
                    page = None
        if page is None and toc_page_index < len(toc_page_entries):
            page = toc_page_entries[toc_page_index][1]
        toc_page_index += 1
        normalized_toc.append((level, title, page))

    search_pos = 0
    matched_lines: Set[int] = set()
    page_markers: Dict[int, int] = {}
    for idx, raw in enumerate(lines):
        if idx in fenced_lines:
            continue
        match = PAGE_START_MARKER_CAPTURE_RE.match(raw.strip())
        if not match:
            continue
        try:
            page_markers[int(match.group(1))] = idx
        except Exception:
            continue
    page_ranges: Dict[int, Tuple[int, int]] = {}
    if page_markers:
        ordered_pages = sorted(page_markers.items(), key=lambda item: item[1])
        for idx, (page_no, start_idx) in enumerate(ordered_pages):
            end_idx = ordered_pages[idx + 1][1] if idx + 1 < len(ordered_pages) else len(lines)
            page_ranges[page_no] = (start_idx, end_idx)
    page_search_pos: Dict[int, int] = {page: start + 1 for page, (start, _) in page_ranges.items()}
    pending_by_page: Dict[int, List[Tuple[int, str]]] = {}
    toc_anchor_re = re.compile(r"\(pag\.\s*[^)]+\)")
    heading_re = re.compile(r"^(?P<prefix>\s*)#{1,}\s+(?P<title>.+?)\s*$")
    for level, title, page_no in normalized_toc:
        target = _normalize_title_for_toc(title)
        found = False
        range_start = search_pos
        range_end = len(lines)
        if page_no is not None and page_no in page_ranges:
            range_start = page_search_pos.get(page_no, page_ranges[page_no][0] + 1)
            range_end = page_ranges[page_no][1]
        for idx in range(range_start, range_end):
            if idx in fenced_lines:
                continue
            if idx in matched_lines:
                continue
            stripped = lines[idx].strip()
            if not stripped or stripped.startswith("<!--"):
                continue
            if toc_list_start is not None and idx >= toc_list_start:
                if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("+ "):
                    if toc_anchor_re.search(stripped):
                        continue
            heading = heading_re.match(lines[idx])
            if heading:
                if re.match(r"^\s*[-*+]\s+|\s*\d+[.)]\s", stripped):
                    continue
                candidate_raw = heading.group("title").strip()
                if not candidate_raw:
                    continue
                candidate_normalized = _normalize_title_for_toc(candidate_raw)
                # Match exactly or when TOC entry is a prefix (truncated heading in TOC)
                if candidate_normalized == target or candidate_normalized.startswith(target + " "):
                    prefix = heading.group("prefix")
                    heading_line = f"{prefix}{'#' * max(1, level)} {title}"
                    lines[idx] = heading_line
                    matched_lines.add(idx)
                    if page_no is not None and page_no in page_search_pos:
                        page_search_pos[page_no] = idx + 1
                    else:
                        search_pos = idx + 1
                    found = True
                    break
        if not found and page_no is not None:
            pending_by_page.setdefault(int(page_no), []).append((level, title))
        if found or page_no is not None or not search_pos:
            continue
        for idx in range(0, min(search_pos, len(lines))):
            if idx in fenced_lines:
                continue
            if idx in matched_lines:
                continue
            stripped = lines[idx].strip()
            if not stripped or stripped.startswith("<!--"):
                continue
            heading = heading_re.match(lines[idx])
            if heading:
                candidate_raw = heading.group("title").strip()
                if not candidate_raw:
                    continue
                candidate_normalized = _normalize_title_for_toc(candidate_raw)
                if candidate_normalized == target or candidate_normalized.startswith(target + " "):
                    prefix = heading.group("prefix")
                    heading_line = f"{prefix}{'#' * max(1, level)} {title}"
                    lines[idx] = heading_line
                    matched_lines.add(idx)
                    search_pos = max(search_pos, idx + 1)
                    break

    if pending_by_page and page_markers:
        pages_by_index = sorted(
            pending_by_page.items(),
            key=lambda item: page_markers.get(item[0], -1),
            reverse=True,
        )
        for page_no, entries in pages_by_index:
            insert_at = page_markers.get(page_no)
            if insert_at is None:
                continue
            new_lines: List[str] = []
            for level, title in entries:
                new_lines.append(f"{'#' * max(1, level)} {title}")
                new_lines.append("")
            lines[insert_at + 1:insert_at + 1] = new_lines

    result = "\n".join(lines)
    if md_text.endswith("\n"):
        result += "\n"
    return result


def clean_markdown_headings(md_text: str, pdf_headings: List[HeadingEntry]) -> str:
    """Degrada le intestazioni Markdown non presenti nella TOC in testo maiuscolo in grassetto."""

    if not pdf_headings:
        return md_text

    normalized_titles = {
        _normalize_title_for_toc(str(title))
        for _, title, *rest in pdf_headings
        if str(title).strip()
    }

    heading_re = re.compile(r"^(?P<prefix>\s*)(?P<hashes>#{1,})\s+(?P<title>.+?)\s*$")

    def _strip_bold(text: str) -> str:
        """Rimuove il grassetto/corsivo esterno se presente restituendo il testo pulito."""

        t = text.strip()
        # Strip outer italic markers (_..._) first, then bold
        while (t.startswith("_") and t.endswith("_") and len(t) > 2
               and not t.startswith("__")):
            t = t[1:-1].strip()
        if (t.startswith("**") and t.endswith("**")) or (t.startswith("__") and t.endswith("__")):
            return t[2:-2].strip()
        return t

    removed_anchors: Set[str] = set()
    lines = md_text.splitlines()
    output: List[str] = []
    fenced_lines = _get_fenced_line_mask(lines)

    for idx, line in enumerate(lines):
        if idx in fenced_lines:
            output.append(line)
            continue

        match = heading_re.match(line)
        if not match:
            output.append(line)
            continue

        title_raw = match.group("title").strip()
        normalized = _normalize_title_for_toc(title_raw)

        if normalized in normalized_titles:
            output.append(line)
            continue

        clean_title = _strip_bold(title_raw).upper()
        bold_title = f"**{clean_title}**"
        output.append(f"{match.group('prefix')}{bold_title}")
        removed_anchors.add(_slugify_markdown_heading(_strip_bold(title_raw)))

    result = "\n".join(output)
    result = _remove_heading_links(result, removed_anchors)
    if md_text.endswith("\n"):
        result += "\n"
    return result


def add_pdf_toc_to_markdown(md_text: str, pdf_headings: List[HeadingEntry]) -> str:
    """Inserisce una TOC Markdown derivata dal pdf_toc all'inizio del documento."""

    if not md_text or not pdf_headings:
        return md_text

    def _normalize_toc_heading_variants(content: str) -> str:
        """Normalizza intestazioni TOC alternative sul formato canonico in grassetto."""

        lines = content.splitlines()
        pattern = re.compile(
            r"^\s*(?:#{1,}\s*)?(?:\*{0,2}\s*)?(?:pdf\s+toc|html\s+toc|toc)\s*(?:\*{0,2}\s*)?$",
            re.IGNORECASE,
        )
        normalized: List[str] = []
        for line in lines:
            if pattern.match(line.strip()):
                normalized.append("** TOC **")
            else:
                normalized.append(line)
        result = "\n".join(normalized)
        if content.endswith("\n") and not result.endswith("\n"):
            result += "\n"
        return result

    md_text = _normalize_toc_heading_variants(md_text)

    toc_lines: List[str] = ["** TOC **", ""]
    for level, title, _ in pdf_headings:
        indent = "  " * max(0, int(level) - 1)
        anchor = _slugify_markdown_heading(title)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    toc_lines.append("")

    lines = md_text.splitlines()
    insert_at = 0
    for idx, raw in enumerate(lines):
        if PAGE_START_MARKER_CAPTURE_RE.match(raw.strip()):
            insert_at = idx + 1
            break

    new_lines = lines[:insert_at] + toc_lines + lines[insert_at:]
    result = "\n".join(new_lines)
    if md_text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def normalize_markdown_format(md_text: str) -> str:
    """Normalizza il Markdown convertendo tag HTML e riformattando paragrafi."""

    if not md_text:
        return md_text

    normalized = _apply_outside_fences(md_text, lambda segment: re.sub(r"(?i)<br\s*/?>", "\n", segment))

    try:
        normalized = normalize_markdown_lists(normalized)
    except Exception as exc:
        LOG.warning("Markdown list normalization failed: %s", exc)

    if os.environ.get("TOMARKDOWN_SKIP_MDFORMAT_UNWRAP") == "1" or os.environ.get("PDF2TREE_SKIP_MDFORMAT_UNWRAP") == "1" or os.environ.get("HTML2TREE_SKIP_MDFORMAT_UNWRAP") == "1":
        if md_text.endswith("\n") and not normalized.endswith("\n"):
            normalized += "\n"
        return _normalize_markdown_underscores(normalized)

    try:
        mdformat = importlib.import_module("mdformat")
    except Exception:
        if md_text.endswith("\n") and not normalized.endswith("\n"):
            normalized += "\n"
        return _normalize_markdown_underscores(normalized)

    def _split_blocks_preserving_fences(text: str) -> List[str]:
        blocks: List[str] = []
        current: List[str] = []
        fence_stack: List[Tuple[str, int]] = []

        for line in text.splitlines():
            if _update_fence_stack(fence_stack, line):
                current.append(line)
                continue
            if fence_stack:
                current.append(line)
                continue
            if not line.strip():
                if current:
                    blocks.append("\n".join(current))
                    current = []
                continue
            current.append(line)

        if current:
            blocks.append("\n".join(current))
        return blocks

    marker_lines = {
        "<!-- start of image -->",
        "<!-- end of image -->",
        "<!-- start of table -->",
        "<!-- end of table -->",
        "<!-- start of picture text -->",
        "<!-- end of picture text -->",
    }

    # Also protect page markers from mdformat
    page_marker_pattern = re.compile(r"^<--\s*(?:start|end) of page\.page_number=\d+\s*-->$", re.IGNORECASE)

    def _is_marker_block(block_lines: List[str]) -> bool:
        non_empty = [line.strip().lower() for line in block_lines if line.strip()]
        return bool(non_empty) and all(line in marker_lines for line in non_empty)

    try:
        parts = _split_blocks_preserving_fences(normalized)
        processed_parts: List[str] = []
        for part in parts:
            stripped_part = part.lstrip("\n")
            lines = stripped_part.splitlines()
            first_line = lines[0] if lines else ""
            trimmed = first_line.lstrip()
            is_table = any(line.lstrip().startswith("|") for line in part.splitlines())
            is_heading = first_line.lstrip().startswith("#")
            is_fenced_code = bool(_CODE_FENCE_RE.match(first_line)) or bool(_DASH_FENCE_RE.match(first_line))
            is_indented_code = first_line.startswith("    ") or first_line.startswith("\t")
            is_list = bool(re.match(r"\d+[.)]", trimmed)) or trimmed.startswith(("-", "*", "+"))
            is_toc_list = trimmed.startswith("-") and "[" in trimmed and "](" in trimmed
            is_marker_block = _is_marker_block(lines)
            is_page_marker = any(page_marker_pattern.match(line.strip()) for line in lines)
            if (
                is_table
                or is_heading
                or is_fenced_code
                or is_indented_code
                or is_list
                or is_toc_list
                or is_marker_block
                or is_page_marker
                or IMG_LINK_RE.search(part)
            ):
                processed_parts.append(part)
                continue
            try:
                processed = mdformat.text(
                    part,
                    options={"wrap": "no", "end_of_line": "lf"},
                    extensions={"gfm"},
                )
                processed_parts.append(processed.rstrip("\n"))
            except Exception:
                processed_parts.append(part)

        normalized = "\n\n".join(processed_parts)
    except Exception as exc:
        LOG.warning("mdformat paragraph unwrap failed: %s", exc)

    if md_text.endswith("\n") and not normalized.endswith("\n"):
        normalized += "\n"

    return _normalize_markdown_underscores(normalized)


def generate_markdown_toc(
    md_text: str
) -> List[Tuple[int, str]]:
    """Estrae voci di TOC dal Markdown e restituisce le intestazioni in memoria."""

    toc_sequence = _scan_markdown_for_toc_entries(md_text)
    heading_entries: List[Tuple[int, str]] = []

    for item in toc_sequence:
        kind, level, text, page_note = item
        if kind == "heading":
            heading_entries.append((level, text))

    return heading_entries


def parse_html_toc(toc_path: Path) -> Tuple[List[List[Any]], TocNode]:
    """@brief Parse toc.html into flat TOC entries and TocNode tree."""

    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"beautifulsoup4 not available: {exc}") from exc

    raw = toc_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    root_ul = soup.find("ul")
    entries: List[List[Any]] = []

    def walk_list(ul, level: int) -> None:
        for li in ul.find_all("li", recursive=False):
            anchor = None
            title = ""
            link = li.find("a", recursive=False)
            if link is not None:
                title = link.get_text(" ", strip=True)
                href = link.get("href") or ""
                if "#" in href:
                    anchor = href.split("#", 1)[1].strip() or None
            else:
                title = li.get_text(" ", strip=True)
            if title:
                entries.append([level, title, None, anchor])
            child_ul = li.find("ul", recursive=False)
            if child_ul is not None:
                walk_list(child_ul, level + 1)

    if root_ul is not None:
        walk_list(root_ul, 1)

    toc_root = build_toc_tree(entries)
    return entries, toc_root


def build_markdown_toc_from_entries(toc_entries: List[List[Any]]) -> str:
    """Genera il contenuto testuale della TOC a partire dalle voci TOC."""

    toc_lines: List[str] = []
    for entry in toc_entries:
        if len(entry) < 2:
            continue
        level = int(entry[0])
        title = str(entry[1]).strip()
        if not title:
            continue

        indent = "  " * max(0, level - 1)
        slug = _slugify_markdown_heading(title)
        toc_lines.append(f"{indent}- [{title}](#{slug})")

    content = "\n".join(toc_lines)
    return (content + "\n") if content else ""


def parse_markdown_toc(
    toc_content: str,
) -> Tuple[List[List[Any]], TocNode]:
    """Parsa il contenuto TOC restituendo la TOC raw e l'albero TOC."""

    lines = toc_content.splitlines()
    toc_raw: List[List[Any]] = []
    toc_item_re = re.compile(r"^(?P<indent>[ \t]*)-\s+\[(?P<title>.+?)\]\(#(?P<anchor>[^)]+)\)(?:\s+.*)?$")

    for line in lines:
        match = toc_item_re.match(line)
        if not match:
            continue
        indent = match.group("indent").replace("\t", "  ")
        level = max(1, len(indent) // 2 + 1)
        title = match.group("title").strip()
        if not title:
            continue
        anchor = match.group("anchor").strip() if match.group("anchor") else ""
        toc_raw.append([level, title, None, anchor or None])

    toc_root = build_toc_tree(toc_raw)
    return toc_raw, toc_root


def _extract_direct_image_url(content: str) -> str:
    """Estrae l'URL dell'immagine anche se il titolo non è racchiuso tra virgolette."""

    url_only, _ = _split_markdown_link(content)
    url_only = (url_only or "").strip()
    if not url_only:
        return url_only

    if url_only.startswith("<") and ">" in url_only:
        inner = url_only[1 : url_only.index(">")].strip()
        if inner:
            return inner

    if re.search(r"\s", url_only):
        first = url_only.split()[0].strip()
        if first.startswith("<") and first.endswith(">"):
            first = first[1:-1].strip()
        return first

    return url_only



def normalize_image_links(md_text: str) -> str:
    """Normalizza i link alle immagini esterne racchiudendoli tra marker dedicati.
    
    Ogni immagine embedded ![...](path) viene racchiusa tra:
    - <!-- Start of image -->
    - <!-- End of image -->
    
    Includendo anche il link diretto [path](path).
    
    Args:
        md_text: Contenuto Markdown da normalizzare
    
    Returns:
        Contenuto Markdown con link immagini normalizzati
    """
    if not md_text:
        return md_text
    
    lines = md_text.splitlines()
    result: List[str] = []
    image_pattern = re.compile(r'^(.*?)!\[([^\]]*)\]\(([^)]+)\)(.*)$')
    
    def _trim_blank_lines(block_lines: List[str]) -> List[str]:
        trimmed = list(block_lines)
        while trimmed and not trimmed[0].strip():
            trimmed.pop(0)
        while trimmed and not trimmed[-1].strip():
            trimmed.pop()
        return trimmed
    
    def _normalize_existing_image_block(block_lines: List[str]) -> List[str]:
        inner = block_lines[1:-1]
        image_alt = ""
        image_url = ""
        direct_url = ""
        equation_blocks: List[List[str]] = []
        annotation_blocks: List[List[str]] = []
        extra_lines: List[str] = []
        idx = 0
        while idx < len(inner):
            block_line = inner[idx]
            stripped = block_line.strip()
            if not stripped:
                idx += 1
                continue
            eq_start = EQUATION_BLOCK_START_RE.match(stripped)
            if eq_start:
                eq_block = [block_line]
                idx += 1
                while idx < len(inner):
                    eq_block.append(inner[idx])
                    if EQUATION_BLOCK_END_RE.match(inner[idx].strip()):
                        idx += 1
                        break
                    idx += 1
                equation_blocks.append(eq_block)
                continue
            ann_start = ANNOTATION_BLOCK_START_RE.match(stripped)
            if ann_start:
                ann_block = [block_line]
                idx += 1
                while idx < len(inner):
                    ann_block.append(inner[idx])
                    if ANNOTATION_BLOCK_END_RE.match(inner[idx].strip()):
                        idx += 1
                        break
                    idx += 1
                annotation_blocks.append(ann_block)
                continue
            match = image_pattern.match(block_line)
            if match:
                prefix = match.group(1).strip()
                alt = match.group(2)
                path = match.group(3)
                suffix = match.group(4).strip()
                url_only = _extract_direct_image_url(path)
                image_url = url_only or path
                image_alt = alt
                if prefix:
                    extra_lines.append(prefix)
                if suffix:
                    extra_lines.append(suffix)
                idx += 1
                continue
            direct_match = DIRECT_IMG_LINK_RE.search(block_line.strip())
            if direct_match:
                url_only = _extract_direct_image_url(direct_match.group(2))
                direct_url = url_only or direct_match.group(2).strip()
                idx += 1
                continue
            extra_lines.append(block_line)
            idx += 1
        
        if not image_url and not direct_url:
            return list(block_lines)
        if not image_url:
            image_url = direct_url
        if not direct_url:
            direct_url = image_url
        
        sections: List[List[str]] = []
        sections.append([f"![{image_alt}]({image_url})"])
        sections.append([f"[{direct_url}]({direct_url})"])
        for block in equation_blocks:
            sections.append(block)
        for block in annotation_blocks:
            sections.append(block)
        for extra in extra_lines:
            if extra.strip():
                sections.append([extra])
        
        normalized_block: List[str] = ["<!-- Start of image -->", ""]
        for section in sections:
            trimmed = _trim_blank_lines(section)
            if not trimmed:
                continue
            normalized_block.extend(trimmed)
            normalized_block.append("")
        if normalized_block and normalized_block[-1].strip():
            normalized_block.append("")
        normalized_block.append("<!-- End of image -->")
        normalized_block.append("")
        return normalized_block
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped == "<!-- Start of image -->":
            block_lines = [line]
            i += 1
            while i < len(lines):
                block_lines.append(lines[i])
                if lines[i].strip() == "<!-- End of image -->":
                    i += 1
                    break
                i += 1
            else:
                result.extend(block_lines)
                break
            normalized_block = _normalize_existing_image_block(block_lines)
            if result and result[-1].strip():
                result.append("")
            result.extend(normalized_block)
            continue
        
        match = image_pattern.match(line)
        if match:
            prefix = match.group(1).strip()
            alt = match.group(2)
            path = match.group(3)
            suffix = match.group(4).strip()
            
            if prefix:
                result.append(prefix)
            
            if result and result[-1].strip():
                result.append("")
            
            result.append("<!-- Start of image -->")
            result.append("")
            
            url_only = _extract_direct_image_url(path)
            embed_target = url_only or path
            result.append(f"![{alt}]({embed_target})")
            result.append("")
            
            result.append(f"[{embed_target}]({embed_target})")
            result.append("")
            
            result.append("<!-- End of image -->")
            result.append("")
            
            if suffix:
                result.append(suffix)
            i += 1
            continue
        
        result.append(line)
        i += 1
    
    normalized_md = "\n".join(result)
    return normalized_md


def normalize_markdown_file(
    toc_raw: List[List[Any]],
    toc_root: TocNode,
    md_content: str,
    out_dir: Path,
    *,
    add_toc: bool = True,
    md_headings: Optional[List[Tuple[int, str]]] = None,
) -> Tuple[str, List[Tuple[int, str]], List[List[Any]], Optional[Path], List[Tuple[int, str, Optional[str]]]]:
    """Normalizza il Markdown usando la TOC in memoria senza rigenerarla dal Markdown."""

    if toc_root is None:
        raise RuntimeError("toc_root is required to normalize the Markdown")

    def _build_document_headings(raw: List[List[Any]]) -> List[HeadingEntry]:
        headings: List[HeadingEntry] = []
        for entry in raw:
            if len(entry) < 2:
                continue
            try:
                level = int(entry[0])
            except Exception:
                continue
            title = str(entry[1]).strip()
            if not title:
                continue
            anchor = entry[3] if len(entry) >= 4 else None
            anchor = anchor or None
            headings.append((level, title, anchor))
        return headings

    md_text = normalize_image_links(md_content)
    md_text = normalize_markdown_format(md_text)
    document_headings = _build_document_headings(toc_raw)
    # DES-060: Do not modify headings in post-processing
    final_md = add_pdf_toc_to_markdown(md_text, document_headings if add_toc else []) if add_toc else md_text
    if md_headings is None:
        md_headings = []

    return final_md, md_headings, toc_raw, None, document_headings


def _normalize_title_for_toc(title: str) -> str:
    """Normalizza un titolo per confronti TOC eliminando differenze stilistiche."""

    norm = unicodedata.normalize("NFKD", title or "")
    norm = norm.replace("\u2019", "'").replace("\u2018", "'")
    norm = norm.replace("\u201c", '"').replace("\u201d", '"')
    norm = norm.replace("\u00a0", " ")
    norm = re.sub(r"\\([_*`])", r"\1", norm)
    norm = _strip_markdown_decoration(norm)
    # Remove arrow and bullet symbols used as decorative separators in headings
    # This allows matching headings where arrow position differs between TOC and content
    norm = re.sub(r"[\u2190-\u21FF\u25B6\u25BA\u25C0\u25C4\u2022\u2023\u2043]+", "", norm)
    norm = re.sub(r"^\d+(?:\.\d+)*\s+", "", norm)
    norm = re.sub(r"\s+", " ", norm)
    return norm.strip()


def validate_markdown_toc_against_document_toc(
    document_headings: List[HeadingEntry],
    headings_md: List[Tuple[int, str]],
) -> TocValidationResult:
    """Confronta la TOC estratta dal Markdown con tree.md restituendo l'esito senza interrompere il flusso."""

    titles_doc = [_normalize_title_for_toc(title) for _, title, _ in document_headings]
    titles_md = [_normalize_title_for_toc(title) for _, title in headings_md]

    mismatches: List[Tuple[int, str, str]] = []
    max_len = max(len(titles_doc), len(titles_md))
    for idx in range(max_len):
        pdf_title = titles_doc[idx] if idx < len(titles_doc) else "<missing>"
        md_title = titles_md[idx] if idx < len(titles_md) else "<missing>"
        if pdf_title != md_title:
            mismatches.append((idx, pdf_title, md_title))

    ok = len(mismatches) == 0
    if ok:
        reason = ""
    elif len(titles_doc) != len(titles_md):
        reason = f"TOC length differs (pdf={len(titles_doc)}, md={len(titles_md)})"
    else:
        first = mismatches[0]
        reason = (
            f"TOC content differs at position {first[0] + 1}: pdf='{first[1]}' vs md='{first[2]}'"
        )

    return TocValidationResult(
        ok=ok,
        pdf_titles=titles_doc,
        md_titles=titles_md,
        mismatches=mismatches,
        pdf_count=len(titles_doc),
        md_count=len(titles_md),
        reason=reason,
    )


def log_toc_validation_result(result: TocValidationResult, *, verbose: bool, debug: bool) -> None:
    """Emette log di esito TOC includendo evidenza dettagliata in verbose/debug."""

    if result.ok:
        if verbose:
            LOG.info("TOC validation passed (%d entries)", result.pdf_count)
        return

    base_msg = f"TOC mismatch between tree.md and Markdown headings (doc={result.pdf_count}, md={result.md_count})"
    if result.mismatches:
        first = result.mismatches[0]
        base_msg += (
            f"; first difference at position {first[0] + 1}: pdf='{first[1]}' vs md='{first[2]}'"
        )
    if result.reason:
        base_msg = f"{base_msg} | {result.reason}"
    LOG.error(base_msg)

    if verbose:
        LOG.info("TOC comparison (tree.md vs Markdown):")
        mismatch_idx = {idx for idx, _, _ in result.mismatches}
        max_len = max(result.pdf_count, result.md_count)
        for idx in range(max_len):
            pdf_title = result.pdf_titles[idx] if idx < result.pdf_count else "<missing>"
            md_title = result.md_titles[idx] if idx < result.md_count else "<missing>"
            status = "OK" if idx not in mismatch_idx else "FAIL"
            LOG.info(
                "[%d] %s | DOC=\"%s\" | MD=\"%s\"",
                idx + 1,
                status,
                pdf_title or "<empty>",
                md_title or "<empty>",
            )

    if debug:
        LOG.debug("TOC normalized tree.md titles (%d): %s", result.pdf_count, result.pdf_titles)
        LOG.debug("TOC normalized Markdown titles (%d): %s", result.md_count, result.md_titles)
        LOG.debug("TOC mismatches indexes: %s", [idx for idx, _, _ in result.mismatches])


def _guess_mime_type(path: Path) -> str:
    """Indovina il MIME type di un file immagine."""

    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream"


def _is_svg_mime(mime_type: str) -> bool:
    """Riconosce i MIME type SVG."""

    return "svg" in (mime_type or "").lower()


def _convert_svg_to_png(path: Path, svg_bytes: Optional[bytes] = None, png_path: Optional[Path] = None) -> bytes:
    """Converte un file SVG in PNG usando cairosvg e lo salva su disco se richiesto."""

    try:
        import cairosvg  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"cairosvg not available for SVG conversion: {exc}") from exc

    try:
        if svg_bytes is not None:
            png_bytes = cairosvg.svg2png(bytestring=svg_bytes)
        else:
            png_bytes = cairosvg.svg2png(url=str(path))
        if png_path is not None:
            png_path.parent.mkdir(parents=True, exist_ok=True)
            png_path.write_bytes(png_bytes)
        return png_bytes
    except Exception as exc:
        raise RuntimeError(f"Unable to convert SVG to PNG for {path}: {exc}") from exc


def _build_gemini_parts(prompt: str, mime_type: str, image_bytes: bytes) -> List[Dict[str, Any]]:
    """Costruisce il payload di richiesta Gemini usando inline_data per le immagini."""
    return [
        {
            "role": "user",
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": image_bytes}},
            ],
        }
    ]


def _init_gemini_model(api_key: str, model_name: str, module_path: str = "google.genai") -> Any:
    """Inizializza il modello Gemini usando esclusivamente il modulo python-genai (google.genai)."""

    try:
        genai = importlib.import_module(module_path)
    except ImportError as exc:  # pragma: no cover - dipendente dall'ambiente
        raise RuntimeError(f"Unable to import module {module_path}: {exc}") from exc

    if hasattr(genai, "configure"):
        genai.configure(api_key=api_key)

    if hasattr(genai, "GenerativeModel"):
        return genai.GenerativeModel(model_name)

    if hasattr(genai, "Client"):
        client = genai.Client(api_key=api_key)

        class _ClientWrapper:
            def __init__(self, client_obj: Any, name: str) -> None:
                self._client = client_obj
                self._model = name

            def generate_content(self, parts: Any) -> Any:
                return self._client.models.generate_content(model=self._model, contents=parts)

        return _ClientWrapper(client, model_name)

    raise RuntimeError(f"Module {module_path} does not provide GenerativeModel or Client APIs")


def _call_gemini_api(
    model: Any,
    parts: List[Dict[str, Any]],
    config: PostProcessingConfig,
    image_path: str,
    is_equation: bool,
) -> Any:
    """Wrapper per chiamate Gemini API con supporto per modalità emulazione.

    In modalità normale (gemini_api_emulation=False): esegue chiamate API reali.
    In modalità emulazione (gemini_api_emulation=True): genera risposte simulate.
    """
    if config.gemini_api_emulation:
        annotation_type = "Equation annotation" if is_equation else "Image annotation"
        model_name = config.gemini_model or GEMINI_DEFAULT_MODEL
        simulated_response = (
            f"_**{annotation_type}**_\n\n"
            f"**Emulated response for:** `{image_path}`\n\n"
            f"**Model:** {model_name}\n\n"
            f"This is a simulated annotation generated in emulation mode.\n"
        )
        
        class _EmulatedResponse:
            def __init__(self, text: str):
                self.text = text
        
        return _EmulatedResponse(simulated_response)
    
    if model is None:
        raise RuntimeError("Gemini model not initialized for real API call")
    
    return model.generate_content(parts)


def _run_pix2tex_test_mode(md_text: str, config: PostProcessingConfig) -> str:
    """Simula Pix2Tex con output deterministico durante gli unit test."""
    formula_raw = _get_test_pix2tex_formula()
    formulas: Dict[str, str] = {}
    if not formula_raw:
        if config.debug:
            LOG.debug("Pix2Tex test mode skipped because canned formula is empty")
        return md_text

    threshold = config.equation_min_len
    length = len(formula_raw)
    if length < threshold:
        if config.verbose:
            LOG.info(
                "Pix2Tex test mode skipped because canned formula length %d < threshold %d",
                length,
                threshold,
            )
        return md_text

    is_valid = validate_latex_formula(formula_raw)
    if not is_valid:
        if config.verbose:
            LOG.info("Pix2Tex test mode skipped because canned formula failed validation")
        return md_text

    image_paths_raw = extract_image_paths_from_markdown(md_text)
    seen: Set[str] = set()
    image_paths: List[str] = []
    for path in image_paths_raw:
        if path not in seen:
            seen.add(path)
            image_paths.append(path)
    total_images = len(image_paths)
    if config.verbose:
        LOG.info("Pix2Tex test mode active: using canned formula for %d images", total_images)
    for index, rel_path in enumerate(image_paths, start=1):
        base_name = Path(str(rel_path)).name
        if not base_name:
            continue
        formulas[base_name] = formula_raw
        if config.verbose:
            LOG.info("Pix2Tex images[%d/%d] %s validation result: PASSED (test mode)", index, total_images, rel_path)

    if not formulas:
        return md_text

    if config.debug:
        LOG.debug("Pix2Tex test mode formula applied: %s", formula_raw)

    if config.enable_pictex:
        md_text = embed_equations_in_markdown(md_text, formulas)
    return md_text


def run_pix2tex_phase(md_text: str, out_dir: Path, config: PostProcessingConfig) -> str:
    """Esegue Pix2Tex sulle immagini referenziate nel Markdown inserendo formule LaTeX."""
    if config.test_mode:
        return _run_pix2tex_test_mode(md_text, config)

    try:
        from PIL import Image  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"Pillow not available: {exc}") from exc

    try:
        from pix2tex.cli import LatexOCR  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"pix2tex not available: {exc}") from exc

    model = LatexOCR()
    formulas: Dict[str, str] = {}
    image_paths_raw = extract_image_paths_from_markdown(md_text)
    seen: Set[str] = set()
    image_paths: List[str] = []
    for path in image_paths_raw:
        if path not in seen:
            seen.add(path)
            image_paths.append(path)
    total_images = len(image_paths)
    for index, rel_path in enumerate(image_paths, start=1):
        if not rel_path:
            continue
        path = out_dir / normalize_path_for_md(str(rel_path))
        pos_ref = f"images[{index}/{total_images}]" if total_images else "images[?]"
        if config.verbose:
            _log_verbose_progress("Pix2Tex", index, total_images, detail=str(rel_path))
        try:
            img = Image.open(path)
        except Exception as exc:
            LOG.debug("Pix2Tex skipped %s (cannot open image): %s", path, exc)
            continue

        try:
            formula_raw = str(model(img)).strip()
        except Exception as exc:
            LOG.debug("Pix2Tex failed on %s: %s", path, exc)
            try:
                img.close()
            except Exception:
                pass
            continue
        finally:
            try:
                img.close()
            except Exception:
                pass

        if config.debug:
            LOG.debug("Pix2Tex %s raw output: %s", pos_ref, formula_raw)

        length = len(formula_raw)
        threshold = config.equation_min_len
        if length >= threshold:
            is_valid = validate_latex_formula(formula_raw)
            if config.verbose:
                status = "PASSED" if is_valid else "FAILED"
                LOG.info("Pix2Tex %s %s validation result: %s", pos_ref, rel_path, status)
            if is_valid:
                base_name = Path(rel_path).name
                formulas[base_name] = formula_raw
        else:
            if config.verbose:
                LOG.info("Pix2Tex %s %s validation result: SKIPPED (len=%d < threshold=%d)", pos_ref, rel_path, length, threshold)

    if formulas and config.enable_pictex:
        md_text = embed_equations_in_markdown(md_text, formulas)
    return md_text


def run_annotation_phase(
    md_text: str, out_dir: Path, config: PostProcessingConfig, pix2tex_executed: bool
) -> str:
    """Annota immagini con Gemini aggiornando il Markdown.

    La logica di annotazione dipende dalla combinazione dei flag Gemini e Pix2Tex:
    - Se Gemini e Pix2Tex entrambi abilitati:
      - Se enable_gemini_over_pixtex: annota TUTTE le immagini
      - Altrimenti: annota solo immagini NON annotate correttamente da Pix2Tex
    - Se Gemini abilitato e Pix2Tex disabilitato:
      - Annota TUTTE le immagini con PROMPT_UNCERTAIN_DEFAULT
    """
    if not config.enable_gemini:
        return md_text

    if not config.gemini_api_key and not config.gemini_api_emulation:
        LOG.warning("Gemini annotation requested but no API key or emulation mode provided. Skipping annotation.")
        return md_text

    model = None
    if not config.test_mode and not config.gemini_api_emulation:
        assert config.gemini_api_key is not None
        module_path = config.gemini_module or "google.genai"
        try:
            model = _init_gemini_model(
                config.gemini_api_key,
                config.gemini_model or GEMINI_DEFAULT_MODEL,
                module_path=module_path,
            )
        except Exception as exc:  # pragma: no cover - dipende da dipendenze esterne
            raise RuntimeError(f"Unable to initialize Gemini model: {exc}") from exc
    elif config.verbose:
        LOG.info("Gemini annotation test mode active: using canned responses")

    annotations: Dict[str, str] = {}
    image_paths_raw = extract_image_paths_from_markdown(md_text)
    seen: Set[str] = set()
    image_paths: List[str] = []
    for path in image_paths_raw:
        if path not in seen:
            seen.add(path)
            image_paths.append(path)
    equation_bases = extract_equation_basenames_from_markdown(md_text)
    total_images = len(image_paths)

    # Determine annotation strategy based on Gemini/Pix2Tex combination
    for index, rel_path in enumerate(image_paths, start=1):
        if not rel_path:
            continue
        base_name = Path(rel_path).name
        if not base_name:
            continue

        # Determine if image should be annotated based on new logic
        is_equation = base_name in equation_bases
        should_annotate = False

        if config.enable_pictex:
            # Both Gemini and Pix2Tex enabled
            if config.enable_gemini_over_pixtex:
                # Annotate ALL images
                should_annotate = True
            else:
                # Annotate only non-equation images (images NOT correctly annotated by Pix2Tex)
                should_annotate = not is_equation
        else:
            # Gemini enabled, Pix2Tex disabled: annotate ALL images
            should_annotate = True

        if not should_annotate:
            continue
        if config.verbose:
            _log_verbose_progress("Annotation", index, total_images, detail=str(rel_path))

        path = out_dir / normalize_path_for_md(str(rel_path))
        if config.verbose:
            LOG.info("Annotating %s: %s", "equation" if is_equation else "image", rel_path)
        try:
            if config.test_mode and not config.gemini_api_emulation:
                annotation_final = _get_test_annotation_text(is_equation, None)
            else:
                # Select appropriate prompt based on annotation strategy
                if config.enable_pictex:
                    # Both Gemini and Pix2Tex enabled
                    if config.enable_gemini_over_pixtex:
                        # Use PROMPT_EQUATION_DEFAULT or PROMPT_NON_EQUATION_DEFAULT
                        prompt = config.prompt_equation if is_equation else config.prompt_non_equation
                    else:
                        # Annotating only non-pixtex images
                        prompt = config.prompt_non_equation
                else:
                    # Gemini enabled, Pix2Tex disabled: use PROMPT_UNCERTAIN_DEFAULT
                    prompt = config.prompt_uncertain
                target_path = path
                mime_type = _guess_mime_type(path)
                is_svg = _is_svg_mime(mime_type)
                png_bytes: Optional[bytes] = None
                png_path: Optional[Path] = None
                if is_svg:
                    png_path = path.with_suffix(".png")
                    if not png_path.exists():
                        svg_bytes = path.read_bytes()
                        png_bytes = _convert_svg_to_png(path, svg_bytes=svg_bytes, png_path=png_path)
                    if png_path.exists():
                        target_path = png_path
                    else:
                        target_path = None
                    mime_type = "image/png"
                try:
                    if target_path is not None and target_path.exists():
                        image_bytes = target_path.read_bytes()
                    elif png_bytes is not None:
                        image_bytes = png_bytes
                    else:
                        raise RuntimeError(f"Converted PNG not available: {(png_path or path)}")
                except Exception as exc:
                    source_path = target_path if target_path else (png_path or path)
                    raise RuntimeError(f"Unable to read image {source_path}: {exc}") from exc
                parts = _build_gemini_parts(prompt, mime_type, image_bytes)
                try:
                    model_response = _call_gemini_api(model, parts, config, rel_path, is_equation)
                except Exception as exc:
                    if config.debug:
                        LOG.debug("Gemini request failed for %s", path.name, exc_info=exc)
                    raise RuntimeError(f"Gemini request failed for {path.name}: {exc}") from exc

                if config.debug:
                    LOG.debug("Gemini raw response for %s: %r", path.name, model_response)

                annotation_text = getattr(model_response, "text", "") if model_response is not None else ""
                if not annotation_text and hasattr(model_response, "candidates"):
                    candidates = getattr(model_response, "candidates", []) or []
                    if candidates:
                        annotation_text = getattr(candidates[0], "text", "") or getattr(candidates[0], "content", "") or ""

                if not annotation_text:
                    raise RuntimeError(f"Empty annotation from Gemini for {path.name}")

                annotation_final = str(annotation_text).strip()

            annotations[base_name] = annotation_final
            if config.verbose:
                LOG.info("Annotation completed: %s", rel_path)
            if config.debug:
                LOG.debug("Annotation content for %s: %s", rel_path, annotation_final)
        except Exception as exc:
            LOG.error("Annotation failed for %s: %s", rel_path, exc)
            if config.debug:
                LOG.debug("Annotation failure details for %s", rel_path, exc_info=exc)
            continue

    if annotations and config.enable_gemini:
        md_text = embed_annotations_in_markdown(md_text, annotations)

    return md_text


def processing_prepare_output_dirs(out_dir: Path, debug_enabled: bool) -> Tuple[Path, Path, Optional[Path]]:
    """Prepara le cartelle di output per immagini, tabelle e debug."""

    start_phase("Preparing output directories")
    images_dir = out_dir / "images"
    tables_dir = out_dir / "tables"
    debug_dir = out_dir / "debug" if debug_enabled else None
    images_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    if debug_dir is not None:
        debug_dir.mkdir(parents=True, exist_ok=True)
    end_phase()
    return images_dir, tables_dir, debug_dir


def copy_assets_dir(source_assets: Path, dest_assets: Path, verbose: bool = False) -> None:
    """@brief Copy HTML assets directory content into output images directory."""

    if dest_assets.exists():
        if dest_assets.is_dir():
            shutil.rmtree(dest_assets)
        else:
            dest_assets.unlink()
    shutil.copytree(source_assets, dest_assets)
    if verbose:
        LOG.info("Copied assets: %s -> %s", source_assets, dest_assets)


def convert_html_to_markdown(
    document_path: Path, *, verbose: bool = False
) -> Tuple[str, List[HtmlTable]]:
    """@brief Convert source HTML to markdown and serialize table placeholders."""
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"beautifulsoup4 not available: {exc}") from exc

    try:
        from markdownify import markdownify as md_convert  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"markdownify not available: {exc}") from exc

    raw_html = document_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup.find_all(["script", "style"]):
        tag.decompose()

    tables = extract_tables_from_html(soup)
    content = soup.body if soup.body is not None else soup
    html_str = str(content)

    if verbose:
        LOG.info("Converting HTML to Markdown via markdownify")

    md_text = md_convert(html_str, heading_style="ATX")
    md_text = _normalize_markdown_heading_text(md_text)
    md_text = _normalize_markdown_underscores(md_text)
    md_text = sanitize_image_links(md_text)
    md_text = replace_table_placeholders(md_text, tables)
    md_text = rewrite_image_links_to_assets_subdir(md_text, subdir="images")
    return md_text, tables


def run_processing_pipeline_html(
    *,
    from_dir: Path,
    out_dir: Path,
    post_processing_cfg: PostProcessingConfig,
    keep_intermediate_files: bool,
) -> Tuple[str, str, List[Tuple[int, str]]]:
    """@brief Execute HTML processing and return markdown, TOC markdown, and headings."""
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=False)

    start_phase("Processing pipeline (HTML)")

    images_dir, tables_dir, _ = processing_prepare_output_dirs(out_dir, bool(post_processing_cfg.debug))

    document_path = from_dir / "document.html"
    toc_path = from_dir / "toc.html"
    assets_source = from_dir / "assets"

    if not document_path.exists():
        raise RuntimeError(f"document.html not found in {from_dir}")
    if not toc_path.exists():
        raise RuntimeError(f"toc.html not found in {from_dir}")

    md_text, tables = convert_html_to_markdown(
        document_path,
        verbose=post_processing_cfg.verbose,
    )

    if tables:
        export_html_tables_files(tables_dir, tables)
        if post_processing_cfg.verbose:
            LOG.info("Exported %d table(s) to %s", len(tables), tables_dir)

    md_text = md_text.strip() + "\n"

    if not check_fenced_code_balanced(md_text):
        raise RuntimeError("Unbalanced fenced code blocks detected in processing content")

    if assets_source.exists() and assets_source.is_dir():
        copy_assets_dir(assets_source, images_dir, verbose=post_processing_cfg.verbose)
    else:
        if post_processing_cfg.verbose:
            LOG.info(
                "No assets directory in source; skipping assets copy. Empty images/ left in output: %s",
                images_dir,
            )

    toc_entries, _toc_root = parse_html_toc(toc_path)
    toc_content = build_markdown_toc_from_entries(toc_entries)
    if post_processing_cfg.verbose:
        LOG.info("Generated TOC content from toc.html (%d entries)", len(toc_entries))

    try:
        delete_empty_folders(out_dir, verbose=post_processing_cfg.verbose)
    except Exception:
        LOG.debug("Error while attempting to delete empty image/table folders", exc_info=True)

    md_text = demote_headings_not_in_toc_html(md_text, toc_entries)
    md_headings = generate_markdown_toc(md_text)

    if keep_intermediate_files:
        processing_path = out_dir / "processing.md"
        safe_write_text(processing_path, md_text)
        if post_processing_cfg.verbose:
            LOG.info("Intermediate file created: %s", processing_path)

    return md_text, toc_content, md_headings


def processing_setup_layout(verbose: bool) -> bool:
    """Inizializza i moduli di layout opzionali restituendo lo stato abilitato."""
    layout_enabled = False
    if verbose:
        LOG.info("Loading PDF and preparing layout modules...")
    try:
        import pymupdf.layout  # noqa: F401  # type: ignore[reportMissingImports]

        layout_enabled = True
    except Exception as exc:
        LOG.warning("pymupdf-layout not active (legacy fallback). Detail: %s", exc)
    return layout_enabled


def processing_import_pymupdf4llm() -> Any:
    """Importa pymupdf4llm fallendo in modo esplicito in caso di errore."""

    try:
        import pymupdf4llm  # type: ignore[reportMissingImports]

        return pymupdf4llm
    except Exception as exc:
        LOG.error("Unable to import pymupdf4llm: %s", exc)
        raise


def processing_open_documents(pdf_path: Path) -> Tuple[pymupdf.Document, pymupdf.Document]:
    """Apre due handle PyMuPDF separati per immagini e testo."""

    doc_images = pymupdf.open(str(pdf_path))
    doc_text = pymupdf.open(str(pdf_path))
    return doc_images, doc_text


def processing_select_pages_and_toc(
    *,
    doc_images: pymupdf.Document,
    doc_text: pymupdf.Document,
    pdf_path: Path,
    args: argparse.Namespace,
) -> Tuple[Dict[str, Any], List[List[Any]], TocNode, int, int, int, int, int, int]:
    """Applica la selezione pagine, raccoglie metadata e TOC, restituendo i parametri di range."""

    def _close_documents() -> None:
        try:
            doc_images.close()
        except Exception:
            pass
        try:
            doc_text.close()
        except Exception:
            pass

    metadata: Dict[str, Any] = {}
    toc_raw: List[List[Any]] = []
    try:
        metadata = doc_text.metadata or {}
    except Exception as exc:
        LOG.debug("doc.metadata failed: %s", exc)
    try:
        toc_raw = doc_text.get_toc() or []
    except Exception as exc:
        LOG.debug("doc.get_toc failed: %s", exc)
    original_page_count = getattr(doc_text, "page_count", 0)
    start_page = int(args.start_page or 1)
    page_offset = max(start_page - 1, 0)
    requested_limit: int = 0
    page_range_end: int = 0

    if original_page_count > 0:
        if start_page > original_page_count:
            _close_documents()
            raise RuntimeError(
                f"Start page {start_page} exceeds document page count {original_page_count}"
            )
        available_from_start = original_page_count - page_offset
        if available_from_start <= 0:
            _close_documents()
            raise RuntimeError(
                f"Start page {start_page} exceeds document page count {original_page_count}"
            )
        if args.n_pages is not None:
            requested_limit = int(args.n_pages)
            if requested_limit > available_from_start:
                _close_documents()
                raise RuntimeError(
                    f"Requested page range {start_page}-{start_page + requested_limit - 1} exceeds document page count {original_page_count}"
                )
            if args.verbose and page_offset == 0 and requested_limit == original_page_count:
                LOG.info(
                    "Requested page limit %d covers all %d page(s); processing entire document",
                    args.n_pages,
                    original_page_count,
                )
        else:
            requested_limit = available_from_start

        page_range_end = start_page + requested_limit - 1
        if page_offset > 0 or requested_limit < original_page_count:
            page_indices = list(range(page_offset, page_offset + requested_limit))
            doc_images.select(page_indices)
            doc_text.select(page_indices)
            if args.verbose:
                LOG.info(
                    "Limiting processing to PDF pages %d-%d (%d page(s) selected out of %d)",
                    start_page,
                    page_range_end,
                    requested_limit,
                    original_page_count,
                )
    else:
        requested_limit = getattr(doc_text, "page_count", 0) or 0
        page_range_end = start_page + max(requested_limit - 1, 0)

    apply_vertical_crop_margins(
        doc_text, header_mm=args.header, footer_mm=args.footer, debug=bool(args.debug), verbose=bool(args.verbose)
    )

    processed_page_count = requested_limit or getattr(doc_text, "page_count", original_page_count)
    toc = toc_raw
    if toc_raw and page_range_end is not None:
        selection_start = start_page
        selection_end = page_range_end
        if selection_start > 1 or (original_page_count and selection_end < original_page_count):
            toc_limited = []
            for entry in toc_raw:
                if len(entry) < 3:
                    continue
                try:
                    page_no = int(entry[2])
                except Exception:
                    continue
                if selection_start <= page_no <= selection_end:
                    toc_limited.append(entry)
            if toc_limited:
                toc = toc_limited

    toc_root = build_toc_tree(toc)

    if not toc_raw:
        _close_documents()
        raise RuntimeError(f"TOC not found in PDF: {pdf_path}")

    return (
        metadata,
        toc,
        toc_root,
        processed_page_count,
        page_offset,
        page_range_end or processed_page_count,
        requested_limit or processed_page_count,
        original_page_count,
        start_page,
    )


def processing_extract_chunks(
    *,
    doc_images: pymupdf.Document,
    doc_text: pymupdf.Document,
    images_dir: Path,
    image_write_dir: Path,
    args: argparse.Namespace,
    layout_enabled: bool,
    pymupdf4llm: Any,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Estrae i chunk Markdown con e senza immagini inline."""

    def _run_to_markdown(use_ocr: bool) -> Tuple[Any, Any]:
        md_kwargs_common = dict(
            page_chunks=True,
            force_text=True,
            show_progress=bool(args.verbose),
            page_separators=bool(args.debug),
            header=True,
            footer=True,
            use_ocr=use_ocr,
            table_strategy="lines_strict",
        )

        md_kwargs_images = dict(
            md_kwargs_common,
            write_images=True,
            embed_images=False,
            image_path=str(image_write_dir),
            image_format="png",
            dpi=150,
        )
        md_kwargs_text = dict(
            md_kwargs_common,
            write_images=False,
            embed_images=False,
            image_path=str(images_dir),
            image_format="png",
            dpi=150,
        )

        if args.verbose:
            LOG.info("Extracting Markdown with inline image generation...")
        extracted_images = pymupdf4llm.to_markdown(doc_images, **md_kwargs_images)
        if args.verbose:
            LOG.info("Extracting Markdown text without embedding images...")
        extracted_text = pymupdf4llm.to_markdown(doc_text, **md_kwargs_text)
        return extracted_images, extracted_text

    def _is_tesseract_language_missing(exc: Exception) -> bool:
        """Check if the exception indicates Tesseract English language data file is missing."""
        msg = str(exc).lower()
        indicators = [
            "failed loading language 'eng'",
            "tesseract couldn't load any languages!",
            "tessdata/eng.traineddata",
            "language initialisation failed",
            "language initialization failed",
        ]
        return any(indicator in msg for indicator in indicators)

    def _is_other_ocr_failure(exc: Exception) -> bool:
        """Check if the exception indicates a non-language-related OCR failure."""
        msg = str(exc).lower()
        # Check for OCR failures but exclude language-specific errors
        if _is_tesseract_language_missing(exc):
            return False
        if "tesseract" in msg or "tessdata" in msg:
            return True
        if "ocr" in msg and "fail" in msg:
            return True
        return isinstance(exc, getattr(pymupdf.mupdf, "FzErrorLibrary", Exception))

    start_phase("Extracting Markdown and assets")
    try:
        chunks_images, chunks_text = _run_to_markdown(bool(layout_enabled))
    except Exception as exc:
        if layout_enabled:
            # Check for missing Tesseract language file (critical error)
            if _is_tesseract_language_missing(exc):
                LOG.error("Tesseract OCR is missing the English language data file.")
                LOG.error("Please install it with: sudo apt-get install tesseract-ocr-eng")
                raise SystemExit(EXIT_INVALID_ARGS)
            # Check for other OCR failures (fallback to legacy)
            if _is_other_ocr_failure(exc):
                LOG.warning("OCR failed; retrying with OCR disabled. Detail: %s", exc)
                chunks_images, chunks_text = _run_to_markdown(False)
            else:
                raise
        else:
            raise
    end_phase()

    if isinstance(chunks_images, str):
        chunks_images = [{"text": chunks_images}]
    if isinstance(chunks_text, str):
        chunks_text = [{"text": chunks_text}]

    return chunks_images, chunks_text


def insert_inline_tables_from_disk(md_text: str, out_dir: Path, verbose: bool = False) -> str:
    """
    Inserisce il contenuto delle tabelle inline leggendo i file Markdown da disco.

    Per ogni sezione racchiusa tra <!-- Start of table --> e <!-- End of table -->,
    estrae il percorso del file Markdown dal link [Markdown](tables/<filename>.md),
    legge il contenuto del file, e lo inserisce all'inizio della sezione subito dopo
    il marker di inizio, rispettando le righe vuote di separazione.

    DES-062, REQ-020
    """
    lines = md_text.splitlines()
    output: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if we found a table start marker
        if line.strip() == "<!-- Start of table -->":
            # Find the end marker
            end_idx = -1
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "<!-- End of table -->":
                    end_idx = j
                    break

            if end_idx == -1:
                # No end marker found, keep the line as-is
                output.append(line)
                i += 1
                continue

            # Extract the section between markers
            section_lines = lines[i:end_idx + 1]

            # Look for the [Markdown](tables/...) link
            md_link_pattern = re.compile(r'\[Markdown\]\(tables/([^)]+\.md)\)')
            table_file_path: Optional[Path] = None

            for section_line in section_lines:
                match = md_link_pattern.search(section_line)
                if match:
                    relative_path = match.group(1)
                    table_file_path = out_dir / "tables" / relative_path
                    break

            # Read table content from disk
            table_content: Optional[str] = None
            if table_file_path and table_file_path.exists():
                try:
                    table_content = table_file_path.read_text(encoding="utf-8").strip()
                    if verbose:
                        LOG.info("Loaded inline table content from: %s", table_file_path)
                except Exception as exc:
                    LOG.warning("Failed to read table file %s: %s", table_file_path, exc)
            elif table_file_path and not table_file_path.exists():
                LOG.warning("Table file not found: %s", table_file_path)

            md_link: Optional[str] = None
            json_link: Optional[str] = None
            for section_line in section_lines:
                stripped = section_line.strip()
                if stripped.startswith("[Markdown]("):
                    md_link = stripped
                elif stripped.startswith("[JSON]("):
                    json_link = stripped

            # Reconstruct the section with inline content
            output.append("<!-- Start of table -->")
            output.append("")

            if table_content:
                output.append(table_content)
                output.append("")

            # Add the links with required spacing
            if md_link:
                output.append(md_link)
                output.append("")
            if json_link:
                output.append(json_link)
                output.append("")

            output.append("<!-- End of table -->")
            output.append("")

            # Skip to the line after the end marker
            i = end_idx + 1
        else:
            output.append(line)
            i += 1

    result = "\n".join(output)
    # Remove excessive blank lines while preserving intentional spacing
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def run_post_processing_pipeline(
    *,
    out_dir: Path,
    md_content: str,
    md_headings: List[Tuple[int, str]],
    config: PostProcessingConfig,
    toc_content: str,
) -> Tuple[str, bool]:
    """Esegue la pipeline di post-processing sul contenuto Markdown passato in memoria."""
    _configure_tomarkdown_logger(_resolve_log_level(config.verbose, config.debug))

    md_path = out_dir / "document.md"

    def _save_markdown(md_text: str) -> str:
        """Salva il Markdown corrente su disco garantendo il newline finale."""

        final_text = md_text if md_text.endswith("\n") else f"{md_text}\n"
        safe_write_text(md_path, final_text)
        return final_text

    if not check_fenced_code_balanced(md_content):
        raise RuntimeError("Unbalanced fenced code blocks detected in input markdown content")

    updated_md = md_content

    document_toc_raw, toc_root = parse_markdown_toc(toc_content)
    (
        normalized_md_text,
        md_headings,
        toc_raw,
        toc_path,
        document_headings,
    ) = normalize_markdown_file(
        document_toc_raw,
        toc_root,
        updated_md,
        out_dir,
        add_toc=False,  # TOC insertion moved to final operation (DES-058, REQ-037)
        md_headings=md_headings,
    )
    normalized_md_text = _save_markdown(normalized_md_text)

    toc_mismatch = False
    if config.skip_toc_validation:
        LOG.info(
            "TOC validation skipped in test mode for limited page range (set TOMARKDOWN_FORCE_TOC_VALIDATION=1 to enforce)."
        )
    else:
        toc_result = validate_markdown_toc_against_document_toc(document_headings, md_headings)
        log_toc_validation_result(toc_result, verbose=config.verbose, debug=config.debug)
        toc_mismatch = not toc_result.ok

    updated_md = normalized_md_text
    pix2tex_executed = False

    # Insert inline tables from disk if enabled (DES-062, REQ-020)
    if config.enable_inline_tables:
        updated_md = insert_inline_tables_from_disk(updated_md, out_dir, verbose=config.verbose)
        updated_md = _save_markdown(updated_md)

    updated_md = rename_images_phase(md_text=updated_md, out_dir=out_dir, config=config)
    updated_md = _save_markdown(updated_md)

    if not config.disable_remove_small_images:
        updated_md = fix_missing_links(md_text=updated_md, out_dir=out_dir, config=config)
        updated_md = _save_markdown(updated_md)
        updated_md = remove_small_images_phase(md_text=updated_md, out_dir=out_dir, config=config)
        updated_md = _save_markdown(updated_md)

    if config.enable_pictex:
        updated_md = run_pix2tex_phase(updated_md, out_dir, config)
        pix2tex_executed = True
        updated_md = _save_markdown(updated_md)

    if config.enable_gemini:
        updated_md = run_annotation_phase(updated_md, out_dir, config, pix2tex_executed=pix2tex_executed)
        updated_md = _save_markdown(updated_md)

    if not config.disable_cleanup:
        if not check_fenced_code_balanced(updated_md):
            raise RuntimeError("Unbalanced fenced code blocks detected before cleanup_markdown")
        updated_md = cleanup_markdown(updated_md, document_headings)
        updated_md = _save_markdown(updated_md)
    elif config.verbose:
        LOG.info("Cleanup disabled via --disable-cleanup flag; Markdown markers preserved.")

    updated_md = _save_markdown(updated_md)
    try:
        final_text = md_path.read_text(encoding="utf-8")
    except Exception:
        final_text = updated_md
    if not check_fenced_code_balanced(final_text):
        raise RuntimeError("Unbalanced fenced code blocks detected after final Markdown save")

    toc_html = out_dir / "toc.html"
    if toc_html.exists():
        try:
            toc_html.unlink()
            if config.verbose:
                LOG.info("Removed toc.html: %s", toc_html)
        except Exception as exc:
            LOG.warning("Unable to remove toc.html %s: %s", toc_html, exc)

    delete_empty_folders(out_dir, verbose=config.verbose)

    # Insert TOC as last operation before final save (DES-058, REQ-037)
    if config.add_toc and toc_content.strip():
        # Build full TOC markdown section with fences and marker
        toc_markdown = build_toc_markdown(toc_content)
        if not toc_markdown:
            return updated_md, toc_mismatch

        # Extract front matter if present
        lines = updated_md.split('\n')
        front_matter_end = 0
        if lines and lines[0].strip() == '---':
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    front_matter_end = i + 1
                    break
        
        if front_matter_end > 0:
            front_matter = '\n'.join(lines[:front_matter_end]).rstrip('\n')
            body = '\n'.join(lines[front_matter_end:]).lstrip('\n')
            updated_md = f"{front_matter}\n\n{toc_markdown}\n\n{body}"
        else:
            body = updated_md.lstrip('\n')
            updated_md = f"\n{toc_markdown}\n\n{body}"
        
        updated_md = _save_markdown(updated_md)
        if config.verbose:
            LOG.info("TOC Markdown section inserted in document.md")

    return updated_md, toc_mismatch


# def find_existing_markdown(out_dir: Path, pdf_stem: Optional[str]) -> Optional[Path]:
#     """Trova un file Markdown esistente nella cartella di output per il PDF indicato."""
#
#     document_md = out_dir / "document.md"
#     if document_md.exists():
#         return document_md
#     if pdf_stem:
#         candidate = out_dir / f"{slugify_filename(pdf_stem)}.md"
#         if candidate.exists():
#             return candidate
#     md_files = sorted(out_dir.glob("*.md"))
#     return md_files[0] if md_files else None
#
#
def promote_bold_to_heading_pdf(md_text: str, toc_headings: List[HeadingEntry]) -> Tuple[str, List[HeadingEntry]]:
    """Promuove i titoli in grassetto a heading Markdown basandosi sulla TOC PDF.

    Implementa algoritmo page-aware con:
    - Raggruppamento TOC per pagina
    - Pattern matching sequenziale (bold variations, case-sensitive/insensitive)
    - Fence skipping (picture text, image, table)
    - Warning e rimozione voci TOC non trovate
    - Sostituzione esatta con testo e livello TOC

    Args:
        md_text: Contenuto Markdown da processare
        toc_headings: Lista TOC entries [level, title, page]

    Returns:
        Tuple (modified_markdown, filtered_toc) dove filtered_toc esclude voci non trovate
    """
    if not md_text or not toc_headings:
        return md_text, toc_headings

    lines = md_text.splitlines()

    # Build fence skip mask (fenced code + picture text + image + table)
    fenced_lines = _get_fenced_line_mask(lines)

    # Add picture text fences
    in_fence = False
    for idx, raw in enumerate(lines):
        stripped = raw.strip().lower()
        if stripped == "<!-- start of picture text -->":
            in_fence = True
            fenced_lines.add(idx)
        elif stripped == "<!-- end of picture text -->":
            fenced_lines.add(idx)
            in_fence = False
        elif in_fence:
            fenced_lines.add(idx)

    # Add image fences
    in_fence = False
    for idx, raw in enumerate(lines):
        stripped = raw.strip().lower()
        if stripped == "<!-- start of image -->":
            in_fence = True
            fenced_lines.add(idx)
        elif stripped == "<!-- end of image -->":
            fenced_lines.add(idx)
            in_fence = False
        elif in_fence:
            fenced_lines.add(idx)

    # Add table fences
    in_fence = False
    for idx, raw in enumerate(lines):
        stripped = raw.strip().lower()
        if stripped == "<!-- start of table -->":
            in_fence = True
            fenced_lines.add(idx)
        elif stripped == "<!-- end of table -->":
            fenced_lines.add(idx)
            in_fence = False
        elif in_fence:
            fenced_lines.add(idx)

    # Extract page markers and build page ranges
    page_markers: Dict[int, int] = {}
    for idx, raw in enumerate(lines):
        if idx in fenced_lines:
            continue
        match = PAGE_START_MARKER_CAPTURE_RE.match(raw.strip())
        if match:
            try:
                page_markers[int(match.group(1))] = idx
            except Exception:
                pass

    page_ranges: Dict[int, Tuple[int, int]] = {}
    if page_markers:
        ordered_pages = sorted(page_markers.items(), key=lambda item: item[1])
        for idx_pair, (page_no, start_idx) in enumerate(ordered_pages):
            # Find end marker for this page
            end_idx = len(lines)
            for check_idx in range(start_idx + 1, len(lines)):
                if check_idx in fenced_lines:
                    continue
                end_match = PAGE_END_MARKER_CAPTURE_RE.match(lines[check_idx].strip())
                if end_match:
                    try:
                        if int(end_match.group(1)) == page_no:
                            end_idx = check_idx
                            break
                    except Exception:
                        pass
            page_ranges[page_no] = (start_idx + 1, end_idx)  # Start after marker, end before end marker

    # Parse and index TOC entries with original index tracking
    original_idx_to_parsed: Dict[int, int] = {}  # original idx -> parsed idx
    parsed_entries: List[Tuple[int, str, Optional[int]]] = []  # (level, title, page)
    for orig_idx, entry in enumerate(toc_headings):
        if len(entry) < 2:
            continue
        try:
            level = int(entry[0])
            title = str(entry[1])
            page: Optional[int] = None
            if len(entry) >= 3 and entry[2] is not None:
                page = int(entry[2])
            original_idx_to_parsed[orig_idx] = len(parsed_entries)
            parsed_entries.append((level, title, page))
        except Exception:
            continue

    # Group TOC entries by page (use -1 for entries without page number to process globally)
    page_to_toc: Dict[int, List[Tuple[int, int, str]]] = {}  # page -> [(parsed_idx, level, title)]
    for parsed_idx, (level, title, page) in enumerate(parsed_entries):
        page_key = page if page is not None else -1
        if page_key not in page_to_toc:
            page_to_toc[page_key] = []
        page_to_toc[page_key].append((parsed_idx, level, title))

    # Track search position per page
    page_search_pos: Dict[int, int] = {}
    for page, (start, _) in page_ranges.items():
        page_search_pos[page] = start

    # Track found parsed indices
    found_parsed_indices: Set[int] = set()

    # Helper to build patterns
    def _build_patterns(title: str) -> List[Tuple[re.Pattern, bool]]:
        """Build sequential matching patterns for a TOC title."""
        # Normalize the title for pattern matching (strip, but keep structure)
        title_stripped = title.strip()
        escaped = re.escape(title_stripped)
        return [
            # Case-sensitive patterns first
            (re.compile(r"^\s*_\*\*\s*" + escaped + r"\s*\*\*_\s*$"), False),
            (re.compile(r"^\s*\*\*\s*" + escaped + r"\s*\*\*\s*$"), False),
            (re.compile(r"^\s*\*\s*" + escaped + r"\s*\*\s*$"), False),
            (re.compile(r"^\s*" + escaped + r"\s*$"), False),
            # Case-insensitive patterns
            (re.compile(r"^\s*_\*\*\s*" + escaped + r"\s*\*\*_\s*$", re.IGNORECASE), True),
            (re.compile(r"^\s*\*\*\s*" + escaped + r"\s*\*\*\s*$", re.IGNORECASE), True),
            (re.compile(r"^\s*\*\s*" + escaped + r"\s*\*\s*$", re.IGNORECASE), True),
            (re.compile(r"^\s*" + escaped + r"\s*$", re.IGNORECASE), True),
        ]

    # Process pages in order
    for page in sorted(page_to_toc.keys()):
        # Handle entries without page number (page=-1): search entire document
        if page == -1:
            start, end = 0, len(lines)
            search_pos = 0
        elif page not in page_ranges:
            # Page not in markdown, log warning for all TOC entries on this page
            for parsed_idx, level, title in page_to_toc[page]:
                LOG.warning("TOC entry not found (page %d not in markdown): [%s] %s", page, "#" * level, title)
            continue
        else:
            start, end = page_ranges[page]
            search_pos = page_search_pos[page]

        # Process TOC entries for this page in order
        for parsed_idx, level, title in page_to_toc[page]:
            patterns = _build_patterns(title)

            found = False
            for line_idx in range(search_pos, end):
                if line_idx in fenced_lines:
                    continue

                line = lines[line_idx]
                stripped = line.strip()
                if not stripped:
                    continue

                # First check if it's already a heading matching this TOC entry
                heading_match = re.match(r"^\s*(#{1,})\s+(.+?)\s*$", stripped)
                if heading_match:
                    heading_text = heading_match.group(2)
                    # Strip any markdown decorations (bold, italic) for comparison
                    heading_text_clean = _strip_markdown_decoration(heading_text).strip()
                    # Normalize for comparison
                    if _normalize_title_for_toc(heading_text_clean) == _normalize_title_for_toc(title):
                        # Already a heading! Update to exact TOC text and level
                        leading_ws = line[:len(line) - len(line.lstrip())]
                        heading_line = f"{leading_ws}{'#' * max(1, level)} {title}"
                        lines[line_idx] = heading_line
                        found_parsed_indices.add(parsed_idx)
                        if page != -1:
                            page_search_pos[page] = line_idx + 1
                        search_pos = line_idx + 1
                        found = True
                        break

                # Try each bold pattern in sequence
                for pattern, is_case_insensitive in patterns:
                    if pattern.match(stripped):
                        # Found match! Replace with heading
                        leading_ws = line[:len(line) - len(line.lstrip())]
                        heading_line = f"{leading_ws}{'#' * max(1, level)} {title}"
                        lines[line_idx] = heading_line
                        found_parsed_indices.add(parsed_idx)
                        if page != -1:
                            page_search_pos[page] = line_idx + 1
                        search_pos = line_idx + 1
                        found = True
                        break

                if found:
                    break

            if not found:
                # TOC entry not found in remaining page section
                LOG.warning("TOC entry not found on page %d: [%s] %s", page, "#" * level, title)

    # Build filtered TOC (only entries that were found)
    filtered_toc: List[HeadingEntry] = []
    for orig_idx, entry in enumerate(toc_headings):
        if orig_idx in original_idx_to_parsed:
            parsed_idx = original_idx_to_parsed[orig_idx]
            if parsed_idx in found_parsed_indices:
                filtered_toc.append(entry)
        else:
            # Entry was skipped during parsing (malformed), keep it anyway
            filtered_toc.append(entry)

    return "\n".join(lines), filtered_toc


def demote_headings_not_in_toc_pdf(md_text: str, toc_headings: List[HeadingEntry]) -> str:
    """Degrada le intestazioni Markdown non presenti nella TOC PDF rispettando il contesto di pagina."""

    if not md_text or not toc_headings:
        return md_text

    lines = md_text.splitlines()

    # Skip code fences but process custom fences by demoting headings inside them.
    fenced_lines = _get_fenced_line_mask(lines)

    custom_fences: Set[int] = set()

    def _mark_custom_fence(start_token: str, end_token: str) -> None:
        in_fence = False
        for idx, raw in enumerate(lines):
            stripped = raw.strip().lower()
            if stripped == start_token:
                in_fence = True
                custom_fences.add(idx)
                continue
            if stripped == end_token:
                custom_fences.add(idx)
                in_fence = False
                continue
            if in_fence:
                custom_fences.add(idx)

    _mark_custom_fence("<!-- start of picture text -->", "<!-- end of picture text -->")
    _mark_custom_fence("<!-- start of image -->", "<!-- end of image -->")
    _mark_custom_fence("<!-- start of table -->", "<!-- end of table -->")

    expected_by_page: Dict[int, Dict[str, int]] = {}
    expected_global: Dict[str, int] = {}

    for entry in toc_headings:
        if len(entry) < 2:
            continue
        title = str(entry[1]).strip()
        if not title:
            continue
        normalized = _normalize_title_for_toc(title)
        page_no: Optional[int] = None
        if len(entry) >= 3 and entry[2] is not None:
            try:
                page_no = int(entry[2])
            except Exception:
                page_no = None
        if page_no is None:
            expected_global[normalized] = expected_global.get(normalized, 0) + 1
        else:
            page_map = expected_by_page.setdefault(page_no, {})
            page_map[normalized] = page_map.get(normalized, 0) + 1

    def _strip_bold(text: str) -> str:
        """Rimuove il grassetto/corsivo esterno se presente restituendo il testo pulito."""

        t = text.strip()
        while (t.startswith("_") and t.endswith("_") and len(t) > 2
               and not t.startswith("__")):
            t = t[1:-1].strip()
        if (t.startswith("**") and t.endswith("**")) or (t.startswith("__") and t.endswith("__")):
            return t[2:-2].strip()
        return t

    def _consume(counter: Dict[str, int], key: str) -> bool:
        count = counter.get(key, 0)
        if count <= 0:
            return False
        counter[key] = count - 1
        return True

    heading_re = re.compile(r"^(?P<prefix>\s*)(?P<hashes>#{1,})\s+(?P<title>.+?)\s*$")
    removed_anchors: Set[str] = set()
    output: List[str] = []
    current_page: Optional[int] = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        start_match = PAGE_START_MARKER_CAPTURE_RE.match(stripped)
        if start_match:
            try:
                current_page = int(start_match.group(1))
            except Exception:
                current_page = None
            output.append(line)
            continue
        end_match = PAGE_END_MARKER_CAPTURE_RE.match(stripped)
        if end_match:
            output.append(line)
            current_page = None
            continue

        if idx in fenced_lines:
            output.append(line)
            continue

        match = heading_re.match(line)
        if not match:
            output.append(line)
            continue

        title_raw = match.group("title").strip()
        normalized = _normalize_title_for_toc(title_raw)

        should_keep = False
        if idx not in custom_fences:
            if current_page is not None:
                page_expected = expected_by_page.get(current_page)
                if page_expected and _consume(page_expected, normalized):
                    should_keep = True
            if not should_keep and expected_global and _consume(expected_global, normalized):
                should_keep = True

        if should_keep:
            output.append(line)
            continue

        clean_title = _strip_bold(title_raw).upper()
        bold_title = f"**{clean_title}**"
        output.append(f"{match.group('prefix')}{bold_title}")
        removed_anchors.add(_slugify_markdown_heading(_strip_bold(title_raw)))

    result = "\n".join(output)
    result = _remove_heading_links(result, removed_anchors)
    if md_text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def demote_headings_not_in_toc_html(md_text: str, toc_entries: List[List[Any]]) -> str:
    """Allinea gli heading HTML alla TOC o li converte in grassetto maiuscolo."""

    if not md_text or not toc_entries:
        return md_text

    expected: List[Tuple[int, str]] = []
    for entry in toc_entries:
        if len(entry) < 2:
            continue
        title = str(entry[1]).strip()
        if not title:
            continue
        try:
            level = int(entry[0])
        except Exception:
            continue
        expected.append((level, title))

    if not expected:
        return md_text

    lines = md_text.splitlines()
    fenced_lines = _get_fenced_line_mask(lines)
    heading_re = re.compile(r"^(?P<prefix>\s*)(?P<hashes>#{1,})\s+(?P<title>.+?)\s*$")

    def _strip_bold(text: str) -> str:
        """Rimuove il grassetto/corsivo esterno se presente restituendo il testo pulito."""

        t = text.strip()
        while (t.startswith("_") and t.endswith("_") and len(t) > 2
               and not t.startswith("__")):
            t = t[1:-1].strip()
        if (t.startswith("**") and t.endswith("**")) or (t.startswith("__") and t.endswith("__")):
            return t[2:-2].strip()
        return t

    expected_idx = 0
    output: List[str] = []

    for idx, line in enumerate(lines):
        if idx in fenced_lines:
            output.append(line)
            continue

        match = heading_re.match(line)
        if not match:
            output.append(line)
            continue

        level = len(match.group("hashes"))
        title_raw = match.group("title").strip()
        if expected_idx < len(expected):
            exp_level, exp_title = expected[expected_idx]
            if title_raw == exp_title:
                expected_idx += 1
                hashes = "#" * max(1, exp_level)
                output.append(f"{match.group('prefix')}{hashes} {exp_title}")
                continue

        clean_title = _strip_bold(title_raw).upper()
        output.append(f"{match.group('prefix')}**{clean_title}**")

    result = "\n".join(output)
    if md_text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def normalize_picture_text_fences_pdf(md_text: str) -> str:
    """Normalizza il formato e posizionamento dei fence Start/End of picture text.

    Sostituisce i fence pymupdf4llm **----- Start/End of picture text -----** con
    <!-- Start/End of picture text -->, rimuove i tag <br> sostituendoli con due ritorni
    a capo (\n\n), e garantisce che ogni fence sia su una riga dedicata all'inizio riga
    con una riga vuota prima e una riga vuota dopo.
    
    Args:
        md_text: Contenuto Markdown da normalizzare
    
    Returns:
        Contenuto Markdown con fence normalizzati
    """
    if not md_text:
        return md_text

    # Split <br> tags to separate lines BEFORE processing fences (DES-032)
    # This ensures fence markers end up on dedicated lines for regex matching
    # Replace <br> with \n\n (two newlines) as required by DES-032
    br_tag_re = re.compile(r"<br\s*/?>", re.IGNORECASE)
    preprocessed = br_tag_re.sub("\n\n", md_text)
    
    lines = preprocessed.splitlines()
    result: List[str] = []
    
    # Pattern per riconoscere i fence (no <br> in pattern since already split above)
    fence_start_re = re.compile(r"^\s*\*{0,2}\s*-{5,}\s*Start of picture text\s*-{5,}\s*\*{0,2}\s*$", re.IGNORECASE)
    fence_end_re = re.compile(r"^\s*\*{0,2}\s*-{5,}\s*End of picture text\s*-{5,}\s*\*{0,2}\s*$", re.IGNORECASE)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for Start fence
        if fence_start_re.match(line):
            # Add one empty line before if needed
            if result:
                while len(result) > 0 and result[-1].strip() == "":
                    result.pop()
                if result:
                    result.append("")
            
            # Add normalized fence
            result.append("<!-- Start of picture text -->")
            
            # Add one empty line after
            result.append("")
            
            i += 1
            # Skip any immediately following empty lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            # Process content between fences (br tags already replaced in preprocessing)
            while i < len(lines):
                content_line = lines[i]
                if fence_end_re.match(content_line):
                    # Process the End fence now
                    # Add one empty line before if needed
                    while len(result) > 0 and result[-1].strip() == "":
                        result.pop()
                    if result:
                        result.append("")
                    
                    # Add normalized fence
                    result.append("<!-- End of picture text -->")
                    
                    # Add one empty line after
                    result.append("")
                    
                    i += 1
                    # Skip any immediately following empty lines
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    break
                # Content line - append as-is (br tags already processed)
                result.append(content_line)
                i += 1
            
            continue
        
        # Check for End fence (should not happen if properly paired)
        if fence_end_re.match(line):
            # Add one empty line before if needed
            while len(result) > 0 and result[-1].strip() == "":
                result.pop()
            if result:
                result.append("")
            
            # Add normalized fence
            result.append("<!-- End of picture text -->")
            
            # Add one empty line after
            result.append("")
            
            i += 1
            # Skip any immediately following empty lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            continue
        
        # Regular line
        result.append(line)
        i += 1
    
    return "\n".join(result)


def run_processing_pipeline_pdf(
    *,
    args: argparse.Namespace,
    pdf_path: Path,
    out_dir: Path,
    post_processing_cfg: PostProcessingConfig,
    form_xobject_enabled: bool,
    vector_images_enabled: bool,
    keep_intermediate_files: bool,
) -> Tuple[str, str, List[Tuple[int, str]]]:
    """Esegue la pipeline PDF→Markdown scrivendo gli artefatti principali."""
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=False)

    images_dir, tables_dir, debug_dir = processing_prepare_output_dirs(out_dir, bool(args.debug))
    image_write_dir = _pymupdf4llm_safe_dir(images_dir)
    if image_write_dir != images_dir:
        image_write_dir.mkdir(parents=True, exist_ok=True)

    start_phase("Loading PDF and metadata")
    layout_enabled = processing_setup_layout(bool(args.verbose))
    pymupdf4llm = processing_import_pymupdf4llm()

    base = slugify_filename(pdf_path.stem)
    image_page_map: Dict[str, int] = {}

    LOG.info("Input:  %s", pdf_path)
    LOG.info("Images: %s", images_dir)
    LOG.info("Tables: %s", tables_dir)
    LOG.info("Layout mode: %s", "ON" if layout_enabled else "OFF (using legacy extraction)")

    doc_images, doc_text = processing_open_documents(pdf_path)

    (
        metadata,
        toc,
        toc_root,
        processed_page_count,
        page_offset,
        page_range_end,
        requested_limit,
        original_page_count,
        start_page,
    ) = processing_select_pages_and_toc(
        doc_images=doc_images,
        doc_text=doc_text,
        pdf_path=pdf_path,
        args=args,
    )

    ocr_ok = True
    if args.verbose and layout_enabled:
        LOG.info("OpenCV importable in the environment: YES")
    end_phase()

    chunks_images, chunks_text = processing_extract_chunks(
        doc_images=doc_images,
        doc_text=doc_text,
        images_dir=images_dir,
        image_write_dir=image_write_dir,
        args=args,
        layout_enabled=layout_enabled and ocr_ok,
        pymupdf4llm=pymupdf4llm,
    )

    page_count = processed_page_count
    final_md: Optional[str] = None
    debug_enabled = bool(args.debug)
    debug_report: Optional[Dict[str, Any]] = {"pages": []} if debug_enabled else None

    page_count = processed_page_count if processed_page_count > 0 else len(chunks_text)

    images_by_page: Dict[int, List[str]] = {}
    for i, page_dict in enumerate(chunks_images or []):
        page_no = i + 1
        actual_page_no = page_offset + page_no
        text_img = page_dict.get("text") or ""
        basenames_ordered = extract_image_basenames_in_order(text_img)
        rels = [f"images/{name}" for name in basenames_ordered]
        if rels:
            images_by_page[actual_page_no] = rels
            for name in basenames_ordered:
                image_page_map[name] = actual_page_no

    parts: List[str] = []
    parts.append(yaml_front_matter(metadata, pdf_path, page_count))
    # TOC insertion moved to post-processing phase (DES-058, REQ-036)

    start_phase("Processing pages")
    if args.verbose:
        if vector_images_enabled:
            LOG.info("Vector extraction enabled; vector regions will be rendered when detected.")
        else:
            LOG.info("vector extraction disabled (use --enable-vector-images to activate)")
        if form_xobject_enabled:
            LOG.info("Form XObject extraction enabled; placements will be rasterized when present.")
        else:
            LOG.info("Form XObject extraction disabled (use --enable-form-xobject to activate)")
    for i, page_dict in enumerate(chunks_text):
        page_no = i + 1
        actual_page_no = page_offset + page_no
        page = doc_text[i]
        if args.verbose:
            detail = f"Processing PDF page {actual_page_no}" if actual_page_no != page_no else "Processing page"
            _log_verbose_progress("Pages", page_no, page_count, detail=detail)

        page_label = f"Page {actual_page_no}"

        raw_text = page_dict.get("text") or ""
        text = PAGE_END_MARKER_RE.sub("", raw_text).strip()

        if text:
            text = rewrite_image_links_to_images_subdir(text, subdir="images")

        entry: Optional[Dict[str, Any]] = None
        if debug_enabled:
            entry = {"page": actual_page_no, "form_placements": [], "vector_regions": [], "insert_method": "none"}

        rel_image_paths = images_by_page.get(actual_page_no, [])
        if args.verbose and rel_image_paths:
            LOG.info("%s: inserting %d raster images from extraction", page_label, len(rel_image_paths))
        text, method = inject_images_into_page_markdown(text, rel_image_paths)
        if entry is not None:
            entry["insert_method"] = method

        if args.verbose and vector_images_enabled:
            LOG.info("%s: vector extraction enabled", page_label)
        if vector_images_enabled:
            regions = find_vector_regions(page, debug=args.debug)
            if regions:
                if args.verbose:
                    LOG.info("%s: rendering %d vector region(s)", page_label, len(regions))
                saved_vectors = render_vector_regions(
                    doc=doc_text,
                    doc_page_index=i,
                    regions=regions,
                    images_dir=images_dir,
                    pdf_filename_prefix=pdf_path.name,
                    pdf_page_no=actual_page_no,
                    dpi=200,
                )
                rels_vec = [f"images/{name}" for name in saved_vectors]
                if rels_vec:
                    if args.verbose:
                        LOG.info("%s: injected %d vector image(s) into Markdown", page_label, len(rels_vec))
                    text, method = inject_images_into_page_markdown(text, rels_vec)
                    if entry is not None:
                        if entry["insert_method"] == "none":
                            entry["insert_method"] = method
                        entry["vector_regions"] = [
                            [float(r.x0), float(r.y0), float(r.x1), float(r.y1)] for r in regions
                        ]
                    for name in saved_vectors:
                        image_page_map[name] = actual_page_no
                text = rewrite_image_links_to_images_subdir(text, subdir="images")
            elif args.verbose:
                LOG.info("%s: no vector regions detected", page_label)
        if form_xobject_enabled:
            page_uncropped = doc_images[i]
            placements = find_form_placements_on_page(doc_images, page_uncropped, actual_page_no, debug=args.debug)
            if placements:
                if args.verbose:
                    LOG.info("%s: rendering %d Form XObject image(s)", page_label, len(placements))
                saved = render_and_save_form_images(
                    page=page_uncropped,
                    placements=placements,
                    images_dir=images_dir,
                    pdf_filename_prefix=pdf_path.name,
                    page_no=actual_page_no,
                    dpi=150,
                )
                rels = [f"images/{fname}" for _, fname in saved]

                text, method = inject_images_into_page_markdown(text, rels)
                if entry is not None:
                    entry["insert_method"] = entry["insert_method"] if entry["insert_method"] != "none" else method
                    entry["form_placements"] = [
                        {"name": placement.name, "xref": placement.xref, "saved_as": f"images/{fname}"} for placement, fname in saved
                    ]

                text = rewrite_image_links_to_images_subdir(text, subdir="images")
                for _, fname in saved:
                    image_page_map[fname] = actual_page_no
            elif args.verbose:
                LOG.info("%s: no Form XObject placements found", page_label)
        elif entry is not None and entry["insert_method"] == "none":
            entry["insert_method"] = "disabled"

        if entry is not None and debug_report is not None:
            debug_report["pages"].append(entry)

        page_image_basenames = extract_image_basenames_from_markdown(text)
        for base_name in page_image_basenames:
            image_page_map.setdefault(base_name, actual_page_no)

        fallback_tables = extract_tables_fallback(doc_text, i)
        table_reference_blocks: List[str] = []
        if fallback_tables:
            exported = export_tables_files(tables_dir, actual_page_no, fallback_tables)
            if args.verbose:
                LOG.info("%s: exported %d fallback table(s)", page_label, len(exported))
            # Always generate table reference blocks (DES-032, REQ-019)
            table_reference_blocks = format_table_references(exported, out_dir)

        # If markdown table detected in text, remove it and insert only links with markers
        # Never keep inline content during processing (DES-032, REQ-019)
        if fallback_tables and looks_like_markdown_table(text):
            lines = text.splitlines()
            last_table_line = -1
            first_table_line = -1
            for idx, line in enumerate(lines):
                if "|" in line:
                    if first_table_line == -1:
                        first_table_line = idx
                    last_table_line = idx

            if first_table_line >= 0 and last_table_line >= 0:
                # Remove the inline table content
                del lines[first_table_line:last_table_line + 1]

                # Insert markers and links only
                if table_reference_blocks:
                    ref_block = table_reference_blocks[0] if table_reference_blocks else ""
                    if ref_block:
                        # Insert the complete ref_block (already contains markers and links)
                        ref_lines = ref_block.strip().split("\n")
                        for idx, ref_line in enumerate(ref_lines):
                            lines.insert(first_table_line + idx, ref_line)

                text = "\n".join(lines)

        parts.append(f"\n<!-- start of page.page_number={actual_page_no} -->\n")
        parts.append(text if text else "_[Pagina senza testo estratto]_")

        # If no markdown table in text, insert table reference blocks with markers
        # Never insert inline content during processing (DES-032, REQ-019)
        if fallback_tables and not looks_like_markdown_table(text):
            if table_reference_blocks:
                for ref_block in table_reference_blocks:
                    if ref_block:
                        parts.append("\n" + ref_block)
        elif not fallback_tables and args.verbose:
            LOG.info("%s: no fallback tables detected", page_label)

        parts.append(f"\n\n<!-- end of page.page_number={actual_page_no} -->\n")

    final_md = "\n".join(parts).strip() + "\n"
    end_phase()

    if final_md is None:
        try:
            doc_images.close()
        except Exception:
            pass
        try:
            doc_text.close()
        except Exception:
            pass
        raise RuntimeError("Unable to generate the final Markdown content.")

    referenced = extract_image_basenames_from_markdown(final_md)

    search_dirs = iter_search_dirs(pdf_path, out_dir, extra_dirs=[image_write_dir])
    probable = collect_probable_generated_images(pdf_path, fmt="png", search_dirs=search_dirs)

    all_to_move = referenced | probable
    if args.verbose:
        LOG.info(
            "Ensuring referenced/generated images are placed into %s (found: %d, probable: %d)",
            images_dir,
            len(referenced),
            len(probable),
        )
    moved = move_files_by_name(all_to_move, search_dirs=search_dirs, dest_dir=images_dir, verbose=bool(args.verbose))

    if args.verbose:
        LOG.info(
            "Referenced in Markdown: %d | probable generated: %d | moved to images/: %d",
            len(referenced),
            len(probable),
            moved,
        )

    # Normalize picture text fences before promoting bold to heading (DES-032)
    final_md = normalize_picture_text_fences_pdf(final_md)

    # Promote bold titles to headings before writing processing.md (DES-056, DES-005)
    # Returns filtered TOC excluding entries not found
    final_md, toc = promote_bold_to_heading_pdf(final_md, cast(List[HeadingEntry], toc))
    # Degrade headings not present in TOC (page-aware) before writing processing.md (DES-013)
    final_md = demote_headings_not_in_toc_pdf(final_md, toc)
    md_headings = generate_markdown_toc(final_md)

    start_phase("Writing artifacts")

    if keep_intermediate_files:
        processing_path = out_dir / "processing.md"
        safe_write_text(processing_path, final_md if final_md.endswith("\n") else f"{final_md}\n")
        if args.verbose:
            LOG.info("Intermediate file created: %s", processing_path)

    toc_content = build_document_toc_content(
        toc,
        page_start=start_page,
        page_end=page_range_end,
    )
    if args.verbose:
        LOG.info("Generated TOC content from PDF (%d entries in range)", len([e for e in toc if len(e) >= 2]))

    if args.debug and debug_report:
        if debug_dir is not None:
            safe_write_text(
                debug_dir / "form_xobjects.json",
                json.dumps(debug_report, ensure_ascii=False, indent=2, default=_json_default),
            )
            safe_write_text(
                debug_dir / f"{base}.chunks.json",
                json.dumps(chunks_text, ensure_ascii=False, indent=2, default=_json_default),
            )

    try:
        doc_images.close()
    except Exception:
        pass
    try:
        doc_text.close()
    except Exception:
        pass

    end_phase()

    return final_md, toc_content, md_headings


def _cleanup_intermediate_files(out_dir: Path, *, keep: bool, verbose: bool) -> None:
    """@brief Remove intermediate files when --keep-intermediate-files is disabled."""

    if keep:
        return
    # Only processing.md needs cleanup (tree.md is only created when keep=True)
    for filename in ("processing.md",):
        path = out_dir / filename
        if not path.exists():
            continue
        try:
            path.unlink()
            if verbose:
                LOG.info("Removed intermediate file: %s", path)
        except Exception as exc:
            LOG.warning("Unable to remove intermediate file %s: %s", path, exc)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point CLI che orchestra parsing argomenti, processing e post-processing."""

    ap = argparse.ArgumentParser(description="toMarkdown: convert PDF/HTML to Markdown with images/tables.")
    ap.add_argument("--mode", help="Processing mode: PDF or HTML")
    ap.add_argument("--from-file", help="Source PDF path")
    ap.add_argument("--from-dir", help="Source directory containing document.html, toc.html, assets/")
    ap.add_argument("--to-dir", help="Output directory")
    ap.add_argument("--verbose", action="store_true", help="Verbose progress logs")
    ap.add_argument("--debug", action="store_true", help="Debug logs + extra artifacts")
    ap.add_argument("--version", action="store_true", help="Print the program version and exit")
    ap.add_argument("--ver", action="store_true", help="Print the program version and exit")
    ap.add_argument("--upgrade", action="store_true", help="Upgrade the installed tomarkdown package and exit")
    ap.add_argument("--uninstall", action="store_true", help="Uninstall the tomarkdown package and exit")
    ap.add_argument("--header", type=float, default=0.0, help="Header margin in mm to ignore (PDF only)")
    ap.add_argument("--footer", type=float, default=0.0, help="Footer margin in mm to ignore (PDF only)")
    ap.add_argument("--start-page", type=int, default=1, help="Page number to start processing from (PDF only)")
    ap.add_argument("--n-pages", type=int, help="Maximum number of pages to process (PDF only)")
    ap.add_argument(
        "--enable-form-xobject",
        action="store_true",
        help="Enable Form XObject rasterization as images (PDF only)",
    )
    ap.add_argument(
        "--enable-vector-images",
        action="store_true",
        help="Enable vector diagram extraction (PDF only)",
    )
    ap.add_argument("--enable-pictex", action="store_true", help="Enable Pix2Tex equation recognition and LaTeX insertion")
    ap.add_argument(
        "--disable-remove-small-images",
        action="store_true",
        help="Disable remove-small-images post-processing phase",
    )
    ap.add_argument(
        "--disable-cleanup",
        action="store_true",
        help="Disable cleanup of page markers before final Markdown save",
    )
    ap.add_argument("--add-toc", action="store_true", help="Add TOC to document.md")
    ap.add_argument("--enable-inline-tables", action="store_true", help="Enable inline markdown table insertion")
    ap.add_argument("--enable-gemini", action="store_true", help="Enable Gemini annotation")
    ap.add_argument("--equation-min-len", type=int, default=5, help="Minimum Pix2Tex length")
    ap.add_argument("--min-size-x", type=int, default=100, help="Minimum width for remove-small-images")
    ap.add_argument("--min-size-y", type=int, default=100, help="Minimum height for remove-small-images")
    ap.add_argument(
        "--enable-gemini-over-pixtex",
        action="store_true",
        help="Force Gemini to annotate all images even when Pix2Tex is active",
    )
    ap.add_argument("--gemini-api-key", help="Gemini API key (fallback: GEMINI_API_KEY env var)")
    ap.add_argument("--gemini-model", default=GEMINI_DEFAULT_MODEL, help="Gemini model name")
    ap.add_argument("--gemini-api-emulation", action="store_true", help="Emulate Gemini API calls without network access")
    ap.add_argument("--prompts", help="Path to prompts JSON (equation/non-equation/uncertain)")
    ap.add_argument("--write-prompts", help="Write default prompts JSON to the given path and exit")
    ap.add_argument(
        "--keep-intermediate-files",
        action="store_true",
        help="Keep processing.md and tree.md after conversion",
    )

    args = ap.parse_args(argv)

    if args.version or args.ver:
        maybe_print_new_version_notice(program_name="tomarkdown")
        print(program_version())
        return 0
    if args.upgrade:
        maybe_print_new_version_notice(program_name="tomarkdown")
        return run_self_upgrade(package_name="tomarkdown")
    if args.uninstall:
        maybe_print_new_version_notice(program_name="tomarkdown")
        return run_self_uninstall(package_name="tomarkdown")

    setup_logging(args.verbose, args.debug)

    if args.write_prompts:
        target = Path(args.write_prompts).expanduser().resolve()
        try:
            _write_prompts_file(target)
        except Exception as exc:
            LOG.error("Unable to write prompts file %s: %s", target, exc)
            return EXIT_INVALID_ARGS
        LOG.info("Default prompts written to %s", target)
        return 0

    mode = (args.mode or "").strip().upper()
    if mode not in {"PDF", "HTML"}:
        ap.print_help()
        LOG.error("Option --mode is required and must be PDF or HTML")
        return EXIT_INVALID_ARGS

    if args.equation_min_len is None or args.equation_min_len <= 0:
        LOG.error("Invalid value for --equation-min-len: must be > 0")
        return EXIT_INVALID_ARGS
    if args.min_size_x is None or args.min_size_x <= 0:
        LOG.error("Invalid value for --min-size-x: must be > 0")
        return EXIT_INVALID_ARGS
    if args.min_size_y is None or args.min_size_y <= 0:
        LOG.error("Invalid value for --min-size-y: must be > 0")
        return EXIT_INVALID_ARGS

    if mode == "PDF":
        if args.header is not None and args.header < 0:
            LOG.error("Invalid value for --header: must be >= 0")
            return EXIT_INVALID_ARGS
        if args.footer is not None and args.footer < 0:
            LOG.error("Invalid value for --footer: must be >= 0")
            return EXIT_INVALID_ARGS
        if args.start_page is None or args.start_page <= 0:
            LOG.error("Invalid value for --start-page: must be > 0")
            return EXIT_INVALID_ARGS
        if args.n_pages is not None and args.n_pages <= 0:
            LOG.error("Invalid value for --n-pages: must be > 0")
            return EXIT_INVALID_ARGS

    # Pix2Tex enabled only if --enable-pictex is passed
    enable_pictex = bool(getattr(args, "enable_pictex", False))

    # Gemini API emulation
    gemini_api_emulation = bool(getattr(args, "gemini_api_emulation", False))

    form_xobject_enabled = bool(args.enable_form_xobject)
    vector_images_enabled = bool(args.enable_vector_images)

    prompts_cfg = dict(DEFAULT_PROMPTS)
    if args.prompts:
        prompts_path = Path(args.prompts).expanduser().resolve()
        if not prompts_path.exists() or not prompts_path.is_file():
            LOG.error("Prompts file not found: %s", prompts_path)
            return EXIT_INVALID_ARGS
        try:
            prompts_cfg = load_prompts_file(prompts_path)
        except ValueError as exc:
            LOG.error("%s", exc)
            return EXIT_INVALID_ARGS

    gemini_api_key = args.gemini_api_key or os.environ.get("GEMINI_API_KEY")
    gemini_module = (
        os.environ.get("TOMARKDOWN_GEMINI_MODULE")
        or os.environ.get("PDF2TREE_GEMINI_MODULE")
        or os.environ.get("HTML2TREE_GEMINI_MODULE")
        or "google.genai"
    )

    # Gemini enabled only if --enable-gemini AND (--gemini-api-key OR --gemini-api-emulation)
    enable_gemini_requested = bool(getattr(args, "enable_gemini", False))
    enable_gemini = enable_gemini_requested and (bool(gemini_api_key) or gemini_api_emulation)

    # Warning if Gemini requested but no key/emulation
    if enable_gemini_requested and not gemini_api_key and not gemini_api_emulation:
        LOG.warning("Gemini annotation requested but no API key or emulation mode provided. Disabling Gemini.")
        enable_gemini = False

    # New flag: enable_gemini_over_pixtex
    enable_gemini_over_pixtex = bool(getattr(args, "enable_gemini_over_pixtex", False))

    force_toc_validation = _env_flag_enabled(
        os.environ.get("TOMARKDOWN_FORCE_TOC_VALIDATION") or os.environ.get("PDF2TREE_FORCE_TOC_VALIDATION")
    )

    if mode == "PDF":
        skip_toc_validation = bool(
            is_test_mode()
            and (args.n_pages is not None or (args.start_page is not None and args.start_page != 1))
            and not force_toc_validation
        )
    else:
        skip_toc_validation = bool(is_test_mode())

    post_processing_cfg = PostProcessingConfig(
        equation_min_len=int(args.equation_min_len),
        verbose=bool(args.verbose),
        debug=bool(args.debug),
        gemini_api_key=gemini_api_key,
        gemini_model=str(args.gemini_model or GEMINI_DEFAULT_MODEL),
        gemini_module=str(gemini_module or "google.genai"),
        gemini_api_emulation=gemini_api_emulation,
        test_mode=is_test_mode(),
        disable_remove_small_images=bool(args.disable_remove_small_images),
        disable_cleanup=bool(args.disable_cleanup),
        add_toc=bool(getattr(args, "add_toc", False)),
        enable_inline_tables=bool(getattr(args, "enable_inline_tables", False)),
        enable_pictex=enable_pictex,
        enable_gemini=enable_gemini,
        enable_gemini_over_pixtex=enable_gemini_over_pixtex,
        min_size_x=int(args.min_size_x),
        min_size_y=int(args.min_size_y),
        prompt_equation=prompts_cfg["prompt_equation"],
        prompt_non_equation=prompts_cfg["prompt_non_equation"],
        prompt_uncertain=prompts_cfg["prompt_uncertain"],
        skip_toc_validation=skip_toc_validation,
    )

    if not args.to_dir:
        ap.print_help()
        LOG.error("--to-dir is required for conversion")
        return EXIT_INVALID_ARGS

    out_dir = Path(args.to_dir).expanduser().resolve()
    if out_dir.exists():
        if not out_dir.is_dir():
            LOG.error("Output path is not a directory: %s", out_dir)
            return EXIT_OUTPUT_DIR
        if any(out_dir.iterdir()):
            LOG.error("Output directory must be empty: %s", out_dir)
            return EXIT_OUTPUT_DIR

    maybe_print_new_version_notice(program_name="tomarkdown")

    if mode == "PDF":
        pdf_path: Optional[Path] = Path(args.from_file).expanduser().resolve() if args.from_file else None
        if pdf_path is None or not pdf_path.exists() or not pdf_path.is_file():
            LOG.error("Source file not found: %s", pdf_path)
            return EXIT_INVALID_ARGS

        if not has_opencv():
            LOG.error("OpenCV (cv2) not installed or not importable: install opencv-python in the environment")
            return EXIT_OPENCV_MISSING

        print_program_banner()
        print_parameter_summary(
            args=args,
            post_config=post_processing_cfg,
            mode=mode,
            source_path=pdf_path,
            from_dir=None,
            out_dir=out_dir,
            form_xobject_enabled=form_xobject_enabled,
            vector_images_enabled=vector_images_enabled,
        )

        pdf_path_required: Path = cast(Path, pdf_path)
        try:
            processing_md_content, toc_content, md_headings = run_processing_pipeline_pdf(
                args=args,
                pdf_path=pdf_path_required,
                out_dir=out_dir,
                post_processing_cfg=post_processing_cfg,
                form_xobject_enabled=form_xobject_enabled,
                vector_images_enabled=vector_images_enabled,
                keep_intermediate_files=bool(args.keep_intermediate_files),
            )
        except RuntimeError as exc:
            msg = str(exc)
            LOG.error("%s", msg)
            if "TOC not found" in msg:
                return 4
            if "Start page" in msg or "Requested page range" in msg:
                return EXIT_INVALID_ARGS
            if "Unable to import pymupdf4llm" in msg:
                return 3
            return 5

        start_phase("Post-processing")
        try:
            updated_md, toc_mismatch = run_post_processing_pipeline(
                out_dir=out_dir,
                md_content=processing_md_content,
                md_headings=md_headings,
                toc_content=toc_content,
                config=post_processing_cfg,
            )
        except RuntimeError as exc:
            LOG.error("Post-processing failed: %s", exc)
            return EXIT_POSTPROC_DEP

        md_out = out_dir / "document.md"
        safe_write_text(md_out, updated_md if updated_md.endswith("\n") else f"{updated_md}\n")
        end_phase()
        LOG.info("Created: %s", md_out)

        if args.keep_intermediate_files:
            tree_md_path = out_dir / "tree.md"
            safe_write_text(tree_md_path, toc_content if toc_content else "")
            if args.verbose:
                LOG.info("Created tree.md (--keep-intermediate-files): %s", tree_md_path)

        _cleanup_intermediate_files(
            out_dir,
            keep=bool(args.keep_intermediate_files),
            verbose=bool(args.verbose),
        )
        return EXIT_POSTPROC_DEP if toc_mismatch else 0

    # HTML mode
    if not args.from_dir:
        ap.print_help()
        LOG.error("--from-dir is required for HTML mode")
        return EXIT_INVALID_ARGS

    from_dir = Path(args.from_dir).expanduser().resolve()
    if not from_dir.exists() or not from_dir.is_dir():
        LOG.error("Source directory not found: %s", from_dir)
        return EXIT_INVALID_ARGS

    document_path = from_dir / "document.html"
    if not document_path.exists():
        LOG.error("document.html not found in %s", from_dir)
        return EXIT_INVALID_ARGS
    if not (from_dir / "toc.html").exists():
        LOG.error("toc.html not found in %s", from_dir)
        return EXIT_INVALID_ARGS

    print_program_banner()
    print_parameter_summary(
        args=args,
        post_config=post_processing_cfg,
        mode=mode,
        source_path=document_path if document_path.exists() else None,
        from_dir=from_dir,
        out_dir=out_dir,
    )

    try:
        processing_md_content, toc_content, md_headings = run_processing_pipeline_html(
            from_dir=from_dir,
            out_dir=out_dir,
            post_processing_cfg=post_processing_cfg,
            keep_intermediate_files=bool(args.keep_intermediate_files),
        )
    except RuntimeError as exc:
        LOG.error("%s", exc)
        return EXIT_INVALID_ARGS

    start_phase("Post-processing")
    try:
        updated_md, toc_mismatch = run_post_processing_pipeline(
            out_dir=out_dir,
            md_content=processing_md_content,
            md_headings=md_headings,
            toc_content=toc_content,
            config=post_processing_cfg,
        )
    except RuntimeError as exc:
        LOG.error("Post-processing failed: %s", exc)
        return EXIT_POSTPROC_DEP

    md_out = out_dir / "document.md"
    safe_write_text(md_out, updated_md if updated_md.endswith("\n") else f"{updated_md}\n")
    end_phase()
    LOG.info("Created: %s", md_out)

    if args.keep_intermediate_files and toc_content:
        tree_md_path = out_dir / "tree.md"
        safe_write_text(tree_md_path, toc_content)
        if args.verbose:
            LOG.info("Created tree.md (--keep-intermediate-files): %s", tree_md_path)

    _cleanup_intermediate_files(
        out_dir,
        keep=bool(args.keep_intermediate_files),
        verbose=bool(args.verbose),
    )
    return EXIT_POSTPROC_DEP if toc_mismatch else 0


if __name__ == "__main__":
    raise SystemExit(main())
