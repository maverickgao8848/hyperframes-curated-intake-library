---
name: hyperframes-curated-intake
description: Prepare a user-approved, source-aware HyperFrames director handoff. Use when the user wants to choose a Frame, decide which scenes receive animation, co-design each animated scene, curate real Registry integrations and media, and produce a complete multi-file build packet for a later separate HyperFrames run. This skill ends after handoff verification and creates no composition or render.
---

# HyperFrames Curated Intake

Create a build-ready director packet that carries creative intent into HyperFrames through explicit files, stable identities, and verifiable integration requirements.

This skill owns teaching-scene intake, creative co-direction, approved scene contracts, Frame adoption, teaching Component curation, media adoption, handoff generation, and handoff preflight. A later `$hyperframes` run owns Sketch, Build, Preview, and Render. Whole-film dominant routing, generic Blocks, and generic Layers belong to the shared catalog and Visual Director.

## Choose the intake mode

- **Standalone:** no `curated-intake-request.json` is supplied. Preserve the existing full intake and explicitly ask “哪些段落/时间范围需要动画”, what stays as source footage, and what visual ideas the user already has. An article without a timeline is not permission to animate the whole article.
- **Routed:** a Visual Director `curated-intake-request.json` is supplied. Validate its parent hash and segment IDs first, restate inherited scope/Frame/timing/assets/locks, and ask only open, missing, or contradictory items. If the exact animation-worthy sentences inside the cluster remain open, ask for that sub-scope. Never change parent dominant-share decisions, non-cluster segments, or locks. Return a result packet instead of editing the parent plan.

## Default creative baseline

Read [creative-defaults.md](references/creative-defaults.md) before the intake. Apply these defaults only while this skill is active. Project-specific user choices take precedence.

## User confirmation points

Collect unanswered decisions in one consolidated message after inspecting the supplied material. Every standalone invocation confirms:

1. the exact `frame.md` source;
2. which source passages or planned scenes receive animation;
3. the user's additions or corrections to the proposed visual idea for each animated scene.

In routed mode, inherit confirmed items and ask only those listed in `questionsStillOpen` or discovered as missing/contradictory. Also confirm any unresolved delivery facts, required assets, factual locks, and exclusions that materially change the result. Use the defaults for the remaining creative decisions.

Read [intake-and-approval.md](references/intake-and-approval.md) for the compact interview and the shared-creative review.

For teaching and explainer work, read [teaching-visual-direction.md](references/teaching-visual-direction.md)
before proposing any Building Block, Component, chart, or transition. This skill owns semantic
classification and recommendation. Scripts may validate hard compatibility and project approved
choices into artifacts; they do not choose the creative winner.

## Workflow

1. Inspect the source material, project state, shared catalog, available Frames, Registry view, media inventory, and optional routed request.
2. Select standalone or routed mode. In standalone, run the consolidated intake and record the selected Frame plus animated-scene scope. In routed mode, validate and restate inherited decisions, then resolve only open items.
3. Classify every animated scene by teaching goal, teaching intent, cognitive action, scene role, evidence form, density, and narrative scale. Then draft the complete scene sequence and its `N−1` adjacent-scene transition map. For every animated scene, present its classification, message, Hero, construction, layers, skill-selected or candidate building blocks, assets, text treatment, motion arc, and continuity idea in plain language. For every boundary, name the transition, outgoing state, incoming state, duration, narrative purpose, whether the backgrounds are effectively the same, its perceptual anchor, and its color dependency.
4. Invite one shared-creative review. Incorporate the user's ideas, then obtain approval for the complete outline and animated-scene set.
5. Encode the approved direction in a temporary storyboard spec following [storyboard-spec.schema.json](references/storyboard-spec.schema.json). Give each scene a construction plan and explicit integration status.
6. Allocate beat windows, validate animation references, project the skill-approved choices into a bounded compatible project palette, and prepare the project packet. Treat any unselected compatible items as discovery evidence, never as automatic recommendations.
7. In routed mode, write `.hyperframes/curated-intake-result.json`; never write the parent plan. Scope changes remain proposals until the user approves them upstream.
8. Run `scripts/verify-handoff.py --project <project>` and resolve every error.
9. Deliver the project root plus `HANDOFF.md`, `BRIEF.md`, `STORYBOARD.md`, and the scene-contract directory. State that composition work remains for the later HyperFrames run.

The artifact authority and generated file set live in [artifact-contract.md](references/artifact-contract.md). Scene construction and integration semantics live in [scene-contracts.md](references/scene-contracts.md). Registry and media handling live in [library.md](references/library.md).

## Preparation commands

```text
python scripts/inventory-library.py --library <library>
python scripts/allocate-beats.py --spec <approved-spec> --write
python scripts/verify-beats.py --spec <approved-spec> --animation-skill <hyperframes-animation>
python scripts/select-project-palette.py --library <library> --storyboard-spec <approved-spec> --frame-preset <frame> --output <curation.json>
python scripts/prepare-project.py --project <project> --library <library> --curation <curation.json> --storyboard-spec <approved-spec> --intent <intent> --destination <destination> --language <language>
python scripts/prepare-project.py --project <project> --library <library> --curation <curation.json> --storyboard-spec <approved-spec> --intent <intent> --destination <destination> --language <language> --request <curated-intake-request.json>
python scripts/verify-handoff.py --project <project>
```

Use `--replace-approved-outline` only after the user approves a revised complete outline.

## Completion contract

A complete intake contains:

- one user-confirmed Frame copied into the project as `frame.md`;
- one approved `STORYBOARD.md` with canonical scene IDs and paths;
- one approved transition contract for every adjacent scene pair;
- one `scene-contracts/<scene-id>.json` for every scene;
- one `.hyperframes/build-plan.json` covering every scene, every directed integration, and every adjacent-scene transition;
- one `.hyperframes/intake-handoff.json` containing the complete scene set, timing, paths, and artifact hashes;
- one copy-ready `HANDOFF.md` that makes the later build protocol explicit;
- project-local required media with provenance;
- a passing handoff preflight;
- no authored composition HTML and no rendered video.

Read [handoff.md](references/handoff.md) when generating or reviewing the copy-ready prompt. Read [verification.md](references/verification.md) for intake and downstream evidence gates.
