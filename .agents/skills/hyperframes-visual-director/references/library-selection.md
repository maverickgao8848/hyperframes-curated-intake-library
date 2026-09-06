# Library selection

Inspect the real shared catalog entry and preview before recommending an ID. Record the exact ID, source/version/hash, kind, semantic job, aspect support, duration/density/energy, frame policy, editable text/media slots, target interface, avoid rules, known gaps, fallback, and why adjacent candidates lost.

TalkCraft entries move through `inventoried → linted → ported → verified → published`. Inventory makes an item discoverable but not ready. Only `verified` or `published` TalkCraft items with a ready status may be presented as ready candidates.

Do not treat all 78 cards as Blocks. The current source category counts are browsing metadata and may evolve independently from runtime kind. If an inventory revision differs from an older planning specification, record the source commit and observed counts instead of silently forcing historical counts.

For revision 15 catalog targets, `routing.family`, `purpose`, `useWhen`, `avoidWhen`, `expects`,
and `motion` are the selection authority and are projected verbatim into the director catalog.
`framePolicy` remains independent. The canonical catalog is revision 15 and all 232 target entries
have individually curated values; its director catalog is a deterministic projection of that
authority. TalkCraft inventory entries are not catalog targets, so never fabricate the six fields
for them.

Revision 15 allows only the six
directing fields plus optional `fallbackIds` inside `routing`. Treat `expects` as semantic evidence,
not a duplicate prop schema: exact machine inputs remain in catalog `parameters` or `interface`.
Hero suitability is semantic and must not be reduced to a boolean switch. Runtime consumes only the six
directing fields for semantic routing, uses catalog facts for hard compatibility, and emits a
non-numeric v5 audit. Explicit TalkCraft locks pass through without synthesized catalog metadata
and never mix with catalog ranking.
