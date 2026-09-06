---
name: hyperframes-curated-intake
description: Prepare a user-approved, source-aware HyperFrames Storyboard v3 and verified build handoff. Use to choose a Frame and animation scope, direct scene content/visual/motion, bind real reusable library items, or return a bounded Visual Director patch. Stops before composition authoring or rendering.
---

# HyperFrames Curated Intake

Produce one clear, executable directing authority for a later `$hyperframes` build. This skill ends
after handoff verification; it does not author compositions or render video.

## Authority and modes

Explicit user locks outrank canonical project artifacts, which outrank skill defaults and catalog
ranking. Once approved, `STORYBOARD.md` is the sole scene-level creative authority. Read
[artifact-contract.md](references/artifact-contract.md) before writing artifacts.

- **Standalone:** inspect the source, confirm the exact `frame.md`, exact passages/scenes that receive
  animation, and the user's corrections to the proposed scene ideas. Do not infer permission to
  animate an entire article.
- **Routed:** validate `curated-intake-request.json`, its parent hash, segment scope, and locks. Ask
  only unresolved or contradictory questions. Return one bounded result patch; do not write a
  parallel BRIEF, Storyboard, handoff, scene contracts, or Build Plan before the parent merge.

## Workflow

1. Inspect source material, current project state, Frame candidates, catalog, Registry view, media,
   and any routed request. Read [intake-and-approval.md](references/intake-and-approval.md).
2. Confirm delivery facts, source scope, asset policy, Frame, animated-scene set, and user-owned
   visual ideas in one compact intake.
3. Read [storyboard-authoring.md](references/storyboard-authoring.md). Author Storyboard v3 with
   numeric continuous timing, one content/visual/motion direction per scene, approved `uses`, and
   explicit `next` transition semantics only when the boundary is not an ordinary hard cut.
4. Invite one whole-sequence shared-creative review and obtain explicit approval. Approval freezes
   stable scene IDs, field locks, and the Storyboard.
5. Read [library-routing.md](references/library-routing.md). Query structured routing semantics in
   separate Block, Component, primitive, template, motion, and transition lanes. Code may hard-filter and rank
   compatible candidates; it cannot override the approved winner. Record complete catalog misses.
6. Stage every required selected item with project-relative paths, hashes, license, and provenance.
   Read [motion-contract.md](references/motion-contract.md) for executable action bindings.
7. In standalone mode generate only `BRIEF.md`, `frame.md`, `STORYBOARD.md`, short `HANDOFF.md`,
   `hyperframes.json`, `.hyperframes/intake-manifest.json`, `.hyperframes/curation.json`, staging
   receipts, and a clearly derived compiled Storyboard cache. Do not generate scene contracts or an
   Intake Build Plan.
8. Run `scripts/verify-handoff.py --project <project>` and resolve every error. Read
   [verification.md](references/verification.md) for intake and later Build evidence gates.

## Commands

```text
python .agents/skills/hyperframes-curated-intake/scripts/migrate-storyboard-v2-to-v3.py --input <approved-v2.json> --output <v3-draft.json> --report <outside-project-review.json>
python .agents/skills/hyperframes-curated-intake/scripts/select-project-palette.py --library .agents/skills/hyperframes-curated-intake/assets/library --storyboard-spec <approved-v3.json> --frame-preset <frame> --review-confirmation <external-review.json> --output <curation.json>
python .agents/skills/hyperframes-curated-intake/scripts/prepare-project.py --project <project> --library .agents/skills/hyperframes-curated-intake/assets/library --curation <curation.json> --storyboard-spec <approved-v3.json> --intent <intent> --destination <destination> --language <language>
python .agents/skills/hyperframes-curated-intake/scripts/stage-selected-items.py --project <project> --library .agents/skills/hyperframes-curated-intake/assets/library --all-required
python .agents/skills/hyperframes-curated-intake/scripts/verify-handoff.py --project <project>
python .agents/skills/hyperframes-curated-intake/scripts/apply-video-spec-refactor.py --check
python .agents/skills/hyperframes-curated-intake/scripts/apply-video-spec-refactor.py --report <outside-library-proposal.json>
```

The canonical production library is `.agents/skills/hyperframes-curated-intake/assets/library`.
Library-aware Curated Intake CLIs resolve that location by default; keep `--library` only when a
test or user-supplied external library must explicitly override it. The former root `library/`
mirror has been removed; do not recreate it or use it as a fallback.
`assets/library/inventory-latest.json` is the sole current library inventory report; no provenance
snapshot is a second current inventory.

Despite its historical filename, `apply-video-spec-refactor.py` is read-only for every library. It
requires exactly one of `--check` or `--report`; only an explicit report path outside the selected
library may be written. It cannot promote entries, update the catalog, or change its revision.

Selection emits `hyperframes-curated-intake/v5`. Non-explicit choices use the six-field routing
contract and non-numeric lexicographic evidence; explicit usable catalog IDs remain locked. Machine
input gates read only `parameters.required` and required `interface.props`, never semantic `expects`.
The canonical catalog is revision 15: routed entries expose only those six directing fields plus
optional declared fallbacks. Older catalog revisions are migration inputs, not production authority.

Use `--replace-approved-outline` only after approval of a revised complete outline. The explicit v2
migration writes a v3 draft and separate `needs-review` report; it never migrates in place or invents
approval, locks, or a motion-review prefix. Inspect an unreviewed draft with `--review-report`; only
an external automated-agent `--review-confirmation` tied to the exact Storyboard hash permits production selection.
Production accepts v3 only and tells v2 callers to run that migration command.
The frozen v2 schema is migration-only.

Storyboard v3 is the single-layer authority defined by `references/storyboard-spec.schema.json`.
Approval, candidate audit, selectors, percentage events, and needs-review state stay outside it.
For every scene longer than three seconds, the normal Curated Intake or Visual Director agent applies
[motion-attestation-rubric.md](references/motion-attestation-rubric.md) and writes an external
attestation with the exact Storyboard hash, scene ID, full verbatim `motionQuote`, decision,
structured conclusion/rationale, rubric version, and model or run provenance. This adds no user step.
The CLI checks structure and provenance only; it performs no textual semantic heuristic. Migration
never creates an attestation. Production accepts exactly `motion-attestation/v1`; no missing, empty,
case-shifted, whitespace-padded, older, newer, or arbitrary rubric identifier is compatible.
An unresolved optional `recipe:` use remains a visible `unresolved-recipe` miss and is not selected;
an unresolved required recipe fails selection, and no unresolved recipe may enter prepare, staging,
or handoff. Every production phase re-resolves a recipe claim from the selected library and verifies
catalog, alias and source hashes, revision, status, license, integration, and stageability.
