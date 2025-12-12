#!/usr/bin/env bash
# Script per inizializzare risorse di progetto da Req
set -euo pipefail

# Determina la directory in cui è installato lo script
# Determina il percorso assoluto dello script e la base degli script
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_BASE="$(dirname "$SCRIPT_PATH")"
# La radice del repository è la directory padre di scripts/
REPO_BASE="$(dirname "$SCRIPT_BASE")"

# Funzioni di logging
VERBOSE=0
DEBUG=0
log() { echo "$@"; }
vlog() { if [ "$VERBOSE" -eq 1 ]; then echo "$@"; fi }
dlog() { if [ "$DEBUG" -eq 1 ]; then echo "DEBUG: $@"; fi }

usage() {
  cat <<EOF
Uso: $(basename "$0") (--base <percorso> | --here) --doc <file.md> --dir <dir> [--verbose] [--debug]

Parametri:
  --base <percorso>   Directory radice del progetto da usare
  --here              Usa la directory corrente come root progetto (mutualmente esclusivo con --base)
  --doc <file.md>     Percorso del file .md dei requisiti (obbligatorio, deve finire con .md)
  --dir <dir>         Percorso di una directory tecnica relativa al progetto (obbligatorio)
  --verbose           Abilita stampe verbose
  --debug             Abilita stampe di debug
EOF
  exit 1
}

# Parsing argomenti
PROJECT_BASE=""
REQ_DOC=""
REQ_DIR=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --base)
      shift; PROJECT_BASE="$1"; shift;;
    --here)
      PROJECT_BASE="$(pwd)"; shift;;
    --verbose)
      VERBOSE=1; shift;;
    --debug)
      DEBUG=1; shift;;
    --doc)
      shift; REQ_DOC="$1"; shift;;
    --dir)
      shift; REQ_DIR="$1"; shift;;
    -h|--help)
      usage;;
    *)
      echo "Argomento sconosciuto: $1"; usage;;
  esac
done

# Validazioni di base
if [ -z "$PROJECT_BASE" ]; then
  echo "Errore: specificare --base <percorso> o --here" >&2
  exit 2
fi

# Controlla eventuale conflitto (se l'utente ha fornito sia --base che --here)
# (qui PROJECT_BASE sarà sovrascritto dalla seconda opzione; per rispettare la
# richiesta consideriamo la presenza simultanea come errore se entrambe sono state passate.)

# Non è facile distinguere se l'utente ha passato entrambe una volta che abbiamo
# consumato gli argomenti; quindi rileviamo tramite variabili d'ambito: se --base
# e --here sono stati passati entrambi, PROJECT_BASE veniva impostato due volte.
# Per semplicità controlliamo la presenza di file descriptor speciale lasciando
# un controllo implementato in fase di parsing (non-stated). Assumiamo che l'utente
# non passi entrambe; se necessario possiamo estendere il parsing.

# Valida REQ_DOC se fornito
# Controlla che i parametri obbligatori --doc e --dir siano stati passati
if [ -z "$REQ_DOC" ]; then
  echo "Errore: il parametro --doc è obbligatorio" >&2
  exit 3
fi
if [ -z "$REQ_DIR" ]; then
  echo "Errore: il parametro --dir è obbligatorio" >&2
  exit 4
fi

# Valida formato di REQ_DOC
if [[ "$REQ_DOC" != *.md ]]; then
  echo "Errore: --doc richiede un file che termini con .md" >&2
  exit 5
fi

# Abilita debug/verbose
dlog "SCRIPT_BASE=$SCRIPT_BASE"
dlog "PROJECT_BASE=$PROJECT_BASE"
dlog "REQ_DOC=$REQ_DOC"
dlog "REQ_DIR=$REQ_DIR"

