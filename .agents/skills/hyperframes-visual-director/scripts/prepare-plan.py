#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from director_plan import atomic_write_json, load_json, plan_metrics, validate_plan


def catalog_digest(catalog: dict[str, Any]) -> str:
    payload = json.dumps(catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def render_director(plan: dict[str, Any]) -> str:
    metrics = plan_metrics(plan)
    lines = [
        "# Visual Director Plan",
        "",
        f"**{plan['project']['title']}** · revision {plan['revision']} · {plan['timing']['precision']} timing",
        "",
        "This document is derived from `director-plan.json`; edit through the workbench, not here.",
        "",
        "## Coverage",
        "",
        f"- Dominant visual coverage: {metrics['dominantVisualCoveragePercent']:g}%",
        f"- Curated teaching segments: {metrics['curatedTeachingCount']}",
        f"- External/user asset requests: {metrics['externalAssetRequestCount']}",
        f"- Unresolved risks: {metrics['unresolvedRiskCount']}",
        "",
        "| Segment | Frames | Message | Dominant visual | Layers | Route | Approval |",
        "|---|---:|---|---|---|---|---|",
    ]
    for segment in plan["segments"]:
        visual = segment["dominantVisual"]
        label = visual.get("catalogId", visual["type"])
        layer_labels = ", ".join(layer.get("catalogId", layer["type"]) for layer in segment.get("layers", [])) or "—"
        lines.append(
            f"| `{segment['id']}` | {segment['range']['startFrame']}–{segment['range']['endFrame']} | "
            f"{segment['message']} | `{label}` ({visual['framePolicy']}) | {layer_labels} | "
            f"`{segment['route']}` | `{segment['approval']['state']}` |"
        )
    lines.extend(["", "## Layer coverage", ""])
    for kind, percent in metrics["layerCoveragePercent"].items():
        lines.append(f"- `{kind}`: {percent:g}%")
    return "\n".join(lines) + "\n"


def render_asset_sheet(plan: dict[str, Any]) -> str:
    lines = [
        "# Asset Call Sheet",
        "",
        "Derived from `director-plan.json`. Status changes must be applied as bounded patches.",
        "",
        "| ID | Priority | Owner | Used in | Specification | Status | Fallback |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in plan.get("assetRequests", []):
        fallback = item.get("fallback", {}).get("description", item.get("fallback", {}).get("type", "—"))
        lines.append(
            f"| `{item['id']}` | {item['priority']} | {item['owner']} | {', '.join(item['segmentIds'])} | "
            f"{item['specification']} | {item['status']} | {fallback} |"
        )
    if not plan.get("assetRequests"):
        lines.append("| — | — | — | — | No asset requests. | — | — |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and install a proposed director plan as the single machine authority.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    destination = project / "director-plan.json"
    if destination.exists() and not args.replace:
        raise SystemExit(f"Refusing to replace existing authority without --replace: {destination}")
    plan = load_json(args.plan)
    catalog = load_json(args.catalog) if args.catalog else None
    if catalog:
        plan.setdefault("libraryLock", {})["catalogSha256"] = catalog_digest(catalog)
    errors = validate_plan(plan, catalog)
    if errors:
        raise SystemExit("Director plan is invalid:\n- " + "\n- ".join(errors))
    project.mkdir(parents=True, exist_ok=True)
    atomic_write_json(destination, plan)
    (project / "DIRECTOR.md").write_text(render_director(plan), encoding="utf-8")
    atomic_write_json(project / "asset-call-sheet.json", {"schemaVersion": "hyperframes-visual-director/asset-call-sheet-v1", "parentRevision": plan["revision"], "items": plan.get("assetRequests", [])})
    (project / "asset-call-sheet.md").write_text(render_asset_sheet(plan), encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
