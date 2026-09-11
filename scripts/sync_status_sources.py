#!/usr/bin/env python3
import argparse
import base64
import copy
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BASE_PROJECTS = DATA / "projects.json"
BASE_ACTIVITY = DATA / "activity.json"
SOURCES = DATA / "status-sources.json"
RUNTIME_PROJECTS = DATA / "runtime-projects.json"
RUNTIME_ACTIVITY = DATA / "runtime-activity.json"

ALLOWED_FIELDS = {
    "status",
    "statusClass",
    "progress",
    "roadmap",
    "current",
    "architecture",
    "next",
    "action",
    "subprojects",
    "runtime",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path: Path, payload):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def fetch_github_json(repository: str, ref: str, path: str):
    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI (gh) não encontrado")

    endpoint = f"repos/{repository}/contents/{path}?ref={ref}"
    result = subprocess.run(
        ["gh", "api", endpoint],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "gh api falhou").strip()
        raise RuntimeError(message)

    envelope = json.loads(result.stdout)
    if envelope.get("encoding") != "base64" or "content" not in envelope:
        raise RuntimeError("resposta do GitHub não contém conteúdo base64 esperado")

    raw = base64.b64decode(envelope["content"].replace("\n", ""))
    return json.loads(raw.decode("utf-8"))


def normalize_progress(value):
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        raise ValueError(f"progress inválido: {value!r}")


def merge_status(project, status):
    for field in ALLOWED_FIELDS:
        if field not in status:
            continue
        value = copy.deepcopy(status[field])
        if field == "progress":
            value = normalize_progress(value)
        project[field] = value


def build_activity_item(project_name, source, status):
    activity = status.get("activity")
    if not isinstance(activity, dict) or not activity.get("text"):
        return None
    return {
        "date": activity.get("date") or datetime.now().astimezone().date().isoformat(),
        "project": project_name,
        "type": activity.get("type") or "sync",
        "text": activity["text"],
        "source": source.get("repository"),
    }


def dedupe_activity(items):
    seen = set()
    result = []
    for item in items:
        key = (
            item.get("date"),
            item.get("project"),
            item.get("type"),
            item.get("text"),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result[:100]


def main():
    parser = argparse.ArgumentParser(description="Sincroniza status publicados pelos projetos com o Project Command Center")
    parser.add_argument("--strict", action="store_true", help="retorna erro se alguma fonte falhar")
    args = parser.parse_args()

    projects_payload = read_json(BASE_PROJECTS)
    activity_payload = read_json(BASE_ACTIVITY)
    sources_payload = read_json(SOURCES)

    projects = copy.deepcopy(projects_payload.get("projects", []))
    by_id = {project.get("id"): project for project in projects}
    activity_items = copy.deepcopy(activity_payload.get("items", []))

    sync_results = []
    failures = 0

    for source in sources_payload.get("sources", []):
        if not source.get("enabled", True):
            continue

        project_id = source.get("projectId")
        result_meta = {
            "projectId": project_id,
            "repository": source.get("repository"),
            "path": source.get("path"),
            "ref": source.get("ref", "main"),
        }

        try:
            if project_id not in by_id:
                raise RuntimeError(f"projeto não existe em projects.json: {project_id}")

            status = fetch_github_json(
                source["repository"],
                source.get("ref", "main"),
                source["path"],
            )

            if status.get("projectId") != project_id:
                raise RuntimeError(
                    f"projectId divergente: esperado {project_id!r}, recebido {status.get('projectId')!r}"
                )

            merge_status(by_id[project_id], status)
            by_id[project_id]["statusSource"] = {
                "repository": source["repository"],
                "path": source["path"],
                "ref": source.get("ref", "main"),
                "updatedAt": status.get("updatedAt"),
            }

            activity = build_activity_item(by_id[project_id].get("name", project_id), source, status)
            if activity:
                activity_items.insert(0, activity)

            result_meta["status"] = "ok"
            result_meta["updatedAt"] = status.get("updatedAt")
        except Exception as exc:
            failures += 1
            result_meta["status"] = "error"
            result_meta["error"] = str(exc)

        sync_results.append(result_meta)

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    runtime_projects = copy.deepcopy(projects_payload)
    runtime_projects["lastUpdated"] = now
    runtime_projects["dashboardVersion"] = "4.6"
    runtime_projects["projects"] = projects
    runtime_projects["autoSync"] = {
        "generatedAt": now,
        "sources": sync_results,
    }

    runtime_activity = copy.deepcopy(activity_payload)
    runtime_activity["items"] = dedupe_activity(activity_items)
    runtime_activity["generatedAt"] = now

    atomic_write_json(RUNTIME_PROJECTS, runtime_projects)
    atomic_write_json(RUNTIME_ACTIVITY, runtime_activity)

    ok = len(sync_results) - failures
    print(f"Auto Status Sync: {ok} fonte(s) OK, {failures} falha(s).")
    print(f"Gerado: {RUNTIME_PROJECTS.relative_to(ROOT)}")

    if failures and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
