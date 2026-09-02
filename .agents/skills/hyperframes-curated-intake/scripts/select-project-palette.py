#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from math import gcd

from _curation import (
    CURATION_SCHEMA_VERSION,
    MEDIA_KINDS,
    POLICIES,
    REGISTRY_KINDS,
    entry_text,
    load_json,
    load_storyboard_spec,
    object_sha256,
    sha256,
    storyboard_scene_text,
    tokenize,
    unique,
    write_json,
)


MEDIA_STOPWORDS = {"asset", "assets", "icon", "identity", "logo", "logos", "mark", "media", "real", "required", "use"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select a project palette from a user-approved outline storyboard.")
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--storyboard-spec", type=Path, required=True, help="Approved outline spec following storyboard-spec.schema.json.")
    parser.add_argument("--frame-preset", required=True)
    parser.add_argument("--policy", choices=POLICIES, default="approved-first")
    parser.add_argument("--registry-source", default="local-staging")
    parser.add_argument("--must-use", action="append", default=[])
    parser.add_argument("--favorite", action="append", default=[])
    parser.add_argument("--avoid", action="append", default=[])
    parser.add_argument("--forbidden", action="append", default=[])
    parser.add_argument("--max-blocks", type=int, default=12)
    parser.add_argument("--max-components", type=int, default=15)
    parser.add_argument("--max-media", type=int, default=10)
    parser.add_argument("--max-transitions", type=int, default=3)
    parser.add_argument("--max-total", type=int, default=40)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def score(entry: dict, query: set[str], favorites: set[str], must_use: set[str]) -> tuple[int, str]:
    entry_id = str(entry["id"])
    words = tokenize(entry_text(entry))
    overlap = len(query & words)
    exact_tag_hits = len(query & set(str(tag).lower() for tag in entry.get("tags", [])))
    value = overlap * 10 + exact_tag_hits * 3
    if entry_id in favorites:
        value += 100
    if entry_id in must_use:
        value += 1000
    if entry.get("preview"):
        value += 1
    return value, entry_id


def split_seconds(value: str) -> float:
    return float(str(value).strip().removesuffix("s"))


def aspect_ratio(value: str) -> str:
    match = __import__("re").fullmatch(r"(\d+)x(\d+)", str(value).strip().lower())
    if not match:
        return str(value)
    width, height = int(match.group(1)), int(match.group(2))
    divisor = gcd(width, height)
    return f"{width // divisor}:{height // divisor}"


def routing_compatible(entry: dict, frame: dict, format_value: str) -> tuple[bool, list[str]]:
    routing = entry.get("routing")
    if not isinstance(routing, dict):
        return True, ["catalog-metadata-basic"]
    reasons: list[str] = []
    available = set(frame.get("available_inputs", [])) | {"durationFrames", "title"}
    missing = sorted(set(routing.get("requiredInputs", [])) - available)
    if missing:
        reasons.append("missing-inputs=" + "+".join(missing))
    aspect = aspect_ratio(format_value)
    aspect_fit = set(routing.get("aspectFit", []))
    if aspect_fit and "all" not in aspect_fit and aspect not in aspect_fit:
        reasons.append(f"aspect!={aspect}")
    duration = split_seconds(frame["duration"])
    if routing.get("durationMin") is not None and duration < float(routing["durationMin"]):
        reasons.append("duration-below-min")
    if routing.get("durationMax") is not None and duration > float(routing["durationMax"]):
        reasons.append("duration-above-max")
    density_fit = set(routing.get("densityFit", []))
    if density_fit and frame.get("density") not in density_fit:
        reasons.append(f"density!={frame.get('density')}")
    if int(routing.get("containerCost", 0)) > int(frame.get("component_budget", 0)):
        reasons.append("container-budget")
    hero_ids = {candidate["id"] for candidate in frame.get("device_candidates", []) if candidate.get("role") == "hero"}
    if entry.get("id") in hero_ids and not routing.get("heroEligible", False):
        reasons.append("not-hero-eligible")
    if routing.get("family") == "ui-mock" and frame.get("evidence_type") in {"image", "video", "interface"} and available & {"image", "video"}:
        reasons.append("real-evidence-excludes-ui-mock")
    return not reasons, reasons


def pick(entries: list[dict], kinds: set[str], limit: int, query: set[str], favorites: set[str], must_use: set[str]) -> list[str]:
    candidates = [entry for entry in entries if entry.get("status") == "ready" and entry.get("kind") in kinds]
    ranked = sorted(candidates, key=lambda entry: (-score(entry, query, favorites, must_use)[0], score(entry, query, favorites, must_use)[1]))
    relevant = [entry for entry in ranked if score(entry, query, favorites, must_use)[0] > 0 or entry["id"] in must_use]
    return unique([entry["id"] for entry in relevant[:limit]] + [entry["id"] for entry in candidates if entry["id"] in must_use])


def main() -> int:
    args = parse_args()
    library = args.library.resolve()
    storyboard = load_storyboard_spec(args.storyboard_spec.resolve())
    catalog = load_json(library / "catalog.json")
    frame_path = library / "frames" / args.frame_preset / "FRAME.md"
    if not frame_path.is_file():
        raise SystemExit(f"Unknown frame preset: {args.frame_preset}")
    entries = [entry for entry in catalog.get("entries", []) if isinstance(entry, dict)]
    ids = {str(entry.get("id")) for entry in entries}
    default_scene_media: dict[str, list[str]] = {}
    for frame in storyboard["frames"]:
        defaults: list[str] = []
        text_effects = {
            str(cue.get("effect"))
            for cue in frame.get("text_plan", {}).get("cues", [])
            if isinstance(cue, dict)
        }
        if text_effects & {"typewriter", "typewriter-paragraph"} and "sfx:typewriter-key" in ids:
            defaults.append("sfx:typewriter-key")
        camera_language = storyboard_scene_text(frame).lower()
        if any(token in camera_language for token in ("camera shutter", "snapshot", "photograph", "photo capture")) and "sfx:camera-shutter" in ids:
            defaults.append("sfx:camera-shutter")
        default_scene_media[str(frame["id"])] = defaults
    default_sfx = {item_id for values in default_scene_media.values() for item_id in values}
    must_use = set(args.must_use)
    storyboard_candidates = {
        item
        for frame in storyboard["frames"]
        for item in frame.get("candidate_items", [])
    }
    storyboard_device_candidates = {
        str(candidate["id"])
        for frame in storyboard["frames"]
        for candidate in frame.get("device_candidates", [])
    }
    directed_integrations = {
        str(item["id"])
        for frame in storyboard["frames"]
        for item in frame.get("integrations", [])
    }
    directed_transitions = {str(item["catalog_id"]) for item in storyboard["transitions"]}
    selection_required = (
        must_use | storyboard_candidates | storyboard_device_candidates | directed_integrations
        | directed_transitions | default_sfx
    )
    unknown = sorted((selection_required | storyboard_device_candidates | set(args.favorite) | set(args.avoid)) - ids)
    if unknown:
        raise SystemExit("Unknown catalog IDs: " + ", ".join(unknown))
    avoided = set(args.avoid)
    registry_manifest_path = library / "registry" / "registry.json"
    installable_registry: set[tuple[str, str]] | None = None
    if registry_manifest_path.is_file():
        registry_manifest = load_json(registry_manifest_path)
        installable_registry = {
            (str(item.get("name")), str(item.get("type")))
            for item in registry_manifest.get("items", [])
            if isinstance(item, dict)
        }

    def installable(entry: dict) -> bool:
        if entry.get("kind") not in REGISTRY_KINDS or installable_registry is None:
            return True
        expected_type = "hyperframes:block" if entry.get("kind") == "registry-block" else "hyperframes:component"
        name = entry.get("source", {}).get("name") or str(entry.get("id", "")).split(":", 1)[-1]
        return (str(name), expected_type) in installable_registry

    unavailable_registry = [entry for entry in entries if entry.get("status") == "ready" and entry.get("kind") in REGISTRY_KINDS and not installable(entry)]
    unavailable_required = sorted(selection_required & {str(entry.get("id")) for entry in unavailable_registry})
    if unavailable_required:
        raise SystemExit("Must-use Registry entries are not installable in the current Registry view: " + ", ".join(unavailable_required))
    eligible = [entry for entry in entries if entry.get("id") not in avoided and installable(entry)]
    scene_needs = [
        {
            "id": str(frame["id"]),
            "title": str(frame["title"]),
            "query": storyboard_scene_text(frame),
        }
        for frame in storyboard["frames"]
    ]
    combined_summary = " ".join(need["query"] for need in scene_needs)
    query = tokenize(combined_summary + " " + args.frame_preset.replace("-", " "))
    favorites = set(args.favorite)
    blocks = pick(eligible, {"registry-block"}, args.max_blocks, query, favorites, selection_required)
    components = pick(eligible, {"registry-component"}, args.max_components, query, favorites, selection_required)
    transitions = pick(eligible, {"transition", "motion-rule", "scene-blueprint"}, args.max_transitions, query, favorites, selection_required)
    media = pick(eligible, MEDIA_KINDS, args.max_media, query, favorites, selection_required)
    selected_by_kind = {
        "blocks": blocks,
        "components": components,
        "transitions": transitions,
        "media": media,
    }
    selected_ids = unique(blocks + components + transitions + media)
    if len(selection_required) > args.max_total:
        raise SystemExit(
            f"Approved scene bindings and required assets need {len(selection_required)} palette items, "
            f"exceeding --max-total {args.max_total}; reuse candidates or explicitly raise the limit"
        )
    if len(selected_ids) > args.max_total:
        optional_slots = args.max_total - len(selection_required)
        optional_entries = [entry for entry in eligible if entry.get("id") in set(selected_ids) - selection_required]
        ranked_optional = sorted(
            optional_entries,
            key=lambda entry: (-score(entry, query, favorites, set())[0], score(entry, query, favorites, set())[1]),
        )
        kept = selection_required | {str(entry["id"]) for entry in ranked_optional[:optional_slots]}
        for role, values in selected_by_kind.items():
            selected_by_kind[role] = [item_id for item_id in values if item_id in kept]
        blocks = selected_by_kind["blocks"]
        components = selected_by_kind["components"]
        transitions = selected_by_kind["transitions"]
        media = selected_by_kind["media"]
    included = set(blocks + components + transitions + media)
    missing_required = sorted(selection_required - included)
    if missing_required:
        raise SystemExit("Must-use entries could not be selected: " + ", ".join(missing_required))
    selected_entries = [entry for entry in eligible if entry.get("id") in included]
    selected_by_id = {str(entry["id"]): entry for entry in selected_entries}
    for need, frame in zip(scene_needs, storyboard["frames"]):
        scene_query = tokenize(storyboard_scene_text(frame) + " " + args.frame_preset.replace("-", " "))
        media_query = scene_query - MEDIA_STOPWORDS
        explicit_items = list(frame.get("candidate_items", []))
        explicit_media = [
            item_id for item_id in explicit_items
            if selected_by_id[item_id].get("kind") in MEDIA_KINDS
        ]
        explicit_media = unique(explicit_media + default_scene_media.get(str(frame["id"]), []))
        explicit_devices: list[dict] = []
        incompatible: list[str] = []
        directed_candidates = [
            {
                "id": item["id"],
                "role": item["role"],
                "responsibility": item["responsibility"],
                "rationale": f"Directed {item['selection']} integration for {item['target']} in {item['slot']}.",
            }
            for item in frame.get("integrations", [])
        ]
        for candidate in directed_candidates + frame.get("device_candidates", []):
            if any(existing["id"] == candidate["id"] for existing in explicit_devices):
                continue
            entry = selected_by_id.get(str(candidate["id"]))
            if not entry:
                continue
            compatible, filter_reasons = routing_compatible(entry, frame, str(storyboard["format"]))
            if not compatible:
                incompatible.append(f"{candidate['id']} ({', '.join(filter_reasons)})")
                continue
            routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
            explicit_devices.append({
                **candidate,
                "compatibility": "passed",
                "compatibilityChecks": ["ready", "installable", "inputs", "aspect", "duration", "density", "budget"],
                "catalogRouting": routing,
            })
        if incompatible:
            raise SystemExit(f"Scene {frame['id']} has incompatible approved device candidates: " + "; ".join(incompatible))
        explicit_device_ids = {str(candidate["id"]) for candidate in explicit_devices}
        for item_id in explicit_items:
            if selected_by_id[item_id].get("kind") in REGISTRY_KINDS and item_id not in explicit_device_ids:
                explicit_devices.append({
                    "id": item_id,
                    "role": "support",
                    "responsibility": "Explicit user-requested Registry preference for this scene.",
                    "rationale": "Explicit user-requested Registry preference for this scene.",
                    "compatibility": "passed",
                    "compatibilityChecks": ["ready", "installable", "approved-explicitly"],
                    "catalogRouting": selected_by_id[item_id].get("routing", {}),
                })
                explicit_device_ids.add(item_id)

        media_entries = [entry for entry in selected_entries if entry.get("kind") in MEDIA_KINDS]
        ranked_media = sorted(
            media_entries,
            key=lambda entry: (-score(entry, media_query, favorites, set())[0], score(entry, media_query, favorites, set())[1]),
        )
        media_ids = unique(explicit_media + [
            str(entry["id"]) for entry in ranked_media
            if score(entry, media_query, favorites, set())[0] > 1
        ])[:3]
        media_candidates = [
            {
                "id": item_id,
                "rationale": (
                    "Scene-approved media or preferred semantic SFX."
                    if item_id in explicit_media
                    else "Media identity matches the approved scene content."
                ),
            }
            for item_id in media_ids
        ]

        device_candidates = list(explicit_devices)
        device_candidates = device_candidates[:3]
        need["device"] = str(frame["device"])
        need["hero"] = bool(frame["hero"])
        need["visualPattern"] = str(frame["visual_pattern"])
        need["heroVisual"] = frame["hero_visual"]
        need["cognitiveAction"] = str(frame["cognitive_action"])
        need["evidenceType"] = str(frame["evidence_type"])
        need["narrativeScale"] = str(frame["narrative_scale"])
        need["componentBudget"] = int(frame["component_budget"])
        need["mediaCandidates"] = media_candidates
        need["deviceCandidates"] = device_candidates
        need["candidateIds"] = unique(
            [candidate["id"] for candidate in media_candidates]
            + [candidate["id"] for candidate in device_candidates]
        )
        need["incomingTransition"] = next(
            (
                {
                    "boundaryId": item["boundary_id"],
                    "catalogId": item["catalog_id"],
                    "role": item["role"],
                    "purpose": item["purpose"],
                    "sameBackground": item["same_background"],
                    "perceptualAnchor": item["perceptual_anchor"],
                    "colorDependency": item["color_dependency"],
                }
                for item in storyboard["transitions"]
                if item["to_scene"] == frame["id"]
            ),
            None,
        )
        need["outgoingTransition"] = next(
            (
                {
                    "boundaryId": item["boundary_id"],
                    "catalogId": item["catalog_id"],
                    "role": item["role"],
                    "purpose": item["purpose"],
                    "sameBackground": item["same_background"],
                    "perceptualAnchor": item["perceptual_anchor"],
                    "colorDependency": item["color_dependency"],
                }
                for item in storyboard["transitions"]
                if item["from_scene"] == frame["id"]
            ),
            None,
        )
    registry_mode = "http" if args.registry_source.startswith(("http://", "https://")) else "local-staging"
    output = {
        "schemaVersion": CURATION_SCHEMA_VERSION,
        "policy": args.policy,
        "frame": {
            "preset": args.frame_preset,
            "projectPath": "frame.md",
            "sourcePath": f"frames/{args.frame_preset}/FRAME.md",
            "sourceSha256": sha256(frame_path),
            "treatment": None,
        },
        "registry": {
            "source": args.registry_source,
            "mode": registry_mode,
            "catalogRevision": catalog.get("revision"),
        },
        "palette": {
            "blocks": blocks,
            "components": components,
            "transitions": transitions,
            "media": media,
        },
        "selectionEvidence": {
            "query": combined_summary,
            "sceneNeeds": scene_needs,
            "storyboardSha256": object_sha256(storyboard),
            "tier": "skill-directed-hard-compatibility",
            "selectionAuthority": "approved-storyboard-spec",
            "favorite": sorted(favorites),
            "avoid": sorted(avoided),
            "registryFiltered": len(unavailable_registry),
        },
        "requiredAssets": sorted(
            item_id for item_id in (must_use | default_sfx)
            if selected_by_id.get(item_id, {}).get("kind") not in REGISTRY_KINDS
        ),
        "forbidden": unique(args.forbidden),
        "onMiss": "stop-and-request-exception" if args.policy == "approved-only" else "record-and-customize",
        "catalogMisses": [],
    }
    write_json(args.output, output)
    print(f"Wrote {args.output} with {len(blocks)} blocks, {len(components)} components, {len(transitions)} transitions, and {len(media)} media candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
