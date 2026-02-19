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
    #echo req --update --base --enable-claude --enable-codex --enable-gemini --enable-github --enable-kiro --enable-opencode --enable-models --enable-tools
    req --update --base --enable-claude --enable-codex --enable-gemini --enable-github --enable-kiro --enable-opencode --enable-models --enable-tools
fi
