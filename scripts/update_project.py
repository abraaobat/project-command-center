#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "data" / "projects.json"
ACTIVITY = ROOT / "data" / "activity.json"

parser = argparse.ArgumentParser(description="Atualiza um projeto no Project Command Center")
parser.add_argument("project_id")
parser.add_argument("--progress", type=int)
parser.add_argument("--status")
parser.add_argument("--current")
parser.add_argument("--next")
parser.add_argument("--action")
parser.add_argument("--activity")
args = parser.parse_args()

data = json.loads(PROJECTS.read_text(encoding="utf-8"))
project = next((p for p in data["projects"] if p["id"] == args.project_id), None)
if not project:
    raise SystemExit(f"Projeto não encontrado: {args.project_id}")

if args.progress is not None:
    project["progress"] = max(0, min(100, args.progress))
if args.status is not None:
    project["status"] = args.status
if args.current is not None:
    project["current"] = args.current
if args.next is not None:
    project["next"] = args.next
if args.action is not None:
    project["action"] = args.action

data["lastUpdated"] = datetime.now().astimezone().isoformat(timespec="seconds")
PROJECTS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if args.activity:
    history = json.loads(ACTIVITY.read_text(encoding="utf-8"))
    history["items"].insert(0, {
        "date": datetime.now().astimezone().date().isoformat(),
        "project": project["name"],
        "type": "update",
        "text": args.activity
    })
    history["items"] = history["items"][:100]
    ACTIVITY.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Atualizado: {project['name']} ({project.get('progress', 0)}%)")
