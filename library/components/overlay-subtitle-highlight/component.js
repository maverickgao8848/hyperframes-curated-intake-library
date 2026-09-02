import { createFidelityHost, createStandardSegments, destroyFidelity, htmlNode, normalizeLocalFrame, validateParams } from "../fidelity-runtime.js";

const CSS = `.comp-overlay-subtitle-highlight{position:relative;display:flex;justify-content:center;width:100%;padding:var(--comp-space-3);font-family:var(--comp-font-sans);color:var(--comp-ink)}.comp-overlay-subtitle-highlight .sh-line{max-width:38em;padding:.62em 1em;border:1px solid var(--comp-line);border-radius:var(--comp-radius-sm);background:var(--comp-surface-strong);font-size:clamp(20px,2.2vw,34px);font-weight:650;line-height:1.45;text-align:center;text-wrap:balance}.comp-overlay-subtitle-highlight .sh-token{color:var(--comp-muted)}.comp-overlay-subtitle-highlight .sh-token[data-state="read"]{color:color-mix(in srgb,var(--comp-ink) 62%,var(--comp-muted))}.comp-overlay-subtitle-highlight .sh-token[data-state="current"]{color:var(--comp-canvas);background:var(--comp-accent);border-radius:.18em;padding:.03em .12em}`;
export const meta = { id: "overlay-subtitle-highlight", version: 1, legacyAliases: ["aroll.subtitle-highlight"], schema: { properties: { text: { type: "string", required: true, maxLength: 120 }, keywordRanges: { type: "array", maxItems: 6, default: [] }, durationFrames: { type: "number", min: 12, max: 900, default: 120 } } } };

export function mount(root, context = {}) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  const { element, gsap } = createFidelityHost(root, context, meta, "sh", CSS);
  const line = htmlNode("p", "sh-line");
  const tokens = [...params.text].map((character, index) => { const token = htmlNode("span", "sh-token", character); token.dataset.index = String(index); line.appendChild(token); return token; });
  element.appendChild(line);
  const ranges = params.keywordRanges.map((range, index) => {
    if (!range || !Number.isInteger(range.start) || !Number.isInteger(range.end) || range.start < 0 || range.end <= range.start || range.end > tokens.length) throw new Error(`[${meta.id}] keywordRanges[${index}] must be within text`);
    return range;
  });
  const state = { progress: 0 };
  const render = () => { const cursor = Math.min(tokens.length - 1, Math.floor(state.progress * tokens.length)); tokens.forEach((token, index) => { const keyword = ranges.some((range) => index >= range.start && index < range.end); token.dataset.state = keyword && index === cursor ? "current" : index < cursor ? "read" : "unread"; }); };
  const segments = createStandardSegments(gsap, element, [line], state, render);
  return { segments, seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); }, destroy() { destroyFidelity(element, segments); } };
}
