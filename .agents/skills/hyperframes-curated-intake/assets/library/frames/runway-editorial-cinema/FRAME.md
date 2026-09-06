---
name: "Runway editorial cinema — frame layer"
description: "Video-first companion to design.md. The frame is the unit; chrome recedes; the image carries the weight; one motivated light and one saturated point per frame."
unit: "the frame — 1920×1080 primary; 1080×1920 and 1080×1080 documented"
principle: "atoms are sacred · composition is free · numbers come from the script"

colors:
  canvas: "#000000"
  ink: "#e9ecf2"
  inkDim: "#7c838d"
  line: "#27272a"
  surface: "#1a1a1a"
  accent: "#57f2c3"

typography:
  # Reading ramp — carried from design.md; each row given its cqw equivalent (@1920).
  display:      { fontFamily: "Inter", weight: 600, fontSize: "58px", lineHeight: 1.05, tracking: "-0.02em", cqw: "3.02cqw" }
  body:         { fontFamily: "Inter", weight: 400, fontSize: "18px", lineHeight: 1.45, tracking: "0",       cqw: "0.94cqw" }
  label:        { fontFamily: "Inter", weight: 600, fontSize: "12px", lineHeight: 1.2,  tracking: "0.08em",  cqw: "0.63cqw" }
  mono:         { fontFamily: "JetBrains Mono", weight: 400, fontSize: "14px", lineHeight: 1.35, tracking: "0", cqw: "0.73cqw" }

  # Frame-native hero ramp — sizes far larger than the web reading ramp, in cqw against 1920.
  wordmark-mega:   { fontFamily: "Inter",  weight: 600, fontSize: "22cqw",  lineHeight: 0.90, tracking: "-0.04em" }
  display-hero:    { fontFamily: "Inter",  weight: 600, fontSize: "11cqw",  lineHeight: 0.98, tracking: "-0.03em" }
  display-mid:     { fontFamily: "Inter",  weight: 600, fontSize: "7.4cqw", lineHeight: 1.02, tracking: "-0.025em" }
  section-head:    { fontFamily: "Inter",  weight: 600, fontSize: "4.2cqw", lineHeight: 1.05, tracking: "-0.02em" }
  pull-quote:      { fontFamily: "Inter",  weight: 400, fontSize: "3.4cqw", lineHeight: 1.20, tracking: "-0.01em" }
  stat-numeral:    { fontFamily: "Inter",  weight: 600, fontSize: "9.5cqw", lineHeight: 0.94, tracking: "-0.03em" }
  stat-ledger:     { fontFamily: "JetBrains Mono", weight: 400, fontSize: "2.4cqw", lineHeight: 1.25, tracking: "0" }
  kicker-mono:     { fontFamily: "JetBrains Mono", weight: 400, fontSize: "0.82cqw", lineHeight: 1.30, tracking: "0.14em", textTransform: "uppercase" }
  label-caps:      { fontFamily: "Inter",  weight: 600, fontSize: "0.82cqw", lineHeight: 1.30, tracking: "0.18em", textTransform: "uppercase" }
  caption-fixed:   { fontFamily: "Inter",  weight: 400, fontSize: "1.45cqw", lineHeight: 1.40, tracking: "0" }
  meta-tag:        { fontFamily: "JetBrains Mono", weight: 400, fontSize: "0.94cqw", lineHeight: 1.30, tracking: "0.06em" }
  index-roman:     { fontFamily: "JetBrains Mono", weight: 400, fontSize: "1.05cqw", lineHeight: 1.30, tracking: "0.10em", textTransform: "uppercase" }

rounded:
  radius: "6px"      # from design.md — small, non-pill
  none:   "0px"

spacing:
  framePad:      "4.2cqw"   # source
  frame-pad:     "5vw"      # doc convention — mirrored from framePad for frame-native authoring
  gap:           "2.0cqw"
  gapTight:      "0.9cqw"
  gapWide:       "3.6cqw"
  hairline:      "1px"
  keepOut:       "2.0cqw"   # decorative keep-out from headline / eyebrow rail
  maxContainers: 2

