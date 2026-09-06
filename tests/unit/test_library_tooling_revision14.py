from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".agents/skills/hyperframes-curated-intake/scripts"
LIBRARY = ROOT / ".agents/skills/hyperframes-curated-intake/assets/library"
DIRECTING_FIELDS = ("family", "purpose", "useWhen", "avoidWhen", "expects", "motion")
PRESERVED_ROUTING_FIELDS = (*DIRECTING_FIELDS, "fallbackIds")


def load_script(name: str):
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(f"c2_{name.replace('-', '_')}", SCRIPTS / name)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


APPLY = load_script("apply-video-spec-refactor.py")
DIRECTOR = load_script("build-director-catalog.py")
REGISTRY = load_script("build-registry-view.py")
VERIFY = load_script("verify-library-contract.py")
ROUTING = load_script("_routing.py")


def directing(*, family: str = "process") -> dict:
    return {
        "family": family,
        "purpose": "Show a process changing state.",
        "useWhen": ["The audience must follow ordered progress."],
        "avoidWhen": ["Only a static identity mark is needed."],
        "expects": ["Named steps", "Current state"],
        "motion": "progressive",
    }


def target_entry(item_id: str = "registry-component:fixture") -> dict:
    routing = {
        **directing(),
        "teachingIntents": ["explain"],
        "cognitiveActions": ["trace"],
        "sceneRoles": ["bridge"],
        "evidenceTypes": ["text"],
        "requiredInputs": ["steps"],
        "styleFit": ["frame-governed"],
        "aspectFit": ["16:9"],
        "durationMin": 1,
        "durationMax": 5,
        "densityFit": ["comfortable"],
        "containerCost": 0,
        "heroEligible": True,
        "avoid": "Do not use for unrelated beats.",
        "fallbackIds": [],
    }
    return {
        "id": item_id,
        "kind": item_id.split(":", 1)[0],
        "title": "Fixture",
        "description": "Fixture entry.",
        "tags": ["process"],
        "capabilities": ["progress"],
        "routing": routing,
        "source": {"type": "bundle", "name": "fixture"},
        "integration": {"mode": "host-dom", "timelineOwner": "host", "renderTimeNetwork": False},
        "sha256": "0" * 64,
        "license": {"status": "local-reuse"},
        "status": "ready",
    }


@pytest.mark.parametrize(
    ("fallback_present", "fallback_value"),
    [
        (False, None),
        (True, []),
        (True, ["registry-component:marker-highlight", "legacy-alias", "registry-component:inline-highlight"]),
    ],
)
def test_read_only_refactor_preserves_directing_and_fallback_state(
    fallback_present: bool, fallback_value,
) -> None:
    entry = target_entry()
    if fallback_present:
        entry["routing"]["fallbackIds"] = fallback_value
    else:
        del entry["routing"]["fallbackIds"]
    before = copy.deepcopy(entry)
    report = APPLY.build_revision14_report([entry])
    expected = {
        field: before["routing"][field]
        for field in PRESERVED_ROUTING_FIELDS
        if field in before["routing"]
    }
    assert report["entries"][0]["preserved"] == expected
    assert entry == before
    assert APPLY.build_revision14_report([entry]) == report


def test_apply_refactor_reports_legacy_family_conflicts_without_slug_inference(tmp_path: Path) -> None:
    entry = target_entry("registry-component:flow-complex")
    entry["routing"] = {"family": "flow-complex", "requiredInputs": ["steps"]}
    entry["motionHooks"] = ["progress"]
    report = APPLY.build_revision14_report([entry])
    item = report["entries"][0]
    assert item["conflicts"] == [{
        "field": "family",
        "value": "flow-complex",
        "confidence": "low",
        "reason": "legacy family is outside the revision 14 enum; manual curation required",
    }]
    assert "family" not in item["suggestions"]
    assert item["suggestions"] == {}
    assert {"purpose", "useWhen", "avoidWhen"} <= set(item["manualRequired"])

    library = tmp_path / "library"
    library.mkdir()
    catalog_path = library / "catalog.json"
    catalog_path.write_text(json.dumps({"revision": 13, "entries": [entry]}), encoding="utf-8")
    before = catalog_snapshot(catalog_path)
    output = tmp_path / "proposal.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "apply-video-spec-refactor.py"), "--library", str(library), "--report", str(output)],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert catalog_snapshot(catalog_path) == before
    assert json.loads(output.read_text(encoding="utf-8"))["authoritative"] is False


