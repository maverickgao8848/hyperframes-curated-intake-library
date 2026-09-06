# typewriter-block · 打字机文本

关键句逐字打出 + 光标跟随，`keywords` 内的词加虚线下划线。
承担口播同步的"正在发生"感——Codex 思考、命令敲入这类语境的标配。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `text` | string | 必填 | 要打出的全文，一两行短句 |
| `keywords` | array | `[]` | `text` 中需要虚线下划线的词，≤3 个 |
| `speed` | number | `12` | 打字速度，字/秒 |
| `cursor` | boolean | `true` | 是否显示方块光标 |

enter 时长 = 字数 / `speed`，覆盖 `intro_seconds` 默认值。
正文吃 `--comp-font-sans`，下划线吃 `--comp-accent`，光标吃 `--comp-ink`。

## 命名段

- `enter`：逐字出现（每字 1/`speed` 秒），光标随字推进；打完后光标闪烁 3 次停在实色，不用无限循环；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: {
    text: "帮我找到队列卡住的原因",
    keywords: ["队列", "原因"],
    speed: 10,
  },
  fps: 30,
});
```

## 组合

放在 `window-card` 内模拟用户输入或 Codex 输出；`keywords` 的词常与 `connector-draw` 的标注目标对应。

## 禁区

- 不超过两行的长文打字，长文拆段或改用普通排版；
- 光标闪烁是有限动画，禁止无限循环（确定性渲染）；
- `keywords` 必须是 `text` 的原样子串，不匹配则不加下划线。
