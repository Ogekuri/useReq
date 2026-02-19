#!/bin/bash

# Assegna il primo argomento passato allo script alla variabile FOLDER_PATH
FOLDER_PATH="temp/test-prj"

rm -rf "${FOLDER_PATH}"
mkdir -p "${FOLDER_PATH}"

# Controlla se il percorso NON esiste o NON è una directory
if [ ! -d "$FOLDER_PATH" ]; then
    echo "Path does not exist"
    exit 1
else
    # make dirs
    mkdir -p "${FOLDER_PATH}/docs"
    mkdir -p "${FOLDER_PATH}/guidelines"
    mkdir -p "${FOLDER_PATH}/tests"
    mkdir -p "${FOLDER_PATH}/src"
    mkdir -p "${FOLDER_PATH}/.github/workflows"
    touch "${FOLDER_PATH}/docs/.place-holder"
    touch "${FOLDER_PATH}/guidelines/.place-holder"

    echo req --base "${FOLDER_PATH}" --docs-dir "${FOLDER_PATH}/docs" --guidelines-dir "${FOLDER_PATH}/guidelines" --tests-dir "${FOLDER_PATH}/tests" --src-dir "${FOLDER_PATH}/src" --src-dir "${FOLDER_PATH}/.github/workflows" --enable-skills --upgrade-guidelines --enable-claude --enable-codex --enable-gemini --enable-github --enable-kiro --enable-opencode --enable-models --enable-tools --legacy
    req --base "${FOLDER_PATH}" --docs-dir "${FOLDER_PATH}/docs" --guidelines-dir "${FOLDER_PATH}/guidelines" --tests-dir "${FOLDER_PATH}/tests" --src-dir "${FOLDER_PATH}/src" --src-dir "${FOLDER_PATH}/.github/workflows" --enable-skills --upgrade-guidelines --enable-claude --enable-codex --enable-gemini --enable-github --enable-kiro --enable-opencode --enable-models --enable-tools --legacy
fi
