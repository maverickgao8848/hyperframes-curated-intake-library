#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from jsonschema import Draft202012Validator

from _curation import catalog_index, copy_verified, entry_source_paths, load_catalog, load_json, object_sha256, sha256, source_target_for_asset, unique, validate_production_review, validate_recipe_resolutions, validate_storyboard, write_json
from _registry import default_library


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage approved Blocks, Components, SVG, Lottie, and media with one receipt format.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json (default: skill assets/library)")
    parser.add_argument("--item", action="append", default=[])
    parser.add_argument("--all-required", action="store_true")
    parser.add_argument("--method", choices=("auto", "local"), default="auto")
    parser.add_argument("--npx", default="npx", help="Deprecated; v3 stages verified local catalog sources.")
    return parser.parse_args()


def required_ids(storyboard: dict, resolutions: dict[tuple[str, str], str]) -> list[str]:
    return unique(
        resolutions.get((scene["id"], binding["id"]), binding["id"])
        for scene in storyboard["scenes"]
        for binding in scene["uses"]
        if binding["required"] and not binding["id"].startswith("authored:")
    )


def main() -> int:
    args = parse_args()
    project, library = args.project.resolve(), args.library.resolve()
    compiled = load_json(project / ".hyperframes" / "compiled" / "storyboard.json")
    if compiled.get("schemaVersion") != "hyperframes-storyboard-compiled/v3":
        raise SystemExit("Only hyperframes-storyboard-compiled/v3 can be staged")
    storyboard = compiled["storyboard"]
    validate_storyboard(storyboard)
    curation = load_json(project / ".hyperframes" / "curation.json")
    review = curation.get("review") if isinstance(curation.get("review"), dict) else {}
    try:
        validate_production_review(storyboard, review)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    curation_schema = load_json(Path(__file__).resolve().parents[1] / "references" / "curation.schema.json")
    errors = list(Draft202012Validator(curation_schema).iter_errors(curation))
    if errors:
        raise SystemExit("Invalid curation: " + "; ".join(error.message for error in errors))
    storyboard_hash = object_sha256(storyboard)
    if curation.get("storyboardHash") != storyboard_hash:
        raise SystemExit("Exact Storyboard hash does not match curation")
    try:
        resolutions = validate_recipe_resolutions(storyboard, curation, library)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    catalog, catalog_name = load_catalog(library)
    index = catalog_index(catalog)
    selected = required_ids(storyboard, resolutions) if args.all_required else args.item
    if not selected:
        raise SystemExit("Pass --all-required or at least one --item")
    approved = set(curation.get("selectedIds", []))
    outside = sorted(set(selected) - approved)
    if outside:
        raise SystemExit("Items are outside the approved Storyboard selection: " + ", ".join(outside))
    items = []
    for item_id in unique(selected):
        entry = index.get(item_id)
        if not entry or entry.get("status") != "ready":
            raise SystemExit(f"Not a ready catalog item: {item_id}")
        files = []
        for source, target, expected in entry_source_paths(library, entry):
            if entry["kind"] == "registry-block":
                destination = Path("compositions/library") / target
            elif entry["kind"] == "registry-component":
                destination = Path("compositions/components/library") / target
            else:
                destination = source_target_for_asset(entry, source)
            copied = copy_verified(source, project / destination, expected or entry.get("sha256"))
            files.append({"sourcePath": source.relative_to(library).as_posix(), "sourceHash": sha256(source), "destinationPath": destination.as_posix(), "destinationHash": copied})
        items.append({"id": item_id, "kind": entry["kind"], "required": item_id in required_ids(storyboard, resolutions), "license": entry.get("license", {}), "provenance": {"catalogRevision": catalog.get("revision"), "catalog": catalog_name}, "integration": entry.get("integration", {}), "files": files, "recipeResolutions": [claim for claim in curation.get("recipeResolutions", []) if claim.get("resolvedId") == item_id]})
    receipt = {"schemaVersion": "hyperframes-curated-staging-receipt/v3", "storyboardHash": object_sha256(storyboard), "items": items}
    write_json(project / ".hyperframes" / "staging-receipt.json", receipt)
    print(f"Staged {len(items)} approved item(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
