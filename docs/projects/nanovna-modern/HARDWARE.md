# NanoVNA Modern — Hardware Fingerprint

## Unit under test

| Field | Observed value |
|---|---|
| Brand | ZeenKo |
| Commercial model | ZN401 |
| Family | NanoVNA-H4 |
| External HW label | `4.7_ZK` |
| Serial on label | `H4-2603769` |
| Display | 480x320 class |
| microSD | Present and recognized by firmware |
| Current firmware | NanoVNA-D 1.2.44 `[x401]` |
| Build date shown | 2025-05-26 |
| MCU shown by firmware | STM32F303xC |
| Architecture | ARMv7E-M Cortex-M4F |
| TXCO shown | 26.000000 MHz |

## Current USB diagnostic

Tests on macOS with the device powered and connected over USB-C have so far shown no child USB device under `ioreg -p IOUSB -w0` and no new `/dev/cu.*` node. Changing the Mac USB-C port did not change the result.

This does **not** yet prove a NanoVNA hardware fault. Remaining controlled tests:

1. known-good USB-A → USB-C data cable through an adapter/hub;
2. reverse USB-C connector orientation where applicable;
3. known-good USB data cable used with another device;
4. DFU enumeration test without flashing;
5. if necessary, physical inspection of the board.

## F0 evidence to collect

### Normal runtime USB

Capture:

```bash
system_profiler SPUSBDataType
ioreg -p IOUSB -w0
ls /dev/cu.*
```

If a serial node appears, collect read-only console output first (`help`, `info`, `version` as available).

### DFU

Use the documented H4 method only after runtime cable tests. DFU testing at F0 is enumeration-only; do not write firmware.

Expected STM32 DFU identity from upstream documentation is typically `0483:df11`, but the actual connected unit must be observed and recorded before any flash procedure is approved.

## Components still to confirm

- exact clock generator/synthesizer fitted to 4.7_ZK;
- exact mixer fitted to this board revision;
- LCD controller/variant;
- touchscreen controller;
- board-level power/USB-C implementation;
- flash capacity/headroom actually available to this build.

Do not infer these solely from the enclosure label if a firmware build decision depends on them.

## Safety rule

No experimental firmware flash is permitted before:

- DFU/recovery path is verified;
- upstream clean build succeeds;
- original settings/calibration strategy is documented;
- correct target and hardware variant are confirmed.
