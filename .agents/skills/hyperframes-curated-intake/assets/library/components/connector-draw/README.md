# connector-draw · 描画连线

两个锚点之间的 1px 细线描画，可选虚线与箭头。表达因果、指向、归属：
"这个参数决定了那个行为"。`step-chain` 的连线就是它的预封装用法。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `from` | string | 必填 | 起点锚点选择器 |
| `to` | string | 必填 | 终点锚点选择器 |
| `dash` | boolean | `false` | 虚线（推测/间接关系） |
| `arrow` | boolean | `true` | 末端箭头（有方向语义时开） |

线色吃 `--comp-line`，描画中的高亮段吃 `--comp-ink-dim`。

## 命名段

- `enter`：从 `from` 向 `to` 描画（stroke-dashoffset），0.6–0.8s 按线长折算；箭头在末端就位后 0.1s 弹入；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: { from: "#flag-verbose", to: "#log-panel", dash: false, arrow: true },
  fps: 30,
});
```

## 组合

配合 `window-card` 标注界面元素，或给 `side-note` 提供跨画面指向；两个以上锚点的流程用 `step-chain`，不手画多条线。

## 禁区

- 跨画面长线同幕不超过两条，多了就是流程图；
- 线不穿过任何文字，必要时绕行或缩短；
- `dash: true` 只用于推测/间接关系，确定因果用实线。
