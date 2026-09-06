---
version: alpha
name: Dell 1996 · Frame Layer
description: Video-first companion to design.md — the Dell December 1996 catalog-era brand reframed for 1920×1080 storyboards. Atoms are carried verbatim (every hex, weight, radius, and font); composition is re-scored so the literal black page frame, ribbon-card ground blocks, chunky Arial Black display, Times Roman body, and hand-cut GIF stickers become frame-scale moves. Dell red stays rationed to CTA + phone callout; the eight tint palette becomes the sequence's color rotation.

colors:
  # ─── Carried verbatim from design.md ───
  primary: "#e91d2a"
  on-primary: "#ffffff"
  canvas: "#ffffff"
  surface: "#ffffff"
  ink: "#000000"
  frame-ink: "#000000"
  yellow-sticker: "#fcc20f"
  purple-stripe: "#6a26a4"
  link: "#0000ee"

  # Ribbon-card tint family (one per product line)
  tint-olive: "#8e8a25"
  tint-sage: "#b3bd95"
  tint-salmon: "#d77a7a"
  tint-peach: "#e6915d"
  tint-lime: "#c0d4a7"
  tint-sky: "#9ab6c8"
  tint-steel: "#a5b8c0"
  tint-periwinkle: "#8c9ae0"

typography:
  # ─── Reading ramp (from design.md, px preserved) ───
  display:
    fontFamily: Arial Black
    fontSize: 36px
    fontWeight: 900
    lineHeight: 1.0
    letterSpacing: 0
  heading-1:
    fontFamily: Arial Black
    fontSize: 24px
    fontWeight: 900
    lineHeight: 1.05
    letterSpacing: 0
  heading-2:
    fontFamily: Helvetica
    fontSize: 16px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: 0
  heading-3:
    fontFamily: Helvetica
    fontSize: 14px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: 0
  body:
    fontFamily: Times New Roman
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  body-sm:
    fontFamily: Times New Roman
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  caption:
    fontFamily: Times New Roman
    fontSize: 11px
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: 0
  button:
    fontFamily: Helvetica
    fontSize: 12px
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: 0
  link:
    fontFamily: Times New Roman
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
  ui-label:
    fontFamily: Helvetica
    fontSize: 12px
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: 0

  # ─── Display / hero ramp (frame-native, vw against 1920) ───
  wordmark-mega:
    fontFamily: Arial Black
    fontSize: 30vw
    fontWeight: 900
    lineHeight: 0.84
    letterSpacing: -1.4vw
  display-hero:
    fontFamily: Arial Black
    fontSize: 14vw
    fontWeight: 900
    lineHeight: 0.9
    letterSpacing: -0.3vw
  claim-mid:
    fontFamily: Arial Black
    fontSize: 8vw
    fontWeight: 900
    lineHeight: 0.95
    letterSpacing: -0.15vw
  section-head:
    fontFamily: Arial Black
    fontSize: 4.2vw
    fontWeight: 900
    lineHeight: 1.0
    letterSpacing: 0
  ribbon-title-giant:
    fontFamily: Helvetica
    fontSize: 3vw
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: 0
  stat-mega:
    fontFamily: Arial Black
    fontSize: 12vw
    fontWeight: 900
    lineHeight: 0.9
    letterSpacing: -0.2vw
  stat-ledger:
    fontFamily: Arial Black
    fontSize: 3.6vw
    fontWeight: 900
    lineHeight: 1.0
    letterSpacing: 0
  body-frame:
    fontFamily: Times New Roman
    fontSize: 1.7vw
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: 0
  ui-label-frame:
    fontFamily: Helvetica
    fontSize: 1.5vw
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: 0
  sticker-giant:
    fontFamily: Helvetica
    fontSize: 2.2vw
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: 0
  phone-mega:
    fontFamily: Helvetica
    fontSize: 5.5vw
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: 0
  caption-frame:
    fontFamily: Times New Roman
    fontSize: 1.4vw
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: 0

rounded:
  none: 0px
  full: 9999px

spacing:
  xxs: 2px
  xs: 4px
  s: 6px
  sm: 8px
  m: 10px
  md: 12px
  lg: 16px
  xl: 20px
  xxl: 24px
  section-sm: 32px
  section: 40px
  section-lg: 48px
  frame-pad: 5vw
  frame-pad-tight: 3vw
  frame-gutter: 2vw

