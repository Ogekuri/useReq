#!/bin/bash

# Assegna il primo argomento passato allo script alla variabile FOLDER_PATH
FOLDER_PATH="$1"

# Controlla se la variabile è vuota (l'utente non ha passato argomenti)
if [ -z "$FOLDER_PATH" ]; then
    echo "Usage: $0 <path_to_folder>"
    exit 1
fi

# Controlla se il percorso NON esiste o NON è una directory
if [ ! -d "$FOLDER_PATH" ]; then
    echo "Path does not exist"
    exit 1
else
    # make dirs
    mkdir -p "${FOLDER_PATH}/req"
    mkdir -p "${FOLDER_PATH}/guidelines"
    mkdir -p "${FOLDER_PATH}/docs"
    mkdir -p "${FOLDER_PATH}/tests"
    mkdir -p "${FOLDER_PATH}/src"
    mkdir -p "${FOLDER_PATH}/.github/workflows"

    echo req --base "${FOLDER_PATH}" --docs-dir "${FOLDER_PATH}/docs" --guidelines-dir "${FOLDER_PATH}/guidelines" \
--src-dir "${FOLDER_PATH}/src" --src-dir ".github/workflows" \
--tests-dir "${FOLDER_PATH}/tests" \
--enable-claude --enable-codex --enable-gemini --enable-github --enable-kiro --enable-opencode --enable-models --enable-tools \
--enable-static-check C=Command#cppcheck#--error-exitcode=1#--enable=warning,style,performance,portability#--std=c11 \
--enable-static-check C++=Command#cppcheck#--error-exitcode=1#--enable=warning,style,performance,portability#--std=c++20 \
--enable-static-check Python=Pylance
fi