components:
  # ── Grounds ────────────────────────────────────────────────────────────────
  ground-canvas:
    backgroundColor: "{colors.canvas}"
    textColor:       "{colors.ink}"
    padding:         "{spacing.framePad}"
  ground-surface:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink}"
    padding:         "{spacing.framePad}"
  ground-light:
    backgroundColor: "{colors.ink}"      # #e9ecf2 as an inverted band
    textColor:       "{colors.canvas}"
    padding:         "{spacing.framePad}"

  # ── Chrome atoms ───────────────────────────────────────────────────────────
  hairline-rule:
    backgroundColor: "{colors.line}"
    height:          "{spacing.hairline}"
    rounded:         "{rounded.none}"
  hairline-rule-ink:
    backgroundColor: "{colors.inkDim}"
    height:          "{spacing.hairline}"
    rounded:         "{rounded.none}"

  kicker-mono:
    typography:  "{typography.kicker-mono}"
    textColor:   "{colors.inkDim}"
  label-caps:
    typography:  "{typography.label-caps}"
    textColor:   "{colors.inkDim}"
  index-roman:
    typography:  "{typography.index-roman}"
    textColor:   "{colors.inkDim}"
  meta-tag:
    typography:  "{typography.meta-tag}"
    textColor:   "{colors.inkDim}"

  # ── The single accent — one per frame ─────────────────────────────────────
  accent-dot:
    backgroundColor: "{colors.accent}"
    size:            "0.9cqw"
    rounded:         "999px"
    shadow:          "none"          # tokens.--comp-window-dot-shadow: none
  accent-underline:
    backgroundColor: "{colors.accent}"
    height:          "0.28cqw"
    width:           "6.0cqw"

  # ── Editorial type slots (composition anchors) ────────────────────────────
  wordmark-mega:
    typography: "{typography.wordmark-mega}"
    textColor:  "{colors.ink}"
  headline-hero:
    typography: "{typography.display-hero}"
    textColor:  "{colors.ink}"
    maxWidth:   "78cqw"
  headline-mid:
    typography: "{typography.display-mid}"
    textColor:  "{colors.ink}"
    maxWidth:   "62cqw"
  section-head:
    typography: "{typography.section-head}"
    textColor:  "{colors.ink}"
  pull-quote-slab:
    typography: "{typography.pull-quote}"
    textColor:  "{colors.ink}"
    maxWidth:   "58cqw"

  # ── Caption / subtitle system (fixed position, fixed style) ───────────────
  caption-fixed:
    typography:      "{typography.caption-fixed}"
    textColor:       "{colors.ink}"
    backgroundColor: "transparent"
    padding:         "0"
    maxWidth:        "44cqw"
  credit-strip:
    typography:      "{typography.label-caps}"
    textColor:       "{colors.inkDim}"
    borderTop:       "{spacing.hairline} solid {colors.line}"
    paddingTop:      "1.0cqw"

  # ── Ledger / catalog cells (dense exception) ──────────────────────────────
  ledger-cell:
    backgroundColor: "transparent"
    borderTop:       "{spacing.hairline} solid {colors.line}"
    padding:         "1.1cqw 0"
  ledger-cell-value:
    typography:      "{typography.stat-ledger}"
    textColor:       "{colors.ink}"
  ledger-cell-label:
    typography:      "{typography.kicker-mono}"
    textColor:       "{colors.inkDim}"
  stat-numeral:
    typography:      "{typography.stat-numeral}"
    textColor:       "{colors.ink}"

  # ── Image-plate (the hero surface — "card is the image") ──────────────────
  hero-plate:
    backgroundColor: "{colors.surface}"    # placeholder ground when no imagery
    textColor:       "{colors.ink}"
    rounded:         "{rounded.radius}"
    borderTop:       "{spacing.hairline} solid {colors.line}"
    shadow:          "none"                # depth ceiling — no interface glow
  hero-plate-bleed:
    backgroundColor: "{colors.surface}"
    rounded:         "{rounded.none}"      # full-bleed variant — no radius when frame owns edge
    shadow:          "none"

  # ── Frame-scale variants of small chrome (giant) ──────────────────────────
  label-caps-giant:
    typography:      { fontFamily: "Inter", weight: 600, fontSize: "1.6cqw", lineHeight: 1.20, tracking: "0.22em", textTransform: "uppercase" }
    textColor:       "{colors.ink}"
  index-roman-giant:
    typography:      { fontFamily: "JetBrains Mono", weight: 400, fontSize: "2.2cqw", lineHeight: 1.20, tracking: "0.12em", textTransform: "uppercase" }
    textColor:       "{colors.inkDim}"
