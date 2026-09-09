#!/bin/zsh
set -e
cd "$(dirname "$0")"
PORT=8787

sync_status() {
  if [ -f "scripts/sync_status_sources.py" ]; then
    python3 scripts/sync_status_sources.py >>/tmp/project-command-center-sync.log 2>&1 || true
  fi
}

# Gera a visão runtime antes de abrir o painel.
sync_status

# Mantém a cópia local sincronizada com o GitHub e atualiza as fontes externas.
if [ -d ".git" ] && git remote get-url origin >/dev/null 2>&1; then
  (
    while true; do
      git pull --ff-only >/dev/null 2>&1 || true
      sync_status
      sleep 60
    done
  ) &
fi

# Evita iniciar um segundo servidor se a porta já estiver ocupada.
if ! lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  python3 -m http.server "$PORT" >/tmp/project-command-center.log 2>&1 &
  sleep 1
fi

open "http://localhost:$PORT"
echo "Project Command Center aberto em http://localhost:$PORT"
echo "Auto Status Sync ativo; log em /tmp/project-command-center-sync.log"
