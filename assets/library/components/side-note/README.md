# side-note · 侧边注释

挂在既有元素旁的小注释（mono 小字 + 可选短引线），补充主线之外的信息：
「这次要做什么」「注意这个参数」。主体讲内容，注释讲上下文。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `text` | string | 必填 | 注释文字，一行短句 |
| `anchor` | string \| null | `null` | 锚点元素选择器；为空时作为自由注释由场景布局 |
| `position` | `"right" \| "below"` | `"right"` | 相对锚点的停靠方位 |

文字吃 `--comp-ink-dim` 与 `--comp-font-mono`，引线吃 `--comp-line`。

## 命名段

- `enter`：fade + 从锚点方向 8px 滑入，0.5s；引线在文字就位前 0.1s 先描出；
- `dim` / `exit`：跟随锚点主体一起降压、退出。

## 示例

```js
mount(root, {
  params: {
    text: "这次要做什么：让 Codex 只看队列相关代码",
    anchor: "#step-read",
    position: "below",
  },
  fps: 30,
});
```

## 组合

挂在 `step-chain` 某步或 `window-card` 内元素旁；需要跨元素指向时改用 `connector-draw`。

## 禁区

- 注释不得早于锚点主体出现，enter 必须排在主体之后；
- 一行写完，不换行、不写段落；
- 不遮挡锚点主体，`right` 放不下就用 `below`。
