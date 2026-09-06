from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from _storyboard_v3_contract import validate_storyboard_v3


STORYBOARD_SCHEMA_VERSION = "hyperframes-storyboard/v3"
CURATION_SCHEMA_VERSION = "hyperframes-curated-intake/v5"
MANIFEST_SCHEMA_VERSION = "curated-intake/v3"
MOTION_ATTESTATION_RUBRIC_VERSION = "motion-attestation/v1"
POLICIES = ("approved-first", "approved-only", "open")
LIBRARY_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references/library.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_storyboard(value: dict[str, Any]) -> None:
    validate_storyboard_v3(value)


def load_storyboard_spec(path: Path) -> dict[str, Any]:
    value = load_json(path)
    if value.get("schema") != STORYBOARD_SCHEMA_VERSION:
        if value.get("schema") == "hyperframes-storyboard/v2":
            raise ValueError(
                "Storyboard v2 is migration-only; run migrate-storyboard-v2-to-v3.py "
                "--input <v2.json> --output <v3-draft.json> --report <migration-report.json>"
            )
        raise ValueError("Only hyperframes-storyboard/v3 is accepted by the production runtime")
    validate_storyboard(value)
    return value


def validate_production_review(storyboard: dict[str, Any], review: dict[str, Any]) -> None:
    """Validate attestation structure/provenance only; semantic judgment belongs to the agent rubric."""
    expected_hash = object_sha256(storyboard)
    if review.get("state") != "approved" or review.get("source") != "automated-agent-attestation":
        raise ValueError("production requires an automated-agent motion attestation")
    if review.get("storyboardHash") != expected_hash:
        raise ValueError("motion review Storyboard hash is stale")
    reviewer = review.get("reviewer") if isinstance(review.get("reviewer"), dict) else {}
    if reviewer.get("type") != "automated-agent" or reviewer.get("workflow") not in {"curated-intake", "visual-director"}:
        raise ValueError("motion review has unsupported automated-agent provenance")
    actual_rubric = reviewer.get("rubricVersion")
    if actual_rubric != MOTION_ATTESTATION_RUBRIC_VERSION:
        raise ValueError(
            f"unsupported motion attestation rubricVersion: actual={actual_rubric!r}; "
            f"supported={MOTION_ATTESTATION_RUBRIC_VERSION!r}"
        )
    model_id = reviewer.get("modelId")
    run_provenance = reviewer.get("runProvenance")
    if not ((isinstance(model_id, str) and model_id.strip()) or (isinstance(run_provenance, dict) and run_provenance)):
        raise ValueError("motion review requires modelId or runProvenance")
    long_scenes = {scene["id"]: scene for scene in storyboard["scenes"] if scene["end"] - scene["start"] > 3}
    records = review.get("sceneReviews", [])
    by_id = {record.get("sceneId"): record for record in records if isinstance(record, dict)}
    if len(by_id) != len(records) or set(by_id) != set(long_scenes):
        raise ValueError("motion review must contain exactly one record for every scene longer than 3 seconds")
    for scene_id, scene in long_scenes.items():
        record = by_id[scene_id]
        if record.get("motionQuote") != scene["motion"]:
            raise ValueError(f"Scene {scene_id} motionQuote is not the exact Storyboard motion")
        if record.get("decision") not in {"internal-change", "static-reason"}:
            raise ValueError(f"Scene {scene_id} has an unsupported motion decision")
        if not isinstance(record.get("conclusion"), dict) or not record["conclusion"]:
            raise ValueError(f"Scene {scene_id} lacks a structured conclusion")
        if not isinstance(record.get("rationale"), str) or not record["rationale"].strip():
            raise ValueError(f"Scene {scene_id} lacks an attestation rationale")


def storyboard_scene_text(scene: dict[str, Any]) -> str:
    return " ".join([
        scene["content"], scene["visual"], scene["motion"], scene.get("narration", ""),
        *(scene.get("on_screen_text", [])),
        *(responsibility for binding in scene["uses"] for responsibility in binding["responsibilities"]),
    ])


def one_line(value: Any) -> str:
    return " ".join(str(value).split())


