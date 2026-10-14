#!/usr/bin/env python3
"""Phase 1A.1: Verify official SSB PxWeb v2 and KLASS API schemas.

This is a metadata-only probe. It never downloads financial observations.
Each execution stores the exact API response bytes in a new dated folder.

Usage (from the repository root):
    python scripts/phase1a_01_probe_official_sources.py --self-test
    python scripts/phase1a_01_probe_official_sources.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

OUT = Path("reports/phase1a/api_probe")
TARGETS = (
    ("ssb_12134_info", "https://data.ssb.no/api/pxwebapi/v2/tables/12134?lang=en"),
    ("ssb_12134_metadata", "https://data.ssb.no/api/pxwebapi/v2/tables/12134/metadata?lang=en"),
    ("ssb_12364_metadata", "https://data.ssb.no/api/pxwebapi/v2/tables/12364/metadata?lang=en"),
    ("ssb_07459_metadata", "https://data.ssb.no/api/pxwebapi/v2/tables/07459/metadata?lang=en"),
    ("klass_2020_codes", "https://data.ssb.no/api/klass/v1/classifications/131/codesAt.json?date=2020-01-01"),
    ("klass_changes", "https://data.ssb.no/api/klass/v1/classifications/131/changes.json?from=2016-01-01&to=2026-01-01"),
)


def check_payload(name: str, document: object) -> None:
    """Reject unexpected SSB/KLASS response structures before archiving."""
    if not isinstance(document, dict):
        raise ValueError(f"{name}: expected a JSON object")

    if name.endswith("_metadata"):
        dimensions = document.get("dimension")
        ids = document.get("id")
        if not isinstance(dimensions, dict) or not isinstance(ids, list):
            raise ValueError(f"{name}: missing JSON-stat2 dimensions or IDs")
        if not ids or len(ids) != len(set(ids)) or set(ids) != set(dimensions):
            raise ValueError(f"{name}: inconsistent dimension IDs")

    elif name == "klass_2020_codes":
        codes = document.get("codes")
        if not isinstance(codes, list) or not codes:
            raise ValueError("KLASS codesAt: expected nonempty 'codes' list")
        if any(not isinstance(record, dict) or not record.get("code") for record in codes):
            raise ValueError("KLASS codesAt: invalid code record")

    elif name == "klass_changes":
        # The official KLASS response uses 'codeChanges', NOT 'changes'.
        changes = document.get("codeChanges")
        if not isinstance(changes, list) or not changes:
            raise ValueError("KLASS changes: expected nonempty 'codeChanges' list")
        for index, record in enumerate(changes):
            if not isinstance(record, dict):
                raise ValueError(f"KLASS change {index}: not an object")
            if not record.get("changeOccurred"):
                raise ValueError(f"KLASS change {index}: missing changeOccurred")
            if not (record.get("oldCode") or record.get("newCode")):
                raise ValueError(f"KLASS change {index}: missing oldCode/newCode")

    elif name.endswith("_info"):
        if not any(field in document for field in ("label", "id", "variableNames")):
            raise ValueError(f"{name}: unexpected table-info schema")

    else:
        raise ValueError(f"Unknown probe target: {name}")


def save_new(path: Path, payload: bytes) -> None:
    """Preserve original response bytes; never replace an existing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)


def self_test() -> None:
    metadata = {"id": ["Region", "ContentsCode", "Tid"],
                "dimension": {key: {} for key in ("Region", "ContentsCode", "Tid")}}
    valid = {
        "ssb_12134_info": {"label": "Test table"},
        "ssb_12134_metadata": metadata,
        "ssb_12364_metadata": metadata,
        "ssb_07459_metadata": metadata,
        "klass_2020_codes": {"codes": [{"code": "0301", "name": "Oslo"}]},
        "klass_changes": {"codeChanges": [{"changeOccurred": "2020-01-01",
                                          "oldCode": "0101", "newCode": "3001"}]},
    }
    for name in valid:
        check_payload(name, valid[name])
    for invalid_name, invalid_doc in (
        ("klass_changes", {"changes": valid["klass_changes"]["codeChanges"]}),
        ("klass_changes", {"codeChanges": [{}]}),
        ("klass_2020_codes", {"codes": []}),
        ("ssb_12134_metadata", {"id": ["Tid"], "dimension": {}}),
    ):
        try:
            check_payload(invalid_name, invalid_doc)
        except ValueError:
            continue
        raise AssertionError(f"Invalid response accepted: {invalid_name}")
    with tempfile.TemporaryDirectory() as temporary:
        destination = Path(temporary) / "response.json"
        save_new(destination, b'{"unchanged": true}')
        try:
            save_new(destination, b'{"changed": true}')
        except FileExistsError:
            pass
        else:
            raise AssertionError("Original source file was overwritten")
    print("PASS: SSB/KLASS schemas, codeChanges regression, immutable raw response")


def run(out_dir: Path, pause: float) -> int:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    session = requests.Session()
    session.headers["User-Agent"] = "NorwayMunicipalResearch-SourceAudit/1.1"
    rows: list[dict] = []

    for index, (name, url) in enumerate(TARGETS):
        record = {
            "checked_utc": datetime.now(timezone.utc).isoformat(),
            "source": name, "url": url, "status": "FAIL",
            "http_status": "", "bytes": "", "sha256": "",
            "raw_path": "", "error": "",
        }
        try:
            response = session.get(url, timeout=45)
            record["http_status"] = response.status_code
            response.raise_for_status()
            raw = response.content
            document = json.loads(raw)
            check_payload(name, document)
            raw_path = run_dir / f"{name}.json"
            save_new(raw_path, raw)
            record.update(status="PASS", bytes=len(raw),
                          sha256=hashlib.sha256(raw).hexdigest(),
                          raw_path=str(raw_path))
        except (requests.RequestException, ValueError, OSError) as error:
            record["error"] = f"{type(error).__name__}: {error}"[:500]
        rows.append(record)
        print(f"{name:24s} {record['status']:4s} HTTP={record['http_status'] or '-'} "
              f"{record['error']}", flush=True)
        if index < len(TARGETS) - 1:
            time.sleep(pause)

    manifest = run_dir / "endpoint_probe_manifest.csv"
    with manifest.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    passed = sum(item["status"] == "PASS" for item in rows)
    print(f"Endpoint probe: {passed}/{len(TARGETS)} passed")
    print(f"Manifest: {manifest}")
    print("Scientific status: BLOCKED. This probe checks connectivity/schema only.")
    return 0 if passed == len(TARGETS) else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--pause", type=float, default=2.5)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not 2.0 <= args.pause <= 300:
        parser.error("--pause must be between 2 and 300 seconds")
    return run(args.out, args.pause)


if __name__ == "__main__":
    raise SystemExit(main())
