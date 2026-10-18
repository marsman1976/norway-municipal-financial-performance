# Phase 1A — Repair 02: year-aware collector (pre-live review)

**Date:** 2026-10-19. **Scope:** source-integrity engineering only.

## Findings and evidence table

| ID | Finding | Evidence | Status |
|---|---|---|---|
| R02-01 | The original full collector reused codes from a non-year-specific table region dimension. | GitHub `scripts/phase1a_02_collect_official_raw.py` inspected before repair. | CONFIRMED SOURCE-CODE DEFECT |
| R02-02 | Earlier 2016 initial pilot was all-null while the corrected historical-code pilot produced 18/18 numeric observations. | Previously retained user pilot and financial-audit terminal results. | CONFIRMED LIMITED PILOT |
| R02-03 | The new planner intersects table region codes with official KLASS municipality codes separately for every year. | Replacement implementation, offline tests. | IMPLEMENTED; LIVE TEST PENDING |
| R02-04 | A modern 2025 municipality code cannot be silently substituted in a 2016 request. | Offline rejection test. | OFFLINE PASS |
| R02-05 | Original metadata, KLASS responses and limited pilot observations use immutable files, with source hashes in dated reports. | Replacement implementation and offline tests. | IMPLEMENTED; LIVE VERIFICATION PENDING |
| R02-06 | Complete 2016–2025 extraction remains unavailable through the repaired script pending scientific release approval. | CLI supports only planning and a maximum two-code single-year table 12134 pilot. | FULL COLLECTION BLOCKED |
| R02-07 | Accounting definitions, year-to-year boundary continuity, and actual disposisjonsfond reconciliation are not resolved by this repair. | Phase 1A.6 release gates G04–G09. | SCIENTIFIC GATE BLOCKED |

## Problem/fix record

| Problem | Why it mattered | Fix | Remaining limitation |
|---|---|---|---|
| Old region selection ignored annual KLASS validity | Could request modern municipality codes for historical years and return all-null observations | Require annual intersection and reject explicit invalid codes | Historical mergers/splits still require structural continuity audit |
| Planned full request before accounting sign-off | Risked large unreviewed data collections | Restrict `--mode plan` to source inspection and `--mode pilot` to one year, two municipalities and table 12134 | Full collector must be separately authorized and assessed |
| Raw overwrite risks | Could alter reproducibility evidence | Exclusive file creation and changed-byte rejection | Public source versions may evolve; future revisions need versioned archive design |

## Next scientific step

Run the offline tests, then the live **planning mode** for 2016. Inspect the selected 2016 codes and original KLASS/source hashes. Only if it is clean, run the controlled 2016 two-code pilot. Review the observations and identities before advancing. Do not rank municipalities or fit models.
