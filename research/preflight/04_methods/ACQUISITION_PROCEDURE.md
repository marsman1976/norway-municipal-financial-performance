# Official collection — manual export procedure (no analysis code)

## For every table in source_catalog.csv
1. Open the SSB table URL in the catalogue. Check description, release date, notes, accounting unit (NOK / NOK 1000 / percent), and region dimension.
2. Use the new Statbank API v2 link or UI download to export source **metadata JSON** (preferably) and raw data **JSON-stat2**, by municipality, year and all needed content concepts. Use 2016–2025 years if supported by that table.
3. Make **chunked** requests for large tables, by years and/or verified content codes, respecting the API 800,000-cell and 30-requests/minute limits. Save query URLs separately; never silently discard errors.
4. Select **municipality** rows only and exclude national/group/county aggregates. Preserve codes like 0101 as strings.
5. Store raw bytes under `raw/ssb/<table_id>/<table_id>_<firstyear>-<lastyear>_<chunk>.(json|csv)`; save accompanying metadata and footnotes. Log original byte hash to source_download_receipts_EMPTY.csv (rename output to receipts.csv).
6. For table 07459 capture sexes and age bands explicitly; verify total once and do not double-count total/both-sex and sex-specific records.
7. For KLASS-131 download year-specific code lists, changes, and correspondence for 2016–2025. Keep 2020 and 2024 split/merger events explicitly.
8. For KLASS-231 verify municipal-group memberships for **2016 and 2017**, not a present-day classification group.
9. Verify P2 (disposisjonsfond) against detailed numerator and operational revenue before the 2018–2022 selection.
10. Preserve detailed 2020–2025 account files separately until an official 2016–2019 accounting bridge is signed off.

### API documentation
- https://www.ssb.no/en/api/pxwebapiv2
- https://www.ssb.no/en/api/pxwebapi
- https://www.ssb.no/en/statbank1/list/kostrahoved/
- https://dataportal.ssb.no/classifications/131/codes
- https://dataportal.ssb.no/classifications/231/codes

### Do not prematurely compute ratios
Do not infer hidden data codes from English fragments; inspect exact `ContentsCode`/statistical-value codes in API metadata and lock those to the dictionary. Do not use “not downloaded” as zero.
