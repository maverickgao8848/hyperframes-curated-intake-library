---
version: alpha
name: "Ferrari-inspired editorial chiaroscuro — frame layer"
description: "Video-first companion to design.md. Same warm near-black canvas, same white editorial display, same zero-radius structure, same one scarce red event — reframed so the frame (1920×1080) is the unit, composition is free, and numbers come from the script."
unit: "the frame — 1920×1080 primary; 1080×1920 and 1080×1080 documented"
principle: "a large dark field supports one lit subject; red is a scarce signal, never wallpaper"
fontAssets:
  sans: "assets/fonts/inter/Inter-400.woff2"
  sansBold: "assets/fonts/inter/Inter-700.woff2"
  mono: "assets/fonts/jetbrains-mono/JetBrainsMono-400.woff2"
  monoBold: "assets/fonts/jetbrains-mono/JetBrainsMono-700.woff2"
  cjk: "assets/fonts/noto-sans-sc/NotoSansSC-Variable.ttf"
colors:
  canvas: "#181818"
  ink: "#ffffff"
  inkDim: "#949494"
  line: "#474747"
  surface: "#303030"
  accent: "#e10600"
typography:
  # (a) Reading ramp — carried verbatim from design.md.
  display:  { fontFamily: "Inter", weight: 500, lineHeight: 1.00, tracking: "-0.02em" }
  body:     { fontFamily: "Inter", weight: 400, lineHeight: 1.45, tracking: "0" }
  label:    { fontFamily: "Inter", weight: 600, lineHeight: 1.20, tracking: "0.10em" }
  mono:     { fontFamily: "JetBrains Mono", weight: 400, lineHeight: 1.35, tracking: "0" }

  # (b) Hero / display ramp — frame-native. Sizes stored as strings (vw), see Known Gaps.
  wordmark-mega:   { fontSize: "26vw",  weight: 500, lineHeight: 0.84, tracking: "-0.03em", fontFamily: "Inter" }
  display-hero:    { fontSize: "14vw",  weight: 500, lineHeight: 0.92, tracking: "-0.02em", fontFamily: "Inter" }
  claim-editorial: { fontSize: "9.5vw", weight: 500, lineHeight: 0.98, tracking: "-0.02em", fontFamily: "Inter" }
  section-head:    { fontSize: "4.2vw", weight: 500, lineHeight: 1.00, tracking: "-0.02em", fontFamily: "Inter" }
  stat-numeral:    { fontSize: "8.4vw", weight: 700, lineHeight: 0.92, tracking: "-0.02em", fontFamily: "Inter" }
  stat-ledger:     { fontSize: "3.6vw", weight: 700, lineHeight: 0.95, tracking: "-0.015em", fontFamily: "Inter" }
  eyebrow-kicker:  { fontSize: "0.95vw",weight: 600, lineHeight: 1.20, tracking: "0.18em",  fontFamily: "Inter" }
  chrome-mono:     { fontSize: "0.85vw",weight: 400, lineHeight: 1.30, tracking: "0.02em",  fontFamily: "JetBrains Mono" }
  caption-body:    { fontSize: "1.5vw", weight: 400, lineHeight: 1.40, tracking: "0",       fontFamily: "Inter" }
rounded:
  none: "0px"      # the corner system, verbatim from design.md
spacing:
  hairline:      "1px"
  frame-pad:     "5vw"     # safe-area padding at frame scale
  gap-tight:     "1.2vw"
  gap:           "2.4vw"   # verbatim from design.md
  gap-wide:      "4.4vw"   # framePad from design.md, reused as wide gap
  gap-editorial: "8vw"
  max-containers: 2
