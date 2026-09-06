# Director model and authority

`director-plan.json` is the sole machine authority during direction. The workbench reads it and submits bounded patches; Markdown, call sheets, previews, and handoffs are regenerated from it.

The output boundary is the plan and its derived review/handoff views; library inventory is input
evidence only, and Curated Intake's `assets/library/inventory-latest.json` is its sole current report.

Each half-open segment range `[startFrame, endFrame)` owns exactly one dominant visual. Sorted segments must begin at frame 0, be contiguous and non-overlapping, and end at `project.durationFrames`. Transitions are edge objects and do not add dominant coverage.

Layers are independent intervals inside their owning segment and may overlap. Coverage for each layer type is the union of its intervals divided by the film duration, so simultaneous layers do not corrupt dominant share.

Timing precision is `word`, `sentence`, or `estimated`. Estimated plans remain reviewable; set `timingNeedsRefinement: true` whenever exact sync is deferred. A later build may pause only the exact-sync work that lacks a timing source.

Approval is revision-bound. Final approval requires every segment to be `approved` or `locked`; `approvedRevision` and `approvedHash` must match the current plan. Any creative mutation returns the plan to `in-review`. Comments may be added to locked segments, but locked decisions cannot be changed.
