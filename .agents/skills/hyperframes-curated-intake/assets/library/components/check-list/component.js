/**
 * check-list · 检查清单
 *
 * 行项逐个出现并打勾，右侧等宽字体放证据细节。
 * 参考形态：SUB-AGENT 片子会话的 Read/Query/Fetch 逐项 ✓。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-check-list{position:relative;display:flex;flex-direction:column;gap:.7em;
min-width:var(--comp-list-w,420px);padding:1.1em 1.3em;
background:var(--comp-surface,rgba(236,236,236,.04));
border:1px solid var(--comp-line,rgba(236,236,236,.22));
border-radius:var(--comp-radius,10px);
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif)}
.comp-check-list .cl-title{font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.72em;letter-spacing:.28em;text-transform:uppercase;
color:var(--comp-ink-dim,rgba(236,236,236,.55));margin-bottom:.3em}
.comp-check-list .cl-row{display:flex;align-items:baseline;gap:.7em}
.comp-check-list .cl-check{flex:none;width:.95em;height:.95em;align-self:center}
.comp-check-list .cl-check path{fill:none;stroke:var(--comp-accent,#ececec);
stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.comp-check-list .cl-label{font-weight:600;color:var(--comp-ink,#ececec);white-space:nowrap}
.comp-check-list .cl-detail{flex:1;text-align:right;
font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);font-size:.78em;
color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

const SVG_NS = "http://www.w3.org/2000/svg";

export const meta = { id: "check-list", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "cl", context);
  const { rows = [], title = null } = params;
  if (!Array.isArray(rows) || rows.length < 2 || rows.length > 7)
    throw new Error("[check-list] params.rows 必须是 2–7 行数组");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[check-list] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[check-list] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-check-list";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;

  if (title) {
    const t = document.createElement("div");
    t.className = "cl-title";
    t.textContent = title;
    el.appendChild(t);
  }

  const rowEls = [];
  const checkPaths = [];
  const detailEls = [];

  rows.forEach((row) => {
    const r = document.createElement("div");
    r.className = "cl-row";

    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "cl-check");
    svg.setAttribute("viewBox", "0 0 12 12");
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", "M2.2 6.4 L5 9 L9.8 3.2");
    path.setAttribute("pathLength", "1");
    path.style.strokeDasharray = "1";
    path.style.strokeDashoffset = "1";
    svg.appendChild(path);

    const label = document.createElement("span");
    label.className = "cl-label";
    label.textContent = row.label ?? "";

    const detail = document.createElement("span");
    detail.className = "cl-detail";
    detail.textContent = row.detail ?? "";

    r.append(svg, label, detail);
    el.appendChild(r);
    rowEls.push(r);
    checkPaths.push(path);
    detailEls.push(detail);
  });
  host.appendChild(el);

  // enter：容器先就位，行出现 → 打勾描画 → 细节淡入，逐行错拍
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, ease: "power1.out" }, 0);
  rowEls.forEach((r, i) => {
    const at = i * 0.32;
    enter.fromTo(
      r,
      { autoAlpha: 0, x: -10 },
      { autoAlpha: 1, x: 0, duration: 0.35, ease: "power2.out" },
      at
    );
    enter.to(
      checkPaths[i],
      { strokeDashoffset: 0, duration: 0.25, ease: "power1.inOut" },
      at + 0.2
    );
    enter.fromTo(
      detailEls[i],
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.25, ease: "power1.out" },
      at + 0.32
    );
  });

  const dim = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0.3, duration: 0.3, ease: "power1.out" });
  const exit = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0, y: -10, duration: 0.4, ease: "power2.in" });

  const segments = { enter, dim, exit };
  return {
    segments,
    seek(localFrame) {
      enter.time(Math.max(0, localFrame) / fps);
    },
    destroy() {
      Object.values(segments).forEach((tl) => tl.kill());
      el.remove();
    },
  };
}
