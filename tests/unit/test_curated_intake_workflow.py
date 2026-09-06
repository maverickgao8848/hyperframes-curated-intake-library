from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/hyperframes-curated-intake"
SCRIPTS = SKILL / "scripts"
FIXTURES = ROOT / "tests/fixtures"
sys.path.insert(0, str(SCRIPTS))


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


PALETTE = load_script("select-project-palette.py")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(name: str, *args: object, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)], cwd=ROOT, capture_output=True, text=True, check=check)


def make_library(tmp_path: Path) -> Path:
    library = tmp_path / "library"
    files = {
        "frames/cobalt/FRAME.md": "---\nname: Cobalt\n---\n# Frame\n",
        "registry/components/trace-line.html": '<div id="trace-line"></div>',
        "media/svg/document.svg": '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>',
        "media/lottie/pulse.json": '{"v":"5.0"}',
    }
    for relative, content in files.items():
        path = library / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    frame_path = library / "frames/cobalt/FRAME.md"
    (library / "frames/inventory.json").write_text(json.dumps({"schemaVersion": "mav-hyperframes-frame-inventory/v1", "frames": [{"preset": "cobalt", "path": "frames/cobalt/FRAME.md", "sha256": digest(frame_path)}]}), encoding="utf-8")
    (library / "registry").mkdir(exist_ok=True)
    (library / "registry/registry.json").write_text(json.dumps({"items": [{"name": "trace-line", "type": "hyperframes:component"}]}), encoding="utf-8")
    entries = []
    for item_id, kind, relative, affordances in (
        ("registry-component:trace-line", "registry-component", "registry/components/trace-line.html", ["trace"]),
        ("svg:primitive:document", "svg", "media/svg/document.svg", ["select", "fold", "carry"]),
        ("lottie:pulse", "lottie", "media/lottie/pulse.json", ["pulse", "signal"]),
    ):
        source = {"type": "bundle", "name": item_id.split(":")[-1], "entry": relative, "files": [{"path": relative, "target": Path(relative).name, "sha256": digest(library / relative)}]} if kind.startswith("registry-") else {"type": "file", "path": relative}
        entries.append({"id": item_id, "kind": kind, "title": item_id, "description": " ".join(affordances), "tags": affordances, "capabilities": affordances, "affordances": affordances, "source": source, "integration": {"mode": "inline", "timelineOwner": "host", "renderTimeNetwork": False}, "sha256": digest(library / relative), "license": {"status": "local-reuse"}, "status": "ready"})
    (library / "catalog.json").write_text(json.dumps({"schemaVersion": "hyperframes-directed-video-library/v1", "revision": 1, "entries": entries}), encoding="utf-8")
    return library


def make_storyboard(tmp_path: Path) -> Path:
    path = tmp_path / "storyboard-v3.json"
    value = {
        "schema": "hyperframes-storyboard/v3", "title": "Selection", "message": "Selection changes outcomes", "duration": 8, "timing_mode": "approximate",
        "scenes": [{
            "id": "s01-select", "title": "Choose the signal", "start": 0, "end": 8,
            "content": "Worthwhile content is selected, not merely decorated.",
            "visual": "A stream of documents; one document arrests, separates, and folds; selection visibly changes its future.",
            "motion": "Internal change: documents stream → one arrests → it folds → final readable hold.",
            "uses": [
                {"id": "lottie:pulse", "responsibilities": ["establish many candidates"], "required": True},
                {"id": "svg:primitive:document", "responsibilities": ["make judgment produce a consequence", "serve as the transforming hero"], "required": True},
                {"id": "registry-component:trace-line", "responsibilities": ["scan candidate documents"], "required": True},
            ],
        }],
    }
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def make_review(tmp_path: Path, storyboard_path: Path) -> Path:
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    payload = json.dumps(storyboard, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    reviews = []
    for scene in storyboard["scenes"]:
        if scene["end"] - scene["start"] > 3:
            reviews.append({"sceneId": scene["id"], "decision": "internal-change", "motionQuote": scene["motion"], "conclusion": {"before": "documents stream", "after": "final readable hold", "direction": "one arrests → it folds"}, "rationale": "The selected document changes state and trajectory within the scene."})
    path = tmp_path / (storyboard_path.stem + "-review.json")
    path.write_text(json.dumps({"state": "approved", "storyboardHash": hashlib.sha256(payload).hexdigest(), "source": "automated-agent-attestation", "unresolvedSceneIds": [], "reviewer": {"type": "automated-agent", "workflow": "curated-intake", "rubricVersion": "motion-attestation/v1", "modelId": "test-agent"}, "sceneReviews": reviews}, ensure_ascii=False), encoding="utf-8")
    return path


def prepare(tmp_path: Path) -> tuple[Path, Path, Path]:
    library, storyboard, project = make_library(tmp_path), make_storyboard(tmp_path), tmp_path / "project"
    curation = tmp_path / "curation.json"
    run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard, "--frame-preset", "cobalt", "--review-confirmation", make_review(tmp_path, storyboard), "--output", curation)
    run("prepare-project.py", "--project", project, "--library", library, "--curation", curation, "--storyboard-spec", storyboard, "--intent", "Explain selection", "--destination", "web", "--language", "zh-CN")
    return project, library, storyboard


