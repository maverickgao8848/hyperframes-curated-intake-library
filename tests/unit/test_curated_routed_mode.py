from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".agents/skills/hyperframes-curated-intake/scripts"
sys.path.insert(0, str(SCRIPTS))

import _routed


def canonical_hash(value: dict) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def test_routed_prepare_writes_only_bounded_result(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_library, make_review, make_storyboard, run
    library, storyboard = make_library(tmp_path), make_storyboard(tmp_path)
    curation = tmp_path / "curation.json"
    run("select-project-palette.py", "--library", library, "--storyboard-spec", storyboard, "--frame-preset", "cobalt", "--review-confirmation", make_review(tmp_path, storyboard), "--output", curation)
    parent = {"segments": [{"id": "seg-1", "route": "curated-intake"}]}
    parent_path = tmp_path / "director-plan.json"
    parent_path.write_text(json.dumps(parent), encoding="utf-8")
    request = {"schemaVersion": "hyperframes-visual-director/curated-request-v3", "parentPlanPath": "director-plan.json", "parentPlanHash": canonical_hash(parent), "clusterId": "cluster-1", "segmentIds": ["seg-1"], "approvedScope": {"segmentIds": ["seg-1"], "ranges": [], "messages": [], "animationSentencesLocked": False, "segmentSceneMap": {"seg-1": ["s01-select"]}, "sceneLocks": {}}, "lockedDecisions": [], "inheritedVisualPolicy": {}, "timing": {"precision": "estimated"}, "assets": [], "questionsStillOpen": []}
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    project = tmp_path / "routed"
    run("prepare-project.py", "--project", project, "--library", library, "--curation", curation, "--storyboard-spec", storyboard, "--intent", "x", "--destination", "web", "--language", "zh", "--request", request_path)
    result = json.loads((project / ".hyperframes/curated-intake-result.json").read_text(encoding="utf-8"))
    assert result["schemaVersion"] == "hyperframes-visual-director/curated-result-v3"
    assert result["scenePatches"][0]["sceneId"] == "s01-select"
    assert set(result["scenePatches"][0]) >= {"segmentId", "sceneId", "start", "end", "content", "visual", "uses", "motion"}
    assert not ({"visual_thesis", "focus", "choreography", "reuse", "exit"} & set(result["scenePatches"][0]))
    assert not (project / "STORYBOARD.md").exists()
    assert not (project / "HANDOFF.md").exists()
    assert not (project / ".hyperframes/intake-manifest.json").exists()


def test_segment_scene_map_is_exact_and_has_no_single_segment_fallback(tmp_path: Path) -> None:
    from test_curated_intake_workflow import make_storyboard
    parent = {"segments": [{"id": "seg-1", "route": "curated-intake"}, {"id": "seg-2", "route": "curated-intake"}]}
    (tmp_path / "director-plan.json").write_text(json.dumps(parent), encoding="utf-8")
    scope = {"segmentIds": ["seg-1", "seg-2"], "ranges": [], "messages": [], "animationSentencesLocked": False, "segmentSceneMap": {"seg-1": ["s01-select"]}, "sceneLocks": {}}
    request = {"schemaVersion": "hyperframes-visual-director/curated-request-v3", "parentPlanPath": "director-plan.json", "parentPlanHash": canonical_hash(parent), "clusterId": "cluster-1", "segmentIds": ["seg-1", "seg-2"], "approvedScope": scope, "lockedDecisions": [], "inheritedVisualPolicy": {}, "timing": {"precision": "estimated"}, "assets": [], "questionsStillOpen": []}
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    try:
        _routed.validate_request(path)
        raise AssertionError("missing segmentSceneMap key was accepted")
    except ValueError as error:
        assert "keys must exactly match" in str(error)

    storyboard = json.loads(make_storyboard(tmp_path).read_text(encoding="utf-8"))
    request["segmentIds"] = ["seg-1"]
    request["approvedScope"]["segmentIds"] = ["seg-1"]
    request["approvedScope"]["segmentSceneMap"] = {"seg-1": []}
    try:
        _routed.result_packet(request, storyboard)
        raise AssertionError("empty stable scene set implicitly claimed Storyboard scenes")
    except ValueError as error:
        assert "unmapped Storyboard scenes" in str(error)