components:
  # Every buildable unit as a structured token. Composition happens in Frame Treatments.

  # — the mono chip that marks index / callsign / timecode
  chrome-chip:
    backgroundColor: "transparent"
    textColor: "{colors.inkDim}"
    typography: "{typography.chrome-mono}"
    rounded: "{rounded.none}"
    padding: "0"
    border: "none"

  # — the eyebrow: uppercase micro-label above a headline
  kicker:
    backgroundColor: "transparent"
    textColor: "{colors.inkDim}"
    typography: "{typography.eyebrow-kicker}"
    rounded: "{rounded.none}"
    padding: "0"

  # — sticker: source rule "pill allowed for small labels only". Never at hero scale.
  sticker:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.eyebrow-kicker}"
    rounded: "{rounded.none}"
    padding: "0.55vw 1.1vw"
    border: "{spacing.hairline} solid {colors.line}"

  # — sticker-accent: the single red event, at sticker scale
  sticker-accent:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.ink}"
    typography: "{typography.eyebrow-kicker}"
    rounded: "{rounded.none}"
    padding: "0.55vw 1.1vw"
    border: "none"

  # — the headline block (composes into display-hero or claim-editorial per fit-to-measure)
  headline-hero:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.display-hero}"
    rounded: "{rounded.none}"
    padding: "0"

  # — wordmark for identity/cover
  wordmark-cover:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.wordmark-mega}"
    rounded: "{rounded.none}"
    padding: "0"

  # — the spec cell: hairline-topped number + label. First-class in this brand.
  spec-cell:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.stat-numeral}"
    rounded: "{rounded.none}"
    padding: "1.6vw 0 0 0"
    borderTop: "{spacing.hairline} solid {colors.line}"

  # — smaller ledger cell used in the density-exception plate
  spec-cell-ledger:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.stat-ledger}"
    rounded: "{rounded.none}"
    padding: "1.1vw 0 0 0"
    borderTop: "{spacing.hairline} solid {colors.line}"

  # — surface plate: the raised near-black step (#303030), used sparingly
  surface-plate:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.caption-body}"
    rounded: "{rounded.none}"
    padding: "1.6vw 2vw"
    border: "none"

  # — hairline rule: the primary depth device. 1px, {colors.line}.
  hairline-rule:
    backgroundColor: "{colors.line}"
    height: "{spacing.hairline}"
    width: "auto"
    rounded: "{rounded.none}"

  # — the red event as a shape. Never scales to a large fill.
  accent-mark:
    backgroundColor: "{colors.accent}"
    rounded: "{rounded.none}"
    height: "0.35vw"
    width: "3.4vw"

  # — caption band: dark strip isolating a subtitle line under a lit subject
  caption-band:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.caption-body}"
    rounded: "{rounded.none}"
    padding: "1vw 1.6vw"
    borderTop: "{spacing.hairline} solid {colors.line}"

  # — chrome bar: thin safe-edge information rail (top or bottom)
  chrome-bar:
    backgroundColor: "transparent"
    textColor: "{colors.inkDim}"
    typography: "{typography.chrome-mono}"
    rounded: "{rounded.none}"
    padding: "0"
    borderTop: "{spacing.hairline} solid {colors.line}"
---

# frame.md — Ferrari-inspired editorial chiaroscuro, frame layer

## 风格速览 / Style Snapshot

- **感觉 / Mood:** 高级杂志式的明暗对照——克制、戏剧化、昂贵但不喧闹。Premium editorial chiaroscuro: restrained, dramatic, and expensive without shouting.
- **最适合 / Best for:** 汽车、奢侈品、人物、品牌电影、高端发布和单一主角叙事。Automotive, luxury, portraits, brand films, premium launches, and single-hero stories.
- **视觉签名 / Signature:** 暖近黑画布、白色大标题、零圆角结构、一个受光主体和极稀缺红色。Warm near-black canvas, white display type, zero-radius structure, one lit subject, and extremely scarce red.
- **避免 / Avoid:** 把红色铺满、堆叠发光层或塞入大量信息，会立刻失去高级感。Flooding the frame with red, stacking glow, or packing in information immediately destroys the premium register.

> **Atoms are sacred · composition is free · numbers come from the script.**

## Overview

