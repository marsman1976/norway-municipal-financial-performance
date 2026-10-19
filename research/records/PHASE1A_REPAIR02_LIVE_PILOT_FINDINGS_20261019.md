# Phase 1A — Repair 02: Verified Live Pilot Findings

Date: 2026-10-19
Project: Norwegian Municipal Financial Performance
Research period: 2016–2025
Source: SSB Table 12134 and historical KLASS municipality codes
Scientific status: BLOCKED for full national analysis

## 1. Research objective

Verify that the repaired collector:
- Selects historically valid municipality codes.
- Retrieves numerical observations correctly.
- Preserves original source data.
- Produces verifiable source hashes.
- Prevents premature scientific analysis.

## 2. Findings table

| ID | Finding | Evidence | Status |
|---|---|---|---|
| R02-01 | Historical planning identified 428 eligible municipality codes for 2016 | Live planning output | PASS |
| R02-02 | 2016 planning required one request batch | Live planning output | PASS |
| R02-03 | Historical codes 0101 and 0104 were accepted | Live numerical pilot | PASS |
| R02-04 | Numerical observations: 18/18 | Live numerical pilot | PASS |
| R02-05 | Missing observations: 0 | Live numerical pilot | PASS |
| R02-06 | Original response saved successfully | Collector output: SAVED | PASS |
| R02-07 | Source SHA-256 matches recorded report hash | Independent local hash-check command | PASS |
| R02-08 | Accounting definitions and historical comparability | Not yet fully validated | BLOCKED |

## 3. Historical code selection

The collector uses the intersection of two code sets:

C(year) = C(SSB) intersection C(KLASS, year)

For 2016:

Number of selected historical codes = 428.

This establishes historical-code eligibility under the implemented selection rule, not complete financial-data coverage.

## 4. Numerical pilot

Table: 12134
Year: 2016
Municipality codes: 0101 and 0104
Expected cells: 18
Numerical cells: 18
Missing cells: 0

Original file:
data/raw/ssb/year_aware_v2/12134/year_2016_codes_0101-0104.json

Original audit report:
reports/phase1a/year_aware_collection/phase02_year_aware_20261018T233740345146Z.json

## 5. Source integrity verification

Actual terminal evidence:

Source hash: PASS
Cells: 18
Numeric: 18
Missing: 0
PILOT EVIDENCE CHECK: PASS

The local verification recomputed SHA-256 from the saved raw JSON
and compared it against the hash stored in the collector's report.

This confirms agreement between the saved source and report.
It does not independently validate financial-account definitions.

## 6. Scientific interpretation

The repaired collector passed the controlled 2016 technical pilot.

Results support correct historical-code selection and retrieval
for the tested municipalities, indicators and year.

They do not establish:
- National financial-data completeness.
- Comparability across 2016–2025.
- Correct classification of disposisjonsfond.
- Municipality financial performance rankings.
- Statistical or causal relationships.

## 7. Decision

Repair 02 limited technical validation: PASS.

Full national data collection and modeling: BLOCKED.

Next: audit historical codes for 2020 and 2025 and
continue accounting-definition reconciliation.
