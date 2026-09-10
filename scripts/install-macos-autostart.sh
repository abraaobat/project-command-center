#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

resolve_saas_root() {
  local preferred="$HOME/Projects/saas-engineering-platform"
  local desktop_base="$HOME/Desktop/SAAS - Projetos"
  local detected=""
  local base=""
  local pid=""
  local cwd=""

  if [[ -n "${SAAS_ENGINEERING_ROOT:-}" ]]; then
    print -r -- "$SAAS_ENGINEERING_ROOT"
    return 0
  fi

  if [[ -f "$preferred/products/studyos/src/server.mjs" ]]; then
    print -r -- "$preferred"
    return 0
  fi

  # Melhor evidência: se o StudyOS já estiver ouvindo em :8788, usa o cwd real do processo.
  pid="$(lsof -tiTCP:8788 -sTCP:LISTEN 2>/dev/null | head -n1 || true)"
  if [[ -n "$pid" ]]; then
    cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -n1 || true)"
    if [[ -n "$cwd" && -f "$cwd/src/server.mjs" && "$cwd" == */products/studyos ]]; then
      print -r -- "${cwd%/products/studyos}"
      return 0
    fi
  fi

  # Compatibilidade com a localização histórica usada neste Mac.
  if [[ -d "$desktop_base" ]]; then
    detected="$(find "$desktop_base" -maxdepth 10 -type f -path '*/saas-engineering-platform/products/studyos/src/server.mjs' -print -quit 2>/dev/null || true)"
    if [[ -n "$detected" ]]; then
      print -r -- "${detected%/products/studyos/src/server.mjs}"
      return 0
    fi
  fi

  # Spotlight costuma ser mais rápido que varrer todo o HOME.
  if command -v mdfind >/dev/null 2>&1; then
    detected="$(mdfind -onlyin "$HOME" 'kMDItemFSName == "server.mjs"' 2>/dev/null | grep '/saas-engineering-platform/products/studyos/src/server.mjs$' | head -n1 || true)"
    if [[ -n "$detected" ]]; then
      print -r -- "${detected%/products/studyos/src/server.mjs}"
      return 0
    fi
  fi

  # Fallback controlado nas áreas comuns do usuário.
  for base in "$HOME/Projects" "$HOME/Desktop" "$HOME/Documents"; do
    [[ -d "$base" ]] || continue
    detected="$(find "$base" -maxdepth 10 -type f -path '*/saas-engineering-platform/products/studyos/src/server.mjs' -print -quit 2>/dev/null || true)"
    if [[ -n "$detected" ]]; then
      print -r -- "${detected%/products/studyos/src/server.mjs}"
      return 0
    fi
  done

  print -r -- "$preferred"
}

SAAS_ROOT="$(resolve_saas_root)"
STUDYOS_ROOT="$SAAS_ROOT/products/studyos"
LAUNCH_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs/ProjectCommandCenter"
PCC_LABEL="com.abraaobat.project-command-center"
STUDYOS_LABEL="com.abraaobat.studyos-local"
PCC_PLIST="$LAUNCH_DIR/$PCC_LABEL.plist"
STUDYOS_PLIST="$LAUNCH_DIR/$STUDYOS_LABEL.plist"
PYTHON_BIN="$(command -v python3 || true)"
USER_ID="$(id -u)"
BASE_PATH="$HOME/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  echo "Erro: python3 não encontrado." >&2
  exit 1
fi
if [[ ! -f "$PROJECT_ROOT/scripts/project-command-center-service.sh" ]]; then
  echo "Erro: runtime do Project Command Center não encontrado." >&2
  exit 1
fi
if [[ ! -f "$STUDYOS_ROOT/src/server.mjs" ]]; then
  echo "Erro: StudyOS não encontrado." >&2
  echo "Caminho testado: $STUDYOS_ROOT" >&2
  echo "Localize com:" >&2
  echo "  find \"$HOME\" -type f -path '*/saas-engineering-platform/products/studyos/src/server.mjs' -print 2>/dev/null | head" >&2
  echo "Ou informe manualmente:" >&2
  echo "  SAAS_ENGINEERING_ROOT=/caminho/saas-engineering-platform /bin/zsh scripts/install-macos-autostart.sh" >&2
  exit 1
fi
if [[ ! -s "$HOME/.nvm/nvm.sh" ]]; then
  echo "Erro: NVM não encontrado em $HOME/.nvm/nvm.sh" >&2
  exit 1
fi

echo "SaaS Engineering Platform: $SAAS_ROOT"
echo "StudyOS:                  $STUDYOS_ROOT"

mkdir -p "$LAUNCH_DIR" "$LOG_DIR"

