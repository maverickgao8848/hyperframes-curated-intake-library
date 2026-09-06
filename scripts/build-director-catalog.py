#!/usr/bin/env python3
"""Build director-catalog.json from checked-in authoritative manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from _registry import default_library

from _capabilities import enrich


SYSTEMS = (
    ("camera-rig", "L1-camera", "source-preserve"),
    ("depth-parallax", "L5-supporting-element", "source-preserve"),
    ("live", "L4-attached-effect", "frame-governed"),
    ("defocus", "L2-focus", "source-preserve"),
    ("environment", "L6-environment", "frame-governed"),
    ("mask", "L7-mask", "frame-governed"),
)
DIRECTING_FIELDS = ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion", "fallbackIds")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_catalog_entry(entry: dict) -> dict:
    """Project catalog facts verbatim; directing metadata has no inference fallback."""
    projected = deepcopy(entry)
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else None
    if routing is not None:
        projected_routing = projected["routing"]
        for field in DIRECTING_FIELDS:
            if field in routing:
                projected_routing[field] = deepcopy(routing[field])
    return projected


def build(library: Path) -> dict:
    catalog_path, talkcraft_path = library / "catalog.json", library / "talkcraft-inventory.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    talkcraft = json.loads(talkcraft_path.read_text(encoding="utf-8"))
    talkcraft_entries = deepcopy(talkcraft.get("entries", []))
    for entry in talkcraft_entries:
        enrich(entry)
    system_source = library / "candidates/talkcraft/global-systems/talkcraft-systems.js"
    system_hash = "sha256:" + sha256(system_source)
    systems = [{
        "id": f"talkcraft-system:{system_id}", "title": system_id.replace("-", " ").title(),
        "kind": "global-system", "status": "candidate", "portStatus": "ported",
        "source": talkcraft.get("source", {}),
        "nativePort": {"path": "candidates/talkcraft/global-systems/talkcraft-systems.js", "sha256": system_hash, "demo": "candidates/talkcraft/global-systems/demo.html"},
        "sevenLayerPosition": layer, "aspectSupport": ["16:9", "9:16"], "framePolicy": frame,
        "seekSafe": True, "networkPolicy": "offline", "knownGaps": ["Matched-frame baseline and visual review pending."],
    } for system_id, layer, frame in SYSTEMS]
    return {
        "schemaVersion": "hyperframes-shared-catalog/v1",
        "revision": catalog.get("revision"),
        "generated": True,
        "sources": [
            {"path": "catalog.json", "sha256": sha256(catalog_path), "schemaVersion": catalog.get("schemaVersion")},
            {"path": "talkcraft-inventory.json", "sha256": sha256(talkcraft_path), "commit": talkcraft.get("source", {}).get("commit")},
        ],
        "entries": [project_catalog_entry(entry) for entry in catalog.get("entries", []) if isinstance(entry, dict)] + talkcraft_entries + systems,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json (default: skill assets/library)")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    library = args.library.resolve()
    output = library / "director-catalog.json"
    rendered = json.dumps(build(library), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("director-catalog.json drifted; rebuild it")
    else:
        output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
