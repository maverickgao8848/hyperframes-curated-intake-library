"""Authority checks for Curated Intake routed by Visual Director."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REQUEST_SCHEMA = "hyperframes-visual-director/curated-request-v1"
RESULT_SCHEMA = "hyperframes-visual-director/curated-result-v1"


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_hash(plan: dict[str, Any]) -> str:
    value = copy.deepcopy(plan)
    if isinstance(value.get("approval"), dict):
        value["approval"]["approvedHash"] = None
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def validate_schema(value: dict[str, Any], schema_path: Path) -> list[str]:
    schema = load(schema_path)
    return [
        "/" + "/".join(str(part) for part in error.absolute_path) + ": " + error.message
        for error in sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.absolute_path))
    ]


def validate_request(request_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    request_path = request_path.resolve()
    request = load(request_path)
    schema_path = Path(__file__).resolve().parents[1] / "references" / "curated-intake-request.schema.json"
    errors = validate_schema(request, schema_path)
    if errors:
        raise ValueError("invalid routed request: " + "; ".join(errors))
    parent_path = (request_path.parent / request["parentPlanPath"]).resolve()
    if not parent_path.is_file():
        raise ValueError(f"parent plan does not exist: {parent_path}")
    parent = load(parent_path)
    if canonical_hash(parent) != request["parentPlanHash"]:
        raise ValueError("parentPlanHash does not match the current director plan")
    parent_by_id = {segment.get("id"): segment for segment in parent.get("segments", []) if isinstance(segment, dict)}
    unknown = [segment_id for segment_id in request["segmentIds"] if segment_id not in parent_by_id]
    if unknown:
        raise ValueError("routed request contains unknown segment IDs: " + ", ".join(unknown))
    wrong_route = [segment_id for segment_id in request["segmentIds"] if parent_by_id[segment_id].get("route") != "curated-intake"]
    if wrong_route:
        raise ValueError("routed request includes non-Curated segments: " + ", ".join(wrong_route))
    scope_ids = request.get("approvedScope", {}).get("segmentIds")
    if scope_ids is not None and scope_ids != request["segmentIds"]:
        raise ValueError("approvedScope.segmentIds must exactly match segmentIds")
    return request, parent


def result_packet(request: dict[str, Any], storyboard: dict[str, Any]) -> dict[str, Any]:
    mapping = request.get("approvedScope", {}).get("segmentSceneMap", {})
    all_scene_ids = [str(frame["id"]) for frame in storyboard["frames"]]
    updates = []
    for index, segment_id in enumerate(request["segmentIds"]):
        scene_ids = mapping.get(segment_id, all_scene_ids if index == 0 else [])
        frames = [frame for frame in storyboard["frames"] if str(frame["id"]) in set(scene_ids)]
        updates.append({
            "segmentId": segment_id,
            "sceneContracts": [f"scene-contracts/{frame['id']}.json" for frame in frames],
            "beats": [beat for frame in frames for beat in frame.get("beats", [])],
            "components": [item for frame in frames for item in frame.get("integrations", [])],
            "questionsResolved": [],
        })
    return {
        "schemaVersion": RESULT_SCHEMA,
        "parentPlanHash": request["parentPlanHash"],
        "clusterId": request["clusterId"],
        "segmentIds": request["segmentIds"],
        "lockedDecisions": request.get("lockedDecisions", []),
        "segmentUpdates": updates,
        "scopeChangeProposal": None,
    }

