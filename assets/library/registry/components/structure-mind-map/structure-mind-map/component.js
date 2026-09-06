import { mountDiagramComponent } from "../diagram-runtime.js";

export const meta = {
  id: "structure-mind-map",
  version: 1,
  legacyAliases: ["broll-structures2.mind-map"],
  schema: { properties: {
    data: { type: "object", required: true },
    title: { type: "string", required: true, maxLength: 80 },
    sourceNote: { type: "string", required: true, maxLength: 180 },
    durationFrames: { type: "number", min: 18, max: 900, default: 120 },
    seed: { type: "number", min: 0, max: 4294967295, default: 1 },
  } },
};

export function mount(root, context = {}) {
  return mountDiagramComponent(root, context, meta, "um", { kind: "mind-map" });
}
