from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Iterable


CURATION_SCHEMA_VERSION = "hyperframes-curated-intake/v3"
HANDOFF_SCHEMA_VERSION = "hyperframes-curated-handoff/v3"
SCENE_CONTRACT_SCHEMA_VERSION = "hyperframes-scene-contract/v2"
BUILD_PLAN_SCHEMA_VERSION = "hyperframes-build-plan/v2"
POLICIES = ("approved-first", "approved-only", "open")
REGISTRY_KINDS = {"registry-block", "registry-component"}
MEDIA_KINDS = {"background", "logo", "lottie", "sfx", "svg", "texture"}
SOURCE_RELATIONS = {"preserve", "augment", "replace", "designed"}
COGNITIVE_ACTIONS = {"notice", "explain", "compare", "predict", "apply", "verify", "remember"}
SCENE_ROLES = {"hook", "definition", "comparison", "evidence", "process", "demo", "chapter", "transition", "summary", "close"}
VISUAL_PATTERNS = {
    "object-metaphor", "prop-timeline", "signal-trace", "gauge-comparison", "annotated-object",
    "editorial-type-impact", "screenshot-focus-lens", "spatial-workspace", "icon-constellation", "data-landscape",
}
TEXT_EFFECT_RULES = {
    "typewriter": ("gsap-effects", "discrete-text-sequence"),
    "typewriter-paragraph": ("gsap-effects", "discrete-text-sequence"),
    "text-scramble": ("gsap-effects", "discrete-text-sequence"),
    "scramble-decode": ("gsap-effects", "discrete-text-sequence"),
    "magnetic-pull": ("gsap-effects",),
    "binary-decode": ("gsap-effects", "discrete-text-sequence"),
    "spotlight-reveal": ("gsap-effects",),
    "spiral-in": ("gsap-effects",),
    "ink-bleed": ("gsap-effects",),
    "redacted-reveal": ("gsap-effects",),
    "progress-underline": ("gsap-effects",),
    "word-stagger": ("gsap-effects",),
    "line-reveal": ("gsap-effects",),
    "number-count": ("counting-dynamic-scale",),
}
WINDOW_RE = re.compile(r"^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)s$")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def load_storyboard_spec(path: Path) -> dict[str, Any]:
    value = load_json(path)
    allowed_globals = {"format", "duration", "message", "arc", "audience", "creative_boldness", "timing_policy", "throughline_prop", "transitions", "frames"}
    unknown_globals = sorted(set(value) - allowed_globals)
    if unknown_globals:
        raise ValueError("Storyboard spec contains unknown fields: " + ", ".join(unknown_globals))
    required_globals = ("format", "duration", "message", "arc", "audience", "creative_boldness", "timing_policy", "transitions", "frames")
    missing_globals = [
        field for field in required_globals
        if field not in value or value[field] is None or value[field] == ""
        or (value[field] == [] and field != "transitions")
    ]
    if missing_globals:
        raise ValueError("Storyboard spec is missing: " + ", ".join(missing_globals))
    frames = value.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("Storyboard spec must contain at least one frame")
    if value["creative_boldness"] not in {"restrained", "balanced", "bold"}:
        raise ValueError("Storyboard creative_boldness must be restrained, balanced, or bold")
    timing_policy = value["timing_policy"]
    if not isinstance(timing_policy, dict) or timing_policy.get("mode") not in {"locked", "bounded", "editorial"}:
        raise ValueError("Storyboard timing_policy.mode must be locked, bounded, or editorial")
    unknown_timing = sorted(set(timing_policy) - {"mode", "tolerance_seconds"})
    if unknown_timing:
        raise ValueError("Storyboard timing_policy contains unknown fields: " + ", ".join(unknown_timing))
    if "tolerance_seconds" in timing_policy and (
        not isinstance(timing_policy["tolerance_seconds"], (int, float))
        or isinstance(timing_policy["tolerance_seconds"], bool)
        or timing_policy["tolerance_seconds"] < 0
    ):
        raise ValueError("Storyboard timing_policy.tolerance_seconds must be a non-negative number")
    value["timing_policy"] = timing_policy
    required_frame = (
        "id", "title", "duration", "scene", "source_relation", "animation", "teaching_goal", "teaching_intent",
        "cognitive_action", "scene_role", "evidence_type", "narrative_scale", "visual_intent", "motion_intent",
        "visual_pattern", "density", "hero_visual", "component_budget", "device", "device_candidates",
        "hero", "blueprint", "ambient", "text_plan", "construction", "narrative",
    )
    seen: set[str] = set()
    for index, frame in enumerate(frames, start=1):
        if not isinstance(frame, dict):
            raise ValueError(f"Storyboard frame {index} must be an object")
        allowed_frame = {
            "id", "title", "duration", "scene", "voiceover", "source_relation", "animation",
            "teaching_goal", "teaching_intent", "cognitive_action", "scene_role", "evidence_type", "narrative_scale",
            "visual_intent", "motion_intent", "visual_pattern", "density", "hero_visual",
            "component_budget", "device", "device_candidates", "hero", "blueprint", "beats", "ambient",
            "text_plan", "prop_state", "diversity_exception", "must_preserve", "avoid", "available_inputs",
            "candidate_items", "construction", "integrations", "asset_bindings", "narrative",
        }
        unknown_frame = sorted(set(frame) - allowed_frame)
        if unknown_frame:
            raise ValueError(f"Storyboard frame {index} contains unknown fields: " + ", ".join(unknown_frame))
        missing = [
            field for field in required_frame
            if field not in frame or frame[field] is None or frame[field] == ""
            or (frame[field] == [] and field != "device_candidates")
        ]
        if missing:
            raise ValueError(f"Storyboard frame {index} is missing: " + ", ".join(missing))
        frame_id = str(frame["id"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", frame_id):
            raise ValueError(f"Storyboard frame id must be kebab-case: {frame_id}")
        if frame_id in seen:
            raise ValueError(f"Duplicate storyboard frame id: {frame_id}")
        seen.add(frame_id)
        if frame["source_relation"] not in SOURCE_RELATIONS:
            raise ValueError(f"Unsupported source_relation in {frame_id}: {frame['source_relation']}")
        if frame["animation"] not in {"source-only", "augment", "authored"}:
            raise ValueError(f"Unsupported animation mode in {frame_id}: {frame['animation']}")
        if frame["cognitive_action"] not in COGNITIVE_ACTIONS:
            raise ValueError(f"Unsupported cognitive_action in {frame_id}: {frame['cognitive_action']}")
        if frame["scene_role"] not in SCENE_ROLES:
            raise ValueError(f"Unsupported scene_role in {frame_id}: {frame['scene_role']}")
        if frame["narrative_scale"] not in {"support-beat", "standard-scene", "chapter-peak"}:
            raise ValueError(f"Unsupported narrative_scale in {frame_id}: {frame['narrative_scale']}")
        if frame["visual_pattern"] not in VISUAL_PATTERNS:
            raise ValueError(f"Unsupported visual_pattern in {frame_id}: {frame['visual_pattern']}")
        if frame["density"] not in {"sparse", "comfortable", "dense"}:
            raise ValueError(f"Unsupported density in {frame_id}: {frame['density']}")
        if not isinstance(frame["component_budget"], int) or not 0 <= frame["component_budget"] <= 2:
            raise ValueError(f"Storyboard frame {frame_id} component_budget must be 0 to 2")
        if not isinstance(frame["device"], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", frame["device"]):
            raise ValueError(f"Storyboard frame {frame_id} device must be kebab-case")
        if not isinstance(frame["hero"], bool):
            raise ValueError(f"Storyboard frame {frame_id} hero must be a boolean")
        candidates = frame["device_candidates"]
        if not isinstance(candidates, list) or len(candidates) > 3:
            raise ValueError(f"Storyboard frame {frame_id} device_candidates must contain 0 to 3 items")
        candidate_ids: list[str] = []
        for candidate in candidates:
            if not isinstance(candidate, dict) or set(candidate) != {"id", "role", "responsibility", "rationale"}:
                raise ValueError(
                    f"Storyboard frame {frame_id} device candidate must contain id, role, responsibility, and rationale"
                )
            candidate_id = candidate.get("id")
            rationale = candidate.get("rationale")
            if not isinstance(candidate_id, str) or not candidate_id.startswith(("registry-block:", "registry-component:")):
                raise ValueError(f"Storyboard frame {frame_id} device candidate must be a Registry block or component")
            if not isinstance(rationale, str) or not rationale.strip():
                raise ValueError(f"Storyboard frame {frame_id} device candidate rationale must be non-empty")
            if candidate.get("role") not in {"hero", "support"}:
                raise ValueError(f"Storyboard frame {frame_id} device candidate role must be hero or support")
            if not isinstance(candidate.get("responsibility"), str) or not candidate["responsibility"].strip():
                raise ValueError(f"Storyboard frame {frame_id} device candidate responsibility must be non-empty")
            candidate_ids.append(candidate_id)
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError(f"Storyboard frame {frame_id} device_candidates contains duplicate IDs")
        construction = frame["construction"]
        if not isinstance(construction, dict):
            raise ValueError(f"Storyboard frame {frame_id} construction must be an object")
        expected_construction = {"composition", "focal_hierarchy", "layers"}
        if not expected_construction.issubset(construction):
            raise ValueError(
                f"Storyboard frame {frame_id} construction is missing: "
                + ", ".join(sorted(expected_construction - set(construction)))
            )
        if not all(isinstance(construction[field], str) and construction[field].strip() for field in ("composition", "focal_hierarchy")):
            raise ValueError(f"Storyboard frame {frame_id} construction needs composition and focal_hierarchy")
        layers = construction["layers"]
        if not isinstance(layers, list) or not layers:
            raise ValueError(f"Storyboard frame {frame_id} construction.layers must contain at least one layer")
        layer_ids: set[str] = set()
        for layer in layers:
            required_layer = {"id", "role", "content", "slot", "z_index"}
            if not isinstance(layer, dict) or not required_layer.issubset(layer):
                raise ValueError(f"Storyboard frame {frame_id} construction layer needs id, role, content, slot, and z_index")
            layer_id = str(layer["id"])
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", layer_id) or layer_id in layer_ids:
                raise ValueError(f"Storyboard frame {frame_id} construction layer ids must be unique kebab-case values")
            layer_ids.add(layer_id)
            if not isinstance(layer["z_index"], int):
                raise ValueError(f"Storyboard frame {frame_id} construction layer {layer_id} z_index must be an integer")
        integrations = frame.get("integrations", [])
        if not isinstance(integrations, list):
            raise ValueError(f"Storyboard frame {frame_id} integrations must be an array")
        integration_ids: set[str] = set()
        for integration in integrations:
            required_integration = {"id", "selection", "role", "responsibility", "slot", "target"}
            if not isinstance(integration, dict) or not required_integration.issubset(integration):
                raise ValueError(
                    f"Storyboard frame {frame_id} integration needs id, selection, role, responsibility, slot, and target"
                )
            integration_id = str(integration["id"])
            if not integration_id.startswith(("registry-block:", "registry-component:")):
                raise ValueError(f"Storyboard frame {frame_id} integration must reference a Registry block or component")
            if integration_id in integration_ids:
                raise ValueError(f"Storyboard frame {frame_id} repeats integration {integration_id}")
            integration_ids.add(integration_id)
            if integration["selection"] not in {"required", "preferred"}:
                raise ValueError(f"Storyboard frame {frame_id} integration selection must be required or preferred")
            if integration["role"] not in {"hero", "support"}:
                raise ValueError(f"Storyboard frame {frame_id} integration role must be hero or support")
        asset_bindings = frame.get("asset_bindings", [])
        if not isinstance(asset_bindings, list):
            raise ValueError(f"Storyboard frame {frame_id} asset_bindings must be an array")
        for binding in asset_bindings:
            required_binding = {"id", "role", "target"}
            if not isinstance(binding, dict) or not required_binding.issubset(binding):
                raise ValueError(f"Storyboard frame {frame_id} asset binding needs id, role, and target")
        if "diversity_exception" in frame and (
            not isinstance(frame["diversity_exception"], str) or not frame["diversity_exception"].strip()
        ):
            raise ValueError(f"Storyboard frame {frame_id} diversity_exception must be non-empty")
        hero_visual = frame["hero_visual"]
        if not isinstance(hero_visual, dict) or set(hero_visual) != {"subject", "medium", "source", "final_state"}:
            raise ValueError(f"Storyboard frame {frame_id} hero_visual must contain subject, medium, source, and final_state")
        if hero_visual.get("medium") == "component":
            component_id = str(hero_visual.get("source", "")).removeprefix("component:")
            expected = f"registry-component:{component_id}"
            matching = [candidate for candidate in candidates if candidate["id"] == expected and candidate["role"] == "hero"]
            if not matching or frame["component_budget"] < 1:
                raise ValueError(
                    f"Storyboard frame {frame_id} component Hero requires a matching hero candidate and component_budget >= 1"
                )
        for field in ("must_preserve", "avoid", "available_inputs", "candidate_items"):
            if field in frame and (not isinstance(frame[field], list) or not all(isinstance(item, str) and item.strip() for item in frame[field])):
                raise ValueError(f"Storyboard frame {frame_id} field {field} must be a list of non-empty strings")
            if field in frame and len(frame[field]) != len(set(frame[field])):
                raise ValueError(f"Storyboard frame {frame_id} field {field} contains duplicates")
        for field in ("voiceover",):
            if field in frame and (not isinstance(frame[field], str) or not frame[field].strip()):
                raise ValueError(f"Storyboard frame {frame_id} field {field} must be a non-empty string")
        validate_frame_expression(frame)
    transitions = value.get("transitions")
    if not isinstance(transitions, list):
        raise ValueError("Storyboard transitions must be an array")
    expected_boundaries = list(zip(frames, frames[1:]))
    if len(transitions) != len(expected_boundaries):
        raise ValueError(
            f"Storyboard with {len(frames)} frames requires exactly {len(expected_boundaries)} transition contracts"
        )
    boundary_ids: set[str] = set()
    for index, (transition, (outgoing, incoming)) in enumerate(zip(transitions, expected_boundaries), start=1):
        required_transition = {
            "boundary_id", "from_scene", "to_scene", "catalog_id", "catalog_kind", "selection",
            "role", "implementation", "duration_seconds", "purpose", "continuity", "same_background",
            "perceptual_anchor", "color_dependency",
        }
        if not isinstance(transition, dict) or set(transition) != required_transition:
            raise ValueError(
                f"Transition {index} must contain exactly: " + ", ".join(sorted(required_transition))
            )
        boundary_id = str(transition["boundary_id"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", boundary_id) or boundary_id in boundary_ids:
            raise ValueError("Transition boundary_id values must be unique kebab-case identifiers")
        boundary_ids.add(boundary_id)
        expected_from = str(outgoing["id"])
        expected_to = str(incoming["id"])
        if transition["from_scene"] != expected_from or transition["to_scene"] != expected_to:
            raise ValueError(
                f"Transition {boundary_id} must connect adjacent frames {expected_from} → {expected_to}"
            )
        catalog_id = str(transition["catalog_id"])
        catalog_kind = str(transition["catalog_kind"])
        prefix_by_kind = {
            "registry-block": "registry-block:",
            "transition": "transition:",
            "motion-rule": "motion-rule:",
        }
        if catalog_kind not in prefix_by_kind or not catalog_id.startswith(prefix_by_kind[catalog_kind]):
            raise ValueError(f"Transition {boundary_id} catalog_id and catalog_kind must agree")
        if transition["selection"] != "required":
            raise ValueError(f"Transition {boundary_id} is a required scene-boundary integration")
        if transition["role"] not in {"primary", "accent"}:
            raise ValueError(f"Transition {boundary_id} role must be primary or accent")
        if transition["implementation"] not in {"shader-runtime", "css-gsap", "subcomposition"}:
            raise ValueError(f"Transition {boundary_id} has an unsupported implementation")
        duration = transition["duration_seconds"]
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or not 0.1 <= duration <= 1.5:
            raise ValueError(f"Transition {boundary_id} duration_seconds must be between 0.1 and 1.5")
        for field in ("purpose", "continuity"):
            if not isinstance(transition[field], str) or not transition[field].strip():
                raise ValueError(f"Transition {boundary_id} {field} must be non-empty")
        if not isinstance(transition["same_background"], bool):
            raise ValueError(f"Transition {boundary_id} same_background must be a boolean")
        if transition["perceptual_anchor"] not in {
            "luminance-seam", "focus-plane", "depth-occlusion", "shared-object", "directional-motion",
            "texture-field", "hard-cut",
        }:
            raise ValueError(f"Transition {boundary_id} has an unsupported perceptual_anchor")
        if transition["color_dependency"] not in {"independent", "supporting", "required"}:
            raise ValueError(f"Transition {boundary_id} has an unsupported color_dependency")
        if transition["same_background"] and transition["color_dependency"] != "independent":
            raise ValueError(
                f"Transition {boundary_id} joins same-background scenes and must be color-independent"
            )
    hero_frames = [frame for frame in frames if frame["hero"]]
    minimum_heroes = 2 if len(frames) >= 6 else 1
    if not minimum_heroes <= len(hero_frames) <= 3:
        raise ValueError(f"Storyboard must contain {minimum_heroes} to 3 hero frames")
    timing_contract(value)
    return value


def parse_seconds(value: str) -> float:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)s", str(value).strip())
    if not match:
        raise ValueError(f"Duration must use seconds, for example 8s: {value}")
    return float(match.group(1))


def parse_window(value: str) -> tuple[float, float]:
    match = WINDOW_RE.fullmatch(str(value).strip())
    if not match:
        raise ValueError(f"Beat window must use start-ends syntax: {value}")
    return float(match.group(1)), float(match.group(2))


def frame_rule_ids(frame: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for beat in frame.get("beats", []):
        values.extend(str(value) for value in beat.get("rule_ids", []))
    text_plan = frame.get("text_plan", {})
    for cue in text_plan.get("cues", []):
        values.extend(TEXT_EFFECT_RULES.get(str(cue.get("effect")), ()))
        if cue.get("emphasis_rule"):
            values.append(str(cue["emphasis_rule"]))
    return unique(values)


def validate_frame_expression(frame: dict[str, Any], *, require_windows: bool = False) -> None:
    frame_id = str(frame["id"])
    duration = parse_seconds(str(frame["duration"]))
    beats = frame.get("beats", [])
    if frame["animation"] == "source-only" and not beats:
        beats = []
    elif not isinstance(beats, list):
        raise ValueError(f"Storyboard frame {frame_id} beats must be an array")
    else:
        reveals = [beat for beat in beats if beat.get("kind") == "reveal"]
        holds = [beat for beat in beats if beat.get("kind") == "hold"]
        minimum_reveals = 5 if duration > 30 else 3 if duration > 15 else 2
        if len(reveals) < minimum_reveals:
            raise ValueError(f"Storyboard frame {frame_id} requires at least {minimum_reveals} reveal beats")
        if len(holds) != 1 or beats[-1].get("kind") != "hold":
            raise ValueError(f"Storyboard frame {frame_id} requires exactly one final hold beat")
        beat_ids: set[str] = set()
        for beat in beats:
            if not isinstance(beat, dict):
                raise ValueError(f"Storyboard frame {frame_id} beat must be an object")
            required = {"id", "kind", "narration", "reveal", "target_role", "rule_ids", "purpose"}
            if not required.issubset(beat):
                raise ValueError(f"Storyboard frame {frame_id} beat is missing: " + ", ".join(sorted(required - set(beat))))
            if beat["id"] in beat_ids:
                raise ValueError(f"Storyboard frame {frame_id} repeats beat id {beat['id']}")
            beat_ids.add(str(beat["id"]))
            if require_windows and not beat.get("window"):
                raise ValueError(f"Storyboard frame {frame_id} beat {beat['id']} has no allocated window")
        if require_windows:
            windows = [parse_window(str(beat["window"])) for beat in beats]
            tolerance = 0.011
            if abs(windows[0][0]) > tolerance:
                raise ValueError(f"Storyboard frame {frame_id} beat windows must start at 0s")
            for previous, current in zip(windows, windows[1:]):
                if abs(previous[1] - current[0]) > tolerance:
                    raise ValueError(f"Storyboard frame {frame_id} beat windows must be continuous")
            if abs(windows[-1][1] - duration) > tolerance:
                raise ValueError(f"Storyboard frame {frame_id} beat windows must end at {duration:g}s")
            if any(end <= start for start, end in windows):
                raise ValueError(f"Storyboard frame {frame_id} beat windows must have positive duration")
            last_reveal_index = max(index for index, beat in enumerate(beats) if beat["kind"] == "reveal")
            if windows[last_reveal_index][0] < duration * 0.60:
                raise ValueError(f"Storyboard frame {frame_id} final reveal must start at or after 60% of the frame")
            hold_start, hold_end = windows[-1]
            if hold_end - hold_start < duration * 0.10 - tolerance:
                raise ValueError(f"Storyboard frame {frame_id} final hold must occupy at least 10% of the frame")
    ambient = frame.get("ambient")
    if not isinstance(ambient, dict) or ambient.get("mode") not in {"active", "none"}:
        raise ValueError(f"Storyboard frame {frame_id} ambient must declare active or none")
    if ambient["mode"] == "active":
        if not all(isinstance(ambient.get(field), str) and ambient[field].strip() for field in ("target_role", "motion", "purpose")):
            raise ValueError(f"Storyboard frame {frame_id} active ambient needs target_role, motion, and purpose")
    elif not isinstance(ambient.get("reason"), str) or not ambient["reason"].strip():
        raise ValueError(f"Storyboard frame {frame_id} ambient none needs an intentional-stillness reason")
    text_plan = frame.get("text_plan")
    if not isinstance(text_plan, dict) or text_plan.get("mode") not in {"animated", "static-readable", "no-visible-text"}:
        raise ValueError(f"Storyboard frame {frame_id} text_plan must declare animated, static-readable, or no-visible-text")
    cues = text_plan.get("cues")
    if not isinstance(cues, list):
        raise ValueError(f"Storyboard frame {frame_id} text_plan cues must be an array")
    if text_plan["mode"] == "animated" and not cues:
        raise ValueError(f"Storyboard frame {frame_id} animated text_plan needs at least one cue")
    if text_plan["mode"] != "animated" and (cues or not str(text_plan.get("reason", "")).strip()):
        raise ValueError(f"Storyboard frame {frame_id} non-animated text_plan needs no cues and an explicit reason")
    beat_ids = {str(beat.get("id")) for beat in beats}
    cue_ids: set[str] = set()
    for cue in cues:
        if cue.get("id") in cue_ids:
            raise ValueError(f"Storyboard frame {frame_id} repeats text cue id {cue.get('id')}")
        cue_ids.add(str(cue.get("id")))
        if cue.get("beat_id") not in beat_ids:
            raise ValueError(f"Storyboard frame {frame_id} text cue {cue.get('id')} references an unknown beat")
        if cue.get("effect") not in TEXT_EFFECT_RULES:
            raise ValueError(f"Storyboard frame {frame_id} text cue {cue.get('id')} has an unsupported effect")


def validate_beat_contract(spec: dict[str, Any], *, require_windows: bool = True) -> None:
    for frame in spec["frames"]:
        validate_frame_expression(frame, require_windows=require_windows)
    timing_contract(spec)


def timing_contract(spec: dict[str, Any]) -> dict[str, Any]:
    target = parse_seconds(str(spec["duration"]))
    policy = spec.get("timing_policy") or {"mode": "bounded"}
    mode = str(policy.get("mode", "bounded"))
    default_tolerance = 0.0 if mode == "locked" else max(0.5, target * 0.05)
    tolerance = float(policy.get("tolerance_seconds", default_tolerance))
    cursor = 0.0
    frames: list[dict[str, Any]] = []
    for frame in spec["frames"]:
        duration = parse_seconds(str(frame["duration"]))
        frames.append({
            "id": str(frame["id"]),
            "start": round(cursor, 3),
            "end": round(cursor + duration, 3),
            "duration": round(duration, 3),
        })
        cursor += duration
    drift = abs(cursor - target)
    if mode in {"locked", "bounded"} and drift > tolerance + 0.001:
        raise ValueError(
            f"Storyboard frame durations total {cursor:g}s but global duration is {target:g}s; "
            f"{mode} timing allows {tolerance:g}s drift"
        )
    return {
        "mode": mode,
        "toleranceSeconds": round(tolerance, 3),
        "targetDurationSeconds": round(target, 3),
        "plannedDurationSeconds": round(cursor, 3),
        "driftSeconds": round(cursor - target, 3),
        "frames": frames,
    }


def storyboard_scene_text(frame: dict[str, Any]) -> str:
    fields = (
        frame.get("title", ""),
        frame.get("scene", ""),
        frame.get("teaching_goal", ""),
        frame.get("teaching_intent", ""),
        frame.get("cognitive_action", ""),
        frame.get("scene_role", ""),
        frame.get("evidence_type", ""),
        frame.get("visual_intent", ""),
        frame.get("motion_intent", ""),
        frame.get("visual_pattern", ""),
        " ".join(str(value) for value in frame.get("hero_visual", {}).values()),
        frame.get("device", ""),
        frame.get("construction", {}).get("composition", ""),
        frame.get("construction", {}).get("focal_hierarchy", ""),
        " ".join(
            f"{layer.get('role', '')} {layer.get('content', '')} {layer.get('slot', '')}"
            for layer in frame.get("construction", {}).get("layers", [])
            if isinstance(layer, dict)
        ),
        " ".join(
            f"{item.get('id', '')} {item.get('role', '')} {item.get('responsibility', '')} {item.get('slot', '')}"
            for item in frame.get("integrations", [])
            if isinstance(item, dict)
        ),
        " ".join(
            f"{candidate.get('id', '')} {candidate.get('role', '')} {candidate.get('responsibility', '')} {candidate.get('rationale', '')}"
            for candidate in frame.get("device_candidates", [])
            if isinstance(candidate, dict)
        ),
        " ".join(
            f"{beat.get('reveal', '')} {beat.get('purpose', '')} {' '.join(beat.get('rule_ids', []))}"
            for beat in frame.get("beats", [])
            if isinstance(beat, dict)
        ),
        " ".join(
            f"{cue.get('text_shape', '')} {cue.get('effect', '')} {cue.get('purpose', '')}"
            for cue in frame.get("text_plan", {}).get("cues", [])
            if isinstance(cue, dict)
        ),
        " ".join(
            f"{binding.get('id', '')} {binding.get('role', '')} {binding.get('target', '')}"
            for binding in frame.get("asset_bindings", [])
            if isinstance(binding, dict)
        ),
        frame.get("narrative", ""),
        " ".join(frame.get("must_preserve", [])),
        " ".join(frame.get("avoid", [])),
    )
    return " ".join(str(value) for value in fields if value)


def validate_device_diversity(spec: dict[str, Any]) -> None:
    frames = spec["frames"]
    for previous, current in zip(frames, frames[1:]):
        if previous["device"] == current["device"] and not current.get("diversity_exception"):
            raise ValueError(
                f"Adjacent frames {previous['id']} and {current['id']} repeat device "
                f"{current['device']} without diversity_exception"
            )
    by_device: dict[str, list[dict[str, Any]]] = {}
    for frame in frames:
        by_device.setdefault(str(frame["device"]), []).append(frame)
    for device, occurrences in by_device.items():
        if len(occurrences) > 3:
            unapproved = [frame["id"] for frame in occurrences[3:] if not frame.get("diversity_exception")]
            if unapproved:
                raise ValueError(
                    f"Device {device} appears more than 3 times without diversity_exception on: "
                    + ", ".join(unapproved)
                )
    hero_devices: set[str] = set()
    for frame in frames:
        if not frame["hero"]:
            continue
        device = str(frame["device"])
        if device in hero_devices and not frame.get("diversity_exception"):
            raise ValueError(f"Hero frame {frame['id']} repeats hero device {device} without diversity_exception")
        hero_devices.add(device)
        reused_by_regular = any(other["device"] == device and not other["hero"] for other in frames)
        if reused_by_regular and not frame.get("diversity_exception"):
            raise ValueError(
                f"Hero frame {frame['id']} must use a distinctive device or declare diversity_exception"
            )


def one_line(value: Any) -> str:
    return " ".join(str(value).split())


def render_storyboard(spec: dict[str, Any]) -> str:
    timing = timing_contract(spec)
    timing_by_id = {item["id"]: item for item in timing["frames"]}
    lines = [
        "---",
        f"format: {yaml_scalar(str(spec['format']))}",
        f"duration: {yaml_scalar(str(spec['duration']))}",
        f"message: {yaml_scalar(str(spec['message']))}",
        f"arc: {yaml_scalar(str(spec['arc']))}",
        f"audience: {yaml_scalar(str(spec['audience']))}",
        f"creative_boldness: {yaml_scalar(str(spec['creative_boldness']))}",
        f"timing_mode: {timing['mode']}",
        f"timing_tolerance_seconds: {timing['toleranceSeconds']:g}",
        "outline_approval: user-approved",
        "intake_handoff: HANDOFF.md",
        "mode: collaborative",
        "---",
        "",
    ]
    if spec.get("throughline_prop"):
        lines.extend([
            "## Through-line",
            "",
            f"- prop: {spec['throughline_prop']['id']}",
            f"- identity: {one_line(spec['throughline_prop']['identity'])}",
            "",
        ])
    if spec["transitions"]:
        lines.extend(["## Transition plan", ""])
        for transition in spec["transitions"]:
            lines.append(
                f"- {transition['boundary_id']}: `{transition['from_scene']}` → `{transition['to_scene']}`; "
                f"catalog={transition['catalog_id']}; role={transition['role']}; "
                f"implementation={transition['implementation']}; duration={transition['duration_seconds']:g}s; "
                f"same_background={'true' if transition['same_background'] else 'false'}; "
                f"anchor={transition['perceptual_anchor']}; color_dependency={transition['color_dependency']}; "
                f"purpose={one_line(transition['purpose'])}; continuity={one_line(transition['continuity'])}"
            )
        lines.append("")
    incoming_by_scene = {transition["to_scene"]: transition for transition in spec["transitions"]}
    for index, frame in enumerate(spec["frames"], start=1):
        frame_id = str(frame["id"])
        lines.extend([
            f"## Frame {index} — {one_line(frame['title'])}",
            "",
            f"- id: {frame_id}",
            "- status: outline",
            f"- src: compositions/frames/{frame_id}.html",
            f"- scene_contract: scene-contracts/{frame_id}.json",
            f"- duration: {one_line(frame['duration'])}",
            f"- timeline_window: {timing_by_id[frame_id]['start']:g}-{timing_by_id[frame_id]['end']:g}s",
        ])
        incoming = incoming_by_scene.get(frame_id)
        lines.append(f"- transition_in: {incoming['boundary_id'] if incoming else 'opening'}")
        lines.extend([
            f"- scene: {one_line(frame['scene'])}",
            f"- source_relation: {frame['source_relation']}",
            f"- animation: {frame['animation']}",
            f"- teaching_goal: {one_line(frame['teaching_goal'])}",
            f"- teaching_intent: {frame['teaching_intent']}",
            f"- cognitive_action: {frame['cognitive_action']}",
            f"- scene_role: {frame['scene_role']}",
            f"- evidence_type: {frame['evidence_type']}",
            f"- narrative_scale: {frame['narrative_scale']}",
            f"- visual_pattern: {frame['visual_pattern']}",
            f"- density: {frame['density']}",
            f"- hero_visual: {one_line(frame['hero_visual']['subject'])}",
            f"- hero_medium: {frame['hero_visual']['medium']}",
            f"- hero_source: {one_line(frame['hero_visual']['source'])}",
            f"- hero_final_state: {one_line(frame['hero_visual']['final_state'])}",
            f"- component_budget: {frame['component_budget']}",
            f"- motion_intent: {one_line(frame['motion_intent'])}",
            f"- device: {frame['device']}",
            f"- hero: {'true' if frame['hero'] else 'false'}",
            f"- blueprint: {frame['blueprint'] if frame['blueprint'] == 'compose' else frame['blueprint'] + ' (Adapt)'}",
        ])
        rules = frame_rule_ids(frame)
        if rules:
            lines.append("- rules: " + ", ".join(rules))
        ambient = frame["ambient"]
        if ambient["mode"] == "active":
            lines.append(
                f"- ambient: {one_line(ambient['target_role'])} — {one_line(ambient['motion'])}; purpose={one_line(ambient['purpose'])}"
            )
        else:
            lines.append(f"- ambient: none; reason={one_line(ambient['reason'])}")
        text_plan = frame["text_plan"]
        lines.append(f"- text_mode: {text_plan['mode']}")
        if text_plan.get("reason"):
            lines.append(f"- text_reason: {one_line(text_plan['reason'])}")
        if frame.get("prop_state"):
            lines.append(f"- prop_state: {one_line(frame['prop_state'])}")
        if frame.get("diversity_exception"):
            lines.append(f"- diversity_exception: {one_line(frame['diversity_exception'])}")
        if frame.get("voiceover"):
            lines.append(f"- voiceover: {one_line(frame['voiceover'])}")
        if frame.get("candidate_items"):
            lines.append("- candidate_items: " + ", ".join(frame["candidate_items"]))
        if frame["device_candidates"]:
            lines.append("- device_candidates:")
            for candidate in frame["device_candidates"]:
                lines.append(
                    f"  - {candidate['id']} — role={candidate['role']}; responsibility={one_line(candidate['responsibility'])}; "
                    f"rationale={one_line(candidate['rationale'])}"
                )
        if frame.get("integrations"):
            lines.append("- directed_integrations:")
            for item in frame["integrations"]:
                lines.append(
                    f"  - {item['id']} — selection={item['selection']}; role={item['role']}; "
                    f"slot={one_line(item['slot'])}; target={one_line(item['target'])}; "
                    f"responsibility={one_line(item['responsibility'])}"
                )
        if frame.get("beats"):
            lines.append("")
            for beat_index, beat in enumerate(frame["beats"], start=1):
                rules_text = ", ".join(beat["rule_ids"]) or "none"
                lines.append(
                    f"Scene {beat_index} ({beat['window']}): [{beat['id']}; {beat['target_role']}; {beat['kind']}] "
                    f"{one_line(beat['reveal'])} — rules={rules_text}; purpose={one_line(beat['purpose'])}"
                )
            if text_plan["mode"] == "animated":
                lines.append("")
                beat_windows = {beat["id"]: beat["window"] for beat in frame["beats"]}
                for cue_index, cue in enumerate(text_plan["cues"], start=1):
                    emphasis = f"; emphasis={cue['emphasis_rule']}" if cue.get("emphasis_rule") else ""
                    lines.append(
                        f"Text {cue_index} ({beat_windows[cue['beat_id']]}): [{cue['id']}; {cue['text_shape']}] "
                        f"effect={cue['effect']}{emphasis}; purpose={one_line(cue['purpose'])}"
                    )
        lines.extend(["", f"**Visual intent:** {one_line(frame['visual_intent'])}", ""])
        if frame.get("must_preserve"):
            lines.extend(["**Must preserve:**", *[f"- {item}" for item in frame["must_preserve"]], ""])
        if frame.get("avoid"):
            lines.extend(["**Avoid:**", *[f"- {item}" for item in frame["avoid"]], ""])
        lines.extend([str(frame["narrative"]).strip(), ""])
    return "\n".join(lines).rstrip() + "\n"


def build_scene_contract(
    frame: dict[str, Any], timeline: dict[str, Any], incoming_transition: dict[str, Any] | None
) -> dict[str, Any]:
    frame_id = str(frame["id"])
    return {
        "schemaVersion": SCENE_CONTRACT_SCHEMA_VERSION,
        "sceneId": frame_id,
        "compositionSrc": f"compositions/frames/{frame_id}.html",
        "motionSidecar": f"compositions/frames/{frame_id}.motion.json",
        "status": "approved",
        "sourceRelation": frame["source_relation"],
        "animation": frame["animation"],
        "timeline": timeline,
        "purpose": frame["teaching_goal"],
        "classification": {
            "teachingIntent": frame["teaching_intent"],
            "cognitiveAction": frame["cognitive_action"],
            "sceneRole": frame["scene_role"],
            "evidenceType": frame["evidence_type"],
            "density": frame["density"],
            "narrativeScale": frame["narrative_scale"],
            "visualPattern": frame["visual_pattern"],
        },
        "visualIntent": frame["visual_intent"],
        "motionIntent": frame["motion_intent"],
        "hero": frame["hero_visual"],
        "construction": frame["construction"],
        "beats": frame.get("beats", []),
        "textPlan": frame["text_plan"],
        "ambient": frame["ambient"],
        "incomingTransition": incoming_transition,
        "assetBindings": frame.get("asset_bindings", []),
        "integrations": frame.get("integrations", []),
        "candidateIntegrations": frame.get("device_candidates", []),
        "mustPreserve": frame.get("must_preserve", []),
        "qualityTargets": {
            "heroSelectorRequired": True,
            "beatSelectorsRequired": bool(frame.get("beats")),
            "textSelectorsRequired": frame["text_plan"]["mode"] == "animated",
            "ambientSelectorRequired": frame["ambient"]["mode"] == "active",
            "transitionEvidenceRequired": incoming_transition is not None,
            "verificationTargets": "visible production elements",
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def ensure_within(root: Path, path: Path) -> Path:
    root = root.resolve()
    path = path.resolve()
    if path != root and root not in path.parents:
        raise ValueError(f"Path escapes allowed root {root}: {path}")
    return path


def entry_source_paths(library: Path, entry: dict[str, Any]) -> list[tuple[Path, str, str | None]]:
    source = entry.get("source", {})
    files = source.get("files")
    if isinstance(files, list):
        result = []
        for item in files:
            if not isinstance(item, dict) or not item.get("path"):
                continue
            result.append(
                (
                    ensure_within(library, library / str(item["path"])),
                    str(item.get("target") or Path(str(item["path"])).name),
                    item.get("sha256"),
                )
            )
        return result
    if source.get("path"):
        source_path = ensure_within(library, library / str(source["path"]))
        return [(source_path, source_path.name, entry.get("sha256"))]
    return []


def catalog_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(entry["id"]): entry for entry in catalog.get("entries", []) if isinstance(entry, dict) and entry.get("id")}


def tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 1}


def entry_text(entry: dict[str, Any]) -> str:
    fields: list[str] = [str(entry.get("id", "")), str(entry.get("title", "")), str(entry.get("description", ""))]
    fields.extend(str(value) for value in entry.get("tags", []))
    fields.extend(str(value) for value in entry.get("capabilities", []))
    routing = entry.get("routing", {})
    if isinstance(routing, dict):
        fields.append(str(routing.get("family", "")))
        fields.append(str(routing.get("avoid", "")))
        for key in ("teachingIntents", "cognitiveActions", "sceneRoles", "evidenceTypes", "styleFit", "aspectFit", "densityFit"):
            fields.extend(str(value) for value in routing.get(key, []))
    return " ".join(fields)


def source_target_for_asset(entry: dict[str, Any], source: Path) -> Path:
    kind = str(entry.get("kind", "asset"))
    entry_id = str(entry.get("id", source.stem)).replace(":", "-")
    return Path("assets") / "library" / kind / f"{entry_id}{source.suffix.lower()}"


def copy_verified(source: Path, target: Path, expected_sha256: str | None) -> str:
    if not source.is_file():
        raise FileNotFoundError(source)
    actual = sha256(source)
    if expected_sha256 and actual != expected_sha256:
        raise ValueError(f"Hash mismatch for {source}: expected {expected_sha256}, got {actual}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    copied = sha256(target)
    if copied != actual:
        raise ValueError(f"Copy verification failed for {target}")
    return copied


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
