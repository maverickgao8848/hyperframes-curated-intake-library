import {
  createFidelityHost,
  createStandardSegments,
  destroyFidelity,
  htmlNode,
  normalizeLocalFrame,
  validateParams,
} from "./fidelity-runtime.js";

const text = (value) => typeof value === "string" && value.trim().length > 0;
const finite = (value) => typeof value === "number" && Number.isFinite(value);
const fail = (id, message) => { throw new Error(`[${id}] ${message}`); };
const list = (id, value, label, min, max) => {
  if (!Array.isArray(value) || value.length < min || value.length > max) fail(id, `${label} requires ${min}-${max} items`);
  return value;
};
const unique = (id, items, label) => {
  const ids = items.map((item, index) => {
    if (!item || !text(item.id)) fail(id, `${label}[${index}].id is required`);
    return item.id;
  });
  if (new Set(ids).size !== ids.length) fail(id, `${label} ids must be unique`);
};

export function validateUiMockPayload(id, kind, data, mock) {
  if (mock !== true) fail(id, "mock must be explicitly true");
  if (!data || typeof data !== "object" || Array.isArray(data)) fail(id, "data must be project-provided");
  if (kind === "terminal") {
    if (!text(data.command)) fail(id, "command is required");
    list(id, data.output, "data.output", 1, 16).forEach((line, index) => { if (!text(line)) fail(id, `data.output[${index}] must be text`); });
  } else if (kind === "chat-thread") {
    list(id, data.messages, "data.messages", 2, 12).forEach((message, index) => {
      if (!message || !["user", "assistant"].includes(message.role) || !text(message.text)) fail(id, `data.messages[${index}] is invalid`);
    });
  } else if (kind === "browser") {
    if (!text(data.url) || !text(data.pageTitle)) fail(id, "url and pageTitle are required");
    list(id, data.sections, "data.sections", 1, 8).forEach((section, index) => { if (!section || !text(section.heading) || !text(section.body)) fail(id, `data.sections[${index}] is invalid`); });
  } else if (kind === "code-editor") {
    if (!text(data.language) || !text(data.code)) fail(id, "language and code are required");
    const lines = data.code.split(/\r?\n/);
    if (lines.length > 40) fail(id, "code is capped at 40 lines");
    (data.highlightLines ?? []).forEach((line) => { if (!Number.isInteger(line) || line < 1 || line > lines.length) fail(id, "highlightLines must reference code lines"); });
  } else if (kind === "api-call") {
    if (!["GET", "POST", "PUT", "PATCH", "DELETE"].includes(data.method) || !text(data.url) || !finite(data.latencyMs) || data.latencyMs < 0 || !Number.isInteger(data.status) || data.status < 100 || data.status > 599 || !text(data.requestText) || !text(data.responseText)) fail(id, "API request metadata and project-provided payloads are required");
  } else if (kind === "dashboard") {
    if (!text(data.asOf)) fail(id, "asOf timestamp or reporting period is required");
    const metrics = list(id, data.metrics, "data.metrics", 1, 8); unique(id, metrics, "data.metrics");
    metrics.forEach((metric, index) => { if (!text(metric.label) || !["string", "number"].includes(typeof metric.value) || (metric.status !== undefined && !["ok", "warning", "critical", "neutral"].includes(metric.status))) fail(id, `data.metrics[${index}] is invalid`); });
  } else fail(id, `unknown UI mock kind ${kind}`);
  return data;
}

const node = (tag, className, value) => htmlNode(tag, className, value);

function chrome(prefix, label) {
  const bar = node("div", `${prefix}-chrome`), dots = node("span", `${prefix}-dots`, "● ● ●");
  bar.append(dots, node("strong", null, label)); return bar;
}

function renderTerminal(body, data, prefix, marks) {
  body.appendChild(chrome(prefix, "PROJECT TERMINAL"));
  const terminal = node("div", `${prefix}-terminal`), command = node("div", `${prefix}-command`);
  command.append(node("span", `${prefix}-prompt`, "$"), node("code", null, data.command)); terminal.appendChild(command); marks.push(command);
  data.output.forEach((line) => { const output = node("div", `${prefix}-output`, line); terminal.appendChild(output); marks.push(output); });
  body.appendChild(terminal);
}

function renderChat(body, data, prefix, marks) {
  body.appendChild(chrome(prefix, "SIMULATED CONVERSATION"));
  const thread = node("div", `${prefix}-thread`);
  data.messages.forEach((message) => {
    const item = node("article", `${prefix}-message ${prefix}-${message.role}`);
    item.append(node("span", `${prefix}-role`, message.role.toUpperCase()), node("p", null, message.text)); thread.appendChild(item); marks.push(item);
  });
  body.appendChild(thread);
}

