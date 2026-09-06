import {
  createFidelityHost,
  destroyFidelity,
  deterministicId,
  htmlNode,
  normalizeLocalFrame,
  svgNode,
  validateParams,
} from "./fidelity-runtime.js";

const W = 1000;
const H = 560;
const PAD = { left: 92, right: 54, top: 56, bottom: 78 };
const finite = (value) => typeof value === "number" && Number.isFinite(value);
const nonEmpty = (value) => typeof value === "string" && value.trim().length > 0;
const fail = (id, message) => { throw new Error(`[${id}] ${message}`); };
const valuesOf = (data) => data.map((item) => item.value).filter(finite);

function requireArray(id, value, label, max = 20) {
  if (!Array.isArray(value)) fail(id, `${label} must be an array`);
  if (value.length > max) fail(id, `${label} may contain at most ${max} items`);
  return value;
}

function validateSeries(id, data, max = 20) {
  requireArray(id, data, "data", max);
  data.forEach((item, index) => {
    if (!item || !nonEmpty(item.label)) fail(id, `data[${index}].label is required`);
    if (item.value !== null && !finite(item.value)) fail(id, `data[${index}].value must be finite or null`);
  });
}

export function validateChartPayload(id, kind, data, params = {}) {
  if (["line", "area", "bar", "horizontal-bar"].includes(kind)) {
    validateSeries(id, data);
  } else if (kind === "multi-line") {
    requireArray(id, data, "data", 3);
    if (!data.length) return;
    data.forEach((series, index) => {
      if (!series || !nonEmpty(series.name)) fail(id, `data[${index}].name is required`);
      validateSeries(id, series.values, 20);
    });
    const length = data[0].values.length;
    if (data.some((series) => series.values.length !== length)) fail(id, "all series must have equal lengths");
  } else if (kind === "stacked-bar") {
    requireArray(id, data, "data", 12);
    data.forEach((item, index) => {
      if (!item || !nonEmpty(item.label)) fail(id, `data[${index}].label is required`);
      requireArray(id, item.segments, `data[${index}].segments`, 5);
      item.segments.forEach((segment, segmentIndex) => {
        if (!segment || !nonEmpty(segment.name) || !finite(segment.value) || segment.value < 0) fail(id, `data[${index}].segments[${segmentIndex}] is invalid`);
      });
    });
  } else if (kind === "donut") {
    validateSeries(id, data, 4);
    if (data.some((item) => item.value === null || item.value < 0)) fail(id, "donut values must be non-negative");
    const sum = valuesOf(data).reduce((total, value) => total + value, 0);
    if (!finite(params.total) || params.total <= 0 || Math.abs(sum - params.total) > 1e-6) fail(id, "donut values must sum exactly to total");
    data.forEach((item, index) => {
      if (item.percent !== undefined && (!finite(item.percent) || Math.abs(item.percent - item.value / params.total * 100) > .1)) fail(id, `data[${index}].percent is inconsistent with total`);
    });
  } else if (kind === "scatter") {
    requireArray(id, data, "data", 30);
    data.forEach((item, index) => {
      if (!item || !nonEmpty(item.label) || !finite(item.x) || !finite(item.y) || (item.size !== undefined && (!finite(item.size) || item.size <= 0))) fail(id, `data[${index}] is invalid`);
    });
  } else if (kind === "heatmap") {
    if (!data || !Array.isArray(data.rows) || !Array.isArray(data.columns) || !Array.isArray(data.values)) fail(id, "heatmap data must include rows, columns, and values");
    if (data.values.length !== data.rows.length || data.values.some((row) => !Array.isArray(row) || row.length !== data.columns.length)) fail(id, "heatmap matrix dimensions must match labels");
    if (data.values.flat().some((value) => value !== null && !finite(value))) fail(id, "heatmap cells must be finite or null");
  } else if (kind === "gauge") {
    if (!data || !finite(data.value) || !finite(data.min) || !finite(data.max) || data.max <= data.min || data.value < data.min || data.value > data.max) fail(id, "gauge requires min <= value <= max and max > min");
    if (data.thresholds !== undefined) {
      requireArray(id, data.thresholds, "data.thresholds", 4);
      if (data.thresholds.some((value) => !finite(value) || value < data.min || value > data.max)) fail(id, "gauge thresholds must stay within the domain");
    }
  } else if (kind === "sparkline") {
    requireArray(id, data, "data", 4);
    data.forEach((metric, index) => {
      if (!metric || !nonEmpty(metric.label) || !nonEmpty(metric.valueLabel)) fail(id, `data[${index}] requires label and valueLabel`);
      requireArray(id, metric.values, `data[${index}].values`, 20);
      if (metric.values.some((value) => value !== null && !finite(value))) fail(id, `data[${index}].values must be finite or null`);
    });
  } else if (kind === "sankey") {
    if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.links)) fail(id, "sankey data must include nodes and links");
    const nodes = new Map();
    data.nodes.forEach((node, index) => {
      if (!node || !nonEmpty(node.id) || !nonEmpty(node.label) || !["source", "middle", "sink"].includes(node.stage) || nodes.has(node.id)) fail(id, `data.nodes[${index}] is invalid`);
      nodes.set(node.id, node);
    });
    const incoming = new Map(), outgoing = new Map();
    data.links.forEach((link, index) => {
      if (!link || !nodes.has(link.source) || !nodes.has(link.target) || !finite(link.value) || link.value <= 0) fail(id, `data.links[${index}] is invalid`);
      outgoing.set(link.source, (outgoing.get(link.source) ?? 0) + link.value);
      incoming.set(link.target, (incoming.get(link.target) ?? 0) + link.value);
    });
    for (const node of nodes.values()) {
      if (node.stage === "middle" && Math.abs((incoming.get(node.id) ?? 0) - (outgoing.get(node.id) ?? 0)) > 1e-6) fail(id, `flow is not conserved at ${node.id}`);
      if (node.stage === "source" && (incoming.get(node.id) ?? 0) !== 0) fail(id, `source ${node.id} has incoming flow`);
      if (node.stage === "sink" && (outgoing.get(node.id) ?? 0) !== 0) fail(id, `sink ${node.id} has outgoing flow`);
    }
  } else fail(id, `unknown chart kind ${kind}`);
  return data;
}

