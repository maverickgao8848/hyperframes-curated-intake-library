# BRIEF contract

`BRIEF.md` is the only directing input besides the copied `frame.md`. Keep it compact enough to
scan, but precise enough that a later builder does not need the intake conversation.
The output boundary is exactly these two files; library inventory is read-only evidence, with
Curated Intake's `assets/library/inventory-latest.json` as the sole current report.

Use this shape. Omit optional prose sections only when they truly do not apply; preserve the YAML
keys because they are the machine-readable control surface.

```markdown
---
schema: hyperframes-brief-controller/v1
workflow: general-video
flow: companion
title: ""
language: zh-CN
deliverable: ""
aspect_ratio: "16:9"
duration: "30-45s"
frame_id: cobalt-grid
frame_file: frame.md
frame_source: .agents/skills/hyperframes-curated-intake/assets/library/frames/cobalt-grid/FRAME.md
frame_sha256: "sha256:..."
frame_application: strict
registry_mode: closed
registry_source: .agents/skills/hyperframes-curated-intake/assets/library/registry
allowed_blocks: []
allowed_components: []
dependency_policy: registry-declared-only
reuse_density: balanced
allowed_transition_families: [cut, mask, push]
forbidden_registry_items: []
authoring_fallback: ask
---

# Outcome

One sentence describing what the viewer should understand, feel, or do.

# Audience and message

- Audience: ...
- Core message: ...
- Tone: ...

# Source material

List exact paths, URLs, quoted claims, or supplied assets. Distinguish facts from creative
interpretation. Never invent figures, quotes, product states, or brand assets.

# Content shape

Describe the intended beginning, development, and ending at beat level. Do not write a shot list or
scene-by-scene storyboard.

# Visual control

- Frame authority: which parts of `frame.md` are strict.
- Native evidence: which UI, documents, screenshots, charts, or brand colors must remain native.
- Motion character: a short description of pace, easing, emphasis, and restraint.
- Density: how `reuse_density` should feel while preserving one primary focus.

# Registry policy

Use an exact table; every ID must exist in the resolved manifest.

| ID | Type | Intended job | Frame compatibility |
| --- | --- | --- | --- |
| `data-chart` | block | Evidence-led data scene | Re-tokenize only if claim colors are not fixed |
| `inline-highlight` | component | Mark one decisive phrase | Uses Frame ink and square geometry |

Rules:

- Discovery and installation are limited to `allowed_blocks` and `allowed_components`.
- Declared dependencies may be installed only to support an allowed item.
- Tags, search results, and nearby catalog items do not expand the palette.
- Catalog selection semantics come only from revision 15 `routing.family`, `purpose`, `useWhen`,
  `avoidWhen`, `expects`, and `motion`; installation and machine compatibility use catalog facts.
- Items listed under `forbidden_registry_items` remain forbidden even if they are dependencies;
  choose another allowed item or stop.
- When no allowed item fits, obey `authoring_fallback` (`ask`, `deny`, or `allow`).
- Do not switch to another Registry source without user approval.

# Locks and exclusions

List required copy, required evidence, forbidden claims, forbidden motifs, and any content that must
not be animated.

# Completion target

State the expected final format and the few observable qualities that define a successful build.
```

## Field values

- `frame_application`: `strict` or `structural-only`.
- `registry_mode`: use `closed` for this skill. A later user-approved revision may widen it.
- `reuse_density`: `sparse`, `balanced`, or `dense`.
- `authoring_fallback`: `ask`, `deny`, or `allow`.
- `allowed_transition_families`: use descriptive families such as `cut`, `fade`, `mask`, `push`,
  `scale`, `camera`, `glitch`, or `shader`; keep the list short and Frame-compatible.

An empty allowlist is valid. It means the build uses authored layout and motion under the selected
Frame, subject to `authoring_fallback`; it does not mean the entire Registry is allowed.
