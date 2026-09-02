/**
 * window-card · 窗口容器
 *
 * 承载命令、对话与界面证据的容器，取景框美学：四角 crop-mark 先描画，
 * hairline 边框随后闭合，header 是大写宽字距小标签 + 荧光状态点。
 * 参考形态：终端 `>_` 提示行逐行输出 / 对话窗底部输入条 / 素面板。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-window-card{position:relative;width:var(--comp-window-w,640px);
background:var(--comp-surface,rgba(236,236,236,.04));
border-radius:var(--comp-radius,10px);
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif);
color:var(--comp-ink,#ececec)}
.comp-window-card .wc-frame{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none}
.comp-window-card .wc-frame rect{fill:none;stroke:var(--comp-line,rgba(236,236,236,.22));
stroke-width:1;rx:var(--comp-radius,10px)}
.comp-window-card .wc-corner{position:absolute;width:14px;height:14px;overflow:visible;pointer-events:none}
.comp-window-card .wc-corner path{fill:none;stroke:var(--comp-ink,#ececec);stroke-width:1.5}
.comp-window-card .wc-corner-tl{top:-6px;left:-6px}
.comp-window-card .wc-corner-tr{top:-6px;right:-6px}
.comp-window-card .wc-corner-br{bottom:-6px;right:-6px}
.comp-window-card .wc-corner-bl{bottom:-6px;left:-6px}
.comp-window-card .wc-head{position:relative;display:flex;align-items:center;gap:.7em;
min-height:var(--comp-window-head-h,38px);padding:0 1.1em;
border-bottom:1px solid var(--comp-line,rgba(236,236,236,.22))}
.comp-window-card .wc-dot{flex:none;width:.5em;height:.5em;border-radius:50%;
background:var(--comp-accent,#ececec);box-shadow:var(--comp-window-dot-shadow,none)}
.comp-window-card .wc-title{flex:1;min-width:0;
font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.72em;letter-spacing:.3em;text-transform:uppercase;
color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.comp-window-card .wc-body{position:relative;padding:1em 1.1em;font-size:.92em;line-height:1.65}
.comp-window-card .wc-prompt,.comp-window-card .wc-line{
font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);font-size:.9em;
white-space:pre-wrap;word-break:break-all}
.comp-window-card .wc-prompt{color:var(--comp-accent,#ececec)}
.comp-window-card .wc-line{color:var(--comp-ink-dim,rgba(236,236,236,.55))}
.comp-window-card .wc-inputbar{display:flex;align-items:center;gap:.8em;
margin:0 1.1em 1em;padding:.55em .9em;
border:1px solid var(--comp-line,rgba(236,236,236,.22));
border-radius:var(--comp-radius,10px)}
.comp-window-card .wc-input-hint{flex:1;min-width:0;font-size:.85em;
color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.comp-window-card .wc-send{flex:none;
font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.68em;letter-spacing:.24em;text-transform:uppercase;
color:var(--comp-accent,#ececec)}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

const SVG_NS = "http://www.w3.org/2000/svg";

// 四角 crop-mark：L 形角标，肘部朝外，悬在卡片四角外沿
const CORNERS = [
  ["tl", "M1 13 L1 1 L13 1"],
  ["tr", "M1 1 L13 1 L13 13"],
  ["br", "M13 1 L13 13 L1 13"],
  ["bl", "M1 1 L1 13 L13 13"],
];

const VARIANTS = ["terminal", "chat", "plain"];

export const meta = { id: "window-card", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "wc", context);
  const {
    title = "",
    variant = "terminal",
    width = "640px",
    chrome = true,
    lines = [],
    inputHint = "",
    sendLabel = "Send",
  } = params;
  if (!VARIANTS.includes(variant))
    throw new Error(`[window-card] params.variant 必须是 ${VARIANTS.join(" | ")}`);
  if (!Array.isArray(lines))
    throw new Error("[window-card] params.lines 必须是字符串数组");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[window-card] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[window-card] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-window-card";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;
  el.dataset.variant = variant;
  if (width) el.style.width = width;

  // hairline 边框：无 viewBox，用户空间即卡片像素，rect 100% 跟随盒体
  const frame = document.createElementNS(SVG_NS, "svg");
  frame.setAttribute("class", "wc-frame");
  frame.setAttribute("aria-hidden", "true");
  const frameRect = document.createElementNS(SVG_NS, "rect");
  frameRect.setAttribute("x", "0");
  frameRect.setAttribute("y", "0");
  frameRect.setAttribute("width", "100%");
  frameRect.setAttribute("height", "100%");
  frameRect.setAttribute("rx", "10");
  frameRect.setAttribute("pathLength", "1");
  frameRect.style.strokeDasharray = "1";
  frameRect.style.strokeDashoffset = "1";
  frame.appendChild(frameRect);
  el.appendChild(frame);

  const cornerPaths = [];
  CORNERS.forEach(([pos, d]) => {
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", `wc-corner wc-corner-${pos}`);
    svg.setAttribute("viewBox", "0 0 14 14");
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", d);
    path.setAttribute("pathLength", "1");
    path.style.strokeDasharray = "1";
    path.style.strokeDashoffset = "1";
    svg.appendChild(path);
    el.appendChild(svg);
    cornerPaths.push(path);
  });

  let headEl = null;
  let dotEl = null;
  let titleEl = null;
  if (chrome) {
    headEl = document.createElement("header");
    headEl.className = "wc-head";
    dotEl = document.createElement("span");
    dotEl.className = "wc-dot";
    titleEl = document.createElement("span");
    titleEl.className = "wc-title";
    titleEl.textContent = title;
    headEl.append(dotEl, titleEl);
    el.appendChild(headEl);
  }

  // contentEl：场景把子组件挂载进这里
  const bodyEl = document.createElement("div");
  bodyEl.className = "wc-body";
  el.appendChild(bodyEl);

  let promptEl = null;
  const lineEls = [];
  if (variant === "terminal") {
    promptEl = document.createElement("div");
    promptEl.className = "wc-prompt";
    promptEl.textContent = ">_";
    bodyEl.appendChild(promptEl);
    lines.forEach((line) => {
      const l = document.createElement("div");
      l.className = "wc-line";
      l.textContent = line;
      bodyEl.appendChild(l);
      lineEls.push(l);
    });
  }

  let inputbarEl = null;
  let sendEl = null;
  if (variant === "chat") {
    inputbarEl = document.createElement("div");
    inputbarEl.className = "wc-inputbar";
    const hintEl = document.createElement("span");
    hintEl.className = "wc-input-hint";
    hintEl.textContent = inputHint;
    sendEl = document.createElement("span");
    sendEl.className = "wc-send";
    sendEl.textContent = sendLabel;
    inputbarEl.append(hintEl, sendEl);
    el.appendChild(inputbarEl);
  }

  host.appendChild(el);

  // enter：窗口体上浮就位 → 四角 crop-mark 描画 → hairline 闭合 → header 跟上 → 变体内容
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(
    el,
    { autoAlpha: 0, y: 10 },
    { autoAlpha: 1, y: 0, duration: 0.5, ease: "power2.out" },
    0
  );
  cornerPaths.forEach((p, i) => {
    enter.to(
      p,
      { strokeDashoffset: 0, duration: 0.3, ease: "power1.inOut" },
      0.1 + i * 0.06
    );
  });
  enter.to(
    frameRect,
    { strokeDashoffset: 0, duration: 0.44, ease: "power1.inOut" },
    0.34
  );
  if (chrome) {
    enter.fromTo(
      headEl,
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.25, ease: "power1.out" },
      0.4
    );
    enter.fromTo(
      dotEl,
      { autoAlpha: 0, scale: 0.3 },
      { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(1.7)" },
      0.44
    );
    enter.fromTo(
      titleEl,
      { autoAlpha: 0, x: -6 },
      { autoAlpha: 1, x: 0, duration: 0.35, ease: "power2.out" },
      0.5
    );
  }
  if (variant === "terminal") {
    enter.fromTo(
      promptEl,
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.25, ease: "power1.out" },
      0.55
    );
    lineEls.forEach((l, i) => {
      enter.fromTo(
        l,
        { autoAlpha: 0, y: 6 },
        { autoAlpha: 1, y: 0, duration: 0.3, ease: "power2.out" },
        0.65 + i * 0.12
      );
    });
  }
  if (variant === "chat") {
    enter.fromTo(
      inputbarEl,
      { autoAlpha: 0, y: 8 },
      { autoAlpha: 1, y: 0, duration: 0.35, ease: "power2.out" },
      0.55
    );
    enter.fromTo(
      sendEl,
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.25, ease: "power1.out" },
      0.68
    );
  }

  const dim = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0.3, duration: 0.3, ease: "power1.out" });
  const exit = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0, y: -10, duration: 0.4, ease: "power2.in" });

  const segments = { enter, dim, exit };
  return {
    segments,
    contentEl: bodyEl,
    seek(localFrame) {
      enter.time(Math.max(0, localFrame) / fps);
    },
    destroy() {
      Object.values(segments).forEach((tl) => tl.kill());
      el.remove();
    },
  };
}
