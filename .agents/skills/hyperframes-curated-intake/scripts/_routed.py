"""Bounded Curated Intake patches for the Visual Director authority."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from _storyboard_v3_contract import validate_routed_result_v3

REQUEST_SCHEMA = "hyperframes-visual-director/curated-request-v3"
RESULT_SCHEMA = "hyperframes-visual-director/curated-result-v3"
PATCH_FIELDS = {
    "title", "start", "end", "content", "visual", "uses", "motion", "next",
    "narration", "on_screen_text", "sfx", "source_anchor", "locks",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(plan: dict[str, Any]) -> str:
    value = copy.deepcopy(plan)
    if isinstance(value.get("approval"), dict):
        value["approval"]["approvedHash"] = None
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def validate_schema(value: dict[str, Any], schema_path: Path) -> list[str]:
    schema = load(schema_path)
    return ["/" + "/".join(map(str, error.absolute_path)) + ": " + error.message for error in sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.absolute_path))]


def validate_request(request_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    request_path = request_path.resolve()
    request = load(request_path)
    errors = validate_schema(request, Path(__file__).resolve().parents[1] / "references" / "curated-intake-request.schema.json")
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
    wrong = [segment_id for segment_id in request["segmentIds"] if parent_by_id[segment_id].get("route") != "curated-intake"]
    if wrong:
        raise ValueError("routed request includes non-Curated segments: " + ", ".join(wrong))
    if request.get("approvedScope", {}).get("segmentIds") not in (None, request["segmentIds"]):
        raise ValueError("approvedScope.segmentIds must exactly match segmentIds")
    scene_map = request.get("approvedScope", {}).get("segmentSceneMap", {})
    requested_segments = set(request["segmentIds"])
    if set(scene_map) != requested_segments:
        missing = sorted(requested_segments - set(scene_map))
        extra = sorted(set(scene_map) - requested_segments)
        raise ValueError("approvedScope.segmentSceneMap keys must exactly match requested segments" + (f"; missing={missing}; extra={extra}" if missing or extra else ""))
    mapped_scene_ids = [str(scene_id) for segment_id in request["segmentIds"] for scene_id in scene_map.get(segment_id, [])]
    if len(mapped_scene_ids) != len(set(mapped_scene_ids)):
        raise ValueError("approvedScope.segmentSceneMap must assign each stable scene ID exactly once")
    unknown_lock_ids = sorted(set(request.get("approvedScope", {}).get("sceneLocks", {})) - set(mapped_scene_ids))
    if unknown_lock_ids:
        raise ValueError("approvedScope.sceneLocks contains unknown stable scene IDs: " + ", ".join(unknown_lock_ids))
    return request, parent


def result_packet(request: dict[str, Any], storyboard: dict[str, Any], catalog_misses: list | None = None) -> dict[str, Any]:
    mapping = request.get("approvedScope", {}).get("segmentSceneMap", {})
    scene_to_segment: dict[str, str] = {}
    for segment_id in request["segmentIds"]:
        for scene_id in mapping.get(segment_id, []):
            scene_to_segment[str(scene_id)] = segment_id
    storyboard_ids = {scene["id"] for scene in storyboard["scenes"]}
    if set(scene_to_segment) != storyboard_ids:
        missing = sorted(storyboard_ids - set(scene_to_segment))
        stale = sorted(set(scene_to_segment) - storyboard_ids)
        details = []
        if missing:
            details.append("unmapped Storyboard scenes: " + ", ".join(missing))
        if stale:
            details.append("mapped scene IDs absent from Storyboard: " + ", ".join(stale))
        raise ValueError("approvedScope.segmentSceneMap mismatch: " + "; ".join(details))
    patches = []
    for scene in storyboard["scenes"]:
        segment_id = scene_to_segment.get(scene["id"])
        if not segment_id:
            continue
        patches.append({
            "segmentId": segment_id,
            "sceneId": scene["id"],
            **{key: copy.deepcopy(value) for key, value in scene.items() if key in PATCH_FIELDS},
        })
    packet = {"schemaVersion": RESULT_SCHEMA, "parentPlanHash": request["parentPlanHash"], "clusterId": request["clusterId"], "requestedSegmentIds": request["segmentIds"], "scenePatches": patches, "catalogMisses": catalog_misses or [], "scopeChangeProposal": None}
    validate_routed_result_v3(packet, storyboard)
    return packet
