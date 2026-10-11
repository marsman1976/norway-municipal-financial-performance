# Norwegian Municipal Financial Performance (2016–2025)

**VS Code starter repository: DATA-FIRST / NOT YET A VERIFIED NUMERICAL DATASET**

Objective: compare one financially strong and one weak **structurally comparable** Norwegian municipality over ten years, with complete appropriate financial ratios and eventual nationwide validation.

## Start here

1. Read `docs/01_VSCODE_SETUP.md`.
2. Open this folder in VS Code.
3. Create/activate `.venv`, install `requirements.txt`.
4. Run `python scripts/verify_workspace.py`.
5. Run `python -m unittest discover -s tests -v`.
6. Inspect the official catalogue in `research/preflight/SOURCE_REGISTER.xlsx` and `research/preflight/01_sources/source_catalog.csv`.
7. Do **not** select municipalities or fit models: no official raw SSB/KLASS observations have been acquired/verified.

## First outputs

- `reports/preflight/workspace_status.json` — documents package integrity, registered counts, raw-file counts and the BLOCKED scientific data gate.
- `reports/phase1a/raw_file_inventory.csv` — SHA-256 inventory of any raw files you later save in `data/raw/`.
- `research/records/` — 4 living records (methodology, errors/fixes, findings, next steps).

## Where everything belongs

- `config/study_config.json` — study years and **proposed** freeze state.
- `data/raw/{ssb,klass,metadata,municipal_reports}` — untouched official files once collected.
- `data/interim/` — future audited transformations.
- `data/processed/` — future validated panel; NOT created now.
- `research/preflight/` — EXACT files from earlier pre-acquisition ZIP, including 37 source entries, 54 conceptual fields, 77 ratios, 24 checks and a copy of the previous paper. **NO municipal observations.**
- `research/records/` — editable living logs copied from the preflight package.
- `scripts/` — only a workspace verifier and raw-file checksum inventory; no selection/model code.
- `tests/` — internal checks without network access.
- `.vscode/` — editor settings and tasks.

## Research barriers

- `P2` unrestricted reserves still require a verified numerator and unit.
- KLASS continuity and historical 2016/2017 KOSTRA group membership remain uncollected.
- Detailed 2016–2019 balance-sheet historical bridge is not presumed.
- Direct collection failed in the earlier environment. Avoid claiming numeric readiness based on a source list.
- Holdout 2023–2025 is new-case-selection holdout; the previous paper considered overlapping years, so not a wholly independent research program holdout.

The file `research/preflight/00_READ_FIRST/collection_status.json` is the original, immutable source-package collection status. No manual checkboxes may override missing numerical data or unresolved definitions.
