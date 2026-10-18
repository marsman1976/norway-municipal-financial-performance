# Phase 1A.2 — All-null pilot finding and remediation gate

**Observed from user terminal output (2026-10-11):**

- SSB table: 12134 (Financial key figures).
- Dry run: 30 data requests planned, maximum 2,700 cells per request; no observations obtained.
- Pilot: `year_2016_part_0001` saved; 18 cells; `null-at-least=18`.
- Stored raw response is **not** proof of usable 2016 observations.
- User has not yet provided the raw JSON or the selected region-code and status details.

## Findings

- **F1A2-001 (verified):** Request planning ran; 30 requests for ten-year table 12134, max planned 2,700 cells.
- **F1A2-002 (verified):** Pilot response was saved and passed structural dimension checks.
- **F1A2-003 (verified):** All 18 returned pilot observations are null; no numeric pilot values established.
- **BUG-002 (verified from collector source):** `make_plan(..., pilot=True)` chooses `regions[:2]`, without checking if those region codes have published observations in 2016. This design can produce an all-null pilot.
- **HYP-002 (unverified):** Historical municipality code validity or coverage may explain nulls; alternative explanations include unavailable indicator-year pairs and source-specific missing statuses.

## Required diagnosis

1. Inspect `data/raw/ssb/pilot/12134/year_2016_part_0001.json` and sibling `metadata.json` without changing them.
2. Print all selected region codes, labels, numeric/non-numeric cells, and SSB observation-status counts.
3. Cross-check identified municipalities against year-specific KLASS identities and 2016 coverage; do not assume new municipality codes apply backward.
4. Only then update the pilot selection to include verified relevant municipality-region-year combinations; preserve the first raw response as evidence.
5. Re-run a corrected pilot into a distinct path; compare its cell coverage and status distribution.
6. Keep scientific readiness **BLOCKED** until full coverage/definition/continuity checks pass.

## Implementation

Diagnostic file: `scripts/phase1a_03_diagnose_pilot.py`

```bash
python scripts/phase1a_03_diagnose_pilot.py --self-test
python scripts/phase1a_03_diagnose_pilot.py --table 12134 --year 2016
```

The diagnosis writes `reports/phase1a/pilot_12134_2016_diagnostic.txt`, but never modifies original source bytes or fetches new data.

## Source interpretation

SSB's official PxWeb v2 API guidance states JSON-stat2 uses `null` with an accompanying `status` code for certain unavailable/confidential observations. A null is not a measured financial zero. Citation: https://www.ssb.no/en/api/pxwebapiv2
