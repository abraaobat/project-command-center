# KES v1 — Pilot Plan

Plano de validação prática do Knowledge Extraction System.

## Estado atual — 2026-09-10

O KES deixou de ser apenas especificação: os dois pilotos agora têm fontes formalmente selecionadas e manifests versionados, e o repositório possui validação automática dos manifests contra o schema v1 e regras extras de privacidade/proveniência.

- **Pilot A:** `A Família Leitora`, de Sarah Mackenzie, disponível na Library privada do usuário. O Git guarda somente referência opaca/metadata; texto protegido e IDs privados não são versionados.
- **Pilot B:** canal público `The Tech Prepper`, inicialmente limitado a inventário + 5–10 vídeos diretamente ligados a comunicações/off-grid/RadioLink.
- **CI:** schema, unicidade, referências privadas e regras de manifesto passam por gate automático.

A extração das fontes e a geração dos primeiros Canonical Knowledge Packages ainda não foram marcadas como concluídas.

## Objetivo

Validar o mesmo modelo canônico em duas modalidades diferentes, sem depender de um domínio específico.

## Pilot A — Book / Document 🟡

Fonte selecionada: **A Família Leitora — Sarah Mackenzie**.

### Concluído

- [x] fonte real selecionada;
- [x] Source Manifest v1 criado;
- [x] referência privada opaca definida;
- [x] política impede commit de conteúdo protegido e IDs internos da Library;
- [x] manifesto validado em CI.

### Próximos entregáveis

- [ ] adquirir/ler a fonte no ambiente privado do pipeline;
- [ ] reconstruir estrutura de capítulos/seções;
- [ ] normalizar texto sem publicar o original no Git;
- [ ] gerar segmentos rastreáveis por capítulo/seção/página;
- [ ] resumo por capítulo;
- [ ] conceitos e glossário;
- [ ] Q&A de teste;
- [ ] relatório dos Quality Gates;
- [ ] índice retrieval-ready;
- [ ] primeiro Canonical Knowledge Package.

### Métricas

- cobertura de capítulos/seções;
- proporção de segmentos com âncora válida;
- número de gaps não explicados;
- duplicações técnicas;
- precisão de recuperação em perguntas de teste.

## Pilot B — Video / YouTube 🟡

Fonte selecionada: **The Tech Prepper**.

Primeira execução: inventário do canal + subconjunto de 5 a 10 vídeos diretamente relacionados ao tema de comunicações/off-grid e às referências do RadioLink. Expansão somente após o primeiro ciclo passar pelos Quality Gates.

### Concluído

- [x] canal real selecionado;
- [x] manifesto da coleção criado;
- [x] escopo inicial 5–10 vídeos definido;
- [x] regra de proveniência por URL/video ID/timestamp definida;
- [x] manifesto validado em CI.

### Próximos entregáveis

- [ ] inventário atual do canal;
- [ ] selecionar 5–10 vídeos do primeiro corpus;
- [ ] manifestos individuais;
- [ ] obter captions/transcrições por método permitido e registrar origem;
- [ ] normalizar transcrições;
- [ ] gerar segmentos com timestamps;
- [ ] usar evidência visual apenas quando necessária;
- [ ] mapa temático;
- [ ] conceitos/procedimentos/referências;
- [ ] relatório dos Quality Gates;
- [ ] índice retrieval-ready;
- [ ] primeiro Canonical Knowledge Package de vídeo.

### Métricas

- cobertura temporal da transcrição;
- proporção de segmentos com timestamps válidos;
- vídeos novos detectados em ingestão incremental;
- duplicações/republicações detectadas;
- precisão de recuperação em perguntas de teste.

## Acceptance criteria do KES v1

O padrão v1 pode ser marcado como **Validated** quando:

1. ambos os pilotos atingirem `PASS` ou `PASS_WITH_WARNINGS`;
2. 100% dos derivados avaliados tiverem `supported_by` válido;
3. nenhum segmento canônico estiver sem `source_id` e âncora;
4. reprocessar uma fonte não gerar duplicação lógica relevante;
5. a mesma camada de retrieval conseguir consultar os dois pilotos;
6. limitações conhecidas estiverem registradas.

## Sequência imediata

```text
Pilot A: source acquire -> extract -> normalize -> segment -> CKP -> gates
Pilot B: channel inventory -> 5–10 videos -> captions -> segment -> CKP -> gates
                         \___________________________/
                                      |
                           shared retrieval validation
```

## Próxima evolução após validação

- KES v1.1: automação de inventário e manifests;
- KES v1.2: normalizadores por modalidade;
- KES v1.3: gerador de CKP;
- KES v1.4: quality-gate runner;
- KES v2: ingestão contínua/incremental e integração direta com produtos como SatOps e Mãe Leitora.
