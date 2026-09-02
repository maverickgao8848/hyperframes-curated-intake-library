from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".agents" / "skills" / "hyperframes-curated-intake" / "scripts"
SCHEMA = ROOT / ".agents" / "skills" / "hyperframes-curated-intake" / "references" / "curation.schema.json"
STORYBOARD_SCHEMA = ROOT / ".agents" / "skills" / "hyperframes-curated-intake" / "references" / "storyboard-spec.schema.json"
SCENE_CONTRACT_SCHEMA = ROOT / ".agents" / "skills" / "hyperframes-curated-intake" / "references" / "scene-contract.schema.json"
BUILD_PLAN_SCHEMA = ROOT / ".agents" / "skills" / "hyperframes-curated-intake" / "references" / "build-plan.schema.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script: str, *args: object, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *(str(value) for value in args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def entry(entry_id: str, kind: str, path: str, sha: str, *, title: str, tags: list[str]) -> dict:
    source: dict
    if kind.startswith("registry-"):
        name = entry_id.split(":", 1)[1]
        source = {
            "type": "bundle",
            "name": name,
            "entry": path,
            "files": [{"path": path, "target": f"{name}.html", "sha256": sha}],
        }
        integration = {
            "mode": "subcomposition" if kind == "registry-block" else "inline",
            "timelineOwner": "isolated" if kind == "registry-block" else "host",
            "renderTimeNetwork": False,
        }
    else:
        source = {"type": "file", "path": path}
        integration = {"mode": "image", "timelineOwner": "host", "renderTimeNetwork": False}
    return {
        "id": entry_id,
        "kind": kind,
        "title": title,
        "description": (
            f"{title} for comparison reveal evidence"
            if kind.startswith("registry-")
            else f"{title} brand identity asset"
        ),
        "tags": tags,
        "capabilities": ["reveal", "comparison"] if kind.startswith("registry-") else ["identity"],
        "source": source,
        "integration": integration,
        "preview": path,
        "sha256": sha,
        "license": {"status": "local-reuse"},
        "status": "ready",
    }


