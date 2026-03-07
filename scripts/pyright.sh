#!/bin/bash
# -*- coding: utf-8 -*-
# VERSION: 0.29.0
# AUTHORS: Ogekuri

now=$(date '+%Y-%m-%d_%H-%M-%S')

# 1. Get the full absolute path of the file (resolving symbolic links)
FULL_PATH=$(readlink -f "$0")

# 2. Extract the directory (the path without the filename)
SCRIPT_PATH=$(dirname "$FULL_PATH")

# 3. Extract the filename
SCRIPT_NAME=$(basename "$FULL_PATH")

# 4. Extract the base directory
BASE_DIR=$(dirname "$SCRIPT_PATH")

# --- Output tests (can be removed) ---
#echo "Full path:          $FULL_PATH"
#echo "Directory:          $SCRIPT_PATH"
#echo "Script name:        $SCRIPT_NAME"
#echo "Base Directory:     $BASE_DIR"


VENVDIR="${BASE_DIR}/.venv"
REQUIREMENTS_FILE="${BASE_DIR}/requirements.txt"

if ! [ -f "${REQUIREMENTS_FILE}" ]; then
  echo "ERROR: requirements.txt not found at ${REQUIREMENTS_FILE}" >&2
  exit 1
fi

if ! [ -d "${VENVDIR}/" ]; then
  echo -n "Create virtual environment ..."
  mkdir -p "${VENVDIR}/"
  virtualenv --python=python3 "${VENVDIR}/" >/dev/null
  echo "done."

  source "${VENVDIR}/bin/activate"

  echo -n "Install python requirements ..."
  "${VENVDIR}/bin/pip" install -r "${REQUIREMENTS_FILE}" >/dev/null
  echo "done."
else
  source "${VENVDIR}/bin/activate"
fi

# Execute the application:
PYTHONPATH="${BASE_DIR}/src:${PYTHONPATH}" \
    exec "${VENVDIR}/bin/pyright" "$@"
