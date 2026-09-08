# Quality Gates v1

Verificações mínimas antes de um conteúdo ser promovido para a camada canônica do Knowledge Extraction System.

## G0 — Source identity

Obrigatório:

- `source_id` único e estável;
- tipo da fonte;
- título;
- autor/criador quando conhecido;
- idioma;
- referência canônica ou localização do original;
- versão do pipeline.

Falha em G0 bloqueia a ingestão canônica.

## G1 — Provenance

Todo segmento deve apontar para a fonte original e possuir âncora verificável.

- documento: capítulo/seção/página quando disponível;
- vídeo: `video_id` + timestamps.

Derivados devem declarar `supported_by`.

## G2 — Extraction coverage

Verificar se partes relevantes foram perdidas.

### Documentos

- capítulos esperados vs. extraídos;
- páginas vazias inesperadas;
- tabelas/figuras relevantes;
- notas e referências importantes.

### Vídeo

- duração da mídia vs. cobertura da transcrição;
- gaps anormais;
- ausência de trechos devido a legenda/ASR;
- conteúdo visual indispensável não representado.

Lacunas conhecidas podem ser aceitas se registradas no relatório.

## G3 — Structural integrity

- segmentos não devem quebrar unidades semânticas deliberadamente;
- ordem da fonte deve ser preservada;
- IDs não podem colidir;
- anchors devem ser monotônicos quando aplicável.

## G4 — Normalization safety

Normalização não pode introduzir reescrita silenciosa.

Correções de ASR, OCR ou encoding que sejam ambíguas devem permanecer sinalizadas ou ser mantidas como originalmente extraídas.

## G5 — Deduplication

Verificar:

- mesma fonte processada duas vezes;
- vídeos republicados;
- capítulos duplicados;
- segmentos substancialmente idênticos gerados por falha do pipeline.

Duplicação temática legítima não deve ser removida como se fosse duplicação técnica.

## G6 — Derived traceability

Resumos, conceitos, Q&A, procedimentos e mapas temáticos devem apontar para segmentos de origem.

Conteúdo derivado sem suporte explícito não entra na base canônica.

## G7 — Human readability

A representação normalizada deve ser legível por uma pessoa sem depender do índice semântico.

Isso serve como mecanismo de auditoria e recuperação independente de ferramentas de IA.

## G8 — Retrieval readiness

A fonte está pronta para indexação quando:

- segmentos possuem tamanho e contexto adequados;
- metadados essenciais estão presentes;
- IDs e anchors estão estáveis;
- não há dependência obrigatória de um único índice proprietário.

## Resultado do relatório

Cada ingestão deve receber um status:

- `PASS` — apta para camada canônica;
- `PASS_WITH_WARNINGS` — apta, com limitações documentadas;
- `FAIL` — requer correção antes da promoção.

Exemplo:

```text
G0 Source identity       PASS
G1 Provenance            PASS
G2 Extraction coverage   PASS_WITH_WARNINGS
G3 Structural integrity  PASS
G4 Normalization safety  PASS
G5 Deduplication         PASS
G6 Derived traceability  PASS
G7 Human readability     PASS
G8 Retrieval readiness   PASS

FINAL: PASS_WITH_WARNINGS
```