function domain(values, explicitMin, explicitMax) {
  const finiteValues = values.filter(finite);
  let min = finite(explicitMin) ? explicitMin : Math.min(0, ...finiteValues);
  let max = finite(explicitMax) ? explicitMax : Math.max(0, ...finiteValues);
  if (min === max) { min -= 1; max += 1; }
  return { min, max };
}

function scaleX(index, count) {
  return PAD.left + (count <= 1 ? .5 : index / (count - 1)) * (W - PAD.left - PAD.right);
}
function scaleY(value, range) {
  return PAD.top + (range.max - value) / (range.max - range.min) * (H - PAD.top - PAD.bottom);
}
function pathFor(items, range) {
  let path = "";
  let open = false;
  items.forEach((item, index) => {
    if (!finite(item.value)) { open = false; return; }
    path += `${open ? " L" : " M"} ${scaleX(index, items.length)} ${scaleY(item.value, range)}`;
    open = true;
  });
  return path.trim();
}
function contiguousRuns(items) {
  const runs = [];
  let current = [];
  items.forEach((item, index) => {
    if (finite(item.value)) current.push({ item, index });
    else if (current.length) { runs.push(current); current = []; }
  });
  if (current.length) runs.push(current);
  return runs;
}
function addText(svg, text, x, y, className, anchor = "middle") {
  const node = svgNode("text", { x, y, "text-anchor": anchor, class: className });
  node.textContent = text;
  svg.appendChild(node);
  return node;
}
function formatValue(value, format = "number") {
  if (!finite(value)) return "—";
  if (format === "percent") return `${value.toLocaleString(undefined, { maximumFractionDigits: 1 })}%`;
  if (format === "compact") return Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(value);
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}
function baseAxes(svg, labels, range, prefix) {
  const parts = [];
  for (let index = 0; index <= 4; index += 1) {
    const value = range.min + (range.max - range.min) * index / 4;
    const y = scaleY(value, range);
    parts.push(svgNode("line", { x1: PAD.left, x2: W - PAD.right, y1: y, y2: y, class: `${prefix}-grid` }));
    addText(svg, formatValue(value), PAD.left - 14, y + 5, `${prefix}-axis`, "end");
  }
  labels.forEach((label, index) => addText(svg, label, scaleX(index, labels.length), H - PAD.bottom + 30, `${prefix}-axis`));
  parts.forEach((part) => svg.appendChild(part));
}

