import { mountChartComponent } from "../chart-runtime.js";

export const meta = {
  id: "chart-sankey",
  version: 1,
  legacyAliases: ["broll-charts.sankey"],
  schema: {
    properties: {
      data: { type: "object", required: true },
      title: { type: "string", required: true, maxLength: 80 },
      sourceNote: { type: "string", required: true, maxLength: 180 },
      emptyLabel: { type: "string", default: "No data", maxLength: 60 },
      durationFrames: { type: "number", min: 18, max: 900, default: 120 },
      format: { type: "enum", values: ["number", "percent", "compact"], default: "number" },
    },
  },
};

export function mount(root, context = {}) {
  return mountChartComponent(root, context, meta, "qy", { kind: "sankey" });
}