stop_known_listener() {
  local port="$1"
  local expected_cwd="$2"
  local expected_fragment="$3"
  local pid=""
  local cmd=""
  local cwd=""
  pid="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null | head -n1 || true)"
  [[ -z "$pid" ]] && return 0
  cmd="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -n1 || true)"
  if [[ "$cwd" == "$expected_cwd" && "$cmd" == *"$expected_fragment"* ]]; then
    echo "Encerrando processo manual conhecido em :$port (PID $pid)..."
    kill -TERM "$pid" 2>/dev/null || true
    for _ in {1..20}; do
      lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1 || return 0
      sleep 0.25
    done
  fi
  if lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Erro: a porta $port está ocupada por um processo que não vou encerrar automaticamente." >&2
    echo "PID: $pid" >&2
    echo "Comando: $cmd" >&2
    echo "Diretório: $cwd" >&2
    exit 1
  fi
}

launchctl bootout "gui/$USER_ID" "$PCC_PLIST" >/dev/null 2>&1 || true
launchctl bootout "gui/$USER_ID" "$STUDYOS_PLIST" >/dev/null 2>&1 || true

stop_known_listener 8787 "$PROJECT_ROOT" "http.server 8787"
stop_known_listener 8788 "$STUDYOS_ROOT" "node src/server.mjs"
rm -f "$STUDYOS_ROOT/.local/server.pid"

cat > "$PCC_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$PCC_LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/zsh</string><string>$PROJECT_ROOT/scripts/project-command-center-service.sh</string></array>
  <key>WorkingDirectory</key><string>$PROJECT_ROOT</string>
  <key>EnvironmentVariables</key><dict>
    <key>HOME</key><string>$HOME</string>
    <key>PATH</key><string>$BASE_PATH</string>
    <key>PCC_PORT</key><string>8787</string>
    <key>PCC_PYTHON_BIN</key><string>$PYTHON_BIN</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>ThrottleInterval</key><integer>5</integer>
  <key>StandardOutPath</key><string>$LOG_DIR/project-command-center.out.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/project-command-center.err.log</string>
</dict>
</plist>
EOF

cat > "$STUDYOS_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$STUDYOS_LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/zsh</string><string>$PROJECT_ROOT/scripts/studyos-launchd-service.sh</string></array>
  <key>WorkingDirectory</key><string>$STUDYOS_ROOT</string>
  <key>EnvironmentVariables</key><dict>
    <key>HOME</key><string>$HOME</string>
    <key>PATH</key><string>$BASE_PATH</string>
    <key>NVM_DIR</key><string>$HOME/.nvm</string>
    <key>STUDYOS_ROOT</key><string>$STUDYOS_ROOT</string>
    <key>STUDYOS_PORT</key><string>8788</string>
    <key>STUDYOS_HOST</key><string>0.0.0.0</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>ThrottleInterval</key><integer>5</integer>
  <key>StandardOutPath</key><string>$LOG_DIR/studyos.out.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/studyos.err.log</string>
</dict>
</plist>
EOF

plutil -lint "$PCC_PLIST"
plutil -lint "$STUDYOS_PLIST"

launchctl bootstrap "gui/$USER_ID" "$PCC_PLIST"
launchctl bootstrap "gui/$USER_ID" "$STUDYOS_PLIST"
launchctl enable "gui/$USER_ID/$PCC_LABEL" >/dev/null 2>&1 || true
launchctl enable "gui/$USER_ID/$STUDYOS_LABEL" >/dev/null 2>&1 || true
launchctl kickstart -k "gui/$USER_ID/$PCC_LABEL"
launchctl kickstart -k "gui/$USER_ID/$STUDYOS_LABEL"

wait_http() {
  local url="$1"
  local name="$2"
  for _ in {1..40}; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "OK: $name"
      return 0
    fi
    sleep 0.25
  done
  echo "FALHA: $name não respondeu a tempo." >&2
  return 1
}

echo ""
echo "Verificando serviços..."
PCC_OK=0
STUDYOS_OK=0
wait_http "http://127.0.0.1:8787/" "Project Command Center :8787" || PCC_OK=1
wait_http "http://127.0.0.1:8788/api/health" "StudyOS Local :8788" || STUDYOS_OK=1

echo ""
echo "Autostart configurado via launchd para o login deste usuário."
echo "Project Command Center: http://localhost:8787"
echo "StudyOS:               http://localhost:8788/orientador"
echo "Logs:                   $LOG_DIR"
echo ""
echo "Status:"
launchctl print "gui/$USER_ID/$PCC_LABEL" 2>/dev/null | grep -E 'state =|pid =' | head -2 || true
launchctl print "gui/$USER_ID/$STUDYOS_LABEL" 2>/dev/null | grep -E 'state =|pid =' | head -2 || true

if (( PCC_OK != 0 || STUDYOS_OK != 0 )); then
  echo "Algum serviço não respondeu. Consulte os logs acima." >&2
  exit 1
fi
