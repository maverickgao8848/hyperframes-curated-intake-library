/**
 * step-chain · 步骤链
 *
 * 编号卡 + 连接箭头逐步生长，可选回环线（如“读取结果 → 继续调整”）。
 * 参考形态：AGENT 片的 STEP 01→04 横向链条与底部回环。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-step-chain{position:relative;display:flex;align-items:stretch;
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif)}
.comp-step-chain[data-direction="column"]{flex-direction:column}
.comp-step-chain .sc-card{display:flex;flex-direction:column;justify-content:center;gap:.45em;
min-width:var(--comp-chain-card-w,200px);padding:1em 1.4em;
background:var(--comp-surface,rgba(236,236,236,.04));
border:1px solid var(--comp-line,rgba(236,236,236,.22));
border-radius:var(--comp-radius,10px)}
.comp-step-chain .sc-index{font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.72em;letter-spacing:.28em;color:var(--comp-ink-dim,rgba(236,236,236,.55))}
.comp-step-chain .sc-title{font-size:1.05em;font-weight:600;color:var(--comp-ink,#ececec);white-space:nowrap}
.comp-step-chain .sc-sub{font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.72em;color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap}
.comp-step-chain .sc-conn{align-self:center;width:var(--comp-chain-gap,44px);height:1px;
background:var(--comp-line,rgba(236,236,236,.22));transform-origin:left center;position:relative}
.comp-step-chain[data-direction="column"] .sc-conn{width:1px;height:var(--comp-chain-gap,44px);
transform-origin:center top;margin-left:2em}
.comp-step-chain .sc-conn::after{content:"";position:absolute;right:-1px;top:-3px;
border-left:6px solid var(--comp-line,rgba(236,236,236,.22));
border-top:3.5px solid transparent;border-bottom:3.5px solid transparent}
.comp-step-chain[data-direction="column"] .sc-conn::after{right:-3px;top:auto;bottom:-1px;
border-left:3.5px solid transparent;border-right:3.5px solid transparent;
border-top:6px solid var(--comp-line,rgba(236,236,236,.22));border-bottom:none}
.comp-step-chain .sc-loop{position:absolute;inset:0;overflow:visible;pointer-events:none}
.comp-step-chain .sc-loop path{fill:none;stroke:var(--comp-line,rgba(236,236,236,.22));stroke-width:1}
.comp-step-chain .sc-loop-label{position:absolute;padding:.35em .9em;
font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);font-size:.72em;
letter-spacing:.12em;color:var(--comp-ink-dim,rgba(236,236,236,.55));
background:var(--comp-surface,rgba(236,236,236,.04));
border:1px solid var(--comp-line,rgba(236,236,236,.22));
border-radius:var(--comp-radius,10px);white-space:nowrap;transform:translate(-50%,-50%)}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

const SVG_NS = "http://www.w3.org/2000/svg";

export const meta = { id: "step-chain", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "sc", context);
  const { steps = [], loop = null, direction = "row" } = params;
  if (!Array.isArray(steps) || steps.length < 2 || steps.length > 6)
    throw new Error("[step-chain] params.steps 必须是 2–6 步数组");
  if (!["row", "column"].includes(direction))
    throw new Error("[step-chain] params.direction 必须是 row | column");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[step-chain] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[step-chain] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-step-chain";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;
  el.dataset.direction = direction;

  const cards = [];
  const conns = [];
  steps.forEach((step, i) => {
    if (i > 0) {
      const conn = document.createElement("div");
      conn.className = "sc-conn";
      el.appendChild(conn);
      conns.push(conn);
    }
    const card = document.createElement("div");
    card.className = "sc-card";
    const index = document.createElement("div");
    index.className = "sc-index";
    index.textContent = step.index ?? `STEP ${String(i + 1).padStart(2, "0")}`;
    const title = document.createElement("div");
    title.className = "sc-title";
    title.textContent = step.title ?? "";
    card.append(index, title);
    if (step.sub) {
      const sub = document.createElement("div");
      sub.className = "sc-sub";
      sub.textContent = step.sub;
      card.appendChild(sub);
    }
    el.appendChild(card);
    cards.push(card);
  });
  host.appendChild(el);

  // enter：卡片错拍上浮，连线在前一张卡就位后描出
  const enter = gsap.timeline({ paused: true });
  cards.forEach((card, i) => {
    enter.fromTo(
      card,
      { autoAlpha: 0, y: 14 },
      { autoAlpha: 1, y: 0, duration: 0.45, ease: "power2.out" },
      i * 0.22
    );
    if (i > 0) {
      enter.fromTo(
        conns[i - 1],
        { scaleX: direction === "row" ? 0 : 1, scaleY: direction === "row" ? 1 : 0 },
        { scaleX: 1, scaleY: 1, duration: 0.3, ease: "power1.inOut" },
        i * 0.22 - 0.08
      );
    }
  });

  // loop：末卡 → 首卡的回环路径 + 标签（如“读取结果 → 继续调整”）
  let loopLabel = null;
  const loopTl = gsap.timeline({ paused: true });
  if (loop && cards.length > 1) {
    const box = el.getBoundingClientRect();
    const first = cards[0].getBoundingClientRect();
    const last = cards[cards.length - 1].getBoundingClientRect();
    const drop = 34;
    const x1 = last.left + last.width / 2 - box.left;
    const y1 = last.bottom - box.top;
    const x2 = first.left + first.width / 2 - box.left;
    const y2 = first.bottom - box.top;

    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "sc-loop");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute(
      "d",
      `M ${x1} ${y1} V ${y1 + drop} H ${x2} V ${y2}`
    );
    path.setAttribute("pathLength", "1");
    path.style.strokeDasharray = "1";
    path.style.strokeDashoffset = "1";
    svg.appendChild(path);
    el.appendChild(svg);

    loopTl.to(path, { strokeDashoffset: 0, duration: 0.7, ease: "power1.inOut" }, 0);

    if (loop.label) {
      loopLabel = document.createElement("div");
      loopLabel.className = "sc-loop-label";
      loopLabel.textContent = loop.label;
      loopLabel.style.left = `${(x1 + x2) / 2}px`;
      loopLabel.style.top = `${y1 + drop}px`;
      el.appendChild(loopLabel);
      loopTl.fromTo(
        loopLabel,
        { autoAlpha: 0, scale: 0.85 },
        { autoAlpha: 1, scale: 1, duration: 0.35, ease: "power2.out" },
        0.45
      );
    }
  }

  const dim = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0.3, duration: 0.3, ease: "power1.out" });
  const exit = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0, y: -10, duration: 0.4, ease: "power2.in" });

  const segments = { enter, loop: loopTl, dim, exit };
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
