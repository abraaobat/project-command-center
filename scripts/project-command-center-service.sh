#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PCC_PORT:-8787}"
BIND="${PCC_BIND:-127.0.0.1}"
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

sync_git() {
  [[ -d ".git" ]] || return 0
  git remote get-url origin >/dev/null 2>&1 || return 0
  local branch
  branch="$(git branch --show-current 2>/dev/null || true)"
  [[ -n "$branch" ]] || return 0
  git fetch origin "$branch" >>/tmp/project-command-center-git.log 2>&1 || return 0
  git merge --ff-only "origin/$branch" >>/tmp/project-command-center-git.log 2>&1 || true
}

cleanup() {
  trap - EXIT INT TERM
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$SYNC_PID" ]]; then
    kill "$SYNC_PID" >/dev/null 2>&1 || true
  fi
  [[ -n "$SERVER_PID" ]] && wait "$SERVER_PID" >/dev/null 2>&1 || true
  [[ -n "$SYNC_PID" ]] && wait "$SYNC_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

# O servidor local inclui a API do Action Runner. Ele fica preso ao loopback por
# padrão porque marcar uma ação pode iniciar um agente que edita o workspace.
"$PYTHON_BIN" scripts/command_center_server.py --port "$PORT" --bind "$BIND" &
SERVER_PID=$!

# Mantém fontes locais/GitHub atualizadas em background. A primeira atualização
# ocorre logo após o servidor já estar disponível.
(
  sync_status
  while true; do
    sync_git
    sync_status
    sleep 60
  done
) &
SYNC_PID=$!

wait "$SERVER_PID"
