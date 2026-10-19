# Phase 1A — Repair 02: 2016 Historical Planning Findings

**Date:** 2026-10-19
**Research period:** 2016–2025
**Source:** SSB table 12134 and official KLASS municipality classification
**Stage:** Live planning verification
**Scientific approval:** BLOCKED

## 1. Findings table

| ID | Finding | Evidence | Status |
|---|---|---|---|
| R02-P01 | 428 historical municipality codes selected for 2016 | Live planning output | PASS |
| R02-P02 | One request batch planned for 2016 | Live planning output | PASS |
| R02-P03 | Planning mode did not download financial observations | Program design and execution mode | CONFIRMED |
| R02-P04 | Previous corrected 2016 pilot returned 18/18 numeric values | Earlier pilot audit | PREVIOUSLY VERIFIED |
| R02-P05 | Numerical pilot using the repaired collector | Not yet executed | PENDING |
| R02-P06 | Accounting definitions and 2016–2025 comparability | Unresolved scientific validation gates | BLOCKED |

## 2. Actual terminal evidence

12134/2016: 428 historical codes; 1 planned part(s); KLASS/SSB intersection PASS

WROTE: reports/phase1a/year_aware_collection/phase02_year_aware_20261018T231738669329Z.json

SCIENTIFIC APPROVAL: BLOCKED — no full collection or case selection

## 3. Mathematical explanation

The program identifies historically eligible municipality codes using:

C_2016 = C_SSB intersection C_KLASS_2016

The observed intersection contains 428 codes.

This verifies the selection rule for the 2016 planning run.
It does not prove that every code has complete financial observations.

## 4. Problems and corrections

| Problem | Correction | Remaining limitation |
|---|---|---|
| Original collector did not validate historical municipality codes by year | Year-specific SSB/KLASS intersection introduced | Historical merger and split continuity is not yet approved |
| Modern codes could be requested for earlier years | Repaired collector validates codes against annual KLASS snapshots | Live numerical pilot still pending |
| Metadata could be confused with validated financial observations | Planning and observation collection are separate modes | Financial accounting definitions remain unverified |

## 5. Scientific interpretation

The repaired collector passed its first live year-aware planning check.

No financial observations were downloaded during this run.

No conclusion about strong or weak municipalities can be drawn.

## 6. Next steps

1. Run the repaired collector's offline tests.
2. Run a controlled numerical pilot for 2016 municipality codes 0101 and 0104.
3. Verify observation counts, missing statuses, identities and source hashes.
4. Update the findings and problem/fix records using the actual pilot evidence.
5. Review and commit the verified changes to GitHub.

**Decision:** Continue with the controlled numerical pilot only.
**National data collection and modeling:** BLOCKED.
