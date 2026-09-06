from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / ".agents/skills/hyperframes-curated-intake/assets/library"
TARGET_COUNTS = {"registry-block": 48, "registry-component": 123, "svg": 31, "lottie": 30}
DIRECTING_FIELDS = ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion")


@pytest.fixture(scope="module")
def entries() -> dict[str, dict]:
    catalog = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
    assert catalog["revision"] == 15
    return {entry["id"]: entry for entry in catalog["entries"]}


def test_exact_curated_cohorts_and_non_target_boundaries(entries: dict[str, dict]) -> None:
    counts = {kind: 0 for kind in TARGET_COUNTS}
    light = 0
    out_of_scope = 0
    for entry in entries.values():
        kind = entry["kind"]
        if kind in counts:
            counts[kind] += 1
            assert all(field in entry["routing"] for field in DIRECTING_FIELDS)
        elif kind in {"logo", "font", "sfx", "background", "texture"}:
            light += 1
            assert not any(field in entry.get("routing", {}) for field in DIRECTING_FIELDS)
        elif kind in {"motion-rule", "scene-blueprint", "transition"}:
            out_of_scope += 1
    assert counts == TARGET_COUNTS
    assert light == 111
    assert out_of_scope == 13


@pytest.mark.parametrize(
    ("item_id", "family", "motion", "expected_input", "avoid_fragment"),
    [
        ("registry-component:chart-line", "data", "progressive", "Ordered points", "unordered categories"),
        ("registry-component:flow-state-machine", "process", "stateful", "transition triggers", "persistent state"),
        ("registry-component:structure-node-graph", "structure", "stateful", "Nodes, links", "simple tree"),
        ("registry-component:structure-matrix-2x2", "compare", "stateful", "Axis labels", "continuous"),
        ("registry-component:ui-terminal", "interface", "stateful", "Commands, outputs", "command text"),
        ("registry-component:abstract-black-box", "concept", "stateful", "Named inputs", "internal mechanism"),
        ("registry-component:inline-highlight", "emphasis", "stateful", "Text range", "whole sentence"),
        ("registry-component:pointer-proof", "evidence", "stateful", "Source media", "located reliably"),
    ],
)
def test_real_catalog_choices_cover_every_family_and_input_avoid_contract(
    entries: dict[str, dict], item_id: str, family: str, motion: str,
    expected_input: str, avoid_fragment: str,
) -> None:
    entry = entries[item_id]
    routing = entry["routing"]
    assert entry["status"] == "ready"
    assert routing["family"] == family
    assert routing["motion"] == motion
    assert expected_input.lower() in routing["expects"][0].lower()
    assert avoid_fragment.lower() in routing["avoidWhen"][0].lower()


@pytest.mark.parametrize(
    ("item_id", "family", "motion"),
    [
        ("registry-block:testimonial-proof-card", "evidence", "entrance-only"),
        ("lottie:trace-progress", "process", "progressive"),
        ("svg:lucide:mouse-pointer-click", "interface", "stateful"),
    ],
)
def test_all_motion_levels_and_primitive_kinds_are_real_ready_choices(
    entries: dict[str, dict], item_id: str, family: str, motion: str,
) -> None:
    entry = entries[item_id]
    assert entry["status"] == "ready"
    assert entry["routing"]["family"] == family
    assert entry["routing"]["motion"] == motion
    source = entry["source"]
    path = source.get("path") or source.get("entry")
    assert path and (LIBRARY / path).is_file()


def test_curated_fallbacks_are_ready_same_family_neighbours(entries: dict[str, dict]) -> None:
    expected = {
        "lottie:trace-progress": "lottie:progress-pill-sweep",
        "registry-component:chart-bar": "registry-component:chart-horizontal-bar",
        "registry-component:flow-sequence": "registry-component:step-chain",
        "registry-component:ui-terminal": "registry-component:ui-code-editor",
        "svg:lucide:terminal": "svg:command-line",
    }
    actual = {
        item_id: entry["routing"]["fallbackIds"][0]
        for item_id, entry in entries.items()
        if entry["kind"] in TARGET_COUNTS and "fallbackIds" in entry.get("routing", {})
    }
    assert actual == expected
    for item_id, fallback_id in actual.items():
        assert entries[fallback_id]["status"] == "ready"
        assert entries[fallback_id]["kind"] in TARGET_COUNTS
        assert entries[fallback_id]["routing"]["family"] == entries[item_id]["routing"]["family"]


def test_current_director_and_registry_views_copy_catalog_authority(entries: dict[str, dict]) -> None:
    director = json.loads((LIBRARY / "director-catalog.json").read_text(encoding="utf-8"))
    director_entries = {entry["id"]: entry for entry in director["entries"]}
    for item_id, entry in entries.items():
        if entry["kind"] not in TARGET_COUNTS:
            continue
        fields = (*DIRECTING_FIELDS, "fallbackIds")
        expected = {field: entry["routing"][field] for field in fields if field in entry["routing"]}
        assert {field: director_entries[item_id]["routing"][field] for field in expected} == expected

    for item_id, entry in entries.items():
        if entry["kind"] not in {"registry-block", "registry-component"} or entry["status"] != "ready":
            continue
        collection = "blocks" if entry["kind"] == "registry-block" else "components"
        name = entry["source"]["name"]
        item = json.loads((LIBRARY / f"registry/{collection}/{name}/registry-item.json").read_text(encoding="utf-8"))
        expected = {
            field: entry["routing"][field]
            for field in (*DIRECTING_FIELDS, "fallbackIds")
            if field in entry["routing"]
        }
        assert item["routing"] == expected
