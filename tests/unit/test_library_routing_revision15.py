from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/hyperframes-curated-intake"
SCRIPTS = SKILL / "scripts"
LIBRARY = SKILL / "assets/library"
OLD_FIELDS = {
    "semantic_tags", "narrative_roles", "granularity", "selection_role", "motionHooks", "supports",
    "compatibleRecipes", "affordances", "heroEligible", "teachingIntents", "cognitiveActions",
    "sceneRoles", "evidenceTypes", "requiredInputs", "styleFit", "aspectFit", "densityFit",
    "containerCost", "durationMin", "durationMax", "matchedSemanticTags", "matchedNarrativeRole", "score",
}


def load_script(filename: str):
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location("d2_" + filename.replace("-", "_"), SCRIPTS / filename)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


ROUTING = load_script("_routing.py")
PALETTE = load_script("select-project-palette.py")
CURATION = load_script("_curation.py")


def directing(
    *, family: str = "data", purpose: str = "Explain measured change",
    use_when: str = "A measured change needs evidence", motion: str = "stateful",
) -> dict:
    return {
        "family": family, "purpose": purpose, "useWhen": [use_when],
        "avoidWhen": ["The claim has no evidence"], "expects": ["A supported claim"], "motion": motion,
    }


def entry(item_id: str, *, family: str = "data", purpose: str = "Explain measured change",
          use_when: str = "A measured change needs evidence", motion: str = "stateful",
          status: str = "ready", kind: str = "registry-component") -> dict:
    name = item_id.split(":")[-1]
    if kind.startswith("registry-"):
        source = {"type": "bundle", "name": name, "entry": f"{name}.js", "files": [{"path": f"{name}.js", "sha256": "0" * 64}]}
    else:
        source = {"type": "file", "path": f"media/{name}.json"}
    return {
        "id": item_id, "kind": kind, "title": name, "tags": [], "capabilities": [], "status": status,
        "source": source, "sha256": "0" * 64,
        "license": {"status": "local-reuse"},
        "integration": {"mode": "host-dom", "timelineOwner": "host", "renderTimeNetwork": False},
        "parameters": {"required": ["data"]},
        "aspectSupport": ["16:9"], "dimensions": {"width": 1920, "height": 1080},
        "duration": 8, "fps": 60,
        "routing": directing(family=family, purpose=purpose, use_when=use_when, motion=motion),
    }


def context(**changes) -> dict:
    value = {
        "family": "data", "purpose": "Explain measured change",
        "useWhen": ["A measured change needs evidence"], "available_inputs": ["data"],
        "aspect": "16:9", "dimensions": {"width": 1920, "height": 1080},
        "duration_seconds": 5, "fps": 60,
    }
    value.update(changes)
    return value


def installable(*entries: dict) -> set[tuple[str, str]]:
    return {
        (item["source"]["name"], "hyperframes:component") for item in entries
        if item["kind"] == "registry-component" and isinstance(item.get("source"), dict) and item["source"].get("name")
    }


def test_legacy_decision_perturbations_are_inert_but_six_fields_change_selection() -> None:
    first = entry("registry-component:a")
    second = entry("registry-component:b", family="concept", purpose="Explain a concept", use_when="A concept needs a model")
    baseline = ROUTING.recommend([second, first], context(), installable_registry=installable(first, second))
    assert baseline["selected"] == first["id"]
    altered = copy.deepcopy([second, first])
    for index, item in enumerate(altered):
        item.update({"semantic_tags": ["evidence"], "narrative_roles": ["hook"], "granularity": "scene", "selection_role": "motion", "heroEligible": index == 0})
        item["routing"].update({"requiredInputs": ["impossible"], "aspectFit": ["9:16"], "durationMin": 99, "durationMax": 100, "heroEligible": index == 0})
    assert ROUTING.recommend(altered, context(), installable_registry=installable(*altered))["selected"] == first["id"]
    altered[0]["routing"].update(directing())
    altered[1]["routing"].update(directing(family="concept"))
    assert ROUTING.recommend(altered, context(), installable_registry=installable(*altered))["selected"] == second["id"]


