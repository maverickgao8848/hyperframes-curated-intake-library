#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

from _curation import CURATION_SCHEMA_VERSION, POLICIES, entry_source_paths, load_catalog, load_json, load_storyboard_spec, object_sha256, sha256, validate_production_review, write_json
from _routing import candidate_audit, evaluate_candidate, resolve_alias
from _registry import default_library


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route approved Storyboard v3 uses through capability-specific catalog lanes.")
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json (default: skill assets/library)")
    parser.add_argument("--storyboard-spec", type=Path, required=True)
    parser.add_argument("--frame-preset", required=True)
    parser.add_argument("--policy", choices=POLICIES, default="approved-first")
    parser.add_argument("--registry-source", default="local-staging")
    parser.add_argument("--must-use", action="append", default=[])
    parser.add_argument("--favorite", action="append", default=[])
    parser.add_argument("--avoid", action="append", default=[])
    parser.add_argument("--forbidden", action="append", default=[])
    parser.add_argument("--max-total", type=int, default=40, help="Resource warning threshold; never changes approved selections.")
    review = parser.add_mutually_exclusive_group(required=True)
    review.add_argument("--review-confirmation", type=Path, help="External automated-agent motion attestation bound to the exact Storyboard hash.")
    review.add_argument("--review-report", type=Path, help="Migration report for an unreviewed draft; output remains blocked from preparation.")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def lane_for(item_id: str) -> str:
    if item_id.startswith("registry-block:"):
        return "block"
    if item_id.startswith("registry-component:"):
        return "component"
    if item_id.startswith(("background:", "font:", "logo:", "lottie:", "sfx:", "svg:", "template:", "texture:")):
        return "primitive"
    if item_id.startswith("scene-blueprint:"):
        return "block"
    if item_id.startswith("motion-rule:"):
        return "motion"
    if item_id.startswith("recipe:"):
        return "recipe"
    if item_id.startswith("transition:"):
        return "transition"
    return "motion"


def scene_use_query(scene: dict, use: dict) -> str:
    """Preserve exact Unicode text and v3 authority order without token heuristics."""
    return "\n".join([
        str(scene["content"]),
        str(scene["visual"]),
        str(scene["motion"]),
        str(use["id"]),
        *(str(responsibility) for responsibility in use["responsibilities"]),
    ])


def review_record(args: argparse.Namespace, storyboard: dict, storyboard_hash: str) -> dict:
    if args.review_confirmation:
        review = load_json(args.review_confirmation.resolve())
        try:
            validate_production_review(storyboard, review)
        except ValueError as error:
            raise SystemExit(str(error)) from error
        return review
    report = load_json(args.review_report.resolve())
    if report.get("schemaVersion") != "hyperframes-storyboard-migration-report/v1" or report.get("status") != "needs-review":
        raise SystemExit("--review-report must be a needs-review Storyboard migration report")
    if report.get("outputHash") != storyboard_hash:
        raise SystemExit("Migration review report does not match the exact Storyboard hash")
    known = {scene["id"] for scene in storyboard["scenes"]}
    unresolved = report.get("unresolvedSceneIds")
    if not isinstance(unresolved, list) or not unresolved or len(unresolved) != len(set(unresolved)) or not set(unresolved) <= known:
        raise SystemExit("Migration review report must name unique unresolved Storyboard scene IDs")
    return {"state": "needs-review", "storyboardHash": storyboard_hash, "source": "migration-report", "unresolvedSceneIds": unresolved}


def routing_context(scene: dict, authority: dict | None = None) -> dict:
    routing = authority.get("routing") if isinstance(authority, dict) and isinstance(authority.get("routing"), dict) else {}
    context = {
        "family": routing.get("family"),
        "purpose": routing.get("purpose"),
        "useWhen": deepcopy(routing.get("useWhen", [])),
        "scene_duration_seconds": scene["end"] - scene["start"],
    }
    return {key: value for key, value in context.items() if value is not None}


def hard_compatible(entry: dict, context: dict, installable_registry: set[tuple[str, str]] | None) -> tuple[bool, str, list[dict]]:
    results = evaluate_candidate(entry, context, installable_registry)
    failed = [result for result in results if not result["passed"]]
    return not failed, failed[0]["filter"] if failed else "passed", results


