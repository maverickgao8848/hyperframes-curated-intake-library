/**
 * meter-bar · 占比条
 *
 * 卡尺式占比：hairline 轨道带 4 个刻度 tick，填充从 0 生长到 value/max，
 * 端头带更亮的 2px cap 竖线，mono 百分比与填充同步 count-up；
 * compare 数组渲染为 dim 色 ghost 细条，在主条下方错拍 0.15s 跟进。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-meter-bar{position:relative;display:flex;flex-direction:column;gap:.55em;
min-width:var(--comp-meter-w,320px);
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif)}
.comp-meter-bar .mb-head{display:flex;align-items:baseline;justify-content:space-between;gap:1em}
.comp-meter-bar .mb-label{font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.72em;letter-spacing:.28em;text-transform:uppercase;
color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap}
.comp-meter-bar .mb-percent{font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.95em;color:var(--comp-ink,#ececec);white-space:nowrap}
.comp-meter-bar .mb-track{position:relative;height:12px}
.comp-meter-bar .mb-track-line{position:absolute;left:0;right:0;top:50%;height:1px;
background:var(--comp-line,rgba(236,236,236,.22))}
.comp-meter-bar .mb-tick{position:absolute;top:50%;width:1px;height:5px;margin-top:-2.5px;
background:var(--comp-line,rgba(236,236,236,.22))}
.comp-meter-bar .mb-fill{position:absolute;left:0;top:50%;width:100%;height:2px;margin-top:-1px;
background:var(--comp-accent,#ececec);opacity:.8;transform-origin:0 50%}
.comp-meter-bar .mb-cap{position:absolute;top:50%;width:2px;height:9px;margin:-4.5px 0 0 -1px;
left:0;background:var(--comp-accent,#ececec);box-shadow:var(--comp-meter-cap-shadow,none);
transform-origin:left center}
.comp-meter-bar .mb-compare{display:flex;flex-direction:column;gap:.45em;margin-top:.15em}
.comp-meter-bar .mb-cmp-row{display:flex;flex-direction:column;gap:.3em}
.comp-meter-bar .mb-cmp-head{display:flex;align-items:baseline;justify-content:space-between;gap:1em}
.comp-meter-bar .mb-cmp-label{font-size:.68em;letter-spacing:.14em;text-transform:uppercase;
color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap}
.comp-meter-bar .mb-cmp-percent{font-family:var(--comp-font-mono,"JetBrains Mono",Consolas,monospace);
font-size:.68em;color:var(--comp-ink-dim,rgba(236,236,236,.55));white-space:nowrap}
.comp-meter-bar .mb-cmp-track{position:relative;height:4px}
.comp-meter-bar .mb-cmp-line{position:absolute;left:0;right:0;top:50%;height:1px;
background:var(--comp-line,rgba(236,236,236,.22));opacity:.6}
.comp-meter-bar .mb-cmp-fill{position:absolute;left:0;top:50%;width:100%;height:1px;
background:var(--comp-ink-dim,rgba(236,236,236,.55));transform-origin:0 50%}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

// 卡尺刻度：0 / 1/3 / 2/3 / 满量程，共 4 个 tick
const TICK_POSITIONS = [0, 33.3333, 66.6667, 100];

function clamp01(n) {
  return Math.min(1, Math.max(0, n));
}

export const meta = { id: "meter-bar", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "mb", context);
  const { label, value, max = 100, compare = [] } = params;
  if (label === undefined || label === null || label === "") {
    throw new Error("[meter-bar] params.label 为必填参数");
  }
  if (typeof value !== "number" || Number.isNaN(value)) {
    throw new Error("[meter-bar] params.value 必须为数字");
  }
  if (typeof max !== "number" || Number.isNaN(max) || max <= 0) {
    throw new Error("[meter-bar] params.max 必须为正数");
  }
  if (!Array.isArray(compare) || compare.length > 2) {
    throw new Error("[meter-bar] params.compare 必须是至多 2 条的数组");
  }

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[meter-bar] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[meter-bar] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-meter-bar";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;

  // 头部：label（大写宽字距小字）+ mono 百分比
  const head = document.createElement("div");
  head.className = "mb-head";
  const labelEl = document.createElement("span");
  labelEl.className = "mb-label";
  labelEl.textContent = label;
  const percentEl = document.createElement("span");
  percentEl.className = "mb-percent";
  percentEl.textContent = "0%";
  head.append(labelEl, percentEl);
  el.appendChild(head);

  // 卡尺轨道：hairline + 4 tick + 填充 + 端头 cap
  const track = document.createElement("div");
  track.className = "mb-track";
  const trackLine = document.createElement("div");
  trackLine.className = "mb-track-line";
  track.appendChild(trackLine);
  const ticks = TICK_POSITIONS.map((pos) => {
    const tick = document.createElement("div");
    tick.className = "mb-tick";
    tick.style.left = `${pos}%`;
    track.appendChild(tick);
    return tick;
  });
  const fill = document.createElement("div");
  fill.className = "mb-fill";
  const cap = document.createElement("div");
  cap.className = "mb-cap";
  track.append(fill, cap);
  el.appendChild(track);

  // compare ghost 细条
  const cmpRows = [];
  if (compare.length) {
    const cmpWrap = document.createElement("div");
    cmpWrap.className = "mb-compare";
    compare.forEach((item) => {
      const row = document.createElement("div");
      row.className = "mb-cmp-row";

      const cmpHead = document.createElement("div");
      cmpHead.className = "mb-cmp-head";
      const cmpLabel = document.createElement("span");
      cmpLabel.className = "mb-cmp-label";
      cmpLabel.textContent = item.label ?? "";
      const cmpPercent = document.createElement("span");
      cmpPercent.className = "mb-cmp-percent";
      cmpPercent.textContent = "0%";
      cmpHead.append(cmpLabel, cmpPercent);

      const cmpTrack = document.createElement("div");
      cmpTrack.className = "mb-cmp-track";
      const cmpLine = document.createElement("div");
      cmpLine.className = "mb-cmp-line";
      const cmpFill = document.createElement("div");
      cmpFill.className = "mb-cmp-fill";
      cmpTrack.append(cmpLine, cmpFill);

      row.append(cmpHead, cmpTrack);
      cmpWrap.appendChild(row);
      cmpRows.push({ row, fill: cmpFill, percent: cmpPercent });
    });
    el.appendChild(cmpWrap);
  }
  host.appendChild(el);

  const pct = clamp01(value / max);
  const pctText = `${pct * 100}%`;
  const capX = track.clientWidth * pct;

  // enter：容器先就位 → label/刻度淡入 → 填充+cap 生长，百分比同步 count-up →
  // compare 细条错拍 0.15s 逐个跟进
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, ease: "power1.out" }, 0);
  enter.fromTo(
    labelEl,
    { autoAlpha: 0, y: 4 },
    { autoAlpha: 1, y: 0, duration: 0.3, ease: "power2.out" },
    0
  );
  enter.fromTo(
    percentEl,
    { autoAlpha: 0 },
    { autoAlpha: 1, duration: 0.25, ease: "power1.out" },
    0.1
  );
  enter.fromTo(
    trackLine,
    { autoAlpha: 0 },
    { autoAlpha: 1, duration: 0.25, ease: "power1.out" },
    0.1
  );
  enter.fromTo(
    ticks,
    { autoAlpha: 0, scaleY: 0 },
    { autoAlpha: 1, scaleY: 1, duration: 0.25, ease: "power2.out", stagger: 0.05 },
    0.1
  );
  const growAt = 0.2;
  enter.fromTo(
    fill,
    { scaleX: 0 },
    { scaleX: pct, duration: 0.6, ease: "power2.out" },
    growAt
  );
  enter.fromTo(
    cap,
    { autoAlpha: 0, x: 0 },
    {
      autoAlpha: 1,
      x: capX,
      duration: 0.6,
      ease: "power2.out",
    },
    growAt
  );
  const counter = { v: 0 };
  enter.to(
    counter,
    {
      v: pct * 100,
      duration: 0.6,
      ease: "power2.out",
      onUpdate() {
        percentEl.textContent = `${Math.round(counter.v)}%`;
      },
    },
    growAt
  );

  cmpRows.forEach((cmp, i) => {
    const item = compare[i];
    const itemMax = typeof item.max === "number" && item.max > 0 ? item.max : max;
    const cmpPct = clamp01((typeof item.value === "number" ? item.value : 0) / itemMax);
    const at = growAt + 0.15 * (i + 1);
    enter.fromTo(
      cmp.row,
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.25, ease: "power1.out" },
      at
    );
    enter.fromTo(
      cmp.fill,
      { scaleX: 0 },
      { scaleX: cmpPct, duration: 0.5, ease: "power2.out" },
      at + 0.05
    );
    const cmpCounter = { v: 0 };
    enter.to(
      cmpCounter,
      {
        v: cmpPct * 100,
        duration: 0.5,
        ease: "power2.out",
        onUpdate() {
          cmp.percent.textContent = `${Math.round(cmpCounter.v)}%`;
        },
      },
      at + 0.05
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
