# Video & YouTube Ingestion v1

Adaptador do Knowledge Extraction System para vídeos individuais, playlists, canais, entrevistas, aulas e podcasts em vídeo.

## Objetivo

Converter conteúdo audiovisual em conhecimento estruturado sem reduzir o vídeo a uma transcrição solta. O pipeline deve preservar contexto, timestamps, autoria/canal, ordem do discurso e elementos visuais relevantes.

## Escopos suportados

- vídeo individual;
- playlist;
- canal completo;
- janela temporal de um canal;
- série temática;
- podcast/entrevista em vídeo.

## Pipeline

### V1 — Inventory
Para canal/playlist, criar primeiro um inventário antes da ingestão profunda.

Registrar por vídeo:

- `video_id`;
- URL canônica;
- canal/autor;
- título;
- data de publicação;
- duração;
- playlist/série quando aplicável;
- idioma;
- descrição;
- disponibilidade de capítulos/legendas;
- estado de ingestão.

O inventário permite ingestão incremental e evita reprocessamento desnecessário.

### V2 — Acquire metadata
Preservar metadados originais antes da geração de resumos ou classificação temática.

### V3 — Acquire transcript
Ordem de preferência:

1. legenda/transcrição oficial do criador;
2. legenda disponibilizada pela plataforma;
3. transcrição fornecida junto à fonte;
4. ASR como fallback.

A origem da transcrição deve ser registrada no manifesto.

### V4 — Visual evidence
A transcrição não é suficiente quando o vídeo depende de demonstrações, slides, diagramas, telas, gráficos ou objetos mostrados visualmente.

Nesses casos, registrar momentos visuais relevantes com timestamp e descrição objetiva. Capturas devem ser seletivas, não uma extração quadro a quadro indiscriminada.

### V5 — Normalize
Normalizar:

- pontuação técnica quando necessária para legibilidade;
- repetições e artefatos claros de ASR;
- identificação de interlocutores quando possível;
- timestamps;
- capítulos fornecidos pelo criador.

Não remover hesitações ou repetições quando elas alterarem o sentido, grau de certeza ou intenção do falante.

### V6 — Segment
Priorizar segmentação semântica, não blocos fixos de tempo.

Fronteiras preferenciais:

1. capítulos oficiais;
2. mudança clara de tópico;
3. pergunta/resposta;
4. demonstração/procedimento;
5. argumento/exemplo;
6. fallback temporal.

Cada segmento deve ter `start_time` e `end_time`.

Exemplo:

```text
video:UCxxxx:abc123:00h12m40s-00h16m05s
```

### V7 — Enrich
Derivados possíveis:

- resumo por vídeo;
- resumo por capítulo/bloco;
- conceitos-chave;
- afirmações e ressalvas;
- procedimentos passo a passo;
- ferramentas/produtos/projetos citados;
- perguntas e respostas;
- referências externas mencionadas;
- glossário;
- relações entre vídeos;
- tópicos recorrentes no canal.

Todo derivado deve manter links para `segment_id` de origem.

### V8 — Channel synthesis
Para canais e playlists, gerar uma camada adicional após a ingestão individual:

- mapa temático do canal;
- séries recorrentes;
- evolução de posições/ideias ao longo do tempo;
- conceitos centrais;
- vídeos fundamentais por tópico;
- duplicações e atualizações de conteúdo;
- contradições ou mudanças de recomendação quando existirem.

Nunca substituir a camada por vídeo por uma síntese global sem rastreabilidade.

### V9 — Validate
Aplicar `QUALITY_GATES_V1.md`.

### V10 — Package
Gerar o Canonical Knowledge Package.

## Saídas mínimas

Para vídeo individual:

```text
manifests/<video_id>.json
normalized/<video_id>.md
segments/<video_id>.jsonl
derived/summaries/<video_id>.md
derived/concepts/<video_id>.json
reports/<video_id>-ingestion.md
```

Para canal/playlist:

```text
manifests/<collection_id>.json
indexes/<collection_id>-inventory.jsonl
derived/<collection_id>-topic-map.md
derived/<collection_id>-canonical-index.md
reports/<collection_id>-ingestion.md
```

## Política incremental para canais

Uma nova execução deve:

1. atualizar o inventário;
2. detectar vídeos novos/alterados/indisponíveis;
3. processar somente o delta necessário;
4. atualizar sínteses globais afetadas;
5. preservar IDs de segmentos antigos quando o conteúdo não mudou.

## Critérios de conclusão

Uma ingestão de vídeo está concluída quando:

- metadados e transcript source estão registrados;
- segmentos têm timestamps válidos;
- elementos visuais essenciais foram representados;
- derivados apontam para segmentos de origem;
- limitações de ASR/legenda estão registradas;
- o relatório de qualidade foi gerado.

Uma ingestão de canal/playlist exige ainda inventário consistente e síntese temática rastreável.
