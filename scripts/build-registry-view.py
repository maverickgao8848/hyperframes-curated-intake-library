#!/usr/bin/env python3
"""Build a deterministic official HyperFrames custom Registry view."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from _registry import (
    CATALOG_SCHEMA,
    REGISTRY_ITEM_SCHEMA,
    REGISTRY_KINDS,
    REGISTRY_SCHEMA,
    block_geometry,
    default_library,
    entry_name,
    load_catalog,
    safe_relative,
    sha256_file,
    source_files,
    write_json,
)


DIRECTING_FIELDS = ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion", "fallbackIds")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json")
    parser.add_argument("--output", type=Path, help="Registry output directory (default: <library>/registry)")
    parser.add_argument("--name", default="hyperframes-curated", help="Registry manifest name")
    parser.add_argument("--homepage", default="https://hyperframes.heygen.com", help="Registry homepage URL")
    parser.add_argument("--report", type=Path, help="Optional JSON build report path")
    return parser


def _copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and sha256_file(destination) == sha256_file(source):
        return
    shutil.copyfile(source, destination)


def _file_mapping(kind: str, name: str, file_record: dict[str, Any], is_entry: bool) -> dict[str, str]:
    original_target = safe_relative(str(file_record.get("target", "")), "source target")
    suffix = Path(original_target.name).suffix.lower()
    if kind == "registry-block" and is_entry:
        target = f"compositions/{name}{suffix or '.html'}"
        file_type = "hyperframes:composition"
        bundle_path = original_target.name
    elif kind == "registry-component":
        relative = original_target
        if relative.parts and relative.parts[0] == "components":
            relative = type(relative)(*relative.parts[1:])
        target = f"compositions/components/{relative.as_posix()}"
        file_type = "hyperframes:snippet"
        bundle_path = relative.as_posix()
    else:
        target = original_target.as_posix()
        if not target.startswith("assets/"):
            target = f"assets/{target}"
        file_type = "hyperframes:asset"
        bundle_path = target
    return {"path": bundle_path, "target": target, "type": file_type}


def _map_entry(library: Path, output: Path, entry: dict[str, Any]) -> tuple[dict[str, str] | None, list[str]]:
    reasons: list[str] = []
    kind = entry.get("kind")
    category, registry_type = REGISTRY_KINDS[kind]
    name = entry_name(entry)
    if name is None:
        return None, ["missing or invalid kebab-case source.name"]
    if entry.get("status") != "ready":
        return None, [f"status is {entry.get('status')!r}, not 'ready'"]
    records = source_files(entry)
    source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
    source_entry = source.get("entry")
    if not records:
        reasons.append("source bundle has no files")
    if not isinstance(source_entry, str):
        reasons.append("source bundle has no entry path")

    resolved: list[tuple[dict[str, Any], Path, bool]] = []
    for record in records:
        try:
            relative = safe_relative(str(record.get("path", "")), "source path")
            path = library / Path(*relative.parts)
        except ValueError as exc:
            reasons.append(str(exc))
            continue
        is_entry = isinstance(source_entry, str) and relative.as_posix() == source_entry.replace("\\", "/")
        if not path.is_file():
            reasons.append(f"source file does not exist: {relative.as_posix()}")
            continue
        expected = record.get("sha256")
        actual = sha256_file(path)
        if not isinstance(expected, str) or actual != expected.lower():
            reasons.append(f"source hash mismatch: {relative.as_posix()}")
            continue
        resolved.append((record, path, is_entry))
    if source_entry and not any(item[2] for item in resolved):
        reasons.append(f"source entry is absent from verified files: {source_entry}")

    dimensions = duration = None
    if kind == "registry-block" and not reasons:
        entry_path = next(path for _, path, is_entry in resolved if is_entry)
        dimensions, duration, geometry_reasons = block_geometry(
            entry_path.read_text(encoding="utf-8"),
            aspect_fit=entry.get("aspectSupport") if isinstance(entry.get("aspectSupport"), list) else None,
            duration_hint=entry.get("duration"),
        )
        reasons.extend(geometry_reasons)
    if reasons:
        return None, sorted(set(reasons))

    item_dir = output / category / name
    files: list[dict[str, str]] = []
    used_paths: set[str] = set()
    for record, source_path, is_entry in resolved:
        try:
            mapping = _file_mapping(kind, name, record, is_entry)
            safe_relative(mapping["path"], "registry file path")
            safe_relative(mapping["target"], "registry file target")
        except ValueError as exc:
            return None, [str(exc)]
        if mapping["path"] in used_paths:
            return None, [f"two source files map to the same Registry path: {mapping['path']}"]
        used_paths.add(mapping["path"])
        _copy(source_path, item_dir / Path(*safe_relative(mapping["path"], "registry file path").parts))
        files.append(mapping)

    metadata: dict[str, Any] = {
        "$schema": REGISTRY_ITEM_SCHEMA,
        "name": name,
        "type": registry_type,
        "title": entry.get("title"),
        "description": entry.get("description"),
        "tags": sorted(set(entry.get("tags") or [])),
    }
    if not isinstance(metadata["title"], str) or not metadata["title"].strip():
        return None, ["title is required"]
    if not isinstance(metadata["description"], str) or not metadata["description"].strip():
        return None, ["description is required"]
    if not all(isinstance(tag, str) and tag for tag in metadata["tags"]):
        return None, ["tags must contain non-empty strings"]
    if kind == "registry-block":
        metadata["dimensions"] = dimensions
        metadata["duration"] = duration
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
    directing = {field: deepcopy(routing[field]) for field in DIRECTING_FIELDS if field in routing}
    if directing:
        metadata["routing"] = directing
    metadata["files"] = sorted(files, key=lambda item: (item["path"], item["target"], item["type"]))
    write_json(item_dir / "registry-item.json", metadata)
    return {"name": name, "type": registry_type}, []


def build(library: Path, output: Path, name: str, homepage: str) -> tuple[dict[str, Any], int]:
    library = library.resolve()
    output = output.resolve()
    catalog_path, catalog = load_catalog(library)
    report: dict[str, Any] = {
        "schemaVersion": "hyperframes-curated-registry-build/v1",
        "catalog": catalog_path.relative_to(library).as_posix(),
        "output": output.relative_to(library).as_posix() if output == library or library in output.parents else str(output),
        "mapped": [],
        "unmapped": [],
        "ignored": [],
    }
    if catalog.get("schemaVersion") != CATALOG_SCHEMA or not isinstance(catalog.get("entries"), list):
        report["unmapped"].append({"id": None, "reasons": [f"catalog schema must be {CATALOG_SCHEMA}"]})
        return report, 2

    seen_names: set[str] = set()
    manifest_items: list[dict[str, str]] = []
    candidates = sorted(
        (entry for entry in catalog["entries"] if isinstance(entry, dict) and entry.get("kind") in REGISTRY_KINDS),
        key=lambda entry: str(entry.get("id", "")),
    )
    for entry in candidates:
        mapped, reasons = _map_entry(library, output, entry)
        if mapped and mapped["name"] in seen_names:
            mapped, reasons = None, [f"duplicate Registry name: {mapped['name']}"]
        if mapped:
            seen_names.add(mapped["name"])
            manifest_items.append(mapped)
            report["mapped"].append({"id": entry.get("id"), **mapped})
        else:
            report["unmapped"].append({"id": entry.get("id"), "reasons": reasons})

    for entry in catalog["entries"]:
        if isinstance(entry, dict) and entry.get("kind") not in REGISTRY_KINDS:
            report["ignored"].append({"id": entry.get("id"), "kind": entry.get("kind")})
    manifest = {
        "$schema": REGISTRY_SCHEMA,
        "name": name,
        "homepage": homepage,
        "items": sorted(manifest_items, key=lambda item: (item["type"], item["name"])),
    }
    write_json(output / "registry.json", manifest)
    report["summary"] = {
        "mapped": len(report["mapped"]),
        "unmapped": len(report["unmapped"]),
        "ignored": len(report["ignored"]),
    }
    return report, 0


def main() -> int:
    args = _parser().parse_args()
    output = args.output or (args.library / "registry")
    try:
        report, code = build(args.library, output, args.name, args.homepage)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    if args.report:
        write_json(args.report, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