This is the video-first companion to `design.md`. The brand is a warm near-black chiaroscuro:
a large dark field (`{colors.canvas}` `#181818`, never pure black, faint warmth) supports one
lit subject in white; the corner system is zero (`{rounded.none}` `0px`); there is no
decorative shadow; depth comes from **hairlines**, **luminance steps**, and **subject
depth-of-field**; Rosso red (`{colors.accent}` `#e10600`) is a scarce signal — one atom per
frame at most, and only on the highest-priority information event. Everything the web spec
calls "editorial" reads at frame scale as: fewer things, larger, farther apart, calmer.

### Frame Craft Bar

- **Squint test** — one lit subject at **3–6×** the visual weight of its neighbor. If two
  things compete for the eye when you squint, one is oversized; the frame fails.
- **Silence test** — sparse archetypes (Cover, Claim, Focal, Red-Event, Closer) read
  **55–75% empty**. The dark field IS the composition; do not fill it to look complete. The
  **one** density exception is the **Ledger** plate — it is tight by design.
- **Restraint test** — the scarce element fires **once per frame**: the red accent, OR the
  raised `{colors.surface}` plate, OR a full-bleed subject. Not two at full strength.
- **Reference bar** — aim: a Ferrari annual-report spread, or a Massimo Vignelli specimen
  page. Failure: a black SaaS hero with a red CTA — same colors, wrong brand.

## Colors

Tokens unchanged from `design.md`. What changes is how they occupy the frame.

- `{colors.canvas}` **`#181818`** — the ground of **every** frame. Never pushed to pure black,
  never tinted cool. It is not a background; it is the subject's support.
- `{colors.ink}` **`#ffffff`** — the lit subject. Reserved for display type, spec numerals,
  the wordmark, and the strongest hairline on any frame.
- `{colors.inkDim}` **`#949494`** — kickers, chrome, timecode, colophon. Anything the eye
  should read second.
- `{colors.line}` **`#474747`** — the hairline. The brand's primary depth device; no shadow
  does its job. Rules divide, group, and step; they never decorate.
- `{colors.surface}` **`#303030`** — the raised near-black step. Used **once per frame**, for
  a caption band, a surface plate under a subhead, or the ledger backdrop.
- `{colors.accent}` **`#e10600`** — the **red event**. Applied to at most one atom per frame:
  a 0.35vw tick, a single word, a sticker-accent chip. Never a fill, never a wash, never a
  headline. If red appears twice, one is wrong.

## Typography

Two ramps live in the frontmatter. Prose gives context.

The **reading ramp** (`{typography.display}` / `body` / `label` / `mono`) is carried verbatim
from `design.md`. It governs prose captions, ledger labels, and any body run at frame scale.

The **display / hero ramp** is frame-native and far larger than any web use: the wordmark
reaches **`{typography.wordmark-mega}` 26vw**, the headline block
**`{typography.display-hero}` 14vw**, the editorial claim
**`{typography.claim-editorial}` 9.5vw**, and the spec numeral
**`{typography.stat-numeral}` 8.4vw**. Display weight stays at **500** — editorial confidence
comes from *size and silence*, never from weight. Tracking is negative (**−0.02em**),
line-height is tight (**0.84–1.00**), and no display line carries a shadow, gradient, or
outline.

**Legibility floor.** Any load-bearing line ≥ **1.4vw** (≈ 27px @ 1920). The eyebrow-kicker
at `0.95vw` and chrome-mono at `0.85vw` are chrome only — they may not carry a beat's meaning.

**Fit-to-measure headlines.** The headline block is capped at **≤ 78vw** wide, never touching
the safe margin. Step the ramp by word count: ≤ 3 words → `wordmark-mega` or `display-hero`;
4–6 words → `claim-editorial`; 7+ words → `section-head`. A long headline at hero size will
blow through the frame — that is a slide, not a plate.

## Layout — The Frame

- **Primary:** 1920×1080 (16:9). Documented reflows: 1080×1920 (9:16) and 1080×1080 (1:1).
- **Safe area:** `{spacing.frame-pad}` `5vw` on all edges. Chrome bars and hairlines sit
  *inside* the safe area.
