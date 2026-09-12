# NanoVNA Modern — Repository Plan

## Preferred repository

`abraaobat/nanovna-modern`

Purpose: umbrella repository for architecture, firmware integration, bridge, web dashboard and SmartLink while boundaries are still evolving.

## Initial tree

```text
nanovna-modern/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── HARDWARE.md
│   ├── UI-UX.md
│   ├── SD-EXTENSIONS.md
│   ├── USB-WEB-BRIDGE.md
│   ├── SMARTLINK-ESP32.md
│   ├── ANALYSIS-AI.md
│   └── adr/
├── firmware/
│   └── README.md
├── bridge/
│   └── README.md
├── web/
│   └── README.md
├── smartlink/
│   └── README.md
├── protocol/
│   └── README.md
├── hardware/
│   └── README.md
└── tools/
```

## Firmware upstream policy

Source of truth upstream: `DiSlord/NanoVNA-D`.

Before adding upstream source code to the umbrella repository:

1. confirm actual license terms and attribution requirements;
2. choose one strategy: fork repository, submodule, subtree, or separate firmware repo;
3. pin baseline commit/tag;
4. keep `upstream` remote documented;
5. never mix local UI changes with untracked vendor patches.

Preferred engineering sequence:

- create/fork upstream;
- reproduce `TARGET=F303` build unchanged;
- CI build baseline;
- create a feature branch for Modern UI;
- keep RF/DSP changes out of early UI PRs.

## Component responsibilities

### `firmware/`

Local NanoVNA UI, SD extensions and protocol hooks. The RF measurement core remains upstream-derived.

### `bridge/`

Desktop USB-to-API service. CLI-first, headless, macOS first.

### `web/`

Responsive dashboard/PWA shared by desktop and SmartLink deployments.

### `smartlink/`

ESP32-S3 firmware: USB Host, Wi-Fi/BLE, WebSocket, buffers, local web host and optional analysis.

### `protocol/`

Schemas and compatibility contracts between firmware, bridge, SmartLink and web client.

### `hardware/`

SmartLink wiring, power/VBUS protection, BOM, enclosure and later PCB work.

## Branch policy

- `main` — stable project baseline/documentation.
- `feature/*` — bounded implementation work.
- `spike/*` — experiments such as TinyML or alternative renderers.
- `upstream-sync/*` — controlled upstream merges/rebases when applicable.

## First PRs

1. `docs/project-foundation` — charter, roadmap, architecture, hardware fingerprint.
2. `build/f303-baseline` — reproducible upstream build and CI.
3. `ui/foundation` — theme/widgets/navigation with zero RF changes.
4. `bridge/usb-probe` — read-only device discovery and protocol inventory.

## Definition of done for project foundation

- standalone GitHub repository exists;
- README and roadmap published;
- upstream strategy recorded in ADR;
- F0 hardware fingerprint tracked;
- project added to Project Command Center;
- next action points to USB/DFU validation, not experimental flash.
