#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from _curation import CURATION_SCHEMA_VERSION, MANIFEST_SCHEMA_VERSION, load_json, object_sha256, sha256, validate_production_review, validate_recipe_resolutions, validate_storyboard, write_json
from _registry import default_library


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a canonical mav-mg v3 handoff before Build.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--library", type=Path, default=default_library())
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def finding(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    findings: list[dict[str, str]] = []
    required = ["BRIEF.md", "frame.md", "STORYBOARD.md", "HANDOFF.md", "hyperframes.json", ".hyperframes/intake-manifest.json", ".hyperframes/curation.json", ".hyperframes/staging-receipt.json", ".hyperframes/compiled/storyboard.json"]
    for relative in required:
        if not (project / relative).is_file():
            findings.append(finding("error", "artifact-missing", f"Required artifact is missing: {relative}"))
    legacy = [project / "scene-contracts", project / ".hyperframes/build-plan.json", project / ".hyperframes/intake-handoff.json"]
    for path in legacy:
        if path.exists():
            findings.append(finding("error", "legacy-parallel-authority", f"Archive legacy intake authority before v3 Build: {path.relative_to(project).as_posix()}"))
    manifest = load_json(project / ".hyperframes/intake-manifest.json") if (project / ".hyperframes/intake-manifest.json").is_file() else {}
    curation = load_json(project / ".hyperframes/curation.json") if (project / ".hyperframes/curation.json").is_file() else {}
    receipt = load_json(project / ".hyperframes/staging-receipt.json") if (project / ".hyperframes/staging-receipt.json").is_file() else {}
    compiled = load_json(project / ".hyperframes/compiled/storyboard.json") if (project / ".hyperframes/compiled/storyboard.json").is_file() else {}
    if manifest.get("schemaVersion") != MANIFEST_SCHEMA_VERSION:
        findings.append(finding("error", "manifest-schema", "Unsupported intake manifest schemaVersion"))
    if curation.get("schemaVersion") != CURATION_SCHEMA_VERSION:
        findings.append(finding("error", "curation-schema", "Unsupported curation schemaVersion"))
    elif curation:
        curation_schema = load_json(Path(__file__).resolve().parents[1] / "references" / "curation.schema.json")
        for error in Draft202012Validator(curation_schema).iter_errors(curation):
            findings.append(finding("error", "curation-schema", error.message))
    if receipt.get("schemaVersion") != "hyperframes-curated-staging-receipt/v3":
        findings.append(finding("error", "staging-schema", "Staging receipt must use hyperframes-curated-staging-receipt/v3"))
    storyboard = compiled.get("storyboard") if isinstance(compiled.get("storyboard"), dict) else {}
    if compiled.get("schemaVersion") != "hyperframes-storyboard-compiled/v3":
        findings.append(finding("error", "compiled-schema", "Compiled Storyboard must use hyperframes-storyboard-compiled/v3"))
    try:
        validate_storyboard(storyboard)
    except ValueError as error:
        findings.append(finding("error", "storyboard-schema", str(error)))
    storyboard_path = project / "STORYBOARD.md"
    if compiled.get("generated") is not True or compiled.get("source") != "STORYBOARD.md":
        findings.append(finding("error", "compiled-authority", "Compiled Storyboard must declare generated=true and source=STORYBOARD.md"))
    if storyboard_path.is_file() and compiled.get("sourceHash") != sha256(storyboard_path):
        findings.append(finding("error", "compiled-stale", "Compiled Storyboard sourceHash does not match STORYBOARD.md"))
    if storyboard and curation.get("storyboardHash") != object_sha256(storyboard):
        findings.append(finding("error", "curation-stale", "Curation does not match the compiled Storyboard"))
    review = curation.get("review") if isinstance(curation.get("review"), dict) else {}
    if storyboard:
        try:
            validate_production_review(storyboard, review)
        except ValueError as error:
            findings.append(finding("error", "storyboard-review", str(error)))
    if storyboard and receipt.get("storyboardHash") != object_sha256(storyboard):
        findings.append(finding("error", "staging-stale", "Staging receipt does not match the compiled Storyboard"))
    if storyboard and manifest.get("sceneIds") != [scene["id"] for scene in storyboard.get("scenes", [])]:
        findings.append(finding("error", "scene-set", "Manifest scene IDs differ from Storyboard order"))
    for relative, expected in manifest.get("hashes", {}).items():
        path = (project / relative).resolve()
        if path != project and project not in path.parents:
            findings.append(finding("error", "artifact-path", f"Manifest path leaves project: {relative}"))
        elif not path.is_file() or sha256(path) != expected:
            findings.append(finding("error", "artifact-hash", f"Missing or changed manifest artifact: {relative}"))
    for key in ("scenes", "transitions", "choreography", "reuse", "visual_thesis", "takeaway", "selector", "event_window"):
        if key in manifest:
            findings.append(finding("error", "manifest-creative-copy", f"Manifest must not copy creative field: {key}"))

    staged = {item.get("id"): item for item in receipt.get("items", []) if isinstance(item, dict)}
    try:
        resolutions = validate_recipe_resolutions(storyboard, curation, args.library.resolve()) if storyboard else {}
    except (OSError, ValueError) as error:
        findings.append(finding("error", "recipe-resolution", str(error)))
        resolutions = {}
    required_ids = set()
    for scene in storyboard.get("scenes", []):
        required_ids.update(resolutions.get((scene["id"], item["id"]), item["id"]) for item in scene.get("uses", []) if item.get("required") and not item["id"].startswith("authored:"))
        for item in scene.get("uses", []):
            if item["id"].startswith("recipe:") and (scene["id"], item["id"]) not in resolutions:
                findings.append(finding("error", "unresolved-recipe", f"Migration-only recipe binding is unresolved: {scene['id']}/{item['id']}"))
    for item_id in sorted(required_ids):
        item = staged.get(item_id)
        if not item:
            findings.append(finding("error", "required-not-staged", f"Required Storyboard binding is not staged: {item_id}"))
            continue
        expected_claims = [claim for claim in curation.get("recipeResolutions", []) if claim.get("resolvedId") == item_id]
        if item.get("recipeResolutions", []) != expected_claims:
            findings.append(finding("error", "recipe-receipt-provenance", f"Staging receipt lost or changed recipe provenance: {item_id}"))
        for file in item.get("files", []):
            relative = str(file.get("destinationPath", ""))
            path = (project / relative).resolve()
            if path != project and project not in path.parents or not path.is_file() or sha256(path) != file.get("destinationHash"):
                findings.append(finding("error", "staging-hash", f"Staged file is missing, outside project, or changed: {item_id} → {relative}"))
    authored = list((project / "compositions" / "frames").glob("*.html")) if (project / "compositions" / "frames").is_dir() else []
    if authored:
        findings.append(finding("error", "composition-present", "Intake must stop before authored frame compositions"))
    handoff_text = (project / "HANDOFF.md").read_text(encoding="utf-8") if (project / "HANDOFF.md").is_file() else ""
    required_handoff = ["Status: ready-for-build", "Schema: curated-intake/v3", "BRIEF.md", "frame.md", "STORYBOARD.md", ".hyperframes/intake-manifest.json", "Preflight: passed", "Run $hyperframes"]
    for token in required_handoff:
        if token not in handoff_text:
            findings.append(finding("error", "handoff-entry", f"HANDOFF is missing: {token}"))
    forbidden = ["Scene Timing", "Composition table", "scene-contract", "build-plan", "Copy-ready", "registry-block:", "registry-component:", "Choreography:"]
    for token in forbidden:
        if token.lower() in handoff_text.lower():
            findings.append(finding("error", "handoff-duplicate", f"HANDOFF duplicates forbidden detail: {token}"))
    for scene in storyboard.get("scenes", []):
        copied_tokens = [scene.get("title", ""), scene.get("content", ""), scene.get("visual", ""), *(item.get("id", "") for item in scene.get("uses", []))]
        for token in copied_tokens:
            if token and token in handoff_text:
                findings.append(finding("error", "handoff-creative-copy", f"HANDOFF copies Storyboard detail: {token}"))
    for miss in curation.get("catalogMisses", []):
        findings.append(finding("warning", "optional-use-miss", f"Optional Storyboard use remains unresolved: {miss.get('sceneId')}/{miss.get('need')}"))
    errors = sum(item["level"] == "error" for item in findings)
    warnings = sum(item["level"] == "warning" for item in findings)
    report = {"schemaVersion": "hyperframes-handoff-verification/v3", "ok": errors == 0, "expectedSceneIds": manifest.get("sceneIds", []), "errors": errors, "warnings": warnings, "findings": findings}
    output = args.output or project / ".hyperframes" / "handoff-verification.json"
    write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
