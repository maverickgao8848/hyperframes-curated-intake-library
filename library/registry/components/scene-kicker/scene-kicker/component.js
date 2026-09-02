/**
 * scene-kicker · 章节角标
 *
 * 每幕身份锚点：等宽字体 eyebrow · 编号 · 标题，固定在画面角落。
 * 参考形态：`EP108 · 01 PROMPT`（左上角、letterspaced、全程在场）。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-scene-kicker{position:absolute;display:flex;align-items:baseline;gap:.85em;
z-index:var(--comp-kicker-z,20);
font-family:var(--comp-font-mono,"JetBrains Mono","SFMono-Regular",Consolas,monospace);
font-size:var(--comp-kicker-size,15px);letter-spacing:.32em;text-transform:uppercase;
color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap;user-select:none;pointer-events:none}
.comp-scene-kicker[data-align="top-left"]{top:var(--comp-kicker-top,28px);left:var(--comp-kicker-left,32px)}
.comp-scene-kicker[data-align="top-right"]{top:var(--comp-kicker-top,28px);right:var(--comp-kicker-left,32px)}
.comp-scene-kicker .ck-index{color:var(--comp-ink,#ececec)}
.comp-scene-kicker .ck-dot{opacity:.4}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "scene-kicker", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "ck", context);
  const {
    eyebrow = "EP",
    index = "01",
    title = "",
    align = "top-left",
  } = params;
  if (!["top-left", "top-right"].includes(align)) {
    throw new Error("[scene-kicker] params.align 必须是 top-left | top-right");
  }

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[scene-kicker] mount root 不存在");

  const el = document.createElement("div");
  el.className = "comp-scene-kicker";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;
  el.dataset.align = align;

  const eyebrowSpan = document.createElement("span");
  eyebrowSpan.className = "ck-eyebrow";
  eyebrowSpan.textContent = eyebrow;
  el.appendChild(eyebrowSpan);

  if (index) {
    const dot = document.createElement("span");
    dot.className = "ck-dot";
    dot.textContent = "·";
    const indexSpan = document.createElement("span");
    indexSpan.className = "ck-index";
    indexSpan.textContent = index;
    el.append(dot, indexSpan);
  }
  if (title) {
    const titleSpan = document.createElement("span");
    titleSpan.className = "ck-title";
    titleSpan.textContent = title;
    el.appendChild(titleSpan);
  }
  host.appendChild(el);

  const gsap = window.gsap;
  if (!gsap) throw new Error("[scene-kicker] 需要全局 window.gsap");

  const enter = gsap
    .timeline({ paused: true })
    .fromTo(
      el,
      { autoAlpha: 0, y: 8 },
      { autoAlpha: 1, y: 0, duration: 0.6, ease: "power2.out" }
    );
  const dim = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0.35, duration: 0.3, ease: "power1.out" });
  const exit = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0, y: -6, duration: 0.4, ease: "power2.in" });

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
