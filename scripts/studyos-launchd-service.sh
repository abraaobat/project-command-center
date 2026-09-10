#!/bin/zsh
set -euo pipefail

STUDYOS_ROOT="${STUDYOS_ROOT:-$HOME/Projects/saas-engineering-platform/products/studyos}"
SAAS_ROOT="$(cd "$STUDYOS_ROOT/../.." && pwd)"
NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if [[ ! -f "$STUDYOS_ROOT/src/server.mjs" ]]; then
  echo "StudyOS não encontrado em: $STUDYOS_ROOT" >&2
  exit 1
fi

if [[ -s "$NVM_DIR/nvm.sh" ]]; then
  source "$NVM_DIR/nvm.sh"
fi

cd "$SAAS_ROOT"
if command -v nvm >/dev/null 2>&1 && [[ -f .nvmrc ]]; then
  nvm use --silent >/dev/null
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js não encontrado para o StudyOS." >&2
  exit 1
fi

cd "$STUDYOS_ROOT"
export STUDYOS_PORT="${STUDYOS_PORT:-8788}"
export STUDYOS_HOST="${STUDYOS_HOST:-0.0.0.0}"

# Foreground: o launchd passa a supervisionar o processo diretamente.
exec node src/server.mjs
