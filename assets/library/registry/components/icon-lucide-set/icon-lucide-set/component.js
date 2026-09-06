import { mountIconComponent } from "../icon-runtime.js";

export const meta = {
  id: "icon-lucide-set",
  version: 1,
  legacyAliases: ["icons.lucide-set"],
  assetPolicy: { frozenSubset: "lucide-teaching-core@1.8.0", arbitrarySvg: false },
  schema: { properties: {
    iconId: { type: "string", required: true, maxLength: 48 },
    strokeWeight: { type: "number", min: 1.5, max: 3, default: 2 },
    title: { type: "string", required: true, maxLength: 80 },
    label: { type: "string", required: true, maxLength: 140 },
    durationFrames: { type: "number", min: 18, max: 900, default: 120 },
  } },
};

export function mount(root, context = {}) {
  return mountIconComponent(root, context, meta, "ia", { kind: "lucide" });
}
