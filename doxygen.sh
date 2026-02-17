#!/usr/bin/env bash

###############################################################################
## @file doxygen.sh
## @brief Generate Doxygen documentation for project sources under src/.
## @details Resolves repository root from script location, generates a temporary
##          Doxygen configuration, builds HTML/PDF/Markdown outputs in
##          doxygen/{html,pdf,markdown}, and fails on missing required tooling.
###############################################################################

set -euo pipefail

###############################################################################
## @brief Resolve project-level paths from script location.
## @details Initializes immutable path variables used by all execution phases.
###############################################################################
SCRIPT_PATH="$(readlink -f "$0")"
PROJECT_ROOT="$(dirname "$SCRIPT_PATH")"
SRC_DIR="$PROJECT_ROOT/src"
DOXYGEN_DIR="$PROJECT_ROOT/doxygen"
HTML_DIR="$DOXYGEN_DIR/html"
MARKDOWN_DIR="$DOXYGEN_DIR/markdown"
PDF_DIR="$DOXYGEN_DIR/pdf"
LATEX_DIR="$DOXYGEN_DIR/latex"
XML_DIR="$DOXYGEN_DIR/xml"
DOXYFILE_TMP="$(mktemp /tmp/doxygen.useReq.XXXXXX.conf)"
SUPPORTS_GENERATE_MARKDOWN=0

###############################################################################
## @brief Validate required binaries and source directory.
## @throws Exits with code 1 when a required dependency or path is missing.
###############################################################################
check_prerequisites() {
  if ! command -v doxygen >/dev/null 2>&1; then
    printf '%s\n' "ERROR: 'doxygen' not found in system PATH." >&2
    exit 1
  fi

  if ! [ -d "$SRC_DIR" ]; then
    printf '%s\n' "ERROR: Source directory not found: $SRC_DIR" >&2
    exit 1
  fi

  if doxygen -x 2>/dev/null | grep -q '^GENERATE_MARKDOWN'; then
    SUPPORTS_GENERATE_MARKDOWN=1
  fi
}

###############################################################################
## @brief Reset output directories before generation.
## @details Deletes previous HTML, PDF, Markdown, LaTeX, and XML outputs.
###############################################################################
prepare_output_dirs() {
  rm -rf "$HTML_DIR" "$MARKDOWN_DIR" "$PDF_DIR" "$LATEX_DIR" "$XML_DIR"
  mkdir -p "$DOXYGEN_DIR" "$PDF_DIR"
}

###############################################################################
## @brief Create temporary Doxygen configuration file.
## @details Writes best-practice options for recursive source analysis and full
##          extraction; enables native markdown output when supported.
###############################################################################
write_doxyfile() {
  cat > "$DOXYFILE_TMP" <<DOXYGEN_CFG
PROJECT_NAME           = "useReq"
OUTPUT_DIRECTORY       = "$DOXYGEN_DIR"
INPUT                  = "$SRC_DIR"
FILE_PATTERNS          = *.py *.sh *.js *.ts *.go *.java *.c *.cpp *.h *.hpp *.rb *.php *.rs *.swift *.kt *.scala *.lua *.r *.m *.mm *.cs
RECURSIVE              = YES
EXTRACT_ALL            = YES
EXTRACT_PRIVATE        = YES
EXTRACT_STATIC         = YES
EXTRACT_LOCAL_CLASSES  = YES
EXTRACT_ANON_NSPACES   = YES
JAVADOC_AUTOBRIEF      = YES
MULTILINE_CPP_IS_BRIEF = YES
SORT_MEMBER_DOCS       = YES
SORT_BRIEF_DOCS        = YES
FULL_PATH_NAMES        = NO
STRIP_FROM_PATH        = "$PROJECT_ROOT"
WARN_IF_UNDOCUMENTED   = NO
WARN_IF_DOC_ERROR      = YES
WARN_NO_PARAMDOC       = NO
QUIET                  = YES
GENERATE_HTML          = YES
HTML_OUTPUT            = html
GENERATE_LATEX         = YES
LATEX_OUTPUT           = latex
USE_PDFLATEX           = YES
GENERATE_XML           = YES
XML_OUTPUT             = xml
MARKDOWN_ID_STYLE      = GITHUB
TOC_INCLUDE_HEADINGS   = 3
DOXYGEN_CFG

  if [ "$SUPPORTS_GENERATE_MARKDOWN" -eq 1 ]; then
    {
      printf '%s\n' 'GENERATE_MARKDOWN      = YES'
      printf '%s\n' 'MARKDOWN_OUTPUT        = markdown'
    } >> "$DOXYFILE_TMP"
  fi
}

