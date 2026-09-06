import { createFidelityHost, createStandardSegments, destroyFidelity, htmlNode, normalizeLocalFrame, validateParams } from "../fidelity-runtime.js";

const CSS = `.comp-hero-pull-quote{position:relative;display:grid;place-items:center;width:100%;height:100%;padding:var(--comp-space-7);font-family:var(--comp-font-sans);color:var(--comp-ink)}.comp-hero-pull-quote .hq-quote{position:relative;width:min(92%,1040px);margin:0;padding-left:var(--comp-space-6)}.comp-hero-pull-quote .hq-quote:before{content:"“";position:absolute;left:-.18em;top:-.34em;color:var(--comp-accent);font:900 clamp(90px,13vw,180px)/1 var(--comp-font-display)}.comp-hero-pull-quote .hq-text{font:750 clamp(34px,5.4vw,78px)/1.08 var(--comp-font-display);letter-spacing:-.035em;text-wrap:balance}.comp-hero-pull-quote .hq-attribution{margin-top:var(--comp-space-5);font-size:clamp(15px,1.8vw,23px);font-weight:700}.comp-hero-pull-quote .hq-source{margin-top:var(--comp-space-2);color:var(--comp-muted);font:500 14px/1.4 var(--comp-font-mono)}`;
export const meta = { id: "hero-pull-quote", version: 1, legacyAliases: ["broll-hero.pull-quote"], schema: { properties: { quote: { type: "string", required: true, maxLength: 180 }, attribution: { type: "string", required: true, maxLength: 80 }, sourceNote: { type: "string", required: true, maxLength: 160 }, durationFrames: { type: "number", min: 12, max: 900, default: 120 } } } };

export function mount(root, context = {}) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  const { element, gsap } = createFidelityHost(root, context, meta, "hq", CSS);
  const block = htmlNode("blockquote", "hq-quote"), quote = htmlNode("div", "hq-text", params.quote), attribution = htmlNode("footer", "hq-attribution", `— ${params.attribution}`), source = htmlNode("div", "hq-source", params.sourceNote);
  block.append(quote, attribution, source); element.appendChild(block);
  const state = { progress: 0 }, render = () => block.style.setProperty("--hq-progress", state.progress.toFixed(3));
  const segments = createStandardSegments(gsap, element, [quote, attribution, source], state, render);
  return { segments, seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); }, destroy() { destroyFidelity(element, segments); } };
}
