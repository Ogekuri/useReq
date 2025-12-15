#!/bin/bash
# AUTHORS: Ogekuri

cd -- "$(dirname "$0")/../"
echo "Run on path: "$(pwd -P)

# check parameters
if [ -z $1 ]; then
    echo "ERROR: missing parameters"
    echo ""
    echo "Usage:      $0 <version>"
    echo ""
    echo "Examples:"
    echo "            $0 1.2.34"
    echo ""
    exit 1
fi

bumpversion --dry-run --verbose --new-version $1 patch --no-commit --no-tag --allow-dirty

echo "Confermi di voler procedere? (S/N)"
read -p "Risposta: " confirm

if [[ "$confirm" =~ ^[sS]$ ]]; then
    echo "Procedo con l'operazione..."
    # Inserisci qui i comandi da eseguire
else
    echo "Operazione annullata."
    exit 1
fi

bumpversion --new-version $1 patch --no-commit --no-tag --allow-dirty
