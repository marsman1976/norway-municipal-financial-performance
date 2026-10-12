#!/usr/bin/env python3
"""Phase 1A.7 — Discover and archive official SSB account metadata (NO observations).

Purpose:
  * Preserve metadata from tables holding KOSTRA financial accounts/ratios.
  * Inventory exact dimension codes, source labels, units, notes and coverage.
  * Highlight candidate reserve/debt/operating concepts for HUMAN review.
  * Record critical historical accounting comparability questions.

Does NOT download municipal financial observations, compute ratios, sign off
accounting definitions, match municipalities, or approve full panel collection.

Run from the repository root:
  python scripts/phase1a_06_discover_financial_accounts.py --self-test
  python scripts/phase1a_06_discover_financial_accounts.py

Dependency: requests (included in project requirements).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

URL_BASE = "https://data.ssb.no/api/pxwebapi/v2/tables"
DEFAULT_TABLES = ("12134", "12364", "12143", "13202", "13551", "13552")
STUDY_YEARS = tuple(str(y) for y in range(2016, 2026))
SOURCE_DIR = Path("data/raw/metadata/phase1a7")
REPORT_DIR = Path("reports/phase1a/financial_account_discovery")

# Hints are NON-AUTHORITATIVE. A hit is a search lead, not a ledger definition.
TOPIC_TERMS = {
    "RESERVE_OR_DISPOSISJONSFOND": (
        "disposisjonsfond", "distributable reserve", "distributable fund",
        "unrestricted reserve", "free equity", "fri egenkapital"),
    "OPERATING_RESULT": (
        "netto driftsresultat", "net operating surplus", "net operating result",
        "operating result", "operating surplus", "driftsresultat", "merforbruk",
        "akkumulert", "accumulated result", "deficit"),
    "REVENUE": (
        "gross operating revenue", "brutto driftsinntekter", "unrestricted revenues",
        "frie inntekter", "tax revenues", "rammetilskudd"),
    "DEBT_INTEREST": (
        "net loan debt", "netto laanegjeld", "netto lanegjeld",
        "loans", "interest", "rente", "gjeld", "debt"),
    "LIQUIDITY": ("working capital", "arbeidskapital", "likviditet", "liquidity"),
    "INVESTMENT": ("gross investment", "investering", "investment", "capital expenditure"),
}

# Formal audit gates are intentional scientific blockers, not code errors.
HISTORICAL_GATES = [
    ("G01", "P2 unrestricted reserve stock", "Locate exact disposisjonsfond/credit balance, denominator, and scope; distinguish free equity after deficits."),
    ("G02", "2015-2017 sign convention", "Check SSB correction log for account 5900 operating deficit displayed negative for 2015-2017."),
    ("G03", "2018-2019 free-equity correction", "Check SSB changes to the handling of account 5900 in free equity and accumulated accounting result."),
    ("G04", "2019-2020 KOSTRA group break", "Freeze each baseline group's official classification version. Do not equate revised groups."),
    ("G05", "2020 detailed-account coverage", "Document that some detailed operating, investment and balance datasets begin 2020; do not backfill 2016-2019."),
    ("G06", "Municipal versus consolidated", "Verify reporting unit for every indicator and its ledger components before reconciliation."),
    ("G07", "Historical geography", "Intersect municipality codes valid for each year with corresponding SSB table region codes; classify splits/mergers."),
    ("G08", "Account-to-ratio reconstruction", "Use account codes and official formulas to reproduce published key figures with frozen rounding tolerances."),
    ("G09", "Source revisions/footnotes", "Preserve publication date, notes, metadata hashes, source corrections and raw-version change log."),
    ("G10", "Time-series coverage", "Verify 2016-2025 availability and actual non-null observations for every required municipality-year."),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def normalize(text: Any) -> str:
    s = unicodedata.normalize("NFKD", str(text or "")).casefold()
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return " ".join(s.split())


def topics_for(text: str) -> list[str]:
    t = normalize(text)
    return [group for group, terms in TOPIC_TERMS.items()
            if any(normalize(term) in t for term in terms)]


def ordered_categories(dim: dict) -> list[tuple[str, str]]:
    category = dim.get("category", {})
    ix = category.get("index")
    if isinstance(ix, dict):
        positions = list(ix.values())
        if any(isinstance(p, bool) or not isinstance(p, int) for p in positions):
            raise ValueError("Category index positions are not integers")
        if sorted(positions) != list(range(len(positions))):
            raise ValueError("Category index positions are missing or duplicated")
        keys = [str(k) for k, _ in sorted(ix.items(), key=lambda pair: pair[1])]
    elif isinstance(ix, list):
        keys = [str(x) for x in ix]
    else:
        raise ValueError("Missing JSON-stat2 category index")
    if not keys or len(keys) != len(set(keys)):
        raise ValueError("Category dimension empty or contains repeated values")
    labels = category.get("label", {})
    if labels is None:
        labels = {}
    if not isinstance(labels, dict):
        raise ValueError("Unexpected category label map")
    return [(key, str(labels.get(key, key))) for key in keys]


def inspect_metadata(doc: dict, table: str) -> tuple[dict, list[dict]]:
    dims = doc.get("dimension")
    ids = doc.get("id")
    if not isinstance(doc, dict) or not isinstance(dims, dict) or not isinstance(ids, list):
        raise ValueError("Missing JSON-stat2 dimension metadata")
    if set(ids) != set(dims) or len(ids) != len(dims):
        raise ValueError("Metadata dimension IDs disagree with dimension map")
    year_ids = [i for i in ids if i.lower() in ("tid", "time", "year")]
    reg_ids = [i for i in ids if "region" in i.casefold() or "kommun" in i.casefold()]
    if len(year_ids) != 1 or len(reg_ids) != 1:
        raise ValueError(f"Cannot unambiguously identify time/region dimensions: {ids}")
    year_id, region_id = year_ids[0], reg_ids[0]
    years = {code for code, _ in ordered_categories(dims[year_id])}
    available = [y for y in STUDY_YEARS if y in years]
    missing = [y for y in STUDY_YEARS if y not in years]
    concept_rows = []
    for dim_id in ids:
        if dim_id in (year_id, region_id):
            continue
        dim = dims[dim_id]
        cat = dim["category"]
        unit_map = cat.get("unit", {})
        notes_map = cat.get("note", {})
        for code, label in ordered_categories(dim):
            unit = unit_map.get(code) if isinstance(unit_map, dict) else unit_map
            note = notes_map.get(code) if isinstance(notes_map, dict) else notes_map
            topics = topics_for(label)
            concept_rows.append({
                "table_id": table, "dimension": dim_id, "code": code,
                "official_label": label,
                "source_unit_raw_json": json.dumps(unit, ensure_ascii=False, sort_keys=True) if unit is not None else "",
                "source_note_raw_json": json.dumps(note, ensure_ascii=False, sort_keys=True) if note else "",
                "research_search_topics": ";".join(topics),
                "candidate_for_review": "YES" if topics else "NO",
                "accounting_scope_verified": "NO",
                "numerator_denominator_verified": "NO",
                "historical_comparability_verified": "NO",
                "source_definition_verified": "NO",
                "review_status": "REVIEW_REQUIRED" if topics else "CATALOGUED_NOT_REVIEWED",
                "statbank_url": f"https://www.ssb.no/en/statbank1/table/{table}/",
            })
    entry = {
        "table_id": table, "title": str(doc.get("label", "")),
        "metadata_updated": str(doc.get("updated", "")),
        "table_source": str(doc.get("source", "")),
        "dimensions": ";".join(ids), "region_dimension": region_id,
        "region_count": len(ordered_categories(dims[region_id])),
        "year_dimension": year_id,
        "study_years_in_metadata": ";".join(available),
        "study_years_missing_in_metadata": ";".join(missing),
        "non_year_region_codes": len(concept_rows),
        "candidate_concept_codes": sum(r["candidate_for_review"] == "YES" for r in concept_rows),
        "table_notes_raw_json": json.dumps(doc.get("note", []), ensure_ascii=False),
        "source_accounting_scope": "NOT_VERIFIED_FROM_LEDGER",
        "accounting_definitions_signed_off": "NO",
        "data_observations_collected": "NO",
        "statbank_url": f"https://www.ssb.no/en/statbank1/table/{table}/",
    }
    return entry, concept_rows


def preserve_metadata(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(
                f"Metadata changed since original archive: {path}. "
                "Preserve version history separately; do not overwrite."
            )
        return "EXISTS_IDENTICAL"
    with path.open("xb") as f:
        f.write(data)
    return "SAVED"


def fetch_or_cache(table: str, source_dir: Path, pause_seconds: float) -> tuple[bytes, str, str]:
    url = f"{URL_BASE}/{table}/metadata?lang=en"
    path = source_dir / f"{table}_metadata.json"
    if path.is_file():
        return path.read_bytes(), "CACHED_UNCHANGED_NOT_REFETCHED", url
    response = requests.get(url, timeout=75,
                            headers={"User-Agent": "MunicipalFinanceMetadataDiscovery/1.0"})
    response.raise_for_status()
    data = response.content
    obj = json.loads(data)
    inspect_metadata(obj, table)  # refuse to archive malformed metadata
    state = preserve_metadata(path, data)
    if pause_seconds:
        time.sleep(pause_seconds)
    return data, state, url


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("x", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def self_test():
    def d(codes, labels=None):
        return {"category": {"index": {s: i for i, s in enumerate(codes)},
                             "label": labels or {s: s for s in codes}}}
    meta = {
        "id": ["KOKkommuneregion0000", "KOKartkap0000", "ContentsCode", "Tid"],
        "dimension": {
            "KOKkommuneregion0000": d(["0101", "0104"]),
            "KOKartkap0000": d(["1", "2"], {"1": "Disposisjonsfond", "2": "Net interest"}),
            "ContentsCode": d(["S"], {"S": "Sum (NOK 1000)"}),
            "Tid": d(["2016", "2020", "2025"]),
        }, "label": "Synthetic for unit test", "note": []
    }
    info, rows = inspect_metadata(meta, "12364")
    assert info["study_years_missing_in_metadata"].startswith("2017")
    assert len(rows) == 3 and rows[0]["research_search_topics"].startswith("RESERVE")
    assert rows[1]["research_search_topics"] == "DEBT_INTEREST"
    assert all(row["source_definition_verified"] == "NO" for row in rows)
    try:
        inspect_metadata({**meta, "id": ["Tid"]}, "12364")
        raise AssertionError("Broken dimensions accepted")
    except ValueError:
        pass
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "orig.json"
        assert preserve_metadata(p, b"original") == "SAVED"
        assert preserve_metadata(p, b"original") == "EXISTS_IDENTICAL"
        try:
            preserve_metadata(p, b"changed")
            raise AssertionError("Overwrote immutable metadata")
        except FileExistsError:
            pass
    print("PASS: account metadata inventory, topic discovery, coverage flags, immutable archive")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tables", nargs="+", default=list(DEFAULT_TABLES))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    ap.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    ap.add_argument("--pause", type=float, default=3.2)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if any(not (t.isdigit() and len(t) == 5) for t in args.tables):
        ap.error("Table identifiers must be 5 digits")
    if len(set(args.tables)) != len(args.tables):
        ap.error("Duplicate table identifiers")
    if not 0 <= args.pause <= 300:
        ap.error("Invalid pause")
    args.report_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    inventory: list[dict] = []
    concepts: list[dict] = []
    errors = 0
    for table in args.tables:
        url = f"{URL_BASE}/{table}/metadata?lang=en"
        path = args.source_dir / f"{table}_metadata.json"
        try:
            raw, state, url = fetch_or_cache(table, args.source_dir, args.pause)
            meta = json.loads(raw)
            record, candidates = inspect_metadata(meta, table)
            record["raw_sha256"] = sha256(raw)
            inventory.append(record)
            concepts.extend(candidates)
            manifest.append({"table_id": table, "metadata_url": url,
                             "raw_path": str(path), "sha256": sha256(raw),
                             "size_bytes": len(raw), "status": state, "error": ""})
            print(f"[{table}] {state} | {len(candidates)} concept/measure codes | "
                  f"{record['candidate_concept_codes']} keyword candidates | "
                  f"{len(record['study_years_missing_in_metadata'].split(';')) if record['study_years_missing_in_metadata'] else 0} years absent")
        except (requests.RequestException, ValueError, OSError, KeyError, TypeError) as exc:
            errors += 1
            manifest.append({"table_id": table, "metadata_url": url,
                             "raw_path": str(path), "sha256": "", "size_bytes": "",
                             "status": "FAILED", "error": f"{type(exc).__name__}: {exc}"[:400]})
            print(f"[{table}] FAILED: {type(exc).__name__}: {exc}")
    token = stamp()
    outputs = {
        "manifest": args.report_dir / f"phase1a7_source_manifest_{token}.csv",
        "inventory": args.report_dir / f"phase1a7_coverage_and_scope_{token}.csv",
        "candidates": args.report_dir / f"phase1a7_account_concept_candidates_{token}.csv",
        "gates": args.report_dir / f"phase1a7_reconciliation_gates_{token}.csv",
        "summary": args.report_dir / f"phase1a7_findings_{token}.md",
    }
    write_csv(outputs["manifest"], manifest,
              ["table_id", "metadata_url", "raw_path", "sha256", "size_bytes", "status", "error"])
    write_csv(outputs["inventory"], inventory, [
        "table_id", "title", "metadata_updated", "table_source", "dimensions",
        "region_dimension", "region_count", "year_dimension",
        "study_years_in_metadata", "study_years_missing_in_metadata",
        "non_year_region_codes", "candidate_concept_codes", "table_notes_raw_json",
        "source_accounting_scope", "accounting_definitions_signed_off",
        "data_observations_collected", "statbank_url", "raw_sha256"])
    write_csv(outputs["candidates"], concepts, [
        "table_id", "dimension", "code", "official_label",
        "source_unit_raw_json", "source_note_raw_json", "research_search_topics",
        "candidate_for_review", "accounting_scope_verified",
        "numerator_denominator_verified", "historical_comparability_verified",
        "source_definition_verified", "review_status", "statbank_url"])
    write_csv(outputs["gates"], [
        {"gate_id": gid, "topic": topic, "required_evidence": desc, "approval": "BLOCKED_PENDING_REVIEW"}
        for gid, topic, desc in HISTORICAL_GATES],
        ["gate_id", "topic", "required_evidence", "approval"])
    approved = sum(r["status"] != "FAILED" for r in manifest)
    outputs["summary"].write_text(
        "# Phase 1A.7 — Financial-account metadata discovery findings\n\n"
        f"Run UTC: {datetime.now(timezone.utc).isoformat()}\n\n"
        f"Requested metadata tables: **{len(args.tables)}**; successful/cached: **{approved}**; failures: **{errors}**.\n\n"
        f"Total concept entries examined: **{len(concepts)}**; keyword matches for review: "
        f"**{sum(x['candidate_for_review']=='YES' for x in concepts)}**.\n\n"
        "**Every candidate remains unverified.** A keyword match is not evidence of a usable ledger account.\n\n"
        "**No financial observations downloaded and no historical accounting definitions approved.**\n\n"
        "Scientific gate: BLOCKED_PENDING_ACCOUNTING_SCOPE_DEFINITIONS_AND_YEAR_COMPARABILITY.\n\n"
        "Important official correction log: https://www.ssb.no/kostra/rettinger-i-tidligere-ars-publiserte-data\n\n"
        "Next: inspect candidate IDs and original SSB footnotes, confirm 2016-2019 historical accounting treatment, "
        "reconcile P2 disposisjonsfond, and then design a year-aware numeric account pilot.\n",
        encoding="utf-8")
    for k, path in outputs.items():
        print(f"WROTE {k}: {path}")
    print("SCIENTIFIC GATE: BLOCKED (metadata discovery is not accounting verification).")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
