/**
 * sticker-label · 贴纸标签
 *
 * 和纸胶带条：半透明纸面带两端撕边（jagged clip-path），微旋转、按压式入场，
 * 替观众说一句口语化强调（如「替你猜」）。每幕最多一个。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-sticker-label{position:relative;display:inline-block;
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif);
font-size:var(--comp-sticker-size,15px);font-weight:600;line-height:1;
user-select:none;pointer-events:none;
filter:var(--comp-sticker-shadow,drop-shadow(0 2px 5px rgba(0,0,0,.16)))}
.comp-sticker-label .sl-tape{display:block;padding:.55em 1.15em;white-space:nowrap;
clip-path:polygon(2.5% 0,97.5% 0,100% 8%,98% 18%,100% 30%,97.5% 42%,100% 54%,98% 66%,100% 78%,97.5% 89%,99.5% 100%,2.5% 100%,0 92%,2% 81%,0 69%,2.5% 57%,0 45%,2% 33%,0 21%,2.5% 10%)}
.comp-sticker-label[data-tone="paper"] .sl-tape{
background:var(--comp-sticker-paper,rgba(243,240,232,.92));
color:var(--comp-sticker-paper-ink,#2b2822)}
.comp-sticker-label[data-tone="dark"] .sl-tape{
background:var(--comp-sticker-dark,rgba(22,22,26,.72));
border:1px solid var(--comp-line,rgba(236,236,236,.22));
color:var(--comp-ink,#ececec)}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "sticker-label", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "sl", context);
  const { text, rotation = -3, tone = "paper" } = params;
  if (!text) throw new Error("[sticker-label] params.text 必填");
  if (!["paper", "dark"].includes(tone))
    throw new Error("[sticker-label] params.tone 必须是 paper | dark");
  if (!Number.isFinite(rotation) || Math.abs(rotation) > 6)
    throw new Error("[sticker-label] params.rotation 必须在 -6 到 6 之间");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[sticker-label] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[sticker-label] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-sticker-label";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;
  el.dataset.tone = tone === "dark" ? "dark" : "paper";

  const tape = document.createElement("span");
  tape.className = "sl-tape";
  tape.textContent = text;
  el.appendChild(tape);
  host.appendChild(el);

  // 旋转限制在 ±6°（再大读不清）；enter 从 ±2° 余量回正
  const rot = Math.max(-6, Math.min(6, Number(rotation) || 0));
  const rotFrom = rot + (rot < 0 ? -2 : 2);

  // enter：按压式入场——1.15 倍按下，back.out 过冲到 ~0.98 再回 1，rotation 回正
  const enter = gsap
    .timeline({ paused: true })
    .fromTo(
      el,
      { autoAlpha: 0, scale: 1.15, rotation: rotFrom },
      { autoAlpha: 1, scale: 1, rotation: rot, duration: 0.5, ease: "back.out(1.9)" },
      0
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
