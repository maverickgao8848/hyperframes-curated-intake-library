#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _curation import BUILD_PLAN_SCHEMA_VERSION, CURATION_SCHEMA_VERSION, HANDOFF_SCHEMA_VERSION, load_json, sha256, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify curated-library policy after an official HyperFrames build.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def searchable_text(project: Path) -> str:
    parts: list[str] = []
    staged_roots = {
        project / "compositions" / "library",
        project / "compositions" / "components" / "library",
    }
    for pattern in ("*.html", "*.js", "*.mjs", "*.css"):
        for path in project.rglob(pattern):
            if (
                ".hyperframes" in path.parts
                or "scene-contracts" in path.parts
                or any(root == path or root in path.parents for root in staged_roots)
                or ".git" in path.parts
                or "node_modules" in path.parts
            ):
                continue
            try:
                parts.append(path.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                continue
    return "\n".join(parts)


def finding(level: str, code: str, message: str) -> dict:
    return {"level": level, "code": code, "message": message}


def storyboard_scenes(storyboard_text: str) -> list[dict]:
    matches = list(re.finditer(r"^## Frame\s+[^\n]+$", storyboard_text, flags=re.MULTILINE))
    scenes: list[dict] = []
    for index, match in enumerate(matches):
        block = storyboard_text[match.start(): matches[index + 1].start() if index + 1 < len(matches) else len(storyboard_text)]

        def field(name: str) -> str | None:
            value = re.search(rf"^-\s+{re.escape(name)}:\s*(.+)$", block, flags=re.MULTILINE | re.IGNORECASE)
            return value.group(1).strip() if value else None

        src = field("src")
        if not src:
            continue
        scenes.append({
            "id": field("id") or Path(src).stem,
            "src": src,
            "sourceRelation": field("source_relation"),
            "animation": field("animation"),
            "device": field("device"),
            "hero": field("hero") == "true",
            "beatIds": re.findall(r"^Scene\s+\d+\s+\([^)]*\):\s+\[([^;\]]+)", block, flags=re.MULTILINE),
            "textEffects": {
                cue_id: effect
                for cue_id, effect in re.findall(
                    r"^Text\s+\d+\s+\([^)]*\):\s+\[([^;\]]+);[^\]]*\]\s+effect=([^;\s]+)",
                    block,
                    flags=re.MULTILINE,
                )
            },
            "ambientActive": bool(field("ambient") and not str(field("ambient")).lower().startswith("none")),
            "textMode": field("text_mode"),
        })
    return scenes


def marker_is_present(marker: dict, text: str) -> bool:
    kind = str(marker.get("kind", ""))
    value = str(marker.get("value", ""))
    if not value:
        return False
    if kind == "id":
        return bool(re.search(rf"\bid\s*=\s*['\"]{re.escape(value)}['\"]", text))
    if kind == "class":
        in_markup = bool(re.search(rf"\bclass\s*=\s*['\"][^'\"]*\b{re.escape(value)}\b", text))
        in_script = bool(re.search(rf"\bclassName\s*=\s*['\"][^'\"]*\b{re.escape(value)}\b", text))
        return in_markup or in_script
    if kind == "css-var":
        return value in text
    return False


def item_is_referenced(item: dict, text: str) -> bool:
    kind = str(item.get("kind", ""))
    item_id = str(item.get("id", ""))
    entry_path = str(item.get("entryPath", ""))
    integration_mode = str(item.get("integration", {}).get("mode", ""))
    if kind == "registry-block" or integration_mode in {"subcomposition", "isolated"}:
        as_subcomposition = bool(entry_path) and bool(re.search(
            rf"\bdata-composition-src\s*=\s*['\"]{re.escape(entry_path)}['\"]", text
        ))
        as_transition_runtime = bool(item_id) and data_attr_present(text, "data-transition-block", item_id) and bool(
            re.search(r"\bHyperShader\.init\s*\(|@hyperframes/shader-transitions", text)
        )
        return as_subcomposition or as_transition_runtime
    if entry_path and entry_path in text:
        return True
    markers = [marker for marker in item.get("signatureMarkers", []) if isinstance(marker, dict)]
    structural = [marker for marker in markers if marker.get("kind") in {"id", "class"}]
    supporting = [marker for marker in markers if marker.get("kind") == "css-var"]
    return bool(structural) and any(marker_is_present(marker, text) for marker in structural) and (
        not supporting or any(marker_is_present(marker, text) for marker in supporting)
    )


def scene_source_text(project: Path, scene: dict) -> str:
    source = (project / str(scene.get("src", ""))).resolve()
    if source != project and project not in source.parents:
        return ""
    paths = [source]
    parts: list[str] = []
    for path in paths:
        if path.is_file():
            try:
                parts.append(path.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                pass
    return "\n".join(parts)


def selector_is_in_source(selector: str, source: str) -> bool:
    selector = str(selector).strip()
    if selector.startswith("#"):
        return bool(re.search(rf"\bid\s*=\s*['\"]{re.escape(selector[1:])}['\"]", source))
    if selector.startswith("."):
        return bool(re.search(rf"\bclass\s*=\s*['\"][^'\"]*\b{re.escape(selector[1:])}\b", source))
    return selector in source


def data_attr_present(source: str, name: str, value: str) -> bool:
    return bool(re.search(rf"\b{re.escape(name)}\s*=\s*['\"]{re.escape(value)}['\"]", source))


def motion_assertions(project: Path, scene: dict) -> list[dict]:
    sidecar = (project / str(scene.get("src", ""))).with_suffix(".motion.json")
    if not sidecar.is_file():
        return []
    try:
        value = json.loads(sidecar.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []
    assertions = value.get("assertions", []) if isinstance(value, dict) else []
    return [item for item in assertions if isinstance(item, dict)]


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    curation = load_json(project / ".hyperframes" / "curation.json")
    findings: list[dict] = []
    if curation.get("schemaVersion") != CURATION_SCHEMA_VERSION:
        findings.append(finding("error", "schema", "Unsupported curation schemaVersion."))
    handoff_path = project / ".hyperframes" / "intake-handoff.json"
    build_plan_path = project / ".hyperframes" / "build-plan.json"
    handoff = load_json(handoff_path) if handoff_path.is_file() else {}
    build_plan = load_json(build_plan_path) if build_plan_path.is_file() else {}
    if handoff.get("schemaVersion") != HANDOFF_SCHEMA_VERSION:
        findings.append(finding("error", "handoff-schema", "Build verification requires the current intake handoff manifest."))
    if build_plan.get("schemaVersion") != BUILD_PLAN_SCHEMA_VERSION:
        findings.append(finding("error", "build-plan-schema", "Build verification requires the current Build Plan."))
    frame = project / str(curation.get("frame", {}).get("projectPath", "frame.md"))
    if not frame.is_file():
        findings.append(finding("error", "frame-missing", "Project frame.md is missing."))
    elif sha256(frame) != curation.get("frame", {}).get("sourceSha256") and not curation.get("frame", {}).get("projectModified"):
        findings.append(finding("error", "frame-hash", "Project frame.md differs from the source without projectModified provenance."))
    storyboard = project / "STORYBOARD.md"
    storyboard_records: list[dict] = []
    if not storyboard.is_file():
        findings.append(finding("error", "storyboard-missing", "Project STORYBOARD.md is missing."))
    else:
        storyboard_text = storyboard.read_text(encoding="utf-8")
        storyboard_records = storyboard_scenes(storyboard_text)
        if not re.search(r"^#{2,3}\s+(?:Frame|Scene|Beat)\s+\d+", storyboard_text, flags=re.MULTILINE | re.IGNORECASE):
            findings.append(finding("error", "storyboard-empty", "Project STORYBOARD.md has no parseable frames."))
        if "source_relation:" not in storyboard_text or "**Visual intent:**" not in storyboard_text:
            findings.append(finding("error", "storyboard-direction-missing", "Storyboard frames must preserve source relationship and visual intent from the approved outline."))
        for scene in storyboard_records:
            if scene["id"] != Path(scene["src"]).stem:
                findings.append(finding(
                    "error", "storyboard-scene-identity-mismatch",
                    f"Storyboard scene id and src stem differ: {scene['id']} → {scene['src']}.",
                ))
    manifest_scene_ids = [
        str(scene.get("id")) for scene in handoff.get("scenes", [])
        if isinstance(scene, dict) and scene.get("id")
    ]
    storyboard_scene_ids = [str(scene["id"]) for scene in storyboard_records]
    if manifest_scene_ids != storyboard_scene_ids:
        findings.append(finding(
            "error", "manifest-storyboard-scene-set",
            "Storyboard scene order and IDs must match the complete handoff manifest scene set.",
        ))
    text = searchable_text(project)
    windows_absolute = re.findall(r"[A-Za-z]:\\[^\"'\s<]+", text)
    if windows_absolute:
        findings.append(finding("error", "absolute-runtime-path", "Built project contains Windows absolute runtime paths."))

    receipt_path = project / ".hyperframes" / "staging-receipt.json"
    receipt = load_json(receipt_path) if receipt_path.is_file() else {"items": []}
    receipt_by_id = {item.get("id"): item for item in receipt.get("items", []) if isinstance(item, dict)}

    manifest_path = project / ".media" / "manifest.jsonl"
    media_records = []
    if manifest_path.is_file():
        media_records = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    media_by_id = {record.get("id"): record for record in media_records}
    for entry_id in curation.get("requiredAssets", []):
        if entry_id.startswith(("registry-block:", "registry-component:")):
            if entry_id not in receipt_by_id:
                findings.append(finding("error", "required-registry-missing", f"Required Registry item was not staged: {entry_id}."))
            continue
        record = media_by_id.get(entry_id)
        if not record:
            findings.append(finding("error", "required-asset-unresolved", f"Required media has no inventory record: {entry_id}."))
            continue
        asset = project / str(record.get("path", ""))
        if not asset.is_file():
            findings.append(finding("error", "asset-missing", f"Required asset is missing: {entry_id}."))
        elif sha256(asset) != record.get("sha256"):
            findings.append(finding("error", "asset-hash", f"Required asset hash changed: {entry_id}."))
        elif record["path"] not in text:
            findings.append(finding("error", "asset-unused", f"Required asset is staged but not referenced: {entry_id}."))

    used_ids: list[str] = []
    for item in receipt.get("items", []):
        item_used = item_is_referenced(item, text)
        for file in item.get("files", []):
            staged = project / file["path"]
            if not staged.is_file() or sha256(staged) != file["sha256"]:
                findings.append(finding("error", "staging-hash", f"Staged file missing or changed: {file['path']}."))
        if item_used:
            used_ids.append(item["id"])
        else:
            findings.append(finding("warning", "staged-unused", f"Staged item has no observable project reference: {item['id']}."))

    usage_path = project / ".hyperframes" / "usage.json"
    staged_roots = {
        (project / "compositions" / "library").resolve(),
        (project / "compositions" / "components" / "library").resolve(),
    }
    authored_compositions = [
        path for path in (project / "compositions").rglob("*.html")
        if not any(root == path.resolve() or root in path.resolve().parents for root in staged_roots)
    ] if (project / "compositions").is_dir() else []
    build_started = bool(authored_compositions)
    if build_started and build_plan.get("state") != "build-selected":
        findings.append(finding("error", "build-plan-state", "Build started before the Build Plan reached build-selected state."))
    built_scenes = [scene for scene in storyboard_records if (project / scene["src"]).is_file()]
    if build_started:
        for scene in storyboard_records:
            composition_path = project / scene["src"]
            if not composition_path.is_file():
                findings.append(finding(
                    "error", "storyboard-src-missing",
                    f"Build started but the declared composition is missing: {scene['id']} → {scene['src']}.",
                ))
                continue
            composition_text = composition_path.read_text(encoding="utf-8")
            composition_ids = re.findall(r"\bdata-composition-id\s*=\s*['\"]([^'\"]+)['\"]", composition_text)
            if scene["id"] not in composition_ids:
                findings.append(finding(
                    "error", "composition-id-mismatch",
                    f"Composition root identity is missing or differs from the canonical scene id: {scene['id']}.",
                ))
    if build_started and not usage_path.is_file():
        findings.append(finding("error", "usage-missing", "Built scenes require .hyperframes/usage.json evidence."))
    usage = load_json(usage_path) if usage_path.is_file() else {"custom": [], "majorScenes": []}
    if (
        not isinstance(usage.get("custom", []), list)
        or not isinstance(usage.get("majorScenes", []), list)
        or not isinstance(usage.get("transitions", []), list)
    ):
        findings.append(finding("error", "usage-schema", "usage.json custom, transitions, and majorScenes must be arrays."))
        usage = {"custom": [], "transitions": [], "majorScenes": []}
    custom = usage.get("custom", [])
    misses = curation.get("catalogMisses", [])
    complete_miss_ids: set[str] = set()
    required_miss_strings = ("id", "need", "query", "tier", "rejectionReason")
    for miss in misses:
        complete = (
            isinstance(miss, dict)
            and all(isinstance(miss.get(field), str) and miss[field].strip() for field in required_miss_strings)
            and isinstance(miss.get("returnedCandidates"), list)
        )
        if complete:
            complete_miss_ids.add(miss["id"])
        else:
            miss_id = miss.get("id", "<unknown>") if isinstance(miss, dict) else "<invalid>"
            findings.append(finding("error", "catalog-miss-incomplete", f"Catalog miss lacks complete need/query/tier/candidates/rejection evidence: {miss_id}."))
    palette_ids = set().union(*(set(values) for values in curation.get("palette", {}).values()))
    if curation.get("policy") == "approved-only":
        if custom:
            findings.append(finding("error", "approved-only-custom", "approved-only project declares custom/out-of-scope dependencies."))
        outside = sorted(item_id for item_id in receipt_by_id if item_id not in palette_ids)
        if outside:
            findings.append(finding("error", "approved-only-outside-palette", "approved-only staged items are outside the project palette: " + ", ".join(outside)))
    if curation.get("policy") == "approved-first":
        uncovered = [item for item in custom if item.get("missId") not in complete_miss_ids]
        if uncovered:
            findings.append(finding("error", "catalog-miss-required", "approved-first custom dependencies require matching catalog-miss records."))
    expected_source_scenes = storyboard_records if build_started else built_scenes
    expected_major = {
        scene["id"]: scene
        for scene in expected_source_scenes
        if scene.get("animation") in {"authored", "augment"}
    }
    declared_major: dict[str, dict] = {}
    plan_by_id = {
        str(scene.get("sceneId")): scene
        for scene in build_plan.get("scenes", [])
        if isinstance(scene, dict) and scene.get("sceneId")
    }
    planned_transitions = [item for item in build_plan.get("transitions", []) if isinstance(item, dict)]
    expected_boundary_pairs = list(zip(manifest_scene_ids, manifest_scene_ids[1:]))
    if len(planned_transitions) != len(expected_boundary_pairs):
        findings.append(finding("error", "transition-plan-count", "Build Plan transition count must equal the adjacent scene-boundary count."))
    transition_usage = usage.get("transitions", [])
    transition_evidence_by_id = {
        str(item.get("boundaryId")): item
        for item in transition_usage
        if isinstance(item, dict) and item.get("boundaryId")
    }
    if len(transition_evidence_by_id) != len(transition_usage):
        findings.append(finding("error", "transition-evidence-duplicate", "Transition evidence contains invalid or duplicate boundary IDs."))
    verified_transitions = 0
    if build_started:
        planned_boundary_ids = [str(item.get("boundaryId", "")) for item in planned_transitions]
        if set(transition_evidence_by_id) != set(planned_boundary_ids):
            findings.append(finding("error", "transition-evidence-mismatch", "Transition evidence must match every Build Plan boundary."))
        for index, planned in enumerate(planned_transitions):
            boundary_id = str(planned.get("boundaryId", ""))
            evidence = transition_evidence_by_id.get(boundary_id, {})
            expected_from, expected_to = expected_boundary_pairs[index] if index < len(expected_boundary_pairs) else (None, None)
            catalog_id = str(planned.get("catalogId", ""))
            resolved = True
            if planned.get("fromScene") != expected_from or planned.get("toScene") != expected_to:
                findings.append(finding("error", "transition-boundary-order", f"Transition {boundary_id} does not connect its adjacent manifest scenes."))
                resolved = False
            expected_evidence = {
                "fromScene": planned.get("fromScene"),
                "toScene": planned.get("toScene"),
                "catalogId": planned.get("catalogId"),
                "implementation": planned.get("implementation"),
            }
            if any(evidence.get(key) != value for key, value in expected_evidence.items()):
                findings.append(finding("error", "transition-evidence-contract", f"Transition evidence differs from the Build Plan: {boundary_id}."))
                resolved = False
            controller = str(evidence.get("controllerSelector", ""))
            markers_present = (
                bool(controller)
                and selector_is_in_source(controller, text)
                and data_attr_present(text, "data-transition-id", boundary_id)
                and data_attr_present(text, "data-transition-from", str(planned.get("fromScene", "")))
                and data_attr_present(text, "data-transition-to", str(planned.get("toScene", "")))
            )
            if not markers_present:
                findings.append(finding("error", "transition-controller-missing", f"Transition {boundary_id} lacks its production controller and boundary markers."))
                resolved = False
            implementation = str(planned.get("implementation", ""))
            if implementation == "shader-runtime":
                runtime_present = bool(re.search(r"\bHyperShader\.init\s*\(|@hyperframes/shader-transitions", text))
            elif implementation == "css-gsap":
                runtime_present = bool(re.search(r"\bgsap\.timeline\s*\(", text))
            else:
                runtime_present = bool(re.search(r"\bdata-composition-src\s*=", text))
            if not runtime_present:
                findings.append(finding("error", "transition-runtime-missing", f"Transition {boundary_id} lacks executable {implementation} wiring."))
                resolved = False
            if planned.get("catalogKind") == "registry-block":
                receipt_item = receipt_by_id.get(catalog_id)
                if not receipt_item:
                    findings.append(finding("error", "transition-unstaged", f"Transition Block has no staging receipt: {boundary_id} → {catalog_id}."))
                    resolved = False
                elif not data_attr_present(text, "data-transition-block", catalog_id) or not item_is_referenced(receipt_item, text):
                    findings.append(finding("error", "transition-implementation-missing", f"Transition Block is staged but its runtime is not integrated: {boundary_id} → {catalog_id}."))
                    resolved = False
            if resolved:
                verified_transitions += 1
    covered_major = 0
    for scene in usage.get("majorScenes", []):
        if not isinstance(scene, dict):
            findings.append(finding("error", "usage-scene-schema", "majorScenes entries must be objects."))
            continue
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not scene_id.strip():
            findings.append(finding("error", "usage-scene-schema", "Every major scene requires a non-empty id."))
            continue
        if scene_id in declared_major:
            findings.append(finding("error", "usage-scene-duplicate", f"Duplicate major scene usage entry: {scene_id}."))
            continue
        declared_major[scene_id] = scene
        curated_ids = scene.get("curatedItems")
        if curated_ids is None and scene.get("curatedItem"):
            curated_ids = [scene["curatedItem"]]
        miss_ids = scene.get("missIds")
        if miss_ids is None and scene.get("missId"):
            miss_ids = [scene["missId"]]
        curated_ids = curated_ids or []
        miss_ids = miss_ids or []
        beat_evidence = scene.get("beatEvidence", [])
        text_effects = scene.get("textEffects", [])
        ambient_evidence = scene.get("ambientEvidence")
        integration_evidence = scene.get("integrationEvidence", [])
        if not isinstance(curated_ids, list) or not all(isinstance(value, str) and value for value in curated_ids):
            findings.append(finding("error", "usage-scene-schema", f"Major scene {scene_id} curatedItems must be an array of IDs."))
            curated_ids = []
        if not isinstance(miss_ids, list) or not all(isinstance(value, str) and value for value in miss_ids):
            findings.append(finding("error", "usage-scene-schema", f"Major scene {scene_id} missIds must be an array of IDs."))
            miss_ids = []
        if not curated_ids and not miss_ids:
            findings.append(finding("error", "scene-evidence-missing", f"Major scene lacks a curated item or catalog miss: {scene_id}."))
            continue
        scene_record = expected_major.get(scene_id)
        per_scene_text = scene_source_text(project, scene_record) if scene_record else ""
        assertions = motion_assertions(project, scene_record) if scene_record else []
        scene_resolved = bool(curated_ids or miss_ids)
        plan_integrations = plan_by_id.get(scene_id, {}).get("integrations", [])
        planned_ids = [item.get("id") for item in plan_integrations if isinstance(item, dict)]
        if not isinstance(integration_evidence, list):
            findings.append(finding("error", "integration-evidence-schema", f"Scene {scene_id} integrationEvidence must be an array."))
            integration_evidence = []
            scene_resolved = False
        evidence_by_id = {
            str(item.get("id")): item
            for item in integration_evidence
            if isinstance(item, dict) and item.get("id")
        }
        if len(evidence_by_id) != len(integration_evidence):
            findings.append(finding("error", "integration-evidence-duplicate", f"Scene {scene_id} integrationEvidence contains invalid or duplicate IDs."))
            scene_resolved = False
        if set(evidence_by_id) != set(planned_ids):
            findings.append(finding("error", "integration-evidence-mismatch", f"Scene {scene_id} integration evidence must match the final Build Plan selections."))
            scene_resolved = False
        for planned in plan_integrations:
            if not isinstance(planned, dict):
                continue
            item_id = str(planned.get("id", ""))
            evidence = evidence_by_id.get(item_id, {})
            selector = str(evidence.get("selector", ""))
            receipt_item = receipt_by_id.get(item_id)
            if item_id not in curated_ids:
                findings.append(finding("error", "planned-item-usage", f"Scene {scene_id} omits its Build Plan integration from curatedItems: {item_id}."))
                scene_resolved = False
            if not receipt_item:
                findings.append(finding("error", "planned-item-unstaged", f"Scene {scene_id} Build Plan integration has no staging receipt: {item_id}."))
                scene_resolved = False
                continue
            if not selector or not selector_is_in_source(selector, per_scene_text):
                findings.append(finding("error", "integration-target-missing", f"Scene {scene_id} integration evidence does not bind a production selector: {item_id}."))
                scene_resolved = False
            if not item_is_referenced(receipt_item, per_scene_text):
                findings.append(finding("error", "integration-implementation-missing", f"Scene {scene_id} lacks the staged implementation signatures for {item_id}."))
                scene_resolved = False
            expected_mode = str(receipt_item.get("integration", {}).get("mode", ""))
            accepted_modes = {"subcomposition"} if receipt_item.get("kind") == "registry-block" else {"host-dom", "inline"}
            if evidence.get("implementation") not in accepted_modes or (
                expected_mode in {"subcomposition", "host-dom", "inline"}
                and evidence.get("implementation") != expected_mode
            ):
                findings.append(finding("error", "integration-method", f"Scene {scene_id} records the wrong integration method for {item_id}."))
                scene_resolved = False
        for curated_id in curated_ids:
            if curated_id not in palette_ids:
                findings.append(finding("error", "scene-item-outside-palette", f"Major scene uses an item outside the project palette: {curated_id}."))
                scene_resolved = False
                continue
            if curated_id not in receipt_by_id:
                findings.append(finding("error", "scene-item-unstaged", f"Major scene declares an unstaged item: {curated_id}."))
                scene_resolved = False
                continue
            if curated_id not in used_ids:
                findings.append(finding("error", "scene-item-unused", f"Major scene declares an item with no observable project reference: {curated_id}."))
                scene_resolved = False
            elif per_scene_text and not item_is_referenced(receipt_by_id[curated_id], per_scene_text):
                findings.append(finding("error", "scene-item-unreferenced", f"Major scene source does not reference its declared item: {scene_id} → {curated_id}."))
                scene_resolved = False
        for miss_id in miss_ids:
            if miss_id not in complete_miss_ids:
                findings.append(finding("error", "scene-miss-invalid", f"Major scene references an absent or incomplete catalog miss: {scene_id} → {miss_id}."))
                scene_resolved = False
        if scene_record:
            expected_beat_ids = list(scene_record.get("beatIds", []))
            declared_beat_ids = [item.get("id") for item in beat_evidence if isinstance(item, dict)] if isinstance(beat_evidence, list) else []
            if declared_beat_ids != expected_beat_ids:
                findings.append(finding("error", "beat-evidence-mismatch", f"Major scene beat evidence does not match Storyboard order: {scene_id}."))
                scene_resolved = False
            for item in beat_evidence if isinstance(beat_evidence, list) else []:
                selector = str(item.get("selector", ""))
                beat_id = str(item.get("id", ""))
                if not selector or not selector_is_in_source(selector, per_scene_text) or not data_attr_present(per_scene_text, "data-beat-id", beat_id):
                    findings.append(finding("error", "beat-target-missing", f"Scene {scene_id} lacks visible binding for beat {beat_id}."))
                    scene_resolved = False
            expected_text = dict(scene_record.get("textEffects", {}))
            declared_text = {
                str(item.get("id")): str(item.get("effect"))
                for item in text_effects if isinstance(item, dict)
            } if isinstance(text_effects, list) else {}
            if declared_text != expected_text:
                findings.append(finding("error", "text-effect-evidence-mismatch", f"Scene {scene_id} text-effect evidence does not match Storyboard text cues."))
                scene_resolved = False
            appears_selectors = {str(item.get("selector")) for item in assertions if item.get("kind") == "appearsBy"}
            for item in text_effects if isinstance(text_effects, list) else []:
                selector = str(item.get("selector", ""))
                cue_id = str(item.get("id", ""))
                effect = str(item.get("effect", ""))
                attrs_present = data_attr_present(per_scene_text, "data-text-cue-id", cue_id) and data_attr_present(
                    per_scene_text, "data-text-effect", effect
                )
                if not selector or not selector_is_in_source(selector, per_scene_text) or not attrs_present:
                    findings.append(finding("error", "text-effect-target-missing", f"Scene {scene_id} lacks executable text binding for {cue_id} → {effect}."))
                    scene_resolved = False
                if selector not in appears_selectors:
                    findings.append(finding("error", "text-effect-motion-missing", f"Scene {scene_id} text cue {cue_id} lacks an appearsBy assertion."))
                    scene_resolved = False
            before_count = sum(item.get("kind") == "before" for item in assertions)
            if len(expected_beat_ids) > 1 and before_count == 0:
                findings.append(finding("error", "beat-order-assertion-missing", f"Scene {scene_id} needs at least one before assertion for beat order."))
                scene_resolved = False
            if scene_record.get("ambientActive"):
                if not isinstance(ambient_evidence, dict) or not ambient_evidence.get("selector"):
                    findings.append(finding("error", "ambient-evidence-missing", f"Scene {scene_id} has active ambient but no ambientEvidence."))
                    scene_resolved = False
                else:
                    selector = str(ambient_evidence["selector"])
                    keeps_moving = any(
                        item.get("kind") == "keepsMoving" and item.get("withinSelector") in {None, selector}
                        for item in assertions
                    )
                    if not selector_is_in_source(selector, per_scene_text) or not keeps_moving:
                        findings.append(finding("error", "ambient-motion-missing", f"Scene {scene_id} active ambient lacks a keepsMoving assertion on its bound target."))
                        scene_resolved = False
            elif ambient_evidence is not None:
                findings.append(finding("error", "ambient-evidence-unexpected", f"Scene {scene_id} declares ambientEvidence for an intentional stillness frame."))
                scene_resolved = False
        if scene_resolved and scene_id in expected_major:
            covered_major += 1
    missing_major = sorted(set(expected_major) - set(declared_major))
    if usage_path.is_file() and missing_major:
        findings.append(finding("error", "usage-scenes-missing", "usage.json omits major designed scenes: " + ", ".join(missing_major)))
    extra_major = sorted(set(declared_major) - set(expected_major))
    if extra_major:
        findings.append(finding("warning", "usage-scenes-extra", "usage.json lists scenes not classified as designed/replace: " + ", ".join(extra_major)))
    device_counts: dict[str, int] = {}
    for scene in storyboard_records:
        if scene.get("device"):
            device_counts[scene["device"]] = device_counts.get(scene["device"], 0) + 1
    errors = sum(item["level"] == "error" for item in findings)
    warnings = sum(item["level"] == "warning" for item in findings)
    report = {
        "schemaVersion": "hyperframes-curated-build-verification/v2",
        "ok": errors == 0,
        "policy": curation.get("policy"),
        "usedCuratedItems": sorted(used_ids),
        "libraryCoverage": {
            "coveredMajorScenes": covered_major,
            "totalMajorScenes": len(expected_major),
            "ratio": round(covered_major / len(expected_major), 3) if expected_major else 1.0,
        },
        "sceneCounts": {
            "expected": len(manifest_scene_ids),
            "built": len(built_scenes),
            "majorExpected": len(expected_major),
            "majorVerified": covered_major,
        },
        "transitionCoverage": {
            "expected": len(expected_boundary_pairs),
            "verified": verified_transitions,
            "ratio": round(verified_transitions / len(expected_boundary_pairs), 3) if expected_boundary_pairs else 1.0,
        },
        "deviceRepetition": dict(sorted(device_counts.items())),
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
    }
    output = args.output or project / ".hyperframes" / "curation-verification.json"
    write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
