/**
 * typewriter-block · 打字机文本
 *
 * 大排版 hero 关键句逐字上屏：预切 <span> 按 speed 错拍弹出，
 * 2px 竖条光标随字推进（x/y 跟随，跨行自动换行跟随），
 * keywords 词打完后用 scaleX 发丝虚线自左向右描出下划。
 * 光标闪烁为有限动画（repeat 走 floor 公式），闪 3 次停在实色。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-typewriter-block{position:relative;max-width:var(--comp-tw-maxw,26em);
font-family:var(--comp-font-sans,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif);
font-size:var(--comp-tw-size,44px);font-weight:600;line-height:1.3;letter-spacing:.01em;
color:var(--comp-ink,#ececec);white-space:pre-wrap;user-select:none}
.comp-typewriter-block .tw-cursor{position:absolute;left:0;top:0;width:2px;height:.92em;
background:var(--comp-ink,#ececec);pointer-events:none}
.comp-typewriter-block .tw-rule{position:absolute;left:0;top:0;height:0;margin-top:-.12em;
border-bottom:1px dashed var(--comp-accent,#ececec);
transform-origin:0 50%;pointer-events:none}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "typewriter-block", version: 1 };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "tw", context);
  const { text: rawText, keywords = [], speed = 12, cursor = true } = params;
  if (typeof rawText !== "string" || !rawText) {
    throw new Error("[typewriter-block] params.text 必填");
  }
  if (!Number.isFinite(speed) || speed <= 0) {
    throw new Error("[typewriter-block] params.speed 必须为正数（字/秒）");
  }
  if (!Array.isArray(keywords)) {
    throw new Error("[typewriter-block] params.keywords 必须是字符串数组");
  }
  // Windows 粘贴可能带 \r\n，统一成 \n（pre-wrap 直接换行）
  const text = rawText.replace(/\r\n?/g, "\n");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[typewriter-block] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[typewriter-block] 需要全局 window.gsap");

  const el = document.createElement("div");
  el.className = "comp-typewriter-block";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;

  // 逐字预切 span（inline 保留自然换行；只做透明度弹出，不做位移变换）
  const chars = [...text];
  const charEls = chars.map((ch) => {
    const s = document.createElement("span");
    s.className = "tw-ch";
    s.textContent = ch;
    el.appendChild(s);
    return s;
  });

  let cursorEl = null;
  if (cursor) {
    cursorEl = document.createElement("span");
    cursorEl.className = "tw-cursor";
    cursorEl.setAttribute("data-layout-allow-occlusion", "");
    el.appendChild(cursorEl);
  }

  host.appendChild(el);

  // 布局测量：mount 同步执行、元素已在 DOM，直接读取 offset*
  const dt = 1 / speed; // 每字间隔
  const charDur = Math.min(0.1, dt * 0.9); // 单字弹出
  const cursorDur = Math.min(0.09, dt * 0.6); // 光标跟随
  const t0 = 0.15; // 容器淡入后开打字
  const cursorH = cursorEl ? cursorEl.offsetHeight : 0;

  // keywords：仅匹配 text 原样子串，不匹配跳过；跨行的词只划首行部分
  const rules = [];
  keywords.slice(0, 3).forEach((kw) => {
    if (!kw) return;
    const start = text.indexOf(kw);
    if (start < 0) return;
    const kChars = charEls.slice(start, start + kw.length);
    const lineY = kChars[0].offsetTop;
    const sameLine = kChars.filter((c) => c.offsetTop === lineY);
    const first = sameLine[0];
    const last = sameLine[sameLine.length - 1];
    const rule = document.createElement("span");
    rule.className = "tw-rule";
    rule.style.left = `${first.offsetLeft}px`;
    rule.style.top = `${first.offsetTop + first.offsetHeight}px`;
    rule.style.width = `${last.offsetLeft + last.offsetWidth - first.offsetLeft}px`;
    el.appendChild(rule);
    rules.push({ rule, endIndex: start + kw.length - 1 });
  });

  // enter：容器就位 → 逐字弹出 + 光标跟随 → 词下划描画 → 光标闪 3 次停实色
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, ease: "power1.out" }, 0);

  if (cursorEl) {
    // 光标初始位：首字左侧（mount 时静态就位，时间线只负责推进）
    gsap.set(cursorEl, {
      x: charEls[0].offsetLeft,
      y: charEls[0].offsetTop + (charEls[0].offsetHeight - cursorH) / 2,
    });
    enter.fromTo(cursorEl, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.15, ease: "power1.out" }, 0);
  }

  charEls.forEach((c, i) => {
    const at = t0 + i * dt;
    enter.fromTo(c, { autoAlpha: 0 }, { autoAlpha: 1, duration: charDur, ease: "power1.out" }, at);
    if (cursorEl && chars[i] !== "\n") {
      enter.to(
        cursorEl,
        {
          x: c.offsetLeft + c.offsetWidth,
          y: c.offsetTop + (c.offsetHeight - cursorH) / 2,
          duration: cursorDur,
          ease: "power1.out",
        },
        at
      );
    }
  });

  const typeEnd = t0 + (chars.length - 1) * dt + charDur;

  // 词打完，虚线自左向右描画
  rules.forEach(({ rule, endIndex }) => {
    enter.fromTo(
      rule,
      { scaleX: 0 },
      { scaleX: 1, duration: 0.3, ease: "power2.out" },
      t0 + endIndex * dt + charDur
    );
  });

  // 打完光标闪烁 3 次停在实色；repeat 走 floor 公式，禁无限循环
  if (cursorEl) {
    const blinkHalf = 0.4; // 半周期：灭或亮
    const blinkTotal = blinkHalf * 2 * 3; // 闪烁 3 次的总窗口
    const blinkRepeat = Math.max(0, Math.floor(blinkTotal / blinkHalf) - 1);
    enter.to(
      cursorEl,
      { autoAlpha: 0, duration: blinkHalf, ease: "steps(1)", yoyo: true, repeat: blinkRepeat },
      typeEnd
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
