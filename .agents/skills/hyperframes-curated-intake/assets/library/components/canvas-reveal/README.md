# Canvas Reveal

Registry ID：`canvas-reveal`；候选身份：`EDU-REVEAL-02`。

真实 WebGL dot-matrix shader。径向揭示、噪声阈值和高亮波前均由 timeline progress 驱动。

| 参数 | 说明 |
| --- | --- |
| `label` | 揭示后的结论文案 |
| `colors` | 一至两个 RGB 数组 |
| `opacities` | 透明度层级，用于视觉语义与 HUD |
| `dotSize` | 点尺寸，1–5 |
| `seed` | 确定性噪声种子 |

命名段：`enter`、`emphasis`、`dim`、`exit`。不使用 `requestAnimationFrame` 或系统时钟。