def render_storyboard(spec: dict[str, Any]) -> str:
    validate_storyboard(spec)
    header = [
        "---", f"schema: {spec['schema']}", f"title: {json.dumps(spec['title'], ensure_ascii=False)}",
        f"duration: {spec['duration']}", f"timing_mode: {spec['timing_mode']}",
    ]
    if spec.get("message"):
        header.append(f"message: {json.dumps(spec['message'], ensure_ascii=False)}")
    lines = header + ["---", "", "# Storyboard", ""]
    for scene in spec["scenes"]:
        lines.extend([
            f"## {scene['id']} · {scene['start']:g}–{scene['end']:g}s" + (f" · {scene['title']}" if scene.get("title") else ""), "",
            f"Content: {one_line(scene['content'])}", "", f"Visual: {one_line(scene['visual'])}", "",
            f"Motion: {one_line(scene['motion'])}", "", "Uses:", "",
        ])
        if scene["uses"]:
            for binding in scene["uses"]:
                lines.append(f"- {binding['id']} · required={str(binding['required']).lower()} · responsibilities={one_line('; '.join(binding['responsibilities']))}")
        else:
            lines.append("- None")
        if scene.get("next"):
            lines.extend(["", f"Next: {scene['next']['sceneId']} · {one_line(scene['next']['transition'])}"])
        for label, key in (("Narration", "narration"), ("On-screen text", "on_screen_text"), ("SFX", "sfx")):
            if scene.get(key):
                value = scene[key] if isinstance(scene[key], str) else "; ".join(scene[key])
                lines.extend(["", f"{label}: {one_line(value)}"])
        if scene.get("source_anchor"):
            lines.extend(["", f"Source anchor: {one_line(scene['source_anchor']['source'])} · {one_line(scene['source_anchor']['anchor'])}"])
        if scene.get("locks"):
            enabled = ", ".join(key for key, locked in scene["locks"].items() if locked)
            lines.extend(["", f"Locks: {enabled or 'none'}"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def compiled_storyboard(spec: dict[str, Any], source_hash: str) -> dict[str, Any]:
    return {"schemaVersion": "hyperframes-storyboard-compiled/v3", "generated": True, "source": "STORYBOARD.md", "sourceHash": source_hash, "storyboard": spec}


def catalog_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(entry["id"]): entry for entry in catalog.get("entries", []) if isinstance(entry, dict) and entry.get("id")}


def load_catalog(library: Path) -> tuple[dict[str, Any], str]:
    # catalog.json is the only routing authority. director-catalog.json is a
    # deterministic projection for the Visual Director and must never feed
    # facts back into Curated Intake.
    path = library / "catalog.json"
    try:
        catalog: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Catalog configuration error: entry=<catalog>; path={path}#/; field=document; {error}"
        ) from error
    schema = load_json(LIBRARY_SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(catalog),
        key=lambda error: [str(value) for value in error.absolute_path],
    )
    if errors:
        rendered: list[str] = []
        entries = catalog.get("entries") if isinstance(catalog, dict) and isinstance(catalog.get("entries"), list) else []
        for error in errors:
            parts = list(error.absolute_path)
            entry_id = "<catalog>"
            if len(parts) >= 2 and parts[0] == "entries" and isinstance(parts[1], int) and parts[1] < len(entries):
                candidate = entries[parts[1]]
                if isinstance(candidate, dict):
                    entry_id = str(candidate.get("id") or f"entries[{parts[1]}]")
            missing = []
            if error.validator == "required" and isinstance(error.instance, dict):
                missing = [str(field) for field in error.validator_value if field not in error.instance]
            field = ",".join(missing) if missing else (str(parts[-1]) if parts else str(error.validator))
            json_path = "/" + "/".join(str(value) for value in parts)
            rendered.append(
                f"entry={entry_id}; path={path}#{json_path}; field={field}; {error.message}"
            )
        raise ValueError("Catalog configuration error: " + " | ".join(rendered))
    return catalog, path.name


def ensure_within(root: Path, path: Path) -> Path:
    resolved_root, resolved = root.resolve(), path.resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise ValueError(f"Path leaves root: {path}")
    return resolved


def entry_source_paths(library: Path, entry: dict[str, Any]) -> list[tuple[Path, str, str | None]]:
    source = entry.get("source", {})
    if source.get("type") == "bundle":
        return [(ensure_within(library, library / item["path"]), item.get("target") or Path(item["path"]).name, item.get("sha256")) for item in source.get("files", [])]
    path = source.get("path")
    return [(ensure_within(library, library / path), Path(path).name, entry.get("sha256"))] if path else []


