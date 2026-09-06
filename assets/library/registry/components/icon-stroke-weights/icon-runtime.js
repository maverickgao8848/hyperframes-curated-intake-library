import {
  createFidelityHost,
  createStandardSegments,
  destroyFidelity,
  htmlNode,
  normalizeLocalFrame,
  validateParams,
} from "./fidelity-runtime.js";
import { FROZEN_ICONS, FROZEN_ICON_IDS } from "./frozen-icon-assets.js";

const fail = (id, message) => { throw new Error(`[${id}] ${message}`); };
const allowedWeights = Object.freeze([1.5, 2, 2.5, 3]);

function frozenSvg(asset, className) {
  const documentNode = new DOMParser().parseFromString(asset.svg, "image/svg+xml");
  if (documentNode.querySelector("parsererror")) throw new Error("Frozen SVG failed to parse");
  const svg = document.importNode(documentNode.documentElement, true);
  svg.classList.add(className);
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  svg.removeAttribute("width");
  svg.removeAttribute("height");
  return svg;
}

export function validateIconParams(id, params, kind) {
  if (!FROZEN_ICONS[params.iconId]) {
    fail(id, `iconId must be one of: ${FROZEN_ICON_IDS.join(", ")}`);
  }
  if (kind === "weights" && !allowedWeights.includes(params.strokeWeight)) {
    fail(id, `strokeWeight must be one of: ${allowedWeights.join(", ")}`);
  }
}

export function mountIconComponent(root, context = {}, meta, prefix, config) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  validateIconParams(meta.id, params, config.kind);
  const asset = FROZEN_ICONS[params.iconId];
  const css = `.comp-${meta.id}{position:relative;display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);align-items:center;width:100%;height:100%;min-width:0;min-height:220px;padding:var(--comp-space-5);gap:var(--comp-space-4);border:1px solid var(--comp-line);border-radius:var(--comp-radius-md);background:var(--comp-surface);color:var(--comp-ink);font-family:var(--comp-font-sans);overflow:hidden;container-type:inline-size}.comp-${meta.id} .${prefix}-visual{display:grid;place-items:center;width:100%;min-width:0;min-height:min(220px,35cqw);aspect-ratio:1;border-radius:var(--comp-radius-md);background:color-mix(in srgb,var(--comp-accent) 13%,var(--comp-surface-strong));color:var(--comp-accent)}.comp-${meta.id} .${prefix}-icon{width:min(58%,160px);height:auto;aspect-ratio:1;overflow:visible}.comp-${meta.id} .${prefix}-copy{min-width:0}.comp-${meta.id} .${prefix}-eyebrow{color:var(--comp-accent);font:700 11px/1.2 var(--comp-font-mono);letter-spacing:.14em;text-transform:uppercase}.comp-${meta.id} .${prefix}-title{margin:9px 0 0;font:800 clamp(22px,3.4vw,48px)/1.03 var(--comp-font-display);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-label{margin:11px 0 0;color:var(--comp-muted);font:600 clamp(14px,1.7vw,21px)/1.35 var(--comp-font-sans);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-path{display:block;margin-top:14px;color:var(--comp-muted);font:500 10px/1.35 var(--comp-font-mono);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-scale{display:flex;align-items:end;gap:9px;margin-top:15px}.comp-${meta.id} .${prefix}-sample{display:grid;place-items:center;flex:1;min-width:0;padding:8px 4px;border-top:1px solid var(--comp-line);color:var(--comp-muted);font:600 9px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-sample svg{width:30px;height:30px;margin-bottom:5px;color:var(--comp-accent)}@container (max-width:520px){.comp-${meta.id}{grid-template-columns:1fr;grid-template-rows:minmax(0,1fr) auto;padding:var(--comp-space-3)}.comp-${meta.id} .${prefix}-visual{min-height:min(150px,40cqw);aspect-ratio:auto}.comp-${meta.id} .${prefix}-icon{width:min(34%,110px);height:auto}.comp-${meta.id} .${prefix}-path{display:none}}`;
  const { element, gsap } = createFidelityHost(root, context, meta, prefix, css);
  element.dataset.iconId = params.iconId;
  element.dataset.assetPath = asset.path;
  element.dataset.assetSha256 = asset.sha256;
  const visual = htmlNode("div", `${prefix}-visual`);
  const icon = frozenSvg(asset, `${prefix}-icon`);
  icon.style.strokeWidth = String(params.strokeWeight);
  visual.appendChild(icon);
  const copy = htmlNode("div", `${prefix}-copy`);
  copy.append(
    htmlNode("div", `${prefix}-eyebrow`, config.kind === "weights" ? "CONTROLLED STROKE HIERARCHY" : "FROZEN LUCIDE SUBSET"),
    htmlNode("h2", `${prefix}-title`, params.title),
    htmlNode("p", `${prefix}-label`, params.label),
    htmlNode("code", `${prefix}-path`, asset.path),
  );
  const marks = [visual, copy];
  if (config.kind === "weights") {
    const scale = htmlNode("div", `${prefix}-scale`);
    for (const weight of allowedWeights) {
      const sample = htmlNode("div", `${prefix}-sample`);
      const sampleIcon = frozenSvg(asset, `${prefix}-sample-icon`);
      sampleIcon.style.strokeWidth = String(weight);
      sample.append(sampleIcon, htmlNode("span", null, String(weight)));
      scale.appendChild(sample);
      marks.push(sample);
    }
    copy.appendChild(scale);
  }
  element.append(visual, copy);
  const state = { progress: 0 };
  const render = () => {
    const progress = normalizeLocalFrame(state.progress * params.durationFrames, params.durationFrames) / params.durationFrames;
    marks.forEach((mark, index) => { mark.style.opacity = progress >= index / Math.max(1, marks.length) ? "" : "0"; });
  };
  const segments = createStandardSegments(gsap, element, marks, state, render);
  state.progress = 1;
  render();
  return {
    segments,
    seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); },
    destroy() { destroyFidelity(element, segments); },
  };
}
