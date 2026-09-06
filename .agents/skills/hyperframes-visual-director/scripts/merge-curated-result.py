#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from director_plan import PatchError, atomic_write_json, load_json, plan_hash, utc_now, validate_plan


PATCH_FIELDS = {"title", "start", "end", "content", "visual", "uses", "motion", "next", "narration", "on_screen_text", "sfx", "source_anchor", "locks"}
LOCK_FIELDS = {"timing": {"start", "end"}, "content": {"content"}, "visual": {"visual"}, "uses": {"uses"}, "motion": {"motion"}, "next": {"next"}}


def _validate_result_schema(result: dict) -> None:
    curated = Path(__file__).resolve().parents[2] / "hyperframes-curated-intake" / "references"
    storyboard_schema = load_json(curated / "storyboard-spec.schema.json")
    result_schema = load_json(curated / "curated-intake-result.schema.json")
    registry = Registry().with_resource(storyboard_schema["$id"], Resource.from_contents(storyboard_schema))
    errors = sorted(Draft202012Validator(result_schema, registry=registry).iter_errors(result), key=lambda error: list(error.absolute_path))
    if errors:
        raise PatchError("invalid curated result v3: " + "; ".join(error.message for error in errors))


def merge_result(plan: dict, result: dict, catalog: dict | None = None, request: dict | None = None) -> dict:
    _validate_result_schema(result)
    if request is None:
        raise PatchError("curated request is required for stable scene membership and lock enforcement")
    if result.get("parentPlanHash") != plan_hash(plan):
        raise PatchError("curated result parentPlanHash does not match current director plan")
    allowed = set(result.get("requestedSegmentIds", []))
    known = {segment["id"] for segment in plan["segments"]}
    if not allowed or not allowed <= known:
        raise PatchError("curated result contains an empty or unknown scope")
    if request.get("parentPlanHash") != result["parentPlanHash"] or set(request.get("segmentIds", [])) != allowed:
        raise PatchError("curated request/result scope or parent hash mismatch")
    updated = copy.deepcopy(plan)
    scene_map = request.get("approvedScope", {}).get("segmentSceneMap", {})
    if set(scene_map) != allowed:
        raise PatchError("approvedScope.segmentSceneMap keys must exactly match requested segments")
    scene_owner: dict[str, str] = {}
    for segment_id in request["segmentIds"]:
        for scene_id in scene_map[segment_id]:
            if scene_id in scene_owner:
                raise PatchError(f"stable scene ID {scene_id!r} is assigned to multiple segments")
            scene_owner[scene_id] = segment_id
    request_locks = set(request.get("lockedDecisions", []))
    requested_scene_locks = request.get("approvedScope", {}).get("sceneLocks", {})
    unknown_lock_ids = sorted(set(requested_scene_locks) - set(scene_owner))
    if unknown_lock_ids:
        raise PatchError("request sceneLocks contain unknown stable scene IDs: " + ", ".join(unknown_lock_ids))
    patched_scene_ids: set[str] = set()
    for update in result.get("scenePatches", []):
        sid = update.get("segmentId")
        if sid not in allowed:
            raise PatchError(f"curated result attempts out-of-scope update {sid!r}")
        segment = next(item for item in updated["segments"] if item["id"] == sid)
        if segment.get("route") != "curated-intake":
            raise PatchError(f"curated result targets non-Curated segment {sid!r}")
        scene_id = update["sceneId"]
        if scene_id in patched_scene_ids:
            raise PatchError(f"curated result repeats scene patch {scene_id!r}")
        patched_scene_ids.add(scene_id)
        if scene_id not in scene_owner:
            raise PatchError(f"curated result scene {scene_id!r} is outside approved stable scene IDs")
        if scene_owner[scene_id] != sid:
            raise PatchError(f"curated result scene {scene_id!r} belongs to {scene_owner[scene_id]!r}, not {sid!r}")
        forbidden = request_locks & set(update)
        if forbidden:
            raise PatchError("curated result modifies locked decisions: " + ", ".join(sorted(forbidden)))
        for lock, locked in requested_scene_locks.get(scene_id, {}).items():
            if locked is True and LOCK_FIELDS.get(lock, set()) & set(update):
                raise PatchError(f"curated result modifies request-locked scene field: {scene_id}/{lock}")
        scenes = segment.setdefault("curated", {}).setdefault("storyboardScenes", [])
        existing = next((scene for scene in scenes if scene.get("id") == scene_id), None)
        if existing is None:
            missing = {"start", "end", "content", "visual", "uses", "motion"} - set(update)
            if missing:
                raise PatchError("first curated scene patch is incomplete: " + ", ".join(sorted(missing)))
            existing = {"id": scene_id}
            scenes.append(existing)
        locks = existing.get("locks", {})
        for lock, fields in LOCK_FIELDS.items():
            if locks.get(lock) is True:
                changed = [field for field in fields if field in update and update[field] != existing.get(field)]
                if changed:
                    raise PatchError(f"curated result modifies scene-locked field: {scene_id}/{changed[0]}")
        if isinstance(update.get("locks"), dict):
            cleared = [key for key, locked in locks.items() if locked is True and update["locks"].get(key) is not True]
            if cleared:
                raise PatchError("curated result cannot clear scene locks: " + ", ".join(sorted(cleared)))
        existing.update({key: copy.deepcopy(value) for key, value in update.items() if key in PATCH_FIELDS})
        segment["approval"]["state"] = "proposed"
    updated["revision"] += 1
    updated["approval"] = {"state": "in-review", "approvedRevision": None, "approvedHash": None}
    updated.setdefault("audit", []).append({"id": f"audit-{updated['revision']:06d}", "at": utc_now(), "actor": "curated-intake", "type": "merge-curated-result", "segmentIds": sorted(allowed)})
    errors = validate_plan(updated, catalog)
    if errors:
        raise PatchError("; ".join(errors))
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge a bounded Curated Intake result into the director authority.")
    parser.add_argument("project", type=Path)
    parser.add_argument("result", type=Path)
    parser.add_argument("--request", type=Path, required=True, help="Original routed request for stable scope and lock enforcement.")
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args()
    plan_path = args.project.resolve() / "director-plan.json"
    plan = load_json(plan_path)
    result = load_json(args.result)
    request = load_json(args.request) if args.request else None
    catalog = load_json(args.catalog) if args.catalog else None
    updated = merge_result(plan, result, catalog, request)
    atomic_write_json(plan_path, updated)
    print(plan_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
