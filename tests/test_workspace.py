"""No network required: only internal preparation-package tests."""
import csv
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceTests(unittest.TestCase):
    def test_manifest_exists(self):
        p = ROOT / 'research/preflight/00_READ_FIRST/package_file_checksums.csv'
        self.assertTrue(p.is_file())
        with p.open(encoding='utf-8-sig', newline='') as f:
            self.assertGreater(len(list(csv.DictReader(f))), 10)

    def test_prepare_documents(self):
        p = subprocess.run([sys.executable, 'scripts/verify_workspace.py'],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, msg=p.stderr + p.stdout)
        self.assertIn('PREPARATION DOCUMENTS: PASS', p.stdout)

    def test_scientific_gate_blocks(self):
        p = subprocess.run([sys.executable, 'scripts/verify_workspace.py', '--require-data'],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn('SCIENTIFIC DATA GATE: BLOCKED', p.stdout)


if __name__ == '__main__':
    unittest.main()
