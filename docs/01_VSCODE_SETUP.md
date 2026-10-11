# New VS Code setup: data-first municipal-finance project

## Prerequisites
- Python 3.11+ (`python --version` or `python3 --version`)
- VS Code and the recommended Python extension
- Git (optional until a source-control repository is created)

## Ubuntu / Linux
From inside this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/verify_workspace.py
python -m unittest discover -s tests -v
python scripts/inventory_raw.py
```

## Windows PowerShell
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/verify_workspace.py
python -m unittest discover -s tests -v
python scripts/inventory_raw.py
```

If PowerShell activation is blocked, run `.venv\Scripts\python.exe` directly instead of changing Windows' global execution policy.

## Open VS Code
Use `File > Open Folder` and choose this project folder. Then run
`Ctrl+Shift+P > Python: Select Interpreter > .venv`.
Open `Terminal > New Terminal` and run the commands above.
Run tasks with `Terminal > Run Task`. The tasks call `python`; select an activated VS Code terminal interpreter or adjust the command to your platform.

## Interpretation
`PREPARATION DOCUMENTS: PASS` means the **documentation ZIP files** are intact.
It does NOT imply that raw numerical SSB/KLASS data have been downloaded or validated.
`SCIENTIFIC DATA GATE: BLOCKED_RAW_NOT_COLLECTED` is the expected current result.

Use `python scripts/verify_workspace.py --require-data` to verify that research cannot proceed; exit code 2 means blocked. No scripts for selecting municipalities or fitting models are included.

## Next step
Download official source files from the registered URLs in `research/preflight/01_sources/source_catalog.csv`, save unmodified files to the appropriate `data/raw/` subfolder, retain accompanying metadata and footnotes, then run the raw inventory. The 24 scientific integrity checks and manual approvals still need implementation and evidence before any case selection.