def test_lexicographic_levels_precede_motion_repetition_and_id() -> None:
    family = entry("registry-component:z-family", purpose="other", use_when="other", motion="entrance-only")
    use = entry("registry-component:a-use", family="concept", purpose="other", motion="stateful")
    use["routing"]["useWhen"] = context()["useWhen"]
    result = ROUTING.recommend([use, family], context(), installable_registry=installable(use, family), prior_use={family["id"]: 99})
    assert result["selected"] == family["id"], "family must outrank every later level"

    purpose = entry("registry-component:a-purpose", family="data", use_when="other", motion="stateful")
    use_same_family = entry("registry-component:z-use", family="data", purpose="other", motion="entrance-only")
    use_same_family["routing"]["useWhen"] = context()["useWhen"]
    result = ROUTING.recommend([purpose, use_same_family], context(), installable_registry=installable(purpose, use_same_family))
    assert result["selected"] == use_same_family["id"], "useWhen must outrank purpose"

    progressive = entry("registry-component:z-progressive", motion="progressive")
    entrance = entry("registry-component:a-entrance", motion="entrance-only")
    long_result = ROUTING.recommend([entrance, progressive], context(), installable_registry=installable(entrance, progressive))
    short_result = ROUTING.recommend([entrance, progressive], context(duration_seconds=3), installable_registry=installable(entrance, progressive))
    assert long_result["selected"] == progressive["id"]
    assert short_result["selected"] == entrance["id"]


def test_machine_inputs_come_only_from_parameters_and_required_interface_props() -> None:
    item = entry("registry-component:inputs")
    item["routing"]["expects"] = ["A semantic explanation unlike any machine prop"]
    item["interface"] = {"props": [{"name": "label", "type": "string", "required": True, "nullable": False}]}
    passed = ROUTING.recommend([item], context(available_inputs=["data", "label"]), installable_registry=installable(item))
    assert passed["status"] == "recommended"
    failed = ROUTING.recommend([item], context(available_inputs=["A semantic explanation unlike any machine prop"]), installable_registry=installable(item))
    gate = next(result for result in failed["rejections"][0]["hardFilterResults"] if result["filter"] == "required_inputs")
    assert gate == {"filter": "required_inputs", "passed": False, "detail": "missing=data,label"}


@pytest.mark.parametrize(
    ("gate", "mutate", "candidate_context", "registry"),
    [
        ("status", lambda item: item.update(status="disabled"), {}, "normal"),
        ("license", lambda item: item.update(license={"status": "restricted"}), {}, "normal"),
        ("source", lambda item: item.update(source={}), {}, "normal"),
        ("hash", lambda item: item.update(sha256="bad"), {}, "normal"),
        ("integration", lambda item: item.update(integration={"mode": "host-dom", "renderTimeNetwork": True}), {}, "normal"),
        ("aspect", lambda item: None, {"aspect": "9:16"}, "normal"),
        ("dimensions", lambda item: None, {"dimensions": {"width": 1080, "height": 1920}}, "normal"),
        ("duration", lambda item: item.update(duration=4), {"duration_seconds": 5}, "normal"),
        ("fps", lambda item: None, {"fps": 30}, "normal"),
        ("installable", lambda item: None, {}, "empty"),
    ],
)
def test_each_machine_fact_is_a_hard_gate(gate, mutate, candidate_context, registry) -> None:
    item = entry("registry-component:gate")
    mutate(item)
    result = ROUTING.recommend(
        [item], context(**candidate_context),
        installable_registry=set() if registry == "empty" else installable(item),
    )
    assert result["status"] == "no_recommendation"
    failed = {record["filter"] for record in result["rejections"][0]["hardFilterResults"] if not record["passed"]}
    assert gate in failed


def test_runtime_integration_sets_are_derived_exactly_from_the_authoritative_schema() -> None:
    schema = json.loads((ROOT / "schemas/library.schema.json").read_text(encoding="utf-8"))
    contract = schema["$defs"]["entry"]["properties"]["integration"]
    properties = contract["properties"]
    assert ROUTING.INTEGRATION_MODES == frozenset(properties["mode"]["enum"])
    assert ROUTING.TIMELINE_OWNERS == frozenset(properties["timelineOwner"]["enum"])
    assert ROUTING.INTEGRATION_REQUIRED == frozenset(contract["required"])
    assert ROUTING.INTEGRATION_FIELDS == frozenset(properties)


@pytest.mark.parametrize("field", ["mode", "timelineOwner", "renderTimeNetwork"])
def test_integration_gate_rejects_each_missing_required_field(field: str) -> None:
    item = entry("registry-component:integration")
    del item["integration"][field]
    result = ROUTING.recommend([item], context(), installable_registry=installable(item))
    assert "integration" in {record["filter"] for record in result["rejections"][0]["hardFilterResults"] if not record["passed"]}


