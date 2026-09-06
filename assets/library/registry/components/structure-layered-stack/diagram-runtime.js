import {
  createFidelityHost,
  destroyFidelity,
  deterministicId,
  htmlNode,
  normalizeLocalFrame,
  seededUnit,
  svgNode,
  validateParams,
} from "./fidelity-runtime.js";

const W = 1000, H = 600;
const finite = (value) => typeof value === "number" && Number.isFinite(value);
const text = (value) => typeof value === "string" && value.trim().length > 0;
const fail = (id, message) => { throw new Error(`[${id}] ${message}`); };
const array = (id, value, label, min, max) => {
  if (!Array.isArray(value) || value.length < min || value.length > max) fail(id, `${label} requires ${min}-${max} items`);
  return value;
};
const uniqueIds = (id, items, label) => {
  const ids = items.map((item, index) => {
    if (!item || !text(item.id) || !text(item.label)) fail(id, `${label}[${index}] requires id and label`);
    return item.id;
  });
  if (new Set(ids).size !== ids.length) fail(id, `${label} ids must be unique`);
  return new Set(ids);
};

export function validateDiagramPayload(id, kind, data, params = {}) {
  if (!data || typeof data !== "object" || Array.isArray(data)) fail(id, "data must be an object");
  if (["complex", "flow-chart"].includes(kind)) {
    const ids = uniqueIds(id, array(id, data.steps, "data.steps", 2, 8), "data.steps");
    if (data.activeId !== undefined && !ids.has(data.activeId)) fail(id, "activeId must reference a step");
  } else if (["branching", "fork-join"].includes(kind)) {
    if (!data.source || !text(data.source.id) || !text(data.source.label) || !data.target || !text(data.target.id) || !text(data.target.label)) fail(id, "source and target are required");
    const branches = array(id, data.branches, "data.branches", 2, 5);
    branches.forEach((branch, index) => {
      if (!branch || !text(branch.id) || !text(branch.label) || !text(branch.transition)) fail(id, `data.branches[${index}] requires id, label, transition`);
    });
    if (new Set([data.source.id, data.target.id, ...branches.map((branch) => branch.id)]).size !== branches.length + 2) fail(id, "source, branch and target ids must be unique");
    if (kind === "branching" && branches.filter((branch) => branch.recommended).length !== 1) fail(id, "branching requires exactly one recommended branch");
  } else if (["decision-tree", "tree"].includes(kind)) {
    const nodes = array(id, data.nodes, "data.nodes", 2, 12), ids = uniqueIds(id, nodes, "data.nodes");
    nodes.forEach((node) => { if (node.parent !== undefined && !ids.has(node.parent)) fail(id, `unknown parent ${node.parent}`); });
    const roots = nodes.filter((node) => node.parent === undefined);
    if (roots.length !== 1) fail(id, "tree requires exactly one root");
    const byId = new Map(nodes.map((node) => [node.id, node]));
    nodes.forEach((node) => {
      const visited = new Set([node.id]); let cursor = node;
      while (cursor.parent !== undefined) {
        if (visited.has(cursor.parent)) fail(id, "tree parent references must be acyclic");
        visited.add(cursor.parent); cursor = byId.get(cursor.parent);
      }
    });
    if (kind === "decision-tree") {
      const path = array(id, data.recommendedPath, "data.recommendedPath", 1, nodes.length);
      if (path.some((nodeId) => !ids.has(nodeId))) fail(id, "recommendedPath contains unknown node");
      if (path[0] !== roots[0].id) fail(id, "recommendedPath must start at the root");
      for (let index = 1; index < path.length; index += 1) {
        if (nodes.find((node) => node.id === path[index])?.parent !== path[index - 1]) fail(id, "recommendedPath is not parent-connected");
      }
    }
  } else if (["state-machine", "node-graph"].includes(kind)) {
    const nodes = array(id, data.nodes, "data.nodes", 2, 12), ids = uniqueIds(id, nodes, "data.nodes");
    if (kind === "node-graph") {
      if (!Number.isInteger(params.seed) && nodes.some((node) => !finite(node.x) || !finite(node.y))) fail(id, "node-graph requires explicit coordinates or integer seed");
    }
    array(id, data.edges, "data.edges", 1, 20).forEach((edge, index) => {
      if (!edge || !ids.has(edge.source) || !ids.has(edge.target) || !text(edge.label)) fail(id, `data.edges[${index}] is invalid`);
    });
    if (data.activeId !== undefined && !ids.has(data.activeId)) fail(id, "activeId must reference a node");
  } else if (kind === "sequence") {
    const roles = array(id, data.roles, "data.roles", 2, 5), roleIds = uniqueIds(id, roles, "data.roles");
    array(id, data.messages, "data.messages", 1, 12).forEach((message, index) => {
      if (!message || !roleIds.has(message.from) || !roleIds.has(message.to) || message.from === message.to || !text(message.label)) fail(id, `data.messages[${index}] is invalid`);
    });
  } else if (kind === "swimlane") {
    const lanes = array(id, data.lanes, "data.lanes", 2, 5), laneIds = uniqueIds(id, lanes, "data.lanes");
    const steps = array(id, data.steps, "data.steps", 2, 12), stepIds = uniqueIds(id, steps, "data.steps");
    steps.forEach((step, index) => { if (!laneIds.has(step.lane)) fail(id, `data.steps[${index}].lane is unknown`); });
    array(id, data.transitions, "data.transitions", 1, 20).forEach((edge, index) => { if (!stepIds.has(edge.source) || !stepIds.has(edge.target) || !text(edge.label)) fail(id, `data.transitions[${index}] is invalid`); });
  } else if (kind === "loop") {
    const steps = array(id, data.steps, "data.steps", 2, 6); uniqueIds(id, steps, "data.steps");
    if (!text(data.exitCondition)) fail(id, "exitCondition is required");
    if (data.activeIndex !== undefined && (!Number.isInteger(data.activeIndex) || data.activeIndex < 0 || data.activeIndex >= steps.length)) fail(id, "activeIndex must reference a step");
  } else if (["pyramid", "funnel", "concentric", "layered-stack"].includes(kind)) {
    const items = array(id, data.levels ?? data.stages ?? data.rings ?? data.layers, `data.${kind}`, 2, 7);
    uniqueIds(id, items, `data.${kind}`);
    items.forEach((item, index) => {
      if (!item || !text(item.id) || !text(item.label)) fail(id, `${kind}[${index}] requires id and label`);
      if (kind === "funnel" && (!finite(item.value) || item.value < 0)) fail(id, `funnel stage ${index} requires non-negative value`);
    });
    if (kind === "funnel" && Math.max(...items.map((item) => item.value)) <= 0) fail(id, "funnel requires at least one positive value");
  } else if (kind === "spectrum") {
    const items = array(id, data.items, "data.items", 1, 8); uniqueIds(id, items, "data.items");
    items.forEach((item, index) => {
      if (!item || !text(item.id) || !text(item.label) || !finite(item.position) || item.position < 0 || item.position > 1) fail(id, `data.items[${index}] is invalid`);
    });
    if (!text(data.leftLabel) || !text(data.rightLabel)) fail(id, "spectrum endpoint labels are required");
  } else if (["mind-map", "hub-spoke"].includes(kind)) {
    if (!data.center || !text(data.center.id) || !text(data.center.label)) fail(id, "center is required");
    const items = array(id, data.items ?? data.spokes, "radial items", 2, 8), itemIds = uniqueIds(id, items, "radial items");
    if (itemIds.has(data.center.id)) fail(id, "center id must be distinct from radial item ids");
  } else if (kind === "matrix-2x2") {
    if (!data.axes || !text(data.axes.xLow) || !text(data.axes.xHigh) || !text(data.axes.yLow) || !text(data.axes.yHigh)) fail(id, "four axis endpoint labels are required");
    const items = array(id, data.items, "data.items", 1, 12); uniqueIds(id, items, "data.items");
    items.forEach((item, index) => {
      if (!item || !text(item.id) || !text(item.label) || !finite(item.x) || !finite(item.y) || item.x < 0 || item.x > 1 || item.y < 0 || item.y > 1) fail(id, `data.items[${index}] is invalid`);
    });
  } else if (kind === "venn") {
    if (!data.left || !data.right || !text(data.left.label) || !text(data.right.label) || !text(data.intersection)) fail(id, "left, right and intersection labels are required");
  } else if (kind === "grid-map") {
    if (!Number.isInteger(data.rows) || !Number.isInteger(data.columns) || data.rows < 1 || data.rows > 8 || data.columns < 1 || data.columns > 8) fail(id, "grid dimensions must be integers from 1 to 8");
    const cells = array(id, data.cells, "data.cells", 1, data.rows * data.columns); uniqueIds(id, cells, "data.cells");
    const occupied = new Set();
    cells.forEach((cell, index) => {
      if (!cell || !text(cell.id) || !text(cell.label) || !Number.isInteger(cell.row) || !Number.isInteger(cell.column) || cell.row < 0 || cell.row >= data.rows || cell.column < 0 || cell.column >= data.columns) fail(id, `data.cells[${index}] is invalid`);
      const position = `${cell.row}:${cell.column}`; if (occupied.has(position)) fail(id, `data.cells[${index}] duplicates a grid position`); occupied.add(position);
    });
  } else fail(id, `unknown diagram kind ${kind}`);
  return data;
}

