"""Tests for safe, idempotent growth-state initialization."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import init_growth_state  # noqa: E402


class InitGrowthStateTests(unittest.TestCase):
    def test_fallback_records_are_created_when_no_template_roots_are_available(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(init_growth_state, "_template_roots", return_value=[]):
            root = Path(directory)
            result = init_growth_state.initialize_growth_state(root)
            state = json.loads((root / ".growth" / "state.json").read_text(encoding="utf-8"))

            self.assertEqual(state["status"], "initialized")
            self.assertTrue((root / ".growth" / "evidence").is_dir())
            self.assertTrue((root / ".growth" / "experiments" / "experiment.template.json").is_file())
            self.assertEqual(result["summary"]["created_records"], len(init_growth_state.RECORD_NAMES))

    def test_explicit_parent_templates_are_renamed_to_canonical_records_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            templates = Path(directory) / "templates"
            templates.mkdir()
            (templates / "state.template.json").write_text('{"from_template": true}', encoding="utf-8")
            (templates / "backlog.template.json").write_text('{"items": ["template"]}', encoding="utf-8")
            (templates / "quality-policy.template.json").write_text('{"status": "DRAFT", "from_template": true}', encoding="utf-8")
            first = init_growth_state.initialize_growth_state(root, template_dir=templates)
            state_path = root / ".growth" / "state.json"
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), {"from_template": True})
            self.assertEqual(json.loads((root / ".growth" / "backlog.json").read_text(encoding="utf-8"))["items"], ["template"])
            self.assertTrue(json.loads((root / ".growth" / "quality-policy.json").read_text(encoding="utf-8"))["from_template"])
            state_path.write_text('{"user": "kept"}', encoding="utf-8")
            second = init_growth_state.initialize_growth_state(root, template_dir=templates)

            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), {"user": "kept"})
            self.assertIn("state.json", second["existing"])
            self.assertGreater(first["summary"]["created_records"], 0)
            self.assertEqual(second["summary"]["created_records"], 0)

    def test_rejects_a_file_as_growth_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "not-a-directory"
            target.write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError):
                init_growth_state.initialize_growth_state(Path(directory), growth_dir=target)


if __name__ == "__main__":
    unittest.main()
