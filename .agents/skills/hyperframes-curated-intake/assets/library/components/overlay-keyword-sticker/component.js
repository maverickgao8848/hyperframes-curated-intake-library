import { createFidelityHost, createStandardSegments, destroyFidelity, htmlNode, normalizeLocalFrame, validateParams } from "../fidelity-runtime.js";

const CSS = `.comp-overlay-keyword-sticker{position:relative;width:100%;height:100%;min-height:180px;font-family:var(--comp-font-display);pointer-events:none}.comp-overlay-keyword-sticker .ok-item{position:absolute;max-width:12em;padding:.42em .7em;border:1px solid var(--comp-line-strong);border-radius:var(--comp-radius-sm);background:var(--comp-accent);color:var(--comp-canvas);font-size:clamp(18px,2.4vw,34px);font-weight:800;line-height:1.08;text-wrap:balance}.comp-overlay-keyword-sticker .ok-item[data-anchor="top-left"]{left:4%;top:6%}.comp-overlay-keyword-sticker .ok-item[data-anchor="top-right"]{right:4%;top:6%}.comp-overlay-keyword-sticker .ok-item[data-anchor="center"]{left:50%;top:50%}.comp-overlay-keyword-sticker .ok-item[data-anchor="bottom-left"]{left:4%;bottom:6%}.comp-overlay-keyword-sticker .ok-item[data-anchor="bottom-right"]{right:4%;bottom:6%}`;
export const meta = { id: "overlay-keyword-sticker", version: 1, legacyAliases: ["aroll.keyword-sticker"], schema: { properties: { items: { type: "array", required: true, minItems: 1, maxItems: 3 }, durationFrames: { type: "number", min: 12, max: 900, default: 90 } } } };

export function mount(root, context = {}) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  const { element, gsap } = createFidelityHost(root, context, meta, "ok", CSS);
  const items = params.items.map((item, index) => {
    if (!item || typeof item.text !== "string" || !item.text.trim()) throw new Error(`[${meta.id}] items[${index}].text is required`);
    const anchor = item.anchor ?? ["top-left", "center", "bottom-right"][index];
    const rotation = Number(item.rotation ?? 0);
    if (!["top-left", "top-right", "center", "bottom-left", "bottom-right"].includes(anchor) || !Number.isFinite(rotation) || Math.abs(rotation) > 8) throw new Error(`[${meta.id}] items[${index}] anchor/rotation invalid`);
    const node = htmlNode("span", "ok-item", item.text); node.dataset.anchor = anchor; node.style.transform = `${anchor === "center" ? "translate(-50%,-50%) " : ""}rotate(${rotation}deg)`; element.appendChild(node); return node;
  });
  const state = { progress: 0 };
  const render = () => items.forEach((item, index) => { item.style.opacity = state.progress >= index / items.length ? "1" : "0"; });
  const segments = createStandardSegments(gsap, element, items, state, render);
  return { segments, seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); }, destroy() { destroyFidelity(element, segments); } };
}
