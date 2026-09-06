---
version: alpha
name: "BMW M-inspired engineered contrast — frame layer"
description: "Video-first companion to design.md. Hard-edged carbon hierarchy at frame scale: near-black grounds, directional rim light, mechanically precise framing, one concentrated light-blue, dark-blue and red stripe group or one white accent per frame."
unit: "the frame — 1920×1080 primary; 1080×1920 and 1080×1080 documented"
principle: "atoms are sacred · composition is free · numbers come from the script"
fontAssets:
  sans: "assets/fonts/inter/Inter-400.woff2"
  sansBold: "assets/fonts/inter/Inter-700.woff2"
  sansBlack: "assets/fonts/inter/Inter-800.woff2"
  mono: "assets/fonts/jetbrains-mono/JetBrainsMono-400.woff2"
  monoBold: "assets/fonts/jetbrains-mono/JetBrainsMono-700.woff2"
  cjk: "assets/fonts/noto-sans-sc/NotoSansSC-Variable.ttf"
colors:
  canvas: "#111111"
  ink: "#f4f4f5"
  inkDim: "#8e8e91"
  inkDimAlpha: "rgba(244, 244, 245, 0.58)"
  line: "#353538"
  surface: "#1a1a1c"
  surfaceHi: "#242426"
  accent: "#ffffff"
  mLightBlue: "#5DADE0"
  mDarkBlue: "#174A8B"
  mRed: "#E32636"
typography:
  # --- Reading ramp (px → cqw @1920) ---
  body:
    fontFamily: "Inter"
    weight: 400
    fontSize: 28px
    fontSizeCqw: 1.46cqw
    lineHeight: 1.45
  label:
    fontFamily: "Inter"
    weight: 600
    fontSize: 22px
    fontSizeCqw: 1.15cqw
    tracking: "0.08em"
    textTransform: uppercase
  mono:
    fontFamily: "JetBrains Mono"
    weight: 400
    fontSize: 22px
    fontSizeCqw: 1.15cqw
    lineHeight: 1.35
  monoBold:
    fontFamily: "JetBrains Mono"
    weight: 700
    fontSize: 22px
    fontSizeCqw: 1.15cqw
    tracking: "0.02em"
  caption:
    fontFamily: "Inter"
    weight: 400
    fontSize: 20px
    fontSizeCqw: 1.05cqw
    lineHeight: 1.4
  # --- Hero / display ramp (frame-native cqw) ---
  wordmark-mega:
    fontFamily: "Inter"
    weight: 800
    fontSize: 30cqw
    lineHeight: 0.84
    tracking: "-0.03em"
  display-hero:
    fontFamily: "Inter"
    weight: 800
    fontSize: 14cqw
    lineHeight: 0.92
    tracking: "-0.025em"
  display-large:
    fontFamily: "Inter"
    weight: 800
    fontSize: 9.5cqw
    lineHeight: 0.94
    tracking: "-0.022em"
  section-head:
    fontFamily: "Inter"
    weight: 800
    fontSize: 4.2cqw
    lineHeight: 1.0
    tracking: "-0.015em"
  stat-hero:
    fontFamily: "Inter"
    weight: 800
    fontSize: 12cqw
    lineHeight: 0.9
    tracking: "-0.02em"
  stat-ledger:
    fontFamily: "Inter"
    weight: 800
    fontSize: 3.6cqw
    lineHeight: 0.95
    tracking: "-0.01em"
  pill-giant:
    fontFamily: "JetBrains Mono"
    weight: 700
    fontSize: 1.35cqw
    tracking: "0.14em"
    textTransform: uppercase
  # --- Legibility floor ---
  legibility_floor: 1.4cqw   # ≈ 27px @ 1920; anything smaller is chrome/colophon only
rounded:
  chrome: "0px"
  media: "0px"
  # source law: 圆角只允许出现在确有需要的产品证据上 → only if the real artifact has one
