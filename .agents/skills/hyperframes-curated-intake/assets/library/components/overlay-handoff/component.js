/**
 * overlay-handoff · 叠化交棒（rack-focus）
 *
 * 图形场景向实拍/截图的交棒：媒体从 scale 1.06 + 低透明度的焦点外浮起，
 * 在 handoff 段落稳到 scale 1；图形层孩子中非 keepComponents 的降到 0，
 * keepComponents 降到 lingerOpacity 以半透明残留压在媒体上。
 * 纯交棒段，不绘制表面，无自有 --comp-* token。契约见 assets/components/README.md。
 */

import {
  assignInstanceRoot,
  assertProjectLocalMediaRef,
  createInstanceScope,
} from "../runtime.js";

const CSS = `
.comp-overlay-handoff-media{position:absolute;inset:0;width:100%;height:100%;
object-fit:cover;opacity:0;visibility:hidden;pointer-events:none;user-select:none}
`;

function ensureStyle(id, css) {
  if (document.getElementById(`comp-style-${id}`)) return;
  const style = document.createElement("style");
  style.id = `comp-style-${id}`;
  style.textContent = css;
  document.head.appendChild(style);
}

export const meta = { id: "overlay-handoff", version: 1 };

// keepComponents 允许选择器、元素，或场景层持有的组件实例（暴露 el/root/element）
function resolveEl(item, scope) {
  if (!item) return null;
  if (typeof item === "string")
    return scope.querySelector(item) || document.querySelector(item);
  if (item instanceof Element) return item;
  if (item.el instanceof Element) return item.el;
  if (item.root instanceof Element) return item.root;
  if (item.element instanceof Element) return item.element;
  return null;
}

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const scope = createInstanceScope(meta.id, "oh", context);
  const {
    mediaRef,
    lingerOpacity = 0.18,
    keepComponents = [],
    graphicsLayer,
    handoffSeconds = 1.2,
  } = params;

  if (!mediaRef) throw new Error("[overlay-handoff] params.mediaRef 必填");
  if (!graphicsLayer) throw new Error("[overlay-handoff] params.graphicsLayer 必填");

  ensureStyle(meta.id, CSS);

  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error("[overlay-handoff] mount root 不存在");

  const gsap = window.gsap;
  if (!gsap) throw new Error("[overlay-handoff] 需要全局 window.gsap");

  const gl =
    typeof graphicsLayer === "string"
      ? document.querySelector(graphicsLayer)
      : graphicsLayer;
  if (!gl) throw new Error("[overlay-handoff] graphicsLayer 不存在");

  // 残留是余韵不是内容：lingerOpacity 上限 0.3
  const linger = Math.min(0.3, Math.max(0, Number(lingerOpacity) || 0));

  // 媒体由组件创建；视频播放与 seek 仍由 HyperFrames 框架拥有。
  const localMediaRef = assertProjectLocalMediaRef(meta.id, mediaRef);
  const isVideo = /\.(?:mp4|webm|mov)(?:[?#].*)?$/i.test(localMediaRef);
  const media = document.createElement(isVideo ? "video" : "img");
  media.className = "comp-overlay-handoff-media";
  assignInstanceRoot(media, scope);
  media.dataset.component = meta.id;
  media.setAttribute("data-layout-allow-occlusion", "");
  if (isVideo) {
    media.muted = true;
    media.playsInline = true;
    media.preload = "auto";
  } else {
    media.alt = "";
  }
  media.src = localMediaRef;
  const glZ = parseInt(getComputedStyle(gl).zIndex, 10);
  const baseZ = Number.isNaN(glZ) ? 0 : glZ;
  media.style.zIndex = String(baseZ);
  host.appendChild(media);

  const graphicsLayerOriginal = {
    position: gl.style.position,
    zIndex: gl.style.zIndex,
  };
  if (getComputedStyle(gl).position === "static") gl.style.position = "relative";
  gl.style.zIndex = String(baseZ + 1);

  // 图形层孩子按 keepComponents 分流：含残留元素的分支整体保留，其余随交棒退出
  const keepEls = keepComponents
    .map((item) => resolveEl(item, gl))
    .filter(Boolean);
  const children = Array.from(gl.children);
  const isKeepBranch = (child) =>
    keepEls.some((k) => k === child || child.contains(k));
  const fadeOutEls = children.filter((c) => !isKeepBranch(c));

  // destroy 时还原场景元素的 inline 状态，保持非破坏
  const originals = [...children, ...keepEls].map((el) => ({
    el,
    opacity: el.style.opacity,
    visibility: el.style.visibility,
    position: el.style.position,
    zIndex: el.style.zIndex,
  }));

  // 残留元素要压在媒体上：z-index 提到媒体之上（handoff 0 点生效）
  const raiseKeeps = () => {
    keepEls.forEach((k) => {
      if (getComputedStyle(k).position === "static")
        k.style.position = "relative";
      k.style.zIndex = String(baseZ + 2);
    });
  };

  // enter：媒体从焦点外浮起（opacity + scale 1.06→1.02），图形层同步降到 60%
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(
    media,
    { autoAlpha: 0, scale: 1.06 },
    {
      autoAlpha: 1,
      scale: 1.02,
      duration: 0.6,
      ease: "power2.out",
    },
    0
  );
  children.forEach((child, i) => {
    enter.to(
      child,
      { autoAlpha: 0.6, duration: 0.5, ease: "power1.out" },
      i * 0.06
    );
  });

  // handoff：交棒主段——媒体聚焦落稳到 scale 1，
  // 非残留降到 0，残留降到 lingerOpacity 停在媒体上
  const handoff = gsap.timeline({ paused: true });
  handoff.call(raiseKeeps, null, 0);
  handoff.to(
    media,
    { scale: 1, duration: 0.8, ease: "power2.out" },
    0
  );
  fadeOutEls.forEach((el, i) => {
    handoff.to(
      el,
      { autoAlpha: 0, duration: 0.4, ease: "power1.in" },
      0.1 + i * 0.06
    );
  });
  keepEls.forEach((el, i) => {
    handoff.to(
      el,
      { autoAlpha: linger, duration: 0.6, ease: "power1.out" },
      0.3 + i * 0.06
    );
  });
  handoff.duration(handoffSeconds);

  // dim / exit：媒体与残留组件一起降压、退出
  const dim = gsap.timeline({ paused: true });
  dim.to(media, { autoAlpha: 0.3, duration: 0.3, ease: "power1.out" }, 0);
  keepEls.forEach((el) => {
    dim.to(el, { autoAlpha: linger * 0.5, duration: 0.3, ease: "power1.out" }, 0);
  });

  const exit = gsap.timeline({ paused: true });
  exit.to(media, { autoAlpha: 0, y: -10, duration: 0.4, ease: "power2.in" }, 0);
  keepEls.forEach((el) => {
    exit.to(el, { autoAlpha: 0, y: -10, duration: 0.4, ease: "power2.in" }, 0);
  });

  const segments = { enter, handoff, dim, exit };
  return {
    segments,
    seek(localFrame) {
      enter.time(Math.max(0, localFrame) / fps);
    },
    destroy() {
      Object.values(segments).forEach((tl) => tl.kill());
      originals.forEach(({ el, opacity, visibility, position, zIndex }) => {
        el.style.opacity = opacity;
        el.style.visibility = visibility;
        el.style.position = position;
        el.style.zIndex = zIndex;
      });
      gl.style.position = graphicsLayerOriginal.position;
      gl.style.zIndex = graphicsLayerOriginal.zIndex;
      media.remove();
    },
  };
}