---

# Runway editorial cinema — frame layer

## 风格速览 / Style Snapshot

- **感觉 / Mood:** 极简编辑电影感——界面退后，影像和一个清晰观点站到前面。Minimal editorial cinema: the interface recedes so imagery and one clear idea can lead.
- **最适合 / Best for:** AI、创意工具、影像产品、未来工作流、设计技术和克制的产品发布。AI, creative tools, imaging products, future workflows, design technology, and restrained product launches.
- **视觉签名 / Signature:** 纯黑底、冷白字、薄荷绿单点、巨型字标、电影式满幅影像和固定字幕系统。Black ground, cool-white type, one mint accent, mega wordmarks, cinematic full-bleed imagery, and a fixed caption system.
- **避免 / Avoid:** 多彩儿童向、电商大促、每个元素都动和界面发光，会破坏“静态 chrome、动态影像”的核心。Colorful children's work, sales promos, animating every element, and glowing UI break its “still chrome, moving image” core.

> **Atoms are sacred · composition is free · numbers come from the script.**

## Overview

Runway at frame scale is **image-led editorial cinema in cold monochrome**. The frame is dark by default, chrome is invisible, and one motivated light source lives inside the image itself (a window, a screen, a lamp, a neon). The interface layer never lights. Editorial rhythm comes from **band-swap**: continuous dark, then a beat of light band, then dark again — never gradients between them. Weight and hierarchy are carried by **tight negative-tracked display type**, not by scale contests; the size ratio across the ramp stays close to `1 : 0.5 : 0.33 : 0.23`, and the top of the ramp gets its punch from tracking and leading, not from a shouted headline. Fonts are Inter (Latin sans, display + body + label) and JetBrains Mono (technical voice, timecodes, ledgers, tags).

**Frame Craft Bar** — every frame passes these three eyeball tests before any structural check:

- **Squint test.** Exactly one element dominates: the hero image, the wordmark, the numeral, the quote slab. Its scale is **3–6×** the nearest neighbor. A chasm, not a ramp.
- **Silence test.** Sparse frames (cover, oversized-claim, focal-artifact, closer) read **55–75% empty.** Never fill silence to look complete — the emptiness is the direction's confidence. **The one named density exception is the data-ledger plate.**
- **Restraint test.** The brand's scarce elements each fire **once per frame at most**: one motivated light, one saturated accent point ({components.accent-dot} or {components.accent-underline}, never both at full strength), one band. If it appears twice, demote one.
- **Reference bar.** Aim: the opening credits of a Denis Villeneuve title card; a Criterion menu still; a Fabien Baron editorial spread. Failure looks like a SaaS marketing page with a mint accent — even chrome, even margins, headline-left, illustration-right.

## Colors

Tokens carried verbatim from `design.md`. The reframing is behavioral: at frame scale, color is **ground first**, and the accent is **rationed to a point**.

- **{colors.canvas} `#000000`** — the default frame ground. Continuous dark bands run 2 frames at most before a beat.
- **{colors.surface} `#1a1a1a`** — the plate: hero image-plate stand-in, ledger container, quiet inset. Never used as a frame ground on its own; it lives *inside* the canvas.
- **{colors.line} `#27272a`** — the only permitted hairline. Depth is *not* shadow; it is the hairline between planes. `1px`, never thicker.
- **{colors.ink} `#e9ecf2`** — display and body ink on dark, and the **inverted light band** ground (as {components.ground-light}) when the edit calls for a beat of light.
- **{colors.inkDim} `#7c838d`** — chrome-only: kickers, meta tags, credits, ledger labels. Never load-bearing.
- **{colors.accent} `#57f2c3`** — the one saturated point in a frame of monochrome. Appears as **a dot, a hairline underline, or a single glyph** — never a fill, never a two-tone gradient, never twice in one frame at full voltage.

