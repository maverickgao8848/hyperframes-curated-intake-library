/**
 * side-note · 侧边注释
 *
 * 蓝图式标注：3px 圆点端子落位 → 肘形引线（SVG stroke 描画）从锚点铺到
 * 文字 → mono 小字 fade + 4px 位移淡入；无 anchor 时只淡入文字块。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-side-note{position:absolute;inset:0;overflow:visible;pointer-events:none;
font-family:var(--comp-font-mono,"JetBrains Mono","SFMono-Regular",Consolas,monospace)}
.comp-side-note[data-free]{position:static;inset:auto;display:inline-block}
.comp-side-note .sn-text{position:absolute;margin:0;white-space:nowrap;
font-size:var(--comp-note-size,12px);line-height:1.5;letter-spacing:.04em;
color:var(--comp-ink-dim,rgba(236,236,236,.55))}
.comp-side-note[data-free] .sn-text{position:static}
.comp-side-note .sn-lead{position:absolute;inset:0;overflow:visible}
.comp-side-note .sn-lead-line{fill:none;stroke:var(--comp-line,rgba(236,236,236,.22));
stroke-width:1;stroke-linecap:round;stroke-linejoin:round}
.comp-side-note .sn-lead-dot{fill:var(--comp-line,rgba(236,236,236,.22))}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

const SVG_NS = "http://www.w3.org/2000/svg";
const STUB = 14; // 引线出锚点的第一段长度（px）
const LAND = 12; // 引线进入文字前的最后一段长度（px）

export const meta = { id: "side-note", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "sn", context);
  const { text = "", anchor = null, position = "right" } = params;
  if (!text) throw new Error("[side-note] params.text 必填");
  if (!["right", "below"].includes(position))
    throw new Error("[side-note] params.position 必须是 right | below");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[side-note] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[side-note] 需要全局 window.gsap");

  const anchorEl = anchor
    ? typeof anchor === "string"
      ? document.querySelector(anchor)
      : anchor
    : null;
  if (anchor && !anchorEl) throw new Error(`[side-note] anchor 未找到: ${anchor}`);
  const side = position === "below" ? "below" : "right";

  const el = document.createElement("div");
  el.className = "comp-side-note";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;
  el.dataset.position = side;
  if (!anchorEl) el.dataset.free = "";

  const textEl = document.createElement("div");
  textEl.className = "sn-text";
  textEl.textContent = text;
  el.appendChild(textEl);
  host.appendChild(el);

  let leadLine = null;
  let leadDot = null;

  if (anchorEl) {
    // 与 host 同一坐标系量出折点，铺肘形引线
    const hostRect = host.getBoundingClientRect();
    const a = anchorEl.getBoundingClientRect();
    const ax = a.left - hostRect.left;
    const ay = a.top - hostRect.top;
    const tw = textEl.offsetWidth;
    const th = textEl.offsetHeight;

    let sx, sy, d;
    if (side === "right") {
      sx = ax + a.width; // 起点：锚点右边中点
      sy = ay + a.height / 2;
      const tx = sx + STUB + LAND;
      const ty = ay; // 文字顶对齐锚点顶
      const my = ty + th / 2;
      textEl.style.left = `${tx}px`;
      textEl.style.top = `${ty}px`;
      d = `M${sx} ${sy} L${sx + STUB} ${sy} L${sx + STUB} ${my} L${tx - 3} ${my}`;
    } else {
      sx = ax + a.width / 2; // 起点：锚点底边中点
      sy = ay + a.height;
      const tx = ax; // 文字左对齐锚点左
      const ty = sy + STUB + LAND;
      const mx = tx + tw / 2;
      textEl.style.left = `${tx}px`;
      textEl.style.top = `${ty}px`;
      d = `M${sx} ${sy} L${sx} ${sy + STUB} L${mx} ${sy + STUB} L${mx} ${ty - 3}`;
    }

    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "sn-lead");
    svg.setAttribute("width", hostRect.width);
    svg.setAttribute("height", hostRect.height);
    svg.setAttribute("viewBox", `0 0 ${hostRect.width} ${hostRect.height}`);

    leadLine = document.createElementNS(SVG_NS, "path");
    leadLine.setAttribute("class", "sn-lead-line");
    leadLine.setAttribute("d", d);
    leadLine.setAttribute("pathLength", "1");
    leadLine.style.strokeDasharray = "1";
    leadLine.style.strokeDashoffset = "1";

    leadDot = document.createElementNS(SVG_NS, "circle");
    leadDot.setAttribute("class", "sn-lead-dot");
    leadDot.setAttribute("cx", sx);
    leadDot.setAttribute("cy", sy);
    leadDot.setAttribute("r", "1.5"); // 3px 圆点端子

    svg.append(leadLine, leadDot);
    el.insertBefore(svg, textEl);
  }

  // enter：圆点端子落位 → 肘形引线描画 → 文字 fade + 4px 位移，共 0.5s
  const shift = side === "below" ? { y: -4 } : { x: -4 };
  const enter = gsap.timeline({ paused: true });
  if (leadLine) {
    enter.fromTo(
      leadDot,
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.1, ease: "power1.out" },
      0
    );
    enter.fromTo(
      leadLine,
      { strokeDashoffset: 1 },
      { strokeDashoffset: 0, duration: 0.2, ease: "power1.inOut" },
      0.04
    );
    enter.fromTo(
      textEl,
      { autoAlpha: 0, ...shift },
      { autoAlpha: 1, x: 0, y: 0, duration: 0.26, ease: "power2.out" },
      0.24
    );
  } else {
    enter.fromTo(
      textEl,
      { autoAlpha: 0, y: 4 },
      { autoAlpha: 1, y: 0, duration: 0.4, ease: "power2.out" },
      0
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
    seek(localFrame) {
      enter.time(Math.max(0, localFrame) / fps);
    },
    destroy() {
      Object.values(segments).forEach((tl) => tl.kill());
      el.remove();
    },
  };
}
