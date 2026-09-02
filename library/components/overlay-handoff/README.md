# overlay-handoff · 叠化交棒

图形场景向实拍/截图的交棒：整幕图形淡出、媒体浮现，指定组件以半透明残留
（`lingerOpacity`）继续压在媒体上，其余随场景退出。用于"讲完原理，看真实界面"。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `mediaRef` | string | 必填 | 图片或视频的项目本地相对路径；禁止 URL、绝对路径和 `..` |
| `graphicsLayer` | string \| Element | 必填 | 被交棒的图形层选择器或元素 |
| `lingerOpacity` | number | `0.18` | 残留组件的停留不透明度（0–1） |
| `keepComponents` | array | `[]` | 残留的组件实例/选择器，其余组件随图形层退出 |
| `handoffSeconds` | number | `1.2` | 交棒主段时长（秒） |

纯交棒段，不绘制表面，无自有 `--comp-*` token。

## 命名段

- `enter`：媒体淡入 0.6s，图形层同步降到 60%；
- `handoff`：交棒主段（默认 1.2s）——图形层退出，`keepComponents` 降到 `lingerOpacity` 停在媒体上；
- `dim` / `exit`：媒体与残留组件一起降压、退出。

## 示例

```js
mount(root, {
  instanceId: "handoff-ui-01",
  params: {
    mediaRef: "assets/images/codex-tui-real.png",
    graphicsLayer: "#concept-graphics",
    lingerOpacity: 0.15,
    keepComponents: ["#annotation-connector"],
  },
  fps: 30,
});
```

## 组合

接在 `window-card` 或 `step-chain` 之后：图形讲结构，交棒看实物；残留常用 `connector-draw` 或 `side-note` 保持标注。

## 禁区

- 残留图形不得遮挡人脸或截图焦点（界面关键区域、按钮、输出文本）；
- `mediaRef` 只用项目本地冻结路径，禁止 render-time 网络媒体；
- 视频由扩展名推断为 `<video>`，组件不调用 `play()` 或自行 seek，播放归 HyperFrames；
- `lingerOpacity` 不超过 0.3，残留是余韵不是内容。
