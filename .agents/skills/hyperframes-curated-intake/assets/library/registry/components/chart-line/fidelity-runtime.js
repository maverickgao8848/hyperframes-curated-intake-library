import { assignInstanceRoot, createInstanceScope } from "./runtime.js";

export const COMMON_PARAM_SCHEMA = Object.freeze({
  width: { type: "string", default: "100%" },
  height: { type: "string", default: "auto" },
  scale: { type: "number", min: 0.75, max: 1.25, default: 1 },
  align: { type: "enum", values: ["start", "center", "end"], default: "center" },
  anchor: {
    type: "enum",
    values: ["top-left", "top-right", "center", "bottom-left", "bottom-right"],
    default: "center",
  },
  density: {
    type: "enum",
    values: ["sparse", "comfortable", "dense"],
    default: "comfortable",
  },
  emphasis: {
    type: "enum",
    values: ["neutral", "primary", "warning", "success"],
    default: "neutral",
  },
  surface: {
    type: "enum",
    values: ["transparent", "subtle", "solid"],
    default: "transparent",
  },
  padding: { type: "string", default: "var(--comp-space-4)" },
  locale: {
    type: "enum",
    values: ["zh-CN", "en-US", "project"],
    default: "project",
  },
  reducedMotion: { type: "boolean", default: false },
});

export const REQUIRED_COMPONENT_TOKENS = Object.freeze([
  "--comp-canvas",
  "--comp-ink",
  "--comp-muted",
  "--comp-surface",
  "--comp-surface-strong",
  "--comp-accent",
  "--comp-positive",
  "--comp-warning",
  "--comp-negative",
  "--comp-line",
  "--comp-line-strong",
  "--comp-radius-sm",
  "--comp-radius-md",
  "--comp-font-display",
  "--comp-font-sans",
  "--comp-font-mono",
  ...Array.from({ length: 8 }, (_, index) => `--comp-space-${index + 1}`),
]);

function schemaError(componentId, field, message) {
  return new Error(`[${componentId}] params.${field} ${message}`);
}

export function validateParams(componentId, params = {}, schema = {}) {
  if (!params || typeof params !== "object" || Array.isArray(params)) {
    throw new Error(`[${componentId}] context.params 必须是对象`);
  }
  const definitions = { ...COMMON_PARAM_SCHEMA, ...schema };
  const result = {};
  for (const [field, definition] of Object.entries(definitions)) {
    const present = Object.prototype.hasOwnProperty.call(params, field);
    const value = present ? params[field] : definition.default;
    if (definition.required && (value === undefined || value === null || value === "")) {
      throw schemaError(componentId, field, "为必填项");
    }
    if (value === undefined) continue;
    if (definition.type === "number") {
      if (typeof value !== "number" || !Number.isFinite(value)) {
        throw schemaError(componentId, field, "必须是有限数字");
      }
      if (definition.min !== undefined && value < definition.min) {
        throw schemaError(componentId, field, `不得小于 ${definition.min}`);
      }
      if (definition.max !== undefined && value > definition.max) {
        throw schemaError(componentId, field, `不得大于 ${definition.max}`);
      }
    } else if (definition.type === "boolean") {
      if (typeof value !== "boolean") throw schemaError(componentId, field, "必须是 boolean");
    } else if (definition.type === "string") {
      if (typeof value !== "string") throw schemaError(componentId, field, "必须是字符串");
      if (definition.maxLength && [...value].length > definition.maxLength) {
        throw schemaError(componentId, field, `长度不得超过 ${definition.maxLength}`);
      }
    } else if (definition.type === "array") {
      if (!Array.isArray(value)) throw schemaError(componentId, field, "必须是数组");
      if (definition.minItems !== undefined && value.length < definition.minItems) {
        throw schemaError(componentId, field, `至少需要 ${definition.minItems} 项`);
      }
      if (definition.maxItems !== undefined && value.length > definition.maxItems) {
        throw schemaError(componentId, field, `最多允许 ${definition.maxItems} 项`);
      }
    } else if (definition.type === "enum" && !definition.values.includes(value)) {
      throw schemaError(componentId, field, `必须是 ${definition.values.join(" | ")}`);
    }
    result[field] = value;
  }
  return Object.freeze(result);
}

export function deterministicId(instanceId, localId) {
  const safe = String(localId).trim().toLowerCase().replace(/[^a-z0-9-]+/g, "-");
  if (!safe) throw new Error("deterministicId localId 不能为空");
  return `${instanceId}-${safe}`;
}

export function normalizeLocalFrame(localFrame, durationFrames) {
  const frame = Number(localFrame);
  const duration = Number(durationFrames);
  if (!Number.isFinite(frame)) return 0;
  if (!Number.isFinite(duration) || duration <= 0) return Math.max(0, frame);
  return Math.max(0, Math.min(duration, frame));
}

