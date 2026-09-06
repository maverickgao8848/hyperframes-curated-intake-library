import {
  createFidelityHost,
  destroyFidelity,
  htmlNode,
  standardTimelines,
} from "../fidelity-runtime.js";

const CSS = `
.comp-wavy-field{position:relative;width:100%;min-height:360px;overflow:hidden;border-radius:var(--comp-radius,22px);background:#05030b;color:#fff}
.comp-wavy-field .wf-canvas{display:block;width:100%;height:360px}
.comp-wavy-field .wf-shade{position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,transparent 0 22%,rgba(5,3,11,.84) 78%)}
.comp-wavy-field .wf-copy{position:absolute;inset:0;display:grid;place-items:center;text-align:center;font-family:var(--comp-font-sans,sans-serif)}
.comp-wavy-field .wf-copy strong{font-size:clamp(34px,6vw,68px);letter-spacing:-.055em}
.comp-wavy-field .wf-copy span{display:block;margin-top:10px;font:600 10px/1 var(--comp-font-mono,monospace);letter-spacing:.25em;color:rgba(255,255,255,.56)}
`;

export const meta = { id: "wavy-field", version: 2, candidateId: "EDU-FOCUS-03" };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const { amplitude = 42, frequency = 1.35, phase = 0, label = "Signals become structure" } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "wf", CSS);
  const canvas = htmlNode("canvas", "wf-canvas");
  canvas.width = 920;
  canvas.height = 360;
  const copy = htmlNode("div", "wf-copy");
  const copyInner = htmlNode("div", "");
  copyInner.append(htmlNode("strong", "", label), htmlNode("span", "", "DETERMINISTIC WAVE FIELD"));
  copy.appendChild(copyInner);
  element.append(canvas, htmlNode("div", "wf-shade"), copy);
  const ctx = canvas.getContext("2d");
  const state = { progress: 0 };
  const colors = ["#ff3fa4","#8b5cff","#3c8dff","#25e2d1","#f8e45d"];

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#05030b";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const amp = Math.max(8, Number(amplitude) || 42);
    const freq = Math.max(.2, Number(frequency) || 1.35);
    const t = Number(phase) + state.progress * Math.PI * 2;
    for (let line = 0; line < 18; line += 1) {
      ctx.beginPath();
      const baseY = 88 + line * 11;
      for (let x = -10; x <= canvas.width + 10; x += 6) {
        const normalized = x / canvas.width;
        const envelope = Math.sin(Math.PI * normalized);
        const y = baseY
          + Math.sin(normalized * Math.PI * 2 * freq + t + line * .23) * amp * envelope
          + Math.sin(normalized * 15 - t * .55 + line * .41) * 8;
        if (x === -10) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = colors[line % colors.length];
      ctx.globalAlpha = .12 + (line % 5) * .045;
      ctx.lineWidth = 1.2;
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  const { enter, emphasis, dim, exit } = standardTimelines(gsap, element, [canvas, copyInner], state, render);
  const segments = { enter, emphasis, dim, exit };
  return {
    segments,
    seek(localFrame) { enter.time(Math.max(0, localFrame) / fps); },
    destroy() { destroyFidelity(element, segments); },
  };
}