def test_storyboard_v3_runtime_uses_the_canonical_schema(tmp_path: Path) -> None:
    storyboard = json.loads(make_storyboard(tmp_path).read_text(encoding="utf-8"))
    schema = json.loads((SKILL / "references/storyboard-spec.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(storyboard, schema)
    assert "component_budget" not in json.dumps(storyboard)
    assert storyboard["scenes"][0]["visual"]


def test_e3_minimal_v3_fixtures_cover_production_and_recipe_boundaries() -> None:
    schema = json.loads((SKILL / "references/storyboard-spec.schema.json").read_text(encoding="utf-8"))
    storyboard = json.loads((FIXTURES / "curated-intake-storyboard-v3-minimal.json").read_text(encoding="utf-8"))
    recipe = json.loads((FIXTURES / "curated-intake-storyboard-v3-recipe.json").read_text(encoding="utf-8"))
    jsonschema.validate(storyboard, schema)
    jsonschema.validate(recipe, schema)
    assert storyboard["timing_mode"] == "locked"
    assert storyboard["scenes"][0]["locks"] == {"timing": True, "uses": True}
    assert "next" not in storyboard["scenes"][0]  # an ordinary hard cut
    assert "next" not in storyboard["scenes"][-1]  # last scene cannot point onward
    assert {use["id"].split(":", 1)[0] for use in storyboard["scenes"][0]["uses"]} == {"logo", "svg", "registry-component"}
    assert any(not use["required"] and use["id"] == "logo:missing-optional" for use in storyboard["scenes"][1]["uses"])
    assert [scene["end"] - scene["start"] > 3 for scene in storyboard["scenes"]] == [False, True, True]
    assert recipe["scenes"][0]["uses"] == [{"id": "recipe:legacy-reveal", "responsibilities": ["Preserve the migrated recipe reference"], "required": False}]


def test_palette_routes_per_event_and_preserves_exact_winner(tmp_path: Path) -> None:
    library, storyboard, output = make_library(tmp_path), make_storyboard(tmp_path), tmp_path / "curation.json"
    run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard, "--frame-preset", "cobalt", "--review-confirmation", make_review(tmp_path, storyboard), "--output", output)
    value = json.loads(output.read_text(encoding="utf-8"))
    assert value["schemaVersion"] == "hyperframes-curated-intake/v5"
    assert {need["lane"] for need in value["needs"]} >= {"component", "primitive"}
    assert "svg:primitive:document" in value["selectedIds"]
    assert not any("title" in need or "visualThesis" in need for need in value["needs"])


def test_scene_use_query_is_unicode_safe_ordered_and_ignores_non_authority_fields() -> None:
    scene = {
        "title": "Ignored title", "content": "内容：选择证据", "visual": "画面：一张卡片展开",
        "motion": "Internal change: 卡片 → 可验证的来源", "candidateAudit": {"score": 99},
    }
    use = {"id": "svg:primitive:document", "responsibilities": ["承载来源", "保持可读"]}
    expected = "\n".join([scene["content"], scene["visual"], scene["motion"], use["id"], *use["responsibilities"]])
    assert PALETTE.scene_use_query(scene, use) == expected
    for field in ("content", "visual", "motion"):
        changed = dict(scene)
        changed[field] += "！"
        assert PALETTE.scene_use_query(changed, use) != expected
    changed_use = dict(use, id="svg:primitive:other")
    assert PALETTE.scene_use_query(scene, changed_use) != expected
    changed_use = dict(use, responsibilities=list(reversed(use["responsibilities"])))
    assert PALETTE.scene_use_query(scene, changed_use) != expected
    ignored = dict(scene, title="Different", candidateAudit={"score": -1}, takeaway="legacy")
    assert PALETTE.scene_use_query(ignored, use) == expected


def test_prepare_writes_single_authority_and_short_handoff(tmp_path: Path) -> None:
    project, _, _ = prepare(tmp_path)
    assert (project / "STORYBOARD.md").is_file()
    assert (project / ".hyperframes/intake-manifest.json").is_file()
    assert (project / ".hyperframes/compiled/storyboard.json").is_file()
    assert not (project / "scene-contracts").exists()
    assert not (project / ".hyperframes/build-plan.json").exists()
    assert not (project / ".hyperframes/intake-handoff.json").exists()
    handoff = (project / "HANDOFF.md").read_text(encoding="utf-8")
    assert "Preflight: passed" in handoff
    assert "Choreography:" not in handoff and "registry-component:" not in handoff
    assert len(handoff.splitlines()) < 20


def test_prepare_stages_registry_svg_and_lottie_with_hashes(tmp_path: Path) -> None:
    project, _, _ = prepare(tmp_path)
    receipt = json.loads((project / ".hyperframes/staging-receipt.json").read_text(encoding="utf-8"))
    assert receipt["schemaVersion"] == "hyperframes-curated-staging-receipt/v3"
    assert {item["kind"] for item in receipt["items"]} == {"registry-component", "svg", "lottie"}
    for item in receipt["items"]:
        assert item["license"] and item["provenance"]
        for file in item["files"]:
            assert file["sourceHash"] == file["destinationHash"]
            assert not Path(file["destinationPath"]).is_absolute()


def test_handoff_detects_stale_compiled_cache(tmp_path: Path) -> None:
    project, _, _ = prepare(tmp_path)
    (project / "STORYBOARD.md").write_text((project / "STORYBOARD.md").read_text(encoding="utf-8") + "\nchanged", encoding="utf-8")
    result = run("verify-handoff.py", "--project", project, check=False)
    assert result.returncode == 1
    assert "compiled-stale" in result.stdout


def test_handoff_preflight_passes(tmp_path: Path) -> None:
    project, _, _ = prepare(tmp_path)
    result = run("verify-handoff.py", "--project", project)
    assert json.loads(result.stdout)["ok"] is True


def test_wrong_rubric_exploit_fails_prepare_stage_and_handoff_with_actual_and_supported(tmp_path: Path) -> None:
    project, library, storyboard = prepare(tmp_path)
    curation_path = project / ".hyperframes/curation.json"
    curation = json.loads(curation_path.read_text(encoding="utf-8"))
    curation["review"]["reviewer"]["rubricVersion"] = "motion-attestation/v2"
    curation_path.write_text(json.dumps(curation), encoding="utf-8")
    expected = "actual='motion-attestation/v2'; supported='motion-attestation/v1'"

    prepared = run("prepare-project.py", "--project", tmp_path / "exploit-prepare", "--library", library, "--curation", curation_path, "--storyboard-spec", storyboard, "--intent", "x", "--destination", "web", "--language", "en", check=False)
    assert prepared.returncode != 0 and expected in prepared.stderr
    staged = run("stage-selected-items.py", "--project", project, "--library", library, "--all-required", check=False)
    assert staged.returncode != 0 and expected in staged.stderr
    verified = run("verify-handoff.py", "--project", project, "--library", library, check=False)
    assert verified.returncode != 0 and expected in verified.stdout


def test_motion_fidelity_rejects_generic_fold_evidence(tmp_path: Path) -> None:
    project, _, _ = prepare(tmp_path)
    frame = project / "compositions/frames/s01-select.html"
    frame.parent.mkdir(parents=True)
    frame.write_text('<div data-composition-id="s01-select"><i id="paper-stream"></i><i id="selected-paper"></i></div>', encoding="utf-8")
    usage = {"schemaVersion": "hyperframes-curated-usage/v3", "scenes": [{"id": "s01-select", "useEvidence": [
        {"id": "registry-component:trace-line", "mounted": True, "sourcePath": "compositions/components/library/trace-line.html"},
        {"id": "svg:primitive:document", "mounted": True, "sourcePath": "assets/library/svg/svg-primitive-document.svg"},
        {"id": "lottie:pulse", "mounted": True, "sourcePath": "assets/library/lottie/lottie-pulse.json"},
    ], "motionEvidence": {"opening": "documents enter", "settled": "selected document folded", "finalHold": "readable"}, "missIds": []}], "boundaries": [], "custom": []}
    (project / ".hyperframes/usage.json").write_text(json.dumps(usage), encoding="utf-8")
    result = run("verify-curation.py", "--project", project, check=False)
    assert result.returncode == 1
    assert "motion-fidelity" in result.stdout
