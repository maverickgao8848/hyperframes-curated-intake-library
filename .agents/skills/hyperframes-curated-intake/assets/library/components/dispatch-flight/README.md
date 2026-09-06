# dispatch-flight · 分发飞行

payload 文本芯片从一个容器飞到另一个容器，表达任务/数据的分发：
任务从主会话交给 sub-agent、请求从客户端发到服务端。飞行即"交接"。

## 参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `payload` | string | 必填 | 芯片文字（mono 短词，如 `job #84`） |
| `from` | string | 必填 | 起点容器选择器 |
| `to` | string | 必填 | 终点容器选择器 |
| `trail` | boolean | `false` | 是否留残影拖尾 |

芯片表面吃 `--comp-surface`，描边吃 `--comp-line`，文字吃 `--comp-font-mono`，落点高亮吃 `--comp-accent`。

## 命名段

- `enter`：芯片在 `from` 内成形（fade + 6px 上浮，0.4s）；
- `flight`：沿 `from → to` 路径飞行 0.8s，落点 1.06 倍缩放回弹锁定；`trail` 残影 0.2s 内消散；
- `dim` / `exit`：焦点降压与退出。

## 示例

```js
mount(root, {
  params: {
    payload: "job #84 · 查日志",
    from: "#main-session",
    to: "#sub-agent-card",
    trail: true,
  },
  fps: 30,
});
```

## 组合

两端容器通常是两个 `window-card`；落地后常接 `check-list` 展示接手方的处理过程。

## 禁区

- 飞行路径不穿过正文，必要时抬弧线绕行；
- 同幕飞行不超过两次，批量分发用列举不用飞行；
- `payload` 一行短词，不是句子。
