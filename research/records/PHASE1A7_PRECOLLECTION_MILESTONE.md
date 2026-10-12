# Phase 1A.7 — Precollection milestone: ledger definitions and historical bridges

**As of 2026-10-12.** No new SSB account metadata or numeric observations have been collected by the user's computer in this phase yet. The next program is tested **offline** and tested against the user's preserved table `12134` metadata.

## Evidence table

| ID | Claim | Supporting evidence | Status | Scientific implication |
|---|---|---|---|---|
| F1A7-001 | The year-aware Halden/Moss 2016 pilot contained 18 non-null financial observations and no missing statuses. | Preserved table-12134 pilot response, SHA-256 `181abcb10698d0b03886220c68564c0e55e9e3ba5e421a6b6e53cf1d3a9b5f02`, prior Phase 1A.6 findings | VERIFIED LOCAL PILOT ONLY | Numeric availability, **not** definition or decade coverage approval. |
| F1A7-002 | SSB table `12364` lists financial basic data by accounting concept for 2015-2025. | https://www.ssb.no/en/statbank1/table/12364/ | OFFICIAL SOURCE CATALOG VERIFIED | Candidate source for official account-level concepts, not yet an approved numerator. |
| F1A7-003 | SSB corrected the sign of operating deficit (account/chapter 5900) for 2015-2017 in earlier reporting and adjusted its treatment in free equity/accumulated result in 2018-2019. | https://www.ssb.no/kostra/rettinger-i-tidligere-ars-publiserte-data | OFFICIAL CORRECTION LOG VERIFIED; EFFECT ON OUR SOURCE SERIES UNTESTED | Freeze source vintage and reconstruction rules before mixing years. |
| F1A7-004 | Free equity operational account differs from standalone `disposisjonsfond`. | https://www.ssb.no/kompis/statbank/?id=28d0afd2-5d6b-435e-a871-0e993729b6f5&lang=en&val=KOSKG210000&ver=94059 | OFFICIAL DEFINITION CONFIRMED | P2 reserve case-selection indicator cannot be substituted using adjusted free equity. |
| F1A7-005 | Certain detailed accounts cover 2020 onward, not all 2016-2025. | SSB table catalog in prior Phase1A.6 learning guide | DOCUMENTED; SPECIFIC TABLE METADATA PENDING | Build explicit per-variable coverage matrix rather than interpolation. |
| F1A7-006 | Phase1A7 source discovery script validated against the original preserved table-12134 metadata with nine entries; no online account metadata downloaded from this execution environment. | Local offline test output of `phase1a_06_discover_financial_accounts.py` | TECHNICAL TEST PASS, LIVE PENDING | Authorize only metadata collection. |

## Update the four living records

- `01_project_methodology.md`: Add the requirement to reconcile P2 `disposisjonsfond` independently; cross-table indicators require common accounting scope and vintage.
- `02_problem_and_fix_log.md`: Add **E10**: original source 5900 historical sign/adjusted-free-equity revisions; fix: table/period-specific correction log review, no transformations until ledger mapping reviewed.
- `03_findings_evidence.md`: Copy evidence table above, keeping source catalogue findings separate from numerical financial results.
- `04_status_next_steps.md`: Mark Phase1A6 2016 pilot audited numerically; **Phase1A7 ledger concept identification NEXT**; full panel and case selection blocked.

## Next execution gate

1. Run Phase1A7 `--self-test`.
2. Run **only** `--tables 12364 12143` initially.
3. Check official source labels and dimensional coverage from the resulting two metadata files.
4. Upload `phase1a7_account_concept_candidates_*.csv` and `phase1a7_coverage_and_scope_*.csv`, or the source metadata JSONs if the candidate results are insufficient.
5. Verify exact P2 `disposisjonsfond` account and numerator/denominator; record any 2015-2019 revised source-vintage issues.
6. Plan a small historically valid, source-matched 2016/2025 account pilot before bulk collection.

**Scientific readiness: BLOCKED — no municipality ranking, selection or modeling.**
