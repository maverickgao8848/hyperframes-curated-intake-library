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
  return new Set(ids);
};
const strings = (id, value, label, min = 1, max = 6) => {
  list(id, value, label, min, max).forEach((item, index) => { if (!text(item)) fail(id, `${label}[${index}] must be text`); });
  return value;
};

export function validateThinkingPayload(id, kind, data) {
  if (!data || typeof data !== "object" || Array.isArray(data)) fail(id, "data must be an object");
  if (kind === "compare-table") {
    const columns = list(id, data.columns, "data.columns", 2, 5), columnIds = unique(id, columns, "data.columns");
    columns.forEach((column, index) => { if (!text(column.label)) fail(id, `data.columns[${index}].label is required`); });
    const rows = list(id, data.rows, "data.rows", 1, 8); unique(id, rows, "data.rows");
    rows.forEach((row, index) => {
      if (!text(row.label) || !row.values || typeof row.values !== "object" || Array.isArray(row.values)) fail(id, `data.rows[${index}] requires label and values`);
      const keys = Object.keys(row.values);
      if (keys.length !== columns.length || keys.some((key) => !columnIds.has(key))) fail(id, `data.rows[${index}] must provide every declared column exactly once`);
      if (Object.values(row.values).some((value) => !["string", "number", "boolean"].includes(typeof value))) fail(id, `data.rows[${index}] contains an unsupported value`);
    });
    if (data.recommendedColumn !== undefined && !columnIds.has(data.recommendedColumn)) fail(id, "recommendedColumn must reference a column");
  } else if (kind === "swot") {
    const fixed = ["strengths", "weaknesses", "opportunities", "threats"];
    if (Object.keys(data).sort().join("|") !== [...fixed].sort().join("|")) fail(id, "SWOT requires exactly strengths, weaknesses, opportunities and threats");
    fixed.forEach((key) => strings(id, data[key], `data.${key}`));
  } else if (kind === "fishbone") {
    if (!text(data.problem)) fail(id, "problem is required");
    const categories = list(id, data.categories, "data.categories", 2, 6); unique(id, categories, "data.categories");
    categories.forEach((category, index) => {
      if (!text(category.label)) fail(id, `data.categories[${index}].label is required`);
      strings(id, category.causes, `data.categories[${index}].causes`, 1, 5);
    });
  } else if (kind === "timeline-row") {
    const events = list(id, data.events, "data.events", 2, 8); unique(id, events, "data.events");
    events.forEach((event, index) => {
      if (!text(event.label) || !text(event.date) || !finite(event.position) || event.position < 0 || event.position > 1) fail(id, `data.events[${index}] is invalid`);
    });
  } else if (kind === "gantt") {
    const tasks = list(id, data.tasks, "data.tasks", 1, 8), ids = unique(id, tasks, "data.tasks");
    tasks.forEach((task, index) => {
      if (!text(task.label) || !finite(task.start) || !finite(task.end) || task.start < 0 || task.end > 1 || (task.milestone ? task.start !== task.end : task.start >= task.end)) fail(id, `data.tasks[${index}] has an invalid range`);
      (task.dependsOn ?? []).forEach((dependency) => { if (!ids.has(dependency) || dependency === task.id) fail(id, `data.tasks[${index}] has an invalid dependency`); });
    });
    const byId = new Map(tasks.map((task) => [task.id, task]));
    const visiting = new Set(), visited = new Set();
    const visit = (task) => {
      if (visiting.has(task.id)) fail(id, "task dependencies must be acyclic");
      if (visited.has(task.id)) return;
      visiting.add(task.id); (task.dependsOn ?? []).forEach((dependency) => visit(byId.get(dependency))); visiting.delete(task.id); visited.add(task.id);
    };
    tasks.forEach(visit);
  } else if (kind === "kanban") {
    const columns = list(id, data.columns, "data.columns", 2, 5), columnIds = unique(id, columns, "data.columns");
    columns.forEach((column, index) => { if (!text(column.label)) fail(id, `data.columns[${index}].label is required`); });
    const cards = list(id, data.cards, "data.cards", 1, 12); unique(id, cards, "data.cards");
    cards.forEach((card, index) => { if (!text(card.title) || !columnIds.has(card.column)) fail(id, `data.cards[${index}] is invalid`); });
  } else if (kind === "card-grid") {
    const cards = list(id, data.cards, "data.cards", 2, 8); unique(id, cards, "data.cards");
    cards.forEach((card, index) => { if (!text(card.title) || !text(card.body)) fail(id, `data.cards[${index}] requires title and body`); });
    if (cards.filter((card) => card.recommended).length > 1) fail(id, "only one card may be recommended");
  } else fail(id, `unknown thinking kind ${kind}`);
  return data;
}