spacing:
  framePad: "3.8cqw"        # 16:9 safe area
  framePadShort: "5.2cqw"   # short-edge safe padding for 9:16 / 1:1
  gap: "1.6cqw"
  gapTight: "0.8cqw"
  gapWide: "3.2cqw"
  hairline: "1px"
  rimLight: "2px"
  maxContainers: 2
components:
  # ——— Chrome atoms ———
  rule-hairline:
    height: "{spacing.hairline}"
    backgroundColor: "{colors.line}"
    role: "structural divider · never decorative"
  rule-rim:
    height: "{spacing.rimLight}"
    backgroundColor: "{colors.accent}"
    role: "the single directional rim-light bar per frame; horizontal or vertical, never both"
  eyebrow-label:
    typography: "{typography.label}"
    textColor: "{colors.inkDim}"
    padding: "0"
    role: "kicker; rationed — appears on a minority of frames"
  eyebrow-mono:
    typography: "{typography.monoBold}"
    textColor: "{colors.inkDim}"
    role: "technical eyebrow / index; sits above a hairline"
  index-chip:
    typography: "{typography.mono}"
    textColor: "{colors.inkDim}"
    backgroundColor: "transparent"
    borderTop: "{spacing.hairline} solid {colors.line}"
    padding: "0.6cqw 0 0 0"
    rounded: "{rounded.chrome}"
    role: "frame index N/NN; bottom-left of the safe area"
  # ——— Surfaces ———
  carbon-panel:
    backgroundColor: "{colors.surface}"
    borderLeft: "{spacing.hairline} solid {colors.line}"
    rounded: "{rounded.chrome}"
    padding: "{spacing.gap}"
    role: "one-tier surface for containers"
  carbon-panel-hi:
    backgroundColor: "{colors.surfaceHi}"
    rounded: "{rounded.chrome}"
    padding: "{spacing.gap}"
    role: "second-tier lift (never soft shadow); focal container"
  caption-band:
    backgroundColor: "rgba(17, 17, 17, 0.72)"
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    padding: "0.8cqw 1.2cqw"
    rounded: "{rounded.chrome}"
    borderTop: "{spacing.rimLight} solid {colors.accent}"
    role: "fixed subtitle system: single position, single weight, one rim-light divider"
  # ——— Cells and chips ———
  ledger-cell:
    backgroundColor: "transparent"
    borderTop: "{spacing.hairline} solid {colors.line}"
    padding: "1.0cqw 0 0 0"
    typography: "{typography.mono}"
    textColor: "{colors.ink}"
    role: "one metric per cell; label above stat"
    fields:
      label: "{typography.label} · {colors.inkDim}"
      value: "{typography.stat-ledger} · {colors.ink}"
  ledger-cell-hero:
    backgroundColor: "transparent"
    borderTop: "{spacing.rimLight} solid {colors.accent}"
    padding: "1.0cqw 0 0 0"
    role: "the one accented cell in a ledger — the rim-light gets spent here"
    fields:
      label: "{typography.label} · {colors.ink}"
      value: "{typography.stat-hero} · {colors.accent}"
  window-chip:
    backgroundColor: "transparent"
    border: "{spacing.hairline} solid {colors.line}"
    textColor: "{colors.ink}"
    typography: "{typography.mono}"
    padding: "0.7cqw 1.0cqw"
    rounded: "{rounded.chrome}"
    whiteSpace: nowrap
    role: "spec/tag chip in catalog frames; never rounds"
  sticker-mono:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.canvas}"
    typography: "{typography.pill-giant}"
    padding: "0.5cqw 0.9cqw"
    rounded: "{rounded.chrome}"
    whiteSpace: nowrap
    role: "the ONE inverted sticker per frame; consumes the accent budget"
  meter-cap:
    backgroundColor: "{colors.accent}"
    width: "0.35cqw"
    height: "2.4cqw"
    role: "hard rim-cap; marks a value terminus or the rim-light on a hero"
  # ——— Buttons ———
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.canvas}"
    typography: "{typography.label}"
    padding: "0.9cqw 1.6cqw"
    rounded: "{rounded.chrome}"
    role: "web-parity CTA; rarely used in-frame"
  button-primary-giant:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.canvas}"
    typography: "{typography.section-head}"
    padding: "1.4cqw 3.0cqw"
    rounded: "{rounded.chrome}"
    whiteSpace: nowrap
    role: "frame-scale action block; only on closer/CTA plates"
  button-ghost-giant:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    border: "{spacing.hairline} solid {colors.line}"
    typography: "{typography.section-head}"
    padding: "1.4cqw 3.0cqw"
    rounded: "{rounded.chrome}"
    whiteSpace: nowrap
    role: "secondary block; pairs with button-primary-giant, no accent"
  # ——— Motif ———
  rim-light-bar:
    height: "{spacing.rimLight}"
    width: "22cqw"
    backgroundColor: "{colors.accent}"
    role: "the single directional highlight; horizontal (heroic) or vertical (locked)"
