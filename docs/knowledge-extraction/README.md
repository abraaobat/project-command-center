# Knowledge Extraction System (KES) v1

Sistema transversal para transformar fontes heterogêneas em pacotes de conhecimento rastreáveis, reutilizáveis e prontos para recuperação por busca/IA.

## Objetivo

Unificar os dois fluxos existentes de extração de conhecimento:

1. **Book & Document Ingestion** — livros, PDFs, EPUBs, DOCX, artigos e documentos.
2. **Video & YouTube Ingestion** — vídeos, playlists, canais, entrevistas e podcasts em vídeo.

Os dois módulos usam adaptadores de aquisição/extração diferentes, mas convergem para o mesmo **Canonical Knowledge Package**.

## Princípios

- **Provenance-first:** todo conhecimento deve apontar para sua origem.
- **Source-preserving:** o original nunca é substituído pelo derivado.
- **Modality adapters:** livro e vídeo têm pipelines próprios de extração, mas uma saída comum.
- **Stable anchors:** páginas/seções para documentos; timestamps/video IDs para vídeo.
- **No silent inference:** inferências, sínteses e correções devem ser distinguíveis do conteúdo da fonte.
- **Incremental ingestion:** novas edições, vídeos ou documentos podem ser adicionados sem reconstruir toda a base.
- **Idempotência:** reprocessar a mesma fonte não deve criar duplicatas lógicas.
- **Versionamento:** manifestos e pacotes carregam versão do pipeline.
- **Quality gates:** conteúdo não entra na camada canônica sem verificações mínimas.

## Arquitetura canônica

```text
SOURCE
  ↓
ACQUIRE
  ↓
EXTRACT
  ↓
NORMALIZE
  ↓
SEGMENT
  ↓
ENRICH
  ↓
VALIDATE
  ↓
PACKAGE
  ↓
INDEX / RETRIEVE
```

### 1. Source
Registrar identidade, autoria, origem, licença/acesso, idioma, data e checksum/IDs quando disponíveis.

### 2. Acquire
Preservar uma representação bruta ou referência estável para a fonte original.

### 3. Extract
Extrair texto, estrutura, metadados e elementos visuais relevantes usando o adaptador apropriado.

### 4. Normalize
Corrigir ruído técnico sem reescrever o conteúdo: encoding, quebras, headers repetidos, timestamps, espaços, ordem lógica e identificadores.

### 5. Segment
Criar unidades semânticas estáveis e citáveis.

### 6. Enrich
Gerar derivados úteis: resumos, conceitos, entidades, glossário, perguntas e respostas, procedimentos, referências cruzadas e tópicos.

### 7. Validate
Executar gates de completude, proveniência, duplicação, estrutura e coerência.

### 8. Package
Gerar o **Canonical Knowledge Package (CKP)**.

### 9. Index / Retrieve
Preparar índices para busca lexical, semântica, RAG e navegação humana.

## Estrutura recomendada por coleção

```text
knowledge/
├── manifests/
├── source/
├── raw/
├── normalized/
├── segments/
├── derived/
│   ├── summaries/
│   ├── concepts/
│   ├── glossary/
│   ├── qa/
│   └── references/
├── indexes/
└── reports/
```

## Identificadores

Cada fonte recebe um `source_id` estável. Cada segmento recebe um `segment_id` derivado do `source_id` + âncora estrutural.

Exemplos:

```text
book:willingham-2021:ch03:s02
video:UCxxxx:abc123:00h12m40s-00h16m05s
```

IDs não devem depender do título traduzido ou de resumos gerados.

## Módulos

- [`BOOK_DOCUMENT_V1.md`](BOOK_DOCUMENT_V1.md)
- [`VIDEO_YOUTUBE_V1.md`](VIDEO_YOUTUBE_V1.md)
- [`CANONICAL_PACKAGE_V1.md`](CANONICAL_PACKAGE_V1.md)
- [`QUALITY_GATES_V1.md`](QUALITY_GATES_V1.md)

## Pilotos de validação

O v1 será considerado validado após dois pilotos equivalentes:

- 1 livro/documento completo;
- 1 canal ou playlist de vídeo representativa.

Os pilotos devem medir: cobertura, rastreabilidade, duplicação, qualidade dos segmentos, utilidade dos derivados e capacidade de recuperação.

## Relação com os projetos

O KES é infraestrutura transversal. Exemplos de consumidores:

- Mãe Leitora — Adriana Muniz;
- SatOps / AI Search / AI Tutor;
- StudyOS;
- bases técnicas de RadioLink, RadioNode-BR e firmware;
- pesquisa e documentação futura.
