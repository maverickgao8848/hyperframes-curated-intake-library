# Artifact contract v3

Every decision has one owner. Conflicts resolve in this order: explicit user locks, the canonical
artifact that owns the field, skill defaults, then catalog ranking. Approval freezes the
Storyboard; defaults and scorers cannot silently replace it.

| Artifact | Class | Sole responsibility |
| --- | --- | --- |
| `BRIEF.md` | canonical | why, who, delivery, source scope, asset policy, explicit overrides |
| `frame.md` | canonical | palette, typography, material, composition grammar, spatial system, motion character |
| `STORYBOARD.md` | canonical | v3 scene timing, content, visual, motion, approved uses, transitions, and locks |
| `.hyperframes/curation.json` | state | v5 runtime output: exact Storyboard hash review state, needs, non-numeric candidate audits, hard-filter evidence, source, rejected choices, catalog misses; v4 is read-only migration input |
| `.hyperframes/intake-manifest.json` | state | status, IDs, relative paths, hashes, blockers |
| `.hyperframes/compiled/storyboard.json` | derived cache | machine projection of `STORYBOARD.md`; never hand-edited |
| `.hyperframes/staging-receipt.json` | evidence | staged sources, destinations, licenses, provenance, hashes |
| `.hyperframes/usage.json` and motion sidecars | build evidence | actual runtime targets, calls, states, snapshots, receipts |
| `HANDOFF.md` | navigation | status, canonical read order, manifest, preflight, next action, blockers |

`hyperframes.json` is runtime configuration, not creative authority. Composition paths derive from
`scene id → compositions/frames/<id>.html`; do not repeat them in scene records.

Derived files carry `generated: true`, `source: STORYBOARD.md`, and `sourceHash`. A hash mismatch
makes the cache stale. Intake does not generate scene contracts or a Build Plan. If Build creates a
   ledger, it stores use IDs, state, receipts, and blockers without copying creative prose.

In routed mode the parent `director-plan.json` remains the only whole-film machine authority.
mav-mg returns one bounded result patch tied to the parent hash and requested segment IDs.
It does not produce a parallel project packet before the Visual Director merges that patch.

## Storyboard v3 boundary

`storyboard-spec.schema.json` defines the production `hyperframes-storyboard/v3` authority. It has one
scene layer (`start/end/content/visual/uses/motion`) and optional title, next, narration,
on-screen text, SFX, source anchor, and field locks. It contains no approval, audit, candidate,
selector, percentage-event, or needs-review state. `curated-intake-result.schema.json` may patch only
those v3 scene fields and must respect global timing and scene locks.

The use-ID contract separates Library-kind/`authored:` IDs from migration-only `recipe:` IDs.
The existing alias resolver may map a recipe to a real catalog ID. Otherwise a required recipe fails
selection, an optional recipe remains a provenance-bearing `unresolved-recipe` miss, and unresolved
recipes fail every production path. Resolution claims are live-verified against the selected library
and retained in staging provenance. Motion attestation is external, automated-agent-authored, and
keyed to the exact Storyboard hash.

The frozen `storyboard-spec.v2.legacy.schema.json` is accepted only by the explicit migration CLI;
it must not evolve. The unused routed-result v2 legacy Schema was removed in F1; production
standalone artifacts and routed results are v3. `assets/library/inventory-latest.json` is the only
current library inventory report.
