# Phase 06 continuation — Repair 01: official-source probe

**Date:** 2026-10-12

## Evidentiary findings

| ID | Finding | Basis | Status |
|---|---|---|---|
| R01-01 | The repository's original Phase 01 probe checked `changes` in the KLASS changes JSON | GitHub `scripts/phase1a_01_probe_official_sources.py` on commit `5c6ca1966b26` | VERIFIED CODE DEFECT |
| R01-02 | The corrected schema key is `codeChanges` | Earlier 6/6 live probe and KLASS integration audit | VERIFIED PRIOR PILOT; RECHECK LIVE |
| R01-03 | A replacement probe now validates `codeChanges` and rejects the old `changes`-only structure | Offline self-test + regression tests | PASSED OFFLINE |
| R01-04 | Probe outputs are timestamped and written using exclusive create | Replacement script implementation and offline self-test | PASSED OFFLINE |
| R01-05 | Six endpoint responses on the updated GitHub replacement | Not run against SSB/KLASS by the assistant | LIVE RUN PENDING |
| R01-06 | All national 2016–2025 financial accounts and ratios | Not within this probe's scope | BLOCKED |

## Original technical issue and scientific implication

The original public repository probe checks `doc.get("changes")`, while the official KLASS endpoint returns `codeChanges`. This can incorrectly flag a healthy classification endpoint as a failed source. It does NOT justify replacing historical municipality IDs with modern codes.

The replacement uses the official response key and rejects malformed or missing event records. It preserves exact response bytes in `reports/phase1a/api_probe/<timestamp>/` and creates a timestamped manifest containing SHA-256 fingerprints. It does not change `data/raw/` and does not perform financial analysis.

## Required next actions

1. Run offline tests, and perform a live six-endpoint probe on the user's computer.
2. Inspect the manifest and confirm expected 6/6 responses.
3. Commit the replacement script, offline tests and this record only after reviewing outputs.
4. Keep Phase 02 full bulk collector blocked until annual KLASS code intersection and geographic continuity tests have passed.

**Scientific approval: BLOCKED. No national raw-data or accounting validation is granted by this repair.**
