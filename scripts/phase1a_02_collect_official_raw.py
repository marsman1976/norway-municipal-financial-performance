#!/usr/bin/env python3
"""Phase 1A.2: Collect ORIGINAL SSB PxWeb v2 and KLASS responses.

NO case selection, financial calculations, merging, imputation, or modeling.
Run from the VS Code repository root. All source response bytes stay unchanged.
SSB API documentation: https://www.ssb.no/en/api/pxwebapiv2
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests

API = "https://data.ssb.no/api/pxwebapi/v2/tables"
KLASS = "https://data.ssb.no/api/klass/v1/classifications/131"
KNOWN_TABLES = {
    "12134": "Financial key figures",
    "12364": "Financial basic data",
    "07459": "Population by sex and age",
    "12143": "Operating and balance sheet ratios",
    "12135": "Debt financial ratios",
    "12137": "Financial amounts per capita",
    "13553": "Operating account financing",
    "12333": "Investment financing",
    "13551": "Detailed operating accounts (2020 onward)",
    "13552": "Detailed investment accounts (2020 onward)",
    "13202": "Detailed balance sheet (2020 onward)",
    "12362": "Service-sector figures",
    "12367": "Function-level expenditures",
}
HARD_CELL_LIMIT = 800_000


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def codes(meta: dict, dimension_id: str) -> list[str]:
    index = meta["dimension"][dimension_id]["category"]["index"]
    if isinstance(index, list):
        answer = [str(x) for x in index]
    elif isinstance(index, dict):
        answer = [str(k) for k, _ in sorted(index.items(), key=lambda kv: int(kv[1]))]
    else:
        raise ValueError(f"Unexpected category index: {dimension_id}")
    if not answer or len(set(answer)) != len(answer):
        raise ValueError(f"Empty or duplicate dimension codes: {dimension_id}")
    return answer


def dimension_ids(meta: dict) -> list[str]:
    ids = meta.get("id")
    dims = meta.get("dimension")
    if not isinstance(ids, list) or not isinstance(dims, dict):
        raise ValueError("Not recognizable JSON-stat2 metadata")
    if set(ids) != set(dims):
        raise ValueError("Metadata dimensions and IDs disagree")
    return [str(x) for x in ids]


def find_dimensions(meta: dict) -> tuple[str, str]:
    ids = dimension_ids(meta)
    role = meta.get("role", {})
    time_candidates = [x for x in role.get("time", []) if x in ids]
    time_candidates += [x for x in ids if x.lower() in ("tid", "time", "year")]
    if not time_candidates:
        time_candidates = [x for x in ids if "time" in x.lower() or "year" in x.lower()]
    region_candidates = [x for x in ids if "region" in x.lower() or "kommun" in x.lower()]
    if not region_candidates:
        region_candidates = [x for x in ids if "region" in str(meta["dimension"][x].get("label", "")).lower()]
    if not time_candidates or not region_candidates:
        raise ValueError(f"Cannot unambiguously locate time/region dimensions: {ids}")
    t, r = time_candidates[0], region_candidates[0]
    if t == r:
        raise ValueError("Time and region dimensions overlap")
    return t, r


def make_plan(meta: dict, table: str, years: range, max_cells: int, max_regions: int,
              pilot: bool) -> tuple[list[dict], list[int]]:
    ids = dimension_ids(meta)
    time_id, region_id = find_dimensions(meta)
    valid_years = set(codes(meta, time_id))
    missing_years = [y for y in years if str(y) not in valid_years]
    selected_years = [y for y in years if str(y) in valid_years]
    regions = codes(meta, region_id)
    other_dims = [d for d in ids if d not in (time_id, region_id)]
    other_cells = math.prod(len(codes(meta, d)) for d in other_dims)
    if other_cells > max_cells:
        raise ValueError(f"{table}: one region-year exceeds {max_cells:,} cells; additional splitting required")
    per_chunk = min(max_regions, max(1, max_cells // max(1, other_cells)))
    if pilot:
        regions, selected_years = regions[:2], selected_years[:1]
    batches = [regions[i:i + per_chunk] for i in range(0, len(regions), per_chunk)]
    result = []
    for year in selected_years:
        for batch_index, selection in enumerate(batches, start=1):
            result.append({
                "table": table, "year": year, "batch": batch_index,
                "time_id": time_id, "region_id": region_id,
                "region_codes": selection,
                "other_sizes": {d: len(codes(meta, d)) for d in other_dims},
                "expected_cells": len(selection) * other_cells,
            })
    return result, missing_years


def data_url(spec: dict) -> str:
    parameters = [
        ("lang", "en"),
        (f"valueCodes[{spec['time_id']}]", str(spec["year"])),
        (f"valueCodes[{spec['region_id']}]", ",".join(spec["region_codes"])),
    ]
    for dim_id in spec["other_sizes"]:
        parameters.append((f"valueCodes[{dim_id}]", "*"))
    parameters.append(("outputFormat", "json-stat2"))
    return f"{API}/{spec['table']}/data?{urlencode(parameters)}"


def validate_response(doc: dict, spec: dict):
    ids = dimension_ids(doc)
    time_id, region_id = spec["time_id"], spec["region_id"]
    if time_id not in ids or region_id not in ids:
        raise ValueError("Response dropped time or region dimension")
    for key, requested in ((time_id, {str(spec['year'])}),
                           (region_id, set(spec['region_codes']))):
        actual = set(codes(doc, key))
        if actual != requested:
            raise ValueError(f"Response {key} mismatch: requested {len(requested)} codes, got {len(actual)}")
    sizes = [len(codes(doc, d)) for d in ids]
    if sizes != doc.get("size"):
        raise ValueError("JSON-stat2 size disagrees with dimension index")
    n = math.prod(sizes)
    if n != spec["expected_cells"] or n > HARD_CELL_LIMIT:
        raise ValueError(f"Unexpected cell count: {n} vs planned {spec['expected_cells']}")
    values = doc.get("value")
    if isinstance(values, list):
        if len(values) != n:
            raise ValueError(f"Dense value array contains {len(values)} entries, expected {n}")
    elif isinstance(values, dict):
        if any((not str(k).isdigit()) or int(k) >= n or int(k) < 0 for k in values):
            raise ValueError("Sparse values contain invalid cell indices")
    else:
        raise ValueError("Missing or unknown JSON-stat2 values")
    status = doc.get("status", {})
    if not isinstance(status, (dict, list)):
        raise ValueError("Unexpected observation-status format")
    return n, sum(v is None for v in values) if isinstance(values, list) else n - len(values)


def save_unmodified(path: Path, data: bytes) -> str:
    """Immutable-by-default: validate existing bytes; never overwrite source files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        previous = path.read_bytes()
        if previous != data:
            raise ValueError(f"Source changed; refusing to overwrite: {path}")
        return "EXISTS_IDENTICAL"
    path.write_bytes(data)
    return "SAVED"


