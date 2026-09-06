/**
 * numbered-tag · 编号标签
 *
 * 编辑排版式编号（非胶囊 chip）：发丝引线先 scaleX 描出，编号从线后的
 * overflow 遮罩里上移入位，uppercase 宽字距标签随后跟上。
 * 参考形态：`— 01 GOAL`（元信息层，给内容一个可引用的序号）。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-numbered-tag{display:inline-flex;align-items:center;gap:.55em;
font-family:var(--comp-font-mono,"JetBrains Mono","SFMono-Regular",Consolas,monospace);
font-size:var(--comp-tag-size,13px);line-height:1;white-space:nowrap;
user-select:none;pointer-events:none}
.comp-numbered-tag[data-size="s"]{font-size:var(--comp-tag-size-s,11px)}
.comp-numbered-tag .nt-rule{flex:none;width:var(--comp-tag-rule-w,24px);height:1px;
transform-origin:left center;
background:var(--comp-line,rgba(236,236,236,.22))}
.comp-numbered-tag .nt-num-mask{display:inline-flex;overflow:hidden}
.comp-numbered-tag .nt-num{display:inline-block;font-weight:600;letter-spacing:.04em;
color:var(--comp-ink,#ececec)}
.comp-numbered-tag[data-tone="accent"] .nt-num{color:var(--comp-accent,#ececec)}
.comp-numbered-tag .nt-label{letter-spacing:.26em;text-transform:uppercase;
color:var(--comp-ink-dim,rgba(236,236,236,.55))}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "numbered-tag", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "nt", context);
  const { index = "01", label = "", tone = "mono", size = "s" } = params;
  if (!["mono", "accent"].includes(tone))
    throw new Error("[numbered-tag] params.tone 必须是 mono | accent");
  if (!["s", "m"].includes(size))
    throw new Error("[numbered-tag] params.size 必须是 s | m");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[numbered-tag] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[numbered-tag] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-numbered-tag";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;
  el.dataset.tone = tone === "accent" ? "accent" : "mono";
  el.dataset.size = size === "s" ? "s" : "m";

  // 发丝引线：enter 0 点起从左 scaleX 描出
  const rule = document.createElement("span");
  rule.className = "nt-rule";
  el.appendChild(rule);

  // 编号藏在 overflow 遮罩内，引线描出后上移入位
  const mask = document.createElement("span");
  mask.className = "nt-num-mask";
  const num = document.createElement("span");
  num.className = "nt-num";
  num.textContent = index;
  mask.appendChild(num);
  el.appendChild(mask);

  let labelEl = null;
  if (label) {
    labelEl = document.createElement("span");
    labelEl.className = "nt-label";
    labelEl.textContent = label;
    el.appendChild(labelEl);
  }
  host.appendChild(el);

  // enter：容器先就位，引线描出 → 编号遮罩揭示 → 宽字距标签跟上，逐级错拍
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(
    el,
    { autoAlpha: 0 },
    { autoAlpha: 1, duration: 0.2, ease: "power1.out" },
    0
  );
  enter.fromTo(
    rule,
    { scaleX: 0 },
    { scaleX: 1, duration: 0.35, ease: "power2.inOut" },
    0
  );
  enter.fromTo(
    num,
    { yPercent: 110 },
    { yPercent: 0, duration: 0.45, ease: "power3.out" },
    0.16
  );
  if (labelEl) {
    enter.fromTo(
      labelEl,
      { autoAlpha: 0, x: -6 },
      { autoAlpha: 1, x: 0, duration: 0.3, ease: "power2.out" },
      0.34
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
