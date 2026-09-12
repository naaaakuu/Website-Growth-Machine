#!/usr/bin/env python3
"""Create a minimal, non-destructive ``.growth`` state directory.

Existing files are never overwritten, deleted, or renamed.  For each foundational
record the initializer first looks for a template (``--template-dir``, then a
project ``templates`` directory, then this package's ``templates`` directory).
It accepts files directly in that directory, under ``.growth``/``growth``, or with
the ``.template`` infix.  If no template exists, a small valid fallback record is
created instead.

Exit codes: 0 for a completed idempotent initialization, 2 for invalid target
arguments, and 3 for a local filesystem/runtime failure.  JSON is written to
stdout unless ``--output`` is supplied.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


JSON_FALLBACKS: Mapping[str, Mapping[str, Any]] = {
    "state.json": {
        "schema_version": "1.0",
        "status": "initialized",
        "current_mode": "DISCOVER",
        "record_paths": {
            "brief": "brief.json",
            "objectives": "objectives.json",
            "metric_tree": "metric-tree.json",
            "opportunity_map": "opportunity-map.json",
        },
    },
    "brief.json": {
        "schema_version": "1.0",
        "status": "draft",
        "business_context": {},
        "audience": [],
        "constraints": [],
        "unknowns": [],
    },
    "objectives.json": {"schema_version": "1.0", "status": "draft", "objectives": []},
    "metric-tree.json": {"schema_version": "1.0", "status": "draft", "north_star_metric": None, "metrics": []},
    "protected-assets.json": {"schema_version": "1.0", "assets": []},
    "opportunity-map.json": {"schema_version": "1.0", "status": "draft", "opportunities": []},
    "backlog.json": {"schema_version": "1.0", "items": []},
    "content-moat.json": {"schema_version": "1.0", "assets": []},
    "source-register.json": {"schema_version": "1.0", "sources": []},
    "risk-coverage.json": {"schema_version": "1.0", "coverage_units": []},
    "quality-policy.json": {
        "schema_version": "1.0",
        "status": "DRAFT",
        "required_cases": [],
        "min_runs": None,
        "score_rules": {},
        "metric_rules": {},
    },
    "evidence/evidence-record.template.json": {"schema_version": "1.0", "id": "EV-TEMPLATE", "claim_status": "UNKNOWN", "raw_evidence_paths": []},
    "decisions/decision-record.template.json": {"schema_version": "1.0", "id": "DEC-TEMPLATE", "decision_status": "PROPOSED", "evidence_ids": []},
    "experiments/experiment.template.json": {"schema_version": "1.0", "id": "EXP-TEMPLATE", "status": "DRAFT", "observation_evidence_ids": []},
    "serp/serp-opportunity.template.json": {"schema_version": "1.0", "id": "SERP-TEMPLATE", "claim_status": "UNKNOWN", "evidence_ids": []},
    "learnings/learning-record.template.json": {"schema_version": "1.0", "id": "LRN-TEMPLATE", "evidence_ids": []},
}

TEXT_FALLBACKS: Mapping[str, str] = {
    "capabilities.md": "# Growth capabilities\n\nNo capabilities have been recorded yet.\n",
    "learnings.md": "# Growth learnings\n\nNo learnings have been recorded yet.\n",
    "decisions.md": "# Growth decisions\n\nNo decisions have been recorded yet.\n",
    "audits/audit-report.template.md": "# Audit report template\n\nNo audit report has been recorded yet.\n",
    "releases/release-report.template.md": "# Release report template\n\nNo release report has been recorded yet.\n",
}

RECORD_NAMES = tuple(list(JSON_FALLBACKS) + list(TEXT_FALLBACKS))
SUBDIRECTORIES = ("audits", "experiments", "releases", "evidence", "serp", "decisions", "learnings")

# The package ships canonical template names rather than asking each project to
# invent its own.  Destination paths intentionally separate reusable templates
# (for example an experiment record) from actual project records.
TEMPLATE_NAMES: Mapping[str, Tuple[str, ...]] = {
    "state.json": ("state.template.json", "state.json"),
    "brief.json": ("brief.template.json", "brief.json"),
    "objectives.json": ("objectives.template.json", "objectives.json"),
    "metric-tree.json": ("metric-tree.template.json", "metric-tree.json"),
    "protected-assets.json": ("protected-assets.template.json", "protected-assets.json"),
    "opportunity-map.json": ("opportunity-map.template.json", "opportunity-map.json"),
    "backlog.json": ("backlog.template.json", "backlog.json"),
    "content-moat.json": ("content-moat.template.json", "content-moat.json"),
    "source-register.json": ("source-register.template.json", "source-register.json"),
    "risk-coverage.json": ("risk-coverage.template.json", "risk-coverage.json"),
    "quality-policy.json": ("quality-policy.template.json", "quality-policy.json"),
    "evidence/evidence-record.template.json": ("evidence-record.template.json",),
    "decisions/decision-record.template.json": ("decision-record.template.json",),
    "experiments/experiment.template.json": ("experiment.template.json",),
    "serp/serp-opportunity.template.json": ("serp-opportunity.template.json",),
    "learnings/learning-record.template.json": ("learning-record.template.json",),
    "audits/audit-report.template.md": ("audit-report.template.md",),
    "releases/release-report.template.md": ("release-report.template.md",),
    "capabilities.md": ("capabilities.template.md", "capabilities.md"),
    "decisions.md": ("decisions.template.md", "decisions.md"),
    "learnings.md": ("learnings.template.md", "learnings.md"),
}


def _fallback_bytes(name: str) -> bytes:
    if name in JSON_FALLBACKS:
        return (json.dumps(JSON_FALLBACKS[name], indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    return TEXT_FALLBACKS[name].encode("utf-8")


def _dedupe_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    result: List[Path] = []
    for path in paths:
        try:
            key = str(path.resolve())
        except OSError:
            key = str(path.absolute())
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def _template_roots(project_root: Path, explicit: Optional[Path]) -> List[Path]:
    """Return locations in precedence order without assuming a machine path."""

    package_templates = Path(__file__).resolve().parent.parent / "templates"
    values: List[Path] = []
    if explicit is not None:
        values.append(explicit)
    values.extend([project_root / "templates", package_templates])
    return _dedupe_paths(values)


def _find_template(names: Iterable[str], roots: Iterable[Path]) -> Optional[Path]:
    """Find one named template directly or in a conventional growth subtree."""

    for root in roots:
        for name in names:
            path = Path(name)
            alternate = "%s.template%s" % (path.stem, path.suffix)
            for candidate in (
                root / path,
                root / ".growth" / path,
                root / "growth" / path,
                root / alternate,
                root / ".growth" / alternate,
                root / "growth" / alternate,
            ):
                if candidate.is_file():
                    return candidate
    return None


def _write_new(path: Path, content: bytes) -> bool:
    """Atomically-ish create a file; false means another process already has it."""

    try:
        with path.open("xb") as handle:
            handle.write(content)
        return True
    except FileExistsError:
        return False


def initialize_growth_state(
    root: Path,
    *,
    growth_dir: Optional[Path] = None,
    template_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Initialize records below ``root/.growth`` without replacing user content."""

    root = Path(root)
    target = Path(growth_dir) if growth_dir is not None else root / ".growth"
    if root.exists() and not root.is_dir():
        raise ValueError("root must be a directory")
    if target.exists() and not target.is_dir():
        raise ValueError("growth_dir exists but is not a directory")
    if template_dir is not None and template_dir.exists() and not template_dir.is_dir():
        raise ValueError("template_dir exists but is not a directory")

    target_preexisting = target.exists()
    target.mkdir(parents=True, exist_ok=True)
    directories_created: List[str] = []
    required_directories = set(SUBDIRECTORIES)
    required_directories.update(str(Path(name).parent) for name in RECORD_NAMES if str(Path(name).parent) != ".")
    for name in sorted(required_directories):
        directory = target / name
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            directories_created.append(name)

    roots = _template_roots(root, template_dir)
    created: List[Dict[str, str]] = []
    existing: List[str] = []
    template_warnings: List[Dict[str, str]] = []
    for name in RECORD_NAMES:
        destination = target / name
        if destination.exists():
            existing.append(name)
            continue
        source = _find_template(TEMPLATE_NAMES.get(name, (name,)), roots)
        content: bytes
        source_kind = "fallback"
        if source is not None:
            try:
                content = source.read_bytes()
                source_kind = "template"
            except OSError as exc:
                template_warnings.append({"record": name, "template": str(source), "message": str(exc)})
                content = _fallback_bytes(name)
        else:
            content = _fallback_bytes(name)
        if _write_new(destination, content):
            item = {"path": name, "source": source_kind}
            if source is not None and source_kind == "template":
                item["template"] = str(source)
            created.append(item)
        else:
            # A concurrent initializer created it between our existence check and x-mode open.
            existing.append(name)

    return {
        "schema_version": "1.0",
        "initialized": True,
        "growth_dir": str(target),
        "growth_dir_preexisting": target_preexisting,
        "directories_created": directories_created,
        "created": created,
        "existing": sorted(existing),
        "template_roots_considered": [str(path) for path in roots if path.exists()],
        "template_warnings": template_warnings,
        "summary": {"created_records": len(created), "existing_records": len(existing)},
    }


def _write_json(report: Mapping[str, Any], output: Optional[str]) -> None:
    encoded = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        Path(output).write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Non-destructively initialize a .growth directory from templates or valid fallback records.",
        epilog="Existing records are never overwritten. Exit 0: initialized; 2: invalid arguments; 3: filesystem/runtime failure.",
    )
    parser.add_argument("--root", default=".", help="Project root; default creates .growth below the current directory")
    parser.add_argument("--growth-dir", help="Optional explicit .growth directory path")
    parser.add_argument("--template-dir", help="Optional preferred template directory")
    parser.add_argument("--output", help="Write JSON result to this path instead of stdout")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = initialize_growth_state(
            Path(args.root),
            growth_dir=Path(args.growth_dir) if args.growth_dir else None,
            template_dir=Path(args.template_dir) if args.template_dir else None,
        )
        _write_json(report, args.output)
        return 0
    except ValueError as exc:
        sys.stderr.write("init_growth_state.py: %s\n" % exc)
        return 2
    except OSError as exc:
        sys.stderr.write("init_growth_state.py: %s\n" % exc)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
