#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from _curation import load_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Build runtime evidence against canonical Storyboard v3 scenes and uses.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def finding(level: str, code: str, message: str) -> dict:
    return {"level": level, "code": code, "message": message}


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    findings = []
    compiled_path = project / ".hyperframes/compiled/storyboard.json"
    curation_path = project / ".hyperframes/curation.json"
    usage_path = project / ".hyperframes/usage.json"
    if not compiled_path.is_file() or not usage_path.is_file():
        missing = "compiled Storyboard" if not compiled_path.is_file() else "usage evidence"
        findings.append(finding("error", "artifact-missing", f"Missing {missing}"))
        storyboard, usage = {"scenes": []}, {}
    else:
        storyboard = load_json(compiled_path).get("storyboard", {})
        usage = load_json(usage_path)
        schema = load_json(Path(__file__).resolve().parents[1] / "references/usage.schema.json")
        for error in Draft202012Validator(schema).iter_errors(usage):
            findings.append(finding("error", "usage-schema", error.message))
    curation = load_json(curation_path) if curation_path.is_file() else {}
    reviewed_decisions = {item.get("sceneId"): item.get("decision") for item in curation.get("review", {}).get("sceneReviews", []) if isinstance(item, dict)}
    recipe_resolutions = {(item.get("sceneId"), item.get("id")): item.get("resolvedId") for item in curation.get("recipeResolutions", []) if isinstance(item, dict)}
    usage_by_scene = {item.get("id"): item for item in usage.get("scenes", []) if isinstance(item, dict)}
    for scene in storyboard.get("scenes", []):
        scene_id = scene["id"]
        composition = project / "compositions" / "frames" / f"{scene_id}.html"
        if not composition.is_file():
            findings.append(finding("error", "composition-missing", f"Missing composition for {scene_id}"))
            continue
        source = composition.read_text(encoding="utf-8")
        if f'data-composition-id="{scene_id}"' not in source and f"data-composition-id='{scene_id}'" not in source:
            findings.append(finding("error", "composition-id", f"Composition ID differs for {scene_id}"))
        evidence = usage_by_scene.get(scene_id, {})
        use_by_id = {item.get("id"): item for item in evidence.get("useEvidence", []) if isinstance(item, dict)}
        for binding in scene["uses"]:
            resolved_id = recipe_resolutions.get((scene_id, binding["id"]), binding["id"])
            if binding["required"] and resolved_id not in use_by_id and not binding["id"].startswith("authored:"):
                findings.append(finding("error", "use-evidence", f"Missing required use evidence: {scene_id}/{resolved_id}"))
        motion = evidence.get("motionEvidence", {})
        if scene["end"] - scene["start"] > 3 and reviewed_decisions.get(scene_id) == "internal-change" and not motion.get("internalChange"):
            findings.append(finding("error", "motion-fidelity", f"Long scene lacks internal semantic-change evidence: {scene_id}"))
        if not motion.get("finalHold"):
            findings.append(finding("error", "final-hold", f"Scene lacks final readable hold evidence: {scene_id}"))
    expected_boundaries = [(scene["id"], scene["next"]["sceneId"], scene["next"]["transition"]) for scene in storyboard.get("scenes", []) if scene.get("next")]
    actual_boundaries = {(item.get("fromScene"), item.get("toScene"), item.get("transition")) for item in usage.get("boundaries", []) if isinstance(item, dict)}
    for boundary in expected_boundaries:
        if boundary not in actual_boundaries:
            findings.append(finding("error", "boundary-evidence", f"Missing outgoing/midpoint/incoming evidence: {boundary[0]} → {boundary[1]}"))
    errors = sum(item["level"] == "error" for item in findings)
    report = {"schemaVersion": "hyperframes-curation-verification/v3", "ok": errors == 0, "errors": errors, "warnings": 0, "findings": findings}
    output = args.output or project / ".hyperframes/curation-verification.json"
    write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
