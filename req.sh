#!/bin/bash
# -*- coding: utf-8 -*-
# VERSION: 0.0.4
# AUTHORS: Ogekuri

now=$(date '+%Y-%m-%d_%H-%M-%S')

# 1. Ottieni il percorso assoluto completo del file (risolvendo i link simbolici)
FULL_PATH=$(readlink -f "$0")

# 2. Estrai la directory (il percorso senza il nome del file)
SCRIPT_PATH=$(dirname "$FULL_PATH")

# 3. Estrai il nome del file
SCRIPT_NAME=$(basename "$FULL_PATH")

# --- Test di output (puoi rimuoverli) ---
#echo "Full Path:   $FULL_PATH"
#echo "Directory:   $SCRIPT_PATH"
#echo "Script Name: $SCRIPT_NAME"

VENVDIR="${SCRIPT_PATH}/.venv"
#echo ${VENVDIR}

# Se non c'è il ${VENVDIR} lo crea
if ! [ -d "${VENVDIR}/" ]; then
  echo -n "Create virtual environment ..."
  mkdir ${VENVDIR}/
  virtualenv --python=python3 ${VENVDIR}/ >/dev/null
  echo "done."

  # Install requirements
  source ${VENVDIR}/bin/activate

  echo -n "Install python requirements ..."
  ${VENVDIR}/bin/pip install -r requirements.txt >/dev/null
  echo "done." 
else
  # echo "Virtual environment found."
  source ${VENVDIR}/bin/activate
fi

# Execute application:
PYTHONPATH="${SCRIPT_PATH}/src:${PYTHONPATH}" \
    exec ${VENVDIR}/bin/python3 -c 'from usereq.cli import main; raise SystemExit(main())' "$@"
