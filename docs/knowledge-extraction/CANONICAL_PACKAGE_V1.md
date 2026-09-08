# Canonical Knowledge Package (CKP) v1

Formato comum de saída para todas as modalidades do Knowledge Extraction System.

## Objetivo

Permitir que conteúdo vindo de livro, documento, vídeo ou canal seja consumido pelos mesmos sistemas de busca, RAG, geração de conteúdo e revisão humana.

## Componentes obrigatórios

### 1. Source manifest
Registro de identidade e proveniência da fonte.

Campos mínimos:

```json
{
  "schema_version": "kes-source-1",
  "source_id": "...",
  "source_type": "book|document|video|playlist|channel",
  "title": "...",
  "creator": ["..."],
  "language": "pt-BR",
  "canonical_ref": "...",
  "acquired_at": "ISO-8601",
  "pipeline_version": "KES-1",
  "extraction_method": "native-text|captions|asr|mixed",
  "notes": []
}
```

Campos adicionais devem ser mantidos quando úteis, sem remover os mínimos.

### 2. Normalized source
Representação legível da fonte com âncoras preservadas.

- Documento: páginas, capítulos e seções.
- Vídeo: timestamps, interlocutores/capítulos quando disponíveis.

### 3. Segment store
Um registro por unidade semântica.

Exemplo conceitual:

```json
{
  "segment_id": "book:source:ch03:s02",
  "source_id": "book:source",
  "anchor": {
    "chapter": "3",
    "section": "2",
    "page_start": 41,
    "page_end": 44
  },
  "text": "...",
  "topics": ["..."],
  "derived": false
}
```

Para vídeo:

```json
{
  "segment_id": "video:channel:id:00h12m40s-00h16m05s",
  "source_id": "video:channel:id",
  "anchor": {
    "start_seconds": 760,
    "end_seconds": 965
  },
  "text": "...",
  "topics": ["..."],
  "derived": false
}
```

### 4. Derived knowledge
Toda síntese deve declarar sua origem.

Exemplo:

```json
{
  "knowledge_id": "concept:phonemic-awareness:001",
  "type": "concept",
  "title": "Consciência fonêmica",
  "content": "...",
  "supported_by": [
    "book:source:ch03:s02",
    "video:channel:id:00h12m40s-00h16m05s"
  ],
  "derived": true
}
```

## Tipos derivados padronizados

- `summary`
- `concept`
- `definition`
- `procedure`
- `claim`
- `evidence`
- `example`
- `qa`
- `glossary_term`
- `reference`
- `topic_map`
- `cross_source_relation`

## Proveniência

A regra central do CKP é:

> nenhuma afirmação derivada deve ficar órfã de uma fonte rastreável.

Sínteses multi-fonte podem apontar para múltiplos segmentos.

## Camadas de confiança

Recomenda-se registrar:

- `source_fidelity`: qualidade da extração da fonte;
- `anchor_confidence`: confiança no vínculo com página/timestamp;
- `derived_confidence`: confiança da síntese/enriquecimento.

Valores sugeridos: `high`, `medium`, `low` acompanhados de notas quando necessário.

## Índices

O CKP pode produzir múltiplos índices sem alterar os dados canônicos:

- índice lexical;
- índice semântico/vector;
- índice por tópico;
- índice por autor/canal;
- índice cronológico;
- grafo de conceitos/relações.

Índices são reconstruíveis. O pacote canônico e os manifestos são a fonte de verdade.

## Versionamento

Mudanças incompatíveis no formato exigem nova `schema_version`. Mudanças de pipeline que não alteram o schema devem atualizar `pipeline_version` e o relatório de ingestão.
