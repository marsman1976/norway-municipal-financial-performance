# DATA-FIRST PACKAGE — NOT A VERIFIED RAW DATASET

**Study:** Ten-year financial performance of comparable Norwegian municipalities (2016–2025).  
**Prepared:** 2026-10-10 (pre-acquisition).  
**Collection status: BLOCKED — official raw KOSTRA/KLASS numeric exports have NOT been downloaded.**

The user's requirement is to collect ALL needed data **before** coding the actual research. This ZIP is an honest source-and-integrity readiness pack, **not** the promised complete data package. The working container has no usable external DNS/network connection; direct requests to the official SSB servers failed. Source documentation and table-level year coverage were independently checked from public official SSB pages.

## What is inside
- `01_sources/source_catalog.csv`: inventory of official SSB/KLASS sources, periods, URLs, intended uses, acquisition status.
- `02_data_dictionary/data_dictionary.csv`: normalized conceptual variables and data needs; **no invented SSB content codes**.
- `03_ratio_definitions/ratio_catalog.csv`: traditional and municipal financial ratio formulas and applicability restrictions.
- `04_methods/phase_data_map.csv`: dataset use at every future research phase; plus detailed scientific notes.
- `05_integrity/`: mandatory pass/fail gates and years-by-source coverage matrix.
- `06_research_records/`: the four living records, dated and with no fabricated numerical findings.
- `07_templates/`: EMPTY evidence, receipts and lineage templates; no fictitious observations.
- `08_prior_manuscript/`: source manuscript and user-provided historic source manifest (documentation, not raw numeric data).
- `09_raw_data_NOT_YET_COLLECTED/`: clear marker for missing raw extracts.
- `SOURCE_REGISTER.xlsx`: browsable official source inventory, variable dictionary, ratios, quality tests, coverage and phase map.

## Nothing is yet fit for municipality selection
Critical absent data include official KOSTRA raw values, KLASS change events, historical KOSTRA group crosswalk, confirmed unrestricted reserves (disposisjonsfond) numerator, and 2016–2019 detailed-account historical bridge for ratio families requiring balances.

## How to complete acquisition without implementing models
1. Download official table extracts as original JSON-stat2/CSV from `source_catalog.csv` (record API queries, save API metadata and footnotes). Do **not** rename content codes without official crosswalks.
2. Get both 2016 and 2017 historically valid KLASS 231 KOSTRA group memberships (correspondence/variant), KLASS 131 municipality changes for every applicable year.
3. Download 12134/12364/12143/12333 and population for **every historical municipality** 2016–2025, then other financial, service and contextual sources in the source catalogue.
4. Preserve originals as immutable files, store a SHA-256 hash and retrieval date for each, and populate the empty receipt and metric mapping templates.
5. Complete every `BLOCKING` quality gate in `05_integrity/quality_gates.csv`, and secure manual footnote/definition sign-off.
6. Only after the audit passes produce a validated raw-data ZIP with `COLLECTION_STATUS: COMPLETE` and numeric municipal observations.

**Do not use this metadata pack as statistical data**. Run no classifications, financial rankings or models from it.
