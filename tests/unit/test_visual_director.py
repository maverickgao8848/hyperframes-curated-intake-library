from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / ".agents" / "skills" / "hyperframes-visual-director" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


director = load_module("director_plan", "director_plan.py")
curated_merge = load_module("merge_curated_result", "merge-curated-result.py")


def catalog():
    return {
        "schemaVersion": "hyperframes-shared-catalog/v1",
        "entries": [
            {
                "id": "registry-block:chatgpt-desktop-exchange",
                "kind": "registry-block",
                "status": "ready",
                "portStatus": "verified",
                "aspectSupport": ["16:9"],
                "framePolicy": "native-evidence",
            },
            {
                "id": "layer:slow-push-in",
                "kind": "layer",
                "status": "ready",
                "portStatus": "verified",
                "aspectSupport": ["16:9", "9:16"],
                "framePolicy": "source-preserve",
            },
            {
                "id": "talkcraft:unverified-card",
                "kind": "layer",
                "status": "candidate",
                "portStatus": "inventoried",
                "aspectSupport": ["16:9"],
                "framePolicy": "source-preserve",
            },
        ],
    }


def valid_plan():
    return {
        "schemaVersion": "hyperframes-visual-director/v1",
        "revision": 1,
        "project": {
            "id": "demo",
            "title": "Mixed visual plan",
            "durationFrames": 600,
            "fps": 60,
            "width": 1920,
            "height": 1080,
            "aspect": "16:9",
        },
        "sources": [{"id": "source-main", "path": "source.mp4", "sha256": "sha256:abc", "segmentIds": ["seg-001"]}],
        "timing": {"precision": "sentence", "fps": 60, "timingNeedsRefinement": False},
        "collaborationMode": "cooperative",
        "visualPolicy": {"framePath": "FRAME.md", "nativeEvidenceMustRemainNative": True},
        "segments": [
            {
                "id": "seg-001",
                "range": {"startFrame": 0, "endFrame": 300},
                "sourceAnchors": [{"kind": "sentence", "text": "Opening"}],
                "message": "Keep the speaker present.",
                "dominantVisual": {
                    "type": "source-footage",
                    "framePolicy": "source-preserve",
                    "content": {"screenText": "Opening"},
                    "rationale": "Trust starts with the speaker.",
                    "fallback": {"type": "source-footage"},
                },
                "layers": [
                    {
                        "id": "layer-001",
                        "type": "camera",
                        "range": {"startFrame": 0, "endFrame": 240},
                        "catalogId": "layer:slow-push-in",
                        "framePolicy": "source-preserve",
                        "target": "source-main",
                        "content": {},
                    },
                    {
                        "id": "layer-002",
                        "type": "caption",
                        "range": {"startFrame": 120, "endFrame": 300},
                        "framePolicy": "source-preserve",
                        "target": "source-main",
                        "content": {"text": "Opening"},
                    },
                ],
                "route": "source-only",
                "assetRequestIds": [],
                "approval": {"state": "approved"},
            },
            {
                "id": "seg-002",
                "range": {"startFrame": 300, "endFrame": 600},
                "sourceAnchors": [{"kind": "sentence", "text": "Answer"}],
                "message": "Show the native product exchange.",
                "dominantVisual": {
                    "type": "registry-block",
                    "catalogId": "registry-block:chatgpt-desktop-exchange",
                    "framePolicy": "native-evidence",
                    "content": {"prompt": "Why?", "answer": "Because."},
                    "rationale": "The UI is evidence.",
                    "fallback": {"type": "external-evidence"},
                },
                "layers": [],
                "route": "direct-build",
                "assetRequestIds": [],
                "approval": {"state": "locked"},
            },
        ],
        "edges": [{"id": "edge-001", "fromSegmentId": "seg-001", "toSegmentId": "seg-002", "boundaryFrame": 300, "kind": "hard-cut"}],
        "assetRequests": [],
        "libraryLock": {"catalogSha256": "sha256:catalog", "entries": []},
        "approval": {"state": "in-review", "approvedRevision": None, "approvedHash": None},
        "audit": [],
    }


