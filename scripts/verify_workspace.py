#!/usr/bin/env python3
"""Verifies PREPARATION PACKAGE integrity. Does NOT validate raw SSB observations."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "research" / "preflight"
CHECKSUMS = PRE / "00_READ_FIRST" / "package_file_checksums.csv"
STATUS = PRE / "00_READ_FIRST" / "collection_status.json"
REGISTERS = {
    "source_catalog_entries": PRE / "01_sources" / "source_catalog.csv",
    "conceptual_variables": PRE / "02_data_dictionary" / "data_dictionary.csv",
    "ratio_inventory": PRE / "03_ratio_definitions" / "ratio_catalog.csv",
    "audit_checks": PRE / "05_integrity" / "quality_gates.csv",
}


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return sum(1 for _ in csv.DictReader(stream))


def check_preflight() -> tuple[list[str], dict[str, int], dict]:
    issues = []
    counts = {}
    if not CHECKSUMS.is_file() or not STATUS.is_file():
        return ["Missing source-package checksums or status JSON"], counts, {}

    with CHECKSUMS.open("r", encoding="utf-8-sig", newline="") as stream:
        manifest = list(csv.DictReader(stream))
    for row in manifest:
        rel = Path(row["path"])
        if rel.is_absolute() or ".." in rel.parts:
            issues.append(f"Unsafe file path in manifest: {rel}")
            continue
        file = PRE / rel
        if not file.is_file():
            issues.append(f"Missing preflight document: {rel}")
            continue
        if file.stat().st_size != int(row["bytes"]):
            issues.append(f"File size mismatch: {rel}")
            continue
        if hash_file(file).lower() != row["sha256"].lower():
            issues.append(f"SHA256 mismatch: {rel}")

    try:
        documented = json.loads(STATUS.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        documented = {}
        issues.append(f"Cannot read original status: {exc}")

    for key, path in REGISTERS.items():
        if not path.is_file():
            issues.append(f"Missing register: {path.relative_to(ROOT)}")
            continue
        counts[key] = csv_count(path)
        expected = documented.get(key)
        if expected is not None and expected != counts[key]:
            issues.append(f"Catalog count mismatch {key}: actual={counts[key]} expected={expected}")
    return issues, counts, documented


def raw_file_counts() -> dict[str, int]:
    result = {}
    for section in ("ssb", "klass", "municipal_reports", "metadata"):
        directory = ROOT / "data" / "raw" / section
        result[section] = sum(
            f.is_file() for f in directory.rglob("*")
            if f.name != ".gitkeep" and f.name != "README.md"
        ) if directory.is_dir() else 0
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-data", action="store_true",
        help="Exit 2 unless the scientific data-readiness gate has passed."
    )
    args = parser.parse_args()

    issues, counts, source_status = check_preflight()
    raw = raw_file_counts()
    raw_total = sum(raw.values())
    # This starter does not contain a scientific signoff mechanism.
    # Even when raw files are present they remain UNAUDITED.
    scientific_gate = (
        "BLOCKED_RAW_NOT_COLLECTED" if raw_total == 0
        else "BLOCKED_RAW_UNVERIFIED"
    )
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "documentation_integrity": "FAIL" if issues else "PASS",
        "original_collection_status": source_status.get("collection_status", "UNKNOWN"),
        "registered_counts": counts,
        "raw_file_counts": raw,
        "raw_file_total": raw_total,
        "scientific_data_gate": scientific_gate,
        "case_selection_allowed": False,
        "modeling_allowed": False,
        "issues": issues,
    }
    folder = ROOT / "reports" / "preflight"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "workspace_status.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("PREPARATION DOCUMENTS:", report["documentation_integrity"])
    print("SOURCE CATALOG COUNTS:", counts)
    print("RAW FILE COUNTS:", raw)
    print("SCIENTIFIC DATA GATE:", scientific_gate)
    print("NO municipality selection or modeling is permitted.")
    if issues:
        for issue in issues:
            print("ERROR:", issue, file=sys.stderr)
        return 1
    if args.require_data:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
