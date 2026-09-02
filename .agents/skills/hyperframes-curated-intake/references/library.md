# Curated library

`library/director-catalog.json` is the shared discovery catalog when present; fall back to `library/catalog.json` for existing projects. `library/registry/` is the deterministic HyperFrames-compatible projection for Registry Blocks and Components.

## Intake use

1. Inventory the catalog and verify source hashes, readiness, previews, and integration metadata.
2. Resolve the user-confirmed Frame from `library/frames/<preset>/FRAME.md` and copy it to the project as `frame.md`.
3. Consume generic complete Blocks, Layers, transitions, source hashes, previews, and installability from the shared catalog. Curated Intake owns only the bounded teaching set: teaching Components, charts, teaching motion rules, SFX, and blueprints. The skill's approved storyboard owns the teaching recommendation; code does not infer a creative winner.
4. Query the current HyperFrames Registry for transition Blocks, then reconcile exact IDs with the local catalog projection before selection.
5. Bind exact required/preferred scene integrations and one required transition for every adjacent scene boundary; keep optional discovery choices in the candidate palette.
6. Adopt required media into project-local paths with hashes.

Logos, SVGs, Lottie, audio, fonts, images, and video remain media assets. Registry Blocks and Components use the official Registry projection.

## Selection priorities

The skill selects by semantic responsibility, evidence form, Frame fit, and whole-film variety. Code filters only hard compatibility facts: readiness, installability, documented integration, required inputs, aspect, duration, density, Hero eligibility, policy, and render-time network use. Candidate quantity is informational; the quality gate begins when an item is approved for Build.

For teaching scenes, follow [teaching-visual-direction.md](teaching-visual-direction.md), including the Mav Charts relationship map and same-background transition rules.

The standard policy is `approved-first`:

- exact directed integrations receive first consideration;
- compatible palette candidates form the next lane;
- a complete catalog miss supports a custom implementation later;
- `required` integrations remain scene gates.

`approved-only` uses the approved palette as an allowlist. `open` allows broader sourcing while preserving provenance.

## Preferred transition set

The current official Registry exposes all seven preferences as shader-transition Blocks:

- `registry-block:cross-warp-morph`
- `registry-block:domain-warp-dissolve`
- `registry-block:glitch`
- `registry-block:gravitational-lens`
- `registry-block:ridged-burn`
- `registry-block:ripple-waves`
- `registry-block:swirl-vortex`

Use the exact Registry ID. A local projection may contain only a subset, so confirm both the current official catalog and local installability. A transition enters the approved packet when its exact catalog source and later installation path are resolved.

## Registry administration

Run `inventory-library.py` before rebuilding the Registry view. `build-registry-view.py` maps ready Registry Blocks and Components and emits a deterministic report. Publishing or uploading the generated Registry is a separate user-authorized action.

WeChat, ChatGPT, Film Credits, generic camera/focus/caption/environment Layers, and generic transition administration are not Curated-owned recommendations. Routed requests may inherit them as fixed context.
