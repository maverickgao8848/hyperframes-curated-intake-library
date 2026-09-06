#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from director_plan import atomic_write_json, compile_handoffs, load_json, plan_hash, validate_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive downstream request packets from an approved director plan.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    plan = load_json(project / "director-plan.json")
    catalog = load_json(args.catalog) if args.catalog else None
    errors = validate_plan(plan, catalog)
    if errors:
        raise SystemExit("Director plan is invalid:\n- " + "\n- ".join(errors))
    packets = compile_handoffs(plan)
    manifest = {"schemaVersion": "hyperframes-visual-director/handoff-manifest-v1", "parentPlanHash": plan_hash(plan), "parentRevision": plan["revision"], "routes": {}}
    for route, items in packets.items():
        manifest["routes"][route] = []
        for item in items:
            suffix = "curated-intake-request.json" if route == "curated-intake" else "request.json"
            packet_id = item.get("clusterId", item.get("segmentId"))
            relative = Path("handoffs") / route / str(packet_id) / suffix
            atomic_write_json(project / relative, item)
            manifest["routes"][route].append(relative.as_posix())
    atomic_write_json(project / "handoffs" / "manifest.json", manifest)
    print(project / "handoffs" / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
