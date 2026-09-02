# Intake and shared-creative approval

## Inspect first

Read the supplied script, transcript, footage, article, prior Storyboard, project assets, library inventory, Frame candidates, and existing handoff state. Summarize what is already known before asking questions.

## Standalone consolidated intake

Ask one compact batch covering only unresolved decisions:

1. delivery: destination, aspect, language, target length, and timing policy;
2. content: single message, factual locks, required passages, and exclusions;
3. Frame: present a small compatible set and ask the user to confirm one exact source;
4. animation scope: list source passages or scene candidates and ask which receive animation;
5. assets: required logos, SVGs, Lottie, supplied photography/video, and SFX direction;
6. scene ideas: invite any metaphor, object, diagram, typography, quotation, or transition idea the user already has;
7. curation policy: `approved-first`, `approved-only`, or `open`.

Apply [creative-defaults.md](creative-defaults.md) to unanswered stylistic details. A second batch is reserved for contradictions or missing facts that block an accurate handoff.

## Shared-creative review

Present the full proposed sequence before preparing files. Each animated scene card includes:

- canonical scene ID and source relationship;
- teaching goal, teaching intent, cognitive action, scene role, evidence form, density, and narrative scale;
- the viewer understanding;
- Hero and final readable state;
- composition and focal hierarchy;
- named layers with slots and depth order;
- required, preferred, and candidate building blocks with one responsibility each;
- real asset bindings;
- text content and chosen text effect;
- reveal beats, ambient motion, transition idea, and continuity state;
- for every adjacent-scene boundary: primary/accent role, exact catalog ID, approximate duration, outgoing state, incoming state, same-background assessment, perceptual anchor, color dependency, and what the transition communicates;
- approximate duration and timing policy.

Ask the user to contribute ideas or corrections across the whole sequence. Incorporate the response and request one explicit approval of:

- the Frame;
- the animated-scene set;
- the complete scene concepts.

The approved review becomes the temporary storyboard spec. Stable scene IDs begin at this approval point.

For a sequence of `N` scenes, approval covers exactly `N−1` transition ideas. Present these within the same shared-creative review so the user can shape both the scenes and the connective tissue before files are generated.

## Routed intake

When `curated-intake-request.json` is present, validate the parent plan hash and segment IDs before questions. Restate approved scope, locked decisions, inherited Frame/visual policy, timing precision, assets, and open questions.

Do not repeat the whole-film interview. Ask only open, missing, or contradictory items. If the request does not lock which sentences inside the cluster deserve animation, ask that one scope question. A proposed scope expansion is returned as `scopeChangeProposal`; it never mutates the parent.

The shared-creative review covers only the requested cluster. Approval may refine teaching classification, Hero/support construction, beats, teaching Components, text plan, and the cluster's internal transitions without changing the parent route or non-cluster timing.
