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
const strings = (id, value, label, min = 1, max = 6) => {
  list(id, value, label, min, max).forEach((item, index) => { if (!text(item)) fail(id, `${label}[${index}] must be text`); });
  return value;
};
const unique = (id, items, label) => {
  const ids = items.map((item, index) => {
    if (!item || !text(item.id)) fail(id, `${label}[${index}].id is required`);
    return item.id;
  });
  if (new Set(ids).size !== ids.length) fail(id, `${label} ids must be unique`);
};

export function validateAbstractPayload(id, kind, data) {
  if (!data || typeof data !== "object" || Array.isArray(data)) fail(id, "data must be an object");
  if (!data.mapping || !text(data.mapping.concept) || !text(data.mapping.visual)) fail(id, "data.mapping requires concept and visual fields");
  if (kind === "analogy") {
    if (!text(data.unfamiliar) || !text(data.familiar) || !text(data.relation)) fail(id, "unfamiliar, familiar and relation are required");
  } else if (kind === "black-box") {
    strings(id, data.inputs, "data.inputs", 1, 5); strings(id, data.outputs, "data.outputs", 1, 5);
    if (!text(data.processLabel)) fail(id, "processLabel is required");
  } else if (kind === "equation") {
    const terms = list(id, data.terms, "data.terms", 2, 5);
    terms.forEach((term, index) => {
      if (!term || !text(term.label) || (index > 0 && !text(term.operator))) fail(id, `data.terms[${index}] is invalid`);
    });
    if (!text(data.result)) fail(id, "result is required");
  } else if (kind === "spectrum") {
    if (!text(data.leftLabel) || !text(data.rightLabel)) fail(id, "single-axis endpoint labels are required");
    const items = list(id, data.items, "data.items", 1, 8); unique(id, items, "data.items");
    items.forEach((item, index) => { if (!text(item.label) || !finite(item.position) || item.position < 0 || item.position > 1) fail(id, `data.items[${index}] is invalid`); });
  } else if (kind === "iceberg") {
    strings(id, data.visible, "data.visible", 1, 5); strings(id, data.hidden, "data.hidden", 1, 7);
    if (!finite(data.visibleRatio) || data.visibleRatio < .15 || data.visibleRatio > .5) fail(id, "visibleRatio must be between 0.15 and 0.5");
  } else if (kind === "versus") {
    if (!text(data.leftLabel) || !text(data.rightLabel)) fail(id, "leftLabel and rightLabel are required");
    const rows = list(id, data.rows, "data.rows", 1, 7); unique(id, rows, "data.rows");
    rows.forEach((row, index) => { if (!text(row.label) || !text(row.left) || !text(row.right)) fail(id, `data.rows[${index}] must align one semantic dimension`); });
  } else if (kind === "placeholder") {
    if (!text(data.missingAsset) || !text(data.requiredSpec) || !text(data.blocker)) fail(id, "missingAsset, requiredSpec and blocker are required");
    if (data.approved !== undefined && typeof data.approved !== "boolean") fail(id, "approved must be boolean when supplied");
  } else fail(id, `unknown abstract kind ${kind}`);
  return data;
}

const node = (tag, className, value) => htmlNode(tag, className, value);

function mappingStrip(data, prefix) {
  const strip = node("aside", `${prefix}-mapping`);
  strip.append(node("span", null, `CONCEPT · ${data.mapping.concept}`), node("span", null, `VISUAL · ${data.mapping.visual}`));
  return strip;
}

function itemList(values, prefix) {
  const listNode = node("ul", `${prefix}-list`); values.forEach((value) => listNode.appendChild(node("li", null, value))); return listNode;
}

function renderAnalogy(body, data, prefix, marks) {
  const unfamiliar = node("article", `${prefix}-object`), familiar = node("article", `${prefix}-object`);
  unfamiliar.append(node("small", null, "UNFAMILIAR"), node("strong", null, data.unfamiliar));
  familiar.append(node("small", null, "FAMILIAR"), node("strong", null, data.familiar));
  const relation = node("div", `${prefix}-relation`, data.relation); body.append(unfamiliar, relation, familiar); marks.push(unfamiliar, relation, familiar);
}

