/**
 * dispatch-flight · 分发飞行
 *
 * payload 文本芯片沿抛物弧从 from 容器抛送到 to 容器，表达任务/数据的交接：
 * x 匀速 + y 两段（上弧 / 下落）拼出抛物线，芯片随飞行微倾 ±6° 再回正；
 * trail 开启时身后跟两重错峰 0.06s 的低透明残影；落点 1.06 倍缩放回弹锁定，
 * to 容器 hairline 边框向 accent 闪光一次再回。
 * 契约见 assets/components/README.md。
 */

import { assignInstanceRoot, createInstanceScope } from "../runtime.js";

const CSS = `
.comp-dispatch-flight{position:absolute;inset:0;overflow:visible;pointer-events:none}
.comp-dispatch-flight .df-chip{position:absolute;left:0;top:0;display:inline-flex;align-items:center;
padding:.42em .9em;background:var(--comp-surface,rgba(236,236,236,.04));
border:1px solid var(--comp-line,rgba(236,236,236,.22));
border-radius:var(--comp-radius,10px);
font-family:var(--comp-font-mono,"JetBrains Mono","SFMono-Regular",Consolas,monospace);
font-size:var(--comp-df-size,12px);letter-spacing:.08em;
color:var(--comp-ink,#ececec);white-space:nowrap;will-change:transform;transform-origin:center}
.comp-dispatch-flight .df-ghost{background:transparent}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "dispatch-flight", version: 1 };

function resolveEl(ref) {
  return typeof ref === "string" ? document.querySelector(ref) : ref;
}

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "df", context);
  const { payload = "", from = null, to = null, trail = false } = params;
  if (!payload) throw new Error("[dispatch-flight] params.payload 不能为空");
  if (from == null) throw new Error("[dispatch-flight] params.from 不能为空");
  if (to == null) throw new Error("[dispatch-flight] params.to 不能为空");

  ensureStyle(meta.id, CSS);

  const host = resolveEl(root);
  if (!host) throw new Error("[dispatch-flight] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[dispatch-flight] 需要全局 window.gsap");

  const fromEl = resolveEl(from);
  if (!fromEl) throw new Error("[dispatch-flight] from 容器未找到（检查选择器或元素）");
  const toEl = resolveEl(to);
  if (!toEl) throw new Error("[dispatch-flight] to 容器未找到（检查选择器或元素）");

  // 覆盖层：透明、不自带表面，芯片在其内做跨容器位移
  const el = document.createElement("div");
  el.className = "comp-dispatch-flight";
  assignInstanceRoot(el, scope);
  el.dataset.component = meta.id;

  const chip = document.createElement("div");
  chip.className = "df-chip";
  chip.textContent = payload;
  el.appendChild(chip);

  const ghosts = [];
  if (trail) {
    for (let i = 0; i < 2; i++) {
      const g = document.createElement("div");
      g.className = "df-chip df-ghost";
      g.textContent = payload;
      g.setAttribute("aria-hidden", "true");
      g.setAttribute("data-layout-ignore", "");
      el.appendChild(g);
      ghosts.push(g);
    }
  }
  host.appendChild(el);

  // mount 同步测量（元素已在 DOM）：chip 中心对齐 from/to 容器中心，坐标相对覆盖层
  const layerRect = el.getBoundingClientRect();
  const fromRect = fromEl.getBoundingClientRect();
  const toRect = toEl.getBoundingClientRect();
  const chipW = chip.offsetWidth;
  const chipH = chip.offsetHeight;
  const x0 = fromRect.left + fromRect.width / 2 - layerRect.left - chipW / 2;
  const y0 = fromRect.top + fromRect.height / 2 - layerRect.top - chipH / 2;
  const x1 = toRect.left + toRect.width / 2 - layerRect.left - chipW / 2;
  const y1 = toRect.top + toRect.height / 2 - layerRect.top - chipH / 2;
  const dx = x1 - x0;
  const dy = y1 - y0;
  // 弧线恒向上抬（避让正文），高度随位移距离伸缩并夹紧
  const arcH = Math.min(110, Math.max(36, Math.hypot(dx, dy) * 0.22));
  const midY = (y0 + y1) / 2 - arcH;
  const tilt = dx >= 0 ? 6 : -6;

  // 落点闪光需要可插值颜色：探针读出 --comp-accent 与 to 容器边框的计算值
  const probe = document.createElement("div");
  probe.style.color = "var(--comp-accent,#ececec)";
  probe.style.display = "none";
  host.appendChild(probe);
  const accentColor = getComputedStyle(probe).color;
  probe.remove();
  const borderBase = getComputedStyle(toEl).borderTopColor;
  const borderInline = toEl.style.borderColor;

  // enter：芯片在 from 内成形（fade + 6px 上浮，0.4s）；残影保持隐藏到 flight
  gsap.set(chip, { x: x0, y: y0, rotation: 0, scale: 1 });
  ghosts.forEach((g) => gsap.set(g, { x: x0, y: y0, autoAlpha: 0, rotation: 0 }));
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(
    chip,
    { autoAlpha: 0, y: y0 + 6 },
    { autoAlpha: 1, y: y0, duration: 0.4, ease: "power2.out" },
    0
  );

  // flight：0.8s 抛物弧飞行（x 匀速，y 上弧 power1.out / 下落 power1.in），
  // 切线倾角 0→±6°→0；残影错峰 0.06s 复制同一组 tween，落地后 0.2s 内消散；
  // 落点 1.06 缩放回弹锁定，to 容器边框闪光一次
  const TRAVEL = 0.8;
  const flight = gsap.timeline({ paused: true });
  flight.to(chip, { x: x1, duration: TRAVEL, ease: "none" }, 0);
  flight.to(chip, { y: midY, duration: TRAVEL / 2, ease: "power1.out" }, 0);
  flight.to(chip, { y: y1, duration: TRAVEL / 2, ease: "power1.in" }, TRAVEL / 2);
  flight.to(chip, { rotation: tilt, duration: 0.3, ease: "power1.out" }, 0);
  flight.to(chip, { rotation: 0, duration: 0.5, ease: "power1.inOut" }, 0.3);

  ghosts.forEach((g, i) => {
    const delay = (i + 1) * 0.06;
    const alpha = i === 0 ? 0.28 : 0.14;
    flight.fromTo(g, { autoAlpha: 0 }, { autoAlpha: alpha, duration: 0.08, ease: "none" }, delay);
    flight.to(g, { x: x1, duration: TRAVEL, ease: "none" }, delay);
    flight.to(g, { y: midY, duration: TRAVEL / 2, ease: "power1.out" }, delay);
    flight.to(g, { y: y1, duration: TRAVEL / 2, ease: "power1.in" }, delay + TRAVEL / 2);
    flight.to(g, { rotation: tilt, duration: 0.3, ease: "power1.out" }, delay);
    flight.to(g, { rotation: 0, duration: 0.5, ease: "power1.inOut" }, delay + 0.3);
    flight.to(g, { autoAlpha: 0, duration: 0.2, ease: "power1.out" }, delay + TRAVEL);
  });

  flight.to(chip, { scale: 1.06, duration: 0.08, ease: "power1.out" }, TRAVEL);
  flight.to(chip, { scale: 1, duration: 0.18, ease: "power2.out" }, TRAVEL + 0.08);
  flight.to(toEl, { borderColor: accentColor, duration: 0.08, ease: "none" }, TRAVEL);
  flight.to(toEl, { borderColor: borderBase, duration: 0.32, ease: "power1.out" }, TRAVEL + 0.08);

  const dim = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0.3, duration: 0.3, ease: "power1.out" });
  const exit = gsap
    .timeline({ paused: true })
    .to(el, { autoAlpha: 0, y: -10, duration: 0.4, ease: "power2.in" });

  const segments = { enter, flight, dim, exit };
  return {
    segments,
    seek(localFrame) {
      enter.time(Math.max(0, localFrame) / fps);
    },
    destroy() {
      Object.values(segments).forEach((tl) => tl.kill());
      toEl.style.borderColor = borderInline;
      el.remove();
    },
  };
}
