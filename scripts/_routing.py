"""Deterministic, explainable routing primitives for Curated Intake."""

from __future__ import annotations

import re
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable


SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
LONG_SCENE_SECONDS = 3.0
LIBRARY_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references/library.schema.json"


def _integration_contract() -> tuple[frozenset[str], frozenset[str], frozenset[str], frozenset[str]]:
    schema = json.loads(LIBRARY_SCHEMA_PATH.read_text(encoding="utf-8"))
    contract = schema["$defs"]["entry"]["properties"]["integration"]
    properties = contract["properties"]
    return (
        frozenset(str(value) for value in properties["mode"]["enum"]),
        frozenset(str(value) for value in properties["timelineOwner"]["enum"]),
        frozenset(str(value) for value in contract["required"]),
        frozenset(str(value) for value in properties),
    )


INTEGRATION_MODES, TIMELINE_OWNERS, INTEGRATION_REQUIRED, INTEGRATION_FIELDS = _integration_contract()


def resolve_alias(value: str, aliases: dict[str, Any]) -> str | None:
    record = aliases.get(value)
    if not isinstance(record, dict):
        return value
    if record.get("result") == "no_recommendation":
        return None
    target = record.get("registry_id")
    return str(target) if target else value


def _required_inputs(entry: dict[str, Any]) -> set[str]:
    parameters = entry.get("parameters") if isinstance(entry.get("parameters"), dict) else {}
    required = {str(value) for value in parameters.get("required", []) if isinstance(value, str) and value}
    interface = entry.get("interface") if isinstance(entry.get("interface"), dict) else {}
    required.update(
        str(prop["name"])
        for prop in interface.get("props", [])
        if isinstance(prop, dict) and prop.get("required") is True and isinstance(prop.get("name"), str)
    )
    return required


def _source_declared(entry: dict[str, Any]) -> bool:
    source = entry.get("source")
    if not isinstance(source, dict) or not source:
        return False
    if source.get("type") == "bundle":
        files = source.get("files")
        return bool(source.get("entry")) and isinstance(files, list) and bool(files)
    return bool(source.get("path") or source.get("repository") or source.get("name"))


def _hashes_declared(entry: dict[str, Any]) -> bool:
    digest = entry.get("sha256")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        return False
    source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
    if source.get("type") != "bundle":
        return True
    files = source.get("files")
    return isinstance(files, list) and bool(files) and all(
        isinstance(record, dict)
        and isinstance(record.get("sha256"), str)
        and SHA256_RE.fullmatch(record["sha256"]) is not None
        for record in files
    )


def _source_hashes_match(entry: dict[str, Any], library_value: Any) -> bool:
    if not library_value:
        return _hashes_declared(entry)
    library = Path(str(library_value)).resolve()
    source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
    records = source.get("files") if source.get("type") == "bundle" else [
        {"path": source.get("path"), "sha256": entry.get("sha256")}
    ]
    if not isinstance(records, list) or not records:
        return False
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            return False
        path = (library / record["path"]).resolve()
        if library != path and library not in path.parents:
            return False
        expected = record.get("sha256")
        if not path.is_file() or not isinstance(expected, str):
            return False
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            return False
    return True


def _avoid_conflicts(entry: dict[str, Any], context: dict[str, Any]) -> list[str]:
    entry_id = str(entry.get("id", ""))
    declared = context.get("avoidConflicts")
    if isinstance(declared, dict):
        value = declared.get(entry_id)
        if value is True:
            return ["explicit conflict"]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        if isinstance(value, list):
            return [str(item) for item in value if isinstance(item, str) and item.strip()]
    active = {
        " ".join(str(item).split()).casefold()
        for item in context.get("avoidWhen", [])
        if isinstance(item, str) and item.strip()
    }
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
    return [
        str(item) for item in routing.get("avoidWhen", [])
        if isinstance(item, str) and " ".join(item.split()).casefold() in active
    ]


def _semantic_matches(entry: dict[str, Any], context: dict[str, Any]) -> tuple[bool, list[str], bool]:
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
    family = context.get("family")
    family_match = isinstance(family, str) and routing.get("family") == family
    wanted_use = {
        " ".join(str(value).split()).casefold()
        for value in context.get("useWhen", [])
        if isinstance(value, str) and value.strip()
    }
    matched_use = [
        str(value) for value in routing.get("useWhen", [])
        if isinstance(value, str) and " ".join(value.split()).casefold() in wanted_use
    ]
    purpose = context.get("purpose")
    purpose_match = (
        isinstance(purpose, str)
        and isinstance(routing.get("purpose"), str)
        and " ".join(purpose.split()).casefold() == " ".join(routing["purpose"].split()).casefold()
    )
    return family_match, matched_use, purpose_match