function renderBlackBox(body, data, prefix, marks) {
  const inputs = node("section", `${prefix}-ports`), box = node("div", `${prefix}-black-box`, data.processLabel), outputs = node("section", `${prefix}-ports`);
  inputs.append(node("h3", null, "INPUT"), itemList(data.inputs, prefix)); outputs.append(node("h3", null, "OUTPUT"), itemList(data.outputs, prefix));
  body.append(inputs, box, outputs); marks.push(inputs, box, outputs);
}

function renderEquation(body, data, prefix, marks) {
  const equation = node("div", `${prefix}-equation`);
  data.terms.forEach((term, index) => {
    if (index > 0) equation.appendChild(node("span", `${prefix}-operator`, term.operator));
    const value = node("strong", `${prefix}-term`, term.label); equation.appendChild(value); marks.push(value);
  });
  equation.append(node("span", `${prefix}-operator`, "="), node("strong", `${prefix}-result`, data.result)); body.appendChild(equation);
}

function renderSpectrum(body, data, prefix, marks) {
  const axis = node("div", `${prefix}-spectrum`);
  axis.append(node("span", `${prefix}-left`, data.leftLabel), node("span", `${prefix}-right`, data.rightLabel));
  data.items.forEach((item) => {
    const point = node("article", `${prefix}-point`, item.label); point.style.left = `${item.position * 100}%`; point.dataset.position = String(item.position); axis.appendChild(point); marks.push(point);
  });
  body.appendChild(axis);
}

function renderIceberg(body, data, prefix, marks) {
  const iceberg = node("div", `${prefix}-iceberg`), visible = node("section", `${prefix}-visible`), hidden = node("section", `${prefix}-hidden`);
  visible.style.flex = `${data.visibleRatio}`; hidden.style.flex = `${1 - data.visibleRatio}`;
  visible.append(node("h3", null, `VISIBLE · ${Math.round(data.visibleRatio * 100)}%`), itemList(data.visible, prefix));
  hidden.append(node("h3", null, `HIDDEN · ${Math.round((1 - data.visibleRatio) * 100)}%`), itemList(data.hidden, prefix));
  iceberg.append(visible, hidden); body.appendChild(iceberg); marks.push(visible, hidden);
}

function renderVersus(body, data, prefix, marks) {
  const table = node("table", `${prefix}-versus`), head = node("thead"), headRow = node("tr");
  headRow.append(node("th", null, "Dimension"), node("th", null, data.leftLabel), node("th", null, data.rightLabel)); head.appendChild(headRow); table.appendChild(head);
  const tbody = node("tbody");
  data.rows.forEach((row) => {
    const tr = node("tr"); tr.dataset.rowId = row.id; tr.append(node("th", null, row.label), node("td", null, row.left), node("td", null, row.right)); tbody.appendChild(tr); marks.push(tr);
  });
  table.appendChild(tbody); body.appendChild(table);
}

function renderPlaceholder(body, data, prefix, marks) {
  const warning = node("section", `${prefix}-placeholder`);
  warning.append(node("strong", null, "EXPORT BLOCKED"), node("h3", null, data.missingAsset), node("p", null, data.requiredSpec), node("p", null, `Blocker · ${data.blocker}`), node("code", null, "readiness ≤ runtime-pass"));
  if (data.approved) warning.appendChild(node("span", `${prefix}-approval`, "APPROVAL RECORDED · REPLACEMENT STILL REQUIRED"));
  body.appendChild(warning); marks.push(warning);
}

function renderAbstract(body, kind, data, prefix, marks) {
  if (kind === "analogy") renderAnalogy(body, data, prefix, marks);
  else if (kind === "black-box") renderBlackBox(body, data, prefix, marks);
  else if (kind === "equation") renderEquation(body, data, prefix, marks);
  else if (kind === "spectrum") renderSpectrum(body, data, prefix, marks);
  else if (kind === "iceberg") renderIceberg(body, data, prefix, marks);
  else if (kind === "versus") renderVersus(body, data, prefix, marks);
  else renderPlaceholder(body, data, prefix, marks);
}

