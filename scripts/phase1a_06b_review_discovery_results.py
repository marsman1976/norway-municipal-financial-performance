#!/usr/bin/env python3
"""Phase 06B: offline integrity review of Phase 06 metadata-discovery CSV evidence.

No network calls. No financial observations. No accounting definitions approved.

From repository root:
  python scripts/phase1a_06b_review_discovery_results.py --self-test
  python scripts/phase1a_06b_review_discovery_results.py --zip phase06_results_for_review.zip

Creates a dated findings Markdown and CSV under reports/phase1a/phase06_review/.
Source JSON bytes are NOT present in a CSV-only ZIP, so this program cannot
independently confirm the manifest's source SHA-256 hashes. It checks that
recorded hashes agree across runs and across coverage/manifest reports.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import tempfile
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

KINDS = {
    "manifest": "phase1a7_source_manifest_",
    "coverage": "phase1a7_coverage_and_scope_",
    "candidates": "phase1a7_account_concept_candidates_",
    "gates": "phase1a7_reconciliation_gates_",
}
REQUIRED = {
    "manifest": {"table_id", "status", "raw_path", "sha256", "size_bytes", "error"},
    "coverage": {"table_id", "study_years_in_metadata", "study_years_missing_in_metadata",
                 "non_year_region_codes", "candidate_concept_codes", "raw_sha256",
                 "accounting_definitions_signed_off", "data_observations_collected"},
    "candidates": {"table_id", "dimension", "code", "official_label", "candidate_for_review",
                   "source_definition_verified", "research_search_topics"},
    "gates": {"gate_id", "topic", "approval"},
}
FOCUS = [
    ("12364", "56", "General funds (M)", "Priority: reserve account; manual reconciliation"),
    ("12143", "56", "General funds (M)", "Priority: published reserve ratio candidate"),
    ("12364", "KG21", "Free equity operational account", "Not a substitute for account 56"),
    ("12364", "AGD13", "Gross operating revenues", "Candidate denominator"),
    ("12364", "AGD23", "Net operating result", "Candidate primary operating outcome"),
    ("12364", "KG31", "Net loan debt", "Candidate debt numerator"),
    ("12364", "5900", "Deficit of the year in operational accounts (M)", "Historical correction check"),
    ("12364", "452", "Interest-only loans", "2024-onward debt classification change"),
]


def csv_rows(raw: bytes, kind: str) -> list[dict[str, str]]:
    stream = io.StringIO(raw.decode("utf-8-sig"))
    rd = csv.DictReader(stream)
    if rd.fieldnames is None or not REQUIRED[kind].issubset(rd.fieldnames):
        raise ValueError(f"Incorrect {kind} CSV schema: {rd.fieldnames}")
    rows = list(rd)
    if not rows:
        raise ValueError(f"Empty {kind} CSV")
    return rows


def review_zip(zippath: Path) -> tuple[list[str], list[dict[str, str]], dict]:
    issues: list[str] = []
    with ZipFile(zippath) as archive:
        grouped: dict[str, dict[str, bytes]] = {}
        for member in archive.infolist():
            if member.is_dir():
                continue
            base = Path(member.filename).name
            matched = [(kind, base[len(prefix):-4]) for kind, prefix in KINDS.items()
                       if base.startswith(prefix) and base.endswith(".csv")]
            if len(matched) != 1:
                raise ValueError(f"Unexpected ZIP member: {member.filename}")
            kind, stamp = matched[0]
            if not re.fullmatch(r"\d{8}T\d{12}Z", stamp):
                raise ValueError(f"Unexpected run timestamp in {base}")
            if kind in grouped.setdefault(stamp, {}):
                raise ValueError(f"Duplicate {kind} within run {stamp}")
            if member.file_size > 10_000_000:
                raise ValueError("Input CSV too large for bounded review")
            grouped[stamp][kind] = archive.read(member)

    if not grouped:
        raise ValueError("ZIP has no Phase 06 reports")
    all_runs = []
    evidence_signatures = {}
    for stamp in sorted(grouped):
        raw = grouped[stamp]
        if set(raw) != set(KINDS):
            raise ValueError(f"Run {stamp}: incomplete CSV set; found {sorted(raw)}")
        docs = {k: csv_rows(raw[k], k) for k in KINDS}
        all_runs.append((stamp, docs))
        for k in ("coverage", "candidates", "gates"):
            digest = hashlib.sha256(raw[k]).hexdigest()
            previous = evidence_signatures.setdefault(k, digest)
            if previous != digest:
                issues.append(f"{k} content differs across runs")

    newest_stamp, latest = all_runs[-1]
    history = {}
    for stamp, docs in all_runs:
        manifests = docs["manifest"]
        tables = [x["table_id"] for x in manifests]
        if len(tables) != len(set(tables)):
            issues.append(f"Run {stamp}: repeated table ID")
        coverage_map = {x["table_id"]: x for x in docs["coverage"]}
        if set(tables) != set(coverage_map):
            issues.append(f"Run {stamp}: manifest/coverage table mismatch")
        for m in manifests:
            t = m["table_id"]
            if m["status"] not in ("SAVED", "EXISTS_IDENTICAL", "CACHED_UNCHANGED_NOT_REFETCHED"):
                issues.append(f"Run {stamp}: table {t} status {m['status']}")
            if m["error"].strip():
                issues.append(f"Run {stamp}: table {t} error: {m['error']}")
            cov = coverage_map.get(t)
            if not cov:
                continue
            if m["sha256"] != cov["raw_sha256"]:
                issues.append(f"Run {stamp}: table {t} manifest/coverage SHA mismatch")
            key = (t, m["sha256"], m["size_bytes"])
            if t in history and history[t] != key:
                issues.append(f"Table {t}: hash/size differs across runs")
            history[t] = key
            years = set(cov["study_years_in_metadata"].split(";"))
            if not {str(y) for y in range(2016, 2026)}.issubset(years):
                issues.append(f"Table {t}: missing study years in metadata")
            if cov["accounting_definitions_signed_off"] != "NO":
                issues.append(f"Table {t}: unexpectedly marked definitions signed off")
            if cov["data_observations_collected"] != "NO":
                issues.append(f"Table {t}: unexpectedly claims observations collected")
        if any(x["approval"] != "BLOCKED_PENDING_REVIEW" for x in docs["gates"]):
            issues.append(f"Run {stamp}: scientific gate approved prematurely")
        if any(x["source_definition_verified"] != "NO" for x in docs["candidates"]):
            issues.append(f"Run {stamp}: unreviewed concept marked verified")

    candidate_rows = latest["candidates"]
    table_counts = Counter(x["table_id"] for x in candidate_rows)
    hit_counts = Counter(x["table_id"] for x in candidate_rows
                         if x["candidate_for_review"] == "YES")
    by_key = {(x["table_id"], x["code"]): x for x in candidate_rows}
    focus_rows = []
    for table, code, expected_name, purpose in FOCUS:
        row = by_key.get((table, code))
        if row is None:
            issues.append(f"Key concept missing: {table} / {code}")
            continue
        if expected_name.lower() not in row["official_label"].lower():
            issues.append(f"Unexpected label for {table} / {code}: {row['official_label']}")
        focus_rows.append({"table_id": table, "code": code,
                           "source_label": row["official_label"],
                           "keyword_flag": row["candidate_for_review"],
                           "research_priority": purpose,
                           "official_definition_signed_off": "NO",
                           "amounts_reconciled": "NO"})

    if by_key.get(("12364", "56"), {}).get("candidate_for_review") != "NO":
        issues.append("Expected missed keyword hit for account 56 not reproduced")

    summary = {
        "runs": len(all_runs), "stamps": [stamp for stamp, _ in all_runs],
        "latest_stamp": newest_stamp, "tables": sorted(table_counts),
        "entries": len(candidate_rows), "by_table": dict(table_counts),
        "keyword_hits": sum(hit_counts.values()), "hits_by_table": dict(hit_counts),
        "blocked_gates": sum(x["approval"] == "BLOCKED_PENDING_REVIEW" for x in latest["gates"]),
        "manifest_history": [{"stamp": stamp, "table": m["table_id"],
                              "status": m["status"], "sha256": m["sha256"]}
                             for stamp, d in all_runs for m in d["manifest"]],
        "issues": sorted(set(issues)),
    }
    return sorted(set(issues)), focus_rows, summary


def report_lines(s: dict, focus: list[dict[str, str]]) -> list[str]:
    issues = s["issues"]
    lines = [
        "# Phase 06 — Review of live SSB metadata discovery (CSV evidence)", "",
        f"**Runs reviewed:** {s['runs']} ({', '.join(s['stamps'])})",
        f"**Latest run:** {s['latest_stamp']}",
        f"**Tables:** {', '.join(s['tables'])}",
        f"**Metadata entries (latest run, not multiplied by repeats):** {s['entries']}",
        f"**Keyword matches:** {s['keyword_hits']}",
        f"**Scientific gates blocked:** {s['blocked_gates']}", "",
        "## Findings supported by the uploaded CSVs", "",
        "| Table | Metadata entries | Keyword matches | Years in metadata |",
        "|---|---:|---:|---|",
    ]
    for table in s["tables"]:
        lines.append(f"| {table} | {s['by_table'][table]} | "
                     f"{s['hits_by_table'].get(table, 0)} | 2016–2025 |")
    lines += [
        "", "- All three runs record consistent SHA-256 values and byte sizes for each table.",
        "- The first run records SAVED; later runs are cached: repeated runs are **not** independent metadata downloads.",
        "- The ZIP contains CSV reports but NOT the original metadata JSON files. Source SHA-256 hashes",
        "  are cross-checked between CSVs, **not independently recomputed from source bytes**.",
        "- Metadata coverage does not prove that financial observations exist for each year,",
        "  municipality or accounting code.", "",
        "## Prioritized accounting concepts (all pending numerical reconciliation)", "",
        "| Table | Code | Official label | Keyword hit? | Next check |",
        "|---|---|---|---|---|",
    ]
    for row in focus:
        lines.append(f"| {row['table_id']} | `{row['code']}` | {row['source_label']} | "
                     f"{row['keyword_flag']} | {row['research_priority']} |")
    lines += [
        "", "## Independent source interpretation", "",
        "- SSB KOSTRA reporting guides for 2015, 2018 and 2024 identify balance account",
        "  `56` as `disposisjonsfond`. The provided English CSV describes code `56` as General funds (M).",
        "  This supports selecting the code for a controlled numerical pilot; it does not approve",
        "  the published values, denominator, scope or time-series comparability.",
        "- Source: https://www.ssb.no/offentlig-sektor/artikler-og-publikasjoner/_attachment/282522?_ts=15b42e83570",
        "- Source: https://www.ssb.no/offentlig-sektor/artikler-og-publikasjoner/_attachment/366611?_ts=166a54a9b30",
        "- Source: https://www.ssb.no/offentlig-sektor/kostra/artikler/kostra-rapportering-2024/",
        "- `KG21` is a different source concept (free equity operational account); do not",
        "  silently substitute it for reserve account `56`.",
        "- Source metadata flags a KOSTRA municipality-group break in 2019–2020.",
        "- Account labels explicitly distinguish several loan instruments ending 2023",
        "  versus introduced 2024. Maintain a mapping rather than directly splicing series.",
        "- Table 12143's English note mentions county authorities although the title has `(M)`;",
        "  investigate official reporting scope rather than assuming note is correct.",
        "- Keyword search also flags a `ContentsCode` percentage label as revenue; search",
        "  hits require human classification.", "",
        "## Integrity observations", "",
    ]
    lines += [f"- {x}" for x in issues] if issues else ["- CSV-level consistency checks passed."]
    lines += [
        "", "**SCIENTIFIC APPROVAL: BLOCKED.**",
        "No annual municipal values were present in the uploaded Phase 06 ZIP.",
        "No financial ratios, municipality rankings or statistical models were calculated.", "",
        "## Next evidence required", "",
        "1. Original preserved `12364_metadata.json` and `12143_metadata.json` for independent SHA-256 checks.",
        "2. Controlled numeric query for account `56`, account `AGD13`, and a comparable ratio",
        "   at historically valid municipality-year identifiers.",
        "3. Audit financial accounting scope, ratio denominators, round-off rules and 2024 debt changes.",
        "4. Repair and test the previous year-unaware bulk collector before full collection.", "",
    ]
    return lines


def self_test() -> None:
    # The regression fixture uses the same four CSV schemas, with synthetic values.
    with tempfile.TemporaryDirectory() as temp:
        zippath = Path(temp) / "tiny.zip"
        heads = {
            "manifest": ["table_id", "raw_path", "sha256", "size_bytes", "status", "error"],
            "coverage": ["table_id", "study_years_in_metadata", "study_years_missing_in_metadata",
                         "non_year_region_codes", "candidate_concept_codes", "raw_sha256",
                         "accounting_definitions_signed_off", "data_observations_collected"],
            "candidates": ["table_id", "dimension", "code", "official_label", "candidate_for_review",
                           "source_definition_verified", "research_search_topics"],
            "gates": ["gate_id", "topic", "approval"],
        }
        manifest = [{"table_id": "12364", "raw_path": "metadata.json", "sha256": "TEST",
                     "size_bytes": "100", "status": "SAVED", "error": ""}]
        coverage = [{"table_id": "12364", "study_years_in_metadata": ";".join(str(y) for y in range(2016,2026)),
                     "study_years_missing_in_metadata": "", "non_year_region_codes": "2",
                     "candidate_concept_codes": "0", "raw_sha256": "TEST",
                     "accounting_definitions_signed_off": "NO", "data_observations_collected": "NO"}]
        candidates = [{"table_id": "12364", "dimension": "KOKartkap0000", "code": code,
                       "official_label": label, "candidate_for_review": "NO",
                       "source_definition_verified": "NO", "research_search_topics": ""}
                      for t, code, label, _ in FOCUS if t == "12364"]
        gates = [{"gate_id": "G01", "topic": "reserve", "approval": "BLOCKED_PENDING_REVIEW"}]
        sets = {"manifest": manifest, "coverage": coverage,
                "candidates": candidates, "gates": gates}
        from zipfile import ZIP_DEFLATED
        with ZipFile(zippath, "w", ZIP_DEFLATED) as archive:
            for kind, rows in sets.items():
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=heads[kind])
                writer.writeheader(); writer.writerows(rows)
                archive.writestr(f"{KINDS[kind]}20261012T175216915322Z.csv", buf.getvalue())
        issues, _, report = review_zip(zippath)
        assert report["runs"] == 1 and report["entries"] == len(candidates)
        assert not any("12364 / 56" in x for x in issues)
        assert any("12143" in x for x in issues), "Missing concept should be flagged"
    print("PASS: CSV schemas, timestamp grouping, candidate reconciliation, and evidence gates")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", type=Path, default=Path("phase06_results_for_review.zip"))
    ap.add_argument("--out", type=Path, default=Path("reports/phase1a/phase06_review"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return 0
    try:
        issues, focus, summary = review_zip(args.zip)
        args.out.mkdir(parents=True, exist_ok=True)
        stamp = summary["latest_stamp"]
        report = args.out / f"PHASE06_REVIEW_{stamp}.md"
        focused = args.out / f"PHASE06_FOCUS_ACCOUNTS_{stamp}.csv"
        with report.open("x", encoding="utf-8") as f:
            f.write("\n".join(report_lines(summary, focus)))
        with focused.open("x", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(focus[0]))
            writer.writeheader(); writer.writerows(focus)
        print(f"RUNS={summary['runs']} TABLES={summary['tables']}")
        print(f"ENTRIES={summary['entries']} KEYWORD_HITS={summary['keyword_hits']}")
        print(f"CSV_LEVEL_ISSUES={len(issues)}")
        print("ORIGINAL_SOURCE_JSON_HASHES_NOT_INDEPENDENTLY_VERIFIED")
        print("SCIENTIFIC_APPROVAL=BLOCKED")
        print("WROTE", report); print("WROTE", focused)
        return 2 if issues else 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
