#!/bin/bash
# -*- coding: utf-8 -*-
# VERSION: 0.42.0
# AUTHORS: Ogekuri

set -euo pipefail

FULL_PATH="$(readlink -f "$0")"
SCRIPT_PATH="$(dirname "$FULL_PATH")"
BASE_DIR="$(dirname "$SCRIPT_PATH")"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv command not found in PATH" >&2
  exit 1
fi

PYTHONPATH="${BASE_DIR}/src:${PYTHONPATH:-}" \
  exec uv run --project "${BASE_DIR}" python -m usereq.cli "$@"