- **Frame-relative law.** Every display value is authored in `vw` against the 1920 frame
  (`px ÷ 1920 × 100 = vw`). Fixed px is reserved for chrome atoms only:
  `{spacing.hairline}` `1px`, the corner system `{rounded.none}` `0px`, font-file weights.
- **Container ceiling.** At most **`{spacing.max-containers}` = 2** information containers on
  any single frame. A third relationship must be carried by direct annotation, spatial
  grouping, or a cut — never a third box.
- **Container-query note (for the showcase).** In `frame-showcase.html`, every `vw` value from
  this document is mapped **1:1 to `cqw`** against a frame with `container-type: size`, so a
  contact-sheet frame renders at true 1920-frame proportion at any display width. See Known
  Gaps.

## Elevation & Depth

One depth ceiling, no shadow.

- **Depth device:** hairlines (`{colors.line}` × 1px), luminance step
  (`{colors.canvas}` → `{colors.surface}`), and photographic depth-of-field on any full-bleed
  subject.
- **Banned:** `box-shadow`, glow, blur behind type, gradient wash, rounded corners.
- **The raised plate** (`{components.surface-plate}`) is the *only* elevated surface, used at
  most once per frame — usually to isolate a caption below a lit subject.

## Shapes

- Every corner is **`{rounded.none}` `0px`**. Rectangles, hairlines, and typography are the
  vocabulary.
- A pill / sticker is permitted **only** at eyebrow scale (`{components.sticker}`,
  `{components.sticker-accent}`). No large pill CTAs, no rounded cards.
- Ledger cells, spec cells, caption bands, and chrome bars all end in sharp corners; the
  hairline is what softens them, not radius.

## Components

Prose context for the frontmatter tokens. Values live in frontmatter; do not re-list them here.

- **`{components.chrome-chip}`** — the mono callsign / index chip. Top-left safe corner or
  bottom-rail only. Sets the "engineering log" register.
- **`{components.kicker}`** — the eyebrow micro-label. Rationed: not every frame gets one.
  When present it sits above the headline on a **≥ 2vw keep-out** rail.
- **`{components.sticker}`** and **`{components.sticker-accent}`** — the only sanctioned pill
  usage. Small labels only. The accent variant is one way the red event may appear.
- **`{components.wordmark-cover}`** — the identity plate. Composes
  `{typography.wordmark-mega}` and centers on the frame.
- **`{components.headline-hero}`** — the display headline. Composes
  `{typography.display-hero}` or `{typography.claim-editorial}` per fit-to-measure.
- **`{components.spec-cell}`** — first-class in this brand. Non-token construction: uppercase
  label in `{typography.eyebrow-kicker}` sits **above** the top hairline; numeral is
  baseline-anchored below.
- **`{components.spec-cell-ledger}`** — the same construction at ledger scale. Only used
  inside the density-exception plate.
- **`{components.surface-plate}`** — the elevated `#303030` step. Non-token construction: sits
  on `{colors.canvas}` with no border; the luminance step *is* the boundary.
- **`{components.hairline-rule}`** — the primary depth device. Always exactly 1px, always
  `{colors.line}`. Full-bleed on editorial frames; inset from the safe area on chrome frames.
- **`{components.accent-mark}`** — the red event as a shape. Never scales to a large fill.
- **`{components.caption-band}`** — a dark band that isolates a subtitle line under a lit
  subject. Top hairline only; no border on the other three sides.
- **`{components.chrome-bar}`** — the thin safe-edge rail carrying callsign, timecode, index.

## Motion & Timing

Chiaroscuro *is* the cut grammar. Nothing in this brand slides, eases, or drifts.

- **Cut vocabulary:** hard cut, dip-to-canvas, and hairline-wipe (a 1px rule sweeps across and
  the frame under it changes). No cross-dissolves between two lit subjects.
