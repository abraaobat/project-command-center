# Project Command Center v4.4

Painel mestre vivo para acompanhar projetos, progresso estimado, fase atual, próximo marco, relações entre iniciativas e atividade recente.

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

- `data/projects.json` — estado atual, relações pai/filho e runtimes dos projetos.
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

## Relações entre projetos

A partir da v4.4, o dashboard pode representar iniciativas subordinadas por meio de `parentId` e `relationshipLabel` em `data/projects.json`.

Exemplo conceitual:

```text
StudyOS
├── Abe Joshua — Estudos  → primeiro aluno real / Learning Plan
└── GameDev 12            → Learning Program
```

As iniciativas filhas continuam visíveis como projetos próprios para acompanhamento operacional, mas o dashboard também mostra explicitamente sua relação com o projeto-pai.

## StudyOS Local Pilot

O StudyOS passa a ser acompanhado como produto-pai do piloto educacional real.

Estado documentado:

- Project Command Center permanece em `http://localhost:8787`;
- StudyOS Local foi reservado para `http://localhost:8788`;
- o runtime `8788` ainda não é considerado operacional até implementação e validação reais;
- Abe Joshua — Estudos é o primeiro Learning Plan real do StudyOS;
- GameDev 12 é o primeiro Learning Program do StudyOS;
- o próximo marco é validar sincronização entre dashboard do orientador no Mac e dashboard do estudante no tablet.

Use o filtro **StudyOS** no painel para visualizar o projeto-pai e suas iniciativas relacionadas.

O card de um projeto pode declarar um bloco `runtime`:

```json
{
  "runtime": {
    "label": "StudyOS Local",
    "url": "http://localhost:8788",
    "status": "planned",
    "note": "Runtime local ainda não implementado."
  }
}
```

Quando o runtime for validado, `status` pode ser promovido para `available`; então o dashboard passa a apresentar um link de abertura.

Documentação específica: `docs/studyos-integration.md`.

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

O Project Command Center é a fonte central de acompanhamento. Alterações relevantes nos projetos devem atualizar o estado correspondente em `data/projects.json` e registrar uma entrada em `data/activity.json`.

O dashboard não deve declarar runtime, deploy, teste ou integração como operacional antes de validação real.
