# Code Block

Registry ID: `code-block`  
Candidate identity: `EDU-CODE-01`

逐行解释代码与高亮证据。这是针对 HyperFrames 重新实现的离线、确定性组件；候选目录中的外部链接仅作为设计研究线索，不代表代码或许可来源。

## 参数

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `code` | composition parameter | Component-specific teaching input |
| `language` | composition parameter | Component-specific teaching input |
| `highlightLines` | composition parameter | Component-specific teaching input |

## 命名段

- `enter`: 建立画面与主视觉。
- `emphasis`: 强调当前教学焦点。
- `dim`: 降低视觉权重。
- `exit`: 确定性退出。

## 时间与组合

所有 timeline 均以 `paused: true` 创建，由唯一 composition timeline 驱动。实例必须传入唯一 `context.instanceId`。媒体参数只接受项目本地路径。

## 禁区

- 不把滚轮、鼠标位置或系统时钟作为动画真值。
- 不在渲染时请求网络资源。
- 不复制候选来源的实现代码或品牌资产。
