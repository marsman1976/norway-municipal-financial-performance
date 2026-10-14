"""Offline regression tests for the official-source probe."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "phase1a_01_probe_official_sources.py"

spec = importlib.util.spec_from_file_location("source_probe", SOURCE)
assert spec is not None and spec.loader is not None
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class SourceProbeTests(unittest.TestCase):
    def test_codechanges_is_valid(self):
        probe.check_payload("klass_changes", {
            "codeChanges": [{"changeOccurred": "2020-01-01", "oldCode": "0101"}]
        })

    def test_old_changes_key_is_rejected(self):
        with self.assertRaises(ValueError):
            probe.check_payload("klass_changes", {
                "changes": [{"changeOccurred": "2020-01-01", "oldCode": "0101"}]
            })

    def test_missing_date_is_rejected(self):
        with self.assertRaises(ValueError):
            probe.check_payload("klass_changes", {"codeChanges": [{"newCode": "3001"}]})

    def test_ssb_dimensional_consistency(self):
        probe.check_payload("ssb_12134_metadata", {
            "id": ["ContentsCode", "Tid"],
            "dimension": {"ContentsCode": {}, "Tid": {}}
        })
        with self.assertRaises(ValueError):
            probe.check_payload("ssb_12134_metadata", {
                "id": ["ContentsCode", "Tid"], "dimension": {"ContentsCode": {}}
            })


if __name__ == "__main__":
    unittest.main()
