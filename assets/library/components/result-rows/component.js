/**
 * result-rows · 结论汇报行
 *
 * 横扫式结论行：每行一条 1px 基线先 scaleX 横扫，文字随后 y+fade 升起。
 * tag 不是胶囊：左侧 2px 竖 tab + 大写宽字距小标签；仅首行吃 --comp-accent，其余 dim。
 * 参考形态：结论 / 证据 / 风险 / 建议 逐条错拍落定。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-result-rows{position:relative;display:flex;flex-direction:column;
min-width:var(--comp-rows-w,460px);
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif)}
.comp-result-rows .rr-row{display:flex;flex-direction:column}
.comp-result-rows .rr-base{height:1px;width:100%;transform-origin:left center;
background:var(--comp-line,rgba(236,236,236,.22))}
.comp-result-rows .rr-body{display:flex;align-items:baseline;gap:.8em;
padding:.55em 0 .6em}
.comp-result-rows .rr-tab{flex:none;width:2px;height:1em;align-self:center;
background:var(--comp-line,rgba(236,236,236,.22))}
.comp-result-rows .rr-tag{flex:none;min-width:var(--comp-rows-tag-w,4.2em);
font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.72em;letter-spacing:.28em;text-transform:uppercase;white-space:nowrap;
color:var(--comp-ink-dim,rgba(236,236,236,.55))}
.comp-result-rows .rr-text{color:var(--comp-ink,#ececec);white-space:nowrap}
.comp-result-rows .rr-row[data-accent] .rr-tab{background:var(--comp-accent,#ececec)}
.comp-result-rows .rr-row[data-accent] .rr-tag{color:var(--comp-accent,#ececec)}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "result-rows", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "rr", context);
  const { rows } = params;
  if (!Array.isArray(rows) || rows.length < 2 || rows.length > 5) {
    throw new Error("[result-rows] params.rows 必填，且为 2-5 行 [{tag, text}]");
  }

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[result-rows] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[result-rows] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-result-rows";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;

  const baseEls = [];
  const bodyEls = [];

  rows.forEach((row, i) => {
    const r = document.createElement("div");
    r.className = "rr-row";
    if (i === 0) r.dataset.accent = ""; // 仅首行吃 --comp-accent，其余保持 dim

    const base = document.createElement("div");
    base.className = "rr-base";

    const body = document.createElement("div");
    body.className = "rr-body";

    const tab = document.createElement("span");
    tab.className = "rr-tab";

    const tag = document.createElement("span");
    tag.className = "rr-tag";
    tag.textContent = row.tag ?? "";

    const text = document.createElement("span");
    text.className = "rr-text";
    text.textContent = row.text ?? "";

    body.append(tab, tag, text);
    r.append(base, body);
    el.appendChild(r);
    baseEls.push(base);
    bodyEls.push(body);
  });
  host.appendChild(el);

  // enter：每行 1px 基线先 scaleX 横扫，文字（tab+tag+text）随后 y+fade 升起，行间 0.18s 错拍
  const enter = gsap.timeline({ paused: true });
  baseEls.forEach((base, i) => {
    const at = i * 0.18;
    enter.fromTo(
      base,
      { autoAlpha: 0, scaleX: 0 },
      { autoAlpha: 1, scaleX: 1, duration: 0.45, ease: "power2.inOut" },
      at
    );
    enter.fromTo(
      bodyEls[i],
      { autoAlpha: 0, y: 10 },
      { autoAlpha: 1, y: 0, duration: 0.4, ease: "power2.out" },
      at + 0.22
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
