/**
 * converge-summary · 收拢汇总
 *
 * 多张要点卡片缩小、沿小弧线飞向中心，收拢成一枚写 summary 的汇总 pill。
 * enter 错拍排开 → converge 吸入聚合（pill 蓄能回弹 + accent hairline 一闪）→ 结论落定。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-converge-summary{position:relative;display:inline-flex;flex-direction:column;
align-items:center;gap:36px;
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif);
user-select:none;pointer-events:none}
.comp-converge-summary .cs-cards{display:flex;align-items:flex-start;gap:14px}
.comp-converge-summary .cs-card{padding:.55em .95em;white-space:nowrap;
background:var(--comp-surface,rgba(236,236,236,.04));
border:1px solid var(--comp-line,rgba(236,236,236,.22));
border-radius:var(--comp-radius,10px);
font-size:.92em;font-weight:600;color:var(--comp-ink,#ececec)}
.comp-converge-summary .cs-pill{position:relative;padding:.62em 1.5em;white-space:nowrap;
background:var(--comp-surface,rgba(236,236,236,.04));
border:1px solid var(--comp-accent,#ececec);border-radius:999px;
font-size:1em;font-weight:600;color:var(--comp-ink,#ececec)}
.comp-converge-summary .cs-flash{position:absolute;inset:-4px;border-radius:999px;
border:1px solid var(--comp-accent,#ececec);pointer-events:none}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "converge-summary", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "cs", context);
  const { items = [], summary = "" } = params;
  if (!Array.isArray(items) || items.length < 2 || items.length > 5) {
    throw new Error("[converge-summary] params.items 必须是 2–5 条文案数组");
  }
  if (!summary) throw new Error("[converge-summary] params.summary 不能为空");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[converge-summary] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[converge-summary] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-converge-summary";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;

  const cardsRow = document.createElement("div");
  cardsRow.className = "cs-cards";
  const cardEls = items.map((text) => {
    const card = document.createElement("div");
    card.className = "cs-card";
    card.textContent = text;
    cardsRow.appendChild(card);
    return card;
  });
  el.appendChild(cardsRow);

  const pill = document.createElement("div");
  pill.className = "cs-pill";
  const summarySpan = document.createElement("span");
  summarySpan.className = "cs-summary";
  summarySpan.textContent = summary;
  const flash = document.createElement("span");
  flash.className = "cs-flash";
  pill.append(summarySpan, flash);
  el.appendChild(pill);
  host.appendChild(el);

  // enter：容器先就位，卡片 0.24s 错拍上浮，交替微旋排开
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, ease: "power1.out" }, 0);
  cardEls.forEach((card, i) => {
    const rot = i % 2 === 0 ? -1.5 : 1.5;
    enter.fromTo(
      card,
      { autoAlpha: 0, y: 14, rotation: 0 },
      { autoAlpha: 1, y: 0, rotation: rot, duration: 0.45, ease: "power2.out" },
      i * 0.24
    );
  });

  // 布局测量（offset* 不受 GSAP transform 影响，卡片/ pill 同以 el 为 offsetParent）
  const centerOf = (node) => ({
    x: node.offsetLeft + node.offsetWidth / 2,
    y: node.offsetTop + node.offsetHeight / 2,
  });
  const pillC = centerOf(pill);

  // converge：各卡 0.1s 错峰沿小弧线汇入 pill 中心，持续缩小并途中淡出；
  // pill 蓄能回弹（0.9 → 1.02 → 1），hairline 一闪即灭，summary 淡入，全段约 1.3s
  const converge = gsap.timeline({ paused: true });
  cardEls.forEach((card, i) => {
    const c = centerOf(card);
    const dx = pillC.x - c.x;
    const dy = pillC.y - c.y;
    converge.to(
      card,
      {
        keyframes: [
          { x: dx * 0.5, y: dy * 0.5 - 18, scale: 0.8, duration: 0.45, ease: "power2.in" },
          { x: dx, y: dy, scale: 0.6, autoAlpha: 0, duration: 0.35, ease: "power1.in" },
        ],
      },
      i * 0.1
    );
  });
  converge.fromTo(
    pill,
    { autoAlpha: 0, scale: 0.9 },
    { autoAlpha: 1, scale: 1.02, duration: 0.3, ease: "power2.out" },
    0.55
  );
  converge.to(pill, { scale: 1, duration: 0.25, ease: "power2.inOut" }, 0.85);
  converge.fromTo(
    summarySpan,
    { autoAlpha: 0, y: 4 },
    { autoAlpha: 1, y: 0, duration: 0.35, ease: "power1.out" },
    0.72
  );
  gsap.set(flash, { autoAlpha: 0 });
  converge.to(flash, { autoAlpha: 1, duration: 0.08, ease: "power1.in" }, 0.84);
  converge.to(flash, { autoAlpha: 0, duration: 0.32, ease: "power1.out" }, 0.92);

  const dim = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0.3, duration: 0.3, ease: "power1.out" });
  const exit = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0, y: -10, duration: 0.4, ease: "power2.in" });

  const segments = { enter, converge, dim, exit };
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
