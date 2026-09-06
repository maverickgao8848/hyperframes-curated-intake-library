import { createFidelityHost, createStandardSegments, destroyFidelity, htmlNode, normalizeLocalFrame, validateParams } from "../fidelity-runtime.js";

const CSS = `.comp-hero-big-number{position:relative;display:grid;place-items:center;width:100%;height:100%;padding:var(--comp-space-6);font-family:var(--comp-font-sans);color:var(--comp-ink)}.comp-hero-big-number .hn-wrap{text-align:center}.comp-hero-big-number .hn-value{font:900 clamp(64px,13vw,210px)/.82 var(--comp-font-display);letter-spacing:-.065em;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}.comp-hero-big-number .hn-unit{margin-left:.15em;color:var(--comp-accent);font-size:.28em;letter-spacing:0}.comp-hero-big-number .hn-label{margin-top:var(--comp-space-5);font-size:clamp(18px,2.4vw,32px);font-weight:650}.comp-hero-big-number .hn-source{margin-top:var(--comp-space-3);color:var(--comp-muted);font:500 14px/1.4 var(--comp-font-mono)}`;
export const meta = { id: "hero-big-number", version: 1, legacyAliases: ["broll-hero.big-number"], schema: { properties: { value: { type: "string", required: true, maxLength: 24 }, unit: { type: "string", default: "", maxLength: 12 }, label: { type: "string", required: true, maxLength: 64 }, sourceNote: { type: "string", required: true, maxLength: 160 }, durationFrames: { type: "number", min: 12, max: 900, default: 120 } } } };

export function mount(root, context = {}) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  const { element, gsap } = createFidelityHost(root, context, meta, "hn", CSS);
  const wrap = htmlNode("article", "hn-wrap"), value = htmlNode("div", "hn-value", params.value), unit = htmlNode("span", "hn-unit", params.unit), label = htmlNode("div", "hn-label", params.label), source = htmlNode("div", "hn-source", params.sourceNote);
  value.appendChild(unit); wrap.append(value, label, source); element.appendChild(wrap);
  const state = { progress: 0 }, render = () => { value.style.opacity = String(.2 + .8 * state.progress); };
  const segments = createStandardSegments(gsap, element, [value, label, source], state, render);
  return { segments, seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); }, destroy() { destroyFidelity(element, segments); } };
}
