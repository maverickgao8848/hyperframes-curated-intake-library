import { createFidelityHost, destroyFidelity, htmlNode, clamp01 } from "../fidelity-runtime.js";

const CSS = `
.comp-teaching-bento{width:100%;min-height:410px;padding:24px;border-radius:24px;overflow:hidden;color:var(--comp-ink,#f7f8fb);font-family:var(--comp-font-sans,sans-serif)}
.comp-teaching-bento .tb-grid{display:grid;grid-template-columns:1.45fr 1fr 1fr;grid-template-rows:1fr 1fr;gap:14px;min-height:362px;perspective:1000px}
.comp-teaching-bento .tb-card{position:relative;overflow:hidden;padding:22px;border:1px solid var(--comp-line,rgba(255,255,255,.13));border-radius:18px;background:linear-gradient(145deg,var(--comp-surface-strong,#171d28),var(--comp-surface,#0d1118));box-shadow:0 20px 55px rgba(0,0,0,.22);transform-style:preserve-3d}
.comp-teaching-bento .tb-card:first-child{grid-row:1/3;padding:30px}.comp-teaching-bento .tb-card:after{content:"";position:absolute;inset:-35%;background:radial-gradient(circle at var(--bx,20%) var(--by,20%),color-mix(in srgb,var(--comp-accent,#78a8ff) 28%,transparent),transparent 32%);opacity:var(--glow,0)}
.comp-teaching-bento .tb-index{position:relative;z-index:2;font:800 9px/1 var(--comp-font-mono,monospace);letter-spacing:.18em;color:var(--comp-accent,#78a8ff)}
.comp-teaching-bento .tb-title{position:relative;z-index:2;margin-top:14px;font-size:22px;font-weight:720;line-height:1.08;letter-spacing:-.025em}.comp-teaching-bento .tb-card:first-child .tb-title{font-size:36px}
.comp-teaching-bento .tb-body{position:relative;z-index:2;margin-top:13px;color:var(--comp-muted,#9aa6b6);font-size:13px;line-height:1.45}.comp-teaching-bento .tb-card:first-child .tb-body{font-size:16px;max-width:90%}
.comp-teaching-bento .tb-meter{position:absolute;z-index:2;left:30px;right:30px;bottom:30px;height:5px;border-radius:5px;background:var(--comp-line,rgba(255,255,255,.12));overflow:hidden}.comp-teaching-bento .tb-meter i{display:block;height:100%;width:var(--meter,0%);background:var(--comp-accent,#78a8ff);box-shadow:0 0 18px var(--comp-accent,#78a8ff)}
`;
export const meta = { id: "teaching-bento", version: 1, candidateId: "EDU-SUMMARY-04" };
export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const { hero = { title: "One governing idea", body: "Lead with the model, then attach the facts that explain and prove it." }, items = [
    { title: "Mechanism", body: "Why it happens" }, { title: "Evidence", body: "What proves it" },
    { title: "Boundary", body: "When it fails" }, { title: "Action", body: "What to do next" },
  ], focus = 0 } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "tb", CSS);
  const grid = htmlNode("div", "tb-grid"), cards = [], data = [hero, ...items].slice(0, 5);
  data.forEach((item, index) => {
    const card = htmlNode("article", "tb-card");
    card.append(htmlNode("div", "tb-index", index ? `SUPPORT / 0${index}` : "GOVERNING IDEA"), htmlNode("div", "tb-title", item.title), htmlNode("div", "tb-body", item.body));
    if (!index) { const meter = htmlNode("div", "tb-meter"); meter.appendChild(htmlNode("i")); card.appendChild(meter); }
    grid.appendChild(card); cards.push(card);
  });
  element.appendChild(grid);
  const state = { progress: 0 }, focusIndex = Math.max(0, Math.min(cards.length - 1, Number(focus) || 0));
  function render() {
    const p = state.progress;
    cards.forEach((card, index) => {
      const local = clamp01(p * 1.45 - index * .12, 0);
      card.style.opacity = String(.18 + local * .82);
      card.style.transform = `translateY(${(1-local)*26}px) rotateX(${(1-local)*6}deg) scale(${index === focusIndex ? 1 + local*.018 : 1})`;
      card.style.setProperty("--glow", String(index === focusIndex ? local : local * .12));
      card.style.setProperty("--bx", `${18 + index * 17}%`); card.style.setProperty("--by", `${22 + index * 11}%`);
    });
    cards[0]?.style.setProperty("--meter", `${Math.round(p * 100)}%`);
  }
  const enter = gsap.timeline({ paused: true }).to(state, { progress: 1, duration: 1.25, ease: "power3.out", onUpdate: render });
  const emphasis = gsap.timeline({ paused: true }).to(cards[focusIndex], { scale: 1.035, duration: .24 }).to(cards[focusIndex], { scale: 1.018, duration: .28 });
  const dim = gsap.timeline({ paused: true }).to(element, { autoAlpha: .32, duration: .3 });
  const exit = gsap.timeline({ paused: true }).to(cards, { autoAlpha: 0, y: -18, duration: .35, stagger: .03 });
  const segments = { enter, emphasis, dim, exit }; render();
  return { segments, seek(frame) { enter.time(Math.max(0, frame) / fps); }, destroy() { destroyFidelity(element, segments); } };
}