function drawStandard(svg, kind, data, params, prefix, instanceId) {
  const marks = [];
  if (["line", "area"].includes(kind)) {
    const range = domain(valuesOf(data), params.min, params.max);
    baseAxes(svg, data.map((item) => item.label), range, prefix);
    const d = pathFor(data, range);
    if (kind === "area" && d) {
      const gradientId = deterministicId(instanceId, "area-fill");
      const defs = svgNode("defs"), gradient = svgNode("linearGradient", { id: gradientId, x1: 0, x2: 0, y1: 0, y2: 1 });
      gradient.append(svgNode("stop", { offset: "0%", "stop-color": "var(--comp-accent)", "stop-opacity": .42 }), svgNode("stop", { offset: "100%", "stop-color": "var(--comp-accent)", "stop-opacity": 0 }));
      defs.appendChild(gradient); svg.appendChild(defs);
      contiguousRuns(data).filter((run) => run.length >= 2).forEach((run) => {
        const runPath = run.map(({ item, index }, runIndex) => `${runIndex === 0 ? "M" : "L"} ${scaleX(index, data.length)} ${scaleY(item.value, range)}`).join(" ");
        const first = run[0].index, last = run[run.length - 1].index;
        const fill = svgNode("path", { d: `${runPath} L ${scaleX(last, data.length)} ${scaleY(range.min, range)} L ${scaleX(first, data.length)} ${scaleY(range.min, range)} Z`, fill: `url(#${gradientId})`, class: `${prefix}-area` });
        svg.appendChild(fill); marks.push(fill);
      });
    }
    const line = svgNode("path", { d, fill: "none", class: `${prefix}-line` }); svg.appendChild(line); marks.push(line);
  } else if (kind === "multi-line") {
    const all = data.flatMap((series) => valuesOf(series.values)), range = domain(all, params.min, params.max);
    baseAxes(svg, data[0]?.values.map((item) => item.label) ?? [], range, prefix);
    data.forEach((series, index) => {
      const line = svgNode("path", { d: pathFor(series.values, range), fill: "none", class: `${prefix}-line ${prefix}-series-${index + 1}` });
      svg.appendChild(line); marks.push(line);
      addText(svg, series.name, W - PAD.right, PAD.top + 22 * index, `${prefix}-legend`, "end");
    });
  } else if (["bar", "horizontal-bar"].includes(kind)) {
    const range = domain(valuesOf(data), params.min, params.max), zero = scaleY(0, range);
    if (kind === "bar") {
      baseAxes(svg, data.map((item) => item.label), range, prefix);
      const band = (W - PAD.left - PAD.right) / Math.max(1, data.length);
      data.forEach((item, index) => {
        if (!finite(item.value)) return;
        const y = scaleY(item.value, range), rect = svgNode("rect", { x: PAD.left + band * index + band * .18, y: Math.min(y, zero), width: band * .64, height: Math.max(1, Math.abs(zero - y)), class: `${prefix}-bar` });
        svg.appendChild(rect); marks.push(rect);
      });
    } else {
      const rangeX = range, innerW = W - PAD.left - PAD.right, row = (H - PAD.top - PAD.bottom) / Math.max(1, data.length);
      data.forEach((item, index) => {
        const lines = item.label.length > 18 ? [item.label.slice(0, 18), item.label.slice(18)] : [item.label];
        lines.forEach((line, lineIndex) => addText(svg, line, PAD.left, PAD.top + row * (index + .5) + (lineIndex - (lines.length - 1) / 2) * 20, `${prefix}-label`, "start"));
        if (!finite(item.value)) return;
        const ratio = (item.value - rangeX.min) / (rangeX.max - rangeX.min), barX = PAD.left + 260, barWidth = Math.max(1, ratio * (innerW - 260)), rect = svgNode("rect", { x: barX, y: PAD.top + row * index + row * .18, width: barWidth, height: row * .5, class: `${prefix}-bar` });
        svg.appendChild(rect); marks.push(rect);
        addText(svg, formatValue(item.value, params.format), W - PAD.right, PAD.top + row * (index + .14), `${prefix}-value`, "end");
      });
    }
  }
  return marks;
}

