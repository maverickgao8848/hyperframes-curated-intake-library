"""Deterministic authority, validation, metrics, patches, and handoffs for Visual Director."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA_VERSION = "hyperframes-visual-director/v1"
PATCH_SCHEMA_VERSION = "hyperframes-visual-director/patch-v1"
READY_STATUSES = {"ready", "verified", "published"}
READY_PORT_STATUSES = {"verified", "published"}
ROUTES = {"direct-build", "curated-intake", "media-sourcing", "source-only"}
FRAME_POLICIES = {"frame-governed", "native-evidence", "wrapper-only", "source-preserve"}
NATIVE_CATALOG_IDS = {
    "registry-block:wechat-desktop-exchange",
    "registry-block:chatgpt-desktop-exchange",
}


class RevisionConflict(ValueError):
    pass


class LockConflict(ValueError):
    pass


class PatchError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def plan_hash(plan: dict[str, Any]) -> str:
    value = copy.deepcopy(plan)
    approval = value.get("approval")
    if isinstance(approval, dict):
        approval["approvedHash"] = None
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = path.parent / ".director-tmp"
    temp_dir.mkdir(exist_ok=True)
    temp = temp_dir / f"{path.name}.{hashlib.sha256(canonical_bytes(value)).hexdigest()[:12]}.tmp"
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    try:
        temp_dir.rmdir()
    except OSError:
        pass


def schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "director-plan.schema.json"


def _schema_errors(plan: dict[str, Any]) -> list[str]:
    schema = load_json(schema_path())
    errors = []
    for error in sorted(Draft202012Validator(schema).iter_errors(plan), key=lambda item: list(item.absolute_path)):
        location = "/" + "/".join(str(part) for part in error.absolute_path)
        errors.append(f"schema{location}: {error.message}")
    return errors


def _catalog_index(catalog: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not catalog:
        return {}
    return {entry.get("id"): entry for entry in catalog.get("entries", []) if isinstance(entry, dict) and isinstance(entry.get("id"), str)}


def _range(value: Any) -> tuple[int, int] | None:
    if not isinstance(value, dict):
        return None
    start, end = value.get("startFrame"), value.get("endFrame")
    if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
        return None
    return start, end


def _validate_catalog_binding(
    errors: list[str],
    item: dict[str, Any],
    label: str,
    catalog_by_id: dict[str, dict[str, Any]],
    project_aspect: str,
) -> None:
    catalog_id = item.get("catalogId")
    if not catalog_id or not catalog_by_id:
        return
    entry = catalog_by_id.get(catalog_id)
    if entry is None:
        errors.append(f"{label}/catalogId: unknown catalog ID {catalog_id!r}")
        return
    status = entry.get("status")
    port_status = entry.get("portStatus")
    if status not in READY_STATUSES or (str(catalog_id).startswith("talkcraft:") and port_status not in READY_PORT_STATUSES):
        errors.append(f"{label}/catalogId: {catalog_id!r} is not ready (status={status!r}, portStatus={port_status!r})")
    aspects = entry.get("aspectSupport")
    if isinstance(aspects, list) and aspects and project_aspect not in aspects:
        errors.append(f"{label}/catalogId: {catalog_id!r} does not support aspect {project_aspect!r}")
    expected_policy = entry.get("framePolicy")
    if expected_policy and item.get("framePolicy") != expected_policy:
        errors.append(f"{label}/framePolicy: catalog requires {expected_policy!r} for {catalog_id!r}")


def validate_plan(plan: dict[str, Any], catalog: dict[str, Any] | None = None) -> list[str]:
    errors = _schema_errors(plan)
    if errors:
        return errors
    project = plan["project"]
    duration = project["durationFrames"]
    aspect = project["aspect"]
    catalog_by_id = _catalog_index(catalog)
    segments = sorted(plan["segments"], key=lambda segment: (segment["range"]["startFrame"], segment["id"]))
    ids: set[str] = set()
    cursor = 0
    for index, segment in enumerate(segments):
        sid = segment["id"]
        if sid in ids:
            errors.append(f"segments/{sid}: duplicate segment id")
        ids.add(sid)
        start, end = segment["range"]["startFrame"], segment["range"]["endFrame"]
        if start < cursor:
            errors.append(f"segments/{sid}/range: dominant visual overlap begins at {start}, before {cursor}")
        elif start > cursor:
            errors.append(f"segments/{sid}/range: dominant visual gap from {cursor} to {start}")
        if end <= start or end > duration:
            errors.append(f"segments/{sid}/range: illegal half-open range [{start}, {end}) for duration {duration}")
        cursor = max(cursor, end)
        dominant = segment["dominantVisual"]
        dtype = dominant["type"]
        policy = dominant["framePolicy"]
        if dtype in {"source-footage", "external-evidence", "external-broll"} and policy not in {"source-preserve", "native-evidence", "wrapper-only"}:
            errors.append(f"segments/{sid}/dominantVisual/framePolicy: preserved source cannot be frame-governed")
        if dominant.get("catalogId") in NATIVE_CATALOG_IDS and policy != "native-evidence":
            errors.append(f"segments/{sid}/dominantVisual/framePolicy: {dominant['catalogId']} must remain native-evidence")
        if policy == "native-evidence" and dtype not in {"registry-block", "external-evidence"}:
            errors.append(f"segments/{sid}/dominantVisual/framePolicy: native-evidence is invalid for {dtype}")
        _validate_catalog_binding(errors, dominant, f"segments/{sid}/dominantVisual", catalog_by_id, aspect)
        layer_ids: set[str] = set()
        for layer in segment.get("layers", []):
            lid = layer["id"]
            if lid in layer_ids:
                errors.append(f"segments/{sid}/layers/{lid}: duplicate layer id")
            layer_ids.add(lid)
            lstart, lend = layer["range"]["startFrame"], layer["range"]["endFrame"]
            if lstart < start or lend > end or lend <= lstart:
                errors.append(f"segments/{sid}/layers/{lid}/range: layer must stay inside its segment")
            _validate_catalog_binding(errors, layer, f"segments/{sid}/layers/{lid}", catalog_by_id, aspect)
        known_assets = {item["id"] for item in plan.get("assetRequests", [])}
        for asset_id in segment.get("assetRequestIds", []):
            if asset_id not in known_assets:
                errors.append(f"segments/{sid}/assetRequestIds: unknown asset request {asset_id!r}")
    if cursor < duration:
        errors.append(f"segments: dominant visual gap from {cursor} to {duration}")
    if sum(segment["range"]["endFrame"] - segment["range"]["startFrame"] for segment in segments) != duration:
        errors.append("segments: dominant visual duration share is not 100%")
    expected_edges = max(0, len(segments) - 1)
    if len(plan["edges"]) != expected_edges:
        errors.append(f"edges: expected {expected_edges} adjacent boundaries, found {len(plan['edges'])}")
    edge_pairs = {(edge["fromSegmentId"], edge["toSegmentId"]): edge for edge in plan["edges"]}
    for left, right in zip(segments, segments[1:]):
        pair = (left["id"], right["id"])
        edge = edge_pairs.get(pair)
        if edge is None:
            errors.append(f"edges: missing boundary {pair[0]} -> {pair[1]}")
        elif edge["boundaryFrame"] != left["range"]["endFrame"]:
            errors.append(f"edges/{edge['id']}: boundaryFrame must equal {left['range']['endFrame']}")
    approval = plan["approval"]
    if approval["state"] == "approved":
        unapproved = [segment["id"] for segment in segments if segment["approval"]["state"] not in {"approved", "locked"}]
        if unapproved:
            errors.append("approval: final approval requires every segment approved or locked: " + ", ".join(unapproved))
        if approval.get("approvedRevision") != plan["revision"]:
            errors.append("approval: approvedRevision must equal revision")
        if approval.get("approvedHash") != plan_hash(plan):
            errors.append("approval: approvedHash is stale or invalid")
    return errors


def _union_length(ranges: list[tuple[int, int]]) -> int:
    if not ranges:
        return 0
    total = 0
    start, end = sorted(ranges)[0]
    for next_start, next_end in sorted(ranges)[1:]:
        if next_start > end:
            total += end - start
            start, end = next_start, next_end
        else:
            end = max(end, next_end)
    return total + end - start


def plan_metrics(plan: dict[str, Any]) -> dict[str, Any]:
    duration = max(1, int(plan.get("project", {}).get("durationFrames", 1)))
    dominant: dict[str, int] = {}
    layer_ranges: dict[str, list[tuple[int, int]]] = {}
    for segment in plan.get("segments", []):
        span = _range(segment.get("range"))
        if not span:
            continue
        frames = max(0, span[1] - span[0])
        dtype = segment.get("dominantVisual", {}).get("type", "unknown")
        dominant[dtype] = dominant.get(dtype, 0) + frames
        for layer in segment.get("layers", []):
            lspan = _range(layer.get("range"))
            if lspan:
                layer_ranges.setdefault(layer.get("type", "unknown"), []).append(lspan)
    percent = lambda frames: round(frames * 100 / duration, 3)
    unresolved_risks = sum(1 for segment in plan.get("segments", []) if segment.get("stale") or segment.get("approval", {}).get("state") in {"proposed", "rejected"})
    return {
        "durationFrames": duration,
        "dominantVisualCoveragePercent": percent(sum(dominant.values())),
        "dominantVisualSharePercent": {key: percent(value) for key, value in sorted(dominant.items())},
        "layerCoveragePercent": {key: percent(_union_length(value)) for key, value in sorted(layer_ranges.items())},
        "curatedTeachingCount": sum(1 for segment in plan.get("segments", []) if segment.get("route") == "curated-intake"),
        "externalAssetRequestCount": sum(1 for item in plan.get("assetRequests", []) if item.get("source") in {"external", "user"}),
        "unresolvedRiskCount": unresolved_risks,
    }


def _segment(plan: dict[str, Any], segment_id: str) -> dict[str, Any]:
    for segment in plan["segments"]:
        if segment["id"] == segment_id:
            return segment
    raise PatchError(f"unknown segment {segment_id!r}")


def _assert_unlocked(segment: dict[str, Any], operation: str) -> None:
    if segment.get("approval", {}).get("state") == "locked" and operation != "comment":
        raise LockConflict(f"segment {segment['id']} is locked")


def apply_patch(plan: dict[str, Any], patch: dict[str, Any], actor: str, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    if patch.get("schemaVersion", PATCH_SCHEMA_VERSION) != PATCH_SCHEMA_VERSION:
        raise PatchError("unsupported patch schemaVersion")
    if patch.get("baseRevision") != plan.get("revision"):
        raise RevisionConflict(f"baseRevision {patch.get('baseRevision')} does not match revision {plan.get('revision')}")
    operations = patch.get("operations")
    if not isinstance(operations, list) or not operations:
        raise PatchError("operations must be a non-empty array")
    result = copy.deepcopy(plan)
    for operation in operations:
        if not isinstance(operation, dict):
            raise PatchError("each operation must be an object")
        op = operation.get("type")
        if op == "comment":
            body = operation.get("body")
            if not isinstance(body, str) or not body.strip():
                raise PatchError("comment body is required")
            continue
        if op == "approve-plan":
            for segment in result["segments"]:
                if segment["approval"]["state"] not in {"approved", "locked"}:
                    raise PatchError("every segment must be approved or locked before final approval")
            continue
        if op == "attach-asset":
            asset_id = operation.get("assetRequestId")
            asset_path = operation.get("assetPath")
            if not isinstance(asset_path, str) or not asset_path.strip():
                raise PatchError("attach-asset requires assetPath")
            asset = next((item for item in result.get("assetRequests", []) if item.get("id") == asset_id), None)
            if asset is None:
                raise PatchError(f"unknown asset request {asset_id!r}")
            if any(_segment(result, sid).get("approval", {}).get("state") == "locked" for sid in asset.get("segmentIds", [])):
                raise LockConflict(f"asset request {asset_id} is used by a locked segment")
            asset["linkedPath"] = asset_path
            asset["status"] = "linked"
            continue
        if op == "set-boundary":
            left_id, right_id, frame = operation.get("leftSegmentId"), operation.get("rightSegmentId"), operation.get("frame")
            if isinstance(frame, bool) or not isinstance(frame, int):
                raise PatchError("set-boundary requires an integer frame")
            left, right = _segment(result, str(left_id)), _segment(result, str(right_id))
            _assert_unlocked(left, str(op))
            _assert_unlocked(right, str(op))
            ordered = sorted(result["segments"], key=lambda item: item["range"]["startFrame"])
            if not any(a["id"] == left["id"] and b["id"] == right["id"] for a, b in zip(ordered, ordered[1:])):
                raise PatchError("set-boundary requires adjacent segments")
            if frame <= left["range"]["startFrame"] or frame >= right["range"]["endFrame"]:
                raise PatchError("set-boundary frame must stay inside the adjacent pair")
            left["range"]["endFrame"] = frame
            right["range"]["startFrame"] = frame
            for edge in result["edges"]:
                if edge["fromSegmentId"] == left["id"] and edge["toSegmentId"] == right["id"]:
                    edge["boundaryFrame"] = frame
            for item in (left, right):
                item["approval"]["state"] = "proposed"
            continue
        segment_id = operation.get("segmentId")
        if not isinstance(segment_id, str):
            raise PatchError(f"{op}: segmentId is required")
        segment = _segment(result, segment_id)
        _assert_unlocked(segment, str(op))
        if op == "set-approval":
            state = operation.get("state")
            if state not in {"proposed", "approved", "rejected", "locked"}:
                raise PatchError("invalid approval state")
            segment["approval"]["state"] = state
        elif op == "set-route":
            route = operation.get("route")
            if route not in ROUTES:
                raise PatchError("invalid route")
            segment["route"] = route
        elif op == "replace-dominant":
            value = operation.get("value")
            if not isinstance(value, dict):
                raise PatchError("replace-dominant requires value")
            segment["dominantVisual"] = copy.deepcopy(value)
            segment["approval"]["state"] = "proposed"
        elif op == "set-content":
            value = operation.get("content")
            if not isinstance(value, dict):
                raise PatchError("set-content requires an object")
            segment["dominantVisual"]["content"] = copy.deepcopy(value)
            segment["approval"]["state"] = "proposed"
        elif op == "set-range":
            value = operation.get("range")
            if _range(value) is None:
                raise PatchError("set-range requires integer startFrame/endFrame")
            segment["range"] = copy.deepcopy(value)
            segment["approval"]["state"] = "proposed"
        elif op == "add-layer":
            value = operation.get("layer")
            if not isinstance(value, dict):
                raise PatchError("add-layer requires layer")
            if any(layer.get("id") == value.get("id") for layer in segment["layers"]):
                raise PatchError(f"duplicate layer {value.get('id')!r}")
            segment["layers"].append(copy.deepcopy(value))
            segment["approval"]["state"] = "proposed"
        elif op == "remove-layer":
            layer_id = operation.get("layerId")
            before = len(segment["layers"])
            segment["layers"] = [layer for layer in segment["layers"] if layer.get("id") != layer_id]
            if len(segment["layers"]) == before:
                raise PatchError(f"unknown layer {layer_id!r}")
            segment["approval"]["state"] = "proposed"
        else:
            raise PatchError(f"unsupported operation {op!r}")
    result["revision"] += 1
    if any(operation.get("type") != "comment" for operation in operations):
        result["approval"] = {"state": "in-review", "approvedRevision": None, "approvedHash": None}
    if any(operation.get("type") == "approve-plan" for operation in operations):
        result["approval"] = {"state": "approved", "approvedRevision": result["revision"], "approvedHash": None}
        result["approval"]["approvedHash"] = plan_hash(result)
    result.setdefault("audit", []).append({
        "id": f"audit-{result['revision']:06d}",
        "at": utc_now(),
        "actor": actor,
        "baseRevision": patch["baseRevision"],
        "revision": result["revision"],
        "operations": copy.deepcopy(operations),
    })
    errors = validate_plan(result, catalog)
    if errors:
        raise PatchError("; ".join(errors))
    return result


def mark_source_changes(plan: dict[str, Any], current_hashes: dict[str, str]) -> dict[str, Any]:
    result = copy.deepcopy(plan)
    affected: set[str] = set()
    for source in result.get("sources", []):
        current = current_hashes.get(source["id"])
        if current and current != source.get("sha256"):
            source["previousSha256"] = source.get("sha256")
            source["sha256"] = current
            affected.update(source.get("segmentIds", []))
    if affected:
        result["revision"] += 1
        for segment in result["segments"]:
            if segment["id"] in affected:
                segment["stale"] = True
                if segment["approval"]["state"] != "locked":
                    segment["approval"]["state"] = "proposed"
        result["approval"] = {"state": "in-review", "approvedRevision": None, "approvedHash": None}
        result.setdefault("audit", []).append({"id": f"audit-{result['revision']:06d}", "at": utc_now(), "actor": "system", "type": "source-hash-change", "affectedSegmentIds": sorted(affected)})
    return result


def compile_handoffs(plan: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    if plan.get("approval", {}).get("state") != "approved":
        raise ValueError("director plan must be finally approved before compiling handoffs")
    packets: dict[str, list[dict[str, Any]]] = {}
    parent_hash = plan_hash(plan)
    for segment in plan["segments"]:
        route = segment["route"]
        packet: dict[str, Any] = {
            "schemaVersion": f"hyperframes-visual-director/{route}-request-v1",
            "parentPlanHash": parent_hash,
            "parentRevision": plan["revision"],
            "segmentId": segment["id"],
            "range": copy.deepcopy(segment["range"]),
            "message": segment["message"],
            "dominantVisual": copy.deepcopy(segment["dominantVisual"]),
            "layers": copy.deepcopy(segment.get("layers", [])),
            "assetRequestIds": copy.deepcopy(segment.get("assetRequestIds", [])),
            "timing": copy.deepcopy(plan["timing"]),
            "visualPolicy": copy.deepcopy(plan["visualPolicy"]),
            "lockedDecisions": ["range", "dominantVisual", "route"] if segment["approval"]["state"] == "locked" else [],
        }
        if route == "curated-intake":
            asset_by_id = {item["id"]: item for item in plan.get("assetRequests", [])}
            stable_scenes = segment.get("curated", {}).get("storyboardScenes", [])
            packet = {
                "schemaVersion": "hyperframes-visual-director/curated-request-v3",
                "parentPlanPath": "../../../director-plan.json",
                "parentPlanHash": parent_hash,
                "clusterId": f"teach-{segment['id']}",
                "segmentIds": [segment["id"]],
                "approvedScope": {
                    "segmentIds": [segment["id"]],
                    "ranges": [copy.deepcopy(segment["range"])],
                    "messages": [segment["message"]],
                    "animationSentencesLocked": segment["approval"]["state"] == "locked",
                    "segmentSceneMap": {segment["id"]: [scene["id"] for scene in stable_scenes]},
                    "sceneLocks": {scene["id"]: copy.deepcopy(scene.get("locks", {})) for scene in stable_scenes if scene.get("locks")},
                },
                "lockedDecisions": ["range", "dominantVisual", "route"] if segment["approval"]["state"] == "locked" else [],
                "inheritedVisualPolicy": copy.deepcopy(plan["visualPolicy"]),
                "timing": copy.deepcopy(plan["timing"]),
                "assets": [copy.deepcopy(asset_by_id[item]) for item in segment.get("assetRequestIds", []) if item in asset_by_id],
                "questionsStillOpen": [] if segment["approval"]["state"] == "locked" else ["Confirm the exact animation-worthy sentences inside this teaching cluster."],
            }
        packets.setdefault(route, []).append(packet)
    return packets
