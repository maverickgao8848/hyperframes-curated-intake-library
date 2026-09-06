# scene-kicker · 章节角标

每幕的身份锚点：`EP108 · 01 PROMPT` 式左上角标，等宽字体、大写字距、全程在场。
观众随时知道"现在讲到哪一节"——这是长教学片不迷路的最低价手段。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `eyebrow` | string | `"EP"` | 系列/栏目名 |
| `index` | string | `"01"` | 章节编号，传空串隐藏编号段 |
| `title` | string | `""` | 章节名（建议英文大写或短词） |
| `align` | `"top-left" \| "top-right"` | `"top-left"` | 停靠角 |

尺寸经 token 覆盖：`--comp-kicker-size`、`--comp-kicker-top`、`--comp-kicker-left`。

## 命名段

- `enter`：fade + 8px 上浮，0.6s；
- `dim`：焦点降压到 35%（幕内主内容登场后调用）；
- `exit`：fade + 上移退出。

## 示例

```js
mount(root, {
  params: { eyebrow: "EP109", index: "02", title: "AGENT" },
  fps: 30,
});
```

## 组合

与任何组件同幕共存；通常第一个 enter、最后一个 exit，`dim` 在 hero 主体登场时触发。

## 禁区

- 不与幕内主标题争夺焦点：角标是元信息，`dim` 后必须退到背景；
- 一幕一个，禁止多角标。
