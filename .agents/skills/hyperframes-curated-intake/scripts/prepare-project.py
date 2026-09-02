#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _routed import result_packet, validate_request

from _curation import (
    BUILD_PLAN_SCHEMA_VERSION,
    CURATION_SCHEMA_VERSION,
    HANDOFF_SCHEMA_VERSION,
    MEDIA_KINDS,
    build_scene_contract,
    catalog_index,
    copy_verified,
    entry_source_paths,
    load_json,
    load_storyboard_spec,
    object_sha256,
    render_storyboard,
    sha256,
    source_target_for_asset,
    timing_contract,
    validate_beat_contract,
    validate_device_diversity,
    write_json,
    yaml_scalar,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a HyperFrames project with a confirmed outline storyboard and no compositions.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--curation", type=Path, required=True)
    parser.add_argument("--storyboard-spec", type=Path, required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--workflow", default="general-video")
    parser.add_argument("--animation-skill", type=Path, help="Path to the installed hyperframes-animation skill.")
    parser.add_argument("--asset", action="append", default=[], help="Additional project-local asset path to list in BRIEF.md.")
    parser.add_argument("--replace-approved-outline", action="store_true", help="Replace all intake-owned files, including STORYBOARD.md; use only after the user approves the revised complete outline.")
    parser.add_argument("--request", type=Path, help="Visual Director curated-intake-request.json. Enables routed mode and preserves parent authority.")
    return parser.parse_args()


def assert_writeable(path: Path, replace_approved_outline: bool) -> None:
    if path.exists() and not replace_approved_outline:
        raise SystemExit(f"Refusing to replace existing file without --replace-approved-outline: {path}")


def resolve_animation_skill(explicit: Path | None) -> Path:
    candidates = [
        explicit,
        Path(__file__).resolve().parents[2] / "hyperframes-animation",
        Path.home() / ".agents" / "skills" / "hyperframes-animation",
        Path.home() / ".codex" / "skills" / "hyperframes-animation",
    ]
    for candidate in candidates:
        if candidate and (candidate / "blueprints").is_dir() and (candidate / "rules").is_dir():
            return candidate.resolve()
    raise SystemExit("Could not locate hyperframes-animation; pass --animation-skill explicitly.")


def validate_animation_references(storyboard: dict, animation_skill: Path) -> None:
    from _curation import frame_rule_ids

    for frame in storyboard["frames"]:
        blueprint = str(frame["blueprint"])
        if blueprint != "compose" and not (animation_skill / "blueprints" / f"{blueprint}.md").is_file():
            raise SystemExit(f"Unknown HyperFrames blueprint in {frame['id']}: {blueprint}")
        missing_rules = [
            rule_id for rule_id in frame_rule_ids(frame)
            if not (animation_skill / "rules" / f"{rule_id}.md").is_file()
        ]
        if missing_rules:
            raise SystemExit(f"Unknown HyperFrames rules in {frame['id']}: " + ", ".join(missing_rules))


def build_intake_handoff(project: Path, storyboard: dict, curation: dict, artifact_paths: list[Path]) -> dict:
    timing = timing_contract(storyboard)
    timing_by_id = {item["id"]: item for item in timing["frames"]}
    scenes: list[dict] = []
    incoming_by_scene = {item["to_scene"]: item for item in storyboard["transitions"]}
    for order, frame in enumerate(storyboard["frames"], start=1):
        frame_id = str(frame["id"])
        src = f"compositions/frames/{frame_id}.html"
        if Path(src).stem != frame_id:
            raise SystemExit(f"Scene identity/path mismatch: {frame_id} != {Path(src).stem}")
        scenes.append({
            "order": order,
            "id": frame_id,
            "src": src,
            "motionSidecar": str(Path(src).with_suffix(".motion.json")).replace("\\", "/"),
            "sceneContract": f"scene-contracts/{frame_id}.json",
            "sceneContractSha256": sha256(project / "scene-contracts" / f"{frame_id}.json"),
            "sourceRelation": frame["source_relation"],
            "animation": frame["animation"],
            "classification": {
                "teachingIntent": frame["teaching_intent"],
                "cognitiveAction": frame["cognitive_action"],
                "sceneRole": frame["scene_role"],
                "evidenceType": frame["evidence_type"],
                "density": frame["density"],
                "narrativeScale": frame["narrative_scale"],
                "visualPattern": frame["visual_pattern"],
            },
            "status": "outline-approved",
            "timeline": timing_by_id[frame_id],
            "incomingTransition": incoming_by_scene.get(frame_id),
            "beats": [
                {
                    "id": beat["id"],
                    "kind": beat["kind"],
                    "window": beat.get("window"),
                    "targetRole": beat["target_role"],
                }
                for beat in frame.get("beats", [])
            ],
            "registryCandidates": [
                {
                    "id": candidate["id"],
                    "role": candidate["role"],
                    "responsibility": candidate["responsibility"],
                    "state": "candidate",
                }
                for candidate in frame.get("device_candidates", [])
            ],
            "directedIntegrations": [
                {
                    "id": item["id"],
                    "selection": item["selection"],
                    "role": item["role"],
                    "responsibility": item["responsibility"],
                }
                for item in frame.get("integrations", [])
            ],
        })
    artifacts = {
        path.relative_to(project).as_posix(): sha256(path)
        for path in artifact_paths
        if path.is_file()
    }
    return {
        "schemaVersion": HANDOFF_SCHEMA_VERSION,
        "state": "ready-for-separate-hyperframes-run",
        "outlineApproval": "user-approved",
        "nextStage": "sketch",
        "timing": timing,
        "identityInvariant": "scene id == src stem == data-composition-id == motion sidecar stem == usage scene id",
        "stateModel": ["candidate", "selected-for-build", "staged", "integrated", "verified"],
        "artifacts": artifacts,
        "scenes": scenes,
        "transitions": storyboard["transitions"],
        "launch": {
            "skill": "$hyperframes",
            "projectRoot": ".",
            "skip": ["intent-interview", "plan-reapproval"],
            "startAt": "sketch",
        },
    }


def render_handoff(storyboard: dict, curation: dict, manifest: dict) -> str:
    timing = manifest["timing"]
    lines = [
        "# HyperFrames Build Handoff",
        "",
        "Status: **ready for a separate `$hyperframes` build**. The approved files below form one executable director contract.",
        "",
        "## What is approved",
        "",
        f"- Message: {storyboard['message']}",
        f"- Audience: {storyboard['audience']}",
        f"- Format: {storyboard['format']}",
        f"- Timing: `{timing['mode']}`; target {timing['targetDurationSeconds']:g}s; planned {timing['plannedDurationSeconds']:g}s; tolerance {timing['toleranceSeconds']:g}s",
        f"- Curation policy: `{curation['policy']}`",
        "- Outline approval: user-approved; the build starts at Sketch with the approved direction already loaded.",
        "",
        "## Canonical artifacts",
        "",
        "- `BRIEF.md` — HyperFrames no-repeat token and intent authority",
        "- `STORYBOARD.md` — official frame dispatch units and canonical composition paths",
        "- `frame.md` — complete visual-language authority",
        "- `.hyperframes/curation.json` — bounded candidate pool and provenance",
        "- `.hyperframes/intake-handoff.json` — machine-readable identity and timing bridge",
        "- `.hyperframes/build-plan.json` — exact selection gate for Registry integrations",
        "- `scene-contracts/<scene-id>.json` — construction, layers, assets, integrations, beats, and evidence targets",
        "",
        "## Scene and timing map",
        "",
        "| # | Scene id | Composition | Contract | Timeline | Transition in | Directed items |",
        "|---:|---|---|---|---:|---|---:|",
    ]
    for scene in manifest["scenes"]:
        window = scene["timeline"]
        directed_count = len(scene["directedIntegrations"])
        incoming = scene.get("incomingTransition")
        incoming_label = incoming["catalog_id"] if incoming else "opening"
        lines.append(
            f"| {scene['order']} | `{scene['id']}` | `{scene['src']}` | `{scene['sceneContract']}` | "
            f"{window['start']:g}–{window['end']:g}s | `{incoming_label}` | {directed_count} |"
        )
    misses = curation.get("catalogMisses", [])
    lines.extend([
        "",
        "## Unresolved before Build",
        "",
        "- None recorded during intake." if not misses else f"- {len(misses)} catalog miss(es) require downstream resolution; see `.hyperframes/curation.json`.",
        "",
        "## Build protocol",
        "",
        "1. Run the handoff preflight and use its complete scene list as the verification denominator.",
        "2. Read `frame.md` once, then read each complete scene contract before authoring its composition.",
        "3. Finalize `.hyperframes/build-plan.json`; every selected scene item and every scene boundary names its responsibility, visible target, and integration method.",
        "4. Promote items through `candidate → selected-for-build → staged → integrated → verified` using observable evidence at each state change.",
        "5. Install every selected transition Block and integrate its real shader/runtime at the declared adjacent-scene boundary; the transition itself carries the outgoing handoff.",
        "6. Wire scene Blocks through their staged `data-composition-src`. Merge Components through their staged HTML, CSS, JavaScript, and timeline hooks.",
        "7. Bind transition, beat, text, ambient, asset, and integration receipts to visible production elements that serve the approved sequence.",
        "8. Preserve `scene id = src stem = data-composition-id = motion-sidecar stem = usage scene id` across all artifacts.",
        "9. Complete HyperFrames check, curation verification, snapshots at both sides and the midpoint of every boundary, and Studio preview, then wait for render approval.",
        "",
        "## Copy-ready next request",
        "",
        "> Use `$hyperframes` in this existing project. Treat `HANDOFF.md` as the execution controller. Read, in order, `BRIEF.md`, `frame.md`, `STORYBOARD.md`, `.hyperframes/intake-handoff.json`, `.hyperframes/curation.json`, `.hyperframes/build-plan.json`, `.media/manifest.jsonl` when present, and every scene contract listed by the handoff manifest. Run the handoff preflight first. Start at Sketch from the approved outline. Preserve the complete `N−1` transition plan: stage every selected transition Block, integrate its actual shader/runtime across the declared adjacent scenes, keep the outgoing scene visible until the shared transition begins, and record boundary evidence in `.hyperframes/usage.json`. Stage and integrate the remaining Registry selections into visible production elements, then record their evidence in usage and motion sidecars. Use the manifest scene list and transition list as the verification denominators. Complete check, transition boundary snapshots, verification, and Studio preview, then request render approval.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    library = args.library.resolve()
    project.mkdir(parents=True, exist_ok=True)
    curation = load_json(args.curation.resolve())
    storyboard = load_storyboard_spec(args.storyboard_spec.resolve())
    routed_request = None
    if args.request:
        try:
            routed_request, _ = validate_request(args.request)
        except ValueError as error:
            raise SystemExit(str(error)) from error
    validate_beat_contract(storyboard, require_windows=True)
    validate_animation_references(storyboard, resolve_animation_skill(args.animation_skill))
    validate_device_diversity(storyboard)
    if curation.get("schemaVersion") != CURATION_SCHEMA_VERSION:
        raise SystemExit("Unsupported curation schemaVersion")
    frame_source = library / str(curation["frame"]["sourcePath"])
    if sha256(frame_source) != curation["frame"]["sourceSha256"]:
        raise SystemExit("Selected Frame no longer matches the curation hash")
    palette_ids = set().union(*(set(values) for values in curation.get("palette", {}).values()))
    expected_storyboard_sha = curation.get("selectionEvidence", {}).get("storyboardSha256")
    if object_sha256(storyboard) != expected_storyboard_sha:
        raise SystemExit("Storyboard spec differs from the approved outline used to select the project palette")
    scene_evidence = {
        str(need.get("id")): need
        for need in curation.get("selectionEvidence", {}).get("sceneNeeds", [])
        if isinstance(need, dict)
    }
    for frame in storyboard["frames"]:
        evidence = scene_evidence.get(str(frame["id"]), {})
        media_ids = [
            str(candidate["id"])
            for candidate in evidence.get("mediaCandidates", [])
            if isinstance(candidate, dict) and candidate.get("id")
        ]
        frame["candidate_items"] = list(dict.fromkeys(frame.get("candidate_items", []) + media_ids))
        merged_devices: list[dict] = []
        for candidate in frame.get("device_candidates", []) + list(evidence.get("deviceCandidates", [])):
            if not isinstance(candidate, dict) or not candidate.get("id"):
                continue
            if any(existing["id"] == candidate["id"] for existing in merged_devices):
                continue
            merged_devices.append({
                "id": str(candidate["id"]),
                "role": str(candidate.get("role", "support")),
                "responsibility": str(candidate.get("responsibility", candidate.get("rationale", "support the scene"))),
                "rationale": str(candidate["rationale"]),
            })
        frame["device_candidates"] = merged_devices[:3]
    unknown_candidates = sorted({
        item
        for frame in storyboard["frames"]
        for item in (
            frame.get("candidate_items", [])
            + [candidate["id"] for candidate in frame.get("device_candidates", [])]
            + [integration["id"] for integration in frame.get("integrations", [])]
        )
        if item not in palette_ids
    } | {
        str(item["catalog_id"])
        for item in storyboard["transitions"]
        if item["catalog_id"] not in palette_ids
    })
    if unknown_candidates:
        raise SystemExit("Storyboard candidate_items are outside the project palette: " + ", ".join(unknown_candidates))
    owned = [
        project / "BRIEF.md", project / "STORYBOARD.md", project / "frame.md", project / "HANDOFF.md",
        project / "hyperframes.json", project / ".hyperframes" / "curation.json",
        project / ".hyperframes" / "intake-handoff.json", project / ".hyperframes" / "build-plan.json",
    ]
    if routed_request:
        owned.extend([
            project / ".hyperframes" / "curated-intake-request.json",
            project / ".hyperframes" / "curated-intake-result.json",
        ])
    owned.extend(project / "scene-contracts" / f"{frame['id']}.json" for frame in storyboard["frames"])
    for path in owned:
        assert_writeable(path, args.replace_approved_outline)
    if args.replace_approved_outline:
        expected_contracts = {f"{frame['id']}.json" for frame in storyboard["frames"]}
        contract_root = project / "scene-contracts"
        if contract_root.is_dir():
            for existing in contract_root.glob("*.json"):
                if existing.name not in expected_contracts:
                    existing.unlink()
    copy_verified(frame_source, project / "frame.md", curation["frame"]["sourceSha256"])
    write_json(project / ".hyperframes" / "curation.json", curation)
    (project / "STORYBOARD.md").write_text(render_storyboard(storyboard), encoding="utf-8")
    timing = timing_contract(storyboard)
    timing_by_id = {item["id"]: item for item in timing["frames"]}
    incoming_by_scene = {item["to_scene"]: item for item in storyboard["transitions"]}
    for frame in storyboard["frames"]:
        write_json(
            project / "scene-contracts" / f"{frame['id']}.json",
            build_scene_contract(frame, timing_by_id[str(frame["id"])], incoming_by_scene.get(str(frame["id"]))),
        )
    build_plan = {
        "schemaVersion": BUILD_PLAN_SCHEMA_VERSION,
        "state": "intake-approved",
        "expectedSceneIds": [str(frame["id"]) for frame in storyboard["frames"]],
        "transitions": [
            {
                "boundaryId": item["boundary_id"],
                "fromScene": item["from_scene"],
                "toScene": item["to_scene"],
                "catalogId": item["catalog_id"],
                "catalogKind": item["catalog_kind"],
                "selection": item["selection"],
                "state": "selected-for-build",
                "role": item["role"],
                "implementation": item["implementation"],
                "durationSeconds": item["duration_seconds"],
                "purpose": item["purpose"],
                "continuity": item["continuity"],
                "sameBackground": item["same_background"],
                "perceptualAnchor": item["perceptual_anchor"],
                "colorDependency": item["color_dependency"],
            }
            for item in storyboard["transitions"]
        ],
        "scenes": [
            {
                "sceneId": str(frame["id"]),
                "compositionSrc": f"compositions/frames/{frame['id']}.html",
                "sceneContract": f"scene-contracts/{frame['id']}.json",
                "classification": {
                    "teachingIntent": frame["teaching_intent"],
                    "cognitiveAction": frame["cognitive_action"],
                    "sceneRole": frame["scene_role"],
                    "evidenceType": frame["evidence_type"],
                    "density": frame["density"],
                    "narrativeScale": frame["narrative_scale"],
                    "visualPattern": frame["visual_pattern"],
                },
                "selectionStatus": "directed" if frame.get("integrations") else "open",
                "integrations": [
                    {
                        **item,
                        "state": "selected-for-build",
                    }
                    for item in frame.get("integrations", [])
                ],
            }
            for frame in storyboard["frames"]
        ],
    }
    write_json(project / ".hyperframes" / "build-plan.json", build_plan)
    if routed_request:
        write_json(project / ".hyperframes" / "curated-intake-request.json", routed_request)
        write_json(project / ".hyperframes" / "curated-intake-result.json", result_packet(routed_request, storyboard))

    registry = curation.get("registry", {})
    config = {
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "paths": {
            "blocks": "compositions/library",
            "components": "compositions/components/library",
            "assets": "assets/library",
        },
    }
    if registry.get("mode") == "http":
        config["registry"] = registry.get("source")
    write_json(project / "hyperframes.json", config)

    catalog = load_json(library / "catalog.json")
    index = catalog_index(catalog)
    asset_lines: list[str] = []
    manifest_records: list[dict] = []
    for entry_id in curation.get("requiredAssets", []):
        entry = index.get(entry_id)
        if not entry or entry.get("kind") not in MEDIA_KINDS:
            continue
        sources = entry_source_paths(library, entry)
        if len(sources) != 1:
            raise SystemExit(f"Required media must resolve to exactly one source file: {entry_id}")
        source, _, expected = sources[0]
        relative_target = source_target_for_asset(entry, source)
        copied_hash = copy_verified(source, project / relative_target, expected or entry.get("sha256"))
        manifest_records.append({
            "id": entry_id,
            "kind": entry["kind"],
            "path": relative_target.as_posix(),
            "sha256": copied_hash,
            "source": f"library/{source.relative_to(library).as_posix()}",
            "required": True,
        })
        asset_lines.append(f"- `{relative_target.as_posix()}` — required `{entry_id}`; use the real asset, not a placeholder.")
    for value in args.asset:
        asset_path = Path(value)
        if asset_path.is_absolute() or ".." in asset_path.parts:
            raise SystemExit(f"Asset paths must be project-relative: {value}")
        if not (project / asset_path).is_file():
            raise SystemExit(f"Additional asset does not exist: {value}")
        asset_lines.append(f"- `{asset_path.as_posix()}` — supplied project asset.")
    manifest = project / ".media" / "manifest.jsonl"
    if manifest_records:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text("".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in manifest_records), encoding="utf-8")
    if not asset_lines:
        asset_lines.append("- No required media was registered during intake.")

    brief = f'''---
workflow: {yaml_scalar(args.workflow)}
flow: companion
storyboard: yes
intake_status: ready-for-separate-hyperframes-run
intake_handoff: HANDOFF.md
message: {yaml_scalar(str(storyboard["message"]))}
destination: {yaml_scalar(args.destination)}
aspect: {yaml_scalar(str(storyboard["format"]))}
language: {yaml_scalar(args.language)}
audience: {yaml_scalar(str(storyboard["audience"]))}
length: {yaml_scalar(str(storyboard["duration"]))}
style_preset: {yaml_scalar(str(curation["frame"]["preset"]))}
---

## Intent

{args.intent.strip()}

## Assets

{chr(10).join(asset_lines)}

## Director contract

- `frame.md` governs the full visual and motion system, including composition, camera organization, element scale, typography, color, material, and density.
- `STORYBOARD.md` carries the user-approved sequence, scene identity, source relationship, purpose, and timing.
- `scene-contracts/<scene-id>.json` carries each approved construction, layer, asset, integration, text, beat, and evidence target.
- `.hyperframes/build-plan.json` carries exact directed Registry selections. Every `required` integration is a scene completion gate.
- `.hyperframes/build-plan.json` also carries exactly one required transition for every adjacent scene boundary.
- `.hyperframes/intake-handoff.json` supplies the complete expected scene set and canonical paths for all downstream checks.
- The later `$hyperframes` run begins at Sketch from this approved plan checkpoint.
- Each scene keeps one identity across its Storyboard id, source stem, scene contract, composition id, motion sidecar, Build Plan, and usage receipt.
- Every time-coded beat becomes a visible phase distributed across its declared window.
- Each animated text cue uses its named effect on the visible target and resolves to a readable final state.
- Animated scenes maintain perceptible activity through progressive text, evidence motion, or content-bound ambient behavior.
- Every adjacent scene pair uses its approved transition contract. The outgoing and incoming scenes overlap inside the transition window, and the transition supplies the outgoing motion.
- Registry discovery follows directed integrations, scene candidates, the project palette, and the full curated Registry in that order.
- Blocks use their staged sub-composition entry; Components contribute their staged HTML, CSS, JavaScript, and timeline behavior.
- `.hyperframes/usage.json` records integrationEvidence, beatEvidence, textEffects, ambientEvidence, curated items, and complete catalog misses for the actual visible scene elements.
- Original logos, SVGs, Lottie, audio, images, and video remain project-local, hash-verified production assets.
- The Build completes HyperFrames checks, manifest-based verification, snapshots, and Studio Preview before requesting render approval.

## Creative baseline

- Dense, designed, highly visual scenes with editorial, cinematic, documentary, or advertising energy as supported by `frame.md`.
- Chinese-first text with concise English emphasis where useful; keywords, conclusions, and short sentences rather than full subtitles.
- Large editorial typography, typewriter and paragraph typing, scramble/decode treatments, spotlight/ink/redaction reveals, progress underlines, word staggers, line reveals, and number counts selected by content shape.
- Real Registry Blocks and Components receive first consideration. Logos, SVGs, and Lottie share first-tier media priority.
- Typewriter-key and camera-shutter SFX accompany matching semantic events. Music remains project-specific.
- Preferred shader-transition Blocks are Cross Warp Morph, Domain Warp Dissolve, Glitch, Gravitational Lens, Ridged Burn, Ripple Waves, and Swirl Vortex; the selected Frame and narrative boundary determine the actual primary/accent assignment.
'''
    (project / "BRIEF.md").write_text(brief, encoding="utf-8")
    artifact_paths = [
        project / "BRIEF.md", project / "STORYBOARD.md", project / "frame.md",
        project / "hyperframes.json", project / ".hyperframes" / "curation.json",
        project / ".hyperframes" / "build-plan.json",
        *[project / "scene-contracts" / f"{frame['id']}.json" for frame in storyboard["frames"]],
    ]
    if manifest.is_file():
        artifact_paths.append(manifest)
    handoff_manifest = build_intake_handoff(project, storyboard, curation, artifact_paths)
    write_json(project / ".hyperframes" / "intake-handoff.json", handoff_manifest)
    (project / "HANDOFF.md").write_text(render_handoff(storyboard, curation, handoff_manifest), encoding="utf-8")
    print(
        f"Prepared {project} with {len(storyboard['frames'])} approved outline frames and HANDOFF.md; "
        "stopped before HyperFrames build."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
