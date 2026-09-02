# Teaching visual direction

This is the creative decision layer only for teaching and explainer scenes. Whole-film dominant routing and generic UI Blocks/Layers stay upstream. The catalog supplies facts;
the skill makes the recommendation. Keyword overlap, numeric routing scores, and hard-coded component
tables are not creative authority.

## Classify before selecting

Classify every animated scene before naming a Building Block or Component:

1. **Teaching goal** — the one conclusion or relationship the viewer must leave with.
2. **Teaching intent** — a compact semantic label for the lesson, such as `mechanism`, `contrast`,
   `evidence`, `procedure`, `spatial-location`, or `data`.
3. **Cognitive action** — `notice`, `explain`, `compare`, `predict`, `apply`, `verify`, or `remember`.
4. **Scene role** — `hook`, `definition`, `comparison`, `evidence`, `process`, `demo`, `chapter`,
   `transition`, `summary`, or `close`.
5. **Evidence form** — the actual proof on screen: text, quote, number, timeseries, table, process,
   hierarchy, trace, interface, image, video, map, or illustration.
6. **Information density** — sparse, comfortable, or dense.
7. **Narrative scale** — `support-beat`, `standard-scene`, or `chapter-peak`.

This borrows the useful separation in `video-spec-builder` between narrative purpose, scene role,
visual form, and transition intent. It adapts that classification to evidence-led teaching video,
reusable HyperFrames integrations, and a whole-film rhythm rather than treating a component as a
standalone effect.

## Skill-owned selection

Follow this order:

1. Use code only to reject hard incompatibilities: readiness, installability, required inputs,
   aspect, duration, density, component budget, Hero eligibility, policy, and render-time network use.
2. Read the scene classification and state the one visible responsibility the integration will own.
3. Match the evidence form before judging visual excitement. A beautiful mismatch is still wrong.
4. Choose a complete Registry Block only when its full choreography serves the teaching goal. Choose
   a Component when the scene needs project-specific data, layout, bindings, or event targets.
5. Reserve Hero-eligible treatments for chapter peaks. Most teaching scenes need one strong Hero and
   at most one supporting component.
6. Read catalog `avoid` and required inputs before approval. Use `fallbackIds` only for a concrete
   production risk.
7. Review the whole-film profile. Reuse motifs deliberately, but vary relationship, spatial grammar,
   evidence form, motion role, and narrative scale across adjacent scenes.

The approved storyboard spec is the selection authority. `device_candidates` and `integrations`
contain the skill's recommendation and rationale. `select-project-palette.py` may project a bounded,
compatible catalog set and validate those choices, but it must not invent a semantic winner.

## Scene routing by teaching situation

| Teaching situation | Preferred visual job | Strong candidates | Avoid |
| --- | --- | --- | --- |
| Source detail proves a claim | focus one exact region while preserving context | `registry-component:evidence-lens` | generic zoom without a named proof target |
| One model organizes several facts | reveal one governing structure plus 2–4 supports | `registry-component:teaching-bento` | a dashboard grid with equal emphasis everywhere |
| One phrase contains the distinction | make a compact statement physically memorable | `registry-component:pointer-proof` | shrinking paragraphs into display type |
| One step or state is active | show progression and current position | `registry-component:active-border` | decorative borders with no state meaning |
| One location, variable, or conclusion anchors the chapter | establish a dominant pin and its consequence | `registry-component:concept-pin` | using a pin where no spatial or logical anchor exists |
| Quantitative relationship is the proof | reveal the relation first, labels and source second | Mav Chart components below | decorative charts, invented data, or charting a single unsupported number |

The five Aceternity-inspired Components are timed, seek-safe adaptations of interaction ideas. Do not
recreate browser hover or scroll behavior in a rendered video.

## Mav Charts routing

Mav Charts are present in the catalog as ready Registry Components. Use them when the quantitative
relationship itself is the teaching goal, not merely because the script contains numbers:

- ordered trend: `registry-component:chart-line` or `chart-area`;
- two or three aligned trends: `registry-component:chart-multi-line`;
- discrete comparison or ranking: `registry-component:chart-bar` or `chart-horizontal-bar`;
- composition across groups: `registry-component:chart-stacked-bar`;
- part of a validated whole, at most four parts: `registry-component:chart-donut`;
- correlation: `registry-component:chart-scatter`;
- intensity across two dimensions: `registry-component:chart-heatmap`;
- conserved flow: `registry-component:chart-sankey`;
- compact supporting trends: `registry-component:chart-sparkline`;
- threshold or range emphasis: `registry-component:gauge-chart` or `chart-gauge` according to the
  catalog's stated responsibility.

Charts have been under-selected because their catalog entries require real `data`, `title`, and
`sourceNote`, are generally not Hero-eligible, and the prior keyword scorer could not infer the
quantitative relationship. During intake, explicitly classify a scene as `teaching_intent: data`,
choose the relationship above, add the required inputs, and give the chart one claim to prove.

## Same-background transition routing

For every adjacent pair, first decide whether the backgrounds are effectively the same. When they
are, set `same_background: true`, require `color_dependency: independent`, and select a perceptual
anchor that creates its own boundary:

- `transition:edge-lit-wipe` with `luminance-seam`: clean chapter or section advance;
- `transition:focus-pull` with `focus-plane`: overview-to-detail or evidence-to-conclusion;
- `transition:depth-swap` with `depth-occlusion`: enter a deeper layer, interface level, or narrative tier;
- `transition:shared-morph` with `shared-object`: a verified object continues across the cut;
- `transition:push-slide` with `directional-motion`: robust directional fallback;
- hard cut with `hard-cut`: default when no semantic continuity needs an effect.

Do not use a crossfade, color-only wipe, or tint dissolve as the primary separator between equal-color
scenes. Every expressive transition must state the semantic relationship it communicates.
