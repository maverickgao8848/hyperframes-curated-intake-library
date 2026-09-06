from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / ".agents" / "skills" / "hyperframes-visual-director" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / file)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(value)
    return value


director = module("director_plan_workbench", "director_plan.py")
workbench = module("workbench_server", "workbench_server.py")


class WorkbenchTests(unittest.TestCase):
    def test_store_persists_patch_and_audit(self):
        from test_visual_director import catalog, valid_plan

        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            (project / "director-plan.json").write_text(json.dumps(valid_plan()), encoding="utf-8")
            catalog_path = project / "catalog.json"
            catalog_path.write_text(json.dumps(catalog()), encoding="utf-8")
            store = workbench.WorkbenchStore(project, catalog_path)
            result = store.patch({"baseRevision": 1, "operations": [{"type": "comment", "targetId": "seg-001", "body": "Looks good."}]})
            self.assertEqual(2, result["plan"]["revision"])
            reopened = workbench.WorkbenchStore(project, catalog_path).read()
            self.assertEqual(2, reopened["plan"]["revision"])
            self.assertEqual("Looks good.", reopened["plan"]["audit"][-1]["operations"][0]["body"])

    def test_workbench_is_plan_derived_and_has_no_model_endpoint(self):
        html = (SCRIPT_DIR.parent / "assets" / "workbench" / "index.html").read_text(encoding="utf-8")
        app = (SCRIPT_DIR.parent / "assets" / "workbench" / "app.js").read_text(encoding="utf-8")
        self.assertIn("多轨时间线", html)
        self.assertIn("素材待办", html)
        self.assertIn("片段审阅", html)
        self.assertIn("技术详情", html)
        self.assertIn("内容", app)
        self.assertIn("主画面", app)
        self.assertIn("辅助层", app)
        self.assertIn("转场", app)
        self.assertNotIn("Transcript", app)
        self.assertNotIn("Dominant visual", app)
        self.assertIn("/api/plan", app)
        self.assertIn("/api/patch", app)
        self.assertNotIn("/api/model", app)
        self.assertNotIn("localStorage", app)


if __name__ == "__main__":
    unittest.main()
