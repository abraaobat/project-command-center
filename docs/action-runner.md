# Project Command Center — Action Runner

## Objetivo

Transformar a caixa de ação no rodapé de cada card em um disparador real de trabalho.

Ao marcar a caixa:

1. o dashboard envia `projectId` para `POST /api/actions/start`;
2. o servidor local resolve a fonte canônica em `data/status-sources.json`;
3. o workspace é localizado em `~/Projects/<repo>` por padrão;
4. quando existe um repositório local e o Codex CLI está disponível, uma execução não interativa é iniciada;
5. o dashboard acompanha `queued`, `running`, `done`, `needs_user`, `blocked` e `failed`;
6. quando a tarefa depende de intervenção humana, o macOS recebe uma notificação.

Projetos filhos herdam o repositório do projeto pai quando não possuem fonte própria. Isso permite, por exemplo, que frentes do StudyOS usem o monorepo `saas-engineering-platform`.

## Política de autonomia v1

O executor usa o Codex CLI com sandbox `workspace-write` e política de aprovação `never`. O prompt determina que o agente:

- avance o máximo possível sem parar para atualizações de progresso;
- edite apenas o workspace do projeto;
- preserve trabalho não relacionado já presente;
- rode testes e validações pertinentes;
- não faça `push`, deploy, publicação, pagamento, flash de hardware ou outra ação externa irreversível;
- complete toda preparação possível antes de solicitar intervenção humana.

A resposta final deve terminar com:

```text
PCC_STATUS: DONE|NEEDS_USER|BLOCKED|FAILED
PCC_USER_ACTION: <instrução objetiva ou NONE>
PCC_SUMMARY: <resumo objetivo>
```

Esses marcadores alimentam o estado visual do card e a decisão de notificar o usuário.

## Notificações

O backend usa o Notification Center do macOS por meio de `osascript`.

Por padrão são notificadas situações `needs_user`, `blocked` e `failed`. Para também notificar conclusão:

```bash
export PCC_NOTIFY_DONE=1
```

Para desativar notificações:

```bash
export PCC_NOTIFICATIONS=0
```

## Segurança

O servidor deixa de usar `python3 -m http.server` e passa a usar `scripts/command_center_server.py`.

O bind padrão é somente loopback:

```text
127.0.0.1:8787
```

Isso é obrigatório porque o endpoint local pode iniciar um agente que altera arquivos do workspace.

O browser envia apenas o `projectId`; a tarefa é construída a partir dos dados canônicos do dashboard. Não há endpoint de shell arbitrário.

## Configuração

| Variável | Padrão | Uso |
| --- | --- | --- |
| `PCC_PORT` | `8787` | porta do dashboard |
| `PCC_BIND` | `127.0.0.1` | endereço local |
| `PCC_PROJECTS_DIR` | `~/Projects` | raiz dos repositórios |
| `PCC_CODEX_BIN` | auto | caminho explícito para `codex` |
| `PCC_JOB_TIMEOUT_SECONDS` | `7200` | timeout de uma execução |
| `PCC_NOTIFICATIONS` | `1` | notificações de bloqueio/ação humana |
| `PCC_NOTIFY_DONE` | `0` | notificar tarefas concluídas |
| `PCC_JOB_LOG_DIR` | `/tmp/project-command-center-jobs` | logs e resposta final |

O backend procura `codex` no `PATH`; se não encontrar, consulta o login shell do macOS. Isso ajuda quando o serviço é iniciado pelo `launchd`.

## Estado e logs

O histórico local fica em:

```text
data/runtime-action-jobs.json
```

Esse arquivo é runtime-only e fica fora do Git.

Logs completos ficam por padrão em:

```text
/tmp/project-command-center-jobs/
```

Se o serviço reiniciar durante uma tarefa, jobs `queued` ou `running` são marcados como interrompidos. O usuário pode revisar o workspace e disparar novamente a ação.

## UX

A caixa deixa de ser um simples valor em `localStorage` e passa a exibir:

- **PRONTO PARA INICIAR**
- **AGUARDANDO**
- **CHATGPT/CODEX EM EXECUÇÃO**
- **CONCLUÍDO**
- **PRECISA DE VOCÊ**
- **BLOQUEADO**
- **FALHOU**

Depois de um estado terminal, desmarcar a caixa descarta visualmente aquele resultado no browser. Marcar novamente dispara uma nova execução da mesma ação.

## Ativação após atualizar o repositório

Como a versão anterior do serviço executa `python3 -m http.server`, a primeira adoção exige um restart do job `launchd` depois que o código chegar ao `main`:

```bash
cd ~/Projects/project-command-center
git pull --ff-only origin main
launchctl kickstart -k gui/$(id -u)/com.abraaobat.project-command-center
```

Depois disso, o dashboard continua em `http://localhost:8787`.

## Próximas evoluções

- auto-commit e auto-push controlados por política;
- fila por prioridade;
- aprovação pelo próprio dashboard para operações externas;
- executor diferente por tipo de projeto;
- notificação também para iPhone/ChatGPT;
- histórico detalhado e botão para abrir log;
- retomada automática depois de uma ação humana.
