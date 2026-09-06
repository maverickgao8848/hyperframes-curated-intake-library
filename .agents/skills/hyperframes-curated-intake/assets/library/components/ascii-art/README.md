# ASCII Art

Registry ID：`ascii-art`；候选身份：`EDU-CODE-02`。

真实 Canvas 图像采样组件：先把项目本地图片缩采样为亮度网格，再映射为字符集，可确定性逐字符揭示。

| 参数 | 说明 |
| --- | --- |
| `mediaRef` | 项目本地图片路径；空值使用内置确定性轮廓测试图 |
| `resolution` | 字符列数，默认 92 |
| `charset` | `standard` / `blocks` / `binary` / `braille` / `dense` 或自定义字符 |
| `colored` | 是否使用原图像素颜色 |
| `inverted` | 是否反转亮度到字符的映射 |
| `objectFit` | `cover` / `contain` / `fill` |

命名段：`enter`、`emphasis`、`dim`、`exit`。所有动画由 paused timeline 驱动，不使用系统时钟或自由运行循环。