**Per-frame color rule.** A frame is one ground + one accent placement + optionally one plate. If a frame has surface, canvas, and a light band all at full presence, delete one.

## Typography

Two ramps live in the frontmatter. The reading ramp preserves the source hierarchy at `1 : 0.5 : 0.33 : 0.23`, given both in px (for reference) and cqw (for authoring). The **hero ramp** is frame-native — it exists only because the frame demands sizes the web ramp doesn't reach.

- **Reading ramp** — {typography.display}, {typography.body}, {typography.label}, {typography.mono}. Used for caption strips, ledger values, credit rails, meta tags.
- **Hero ramp** — {typography.wordmark-mega} (22cqw, the identity plate only), {typography.display-hero} (11cqw), {typography.display-mid} (7.4cqw), {typography.section-head} (4.2cqw), {typography.pull-quote} (3.4cqw), {typography.stat-numeral} (9.5cqw). All carry tight negative tracking (−0.02em to −0.04em) and line-heights 0.90–1.05: the "film title card" density.
- **Fit-to-measure headlines.** Text block capped at **≤ 78cqw wide**. Step the hero ramp by word count: **≤ 3 words → {typography.display-hero}**; **4–6 → {typography.display-mid}**; **7+ → {typography.section-head}**. A fixed hero size on a long line blows out edge-to-edge and reads as a screaming slide.
- **Legibility floor: 1.4cqw** (≈ 27px @ 1920). Any line below that floor is chrome/colophon (kickers, meta, credits) and may never carry a beat's meaning.

## Layout — The Frame

- **Primary:** 1920 × 1080 (16:9). Also documented: 1080 × 1920 (9:16) and 1080 × 1080 (1:1).
- **Safe area:** {spacing.framePad} = 4.2cqw from every edge on 16:9. On 9:16 and 1:1, use the **short edge** to derive safe pad — never the long one.
- **The vw law.** All frame-relative sizing is authored in **cqw**, resolved against the frame container (not the viewport). Conversion: `px ÷ 1920 × 100 = cqw`. Fixed px is reserved for true chrome atoms: hairline (`1px`), radius (`6px`), micro shadows (`none`).
- **cqw note.** The DESIGN.md spec's consumer table tolerates `cqw` as a stored string; frame.md is the intended consumer. See Known Gaps.
- **Two-container ceiling.** At most two information containers per frame ({spacing.maxContainers}). A third relationship is carried by **spatial grouping, direct annotation, or shared light** — never by a third card.
- **Anchor:** the default is **centered** for identity, oversized-claim, focal-artifact, and closer plates. Reserve left-anchor for genuine reading/editorial and catalog frames. No more than ~2 consecutive frames share an anchor.

## Elevation & Depth

- **Depth ceiling: none.** `--comp-window-dot-shadow`, `--comp-meter-cap-shadow`, `--comp-sticker-shadow` are all `none`. The interface layer has zero shadow, zero glow, zero decorative border.
- **What depth exists** comes from the *image* — the motivated light source, the fall-off, the plane crossing. A plate against canvas is separated by a **1px hairline** ({components.hairline-rule}), never by a drop shadow.
- **Banned.** Interface glow, colored soft-light layers, gradients across a card, multi-color rims. If the frame wants "punch," it gets it from cropping harder or making the ground darker — never from lighting the chrome.

## Shapes

- **Radius: {rounded.radius} = 6px.** Small, editorial, non-pill. Applies to plates and inset chrome only.
- **Full-bleed variant:** {components.hero-plate-bleed} — when a plate owns the frame edge, radius drops to 0. A rounded corner touching a frame edge is a rendering bug.
- **CTA geometry.** This preset has no marketing CTA. If one is required, it is a **label-caps line + underline hairline** ({components.label-caps} + {components.accent-underline}), never a pill.

## Components

Every buildable unit lives in the frontmatter as a structured component token. The prose here is intent + when-to-use + non-token construction. **Do not re-list resolved values in prose** — the frontmatter is the single source of truth.