def _motion_preference(entry: dict[str, Any], context: dict[str, Any]) -> str:
    duration = context.get("scene_duration_seconds", context.get("duration_seconds"))
    if not isinstance(duration, (int, float)) or duration <= LONG_SCENE_SECONDS:
        return "acceptable"
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
    return "mismatch" if routing.get("motion") == "entrance-only" else "preferred"


def evaluate_candidate(
    entry: dict[str, Any], context: dict[str, Any], installable_registry: set[tuple[str, str]] | None,
) -> list[dict[str, Any]]:
    """Return machine-fact and explicit-conflict gates in a stable order."""
    source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
    integration = entry.get("integration") if isinstance(entry.get("integration"), dict) else {}
    license_data = entry.get("license") if isinstance(entry.get("license"), dict) else {}
    results: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        results.append({"filter": name, "passed": bool(passed), "detail": detail or "not applicable"})

    add("status", entry.get("status") == "ready", f"status={entry.get('status')!r}")
    rights = bool(license_data) and license_data.get("status") not in {"missing", "restricted", "unknown"}
    add("license", rights, "declared" if rights else "missing or restricted")
    source_ok = _source_declared(entry)
    add("source", source_ok, "declared" if source_ok else "missing install source")
    hashes_ok = _hashes_declared(entry) and _source_hashes_match(entry, context.get("_library"))
    add("hash", hashes_ok, "declared" if hashes_ok else "missing or invalid SHA-256")
    integration_ok = (
        isinstance(entry.get("integration"), dict)
        and frozenset(integration) == INTEGRATION_REQUIRED == INTEGRATION_FIELDS
        and isinstance(integration.get("mode"), str)
        and integration["mode"] in INTEGRATION_MODES
        and isinstance(integration.get("timelineOwner"), str)
        and integration["timelineOwner"] in TIMELINE_OWNERS
        and integration.get("renderTimeNetwork") is False
    )
    add(
        "integration",
        integration_ok,
        f"mode={integration.get('mode')!r}; timelineOwner={integration.get('timelineOwner')!r}; renderTimeNetwork={integration.get('renderTimeNetwork')!r}",
    )

    required = _required_inputs(entry)
    available = {str(value) for value in context.get("available_inputs", []) if isinstance(value, str)}
    missing = sorted(required - available)
    add("required_inputs", not missing, "available" if not missing else "missing=" + ",".join(missing))

    aspect = context.get("aspect")
    supported = entry.get("aspectSupport") if isinstance(entry.get("aspectSupport"), list) else []
    aspect_ok = not aspect or (bool(supported) and aspect in supported)
    add("aspect", aspect_ok, f"requested={aspect!r}; supported={supported!r}")

    wanted_dimensions = context.get("dimensions")
    actual_dimensions = entry.get("dimensions") if isinstance(entry.get("dimensions"), dict) else None
    dimensions_ok = not isinstance(wanted_dimensions, dict) or actual_dimensions == wanted_dimensions
    add("dimensions", dimensions_ok, f"requested={wanted_dimensions!r}; actual={actual_dimensions!r}")

    requested_duration = context.get("duration_seconds")
    actual_duration = entry.get("duration")
    duration_ok = not isinstance(requested_duration, (int, float)) or (
        isinstance(actual_duration, (int, float)) and requested_duration <= actual_duration
    )
    add("duration", duration_ok, f"requested={requested_duration!r}; actual={actual_duration!r}")

    requested_fps = context.get("fps")
    actual_fps = entry.get("fps")
    fps_ok = not isinstance(requested_fps, (int, float)) or actual_fps == requested_fps
    add("fps", fps_ok, f"requested={requested_fps!r}; actual={actual_fps!r}")

    conflicts = _avoid_conflicts(entry, context)
    add("avoid", not conflicts, "unknown/no conflict" if not conflicts else "; ".join(conflicts))

    hero_required = context.get("hero_required") is True
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
    _, matched_hero_use, matched_hero_purpose = _semantic_matches(entry, context)
    semantic_hero = (
        routing.get("family") == "emphasis"
        and isinstance(routing.get("purpose"), str) and bool(routing["purpose"].strip())
        and isinstance(routing.get("useWhen"), list) and bool(routing["useWhen"])
        and (not context.get("purpose") or matched_hero_purpose)
        and (not context.get("useWhen") or bool(matched_hero_use))
    )
    add("hero", not hero_required or semantic_hero, "semantic emphasis" if semantic_hero else "not semantic emphasis")

    installable = True
    if entry.get("kind") in {"registry-block", "registry-component"}:
        expected_type = "hyperframes:block" if entry["kind"] == "registry-block" else "hyperframes:component"
        name = source.get("name") or str(entry.get("id", "")).split(":", 1)[-1]
        installable = installable_registry is not None and (str(name), expected_type) in installable_registry
    add("installable", installable, str(source.get("name") or entry.get("id") or "missing"))
    return results