export function createTeardown() {
  const callbacks = [];
  let destroyed = false;
  return {
    add(callback) {
      if (typeof callback !== "function") throw new Error("teardown callback 必须是函数");
      if (destroyed) callback();
      else callbacks.push(callback);
      return callback;
    },
    run() {
      if (destroyed) return;
      destroyed = true;
      for (const callback of callbacks.splice(0).reverse()) callback();
    },
    get destroyed() {
      return destroyed;
    },
  };
}

export function resolveComponentTokens(element, names = REQUIRED_COMPONENT_TOKENS) {
  const computed =
    typeof getComputedStyle === "function" && element ? getComputedStyle(element) : null;
  return Object.fromEntries(
    names.map((name) => [name, computed?.getPropertyValue(name)?.trim() || ""]),
  );
}

// Shared contract marker: every fidelity component exposes seek(localFrame).
export function createFidelityHost(root, context, meta, prefix, css) {
  const host = typeof root === "string" ? document.querySelector(root) : root;
  if (!host) throw new Error(`[${meta.id}] mount root 不存在`);
  const gsap = context.gsap ?? window.gsap;
  if (!gsap) throw new Error(`[${meta.id}] 需要全局 window.gsap`);
  const styleId = `comp-style-${meta.id}`;
  if (!document.getElementById(styleId)) {
    const style = document.createElement("style");
    style.id = styleId;
    style.textContent = css;
    document.head.appendChild(style);
  }
  const scope = createInstanceScope(meta.id, prefix, context);
  const element = document.createElement("section");
  element.className = `comp-${meta.id}`;
  element.dataset.component = meta.id;
  assignInstanceRoot(element, scope);
  host.appendChild(element);
  return { element, gsap };
}

export function htmlNode(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = String(text);
  return element;
}

export function svgNode(tag, attributes = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [name, value] of Object.entries(attributes)) {
    element.setAttribute(name, String(value));
  }
  return element;
}

export function clamp01(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.min(1, number)) : fallback;
}

export function seededUnit(seed, index) {
  let value = (Number(seed) || 1) ^ Math.imul(index + 1, 0x9e3779b1);
  value ^= value >>> 16;
  value = Math.imul(value, 0x21f0aaad);
  value ^= value >>> 15;
  value = Math.imul(value, 0x735a2d97);
  value ^= value >>> 15;
  return (value >>> 0) / 4294967296;
}

export function createSeededCanvasState(seed = 1) {
  let index = 0;
  return {
    next() {
      return seededUnit(seed, index++);
    },
    reset() {
      index = 0;
    },
  };
}

export function standardTimelines(gsap, element, parts, state, render) {
  const enter = gsap.timeline({ paused: true });
  enter.fromTo(element, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, ease: "power2.out" }, 0);
  if (parts.length) {
    enter.fromTo(
      parts,
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.45, stagger: { amount: 0.35 }, ease: "power2.out" },
      0.06,
    );
  }
  enter.to(state, { progress: 1, duration: 1.1, ease: "power2.inOut", onUpdate: render }, 0.05);
  const emphasis = gsap.timeline({ paused: true })
    .to(element, { scale: 1.018, duration: 0.28, ease: "power2.out" })
    .to(element, { scale: 1, duration: 0.32, ease: "power1.inOut" });
  const dim = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0.32, duration: 0.3, ease: "power1.out" });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, y: -14, duration: 0.4, ease: "power2.in" });
  render();
  return { enter, emphasis, dim, exit };
}

export function createStandardSegments(gsap, element, parts = [], state = {}, render = () => {}) {
  const enter = gsap.timeline({ paused: true })
    .fromTo(element, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3, ease: "power2.out" }, 0);
  if (parts.length) {
    enter.fromTo(
      parts,
      { autoAlpha: 0, y: 10 },
      { autoAlpha: 1, y: 0, duration: 0.4, stagger: { amount: 0.25 }, ease: "power2.out" },
      0.05,
    );
  }
  const explain = gsap.timeline({ paused: true })
    .to(state, { progress: 1, duration: 1, ease: "none", onUpdate: render }, 0);
  const emphasize = gsap.timeline({ paused: true })
    .to(element, { scale: 1.015, duration: 0.2, ease: "power2.out" })
    .to(element, { scale: 1, duration: 0.25, ease: "power1.inOut" });
  const exit = gsap.timeline({ paused: true })
    .to(element, { autoAlpha: 0, y: -10, duration: 0.35, ease: "power2.in" });
  render();
  return { enter, explain, emphasize, exit };
}

export function destroyFidelity(element, segments, cleanup) {
  Object.values(segments).forEach((timeline) => timeline.kill());
  cleanup?.();
  element.remove();
}