- **May animate:** the red accent may enter once per sequence, in a single frame, as a
  hairline draw or a 1-tick chip appearance. A spec numeral may count up on entry — once —
  then hold.
- **Must not animate:** the canvas ground, the hairline rule (as decoration), the wordmark,
  the surface plate. Parallax is banned; scale-on-scroll is banned; text glow is banned.
- **Dwell:** sparse plates hold **long** (the silence *is* the content). Ledger plates hold
  shorter but never race; a spec numeral must be readable in a 25% thumbnail during its dwell.
- **Export.** Timeline values are owned by HyperFrames; this spec sets structure only. Pace
  is driven by *density* (fewer elements per frame → more frames per beat), never by adding
  motion inside a frame.

## Frame Treatments

Seven plate archetypes. Each composes frontmatter components and adds only placement.

### 1 · Identity Cover  (identity/cover · move: lit wordmark on dark field, hairline colophon)
**Ground** `{colors.canvas}`, padding: `{spacing.frame-pad}`.
**Container** single centered flex column, gap: `{spacing.gap-tight}`.
**Composes** `{components.wordmark-cover}`, `{components.chrome-bar}`, `{components.chrome-chip}`.
**Focal** `{components.wordmark-cover}`: composes `{typography.wordmark-mega}`, centered
vertically and horizontally, `{colors.ink}` on `{colors.canvas}`.
**Chrome** `{components.chrome-bar}` pinned to the bottom safe edge; `{components.chrome-chip}`
in the top-left safe corner (callsign / index).
**Accent** none. The wordmark IS the event.
**Silence** ~72% empty.
**Fixed** wordmark is centered; the corner system is `{rounded.none}`; nothing overlaps the
wordmark bounding box (≥ 2vw keep-out); no shadow, no glow.
**Free** the wordmark string (per script), the chip callsign, the timecode.
**Density** sparse.  **Pace** low.

### 2 · Editorial Claim  (editorial/oversized-claim · move: single sentence, hairline top, dark silence below)
**Ground** `{colors.canvas}`, padding: `{spacing.frame-pad}`.
**Container** flex column, anchor: **centered** (default), gap: `{spacing.gap}`; content block
≤ 78vw wide.
**Composes** `{components.kicker}`, `{components.headline-hero}`, `{components.hairline-rule}`,
`{components.chrome-chip}`.
**Focal** `{components.headline-hero}`, stepped by word count — ≤ 3 words uses
`{typography.display-hero}`; 4–6 words steps to `{typography.claim-editorial}`; 7+ words steps
to `{typography.section-head}`. Baseline sits on the vertical golden line.
**Chrome** `{components.kicker}` above the headline on a 2vw keep-out rail;
`{components.hairline-rule}` full-bleed above the kicker; `{components.chrome-chip}` bottom-left.
**Accent** optional: one `{components.accent-mark}` under a single word. If the kicker uses
the red variant, the mark is omitted (restraint).
**Silence** ~65% empty.
**Fixed** hairline is 1px; display weight is 500; corners `{rounded.none}`; kicker keep-out
≥ 2vw.
**Free** the sentence, the kicker string, whether the accent-mark appears.
**Density** sparse.  **Pace** low.

### 3 · Focal Artifact  (focal-artifact · move: subject bleeds one edge, hairline callout across the dark)
**Ground** `{colors.canvas}`, padding: `{spacing.frame-pad}`.
**Container** two-container layout — subject plane (bleed) + annotation column;
gap: `{spacing.gap-wide}`. Anchor: **right-bleed** (the occasional asymmetric beat).
**Composes** `{components.hairline-rule}`, `{components.caption-band}`, `{components.chrome-chip}`,
optionally `{components.accent-mark}`.
**Focal** the artifact subject at ~62% frame width, bleeding one edge; depth-of-field carries
the third dimension.
**Chrome** a `{components.hairline-rule}` runs from the subject's optical center across the
dark to a `{components.caption-band}` on the left carrying one caption line in
`{typography.caption-body}`.
**Accent** one `{components.accent-mark}` at the terminus of the hairline (pointer tick).
The mark appears **only** at the callout terminus — never on the subject.
**Silence** ~55% empty.
**Fixed** hairline is 1px; the accent mark stays at its token dimensions; the subject may
bleed only one edge; no shadow behind the subject.
**Free** the subject, the caption sentence, which edge bleeds.
**Density** sparse.  **Pace** moderate.