motion:
  cut_grammar: "hard cut · lateral force · lock-off"
  banned: "ease-out bounce, rebound, soft crossfade, elastic scale"
  allowed: "instant cut, rim-light wipe (1 frame), lateral push (≤200ms), lock-off freeze (≥600ms hold)"
  dwell_min_ms: 600
  export: "1920×1080 @ 30fps · sRGB · sound-off legible"
---

# frame.md — BMW M-inspired engineered contrast (frame layer)

## 风格速览 / Style Snapshot

- **感觉 / Mood:** 冷静、精确、有机械张力，像性能工程发布片。Controlled, exact, and mechanically tense—built like a performance-engineering launch film.
- **最适合 / Best for:** 汽车、硬件、制造、工程、性能指标和严肃技术产品。Automotive, hardware, manufacturing, engineering, performance metrics, and serious technical products.
- **视觉签名 / Signature:** 近黑底、硬边框架、定向轮廓光，以及浅蓝／深蓝／红三道斜切色带。Near-black grounds, hard framing, directional rim light, and a light-blue / dark-blue / red diagonal stripe signature.
- **避免 / Avoid:** 柔软生活方式、儿童内容、糖果色和装饰性圆角会削弱它的工程可信度。Soft lifestyle work, children's content, candy colors, and decorative rounding dilute its engineered credibility.

> **atoms are sacred · composition is free · numbers come from the script.**

## Overview

This is the **frame layer** of the BMW M-inspired direction. The palette below governs this Frame; `design.md` supplies the base
weights, radius `0`, hairline `1px`, and framePad `3.8cqw`. This file
re-frames those atoms so the **frame** — not the page — is the unit. The register is mechanical:
near-black canvas, three carbon tiers (`{colors.canvas}` → `{colors.surface}` → `{colors.surfaceHi}`),
Inter 800 display against Inter 400 body, JetBrains Mono for technical voice, and a light-blue / dark-blue / red stripe signature.
Use that stripe group as the focal accent on identity and showcase frames; on other frames,
choose either the stripe group or a single white accent. No soft decorative shadow, no pill geometry, no
dead-black unstructured space.

### Frame Craft Bar

Every frame passes four eyeball tests before any structural check:

- **Squint test** — exactly one element dominates at **3–6×** the size of its nearest neighbor. A chasm, not a ramp.
- **Silence test** — sparse archetypes (identity, oversized-claim, focal-artifact, closer) read **55–75% empty**. Emptiness is the brand's confidence — do not fill it. The **ledger / spec-sheet** plate is the ONE named density exception.
- **Restraint test** — the brand's scarce element (one stripe group or one `{colors.accent}` moment — a `{components.sticker-mono}`, a `{components.rim-light-bar}`, a `{components.ledger-cell-hero}` rim, or an accent stat) fires **once per frame**. If it appears twice at full strength, demote one to `{colors.ink}`.
- **Reference bar** — aim at a BMW M keynote plate or a motorsport print specimen: hard edges, three carbon tiers, and a concentrated blue / blue / red stripe group. Failure looks like a generic dark-mode SaaS dashboard — too many gray boxes, accent spent everywhere.

## Colors

