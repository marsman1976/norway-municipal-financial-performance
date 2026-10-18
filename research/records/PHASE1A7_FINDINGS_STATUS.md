# Phase 1A.7 — Research findings and evidence checkpoint

**Project:** Norwegian municipal financial performance, 2016–2025  
**Stage:** Before live Phase 1A.7 account metadata discovery  
**Evidence basis:** Terminal outputs supplied by the researcher; immutable pilot archive SHA-256; previously reviewed official SSB/KLASS metadata; repository inspection.  
**Scientific gate:** **BLOCKED — accounting definitions and ten-year comparability not approved.**

## A. Verified findings from completed phases

| ID | Question or finding | Evidence/observation | What this establishes | What it does not establish | Status |
|---|---|---|---|---|---|
| F1A-001 | Are official endpoints reachable? | Six of six SSB/KLASS metadata checks PASS, HTTP 200 | The six probed endpoints are reachable and return expected structures | Data quality, financial validity or full source coverage | VERIFIED TECHNICAL |
| F1A-002 | Why did the first 2016 pilot fail? | Table 12134, codes 3101/3103, 18 cells, 18 null, SSB status `.` | The first selected code–year combination returned no usable observations | That the financial values were zero | VERIFIED SOURCE RESULT |
| F1A-003 | Does year-specific code selection recover observations? | Table 12134, 2016 codes 0101 Halden and 0104 Moss: 18/18 numeric, 0 null | Historical code selection fixed this particular pilot's availability problem | National availability for every year or other sources | VERIFIED SOURCE RESULT |
| F1A-004 | Was the corrected pilot preserved? | Corrected raw JSON SHA-256 `181abcb10698d0b03886220c68564c0e55e9e3ba5e421a6b6e53cf1d3a9b5f02` | Exact byte-level identity for the preserved source version | Accuracy of SSB's underlying reported accounts | VERIFIED PROVENANCE |
| F1A-005 | Are all nine source indicator units available? | Automated pilot audit: 9/9 metadata units, all 18 values numeric, IDs matched | The nine categories have units and matching observed codes | Numerator/denominator/accounting scope approval | VERIFIED AUTOMATED |
| F1A-006 | Can adjusted free equity substitute for unrestricted reserves? | Source review distinguishes adjusted free equity from the actual disposisjonsfond stock | P2 requires a separately verified reserve measure | A confirmed source code/formula for P2 | OPEN SCIENTIFIC |
| F1A-007 | Is the 2016–2025 panel ready? | Only a two-municipality, one-year pilot has been numerically validated | No legitimate strong/weak municipality selection yet | Ten-year national comparability | BLOCKED |

## B. Phase 1A.7: planned checks — DO NOT mark PASS before live run

| ID | Test | Required evidence | Current result | Status |
|---|---|---|---|---|
| F1A7-001 | `phase1a_06_discover_financial_accounts.py --self-test` | Printed offline PASS | Offline self-test confirmed in preparation environment | PASS OFFLINE ONLY |
| F1A7-002 | Table 12364 metadata download or unchanged cache | Original metadata bytes; SHA-256; manifest SUCCESS | Awaiting researcher run | PENDING LIVE |
| F1A7-003 | Table 12143 metadata download or unchanged cache | Original metadata bytes; SHA-256; manifest SUCCESS | Awaiting researcher run | PENDING LIVE |
| F1A7-004 | Exact disposisjonsfond candidate | Verified official code + definition + unit + accounting scope | No approved candidate | OPEN SCIENTIFIC |
| F1A7-005 | Historical coverage | Official year labels plus real non-null year–municipality observations | Year labels not yet examined in researcher live run | PENDING LIVE |
| F1A7-006 | Historical comparability | Source corrections, reporting scope, 2016–2019 / 2020–2025 bridge | Unresolved | BLOCKED |

## C. Open problems and corrective actions

| Problem | Cause/risk | Action | Exit criterion |
|---|---|---|---|
| HIST-001 | Historical and current municipality codes differ | Require KLASS codes valid in the observation year | All sampled codes valid in corresponding year |
| META-001 | Metadata title may suggest a formula not established by ledger | Separate candidate discovery from signed definition | Official account code, numerator, denominator and scope documented |
| META-002 | Source catalog years are not proof of non-null values | Extract limited observation samples only after metadata and geography audit | Missingness matrix for each source/required year |
| ACC-001 | Adjusted free equity is not identical to disposisjonsfond | Reconcile unrestricted reserve stock against original accounts | P2 formula and series documented |
| ACC-002 | Municipal / consolidated and historical reporting changes | Freeze reporting scope and correction log per variable | Comparable measurement or transparent period restriction |

## D. Decision and next steps

1. Run metadata discovery locally using the exact commands in the guide.
2. Inspect `phase1a7_account_concept_candidates_*.csv`, `phase1a7_coverage_and_scope_*.csv`, and `phase1a7_source_manifest_*.csv`.
3. Preserve original JSON files locally under `data/raw/metadata/phase1a7/`; do not commit their contents to public GitHub by default.
4. Submit candidate/coverage CSVs for evidence review. Update this record with actual counts and official code labels **only after checking the files**.
5. Do **not** select municipalities, infer trends, reconstruct financial ratios, or begin full national extraction while scientific gates are open.

## E. Mathematical interpretation of the pilot only

Availability rate is `number of non-null cells / number of requested cells`.
Original pilot: `0/18 = 0%`. Corrected pilot: `18/18 = 100%`. This is an **availability comparison** for the tested source-year-code cells, not a performance effect size or statistical hypothesis test.
