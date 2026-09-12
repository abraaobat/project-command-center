# NanoVNA Modern — Architecture

## System view

```text
                       ┌───────────────────────────────┐
                       │      Web Dashboard / PWA      │
                       │ Desktop • Tablet • Smartphone │
                       └──────────────┬────────────────┘
                                      │ REST / WebSocket
                         ┌────────────┴────────────┐
                         │                         │
                ┌────────▼────────┐       ┌────────▼─────────┐
                │ NanoVNA Bridge  │       │ SmartLink ESP32  │
                │ macOS/Linux/Win │       │ ESP32-S3 N16R8   │
                └────────┬────────┘       └────────┬─────────┘
                         │ USB CDC/serial          │ USB Host CDC
                         └────────────┬────────────┘
                                      │
                              ┌───────▼────────┐
                              │  NanoVNA-H4    │
                              │ ZN401 4.7_ZK   │
                              ├────────────────┤
                              │ RF / DSP       │
                              │ Calibration    │
                              │ Sweep          │
                              │ Modern UI      │
                              │ microSD        │
                              └────────────────┘
```

## Architectural rule

A cadeia crítica `RF → aquisição → DSP → calibração → sweep` deve permanecer desacoplada da UI moderna, web, Wi‑Fi, ML e IA externa. A primeira meta do fork é preservar comportamento do upstream e introduzir novas camadas ao redor do motor existente.

## Layer 1 — Measurement Core

Responsabilidade do STM32/NanoVNA:

- geração e aquisição RF;
- S11/S21;
- calibração;
- sweep;
- dados complexos;
- markers fundamentais;
- operação standalone.

Regra: nenhuma dependência de rede/cloud para medição básica.

## Layer 2 — Local Modern UI

Componentes planejados:

```text
ui/
├── theme
├── navigation
├── widgets
├── overlays
├── layouts
├── presets
├── screens
└── renderer
```

O renderer deve priorizar desenho imediato e redraw parcial. Não assumir framebuffer RGB565 completo, pois 480x320x2 exigiria ~300 KiB.

### Widget model

```text
Widget
├── id
├── enabled
├── priority
├── slot
├── formatter
├── data_source
└── render()
```

Exemplos: `SWR`, `IMPEDANCE`, `MARKER_FREQ`, `RETURN_LOSS`, `PHASE`, `CAL_STATUS`, `BATTERY`, `SWEEP_RANGE`.

## Layer 3 — SD Extension Store

Estrutura proposta:

```text
/NANOVNA/
├── profiles/
├── dashboards/
├── themes/
├── scripts/
├── measurements/
├── calibrations/
├── screenshots/
├── languages/
└── analysis/
```

O SD não executará código nativo arbitrário. Extensões devem usar formatos declarativos ou scripts limitados a comandos permitidos.

## Layer 4 — USB Protocol

Criar uma camada de compatibilidade acima do console/protocolo já exposto pelo firmware.

Entidades normalizadas:

```text
DeviceInfo
SweepConfig
SweepFrame
ComplexPoint
Trace
Marker
CalibrationState
Preset
MeasurementSession
```

O protocolo web não deve expor detalhes de transporte serial diretamente.

## Layer 5 — NanoVNA Bridge

Serviço local responsável por:

- descobrir porta USB;
- abrir/reabrir sessão;
- serializar comandos;
- coletar sweep binário/textual;
- normalizar dados;
- expor REST/WebSocket;
- registrar diagnósticos.

A implementação inicial deve ser CLI-first e headless para facilitar testes.

## Layer 6 — Web Dashboard

Aplicação responsiva independente do transporte físico.

```text
Browser
  ↓
Web client
  ↓
API client
  ↓
REST + WebSocket
  ↓
Bridge ou SmartLink
```

A mesma UI deve funcionar contra bridge desktop e ESP32 quando possível.

## Layer 7 — SmartLink ESP32-S3

Responsabilidades:

- USB Host para NanoVNA;
- Wi‑Fi AP/STA;
- mDNS;
- WebSocket/REST;
- buffers em PSRAM;
- histórico/cache;
- microSD opcional;
- Smart Analysis;
- OTA do próprio ESP32.

Não deve assumir funções de RF/calibração do NanoVNA.

## Layer 8 — Analysis Engine

Ordem de implementação:

1. matemática/DSP determinístico;
2. heurísticas com explicação;
3. TinyML experimental;
4. IA externa opcional.

Toda recomendação deve manter dados observados, regra/modelo usado e grau de confiança quando aplicável.

## Power architecture for SmartLink

O SmartLink não deve ligar D+/D- e VBUS de forma improvisada. O hardware precisa controlar VBUS e impedir backfeed.

```text
5V input
  ↓
protected regulator / load switch
  ↓
VBUS controlled
  ↓
NanoVNA USB-C

ESP32-S3 USB Host PHY
  ├── D+
  └── D-
```

A topologia final será validada antes de PCB/enclosure.

## Repository strategy

Enquanto o produto está em descoberta, preferir um repositório guarda-chuva com limites claros entre componentes. O firmware deve preservar origem/upstream e histórico de licença. Antes de importar código do NanoVNA-D, registrar a estratégia em ADR e confirmar os termos de licença efetivos do upstream.