function drawSpecial(svg, kind, data, params, prefix, instanceId) {
  const marks = [];
  if (kind === "stacked-bar") {
    const totals = data.map((item) => item.segments.reduce((sum, segment) => sum + segment.value, 0)), max = Math.max(1, ...totals), band = (W - PAD.left - PAD.right) / Math.max(1, data.length);
    data.forEach((item, index) => {
      let cursor = H - PAD.bottom;
      item.segments.forEach((segment, segmentIndex) => {
        const height = segment.value / max * (H - PAD.top - PAD.bottom);
        const rect = svgNode("rect", { x: PAD.left + band * index + band * .2, y: cursor - height, width: band * .6, height, class: `${prefix}-bar ${prefix}-series-${segmentIndex + 1}` });
        svg.appendChild(rect); marks.push(rect); cursor -= height;
      });
      addText(svg, item.label, PAD.left + band * (index + .5), H - PAD.bottom + 30, `${prefix}-axis`);
    });
  } else if (kind === "donut") {
    const radius = 165, circumference = 2 * Math.PI * radius, cx = 360, cy = 280; let offset = 0;
    const groupId = deterministicId(instanceId, "donut");
    const group = svgNode("g", { id: groupId, transform: `rotate(-90 ${cx} ${cy})` });
    data.forEach((item, index) => {
      const length = item.value / params.total * circumference;
      const circle = svgNode("circle", { cx, cy, r: radius, fill: "none", "stroke-dasharray": `${length} ${circumference - length}`, "stroke-dashoffset": -offset, class: `${prefix}-donut ${prefix}-series-${index + 1}` });
      group.appendChild(circle); marks.push(circle); offset += length;
      addText(svg, `${item.label} ${formatValue(item.value / params.total * 100, "percent")}`, 650, 190 + index * 54, `${prefix}-label`, "start");
    });
    svg.appendChild(group);
  } else if (kind === "scatter") {
    const xRange = domain(data.map((item) => item.x), params.xMin, params.xMax), yRange = domain(data.map((item) => item.y), params.yMin, params.yMax);
    data.forEach((item) => {
      const cx = PAD.left + (item.x - xRange.min) / (xRange.max - xRange.min) * (W - PAD.left - PAD.right), cy = scaleY(item.y, yRange);
      const circle = svgNode("circle", { cx, cy, r: Math.max(7, Math.min(34, item.size ?? 12)), class: `${prefix}-point` });
      svg.appendChild(circle); marks.push(circle); addText(svg, item.label, cx + Math.max(7, Math.min(34, item.size ?? 12)) + 8, cy + 5, `${prefix}-point-label`, "start");
    });
  } else if (kind === "heatmap") {
    const cellW = (W - PAD.left - PAD.right) / Math.max(1, data.columns.length), cellH = (H - PAD.top - PAD.bottom) / Math.max(1, data.rows.length);
    const vals = data.values.flat().filter(finite), range = domain(vals, params.min, params.max);
    data.rows.forEach((label, rowIndex) => {
      addText(svg, label, PAD.left - 12, PAD.top + cellH * (rowIndex + .58), `${prefix}-axis`, "end");
      data.columns.forEach((column, columnIndex) => {
        if (rowIndex === 0) addText(svg, column, PAD.left + cellW * (columnIndex + .5), H - PAD.bottom + 30, `${prefix}-axis`);
        const value = data.values[rowIndex][columnIndex], ratio = finite(value) ? (value - range.min) / (range.max - range.min) : 0;
        const rect = svgNode("rect", { x: PAD.left + cellW * columnIndex + 2, y: PAD.top + cellH * rowIndex + 2, width: cellW - 4, height: cellH - 4, class: `${prefix}-heat`, opacity: finite(value) ? (.12 + ratio * .88).toFixed(3) : .03 });
        svg.appendChild(rect); marks.push(rect);
      });
    });
  } else if (kind === "gauge") {
    const cx = 350, cy = 330, radius = 180, circumference = 220 / 360 * 2 * Math.PI * radius, ratio = (data.value - data.min) / (data.max - data.min);
    const base = svgNode("path", { d: `M 180 440 A ${radius} ${radius} 0 1 1 520 440`, class: `${prefix}-gauge-track` });
    const value = svgNode("path", { d: base.getAttribute("d"), class: `${prefix}-gauge`, "stroke-dasharray": `${ratio * circumference} ${circumference}` });
    svg.append(base, value); marks.push(value);
    addText(svg, formatValue(data.value, params.format), cx, cy + 20, `${prefix}-gauge-value`);
    addText(svg, params.label, cx, cy + 66, `${prefix}-label`);
  } else if (kind === "sparkline") {
    const columns = data.length <= 2 ? 2 : data.length, cardW = (W - PAD.left - PAD.right) / Math.max(1, columns);
    data.forEach((metric, index) => {
      const x0 = PAD.left + cardW * index, range = domain(metric.values, undefined, undefined);
      addText(svg, metric.label, x0 + 10, 130, `${prefix}-label`, "start"); addText(svg, metric.valueLabel, x0 + 10, 185, `${prefix}-metric`, "start");
      const points = metric.values.map((value, pointIndex) => ({ label: String(pointIndex), value }));
      const raw = pathFor(points, range), transformed = raw.replaceAll(/([ML])\s+([\d.]+)\s+([\d.]+)/g, (_m, op, x, y) => `${op} ${x0 + 10 + (Number(x) - PAD.left) / (W - PAD.left - PAD.right) * (cardW - 20)} ${250 + (Number(y) - PAD.top) / (H - PAD.top - PAD.bottom) * 120}`);
      const path = svgNode("path", { d: transformed, fill: "none", class: `${prefix}-line` }); svg.appendChild(path); marks.push(path);
    });
  } else if (kind === "sankey") {
    const stages = ["source", "middle", "sink"], positions = new Map(), stageX = { source: 120, middle: 500, sink: 880 };
    stages.forEach((stage) => {
      const nodes = data.nodes.filter((node) => node.stage === stage), gap = (H - PAD.top - PAD.bottom) / Math.max(1, nodes.length);
      nodes.forEach((node, index) => positions.set(node.id, { x: stageX[stage], y: PAD.top + gap * (index + .5), node }));
    });
    const maxFlow = Math.max(...data.links.map((link) => link.value));
    data.links.forEach((link) => {
      const a = positions.get(link.source), b = positions.get(link.target), mid = (a.x + b.x) / 2;
      const path = svgNode("path", { d: `M ${a.x} ${a.y} C ${mid} ${a.y} ${mid} ${b.y} ${b.x} ${b.y}`, fill: "none", class: `${prefix}-flow`, "stroke-width": Math.max(3, link.value / maxFlow * 34) });
      svg.appendChild(path); marks.push(path);
    });
    positions.forEach(({ x, y, node }) => {
      svg.appendChild(svgNode("rect", { x: x - 9, y: y - 34, width: 18, height: 68, class: `${prefix}-node` }));
      if (node.stage === "source") addText(svg, node.label, x - 18, y + 5, `${prefix}-label`, "end");
      else if (node.stage === "middle") addText(svg, node.label, x, y - 46, `${prefix}-label`, "middle");
      else addText(svg, node.label, x + 18, y + 5, `${prefix}-label`, "start");
    });
  }
  return marks;
}

