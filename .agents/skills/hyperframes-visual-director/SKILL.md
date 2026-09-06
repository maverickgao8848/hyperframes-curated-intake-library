---
name: hyperframes-visual-director
description: "Direct a whole video before build: inspect source footage or narration, browse real HyperFrames and TalkCraft catalog items, assign one dominant visual plus optional layers to every interval, collect asset requests, open a revision-safe approval workbench, and compile approved downstream handoffs. Use for whole-film visual planning and approval; stop before composition authoring or rendering."
---

# HyperFrames Visual Director

Create one reviewable whole-film visual plan. The machine authority is `director-plan.json`; `DIRECTOR.md`, the workbench, call sheets, previews, and downstream packets are derived views. Never create a second hidden state in the browser.

## Entry boundary

Use this skill for whole-film visual direction before build. It may route selected teaching clusters to `$hyperframes-curated-intake`, but it does not own teaching-scene detail, composition HTML, Studio, render, or final build verification. Stop after the user approves the plan and the handoff packets compile, unless the user explicitly asks to continue into Curated Intake.

## Inspect first

Before asking questions, inspect the supplied script, transcript, video/audio metadata, existing assets, `FRAME.md`, storyboard, `.agents/skills/hyperframes-curated-intake/assets/library/director-catalog.json`, previews, and any prior `director-plan.json`. Read [director-model.md](references/director-model.md) for authority and timing rules and [library-selection.md](references/library-selection.md) before recommending catalog items. The former root `library/` mirror has been removed; do not recreate it or use it as a fallback.

Summarize known facts, then consolidate only unresolved questions: delivery format, one core claim, factual locks and exclusions, source-footage/host presence, preferred visual balance, collaboration mode, timing precision, required or forbidden product UI, and where Frame should or should not apply. For collaboration modes and asset tasks, read [asset-direction.md](references/asset-direction.md).

For current library inventory evidence, use only the canonical Curated Intake library's
`inventory-latest.json`; historical provenance snapshots are not current inventory authority.

## Direct the whole film

1. Split by semantic beats, not fixed seconds. Every frame belongs to exactly one segment.
2. Assign one dominant visual to every segment: source footage, external evidence, external B-roll, a complete Registry Block, curated teaching, or a generated visual.
3. Add zero or more independent layers. Read [layer-and-block-taxonomy.md](references/layer-and-block-taxonomy.md) before classifying a TalkCraft or Registry candidate.
4. Apply a `framePolicy` to each dominant visual and layer. Read [frame-policy.md](references/frame-policy.md). WeChat and ChatGPT product UI remain `native-evidence`; Film Credits may be `frame-governed`.
5. Browse actual catalog entries and previews before naming an ID. Only `ready` entries whose TalkCraft `portStatus` is `verified` or `published` may be recommended as ready.
   Canonical revision 15 catalog items use only the six-field routing contract plus optional declared
   fallbacks for selection semantics; do not infer classifications or weights from removed metadata.
6. Assign one downstream route per segment: `direct-build`, `curated-intake`, `media-sourcing`, or `source-only`.
7. Record exact screen text/props, target, range, rationale, fallback, asset requests, and transition boundaries.

Use `scripts/validate-director-plan.py` throughout. The schema and semantic validator enforce 100% dominant coverage, legal overlaps, catalog readiness, frame policy, locks, edges, and approval integrity.

When rebuilding the Visual Director inventory in an explicitly authorized library-changing Sprint,
pass the canonical path through unchanged:

```text
python .agents/skills/hyperframes-visual-director/scripts/inventory-library.py --library .agents/skills/hyperframes-curated-intake/assets/library --talkcraft <talkcraft-repository>
```

## Review in the workbench

Read [workbench-contract.md](references/workbench-contract.md). Install a proposed plan with `scripts/prepare-plan.py`, then run `scripts/serve-workbench.py <project> --catalog <catalog>`. The workbench supports candidate replacement, text/props edits, boundary moves, layer changes, asset linking, route changes, comments, segment approval/lock, diffs, and final approval through bounded revision-safe patches.

Do not ask the user to edit JSON. Reject stale revisions and mutations touching locked decisions. Source hash changes stale only affected segments.

## Compile handoffs and stop

After final approval, run `scripts/compile-handoffs.py`. Read [curated-intake-handoff.md](references/curated-intake-handoff.md) before compiling or merging Curated packets. Curated requests use v3 scope packets whose `segmentSceneMap` has exactly one key per requested segment; an empty list means that segment owns no scene, never implicit fallback scope. Each stable scene ID belongs to exactly one segment. Curated results contain only Storyboard v3 scene patches. Direct-build, Curated, media-sourcing, and source-only packets remain derived from the parent plan and include its hash.

For a routed Storyboard scene longer than three seconds, the Visual Director agent may act as the
automated semantic authority under Curated Intake's versioned motion-attestation rubric. Write the
attestation outside Storyboard with the exact hash, scene ID, full verbatim motion quote, structured
decision/conclusion/rationale, and model or run provenance. This is an agent gate, not another user
approval step; the receiving CLI validates structure and provenance rather than judging prose. Use
the sole supported, case-sensitive production rubric ID `motion-attestation/v1`.

Do not author a composition or render a video in this skill. If the user explicitly asks to continue with a teaching cluster, invoke `$hyperframes-curated-intake` with its generated request. Otherwise report the approved project root and handoff manifest.
