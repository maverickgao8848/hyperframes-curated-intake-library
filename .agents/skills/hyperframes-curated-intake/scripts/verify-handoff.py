#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _routed import RESULT_SCHEMA, canonical_hash, load as load_routed_json, validate_request, validate_schema

from _curation import (
    BUILD_PLAN_SCHEMA_VERSION,
    CURATION_SCHEMA_VERSION,
    HANDOFF_SCHEMA_VERSION,
    SCENE_CONTRACT_SCHEMA_VERSION,
    load_json,
    sha256,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a HyperFrames curated intake packet before Build.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def finding(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    findings: list[dict[str, str]] = []
    required_files = [
        "BRIEF.md",
        "STORYBOARD.md",
        "frame.md",
        "HANDOFF.md",
        "hyperframes.json",
        ".hyperframes/curation.json",
        ".hyperframes/build-plan.json",
        ".hyperframes/intake-handoff.json",
    ]
    for relative in required_files:
        if not (project / relative).is_file():
            findings.append(finding("error", "artifact-missing", f"Required handoff artifact is missing: {relative}."))

    handoff_path = project / ".hyperframes" / "intake-handoff.json"
    curation_path = project / ".hyperframes" / "curation.json"
    build_plan_path = project / ".hyperframes" / "build-plan.json"
    handoff = load_json(handoff_path) if handoff_path.is_file() else {}
    curation = load_json(curation_path) if curation_path.is_file() else {}
    build_plan = load_json(build_plan_path) if build_plan_path.is_file() else {}

    routed_request_path = project / ".hyperframes" / "curated-intake-request.json"
    routed_result_path = project / ".hyperframes" / "curated-intake-result.json"
    if routed_request_path.is_file() or routed_result_path.is_file():
        if not routed_request_path.is_file() or not routed_result_path.is_file():
            findings.append(finding("error", "routed-artifact-pair", "Routed mode requires both request and result packets."))
        else:
            try:
                request, parent = validate_request(routed_request_path)
                result = load_routed_json(routed_result_path)
                result_schema = Path(__file__).resolve().parents[1] / "references" / "curated-intake-result.schema.json"
                result_errors = validate_schema(result, result_schema)
                if result_errors:
                    findings.append(finding("error", "routed-result-schema", "; ".join(result_errors)))
                if result.get("schemaVersion") != RESULT_SCHEMA or result.get("parentPlanHash") != canonical_hash(parent):
                    findings.append(finding("error", "routed-parent-hash", "Curated result does not bind to the current parent plan."))
                if result.get("segmentIds") != request.get("segmentIds"):
                    findings.append(finding("error", "routed-scope", "Curated result segment scope differs from its request."))
                result_ids = [item.get("segmentId") for item in result.get("segmentUpdates", []) if isinstance(item, dict)]
                if sorted(result_ids) != sorted(request.get("segmentIds", [])):
                    findings.append(finding("error", "routed-result-scope", "Curated result must return exactly one update record per requested segment."))
            except (OSError, ValueError) as error:
                findings.append(finding("error", "routed-request", str(error)))

    if handoff.get("schemaVersion") != HANDOFF_SCHEMA_VERSION:
        findings.append(finding("error", "handoff-schema", "The handoff manifest uses an unsupported schemaVersion."))
    if curation.get("schemaVersion") != CURATION_SCHEMA_VERSION:
        findings.append(finding("error", "curation-schema", "The curation file uses an unsupported schemaVersion."))
    if build_plan.get("schemaVersion") != BUILD_PLAN_SCHEMA_VERSION:
        findings.append(finding("error", "build-plan-schema", "The Build Plan uses an unsupported schemaVersion."))

    for relative, expected in handoff.get("artifacts", {}).items():
        path = (project / str(relative)).resolve()
        if path != project and project not in path.parents:
            findings.append(finding("error", "artifact-path", f"Artifact path leaves the project: {relative}."))
        elif not path.is_file():
            findings.append(finding("error", "artifact-missing", f"Manifest artifact is missing: {relative}."))
        elif sha256(path) != expected:
            findings.append(finding("error", "artifact-hash", f"Manifest artifact hash changed: {relative}."))

    scene_records = handoff.get("scenes", []) if isinstance(handoff.get("scenes"), list) else []
    scene_ids = [str(scene.get("id", "")) for scene in scene_records if isinstance(scene, dict)]
    if not scene_ids or any(not scene_id for scene_id in scene_ids) or len(scene_ids) != len(set(scene_ids)):
        findings.append(finding("error", "scene-set", "The handoff scene set must contain unique non-empty IDs."))

    plan_scene_records = build_plan.get("scenes", []) if isinstance(build_plan.get("scenes"), list) else []
    plan_by_id = {
        str(scene.get("sceneId")): scene
        for scene in plan_scene_records
        if isinstance(scene, dict) and scene.get("sceneId")
    }
    expected_plan_ids = build_plan.get("expectedSceneIds", [])
    if expected_plan_ids != scene_ids or list(plan_by_id) != scene_ids:
        findings.append(finding("error", "build-plan-scene-set", "Build Plan scene order and IDs must match the handoff manifest."))

    palette_ids = set().union(*(
        set(values) for values in curation.get("palette", {}).values() if isinstance(values, list)
    ))
    manifest_transitions = handoff.get("transitions", []) if isinstance(handoff.get("transitions"), list) else []
    plan_transitions = build_plan.get("transitions", []) if isinstance(build_plan.get("transitions"), list) else []
    expected_boundaries = list(zip(scene_ids, scene_ids[1:]))
    if len(manifest_transitions) != len(expected_boundaries):
        findings.append(finding("error", "transition-count", "The handoff must contain exactly one transition for every adjacent scene pair."))
    if len(plan_transitions) != len(expected_boundaries):
        findings.append(finding("error", "transition-plan-count", "The Build Plan must contain exactly one transition gate for every adjacent scene pair."))
    transition_by_target: dict[str, dict] = {}
    for index, (expected_from, expected_to) in enumerate(expected_boundaries):
        manifest_transition = manifest_transitions[index] if index < len(manifest_transitions) and isinstance(manifest_transitions[index], dict) else {}
        plan_transition = plan_transitions[index] if index < len(plan_transitions) and isinstance(plan_transitions[index], dict) else {}
        boundary_id = str(manifest_transition.get("boundary_id", ""))
        expected_plan = {
            "boundaryId": boundary_id,
            "fromScene": expected_from,
            "toScene": expected_to,
            "catalogId": manifest_transition.get("catalog_id"),
            "catalogKind": manifest_transition.get("catalog_kind"),
            "selection": manifest_transition.get("selection"),
            "role": manifest_transition.get("role"),
            "implementation": manifest_transition.get("implementation"),
            "durationSeconds": manifest_transition.get("duration_seconds"),
            "purpose": manifest_transition.get("purpose"),
            "continuity": manifest_transition.get("continuity"),
        }
        observed_plan = {key: plan_transition.get(key) for key in expected_plan}
        if (
            manifest_transition.get("from_scene") != expected_from
            or manifest_transition.get("to_scene") != expected_to
            or observed_plan != expected_plan
        ):
            findings.append(finding("error", "transition-boundary", f"Transition contract differs across the adjacent boundary {expected_from} → {expected_to}."))
        catalog_id = str(manifest_transition.get("catalog_id", ""))
        if catalog_id not in palette_ids:
            findings.append(finding("error", "transition-palette", f"Transition is outside the approved palette: {boundary_id} → {catalog_id}."))
        if manifest_transition.get("selection") != "required" or plan_transition.get("state") != "selected-for-build":
            findings.append(finding("error", "transition-gate", f"Transition lacks its required Build Plan gate: {boundary_id}."))
        if expected_to:
            transition_by_target[expected_to] = manifest_transition
    for scene in scene_records:
        if not isinstance(scene, dict):
            continue
        scene_id = str(scene.get("id", ""))
        src = str(scene.get("src", ""))
        motion = str(scene.get("motionSidecar", ""))
        contract_relative = str(scene.get("sceneContract", ""))
        if Path(src).stem != scene_id or Path(motion).name != f"{scene_id}.motion.json" or Path(contract_relative).stem != scene_id:
            findings.append(finding("error", "scene-identity", f"Scene identity paths diverge for {scene_id}."))
        contract_path = project / contract_relative
        if not contract_path.is_file():
            findings.append(finding("error", "scene-contract-missing", f"Scene contract is missing: {contract_relative}."))
            continue
        if sha256(contract_path) != scene.get("sceneContractSha256"):
            findings.append(finding("error", "scene-contract-hash", f"Scene contract hash changed: {contract_relative}."))
        contract = load_json(contract_path)
        if contract.get("schemaVersion") != SCENE_CONTRACT_SCHEMA_VERSION:
            findings.append(finding("error", "scene-contract-schema", f"Scene contract schema is unsupported: {scene_id}."))
        if contract.get("sceneId") != scene_id or contract.get("compositionSrc") != src or contract.get("motionSidecar") != motion:
            findings.append(finding("error", "scene-contract-identity", f"Scene contract identity differs from the manifest: {scene_id}."))
        expected_incoming = transition_by_target.get(scene_id)
        if contract.get("incomingTransition") != expected_incoming or scene.get("incomingTransition") != expected_incoming:
            findings.append(finding("error", "transition-scene-contract", f"Incoming transition differs across manifest and scene contract: {scene_id}."))
        plan_scene = plan_by_id.get(scene_id, {})
        if plan_scene.get("compositionSrc") != src or plan_scene.get("sceneContract") != contract_relative:
            findings.append(finding("error", "build-plan-identity", f"Build Plan paths differ from the manifest: {scene_id}."))
        contract_integrations = contract.get("integrations", [])
        plan_integrations = plan_scene.get("integrations", []) if isinstance(plan_scene, dict) else []
        contract_ids = [item.get("id") for item in contract_integrations if isinstance(item, dict)]
        plan_ids = [item.get("id") for item in plan_integrations if isinstance(item, dict)]
        if contract_ids != plan_ids:
            findings.append(finding("error", "integration-plan", f"Directed integrations differ between scene contract and Build Plan: {scene_id}."))
        for item in contract_integrations:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", ""))
            if item_id not in palette_ids:
                findings.append(finding("error", "integration-palette", f"Directed integration is outside the project palette: {scene_id} → {item_id}."))
            matching = [plan for plan in plan_integrations if isinstance(plan, dict) and plan.get("id") == item_id]
            if item.get("selection") == "required" and (not matching or matching[0].get("state") != "selected-for-build"):
                findings.append(finding("error", "required-integration-gate", f"Required integration lacks its Build Plan gate: {scene_id} → {item_id}."))

    frame_path = project / str(curation.get("frame", {}).get("projectPath", "frame.md"))
    if frame_path.is_file() and sha256(frame_path) != curation.get("frame", {}).get("sourceSha256") and not curation.get("frame", {}).get("projectModified"):
        findings.append(finding("error", "frame-hash", "Project frame.md differs from its approved source hash."))

    media_manifest = project / ".media" / "manifest.jsonl"
    if media_manifest.is_file():
        for line_number, line in enumerate(media_manifest.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                findings.append(finding("error", "media-manifest", f"Invalid media manifest JSON at line {line_number}."))
                continue
            path = project / str(record.get("path", ""))
            if not path.is_file() or sha256(path) != record.get("sha256"):
                findings.append(finding("error", "media-provenance", f"Media file or hash is invalid: {record.get('id', line_number)}."))

    authored_html = list((project / "compositions").rglob("*.html")) if (project / "compositions").is_dir() else []
    if authored_html:
        findings.append(finding("error", "composition-present", "The intake project already contains composition HTML."))

    handoff_text = (project / "HANDOFF.md").read_text(encoding="utf-8") if (project / "HANDOFF.md").is_file() else ""
    for token in ("## Copy-ready next request", ".hyperframes/build-plan.json", "scene-contracts/", "N−1"):
        if token not in handoff_text:
            findings.append(finding("error", "handoff-controller", f"HANDOFF.md is missing controller content: {token}."))

    errors = sum(item["level"] == "error" for item in findings)
    warnings = sum(item["level"] == "warning" for item in findings)
    report = {
        "schemaVersion": "hyperframes-handoff-verification/v1",
        "ok": errors == 0,
        "expectedSceneIds": scene_ids,
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
    }
    output = args.output or project / ".hyperframes" / "handoff-verification.json"
    write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
