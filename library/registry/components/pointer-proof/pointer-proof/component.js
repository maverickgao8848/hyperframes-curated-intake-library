import { createFidelityHost, destroyFidelity, htmlNode, clamp01 } from "../fidelity-runtime.js";

const CSS = `
.comp-pointer-proof{width:100%;min-height:300px;display:grid;place-items:center;padding:36px;border-radius:24px;color:var(--comp-ink,#f7f8fb);font-family:var(--comp-font-sans,sans-serif)}
.comp-pointer-proof .pp-copy{max-width:820px;font-size:42px;font-weight:710;line-height:1.18;letter-spacing:-.035em;text-align:center}.comp-pointer-proof .pp-target{position:relative;display:inline-block;margin:0 .08em;color:var(--comp-ink,#fff);z-index:1}
.comp-pointer-proof .pp-target:before{content:"";position:absolute;z-index:-1;left:-.08em;right:-.08em;bottom:.03em;height:.42em;border-radius:.15em;background:color-mix(in srgb,var(--comp-accent,#78a8ff) 72%,transparent);transform-origin:left center;transform:scaleX(var(--sweep,0))}
.comp-pointer-proof .pp-outline{position:absolute;inset:-.18em -.2em;border:2px solid var(--comp-accent,#78a8ff);border-radius:.18em;transform-origin:left center;transform:scaleX(var(--outline,0));filter:drop-shadow(0 0 10px color-mix(in srgb,var(--comp-accent,#78a8ff) 46%,transparent))}
.comp-pointer-proof .pp-pointer{position:absolute;right:-22px;bottom:-28px;width:34px;height:34px;transform:translate(20px,18px) rotate(-18deg) scale(var(--pointer,0));filter:drop-shadow(0 5px 8px rgba(0,0,0,.35))}.comp-pointer-proof .pp-pointer:before{content:"";display:block;width:0;height:0;border-left:10px solid transparent;border-right:10px solid transparent;border-bottom:28px solid var(--comp-accent,#78a8ff);transform:rotate(-42deg)}
.comp-pointer-proof .pp-caption{margin-top:28px;color:var(--comp-muted,#9aa6b6);font:700 10px/1 var(--comp-font-mono,monospace);letter-spacing:.16em;text-align:center}
`;
export const meta = { id: "pointer-proof", version: 1, candidateId: "EDU-EMPHASIS-05" };
export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const { before = "The idea only becomes useful when the viewer sees", phrase = "the exact distinction", after = "that changes the decision.", caption = "NOTICE → NAME → REMEMBER" } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "pp", CSS);
  const copy = htmlNode("div", "pp-copy"), target = htmlNode("span", "pp-target", phrase), outline = htmlNode("i", "pp-outline"), pointer = htmlNode("i", "pp-pointer");
  target.append(outline, pointer); copy.append(document.createTextNode(`${before} `), target, document.createTextNode(` ${after}`));
  element.append(copy, htmlNode("div", "pp-caption", caption));
  const state = { progress: 0 };
  function render() { const p = clamp01(state.progress); target.style.setProperty("--sweep", String(clamp01(p * 1.6))); target.style.setProperty("--outline", String(clamp01((p - .28) * 1.7))); target.style.setProperty("--pointer", String(clamp01((p - .58) * 2.4))); }
  const enter = gsap.timeline({ paused: true }).fromTo(copy, { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: .38 }).to(state, { progress: 1, duration: .95, ease: "power2.inOut", onUpdate: render }, .18);
  const emphasis = gsap.timeline({ paused: true }).to(target, { scale: 1.035, duration: .2 }).to(target, { scale: 1, duration: .25 });
  const dim = gsap.timeline({ paused: true }).to(element, { autoAlpha: .3, duration: .25 });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, y: -12, duration: .34 });
  const segments = { enter, emphasis, dim, exit }; render();
  return { segments, seek(frame) { enter.time(Math.max(0, frame) / fps); }, destroy() { destroyFidelity(element, segments); } };
}
