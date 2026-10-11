# Phase 1A.5 — 2016 SSB 12134 financial pilot verification

**Project:** `marsman1976/norway-municipal-financial-performance`  
**Research stage:** Pre-modeling data integrity, **not** nationwide panel validation  
**Status:** Standalone Python audit tested offline; live evaluation against the user's actual immutable 2016 source remains pending.

## Evidence from the user's successful corrected pilot

- Table: SSB KOSTRA **12134**, *Financial key figures for municipalities*.
- Year: **2016**.
- Municipality codes: **0101 Halden**, **0104 Moss** (confirmed by the previously run year-aware KLASS selection).
- **2 municipalities × 9 financial indicators × 1 year = 18 cells**.
- Observations: **18 non-null, 0 null**.
- SHA-256 of preserved corrected pilot: `181abcb10698d0b03886220c68564c0e55e9e3ba5e421a6b6e53cf1d3a9b5f02`.
- Prior failing pilot: 2016 requested using 2024-and-later identifiers `3101`, `3103`; all 18 observations were missing with source status `.`.
- Diagnosis: The year-aware correction strongly supports the code-mismatch explanation. It does not confirm accounting comparability, historical continuity, or any national inference.

## Install and run

Place `phase1a_05_audit_financial_pilot.py` under `scripts/` in the existing repository.

```bash
cd ~/Norway_Municipal_Performance_VSCode_Starter
source .venv/bin/activate
python scripts/phase1a_05_audit_financial_pilot.py --self-test
python scripts/phase1a_05_audit_financial_pilot.py
```

The script expects three **existing, unchanged** source files:

```text
data/raw/ssb/pilot_year_aware/12134/year_2016_codes_0101-0104.json
data/raw/ssb/pilot/12134/metadata.json
data/raw/klass/codes_2016.json
```

If any source is missing, **stop**. Do not produce replacement observations, backfill missing financial data or modify original files. The script checks the corrected pilot against the exact SHA-256 reported by the user.

## Outputs (new, timestamped; never overwrite)

```text
reports/phase1a/financial_pilot_audit/
  pilot_12134_2016_<UTC>_cells.csv
  pilot_12134_2016_<UTC>_audit.json
  pilot_12134_2016_<UTC>_definition_review.csv
  pilot_12134_2016_<UTC>_notes.json
```

The **cells.csv** provides the exact 18 unmodified numbers aligned with municipality code, financial indicator code, SSB label, raw metadata unit, observation status, and source year. The **audit.json** preserves the independent hashes of the three inputs and machine-level validation results. The **definition_review.csv** presents one review row for each of nine indicators, leaving accounting definitions, time comparability, and municipal-versus-consolidated scope explicitly **unverified**. The **notes.json** lists footnote topics that require examination in the official data documentation.

## Checks and limitations

The script checks raw-file integrity against the recorded SHA-256; dimension order; code lists; exact year and municipalities; nine expected indicator codes; matching source metadata; 2016 KLASS code-name validity; absence of nonfinite values; source missing/status codes; and preservation of the original files.

Passing these checks **does not** establish that:

1. Each reported percentage has a stable accounting definition over 2016–2025.
2. The number represents municipal accounts or consolidated municipal accounts consistently.
3. There are no comparability breaks due to KOSTRA revisions or geography changes.
4. The accounting components for each ratio have been reconciled against detailed financial statements.
5. The municipal unrestricted reserve fund (*disposisjonsfond*) equals the SSB indicator *free equity operational account*; these constructs are distinct and must be verified.
6. Both municipalities are suitable for matched case selection; selection must wait for the nationwide continuity-stable, definition-audited panel.

## Exact nine indicators included

| Code | Interpretation to verify | Intended role |
|---|---|---|
| `KOSAGD230000` | Net operating surplus / gross operating revenue | Primary financial performance P1 |
| `KOSAGD290000` | Annual accumulated surplus / deficit | Secondary financial health |
| `KOSKG280000` | Working capital excluding pension premium deviation | Liquidity |
| `KOSKG400000` | Net interest rate exposure | Financial risk |
| `KOSKG320000` | Net loan debt relative to operating revenue | Primary debt measure P3 |
| `KOSAG110000` | Unrestricted revenue per inhabitant | Baseline matching and revenue capacity |
| `KOSKG210000` | Free equity operational account | Supporting buffer indicator only; **not** verified `disposisjonsfond` P2 |
| `KOSAGI10000` | Gross investment spending relative to operating revenue | Investment intensity |
| `KOSAGI210000` | Self-investment financing relative to gross investment spending | Investment-financing analysis |

**P2 unrestricted-reserve / disposisjonsfond needs separate identification and reconciliation.** This pilot cannot establish P2.

## GitHub reproducibility

Version-control code and the phase research logs. Do not commit files under `data/raw/` or `reports/` unless deliberately approved and documented as a release. The project's existing `.gitignore` excludes these directories.

```bash
git add scripts/phase1a_05_audit_financial_pilot.py
# Add the Markdown guide if stored under docs/ or research/records/
git add docs/PHASE1A5_FINANCIAL_PILOT_AUDIT_GUIDE.md
git diff --cached --stat
git commit -m "Audit corrected historical SSB financial pilot"
git push origin main
```

## Decision gate

Proceed to 2016–2025 multi-table collection only after examination of the detailed 9-indicator review and a historical year-specific region-code selection procedure for **every requested year and source**, not merely the small 2016 pilot. The previous full collector's `--pilot` logic selects first-listed codes and must be **fixed** before running it in full mode.