def validate_recipe_resolutions(storyboard: dict[str, Any], curation: dict[str, Any], library: Path) -> dict[tuple[str, str], str]:
    """Re-resolve every recipe against the selected library; never trust a stored claim alone."""
    recipes = {
        (scene["id"], binding["id"]): bool(binding["required"])
        for scene in storyboard["scenes"] for binding in scene["uses"]
        if binding["id"].startswith("recipe:")
    }
    claims = curation.get("recipeResolutions", [])
    if not recipes and not claims:
        return {}
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("recipe resolution claim must be an object")
        key = (claim.get("sceneId"), claim.get("id"))
        if key in by_key:
            raise ValueError(f"duplicate/conflicting recipe resolution claim: {key[0]}/{key[1]}")
        by_key[key] = claim
    fabricated = set(by_key) - set(recipes)
    if fabricated:
        scene_id, recipe_id = sorted(fabricated)[0]
        raise ValueError(f"fabricated recipe resolution claim: {scene_id}/{recipe_id}")
    missing = set(recipes) - set(by_key)
    if missing:
        scene_id, recipe_id = sorted(missing)[0]
        raise ValueError(f"unresolved migration-only recipe binding: {scene_id}/{recipe_id}")
    catalog, catalog_name = load_catalog(library)
    index = catalog_index(catalog)
    catalog_hash = sha256(library / catalog_name)
    alias_path = library / "legacy-component-aliases.json"
    if not alias_path.is_file():
        raise ValueError("selected library has no legacy recipe resolver")
    alias_document = load_json(alias_path)
    aliases = alias_document.get("aliases", {})
    alias_hash = sha256(alias_path)
    resolved: dict[tuple[str, str], str] = {}
    for key, claim in by_key.items():
        scene_id, recipe_id = key
        record = aliases.get(recipe_id)
        actual_id = str(record.get("registry_id")) if isinstance(record, dict) and record.get("result") == "ready" and record.get("registry_id") else None
        if actual_id is None or actual_id.startswith("recipe:") or claim.get("resolvedId") != actual_id:
            raise ValueError(f"stale or fabricated recipe resolution: {scene_id}/{recipe_id}")
        if claim.get("required") is not recipes[key]:
            raise ValueError(f"recipe required flag changed: {scene_id}/{recipe_id}")
        entry = index.get(actual_id)
        if not entry or entry.get("status") != "ready" or not isinstance(entry.get("license"), dict) or not entry["license"] or not isinstance(entry.get("integration"), dict) or not entry["integration"]:
            raise ValueError(f"resolved recipe is not a ready, licensed, integrated catalog item: {actual_id}")
        source_files = entry_source_paths(library, entry)
        if not source_files:
            raise ValueError(f"resolved recipe is not stageable: {actual_id}")
        actual_sources = []
        for source, _, expected_hash in source_files:
            observed_hash = sha256(source)
            declared_hash = str(expected_hash or entry.get("sha256", "")).removeprefix("sha256:")
            if declared_hash and observed_hash != declared_hash:
                raise ValueError(f"resolved recipe source hash mismatch: {actual_id}/{source.relative_to(library).as_posix()}")
            actual_sources.append({"path": source.relative_to(library).as_posix(), "sha256": observed_hash})
        provenance = claim.get("provenance") if isinstance(claim.get("provenance"), dict) else {}
        expected = {
            "library": "selected-library", "catalog": catalog_name, "catalogRevision": catalog.get("revision"),
            "catalogSha256": catalog_hash, "aliases": alias_path.name, "aliasesSha256": alias_hash,
            "sourceFiles": actual_sources, "status": entry.get("status"), "license": entry.get("license"),
            "integration": entry.get("integration"),
        }
        if provenance != expected:
            raise ValueError(f"stale recipe library provenance: {scene_id}/{recipe_id}")
        if actual_id not in curation.get("selectedIds", []):
            raise ValueError(f"resolved recipe is absent from selectedIds: {scene_id}/{recipe_id}")
        resolved[key] = actual_id
    return resolved


def source_target_for_asset(entry: dict[str, Any], source: Path) -> Path:
    kind = str(entry.get("kind", "asset"))
    safe_id = str(entry["id"]).replace(":", "-")
    return Path("assets") / "library" / kind / f"{safe_id}{source.suffix}"


def copy_verified(source: Path, target: Path, expected_sha256: str | None) -> str:
    observed = sha256(source)
    if expected_sha256 and observed != str(expected_sha256).removeprefix("sha256:"):
        raise ValueError(f"Source hash mismatch: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return sha256(target)


def yaml_scalar(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))