Carbon and white tokens follow `design.md`; the M-inspired stripe palette is defined here. Reframed as **full-frame grounds and a rationed accent**, not surface swatches.

| Token | Value | Frame role |
| --- | --- | --- |
| `{colors.canvas}` | `#111111` | Default ground for ~80% of frames. Never pure black — source law: *近黑画布不是纯黑*. |
| `{colors.surface}` | `#1a1a1c` | Tier-2 carbon. Container ground for the primary panel. |
| `{colors.surfaceHi}` | `#242426` | Tier-3 carbon. Lifts the focal container above tier-2 — the source's *可感知的重量差*. |
| `{colors.line}` | `#353538` | Every hairline and container edge. Structural, never decorative. |
| `{colors.ink}` | `#f4f4f5` | Load-bearing type. Never `#ffffff`. |
| `{colors.inkDim}` | `#8e8e91` | Kickers, labels, secondary rows. |
| `{colors.accent}` | `#ffffff` | **Rationed.** One firing per frame — rim-light, one stat, one sticker, or one meter-cap. |
| `{colors.mLightBlue}` | `#5DADE0` | First stripe in the M-inspired signature. |
| `{colors.mDarkBlue}` | `#174A8B` | Second stripe; keep distinct from the carbon ground. |
| `{colors.mRed}` | `#E32636` | Third stripe; keep grouped with the blues. |

The stripe colors are this Frame's illustrative palette, not an official brand color specification.
Render them as three adjacent hard-edged diagonal bands, ordered light blue, dark blue, red.
Treat the group as one accent; keep it legible at thumbnail size.

**Frame color rules.** A frame's ground is a single carbon tier; no gradient crosses the frame edge. Every tier step must be perceptibly heavier. Use one stripe group or one white accent at full strength; do not spread the stripe colors across unrelated UI elements.

## Typography

Two ramps: a **reading ramp** carried from `design.md` in px (with `cqw` equivalents), and a **display/hero ramp** authored frame-native. Resolved values live under `{typography.*}` in frontmatter.

**Reading ramp** — `{typography.body}` `{typography.label}` `{typography.caption}` `{typography.mono}`. Load-bearing at ≥ **1.4cqw** (≈27px@1920). This is the **legibility floor** — anything below carries chrome only.

**Display / hero ramp** — `{typography.wordmark-mega}` `{typography.display-hero}` `{typography.display-large}` `{typography.section-head}` `{typography.stat-hero}` `{typography.stat-ledger}` `{typography.pill-giant}`. Weights are frozen at **800 / 400 / 600** as the source specifies; hero line-height stays tight (`0.84–0.94`); tracking negative on display, positive on mono chrome.

**Fit-to-measure headlines.** A headline's size is a function of its line length. Cap the text block at **≤ 78cqw**; step the ramp by word count: **≤ 3 words → `{typography.wordmark-mega}` or `{typography.display-hero}`**; **4–6 words → `{typography.display-large}`**; **7+ words → `{typography.section-head}`**. Short lines go big; long lines go small.

**Voice split.** Inter carries meaning. JetBrains Mono carries **evidence** — indices, spec labels, unit tags, technical eyebrows. Never mix them inside a single line.

## Layout — The Frame

- **Primary frame:** 1920×1080 (16:9). Reflows: 1080×1920 (9:16), 1080×1080 (1:1).
- **Safe area:** `{spacing.framePad}` = `3.8cqw` on all four sides for 16:9. `{spacing.framePadShort}` = `5.2cqw` on the short edge for 9:16 / 1:1.
- **Grid:** informal 12-track on 16:9 with `{spacing.gap}` = `1.6cqw`. Snap containers to one spine.
- **Frame-relative law:** every display size, container, gap, and padding is expressed in `cqw` against 1920. Only chrome atoms are `px` — hairline `1px`, rim-light `2px`, radius `0px`.
- **`cqw` law.** Frame-relative sizes are authored against the **frame container** (`container-type: size`), not the viewport — so the frame renders at true proportion whether full-bleed or in a contact sheet.
- **Max two information containers per frame** (source rule). A third relationship rides on direct annotation or shared rim-light — never a third container.

