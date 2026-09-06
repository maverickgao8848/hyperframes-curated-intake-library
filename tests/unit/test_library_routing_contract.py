from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROOT_LIBRARY = ROOT / "library"
LIBRARY = ROOT / ".agents/skills/hyperframes-curated-intake/assets/library"
SCRIPTS = ROOT / ".agents/skills/hyperframes-curated-intake/scripts"
sys.path.insert(0, str(SCRIPTS))
DEFAULT_LIBRARY_CLIS = (
    "select-project-palette.py",
    "prepare-project.py",
    "stage-selected-items.py",
    "apply-video-spec-refactor.py",
    "build-director-catalog.py",
    "build-legacy-aliases.py",
    "verify-legacy-registry.py",
    "verify-library-contract.py",
    "inventory-library.py",
    "build-registry-view.py",
)


def load_routing():
    spec = importlib.util.spec_from_file_location("curated_routing", SCRIPTS / "_routing.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LibraryRoutingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
        cls.index = {entry["id"]: entry for entry in cls.catalog["entries"]}
        cls.routing = load_routing()

    def test_library_contract_and_director_derivation_are_current(self):
        self.assertFalse(ROOT_LIBRARY.exists(), "the retired root library mirror must not be recreated")
        verify = subprocess.run(
            [sys.executable, str(SCRIPTS / "verify-library-contract.py")],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, verify.returncode, verify.stdout + verify.stderr)
        report = json.loads(verify.stdout)
        self.assertEqual(162, report["summary"]["readyRegistry"])
        self.assertEqual(162, report["summary"]["installable"])
        self.assertEqual(68, report["summary"]["legacyReady"])
        self.assertGreaterEqual(report["summary"]["coverage"], 0.8)
        builder = importlib.util.spec_from_file_location("director_builder_d2", SCRIPTS / "build-director-catalog.py")
        builder_module = importlib.util.module_from_spec(builder)
        assert builder.loader is not None
        builder.loader.exec_module(builder_module)
        derived = builder_module.build(LIBRARY)
        talkcraft = json.loads((LIBRARY / "talkcraft-inventory.json").read_text(encoding="utf-8"))["entries"]
        derived_talkcraft = [entry for entry in derived["entries"] if str(entry.get("id", "")).startswith("talkcraft:")]
        self.assertEqual(talkcraft, derived_talkcraft, "TalkCraft must pass through without synthesized routing metadata")

        legacy = subprocess.run(
            [sys.executable, str(SCRIPTS / "verify-legacy-registry.py"), "--library", str(LIBRARY)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, legacy.returncode, legacy.stdout + legacy.stderr)
        legacy_report = json.loads(legacy.stdout)
        self.assertEqual(68, legacy_report["summary"]["registryArtifacts"])
        self.assertEqual(68, legacy_report["summary"]["mountExports"])
        self.assertEqual(68, legacy_report["summary"]["seekSafeClosures"])
        self.assertFalse(ROOT_LIBRARY.exists(), "library checks must not recreate the retired root mirror")

    def test_three_skill_output_boundaries_share_one_current_inventory_authority(self):
        curated = (ROOT / ".agents/skills/hyperframes-curated-intake/SKILL.md").read_text(encoding="utf-8")
        brief = (ROOT / ".agents/skills/hyperframes-brief-controller/SKILL.md").read_text(encoding="utf-8")
        director = (ROOT / ".agents/skills/hyperframes-visual-director/SKILL.md").read_text(encoding="utf-8")
        for contract in (curated, brief, director):
            self.assertIn("inventory-latest.json", contract)
            self.assertNotIn("curated-library-inventory.json", contract)
        self.assertIn("generate only `BRIEF.md`, `frame.md`, `STORYBOARD.md`", curated)
        self.assertIn("Write exactly two project artifacts", brief)
        self.assertIn("does not own teaching-scene detail, composition HTML, Studio, render", director)
        direct_contracts = (
            ROOT / ".agents/skills/hyperframes-curated-intake/references/artifact-contract.md",
            ROOT / ".agents/skills/hyperframes-brief-controller/references/brief-contract.md",
            ROOT / ".agents/skills/hyperframes-visual-director/references/director-model.md",
        )
        for path in direct_contracts:
            text = path.read_text(encoding="utf-8")
            self.assertIn("inventory-latest.json", text)
            self.assertNotIn("curated-library-inventory.json", text)
        self.assertFalse((ROOT / ".agents/skills/hyperframes-curated-intake/references/curated-intake-result.v2.legacy.schema.json").exists())
        self.assertFalse((LIBRARY / "provenance/curated-library-inventory.json").exists())
        self.assertTrue((LIBRARY / "inventory-latest.json").is_file())

    def test_all_curated_library_clis_share_one_cwd_independent_default_and_allow_override(self):
        self.assertFalse(ROOT_LIBRARY.exists(), "only the skill-owned canonical library may exist")
        registry = importlib.util.spec_from_file_location("curated_registry", SCRIPTS / "_registry.py")
        module = importlib.util.module_from_spec(registry)
        assert registry.loader is not None
        registry.loader.exec_module(module)
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as temp:
            try:
                os.chdir(temp)
                self.assertEqual(LIBRARY.resolve(), module.default_library().resolve())
            finally:
                os.chdir(previous)

        for filename in DEFAULT_LIBRARY_CLIS:
            tree = ast.parse((SCRIPTS / filename).read_text(encoding="utf-8"), filename=filename)
            actions = [
                node for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "--library"
            ]
            self.assertEqual(1, len(actions), filename)
            keywords = {keyword.arg: keyword.value for keyword in actions[0].keywords}
            default = keywords.get("default")
            self.assertIsInstance(default, ast.Call, filename)
            self.assertIsInstance(default.func, ast.Name, filename)
            self.assertEqual("default_library", default.func.id, filename)
            self.assertNotEqual(True, getattr(keywords.get("required"), "value", False), filename)
            value_type = keywords.get("type")
            self.assertIsInstance(value_type, ast.Name, filename)
            self.assertEqual("Path", value_type.id, filename)

    def test_legacy_alias_source_is_library_root_relative_for_default_and_override(self):
        self.assertFalse(ROOT_LIBRARY.exists(), "the retired root mirror must not be a generator target")
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            default_output = temp_root / "default-aliases.json"
            default_result = subprocess.run(
                [sys.executable, str(SCRIPTS / "build-legacy-aliases.py"), "--output", str(default_output)],
                cwd=temp_root, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, default_result.returncode, default_result.stdout + default_result.stderr)
            default_payload = json.loads(default_output.read_text(encoding="utf-8"))
            self.assertEqual("catalog.json", default_payload["source"])

            library = temp_root / "external-library"
            library.mkdir()
            (library / "catalog.json").write_text(json.dumps({"entries": []}), encoding="utf-8")
            output = temp_root / "aliases.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "build-legacy-aliases.py"), "--library", str(library), "--output", str(output)],
                cwd=temp_root, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("catalog.json", payload["source"])
        self.assertFalse(ROOT_LIBRARY.exists(), "explicit overrides must not recreate the retired root mirror")

    def test_default_and_explicit_staging_frame_and_director_selection_use_canonical_library(self):
        self.assertFalse(ROOT_LIBRARY.exists(), "staging must not fall back to the retired root mirror")
        component_id = "registry-component:flow-complex"
        component = self.index[component_id]
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            receipts = []
            for name, library_args in (("default", []), ("explicit", ["--library", str(LIBRARY)])):
                project = temp_root / name
                compiled = project / ".hyperframes/compiled"
                compiled.mkdir(parents=True)
                storyboard = {
                    "schema": "hyperframes-storyboard/v3",
                    "title": "Staging",
                    "duration": 3,
                    "timing_mode": "locked",
                    "scenes": [{
                        "id": "scene-one", "start": 0, "end": 3,
                        "content": "Stage the selected component.",
                        "visual": "The component fills the frame.",
                        "motion": "The component settles into its final state.",
                        "uses": [{"id": component_id, "responsibilities": ["Show the selected component"], "required": True}],
                    }]
                }
                (compiled / "storyboard.json").write_text(json.dumps({"schemaVersion": "hyperframes-storyboard-compiled/v3", "storyboard": storyboard}), encoding="utf-8")
                storyboard_hash = hashlib.sha256(json.dumps(storyboard, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
                (project / ".hyperframes/curation.json").write_text(
                    json.dumps({"schemaVersion": "hyperframes-curated-intake/v5", "policy": "approved-first", "frame": {"preset": "fixture", "projectPath": "frame.md", "sourcePath": "frames/cobalt-grid/FRAME.md", "sourceSha256": "0" * 64}, "registry": {}, "needs": [], "selectedIds": [component_id], "catalogMisses": [], "recipeResolutions": [], "storyboardHash": storyboard_hash, "review": {"state": "approved", "storyboardHash": storyboard_hash, "source": "automated-agent-attestation", "unresolvedSceneIds": [], "reviewer": {"type": "automated-agent", "workflow": "curated-intake", "rubricVersion": "motion-attestation/v1", "modelId": "fixture-agent"}, "sceneReviews": []}}), encoding="utf-8"
                )
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS / "stage-selected-items.py"), "--project", str(project), "--all-required", *library_args],
                    cwd=temp_root, text=True, capture_output=True, check=False,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                receipt = json.loads((project / ".hyperframes/staging-receipt.json").read_text(encoding="utf-8"))
                receipts.append(receipt)
                for record in receipt["items"][0]["files"]:
                    source = LIBRARY / record["sourcePath"]
                    destination = project / record["destinationPath"]
                    self.assertTrue(destination.is_file())
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), record["sourceHash"])
                    self.assertEqual(hashlib.sha256(destination.read_bytes()).hexdigest(), record["destinationHash"])
            self.assertEqual(receipts[0], receipts[1])

            frame_inventory = json.loads((LIBRARY / "frames/inventory.json").read_text(encoding="utf-8"))
            frame = next(item for item in frame_inventory["frames"] if item["preset"] == "cobalt-grid")
            source_frame = LIBRARY / frame["path"]
            staged_frame = temp_root / "frame.md"
            staged_frame.write_bytes(source_frame.read_bytes())
            self.assertEqual(frame["sha256"], hashlib.sha256(staged_frame.read_bytes()).hexdigest())

            director = json.loads((LIBRARY / "director-catalog.json").read_text(encoding="utf-8"))
            talkcraft = next(entry for entry in director["entries"] if entry["id"] == "talkcraft:alt-block-lines")
            self.assertEqual("candidate", talkcraft["status"])
            self.assertEqual("linted", talkcraft["portStatus"])
            self.assertNotIn(talkcraft["id"], {entry["id"] for entry in self.catalog["entries"] if entry.get("status") == "ready"})

    def test_plan_blocks_and_special_components_have_revision15_routing(self):
        blocks = {
            "chatgpt-desktop-exchange", "wechat-desktop-exchange", "code-snippet-apple-terminal-clear-dark",
            "code-typing", "film-credits-stagger", "lower-third-bild", "news-ticker", "notes-reveal",
            "telemetry-hud", "testimonial-proof-card", "us-map-hex", "x-post", "yt-comment-card", "hw-pipeline",
        }
        for name in blocks:
            entry = self.index[f"registry-block:{name}"]
            self.assertEqual("ready", entry["status"])
            self.assertEqual(
                {"family", "purpose", "useWhen", "avoidWhen", "expects", "motion"},
                set(entry["routing"]) - {"fallbackIds"},
            )
        for name in ("caption-blend-difference", "grain-overlay", "grid-pixelate-wipe", "inline-highlight", "typewriter"):
            entry = self.index[f"registry-component:{name}"]
            self.assertEqual(
                {"family", "purpose", "useWhen", "avoidWhen", "expects", "motion"},
                set(entry["routing"]) - {"fallbackIds"},
            )

    def test_aliases_are_complete_and_placeholder_is_no_recommendation(self):
        aliases = json.loads((LIBRARY / "legacy-component-aliases.json").read_text(encoding="utf-8"))["aliases"]
        self.assertEqual(69, len(aliases))
        self.assertEqual("no_recommendation", aliases["broll-abstract.placeholder"]["result"])
        self.assertIsNone(self.routing.resolve_alias("broll-abstract.placeholder", aliases))

    def test_hard_filters_and_ranking_are_deterministic(self):
        base = {
            "kind": "registry-component", "status": "ready",
            "license": {"status": "local-reuse"}, "integration": {"mode": "host-dom", "timelineOwner": "host", "renderTimeNetwork": False},
            "parameters": {"required": ["value"]}, "aspectSupport": ["16:9"], "duration": 4, "fps": 60,
            "routing": {"family": "data", "purpose": "Show the value", "useWhen": ["A value must be compared"], "avoidWhen": ["No value is available"], "expects": ["A meaningful value"], "motion": "stateful"},
            "source": {"type": "bundle", "name": "a", "entry": "a.js", "files": [{"path": "a.js", "sha256": "0" * 64}]},
            "sha256": "0" * 64,
        }
        first = dict(base, id="registry-component:a")
        second = dict(base, id="registry-component:b", source={"name": "b"})
        context = {"family": "data", "purpose": "Show the value", "useWhen": ["A value must be compared"], "available_inputs": ["value"], "aspect": "16:9", "duration_seconds": 2, "fps": 60}
        installable = {("a", "hyperframes:component"), ("b", "hyperframes:component")}
        one = self.routing.recommend([second, first], context, installable_registry=installable, prior_use={"registry-component:a": 1})
        two = self.routing.recommend([first, second], context, installable_registry=installable, prior_use={"registry-component:a": 1})
        self.assertEqual(one, two)
        self.assertEqual("registry-component:b", one["selected"])
        no_match = self.routing.recommend([first], dict(context, aspect="9:16"), installable_registry=installable)
        self.assertEqual("no_recommendation", no_match["status"])
        self.assertEqual("aspect", next(result["filter"] for result in no_match["rejections"][0]["hardFilterResults"] if not result["passed"]))


if __name__ == "__main__":
    unittest.main()
