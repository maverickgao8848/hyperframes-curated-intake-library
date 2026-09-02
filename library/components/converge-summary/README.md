# converge-summary · 收拢汇总

多张要点卡片缩小、飞向中心，收拢成一枚写 `summary` 的汇总 pill。
把"刚才讲的几件事"压成"所以记住这一句"——结论段的视觉句号。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `items` | array | 必填 | 要点卡片文案数组，2–5 条 |
| `summary` | string | 必填 | 汇总 pill 文字，一句话结论 |

卡片表面吃 `--comp-surface` 与 `--comp-radius`，pill 描边吃 `--comp-accent`，文字吃 `--comp-font-sans`。

## 命名段

- `enter`：卡片 0.24s 错拍上浮就位；
- `converge`：卡片同步缩小（scale → 0.6）飞向中心，途中淡出，pill 在中心 1.05 倍弹入锁定，全段约 1.5s；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: {
    items: ["只读相关代码", "先看日志再改", "改完跑测试"],
    summary: "小步快跑，每步可验证",
  },
  fps: 30,
});
```

## 组合

`items` 常复用上一幕 `check-list` 或 `step-chain` 的关键词；pill 落定后可接 `result-rows` 展开结论细节。

## 禁区

- 成员不超过五个，再多说明上一步没归纳好；
- `summary` 是归纳不是新信息，不引入卡片里没出现过的概念；
- 卡片飞行途中必须持续缩小，禁止平移搬运式收拢。
