import { createFidelityHost, destroyFidelity, htmlNode, clamp01 } from "../fidelity-runtime.js";

const CSS = `
.comp-active-border{width:100%;min-height:330px;padding:28px;border-radius:24px;color:var(--comp-ink,#f7f8fb);font-family:var(--comp-font-sans,sans-serif)}
.comp-active-border .ab-list{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.comp-active-border .ab-wrap{position:relative;padding:2px;border-radius:20px;overflow:hidden;background:var(--comp-line,rgba(255,255,255,.13));box-shadow:0 18px 50px rgba(0,0,0,.2)}
.comp-active-border .ab-beam{position:absolute;inset:-80%;background:conic-gradient(from var(--angle,0deg),transparent 0 40%,var(--comp-accent,#78a8ff) 48%,white 50%,var(--comp-accent,#78a8ff) 52%,transparent 60%);opacity:var(--active,0);filter:blur(.2px)}
.comp-active-border .ab-card{position:relative;z-index:1;min-height:250px;padding:27px;border-radius:18px;background:var(--comp-surface,#0e131b)}
.comp-active-border .ab-step{font:800 9px/1 var(--comp-font-mono,monospace);letter-spacing:.18em;color:var(--comp-accent,#78a8ff)}.comp-active-border .ab-title{margin-top:22px;font-size:25px;font-weight:730;letter-spacing:-.025em}.comp-active-border .ab-body{margin-top:14px;color:var(--comp-muted,#9aa6b6);font-size:14px;line-height:1.5}.comp-active-border .ab-status{position:absolute;left:27px;bottom:25px;padding:7px 10px;border-radius:999px;background:color-mix(in srgb,var(--comp-accent,#78a8ff) 14%,transparent);font:800 9px/1 var(--comp-font-mono,monospace);letter-spacing:.12em;color:var(--comp-accent,#78a8ff)}
`;
export const meta = { id: "active-border", version: 1, candidateId: "EDU-PROCESS-07" };
export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const { items = [{ title: "Observe", body: "Collect the signal before naming the cause." }, { title: "Explain", body: "Reveal the mechanism and its boundary." }, { title: "Apply", body: "Convert the model into the next action." }], active = 1 } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "ab", CSS), list = htmlNode("div", "ab-list"), wraps = [];
  [...items].slice(0, 3).forEach((item, index) => { const wrap = htmlNode("article", "ab-wrap"), beam = htmlNode("i", "ab-beam"), card = htmlNode("div", "ab-card"); card.append(htmlNode("div", "ab-step", `STEP / 0${index + 1}`), htmlNode("div", "ab-title", item.title), htmlNode("div", "ab-body", item.body), htmlNode("div", "ab-status", index === active ? "ACTIVE" : "QUEUED")); wrap.append(beam, card); list.appendChild(wrap); wraps.push({ wrap, beam }); });
  element.appendChild(list); const state = { progress: 0 }, activeIndex = Math.max(0, Math.min(wraps.length - 1, Number(active) || 0));
  function render() { const p = clamp01(state.progress); wraps.forEach(({ wrap, beam }, index) => { const on = index === activeIndex ? p : p * .08; beam.style.setProperty("--active", String(on)); beam.style.setProperty("--angle", `${-110 + p * 430}deg`); wrap.style.transform = `translateY(${(1-clamp01(p*1.4-index*.12))*22}px) scale(${index === activeIndex ? .985 + p*.015 : 1})`; wrap.style.opacity = String(.18 + clamp01(p*1.4-index*.12)*.82); }); }
  const enter = gsap.timeline({ paused: true }).to(state, { progress: 1, duration: 1.25, ease: "power2.inOut", onUpdate: render });
  const emphasis = gsap.timeline({ paused: true }).to(wraps[activeIndex].wrap, { scale: 1.025, duration: .22 }).to(wraps[activeIndex].wrap, { scale: 1, duration: .28 });
  const dim = gsap.timeline({ paused: true }).to(element, { autoAlpha: .32, duration: .28 });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, y: -14, duration: .35 });
  const segments = { enter, emphasis, dim, exit }; render();
  return { segments, seek(frame) { enter.time(Math.max(0, frame) / fps); }, destroy() { destroyFidelity(element, segments); } };
}
