import {
  createFidelityHost,
  createStandardSegments,
  destroyFidelity,
  htmlNode,
  normalizeLocalFrame,
  validateParams,
} from "./fidelity-runtime.js";
import { FROZEN_ILLUSTRATIONS, FROZEN_SCENE_IDS } from "./frozen-illustration-assets.js";
import { FROZEN_ICONS } from "./frozen-icon-assets.js";

const sceneIcons = Object.freeze({
  thinking: "lightbulb",
  "co-create": "users",
  prompt: "terminal",
  retrieval: "search",
  analytics: "chart-no-axes-combined",
  launch: "git-pull-request",
});
const fail = (id, message) => { throw new Error(`[${id}] ${message}`); };

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

export function validateIllustrationParams(id, params, fixedSceneId) {
  const sceneId = fixedSceneId ?? params.sceneId;
  if (!FROZEN_ILLUSTRATIONS[sceneId]) fail(id, `sceneId must be one of: ${FROZEN_SCENE_IDS.join(", ")}`);
  if (fixedSceneId && params.sceneVariant !== fixedSceneId) {
    fail(id, `sceneVariant must be ${fixedSceneId} for this chapter component`);
  }
  return sceneId;
}

export function mountIllustrationComponent(root, context = {}, meta, prefix, config) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  const sceneId = validateIllustrationParams(meta.id, params, config.fixedSceneId);
  const asset = FROZEN_ILLUSTRATIONS[sceneId];
  const iconAsset = FROZEN_ICONS[sceneIcons[sceneId]];
  const css = `.comp-${meta.id}{position:relative;isolation:isolate;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(220px,.95fr);width:100%;height:100%;min-width:0;min-height:330px;padding:var(--comp-space-6);gap:var(--comp-space-4);border:1px solid var(--comp-line);border-radius:var(--comp-radius-md);background:var(--comp-canvas);color:var(--comp-ink);font-family:var(--comp-font-sans);overflow:hidden;container-type:inline-size}.comp-${meta.id}[data-focal-side="left"]{grid-template-columns:minmax(220px,.95fr) minmax(0,1.05fr)}.comp-${meta.id}[data-focal-side="left"] .${prefix}-art{order:-1}.comp-${meta.id} .${prefix}-copy{position:relative;z-index:3;align-self:end;min-width:0;padding-bottom:var(--comp-space-3)}.comp-${meta.id} .${prefix}-index{display:inline-flex;align-items:center;gap:8px;color:var(--comp-accent);font:750 12px/1 var(--comp-font-mono);letter-spacing:.12em}.comp-${meta.id} .${prefix}-index:before{content:"";width:34px;height:2px;background:currentColor}.comp-${meta.id} .${prefix}-title{max-width:13ch;margin:18px 0 0;font:850 clamp(34px,5.5vw,82px)/.92 var(--comp-font-display);letter-spacing:-.035em;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-caption{max-width:40ch;margin:18px 0 0;color:var(--comp-muted);font:550 clamp(14px,1.55vw,21px)/1.42 var(--comp-font-sans);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-role{display:inline-block;margin-top:18px;padding:7px 10px;border:1px solid var(--comp-line-strong);border-radius:999px;color:var(--comp-muted);font:650 10px/1 var(--comp-font-mono);text-transform:uppercase}.comp-${meta.id} .${prefix}-art{position:relative;z-index:2;display:grid;place-items:end center;min-width:0;min-height:0;border-radius:var(--comp-radius-md);background:linear-gradient(145deg,color-mix(in srgb,var(--comp-accent) 18%,var(--comp-surface)),var(--comp-surface-strong));overflow:hidden}.comp-${meta.id} .${prefix}-orbit{position:absolute;inset:12%;border:1px solid color-mix(in srgb,var(--comp-accent) 55%,transparent);border-radius:50%;transform:scale(.92)}.comp-${meta.id} .${prefix}-orbit:before,.comp-${meta.id} .${prefix}-orbit:after{content:"";position:absolute;inset:14%;border:1px solid var(--comp-line);border-radius:50%}.comp-${meta.id} .${prefix}-orbit:after{inset:31%;background:color-mix(in srgb,var(--comp-accent) 14%,transparent)}.comp-${meta.id} .${prefix}-peep{position:relative;z-index:2;width:auto;height:min(86%,620px);max-width:82%;color:var(--comp-ink)}.comp-${meta.id} .${prefix}-badge{position:absolute;z-index:4;top:var(--comp-space-4);right:var(--comp-space-4);display:grid;place-items:center;width:74px;height:74px;border-radius:50%;background:var(--comp-accent);color:var(--comp-canvas);box-shadow:0 12px 40px color-mix(in srgb,var(--comp-ink) 18%,transparent)}.comp-${meta.id} .${prefix}-badge svg{width:36px;height:36px}.comp-${meta.id}[data-density="sparse"] .${prefix}-orbit:before,.comp-${meta.id}[data-density="sparse"] .${prefix}-orbit:after{display:none}.comp-${meta.id}[data-density="dense"] .${prefix}-art:after{content:"";position:absolute;inset:8%;border:1px dashed color-mix(in srgb,var(--comp-accent) 50%,transparent);border-radius:var(--comp-radius-md)}@container (max-width:620px){.comp-${meta.id},.comp-${meta.id}[data-focal-side]{grid-template-columns:1fr;grid-template-rows:auto minmax(0,1fr);padding:var(--comp-space-4)}.comp-${meta.id} .${prefix}-copy{align-self:start;padding:0}.comp-${meta.id} .${prefix}-title{margin-top:10px;font-size:clamp(26px,8vw,52px)}.comp-${meta.id} .${prefix}-caption{margin-top:10px}.comp-${meta.id} .${prefix}-art{order:2!important}.comp-${meta.id} .${prefix}-peep{height:min(92%,420px)}.comp-${meta.id} .${prefix}-badge{width:54px;height:54px}.comp-${meta.id} .${prefix}-badge svg{width:26px;height:26px}}`;
  const { element, gsap } = createFidelityHost(root, context, meta, prefix, css);
  element.dataset.sceneId = sceneId;
  element.dataset.sceneVariant = params.sceneVariant;
  element.dataset.focalSide = params.focalSide;
  element.dataset.density = params.density;
  element.dataset.accentRole = params.accentRole;
  element.dataset.assetPath = asset.path;
  element.dataset.assetSha256 = asset.sha256;
  element.dataset.sceneRole = "chapter-cover";
  element.dataset.evidenceEligible = "false";
  const copy = htmlNode("div", `${prefix}-copy`);
  copy.append(
    htmlNode("div", `${prefix}-index`, `CHAPTER ${String(params.chapterIndex).padStart(2, "0")}`),
    htmlNode("h2", `${prefix}-title`, params.title),
    htmlNode("p", `${prefix}-caption`, params.caption),
    htmlNode("span", `${prefix}-role`, params.accentRole),
  );
  const art = htmlNode("div", `${prefix}-art`);
  const orbit = htmlNode("div", `${prefix}-orbit`);
  const peep = frozenSvg(asset, `${prefix}-peep`);
  const badge = htmlNode("div", `${prefix}-badge`);
  badge.appendChild(frozenSvg(iconAsset, `${prefix}-scene-icon`));
  art.append(orbit, peep, badge);
  element.append(copy, art);
  const marks = [copy, orbit, peep, badge];
  const state = { progress: 0 };
  const render = () => {
    const progress = normalizeLocalFrame(state.progress * params.durationFrames, params.durationFrames) / params.durationFrames;
    marks.forEach((mark, index) => { mark.style.opacity = progress >= index / marks.length ? "" : "0"; });
    orbit.style.transform = `scale(${.92 + progress * .08})`;
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
