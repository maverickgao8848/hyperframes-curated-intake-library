#!/usr/bin/env python3
"""Verify the single-authority catalog, aliases, Registry, and routing coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _registry import default_library


REGISTRY_KINDS = {"registry-block": "hyperframes:block", "registry-component": "hyperframes:component"}
DIRECTED_COUNTS = {"registry-block": 48, "registry-component": 123, "svg": 31, "lottie": 30}
DIRECTING_FIELDS = ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion")
DIRECTING_FAMILIES = {"data", "process", "structure", "compare", "interface", "concept", "emphasis", "evidence"}
DIRECTING_MOTIONS = {"entrance-only", "progressive", "stateful"}
PLACEHOLDERS = {"tbd", "todo", "placeholder", "n/a", "待定", "占位"}


def _valid_directing_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in PLACEHOLDERS


def validate_directed_revision(entries: list[dict], index: dict[str, dict], revision: int) -> tuple[list[str], dict]:
    errors: list[str] = []
    targets = [entry for entry in entries if entry.get("kind") in DIRECTED_COUNTS]
    actual_counts = {kind: sum(entry.get("kind") == kind for entry in targets) for kind in DIRECTED_COUNTS}
    for kind, expected in DIRECTED_COUNTS.items():
        if actual_counts[kind] != expected:
            errors.append(f"revision {revision} expected {expected} {kind} entries, found {actual_counts[kind]}")
    complete = 0
    for entry in targets:
        item_id = str(entry.get("id"))
        routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else None
        if routing is None:
            errors.append(f"revision {revision} directing metadata missing routing: {item_id}")
            continue
        item_errors = 0
        missing = [field for field in DIRECTING_FIELDS if field not in routing]
        if missing:
            errors.append(f"revision {revision} directing fields missing: {item_id}: {', '.join(missing)}")
            item_errors += 1
        if routing.get("family") not in DIRECTING_FAMILIES:
            errors.append(f"revision {revision} invalid family: {item_id}: {routing.get('family')!r}")
            item_errors += 1
        if routing.get("motion") not in DIRECTING_MOTIONS:
            errors.append(f"revision {revision} invalid motion: {item_id}: {routing.get('motion')!r}")
            item_errors += 1
        if not _valid_directing_text(routing.get("purpose")):
            errors.append(f"revision {revision} invalid purpose: {item_id}")
            item_errors += 1
        for field in ("useWhen", "avoidWhen", "expects"):
            values = routing.get(field)
            if (
                not isinstance(values, list)
                or not values
                or any(not _valid_directing_text(value) for value in values)
                or len(values) != len(set(values))
            ):
                errors.append(f"revision {revision} invalid {field}: {item_id}")
                item_errors += 1
        fallbacks = routing.get("fallbackIds", [])
        if not isinstance(fallbacks, list) or any(not isinstance(value, str) for value in fallbacks) or len(fallbacks) != len(set(fallbacks)):
            errors.append(f"revision {revision} invalid fallbackIds: {item_id}")
            item_errors += 1
        else:
            for fallback in fallbacks:
                target = index.get(fallback)
                if fallback == item_id:
                    errors.append(f"revision {revision} self fallback: {item_id}")
                    item_errors += 1
                elif target is None:
                    errors.append(f"revision {revision} dangling fallback: {item_id} -> {fallback}")
                    item_errors += 1
                elif target.get("status") != "ready":
                    errors.append(f"revision {revision} non-ready fallback: {item_id} -> {fallback}")
                    item_errors += 1
                elif target.get("kind") not in DIRECTED_COUNTS:
                    errors.append(f"revision {revision} fallback is not a directing peer: {item_id} -> {fallback}")
                    item_errors += 1
                else:
                    target_routing = target.get("routing") if isinstance(target.get("routing"), dict) else {}
                    if routing.get("family") in DIRECTING_FAMILIES and target_routing.get("family") != routing.get("family"):
                        errors.append(f"revision {revision} fallback family mismatch: {item_id} -> {fallback}")
                        item_errors += 1
        if item_errors == 0:
            complete += 1
    return errors, {
        "enforced": True,
        "expected": DIRECTED_COUNTS,
        "actual": actual_counts,
        "targetEntries": len(targets),
        "complete": complete,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json (default: skill assets/library)")
    args = parser.parse_args()
    library = args.library.resolve()
    catalog = json.loads((library / "catalog.json").read_text(encoding="utf-8"))
    registry = json.loads((library / "registry/registry.json").read_text(encoding="utf-8"))
    aliases = json.loads((library / "legacy-component-aliases.json").read_text(encoding="utf-8"))["aliases"]
    errors: list[str] = []
    entries = [entry for entry in catalog.get("entries", []) if isinstance(entry, dict)]
    ids = [entry.get("id") for entry in entries]
    if len(ids) != len(set(ids)):
        errors.append("catalog contains duplicate IDs")
    index = {entry["id"]: entry for entry in entries}
    installable = {(item["name"], item["type"]) for item in registry.get("items", [])}
    if len(installable) != len(registry.get("items", [])):
        errors.append("registry contains duplicate name/type pairs")
    ready_registry = [entry for entry in entries if entry.get("kind") in REGISTRY_KINDS and entry.get("status") == "ready"]
    for entry in ready_registry:
        name = entry.get("source", {}).get("name") or entry["id"].split(":", 1)[1]
        if (name, REGISTRY_KINDS[entry["kind"]]) not in installable:
            errors.append(f"ready entry is not installable: {entry['id']}")
        routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
        for fallback in routing.get("fallbackIds", []):
            if fallback not in index:
                errors.append(f"dangling fallback: {entry['id']} -> {fallback}")
            elif index[fallback].get("status") != "ready":
                errors.append(f"non-ready fallback: {entry['id']} -> {fallback}")
    if len(aliases) != 69:
        errors.append(f"expected 69 legacy aliases, found {len(aliases)}")
    alias_ready = 0
    for alias, record in aliases.items():
        target = record.get("registry_id")
        if record.get("result") == "no_recommendation":
            if alias != "broll-abstract.placeholder" or target is not None:
                errors.append(f"invalid no_recommendation alias: {alias}")
            continue
        alias_ready += 1
        if target not in index or index[target].get("status") != "ready":
            errors.append(f"alias targets missing/non-ready entry: {alias} -> {target}")
    if alias_ready != 68:
        errors.append(f"expected 68 ready aliases, found {alias_ready}")
    routed = [
        entry for entry in ready_registry
        if isinstance(entry.get("routing"), dict)
        and all(field in entry["routing"] for field in DIRECTING_FIELDS)
    ]
    coverage = len(routed) / len(ready_registry) if ready_registry else 0
    if coverage < 0.8:
        errors.append(f"routing coverage below 80%: {len(routed)}/{len(ready_registry)}")
    revision = catalog.get("revision")
    directing = {"enforced": False, "revision": revision, "targetEntries": 0, "complete": 0}
    if revision in {14, 15}:
        directing_errors, directing = validate_directed_revision(entries, index, revision)
        errors.extend(directing_errors)
    report = {
        "schemaVersion": "hyperframes-library-contract-report/v1",
        "ok": not errors,
        "summary": {"readyRegistry": len(ready_registry), "installable": len(installable), "legacyReady": alias_ready, "routed": len(routed), "coverage": round(coverage, 4), "directing": directing},
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
