from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/hyperframes-curated-intake"
sys.path.insert(0, str(SKILL / "scripts"))

from _storyboard_v3_contract import validate_routed_result_v3, validate_storyboard_v3


SCHEMA = json.loads((SKILL / "references/storyboard-spec.schema.json").read_text(encoding="utf-8"))
LEGACY_SCHEMA = json.loads((SKILL / "references/storyboard-spec.v2.legacy.schema.json").read_text(encoding="utf-8"))
LIBRARY_SCHEMA = json.loads((ROOT / "schemas/library.schema.json").read_text(encoding="utf-8"))
CATALOG_KINDS = set(LIBRARY_SCHEMA["$defs"]["entry"]["properties"]["kind"]["enum"])


def scene(scene_id: str, start: float, end: float, **extra: object) -> dict:
    value = {
        "id": scene_id,
        "start": start,
        "end": end,
        "content": f"Content for {scene_id}",
        "visual": f"Visual direction for {scene_id}",
        "uses": [{"id": "registry-component:flow-sequence", "responsibilities": ["Show ordered stages"], "required": True}],
        "motion": "Progressively reveal the stages, then hold.",
    }
    value.update(extra)
    return value


def storyboard(*, timing_mode: str = "approximate") -> dict:
    return {
        "schema": "hyperframes-storyboard/v3",
        "title": "Lean Storyboard",
        "message": "Selection changes outcomes.",
        "duration": 8,
        "timing_mode": timing_mode,
        "scenes": [
            scene("scene-one", 0, 4, next={"sceneId": "scene-two", "transition": "The selected card expands into the result."}),
            scene("scene-two", 4, 8, uses=[{"id": "authored:result-proof", "responsibilities": ["Show the verified result"], "required": True}]),
        ],
    }


def result(patch: dict) -> dict:
    return {
        "schemaVersion": "hyperframes-visual-director/curated-result-v3",
        "parentPlanHash": "sha256:" + "0" * 64,
        "clusterId": "cluster-1",
        "requestedSegmentIds": ["segment-1"],
        "scenePatches": [patch],
        "catalogMisses": [],
        "scopeChangeProposal": None,
    }


def test_minimal_v3_and_optional_fields_validate() -> None:
    value = storyboard()
    value["scenes"][0].update({
        "title": "Choose",
        "narration": "Choose the strongest evidence.",
        "on_screen_text": ["Choose"],
        "sfx": ["soft confirmation"],
        "source_anchor": {"source": "article.md", "anchor": "selection"},
        "locks": {"content": True, "uses": False},
    })
    jsonschema.Draft202012Validator(SCHEMA).validate(value)
    validate_storyboard_v3(value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("creative_profile", "dense-signature-v1"),
        ("throughline", "legacy prop"),
        ("selector", "#hero"),
        ("event_window", "0-50%"),
        ("candidateAudit", {"score": 9}),
        ("approval", {"status": "approved"}),
        ("needs-review", True),
    ],
)
def test_v3_rejects_legacy_selector_percentage_and_audit_fields(field: str, value: object) -> None:
    candidate = storyboard()
    candidate["scenes"][0][field] = value
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(SCHEMA).validate(candidate)


@pytest.mark.parametrize(
    "mutate,message",
    [
        (lambda value: value["scenes"][1].update(start=5), "continuous"),
        (lambda value: value["scenes"][0].update(end=0), "minimum"),
        (lambda value: value["scenes"][1].update(end=7), "duration"),
        (lambda value: value["scenes"][0]["next"].update(sceneId="scene-one"), "adjacent"),
        (lambda value: value["scenes"][1].update(next={"sceneId": "scene-one", "transition": "loop"}), "omit next"),
        (lambda value: value["scenes"][0]["uses"].append(copy.deepcopy(value["scenes"][0]["uses"][0])), "at most once"),
    ],
)
def test_v3_semantic_validator_rejects_timing_next_and_duplicate_uses(mutate, message: str) -> None:
    value = storyboard()
    mutate(value)
    with pytest.raises(ValueError, match=message):
        validate_storyboard_v3(value)


def test_next_may_be_omitted_for_an_ordinary_hard_cut() -> None:
    value = storyboard()
    value["scenes"][0].pop("next")
    validate_storyboard_v3(value)


