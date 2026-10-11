# Release-stopping audit gates

An accepted package must have **all** blocking gates supported by a reproducible log and original raw bytes. `quality_gates.csv` is the authoritative checklist.

- Source manifest contains a verified timestamp, official URI, file hash and data rights for every file.
- Accounting population must be constant. Municipality-only versus consolidated source data are separate.
- Identifiers remain exact four-character municipality strings, valid by historical year.
- Changes and reclassifications are checked against official KLASS event structure; simple code renumbering is not a merger.
- Ratio numerators/denominators reconcile to official published ratios. Investigate any mismatch rather than rewriting originals.
- P2 unrestricted reserve ratio must use `disposisjonsfond`, not the free-equity operational key figure.
- All value statuses and missingness flags are classified. No missing value is silently imputed.
- Published table years are *not* evidence that every municipality has every observation.
- Conventional corporate ROE/ROIC/ROCE/EBITDA cannot be silently computed for whole municipalities.
- Cash-flow data require auditable cash movements, not net operating result as a proxy.
- Project returns require an individual cost/benefit ledger and horizon; only available after case selection.
- No 2023–2025 outcomes contribute to case selection. No variable feature-year after forecast origin.
- Final whole-panel ratio coverage is reported by table/year/entity/variable. Any metric without 2016–2025 coverage is either restricted to valid subset or excluded from ten-year comparisons.
