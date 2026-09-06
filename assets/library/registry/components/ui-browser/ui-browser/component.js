import { mountUiMockComponent } from "../ui-mock-runtime.js";

export const meta = {
  id: "ui-browser",
  version: 1,
  legacyAliases: ["broll-ui.browser"],
  schema: { properties: {
    data: { type: "object", required: true },
    mock: { type: "boolean", required: true },
    title: { type: "string", required: true, maxLength: 80 },
    sourceNote: { type: "string", required: true, maxLength: 180 },
    durationFrames: { type: "number", min: 18, max: 900, default: 120 },
  } },
};

export function mount(root, context = {}) {
  return mountUiMockComponent(root, context, meta, "ud", { kind: "browser" });
}