- **Grounds** — {components.ground-canvas} is the default frame ground. {components.ground-surface} is a quiet inset only, never the frame edge. {components.ground-light} is the inverted band beat: light frames come only from this token, never by dimming canvas.
- **Chrome atoms** — {components.hairline-rule} is the only depth device. {components.kicker-mono} (JetBrains Mono, uppercase, wide-tracked) opens a section rail; {components.label-caps} is its Inter twin for eyebrow use; {components.index-roman} numbers editorial sequences (I · II · III). {components.meta-tag} carries a filename, a timecode, an ISO date.
- **Accent** — {components.accent-dot} and {components.accent-underline} share a budget of *one voltage per frame*. If a dot is on-frame, the underline is off; if the underline is present, the dot is off. Never both at full strength.
- **Editorial slots** — {components.wordmark-mega} is the identity plate only, appears once in a sequence. {components.headline-hero} and {components.headline-mid} are the oversized-claim slots (choose by word count, per the fit-to-measure rule above). {components.section-head} opens a chaptered frame. {components.pull-quote-slab} carries verbatim source language.
- **Caption system** — {components.caption-fixed} is a **fixed system**: same position (lower-left of the frame, inside the safe pad), same size, same weight, throughout a sequence. Do not restyle it per frame. {components.credit-strip} runs a single hairline above the credit line at the frame's lower edge, inside safe pad.
- **Ledger cells** — {components.ledger-cell} is a row: top hairline, {components.ledger-cell-value} in mono, {components.ledger-cell-label} in kicker-mono. Rows stack vertically inside a two-column ledger. This is the density exception.
- **Numeral** — {components.stat-numeral} is a single load-bearing figure; it is the entire silence of a stat frame.
- **Hero plate** — {components.hero-plate} is a stand-in for the image ("card is the image"): a #1a1a1a surface with a 1px top hairline and 6px radius, ready to receive imagery. {components.hero-plate-bleed} is its edge-owning variant.
- **Frame-scale variants** — {components.label-caps-giant} and {components.index-roman-giant} exist when chrome must be legible against a mega wordmark and cannot use the base sizes without disappearing.

Any construction the tokens can't hold (per-instance placement, which quadrant the caption sits in, which corner the accent dot occupies) is specified in **Frame Treatments**, not here.

## Motion & Timing

The brand's motion character is **still chrome, moving image**. The interface layer does not animate. The image within may reveal through **physical weight** (a subject entering frame) or **continuous camera travel** (a slow dolly, a track). Cuts between frames are **hard cuts on band changes** (dark → light → dark), never dissolves.

- **May animate:** the image inside {components.hero-plate}; the light source inside the image; a subject entering or leaving frame.
- **Must not animate:** kickers, labels, meta tags, hairlines, credit strip, accent dot (it appears, it does not pulse), wordmark tracking (do not "kern in" the identity).
- **Dwell.** Density drives pace, not the other way around: a sparse cover holds longer than a ledger. HyperFrames owns the actual timeline values — this spec sets only the *shape* of the beat.
- **Export.** Every frame must pass a still test at 25% scale: the hero is legible, the accent point is countable, and no chrome floats.

## Frame Treatments

Seven recipe plates. Each **composes** frontmatter components and specifies only ground, container, focal placement, chrome position, accent placement, silence, and Fixed/Free.

### 1 · Identity Card  (identity/cover · move: mega wordmark centered on canvas, single accent dot upper-right, credit strip at lower edge)
**Ground** {components.ground-canvas}, padding: {spacing.framePad}.
**Container** flex, column, justify: center, align: center; gap: {spacing.gapWide}.
**Composes** {components.wordmark-mega}, {components.accent-dot}, {components.kicker-mono}, {components.credit-strip}.
**Focal** {components.wordmark-mega}: font-size 22cqw, centered horizontally, optical-center vertically (≈ 46cqh from top).
**Chrome** {components.kicker-mono} above the wordmark ({spacing.gapWide} above); {components.credit-strip} pinned {spacing.framePad} from left/right and bottom edges.
**Accent** one {components.accent-dot} at (x: 100cqw − {spacing.framePad}, y: {spacing.framePad}) — upper-right, inside safe pad.
**Silence** ~72% empty. Nothing lives in the left or right thirds beyond the wordmark's own bounds.
**Fixed** wordmark tracking, accent-dot size and position, credit-strip position.  **Free** the wordmark string (from the script), the credit line copy.
**Pace** low.

