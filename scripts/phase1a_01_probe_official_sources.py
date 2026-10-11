#!/usr/bin/env python3
"""Phase 1A.1: Probe official SSB PxWeb v2 and KLASS endpoints.

Run from repository root: python scripts/phase1a_01_probe_official_sources.py
Only reads public metadata. Never fetches or transforms municipality financial data.
Writes responses/logs under reports/phase1a/api_probe/ (not data/raw).
"""
from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

OUT = Path('reports/phase1a/api_probe')
TARGETS = [
    ('ssb_12134_info', 'https://data.ssb.no/api/pxwebapi/v2/tables/12134?lang=en'),
    ('ssb_12134_metadata', 'https://data.ssb.no/api/pxwebapi/v2/tables/12134/metadata?lang=en'),
    ('ssb_12364_metadata', 'https://data.ssb.no/api/pxwebapi/v2/tables/12364/metadata?lang=en'),
    ('ssb_07459_metadata', 'https://data.ssb.no/api/pxwebapi/v2/tables/07459/metadata?lang=en'),
    ('klass_2020_codes', 'https://data.ssb.no/api/klass/v1/classifications/131/codesAt.json?date=2020-01-01'),
    ('klass_changes', 'https://data.ssb.no/api/klass/v1/classifications/131/changes.json?from=2016-01-01&to=2026-01-01'),
]


def check_payload(name: str, doc: object) -> None:
    if not isinstance(doc, dict):
        raise ValueError('Response root is not a JSON object')
    if name.endswith('_metadata'):
        if not isinstance(doc.get('dimension'), dict) or not isinstance(doc.get('id'), list):
            raise ValueError('Missing JSON-stat2 dimensions or dimension IDs')
    elif name == 'klass_2020_codes':
        if not isinstance(doc.get('codes'), list) or not doc['codes']:
            raise ValueError('KLASS returned no municipality codes')
    elif name == 'klass_changes':
        if not isinstance(doc.get('changes'), list):
            raise ValueError('KLASS changes field missing or unexpected')
    elif name.endswith('_info'):
        if not any(key in doc for key in ('label', 'id', 'variableNames')):
            raise ValueError('Unexpected SSB table-info structure')


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({'User-Agent': 'NorwayMunicipalResearch-DataPreflight/0.1'})
    records = []
    for i, (name, url) in enumerate(TARGETS):
        record = {
            'checked_utc': datetime.now(timezone.utc).isoformat(),
            'source': name, 'url': url, 'status': 'FAIL',
            'http_status': '', 'bytes': '', 'sha256': '', 'error': ''
        }
        try:
            response = session.get(url, timeout=35)
            record['http_status'] = str(response.status_code)
            response.raise_for_status()
            document = response.json()
            check_payload(name, document)
            payload = response.content
            (OUT / f'{name}.json').write_bytes(payload)
            record.update(status='PASS', bytes=str(len(payload)), sha256=hashlib.sha256(payload).hexdigest())
        except (requests.RequestException, ValueError) as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'[:500]
        records.append(record)
        print(f"{name:24s} {record['status']:4s} HTTP={record['http_status'] or '-'} {record['error']}")
        if i < len(TARGETS) - 1:
            time.sleep(2.5)  # Stay well within SSB's published rate limit.
    with (OUT / 'endpoint_probe_manifest.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    passed = sum(r['status'] == 'PASS' for r in records)
    print(f'\nEndpoint probe: {passed}/{len(records)} passed')
    print(f'Manifest: {OUT / "endpoint_probe_manifest.csv"}')
    print('No municipality financial observations were downloaded.')
    return 0 if passed == len(records) else 2


if __name__ == '__main__':
    raise SystemExit(main())
