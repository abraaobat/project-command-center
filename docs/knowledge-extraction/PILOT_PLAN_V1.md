# KES v1 — Pilot Plan

Plano de validação prática do Knowledge Extraction System.

## Objetivo

Validar o mesmo modelo canônico em duas modalidades diferentes, sem depender de um domínio específico.

## Pilot A — Book / Document

Fonte preferencial: um livro já usado na Knowledge Base Mãe Leitora, idealmente um dos títulos-base do projeto.

### Entregáveis

- manifesto da fonte;
- estrutura reconstruída;
- texto normalizado;
- segmentos rastreáveis por capítulo/seção/página;
- resumo por capítulo;
- conceitos e glossário;
- Q&A de teste;
- relatório dos Quality Gates;
- índice retrieval-ready.

### Métricas

- cobertura de capítulos/seções;
- proporção de segmentos com âncora válida;
- número de gaps não explicados;
- duplicações técnicas;
- precisão de recuperação em um conjunto de perguntas de teste.

## Pilot B — Video / YouTube

Fonte preferencial: um canal já relevante aos projetos técnicos, com **The Tech Prepper** como candidato inicial por já ter sido usado como referência arquitetural em RadioLink.

Primeira execução recomendada: inventário do canal + subconjunto de 5 a 10 vídeos diretamente relacionados ao tema de interesse. Depois, expandir incrementalmente.

### Entregáveis

- manifesto da coleção/canal;
- inventário de vídeos;
- manifestos individuais;
- transcrições normalizadas com origem registrada;
- segmentos com timestamps;
- evidências visuais apenas quando necessárias;
- mapa temático;
- conceitos/procedimentos/referências;
- relatório dos Quality Gates;
- índice retrieval-ready.

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

## Próxima evolução após validação

- KES v1.1: automação de inventário e manifests;
- KES v1.2: normalizadores por modalidade;
- KES v1.3: gerador de CKP;
- KES v1.4: quality-gate runner;
- KES v2: ingestão contínua/incremental e integração direta com produtos como SatOps e Mãe Leitora.
