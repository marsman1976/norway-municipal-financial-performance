# What each type of data will do

| Data family | Official sources | Why needed | When used | Key integrity risk |
|---|---|---|---|---|
| Financial key ratios | 12134, 12143, 12135, 12137 | Predefined P1/P2/P3 screening, liquidity, leverage | Phase 1B onward | P2 cannot silently use free equity operational account |
| Financial amounts / operating funds | 12364, 13553, 12858 | Cross-check denominators, reconstruct ratios, measure spending | Phases 1A, 2–6 | NOK 1000 vs NOK/person and accounting definitions |
| Investment financing | 12333, 13552 | Capital structure and spending financed internally | Phases 2–6 | 13552 only 2020–25 |
| Detailed operating statements | 13551, 12367 | Personnel, administration, expenditure by function | Phases 2–6 | 13551 only 2020–25; function vs accounting scope |
| Detailed balance sheets | 13202 | Current ratios, liquidity, equity, pension liabilities | Phases 2–6 | Starts 2020; earlier comparable breakdown not guaranteed |
| Consolidated accounts | 13542, 13543, 13545, 13557, 13566 | Separate sensitivity checks for municipally controlled entities | Phase 6 sensitivity | Never mix accounting populations in same panel |
| Population and demographics | 07459, 11820, 11805, 13536, 11618 | Matching controls, per-capita denominators | Phase 1B onward | 0–100 vs 101+ age bands and 31 Dec vs 1 Jan |
| Historical municipality structures | KLASS-131 | Resolve code renumbering and mark mergers/splits | Phase 1A | Non-1:1 reorganization cannot be joined mechanically |
| KOSTRA comparisons | KLASS-231 | Baseline 2016/17 matching strata | Phase 1B | Historical classification group mapping must be verified |
| Education/service | 12255, 13502, 12209, 12362, 12283, 11971 | Safeguard quality, coverage, cost-per-user | Phases 3–7 | Apparent savings can mask reduced coverage |
| Property/infrastructure | 12051, 11791, 11789 | Maintenance and asset quality | Phases 3–7 | Physical units and ownership differ |
| Prices | CPI official series pending exact table | Comparable real NOK time trends | Phases 2–6 | Different CPI reference years |
| Project annual reports | Official audited municipal reports (after pair selection) | Investment ROI, NPV, IRR, true operating cash flow | Phase 6+ | May not exist in nationally standardized KOSTRA accounts |

## Source derived versus analysis derived
SSB published measures can be used as original variables only after source code and units are verified. Reconstructed ratios have explicit numerator, denominator and transformation metadata. Projects do not inherit corporate operating cash flow or ROIC automatically. Structural covariates are lagged/frozen before the case-selection period.

## Period logic
- 2016–2017: match municipalities only using baseline covariates.
- 2018–2022: use outcomes for strong-versus-weak discovery classification.
- 2023–2025: held out from *new case selection*; prior manuscript already explored related years, so not wholly untouched by the broader research program.