## Elevation & Depth

There is no soft shadow. Depth is built by:

1. **Carbon tier steps** — `{colors.canvas}` → `{colors.surface}` → `{colors.surfaceHi}`, each visibly heavier.
2. **Hairline edges** — `{spacing.hairline}` in `{colors.line}` marking every container boundary.
3. **Directional rim-light** — the single `{components.rule-rim}` or `{components.rim-light-bar}` per frame indicating light direction.

**Ceiling:** three tiers max. No fourth surface. No blur, no inner glow. Source law: *不使用装饰性柔和阴影*.

## Shapes

- **Radius:** `{rounded.chrome}` = `0px`. Every atom — chip, sticker, button, panel — has square corners.
- **Media crop:** hard rectangles. No rounded frames on captured video or product plates.
- **Exception:** rounded corners appear only on the real artifact itself, and only if the artifact has them.

## Components

Every buildable unit lives in the frontmatter `{components.*}` block. Prose here describes intent and construction the token set cannot hold — never re-lists resolved values.

- **`{components.rule-hairline}`** — the structural divider. Every panel edge, ledger cell top-border, and eyebrow-to-body separator uses it. If it doesn't separate two zones, remove it.
- **`{components.rule-rim}`** and **`{components.rim-light-bar}`** — the frame's directional light. Horizontal reads as heroic acceleration; vertical reads as lock-off. Pick one; never both.
- **`{components.eyebrow-label}`** and **`{components.eyebrow-mono}`** — kickers. Ration them — the top-left eyebrow is a deck reflex; use on a **minority** of frames.
- **`{components.index-chip}`** — frame index (`04 / 12`) as a mono row anchored under a hairline. Bottom-left of the safe area on catalog/editorial plates.
- **`{components.carbon-panel}`** and **`{components.carbon-panel-hi}`** — the two-tier container system. The `-hi` variant lifts by tier step, not shadow. Never nest three panels.
- **`{components.caption-band}`** — the **fixed subtitle system**. Position, weight, and rim-light divider are frozen across the deck.
- **`{components.ledger-cell}`** and **`{components.ledger-cell-hero}`** — the spec-sheet cell. Every cell shares construction; the `-hero` cell spends the frame's accent budget on its top rim and stat color.
- **`{components.window-chip}`** — the spec chip in a catalog grid. Border, mono type, square corners; never fills.
- **`{components.sticker-mono}`** — the ONE inverted mono sticker per frame. If a sticker fires, the rim-light does not.
- **`{components.meter-cap}`** — a hard rim-cap terminus.
- **`{components.button-primary}` / `{components.button-primary-giant}` / `{components.button-ghost-giant}`** — CTAs. Giant variants only on closer plates.

**Construction the token set cannot hold:** a `{components.ledger-cell-hero}` is always at the **leftmost** position of its row (light travels left-to-right); the `{components.sticker-mono}` and `{components.rim-light-bar}` never appear on the same frame (shared accent budget). These are relational rules, not property values.

## Motion & Timing

Cut grammar derived from the brand character (see `{motion.*}` in frontmatter):

- **Allowed:** instant hard cuts, one-frame rim-light wipes, lateral push ≤ 200ms, lock-off freeze ≥ 600ms hold.
- **Banned:** ease-out bounce, elastic scale, rebound, soft crossfade, decorative motion.
- **Dwell:** every frame holds at least 600ms after lock-off.
- **What must not animate:** the `{components.caption-band}` (fixed system), hairline grid, frame index.
- **What may animate:** the `{components.rim-light-bar}` sweep, a single count-up on the `{components.ledger-cell-hero}`, lateral crops on full-bleed media.
- **Export:** 1920×1080 @ 30fps, sRGB, legible with sound off — captions are load-bearing.

## Frame Treatments

Six plate archetypes. Each **composes** frontmatter components and adds only placement — construction values live in tokens, never in prose. Every size named is a token reference; no ad-hoc numbers.

