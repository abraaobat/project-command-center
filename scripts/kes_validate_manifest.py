#!/usr/bin/env python3
"""Validador leve do KES Source Manifest v1, sem dependências externas."""

import argparse
import json
from pathlib import Path

REQUIRED = [
    "schema_version", "source_id", "source_type", "title", "language",
    "canonical_ref", "acquired_at", "pipeline_version", "extraction_method"
]
SOURCE_TYPES = {"book", "document", "article", "video", "playlist", "channel", "podcast_video"}
METHODS = {
    "native-text", "pdf-text", "ocr", "captions-official",
    "captions-platform", "asr", "mixed", "manual"
}

parser = argparse.ArgumentParser(description="Validate a KES v1 source manifest")
parser.add_argument("manifest")
args = parser.parse_args()

path = Path(args.manifest)
errors = []

try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception as exc:
    raise SystemExit(f"FAIL: invalid JSON: {exc}")

for key in REQUIRED:
    if key not in data or data[key] in (None, ""):
        errors.append(f"missing required field: {key}")

if data.get("schema_version") != "kes-source-1":
    errors.append("schema_version must be 'kes-source-1'")

if data.get("source_type") not in SOURCE_TYPES:
    errors.append(f"invalid source_type: {data.get('source_type')!r}")

if data.get("extraction_method") not in METHODS:
    errors.append(f"invalid extraction_method: {data.get('extraction_method')!r}")

creator = data.get("creator", [])
if creator is not None and not isinstance(creator, list):
    errors.append("creator must be an array")

notes = data.get("notes", [])
if notes is not None and not isinstance(notes, list):
    errors.append("notes must be an array")

if errors:
    print("FAIL")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("PASS")
print(f"source_id: {data['source_id']}")
print(f"source_type: {data['source_type']}")
print(f"extraction_method: {data['extraction_method']}")