function cell(tag, className, value) {
  return htmlNode(tag, className, value);
}

function renderCompare(body, data, prefix, marks) {
  const table = cell("table", `${prefix}-table`), head = cell("thead"), headRow = cell("tr");
  headRow.appendChild(cell("th", null, "Dimension"));
  data.columns.forEach((column) => {
    const th = cell("th", column.id === data.recommendedColumn ? `${prefix}-recommended` : "", column.label);
    headRow.appendChild(th);
  });
  head.appendChild(headRow); table.appendChild(head);
  const tbody = cell("tbody");
  data.rows.forEach((row) => {
    const tr = cell("tr"); tr.appendChild(cell("th", null, row.label));
    data.columns.forEach((column) => tr.appendChild(cell("td", column.id === data.recommendedColumn ? `${prefix}-recommended` : "", row.values[column.id])));
    tbody.appendChild(tr); marks.push(tr);
  });
  table.appendChild(tbody); body.appendChild(table);
}

function renderSwot(body, data, prefix, marks) {
  const labels = { strengths: "Strengths", weaknesses: "Weaknesses", opportunities: "Opportunities", threats: "Threats" };
  for (const key of Object.keys(labels)) {
    const panel = cell("section", `${prefix}-quadrant ${prefix}-${key}`), heading = cell("h3", null, labels[key]), ul = cell("ul");
    data[key].forEach((item) => ul.appendChild(cell("li", null, item)));
    panel.append(heading, ul); body.appendChild(panel); marks.push(panel);
  }
}

function renderFishbone(body, data, prefix, marks) {
  const causes = cell("div", `${prefix}-bones`);
  data.categories.forEach((category, index) => {
    const branch = cell("section", `${prefix}-bone ${index % 2 ? `${prefix}-lower` : `${prefix}-upper`}`), heading = cell("h3", null, category.label), ul = cell("ul");
    category.causes.forEach((cause) => ul.appendChild(cell("li", null, cause)));
    branch.append(heading, ul); causes.appendChild(branch); marks.push(branch);
  });
  const problem = cell("div", `${prefix}-problem`, data.problem); body.append(causes, problem); marks.push(problem);
}

function renderTimeline(body, data, prefix, marks) {
  const axis = cell("div", `${prefix}-timeline-axis`);
  data.events.forEach((event) => {
    const item = cell("article", `${prefix}-event`); item.style.left = `${14 + event.position * 72}%`;
    item.append(cell("time", null, event.date), cell("strong", null, event.label)); axis.appendChild(item); marks.push(item);
  });
  body.appendChild(axis);
}

function renderGantt(body, data, prefix, marks) {
  const grid = cell("div", `${prefix}-gantt`);
  data.tasks.forEach((task) => {
    const row = cell("div", `${prefix}-gantt-row`), label = cell("strong", null, task.label), track = cell("div", `${prefix}-track`);
    const bar = cell("div", task.milestone ? `${prefix}-milestone` : `${prefix}-bar`);
    bar.style.left = `${task.start * 100}%`;
    if (!task.milestone) bar.style.width = `${(task.end - task.start) * 100}%`;
    if (task.dependsOn?.length) bar.setAttribute("data-depends-on", task.dependsOn.join(" "));
    track.appendChild(bar); row.append(label, track); grid.appendChild(row); marks.push(row);
  });
  body.appendChild(grid);
}

