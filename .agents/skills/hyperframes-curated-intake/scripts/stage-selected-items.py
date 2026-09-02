#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path

from _curation import catalog_index, copy_verified, entry_source_paths, load_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage only exact Registry items selected by the official HyperFrames plan.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--item", action="append", required=True, help="Exact catalog ID or Registry name.")
    parser.add_argument("--method", choices=("auto", "local", "official"), default="auto")
    parser.add_argument("--npx", default="npx")
    return parser.parse_args()


def resolve_item(index: dict[str, dict], value: str) -> dict:
    if value in index:
        return index[value]
    matches = [entry for entry in index.values() if entry.get("source", {}).get("name") == value]
    if len(matches) != 1:
        raise SystemExit(f"Registry item does not resolve uniquely: {value}")
    return matches[0]


def integration_markers(path: Path) -> list[dict[str, str]]:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    markers: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(kind: str, value: str) -> None:
        value = value.strip()
        key = (kind, value)
        if len(value) < 5 or key in seen or value in {"root", "clip", "frame", "container"}:
            return
        seen.add(key)
        markers.append({"kind": kind, "value": value})

    for value in re.findall(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", source):
        add("id", value)
    for group in re.findall(r"\bclass\s*=\s*['\"]([^'\"]+)['\"]", source):
        for value in group.split():
            add("class", value)
    for value in re.findall(r"(?<![\w-])\.([a-zA-Z][\w-]{4,})", source):
        add("class", value)
    for value in re.findall(r"(?<![\w-])(--[a-zA-Z][\w-]{4,})", source):
        add("css-var", value)
    return markers[:12]


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    library = args.library.resolve()
    curation = load_json(project / ".hyperframes" / "curation.json")
    build_plan = load_json(project / ".hyperframes" / "build-plan.json")
    catalog = load_json(library / "catalog.json")
    index = catalog_index(catalog)
    allowed = set(curation.get("palette", {}).get("blocks", []) + curation.get("palette", {}).get("components", []))
    entries = [resolve_item(index, value) for value in args.item]
    selected_ids = {
        str(item.get("id"))
        for scene in build_plan.get("scenes", [])
        if isinstance(scene, dict)
        for item in scene.get("integrations", [])
        if isinstance(item, dict) and item.get("state") == "selected-for-build"
    } | {
        str(item.get("catalogId"))
        for item in build_plan.get("transitions", [])
        if isinstance(item, dict) and item.get("state") == "selected-for-build" and item.get("catalogId")
    }
    outside_plan = sorted(str(entry["id"]) for entry in entries if entry["id"] not in selected_ids)
    if outside_plan:
        raise SystemExit("Registry items are outside the exact Build Plan selection: " + ", ".join(outside_plan))
    if curation.get("policy") == "approved-only":
        outside = sorted(str(entry["id"]) for entry in entries if entry["id"] not in allowed)
        if outside:
            raise SystemExit("approved-only blocks out-of-palette staging: " + ", ".join(outside))
    method = args.method
    if method == "auto":
        method = "official" if curation.get("registry", {}).get("mode") == "http" else "local"
    receipt_items: list[dict] = []
    for entry in entries:
        if entry.get("status") != "ready" or entry.get("kind") not in {"registry-block", "registry-component"}:
            raise SystemExit(f"Not a ready Registry Block/Component: {entry.get('id')}")
        name = str(entry.get("source", {}).get("name") or str(entry["id"]).split(":", 1)[1])
        if method == "official":
            command = [args.npx, "hyperframes", "add", name, "--dir", str(project), "--json", "--no-clipboard"]
            completed = subprocess.run(command, capture_output=True, text=True)
            if completed.returncode:
                raise SystemExit(f"Official hyperframes add failed for {name}:\n{completed.stderr or completed.stdout}")
            destination_root = project / ("compositions/library" if entry["kind"] == "registry-block" else "compositions/components/library")
            entry_source = (library / str(entry.get("source", {}).get("entry", ""))).resolve()
            copied_files: list[dict[str, str]] = []
            entry_path: str | None = None
            signature_markers: list[dict[str, str]] = []
            for source, target, _ in entry_source_paths(library, entry):
                installed = destination_root / target
                if installed.is_file():
                    copied_files.append({
                        "path": installed.relative_to(project).as_posix(),
                        "sha256": hashlib.sha256(installed.read_bytes()).hexdigest(),
                    })
                if source.resolve() == entry_source:
                    entry_path = installed.relative_to(project).as_posix()
                    signature_markers = integration_markers(source)
            receipt_items.append({
                "id": entry["id"], "name": name, "kind": entry["kind"], "method": "official",
                "integration": entry.get("integration", {}), "entryPath": entry_path,
                "signatureMarkers": signature_markers, "files": copied_files, "command": command,
            })
            continue
        destination_root = project / ("compositions/library" if entry["kind"] == "registry-block" else "compositions/components/library")
        copied_files = []
        entry_source = (library / str(entry.get("source", {}).get("entry", ""))).resolve()
        entry_path: str | None = None
        signature_markers: list[dict[str, str]] = []
        for source, target, expected in entry_source_paths(library, entry):
            target_path = destination_root / target
            copied_hash = copy_verified(source, target_path, expected)
            copied_files.append({"path": target_path.relative_to(project).as_posix(), "sha256": copied_hash})
            if source.resolve() == entry_source:
                entry_path = target_path.relative_to(project).as_posix()
                signature_markers = integration_markers(source)
        if not copied_files:
            raise SystemExit(f"No stageable source files for {entry['id']}")
        receipt_items.append({
            "id": entry["id"], "name": name, "kind": entry["kind"], "method": "local",
            "integration": entry.get("integration", {}), "entryPath": entry_path,
            "signatureMarkers": signature_markers, "files": copied_files,
        })
    receipt = {
        "schemaVersion": "hyperframes-curated-staging-receipt/v1",
        "policy": curation.get("policy"),
        "items": sorted(receipt_items, key=lambda item: item["id"]),
    }
    output = project / ".hyperframes" / "staging-receipt.json"
    write_json(output, receipt)
    print(f"Staged {len(receipt_items)} exact item(s); wrote {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
