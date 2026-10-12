# Phase 1A.6 — Financial definitions, findings, and research lesson

**Project:** Norwegian municipal financial performance, 2016–2025  
**Audit date:** 2026-10-12  
**Evidence scope:** SSB table 12134, **2016 only**, Halden 0101 and Moss 0104; nine published indicators; KLASS year-2016 municipality list.  
**Decision:** **AUTOMATED PILOT VERIFIED; FULL SCIENTIFIC DEFINITIONS AND DECADE COMPARABILITY NOT APPROVED.**

## 1. What was in the uploaded archive?

Exactly four original user-supplied files were examined without changing their bytes: source metadata, official KLASS 2016 codes, one corrected 18-cell JSON-stat2 response, and the nine-row definition-review CSV. SHA-256 values are in `reports/phase1a/phase1a6_source_hash_manifest.csv`. Original financial response hash: `181abcb10698d0b03886220c68564c0e55e9e3ba5e421a6b6e53cf1d3a9b5f02`.

The archive alone **does not include 2017–2025 financial observations** or underlying original accounting entries. It therefore cannot prove decade-long construct stability.

## 2. Our workflow, explained as a research lesson

### Step A — Define before downloading
We froze the intended ten-year study and distinguished core outcomes (net operating result, **actual unrestricted reserve / disposisjonsfond**, net loan debt) from diagnostic metrics. Why? Choosing cases after observing dozens of ratios creates selection bias and an artificial ranking.

### Step B — Confirm source provenance
We stored original responses and verified bytes with **SHA-256**. SHA-256 is a deterministic fingerprint of file content. Matching hashes demonstrate that the file under audit is byte-for-byte the same as the recorded pilot, **not** that its accounting interpretation is true.

### Step C — Use historical municipality identities
The first 2016 request used modern codes (3101, 3103) and returned **0/18 numeric observations**. The revised request intersected 2016 KLASS codes with table metadata: Halden **0101**, Moss **0104**, giving **18/18 numeric observations**. Thus the change in year-code selection is an empirically supported explanation for the recovered results in these two pilot records. It does not yet prove the correction covers all 2016–2025 histories.

### Step D — Validate data shape and missingness
The corrected JSON-stat2 response has region × indicator × time dimensions **2 × 9 × 1**, giving $2\times 9\times 1=18$ cells, all finite and non-null. The missing-value status field is absent in this response; therefore there are no observed missing status markers for this particular pilot. It would be wrong to claim that the SSB catalogue contains no missing values generally.

### Step E — Validate units before calculations
The metadata gives eight percentage-based indicators and one indicator in **NOK per inhabitant**. Comparisons of percent values are differences in **percentage points**, whereas differences for per-capita revenue are **NOK per person**. Summing percentages and NOK as though they had the same scale is invalid.

### Step F — Verify constructs, not just names
A published ratio label suggests a mathematical pattern such as

$$\mathrm{NetOperatingResultRatio}_{it} = 100 \times \frac{\mathrm{NetOperatingResult}_{it}}{\mathrm{GrossOperatingRevenue}_{it}}.$$ 

But numerator/denominator *account codes*, fiscal accounting entity, and year-to-year reconciliation **remain unsigned** for all nine indicators. The appendix CSV lists every unresolved item. No accounting-specific numerator has been fabricated.

**Special warning — KOSKG210000:** SSB's official indicator definition states that the free equity operational account measure reflects distributable reserves **minus the annual deficit**. This is not simply the stock of `disposisjonsfond`. The study's primary reserve outcome **P2 remains unavailable** until actual fund balances and the relevant denominator are separately verified.

### Step G — Check temporal comparability
SSB's table-level note warns of a KOSTRA municipality-*group* classification break between 2019 and 2020. SSB's statistical-methods page additionally identifies regional changes and some alterations to the chart of accounts around the 2019 legal changes. These are **distinct** from the first-pilot problem. We must validate historical municipal continuity, KOSTRA group membership, and definition bridges separately.

