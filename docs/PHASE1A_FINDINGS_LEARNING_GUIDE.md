# PHASE 1A — What we did, what we found, and why it matters

**Project:** Determinants of Long-Term Municipal Financial Performance in Norway (2016–2025)  
**Evidence cut-off:** 11 October 2026 (user-supplied terminal results, available project scripts)  
**Status:** Technical and one-year pilot audits passed; financial definitions, historical comparability, and full source collection **not approved**.

> **Evidence rule:** The original municipal numerical files and the generated definition-review CSV are on the user's computer and were not uploaded here. The recorded counts and SHA-256 identifiers come from the user's *terminal output*, not an independent re-reading of the raw financial values. We independently inspected relevant code in the GitHub repository. No complete municipal financial panel or empirical performance finding is claimed.

## Part A — The study we are preparing

**Main question:** Why do some structurally comparable Norwegian municipalities sustain stronger financial performance, and do candidate explanatory factors generalize to other municipalities?

We plan to use **2016–2017** for baseline matching, **2018–2022** to identify strong/weak candidates, and **2023–2025** to assess later outcomes. Selection is not permitted until source definitions, historical codes, reserves, and completeness have been verified.

Three *primary selection outcomes* have been proposed:
- **P1**: net operating result / gross operating revenues;
- **P2**: verified unrestricted **disposisjonsfond** reserve ratio—not automatically SSB's “free equity operational account”;
- **P3**: net loan debt / gross operating revenues.

The project also inventories liquidity, balance-sheet, investment, cash movements, financial risks, and public-service efficiency. Many business ratios (ROE, ROIC, ROCE) need project/enterprise-specific accounts; they are not automatically municipality-wide indicators.

## Part B — Timeline: each research step explained

### Step 0. Set up the research repository

**Why:** A research result must be traceable to the exact input, program version, and procedure that produced it.

**What we did:** Created a VS Code/Python repository with `scripts/`, `data/raw/`, `reports/`, tests, dictionaries, and four living records. GitHub repository: https://github.com/marsman1976/norway-municipal-financial-performance .

**What it proved:** The project structure and basic tools were in place. **It did not prove that any financial data were correct.**

### Step 1. Inventory the source requirements

**Why:** Our earlier experiments ran into missing tables, differently defined variables, and incompatible time coverage. We must know every source before combining data.

**What we did:** Prepared a source inventory, conceptual-variable dictionary, financial ratio list, and integrity checklist. The preflight package catalogued 37 source entries, 54 conceptual fields, 77 candidate financial metrics, and 24 integrity checks. These are *planned inventory counts*, not verified available numeric series.

**What it proved:** We have a plan of required sources and tests. It did not collect the full 2016–2025 dataset.

### Step 2. Probe official data APIs (Phase 1A.1)

**Why:** HTTP access can fail or return a JSON response with an unexpected structure.

**What we did:** Checked six SSB/KLASS endpoints. The first KLASS changes probe returned HTTP 200 but failed a parser expecting `changes`. Inspection of official KLASS integration tests showed the wrapper is `codeChanges`.

**Result:** After the parser fix, **6/6 endpoint probes passed**.

**How to interpret:** Successful *metadata/API communication* is not the same as good financial observations.

**Evidence:** `reports/phase1a/api_probe/endpoint_probe_manifest.csv` on the local machine; probe source in `scripts/phase1a_01_probe_official_sources.py`.

### Step 3. Plan a safe API download (Phase 1A.2)

**Why:** Blind “download everything” requests may exceed provider limits, return unexpected dimensions, or mix incompatible region codes.

**What we did:** SSB table 12134 dry-run: **30 planned requests**, maximum **2,700 planned cells per request**.

**Result:** Planning worked, but **no observations** were downloaded in dry-run mode.

**Interpretation:** Planned cell counts are a sizing check, not a quality check.

### Step 4. Collect the first pilot and find missing values

**Why:** Small, controlled samples expose source errors before they contaminate a decade of data.

**What we did:** Requested 2016 with region codes `3101` Halden and `3103` Moss. Each region had nine selected financial indicators.

**Mathematics of cell counts:**

\[
N_\mathrm{cells}=N_\mathrm{municipalities}\times N_\mathrm{indicators}\times N_\mathrm{years}
=2\times9\times1=18.
\]

**Observed:** 18 cells, **0 numeric**, **18 null**, each missing with SSB status `.`.

**Interpretation:** JSON-stat2 was structurally present, but *nothing in this sample could be used numerically*. A null is **not zero**.

**Evidence:** Pilot hash reported as `6382ed57f44c31f658d91cb6b345c8a6e424eb7b9e428bddebec3fee9f817f24`.

### Step 5. Diagnose rather than conceal the failure (Phase 1A.3)

**Why:** We need the reason for missing data, not an arbitrary substitution.

**What we did:** Inspected original dimensions, code labels, values, missing-status counts, and 2016 identity codes. The diagnosis found that the pilot had chosen *present-day* municipality codes without checking their validity for the historical year.

