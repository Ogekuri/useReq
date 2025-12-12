#!/usr/bin/env python3
"""
Converti un Markdown in TOML (md2toml)

Questo script è una versione rinominata di md3toml; estrae il campo
`description:` dal blocco iniziale delimitato da "---" e genera un file
TOML con `description` e `prompt`.
"""

import argparse
import os
import re
import sys


def error(msg: str, code: int = 1) -> None:
    # Stampa un messaggio di errore su stderr e termina con codice di uscita
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> None:
    parser = argparse.ArgumentParser(description="Converti MD in TOML (md2toml)")
    parser.add_argument("--md", required=True, help="file Markdown sorgente (deve esistere)")
    parser.add_argument("--toml", required=True, help="file TOML di destinazione")
    parser.add_argument("--force", action="store_true", help="sovrascrivi la destinazione se esiste")

    args = parser.parse_args()

    md_path = args.md
    toml_path = args.toml

    # Verifica che il file Markdown sorgente esista
    if not os.path.isfile(md_path):
        error(f"Markdown file does not exist: {md_path}", 2)

    if os.path.exists(toml_path) and not args.force:
        error(f"Destination TOML already exists (use --force to overwrite): {toml_path}", 3)

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Cerca il blocco iniziale delimitato da '---' all'inizio del file
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n(.*)$", content, re.S)
    if not m:
        error("No leading '---' block found at start of Markdown file.", 4)

    block = m.group(1)
    rest = m.group(2)

    # Estrai il valore di `description:` dal blocco
    desc_m = re.search(r"^description:\s*(.*)$", block, re.M)
    if not desc_m:
        error("No 'description:' field found inside the leading block.", 5)

    desc = desc_m.group(1).strip()

    # Prepara il contenuto rimanente: non effettuare sostituzioni su $ARGUMENTS
    # (la sostituzione di %%ARGS%% viene gestita dallo script Req)
    rest_text = rest

    # Escape della descrizione per essere inserita in una stringa TOML tra doppie virgolette
    desc_escaped = desc.replace("\\", "\\\\").replace('"', '\\"')

    toml_body = []
    toml_body.append(f'description = "{desc_escaped}"')
    toml_body.append("")
    toml_body.append('prompt = """')
    toml_body.append(rest_text)
    # Assicura che ci sia una newline finale prima di chiudere le triple virgolette
    if not rest_text.endswith("\n"):
        toml_body.append("")
    toml_body.append('"""\n')

    # Scrivi il file di output
    os.makedirs(os.path.dirname(toml_path) or ".", exist_ok=True)
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(toml_body))

    print(f"Wrote TOML to: {toml_path}")


if __name__ == "__main__":
    main()
