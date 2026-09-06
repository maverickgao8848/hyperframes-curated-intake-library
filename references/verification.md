# Verification

## Intake preflight

`verify-handoff.py` checks the Storyboard v3 schema; unique scene and use IDs; continuous numeric
timing; adjacent transition targets; required staging; relative paths; stale compiled caches;
routed parent hash and scope; and the absence of authored composition HTML. Required catalog uses
must resolve. Missing optional uses remain visible as warnings instead of disappearing.

Preparation, staging, and handoff verification require an external automated-agent attestation for
the exact Storyboard hash. Every scene longer than three seconds needs one record containing its full
verbatim motion quote, supported agent provenance, decision, structured conclusion, and rationale.
The CLI checks only structure/hash/quote/provenance/coverage/conflicts; semantic accept/reject belongs
to the versioned agent rubric. Resolved recipe claims are re-read and revalidated against the selected
library's catalog, aliases and sources on every phase; unresolved or stale claims fail closed.
The Schema and every production boundary accept exactly `motion-attestation/v1`; rejection messages
report both the actual value and that sole supported value.

It also rejects creative content in the manifest and rejects HANDOFF sections that duplicate scene
content, catalog IDs, timing maps, transition maps, or long prompts. Production does not implicitly
migrate v2; its fail-fast message names the explicit v2-to-v3 migration command.

## Build evidence

This is a later Build responsibility; Curated Intake publishes the gate and still stops at the
verified handoff. Before the builder opens the final preview, it performs one
compare-correct-recheck pass against the approved Storyboard v3, `frame.md`, delivery requirements,
and [motion-contract.md](motion-contract.md):

1. **Compare the running work.** Inspect every scene and adjacent transition in the actual
   composition. Confirm that content and visual direction agree, each required action visibly
   happens, transitions connect, and the ending holds long enough to read. For every selected Block,
   Component, primitive, template, motion, or transition, verify its real runtime call and visible
   responsibility; documentation, staged files, or a passing technical check alone are not evidence
   that it was used. Use snapshots for static layout and consecutive timeline points or actual
   playback for motion and continuity.
2. **Correct what the comparison finds.** Within the approved requirements, fix missing or weak
   actions, occlusion, layout, typography, Frame/theme drift, and selected items that are staged but
   not functionally used. Do not rewrite the approved Storyboard to make an implementation pass. If
   creative authorities conflict, use the existing conflict-resolution and user-lock rules.
3. **Recheck before delivery.** Reinspect every changed scene and its neighboring transitions, then
   rerun the affected technical checks. For timeline changes, verify forward playback, backward seek,
   and direct seek. Update affected derived files and existing evidence in place, and enter the normal
   final-preview flow only after every finding from this pass is resolved.

`verify-curation.py` contributes to this pass by validating the actual project against Storyboard v3
`uses`, `motion`, and `next`. Each required use must be staged and have runtime evidence for its
stated responsibilities. Scenes longer than three seconds need evidence for the declared internal
semantic change unless `motion` records an explicit static reason. Opening, settle, final hold,
outgoing, midpoint, and incoming states must be seek-stable. Report intake validity separately from
runtime fidelity; selectors, candidate audit, and needs-review state remain in external evidence
only. Reuse the project's existing evidence locations; this gate does not introduce a new report.
