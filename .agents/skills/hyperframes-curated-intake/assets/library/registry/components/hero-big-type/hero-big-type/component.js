import { createFidelityHost, createStandardSegments, destroyFidelity, htmlNode, normalizeLocalFrame, validateParams } from "../fidelity-runtime.js";

const CSS = `.comp-hero-big-type{position:relative;display:grid;place-items:center;width:100%;height:100%;padding:var(--comp-space-6);font-family:var(--comp-font-display);color:var(--comp-ink);overflow:hidden}.comp-hero-big-type .ht-text{max-width:12em;margin:0;font-size:clamp(54px,10vw,154px);font-weight:900;line-height:.88;letter-spacing:-.055em;text-align:center;text-wrap:balance;overflow-wrap:anywhere;white-space:pre-line}.comp-hero-big-type[data-locale^="zh"] .ht-text{max-width:8em;line-height:.98;letter-spacing:-.035em}.comp-hero-big-type .ht-rule{width:min(26vw,220px);height:5px;margin-top:var(--comp-space-5);border-radius:99px;background:var(--comp-accent);transform-origin:left center}`;
export const meta = { id: "hero-big-type", version: 1, legacyAliases: ["broll-hero.big-type"], schema: { properties: { text: { type: "string", required: true, maxLength: 72 }, durationFrames: { type: "number", min: 12, max: 900, default: 120 } } } };

export function mount(root, context = {}) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  const { element, gsap } = createFidelityHost(root, context, meta, "ht", CSS); element.dataset.locale = params.locale === "project" ? "en-US" : params.locale;
  const text = htmlNode("h1", "ht-text", params.text.replace(/\r\n?/g, "\n")), rule = htmlNode("div", "ht-rule"); element.append(text, rule);
  const state = { progress: 0 }, render = () => { rule.style.transform = `scaleX(${state.progress.toFixed(3)})`; };
  const segments = createStandardSegments(gsap, element, [text, rule], state, render);
  return { segments, seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); }, destroy() { destroyFidelity(element, segments); } };
}
