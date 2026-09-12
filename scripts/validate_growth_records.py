#!/usr/bin/env python3
"""Validate status and evidence linkage for a local ``.growth`` record store.

The validator deliberately uses a small documented convention instead of assuming a
specific project-management product:

* JSON files in ``audits/``, ``experiments/``, and ``releases/`` are operational
  records.  They need a non-empty ``id`` (``issue_id`` is also accepted) and a
  recognised ``status``.
* ``complete``, ``completed``, ``released``, and ``validated`` records need a
  non-empty ``evidence`` (or ``evidence_links``) list.
* Evidence may be a relative file below ``.growth/evidence/`` (or start with
  ``evidence/``), an ``https://``/``http://`` reference, or an ``evidence_ids``
  / ``observation_evidence_ids`` list pointing to an ``id`` in that directory.
  Local evidence must exist and may not escape the evidence directory.

Recognised non-terminal statuses are ``initialized``, ``draft``, ``proposed``,
``planned``, ``queued``, ``in_progress``, ``active``, ``blocked``, and
``observing``.  ``cancelled``/``canceled``, ``archived``, and ``superseded`` are
also accepted terminal administrative states.  The report contains every issue and
is safe to use in CI.

Exit codes: 0 when valid, 1 for validation failures, 2 for an invalid/missing
target, and 3 for a local/runtime failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple
from urllib.parse import urlsplit


OPERATIONAL_DIRECTORIES = {"audits", "experiments", "releases"}
COMPLETION_STATUSES = {"complete", "completed", "released", "validated"}
ALLOWED_STATUSES = {
    "initialized",
    "draft",
    "proposed",
    "planned",
    "queued",
    "in_progress",
    "active",
    "blocked",
    "observing",
    "complete",
    "completed",
    "released",
    "validated",
    "cancelled",
    "canceled",
    "archived",
    "superseded",
}


def _issue(code: str, message: str, **details: Any) -> Dict[str, Any]:
    item: Dict[str, Any] = {"code": code, "message": message}
    item.update(details)
    return item


def _safe_relative(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _reference_value(value: Any) -> Tuple[Optional[str], Optional[str]]:
    """Return a path/URL reference and its source field, or an explanation."""

    if isinstance(value, str) and value.strip():
        return value.strip(), "string"
    if isinstance(value, Mapping):
        for field in ("path", "file", "url", "uri", "href"):
            candidate = value.get(field)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip(), field
    return None, None


def _validate_evidence_reference(value: Any, growth_dir: Path, evidence_dir: Path) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Return (linked item, error) for one evidence reference."""

    reference, source_field = _reference_value(value)
    if reference is None:
        return None, _issue("invalid_evidence_reference", "Evidence entries must be a non-empty string or object with path/file/url/uri/href.")
    parsed = urlsplit(reference)
    if parsed.scheme.lower() in {"http", "https"} and parsed.netloc:
        return {"reference": reference, "kind": "external", "field": source_field}, None
    if parsed.scheme:
        return None, _issue("unsupported_evidence_reference", "Evidence references may be relative files or http(s) URLs.", reference=reference)

    relative = Path(reference)
    if relative.is_absolute() or ".." in relative.parts:
        return None, _issue("unsafe_evidence_path", "Evidence path must stay below .growth/evidence.", reference=reference)
    # The documented form is evidence/x.json.  A short name is convenient and is
    # interpreted below the evidence directory rather than relative to the record.
    candidate = growth_dir / relative if relative.parts and relative.parts[0].lower() == "evidence" else evidence_dir / relative
    if not _safe_relative(candidate, evidence_dir):
        return None, _issue("unsafe_evidence_path", "Evidence path must stay below .growth/evidence.", reference=reference)
    if not candidate.is_file():
        return None, _issue("missing_evidence_file", "Linked local evidence file does not exist.", reference=reference)
    return {"reference": reference, "kind": "local", "path": candidate.relative_to(growth_dir).as_posix(), "field": source_field}, None