export function mountChartComponent(root, context = {}, meta, prefix, config) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  validateChartPayload(meta.id, config.kind, params.data, params);
  const css = `.comp-${meta.id}{position:relative;display:grid;grid-template-rows:auto 1fr auto;width:100%;height:100%;min-height:280px;padding:var(--comp-space-5);border:1px solid var(--comp-line);border-radius:var(--comp-radius-md);background:var(--comp-surface);color:var(--comp-ink);font-family:var(--comp-font-sans);overflow:hidden}.comp-${meta.id} .${prefix}-head{display:flex;justify-content:space-between;gap:var(--comp-space-4);align-items:end}.comp-${meta.id} .${prefix}-title{margin:0;font:800 clamp(22px,3vw,42px)/1.05 var(--comp-font-display);text-wrap:balance}.comp-${meta.id} .${prefix}-empty{display:grid;place-items:center;color:var(--comp-muted);font:600 18px/1.4 var(--comp-font-sans)}.comp-${meta.id} .${prefix}-plot{width:100%;height:100%;min-height:180px}.comp-${meta.id} .${prefix}-source{color:var(--comp-muted);font:500 14px/1.4 var(--comp-font-mono)}.comp-${meta.id} .${prefix}-grid{stroke:var(--comp-line);stroke-width:1}.comp-${meta.id} .${prefix}-axis{fill:var(--comp-muted);font:500 14px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-label,.comp-${meta.id} .${prefix}-legend{fill:var(--comp-ink);font:650 17px var(--comp-font-sans)}.comp-${meta.id} .${prefix}-value,.comp-${meta.id} .${prefix}-metric{fill:var(--comp-ink);font:800 24px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-line{stroke:var(--comp-accent);stroke-width:4;stroke-linejoin:round;stroke-linecap:round}.comp-${meta.id} .${prefix}-series-2{stroke:var(--comp-muted)}.comp-${meta.id} .${prefix}-series-3{stroke:var(--comp-line-strong)}.comp-${meta.id} .${prefix}-bar,.comp-${meta.id} .${prefix}-node{fill:var(--comp-accent);transform-box:fill-box;transform-origin:center bottom}.comp-${meta.id} .${prefix}-bar.${prefix}-series-2{fill:var(--comp-muted)}.comp-${meta.id} .${prefix}-bar.${prefix}-series-3{fill:var(--comp-line-strong)}.comp-${meta.id} .${prefix}-area{opacity:.8}.comp-${meta.id} .${prefix}-donut{fill:none;stroke:var(--comp-accent);stroke-width:42}.comp-${meta.id} .${prefix}-donut.${prefix}-series-2{stroke:var(--comp-muted)}.comp-${meta.id} .${prefix}-donut.${prefix}-series-3{stroke:var(--comp-line-strong)}.comp-${meta.id} .${prefix}-point{fill:var(--comp-accent);stroke:var(--comp-canvas);stroke-width:2}.comp-${meta.id} .${prefix}-point-label{fill:var(--comp-ink);font:800 13px var(--comp-font-mono);paint-order:stroke;stroke:var(--comp-canvas);stroke-width:4px;stroke-linejoin:round}.comp-${meta.id} .${prefix}-heat{fill:var(--comp-accent)}.comp-${meta.id} .${prefix}-gauge-track{fill:none;stroke:var(--comp-line);stroke-width:28;stroke-linecap:round}.comp-${meta.id} .${prefix}-gauge{fill:none;stroke:var(--comp-accent);stroke-width:28;stroke-linecap:round}.comp-${meta.id} .${prefix}-gauge-value{fill:var(--comp-accent);font:900 70px var(--comp-font-mono)}.comp-${meta.id} .${prefix}-flow{stroke:var(--comp-accent);opacity:.28}`;
  const { element, gsap } = createFidelityHost(root, context, meta, prefix, css);
  const head = htmlNode("header", `${prefix}-head`), title = htmlNode("h2", `${prefix}-title`, params.title);
  head.appendChild(title); element.appendChild(head);
  const empty = Array.isArray(params.data) ? params.data.length === 0 : config.kind === "heatmap" ? params.data.rows.length === 0 : config.kind === "sankey" ? params.data.nodes.length === 0 : false;
  const plot = empty ? htmlNode("div", `${prefix}-empty`, params.emptyLabel) : svgNode("svg", { viewBox: `0 0 ${W} ${H}`, class: `${prefix}-plot`, role: "img", "aria-label": params.title });
  element.appendChild(plot);
  const source = htmlNode("footer", `${prefix}-source`, params.sourceNote); element.appendChild(source);
  const marks = empty ? [] : ["line", "area", "multi-line", "bar", "horizontal-bar"].includes(config.kind)
    ? drawStandard(plot, config.kind, params.data, params, prefix, context.instanceId)
    : drawSpecial(plot, config.kind, params.data, params, prefix, context.instanceId);
  const state = { progress: 0 };
  const render = () => {
    const progress = Math.max(.001, state.progress);
    marks.forEach((mark) => {
      const tag = mark.tagName.toLowerCase();
      if (tag === "rect") mark.style.transform = config.kind === "horizontal-bar" ? `scaleX(${progress})` : `scaleY(${progress})`;
      else mark.style.opacity = String(progress);
    });
  };
  const enter = gsap.timeline({ paused: true }).fromTo(element, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3, ease: "power2.out" });
  const explain = gsap.timeline({ paused: true }).to(state, { progress: 1, duration: 1.2, ease: "power2.inOut", onUpdate: render });
  const emphasize = gsap.timeline({ paused: true }).to(element, { scale: 1.012, duration: .22, ease: "power2.out" }).to(element, { scale: 1, duration: .24 });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, y: -10, duration: .35, ease: "power2.in" });
  const segments = { enter, explain, emphasize, exit };
  render();
  return {
    segments,
    seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); },
    destroy() { destroyFidelity(element, segments); },
  };
}
