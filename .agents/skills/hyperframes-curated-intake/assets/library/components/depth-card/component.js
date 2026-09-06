import {
  clamp01,
  createFidelityHost,
  destroyFidelity,
  htmlNode,
  standardTimelines,
} from "../fidelity-runtime.js";

const CSS = `
.comp-depth-card{position:relative;width:100%;min-height:360px;display:grid;place-items:center;overflow:hidden;border-radius:var(--comp-radius,22px);background:radial-gradient(circle at 50% 38%,#24304b 0,#090b11 64%);color:#f8fafc;perspective:900px;font-family:var(--comp-font-sans,sans-serif)}
.comp-depth-card .dc-card{position:relative;width:min(72%,560px);height:260px;border:1px solid rgba(255,255,255,.2);border-radius:24px;background:linear-gradient(145deg,rgba(255,255,255,.13),rgba(255,255,255,.035));box-shadow:0 45px 100px rgba(0,0,0,.48);transform-style:preserve-3d}
.comp-depth-card .dc-grid{position:absolute;inset:0;border-radius:inherit;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px}
.comp-depth-card .dc-kicker{position:absolute;left:30px;top:28px;font:600 10px/1 var(--comp-font-mono,monospace);letter-spacing:.2em;color:#93c5fd;transform:translateZ(44px)}
.comp-depth-card .dc-title{position:absolute;left:30px;top:60px;max-width:70%;font-size:38px;font-weight:760;line-height:1.02;letter-spacing:-.045em;transform:translateZ(72px)}
.comp-depth-card .dc-chip{position:absolute;left:30px;bottom:27px;padding:10px 13px;border-radius:999px;background:#e7efff;color:#101725;font:700 10px/1 var(--comp-font-mono,monospace);transform:translateZ(54px)}
.comp-depth-card .dc-orb{position:absolute;right:34px;bottom:32px;width:104px;height:104px;border-radius:32px;background:linear-gradient(145deg,#78a8ff,#7757ff);box-shadow:0 24px 45px rgba(94,85,255,.42);transform:translateZ(92px)}
.comp-depth-card .dc-orb:after{content:"";position:absolute;inset:22px;border:1px solid rgba(255,255,255,.65);border-radius:50%}
`;

export const meta = { id: "depth-card", version: 2, candidateId: "EDU-DEPTH-01" };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const { title = "Make things float in air", layers = ["SURFACE","CONTENT","ACTION"], tilt = 0.72 } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "dc", CSS);
  const card = htmlNode("div", "dc-card");
  const grid = htmlNode("div", "dc-grid");
  const kicker = htmlNode("div", "dc-kicker", Array.isArray(layers) ? layers.join(" · ") : String(layers));
  const heading = htmlNode("div", "dc-title", title);
  const chip = htmlNode("div", "dc-chip", "EXPLODE LAYERS →");
  const orb = htmlNode("div", "dc-orb");
  card.append(grid, kicker, heading, chip, orb);
  element.appendChild(card);
  const state = { progress: 0 };
  const amount = clamp01(tilt, .72);
  function render() {
    const p = state.progress;
    card.style.transform = `rotateX(${(1-p)*12*amount}deg) rotateY(${(1-p)*-18*amount}deg) translateZ(${p*8}px)`;
    grid.style.opacity = String(.25 + p * .75);
    orb.style.transform = `translateZ(${42 + p*72}px) rotate(${(1-p)*-12}deg)`;
    heading.style.transform = `translateZ(${32 + p*62}px)`;
  }
  const { enter, emphasis, dim, exit } = standardTimelines(gsap, element, [card, kicker, heading, chip, orb], state, render);
  const segments = { enter, emphasis, dim, exit };
  return {
    segments,
    seek(localFrame) { enter.time(Math.max(0, localFrame) / fps); },
    destroy() { destroyFidelity(element, segments); },
  };
}