function renderKanban(body, data, prefix, marks) {
  data.columns.forEach((column) => {
    const lane = cell("section", `${prefix}-kanban-column`), heading = cell("h3", null, column.label);
    lane.appendChild(heading);
    data.cards.filter((card) => card.column === column.id).forEach((card) => {
      const item = cell("article", `${prefix}-kanban-card`, card.title); item.dataset.cardId = card.id; lane.appendChild(item); marks.push(item);
    });
    body.appendChild(lane);
  });
}

function renderCards(body, data, prefix, marks) {
  data.cards.forEach((card) => {
    const item = cell("article", `${prefix}-concept-card${card.recommended ? ` ${prefix}-recommended-card` : ""}`);
    item.dataset.cardId = card.id; item.append(cell("h3", null, card.title), cell("p", null, card.body));
    if (card.recommended) item.appendChild(cell("span", `${prefix}-recommendation`, "RECOMMENDED"));
    body.appendChild(item); marks.push(item);
  });
}

function renderThinking(body, kind, data, prefix, marks) {
  if (kind === "compare-table") renderCompare(body, data, prefix, marks);
  else if (kind === "swot") renderSwot(body, data, prefix, marks);
  else if (kind === "fishbone") renderFishbone(body, data, prefix, marks);
  else if (kind === "timeline-row") renderTimeline(body, data, prefix, marks);
  else if (kind === "gantt") renderGantt(body, data, prefix, marks);
  else if (kind === "kanban") renderKanban(body, data, prefix, marks);
  else renderCards(body, data, prefix, marks);
}

