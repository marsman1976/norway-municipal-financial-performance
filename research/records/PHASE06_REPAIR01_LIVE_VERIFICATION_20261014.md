# Phase 06 — Repair 01: live SSB/KLASS source-probe verification

**Evidence date:** 2026-10-14  
**Source:** User-provided terminal output from `scripts/phase1a_01_probe_official_sources.py`  
**Scope:** Connectivity and response-schema validation only; no municipal financial observations or model estimates.  
**Associated GitHub commit:** `5448db220d8d` (`Complete Phase 06 review and repair KLASS probe`; verified present on `main`).

## 1. Results reproduced from the terminal

| Probe | HTTP status | Outcome |
|---|---:|---|
| `ssb_12134_info` | 200 | PASS |
| `ssb_12134_metadata` | 200 | PASS |
| `ssb_12364_metadata` | 200 | PASS |
| `ssb_07459_metadata` | 200 | PASS |
| `klass_2020_codes` | 200 | PASS |
| `klass_changes` | 200 | PASS |

**Live probe:** `6/6 PASS`.  
**Earlier automated unit tests:** `7/7 PASS` in `0.524s`, as reported by the user.  
**Evidence manifest path (local, not independently inspected):** `reports/phase1a/api_probe/20261014T035833341707Z/endpoint_probe_manifest.csv`.

## 2. Finding table

| Finding ID | Claim | Evidence | Decision |
|---|---|---|---|
| F06-R01-01 | All six requested official source endpoints returned HTTP 200 and passed the program's response checks | Terminal output of live run | CONFIRMED FOR THIS RUN |
| F06-R01-02 | The KLASS change endpoint passed the corrected `codeChanges` validation | Terminal output and corrected script on GitHub | IMPLEMENTATION FIX VERIFIED IN LIVE PROBE |
| F06-R01-03 | Seven offline unit tests passed without failure | User-provided test-suite summary | OFFLINE TEST PASS |
| F06-R01-04 | New probe outputs are written into a timestamped run directory | Program code; manifest path printed in terminal | IMPLEMENTED; RAW BYTES/HASHES NOT INSPECTED HERE |
| F06-R01-05 | Source/API correctness does not certify financial definitions or a ten-year data panel | The probe intentionally fetches metadata only | SCIENTIFIC DATA GATE BLOCKED |
| F06-R01-06 | The full-data collector still requires year-specific KLASS region validation | Earlier audit of `scripts/phase1a_02_collect_official_raw.py` | OPEN / DO NOT BULK RUN |

## 3. Error and correction log

| Error ID | Problem | Correction | Test evidence | Status |
|---|---|---|---|---|
| P06-09 | Old KLASS response parser expected `changes` rather than `codeChanges` | Corrected parser plus offline regression tests | Offline 7/7; live KLASS changes PASS, HTTP 200 | CLOSED FOR PROBE |
| P06-08 | Full SSB collector selects municipality codes without year-specific KLASS intersection | Replace collector planner and add time-specific municipality-code tests | Not yet implemented | OPEN / BLOCKS FULL COLLECTION |
| P06-EVIDENCE | Manifest and original response JSON have not been inspected in this chat | Preserve local response bytes, timestamp and SHA-256; inspect as necessary | Terminal path only | NOT INDEPENDENTLY VERIFIED |

## 4. What the tests prove and do not prove

**Established:** the current probe can contact the six specified endpoints and validate their expected response structures during this particular execution. The corrected KLASS field handling works with the current live response.

**Not established:** accuracy or completeness of municipal financial observations, correct accounting interpretation, historical comparability over 2016–2025, a valid `disposisjonsfond` numerator, municipality ranking, regression results, or causal relationships.

**Scientific approval:** `BLOCKED_PENDING_ACCOUNTING_RECONCILIATION_AND_HISTORICAL_COLLECTION_AUDIT`.

## 5. Next step — Repair 02

Before any complete historical-data download, repair `scripts/phase1a_02_collect_official_raw.py` to intersect year-specific official KLASS municipality codes with each SSB table's region dimension. Preserve immutable originals, identify mergers and splits separately, and add regression tests for 2016 historic codes versus present-day codes. Review the resulting small pilot before approving larger collections.

## 6. Repository handling

Keep original JSON API responses and generated manifests in local `reports/` and `data/raw/` according to the repository `.gitignore`. This Markdown record may be committed under `research/records/` after the reviewer checks that it matches the actual terminal output. Do not rewrite the earlier source-package preflight records to claim that the national panel was validated.