def explicit_choice(
    requested_id: str,
    index: dict[str, dict],
    context: dict,
    installable_registry: set[tuple[str, str]] | None,
    prior_use: dict[str, int],
    forbidden: set[str],
) -> tuple[str | None, list[dict], list[dict], str]:
    """Validate one explicit lock; only a disabled item may traverse declared fallbacks."""
    entry = index.get(requested_id)
    if requested_id in forbidden:
        return None, [], [], "explicit catalog ID conflicts with a user exclusion"
    if entry is None:
        if requested_id.startswith("talkcraft:"):
            return requested_id, [], [], "talkcraft lock passed through without synthesized metadata"
        return None, [], [], "explicit catalog ID is missing"
    compatible, reason, filters = hard_compatible(entry, context, installable_registry)
    audit = candidate_audit(entry, context, filters, prior_use)
    if compatible:
        return requested_id, [audit], [], "passed"
    rejected = [audit]
    if entry.get("status") != "disabled":
        return None, [], rejected, reason
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
    trace = [requested_id]
    for fallback_id in routing.get("fallbackIds", []):
        fallback_id = str(fallback_id)
        trace.append(fallback_id)
        fallback = index.get(fallback_id)
        if fallback is None or fallback_id in forbidden:
            continue
        passed, _, fallback_filters = hard_compatible(fallback, context, installable_registry)
        fallback_audit = candidate_audit(fallback, context, fallback_filters, prior_use, fallback_trace=trace)
        if passed:
            return fallback_id, [fallback_audit], rejected, "declared fallback"
        rejected.append(fallback_audit)
    return None, [], rejected, "disabled explicit ID has no compatible declared fallback"


