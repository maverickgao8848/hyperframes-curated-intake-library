# Library routing and staging

Read `.agents/skills/hyperframes-curated-intake/assets/library/catalog.json` as the only routing
authority. `.agents/skills/hyperframes-curated-intake/assets/library/director-catalog.json` is a
deterministic projection for Visual Director inspection and must never feed facts back into routing. The catalog owns
capability facts, readiness, source metadata, rights, and installation mechanics; it does not own the
creative winner.

`schemas/library.schema.json` defines the production revision 15 contract. Each
`registry-block`, `registry-component`, `svg`, and `lottie` entry must keep the six directing facts
inside `routing`: `family`, `purpose`, `useWhen`, `avoidWhen`, `expects`, and `motion`, with only
optional declared `fallbackIds` alongside them. Revisions 13 and 14 remain readable migration
inputs. The canonical revision 15 catalog has individually curated values for all 232 target entries.

Those six values are the director-selection authority. `framePolicy` remains an independent
application constraint and must not be inferred from `family` or `motion`. Tooling preserves and
projects curated values. The historically named `apply-video-spec-refactor.py`
is strictly read-only for libraries: it requires exactly one of `--check` or an explicit `--report`
outside the selected library, and the latter emits only a non-authoritative conflict report.
For the four routed visual kinds, revision 15 `routing` permits
only the six directing fields plus optional `fallbackIds`; the revision 14 decision fields are
invalid at both entry and routing levels. `expects` describes the semantic evidence a director
must supply, while machine-facing prop names remain in `parameters` and
`interface`. Hero suitability is expressed by `purpose`, `useWhen`, and `avoidWhen`, never a
separate boolean switch.

The `hyperframes-curated-intake/v5` curation candidate uses explainable, non-numeric audit facts: semantic tier, family and
purpose matches, matching use conditions, avoid conflicts, evidence for expectations, hard-filter
results, motion preference, repetition application, fallback trace, and source. Numeric scores and
the legacy semantic-tag, narrative-role, selection-role, or granularity audit fields are invalid.
The D2 runtime emits v5. Curation v4 and library revision 14 remain readable migration inputs, but
they do not authorize the router to read legacy decision fields.

For non-explicit candidates, compare structured values in this strict order: `family`, matching
`useWhen`, matching `purpose`, motion suitability for scenes longer than three seconds, prior use,
then catalog ID. This is lexicographic, not a numeric score; no later level may defeat an earlier
one. A known `avoidWhen` conflict excludes the candidate, while an unevaluated avoid condition is
retained as unknown. `expects` is explanatory semantic evidence and is never compared with
`available_inputs`. Required machine inputs come only from `parameters.required` and required
`interface.props`.

Hard gates use status, license, verified source hashes, integration/network safety, installability,
`aspectSupport`, dimensions, actual duration, and fps. A usable explicit ID—including SVG or logo
locks—is validated but never ranked. A disabled explicit item may traverse only its declared
`fallbackIds`, in order, with every fallback passing the same gates; otherwise record a catalog miss.
Hero-required selection needs an `emphasis` family plus non-empty semantic purpose/use conditions,
not a legacy boolean. TalkCraft locks pass through unchanged and never enter catalog ranking or
receive synthesized catalog metadata.

Before routing, the catalog loader validates the complete `catalog.json` against the single
repository-root `schemas/library.schema.json`; a failure is a configuration error identifying the
entry, JSON path, and field. The integration hard gate is fail-closed: its required fields, allowed
`mode` and `timelineOwner` values, and permitted property set come directly from that Schema, and
`renderTimeNetwork` must be the literal boolean `false`.

For each approved Storyboard v3 scene and use responsibility:

1. Read semantic needs from scene `content`, `visual`, `motion`, and `uses` responsibilities.
2. Query separate lanes: complete Registry Block, structural Registry Component, SVG/Lottie
   primitive, motion recipe, atomic motion rule, and transition.
3. Hard-filter readiness, installability, required inputs, aspect, duration, rights, render-time
   network safety, and semantic Hero suitability. Under revision 15 the latter is evaluated from
   `purpose`, `useWhen`, and `avoidWhen`, never a `heroEligible` flag.
4. Rank only compatible non-explicit candidates with the fixed lexicographic order. Preserve an
   explicit Storyboard selection after it passes hard gates.
5. Record candidates and rejections in curation; record no candidate prose in Storyboard.
6. Return a complete catalog miss instead of silently substituting an unrelated high-scoring item.

Do not restore removed classification, scoring, or compatibility-decision metadata to the
production catalog. Revisions 13 and 14 may be read only through explicit migration paths. Do not
introduce a new catalog kind.

Stage every required selected Block, Component, SVG, Lottie, and other media before preflight.
Receipts use project-relative destinations and include catalog ID, source and destination hashes,
license, provenance, and integration metadata. Render-time network access is forbidden. A total
staging limit may warn about resource pressure but cannot alter an approved selection.
