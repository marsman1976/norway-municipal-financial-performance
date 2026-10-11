#!/usr/bin/env python3
"""Produce a SHA-256 inventory of downloaded files; never alters originals."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from verify_workspace import ROOT, hash_file

FOLDERS = ("ssb", "klass", "municipal_reports", "metadata")


def main() -> None:
    rows = []
    for section in FOLDERS:
        folder = ROOT / "data" / "raw" / section
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or path.name in (".gitkeep", "README.md"):
                continue
            rows.append({
                "source_group": section,
                "relative_path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": hash_file(path),
                "inventoried_utc": datetime.now(timezone.utc).isoformat(),
                "definition_verified": "NO",
                "data_quality_verified": "NO",
            })
    dest = ROOT / "reports" / "phase1a" / "raw_file_inventory.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "source_group", "relative_path", "bytes", "sha256",
            "inventoried_utc", "definition_verified", "data_quality_verified",
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote: {dest}")
    print(f"Raw files found: {len(rows)}")
    print("Status: UNAUDITED. This is only a checksum inventory.")


if __name__ == "__main__":
    main()
