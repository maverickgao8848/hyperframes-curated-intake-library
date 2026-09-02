import { mountChartComponent } from "../chart-runtime.js";

export const meta = {
  id: "chart-gauge",
  version: 1,
  legacyAliases: ["broll-charts.gauge"],
  schema: {
    properties: {
      data: { type: "object", required: true },
      title: { type: "string", required: true, maxLength: 80 },
      sourceNote: { type: "string", required: true, maxLength: 180 },
      emptyLabel: { type: "string", default: "No data", maxLength: 60 },
      durationFrames: { type: "number", min: 18, max: 900, default: 120 },
      format: { type: "enum", values: ["number", "percent", "compact"], default: "number" },
      label: { type: "string", required: true, maxLength: 60 },
    },
  },
};

export function mount(root, context = {}) {
  return mountChartComponent(root, context, meta, "qg", { kind: "gauge" });
}
