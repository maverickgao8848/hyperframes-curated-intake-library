# sticker-label · 贴纸标签

微旋转的纸片标签（白底黑字、像随手贴上去的），打破深色网格的"人情味"件。
承担口语化强调：替观众说一句话，如「替你猜」。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `text` | string | 必填 | 贴纸文案，≤8 字短口语 |
| `rotation` | number | `-3` | 旋转角度，建议 -6° 到 6° |
| `tone` | `"paper" \| "dark"` | `"paper"` | 纸片配色：白纸黑字 / 深底白字 |

paper 态用 `--comp-ink` 反相（亮底暗字），dark 态回归 `--comp-surface` 系；字体吃 `--comp-font-sans`。

## 命名段

- `enter`：从 1.15 倍缩放回 1，rotation 从 ±2° 余量回正，0.5s 弹性收尾；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: { text: "替你猜", rotation: -4, tone: "paper" },
  fps: 30,
});
```

## 组合

常贴在 `typewriter-block` 的关键句旁或 `window-card` 边角；与 `side-note` 分工：贴纸给情绪，注释给信息。

## 禁区

- 每幕最多一个贴纸，第二个就没有"打破网格"的效果了；
- 旋转不超过 ±6°，再大读不清；
- 不承担关键信息，遮住贴纸不影响理解。
