#!/usr/bin/env python3
"""Explicit, deterministic Storyboard v2 to v3 draft migration."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from _storyboard_v3_contract import validate_storyboard_v3


REFERENCES = Path(__file__).resolve().parents[1] / "references"
WINDOW_RE = re.compile(r"^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)s$")


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def parse_window(value: str) -> tuple[float, float]:
    match = WINDOW_RE.fullmatch(value)
    if not match:
        raise ValueError(f"Invalid v2 scene window: {value}")
    return float(match.group(1)), float(match.group(2))


def labeled_visual(scene: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    thesis = scene["visual_thesis"]
    focus = scene["focus"]
    values = [
        ("Subject", thesis["subject"], "/visual_thesis/subject"),
        ("Change", thesis["change"], "/visual_thesis/change"),
        ("Semantic bridge", thesis["semantic_bridge"], "/visual_thesis/semantic_bridge"),
        ("Primary focus", focus["primary"], "/focus/primary"),
    ]
    if focus.get("secondary"):
        values.append(("Secondary focus", focus["secondary"], "/focus/secondary"))
    return "\n".join(f"{label}: {text}" for label, text, _ in values), [
        {"source": source, "destination": "/visual", "label": label} for label, _, source in values
    ]


def aggregate_uses(scene: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    order: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    evidence: list[dict[str, Any]] = []

    def add(item_id: str, responsibility: str, required: bool, source: str, removed_target: str | None = None) -> None:
        if item_id not in by_id:
            order.append(item_id)
            by_id[item_id] = {"id": item_id, "responsibilities": [], "required": False}
        record = by_id[item_id]
        if responsibility not in record["responsibilities"]:
            record["responsibilities"].append(responsibility)
        record["required"] = bool(record["required"] or required)
        mapping = {"source": source, "destinationId": item_id, "required": required}
        if removed_target is not None:
            mapping["removedTarget"] = removed_target
        evidence.append(mapping)

    for index, event in enumerate(scene["choreography"]):
        if event.get("via"):
            add(str(event["via"]), str(event["purpose"]), True, f"/choreography/{index}/via", str(event["target"]))
    for index, binding in enumerate(scene["reuse"]):
        add(str(binding["id"]), str(binding["responsibility"]), binding["required"] is True, f"/reuse/{index}/id", str(binding["target"]))
    exit_value = scene["exit"]
    if exit_value.get("via"):
        add(str(exit_value["via"]), f"Transition: {exit_value['state']}", True, "/exit/via")
    return [by_id[item_id] for item_id in order], evidence


def migrate_v2(value: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if value.get("schema") == "hyperframes-storyboard/v3":
        raise ValueError("Input is already hyperframes-storyboard/v3; migration is not idempotent input normalization")
    if value.get("schema") != "hyperframes-storyboard/v2":
        raise ValueError("Only hyperframes-storyboard/v2 can be migrated")
    legacy_schema = read_object(REFERENCES / "storyboard-spec.v2.legacy.schema.json")
    errors = sorted(Draft202012Validator(legacy_schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        raise ValueError("Invalid Storyboard v2: " + "; ".join(error.message for error in errors))

    message = str(value["message"])
    root_mappings = [
        {"source": "/title", "destination": "/title"},
        {"source": "/message", "destination": "/message"},
        {"source": "/duration", "destination": "/duration", "conversion": "seconds string to number"},
        {"source": "/timing_mode", "destination": "/timing_mode"},
    ]
    if value.get("throughline"):
        message += "\nThroughline: " + str(value["throughline"])
        root_mappings.append({"source": "/throughline", "destination": "/message", "label": "Throughline"})
    scenes: list[dict[str, Any]] = []
    scene_mappings: list[dict[str, Any]] = []
    for scene_index, old in enumerate(value["scenes"]):
        start, end = parse_window(old["window"])
        visual, text_mappings = labeled_visual(old)
        motion_lines: list[str] = []
        event_mappings: list[dict[str, Any]] = []
        for event_index, event in enumerate(old["choreography"]):
            motion_lines.extend([f"Change: {event['change']}", f"Purpose: {event['purpose']}"])
            event_mappings.append({
                "eventId": event["id"],
                "source": f"/choreography/{event_index}",
                "destination": "/motion",
                "removedStructure": {
                    "id": event["id"], "window": event["window"],
                    "target": event["target"], "role": event["role"],
                },
            })
        exit_value = old["exit"]
        next_value = None
        if exit_value["to_scene"] is not None:
            next_value = {"sceneId": exit_value["to_scene"], "transition": exit_value["state"]}
        else:
            motion_lines.append("Final state: " + exit_value["state"])
        uses, binding_mappings = aggregate_uses(old)
        new_scene: dict[str, Any] = {
            "id": old["id"],
            "title": old["title"],
            "start": start,
            "end": end,
            "content": old["takeaway"],
            "visual": visual,
            "uses": uses,
            "motion": "\n".join(motion_lines),
        }
        if next_value is not None:
            new_scene["next"] = next_value
        if old.get("source_anchor"):
            new_scene["source_anchor"] = copy.deepcopy(old["source_anchor"])
        scenes.append(new_scene)
        scene_mappings.append({
            "sourceSceneId": old["id"],
            "outputSceneId": new_scene["id"],
            "idMapping": {"source": "/id", "destination": "/id"},
            "textMappings": [
                {"source": "/title", "destination": "/title"},
                {"source": "/takeaway", "destination": "/content"},
                *text_mappings,
                *[
                    {"source": f"/choreography/{index}/{field}", "destination": "/motion", "label": field.title()}
                    for index, _ in enumerate(old["choreography"])
                    for field in ("change", "purpose")
                ],
                {"source": "/exit/state", "destination": "/next/transition" if next_value else "/motion", "label": "Transition" if next_value else "Final state"},
            ],
            "eventMappings": event_mappings,
            "bindingMappings": binding_mappings,
            "sourceAnchor": {"source": "/source_anchor", "destination": "/source_anchor", "mapped": bool(old.get("source_anchor"))},
            "externalizedNeedsReview": [
                {"source": f"/{field}", "value": copy.deepcopy(old[field])}
                for field in (
                    "semantic_tags", "narrative_role", "available_inputs", "aspect",
                    "duration_seconds", "hero_required", "exceptions", "tempo_override",
                )
                if field in old
            ],
            "review": {
                "state": "needs-review",
                "reasons": [
                    "Confirm the flattened visual and every aggregated binding.",
                    *(["Author an explicit internal semantic change or justified static reason for this scene over three seconds."] if end - start > 3 else []),
                ],
            },
        })
    output = {
        "schema": "hyperframes-storyboard/v3",
        "title": value["title"],
        "message": message,
        "duration": float(str(value["duration"]).removesuffix("s")),
        "timing_mode": value["timing_mode"],
        "scenes": scenes,
    }
    validate_storyboard_v3(output)
    report = {
        "schemaVersion": "hyperframes-storyboard-migration-report/v1",
        "status": "needs-review",
        "sourceSchema": "hyperframes-storyboard/v2",
        "outputSchema": "hyperframes-storyboard/v3",
        "sourceHash": canonical_hash(value),
        "outputHash": canonical_hash(output),
        "approvalInherited": False,
        "authoritative": False,
        "unresolvedSceneIds": [scene["id"] for scene in output["scenes"]],
        "rootMappings": root_mappings,
        "sceneMappings": scene_mappings,
        "reviewReasons": [
            "Confirm the flattened visual and motion prose.",
            "Confirm every aggregated use and transition before approval.",
            "Migration never inherits approval or locks.",
        ],
    }
    return output, report


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an unapproved Storyboard v3 draft and external mapping report from v2.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source, output, report = args.input.resolve(), args.output.resolve(), args.report.resolve()
    if len({source, output, report}) != 3:
        raise SystemExit("--input, --output, and --report must be three distinct paths; in-place migration is forbidden")
    try:
        migrated, migration_report = migrate_v2(read_object(source))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(str(error)) from error
    write_json(output, migrated)
    write_json(report, migration_report)
    print(f"Wrote unapproved v3 draft: {output}")
    print(f"Wrote non-authoritative needs-review report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
