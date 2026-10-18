#!/usr/bin/env python3
"""Phase 1A — Repair 02: historically valid SSB municipality-code selection.

Safe modes:
  --mode plan  : source-metadata + official year-specific KLASS, NO observations
  --mode pilot : one year, table 12134, exactly 1–2 explicit municipality codes

Bulk extraction is intentionally unavailable until historical continuity and
accounting-definition gates are approved. Never edits earlier raw files.

From repository root:
  python scripts/phase1a_02_collect_official_raw.py --self-test
  python scripts/phase1a_02_collect_official_raw.py --mode plan --years 2016
  python scripts/phase1a_02_collect_official_raw.py --mode pilot --years 2016 --region-codes 0101 0104
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests

SSB = "https://data.ssb.no/api/pxwebapi/v2/tables"
KLASS = "https://data.ssb.no/api/klass/v1/classifications/131"
KNOWN = {"12134", "12364", "12143", "07459"}
RAW = Path("data/raw")
REPORTS = Path("reports/phase1a/year_aware_collection")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def save_original(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Original source differs: {path}")
        return "EXISTS_IDENTICAL"
    with path.open("xb") as handle:
        handle.write(data)
    return "SAVED"


class Client:
    def __init__(self, pause: float = 3.2):
        self.pause = pause
        self.last = 0.0
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MunicipalFinanceYearAwareAudit/2.0"})

    def get(self, url: str) -> bytes:
        elapsed = time.monotonic() - self.last
        if elapsed < self.pause:
            time.sleep(self.pause - elapsed)
        response = self.session.get(url, timeout=90)
        self.last = time.monotonic()
        response.raise_for_status()
        return response.content


def load_or_fetch(client: Client, path: Path, url: str) -> tuple[dict, dict]:
    if path.exists():
        raw = path.read_bytes()
        source_state = "CACHED_NOT_REFETCHED"
    else:
        raw = client.get(url)
        source_state = "NEW_DOWNLOAD"
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError(f"Expected JSON object at {url}")
    if source_state == "NEW_DOWNLOAD":
        save_original(path, raw)
    return obj, {"path": str(path), "url": url, "sha256": digest(raw),
                 "bytes": len(raw), "state": source_state}


def dimensions(doc: dict) -> list[str]:
    ids, dims = doc.get("id"), doc.get("dimension")
    if not isinstance(ids, list) or not isinstance(dims, dict):
        raise ValueError("Missing JSON-stat2 dimensions")
    if not ids or len(ids) != len(set(ids)) or set(ids) != set(dims):
        raise ValueError("Inconsistent JSON-stat2 dimension IDs")
    return ids


def codes(doc: dict, dimension: str) -> list[str]:
    index = doc["dimension"][dimension]["category"]["index"]
    if isinstance(index, list):
        result = [str(x) for x in index]
    elif isinstance(index, dict):
        values = list(index.values())
        if any(type(x) is not int for x in values) or sorted(values) != list(range(len(values))):
            raise ValueError(f"Invalid category positions: {dimension}")
        result = [str(k) for k, _ in sorted(index.items(), key=lambda x: x[1])]
    else:
        raise ValueError(f"Invalid category structure: {dimension}")
    if not result or len(result) != len(set(result)):
        raise ValueError(f"Empty or repeated category codes: {dimension}")
    return result


def region_and_time(doc: dict) -> tuple[str, str]:
    ids = dimensions(doc)
    regions = [d for d in ids if "region" in d.lower() or "kommun" in d.lower()]
    years = [d for d in ids if d.lower() in ("tid", "year", "time")]
    if len(regions) != 1 or len(years) != 1 or regions[0] == years[0]:
        raise ValueError(f"Cannot uniquely identify municipality and year dimensions: {ids}")
    return regions[0], years[0]


def klass_codes(doc: dict) -> dict[str, str]:
    rows = doc.get("codes")
    if not isinstance(rows, list) or not rows:
        raise ValueError("KLASS codesAt must contain nonempty 'codes'")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("code"), str):
            raise ValueError("Malformed KLASS municipality code")
        code = row["code"]
        if code in result:
            raise ValueError(f"Duplicate KLASS code: {code}")
        result[code] = str(row.get("name", ""))
    return result


def make_year_plan(meta: dict, klass: dict, table: str, year: int,
                   requested: list[str], max_cells: int) -> dict:
    rid, tid = region_and_time(meta)
    if str(year) not in codes(meta, tid):
        raise ValueError(f"{table}: {year} absent from source metadata")
    source_codes = codes(meta, rid)
    historical = klass_codes(klass)
    eligible = [c for c in source_codes if c in historical and re.fullmatch(r"\d{4}", c)]
    if not eligible:
        raise ValueError(f"{table}/{year}: no intersection with historical KLASS municipality codes")
    if requested:
        if len(set(requested)) != len(requested) or any(not re.fullmatch(r"\d{4}", c) for c in requested):
            raise ValueError("Supply unique four-digit historical municipality codes")
        not_in_source = [c for c in requested if c not in source_codes]
        not_in_klass = [c for c in requested if c not in historical]
        if not_in_source or not_in_klass:
            raise ValueError(f"{year}: invalid historical selection; missing in SSB={not_in_source}, "
                             f"missing in KLASS={not_in_klass}")
        eligible = [c for c in source_codes if c in requested]
    others = [d for d in dimensions(meta) if d not in (rid, tid)]
    other_cells = math.prod(len(codes(meta, d)) for d in others)
    if other_cells > max_cells:
        raise ValueError(f"{table}: one municipality-year needs {other_cells} cells; split dimensions first")
    per_part = max(1, max_cells // other_cells)
    chunks = [eligible[i:i + per_part] for i in range(0, len(eligible), per_part)]
    return {"table": table, "year": year, "region_id": rid, "time_id": tid,
            "source_municipality_codes": len(source_codes), "klass_count": len(historical),
            "selected": eligible, "not_valid_in_KLASS_this_year": sum(1 for c in source_codes if c not in historical),
            "not_selected_due_to_requested_filter": sum(1 for c in source_codes if c in historical and c not in eligible),
            "other_dimensions": others, "other_cells_per_municipality": other_cells,
            "parts": [{"codes": part, "expected_cells": len(part) * other_cells}
                      for part in chunks]}


def observation_url(plan: dict, part: dict) -> str:
    params = [("lang", "en"), (f"valueCodes[{plan['time_id']}]", str(plan["year"])),
              (f"valueCodes[{plan['region_id']}]", ",".join(part["codes"]))]
    params.extend((f"valueCodes[{d}]", "*") for d in plan["other_dimensions"])
    params.append(("outputFormat", "json-stat2"))
    return f"{SSB}/{plan['table']}/data?{urlencode(params)}"


def observation_stats(doc: dict, meta: dict, plan: dict, part: dict) -> dict:
    ids = dimensions(meta)
    if dimensions(doc) != ids:
        raise ValueError("Response dimension IDs/order differ from metadata")
    for d in ids:
        expected = ([str(plan["year"])] if d == plan["time_id"] else
                    part["codes"] if d == plan["region_id"] else codes(meta, d))
        if codes(doc, d) != expected:
            raise ValueError(f"Response codes or order differ for {d}")
    sizes = [len(codes(doc, d)) for d in ids]
    n = math.prod(sizes)
    if sizes != doc.get("size") or n != part["expected_cells"]:
        raise ValueError("Response cell dimensions/count differ from query")
    values, status = doc.get("value"), doc.get("status", {})
    for label, obj in (("value", values), ("status", status)):
        if isinstance(obj, list) and len(obj) != n:
            raise ValueError(f"Invalid dense {label} length")
        if isinstance(obj, dict) and any(not str(i).isdigit() or int(i) >= n for i in obj):
            raise ValueError(f"Invalid sparse {label} indices")
        if not isinstance(obj, (list, dict)):
            raise ValueError(f"Unsupported {label} format")
    at = lambda container, i: container[i] if isinstance(container, list) else container.get(str(i))
    non_null = 0
    flags = Counter()
    for i in range(n):
        value = at(values, i)
        if value is None:
            flags[str(at(status, i) or "UNANNOTATED")] += 1
        elif type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"Non-finite/non-numeric observation at cell {i}")
        else:
            non_null += 1
    return {"cells": n, "numeric": non_null, "missing": n - non_null,
            "missing_statuses": dict(flags)}


def self_test() -> None:
    region = "KOKkommuneregion0000"
    ids = [region, "ContentsCode", "Tid"]
    def dim(items):
        return {"category": {"index": {item: i for i, item in enumerate(items)}}}
    meta = {"id": ids, "dimension": {
        region: dim(["0101", "0104", "3101", "3103"]),
        "ContentsCode": dim(["A", "B"]), "Tid": dim(["2016", "2025"])}}
    old = {"codes": [{"code": "0101", "name": "Halden"},
                     {"code": "0104", "name": "Moss"}]}
    new = {"codes": [{"code": "3101", "name": "Halden"},
                     {"code": "3103", "name": "Moss"}]}
    p16 = make_year_plan(meta, old, "12134", 2016, [], 100)
    p25 = make_year_plan(meta, new, "12134", 2025, [], 100)
    assert p16["selected"] == ["0101", "0104"]
    assert p25["selected"] == ["3101", "3103"]
    try:
        make_year_plan(meta, old, "12134", 2016, ["3101"], 100)
        raise AssertionError("Invalid modern code accepted for 2016")
    except ValueError:
        pass
    part = p16["parts"][0]
    response = {"id": ids, "size": [2, 2, 1], "dimension": {
        region: dim(["0101", "0104"]), "ContentsCode": dim(["A", "B"]),
        "Tid": dim(["2016"])}, "value": [1.0, None, 0.0, 3.0],
        "status": {"1": "."}}
    counts = observation_stats(response, meta, p16, part)
    assert counts["numeric"] == 3 and counts["missing_statuses"] == {".": 1}
    response["dimension"][region] = dim(["0104", "0101"])
    try:
        observation_stats(response, meta, p16, part)
        raise AssertionError("Changed response region order accepted")
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "raw.json"
        assert save_original(path, b"original") == "SAVED"
        assert save_original(path, b"original") == "EXISTS_IDENTICAL"
        try:
            save_original(path, b"changed")
            raise AssertionError("Original source overwritten")
        except FileExistsError:
            pass
    print("PASS: 2016/2025 KLASS selection, modern-code rejection, JSON-stat2, immutable sources")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("plan", "pilot"), default="plan")
    parser.add_argument("--table", choices=sorted(KNOWN), default="12134")
    parser.add_argument("--years", nargs="+", type=int, default=[2016])
    parser.add_argument("--region-codes", nargs="*", default=[])
    parser.add_argument("--max-cells", type=int, default=10000)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.years or len(args.years) != len(set(args.years)) or any(y < 2016 or y > 2025 for y in args.years):
        parser.error("Years must be unique and inside 2016–2025")
    if args.max_cells < 1 or args.max_cells > 10000:
        parser.error("This controlled repair allows at most 10,000 cells per request")
    if args.mode == "pilot" and (args.table != "12134" or len(args.years) != 1 or not 1 <= len(args.region_codes) <= 2):
        parser.error("Pilot requires table 12134, one year, and 1–2 explicit municipality codes")
    client = Client()
    metadata_url = f"{SSB}/{args.table}/metadata?lang=en"
    meta, meta_receipt = load_or_fetch(client, RAW / "ssb" / "year_aware_v2" /
                                       args.table / "metadata.json", metadata_url)
    plans = []
    receipts = [meta_receipt]
    for year in args.years:
        klass_url = f"{KLASS}/codesAt.json?date={year}-01-01"
        klass, receipt = load_or_fetch(client, RAW / "klass" /
                                        f"codes_{year}.json", klass_url)
        receipts.append(receipt)
        plan = make_year_plan(meta, klass, args.table, year, args.region_codes, args.max_cells)
        plans.append(plan)
        print(f"{args.table}/{year}: {len(plan['selected'])} historical codes; "
              f"{len(plan['parts'])} planned part(s); KLASS/SSB intersection PASS")
    result = {"mode": args.mode, "created_utc": datetime.now(timezone.utc).isoformat(),
              "scientific_approval": "BLOCKED_ACCOUNTING_AND_HISTORICAL_CONTINUITY_REVIEW",
              "sources": receipts, "plans": plans, "observations": []}
    if args.mode == "pilot":
        plan = plans[0]
        part = plan["parts"][0]
        url = observation_url(plan, part)
        source_file = (RAW / "ssb" / "year_aware_v2" / args.table /
                       f"year_{plan['year']}_codes_{'-'.join(part['codes'])}.json")
        raw = client.get(url)
        doc = json.loads(raw)
        counts = observation_stats(doc, meta, plan, part)
        state = save_original(source_file, raw)
        result["observations"].append({"url": url, "file": str(source_file),
                                        "sha256": digest(raw), "state": state, **counts})
        print(f"PILOT: {counts['numeric']}/{counts['cells']} numeric; "
              f"missing={counts['missing']} | {source_file} | {state}")
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = REPORTS / f"phase02_year_aware_{stamp()}.json"
    with report.open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"WROTE: {report}")
    print("SCIENTIFIC APPROVAL: BLOCKED — no full collection or case selection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
