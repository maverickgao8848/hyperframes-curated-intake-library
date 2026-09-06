# window-card · 窗口容器

承载命令、对话与界面证据的容器：macOS 三点 + 标题栏的终端/聊天窗口，
1px 细描边、近黑表面。它是"这是真实界面"的证据框架——观众先认窗口，再读内容。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `title` | string | `""` | 标题栏文字（mono 小字，如 `zsh — codex`） |
| `variant` | `"terminal" \| "chat" \| "plain"` | `"terminal"` | 窗口气质：终端 / 对话 / 素面板 |
| `width` | string | `"640px"` | 窗口宽度，CSS 长度 |
| `chrome` | boolean | `true` | 是否绘制三点与标题栏 |
| `lines` | array | `[]` | terminal 模式下的逐行内容 |
| `inputHint` | string | `""` | chat 模式输入栏提示 |
| `sendLabel` | string | `"Send"` | chat 模式发送动作短词 |

尺寸经 token 覆盖：`--comp-window-w`、`--comp-window-head-h`；
表面吃 `--comp-surface`，描边吃 `--comp-line`，圆角吃 `--comp-radius`。

## 命名段

- `enter`：窗口体 fade + 10px 上浮（0.5s），三点与标题栏错拍 0.08s 跟上，合计约 0.8s；
- `dim`：焦点降压到 40%，窗口退为背景层；
- `exit`：fade + 下移退出，内部组件先行 exit。

## 示例

```js
mount(root, {
  params: {
    title: "zsh — codex · ~/repo",
    variant: "terminal",
    width: "680px",
  },
  fps: 30,
});
```

## 组合

内部承载 `check-list`、`typewriter-block` 充当窗口内容；外部可用 `connector-draw` 把注释指到窗口内元素。

## 禁区

- 窗口内堆叠不超过两层组件，再深另开一幕；
- `chrome: false` 时不假装终端，素面板不承担"真实界面"语义；
- 窗口是容器不是主体，hero 另有其物。
