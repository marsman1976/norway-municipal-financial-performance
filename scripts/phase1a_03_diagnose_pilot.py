#!/usr/bin/env python3
"""Read-only diagnostic for an SSB PxWeb v2 JSON-stat2 pilot.

Does NOT modify source files, fetch data, compute ratios, or select municipalities.
Run from the project root:
    python scripts/phase1a_03_diagnose_pilot.py --table 12134 --year 2016
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def category_codes(doc: dict, dim: str) -> list[str]:
    cats = doc["dimension"][dim]["category"]
    idx = cats["index"]
    if isinstance(idx, list):
        return [str(c) for c in idx]
    if isinstance(idx, dict):
        if sorted(idx.values()) != list(range(len(idx))):
            raise ValueError(f"Bad category offsets for {dim}")
        return [str(code) for code, _ in sorted(idx.items(), key=lambda x: x[1])]
    raise ValueError(f"Unexpected category index: {dim}")


def category_label(doc: dict, dim: str, code: str) -> str:
    cat = doc["dimension"][dim]["category"]
    labels = cat.get("label", {})
    if isinstance(labels, dict):
        return str(labels.get(code, "(no label)"))
    if isinstance(labels, list):
        index = category_codes(doc, dim).index(code)
        return str(labels[index]) if index < len(labels) else "(no label)"
    return "(no label)"


def datum(container, i):
    if isinstance(container, list):
        return container[i] if i < len(container) else None
    if isinstance(container, dict):
        return container.get(str(i), container.get(i))
    raise ValueError("Data/status must be a list or index-keyed dictionary")


def diagnostic(src: Path, meta_path: Path, max_lines: int = 30) -> str:
    if not src.is_file():
        raise FileNotFoundError(f"Pilot raw response not found: {src}")
    if not meta_path.is_file():
        raise FileNotFoundError(f"Pilot source metadata not found: {meta_path}")
    raw = src.read_bytes()
    doc = json.loads(raw)
    meta = json.loads(meta_path.read_bytes())
    ids = doc["id"]
    if set(ids) != set(doc["dimension"]):
        raise ValueError("JSON-stat2 pilot dimensions inconsistent")
    ordered = [category_codes(doc, d) for d in ids]
    cells = 1
    for c in ordered:
        cells *= len(c)
    if cells != len(doc["value"]) and isinstance(doc["value"], list):
        raise ValueError("Dense value count and dimension product disagree")
    if cells != __import__('math').prod(doc["size"]):
        raise ValueError("JSON-stat2 size mismatch")

    rid = next((d for d in ids if "region" in d.lower() or "kommun" in d.lower()), None)
    tid = next((d for d in ids if "tid" == d.lower() or "time" in d.lower() or "year" in d.lower()), None)
    cid = next((d for d in ids if d.lower() == "contentscode" or "contents" in d.lower()), None)
    by_region = defaultdict(Counter)
    missing_status = Counter()
    valrows = []
    available = 0
    value_obj = doc["value"]
    status_obj = doc.get("status", {})
    if not isinstance(status_obj, (dict, list)):
        raise ValueError("Unexpected status structure")
    for i, tuple_codes in enumerate(itertools.product(*ordered)):
        m = dict(zip(ids, tuple_codes))
        v = datum(value_obj, i)
        status = datum(status_obj, i)
        if v is None:
            missing_status[str(status) if status is not None else "UNANNOTATED_NULL"] += 1
        else:
            available += 1
        if rid:
            by_region[m[rid]]["non_null" if v is not None else "null"] += 1
        if i < max_lines:
            label = category_label(meta, cid, m[cid]) if cid and cid in meta.get('dimension',{}) else ""
            label = label[:72]
            valrows.append((i, m.get(rid, ""), m.get(tid, ""), m.get(cid, ""), str(v), str(status), label))

    lines = [
        "PHASE 1A.3 — READ-ONLY PILOT DIAGNOSTIC",
        "Pilot file: " + str(src),
        "SHA-256: " + hashlib.sha256(raw).hexdigest(),
        f"Dimensions: {[(d, len(c)) for d, c in zip(ids, ordered)]}",
        f"Total cells: {cells}",
        f"Non-null observations: {available}",
        f"Null observations: {cells-available}",
        f"Null status counts: {dict(missing_status)}",
        "",
        "Selected region codes (must be audited against year-specific KLASS):"
    ]
    if rid:
        for code in category_codes(doc, rid):
            label = category_label(meta, rid, code)
            counts = by_region[code]
            lines.append(f"  {code}: {label} | nonnull={counts['non_null']}, null={counts['null']}")
    else:
        lines.append("  REGION DIMENSION NOT IDENTIFIED")
    lines += ["", "First pilot cells (code-level; null is never zero):"]
    for i, r, t, c, v, status, label in valrows:
        lines.append(f"  {i:03d} | region={r} year={t} indicator={c} | value={v} status={status} | {label}")
    lines += ["", "INTEGRITY DECISION:"]
    if not available:
        lines.append("  BLOCKED_ALL_NULL — Saved raw file is structurally valid but contains no numeric observations.")
        lines.append("  Do NOT run full extraction yet. Identify suitable region/year combinations first.")
    else:
        lines.append("  HAS_NUMERIC_OBSERVATIONS — Manual review of region identity, units and status is still required.")
    lines.append("  Do not replace nulls with zero or treat this as proof of a complete historical panel.")
    return "\n".join(lines) + "\n"


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        def dimension(codes, labels):
            return {"category":{"index":{c:i for i,c in enumerate(codes)},"label":dict(zip(codes,labels))}}
        sample={"id":["Region","ContentsCode","Tid"],"size":[2,2,1],
                "dimension":{"Region":dimension(["3101","0101"],["Halden new","Halden old"]),
                             "ContentsCode":dimension(["A","B"],["alpha","beta"]),
                             "Tid":dimension(["2016"],["2016"])},
                "value":[None,None,1.1,None],"status":{"0":"..","1":"..","3":".."}}
        f=base/'pilot.json'; m=base/'metadata.json'
        f.write_text(json.dumps(sample));m.write_text(json.dumps(sample))
        out=diagnostic(f,m)
        assert "Non-null observations: 1" in out and "null=2" in out and "3101" in out
        sample["value"]={"2":1.1}
        f.write_text(json.dumps(sample))
        assert "Non-null observations: 1" in diagnostic(f,m)
        print("PASS: read-only JSON-stat2 dense/sparse/status diagnostic tests")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table",default="12134")
    parser.add_argument("--year",default="2016")
    parser.add_argument("--part",default="0001")
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        self_test(); return
    folder=Path("data/raw/ssb/pilot")/args.table
    p=folder/f"year_{args.year}_part_{args.part}.json"
    m=folder/"metadata.json"
    s=diagnostic(p,m)
    print(s)
    output=Path("reports/phase1a")/f"pilot_{args.table}_{args.year}_diagnostic.txt"
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing diagnosis: {output}")
    output.write_text("Generated at " + datetime.now(timezone.utc).isoformat() + "\n" + s)
    print(f"Diagnostic report: {output}")


if __name__=="__main__":
    main()