**Additional issue:** An attempted rerun raised `FileExistsError` because the previous diagnostic report already existed. This is a deliberate no-overwrite safeguard, not another source-data failure.

**Decision:** Retain both the missing-value pilot and its diagnostic report as research evidence.

### Step 6. Repeat the pilot with year-aware municipality codes (Phase 1A.4)

**Why:** Municipalities can be renamed, renumbered, merged, or split. Matching 2016 numbers to 2024 geographic labels may create false missingness or false longitudinal identity.

**Correction:** Verify requested municipality codes against official KLASS for the year and the SSB table metadata.

| Municipality | Original 2016 request | Corrected 2016 request |
|---|---:|---:|
| Halden | `3101` | `0101` |
| Moss | `3103` | `0104` |

**Observed:** **18 non-null out of 18**, with **0 missing**, under the corrected codes.

**Pilot hash reported:** `181abcb10698d0b03886220c68564c0e55e9e3ba5e421a6b6e53cf1d3a9b5f02`.

**Conclusion:** The code correction recovered numeric data in this controlled 2016 pilot. It does **not** establish correctness of all years or municipalities.

### Step 7. Audit observed values and metadata (Phase 1A.5)

**Why:** Even a complete numeric series can be scientifically wrong when units, entities, definitions, or denominators are misunderstood.

**What we did:** Audited the 18 observations against source dimensions and the 2016 KLASS snapshot. The script checks finite numeric values, exact indicator-code set, order, metadata labels, and missing-status structure.

**Terminal result:** **9/9 indicator codes had unit metadata**; automated gate:
`PASS_NUMERIC_AND_IDENTITY__DEFINITION_REVIEW_PENDING`.

**Scientific decision:** `BLOCKED_NOT_YET_AUDITED_FOR_DEFINITIONS_OR_2016_2025_COMPARABILITY`.

This distinction is essential: **passing automated checks is not scientific permission to analyze.**

The program wrote four local files: `_cells.csv`, `_audit.json`, `_definition_review.csv`, and `_notes.json`. Their timestamped prefix is `pilot_12134_2016_20261011T162926430705Z`.

### Step 8. Audit precise accounting definitions (NEXT)

**Why:** “Free equity operational account” may be different from *disposisjonsfond*. Confusing them could change which municipality we label as financially strong or weak. The formulas and reporting scope for all nine indicators require review.

**What we still must do:** Inspect `definition_review.csv` and the original `metadata.json`, verify SSB notes, scope, numerator, denominator, unit and years. A reviewer should be able to reproduce every decision.

**Decision:** Not yet done; this is the immediate scientific blocker.

### Step 9. Correct and perform full collection (PLANNED)

The old bulk collector still chooses region codes without filtering them for each historical year. **Do not run it unchanged.** The new extractor must intersect the table's available codes with the year-specific KLASS snapshot and document missingness and continuity per year, table and indicator.

Only then will we collect full 2016–2025 files, perform account reconciliation, compare 2019–2020 accounting breaks, and assemble the original-data ZIP with hashes and audit reports.

### Step 10. Match and analyze municipalities (FUTURE)

Once scientific data gates pass, choose comparable strong and weak municipalities under frozen rules, analyze their ten-year financial statements and ratios, then test broader associations/predictability with the national panel. No results or causal claims have been generated for this new comparison.

---

## Part C — How to read the findings spreadsheet

Each row in `phase1a_findings_matrix.csv` and the Excel workbook has:

| Column | Question it answers |
|---|---|
| Finding ID | How do we refer to the finding unambiguously? |
| Phase | What part of the workflow produced it? |
| Observed finding | What exactly happened? |
| Evidence and precise scope | Which file or terminal observation supports it, and over how many municipalities/years? |
| Status | Pass, fail, open, blocked, or limited audit? |
| Evidence level | Technical, data-quality, scientific, or empirical? |
| Evidence locator | Where can another researcher verify it? |
| Required next step | What decision or test comes next? |

**Worked example — `PILOT-002`:**  
Observed: 18/18 values were numeric, from **two municipalities in 2016**.  
Evidence: user's local SSB pilot run and recorded SHA-256.  
Interpretation: historical year-aware extraction retrieves numeric observations.  
Not proved: the financial values' accounting definitions or national generalizability.  
Next action: manual definition review and multi-year collection validation.

## Part D — Financial indicator learning table

All nine indicators had unit metadata according to your local audit, but **none has been signed off for exact formula/scope or 2016–2025 comparability**. The working names below are interpretations to verify against SSB's official metadata.