def catalog_snapshot(path: Path) -> tuple[int, str, int, int]:
    content = path.read_bytes()
    value = json.loads(content)
    stat = path.stat()
    return len(content), hashlib.sha256(content).hexdigest(), stat.st_mtime_ns, value["revision"]


def run_refactor(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "apply-video-spec-refactor.py"), *args],
        cwd=cwd, capture_output=True, text=True, check=False,
    )


def test_refactor_cli_requires_one_read_only_operation_and_rejects_removed_mutations() -> None:
    for args in ((), ("--apply",), ("--promote",), ("--check", "--report", "proposal.json")):
        result = run_refactor(*args)
        assert result.returncode == 2


def test_refactor_check_cannot_write_default_canonical_catalog() -> None:
    catalog_path = LIBRARY / "catalog.json"
    before = catalog_snapshot(catalog_path)
    result = run_refactor("--check")
    assert result.returncode == 0
    assert catalog_snapshot(catalog_path) == before


def test_refactor_explicit_library_is_read_only_and_report_must_be_outside_it(tmp_path: Path) -> None:
    library = tmp_path / "library"
    library.mkdir()
    catalog_path = library / "catalog.json"
    catalog_path.write_text(json.dumps({"revision": 13, "entries": [target_entry()]}), encoding="utf-8")
    before = catalog_snapshot(catalog_path)

    checked = run_refactor("--library", str(library), "--check", cwd=tmp_path)
    assert checked.returncode == 0
    assert catalog_snapshot(catalog_path) == before

    blocked = library / "proposal.json"
    rejected = run_refactor("--library", str(library), "--report", str(blocked), cwd=tmp_path)
    assert rejected.returncode == 2
    assert not blocked.exists()
    assert catalog_snapshot(catalog_path) == before


def test_refactor_rejects_report_inside_default_canonical_library() -> None:
    blocked = LIBRARY / "revision14-proposal.json"
    assert not blocked.exists()
    result = run_refactor("--report", str(blocked))
    assert result.returncode == 2
    assert not blocked.exists()


def test_capability_enricher_only_adds_non_decision_capability_facts(tmp_path: Path) -> None:
    entry = target_entry("svg:primitive:document")
    entry["kind"] = "svg"
    entry["capabilities"] = ["local-file"]
    expected = copy.deepcopy({field: entry["routing"][field] for field in DIRECTING_FIELDS})
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"entries": [entry]}), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(SCRIPTS / "enrich-catalog-capabilities.py"), str(path)],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    enriched = json.loads(path.read_text(encoding="utf-8"))["entries"][0]
    assert {field: enriched["routing"][field] for field in DIRECTING_FIELDS} == expected
    assert {"local-file", "select", "fold", "carry", "split"} == set(enriched["capabilities"])
    for field in ("motionHooks", "supports", "compatibleRecipes", "affordances", "avoid", "heroEligible"):
        assert field not in enriched


def test_director_projection_copies_catalog_directing_only_and_does_not_fabricate_talkcraft(tmp_path: Path) -> None:
    library = tmp_path / "library"
    (library / "candidates/talkcraft/global-systems").mkdir(parents=True)
    (library / "candidates/talkcraft/global-systems/talkcraft-systems.js").write_text("export {};", encoding="utf-8")
    entry = target_entry()
    (library / "catalog.json").write_text(json.dumps({
        "schemaVersion": "hyperframes-directed-video-library/v1", "revision": 14, "entries": [entry]
    }), encoding="utf-8")
    (library / "talkcraft-inventory.json").write_text(json.dumps({
        "source": {"commit": "fixture"},
        "entries": [{"id": "talkcraft:fixture", "kind": "layer", "tags": ["motion"], "capabilities": []}],
    }), encoding="utf-8")
    output = DIRECTOR.build(library)
    projected = next(item for item in output["entries"] if item["id"] == entry["id"])
    assert {field: projected["routing"][field] for field in DIRECTING_FIELDS} == {
        field: entry["routing"][field] for field in DIRECTING_FIELDS
    }
    talkcraft = next(item for item in output["entries"] if item["id"] == "talkcraft:fixture")
    assert "routing" not in talkcraft
    assert not any(field in talkcraft for field in DIRECTING_FIELDS)


