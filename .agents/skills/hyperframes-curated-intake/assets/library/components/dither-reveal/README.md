# Dither Reveal

Registry ID：`dither-reveal`；候选身份：`EDU-REVEAL-03`。

真实 Canvas 像素采样与 ordered dithering。支持 Bayer、halftone 和确定性 noise 阈值。

| 参数 | 说明 |
| --- | --- |
| `mediaRef` | 项目本地图片；空值使用内置测试图 |
| `gridSize` | 像素网格尺寸 |
| `ditherMode` | `bayer` / `halftone` / `noise` |
| `colorMode` | `duotone` / `original` |
| `invert` | 反转亮度 |
| `threshold` | 基础阈值 0–1 |
| `primaryColor` | 暗色 |
| `secondaryColor` | 亮色 |

命名段：`enter`、`emphasis`、`dim`、`exit`。
