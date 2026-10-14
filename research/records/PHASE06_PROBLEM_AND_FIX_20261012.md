# Phase 06 — Problems, causes and corrective actions

| ID | Problem / risk | Evidence | Corrective action | Status |
|---|---|---|---|---|
| P06-01 | Keyword inventory missed reserve account `56` | `56 General funds (M)` appears with `candidate_for_review=NO` in both tables | Add a reviewed explicit account-code mapping with official SSB documentary references; retain search hints as non-authoritative | IDENTIFIED; SCRIPT_06_NOT_YET_CHANGED |
| P06-02 | Three successful CSV batches could be mistaken for independent replication | One `SAVED` run plus two `CACHED_UNCHANGED_NOT_REFETCHED` | Label the three as reruns over the same two preserved metadata files | DOCUMENTED |
| P06-03 | Source hashes cannot be independently recomputed from supplied ZIP | ZIP contains reports only, not original metadata JSON | Obtain `12364_metadata.json` and `12143_metadata.json`, compare hashes with source manifest | OPEN |
| P06-04 | Accounting concepts may change meaning through time | Year-tagged debt codes `(-2023)` and `(2024-)` | Create account-to-account historical mapping; verify before comparing debt components | OPEN |
| P06-05 | Historical KOSTRA-group discontinuity | SSB table footnote mentions 2019–2020 | Freeze 2016/2017 group membership from historical version; evaluate 2020 break explicitly | OPEN |
| P06-06 | Table 12143 scope description is inconsistent | Title `(M)` but general English note mentions county authorities | Check Norwegian source title, full table definition and variable-level scope | OPEN |
| P06-07 | A percentage `ContentsCode` was flagged as a revenue concept | Candidate `KOSbelopbrinv0000` in 12143 | Exclude measure-type codes from account-based keyword screening | OPEN |
| P06-08 | Bulk collector still selects municipality codes without annual KLASS intersection | GitHub `scripts/phase1a_02_collect_official_raw.py` | Correct to year-aware KLASS code lists and test 2016 Halden/Moss example | OPEN / DO_NOT_BULK_DOWNLOAD |
| P06-09 | Old KLASS probe parser checks `changes` field | GitHub `scripts/phase1a_01_probe_official_sources.py` | Update to `codeChanges` and add offline JSON fixture | OPEN |
| P06-10 | Master README and four master logs still describe pre-pilot collection stage | Repository contents checked 2026-10-12 | Update dated current status without changing immutable preflight archival copy | OPEN |

Do not convert any OPEN account-definition or 2016–2025 comparability item to PASS without source-backed evidence.
