#!/usr/bin/env python3
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from sync_status_sources import build_activity_item, dedupe_activity, merge_status, normalize_progress


def test_progress_bounds():
    assert normalize_progress(-4) == 0
    assert normalize_progress(52) == 52
    assert normalize_progress(140) == 100


def test_merge_allowlist_preserves_identity():
    project = {
        "id": "studyos",
        "name": "StudyOS",
        "category": "saas",
        "priority": "Alta",
        "progress": 10,
        "current": "antigo",
    }
    status = {
        "projectId": "studyos",
        "name": "NÃO DEVE SUBSTITUIR",
        "category": "other",
        "priority": "Baixa",
        "progress": 44,
        "current": "novo",
        "next": "HTTPS",
    }

    merge_status(project, status)

    assert project["id"] == "studyos"
    assert project["name"] == "StudyOS"
    assert project["category"] == "saas"
    assert project["priority"] == "Alta"
    assert project["progress"] == 44
    assert project["current"] == "novo"
    assert project["next"] == "HTTPS"


def test_activity_deduplication():
    items = [
        {"date": "2026-09-08", "project": "StudyOS", "type": "validation", "text": "ok"},
        {"date": "2026-09-08", "project": "StudyOS", "type": "validation", "text": "ok"},
        {"date": "2026-09-08", "project": "StudyOS", "type": "feature", "text": "outro"},
    ]
    result = dedupe_activity(items)
    assert len(result) == 2


def test_activity_contract():
    source = {"repository": "abraaobat/saas-engineering-platform"}
    status = {
        "activity": {
            "date": "2026-09-08",
            "type": "validation",
            "text": "Presença validada",
        }
    }
    item = build_activity_item("StudyOS", source, status)
    assert item["project"] == "StudyOS"
    assert item["source"] == source["repository"]
    assert item["text"] == "Presença validada"


def main():
    test_progress_bounds()
    test_merge_allowlist_preserves_identity()
    test_activity_deduplication()
    test_activity_contract()
    print("Auto Status Sync tests: PASS")


if __name__ == "__main__":
    main()