### 2 · Oversized Claim  (editorial/oversized-claim · move: tight display headline anchored bottom-left, kicker above, upper 60% of frame is empty canvas)
**Ground** {components.ground-canvas}, padding: {spacing.framePad}.
**Container** flex, column, justify: flex-end, align: flex-start; gap: {spacing.gap}.
**Composes** {components.headline-hero} (or {components.headline-mid} / {components.section-head} per word count), {components.kicker-mono}, {components.accent-underline}.
**Focal** {components.headline-hero}: size from ramp by word count, max-width 78cqw, anchor bottom-left inside safe pad.
**Chrome** {components.kicker-mono} 2.4cqw above the headline, left-aligned to it.
**Accent** one {components.accent-underline} directly under the headline's last line, 6cqw long, aligned to the headline's left edge.
**Silence** ~65% empty — the top of the frame is untouched canvas.
**Fixed** anchor, kicker position, accent-underline geometry.  **Free** the headline text (word count picks the ramp step), the kicker string.
**Pace** moderate.

### 3 · Focal Artifact  (focal-artifact · move: full-bleed hero image-plate with fixed lower-left caption, one accent dot at plate corner)
**Ground** {components.ground-canvas}, padding: 0 (the plate owns the frame edges).
**Container** relative; {components.hero-plate-bleed} inset: 0 (fills the frame); overlays are `position:absolute` inside the safe pad.
**Composes** {components.hero-plate-bleed}, {components.caption-fixed}, {components.accent-dot}, {components.meta-tag}.
**Focal** {components.hero-plate-bleed}: 100cqw × 100cqh, radius 0, one motivated light inside the image.
**Chrome** {components.caption-fixed} bottom-left, inset {spacing.framePad} from left and bottom edges, max-width 44cqw; {components.meta-tag} top-left, inset {spacing.framePad} from top and left edges.
**Accent** one {components.accent-dot} at the plate's inner upper-right ({spacing.framePad} inset).
**Silence** the frame is dense with image, but ~78% of the chrome layer is empty; captions never overlap the light source.
**Fixed** caption position, meta-tag position, accent-dot position, plate bleed.  **Free** the image, the caption copy, the meta-tag string.
**Pace** moderate.

