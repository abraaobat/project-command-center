# NanoVNA Modern

Projeto para evoluir o NanoVNA-H4/ZN401 em uma plataforma de medição RF moderna, configurável e extensível, mantendo o núcleo de medição confiável do NanoVNA-D e adicionando uma nova experiência local, integração USB/web e um coprocessador ESP32-S3 opcional.

## Escopo

O projeto será organizado em quatro camadas:

1. **NanoVNA Firmware** — fork do `DiSlord/NanoVNA-D`, inicialmente sem alterar o motor RF/DSP.
2. **Modern UI** — interface redesenhada para 480x320, painel modular, presets, gráficos aprimorados e fluxo de calibração moderno.
3. **USB/Web Platform** — bridge local via USB-C, API/WebSocket e dashboard web/PWA para desktop, tablet e celular.
4. **SmartLink ESP32-S3** — gateway USB Host + Wi‑Fi/BLE + PSRAM/microSD para uso sem computador, histórico e processamento auxiliar.

## Hardware de referência inicial

- ZeenKo ZN401 / NanoVNA-H4
- HW `4.7_ZK`
- MCU STM32F303xC / Cortex-M4F
- Display 480x320
- NanoVNA-D 1.2.44 `[x401]` atualmente instalado
- TXCO 26 MHz
- microSD funcional

## Princípios

- Preservar primeiro a precisão e estabilidade de medição.
- Nunca acoplar UI, IA ou conectividade diretamente à cadeia crítica de RF sem necessidade.
- Evolução incremental: baseline reproduzível → UI → USB/web → ESP32 → inteligência.
- Interface local deve continuar plenamente funcional sem microSD, rede ou ESP32.
- microSD é armazenamento persistente, não substituto de RAM.
- Recursos avançados devem ser opcionais e degradar de forma segura.

## Pilares funcionais

### Modern UI

Abas de alto nível propostas:

`MEASURE | DISPLAY | MARKERS | CAL | PRESETS | SETUP`

A linguagem visual será inspirada em instrumentos profissionais modernos: fundo escuro, cards grandes, hierarquia clara, seleção em azul e áreas de toque amplas. Não será uma cópia visual de produtos Blackmagic.

### Painel modular

Widgets/overlays poderão ser habilitados ou desabilitados conforme a tarefa, incluindo:

- frequência de marker;
- Start/Stop ou Center/Span;
- SWR;
- Return Loss;
- fase;
- impedância R+jX;
- magnitude;
- Group Delay;
- estado de calibração;
- bateria;
- sweep points;
- averaging/smoothing;
- trace/channel;
- estado SD/USB.

Perfis sugeridos: `Minimal`, `Antenna`, `Filter`, `Cable`, `Lab`, `Studio`.

### Gráficos

Modos planejados:

- `Classic` — máxima leveza;
- `Enhanced` — melhor grade, traço e markers;
- `Studio` — glow leve, persistência limitada e visual premium;
- `Diagnostic` — máxima densidade de informação.

Efeitos devem ser implementados com desenho incremental, primitivas e buffers compactos, evitando framebuffer integral.

### microSD Extensions

O cartão poderá armazenar:

- presets e dashboards;
- temas e traduções;
- scripts `.cmd` e automações seguras;
- calibrações;
- arquivos S1P/S2P;
- histórico de medições;
- screenshots;
- modelos/assinaturas compactas para análise assistida.

### USB/Web

O NanoVNA expõe os dados pelo USB; um `NanoVNA Bridge` no computador converte o protocolo serial em API moderna:

- REST para estado/configuração;
- WebSocket para sweep ao vivo;
- dashboard web responsivo/PWA;
- acesso pela LAN a partir de celular/tablet.

### SmartLink ESP32-S3

O ESP32-S3 atuará como coprocessador e gateway:

`NanoVNA USB Device → ESP32-S3 USB Host → Wi‑Fi/BLE/WebSocket → Browser`

Funções planejadas:

- USB Host CDC;
- Wi‑Fi AP/STA;
- BLE opcional;
- servidor web local;
- PSRAM para histórico e processamento;
- microSD adicional opcional;
- Smart Analysis;
- TinyML experimental;
- ponte para IA externa.

## Inteligência

A prioridade será **Smart Assist determinístico** antes de redes neurais:

- detecção de ressonância;
- SWR mínimo;
- largura de banda;
- Q;
- insertion loss;
- detecção de picos/notches;
- estimativa de falhas de cabo/TDR;
- comparação entre medições;
- alertas de deslocamento de resposta.

TinyML e IA externa serão camadas posteriores e nunca requisito para operação básica.

## Estratégia de repositórios

O projeto será mantido como um produto guarda-chuva chamado **NanoVNA Modern**. A estratégia preferida é:

- `abraaobat/nanovna-modern` — repositório principal da plataforma/documentação;
- fork do `DiSlord/NanoVNA-D` ou subtree/submodule claramente rastreado para o firmware;
- componentes `bridge`, `web` e `smartlink` no mesmo repositório enquanto a arquitetura amadurece.

A decisão final de empacotamento será registrada em ADR antes da primeira implementação.

## Estado atual

**Status:** planejamento técnico / hardware fingerprint em andamento.

**Próximo gate:** confirmar enumeração USB/DFU do ZN401 4.7_ZK e obter um build limpo/reproduzível do upstream para F303 antes de qualquer alteração funcional.
