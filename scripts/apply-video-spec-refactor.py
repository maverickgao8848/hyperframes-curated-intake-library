#!/usr/bin/env python3
"""Inspect a catalog and report revision 14 directing-metadata readiness."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from _registry import default_library


DIRECTING_FIELDS = ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion")
PRESERVED_ROUTING_FIELDS = (*DIRECTING_FIELDS, "fallbackIds")
DIRECTING_FAMILIES = {"data", "process", "structure", "compare", "interface", "concept", "emphasis", "evidence"}
REVISION_14_KINDS = {"registry-block", "registry-component", "svg", "lottie"}


def build_revision14_report(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a review aid without mutating entries or normalizing curated routing."""
    reports: list[dict[str, Any]] = []
    for entry in sorted(entries, key=lambda item: str(item.get("id", ""))):
        if entry.get("kind") not in REVISION_14_KINDS:
            continue
        routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
        missing = [field for field in DIRECTING_FIELDS if field not in routing]
        conflicts: list[dict[str, Any]] = []
        family = routing.get("family")
        if family is not None and family not in DIRECTING_FAMILIES:
            conflicts.append({
                "field": "family",
                "value": deepcopy(family),
                "confidence": "low",
                "reason": "legacy family is outside the revision 14 enum; manual curation required",
            })
        suggestions: dict[str, Any] = {}
        manual = list(missing)
        reports.append({
            "id": entry.get("id"),
            "kind": entry.get("kind"),
            "preserved": {
                field: deepcopy(routing[field])
                for field in PRESERVED_ROUTING_FIELDS
                if field in routing
            },
            "suggestions": suggestions,
            "manualRequired": manual,
            "conflicts": conflicts,
            "ready": not missing and not conflicts,
        })
    return {
        "schemaVersion": "hyperframes-library-revision14-proposal/v1",
        "targetRevision": 14,
        "authoritative": False,
        "note": "Suggestions are evidence-bounded review aids; catalog routing remains the sole authority.",
        "entries": reports,
        "summary": {
            "targetEntries": len(reports),
            "ready": sum(1 for item in reports if item["ready"]),
            "needsManual": sum(1 for item in reports if item["manualRequired"] or item["conflicts"]),
            "conflicts": sum(len(item["conflicts"]) for item in reports),
        },
    }


def _inside(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--library",
        type=Path,
        default=default_library(),
        help="Read-only library containing catalog.json (default: skill assets/library)",
    )
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument(
        "--report",
        type=Path,
        help="Write the non-authoritative proposal to an explicit path outside the input library",
    )
    operation.add_argument(
        "--check",
        action="store_true",
        help="Print revision 14 readiness without writing any file",
    )
    args = parser.parse_args()

    library = args.library.resolve()
    catalog_path = library / "catalog.json"
    if not catalog_path.is_file():
        parser.error(f"catalog not found: {catalog_path}")
    report_path = args.report.resolve() if args.report else None
    if report_path is not None:
        if _inside(report_path, library):
            parser.error("--report must be outside the input library")
        if not report_path.parent.is_dir():
            parser.error("--report parent directory must already exist")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    proposal = build_revision14_report(
        [entry for entry in catalog.get("entries", []) if isinstance(entry, dict)]
    )
    rendered = json.dumps(proposal, ensure_ascii=False, indent=2) + "\n"
    if report_path is not None:
        report_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if proposal["summary"]["needsManual"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
