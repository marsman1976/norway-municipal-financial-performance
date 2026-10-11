# Research data: source-of-truth rules

`raw/ssb/` — downloaded official KOSTRA JSON-stat/CSV source files.

`raw/klass/` — official KLASS classification/member/change-response files.

`raw/metadata/` — API metadata, request queries, footnotes, retrieval receipts.

`raw/municipal_reports/` — source annual reports/project accounts (retain URLs, licenses).

`interim/` — auditable cleaning and linkages, **never** replacements for raw originals.

`processed/` — future verified analytical panels (not created in starter).

Do not rename official content codes without a source crosswalk. Never fill a missing value with zero.
Run `scripts/inventory_raw.py` whenever raw files are added, and preserve the original download bytes.
Raw datasets are excluded from Git. They require a separate data-release archive with verified provenance.
