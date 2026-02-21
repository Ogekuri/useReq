#!/bin/bash
# VERSION: 0.0.75
# AUTHORS: Ogekuri

cd -- "$(dirname "$0")/"
echo "Run on path: "$(pwd -P)

VENVDIR=".venv"

if [ -d "${VENVDIR}/" ]; then
    echo -n "Remove old virtual environment ..."
    rm -rf ${VENVDIR}/
    echo "done."
fi

# If ${VENVDIR} does not exist, create it
if ! [ -d "${VENVDIR}/" ]; then
    echo -n "Create virtual environment ..."
    mkdir ${VENVDIR}/
    virtualenv --python=python3 ${VENVDIR}/ >/dev/null
    echo "done."
fi

# Install Python requirements
source ${VENVDIR}/bin/activate

echo -n "Install python requirements ..."
${VENVDIR}/bin/pip install -r requirements.txt >/dev/null
echo "done."