### 1 · Identity Cover  (identity · move: monogram lock-off)
**Ground** `{colors.canvas}`, padding `{spacing.framePad}`.
**Container** single-cell flex, centered, column, gap `{spacing.gapWide}`.
**Composes** `{components.rim-light-bar}`, `{components.eyebrow-mono}`, `{components.index-chip}`.
**Focal** wordmark at `{typography.wordmark-mega}` in `{colors.ink}`, centered, clamped to one line.
**Chrome** `{components.eyebrow-mono}` above the wordmark at top-safe; `{components.index-chip}` `00 / NN` bottom-left.
**Accent** one light-blue / dark-blue / red diagonal stripe group beneath the wordmark, offset left.
**Silence** ~72% empty.
**Fixed** wordmark centered; stripe group left-offset under focal.  **Free** the wordmark string, index count, eyebrow copy.
**Density** sparse.

### 2 · Editorial Oversized-Claim  (editorial · move: fit-to-measure hero)
**Ground** `{colors.canvas}`, padding `{spacing.framePad}`.
**Container** single-column flex, centered vertically, text-block width capped at `78cqw`.
**Composes** `{components.eyebrow-label}` (rationed — appears here), `{components.rule-hairline}`, `{components.index-chip}`.
**Focal** headline stepped by word count: `{typography.display-hero}` (≤3 words) · `{typography.display-large}` (4–6) · `{typography.section-head}` (7+), in `{colors.ink}`.
**Chrome** `{components.eyebrow-label}` above headline in `{colors.inkDim}`; `{components.rule-hairline}` between them, `22cqw` wide; `{components.index-chip}` bottom-left.
**Accent** none — spends its budget on typographic weight.
**Silence** ~65% empty.
**Fixed** headline center-anchored; eyebrow above rule.  **Free** the claim, word count, eyebrow string.
**Density** sparse.

### 3 · Focal Artifact  (focal-artifact · move: rim-lit hero)
**Ground** `{colors.canvas}`, padding `{spacing.framePad}`.
**Container** two-zone: focal media centered/upper; annotation band below.
**Composes** `{components.rim-light-bar}` (vertical variant), `{components.caption-band}`, `{components.meter-cap}`, `{components.index-chip}`.
**Focal** the artifact as a flat token-colored block bleeding to `68cqw × 68cqh` (real media substitutes at production).
**Chrome** `{components.caption-band}` low-center at `72cqw` width; `{components.index-chip}` bottom-left; a `{components.meter-cap}` marks the artifact's right edge.
**Accent** one vertical `{components.rim-light-bar}` at the artifact's right edge (light travels left→right).
**Silence** ~55% empty around the artifact.
**Fixed** rim-light on right edge; caption position.  **Free** the artifact silhouette, caption copy.
**Density** sparse.

### 4 · Spec Ledger  (data · move: dense grid with one accented cell)
**Ground** `{colors.surface}`, padding `{spacing.framePad}`.
**Container** 4-column CSS grid, column-gap `{spacing.gapWide}`, row-gap `{spacing.gap}`; section head anchors top-left with `margin-bottom: {spacing.gap}` (nowrap on the head line so a wrap cannot collide with row 1).
**Composes** `{components.ledger-cell}` × 7, `{components.ledger-cell-hero}` × 1, `{components.rule-hairline}`, `{components.eyebrow-mono}`, `{components.index-chip}`.
**Focal** the single `{components.ledger-cell-hero}`, positioned leftmost of the first row (light-source rule); stat renders `{typography.stat-hero}` in `{colors.accent}`.
**Chrome** section head at `{typography.section-head}` in `{colors.ink}`; `{components.eyebrow-mono}` above it; row of `{components.ledger-cell}` cells beneath. `{components.index-chip}` bottom-left.
**Accent** the `{components.ledger-cell-hero}` top rim + accent stat — the entire budget.
**Silence** dense-exception — the one plate that reads full.
**Fixed** hero-cell always leftmost of row 1; every cell shares construction.  **Free** the 8 label/value pairs, section head, eyebrow.
**Density** dense-exception.

