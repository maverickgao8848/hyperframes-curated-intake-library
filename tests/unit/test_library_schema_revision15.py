from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[2]
LIBRARY_SCHEMA = json.loads((ROOT / "schemas/library.schema.json").read_text(encoding="utf-8"))
CURATION_SCHEMA = json.loads(
    (ROOT / ".agents/skills/hyperframes-curated-intake/references/curation.schema.json").read_text(encoding="utf-8")
)
STORYBOARD_PATH = ROOT / ".agents/skills/hyperframes-curated-intake/references/storyboard-spec.v2.legacy.schema.json"
CATALOG = json.loads(
    (ROOT / ".agents/skills/hyperframes-curated-intake/assets/library/catalog.json").read_text(encoding="utf-8")
)
LIBRARY_VALIDATOR = jsonschema.Draft202012Validator(LIBRARY_SCHEMA)
CURATION_VALIDATOR = jsonschema.Draft202012Validator(CURATION_SCHEMA)
TARGET_KINDS = {"registry-block", "registry-component", "svg", "lottie"}
DIRECTING_FIELDS = {"family", "purpose", "useWhen", "avoidWhen", "expects", "motion", "fallbackIds"}
LEGACY_TOP_LEVEL = {
    "semantic_tags", "narrative_roles", "granularity", "selection_role", "motionHooks", "supports",
    "compatibleRecipes", "affordances", "avoid", "heroEligible",
}
LEGACY_ROUTING = {
    "teachingIntents", "cognitiveActions", "sceneRoles", "evidenceTypes", "requiredInputs", "styleFit",
    "aspectFit", "densityFit", "containerCost", "heroEligible", "avoid", "durationMin", "durationMax",
}


def revision15_catalog() -> dict:
    value = copy.deepcopy(CATALOG)
    value["revision"] = 15
    for entry in value["entries"]:
        if entry["kind"] not in TARGET_KINDS:
            continue
        for field in LEGACY_TOP_LEVEL:
            entry.pop(field, None)
        routing = entry["routing"]
        for field in LEGACY_ROUTING:
            routing.pop(field, None)
    return value


def assert_invalid_library(value: dict) -> None:
    with pytest.raises(jsonschema.ValidationError):
        LIBRARY_VALIDATOR.validate(value)


def candidate() -> dict:
    return {
        "id": "registry-component:flow-sequence",
        "semanticTier": "exact",
        "matchedFamily": True,
        "matchedUseWhen": ["The beat has a strict sequence."],
        "matchedPurpose": True,
        "avoidConflicts": [],
        "expectsEvidence": [{"expectation": "Ordered step names", "evidence": "Storyboard event supplies three named steps."}],
        "hardFilterResults": [{"filter": "status-ready", "passed": True}],
        "motionPreference": "preferred",
        "repetitionApplied": False,
        "fallbackTrace": [],
        "source": {"catalogRevision": 15, "catalogId": "registry-component:flow-sequence"},
    }


def curation(candidate_value: dict, *, version: int = 5) -> dict:
    value = {
        "schemaVersion": f"hyperframes-curated-intake/v{version}",
        "policy": "approved-first",
        "frame": {
            "preset": "swiss-pulse", "projectPath": "frame.md", "sourcePath": "frames/swiss-pulse/FRAME.md",
            "sourceSha256": "0" * 64,
        },
        "registry": {},
        "storyboardHash": "1" * 64,
        "needs": [{
            "sceneId": "scene-01", "eventId": "event-01", "lane": "component", "query": "ordered process",
            "affordances": ["steps"], "candidates": [candidate_value],
            "selectedRef": "registry-component:flow-sequence", "result": "recommended", "rejections": [],
        }],
        "selectedIds": ["registry-component:flow-sequence"],
        "catalogMisses": [],
    }
    if version == 5:
        value["review"] = {"state": "approved", "storyboardHash": "1" * 64, "source": "automated-agent-attestation", "unresolvedSceneIds": [], "reviewer": {"type": "automated-agent", "workflow": "curated-intake", "rubricVersion": "motion-attestation/v1", "modelId": "fixture-agent"}, "sceneReviews": []}
    return value


def test_revision15_canonical_and_revision14_migration_input_are_valid() -> None:
    assert CATALOG["revision"] == 15
    LIBRARY_VALIDATOR.validate(CATALOG)
    migration_input = copy.deepcopy(CATALOG)
    migration_input["revision"] = 14
    LIBRARY_VALIDATOR.validate(migration_input)


