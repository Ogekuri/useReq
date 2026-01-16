#!/bin/bash
# -*- coding: utf-8 -*-
# VERSION: 0.0.51
# AUTHORS: Ogekuri

now=$(date '+%Y-%m-%d_%H-%M-%S')

# 1. Ottieni il percorso assoluto completo del file (risolvendo i link simbolici)
FULL_PATH=$(readlink -f "$0")

# 2. Estrai la directory (il percorso senza il nome del file)
SCRIPT_PATH=$(dirname "$FULL_PATH")

# 3. Estrai il nome del file
SCRIPT_NAME=$(basename "$FULL_PATH")

# --- Test di output (puoi rimuoverli) ---
#echo "Percorso completo:   $FULL_PATH"
#echo "Directory:           $SCRIPT_PATH"
#echo "Nome script:         $SCRIPT_NAME"

VENVDIR="${SCRIPT_PATH}/.venv"
#echo ${VENVDIR}

# Se non c'e il ${VENVDIR} lo crea
if ! [ -d "${VENVDIR}/" ]; then
  echo -n "Create virtual environment ..."
  mkdir ${VENVDIR}/
  virtualenv --python=python3 ${VENVDIR}/ >/dev/null
  echo "done."

  # Installa i requisiti Python
  source ${VENVDIR}/bin/activate

  echo -n "Install python requirements ..."
  ${VENVDIR}/bin/pip install -r "${SCRIPT_PATH}/requirements.txt" >/dev/null
  echo "done." 
else
  # echo "Ambiente virtuale trovato."
  source ${VENVDIR}/bin/activate
fi

# Esegue l'applicazione:
PYTHONPATH="${SCRIPT_PATH}/src:${PYTHONPATH}" \
    exec ${VENVDIR}/bin/python3 -c 'from usereq.cli import main; raise SystemExit(main())' "$@"