### Step H — Approve only what the evidence supports
The pilot passes identity, structural and unit checks for two municipalities in 2016. The study cannot yet select financial winners/losers, infer causes, calculate ten-year ratios, or fit predictive models.

## 3. Actual financial observations — educational example only

| Official indicator | Unit | Halden 2016 | Moss 2016 | Halden − Moss |
|---|---|---:|---:|---:|
| Net operating surplus as a percentage of gross operating revenues (per cent) | per cent | 4.5 | 3.9 | +0.6 pp |
| Annual accumulated surplus/deficit  as a percentage of gross operating revenues (per cent) | per cent | 2.4 | 1.8 | +0.6 pp |
| Working capital  excl. pension premium deviation as a percentage of gross operating revenues (per cent) | per cent | -11.9 | 12.7 | -24.6 pp |
| Net interest rate exposure as a percentage of gross operating revenues (per cent) | per cent | 50.2 | 48.7 | +1.5 pp |
| Net loan debt as a percentage of gross operating revenues (per cent) | per cent | 96.2 | 96.8 | -0.6 pp |
| Unrestricted revenues per capita (NOK) | NOK | 50,043.0 | 48,369.0 | +1,674.0 NOK/person |
| Free equity operational account (per cent) | per cent | -7.4 | 11.5 | -18.9 pp |
| Gross investment expenditures as a percentage of gross operating revenues (per cent) | per cent | 12.7 | 10.3 | +2.4 pp |
| Self-investment financing as a percentage of total gross investment expenditures (per cent) | per cent | 10.7 | 53.2 | -42.5 pp |

The comparison is an **arithmetic contrast**, not a matched-case research finding. For example, Halden's 2016 net operating result ratio is 4.5%, versus Moss's 3.9%: a difference of **0.6 percentage points**, not a causal treatment effect. Conversely, the free-equity-account series is -7.4% for Halden and 11.5% for Moss, but interpreting either value as the exact `disposisjonsfond` reserve balance would be wrong. **Neither municipality has been selected as our strong or weak case.**

## 4. Variable-by-variable review table

| Code | Meaning from label | Mathematical working expression | Research use | Definition approval |
|---|---|---|---|---|
| `KOSAGD230000` | Net operating surplus as a percentage of gross operating revenues (per cent) | Net operating surplus / gross operating revenues × 100 | Primary P1; conditional | **NO** |
| `KOSAGD290000` | Annual accumulated surplus/deficit  as a percentage of gross operating revenues (per cent) | Annual accumulated surplus or deficit / gross operating revenues × 100 | Secondary sustainability diagnostic | **NO** |
| `KOSKG280000` | Working capital  excl. pension premium deviation as a percentage of gross operating revenues (per cent) | Working capital excluding pension premium deviation / gross operating revenues × 100 | Supporting liquidity | **NO** |
| `KOSKG400000` | Net interest rate exposure as a percentage of gross operating revenues (per cent) | Net interest-rate exposure / gross operating revenues × 100 | Supporting financing-risk predictor | **NO** |
| `KOSKG320000` | Net loan debt as a percentage of gross operating revenues (per cent) | Net loan debt / gross operating revenues × 100 | Primary P3; conditional | **NO** |
| `KOSAG110000` | Unrestricted revenues per capita (NOK) | Unrestricted revenues / population | Matching baseline; conditional | **NO** |
| `KOSKG210000` | Free equity operational account (per cent) | Free equity in operational account; percent denominator not established in preserved metadata | NOT P2; supporting only | **NO** |
| `KOSAGI10000` | Gross investment expenditures as a percentage of gross operating revenues (per cent) | Gross investment expenditures / gross operating revenues × 100 | Supporting CapEx intensity | **NO** |
| `KOSAGI210000` | Self-investment financing as a percentage of total gross investment expenditures (per cent) | Self-investment financing / total gross investment expenditures × 100 | Supporting financing factor | **NO** |

All working expressions are *label-based interpretation*, not a reproduced ledger calculation. The exact unresolved requirements for each indicator are in `phase1a6_indicator_definition_matrix.csv`.

