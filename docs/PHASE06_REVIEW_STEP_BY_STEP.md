# Teaching guide — Phase 06 metadata review

## Research question of this phase

Do SSB tables 12364 (basic accounts) and 12143 (accounting key ratios) offer candidate financial concepts and year metadata that could support our 2016–2025 municipality study?

**Not the question:** whether Halden or Moss is financially stronger, or whether a factor causes better results.

## 1. What you executed

The file `scripts/phase1a_06_discover_financial_accounts.py` downloaded the original metadata for two tables on its first run and reused its local, preserved copies on later runs. Metadata specify *available dimensions, codes, labels and units*, not the underlying numerical time series.

Your ZIP contains twelve CSVs: manifest, coverage, candidates and reconciliation gates, repeated for three run timestamps. The three instances should be treated as an audit history, not as three independent samples.

## 2. Why each report matters

- **Source manifest:** file path, source URL, source SHA-256 recorded at retrieval, byte count, retrieval status. It helps trace the source used.
- **Coverage and scope:** year dimension, region dimension, table-level notes, number of listed codes and signed-off flags. It identifies potential historical availability.
- **Account candidates:** official SSB dimension/code/label and heuristic topic hits. A keyword hit is only a lead.
- **Reconciliation gates:** documents scientific stopping conditions. Correct status is BLOCKED_PENDING_REVIEW for all ten gates.

## 3. What your reports actually say

- Table 12364: **81** non-geographic/non-year dimension entries; **26** keyword matches.
- Table 12143: **25** such entries; **13** keyword matches.
- Combined **106** entries, **39** matches. Some are measure (`ContentsCode`) entries, and some codes appear in both tables.
- Both tables list every year **2016–2025** in their metadata.
- Original source SHA-256 strings are stable across your three CSV runs, but the original JSON files were not included in this review ZIP. We cannot independently recompute those hashes here.
- All ten scientific reconciliation gates are blocked, correctly.

## 4. A critical discovery missed by keywords

The original account inventory contains **code `56`, 'General funds (M)'**, in both tables. It was not selected by our reserve-keyword dictionary. Official SSB KOSTRA accounting guides for 2015, 2018 and 2024 refer to the balance account `56` as **Disposisjonsfond**. Thus it is a high-priority account to test, not yet a verified numerical series.

We must keep code `56` distinct from `KG21` (free equity operational account), which includes other accounting considerations. Using KG21 for P2 without reconciliation could select the wrong municipalities.

## 5. Calculating the reserve ratio — hypothesis, not yet a result

Possible intended ratio:

`Reserve ratio (%) = 100 × Verified disposisjonsfond balance / Verified gross operating revenues`

Potential codes: numerator `56` and denominator `AGD13` from table 12364. Table 12143 contains `56` and both an amount and a percent measure type.

Before calculation, confirm the source's numerical sign conventions, same reporting scope, financial-year convention, NOK 1000 scaling, precise numerator/denominator definition and published rounding rules.

If both account totals are in NOK 1000, the unit factor cancels in the ratio. That is a mathematical statement; it does *not* prove accounting equivalence.

## 6. Important changes in historical data

- **2019–2020:** table notes identify changes in KOSTRA municipality-group classifications. The comparison group cannot simply be treated as a fixed label over time.
- **2024:** several debt-instrument codes were introduced, with older codes ending in 2023. Avoid splicing incompatible line items.
- **Historical municipality identities:** use valid codes per reference year; our earlier 2016 18-null pilot is a concrete failure example.
- **Reporting scope discrepancy:** table 12143 is titled `(M)` but the English table note mentions county authorities. Verify its official Norwegian description/definition before interpreting scope.

## 7. Run the offline review script

From repository root:

```bash
source .venv/bin/activate
python scripts/phase1a_06b_review_discovery_results.py --self-test
python scripts/phase1a_06b_review_discovery_results.py --zip phase06_results_for_review.zip
```

This writes two files under `reports/phase1a/phase06_review/` using the latest input run timestamp. It never alters the original ZIP or data files. If running twice, use a new `--out` directory (the program intentionally refuses to overwrite existing generated evidence).

Read the generated Markdown first. Review the prioritized-account CSV next. Only commit the independently reviewed finding record under `research/records/`, not the original data or auto-generated reports.

## 8. What the status labels mean

- **PASS_CSV:** the reports agree internally, not confirmation against original JSON bytes.
- **SUPPORTED_DOCUMENTATION:** a particular account-code interpretation is supported by an official guide.
- **CANDIDATE_ONLY:** the source label is relevant but its precise use is unresolved.
- **BLOCKED:** ratio reconstruction, full panel collection, matching and regression cannot proceed yet.

## 9. Next scientific milestone

Obtain the two original JSON metadata files, verify their recorded SHA-256, and design a controlled year-aware 2016 and recent-year extraction for `56`, `AGD13`, `AGD23`, `KG31`, with 12143 amount/percent cross-check. Record errors and evidence before any full download.

The old full collector also needs a 2016–2025 year-aware municipality identity fix. Do not use it unchanged.
