# result-rows · 结论汇报行

`[{tag, text}]` 标签 + 一行文，错拍逐条出现：结论 / 证据 / 风险 / 建议。
汇报段的标准件——`check-list` 管过程，`result-rows` 管结果。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `rows` | array | 必填 | `[{ tag, text }]`，2–5 行；`tag` ≤4 字，`text` 一行 |

tag 吃 `--comp-font-mono` 与 `--comp-accent`，text 吃 `--comp-font-sans` 与 `--comp-ink`。

## 命名段

- `enter`：每行 fade + 左移 10px，0.28s 错拍；tag 与 text 同行同步进入；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: {
    rows: [
      { tag: "结论", text: "队列卡在重试循环" },
      { tag: "证据", text: "jobs WHERE id=84 · retry=17" },
      { tag: "风险", text: "重试无上限，会拖垮 worker" },
      { tag: "建议", text: "加指数退避与最大次数" },
    ],
  },
  fps: 30,
});
```

## 组合

常接在 `check-list`（过程确认）或 `converge-summary`（归纳）之后；tag 可用 `numbered-tag` 同系编号替代。

## 禁区

- 标签文字不超过四个字，长标签改用 `side-note`；
- `text` 只写一行，折行就拆行；
- 不与 `check-list` 混用语义：勾号管"做完了"，tag 管"怎么看"。
