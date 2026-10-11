# Phase 1A — Historical-region pilot failure and remedy

## Observation (user-run, 2026-10-11)
- Source: SSB PxWeb API v2, table 12134.
- Preserved raw pilot: `data/raw/ssb/pilot/12134/year_2016_part_0001.json`.
- Raw SHA-256: `6382ed57f44c31f658d91cb6b345c8a6e424eb7b9e428bddebec3fee9f817f24`.
- Dimensions: municipality 2 × financial indicators 9 × year 1 = 18 cells.
- Regions: `3101` Halden and `3103` Moss, requested for 2016.
- Values: 0 non-null / 18 null; status code `.` for all 18 null cells.
- Diagnostic reported `BLOCKED_ALL_NULL`.

## Problem E10 — Wrong historical region code selected for year
The original collection script uses the first two region codes in its full metadata list, ignoring the year. The names displayed for those codes are not evidence that the code was valid in the selected year. SSB's historical region guidance notes that old codes retain observations only for their valid period and new codes start in the year they were introduced. SSB's 2016 population tables report Halden `0101` and Moss `0104`. The conclusion that the code mismatch caused these particular 18 nulls remains a strong hypothesis until the corrected query returns valid observations.

Primary references:
- SSB, *Hvordan ivareta historikken med ny kommune- og fylkesstruktur* (2026): https://www.ssb.no/statbank/hvordan-bruke-statistikkbanken/hvordan-ivareta-historikken
- SSB 2016 municipality population tables: https://www.ssb.no/befolkning/statistikker/beftett/aar/2016-12-06?fane=tabell&sort=nummer&tabell=285841

## Problem E11 — Diagnostic report overwrite refusal
A second run of `phase1a_03_diagnose_pilot.py` raises `FileExistsError` for `reports/phase1a/pilot_12134_2016_diagnostic.txt`. The report has already been generated; the exception is the tool's intentional immutable-report safeguard. Read the existing file using `cat`. It is unnecessary and potentially undesirable to delete or overwrite it.

## Fix F10 — Controlled year-aware pilot
1. Use preserved table metadata, not presumed region names, as the valid regional code inventory.
2. Retrieve or reuse original KLASS `codesAt.json?date=2016-01-01` data; retain raw bytes and checksum.
3. Require the selected region codes to appear both in the table metadata and in the official 2016 KLASS snapshot.
4. Test historical municipality codes `0101` (Halden), `0104` (Moss) only after both checks pass.
5. Validate all returned JSON-stat2 dimensions and cell counts; retain original response at a *new* path so the failed pilot is unchanged.
6. Report total cells, null statuses and count of non-null observations. A pilot containing some numeric cells still does **not** constitute scientific source validation.

Script: `scripts/phase1a_04_year_aware_pilot.py`.

## Verification status
- Offline syntax and simulated validation tests: PASS (not live API confirmation).
- Official year-2016 KLASS check on the user's computer: PENDING.
- Corrected live SSB extract: PENDING.
- Longitudinal municipality continuity and accounting-definition audit: BLOCKED.
- Full 2016–2025 collection and municipality matching: BLOCKED.

## Required next evidence
Run:
```
python scripts/phase1a_04_year_aware_pilot.py --self-test
python scripts/phase1a_04_year_aware_pilot.py --dry-run
python scripts/phase1a_04_year_aware_pilot.py
```
Then share the last command's output and the created report JSON's `observations` section. Do not commit raw data or generated reports; do commit this method/fix record and the script.
