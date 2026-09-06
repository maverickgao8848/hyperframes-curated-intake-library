(() => {
  "use strict";

  const $ = (selector) => document.querySelector(selector);
  const VISUAL_TYPES = ["source-footage", "external-evidence", "external-broll", "registry-block", "curated-teaching", "generated-visual"];
  const POLICIES = ["frame-governed", "native-evidence", "wrapper-only", "source-preserve"];
  const LAYER_TYPES = ["camera", "focus", "annotation", "typography", "caption", "host", "environment", "evidence", "audio"];
  const TRACKS = [["story", "内容"], ["dominant", "主画面"], ["layers", "辅助层"], ["transition", "转场"]];

  const VISUAL_LABELS = {
    "source-footage": "原片",
    "external-evidence": "外部证据",
    "external-broll": "补充素材",
    "registry-block": "完整动画画面",
    "curated-teaching": "教学动画",
    "generated-visual": "定制画面"
  };
  const POLICY_LABELS = {
    "frame-governed": "跟随项目视觉",
    "native-evidence": "保留原生界面",
    "wrapper-only": "仅调整外层",
    "source-preserve": "保留素材原貌"
  };
  const LAYER_LABELS = {
    camera: "镜头运动", focus: "聚焦", annotation: "标注", typography: "文字动效",
    caption: "字幕", host: "人物", environment: "环境氛围", evidence: "证据提示", audio: "声音"
  };
  const STATE_LABELS = {proposed: "待确认", approved: "已接受", rejected: "需修改", locked: "已锁定", draft: "草稿", "in-review": "审阅中"};
  const ROUTE_LABELS = {"direct-build": "直接制作", "curated-intake": "教学动画设计", "media-sourcing": "素材准备", "source-only": "保留原片"};
  const CONTENT_LABELS = {
    sourceId: "素材", screenText: "屏幕文字", fit: "画面适配", contactName: "联系人",
    message1: "第 1 条消息", message2: "第 2 条消息", message3: "第 3 条消息", message4: "第 4 条消息",
    prompt: "提问文字", intro1: "回答第一段", intro2: "回答第二段", compactMode: "紧凑模式",
    teachingGoal: "教学目标", animationScopeConfirmed: "动画范围已确认",
    role1: "第一行角色", name1: "第一行名称", role2: "第二行角色", name2: "第二行名称",
    foreground: "前景色", accent: "强调色", background: "背景色"
  };

  let state;
  let selectedId;
  let toastTimer;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[character]));
  const option = (value, label = value) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`;
  const percent = (frame) => `${frame * 100 / state.plan.project.durationFrames}%`;
  const seconds = (frame) => frame / state.plan.project.fps;
  const timeLabel = (frame) => `${seconds(frame).toFixed(seconds(frame) % 1 ? 1 : 0)} 秒`;
  const segmentNumber = (id) => state.plan.segments.findIndex((segment) => segment.id === id) + 1;
  const segmentLabel = (id) => `第 ${segmentNumber(id)} 段`;

  function toast(message, error = false) {
    clearTimeout(toastTimer);
    const element = $("#toast");
    element.textContent = message;
    element.className = `toast show${error ? " error" : ""}`;
    toastTimer = setTimeout(() => { element.className = "toast"; }, 3200);
  }

  async function load() {
    const response = await fetch("/api/plan", {cache: "no-store"});
    state = await response.json();
    if (!selectedId && state.plan.segments.length) selectedId = state.plan.segments[0].id;
    render();
  }

  async function patch(operations) {
    const response = await fetch("/api/patch", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({schemaVersion: "hyperframes-visual-director/patch-v1", baseRevision: state.plan.revision, operations})
    });
    const data = await response.json();
    if (!response.ok) {
      toast(data.message || data.error || "保存失败，请检查后重试", true);
      if (response.status === 409) await load();
      return false;
    }
    state = {...state, ...data};
    toast(`已保存 · 版本 ${state.plan.revision}`);
    render();
    return true;
  }

  function visualTitle(segment) {
    const visual = segment.dominantVisual;
    const catalog = state.catalog.entries.find((entry) => entry.id === visual.catalogId);
    return catalog?.title || VISUAL_LABELS[visual.type] || visual.type;
  }

  function render() {
    const plan = state.plan;
    const approved = plan.segments.filter((segment) => ["approved", "locked"].includes(segment.approval.state)).length;
    const pending = plan.segments.length - approved;
    $("#revision").textContent = `版本 ${plan.revision}`;
    $("#approval").textContent = STATE_LABELS[plan.approval.state] || plan.approval.state;
    $("#projectMeta").textContent = `${plan.project.width}×${plan.project.height} · ${plan.project.fps} fps`;
    $("#metricGrid").innerHTML = [
      [`${seconds(plan.project.durationFrames).toFixed(1)} 秒`, "总时长"],
      [plan.segments.length, "片段"],
      [pending, "待确认"],
      [plan.assetRequests.filter((item) => !["ready", "waived"].includes(item.status)).length, "素材待办"]
    ].map(([value, label]) => `<div class="metric"><b>${value}</b><span>${label}</span></div>`).join("");
    $("#shareBars").innerHTML = Object.entries(state.metrics.dominantVisualSharePercent).map(([key, value]) => `<div class="share ${escapeHtml(key)}" style="width:${value}%" data-label="${escapeHtml(VISUAL_LABELS[key] || key)} ${value}%"></div>`).join("");
    renderTimeline();
    renderAssets();
    renderApproval();
    renderInspector();
  }

  function renderTimeline() {
    $("#trackLabels").innerHTML = TRACKS.map(([, label]) => `<div class="track-label">${label}</div>`).join("");
    $("#ruler").innerHTML = Array.from({length: 9}, (_, index) => {
      const frame = state.plan.project.durationFrames * index / 8;
      return `<span class="tick" style="left:${index * 12.5}%">${seconds(frame).toFixed(1)}s</span>`;
    }).join("");
    const rows = Object.fromEntries(TRACKS.map(([key]) => [key, []]));
    for (const segment of state.plan.segments) {
      const visual = segment.dominantVisual;
      const story = segment.message || segment.sourceAnchors.map((anchor) => anchor.text).join(" ");
      rows.story.push(timelineClip(segment.id, segment.range, story, "story"));
      rows.dominant.push(timelineClip(segment.id, segment.range, visualTitle(segment), visual.type, true));
      if (segment.layers.length) {
        const layerNames = [...new Set(segment.layers.map((layer) => LAYER_LABELS[layer.type] || layer.type))].join(" + ");
        rows.layers.push(timelineClip(segment.id, segment.range, layerNames, "layer-summary"));
      }
    }
    for (const edge of state.plan.edges) {
      rows.transition.push(`<span class="clip edge" style="left:${percent(edge.boundaryFrame)}" title="片段切换"></span>`);
    }
    $("#tracks").innerHTML = TRACKS.map(([key]) => `<div class="track ${key}">${rows[key].join("")}</div>`).join("");
    document.querySelectorAll("[data-segment]").forEach((element) => element.addEventListener("click", () => {
      selectedId = element.dataset.segment;
      renderTimeline();
      renderInspector();
    }));
  }

  function timelineClip(id, range, label, className, clickable = false) {
    const selected = selectedId === id ? " selected" : "";
    const title = `${segmentLabel(id)} · ${timeLabel(range.startFrame)}–${timeLabel(range.endFrame)} · ${label}`;
    return `<button class="clip ${className}${selected}" style="left:${percent(range.startFrame)};width:${percent(range.endFrame - range.startFrame)}" ${clickable ? `data-segment="${escapeHtml(id)}"` : "tabindex='-1'"} title="${escapeHtml(title)}">${escapeHtml(label)}</button>`;
  }

  function catalogEntries(kind) {
    return state.catalog.entries.filter((entry) => entry.kind === kind && ["ready", "verified", "published"].includes(entry.status) && (!String(entry.id).startsWith("talkcraft:") || ["verified", "published"].includes(entry.portStatus)));
  }

  function renderInspector() {
    const segment = state.plan.segments.find((item) => item.id === selectedId);
    if (!segment) {
      selectedId = null;
      $("#segmentInspector").hidden = true;
      $("#emptyInspector").hidden = false;
      return;
    }
    const visual = segment.dominantVisual;
    $("#emptyInspector").hidden = true;
    $("#segmentInspector").hidden = false;
    $("#selectionState").textContent = segmentLabel(segment.id);
    $("#segmentNumber").textContent = segmentLabel(segment.id);
    $("#segmentTime").textContent = `${timeLabel(segment.range.startFrame)} — ${timeLabel(segment.range.endFrame)}`;
    $("#segmentStatus").textContent = STATE_LABELS[segment.approval.state] || segment.approval.state;
    $("#segmentStatus").className = `status-pill ${segment.approval.state}`;
    $("#messageView").textContent = segment.message;
    $("#visualTitle").textContent = visualTitle(segment);
    $("#visualBadge").textContent = VISUAL_LABELS[visual.type] || visual.type;
    $("#rationaleView").textContent = visual.rationale || "这是当前推荐方案。";

    $("#segmentId").value = segment.id;
    $("#route").value = segment.route;
    $("#startFrame").value = segment.range.startFrame;
    $("#endFrame").value = segment.range.endFrame;
    $("#endSeconds").value = seconds(segment.range.endFrame).toFixed(1);
    $("#message").value = segment.message;
    $("#visualType").innerHTML = VISUAL_TYPES.map((value) => option(value, VISUAL_LABELS[value])).join("");
    $("#visualType").value = visual.type;
    $("#framePolicy").innerHTML = POLICIES.map((value) => option(value, POLICY_LABELS[value])).join("");
    $("#framePolicy").value = visual.framePolicy;
    const blocks = catalogEntries("registry-block");
    $("#catalogId").innerHTML = option("", "请选择具体方案") + blocks.map((entry) => option(entry.id, entry.title || entry.id)).join("");
    $("#catalogId").value = visual.catalogId || "";
    $("#catalogField").hidden = visual.type !== "registry-block";
    $("#content").value = JSON.stringify(visual.content || {}, null, 2);
    $("#rationale").value = visual.rationale || "";
    renderContentFields(visual.content || {});
    renderLayers(segment);
    $("#segmentJson").textContent = JSON.stringify({segment, audit: state.plan.audit.slice(-5)}, null, 2);
  }

  function renderContentFields(content) {
    const entries = Object.entries(content).filter(([, value]) => ["string", "number", "boolean"].includes(typeof value));
    $("#contentFields").innerHTML = entries.length ? `<span class="field-title">画面中的关键内容</span><div class="content-grid">${entries.map(([key, value]) => {
      const label = CONTENT_LABELS[key] || key.replace(/([A-Z])/g, " $1").trim();
      if (typeof value === "boolean") return `<label class="check-field"><input type="checkbox" data-content-key="${escapeHtml(key)}" data-value-type="boolean" ${value ? "checked" : ""}><span>${escapeHtml(label)}</span></label>`;
      if (typeof value === "number") return `<label>${escapeHtml(label)}<input type="number" data-content-key="${escapeHtml(key)}" data-value-type="number" value="${value}"></label>`;
      const control = String(value).length > 52 ? `<textarea rows="2" data-content-key="${escapeHtml(key)}" data-value-type="string">${escapeHtml(value)}</textarea>` : `<input data-content-key="${escapeHtml(key)}" data-value-type="string" value="${escapeHtml(value)}">`;
      return `<label>${escapeHtml(label)}${control}</label>`;
    }).join("")}</div>` : "";
  }

  function renderLayers(segment) {
    $("#layerCount").textContent = `${segment.layers.length} 项`;
    $("#layerList").innerHTML = segment.layers.map((layer) => `<div class="layer-row"><div><b>${escapeHtml(LAYER_LABELS[layer.type] || layer.type)}</b><small>${timeLabel(layer.range.startFrame)}–${timeLabel(layer.range.endFrame)}</small></div><button data-remove-layer="${escapeHtml(layer.id)}" aria-label="删除${escapeHtml(LAYER_LABELS[layer.type] || layer.type)}">移除</button></div>`).join("") || "<p class='empty compact'>这段没有辅助效果。</p>";
    document.querySelectorAll("[data-remove-layer]").forEach((element) => {
      element.onclick = () => patch([{type: "remove-layer", segmentId: segment.id, layerId: element.dataset.removeLayer}]);
    });
    $("#newLayerType").innerHTML = LAYER_TYPES.map((value) => option(value, LAYER_LABELS[value])).join("");
    renderLayerCandidates();
  }

  function renderLayerCandidates() {
    const type = $("#newLayerType").value;
    const entries = state.catalog.entries.filter((entry) => entry.kind === "layer" && (!entry.layerType || entry.layerType === type) && ["ready", "verified", "published"].includes(entry.status));
    $("#newLayerCatalog").innerHTML = option("", "自定义") + entries.map((entry) => option(entry.id, entry.title || entry.id)).join("");
  }

  function renderAssets() {
    const priorities = {required: "必须", recommended: "建议", optional: "可选"};
    const statuses = {open: "待准备", linked: "已关联", waived: "已跳过", ready: "已就绪"};
    $("#assetCount").textContent = `${state.plan.assetRequests.length} 项`;
    $("#assetList").innerHTML = state.plan.assetRequests.map((item, index) => {
      const usedIn = item.segmentIds.map(segmentLabel).join("、");
      return `<article class="asset-card"><div class="asset-card-head"><h3>素材 ${index + 1}</h3><span>${escapeHtml(statuses[item.status] || item.status)}</span></div><p>${escapeHtml(item.specification)}</p><small>${escapeHtml(priorities[item.priority] || item.priority)} · 用于 ${escapeHtml(usedIn)}</small><div class="asset-link"><input data-asset-path="${escapeHtml(item.id)}" value="${escapeHtml(item.linkedPath || item.path || "")}" placeholder="选择或粘贴本地素材路径"><button data-link-asset="${escapeHtml(item.id)}">关联素材</button></div></article>`;
    }).join("") || "<div class='empty compact'>没有素材待办。</div>";
    document.querySelectorAll("[data-link-asset]").forEach((element) => {
      element.onclick = () => {
        const id = element.dataset.linkAsset;
        const input = document.querySelector(`[data-asset-path='${CSS.escape(id)}']`);
        patch([{type: "attach-asset", assetRequestId: id, assetPath: input.value}]);
      };
    });
  }

  function renderApproval() {
    const approved = state.plan.segments.filter((segment) => ["approved", "locked"].includes(segment.approval.state)).length;
    const errors = state.errors || [];
    $("#validation").className = errors.length ? "validation-errors" : "validation-ok";
    $("#validation").innerHTML = errors.length
      ? `<b>还有 ${errors.length} 项需要处理</b><p>先完成片段确认或修正配置，再批准整片。</p><details><summary>查看技术原因</summary><ul>${errors.map((error) => `<li>${escapeHtml(error)}</li>`).join("")}</ul></details>`
      : "<b>检查通过</b><p>画面覆盖、时间边界和素材绑定均有效。</p>";
    $("#approvalSummary").innerHTML = `<b>${approved}/${state.plan.segments.length} 段已确认</b><span>${approved === state.plan.segments.length ? "可以批准整片" : `还有 ${state.plan.segments.length - approved} 段待确认`}</span>`;
    $("#finalApprove").disabled = Boolean(errors.length) || approved !== state.plan.segments.length || state.plan.approval.state === "approved";
  }

  $("#visualType").addEventListener("change", () => {
    const type = $("#visualType").value;
    $("#catalogField").hidden = type !== "registry-block";
    if (type !== "registry-block") $("#catalogId").value = "";
    $("#framePolicy").value = ["source-footage", "external-evidence", "external-broll"].includes(type) ? "source-preserve" : "frame-governed";
  });
  $("#catalogId").addEventListener("change", () => {
    const entry = state.catalog.entries.find((item) => item.id === $("#catalogId").value);
    if (entry?.framePolicy) $("#framePolicy").value = entry.framePolicy;
  });
  $("#newLayerType").addEventListener("change", renderLayerCandidates);
  $("#route").addEventListener("change", () => patch([{type: "set-route", segmentId: selectedId, route: $("#route").value}]));
  $("#endSeconds").addEventListener("change", () => {
    const segments = state.plan.segments;
    const index = segments.findIndex((segment) => segment.id === selectedId);
    if (index >= segments.length - 1) {
      toast("最后一段的结束时间由全片时长决定", true);
      renderInspector();
      return;
    }
    const frame = Math.round(Number($("#endSeconds").value) * state.plan.project.fps);
    patch([{type: "set-boundary", leftSegmentId: selectedId, rightSegmentId: segments[index + 1].id, frame}]);
  });
  $("#saveVisual").addEventListener("click", () => {
    let content;
    try { content = JSON.parse($("#content").value || "{}"); }
    catch { toast("技术详情中的画面参数不是有效 JSON", true); return; }
    document.querySelectorAll("[data-content-key]").forEach((field) => {
      const type = field.dataset.valueType;
      content[field.dataset.contentKey] = type === "boolean" ? field.checked : type === "number" ? Number(field.value) : field.value;
    });
    const current = state.plan.segments.find((segment) => segment.id === selectedId).dominantVisual;
    const value = {...current, type: $("#visualType").value, framePolicy: $("#framePolicy").value, content, rationale: $("#rationale").value};
    const catalogId = $("#catalogId").value;
    if (catalogId) value.catalogId = catalogId; else delete value.catalogId;
    patch([{type: "replace-dominant", segmentId: selectedId, value}]);
  });
  $("#addLayer").addEventListener("click", () => {
    const segment = state.plan.segments.find((item) => item.id === selectedId);
    const type = $("#newLayerType").value;
    const catalogId = $("#newLayerCatalog").value;
    const layer = {
      id: `layer-${Date.now().toString(36)}`,
      type,
      range: {...segment.range},
      framePolicy: ["camera", "focus", "evidence"].includes(type) ? "source-preserve" : "frame-governed",
      target: $("#newLayerTarget").value || "dominant-visual",
      content: {}
    };
    if (catalogId) layer.catalogId = catalogId;
    patch([{type: "add-layer", segmentId: selectedId, layer}]);
  });
  document.querySelectorAll("[data-state]").forEach((element) => element.addEventListener("click", () => patch([{type: "set-approval", segmentId: selectedId, state: element.dataset.state}])));
  $("#addComment").addEventListener("click", () => {
    const body = $("#commentBody").value.trim();
    if (!body) { toast("请先写下具体修改意见", true); return; }
    patch([{type: "comment", targetId: selectedId, body}]).then((ok) => { if (ok) $("#commentBody").value = ""; });
  });
  $("#finalApprove").addEventListener("click", () => patch([{type: "approve-plan"}]));

  load().catch((error) => toast(`载入失败：${error.message}`, true));
})();
