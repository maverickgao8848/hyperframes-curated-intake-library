import { mountThinkingComponent } from "../thinking-runtime.js";

export const meta = {
  id: "thinking-kanban",
  version: 1,
  legacyAliases: ["broll-thinking.kanban"],
  schema: { properties: {
    data: { type: "object", required: true },
    title: { type: "string", required: true, maxLength: 80 },
    sourceNote: { type: "string", required: true, maxLength: 180 },
    durationFrames: { type: "number", min: 18, max: 900, default: 120 },
  } },
};

export function mount(root, context = {}) {
  return mountThinkingComponent(root, context, meta, "tj", { kind: "kanban" });
}
