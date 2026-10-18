# Phase 1A — Living findings snapshot

**As of 2026-10-11.** The results below are recorded from the user's local terminal output and the available GitHub scripts. The original numeric files and generated definition-review CSV were not directly inspected here. This document supplements, not replaces, `03_findings_evidence.md`.

| ID | What we observed | What it means | Status | What remains |
|---|---|---|---|---|
| SETUP-001 | VS Code project and GitHub repository exist | Project setup | PASS | Use version control for next validated scripts |
| SETUP-002 | Raw inventory initially found zero files | Initial raw inventory | PASS (at initial inventory) | Do not confuse initial zero files with current file inventory |
| API-001 | Six SSB/KLASS requests responded and passed basic structure checks | API connectivity | PASS (local log) | Save exact endpoint manifest with research records locally |
| BUG-001 | KLASS changes endpoint used codeChanges rather than changes | KLASS response format | RESOLVED | Preserve fix in scripts and problem log |
| PLAN-001 | Table 12134 dry-run generated 30 requests with max 2700 planned cells | Download planning | PASS (dry-run) | Do not mistake planning for downloaded data |
| PILOT-001 | 0/18 numeric cells (18 missing; status `.`) using codes `3101`,`3103` for 2016 | Initial pilot unusable; missing is not zero. | FAIL | Keep original raw file immutable as evidence |
| DIAG-001 | Diagnostic refused to overwrite an existing report | Duplicate report handling | SAFEGUARD | Read existing report; do not delete to conceal the previous failure |
| FIX-001 | Validated historic 2016 codes 0101 Halden, 0104 Moss | Year-aware municipal codes | RESOLVED (pilot) | Extend year-aware selection to full collector, not just pilot |
| PILOT-002 | 18/18 numeric cells using historical codes `0101`,`0104` for 2016 | Historical code correction recovered 2016 financial observations. | PASS (local log) | Review every numeric indicator's unit and accounting definition |
| AUDIT-001 | 9/9 indicator units present; automated numeric/identity gate passed | Machine-checkable checks passed; not financial signoff. | PASS (limited) | Read definition_review.csv and verify exact definitions |
| DEF-001 | All nine accounting definitions still require scientific signoff | Indicator definition signoff | BLOCKED | Validate SSB footnotes, units, numerator, denominator and accounting scope |
| DEF-002 | SSB free equity operational account is not automatically the same as disposisjonsfond | Do not substitute free equity for verified unrestricted reserves. | BLOCKED | Do not substitute free equity operational account for primary reserve measure |
| CONT-001 | 2016 pilot does not prove 2016–2025 code continuity | Longitudinal geography | BLOCKED | Audit annual 1:1 changes, mergers, splits, KOSTRA group changes |
| COV-001 | Detailed 2020-onward accounting sources cannot automatically fill 2016–2019 | Historical accounting coverage | BLOCKED | Find valid older equivalent or mark metric unavailable for full decade |
| COLL-001 | Only a two-municipality one-year pilot has reported numeric success | Full official data collection | PENDING | Build corrected historical year-aware bulk collector after definition checks |
| CASE-001 | No municipalities have been classified or matched | Strong/weak municipality selection | BLOCKED | Wait for final source integrity and P1/P2/P3 definitions |
| HYP-001 | No success/failure factor has been empirically established for the new paper | Financial causes of performance | UNTESTED | Test later with cases and nationwide panel; avoid causal claims |

**Evidence classification:** API, code, storage and automated tests are *technical*. Accounting signoff and longitudinal consistency are *scientific*. The strong/weak municipality comparison and explanatory-factor tests are *empirical* and have not started.

**Next evidence needed:** `pilot_12134_2016_20261011T162926430705Z_definition_review.csv` and `data/raw/ssb/pilot/12134/metadata.json`.

**No full 2016–2025 data release or municipality performance finding has been approved.**
