from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".agents/skills/hyperframes-curated-intake/scripts"


def run(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def v2_storyboard() -> dict:
    def event(event_id: str, window: str, target: str, change: str, purpose: str, via: str | None, role: str) -> dict:
        value = {"id": event_id, "window": window, "target": target, "change": change, "purpose": purpose, "role": role}
        if via:
            value["via"] = via
        return value

    return {
        "schema": "hyperframes-storyboard/v2",
        "title": "Migration proof",
        "message": "Choose the evidence.",
        "duration": "8s",
        "timing_mode": "locked",
        "throughline": "A signal becomes proof.",
        "creative_profile": "dense-signature-v1",
        "scenes": [
            {
                "id": "scene-one", "title": "Choose", "window": "0-4s", "takeaway": "Only relevant evidence advances.",
                "semantic_tags": ["evidence"], "narrative_role": "hook", "available_inputs": ["documents"],
                "visual_thesis": {"subject": "A document stream", "change": "one document stops", "semantic_bridge": "selection changes its path"},
                "focus": {"primary": "selected document", "secondary": "scanner"},
                "source_anchor": {"source": "article.md", "anchor": "selection-paragraph"},
                "choreography": [
                    event("scan", "0-50%", "#stream", "Documents pass the scanner", "Establish candidates", "registry-component:trace-line", "secondary"),
                    event("hold", "50-100%", "#selected", "The chosen document holds", "Confirm selection", "svg:primitive:document", "confirmation"),
                ],
                "reuse": [
                    {"id": "registry-component:trace-line", "target": "#stream", "responsibility": "Scan the document stream", "required": False},
                    {"id": "authored:openai-mark", "target": "#brand", "responsibility": "Identify the source", "required": True},
                ],
                "exit": {"state": "The selected document unfolds into proof", "to_scene": "scene-two", "via": "transition:wipe"},
            },
            {
                "id": "scene-two", "title": "Prove", "window": "4-8s", "takeaway": "The selected evidence supports the claim.",
                "visual_thesis": {"subject": "The selected document", "change": "it opens beside the claim", "semantic_bridge": "source and claim become inspectable together"},
                "focus": {"primary": "document and claim"},
                "choreography": [
                    event("open", "0-70%", "#document", "The document opens", "Reveal the source", "recipe:legacy-reveal", "primary"),
                    event("settle", "70-100%", "#claim", "The claim remains readable", "Preserve the final hold", None, "confirmation"),
                ],
                "reuse": [{"id": "recipe:legacy-reveal", "target": "#document", "responsibility": "Keep the original reveal recipe", "required": False}],
                "exit": {"state": "The sourced claim remains readable", "to_scene": None, "via": "recipe:legacy-settle"},
            },
        ],
    }


def write(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def confirmation(path: Path, storyboard_path: Path, *, reviewer: str = "human-reviewer") -> Path:
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    payload = json.dumps(storyboard, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    reviews = []
    for scene in storyboard["scenes"]:
        if scene["end"] - scene["start"] <= 3:
            continue
        if "documents stream → one arrests → it folds → final readable hold" in scene["motion"]:
            reviews.append({"sceneId": scene["id"], "decision": "internal-change", "motionQuote": scene["motion"], "conclusion": {"before": "documents stream", "after": "final readable hold", "direction": "one arrests → it folds"}, "rationale": "The document changes state and trajectory."})
        else:
            reviews.append({"sceneId": scene["id"], "decision": "static-reason", "motionQuote": scene["motion"], "conclusion": {"object": scene["motion"], "reason": scene["motion"], "reasonType": "readability"}, "rationale": "The authored motion explicitly preserves a readable evidence state."})
    return write(path, {"state": "approved", "storyboardHash": __import__("hashlib").sha256(payload).hexdigest(), "source": "automated-agent-attestation", "unresolvedSceneIds": [], "reviewer": {"type": "automated-agent", "workflow": "curated-intake", "rubricVersion": "motion-attestation/v1", "modelId": reviewer}, "sceneReviews": reviews})


def test_migration_is_deterministic_lossless_and_externalizes_review(tmp_path: Path) -> None:
    source = write(tmp_path / "v2.json", v2_storyboard())
    outputs = []
    reports = []
    for suffix in ("a", "b"):
        output, report = tmp_path / f"v3-{suffix}.json", tmp_path / f"report-{suffix}.json"
        result = run("migrate-storyboard-v2-to-v3.py", "--input", source, "--output", output, "--report", report)
        assert result.returncode == 0, result.stdout + result.stderr
        outputs.append(output)
        reports.append(report)
    assert outputs[0].read_bytes() == outputs[1].read_bytes()
    assert reports[0].read_bytes() == reports[1].read_bytes()

    old = v2_storyboard()
    new = json.loads(outputs[0].read_text(encoding="utf-8"))
    report = json.loads(reports[0].read_text(encoding="utf-8"))
    assert new["schema"] == "hyperframes-storyboard/v3"
    assert new["message"] == "Choose the evidence.\nThroughline: A signal becomes proof."
    assert [scene["id"] for scene in new["scenes"]] == [scene["id"] for scene in old["scenes"]]
    first = new["scenes"][0]
    assert first["content"] == old["scenes"][0]["takeaway"]
    for text in (*old["scenes"][0]["visual_thesis"].values(), *old["scenes"][0]["focus"].values()):
        assert text in first["visual"]
    for event in old["scenes"][0]["choreography"]:
        assert event["change"] in first["motion"] and event["purpose"] in first["motion"]
    assert first["source_anchor"] == old["scenes"][0]["source_anchor"]
    assert first["next"] == {"sceneId": "scene-two", "transition": old["scenes"][0]["exit"]["state"]}
    assert old["scenes"][1]["exit"]["state"] in new["scenes"][1]["motion"]
    assert not new["scenes"][0]["motion"].startswith(("Internal change:", "Static reason:"))
    assert [item["id"] for item in new["scenes"][1]["uses"]] == ["recipe:legacy-reveal", "recipe:legacy-settle"]
    assert new["scenes"][1]["uses"][0] == {"id": "recipe:legacy-reveal", "responsibilities": ["Reveal the source", "Keep the original reveal recipe"], "required": True}
    assert [item["id"] for item in first["uses"]] == ["registry-component:trace-line", "svg:primitive:document", "authored:openai-mark", "transition:wipe"]
    trace = first["uses"][0]
    assert trace["responsibilities"] == ["Establish candidates", "Scan the document stream"]
    assert trace["required"] is True
    assert first["uses"][-1] == {"id": "transition:wipe", "responsibilities": ["Transition: The selected document unfolds into proof"], "required": True}
    assert not ({"approval", "locks", "choreography", "reuse", "exit", "visual_thesis", "focus"} & set(first))
    assert report["status"] == "needs-review" and report["authoritative"] is False and report["approvalInherited"] is False
    assert report["unresolvedSceneIds"] == ["scene-one", "scene-two"]
    assert [item["sourceSceneId"] for item in report["sceneMappings"]] == ["scene-one", "scene-two"]
    assert report["sceneMappings"][0]["sourceAnchor"]["mapped"] is True
    assert {item["eventId"] for item in report["sceneMappings"][0]["eventMappings"]} == {"scan", "hold"}
    assert report["sceneMappings"][0]["eventMappings"][0]["removedStructure"] == {"id": "scan", "window": "0-50%", "target": "#stream", "role": "secondary"}
    assert {item["source"] for item in report["sceneMappings"][0]["externalizedNeedsReview"]} == {"/semantic_tags", "/narrative_role", "/available_inputs"}
    assert report["sceneMappings"][0]["review"]["state"] == "needs-review"


def test_migration_requires_three_distinct_paths_and_rejects_v3_input(tmp_path: Path) -> None:
    source = write(tmp_path / "v2.json", v2_storyboard())
    same = run("migrate-storyboard-v2-to-v3.py", "--input", source, "--output", source, "--report", tmp_path / "report.json")
    assert same.returncode != 0 and "in-place migration is forbidden" in same.stderr
    v3 = copy.deepcopy(v2_storyboard())
    v3["schema"] = "hyperframes-storyboard/v3"
    source_v3 = write(tmp_path / "already-v3.json", v3)
    result = run("migrate-storyboard-v2-to-v3.py", "--input", source_v3, "--output", tmp_path / "out.json", "--report", tmp_path / "out-report.json")
    assert result.returncode != 0 and "already hyperframes-storyboard/v3" in result.stderr
    assert not (tmp_path / "out.json").exists()


def test_production_v3_loader_rejects_v2_with_explicit_command(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library
    source = write(tmp_path / "v2.json", v2_storyboard())
    result = run("select-project-palette.py", "--library", make_library(tmp_path), "--storyboard-spec", source, "--frame-preset", "cobalt", "--review-confirmation", tmp_path / "absent-review.json", "--output", tmp_path / "curation.json")
    assert result.returncode != 0
    assert "migrate-storyboard-v2-to-v3.py --input" in result.stderr


def test_required_missing_use_fails_and_optional_missing_remains_visible(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_storyboard
    library = make_library(tmp_path)
    storyboard_path = make_storyboard(tmp_path)
    value = json.loads(storyboard_path.read_text(encoding="utf-8"))
    value["scenes"][0]["uses"].append({"id": "logo:missing", "responsibilities": ["Show optional partner"], "required": False})
    write(storyboard_path, value)
    curation = tmp_path / "optional-curation.json"
    result = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", confirmation(tmp_path / "optional-review.json", storyboard_path), "--output", curation)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(curation.read_text(encoding="utf-8"))
    assert any(miss["need"].endswith("logo:missing\nShow optional partner") for miss in payload["catalogMisses"])
    assert "logo:missing" not in payload["selectedIds"]
    project = tmp_path / "optional-project"
    prepared = run("prepare-project.py", "--project", project, "--library", library, "--curation", curation, "--storyboard-spec", storyboard_path, "--intent", "Show optional binding", "--destination", "web", "--language", "en")
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    verified = run("verify-handoff.py", "--project", project)
    assert verified.returncode == 0, verified.stdout + verified.stderr
    verification = json.loads(verified.stdout)
    assert verification["warnings"] == 1
    assert any(item["code"] == "optional-use-miss" for item in verification["findings"])

    value["scenes"][0]["uses"][-1]["required"] = True
    write(storyboard_path, value)
    required = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", confirmation(tmp_path / "required-review.json", storyboard_path), "--output", tmp_path / "required-curation.json")
    assert required.returncode != 0 and "Required Storyboard use is unavailable" in required.stderr


def test_long_scene_gate_requires_exact_external_structured_review(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_storyboard
    library, storyboard_path = make_library(tmp_path), make_storyboard(tmp_path)
    value = json.loads(storyboard_path.read_text(encoding="utf-8"))
    value["scenes"][0]["motion"] = "The source quotation remains readable while the claim is inspected."
    write(storyboard_path, value)
    review_path = confirmation(tmp_path / "review.json", storyboard_path)
    review = json.loads(review_path.read_text(encoding="utf-8"))
    del review["sceneReviews"][0]["rationale"]
    write(review_path, review)
    invalid = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", review_path, "--output", tmp_path / "invalid.json")
    assert invalid.returncode != 0 and "rationale" in invalid.stderr
    review_path = confirmation(tmp_path / "valid-review.json", storyboard_path)
    valid = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", review_path, "--output", tmp_path / "valid.json")
    assert valid.returncode == 0, valid.stdout + valid.stderr
    value["scenes"][0]["motion"] += " changed"
    write(storyboard_path, value)
    stale = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", review_path, "--output", tmp_path / "stale.json")
    assert stale.returncode != 0 and "stale" in stale.stderr


@pytest.mark.parametrize("mutation, expected", [
    (lambda review: review["reviewer"].update(workflow="unknown"), "unsupported automated-agent provenance"),
    (lambda review: review["reviewer"].pop("modelId"), "modelId or runProvenance"),
    (lambda review: review["sceneReviews"].append(copy.deepcopy(review["sceneReviews"][0])), "exactly one record"),
    (lambda review: review["sceneReviews"][0].update(motionQuote="not the Storyboard motion"), "motionQuote"),
    (lambda review: review["sceneReviews"][0].pop("conclusion"), "structured conclusion"),
])
def test_motion_attestation_rejects_invalid_structure_and_provenance(mutation, expected: str, tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_storyboard
    library, storyboard_path = make_library(tmp_path), make_storyboard(tmp_path)
    review_path = confirmation(tmp_path / "review.json", storyboard_path)
    review = json.loads(review_path.read_text(encoding="utf-8"))
    mutation(review)
    write(review_path, review)
    result = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", review_path, "--output", tmp_path / "curation.json")
    assert result.returncode != 0 and expected in result.stderr


@pytest.mark.parametrize("rubric", ["__missing__", None, "", "Motion-Attestation/v1", " motion-attestation/v1", "motion-attestation/v1 ", "motion-attestation/v0", "motion-attestation/v2", "random"])
def test_motion_attestation_accepts_exactly_one_rubric_version(rubric, tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_storyboard
    library, storyboard_path = make_library(tmp_path), make_storyboard(tmp_path)
    review_path = confirmation(tmp_path / "review.json", storyboard_path)
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if rubric == "__missing__":
        del review["reviewer"]["rubricVersion"]
        actual = "None"
    else:
        review["reviewer"]["rubricVersion"] = rubric
        actual = repr(rubric)
    write(review_path, review)
    result = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", review_path, "--output", tmp_path / "curation.json")
    assert result.returncode != 0
    assert f"actual={actual}" in result.stderr
    assert "supported='motion-attestation/v1'" in result.stderr


def test_motion_semantics_are_versioned_agent_eval_not_cli_heuristics() -> None:
    fixture = json.loads((ROOT / "tests/fixtures/curated-intake-motion-attestation-v1.json").read_text(encoding="utf-8"))
    assert fixture["rubricVersion"] == "motion-attestation/v1"
    assert {case["language"] for case in fixture["cases"]} == {"en", "zh-CN"}
    assert all(case["expected"] == "reject" for case in fixture["cases"] if case["category"] in {"filler", "template", "same-state", "missing-direction", "non-specific-static-reason"})


def test_migration_report_curation_cannot_prepare_until_exact_hash_is_human_reviewed(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library
    source = write(tmp_path / "v2.json", v2_storyboard())
    draft, report = tmp_path / "draft.json", tmp_path / "review.json"
    migrated = run("migrate-storyboard-v2-to-v3.py", "--input", source, "--output", draft, "--report", report)
    assert migrated.returncode == 0, migrated.stdout + migrated.stderr
    library, curation = make_library(tmp_path), tmp_path / "curation.json"
    selected = run("select-project-palette.py", "--library", library, "--storyboard-spec", draft, "--frame-preset", "cobalt", "--review-report", report, "--output", curation)
    assert selected.returncode != 0
    assert "Required Storyboard recipe is unresolved" in selected.stderr


def test_migration_only_recipe_can_be_reviewed_but_not_prepared_as_catalog(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_storyboard
    library, storyboard_path = make_library(tmp_path), make_storyboard(tmp_path)
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    storyboard["scenes"][0]["uses"].append({"id": "recipe:legacy-fold", "responsibilities": ["Preserve the legacy fold"], "required": False})
    write(storyboard_path, storyboard)
    curation = tmp_path / "recipe-curation.json"
    selected = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", confirmation(tmp_path / "recipe-review.json", storyboard_path), "--output", curation)
    assert selected.returncode == 0, selected.stdout + selected.stderr
    prepared = run("prepare-project.py", "--project", tmp_path / "recipe-project", "--library", library, "--curation", curation, "--storyboard-spec", storyboard_path, "--intent", "x", "--destination", "web", "--language", "en")
    assert prepared.returncode != 0
    assert "unresolved migration-only recipe" in prepared.stderr.lower()
    payload = json.loads(curation.read_text(encoding="utf-8"))
    miss = next(item for item in payload["catalogMisses"] if item.get("reason") == "unresolved-recipe")
    assert miss["id"] == "recipe:legacy-fold" and miss["required"] is False and miss["sceneId"] == "s01-select"
    assert "recipe:legacy-fold" not in payload["selectedIds"]


def test_required_recipe_fails_selection_but_existing_alias_resolution_can_stage(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_storyboard
    library, storyboard_path = make_library(tmp_path), make_storyboard(tmp_path)
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    storyboard["scenes"][0]["uses"] = [{"id": "recipe:legacy-trace", "responsibilities": ["Trace the evidence"], "required": True}]
    write(storyboard_path, storyboard)
    review_path = confirmation(tmp_path / "recipe-required-review.json", storyboard_path)
    failed = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", review_path, "--output", tmp_path / "failed.json")
    assert failed.returncode != 0 and "Required Storyboard recipe is unresolved" in failed.stderr

    write(library / "legacy-component-aliases.json", {"aliases": {"recipe:legacy-trace": {"registry_id": "registry-component:trace-line", "result": "ready"}}})
    curation = tmp_path / "resolved.json"
    selected = run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard_path, "--frame-preset", "cobalt", "--review-confirmation", review_path, "--output", curation)
    assert selected.returncode == 0, selected.stdout + selected.stderr
    payload = json.loads(curation.read_text(encoding="utf-8"))
    assert len(payload["recipeResolutions"]) == 1
    claim = payload["recipeResolutions"][0]
    assert {key: claim[key] for key in ("sceneId", "id", "required", "resolvedId")} == {"sceneId": "s01-select", "id": "recipe:legacy-trace", "required": True, "resolvedId": "registry-component:trace-line"}
    assert claim["provenance"]["aliases"] == "legacy-component-aliases.json"
    assert claim["provenance"]["catalog"] == "catalog.json" and claim["provenance"]["sourceFiles"]
    project = tmp_path / "resolved-project"
    prepared = run("prepare-project.py", "--project", project, "--library", library, "--curation", curation, "--storyboard-spec", storyboard_path, "--intent", "x", "--destination", "web", "--language", "en")
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    receipt = json.loads((project / ".hyperframes/staging-receipt.json").read_text(encoding="utf-8"))
    assert [item["id"] for item in receipt["items"]] == ["registry-component:trace-line"]
    assert receipt["items"][0]["recipeResolutions"] == payload["recipeResolutions"]

    aliases = json.loads((library / "legacy-component-aliases.json").read_text(encoding="utf-8"))
    aliases["aliases"]["recipe:legacy-trace"]["registry_id"] = "lottie:pulse"
    write(library / "legacy-component-aliases.json", aliases)
    staged = run("stage-selected-items.py", "--project", project, "--library", library, "--all-required")
    assert staged.returncode != 0 and "stale or fabricated recipe resolution" in staged.stderr
    verified = run("verify-handoff.py", "--project", project, "--library", library)
    assert verified.returncode != 0 and "recipe-resolution" in verified.stdout


def test_fabricated_recipe_claim_fails_live_library_validation(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_storyboard
    library, storyboard_path = make_library(tmp_path), make_storyboard(tmp_path)
    curation = {
        "storyboardHash": "0" * 64, "selectedIds": ["registry-component:trace-line"],
        "recipeResolutions": [{"sceneId": "s01-select", "id": "recipe:fabricated", "required": True, "resolvedId": "registry-component:trace-line", "provenance": {}}],
    }
    sys.path.insert(0, str(SCRIPTS))
    from _curation import validate_recipe_resolutions
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="fabricated recipe resolution claim"):
        validate_recipe_resolutions(storyboard, curation, library)