def _validate_evidence_id(value: Any, known_ids: Mapping[str, List[str]]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Resolve a parent-template-style evidence id to an evidence record."""

    if not isinstance(value, str) or not value.strip():
        return None, _issue("invalid_evidence_id", "Evidence ids must be non-empty strings.")
    evidence_id = value.strip()
    locations = known_ids.get(evidence_id, [])
    if not locations:
        return None, _issue("missing_evidence_id", "Evidence id does not resolve to a record in .growth/evidence.", evidence_id=evidence_id)
    if len(locations) > 1:
        return None, _issue("ambiguous_evidence_id", "Evidence id resolves to multiple records.", evidence_id=evidence_id, files=sorted(locations))
    return {"reference": evidence_id, "kind": "evidence_id", "path": locations[0], "field": "evidence_ids"}, None


def _record_status(record: Mapping[str, Any], file_name: str, *, required: bool) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    errors: List[Dict[str, Any]] = []
    raw_status = record.get("status")
    if raw_status is None:
        if required:
            errors.append(_issue("missing_status", "Operational records need a status.", file=file_name))
        return None, errors
    if not isinstance(raw_status, str) or not raw_status.strip():
        errors.append(_issue("invalid_status", "status must be a non-empty string.", file=file_name))
        return None, errors
    status = raw_status.strip().lower()
    if status not in ALLOWED_STATUSES:
        errors.append(_issue("unknown_status", "status is not one of the documented lifecycle values.", file=file_name, status=raw_status))
    return status, errors


def _load_json_records(growth_dir: Path) -> Tuple[List[Tuple[Path, Any]], List[Dict[str, Any]]]:
    records: List[Tuple[Path, Any]] = []
    errors: List[Dict[str, Any]] = []
    for path in sorted(candidate for candidate in growth_dir.rglob("*.json") if candidate.is_file()):
        relative = path.relative_to(growth_dir).as_posix()
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(_issue("unreadable_json_record", "JSON record could not be read: %s" % exc, file=relative))
            continue
        except json.JSONDecodeError as exc:
            errors.append(_issue("malformed_json_record", "JSON record is malformed: %s" % exc.msg, file=relative, line=exc.lineno))
            continue
        if not isinstance(payload, Mapping):
            errors.append(_issue("invalid_json_record", "JSON records must be objects.", file=relative))
            continue
        records.append((path, payload))
    return records, errors


def validate_growth_records(growth_dir: Path) -> Dict[str, Any]:
    """Validate a ``.growth`` directory and return a complete deterministic summary."""

    growth_dir = Path(growth_dir)
    if not growth_dir.exists():
        return {
            "schema_version": "1.0",
            "valid": False,
            "growth_dir": str(growth_dir),
            "errors": [_issue("missing_growth_directory", "The .growth directory does not exist.")],
            "warnings": [],
            "records": [],
            "summary": {"records_scanned": 0, "records_valid": 0, "records_invalid": 0, "errors": 1},
            "invocation_error": True,
        }
    if not growth_dir.is_dir():
        return {
            "schema_version": "1.0",
            "valid": False,
            "growth_dir": str(growth_dir),
            "errors": [_issue("invalid_growth_directory", "The .growth target is not a directory.")],
            "warnings": [],
            "records": [],
            "summary": {"records_scanned": 0, "records_valid": 0, "records_invalid": 0, "errors": 1},
            "invocation_error": True,
        }

    records, errors = _load_json_records(growth_dir)
    warnings: List[Dict[str, Any]] = []
    evidence_dir = growth_dir / "evidence"
    if not evidence_dir.exists():
        errors.append(_issue("missing_evidence_directory", "The .growth/evidence directory does not exist."))
    elif not evidence_dir.is_dir():
        errors.append(_issue("invalid_evidence_directory", "The .growth/evidence target is not a directory."))
    if not (growth_dir / "state.json").is_file():
        errors.append(_issue("missing_state_record", "The .growth/state.json record does not exist."))

    known_evidence_ids: Dict[str, List[str]] = defaultdict(list)
    for path, record in records:
        relative = path.relative_to(growth_dir).as_posix()
        parts = Path(relative).parts
        evidence_id = record.get("id")
        if parts and parts[0] == "evidence" and isinstance(evidence_id, str) and evidence_id.strip():
            known_evidence_ids[evidence_id.strip()].append(relative)
    for evidence_id, locations in sorted(known_evidence_ids.items()):
        if len(locations) > 1:
            errors.append(_issue("duplicate_evidence_id", "Evidence id appears in more than one evidence record.", id=evidence_id, files=sorted(locations)))

    record_summaries: List[Dict[str, Any]] = []
    id_locations: Dict[str, List[str]] = defaultdict(list)
    linked_local = 0
    linked_external = 0
    completed_records = 0

    for path, record in records:
        relative = path.relative_to(growth_dir).as_posix()
        parts = Path(relative).parts
        operational = bool(parts and parts[0] in OPERATIONAL_DIRECTORIES)
        record_errors: List[Dict[str, Any]] = []
        status, status_errors = _record_status(record, relative, required=operational or relative == "state.json")
        record_errors.extend(status_errors)
        record_id = record.get("id", record.get("issue_id"))
        if operational:
            if not isinstance(record_id, str) or not record_id.strip():
                record_errors.append(_issue("missing_record_id", "Operational records need a non-empty id (or issue_id).", file=relative))
            else:
                id_locations[record_id.strip()].append(relative)

        reference_fields = (("evidence", "path"), ("evidence_links", "path"), ("evidence_ids", "id"), ("observation_evidence_ids", "id"))
        supplied_reference_fields = [(field, kind, record[field]) for field, kind in reference_fields if field in record]
        needs_evidence = operational and status in COMPLETION_STATUSES
        has_nonempty_evidence = any(isinstance(value, list) and value for _, _, value in supplied_reference_fields)
        if needs_evidence:
            completed_records += 1
            if not has_nonempty_evidence:
                record_errors.append(_issue("missing_required_evidence", "Completed/released/validated records need a non-empty evidence list.", file=relative, status=status))

        linked: List[Dict[str, Any]] = []
        for field, kind, references in supplied_reference_fields:
            if not isinstance(references, list):
                record_errors.append(_issue("invalid_evidence", "%s must be a list when supplied." % field, file=relative, field=field))
                continue
            for reference in references:
                if kind == "id":
                    linked_item, evidence_error = _validate_evidence_id(reference, known_evidence_ids)
                    if linked_item:
                        linked_item["field"] = field
                elif evidence_dir.is_dir():
                    linked_item, evidence_error = _validate_evidence_reference(reference, growth_dir, evidence_dir)
                    if linked_item:
                        linked_item["field"] = field
                else:
                    linked_item, evidence_error = None, _issue("missing_evidence_directory", "The .growth/evidence directory does not exist.")
                if evidence_error:
                    evidence_error["file"] = relative
                    record_errors.append(evidence_error)
                elif linked_item:
                    linked.append(linked_item)
                    if linked_item["kind"] in {"local", "evidence_id"}:
                        linked_local += 1
                    else:
                        linked_external += 1
                        warnings.append(_issue("external_evidence_link", "External evidence URL was linked but cannot be checked locally.", file=relative, reference=linked_item["reference"]))

        record_summaries.append(
            {
                "file": relative,
                "operational": operational,
                "id": record_id.strip() if isinstance(record_id, str) else None,
                "status": status,
                "evidence_links": linked,
                "errors": record_errors,
            }
        )
        errors.extend(record_errors)

    for record_id, locations in sorted(id_locations.items()):
        if len(locations) <= 1:
            continue
        duplicate = _issue("duplicate_record_id", "Operational record id appears in more than one file.", id=record_id, files=sorted(locations))
        errors.append(duplicate)
        for summary in record_summaries:
            if summary["id"] == record_id:
                summary["errors"].append(duplicate)

    # JSON parse failures do not have a summary entry, but count as invalid records.
    scanned_count = len(records) + sum(1 for error in errors if error["code"] in {"unreadable_json_record", "malformed_json_record", "invalid_json_record"})
    record_invalid_count = len({item["file"] for item in record_summaries if item["errors"]}) + len(
        {str(error.get("file")) for error in errors if error["code"] in {"unreadable_json_record", "malformed_json_record", "invalid_json_record"}}
    )
    record_valid_count = sum(1 for item in record_summaries if not item["errors"])
    return {
        "schema_version": "1.0",
        "valid": not errors,
        "growth_dir": str(growth_dir),
        "errors": errors,
        "warnings": warnings,
        "records": record_summaries,
        "summary": {
            "records_scanned": scanned_count,
            "records_valid": record_valid_count,
            "records_invalid": record_invalid_count,
            "operational_records": sum(1 for item in record_summaries if item["operational"]),
            "completed_operational_records": completed_records,
            "linked_local_evidence": linked_local,
            "external_evidence_links": linked_external,
            "errors": len(errors),
        },
        "invocation_error": False,
    }


def _write_json(report: Mapping[str, Any], output: Optional[str]) -> None:
    encoded = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        Path(output).write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate .growth record statuses, ids, and evidence linkage without modifying files.",
        epilog="Exit 0: valid; 1: validation failure; 2: missing/invalid target; 3: local/runtime failure.",
    )
    parser.add_argument("--root", default=".", help="Project root containing .growth (default: current directory)")
    parser.add_argument("--growth-dir", help="Optional explicit .growth directory path")
    parser.add_argument("--output", help="Write JSON validation report to this path instead of stdout")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    target = Path(args.growth_dir) if args.growth_dir else Path(args.root) / ".growth"
    try:
        report = validate_growth_records(target)
        _write_json(report, args.output)
    except OSError as exc:
        sys.stderr.write("validate_growth_records.py: %s\n" % exc)
        return 3
    if report["invocation_error"]:
        return 2
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
