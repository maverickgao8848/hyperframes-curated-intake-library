# check-list · 检查清单

行项逐个出现并打勾，右侧等宽字体放证据细节，表达操作序列、验证步骤、完成确认。
参考形态：SUB-AGENT 片子会话的 `Read worker/queue.ts ✓`、`Query db · jobs WHERE id=84 ✓`。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `rows` | array | 必填 | `[{ label, detail? }]`，2–7 行；`label` 是动作名，`detail` 是证据 |
| `title` | string \| null | `null` | 清单标题（mono 小字，如 `过程 · 只看相关代码`） |

尺寸经 token 覆盖：`--comp-list-w`；勾号颜色吃 `--comp-accent`。

## 命名段

- `enter`：每行 fade + 左移 10px 进入（0.32s 错拍）→ 勾号描画 → detail 淡入；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: {
    title: "过程 · 只看相关代码 / 接口 / 日志",
    rows: [
      { label: "Read", detail: "worker/queue.ts · 状态写入" },
      { label: "Query", detail: "db · jobs WHERE id=84" },
      { label: "Fetch", detail: "/api/status/84 → completed" },
    ],
  },
  fps: 30,
});
```

## 组合

常放在 `window-card` 内部充当窗口内容；完成后可接 `result-rows` 汇报结论。

## 禁区

- 超过七行拆幕，不用滚动或缩小硬塞；
- `detail` 只放一行短证据（文件、命令、参数），不写句子；
- 勾号是确认语义，禁止用于未完成项。