@pytest.mark.parametrize("field", ["mode", "timelineOwner"])
@pytest.mark.parametrize("value", ["", "unknown", None, 1, True, {}, []])
def test_integration_gate_rejects_every_invalid_enum_shape(field: str, value) -> None:
    item = entry("registry-component:integration")
    item["integration"][field] = value
    result = ROUTING.recommend([item], context(), installable_registry=installable(item))
    assert "integration" in {record["filter"] for record in result["rejections"][0]["hardFilterResults"] if not record["passed"]}


@pytest.mark.parametrize("value", [True, "false", "", None, 0, 1, {}, []])
def test_integration_gate_requires_render_time_network_to_be_literal_false(value) -> None:
    item = entry("registry-component:integration")
    item["integration"]["renderTimeNetwork"] = value
    result = ROUTING.recommend([item], context(), installable_registry=installable(item))
    assert "integration" in {record["filter"] for record in result["rejections"][0]["hardFilterResults"] if not record["passed"]}


def test_integration_gate_rejects_unknown_keys() -> None:
    item = entry("registry-component:integration")
    item["integration"]["unknown"] = "value"
    result = ROUTING.recommend([item], context(), installable_registry=installable(item))
    assert "integration" in {record["filter"] for record in result["rejections"][0]["hardFilterResults"] if not record["passed"]}


def test_load_catalog_validates_the_complete_root_schema_with_actionable_configuration_error(tmp_path: Path) -> None:
    library = tmp_path / "library"
    library.mkdir()
    item = entry("registry-component:fixture")
    catalog = {"schemaVersion": "hyperframes-directed-video-library/v1", "revision": 14, "entries": [item]}
    path = library / "catalog.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    loaded, name = CURATION.load_catalog(library)
    assert loaded == catalog and name == "catalog.json"

    del catalog["entries"][0]["integration"]["timelineOwner"]
    path.write_text(json.dumps(catalog), encoding="utf-8")
    with pytest.raises(ValueError) as caught:
        CURATION.load_catalog(library)
    message = str(caught.value)
    assert "Catalog configuration error" in message
    assert "entry=registry-component:fixture" in message
    assert f"path={path}#/entries/0/integration" in message
    assert "field=timelineOwner" in message


@pytest.mark.parametrize("payload", [None, [], {}, {"schemaVersion": "unknown", "revision": 14, "entries": []}])
def test_load_catalog_reports_every_invalid_document_as_configuration_error(tmp_path: Path, payload) -> None:
    library = tmp_path / "library"
    library.mkdir()
    path = library / "catalog.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError) as caught:
        CURATION.load_catalog(library)
    message = str(caught.value)
    assert "Catalog configuration error" in message
    assert "entry=<catalog>" in message
    assert f"path={path}#/" in message
    assert "field=" in message


def test_source_bytes_are_hashed_when_a_library_root_is_available(tmp_path: Path) -> None:
    item = entry("svg:verified", kind="svg")
    source = tmp_path / item["source"]["path"]
    source.parent.mkdir(parents=True)
    source.write_bytes(b"verified")
    digest = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
    item["sha256"] = digest
    verified_context = context(_library=str(tmp_path))
    assert ROUTING.recommend([item], verified_context)["selected"] == item["id"]
    source.write_bytes(b"drifted")
    result = ROUTING.recommend([item], verified_context)
    failed = {record["filter"] for record in result["rejections"][0]["hardFilterResults"] if not record["passed"]}
    assert "hash" in failed


def test_explicit_avoid_conflict_excludes_and_unknown_is_retained() -> None:
    first = entry("registry-component:a")
    second = entry("registry-component:b")
    unknown = ROUTING.recommend([first], context(), installable_registry=installable(first))
    assert unknown["selected"] == first["id"]
    blocked = ROUTING.recommend([first, second], context(avoidConflicts={first["id"]: "known contradiction"}), installable_registry=installable(first, second))
    assert blocked["selected"] == second["id"]
    assert blocked["rejections"][0]["avoidConflicts"] == ["known contradiction"]