function addText(svg, value, x, y, className, anchor = "middle") {
  const node = svgNode("text", { x, y, class: className, "text-anchor": anchor }); node.textContent = value; svg.appendChild(node); return node;
}
function node(svg, item, x, y, prefix, state = "future") {
  const group = svgNode("g", { class: `${prefix}-node ${prefix}-${state}`, "data-node-id": item.id, transform: `translate(${x} ${y})` });
  group.appendChild(svgNode("rect", { x: -72, y: -28, width: 144, height: 56, rx: 10 }));
  const label = svgNode("text", { x: 0, y: 6, "text-anchor": "middle" }); label.textContent = item.label; group.appendChild(label); svg.appendChild(group); return group;
}
function edge(svg, a, b, label, prefix, markerId, active = false) {
  const path = svgNode("path", { d: `M ${a.x} ${a.y} C ${(a.x + b.x) / 2} ${a.y} ${(a.x + b.x) / 2} ${b.y} ${b.x} ${b.y}`, class: `${prefix}-edge${active ? ` ${prefix}-active-edge` : ""}`, "marker-end": `url(#${markerId})` });
  svg.appendChild(path); if (label) addText(svg, label, (a.x + b.x) / 2, (a.y + b.y) / 2 - 9, `${prefix}-edge-label`); return path;
}
function trimmedNodeEdge(a, b) {
  const dx = b.x - a.x, dy = b.y - a.y;
  const boundaryT = () => Math.min(Math.abs(dx) > .001 ? 72 / Math.abs(dx) : Infinity, Math.abs(dy) > .001 ? 28 / Math.abs(dy) : Infinity);
  const t = Math.min(.45, boundaryT());
  return [{ x: a.x + dx * t, y: a.y + dy * t }, { x: b.x - dx * t, y: b.y - dy * t }];
}
function stateFor(id, data, index = 0) {
  if (data.activeId === id) return "current";
  if (data.recommendedPath?.includes(id) || data.branches?.find((item) => item.id === id)?.recommended) return "recommended";
  const activeIndex = data.steps?.findIndex((item) => item.id === data.activeId) ?? -1;
  return activeIndex >= 0 && index < activeIndex ? "past" : "future";
}

