#!/usr/bin/env python3
"""Cria um manifesto inicial compatível com KES Source Manifest v1."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE_TYPES = ["book", "document", "article", "video", "playlist", "channel", "podcast_video"]
METHODS = [
    "native-text", "pdf-text", "ocr", "captions-official",
    "captions-platform", "asr", "mixed", "manual"
]

parser = argparse.ArgumentParser(description="Create a KES v1 source manifest")
parser.add_argument("source_id")
parser.add_argument("--type", required=True, choices=SOURCE_TYPES, dest="source_type")
parser.add_argument("--title", required=True)
parser.add_argument("--creator", action="append", default=[])
parser.add_argument("--language", default="pt-BR")
parser.add_argument("--ref", required=True, dest="canonical_ref")
parser.add_argument("--method", required=True, choices=METHODS, dest="extraction_method")
parser.add_argument("--platform-id")
parser.add_argument("--parent-collection-id")
parser.add_argument("--output")
args = parser.parse_args()

manifest = {
    "schema_version": "kes-source-1",
    "source_id": args.source_id,
    "source_type": args.source_type,
    "title": args.title,
    "creator": args.creator,
    "language": args.language,
    "canonical_ref": args.canonical_ref,
    "acquired_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "pipeline_version": "KES-1",
    "extraction_method": args.extraction_method,
    "source_checksum": None,
    "platform_id": args.platform_id,
    "parent_collection_id": args.parent_collection_id,
    "license_or_access": None,
    "notes": []
}

output = Path(args.output or f"{args.source_id.replace(':', '_')}.manifest.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(output)
