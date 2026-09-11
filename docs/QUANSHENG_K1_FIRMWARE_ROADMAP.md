# Quansheng K1 Firmware — Roadmap

Updated: 2026-09-10

## Goal

Create a controlled custom-firmware path for the user's Quansheng K1 / UV-K5 V3-class radio, prioritizing satellite/field-operation features and future integration with DigiRig/RadioLink without flashing experimental changes before reproducible builds and recovery procedures are proven.

## Selected upstream baseline

Primary candidate: `armel/uv-k1-k5v3-firmware-custom`, specific to UV-K1 / UV-K5 V3 hardware based on the PY32F071 MCU.

Current upstream reference evaluated: **F4HWN v6.0.0**.

Relevant editions:

- **Fusion** — balanced upstream reference edition and default baseline candidate;
- **FieldOps** — field-oriented edition with Fox Hunt, Morse Beacon and RescueOps features relevant to the project;
- **Transfer** — radio-to-radio transfer features, secondary interest;
- **Labs** — experimental; not a default base for the first fork.

## K0 — Upstream selection ✅

- [x] identify K1/K5 V3-specific upstream;
- [x] confirm PY32F071 target family;
- [x] confirm reproducible Docker/CMake build workflow exists;
- [x] identify v6.0.0 edition split;
- [x] narrow first comparison to Fusion vs FieldOps;
- [ ] pin exact upstream commit after comparative build.

## K1 — Reproducible clean builds 🟡 NEXT

- [ ] build unmodified Fusion v6.0.0;
- [ ] build unmodified FieldOps v6.0.0;
- [ ] record binary sizes and RAM/flash headroom;
- [ ] compare build outputs with upstream release artifacts where practical;
- [ ] document toolchain/Docker versions;
- [ ] select default edition for the future fork.

**Promotion rule:** no custom code before at least one clean upstream build is reproducible.

## K2 — Recovery + safe flashing

- [ ] document exact radio model/hardware revision;
- [ ] back up channels/settings where supported;
- [ ] document bootloader/flash/recovery procedure;
- [ ] keep known-good upstream binary available;
- [ ] define rollback checklist;
- [ ] perform first flash only after recovery path is understood.

## K3 — Own repository / fork

- [ ] create user's firmware repository/fork;
- [ ] preserve upstream attribution/license;
- [ ] add upstream remote strategy;
- [ ] add CI build for selected edition;
- [ ] add project status contract for Project Command Center;
- [ ] tag first unmodified reproducible baseline.

## K4 — Satellite / field feature profile

Candidate scope only after K1–K3:

- satellite-oriented channel/workflow helpers;
- Doppler workflow investigation;
- beacon behavior;
- RF log;
- Fox Hunt;
- dual watch / DW/DWR behavior;
- field presets based on validated upstream features.

No feature is considered available merely because another edition/upstream documents it; it must be present and tested in the selected build.

## K5 — DigiRig / RadioLink integration

- [ ] validate K1 + DigiRig audio/PTT path on macOS;
- [ ] Dire Wolf AFSK/KISS interoperability;
- [ ] RadioLink CLI receive path;
- [ ] RadioLink CLI transmit path under controlled amateur-radio operation;
- [ ] document mode/frequency/PTT constraints.

## K6 — Custom feature development

Only after baseline/recovery/integration are proven:

- [ ] prioritize custom features by measurable operational value;
- [ ] implement one feature per short branch;
- [ ] preserve clean upstream comparison;
- [ ] automated build on every PR;
- [ ] hardware validation before release.

## Immediate next action

Build **Fusion v6.0.0** and **FieldOps v6.0.0** unmodified with the upstream Docker/CMake workflow, compare flash/RAM headroom and use that evidence to select the first pinned base. No radio flashing is required for this gate.
