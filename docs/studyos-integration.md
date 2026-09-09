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
        +-- Learning Resources / Learning Programs
        +-- companion capabilities under validation
```

The Command Center is the project-control plane. StudyOS is the educational runtime and source of truth.

## Current hierarchy

```text
StudyOS
├── Abe Joshua — Estudos
│   └── relationship: first real student / Learning Plan
├── GameDev 12
│   └── relationship: Learning Program
└── Premiere Mobile — iPad
    └── relationship: Learning Program
```

Algebra resources remain inside the Abe/StudyOS educational domain rather than becoming a separate portfolio project.

## Current StudyOS capabilities tracked at portfolio level

- Local runtime `:8788` operational when started;
- Mac ↔ tablet routine synchronization validated;
- Algebra resource bundle integrated: YouTube playlist, Khan Academy and Prime Video support series;
- GameDev 12 represented as a Learning Program;
- Premiere Mobile — iPad represented as a second Learning Program;
- open-dashboard Orientador notifications validated on the real Mac using service worker delivery;
- student device presence/last-seen validated on the real tablet/Mac pair;
- presence transition `ONLINE -> OFFLINE` confirmed after screen lock, tab closure and window minimization;
- precise geolocation remains planned until HTTPS/secure-context requirements are satisfied;
- Ambient Dashboard ESP32-S3 remains a planned read-only companion.

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
  "children": ["abe-joshua-estudos", "gamedev-12", "premiere-mobile-ipad"]
}
```

### Runtime metadata

```json
{
  "runtime": {
    "label": "StudyOS Local",
    "url": "http://localhost:8788/orientador",
    "status": "available",
    "note": "Runtime local operacional; notificações e presença/last-seen validados."
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
- authoritative routine state remains owned by StudyOS, not by Project Command Center;
- open-dashboard notification delivery was accepted by the browser on the real Mac through the service worker path;
- presence/last-seen correctly switched between online and offline on real devices after screen lock, tab closure and window minimization.

The LAN IP is dynamic and must not be stored as a permanent project setting.

## Presence, notifications and location boundary

The Command Center may track implementation status for these capabilities, but must not ingest their private runtime data.

- Notifications: only implementation/validation status belongs in the Command Center.
- Presence/last-seen: only feature status belongs in the Command Center; live device presence stays in StudyOS.
- Precise location: never persist coordinates or location history in Project Command Center data.
- Ambient Display: track the companion project/milestone, not the private educational payload shown on the device.

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
- learning resources;
- study sessions;
- Learning Program progress;
- portfolio/evidence;
- orientador/student permissions;
- presence/last-seen;
- precise location when implemented;
- Student Intelligence.

No student progress should be copied into Command Center JSON as an authoritative educational record. The Command Center may later consume a read-only StudyOS summary endpoint, but StudyOS remains the source of truth.

## Next evolution

With runtime, notifications and presence validated:

1. prepare HTTPS/secure origin for the Local Pilot or deployed app;
2. implement explicit-permission precise geolocation with bounded retention and Orientador-only access;
3. normalize the full Learning Plan and real Algebra Study Session contract;
4. record the first GameDev and Premiere sessions;
5. later add Web Push for notifications with the dashboard/browser closed;
6. later add a minimal read-only StudyOS health/summary integration;
7. keep detailed educational dashboards inside StudyOS.

## Security and privacy

The Command Center must not become a second database for private student information. In particular:

- do not store detailed routine logs or grades in `projects.json`;
- do not store device presence timestamps as an operational feed;
- do not store precise student location;
- do not expose private StudyOS API data through the static dashboard;
- avoid recording sensitive information about minors in activity logs;
- local URLs do not imply internet exposure;
- remote StudyOS access must use the deployed authenticated application, not the local development port.

## Current status

As of 2026-09-08:

- StudyOS Local Pilot is operational on `:8788` when the local service is running;
- the first real Mac ↔ tablet synchronization flow is validated;
- Algebra resources and Premiere Mobile — iPad are integrated into StudyOS;
- open-dashboard notifications are validated on the real Mac;
- presence/last-seen is validated on the real tablet/Mac pair across screen lock, tab closure and window minimization;
- precise GPS and Ambient Dashboard remain planned follow-up capabilities.
