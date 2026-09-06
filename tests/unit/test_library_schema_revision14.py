from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schemas/library.schema.json").read_text(encoding="utf-8"))
CATALOG = json.loads(
    (ROOT / ".agents/skills/hyperframes-curated-intake/assets/library/catalog.json").read_text(encoding="utf-8")
)
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)

TARGET_KINDS = {"registry-block", "registry-component", "svg", "lottie"}
LIGHT_KINDS = {"logo", "font", "sfx", "background", "texture"}
OUT_OF_SCOPE_KINDS = {"motion-rule", "scene-blueprint", "transition"}


def routing() -> dict:
    return {
        "family": "process",
        "purpose": "Show how a decision advances through a sequence.",
        "useWhen": ["A sequence has at least two meaningful states."],
        "avoidWhen": ["The content is a static identity asset."],
        "expects": ["Named steps and the current state."],
        "motion": "progressive",
        "fallbackIds": ["registry-component:flow-complex"],
        "teachingIntents": ["explain"],
    }


def entry(kind: str, *, with_routing: bool = False) -> dict:
    value = {
        "id": f"{kind}:fixture",
        "kind": kind,
        "title": "Fixture",
        "tags": [],
        "capabilities": [],
        "source": {"type": "fixture"},
        "integration": {"mode": "inline", "timelineOwner": "host", "renderTimeNetwork": False},
        "sha256": "0" * 64,
        "license": {"status": "local-reuse"},
        "status": "ready",
    }
    if with_routing:
        value["routing"] = routing()
    return value


def catalog(item: dict, *, revision: int = 14) -> dict:
    return {
        "schemaVersion": "hyperframes-directed-video-library/v1",
        "revision": revision,
        "entries": [item],
    }


def assert_valid(value: dict) -> None:
    VALIDATOR.validate(value)


def assert_invalid(value: dict) -> None:
    with pytest.raises(jsonschema.ValidationError):
        VALIDATOR.validate(value)


def test_revision_15_canonical_and_revision_14_13_migration_inputs_remain_valid_with_frozen_cohorts() -> None:
    assert CATALOG["revision"] == 15
    assert_valid(CATALOG)
    counts = Counter(item["kind"] for item in CATALOG["entries"])
    assert {kind: counts[kind] for kind in TARGET_KINDS} == {
        "registry-block": 48,
        "registry-component": 123,
        "svg": 31,
        "lottie": 30,
    }
    assert {kind: counts[kind] for kind in LIGHT_KINDS} == {
        "logo": 95,
        "font": 8,
        "sfx": 3,
        "background": 4,
        "texture": 1,
    }
    assert {kind: counts[kind] for kind in OUT_OF_SCOPE_KINDS} == {
        "motion-rule": 4,
        "scene-blueprint": 4,
        "transition": 5,
    }
    revision14_input = copy.deepcopy(CATALOG)
    revision14_input["revision"] = 14
    assert_valid(revision14_input)
    revision13_input = copy.deepcopy(CATALOG)
    revision13_input["revision"] = 13
    for item in revision13_input["entries"]:
        if item["kind"] in TARGET_KINDS:
            for field in ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion", "fallbackIds"):
                item.get("routing", {}).pop(field, None)
    assert_valid(revision13_input)


@pytest.mark.parametrize("kind", sorted(TARGET_KINDS))
def test_revision_14_target_kinds_accept_the_six_field_contract_and_legacy_routing_fields(kind: str) -> None:
    assert_valid(catalog(entry(kind, with_routing=True)))


@pytest.mark.parametrize("field", ["family", "purpose", "useWhen", "avoidWhen", "expects", "motion"])
def test_revision_14_target_kinds_reject_each_missing_directing_field(field: str) -> None:
    value = catalog(entry("registry-block", with_routing=True))
    del value["entries"][0]["routing"][field]
    assert_invalid(value)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [("family", "narrative"), ("motion", "looping")],
)
def test_revision_14_rejects_unknown_family_and_motion_values(field: str, invalid: str) -> None:
    value = catalog(entry("registry-component", with_routing=True))
    value["entries"][0]["routing"][field] = invalid
    assert_invalid(value)


@pytest.mark.parametrize("field", ["useWhen", "avoidWhen", "expects"])
def test_revision_14_rejects_empty_directing_arrays(field: str) -> None:
    value = catalog(entry("svg", with_routing=True))
    value["entries"][0]["routing"][field] = []
    assert_invalid(value)


@pytest.mark.parametrize("field", ["useWhen", "avoidWhen", "expects"])
def test_revision_14_rejects_duplicate_directing_array_items(field: str) -> None:
    value = catalog(entry("lottie", with_routing=True))
    value["entries"][0]["routing"][field] = ["Repeated", "Repeated"]
    assert_invalid(value)


@pytest.mark.parametrize("field", ["purpose", "useWhen", "avoidWhen", "expects"])
def test_revision_14_rejects_empty_whitespace_and_placeholder_text(field: str) -> None:
    for text in ("", "   ", "placeholder", "Placeholder", "TBD", "todo", "N/A", "待定", "占位"):
        value = catalog(entry("registry-block", with_routing=True))
        value["entries"][0]["routing"][field] = text if field == "purpose" else [text]
        assert_invalid(value)


@pytest.mark.parametrize("kind", sorted(LIGHT_KINDS))
def test_revision_14_light_identity_assets_pass_without_directing_metadata(kind: str) -> None:
    assert_valid(catalog(entry(kind)))


@pytest.mark.parametrize("kind", sorted(OUT_OF_SCOPE_KINDS))
def test_revision_14_out_of_scope_contracts_pass_unchanged(kind: str) -> None:
    assert_valid(catalog(entry(kind)))


def test_revision_14_rejects_unknown_top_level_and_parallel_directing_metadata() -> None:
    unknown_top = catalog(entry("registry-block", with_routing=True))
    unknown_top["directing"] = {}
    assert_invalid(unknown_top)

    parallel_entry = catalog(entry("registry-block", with_routing=True))
    parallel_entry["entries"][0]["directing"] = routing()
    assert_invalid(parallel_entry)


def test_revision_14_optional_fallback_ids_require_unique_catalog_id_shapes() -> None:
    valid = catalog(entry("registry-component", with_routing=True))
    assert_valid(valid)

    for invalid in (
        "registry-component:flow-complex",
        ["registry-component:flow-complex", "registry-component:flow-complex"],
        ["not-an-id"],
    ):
        value = copy.deepcopy(valid)
        value["entries"][0]["routing"]["fallbackIds"] = invalid
        assert_invalid(value)