function drawLinear(svg, data, prefix, markerId, kind) {
  const steps = data.steps; const marks = [], gap = 780 / Math.max(1, steps.length - 1);
  const positions = steps.map((item, index) => ({ x: 110 + gap * index, y: 300, item }));
  positions.slice(0, -1).forEach((position, index) => marks.push(edge(svg, { x: position.x + 72, y: 300 }, { x: positions[index + 1].x - 72, y: 300 }, steps[index + 1].transition ?? "next", prefix, markerId, stateFor(steps[index + 1].id, data, index + 1) !== "future")));
  positions.forEach((position, index) => marks.push(node(svg, position.item, position.x, position.y, prefix, stateFor(position.item.id, data, index))));
  return marks;
}
function drawBranches(svg, data, prefix, markerId) {
  const marks = [], source = { x: 120, y: 300 }, target = { x: 880, y: 300 };
  marks.push(node(svg, data.source, source.x, source.y, prefix, "past"), node(svg, data.target, target.x, target.y, prefix, "future"));
  data.branches.forEach((branch, index) => {
    const y = 130 + index * 340 / Math.max(1, data.branches.length - 1), state = branch.recommended ? "recommended" : "future";
    marks.push(edge(svg, { x: 192, y: 300 }, { x: 428, y }, branch.transition, prefix, markerId, branch.recommended));
    marks.push(node(svg, branch, 500, y, prefix, state));
    marks.push(edge(svg, { x: 572, y }, { x: 808, y: 300 }, "join", prefix, markerId, branch.recommended));
  });
  return marks;
}
function treePositions(nodes) {
  const byId = new Map(nodes.map((item) => [item.id, item])), levels = new Map();
  const depth = (item) => item.parent ? 1 + depth(byId.get(item.parent)) : 0;
  nodes.forEach((item) => { const d = depth(item); if (!levels.has(d)) levels.set(d, []); levels.get(d).push(item); });
  const positions = new Map();
  levels.forEach((items, d) => items.forEach((item, index) => positions.set(item.id, { x: 120 + d * 760 / Math.max(1, levels.size - 1), y: 100 + (index + 1) * 400 / (items.length + 1) })));
  return positions;
}
function drawTree(svg, data, prefix, markerId) {
  const marks = [], positions = treePositions(data.nodes);
  data.nodes.filter((item) => item.parent).forEach((item) => marks.push(edge(svg, { ...positions.get(item.parent), x: positions.get(item.parent).x + 72 }, { ...positions.get(item.id), x: positions.get(item.id).x - 72 }, item.transition ?? "path", prefix, markerId, data.recommendedPath?.includes(item.id))));
  data.nodes.forEach((item) => { const p = positions.get(item.id); marks.push(node(svg, item, p.x, p.y, prefix, data.recommendedPath?.includes(item.id) ? "recommended" : "future")); });
  return marks;
}
function drawGraph(svg, data, prefix, markerId, seed) {
  const marks = [], positions = new Map();
  data.nodes.forEach((item, index) => positions.set(item.id, {
    x: finite(item.x) ? 80 + item.x * 840 : 100 + seededUnit(seed, index * 2) * 800,
    y: finite(item.y) ? 80 + item.y * 440 : 100 + seededUnit(seed, index * 2 + 1) * 400,
  }));
  data.edges.forEach((item) => { const [a, b] = trimmedNodeEdge(positions.get(item.source), positions.get(item.target)); marks.push(edge(svg, a, b, item.label, prefix, markerId, item.active)); });
  data.nodes.forEach((item, index) => { const p = positions.get(item.id); marks.push(node(svg, item, p.x, p.y, prefix, stateFor(item.id, data, index))); });
  return marks;
}
function drawSequence(svg, data, prefix, markerId) {
  const marks = [], gap = 760 / Math.max(1, data.roles.length - 1), positions = new Map();
  data.roles.forEach((role, index) => { const x = 120 + gap * index; positions.set(role.id, x); marks.push(node(svg, role, x, 80, prefix, "future")); const line = svgNode("line", { x1: x, x2: x, y1: 110, y2: 540, class: `${prefix}-lifeline` }); svg.appendChild(line); marks.push(line); });
  data.messages.forEach((message, index) => { const y = 170 + index * 330 / Math.max(1, data.messages.length - 1); marks.push(edge(svg, { x: positions.get(message.from), y }, { x: positions.get(message.to), y }, message.label, prefix, markerId, message.active)); });
  return marks;
}
function drawSwimlane(svg, data, prefix, markerId) {
  const marks = [], laneH = 480 / data.lanes.length, positions = new Map();
  data.lanes.forEach((lane, index) => { const y = 70 + laneH * index; svg.appendChild(svgNode("rect", { x: 70, y, width: 860, height: laneH - 8, class: `${prefix}-lane` })); addText(svg, lane.label, 85, y + 24, `${prefix}-lane-label`, "start"); });
  data.steps.forEach((step, index) => { const laneIndex = data.lanes.findIndex((lane) => lane.id === step.lane), x = 220 + index * 660 / Math.max(1, data.steps.length - 1), y = 70 + laneH * (laneIndex + .56); positions.set(step.id, { x, y }); marks.push(node(svg, step, x, y, prefix, stateFor(step.id, data, index))); });
  data.transitions.forEach((item) => { const [a, b] = trimmedNodeEdge(positions.get(item.source), positions.get(item.target)); marks.push(edge(svg, a, b, item.label, prefix, markerId, item.active)); });
  return marks;
}
function drawLoop(svg, data, prefix, markerId) {
  const marks = [], center = { x: 460, y: 290 }, radius = 185;
  const positions = data.steps.map((item, index) => ({ item, x: center.x + Math.cos(-Math.PI / 2 + index * Math.PI * 2 / data.steps.length) * radius, y: center.y + Math.sin(-Math.PI / 2 + index * Math.PI * 2 / data.steps.length) * radius }));
  positions.forEach((position, index) => { const next = positions[(index + 1) % positions.length], [a, b] = trimmedNodeEdge(position, next); marks.push(edge(svg, a, b, index === positions.length - 1 ? "repeat" : "next", prefix, markerId, index <= (data.activeIndex ?? 0))); marks.push(node(svg, position.item, position.x, position.y, prefix, index === data.activeIndex ? "current" : "future")); });
  const exitPosition = { x: 110, y: 500 }, exit = { id: "exit", label: data.exitCondition }, [exitA, exitB] = trimmedNodeEdge(positions.at(-1), exitPosition); marks.push(edge(svg, exitA, exitB, "exit", prefix, markerId, true), node(svg, exit, exitPosition.x, exitPosition.y, prefix, "recommended")); return marks;
}
function drawStack(svg, items, prefix, kind) {
  const marks = [], count = items.length;
  items.forEach((item, index) => {
    const ratio = kind === "funnel" && finite(item.value) ? item.value / Math.max(...items.map((entry) => entry.value)) : 1 - index * .11;
    const width = 720 * Math.max(.3, ratio), y = 90 + index * 430 / count, height = 380 / count;
    const path = svgNode("path", { d: `M ${500 - width / 2} ${y} L ${500 + width / 2} ${y} L ${500 + width * .43} ${y + height} L ${500 - width * .43} ${y + height} Z`, class: `${prefix}-layer ${prefix}-series-${index + 1}` }); svg.appendChild(path); marks.push(path); marks.push(addText(svg, item.label, 500, y + height * .62, `${prefix}-layer-label`));
  }); return marks;
}
function drawRadial(svg, center, items, prefix, markerId, concentric = false) {
  const marks = [];
  if (concentric) {
    [...items].reverse().forEach((item, reverseIndex) => { const index = items.length - 1 - reverseIndex, radius = 70 + index * 55; const circle = svgNode("circle", { cx: 500, cy: 300, r: radius, class: `${prefix}-ring ${prefix}-series-${index + 1}` }); svg.appendChild(circle); marks.push(circle); addText(svg, item.label, 500, 305 - radius, `${prefix}-ring-label`); });
  } else {
    marks.push(node(svg, center, 500, 300, prefix, "current"));
    items.forEach((item, index) => { const angle = -Math.PI / 2 + index * Math.PI * 2 / items.length, p = { x: 500 + Math.cos(angle) * 300, y: 300 + Math.sin(angle) * 210 }; marks.push(edge(svg, { x: 500, y: 300 }, p, item.transition ?? "relation", prefix, markerId, item.active), node(svg, item, p.x, p.y, prefix, item.active ? "recommended" : "future")); });
  } return marks;
}
function drawSpecial(svg, kind, data, prefix, markerId) {
  const marks = [];
  if (kind === "spectrum") {
    svg.appendChild(svgNode("line", { x1: 120, x2: 880, y1: 300, y2: 300, class: `${prefix}-spectrum` })); addText(svg, data.leftLabel, 120, 350, `${prefix}-endpoint`); addText(svg, data.rightLabel, 880, 350, `${prefix}-endpoint`);
    data.items.forEach((item) => { const x = 120 + item.position * 760; svg.appendChild(svgNode("line", { x1: x, x2: x, y1: 275, y2: 325, class: `${prefix}-tick` })); addText(svg, item.label, x, 255, `${prefix}-label`); });
  } else if (kind === "matrix-2x2") {
    svg.appendChild(svgNode("line", { x1: 120, x2: 880, y1: 300, y2: 300, class: `${prefix}-spectrum` })); svg.appendChild(svgNode("line", { x1: 500, x2: 500, y1: 80, y2: 520, class: `${prefix}-spectrum` }));
    addText(svg, data.axes.xLow, 120, 350, `${prefix}-endpoint`); addText(svg, data.axes.xHigh, 880, 350, `${prefix}-endpoint`); addText(svg, data.axes.yHigh, 520, 95, `${prefix}-endpoint`, "start"); addText(svg, data.axes.yLow, 520, 515, `${prefix}-endpoint`, "start");
    data.items.forEach((item) => marks.push(node(svg, item, 150 + item.x * 700, 490 - item.y * 380, prefix, item.recommended ? "recommended" : "future")));
  } else if (kind === "venn") {
    const left = svgNode("circle", { cx: 410, cy: 300, r: 190, class: `${prefix}-venn ${prefix}-series-1` }), right = svgNode("circle", { cx: 590, cy: 300, r: 190, class: `${prefix}-venn ${prefix}-series-2` }); svg.append(left, right); marks.push(left, right);
    addText(svg, data.left.label, 330, 300, `${prefix}-label`); addText(svg, data.right.label, 670, 300, `${prefix}-label`); addText(svg, data.intersection, 500, 300, `${prefix}-intersection`);
  } else if (kind === "grid-map") {
    const cellW = 760 / data.columns, cellH = 420 / data.rows;
    data.cells.forEach((cell) => { const x = 120 + cell.column * cellW, y = 90 + cell.row * cellH; const rect = svgNode("rect", { x: x + 4, y: y + 4, width: cellW - 8, height: cellH - 8, class: `${prefix}-cell ${prefix}-${cell.state ?? "future"}` }); svg.appendChild(rect); marks.push(rect); addText(svg, cell.label, x + cellW / 2, y + cellH / 2 + 5, `${prefix}-cell-label`); });
  }
  return marks;
}