## 5. What each metric tells us (and cannot tell us)

- **Net operating surplus ratio:** Operating balance relative to operating revenue; useful for tracking fiscal room, but positive one-year values do not prove future sustainability.
- **Annual accumulated surplus/deficit ratio:** An annual operating balance/deficit-related measure; not automatically a ten-year cumulative performance score.
- **Working capital excluding pension deviation:** A liquidity proxy; exclusion of pension premium deviation is central to the interpretation.
- **Net interest-rate exposure:** A *balance-sheet exposure to rate fluctuations*, not an interest-expense ratio. Do not confuse it with debt service paid.
- **Net loan debt:** Relative leverage; may change with numerator or revenue denominator, and not all debt necessarily finances the same services.
- **Unrestricted revenue per capita:** A resource-capacity measure; nominal NOK values should not be confused with inflation-adjusted comparisons over ten years.
- **Free equity operational account:** An adjusted balance after annual deficit; **not interchangeable with unrestricted reserve fund**.
- **Gross capital investment ratio:** Investment intensity, not project return or efficiency by itself.
- **Self-investment financing ratio:** Share of investment expenditures financed by the specified own-financing concept; not automatically equivalent to cash generated or economic ROI.

## 6. What we can and cannot claim

**Verified from supplied files:** two official 2016 region identities, nine indicator labels and units, 18 non-null values, original 2016 raw-data SHA-256, table-level notes on grouping breaks. **Corroborated externally:** the scope of municipal accounts, the public definition of adjusted free equity, and SSB's warnings regarding 2019–2020 changes.

**Not verified:** ledger components, 2016–2025 historical comparability, national missingness, separately measured `disposisjonsfond`, core case-matching variables, cross-table reconciliation, causal drivers, or any financial-performance ranking.

## 7. Next controlled actions and pass/fail criteria

1. Retrieve official indicator definition and historic accounting-code documentation; record numerator, denominator, municipal/consolidated scope, rounding and applicable years. **Pass:** supported evidence links and unambiguous coding for each chosen variable.
2. Retrieve account-level financing/balance tables and the exact `disposisjonsfond` balance. **Pass:** compute P2 and distinguish it from free equity and accumulated deficit.
3. Freeze 2016–2017 KOSTRA matching-group versions and year-by-year KLASS municipality mappings. **Pass:** mapped entity histories and explicit structural-exclusion decisions.
4. Amend the **full collector** to choose only year-valid regions, preserve source bytes, and count missing statuses for each year separately. **Pass:** real sample across 2016–2025 with reproducible region-year coverage and no silent zero-filling.
5. Perform independent account-to-published-indicator reconciliation on a sampled panel, with documented rounding tolerances. **Pass:** all critical identities and errors within declared thresholds.
6. **Only after gates 1–5:** authorize strong/weak matching and statistical experiments.

## 8. Source URLs and provenance

- Original public SSB table and definitions: https://www.ssb.no/en/statbank1/table/12134/
- SSB municipal-account methods and comparability: https://www.ssb.no/en/offentlig-sektor/kommunale-finanser/statistikk/kommuneregnskap
- SSB free-equity official variable definition: https://www.ssb.no/kompis/statbank/?id=28d0afd2-5d6b-435e-a871-0e993729b6f5&lang=en&val=KOSKG210000&ver=94059
- SSB separate municipal vs consolidated-scope key figures: https://www.ssb.no/en/statbank1/table/13542/
- KOSTRA group history: https://www.ssb.no/klass/klassifikasjoner/112/versjoner
- SSB corrections and historical-account caveats: https://www.ssb.no/kostra/rettinger-i-tidligere-ars-publiserte-data

**GitHub workflow:** keep the authoritative originals under ignored `data/raw/`, the new Markdown learning guide under `docs/`, and small evidence matrices under `research/records/`. Do not commit this evidence ZIP or raw numerical JSON to a public repository until provenance/reuse choices are reviewed.