def test_hero_uses_semantic_emphasis_and_never_legacy_flag() -> None:
    old_flag = entry("registry-component:a")
    old_flag["heroEligible"] = True
    old_flag["routing"]["heroEligible"] = True
    miss = ROUTING.recommend([old_flag], context(hero_required=True), installable_registry=installable(old_flag))
    assert miss["status"] == "no_recommendation"
    hero = entry("registry-component:hero", family="emphasis")
    hit = ROUTING.recommend([hero], context(hero_required=True, family="emphasis"), installable_registry=installable(hero))
    assert hit["selected"] == hero["id"]


def test_explicit_lock_bypasses_ranking_and_disabled_fallbacks_follow_declared_order() -> None:
    locked = entry("registry-component:locked", family="concept")
    better = entry("registry-component:better")
    index = {item["id"]: item for item in (locked, better)}
    selected, candidates, _, _ = PALETTE.explicit_choice(locked["id"], index, context(), installable(locked, better), {}, set())
    assert selected == locked["id"] and [item["id"] for item in candidates] == [locked["id"]]

    disabled = entry("registry-component:disabled", status="disabled")
    bad = entry("registry-component:bad")
    bad["license"] = {"status": "restricted"}
    good = entry("registry-component:good")
    disabled["routing"]["fallbackIds"] = [bad["id"], good["id"]]
    index = {item["id"]: item for item in (disabled, bad, good)}
    selected, candidates, rejected, _ = PALETTE.explicit_choice(disabled["id"], index, context(), installable(disabled, bad, good), {}, set())
    assert selected == good["id"]
    assert candidates[0]["fallbackTrace"] == [disabled["id"], bad["id"], good["id"]]
    assert [item["id"] for item in rejected] == [disabled["id"], bad["id"]]
    disabled["routing"]["fallbackIds"] = []
    assert PALETTE.explicit_choice(disabled["id"], index, context(), installable(disabled, bad, good), {}, set())[0] is None

    svg = entry("svg:locked", kind="svg")
    logo = entry("logo:locked", kind="logo")
    for item in (svg, logo):
        selected, candidates, _, _ = PALETTE.explicit_choice(item["id"], {item["id"]: item}, context(), None, {}, set())
        assert selected == item["id"] and [candidate["id"] for candidate in candidates] == [item["id"]]


def test_v5_audit_is_schema_valid_nonnumeric_and_idempotent() -> None:
    item = entry("registry-component:a")
    one = ROUTING.recommend([item], context(), installable_registry=installable(item))
    two = ROUTING.recommend([copy.deepcopy(item)], copy.deepcopy(context()), installable_registry=installable(item))
    assert one == two
    candidate = one["candidates"][0]
    assert not (OLD_FIELDS & set(candidate))
    schema = json.loads((SKILL / "references/curation.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema["$defs"]["candidateAudit"]).validate(candidate)


def test_all_61_primitives_have_six_field_authority_and_staging_regression_passes() -> None:
    catalog = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
    primitives = [item for item in catalog["entries"] if item.get("kind") in {"svg", "lottie"}]
    assert len(primitives) == 61
    assert all(set(("family", "purpose", "useWhen", "avoidWhen", "expects", "motion")) <= set(item["routing"]) for item in primitives)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/test_curated_intake_workflow.py::test_prepare_stages_registry_svg_and_lottie_with_hashes", "-q"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_talkcraft_lock_passes_through_without_metadata_or_mixed_ranking() -> None:
    selected, candidates, rejected, reason = PALETTE.explicit_choice(
        "talkcraft:locked-card", {}, context(), None, {}, set(),
    )
    assert selected == "talkcraft:locked-card"
    assert candidates == [] and rejected == []
    assert "without synthesized metadata" in reason


def test_production_router_sources_do_not_reference_legacy_decision_fields() -> None:
    production = [
        SCRIPTS / "_routing.py", SCRIPTS / "_capabilities.py", SCRIPTS / "apply-video-spec-refactor.py",
        SCRIPTS / "build-registry-view.py", SCRIPTS / "verify-library-contract.py",
    ]
    for path in production:
        text = path.read_text(encoding="utf-8")
        assert not (OLD_FIELDS & set(__import__("re").findall(r"[A-Za-z_][A-Za-z0-9_]*", text))), path
    palette_text = (SCRIPTS / "select-project-palette.py").read_text(encoding="utf-8")
    forbidden = OLD_FIELDS - {"affordances"}
    assert not (forbidden & set(__import__("re").findall(r"[A-Za-z_][A-Za-z0-9_]*", palette_text)))