function renderDiagram(svg, kind, data, prefix, markerId, seed) {
  if (["complex", "flow-chart"].includes(kind)) return drawLinear(svg, data, prefix, markerId, kind);
  if (["branching", "fork-join"].includes(kind)) return drawBranches(svg, data, prefix, markerId);
  if (["decision-tree", "tree"].includes(kind)) return drawTree(svg, data, prefix, markerId);
  if (["state-machine", "node-graph"].includes(kind)) return drawGraph(svg, data, prefix, markerId, seed);
  if (kind === "sequence") return drawSequence(svg, data, prefix, markerId);
  if (kind === "swimlane") return drawSwimlane(svg, data, prefix, markerId);
  if (kind === "loop") return drawLoop(svg, data, prefix, markerId);
  if (["pyramid", "funnel", "layered-stack"].includes(kind)) return drawStack(svg, data.levels ?? data.stages ?? data.layers, prefix, kind);
  if (kind === "concentric") return drawRadial(svg, null, data.rings, prefix, markerId, true);
  if (["mind-map", "hub-spoke"].includes(kind)) return drawRadial(svg, data.center, data.items ?? data.spokes, prefix, markerId);
  return drawSpecial(svg, kind, data, prefix, markerId);
}

export function mountDiagramComponent(root, context = {}, meta, prefix, config) {
  const params = validateParams(meta.id, context.params, meta.schema.properties);
  validateDiagramPayload(meta.id, config.kind, params.data, params);
  const css = `.comp-${meta.id}{position:relative;display:grid;grid-template-rows:auto minmax(0,1fr) auto;width:100%;height:100%;min-height:300px;padding:var(--comp-space-5);border:1px solid var(--comp-line);border-radius:var(--comp-radius-md);background:var(--comp-surface);color:var(--comp-ink);font-family:var(--comp-font-sans);overflow:hidden}.comp-${meta.id} .${prefix}-title{margin:0;font:800 clamp(22px,3vw,42px)/1.05 var(--comp-font-display)}.comp-${meta.id} .${prefix}-plot{width:100%;height:100%;min-height:210px}.comp-${meta.id} .${prefix}-source{color:var(--comp-muted);font:500 14px/1.4 var(--comp-font-mono)}.comp-${meta.id} .${prefix}-node rect{fill:var(--comp-surface-strong);stroke:var(--comp-line-strong);stroke-width:2}.comp-${meta.id} .${prefix}-node text{fill:var(--comp-ink);font:700 16px var(--comp-font-sans)}.comp-${meta.id} .${prefix}-past rect{fill:var(--comp-line)}.comp-${meta.id} .${prefix}-current rect,.comp-${meta.id} .${prefix}-recommended rect{fill:var(--comp-surface-strong);stroke:var(--comp-accent);stroke-width:5}.comp-${meta.id} .${prefix}-edge{fill:none;stroke:var(--comp-line-strong);stroke-width:3}.comp-${meta.id} .${prefix}-active-edge{stroke:var(--comp-accent);stroke-width:5}.comp-${meta.id} .${prefix}-arrow{fill:var(--comp-accent)}.comp-${meta.id} .${prefix}-edge-label,.comp-${meta.id} .${prefix}-label,.comp-${meta.id} .${prefix}-endpoint,.comp-${meta.id} .${prefix}-lane-label,.comp-${meta.id} .${prefix}-ring-label{fill:var(--comp-ink);font:650 14px var(--comp-font-sans);paint-order:stroke;stroke:var(--comp-canvas);stroke-width:5px}.comp-${meta.id} .${prefix}-lifeline{stroke:var(--comp-line);stroke-width:2;stroke-dasharray:8 8}.comp-${meta.id} .${prefix}-lane{fill:var(--comp-surface);stroke:var(--comp-line)}.comp-${meta.id} .${prefix}-layer{fill:var(--comp-accent);opacity:.9;stroke:var(--comp-canvas);stroke-width:2}.comp-${meta.id} .${prefix}-layer-label,.comp-${meta.id} .${prefix}-cell-label{fill:var(--comp-ink);font:750 17px var(--comp-font-sans);paint-order:stroke;stroke:var(--comp-canvas);stroke-width:8px;stroke-linejoin:round}.comp-${meta.id} .${prefix}-ring{fill:none;stroke:var(--comp-accent);stroke-width:28;opacity:.28}.comp-${meta.id} .${prefix}-series-1{opacity:.9}.comp-${meta.id} .${prefix}-series-2{opacity:.58}.comp-${meta.id} .${prefix}-series-3{opacity:.35}.comp-${meta.id} .${prefix}-spectrum,.comp-${meta.id} .${prefix}-tick{stroke:var(--comp-line-strong);stroke-width:3}.comp-${meta.id} .${prefix}-venn{fill:var(--comp-accent);stroke:var(--comp-accent);stroke-width:3;opacity:.38}.comp-${meta.id} .${prefix}-intersection{fill:var(--comp-ink);font:800 17px var(--comp-font-sans);paint-order:stroke;stroke:var(--comp-canvas);stroke-width:10px;stroke-linejoin:round}.comp-${meta.id} .${prefix}-cell{fill:var(--comp-surface-strong);stroke:var(--comp-line)}.comp-${meta.id} .${prefix}-cell.${prefix}-current,.comp-${meta.id} .${prefix}-cell.${prefix}-recommended{fill:var(--comp-surface-strong);stroke:var(--comp-accent);stroke-width:5}`;
  const { element, gsap } = createFidelityHost(root, context, meta, prefix, css);
  const title = htmlNode("h2", `${prefix}-title`, params.title); element.appendChild(title);
  const plot = svgNode("svg", { viewBox: `0 0 ${W} ${H}`, class: `${prefix}-plot`, role: "img", "aria-label": params.title });
  const markerId = deterministicId(context.instanceId, "arrow");
  const defs = svgNode("defs"), marker = svgNode("marker", { id: markerId, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" });
  marker.appendChild(svgNode("path", { d: "M 0 0 L 10 5 L 0 10 z", class: `${prefix}-arrow` })); defs.appendChild(marker); plot.appendChild(defs);
  const marks = renderDiagram(plot, config.kind, params.data, prefix, markerId, params.seed ?? 1); element.appendChild(plot);
  const source = htmlNode("footer", `${prefix}-source`, params.sourceNote); element.appendChild(source);
  const state = { progress: 0 };
  const render = () => marks.forEach((mark, index) => { mark.style.opacity = state.progress >= index / Math.max(1, marks.length) ? "" : "0"; });
  const enter = gsap.timeline({ paused: true }).fromTo(element, { autoAlpha: 0 }, { autoAlpha: 1, duration: .3, ease: "power2.out" });
  const explain = gsap.timeline({ paused: true }).to(state, { progress: 1, duration: 1.25, ease: "none", onUpdate: render });
  const emphasize = gsap.timeline({ paused: true }).to(element, { scale: 1.012, duration: .22 }).to(element, { scale: 1, duration: .24 });
  const exit = gsap.timeline({ paused: true }).to(element, { autoAlpha: 0, y: -10, duration: .35 });
  const segments = { enter, explain, emphasize, exit }; render();
  return { segments, seek(localFrame) { state.progress = normalizeLocalFrame(localFrame, params.durationFrames) / params.durationFrames; render(); }, destroy() { destroyFidelity(element, segments); } };
}
