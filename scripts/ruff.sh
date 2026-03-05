#!/bin/bash
# -*- coding: utf-8 -*-
# VERSION: 0.10.0
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
#echo ${VENVDIR}

# If ${VENVDIR} does not exist, create it
if ! [ -d "${VENVDIR}/" ]; then
  echo -n "Create virtual environment ..."
  mkdir ${VENVDIR}/
  virtualenv --python=python3 ${VENVDIR}/ >/dev/null
  echo "done."

  # Install Python requirements
  source ${VENVDIR}/bin/activate

  echo -n "Install python requirements ..."
  ${VENVDIR}/bin/pip install -r "${BASE_DIR}/requirements.txt" >/dev/null
  echo "done." 
else
  # echo "Virtual environment found."
  source ${VENVDIR}/bin/activate
fi

# Execute the application:
PYTHONPATH="${BASE_DIR}/src:${PYTHONPATH}" \
    exec ${VENVDIR}/bin/ruff "$@"
