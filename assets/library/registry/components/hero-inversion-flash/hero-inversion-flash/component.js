import { createFidelityHost, destroyFidelity, htmlNode, normalizeLocalFrame, validateParams } from "../fidelity-runtime.js";

const CSS = `.comp-hero-inversion-flash{position:relative;display:grid;place-items:center;width:100%;height:100%;padding:var(--comp-space-6);overflow:hidden;background:var(--comp-canvas);color:var(--comp-ink);font-family:var(--comp-font-display)}.comp-hero-inversion-flash .hi-text{max-width:11em;margin:0;font-size:clamp(52px,10vw,154px);font-weight:900;line-height:.9;letter-spacing:-.055em;text-align:center;text-wrap:balance;overflow-wrap:anywhere}.comp-hero-inversion-flash[data-phase="white"]{background:#fff;color:#050505}.comp-hero-inversion-flash[data-phase="black"]{background:#050505;color:#fff}.comp-hero-inversion-flash[data-phase="settle"]{background:var(--comp-canvas);color:var(--comp-ink)}`;
export const meta = { id: "hero-inversion-flash", version: 1, legacyAliases: ["broll-hero.inversion-flash"], schema: { properties: { text: { type: "string", required: true, maxLength: 72 }, flashes: { type: "number", min: 1, max: 3, default: 2 }, durationFrames: { type: "number", min: 18, max: 180, default: 60 } } } };

export function mount(root, context = {}) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  if (!Number.isInteger(params.flashes)) throw new Error(`[${meta.id}] params.flashes must be an integer`);
  const { element, gsap } = createFidelityHost(root, context, meta, "hi", CSS), text = htmlNode("h1", "hi-text", params.text); element.appendChild(text);
  const renderFrame = (localFrame) => { const frame = normalizeLocalFrame(localFrame, params.durationFrames), flashWindow = params.durationFrames * .62; element.dataset.phase = frame >= flashWindow ? "settle" : Math.floor(frame / (flashWindow / (params.flashes * 2))) % 2 === 0 ? "black" : "white"; };
  const enter = gsap.timeline({ paused: true }).fromTo(element, { autoAlpha: 0 }, { autoAlpha: 1, duration: .12, ease: "none" });
  const explain = gsap.timeline({ paused: true }).call(() => renderFrame(0), [], 0).call(() => renderFrame(params.durationFrames * .31), [], .22).call(() => renderFrame(params.durationFrames), [], .62);
  const emphasize = gsap.timeline({ paused: true }).fromTo(text, { scale: .96 }, { scale: 1, duration: .25, ease: "power2.out" });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, duration: .25, ease: "power2.in" });
  const segments = { enter, explain, emphasize, exit }; renderFrame(0);
  return { segments, seek(localFrame) { renderFrame(localFrame); }, destroy() { destroyFidelity(element, segments); } };
}
