# step-chain · 步骤链

编号卡 + 箭头逐个生长，表达流程、算法步骤与因果递进；可选末步回环到首步
（如 AGENT 片的「读取结果 → 继续调整」）。这是教学片里出现频率最高的关系组件。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `steps` | array | 必填 | `[{ index?, title, sub? }]`，2–6 步；`index` 缺省自动补 `STEP 01…` |
| `loop` | object \| null | `null` | `{ label }` 末卡回环到首卡并显示标签 |
| `direction` | `"row" \| "column"` | `"row"` | 横向或纵向链条 |

`sub` 用等宽字体放证据型小字（`src/ · 37 files`、`api/jobs.ts +42 -7`）。
尺寸经 token 覆盖：`--comp-chain-card-w`、`--comp-chain-gap`。

## 命名段

- `enter`：卡片 0.22s 错拍上浮，连线在前一卡就位后描出（横向 scaleX / 纵向 scaleY）；
- `loop`：回环路径描画 0.7s，标签 0.45s 处弹入（无 `loop` 参数时为空段）；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: {
    steps: [
      { title: "读取项目", sub: "src/ · 37 files" },
      { title: "找到相关代码", sub: "upload · jobs · results" },
      { title: "修改文件", sub: "api/jobs.ts +42 -7" },
      { title: "运行终端与浏览器", sub: "build ✓ · e2e · browser" },
    ],
    loop: { label: "读取结果 → 继续调整" },
  },
  fps: 30,
});
```

## 组合

上方常配 `numbered-tag` 或 `window-card` 交代上下文；每步可用 `side-note` 追加注释。

## 禁区

- 超过六步必须拆幕，不压缩卡片硬塞；
- `sub` 只放一行短证据，不写句子；
- 回环最多一条，禁止多回环交叉。
