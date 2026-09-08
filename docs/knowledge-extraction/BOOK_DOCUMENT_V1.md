# Book & Document Ingestion v1

Adaptador do Knowledge Extraction System para livros, PDFs, EPUBs, DOCX, artigos e documentos estruturados.

## Ordem de preferência de extração

1. Texto e estrutura nativos do arquivo.
2. Camada de texto embutida no PDF.
3. Extração por página/bloco com reconstrução de leitura.
4. OCR apenas quando não houver texto utilizável.

A regra evita OCR desnecessário e preserva melhor estrutura, acentos e referências.

## Pipeline

### B1 — Register
Criar manifesto da fonte com título, autor, edição, idioma, formato, origem, data de aquisição e identificador/checksum quando disponível.

### B2 — Preserve source
Manter o original intacto em `source/` ou registrar uma referência estável para ele.

### B3 — Extract structure
Identificar, quando existirem:

- capa e metadados editoriais;
- sumário;
- partes, capítulos e seções;
- cabeçalhos e rodapés;
- notas de rodapé/fim;
- figuras e legendas;
- tabelas;
- caixas laterais;
- referências/bibliografia;
- índice remissivo.

### B4 — Normalize
Remover ruído técnico sem alterar o sentido do texto. Exemplos: headers repetitivos, quebras artificiais de linha, hifenação de fim de linha e artefatos de conversão.

Toda alteração que possa mudar conteúdo deve ser evitada ou registrada.

### B5 — Anchor
A unidade mínima de rastreabilidade deve preservar:

- página física ou lógica quando disponível;
- capítulo/seção;
- posição relativa no documento.

### B6 — Segment
Priorizar fronteiras editoriais reais. Ordem sugerida:

1. capítulo;
2. seção/subseção;
3. bloco semântico;
4. fallback por tamanho somente quando necessário.

Não cortar listas, tabelas, exemplos ou argumentos no meio quando for evitável.

### B7 — Enrich
Derivados permitidos:

- resumo por capítulo/seção;
- conceitos-chave;
- definições;
- entidades/pessoas/obras citadas;
- procedimentos/métodos;
- argumentos e evidências;
- glossário;
- Q&A;
- relações entre capítulos;
- referências externas.

Conteúdo derivado deve apontar para os `segment_id` que o sustentam.

### B8 — Validate
Aplicar `QUALITY_GATES_V1.md`.

### B9 — Package
Gerar o Canonical Knowledge Package.

## Saídas mínimas

```text
manifests/<source_id>.json
normalized/<source_id>.md
segments/<source_id>.jsonl
derived/summaries/<source_id>.md
derived/concepts/<source_id>.json
reports/<source_id>-ingestion.md
```

## Regras para imagens e tabelas

- Extrair apenas quando carregarem informação relevante.
- Manter legenda, página e relação com o texto.
- Tabelas devem preservar cabeçalhos e unidade semântica.
- Se a representação textual perder informação, registrar a limitação no relatório.

## Critérios de conclusão

Uma ingestão de livro/documento está concluída quando:

- a estrutura principal está reconstruída;
- todos os segmentos possuem âncora rastreável;
- os derivados apontam para segmentos de origem;
- não existem lacunas relevantes sem justificativa;
- o relatório de qualidade foi gerado.
