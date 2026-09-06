import { mountIllustrationComponent } from "../illustration-runtime.js";

export const meta = {
  id: "illustration-analytics",
  version: 1,
  legacyAliases: ["illustrations.scene-analytics"],
  sceneRole: "chapter-cover",
  evidenceEligible: false,
  styleFallbacks: { ferrari: "icon-lucide-set", lamborghini: "icon-lucide-set" },
  schema: { properties: {
    title: { type: "string", required: true, maxLength: 90 },
    chapterIndex: { type: "number", min: 1, max: 99, default: 1 },
    sceneVariant: { type: "enum", values: ["analytics"], default: "analytics" },
    focalSide: { type: "enum", values: ["left", "right"], default: "right" },
    density: { type: "enum", values: ["sparse", "comfortable", "dense"], default: "comfortable" },
    caption: { type: "string", required: true, maxLength: 180 },
    accentRole: { type: "enum", values: ["concept", "collaboration", "tool", "evidence", "verification", "delivery"], default: "concept" },
    durationFrames: { type: "number", min: 18, max: 900, default: 120 },
  } },
};

export function mount(root, context = {}) {
  return mountIllustrationComponent(root, context, meta, "ia", { fixedSceneId: "analytics" });
}
