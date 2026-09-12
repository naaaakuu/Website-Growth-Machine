#!/usr/bin/env python3
"""Validate saved Lighthouse JSON reports against an explicit, repeatable policy.

This tool only reads existing JSON files.  It does not invoke Lighthouse, open a
browser, or make network requests.  A policy has this compact shape::

    {
      "required_cases": [
        {"url": "https://example.test/", "device": "mobile"},
        {"url": "https://example.test/", "device": "desktop"}
      ],
      "min_runs": 3,
      "score_rules": {"performance": {"min": 0.9}},
      "metric_rules": {"largest-contentful-paint": {"max": 2500}},
      "allow_extra_cases": true
    }

``required_url_device_cases``, ``min_runs_per_case``, ``scores``, and ``metrics``
are accepted as backwards-friendly aliases.  Score rule values are in Lighthouse's
0..1 scale; metric values use the Lighthouse audit's ``numericValue`` units.

Exit codes
----------
0
    All policy, report-shape, uniqueness, coverage, and threshold checks passed.
1
    Validation completed but at least one policy/data-quality/threshold check failed.
2
    The policy or invocation is invalid.
3
    An unexpected local/runtime error prevented a report from being emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlsplit, urlunsplit


SUPPORTED_DEVICES = {"mobile", "desktop"}
VOLATILE_LHR_KEYS = {
    "fetchTime",
    "generatedTime",
    "timing",
    "userAgent",
    "benchmarkIndex",
    "channel",
}


def normalize_url(value: Any) -> Optional[str]:
    """Normalize an absolute HTTP(S) URL for policy and Lighthouse grouping."""

    if not isinstance(value, str):
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        port = parsed.port
    except (TypeError, ValueError):
        return None
    host = parsed.hostname.lower()
    default_port = 443 if parsed.scheme.lower() == "https" else 80
    netloc = host if port in (None, default_port) else "%s:%s" % (host, port)
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, ""))


def _issue(code: str, message: str, **details: Any) -> Dict[str, Any]:
    value: Dict[str, Any] = {"code": code, "message": message}
    value.update(details)
    return value


def _number(value: Any, *, low: Optional[float] = None, high: Optional[float] = None) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    if low is not None and number < low:
        return None
    if high is not None and number > high:
        return None
    return number


def _normalize_rule(value: Any, *, kind: str, name: str) -> Tuple[Optional[Dict[str, float]], Optional[Dict[str, Any]]]:
    """Normalize one min/max rule, allowing a concise numeric shorthand."""

    if isinstance(value, bool):
        return None, _issue("invalid_rule", "Rule must be a number or an object with min and/or max.", rule_type=kind, rule=name)
    if isinstance(value, (int, float)):
        value = {"min": value} if kind == "score" else {"max": value}
    if not isinstance(value, Mapping):
        return None, _issue("invalid_rule", "Rule must be a number or an object with min and/or max.", rule_type=kind, rule=name)
    normalized: Dict[str, float] = {}
    for bound in ("min", "max"):
        if bound not in value:
            continue
        low, high = (0.0, 1.0) if kind == "score" else (0.0, None)
        numeric = _number(value[bound], low=low, high=high)
        if numeric is None:
            constraint = "between 0 and 1" if kind == "score" else "a finite non-negative number"
            return None, _issue("invalid_rule", "Rule %s must be %s." % (bound, constraint), rule_type=kind, rule=name)
        normalized[bound] = numeric
    if not normalized:
        return None, _issue("invalid_rule", "Rule needs at least one of min or max.", rule_type=kind, rule=name)
    if "min" in normalized and "max" in normalized and normalized["min"] > normalized["max"]:
        return None, _issue("invalid_rule", "Rule min cannot exceed max.", rule_type=kind, rule=name)
    return normalized, None


def normalize_policy(policy: Any) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """Validate and normalize a policy without relying on a third-party schema lib."""

    errors: List[Dict[str, Any]] = []
    if not isinstance(policy, Mapping):
        return None, [_issue("invalid_policy", "Policy JSON must be an object.")]

    raw_cases = policy.get("required_cases", policy.get("required_url_device_cases"))
    if not isinstance(raw_cases, list) or not raw_cases:
        errors.append(_issue("invalid_required_cases", "Policy needs a non-empty required_cases list."))
        raw_cases = []
    cases: List[Dict[str, str]] = []
    seen_cases = set()
    for index, case in enumerate(raw_cases):
        if not isinstance(case, Mapping):
            errors.append(_issue("invalid_case", "Each required case must be an object.", index=index))
            continue
        url = normalize_url(case.get("url"))
        device = case.get("device")
        device = device.lower() if isinstance(device, str) else None
        if url is None or device not in SUPPORTED_DEVICES:
            errors.append(_issue("invalid_case", "A required case needs an absolute HTTP(S) url and mobile or desktop device.", index=index))
            continue
        key = (url, device)
        if key in seen_cases:
            errors.append(_issue("duplicate_required_case", "A URL/device case appears more than once in the policy.", url=url, device=device))
            continue
        seen_cases.add(key)
        cases.append({"url": url, "device": device})

    raw_min_runs = policy.get("min_runs", policy.get("min_runs_per_case", 1))
    if isinstance(raw_min_runs, bool) or not isinstance(raw_min_runs, int) or raw_min_runs < 1:
        errors.append(_issue("invalid_min_runs", "min_runs must be an integer of at least 1."))
        min_runs = 1
    else:
        min_runs = raw_min_runs

    def normalize_rules(raw: Any, kind: str) -> Dict[str, Dict[str, float]]:
        if raw is None:
            return {}
        if not isinstance(raw, Mapping):
            errors.append(_issue("invalid_rules", "%s rules must be an object." % kind))
            return {}
        rules: Dict[str, Dict[str, float]] = {}
        for name, raw_rule in sorted(raw.items(), key=lambda item: str(item[0])):
            if not isinstance(name, str) or not name.strip():
                errors.append(_issue("invalid_rule_name", "%s rule names must be non-empty strings." % kind))
                continue
            rule, rule_error = _normalize_rule(raw_rule, kind=kind, name=name)
            if rule_error:
                errors.append(rule_error)
            elif rule:
                rules[name] = rule
        return rules

    score_rules = normalize_rules(policy.get("score_rules", policy.get("scores", {})), "score")
    metric_rules = normalize_rules(policy.get("metric_rules", policy.get("metrics", {})), "metric")
    raw_allow_extra = policy.get("allow_extra_cases", policy.get("allow_unexpected_cases", True))
    if not isinstance(raw_allow_extra, bool):
        errors.append(_issue("invalid_allow_extra_cases", "allow_extra_cases must be true or false."))
        raw_allow_extra = True
    normalized = {
        "required_cases": cases,
        "min_runs": min_runs,
        "score_rules": score_rules,
        "metric_rules": metric_rules,
        "allow_extra_cases": raw_allow_extra,
    }
    return (None, errors) if errors else (normalized, [])


def _get_nested(mapping: Mapping[str, Any], *keys: str) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _semantic_fingerprint(report: Mapping[str, Any]) -> str:
    """Fingerprint a report while ignoring known run-time metadata fields."""

    def clean(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(key): clean(child) for key, child in sorted(value.items(), key=lambda item: str(item[0])) if str(key) not in VOLATILE_LHR_KEYS}
        if isinstance(value, list):
            return [clean(child) for child in value]
        return value

    encoded = json.dumps(clean(report), sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _extract_device(report: Mapping[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    fields = (
        _get_nested(report, "configSettings", "formFactor"),
        _get_nested(report, "configSettings", "emulatedFormFactor"),
        _get_nested(report, "settings", "formFactor"),
        _get_nested(report, "settings", "emulatedFormFactor"),
    )
    values = {value.lower() for value in fields if isinstance(value, str) and value.strip()}
    if len(values) > 1:
        return None, _issue("inconsistent_device", "Lighthouse device/form-factor fields disagree.", values=sorted(values))
    if not values:
        return None, _issue("missing_device", "No Lighthouse formFactor/emulatedFormFactor was found.")
    device = next(iter(values))
    if device not in SUPPORTED_DEVICES:
        return None, _issue("unsupported_device", "Device must be mobile or desktop.", device=device)
    return device, None


def _parse_report(path: Path, policy: Mapping[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    errors: List[Dict[str, Any]] = []
    source = str(path)
    try:
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError:
        return None, [_issue("missing_report", "Report file does not exist.", file=source)]
    except (OSError, UnicodeDecodeError) as exc:
        return None, [_issue("unreadable_report", "Report could not be read: %s" % exc, file=source)]
    except json.JSONDecodeError as exc:
        return None, [_issue("malformed_json", "Report is not valid JSON: %s" % exc.msg, file=source, line=exc.lineno)]

    report = raw.get("lhr") if isinstance(raw, Mapping) and isinstance(raw.get("lhr"), Mapping) else raw
    if not isinstance(report, Mapping):
        return None, [_issue("malformed_report", "Lighthouse report must be a JSON object.", file=source)]
    final_url = normalize_url(report.get("finalUrl") or report.get("requestedUrl"))
    if final_url is None:
        errors.append(_issue("missing_url", "Report needs an absolute finalUrl or requestedUrl.", file=source))
    requested_value = report.get("requestedUrl")
    if requested_value is not None and normalize_url(requested_value) is None:
        errors.append(_issue("invalid_requested_url", "requestedUrl is not an absolute HTTP(S) URL.", file=source))
    device, device_error = _extract_device(report)
    if device_error:
        device_error["file"] = source
        errors.append(device_error)

    categories = report.get("categories")
    if not isinstance(categories, Mapping):
        errors.append(_issue("missing_categories", "Report categories must be an object.", file=source))
        categories = {}
    scores: Dict[str, float] = {}
    for category in policy["score_rules"]:
        category_data = categories.get(category)
        score = category_data.get("score") if isinstance(category_data, Mapping) else None
        numeric = _number(score, low=0.0, high=1.0)
        if numeric is None:
            errors.append(_issue("missing_or_invalid_score", "Required category score is missing or outside 0..1.", file=source, category=category))
        else:
            scores[category] = numeric

    audits = report.get("audits")
    if policy["metric_rules"] and not isinstance(audits, Mapping):
        errors.append(_issue("missing_audits", "Report audits must be an object when metric rules are used.", file=source))
        audits = {}
    if not isinstance(audits, Mapping):
        audits = {}
    metrics: Dict[str, float] = {}
    for audit_id in policy["metric_rules"]:
        audit_data = audits.get(audit_id)
        numeric = _number(audit_data.get("numericValue") if isinstance(audit_data, Mapping) else None, low=0.0)
        if numeric is None:
            errors.append(_issue("missing_or_invalid_metric", "Required metric numericValue is missing or invalid.", file=source, metric=audit_id))
        else:
            metrics[audit_id] = numeric
    if errors:
        return None, errors
    assert final_url is not None and device is not None
    return {
        "file": source,
        "url": final_url,
        "device": device,
        "scores": scores,
        "metrics": metrics,
        "fingerprint": _semantic_fingerprint(report),
    }, []


def _violates(value: float, rule: Mapping[str, float]) -> Optional[str]:
    if "min" in rule and value < rule["min"]:
        return "below_min"
    if "max" in rule and value > rule["max"]:
        return "above_max"
    return None


def evaluate_lighthouse(policy: Any, report_paths: Iterable[Path]) -> Dict[str, Any]:
    """Evaluate local Lighthouse reports and return an entirely JSON-serializable result."""

    normalized_policy, policy_errors = normalize_policy(policy)
    paths = [Path(path) for path in report_paths]
    if normalized_policy is None:
        return {
            "schema_version": "1.0",
            "valid": False,
            "policy": None,
            "reports_examined": len(paths),
            "policy_errors": policy_errors,
            "malformed_reports": [],
            "duplicate_reports": [],
            "cases": [],
            "rule_violations": [],
            "unexpected_cases": [],
            "summary": {"errors": len(policy_errors), "valid_reports": 0},
        }

    malformed: List[Dict[str, Any]] = []
    valid_reports: List[Dict[str, Any]] = []
    for path in paths:
        parsed, errors = _parse_report(path, normalized_policy)
        if errors:
            malformed.append({"file": str(path), "errors": errors})
        elif parsed:
            valid_reports.append(parsed)

    by_fingerprint: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for report in valid_reports:
        by_fingerprint[report["fingerprint"]].append(report)
    duplicate_reports = [
        {
            "fingerprint": fingerprint,
            "files": sorted(report["file"] for report in reports),
            "case": {"url": reports[0]["url"], "device": reports[0]["device"]},
        }
        for fingerprint, reports in sorted(by_fingerprint.items())
        if len(reports) > 1
    ]

    # A duplicate cannot create a second independent run.  Retain the first input
    # occurrence for coverage and threshold checks so outcomes remain deterministic.
    unique_reports: List[Dict[str, Any]] = []
    seen_fingerprints = set()
    for report in valid_reports:
        if report["fingerprint"] not in seen_fingerprints:
            unique_reports.append(report)
            seen_fingerprints.add(report["fingerprint"])

    grouped_valid: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    grouped_unique: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for report in valid_reports:
        grouped_valid[(report["url"], report["device"])].append(report)
    for report in unique_reports:
        grouped_unique[(report["url"], report["device"])].append(report)

    required_keys = {(case["url"], case["device"]) for case in normalized_policy["required_cases"]}
    cases: List[Dict[str, Any]] = []
    coverage_errors: List[Dict[str, Any]] = []
    for case in normalized_policy["required_cases"]:
        key = (case["url"], case["device"])
        run_count = len(grouped_valid[key])
        unique_count = len(grouped_unique[key])
        case_errors: List[Dict[str, Any]] = []
        if run_count == 0:
            case_errors.append(_issue("missing_required_case", "No valid report matches this required URL/device case.", **case))
        if unique_count < normalized_policy["min_runs"]:
            case_errors.append(
                _issue(
                    "insufficient_unique_runs",
                    "Case does not have enough independent reports.",
                    **case,
                    min_runs=normalized_policy["min_runs"],
                    unique_runs=unique_count,
                )
            )
        coverage_errors.extend(case_errors)
        cases.append({**case, "runs_found": run_count, "unique_runs": unique_count, "required_min_runs": normalized_policy["min_runs"], "errors": case_errors})

    unexpected_cases = [
        {"url": key[0], "device": key[1], "runs_found": len(reports)}
        for key, reports in sorted(grouped_valid.items())
        if key not in required_keys
    ]
    unexpected_errors: List[Dict[str, Any]] = []
    if unexpected_cases and not normalized_policy["allow_extra_cases"]:
        unexpected_errors = [
            _issue("unexpected_case", "A report does not match a required URL/device case.", **case)
            for case in unexpected_cases
        ]

    rule_violations: List[Dict[str, Any]] = []
    for report in unique_reports:
        for category, rule in normalized_policy["score_rules"].items():
            outcome = _violates(report["scores"][category], rule)
            if outcome:
                rule_violations.append(
                    {
                        "file": report["file"],
                        "case": {"url": report["url"], "device": report["device"]},
                        "kind": "score",
                        "name": category,
                        "value": report["scores"][category],
                        "rule": rule,
                        "outcome": outcome,
                    }
                )
        for metric, rule in normalized_policy["metric_rules"].items():
            outcome = _violates(report["metrics"][metric], rule)
            if outcome:
                rule_violations.append(
                    {
                        "file": report["file"],
                        "case": {"url": report["url"], "device": report["device"]},
                        "kind": "metric",
                        "name": metric,
                        "value": report["metrics"][metric],
                        "rule": rule,
                        "outcome": outcome,
                    }
                )

    total_errors = len(policy_errors) + len(malformed) + len(duplicate_reports) + len(coverage_errors) + len(unexpected_errors) + len(rule_violations)
    return {
        "schema_version": "1.0",
        "valid": total_errors == 0,
        "policy": normalized_policy,
        "reports_examined": len(paths),
        "policy_errors": policy_errors,
        "malformed_reports": malformed,
        "duplicate_reports": duplicate_reports,
        "cases": cases,
        "rule_violations": sorted(rule_violations, key=lambda item: (item["file"], item["kind"], item["name"])),
        "unexpected_cases": unexpected_cases,
        "unexpected_case_errors": unexpected_errors,
        "summary": {
            "errors": total_errors,
            "valid_reports": len(valid_reports),
            "unique_reports": len(unique_reports),
            "malformed_reports": len(malformed),
            "duplicate_report_groups": len(duplicate_reports),
            "rule_violations": len(rule_violations),
        },
    }


def _collect_report_paths(values: Iterable[str]) -> List[Path]:
    paths: List[Path] = []
    for value in values:
        path = Path(value)
        if path.is_dir():
            paths.extend(sorted(candidate for candidate in path.rglob("*.json") if candidate.is_file()))
        else:
            paths.append(path)
    return paths


def _write_json(report: Mapping[str, Any], output: Optional[str]) -> None:
    encoded = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        Path(output).write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate saved Lighthouse JSON reports against a URL/device, run-count, score, and metric policy.",
        epilog="Exit 0: pass; 1: validation failure; 2: invalid policy/invocation; 3: local/runtime failure.",
    )
    parser.add_argument("--policy", required=True, help="Path to policy JSON")
    parser.add_argument("reports", nargs="*", help="Lighthouse JSON files or directories (directories are scanned recursively)")
    parser.add_argument("--reports-dir", action="append", default=[], help="Additional directory or report path; may be repeated")
    parser.add_argument("--output", help="Write JSON evaluation to this path instead of stdout")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    inputs = list(args.reports) + list(args.reports_dir)
    if not inputs:
        parser.error("provide at least one report path or --reports-dir")
    try:
        with Path(args.policy).open("r", encoding="utf-8") as handle:
            policy = json.load(handle)
    except FileNotFoundError:
        report = {
            "schema_version": "1.0",
            "valid": False,
            "policy": None,
            "policy_errors": [_issue("missing_policy", "Policy file does not exist.", file=args.policy)],
            "summary": {"errors": 1, "valid_reports": 0},
        }
        try:
            _write_json(report, args.output)
        except OSError as exc:
            sys.stderr.write("evaluate_lighthouse.py: %s\n" % exc)
            return 3
        return 2
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        report = {
            "schema_version": "1.0",
            "valid": False,
            "policy": None,
            "policy_errors": [_issue("unreadable_policy", "Policy could not be parsed: %s" % exc, file=args.policy)],
            "summary": {"errors": 1, "valid_reports": 0},
        }
        try:
            _write_json(report, args.output)
        except OSError as output_error:
            sys.stderr.write("evaluate_lighthouse.py: %s\n" % output_error)
            return 3
        return 2
    try:
        report = evaluate_lighthouse(policy, _collect_report_paths(inputs))
        _write_json(report, args.output)
    except (OSError, TypeError, ValueError) as exc:
        sys.stderr.write("evaluate_lighthouse.py: %s\n" % exc)
        return 3
    return 2 if report["policy_errors"] else (0 if report["valid"] else 1)


if __name__ == "__main__":
    raise SystemExit(main())
