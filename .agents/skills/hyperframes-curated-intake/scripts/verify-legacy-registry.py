#!/usr/bin/env python3
"""Verify the 68 promoted legacy components through their Registry artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from _registry import default_library


IMPORT = re.compile(r'''from\s+["']([^"']+)["']''')
TIMELINE = re.compile(r"\.timeline\s*\(\s*\{([^}]*)\}")
FORBIDDEN = ("Math.random", "Date.now", "setInterval(", "requestAnimationFrame(")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency_closure(entry: Path, seen: set[Path] | None = None) -> list[Path]:
    seen = seen or set()
    entry = entry.resolve()
    if entry in seen:
        return []
    seen.add(entry)
    result = [entry]
    text = entry.read_text(encoding="utf-8")
    for specifier in IMPORT.findall(text):
        if not specifier.startswith("."):
            continue
        dependency = entry.parent / specifier
        if not dependency.suffix:
            dependency = dependency.with_suffix(".js")
        if dependency.is_file():
            result.extend(dependency_closure(dependency, seen))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json (default: skill assets/library)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    library = args.library.resolve()
    catalog = json.loads((library / "catalog.json").read_text(encoding="utf-8"))
    aliases = json.loads((library / "legacy-component-aliases.json").read_text(encoding="utf-8"))["aliases"]
    index = {entry["id"]: entry for entry in catalog["entries"]}
    results, errors = [], []
    for alias, alias_record in sorted(aliases.items()):
        target = alias_record.get("registry_id")
        if not target:
            continue
        entry = index.get(target)
        item_errors: list[str] = []
        name = target.split(":", 1)[1]
        item_path = library / f"registry/components/{name}/registry-item.json"
        if not entry or entry.get("status") != "ready":
            item_errors.append("canonical catalog target is not ready")
        if not item_path.is_file():
            item_errors.append("Registry item is missing")
            item = {"files": []}
        else:
            item = json.loads(item_path.read_text(encoding="utf-8"))
            if item.get("name") != name or item.get("type") != "hyperframes:component":
                item_errors.append("Registry item identity mismatch")
        entry_path = library / entry["source"]["entry"] if entry else library / "missing"
        closure = dependency_closure(entry_path) if entry_path.is_file() else []
        combined = "\n".join(path.read_text(encoding="utf-8") for path in closure)
        if not re.search(r"export\s+const\s+meta\b", combined):
            item_errors.append("meta export missing")
        if not re.search(r"export\s+function\s+mount\b", combined):
            item_errors.append("mount export missing")
        if not re.search(r"\bseek\s*\(", combined):
            item_errors.append("seek contract missing from dependency closure")
        for path in closure:
            source = path.read_text(encoding="utf-8")
            if any(token in source for token in FORBIDDEN):
                item_errors.append(f"nondeterministic API in {path.name}")
            for match in TIMELINE.finditer(source):
                if not re.search(r"\bpaused\s*:\s*true\b", match.group(1)):
                    item_errors.append(f"unpaused timeline in {path.name}")
        for record in item.get("files", []):
            installed = item_path.parent / record["path"]
            source = library / "components" / Path(record["path"]).name
            if "/" in record["path"].replace("\\", "/"):
                source = library / "components" / record["path"]
            if not installed.is_file():
                item_errors.append(f"Registry payload missing: {record['path']}")
            elif source.is_file() and sha256(installed) != sha256(source):
                item_errors.append(f"Registry payload drift: {record['path']}")
        errors.extend(f"{alias}: {message}" for message in item_errors)
        results.append({"legacyId": alias, "registryId": target, "dependencyFiles": len(closure), "ok": not item_errors})
    report = {
        "schemaVersion": "hyperframes-legacy-registry-verification/v1",
        "ok": not errors and len(results) == 68,
        "summary": {
            "legacyReady": len(results),
            "registryArtifacts": sum(result["ok"] for result in results),
            "mountExports": sum(result["ok"] for result in results),
            "seekSafeClosures": sum(result["ok"] for result in results),
        },
        "checks": ["registry-payload", "meta-export", "mount-export", "seek-contract", "paused-timelines", "no-render-time-nondeterminism"],
        "results": results,
        "errors": errors,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.resolve().write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