### 4 · Ledger  (data/ledger · move: two-column mono ledger, hairline-ruled rows, section head anchored top-left — the density exception)
**Ground** {components.ground-canvas}, padding: {spacing.framePad}.
**Container** grid, 12 columns, gap {spacing.gap}. Section head spans cols 1–8, row 1. Ledger occupies cols 1–6 and cols 7–12, rows 2–N.
**Composes** {components.section-head}, {components.ledger-cell} × N, {components.ledger-cell-value}, {components.ledger-cell-label}, {components.index-roman}, {components.hairline-rule}.
**Focal** {components.section-head}: 4.2cqw, upper-left, single line (max 32 characters or step down).
**Chrome** {components.index-roman} above the section head; two columns of {components.ledger-cell}, each row with {components.ledger-cell-label} left, {components.ledger-cell-value} right.
**Accent** one {components.accent-underline} beneath the section-head — the only accent in a dense frame.
**Silence** tight by design — the density exception. Rows may fill 6–10 slots; whitespace lives in the column gutter (2cqw) and the outer safe pad.
**Fixed** two-column ratio, hairline weight, section-head to first-row clearance (≥ 2.4cqw so a wrapped head can't collide).  **Free** the row values, the row labels, the number of rows (6–10).
**Pace** high.

### 5 · Pull Quote  (brand-signature · move: verbatim quote slab centered mid-frame, source attribution on a credit strip below)
**Ground** {components.ground-canvas}, padding: {spacing.framePad}.
**Container** flex, column, justify: center, align: center; gap: {spacing.gap}.
**Composes** {components.pull-quote-slab}, {components.credit-strip}, {components.accent-underline}.
**Focal** {components.pull-quote-slab}: 3.4cqw, max-width 58cqw, centered.
**Chrome** {components.credit-strip} pinned {spacing.framePad} from lower edge, ≤ 44cqw wide, left-aligned within a centered block.
**Accent** one {components.accent-underline} between the quote and the credit strip, 6cqw, centered.
**Silence** ~68% empty. The quote sits in a chasm — the top and side thirds are untouched canvas.
**Fixed** quote centering, accent between quote and credit, credit-strip typography.  **Free** the quote text, the source attribution.
**Pace** low.

### 6 · Chapter Card  (chrome/catalog · move: light-band inversion, roman index left, section head right, single hairline dividing the frame)
**Ground** {components.ground-light}, padding: {spacing.framePad}.
**Container** flex, row, justify: space-between, align: center; gap: {spacing.gapWide}. A single {components.hairline-rule-ink} divides the frame at mid-height.
**Composes** {components.ground-light}, {components.index-roman-giant}, {components.section-head}, {components.hairline-rule-ink}, {components.label-caps}.
**Focal** {components.section-head} on the right, ink = canvas (#000000), max-width 62cqw.
**Chrome** {components.index-roman-giant} on the left (mono roman numeral); {components.label-caps} above the section head, wide-tracked, ink #7c838d.
**Accent** none — this is the light-band beat; the accent budget is deliberately zero here so the band inversion carries the change.
**Silence** ~60% empty. The horizontal hairline splits the frame; type sits above the rule, empty light sits below.
**Fixed** ground inversion, hairline geometry, no-accent rule.  **Free** the numeral, the section title, the eyebrow label.
**Pace** moderate.

### 7 · Closer  (identity/cover · move: single accent dot centered on canvas, tiny caption below — the credits-roll beat)
**Ground** {components.ground-canvas}, padding: {spacing.framePad}.
**Container** flex, column, justify: center, align: center; gap: {spacing.gapWide}.
**Composes** {components.accent-dot}, {components.caption-fixed}, {components.kicker-mono}.
**Focal** {components.accent-dot} centered horizontally, at optical-center vertically. This is the only frame where the dot is the focal element.
**Chrome** {components.caption-fixed} directly below the dot ({spacing.gapWide} below), centered, max-width 44cqw. {components.kicker-mono} at the frame's lower-left inside safe pad.
**Accent** the dot IS the accent — its budget is spent as the focal, no additional voltage.
**Silence** ~85% empty. This is the sparsest frame in the set.
**Fixed** dot centering, caption centering, dot size (0.9cqw — do not scale up).  **Free** the caption line, the kicker string.
**Pace** low.

## Do's and Don'ts

**Do**
- Center the focal on identity, oversized-claim, focal-artifact, closer, and pull-quote plates. Vary anchor to left only for editorial and ledger.
- One motivated light per image. One accent voltage per frame. One ground per frame.
- Break density into more frames rather than packing a slide. Two thoughts = two frames.
- Bleed the hero image to the frame edge (radius 0 via {components.hero-plate-bleed}) as a cadence tool, not a default.
- Use the caption as a **system**: same position, same style, throughout a sequence.

**Don't**
- Don't stack accent dot + accent underline in the same frame at full strength. Demote one.
- Don't put a shadow, glow, or gradient on the interface layer — ever. Depth is hairline, not fog.
- Don't run more than two consecutive dark bands without a light-band beat (Chapter Card).
- Don't run a top-left kicker on every frame; ration it. It is a chrome atom, not a template.
- Don't let a decorative element cross the headline bounding box or eyebrow rail ({spacing.keepOut} = 2cqw keep-out).
- Don't turn the wordmark into a headline. It appears once, as identity.

## Aspect-Ratio Behavior

| Treatment            | 16:9 (primary)                          | 9:16 (portrait)                                              | 1:1 (square)                                              |
|---                   |---                                      |---                                                           |---                                                        |
| 1 · Identity Card    | Wordmark 22cqw centered, dot upper-R.   | Wordmark drops to display-hero (11cqw) to fit width; stacks vertically; dot moves to lower-R.| Wordmark drops to display-mid (7.4cqw); dot inline right of wordmark. |
| 2 · Oversized Claim  | Headline bottom-left, ramp by words.    | Headline anchors bottom, full 78cqw of short edge; kicker above.| Headline centered; underline centered; upper 40% empty. |
| 3 · Focal Artifact   | Plate 100×100; caption lower-L; meta upper-L. | Plate 100×100; caption bottom (single line, ≤ 78cqw); meta top-L. | Plate 100×100; caption lower-L; meta upper-L (tight). |
| 4 · Ledger           | Two columns, 6–10 rows.                 | **One column**, rows stack; section head spans full width; row count drops to 5–7. | Two columns preserved; row count capped at 5; column gap compresses to {spacing.gap}. |
| 5 · Pull Quote       | Quote centered, credit below.           | Quote centered; max-width relaxes to 78cqw of short edge; credit below. | Quote centered; max-width 62cqw; credit below. |
| 6 · Chapter Card     | Index left, section head right, hairline mid. | Index top, section head bottom; hairline becomes horizontal split at 40cqh. | Index top-L, section head bottom-R; hairline horizontal mid. |
| 7 · Closer           | Dot centered, caption below.            | Dot centered, caption below (short). | Dot centered, caption below. |

Safe pad ({spacing.framePad} on 16:9) is re-derived from the **short edge** on 9:16 and 1:1. Load-bearing type must never drop below the 1.4cqw floor after a ratio change.

## Approved Real Entities & Numerals

- Entities named in `design.md` and its preserved source (Runway, runwayml.com; VoltAgent / awesome-design-md attribution; Inter, JetBrains Mono, Noto Sans SC as licensed local fonts) may be used verbatim in a frame when the beat requires them.
- **Numerals come from the script, not from this spec.** Ledger values, dates, timecodes, filenames, and figures are supplied per-frame by the caller. Placeholders in the showcase read `— figure —`, `{price}`, `{timecode}`.
- Do not invent third-party marks, statistics, or logos. If a figure isn't in the script, the ledger row does not exist.

## Pre-Render Self-Audit

Run all before finalizing any frame:

- **Squint** — one element dominates; nearest neighbor is 3–6× smaller. ✓/✗
- **Silence** — sparse plates read 55–75% empty; only the Ledger is exempt. ✓/✗
- **Voltage** — exactly one accent placement fires at full strength (dot OR underline OR none — never both). ✓/✗
- **Depth** — no shadows, no glows, no gradients on chrome. Depth is hairline only. ✓/✗
- **Weight** — hero text tracks negative (−0.02em to −0.04em); line-height 0.90–1.05. ✓/✗
- **Geometry** — radius is 6px for insets, 0 for bleeds; no rounded corner touches a frame edge. ✓/✗
- **Anchor** — centered by default for identity/claim/artifact/closer; anchor varies across the sequence (≤ 2 consecutive share). ✓/✗
- **Element count** — ≤ 2–3 distinct elements per frame (focal + kicker + at most one support/accent). Ledger is the exception. ✓/✗
- **Fit-to-measure** — headline size chosen from the ramp by word count; text block ≤ 78cqw; no line touches the safe margin. ✓/✗
- **Floor** — no load-bearing line below 1.4cqw. ✓/✗
- **Band cadence** — no more than 2 consecutive dark bands without a light beat. ✓/✗
- **25% test** — hero legible at 25% zoom; accent point countable; chrome does not float. ✓/✗

## Known Gaps

- **`cqw` as string.** The DESIGN.md spec's consumer-behavior table stores extension units as opaque strings; frame.md is the intended consumer and treats `cqw` as a first-class authoring unit, resolved against the frame container. Downstream tools that do not understand `cqw` must preserve it verbatim. The `spacing.frame-pad: 5vw` entry is a doc convention and is stored as a string; `spacing.framePad: 4.2cqw` is the operative safe-pad token.
- **Aspect-ratio behavior is guidance.** The 9:16 and 1:1 columns describe *reflow intent*; a treatment reflowed under duress may need a bespoke pass. When in doubt, hold the short edge, re-derive safe pad, and preserve the anchor described in the 16:9 column.
- **Motion timing is out of scope.** This spec sets the *shape* of the beat (what may animate, what must not, cut grammar, dwell shape). HyperFrames owns the numeric timeline.
- **Derived sections.** Motion & Timing, Frame Treatments, Aspect-Ratio Behavior, and Pre-Render Self-Audit are video-first derivations. `design.md` remains the source of truth for atoms.
