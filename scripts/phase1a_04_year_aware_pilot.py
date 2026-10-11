#!/usr/bin/env python3
"""Phase 1A.4: year-aware, read-only-to-existing-files SSB table 12134 pilot.

Run from the research repository root. This script never overwrites an existing
raw observation, an existing KLASS snapshot, or a diagnostic report.

This is a controlled validation PILOT, not a full-data collector. It selects
historically valid municipalities by intersecting source metadata and an
*official year-specific* KLASS snapshot before making the observation request.
No financial ratios, case selection, cleaning or imputation are performed.

Usage:
    python scripts/phase1a_04_year_aware_pilot.py --self-test
    python scripts/phase1a_04_year_aware_pilot.py --dry-run
    python scripts/phase1a_04_year_aware_pilot.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests

API = 'https://data.ssb.no/api/pxwebapi/v2/tables'
KLASS = 'https://data.ssb.no/api/klass/v1/classifications/131'
TIMEOUT = 90


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')


def dim_codes(meta: dict, dim_id: str) -> list[str]:
    category = meta['dimension'][dim_id]['category']
    index = category['index']
    if isinstance(index, list):
        out = [str(x) for x in index]
    elif isinstance(index, dict):
        positions = list(index.values())
        if sorted(positions) != list(range(len(positions))):
            raise ValueError(f'Non-contiguous index positions for {dim_id}')
        out = [str(k) for k, _ in sorted(index.items(), key=lambda p: p[1])]
    else:
        raise ValueError(f'Unrecognized category index for {dim_id}')
    if not out or len(set(out)) != len(out):
        raise ValueError(f'Empty or duplicated codes in dimension {dim_id}')
    return out


def dimension_ids(meta: dict) -> list[str]:
    ids = meta.get('id')
    if not isinstance(ids, list) or not isinstance(meta.get('dimension'), dict):
        raise ValueError('Not a JSON-stat2 dataset')
    if set(ids) != set(meta['dimension']):
        raise ValueError('Dimension keys and IDs disagree')
    return ids


def require_dimensions(meta: dict) -> tuple[str, str]:
    ids = dimension_ids(meta)
    region = [x for x in ids if 'region' in x.lower() or 'kommun' in x.lower()]
    years = [x for x in ids if x.lower() in ('tid', 'time', 'year')]
    if len(region) != 1 or len(years) != 1:
        raise ValueError(f'Cannot identify one region and one year dimension: {ids}')
    return region[0], years[0]


def official_klass_codes(doc: dict) -> dict[str, str]:
    records = doc.get('codes')
    if not isinstance(records, list) or not records:
        raise ValueError('KLASS codesAt response lacks nonempty codes list')
    result = {}
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get('code'), str):
            raise ValueError('KLASS record lacks string code')
        code = item['code']
        if code in result:
            raise ValueError('Duplicate code in KLASS snapshot: ' + code)
        result[code] = str(item.get('name', ''))
    return result


def choose_codes(meta: dict, klass: dict, year: int, requested: list[str]):
    region_id, time_id = require_dimensions(meta)
    if str(year) not in dim_codes(meta, time_id):
        raise ValueError(f'Year {year} not present in source metadata')
    available = set(dim_codes(meta, region_id))
    legitimate = official_klass_codes(klass)
    if not requested or len(set(requested)) != len(requested):
        raise ValueError('Provide unique explicit municipality codes')
    unsupported = [c for c in requested if c not in available]
    invalid_year = [c for c in requested if c not in legitimate]
    if unsupported or invalid_year:
        raise ValueError(f'Historical selection blocked. Not in table metadata={unsupported}; '
                         f'not valid in KLASS for {year}={invalid_year}. '
                         'Do not substitute newer municipality codes.')
    return region_id, time_id, [(c, legitimate[c]) for c in requested]


def build_url(table: str, meta: dict, year: int, region_id: str,
              time_id: str, region_codes: list[str]) -> tuple[str, int]:
    params = [('lang', 'en'), (f'valueCodes[{time_id}]', str(year)),
              (f'valueCodes[{region_id}]', ','.join(region_codes))]
    product = len(region_codes)
    for d in dimension_ids(meta):
        if d not in (region_id, time_id):
            params.append((f'valueCodes[{d}]', '*'))
            product *= len(dim_codes(meta, d))
    params.append(('outputFormat', 'json-stat2'))
    if product > 10000:
        raise ValueError(f'Pilot too large ({product} cells); narrow other dimensions')
    return f'{API}/{table}/data?{urlencode(params)}', product


def observation_at(obj, i):
    if isinstance(obj, list):
        return obj[i] if i < len(obj) else None
    if isinstance(obj, dict):
        return obj.get(str(i), obj.get(i))
    raise ValueError('Unexpected JSON-stat2 value/status container')


def validate_observations(doc: dict, meta: dict, year: int,
                          region_id: str, time_id: str,
                          requested: list[str], expected: int) -> dict:
    ids = dimension_ids(doc)
    if ids != dimension_ids(meta):
        raise ValueError('Response dimension IDs/order differ from metadata')
    sizes = [len(dim_codes(doc, d)) for d in ids]
    if sizes != doc.get('size') or math.prod(sizes) != expected:
        raise ValueError('Response size differs from requested cells')
    for d in ids:
        wanted = ([str(year)] if d == time_id else requested if d == region_id
                  else dim_codes(meta, d))
        if dim_codes(doc, d) != wanted:
            raise ValueError(f'Unexpected returned codes/order for {d}')
    values = doc.get('value')
    if not isinstance(values, (dict, list)):
        raise ValueError('Response lacks valid value structure')
    if isinstance(values, list) and len(values) != expected:
        raise ValueError('Dense values incomplete')
    if isinstance(values, dict) and any(
        not str(i).isdigit() or int(i) >= expected for i in values
    ):
        raise ValueError('Sparse value keys invalid')
    statuses = doc.get('status', {})
    if not isinstance(statuses, (dict, list)):
        raise ValueError('Response status is not a list or object')
    if isinstance(statuses, list) and len(statuses) != expected:
        raise ValueError('Dense status length mismatch')
    if isinstance(statuses, dict) and any(
        not str(i).isdigit() or int(i) >= expected for i in statuses
    ):
        raise ValueError('Sparse status keys invalid')
    present = sum(observation_at(values, i) is not None for i in range(expected))
    status_counter = Counter(str(observation_at(statuses, i) or 'UNANNOTATED')
                             for i in range(expected)
                             if observation_at(values, i) is None)
    return {'total_cells': expected, 'non_null': present, 'null': expected - present,
            'null_status_counts': dict(status_counter)}


def fetch(url: str) -> bytes:
    response = requests.get(url, timeout=TIMEOUT, headers={
        'User-Agent': 'NorwegianMunicipalFinanceYearAwarePilot/1.0',
        'Accept': 'application/json'
    })
    response.raise_for_status()
    return response.content


def preserve_bytes(path: Path, b: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != b:
            raise FileExistsError(f'Existing immutable source differs: {path}')
        return 'EXISTS_IDENTICAL'
    # Exclusive creation protects against accidental overwrite.
    with path.open('xb') as f:
        f.write(b)
    return 'SAVED'


def load_or_collect_klass(year: int, path: Path) -> tuple[dict, str]:
    if path.exists():
        b = path.read_bytes()
        state = 'CACHED'
    else:
        url = f'{KLASS}/codesAt.json?date={year}-01-01'
        b = fetch(url)
        state = preserve_bytes(path, b)
    doc = json.loads(b)
    official_klass_codes(doc)
    return doc, state


def save_report(table: str, year: int, selected: list[tuple[str, str]],
                source: Path, url: str, klass_path: Path, stats: dict,
                state: str, stamp: str) -> Path:
    report_folder = Path('reports/phase1a')
    report_folder.mkdir(parents=True, exist_ok=True)
    report = report_folder / f'year_aware_pilot_{table}_{year}_{stamp}.json'
    record = {
        'purpose': 'Historical municipality-code pilot; not analytical verification',
        'table': table, 'year': year, 'selected_regions': [
            {'code': code, 'name_in_KLASS': label} for code, label in selected],
        'api_url': url, 'source_file': str(source), 'source_sha256': sha256(source.read_bytes()),
        'source_bytes': source.stat().st_size, 'write_status': state,
        'klass_codes_path': str(klass_path), 'klass_sha256': sha256(klass_path.read_bytes()),
        'observations': stats,
        'integrity_gate': ('PILOT_HAS_NUMERIC_VALUES_REQUIRES_MANUAL_AUDIT'
                           if stats['non_null'] else 'BLOCKED_ALL_NULL'),
        'warnings': [
            'Original failed pilot is retained unchanged.',
            'Numeric observations do not prove accounting-definition or panel integrity.',
            'Do not rank municipalities or run models yet.',
        ],
    }
    with report.open('x', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return report


def self_test():
    import tempfile
    region = 'KOKkommuneregion0000'
    ids = [region, 'ContentsCode', 'Tid']
    def cat(vals):
        return {'category': {'index': {s: i for i, s in enumerate(vals)}}}
    meta = {'id': ids, 'dimension': {
        region: cat(['3101', '0101', '0104']),
        'ContentsCode': cat(['A', 'B']), 'Tid': cat(['2016'])}}
    klass = {'codes': [{'code': '0101', 'name': 'Halden'},
                       {'code': '0104', 'name': 'Moss'}]}
    r, t, selected = choose_codes(meta, klass, 2016, ['0101', '0104'])
    assert len(selected) == 2
    try:
        choose_codes(meta, klass, 2016, ['3101'])
        raise AssertionError('Invalid historical code accepted')
    except ValueError:
        pass
    url, n = build_url('12134', meta, 2016, r, t, ['0101', '0104'])
    assert n == 4 and '0101' in url
    doc = {'id': ids, 'size': [2, 2, 1], 'dimension': {
        region: cat(['0101', '0104']), 'ContentsCode': cat(['A', 'B']),
        'Tid': cat(['2016'])}, 'value': [1.0, None, 0.0, 2.0],
        'status': {'1': '.'}}
    stats = validate_observations(doc, meta, 2016, r, t, ['0101', '0104'], n)
    assert (stats['non_null'], stats['null']) == (3, 1)
    assert stats['null_status_counts'] == {'.': 1}
    doc['dimension'][region] = cat(['0104', '0101'])
    try:
        validate_observations(doc, meta, 2016, r, t, ['0101', '0104'], n)
        raise AssertionError('Mismatched region order accepted')
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 'raw.json'
        assert preserve_bytes(p, b'original') == 'SAVED'
        assert preserve_bytes(p, b'original') == 'EXISTS_IDENTICAL'
        try:
            preserve_bytes(p, b'different')
            raise AssertionError('Overwrote original raw data')
        except FileExistsError:
            pass
    print('PASS: historical-KLASS selection, missing-value accounting, dimension validation, immutability')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--table', default='12134', choices=['12134'])
    p.add_argument('--year', type=int, default=2016)
    p.add_argument('--region-codes', nargs='+', default=['0101', '0104'],
                   help='Exact historical municipality codes verified against KLASS and metadata')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not 2016 <= args.year <= 2025:
        p.error('Year outside research period 2016–2025')
    raw_meta = Path(f'data/raw/ssb/pilot/{args.table}/metadata.json')
    if not raw_meta.is_file():
        p.error(f'Missing preserved pilot metadata: {raw_meta}')
    meta = json.loads(raw_meta.read_bytes())
    klass_path = Path(f'data/raw/klass/codes_{args.year}.json')
    print(f'Loading official KLASS {args.year} municipality codes...', flush=True)
    klass, status = load_or_collect_klass(args.year, klass_path)
    rid, tid, selected = choose_codes(meta, klass, args.year, args.region_codes)
    url, expected = build_url(args.table, meta, args.year, rid, tid, args.region_codes)
    print('Historical municipality validation: PASS')
    print('Selected:', ', '.join(f'{code} {name}' for code, name in selected))
    print(f'KLASS raw snapshot: {klass_path} ({status})')
    print(f'Expected cells: {expected}')
    if args.dry_run:
        print('DRY RUN: No financial observations downloaded.')
        return 0
    print('Downloading original SSB response...', flush=True)
    b = fetch(url)
    doc = json.loads(b)
    stats = validate_observations(doc, meta, args.year, rid, tid, args.region_codes, expected)
    part = '-'.join(args.region_codes)
    dest = Path(f'data/raw/ssb/pilot_year_aware/{args.table}/year_{args.year}_codes_{part}.json')
    state = preserve_bytes(dest, b)
    report = save_report(args.table, args.year, selected, dest, url,
                         klass_path, stats, state, utc_stamp())
    print(f'Raw: {dest} ({state}, SHA-256={sha256(b)})')
    print(f"Cells={stats['total_cells']} non-null={stats['non_null']} null={stats['null']}")
    print(f"Null status counts: {stats['null_status_counts']}")
    print(f'Independent pilot report: {report}')
    if stats['non_null'] == 0:
        print('BLOCKED_ALL_NULL: Do not start full data collection.')
        return 2
    print('PILOT_HAS_NUMERIC_VALUES_REQUIRES_MANUAL_AUDIT')
    print('Full collection still blocked until historical coverage/footnote and accounting checks.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
