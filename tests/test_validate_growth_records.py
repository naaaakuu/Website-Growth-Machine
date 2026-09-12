"""Tests for status and evidence-link validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import validate_growth_records  # noqa: E402


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class ValidateGrowthRecordsTests(unittest.TestCase):
    def test_completed_operational_record_can_link_to_existing_evidence_id(self):
        with tempfile.TemporaryDirectory() as directory:
            growth = Path(directory) / ".growth"
            write_json(growth / "state.json", {"status": "initialized"})
            write_json(growth / "evidence" / "ev-001.json", {"id": "EV-001"})
            write_json(
                growth / "experiments" / "exp-001.json",
                {"id": "EXP-001", "status": "complete", "evidence_ids": ["EV-001"]},
            )
            result = validate_growth_records.validate_growth_records(growth)

        self.assertTrue(result["valid"])
        self.assertEqual(result["summary"]["linked_local_evidence"], 1)
        experiment = next(item for item in result["records"] if item["file"] == "experiments/exp-001.json")
        self.assertEqual(experiment["evidence_links"][0]["path"], "evidence/ev-001.json")

    def test_missing_or_unsafe_completed_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            growth = Path(directory) / ".growth"
            write_json(growth / "state.json", {"status": "active"})
            (growth / "evidence").mkdir(parents=True)
            write_json(
                growth / "audits" / "audit.json",
                {"id": "AUD-001", "status": "released", "evidence": ["../not-evidence.json"]},
            )
            result = validate_growth_records.validate_growth_records(growth)

        self.assertFalse(result["valid"])
        self.assertIn("unsafe_evidence_path", {item["code"] for item in result["errors"]})

    def test_duplicate_operational_ids_and_unknown_status_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            growth = Path(directory) / ".growth"
            write_json(growth / "state.json", {"status": "initialized"})
            (growth / "evidence").mkdir(parents=True)
            write_json(growth / "audits" / "one.json", {"id": "DUP", "status": "not-real"})
            write_json(growth / "releases" / "two.json", {"id": "DUP", "status": "planned"})
            result = validate_growth_records.validate_growth_records(growth)

        codes = {item["code"] for item in result["errors"]}
        self.assertIn("unknown_status", codes)
        self.assertIn("duplicate_record_id", codes)

    def test_missing_growth_directory_is_an_invocation_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result = validate_growth_records.validate_growth_records(Path(directory) / ".growth")
        self.assertFalse(result["valid"])
        self.assertTrue(result["invocation_error"])
        self.assertEqual(result["errors"][0]["code"], "missing_growth_directory")


if __name__ == "__main__":
    unittest.main()
