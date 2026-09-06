import { createFidelityHost, createStandardSegments, destroyFidelity, htmlNode, normalizeLocalFrame, validateParams } from "../fidelity-runtime.js";

const CSS = `.comp-overlay-concept-card{position:relative;display:grid;place-items:center;width:100%;font-family:var(--comp-font-sans);color:var(--comp-ink)}.comp-overlay-concept-card .oc-card{width:min(92%,720px);padding:var(--comp-space-6);border:1px solid var(--comp-line-strong);border-radius:var(--comp-radius-md);background:var(--comp-surface-strong)}.comp-overlay-concept-card .oc-eyebrow{color:var(--comp-accent);font:700 13px/1 var(--comp-font-mono);letter-spacing:.16em;text-transform:uppercase}.comp-overlay-concept-card .oc-title{margin:.45em 0 .5em;font:800 clamp(30px,5vw,62px)/1.02 var(--comp-font-display);text-wrap:balance}.comp-overlay-concept-card .oc-line{margin:.22em 0;color:var(--comp-muted);font-size:clamp(17px,2vw,25px);line-height:1.45}.comp-overlay-concept-card .oc-source{margin-top:var(--comp-space-5);padding-top:var(--comp-space-3);border-top:1px solid var(--comp-line);color:var(--comp-muted);font:500 14px/1.4 var(--comp-font-mono)}`;
export const meta = { id: "overlay-concept-card", version: 1, legacyAliases: ["aroll.concept-card"], schema: { properties: { eyebrow: { type: "string", default: "Concept", maxLength: 24 }, title: { type: "string", required: true, maxLength: 36 }, lines: { type: "array", required: true, minItems: 1, maxItems: 3 }, sourceNote: { type: "string", required: true, maxLength: 120 }, durationFrames: { type: "number", min: 12, max: 900, default: 120 } } } };

export function mount(root, context = {}) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  if (params.lines.some((line) => typeof line !== "string" || !line.trim())) throw new Error(`[${meta.id}] lines must be non-empty strings`);
  const { element, gsap } = createFidelityHost(root, context, meta, "oc", CSS);
  const card = htmlNode("article", "oc-card"), eyebrow = htmlNode("div", "oc-eyebrow", params.eyebrow), title = htmlNode("h2", "oc-title", params.title);
  const lines = params.lines.map((line) => htmlNode("p", "oc-line", line)), source = htmlNode("footer", "oc-source", params.sourceNote);
  card.append(eyebrow, title, ...lines, source); element.appendChild(card);
  const state = { progress: 0 }, render = () => card.style.setProperty("--oc-progress", state.progress.toFixed(3));
  const segments = createStandardSegments(gsap, element, [eyebrow, title, ...lines, source], state, render);
  return { segments, seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); }, destroy() { destroyFidelity(element, segments); } };
}