def make_library(tmp_path: Path) -> Path:
    library = tmp_path / "library"
    frame = library / "frames" / "cobalt-grid" / "FRAME.md"
    block = library / "registry" / "blocks" / "comparison-reveal.html"
    component = library / "registry" / "components" / "trace-line.html"
    logo = library / "media" / "logos" / "acme.svg"
    other_logo = library / "media" / "logos" / "other.svg"
    for path, content in (
        (frame, "---\nname: Test Frame\n---\n# Frame\n"),
        (block, '<div data-composition-id="comparison-reveal"></div>'),
        (component, '<div class="trace-line"></div>'),
        (logo, '<svg xmlns="http://www.w3.org/2000/svg"></svg>'),
        (other_logo, '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    entries = [
        entry("registry-block:comparison-reveal", "registry-block", "registry/blocks/comparison-reveal.html", digest(block), title="Comparison Reveal", tags=["comparison", "primary-scene"]),
        entry("registry-component:trace-line", "registry-component", "registry/components/trace-line.html", digest(component), title="Trace Line", tags=["trace", "support"]),
        entry("logo:acme:mark", "logo", "media/logos/acme.svg", digest(logo), title="Acme Mark", tags=["logo", "identity"]),
        entry("logo:other:mark", "logo", "media/logos/other.svg", digest(other_logo), title="Other Mark", tags=["logo", "identity"]),
    ]
    (library / "catalog.json").write_text(
        json.dumps({"schemaVersion": "hyperframes-directed-video-library/v1", "revision": 1, "entries": entries}),
        encoding="utf-8",
    )
    return library


def storyboard_spec(tmp_path: Path, *, candidate_items: list[str] | None = None) -> Path:
    path = tmp_path / "storyboard-spec.json"
    path.write_text(
        json.dumps({
            "format": "1920x1080",
            "duration": "8s",
            "message": "Show why the product is clearer",
            "arc": "Problem → Comparison → Proof",
            "audience": "product teams",
            "creative_boldness": "bold",
            "timing_policy": {"mode": "bounded", "tolerance_seconds": 0.5},
            "transitions": [],
            "frames": [
                {
                    "id": "01-comparison",
                    "title": "Comparison",
                    "duration": "8s",
                    "scene": "A before-and-after comparison reveals the clearer product",
                    "voiceover": "See the difference immediately.",
                    "source_relation": "designed",
                    "animation": "authored",
                    "teaching_goal": "Compare the two states and identify the improvement",
                    "teaching_intent": "comparison",
                    "cognitive_action": "compare",
                    "scene_role": "comparison",
                    "evidence_type": "trace",
                    "narrative_scale": "standard-scene",
                    "visual_intent": "Two product states separate around a central dividing line",
                    "motion_intent": "Reveal the improved state, then trace the evidence",
                    "visual_pattern": "annotated-object",
                    "density": "comfortable",
                    "hero_visual": {
                        "subject": "The before-and-after product states",
                        "medium": "dom",
                        "source": "authored",
                        "final_state": "The improved state is visibly separated and annotated",
                    },
                    "construction": {
                        "composition": "A central before-and-after Hero fills the frame while a traced divider carries the evidence.",
                        "focal_hierarchy": "Improved state, original state, traced difference, concise conclusion.",
                        "continuity": "The divider becomes the outgoing transition seam.",
                        "layers": [
                            {"id": "frame-field", "role": "background", "content": "Frame-owned field", "slot": "full-bleed", "z_index": 0},
                            {"id": "comparison-hero", "role": "hero", "content": "Before and after product states", "slot": "center", "z_index": 10},
                            {"id": "trace-evidence", "role": "evidence", "content": "Visible traced divider", "slot": "center-seam", "z_index": 20},
                        ],
                    },
                    "integrations": [{
                        "id": "registry-component:trace-line",
                        "selection": "required",
                        "role": "support",
                        "responsibility": "Draw the real comparison evidence on the central seam.",
                        "slot": "center-seam",
                        "target": "trace-evidence",
                        "props": {},
                    }],
                    "asset_bindings": [{"id": "logo:acme:mark", "role": "identity", "target": "comparison-hero", "required": True}],
                    "component_budget": 1,
                    "device": "comparison-reveal",
                    "device_candidates": [{
                        "id": "registry-component:trace-line",
                        "role": "support",
                        "responsibility": "Trace the dividing evidence between product states.",
                        "rationale": "The traced divider makes the comparison legible.",
                    }],
                    "hero": True,
                    "blueprint": "compose",
                    "beats": [
                        {
                            "id": "establish-before", "kind": "reveal", "window": "0-5.2s",
                            "narration": "See the", "reveal": "Establish the original product state",
                            "target_role": "hero", "rule_ids": [], "purpose": "Create a baseline",
                        },
                        {
                            "id": "reveal-after", "kind": "reveal", "window": "5.2-7.2s",
                            "narration": "difference immediately", "reveal": "Reveal and annotate the improved state",
                            "target_role": "evidence", "rule_ids": ["svg-path-draw"], "purpose": "Make the improvement visible",
                        },
                        {
                            "id": "comparison-hold", "kind": "hold", "window": "7.2-8s",
                            "narration": "", "reveal": "Hold the complete comparison",
                            "target_role": "confirmation", "rule_ids": [], "purpose": "Allow the result to be read",
                        },
                    ],
                    "ambient": {"mode": "none", "reason": "The short final comparison hold should remain still and readable."},
                    "text_plan": {
                        "mode": "animated",
                        "cues": [{
                            "id": "comparison-title", "beat_id": "establish-before", "text_shape": "heading",
                            "effect": "word-stagger", "purpose": "Introduce the comparison without a generic fade",
                        }],
                    },
                    "must_preserve": ["Use the real Acme mark"],
                    "avoid": ["Generic floating cards"],
                    "candidate_items": candidate_items or [],
                    "narrative": "The viewer should understand the improvement without reading a paragraph.",
                }
            ],
        }),
        encoding="utf-8",
    )
    return path


def add_cross_warp_transition(library: Path) -> None:
    source = library / "registry" / "blocks" / "cross-warp-morph.html"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('<div data-composition-id="cross-warp-morph">HyperShader transition source</div>', encoding="utf-8")
    catalog_path = library / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["entries"].append(entry(
        "registry-block:cross-warp-morph", "registry-block", "registry/blocks/cross-warp-morph.html",
        digest(source), title="Cross Warp Morph", tags=["transition", "shader"],
    ))
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")


def two_scene_storyboard_spec(tmp_path: Path) -> Path:
    path = storyboard_spec(tmp_path)
    value = json.loads(path.read_text(encoding="utf-8"))
    second = json.loads(json.dumps(value["frames"][0]))
    second.update({
        "id": "02-proof",
        "title": "Proof",
        "scene": "The comparison resolves into a concise proof frame",
        "source_relation": "preserve",
        "animation": "source-only",
        "teaching_goal": "Retain the proof as a readable final state",
        "teaching_intent": "evidence",
        "cognitive_action": "verify",
        "scene_role": "close",
        "evidence_type": "text",
        "narrative_scale": "support-beat",
        "visual_intent": "A decisive proof statement holds in the selected Frame language",
        "motion_intent": "Receive the transition and settle into the proof",
        "visual_pattern": "editorial-type-impact",
        "device": "editorial-proof",
        "device_candidates": [],
        "hero": False,
        "beats": [],
        "ambient": {"mode": "none", "reason": "The source proof remains readable."},
        "text_plan": {"mode": "static-readable", "reason": "The source proof remains intact.", "cues": []},
        "integrations": [],
        "candidate_items": [],
        "narrative": "The incoming warp resolves the visual comparison into a final proof.",
    })
    value["duration"] = "16s"
    value["frames"].append(second)
    value["transitions"] = [{
        "boundary_id": "comparison-to-proof",
        "from_scene": "01-comparison",
        "to_scene": "02-proof",
        "catalog_id": "registry-block:cross-warp-morph",
        "catalog_kind": "registry-block",
        "selection": "required",
        "role": "primary",
        "implementation": "shader-runtime",
        "duration_seconds": 0.6,
        "purpose": "Transform the comparison seam into the proof reveal.",
        "continuity": "The central divider bends into the warp field and releases the proof statement.",
        "same_background": True,
        "perceptual_anchor": "depth-occlusion",
        "color_dependency": "independent",
    }]
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def select(
    library: Path,
    output: Path,
    spec: Path,
    policy: str = "approved-first",
    must_use: tuple[str, ...] = ("logo:acme:mark",),
) -> dict:
    args: list[object] = [
        "select-project-palette.py",
        "--library", library,
        "--storyboard-spec", spec,
        "--frame-preset", "cobalt-grid",
        "--policy", policy,
        "--output", output,
    ]
    for item_id in must_use:
        args.extend(("--must-use", item_id))
    run(*args)
    return json.loads(output.read_text(encoding="utf-8"))


def prepare(library: Path, curation_path: Path, spec: Path, project: Path) -> None:
    run(
        "prepare-project.py",
        "--project", project,
        "--library", library,
        "--curation", curation_path,
        "--storyboard-spec", spec,
        "--intent", "Explain the before and after to product teams.",
        "--destination", "website",
        "--language", "en",
    )


def finalize_build_plan(project: Path) -> None:
    path = project / ".hyperframes" / "build-plan.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["state"] = "build-selected"
    for scene in value["scenes"]:
        scene["selectionStatus"] = "final"
    path.write_text(json.dumps(value), encoding="utf-8")


def test_palette_is_bounded_and_derived_from_approved_scene_needs(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    output = tmp_path / "curation.json"
    curation = select(library, output, spec)
    jsonschema.validate(curation, json.loads(SCHEMA.read_text(encoding="utf-8")))
    jsonschema.validate(json.loads(spec.read_text(encoding="utf-8")), json.loads(STORYBOARD_SCHEMA.read_text(encoding="utf-8")))
    assert curation["palette"]["blocks"] == ["registry-block:comparison-reveal"]
    assert curation["palette"]["components"] == ["registry-component:trace-line"]
    assert curation["requiredAssets"] == ["logo:acme:mark"]
    assert curation["selectionEvidence"]["sceneNeeds"][0]["id"] == "01-comparison"
    assert "central dividing line" in curation["selectionEvidence"]["sceneNeeds"][0]["query"]
    assert curation["selectionEvidence"]["sceneNeeds"][0]["deviceCandidates"][0]["id"] == "registry-component:trace-line"
    assert len(curation["selectionEvidence"]["sceneNeeds"][0]["deviceCandidates"]) == 1
    assert curation["selectionEvidence"]["sceneNeeds"][0]["mediaCandidates"][0]["id"] == "logo:acme:mark"


def test_palette_excludes_ready_registry_entries_missing_from_built_view(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    registry = library / "registry"
    registry.mkdir(exist_ok=True)
    (registry / "registry.json").write_text(
        json.dumps({
            "$schema": "https://hyperframes.heygen.com/schema/registry.json",
            "name": "test",
            "homepage": "https://example.invalid",
            "items": [{"name": "trace-line", "type": "hyperframes:component"}],
        }),
        encoding="utf-8",
    )
    output = tmp_path / "curation.json"
    curation = select(library, output, spec)
    assert curation["palette"]["blocks"] == []
    assert curation["palette"]["components"] == ["registry-component:trace-line"]
    assert curation["selectionEvidence"]["registryFiltered"] == 1


def test_global_required_media_does_not_monopolize_scene_candidates(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path, candidate_items=["logo:acme:mark"])
    output = tmp_path / "curation.json"
    curation = select(library, output, spec, must_use=("logo:other:mark",))
    assert set(curation["palette"]["media"]) == {"logo:acme:mark", "logo:other:mark"}
    scene_media = [candidate["id"] for candidate in curation["selectionEvidence"]["sceneNeeds"][0]["mediaCandidates"]]
    assert scene_media == ["logo:acme:mark"]


def test_prepare_writes_canonical_outline_handoff_and_adopts_required_media(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path, candidate_items=["registry-block:comparison-reveal"])
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    assert (project / "BRIEF.md").is_file()
    assert (project / "frame.md").read_bytes() == (library / "frames/cobalt-grid/FRAME.md").read_bytes()
    assert (project / ".hyperframes/curation.json").is_file()
    assert (project / ".hyperframes/intake-handoff.json").is_file()
    assert (project / ".hyperframes/build-plan.json").is_file()
    assert (project / "HANDOFF.md").is_file()
    assert (project / "scene-contracts/01-comparison.json").is_file()
    assert (project / ".media/manifest.jsonl").is_file()
    storyboard = (project / "STORYBOARD.md").read_text(encoding="utf-8")
    assert "status: outline" in storyboard
    assert "id: 01-comparison" in storyboard
    assert "timeline_window: 0-8s" in storyboard
    assert "source_relation: designed" in storyboard
    assert "Visual intent" in storyboard
    assert "device: comparison-reveal" in storyboard
    assert "cognitive_action: compare" in storyboard
    assert "narrative_scale: standard-scene" in storyboard
    assert "visual_pattern: annotated-object" in storyboard
    assert "blueprint: compose" in storyboard
    assert "rules: svg-path-draw, gsap-effects" in storyboard
    assert "effect=word-stagger" in storyboard
    assert "Scene 3 (7.2-8s)" in storyboard
    assert "device_candidates:" in storyboard
    assert "registry-block:comparison-reveal" in storyboard
    assert not (project / "compositions").exists()
    jsonschema.validate(
        json.loads((project / "scene-contracts/01-comparison.json").read_text(encoding="utf-8")),
        json.loads(SCENE_CONTRACT_SCHEMA.read_text(encoding="utf-8")),
    )
    jsonschema.validate(
        json.loads((project / ".hyperframes/build-plan.json").read_text(encoding="utf-8")),
        json.loads(BUILD_PLAN_SCHEMA.read_text(encoding="utf-8")),
    )
    handoff = (project / "HANDOFF.md").read_text(encoding="utf-8")
    assert "ready for a separate `$hyperframes` build" in handoff
    assert run("verify-handoff.py", "--project", project).returncode == 0
    assert "Start at Sketch from the approved outline" in handoff
    manifest = json.loads((project / ".hyperframes/intake-handoff.json").read_text(encoding="utf-8"))
    assert manifest["nextStage"] == "sketch"
    assert manifest["scenes"][0]["id"] == "01-comparison"
    assert manifest["scenes"][0]["src"] == "compositions/frames/01-comparison.html"
    assert manifest["scenes"][0]["classification"]["narrativeScale"] == "standard-scene"
    assert manifest["scenes"][0]["registryCandidates"][0]["state"] == "candidate"
    config = json.loads((project / "hyperframes.json").read_text(encoding="utf-8"))
    assert "registry" not in config  # local staging is explicit; it is not misrepresented as official add.


def test_multiscene_storyboard_requires_one_transition_per_adjacent_boundary(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    add_cross_warp_transition(library)
    spec = two_scene_storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["transitions"] = []
    spec.write_text(json.dumps(value), encoding="utf-8")
    completed = run(
        "select-project-palette.py", "--library", library, "--storyboard-spec", spec,
        "--frame-preset", "cobalt-grid", "--output", tmp_path / "curation.json", check=False,
    )
    assert completed.returncode != 0
    assert "requires exactly 1 transition contracts" in completed.stderr


def test_prepare_carries_transition_contract_across_all_handoff_artifacts(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    add_cross_warp_transition(library)
    spec = two_scene_storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    curation = select(library, curation_path, spec)
    assert "registry-block:cross-warp-morph" in curation["palette"]["blocks"]
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)

    storyboard = (project / "STORYBOARD.md").read_text(encoding="utf-8")
    assert "## Transition plan" in storyboard
    assert "comparison-to-proof" in storyboard
    contract = json.loads((project / "scene-contracts/02-proof.json").read_text(encoding="utf-8"))
    assert contract["incomingTransition"]["catalog_id"] == "registry-block:cross-warp-morph"
    plan = json.loads((project / ".hyperframes/build-plan.json").read_text(encoding="utf-8"))
    assert len(plan["transitions"]) == 1
    assert plan["transitions"][0]["state"] == "selected-for-build"
    assert plan["transitions"][0]["sameBackground"] is True
    assert plan["transitions"][0]["perceptualAnchor"] == "depth-occlusion"
    assert plan["transitions"][0]["colorDependency"] == "independent"
    manifest = json.loads((project / ".hyperframes/intake-handoff.json").read_text(encoding="utf-8"))
    assert manifest["transitions"][0]["from_scene"] == "01-comparison"
    assert run("verify-handoff.py", "--project", project).returncode == 0


def test_same_background_transition_must_be_color_independent(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    add_cross_warp_transition(library)
    spec = two_scene_storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["transitions"][0]["color_dependency"] = "required"
    spec.write_text(json.dumps(value), encoding="utf-8")
    completed = run(
        "select-project-palette.py", "--library", library, "--storyboard-spec", spec,
        "--frame-preset", "cobalt-grid", "--output", tmp_path / "curation.json", check=False,
    )
    assert completed.returncode != 0
    assert "must be color-independent" in completed.stderr


def test_handoff_preflight_rejects_transition_plan_denominator_shrink(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    add_cross_warp_transition(library)
    spec = two_scene_storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    plan_path = project / ".hyperframes/build-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["transitions"] = []
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    completed = run("verify-handoff.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/handoff-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    assert "transition-plan-count" in {item["code"] for item in report["findings"]}


def test_allocate_beats_places_final_reveal_late_and_reserves_hold(tmp_path: Path) -> None:
    spec = storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    for beat in value["frames"][0]["beats"]:
        beat.pop("window")
    spec.write_text(json.dumps(value), encoding="utf-8")
    run("allocate-beats.py", "--spec", spec, "--write")
    allocated = json.loads(spec.read_text(encoding="utf-8"))["frames"][0]["beats"]
    assert [beat["window"] for beat in allocated] == ["0-5.2s", "5.2-7.2s", "7.2-8s"]
    run("allocate-beats.py", "--spec", spec, "--check")


def test_verify_beats_accepts_compose_and_rejects_unknown_rule(tmp_path: Path) -> None:
    spec = storyboard_spec(tmp_path)
    animation_skill = Path.home() / ".agents/skills/hyperframes-animation"
    completed = run("verify-beats.py", "--spec", spec, "--animation-skill", animation_skill)
    assert completed.returncode == 0
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["frames"][0]["beats"][1]["rule_ids"] = ["not-a-real-rule"]
    spec.write_text(json.dumps(value), encoding="utf-8")
    completed = run(
        "verify-beats.py", "--spec", spec, "--animation-skill", animation_skill, check=False,
    )
    assert completed.returncode == 1
    assert "rule-missing" in completed.stdout


def test_selector_rejects_capability_candidate_with_missing_inputs(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    catalog_path = library / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    trace = next(entry for entry in catalog["entries"] if entry["id"] == "registry-component:trace-line")
    trace["routing"] = {
        "family": "diagram", "teachingIntents": ["comparison"], "cognitiveActions": ["compare"],
        "sceneRoles": ["comparison"], "evidenceTypes": ["trace"], "requiredInputs": ["image"],
        "aspectFit": ["16:9"], "durationMin": 1, "durationMax": 12,
        "densityFit": ["comfortable"], "containerCost": 1, "heroEligible": False,
        "avoid": "Do not use without image evidence", "fallbackIds": [],
    }
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    spec = storyboard_spec(tmp_path)
    completed = run(
        "select-project-palette.py", "--library", library, "--storyboard-spec", spec,
        "--frame-preset", "cobalt-grid", "--output", tmp_path / "curation.json", check=False,
    )
    assert completed.returncode != 0
    assert "missing-inputs=image" in completed.stderr


def test_selector_records_hard_compatibility_and_preserves_director_responsibility(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    catalog_path = library / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    trace = next(entry for entry in catalog["entries"] if entry["id"] == "registry-component:trace-line")
    trace["routing"] = {
        "family": "diagram", "teachingIntents": ["comparison"], "cognitiveActions": ["compare"],
        "sceneRoles": ["comparison"], "evidenceTypes": ["trace"], "requiredInputs": [],
        "aspectFit": ["16:9"], "durationMin": 1, "durationMax": 12,
        "densityFit": ["comfortable"], "containerCost": 1, "heroEligible": False,
        "avoid": "Do not trace unrelated states", "fallbackIds": [],
    }
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    spec = storyboard_spec(tmp_path)
    output = tmp_path / "curation.json"
    curation = select(library, output, spec)
    candidate = curation["selectionEvidence"]["sceneNeeds"][0]["deviceCandidates"][0]
    assert candidate["role"] == "support"
    assert candidate["responsibility"].startswith("Draw the real comparison evidence")
    assert candidate["compatibility"] == "passed"
    assert "inputs" in candidate["compatibilityChecks"]
    assert candidate["catalogRouting"]["avoid"] == "Do not trace unrelated states"


def test_text_plan_requires_named_effect_or_explicit_exemption(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["frames"][0]["text_plan"] = {"mode": "static-readable", "cues": []}
    spec.write_text(json.dumps(value), encoding="utf-8")
    completed = run(
        "select-project-palette.py", "--library", library, "--storyboard-spec", spec,
        "--frame-preset", "cobalt-grid", "--output", tmp_path / "curation.json", check=False,
    )
    assert completed.returncode != 0
    assert "explicit reason" in completed.stderr


def test_prepare_rejects_storyboard_changed_after_palette_selection(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    selection_spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, selection_spec)
    invalid_spec = storyboard_spec(tmp_path, candidate_items=["registry-block:not-approved"])
    completed = run(
        "prepare-project.py",
        "--project", tmp_path / "project",
        "--library", library,
        "--curation", curation_path,
        "--storyboard-spec", invalid_spec,
        "--intent", "Explain the before and after to product teams.",
        "--destination", "website",
        "--language", "en",
        check=False,
    )
    assert completed.returncode != 0
    assert "differs from the approved outline" in completed.stderr


def test_selector_rejects_unknown_scene_candidate(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    invalid_spec = storyboard_spec(tmp_path, candidate_items=["registry-block:not-approved"])
    completed = run(
        "select-project-palette.py",
        "--library", library,
        "--storyboard-spec", invalid_spec,
        "--frame-preset", "cobalt-grid",
        "--output", tmp_path / "curation.json",
        check=False,
    )
    assert completed.returncode != 0
    assert "Unknown catalog IDs" in completed.stderr


def test_prepare_preserves_existing_storyboard_without_explicit_force(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    project.mkdir()
    existing = project / "STORYBOARD.md"
    existing.write_text("approved storyboard\n", encoding="utf-8")
    completed = run(
        "prepare-project.py",
        "--project", project,
        "--library", library,
        "--curation", curation_path,
        "--storyboard-spec", spec,
        "--intent", "Explain the before and after to product teams.",
        "--destination", "website",
        "--language", "en",
        check=False,
    )
    assert completed.returncode != 0
    assert existing.read_text(encoding="utf-8") == "approved storyboard\n"


def test_local_staging_copies_only_exact_selected_item(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    run(
        "stage-selected-items.py",
        "--project", project,
        "--library", library,
        "--method", "local",
        "--item", "trace-line",
    )
    assert (project / "compositions/components/library/trace-line.html").is_file()
    assert not (project / "compositions/library/comparison-reveal.html").exists()
    receipt = json.loads((project / ".hyperframes/staging-receipt.json").read_text(encoding="utf-8"))
    assert [item["id"] for item in receipt["items"]] == ["registry-component:trace-line"]


def test_staging_rejects_palette_candidate_outside_build_plan(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path, candidate_items=["registry-block:comparison-reveal"])
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    completed = run(
        "stage-selected-items.py",
        "--project", project,
        "--library", library,
        "--method", "local",
        "--item", "comparison-reveal",
        check=False,
    )
    assert completed.returncode == 1
    assert "outside the exact Build Plan selection" in completed.stderr


def test_verifier_distinguishes_staged_from_used_and_accepts_real_references(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    run("stage-selected-items.py", "--project", project, "--library", library, "--method", "local", "--item", "trace-line")
    finalize_build_plan(project)
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    composition = project / "compositions/frames/01-comparison.html"
    composition.parent.mkdir(parents=True)
    composition.write_text(
        f'<div data-composition-id="01-comparison"></div><img src="{logo_record["path"]}">'
        '<h1 id="comparison-title" data-text-cue-id="comparison-title" data-text-effect="word-stagger">Compare</h1>'
        '<div id="beat-before" data-beat-id="establish-before"></div>'
        '<div id="beat-after" data-beat-id="reveal-after"></div>'
        '<div id="beat-hold" data-beat-id="comparison-hold"></div>'
        '<div id="trace-evidence" class="trace-line"></div>',
        encoding="utf-8",
    )
    composition.with_suffix(".motion.json").write_text(
        json.dumps({
            "duration": 8,
            "assertions": [
                {"kind": "appearsBy", "selector": "#comparison-title", "bySec": 5.2},
                {"kind": "before", "a": "#beat-before", "b": "#beat-after"},
            ],
        }),
        encoding="utf-8",
    )
    (project / ".hyperframes/usage.json").write_text(
        json.dumps({
            "majorScenes": [{
                "id": "01-comparison",
                "curatedItems": ["registry-component:trace-line"],
                "missIds": [],
                "integrationEvidence": [{"id": "registry-component:trace-line", "selector": "#trace-evidence", "implementation": "inline"}],
                "beatEvidence": [
                    {"id": "establish-before", "selector": "#beat-before"},
                    {"id": "reveal-after", "selector": "#beat-after"},
                    {"id": "comparison-hold", "selector": "#beat-hold"},
                ],
                "textEffects": [{"id": "comparison-title", "effect": "word-stagger", "selector": "#comparison-title"}],
                "ambientEvidence": None,
            }],
            "custom": [],
        }),
        encoding="utf-8",
    )
    completed = run("verify-curation.py", "--project", project)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 0
    assert report["ok"] is True
    assert report["usedCuratedItems"] == ["registry-component:trace-line"]
    assert report["libraryCoverage"]["ratio"] == 1.0


def test_verifier_requires_usage_contract_for_built_major_scenes(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    composition = project / "compositions/frames/01-comparison.html"
    composition.parent.mkdir(parents=True)
    composition.write_text(f'<div data-composition-id="01-comparison"></div><img src="{logo_record["path"]}">', encoding="utf-8")
    finalize_build_plan(project)
    completed = run("verify-curation.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    assert "usage-missing" in {item["code"] for item in report["findings"]}


def test_verifier_requires_real_transition_runtime_and_boundary_evidence(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    add_cross_warp_transition(library)
    spec = two_scene_storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    run(
        "stage-selected-items.py", "--project", project, "--library", library, "--method", "local",
        "--item", "trace-line", "--item", "cross-warp-morph",
    )
    finalize_build_plan(project)
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    first = project / "compositions/frames/01-comparison.html"
    first.parent.mkdir(parents=True)
    first.write_text(
        f'<div data-composition-id="01-comparison"></div><img src="{logo_record["path"]}">'
        '<h1 id="comparison-title" data-text-cue-id="comparison-title" data-text-effect="word-stagger">Compare</h1>'
        '<div id="beat-before" data-beat-id="establish-before"></div>'
        '<div id="beat-after" data-beat-id="reveal-after"></div>'
        '<div id="beat-hold" data-beat-id="comparison-hold"></div>'
        '<div id="trace-evidence" class="trace-line"></div>',
        encoding="utf-8",
    )
    first.with_suffix(".motion.json").write_text(json.dumps({
        "duration": 8,
        "assertions": [
            {"kind": "appearsBy", "selector": "#comparison-title", "bySec": 5.2},
            {"kind": "before", "a": "#beat-before", "b": "#beat-after"},
        ],
    }), encoding="utf-8")
    (project / "compositions/frames/02-proof.html").write_text(
        '<div data-composition-id="02-proof">Proof</div>', encoding="utf-8",
    )
    (project / "index.html").write_text(
        '<div id="comparison-to-proof" data-transition-id="comparison-to-proof" '
        'data-transition-from="01-comparison" data-transition-to="02-proof" '
        'data-transition-block="registry-block:cross-warp-morph"></div>'
        '<script>HyperShader.init({scenes:["01-comparison","02-proof"]});</script>',
        encoding="utf-8",
    )
    (project / ".hyperframes/usage.json").write_text(json.dumps({
        "majorScenes": [{
            "id": "01-comparison",
            "curatedItems": ["registry-component:trace-line"],
            "missIds": [],
            "integrationEvidence": [{"id": "registry-component:trace-line", "selector": "#trace-evidence", "implementation": "inline"}],
            "beatEvidence": [
                {"id": "establish-before", "selector": "#beat-before"},
                {"id": "reveal-after", "selector": "#beat-after"},
                {"id": "comparison-hold", "selector": "#beat-hold"},
            ],
            "textEffects": [{"id": "comparison-title", "effect": "word-stagger", "selector": "#comparison-title"}],
            "ambientEvidence": None,
        }],
        "transitions": [{
            "boundaryId": "comparison-to-proof",
            "fromScene": "01-comparison",
            "toScene": "02-proof",
            "catalogId": "registry-block:cross-warp-morph",
            "implementation": "shader-runtime",
            "controllerSelector": "#comparison-to-proof",
        }],
        "custom": [],
    }), encoding="utf-8")
    completed = run("verify-curation.py", "--project", project)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 0
    assert report["transitionCoverage"] == {"expected": 1, "verified": 1, "ratio": 1.0}

    index = project / "index.html"
    index.write_text('<div id="comparison-to-proof"></div>', encoding="utf-8")
    completed = run("verify-curation.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    codes = {item["code"] for item in report["findings"]}
    assert "transition-controller-missing" in codes
    assert "transition-runtime-missing" in codes


def test_verifier_does_not_count_staged_bundle_self_references_as_usage(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    run("stage-selected-items.py", "--project", project, "--library", library, "--method", "local", "--item", "trace-line")
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    (project / "index.html").write_text(f'<img src="{logo_record["path"]}">', encoding="utf-8")
    completed = run("verify-curation.py", "--project", project)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 0
    assert report["usedCuratedItems"] == []
    assert "staged-unused" in {item["code"] for item in report["findings"]}


def test_policy_gates_custom_dependencies(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    for policy, expected_code in (("approved-only", "approved-only-custom"), ("approved-first", "catalog-miss-required")):
        curation_path = tmp_path / f"{policy}.json"
        select(library, curation_path, spec, policy=policy)
        project = tmp_path / policy
        prepare(library, curation_path, spec, project)
        logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
        (project / "index.html").write_text(f'<img src="{logo_record["path"]}">', encoding="utf-8")
        (project / ".hyperframes/usage.json").write_text(
            json.dumps({"custom": [{"name": "hand-built-scene", "missId": "miss-1"}]}),
            encoding="utf-8",
        )
        completed = run("verify-curation.py", "--project", project, check=False)
        assert completed.returncode == 1
        report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
        assert expected_code in {item["code"] for item in report["findings"]}


def test_open_policy_allows_declared_custom_dependency(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "open.json"
    select(library, curation_path, spec, policy="open")
    project = tmp_path / "open"
    prepare(library, curation_path, spec, project)
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    (project / "index.html").write_text(f'<img src="{logo_record["path"]}">', encoding="utf-8")
    (project / ".hyperframes/usage.json").write_text(json.dumps({"custom": [{"name": "freeform"}]}), encoding="utf-8")
    completed = run("verify-curation.py", "--project", project)
    assert completed.returncode == 0


def test_approved_first_requires_complete_catalog_miss_evidence(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    curation = select(library, curation_path, spec)
    curation["catalogMisses"] = [{"id": "miss-1"}]
    curation_path.write_text(json.dumps(curation), encoding="utf-8")
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    (project / "index.html").write_text(f'<img src="{logo_record["path"]}">', encoding="utf-8")
    (project / ".hyperframes/usage.json").write_text(
        json.dumps({"custom": [{"name": "hand-built-scene", "missId": "miss-1"}]}),
        encoding="utf-8",
    )
    completed = run("verify-curation.py", "--project", project, check=False)
    assert completed.returncode == 1
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    codes = {item["code"] for item in report["findings"]}
    assert "catalog-miss-incomplete" in codes
    assert "catalog-miss-required" in codes


def test_bounded_timing_rejects_global_and_frame_duration_drift(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["duration"] = "12s"
    value["timing_policy"] = {"mode": "bounded", "tolerance_seconds": 0.5}
    spec.write_text(json.dumps(value), encoding="utf-8")
    completed = run(
        "select-project-palette.py", "--library", library, "--storyboard-spec", spec,
        "--frame-preset", "cobalt-grid", "--output", tmp_path / "curation.json", check=False,
    )
    assert completed.returncode != 0
    assert "frame durations total 8s" in completed.stderr


def test_verifier_counts_declared_scene_when_build_uses_wrong_filename(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    (project / "index.html").write_text(f'<img src="{logo_record["path"]}">', encoding="utf-8")
    wrong = project / "compositions/frames/01-renamed.html"
    wrong.parent.mkdir(parents=True)
    wrong.write_text('<div data-composition-id="01-renamed"></div>', encoding="utf-8")
    finalize_build_plan(project)
    completed = run("verify-curation.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    assert "storyboard-src-missing" in {item["code"] for item in report["findings"]}
    assert report["libraryCoverage"]["totalMajorScenes"] == 1


def test_verifier_rejects_wrong_composition_id_at_canonical_path(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    composition = project / "compositions/frames/01-comparison.html"
    composition.parent.mkdir(parents=True)
    composition.write_text('<div data-composition-id="01-renamed"></div>', encoding="utf-8")
    finalize_build_plan(project)
    completed = run("verify-curation.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    assert "composition-id-mismatch" in {item["code"] for item in report["findings"]}


def test_component_metadata_without_real_markers_is_not_counted_as_use(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    run(
        "stage-selected-items.py", "--project", project, "--library", library,
        "--method", "local", "--item", "trace-line",
    )
    logo_record = json.loads((project / ".media/manifest.jsonl").read_text(encoding="utf-8"))
    composition = project / "compositions/frames/01-comparison.html"
    composition.parent.mkdir(parents=True)
    finalize_build_plan(project)
    composition.write_text(
        f'<div data-composition-id="01-comparison"></div><img src="{logo_record["path"]}">'
        '<div id="trace-evidence" data-component-id="trace-line"></div>'
        '<h1 id="comparison-title" data-text-cue-id="comparison-title" data-text-effect="word-stagger">Compare</h1>'
        '<div id="beat-before" data-beat-id="establish-before"></div>'
        '<div id="beat-after" data-beat-id="reveal-after"></div>'
        '<div id="beat-hold" data-beat-id="comparison-hold"></div>',
        encoding="utf-8",
    )
    composition.with_suffix(".motion.json").write_text(
        json.dumps({
            "duration": 8,
            "assertions": [
                {"kind": "appearsBy", "selector": "#comparison-title", "bySec": 5.2},
                {"kind": "before", "a": "#beat-before", "b": "#beat-after"},
            ],
        }),
        encoding="utf-8",
    )
    (project / ".hyperframes/usage.json").write_text(
        json.dumps({
            "majorScenes": [{
                "id": "01-comparison",
                "curatedItems": ["registry-component:trace-line"],
                "missIds": [],
                "integrationEvidence": [{"id": "registry-component:trace-line", "selector": "#trace-evidence", "implementation": "inline"}],
                "beatEvidence": [
                    {"id": "establish-before", "selector": "#beat-before"},
                    {"id": "reveal-after", "selector": "#beat-after"},
                    {"id": "comparison-hold", "selector": "#beat-hold"},
                ],
                "textEffects": [{"id": "comparison-title", "effect": "word-stagger", "selector": "#comparison-title"}],
                "ambientEvidence": None,
            }],
            "custom": [],
        }),
        encoding="utf-8",
    )
    completed = run("verify-curation.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/curation-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    codes = {item["code"] for item in report["findings"]}
    assert "scene-item-unused" in codes
    assert report["usedCuratedItems"] == []


def test_handoff_preflight_rejects_missing_scene_contract(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    (project / "scene-contracts/01-comparison.json").unlink()
    completed = run("verify-handoff.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/handoff-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    assert "scene-contract-missing" in {item["code"] for item in report["findings"]}


def test_handoff_preflight_requires_directed_integration_build_gate(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    curation_path = tmp_path / "curation.json"
    select(library, curation_path, spec)
    project = tmp_path / "project"
    prepare(library, curation_path, spec, project)
    plan_path = project / ".hyperframes/build-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["scenes"][0]["integrations"] = []
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    completed = run("verify-handoff.py", "--project", project, check=False)
    report = json.loads((project / ".hyperframes/handoff-verification.json").read_text(encoding="utf-8"))
    assert completed.returncode == 1
    assert "integration-plan" in {item["code"] for item in report["findings"]}


def test_optional_candidates_can_be_empty_without_fabricated_registry_use(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["frames"][0]["device_candidates"] = []
    value["frames"][0]["integrations"] = []
    spec.write_text(json.dumps(value), encoding="utf-8")
    output = tmp_path / "curation.json"
    curation = select(library, output, spec)
    scene_need = curation["selectionEvidence"]["sceneNeeds"][0]
    assert scene_need["deviceCandidates"] == []
    assert curation["selectionEvidence"]["selectionAuthority"] == "approved-storyboard-spec"


def test_preferred_text_effect_vocabulary_is_accepted(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    spec = storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["frames"][0]["text_plan"]["cues"][0]["effect"] = "text-scramble"
    spec.write_text(json.dumps(value), encoding="utf-8")
    output = tmp_path / "curation.json"
    curation = select(library, output, spec)
    jsonschema.validate(curation, json.loads(SCHEMA.read_text(encoding="utf-8")))
    jsonschema.validate(value, json.loads(STORYBOARD_SCHEMA.read_text(encoding="utf-8")))


def test_typewriter_effect_adopts_preferred_semantic_sfx(tmp_path: Path) -> None:
    library = make_library(tmp_path)
    sfx = library / "media/sfx/typewriter-key.wav"
    sfx.parent.mkdir(parents=True)
    sfx.write_bytes(b"RIFF-test")
    catalog_path = library / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["entries"].append(entry(
        "sfx:typewriter-key", "sfx", "media/sfx/typewriter-key.wav", digest(sfx),
        title="Typewriter Key", tags=["typewriter", "typing", "sfx"],
    ))
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    spec = storyboard_spec(tmp_path)
    value = json.loads(spec.read_text(encoding="utf-8"))
    value["frames"][0]["text_plan"]["cues"][0]["effect"] = "typewriter"
    spec.write_text(json.dumps(value), encoding="utf-8")
    output = tmp_path / "curation.json"
    curation = select(library, output, spec)
    assert "sfx:typewriter-key" in curation["requiredAssets"]
    media_ids = [item["id"] for item in curation["selectionEvidence"]["sceneNeeds"][0]["mediaCandidates"]]
    assert "sfx:typewriter-key" in media_ids
