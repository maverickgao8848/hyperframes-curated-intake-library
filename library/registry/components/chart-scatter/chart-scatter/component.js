import { mountChartComponent } from "../chart-runtime.js";

export const meta = {
  id: "chart-scatter",
  version: 1,
  legacyAliases: ["broll-charts.scatter"],
  schema: {
    properties: {
      data: { type: "array", required: true, maxItems: 30 },
      title: { type: "string", required: true, maxLength: 80 },
      sourceNote: { type: "string", required: true, maxLength: 180 },
      emptyLabel: { type: "string", default: "No data", maxLength: 60 },
      durationFrames: { type: "number", min: 18, max: 900, default: 120 },
      format: { type: "enum", values: ["number", "percent", "compact"], default: "number" },
      xMin: { type: "number" },
      xMax: { type: "number" },
      yMin: { type: "number" },
      yMax: { type: "number" },
    },
  },
};

export function mount(root, context = {}) {
  return mountChartComponent(root, context, meta, "qs", { kind: "scatter" });
}
