# Phase 06: reviewed live metadata-discovery evidence

**Review date:** 2026-10-12  
**Input:** `phase06_results_for_review.zip` (12 CSVs, three complete four-file runs).  
**Review method:** CSV parsing, run-consistency checks, code-level inspection, and independent official SSB KOSTRA-document cross-reference.  
**Data gate:** **BLOCKED** — no municipality-year financial amounts in the uploaded ZIP; no account-to-ratio numerical reconciliation.

## Evidence findings matrix

| ID | Finding | Evidence | Interpretation | Status |
|---|---|---|---|---|
| F06-01 | All three runs have two metadata tables, `12364` and `12143` | Source manifests at 16:56, 17:39 and 17:52 UTC | The metadata-discovery procedure produced three complete CSV report batches | PASS_CSV |
| F06-02 | First run `SAVED` both tables; next two were `CACHED_UNCHANGED_NOT_REFETCHED` | Source manifests | Cached repeats are not three independent SSB retrievals | VERIFIED |
| F06-03 | `12364` metadata: 81 concept/measure entries, 26 keyword hits | Candidate CSV | Candidate inventory, not 81 distinct financial outcomes | VERIFIED |
| F06-04 | `12143` metadata: 25 concept/measure entries, 13 keyword hits | Candidate CSV | Includes the `ContentsCode` measure dimension | VERIFIED |
| F06-05 | Total entries 106; keyword hits 39, from one latest run | Candidate CSV | Counts must not be multiplied by three repeated runs | VERIFIED |
| F06-06 | All ten 2016–2025 years appear in both table metadata year dimensions | Coverage CSV | Metadata coverage only; not full numeric coverage | PASS_METADATA_ONLY |
| F06-07 | Reported metadata hashes and byte counts stay consistent across three runs | Manifest + coverage CSV | CSV-level agreement; original metadata JSON bytes absent from uploaded ZIP | PASS_CSV_ONLY |
| F06-08 | `12364` code `56` and `12143` code `56` are labeled `General funds (M)` | Candidate CSV (unflagged rows) | Strong candidate for actual *disposisjonsfond* source | VERIFIED_LABEL |
| F06-09 | Official SSB KOSTRA reporting guides identify code `56` as `Disposisjonsfond` in 2015, 2018 and 2024 | Official SSB reporting guides linked below | Historical account-code interpretation supported, numerical use still pending | SUPPORTED_DOCUMENTATION |
| F06-10 | Code `KG21` is `Free equity operational account` | Candidate CSV | Not a substitute for code `56` as unrestricted reserve stock | VERIFIED_DIFFERENT_LABEL |
| F06-11 | `12364` code `AGD13` gross operating revenues; `AGD23` net operating result; `KG31` net loan debt | Candidate CSV | Possible components for three outcome concepts | CANDIDATE_ONLY |
| F06-12 | Source metadata footnotes flag a 2019–2020 KOSTRA-group classification break | Coverage CSV | Frozen historic group mapping required | REQUIRES_BRIDGE |
| F06-13 | Debt instrument labels contain `(-2023)` and `(2024-)` | Candidate CSV | A second account-classification break needs formal treatment | REQUIRES_BRIDGE |
| F06-14 | `12143` title marks `(M)` but English general note refers to county authorities | Coverage CSV | Ambiguous table description; verify the reporting scope | SOURCE_NOTE_INCONSISTENCY |
| F06-15 | One `12143` `ContentsCode` percentage measure was flagged by revenue keyword matching | Candidate CSV | Keyword hits can be false positives; human review needed | SEARCH_METHOD_LIMITATION |
| F06-16 | All 106 rows have `source_definition_verified=NO`; all 10 gates remain blocked | Candidate and gates CSVs | Correct: discovery does not authorize statistical analysis | BLOCKED |
| F06-17 | Zero municipality-year financial amounts in this evidence ZIP | ZIP contents | Ratio reconstruction and financial comparisons cannot be assessed | NOT_TESTED |

## Priority account/indicator mapping (not yet signed off)

| Research construct | SSB source | Code | Official English label | Proposed next test |
|---|---|---|---|---|
| Unrestricted reserve stock (P2 numerator) | 12364 | `56` | General funds (M) | Confirm published balance, sign, entity and year coverage |
| Published unrestricted reserve share (cross-check) | 12143 | `56` + percentage `ContentsCode` | General funds (M) | Compare with reconstructed ratio; verify unit and rounding |
| Potential P2 denominator | 12364 | `AGD13` | Gross operating revenues | Reconcile denominator with 12143 |
| Operating result (P1) | 12364 | `AGD23` | Net operating result | Compare against previously audited 12134 ratio |
| Net loan debt (P3) | 12364 | `KG31` | Net loan debt | Reproduce published debt ratio in controlled pilot |
| Adjusted/free equity | 12364 | `KG21` | Free equity operational account | Keep separate from reserve stock |
| Historical deficit adjustment | 12364 | `5900` | Deficit of the year in operational accounts (M) | Review historical sign and correction log |

**Proposed formula, not yet validated:**

`Disposisjonsfond ratio (%) = 100 × (account 56 balance) / (AGD13 gross operating revenues)`

The signs, period-end stock/annual-flow alignment, reporting entity and treatment of the percentage output in 12143 must all be audited. If original accounting uses credit signs, normalize using documented rules, never by arbitrary absolute values.

## Official documentation used for the account-56 interpretation

- SSB KOSTRA reporting guide 2015: https://www.ssb.no/offentlig-sektor/artikler-og-publikasjoner/_attachment/282522?_ts=15b42e83570
- SSB KOSTRA reporting guide 2018: https://www.ssb.no/offentlig-sektor/artikler-og-publikasjoner/_attachment/366611?_ts=166a54a9b30
- SSB KOSTRA reporting guide 2024: https://www.ssb.no/offentlig-sektor/kostra/artikler/kostra-rapportering-2024/
- SSB KOSTRA balance classification: https://dataportal.ssb.no/classifications/270/versions/2798/codes

**Next:** obtain original metadata JSON files to independently recompute hashes, then design a small year-aware account-level numerical pilot for codes `56`, `AGD13`, `AGD23`, `KG31` and an appropriate published percentage from 12143. Repair known historical-identity issue in the bulk collector before any full download.
