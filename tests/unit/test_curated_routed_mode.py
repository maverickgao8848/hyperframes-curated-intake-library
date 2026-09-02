from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CURATED = ROOT / ".agents" / "skills" / "hyperframes-curated-intake" / "scripts"
DIRECTOR = ROOT / ".agents" / "skills" / "hyperframes-visual-director" / "scripts"
sys.path[:0] = [str(CURATED), str(DIRECTOR)]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


routed = load("curated_routed", CURATED / "_routed.py")
merge = load("merge_curated", DIRECTOR / "merge-curated-result.py")


class RoutedCuratedTests(unittest.TestCase):
    def parent_plan(self):
        from test_visual_director import valid_plan

        plan = valid_plan()
        plan["segments"][1]["route"] = "curated-intake"
        return plan

    def write_request(self, root: Path, plan: dict, *, hash_value: str | None = None, segment_ids=None) -> Path:
        parent = root / "director-plan.json"
        parent.write_text(json.dumps(plan), encoding="utf-8")
        request = {
            "schemaVersion": "hyperframes-visual-director/curated-request-v1",
            "parentPlanPath": "director-plan.json",
            "parentPlanHash": hash_value or routed.canonical_hash(plan),
            "clusterId": "teach-001",
            "segmentIds": segment_ids or ["seg-002"],
            "approvedScope": {"segmentIds": segment_ids or ["seg-002"], "animationSentencesLocked": True},
            "lockedDecisions": ["range", "dominantVisual", "route"],
            "inheritedVisualPolicy": plan["visualPolicy"],
            "timing": plan["timing"],
            "assets": [],
            "questionsStillOpen": [],
        }
        path = root / "curated-intake-request.json"
        path.write_text(json.dumps(request), encoding="utf-8")
        return path

    def test_valid_request_binds_parent_scope_and_hash(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            path = self.write_request(root, self.parent_plan())
            request, parent = routed.validate_request(path)
            self.assertEqual(["seg-002"], request["segmentIds"])
            self.assertEqual("curated-intake", parent["segments"][1]["route"])

    def test_stale_hash_and_non_curated_scope_are_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            with self.assertRaisesRegex(ValueError, "parentPlanHash"):
                routed.validate_request(self.write_request(root, self.parent_plan(), hash_value="sha256:" + "0" * 64))
            with self.assertRaisesRegex(ValueError, "non-Curated"):
                routed.validate_request(self.write_request(root, self.parent_plan(), segment_ids=["seg-001"]))

    def test_result_cannot_modify_locked_or_out_of_scope_parent_fields(self):
        plan = self.parent_plan()
        result = {
            "schemaVersion": "hyperframes-visual-director/curated-result-v1",
            "parentPlanHash": routed.canonical_hash(plan),
            "clusterId": "teach-001",
            "segmentIds": ["seg-002"],
            "lockedDecisions": ["range", "dominantVisual", "route"],
            "segmentUpdates": [{"segmentId": "seg-002", "range": {"startFrame": 250, "endFrame": 600}, "sceneContracts": [], "beats": [], "components": [], "questionsResolved": []}],
            "scopeChangeProposal": None,
        }
        with self.assertRaisesRegex(Exception, "locked decisions"):
            merge.merge_result(plan, result)
        result["segmentUpdates"][0].pop("range")
        updated = merge.merge_result(plan, result)
        self.assertIn("curated", updated["segments"][1])
        self.assertEqual("proposed", updated["segments"][1]["approval"]["state"])
        self.assertEqual(300, updated["segments"][1]["range"]["startFrame"])

    def test_standalone_skill_text_still_requires_animation_scope(self):
        skill = (CURATED.parent / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("哪些段落/时间范围需要动画", skill)
        self.assertIn("Standalone", skill)
        self.assertIn("Routed", skill)


if __name__ == "__main__":
    unittest.main()
