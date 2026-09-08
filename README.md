# Project Command Center v4

Painel mestre vivo para acompanhar os projetos, progresso estimado, fase atual,
próximo marco e atividade recente.

## Primeira instalação no Mac

1. Descompacte esta pasta em um local permanente.
2. Dê duplo clique em `Configurar GitHub.command`.
3. O script:
   - inicia um repositório Git local;
   - cria `abraaobat/project-command-center` se ele ainda não existir;
   - publica a versão inicial;
   - configura `origin`;
   - abre o dashboard.

Pré-requisitos: `git`, GitHub CLI (`gh`) e autenticação do `gh`.

Se o `gh` não estiver instalado:

```bash
brew install gh
gh auth login
```

Depois execute novamente `Configurar GitHub.command`.

## Uso diário

Dê duplo clique em:

`Abrir Dashboard.command`

O painel abre em:

`http://localhost:8787`

Enquanto estiver aberto:
- `git pull --ff-only` roda a cada 60 segundos;
- `projects.json` e `activity.json` são recarregados no navegador a cada 10 segundos.

## Fonte de dados

- `data/projects.json` — estado atual dos projetos.
- `data/activity.json` — histórico recente.
- `scripts/update_project.py` — atualização manual opcional.

Exemplo:

```bash
python3 scripts/update_project.py radionode-br   --progress 30   --current "RX AFSK validado em bancada"   --next "Validar TX AFSK"   --activity "Primeiro RX AFSK real decodificado."
```

Depois:

```bash
git add .
git commit -m "chore: update RadioNode-BR status"
git push
```

## Atualizações via ChatGPT

Depois que o repositório estiver criado e conectado, o Project Command Center pode
ser usado como fonte central. Alterações relevantes nos projetos devem atualizar
o estado do projeto e registrar uma entrada em `data/activity.json`.