def main() -> int:
    args = parse_args()
    library = args.library.resolve()
    storyboard = load_storyboard_spec(args.storyboard_spec.resolve())
    storyboard_hash = object_sha256(storyboard)
    review = review_record(args, storyboard, storyboard_hash)
    catalog, catalog_name = load_catalog(library)
    catalog_hash = sha256(library / catalog_name)
    entries = [entry for entry in catalog.get("entries", []) if isinstance(entry, dict) and entry.get("id")]
    index = {str(entry["id"]): entry for entry in entries}
    alias_path = library / "legacy-component-aliases.json"
    aliases = load_json(alias_path).get("aliases", {}) if alias_path.is_file() else {}
    alias_hash = sha256(alias_path) if alias_path.is_file() else None
    inventory_path = library / "frames" / "inventory.json"
    inventory = load_json(inventory_path) if inventory_path.is_file() else {"frames": []}
    frame_record = next((item for item in inventory.get("frames", []) if item.get("preset") == args.frame_preset), None)
    frame_path = library / frame_record["path"] if frame_record else None
    if frame_path is None or not frame_path.is_file():
        raise SystemExit(f"Unknown frame preset: {args.frame_preset}")
    observed_frame_hash = sha256(frame_path)
    if observed_frame_hash != frame_record.get("sha256"):
        raise SystemExit(f"Frame hash mismatch for preset: {args.frame_preset}")
    registry_path = library / "registry" / "registry.json"
    installable_registry = None
    if registry_path.is_file():
        registry = load_json(registry_path)
        installable_registry = {(str(item.get("name")), str(item.get("type"))) for item in registry.get("items", []) if isinstance(item, dict)}

    forbidden = set(args.avoid) | set(args.forbidden)
    favorites = {resolve_alias(item, aliases) or item for item in args.favorite}
    approved: set[str] = set()
    prior_use: dict[str, int] = {}
    needs_records: list[dict] = []
    misses: list[dict] = []
    recipe_resolutions: list[dict] = []
    for scene in storyboard["scenes"]:
        bindings = [(None, item["id"], scene_use_query(scene, item), item["required"]) for item in scene["uses"]]
        seen: set[tuple[str | None, str]] = set()
        for event_id, selected_ref, query, required in bindings:
            original_ref = str(selected_ref)
            selected_ref = resolve_alias(original_ref, aliases)
            if original_ref.startswith("recipe:") and (selected_ref is None or selected_ref == original_ref):
                if required:
                    raise SystemExit(f"Required Storyboard recipe is unresolved: {scene['id']}/{original_ref}")
                source = {"type": "storyboard-use", "resolver": "legacy-component-aliases.json"}
                misses.append({"id": original_ref, "sceneId": scene["id"], "eventId": event_id, "lane": "recipe", "need": query, "returnedCandidates": [], "result": "no_recommendation", "rejectionReason": "unresolved-recipe", "reason": "unresolved-recipe", "required": False, "source": source, "provenance": {"storyboardHash": storyboard_hash}})
                needs_records.append({"sceneId": scene["id"], "eventId": event_id, "lane": "recipe", "query": query, "affordances": [], "candidates": [], "selectedRef": None, "result": "no_recommendation", "rejections": []})
                continue
            if selected_ref is None:
                if required:
                    raise SystemExit(f"Required Storyboard use is unavailable: {scene['id']}/{original_ref}: alias resolves to no recommendation")
                misses.append({"id": "miss-" + re.sub(r"[^a-z0-9]+", "-", f"{scene['id']}-use-no-recommendation".lower()).strip("-"), "sceneId": scene["id"], "eventId": event_id, "lane": "component", "need": query, "returnedCandidates": [], "result": "no_recommendation", "rejectionReason": f"Legacy binding {original_ref} intentionally resolves to no_recommendation."})
                needs_records.append({"sceneId": scene["id"], "eventId": event_id, "lane": "component", "query": query, "affordances": [], "candidates": [], "selectedRef": None, "result": "no_recommendation", "rejections": []})
                continue
            if (event_id, selected_ref) in seen:
                continue
            seen.add((event_id, selected_ref))
            lane = lane_for(str(selected_ref))
            selected_entry = index.get(str(selected_ref), {})
            context = routing_context(scene, selected_entry)
            context["_library"] = str(library)
            context["_catalog"] = "catalog.json"
            context["_catalogRevision"] = catalog.get("revision")
            candidates, rejections = [], []
            if str(selected_ref).startswith("authored:"):
                selected_catalog_ref = None
                choice_reason = f"Storyboard explicitly binds authored gap {selected_ref}; no compatible catalog implementation was approved."
            else:
                selected_catalog_ref, candidates, rejected_audits, choice_reason = explicit_choice(
                    str(selected_ref), index, context, installable_registry, prior_use, forbidden,
                )
                rejections = [
                    {"id": item["id"], "reason": next((result["filter"] for result in item["hardFilterResults"] if not result["passed"]), "rejected"), "filterResults": item["hardFilterResults"]}
                    for item in rejected_audits
                ]
                if selected_catalog_ref:
                    approved.add(selected_catalog_ref)
                    prior_use[selected_catalog_ref] = prior_use.get(selected_catalog_ref, 0) + 1
                    if original_ref.startswith("recipe:"):
                        resolved_entry = index[selected_catalog_ref]
                        recipe_resolutions.append({
                            "sceneId": scene["id"], "id": original_ref, "required": required,
                            "resolvedId": selected_catalog_ref,
                            "provenance": {
                                "library": "selected-library", "catalog": catalog_name,
                                "catalogRevision": catalog.get("revision"), "catalogSha256": catalog_hash,
                                "aliases": alias_path.name, "aliasesSha256": alias_hash,
                                "sourceFiles": [
                                    {"path": source.relative_to(library).as_posix(), "sha256": sha256(source)}
                                    for source, _, _ in entry_source_paths(library, resolved_entry)
                                ],
                                "status": resolved_entry.get("status"), "license": deepcopy(resolved_entry.get("license")),
                                "integration": deepcopy(resolved_entry.get("integration")),
                            },
                        })
            if selected_catalog_ref is None:
                misses.append({"id": "miss-" + re.sub(r"[^a-z0-9]+", "-", f"{scene['id']}-use-{lane}".lower()).strip("-"), "sceneId": scene["id"], "eventId": event_id, "lane": lane, "need": query, "returnedCandidates": [item["id"] for item in candidates], "result": "no_recommendation", "rejectionReason": choice_reason})
                if required and not str(selected_ref).startswith("authored:") and review["state"] == "approved":
                    raise SystemExit(f"Required Storyboard use is unavailable: {scene['id']}/{selected_ref}: {choice_reason}")
            needs_records.append({"sceneId": scene["id"], "eventId": event_id, "lane": lane, "query": query, "affordances": [], "candidates": candidates, "selectedRef": selected_catalog_ref, "result": "recommended" if selected_catalog_ref else "no_recommendation", "rejections": rejections})

    normalized_forced = {resolved for item in args.must_use if (resolved := resolve_alias(item, aliases))}
    unknown_forced = sorted(item for item in (normalized_forced | favorites) - set(index) if not item.startswith("talkcraft:"))
    if unknown_forced:
        raise SystemExit("Unknown catalog IDs: " + ", ".join(unknown_forced))
    for item in sorted(normalized_forced):
        selected, _, _, reason = explicit_choice(item, index, {"_library": str(library)}, installable_registry, {}, forbidden)
        if selected is None:
            raise SystemExit(f"Explicit catalog lock {item} failed hard compatibility: {reason}")
        approved.add(selected)
    if len(approved) > args.max_total:
        print(f"WARNING: {len(approved)} approved items exceed resource threshold {args.max_total}; approval was preserved.")
    output = {
        "schemaVersion": CURATION_SCHEMA_VERSION,
        "policy": args.policy,
        "frame": {"preset": args.frame_preset, "projectPath": "frame.md", "sourcePath": frame_record["path"], "sourceSha256": observed_frame_hash, "treatment": None},
        "registry": {"source": args.registry_source, "mode": "http" if args.registry_source.startswith(("http://", "https://")) else "local-staging", "catalogRevision": catalog.get("revision")},
        "storyboardHash": storyboard_hash,
        "review": review,
        "needs": needs_records,
        "selectedIds": sorted(approved),
        "catalogMisses": misses,
        "recipeResolutions": recipe_resolutions,
    }
    schema = load_json(Path(__file__).resolve().parents[1] / "references" / "curation.schema.json")
    errors = list(Draft202012Validator(schema).iter_errors(output))
    if errors:
        raise SystemExit("Generated invalid curation: " + "; ".join(error.message for error in errors))
    write_json(args.output.resolve(), output)
    print(f"Wrote {args.output} with {len(needs_records)} lane-specific needs, {len(approved)} approved catalog bindings, and {len(misses)} misses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
