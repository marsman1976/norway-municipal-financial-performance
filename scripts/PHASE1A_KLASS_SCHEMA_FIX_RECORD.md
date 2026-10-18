# Phase 1A.1: KLASS changes JSON-schema correction

Status: LOCAL SOFTWARE TEST PASS; LIVE SSB/KLASS RECHECK REQUIRED.

## Evidence from user's official API probe
- `ssb_12364_metadata`: PASS, HTTP 200.
- `ssb_07459_metadata`: PASS, HTTP 200.
- `klass_2020_codes`: PASS, HTTP 200.
- `klass_changes`: FAIL, HTTP 200, `ValueError: KLASS changes field missing or unexpected`.
- The user did not provide the other two API results in this message.

## Root cause
The original `phase1a_01_probe_official_sources.py` expected a top-level JSON array named `changes`. The KLASS API tests in SSB's official GitHub repository use `codeChanges` at the root of the response (`RestApiChangesIntegrationTest.java`).

## Fix
- Replace `doc.get('changes')` with `doc.get('codeChanges')` in the metadata probe.
- Verify the list is non-empty and every item contains a date plus at least one of old/new municipality codes.
- Also update the later comprehensive audit's `changes.get('changes')` to `changes.get('codeChanges')`; this prevents the same schema mismatch from reappearing.

## Verification
- Python syntax compilation: PASS locally.
- Simulated valid `codeChanges` JSON: PASS.
- Simulated wrong root key: rejected, as expected.
- Simulated missing change date: rejected, as expected.
- Live endpoint: NOT YET RETESTED by user.

## Scientific implications
This was a *schema validation failure*, not proof that municipality changes were absent or that the source server was unavailable. No municipality continuity chains, selection, or financial findings are authorized until official KLASS change events are collected and audited.

## Next step
Run `python scripts/phase1a_01_probe_official_sources.py` with the corrected script, inspect `reports/phase1a/api_probe/endpoint_probe_manifest.csv`, retain source SHA-256 and the raw `klass_changes.json`, and continue only after the six metadata checks pass.

## Sources
- https://data.ssb.no/api/klass/v1/api-guide.html
- https://github.com/statisticsnorway/klass/blob/master/klass-api/src/test/java/no/ssb/klass/api/applicationtest/RestApiChangesIntegrationTest.java
