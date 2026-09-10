#!/usr/bin/env python3
"""Validate KES v1 source manifests committed to the repository."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
KES_DIR = ROOT / "docs" / "knowledge-extraction"
SCHEMA_PATH = KES_DIR / "source-manifest.schema.json"
PILOTS_DIR = KES_DIR / "pilots"
PRIVATE_ID_PATTERN = re.compile(r"(?:^|[^a-zA-Z0-9])(?:file_|libfile_|file-inline-libfile_)[a-zA-Z0-9_-]+")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_repository_invariants(manifest: dict, path: Path) -> None:
    canonical_ref = manifest["canonical_ref"]
    access = (manifest.get("license_or_access") or "").lower()
    serialized = json.dumps(manifest, ensure_ascii=False)

    if PRIVATE_ID_PATTERN.search(serialized):
        raise ValueError(f"{path}: private Library/file identifier must not be committed")

    parsed = urlparse(canonical_ref)
    if canonical_ref.startswith("private-library://"):
        if not parsed.netloc or not parsed.path.strip("/"):
            raise ValueError(f"{path}: private-library canonical_ref must be stable and opaque")
        if "private" not in access:
            raise ValueError(f"{path}: private source must document private access")
    elif parsed.scheme not in {"http", "https"}:
        raise ValueError(
            f"{path}: public canonical_ref must use http(s), or private sources must use private-library://"
        )

    if manifest["source_type"] == "channel" and manifest.get("extraction_method") not in {
        "manual",
        "captions-official",
        "captions-platform",
        "mixed",
    }:
        raise ValueError(f"{path}: channel manifest uses an implausible extraction method")


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    manifests = sorted(PILOTS_DIR.glob("*/source-manifest.json"))
    if len(manifests) < 2:
        raise SystemExit("KES pilots require at least two source manifests")

    source_ids: set[str] = set()
    canonical_refs: set[str] = set()

    for path in manifests:
        manifest = load_json(path)
        errors = sorted(validator.iter_errors(manifest), key=lambda error: list(error.path))
        if errors:
            details = "; ".join(error.message for error in errors)
            raise SystemExit(f"{path}: schema validation failed: {details}")

        validate_repository_invariants(manifest, path)

        source_id = manifest["source_id"]
        canonical_ref = manifest["canonical_ref"]
        if source_id in source_ids:
            raise SystemExit(f"duplicate source_id: {source_id}")
        if canonical_ref in canonical_refs:
            raise SystemExit(f"duplicate canonical_ref: {canonical_ref}")
        source_ids.add(source_id)
        canonical_refs.add(canonical_ref)

        print(f"PASS {path.relative_to(ROOT)} -> {source_id}")

    print(f"KES manifest validation: PASS ({len(manifests)} manifests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
