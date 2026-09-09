# Project Command Center v4.5

Painel mestre vivo para acompanhar projetos, progresso estimado, fase atual, próximo marco, relações entre iniciativas, runtimes e atividade recente.

## Uso diário no Mac

Dê duplo clique em:

`Abrir Dashboard.command`

O painel abre em:

`http://localhost:8787`

Enquanto estiver aberto:
- `git pull --ff-only` roda aproximadamente a cada 60 segundos;
- `scripts/sync_status_sources.py` consulta as fontes machine-readable configuradas em `data/status-sources.json`;
- a visão gerada localmente fica em `data/runtime-projects.json` e `data/runtime-activity.json`;
- esses arquivos runtime são ignorados pelo Git e não bloqueiam futuros `git pull`;
- o navegador recarrega a visão a cada 10 segundos;
- se o Auto Status Sync falhar, o dashboard usa `data/projects.json` e `data/activity.json` como fallback seguro.

Pré-requisitos para sincronização remota: `git`, GitHub CLI (`gh`) e autenticação do `gh`.

```bash
brew install gh
gh auth login
```

## Auto Status Sync v4.5

Cada projeto pode publicar um pequeno arquivo JSON no próprio repositório. O Project Command Center busca esse arquivo e aplica somente campos de portfólio permitidos ao card correspondente.

Fluxo:

```text
Projeto de origem
└── project-status.json
            ↓
GitHub / gh api
            ↓
Project Command Center
└── scripts/sync_status_sources.py
            ↓
   runtime-projects.json
            ↓
      dashboard :8787
```

Configuração das fontes:

`data/status-sources.json`

### Fontes automáticas atuais

1. `studyos` → `abraaobat/saas-engineering-platform/products/studyos/project-status.json`
2. `radiolink-mobile` → `abraaobat/radiolink-mobile/project-status.json`
3. `radionode-br` → `abraaobat/radionode-br/project-status.json`
4. `esp32-adblocker` → `abraaobat/ESP32_AdBlocker/project-status.json`
5. `satops` → `abraaobat/saas-engineering-platform/products/satops/project-status.json`
6. `saas-platform` → `abraaobat/saas-engineering-platform/project-status.json`
7. `knowledge-extraction-system` → `abraaobat/project-command-center/data/status-contracts/knowledge-extraction-system.json`

Exemplo de fonte:

```json
{
  "projectId": "studyos",
  "repository": "abraaobat/saas-engineering-platform",
  "ref": "main",
  "path": "products/studyos/project-status.json",
  "enabled": true
}
```

Campos que uma fonte externa pode atualizar:
- `status` / `statusClass`;
- `progress`;
- `roadmap`;
- `current`;
- `architecture`;
- `next`;
- `action`;
- `subprojects`;
- `runtime`;
- uma entrada resumida opcional de `activity`.

O sincronizador não aceita que a fonte externa substitua identidade do projeto, categoria, prioridade, relações pai/filho ou outros campos fora dessa allowlist.

## Teste manual do sincronizador

```bash
python3 scripts/sync_status_sources.py
```

Resultado esperado com as sete fontes principais ativas:

```text
Auto Status Sync: 7 fonte(s) OK, 0 falha(s).
Gerado: data/runtime-projects.json
```

Para tratar qualquer fonte indisponível como erro:

```bash
python3 scripts/sync_status_sources.py --strict
```

O log do launcher fica em:

`/tmp/project-command-center-sync.log`

## Fonte de dados e compatibilidade

Arquivos rastreados pelo Git continuam existindo como catálogo/fallback:
- `data/projects.json` — estado-base, identidade dos projetos, relações e runtimes;
- `data/activity.json` — histórico-base;
- `data/knowledge-extraction-projects.json` — projetos do KES;
- `scripts/update_project.py` — atualização manual opcional para projetos ainda não migrados.

Arquivos locais gerados automaticamente:
- `data/runtime-projects.json`;
- `data/runtime-activity.json`.

A migração para fontes próprias é incremental. Projetos sem contrato machine-readable continuam funcionando pelo fallback estático.

## Relações entre projetos

O dashboard representa iniciativas subordinadas por meio de `parentId` e `relationshipLabel`.

```text
StudyOS
├── Abe Joshua — Estudos  → primeiro aluno real / Learning Plan
├── GameDev 12            → Learning Program
└── Premiere Mobile       → Learning Program
```

## StudyOS

Estado atual do piloto:
- runtime local `http://localhost:8788/orientador` operacional;
- sincronização Mac ↔ tablet validada;
- notificações do Orientador validadas;
- presença/last-seen validada no tablet real;
- Álgebra e Premiere Mobile integrados;
- próximo marco: HTTPS / secure origin e localização precisa com consentimento explícito.

O Project Command Center guarda apenas metadados de projeto. Presença ao vivo, rotina detalhada, notas, localização e demais dados privados permanecem exclusivamente no StudyOS.

Documentação específica: `docs/studyos-integration.md`.

## Atualização manual ainda disponível

Para projetos que ainda não publicam status próprio:

```bash
python3 scripts/update_project.py aprsd-smsbr \
  --progress 20 \
  --current "Novo marco validado" \
  --next "Próximo gate" \
  --activity "Resumo da mudança."
```

Depois faça commit/push normalmente.

## Regra operacional

O dashboard nunca deve declarar runtime, deploy, teste ou integração como operacional antes de validação real. Auto Status Sync reduz trabalho manual, mas não substitui essa regra de evidência.