components:
  # ─── Carried verbatim from design.md ───
  page-frame:
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.canvas}"
    rounded: "{rounded.none}"
    padding: 8px
  top-banner:
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.canvas}"
    typography: "{typography.heading-2}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  section-eyebrow-olive:
    backgroundColor: "{colors.tint-olive}"
    textColor: "{colors.ink}"
    typography: "{typography.display}"
    rounded: "{rounded.none}"
    padding: 24px 16px
  section-eyebrow-salmon:
    backgroundColor: "{colors.tint-salmon}"
    textColor: "{colors.ink}"
    typography: "{typography.display}"
    rounded: "{rounded.none}"
    padding: 24px 16px
  ribbon-card-title:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.heading-3}"
    rounded: "{rounded.none}"
    padding: 6px 12px
  ribbon-card-body-sage:
    backgroundColor: "{colors.tint-sage}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  ribbon-card-body-salmon:
    backgroundColor: "{colors.tint-salmon}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  ribbon-card-body-peach:
    backgroundColor: "{colors.tint-peach}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  ribbon-card-body-lime:
    backgroundColor: "{colors.tint-lime}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  ribbon-card-body-sky:
    backgroundColor: "{colors.tint-sky}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  ribbon-card-body-steel:
    backgroundColor: "{colors.tint-steel}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  ribbon-card-body-periwinkle:
    backgroundColor: "{colors.tint-periwinkle}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 12px 16px
  cta-block-red:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 16px
  phone-callout:
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.primary}"
    typography: "{typography.heading-2}"
    rounded: "{rounded.none}"
    padding: 4px 8px
  buy-a-dell-sticker:
    backgroundColor: "{colors.yellow-sticker}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: 4px 8px
  new-burst-sticker:
    backgroundColor: "{colors.yellow-sticker}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: 4px 8px
  cert-seal:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.canvas}"
    typography: "{typography.button}"
    rounded: "{rounded.full}"
    size: 64px
  icon-label-nav:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.ui-label}"
    rounded: "{rounded.none}"
    padding: 8px
  text-input:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: 4px 6px
  button-primary:
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.on-primary}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: 6px 16px
  button-secondary:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: 6px 16px
  button-text-link:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.link}"
    typography: "{typography.link}"
    rounded: "{rounded.none}"
  footer-band:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-sm}"
    padding: 16px

  # ─── Frame-scale variants (new, added for video) ───
  page-frame-giant:
    description: "The literal black picture frame around every video frame — the brand's single most identifiable chrome, held at frame scale."
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.canvas}"
    rounded: "{rounded.none}"
    padding: 1vw
  top-banner-frame:
    description: "Black establishing strip across the top of a frame; carries wordmark, sub-tagline, and stickers at frame scale."
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.canvas}"
    typography: "{typography.section-head}"
    rounded: "{rounded.none}"
    padding: 1.5vw 2vw
  section-eyebrow-giant-olive:
    description: "Frame-scale color eyebrow block — full-frame or full-band ground fill for oversized-claim frames."
    backgroundColor: "{colors.tint-olive}"
    textColor: "{colors.ink}"
    typography: "{typography.display-hero}"
    rounded: "{rounded.none}"
    padding: 4vw 5vw
  section-eyebrow-giant-salmon:
    description: "Salmon frame-scale eyebrow ground — same chrome as olive."
    backgroundColor: "{colors.tint-salmon}"
    textColor: "{colors.ink}"
    typography: "{typography.display-hero}"
    rounded: "{rounded.none}"
    padding: 4vw 5vw
  section-eyebrow-giant-periwinkle:
    description: "Periwinkle frame-scale eyebrow ground — same chrome, rotates color per beat."
    backgroundColor: "{colors.tint-periwinkle}"
    textColor: "{colors.ink}"
    typography: "{typography.display-hero}"
    rounded: "{rounded.none}"
    padding: 4vw 5vw
  ribbon-card-title-giant:
    description: "White horizontal title bar for frame-scale ribbon cards — Helvetica Bold all-caps product name, 1px black bottom border."
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.ribbon-title-giant}"
    rounded: "{rounded.none}"
    padding: 0.9vw 1.6vw
  ribbon-card-body-giant-sage:
    description: "Frame-scale sage ribbon body — Latitude family."
    backgroundColor: "{colors.tint-sage}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  ribbon-card-body-giant-salmon:
    description: "Frame-scale salmon ribbon body — OptiPlex GX family."
    backgroundColor: "{colors.tint-salmon}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  ribbon-card-body-giant-peach:
    description: "Frame-scale peach ribbon body — Dimension / OptiPlex Gs."
    backgroundColor: "{colors.tint-peach}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  ribbon-card-body-giant-lime:
    description: "Frame-scale lime ribbon body — OptiPlex G Series."
    backgroundColor: "{colors.tint-lime}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  ribbon-card-body-giant-sky:
    description: "Frame-scale sky ribbon body — Dellware."
    backgroundColor: "{colors.tint-sky}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  ribbon-card-body-giant-steel:
    description: "Frame-scale steel ribbon body — Dimension XPS Pro."
    backgroundColor: "{colors.tint-steel}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  ribbon-card-body-giant-periwinkle:
    description: "Frame-scale periwinkle ribbon body — PowerEdge."
    backgroundColor: "{colors.tint-periwinkle}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  ribbon-card-body-giant-olive:
    description: "Frame-scale olive ribbon body — Dimension Desktops eyebrow-tinted family."
    backgroundColor: "{colors.tint-olive}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.4vw 1.8vw
  cta-block-red-giant:
    description: "Frame-scale Dell-red CTA ground — the singular attention pole. One per frame, one frame per sequence."
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 3vw 4vw
  phone-callout-giant:
    description: "Frame-scale phone number: red on black, Helvetica Bold. Focal on the closer, chrome on the top banner."
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.primary}"
    typography: "{typography.phone-mega}"
    rounded: "{rounded.none}"
    padding: 0.6vw 1.2vw
  buy-a-dell-sticker-giant:
    description: "Frame-scale yellow BUY-a-DELL sticker with 1px black border; pinned top-right chrome atom."
    backgroundColor: "{colors.yellow-sticker}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.sticker-giant}"
    rounded: "{rounded.none}"
    padding: 0.6vw 1.2vw
  new-burst-sticker-giant:
    description: "Frame-scale NEW! burst — yellow sticker, ~12° rotation, pinned over a ribbon card's right edge as the single accent."
    backgroundColor: "{colors.yellow-sticker}"
    textColor: "{colors.ink}"
    typography: "{typography.sticker-giant}"
    rounded: "{rounded.none}"
    padding: 0.6vw 1.2vw
  cert-seal-giant:
    description: "Frame-scale round PC Magazine Readers' Choice seal — Dell red disc, white type, held on the right rail."
    backgroundColor: "{colors.primary}"
    textColor: "{colors.canvas}"
    typography: "{typography.ui-label-frame}"
    rounded: "{rounded.full}"
    size: 14vw
  button-primary-giant:
    description: "Frame-scale black filled button — used inside CTA plates and closer frames."
    backgroundColor: "{colors.frame-ink}"
    textColor: "{colors.on-primary}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.sticker-giant}"
    rounded: "{rounded.none}"
    padding: 1vw 2.2vw
  ledger-row:
    description: "Frame-scale spec-ledger row: white ground with hairline black divider between rows; header cell reads in caps."
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame-ink}"
    typography: "{typography.body-frame}"
    rounded: "{rounded.none}"
    padding: 1.2vw 1.6vw
  icon-label-nav-giant:
    description: "Frame-scale footer/nav icon-label pair — Helvetica Bold caps label under a hand-drawn icon slug."
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.ui-label-frame}"
    rounded: "{rounded.none}"
    padding: 1vw