class DirectorPlanTests(unittest.TestCase):
    def test_valid_plan_and_metrics(self):
        plan = valid_plan()
        self.assertEqual([], director.validate_plan(plan, catalog()))
        metrics = director.plan_metrics(plan)
        self.assertEqual(100.0, metrics["dominantVisualCoveragePercent"])
        self.assertEqual(40.0, metrics["layerCoveragePercent"]["camera"])
        self.assertEqual(30.0, metrics["layerCoveragePercent"]["caption"])

    def test_gap_and_overlap_fail_but_overlapping_layers_are_legal(self):
        plan = valid_plan()
        plan["segments"][1]["range"]["startFrame"] = 320
        self.assertTrue(any("gap" in error for error in director.validate_plan(plan, catalog())))
        plan = valid_plan()
        plan["segments"][1]["range"]["startFrame"] = 280
        self.assertTrue(any("overlap" in error for error in director.validate_plan(plan, catalog())))
        self.assertFalse(any("layer" in error and "overlap" in error for error in director.validate_plan(valid_plan(), catalog())))

    def test_native_evidence_and_catalog_status_are_enforced(self):
        plan = valid_plan()
        plan["segments"][1]["dominantVisual"]["framePolicy"] = "frame-governed"
        self.assertTrue(any("native-evidence" in error for error in director.validate_plan(plan, catalog())))
        plan = valid_plan()
        plan["segments"][0]["layers"][0]["catalogId"] = "talkcraft:unverified-card"
        self.assertTrue(any("not ready" in error for error in director.validate_plan(plan, catalog())))

    def test_patch_is_revision_safe_and_respects_locks(self):
        plan = valid_plan()
        with self.assertRaises(director.RevisionConflict):
            director.apply_patch(plan, {"baseRevision": 0, "operations": []}, "human")
        with self.assertRaises(director.LockConflict):
            director.apply_patch(
                plan,
                {"baseRevision": 1, "operations": [{"type": "set-route", "segmentId": "seg-002", "route": "curated-intake"}]},
                "human",
            )
        updated = director.apply_patch(
            plan,
            {"baseRevision": 1, "operations": [{"type": "comment", "targetId": "seg-002", "body": "Keep this exact UI."}]},
            "human",
        )
        self.assertEqual(2, updated["revision"])
        self.assertEqual("comment", updated["audit"][-1]["operations"][0]["type"])

    def test_changed_source_marks_only_affected_segments_stale(self):
        plan = valid_plan()
        updated = director.mark_source_changes(plan, {"source-main": "sha256:new"})
        self.assertTrue(updated["segments"][0]["stale"])
        self.assertFalse(updated["segments"][1].get("stale", False))

    def test_boundary_patch_updates_both_segments_and_edge(self):
        plan = valid_plan()
        plan["segments"][1]["approval"]["state"] = "approved"
        updated = director.apply_patch(plan, {"baseRevision": 1, "operations": [{"type": "set-boundary", "leftSegmentId": "seg-001", "rightSegmentId": "seg-002", "frame": 330}]}, "human", catalog())
        self.assertEqual(330, updated["segments"][0]["range"]["endFrame"])
        self.assertEqual(330, updated["segments"][1]["range"]["startFrame"])
        self.assertEqual(330, updated["edges"][0]["boundaryFrame"])

    def test_handoffs_derive_from_the_plan(self):
        plan = valid_plan()
        plan["approval"] = {"state": "approved", "approvedRevision": 1, "approvedHash": director.plan_hash(plan)}
        packets = director.compile_handoffs(plan)
        self.assertEqual({"source-only", "direct-build"}, set(packets))
        self.assertEqual(["seg-002"], [item["segmentId"] for item in packets["direct-build"]])

    def test_curated_handoff_carries_parent_authority_and_open_scope_question(self):
        plan = valid_plan()
        plan["segments"][1]["route"] = "curated-intake"
        plan["segments"][1]["approval"]["state"] = "approved"
        plan["approval"] = {"state": "approved", "approvedRevision": 1, "approvedHash": director.plan_hash(plan)}
        packet = director.compile_handoffs(plan)["curated-intake"][0]
        self.assertEqual("hyperframes-visual-director/curated-request-v3", packet["schemaVersion"])
        self.assertEqual(["seg-002"], packet["segmentIds"])
        self.assertEqual({"seg-002": []}, packet["approvedScope"]["segmentSceneMap"])
        self.assertFalse(packet["approvedScope"]["animationSentencesLocked"])
        self.assertTrue(packet["questionsStillOpen"])

    def test_curated_v3_merge_uses_stable_scene_ids_and_preserves_scene_locks(self):
        plan = valid_plan()
        segment = plan["segments"][1]
        segment["route"] = "curated-intake"
        segment["approval"]["state"] = "approved"
        parent_hash = director.plan_hash(plan)
        request = {
            "parentPlanHash": parent_hash,
            "segmentIds": ["seg-002"],
            "approvedScope": {
                "segmentSceneMap": {"seg-002": ["scene-proof"]},
                "sceneLocks": {"scene-proof": {"content": True}},
            },
            "lockedDecisions": [],
        }
        patch = {
            "segmentId": "seg-002", "sceneId": "scene-proof", "start": 0, "end": 5,
            "content": "Show the approved evidence.", "visual": "The native exchange remains legible.",
            "uses": [{"id": "authored:native-exchange", "responsibilities": ["Show the approved evidence"], "required": True}],
            "motion": "Internal change: the answer resolves while the source remains visible.",
            "locks": {"content": True},
        }
        result = {
            "schemaVersion": "hyperframes-visual-director/curated-result-v3",
            "parentPlanHash": parent_hash,
            "clusterId": "teach-seg-002",
            "requestedSegmentIds": ["seg-002"],
            "scenePatches": [patch],
            "catalogMisses": [],
            "scopeChangeProposal": None,
        }
        with self.assertRaisesRegex(curated_merge.PatchError, "request-locked"):
            curated_merge.merge_result(plan, result, request=request)
        request["approvedScope"]["sceneLocks"] = {}
        merged = curated_merge.merge_result(plan, result, request=request)
        scene = merged["segments"][1]["curated"]["storyboardScenes"][0]
        self.assertEqual("scene-proof", scene["id"])
        self.assertEqual("Show the approved evidence.", scene["content"])
        changed = copy.deepcopy(result)
        changed["parentPlanHash"] = director.plan_hash(merged)
        changed["scenePatches"][0] = {"segmentId": "seg-002", "sceneId": "scene-proof", "content": "Overwrite"}
        request["parentPlanHash"] = changed["parentPlanHash"]
        with self.assertRaisesRegex(curated_merge.PatchError, "scene-locked"):
            curated_merge.merge_result(merged, changed, request=request)

    def test_curated_merge_rejects_unknown_duplicate_and_cross_segment_scene_membership(self):
        plan = valid_plan()
        for segment in plan["segments"]:
            segment["route"] = "curated-intake"
            segment["approval"]["state"] = "approved"
        parent_hash = director.plan_hash(plan)
        request = {
            "parentPlanHash": parent_hash, "segmentIds": ["seg-001", "seg-002"], "lockedDecisions": [],
            "approvedScope": {"segmentSceneMap": {"seg-001": ["scene-a"], "seg-002": ["scene-b"]}, "sceneLocks": {}},
        }
        patch = {
            "segmentId": "seg-001", "sceneId": "scene-a", "start": 0, "end": 2,
            "content": "A", "visual": "A visual", "uses": [], "motion": "A changes.",
        }
        result = {"schemaVersion": "hyperframes-visual-director/curated-result-v3", "parentPlanHash": parent_hash, "clusterId": "teach-both", "requestedSegmentIds": ["seg-001", "seg-002"], "scenePatches": [patch], "catalogMisses": [], "scopeChangeProposal": None}

        unknown = copy.deepcopy(result)
        unknown["scenePatches"][0]["sceneId"] = "scene-unknown"
        with self.assertRaisesRegex(curated_merge.PatchError, "outside approved"):
            curated_merge.merge_result(plan, unknown, request=request)
        cross = copy.deepcopy(result)
        cross["scenePatches"][0]["segmentId"] = "seg-002"
        with self.assertRaisesRegex(curated_merge.PatchError, "belongs to"):
            curated_merge.merge_result(plan, cross, request=request)
        duplicate_request = copy.deepcopy(request)
        duplicate_request["approvedScope"]["segmentSceneMap"]["seg-002"] = ["scene-a"]
        with self.assertRaisesRegex(curated_merge.PatchError, "multiple segments"):
            curated_merge.merge_result(plan, result, request=duplicate_request)
        duplicate_result = copy.deepcopy(result)
        duplicate_result["scenePatches"].append(copy.deepcopy(patch))
        with self.assertRaisesRegex(curated_merge.PatchError, "repeats scene patch"):
            curated_merge.merge_result(plan, duplicate_result, request=request)


if __name__ == "__main__":
    unittest.main()
