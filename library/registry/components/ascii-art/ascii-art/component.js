import { assertProjectLocalMediaRef } from "../runtime.js";
import {
  clamp01,
  createFidelityHost,
  destroyFidelity,
  htmlNode,
  seededUnit,
  standardTimelines,
} from "../fidelity-runtime.js";

const CSS = `
.comp-ascii-art{position:relative;width:100%;min-height:360px;overflow:hidden;border-radius:var(--comp-radius,22px);background:#050706;color:var(--comp-ink,#f2f5f2);font-family:var(--comp-font-mono,"JetBrains Mono",monospace)}
.comp-ascii-art .aa-canvas{display:block;width:100%;height:360px;background:radial-gradient(circle at 50% 38%,#11251e 0,#050706 62%)}
.comp-ascii-art .aa-hud{position:absolute;inset:20px 22px auto;display:flex;align-items:center;justify-content:space-between;z-index:2;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:rgba(210,255,229,.62)}
.comp-ascii-art .aa-chip{padding:7px 10px;border:1px solid rgba(97,255,170,.28);border-radius:999px;background:rgba(5,14,10,.72)}
.comp-ascii-art .aa-scan{position:absolute;left:0;right:0;top:0;height:2px;background:#63ffad;box-shadow:0 0 22px 5px rgba(70,255,155,.5);transform-origin:left center;pointer-events:none}
`;

const CHARSETS = {
  standard: " .,:;i1tfLCG08@",
  blocks: " ░▒▓█",
  binary: " 01",
  braille: " ⠁⠃⠇⠏⠟⠿⡿⣿",
  dense: " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
};

function proceduralSource(width, height) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  const gradient = ctx.createRadialGradient(width * 0.5, height * 0.38, 8, width * 0.5, height * 0.5, width * 0.52);
  gradient.addColorStop(0, "#e8fff1");
  gradient.addColorStop(0.32, "#63ffad");
  gradient.addColorStop(1, "#07100c");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = "#020403";
  ctx.beginPath();
  ctx.arc(width * 0.5, height * 0.34, height * 0.16, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(width * 0.5, height * 0.77, width * 0.23, height * 0.32, 0, 0, Math.PI * 2);
  ctx.fill();
  return canvas;
}

export const meta = { id: "ascii-art", version: 2, candidateId: "EDU-CODE-02" };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const {
    mediaRef,
    resolution = 92,
    charset = "standard",
    colored = false,
    inverted = false,
    objectFit = "cover",
  } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "aa", CSS);
  const canvas = htmlNode("canvas", "aa-canvas");
  canvas.width = 920;
  canvas.height = 360;
  const hud = htmlNode("div", "aa-hud");
  hud.append(htmlNode("span", "", "IMAGE → LUMINANCE → GLYPH"), htmlNode("span", "aa-chip", `${resolution} COL · ${String(charset).toUpperCase()}`));
  const scan = htmlNode("div", "aa-scan");
  element.append(canvas, hud, scan);
  const ctx = canvas.getContext("2d");
  const state = { progress: 0 };
  let source = proceduralSource(920, 360);
  let image = null;

  function fitRect(sw, sh, dw, dh) {
    if (objectFit === "fill") return [0, 0, sw, sh];
    const scale = objectFit === "contain" ? Math.min(dw / sw, dh / sh) : Math.max(dw / sw, dh / sh);
    const cropW = dw / scale;
    const cropH = dh / scale;
    return [(sw - cropW) / 2, (sh - cropH) / 2, cropW, cropH];
  }

  function sample() {
    const columns = Math.max(24, Math.min(160, Number(resolution) || 92));
    const rows = Math.max(10, Math.round(columns * 0.39));
    const sampleCanvas = document.createElement("canvas");
    sampleCanvas.width = columns;
    sampleCanvas.height = rows;
    const sampleCtx = sampleCanvas.getContext("2d", { willReadFrequently: true });
    const sw = source.naturalWidth || source.width;
    const sh = source.naturalHeight || source.height;
    const [sx, sy, cropW, cropH] = fitRect(sw, sh, columns, rows);
    sampleCtx.drawImage(source, sx, sy, cropW, cropH, 0, 0, columns, rows);
    return { columns, rows, pixels: sampleCtx.getImageData(0, 0, columns, rows).data };
  }

  function render() {
    const { columns, rows, pixels } = sample();
    const glyphs = CHARSETS[charset] || String(charset || CHARSETS.standard);
    const ordered = inverted ? [...glyphs].reverse().join("") : glyphs;
    const cellW = canvas.width / columns;
    const cellH = canvas.height / rows;
    const shown = Math.floor(columns * rows * clamp01(state.progress));
    ctx.fillStyle = "#050706";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.font = `${Math.max(6, cellH * 0.92)}px "JetBrains Mono",monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (let index = 0; index < shown; index += 1) {
      const x = index % columns;
      const y = Math.floor(index / columns);
      const pixelIndex = index * 4;
      const r = pixels[pixelIndex];
      const g = pixels[pixelIndex + 1];
      const b = pixels[pixelIndex + 2];
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
      const glyph = ordered[Math.min(ordered.length - 1, Math.floor(luminance * ordered.length))] || " ";
      ctx.globalAlpha = 0.42 + luminance * 0.58;
      ctx.fillStyle = colored ? `rgb(${r} ${g} ${b})` : "#7dffb8";
      ctx.fillText(glyph, x * cellW + cellW / 2, y * cellH + cellH / 2);
    }
    ctx.globalAlpha = 1;
    scan.style.transform = `translateY(${state.progress * 358}px) scaleX(${0.35 + state.progress * 0.65})`;
  }

  if (mediaRef) {
    const safeRef = assertProjectLocalMediaRef(meta.id, mediaRef);
    image = new Image();
    image.onload = () => {
      source = image;
      render();
    };
    image.src = safeRef;
  }
  const { enter, emphasis, dim, exit } = standardTimelines(gsap, element, [hud, canvas], state, render);
  const segments = { enter, emphasis, dim, exit };
  return {
    segments,
    seek(localFrame) {
      enter.time(Math.max(0, localFrame) / fps);
    },
    destroy() {
      if (image) image.onload = null;
      destroyFidelity(element, segments);
    },
  };
}
