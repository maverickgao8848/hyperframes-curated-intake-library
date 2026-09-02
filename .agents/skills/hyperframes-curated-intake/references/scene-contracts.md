# Scene contracts

Create one `scene-contracts/<scene-id>.json` for every Storyboard scene. The contract gives a later HyperFrames worker enough information to reproduce the approved idea without inventing a parallel interpretation.

## Construction

Every contract names:

- `classification`: teaching intent, cognitive action, scene role, evidence form, density, narrative scale, and visual pattern;
- `composition`: the spatial idea in one concrete paragraph;
- `focal_hierarchy`: the viewer's intended attention order;
- `layers`: stable layer IDs with role, visible content, slot, and integer z-index;
- `hero`: subject, medium, source, and final readable state;
- `assetBindings`: real media IDs, roles, targets, and project paths when known;
- `integrations`: exact Registry items that are `required` or `preferred`;
- `incomingTransition`: the exact boundary contract entering this scene, or `null` for the opening scene;
- `candidateIntegrations`: optional discovery alternatives;
- `beats`, `textPlan`, `ambient`, and `motionIntent`;
- `qualityTargets`: selectors and receipts the later Build will provide.

Use spatial language that translates to a layout: center core, upper-third editorial statement, left evidence rail, lower-right logo constellation, full-bleed background, foreground transition mask. Exact pixel coordinates are useful only when the user locks them.

## Directed integrations

Each integration includes:

- catalog ID and inferred kind;
- `selection`: `required` or `preferred`;
- Hero/support role;
- one named responsibility;
- layout slot and visible target;
- props when the catalog exposes them;
- expected integration method from the catalog.

`required` means the later Build completes the real integration for this scene. A compatibility, installation, or runtime blocker pauses that scene and reports the concrete cause. `preferred` enters the Build Plan when it remains the best semantic fit after staging inspection.

Blocks integrate as real sub-compositions. Components contribute their staged HTML/CSS/JavaScript and timeline behavior to a visible production element. Data labels and usage declarations describe the integration; the staged implementation and runtime evidence establish it.

## Adjacent-scene transitions

The Storyboard owns one transition contract per adjacent scene pair. Each contract includes a stable boundary ID, exact outgoing and incoming scene IDs, catalog ID and kind, required selection state, primary/accent role, implementation mode, duration, narrative purpose, continuity description, same-background assessment, perceptual anchor, and color dependency.

When `same_background` is true, `color_dependency` must be `independent`. Prefer `edge-lit-wipe`, `focus-pull`, `depth-swap`, a verified shared morph, directional push, or a hard cut according to the boundary's semantic relationship.

Shader-transition Blocks are staged as real Registry sources and integrated through their shader/runtime behavior at the declared boundary. The later Build records one production controller selector plus the catalog ID, both scene IDs, and implementation mode in `.hyperframes/usage.json`. Boundary verification samples the outgoing side, transition midpoint, and incoming side.

The preferred verified shader Blocks are `cross-warp-morph`, `domain-warp-dissolve`, `glitch`, `gravitational-lens`, `ridged-burn`, `ripple-waves`, and `swirl-vortex`. The Frame and narrative relationship choose the primary and accents.

## Text and reading motion

Animated scenes maintain visual activity during reading. Choose a text effect that supports the content shape, bind it to a beat, and retain a readable final state. Long prose favors Typewriter Paragraph or progressive line treatment. Headlines and quotations may use a stronger scramble, decode, spotlight, spiral, ink, redaction, or underline treatment when the approved library supports it.

## Evidence targets

Every beat, text cue, active ambient layer, required asset, and directed integration identifies a visible production target. The later Build records stable selectors for those targets. Review graphics, technical labels, and verification-only elements remain outside the final composition evidence model.