def test_revision15_canonical_has_no_legacy_decision_fields_anywhere_in_entries() -> None:
    assert CATALOG["revision"] == 15
    for entry in CATALOG["entries"]:
        assert LEGACY_TOP_LEVEL.isdisjoint(entry), entry["id"]
        assert LEGACY_ROUTING.isdisjoint(entry.get("routing", {})), entry["id"]
        if entry["kind"] in TARGET_KINDS:
            assert set(entry["routing"]) <= DIRECTING_FIELDS


def test_migrated_block_machine_facts_keep_the_registry_rebuild_installable() -> None:
    index = {entry["id"]: entry for entry in CATALOG["entries"]}
    for item_id in (
        "registry-block:before-after-wipe",
        "registry-block:caption-camera-follow",
        "registry-block:ordered-dither-pass",
        "registry-block:particle-text-dissolve",
        "registry-block:stitched-text-draw",
        "registry-block:telemetry-hud",
        "registry-block:testimonial-proof-card",
        "registry-block:variable-axis-type",
    ):
        assert index[item_id]["aspectSupport"] == ["16:9"]
    assert index["registry-block:code-snippet-apple-terminal-clear-dark"]["duration"] == 7
    assert index["registry-block:code-snippet-dark-plus"]["duration"] == 12


def test_revision15_accepts_only_seven_routing_fields_on_all_targets() -> None:
    value = revision15_catalog()
    LIBRARY_VALIDATOR.validate(value)
    for entry in value["entries"]:
        if entry["kind"] in TARGET_KINDS:
            assert set(entry["routing"]) <= DIRECTING_FIELDS


@pytest.mark.parametrize("field", sorted(LEGACY_TOP_LEVEL))
def test_revision15_rejects_each_legacy_top_level_decision_field(field: str) -> None:
    value = revision15_catalog()
    entry = next(item for item in value["entries"] if item["kind"] == "registry-component")
    entry[field] = False if field == "heroEligible" else ([] if field not in {"granularity", "selection_role"} else ("element" if field == "granularity" else "content"))
    assert_invalid_library(value)


@pytest.mark.parametrize("field", sorted(LEGACY_ROUTING))
def test_revision15_rejects_each_legacy_routing_decision_field(field: str) -> None:
    value = revision15_catalog()
    entry = next(item for item in value["entries"] if item["kind"] == "registry-component")
    entry["routing"][field] = 1 if field == "containerCost" else (False if field == "heroEligible" else (1.0 if field in {"durationMin", "durationMax"} else ([] if field != "avoid" else "legacy")))
    assert_invalid_library(value)


def test_revision15_keeps_non_decision_facts_and_separates_semantic_expects_from_machine_inputs() -> None:
    value = revision15_catalog()
    entry = next(item for item in value["entries"] if item["id"] == "registry-component:flow-sequence")
    assert entry["routing"]["expects"] == ["Ordered step names and current step"]
    assert entry["parameters"]["required"] == ["data", "sourceNote", "title"]
    entry["interface"] = {
        "props": [{"name": "steps", "type": "array", "required": True, "nullable": False}],
        "eventTargets": ["step:active"],
    }
    assert entry["interface"]["props"][0]["name"] == "steps"
    assert "heroEligible" not in entry
    for fact in ("tags", "capabilities", "source", "integration", "parameters", "interface", "sha256", "license", "status"):
        assert fact in entry
    LIBRARY_VALIDATOR.validate(value)


def test_curation_candidate_accepts_explainable_non_numeric_audit() -> None:
    CURATION_VALIDATOR.validate(curation(candidate()))


def test_curation_v4_remains_a_runtime_migration_input() -> None:
    legacy = {
        "id": "registry-component:flow-sequence",
        "score": 7,
        "matchedSemanticTags": ["flow"],
        "selectionRole": "content",
        "provenance": {"catalogRevision": 14},
    }
    CURATION_VALIDATOR.validate(curation(legacy, version=4))


@pytest.mark.parametrize(
    "field",
    ["score", "matchedSemanticTags", "matchedNarrativeRole", "selectionRole", "granularity"],
)
def test_curation_candidate_rejects_legacy_weight_and_audit_fields(field: str) -> None:
    value = candidate()
    value[field] = 1 if field == "score" else "legacy"
    with pytest.raises(jsonschema.ValidationError):
        CURATION_VALIDATOR.validate(curation(value))


def test_storyboard_v2_legacy_schema_bytes_and_structure_are_unchanged() -> None:
    content = STORYBOARD_PATH.read_bytes()
    assert hashlib.sha256(content).hexdigest() == "570de77e000465fdc14839203b31e57ebbF2e6ef036153a795592db09d16d824".lower()
    schema = json.loads(content)
    assert schema["$defs"]["scene"]["required"]
    assert "candidates" not in json.dumps(schema)
