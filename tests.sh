#!/bin/bash
# -*- coding: utf-8 -*-
# VERSION: 0.0.40
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
  ${VENVDIR}/bin/playwright install chromium
  echo "done." 
else
  # echo "Ambiente virtuale trovato."
  source ${VENVDIR}/bin/activate
fi

# Esegue i test in 2 fasi:
# 1) Suite standard
# 2) Solo i post-test di validazione link (solo se 1) ha successo)

PYTHONPATH="${SCRIPT_PATH}/src:${PYTHONPATH}" \
    ${VENVDIR}/bin/python3 -m 'pytest' "$@"

rc=$?
if [ $rc -ne 0 ]; then
  exit $rc
fi

echo "[tests.sh] Main test suite OK. Running post-link tests..."

PYTHONPATH="${SCRIPT_PATH}/src:${PYTHONPATH}" \
  RUN_POST_LINK_TESTS=1 \
  ${VENVDIR}/bin/python3 -m 'pytest'