function renderBrowser(body, data, prefix, marks) {
  body.appendChild(chrome(prefix, "SIMULATED BROWSER"));
  const address = node("div", `${prefix}-address`, data.url), page = node("div", `${prefix}-page`);
  page.appendChild(node("h3", null, data.pageTitle));
  data.sections.forEach((section) => {
    const item = node("section", `${prefix}-page-section`); item.append(node("h4", null, section.heading), node("p", null, section.body)); page.appendChild(item); marks.push(item);
  });
  body.append(address, page);
}

function renderCode(body, data, prefix, marks) {
  body.appendChild(chrome(prefix, `SIMULATED EDITOR · ${data.language.toUpperCase()}`));
  const code = node("ol", `${prefix}-code`);
  data.code.split(/\r?\n/).forEach((line, index) => {
    const item = node("li", data.highlightLines?.includes(index + 1) ? `${prefix}-highlight` : "");
    item.appendChild(node("code", null, line || " ")); code.appendChild(item); marks.push(item);
  });
  body.appendChild(code);
}

function renderApi(body, data, prefix, marks) {
  body.appendChild(chrome(prefix, "SIMULATED API INSPECTOR"));
  const request = node("section", `${prefix}-api-panel`), response = node("section", `${prefix}-api-panel`);
  const requestHead = node("div", `${prefix}-api-head`); requestHead.append(node("strong", `${prefix}-method`, data.method), node("span", `${prefix}-url`, data.url));
  request.append(requestHead, node("pre", null, data.requestText));
  const responseHead = node("div", `${prefix}-api-head`); responseHead.append(node("strong", null, String(data.status)), node("span", null, `${data.latencyMs} ms`));
  response.append(responseHead, node("pre", null, data.responseText)); body.append(request, response); marks.push(request, response);
}

function renderDashboard(body, data, prefix, marks) {
  body.appendChild(chrome(prefix, `SIMULATED DASHBOARD · AS OF ${data.asOf}`));
  const grid = node("div", `${prefix}-metrics`);
  data.metrics.forEach((metric) => {
    const card = node("article", `${prefix}-metric ${prefix}-${metric.status ?? "neutral"}`);
    card.append(node("span", null, metric.label), node("strong", null, metric.value)); grid.appendChild(card); marks.push(card);
  });
  body.appendChild(grid);
}

function renderUi(body, kind, data, prefix, marks) {
  if (kind === "terminal") renderTerminal(body, data, prefix, marks);
  else if (kind === "chat-thread") renderChat(body, data, prefix, marks);
  else if (kind === "browser") renderBrowser(body, data, prefix, marks);
  else if (kind === "code-editor") renderCode(body, data, prefix, marks);
  else if (kind === "api-call") renderApi(body, data, prefix, marks);
  else renderDashboard(body, data, prefix, marks);
}

