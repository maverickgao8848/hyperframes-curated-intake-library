# meter-bar · 占比条

label + 细占比条 + mono 百分比，表达完成度、覆盖率、资源占用；
`compare` 数组放对比条，一眼看出"改前改后"。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `label` | string | 必填 | 条目标签（mono 短词，如 `测试覆盖`） |
| `value` | number | 必填 | 当前值 |
| `max` | number | `100` | 满量程值 |
| `compare` | array | `[]` | 对比条 `[{ label, value, max? }]`，与主条同量程 |

轨道吃 `--comp-line`，主条填充吃 `--comp-accent`，compare 条吃 `--comp-ink-dim`，百分比吃 `--comp-font-mono`。

## 命名段

- `enter`：label 先 fade 入（0.3s），条从 0 生长到 `value/max` 比例（0.6s，easeOut），百分比数字同步 count-up；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: {
    label: "测试覆盖",
    value: 87,
    max: 100,
    compare: [{ label: "重构前", value: 41 }],
  },
  fps: 30,
});
```

## 组合

常以 2–3 条成组出现，配 `result-rows` 给结论一个数字证据；`numbered-tag` 可给每条编号。

## 禁区

- 同幕（含 compare）不超过三条占比条，对比再多改用表格或拆幕；
- 百分比必须与条形同步到位，禁止数字先跳到位；
- 只表达占比/满量程数据，绝对数值对比不用占比条。
