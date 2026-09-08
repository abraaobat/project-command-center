# StudyOS integration in Project Command Center

## Purpose

The Project Command Center tracks StudyOS as a parent product and keeps the first real educational vertical slice visible without turning the Command Center into the StudyOS application itself.

The separation is intentional:

```text
Project Command Center
http://localhost:8787
        |
        | tracks status / links / milestones
        v
StudyOS Local Pilot
http://localhost:8788
        |
        +-- Orientador experience
        +-- Estudante experience
        +-- shared server-side StudyOS data
```

The Command Center is the project-control plane. StudyOS is the educational runtime.

## Current hierarchy

```text
StudyOS
├── Abe Joshua — Estudos
│   └── relationship: first real student / Learning Plan
└── GameDev 12
    └── relationship: Learning Program
```

The child initiatives remain separately trackable because they have their own progress and next actions, but their parent relationship must be visible in the UI.

## Data contract

`data/projects.json` supports the following optional fields:

### Parent relationship

```json
{
  "parentId": "studyos",
  "relationshipLabel": "Learning Program"
}
```

`parentId` references another project ID in the same dataset. `relationshipLabel` is presentation text only and must not be treated as authorization or product-domain data.

### Child list

Parent projects may declare children for explicit documentation:

```json
{
  "children": ["abe-joshua-estudos", "gamedev-12"]
}
```

The UI currently derives the visible relationship from child `parentId`; `children` is descriptive and useful for external tooling.

### Runtime metadata

```json
{
  "runtime": {
    "label": "StudyOS Local",
    "url": "http://localhost:8788",
    "status": "planned",
    "note": "Runtime local ainda não implementado."
  }
}
```

Supported UI states:

- `planned`: display the target runtime and note, but do not provide an operational launch action;
- `available`: display an actionable link to open the runtime.

A runtime must not be promoted to `available` merely because a URL was reserved. It requires a real server to be running and the applicable validation to have passed.

## StudyOS filter

The dashboard exposes a `StudyOS` filter. It includes:

- the StudyOS parent card;
- all projects whose `parentId` is `studyos`.

This provides a focused product view while preserving the global project inventory.

## Ownership boundaries

Project Command Center owns:

- portfolio-level status;
- estimated progress;
- project relationships;
- current phase and next milestone;
- local runtime discovery/launch metadata;
- recent project activity.

StudyOS owns:

- student profiles;
- routine data and history;
- Learning Plan data;
- study sessions;
- GameDev/Learning Program progress;
- portfolio/evidence;
- orientador/student permissions;
- Student Intelligence.

No student progress should be copied into Command Center JSON as an authoritative educational record. The Command Center may later consume a read-only StudyOS summary endpoint, but StudyOS remains the source of truth.

## Planned evolution

After the StudyOS Local Pilot is implemented and validated:

1. mark the StudyOS runtime as `available`;
2. expose the launch link in the StudyOS card;
3. optionally add a read-only health/status check;
4. later consume a minimal summary API for high-level StudyOS status without duplicating private student data;
5. keep detailed educational dashboards inside StudyOS.

## Security and privacy

The Command Center must not become a second database for private student information. In particular:

- do not store detailed routine logs or grades in `projects.json`;
- do not expose private StudyOS API data through the static dashboard;
- avoid recording sensitive information about minors in activity logs;
- local URLs do not imply internet exposure;
- remote StudyOS access must use the deployed authenticated application, not the local development port.

## Current status

As of 2026-09-08:

- StudyOS Local Pilot is documented but not yet running;
- `8788` is a reserved local target, not an operational service;
- the Project Command Center integration is a control-plane/UI preparation;
- the next technical milestone is the reproducible StudyOS local runtime and Mac ↔ tablet synchronization validation.