export function mountUiMockComponent(root, context = {}, meta, prefix, config) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  validateUiMockPayload(meta.id, config.kind, params.data, params.mock);
  const css = `.comp-${meta.id}{position:relative;display:grid;grid-template-rows:auto minmax(0,1fr) auto;width:100%;height:100%;min-height:340px;padding:var(--comp-space-5);gap:var(--comp-space-3);border:2px dashed var(--comp-line-strong);border-radius:var(--comp-radius-md);background:var(--comp-surface);color:var(--comp-ink);font-family:var(--comp-font-sans);overflow:hidden}.comp-${meta.id}:after{content:"SIMULATED UI";position:absolute;right:18px;bottom:42px;color:var(--comp-line-strong);font:900 clamp(18px,4vw,54px) var(--comp-font-display);transform:rotate(-12deg);pointer-events:none;opacity:.35}.comp-${meta.id} .${prefix}-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.comp-${meta.id} .${prefix}-title{margin:0;font:800 clamp(22px,3vw,42px)/1.05 var(--comp-font-display)}.comp-${meta.id} .${prefix}-badge{padding:7px 10px;border:2px solid var(--comp-accent);border-radius:999px;color:var(--comp-accent);font:800 11px var(--comp-font-mono);letter-spacing:.08em;white-space:nowrap}.comp-${meta.id} .${prefix}-body{position:relative;display:grid;min-height:0;align-content:start;border:1px solid var(--comp-line);border-radius:var(--comp-radius-sm);background:var(--comp-canvas);overflow:hidden}.comp-${meta.id} .${prefix}-chrome{display:flex;align-items:center;gap:16px;padding:9px 12px;border-bottom:1px solid var(--comp-line);background:var(--comp-surface-strong);font:700 12px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-dots{color:var(--comp-accent);letter-spacing:.2em}.comp-${meta.id} .${prefix}-source{color:var(--comp-muted);font:500 13px/1.4 var(--comp-font-mono)}.comp-${meta.id} .${prefix}-terminal,.comp-${meta.id} .${prefix}-thread,.comp-${meta.id} .${prefix}-page,.comp-${meta.id} .${prefix}-code{padding:16px;overflow:auto}.comp-${meta.id} .${prefix}-command{display:flex;gap:10px;color:var(--comp-ink);font:650 15px/1.5 var(--comp-font-mono);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-prompt,.comp-${meta.id} .${prefix}-method{color:var(--comp-accent)}.comp-${meta.id} .${prefix}-output{color:var(--comp-muted);font:500 14px/1.45 var(--comp-font-mono);white-space:pre-wrap;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-thread{display:grid;gap:10px}.comp-${meta.id} .${prefix}-message{max-width:80%;padding:12px 14px;border:1px solid var(--comp-line);border-radius:14px;background:var(--comp-surface)}.comp-${meta.id} .${prefix}-assistant{justify-self:end;border-color:var(--comp-accent)}.comp-${meta.id} .${prefix}-message p{margin:4px 0 0;white-space:pre-wrap;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-role{color:var(--comp-muted);font:700 10px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-address{padding:10px 14px;border-bottom:1px solid var(--comp-line);color:var(--comp-muted);font:500 12px var(--comp-font-mono);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-page{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.comp-${meta.id} .${prefix}-page>h3{grid-column:1/-1;margin:0}.comp-${meta.id} .${prefix}-page-section{padding:12px;border:1px solid var(--comp-line);background:var(--comp-surface)}.comp-${meta.id} h4,.comp-${meta.id} .${prefix}-page-section p{margin:0}.comp-${meta.id} .${prefix}-page-section p{margin-top:6px;color:var(--comp-muted)}.comp-${meta.id} .${prefix}-code{margin:0;list-style-position:outside;padding-left:54px;color:var(--comp-muted);font:500 13px/1.5 var(--comp-font-mono)}.comp-${meta.id} .${prefix}-code code{color:var(--comp-ink);white-space:pre-wrap;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-highlight{background:color-mix(in srgb,var(--comp-accent) 18%,transparent);outline:1px solid var(--comp-accent)}.comp-${meta.id} .${prefix}-body:has(.${prefix}-api-panel){grid-template-columns:repeat(2,minmax(0,1fr));gap:1px}.comp-${meta.id} .${prefix}-api-panel{min-width:0;padding:14px;background:var(--comp-surface)}.comp-${meta.id} .${prefix}-api-head{display:flex;gap:10px;align-items:flex-start}.comp-${meta.id} .${prefix}-url{overflow-wrap:anywhere}.comp-${meta.id} pre{margin:12px 0 0;white-space:pre-wrap;overflow-wrap:anywhere;color:var(--comp-muted);font:500 12px/1.45 var(--comp-font-mono)}.comp-${meta.id} .${prefix}-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;padding:14px}.comp-${meta.id} .${prefix}-metric{display:grid;gap:8px;padding:14px;border:1px solid var(--comp-line);background:var(--comp-surface)}.comp-${meta.id} .${prefix}-metric span{color:var(--comp-muted)}.comp-${meta.id} .${prefix}-metric strong{font:800 clamp(22px,3vw,38px) var(--comp-font-display)}.comp-${meta.id} .${prefix}-warning,.comp-${meta.id} .${prefix}-critical{border-left:5px solid var(--comp-accent)}`;
  const { element, gsap } = createFidelityHost(root, context, meta, prefix, css);
  element.dataset.mock = "true"; element.dataset.evidence = "simulated-interface"; element.dataset.exportEvidence = "false";
  const head = node("header", `${prefix}-head`); head.append(node("h2", `${prefix}-title`, params.title), node("span", `${prefix}-badge`, "MOCK · NOT EVIDENCE")); element.appendChild(head);
  const body = node("div", `${prefix}-body`), marks = []; renderUi(body, config.kind, params.data, prefix, marks); element.appendChild(body);
  element.appendChild(node("footer", `${prefix}-source`, params.sourceNote));
  const state = { progress: 0 };
  const render = () => marks.forEach((mark, index) => { mark.style.opacity = state.progress >= (index + 1) / Math.max(1, marks.length) ? "" : "0"; });
  const segments = createStandardSegments(gsap, element, marks, state, render); render();
  return {
    segments,
    seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); },
    destroy() { destroyFidelity(element, segments); },
  };
}