class Client:
    def __init__(self, pause_seconds: float):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "NorwegianMunicipalFinanceSourceAudit/1.0"
        self.pause = max(3.0, pause_seconds)  # <=20 requests/minute on one client
        self.last_request = 0.0

    def get(self, url: str) -> bytes:
        for attempt in range(4):
            elapsed = time.monotonic() - self.last_request
            if elapsed < self.pause:
                time.sleep(self.pause - elapsed)
            self.last_request = time.monotonic()
            try:
                res = self.session.get(url, timeout=120)
                if res.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                    wait = min(60.0, max(float(res.headers.get("Retry-After", "0")), 5 * 2**attempt))
                    print(f"  HTTP {res.status_code}; retry in {wait:.0f}s", flush=True)
                    time.sleep(wait)
                    continue
                res.raise_for_status()
                return res.content
            except requests.RequestException:
                if attempt == 3:
                    raise
                time.sleep(5 * 2**attempt)
        raise RuntimeError("Request exhausted")


def json_bytes(client: Client, url: str) -> tuple[bytes, dict]:
    b = client.get(url)
    obj = json.loads(b)
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object")
    return b, obj


def result_row(source, part, url, destination, status, cells="", nulls="", error=""):
    return {
        "utc": utc_now(), "source": source, "part": part, "url": url,
        "raw_file": str(destination), "status": status,
        "sha256": sha256(destination.read_bytes()) if destination.exists() else "",
        "bytes": destination.stat().st_size if destination.exists() else "",
        "cells": cells, "null_cells_minimum": nulls, "error": str(error)[:700],
    }