### 4 · Spec Ledger  (data/ledger · move: hairline-divided grid of oversized numerals — the density exception)
**Ground** `{colors.canvas}`, padding: `{spacing.frame-pad}`.
**Container** CSS grid, 4 columns × 2 rows, gap: `{spacing.gap-wide}` column /
`{spacing.gap}` row. Anchor: **left** (this IS a reading/catalog frame).
**Composes** `{components.spec-cell-ledger}` ×6–8, `{components.hairline-rule}` (section-head
divider), `{typography.section-head}` header, `{components.chrome-bar}`,
`{components.chrome-chip}`.
**Focal** the numerals themselves at `{typography.stat-ledger}` — the grid as a whole is
the focal object, no single cell dominates. One cell may promote its numeral to
`{typography.stat-numeral}` for a headline stat.
**Chrome** section title uses `{typography.section-head}`, sits above the grid on a top
`{components.hairline-rule}` full-bleed. Header has `margin-bottom: {spacing.gap-wide}` so a
wrapped title cannot collide with row 1. `{components.chrome-bar}` at the bottom safe edge.
**Accent** one cell's uppercase label may be `{colors.accent}` — the highest-priority row
only.
**Silence** ~30% empty — the named density exception.
**Fixed** every cell has a top hairline rule; label above rule, numeral below; corners
`{rounded.none}`; maximum one accent'd cell; header keep-out ≥ 2vw.
**Free** cell count (6 or 8), numerals, labels, which row is promoted.
**Density** dense-exception.  **Pace** high.

### 5 · Chrome Catalog  (chrome/catalog · move: hairline index of rows, small type, wide silence at top)
**Ground** `{colors.canvas}`, padding: `{spacing.frame-pad}`.
**Container** flex column, anchor: **left**; gap: `{spacing.gap}` between rows;
`{spacing.gap-editorial}` above row 1.
**Composes** `{components.hairline-rule}` (row dividers), `{components.chrome-chip}` (row
index), `{components.kicker}` (row category), `{typography.caption-body}` (row title),
`{components.chrome-bar}`.
**Focal** the *rhythm* of the row list — no single row dominates. Rows are index chip ·
category kicker · title, separated by a full-bleed `{components.hairline-rule}` on every row.
**Chrome** a `{typography.section-head}` label sits top-left above the first hairline;
`{components.chrome-bar}` at the bottom safe edge.
**Accent** none by default. If present, at most one row's index chip is `{colors.accent}`.
**Silence** ~45% empty (concentrated in the top third above the section label).
**Fixed** row height stays constant; hairlines are full-bleed 1px; corners `{rounded.none}`;
titles never wrap beyond one line (truncate at the safe margin, not shrink).
**Free** row count (typically 4–7), titles, the category kickers.
**Density** standard.  **Pace** moderate.

### 6 · The Red Event  (brand-signature · move: one lit numeral, one red tick, otherwise all dark)
**Ground** `{colors.canvas}`, padding: `{spacing.frame-pad}`.
**Container** single centered flex column, gap: `{spacing.gap-tight}`. Anchor: **centered**.
Content block ≤ 62vw wide.
**Composes** `{components.spec-cell}` (single, promoted), `{components.accent-mark}`,
`{components.chrome-chip}`, optionally `{components.caption-band}`.
**Focal** one `{components.spec-cell}` composing `{typography.stat-numeral}`, label in
`{typography.eyebrow-kicker}` above the top hairline. Optically centered on the frame.
**Chrome** `{components.chrome-chip}` top-left (index); `{components.caption-band}` optional
at bottom, carrying one line of `{typography.caption-body}`.
**Accent** the sole red event on the entire sequence lands here: an `{components.accent-mark}`
tucked under the numeral, OR one word of the caption band set in `{colors.accent}`. Not both.
**Silence** ~70% empty.
**Fixed** exactly one accent atom; numeral is `{colors.ink}` (never red); the hairline above
the numeral is 1px; corners `{rounded.none}`; no shadow.
**Free** the numeral, the label, the caption sentence.
**Density** sparse.  **Pace** low.