def test_uses_requires_valid_id_unique_nonempty_responsibilities_and_boolean_required() -> None:
    for invalid in (
        {"id": "flow-sequence", "responsibilities": ["Show order"], "required": True},
        {"id": "authored:gap", "responsibilities": [], "required": True},
        {"id": "authored:gap", "responsibilities": ["Show", "Show"], "required": True},
        {"id": "authored:gap", "responsibilities": ["Show"], "required": 1},
    ):
        value = storyboard()
        value["scenes"][0]["uses"] = [invalid]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(SCHEMA).validate(value)


@pytest.mark.parametrize("namespace", sorted(CATALOG_KINDS | {"authored"}))
def test_uses_accepts_every_library_kind_namespace_and_authored(namespace: str) -> None:
    value = storyboard()
    value["scenes"][0]["uses"] = [{
        "id": f"{namespace}:example",
        "responsibilities": ["Provide the scene evidence"],
        "required": True,
    }]
    validate_storyboard_v3(value)


def test_uses_catalog_namespaces_exactly_match_the_root_library_schema() -> None:
    pattern = SCHEMA["$defs"]["catalogOrAuthoredUseId"]["pattern"]
    accepted = {
        kind
        for kind in CATALOG_KINDS | {"authored", "unknown"}
        if re.fullmatch(pattern, f"{kind}:example")
    }
    assert accepted == CATALOG_KINDS | {"authored"}


def test_recipe_use_id_is_separate_and_migration_only() -> None:
    assert "recipe" not in SCHEMA["$defs"]["catalogOrAuthoredUseId"]["pattern"]
    assert SCHEMA["$defs"]["migrationOnlyRecipeUseId"]["pattern"].startswith("^recipe:")
    value = storyboard()
    value["scenes"][0]["uses"] = [{"id": "recipe:legacy-fold", "responsibilities": ["Preserve the legacy binding"], "required": True}]
    validate_storyboard_v3(value)


@pytest.mark.parametrize(
    "item_id",
    ["unknown:example", "template:", ":example", "template", "Template:example", "template:Example"],
)
def test_uses_rejects_unknown_empty_missing_and_wrong_case_ids(item_id: str) -> None:
    value = storyboard()
    value["scenes"][0]["uses"] = [{"id": item_id, "responsibilities": ["Evidence"], "required": True}]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(SCHEMA).validate(value)


def test_locks_allow_only_the_six_confirmed_boolean_fields() -> None:
    value = storyboard()
    value["scenes"][0]["locks"] = {name: True for name in ("timing", "content", "visual", "uses", "motion", "next")}
    jsonschema.Draft202012Validator(SCHEMA).validate(value)
    for invalid in ({"title": True}, {"visual": "yes"}):
        value["scenes"][0]["locks"] = invalid
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(SCHEMA).validate(value)


def test_v3_patch_accepts_only_v3_fields_and_preserves_global_timing_lock() -> None:
    approved = storyboard(timing_mode="locked")
    merged = validate_routed_result_v3(
        result({"segmentId": "segment-1", "sceneId": "scene-one", "visual": "A clearer visual."}),
        approved,
    )
    assert merged["scenes"][0]["visual"] == "A clearer visual."
    assert approved["scenes"][0]["visual"] != merged["scenes"][0]["visual"]
    with pytest.raises(ValueError, match="locked timing"):
        validate_routed_result_v3(
            result({"segmentId": "segment-1", "sceneId": "scene-one", "end": 3}),
            approved,
        )
    with pytest.raises(ValueError, match="Invalid routed result v3"):
        validate_routed_result_v3(
            result({"segmentId": "segment-1", "sceneId": "scene-one", "visual_thesis": {}}),
            approved,
        )


def test_v3_patch_respects_scene_locks_and_cannot_clear_them() -> None:
    approved = storyboard()
    approved["scenes"][0]["locks"] = {"visual": True}
    with pytest.raises(ValueError, match="locked field visual"):
        validate_routed_result_v3(
            result({"segmentId": "segment-1", "sceneId": "scene-one", "visual": "Replacement"}),
            approved,
        )
    with pytest.raises(ValueError, match="cannot clear locks"):
        validate_routed_result_v3(
            result({"segmentId": "segment-1", "sceneId": "scene-one", "locks": {"visual": False}}),
            approved,
        )


def test_v2_schema_is_frozen_migration_only_and_rejects_v3() -> None:
    assert LEGACY_SCHEMA["$id"].endswith("curated-storyboard-v2.json")
    assert LEGACY_SCHEMA["properties"]["schema"]["const"] == "hyperframes-storyboard/v2"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(LEGACY_SCHEMA).validate(storyboard())
