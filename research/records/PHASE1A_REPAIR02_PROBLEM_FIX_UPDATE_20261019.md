# Phase 1A — Repair 02: Problem and Fix Log

Date: 2026-10-19
Project: Norwegian Municipal Financial Performance

## 1. Problems, corrections and evidence

| ID | Problem | Correction | Evidence | Status |
|---|---|---|---|---|
| P02-01 | The original collector could use modern codes for historical years | Added year-specific SSB/KLASS intersection | 2016 planning: 428 codes | FIXED FOR TESTED YEAR |
| P02-02 | Original 2016 pilot produced all-null observations | Used valid historical codes 0101 and 0104 | Repaired pilot: 18/18 numeric | FIXED FOR PILOT |
| P02-03 | Risk of overwriting original source files | Added immutable-by-default source storage | Collector reported SAVED | IMPLEMENTED |
| P02-04 | Source integrity needed independent confirmation | Recomputed SHA-256 and compared with report | Source hash: PASS | VERIFIED LOCALLY |
| P02-05 | Historical accounting and municipality continuity are unresolved | Continue scientific release gates | Not yet tested comprehensively | OPEN |

## 2. Confirmed test results

- Official source probe: 6/6 PASS.
- 2016 historical planning: PASS.
- Historically eligible 2016 codes: 428.
- Controlled numerical pilot: 18/18.
- Missing numerical observations: 0.
- Source hash comparison: PASS.
- No national ranking or statistical model was executed.

## 3. Remaining scientific limitations

1. Verify accounting definitions for each selected financial indicator.
2. Confirm genuine disposisjonsfond measurements.
3. Establish historical identity continuity across mergers and splits.
4. Verify source coverage across every required year and table.
5. Verify numerator, denominator, units and accounting scope.
6. Document missingness and comparability before panel construction.

## 4. Scientific decision

The collector's limited 2016 technical validation is complete.

The study is not yet approved for full national collection,
municipality ranking, inference or machine-learning modeling.

## 5. Next experiment

Run planning-only checks for SSB table 12134 in 2020 and 2025.

Compare historical eligibility across 2016, 2020 and 2025.
Investigate discontinuities without automatically assuming
that municipalities with similar names or codes are comparable.
