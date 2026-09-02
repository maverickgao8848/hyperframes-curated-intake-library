import { createFidelityHost, destroyFidelity, htmlNode, clamp01 } from "../fidelity-runtime.js";

const CSS = `
.comp-concept-pin{width:100%;min-height:390px;display:grid;place-items:center;overflow:hidden;border-radius:24px;color:var(--comp-ink,#f7f8fb);font-family:var(--comp-font-sans,sans-serif);perspective:900px}
.comp-concept-pin .cp-stage{position:relative;width:min(78%,720px);height:300px;transform-style:preserve-3d;transform:rotateX(58deg) rotateZ(-8deg)}
.comp-concept-pin .cp-ground{position:absolute;z-index:0;inset:35px;border:1px solid var(--comp-line,rgba(255,255,255,.14));border-radius:50%;background:radial-gradient(circle,var(--comp-surface-strong,#161d28),var(--comp-surface,#090d13) 68%);box-shadow:0 40px 80px rgba(0,0,0,.38);transform:translateZ(-70px)}
.comp-concept-pin .cp-ring{position:absolute;z-index:1;left:50%;top:50%;width:150px;height:150px;border:2px solid var(--comp-accent,#78a8ff);border-radius:50%;transform:translate(-50%,-50%) translateZ(-30px) scale(var(--ring,.2));opacity:var(--ring-opacity,0);box-shadow:0 0 34px color-mix(in srgb,var(--comp-accent,#78a8ff) 40%,transparent)}
.comp-concept-pin .cp-stem{position:absolute;z-index:2;left:50%;top:50%;width:2px;height:150px;background:linear-gradient(var(--comp-accent,#78a8ff),transparent);transform-origin:top;transform:translate(-50%,0) rotateX(-90deg) scaleY(var(--stem,0));box-shadow:0 0 14px var(--comp-accent,#78a8ff)}
.comp-concept-pin .cp-card{position:absolute;z-index:3;left:50%;top:12px;width:310px;padding:23px;border:1px solid color-mix(in srgb,var(--comp-accent,#78a8ff) 55%,var(--comp-line,transparent));border-radius:18px;background:var(--comp-surface-strong,#151c27);box-shadow:0 30px 80px rgba(0,0,0,.5);transform:translate(-50%,var(--lift,80px)) translateZ(110px) rotateZ(8deg) rotateX(-58deg) scale(var(--scale,.78));opacity:var(--card-opacity,0)}
.comp-concept-pin .cp-kicker{font:800 9px/1 var(--comp-font-mono,monospace);letter-spacing:.17em;color:var(--comp-accent,#78a8ff)}.comp-concept-pin .cp-value{margin-top:11px;font-size:46px;font-weight:780;line-height:1;letter-spacing:-.045em}.comp-concept-pin .cp-title{margin-top:10px;font-size:17px;font-weight:680}.comp-concept-pin .cp-context{margin-top:9px;color:var(--comp-muted,#9aa6b6);font-size:12px;line-height:1.4}
`;
export const meta = { id: "concept-pin", version: 1, candidateId: "EDU-ANCHOR-03" };
export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context, { label = "KEY VARIABLE", value = "2.4×", title = "One factor dominates the outcome", context: note = "Use the pin to anchor a place, value, or concept before explaining its consequences." } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "cp", CSS), stage = htmlNode("div", "cp-stage"), ground = htmlNode("div", "cp-ground"), ring = htmlNode("i", "cp-ring"), stem = htmlNode("i", "cp-stem"), card = htmlNode("article", "cp-card");
  card.append(htmlNode("div", "cp-kicker", label), htmlNode("div", "cp-value", value), htmlNode("div", "cp-title", title), htmlNode("div", "cp-context", note)); stage.append(ground, ring, stem, card); element.appendChild(stage);
  const state = { progress: 0 }; function render() { const p = clamp01(state.progress), land = clamp01(p*1.35), bloom = clamp01((p-.28)*1.5); ring.style.setProperty("--ring", String(.2+bloom*1.25)); ring.style.setProperty("--ring-opacity", String((1-bloom)*.85)); stem.style.setProperty("--stem", String(land)); card.style.setProperty("--lift", `${80-land*126}px`); card.style.setProperty("--scale", String(.78+land*.22)); card.style.setProperty("--card-opacity", String(land)); }
  const enter = gsap.timeline({ paused: true }).to(state, { progress: 1, duration: 1.15, ease: "power3.out", onUpdate: render });
  const emphasis = gsap.timeline({ paused: true }).to(card, { y: -7, duration: .24 }).to(card, { y: 0, duration: .3 });
  const dim = gsap.timeline({ paused: true }).to(element, { autoAlpha: .32, duration: .28 });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, scale: .98, duration: .35 });
  const segments = { enter, emphasis, dim, exit }; render();
  return { segments, seek(frame) { enter.time(Math.max(0, frame) / fps); }, destroy() { destroyFidelity(element, segments); } };
}