export function mountThinkingComponent(root, context = {}, meta, prefix, config) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  validateThinkingPayload(meta.id, config.kind, params.data);
  const css = `.comp-${meta.id}{position:relative;display:grid;grid-template-rows:auto minmax(0,1fr) auto;width:100%;height:100%;min-height:320px;padding:var(--comp-space-5);gap:var(--comp-space-3);border:1px solid var(--comp-line);border-radius:var(--comp-radius-md);background:var(--comp-surface);color:var(--comp-ink);font-family:var(--comp-font-sans);overflow:hidden;container-type:inline-size}.comp-${meta.id} .${prefix}-title{margin:0;font:800 clamp(22px,3vw,42px)/1.05 var(--comp-font-display)}.comp-${meta.id} .${prefix}-body{display:grid;min-height:0;gap:10px;align-content:center}.comp-${meta.id} .${prefix}-source{color:var(--comp-muted);font:500 13px/1.4 var(--comp-font-mono)}.comp-${meta.id} .${prefix}-table{width:100%;border-collapse:collapse;font-size:clamp(12px,1.3vw,18px)}.comp-${meta.id} th,.comp-${meta.id} td{padding:9px;border:1px solid var(--comp-line);text-align:left;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-recommended{outline:2px solid var(--comp-accent);outline-offset:-2px;background:var(--comp-surface-strong)}.comp-${meta.id} .${prefix}-body:has(.${prefix}-quadrant){grid-template-columns:repeat(2,minmax(0,1fr))}.comp-${meta.id} .${prefix}-quadrant,.comp-${meta.id} .${prefix}-concept-card,.comp-${meta.id} .${prefix}-kanban-column{padding:12px;border:1px solid var(--comp-line);border-radius:var(--comp-radius-sm);background:var(--comp-surface-strong)}.comp-${meta.id} h3{margin:0 0 8px;font-size:16px}.comp-${meta.id} ul{margin:0;padding-left:18px}.comp-${meta.id} .${prefix}-strengths,.comp-${meta.id} .${prefix}-opportunities{border-left:4px solid var(--comp-accent)}.comp-${meta.id} .${prefix}-body:has(.${prefix}-bones){grid-template-columns:minmax(0,1fr) auto;align-items:center}.comp-${meta.id} .${prefix}-bones{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;border-bottom:4px solid var(--comp-line-strong)}.comp-${meta.id} .${prefix}-bone{min-width:0;padding:8px;border-left:3px solid var(--comp-accent);background:var(--comp-surface-strong)}.comp-${meta.id} .${prefix}-bone ul{padding-left:13px}.comp-${meta.id} .${prefix}-bone li{font-size:11px;overflow-wrap:anywhere}.comp-${meta.id} .${prefix}-problem{padding:18px;border:3px solid var(--comp-accent);border-radius:999px;font-weight:800}.comp-${meta.id} .${prefix}-timeline-axis{position:relative;height:170px;border-top:3px solid var(--comp-line-strong);margin:60px 8% 0}.comp-${meta.id} .${prefix}-event{position:absolute;top:-18px;width:110px;transform:translateX(-50%);padding-top:30px;text-align:center}.comp-${meta.id} .${prefix}-event:before{content:"";position:absolute;top:8px;left:50%;width:16px;height:16px;border-radius:50%;background:var(--comp-accent);transform:translateX(-50%)}.comp-${meta.id} time{display:block;color:var(--comp-muted);font:600 12px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-gantt{display:grid;gap:8px}.comp-${meta.id} .${prefix}-gantt-row{display:grid;grid-template-columns:minmax(80px,22%) 1fr;align-items:center;gap:12px}.comp-${meta.id} .${prefix}-track{position:relative;height:24px;background:var(--comp-line);border-radius:999px}.comp-${meta.id} .${prefix}-bar{position:absolute;top:4px;height:16px;border-radius:999px;background:var(--comp-accent)}.comp-${meta.id} .${prefix}-milestone{position:absolute;top:5px;width:14px;height:14px;background:var(--comp-accent);transform:translateX(-50%) rotate(45deg)}.comp-${meta.id} .${prefix}-body:has(.${prefix}-kanban-column){grid-template-columns:repeat(auto-fit,minmax(130px,1fr));align-items:stretch}.comp-${meta.id} .${prefix}-kanban-card{padding:10px;margin-top:8px;border:1px solid var(--comp-line);border-radius:8px;background:var(--comp-surface)}.comp-${meta.id} .${prefix}-body:has(.${prefix}-concept-card){grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}.comp-${meta.id} .${prefix}-concept-card{position:relative}.comp-${meta.id} .${prefix}-concept-card p{margin:0;color:var(--comp-muted)}.comp-${meta.id} .${prefix}-recommended-card{outline:3px solid var(--comp-accent);outline-offset:-3px}.comp-${meta.id} .${prefix}-recommendation{display:inline-block;margin-top:10px;color:var(--comp-accent);font:700 11px var(--comp-font-mono)}@container (max-width:440px){.comp-${meta.id} .${prefix}-body:has(.${prefix}-bones){grid-template-columns:1fr;gap:6px}.comp-${meta.id} .${prefix}-problem{justify-self:center;padding:6px 12px;font-size:12px}.comp-${meta.id} .${prefix}-bone{padding:5px}.comp-${meta.id} .${prefix}-bone h3{font-size:12px;margin-bottom:3px}.comp-${meta.id} .${prefix}-bone li{font-size:9px;line-height:1.2}}`;
  const { element, gsap } = createFidelityHost(root, context, meta, prefix, css);
  element.appendChild(cell("h2", `${prefix}-title`, params.title));
  const body = cell("div", `${prefix}-body`), marks = []; renderThinking(body, config.kind, params.data, prefix, marks); element.appendChild(body);
  element.appendChild(cell("footer", `${prefix}-source`, params.sourceNote));
  const state = { progress: 0 };
  const render = () => marks.forEach((mark, index) => { mark.style.opacity = state.progress >= (index + 1) / Math.max(1, marks.length) ? "" : "0"; });
  const segments = createStandardSegments(gsap, element, marks, state, render); render();
  return {
    segments,
    seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); },
    destroy() { destroyFidelity(element, segments); },
  };
}
