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

`data/projects.json` supports optional parent/child and runtime metadata.

### Parent relationship

```json
{
  "parentId": "studyos",
  "relationshipLabel": "Learning Program"
}
```

### Child list

```json
{
  "children": ["abe-joshua-estudos", "gamedev-12"]
}
```

### Runtime metadata

```json
{
  "runtime": {
    "label": "StudyOS Local",
    "url": "http://localhost:8788/orientador",
    "status": "available",
    "note": "Validado em Mac ↔ tablet; runtime local operacional enquanto o serviço estiver iniciado."
  }
}
```

Supported UI states:

- `planned`: display the target runtime and note, but do not provide an operational launch action;
- `available`: display an actionable link to open the runtime.

A runtime must not be promoted to `available` merely because a URL was reserved. StudyOS was promoted only after the real service ran on the Mac, a tablet joined through the local pairing flow, and routine changes made on the tablet were reflected on the Orientador dashboard.

## Validated StudyOS Local flow

On 2026-09-08 the first physical cross-device vertical slice passed:

```text
Tablet / Estudante
        |
        | check / uncheck routine item
        v
StudyOS Local :8788
server-side state
        |
        v
Mac / Orientador
updated dashboard state
```

Validated facts:

- Mac opened the Orientador dashboard on `localhost:8788`;
- LAN access reached the same StudyOS instance;
- an unpaired device was correctly blocked by the local access gate;
- the tablet was paired using the tokenized access link copied from the Orientador dashboard;
- the Estudante dashboard opened on the tablet;
- student routine changes produced the corresponding state change on the Orientador dashboard immediately;
- authoritative routine state remains owned by StudyOS, not by Project Command Center.

The LAN IP is dynamic and must not be stored as a permanent project setting.

## StudyOS filter

The dashboard exposes a `StudyOS` filter. It includes the StudyOS parent card and projects whose `parentId` is `studyos`.

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

## Next evolution

With the local runtime validated and marked `available`:

1. keep the launch action in the StudyOS card;
2. optionally add a read-only health/status probe;
3. later consume only a minimal high-level StudyOS summary API;
4. keep detailed educational dashboards inside StudyOS;
5. never persist dynamic LAN addresses or private student-detail state in Command Center data.

## Security and privacy

The Command Center must not become a second database for private student information. In particular:

- do not store detailed routine logs or grades in `projects.json`;
- do not expose private StudyOS API data through the static dashboard;
- avoid recording sensitive information about minors in activity logs;
- local URLs do not imply internet exposure;
- remote StudyOS access must use the deployed authenticated application, not the local development port.

## Current status

As of 2026-09-08:

- StudyOS Local Pilot is operational on `:8788` when the local service is running;
- the first real Mac ↔ tablet synchronization flow is validated;
- Project Command Center may show StudyOS Local as `available` and provide its launch link;
- the next StudyOS milestone is deeper domain migration: full Learning Plan/routine normalization, generic Student profile and the first real GameDev session record.