| SSB code | Working interpretation | Role in our study | Important caveat |
|---|---|---|---|
| KOSAGD230000 | Net operating result ratio | Primary outcome P1 | Verify numerator, denominator, scope |
| KOSAGD290000 | Annual accumulated surplus/deficit ratio | Secondary balance | Do not equate with a stock of reserves |
| KOSKG280000 | Working capital excluding pension premium deviation | Liquidity | Check pension accounting treatment |
| KOSKG400000 | Net interest exposure ratio | Financial risk | Verify liabilities/assets included |
| KOSKG320000 | Net loan debt ratio | Primary outcome P3 | Check consolidated versus municipal scope |
| KOSAG110000 | Unrestricted revenue per person | Baseline matching | Check the population denominator |
| KOSKG210000 | Free equity operational account | Secondary buffer only | **Not automatically P2 disposisjonsfond** |
| KOSAGI10000 | Gross investment expenditures / revenues | Investment intensity | Verify year and expenditure accounting |
| KOSAGI210000 | Self-investment financing share | Candidate explanatory factor | Verify included funding sources |

**Formula example (purely illustrative, not a real municipality):**

\[
\text{Operating result ratio} = 100\cdot\frac{\text{net operating result}}{\text{gross operating revenues}}
\]

If hypothetical net operating result is NOK 5 million and gross revenues are NOK 100 million, the ratio is **5%**. That arithmetic is straightforward, but the scientific challenge is ensuring the two account definitions match SSB's exact convention. We will not calculate new municipal ratios until that is verified.

## Part E — Terms you should understand

- **Raw data:** The source's original download, kept without edits.
- **Metadata:** The accompanying definitions, dimensions, code lists, units, labels, update information, and explanatory notes.
- **Observation / cell:** A value at the intersection of municipality, indicator and year.
- **Null / missing:** No usable numeric value. It must not become zero without source justification.
- **JSON-stat2 status:** A code that accompanies an observation; its interpretation must follow provider documentation.
- **KLASS:** SSB's official classifications, used here to validate municipality codes valid on a date.
- **SHA-256:** A digital fingerprint of file bytes. Matching hashes support byte-level integrity, not financial meaning.
- **Manifest:** Log of which endpoint, parameters, time, bytes, and hash produced a file.
- **Automated gate:** Machine-enforceable rules (e.g., 18 expected cells, all finite, valid 2016 codes).
- **Scientific gate:** Human/source-backed decisions (e.g., finance numerator, denominator, scope and historical comparability).
- **Reconciliation:** Checking a computed financial ratio against official related account values and published indicators.
- **Longitudinal continuity:** Verifying that each observation represents a comparable government entity across time.

## Part F — What we may and may not claim in the paper today

**Supported:**
1. The metadata probe passed six requests in the local workflow.
2. The original 2016 pilot had 0/18 numeric observations under codes 3101/3103.
3. Year-aware codes 0101/0104 recovered 18/18 numeric observations in the local pilot.
4. Nine indicators had unit metadata and the local automated numeric/identity audit passed.
5. The definition review and 2016–2025 comparability check are outstanding.

**Not supported:**
- That all data sources have been collected;
- that all nine ratio definitions have been scientifically validated;
- that the complete 2016–2025 panel is comparable;
- that a strongest or weakest municipality has been selected;
- that ROI, liquidity, debt or financial practices explain any observed performance difference;
- that any factor has been tested causally.

## Part G — Required data-release gate before analysis

| Audit gate | Evidence required | Current assessment |
|---|---|---|
| File integrity | Source files + hashes + source endpoints | Pilot-only evidence |
| Source definitions | Official footnotes, verified accounting scopes, units and formula components | BLOCKED |
| Annual continuity | KLASS year-by-year identity mapping, accounting breaks | BLOCKED |
| Availability | All requested tables, codes, years; explain missingness | BLOCKED |
| Financial reconciliation | Recompute/reconcile ratios to official accounts where possible | BLOCKED |
| Case-selection readiness | P1, verified P2 disposisjonsfond, P3 and matching controls | BLOCKED |

**Next action:** Review `reports/phase1a/financial_pilot_audit/pilot_12134_2016_20261011T162926430705Z_definition_review.csv` and the original `data/raw/ssb/pilot/12134/metadata.json`. Upload them to the chat to enable an evidence-grounded definition signoff. Preserve local originals. Do not modify raw SSB files.

## Part H — How to incorporate these records into GitHub

Suggested locations (the package already uses these relative paths):

```
research/records/phase1a_findings_matrix.csv
research/records/phase1a_problem_fix_log.csv
docs/PHASE1A_FINDINGS_LEARNING_GUIDE.md
```

These are **non-destructive supplements**. Your existing `01_project_methodology.md`, `02_problem_and_fix_log.md`, `03_findings_evidence.md`, and `04_status_next_steps.md` are older snapshots. Update them only after comparing with your local versions and incorporating the verified new findings. Keep the original audit reports and raw files out of the normal Git commit.

**Code provenance:** https://github.com/marsman1976/norway-municipal-financial-performance  
**Primary SSB table:** https://www.ssb.no/en/statbank1/table/12134/  
**Official KLASS implementation:** https://github.com/statisticsnorway/klass