### 5 · Chrome Catalog  (catalog · move: chip grid with rationed sticker)
**Ground** `{colors.canvas}`, padding `{spacing.framePad}`.
**Container** wrap-flex row of `{components.window-chip}` items, gap `{spacing.gap}`, max width `74cqw`, left-anchored (catalog is a genuine reading frame).
**Composes** `{components.window-chip}` × 6–10, `{components.sticker-mono}` × 1, `{components.eyebrow-label}`, `{components.rule-hairline}`, `{components.index-chip}`.
**Focal** the chip grid as a whole, anchored to a section head at `{typography.section-head}` in `{colors.ink}`.
**Chrome** `{components.eyebrow-label}` above the head; `{components.rule-hairline}` at `22cqw` between them; `{components.index-chip}` bottom-left.
**Accent** exactly one `{components.sticker-mono}` inline in the grid — the accent budget.
**Silence** ~58% empty (top-right quadrant reserved).
**Fixed** left-anchored; one sticker; chips share construction.  **Free** the taxonomy list, sticker copy, head string.
**Density** standard.

### 6 · Closer Lock-Off  (closer · move: paired giant blocks)
**Ground** `{colors.canvas}`, padding `{spacing.framePad}`.
**Container** centered column, gap `{spacing.gapWide}`; block row centered below.
**Composes** `{components.button-primary-giant}`, `{components.button-ghost-giant}`, `{components.rule-rim}`, `{components.index-chip}`.
**Focal** the paired giant blocks — `{components.button-primary-giant}` (accent) left, `{components.button-ghost-giant}` right.
**Chrome** short claim above the pair at `{typography.display-large}` in `{colors.ink}`, ≤ 5 words; `{components.rule-rim}` above the claim, `18cqw` wide, centered.
**Accent** the `{components.button-primary-giant}` ground + `{components.rule-rim}` share one direction — one voltage overall.
**Silence** ~68% empty.
**Fixed** primary block left of ghost; rim above claim.  **Free** claim string, block labels.
**Density** sparse.

## Do's and Don'ts

**Do**
- Compose against **one** carbon tier as ground, with `{components.rule-hairline}` marking every container edge.
- Ration the accent — one firing per frame. If a `{components.sticker-mono}` fires, the `{components.rim-light-bar}` does not.
- Lean **centered** on sparse plates (identity, oversized-claim, focal-artifact, closer). Reserve **left** for catalog/ledger; right/asymmetric as a rare tension beat.
- Vary the composition axis every consecutive frame; never repeat the same L/R split twice in a row.
- Bleed / crop the focal artifact to 68–95% of frame.
- Full-bleed on a cadence — one every 3–4 frames — as punctuation, not a default.
- One idea per frame; ≤ 2–3 distinct elements (focal + ≤ 1 kicker + ≤ 1 support).
- Keep the caption system fixed — one position, one weight, one divider across the whole deck.

**Don't**
- Don't drop a soft decorative shadow anywhere. Depth is tier + hairline + rim, never blur.
- Don't round any atom (`{rounded.chrome}` = `0`). Radius appears only on the real artifact if it has one.
- Don't let a load-bearing line drop below `{typography.legibility_floor}` (`1.4cqw`).
- Don't overlap decoration on a headline or eyebrow rail — ≥ `2cqw` keep-out.
- Don't run three tiers of surface at once as a stack.
- Don't fill the empty quadrant on a sparse plate to look complete.
- Don't split accent voltage across two elements at full strength — demote one to `{colors.ink}`.
- Don't reuse the same anchor for more than ~2 consecutive frames.
- Don't build a persistent web-nav or footer inside a frame; treatments are standalone plates.

## Aspect-Ratio Behavior

Every treatment reflows across the three ratios. Short-edge safe area is `{spacing.framePadShort}` = `5.2cqw`. No load-bearing line drops below `{typography.legibility_floor}`.

