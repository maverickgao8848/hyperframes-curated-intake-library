#!/usr/bin/env python3
"""Read-only validation and inventory report for a curated HyperFrames library."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from _registry import (
    CATALOG_SCHEMA,
    REGISTRY_KINDS,
    default_library,
    entry_name,
    load_catalog,
    safe_relative,
    sha256_file,
    source_files,
    write_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json")
    parser.add_argument("--output", type=Path, help="Write the JSON report here instead of stdout")
    return parser


def inventory(library: Path) -> tuple[dict[str, Any], int]:
    library = library.resolve()
    catalog_path, catalog = load_catalog(library)
    issues: list[dict[str, Any]] = []

    def issue(severity: str, code: str, message: str, entry_id: str | None = None) -> None:
        value: dict[str, Any] = {"severity": severity, "code": code, "message": message}
        if entry_id is not None:
            value["id"] = entry_id
        issues.append(value)

    schema_valid = catalog.get("schemaVersion") == CATALOG_SCHEMA
    if not schema_valid:
        issue("error", "catalog-schema", f"expected {CATALOG_SCHEMA}, got {catalog.get('schemaVersion')!r}")
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        issue("error", "catalog-entries", "catalog entries must be an array")
        entries = []

    registry_root = library / "registry"
    registry_manifest_path = registry_root / "registry.json"
    registry_manifest: dict[str, Any] | None = None
    registry_entries: set[tuple[str, str]] = set()
    if registry_manifest_path.is_file():
        try:
            loaded = json.loads(registry_manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                registry_manifest = loaded
                for item in loaded.get("items", []):
                    if isinstance(item, dict) and isinstance(item.get("name"), str) and isinstance(item.get("type"), str):
                        registry_entries.add((item["name"], item["type"]))
            else:
                issue("error", "registry-manifest", "registry.json must contain a JSON object")
        except (OSError, json.JSONDecodeError) as exc:
            issue("error", "registry-manifest", f"cannot read registry.json: {exc}")

    entry_reports: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            issue("error", "entry-shape", "catalog entry must be an object")
            continue
        entry_id = str(entry.get("id", ""))
        files_report: list[dict[str, Any]] = []
        for record in source_files(entry):
            record_report: dict[str, Any] = {"path": record.get("path"), "exists": False, "hashMatches": False}
            try:
                relative = safe_relative(str(record.get("path", "")), "source path")
                path = library / Path(*relative.parts)
                record_report["exists"] = path.is_file()
                if path.is_file():
                    actual = sha256_file(path)
                    record_report["sha256"] = actual
                    expected = record.get("sha256")
                    record_report["hashMatches"] = isinstance(expected, str) and actual == expected.lower()
                    if not record_report["hashMatches"]:
                        issue("error", "source-hash", f"hash mismatch: {relative.as_posix()}", entry_id)
                else:
                    issue("error", "source-missing", f"missing source: {relative.as_posix()}", entry_id)
            except ValueError as exc:
                issue("error", "source-path", str(exc), entry_id)
            files_report.append(record_report)

        preview_value = entry.get("preview")
        preview_exists = False
        if isinstance(preview_value, str):
            try:
                preview_relative = safe_relative(preview_value, "preview path")
                preview_exists = (library / Path(*preview_relative.parts)).is_file()
            except ValueError:
                preview_exists = False
        if entry.get("status") == "ready" and not preview_exists:
            issue("warning", "preview-missing", f"ready entry preview is missing: {preview_value!r}", entry_id)

        mapping: dict[str, Any] | None = None
        if entry.get("kind") in REGISTRY_KINDS:
            category, registry_type = REGISTRY_KINDS[entry["kind"]]
            name = entry_name(entry)
            mapping = {
                "eligible": entry.get("status") == "ready" and name is not None,
                "type": registry_type,
                "itemPath": f"{category}/{name}/registry-item.json" if name else None,
            }
            view_path = registry_root / mapping["itemPath"] if mapping["itemPath"] else None
            mapping["exists"] = bool(view_path and view_path.is_file())
            mapping["manifestListed"] = bool(name and (name, registry_type) in registry_entries)
            mapping["valid"] = False
            if view_path and view_path.is_file():
                try:
                    registry_item = json.loads(view_path.read_text(encoding="utf-8"))
                    mapping["valid"] = bool(
                        isinstance(registry_item, dict)
                        and registry_item.get("name") == name
                        and registry_item.get("type") == registry_type
                        and isinstance(registry_item.get("files"), list)
                        and registry_item["files"]
                    )
                    if mapping["manifestListed"] and not mapping["valid"]:
                        issue("error", "registry-item", f"invalid Registry item: {mapping['itemPath']}", entry_id)
                except (OSError, json.JSONDecodeError) as exc:
                    issue("error", "registry-item", f"cannot read {mapping['itemPath']}: {exc}", entry_id)

        entry_reports.append(
            {
                "id": entry.get("id"),
                "kind": entry.get("kind"),
                "status": entry.get("status"),
                "sourceFiles": files_report,
                "preview": {"path": preview_value, "exists": preview_exists},
                "registry": mapping,
            }
        )

    frames: list[dict[str, Any]] = []
    frames_root = library / "frames"
    if frames_root.is_dir():
        for frame_path in sorted(frames_root.glob("*/FRAME.md"), key=lambda path: path.parent.name):
            frames.append(
                {
                    "preset": frame_path.parent.name,
                    "path": frame_path.relative_to(library).as_posix(),
                    "sha256": sha256_file(frame_path),
                }
            )

    statuses = Counter(str(entry.get("status")) for entry in entries if isinstance(entry, dict))
    kinds = Counter(str(entry.get("kind")) for entry in entries if isinstance(entry, dict))
    mappings = [item["registry"] for item in entry_reports if item["registry"] is not None]
    report = {
        "schemaVersion": "hyperframes-curated-library-inventory/v1",
        "library": ".",
        "catalog": {
            "path": catalog_path.relative_to(library).as_posix(),
            "schemaVersion": catalog.get("schemaVersion"),
            "schemaValid": schema_valid,
            "revision": catalog.get("revision"),
            "sha256": sha256_file(catalog_path),
        },
        "registry": {
            "path": registry_manifest_path.relative_to(library).as_posix(),
            "exists": registry_manifest_path.is_file(),
            "name": registry_manifest.get("name") if registry_manifest else None,
            "items": len(registry_entries),
        },
        "summary": {
            "entries": len(entry_reports),
            "kinds": dict(sorted(kinds.items())),
            "statuses": dict(sorted(statuses.items())),
            "registryEligible": sum(bool(item["eligible"]) for item in mappings),
            "registryMapped": sum(bool(item["exists"] and item["manifestListed"]) for item in mappings),
            "registryValid": sum(
                bool(item["exists"] and item["manifestListed"] and item["valid"]) for item in mappings
            ),
            "frames": len(frames),
            "errors": sum(item["severity"] == "error" for item in issues),
            "warnings": sum(item["severity"] == "warning" for item in issues),
        },
        "frames": frames,
        "entries": entry_reports,
        "issues": sorted(issues, key=lambda item: (item["severity"], item["code"], item.get("id", ""))),
    }
    return report, 1 if report["summary"]["errors"] else 0


def main() -> int:
    args = _parser().parse_args()
    try:
        report, code = inventory(args.library)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    if args.output:
        write_json(args.output, report)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