---

# Dell 1996 — Frame (video / frame layer)

## 风格速览 / Style Snapshot

- **感觉 / Mood:** 1996 年电脑目录与早期网页的快乐复古，笨拙得真诚，也因此很有记忆点。Joyful 1996 computer-catalog and early-web nostalgia—awkward, sincere, and memorable.
- **最适合 / Best for:** 怀旧科技、互联网文化、品牌历史、趣味产品故事和反精致叙事。Retro technology, internet culture, brand history, playful product stories, and intentionally anti-polished narratives.
- **视觉签名 / Signature:** 黑色页面外框、彩色 ribbon cards、Arial Black、Times、GIF 贴纸与稀缺 Dell 红。A black page frame, tinted ribbon cards, Arial Black, Times, GIF stickers, and scarce Dell red.
- **避免 / Avoid:** 极简奢侈品、严肃金融和需要当代高级感的内容通常会与它的时代感冲突。Minimal luxury, serious finance, and contemporary-premium work usually conflict with its period character.

> **Atoms are sacred · composition is free · numbers come from the script.**

## Overview

Dell's December 1996 home page is a fossil of catalog-era enterprise design: black picture-frame border, tinted "ribbon card" per product line, chunky Arial Black eyebrows, Times Roman body, and hand-cut GIF stickers. At frame scale, that vocabulary is a gift. The literal `{components.page-frame-giant}` becomes the container the video lives inside — not a stylistic border but a diegetic frame. The eight-tint palette becomes the sequence's color rotation. Dell red stays exactly as it was: the singular attention pole, reserved for `{components.cta-block-red-giant}` and `{components.phone-callout-giant}` — never decorative.

The register the video must hit is **catalog-era enterprise, not retro pastiche.** That means flat fills only (no gradient, no soft shadow, no Material elevation); hairlines and frame-scaled borders only (no rounded corners except the seal); serif body against sans display (the mid-90s tell); and stickers as the sole decorative vocabulary. The reference caliber is a Dell homepage GIF snapshot from December 1996, not a modern retro-poster.

### Frame Craft Bar

- **Squint test** — one thing dominates every frame at 3–6× its nearest neighbor: the wordmark, the eyebrow claim, the ribbon-card title, the red CTA, or the phone number. A ribbon body and its title bar are one composed object, not two competing focal elements.
- **Silence test** — sparse plates (cover, oversized-claim, focal-artifact, red-CTA, closer) read **55–75% empty** — most of the frame is the black `{components.page-frame-giant}` ground or a single tinted fill. The **named density exception is the ribbon catalog plate**, which is deliberately tight because it's showing the whole product family at once.
- **Restraint test** — the brand's scarce element is **Dell red (`{colors.primary}`).** It may fire at full strength once per frame — either as the CTA ground or the phone callout, never both. The `{components.new-burst-sticker-giant}` yellow accent is the only other rationed voltage: one per frame, tilted, over a ribbon edge.
- **Reference bar** — aim at a preserved 1996 dell.com screenshot rendered at 1920×1080 as if projected in a boardroom AV cabinet. Failure looks like a Wes-Anderson palette poster, a retro Mac-OS mockup, or a "Y2K aesthetic" TikTok — all downstream of the 1996 web but none of them the thing.

## Colors

The palette is closed and rationed. At frame scale, three roles exist:

- **Frame ground.** Every frame sits on `{colors.frame-ink}` (#000000) — the literal `{components.page-frame-giant}`. The frame is always visible; the canvas surface (`{colors.canvas}` #ffffff) is what fills the interior. Black is the container, white is the room.
- **Tint fills** — the eight ribbon-card colors (`{colors.tint-olive}` / `{colors.tint-sage}` / `{colors.tint-salmon}` / `{colors.tint-peach}` / `{colors.tint-lime}` / `{colors.tint-sky}` / `{colors.tint-steel}` / `{colors.tint-periwinkle}`) are used as **full-frame or full-band grounds** for oversized-claim and ribbon-focal frames. One per product line across a sequence — pick and stay. Never mix two tints in the same frame body except in the catalog plate.
- **Voltage.** `{colors.primary}` Dell red fires **once per frame maximum**, on either `{components.cta-block-red-giant}` or `{components.phone-callout-giant}` — pick one. `{colors.yellow-sticker}` fires once per frame as a `{components.new-burst-sticker-giant}` or `{components.buy-a-dell-sticker-giant}`. `{colors.link}` #0000ee (classic Mosaic blue) appears only under a Times Roman underlined anchor in the closer/legal band.

The tints are saturated but sub-vivid — that just-below-neutral chroma is the signature of 8-bit web-safe quantization. Preserve it. A "cleaner" recoloured palette breaks the era.

## Typography

Two ramps run in parallel.

**Reading ramp** (px preserved from design.md, for any web-analog surface a frame quotes): `{typography.display}` 36 · `{typography.heading-1}` 24 · `{typography.heading-2}` 16 · `{typography.heading-3}` 14 · `{typography.body}` 14 Times Roman · `{typography.body-sm}` 12 · `{typography.caption}` 11 · `{typography.button}` / `{typography.ui-label}` 12 Helvetica Bold. When a frame renders a page-embedded artifact (e.g. the mini top-banner inside the cover, a legal caption in the closer), it uses these tokens verbatim so the artifact reads as the period document it's quoting.

**Display / hero ramp** (frame-native, vw against 1920): `{typography.wordmark-mega}` at 30vw for the cover wordmark; `{typography.display-hero}` at 14vw for oversized eyebrow claims; `{typography.claim-mid}` at 8vw for medium hero copy; `{typography.section-head}` at 4.2vw for section eyebrows; `{typography.stat-mega}` at 12vw and `{typography.stat-ledger}` at 3.6vw for numerals; `{typography.ribbon-title-giant}` at 3vw for ribbon title bars; `{typography.body-frame}` at 1.7vw for Times Roman body; `{typography.phone-mega}` at 5.5vw for the phone callout; `{typography.sticker-giant}` at 2.2vw for BUY-a-DELL / NEW! stickers.

**Weight ceiling.** Display is always **900** (Arial Black), UI is always **700** (Helvetica), body is **400** (Times Roman). Never soften. The extreme-weight-against-flat-fill is the brand's typographic register.

**Legibility floor.** No load-bearing line drops below **1.4vw (~27px @ 1920)** — that is the `{typography.caption-frame}` token. Anything smaller is chrome or colophon only and may not carry a beat's meaning.

**Fit-to-measure headlines.** Headline text blocks cap at **≤ 78vw** wide and never touch the frame's safe margin. Step the hero ramp by word count: ≤ 3 words → `{typography.display-hero}` (14vw); 4–6 words → `{typography.claim-mid}` (8vw); 7+ words → `{typography.section-head}` (4.2vw). Short lines go big, long lines step down.

## Layout — The Frame

- **Primary aspect** 16:9 at 1920×1080. Companion aspects 9:16 (1080×1920) and 1:1 (1080×1080). This document sizes for landscape; see Aspect-Ratio Behavior for reflow.
- **The literal frame.** Every frame renders inside `{components.page-frame-giant}` — a `{colors.frame-ink}` #000000 border 1vw thick (≈19 px @ 1920, honouring the 8-px web spec scaled to the frame). The interior canvas sits at `{colors.canvas}` #ffffff and is where composition happens.
- **Safe area** = 5vw on all sides inside the black frame — the `{spacing.frame-pad}` token. No load-bearing element touches within 2vw of that boundary.
- **Two-column structural echo.** When a frame wants the 1996 homepage's two-column register (left rail CTA + right column product stack), split at ≈ 30 / 70 with `{spacing.frame-gutter}` (2vw) between. Otherwise, the frame is single-column with a centered anchor.
- **The vw law.** Every display size, gap, and padding is authored in vw against 1920 (px ÷ 1920 × 100 = vw). Fixed px is reserved for atomic chrome — hairlines (1px), the base radius scale (0px / 9999px), and the source spacing tokens quoted inside embedded artifacts.
- **cqw at render time.** The showcase renders each frame in a `container-type: size` element and internal sizing switches from `vw` to `cqw` at the same numeric value. That is what lets a frame render at true proportions whether it's 900px wide on a contact sheet or 1920px on export.

## Elevation & Depth

The depth ceiling is **1 px hairline + literal frame + hand-edge bevel.** Nothing else.

- **Flush** — body copy, tint fills, closer band.
- **Hairline** — 1px `{colors.frame-ink}` around every ribbon card, ledger row, and text input.
- **Frame** — the 1vw `{components.page-frame-giant}` around every frame.
- **Bevel** — hard-edge 1-px highlight + 1-px shadow on stickers and product photos. Simulated in CSS via a hard `filter: drop-shadow(2px 2px 0 #000)`; no soft blur radius.

**Banned at frame scale:** soft drop shadows, atmospheric gradients, blur, glass, glow, parallax depth layers. Any of these breaks the period.

## Shapes

Two radius modes, verbatim from design.md: `{rounded.none}` 0px (everything — cards, buttons, inputs, ribbons, banners, the frame itself) and `{rounded.full}` 9999px (the round `{components.cert-seal-giant}` only).

At frame scale this means every rectangle is razor-square. A single 4-px radius on a CTA breaks the brand. The `{components.cert-seal-giant}` is the only circular object and is sized to 14vw when it appears.

## Components

The frontmatter `components:` block is the normative source of truth. Prose here describes each component's intent and when to use it.

**`{components.page-frame-giant}`** — the always-on outer container. Non-negotiable; every frame has it. Collapsing it below 0.5vw is acceptable in extreme sub-crops but never absent.

**`{components.top-banner-frame}`** — a black establishing strip across the top of a frame. Composes the wordmark, the sub-tagline, `{components.buy-a-dell-sticker-giant}` at right, and `{components.phone-callout-giant}` when the frame wants both voltages present. Not used on every frame — it's an establishing element.

**`{components.section-eyebrow-giant-*}`** — full-frame or full-band tint fills carrying `{typography.display-hero}` claims. The frame's chromatic personality. Compose one of the eight tints per frame; never pair two.

**`{components.ribbon-card-title-giant}` + `{components.ribbon-card-body-giant-*}`** — the brand's signature composed object. Always paired: the white title bar sits on top with a 1px `{colors.frame-ink}` bottom hairline, the tinted body bar sits below. Product name in `{typography.ribbon-title-giant}`; body copy in `{typography.body-frame}`. When a product photo would notch the right edge, reserve ~25% of the body's right side and let a token-colored block stand in (no `<img>`).

**`{components.cta-block-red-giant}`** — the Dell-red panel. One per sequence maximum. Its purpose is the singular top-tier sales message. Never as decoration; never as a card fill.

**`{components.phone-callout-giant}`** — red-on-black phone number in `{typography.phone-mega}`. When it stands alone (closer frame), it may become the focal element at up to 5.5vw. When it sits inside `{components.top-banner-frame}`, it stays at chrome scale.

**`{components.buy-a-dell-sticker-giant}` / `{components.new-burst-sticker-giant}`** — yellow sticker chrome. BUY-a-DELL is a fixed top-right pin; NEW! is a rotated (~12°) accent over a ribbon-card edge. Only one sticker fires per frame.

**`{components.cert-seal-giant}`** — round Dell-red PC Magazine Readers' Choice seal. Right-rail accent on focal-artifact plates. 14vw.

**`{components.ledger-row}`** — white ground row with a black hairline divider. The ledger/data plate composes 4–8 of these vertically; header row uses `{typography.ui-label-frame}` all-caps, body cells use `{typography.stat-ledger}` for numerals and `{typography.body-frame}` for labels.

**`{components.button-primary-giant}`** — the frame-scale black filled button. Used inside `{components.cta-block-red-giant}` compositions and closer plates.

**`{components.icon-label-nav-giant}`** — footer icon-label pair. The connecting green rule from the original page is drawn separately (a 1px `{colors.tint-lime}` inline line under the icon row); it is not part of the token because it's chrome geometry.

Construction not carried by tokens: the 1px hairline between ribbon-card title and body is drawn as `border-bottom: 1px solid {colors.frame-ink}` on the title element. The NEW! sticker's rotation is applied via `transform: rotate(-12deg)` at compose time.

## Motion & Timing

The Dell 1996 brand is **static print delivered as a webpage.** There was no animation — the entire visual grammar is bevels and flat fills. Motion inherits that.

**Cut grammar.** Hard cuts only. No dissolves, no wipes, no pushes. Frame-to-frame is a page-turn, not a transition — the effect a print catalog gives when you flip to the next spread.

**What may animate**
- The NEW! sticker may **snap in** on a single-frame delay (2 frames of hold before appearing) — the "pinned on by hand" gesture.
- The `{components.phone-callout-giant}` red text may **hold-and-blink** at 1Hz on the closer frame only — evoking a 1996 blinking `<blink>` tag at brand-serious cadence.
- The `{components.cert-seal-giant}` may pop-in with 1 frame of scale from 0.9 → 1.0, no easing.

**What must not animate**
- No zoom-in on the wordmark. No parallax on the frame. No kern-in on Arial Black. No color transition on tint fills. No motion path on stickers. No fade in / fade out — cuts only.

**Dwell.** Sparse frames hold **1.6–2.2s** (long enough for the squint test to resolve). The ribbon catalog plate holds **2.6–3.4s** because there is more to read. The closer holds **2.0s + phone-blink cadence**.

**Export.** 24 fps, 1920×1080 progressive, sRGB. No motion blur.

## Frame Treatments

Seven treatments cover the brand's archetypes. Each composes frontmatter components; each has resolved values and a Fixed/Free split.

### 1 · Cover — Dell Wordmark on Ink  (identity/cover · move: full-frame black ground with mega-wordmark centered inside the picture frame)

**Ground** `{components.page-frame-giant}` at 1vw border on `{colors.frame-ink}` #000000, interior `{colors.frame-ink}` (the frame and the ground are the same black — the wordmark reads as light on a solid slab), padding `{spacing.frame-pad}` (5vw).
**Container** single flex column, `justify-content:center`, `align-items:center`, no columns.
**Composes** `{components.page-frame-giant}`, `{components.buy-a-dell-sticker-giant}`, `{components.phone-callout-giant}`.
**Focal** wordmark set in `{typography.wordmark-mega}` (30vw / weight 900 / letter-spacing -1.4vw), color `{colors.canvas}`, centered on both axes; the "DELL" wordmark spans ~74vw.
**Chrome** `{components.buy-a-dell-sticker-giant}` pinned top-right at `top: 5vw; right: 5vw`; a `{typography.caption-frame}` sub-line "www.dell.com · December 1996" centered under the wordmark at 2vw gap.
**Accent** `{components.phone-callout-giant}` pinned top-left at `top: 5vw; left: 5vw` — the phone number is the only red on the frame.
**Silence** ~70% empty (the black ground reads as absence, not fill).
**Fixed** wordmark is Arial Black 900 at `{typography.wordmark-mega}`; palette is ink+canvas+yellow-sticker+primary only.  **Free** the caption line ("www.dell.com · December 1996") is script-provided; the phone number may be any brand phone atom.
**Density** sparse.

### 2 · Oversized Claim — Full-Frame Tint  (editorial/oversized-claim · move: one tint fills the entire frame ground, a chunky Arial Black 900 claim reads across)

**Ground** `{components.page-frame-giant}` with interior filled by `{components.section-eyebrow-giant-salmon}` at `{colors.tint-salmon}` #d77a7a, padding `{spacing.frame-pad}` (5vw).
**Container** single flex column, `justify-content:center`, headline text block capped at `max-width: 78vw`.
**Composes** `{components.page-frame-giant}`, `{components.section-eyebrow-giant-salmon}`.
**Focal** headline in `{typography.claim-mid}` (8vw / weight 900 / line-height 0.95), color `{colors.ink}`, centered; step ramp by word count (see Typography).
**Chrome** small `{typography.ui-label-frame}` all-caps kicker centered above the claim at 2.4vw gap — used sparingly.
**Accent** none — the tint fill IS the voltage on this plate. No red, no yellow.
**Silence** ~62% empty.
**Fixed** ground is exactly one of `{components.section-eyebrow-giant-olive|salmon|periwinkle}` (or another tint variant); typography is Arial Black 900; ink text only.  **Free** headline copy is script-provided; kicker line is optional per frame; tint may rotate to any of the eight family colors.
**Density** sparse.

### 3 · Ribbon Focal — Product Card at Frame Scale  (focal-artifact · move: one ribbon card composed and enlarged to occupy the center of the frame)

**Ground** `{components.page-frame-giant}`, interior `{colors.canvas}` #ffffff, padding `{spacing.frame-pad}` (5vw).
**Container** single centered ribbon column, `max-width: 66vw`, `justify-content:center`; certification seal absolutely positioned on the right rail.
**Composes** `{components.page-frame-giant}`, `{components.ribbon-card-title-giant}`, `{components.ribbon-card-body-giant-periwinkle}`, `{components.cert-seal-giant}`.
**Focal** the composed ribbon card (title bar + tinted body) — title in `{typography.ribbon-title-giant}` (3vw), body in `{typography.body-frame}` (1.7vw), tinted body at 66vw wide × ~26vw tall; centered vertically. The title bar carries a 1px `{colors.frame-ink}` bottom hairline.
**Chrome** a token-colored block stands in for the product photo at the ribbon body's right edge (~14vw × 18vw), notched to hang 2vw above and below the body bar; `— product photo —` caption inside.
**Accent** `{components.cert-seal-giant}` at 14vw pinned to `top: 12vw; right: 6vw`, red disc on canvas.
**Silence** ~58% empty.
**Fixed** the title+body pairing, hairline, notch geometry, the seal atom.  **Free** the tint variant (any of the eight ribbon-card-body-giant-* variants), product name in the title bar, marketing pitch in the body, and whether the seal is present per frame.
**Density** standard.

### 4 · Ribbon Catalog — Product Family Grid  (chrome/catalog · move: multiple ribbon cards stacked in a two-column grid, the whole product family present at once — the density exception)

**Ground** `{components.page-frame-giant}`, interior `{colors.canvas}` #ffffff, padding `{spacing.frame-pad-tight}` (3vw).
**Container** CSS grid, `grid-template-columns: 1fr 1fr`, `gap: 2vw` (`{spacing.frame-gutter}`), 3 rows × 2 columns = 6 ribbon slots.
**Composes** `{components.page-frame-giant}`, `{components.top-banner-frame}` (as a thin heading strip), six `{components.ribbon-card-title-giant}` + `{components.ribbon-card-body-giant-*}` pairs (one per tint), `{components.new-burst-sticker-giant}`.
**Focal** the grid as a whole; no single card dominates — this is a survey plate. Each ribbon card is ~38vw × 18vw.
**Chrome** `{components.top-banner-frame}` at top holding a `{typography.section-head}` (4.2vw) all-caps label like "PRODUCT FAMILY" for the sequence; small `{typography.caption-frame}` legal line pinned bottom-center at 2vw from the frame edge.
**Accent** exactly one `{components.new-burst-sticker-giant}` rotated -12° over the top-right corner of a single ribbon card — the one voltage in the plate.
**Silence** tight by design — the density exception. Reads ~15% empty; the catalog register is the point.
**Fixed** the grid structure (2 columns × 3 rows), the six tint variants covering the family, the single yellow burst placement.  **Free** which six of the eight tints are used per frame, product names in each title bar, which card carries the NEW! burst.
**Density** dense-exception.

### 5 · Dell Red CTA — The Attention Pole  (brand-signature · move: the frame becomes the CTA panel — Dell red fills the interior, Times Roman body sits centered, a single black button anchors it)

**Ground** `{components.page-frame-giant}` with interior filled edge-to-edge by `{components.cta-block-red-giant}` at `{colors.primary}` #e91d2a, padding `{spacing.frame-pad}` (5vw).
**Container** single flex column, `justify-content:center`, `align-items:center`, text block capped at `max-width: 70vw`.
**Composes** `{components.page-frame-giant}`, `{components.cta-block-red-giant}`, `{components.button-primary-giant}`.
**Focal** headline copy in `{typography.claim-mid}` (8vw / Arial Black 900), color `{colors.on-primary}` #ffffff; ≤ 6 words, centered.
**Chrome** short sub-line in `{typography.body-frame}` (1.7vw) Times Roman, `{colors.on-primary}`, centered 2vw below the headline.
**Accent** `{components.button-primary-giant}` centered 4vw below the sub-line — black fill, white Helvetica Bold caps label ≈ 2.2vw type. This is the singular Dell-red frame in the sequence; nothing else red may appear.
**Silence** ~55% empty.
**Fixed** the ground is exactly `{colors.primary}`; text is only `{colors.on-primary}`; the button is `{components.button-primary-giant}`; no seal, no sticker, no phone atom.  **Free** headline copy, sub-line, button label — all script-provided.
**Density** sparse.

### 6 · Spec Ledger — Numbers on Canvas  (data/ledger · move: a stack of ledger rows with numerals against a white canvas — the catalog spec sheet at frame scale)

**Ground** `{components.page-frame-giant}`, interior `{colors.canvas}` #ffffff, padding `{spacing.frame-pad}` (5vw).
**Container** single flex column: `{components.top-banner-frame}` as thin heading strip at top, then a flex column of 5 `{components.ledger-row}` rows below with 1px `{colors.frame-ink}` hairlines between; column width capped at `max-width: 74vw`, centered.
**Composes** `{components.page-frame-giant}`, `{components.top-banner-frame}`, five `{components.ledger-row}`, `{components.buy-a-dell-sticker-giant}`.
**Focal** the numerals column — each ledger row's right cell is a numeral in `{typography.stat-ledger}` (3.6vw / Arial Black 900); the left cell is a label in `{typography.body-frame}` (1.7vw / Times Roman). The header row uses `{typography.ui-label-frame}` (1.5vw / Helvetica Bold caps).
**Chrome** heading strip carries `{typography.section-head}` (4.2vw) all-caps title in `{colors.canvas}` on `{colors.frame-ink}` ground; `margin-bottom: 3vw` clearance to the first ledger row (no headline collision).
**Accent** `{components.buy-a-dell-sticker-giant}` pinned top-right at `top: 5vw; right: 5vw` — one voltage, chrome scale.
**Silence** ~30% empty — denser than a claim plate but not the catalog exception; the rows read like a printed spec table.
**Fixed** the row hairlines, header row typography, the sticker atom.  **Free** the label/numeral pairs are entirely script-provided (never invent figures — see Approved Real Entities).
**Density** standard.

### 7 · Closer — Phone Callout  (closer · move: the frame collapses to the top-banner register — black ground, giant red phone number centered, a single blue Copyright line beneath)

**Ground** `{components.page-frame-giant}`, interior `{colors.frame-ink}` #000000 (same as frame), padding `{spacing.frame-pad}` (5vw).
**Container** single flex column centered.
**Composes** `{components.page-frame-giant}`, `{components.phone-callout-giant}`, `{components.icon-label-nav-giant}`, `{components.button-text-link}` (rendered as `{typography.body-frame}` blue underlined line on canvas band).
**Focal** phone number rendered in `{typography.phone-mega}` (5.5vw / Helvetica Bold 700), color `{colors.primary}` on `{colors.frame-ink}`, centered vertically.
**Chrome** small `{typography.ui-label-frame}` caps line "CALL DELL ORDER SUPPORT" centered 2.4vw above the phone number in `{colors.canvas}`; four `{components.icon-label-nav-giant}` pairs in a row 6vw below the phone (FIND / HOME / ONLINE STORE / SERVICE & SUPPORT — the fixed 1996 nav quartet) on a `{colors.canvas}` band with a 1px `{colors.tint-lime}` horizontal rule connecting them.
**Accent** single `{colors.link}` #0000ee underlined "Copyright" line at the bottom in `{typography.body-frame}` — the only blue in the sequence.
**Silence** ~60% empty.
**Fixed** phone color `{colors.primary}`; ground `{colors.frame-ink}`; nav quartet labels; underline blue for the anchor.  **Free** the actual phone atom (script-provided), the copyright year (script-provided).
**Density** sparse.

## Do's and Don'ts

**Do**
- Keep the literal `{components.page-frame-giant}` on every frame — it is the brand.
- Reserve `{colors.primary}` for `{components.cta-block-red-giant}` or `{components.phone-callout-giant}`. One or the other, once per frame.
- Compose ribbon cards as **title + tinted body pair** — the two are one object.
- Use the eight tints as a **family**: pick one per product line and hold it across the sequence.
- Set every display in `{typography.wordmark-mega}` / `{typography.display-hero}` / `{typography.claim-mid}` — Arial Black 900 against flat fill.
- Keep body copy in Times Roman via `{typography.body-frame}` — the serif is the era.
- Anchor centered by default on cover/oversized-claim/focal/red-CTA/closer; reserve two-column left-anchor for the ledger and catalog plates.
- Vary the composition axis frame-to-frame; no more than 2 consecutive frames share an anchor.

**Don't**
- Don't introduce a chromatic accent outside the eight tints + Dell red + Dell yellow + classic link blue.
- Don't soften a corner. `{rounded.none}` is universal; only the `{components.cert-seal-giant}` is round.
- Don't replace Times Roman body with a sans — the serif body is the era's signature.
- Don't add a soft drop-shadow, gradient, or glass surface. Hard-edge bevels only.
- Don't animate the wordmark, the frame, or the tint grounds. Motion is limited (see Motion & Timing).
- Don't compose two `{components.cta-block-red-giant}` frames in the same sequence — the red is scarce by design.
- Don't strip `{components.phone-callout-giant}` from the closer.
- Don't fill sparse frames just because they read empty — the emptiness is the confidence.

## Aspect-Ratio Behavior

| Treatment | 16:9 (1920×1080, primary) | 9:16 (1080×1920) | 1:1 (1080×1080) |
|---|---|---|---|
| 1 · Cover | wordmark 30vw centered; phone top-left, sticker top-right | wordmark drops to ~24vh equivalent, stacks over caption; phone below wordmark, sticker top-right | wordmark 26vw centered; phone above wordmark, sticker below-right |
| 2 · Oversized Claim | claim centered, 8vw hero | claim rebreaks to more lines; hero steps down one tier if word count crosses breakpoint | claim centered, 10vw if ≤ 3 words |
| 3 · Ribbon Focal | ribbon 66vw × 26vw centered; seal right rail | ribbon 84vw wide, seal moves below body bar; photo notch becomes top-aligned band | ribbon 76vw wide, seal top-right corner |
| 4 · Ribbon Catalog | 2 col × 3 row grid | 1 col × 6 row stack; heading strip stays; caption legal wraps below last card | 2 col × 3 row grid; cards shrink to 32vw wide |
| 5 · Dell Red CTA | headline 8vw + sub + button, centered | headline steps to `{typography.claim-mid}` at word-count breakpoint; button pinned to bottom safe area | headline 8vw + button; sub-line drops if crowding |
| 6 · Spec Ledger | 5 rows @ 74vw column, centered | 5 rows stack full-width; numeral cell wraps under label cell within row | 5 rows @ 82vw column |
| 7 · Closer | phone 5.5vw centered; nav quartet row | phone 8vw; nav quartet becomes 2×2 grid | phone 7vw; nav quartet 2×2 grid |

Safe area is always 5vw (or the aspect-scaled equivalent on the short edge) inside the frame border. No load-bearing line drops below the 1.4vw legibility floor after reflow.

## Approved Real Entities & Numerals

The following are the only concrete brand entities from design.md that a frame may quote verbatim:

- **Brand phone atom.** `1-800-213-DELL` — appears on the cover, in the top-banner-frame, and as the closer focal. Never invent an alternate number.
- **Wordmark.** "Dell" or "DELL" (both variants documented). Never stylize.
- **Product family names** referenced in design.md: DIMENSION, DIMENSION XPS, OPTIPLEX GX PRO, OPTIPLEX G Series, LATITUDE, POWEREDGE, DELLWARE.
- **Sticker copy.** "BUY a DELL" and "NEW!" — verbatim wording, verbatim punctuation.
- **Certification.** "PC MAGAZINE READERS' CHOICE · SERVICE · RELIABILITY" — the seal's ring copy.
- **Nav quartet.** FIND · HOME · ONLINE STORE · SERVICE & SUPPORT.
- **Anchor phrases.** "Copyright" · "(Terms of Use)" · "www.dell.com".

**Numerals are never invented.** Any price, spec (MHz, MB, GB), award year, or ranking must come from the script. Frames with unknown figures render `— figure —` in the numeral cell.

## Pre-Render Self-Audit

Run before finalizing any frame:

- **Squint** — one element dominates at 3–6× its nearest neighbor.
- **Silence** — sparse plate reads 55–75% empty; catalog plate exempt.
- **Restraint** — Dell red fires exactly once (or not at all) per frame; yellow sticker fires once maximum; blue link only in the closer.
- **Weight** — display is Arial Black 900; UI is Helvetica Bold 700; body is Times Roman 400. Nothing softer.
- **Depth** — no soft shadow, no gradient, no blur. Hairline + literal frame + hard bevel only.
- **Geometry** — every rectangle is `{rounded.none}`; only the seal is `{rounded.full}`.
- **Anchor** — centered by default; two-column register only on ledger/catalog; no more than 2 consecutive frames share anchor.
- **Element count** — ≤ 2–3 focal elements per frame (catalog exception).
- **Floor** — no load-bearing line under 1.4vw / 27px @ 1920.
- **Frame** — `{components.page-frame-giant}` present and 1vw thick.
- **Copy fidelity** — every entity above is verbatim; every numeral came from the script or is `— figure —`.

## Known Gaps

- **vw / cqw as strings.** The DESIGN.md spec consumer stores unknown units as opaque strings. `frame.md` uses vw in the frontmatter typography ramp and layout tokens; the showcase renders them as cqw via container queries. Consumers that need px should multiply the vw value by 19.2 (1920 ÷ 100).
- **Portrait and square treatments** are derived by the Aspect-Ratio Behavior table. This document authors 16:9 as primary; the derived sizes are guidance until each treatment is rendered in the target ratio.
- **Product photography** is intentionally placeholder-only in this spec — the ribbon-focal frame reserves the right-edge notch but never composes a real image. Renderers should stand in a flat token-colored block with a `— product photo —` caption.
- **The connecting green rule** under the icon-label nav row is drawn as a 1px `{colors.tint-lime}` line at compose time; it is not a token because the geometry is chrome, not surface.
- **Motion tokens** are prose-only (dwell ranges, cut grammar) — no formal easing/duration token block, because the brand's motion vocabulary is deliberately near-zero.