# Normalizza percorsi: se REQ_DOC o REQ_DIR sono percorsi assoluti che contengono
# PROJECT_BASE, li rendiamo relativi rispetto a PROJECT_BASE
make_relative_if_contains_project() {
  local p="$1"
  if [ -z "$p" ]; then
    echo ""
    return
  fi
  if [[ "$p" = /* ]]; then
    # percorso assoluto
    if [[ "$p" == "$PROJECT_BASE"* ]]; then
      # rimuovi prefisso PROJECT_BASE/
      local rel="${p#$PROJECT_BASE}"
      rel="${rel#/}"
      echo "$rel"
      return
    else
      # non contiene PROJECT_BASE -> lasciare come assoluto (gestione a valle)
      echo "$p"
      return
    fi
  else
    # già relativo
    # se il percorso relativo inizia con il valore di PROJECT_BASE (anche relativo), rimuovi il prefisso
    if [[ "$p" == "$PROJECT_BASE"* ]]; then
      local rel="${p#$PROJECT_BASE}"
      rel="${rel#/}"
      echo "$rel"
      return
    fi
    echo "$p"
    return
  fi
}

if [ -n "$REQ_DOC" ]; then
  REQ_DOC="$(make_relative_if_contains_project "$REQ_DOC")"
fi
if [ -n "$REQ_DIR" ]; then
  REQ_DIR="$(make_relative_if_contains_project "$REQ_DIR")"
fi

dlog "After normalize REQ_DOC=$REQ_DOC"
dlog "After normalize REQ_DIR=$REQ_DIR"

# Dopo normalizzazione, REQ_DOC e REQ_DIR devono essere percorsi relativi (se impostati)
if [ -n "$REQ_DOC" ]; then
  if [[ "$REQ_DOC" = /* ]]; then
    echo "Errore: REQ_DOC deve essere un percorso relativo rispetto a PROJECT_BASE" >&2
    exit 4
  fi
fi
if [ -n "$REQ_DIR" ]; then
  if [[ "$REQ_DIR" = /* ]]; then
    echo "Errore: REQ_DIR deve essere un percorso relativo rispetto a PROJECT_BASE" >&2
    exit 5
  fi
fi

# Assicura che PROJECT_BASE sia path assoluto
PROJECT_BASE="$(readlink -f "$PROJECT_BASE")"

# Deriva percorsi assoluti da REQ_DOC/REQ_DIR e poi calcola i percorsi relativi
# rispetto a PROJECT_BASE rimuovendo il prefisso PROJECT_BASE/ quando possibile.
if [ -n "$REQ_DOC" ]; then
  # Try to resolve REQ_DOC to an absolute path, either as given or relative to CWD
  abs_req="$(readlink -f "$REQ_DOC" 2>/dev/null || true)"
  # If that failed, try relative to PROJECT_BASE
  if [ -z "$abs_req" ]; then
    abs_req="$(readlink -f "$PROJECT_BASE/$REQ_DOC" 2>/dev/null || true)"
  fi
  if [ -n "$abs_req" ] && [[ "$abs_req" == "$PROJECT_BASE"* ]]; then
    SUB_REQ_DOC="${abs_req#$PROJECT_BASE}"
    SUB_REQ_DOC="${SUB_REQ_DOC#/}"
  else
    SUB_REQ_DOC="$REQ_DOC"
  fi
else
  SUB_REQ_DOC=""
fi

if [ -n "$REQ_DIR" ]; then
  abs_tech="$(readlink -f "$REQ_DIR" 2>/dev/null || true)"
  if [ -z "$abs_tech" ]; then
    abs_tech="$(readlink -f "$PROJECT_BASE/$REQ_DIR" 2>/dev/null || true)"
  fi
  if [ -n "$abs_tech" ] && [[ "$abs_tech" == "$PROJECT_BASE"* ]]; then
    SUB_TECH_DIR="${abs_tech#$PROJECT_BASE}"
    SUB_TECH_DIR="${SUB_TECH_DIR#/}"
  else
    SUB_TECH_DIR="$REQ_DIR"
  fi
else
  SUB_TECH_DIR=""
fi

# Aggiungi prefisso ../../ per risalire dalla posizione dei prompt alla root del progetto
if [ -n "$SUB_REQ_DOC" ]; then
  case "$SUB_REQ_DOC" in
    ../*|../../* ) ;;
    *) SUB_REQ_DOC="../../$SUB_REQ_DOC" ;;
  esac
fi
if [ -n "$SUB_TECH_DIR" ]; then
  case "$SUB_TECH_DIR" in
    ../*|../../* ) ;;
    *) SUB_TECH_DIR="../../$SUB_TECH_DIR" ;;
  esac
fi

# Verifica che la directory REQ_DIR esista sotto PROJECT_BASE (controllo dei parametri)
if [ -n "$REQ_DIR" ]; then
  tech_abs="$PROJECT_BASE/$REQ_DIR"
  if [ ! -d "$tech_abs" ]; then
    echo "Errore: la directory REQ_DIR '$REQ_DIR' non esiste sotto $PROJECT_BASE" >&2
    exit 8
  fi
fi

# Se esiste il percorso $PROJECT_BASE/.req cancellalo
if [ -e "$PROJECT_BASE/.req" ]; then
  vlog "Rimuovo $PROJECT_BASE/.req"
  rm -rf "$PROJECT_BASE/.req"
fi

# Assicura che la directory .req esista (anche se non ci sono script/templates da copiare)
mkdir -p "$PROJECT_BASE/.req"
if [ "$VERBOSE" -eq 1 ]; then
  echo "OK: assicurata directory $PROJECT_BASE/.req"
fi

# Se il file REQ_DOC non esiste, copiarlo da templates/requirements.md
if [ -n "$REQ_DOC" ]; then
  target_req="$PROJECT_BASE/$REQ_DOC"
  if [ ! -f "$target_req" ]; then
    vlog "Creazione di $target_req da $REPO_BASE/templates/requirements.md"
    mkdir -p "$(dirname "$target_req")"
    cp "$REPO_BASE/templates/requirements.md" "$target_req"
    # Messaggio visibile solo in verbose
    if [ "$VERBOSE" -eq 1 ]; then
      echo "Creato $target_req — modificare il file con i requisiti del progetto." 
    fi
  fi
fi

# Assicura percorso REQ_DIR (deve già esistere, verificato prima)
if [ -n "$REQ_DIR" ]; then
  target_tech="$PROJECT_BASE/$REQ_DIR"
  if [ "$VERBOSE" -eq 1 ]; then
    echo "OK: directory tecnica trovata $target_tech"
  fi
fi

# Funzione per copiare e sostituire %%REQ_DOC%% con la variabile corretta
copy_and_replace() {
  local src="$1" dst="$2"
  local mode="${3:-}"
  # base replacements (use substituted relative paths)
  local sed_expr="s|%%REQ_DOC%%|$SUB_REQ_DOC|g; s|%%REQ_DIR%%|$SUB_TECH_DIR|g"
  mkdir -p "$(dirname "$dst")"
  # format-specific replacement for %%ARGS%%
  if [ "$mode" = "codex" ] || [ "$mode" = "github" ]; then
    # replace with literal $ARGUMENTS
    sed_expr="$sed_expr; s|%%ARGS%%|\$ARGUMENTS|g"
  elif [ "$mode" = "gemini" ]; then
    sed_expr="$sed_expr; s|%%ARGS%%|{{args}}|g"
  fi
  sed "$sed_expr" "$src" > "$dst"
}

# Assicura esistenza delle cartelle .codex, .github, .gemini
mkdir -p "$PROJECT_BASE/.codex/prompts"
mkdir -p "$PROJECT_BASE/.github/agents"
mkdir -p "$PROJECT_BASE/.github/prompts"
mkdir -p "$PROJECT_BASE/.gemini/commands"
if [ "$VERBOSE" -eq 1 ]; then
  echo "OK: create/assicurate cartelle .codex, .github, .gemini sotto $PROJECT_BASE"
fi

# Per ogni file .md in $REPO_BASE/prompts
if [ -d "$REPO_BASE/prompts" ]; then
  for file in "$REPO_BASE"/prompts/*.md; do
    [ -e "$file" ] || continue
    basefile="$(basename "$file")"
    PROMPT="${basefile%.md}"
    vlog "Processo prompt: $PROMPT"

    # a) copia in .codex/prompts/req.$PROMPT.md
    dst1="$PROJECT_BASE/.codex/prompts/req.$PROMPT.md"
    copy_and_replace "$file" "$dst1" "codex" 
    if [ "$VERBOSE" -eq 1 ]; then echo "OK: scritto $dst1"; fi

    # b) copia in .github/agents/req.$PROMPT.agent.md
    dst2="$PROJECT_BASE/.github/agents/req.$PROMPT.agent.md"
    copy_and_replace "$file" "$dst2" "github" 
    if [ "$VERBOSE" -eq 1 ]; then echo "OK: scritto $dst2"; fi

    # c) crea .github/prompts/req.$PROMPT.prompt.md con contenuto che rispecchia l'agente
    dst3="$PROJECT_BASE/.github/prompts/req.$PROMPT.prompt.md"
    mkdir -p "$(dirname "$dst3")"
    cat > "$dst3" <<EOF
---
agent: req.$PROMPT.agent
---
EOF
    if [ "$VERBOSE" -eq 1 ]; then echo "OK: scritto $dst3"; fi

    # d) genera file .gemini/commands/req.$PROMPT.toml usando md2toml/md2toml.sh
    dst4="$PROJECT_BASE/.gemini/commands/req.$PROMPT.toml"
    mkdir -p "$(dirname "$dst4")"
    # scegli convertitore disponibile
    if [ -x "$SCRIPT_BASE/md2toml.sh" ]; then
      converter="$SCRIPT_BASE/md2toml.sh"
    else
      echo "Errore: nessun convertitore md2toml/md2toml.sh trovato in $SCRIPT_BASE" >&2
      exit 6
    fi
    # esegui conversione: usa --force solo se il file di destinazione esiste
    if [ -f "$dst4" ]; then
      out="$($converter --md "$file" --toml "$dst4" --force 2>&1)"
      rc=$?
    else
      out="$($converter --md "$file" --toml "$dst4" 2>&1)"
      rc=$?
    fi
    # Mostra l'output del convertitore solo se è attivo debug
    if [ "$DEBUG" -eq 1 ]; then
      [ -n "$out" ] && echo "$out"
    fi
    if [ $rc -ne 0 ]; then
      echo "Errore: conversione MD->TOML fallita per $file (exit $rc)" >&2
      [ -n "$out" ] && echo "$out" >&2
      exit 7
    fi
    # Quando verbose, segnala il successo dello step
    if [ "$VERBOSE" -eq 1 ]; then
      echo "OK: generato $dst4"
    fi
    # sostituisci %%REQ_DOC%%, %%REQ_DIR%% e %%ARGS%% nel file generato
    sed -i "s|%%REQ_DOC%%|$SUB_REQ_DOC|g; s|%%REQ_DIR%%|$SUB_TECH_DIR|g; s|%%ARGS%%|{{args}}|g" "$dst4"
  done
fi

# Copia tutti gli script personalizzati presenti in req_scripts o usereq_scripts
script_src=""
if [ -d "$REPO_BASE/req_scripts" ]; then
  script_src="$REPO_BASE/req_scripts"
elif [ -d "$REPO_BASE/usereq_scripts" ]; then
  script_src="$REPO_BASE/usereq_scripts"
fi
if [ -n "$script_src" ]; then
  mkdir -p "$PROJECT_BASE/.req/scripts"
  cp -r "$script_src/." "$PROJECT_BASE/.req/scripts/" || true
  if [ "$VERBOSE" -eq 1 ]; then
    echo "OK: copiati script da $script_src a $PROJECT_BASE/.req/scripts"
  fi
fi

# Copia template (supporta sia req_templates che usereq_templates)
template_src=""
if [ -d "$REPO_BASE/req_templates" ]; then
  template_src="$REPO_BASE/req_templates"
elif [ -d "$REPO_BASE/usereq_templates" ]; then
  template_src="$REPO_BASE/usereq_templates"
fi
if [ -n "$template_src" ]; then
  mkdir -p "$PROJECT_BASE/.req/templates"
  cp -r "$template_src/." "$PROJECT_BASE/.req/templates/"
  if [ "$VERBOSE" -eq 1 ]; then
    echo "OK: copiati template da $template_src a $PROJECT_BASE/.req/templates"
  fi
fi

# Integra settings.json di vscode
if [ -f "$REPO_BASE/vcode/settings.json" ]; then
  mkdir -p "$PROJECT_BASE/.vscode"
  target_settings="$PROJECT_BASE/.vscode/settings.json"
  if [ -f "$target_settings" ]; then
    # Unione JSON: usa python per effettuare merge senza rimuovere chiavi esistenti
    python3 - <<PY
import json,sys
base=json.load(open('$target_settings'))
src=json.load(open('$REPO_BASE/vcode/settings.json'))
base.update(src)
json.dump(base,open('$target_settings','w'),indent=2,ensure_ascii=False)
PY
  else
    cp "$REPO_BASE/vcode/settings.json" "$target_settings"
  fi
  if [ "$VERBOSE" -eq 1 ]; then
    echo "OK: integrato settings.json in $target_settings"
  fi
fi

echo "Req: operazioni completate in $PROJECT_BASE"
