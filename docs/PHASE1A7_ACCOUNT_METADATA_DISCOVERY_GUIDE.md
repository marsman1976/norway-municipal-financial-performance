# Phase 1A.7 — Account-source metadata discovery (learning guide)

## Goal
Prior Phase 1A.6 confirmed that a corrected 2016 pilot returned 18/18 numerical observations for Halden (`0101`) and Moss (`0104`) across nine published financial indicators. This does **not** validate underlying accounting formulas or historical comparability.

In this step, we identify and archive official **source metadata** for six SSB tables, including table `12364` for base financial amounts and `12143` for municipal-group financial ratios. The script inventories accounting concept IDs and highlights **possible** reserve/fund, revenue, operating-result, debt, interest, liquidity and investment candidates.

## Install and run in VS Code

Save `phase1a_06_discover_financial_accounts.py` to `scripts/` in your existing repository. From the repository root:

```bash
source .venv/bin/activate
python scripts/phase1a_06_discover_financial_accounts.py --self-test
python scripts/phase1a_06_discover_financial_accounts.py --tables 12364 12143
```

That **first live run** makes at most two official metadata queries, **not** financial-data requests. Review output before adding more tables:

```bash
python scripts/phase1a_06_discover_financial_accounts.py
```

Subsequent runs reuse the immutable cached metadata; they do not recheck for later source revisions. If you later need new versions, use a separately versioned archive directory rather than overwrite the saved originals.

## Files produced

- `data/raw/metadata/phase1a7/{table}_metadata.json`: official unmodified metadata bytes, SHA-256 recorded in manifest.
- `reports/phase1a/financial_account_discovery/phase1a7_source_manifest_*.csv`: retrieval evidence and failures.
- `phase1a7_coverage_and_scope_*.csv`: table titles, dimensions, source years, missing study years, source notes.
- `phase1a7_account_concept_candidates_*.csv`: all non-region/time category codes and official labels. Keyword hits are search leads **only**.
- `phase1a7_reconciliation_gates_*.csv`: research questions that must be answered before data are authorized for analysis.
- `phase1a7_findings_*.md`: counts and explicit scientific-readiness decision.

## Why this matters

1. **A ratio name does not give the ledger formula.** Metadata help discover source codes, not necessarily numerator and denominator.
2. **Municipal versus consolidated scope must match.** A standalone municipality series cannot automatically be reconstructed with a municipal-group table.
3. **`disposisjonsfond` is not identical to free equity after subtracting accumulated operating deficits.** The P2 case-selection outcome is blocked until its exact source accounts and denominator are verified.
4. **SSB has corrected the historical sign presentation of operating deficits (`merforbruk`, account 5900) for 2015–2017 and corrections to the 2018–2019 free-equity calculation.** This must be documented before comparing decade-long ratios.
5. **KOSTRA group classification changed around 2019–2020.** Classification continuity and accounting-value continuity are different issues.
6. **Some detailed account tables begin in 2020.** Flag missing 2016–2019 historical coverage rather than interpolate or assume stable account structures.

## What constitutes PASS?

- Metadata from intended official sources is saved with traceable SHA-256 and units/notes.
- Candidate ledger concepts have exact SSB codes, formal numerator/denominator definitions, accounting scope, and years **reviewed against official source docs**.
- Historical source and entity-code changes are documented, and actual `disposisjonsfond` can be distinguished from adjusted free equity.
- A later **separate** data pilot reproduces published financial ratios within a justified rounding tolerance.

The script's successful execution is **metadata-collection PASS only**. It does not close the scientific gate.

## Official references

- SSB 12364: https://www.ssb.no/en/statbank1/table/12364/
- SSB 12134: https://www.ssb.no/en/statbank1/table/12134/
- SSB 12143: https://www.ssb.no/en/statbank1/table/12143/
- SSB data corrections: https://www.ssb.no/kostra/rettinger-i-tidligere-ars-publiserte-data
- PxWeb v2 API guidance: https://www.ssb.no/en/api/pxwebapiv2

## Research log entries after running

- SOURCE-12364: metadata retrieval PASS/FAIL and original file hash.
- SOURCE-12143: metadata retrieval PASS/FAIL and original file hash.
- DEF-P2: whether a precise official `disposisjonsfond` account was identified (do not mark PASS from a keyword alone).
- HIST-ACCOUNT-5900: review of pre-2018 historical sign convention.
- GATE-1A7: scientific approval remains blocked until reconciliations are finished.

Do not commit the files under `data/raw/` or generated `reports/`; commit only the reviewed guide and script. GitHub does not need the source observations yet.