###############################################################################
## @brief Build markdown index from Doxygen XML when native markdown is absent.
## @details Converts index.xml compound metadata into deterministic markdown list
##          to satisfy markdown output contract on older Doxygen versions.
###############################################################################
generate_markdown_fallback() {
  mkdir -p "$MARKDOWN_DIR"
  PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}" python3 - "$XML_DIR/index.xml" "$MARKDOWN_DIR/index.md" <<'PYCODE'
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

xml_index = Path(sys.argv[1])
markdown_index = Path(sys.argv[2])
root = ET.parse(xml_index).getroot()
entries = []
for compound in root.findall("compound"):
    name = (compound.findtext("name") or "").strip()
    kind = (compound.get("kind") or "").strip()
    refid = (compound.get("refid") or "").strip()
    if name:
        entries.append((kind, name, refid))

entries.sort(key=lambda item: (item[0], item[1]))
lines = [
    "# Doxygen Markdown Index",
    "",
    "Generated from Doxygen XML output.",
    "",
]
for kind, name, refid in entries:
    lines.append(f"- `{kind}` `{name}` (`{refid}`)")

markdown_index.write_text("\n".join(lines) + "\n", encoding="utf-8")
PYCODE
}

###############################################################################
## @brief Compile LaTeX output and publish PDF artifact.
## @throws Exits with code 1 when Makefile, make, pdflatex, or refman.pdf is missing.
###############################################################################
build_pdf_output() {
  if ! [ -f "$LATEX_DIR/Makefile" ]; then
    printf '%s\n' "ERROR: Missing LaTeX Makefile in $LATEX_DIR" >&2
    exit 1
  fi

  if ! command -v make >/dev/null 2>&1; then
    printf '%s\n' "ERROR: 'make' not found in system PATH; cannot build PDF." >&2
    exit 1
  fi

  if ! command -v pdflatex >/dev/null 2>&1; then
    printf '%s\n' "ERROR: 'pdflatex' not found in system PATH; cannot build PDF." >&2
    exit 1
  fi

  make -C "$LATEX_DIR" >/dev/null

  if ! [ -f "$LATEX_DIR/refman.pdf" ]; then
    printf '%s\n' "ERROR: PDF artifact not generated: $LATEX_DIR/refman.pdf" >&2
    exit 1
  fi

  cp "$LATEX_DIR/refman.pdf" "$PDF_DIR/refman.pdf"
}

###############################################################################
## @brief Main entrypoint for documentation generation.
## @details Executes prerequisites, config generation, Doxygen run, markdown
##          fallback handling, PDF compilation, and final path summary.
###############################################################################
main() {
  trap 'rm -f "$DOXYFILE_TMP"' EXIT

  check_prerequisites
  prepare_output_dirs
  write_doxyfile
  doxygen "$DOXYFILE_TMP"

  if [ "$SUPPORTS_GENERATE_MARKDOWN" -ne 1 ]; then
    generate_markdown_fallback
  fi

  build_pdf_output

  printf '%s\n' "Generated: $HTML_DIR"
  printf '%s\n' "Generated: $MARKDOWN_DIR"
  printf '%s\n' "Generated: $PDF_DIR/refman.pdf"
}

main "$@"
