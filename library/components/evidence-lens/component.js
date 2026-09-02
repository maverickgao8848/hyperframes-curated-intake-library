import { createFidelityHost, destroyFidelity, htmlNode, clamp01 } from "../fidelity-runtime.js";

const CSS = `
.comp-evidence-lens{position:relative;width:100%;min-height:390px;overflow:hidden;border-radius:24px;color:var(--comp-ink,#f7f8fb);font-family:var(--comp-font-sans,sans-serif)}
.comp-evidence-lens .el-sheet{position:absolute;inset:18px;padding:34px 38px;border:1px solid var(--comp-line,rgba(255,255,255,.14));border-radius:20px;background:var(--comp-surface,#10141c);box-shadow:0 30px 90px rgba(0,0,0,.34)}
.comp-evidence-lens .el-kicker{font:700 10px/1 var(--comp-font-mono,monospace);letter-spacing:.18em;color:var(--comp-accent,#78a8ff)}
.comp-evidence-lens .el-title{max-width:76%;margin-top:18px;font-size:32px;font-weight:760;line-height:1.05;letter-spacing:-.035em}
.comp-evidence-lens .el-lines{display:grid;gap:12px;margin-top:26px}.comp-evidence-lens .el-line{height:9px;border-radius:9px;background:var(--comp-line,rgba(255,255,255,.12))}.comp-evidence-lens .el-line:nth-child(2){width:82%}.comp-evidence-lens .el-line:nth-child(3){width:63%}
.comp-evidence-lens .el-proof{position:absolute;left:38px;right:38px;bottom:34px;padding:17px 20px;border-left:3px solid var(--comp-accent,#78a8ff);background:color-mix(in srgb,var(--comp-accent,#78a8ff) 10%,transparent);font:650 16px/1.35 var(--comp-font-sans,sans-serif)}
.comp-evidence-lens .el-dim{position:absolute;inset:0;background:rgba(2,4,8,.42)}
.comp-evidence-lens .el-lens{position:absolute;width:190px;height:190px;border:2px solid color-mix(in srgb,var(--comp-accent,#78a8ff) 80%,white);border-radius:50%;overflow:hidden;background:var(--comp-surface-strong,#161d28);box-shadow:0 0 0 9px rgba(255,255,255,.05),0 28px 70px rgba(0,0,0,.58),0 0 34px color-mix(in srgb,var(--comp-accent,#78a8ff) 38%,transparent);transform:translate(-50%,-50%)}
.comp-evidence-lens .el-magnified{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:25px;background:radial-gradient(circle at 32% 25%,color-mix(in srgb,var(--comp-accent,#78a8ff) 18%,var(--comp-surface-strong,#161d28)),var(--comp-surface,#10141c));transform-origin:center}.comp-evidence-lens .el-zoom-kicker{font:800 9px/1 var(--comp-font-mono,monospace);letter-spacing:.15em;color:var(--comp-accent,#78a8ff)}.comp-evidence-lens .el-zoom-detail{margin-top:12px;font-size:17px;font-weight:720;line-height:1.25}
.comp-evidence-lens .el-tag{position:absolute;z-index:3;padding:8px 11px;border-radius:999px;background:var(--comp-accent,#78a8ff);color:#07101e;font:800 9px/1 var(--comp-font-mono,monospace);letter-spacing:.12em;white-space:nowrap}
`;

export const meta = { id: "evidence-lens", version: 1, candidateId: "EDU-PROOF-06" };

function sheetContent(title, sourceLabel, detail) {
  const fragment = document.createDocumentFragment();
  fragment.append(htmlNode("div", "el-kicker", sourceLabel), htmlNode("div", "el-title", title));
  const lines = htmlNode("div", "el-lines");
  for (let index = 0; index < 3; index += 1) lines.appendChild(htmlNode("i", "el-line"));
  fragment.append(lines, htmlNode("div", "el-proof", detail));
  return fragment;
}

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const {
    title = "The claim becomes credible when the exact evidence is visible",
    sourceLabel = "SOURCE / EXHIBIT 04",
    detail = "Focus the viewer on the sentence, value, or interface state that proves the point.",
    focusX = 0.72,
    focusY = 0.68,
    zoomFactor = 1.72,
  } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "el", CSS);
  const sheet = htmlNode("article", "el-sheet");
  sheet.append(sheetContent(title, sourceLabel, detail));
  const dim = htmlNode("div", "el-dim");
  const lens = htmlNode("div", "el-lens");
  const magnified = htmlNode("div", "el-magnified");
  magnified.append(htmlNode("div", "el-zoom-kicker", sourceLabel), htmlNode("div", "el-zoom-detail", detail));
  lens.appendChild(magnified);
  const tag = htmlNode("div", "el-tag", "EVIDENCE LOCK");
  element.append(sheet, dim, lens, tag);
  const state = { progress: 0 };
  const x = clamp01(focusX, .72), y = clamp01(focusY, .68), zoom = Math.max(1.15, Math.min(2.4, Number(zoomFactor) || 1.72));
  function render() {
    const p = state.progress;
    const px = 20 + x * 60, py = 24 + y * 58;
    lens.style.left = `${px}%`; lens.style.top = `${py}%`;
    lens.style.transform = `translate(-50%,-50%) scale(${.7 + p * .3})`;
    dim.style.opacity = String(p * .9);
    magnified.style.transform = `scale(${1 + p * Math.min(.12, (zoom - 1) * .08)})`;
    tag.style.left = `calc(${px}% + 72px)`; tag.style.top = `calc(${py}% - 104px)`;
    tag.style.opacity = String(Math.max(0, (p - .45) / .55));
  }
  const enter = gsap.timeline({ paused: true })
    .fromTo(element, { autoAlpha: 0 }, { autoAlpha: 1, duration: .22, ease: "power2.out" }, 0)
    .to(state, { progress: 1, duration: 1.15, ease: "power3.inOut", onUpdate: render }, .08);
  const emphasis = gsap.timeline({ paused: true }).to(lens, { scale: 1.035, duration: .2 }).to(lens, { scale: 1, duration: .26 });
  const dimSegment = gsap.timeline({ paused: true }).to(element, { autoAlpha: .35, duration: .25 });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, scale: .985, duration: .35, ease: "power2.in" });
  const segments = { enter, emphasis, dim: dimSegment, exit };
  render();
  return { segments, seek(frame) { enter.time(Math.max(0, frame) / fps); }, destroy() { destroyFidelity(element, segments); } };
}
