# Workbench contract

The workbench is a product review surface derived from `director-plan.json`. Its primary surface is deliberately sparse: project duration, segment and pending-review counts, asset tasks, a four-lane timeline (`content`, `main visual`, `supporting layers`, `transitions`), and one segment's editorial decision at a time.

The main segment review flow exposes only the viewer-facing intent, recommended visual, editable key content, end time in seconds, supporting effects, feedback, and approval actions. Machine-oriented fields remain available under a collapsed technical-details disclosure: segment ID, route, frame policy, raw frame boundaries, catalog ID, layer target selectors, raw props JSON, and audit/diff evidence. Progressive disclosure changes presentation only; it must never remove plan data or weaken validation and approval semantics.

All edits are bounded operations with `baseRevision`. The server applies them under a lock, validates schema/catalog/coverage/locks, atomically replaces the plan, and appends audit evidence. A stale revision returns conflict; a locked target returns locked; invalid coverage or catalog binding returns an actionable validation error.

The browser has no model endpoint, no local hidden authority, and no direct filesystem write. Reopening the page reconstructs state solely from the plan.

V1 operations: approve/reject/lock, replace dominant candidate, edit content props, move an adjacent boundary, add/remove a layer, link an asset, change route, request a local reproposal through a comment, review audit/diff data, and finally approve.
