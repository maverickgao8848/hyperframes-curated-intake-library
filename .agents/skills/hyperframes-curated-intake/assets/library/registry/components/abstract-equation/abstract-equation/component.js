import { mountAbstractComponent } from "../abstract-runtime.js";

export const meta = {
  id: "abstract-equation",
  version: 1,
  legacyAliases: ["broll-abstract.equation"],
  schema: { properties: {
    data: { type: "object", required: true },
    title: { type: "string", required: true, maxLength: 80 },
    sourceNote: { type: "string", required: true, maxLength: 180 },
    durationFrames: { type: "number", min: 18, max: 900, default: 120 },
  } },
};

export function mount(root, context = {}) {
  return mountAbstractComponent(root, context, meta, "ac", { kind: "equation" });
}
