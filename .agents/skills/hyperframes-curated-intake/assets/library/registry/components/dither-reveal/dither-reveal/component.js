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
.comp-dither-reveal{position:relative;width:100%;min-height:360px;overflow:hidden;border-radius:var(--comp-radius,22px);background:#050505;color:#fff;font-family:var(--comp-font-mono,monospace)}
.comp-dither-reveal .dr-canvas{display:block;width:100%;height:360px;image-rendering:pixelated}
.comp-dither-reveal .dr-label{position:absolute;left:24px;top:22px;padding:8px 11px;border:1px solid rgba(255,255,255,.24);border-radius:999px;background:rgba(0,0,0,.58);font-size:10px;letter-spacing:.18em;text-transform:uppercase}
.comp-dither-reveal .dr-scale{position:absolute;left:24px;right:24px;bottom:20px;display:flex;justify-content:space-between;font-size:9px;letter-spacing:.14em;color:rgba(255,255,255,.62)}
`;

const BAYER_4 = [
  0,8,2,10,
  12,4,14,6,
  3,11,1,9,
  15,7,13,5,
].map((value) => (value + 0.5) / 16);

function hexRgb(value, fallback) {
  const match = String(value || fallback).match(/^#?([\da-f]{2})([\da-f]{2})([\da-f]{2})$/i);
  return match ? match.slice(1).map((part) => parseInt(part, 16)) : [255,255,255];
}

function procedural(width, height) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, "#ff3d77");
  gradient.addColorStop(0.48, "#f8e16c");
  gradient.addColorStop(1, "#4f7cff");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = "rgba(5,5,7,.88)";
  ctx.beginPath();
  ctx.arc(width * .55, height * .46, height * .28, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#f5f5ee";
  ctx.font = "800 96px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("DITHER", width * .52, height * .56);
  return canvas;
}

export const meta = { id: "dither-reveal", version: 2, candidateId: "EDU-REVEAL-03" };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const {
    mediaRef,
    gridSize = 4,
    ditherMode = "bayer",
    colorMode = "duotone",
    invert = false,
    threshold = 0.5,
    primaryColor = "#080808",
    secondaryColor = "#f5f5ed",
  } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "dr", CSS);
  const canvas = htmlNode("canvas", "dr-canvas");
  canvas.width = 920;
  canvas.height = 360;
  const label = htmlNode("div", "dr-label", `${String(ditherMode).toUpperCase()} · ${String(colorMode).toUpperCase()}`);
  const scale = htmlNode("div", "dr-scale");
  scale.append(htmlNode("span", "", "0.00 BLACK"), htmlNode("span", "", "ORDERED THRESHOLD"), htmlNode("span", "", "1.00 WHITE"));
  element.append(canvas, label, scale);
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const state = { progress: 0 };
  let source = procedural(920, 360);
  let image = null;
  const first = hexRgb(primaryColor, "#080808");
  const second = hexRgb(secondaryColor, "#f5f5ed");

  function render() {
    const cell = Math.max(2, Math.min(12, Number(gridSize) || 4));
    const sampleWidth = Math.ceil(canvas.width / cell);
    const sampleHeight = Math.ceil(canvas.height / cell);
    const offscreen = document.createElement("canvas");
    offscreen.width = sampleWidth;
    offscreen.height = sampleHeight;
    const offctx = offscreen.getContext("2d", { willReadFrequently: true });
    offctx.drawImage(source, 0, 0, source.naturalWidth || source.width, source.naturalHeight || source.height, 0, 0, sampleWidth, sampleHeight);
    const pixels = offctx.getImageData(0, 0, sampleWidth, sampleHeight).data;
    ctx.fillStyle = `rgb(${first.join(" ")})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const animatedThreshold = Number(threshold) + (0.5 - clamp01(state.progress)) * 0.62;
    for (let y = 0; y < sampleHeight; y += 1) {
      for (let x = 0; x < sampleWidth; x += 1) {
        const index = (y * sampleWidth + x) * 4;
        const r = pixels[index];
        const g = pixels[index + 1];
        const b = pixels[index + 2];
        let luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        if (invert) luminance = 1 - luminance;
        let pattern = BAYER_4[(y % 4) * 4 + (x % 4)];
        if (ditherMode === "halftone") pattern = (Math.sin(x * 1.7) + Math.cos(y * 1.7) + 2) / 4;
        if (ditherMode === "noise") pattern = seededUnit(83, y * sampleWidth + x);
        const on = luminance + (pattern - 0.5) * 0.5 > animatedThreshold;
        if (colorMode === "original" && on) ctx.fillStyle = `rgb(${r} ${g} ${b})`;
        else ctx.fillStyle = `rgb(${(on ? second : first).join(" ")})`;
        ctx.fillRect(x * cell, y * cell, cell + 0.25, cell + 0.25);
      }
    }
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
  const { enter, emphasis, dim, exit } = standardTimelines(gsap, element, [canvas, label, scale], state, render);
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
