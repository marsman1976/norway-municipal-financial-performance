#!/usr/bin/env python3
"""Phase 1A.5: read-only audit of the corrected 2016 SSB 12134 pilot.

Reads immutable original SSB JSON-stat2, pilot metadata, and year-specific KLASS.
Writes timestamped audit evidence under reports/phase1a/financial_pilot_audit/.
Never changes raw observations, never calculates derived financial ratios, and
never declares the ten-year data scientifically validated.

Run from the repository root:
    python scripts/phase1a_05_audit_financial_pilot.py --self-test
    python scripts/phase1a_05_audit_financial_pilot.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import tempfile
from collections import Counter
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

TABLE = '12134'
PINNED_RAW_SHA256 = '181abcb10698d0b03886220c68564c0e55e9e3ba5e421a6b6e53cf1d3a9b5f02'
YEAR = '2016'
EXPECTED_REGIONS = {'0101': 'Halden', '0104': 'Moss'}
EXPECTED_INDICATORS = {
    'KOSAGD230000': 'Net operating surplus / gross operating revenues',
    'KOSAGD290000': 'Annual accumulated surplus/deficit / gross operating revenues',
    'KOSKG280000': 'Working capital excluding pension premium deviation / revenue',
    'KOSKG400000': 'Net interest rate exposure / gross operating revenues',
    'KOSKG320000': 'Net loan debt / gross operating revenues',
    'KOSAG110000': 'Unrestricted revenues per capita',
    'KOSKG210000': 'Free equity operational account (NOT automatically disposisjonsfond)',
    'KOSAGI10000': 'Gross investment expenditures / gross operating revenues',
    'KOSAGI210000': 'Self-investment financing / gross investment expenditures',
}
RAW = Path('data/raw/ssb/pilot_year_aware/12134/year_2016_codes_0101-0104.json')
META = Path('data/raw/ssb/pilot/12134/metadata.json')
KLASS = Path('data/raw/klass/codes_2016.json')
OUT = Path('reports/phase1a/financial_pilot_audit')


def hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_json(path: Path) -> tuple[dict, str]:
    if not path.is_file():
        raise FileNotFoundError(f'Required preserved source not found: {path}')
    b = path.read_bytes()
    try:
        obj = json.loads(b)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f'Invalid original JSON: {path}: {exc}') from exc
    if not isinstance(obj, dict):
        raise ValueError(f'Expected JSON object: {path}')
    return obj, hash_bytes(b)


def ordered_codes(doc: dict, dim: str) -> list[str]:
    try:
        index = doc['dimension'][dim]['category']['index']
    except (TypeError, KeyError) as exc:
        raise ValueError(f'Missing category index in {dim}') from exc
    if isinstance(index, list):
        codes = [str(c) for c in index]
    elif isinstance(index, dict):
        try:
            positions = [int(p) for p in index.values()]
        except (ValueError, TypeError) as exc:
            raise ValueError(f'Invalid positions for {dim}') from exc
        if sorted(positions) != list(range(len(index))):
            raise ValueError(f'Category positions not contiguous for {dim}')
        codes = [str(c) for c, _ in sorted(index.items(), key=lambda kv: int(kv[1]))]
    else:
        raise ValueError(f'Unrecognized category index in {dim}')
    if not codes or len(codes) != len(set(codes)):
        raise ValueError(f'Empty or duplicate category codes in {dim}')
    return codes


def dimension_ids(doc: dict) -> list[str]:
    dims = doc.get('dimension')
    ids = doc.get('id')
    if not isinstance(ids, list) or not isinstance(dims, dict) or set(ids) != set(dims):
        raise ValueError('Not a JSON-stat2 dataset with a consistent dimension map')
    return ids


def at(values: list | dict, i: int):
    if isinstance(values, list):
        return values[i]
    return values.get(str(i), values.get(i))


def validate_dense_or_sparse(container: object, n: int, label: str) -> None:
    if isinstance(container, list):
        if len(container) != n:
            raise ValueError(f'{label}: expected {n} dense entries, got {len(container)}')
    elif isinstance(container, dict):
        if any(not str(k).isdigit() or not 0 <= int(k) < n for k in container):
            raise ValueError(f'{label}: illegal JSON-stat2 sparse index')
    else:
        raise ValueError(f'{label}: expected JSON-stat2 list or object')


def label_for(doc: dict, dim: str, code: str) -> str:
    labels = doc['dimension'][dim]['category'].get('label', {})
    return str(labels.get(code, '') if isinstance(labels, dict) else '')


def unit_for(doc: dict, dim: str, code: str) -> str:
    cat = doc['dimension'][dim]['category']
    unit = cat.get('unit', {})
    if isinstance(unit, dict):
        value = unit.get(code)
    else:
        value = unit
    return json.dumps(value, ensure_ascii=False, sort_keys=True) if value is not None else ''


def notes_for(doc: dict, dim: str, code: str) -> str:
    cat = doc['dimension'][dim]['category']
    notes = cat.get('note', {})
    if isinstance(notes, dict):
        selected = notes.get(code, '')
    else:
        selected = notes
    return json.dumps(selected, ensure_ascii=False, sort_keys=True) if selected else ''


def locate_dimensions(meta: dict) -> tuple[str, str, str]:
    dims = dimension_ids(meta)
    regions = [x for x in dims if 'region' in x.lower() or 'kommun' in x.lower()]
    times = [x for x in dims if x.lower() in ('tid', 'year', 'time')]
    contents = [x for x in dims if x.lower() == 'contentscode']
    if len(regions) != 1 or len(times) != 1 or len(contents) != 1 or len(dims) != 3:
        raise ValueError(f'Cannot uniquely identify region, time, content (dims={dims})')
    return regions[0], times[0], contents[0]


def klass_codes(doc: dict) -> dict[str, str]:
    recs = doc.get('codes')
    if not isinstance(recs, list) or not recs:
        raise ValueError('KLASS lacks nonempty codes list')
    out = {}
    for v in recs:
        if not isinstance(v, dict) or not isinstance(v.get('code'), str):
            raise ValueError('KLASS invalid record')
        code = v['code']
        if code in out:
            raise ValueError(f'Duplicate KLASS code {code}')
        out[code] = str(v.get('name', ''))
    return out


def analyze(raw: dict, meta: dict, klass: dict) -> dict:
    ids = dimension_ids(raw)
    meta_ids = dimension_ids(meta)
    if ids != meta_ids:
        raise ValueError('Pilot and preserved metadata dimension IDs/order disagree')
    region_id, time_id, content_id = locate_dimensions(meta)
    code_lists = {d: ordered_codes(raw, d) for d in ids}
    dimensions = [len(code_lists[d]) for d in ids]
    n = math.prod(dimensions)
    if raw.get('size') != dimensions:
        raise ValueError('JSON-stat2 size differs from category indices')
    if n != 18:
        raise ValueError(f'Expected 18 pilot cells; got {n}')
    regions, years, indicators = code_lists[region_id], code_lists[time_id], code_lists[content_id]
    if regions != list(EXPECTED_REGIONS) or years != [YEAR]:
        raise ValueError(f'Unexpected pilot regions/years: {regions}, {years}')
    if len(indicators) != len(EXPECTED_INDICATORS) or set(indicators) != set(EXPECTED_INDICATORS):
        raise ValueError(f'Unexpected indicator set: {indicators}')
    for d in ids:
        allowed = ordered_codes(meta, d)
        if not set(code_lists[d]).issubset(set(allowed)):
            raise ValueError(f'Pilot contains codes absent from metadata: {d}')
        if d == content_id and code_lists[d] != allowed:
            raise ValueError('Indicator selection/order inconsistent with official metadata')
    historical = klass_codes(klass)
    for code, expected_name in EXPECTED_REGIONS.items():
        if code not in historical:
            raise ValueError(f'2016 code {code} absent from official KLASS snapshot')
        name = historical[code].lower()
        if expected_name.lower() not in name:
            raise ValueError(f'2016 code {code}: expected {expected_name}, KLASS gave {historical[code]}')

    values = raw.get('value')
    statuses = raw.get('status', {})
    validate_dense_or_sparse(values, n, 'value')
    validate_dense_or_sparse(statuses, n, 'status')
    rows = []
    null_states = Counter()
    nonnull_states = Counter()
    for i, combination in enumerate(product(*(code_lists[d] for d in ids))):
        x = dict(zip(ids, combination))
        code = x[content_id]
        region = x[region_id]
        v = at(values, i)
        status = at(statuses, i)
        if v is None:
            null_states[str(status) if status is not None else 'UNANNOTATED'] += 1
        else:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError(f'Cell {i} has invalid numeric value: {v!r}')
            if status is not None:
                nonnull_states[str(status)] += 1
        rows.append({
            'table_id': TABLE, 'year': x[time_id],
            'municipality_code_2016': region,
            'municipality_name_2016_KLASS': historical[region],
            'indicator_code': code,
            'indicator_label_SSB': label_for(meta, content_id, code) or label_for(raw, content_id, code),
            'proposed_research_interpretation_UNVERIFIED': EXPECTED_INDICATORS[code],
            'unit_metadata_raw_json': unit_for(meta, content_id, code),
            'indicator_note_metadata_raw_json': notes_for(meta, content_id, code),
            'value_original': '' if v is None else v,
            'numeric_present': 'YES' if v is not None else 'NO',
            'observation_status': '' if status is None else str(status),
            'financial_definition_signed_off': 'NO',
        })
    nonnull = sum(row['numeric_present'] == 'YES' for row in rows)
    unit_count = sum(bool(unit_for(meta, content_id, c)) for c in indicators)
    label_count = sum(bool(label_for(meta, content_id, c)) for c in indicators)
    checks = {
        'expected_18_cells': n == 18,
        'all_18_values_finite_numeric': nonnull == 18,
        'all_regions_valid_in_2016_KLASS': True,
        'indicator_set_matches_12134_metadata': True,
        'nine_indicators_have_labels_in_metadata': label_count == 9,
        'no_status_on_numeric_values': not bool(nonnull_states),
    }
    summary = {
        'study_phase': '1A.5', 'table_id': TABLE, 'year': YEAR,
        'regions': list(EXPECTED_REGIONS), 'expected_cells': n,
        'numeric_observations': nonnull, 'null_observations': n - nonnull,
        'null_status_counts': dict(null_states),
        'numeric_status_counts': dict(nonnull_states),
        'indicators_with_metadata_unit': unit_count,
        'indicators_with_metadata_label': label_count,
        'automated_checks': checks,
        'automated_gate': ('PASS_NUMERIC_AND_IDENTITY__DEFINITION_REVIEW_PENDING'
                           if all(checks.values()) else 'BLOCKED_AUTOMATED_AUDIT'),
        'scientific_approval': 'BLOCKED_NOT_YET_AUDITED_FOR_DEFINITIONS_OR_2016_2025_COMPARABILITY',
        'critical_definition_caveat': ('KOSKG210000 (free equity operational account) is NOT '
                                       'interchangeable with verified unrestricted reserve fund / disposisjonsfond.'),
        'scope': '2 municipalities × 9 indicators × 1 year ONLY. No national generalization.',
    }
    return {'rows': rows, 'summary': summary, 'indicators': indicators, 'content_id': content_id}


def save_outputs(result: dict, paths: dict[str, str], hashes: dict[str, str], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    prefix = f'pilot_12134_2016_{stamp}'
    csv_path = out_dir / (prefix + '_cells.csv')
    json_path = out_dir / (prefix + '_audit.json')
    review_path = out_dir / (prefix + '_definition_review.csv')
    notes_path = out_dir / (prefix + '_notes.json')

    fields = list(result['rows'][0])
    with csv_path.open('x', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(result['rows'])

    report = {'summary': result['summary'], 'inputs': [
        {'role': key, 'path': paths[key], 'sha256': hashes[key]}
        for key in ('raw', 'metadata', 'klass')],
        'note': 'These are exact source hashes from this run. Original bytes were not modified.'}
    with json_path.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    content_id = result['content_id']
    with review_path.open('x', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=[
            'indicator_code', 'source_label', 'metadata_unit_raw_json',
            'intended_construct_UNVERIFIED', 'exact_accounting_definition_verified',
            'accounting_scope_verified', '2016_2025_comparability_verified',
            'definition_notes_and_source_url', 'review_status'])
        w.writeheader()
        by_indicator = {r['indicator_code']: r for r in result['rows']}
        for c in result['indicators']:
            r = by_indicator[c]
            w.writerow({'indicator_code': c, 'source_label': r['indicator_label_SSB'],
                        'metadata_unit_raw_json': r['unit_metadata_raw_json'],
                        'intended_construct_UNVERIFIED': EXPECTED_INDICATORS[c],
                        'exact_accounting_definition_verified': 'NO',
                        'accounting_scope_verified': 'NO',
                        '2016_2025_comparability_verified': 'NO',
                        'definition_notes_and_source_url': '',
                        'review_status': 'REQUIRES_HUMAN_SOURCE_AUDIT'})

    with notes_path.open('x', encoding='utf-8') as f:
        json.dump({'source_audit_note': 'Exact SSB metadata and dataset footnote fields below; raw input files remain source of truth.',
                   'footnote_fields_available_in_preserved_metadata': 'Inspect input metadata source JSON and per-indicator notes',
                   'common_manual_flags': [
                       'SSB table-level note, source and latest update date',
                       'KOSTRA definition changes, especially around 2020',
                       'Municipality accounts versus municipal consolidated accounts',
                       'KOSKG210000 is not necessarily disposisjonsfond',
                       'Published rounded ratios versus raw-account reconstructed ratios',
                       'Financial indicator availability beyond this pilot (2017–2025)',
                   ]}, f, indent=2, ensure_ascii=False)
    return [csv_path, json_path, review_path, notes_path]


def self_test() -> None:
    r, t, c = 'KOKkommuneregion0000', 'Tid', 'ContentsCode'
    ids = [r, c, t]
    def dim(cs):
        return {'category': {'index': {v: i for i, v in enumerate(cs)},
                             'label': {v: 'label_' + v for v in cs}}}
    indicator_codes = list(EXPECTED_INDICATORS)
    meta = {'id': ids, 'dimension': {r: dim(['0101','0104','3101']),
                                   c: dim(indicator_codes), t: dim(['2016','2017'])}}
    raw = {'id': ids, 'size': [2,9,1], 'dimension': {r: dim(['0101','0104']),
                                                      c: dim(indicator_codes), t: dim(['2016'])},
           'value': [float(i) for i in range(18)], 'status': {}}
    klass = {'codes': [{'code': '0101','name': 'Halden'}, {'code': '0104','name': 'Moss'}]}
    res = analyze(raw, meta, klass)
    assert res['summary']['automated_gate'].startswith('PASS')
    assert res['summary']['numeric_observations'] == 18
    assert len(res['rows']) == 18
    raw['value'][0] = None
    raw['status'] = {'0': '.'}
    res = analyze(raw, meta, klass)
    assert res['summary']['automated_gate'].startswith('BLOCKED')
    assert res['summary']['null_status_counts'] == {'.': 1}
    raw['value'][0] = float('inf')
    try:
        analyze(raw, meta, klass)
    except ValueError:
        pass
    else:
        raise AssertionError('Infinite value was not rejected')
    raw['value'][0] = 0.0
    raw['status'] = {}
    raw['dimension'][r]['category']['index'] = {'3101': 0, '0104': 1}
    try:
        analyze(raw, meta, klass)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid historical municipality code was not rejected')
    with tempfile.TemporaryDirectory() as td:
        raw['dimension'][r] = dim(['0101','0104'])
        res = analyze(raw, meta, klass)
        paths = save_outputs(res, {'raw':'raw.json','metadata':'meta.json','klass':'klass.json'},
                             {'raw':'abc','metadata':'def','klass':'ghi'}, Path(td))
        assert len(paths) == 4 and all(p.is_file() for p in paths)
        with paths[2].open(encoding='utf-8', newline='') as f:
            assert len(list(csv.DictReader(f))) == 9
    print('PASS: 18-cell mapping, 2016 KLASS, numeric/missing statuses, dimensions, read-only output')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw', type=Path, default=RAW)
    p.add_argument('--metadata', type=Path, default=META)
    p.add_argument('--klass', type=Path, default=KLASS)
    p.add_argument('--out', type=Path, default=OUT)
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        self_test()
        return 0
    paths = {'raw': str(args.raw), 'metadata': str(args.metadata), 'klass': str(args.klass)}
    try:
        raw, h_raw = load_json(args.raw)
        if h_raw != PINNED_RAW_SHA256:
            raise ValueError(f'Pilot SHA-256 differs from recorded immutable original: {h_raw} != {PINNED_RAW_SHA256}')
        meta, h_meta = load_json(args.metadata)
        klass, h_klass = load_json(args.klass)
        result = analyze(raw, meta, klass)
        output = save_outputs(result, paths, {'raw': h_raw, 'metadata': h_meta, 'klass': h_klass}, args.out)
    except (ValueError, KeyError, FileNotFoundError, OSError) as exc:
        print(f'BLOCKED: {type(exc).__name__}: {exc}')
        return 2
    s = result['summary']
    print('=== PHASE 1A.5 — FINANCIAL PILOT INTEGRITY AUDIT ===')
    print(f'Input SHA-256: {h_raw}')
    print(f"Cells={s['expected_cells']} numeric={s['numeric_observations']} null={s['null_observations']}")
    print(f"Indicator labels in metadata={s['indicators_with_metadata_label']}/9")
    print(f"Indicator units provided in metadata={s['indicators_with_metadata_unit']}/9")
    print(f"Automated gate: {s['automated_gate']}")
    print(f"Scientific approval: {s['scientific_approval']}")
    for file in output:
        print(f'WROTE: {file}')
    print('NEXT: verify nine source definitions, units, accounting scopes, and historical comparability.')
    return 0 if s['automated_gate'].startswith('PASS') else 2


if __name__ == '__main__':
    raise SystemExit(main())
