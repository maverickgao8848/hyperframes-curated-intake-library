#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from jsonschema import Draft202012Validator

from _routed import result_packet, validate_request
from _curation import CURATION_SCHEMA_VERSION, MANIFEST_SCHEMA_VERSION, catalog_index, compiled_storyboard, copy_verified, entry_source_paths, load_catalog, load_json, load_storyboard_spec, object_sha256, render_storyboard, sha256, source_target_for_asset, unique, validate_production_review, validate_recipe_resolutions, write_json, yaml_scalar
from _registry import default_library


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a canonical HyperFrames Curated Intake v3 packet; stop before Build.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--library", type=Path, default=default_library(), help="Library containing catalog.json (default: skill assets/library)")
    parser.add_argument("--curation", type=Path, required=True)
    parser.add_argument("--storyboard-spec", type=Path, required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--workflow", default="general-video")
    parser.add_argument("--animation-skill", type=Path, help="Deprecated; v3 uses bind catalog or authored IDs directly.")
    parser.add_argument("--asset", action="append", default=[])
    parser.add_argument("--replace-approved-outline", action="store_true")
    parser.add_argument("--request", type=Path)
    return parser.parse_args()


def assert_writeable(path: Path, replace: bool) -> None:
    if path.exists() and not replace:
        raise SystemExit(f"Refusing to replace existing file without --replace-approved-outline: {path}")


def required_ids(storyboard: dict, resolutions: dict[tuple[str, str], str]) -> list[str]:
    return unique(
        resolutions.get((scene["id"], binding["id"]), binding["id"])
        for scene in storyboard["scenes"]
        for binding in scene["uses"]
        if binding["required"] and not binding["id"].startswith("authored:")
    )


def assert_production_review(storyboard: dict, curation: dict, library: Path) -> dict[tuple[str, str], str]:
    storyboard_hash = object_sha256(storyboard)
    review = curation.get("review") if isinstance(curation.get("review"), dict) else {}
    if curation.get("storyboardHash") != storyboard_hash:
        raise SystemExit("Storyboard review/curation hash does not match the exact production Storyboard")
    try:
        validate_production_review(storyboard, review)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    try:
        return validate_recipe_resolutions(storyboard, curation, library)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error


def stage_required(project: Path, library: Path, storyboard: dict, curation: dict, resolutions: dict[tuple[str, str], str]) -> dict:
    catalog, catalog_name = load_catalog(library)
    index = catalog_index(catalog)
    items = []
    claims = curation.get("recipeResolutions", [])
    for item_id in required_ids(storyboard, resolutions):
        entry = index.get(item_id)
        if not entry:
            raise SystemExit(f"Required Storyboard binding is not in the catalog: {item_id}")
        files = []
        kind = str(entry.get("kind"))
        for source, target_name, expected in entry_source_paths(library, entry):
            if kind == "registry-block":
                destination = Path("compositions/library") / target_name
            elif kind == "registry-component":
                destination = Path("compositions/components/library") / target_name
            else:
                destination = source_target_for_asset(entry, source)
            copied_hash = copy_verified(source, project / destination, expected or entry.get("sha256"))
            files.append({"sourcePath": source.relative_to(library).as_posix(), "sourceHash": sha256(source), "destinationPath": destination.as_posix(), "destinationHash": copied_hash})
        if not files:
            raise SystemExit(f"No stageable source files for required binding: {item_id}")
        items.append({"id": item_id, "kind": kind, "required": True, "license": entry.get("license", {}), "provenance": {"catalogRevision": catalog.get("revision"), "catalog": catalog_name}, "integration": entry.get("integration", {}), "files": files, "recipeResolutions": [claim for claim in claims if claim.get("resolvedId") == item_id]})
    return {"schemaVersion": "hyperframes-curated-staging-receipt/v3", "storyboardHash": object_sha256(storyboard), "items": items}


def render_handoff(blockers: list[str]) -> str:
    blocker_text = "none" if not blockers else "; ".join(blockers)
    return "\n".join([
        "# HyperFrames Build Handoff", "", "Status: ready-for-build", "Schema: curated-intake/v3", "Project: .", "",
        "Canonical inputs:", "1. BRIEF.md", "2. frame.md", "3. STORYBOARD.md", "",
        "Machine manifest: .hyperframes/intake-manifest.json", "Preflight: passed" if not blockers else "Preflight: blocked",
        "Next action: Run $hyperframes in this existing project and build the approved storyboard.", f"Blockers: {blocker_text}", "",
    ])


def main() -> int:
    args = parse_args()
    project, library = args.project.resolve(), args.library.resolve()
    project.mkdir(parents=True, exist_ok=True)
    storyboard = load_storyboard_spec(args.storyboard_spec.resolve())
    curation = load_json(args.curation.resolve())
    if curation.get("schemaVersion") != CURATION_SCHEMA_VERSION:
        raise SystemExit("Unsupported curation schemaVersion")
    try:
        validate_production_review(storyboard, curation.get("review") if isinstance(curation.get("review"), dict) else {})
    except ValueError as error:
        raise SystemExit(str(error)) from error
    curation_schema = load_json(Path(__file__).resolve().parents[1] / "references" / "curation.schema.json")
    curation_errors = list(Draft202012Validator(curation_schema).iter_errors(curation))
    if curation_errors:
        raise SystemExit("Invalid curation: " + "; ".join(error.message for error in curation_errors))
    resolutions = assert_production_review(storyboard, curation, library)
    if args.request:
        request, _ = validate_request(args.request)
        result_path = project / ".hyperframes" / "curated-intake-result.json"
        assert_writeable(result_path, args.replace_approved_outline)
        write_json(result_path, result_packet(request, storyboard, curation.get("catalogMisses", [])))
        print(f"Wrote bounded routed result: {result_path}; no parallel project packet was created.")
        return 0

    frame_source = library / str(curation["frame"]["sourcePath"])
    if not frame_source.is_file() or sha256(frame_source) != curation["frame"]["sourceSha256"]:
        raise SystemExit("Selected Frame no longer matches its curation hash")
    selected = set(curation.get("selectedIds", []))
    missing_selection = sorted(set(required_ids(storyboard, resolutions)) - selected)
    if missing_selection:
        raise SystemExit("Required Storyboard bindings are absent from curation: " + ", ".join(missing_selection))

    owned = [project / name for name in ("BRIEF.md", "frame.md", "STORYBOARD.md", "HANDOFF.md", "hyperframes.json")]
    owned += [project / ".hyperframes" / name for name in ("curation.json", "intake-manifest.json", "staging-receipt.json")]
    owned.append(project / ".hyperframes" / "compiled" / "storyboard.json")
    for path in owned:
        assert_writeable(path, args.replace_approved_outline)

    copy_verified(frame_source, project / "frame.md", curation["frame"]["sourceSha256"])
    write_json(project / ".hyperframes" / "curation.json", curation)
    storyboard_path = project / "STORYBOARD.md"
    storyboard_path.write_text(render_storyboard(storyboard), encoding="utf-8")
    storyboard_hash = sha256(storyboard_path)
    write_json(project / ".hyperframes" / "compiled" / "storyboard.json", compiled_storyboard(storyboard, storyboard_hash))
    receipt = stage_required(project, library, storyboard, curation, resolutions)
    write_json(project / ".hyperframes" / "staging-receipt.json", receipt)

    for value in args.asset:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or not (project / path).is_file():
            raise SystemExit(f"Additional asset must be an existing project-relative path: {value}")
    brief = "\n".join([
        "---", f"workflow: {yaml_scalar(args.workflow)}", "intake_schema: curated-intake/v3", "intake_status: ready-for-build",
        f"title: {yaml_scalar(storyboard['title'])}", f"message: {yaml_scalar(storyboard.get('message', storyboard['title']))}", f"duration: {storyboard['duration']}",
        f"timing_mode: {storyboard['timing_mode']}", f"language: {yaml_scalar(args.language)}", f"destination: {yaml_scalar(args.destination)}",
        f"frame_preset: {yaml_scalar(curation['frame']['preset'])}", "---", "",
        "## Intent", "", args.intent.strip(), "", "## Asset policy", "",
        "Use only approved, staged, project-local assets with recorded provenance. Render-time network access is forbidden.", "",
        "## Explicit overrides", "", "None recorded.", "",
    ])
    (project / "BRIEF.md").write_text(brief, encoding="utf-8")
    registry = curation.get("registry", {})
    config = {"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions/library", "components": "compositions/components/library", "assets": "assets/library"}}
    if registry.get("mode") == "http":
        config["registry"] = registry.get("source")
    write_json(project / "hyperframes.json", config)
    hashes = {relative: sha256(project / relative) for relative in ("BRIEF.md", "frame.md", "STORYBOARD.md", "hyperframes.json", ".hyperframes/curation.json", ".hyperframes/staging-receipt.json", ".hyperframes/compiled/storyboard.json")}
    manifest = {"schemaVersion": MANIFEST_SCHEMA_VERSION, "state": "ready-for-build", "project": ".", "storyboardSchema": storyboard["schema"], "sceneIds": [scene["id"] for scene in storyboard["scenes"]], "paths": {"brief": "BRIEF.md", "frame": "frame.md", "storyboard": "STORYBOARD.md", "compiledStoryboard": ".hyperframes/compiled/storyboard.json", "curation": ".hyperframes/curation.json", "stagingReceipt": ".hyperframes/staging-receipt.json"}, "hashes": hashes, "blockers": []}
    write_json(project / ".hyperframes" / "intake-manifest.json", manifest)
    (project / "HANDOFF.md").write_text(render_handoff(manifest["blockers"]), encoding="utf-8")
    print(f"Prepared {project} with {len(storyboard['scenes'])} canonical Storyboard scenes; stopped before Build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