def test_registry_projection_preserves_directing_and_legacy_geometry_without_install_drift(tmp_path: Path) -> None:
    library = tmp_path / "library"
    source = library / "source/fixture.html"
    source.parent.mkdir(parents=True)
    source.write_text('<div data-width="1920" data-height="1080" data-duration="5"></div>', encoding="utf-8")
    entry = target_entry("registry-block:fixture")
    entry["source"] = {
        "type": "bundle", "name": "fixture", "entry": "source/fixture.html",
        "files": [{"path": "source/fixture.html", "target": "fixture.html", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}],
    }
    (library / "catalog.json").write_text(json.dumps({
        "schemaVersion": "hyperframes-directed-video-library/v1", "revision": 14, "entries": [entry]
    }), encoding="utf-8")
    output = tmp_path / "registry"
    report, code = REGISTRY.build(library, output, "fixture", "https://example.invalid")
    assert code == 0, report
    item_path = output / "blocks/fixture/registry-item.json"
    item = json.loads(item_path.read_text(encoding="utf-8"))
    expected = {field: entry["routing"][field] for field in (*DIRECTING_FIELDS, "fallbackIds")}
    assert item["routing"] == expected
    assert item["dimensions"] == {"width": 1920, "height": 1080}
    assert item["duration"] == 5
    first = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    REGISTRY.build(library, output, "fixture", "https://example.invalid")
    second = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    assert second == first


def revision14_entries() -> list[dict]:
    counts = {"registry-block": 48, "registry-component": 123, "svg": 31, "lottie": 30}
    entries = []
    for kind, count in counts.items():
        for index in range(count):
            entries.append({
                "id": f"{kind}:fixture-{index}",
                "kind": kind,
                "status": "ready",
                "routing": {**directing(), "fallbackIds": []},
            })
    return entries


def verify(entries: list[dict]) -> list[str]:
    errors, summary = VERIFY.validate_directed_revision(entries, {entry["id"]: entry for entry in entries}, 15)
    assert summary["targetEntries"] == 232
    return errors


def test_revision14_verifier_accepts_complete_cohort() -> None:
    entries = revision14_entries()
    assert verify(entries) == []


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("purpose", None, "fields missing"),
        ("purpose", "placeholder", "invalid purpose"),
        ("family", "flow", "invalid family"),
        ("motion", "loop", "invalid motion"),
        ("useWhen", [], "invalid useWhen"),
        ("avoidWhen", ["same", "same"], "invalid avoidWhen"),
        ("expects", ["TBD"], "invalid expects"),
    ],
)
def test_revision14_verifier_reports_missing_enum_placeholder_and_array_errors(field: str, value, message: str) -> None:
    entries = revision14_entries()
    if value is None:
        del entries[0]["routing"][field]
    else:
        entries[0]["routing"][field] = value
    assert any(message in error for error in verify(entries))


def test_revision14_verifier_checks_fallback_exists_ready_and_same_family() -> None:
    entries = revision14_entries()
    entries[0]["routing"]["fallbackIds"] = ["registry-component:fixture-0"]
    assert verify(entries) == []

    entries[1]["routing"]["fallbackIds"] = ["registry-component:missing"]
    assert any("dangling fallback" in error for error in verify(entries))
    entries[1]["routing"]["fallbackIds"] = ["registry-component:fixture-1"]
    peer = next(entry for entry in entries if entry["id"] == "registry-component:fixture-1")
    peer["status"] = "disabled"
    assert any("non-ready fallback" in error for error in verify(entries))
    peer["status"] = "ready"
    peer["routing"]["family"] = "data"
    assert any("fallback family mismatch" in error for error in verify(entries))


def test_legacy_router_output_is_unchanged_by_idempotent_catalog_enrichment() -> None:
    catalog = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
    entries = [copy.deepcopy(entry) for entry in catalog["entries"] if entry["id"] in {
        "registry-component:flow-complex", "registry-component:flow-branching"
    }]
    context = {
        "selection_role": "content", "available_inputs": ["steps"], "aspect": "16:9",
        "duration_seconds": 2, "semantic_tags": ["flow"], "narrative_role": "bridge", "granularity": "element",
    }
    installable = {(entry["source"]["name"], "hyperframes:component") for entry in entries}
    before = ROUTING.recommend(entries, context, installable_registry=installable)
    report = APPLY.build_revision14_report(entries)
    after = ROUTING.recommend(entries, context, installable_registry=installable)
    assert after == before
    assert report == APPLY.build_revision14_report(entries)


def test_no_revision14_proposal_or_overlay_is_committed() -> None:
    names = {path.name for path in ROOT.rglob("*.json") if ".git" not in path.parts}
    assert "revision14-proposal.json" not in names
    assert "directing-overlay.json" not in names
