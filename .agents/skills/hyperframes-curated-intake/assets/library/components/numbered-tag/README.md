# numbered-tag · 编号标签

编号 chip：`Q1`、`STEP 01`、`01·GOAL` 这类等宽小标签，给内容一个可引用的序号。
枚举、提问、目标的元信息层——观众靠编号定位，不靠记忆。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `index` | string | `"01"` | 编号文本（`Q1`、`STEP 01`、`01`） |
| `label` | string | `""` | 编号后的短词（如 `GOAL`），空串只显示编号 |
| `tone` | `"mono" \| "accent"` | `"mono"` | 配色：mono 低调 / accent 强调 |
| `size` | `"s" \| "m"` | `"s"` | 尺寸档位 |

字体吃 `--comp-font-mono`，accent 态吃 `--comp-accent`，描边吃 `--comp-line`。

## 命名段

- `enter`：fade + 6px 上浮，0.4s；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: { index: "01", label: "GOAL", tone: "mono", size: "m" },
  fps: 30,
});
```

## 组合

常与 `step-chain` 共用同一套编号；`result-rows` 的 tag 是它的表格化变体。编号体系与 `scene-kicker` 的章节号保持一致。

## 禁区

- 同幕编号体系不超过两套（如 `Q1/Q2` 与 `STEP 01…` 不同时出现）；
- chip 是元信息，不做强调主体，不放大当标题用；
- `index` 与 `label` 各不超过 8 个字符。
