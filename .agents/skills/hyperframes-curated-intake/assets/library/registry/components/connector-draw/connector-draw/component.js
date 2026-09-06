/**
 * connector-draw · 描画连线
 *
 * 两个锚点之间的 1px 细线描画：路径从 from 向 to 描出后，一颗小圆点
 * 沿路径从 from 流向 to（有限次）暗示流向，末端 chevron 滑入收束方向。
 * 表达因果、指向、归属："这个参数决定了那个行为"。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-connector-draw{position:absolute;inset:0;pointer-events:none;overflow:visible}
.comp-connector-draw svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.comp-connector-draw .cd-line{fill:none;stroke:var(--comp-line,rgba(236,236,236,.22));stroke-width:1}
.comp-connector-draw .cd-dot{fill:var(--comp-ink-dim,rgba(236,236,236,.55))}
.comp-connector-draw .cd-arrow path{fill:none;stroke:var(--comp-line,rgba(236,236,236,.22));
stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

const SVG_NS = "http://www.w3.org/2000/svg";

export const meta = { id: "connector-draw", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "cd", context);
  const { from, to, dash = false, arrow = true } = params;
  if (!from) throw new Error("[connector-draw] params.from 必填");
  if (!to) throw new Error("[connector-draw] params.to 必填");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[connector-draw] mount root 不存在");

  const fromEl = typeof from === "string" ? document.querySelector(from) : from;
  const toEl = typeof to === "string" ? document.querySelector(to) : to;
  if (!fromEl) throw new Error("[connector-draw] from 锚点不存在");
  if (!toEl) throw new Error("[connector-draw] to 锚点不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[connector-draw] 需要全局 window.gsap");

  // mount 时元素已在 DOM，直接测量两锚点中心并换算到 host 局部坐标
  const hostBox = host.getBoundingClientRect();
  const a = fromEl.getBoundingClientRect();
  const b = toEl.getBoundingClientRect();
  const x1 = a.left + a.width / 2 - hostBox.left;
  const y1 = a.top + a.height / 2 - hostBox.top;
  const x2 = b.left + b.width / 2 - hostBox.left;
  const y2 = b.top + b.height / 2 - hostBox.top;
  const len = Math.hypot(x2 - x1, y2 - y1);
  const angle = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;

  // 根元素铺满 host（连线要跨任意两个锚点，坐标在 host 空间内解析）
  const el = document.createElement("div");
  el.className = "comp-connector-draw";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;
  el.dataset.dash = String(dash);

  const svg = document.createElementNS(SVG_NS, "svg");
  el.appendChild(svg);

  // 主路径：默认直线，pathLength=1 归一化后用 dashoffset 描画
  const line = document.createElementNS(SVG_NS, "path");
  line.setAttribute("class", "cd-line");
  line.setAttribute("d", `M ${x1} ${y1} L ${x2} ${y2}`);
  line.setAttribute("pathLength", "1");
  line.style.strokeDasharray = "1";
  line.style.strokeDashoffset = "1";
  svg.appendChild(line);

  // 流向圆点：描画完成后沿路径从 from 流向 to
  const dot = document.createElementNS(SVG_NS, "circle");
  dot.setAttribute("class", "cd-dot");
  dot.setAttribute("r", "2.6");
  dot.setAttribute("cx", String(x1));
  dot.setAttribute("cy", String(y1));
  dot.style.opacity = "0";
  svg.appendChild(dot);

  // 末端 chevron：外层 g 负责定位+朝向，内层 g 负责滑入（避免争夺 transform）
  let arrowSlide = null;
  if (arrow) {
    const arrowG = document.createElementNS(SVG_NS, "g");
    arrowG.setAttribute("class", "cd-arrow");
    arrowG.setAttribute("transform", `translate(${x2} ${y2}) rotate(${angle})`);
    arrowSlide = document.createElementNS(SVG_NS, "g");
    arrowSlide.style.opacity = "0";
    const chevron = document.createElementNS(SVG_NS, "path");
    chevron.setAttribute("d", "M -7 -4.5 L 0 0 L -7 4.5");
    arrowSlide.appendChild(chevron);
    arrowG.appendChild(arrowSlide);
    svg.appendChild(arrowG);
  }
  host.appendChild(el);

  // enter：容器就位 → 路径描画（0.6–0.8s 按线长折算）→ chevron 滑入 → 圆点流向终点
  const drawDur = Math.min(0.8, Math.max(0.6, len / 700));
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "power1.out" }, 0);
  enter.to(line, { strokeDashoffset: 0, duration: drawDur, ease: "power1.inOut" }, 0);
  // dash：描画完成后切换为虚线外观（推测/间接关系）
  if (dash) enter.set(line, { strokeDasharray: "0.045 0.03" }, drawDur);
  if (arrow) {
    enter.fromTo(
      arrowSlide,
      { autoAlpha: 0, x: -4 },
      { autoAlpha: 1, x: 0, duration: 0.2, ease: "power2.out" },
      drawDur
    );
  }
  // 圆点流动：有限次，repeat 用 floor 公式约束在展示窗口内
  const dotStart = drawDur + 0.1;
  const dotCycle = 0.65;
  const dotWindow = 0.75;
  const dotRepeat = Math.max(0, Math.floor(dotWindow / dotCycle) - 1);
  enter.fromTo(dot, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.15, ease: "power1.out" }, dotStart);
  enter.fromTo(
    dot,
    { attr: { cx: x1, cy: y1 } },
    { attr: { cx: x2, cy: y2 }, duration: dotCycle, ease: "power1.inOut", repeat: dotRepeat },
    dotStart + 0.1
  );

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
