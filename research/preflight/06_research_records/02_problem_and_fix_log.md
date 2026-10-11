# 02. Problem and fix log

| ID | Problem | Impact | Fix / verification | Status |
|---|---|---|---|---|
| E01 | Direct SSB DNS/download requests fail from working environment | No raw official data collected | Collect in network-accessible environment, attach original ZIP, verify hashes | BLOCKER |
| E02 | Disposisjonsfond vs free equity operational account not identical | Can misclassify the strongest and weakest | Verify original balances and ratio, reconcile to source metadata | OPEN |
| E03 | KLASS municipality identity changes during 2020/2024 | Spurious trends or identity mismatch | Download official change tables, exclude non-1:1 structural histories | OPEN |
| E04 | Historic KOSTRA comparability groups need 2016/2017 crosswalk | False pair matching | Freeze relevant KLASS-231 correspondence/variants | OPEN |
| E05 | Detailed 13551/13552/13202 statements begin 2020 | Cannot calculate all detailed 10-year ratios consistently | Source historical detail or mark 2020-only subset | OPEN |
| E06 | Corporate profitability/accounting ratios may be invalid for municipalities | Misleading ROI/ROA/ROE labels | Project-specific accounting rules and domain tags | OPEN |
| E07 | API status codes, population 101+ and units unknown until source files downloaded | Invalid population/control and ratios | Inspect full metadata, original value-status and reconcile | OPEN |
| E08 | Official PDF manuscript is prior evidence, not raw data | Risk of using published regression coefficients as panel values | Archive manuscript separately; reacquire original KOSTRA numeric files | DOCUMENTED |
| E09 | Prior municipality extraction diagnostic showed historical year rows under a repeated region label (`3101 - 3101 Halden`) | Present-day geographic recoding can be mistaken for contemporaneous municipality codes | Verify source regional dimension and official historical geography before constructing longitudinal IDs | OPEN |
