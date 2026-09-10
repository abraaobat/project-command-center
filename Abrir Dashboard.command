#!/bin/zsh
set -e
cd "$(dirname "$0")"
PORT=8787
LABEL="com.abraaobat.project-command-center"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

# Se o serviço ainda não estiver ativo, tenta iniciar a instalação launchd já configurada.
if ! lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  if [[ -f "$PLIST" ]]; then
    launchctl kickstart -k "gui/$(id -u)/$LABEL" >/dev/null 2>&1 || true
    for _ in {1..20}; do
      lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1 && break
      sleep 0.25
    done
  fi
fi

# Fallback para instalações ainda sem launchd.
if ! lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  nohup /bin/zsh scripts/project-command-center-service.sh >/tmp/project-command-center-fallback.log 2>&1 &
  for _ in {1..20}; do
    lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1 && break
    sleep 0.25
  done
fi

if ! lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Não foi possível iniciar o Project Command Center. Veja /tmp/project-command-center-fallback.log"
  exit 1
fi

open "http://localhost:$PORT"
echo "Project Command Center aberto em http://localhost:$PORT"
echo "Serviço persistente: $LABEL"