def write_manifest(rows: list[dict], report_dir: Path):
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = report_dir / f"phase1a2_collection_manifest_{stem}.csv"
    fields = list(result_row("", "", "", Path("/not-a-real-file"), "").keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    findings = report_dir / f"phase1a2_findings_{stem}.md"
    successful = sum(x["status"] in ("SAVED", "EXISTS_IDENTICAL") for x in rows)
    failed = sum(x["status"] == "FAIL" for x in rows)
    findings.write_text(
        "# Phase 1A.2 — Source collection findings\n\n"
        f"Created (UTC): {utc_now()}\n\n"
        f"- Successful or identical files: **{successful}**\n"
        f"- Failed checks/requests: **{failed}**\n"
        "- **Scientific readiness: BLOCKED.** Acquisition and structural checks do not establish correct accounting definitions, completeness, continuity, or matching eligibility.\n"
        "- No municipality ranking, outcome calculation, model, or hypothesis test was performed.\n"
        "- Review the manifest, source footnotes, observation statuses, and historical coverage before proceeding.\n",
        encoding="utf-8",
    )
    print(f"Manifest: {path}\nFindings: {findings}")


def acquire_klass(client: Client, raw: Path, rows: list[dict], years: range):
    sources = [("changes", f"{KLASS}/changes.json?from={years.start}-01-01&to={years.stop}-01-01")]
    sources += [(f"codes_{y}", f"{KLASS}/codesAt.json?date={y}-01-01") for y in years]
    for name, url in sources:
        p = raw / "klass" / f"{name}.json"
        try:
            b, obj = json_bytes(client, url)
            key = "codeChanges" if name == "changes" else "codes"
            if not isinstance(obj.get(key), list) or not obj[key]:
                raise ValueError(f"KLASS {name}: missing/nonempty {key} list")
            if name == "changes":
                if any(not x.get("changeOccurred") or not (x.get("oldCode") or x.get("newCode"))
                       for x in obj[key] if isinstance(x, dict)):
                    raise ValueError("KLASS change records missing date or both codes")
            state = save_unmodified(p, b)
            rows.append(result_row("KLASS", name, url, p, state, len(obj[key])))
            print("KLASS", name, state)
        except Exception as e:
            rows.append(result_row("KLASS", name, url, p, "FAIL", error=e))
            print("KLASS", name, "FAIL", str(e)[:200])


def self_test():
    meta = {
        "id": ["KOKkommuneregion0000", "ContentsCode", "Tid"],
        "dimension": {
            "KOKkommuneregion0000": {"label": "Municipal region", "category": {"index": {"0301": 0, "3101": 1, "3103": 2}}},
            "ContentsCode": {"category": {"index": ["M1", "M2"]}},
            "Tid": {"category": {"index": ["2016", "2017"]}},
        },
        "role": {"time": ["Tid"]},
    }
    specs, missing = make_plan(meta, "12134", range(2016, 2018), 4, 100, False)
    assert not missing and len(specs) == 4
    assert specs[0]["expected_cells"] == 4
    doc = {
        "id": ["KOKkommuneregion0000", "ContentsCode", "Tid"],
        "size": [2, 2, 1],
        "dimension": {
            "KOKkommuneregion0000": {"category": {"index": ["0301", "3101"]}},
            "ContentsCode": {"category": {"index": ["M1", "M2"]}},
            "Tid": {"category": {"index": ["2016"]}},
        },
        "value": [1, 2, None, 4], "status": {"2": ".."},
    }
    assert validate_response(doc, specs[0]) == (4, 1)
    doc["size"] = [3, 2, 1]
    try:
        validate_response(doc, specs[0])
        raise AssertionError("Invalid response was not rejected")
    except ValueError:
        pass
    print("PASS: offline plan, JSON-stat2, mismatch-rejection tests")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tables", nargs="+", default=["12134", "12364", "07459"])
    ap.add_argument("--klass", action="store_true", help="Also collect annual official KLASS snapshots/changes")
    ap.add_argument("--start", type=int, default=2016)
    ap.add_argument("--end", type=int, default=2025)
    ap.add_argument("--pilot", action="store_true", help="Only first available year and first 2 region codes")
    ap.add_argument("--dry-run", action="store_true", help="Plan queries; metadata only, no observations")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-cells", type=int, default=150_000)
    ap.add_argument("--max-regions", type=int, default=300)
    ap.add_argument("--pause", type=float, default=3.2)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.start > args.end or not 1 <= args.max_cells <= 750_000 or args.max_regions < 1:
        ap.error("Invalid year or chunk-size arguments")
    if any(x not in KNOWN_TABLES for x in args.tables):
        ap.error("Unknown table code; verify source catalogue before adding it")
    if args.dry_run and args.klass:
        print("Dry run skips KLASS downloads; run without --dry-run for KLASS files")
    out = Path("data/raw")
    reports = Path("reports/phase1a")
    client = Client(args.pause)
    rows = []
    errors = 0
    period = range(args.start, args.end + 1)
    for table in args.tables:
        print(f"\n=== {table}: {KNOWN_TABLES[table]} ===", flush=True)
        meta_url = f"{API}/{table}/metadata?lang=en"
        info_url = f"{API}/{table}?lang=en"
        base = out / "ssb" / ("pilot" if args.pilot else "complete") / table
        try:
            info_bytes, info = json_bytes(client, info_url)
            meta_bytes, meta = json_bytes(client, meta_url)
            if not isinstance(info.get("label"), str):
                raise ValueError("Unexpected table-info response; missing title")
            plan, missing = make_plan(meta, table, period, args.max_cells, args.max_regions, args.pilot)
            if not plan:
                raise ValueError("No requested years occur in source metadata")
            for name, b, u in (("info", info_bytes, info_url), ("metadata", meta_bytes, meta_url)):
                p = base / f"{name}.json"
                state = "DRYRUN" if args.dry_run else save_unmodified(p, b)
                rows.append(result_row(table, name, u, p, state))
            if missing:
                print(f"  COVERAGE WARNING — absent years: {missing}")
                rows.append(result_row(table, "coverage", meta_url, base / "metadata.json",
                                       "MISSING_YEARS", error=str(missing)))
            print(f"  {len(plan)} data requests; max planned cells: {max(s['expected_cells'] for s in plan):,}")
            for spec in plan:
                name = f"year_{spec['year']}_part_{spec['batch']:04d}"
                url = data_url(spec)
                p = base / f"{name}.json"
                if args.dry_run:
                    continue
                try:
                    if p.exists():
                        b = p.read_bytes()
                        doc = json.loads(b)
                        validate_response(doc, spec)
                        state = "EXISTS_IDENTICAL"
                    else:
                        b, doc = json_bytes(client, url)
                        cells, nulls = validate_response(doc, spec)
                        state = save_unmodified(p, b)
                    cells, nulls = validate_response(doc, spec)
                    rows.append(result_row(table, name, url, p, state, cells, nulls))
                    print(f"  {name} {state} cells={cells:,} null-at-least={nulls:,}", flush=True)
                except Exception as e:
                    errors += 1
                    rows.append(result_row(table, name, url, p, "FAIL", error=e))
                    print(f"  {name} FAIL {e}", flush=True)
                    # Do not continue bulk downloading if schema/data integrity failed.
                    break
        except Exception as e:
            errors += 1
            rows.append(result_row(table, "metadata_or_plan", meta_url, base / "metadata.json", "FAIL", error=e))
            print("  TABLE BLOCKED:", e, flush=True)
    if args.klass and not args.dry_run:
        acquire_klass(client, out, rows, period)
    write_manifest(rows, reports)
    print("\nSTATUS: SOURCE DATA NOT SCIENTIFICALLY VALIDATED. No ranking or modeling.")
    if args.dry_run:
        print("DRY RUN: no municipality observations were downloaded.")
    if errors or any(r["status"] == "FAIL" for r in rows):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
