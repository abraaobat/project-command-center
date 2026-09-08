# Project Command Center v4.1

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
python3 scripts/update_project.py radionode-br \
  --progress 30 \
  --current "RX AFSK validado em bancada" \
  --next "Validar TX AFSK" \
  --activity "Primeiro RX AFSK real decodificado."
```

Depois:

```bash
git add .
git commit -m "chore: update RadioNode-BR status"
git push
```

## Knowledge Extraction System

Os antigos fluxos separados de ingestão de livros/documentos e vídeo/YouTube foram consolidados no **Knowledge Extraction System (KES) v1**.

Documentação principal:

- `docs/knowledge-extraction/README.md`
- `docs/knowledge-extraction/BOOK_DOCUMENT_V1.md`
- `docs/knowledge-extraction/VIDEO_YOUTUBE_V1.md`
- `docs/knowledge-extraction/CANONICAL_PACKAGE_V1.md`
- `docs/knowledge-extraction/QUALITY_GATES_V1.md`
- `docs/knowledge-extraction/source-manifest.schema.json`
- `docs/knowledge-extraction/PILOT_PLAN_V1.md`

O KES é infraestrutura transversal para Mãe Leitora, SatOps, StudyOS e bases técnicas.

## Atualizações via ChatGPT

O Project Command Center é a fonte central de acompanhamento. Alterações relevantes
nos projetos devem atualizar o estado correspondente em `data/projects.json` e
registrar uma entrada em `data/activity.json`.