def candidate_audit(
    entry: dict[str, Any], context: dict[str, Any], filters: list[dict[str, Any]], prior_use: dict[str, int],
    *, fallback_trace: list[str] | None = None,
) -> dict[str, Any]:
    family_match, matched_use, purpose_match = _semantic_matches(entry, context)
    exact = family_match and bool(matched_use) and purpose_match
    compatible = family_match or bool(matched_use) or purpose_match
    routing = entry.get("routing") if isinstance(entry.get("routing"), dict) else {}
    supplied_evidence = context.get("expectsEvidence") if isinstance(context.get("expectsEvidence"), dict) else {}
    expects_evidence = [
        {"expectation": str(expectation), "evidence": str(supplied_evidence.get(expectation) or "semantic expectation retained for director review")}
        for expectation in routing.get("expects", []) if isinstance(expectation, str) and expectation
    ]
    source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
    return {
        "id": str(entry["id"]),
        "semanticTier": "exact" if exact else ("compatible" if compatible else "fallback"),
        "matchedFamily": family_match,
        "matchedUseWhen": matched_use,
        "matchedPurpose": purpose_match,
        "avoidConflicts": _avoid_conflicts(entry, context),
        "expectsEvidence": expects_evidence,
        "hardFilterResults": deepcopy(filters),
        "motionPreference": _motion_preference(entry, context),
        "repetitionApplied": prior_use.get(str(entry["id"]), 0) > 0,
        "fallbackTrace": list(fallback_trace or []),
        "source": {
            "catalog": str(context.get("_catalog") or "catalog.json"),
            "catalogRevision": context.get("_catalogRevision"),
            "entry": deepcopy(source),
            "license": deepcopy(entry.get("license") if isinstance(entry.get("license"), dict) else {}),
        },
    }


def candidate_rank(entry: dict[str, Any], context: dict[str, Any], prior_use: dict[str, int]) -> tuple[int, int, int, int, int, str]:
    family_match, matched_use, purpose_match = _semantic_matches(entry, context)
    motion_order = {"preferred": 0, "acceptable": 1, "mismatch": 2}[_motion_preference(entry, context)]
    return (
        0 if family_match else 1,
        0 if matched_use else 1,
        0 if purpose_match else 1,
        motion_order,
        prior_use.get(str(entry.get("id")), 0),
        str(entry.get("id", "")),
    )


def recommend(
    entries: Iterable[dict[str, Any]], context: dict[str, Any], *,
    installable_registry: set[tuple[str, str]] | None = None,
    prior_use: dict[str, int] | None = None,
    forbidden: set[str] | None = None,
) -> dict[str, Any]:
    prior_use, forbidden = prior_use or {}, forbidden or set()
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("id") or entry["id"] in forbidden:
            continue
        filters = evaluate_candidate(entry, context, installable_registry)
        audit = candidate_audit(entry, context, filters, prior_use)
        if all(result["passed"] for result in filters):
            accepted.append({"entry": entry, "audit": audit})
        else:
            rejected.append(audit)
    accepted.sort(key=lambda item: candidate_rank(item["entry"], context, prior_use))
    if not accepted:
        return {"status": "no_recommendation", "selected": None, "candidates": [], "rejections": rejected}
    candidates = [item["audit"] for item in accepted]
    return {"status": "recommended", "selected": candidates[0]["id"], "candidates": candidates, "rejections": rejected}