### 7 · Closer  (closer · move: full canvas, tiny colophon, single hairline)
**Ground** `{colors.canvas}`, padding: `{spacing.frame-pad}`.
**Container** flex column, anchor: **centered**, gap: `{spacing.gap-tight}`.
**Composes** `{components.chrome-bar}`, `{components.chrome-chip}`, `{components.hairline-rule}`,
`{components.kicker}`.
**Focal** a single `{components.hairline-rule}` inset to 40vw, centered — the whole frame IS
the focal object.
**Chrome** `{components.kicker}` centered above the rule; `{components.chrome-chip}` top-left;
`{components.chrome-bar}` bottom safe edge.
**Accent** none. The closer refuses the red event — restraint is the signature.
**Silence** ~85% empty.
**Fixed** hairline is 1px, 40vw wide; no image; no accent; corners `{rounded.none}`.
**Free** the kicker string (typically end-mark or timestamp), the chip index.
**Density** sparse.  **Pace** low.

## Do's and Don'ts

**Do**
- Lean centered. Cover, Claim, Red Event, Closer all center their focal element. Reserve
  **left-anchor** for Ledger and Catalog (reading frames); reserve **right-bleed** for Focal
  Artifact (the tension beat).
- Vary the composition axis between consecutive frames — never run two identical anchors back
  to back beyond a 2-frame streak.
- Push one idea per frame. **≤ 2–3 distinct elements** (focal + at most a kicker + one
  support).
- Full-bleed one element on a **cadence** — every 3–4 frames, one atom owns the frame
  (a subject, a wordmark, a numeral). Not every frame.
- Ration the top-left kicker. The `{components.chrome-chip}` is allowed on most frames; the
  eyebrow `{components.kicker}` is not.
- Use the hairline as the primary structural device. It carries what a shadow would carry.
- Keep the accent scarce: one atom, one frame, and not every frame.

**Don't**
- No red wash, no red headline, no two red atoms in one frame, no red gradient. If red
  repeats, demote one to `{colors.ink}` or `{colors.inkDim}`.
- No rounded corners anywhere. No pill CTA. No card-with-shadow. No glow behind type.
- No decorative element overlaps the headline bounding box or the eyebrow rail (≥ 2vw
  keep-out).
- No third information container. If a third relationship exists, cut to a new frame.
- No ambient bloom, no parallax, no cross-dissolve between lit subjects.
- No same-anchor deck cadence (headline-left · graphic-right on every frame). That's a slide.
- No display line below the **1.4vw** legibility floor.

## Aspect-Ratio Behavior

| Treatment            | 16:9 (primary)                                        | 9:16 (portrait)                                                     | 1:1 (square)                                                  |
|----------------------|-------------------------------------------------------|---------------------------------------------------------------------|---------------------------------------------------------------|
| 1 · Identity Cover   | Wordmark centered at `wordmark-mega`                  | Wordmark re-scales to fit width (≤ 24vw of short edge)              | Wordmark steps to `display-hero`; centered; safe pad grows    |
| 2 · Editorial Claim  | Centered headline, kicker top, hairline full-bleed    | Headline re-flows to 3–4 lines at stepped-down size                 | Headline uses `claim-editorial`; block ≤ 82% width             |
| 3 · Focal Artifact   | Subject right-bleed; caption band left                | Subject **top-bleed**; caption band **below**; hairline vertical    | Subject centered, bleeds top only; caption band bottom-safe   |
| 4 · Spec Ledger      | 4 × 2 grid; section head top                          | 2 × 4 grid (columns collapse); promoted cell moves to top of stack  | 3 × 3 grid; drop one cell rather than shrink numerals         |
| 5 · Chrome Catalog   | 4–7 rows; hairlines full-bleed                        | Rows keep count; titles may truncate                                | Row count 3–5; kicker sits **above** title, not inline        |
| 6 · The Red Event    | Single spec-cell centered; accent mark below numeral  | Same; caption band mandatory (screen height gives room for context) | Same, tighter; accent mark stays at token dimensions          |
| 7 · Closer           | 40vw hairline centered                                | Hairline stays horizontal at 55vw of short edge                     | Hairline centered at 45vw                                     |

