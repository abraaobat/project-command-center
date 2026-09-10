#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${SAAS_TARGET_ROOT:-$HOME/Projects/saas-engineering-platform}"
SOURCE="${SAAS_ENGINEERING_ROOT:-}"
USER_ID="$(id -u)"
STUDYOS_LABEL="com.abraaobat.studyos-local"
STUDYOS_PLIST="$HOME/Library/LaunchAgents/$STUDYOS_LABEL.plist"

resolve_source() {
  local detected=""
  local pid=""
  local cwd=""

  if [[ -n "$SOURCE" && -f "$SOURCE/products/studyos/src/server.mjs" ]]; then
    print -r -- "$SOURCE"
    return 0
  fi

  pid="$(lsof -tiTCP:8788 -sTCP:LISTEN 2>/dev/null | head -n1 || true)"
  if [[ -n "$pid" ]]; then
    cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -n1 || true)"
    if [[ -n "$cwd" && -f "$cwd/src/server.mjs" && "$cwd" == */products/studyos ]]; then
      print -r -- "${cwd%/products/studyos}"
      return 0
    fi
  fi

  if [[ -d "$HOME/Desktop" ]]; then
    detected="$(find "$HOME/Desktop" -maxdepth 12 -type f -path '*/saas-engineering-platform/products/studyos/src/server.mjs' -print -quit 2>/dev/null || true)"
    if [[ -n "$detected" ]]; then
      print -r -- "${detected%/products/studyos/src/server.mjs}"
      return 0
    fi
  fi

  if command -v mdfind >/dev/null 2>&1; then
    detected="$(mdfind -onlyin "$HOME" 'kMDItemFSName == "server.mjs"' 2>/dev/null | grep '/saas-engineering-platform/products/studyos/src/server.mjs$' | head -n1 || true)"
    if [[ -n "$detected" ]]; then
      print -r -- "${detected%/products/studyos/src/server.mjs}"
      return 0
    fi
  fi

  return 1
}

SOURCE="$(resolve_source || true)"

if [[ -z "$SOURCE" || ! -f "$SOURCE/products/studyos/src/server.mjs" ]]; then
  echo "Erro: não consegui localizar o saas-engineering-platform atual." >&2
  echo "Informe manualmente, por exemplo:" >&2
  echo "SAAS_ENGINEERING_ROOT='/caminho/saas-engineering-platform' /bin/zsh scripts/migrate-saas-runtime-to-projects.sh" >&2
  exit 1
fi

if [[ "$SOURCE" == "$TARGET" ]]; then
  echo "SaaS Engineering Platform já está no caminho recomendado:"
  echo "$TARGET"
  exec env SAAS_ENGINEERING_ROOT="$TARGET" /bin/zsh "$PROJECT_ROOT/scripts/install-macos-autostart.sh"
fi

if [[ -e "$TARGET" ]]; then
  echo "Erro: destino já existe: $TARGET" >&2
  echo "Nenhum arquivo foi movido." >&2
  exit 1
fi

echo "Origem:  $SOURCE"
echo "Destino: $TARGET"
echo ""
echo "Motivo: LaunchAgents do macOS podem ser bloqueados pelas proteções de privacidade ao acessar Desktop/Documents."
echo "O repositório será movido inteiro, preservando .git, alterações locais e arquivos não rastreados."

# Para o job quebrado antes de mover seu WorkingDirectory.
launchctl bootout "gui/$USER_ID" "$STUDYOS_PLIST" >/dev/null 2>&1 || true

# Se houver um StudyOS manual real na porta, encerra apenas quando o cwd corresponde à origem.
pid="$(lsof -tiTCP:8788 -sTCP:LISTEN 2>/dev/null | head -n1 || true)"
if [[ -n "$pid" ]]; then
  cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -n1 || true)"
  cmd="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  if [[ "$cwd" == "$SOURCE/products/studyos" && "$cmd" == *"node src/server.mjs"* ]]; then
    echo "Encerrando StudyOS manual em :8788 (PID $pid)..."
    kill -TERM "$pid" 2>/dev/null || true
    for _ in {1..20}; do
      lsof -iTCP:8788 -sTCP:LISTEN >/dev/null 2>&1 || break
      sleep 0.25
    done
  else
    echo "Erro: :8788 está ocupada por outro processo; não vou encerrá-lo." >&2
    echo "PID: $pid" >&2
    echo "Comando: $cmd" >&2
    echo "Diretório: $cwd" >&2
    exit 1
  fi
fi

mkdir -p "$(dirname "$TARGET")"
mv "$SOURCE" "$TARGET"

# Compatibilidade para atalhos manuais antigos. O launchd NÃO usará este symlink.
if [[ ! -e "$SOURCE" ]]; then
  ln -s "$TARGET" "$SOURCE" 2>/dev/null || true
fi

echo ""
echo "Migração concluída. Reinstalando LaunchAgents com o caminho não protegido..."
exec env SAAS_ENGINEERING_ROOT="$TARGET" /bin/zsh "$PROJECT_ROOT/scripts/install-macos-autostart.sh"
