#!/bin/bash

FOLDER_PATH="${1:-}"
if ! [ -d "$FOLDER_PATH" ]; then
    # Assegna il primo argomento passato allo script alla variabile FOLDER_PATH
    FOLDER_PATH="temp/test-install"
    echo "Clean+Install on path: ${FOLDER_PATH}"
    rm -rf "${FOLDER_PATH}"
    mkdir -p "${FOLDER_PATH}"
else
    echo "Install on path: ${FOLDER_PATH}"
fi

delete_dirs=(
    ".gemini/commands"
    ".gemini/skills"
    ".claude/commands"
    ".claude/agents"
    ".claude/skills"
    ".github/prompts"
    ".github/agents"
    ".github/skills"
    ".codex/prompts"
    ".codex/skills"
    ".kiro/prompts"
    ".kiro/agents"
    ".kiro/skills"
    ".opencode/agent"
    ".opencode/command"
    ".opencode/skill"
)

# Controlla se il percorso NON esiste o NON è una directory
if [ ! -d "$FOLDER_PATH" ]; then
    echo "Path does not exist"
    exit 1
else
    echo "Remove old dirs."
    for del in "${delete_dirs[@]}"; do
	#echo Remove direcory: "${FOLDER_PATH}/${del}"
	if [ -d "${FOLDER_PATH}/${del}" ]; then
	    rm -rf "${FOLDER_PATH}/${del}"
	fi
    done

    # make dirs
    rm -rf "${FOLDER_PATH}/guidelines"
    mkdir -p "${FOLDER_PATH}/guidelines"
    mkdir -p "${FOLDER_PATH}/docs"
    mkdir -p "${FOLDER_PATH}/tests"
    mkdir -p "${FOLDER_PATH}/src"
    mkdir -p "${FOLDER_PATH}/.github/workflows"
    touch "${FOLDER_PATH}/docs/.place-holder"
    touch "${FOLDER_PATH}/guidelines/.place-holder"
    touch "${FOLDER_PATH}/tests/.place-holder"
    touch "${FOLDER_PATH}/src/.place-holder"
    touch "${FOLDER_PATH}/.github/workflows/.place-holder"

    echo req --base "${FOLDER_PATH}" --docs-dir "${FOLDER_PATH}/docs" --guidelines-dir "${FOLDER_PATH}/guidelines" --tests-dir "${FOLDER_PATH}/tests"
    req \
--base "${FOLDER_PATH}" --docs-dir "${FOLDER_PATH}/docs" --guidelines-dir "${FOLDER_PATH}/guidelines" \
--src-dir "${FOLDER_PATH}/src" --src-dir ".github/workflows" \
--tests-dir "${FOLDER_PATH}/tests" \
--upgrade-guidelines \
--enable-claude --enable-codex --enable-gemini --enable-github --enable-kiro --enable-opencode \
--enable-models --enable-tools \
--enable-prompts --enable-agents \
--enable-static-check C=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c11 \
--enable-static-check C=Command,clang-format,--dry-run,--Werror \
--enable-static-check C++=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c++20 \
--enable-static-check C++=Command,clang-format,--dry-run,--Werror \
--enable-static-check Python=Pylance \
--enable-static-check Python=Ruff
fi