Load-bearing text never drops below **1.4vw** of the frame's short edge; if a re-scale would
break the floor, step the ramp down (Claim `display-hero` → `claim-editorial` →
`section-head`).

## Approved Real Entities & Numerals

- Entities named in `design.md` and its preserved intent: Ferrari (as visual reference, per
  the source's teaching credit to VoltAgent / awesome-design-md, MIT), Inter, JetBrains Mono,
  Noto Sans SC. These may appear as-named in colophon / credit chrome only.
- **Every stat, price, spec numeral, wordmark string, and headline sentence is a placeholder
  until the script provides it.** No figure in this document (`26vw`, `14vw`, `0.35vw`) is a
  content number — those are scale tokens. Never invent a horsepower, a lap time, a year, or
  a price. If the script has not delivered it, render `— figure —` and hold.

## Pre-Render Self-Audit

Run before finalizing every frame:

- **Squint** — does exactly one atom dominate at 3–6× its neighbor? (fail → oversize the focal)
- **Silence** — sparse frame reads 55–75% empty? (fail → remove an element, not shrink one)
- **Restraint** — red event present at most once, on one atom? (fail → demote to `{colors.ink}`)
- **Weight** — display weight exactly 500 (never 700 for display use in the reading ramp)?
- **Depth** — depth carried by hairline / luminance step / DOF only? (fail → strip shadow/glow)
- **Geometry** — every corner `{rounded.none}`? no pill above eyebrow scale?
- **Anchor** — centered by default; different from the previous frame beyond a 2-frame streak?
- **Element count** — ≤ 2–3 distinct elements? (fail → cut to a second frame)
- **Floor** — every load-bearing line ≥ **1.4vw**?
- **Fidelity** — every size references a frontmatter token; no ad-hoc `vw` invented in prose?
- **Component fidelity** — every buildable unit resolves to a `{components.X}` reference?
- **Keep-out** — no decoration overlaps headline or kicker rail (≥ 2vw)?
- **Legibility at 25%** — headline and hero numeral still readable in a thumbnail?

## Known Gaps

- **vw as string.** The DESIGN.md spec's consumer-behavior table stores `vw` values as
  strings (they are a documented frame-layer extension). Consumers hydrating CSS variables
  should read frontmatter sizes as strings and pass them through unchanged.
- **vw ↔ cqw mapping.** In `frame-showcase.html`, every `vw` value here is used as a `cqw`
  value (1:1) against a frame with `container-type: size`, so a contact-sheet frame renders
  at true 1920-frame proportion at any display width. This is the reason the showcase does
  not read as full-bleed billboards.
- **Motion timing owned elsewhere.** This document sets cut vocabulary and dwell character;
  HyperFrames owns timeline values. Any duration here is guidance.
- **Aspect re-scales are guidance.** The 9:16 and 1:1 reflows are structural rules, not pixel
  templates; per-frame re-scale is validated by the self-audit (legibility floor + 25%
  thumbnail check), not by a fixed size table.
- **Real entities.** Ferrari is the visual *reference* per the source's teaching credit; no
  Ferrari trademark, wordmark, or livery imagery is bundled. Any real logo, product image, or
  footage must clear the source's media / rights / manifest contract before render.
