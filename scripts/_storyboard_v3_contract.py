"""Pure Storyboard v3 and routed-result contract validation."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


REFERENCES = Path(__file__).resolve().parents[1] / "references"
STORYBOARD_SCHEMA_PATH = REFERENCES / "storyboard-spec.schema.json"
RESULT_SCHEMA_PATH = REFERENCES / "curated-intake-result.schema.json"
LOCKED_FIELDS = {
    "timing": ("start", "end"),
    "content": ("content",),
    "visual": ("visual",),
    "uses": ("uses",),
    "motion": ("motion",),
    "next": ("next",),
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_errors(value: dict[str, Any], schema_path: Path) -> list[str]:
    storyboard_schema = _load(STORYBOARD_SCHEMA_PATH)
    registry = Registry().with_resource(storyboard_schema["$id"], Resource.from_contents(storyboard_schema))
    validator = Draft202012Validator(_load(schema_path), registry=registry)
    return [
        "/" + "/".join(map(str, error.absolute_path)) + ": " + error.message
        for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    ]


def validate_storyboard_v3(value: dict[str, Any]) -> None:
    errors = _schema_errors(value, STORYBOARD_SCHEMA_PATH)
    if errors:
        raise ValueError("Invalid Storyboard v3: " + "; ".join(errors))
    scenes = value["scenes"]
    scene_ids = [scene["id"] for scene in scenes]
    if len(scene_ids) != len(set(scene_ids)):
        raise ValueError("Storyboard v3 scene IDs must be unique")
    cursor = 0
    for index, scene in enumerate(scenes):
        if scene["start"] != cursor or scene["end"] <= scene["start"]:
            raise ValueError(f"Scene {scene['id']} must be positive and continuous from {cursor:g} seconds")
        cursor = scene["end"]
        use_ids = [binding["id"] for binding in scene["uses"]]
        if len(use_ids) != len(set(use_ids)):
            raise ValueError(f"Scene {scene['id']} uses each catalog/authored ID at most once")
        next_value = scene.get("next")
        if index == len(scenes) - 1:
            if next_value is not None:
                raise ValueError(f"Final scene {scene['id']} must omit next")
        elif next_value is not None and next_value["sceneId"] != scene_ids[index + 1]:
            raise ValueError(f"Scene {scene['id']} next.sceneId must be the adjacent scene {scene_ids[index + 1]!r}")
    if cursor != value["duration"]:
        raise ValueError(f"Storyboard v3 scenes end at {cursor:g} seconds, not duration {value['duration']:g}")


def validate_routed_result_v3(result: dict[str, Any], storyboard: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a merged copy without mutating the approved Storyboard."""
    validate_storyboard_v3(storyboard)
    errors = _schema_errors(result, RESULT_SCHEMA_PATH)
    if errors:
        raise ValueError("Invalid routed result v3: " + "; ".join(errors))
    merged = copy.deepcopy(storyboard)
    scenes = {scene["id"]: scene for scene in merged["scenes"]}
    patched_ids: set[str] = set()
    for patch in result["scenePatches"]:
        scene_id = patch["sceneId"]
        if scene_id in patched_ids:
            raise ValueError(f"Routed result repeats scene patch {scene_id}")
        patched_ids.add(scene_id)
        if scene_id not in scenes:
            raise ValueError(f"Routed result references unknown scene {scene_id}")
        scene = scenes[scene_id]
        locks = scene.get("locks", {})
        if storyboard["timing_mode"] == "locked" or locks.get("timing") is True:
            for field in LOCKED_FIELDS["timing"]:
                if field in patch and patch[field] != scene[field]:
                    raise ValueError(f"Scene {scene_id} has locked timing field {field}")
        for lock, fields in LOCKED_FIELDS.items():
            if lock == "timing" or locks.get(lock) is not True:
                continue
            for field in fields:
                if field in patch and patch[field] != scene.get(field):
                    raise ValueError(f"Scene {scene_id} has locked field {field}")
        patch_locks = patch.get("locks")
        if isinstance(patch_locks, dict):
            cleared = [name for name, locked in locks.items() if locked is True and patch_locks.get(name) is not True]
            if cleared:
                raise ValueError(f"Scene {scene_id} patch cannot clear locks: {', '.join(sorted(cleared))}")
        for field, value in patch.items():
            if field not in {"segmentId", "sceneId"}:
                scene[field] = copy.deepcopy(value)
    validate_storyboard_v3(merged)
    return merged
