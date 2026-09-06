# Storyboard authoring v3

`STORYBOARD.md` is the sole scene-level creative authority. Its machine projection uses
`hyperframes-storyboard/v3`: numeric seconds, continuous scenes, and one deliberately lean scene
record. Candidates, ranking evidence, approval, and migration review never belong in it.

Each scene must state:

- `content`: the exact idea or evidence the audience must understand;
- `visual`: the concrete visual state and focus that express it;
- `motion`: the meaningful internal change, or an explicit reason the scene remains static;
- `uses`: approved catalog or `authored:` bindings, each with unique responsibilities and a
  required flag.

Use one to three through-line props, spaces, or signals when they create continuity. Prefer real
interface, data, quotations, and source evidence when proof is required. A noun-matching icon is not
a visual argument. For every scene longer than three seconds, keep `motion` as the authored motion
description. The normal Curated Intake or Visual Director agent applies the versioned motion rubric
and records an external attestation: exact Storyboard SHA, scene ID, full verbatim motion quote,
automated-agent provenance, decision, structured conclusion, and rationale. This is not another user
step. The CLI makes no textual semantic judgment; migration and legacy event count never attest.

`uses` is the final binding authority. A required binding must resolve and stage; an unavailable
optional binding remains visible as a catalog miss or verification warning. Do not put selectors,
target paths, percentages, candidate scores, or audit details in a use binding. Machine props come
from the catalog interface, not from semantic responsibilities.

The v3 type accepts `recipe:` only as a migration-only ID so v2 bindings can be preserved exactly.
It is deliberately outside the root Library kind enum. The existing legacy resolver may map it to
a real catalog ID. Otherwise an optional recipe produces a visible `unresolved-recipe` miss and is
neither selected nor staged; a required recipe fails selection, and all unresolved recipes fail
prepare, staging, and handoff verification. Every claimed mapping is re-resolved against the selected
library and must retain exact catalog, alias, source and integration provenance. No tool guesses.

`next` is omitted for an ordinary hard cut. Otherwise it names the immediately adjacent scene and
describes the transition semantics. The final scene always omits `next`. Scenes must continuously
cover `0..duration` without gaps or overlaps.

Locks are booleans for exactly timing, content, visual, uses, motion, and next. A routed result may
patch only v3 scene fields and cannot change locked timing or scene values, clear an existing lock,
or introduce a scene ID outside the approved segment-to-scene map.

For legacy input, run `migrate-storyboard-v2-to-v3.py` with distinct input, output, and report paths.
The deterministic draft preserves scene IDs, text, source anchors, event meaning/order, reuse, and
exit semantics without adding `Internal change:` or `Static reason:`. Its external `needs-review`
report names every unresolved scene and is evidence, not a second Storyboard authority.
Review and approve the v3 draft explicitly before production use.