export function mountAbstractComponent(root, context = {}, meta, prefix, config) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  validateAbstractPayload(meta.id, config.kind, params.data);
  const css = `.comp-${meta.id}{position:relative;display:grid;grid-template-rows:auto auto minmax(0,1fr) auto;width:100%;height:100%;min-width:0;min-height:330px;padding:var(--comp-space-5);gap:var(--comp-space-3);border:1px solid var(--comp-line);border-radius:var(--comp-radius-md);background:var(--comp-surface);color:var(--comp-ink);font-family:var(--comp-font-sans);overflow:hidden;container-type:inline-size}.comp-${meta.id} .${prefix}-title{min-width:0;margin:0;font:800 clamp(22px,3vw,42px)/1.05 var(--comp-font-display);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-mapping{display:flex;flex-wrap:wrap;justify-content:space-between;gap:5px 12px;min-width:0;padding:8px 10px;border-left:4px solid var(--comp-accent);background:var(--comp-surface-strong);color:var(--comp-muted);font:650 11px/1.35 var(--comp-font-mono);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-body{display:flex;flex-wrap:wrap;min-width:0;min-height:0;align-items:center;justify-content:center;gap:10px;overflow:hidden}.comp-${meta.id} .${prefix}-source{position:relative;z-index:2;min-width:0;color:var(--comp-ink);font:500 13px/1.4 var(--comp-font-mono);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-object,.comp-${meta.id} .${prefix}-ports{flex:1 1 110px;min-width:0;padding:12px;border:1px solid var(--comp-line);border-radius:var(--comp-radius-sm);background:var(--comp-surface-strong);text-align:center;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-object strong{display:block;margin-top:8px;font:800 clamp(17px,2.3vw,34px) var(--comp-font-display);overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-relation{padding:8px 12px;border:2px solid var(--comp-accent);border-radius:999px;color:var(--comp-accent);font-weight:800;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-ports h3{margin:0 0 10px}.comp-${meta.id} .${prefix}-list{margin:0;padding-left:16px;text-align:left}.comp-${meta.id} .${prefix}-black-box{flex:1 1 130px;min-width:0;padding:34px 14px;border:3px solid var(--comp-accent);background:var(--comp-canvas);box-shadow:inset 0 0 0 8px var(--comp-surface-strong);font:800 18px var(--comp-font-display);text-align:center;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-equation{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap}.comp-${meta.id} .${prefix}-term,.comp-${meta.id} .${prefix}-result{padding:14px;border:1px solid var(--comp-line);border-radius:10px;background:var(--comp-surface-strong);font:800 clamp(16px,2.3vw,30px) var(--comp-font-display)}.comp-${meta.id} .${prefix}-result{border:3px solid var(--comp-accent)}.comp-${meta.id} .${prefix}-operator{color:var(--comp-accent);font:800 24px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-spectrum{position:relative;width:78%;height:150px;border-top:4px solid var(--comp-line-strong);margin-top:65px}.comp-${meta.id} .${prefix}-left,.comp-${meta.id} .${prefix}-right{position:absolute;top:62px;font-weight:700}.comp-${meta.id} .${prefix}-left{left:0}.comp-${meta.id} .${prefix}-right{right:0}.comp-${meta.id} .${prefix}-point{position:absolute;top:-18px;transform:translateX(-50%);padding-top:34px;text-align:center}.comp-${meta.id} .${prefix}-point:before{content:"";position:absolute;top:6px;left:50%;width:16px;height:16px;border-radius:50%;background:var(--comp-accent);transform:translateX(-50%)}.comp-${meta.id} .${prefix}-iceberg{display:flex;flex-direction:column;width:min(720px,90%);height:100%;min-height:0;clip-path:polygon(18% 0,82% 0,100% 100%,0 100%)}.comp-${meta.id} .${prefix}-visible,.comp-${meta.id} .${prefix}-hidden{display:grid;align-content:center;padding:8px 20%;min-height:0}.comp-${meta.id} .${prefix}-visible{background:var(--comp-surface-strong);border-bottom:5px solid var(--comp-accent)}.comp-${meta.id} .${prefix}-hidden{background:color-mix(in srgb,var(--comp-accent) 28%,var(--comp-canvas))}.comp-${meta.id} .${prefix}-visible h3,.comp-${meta.id} .${prefix}-hidden h3{margin:0 0 4px}.comp-${meta.id} .${prefix}-versus{width:100%;border-collapse:collapse}.comp-${meta.id} .${prefix}-versus th,.comp-${meta.id} .${prefix}-versus td{padding:10px;border:1px solid var(--comp-line);text-align:left;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-versus thead th{border-bottom:3px solid var(--comp-accent)}.comp-${meta.id} .${prefix}-placeholder{width:min(720px,95%);padding:20px;border:4px dashed var(--comp-accent);background:var(--comp-canvas);text-align:center;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-placeholder>strong{color:var(--comp-accent);font:900 12px var(--comp-font-mono);letter-spacing:.15em}.comp-${meta.id} .${prefix}-placeholder h3{margin:12px 0;font:800 clamp(20px,3vw,38px) var(--comp-font-display)}.comp-${meta.id} .${prefix}-placeholder p{margin:7px 0;color:var(--comp-muted)}.comp-${meta.id} .${prefix}-placeholder code{display:block;margin-top:14px;color:var(--comp-accent)}.comp-${meta.id} .${prefix}-approval{display:block;margin-top:10px;font:700 11px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-body:has(.${prefix}-object){display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)}.comp-${meta.id} .${prefix}-body:has(.${prefix}-ports){display:grid;grid-template-columns:minmax(0,1fr) minmax(0,.8fr) minmax(0,1fr)}@container (max-width:520px){.comp-${meta.id} .${prefix}-body:has(.${prefix}-object){grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:minmax(0,1fr) auto}.comp-${meta.id} .${prefix}-body:has(.${prefix}-object) .${prefix}-relation{grid-column:1/-1;grid-row:2;justify-self:center}.comp-${meta.id} .${prefix}-object strong{font-size:16px}}@container (max-width:380px){.comp-${meta.id} .${prefix}-mapping{padding:4px 7px;font-size:8px}.comp-${meta.id} .${prefix}-object,.comp-${meta.id} .${prefix}-ports{padding:6px}.comp-${meta.id} .${prefix}-object strong{font-size:14px}.comp-${meta.id} .${prefix}-relation{padding:5px 7px;font-size:9px}.comp-${meta.id} .${prefix}-black-box{padding:18px 8px;font-size:12px;box-shadow:inset 0 0 0 4px var(--comp-surface-strong)}.comp-${meta.id} .${prefix}-placeholder{padding:7px}.comp-${meta.id} .${prefix}-placeholder>strong{font-size:9px}.comp-${meta.id} .${prefix}-placeholder h3{margin:4px 0;font-size:15px}.comp-${meta.id} .${prefix}-placeholder p{margin:3px 0;font-size:9px}.comp-${meta.id} .${prefix}-placeholder code{margin-top:5px;font-size:9px}.comp-${meta.id} .${prefix}-visible,.comp-${meta.id} .${prefix}-hidden{padding:4px 18%;font-size:9px}.comp-${meta.id} .${prefix}-visible h3,.comp-${meta.id} .${prefix}-hidden h3{font-size:10px}}`;
  const { element, gsap } = createFidelityHost(root, context, meta, prefix, css);
  if (config.kind === "placeholder") {
    element.dataset.readiness = "runtime-pass"; element.dataset.exportBlocked = "true"; element.dataset.requiresReplacement = "true";
  }
  element.appendChild(node("h2", `${prefix}-title`, params.title));
  element.appendChild(mappingStrip(params.data, prefix));
  const body = node("div", `${prefix}-body`), marks = []; renderAbstract(body, config.kind, params.data, prefix, marks); element.appendChild(body);
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
