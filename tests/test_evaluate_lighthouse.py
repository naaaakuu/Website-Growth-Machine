"""Offline fixture tests for Lighthouse policy evaluation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import evaluate_lighthouse  # noqa: E402


def lighthouse_report(url="https://example.test/", device="mobile", performance=0.95, lcp=1800, fetch_time=None):
    report = {
        "finalUrl": url,
        "configSettings": {"formFactor": device},
        "categories": {"performance": {"score": performance}, "accessibility": {"score": 0.99}},
        "audits": {"largest-contentful-paint": {"numericValue": lcp}},
    }
    if fetch_time is not None:
        report["fetchTime"] = fetch_time
    return report


class LighthouseEvaluationTests(unittest.TestCase):
    def write_report(self, directory, name, payload):
        path = Path(directory) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_required_cases_min_runs_and_rules_pass_for_distinct_reports(self):
        policy = {
            "required_cases": [
                {"url": "https://example.test/", "device": "mobile"},
                {"url": "https://example.test/", "device": "desktop"},
            ],
            "min_runs": 2,
            "score_rules": {"performance": {"min": 0.9}},
            "metric_rules": {"largest-contentful-paint": {"max": 2500}},
        }
        with tempfile.TemporaryDirectory() as directory:
            reports = [
                self.write_report(directory, "m1.json", lighthouse_report(performance=0.95)),
                self.write_report(directory, "m2.json", lighthouse_report(performance=0.94)),
                self.write_report(directory, "d1.json", lighthouse_report(device="desktop", performance=0.96)),
                self.write_report(directory, "d2.json", lighthouse_report(device="desktop", performance=0.93)),
            ]
            result = evaluate_lighthouse.evaluate_lighthouse(policy, reports)

        self.assertTrue(result["valid"])
        self.assertEqual(result["summary"]["unique_reports"], 4)
        self.assertEqual(result["summary"]["errors"], 0)

    def test_semantically_duplicated_reports_do_not_count_as_independent_runs(self):
        policy = {
            "required_cases": [{"url": "https://example.test/", "device": "mobile"}],
            "min_runs": 2,
        }
        with tempfile.TemporaryDirectory() as directory:
            first = self.write_report(directory, "first.json", lighthouse_report(fetch_time="2026-01-01T00:00:00Z"))
            second = self.write_report(directory, "copied.json", lighthouse_report(fetch_time="2026-01-02T00:00:00Z"))
            result = evaluate_lighthouse.evaluate_lighthouse(policy, [first, second])

        self.assertFalse(result["valid"])
        self.assertEqual(result["summary"]["duplicate_report_groups"], 1)
        self.assertEqual(result["cases"][0]["unique_runs"], 1)
        self.assertEqual(result["cases"][0]["errors"][0]["code"], "insufficient_unique_runs")

    def test_malformed_inconsistent_device_and_threshold_failure_are_reported(self):
        policy = {
            "required_cases": [{"url": "https://example.test/", "device": "mobile"}],
            "score_rules": {"performance": 0.9},
            "metric_rules": {"largest-contentful-paint": 2500},
        }
        with tempfile.TemporaryDirectory() as directory:
            malformed = lighthouse_report()
            malformed["settings"] = {"formFactor": "desktop"}
            bad_path = self.write_report(directory, "inconsistent.json", malformed)
            low_path = self.write_report(directory, "low-score.json", lighthouse_report(performance=0.5, lcp=3000))
            result = evaluate_lighthouse.evaluate_lighthouse(policy, [bad_path, low_path])

        self.assertFalse(result["valid"])
        malformed_codes = {error["code"] for error in result["malformed_reports"][0]["errors"]}
        self.assertIn("inconsistent_device", malformed_codes)
        self.assertEqual({item["name"] for item in result["rule_violations"]}, {"performance", "largest-contentful-paint"})

    def test_invalid_policy_is_distinct_from_report_failure(self):
        result = evaluate_lighthouse.evaluate_lighthouse({"min_runs": 0}, [])
        self.assertFalse(result["valid"])
        self.assertIsNone(result["policy"])
        self.assertIn("invalid_required_cases", {item["code"] for item in result["policy_errors"]})


if __name__ == "__main__":
    unittest.main()
