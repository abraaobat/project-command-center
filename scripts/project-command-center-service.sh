#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PCC_PORT:-8787}"
PYTHON_BIN="${PCC_PYTHON_BIN:-$(command -v python3 || true)}"
SYNC_PID=""
SERVER_PID=""

cd "$PROJECT_ROOT"

if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  echo "python3 não encontrado." >&2
  exit 1
fi

sync_status() {
  if [[ -f "scripts/sync_status_sources.py" ]]; then
    "$PYTHON_BIN" scripts/sync_status_sources.py >>/tmp/project-command-center-sync.log 2>&1 || true
  fi
}

cleanup() {
  trap - EXIT INT TERM
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$SYNC_PID" ]]; then
    kill "$SYNC_PID" >/dev/null 2>&1 || true
  fi
  wait "$SERVER_PID" >/dev/null 2>&1 || true
  wait "$SYNC_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

# Atualiza a visão runtime imediatamente.
sync_status

# Mantém fontes locais/GitHub atualizadas sem depender de uma janela do Terminal.
(
  while true; do
    if [[ -d ".git" ]] && git remote get-url origin >/dev/null 2>&1; then
      git pull --ff-only >>/tmp/project-command-center-git.log 2>&1 || true
    fi
    sync_status
    sleep 60
  done
) &
SYNC_PID=$!

# O servidor fica como filho direto deste serviço; o shell permanece vivo para
# encerrar também o loop de sincronização quando o launchd reiniciar o job.
"$PYTHON_BIN" -m http.server "$PORT" &
SERVER_PID=$!
wait "$SERVER_PID"
