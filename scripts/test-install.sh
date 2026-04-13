#!/bin/bash
# -*- coding: utf-8 -*-
# VERSION: 0.61.0
# AUTHORS: Ogekuri
# @file test-install.sh
# @brief Rebuilds a disposable installation target with the repository
# smoke-test configuration.
# @details Resolves repository-relative paths, removes generated provider
# directories from the target path, recreates the required directory scaffold,
# and invokes `scripts/req.sh` with the canonical installation argument set.
# The provider list includes Pi prompts and Pi skills with artifact-local
# `enable-models` and `enable-tools` options so `.pi` resources are exercised
# during smoke installation.
# @satisfies SRS-366, SRS-367

# @brief Stores a timestamp string for ad hoc diagnostics.
# @details Retained for compatibility with the existing script layout. No
# downstream consumer reads this variable.
now=$(date '+%Y-%m-%d_%H-%M-%S')

# @brief Stores the canonical absolute path to the current script file.
# @details Resolves symbolic links so downstream path derivation is stable
# across direct and symlinked invocation modes.
FULL_PATH=$(readlink -f "$0")

# @brief Stores the directory that contains the current script file.
# @details Derived from `FULL_PATH`; used to locate `req.sh` without relying on
# the caller working directory.
SCRIPT_PATH=$(dirname "$FULL_PATH")

# @brief Stores the basename of the current script file.
# @details Retained for manual diagnostics and parity with the existing
# smoke-test script layout.
SCRIPT_NAME=$(basename "$FULL_PATH")

# @brief Stores the repository root directory inferred from the script
# location.
# @details Derived from the parent directory of `SCRIPT_PATH`; used as the
# default base for temporary installation targets.
BASE_DIR=$(dirname "$SCRIPT_PATH")

# --- Output tests (can be removed) ---
#echo "Full path:          $FULL_PATH"
#echo "Directory:          $SCRIPT_PATH"
#echo "Script name:        $SCRIPT_NAME"
#echo "Base Directory:     $BASE_DIR"

# @brief Stores the requested installation target path.
# @details Uses the first positional argument when it names an existing
# directory; otherwise the script falls back to a disposable target under
# `temp/test-install`.
FOLDER_PATH="${1:-}"
if ! [ -d "$FOLDER_PATH" ]; then
    # @brief Stores the fallback disposable installation target path.
    # @details Used by the clean-install path when the caller does not provide
    # an existing target directory.
    FOLDER_PATH="$BASE_DIR/temp/test-install"
    echo "Clean+Install on path: ${FOLDER_PATH}"
    rm -rf "${FOLDER_PATH}"
    mkdir -p "${FOLDER_PATH}"
else
    echo "Install on path: ${FOLDER_PATH}"
fi

# @brief Declares generated provider directories deleted before reinstall.
# @details Enumerates provider output roots under the target path that are
# removed before the smoke-test installation runs. Pi prompt and skill roots
# are included to keep repeated executions deterministic.
# @satisfies SRS-367
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
    ".pi/prompts"
    ".pi/skills"
)

if [ ! -d "$FOLDER_PATH" ]; then
    echo "Path does not exist"
    exit 1
else
    echo "Remove old dirs."
    for del in "${delete_dirs[@]}"; do
        #echo Remove directory: "${FOLDER_PATH}/${del}"
        if [ -d "${FOLDER_PATH}/${del}" ]; then
            rm -rf "${FOLDER_PATH}/${del}"
        fi
    done

    # make dirs
    mkdir -p "${FOLDER_PATH}/guidelines"
    mkdir -p "${FOLDER_PATH}/docs"
    mkdir -p "${FOLDER_PATH}/tests"
    mkdir -p "${FOLDER_PATH}/src"
    mkdir -p "${FOLDER_PATH}/.github/workflows"

    # @brief Prints the exact smoke-test installation command line.
    # @details Mirrors the execution command for manual reproduction and keeps
    # the Pi provider visible in installation logs.
    echo "${SCRIPT_PATH}/req.sh" \
        --base "${FOLDER_PATH}" --docs-dir "${FOLDER_PATH}/docs" \
        --guidelines-dir "${FOLDER_PATH}/guidelines" \
        --src-dir "${FOLDER_PATH}/src" --src-dir ".github/workflows" \
        --tests-dir "${FOLDER_PATH}/tests" \
        --upgrade-guidelines \
        --provider claude:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider codex:prompts,skills \
        --provider gemini:prompts,skills \
        --provider github:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider kiro:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider opencode:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider pi:prompts+enable-models+enable-tools,skills+enable-models+enable-tools \
        --enable-static-check C=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c11 \
        --enable-static-check C=Command,clang-format,--dry-run,--Werror \
        --enable-static-check C++=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c++20 \
        --enable-static-check C++=Command,clang-format,--dry-run,--Werror \
        --enable-static-check Python=Pylance \
        --enable-static-check Python=Ruff

    # @brief Executes the smoke-test installation command.
    # @details Installs the canonical provider/resource set, including Pi
    # prompts and Pi skills with model and tool enablement.
    "${SCRIPT_PATH}/req.sh" \
        --base "${FOLDER_PATH}" --docs-dir "${FOLDER_PATH}/docs" \
        --guidelines-dir "${FOLDER_PATH}/guidelines" \
        --src-dir "${FOLDER_PATH}/src" --src-dir ".github/workflows" \
        --tests-dir "${FOLDER_PATH}/tests" \
        --upgrade-guidelines \
        --provider claude:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider codex:prompts,skills \
        --provider gemini:prompts,skills \
        --provider github:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider kiro:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider opencode:prompts+enable-models+enable-tools,agents+enable-models+enable-tools,skills+enable-models+enable-tools \
        --provider pi:prompts+enable-models+enable-tools,skills+enable-models+enable-tools \
        --enable-static-check C=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c11 \
        --enable-static-check C=Command,clang-format,--dry-run,--Werror \
        --enable-static-check C++=Command,cppcheck,--error-exitcode=1,\"--enable=warning,style,performance,portability\",--std=c++20 \
        --enable-static-check C++=Command,clang-format,--dry-run,--Werror \
        --enable-static-check Python=Pylance \
        --enable-static-check Python=Ruff
fi
