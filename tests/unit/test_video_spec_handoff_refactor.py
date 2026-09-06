from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/hyperframes-curated-intake"
SCRIPTS = SKILL / "scripts"
LIBRARY = SKILL / "assets/library"
STORYBOARD_SCHEMA = json.loads(
    (SKILL / "references/storyboard-spec.schema.json").read_text(encoding="utf-8")
)
PYTHON = sys.executable


def object_hash(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def storyboard(*item_ids: str, required: bool = True) -> dict:
    return {
        "schema": "hyperframes-storyboard/v3",
        "title": "Current v3 handoff regression",
        "duration": 3,
        "timing_mode": "locked",
        "scenes": [{
            "id": "scene-media", "start": 0, "end": 3,
            "content": "Show the selected evidence.",
            "visual": "The selected evidence remains legible.",
            "motion": "The evidence enters once and holds.",
            "uses": [{
                "id": item_id,
                "responsibilities": [f"Present {item_id}"],
                "required": required,
            } for item_id in item_ids],
        }],
    }


def approved_review(value: dict) -> dict:
    return {
        "state": "approved",
        "storyboardHash": object_hash(value),
        "source": "automated-agent-attestation",
        "unresolvedSceneIds": [],
        "reviewer": {
            "type": "automated-agent", "workflow": "curated-intake",
            "rubricVersion": "motion-attestation/v1", "modelId": "v3-regression-agent",
        },
        "sceneReviews": [],
    }


class VideoSpecHandoffRefactorTests(unittest.TestCase):
    def run_script(
        self, name: str, *args: object, expect: int = 0
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [PYTHON, str(SCRIPTS / name), *(str(arg) for arg in args)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(expect, result.returncode, result.stdout + result.stderr)
        return result

    @staticmethod
    def write_json(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_all_eight_inventory_frames_materialize_byte_exact(self):
        inventory = json.loads((LIBRARY / "frames/inventory.json").read_text(encoding="utf-8"))
        catalog = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
        frames = inventory["frames"]
        item_ids = [
            entry["id"] for entry in catalog["entries"]
            if entry["kind"] == "logo" and entry["status"] == "ready"
        ][:8]
        self.assertEqual(8, len(frames))
        self.assertEqual(8, len(item_ids))
        self.assertEqual(8, len(set(item_ids)))

        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            spec = storyboard(*item_ids)
            spec_path = temp_root / "storyboard.json"
            review_path = temp_root / "review.json"
            self.write_json(spec_path, spec)
            self.write_json(review_path, approved_review(spec))

            for frame in frames:
                project = temp_root / "projects" / frame["preset"]
                curation_path = temp_root / "curation" / f"{frame['preset']}.json"
                self.run_script(
                    "select-project-palette.py", "--library", LIBRARY,
                    "--storyboard-spec", spec_path, "--frame-preset", frame["preset"],
                    "--review-confirmation", review_path, "--output", curation_path,
                )
                curation = json.loads(curation_path.read_text(encoding="utf-8"))
                self.assertEqual([], curation["catalogMisses"])
                self.run_script(
                    "prepare-project.py", "--project", project, "--library", LIBRARY,
                    "--curation", curation_path, "--storyboard-spec", spec_path,
                    "--intent", "Verify every canonical Frame", "--destination", "test",
                    "--language", "en",
                )
                self.run_script(
                    "stage-selected-items.py", "--project", project, "--library", LIBRARY,
                    "--all-required",
                )

                source = LIBRARY / frame["path"]
                observed = project / "frame.md"
                self.assertEqual(source.stat().st_size, observed.stat().st_size)
                self.assertEqual(source.read_bytes(), observed.read_bytes())
                self.assertEqual(frame["sha256"], hashlib.sha256(observed.read_bytes()).hexdigest())

                receipt = json.loads(
                    (project / ".hyperframes/staging-receipt.json").read_text(encoding="utf-8")
                )
                receipt_ids = [item["id"] for item in receipt["items"]]
                self.assertEqual(item_ids, receipt_ids)
                self.assertEqual(8, len(set(receipt_ids)))
                for item in receipt["items"]:
                    for record in item["files"]:
                        source_path = LIBRARY / record["sourcePath"]
                        destination = project / record["destinationPath"]
                        self.assertEqual(source_path.stat().st_size, destination.stat().st_size)
                        self.assertEqual(record["sourceHash"], record["destinationHash"])
                        self.assertEqual(
                            record["sourceHash"], hashlib.sha256(destination.read_bytes()).hexdigest()
                        )

    def test_v3_handoff_hashes_and_output_boundaries_fail_closed_on_missing_or_tampered_media(self):
        from test_curated_intake_workflow import prepare

        with tempfile.TemporaryDirectory() as temp:
            project, library, _ = prepare(Path(temp))
            self.run_script(
                "stage-selected-items.py", "--project", project, "--library", library,
                "--all-required",
            )
            verified = self.run_script("verify-handoff.py", "--project", project)
            self.assertTrue(json.loads(verified.stdout)["ok"])

            expected_top_level = {
                ".hyperframes", "assets", "compositions", "BRIEF.md", "frame.md",
                "HANDOFF.md", "hyperframes.json", "STORYBOARD.md",
            }
            self.assertEqual(expected_top_level, {path.name for path in project.iterdir()})
            for forbidden in ("video-spec.md", ".media", "scene-contracts"):
                self.assertFalse((project / forbidden).exists())

            manifest = json.loads(
                (project / ".hyperframes/intake-manifest.json").read_text(encoding="utf-8")
            )
            for relative, expected in manifest["hashes"].items():
                self.assertEqual(expected, hashlib.sha256((project / relative).read_bytes()).hexdigest())
            receipt = json.loads(
                (project / ".hyperframes/staging-receipt.json").read_text(encoding="utf-8")
            )
            staged = receipt["items"][0]["files"][0]
            staged_path = project / staged["destinationPath"]
            original = staged_path.read_bytes()
            self.assertEqual(staged["sourceHash"], staged["destinationHash"])

            staged_path.unlink()
            missing = self.run_script("verify-handoff.py", "--project", project, expect=1)
            self.assertIn('"code": "staging-hash"', missing.stdout)
            self.assertIn("Staged file is missing, outside project, or changed", missing.stdout)
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path.write_bytes(original + b"tampered")
            tampered = self.run_script("verify-handoff.py", "--project", project, expect=1)
            self.assertIn('"code": "staging-hash"', tampered.stdout)
            self.assertIn("Staged file is missing, outside project, or changed", tampered.stdout)

    def test_template_namespace_and_runtime_integration_are_schema_driven_and_fail_closed(self):
        jsonschema.validate(storyboard("template:example"), STORYBOARD_SCHEMA)
        for item_id in ("unknown:example", "Template:example", "template:", "template"):
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(storyboard(item_id), STORYBOARD_SCHEMA)

        from test_curated_intake_workflow import make_library, make_review, make_storyboard

        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            library = make_library(temp_root)
            spec_path = make_storyboard(temp_root)
            review_path = make_review(temp_root, spec_path)
            catalog_path = library / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["entries"][0]["integration"]["mode"] = "unsupported"
            self.write_json(catalog_path, catalog)
            invalid_integration = self.run_script(
                "select-project-palette.py", "--library", library,
                "--storyboard-spec", spec_path, "--frame-preset", "cobalt",
                "--review-confirmation", review_path,
                "--output", temp_root / "invalid-integration.json", expect=1,
            )
            self.assertIn("Catalog configuration error", invalid_integration.stderr)
            self.assertIn("integration", invalid_integration.stderr)

            stage_root = temp_root / "missing-source"
            library = make_library(stage_root)
            spec_path = make_storyboard(stage_root)
            review_path = make_review(stage_root, spec_path)
            (library / "media/svg/document.svg").unlink()
            unavailable = self.run_script(
                "select-project-palette.py", "--library", library,
                "--storyboard-spec", spec_path, "--frame-preset", "cobalt",
                "--review-confirmation", review_path,
                "--output", stage_root / "unavailable.json", expect=1,
            )
            self.assertIn("s01-select/svg:primitive:document", unavailable.stderr)
            self.assertIn("hash", unavailable.stderr.lower())

    def test_unknown_v3_use_is_visible_in_curation_and_rejected_at_every_production_boundary(self):
        from test_curated_intake_workflow import make_library

        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            library = make_library(temp_root)
            missing_id = "logo:missing"
            optional = storyboard(missing_id, required=False)
            optional_path = temp_root / "optional.json"
            optional_review = temp_root / "optional-review.json"
            curation_path = temp_root / "curation.json"
            self.write_json(optional_path, optional)
            self.write_json(optional_review, approved_review(optional))
            self.run_script(
                "select-project-palette.py", "--library", library,
                "--storyboard-spec", optional_path, "--frame-preset", "cobalt",
                "--review-confirmation", optional_review, "--output", curation_path,
            )
            curation = json.loads(curation_path.read_text(encoding="utf-8"))
            miss = curation["catalogMisses"][0]
            self.assertEqual("scene-media", miss["sceneId"])
            self.assertIn(missing_id, miss["need"])
            self.assertNotIn(missing_id, curation["selectedIds"])

            required = storyboard(missing_id)
            required_path = temp_root / "required.json"
            required_review = temp_root / "required-review.json"
            self.write_json(required_path, required)
            self.write_json(required_review, approved_review(required))
            selection = self.run_script(
                "select-project-palette.py", "--library", library,
                "--storyboard-spec", required_path, "--frame-preset", "cobalt",
                "--review-confirmation", required_review,
                "--output", temp_root / "required-curation.json", expect=1,
            )
            self.assertIn("scene-media/logo:missing", selection.stderr)
            self.assertIn("unavailable", selection.stderr.lower())

            curation["storyboardHash"] = object_hash(required)
            curation["review"] = approved_review(required)
            self.write_json(curation_path, curation)
            project = temp_root / "project"
            rejected_prepare = self.run_script(
                "prepare-project.py", "--project", project, "--library", library,
                "--curation", curation_path, "--storyboard-spec", required_path,
                "--intent", "Reject unknown required media", "--destination", "test",
                "--language", "en", expect=1,
            )
            self.assertIn(missing_id, rejected_prepare.stderr)
            self.assertIn("absent from curation", rejected_prepare.stderr)

            # Build the optional packet, then make its compiled production authority require it.
            curation["storyboardHash"] = object_hash(optional)
            curation["review"] = approved_review(optional)
            self.write_json(curation_path, curation)
            self.run_script(
                "prepare-project.py", "--project", project, "--library", library,
                "--curation", curation_path, "--storyboard-spec", optional_path,
                "--intent", "Retain a visible optional miss", "--destination", "test",
                "--language", "en",
            )
            compiled_path = project / ".hyperframes/compiled/storyboard.json"
            compiled = json.loads(compiled_path.read_text(encoding="utf-8"))
            compiled["storyboard"] = required
            self.write_json(compiled_path, compiled)
            project_curation_path = project / ".hyperframes/curation.json"
            project_curation = json.loads(project_curation_path.read_text(encoding="utf-8"))
            project_curation["storyboardHash"] = object_hash(required)
            project_curation["review"] = approved_review(required)
            self.write_json(project_curation_path, project_curation)

            rejected_stage = self.run_script(
                "stage-selected-items.py", "--project", project, "--library", library,
                "--all-required", expect=1,
            )
            self.assertIn(missing_id, rejected_stage.stderr)
            self.assertIn("outside the approved Storyboard selection", rejected_stage.stderr)

            rejected_handoff = self.run_script("verify-handoff.py", "--project", project, expect=1)
            rendered = json.dumps(json.loads(rejected_handoff.stdout), ensure_ascii=False)
            self.assertIn("scene-media", rendered)
            self.assertIn(missing_id, rendered)
            self.assertIn("required-not-staged", rendered)


if __name__ == "__main__":
    unittest.main()
