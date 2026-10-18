"""Offline tests for Phase 1A Repair 02; no network access required."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "phase1a_02_collect_official_raw.py"
SPEC = importlib.util.spec_from_file_location("year_aware_collector", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def dim(items):
    return {"category": {"index": {value: n for n, value in enumerate(items)}}}


class HistoricalCollectorTests(unittest.TestCase):
    def setUp(self):
        self.region = "KOKkommuneregion0000"
        self.ids = [self.region, "ContentsCode", "Tid"]
        self.metadata = {"id": self.ids, "dimension": {
            self.region: dim(["0101", "0104", "3101", "3103"]),
            "ContentsCode": dim(["A", "B"]), "Tid": dim(["2016", "2025"])}}
        self.k16 = {"codes": [{"code": "0101", "name": "Halden"},
                               {"code": "0104", "name": "Moss"}]}
        self.k25 = {"codes": [{"code": "3101", "name": "Halden"},
                               {"code": "3103", "name": "Moss"}]}

    def test_only_historical_codes_selected(self):
        p = module.make_year_plan(self.metadata, self.k16, "12134", 2016, [], 100)
        self.assertEqual(p["selected"], ["0101", "0104"])
        self.assertNotIn("3101", p["selected"])

    def test_2025_uses_different_codes(self):
        p = module.make_year_plan(self.metadata, self.k25, "12134", 2025, [], 100)
        self.assertEqual(p["selected"], ["3101", "3103"])

    def test_modern_code_in_2016_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing in KLASS"):
            module.make_year_plan(self.metadata, self.k16, "12134", 2016, ["3101"], 100)

    def test_part_splitting_respects_cell_limit(self):
        p = module.make_year_plan(self.metadata, self.k16, "12134", 2016, [], 2)
        self.assertEqual(len(p["parts"]), 2)
        self.assertTrue(all(x["expected_cells"] <= 2 for x in p["parts"]))

    def test_missing_status_counts(self):
        p = module.make_year_plan(self.metadata, self.k16, "12134", 2016, [], 100)
        response = {"id": self.ids, "size": [2, 2, 1], "dimension": {
            self.region: dim(["0101", "0104"]), "ContentsCode": dim(["A", "B"]),
            "Tid": dim(["2016"])}, "value": [2.0, None, 0.0, 1.0],
            "status": {"1": "."}}
        result = module.observation_stats(response, self.metadata, p, p["parts"][0])
        self.assertEqual((result["numeric"], result["missing"]), (3, 1))
        self.assertEqual(result["missing_statuses"], {".": 1})
        response["dimension"][self.region] = dim(["0104", "0101"])
        with self.assertRaises(ValueError):
            module.observation_stats(response, self.metadata, p, p["parts"][0])

    def test_immutable_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "raw.json"
            self.assertEqual(module.save_original(p, b"source A"), "SAVED")
            self.assertEqual(module.save_original(p, b"source A"), "EXISTS_IDENTICAL")
            with self.assertRaises(FileExistsError):
                module.save_original(p, b"source B")
            self.assertEqual(p.read_bytes(), b"source A")


if __name__ == "__main__":
    unittest.main()
