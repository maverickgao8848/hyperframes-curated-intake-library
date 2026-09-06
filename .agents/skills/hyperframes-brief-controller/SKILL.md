---
name: hyperframes-brief-controller
description: Prepare a minimal upstream HyperFrames handoff that writes only BRIEF.md and selects one stored Frame as frame.md. Use when the user wants to constrain the visual system, allowed Registry blocks/components, reuse density, or authoring fallback before a later HyperFrames build. Stop before storyboard, composition authoring, installation, preview, or render.
---

# HyperFrames Brief Controller

Create a small, opinionated control surface for a later `$hyperframes` run. The result is a brief,
not a storyboard or a build.

## Output boundary

Write exactly two project artifacts:

- `BRIEF.md` — content intent, delivery facts, selected Frame identity, and Registry policy.
- `frame.md` — a byte-for-byte copy of one approved stored `FRAME.md`.

Do not create `STORYBOARD.md`, `HANDOFF.md`, `hyperframes.json`, curation files, scene contracts,
composition HTML, assets, previews, or renders. Inspecting source material, Frame inventories, and
Registry manifests is allowed. If the two output files already exist, read them first and preserve
explicit user locks unless the user asked to replace them.

If a later Curated Intake run is requested, its production scene authority is Storyboard v3. This
Brief Controller does not author or migrate that downstream artifact. The normal downstream Curated
Intake or Visual Director agent supplies the versioned semantic motion attestation for the exact
Storyboard hash; this does not add a user approval step. The sole production rubric ID is the exact
string `motion-attestation/v1`.

## Default sources

In this workspace, prefer:

- Frame inventory: `.agents/skills/hyperframes-curated-intake/assets/library/frames/inventory.json`
- Stored Frames: `.agents/skills/hyperframes-curated-intake/assets/library/frames/<preset>/FRAME.md`
- Curated Registry manifest: `.agents/skills/hyperframes-curated-intake/assets/library/registry/registry.json`

The former root `library/` mirror has been removed; do not recreate it or use it as a fallback.
When inventory evidence is required, `assets/library/inventory-latest.json` under the canonical
Curated Intake skill library is the sole current report.

Use user-supplied locations when provided. Never name a Frame or Registry item that is absent from
the resolved inventory or manifest.

## Workflow

1. Inspect the requested source, destination project, Frame inventory, candidate Frames, and
   Registry manifest. Do not run the full HyperFrames intent interview.
2. Resolve only the decisions required by [the BRIEF contract](references/brief-contract.md).
   Prefer the user's explicit choice. Otherwise select one Frame by content fit, legibility,
   evidence needs, aspect ratio, and desired tone. If two candidates imply materially different
   outcomes and the user has not expressed a preference, show at most three concise candidates and
   ask for one choice.
3. Copy the selected stored `FRAME.md` to the destination as `frame.md` without rewriting it.
   Record its source path and SHA-256 in `BRIEF.md`.
4. Build a closed Registry palette from exact IDs in the resolved manifest:
   - `allowed_blocks` contains only complete scene/sub-composition candidates.
   - `allowed_components` contains only inline effects, diagrams, overlays, or UI pieces.
   - Keep the palette deliberately small and give each item one intended semantic job.
   - Use canonical revision 15 `routing.family`, `purpose`, `useWhen`, `avoidWhen`, `expects`, and
     `motion` as the only catalog selection semantics; machine compatibility remains in catalog facts.
   - Choose for content function first, then reject items that contradict the selected Frame.
   - Do not use broad tags as permission and do not silently fall back to the public Registry.
   - Registry-declared transitive dependencies are allowed only as dependencies, not as additional
     creative choices.
5. Set `authoring_fallback` explicitly. Default to `ask`: if the allowlist cannot express a needed
   move, the builder must pause and request permission before hand-authoring or expanding the
   palette. Use `deny` only when the user wants a strictly closed system; use `allow` only when the
   user explicitly permits custom authoring.
6. Write `BRIEF.md` using the contract. Default to `workflow: general-video` and
   `flow: companion` so a later `$hyperframes` run consumes the brief without reopening intake.
7. Verify that the selected Frame exists, its hash matches, every Registry ID exists with the
   declared type, and no project artifact other than `BRIEF.md` and `frame.md` was written.

## Control semantics

Treat the selected Frame and the Registry palette as separate controls:

- `frame.md` governs palette, typography, material, composition grammar, spacing, and visual
  restraint.
- `BRIEF.md` governs what the film communicates and which reusable building blocks may be used.
- `frame_application: strict` applies the Frame to authored scenes. Use `structural-only` for real
  product UI, documents, screenshots, charts with fixed brand colors, or other native evidence;
  preserve evidence fidelity instead of reskinning it.
- `reuse_density` controls frequency, not simultaneous clutter. `sparse`, `balanced`, and `dense`
  should still preserve one primary focus at a time.
- `allowed_transition_families` constrains transition character even when a transition is authored
  rather than installed.

The allowlist in `BRIEF.md` is a downstream authoring contract, not a CLI security boundary. For
hard enforcement, the downstream build must validate installed/used item IDs against the allowlist
or point `hyperframes.json#registry` at a separately maintained filtered Registry. This skill does
neither because its output boundary is exactly two files.

## Stop condition

Return the paths to `BRIEF.md` and `frame.md`, name the selected Frame, summarize the Registry
palette and fallback mode, then stop. Do not continue into `$hyperframes` unless the user explicitly
asks for the build.
