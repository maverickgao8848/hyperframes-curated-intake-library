import {
  clamp01,
  createFidelityHost,
  destroyFidelity,
  htmlNode,
  standardTimelines,
} from "../fidelity-runtime.js";

const CSS = `
.comp-glare-card{position:relative;width:100%;min-height:360px;display:grid;place-items:center;overflow:hidden;border-radius:var(--comp-radius,22px);background:#08090c;color:#f7f7f4;perspective:900px;font-family:var(--comp-font-sans,sans-serif)}
.comp-glare-card .gc-card{position:relative;width:min(68%,520px);height:270px;overflow:hidden;border:1px solid rgba(255,255,255,.18);border-radius:24px;background:linear-gradient(145deg,#20222b,#0e1015);box-shadow:0 35px 90px rgba(0,0,0,.56);transform-style:preserve-3d}
.comp-glare-card .gc-noise{position:absolute;inset:0;opacity:.2;background-image:radial-gradient(rgba(255,255,255,.35) .6px,transparent .7px);background-size:5px 5px}
.comp-glare-card .gc-glare{position:absolute;inset:-45%;background:conic-gradient(from 190deg,transparent 0 28%,rgba(142,235,255,.68) 38%,rgba(255,176,244,.5) 46%,transparent 56% 100%);mix-blend-mode:screen;transform:translate3d(var(--gc-x,-20%),var(--gc-y,-10%),70px) rotate(var(--gc-r,-18deg));opacity:var(--gc-a,.2)}
.comp-glare-card .gc-copy{position:absolute;left:30px;right:30px;bottom:30px;z-index:2;transform:translateZ(58px)}
.comp-glare-card .gc-title{font-size:34px;font-weight:760;letter-spacing:-.04em}
.comp-glare-card .gc-body{max-width:380px;margin-top:10px;color:rgba(255,255,255,.62);font-size:13px;line-height:1.5}
.comp-glare-card .gc-mark{position:absolute;right:28px;top:25px;z-index:2;font:700 10px/1 var(--comp-font-mono,monospace);letter-spacing:.18em;color:#b8f5ff}
`;

export const meta = { id: "glare-card", version: 2, candidateId: "EDU-DEPTH-03" };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const { title = "Precision surface", body = "A controlled light pass reveals material and hierarchy.", lightProgress = 0.78 } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "gc", CSS);
  const card = htmlNode("article", "gc-card");
  card.setAttribute("data-layout-allow-overflow", "");
  const glare = htmlNode("div", "gc-glare");
  const copy = htmlNode("div", "gc-copy");
  copy.append(htmlNode("div", "gc-title", title), htmlNode("div", "gc-body", body));
  card.append(htmlNode("div", "gc-noise"), glare, htmlNode("div", "gc-mark", "OPTICAL / 01"), copy);
  element.appendChild(card);
  const state = { progress: 0 };
  const strength = clamp01(lightProgress, .78);
  function render() {
    const p = state.progress;
    card.style.transform = `rotateX(${8-p*13}deg) rotateY(${-12+p*19}deg)`;
    glare.style.setProperty("--gc-x", `${-48+p*88}%`);
    glare.style.setProperty("--gc-y", `${-26+p*52}%`);
    glare.style.setProperty("--gc-r", `${-28+p*52}deg`);
    glare.style.setProperty("--gc-a", String(.1+p*.78*strength));
  }
  const { enter, emphasis, dim, exit } = standardTimelines(gsap, element, [card, copy], state, render);
  const segments = { enter, emphasis, dim, exit };
  return {
    segments,
    seek(localFrame) { enter.time(Math.max(0, localFrame) / fps); },
    destroy() { destroyFidelity(element, segments); },
  };
}