| Treatment | 16:9 (primary) | 9:16 (portrait) | 1:1 (square) |
| --- | --- | --- | --- |
| **1 · Identity Cover** | Wordmark `{typography.wordmark-mega}` centered; stripe group left-offset. | Wordmark steps to `{typography.display-hero}`; stripe group centered under mark. | Wordmark at `{typography.display-large}`; stripe group centered; eyebrow above. |
| **2 · Editorial Claim** | Fit-to-measure hero, ≤78cqw. | Text block re-caps at `78cqw` of short edge; ramp steps one size down. | Ramp steps one size down; center-anchored; rule beneath eyebrow. |
| **3 · Focal Artifact** | Artifact upper-center, caption below, rim-light right. | Artifact re-crops to `78cqw × 60cqh`; caption stacks; rim on right edge of new crop. | Artifact centered `72cqw × 72cqh`; rim-light shortens to `12cqw`. |
| **4 · Spec Ledger** | 4-column grid; hero cell top-left. | Grid reflows to 2 columns; hero cell top-left of row 1. | 3-column grid; hero cell top-left; ledger stays dense-exception. |
| **5 · Chrome Catalog** | Chip grid left-anchored under head. | Chips reflow to 2–3 per row; sticker inline; head stacks above. | Chips 3 per row; sticker inline in row 1; index-chip bottom-left. |
| **6 · Closer Lock-Off** | Paired giant blocks in a row. | Blocks stack vertically, primary above ghost; rim-rule shrinks to `24cqw` of short edge. | Blocks side-by-side but narrower; claim above; rim-rule centered. |

Re-scale display sizes per ratio so no line drops below the floor; short-edge padding is always `{spacing.framePadShort}`.

## Approved Real Entities & Numerals

Real entities and figures come **only** from the source or a downstream script; never invent.

- **Named entity:** *BMW M* (visual reference, per source; not a licensor).
- **Named fonts:** *Inter*, *JetBrains Mono*, *Noto Sans SC*.
- **Numerals authored as tokens:** every size in `{typography.*}`, spacings in `{spacing.*}`, the `1px` hairline, the `2px` rim-light, the `0px` radius, the tier hexes.

Volatile copy — product names, prices, stat values, dates, benchmarks — is a **script input** and appears as `{placeholder}` in this spec. In the showcase, volatile figures render as `— figure —` or `{token}`. Do not seed the spec with concrete numbers.

## Pre-Render Self-Audit

Run before finalizing any frame:

- **Squint** — one element dominates at 3–6× its nearest neighbor?
- **Silence** — sparse plate reads 55–75% empty? (Ledger is the named exception.)
- **Restraint** — one blue / blue / red stripe group or one white accent at full strength?
- **Weight** — display at Inter 800, body at Inter 400, no in-between weights introduced?
- **Depth** — three carbon tiers max, no soft shadow, one rim-light direction?
- **Geometry** — `{rounded.chrome}` = `0` on every atom; hairlines structural?
- **Anchor** — is this frame's anchor different from the previous two? Sparse plates centered by default?
- **Element count** — ≤ 2–3 distinct elements?
- **Floor** — every load-bearing line ≥ `1.4cqw`?
- **Fidelity** — every size referenced from a `{path.to.token}`, none invented in prose?
- **Fixed caption** — subtitles at the frozen `{components.caption-band}` position and weight?
- **Real entities** — every figure/name traceable to source or script?

## Known Gaps

- **`cqw` as string.** DESIGN.md consumers store non-atomic unit values as strings; consumers reading `{typography.wordmark-mega}.fontSize` receive `"30cqw"` and must resolve against the frame container. Intended.
- **Aspect re-scales are guidance.** The 9:16 / 1:1 rows describe reflow *direction*; exact sizes re-derive by fit-to-measure per frame.
- **Motion is directional only.** `{motion.*}` names allowed/banned gestures and a dwell floor; concrete keyframes are owned by HyperFrames.
- **Media is placeholder.** Frame Treatments describe artifact placement and crop; real footage substitutes at production. Showcase renders artifacts as flat token-colored blocks.
- **No fourth surface tier.** If a plate needs more separation than three tiers can carry, use a hairline, not a new tier.
