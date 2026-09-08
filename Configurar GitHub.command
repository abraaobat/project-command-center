#!/bin/zsh
set -e
cd "$(dirname "$0")"

REPO="abraaobat/project-command-center"
DESC="Painel mestre vivo para acompanhar andamento, marcos e próximos passos dos projetos."

echo "=== Project Command Center — configuração GitHub ==="

if ! command -v git >/dev/null 2>&1; then
  echo "Git não encontrado. Instale as Command Line Tools do macOS e execute novamente."
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) não encontrado."
  echo "Se você usa Homebrew: brew install gh"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "O GitHub CLI ainda não está autenticado."
  echo "Execute: gh auth login"
  exit 1
fi

if [ ! -d ".git" ]; then
  git init -b main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "feat: initialize Project Command Center v4"
fi

if gh repo view "$REPO" >/dev/null 2>&1; then
  echo "Repositório já existe: $REPO"
  if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "git@github.com:$REPO.git"
  fi
  git push -u origin main
else
  gh repo create "$REPO" \
    --public \
    --description "$DESC" \
    --source=. \
    --remote=origin \
    --push
fi

echo ""
echo "Pronto: https://github.com/$REPO"
echo "Abrindo dashboard..."
open "./Abrir Dashboard.command"
